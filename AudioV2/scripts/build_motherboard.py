#!/usr/bin/env python3
"""ルート基板（AudioV2Case）を旧シートから組み立てる。

2026-09-09: かつての `MotherBoard` 中間階層を廃止し、内容を親 `AudioV2Case` へ
繰り上げた。箱外 I/O（音声端子・PD 受け）はルート上のコネクタで閉じるので、
親スタブ用の階層ラベル（COMMON/PHONE/LINE）は不要。

    AudioV2Case = PowerModule + OutputStage + ControlPanelAnalog
                + 娘基板スロット + 子シート3枚

素材の旧シートは `legacy/` に凍結してある。`sch_import` で **元のままの S式**
として読むので、手描きの配線とジャンクションがそのままルートへ移る。

    python3 AudioV2/scripts/build_motherboard.py           # 書き出す
    python3 AudioV2/scripts/build_motherboard.py --dry-run # 内訳だけ

⚠ ファイル名は歴史的に `build_motherboard.py` のまま（呼び出し側が多い）。
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
import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from generate_kicad_scaffold import PARENT, PROJECT, sheet_block  # noqa: E402
from sch_helpers import embed_lib_symbols, pin_connect, symbol_inst_v10  # noqa: E402

# 生成コード所有のシートは「回すたびに UUID が変わる」と差分がレビューできない
# （§2.8 の既知の問題。control を2回流すと 348 行の uuid が毎回変わった）。
# ここで作る要素の UUID は決定的にして、再実行が同じバイト列になるようにする。
_UID_NS = uuid.UUID("b2000012-0012-4012-8012-000000000012")
_uid_seq = 0


def uid() -> str:
    """呼ばれた順に決まる UUID。同じ手順なら毎回同じ値になる。"""
    global _uid_seq
    _uid_seq += 1
    return str(uuid.uuid5(_UID_NS, f"motherboard/{_uid_seq}"))

# 旧 MotherBoard シートのインスタンス UUID。2026-09-09 に中間階層を廃止したあとも
# 素材の instances パス書き換え・娘基板スクリプトの互換 import 用に残す。
# ルートのシートインスタンスとしては使わない。
UUID_MOTHER_INST = "a1000012-0012-4012-8012-000000000012"
UUID_MOTHER_FILE = "b2000012-0012-4012-8012-000000000012"  # 旧 MotherBoard ファイル UUID（未使用）

# ルートシートのインスタンスパス（中間階層なし）
ROOT_PATH = f"/{PARENT}"

SOURCES = [
    # (ファイル, 元のシートインスタンス UUID, 平行移動)
    ("legacy/PowerModule.kicad_sch", "a1000002-0002-4002-8002-000000000002", (0.0, 0.0)),
    # ⚠ 平行移動量は 2.54 の倍数にすること。半端な値だと配線の端点がグリッドから
    #    外れ、KiCad の ERC が endpoint_off_grid を吐く（110.0 で 46 件出した）。
    ("legacy/OutputStage.kicad_sch", "a1000007-0007-4007-8007-000000000007", (0.0, 111.76)),
    # ControlPanel は B4'-2 で解体。UI と Pico は計測基板へ移した（D27）ので、
    # ここへ来るのは PT2314 とその周辺・BP5293(+5V)・パネル PWR SW・12V LED。
    ("legacy/ControlPanelAnalog.kicad_sch", "a1000006-0006-4006-8006-000000000006",
     (355.6, 0.0)),
]

PAPER = "A2"   # ControlPanel を取り込んで A3 では収まらなくなった

# --- 娘基板スロット（D18 のピン割当）------------------------------------
#
# 両版で完全に同一のヘッダ。スイッチ版は +5V_COIL / GND_COIL を使わないだけ。
# アナログ4本は、直交する隣接ピンが3方向とも A_GND になるよう千鳥に置いてある
# （標準の 2xNN フットプリントは 奇数=1列目 / 偶数=2列目 で行が y に進む）。
SLOT_ANA_NETS = {
    1: "A_GND",  2: "A_GND",
    3: "TONE_L", 4: "A_GND",
    5: "A_GND",  6: "TONE_R",
    7: "AMP_SEL_L", 8: "A_GND",
    9: "A_GND", 10: "AMP_SEL_R",
}
# 11/12 は番地。母板側でスロットごとに D_GND / 3V3 へ落とす（D21）。
SLOT_PWR_NETS = {
    1: "+15V",     2: "A_GND",
    3: "-15V",     4: "A_GND",
    5: "+5V_COIL", 6: "GND_COIL",
    7: "I2C_SDA",  8: "D_GND",
    9: "I2C_SCL", 10: "3V3",
}
# スロット番号 -> (ADDR0, ADDR1)。0x20 と 0x21。
SLOT_ADDR = {1: ("D_GND", "D_GND"), 2: ("3V3", "D_GND")}
# (スロット番号, J_ANA の位置, J_PWR の位置)
SLOTS = [(1, (215.9, 50.8), (215.9, 96.52)),
         (2, (279.4, 50.8), (279.4, 96.52))]
NETTIE_AT = (215.9, 154.94)   # GND_COIL <-> D_GND
# --- 子シート（ルート直下）-----------------------------------------------
# 2026-09-04 に母板の子へ入れ、2026-09-09 に母板ごとルートへ繰り上げた。
# KiCad の階層シートは配置を縛らないので、**どこに実装するか（B5）とは独立**。
#
# (名前, ファイル, インスタンス UUID, 位置, 大きさ, [(シートピン名, 種別, 左右, ルート側のネット)])
CHILD_SHEETS = [
    ("MeasureControl", "MeasureControl.kicad_sch",
     "43e41fda-fe26-43e3-950a-c017f3070bbf", (400.0, 220.0), (45.72, 33.02), [
         ("+15V_A", "input", "L", "+15V"), ("-15V_A", "input", "L", "-15V"),
         ("ADC_GND_IN", "input", "L", "PD_GND"), ("ADC_V_IN", "input", "L", "PD_12V_SW"),
         ("AUDIO_L_IN", "input", "L", "AMP_SEL_L"), ("AUDIO_R_IN", "input", "L", "AMP_SEL_R"),
         ("A_GND", "bidirectional", "L", "A_GND"),
         ("I2C_SDA", "bidirectional", "R", "I2C_SDA"), ("I2C_SCL", "bidirectional", "R", "I2C_SCL"),
         ("3V3", "output", "R", "3V3"), ("D_GND", "bidirectional", "R", "D_GND"),
     ]),
    ("AmpBankSwitch", "AmpBankSwitch.kicad_sch",
     "a1000011-0011-4011-8011-000000000011", (400.0, 270.0), (45.72, 40.64), [
         ("TONE_L", "input", "L", "TONE_L"), ("TONE_R", "input", "L", "TONE_R"),
         ("+15V", "input", "L", "+15V"), ("-15V", "input", "L", "-15V"),
         ("A_GND", "bidirectional", "L", "A_GND"),
         ("I2C_SDA", "bidirectional", "L", "I2C_SDA"), ("I2C_SCL", "bidirectional", "L", "I2C_SCL"),
         ("D_GND", "input", "L", "D_GND"), ("3V3", "input", "L", "3V3"),
         # 番地はスロットごとに違う値（D21）。スイッチ版 = 0x20
         ("ADDR0", "input", "L", "D_GND"), ("ADDR1", "input", "L", "D_GND"),
         ("AMP_SEL_L", "output", "R", "AMP_SEL_L"), ("AMP_SEL_R", "output", "R", "AMP_SEL_R"),
     ]),
    ("AmpBankRelay", "AmpBankRelay.kicad_sch",
     "a1000013-0013-4013-8013-000000000013", (400.0, 330.0), (45.72, 45.72), [
         ("TONE_L", "input", "L", "TONE_L"), ("TONE_R", "input", "L", "TONE_R"),
         ("+15V", "input", "L", "+15V"), ("-15V", "input", "L", "-15V"),
         ("A_GND", "bidirectional", "L", "A_GND"),
         ("I2C_SDA", "bidirectional", "L", "I2C_SDA"), ("I2C_SCL", "bidirectional", "L", "I2C_SCL"),
         ("D_GND", "input", "L", "D_GND"), ("3V3", "input", "L", "3V3"),
         # リレー版 = 0x21（ADDR0 が 3V3）
         ("ADDR0", "input", "L", "3V3"), ("ADDR1", "input", "L", "D_GND"),
         ("+5V_COIL", "input", "L", "+5V_COIL"), ("GND_COIL", "bidirectional", "L", "GND_COIL"),
         ("AMP_SEL_L", "output", "R", "AMP_SEL_L"), ("AMP_SEL_R", "output", "R", "AMP_SEL_R"),
     ]),
]

SLOT_LIBS = ["power:PWR_FLAG",
             "Connector_Generic:Conn_02x05_Odd_Even",
             "Connector_Generic:Conn_02x06_Odd_Even",
             "Device:NetTie_2"]
# 娘基板スロットのフットプリント（A5）。
#   母板は**メス（ソケット）**、娘基板は**オス**。娘基板側は build_daughter.py が
#   PinHeader_2x0N_P2.54mm_Vertical を入れている。
#   ⚠ ピン長（標準 vs ロングピン 11mm）はフットプリントでは区別されない。
#     パッド配置は同じで、違うのは部品高さだけなので**発注時の属性**として扱う。
#     基板間 15mm を成立させるのは娘基板側のロングピン品（A5 の案a）。
SLOT_FP_ANA = "Connector_PinSocket_2.54mm:PinSocket_2x05_P2.54mm_Vertical"
SLOT_FP_PWR = "Connector_PinSocket_2.54mm:PinSocket_2x06_P2.54mm_Vertical"
# 娘基板スロットで新たに母板の外へ出る／入るネット
# ⚠ 娘基板スロットが要求するネットのうち、母板の中で作られるようになったもの
#    （TONE_L/R は PT2314、+5V は BP5293）は方向が input -> output に変わる。
#    VCC_TONE と PD_12V は ControlPanel が母板に入って**完全に内部**になったので階層ピンから外した。
# 子シートを母板の中に置いたので、これらは**母板内のネット**。階層ピンにはしない。
SLOT_HIER = [("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
             ("D_GND", "input"), ("3V3", "input"),
             # ⚠ 親のシートピンを足すだけでは繋がらない。シート側に階層ラベルが
             #    無いとピンに対応するものが無く、母板内とルートで別ネットになる。
             ("GND_COIL", "bidirectional")]

# 親から外すシート。母板へ統合される2枚に加え、"MotherBoard" 自身も入れて
# 再実行を冪等にする（回すたびにシートが増えないように）。
# 親から外すシート。母板へ統合された3枚と、母板自身（再実行を冪等にするため）、
# そして 2026-09-04 に**母板の子へ移した3枚**。
REPLACED_SHEETS = ("PowerModule", "OutputStage", "ControlPanel", "MotherBoard",
                   "MeasureControl", "AmpBankSwitch", "AmpBankRelay")

# ControlPanel が母板に入ったことで、作る側と使う側の両方が母板の中に収まった
# ネット。階層ピンに残すと親で行き先の無いピンになるのでローカルへ落とす。
#   VCC_TONE: PowerModule の 7809 -> PT2314
#   PD_12V  : PowerModule -> パネル PWR SW(SW402)
INTERNAL_NOW = {
    "VCC_TONE", "PD_12V",
    # 2026-09-04: 子シートが母板の中に入ったので、これらは母板内で閉じる
    "+15V", "-15V", "A_GND", "+5V_COIL", "TONE_L", "TONE_R",
    "AMP_SEL_L", "AMP_SEL_R", "I2C_SDA", "I2C_SCL",
    "PD_12V_SW", "PD_GND", "GND_COIL", "D_GND", "3V3",
    # 2026-09-09: ルートへ繰り上げ。箱外 I/O はルート上のコネクタで閉じるので
    # 親スタブ用の階層ラベルはローカルへ落とす。
    "COMMON_L", "COMMON_R", "PHONE_L", "PHONE_R", "LINE_L", "LINE_R",
}


def _label_from_hier(el: sch_import.Element) -> sch_import.Element:
    """階層ラベルを同じ位置のローカルラベルへ落とす（シート内の結線は保たれる）。

    2枚に分かれていたときは両方が親経由で繋がっていたネットが、統合後は
    シート内で閉じる。階層ラベルを2つ残すと親のシートピンが重複するので、
    片方をローカルラベルに落とす。
    """
    name = el.name
    m = re.search(r"\(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)", el.text)
    x, y, rot = float(m.group(1)), float(m.group(2)), float(m.group(3))
    just = "right" if "justify right" in el.text else "left"
    text = (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')
    return sch_import.Element("label", text, None, name, (x, y))


def _lib_pin_tips(lib_id: str, sx: float, sy: float, rot: int = 0) -> dict[str, tuple[float, float]]:
    """ライブラリのピン定義から、配置後の電気的な先端を番号ごとに返す。

    ピン座標を手で写すと間違えるので、KiCad のシンボルから直接読む。
    """
    lib, name = lib_id.split(":", 1)
    text = sch_helpers._read_symbol_text(lib, name)
    m = re.search(rf'\n\t\(symbol "{re.escape(name)}"', text)
    if not m:
        raise KeyError(f"シンボルが見つからない: {lib_id}")
    start, depth, i, in_str = m.start() + 1, 0, m.start() + 1, False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[start:i + 1]
    out: dict[str, tuple[float, float]] = {}
    for px, py, num in re.findall(
            r"\(pin \w+ \w+\s*\n\s*\(at (-?[\d.]+) (-?[\d.]+) -?[\d.]+\)"
            r'[\s\S]{0,300}?\(number "([^"]+)"', body):
        out[num] = pin_connect(sx, sy, rot, float(px), float(py))
    return out


def daughter_slots() -> tuple[list[sch_import.Element], list[str]]:
    """娘基板スロット2組と、コイル帰路の NetTie を組み立てる（D18 / D19 / D21）。"""
    els: list[sch_import.Element] = []
    hier_names: list[str] = []
    path = ROOT_PATH

    # symbol_inst_v10 は sch_helpers.new_uid()、hier_label は scaffold.uid() を使う。
    # 両方とも決定的な uid() に差し替える（片方だけだと再実行でその分だけ差分が出る。
    # 実際に階層ラベル7本ぶん、uuid 14 行が毎回変わった）。
    saved_new, sch_helpers.new_uid = sch_helpers.new_uid, uid
    saved_sc, scaffold.uid = scaffold.uid, uid
    try:
        for slot, ana_at, pwr_at in SLOTS:
            for lib, ref, value, at, nets, fp in (
                ("Connector_Generic:Conn_02x05_Odd_Even", f"J_ANA10{slot}",
                 f"SLOT{slot} ANA (D18)", ana_at, SLOT_ANA_NETS, SLOT_FP_ANA),
                ("Connector_Generic:Conn_02x06_Odd_Even", f"J_PWR10{slot}",
                 f"SLOT{slot} PWR/CTRL (D18)", pwr_at,
                 {**SLOT_PWR_NETS, 11: SLOT_ADDR[slot][0], 12: SLOT_ADDR[slot][1]},
                 SLOT_FP_PWR),
            ):
                els.append(sch_import.Element(
                    "symbol",
                    symbol_inst_v10(lib, ref, value, at[0], at[1], 0, path,
                                    footprint=fp),
                    ref, None, at))
                tips = _lib_pin_tips(lib, at[0], at[1])
                for num, net in nets.items():
                    x, y = tips[str(num)]
                    # 奇数ピンは左向き、偶数ピンは右向きに出ている
                    left = num % 2 == 1
                    els.append(sch_import.Element(
                        "label",
                        _plain_label(net, x, y, 180 if left else 0,
                                     "right" if left else "left"),
                        None, net, (x, y)))

        nx, ny = NETTIE_AT
        els.append(sch_import.Element(
            "symbol",
            symbol_inst_v10("Device:NetTie_2", "NT101", "GND_COIL-D_GND", nx, ny, 0, path,
                            footprint="NetTie:NetTie-2_SMD_Pad2.0mm",
                            # 基板上の銅箔で買う部品ではない。KiCad 標準の
                            # Device:NetTie_2 の既定も in_bom=no で、手編集所有の
                            # MeasureControl の NT1601/NT1602 もそうなっている
                            in_bom=False),
            "NT101", None, (nx, ny)))
        tips = _lib_pin_tips("Device:NetTie_2", nx, ny)
        for num, net, ang, just in (("1", "GND_COIL", 180, "right"), ("2", "D_GND", 0, "left")):
            x, y = tips[num]
            els.append(sch_import.Element("label", _plain_label(net, x, y, ang, just),
                                          None, net, (x, y)))
        # NetTie 越しだと ERC は駆動側と見なさない。リレー版ドライバの GND が
        # power_pin_not_driven になるので GND_COIL に PWR_FLAG を立てる。
        fx, fy = nx - 12.7, ny
        els.append(sch_import.Element(
            "symbol",
            symbol_inst_v10("power:PWR_FLAG", "#FLG0101", "PWR_FLAG", fx, fy, 0, path),
            "#FLG0101", None, (fx, fy)))
        ftips = _lib_pin_tips("power:PWR_FLAG", fx, fy)
        for x, y in ftips.values():
            els.append(sch_import.Element(
                "label", _plain_label("GND_COIL", x, y, 0, "left"), None, "GND_COIL", (x, y)))

        # 2026-09-04: SLOT_HIER は役目を終えた。
        # 子シートが母板の中に入ったので、これらは母板内のネットになり、
        # 階層ラベルは不要（親にピンが無く hier_label_mismatch になる）。
        # 単独のローカルラベルも浮くだけ（label_dangling）。
        # これらのネットは J_PWR101/102（スロットコネクタ）・NT101・U402 側に
        # 実体があるので、ここで置く必要はない。定義は経緯の記録として残す。
    finally:
        sch_helpers.new_uid = saved_new
        scaffold.uid = saved_sc
    return els, hier_names


def _merge_lib_symbols(blocks: list[str]) -> str:
    """複数シートの (lib_symbols ...) を名前で重複排除して1つにする。"""
    seen: dict[str, str] = {}
    for blk in blocks:
        # 実図の lib_symbols は 2 タブ、`embed_lib_symbols()` は 1 タブで
        # `(symbol` を出す。両方受けて 2 タブへ揃える（1タブのままだと
        # ここの抽出に引っかからず、シンボルが lib_symbols から落ちる。
        # 落ちると KiCad がピンを解決できず、そのコネクタの全ピンが
        # 1本のネットに潰れる ＝ 2026-09-03 に実際に踏んだ）。
        for m in re.finditer(r'\n(\t+)\(symbol "([^"]+)"', blk):
            indent, name = m.group(1), m.group(2)
            start = m.start() + 1
            depth, i, in_str = 0, start, False
            while i < len(blk):
                c = blk[i]
                if in_str:
                    if c == "\\":
                        i += 2
                        continue
                    if c == '"':
                        in_str = False
                elif c == '"':
                    in_str = True
                elif c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            body = blk[start:i + 1]
            if len(indent) < 2:
                pad = "\t" * (2 - len(indent))
                body = "\n".join(pad + ln if ln else ln for ln in body.split("\n"))
            seen.setdefault(name, body)
    body = "\n".join(seen[k] for k in sorted(seen))
    return f"\n\t(lib_symbols\n{body}\n\t)\n"


def build(dry_run: bool = False) -> str:
    sheets = []
    for fname, old_inst, (dx, dy) in SOURCES:
        s = sch_import.load(ROOT / fname)
        sheets.append((fname, s, old_inst, dx, dy))

    elements: list[sch_import.Element] = []
    hier_seen: set[str] = set()
    demoted: list[str] = []

    for fname, s, old_inst, dx, dy in sheets:
        for el in s.elements:
            if dx or dy:
                el = el.translated(dx, dy)
            if el.kind == "hierarchical_label":
                if el.name in INTERNAL_NOW:
                    demoted.append(f"{fname}:{el.name}(内部化)")
                    el = _label_from_hier(el)
                elif el.name in hier_seen:
                    demoted.append(f"{fname}:{el.name}")
                    el = _label_from_hier(el)
                else:
                    hier_seen.add(el.name)
            elif el.kind == "symbol":
                # インスタンスパスをルートへ付け替える（旧素材 / 旧母板パスの両方）
                text = el.text.replace(
                    f"/{PARENT}/{UUID_MOTHER_INST}", ROOT_PATH)
                text = text.replace(f"/{PARENT}/{old_inst}", ROOT_PATH)
                el = sch_import.Element(el.kind, text, el.ref, el.name, el.at)
            elements.append(el)

    slot_els, slot_hier = daughter_slots()
    elements.extend(slot_els)
    hier_seen.update(slot_hier)

    # --- 子シート3枚を母板の中に置く（2026-09-04）---
    saved_sc2, scaffold.uid = scaffold.uid, uid
    try:
        for name, fname, inst, (sx, sy), (sw, sh), pins in CHILD_SHEETS:
            lefts = [x for x in pins if x[2] == "L"]
            rights = [x for x in pins if x[2] == "R"]
            blk_pins = []
            for group, px in ((lefts, sx), (rights, sx + sw)):
                for i, (pn, kind, side, net) in enumerate(group):
                    py = sy + 2.54 + i * 2.54
                    blk_pins.append((pn, kind, px, py, 180 if side == "L" else 0))
                    elements.append(sch_import.Element(
                        "label", _plain_label(net, px, py, 180 if side == "L" else 0,
                                              "right" if side == "L" else "left"),
                        None, net, (px, py)))
            need = sy + 2.54 + (max(len(lefts), len(rights)) - 1) * 2.54
            if need > sy + sh:
                raise ValueError(f"{name}: シートピンが枠の外（枠 {sy}..{sy+sh} / 最終ピン {need}）")
            # AmpBankRelay は当面 BOM・基板から外す（アナログSW版を優先）。
            # シート属性は再生成で消えるのでここで固定する。
            on_board = in_bom = name != "AmpBankRelay"
            elements.append(sch_import.Element(
                "sheet", sheet_block(
                    inst, name, fname, sx, sy, sw, sh, blk_pins, "1",
                    in_bom=in_bom, on_board=on_board),
                None, name, (sx, sy)))
    finally:
        scaffold.uid = saved_sc2

    lib = _merge_lib_symbols(
        [h for _, s, *_ in sheets for h in s.header if h.lstrip().startswith("(lib_symbols")]
        + [embed_lib_symbols(SLOT_LIBS)])

    # 外接は要素のアンカーとワイヤ端だけで測る。symbol の hide 済みプロパティは
    # KiCad が置き去りにした負座標を持つことがあり（例: PowerModule の C206 が
    # (at -62.23 21.59)）、混ぜると外接が実態とかけ離れる。
    pts = [e.at for e in elements if e.at] + \
          [c for e in elements if e.kind == "wire" for c in e.coords()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if dry_run:
        from collections import Counter
        c = Counter(e.kind for e in elements)
        print("母板 v0 の内訳:", " ".join(f"{k}={v}" for k, v in sorted(c.items())))
        print(f"  外接: x {min(xs):.1f}..{max(xs):.1f}  y {min(ys):.1f}..{max(ys):.1f}  (paper {PAPER})")
        print(f"  階層ピン {len(hier_seen)} 本: {', '.join(sorted(hier_seen))}")
        print(f"  ローカルへ落とした階層ラベル: {demoted or 'なし'}")
        return ""

    header = (f'\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n'
              f'\t(uuid "{PARENT}")\n\t(paper "{PAPER}")\n{lib}')
    footer = '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
    return "(kicad_sch" + header + "".join(e.text for e in elements) + footer + ")\n"


def _plain_label(name: str, x: float, y: float, rot: int, justify: str) -> str:
    return (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {justify} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')


def rewrite_child_instance_paths() -> list[str]:
    """手編集所有の MeasureControl など、生成が触らない子の instances パスから
    旧 MotherBoard 段を落とす。"""
    notes: list[str] = []
    old = f"/{PARENT}/{UUID_MOTHER_INST}/"
    new = f"/{PARENT}/"
    for fname in ("MeasureControl.kicad_sch",):
        path = ROOT / fname
        text = path.read_text(encoding="utf-8")
        if old not in text:
            notes.append(f"{fname}: 旧パス無し")
            continue
        n = text.count(old)
        sch_helpers.write_sch(path, text.replace(old, new))
        notes.append(f"{fname}: MotherBoard 段を {n} 箇所削除")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = build(dry_run=a.dry_run)
    if a.dry_run:
        return 0
    if out:
        sch_helpers.write_sch(ROOT / "AudioV2Case.kicad_sch", out)
        print(f"書き出し: AudioV2/AudioV2Case.kicad_sch ({len(out)} bytes)")
    for note in rewrite_child_instance_paths():
        print(f"  {note}")
    mother = ROOT / "MotherBoard.kicad_sch"
    if mother.exists():
        mother.unlink()
        print("削除: AudioV2/MotherBoard.kicad_sch（中間階層を廃止）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
