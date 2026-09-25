# AudioV2.1 — エージェント向けメモ

v2.1 の作業のときはこのファイルがリポジトリ直下の `CLAUDE.md` より優先する（直下の表・期待値・所有権は v2 のもの）。

## 入口

1. **[NOW.md](NOW.md)** — いま何待ちか・次の一手。再開はここから
2. **[DECISIONS.md](DECISIONS.md)** — 決定の正（何を決めたか・なぜか・何を捨てたか）。v2 から引き継いだものは §7（`V21-継-nn`）
3. **[ds_facts/](ds_facts/)** — DS から読んだ事実（照合済み）。DS の PDF は [datasheets/](datasheets/README.md)、手持ちの石は [OPAMP_STOCK.md](OPAMP_STOCK.md)
4. **[review/](review/README.md)** — 凍結した調査・査読の記録。行番号の基準は `review/README.md`

**`AudioV2/`（v2）と `Audio/`（v1）の文書（NOW・DECISIONS・AGENT_HANDOFF・README ほか）を v2.1 の文脈として読まない。**
v2.1 が頼る事実は v2.1 の中に書き直してある。見つからなければ v2・v1 を読みに行かず、ユーザーに聞く。
リポジトリ直下の [SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md) は**原則だけ**使う（回路図から導出できる数値を文書に書かない、部品は機能名・ネット名で書く）。そこから辿る `AudioV2/…` のリンクは読まない。
v2.1 での置き場: 現況は `NOW.md`、決定は `DECISIONS.md`、DS の事実は `ds_facts/`、品番は `PARTS.md`。

## `scripts/` と `legacy/` の扱い

- **`scripts/` と `legacy/` は v2 からの写し。道具が動き続けるためだけに置いている。** 実装の段階で、v2.1 用に新しく書き起こすスクリプトに置き換える
- スクリプト・`legacy/`・`firmware/` のコメントや docstring で v2 を引いているところ（「v2 の DECISIONS」「AGENT_HANDOFF §…」「CIRCUIT_DESIGN」など）は **v2 の記録であって v2.1 の決定ではない**。v2.1 の決定は `DECISIONS.md` を見る
- 設計の行為（回路・定数を決める）と実装の行為（図・スクリプトに入れる）は分ける。文書を直すついでに図やスクリプトの中身を変えない

## シートの所有権

| シート | 誰が作るか |
|---|---|
| `AudioV2Case`（ルート） | **手編集所有。KiCad で直接／ピンポイント。** `build_motherboard.py` は回さない（安全弁で止まる） |
| `AmpBankSwitch` / `AmpBankRelay` | `scripts/build_daughter.py` が回路の正。**全面再生成しない。** 足すものは生成スクリプトに書いたうえで、その要素だけ図へ差し込む |
| `MeasureControl` / `FrontPanel` | 生成対象外。KiCad で直接いじってよい |

⚠ 子シートにシートピンを足したら、ルートのシートシンボルにも KiCad で足すこと（`sch_facts.py iface` で確かめる）。

## 禁止事項（踏むと壊れるもの）

- **`scripts/generate_kicad_scaffold.py` を回さない**（旧構成に戻る。ほかのスクリプトが import するので消さない）
- **`scripts/build_motherboard.py` を回さない**（ルートが電気的に別物へ戻る。`build_daughter.py` が import するので消さない）
- **`sch_edit.prune()` を生成シート（`AudioV2Case` / `AmpBankSwitch` / `AmpBankRelay` / `AmpChannel`）に使わない**（ピン先に直置きしたラベルを浮きと誤認して大量に消す）
- **配線の検証に `sch_drift.py` を使わない**（ワイヤもジャンクションも比較しない）
- **KiCad ライブラリの名前を変えない。** `lib/` の `Library`（フットプリント）・`BP5293_ROHM`・`MeasurementADC1804`・`MeasurementADC_Extras` は v1 と同じ名前で置いてある。名前を変えると図の `lib_id` と PCB の footprint 名が切れる。ライブラリ表は `sym-lib-table`・`fp-lib-table`（`${KIPRJMOD}/lib/…`）
- S式をテキストで直したら必ず `check_sexpr.py` を回す（下）
- 生成物の書き出しは `sch_helpers.write_sch()` を通す（最後に `canonicalize_sch()`＝`kicad-cli sch upgrade`。`kicad-cli` が無いと落ちる）

## 検証コマンドと期待値（v2.1。2026-09-25 実測、kicad-cli 10.0.6・`KICAD_BACKEND=local`）

**図を変えたコミットでは、ここの表を一緒に直す**（リポジトリ直下の `CLAUDE.md` の表は v2 のもの。v2.1 の値をそちらに書かない）。

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2.1
python3 AudioV2.1/scripts/sch_import.py --roundtrip AudioV2.1/*.kicad_sch
python3 AudioV2.1/scripts/gen_parts_bom.py --check
KICAD_BACKEND=local docker/kicad-cloud-build/kicad-run.sh erc AudioV2.1/AudioV2Case.kicad_sch
KICAD_BACKEND=local docker/kicad-cloud-build/kicad-run.sh netlist AudioV2.1/AudioV2Case.kicad_sch
kicad-cli pcb drc --format json --severity-all --schematic-parity -o out/v21/drc.json AudioV2.1/AudioV2Case.kicad_pcb
python3 AudioV2.1/scripts/sch_facts.py all
```

| | 期待値 |
|---|---|
| `check_sexpr.py -q AudioV2.1` | **問題 0**。ファイル数 32（図・PCB・プロジェクト 13 ＋ `lib/` のシンボル 3・フットプリント 16） |
| `sch_import.py --roundtrip` | **6 枚とも OK** |
| `gen_parts_bom.py --check` | **OK**（図を変えたら回して `PARTS.md` をコミットする） |
| `kicad-run.sh erc` | **5 件、型は 3 種** — `ground_pin_not_ground` 2（±15 V アナログ SW の VSS が `-15V`）、`isolated_pin_label` 2（`AmpBankRelay` のシートピン `TONE_L`/`TONE_R`）、`multiple_net_names` 1（`3V3`/`PICO_3V3` の意図的な別名重ね）。場所は項目の `uuid` で引く |
| `kicad-run.sh netlist` | **部品 355・重複 0**（`sch_facts.py` のインスタンス数も 355） |
| `pcb drc --schematic-parity` | **`schematic_parity` 0 件**（2026-09-25 実測）。出たら何かが変わっている |

## 査読を投げるとき

`/sch-review`（`.claude/agents/sch-review.md`）は v2 向けに書かれている。v2.1 に投げるときは次を必ず渡す:

> 対象は `AudioV2.1/*.kicad_sch`（親 `AudioV2.1/AudioV2Case.kicad_sch`）。事実は `python3 AudioV2.1/scripts/sch_facts.py all`。
> 決定は `AudioV2.1/DECISIONS.md`、DS は `AudioV2.1/datasheets/` と `AudioV2.1/ds_facts/`。`AudioV2/`・`Audio/` の文書は読まない。
