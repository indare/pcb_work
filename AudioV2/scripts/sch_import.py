#!/usr/bin/env python3
"""実図の .kicad_sch をトップレベル要素へ分解する（読み取り専用）。

手編集所有のシートをスクリプト所有へ戻すための取り込み用。KiCad が書いた
S式を **そのままの文字列で** 切り出すので、連結し直せば元ファイルに一致する
（`--roundtrip` で検証できる）。座標だけを構造化して持つので、シートごと
平行移動したり要素を別シートへ移したりはコード側から扱える。

    python3 AudioV2/scripts/sch_import.py --roundtrip AudioV2/*.kicad_sch
    python3 AudioV2/scripts/sch_import.py --stats     AudioV2/PowerModule.kicad_sch
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# トップレベルに現れる要素。AudioV2 の全シートを調べた結果この 8 種で閉じている
# （bus / bus_entry / netclass_flag / rule_area は使っていない）。
ELEMENT_KINDS = {
    "symbol", "wire", "label", "junction",
    "hierarchical_label", "text", "no_connect", "sheet",
}
# 要素ではなくファイルの骨格
HEADER_KINDS = {"version", "generator", "generator_version", "uuid", "paper",
                "title_block", "lib_symbols", "embedded_fonts"}
FOOTER_KINDS = {"sheet_instances"}

COORD_RE = re.compile(r"\((at|xy|start|end|mid|center) (-?[\d.]+) (-?[\d.]+)")


@dataclass
class Element:
    kind: str
    text: str                      # KiCad が書いた元のまま
    ref: str | None = None         # symbol のみ
    name: str | None = None        # label / hierarchical_label / sheet のみ
    at: tuple[float, float] | None = None

    def coords(self) -> list[tuple[float, float]]:
        return [(float(m.group(2)), float(m.group(3))) for m in COORD_RE.finditer(self.text)]

    def translated(self, dx: float, dy: float) -> "Element":
        """要素まるごとを平行移動した複製。座標を持つ全フィールドを書き換える。"""
        def sub(m: re.Match[str]) -> str:
            return f"({m.group(1)} {round(float(m.group(2)) + dx, 4):g} {round(float(m.group(3)) + dy, 4):g}"
        moved = COORD_RE.sub(sub, self.text)
        at = (self.at[0] + dx, self.at[1] + dy) if self.at else None
        return Element(self.kind, moved, self.ref, self.name, at)


@dataclass
class Sheet:
    path: Path
    header: list[str] = field(default_factory=list)
    elements: list[Element] = field(default_factory=list)
    footer: list[str] = field(default_factory=list)

    def render(self) -> str:
        return ("(kicad_sch" + "".join(self.header)
                + "".join(e.text for e in self.elements)
                + "".join(self.footer) + ")\n")

    def of_kind(self, kind: str) -> list[Element]:
        return [e for e in self.elements if e.kind == kind]


def _top_level_spans(text: str) -> list[tuple[str, str]]:
    """`(kicad_sch` の直下の子を (先頭シンボル, 元のままの文字列) で返す。"""
    i = text.index("(kicad_sch") + len("(kicad_sch")
    spans: list[tuple[str, str]] = []
    n = len(text)
    while i < n:
        # 次の子の開き括弧まで（間の改行・タブは子に含める）
        j = text.find("(", i)
        if j < 0:
            break
        close = text.rfind(")", i, j) if False else -1  # noqa: F841  (可読性のため明示)
        # ルートの閉じ括弧に到達していないか確認する
        if text[i:j].count(")") > 0:
            break
        depth = 0
        k = j
        in_str = False
        while k < n:
            c = text[k]
            if in_str:
                if c == "\\":
                    k += 2
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
            k += 1
        body = text[j:k + 1]
        head = re.match(r"\(([A-Za-z_][\w]*)", body)
        # 直後の改行までを子に含める（KiCad は要素ごとに改行する）
        end = k + 1
        if end < n and text[end] == "\n":
            end += 1
        spans.append((head.group(1) if head else "?", text[i:end]))
        i = end
    return spans


def load(path: str | Path) -> Sheet:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    sheet = Sheet(path=p)
    for kind, span in _top_level_spans(text):
        if kind in ELEMENT_KINDS:
            sheet.elements.append(_make_element(kind, span))
        elif kind in FOOTER_KINDS or sheet.footer:
            sheet.footer.append(span)
        else:
            sheet.header.append(span)
    return sheet


def _make_element(kind: str, span: str) -> Element:
    ref = name = None
    if kind == "symbol":
        m = re.search(r'\(property "Reference" "([^"]+)"', span)
        ref = m.group(1) if m else None
    elif kind in ("label", "hierarchical_label"):
        m = re.match(r'\s*\(\w+ "([^"]+)"', span)
        name = m.group(1) if m else None
    elif kind == "sheet":
        m = re.search(r'\(property "Sheetname" "([^"]+)"', span)
        name = m.group(1) if m else None
    m = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", span)
    at = (float(m.group(1)), float(m.group(2))) if m else None
    if kind == "wire":
        m = re.search(r"\(xy (-?[\d.]+) (-?[\d.]+)\)", span)
        at = (float(m.group(1)), float(m.group(2))) if m else None
    return Element(kind, span, ref, name, at)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--roundtrip", action="store_true", help="分解→再構成が元と一致するか")
    ap.add_argument("--stats", action="store_true", help="要素の内訳")
    a = ap.parse_args()

    bad = 0
    for path in a.paths:
        sheet = load(path)
        if a.roundtrip:
            original = Path(path).read_text(encoding="utf-8")
            ok = sheet.render() == original
            print(f"{'OK  ' if ok else 'NG  '} {path}")
            if not ok:
                bad += 1
                r = sheet.render()
                for i, (x, y) in enumerate(zip(original, r)):
                    if x != y:
                        print(f"      最初の相違 {i} 文字目: 元={original[i:i+60]!r}")
                        print(f"                          復元={r[i:i+60]!r}")
                        break
                else:
                    print(f"      長さのみ相違 元={len(original)} 復元={len(r)}")
        if a.stats:
            from collections import Counter
            c = Counter(e.kind for e in sheet.elements)
            print(f"{path}: header={len(sheet.header)} footer={len(sheet.footer)} " +
                  " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
