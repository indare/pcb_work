# legacy/ — 母板へ統合済みの旧シート（凍結。編集しない）

`MotherBoard.kicad_sch` を組み立てるための**素材**。設計の一部ではなく、
親（`AudioV2Case.kicad_sch`）からも参照されていない。

| ファイル | 状態 |
|---|---|
| `PowerModule.kicad_sch` | 2026-09-03 に母板へ統合。**手描きの配線ごと移設済み** |
| `OutputStage.kicad_sch` | 同上。`+111.76 mm` 平行移動して母板の下半分に入っている |

**編集しないこと。** ここを直しても設計には反映されない。母板の回路を変えるなら
[`../scripts/build_motherboard.py`](../scripts/build_motherboard.py) を直して回す。

## なぜコピーではなく移設なのか

生成コードは 2026-09-03 まで**ワイヤを1本も出せなかった**（ピン先にラベルを置く方式のみ）。
一方この2枚は wire 92 本・junction 33 個を持つ。書き起こし直すとその配線が失われるので、
[`../scripts/sch_import.py`](../scripts/sch_import.py) で **KiCad が書いた S式のまま**読み、
平行移動だけして母板へ入れている。分解→再構成がバイト一致することは `--roundtrip` で検証済み。

## 統合が正しいことの確認方法

`sch_drift.py` はワイヤもジャンクションも比較しないので使えない。**ネットリストの分割**で見る。

```bash
docker/kicad-cloud-build/kicad-run.sh netlist
python3 AudioV2/scripts/netlist_partition.py <統合前の.net> out/netlist.net
```

2026-09-03 の統合時は **310 ネットの分割が完全一致**（名前だけ 4 件が
`/OutputStage/*` → `/MotherBoard/*` に変化）、**ERC も 60 件で前後同一**だった。

## ControlPanelAnalog.kicad_sch（2026-09-03 追加）

`ControlPanel` から UI と Pico を外した残り（`PT2314` と周辺・`BP5293-50`・パネル `PWR SW`・12V LED）。
**B4'-2 で母板へ統合済み**。`build_motherboard.py` がここを読んで母板を組み立てる。

UI（エンコーダ3個・DEST LED・OLED・DEST センスラダー・I2C プルアップ）と `U401`(Pico) は
**B4'-1 で `MeasureControl` へ移した**（D27）。この legacy ファイルには残っていない。
