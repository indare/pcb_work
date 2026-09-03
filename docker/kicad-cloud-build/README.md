# KiCad 10.0.6 クラウドビルド環境

`kicad-cli`（KiCad 10.0.6）をソースからビルドするDockerイメージと、それを使ってこのリポジトリの基板ファイルをヘッドレス検証するラッパースクリプト。GUIなしで ERC・ネットリスト出力・DRC・Gerber出力などをCIやクラウド上で実行するためのもの。

| ファイル | 役割 |
|---|---|
| `Dockerfile.10.0.6` | `kicad-cli` 10.0.6 をソースビルドするイメージ定義 |
| `kicad-run.sh` | リポジトリのファイルに対して kicad-cli を回すラッパー |
| `sch_drift.py` | 旧構成向けの回路図突き合わせ（S式パーサ + 差分）。**`kicad-run.sh` からは呼ばれない**（下の「生成スクリプトと実図の突き合わせ」） |

公式の Docker Hub イメージ (`kicad/kicad`) が 10.0.6 に追随する前でも、KiCad公式リポジトリの `10.0.6` タグから直接ビルドすることで最新版を使える。ビルドレシピは KiCad 公式の [`kicad/packaging/kicad-docker`](https://gitlab.com/kicad/packaging/kicad-docker)（`Dockerfile.10.0-stable`）をベースに、Debian trixie 向けの内容を Ubuntu 24.04 用のパッケージ名に置き換えたもの。

---

## クイックスタート

```sh
# 1. イメージをビルド（初回のみ・約45分）
docker/kicad-cloud-build/kicad-run.sh build

# 2. AudioV2 全体の ERC を実行
docker/kicad-cloud-build/kicad-run.sh erc
```

出力は `out/erc.json` と `out/erc.rpt`。標準出力には違反の種別ごとの集計が出る（下は `KICAD_BACKEND=local` で実行したときの例）。**件数は 2026-09-01 の実測で、現在の期待値は [`CLAUDE.md`](../../CLAUDE.md) が正**（ここでは追随しない）。

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

# シート単位（例: 母板だけ）
docker/kicad-cloud-build/kicad-run.sh erc AudioV2/MotherBoard.kicad_sch

# 違反があれば失敗させる
docker/kicad-cloud-build/kicad-run.sh erc --strict

# ネットリスト
docker/kicad-cloud-build/kicad-run.sh netlist
```

### 生成スクリプトと実図の突き合わせ（`drift` は廃止）

`kicad-run.sh drift` と、それが使っていた「`wire_circuit_design.py` を一時ディレクトリで回して
実図と突き合わせる」仕組みは **2026-09-03 に削除した**。理由は2つ。

- **前提が消えた。** 構成刷新で現行シートを作るのは `AudioV2/scripts/build_motherboard.py` /
  `build_daughter.py` になり、`wire_circuit_design.py` は**どのシートも書き出さない**
  （旧構成のロジックの記録として残っているだけ）。drift はそれを回していたので比較対象が空になる。
  `--force-*` で無理に書かせても出てくるのは `AudioV2/legacy/` に凍結された旧シートで、
  **現行シートは全部「対象外・比較していない」に落ちる**。実際の出力は
  「リポジトリ側に旧シートが無い＝乖離あり」という**逆向きの警告**になっていた
- **もともと配線の検証には使えない。** ワイヤ・ジャンクション・`no_connect` の実配線と、
  ラベルがどのワイヤに付いているかを比較対象に入れていない
  （[`CLAUDE.md`](../../CLAUDE.md)・[`AGENT_HANDOFF.md`](../../AudioV2/AGENT_HANDOFF.md) §2.8）

代わりに使うもの:

| 見たいもの | 道具 |
|---|---|
| 生成スクリプトと実図のズレ | **生成スクリプトを回して `git diff` が空か見る。** 母板・娘基板の生成は冪等でバイト一致する（[`CLAUDE.md`](../../CLAUDE.md)）ので、これが drift より強い検査になる |
| 統合・移設で接続が保たれたか | **`AudioV2/scripts/netlist_partition.py`** — ネットリストを「ピン集合の集合」で比較する |
| 接続そのもの | `kicad-run.sh erc` / `kicad-run.sh netlist` |

`sch_drift.py` はファイルとしては残してある（旧構成向けの突き合わせとして手で回せる。
`sch_drift.py GEN_DIR REPO_DIR`）。**ただし上記のとおり配線は見ないので、接続の検証にはならない。**
どのシートを誰が作るかは [`CLAUDE.md`](../../CLAUDE.md) と
[`AGENT_HANDOFF.md`](../../AudioV2/AGENT_HANDOFF.md) §2.8 が正。ここでは重複させない。

### `cli` によるパススルー

`erc` / `netlist` 以外は `cli` で任意のコマンドを渡せる。引数中の `@WORK@` はリポジトリルート、`@OUT@` は出力ディレクトリに置換される（Docker実行時はコンテナ内パス、ローカル実行時はホストパス）。

AudioV2 の PCB はまだ未設計（`AudioV2Case.kicad_pcb` は空のスキャフォールドだけ）。以下は旧 `Audio/`
の基板を例にした PCB 系の実行例で、AudioV2 の PCB を起こしたら同じ形でパスを差し替える。

```sh
# BOM 出力（AudioV2 の階層ルートから。子シートも含めて集計される）
docker/kicad-cloud-build/kicad-run.sh cli sch export bom --group-by Value \
  -o @OUT@/bom.csv @WORK@/AudioV2/AudioV2Case.kicad_sch

# DRC / Gerber / ドリル（旧 Audio プロジェクトの基板を例に）
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
- `drift` は **2026-09-03 に削除**（理由は上の「生成スクリプトと実図の突き合わせ」）。2026-09-01 の確認記録もここから外した。削除したのは `drift` 専用のコードと `--help` の記述だけで、`erc` / `netlist` / `cli` / `version` / `build` の引数解釈には触っていない（`AudioV2/scripts/gen_parts_bom.py` が `cli` 経由で BOM を出すため、ここの互換性は壊せない）。
- `kicad-run.sh` の `erc` / `netlist` / `cli` / `version`、`erc --strict` の非ゼロ終了、存在しないファイルのエラー処理は **`KICAD_BACKEND=local`（kicad-cli 10.0.6）で実行確認済み**。プロジェクトツリーを読み取り専用にした状態でも ERC が完走することを確認しており、`:ro` マウント前提の設計はこれに基づく。
- **未確認**: Docker バックエンド経由の実行（イメージが未ビルドのため）。初回は `kicad-run.sh build` の後に `kicad-run.sh version` で 10.0.6 が返ることを確認すること。

---

## Cloud Agent 環境での使い方

このディレクトリの `Dockerfile.10.0.6` は **Docker イメージをソースビルドする**ためのもので、初回に約45分かかる。Cursor Cloud Agent の VM には Docker が入っていないので、この Dockerfile をそのまま `docker build` する経路は使えない。

代わりに、ランタイム成果物（`kicad-cli` 10.0.6 + シンボル / フットプリント / テンプレート）を **apt パッケージで揃える**。その手順が [`scripts/cloud-agent-setup.sh`](../../scripts/cloud-agent-setup.sh)（冪等・[案内](../../scripts/README.md)）で、ダッシュボード管理環境の `install` コマンドとして実行する想定。

| `Dockerfile.10.0.6` | `scripts/cloud-agent-setup.sh` |
|---|---|
| KiCad 10.0.6 をソースからフルビルド | PPA `ppa:kicad/kicad-10.0-releases` から `apt install kicad`（Ubuntu 24.04 で 10.0.6） |
| `kicad-symbols` / `kicad-footprints` / `kicad-templates` を gitlab から clone して install | 同名の apt パッケージ |
| `ngspice` を apt で導入 | 同じ |
| ユーザー設定へ `*-lib-table` をコピー | `~/.config/kicad/<ver>/` へ同じファイルをコピー |
| 3Dモデル (`kicad-packages3d`) は入れない | `--no-install-recommends` で `kicad-libraries` 経由の巻き込みを避ける（展開 ~5.6GB） |
| （対象外） | `uv` / `uvx` — `uvx kicad-mcp-pro` 用。root [README](../../README.md) の「前提」参照 |

**ローカルで回せない検証をクラウドエージェントへ投げるための導線がこれ。** ERC / ネットリスト / DRC / Gerber が向こう側でも同じ結果になることを、パッケージ構成をこの表で Dockerfile に揃えることで担保している。

> スナップショットを取り直したら `kicad-cli version` が `10.0.6` を返すことを確認する。PPA は 10.0 系の最新を出すので、将来 10.0.7 以降に上がるとホスト側の `KICAD_BACKEND=local` と版がずれる。**版差が結果に効く検証では Docker バックエンドを明示する**（上の「バックエンド」節）。
