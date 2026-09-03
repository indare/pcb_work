#!/usr/bin/env python3
"""娘基板（5ch）を2種つくる — B3a（スイッチ版）と B3b（リレー版）。

D19 のとおり **5ch × 2枚**。D9 のとおり**両版を混ぜて挿す**ので、
スロット1にスイッチ版・スロット2にリレー版を入れた状態を親に組む。
`AmpChannel` は D22 で両版共通になっているので、違うのは切替段だけ。

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

VARIANT = {
    SWITCH: dict(
        name="AmpBankSwitch",
        file_uuid="b2000013-0013-4013-8013-000000000013",
        inst_uuid="a1000011-0011-4011-8011-000000000011",   # 旧 AmpBank の枠を再利用
        chan_uuids=[f"a10000{20+i}-00{20+i}-40{20+i}-80{20+i}-0000000000{20+i}" for i in range(5)],
        chan_refs=[6, 7, 8, 9, 10],          # 参照の百の位（6xx, 7xx, ...）
        suffix="301",
        slot=1,
    ),
    RELAY: dict(
        name="AmpBankRelay",
        file_uuid="b2000014-0014-4014-8014-000000000014",
        inst_uuid="a1000013-0013-4013-8013-000000000013",
        chan_uuids=[f"a10000{30+i}-00{30+i}-40{30+i}-80{30+i}-0000000000{30+i}" for i in range(5)],
        chan_refs=[11, 12, 13, 14, 15],
        suffix="302",
        slot=2,
    ),
}

# --- D18 のヘッダ（娘基板側の受け）--------------------------------------
ANA_NETS = {1: "A_GND", 2: "A_GND", 3: "TONE_L", 4: "A_GND",
            5: "A_GND", 6: "TONE_R", 7: "AMP_SEL_L", 8: "A_GND",
            9: "A_GND", 10: "AMP_SEL_R"}
PWR_NETS = {1: "+15V", 2: "A_GND", 3: "-15V", 4: "A_GND",
            5: "+5V_COIL", 6: "GND_COIL", 7: "I2C_SDA", 8: "D_GND",
            9: "I2C_SCL", 10: "3V3", 11: "ADDR0", 12: "ADDR1"}

# --- MCP23017 -----------------------------------------------------------
# スイッチ版は 1ch=1ビット（5本）、リレー版は 1ch=2ビット（SET/RESET で 10本）。
MCP = "Interface_Expansion:MCP23017x-x-SP"
MCP_COMMON = {"13": "I2C_SDA", "12": "I2C_SCL",
              "15": "ADDR0", "16": "ADDR1", "17": "D_GND",   # A0/A1 はスロットから（D21）
              "18": "3V3", "9": "3V3", "10": "D_GND"}        # ~RESET / VDD / VSS
GPA = ["21", "22", "23", "24", "25", "26", "27", "28"]        # GPA0..GPA7
GPB = ["1", "2", "3", "4", "5", "6", "7", "8"]               # GPB0..GPB7
MCP_NC_ALWAYS = ["11", "14", "19", "20"]                     # NC / INTB / INTA

TMUX = "AudioV2:TMUX7612"
# S 側が ch ごと、D 側が共通バス。1 IC = 2ch（D22）
TMUX_MAP = {"3": "CH{a}_OUT_L", "2": "AMP_SEL_L", "14": "CH{a}_OUT_R", "15": "AMP_SEL_R",
            "11": "CH{b}_OUT_L", "10": "AMP_SEL_L", "6": "CH{b}_OUT_R", "7": "AMP_SEL_R",
            "1": "SEL_CH{a}", "16": "SEL_CH{a}", "9": "SEL_CH{b}", "8": "SEL_CH{b}",
            "13": "+15V", "4": "-15V", "5": "A_GND"}

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

# ⚠ ULN2803A ではなく TBD62083APG（ピン互換のドロップイン）を使う。
#    §2.7-3 で「ULN2803 のダーリントンが約 1V 落とすので 40℃ 超で AZ850 の
#    Must Operate 3.75V を満たさない」と検算済み。TBD62083APG は DMOS で
#    RON 3.25Ω max、コイル 1 個（125Ω ≒ 40mA）なら降下 0.13V。
#    シンボルはピン互換の ULN2803A を流用し、Value で区別する。
DRV = "Transistor_Array:ULN2803A"
DRV_VALUE = "TBD62083APG"
# ドライバ1個で 8ch。5ch×2コイル=10本なので **2個**要る
# （4ch/枚なら 8本で1個で済んだ。5ch/枚を選んだぶんのコスト）。
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
        self.path = f"/{PARENT}/{self.cfg['inst_uuid']}"
        self.els: list[sch_import.Element] = []
        self.libs: list[str] = []

    # --- 部品を置いて、ピン先にラベルを撒く ---
    def place(self, lib: str, ref: str, value: str, x: float, y: float,
              nets: dict[str, str], nc: list[str] | None = None,
              footprint: str = "", rot: int = 0) -> None:
        el = sch_import.Element(
            "symbol", symbol_inst_v10(lib, ref, value, x, y, rot, self.path,
                                      footprint=footprint), ref, None, (x, y))
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
        # --- AmpChannel ×5 ---
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
                                  sx, sy, 76.2, 30.48, pins, "1")
            finally:
                scaffold.uid = saved
            self.els.append(sch_import.Element("sheet", blk, None, f"AmpCh{j+1}", (sx, sy)))

        # --- MCP23017 ---
        mcp = dict(MCP_COMMON)
        if self.v == SWITCH:
            for i in range(5):
                mcp[GPA[i]] = f"SEL_CH{i+1}"
            nc = GPA[5:] + GPB + MCP_NC_ALWAYS
        else:
            for i in range(5):
                mcp[GPA[i]] = f"CH{i+1}_SET"
                mcp[GPB[i]] = f"CH{i+1}_RST"
            nc = GPA[5:] + GPB[5:] + MCP_NC_ALWAYS
        self.place(MCP, f"U_IO{sfx}", "MCP23017", 200.66, 213.36, mcp, nc,
                   footprint="Package_DIP:DIP-28_W7.62mm")
        self.cap(f"C_IO{sfx}", "100nF", 236.22, 213.36, "3V3", "D_GND")
        self.cap(f"C_BULK_P{sfx}", "100uF 35V", 251.46, 213.36, "+15V", "A_GND", True)
        self.cap(f"C_BULK_N{sfx}", "100uF 35V", 266.7, 213.36, "A_GND", "-15V", True)

        # --- 切替段 ---
        if self.v == SWITCH:
            for i, (a, b) in enumerate([(1, 2), (3, 4), (5, None)]):
                ref = f"U{311+i}"
                nets = {}
                for num, tmpl in TMUX_MAP.items():
                    if b is None and "{b}" in tmpl:
                        continue
                    nets[num] = tmpl.format(a=a, b=b)
                ncs = ["12"] + (["11", "10", "6", "7", "9", "8"] if b is None else [])
                self.place(TMUX, ref, "TMUX7612", 150.0 + i * 63.5, 290.0, nets, ncs,
                           footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm")
                self.cap(f"C{311+i*2}", "100nF", 130.0 + i * 63.5, 315.0, "+15V", "A_GND")
                self.cap(f"C{312+i*2}", "100nF", 137.62 + i * 63.5, 315.0, "A_GND", "-15V")
        else:
            for n in range(1, 6):
                self.place(RELAY_SYM, f"K{300+n}", "AZ850P2-5",
                           150.0 + (n - 1) * 45.72, 290.0,
                           {k: v.format(n=n) for k, v in RELAY_MAP.items()}, RELAY_NC,
                           # FP は v1 実績の FRT5（AZ850P2-5 / TQ2-L2-5V 互換）
                           footprint="Relay_THT:Relay_DPDT_FRT5")
            for i, (ref, span) in enumerate((("U321", range(1, 5)), ("U322", range(5, 6)))):
                nets = {"9": "GND_COIL", "10": "+5V_COIL"}
                used_in, used_out = [], []
                for k, ch in enumerate(span):
                    nets[DRV_IN[k * 2]] = f"CH{ch}_SET"
                    nets[DRV_IN[k * 2 + 1]] = f"CH{ch}_RST"
                    nets[DRV_OUT[k * 2]] = f"CH{ch}_SETC"
                    nets[DRV_OUT[k * 2 + 1]] = f"CH{ch}_RSTC"
                    used_in += [DRV_IN[k * 2], DRV_IN[k * 2 + 1]]
                    used_out += [DRV_OUT[k * 2], DRV_OUT[k * 2 + 1]]
                ncs = [p for p in DRV_IN + DRV_OUT if p not in used_in + used_out]
                self.place(DRV, ref, DRV_VALUE, 150.0 + i * 76.2, 340.0, nets, ncs,
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

    パスは `/親/娘基板/ch` の3段。娘基板が2枚になるので 5×2 = 10 パス。
    参照は **娘基板1 が 6xx..10xx、娘基板2 が 11xx..15xx** と読みやすく振り直す
    （百の位が ch 番号。生成しているので採番は制御できる）。
    """
    s = sch_import.load(ROOT / "AmpChannel.kicad_sch")
    sw, rl = VARIANT[SWITCH], VARIANT[RELAY]
    order = [(sw["inst_uuid"], u) for u in sw["chan_uuids"]] + \
            [(rl["inst_uuid"], u) for u in rl["chan_uuids"]]
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
                f'\t\t\t\t(path "/{PARENT}/{bank}/{chan}"\n'
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
#   - +5V_COIL / GND_COIL は母板側のネット名が別
PARENT_NET = {
    SWITCH: {"ADDR0": "D_GND", "ADDR1": "D_GND"},
    RELAY: {"ADDR0": "3V3", "ADDR1": "D_GND",
            "+5V_COIL": "+5V", "GND_COIL": "GND_COIL"},
}


def patch_parent() -> str:
    """親から `AmpBank` を外し、娘基板2枚（スイッチ版・リレー版）に置き換える。"""
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
    parent = patch_parent()
    if a.dry_run:
        return 0
    for name, text in outs.items():
        (ROOT / f"{name}.kicad_sch").write_text(text, encoding="utf-8")
        print(f"書き出し: AudioV2/{name}.kicad_sch ({len(text)} bytes)")
    (ROOT / "AmpChannel.kicad_sch").write_text(chan, encoding="utf-8")
    (ROOT / "AudioV2Case.kicad_sch").write_text(parent, encoding="utf-8")
    print("書き換え: AmpChannel.kicad_sch / AudioV2Case.kicad_sch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
