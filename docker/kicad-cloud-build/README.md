# KiCad 10.0.6 クラウドビルド環境

`kicad-cli`（KiCad 10.0.6）をソースからビルドするDockerイメージと、それを使ってこのリポジトリの基板ファイルをヘッドレス検証するラッパースクリプト。GUIなしで ERC・ネットリスト出力・DRC・Gerber出力などをCIやクラウド上で実行するためのもの。

| ファイル | 役割 |
|---|---|
| `Dockerfile.10.0.6` | `kicad-cli` 10.0.6 をソースビルドするイメージ定義 |
| `kicad-run.sh` | リポジトリのファイルに対して kicad-cli を回すラッパー |
| `sch_drift.py` | `kicad-run.sh drift` が使う回路図の突き合わせ（S式パーサ + 差分） |

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
| `drift` | 生成スクリプトの出力と実図の乖離をシート単位で報告。`out/drift.json` |
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

### `drift` — 生成スクリプトと実図の乖離を見る

`AudioV2/scripts/wire_circuit_design.py` が生成する回路図と、リポジトリの実図（KiCad上で手編集されたもの）がどれだけ離れたかをシート単位で報告する。**同期はしない。ズレを見せるだけ。**

```sh
docker/kicad-cloud-build/kicad-run.sh drift

# 乖離があれば非ゼロ終了（CI用）
docker/kicad-cloud-build/kicad-run.sh drift --strict
```

やっていること:

1. 一時ディレクトリに `AudioV2/` をコピーし、`Audio/*.kicad_sym` も兄弟として置く（生成スクリプトが `../Audio/BP5293_ROHM.kicad_sym` などを読むため。無いと落ちる）
2. コピー側の `*.kicad_sch` を消してから `wire_circuit_design.py all` を回す（実図のコピーが残っていると、生成されないシートが「乖離ゼロ」に見えてしまう）
3. 手編集所有シート（[AGENT_HANDOFF.md](../../AudioV2/AGENT_HANDOFF.md) §2.8）は既定でスキップされるので `--force-relay` などを付けて強制生成する。drift が見たいのは「いま生成したらどうなるか」なので強制でよい
4. 生成物とリポジトリの実図を突き合わせて報告する

**リポジトリの `*.kicad_sch` には一切書き込まない。** 生成は一時ディレクトリの中だけで行い、終了時（中断時も）に trap で消す。`kicad-cli` を使わないので、バックエンドの設定とは無関係に動く（必要なのはホストの `python3` だけ）。

シートごとに出るもの:

| 項目 | 内容 |
|---|---|
| 生成のみに存在 / 実図のみに存在 | 片側にしかない部品。参照(designator)は再アノテーションで動くので、同一性は **Value と lib_id** で見る |
| 参照が相違 | 同じ部品だが designator が違う |
| ネット名が相違 | 片側にしか無いネット名（`label` / `hierarchical_label` / `global_label`） |
| 座標が相違 | 同じ部品で座標だけ違うものの件数。明細は `out/drift.json` |
| サブシートが相違 | `(sheet ...)` の Sheetname / Sheetfile / シートピン名。親シートは部品を持たないので、ここが実質的な比較対象になる |

> **「一致」は接続の一致を意味しない。** 比較しているのは *部品（lib_id / Value / ユニット / 座標）*、*ネット名の集合*、*サブシート定義* だけで、**ワイヤ・ジャンクション・no_connect の実配線、およびラベルがどのワイヤに付いているかは見ていない**。同じ名前のラベルが別のワイヤに移動しても検出できない。接続そのものの検証は `erc` と `netlist` の役目。

`[生成コード所有]` / `[手編集所有]` の別は生成スクリプトの `SKIPPED` 出力から取っている。**追随するのは `wire_circuit_design.py` の `HAND_EDITED` 定義であって、§2.8 の表ではない** — 所有権を移すときは両方を直すこと（片方だけだと表示と方針がずれる）。取りこぼしたときは die して黙って通さない。**手編集所有シートの差分は想定内**（KiCad側が正）。生成コード所有シートに差分が出ていたら、スクリプトか実図のどちらかが古い。

実行例（2026-09-01 時点の実出力。`KICAD_BACKEND` 非依存）:

```
drift: wire_circuit_design.py all --force-relay --force-power --force-output を一時ディレクトリで再生成 → AudioV2/ と比較
シート差分（スクリプト再生成 → リポジトリの実図）

  AmpModule.kicad_sch      [生成コード所有] 一致  (部品 生成 28 / 実図 28)
  AudioV2Case.kicad_sch    [生成コード所有] 一致  (部品 生成 0 / 実図 0 · サブシート 6 — 部品を持たないシート。比較はサブシート定義とネット名のみ)
  ControlPanel.kicad_sch   [生成コード所有] 一致  (部品 生成 39 / 実図 39)
  OutputStage.kicad_sch    [手編集所有] 実図のみ 1／ネット名相違 2／座標相違 5  (部品 生成 6 / 実図 7)
    実図のみに存在 1 件:
      J_RAIL601  Connector:Screw_Terminal_01x03 "RAIL IN"
    生成のみのネット名: MUTE_NC_L, MUTE_NC_R
    座標が相違: 5 件（明細は JSON 側）
  PowerModule.kicad_sch    [手編集所有] 生成のみ 3／実図のみ 6／参照相違 6／ネット名相違 4／座標相違 10  (部品 生成 13 / 実図 16)
    生成のみに存在 3 件:
      U2         AudioV2:CH224_50224 "50224_CH224 12V"
      J_PD       Connector:Conn_01x02_Pin "PD_12V/GND to panel"
      J1         Connector:USB_C_Receptacle_USB2.0_16P "USB-C PD in"
    実図のみに存在 6 件:
      J202       Connector:Conn_01x02_Pin "PD module in (1=GND 2=+12V)"
      J203       Connector:Conn_01x02_Pin "VCC_TONE OUT (1=A_GND 2=9V)"
      C208       Device:C "0.1u"
      C204       Device:C "0.1u"
      #FLG0201   power:PWR_FLAG "PWR_FLAG"
      #FLG0202   power:PWR_FLAG "PWR_FLAG"
    参照が相違 6 件:
      生成 C104       → 実図 C206       Device:C "0.1u"
      生成 C302       → 実図 C202       Device:C "0.1u"
      生成 C301       → 実図 C203       Device:C "10u"
      生成 C101       → 実図 C205       Device:C "47u"
      生成 C102       → 実図 C201       Device:C "47u"
      生成 C103       → 実図 C207       Device:C "47u"
    生成のみのネット名: DKMW_VIN, PG_NOCONN, RC_OPEN, VBUS
    座標が相違: 10 件（明細は JSON 側）
  RelayBoard.kicad_sch     [手編集所有] ネット名相違 2／座標相違 24  (部品 生成 32 / 実図 32)
    生成のみのネット名: ADDR_A0, ADDR_A1
    座標が相違: 24 件（明細は JSON 側）

乖離あり。手編集所有シートの差分は想定内（KiCad 側が正: AGENT_HANDOFF.md §2.8）。
生成コード所有シートに差分が出ていたら、スクリプトか実図のどちらかが古い。

比較しているのは 部品(lib_id/Value/ユニット/座標)・ネット名の集合・サブシート(名前/ファイル/ピン名) だけ。
ワイヤやジャンクションの実配線、ラベルがどのワイヤに付いているかは見ていないので、『一致』は接続の一致を意味しない。
出力: /Users/masashiarino/workspace/pcb_work/out/drift.json
```

`kicad_sch` はS式なので、`sch_drift.py` は括弧の対応を数えるパーサで読んでいる。正規表現で属性を拾うと `(property ...)` の内側の `(at ...)` を部品座標と取り違えるなど、隣の要素に食い込んだ誤った組み合わせを拾う。座標は文字列ではなく数値で比べる（生成側は `83.82000000000001` / `127.0`、KiCad が書き戻すと `83.82` / `127` になり、文字列比較では別物に見える）。

### `cli` によるパススルー

`erc` / `netlist` 以外は `cli` で任意のコマンドを渡せる。引数中の `@WORK@` はリポジトリルート、`@OUT@` は出力ディレクトリに置換される（Docker実行時はコンテナ内パス、ローカル実行時はホストパス）。

AudioV2 にはまだ PCB が無い（2026-09-01 に未設計として削除）。以下は旧 `Audio/` の基板を例にした
PCB 系の実行例で、AudioV2 の PCB を起こしたら同じ形でパスを差し替える。

```sh
# BOM 出力（AudioV2 の回路図から）
docker/kicad-cloud-build/kicad-run.sh cli sch export bom --group-by Value \
  -o @OUT@/bom.csv @WORK@/AudioV2/AmpModule.kicad_sch

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
- `drift` は **2026-09-01 に実行確認済み**（ERC 54件・netlist が従来どおり通ること、`git status` で `*.kicad_sch` が無変更であることも同時に確認）。`--strict` が乖離時に 1 を返すこと、一時ディレクトリが残らないこと、`KICAD_BACKEND=docker` を指定してもイメージ無しで動く（＝バックエンド非依存）ことも確認済み。
- `kicad-run.sh` の `erc` / `netlist` / `cli` / `version`、`erc --strict` の非ゼロ終了、存在しないファイルのエラー処理は **`KICAD_BACKEND=local`（kicad-cli 10.0.6）で実行確認済み**。プロジェクトツリーを読み取り専用にした状態でも ERC が完走することを確認しており、`:ro` マウント前提の設計はこれに基づく。
- **未確認**: Docker バックエンド経由の実行（イメージが未ビルドのため）。初回は `kicad-run.sh build` の後に `kicad-run.sh version` で 10.0.6 が返ることを確認すること。
