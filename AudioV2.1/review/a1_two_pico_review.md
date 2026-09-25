# A1「Pico を 2 個」評価の否定側査読

- 作成: 2026-09-25（否定側の査読エージェント、読み取り専用）。**書いたのはこのファイルだけ**（対象ファイル・DECISIONS・NOW・図・スクリプトは触っていない。commit もしていない）
- 対象: [`review/a1_two_pico.md`](a1_two_pico.md)（以下 **[A1P]**。結論「P1: Pico-A＝UI・トーン・計測・USB、Pico-B＝スタックの制御専用、間は UART が僅差で勝ち」）
- 比較の土台: [`review/design_eval_review.md`](design_eval_review.md)（[DER]、A1 の推奨＝親に制御専用 MCP23017・RESET は Pico の GPIO）、[`review/design_eval_control.md`](design_eval_control.md)（[制]）
- 入口として読んだもの: `AudioV2.1/CLAUDE.md`・`NOW.md`・`DECISIONS.md`（[DEC] §n）。`AudioV2/`・`Audio/` の文書は読んでいない
- 凡例: 〔DS p.xx〕は PDF の通し番号（`pdftotext -layout` の頁）。〔計算〕〔推論〕〔仮定〕は [A1P] と同じ意味。[SF …] は `python3 AudioV2.1/scripts/sch_facts.py …`（図はまだ v2 の回路なので「今ある物」だけ）
- 判定: **支持**（裏が取れた）／**修正**（結論は残るが数値・理由・範囲を直す）／**棄却**（成り立たない）／**確かめられず**（リポジトリの中に根拠が無い）

> 作業中（途中でコンテナが落ちても残るよう、調べながら書き足している）

## 0. 判定の要約（最後に埋める）

（調査中）

---

## 1. ピン数の算術

（調査中）

## 2. リセット直後の状態が「同等」か

（調査中）

## 3. P1 の 3 つの利点の裏

（調査中）

## 4. 見落とし

（調査中）

## 5. 結論の妥当性

（調査中）

## 6. 確かめられなかったこと

（調査中）
