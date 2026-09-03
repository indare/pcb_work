# AudioV2

**「オペアンプを何個も電子的に切り替えて、なんとなく音が違うのを楽しむ箱」の KiCad プロジェクト。**
計測系が載っているのは「切替素子が音を悪くしないか」を確かめるためで、装置そのものは計測器ではない。
優劣は測定ではなく耳で決める。

母板に電源・トーン・出力段をまとめ、オペアンプと切替素子を載せた**娘基板をヘッダでスタック**する。
娘基板は切替素子だけを替えた版を作り、**同じ箱に混ぜて挿して同一セッションで比べる**
（時間ドリフトと抜き差しを比較に交絡させないため）。**PCB は未着手。**

この段落より詳しいことは以下の文書が正。**README には書かない。**

## 着手する前に読むもの

| | 何が書いてあるか |
|---|---|
| [`../CLAUDE.md`](../CLAUDE.md) | **守ること。シートの所有権**（どれをスクリプトが生成し、どれを KiCad で直すか）**と検証コマンド・その期待値** |
| [`../SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) | ドキュメントに何を書き、何を書かないか。**ドキュメント編集の前に必読** |
| [AGENT_HANDOFF.md](AGENT_HANDOFF.md) | 長い文脈の入口。確定事項の一覧・次にやること・踏んだ落とし穴 |

回路図のシート構成と、手で触ってよいシートは **`CLAUDE.md` の所有権表が正**。
構成は何度も変わっているので、ここには写さない。

## この下にあるもの

| | |
|---|---|
| `*.kicad_sch` / `AudioV2.kicad_sym` / `AudioV2Case.kicad_pro` | 回路図本体。`AudioV2Case.kicad_pcb` は空のスキャフォールド（PCB 未着手） |
| [DECISIONS.md](DECISIONS.md) | **確定事項の正。** 電源レール・切替方式・基板構成・スタック規格。迷ったらここ |
| [CIRCUIT_DESIGN.md](CIRCUIT_DESIGN.md) | 回路の構成、データシートとのピン照合、机上検算 |
| [PARTS.md](PARTS.md) | 品番と機能等価の代替。BOM のブロックは回路図から生成する |
| [WIRING.md](WIRING.md) | 箱配線・シールドの落とし方・図の外にある流用基板との接続 |
| [DEST_SENSE_LADDER.md](DEST_SENSE_LADDER.md) | 出力先センスの抵抗ラダー設計 |
| [spice/](spice/README.md) | 設計判断の根拠に回した ngspice ネットリスト |
| [scripts/](scripts/) | 回路図の生成・編集・検証の道具。どれを何に使うかは `CLAUDE.md` |
| [datasheets/](datasheets/) | 参照したデータシート PDF |
| [legacy/](legacy/README.md) | **母板へ統合済みの旧シート。凍結してある。編集しても設計には反映されない** |
| 発注リスト | **持たない。** 発注のときに [PARTS.md](PARTS.md) §4.1 の生成部品表から起こす。ベンダのデータを読むときの罠は §0b |
| [VOLUME_IC_COMPARISON.md](VOLUME_IC_COMPARISON.md) / [SYMBOL_FIX_TODO.md](SYMBOL_FIX_TODO.md) / [SYMBOL_REVIEW_SUMMARY.md](SYMBOL_REVIEW_SUMMARY.md) | **2026-08-30 前後の記録。** 不採用になった案・当時の作業指示で、現構成より前の内容 |

## 古い記述の読み方

構成を何度も作り直しているので、**どの文書にも日付の違う記述が混在している。**
不採用になった経路も「同じ検討を繰り返さない」ために消さずに残してある。

- **新しい日付の節が正。** 最新は [DECISIONS.md](DECISIONS.md) と
  [AGENT_HANDOFF.md](AGENT_HANDOFF.md) の確定事項に集約されている
- 解体されたシートの名前（`ControlPanel` / `PowerModule` / `OutputStage` / `RelayBoard` /
  `AmpModule` / 10ch 一体の `AmpBank`）が出てくる節は、**旧構成の記録**
- 部品数・ERC 件数・ネット名・ピン接続は**回路図が正**。文書の値は当時のもの
  （[`../SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md)）
