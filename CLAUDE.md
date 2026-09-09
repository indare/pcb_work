# pcb_work — エージェント向けメモ

KiCad の基板プロジェクト。現在の作業対象は `AudioV2/`。

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

**2026-09-04 に階層を物理の入れ子に合わせた。親は「箱の皮」だけになった。**

```
AudioV2Case（親）  COMMON_L/R・PHONE_L/R・LINE_L/R の6本だけ
└─ MotherBoard
   ├─ MeasureControl
   ├─ AmpBankSwitch  └─ AmpCh1-5
   └─ AmpBankRelay   └─ AmpCh1-5
```

**KiCad の階層シートは配置を縛らない。** どれを別基板に切り出すかは PCB を起こす
とき（B5）に決める。入れ子は「電気的にどこに属するか」だけを言っている。

| シート | 誰が作るか |
|---|---|
| `MotherBoard` | **`scripts/build_motherboard.py`**（冪等・再実行でバイト一致） |
| `AmpBankSwitch` / `AmpBankRelay` | **`scripts/build_daughter.py`**（同上） |
| `MeasureControl` | 生成対象外。**KiCad で直接いじってよい** |
| `AudioV2Case`（親） | `build_motherboard.py` がパッチする |

**生成対象のシートを手で直さないこと。** 回すと上書きされる。回路を変えるならスクリプトを直す。

**⚠ `MeasureControl` にシートピンを足したら `build_motherboard.py` の `CHILD_SHEETS` にも足すこと。**
手編集所有だが、**母板に置かれる側のピンはコードが持っている**。片方だけだと親子で
ピンの対応が取れず `hier_label_mismatch` が出る。

**順序は `build_daughter.py` → `build_motherboard.py`。**
娘基板のファイルを母板がシートとして参照するので、回路を変えたときはこの順が自然。
ただし**逆順でも母板単独でも結果はバイト一致する**（2026-09-04 実測）。親を書くのは
`build_motherboard.py` だけになったため。入れ子化より前にあった
「逆順で 900 行規模の並べ替え差分」「1巡目が過渡状態でラベルが二重に入る」は
**どちらも解消した**。

**⚠ KiCad で開いて保存した後の再生成だけは未検証。** 回したら
`kicad-run.sh erc` の件数が期待値（下の表）に戻ることを確認すること。

`ControlPanel` / `PowerModule` / `OutputStage` / `AmpBank` は**解体済みで `AudioV2/legacy/` に凍結**。
親からは参照されていないが、**`build_motherboard.py` が素材として読むので直すと設計に届く**
（2026-09-03 に PPTC 追加でここを編集し、実際に母板へ反映された）。直したら必ず回すこと。
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
  （新しいマシンで最初にこれ）。**生成物の書き出しは `write_sch()` を通すこと** —
  素の `write_text` は Windows で CRLF になり、内容が同じでも全ファイルが変更扱いになる
- **`sch_facts.py`** — 回路図から機械的に導出できる事実を出す（階層の枚数・部品数・レールごとの
  容量・親子のシート界面・未接続ピン・1本のネットに載った別名）。**読み取り専用。査読の入口**。
  裏の取れ方と限界はスクリプト先頭の docstring にある。**ERC の正はこれではなく `kicad-run.sh erc`**

**⚠ 配線の検証に `sch_drift.py` を使ってはいけない。** ワイヤもジャンクションも比較対象外。

**⚠ `sch_edit.prune()` を生成シートに使ってはいけない**（`MotherBoard` / `AmpBankSwitch` /
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

**2026-09-03 時点の期待値**（これと違ったら何かが変わっている）。**`kicad-cli` 10.0.6・`KICAD_BACKEND=local`（このマシンのホスト KiCad）で実測した値**。版が変われば ERC 件数は動くので、ずれたら先に `kicad-run.sh version` を見ること。
**2026-09-06 に Windows（Git Bash・Docker 無し・同 10.0.6）でも同じ値になることを確認した**:

| | |
|---|---|
| `check_sexpr.py -q AudioV2` | **問題 0**。ファイル数は環境で増える — `AudioV2/.kicad-mcp/` の作業ファイルや、KiCad を開いているときの `_autosave-*` を拾うため。**素の状態で 13、2026-09-06 の実測は 15**（増分は `.kicad-mcp/visual-diff-*-before.kicad_sch` の2件）。どちらも gitignore 済みだが `check_sexpr` はディレクトリを見るので数に出る |
| `kicad-run.sh erc` | **11 件**（2026-09-07 に 29→17→11。17→11 は外部入力端子台 `J_IN401` を入れて `COMMON_L/R` が1ピンでなくなり `isolated_pin_label` が 9→1 になった分。**残る11件は全部宣言済みの型** — `label_dangling` 6 は親の箱外スタブ（[AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md) 参照）、`ground_pin_not_ground` 3 は ±15V アナログSWの VSS が `-15V` で正常、`isolated_pin_label` 1 は `DEST_SENSE_MUTE_NC`（ミュート位置なので意図的に開放）、`multiple_net_names` 1 は `3V3`/`PICO_3V3` の意図的な別名重ね（`build_ui_move.py` が置いた）） |
| `kicad-run.sh netlist` | **部品 391 個・重複 0・注釈警告なし**（2026-09-04 に D-g のヒューズ＋バルクで 371→373、2026-09-06 に D-f の PPTC で 373→374、2026-09-07 に PT2314E のトーン網をDS通りに組み直して抵抗5本減り 374→369、同日 U1607 の入力コンデンサ C1645 で 369→370、D403 の直列抵抗 R401 で 370→371、外部入力端子台 J_IN401 で 371→372、U1604(MBC2596 バック)+C1644+F1603 を削除し NT1603 を足して 372→370。計測タップのバッファ U1611(OPA1656)+R1659/R1660(100k)+C1646/C1647 を足し MCLK_SENSE の R1605 を外して 370→374。2026-09-08 に HP バッファ U501+R501-504+C501-506 で 374→385、I²C レベルシフタ Q401/Q402+R412/R413 で 385→389。2026-09-09 に ENC_INTA/INTB の 10k プルアップ R1661/R1662 で 389→391。`PWR_FLAG` は仮想なので計上外。**`gen_parts_bom.py` が PARTS.md に書く「部品総数」は NetTie 4個も除くので 4 少ない（387）**） |
| `sch_import.py --roundtrip AudioV2/*.kicad_sch` | **全部 OK** |

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
