#!/usr/bin/env bash
#
# このリポジトリの検証ワークフローが前提とするツールを、揃える／揃っているか見る。
#
#   - KiCad 10 本体 (kicad-cli + pcbnew Python モジュール)
#   - KiCad 標準ライブラリ (シンボル / フットプリント / テンプレート)
#   - ngspice (AudioV2/spice/*.cir を -b で回す。KiCad 連携ではなく単体実行)
#   - uv / uvx (README 記載の kicad-mcp-pro を起動するために使う)
#
# モード:
#   既定       apt がある環境（Cloud Agent の Ubuntu）では導入する。
#              apt が無い環境（Windows の Git Bash / macOS）では検証のみに落ちる。
#   --verify   何も導入せず、揃っているかだけ見て報告する。足りなければ非ゼロ終了。
#
# パッケージ構成は docker/kicad-cloud-build/Dockerfile.10.0.6 の runtime 段に
# そろえてある（kicad / kicad-symbols / kicad-footprints / kicad-templates /
# ngspice + グローバル lib-table のシード）。3D モデル (kicad-packages3d,
# 展開 ~5.6GB) は Dockerfile 側も含めないため対象外。
#
# ダッシュボード管理環境の install コマンドとして実行される想定。
# 何度再実行しても安全（各ツールの存在を確認してからのみ導入する）。
#
# Windows では KiCad は公式インストーラで入れる（WSL2 / Docker は前提にしない）。
# 詳細は .cursor/rules/kicad-cli-git-bash.mdc。
#
set -euo pipefail

KICAD_PPA="ppa:kicad/kicad-10.0-releases"

# PPA は add-apt-repository を使わず、鍵と sources.list を自分で置いて足す。
#
# **add-apt-repository は使えない。** Claude Code on the web のコンテナでは
# 実体はあるのに `ModuleNotFoundError: No module named 'apt_pkg'` で落ちる
# （python3 と apt_pkg の版がずれている。2026-09-07 実測）。set -e で走る
# このスクリプトはそこで丸ごと止まり、**何も入らないまま終わる**。
# 「クラウドに KiCad のシンボルが無い」の原因がこれだった。
#
# 鍵は keyserver から取らずリポジトリに同梱したものを使う。制限された網では
# HTTPS が直通しないことがあり（この環境は HTTP 直通・HTTPS はプロキシ経由）、
# 取りに行かない方が確実に再現する。どちらにせよ入れる前に指紋を突き合わせる。
KICAD_PPA_URI="http://ppa.launchpad.net/kicad/kicad-10.0-releases/ubuntu"
KICAD_PPA_KEY_FPR="FDA854F61C4D0D9572BB95E5245D5502FAD7A805"
KICAD_PPA_KEYRING="/usr/share/keyrings/kicad-ppa.gpg"
KICAD_PPA_LIST="/etc/apt/sources.list.d/kicad-10.list"
KICAD_PPA_KEY_ASC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docker/kicad-cloud-build/kicad-ppa-10.0.asc"

add_kicad_ppa() {
	if [ ! -f "$KICAD_PPA_KEYRING" ]; then
		command -v gpg >/dev/null 2>&1 \
			|| sudo apt-get install -y --no-install-recommends gnupg \
			|| { sudo apt-get update && sudo apt-get install -y --no-install-recommends gnupg; }
		[ -f "$KICAD_PPA_KEY_ASC" ] || { echo "PPA の署名鍵が無い: $KICAD_PPA_KEY_ASC" >&2; return 1; }
		local fpr
		fpr="$(gpg --show-keys --with-colons "$KICAD_PPA_KEY_ASC" 2>/dev/null | awk -F: '/^fpr:/{print $10; exit}')"
		if [ "$fpr" != "$KICAD_PPA_KEY_FPR" ]; then
			echo "PPA の署名鍵の指紋が合わない (期待 $KICAD_PPA_KEY_FPR / 実際 ${fpr:-読めず})" >&2
			return 1
		fi
		sudo gpg --dearmor --yes -o "$KICAD_PPA_KEYRING" "$KICAD_PPA_KEY_ASC"
		echo "PPA の署名鍵を入れた（指紋 OK）"
	fi
	if [ ! -f "$KICAD_PPA_LIST" ]; then
		local codename
		codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
		printf 'deb [signed-by=%s] %s %s main\n' \
			"$KICAD_PPA_KEYRING" "$KICAD_PPA_URI" "$codename" \
			| sudo tee "$KICAD_PPA_LIST" >/dev/null
		echo "$KICAD_PPA を追加した ($codename)"
	fi
}

MODE=install
case "${1:-}" in
	--verify) MODE=verify ;;
	"")       ;;
	*)        echo "usage: $0 [--verify]" >&2; exit 2 ;;
esac

# apt が無ければ導入はできない。黙って成功を名乗らず検証に落とす。
if [ "$MODE" = install ] && ! command -v apt-get >/dev/null 2>&1; then
	echo "apt-get が無いので導入はしない（検証のみ）。"
	echo "Windows/macOS では KiCad は公式インストーラで入れる。"
	MODE=verify
fi

# --- 置き場の解決（プラットフォームごとに違う） -------------------------
# KiCad の設定ディレクトリ: Linux は ~/.config/kicad/<ver>、
# Windows は %APPDATA%/kicad/<ver>。Git Bash では $APPDATA が見える。
kicad_config_dir() {
	local ver="$1"
	if [ -n "${APPDATA:-}" ] && [ -d "$APPDATA" ]; then
		printf '%s\n' "$APPDATA/kicad/$ver"
	else
		printf '%s\n' "$HOME/.config/kicad/$ver"
	fi
}

# lib-table の雛形。kicad-cli の実体から辿るので、Linux の /usr/share でも
# Windows の "C:/Program Files/KiCad/10.0/share" でも同じ式で当たる。
kicad_template_dir() {
	local bin
	bin="$(command -v kicad-cli)" || return 1
	while [ -L "$bin" ]; do bin="$(readlink "$bin")"; done
	printf '%s\n' "$(cd "$(dirname "$bin")/../share/kicad/template" 2>/dev/null && pwd)"
}

# --- 導入（apt がある環境だけ） -----------------------------------------
install_all() {
	# 1. KiCad 10 本体 + 標準ライブラリ + SPICE。
	#    --no-install-recommends で GUI 3D モデル一式 (kicad-libraries 経由の
	#    kicad-packages3d) を避け、ヘッドレス CLI 検証に必要な構成だけ入れる。
	if ! command -v kicad-cli >/dev/null 2>&1; then
		add_kicad_ppa
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

	# ngspice は kicad-cli とは別に見る。上の塊に混ぜたままだと、
	# kicad-cli だけ先に入っている環境（手で入れた・別経路で入った）で
	# 塊ごと飛ばされ、ngspice が永久に入らない。PPA ではなく標準アーカイブにある。
	if ! command -v ngspice >/dev/null 2>&1; then
		sudo apt-get install -y --no-install-recommends ngspice \
			|| { sudo apt-get update && sudo apt-get install -y --no-install-recommends ngspice; }
	else
		echo "ngspice は導入済み: $(command -v ngspice)"
	fi

	# 2. グローバル lib-table をシード（Dockerfile と同じ手順）。
	#    プロジェクト外からでも標準シンボル / フットプリントを解決できるようにする。
	local ver cfg tpl t
	ver="$(kicad-cli version | cut -d. -f1,2)"
	cfg="$(kicad_config_dir "$ver")"
	tpl="$(kicad_template_dir || true)"
	mkdir -p "$cfg"
	for t in sym-lib-table fp-lib-table; do
		if [ ! -f "$cfg/$t" ] && [ -n "$tpl" ] && [ -f "$tpl/$t" ]; then
			cp "$tpl/$t" "$cfg/$t"
		fi
	done

	# 3. uv / uvx（kicad-mcp-pro 用。README「前提」参照）。
	#    全ユーザーが使えるよう /usr/local/bin へ配置する。
	# ここで失敗しても中断しない。uv は kicad-mcp-pro のためのもので、
	# ERC / ネットリスト / DRC には要らない。astral.sh への HTTPS が通らない網で
	# 全体を巻き添えに止めると、肝心の kicad-cli まで入らないまま終わる。
	# 入らなかったことは末尾の verify_all が NG 行で報せる。
	if ! command -v uv >/dev/null 2>&1; then
		if ! command -v curl >/dev/null 2>&1; then
			echo "curl が無いので uv は入れない（kicad-mcp-pro のみ影響）"
		elif ! curl -LsSf https://astral.sh/uv/install.sh \
			| sudo env UV_INSTALL_DIR=/usr/local/bin UV_UNMANAGED_INSTALL=/usr/local/bin sh; then
			echo "uv を入れられなかった（kicad-mcp-pro のみ影響）。検証は続ける"
		fi
	else
		echo "uv は導入済み: $(uv --version)"
	fi
}

# --- 検証 ---------------------------------------------------------------
# 揃っていないものを数える。0 なら exit 0。
verify_all() {
	local missing=0 ver cfg t

	if command -v kicad-cli >/dev/null 2>&1; then
		ver="$(kicad-cli version | cut -d. -f1,2)"
		echo "OK   kicad-cli $(kicad-cli version)  ($(command -v kicad-cli))"
	else
		echo "NG   kicad-cli が無い（ERC / netlist / DRC が回らない）"
		missing=$((missing + 1))
		ver=""
	fi

	if command -v ngspice >/dev/null 2>&1; then
		echo "OK   ngspice          ($(command -v ngspice))"
	else
		echo "NG   ngspice が無い（AudioV2/spice/*.cir が回らない）"
		# Windows の KiCad は内蔵シミュレータ用の ngspice.dll と lib/ngspice だけを
		# 同梱していて、CLI の ngspice は入らない。dll があるので紛らわしい。
		if [ -n "${APPDATA:-}" ]; then
			echo "     Windows の KiCad が同梱するのは ngspice.dll だけ。CLI は別途入れる"
		fi
		missing=$((missing + 1))
	fi

	if command -v uvx >/dev/null 2>&1; then
		echo "OK   uv $(uv --version 2>/dev/null | awk '{print $2}')             ($(command -v uvx))"
	else
		echo "NG   uvx が無い（kicad-mcp-pro が起動しない）"
		missing=$((missing + 1))
	fi

	if [ -n "$ver" ]; then
		cfg="$(kicad_config_dir "$ver")"
		for t in sym-lib-table fp-lib-table; do
			if [ -f "$cfg/$t" ]; then
				echo "OK   $t   ($cfg)"
			else
				echo "NG   $t が無い: $cfg/$t（標準シンボルが解決できない）"
				missing=$((missing + 1))
			fi
		done
	fi

	if [ "$missing" -gt 0 ]; then
		echo "=== $missing 件足りない ==="
		return 1
	fi
	echo "=== 揃っている ==="
}

if [ "$MODE" = install ]; then
	install_all
	echo "=== セットアップ完了。検証: ==="
fi
verify_all
