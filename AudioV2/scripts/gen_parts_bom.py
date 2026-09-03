#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PARTS.md の「回路図から導出できる部品表」を kicad-cli から生成して差し込む。

方針は [SOURCE_OF_TRUTH.md](../../SOURCE_OF_TRUTH.md):
  回路図から機械的に導出できる情報（参照・値・フットプリント・個数・役割）は
  ドキュメントに手書きしない。書くなら生成する。

このスクリプトは PARTS.md の

    <!-- BEGIN GENERATED: <id> -->
    ... ここだけ毎回まるごと差し替わる ...
    <!-- END GENERATED: <id> -->

で囲まれたブロックだけを書き換える。マーカーの外側 — 調達情報、C&K の現物端子
対応表、選定理由、パネル/箱配線など「回路図から導出できないもの」 — には触らない。

使い方:
    python3 AudioV2/scripts/gen_parts_bom.py           # 生成して PARTS.md を更新
    python3 AudioV2/scripts/gen_parts_bom.py --check   # 実図とズレていれば exit 1（更新しない）
    python3 AudioV2/scripts/gen_parts_bom.py --print   # 差し込む内容を stdout に出すだけ

決定論性（これを壊さないこと）:
  - 行の並びは参照の自然順にこちら側で固定する（kicad-cli の既定順に依存しない）
  - 日時・実行者・ホスト名・kicad-cli のバージョンなど、環境で変わるものは埋め込まない
  → 同じ .kicad_sch なら、誰が何度実行しても同じ PARTS.md になる。

回路図は読むだけで、*.kicad_sch / *.kicad_pcb は書き換えない
（kicad-run.sh はリポジトリを read-only でマウントする）。

⚠ 全数 BOM は必ず階層ルートの AudioV2Case.kicad_sch から取ること。
  AmpBankSwitch / AmpBankRelay を単体で export すると、子シート AmpChannel の
  参照のインスタンス別上書き（ch2=8xx, ch3=9xx…）を kicad-cli が解決できず、
  1 インスタンス分の値しか出ない。旧 AmpBank.kicad_sch でも同じだった。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# 生成するブロックの定義。増やすときはここに1つ足して、PARTS.md 側に
# 同じ id の BEGIN/END マーカーを置くだけでよい。
# --------------------------------------------------------------------------
# kicad-cli sch export bom に渡す列。Description は回路図の部品プロパティ
# （= 役割の記述）で、これも回路図から導出できる情報なので生成側に含める。
_FIELDS = "Reference,Value,Footprint,QUANTITY,Description"
_LABELS = "Refs,Value,Footprint,Qty,Role"
# Value だけでグループ化すると、同一 Value・異 Footprint が 1 行に合流し
# Footprint 列が "fpA,fpB" になる。Phoenix の FP 名自体がカンマを含むので
# 後から気づけない。Footprint もグループキーに入れて分離する。
_GROUP_BY = "Value,Footprint"
# Role 列は同一値グループ内で重複しがちなので、重複を畳んで " / " で繋ぐ
_DEDUPE = "Role"

BLOCKS = [
    {
        # PARTS.md のマーカー id
        "id": "case-bom",
        # 生成元シート（リポジトリルートからの相対パス）。
        # **階層ルート**を渡すのが肝。ここから取ると AmpChannel×10 の
        # インスタンス別参照上書き（ch2=8xx, ch3=9xx…）まで解決されるので、
        # これが唯一の「全数」BOM になる。娘基板シート単体では 1ch 分しか出ない
        # （docstring の ⚠ 参照）。
        "sheet": "AudioV2/AudioV2Case.kicad_sch",
        "fields": _FIELDS,
        "labels": _LABELS,
        "group_by": _GROUP_BY,
        "dedupe_column": _DEDUPE,
        # 表の直前に出す見出し行（生成物の一部。人が書き換えても再生成で戻る）
        "caption": "AudioV2 全体部品表（母板 + 娘基板 + 計測 + 親）",
    },
    {
        # 1ch あたり何が要るかを見るためのテンプレート。娘基板の共通部
        # （切替素子・I2C エキスパンダ・入口バルク・スロット）は含まれない。
        # 発注数の根拠には使えない。使うのは上の case-bom。
        "id": "ampchannel-bom",
        "sheet": "AudioV2/AmpChannel.kicad_sch",
        "fields": _FIELDS,
        "labels": _LABELS,
        "group_by": _GROUP_BY,
        "dedupe_column": _DEDUPE,
        "caption": "AmpChannel 1ch テンプレート（×10 される中身）",
    },
]

MARKER_BEGIN = "<!-- BEGIN GENERATED: {id} -->"
MARKER_END = "<!-- END GENERATED: {id} -->"

TARGET_DOC = "AudioV2/PARTS.md"
RUNNER = "docker/kicad-cloud-build/kicad-run.sh"
SELF = "AudioV2/scripts/gen_parts_bom.py"


def repo_root() -> Path:
    here = Path(__file__).resolve().parent
    try:
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return here.parent.parent


def out_dir(root: Path) -> Path:
    return Path(os.environ.get("KICAD_OUT", root / "out"))


def export_bom(root: Path, block: dict) -> Path:
    """kicad-cli で BOM を CSV に出す。戻り値は CSV の実パス。"""
    csv_name = f"bom_{block['id']}.csv"
    runner = root / RUNNER
    if not runner.exists():
        sys.exit(f"error: {RUNNER} がありません")
    sheet = root / block["sheet"]
    if not sheet.exists():
        sys.exit(f"error: 生成元シートがありません: {block['sheet']}")

    cmd = [
        # kicad-run.sh has a bash shebang; Windows can't exec it directly.
        *(["bash"] if os.name == "nt" else []),
        str(runner), "cli", "sch", "export", "bom",
        "--group-by", block["group_by"],
        "--fields", block["fields"],
        "--labels", block["labels"],
        # 参照の範囲表記（R705-R708 のような省略）を禁止する。
        # 範囲表記は再アノテーションで連番が崩れた瞬間に嘘になった実績がある
        # （SOURCE_OF_TRUTH.md §2）。生成物でも使わない。
        "--ref-range-delimiter", "",
        "-o", f"@OUT@/{csv_name}",
        f"@WORK@/{block['sheet']}",
    ]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        sys.exit(f"error: kicad-cli の BOM 出力に失敗しました ({block['sheet']})")

    path = out_dir(root) / csv_name
    if not path.exists():
        sys.exit(f"error: BOM CSV が見つかりません: {path}")
    return path


_NAT = re.compile(r"(\d+)")


def natural_key(text: str):
    """R701 / R1001 を人間の期待どおりに並べるためのキー。"""
    return tuple(
        int(part) if part.isdigit() else part
        for part in _NAT.split(text)
    )


def dedupe_cell(value: str, qty: str) -> str:
    """グループ内で連結された列を " / " 区切りの読める形にする。

    kicad-cli はグループ内の値を **重複除去してアルファベット順に並べ**、"," で
    連結する（実測: 抵抗10本のグループで Refs 10 個に対し Value は `1k,20k,220k,47R`
    の 4 個）。したがってここでやることは区切りの置換だけで、重複畳み込みではない。

    唯一の危険は値自体にカンマが含まれる場合で、そのときは要素数が Qty を
    超える。超えたら分解せず原文を返す（壊すより読みにくい方がまし）。
    """
    if "," not in value:
        return value
    parts = [p.strip() for p in value.split(",") if p.strip()]
    try:
        expected = int(qty)
    except (TypeError, ValueError):
        return value
    if len(parts) > expected:
        # 値にカンマが埋まっている。分解すると文が切れるので触らない。
        return value
    return " / ".join(parts)


def md_cell(text: str, code: bool = False) -> str:
    text = (text or "").replace("|", "\\|").strip()
    if code and text:
        return f"`{text}`"
    return text


def render_block(root: Path, block: dict) -> str:
    csv_path = export_bom(root, block)
    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        sys.exit(f"error: BOM CSV が空です: {csv_path}")

    header, body = rows[0], rows[1:]
    if not body:
        # ヘッダだけ = 部品0件。黙って空表を書くと --check がグリーンになる。
        sys.exit(f"error: BOM に部品が1件もありません: {csv_path}")
    qty_i = header.index("Qty") if "Qty" in header else None
    dedupe_i = (
        header.index(block["dedupe_column"])
        if block.get("dedupe_column") in header else None
    )
    fp_i = header.index("Footprint") if "Footprint" in header else None

    # 並びはここで固定する（kicad-cli の既定順に依存しない = 決定論的）
    body.sort(key=lambda r: natural_key(r[0]))

    # 部品総数。ネットリストの comp 数と突き合わせられるので、
    # 「シートを取り違えて 1ch 分しか出ていない」のを人が気づける唯一の手がかり。
    # Qty が数値でない行が混じったら黙って諦める（表そのものは正しいので）。
    total_qty = None
    if qty_i is not None:
        try:
            total_qty = sum(int(r[qty_i]) for r in body)
        except (TypeError, ValueError):
            total_qty = None

    lines = [
        "",
        f"**{block['caption']}** — 下の表は `{block['sheet']}` から自動生成しています。",
        "**手で編集しないでください**（次の再生成で消えます）。値・フットプリント・"
        "役割を直すときは KiCad の回路図側を直し、",
        f"`python3 {SELF}` で再生成します。",
        "",
        "> `Refs` 列と `Value` / `Role` 列に**位置の対応はありません**。kicad-cli は"
        "グループ内の値を重複除去してアルファベット順に並べるため、"
        "「n 番目の参照 = n 番目の役割」とは読めません。",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
    ]
    # Footprint が空の個数。AudioV2 の PCB はまだ設計していないので、legacy
    # シートからそのまま持ってきた部品は Footprint が空のまま残っている。
    # 数を出しておかないと表がびっしり埋まって見えて、レイアウト時に気づく。
    no_fp = None
    if fp_i is not None and qty_i is not None:
        try:
            no_fp = sum(int(r[qty_i]) for r in body if not r[fp_i].strip())
        except (TypeError, ValueError):
            no_fp = None

    if total_qty is not None:
        # 見出し群の直後・注記の前に置く。後ろに空行を足さないと注記の
        # blockquote と密着して Markdown が崩れる。
        summary = f"行数 {len(body)} / 部品総数 {total_qty}。"
        if no_fp:
            summary += f"うち **Footprint 未設定 {no_fp} 個**（§5）。"
        lines[5:5] = [summary, ""]
    for row in body:
        cells = []
        for i, cell in enumerate(row):
            if dedupe_i is not None and i == dedupe_i and qty_i is not None:
                cell = dedupe_cell(cell, row[qty_i])
            cells.append(md_cell(cell, code=(i == fp_i)))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def replace_block(text: str, block_id: str, content: str) -> str:
    begin = MARKER_BEGIN.format(id=block_id)
    end = MARKER_END.format(id=block_id)
    if begin not in text or end not in text:
        sys.exit(
            f"error: {TARGET_DOC} に {block_id} のマーカーがありません。\n"
            f"  次の2行で囲んだ場所を作ってください:\n    {begin}\n    {end}"
        )
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    result, n = pattern.subn(lambda _m: begin + content + end, text, count=1)
    if n != 1:
        # BEGIN/END は両方あるのに一致しない = END が BEGIN より前にある等。
        # ここで黙って原文を返すと --check がグリーンのまま通ってしまう。
        sys.exit(
            f"error: {TARGET_DOC} の {block_id} マーカーが不正です"
            f"（BEGIN と END の順序を確認してください）。"
        )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="更新せず、実図とズレていたら exit 1")
    ap.add_argument("--print", dest="do_print", action="store_true",
                    help="差し込む内容を stdout に出すだけ")
    args = ap.parse_args()

    root = repo_root()
    doc = root / TARGET_DOC
    original = doc.read_text(encoding="utf-8")

    updated = original
    for block in BLOCKS:
        content = render_block(root, block)
        if args.do_print:
            print(MARKER_BEGIN.format(id=block["id"]) + content
                  + MARKER_END.format(id=block["id"]))
            continue
        updated = replace_block(updated, block["id"], content)

    if args.do_print:
        return 0

    if args.check:
        if updated != original:
            print(f"NG: {TARGET_DOC} の生成ブロックが回路図と一致していません。")
            print(f"    `python3 {SELF}` を実行して差分をコミットしてください。")
            return 1
        print(f"OK: {TARGET_DOC} の生成ブロックは回路図と一致しています。")
        return 0

    if updated == original:
        print(f"変更なし: {TARGET_DOC}")
    else:
        doc.write_text(updated, encoding="utf-8")
        print(f"更新: {TARGET_DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
