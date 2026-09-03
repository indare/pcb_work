#!/usr/bin/env python3
"""実図を部品単位で編集するための道具（`sch_import` の上に乗る）。

シートを書き起こし直すと**手描きの配線が失われる**ので、残す部分はそのまま置いて
「部品を外す／値を変える／ラベルを差し替える」だけを機械的にやる。

外した部品にぶら下がっていたワイヤ・ジャンクション・ラベルは `prune()` が
収束するまで落とす。どれを落とすかを人が数えると必ず取りこぼすので機械にやらせる。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sch_helpers  # noqa: E402
import sch_import  # noqa: E402
from sch_helpers import pin_connect  # noqa: E402

_TOL = 0.01


def _key(pt: tuple[float, float]) -> tuple[float, float]:
    return (round(pt[0] / _TOL) * _TOL, round(pt[1] / _TOL) * _TOL)


_lib_cache: dict[str, dict[str, tuple[float, float]]] = {}


def _symbol_body(text: str, name: str) -> str:
    m = re.search(rf'\n\t\(symbol "{re.escape(name)}"', text)
    if not m:
        raise KeyError(name)
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
    return text[start:i + 1]


def lib_pin_names(lib_id: str) -> dict[str, str]:
    """`(ピン番号 -> ピン名)`。`extends` を辿る。"""
    lib, name = lib_id.split(":", 1)
    text = sch_helpers._read_symbol_text(lib, name)
    body = _symbol_body(text, name)
    ext = re.search(r'\(extends "([^"]+)"\)', body)
    if ext and not re.search(r'\(pin \w+ \w+', body):
        body = _symbol_body(text, ext.group(1))
    return {
        num: nm
        for nm, num in re.findall(
            r'\(name "([^"]*)"[\s\S]{0,200}?\(number "([^"]+)"', body)
    }


def lib_pins(lib_id: str) -> dict[str, tuple[float, float]]:
    """ライブラリのピン定義 `(番号 -> (x, y))`。KiCad のシンボルから直接読む。

    ⚠ `extends` で派生したシンボル（例 `MCP23017x-x-SP` は `...-SO` を継承）は
    自分ではピンを持たない。辿らないとピンが 0 個になり、シンボルが
    ネットリストから丸ごと消える。
    """
    if lib_id in _lib_cache:
        return _lib_cache[lib_id]
    lib, name = lib_id.split(":", 1)
    text = sch_helpers._read_symbol_text(lib, name)
    body0 = _symbol_body(text, name)
    ext = re.search(r'\(extends "([^"]+)"\)', body0)
    if ext and not re.search(r"\(pin \w+ \w+", body0):
        name = ext.group(1)
    m = re.search(rf'\n\t\(symbol "{re.escape(name)}"', text)
    if not m:
        raise KeyError(lib_id)
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
    out = {
        num: (float(px), float(py))
        for px, py, num in re.findall(
            r"\(pin \w+ \w+\s*\n\s*\(at (-?[\d.]+) (-?[\d.]+) -?[\d.]+\)"
            r'[\s\S]{0,300}?\(number "([^"]+)"', text[start:i + 1])
    }
    _lib_cache[lib_id] = out
    return out


def symbol_tips(el: sch_import.Element) -> list[tuple[float, float]]:
    """配置済みシンボルの電気的なピン先。マルチユニットは全ユニット分返す。"""
    lib = re.search(r'\(lib_id "([^"]+)"\)', el.text).group(1)
    at = re.search(r"\(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)", el.text)
    x, y, rot = float(at.group(1)), float(at.group(2)), int(float(at.group(3)))
    return [pin_connect(x, y, rot, px, py) for px, py in lib_pins(lib).values()]


def _on_seg(pt: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> bool:
    """点が線分上（端点含む）にあるか。KiCad は T 字接続でワイヤの途中に乗る。"""
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    if min(x1, x2) - _TOL <= x <= max(x1, x2) + _TOL and min(y1, y2) - _TOL <= y <= max(y1, y2) + _TOL:
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        return abs(cross) <= _TOL * max(1.0, abs(x2 - x1) + abs(y2 - y1))
    return False


def prune(sheet: sch_import.Sheet, verbose: bool = False) -> dict[str, int]:
    """浮いたワイヤ・ジャンクション・ラベルを収束するまで落とす。

    ⚠ 「点がワイヤに触れている」は端点だけでは足りない。KiCad は T 字接続で
    ワイヤの**途中**に別のワイヤ端・ジャンクション・ラベルが乗る。端点だけを
    見る実装にしたら、無変更のシートから 9 本のワイヤを落とした（2026-09-03）。
    """
    dropped: dict[str, int] = {}
    while True:
        els = sheet.elements
        tips = {_key(t) for e in els if e.kind == "symbol" for t in symbol_tips(e)}
        segs = [(tuple(c) for c in e.coords()) for e in els if e.kind == "wire"]
        segs = [tuple(e.coords()) for e in els if e.kind == "wire"]
        labels = {_key(e.at) for e in els if e.kind in ("label", "hierarchical_label") and e.at}

        def touching(pt: tuple[float, float], skip: int | None = None) -> int:
            """その点に触れているワイヤの本数。"""
            return sum(1 for i, s in enumerate(segs)
                       if i != skip and _on_seg(pt, s[0], s[1]))

        keep: list[sch_import.Element] = []
        changed = False
        for idx, e in enumerate(els):
            if e.kind == "wire":
                wi = segs.index(tuple(e.coords()))
                ok = all(_key(c) in tips or _key(c) in labels or touching(c, wi) > 0
                         for c in e.coords())
            elif e.kind == "junction":
                ok = touching(e.at) >= 2 or (touching(e.at) >= 1 and _key(e.at) in tips)
            elif e.kind in ("label", "hierarchical_label"):
                ok = _key(e.at) in tips or touching(e.at) > 0
            elif e.kind == "no_connect":
                ok = _key(e.at) in tips
            else:
                ok = True
            if ok:
                keep.append(e)
            else:
                dropped[e.kind] = dropped.get(e.kind, 0) + 1
                changed = True
                if verbose:
                    print(f"    落とす {e.kind} {e.name or e.ref or ''} @{e.at}")
        sheet.elements = keep
        if not changed:
            return dropped


def remove_symbols(sheet: sch_import.Sheet, refs: set[str]) -> list[str]:
    gone = [e.ref for e in sheet.elements if e.kind == "symbol" and e.ref in refs]
    sheet.elements = [e for e in sheet.elements
                      if not (e.kind == "symbol" and e.ref in refs)]
    missing = refs - set(gone)
    if missing:
        raise KeyError(f"外す部品が見つからない: {sorted(missing)}")
    return gone


def set_value(sheet: sch_import.Sheet, ref: str, value: str, footprint: str | None = None) -> None:
    for i, e in enumerate(sheet.elements):
        if e.kind == "symbol" and e.ref == ref:
            txt = re.sub(r'(\(property "Value" ")[^"]*(")', rf"\g<1>{value}\g<2>", e.text, count=1)
            if footprint is not None:
                txt = re.sub(r'(\(property "Footprint" ")[^"]*(")',
                             rf"\g<1>{footprint}\g<2>", txt, count=1)
            sheet.elements[i] = sch_import.Element(e.kind, txt, e.ref, e.name, e.at)
            return
    raise KeyError(ref)
