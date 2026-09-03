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
import sch_import  # noqa: E402
from generate_kicad_scaffold import PARENT, PROJECT, sheet_block  # noqa: E402

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
]

PAPER = "A3"

# 親での母板シート。PowerModule が居た場所を使う（OutputStage の枠は空く）。
MOTHER_AT = (25.4, 25.4)
MOTHER_SIZE = (35.56, 86.36)
# (階層ピン名, 種別, 左右, y)
MOTHER_PINS = [
    ("PD_12V_SW", "input", "L", 33.02),
    ("AMP_SEL_L", "input", "L", 40.64),
    ("AMP_SEL_R", "input", "L", 48.26),
    ("+15V", "output", "R", 33.02),
    ("-15V", "output", "R", 40.64),
    ("A_GND", "bidirectional", "R", 48.26),
    ("VCC_TONE", "output", "R", 55.88),
    ("PD_12V", "output", "R", 63.5),
    ("PD_GND", "bidirectional", "R", 71.12),
    ("PHONE_L", "output", "R", 78.74),
    ("PHONE_R", "output", "R", 86.36),
    ("LINE_L", "output", "R", 93.98),
    ("LINE_R", "output", "R", 101.6),
]
# 親から外すシート。母板へ統合される2枚に加え、"MotherBoard" 自身も入れて
# 再実行を冪等にする（回すたびにシートが増えないように）。
REPLACED_SHEETS = ("PowerModule", "OutputStage", "MotherBoard")


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


def _merge_lib_symbols(blocks: list[str]) -> str:
    """複数シートの (lib_symbols ...) を名前で重複排除して1つにする。"""
    seen: dict[str, str] = {}
    for blk in blocks:
        for m in re.finditer(r'\n\t\t\(symbol "([^"]+)"', blk):
            name = m.group(1)
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
            seen.setdefault(name, blk[start:i + 1])
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
                if el.name in hier_seen:
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

    lib = _merge_lib_symbols([h for _, s, *_ in sheets for h in s.header if h.lstrip().startswith("(lib_symbols")])

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
