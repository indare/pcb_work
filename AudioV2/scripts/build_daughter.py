#!/usr/bin/env python3
"""娘基板（4ch）を2種つくる — B3a（スイッチ版）と B3b（リレー版）。

1枚は **AmpCh ×4**（`TMUX7612` ×2 を使い切る / リレーは ×4 とドライバ1個）。
母板スロットは 3 口（ADDR 0x20 / 0x21 / 0x22）なので、同じスイッチ版を
3 枚まで挿せる。D9 のとおりリレー版とも混ぜられる（そのときは空きスロットへ）。
`AmpChannel` は D22 で両版共通。違うのは切替段だけ。

結線は**ピン先のラベル**で行う（ワイヤは引かない）。`AmpBank` も `ControlPanel` も
同じ流儀で、ネットリストで検証できる。

    python3 AudioV2/scripts/build_daughter.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_kicad_scaffold as scaffold  # noqa: E402
import sch_edit  # noqa: E402
import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from build_motherboard import _merge_lib_symbols  # noqa: E402
from build_motherboard import ROOT_PATH  # noqa: E402
from build_motherboard import SLOT_ANA_NETS, SLOT_PWR_NETS  # noqa: E402
from generate_kicad_scaffold import PARENT, sheet_block  # noqa: E402
from sch_helpers import embed_lib_symbols, symbol_inst_v10  # noqa: E402

_seq = 0
_NS = uuid.UUID("b2000013-0013-4013-8013-000000000013")


def uid() -> str:
    global _seq
    _seq += 1
    return str(uuid.uuid5(_NS, f"daughter/{_seq}"))


# --- 版ごとの定義 -------------------------------------------------------
SWITCH, RELAY = "switch", "relay"
N_CH = 4  # 1 枚あたり。TMUX は 1 IC = 2ch なので偶数。スロットは母板側で 3 口

VARIANT = {
    SWITCH: dict(
        name="AmpBankSwitch",
        file_uuid="b2000013-0013-4013-8013-000000000013",
        inst_uuid="a1000011-0011-4011-8011-000000000011",   # 旧 AmpBank の枠を再利用
        chan_uuids=[f"a10000{20+i}-00{20+i}-40{20+i}-80{20+i}-0000000000{20+i}" for i in range(N_CH)],
        chan_refs=[6, 7, 8, 9],          # 参照の百の位（6xx..9xx）
        suffix="301",
        slot=1,
        # KiCad はページ番号を階層の浅い順に振る。ルート=1、その直下の
        # MeasureControl / AmpBankSwitch / AmpBankRelay が 2/3/4、その次の段が 5 から。
        page_base=5,
    ),
    RELAY: dict(
        name="AmpBankRelay",
        file_uuid="b2000014-0014-4014-8014-000000000014",
        inst_uuid="a1000013-0013-4013-8013-000000000013",
        chan_uuids=[f"a10000{30+i}-00{30+i}-40{30+i}-80{30+i}-0000000000{30+i}" for i in range(N_CH)],
        chan_refs=[11, 12, 13, 14],
        suffix="302",
        slot=2,
        page_base=9,                     # AmpBankSwitch の 4 枚（5..8）の次
    ),
}

# --- D18 のヘッダ（娘基板側の受け）--------------------------------------
# ⚠ 割当の正は build_motherboard 側（D-k）。ここで literal を持たない。
# 母板とはコネクタ対でも繋がっているので、ピン番号がズレても ERC にも
# ネットリストにも出ず、基板が出来上がってから分かる。
ANA_NETS = dict(SLOT_ANA_NETS)
# 11/12（番地）は娘基板だけが持つ。母板はスロットごとに D_GND / 3V3 へ落とす（D21）。
PWR_NETS = {**SLOT_PWR_NETS, 11: "ADDR0", 12: "ADDR1"}

# --- MCP23017 -----------------------------------------------------------
# スイッチ版は 1ch=1ビット（4本）、リレー版は 1ch=2ビット（SET/RESET で 8本）。
MCP = "Interface_Expansion:MCP23017x-x-SP"
MCP_COMMON = {"13": "I2C_SDA", "12": "I2C_SCL",
              "15": "ADDR0", "16": "ADDR1", "17": "D_GND",   # A0/A1 はスロットから（D21）
              "18": "3V3", "9": "3V3", "10": "D_GND"}        # ~RESET / VDD / VSS
GPA = ["21", "22", "23", "24", "25", "26", "27", "28"]        # GPA0..GPA7
GPB = ["1", "2", "3", "4", "5", "6", "7", "8"]               # GPB0..GPB7
MCP_NC_ALWAYS = ["11", "14", "19", "20"]                     # NC / INTB / INTA

TMUX = "AudioV2:TMUX7612"
# 案C（2026-09-11）: PCB 配置に合わせてピンを組み直す。
# - PCB 上の TMUX は **90°**（KiCad）: 北辺=ピン9–16、南辺=ピン1–8
# - S↔D 入れ替え: D=各ch出力（Amp側へ引き出し）、S=共通バス AMP_SEL
# - 北辺（奇数）=スイッチ2+3、南辺（偶数）=スイッチ1+4
# - SEL: 奇数=SEL2+SEL3、偶数=SEL1+SEL4
# - L/R: 北DIP(0°)は L西R東。南DIP(180°)は基板上 L東R西 → 南辺だけ L/R を入れ替え
TMUX_MAP = {
    # 奇数 ch{a}: 北辺（D2/D3・S2/S3・SEL2/SEL3）
    "15": "CH{a}_OUT_L",  # D2 西
    "10": "CH{a}_OUT_R",  # D3 東
    "14": "AMP_SEL_L",    # S2
    "11": "AMP_SEL_R",    # S3
    "16": "SEL_CH{a}",    # SEL2
    "9": "SEL_CH{a}",     # SEL3
    # 偶数 ch{b}: 南辺（D1/D4・S1/S4・SEL1/SEL4）※180° DIP 向けに L=東
    "7": "CH{b}_OUT_L",   # D4 東
    "2": "CH{b}_OUT_R",   # D1 西
    "6": "AMP_SEL_L",     # S4
    "3": "AMP_SEL_R",     # S1
    "8": "SEL_CH{b}",     # SEL4
    "1": "SEL_CH{b}",     # SEL1
    "13": "+15V",
    "4": "-15V",
    "5": "A_GND",
}

RELAY_SYM = "Relay:AZ850P2-x"
# v1 の RelayBoard から復元したピン割当（K305 のラベルで確認）:
#   コイル 1(+5V)-5(RST 側) / 10(+5V)-6(SET 側)、接点 3(COM)-2/4 と 8(COM)-9/7
#
# ⚠ 接点は **ch 出力を COM に、共通バスを NO に**入れる。逆（バスを COM）にすると
#    非選択 ch が共通バスを自分の反対接点へ落としてしまう。
# ⚠ 2/4 と 9/7 のどちらが NO かはシンボルにピン名が無く確認できていない。
#    「COM の外側 = NO（SET で導通）」として組んである。**製造前に FP で要確認。**
RELAY_MAP = {"1": "+5V_COIL", "5": "CH{n}_RSTC", "10": "+5V_COIL", "6": "CH{n}_SETC",
             "3": "CH{n}_OUT_L", "4": "AMP_SEL_L",
             "8": "CH{n}_OUT_R", "7": "AMP_SEL_R"}
RELAY_NC = ["2", "9"]
# 石は v1 と同じ AZ850P2-5 に固定（2026-09-09 ユーザー確定）。接点ピンの使い方（3/8・4/7 を使い
# 2/9 を開放）とコイル（1-5 / 10-6）は v1 のネットリストと同一で、v1 実機で動いている組み合わせ。
RELAY_DESC = ("双コイル・ラッチングリレー。v1 と同じ AZ850P2-5 に固定（2026-09-09）。接点 3/8・4/7 を使い 2/9 は開放、"
              "コイル 1-5 / 10-6 —— v1 のネットリストと同一の使い方で、v1 実機で動作実績あり。"
              "⚠ 外形（FRT5）が同じセカンドソース（TQ2-L2 など）は接点の COM/NC/NO のピン番号が同じとは限らず、"
              "挿すと SET/RESET の意味が反転しうる。AZ850P2-5 以外を挿さない。")

# ⚠ ULN2803A ではなく TBD62083APG（ピン互換のドロップイン）を使う。
#    §2.7-3 で「ULN2803 のダーリントンが約 1V 落とすので 40℃ 超で AZ850 の
#    Must Operate 3.75V を満たさない」と検算済み。TBD62083APG は DMOS で
#    RON 3.25Ω max、コイル 1 個（125Ω ≒ 40mA）なら降下 0.13V。
#    シンボルはピン互換の ULN2803A を流用し、Value で区別する。
DRV = "Transistor_Array:ULN2803A"
DRV_VALUE = "TBD62083APG"
# ドライバ1個で 8 出力。4ch×2コイル=8本なので **1個で足りる**。
DRV_IN = ["1", "2", "3", "4", "5", "6", "7", "8"]
DRV_OUT = ["18", "17", "16", "15", "14", "13", "12", "11"]   # I1->O1(18) ... I8->O8(11)

CHAN_PINS = [("TONE_L", "input", "L"), ("TONE_R", "input", "L"),
             ("+15V", "input", "L"), ("-15V", "input", "L"), ("A_GND", "bidirectional", "L"),
             ("OUT_L", "output", "R"), ("OUT_R", "output", "R")]

HIER = [("TONE_L", "input"), ("TONE_R", "input"),
        ("AMP_SEL_L", "output"), ("AMP_SEL_R", "output"),
        ("+15V", "input"), ("-15V", "input"), ("A_GND", "bidirectional"),
        ("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
        ("D_GND", "input"), ("3V3", "input"), ("ADDR0", "input"), ("ADDR1", "input")]
HIER_RELAY_EXTRA = [("+5V_COIL", "input"), ("GND_COIL", "bidirectional")]


def _label(name: str, x: float, y: float, left: bool) -> str:
    rot, just = (180, "right") if left else (0, "left")
    return (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')


def _nc(x: float, y: float) -> str:
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)\n'


class Builder:
    def __init__(self, variant: str) -> None:
        self.v = variant
        self.cfg = VARIANT[variant]
        # 2026-09-09: 母板中間階層を廃止。パスは /親/娘基板。
        self.path = f"{ROOT_PATH}/{self.cfg['inst_uuid']}"
        self.els: list[sch_import.Element] = []
        self.libs: list[str] = []

    # --- 部品を置いて、ピン先にラベルを撒く ---
    def place(self, lib: str, ref: str, value: str, x: float, y: float,
              nets: dict[str, str], nc: list[str] | None = None,
              footprint: str = "", rot: int = 0, description: str = "") -> None:
        el = sch_import.Element(
            "symbol", symbol_inst_v10(lib, ref, value, x, y, rot, self.path,
                                      footprint=footprint, description=description),
            ref, None, (x, y))
        self.els.append(el)
        if lib not in self.libs:
            self.libs.append(lib)
        pin_order = list(sch_edit.lib_pins(lib).keys())
        tips = dict(zip(pin_order, sch_edit.symbol_tips(el)))
        for num, net in nets.items():
            tx, ty = tips[str(num)]
            self.els.append(sch_import.Element(
                "label", _label(net, tx, ty, tx < x), None, net, (tx, ty)))
        for num in (nc or []):
            tx, ty = tips[str(num)]
            self.els.append(sch_import.Element("no_connect", _nc(tx, ty), None, None, (tx, ty)))

    def cap(self, ref: str, value: str, x: float, y: float, hi: str, lo: str,
            polarized: bool = False) -> None:
        lib = "Device:C_Polarized" if polarized else "Device:C"
        fp = ("Capacitor_SMD:CP_Elec_10x12.6" if polarized else
              "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder")
        el = sch_import.Element(
            "symbol", symbol_inst_v10(lib, ref, value, x, y, 0, self.path, footprint=fp),
            ref, None, (x, y))
        self.els.append(el)
        if lib not in self.libs:
            self.libs.append(lib)
        top, bot = sorted(sch_edit.symbol_tips(el), key=lambda p: p[1])
        for (px, py), net in ((top, hi), (bot, lo)):
            self.els.append(sch_import.Element(
                "label", _label(net, px, py, False), None, net, (px, py)))

    def build(self) -> str:
        c = self.cfg
        sfx = c["suffix"]
        # --- AmpChannel ×N_CH ---
        for j, cu in enumerate(c["chan_uuids"]):
            sx, sy = 38.1, 25.4 + j * 35.56
            pins = []
            for k, (nm, kind, side) in enumerate(CHAN_PINS):
                lefts = [p for p in CHAN_PINS if p[2] == "L"]
                if side == "L":
                    px, py = sx, sy + 5.08 + lefts.index((nm, kind, side)) * 5.08
                else:
                    rights = [p for p in CHAN_PINS if p[2] == "R"]
                    px, py = sx + 76.2, sy + 5.08 + rights.index((nm, kind, side)) * 5.08
                pins.append((nm, kind, px, py, 180 if side == "L" else 0))
                net = nm if side == "L" else f"CH{j+1}_{nm}"
                self.els.append(sch_import.Element(
                    "label", _label(net, px, py, side == "L"), None, net, (px, py)))
            saved, scaffold.uid = scaffold.uid, uid
            try:
                blk = sheet_block(cu, f"AmpCh{j+1}", "AmpChannel.kicad_sch",
                                  sx, sy, 76.2, 30.48, pins,
                                  str(c["page_base"] + j), parent_path=self.path)
            finally:
                scaffold.uid = saved
            self.els.append(sch_import.Element("sheet", blk, None, f"AmpCh{j+1}", (sx, sy)))

        # --- MCP23017 ---
        mcp = dict(MCP_COMMON)
        if self.v == SWITCH:
            for i in range(N_CH):
                mcp[GPA[i]] = f"SEL_CH{i+1}"
            nc = GPA[N_CH:] + GPB + MCP_NC_ALWAYS
        else:
            for i in range(N_CH):
                mcp[GPA[i]] = f"CH{i+1}_SET"
                mcp[GPB[i]] = f"CH{i+1}_RST"
            nc = GPA[N_CH:] + GPB[N_CH:] + MCP_NC_ALWAYS
        self.place(MCP, f"U_IO{sfx}", "MCP23017", 200.66, 213.36, mcp, nc,
                   footprint="Package_DIP:DIP-28_W7.62mm")
        self.cap(f"C_IO{sfx}", "100nF", 236.22, 213.36, "3V3", "D_GND")
        self.cap(f"C_BULK_P{sfx}", "100uF 35V", 251.46, 213.36, "+15V", "A_GND", True)
        self.cap(f"C_BULK_N{sfx}", "100uF 35V", 266.7, 213.36, "A_GND", "-15V", True)

        # --- 切替段 ---
        if self.v == SWITCH:
            for i, (a, b) in enumerate([(1, 2), (3, 4)]):
                ref = f"U{311+i}"
                nets = {num: tmpl.format(a=a, b=b) for num, tmpl in TMUX_MAP.items()}
                self.place(TMUX, ref, "TMUX7612", 150.0 + i * 63.5, 290.0, nets, ["12"],
                           footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm")
                self.cap(f"C{311+i*2}", "100nF", 130.0 + i * 63.5, 315.0, "+15V", "A_GND")
                self.cap(f"C{312+i*2}", "100nF", 137.62 + i * 63.5, 315.0, "A_GND", "-15V")
        else:
            for n in range(1, N_CH + 1):
                self.place(RELAY_SYM, f"K{300+n}", "AZ850P2-5",
                           150.0 + (n - 1) * 45.72, 290.0,
                           {k: v.format(n=n) for k, v in RELAY_MAP.items()}, RELAY_NC,
                           # FP は v1 実績の FRT5。⚠ 外形が同じ TQ2-L2 は接点ピンの割り当てが
                           #    違う（2026-09-09 査読）ので「互換」ではない。石は AZ850P2-5 に固定
                           footprint="Relay_THT:Relay_DPDT_FRT5",
                           description=RELAY_DESC)
            nets = {"9": "GND_COIL", "10": "+5V_COIL"}
            for k, ch in enumerate(range(1, N_CH + 1)):
                nets[DRV_IN[k * 2]] = f"CH{ch}_SET"
                nets[DRV_IN[k * 2 + 1]] = f"CH{ch}_RST"
                nets[DRV_OUT[k * 2]] = f"CH{ch}_SETC"
                nets[DRV_OUT[k * 2 + 1]] = f"CH{ch}_RSTC"
            self.place(DRV, "U321", DRV_VALUE, 150.0, 340.0, nets, None,
                       footprint="Package_DIP:DIP-18_W7.62mm")
            self.cap("C321", "100uF 25V", 320.0, 340.0, "+5V_COIL", "GND_COIL", True)
            self.cap("C322", "100nF", 335.0, 340.0, "+5V_COIL", "GND_COIL")

        # --- D18 のヘッダ（娘基板側の受け）---
        self.place("Connector_Generic:Conn_02x05_Odd_Even", f"J_ANA{sfx}",
                   f"SLOT ANA (D18)", 340.36, 60.96, ANA_NETS,
                   footprint="Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical")
        pwr = dict(PWR_NETS)
        if self.v == SWITCH:          # スイッチ版はコイル線を使わない
            pwr = {k: v for k, v in pwr.items() if v not in ("+5V_COIL", "GND_COIL")}
        self.place("Connector_Generic:Conn_02x06_Odd_Even", f"J_PWR{sfx}",
                   f"SLOT PWR/CTRL (D18)", 340.36, 116.84, pwr,
                   ["5", "6"] if self.v == SWITCH else None,
                   footprint="Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical")

        # --- 取付穴（A2: M3 φ3.2 を四隅、端から 5.0 mm）---
        # ピンが無いのでネットは持たない。v1 と同じく回路図にシンボルを置いて
        # PCB とフットプリントの対応を取る（board 側だけに足すと parity が崩れる）。
        # ⚠ 穴の実座標は外形に依存するので PCB が正。ここは「4個あること」だけ。
        for i in range(4):
            self.place("Mechanical:MountingHole",
                       f"H{300 + (c['slot'] - 1) * 10 + i + 1}", "M3",
                       340.36 + i * 12.7, 160.02, {},
                       footprint="MountingHole:MountingHole_3.2mm_M3")

        # --- 階層ピン ---
        hier = HIER + (HIER_RELAY_EXTRA if self.v == RELAY else [])
        saved, scaffold.uid = scaffold.uid, uid
        try:
            for i, (nm, shape) in enumerate(hier):
                hx, hy = 419.1, 40.64 + i * 7.62
                self.els.append(sch_import.Element(
                    "hierarchical_label", scaffold.hier_label(nm, shape, hx, hy, 0),
                    None, nm, (hx, hy)))
                self.els.append(sch_import.Element(
                    "label", _label(nm, hx, hy, False), None, nm, (hx, hy)))
        finally:
            scaffold.uid = saved

        lib = _merge_lib_symbols([embed_lib_symbols(self.libs)])
        header = (f'\n\t(version 20260306)\n\t(generator "eeschema")\n'
                  f'\t(generator_version "10.0")\n\t(uuid "{c["file_uuid"]}")\n'
                  f'\t(paper "A2")\n{lib}')
        footer = '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
        return "(kicad_sch" + header + "".join(e.text for e in self.els) + footer + ")\n"


def rewrite_ampchannel_instances() -> tuple[str, list[str]]:
    """`AmpChannel` の instances を新しい3階層のパスへ張り替える。

    パスは `/親/娘基板/ch` の3段。生成シートはスイッチ＋リレーの 4×2 = 8 パス
    （物理スロット3口目は同じ `AmpBankSwitch` を挿すだけで、別ファイルは持たない）。
    参照は **娘基板1 が 6xx..9xx、娘基板2 が 11xx..14xx**。
    """
    s = sch_import.load(ROOT / "AmpChannel.kicad_sch")
    sw, rl = VARIANT[SWITCH], VARIANT[RELAY]
    order = [(sw["inst_uuid"], u) for u in sw["chan_uuids"]] + \
            [(rl["inst_uuid"], u) for u in rl["chan_uuids"]]
    path_base = ROOT_PATH   # 2026-09-09: 母板中間階層を廃止
    notes: list[str] = []
    for i, e in enumerate(s.elements):
        if e.kind != "symbol":
            continue
        m = re.search(r'\(path "[^"]+"\n\t+\(reference "([A-Za-z_#]+)(\d+)"\)\n\t+\(unit (\d+)\)',
                      e.text)
        if not m:
            continue
        prefix, num, unit = m.group(1), int(m.group(2)), m.group(3)
        base = num % 100 + 600 if num >= 600 else num       # 6xx を基準に揃える
        blocks = []
        for k, (bank, chan) in enumerate(order):
            blocks.append(
                f'\t\t\t\t(path "{path_base}/{bank}/{chan}"\n'
                f'\t\t\t\t\t(reference "{prefix}{base + 100 * k}")\n'
                f"\t\t\t\t\t(unit {unit})\n\t\t\t\t)")
        new_inst = ('(instances\n\t\t\t(project "AudioV2Case"\n'
                    + "\n".join(blocks) + "\n\t\t\t)\n\t\t)")
        start = e.text.index("(instances")
        end = e.text.rindex("\t\t)\n\t)\n")
        s.elements[i] = sch_import.Element(
            e.kind, e.text[:start] + new_inst + "\n\t)\n", e.ref, e.name, e.at)
        notes.append(f"{prefix}{base} -> {prefix}{base}..{prefix}{base + 900}")
    return s.render(), notes


PARENT_SHEETS = [
    (SWITCH, (80.0, 150.0), (35.56, 114.3)),
    (RELAY, (160.0, 150.0), (35.56, 114.3)),
]

# 親側でシートピンに置くラベル。娘基板の階層ピン名をそのまま使うと**両スロットが
# 同じネットに合流してしまう**ものを、ここで差し替える。
#   - ADDR0/ADDR1 は D21 のとおり**スロットごとに違う値**でなければ番地にならない
#     （スロット1 = 0x20、スロット2 = 0x21）
#   - +5V_COIL / GND_COIL は母板側と同名（2026-09-04 に母板を +5V -> +5V_COIL へ
#     揃えたので恒等。以前は母板が +5V で名前が食い違っていた）
PARENT_NET = {
    SWITCH: {"ADDR0": "D_GND", "ADDR1": "D_GND"},
    RELAY: {"ADDR0": "3V3", "ADDR1": "D_GND",
            "+5V_COIL": "+5V_COIL", "GND_COIL": "GND_COIL"},
}


def patch_parent() -> str:
    """⚠ 2026-09-04 以降は使わない。娘基板は母板の子になり、シートを置くのは
    build_motherboard.py の CHILD_SHEETS。残してあるのは経緯の記録のため。"""
    p = sch_import.load(ROOT / "AudioV2Case.kicad_sch")
    drop_names = {"AmpBank"} | {VARIANT[v]["name"] for v, _, _ in PARENT_SHEETS}
    drop_pins: set[tuple[float, float]] = set()
    kept = []
    for el in p.elements:
        if el.kind == "sheet" and el.name in drop_names:
            for m in re.finditer(r'\(pin "[^"]+" \w+\n\t\t\t\(at (-?[\d.]+) (-?[\d.]+)', el.text):
                drop_pins.add((round(float(m.group(1)), 2), round(float(m.group(2)), 2)))
            continue
        kept.append(el)
    kept = [e for e in kept if not (e.kind == "label" and e.at
                                    and (round(e.at[0], 2), round(e.at[1], 2)) in drop_pins)]

    saved, scaffold.uid = scaffold.uid, uid
    try:
        for v, (sx, sy), (w, h) in PARENT_SHEETS:
            cfg = VARIANT[v]
            hier = HIER + (HIER_RELAY_EXTRA if v == RELAY else [])
            pins = []
            li = ri = 0
            for nm, shape in hier:
                left = shape != "output"
                if left:
                    px, py = sx, sy + 7.62 + li * 7.62
                    li += 1
                else:
                    px, py = sx + w, sy + 7.62 + ri * 7.62
                    ri += 1
                pins.append((nm, shape, px, py, 180 if left else 0))
                net = PARENT_NET[v].get(nm, nm)
                kept.append(sch_import.Element(
                    "label", _label(net, px, py, left), None, net, (px, py)))
            kept.append(sch_import.Element(
                "sheet",
                sheet_block(cfg["inst_uuid"], cfg["name"], f"{cfg['name']}.kicad_sch",
                            sx, sy, w, h, pins, "1"),
                None, cfg["name"], (sx, sy)))
    finally:
        scaffold.uid = saved

    p.elements = kept
    # 娘基板2枚ぶん増えたので用紙を A3 へ（既存シートの座標は動かさない）
    p.header = [h.replace('(paper "A4")', '(paper "A3")') for h in p.header]
    return p.render()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    # symbol_inst_v10 / pin_uuid_block は sch_helpers.new_uid()（uuid4 = 乱数）を
    # 使う。ここを差し替えないと再実行でシンボルの uuid が毎回変わり、
    # 「冪等・再実行でバイト一致」（CLAUDE.md）が成立しない。
    # 下の3箇所で scaffold.uid は個別に差し替えているが、片方だけでは足りない
    # （同じ罠の実測は build_motherboard.daughter_slots() の注記にある）。
    # ここは生成全体を覆うので、build() / rewrite_ampchannel_instances() /
    # patch_parent() のすべてが決定的な uid() を通る。
    saved_new_uid, sch_helpers.new_uid = sch_helpers.new_uid, uid
    try:
        return _build_all(a)
    finally:
        sch_helpers.new_uid = saved_new_uid


def _build_all(a) -> int:
    outs = {}
    for v in (SWITCH, RELAY):
        b = Builder(v)
        outs[VARIANT[v]["name"]] = b.build()
        print(f"{VARIANT[v]['name']}: 部品 "
              f"{len([e for e in b.els if e.kind=='symbol'])} / "
              f"シート {len([e for e in b.els if e.kind=='sheet'])} / "
              f"ラベル {len([e for e in b.els if e.kind=='label'])} / "
              f"階層ピン {len([e for e in b.els if e.kind=='hierarchical_label'])}")
    chan, notes = rewrite_ampchannel_instances()
    print("AmpChannel の参照:", ", ".join(notes[:3]), f"… 計 {len(notes)} 部品")
    # 2026-09-04: 娘基板は母板の子になったので、親は触らない。
    # シートを置くのは build_motherboard.py（CHILD_SHEETS）。
    parent = ""
    if a.dry_run:
        return 0
    written = []
    for name, text in outs.items():
        if len(text) < 1000:          # 空や欠けたものを書き込まない安全弁
            raise SystemExit(f"{name}: 生成結果が短すぎる（{len(text)} bytes）")
        sch_helpers.write_sch(ROOT / f"{name}.kicad_sch", text)
        written.append(ROOT / f"{name}.kicad_sch")
        print(f"書き出し: AudioV2/{name}.kicad_sch ({len(text)} bytes)")
    sch_helpers.write_sch(ROOT / "AmpChannel.kicad_sch", chan)
    written.append(ROOT / "AmpChannel.kicad_sch")
    print("書き換え: AmpChannel.kicad_sch（親は build_motherboard.py が扱う）")
    sch_helpers.canonicalize_sch(written)
    print(f"正準化: {len(written)} 枚を kicad-cli sch upgrade に通した")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
