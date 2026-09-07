#!/usr/bin/env bash
#
# SessionStart フック。Claude Code on the web のコンテナに検証ツールを揃える。
#
# コンテナは回収されると消えるので、毎セッション
#   kicad-cli / シンボルライブラリ / ~/.config/kicad/10.0/*-lib-table / ngspice
# が欠けた状態から始まる。lib-table が抜けると ERC が 29 件ではなく 387 件になる
# （lib_symbol_issues 197 + footprint_link_issues 161 の偽陽性が乗る）。
#
# 中身は書かない。scripts/cloud-agent-setup.sh を呼ぶだけ。
# あれは Cursor Cloud Agent の install コマンドとして既にある冪等スクリプトで、
# 同じことを2箇所に書くと必ず片方が腐る（CLAUDE.md「Cursor と Claude で同じに動かすために」）。
# **足りなかったのはスクリプトではなく、Claude Code のセッションでそれを回す導線。**
set -euo pipefail

# 手元の macOS / Windows では走らせない。KiCad は公式インストーラで入れる前提で、
# 勝手に apt を叩かない。クラウドでだけ効かせる。
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

# 揃わなくてもセッションは開始させる。ここで落とすと、ネットワークが一時的に
# 不調なだけで作業自体が始められなくなる。スクリプトは末尾で自分で検証して
# NG 行を出すので、ここでは足りなかったことを一言添えるだけにする。
"$root/scripts/cloud-agent-setup.sh" \
  || echo "[session-start] 上の NG が残っている。検証コマンドが期待値どおりに動かない可能性がある" >&2
