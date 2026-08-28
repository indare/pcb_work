#!/usr/bin/env python3
"""KiCad ファイルの構文健全性チェック（S式の括弧対応 / kicad_pro の JSON）。

使い方:
    python3 Audio/scripts/check_sexpr.py                 # リポジトリ全体
    python3 Audio/scripts/check_sexpr.py Audio/Foo.kicad_sch
    python3 Audio/scripts/check_sexpr.py --fix           # 既知パターンを自動修復

--fix は「修復後にファイル全体の括弧が閉じる」場合だけ書き込む。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AT_XY_ONLY = re.compile(r"^(\t+)\(at (-?[0-9.]+) (-?[0-9.]+)\)[\t ]*$")

SEXPR_SUFFIXES = {
    ".kicad_sch",
    ".kicad_pcb",
    ".kicad_sym",
    ".kicad_mod",
    ".kicad_dru",
    ".kicad_wks",
}
JSON_SUFFIXES = {".kicad_pro"}
SKIP_DIRS = {".git", ".history", "__pycache__", ".deps"}


def scan_parens(text: str):
    """括弧の対応を調べる。問題なければ None、あれば (line, message)。"""
    depth = 0
    line = 1
    in_str = False
    i = 0
    n = len(text)
    open_lines: list[int] = []
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
            continue
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
            open_lines.append(line)
        elif c == ")":
            depth -= 1
            if depth < 0:
                return line, "余分な ')'（親ブロックが早く閉じられています）"
            open_lines.pop()
        i += 1
    if in_str:
        return line, '文字列 " が閉じていません'
    if depth > 0:
        head = ", ".join(str(x) for x in open_lines[:5])
        return open_lines[0], f"'(' が {depth} 個閉じていません（開始行: {head}）"
    return None


def indent_of(line: str) -> str:
    body = line.lstrip("\t ")
    return line[: len(line) - len(body)]


def is_self_closed_form(line: str) -> bool:
    """その行だけで '(' から ')' まで完結しているか（文字列内の括弧は無視）。"""
    body = line.strip()
    if not body.startswith("(") or not body.endswith(")"):
        return False
    depth = 0
    in_str = False
    i = 0
    while i < len(body):
        c = body[i]
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
            if depth == 0 and i != len(body) - 1:
                return False  # 1行に複数の形がある
            if depth < 0:
                return False
        i += 1
    return depth == 0 and not in_str


def find_stray_close_candidates(lines: list[str]) -> list[int]:
    """自己完結した行の直後に、より深いインデントの '(' が続く箇所を返す。

    KiCad の出力はインデント＝ネスト深さなので、この形は
    `(property "X" "Y")` のように閉じ括弧が早すぎるサインになる。
    """
    candidates = []
    for idx, raw in enumerate(lines):
        line = raw.rstrip("\n")
        if not is_self_closed_form(line):
            continue
        nxt = next((lines[j] for j in range(idx + 1, len(lines)) if lines[j].strip()), None)
        if nxt is None:
            continue
        if nxt.lstrip("\t ").startswith("(") and len(indent_of(nxt)) > len(indent_of(line)):
            candidates.append(idx)
    return candidates


def find_symbol_at_missing_angle(lines: list[str]) -> list[int]:
    """回路図シンボル実体の `(at x y)` に回転角が無い行。

    KiCad 10 は 'symbol orientation' requires a number でファイル全体を開けなくなる。
    junction / wire / sheet の `(at x y)` は対象外。
    """
    hits = []
    for idx, raw in enumerate(lines):
        if raw.rstrip("\n") != "\t(symbol":
            continue
        for j in range(idx + 1, min(idx + 10, len(lines))):
            body = lines[j].lstrip("\t ")
            if body.startswith("(unit ") or body.startswith("(uuid "):
                break
            m = AT_XY_ONLY.match(lines[j].rstrip("\n"))
            if m and m.group(1) == "\t\t":
                hits.append(j)
                break
    return hits


def try_fix(lines: list[str]) -> tuple[list[str] | None, list[int]]:
    """既知パターンを修復した行リストを返す。直らなければ (None, 候補行)。"""
    stray = find_stray_close_candidates(lines)
    missing_at = find_symbol_at_missing_angle(lines)
    candidates = stray + [i for i in missing_at if i not in stray]
    if not candidates:
        return None, []
    fixed = list(lines)
    for idx in stray:
        stripped = fixed[idx].rstrip("\n")
        eol = fixed[idx][len(stripped) :]
        fixed[idx] = stripped.rstrip()[:-1] + eol  # 末尾の ')' を落とす
    for idx in missing_at:
        stripped = fixed[idx].rstrip("\n")
        eol = fixed[idx][len(stripped) :]
        m = AT_XY_ONLY.match(stripped)
        if m:
            fixed[idx] = f"{m.group(1)}(at {m.group(2)} {m.group(3)} 0){eol}"
    if scan_parens("".join(fixed)) is None and not find_symbol_at_missing_angle(fixed):
        return fixed, candidates
    return None, candidates


def collect(paths: list[str]) -> list[Path]:
    roots = [Path(p) for p in paths] if paths else [Path(".")]
    found: list[Path] = []
    for root in roots:
        if root.is_file():
            found.append(root)
            continue
        for p in sorted(root.rglob("*")):
            if any(part in SKIP_DIRS or part.endswith("-backups") for part in p.parts):
                continue
            if p.is_file() and p.suffix in SEXPR_SUFFIXES | JSON_SUFFIXES:
                found.append(p)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="ファイルまたはディレクトリ（既定: カレント以下すべて）")
    ap.add_argument("--fix", action="store_true", help="既知パターンを自動修復する")
    ap.add_argument("-q", "--quiet", action="store_true", help="問題のあるファイルだけ表示する")
    args = ap.parse_args()

    targets = collect(args.paths)
    if not targets:
        print("対象ファイルがありません", file=sys.stderr)
        return 2

    failures = 0
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")

        if path.suffix in JSON_SUFFIXES:
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                print(f"NG   {path}: JSON エラー {e.lineno}行目: {e.msg}")
                failures += 1
            else:
                if not args.quiet:
                    print(f"OK   {path}")
            continue

        lines = text.splitlines(keepends=True)
        problem = scan_parens(text)
        missing_at = find_symbol_at_missing_angle(lines) if path.suffix == ".kicad_sch" else []

        if problem is None and not missing_at:
            if not args.quiet:
                print(f"OK   {path}")
            continue

        if problem is not None:
            line, msg = problem
            print(f"NG   {path}: {line}行目: {msg}")
        for idx in missing_at:
            print(f"NG   {path}: {idx + 1}行目: シンボルの (at x y) に回転角がありません（KiCad: symbol orientation）")

        if not args.fix:
            failures += 1
            continue

        original = list(lines)
        fixed, candidates = try_fix(lines)
        if fixed is None:
            if candidates:
                shown = ", ".join(str(c + 1) for c in candidates)
                print(f"     自動修復できません。疑いのある行: {shown}")
            else:
                print("     自動修復できません。手で直してください。")
            failures += 1
            continue

        path.write_text("".join(fixed), encoding="utf-8")
        print(f"     修復しました（{len(candidates)}箇所）:")
        for idx in candidates:
            print(f"       {idx + 1}: {original[idx].strip()}  ->  {fixed[idx].strip()}")

    print(f"--- {len(targets)} ファイル / 問題 {failures} 件")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
