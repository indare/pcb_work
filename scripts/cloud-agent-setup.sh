#!/usr/bin/env bash
#
# Cursor Cloud Agent (dashboard-managed) 開発環境セットアップ。
#
# このリポジトリの検証ワークフローが前提とするツールを冪等に導入する:
#   - KiCad 10 本体 (kicad-cli + pcbnew Python モジュール)
#   - KiCad 標準ライブラリ (シンボル / フットプリント / テンプレート)
#   - ngspice (AudioV2/spice/*.cir を -b で回す。KiCad 連携ではなく単体実行)
#   - uv / uvx (README 記載の kicad-mcp-pro を起動するために使う)
#
# パッケージ構成は docker/kicad-cloud-build/Dockerfile.10.0.6 の runtime 段に
# そろえてある（kicad / kicad-symbols / kicad-footprints / kicad-templates /
# ngspice + グローバル lib-table のシード）。3D モデル (kicad-packages3d,
# 展開 ~5.6GB) は Dockerfile 側も含めないため対象外。
#
# ダッシュボード管理環境の install コマンドとして実行される想定。
# 何度再実行しても安全（各ツールの存在を確認してからのみ導入する）。
#
set -euo pipefail

KICAD_PPA="ppa:kicad/kicad-10.0-releases"

# 1. KiCad 10 本体 + 標準ライブラリ + SPICE。
#    --no-install-recommends で GUI 3D モデル一式 (kicad-libraries 経由の
#    kicad-packages3d) を避け、ヘッドレス CLI 検証に必要な構成だけ入れる。
if ! command -v kicad-cli >/dev/null 2>&1; then
	sudo add-apt-repository -y "$KICAD_PPA"
	sudo apt-get update
	sudo apt-get install -y --no-install-recommends \
		kicad \
		kicad-symbols \
		kicad-footprints \
		kicad-templates \
		ngspice \
		python3-yaml
else
	echo "kicad-cli は導入済み: $(kicad-cli version)"
fi

# 2. グローバル lib-table をシード（Dockerfile と同じ手順）。
#    プロジェクト外からでも標準シンボル / フットプリントを解決できるようにする。
KICAD_VER="$(kicad-cli version | cut -d. -f1,2)"
KICAD_CFG="$HOME/.config/kicad/$KICAD_VER"
mkdir -p "$KICAD_CFG"
for t in sym-lib-table fp-lib-table; do
	if [ ! -f "$KICAD_CFG/$t" ] && [ -f "/usr/share/kicad/template/$t" ]; then
		cp "/usr/share/kicad/template/$t" "$KICAD_CFG/$t"
	fi
done

# 3. uv / uvx（kicad-mcp-pro 用。README「前提」参照）。
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
