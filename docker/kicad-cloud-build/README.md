# KiCad 10.0.6 クラウドビルド環境

`kicad-cli`（KiCad 10.0.6）をソースからビルドするDockerイメージ。GUIなしでDRC・Gerber・ドリルファイル出力などをCIやクラウド上で実行するためのもの。

公式の Docker Hub イメージ (`kicad/kicad`) が 10.0.6 に追随する前でも、KiCad公式リポジトリの `10.0.6` タグから直接ビルドすることで最新版を使える。ビルドレシピは KiCad 公式の [`kicad/packaging/kicad-docker`](https://gitlab.com/kicad/packaging/kicad-docker)（`Dockerfile.10.0-stable`）をベースに、Debian trixie 向けの内容を Ubuntu 24.04 用のパッケージ名に置き換えたもの。

## ビルド

```sh
docker build -f docker/kicad-cloud-build/Dockerfile.10.0.6 \
  -t kicad-cloud:10.0.6 docker/kicad-cloud-build
```

ソースを `gitlab.com` から `git clone` し、そこから ninja でフルビルドするため、初回は数十分かかる（実測で約45分)。2回目以降は Docker のレイヤーキャッシュが効く。

HTTPSプロキシ経由でしかgitlab.comに出られない環境では `--build-arg HTTPS_PROXY=http://...` を渡す。プロキシがTLSを終端して独自CAを使っている場合は、Dockerfile内の `ca-certificates` インストール行の前に、そのCA証明書を `/usr/local/share/ca-certificates/` へ `COPY` して `update-ca-certificates` を追加する必要がある。

## 実行例

このリポジトリの基板ファイルに対してDRCとGerber出力を行う例:

```sh
mkdir -p out
docker run --rm \
  -v "$PWD/Audio":/work:ro \
  -v "$PWD/out":/out \
  -w /work kicad-cloud:10.0.6 \
  kicad-cli pcb drc --format json /work/split/AudioCase_4_amp.kicad_pcb -o /out/drc.json

docker run --rm \
  -v "$PWD/Audio":/work:ro \
  -v "$PWD/out":/out \
  -w /work kicad-cloud:10.0.6 \
  kicad-cli pcb export gerbers /work/split/AudioCase_4_amp.kicad_pcb -o /out/gerbers/
```

`/out` はコンテナ内の非rootユーザー（`kicad`, uid 1001）から書き込めるように、ホスト側で書き込み権限を付けておくこと（例: `chmod 777 out` または `-u $(id -u):$(id -g)` を付けて実行）。

## バージョン確認

```sh
docker run --rm kicad-cloud:10.0.6 kicad-cli version
# => 10.0.6
```

## 動作確認済み事項

- `mirror.gcr.io` 経由のベースイメージ + `gitlab.com` からのソース取得で、Docker Hub のイメージ配信やKiCad公式サイトへの直接アクセスが制限された環境でもビルド可能なことを確認済み。
- 本リポジトリの `Audio/split/AudioCase_4_amp.kicad_pcb` に対して実際に DRC・Gerber・ドリル出力を実行し、成功を確認済み（DRC違反7件検出）。
