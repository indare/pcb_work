# A1 の別案「Pico を 2 個」— 親の制御 MCP23017 案との比較

- 作成: 2026-09-25（評価エージェント、読み取り専用）。書いたのはこのファイルだけ
- 状態: **書きかけ（調べながら追記中）**

## 0. 結論（あとで埋める）

（調査中）

---

## 1. 前提（読んだもの・数え方）

- 入口: `AudioV2.1/CLAUDE.md`・`NOW.md`・`DECISIONS.md`（以下 [DEC] §n）。統合リスト `review/design_eval_review.md`（[DER]）、`review/design_eval_control.md`（[制]）、`review/design_eval_electrical.md`（[電]）
- `AudioV2/`・`Audio/` の文書は読んでいない
- 凡例: 〔DS p.xx〕は DS の PDF ページ（`pdftotext -layout` の頁、PDF の通し番号）／〔計算〕／〔推論〕／〔仮定〕／[SF …] は `python3 AudioV2.1/scripts/sch_facts.py …`（図は v2 の回路なので「今ある物」だけ）
