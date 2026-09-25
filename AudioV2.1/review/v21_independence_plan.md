# AudioV2.1 を v2・v1 から切り離す計画（読み取り専用の調査結果）

調査日 2026-09-25。対象ブランチ `claude/vibrant-cray-axng64`（HEAD `6f3cd7e`）、比較先 `origin/main`（`c6d3acc`）。
**この調査ではリポジトリのファイルを 1 つも変えていない。** 下の手順はすべて「これからやること」の案。

---

## 0. 要約

| 数えたもの | 件数 | 補足 |
|---|---:|---|
| `AudioV2.1/` の Markdown から v2.1 の外へ出るリンク | **142** | `AudioV2/DECISIONS.md` 99、`CLAUDE.md` 17、`SOURCE_OF_TRUTH.md` 13、`Audio/` 10、v1 の `Control/` 2、`.cursor/skills/` 1 |
| v2・v1 のパスを文字で書いている行（md・py・sch・pcb・sym・lib-table） | 382 | 削除する文書を除くと **約 223 行**（うち `review/DECISIONS_v21_draft.md` 49） |
| **設計データとしての実依存**（無いと道具が壊れるもの） | **5 系統** | ① `sym-lib-table` の 4 ライブラリ ② `fp-lib-table` の `Library.pretty` ③ `spice/extract_dut_thd.py` が `Audio/datasheets/opamps/` を読む ④ `scripts/amp_sel_hop.py` が `Audio/` を symlink ⑤ `scripts/sch_helpers.py` が `Audio/BP5293_ROHM.kicad_sym` を読む（ルート生成時だけ） |
| v2.1 が引いているのに `AudioV2.1/datasheets/` に無い DS | **19 本・約 24.7 MB** | `Audio/datasheets/opamps/*.pdf` 17 本（AD797 を含む）＋ `TMR9`・`TMR6`。ほかに v1 文書 3 本（在庫表・高速石の精査・opamps の README） |
| DECISIONS §7 の引き継ぎ項目 | **31**（書き直し文案は §4） | ほかに「監査で維持・図やコードが頼っているのに §7 に無い」もの **19**（§4.7） |
| 移行後に `AudioV2.1/` から消す文書 | **9 本 ＋ スクリプト 1**（`legacy/` 6 本は任意） | §7 |
| 回路図・PCB の文字列で v2・v1 文書を指すもの | ルート sch 5 行、pcb 1 行、sym 2 行、legacy 3 行 | §5.5 |
| main へ出すための巻き戻し | `AudioV2/NOW.md` 1 本と `Audio/*` 4 本 | §8 |

**いちばん大きい見落としは文書ではなくライブラリ表。** `AudioV2.1/sym-lib-table` と `fp-lib-table` は `${KIPRJMOD}/../Audio/…` を指していて、
v2.1 の回路図は `BP5293_ROHM`・`MeasurementADC1804`・`MeasurementADC_Extras` のシンボル（20 インスタンス）と、
`Library:` のフットプリント（PCB 上 7 種・10 個、図の Footprint 欄では MBC2596 を含む 8 種・27 箇所）を v1 の置き場から引いている。いまは図に埋め込まれているので開けるが、
「ライブラリから更新」・DRC の `lib_footprint_*`・生成スクリプトは v1 に依存したまま。

**現状の基準値（移行の前後で同じであることを確かめる）** — このセッションで実測:
`check_sexpr.py -q AudioV2.1` 13 ファイル・問題 0／`sch_import.py --roundtrip AudioV2.1/*.kicad_sch` 6 枚とも OK／
`gen_parts_bom.py --check` OK／`KICAD_BACKEND=local kicad-run.sh erc AudioV2.1/AudioV2Case.kicad_sch` 5 件（`ground_pin_not_ground` 2・`isolated_pin_label` 2・`multiple_net_names` 1）。kicad-cli 10.0.6。

---

## 1. 方針

1. **v2.1 が頼っている事実・決定は v2.1 の中に置く。** 置き方は 5 つだけ:
   (a) `DECISIONS.md` に v2.1 の決定として書き直す（理由と v2.1 内の出典つき）
   (b) `NOW.md` に現況として書く
   (c) `ds_facts/` に DS の事実として置く
   (d) ファイルを複写する（DS の PDF・KiCad ライブラリ・在庫表など、書き直す意味の無いもの）
   (e) 道具として共有のまま（下の表）
2. **置いたあと、v2・v1 の文書への参照を消す。** 「v2 の L1234」「v2 の DECISIONS」も消す（v2.1 の §7 を置き換えるので要らなくなる）。
3. **凍結した記録（`review/*.md`）は本文を書き換えない。** 出典キーの定義行だけを v2.1 の git 履歴（コミットとパス）に向け直す。
   履歴を指す書き方は「読まなくてよい。事実は本文に写してある」と明記する（§5.3）。
4. **v2（`AudioV2/`）と v1（`Audio/`）は変えない。** このブランチで入った `AudioV2/NOW.md` と `Audio/*` の変更は巻き戻して別 PR へ（§8）。
5. **main へマージできる形にする。** 移行後の `git diff --stat origin/main...HEAD` で `AudioV2.1/` の外に出るのは
   `.gitignore`（2 行）と `CLAUDE.md`（短い 1 ブロック）だけ。**`.cursor/rules/`・`.claude/agents/`・`SOURCE_OF_TRUTH.md` は触れない**ので、
   v2.1 用の指示は `AudioV2.1/` の中（入れ子の `CLAUDE.md` など）に置く（§9）。

### 1.1 共有のままにする道具（持ち込まない）

| 道具 | どこ | v2.1 からの使い方 | 備考 |
|---|---|---|---|
| S式の検査 | `Audio/scripts/check_sexpr.py` | `python3 Audio/scripts/check_sexpr.py -q AudioV2.1` | v2.1 の文書が書いているのはこのコマンドだけでよい |
| kicad-cli の起動 | `docker/kicad-cloud-build/kicad-run.sh` | 既定は v2 なので **`erc AudioV2.1/AudioV2Case.kicad_sch` と明示**。`gen_parts_bom.py` が内部で使う | 出力は `KICAD_OUT`（既定 `out/`） |
| KiCad 標準シンボル・フットプリント | ホストの KiCad | `sch_helpers.py` が自動探索 | |
| DigiKey の認証 | リポジトリ直下 `.secrets.env` | `digikey_search.py` / `dcdc_survey.py` | 秘密。中身は写さない |
| 計測ファーム（v1） | `Audio/measurement_fw/` | 実機のスペアナ・キャプチャ。**設計の根拠としては読まない**（根拠は `review/tap_facts.md` に写してある） | 使うときはユーザーに確認。v2.1 の文書にはパスを書かない |
| リポジトリ共通の方針 | `SOURCE_OF_TRUTH.md` | 原則（導出できる数値を書かない等）だけ使う。**そこから辿る `AudioV2/…` のリンクは読まない** | このブランチでは変えられない |

---

## 2. 依存の一覧

列: **何が** ／ **どこにある** ／ **v2.1 に要るか** ／ **持ってくる形** ／ **行き先**

### 2.1 KiCad ライブラリ（実依存。最優先）

| 何が | どこにある | 要るか | 持ってくる形 | 行き先 |
|---|---|---|---|---|
| `BP5293_ROHM` シンボル（ルートの 5 V バック 2 個） | `Audio/BP5293_ROHM.kicad_sym`（2.4 KB） | 要る | ファイルを複写。**ライブラリ名は `BP5293_ROHM` のまま** | `AudioV2.1/lib/BP5293_ROHM.kicad_sym` |
| `MeasurementADC1804`（`ADC1804_F_MODULE` 1・`OPA1656` 12） | `Audio/MeasurementADC1804.kicad_sym`（8.4 KB） | 要る | 複写・名前据え置き | `AudioV2.1/lib/MeasurementADC1804.kicad_sym` |
| `MeasurementADC_Extras`（ASFL1・LT1763-3.3/-5・TPS3307・XC8107・WAVESHARE・MBC2596 ほか） | `Audio/MeasurementADC_Extras.kicad_sym`（30.7 KB） | 要る | 複写・名前据え置き | `AudioV2.1/lib/MeasurementADC_Extras.kicad_sym` |
| `DKMW20` | `Audio/DKMW20.kicad_sym` | **要らない**（図に `lib_id` 0） | `sym-lib-table` から行を消す | — |
| フットプリント `Library:`（ADC1804_F・BP5293 SIP-3・ASFL・PPTC・REC20K・Cosland 2MD1/2MS1・MBC2596 ほか 16 種） | `Audio/Library.pretty`（464 KB） | 要る（PCB に 7 種・10 個、図の Footprint 欄に 27 箇所） | ディレクトリごと複写・**名前 `Library` 据え置き** | `AudioV2.1/lib/Library.pretty/` |
| `sym-lib-table` / `fp-lib-table` | `AudioV2.1/`（中身が `${KIPRJMOD}/../Audio/…`） | — | `uri` だけ `${KIPRJMOD}/lib/…` に書き換える | 同じファイル |

⚠ v2 の `AGENT_HANDOFF.md` §8 は「`Audio/*.kicad_sym` を AudioV2 へ複製する」を禁止にしている。これは **v2 の規則**で、v2.1 の独立（ユーザーの意図）とぶつかる。
v1 のライブラリは main で凍結されているので、複写しても中身がずれる心配は小さい。**複写でよいかはユーザーに一言確かめること。**
複写しない場合は「道具として共有」に分類し直し、`AudioV2.1/CLAUDE.md` に「ライブラリだけは `../Audio/` を読む」と書く。

### 2.2 データシート（§6 に一覧）

| 何が | どこにある | 要るか | 持ってくる形 | 行き先 |
|---|---|---|---|---|
| 手持ちオペアンプ 17 石の DS（`ds_facts/opamps.md`・`verify_opamps.md` が 79 箇所で引く。`rail_budget.py`・`spice/*` も） | `Audio/datasheets/opamps/*.pdf`（AD797 はこのブランチで追加） | 要る | 複写 | `AudioV2.1/datasheets/opamps/` |
| opamps の README（石と PDF の対応・MUSES03 の要点） | `Audio/datasheets/opamps/README.md` | 要る | 複写し、外向きリンク 3 本を直す | `AudioV2.1/datasheets/opamps/README.md` |
| Traco `TMR9` / `TMR6` | `Audio/datasheets/` | 要る（電源比較の査読 5 本が引く。`scripts/dcdc2/` の抽出テキストの元） | 複写 | `AudioV2.1/datasheets/` |
| `SKMW20_DKMW20_Datasheet.pdf`（`AudioV2.kicad_sym` の DKMW20 の Datasheet 欄） | `Audio/datasheets/` | 要らない（同じ内容が `MeanWell_SKMW20_DKMW20.pdf` として v2.1 にある。`cmp` で一致） | 欄を書き換える | — |
| `Recom_REC20K-Z_Rev3-2025.pdf`（Datasheet 欄が `AudioV2/datasheets/…`） | v2.1 にもある | — | 欄の `AudioV2/` を外す（RS6 へ替えるときに消える欄） | — |

### 2.3 v1（`Audio/`）の文書

| 何が | どこにある | 要るか | 持ってくる形 | 行き先 |
|---|---|---|---|---|
| 手持ちオペアンプの在庫（ユーザー申告） | `Audio/OPAMP_INVENTORY.md`（**このブランチの版**） | 要る（`ds_facts/opamps.md` の対象の定義、`pm12_judgement.md`、PARTS §4.2） | 複写。中の PDF リンクは同じディレクトリへ、`README.md`・`FAST` へのリンクは v2.1 側へ | `AudioV2.1/datasheets/opamps/INVENTORY.md` |
| 高速寄りオペアンプの DS 精査（高速娘の Cf・網・バイアス） | `Audio/OPAMP_FAST_DS_REVIEW.md`（**このブランチの版**） | 要る（NOW の「議論中」、V21-未決-18） | 複写。`AmpModule_OPAMP_REFINE.md`（v1）へのリンク 3 本は外す | `AudioV2.1/review/opamp_fast_ds_review.md` |
| v1 実機の測定記録（`MeasurementADC_BRINGUP.md`・`_STATUS.md`・`README.md`・`AudioCase.kicad_sch`・`measurement_fw/captures/`） | `Audio/` | 事実は要る。**事実は既に `review/tap_facts.md` に写してある** | 出典キーの定義行だけ git 履歴へ（§5.3）。複写しない | — |
| v1 の制御ファーム（`Control/relays.py` の SET/RESET 順、`Control/protocol.py` の I²C 速度） | リポジトリ直下 `Control/` | 順序だけ要る | DECISIONS §2-7・§6-2 に既にある。`firmware/amp_select.py:62` の TODO をそちらへ向ける | — |
| `Audio/Library.pretty/TEC3-1223_SIP8_THT.kicad_mod` | `Audio/` | 査読の記録にだけ出る | ライブラリを複写すれば v2.1 内で解決（パスを書き換え） | `AudioV2.1/lib/Library.pretty/` |
| `Audio/Controll.kicad_sch`・`split/AudioCase_4_amp.kicad_pcb`・`PowerModule_TEC3_REDESIGN.md` | `Audio/` | 要らない（PARTS・VOLUME_IC・CIRCUIT_DESIGN の履歴の文） | 行ごと削除（文書ごと消えるものが多い） | — |

### 2.4 v2（`AudioV2/`）の文書

| 何が | どこにある | 要るか | 持ってくる形 | 行き先 |
|---|---|---|---|---|
| v2 の決定ログ（リンク 99 本、「v2 Lnnn」「v2 の DECISIONS」） | `AudioV2/DECISIONS.md` | §7 の 31 項目と §4.7 の 19 項目は要る。残りは履歴 | **DECISIONS に書き直す**（§4）。§8 の表と §1〜6・§9・§10 の行番号は言葉に置き換える（§4.8） | `AudioV2.1/DECISIONS.md` |
| 同じもの（v2.1 の中の写し） | `AudioV2.1/AGENT_HANDOFF.md` ほか 8 本（§3） | 部分的に要る | 要る部分を DECISIONS／NOW／ds_facts に移してから**削除** | §3・§7 |
| 査読が引く「`AudioV2.1/DECISIONS.md` Lnnn」「`AudioV2.1/AGENT_HANDOFF.md` Lnnn」 | 当時の v2.1 は v2 の**バイト一致の写し**だった（`git show 5d2cd25:AudioV2.1/DECISIONS.md` が `AudioV2/DECISIONS.md` と一致することを確認） | 記録として要る | **`review/README.md` を 1 本足して、行番号の基準を「`5d2cd25` 時点の v2.1」と書く**（v2 のパスは出さない） | `AudioV2.1/review/README.md` |

### 2.5 スクリプト（§5.4 に行番号）

| 何が | どこにある | 要るか | 持ってくる形 | 行き先 |
|---|---|---|---|---|
| `spice/extract_dut_thd.py` の `DS = parents[2]/"Audio"/"datasheets"/"opamps"`（抽出モードで PDF を読む） | L50 | 要る | パスを `parents[1]/"datasheets"/"opamps"` に | 同じファイル |
| `scripts/amp_sel_hop.py` の `os.symlink(ROOT/"Audio", dest/"Audio")`（DRC 用の作業場所でライブラリを解決するため） | L854 | ライブラリを v2.1 に入れれば**要らない** | 行を消す（`AudioV2.1/` の中身は symlink で全部渡るので `lib/` も届く） | 同じファイル |
| `scripts/sch_helpers.py` `_read_symbol_text()` の BP5293 | L425 | ルート生成（止めてある）からしか呼ばれない | `ROOT/"lib"/"BP5293_ROHM.kicad_sym"` に | 同じファイル |
| `scripts/split_frontpanel.py` の Extras | L111 | 一回きりの済んだ移設スクリプト | `ROOT/"lib"/…` に（または削除候補） | 同じファイル |
| `scripts/generate_kicad_scaffold.py` の `AUDIO = ROOT.parent/"Audio"`、lib-table 文字列、`WIRING.md`・`README.md` を書き出す処理 | L18・876–888・1181–1245 | **回してはいけない**が、`build_daughter`・`build_motherboard`・`wire_circuit_design` ほか 7 本が import する | 消さない。パス文字列だけ `${KIPRJMOD}/lib/…` に揃える（grep を通すため） | 同じファイル |
| `scripts/rail_budget.py` の出典文字列（v2 の DECISIONS 3 か所・`Audio/datasheets/opamps` 3 か所） | L31–49 | 要る（出力に載る） | §4 の v2.1 項目・`datasheets/opamps/` へ。L7809 の Iq は `ds_facts/power.md` §5（`ST_L78.pdf`、v2.1 にある）で裏が取れるか確かめ直す | 同じファイル |
| `scripts/build_daughter.py` L357 のコメント「v2 の DECISIONS『TMUX7612 に 1 µF…』」 | L357 | 要る（§4.7 の G1） | DECISIONS の新項目へ | 同じファイル |
| `scripts/wire_circuit_design.py` L662 の図の注記文字列「v2 の DECISIONS manual volume」、L2・1244・1294 の `AGENT_HANDOFF` | — | 生成物の注記。回路には効かない | 「DECISIONS 継-02」等へ | 同じファイル |
| `scripts/dcdc_survey.py` L4・`digikey_search.py` L4・`sch_helpers.py` L403・`amp_sel_hop.py` L4 の docstring が `AGENT_HANDOFF`／`AMP_SEL_ROUTING_HANDOFF` を引く | — | 理由の説明だけ | docstring を DECISIONS §7 の項目へ | 同じファイル |
| `scripts/dest_ladder_sim.py` | — | **要らない**（位置センスラダーは廃止） | 削除（`DEST_SENSE_LADDER.md` と一緒） | — |
| `scripts/build_motherboard.py` と `legacy/*.kicad_sch` | — | `build_daughter.py` が `SLOT_*_NETS`・`_merge_lib_symbols`・`ROOT_PATH` を import するので **スクリプトは残す**。`legacy/` は `build()`（安全弁で止めてある）と `--dry-run` だけが読む | `legacy/` は任意で削除（§7.2） | — |

### 2.6 回路図・PCB の文字列（§5.5 に行番号）

| 何が | 要るか | 持ってくる形 |
|---|---|---|
| ルートの Description「（v2 の DECISIONS）」3 か所（HP 出力の DC ブロック、BSS138、I²C レベルシフタの注記） | 理由は要る | 「DECISIONS 継-05」「継-03」へ。**直したら `gen_parts_bom.py` で PARTS を作り直して同じコミットに入れる**（生成ブロックに Description が載る） |
| ルートの注記「AudioV2 PowerModule — label-wired (§9 / CIRCUIT_DESIGN §4)」 | 要らない | 「(§9 / CIRCUIT_DESIGN §4)」を外す |
| Datasheet 欄 `AudioV2/datasheets/Recom_REC20K-Z_Rev3-2025.pdf`（sch 2・pcb 1・sym 1・legacy 2） | — | `datasheets/…` に（RS6 へ替える作業で消えるなら、そのとき一緒に） |
| 「v1 C901」「v1 と同じ AZ850P2-5」など v1 の由来注記（ルート 14・MeasureControl 5・AmpBankRelay 4） | 文書への参照ではない | **任意**。残すなら由来として無害。消すなら部品の役目だけにする |

### 2.7 エージェント向けの設定（このブランチでは直せないもの）

| 何が | 何を読ませてしまうか | 対処（`AudioV2.1/**` と `CLAUDE.md` の中だけで） |
|---|---|---|
| `CLAUDE.md`「最初に読むもの」「期待値」表 | `AudioV2/NOW.md`・`AGENT_HANDOFF.md`、v2 の期待値 | ルートに短い 1 ブロック（§9.1）。v2.1 の期待値は `AudioV2.1/CLAUDE.md`（§9.2） |
| `SOURCE_OF_TRUTH.md` L8–9・60–75 | `AudioV2/AGENT_HANDOFF.md §2.8`・`AudioV2/NOW.md` | `AudioV2.1/CLAUDE.md` に「原則は使う、リンクは辿らない、v2.1 での置き場はこれ」 |
| `.cursor/rules/work-on-main.mdc`（alwaysApply）・`source-of-truth.mdc`（alwaysApply） | `AudioV2/NOW.md` から再開せよ | `AudioV2.1/.cursor/rules/v21-context.mdc`（入れ子のルール。**Cursor 側で効くかは要確認**） |
| `.claude/agents/sch-review.md`・`.claude/commands/sch-review.md` | 対象 `AudioV2/*.kicad_sch`、読む表に v2 の NOW/DECISIONS/HANDOFF/datasheets/legacy | v2.1 で査読を投げるときは「対象は AudioV2.1、`sch_facts.py --root AudioV2.1/AudioV2Case.kicad_sch`、`AudioV2/`・`Audio/` の文書は読まない、決定は `AudioV2.1/DECISIONS.md`」を必ず渡す（`AudioV2.1/CLAUDE.md` に定型文） |
| `.cursor/skills/audiov2-pcb-layout/SKILL.md` | `AMP_SEL_ROUTING_HANDOFF.md` が引く v2 の配線スキル | 道具として共有扱い。v2.1 の文書からリンクしない |

---

## 3. `AudioV2.1/` にある v2 の写し — 何を残し何を捨てるか

v2 と比べた差分行数は `diff AudioV2/<f> AudioV2.1/<f>`（0 はバイト一致）。

| 文書 | 差分 | v2.1 がまだ頼っている部分 | 純粋な v2 の履歴 | 処置 |
|---|---:|---|---|---|
| `AGENT_HANDOFF.md`（1888 行） | 88（リンクの向け直しだけ） | L220「大前提: いまの実測の絶対値で設計判断をしない」（使ってよいもの／いけないもの・順序）→ §4.7 G11。§2.3「基板外へ電源を出すときは +V と戻りを同じケーブルに」→ G12。§2.4 手持ち石 → 在庫表の複写。§2.8 所有権 → 既に CLAUDE.md。§8「触ってよい／だめ」→ `AudioV2.1/CLAUDE.md` | §1〜§2.2・§2.5〜2.7・§2.9〜2.10・§3〜§7・§9（RelayBoard・AmpModule・REC10K 選定・PR・タイムライン・再開プロンプト） | 3 点を移して**削除** |
| `AMP_SEL_ROUTING_HANDOFF.md`（67 行） | 2 | 「やってみて分かったこと」（無検査の F→B 載せ替えは不可 ほか）。娘の PCB は v2.1 でコネクタ 2×12・リレー追加で引き直しになるが、教訓は残る | 09-24 時点の残件 2 点（NOW に済みと書いてある） | 教訓を NOW の PCB 節へ 3〜5 行で移して**削除**。`scripts/amp_sel_hop.py` L4 の docstring も直す |
| `CIRCUIT_DESIGN.md`（205 行） | 6 | §2 PT2314E の外付け網（`BOUT`/`BIN` を 100 nF で 1 点・5.6 k で GND）→ G10。§0 シンボル方針（標準 lib 優先・カスタムは `AudioV2.kicad_sym`）→ `AudioV2.1/CLAUDE.md` | §3 DEST ラダー、§4 PowerModule 値、RelayBoard・AmpModule（廃止）、§7〜8 チェックリスト | **削除**（ピン照合は図と `ds_facts/switch_control.md` が正） |
| `WIRING.md`（118 行） | 12 | 「ポット・行き先スイッチ・入出力ジャックはパネル実装でリード（XH）戻し」、「シールドは受け側 1 か所の `A_GND` だけに落とす」「PD_GND と A_GND を束ねない」→ G13 | 本文は冒頭で自ら「旧構成（4 枚）の記録」。基板構成・I²C 4P・v1 流用基板 | **削除** |
| `VOLUME_IC_COMPARISON.md`（275 行） | 16 | 音量 IC を採らない理由（→ 継-02 に吸収） | 全体が 2026-08-30 のアーカイブ（MCP45HV51 vs PGA231x） | **削除** |
| `DEST_SENSE_LADDER.md`（69 行） | 0 | なし（ラダーは廃止。`DEST_ADC` は v2.1 で LM4040 の比率校正に使う＝DECISIONS §5-2） | 全部 | **削除**＋`scripts/dest_ladder_sim.py` も |
| `SYMBOL_FIX_TODO.md`（104 行） | 0 | なし | 2026-08-30 の作業指示 WP-A〜D | **削除** |
| `SYMBOL_REVIEW_SUMMARY.md`（99 行） | 0 | なし | 2026-08-30 の査読要約 | **削除** |
| `README.md`（51 行） | 0 | 冒頭 2 段落（装置の目的）だけ | 「PCB は未着手」「娘基板 2 版を混ぜて比べる」は v2.1 では誤り。表の半分は消える文書 | **書き直し**（10 行ほど。入口は NOW／決定は DECISIONS／DS 事実は ds_facts／査読は review／道具は scripts。v2・v1 に触れない） |
| `PARTS.md`（495 行） | 44 | §0a（繋ぐもの: HD 560S 120 Ω・Cloud III 64 Ω・iLoud、32 Ω 級は無い）、§0b（ベンダのデータの罠）、§0c（PRECISION／MATCH／SPEC）、§2.2（ポット Alps RK27112A00CF）、§2.3 のうち DIP-28 ソケット・PT2314E・一次ヒューズ（F2A 速断・ホルダ Schurter OGN）・PPTC（RXEF 系）・PD の供給元、§4.2（DIP-8 差し替えの条件）。**生成ブロック（`case-bom`・`ampchannel-bom`）は回路図の写しなので、図を直して作り直す** | §0 の表（SW_DEST 3 極 ON-OFF-ON・REC10K・OLED）、§1 表示（OLED は廃止）、§2.1 C&K 7303（Cosland 2MD1 に替わった）、§2.3 の DC-DC 行（REC10K）と J_I2C 行、§4.3 MCU、§5、変更履歴 | **書き直し**（v2.1 の品番表として。§0b の根拠リンク `AGENT_HANDOFF §2.10` は外し、罠の本文だけ残す） |
| `datasheets/README.md`（225 行） | 12 | 表の DS の対応（どの PDF が何の部品か） | 「AudioV2 予定部品」「PowerModule 再設計」「OLED」「`Audio/` 流用・複製しない」L200–203・L217 | **書き直し**（v2 DECISIONS へのリンク 4 本を外す。L200–203 の「opamps は `Audio/` が正」を「`opamps/` にある」へ） |
| `firmware/README.md`（50 行） | 0 | 方針表（ENC×3・LCD・100 kHz・Switch SEL の起動） | 「v1 の `Control/`・`Audio/measurement_fw/` は参照用」、`cd AudioV2/firmware`（パス誤り）、娘番地 6 段・Switch/Relay 共通 API（v2.1 は 1 種類・未決-03） | **書き直し**（v2.1 の §6 ファームの責務を指す） |
| `legacy/README.md`・`README_ampbank.md` | 0 | なし（v2.1 のルートは手編集所有で、`legacy/` から再生成しない） | 全部 | `legacy/` を消すなら一緒に（§7.2） |
| `spice/README.md`（698 行） | 4 | 切替素子・入力トポロジの解析の前提と結果（DECISIONS が `spice/stack_relay/` を引く） | v2 の構成（10 ch・常時通電）での判定文 | **残す**。v2 パス 10 行を v2.1 内へ（`AudioV2/spice/…` → `spice/…`、DS → `datasheets/…`）。§11.1 を引く 2 行は DECISIONS の該当項目へ |
| `NOW.md`（241 行） | 62 | 冒頭〜「次にやること」、装置、UI、図と PCB の現況（**v2.1 のファイルは写しなので、書かれた PCB・図の状態は v2.1 の現況でもある**） | 「電源（v2 の記録）」「次に手を動かすなら（v2 から引き継いだ表）」「2026-09-07〜09 に閉じたもの」 | **短く差し替え**（§5.1） |

---

## 4. DECISIONS §7 の書き直し文案

形: **決定**／**理由**／**出典**（v2.1 の中のファイルか、複写した DS）。v2 へのリンクは書かない。
ID は `V21-継-nn` を提案（§10 の `V21-未決-nn`・`V21-実測-nn` と同じ流儀）。**状態**はどれも「決定（v2 から引き継ぎ、v2.1 で見直していない）」。
差し替えるのは `DECISIONS.md` L576–620（§7 全体）。

### 4.1 UI・操作

- **V21-継-01 エンコーダ ×3（CH / BASS / TREBLE）** — 決定: EC11 系・押し SW 付き ×3。回して候補、押して確定。CH の確定で入るのは入力切替と ch LDO の EN（§2-8）。
  理由: 操作は v2.1 で変えない（ユーザー）。音量と DEST は物理操作子なのでエンコーダに載せない。
  出典: `FrontPanel.kicad_sch`（ENC）、`datasheets/RotaryEncoder_EC11_generic.md`。
- **V21-継-02 音量は Amp の後の手回し A50k デュアル ×2（HP / LINE 独立）。IC にしない** — 決定: PGA2310・digipot は信号経路に入れない。音量は LCD に出さない。ポットは Alps RK27112A00CF 級で、本体はユニバーサル基板から XH 6P で FrontPanel へ。
  理由: 遠隔操作が要らないので音量 IC を入れる理由が無い（UI・コスト・SNR）。「±5 V で振幅が足りない」は振幅の上限の話で、専用電源を足しても解けない。
  出典: `FrontPanel.kicad_sch`、`datasheets/TI_PGA2310.pdf`（却下した側）、`PARTS.md` §2.2。
- **V21-継-03 出力段: PHONE はユニティバッファ、LINE はポット直出し、ゲインは付けない** — 決定: HP は OPA1652（DIP-8 ソケット、10 Ω＋470 µF NP）、LINE はバッファ無し。バッファは全 ch に共通に掛かるので **1 回の比較の中では差し替えない**。
  理由: ワイパー（最大 12.5 kΩ）では 64〜120 Ω を駆動できない。LINE の相手はアクティブスピーカー。つなぐ実機 2 機種（HD 560S 120 Ω・Cloud III 64 Ω）では出力は足りないのでなく過剰で、ゲインを足すとポットの使用域が下端に寄る。LINE もバッファするなら石がもう 1 個要る（共用はできない）。
  出典: `ds_facts/opamps.md` §8（OPA1652 出力 ±30 mA、p1）、`datasheets/opamps/TI_OPA1652.pdf`、`PARTS.md` §0a。
- **V21-継-04 DEST は機械スイッチ。リレーは使わない** — 決定: DPDT ON–ON 1 本で PHONE↔LINE。MUTE 位置と位置センスのラダーは無い（電源断は PWR SW）。
  理由: 出口はユーザーが手で選ぶもので、ファームが知る必要が無い。音声経路の接点が増えない。
  出典: `FrontPanel.kicad_sch`（Cosland 2MD1）。
  注: v2 の記録にある「3PDT ON-OFF-ON＋抵抗ラダー」は v2 の中で既に古い。
- **V21-継-05 トーンは PT2314E。`DGND` はチップの足元で `A_GND`。I²C 境界は BSS138 ×2** — 決定: Bass/Treble だけ使い、音量は 0 dB 固定。ch 選択の前に置き、全 ch に配る。PT 側のプルアップは 10 k → `VCC_TONE`（9 V）。
  理由: 無印 PT2314 は買えない（E はピン・外付け網とも同じ）。PT2314E の VIH min 3.0 V に 3.3 V のプルアップでは余裕 0.3 V しか無い。P82B96 は Sx 側の VOL 0.8〜1.0 V が PT2314E の VIL max 1.0 V・RP2350 の VIL 0.8 V を食い切る。
  出典: `ds_facts/switch_control.md`（PT2314E の VIL/VIH、p12）、`datasheets/Princeton_PT2314E.pdf`、`datasheets/RaspberryPi_RP2350.pdf`。
  ⚠ P82B96 の DS はリポジトリに無い。§10-1 の「DS を取るもの」に足すか、「v2 で DS を読んで決めた値」と書く。
- **V21-継-06 HP の固定パッドは付けない（0 Ω）。DNP で後から付けられる足場** — 理由: ソケットは ±12 V（§3-3）で Amp の最大は約 6.5〜7 Vrms。固定 −20 dB は過剰。出典: ルート回路図の HP 経路。

### 4.2 計測（Q1 の土台）

- **V21-継-07 計測タップの「+」側にユニティバッファ（OPA1656、入力 100 k → `A_GND`）** — 理由: 無いとバスから見た負荷が 1.87 kΩ になり、TMUX7612 の H3 が悪くなる。バッファで約 30 kΩ。
  出典: `MeasureControl.kicad_sch`、`ds_facts/tap.md`、`review/tap_facts.md`、`datasheets/opamps/TI_OPA1656.pdf`。
- **V21-継-08 ADC 前段の入力抵抗 6.19 k（0.1 %）** — 決定: PT2314E 経路についての値。理由: PT2314E の VOMAX typ 2.6 Vrms × Amp ゲイン 2 ＝ 5.2 Vrms を ADC のフルスケール（バス換算 5.47 Vrms）に入れる。LPF の極は変えない。DIRECT の振幅は V21-未決-14。
  出典: `ds_facts/switch_control.md`（PT2314E VOMAX）、`datasheets/TI_PCM1804.pdf`、`MeasureControl.kicad_sch`。
- **V21-継-09 `MCLK_SENSE` は無い（GP9 は no_connect）** — 理由: ファームが読んでいない。12.288 MHz が `ADC_GND`→`A_GND`→`D_GND` を渡る経路が一本減る。出典: `MeasureControl.kicad_sch`、`firmware/board.py`。

### 4.3 部品選定の理屈

- **V21-継-10 2.2 µF の出力フィルムは公差でなく耐圧で選ぶ** — 決定: 50 V 級・±10 % で足りる。耐圧を上げない。ch 間の揃いは LCR 選別（`PARTS.md` §0c MATCH）。
  理由: 信号 ±13 Vpk に 50 V で約 4 倍の余裕。フィルムの体積は概ね C×V で、耐圧を上げると基板に入らない。公差の生む ch 間差は f0 付近（約 1.8 Hz）の話で可聴帯に効かない。
  出典: `PARTS.md` §0c、図のフットプリント（B32529・P5）。
- **V21-継-11 受動部品の型番は回路が固まってから DigiKey API でまとめて選ぶ（カップリング C とゲイン R は一緒に）** — API の入手性の欄は信用せず `ProductUrl` を開く。出典: `scripts/digikey_search.py`、`PARTS.md` §0b。
- **V21-継-12 DIP-28 ソケットは 0.300"・板バネ型** — 挿さるのは MCP23017 だけで、I²C のデジタル。娘の MCP を残すかは V21-未決-03。出典: 図のフットプリント `DIP-28_W7.62mm`。
- **V21-継-13 却下のまま（理由は v2.1 でも成り立つ）**
  - 固定 6 V の三端子（7806 級）— `LT1763-5` の実負荷の規定は 6 V < VIN（`ds_facts/power.md` LT1763、`datasheets/ADI_LT1763.pdf` p4）
  - Aimtec AM10TW / AM15CW — 絶縁容量 2000 pF、DigiKey では Marketplace 出品（`datasheets/Aimtec_*.pdf`）
  - TDK-Lambda CCG — OVP なし・RC 負論理・絶縁容量が非公表（`datasheets/TDK-Lambda_CCG15-30.pdf`）／CUI PYBE10 — NFND、50 % 未満で周波数を下げる（`datasheets/CUI_PYBE10.pdf`）
  - Mornsun URA — DigiKey の品が全数 NFND（2026-09-05 に API で確認）
  - MeanWell NSD10-12D12 — 2″×1″ で新しいフットプリント、最小負荷 20 mA/レール（`datasheets/MeanWell_NSD10-D.pdf`）
  - 入力ヒューズ T3.15 A — PD の故障電流の範囲で切れず、保護にならない（今のヒューズの見直しは V21-未決-16）

### 4.4 回路の原則

- **V21-継-14 電源を切った石は出力も切る** — 理由: オペアンプの出力は電源が無くても ESD／基板ダイオードでレールにつながる。§2-8 の前提。出典: `ds_facts/opamps.md`（入力・出力の保護の記述）、`review/arch_zero_base_review.md`。
- **V21-継-15 電源を切るなら入力も切る** — 理由: 電源 0 V の石の入力保護が ±0.6 V でクランプし、1 µF 越しに数十 mA 流れる。出典: `ds_facts/opamps.md`（入力保護 ≤ 10 mA、〔照合で追加〕の行）。
- **V21-継-16 境目のアナログスイッチは、バスにつながっている間は通電しておく** — 選んでいない娘の TMUX は電源ごと落とし、境目のリレーで切る（§2-1・§2-8）。理由: 電源の落ちたスイッチは自分のピンでバスをクランプする。出典: `ds_facts/boundary.md` §1.1（"Pins are diode-clamped to the power-supply rails."）。
- **V21-継-17 出力側のスイッチは 47 Ω の出力抵抗の後ろ** — 理由: OFF 側の容量を 47 Ω が隔離する（極は 12 MHz 以上）。追加の直列抵抗は要らない。
- **V21-継-18 break-before-make はファームで担保する（全 OFF → 待つ → 目標 ON）** — 理由: IC の BBM は同じパッケージで D を束ねたときだけ効く。§6-2 と同じ。出典: `ds_facts/switch_control.md`（TMUX7612）。
- **V21-継-19 グランドは木。結合は系統ごとに 1 か所、2 か所目は閉路。同居は結合ではない** — 同じシート・同じ基板に `A_GND` と `D_GND` があってもネットは別。パネルへ戻すリードで `A_GND` と `D_GND` を束ねない・並走させない。回路図が決めるのはループの有無だけで、帰路の実際は銅箔とハーネス。出典: 図の NetTie（`NT101`・`NT1601`〜`NT1603`）、`review/adc_gnd_retree.md`。
- **V21-継-20 シャーシは 1 点で落とす**（2 点だとシャーシ経由のループ）。落とす先は V21-未決-15。
- **V21-継-21 I²S とクロック** — 効く順: `ADC_GND` の帰路を短く（銅箔）→ I²S 3 本に直列ダンパ（足場は V21-未決-10）→ 測定中に LCD を電源ごと切れること（ロードスイッチはある）→ Pico の電源を静かにする（効きは小さい）。Pico は ADC と同じ基板に置き、基板の境目は遅い信号（I²C）のところにする。デジタル基板をアナログに密着させるとクロック結合が増える方向（`fs/64` 系列は BCK 由来）。BCK は 3.072 MHz（§9-12）。出典: `review/tap_facts.md`、`review/tap_compare.md`。
- **V21-継-22 基板間はワイヤでなくヘッダのスタック。DIP ソケットに手が届くこと** — 理由: 接点と線材を減らす方向が効く。この装置の目的はオペアンプの差し替えなので、ソケットへの手の届きは最大の制約（縦積みでの確認は V21-未決-20）。
- **V21-継-23 ヘッダの挿抜寿命は制約にしない** — 抜き差しは組み立てと保守のときだけ。電流は縦積みで突入 0.68 A・コイル 560 mA のパルスが加わるので品番の DS で確かめる（`review/stack_relay_power.md` §7.3）。接触抵抗は値ではなく非線形性が論点。

### 4.5 道具・手順の警告

- **V21-継-24 DC-DC は同じ仕様でも絶縁容量が桁で違う。サフィックス 1 つで変わる** — 例: Recom RS-1215D の無印と /H3、XP の ITP と ITU。絶縁容量の測定条件はメーカーごとに揃っていないので横並びで比べない。出典: `datasheets/` の各 DC-DC の DS。
- **V21-継-25 レール容量は `scripts/sch_facts.py rails` でそのつど数える。数値を文書に書かない** — `J201` の先（基板の外）に注意。計測側にはデカップ以外の電解がある。
- **V21-継-26 DC-DC の表の Fsw 欄で候補を比べない** — 見出しの条件が full load で、値は Max 列のことが多い。RS6 の読みは §9-2。
- **V21-継-27 同じ前提を渡した並列の結論の一致は、独立の裏付けにならない** — 探索範囲の指定そのものが盲点になる。否定側査読には前提を壊しに行かせる。
- **V21-継-28 「USB で 23 dB」を DC-DC 不要の論拠にしない** — 23 dB は正常構成とグランド基準を失った故障構成の差で、再現は 2.9 dB。判定は閾値（床・実用律速）に対して何 dB 下かで行う。出典: `review/tap_facts.md`（L258 の項）。
- **V21-継-29 参照番号は実物を列挙して空きを確かめる（最大値＋1 で採らない）** — マルチユニット部品は `(unit N)` で区別する。PPTC の下流には `PWR_FLAG`。
- **V21-継-30 買ったことを採用の根拠にしない** — MCP23017・DIP-28 ソケット・NJM7809 は在庫として持っているだけ。
- **V21-継-31 TMUX7612 の DS は表を取り違えやすい** — ±15 V の表（§5.7、p7）と ±20 V の表（§5.9、p10）が別。平坦度の条件は VS ±10 V。出典: `datasheets/TI_TMUX7612.pdf`、`ds_facts/switch_control.md`。

### 4.6 §7 の前置きの書き直し

L578「本文は v2 のまま。行番号は [../AudioV2/DECISIONS.md]…」を次に置き換える:

> v2 から引き継いだ決定。v2.1 で個別に見直していないものは状態を「引き継ぎ」とする。
> どれを引き継ぐかは棚卸し（`review/decisions_audit_1〜3.md` とそれぞれの `_review`）の「維持」から選んだ。
> 棚卸しの行番号は `review/README.md` の基準（`5d2cd25` 時点の v2.1）で読む。

### 4.7 §7 に無いが、監査で「維持」で、図やコードが頼っているもの（追加するか要判断）

| # | 中身（決定／理由） | 誰が頼っているか | 出典にできる v2.1 の中のもの |
|---|---|---|---|
| G1 | TMUX7612 に 0.1 µF と 1 µF（DS p34 のメーカー推奨）。Figure 5-19 の 27〜31 dB は「0.1 µF あり 対 無し」の差なので根拠にしない | `scripts/build_daughter.py` L357、図 | `datasheets/TI_TMUX7612.pdf`、`ds_facts/switch_control.md` |
| G2 | ADC 系の電流は ≤ 84 mA max／約 59 mA typ（PCM1804 VCC 45＋VDD 20＋発振器 15） | `scripts/rail_budget.py` `ADC_TOTAL`、DECISIONS §4 | `ds_facts/switch_control.md` §6、`datasheets/Abracon_ASFL1.pdf` |
| G3 | ソケット 1 個あたりの最悪 Icc は在庫の MUSES03 変換基板 20 mA（10 mA max ×2） | `rail_budget.py` `SOCKET` | `ds_facts/opamps.md` §16、`datasheets/opamps/NJR_MUSES03.pdf` |
| G4 | L7809 の Iq（今は「一次 DS 未入手・web 由来」と書いてある） | `rail_budget.py` `SUBRAIL` | `ds_facts/power.md` §5（`ST_L78.pdf` は v2.1 にある）。**この注記は古い可能性が高い** |
| G5 | PD は外付けモジュール、板上は受け端子。電源の UI はパワースイッチ＋12 V LED | 図 | 図 |
| G6 | 主系だけガラス管（ハードに開放する・ホルダで交換）、小系は PPTC（自己復帰）。PPTC は Littelfuse RXEF 系、ホルダは Schurter OGN | 図・PARTS | `PARTS.md` §2.3（書き直し後） |
| G7 | リレーは AZ850P2-5。接点 3/8・4/7、2/9 開放、コイル 5/6。**外形が同じ TQ2-L2 は COM/NC/NO の番号が違うので挿さない**（SET/RESET の意味が反転） | 図の Description、§2-2 | `datasheets/Zettler_AZ850.pdf`、`ds_facts/relay4.md` |
| G8 | BP5293 のフットプリントの穴は DS 推奨の Ø0.9（「DS 1.2」は外形注記の誤読） | フットプリント | `datasheets/ROHM_BP5293-xx.pdf` |
| G9 | 入力 1 µF・出力 2.2 µF のフィルムは TDK B32529 系 P5（PET）＋ LCR 選別 | 図・PARTS §0c | `PARTS.md` §0c |
| G10 | PT2314E: 外付け網（`BOUT`/`BIN` を 100 nF で 1 点・5.6 k で GND）、未使用入力は no_connect、電源投入後 50 ms は I²C を送らない（§6-2 に既出） | 図・ファーム | `datasheets/Princeton_PT2314E.pdf`、`ds_facts/switch_control.md` |
| G11 | 仮組みの測定の絶対値で設計判断をしない（手法と罠は使う、絶対値は使わない。配線とケーシングを先に） | 査読の読み方全般 | 本文そのもの（v2.1 のルールとして） |
| G12 | 基板の外へ電源を出すときは +V と戻りを同じケーブルに入れ、戻りを他所で幹線に結ばない | ケーブル | 同上 |
| G13 | ポット・DEST・入出力ジャックはパネル実装で XH で戻す。ケーブルのシールドは受け側 1 か所の `A_GND` にだけ落とす | 箱配線 | 同上 |
| G14 | XH ごとに GND を混ぜない（`A_GND` は音声 XH、`D_GND` はデジ XH、`PD_GND` は電源 XH） | FrontPanel・ルート | 図（NOW の PCB 節にもある） |
| G15 | ベタ GND は 1 枚にしない。系統ごとに別ゾーン（NetTie の星が全部バイパスされる） | PCB | NOW |
| G16 | 娘のコネクタ規則（pin1 のローカル X、南北の辺、キーイング、M3 四隅・端から 5 mm）は v2.1 でも維持（本数は §2-5 の 2×12） | PCB・`build_daughter.py` | `place_a2_slot_connectors.py` |
| G17 | PD は安定化電源なので UVLO に向かって沈まない。UVLO の余裕は 1.3 倍で足りる（RS6 の UVLO ON 9 V は typ、§9-4） | §3-2 | `ds_facts/power.md` |
| G18 | 入力 220 kΩ の撤去の理由・再導入は未決-13 に既出 | — | — |
| G19 | 実機の Pico は既定で LCD スペアナ版の `main.py`。測定用に差し替えたら戻す | 実機運用 | `firmware/README.md`（書き直し後） |

### 4.8 §7 以外に残る v2 の行番号（言葉に置き換える）

| 行 | 今 | 置き換え |
|---|---|---|
| L3–4・L9 | 「v2 の決定ログは ../AudioV2/DECISIONS.md」「v2 の行番号と見出しの語で示す」 | 「v2 から引き継いだものは §7、成り立たないものは §8。v2 の本文は引かない」 |
| L23・L24 | 0-2 の `../CLAUDE.md`・「v2 L28 決定ログ『切替方式』」 | 「v2 は全ソケット常時通電・入力ブロードキャストだった」だけ |
| L63・L71・L90・L97・L195・L196・L246・L251・L263・L273・L274・L281・L376・L398・L400・L407・L460・L461・L570・L672・L739 | 「v2 Lnnn『見出し』」 | 対応する `V21-継-nn`（あれば）か、括弧の中身を言葉で（例: L196 →「電源を切った石の出力も ESD でレールにつながる（継-14）」、L251 →「NFND（継-13）」、L739 →「DIP ソケットへ手が届くこと（継-22）」） |
| §8 の表の左列（28 行） | 「L28 決定ログ『切替方式』」など | 「v2 でそうしていたこと」を 1 句で（例「全ソケット常時通電・入力ブロードキャスト」）。行番号は消す |
| §9 #12 | 「（v2 L3375、L3369…の表の行）」 | 「v2 の記録の表」 |
| `[NOW] Lnn` | `a63caac` の NOW.md の行 | v2.1 の履歴なので残してよい |

---

## 5. 参照の書き換え一覧（file:line）

削除する文書（§7）の中の参照は数えていない。

### 5.1 `NOW.md`

| 行 | 今 | 処置 |
|---|---|---|
| 4 | 「v2.1 は v2（`AudioV2/`）の全コピー」 | 「2026-09-25 に v2 の図を写して始めた」だけ（パスを書かない） |
| 112 | `../Audio/OPAMP_FAST_DS_REVIEW.md` | `review/opamp_fast_ds_review.md` |
| 146–194「電源（v2 の記録）」 | REC20K・U1604・ADC の PPTC・Ciso、v2 DECISIONS へのリンク 5 本（148・156・163・167・187） | **現図の事実**（今の図は REC20K・F2A・PPTC 3 個で、RS6 等へ替える予定）だけ 3〜4 行に。理由は DECISIONS §3・§4・§8 と継-05 |
| 209–227「次に手を動かすなら（v2 から引き継いだ表）」 | B5・v1 との同一性 | 削除。AZ850 の行は G7、ヒューズの行は G6 へ |
| 218・228–241「閉じたもの」 | `../AudioV2/DECISIONS.md` | 削除（履歴） |
| 133 付近 | `firmware/amp_select.py` の説明の「（v2。v2.1 では…）」 | v2.1 の形だけに |

### 5.2 `DECISIONS.md` — §4.6・§4.8 のとおり（L3・4・9・23・24・63・71・90・97・195・196・246・251・263・273・274・281・376・398・400・407・460・461・570・578・672・739 と §8 の表）

### 5.3 `review/` と `ds_facts/`（凍結した記録。定義行と DS のパスだけ直す）

**まず `review/README.md` を新設**（数行）:
- 「この下の査読・監査が引く `AudioV2.1/DECISIONS.md` の行番号は `git show 5d2cd25:AudioV2.1/DECISIONS.md`、`AudioV2.1/AGENT_HANDOFF.md` は `git show 5d2cd25:AudioV2.1/AGENT_HANDOFF.md` の行。**読まなくてよい。v2.1 の決定の正は `../DECISIONS.md`**」
- 「v1 の測定記録の事実は `tap_facts.md` に写してある。出典キー [BU] 等は `git show 6f3cd7e:Audio/…`（凍結）」

| file:line | 今 | 書き換え |
|---|---|---|
| `ds_facts/opamps.md:6` | 「対象: `Audio/OPAMP_INVENTORY.md` の手持ちリスト…DS は `Audio/datasheets/opamps/`」 | 「対象: `../datasheets/opamps/INVENTORY.md`…DS は `../datasheets/opamps/`」（本文の 62 箇所は PDF の素の名前なので直さなくてよい） |
| `ds_facts/verify_opamps.md:5` | 「DS: `Audio/datasheets/opamps/*.pdf`」 | `AudioV2.1/datasheets/opamps/*.pdf` |
| `ds_facts/verify_boundary.md:5` | 「（`AudioV2/datasheets/` にも同名のものがある）」 | 括弧ごと削除 |
| `review/tap_facts.md:7・9・10` | 出典キーの定義（`Audio/AudioCase.kicad_sch`、[DEC]/[HO] = `AudioV2.1/…`、[BU] = `Audio/MeasurementADC_BRINGUP.md`） | 定義行だけ `review/README.md` の基準へ。**本文の [BU:行] 等はそのまま** |
| `review/tap_facts.md:128・149・151・154・155・160・166・168・174・187・209・222・261・286` | `Audio/…` のパス | 128 は `datasheets/opamps/TI_OPA1656.pdf`。他は「v1 の …（`review/README.md` の基準）」 |
| `review/tap_compare.md:18・55・291` | BRINGUP・`capture_raw.py`・OPA1656 の PDF | 18・55 → `tap_facts.md` の該当節、291 → `datasheets/opamps/TI_OPA1656.pdf` |
| `review/tap_compare_review.md:8・34` | BRINGUP・`i2s_rx.py` | 同上 |
| `review/rejected_review.md:10・144` | `Audio/datasheets/TMR9_Datasheet.pdf`・`TMR6` | `datasheets/TMR9_Datasheet.pdf`・`TMR6` |
| `review/rejected_review_review.md:7・8・9` | TMR9・TMR6・BRINGUP | 同上／9 は `tap_facts.md` |
| `review/main_power_compare.md:21・22・25・26・158` | TMR9・`AudioV2/datasheets/`・TMR6・OPA1652・`Audio/Library.pretty/TEC3…` | `datasheets/…`、`datasheets/opamps/TI_OPA1652.pdf`、`lib/Library.pretty/TEC3-1223_SIP8_THT.kicad_mod` |
| `review/main_power_compare_review.md:15・73` | 同上 | 同上 |
| `review/dcdc_2stage.md:23` | TMR9 | `datasheets/TMR9_Datasheet.pdf` |
| `review/pm12_judgement.md:9` | `Audio/OPAMP_INVENTORY.md` | `datasheets/opamps/INVENTORY.md` |
| `review/adc_gnd_retree.md:4`・`decisions_audit_3.md:260`・`decisions_audit_2.md:57・58・111・114・118・166`・`decisions_audit_2_review.md:6・10・21・50・104` | 「AudioV2/」「Audio/」「`Control/protocol.py`」「`AudioV2/control_fw/`」の地の文 | 残す（凍結記録の地の文）か「v1／v2 の…」に。**README の基準で読めれば直さなくてよい** |
| `review/DECISIONS_v21_draft.md`（外向きリンク 63） | v2 DECISIONS へのリンク | リンクを外して文字だけに（一括置換 `](../../AudioV2/DECISIONS.md)` → 空）。下書きは置き換え済みなので中身は触らない |
| `review/DECISIONS_v21_review.md:5・6・66・95・187` | v2 DECISIONS・「v2 Lnnn」 | 同上。**ついでに**: L35・40・44・53・60・69・75・86 の 10 本は `review/…` を二重に付けた壊れたリンク（`review/review/…` に解決）→ `review/` を外す |

### 5.4 スクリプト・spice・firmware

| file:line | 今 | 書き換え |
|---|---|---|
| `scripts/rail_budget.py:31・35・37・45・48・49・52` | v2 の DECISIONS・`Audio/datasheets/opamps/…` | 「DECISIONS 継-nn／G2・G3」、`AudioV2.1/datasheets/opamps/…`、L7809 は `ds_facts/power.md` §5 |
| `scripts/build_daughter.py:357` | v2 の DECISIONS「TMUX7612 に 1 µF…」 | DECISIONS G1 の新項目 |
| `scripts/sch_helpers.py:425`（403 の docstring も） | `ROOT.parent/"Audio"/"BP5293_ROHM.kicad_sym"` | `ROOT/"lib"/"BP5293_ROHM.kicad_sym"` |
| `scripts/split_frontpanel.py:111` | `ROOT.parent/"Audio"/"MeasurementADC_Extras.kicad_sym"` | `ROOT/"lib"/…` |
| `scripts/amp_sel_hop.py:854`（4 の docstring も） | `os.symlink(ROOT/"Audio", …)` | 行を削除 |
| `scripts/generate_kicad_scaffold.py:18・876–888` | `AUDIO`、lib-table の `../Audio/…` | `ROOT/"lib"`、`${KIPRJMOD}/lib/…`（回さないが grep を通すため）。968・1141・1181・1207–1214 の「Audio/ 流用」の文字列は v2 当時の生成物の文面なので残してよい（allow-list） |
| `scripts/wire_circuit_design.py:2・432・662・882・940・1230・1244・1294` | `CIRCUIT_DESIGN.md`・`AGENT_HANDOFF.md`・「v2 の DECISIONS manual volume」 | DECISIONS の項目か「CLAUDE.md（v2.1）のシート所有権」へ |
| `scripts/dcdc_survey.py:4`・`digikey_search.py:4` | `AGENT_HANDOFF.md §2.10` | 継-24・継-26・PARTS §0b |
| `spice/extract_dut_thd.py:50` | `parents[2]/"Audio"/"datasheets"/"opamps"` | `parents[1]/"datasheets"/"opamps"` |
| `spice/switch_compare.py:41`・`input_topology.py:44` | `Audio/datasheets/opamps/` | `datasheets/opamps/` |
| `spice/switch_thd.py:55` | `AudioV2/DECISIONS.md §8` | 「Amp のゲイン 2（Rf/Rg 20k/20k、図）」 |
| `spice/README.md:4・8・133・203・237・356・398・416・465・485` | v2 の DECISIONS・`AudioV2/spice/…`・`AudioV2/datasheets/…`・`Audio/datasheets/opamps/` | v2.1 の中のパスへ。4・465 は DECISIONS の該当項目 |
| `firmware/README.md:3・4・15・44` | v1 `Control/`・`Audio/measurement_fw/`・`cd AudioV2/firmware` | 3・4・15: 「計測ファームは v2.1 には無い（実機の既定は LCD スペアナ版）」、44: `cd AudioV2.1/firmware` |
| `firmware/vendor/lcd_st7796.py:3` | 「`Audio/measurement_fw/lcd.py` から分岐」 | 「v1 の計測ファームの LCD ドライバから分岐（2026-09）」 |
| `firmware/amp_select.py:56・62` | 「v1 relays の流れ」「v1 `Control/relays.py` を参照」 | 「DECISIONS §2-7・§6-2 の順序」 |

### 5.5 回路図・PCB・シンボル・ライブラリ表

| file:line | 今 | 書き換え |
|---|---|---|
| `AudioV2Case.kicad_sch:44681` | 注記「…(§9 / CIRCUIT_DESIGN §4)」 | 括弧を外す |
| `AudioV2Case.kicad_sch:44703` | 注記の「（v2 の DECISIONS）」 | 「（DECISIONS 継-05）」 |
| `AudioV2Case.kicad_sch:49809` | C501 の Description「（v2 の DECISIONS）」 | 「（DECISIONS 継-03）」。**PCB 側 `AudioV2Case.kicad_pcb:7393` の同じ欄は「（DECISIONS）」のまま**なので揃える |
| `AudioV2Case.kicad_sch:50379` | Q401 の Description「（v2 の DECISIONS）」 | 「（DECISIONS 継-05）」。PCB 側 `:46405` も |
| `AudioV2Case.kicad_sch:903・54031`、`AudioV2Case.kicad_pcb:25447`、`AudioV2.kicad_sym:630`、`legacy/PowerModule.kicad_sch:48・3518` | Datasheet `AudioV2/datasheets/Recom_REC20K-Z_Rev3-2025.pdf` | `datasheets/…`（RS6 へ替えるときに消えるなら、その作業で） |
| `AudioV2.kicad_sym:207` | DKMW20 の Datasheet `datasheets/SKMW20_DKMW20_Datasheet.pdf`（v2.1 に無い名前） | `datasheets/MeanWell_SKMW20_DKMW20.pdf` |
| `legacy/AmpBank.kicad_sch:3474`・`legacy/PowerModule.kicad_sch:1559`・`legacy/README.md:43` | `AGENT_HANDOFF 2.9`・`CIRCUIT_DESIGN §4`・`AudioV2/scripts/…` | `legacy/` を消すなら不要。残すなら直す |
| `sym-lib-table:3・4・6・7` | `${KIPRJMOD}/../Audio/…` | 3（DKMW20）は行ごと削除、4・6・7 は `${KIPRJMOD}/lib/…` |
| `fp-lib-table:3` | `${KIPRJMOD}/../Audio/Library.pretty` | `${KIPRJMOD}/lib/Library.pretty` |

### 5.6 `PARTS.md`（書き直しのときに消えるか直す）

5・7・20・21・69・115・128–162（§1 表示）・175・223・231・234・236・240・242・244・245・247・249・252・437・439・450・468・473・492・494・495。
生成ブロックの 313・366 は図の Description の写しなので、§5.5 を直して `gen_parts_bom.py` を回せば消える。
L20・21・495 のコマンド例 `AudioV2/scripts/gen_parts_bom.py` は `AudioV2.1/…` に。

---

## 6. `AudioV2.1/datasheets/` へ複写するもの

置き場は `AudioV2.1/datasheets/opamps/`（v1 と同じ構成にして、`ds_facts` の素の PDF 名がそのまま通るようにする）。**複写元はこのブランチの HEAD**（AD797 は main に無い）。

| 複写元 | 大きさ | 複写先 | 引いているところ |
|---|---:|---|---|
| `Audio/datasheets/opamps/AD_AD797.pdf` | 344,953 | `datasheets/opamps/` | `ds_facts/opamps.md`・`verify_opamps.md`・`opamp_fast_ds_review.md` |
| `…/AD_LT1364.pdf` | 229,606 | 同 | ds_facts（16 箇所）・FAST |
| `…/NJR_MUSES01.pdf` | 665,654 | 同 | ds_facts |
| `…/NJR_MUSES02.pdf` | 705,433 | 同 | ds_facts |
| `…/NJR_MUSES03.pdf` | 1,022,181 | 同 | ds_facts・`rail_budget.py`（G3） |
| `…/NJR_NJM4580.pdf` | 290,739 | 同 | ds_facts |
| `…/NJR_NJM5532.pdf` | 282,559 | 同 | ds_facts・`ds_errata_review.md` |
| `…/TI_LME49860.pdf` | 1,870,670 | 同 | ds_facts |
| `…/TI_NE5532.pdf` | 1,080,659 | 同 | ds_facts・`rail_budget.py` |
| `…/TI_OPA1612.pdf` | 1,573,947 | 同 | ds_facts・`spice/extract_dut_thd.py`（抽出モード） |
| `…/TI_OPA1652.pdf` | 2,221,948 | 同 | ds_facts・`rail_budget.py`・`main_power_compare*.md` |
| `…/TI_OPA1656.pdf` | 3,302,860 | 同 | ds_facts・`rail_budget.py`・`tap_facts.md`・`tap_compare.md` |
| `…/TI_OPA2134.pdf` | 1,482,135 | 同 | ds_facts |
| `…/TI_OPA2140.pdf` | 3,132,883 | 同 | ds_facts |
| `…/TI_OPA2604.pdf` | 588,657 | 同 | ds_facts |
| `…/TI_OPA627.pdf` | 1,614,402 | 同 | ds_facts |
| `…/TI_OPA828.pdf` | 3,193,639 | 同 | ds_facts・FAST |
| `…/README.md` | 3,041 | 同（L4・5・56 のリンクを直す） | 在庫表・FAST |
| `Audio/OPAMP_INVENTORY.md` | 7,359 | `datasheets/opamps/INVENTORY.md`（リンクを直す。L34 の「AudioV2 のレールは ±15 V…」は v2.1 の §3-3 に合わせて 1 行に） | `ds_facts/opamps.md:6`・`pm12_judgement.md:9`・PARTS §4.2 |
| `Audio/OPAMP_FAST_DS_REVIEW.md` | 13,292 | `review/opamp_fast_ds_review.md` | NOW L112・V21-未決-18 |
| `Audio/datasheets/TMR9_Datasheet.pdf` | 896,624 | `datasheets/` | `rejected_review*.md`・`main_power_compare*.md`・`dcdc_2stage.md`・`scripts/dcdc2/` |
| `Audio/datasheets/TMR6_Datasheet.pdf` | 229,722 | `datasheets/` | `rejected_review*.md`・`main_power_compare.md` |

合計: PDF 19 本・約 24.7 MB、文書 3 本。
KiCad ライブラリ（§2.1）: `Library.pretty` 464 KB ＋ `.kicad_sym` 3 本 41 KB → `AudioV2.1/lib/`。

リポジトリに無いまま引かれている DS（写しようが無いもの）: P82B96（継-05 の理由）、BSS138。§10-1 の「DS を取るもの」に足すかをユーザーに聞く。

---

## 7. 削除するもの

### 7.1 移行後に消す（v2.1 に要る部分を §3・§4 のとおり移したあと）

| ファイル | 消したあとに指しているもの（直すか消す） |
|---|---|
| `AGENT_HANDOFF.md` | `README.md:19`、`PARTS.md:69・439`、`datasheets/README.md:177`、`scripts/wire_circuit_design.py:1244・1294`、`scripts/sch_helpers.py:403`、`scripts/dcdc_survey.py:4`、`scripts/digikey_search.py:4`、`spice/README.md:4`、`legacy/AmpBank.kicad_sch:3474`、査読の地の文（`adc_gnd_retree_review.md:100・274`、`rejected_review.md:6`、`tap_facts.md:9` → README の基準で読む） |
| `AMP_SEL_ROUTING_HANDOFF.md` | `scripts/amp_sel_hop.py:4` |
| `CIRCUIT_DESIGN.md` | `README.md:30`、`PARTS.md:7`、`AudioV2Case.kicad_sch:44681`、`legacy/PowerModule.kicad_sch:1559`、`scripts/wire_circuit_design.py:2・432・882・940・1230` |
| `WIRING.md` | `README.md:32`、`scripts/generate_kicad_scaffold.py:1142・1230`（書き出す処理。回さない）、`review/decisions_audit_3.md:96`・`tap_facts.md:283`（地の文） |
| `VOLUME_IC_COMPARISON.md` | `README.md:37` |
| `DEST_SENSE_LADDER.md` | `README.md:33`、`PARTS.md:7` |
| `SYMBOL_FIX_TODO.md` | `README.md:37`、`scripts/generate_kicad_scaffold.py:7` |
| `SYMBOL_REVIEW_SUMMARY.md` | `README.md:37` |
| `scripts/dest_ladder_sim.py` | `DEST_SENSE_LADDER.md`（一緒に消える）。import 元なし |
| `scripts/__pycache__/`・`spice/__pycache__/` | git では追跡されていない（`git ls-files` で 0 件を確認済み）。grep から外すだけ |

**確かめ方**（消したあとに 0 件であること）:

```bash
cd /home/user/pcb_work
grep -rnIE --exclude-dir=__pycache__ \
  'AGENT_HANDOFF|AMP_SEL_ROUTING_HANDOFF|CIRCUIT_DESIGN|WIRING\.md|DEST_SENSE_LADDER|VOLUME_IC_COMPARISON|SYMBOL_FIX_TODO|SYMBOL_REVIEW_SUMMARY|dest_ladder_sim' \
  AudioV2.1 | grep -v '^AudioV2.1/review/'        # review/ は README の基準で読む地の文だけ残る
python3 - <<'EOF'   # Markdown の相対リンクが全部 v2.1 の中で解決するか
import re,os; from pathlib import Path
root=Path('AudioV2.1').resolve(); bad=0
for p in root.rglob('*.md'):
    t=p.read_text(encoding='utf-8',errors='ignore')
    for m in re.finditer(r'\]\(([^)\s]+)\)',t):
        u=m.group(1).split('#')[0]
        if not u or re.match(r'[a-z]+:',u): continue
        q=(p.parent/u).resolve(); ln=t[:m.start()].count('\n')+1
        ok_out = q.name in ('CLAUDE.md',) and q.parent==root.parent   # ルートの CLAUDE.md だけは許す
        if (not str(q).startswith(str(root)+os.sep) and not ok_out) or not q.exists():
            bad+=1; print(f"{p.relative_to(root.parent)}:{ln} -> {u}")
print('bad', bad)
EOF
```

### 7.2 任意: `legacy/`（6 ファイル）

- 読むのは `scripts/build_motherboard.py` の `build()` だけ（通常の実行は安全弁で止まる。`--dry-run` と `--overwrite-hand-owned-root` は読む）。`build_daughter.py` は `build_motherboard` を import するが `legacy/` は読まない
- 消すなら `build_motherboard.py` の `main()` を「v2.1 ではルートを生成しない」で即終了にする（`--dry-run` でも）
- 消すと `check_sexpr.py -q AudioV2.1` のファイル数は 13 → 9。期待値を `AudioV2.1/CLAUDE.md` に書く
- ルートの CLAUDE.md にある「生成シートから部品を外すときは素材（`legacy/`）を編集して再生成する」は v2 の規則。v2.1 のルートは手編集所有なので、`AudioV2.1/CLAUDE.md` では「娘は `build_daughter.py`、ルートは KiCad」とだけ書く

---

## 8. main へマージできる形にする — 巻き戻しと別 PR

今の `git diff --stat origin/main...HEAD -- . ':!AudioV2.1'`:
`.gitignore` +2、`CLAUDE.md` +2、`AudioV2/NOW.md` +8/−1、`Audio/OPAMP_FAST_DS_REVIEW.md`、`Audio/OPAMP_INVENTORY.md`、`Audio/datasheets/opamps/README.md`、`Audio/datasheets/opamps/AD_AD797.pdf`（新規）。

`AudioV2/NOW.md` の差分は 3 つのコミットから来ている（**ポインタだけではない**）:

| コミット | `AudioV2/NOW.md` の中身 | 行き先 |
|---|---|---|
| `2a77504`（Audio の 2 文書も） | `J_ANA301` の L/R 交差を直した（09-24）、「3. 高速娘」の項を追加 | 別 PR |
| `33dac84`・`bc7bb7f` | 高速娘の電源方針 → 見直し中に差し替え | 別 PR |
| `21cab8d`（v2.1 作成） | 冒頭 1 行「電源ゲート構成の検討は `AudioV2.1/`」 | **捨てる**（v2 は v2.1 を知らない） |
| `a03ac0a` | （NOW は触らない）AD797 の PDF と Audio 側の参照 | 別 PR |

手順（順序が大事。**v2.1 への複写（§6）を先に済ませてから** 3 をやる）:

```bash
cd /home/user/pcb_work
# 1. 別 PR 用のブランチ（v1 文書の訂正・AD797・v2 NOW の高速娘）
git switch -c docs/v1-opamp-review-fixes origin/main
git cherry-pick 2a77504 a03ac0a 33dac84 bc7bb7f     # どれも Audio/* と AudioV2/NOW.md だけを触る
git diff --stat origin/main -- . ':!Audio' ':!AudioV2/NOW.md'   # 空であること
git push -u origin docs/v1-opamp-review-fixes      # PR は別に立てる
git switch claude/vibrant-cray-axng64

# 2. §6 の複写（AD797 を含む）と §5 の書き換えをこのブランチでコミット

# 3. v2・v1 を main の状態へ戻す
git checkout origin/main -- AudioV2/NOW.md \
    Audio/OPAMP_FAST_DS_REVIEW.md Audio/OPAMP_INVENTORY.md Audio/datasheets/opamps/README.md
git rm Audio/datasheets/opamps/AD_AD797.pdf
git commit -m "v2・v1 を main の状態へ戻す（v1 文書の訂正は別 PR、v2.1 は自分の写しを持つ）"

# 4. 確認
git diff --stat origin/main...HEAD -- . ':!AudioV2.1'   # .gitignore と CLAUDE.md の 2 本だけ
git diff origin/main...HEAD -- .gitignore               # AudioV2.1/output/ と AudioV2.1/.kicad-mcp/ の 2 行
```

注意:
- 1 の cherry-pick は `2a77504` の NOW の変更に `33dac84` が乗るので、この順で入れる（衝突の有無は未確認。このセッションでは試していない）
- 別 PR が先に main に入ると、main 側にも AD797 と在庫表の訂正が入る。v2.1 の写しとは別物として扱い、**どちらを直すかは都度ユーザーに聞く**（在庫が増えたときに片方だけ直る）
- `CLAUDE.md` の今の 2 行は §9.1 のブロックに置き換える（行数は数行増える）

---

## 9. CLAUDE.md への追記案

### 9.1 ルートの `CLAUDE.md`（冒頭の 2 行を置き換える 1 ブロック）

```markdown
### AudioV2.1 を触るとき

- **v2.1 の作業は [AudioV2.1/NOW.md](../NOW.md) から始める。** 決定の正は `AudioV2.1/DECISIONS.md`、DS の事実は `AudioV2.1/ds_facts/`。
  所有権・検証の期待値・禁止事項の v2.1 版は [AudioV2.1/CLAUDE.md](../CLAUDE.md)（このファイルの表は v2 のもの）
- **v2.1 の作業中は `AudioV2/` と `Audio/` の文書（NOW・DECISIONS・AGENT_HANDOFF・README ほか）を文脈として読まない。**
  v2.1 が頼る事実は v2.1 の中に書き直してある。見つからなければ v2・v1 を読みに行かず、ユーザーに聞く
- 共有の道具（`Audio/scripts/check_sexpr.py`・`docker/kicad-cloud-build/kicad-run.sh`）はそのまま使い、対象は `AudioV2.1/…` と明示する
```

### 9.2 入れ子の `AudioV2.1/CLAUDE.md`（新設。`AudioV2.1/**` の中なのでマージ条件を満たす）

中身の骨子（Claude Code は作業中のディレクトリの `CLAUDE.md` を読み込む。ルートの 9.1 がここを指すので確実に届く）:

1. 入口: `NOW.md` → `DECISIONS.md`（§7 が v2 から引き継いだもの）→ `ds_facts/` → `review/`（凍結。行番号の基準は `review/README.md`）
2. シートの所有権（今の v2 と同じ形を v2.1 の名前で。ルートは手編集、娘は `scripts/build_daughter.py` が回路の正でピンポイント差し込み、`MeasureControl`・`FrontPanel` は KiCad）
3. 禁止: `generate_kicad_scaffold.py` を回さない（import 元として残す）、`build_motherboard.py` を回さない、`sch_edit.prune()` を生成シートに使わない、配線の検証に `sch_drift.py` を使わない
4. 検証の期待値（v2.1 の値。**図を変えたコミットではルートの CLAUDE.md ではなくここを直す** — ルートを直すと main へマージできなくなる）:
   `check_sexpr.py -q AudioV2.1` 13（`legacy/` を消したら 9）・問題 0 ／ `erc AudioV2.1/AudioV2Case.kicad_sch` 5 件・型は上の 3 種 ／ netlist 355 ／ roundtrip 全部 OK ／ `gen_parts_bom.py --check` OK
5. `SOURCE_OF_TRUTH.md` の原則は使う。**そこから辿る `AudioV2/…` へのリンクは読まない**
6. 査読（`/sch-review`）を v2.1 に投げるときの定型文: 「対象は `AudioV2.1/*.kicad_sch`（親 `AudioV2.1/AudioV2Case.kicad_sch`）。事実は `python3 AudioV2.1/scripts/sch_facts.py all`。決定は `AudioV2.1/DECISIONS.md`、DS は `AudioV2.1/datasheets/`。`AudioV2/`・`Audio/` の文書は読まない」
7. KiCad ライブラリは `AudioV2.1/lib/`（名前は v1 と同じ `Library`・`BP5293_ROHM`・`MeasurementADC1804`・`MeasurementADC_Extras`。名前を変えると図の `lib_id` と PCB の footprint 名が切れる）

Cursor 向けには `AudioV2.1/.cursor/rules/v21-context.mdc`（`globs: AudioV2.1/**`）に 1〜4 行で同じことを書く。
**入れ子の `.cursor/rules/` が今の Cursor で効くかは未確認**。効かなければ、ルートの `work-on-main.mdc`（alwaysApply、v2 の NOW へ誘導）がそのまま効き続ける — これは main へ入れたあとに別途直すしかない。

---

## 10. 手順（おすすめの順）

1. **ライブラリ**（§2.1）: `AudioV2.1/lib/` へ複写 → lib-table 2 本の `uri` → `amp_sel_hop.py`・`sch_helpers.py`・`split_frontpanel.py`・`generate_kicad_scaffold.py` のパス → ERC・DRC で前後比較（§11）。1 コミット
2. **DS と v1 文書の複写**（§6）→ `ds_facts/opamps.md:6`・`verify_*.md`・`review/` の DS パス・`rail_budget.py`・`spice/*.py` を書き換え。1 コミット
3. **DECISIONS**（§4）: §7 を差し替え、§4.7 から採るものを足し、§1〜6・§8・§9 の行番号を言葉に。**ユーザーが §4.7 の取捨を決めてから**
4. **回路図の文字列**（§5.5）→ `gen_parts_bom.py` で PARTS を作り直して同じコミット
5. **NOW・README・PARTS・datasheets/README・firmware/README・spice/README** を書き直し
6. **`review/README.md`** を足し、査読の出典キーの定義行と DS パスを直す
7. **削除**（§7.1、任意で §7.2）→ §7.1 の grep とリンク検査が 0
8. **`AudioV2.1/CLAUDE.md`** と、ルート `CLAUDE.md` のブロック（§9）
9. **巻き戻しと別 PR**（§8）→ `git diff --stat origin/main...HEAD -- . ':!AudioV2.1'` が 2 本

---

## 11. リスクと確かめ方

### 11.1 壊れうるもの

| リスク | どう壊れるか | 防ぎ方 |
|---|---|---|
| ライブラリ名を変えてしまう | 図の `lib_id`（`BP5293_ROHM:…` 等 20）と PCB の `Library:…`（10）が切れる。図は埋め込みで開けるが、ERC に `lib_symbol_issues`、DRC に `lib_footprint_issues` が出る | 名前は据え置き、`uri` だけ変える。前後で ERC・DRC の件数を比べる |
| 複写したライブラリの中身が図の埋め込みとずれる | ERC の `lib_symbol_mismatch`・DRC の `lib_footprint_mismatch` | `git diff origin/main -- Audio/Library.pretty Audio/*.kicad_sym` が空（v1 のライブラリはこのブランチで変わっていない。確認済み）なので、そのまま複写すれば同じ |
| 図の Description を直して PARTS を作り直さない | `gen_parts_bom.py --check` が落ちる（生成ブロックに Description が載る） | 同じコミットで `python3 AudioV2.1/scripts/gen_parts_bom.py` |
| 図の Description を直して PCB を直さない | PCB の同じ欄が古いまま（`:7393` は既に「（DECISIONS）」で図とずれている）。parity が Description を見るかは未確認 | PCB の 2 か所も同じ文に。`pcb drc --schematic-parity` を前後で比べる |
| `generate_kicad_scaffold.py` を消す | `build_daughter.py` ほか 7 本の import が落ちる | 消さない。パス文字列だけ直す |
| `build_motherboard.py` を消す | `build_daughter.py` が `SLOT_ANA_NETS`・`SLOT_PWR_NETS`・`_merge_lib_symbols`・`ROOT_PATH` を失う | 消さない |
| `legacy/` を消す | `build_motherboard.py --dry-run` が FileNotFoundError | `main()` で即終了にする（§7.2） |
| `spice/extract_dut_thd.py` の DS パス | 抽出モードで PDF が見つからない（`--report` は JSON を読むだけなので影響なし） | 複写後に抽出モードを 1 回 |
| `amp_sel_hop.py` の symlink を消す前にライブラリを複写しない | DRC の作業場所で `Library` が解決できない | 手順 1 の中で順に |
| 査読の行番号 | `AGENT_HANDOFF.md` を消すと `[HO:行]` が辿れない（DECISIONS は既に置き換え済みで `[DEC:行]` も今の v2.1 とは合わない） | `review/README.md` に基準コミット `5d2cd25` を書く |
| main へのマージ | v2.1 の期待値をルート `CLAUDE.md` の表へ書くと diff が増える。`.cursor`・`.claude`・`SOURCE_OF_TRUTH.md` を直しても同じ | v2.1 の期待値と指示は `AudioV2.1/CLAUDE.md` へ（§9.2）。§8 の最後の確認 |
| エージェントの設定が v2 へ誘導し続ける | `.claude/agents/sch-review.md`・`.cursor/rules/work-on-main.mdc` は v2 の NOW・DECISIONS・datasheets・legacy を読ませる | 9.2 の定型文を必ず渡す。main へ入ったあとで別途直す |
| リポジトリが太る | opamps の PDF 約 24 MB が 2 重になる | 許容するか、LFS にするかをユーザーに |
| 在庫表・FAST 精査が 2 本になる | ユーザーが在庫を更新したとき片方だけ直る | v2.1 の写しが v2.1 の正、と `datasheets/opamps/INVENTORY.md` の冒頭に書く |
| `DECISIONS_v21_review.md` の壊れたリンク 10 本 | 既に壊れている（`review/review/…`） | ついでに直す（§5.3） |

### 11.2 確かめるコマンド（前後で同じ値）

```bash
cd /home/user/pcb_work
python3 Audio/scripts/check_sexpr.py -q AudioV2.1                       # 問題 0（13 ファイル、legacy を消したら 9）
python3 AudioV2.1/scripts/sch_import.py --roundtrip AudioV2.1/*.kicad_sch  # 全部 OK
python3 AudioV2.1/scripts/gen_parts_bom.py --check                      # OK
KICAD_BACKEND=local docker/kicad-cloud-build/kicad-run.sh erc AudioV2.1/AudioV2Case.kicad_sch
                                                                        # 5 件、型は ground_pin_not_ground 2 / isolated_pin_label 2 / multiple_net_names 1
KICAD_BACKEND=local docker/kicad-cloud-build/kicad-run.sh netlist AudioV2.1/AudioV2Case.kicad_sch   # 部品 355・重複 0
kicad-cli pcb drc --format json --severity-all --schematic-parity -o out/v21/drc.json AudioV2.1/AudioV2Case.kicad_pcb
                                                                        # schematic_parity 0、lib_footprint_* が移行前と同じ（移行前に 1 回取っておく）
python3 AudioV2.1/scripts/sch_helpers.py          # シンボル探索の自己診断
python3 AudioV2.1/scripts/build_daughter.py --dry-run
python3 AudioV2.1/scripts/rail_budget.py          # 出典の文字列が v2.1 の中を指す
python3 AudioV2.1/scripts/sch_facts.py all        # 355
```

**v2・v1 が無くても動くことの確認**（いちばん強い検査。リポジトリの外の作業場所で）:

```bash
git worktree add /tmp/v21iso HEAD
rm -rf /tmp/v21iso/AudioV2 /tmp/v21iso/Audio/*.kicad_sym /tmp/v21iso/Audio/Library.pretty \
       /tmp/v21iso/Audio/datasheets /tmp/v21iso/Audio/*.md /tmp/v21iso/Control
cd /tmp/v21iso && (上の 11.2 のコマンドを全部)      # check_sexpr.py と kicad-run.sh は残る
cd /home/user/pcb_work && git worktree remove --force /tmp/v21iso
```

**参照が残っていないことの確認**（許すのは道具の行だけ）:

```bash
grep -rnIE --exclude-dir=__pycache__ \
  '(\.\./)+(AudioV2|Audio|Control)/|(^|[^.0-9A-Za-z])AudioV2/|(^|[^A-Za-z0-9])Audio/(datasheets|OPAMP|Measurement|README|measurement_fw|Library|split|Controll|AudioCase)|"Audio"|v2 の DECISIONS|v2 の決定ログ|v2 L[0-9]' \
  AudioV2.1 \
  | grep -vE 'Audio/scripts/check_sexpr\.py|generate_kicad_scaffold\.py:(968|1141|1181|120[7-9]|121[0-4])|^AudioV2\.1/review/'
# 期待: 0 行。review/ は README の基準で読む地の文だけ残る（別に数えて、DS のパスが 0 であること）
grep -rnE 'Audio/datasheets|AudioV2/datasheets' AudioV2.1/review AudioV2.1/ds_facts   # 0 行
git diff --stat origin/main...HEAD -- . ':!AudioV2.1'                                  # .gitignore と CLAUDE.md だけ
```
