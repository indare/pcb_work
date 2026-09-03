#!/usr/bin/env python3
"""再生成した回路図と実図を突き合わせ、シートごとの乖離を報告する。

⚠ **これは配線の検証にならない。** ワイヤ・ジャンクション・no_connect の実配線と、
ラベルがどのワイヤに付いているかを比較していない（CLAUDE.md / AGENT_HANDOFF.md §2.8）。
接続の同値は `AudioV2/scripts/netlist_partition.py` と `kicad-run.sh erc` / `netlist` で見る。

⚠ **`kicad-run.sh` からは呼ばれない。** 2026-09-03 の構成刷新で `drift` サブコマンドは
削除した（経緯は README.md「生成スクリプトと実図の突き合わせ」）。旧構成向けの道具として
手で回せるように残しているだけで、現行シートの生成（`build_motherboard.py` /
`build_daughter.py`）は冪等でバイト一致するので、そちらは `git diff` で見るほうが強い。

GEN_DIR には再生成した回路図のディレクトリ、REPO_DIR にはリポジトリの実図（AudioV2/）を渡す。

kicad_sch は S式なので、括弧の対応を数える素朴なパーサで読む。属性を正規表現で
拾うと `(property ...)` の内側の `(at ...)` を部品座標と取り違えるなど、隣の要素に
食い込んだ誤った組み合わせを拾ってしまう。

使い方:
    sch_drift.py GEN_DIR REPO_DIR [--json PATH] [--hand-edited SHEET]...
終了コード:
    0 = 乖離なし / 1 = 乖離あり / 2 = 実行できなかった
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------- S式パーサ

OPEN, CLOSE, ATOM = 0, 1, 2

# ネット名を持つ要素（配線の見た目ではなく接続の意図を表す）
LABEL_TAGS = ("label", "hierarchical_label", "global_label")


def _tokens(text: str):
    """S式をトークン列にする。'(' / ')' と、引用符付き・裸のアトムを区別する。"""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "(":
            yield (OPEN, c)
            i += 1
        elif c == ")":
            yield (CLOSE, c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            buf: list[str] = []
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    buf.append(text[i + 1])
                    i += 2
                else:
                    buf.append(text[i])
                    i += 1
            yield (ATOM, "".join(buf))
            i += 1  # 閉じ引用符
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            yield (ATOM, text[i:j])
            i = j


def parse(text: str) -> list:
    """S式を入れ子のリストにする。アトムは str、リストは list。"""
    root: list = []
    stack = [root]
    for kind, val in _tokens(text):
        if kind == OPEN:
            node: list = []
            stack[-1].append(node)
            stack.append(node)
        elif kind == CLOSE:
            if len(stack) == 1:
                raise ValueError("括弧が閉じすぎています")
            stack.pop()
        else:
            stack[-1].append(val)
    if len(stack) != 1:
        raise ValueError("括弧が閉じていません")
    return root


def kids(node: list, tag: str):
    """直下の子ノードのうちタグが一致するものだけを返す（孫は見ない）。"""
    for c in node:
        if isinstance(c, list) and c and c[0] == tag:
            yield c


def kid(node: list, tag: str):
    return next(kids(node, tag), None)


# ---------------------------------------------------------------- 読み取り


def _num(v: str) -> float:
    try:
        return float(v)
    except ValueError:
        return 0.0


def _at(node: list) -> list[float]:
    """(at x y [rot]) を数値で返す。

    生成側は浮動小数の計算結果をそのまま書くので `83.82000000000001` や
    `127.0` という表記になり、KiCad が書き戻した `83.82` / `127` と
    文字列のまま比べると差分に見えてしまう。丸めて数値で比べる。
    """
    at = kid(node, "at")
    if not at or len(at) < 3:
        return []
    rot = _num(at[3]) if len(at) > 3 else 0.0
    return [round(_num(at[1]), 3), round(_num(at[2]), 3), rot % 360]


def prop(node: list, name: str) -> str:
    """(property "<name>" "<値>" ...) の値。直下の property だけを見る。"""
    for p in kids(node, "property"):
        if len(p) >= 3 and p[1] == name:
            return p[2]
    return ""


def load(path: Path) -> tuple[list[dict], set[str], set[str]]:
    """シートから部品一覧・ネット名・サブシート定義を取り出す。

    ルート直下の (symbol ...) が配置された部品。(lib_symbols ...) 内の
    シンボル定義はルート直下ではないので自然に除かれる。

    親シートは部品を持たないため、部品比較だけでは実質ノーチェックになる。
    (sheet ...) の Sheetname / Sheetfile / シートピン名も比較対象に入れて、
    サブシートの増減やシートピンの付け替えを検出できるようにする。
    """
    tree = parse(path.read_text(encoding="utf-8"))
    root = next((n for n in tree if isinstance(n, list) and n and n[0] == "kicad_sch"), None)
    if root is None:
        raise ValueError(f"kicad_sch ではありません: {path}")

    items = []
    for s in kids(root, "symbol"):
        unit = kid(s, "unit") or []
        items.append(
            {
                "lib_id": (kid(s, "lib_id") or ["lib_id", ""])[1],
                "ref": prop(s, "Reference"),
                "value": prop(s, "Value"),
                "unit": unit[1] if len(unit) > 1 else "1",
                "at": _at(s),
            }
        )

    nets = {n[1] for tag in LABEL_TAGS for n in kids(root, tag) if len(n) > 1}

    sheets = set()
    for sh in kids(root, "sheet"):
        nm = prop(sh, "Sheetname") or "?"
        fn = prop(sh, "Sheetfile") or "?"
        pins = sorted(pn[1] for pn in kids(sh, "pin") if len(pn) > 1)
        sheets.add(f"{nm} -> {fn} [{', '.join(pins)}]")

    return items, nets, sheets


# ---------------------------------------------------------------- 突き合わせ


def _key(p: dict) -> tuple:
    # 参照(designator)は再アノテーションで動くので、同一性は lib_id と Value で見る。
    # マルチユニット部品は同じ lib_id/Value が複数出るのでユニット番号も含める。
    return (p["lib_id"], p["value"], p["unit"])


def _label(p: dict) -> str:
    return p["lib_id"] + (f' "{p["value"]}"' if p["value"] else "")


def compare(gen: Path, act: Path) -> dict:
    """1シート分の差分。

    部品は lib_id/Value/ユニットごとに束ねて対応付ける。同じ束の中では
    「参照が一致するもの」を先に組にし、残りを座標順で組にする。こうすると
    参照が動いただけの部品が「生成のみ／実図のみ」に化けずに済む。
    """
    gen_parts, gen_nets, gen_sheets = load(gen)
    act_parts, act_nets, act_sheets = load(act)

    groups: dict[tuple, tuple[list, list]] = {}
    for p in gen_parts:
        groups.setdefault(_key(p), ([], []))[0].append(p)
    for p in act_parts:
        groups.setdefault(_key(p), ([], []))[1].append(p)

    gen_only, act_only, ref_diff, pos_diff = [], [], [], []

    for key in sorted(groups):
        g, a = groups[key]
        pairs = []

        # 1) 参照が一致するもの同士を先に組にする
        by_ref: dict[str, list] = {}
        for p in a:
            by_ref.setdefault(p["ref"], []).append(p)
        rest_g = []
        for p in g:
            cand = by_ref.get(p["ref"])
            if cand:
                pairs.append((p, cand.pop(0)))
            else:
                rest_g.append(p)
        rest_a = [p for lst in by_ref.values() for p in lst]

        # 2) 残りは座標順に組にする（余った分が片側にしか無い部品）
        rest_g.sort(key=lambda p: (p["at"], p["ref"]))
        rest_a.sort(key=lambda p: (p["at"], p["ref"]))
        for pg, pa in zip(rest_g, rest_a):
            pairs.append((pg, pa))
        gen_only.extend(rest_g[len(rest_a):])
        act_only.extend(rest_a[len(rest_g):])

        for pg, pa in pairs:
            if pg["ref"] != pa["ref"]:
                ref_diff.append({"gen": pg["ref"], "act": pa["ref"], "part": _label(pg)})
            if pg["at"] != pa["at"]:
                pos_diff.append(
                    {
                        "ref": pa["ref"] or pg["ref"],
                        "part": _label(pg),
                        "gen_at": pg["at"],
                        "act_at": pa["at"],
                    }
                )

    def fmt(p: dict) -> dict:
        return {"ref": p["ref"], "part": _label(p)}

    return {
        "gen_parts": len(gen_parts),
        "act_parts": len(act_parts),
        "gen_only": [fmt(p) for p in gen_only],
        "act_only": [fmt(p) for p in act_only],
        "ref_diff": ref_diff,
        "pos_diff": pos_diff,
        "net_gen_only": sorted(gen_nets - act_nets),
        "net_act_only": sorted(act_nets - gen_nets),
        "sheet_gen_only": sorted(gen_sheets - act_sheets),
        "sheet_act_only": sorted(act_sheets - gen_sheets),
        "part_count": [len(gen_parts), len(act_parts)],
        "sheet_count": len(act_sheets),
    }


# ---------------------------------------------------------------- 出力

MAX_LIST = 12  # 一覧に出す件数の上限（超えた分は件数だけ）


def _dump(title: str, items: list, render) -> None:
    if not items:
        return
    print(f"    {title} {len(items)} 件:")
    for it in items[:MAX_LIST]:
        print(f"      {render(it)}")
    if len(items) > MAX_LIST:
        print(f"      … 他 {len(items) - MAX_LIST} 件")


def report_sheet(name: str, d: dict, hand_edited: bool) -> bool:
    kinds = []
    for label, key in (
        ("生成のみ", "gen_only"),
        ("実図のみ", "act_only"),
        ("参照相違", "ref_diff"),
        ("ネット名相違", None),
        ("サブシート相違", "__sheet__"),
        ("座標相違", "pos_diff"),
    ):
        if key is None:
            n = len(d["net_gen_only"]) + len(d["net_act_only"])
        elif key == "__sheet__":
            n = len(d["sheet_gen_only"]) + len(d["sheet_act_only"])
        else:
            n = len(d[key])
        if n:
            kinds.append(f"{label} {n}")

    owner = "手編集所有" if hand_edited else "生成コード所有"
    status = "／".join(kinds) if kinds else "一致"
    print(
        f"  {name:<24} [{owner}] {status}"
        f"  (部品 生成 {d['gen_parts']} / 実図 {d['act_parts']}"
        + (f" · サブシート {d['sheet_count']}" if d.get("sheet_count") else "")
        + (" — 部品を持たないシート。比較はサブシート定義とネット名のみ"
           if d["gen_parts"] == 0 and d["act_parts"] == 0 else "")
        + ")"
    )

    _dump("生成のみに存在", d["gen_only"], lambda i: f"{i['ref']:<10} {i['part']}")
    _dump("実図のみに存在", d["act_only"], lambda i: f"{i['ref']:<10} {i['part']}")
    _dump(
        "参照が相違",
        d["ref_diff"],
        lambda i: f"生成 {i['gen']:<10} → 実図 {i['act']:<10} {i['part']}",
    )
    if d["net_gen_only"]:
        print(f"    生成のみのネット名: {', '.join(d['net_gen_only'])}")
    if d["net_act_only"]:
        print(f"    実図のみのネット名: {', '.join(d['net_act_only'])}")
    for lbl, k in (("生成のみのサブシート", "sheet_gen_only"),
                   ("実図のみのサブシート", "sheet_act_only")):
        for it in d.get(k, []):
            print(f"    {lbl}: {it}")
    if d["pos_diff"]:
        print(f"    座標が相違: {len(d['pos_diff'])} 件（明細は JSON 側）")
    return bool(kinds)


def main() -> int:
    args, positional = sys.argv[1:], []
    json_path: Path | None = None
    hand_edited: set[str] = set()
    i = 0
    while i < len(args):
        if args[i] == "--json":
            i += 1
            json_path = Path(args[i])
        elif args[i] == "--hand-edited":
            i += 1
            hand_edited.add(args[i])
        elif args[i].startswith("-"):
            print(f"error: 不明なオプション {args[i]}", file=sys.stderr)
            return 2
        else:
            positional.append(args[i])
        i += 1

    if len(positional) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    gen_dir, repo_dir = Path(positional[0]), Path(positional[1])

    names = sorted(p.name for p in gen_dir.glob("*.kicad_sch"))
    if not names:
        print(f"error: 再生成されたシートがありません: {gen_dir}", file=sys.stderr)
        return 2

    print("シート差分（スクリプト再生成 → リポジトリの実図）")
    print()
    drifted = False
    results: dict[str, dict] = {}
    for name in names:
        act = repo_dir / name
        if not act.exists():
            print(f"  {name:<24} 実図が存在しません（生成のみ）")
            results[name] = {"missing_in_repo": True}
            drifted = True
            continue
        d = compare(gen_dir / name, act)
        drifted |= report_sheet(name, d, name in hand_edited)
        results[name] = dict(d, hand_edited=name in hand_edited)

    # 生成スクリプトが出力しないシート。乖離ではないが、黙って落とすと
    # 「見ていない範囲」が増えるので必ず名前を出す。
    ungenerated = sorted(p.name for p in repo_dir.glob("*.kicad_sch") if p.name not in names)
    for name in ungenerated:
        print(f"  {name:<24} [対象外] 生成スクリプトが出力しないシート（比較していない）")

    print()
    if drifted:
        print("乖離あり。手編集所有シートの差分は想定内（KiCad 側が正: AGENT_HANDOFF.md §2.8）。")
        print("生成コード所有シートに差分が出ていたら、スクリプトか実図のどちらかが古い。")
    else:
        print("比較した範囲では乖離なし。")
    print()
    print("比較しているのは 部品(lib_id/Value/ユニット/座標)・ネット名の集合・"
          "サブシート(名前/ファイル/ピン名) だけ。")
    print("ワイヤやジャンクションの実配線、ラベルがどのワイヤに付いているかは"
          "見ていないので、『一致』は接続の一致を意味しない。")

    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {"sheets": results, "ungenerated": ungenerated},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
