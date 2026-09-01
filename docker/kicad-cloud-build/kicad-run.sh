#!/usr/bin/env bash
#
# このリポジトリの KiCad ファイルに対して kicad-cli をヘッドレス実行するラッパー。
#
# 既定では Docker イメージ kicad-cloud:10.0.6 を使い、無ければホストの
# kicad-cli にフォールバックする（KICAD_BACKEND で固定可）。
# 出力は常にリポジトリ直下の out/ に置き、リポジトリ自体は読み取り専用で
# マウントするので、検証実行が作業ツリーを書き換えることはない。
#
# 使い方:
#   docker/kicad-cloud-build/kicad-run.sh erc              # AudioV2 全体の ERC
#   docker/kicad-cloud-build/kicad-run.sh erc --strict     # 違反があれば非ゼロ終了
#   docker/kicad-cloud-build/kicad-run.sh netlist          # ネットリスト出力
#   docker/kicad-cloud-build/kicad-run.sh erc AudioV2/AmpModule.kicad_sch
#   docker/kicad-cloud-build/kicad-run.sh drift            # 生成スクリプトと実図の乖離
#   docker/kicad-cloud-build/kicad-run.sh drift --strict   # 乖離があれば非ゼロ終了
#   docker/kicad-cloud-build/kicad-run.sh cli sch export bom \
#       -o @OUT@/bom.csv @WORK@/AudioV2/AmpModule.kicad_sch
#   docker/kicad-cloud-build/kicad-run.sh version
#   docker/kicad-cloud-build/kicad-run.sh build            # イメージをビルド(約45分)
#
# 環境変数:
#   KICAD_IMAGE    使用するイメージ    (既定: kicad-cloud:10.0.6)
#   KICAD_BACKEND  auto | docker | local (既定: auto)
#   KICAD_OUT      出力ディレクトリ    (既定: <repo>/out)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../.." && pwd))"

IMAGE="${KICAD_IMAGE:-kicad-cloud:10.0.6}"
OUT_DIR="${KICAD_OUT:-$REPO_ROOT/out}"
BACKEND="${KICAD_BACKEND:-auto}"

# 既定の検証対象: AudioV2 の階層ルートシート
SCH_DEFAULT="AudioV2/AudioV2Case.kicad_sch"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

resolve_backend() {
  # docker に未作成のパスを渡すと root 所有で作られるため、先に作っておく
  mkdir -p "$OUT_DIR"

  case "$BACKEND" in
    docker|local) ;;
    auto)
      if command -v docker >/dev/null 2>&1 && docker image inspect "$IMAGE" >/dev/null 2>&1; then
        BACKEND=docker
      elif command -v kicad-cli >/dev/null 2>&1; then
        BACKEND=local
      else
        die "$IMAGE が無く、ホストにも kicad-cli がありません。
  イメージをビルド: $0 build
  （ソースビルドのため初回は約45分かかります）"
      fi
      ;;
    *) die "KICAD_BACKEND は auto / docker / local のいずれかです: $BACKEND" ;;
  esac

  if [ "$BACKEND" = docker ]; then
    command -v docker >/dev/null 2>&1 || die "docker が見つかりません"
    docker image inspect "$IMAGE" >/dev/null 2>&1 \
      || die "イメージ $IMAGE がありません。'$0 build' でビルドしてください"
    WORK=/work
    OUT=/out
  else
    command -v kicad-cli >/dev/null 2>&1 || die "kicad-cli が見つかりません"
    WORK="$REPO_ROOT"
    OUT="$OUT_DIR"
  fi
}

# kicad-cli をバックエンド経由で実行する。
kc() {
  if [ "$BACKEND" = docker ]; then
    # イメージの既定ユーザは uid 1001。ホスト側の所有権を合わせるため
    # 呼び出し元の uid:gid で走らせ、その uid にホームが無いぶんを
    # HOME と グローバル lib-table のコピーで補う。
    docker run --rm \
      -u "$(id -u):$(id -g)" \
      -e HOME=/tmp/kicad-home \
      -v "$REPO_ROOT:/work:ro" \
      -v "$OUT_DIR:/out" \
      -w /work \
      "$IMAGE" \
      bash -c '
        set -e
        v=$(kicad-cli -v | cut -d . -f 1,2)
        mkdir -p "$HOME/.config/kicad/$v"
        cp -n /usr/share/kicad/template/*-lib-table "$HOME/.config/kicad/$v/" 2>/dev/null || true
        exec "$@"
      ' _ kicad-cli "$@"
  else
    kicad-cli "$@"
  fi
}

summarize_erc() {
  local json="$1"
  command -v python3 >/dev/null 2>&1 || return 0
  [ -f "$json" ] || return 0
  python3 - "$json" <<'PY'
import json, sys
from collections import Counter
with open(sys.argv[1]) as f:
    d = json.load(f)
c = Counter()
for sheet in d.get('sheets', []):
    for v in sheet.get('violations', []):
        c[(v.get('severity', '?'), v.get('type', '?'))] += 1
print(f"\nERC 違反 合計 {sum(c.values())} 件")
for (sev, typ), n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"  {sev:<9} {typ:<32} {n}")
PY
}

cmd_erc() {
  local strict=() sch=""
  for a in "$@"; do
    case "$a" in
      --strict) strict=(--exit-code-violations) ;;
      -*) die "erc: 不明なオプション $a" ;;
      *)  sch="$a" ;;
    esac
  done
  sch="${sch:-$SCH_DEFAULT}"
  [ -f "$REPO_ROOT/$sch" ] || die "スキーマが見つかりません: $sch"

  echo "ERC: $sch  (backend=$BACKEND, image=$IMAGE)"
  kc sch erc --format report --severity-all -o "$OUT/erc.rpt"  "$WORK/$sch"
  local rc=0
  kc sch erc --format json   --severity-all "${strict[@]+"${strict[@]}"}" -o "$OUT/erc.json" "$WORK/$sch" || rc=$?
  summarize_erc "$OUT_DIR/erc.json"
  echo "出力: $OUT_DIR/erc.json, $OUT_DIR/erc.rpt"
  return $rc
}

cmd_netlist() {
  local sch="${1:-$SCH_DEFAULT}"
  [ -f "$REPO_ROOT/$sch" ] || die "スキーマが見つかりません: $sch"
  echo "netlist: $sch  (backend=$BACKEND)"
  kc sch export netlist --format kicadsexpr -o "$OUT/netlist.net" "$WORK/$sch"
  echo "出力: $OUT_DIR/netlist.net"
}

# 任意の kicad-cli コマンドをそのまま渡す。引数中の @WORK@ / @OUT@ を
# バックエンドに応じたパスへ置換する。
cmd_cli() {
  [ $# -gt 0 ] || die "cli: kicad-cli に渡す引数を指定してください"
  local args=() a
  for a in "$@"; do
    a="${a//@WORK@/$WORK}"
    a="${a//@OUT@/$OUT}"
    args+=("$a")
  done
  kc "${args[@]}"
}

# --- drift: 生成スクリプトと実図の乖離を見る -------------------------------
#
# kicad-cli は使わない（バックエンド非依存。必要なのはホストの python3 だけ）。
# 回路図の生成は必ず一時ディレクトリで行い、リポジトリの *.kicad_sch には
# 一切触らない。

DRIFT_TMP=""
drift_cleanup() {
  if [ -n "$DRIFT_TMP" ]; then rm -rf "$DRIFT_TMP"; fi
}

cmd_drift() {
  local strict=0 a
  for a in "$@"; do
    case "$a" in
      --strict) strict=1 ;;
      *) die "drift: 不明なオプション $a" ;;
    esac
  done

  command -v python3 >/dev/null 2>&1 || die "python3 が見つかりません"
  local gen_rel="AudioV2/scripts/wire_circuit_design.py"
  [ -f "$REPO_ROOT/$gen_rel" ] || die "生成スクリプトが見つかりません: $gen_rel"
  mkdir -p "$OUT_DIR"

  DRIFT_TMP="$(mktemp -d "${TMPDIR:-/tmp}/kicad-drift.XXXXXX")"
  trap drift_cleanup EXIT INT TERM

  # AudioV2 を丸ごとコピーし、兄弟の Audio/ のシンボルも置く。生成スクリプトは
  # ../Audio/BP5293_ROHM.kicad_sym などを読むので、これが無いと落ちる。
  cp -R "$REPO_ROOT/AudioV2" "$DRIFT_TMP/AudioV2"
  mkdir -p "$DRIFT_TMP/Audio"
  cp "$REPO_ROOT"/Audio/*.kicad_sym "$DRIFT_TMP/Audio/" \
    || die "drift: Audio/*.kicad_sym をコピーできません（生成スクリプトが参照します）"
  # コピーしてきた実図は消す。残しておくと「生成されなかったシート」が
  # 実図のコピーのまま残り、乖離ゼロに見えてしまう。
  rm -f "$DRIFT_TMP/AudioV2"/*.kicad_sch

  local gen="$DRIFT_TMP/AudioV2/scripts/wire_circuit_design.py"

  # 手編集所有シート（AGENT_HANDOFF.md §2.8）の一覧と、その強制生成フラグは
  # 生成スクリプト自身が知っている。まず素で回して SKIPPED の行から拾う。
  python3 "$gen" all >/dev/null 2>"$DRIFT_TMP/skipped.txt" \
    || { cat "$DRIFT_TMP/skipped.txt" >&2; die "drift: 回路図の生成に失敗しました"; }

  local hand=() force=() line
  while IFS= read -r line; do
    if [ -n "$line" ]; then hand+=(--hand-edited "$line"); fi
  done < <(sed -n 's/^SKIPPED \([^:]*\):.*/\1/p' "$DRIFT_TMP/skipped.txt")
  while IFS= read -r line; do
    if [ -n "$line" ]; then force+=("$line"); fi
  done < <(sed -n 's/.*pass \(--force-[a-z-]*\) to.*/\1/p' "$DRIFT_TMP/skipped.txt")

  # どちらも生成スクリプトの英文メッセージを削って作っている。書式が変わって
  # hand 側だけ空になると、手編集所有シートが [生成コード所有] と表示され、
  # 想定内の差分が「スクリプトか実図が古い」という警告に化ける。両者の件数が
  # 一致することを確認して、静かな誤表示を防ぐ。
  if [ $(( ${#hand[@]} / 2 )) -ne ${#force[@]} ]; then
    cat "$DRIFT_TMP/skipped.txt" >&2
    die "drift: 手編集所有シートの検出に失敗しました（SKIPPED メッセージの書式変更の可能性）"
  fi

  # 手編集所有シートも「いま生成したらどうなるか」を見たいので強制生成する。
  # 一時ディレクトリなのでリポジトリには影響しない。
  echo "drift: wire_circuit_design.py all ${force[*]-} を一時ディレクトリで再生成 → AudioV2/ と比較"
  python3 "$gen" all "${force[@]+"${force[@]}"}" >/dev/null 2>"$DRIFT_TMP/skipped2.txt" \
    || { cat "$DRIFT_TMP/skipped2.txt" >&2; die "drift: 回路図の強制生成に失敗しました"; }
  if grep -q '^SKIPPED' "$DRIFT_TMP/skipped2.txt"; then
    cat "$DRIFT_TMP/skipped2.txt" >&2
    die "drift: 強制生成されなかったシートがあります（--force-* の名前が変わった可能性）"
  fi

  local rc=0
  python3 "$SCRIPT_DIR/sch_drift.py" "$DRIFT_TMP/AudioV2" "$REPO_ROOT/AudioV2" \
    --json "$OUT_DIR/drift.json" "${hand[@]+"${hand[@]}"}" || rc=$?
  [ "$rc" -le 1 ] || die "drift: 比較に失敗しました"
  echo "出力: $OUT_DIR/drift.json"

  # 乖離（rc=1）は既定では成功扱い。CI で落としたいときだけ --strict。
  if [ "$strict" = 1 ]; then return "$rc"; fi
  return 0
}

cmd_build() {
  command -v docker >/dev/null 2>&1 || die "docker が見つかりません"
  echo "$IMAGE をビルドします（ソースビルドのため約45分）..."
  docker build -f "$SCRIPT_DIR/Dockerfile.10.0.6" -t "$IMAGE" "$@" "$SCRIPT_DIR"
}

usage() {
  awk 'NR>2 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "${BASH_SOURCE[0]}"
}

main() {
  local cmd="${1:-}"
  [ $# -gt 0 ] && shift || true
  case "$cmd" in
    build)              cmd_build "$@" ;;                      # ビルドはバックエンド解決不要
    drift)              cmd_drift "$@" ;;                      # kicad-cli 不要
    erc)                resolve_backend; cmd_erc "$@" ;;
    netlist)            resolve_backend; cmd_netlist "$@" ;;
    cli)                resolve_backend; cmd_cli "$@" ;;
    version)            resolve_backend; kc version ;;
    shell)              resolve_backend
                        [ "$BACKEND" = docker ] || die "shell は docker バックエンド専用です"
                        docker run --rm -it -u "$(id -u):$(id -g)" -e HOME=/tmp/kicad-home \
                          -v "$REPO_ROOT:/work:ro" -v "$OUT_DIR:/out" -w /work "$IMAGE" bash ;;
    ""|-h|--help|help)  usage ;;
    *)                  die "不明なコマンド: $cmd（--help を参照）" ;;
  esac
}

main "$@"
