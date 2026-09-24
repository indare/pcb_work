# pcb_work — エージェント向けメモ

KiCad の基板プロジェクト。現在の作業対象は `AudioV2/`。
**`AudioV2.1/` は v2 の全コピー（2026-09-25）** — 選んだ ch だけ電源と入力を生かす構成の検討用。v2 は残す。
現況は [AudioV2.1/NOW.md](AudioV2.1/NOW.md)。コピー側のスクリプトは `AudioV2.1/` を指す（v2 のファイルを触らない）。

## 最初に読むもの

- **[AudioV2/NOW.md](AudioV2/NOW.md)** — **いま何待ちか・次の一手**（1画面）。再開はここから
- **[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)** — 何をどこに書くか。ドキュメント編集の前に必読
- **[AudioV2/AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md)** — 長い文脈・決定の理由と**履歴**（現況の正ではない）

## 進捗とドキュメント（ポチョムキン防止）

**進捗の定義は、コミット可能な差分が次のどれかになること:**
`.kicad_sch` / `.kicad_pcb` / `AudioV2/scripts/` の生成・検証コード。  
HANDOFF や DECISIONS を追記しただけでは進捗に数えない。

エージェントが守ること:

- **工程ラベルを新設しない。** 「ゲート N」「〇〇は閉じた」「B5 解放」などを自分で作って
  着手条件にしない。ユーザーが言ったときだけ使う
- **`AGENT_HANDOFF.md` / `DECISIONS.md` は、ユーザーが更新を頼んだときだけ書く。**
  実測や実装のあと、黙って物語を足さない
- **現況の更新は [AudioV2/NOW.md](AudioV2/NOW.md) だけ。** 短く差し替える。履歴は HANDOFF / DECISIONS
- 回路図から導出できる数値をドキュメントに書かない（[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)）

2026-09-07 に、測定結果のあと「新ゲート」を自作して B5 を止めかけ、同日撤回した。
同じ形を繰り返さないための禁止。

## Cursor と Claude で同じに動かすために

このリポジトリは Cursor と Claude Code の両方から触られる。**同じ事実を2箇所に書くと
必ず片方が腐る** — 実際 `.cursor/rules/work-on-main.mdc` は2世代遅れて、解体済みの
シート名と、回すと `MeasureControl` が消えるコマンドを指示していた（2026-09-03 に修正）。

なので、正は1つに決めてある:

| 事実 | 正 | どう届くか |
|---|---|---|
| シートの所有権・再生成の順・検証の期待値 | **このファイル** | Claude は自動で読む。Cursor は `work-on-main.mdc` から誘導 |
| **いま何待ちか・次の一手** | [AudioV2/NOW.md](AudioV2/NOW.md) | 両方。HANDOFF の現況節よりこちらが正 |
| 何をどこに書くか | [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) | 両方。Cursor 側は `source-of-truth.mdc` が要約＋誘導 |
| S式を壊さない手順 | `.cursor/rules/kicad-sexpr-integrity.mdc` | 両方。Cursor 用の置き場だが**リポジトリ共通のルール** |
| Windows での kicad-cli の回し方 | `.cursor/rules/kicad-cli-git-bash.mdc` | 両方。同上 |
| 長い文脈・決定の理由・履歴 | [AudioV2/AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md) | 両方。**現況は NOW.md** |

`.cursor/rules/*.mdc` のうち `alwaysApply: true` のものは Cursor が必ず読む。
**禁止事項（踏むと壊れるもの）だけは重複して書いてよい** — リンク先にあると踏む。
それ以外は正へのリンクにして、表や数値を複製しない。

## 守ること

### ドキュメントを書くとき

回路図から機械的に導出できる情報（ネットリスト、参照、ピン接続、部品数・値）は
**ドキュメントに書かない**。書く必要があるときは designator ではなく
**ネット名・機能名**で書く（`R501` ではなく「ControlPanel の I2C プルアップ」）。
理由と詳細は [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)。

### シートの所有権

**2026-09-09 に中間の `MotherBoard` を廃止し、内容を親へ繰り上げた。**
箱外 I/O はルート上のコネクタで閉じる（親スタブ用の階層ラベルは不要）。

```
AudioV2Case（旧 MotherBoard の中身）
├─ MeasureControl
├─ FrontPanel
├─ AmpBankSwitch  └─ AmpCh1-4
└─ AmpBankRelay   └─ AmpCh1-4
```

**KiCad の階層シートは配置を縛らない。** どれを別基板に切り出すかは PCB を起こす
とき（B5）に決める。入れ子は「電気的にどこに属するか」だけを言っている。

| シート | 誰が作るか |
|---|---|
| `AudioV2Case`（ルート） | **手編集所有（2026-09-24 に切替）。KiCad で直接／ピンポイント**。`build_motherboard.py` は 09-15 以降の変更を持たず、回すと電気的に別物（3 口スロット等）へ戻るので**安全弁で止まる** |
| `AmpBankSwitch` / `AmpBankRelay` | **`scripts/build_daughter.py`**。ただし**コミット済みの図は手の見た目修正が生成物より新しい**（電気的には一致、2026-09-24 実測）。全面再生成せず、足すものは生成スクリプトに書いたうえで**その要素だけ差し込む**。新しい要素の UUID は `fixed_uids()` で通し番号から切り離す |
| `MeasureControl` | 生成対象外。**KiCad で直接いじってよい** |
| `FrontPanel` | 生成対象外。**KiCad で直接いじってよい**（母板直下。操作系＝ENC/RV/SW/表示。母板↔パネルは `J_PNL`＋`J_PNL_A`） |

**娘基板の回路を変えるときは生成スクリプトも直すこと**（生成スクリプトが回路の正。図だけ直すと次の再生成で消える）。

**⚠ 子シートにシートピンを足したら、ルートのシートシンボルにも KiCad で足すこと。**
片方だけだと親子でピンの対応が取れず `hier_label_mismatch` が出る（`sch_facts.py` の「親子のシート界面」で確かめる）。

**生成物は KiCad の正準形で書き出す（2026-09-10）。** 生成は最後に
`sch_helpers.canonicalize_sch()`（＝`kicad-cli sch upgrade`）を通る。**`kicad-cli` が
無いと落ちる**（`KICAD_CLI` で明示できる。自己診断は `sch_helpers.py` 単体実行）。

これが無いと、**KiCad で開いて保存しただけで 3 万行の差分が出て、再生成すると元へ戻る**
往復が起きる。原因はスクリプトが `.kicad_sym` からシンボル本体をそのまま貼っていること
（`.kicad_sch` の `lib_symbols` とは方言が違い、シンボルごとの `embedded_fonts` /
`in_bom` などが欠ける）。KiCad は読むときは寛容だが保存で自分の形に直す。
**生成物と KiCad の保存結果が 5 枚ともバイト一致することを 2026-09-10 に実測した。**
ここがずれたら、まず `kicad-cli` の版を疑うこと。

`ControlPanel` / `PowerModule` / `OutputStage` / `AmpBank` は**解体済みで `AudioV2/legacy/` に凍結**。
ルートからは参照されていない。`build_motherboard.py` の素材だったが、**ルートが手編集所有になったので（2026-09-24）ここを直しても設計には届かない**。
編集時の注意は [AudioV2/legacy/README.md](AudioV2/legacy/README.md)。

**⚠ 生成スクリプトは KiCad の標準シンボルライブラリを読む。** macOS / Windows / Linux の
どれでも自動で探すが、**新しいマシンで最初に回すのはこれ**:

```bash
python3 AudioV2/scripts/sch_helpers.py     # 見つかった場所と、探した順を全部出す
```

見つからなければ `KICAD_SYMBOL_DIR` で明示する。**Windows で `C:\tmp\kicad-symbols` の
ジャンクションを作る必要はもう無い**（2026-09-06 に自動探索へ変えた）。

道具（すべて `AudioV2/scripts/`）:

- **`sch_import.py`** — `.kicad_sch` を要素へ分解／再構成／平行移動。`--roundtrip` がバイト一致
- **`sch_edit.py`** — 部品単位の編集。ピン座標は KiCad のシンボルから直読み（`extends` も辿る）
- **`netlist_partition.py`** — ネットリストを「ピン集合の集合」で比較。**統合・移設の検証はこれ**
- **`sch_helpers.py`** — 生成の土台。単体で回すと**シンボルライブラリの探索を自己診断**する
  （新しいマシンで最初にこれ。`kicad-cli` の探索も見る）。**生成物の書き出しは `write_sch()`
  を通すこと** — 素の `write_text` は Windows で CRLF になり、内容が同じでも全ファイルが
  変更扱いになる。**書き出しの最後は `canonicalize_sch()`**（上の「正準形」を参照）
- **`sch_facts.py`** — 回路図から機械的に導出できる事実を出す（階層の枚数・部品数・レールごとの
  容量・親子のシート界面・未接続ピン・1本のネットに載った別名）。**読み取り専用。査読の入口**。
  裏の取れ方と限界はスクリプト先頭の docstring にある。**ERC の正はこれではなく `kicad-run.sh erc`**

**⚠ 配線の検証に `sch_drift.py` を使ってはいけない。** ワイヤもジャンクションも比較対象外。

**⚠ `sch_edit.prune()` を生成シートに使ってはいけない**（`AudioV2Case` / `AmpBankSwitch` /
`AmpBankRelay` / `AmpChannel`）。**黙って大量のラベルを消す。**

この設計は生成コードの `net_at()` 方式で**ラベルをピン先に直置き**しており、ワイヤに
乗っていない。一方 `prune()` は「ワイヤに触れていないラベルは浮いている」と判定するので、
**設計の本体を浮きと誤認して落とす**。2026-09-04 に実測: 母板から部品1個を外したら
**ラベル 27 個・階層ラベル 13 個**が一緒に消えた（階層ラベルはシート界面なので親子の
接続が壊れる）。同じ操作を素材の `legacy/*.kicad_sch`（手描き・ラベルはワイヤに乗る）で
やるとワイヤ3本だけで正しく動く。

**生成シートから部品を外すときは素材（`legacy/`）を編集して再生成する。**

`generate_kicad_scaffold.py` は再実行しない — **回すと PGA2310 / ENC×6 / DEST リレーの
旧構成に戻る**（3つとも採用しない方針に変わっている: 音量は手回しポット、ENC は×3、
DEST は機械スイッチ）。理由を書かない禁止は破られるので、ここに理由ごと置く。

### KiCad ファイル（S式）を編集したとき

括弧が1個崩れるだけで KiCad はファイルを開けなくなる。テキスト編集したら必ず検証する。

```bash
python3 Audio/scripts/check_sexpr.py -q Audio
```

詳細は `.cursor/rules/kicad-sexpr-integrity.mdc`（Cursor 用だがこのリポジトリ共通のルール）。

### 検証コマンド

```bash
docker/kicad-cloud-build/kicad-run.sh erc        # AudioV2 全体の ERC
docker/kicad-cloud-build/kicad-run.sh netlist    # ネットリスト出力
```

**2026-09-24 時点の期待値**（これと違ったら何かが変わっている。**回路図を変えたコミットで一緒に更新すること** —
09-10 から 09-24 まで更新されず、その間に ERC が 4→59 件、部品数が 265→352 に動いたのを誰も拾えなかった）。
**`kicad-cli` 10.0.6・`KICAD_BACKEND=local` で実測した値**。版が変われば ERC 件数は動くので、ずれたら先に `kicad-run.sh version` を見ること:

| | |
|---|---|
| `check_sexpr.py -q AudioV2` | **問題 0**。ファイル数は素の状態で 13（`AudioV2/.kicad-mcp/` の作業ファイルや KiCad の `_autosave-*` があると増える。どちらも gitignore 済み） |
| `kicad-run.sh erc` | **5 件、全部宣言済みの型** — `ground_pin_not_ground` 2 は ±15V アナログSWの VSS が `-15V` で正常、`multiple_net_names` 1 は `3V3`/`PICO_3V3` の意図的な別名重ね、`isolated_pin_label` 2 は `AmpBankRelay` の AmpCh4 シートピンの `TONE_L`/`TONE_R`（ネットは全 ch に届いていることを netlist で確認済み）。⚠ ERC の JSON は座標・長さを 1/100 で出し、`sheets[].path` も当てにならない — 場所は項目の `uuid` で引くこと |
| `kicad-run.sh netlist` | **部品 355 個・重複 0・注釈警告なし**（NetTie 4 を含む。2026-09-23 から `AmpBankRelay` を BOM・基板に含める＝シートの `in_bom`/`on_board`=yes）。回路図インスタンスは `sch_facts.py` で同じく **355**。`PWR_FLAG` は仮想なので計上外。**`gen_parts_bom.py` が PARTS.md に書く「部品総数」は NetTie も除く** |
| PCB のフットプリント数 | **355**（netlist と一致）。`kicad-cli pcb drc` の `schematic_parity` が **0 件**であることが正。⚠ **`pcb_sync_from_schematic` は足すだけで、回路図から消えた部品を PCB から消さない**。⚠ `update_pcb_from_sch.py` は逆に**回路図の基板対象外を PCB から消し、パッドにネットも付けない** — 部品を足すときは `place_tmux_1u.py` のようにネットと KIID パスつきで足す |
| `sch_import.py --roundtrip AudioV2/*.kicad_sch` | **全部 OK** |
| `gen_parts_bom.py --check` | **OK**（回路図を変えたら回して PARTS.md をコミットする） |

イメージがあれば Docker(KiCad 10.0.6)、無ければホストの `kicad-cli` で動く。
出力は `out/`（gitignore 済み）。詳細は [docker/kicad-cloud-build/README.md](docker/kicad-cloud-build/README.md)。

### 回路図の査読

査読はエージェントに投げる。定義は **[`.claude/agents/sch-review.md`](.claude/agents/sch-review.md)**
（Claude Code のサブエージェント。`/sch-review [論点]` でも起動する）。

読み取り専用で、回路図もドキュメントも書き換えない。**まず `sch_facts.py all` を回して
回路図から事実を降ろし、そこから指摘を立てる**という順序を定義側で縛ってある。
ドキュメントの数値をそのまま根拠にしないのは [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) と同じ理由。

戻ってきた指摘は**そのまま採用しない**。回路図まで降りているか・確度は何か・外れる条件は
書かれているかを見てから扱う（2026-09-05 の否定側査読では、親エージェント自身の推論が
1件撤回になっている）。

### ブランチ

作業ブランチの正は **`main`**。マージ済みの `cursor/*` を checkout / PR base にしない。
