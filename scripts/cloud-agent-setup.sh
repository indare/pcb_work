#!/usr/bin/env bash
#
# Cursor Cloud Agent (dashboard-managed) 開発環境セットアップ。
#
# このリポジトリの検証ワークフローが前提とするツールを冪等に導入する:
#   - KiCad 10 (kicad-cli + pcbnew Python モジュール)
#       S式健全性チェック後の `kicad-cli sch export netlist`、DRC / Gerber /
#       ドリル出力、および Audio/scripts の pcbnew 依存スクリプトで使う。
#   - uv / uvx
#       README 記載の kicad-mcp-pro (KiCad MCP サーバ) を起動するために使う。
#
# ダッシュボード管理環境の install コマンドとして実行される想定。
# 何度再実行しても安全（各ツールの存在を確認してからのみ導入する）。
#
set -euo pipefail

KICAD_PPA="ppa:kicad/kicad-10.0-releases"

# 1. KiCad 10（kicad-cli と pcbnew Python モジュールを提供）。
#    --no-install-recommends で GUI 3D モデルや巨大ライブラリ一式を避け、
#    ヘッドレス CLI 検証に必要な最小構成だけ入れる。
if ! command -v kicad-cli >/dev/null 2>&1; then
	sudo add-apt-repository -y "$KICAD_PPA"
	sudo apt-get update
	sudo apt-get install -y --no-install-recommends kicad
else
	echo "kicad-cli は導入済み: $(kicad-cli version)"
fi

# 2. uv / uvx（kicad-mcp-pro 用。README「前提」参照）。
#    全ユーザーが使えるよう /usr/local/bin へ配置する。
if ! command -v uv >/dev/null 2>&1; then
	curl -LsSf https://astral.sh/uv/install.sh \
		| sudo env UV_INSTALL_DIR=/usr/local/bin UV_UNMANAGED_INSTALL=/usr/local/bin sh
else
	echo "uv は導入済み: $(uv --version)"
fi

echo "=== セットアップ完了 ==="
kicad-cli version
uv --version
