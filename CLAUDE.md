# pcb_work — エージェント向けメモ

KiCad の基板プロジェクト。現在の作業対象は `AudioV2/`。

## 最初に読むもの

- **[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)** — 何をどこに書くか。ドキュメント編集の前に必読
- **[AudioV2/AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md)** — 長い文脈・確定事項・決定の理由と履歴

## Cursor と Claude で同じに動かすために

このリポジトリは Cursor と Claude Code の両方から触られる。**同じ事実を2箇所に書くと
必ず片方が腐る** — 実際 `.cursor/rules/work-on-main.mdc` は2世代遅れて、解体済みの
シート名と、回すと `MeasureControl` が消えるコマンドを指示していた（2026-09-03 に修正）。

なので、正は1つに決めてある:

| 事実 | 正 | どう届くか |
|---|---|---|
| シートの所有権・再生成の順・検証の期待値 | **このファイル** | Claude は自動で読む。Cursor は `work-on-main.mdc` から誘導 |
| 何をどこに書くか | [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) | 両方。Cursor 側は `source-of-truth.mdc` が要約＋誘導 |
| S式を壊さない手順 | `.cursor/rules/kicad-sexpr-integrity.mdc` | 両方。Cursor 用の置き場だが**リポジトリ共通のルール** |
| Windows での kicad-cli の回し方 | `.cursor/rules/kicad-cli-git-bash.mdc` | 両方。同上 |
| 長い文脈・決定の理由・履歴 | [AudioV2/AGENT_HANDOFF.md](AudioV2/AGENT_HANDOFF.md) | 両方 |

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

道具（すべて `AudioV2/scripts/`）:

- **`sch_import.py`** — `.kicad_sch` を要素へ分解／再構成／平行移動。`--roundtrip` がバイト一致
- **`sch_edit.py`** — 部品単位の編集。ピン座標は KiCad のシンボルから直読み（`extends` も辿る）
- **`netlist_partition.py`** — ネットリストを「ピン集合の集合」で比較。**統合・移設の検証はこれ**

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

**2026-09-03 時点の期待値**（これと違ったら何かが変わっている）。**`kicad-cli` 10.0.6・`KICAD_BACKEND=local`（このマシンのホスト KiCad）で実測した値**。版が変われば ERC 件数は動くので、ずれたら先に `kicad-run.sh version` を見ること:

| | |
|---|---|
| `check_sexpr.py -q AudioV2` | **13 ファイル / 問題 0**（KiCad を開いていると `_autosave-*` が増えて **15** になる。gitignore 済みだが `check_sexpr` はディレクトリを見るので数に出る） |
| `kicad-run.sh erc` | **29 件** |
| `kicad-run.sh netlist` | **部品 371 個・重複 0・注釈警告なし** |
| `sch_import.py --roundtrip AudioV2/*.kicad_sch` | **全部 OK** |

イメージがあれば Docker(KiCad 10.0.6)、無ければホストの `kicad-cli` で動く。
出力は `out/`（gitignore 済み）。詳細は [docker/kicad-cloud-build/README.md](docker/kicad-cloud-build/README.md)。

### ブランチ

作業ブランチの正は **`main`**。マージ済みの `cursor/*` を checkout / PR base にしない。
