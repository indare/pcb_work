# pcb_work — エージェント向けメモ

KiCad の基板プロジェクト。現在の作業対象は `AudioV2/`。

## 最初に読むもの

- **[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)** — 何をどこに書くか。ドキュメント編集の前に必読
- **[AudioV2/AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md)** — 長い文脈・確定事項・シート所有権(§2.8)

## 守ること

### ドキュメントを書くとき

回路図から機械的に導出できる情報（ネットリスト、参照、ピン接続、部品数・値）は
**ドキュメントに書かない**。書く必要があるときは designator ではなく
**ネット名・機能名**で書く（`R501` ではなく「ControlPanel の I2C プルアップ」）。
理由と詳細は [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)。

### シートの所有権

[AudioV2/AGENT_HANDOFF.md §2.8](AudioV2/AGENT_HANDOFF.md) の表が正。
**手編集所有**のシート（RelayBoard / PowerModule / OutputStage）は KiCad 側が正で、
`wire_circuit_design.py` から機械的に上書きしてはいけない。
ロジック変更もそれらは KiCad 側で直接行う。

`generate_kicad_scaffold.py` は再実行しない。

### KiCad ファイル（S式）を編集したとき

括弧が1個崩れるだけで KiCad はファイルを開けなくなる。テキスト編集したら必ず検証する。

```bash
python3 Audio/scripts/check_sexpr.py -q Audio
```

詳細は `.cursor/rules/kicad-sexpr-integrity.mdc`（Cursor 用だがこのリポジトリ共通のルール）。

### 検証コマンド

```bash
docker/kicad-cloud-build/kicad-run.sh erc        # AudioV2 全体の ERC
docker/kicad-cloud-build/kicad-run.sh netlist    # ネットリスト出力
```

イメージがあれば Docker(KiCad 10.0.6)、無ければホストの `kicad-cli` で動く。
出力は `out/`（gitignore 済み）。詳細は [docker/kicad-cloud-build/README.md](docker/kicad-cloud-build/README.md)。

### ブランチ

作業ブランチの正は **`main`**。マージ済みの `cursor/*` を checkout / PR base にしない。
