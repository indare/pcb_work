# AudioV2.1

**「オペアンプを電子的に切り替えて、なんとなく音が違うのを楽しむ箱」の KiCad プロジェクト。**
計測系が載っているのは表示と簡易分析のためで、装置そのものは計測器ではない。優劣は測定ではなく耳で決める。

v2.1 は「選んだ ch だけ電源と入力を生かす」構成。何を決めたかは [DECISIONS.md](DECISIONS.md)、いま何待ちかは [NOW.md](NOW.md)。
この段落より詳しいことは以下の文書が正。**README には書かない。**

## 入口

| | 何が書いてあるか |
|---|---|
| [NOW.md](NOW.md) | **いま何待ちか・次の一手。再開はここから** |
| [CLAUDE.md](CLAUDE.md) | 守ること。シートの所有権・禁止事項・検証コマンドと期待値 |
| [DECISIONS.md](DECISIONS.md) | **決定の正。** 何を決めたか・なぜか・何を捨てたか。v2 から引き継いだものは §7 |

## この下にあるもの

| | |
|---|---|
| `*.kicad_sch` / `AudioV2.kicad_sym` / `AudioV2Case.kicad_pro` / `AudioV2Case.kicad_pcb` | 回路図と PCB |
| [lib/](lib/) | プロジェクトの KiCad ライブラリ（`Library.pretty`・`BP5293_ROHM`・`MeasurementADC1804`・`MeasurementADC_Extras`）。名前は図の `lib_id` と PCB の footprint 名が使うので変えない |
| [ds_facts/](ds_facts/) | データシートから読んだ事実（照合済み） |
| [datasheets/](datasheets/README.md) | 参照したデータシート PDF。手持ちオペアンプの DS は `datasheets/opamps/` |
| [OPAMP_STOCK.md](OPAMP_STOCK.md) | 手持ちオペアンプの一覧（ユーザー申告） |
| [PARTS.md](PARTS.md) | 品番と機能等価の代替。BOM のブロックは回路図から生成する |
| [review/](review/README.md) | 調査・否定側査読・棚卸しの記録（凍結。行番号の基準は `review/README.md`） |
| [spice/](spice/README.md) | 設計判断の根拠に回した ngspice ネットリスト |
| [scripts/](scripts/) | 回路図の生成・編集・検証の道具（v2 からの写し。扱いは [CLAUDE.md](CLAUDE.md)） |
| [firmware/](firmware/README.md) | Pico のファーム（骨格） |
| [legacy/](legacy/README.md) | 道具が読む旧シート（v2 からの写し。設計には反映されない） |
| 発注リスト | **持たない。** 発注のときに [PARTS.md](PARTS.md) の生成部品表から起こす。ベンダのデータを読むときの罠は §0b |

部品数・ERC 件数・ネット名・ピン接続は**回路図が正**。文書の値は当時のもの。
