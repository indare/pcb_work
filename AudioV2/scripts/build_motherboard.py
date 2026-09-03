#!/usr/bin/env python3
"""母板（MotherBoard）を旧シートから組み立てる。

新構成では PowerModule / OutputStage / ControlPanel(PT2314部) が1枚の母板へ統合される
（`DECISIONS.md`「2026-09-03 時点の基板構成案」）。ここは **v0 = 確定している部分だけ**:

    母板 v0 = PowerModule の全要素 ＋ OutputStage の全要素（平行移動）

`PT2314` の移設と `ControlPanel` の解体は未決なので触らない（未決のまま足すと
検証できない）。娘基板スロットは別ステップ。

素材の旧シートは `legacy/` に凍結してある（親からは参照されていない）。
`sch_import` で **元のままの S式** として読むので、**手描きの配線と
ジャンクションがそのまま母板へ移る**。分解→再構成がバイト一致することは
`sch_import.py --roundtrip` で検証済み。

    python3 AudioV2/scripts/build_motherboard.py           # 書き出す
    python3 AudioV2/scripts/build_motherboard.py --dry-run # 内訳だけ
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

# 母板の UUID。既存の a10000NN / b20000NN 系に合わせて 12 番を確保する。
UUID_MOTHER_INST = "a1000012-0012-4012-8012-000000000012"
UUID_MOTHER_FILE = "b2000012-0012-4012-8012-000000000012"

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

# 親での母板シート。PowerModule が居た場所を使う（OutputStage の枠は空く）。
MOTHER_AT = (25.4, 25.4)
MOTHER_SIZE = (35.56, 101.6)
_PIN_Y0, _PIN_PITCH = 33.02, 7.62
# 左＝入力、右＝出力と双方向。順序がそのまま上からの並びになる。
MOTHER_PINS_L = [
    ("COMMON_L", "input"), ("COMMON_R", "input"),      # 箱外スタブ（外部入力）
    ("AMP_SEL_L", "input"), ("AMP_SEL_R", "input"),    # 娘基板から
    ("D_GND", "input"), ("3V3", "input"),              # 計測基板から（D27 で発生源が移った）
]
MOTHER_PINS_R = [
    ("+15V", "output"), ("-15V", "output"), ("A_GND", "bidirectional"),
    ("+5V", "output"),                                  # BP5293。娘基板のコイル電源
    ("TONE_L", "output"), ("TONE_R", "output"),         # PT2314 の出力（母板に載った）
    ("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
    ("PD_12V_SW", "output"), ("PD_GND", "bidirectional"),
    ("GND_COIL", "bidirectional"),
    ("PHONE_L", "output"), ("PHONE_R", "output"),
    ("LINE_L", "output"), ("LINE_R", "output"),
]
# (階層ピン名, 種別, 左右, y)
MOTHER_PINS = (
    [(n, k, "L", _PIN_Y0 + i * _PIN_PITCH) for i, (n, k) in enumerate(MOTHER_PINS_L)]
    + [(n, k, "R", _PIN_Y0 + i * _PIN_PITCH) for i, (n, k) in enumerate(MOTHER_PINS_R)]
)

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
    5: "+5V",      6: "GND_COIL",
    7: "I2C_SDA",  8: "D_GND",
    9: "I2C_SCL", 10: "3V3",
}
# スロット番号 -> (ADDR0, ADDR1)。0x20 と 0x21。
SLOT_ADDR = {1: ("D_GND", "D_GND"), 2: ("3V3", "D_GND")}
# (スロット番号, J_ANA の位置, J_PWR の位置)
SLOTS = [(1, (215.9, 50.8), (215.9, 96.52)),
         (2, (279.4, 50.8), (279.4, 96.52))]
NETTIE_AT = (215.9, 154.94)   # GND_COIL <-> D_GND
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
SLOT_HIER = [("I2C_SDA", "bidirectional"), ("I2C_SCL", "bidirectional"),
             ("D_GND", "input"), ("3V3", "input"),
             # ⚠ 親のシートピンを足すだけでは繋がらない。シート側に階層ラベルが
             #    無いとピンに対応するものが無く、母板内とルートで別ネットになる。
             ("GND_COIL", "bidirectional")]

# 親から外すシート。母板へ統合される2枚に加え、"MotherBoard" 自身も入れて
# 再実行を冪等にする（回すたびにシートが増えないように）。
REPLACED_SHEETS = ("PowerModule", "OutputStage", "ControlPanel", "MotherBoard")

# ControlPanel が母板に入ったことで、作る側と使う側の両方が母板の中に収まった
# ネット。階層ピンに残すと親で行き先の無いピンになるのでローカルへ落とす。
#   VCC_TONE: PowerModule の 7809 -> PT2314
#   PD_12V  : PowerModule -> パネル PWR SW(SW402)
INTERNAL_NOW = {"VCC_TONE", "PD_12V"}


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
    path = f"/{PARENT}/{UUID_MOTHER_INST}"

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
                            footprint="NetTie:NetTie-2_SMD_Pad2.0mm"),
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

        # 母板の外と繋がるネットを階層ピンにする（scaffold.uid を使うので try の中）
        hx, hy = 340.36, 40.64
        for i, (name, shape) in enumerate(SLOT_HIER):
            y = hy + i * 7.62
            els.append(sch_import.Element(
                "hierarchical_label",
                scaffold.hier_label(name, shape, hx, y, 0), None, name, (hx, y)))
            els.append(sch_import.Element("label", _plain_label(name, hx, y, 0, "left"),
                                          None, name, (hx, y)))
            hier_names.append(name)
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
                # インスタンスパスを母板のシートへ付け替える
                el = sch_import.Element(
                    el.kind,
                    el.text.replace(f"/{PARENT}/{old_inst}", f"/{PARENT}/{UUID_MOTHER_INST}"),
                    el.ref, el.name, el.at)
            elements.append(el)

    slot_els, slot_hier = daughter_slots()
    elements.extend(slot_els)
    hier_seen.update(slot_hier)

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
              f'\t(uuid "{UUID_MOTHER_FILE}")\n\t(paper "{PAPER}")\n{lib}')
    footer = '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
    return "(kicad_sch" + header + "".join(e.text for e in elements) + footer + ")\n"


def _plain_label(name: str, x: float, y: float, rot: int, justify: str) -> str:
    return (f'\t(label "{name}"\n\t\t(at {x} {y} {rot})\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {justify} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)\n')


def patch_parent(dry_run: bool = False) -> str:
    """親から PowerModule / OutputStage を外し、母板シート1枚に置き換える。

    この親は「シートピンの座標にラベルを置く」方式で結線しているので、外すシートの
    ピン上にあったラベルも一緒に外し、母板のピン上に置き直す。
    """
    parent = sch_import.load(ROOT / "AudioV2Case.kicad_sch")

    drop_pins: set[tuple[float, float]] = set()
    kept: list[sch_import.Element] = []
    removed_sheets: list[str] = []
    for el in parent.elements:
        if el.kind == "sheet" and el.name in REPLACED_SHEETS:
            removed_sheets.append(el.name)
            for m in re.finditer(r"\(pin \"[^\"]+\" \w+\n\t\t\t\(at (-?[\d.]+) (-?[\d.]+)", el.text):
                drop_pins.add((round(float(m.group(1)), 2), round(float(m.group(2)), 2)))
            continue
        kept.append(el)

    dropped_labels: list[str] = []
    out: list[sch_import.Element] = []
    for el in kept:
        if el.kind == "label" and el.at and (round(el.at[0], 2), round(el.at[1], 2)) in drop_pins:
            dropped_labels.append(f"{el.name}@{el.at[0]},{el.at[1]}")
            continue
        out.append(el)

    mx, my = MOTHER_AT
    mw, mh = MOTHER_SIZE
    pins, labels = [], []
    for name, ptype, side, y in MOTHER_PINS:
        x = mx if side == "L" else mx + mw
        angle = 180 if side == "L" else 0
        pins.append((name, ptype, x, y, angle))
        labels.append(sch_import.Element(
            "label",
            _plain_label(name, x, y, angle, "right" if side == "L" else "left"),
            None, name, (x, y)))

    saved, scaffold.uid = scaffold.uid, uid   # sheet_block 内のピン UUID も決定的に
    try:
        block = sheet_block(UUID_MOTHER_INST, "MotherBoard", "MotherBoard.kicad_sch",
                            mx, my, mw, mh, pins, "1")
    finally:
        scaffold.uid = saved
    out.append(sch_import.Element("sheet", block, None, "MotherBoard", (mx, my)))
    out.extend(labels)

    if dry_run:
        print(f"親: 外すシート {removed_sheets} / そのピン {len(drop_pins)} 本")
        print(f"    外すラベル {len(dropped_labels)}: {', '.join(dropped_labels)}")
        print(f"    足す母板シート: ピン {len(pins)} 本 ＋ 同数のラベル")
        return ""

    parent.elements = out
    return parent.render()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = build(dry_run=a.dry_run)
    parent = patch_parent(dry_run=a.dry_run)
    if out:
        (ROOT / "MotherBoard.kicad_sch").write_text(out, encoding="utf-8")
        print(f"書き出し: AudioV2/MotherBoard.kicad_sch ({len(out)} bytes)")
    if parent:
        (ROOT / "AudioV2Case.kicad_sch").write_text(parent, encoding="utf-8")
        print(f"書き換え: AudioV2/AudioV2Case.kicad_sch ({len(parent)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
