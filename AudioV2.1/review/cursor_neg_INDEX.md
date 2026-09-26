# v2.1 否定側査読（Cursor 並行）— 索引

- 作成: 2026-09-26
- 対象版: `origin/claude/vibrant-cray-axng64` 先端の `AudioV2.1/DECISIONS.md` / `NOW.md`
- 立場: 読み取り専用の否定側査読。回路図・DECISIONS・NOW は書き換えていない
- ファイル名: `cursor_neg_*`（Claude 側の `design_eval_*` / `*_review.md` 等と衝突しない）

| # | 観点 | ファイル |
|---|---|---|
| ① | 電源と故障の形 | [cursor_neg_01_power_fault.md](cursor_neg_01_power_fault.md) |
| ② | 制御・ファーム・手順 | [cursor_neg_02_control_fw.md](cursor_neg_02_control_fw.md) |
| ③ | 音声の経路の品質 | [cursor_neg_03_audio_path.md](cursor_neg_03_audio_path.md) |
| ④ | DECISIONS の食い違い・古い記述・参照切れ | [cursor_neg_04_decisions_consistency.md](cursor_neg_04_decisions_consistency.md) |
| ⑤ | 部品の入手・熱・実装のしやすさ | [cursor_neg_05_parts_therm_mfg.md](cursor_neg_05_parts_therm_mfg.md) |
| ⑥ | 機械・縦積み・筐体・手の届き（追加） | [cursor_neg_06_mech_stack.md](cursor_neg_06_mech_stack.md) |
| ⑦ | 起動・テスト可能性・デバッグ（追加） | [cursor_neg_07_testability.md](cursor_neg_07_testability.md) |

観点 ①〜⑤は NOW の案。⑥⑦は抜けを補う追加。

前回の全体評価（`design_eval_review.md`、09-25）以降の変更（NJW1194・A1・B7・電源ルート・ヒューズ・LDO 容量など）を含めて見ている。指摘の採用は依頼者側で、回路図／DS まで降ろしてから。
