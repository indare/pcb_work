# legacy/ — 母板へ統合済みの旧シート（凍結。編集しない）

`MotherBoard.kicad_sch` を組み立てるための**素材**。設計の一部ではなく、
親（`AudioV2Case.kicad_sch`）からも参照されていない。

| ファイル | 状態 | `build_motherboard.py` が読むか |
|---|---|---|
| `PowerModule.kicad_sch` | 2026-09-03 に母板へ統合。**手描きの配線ごと移設済み** | **読む**（`(0, 0)`） |
| `OutputStage.kicad_sch` | 同上。`+111.76 mm` 平行移動して母板の下半分に入っている | **読む**（`(0, 111.76)`） |
| `ControlPanelAnalog.kicad_sch` | 同上。`+355.6 mm` 右へ | **読む**（`(355.6, 0)`） |
| `AmpBank.kicad_sch` | 娘基板2版（`build_daughter.py`）に置き換わった | **読まない**。完全に記録だけ |

**⚠ 平行移動量は 2.54 の倍数にすること。** 110.0 mm でやったら ERC の
`endpoint_off_grid` が 46 件出た（2026-09-03 実測）。

**⚠ ここは「凍結した素材」であって「無効なファイル」ではない。**
[`../scripts/build_motherboard.py`](../scripts/build_motherboard.py) が**読んで母板に取り込む**ので、
**ここを直すと設計に届く**（2026-09-03 に PPTC 追加でここを編集し、実際に母板へ反映された）。

編集するなら次を守ること。

- **参照の重複を作らない。** `#PWR` / `#FLG` を含む。KiCad で開かずに手で足すと採番されない。
  実際に `#FLG0202` を2個作ってしまい、ネットリストが**注釈エラー**を出した（2026-09-03）
- 直したら **`build_motherboard.py` を回して母板へ反映**する（回さないと素材と生成物がずれる）
- 検証は `netlist_partition.py`。`sch_drift.py` はワイヤを見ないので使えない

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
