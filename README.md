# PCB Work

KiCad 10 の基板・回路図リポジトリです。**いま設計作業をしているのは `AudioV2/`**。
v1 の実機（AudioCase / MeasurementADC）は `Audio/` にあり、こちらは組んで動いているものです。

## ディレクトリ

| パス | 内容 |
| --- | --- |
| `AudioV2/` | 現行の設計作業。回路図・生成スクリプト・検討メモ。[案内](AudioV2/AGENT_HANDOFF.md) |
| `Audio/` | v1 実機。AudioCase 本体・MeasurementADC・分割 Gerber・計測 FW。[案内](Audio/README.md) |
| `Control/` | Controll 用 Pico2 ファーム（親／子） |
| `docker/` | KiCad 10.0.6 のヘッドレス検証環境（ERC / ネットリスト / DRC / Gerber）。[案内](docker/kicad-cloud-build/README.md) |
| `scripts/` | 環境セットアップ。ローカルで回せない検証をクラウドエージェントへ投げるための導入手順。[案内](scripts/README.md) |
| `.cursor/` | Cursor 用ルール・MCP 設定 |

## いまの実機（要約）

- **Amp → MeasurementADC（LCD スペアナ）** が接続して動作中
- Controll 2 段は外している。EQ は今号では使わない
- 次は MeasurementADC 初号ジャンパの次号解消 → 端子台／ケース
- 詳細: [Audio/MeasurementADC_STATUS.md](Audio/MeasurementADC_STATUS.md)

## Cursor MCP（KiCad）

プロジェクト設定: [`.cursor/mcp.json`](.cursor/mcp.json)  
雛形: [`.cursor/mcp.json.example`](.cursor/mcp.json.example)

個人の絶対パスはコミットしません。Cursor の変数展開を使います。
**2026-09-04 に Cursor で実際に動作確認済み**（`${workspaceFolder}` は展開され、`uvx` は PATH から解決される）。

```json
{
  "mcpServers": {
    "kicad": {
      "type": "stdio",
      "command": "uvx",
      "args": ["kicad-mcp-pro"],
      "env": {
        "KICAD_MCP_PROJECT_DIR": "${workspaceFolder}/AudioV2",
        "KICAD_MCP_PROFILE": "full",
        "KICAD_MCP_OPERATING_MODE": "write"
      }
    }
  }
}
```

### 前提

1. [uv](https://docs.astral.sh/uv/) を入れる（`uvx` が PATH に載ること）
2. Cursor を再起動し、**Settings → Tools & MCP** で `kicad` を ON
3. KiCad で基板を開くときは IPC API を有効にしておく（MCP のライブ連携用）

### 変数

| 値 | 意味 |
| --- | --- |
| `${workspaceFolder}` | このリポジトリのルート（`.cursor/mcp.json` がある側） |
| `KICAD_MCP_PROJECT_DIR` | KiCad プロジェクトディレクトリ（現行は `AudioV2/`） |
| `KICAD_MCP_PROFILE` | `full`（2026-09-02 に `build` から変更。AudioV2 移行と同時） |
| `KICAD_MCP_OPERATING_MODE` | `write`（読み取り専用にしたい場合は `readonly`） |

### PATH に `uvx` が無い場合

ユーザー設定 `~/.cursor/mcp.json`（コミット対象外）にだけフルパスを書いてください。  
ローカル上書き用: `.cursor/mcp.local.env`（gitignore 済み）。

### Windows / Git Bash

このリポジトリの KiCad CLI は Git Bash 経由を想定しています。`kicad-cli` は KiCad 10.0 の bin が PATH にあること。

## MeasurementADC メモ

- 進捗: `Audio/MeasurementADC_STATUS.md`
- 発注: `Audio/MeasurementADC_ORDER.md`
- ブリングアップ履歴: `Audio/MeasurementADC_BRINGUP.md`
- MBC2596-01 FP（0°）: 左上 IN+ / 左下 IN- / 右上 OUT+ / 右下 OUT-
