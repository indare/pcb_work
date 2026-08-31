# scripts/

リポジトリ横断のインフラ・環境系スクリプト。

## `cloud-agent-setup.sh`

Cursor Cloud Agent の**ダッシュボード管理（DB管理）開発環境**用の冪等セットアップスクリプト。

このリポジトリの検証ワークフローが前提とするツールを導入する:

| ツール | 用途 |
|---|---|
| KiCad 10 (`kicad-cli` + `pcbnew`) | S式チェック後の `kicad-cli sch export netlist`、DRC / Gerber / ドリル出力、`Audio/scripts` の pcbnew 依存スクリプト |
| `uv` / `uvx` | README「前提」記載の kicad-mcp-pro（KiCad MCP サーバ）の起動 |

KiCad は公式 PPA `ppa:kicad/kicad-10.0-releases`（Ubuntu 24.04 で `10.0.6`）から
`--no-install-recommends` で導入する。GUI ではなくヘッドレス CLI 検証が目的のため、
`docker/kicad-cloud-build/` のソースビルドイメージと違いフルビルドは不要。

Cloud Agent 環境の `install` コマンドとして実行される。手元でも実行可能:

```sh
bash scripts/cloud-agent-setup.sh
```

冪等なので再実行しても安全。
