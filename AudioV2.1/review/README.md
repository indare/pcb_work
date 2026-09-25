# review/ — 凍結した調査・査読・監査の記録

ここにあるのは、その時点で書いた調査・否定側査読（`*_review.md`）・棚卸しの**記録**。v2.1 の決定の正は [../DECISIONS.md](../DECISIONS.md)、現況は [../NOW.md](../NOW.md)。
本文は書き換えない。2026-09-25 の独立化で直したのは、DS・在庫表・KiCad ライブラリのパスを v2.1 の中の写しへ向けたことと、壊れたリンクだけ。

## 行番号の基準

- **`AudioV2.1/DECISIONS.md` の行番号（`[DEC:行]`・「DECISIONS Lnnn」など）と、`AudioV2.1/AGENT_HANDOFF.md` の行番号（`[HO:行]` など）は、コミット `5d2cd25` の版の行。**
  そのころの v2.1 の DECISIONS・AGENT_HANDOFF は v2 のバイト一致の写しだった。見たければ `git show 5d2cd25:AudioV2.1/DECISIONS.md`（`AGENT_HANDOFF.md` も同じ）。
  **読まなくてよい。** v2.1 が頼る決定は `../DECISIONS.md` に書き直してある（v2 から引き継いだものは §7）。
- 「v2 Lnnn」「v2 の DECISIONS」も同じ v2 の決定ログの行（上の `5d2cd25` の版と同じ中身）。
- `[NOW] Lnn`・`[NOW:Lnn]` はそれぞれの記録を書いた時点の `AudioV2.1/NOW.md` の行。今の NOW.md とは合わない。

## v1・v2 のパスが出てくるところ

本文に出る `Audio/…`（v1 の測定記録・計測ファーム・v1 の図）、`AudioV2/…`、`Control/…` は、記録を書いたときに読んだ v1・v2 のファイル。
**v2.1 の作業ではこれらを読みに行かない。** 当時の中身が要るときは `git show 6f3cd7e:<パス>` で読める（v1・v2 は main で凍結）。
v1 実機の測定の事実は [tap_facts.md](tap_facts.md) に写してある。

## ここにある v2 と v1 の記録

- [v2_carryover.md](v2_carryover.md) — 「v2.1 では成り立たない v2 の決定」と「訂正された記録」の表（2026-09-25 まで DECISIONS §8・§9 にあったもの）
- [opamp_fast_ds_review_v1.md](opamp_fast_ds_review_v1.md) — 高速寄りオペアンプの DS 精査（v1/v2 のころの分析の写し。DECISIONS の未決の材料）
- [v21_independence_plan.md](v21_independence_plan.md) — v2.1 を v2・v1 から切り離す計画（2026-09-25。実施した内容はユーザーの判断で一部変えた）

## 外部製品の調査

- [cn_dac_amp_survey.md](cn_dac_amp_survey.md) — 中国製 DAC 内蔵アンプの音量・EQ・エフェクト・切替を、製品と部品の両側から調べた記録（2026-09-25）。PT2314E の音量段と電源投入時について DS から分かったこと（§5）、未決への材料（§6）
- [product_board_layout.md](product_board_layout.md) — 製品基板の内部写真と一次資料から学べる配線（2026-09-25）。v2.1 と違うところ（§3）
