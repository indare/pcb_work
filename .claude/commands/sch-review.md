---
description: AudioV2 の回路図を査読する（sch-review エージェントを起動）
---

`sch-review` エージェント（`.claude/agents/sch-review.md`）を起動して、AudioV2 の回路図を査読させる。

**論点:** $ARGUMENTS

論点が空なら全面査読。「否定側で」と書かれていたら、エージェント定義 §6 の否定側モードで回す。

エージェントには次を渡すこと:

- 対象は `AudioV2/*.kicad_sch`（親は `AudioV2/AudioV2Case.kicad_sch`）
- **目的は伝えない**（伝えられていないなら、推測して補わない）
- 読み取り専用。回路図もドキュメントも書き換えない

戻ってきた指摘は**そのまま採用しない**。回路図まで降りている指摘か、確度は何か、
外れる条件は書かれているかを見てから扱う。ドキュメントへ反映するときは
[SOURCE_OF_TRUTH.md](../../SOURCE_OF_TRUTH.md) に従う（回路図から導出できる数値を書き写さない）。
現況の更新は [AudioV2/NOW.md](../../AudioV2/NOW.md) だけ。HANDOFF への物語追記はユーザーが頼んだとき。
