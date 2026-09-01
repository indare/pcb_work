# KiCad 10.0.6 クラウドビルド環境

`kicad-cli`（KiCad 10.0.6）をソースからビルドするDockerイメージと、それを使ってこのリポジトリの基板ファイルをヘッドレス検証するラッパースクリプト。GUIなしで ERC・ネットリスト出力・DRC・Gerber出力などをCIやクラウド上で実行するためのもの。

| ファイル | 役割 |
|---|---|
| `Dockerfile.10.0.6` | `kicad-cli` 10.0.6 をソースビルドするイメージ定義 |
| `kicad-run.sh` | リポジトリのファイルに対して kicad-cli を回すラッパー |

公式の Docker Hub イメージ (`kicad/kicad`) が 10.0.6 に追随する前でも、KiCad公式リポジトリの `10.0.6` タグから直接ビルドすることで最新版を使える。ビルドレシピは KiCad 公式の [`kicad/packaging/kicad-docker`](https://gitlab.com/kicad/packaging/kicad-docker)（`Dockerfile.10.0-stable`）をベースに、Debian trixie 向けの内容を Ubuntu 24.04 用のパッケージ名に置き換えたもの。

---

## クイックスタート

```sh
# 1. イメージをビルド（初回のみ・約45分）
docker/kicad-cloud-build/kicad-run.sh build

# 2. AudioV2 全体の ERC を実行
docker/kicad-cloud-build/kicad-run.sh erc
```

出力は `out/erc.json` と `out/erc.rpt`。標準出力には違反の種別ごとの集計が出る（下は `KICAD_BACKEND=local` で実行したときの例）。

```
ERC: AudioV2/AudioV2Case.kicad_sch  (backend=local, image=kicad-cloud:10.0.6)

ERC 違反 合計 54 件
  error     pin_not_connected                30
  error     label_dangling                   12
  warning   isolated_pin_label                9
  error     power_pin_not_driven              2
  warning   lib_symbol_issues                 1
出力: /path/to/pcb_work/out/erc.json, /path/to/pcb_work/out/erc.rpt
```

`out/` は `.gitignore` 済み。リポジトリは**読み取り専用でマウント**されるため、検証実行が作業ツリーを書き換えることはない。

---

## `kicad-run.sh`

### コマンド

| コマンド | 内容 |
|---|---|
| `erc [SCH]` | ERC実行。既定の対象は `AudioV2/AudioV2Case.kicad_sch`（階層ルート）。`out/erc.json` + `out/erc.rpt` |
| `netlist [SCH]` | ネットリスト出力（kicadsexpr）。`out/netlist.net` |
| `cli ARGS...` | 任意の `kicad-cli` コマンドをそのまま実行 |
| `version` | 使用中の kicad-cli のバージョン |
| `shell` | コンテナ内で対話シェル（dockerバックエンド専用） |
| `build` | イメージをビルド |

`erc` に `--strict` を付けると、違反があるとき非ゼロで終了する（CI用）。

```sh
# AudioV2 全体
docker/kicad-cloud-build/kicad-run.sh erc

# シート単位（例: RelayBoard だけ）
docker/kicad-cloud-build/kicad-run.sh erc AudioV2/RelayBoard.kicad_sch

# 違反があれば失敗させる
docker/kicad-cloud-build/kicad-run.sh erc --strict

# ネットリスト
docker/kicad-cloud-build/kicad-run.sh netlist
```

### `cli` によるパススルー

`erc` / `netlist` 以外は `cli` で任意のコマンドを渡せる。引数中の `@WORK@` はリポジトリルート、`@OUT@` は出力ディレクトリに置換される（Docker実行時はコンテナ内パス、ローカル実行時はホストパス）。

```sh
# AmpModule の DRC
docker/kicad-cloud-build/kicad-run.sh cli pcb drc --format json \
  -o @OUT@/drc.json @WORK@/AudioV2/AmpModule.kicad_pcb

# Gerber 出力
docker/kicad-cloud-build/kicad-run.sh cli pcb export gerbers \
  -o @OUT@/gerbers/ @WORK@/AudioV2/AmpModule.kicad_pcb

# ドリルファイル
docker/kicad-cloud-build/kicad-run.sh cli pcb export drill \
  -o @OUT@/drill/ @WORK@/AudioV2/AmpModule.kicad_pcb

# 旧 Audio プロジェクトも同様に指定できる
docker/kicad-cloud-build/kicad-run.sh cli pcb drc --format json \
  -o @OUT@/audio-drc.json @WORK@/Audio/split/AudioCase_4_amp.kicad_pcb
```

### バックエンド

既定は `auto`。イメージ `kicad-cloud:10.0.6` があればそれを使い、無ければホストの `kicad-cli` にフォールバックする。どちらも無ければビルド方法を案内して終了する。

| 環境変数 | 既定 | 内容 |
|---|---|---|
| `KICAD_IMAGE` | `kicad-cloud:10.0.6` | 使用するイメージ |
| `KICAD_BACKEND` | `auto` | `auto` / `docker` / `local` |
| `KICAD_OUT` | `<repo>/out` | 出力ディレクトリ |

```sh
# Docker を必ず使う（ホストに別バージョンの kicad-cli があるときに）
KICAD_BACKEND=docker docker/kicad-cloud-build/kicad-run.sh erc

# ホストの kicad-cli を使う
KICAD_BACKEND=local docker/kicad-cloud-build/kicad-run.sh erc
```

ローカルフォールバックはホストの kicad-cli のバージョンに依存する。**バージョン差が結果に効く検証では `KICAD_BACKEND=docker` を明示すること。** `version` サブコマンドで実際に使われている版を確認できる。

---

## イメージのビルド

`kicad-run.sh build` は次と等価:

```sh
docker build -f docker/kicad-cloud-build/Dockerfile.10.0.6 \
  -t kicad-cloud:10.0.6 docker/kicad-cloud-build
```

ソースを `gitlab.com` から `git clone` し、そこから ninja でフルビルドするため、初回は数十分かかる（実測で約45分）。2回目以降は Docker のレイヤーキャッシュが効く。

HTTPSプロキシ経由でしかgitlab.comに出られない環境では `--build-arg HTTPS_PROXY=http://...` を渡す（`kicad-run.sh build --build-arg ...` でそのまま透過する）。プロキシがTLSを終端して独自CAを使っている場合は、Dockerfile内の `ca-certificates` インストール行の前に、そのCA証明書を `/usr/local/share/ca-certificates/` へ `COPY` して `update-ca-certificates` を追加する必要がある。

---

## 直接 `docker run` する場合

`kicad-run.sh` を使わない場合の同等コマンド。イメージの既定ユーザは非rootの `kicad`（uid 1001）なので、ホスト側の所有権を合わせるため呼び出し元の uid/gid で実行し、その uid にホームが無いぶんを `HOME` とグローバル lib-table のコピーで補っている。

```sh
mkdir -p out
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -e HOME=/tmp/kicad-home \
  -v "$PWD":/work:ro \
  -v "$PWD/out":/out \
  -w /work kicad-cloud:10.0.6 \
  bash -c '
    v=$(kicad-cli -v | cut -d . -f 1,2)
    mkdir -p "$HOME/.config/kicad/$v"
    cp -n /usr/share/kicad/template/*-lib-table "$HOME/.config/kicad/$v/" 2>/dev/null || true
    exec "$@"
  ' _ kicad-cli sch erc --format json --severity-all \
      -o /out/erc.json /work/AudioV2/AudioV2Case.kicad_sch
```

`-u` を付けずに既定の `kicad` ユーザで走らせる場合は、`out/` をそのuidから書けるようにしておくこと（例: `chmod 777 out`）。

## バージョン確認

```sh
docker/kicad-cloud-build/kicad-run.sh version
# => 10.0.6
```

---

## 動作確認済み事項

- `mirror.gcr.io` 経由のベースイメージ + `gitlab.com` からのソース取得で、Docker Hub のイメージ配信やKiCad公式サイトへの直接アクセスが制限された環境でもビルド可能なことを確認済み。
- `Audio/split/AudioCase_4_amp.kicad_pcb` に対して実際に DRC・Gerber・ドリル出力を実行し、成功を確認済み（DRC違反7件検出）。
- `kicad-run.sh` の `erc` / `netlist` / `cli` / `version`、`erc --strict` の非ゼロ終了、存在しないファイルのエラー処理は **`KICAD_BACKEND=local`（kicad-cli 10.0.6）で実行確認済み**。プロジェクトツリーを読み取り専用にした状態でも ERC が完走することを確認しており、`:ro` マウント前提の設計はこれに基づく。
- **未確認**: Docker バックエンド経由の実行（イメージが未ビルドのため）。初回は `kicad-run.sh build` の後に `kicad-run.sh version` で 10.0.6 が返ることを確認すること。
