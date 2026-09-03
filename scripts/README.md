# scripts/

リポジトリ横断のインフラ・環境系スクリプト。

## `cloud-agent-setup.sh`

Cursor Cloud Agent の**ダッシュボード管理（DB管理）開発環境**用の冪等セットアップスクリプト。

このリポジトリの検証ワークフローが前提とするツールを導入する:

| ツール | 用途 |
|---|---|
| KiCad 10 本体 (`kicad-cli` + `pcbnew`) | S式チェック後の `kicad-cli sch export netlist`、ERC / DRC / Gerber / ドリル出力、`Audio/scripts` の pcbnew 依存スクリプト |
| KiCad 標準ライブラリ (`kicad-symbols` / `kicad-footprints` / `kicad-templates`) | 標準シンボル / フットプリントの解決、グローバル lib-table |
| `ngspice` | `AudioV2/spice/*.cir` を `ngspice -b` で回す（設計判断の根拠にした波形の再現） |
| `uv` / `uvx` | README「前提」記載の kicad-mcp-pro（KiCad MCP サーバ）の起動 |

KiCad は公式 PPA `ppa:kicad/kicad-10.0-releases`（Ubuntu 24.04 で `10.0.6`）から
`--no-install-recommends` で導入する。GUI ではなくヘッドレス CLI 検証が目的のため、
`docker/kicad-cloud-build/` のソースビルドイメージと違いフルビルドは不要。

パッケージ構成は `docker/kicad-cloud-build/Dockerfile.10.0.6` の runtime 段にそろえてある
（本体 + シンボル / フットプリント / テンプレート + `ngspice` + グローバル lib-table のシード）。
3D モデル (`kicad-packages3d`, 展開 ~5.6GB) は Dockerfile 側も含めないため対象外。

### モード

| | 動き |
|---|---|
| 既定 | `apt-get` があれば導入する。無ければ**検証のみに落ちる**（下記） |
| `--verify` | 何も導入せず、揃っているかだけ見て報告する。足りなければ非ゼロ終了 |

```sh
bash scripts/cloud-agent-setup.sh            # Cloud Agent の install コマンド
bash scripts/cloud-agent-setup.sh --verify   # 環境が揃っているかだけ見る
```

冪等なので再実行しても安全。

### Windows / macOS では検証のみ

`apt-get` が無い環境では導入せず検証だけする。**黙って「セットアップ完了」と
言わせないため** — 以前は `kicad-cli` と `uv` が既にあるとどちらもスキップし、
`/usr/share/kicad/template/` が無いので lib-table のコピーも飛ばして、
何も検証せずに成功を名乗っていた。

検証は置き場の違いを吸収する。KiCad の設定は Linux が `~/.config/kicad/<ver>`、
Windows が `%APPDATA%/kicad/<ver>`。lib-table の雛形は `kicad-cli` の実体から
`../share/kicad/template` を辿るので、`/usr/share` でも
`C:/Program Files/KiCad/<ver>/share` でも同じ式で当たる。

Windows で KiCad は公式インストーラで入れる（このリポジトリは WSL2 / Docker を
前提にしない）。詳細は `.cursor/rules/kicad-cli-git-bash.mdc`。

> **`ngspice` は Windows の KiCad には CLI が入らない。** 同梱されるのは内蔵
> シミュレータ用の `ngspice.dll` と `lib/ngspice` だけで、`ngspice -b` は打てない。
> `AudioV2/spice/*.cir` を回すなら別途入れる。`--verify` はこれを検出する。
