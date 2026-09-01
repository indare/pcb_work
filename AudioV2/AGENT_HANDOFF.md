# AudioV2 エージェント引き継ぎメモ

**更新:** 2026-09-01（ローカル `DESK01`）  
**目的:** クラウド↔ローカル切替で会話 UI が分岐／短く見えることがあるため、別チャットからでも再開できるようにする。  
**作業の正:** 常に git ブランチ **`main`**（歴史的な `cursor/audiov2-*` 等は base にしない）。

関連:

- ルール: `.cursor/rules/work-on-main.mdc`
- ローカル会話: [Power/PD 整理系](37c7411c-c7bb-4644-9194-686ff5fe1fd5)

---

## 1. いま何をしているか（一言）

**アーキテクチャ刷新（§2.9）の手順3〜5が完了・コミット済み（`main` へ push 済み）。
`AmpBank`/`AmpChannel` はユーザーが KiCad で `AmpCh2` を手直ししたのを機に
**生成コード所有→手編集所有へ卒業**（2026-09-02、§2.8）。
いま進行中なのは別スレッド: **PowerModule の絶縁型DC-DCコンバータ（現行 `DKMW20F-15`、$30.75）が
高いという指摘を受けての代替候補調査**（§2.10 に詳細・次のセッションはここから再開）。
回路図・BOMへの反映は**まだ何もしていない**（調査・比較のみ）。**

2026-09-01 に「RelayBoard 5ch×2 + AmpModule ×10」を **`AmpBank` 1枚へ統合**すると決めた（§2.9）。
切替はラッチングリレー AZ850 → **アナログスイッチ TMUX7612**、電源は切替せず **常時給電**、
レールは **±15 V**（TMUX7612 と LT1364 の要求、v1 資産との互換。DECISIONS.md §8）。経緯と根拠は §2.9。

いまリポジトリに **ある / 無い**もの（2026-09-01 更新）:

| もの | 状態 |
|---|---|
| `TMUX7612` シンボル、`DKMW20F-15` シンボル（`AudioV2.kicad_sym`） | **ある**。DKMW20F-15 は v1 `Audio/DKMW20.kicad_sym` から移植（フットプリント `Library:DKMW20F-15_1in_THT` も v1 資産で既存） |
| `AmpBank.kicad_sch` / `AmpChannel.kicad_sch` | **ある**。`wire_circuit_design.py bank` / `channel` で生成・コミット済み。所有権は生成コード |
| `AudioV2Case.kicad_sch`（親） | **`AmpBank` 1枚に差し替え済み**。旧3シート（RelayBoard_A/B, AmpModule_Reference）を撤去 |
| `PowerModule.kicad_sch`（手編集所有） | **`+15V`/`-15V` へ改名、DKMW20F-12 → -15 に差替え済み**（直接 sexpr 編集。KiCad GUI 未検証） |
| `ControlPanel.kicad_sch` | **`+15V`/`-15V` へ改名して再生成済み**（生成コード所有なのでスクリプト実行のみ） |
| 旧 `RelayBoard.kicad_sch` / `AmpModule.kicad_sch` | **削除済み**（`git rm`）。生成関数 `relay_board_wired()`/`amp_module_wired()` はコード上に残置（デッドコード、§2.8 未整理） |

残る作業（§2.9 手順6・7 相当）:
1. **§2.8 所有権モデル表の更新** — 本メモ内でこの手順の一部として反映済み（下記参照）。旧 `relay_board_wired()`/`amp_module_wired()` 関数本体の削除はまだ
2. `CIRCUIT_DESIGN.md` §5・`WIRING.md` 全体・`DECISIONS.md` のRelayBoard/AmpModule前提の記述は**未着手**（重要箇所にのみ「旧アーキテクチャの記録」フラグを追記済み。全面書き換えは別タスク）
3. `PARTS.md` §4.2「選定・実装メモ」の内容更新（BOM生成ブロックの対象は `AmpBank.kicad_sch` へ切替済み。ただし kicad-cli の制約で**代表 ch1 分＋共通部のみ**表示、×10 は手動換算が要る旨を注記済み。詳細は §5）

刷新後も生きている確定事項:
I2C/電源トポロジは **スター確定**（daisy 不採用、WIRING.md）。端子台は v1 `Audio/Controll.kicad_sch` と同じ Phoenix MKDS-1,5 系。
A_GND / D_GND の NetTie は **ControlPanel 側**（Pico 直近）に1点。ゲイン2（20k/20k）、DIP-8 ソケット。
帰還抵抗の倍率表をシルクに入れる（§2.9）。

刷新により **不採用経路の記録** に降格したもの: §2.6 番地ストラップ、§2.7-3 コイル駆動マージン、
および §2.7 の RelayBoard レビュー指摘全般（基板そのものが無くなるため）。

KiCad の実行環境は `docker/kicad-cloud-build/kicad-run.sh` で解決済み（Docker イメージが無ければ
ホストの `kicad-cli` へ自動フォールバック）。**この Windows ローカル環境では別途:**
`C:\tmp\kicad-symbols` を KiCad インストールの `share/kicad/symbols` へのジャンクションとして
作成しないと `wire_circuit_design.py` のピン数ルックアップが失敗する（`sch_helpers.py` の
`KICAD_SYM_ROOT` フォールバックが `/tmp/kicad-symbols` 前提のため）。`kicad-run.sh` には
`PYTHONUTF8=1` を追加済み（Windows のコンソールコードページで `drift`/`gen_parts_bom.py` の
UTF-8 出力がクラッシュする問題への対処）。

次の話題候補: ERC 60件の仕分け（旧47件から純増10件は AmpBank 各chの `ground_pin_not_ground`
警告＝TMUX7612 VSS=-15V の既知誤検知。残りは元々あったControlPanel未接続ピン等） /
`WIRING.md`・`CIRCUIT_DESIGN.md`・`DECISIONS.md` の RelayBoard/AmpModule 前提記述の全面書き換え /
`relay_board_wired()`/`amp_module_wired()` デッドコードの削除。

> **記法について:** このメモは部品を原則 **ネット名・機能名**（回路図 Value 欄の名前）で指す。
> 参照(designator)は KiCad の採番の産物で再アノテーションのたびに動くため（2026-09-01 に58件が変わった）、
> 参照が主題そのものになる箇所（§2.6 の番地ストラップ表、§2.8 の所有権/参照対応、生成スクリプト内の識別子）
> だけに限定して残している。方針は [`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §3。

---

## 2. 設計の確定事項（忘れないこと）

| 項目 | 内容 |
|---|---|
| 最終音量 | **手回しデュアルポット**（PGA / digipot 不採用） |
| DEST | トグル＋抵抗ラダー |
| Tone | PT2314。電源は **`VCC_TONE`(+9)** ← Power LM7809 |
| 基板分割 | **Power ≠ Control**。Control+Output 同居可。Power 同居は非推奨（GND/熱/EMI） |
| 隔離 | 一次 `PD_GND` ≠ 二次 `A_GND`。DKMW **R.C. = NC（オープン=ON）** |
| Output / Amp | Outputは`SW_SP3T`×2。Ampは `AmpBank` 1枚に10ch統合、`AmpChannel`サブシート×10（§2.9、PCB は未設計） |

詳細: `DECISIONS.md` / `CIRCUIT_DESIGN.md` / `PARTS.md` / `WIRING.md`

### 2.1 PowerModule 現状（2026-09-01 更新）

```text
`PD module in` 端子台 ← 外付け PD モジュール (1=GND 2=+12V)
        → PD_12V ──(Case)──► ControlPanel パネル PWR SW
                              → PD_12V_SW ──(Case)──► ヒューズ(3A slow) → DKMW +Vin
                                 └─ 12V パネル LED もこの節点から PD_GND へ（SW 後＝通電表示）
        PD_GND ←→ 一次（LED 戻りもここ）

DKMW → +12V / -12V / A_GND → `+12/-12/A_GND out` 端子台（星型幹線 3P）
+12V → LM7809 → `VCC_TONE OUT` 端子台 (1=A_GND 2=9V) → ControlPanel PT2314
```

Power 基板の端子台は3つ。回路図の **Value 欄**が下表の文字列そのものなので、参照(designator)ではなく
これで引くこと（Value は設計者が付けた名前なので再アノテーションで動かない）。ピン割当は Value に
埋め込んである。**下表は実 Value の全文**（`kicad-cli sch export netlist` で確認）。

| 端子台（回路図 Value・全文） | 役割 |
|---|---|
| **`PD module in (1=GND 2=+12V)`**（2P） | PD 給電モジュール入（外付け 50224 可）。1=`PD_GND` / 2=`PD_12V` |
| **`+12/-12/A_GND out`**（3P） | `+12V` / `-12V` / `A_GND` 星型出 |
| **`VCC_TONE OUT (1=A_GND 2=9V)`**（2P） | `VCC_TONE` 出。1=`A_GND` / 2=+9 V。戻りは星点側 `A_GND`。幹線 `A_GND` と二重ループにしない |

- シート注記も上記に更新済み
- **PWR SW / 12V LED の実体は ControlPanel**（フロント PCB）。Power に置かない
- オンボード USB-C / CH224 は外してよい（50224 モジュール代用がデフォルト想定の一つ）

### 2.2 PD 配線トポロジ（未決・議論メモ）

どちらも「SW 後で DKMW」は同じ。違うのは **PD モジュールの差し込み位置**。

| | 入口 | 実配線 |
|---|---|---|
| **A（いまの図）** | Power の `PD module in` 端子台 | Power→Panel へ未スイッチ HOT+GND、Panel→Power へ SW 済み HOT（**往復端子が必要**） |
| **B** | ControlPanel | Panel で SW 後、Power は `PD_12V_SW`+`PD_GND` だけ（往復の「出し」不要） |

- 守りたい本体は **Power**。ホット切り離しは **ControlPanel**
- 実配線の自然さは B 寄り、電源室に PD を集めるなら A
- **この話題は一旦打ち切り**（2026-08-31）。図は A のまま

### 2.3 GND / VCC_TONE

- `VCC_TONE` 戻り = 二次 `A_GND`（7809 GND と同一。衝突ではなく共用）
- 星型 `A_GND` とトーン用戻りを別ケーブルで両端接続すると **ループ**しやすい → `VCC_TONE OUT` 端子台で寄り道するのが方針。**+9 V と戻り `A_GND` を同じ 2P に同梱し、この 2P 以外では戻りを幹線 `A_GND` に結ばない**（別ケーブルで引いて両端で繋ぐとループになる）

### 2.4 手持ちオペアンプ（2026-08-31 申告）

正本: **[`Audio/OPAMP_INVENTORY.md`](../Audio/OPAMP_INVENTORY.md)**  
DS PDF: **[`Audio/datasheets/opamps/`](../Audio/datasheets/opamps/README.md)**（全石ローカル保管済み）

NJM5532DD / NJM4580DD / OPA2134PA / OPA1656ID / OPA2604AQ / LME49860NA / LT1364CN8 / **MUSE01**（2石→1DIP変換）・**MUSE03**（2石→DIP化・2ch変換基板）・MUSES02D、および OPA828・OPA627AU・OPA1612・OPA2140・OPA1652 の DIP 化モジュール等。  
±12 V（DKMW）電源定格は **全石 OK**（詳細は在庫表）。

### 2.5 AmpModule再版（2026-08-31）

- `AudioV2/AmpModule.kicad_sch`: L/R非反転、ゲイン `1+20k/20k=2`
- **PCB は未設計**（2026-09-01 に `AmpModule.kicad_pcb` と `build_amp_pcb.py` を削除）。旧 pcb は `Audio/split/AudioCase_4_amp.kicad_pcb` からの移植で、削除の決め手は**再アノテーションで参照対応が壊れており、生成器を回すと実図と違う PCB を出力する状態だった**こと（生成器は `R703=1k`／実図は `R703=47R` 等）。外形15mm拡張の実座標・新規部品の配置・バルク周りの配線は `git show 6044089:AudioV2/scripts/build_amp_pcb.py` に残る。着手時の要件は `PARTS.md` §4.2
- バルク: `+12V` / `-12V` 各レールに 100 µF 35 V polymer
- 高周波: 各レールに 100 nF X7R ＋ 1 nF C0G（高速石を挿しても高域までレールを低インピーダンスに保つため、X7R 単独にしない）
- 出力: L/R 各chに 47 Ω 直列 ＋ 470 µF 25 V D12.5/P5 の DC カット（この順。47 Ω が先）。47 Ω は**出力アイソレーション**で、直後の 470 µF とケーブルの容量負荷から OpAmp 出力段を切り離す。高速石に差し替えたときの発振余裕のため（`CIRCUIT_DESIGN.md`）
- 親は`AmpModule_Reference` 1シート。回路/BOM代表であり、Relay端子配線で物理×10を選択

**信号順配線化（2026-08-31、コード変更のみ・未実行）:** `amp_module_wired()`はラベルのみで実配線が無かった（旧v1の`Audio/AmpModule.kicad_sch`は逆に配線68本・ラベル0）。以下をコードに反映済み:
- OpAmp2ユニットの**回路図上の配置**をunit1↔unit2で入れ替え、各chの帰還/出力段（既にL=y45.72-66.04, R=y78.74-99.06で各chごとに纏まっていた）とOpAmpユニットが同じ行に来るようにした（物理ピン割当=unit A/Bは変更していないのでPCBには無関係）
- 入力バス（入力端子台 `AMP_IN L/R` → `TONE_L`/`TONE_R` → 各chの入力抵抗・カップリング）と出力段末尾（DC カット → 出力端子台 `AMP_OUT L/R` = `AMP_SEL_L`/`AMP_SEL_R`）に実配線を追加。ネットラベルは残したまま（配線＋ラベル両方あるが電気的に問題なし）
- 帰還ネットワーク周り（L_AC/L_INV/L_OUT_OP等、複数分岐・複数ピンが絡む箇所）は座標を手計算で引くリスクが高いためラベルのままにした（安全側判断）
- **AmpModule.kicad_sch自体はまだ未再生成。** `python3 AudioV2/scripts/wire_circuit_design.py amp` をKiCadのあるマシンで実行し、`check_sexpr.py`とKiCadでの表示・ERCを確認してからコミットすること。AmpModuleは「生成コード所有」のまま（RelayBoardと違い安全装置は不要）

### 2.6 RelayBoard 番地ストラップ（2026-08-31 更新 / **不採用経路の記録** — §2.9 で統合1枚基板へ）

結線は **`3V3 → JP → A0/A1 → 10 kΩ → D_GND`**。プルダウンはジャンパ**後段**。JP 手前で分岐すると JP 未実装時に A0/A1 が浮くので不可。

**この節は例外的に参照(designator)で書く。**「どの部品を実装するか／しないか」で番地が決まる実装指示であり、
参照が記述の主題そのものだから（[`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §3 の語彙ルールの適用外、同 §4「それでも designator が要る場所」）。
以下の参照は **A 板（親の1インスタンス目）**のもの。親で RelayBoard を2回インスタンス化しているため、
B 板のストラップ／プルダウンには別の参照が振られる（§2.7-4）。

- `JP301`/`JP302` = **`Device:R` / 値 `0R` / FP `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder`**
- `R301`/`R302` = 10 kΩ プルダウン、**常時実装**。同じ 1206 FP
- 番地ビットは「どちら側に載せるか」ではなく **JP を載せるか載せないか**で決まる

| JP302 (A1) | JP301 (A0) | ADDR | 板 |
|---|---|---|---|
| 未実装 | 未実装 | 0x20 | A |
| 未実装 | 0 Ω | 0x21 | B |
| 0 Ω | 未実装 | 0x22 | C |
| 0 Ω | 0 Ω | 0x23 | D |

- **`SolderJumper_2_Open` は不採用**。FP が `SolderJumper-2_P1.3mm_*`（1.3 mm ピッチ / 1.0×1.5 mm パッド）しか無く 0 Ω チップが載らない。1206 なら 0 Ω 実装でもハンダブリッジでも可
- JP 位置に 10 kΩ を載せるのは誤り（10k∥10k で約 1.65 V、3.3 V の VIH を下回る）
- `~RESET`(18) は `3V3` 直結（Low アクティブ、浮かせ禁止）。`A2`(17) は `V_SS`(10) と同節点で `D_GND`
- I2C プルアップ（`I2C_SDA`/`I2C_SCL` → `3V3`、4.7 kΩ ×2）は **ControlPanel 側にのみ置く**。RelayBoard 側には置かない — 板を増やすたびに並列化して合成値が下がる（RelayBoard 4 枚に置くと板側だけで 4.7 k/4 ≈ 1.2 kΩ、ControlPanel 側の 1 本と合わせて 4.7 k/5 ≈ 0.94 kΩ）ため。スター配線（WIRING.md）の電気的中心が ControlPanel なのとも一致する
- 参照接頭辞は `Device:R` に対し `JP` のまま（ストラップである意図を残す）。**KiCad で「既存アノテーションをリセット」して再アノテートすると `R3xx` に振り直される**ので実行しない

**✅ スクリプト同期（2026-08-31、コード上は完了・実機未検証）:** `wire_circuit_design.py` の `addr_strap`/`C301`/`C302`/`J_I2C`（いずれもスクリプト内の識別子。スクリプトが参照をハードコードしている点自体は [`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §2 の負債）と階層ラベルを現図の座標へ書き直した。根拠は `RelayBoard.kicad_sch` の実座標を `pin_connect()` 相当の計算で裏取りし、`CIRCUIT_DESIGN.md`/`DECISIONS.md` の論理設計（`JP301`=A0・`JP302`=A1、I2C/電源コネクタのピン順 = `I2C_SDA`/`I2C_SCL`/`3V3`/`+5V`/`D_GND`）と突き合わせて確認したもの。`ADDR_A0`/`ADDR_A1` のネットラベルも復活させた。

途中で `sch_helpers.grid()`/`symbol_inst_v10()` が **常に2.54mmグリッドへ丸めていた**ことに気づいた（RelayBoardの実配置は半分の1.27mmグリッド）。全シート共通のヘルパーなので既定値2.54は変えず、`grid_step`/`at(x,y,step)`という**オプション引数**を追加し、RelayBoardの新規座標だけ`1.27`を明示的に渡す形にした（他シートの出力は不変）。これに気づかず2.54のまま実装していたら、座標が数mmずれた状態で「同期完了」と誤報告するところだった。

**ただしこのクラウド環境にKiCad本体が無く、`wire_circuit_design.py relay --force-relay` を実際に実行してKiCadで開ける／ERCが通ることまでは検証できていない。** ローカル（Windows）で一度実行し、`kicad-cli sch export netlist` と `kicad-cli sch erc` で確認してから安全装置解除の判断をすること。

**安全装置（2026-08-31 追加）:** `main()` は `relay` への書き込みをデフォルトでスキップし、警告を出すだけになった。上書きするには明示的に `--force-relay` を付ける（`python3 wire_circuit_design.py relay --force-relay`）。誤操作（Cursorエージェントが `.cursor/rules/work-on-main.mdc` を見て「再生成は wire_circuit_design.py」とだけ理解し `all` を回すケースなど）を防ぐための保険。スクリプト同期は済んだが、上記の実機未検証ゆえ**当面は解除しない**。

### 2.7 RelayBoard レビュー指摘（2026-08-31、いずれも接続ミスではない / **不採用経路の記録** — §2.9 で基板ごと置換）

1. **A0/A1 ネットが無名** — MCP23017 の A0/A1 に付くネットに名前が無く、KiCad が参照から自動生成した名前（`Net-(U302-A0)` 形式）になっている。`ADDR_A0`/`ADDR_A1` ラベルを戻すとネットリスト差分と ERC ログが読みやすい。**自動生成名は参照を含むので、再アノテーションのたびにネット名まで動く**（＝ `SOURCE_OF_TRUTH.md` §3 の語彙ルールが効かない状態）のも名前を付けたい理由。**→ `wire_circuit_design.py` のスクリプト同期（§2.6）でラベルを復活させた。`--force-relay` で実図に反映するまでは無名のまま**
2. **IC 直近パスコン不足** — 既存の 100 nF ×2 は方針どおり I2C/電源コネクタ入口（`3V3` 側・`+5V` 側）に置いてある。別途 MCP23017 の 9/10 ピン間、ULN2803A 2個の 10/9 ピン間に 100 nF が欲しい。`+5V` はリレーパルスが乗るので、リレー群近傍にバルク 100–220 µF も検討
3. **コイル駆動マージン不足 — 仕様上アウト（2026-09-01 検算済み / 対処は §2.9 のアーキテクチャ刷新。以下は検算の記録）**

   データシート実値だけで検算した結果、**周囲 40 ℃ を超えると Must Operate を満たさない**。25 ℃ でも余裕は 7 % しかない。

   | 出典 | 実値 |
   |---|---|
   | `Zettler_AZ850.pdf` p2 “Dual coil latching” | コイル **125 Ω ±10 %**、**Must Operate 3.75 V**、Max Continuous 10 V |
   | `ST_ULN2803A.pdf` Table 4 | VCE(sat) **IC=100 mA で 0.9 typ / 1.1 max V** |
   | `ROHM_BP5293-xx.pdf` | +5 V 出力 **5.0 V ±2 %**、最大 1.0 A |

   `CHn_SET` は audio/power 2 個のコイルを並列駆動（125 Ω∥125 Ω = 62.5 Ω）。実測モデルで解くと ULN2803A の降下は 65 mA で **0.98 V**。

   | 条件 | コイル印加 | 必要 | 余裕 |
   |---|---|---|---|
   | 公称 25 ℃・電源 5.00 V | 4.02 V | 3.75 V | +7.2 % △ |
   | 電源 −2 %・40 ℃ | 3.89 V | 3.97 V | **−1.9 % NG** |
   | 電源 −2 %・60 ℃ | 3.91 V | 4.27 V | **−8.4 % NG** |

   **真因は「2 個並列」ではなく、ダーリントンが約 1 V 落とすこと。** 1 コイル/ch に分けても余裕は +7.2 % → +10.2 % にしかならない（ULN を 3 個に増やす価値は無い）。5 V レールの 20 % が駆動段で消えているのが本質。

   **対策候補: `TBD62083APG`（東芝、8ch sink DMOS アレイ）へのドロップイン差替。**
   DS（2026-05-13 版）実値: RON **2.0 typ / 3.25 max Ω**（VDS 0.325 V max @ IOUT=100 mA）、VIN(ON) **2.5 V MIN**、出力 50 V / 500 mA/ch、各出力にクランプダイオード内蔵。**ピン配置（1-8=I1-I8 / 9=GND / 10=COMMON / 11-18=O8-O1）とパッケージ（P-DIP18-300-2.54）が ULN2803A と完全一致**。65 mA での降下は 0.21 V。

   | 条件 | コイル印加 | 必要 | 余裕 |
   |---|---|---|---|
   | 公称 25 ℃ | 4.75 V | 3.75 V | +26.6 % OK |
   | 電源 −2 %・40 ℃ | 4.62 V | 3.97 V | +16.4 % OK |
   | 電源 −2 %・60 ℃ | 4.64 V | 4.27 V | +8.7 % △ |

   **判定基準について:** Must Operate 3.75 V は製造ばらつき込みでメーカーが保証する電圧なので、これにコイル抵抗 ±10 % を掛けるのは二重計上。温度によるコイル抵抗上昇ぶん（銅 +0.393 %/℃）だけ必要電圧を押し上げるのが正しい扱い。

   **残る不確実性:** TBD62083A の RON は **VIN=5.0 V での規定値**で、MCP23017 の 3.3 V 駆動では規定されていない（しきい値 2.5 V は超えるので動作はする）。悲観的に RON を 2 倍と置いても公称 +20.7 % / 40 ℃ で +8 % 台なので結論は変わらないが、採用時は実測か東芝への確認が要る。なお **MCP23017 を 5 V 電源にする案は採れない** — VIH = 0.8×VDD = 4.0 V となり、ControlPanel 側 3.3 V プルアップの I2C を High と認識できないため。

   **ケーブル降下は無視できる**（当初 0.2 V と見積もったのは過大。AWG24・1 m 往復でも 65 mA で 11 mV）。圧着不良がある場合のみ問題。
4. **A/B は同一番地に見える** — 親で 2 回インスタンス化しているため、ネットリスト上は A/B が同じ JP 状態＝同じ番地。実装時に基板ごとに JP を変える運用（シルク早見表が前提）
5. **起動時 I2C スキャン** — 0x20–0x23 を叩いて応答番地をログ出力。JP 未実装のまま 2 枚組むと両方 0x20 で応答し、配線不良に見える化け方をするため
6. A1 側プルダウン抵抗の参照テキストが MCP23017 のピン番号「17」と軽く重なる（可読性のみ）

**確認済み・問題なし:** 3.3 V ロジック → ULN2803A 入力は IB ≈ 0.7 mA、必要 hFE ≈ 114 に対しダーリントンは 1000 以上。

### 2.8 シートの所有権モデル（2026-08-31 制定）

`wire_circuit_design.py` が担保するのは**回路の論理設計と意図**（どのネットがどのピンに繋がるか）を回路図sexprに正しく起こすところまで。生成された回路図は人間がKiCad上で読んで座標・フットプリント・配線の見た目を手で整える対象で、そこに手が入った時点でそのシートは**「生成コード所有」から「手編集所有」へ卒業**する。

| 状態 | 意味 | 該当シート |
|---|---|---|
| **生成コード所有** | `wire_circuit_design.py <target>` を回せばそのまま正 | Control, 親 |
| **手編集所有** | KiCad上の手編集が正。生成コードはロジック（ネット/ピン対応）のドキュメントとして残すが、機械的に上書きしてはいけない | **Power**（2026-09-01〜）, **Output**（2026-09-01〜）, **AmpBank**（2026-09-02〜）, **AmpChannel**（2026-09-02〜） |

**2026-09-01 更新（§2.9 統合）:** `RelayBoard` は基板ごと廃止（削除済み）。`Amp`（旧 `AmpModule`）は
`AmpBank`/`AmpChannel` に置き換わり、生成コード所有のまま。旧 `relay` の書き込み安全装置
（`--force-relay` 必須化）は対象シートが無くなったため `main()` の `HAND_EDITED` から削除した。

**2026-09-02 更新:** ユーザーが `AmpCh2` を KiCad で直接修正（バルクコンデンサ周りの未接続配線を含む）。
これにより `AmpBank`/`AmpChannel` は**生成コード所有から手編集所有へ卒業**。`main()` の `HAND_EDITED` に
`bank`/`channel` を追加し（`--force-bank`/`--force-channel` が脱出ハッチ）、`GENERATED` からは削除した。
再アノテーションで `AMP701→AMP601` 等・`C_BULK_P`/`C_BULK_N` の参照が入れ替わったが、ネットリストで
電気的な接続と極性を個別に検証済み（後述、問題なし）。

**drift 実測（2026-09-02、`kicad-run.sh drift` をこの Windows ローカル環境で実行）:**

| シート | 再生成 vs 実図 |
|---|---|
| Control / 親 | ✅ 完全一致（部品・ネット名・サブシートとも） |
| **AmpBank** | 手編集所有に移行。参照相違8件（`J_CTRL→J_CTRL301`等、末尾301付与＋`C_BULK_P`/`C_BULK_N`入れ替え）・座標相違6件。想定内 |
| **AmpChannel** | 手編集所有に移行。参照相違24件（再アノテーションでAMP701→AMP601等に変動）・ネット名相違8件・座標相違24件。想定内 |
| **Output** | 変わらず — Amp 共通ハーネス受けの `RAIL IN` 端子台が生成されない。部品5個の座標も相違（従来からの既知ギャップ） |
| **Power** | 変わらず一世代古い（PD 前段が USB-C+CH224 内蔵 vs 実図は外付けモジュール）。`+15V`/`-15V` ネット名と `DKMW20F-15` は生成側・実図側とも一致 |

**参照の対応表（生成スクリプト側 → 実図）:** ここは参照そのものが主題なので designator で書く。
Power は `F1→F201` / `U1→U201` / `U3→U202` / `J202→J201` のみ確実に対応が取れたため修正済み。
コンデンサ群（`C101-104`/`C301-302` 対 `C201-C208`）は一意に決まらないため未着手。

**運用ルール:**
- 手編集所有シートへの**ロジック変更**（ネットの追加/変更、部品の追加）は **KiCad側で直接行う**。`wire_circuit_design.py` 側のコードは追随してドキュメント更新するが、それを起点に書き戻さない
- PowerModule の `+12V`/`-12V` → `+15V`/`-15V` 改名と `DKMW20F-12`→`-15` 差替えは、KiCad GUI が無い
  環境だったため**実ファイルの sexpr を直接テキスト編集**して行った（§2.9）。手編集所有シートの本来の
  運用（人が KiCad で触る）からは外れる例外対応。次に KiCad で開いたときに壊れていないか確認すること
- 新しいシートが今後同様に手編集され始めたら、この表に追記して所有権を切り替えること

### 2.9 アーキテクチャ刷新 — `AmpBank` へ統合（2026-09-01 決定）

**RelayBoard（5ch×2枚）と AmpModule（×10枚）を廃止し、10ch 分のアンプと切替を載せた1枚の基板 `AmpBank` へ統合する。** 回路図はまだ着手していない。

#### なぜ

用途は**「常設で10個のオペアンプを切り替えて聴き比べる」**。この目的に照らすと、現行の12枚構成には根拠が無かった。

- 12枚に分かれていたのは v1 の「**既にあるアンプ基板を流用する**」という制約の名残。AudioV2 はアンプ基板を新規設計するので、この理由は消えている
- 「アンプ基板を5枚作る」のは **JLCPCB の最小ロットが5枚**だったから。1種類の基板を5枚もらう仕組みなので、**1枚に統合しても最小ロットは変わらない**（予備が4枚付くだけ）
- 2026-09-01 に検討した問題群は、**すべて「離れた10枚を1本のバスで束ねる」ことに由来**していた

| 問題 | 由来 |
|---|---|
| 非選択アンプの出力がバスにぶら下がる | 出力が箱配線で常時共通。切る手段が基板をまたぐ |
| コイル駆動マージン不足（§2.7-3） | 遠隔基板を +5 V コイルで駆動 |
| 寄生給電・バルクの可否 | 電源を切ることを分離手段にしていた |
| 番地ストラップ・I2C 拡張（§2.6） | 複数のリレー基板を識別する必要 |
| ポップ対策シーケンス・突入電流 | 電源を切替対象にしていた |

1枚に載せると信号がパターンになり、切替素子がオペアンプの直近に来るので、**上記が全部消える**。

#### 決めたこと

| 項目 | 内容 |
|---|---|
| **入力と出力の両方を切る** | 非選択アンプを信号経路から完全に孤立させる。電源状態に依存しない分離 |
| **電源は常時給電** | 出力を切るので電源を切る理由が消える。10台常時でも `DKMW20F-12` 容量の最大24%（静止20 mA/台想定） |
| **切替素子はアナログスイッチ** | 1枚に集約するとリレーは面積を食いすぎる（20個+ドライバ5個で 27.5 cm² 対 8chスイッチIC 5個で 3.0 cm²）。**素子の型番は未定** |
| **制御は SPI デイジーチェーン想定** | Pico から3本で40回路。MCP23017・番地ストラップ・ドライバIC が不要になる |
| **出力カップリング 470 µF → 2.2 µF フィルム** | 負荷 50 kΩ なので -3dB=1.4 Hz で十分（470 µF は 0.0068 Hz と6桁過剰）。面積 24.5→3.6 cm²、信号経路から大容量電解が消える |
| 基板サイズ | 150×100 mm 見込み（DIP-8 ソケット10個が面積の支配要因） |

#### ラッチングリレーを外す判断について

v1 でラッチングを選んだ理由は「**通常リレーはコイル電流を流し続けるのでノイズになる**」。アナログスイッチはコイル自体が無く消費が漏れ電流のみなので、**この要件をより良く満たす**。ラッチングという手段が目的化しないよう明記しておく。

代償は信号経路の直列抵抗。AZ850 の金属接点 50 mΩ（−120 dB）に対し、アナログスイッチは 1.5〜2 Ω（−88 dB）。負荷が 50 kΩ で信号電流が 140 µA と小さいため、Ron による降下は 294 µV に留まる。**実用上まず聴こえない差**と判断した。

#### 廃止・位置づけ変更

- `RelayBoard.kicad_sch` — **廃止**
- `AmpModule.kicad_sch` — **廃止**。10ch 展開して `AmpBank.kicad_sch` へ吸収
- §2.6 番地ストラップ、§2.7-3 コイル駆動マージン検算 — **不採用となった経路の記録**として残す（検算内容自体は正しい）
- ControlPanel → `AmpBank` は I2C（MCP23017、GPIO 10本）+ **±15 V**

#### 確定（2026-09-01）

| 項目 | 決定 |
|---|---|
| 切替素子 | **TI `TMUX7612PWR`**（TSSOP-16、4回路SPST）。1パッケージ = 1ch、制御は GPIO 1本/ch |
| 制御 | 10本 → **MCP23017 が1個**。SPI デイジーチェーンは不要と判断 |
| 電源 | **±15 V（`DKMW20F-15`）へ戻す**。主因は v1 資産との互換（[DECISIONS.md](DECISIONS.md) §8） |
| 入力スイッチ | **オペアンプ + 入力の直前**（高インピーダンス側）。結合 C とバイアス抵抗は全 ch 共通化 |
| 出力スイッチ | 既存の 47 Ω より後。バス容量 265 pF は 47 Ω が隔離（ポール 12 MHz 超）、追加部品不要 |
| BBM | IC 機能は本構成では効かない。**ファームで「全OFF → 待つ → 目標ONの2トランザクション」** |

`TMUX7612` は `ADG1412` とピン互換なので、同じフットプリントで差し替え比較できる（¥1,795）。
制御ピンに内蔵プルダウンがあり、MCP23017 がリセットで Hi-Z のとき自動的に全 OFF になる。

#### 1ch の回路構成（2026-09-01 確定、シミュレーション根拠あり）

```text
TONE_L ─[SW1]─┬─ 220k ─ A_GND          ← プルダウンは SW の「後」
               └─ 100nF ∥ 10µF ─┬─ 1k ─ A_GND
                                  └─ AMP + 入力
                    帰還 Rf/Rg（既定 20k/20k = GAIN 2）
               AMP 出力 ─ 47Ω ─ 2.2µF ─[SW3]─ AMP_SEL_L
```

R 側も同一（`SW2` = R入力、`SW4` = R出力）。**`SEL1`〜`SEL4` を束ねて制御線1本/ch。**

現行 `AmpModule` からの変更は次の2点だけ。入力回路の構造は変えない。

| 変更 | 根拠 |
|---|---|
| 出力カップリング **470 µF → 2.2 µF フィルム** | 負荷 50 kΩ なので -3dB=1.4 Hz で十分。ch 毎に持てる面積になる（3.6 cm²、470 µF なら 24.5 cm² で不可能） |
| 220 kΩ プルダウンを **SW の後ろへ移す** | [spice/ampbank_input_pulldown.cir](spice/README.md)。前に置くと非選択中に結合C左極板が浮き、オフ漏れ電流で充電されて再接続時に段差が出る |

**入力の構造変更（共通バイアス化＋オペアンプ+入力直前で切る）は不要になった。**
あれは ADG1412（Ron 平坦度 0.3 Ω）を前提に検討したもので、1 kΩ 負荷では -70 dB に留まるためだった。
TMUX7612（0.0003 Ω）なら現行構造のまま **-130 dB**。現行構造の方が、非選択時も 1 kΩ が + 入力を
A_GND に固定するので浮かず、入力バイアス電流による DC オフセットも選択・非選択で変わらない（0.2 mV 一定）。

**出力カップリングはスイッチの「前」**（ch 毎に持つ）。
[spice/ampbank_switch_pop.cir](spice/README.md) — 後ろに置いて全 ch 共通1組にすると、
オペアンプ間の DC オフセット差がそのままバスに出る（±3 mV のとき **-6 mV の段差が 150 ms**）。
信号 7 V に対し -61 dB、雑音フロアの約3000倍の低周波過渡で「ボツッ」と聴こえる。

#### シルク印刷（実装時に忘れないこと）

帰還抵抗の倍率表を基板の隅に入れる。Rg を 20 kΩ 固定にし、Rf だけ替える形にする
（替えるのが1本で済む方が実際に触るとき楽なため）。

```text
GAIN = 1 + Rf/Rg     Rf=R705  Rg=R704
 Rf     GAIN    dB
 0R      1.0    0.0    (follower)
 10k     1.5    3.5
 20k     2.0    6.0    <-- default
 39k     3.0    9.4
 62k     4.1   12.3
 82k     5.1   14.2
180k    10.0   20.0
```

#### 部品構成（2026-09-01 確定）

**合計 236 点**（旧構成は 324 点 + PCB 12 枚 + 基板間ケーブル 30 本）。

1ch = **22 点**：`NE5532`（DIP-8 ソケット）1、`TMUX7612` 1、抵抗 10（220k×2 / 1k×2 / 20k×4 / 47R×2）、
コンデンサ 10（入力 100nF film×2・10µF×2、出力 2.2µF film×2、AMP 直近 100nF×2、SW 直近 100nF×2）。

共通部 = **16 点**：`MCP23017`、端子台 3 種（±15V 3P / TONE 2P / AMP_SEL 2P）、I2C ヘッダ 4P、
入口バルク 100µF×2、SW 用 1µF×8（数 IC で共有）、デカップリング 100nF。

**デカップリングは「入口にバルク + 各 IC 直近に 100nF」に変更する。**
旧 `AmpModule` が ch 毎に 100 µF polymer を持っていたのは「1 枚 1 台・ケーブル 1 m の先」
という前提だったため。1 枚に統合すると電源入口から数 cm になるのでその前提が消える。
そのまま 10ch 展開すると 100 µF が 20 個で 25.2 cm² を食うが、入口 2 個なら 2.5 cm²。
信号電流は選択中の 1 台で 0.14 mA、静止電流も 10 台で 80 mA なので入口バルクで足りる。
1 nF C0G は 100nF をピア直近に置けば同等なので省く（必要なら DNP パターンを残す）。

#### シンボル・フットプリントの調査結果（2026-09-01）

**新規作成が必要だったのは `TMUX7612` シンボルの 1 個だけ。** フットプリントは全て標準 lib にあった。

| | 状況 |
|---|---|
| `Amplifier_Operational:NE5532` / `Device:R` / `C` / `C_Polarized` | 標準 lib にあり |
| `Connector:Screw_Terminal_01x02` / `_01x03` / `Conn_01x04_Pin` | あり |
| **`Interface_Expansion:MCP23017x-x-SP`** | あり。**旧回路図の `MCP23017-E/SP` は KiCad 10 で使えない名前**。新シートでは `MCP23017x-x-SP`(DIP-28) か `-SO` を使う |
| `TMUX7612` | **なし → `AudioV2.kicad_sym` に作成済み** |
| フットプリント（TSSOP-16 / DIP-8ソケット / 1206 / フィルムP5 / 端子台 等） | **全て標準 lib にあり** |

#### 実装の進捗

| # | 作業 | 状態 |
|---|---|---|
| 1 | `TMUX7612` シンボル作成 | **完了**（2026-09-01） |
| 2a | `amp_channel_wired()` — 1ch の生成コード | **完了**。ネットリストで設計どおりを確認 |
| 2b | `amp_bank_wired()` — Bank 側（共通部 + 10 インスタンス） | **完了**。全コネクタの接続をネットリストで確認 |
| 3 | `RelayBoard` / `AmpModule` の削除 | **完了**（2026-09-01、`git rm`） |
| 4 | 親から3シートを外して `AmpBank` へ | **完了**。`drift` で親シート一致を確認済み |
| 5 | ネット名 `+15V` / `-15V` へ改名 | **完了**（PowerModule の `DKMW20F-12`→`-15` 差替え含む、全シート） |
| 6 | §2.8 所有権表の更新 | **一部完了**。表は更新済み。旧 `relay_board_wired()`/`amp_module_wired()` 関数本体の削除は未着手（デッドコードのまま残置） |
| 7 | `gen_parts_bom.py` の対象シート差し替え | **完了**。ただし kicad-cli の制約で ch1 代表 + 共通部のみ（×10 の全数展開は不可、PARTS.md に注記） |

**構造:** `AmpChannel` サブシートを 10 回インスタンス化する（`AudioV2Case → AmpBank → AmpChannel ×10`）。
生成コードが書くのは 1ch 分（22点）と Bank 側（16点）だけで、236点を並べるより約6倍簡単。
1ch を直せば 10ch すべてに反映される。全 ch が同一であるべき比較装置の性質とも一致する。

**所有権:** まず `AmpBank` / `AmpChannel` とも**生成コード所有**で起こす。KiCad で手を入れた
時点で手編集所有へ卒業させ §2.8 を更新する。今日 `drift` を作ったので、卒業を記録し忘れても乖離は見える。

#### 生成の検証状況（2026-09-01）

サンドボックスで親に繋いで検証した。**残る ERC は親側の配線が未整備なためのもので、
回路の誤りではないことを実証済み。**

| 検証 | 結果 |
|---|---|
| 全コネクタ（`J_PWR` 3P / `J_TONE` 2P / `J_OUT` 2P / `J_CTRL` 4P） | ネットリストで接続を確認 |
| `SEL_CH1`〜`SEL_CH10` | MCP23017 の GPA0-7 + GPB0-1 から各 ch の SW へ |
| `different_unit_net` 54 件 | 親に繋いで 8 件 → **旧 3 シートを外すと 0 件**。旧 `AmpModule_Reference` の `AMP701` と新 `AmpBank/AmpCh1` の `AMP701` の参照衝突が原因で、回路の誤りではないと確定 |

#### 実装で踏んだ落とし穴（同じ轍を踏まないこと）

- **`NE5532` は `LM2904` を継承**しており、実ピン座標は親側にある。
  unit2 のピン番号は **5/6/7**（1/2/3 ではない）、unit3 の電源ピンは **x=−2.54**（0 ではない）。
  番号直書きをやめ、役割（`out`/`inv`/`nin`/`vp`/`vn`）で引く `ne5532_pin()` にした
- **`sch_helpers.PIN_NUMBERS` への登録が必要**。未登録だと `embed_lib_symbols` が
  シンボルを埋め込まず、KiCad が読めない。`AudioV2:TMUX7612` を追加済み
- **階層ラベルは最初から実ピン先端に置く**。固定座標に浮かせると `label_dangling` になり、
  同名ローカルラベルと「名前だけで繋がっている」脆い状態になる（AmpModule で踏んだのと同じ）
- **`Screw_Terminal_01x0n` のピンは `x=-5.08`（左側）**。`Conn_01x0n_Pin` は `x=+5.08`（右側）で、
  既存の `conn02_pins` / `conn03_pins` は後者用。端子台に使うと 10.16 mm ずれて繋がらない。
  `screw_pins()` を追加した。さらに **`01x02` は pin1 が y=0 で中心対称ではない**ので、
  `(n-1)*1.27` のオフセット計算だと 2 ピンのときだけ 1.27 ずれる
- **共通部とサブシート枠の座標衝突に注意。** MCP23017 の SDA ピンと ch9 の `AMP_SEL_L`
  シートピンが同一座標になり、ネットが融合して `multiple_net_names` が出た。
  共通部はシート群と x 方向で分離して置く
- 単体 ERC の `pin_not_connected` / `isolated_pin_label` / `power_pin_not_driven` は
  **子シートを単体で回したときの副産物**。親に繋げば解消する（`AmpModule` 単体でも 9 件出る）。
  `lib_symbol_issues` は `kicad-cli` が単体シートに対しプロジェクトの `sym-lib-table` を
  読まないための表示で、回路の誤りではない

#### 実装時の作業（旧: 全項目未着手だった時点の記録）

1. ~~`TMUX7612` シンボルの作成~~ → **2026-09-01 完了**。`AudioV2.kicad_sym` に追加済み。
   全16ピンが DS（TSSOP-16）と一致することを検証済み。`kicad-cli sym export svg` も通る。
   フットプリントは **`Package_SO:TSSOP-16_4.4x5mm_P0.65mm` が標準 lib にあり、新規作成は不要**だった
2. ~~`AmpBank.kicad_sch` を新規作成（10ch 分のアンプ + 切替 + MCP23017）~~ →
   **2026-09-01 生成コード完了・検証済み。ただしファイルはリポジトリに未書き込み。**
   `amp_channel_wired()`（1ch）と `amp_bank_wired()`（10ch を階層で構成 + MCP23017 + 各コネクタ）を
   `wire_circuit_design.py` に追加済み。サンドボックスで生成してネットリスト / ERC まで通した
3. `RelayBoard.kicad_sch` / `AmpModule.kicad_sch` を削除
4. 親 `AudioV2Case.kicad_sch` から `RelayBoard_A` / `RelayBoard_B` / `AmpModule_Reference` の
   3シートを外し、`AmpBank` 1枚に置き換える
5. **ネット名 `+12V` / `-12V` → `+15V` / `-15V` へ改名**（親・各シート）
6. `amp_bank_wired()` は**作成済み**。残りは旧 `relay_board_wired()` / `amp_module_wired()` の
   廃止と、§2.8 所有権表の更新
7. `PARTS.md` の生成ブロック（`gen_parts_bom.py`）の対象シートを差し替え

---

### 2.10 PowerModule 絶縁型DC-DCコンバータ — 代替候補調査（2026-09-02、途中・未反映）

**発端:** 現行 `DKMW20F-15`（±15V/±660mA、$30.75/Digikey）が「結構良いお値段」という指摘。
**電圧そのもの（±15V）も固定ではない**とユーザーから明言あり（v1互換という当初理由は
§2.9でRelayBoard/AmpModuleが無くなったことで大部分が失効している）。

**回路図・PARTS.md・DECISIONS.mdへの反映は一切まだ行っていない。** 唯一の実ファイル変更は
`DECISIONS.md` §11.1 に追記した電流マージンの数値根拠（下記）。**次のセッションはここから続行できる。**

#### 判明した実負荷（DECISIONS.md §11.1 に反映済み）

v1時代の見積り（Amp×10+計測+Buffer同居、Icc控えめ8mA/ch）は今のAudioV2には当てはまらない
（計測ADCは別電源系統）。実際にPowerModuleが賄うのは **AmpBank + ControlPanelのLM7809/PT2314系統のみ**。

| レール | 現実的レンジ |
|---|---|
| +15V | ~115〜208mA（AmpBank 80〜150mA + LM7809/PT2314系 ~35mA + スペアナ基盤を乗せるなら+23mA） |
| -15V | ~80〜173mA（AmpBank のみ、+スペアナなら+23mA） |

オペアンプ差し替え最悪ケース（`Audio/AmpModule_OPAMP_REFINE.md` §4.4 実測ベース、10ch異なる型番前提）
では既存想定（20mA/ch）が十分安全側と確認済み。AK05/LC5（最大150mA、実測必須）は1ch挿しなら余裕あり。

#### 検討した候補と実勢価格・仕様（一次資料で検証済み）

| 候補 | 電圧/電流 | 価格（実勢） | Cout上限 | Remote ON/OFF | 備考 |
|---|---|---|---|---|---|
| **DKMW20F-15**（現行） | ±15V/660mA | $30.75(Digikey) | 650µF/rail | R.C.=Open=ON | 余裕最大・実績あり |
| RS6-1215D/1212D（RECOM） | ±15V/200mA・±12V/250mA | $19.04(Digikey) | **660〜900µF**（データシートTable値、確認済み・問題なし） | Open=ON寄り（DKMW20と近い論理、詳細未確認） | Cout・ノイズとも良好 |
| MGW61215/61212（Cosel） | ±15V/200mA・±12V/250mA | ¥1,870（RS Japan品番171-4773/171-5235、正規代理店価格で確認済み。以前提示した$5.92は不正確な集約サイト値だったので訂正済み） | **0-100µF/rail**（Cosel公式Instruction Manual `CME_MG1R5-10.pdf` Table 2.3で実測確認。AmpBank入口100µF+PowerModule直近47µFの合算がこの上限を超える可能性があり要注意） | **Negative logic: L=ON, H=OFF**（現行DKMW20と逆論理、配線変更必須） | 実測リップル&ノイズは5〜15mVと良好（スペック上限120-600mVは保証値で実力はもっと良い）。EMI/EMS全項目Pass（EN55022 ClassA等、マージン25dB以上）。入力側に指定EMIフィルタ部品あり（L1=2.2µH/2600mA等、`mgw61212-en55022.pdf`参照） |
| **Aimtec AM10TW-2415DLPZ**（±15V） | 9-36Vin→±15V/**333mA** | ¥9.98 | **330µF**（データシート`F059e`本文で確認済み・問題なし） | **Open/pulled-high=ON, pulled-low=OFF**（DKMW20F-15と同じ論理。配線変更不要と確認済み） | 10W、87%効率、リップル&ノイズ40typ/85max mVp-p（DKMW20の100mVp-pより良好）、300kHz固定（Coselのような軽負荷間欠動作なし）、絶縁1500VDC/≥1000MΩ/2000pF、24-DIPパッケージ |
| Aimtec AM10TW-2412DLPZ（±12V） | 9-36Vin→±12V/**416mA** | ¥9.98 | **470µF** | 同上 | 同上シリーズ。電流・Cout ともさらに余裕 |
| Aimtec AM10GH-2415DLPZ | 9-36Vin→±15V/333mA | ¥8.80 | 未確認（8-SIP、保護機能はAM10TWよりやや少ない：OVP+SCPのみ） | 未確認 | AM10TWで代替十分ならこちらは調査不要 |
| Aimtec AM3G-1215DLPZ | 9-18Vin→±15V/100mA | ¥5.85 | 未確認 | 未確認 | 3W、DKMW20より電流余裕が少ない。優先度低 |

**AM10TW-2415DLPZ/2412DLPZ が最有力候補として確定的。** DKMW20F-15の懸念（コスト）とCoselの懸念
（Cout制限0-100µF・Remote配線変更必須）を**両方解消**。価格・電流余裕（330-416mA）・Cout（330-470µF）・
配線互換性（Open=ON同一）のすべてで現行より優れるか同等。**±12V/±15Vのどちらもラインナップにあるため、
電圧の最終判断（v1互換という当初理由は失効済み、純粋にコスト/性能で選べる）は依然オープン。**

**入手経路:** [`AudioV2/dc_dc.csv`](dc_dc.csv) — DigiKeyの実フィルタ済みエクスポート
（絶縁型・出力±12V/±15V、79件）。データシート: `https://aimtec.com/site/Aimtec/files/Datasheet/HighResolution/AM10TW-LPZ.pdf`
（`F059e – 01apr2024 R0`、pdfplumberで全文抽出済み・信頼できる一次資料）。

#### 次にやること（優先順）

1. **±12V か ±15V かを確定**（AM10TWは両方あるので、あとは純粋な電圧選定の意思決定のみ）
2. シンボル・フットプリントの要否確認（Aimtec AM10TW-LPZ、24-DIPパッケージ。KiCad標準libに無い可能性が高く新規作成が要る）
3. `PowerModule.kicad_sch`（手編集所有）の部品差し替え・ネット名調整
4. `power_module_wired()`（生成コード、ドキュメント用途）も追随
5. 検証: `check_sexpr` / ERC / netlist / drift
6. （任意）AM10TW-LPZ に明示的なEMI/EMC試験報告書があるか確認（Coselでは別PDFで確認できたが、AM10TWは未確認）

#### この調査で得た副産物

- PDFデータシートの自動テキスト抽出: `WebFetch`が失敗する場合、生バイナリを保存の上
  ①crude zlib-stream展開（`re.finditer(rb'stream...endstream')`+`zlib.decompress`）を試し、
  ②それでも0件なら`pdfplumber`（`pip install pdfplumber`、本セッションで導入済み）を使うと高確率で成功する
  （Cosel `SFE_MG1R5-10.pdf`はcrude法で成功、`CME_MG1R5-10.pdf`はcrude法が0件でpdfplumberが成功、
  という実例あり。PDF生成ツールの違いで内部構造が変わるため両方試す価値がある）
- DigiKeyの「フィルタ済みURL」はGoogle広告経由などで来ると**フィルタが反映されないことがある**
  （今回92,861件の未フィルタ状態だった）。信頼できるのはCSVエクスポートかUI操作での再現のみ

---

## 3. マージ済み PR（このスレッドで扱った範囲）

| PR | 内容 | 状態 |
|---|---|---|
| #22–#28 | 手回し音量〜ラベル結線〜WP-C salvage | 上記履歴どおり。**#27/#28 MERGED** |

### 再発防止

- **禁止:** `generate_kicad_scaffold.py` 再実行。再生成は `wire_circuit_design.py`
- 親シート: 同名シートピンはローカルラベルで橋渡し
- sexpr 編集後は `python3 Audio/scripts/check_sexpr.py -q AudioV2`

---

## 4. 現状の git / 作業ツリー

作業ブランチは **`main`**。§2.9 手順3〜5とKiCad正規化はそれぞれ commit 済み・push 済み
（`ca0af51` AmpBank統合・+15V改名、`f04f0ad` KiCad正規化）。このメモの更新時点でさらに
未コミット分あり（AmpCh2手直しに伴う所有権変更・DECISIONS.md §11.1・PROCUREMENT.xlsx・
dc_dc.csv・本メモ自体）→ このセッションの最後にまとめてコミット・push する。

**未確認の副産物:** `AudioV2Case.kicad_pcb` が untracked で出現している（91行・部品0〜1個程度の
ごく小さいファイル）。KiCadでPCBエディタを開いた際の空スキャフォールドと思われるが、
実際にPCBレイアウト着手の意図があるものか未確認。**次のセッションでユーザーに確認してから
git add するか判断すること**（AGENT_HANDOFF は「PCB未設計」と各所に書いているため、
着手済みなら§2.9等の記述更新が必要になる）。

履歴ブランチ（`cursor/audiov2-*` 等）は base にしない。クラウドが古い `branchName` を fetch して落ちることがある → tip が必要なら一時復帰のみ。

---

## 5. 回路の完成度

### できている

- Power: PD モジュール入・DKMW20F-15・7809・端子台3種（§2.1、Value は `+15/-15/A_GND out` に改名済み）・パネル SW ループ（論理）
- Control: パネル PWR SW（`PD_12V` → `PD_12V_SW`）＋ 12 V パネル LED（`PD_12V_SW` → `PD_GND`。SW 後に入れてあるので通電表示になる）、PT2314 / Pico / ENC 等。`+15V`/`-15V` へ改名済み
- Output / ラベル結線素案（#27）
- `AmpBank`（10ch 統合、TMUX7612 切替、常時給電、±15V）。**リポジトリに存在し、親に配線済み。PCB は未設計**（§2.9）
- 旧 AmpModule / RelayBoard は **削除済み**（§2.9 手順3〜5完了）

### 未着手・優先候補

1. ERC 60 件の仕分け（純増10件は AmpBank 各chの `ground_pin_not_ground` — TMUX7612 VSS=-15V の既知誤検知。残りは元々あった ControlPanel 未接続ピン等、下記2と重複）
2. **ControlPanel 未接続ピンの整理**（Pico 未使用GPIO、PT2314 未使用入力。§2.9以前からの既知事項）
3. `WIRING.md` 全面書き換え（RelayBoard 前提の箱配線記述が残っている。冒頭に注意書きを追記済みだが本文は未更新）／`CIRCUIT_DESIGN.md` §5・`DECISIONS.md` の語彙をネット名ベースへ書き換え（SOURCE_OF_TRUTH.md §3）
4. PD 往復端子（A のままなら Power↔Panel 用コネクタ追加）or トポロジ B への図変更
5. OLED FP、PT2314 未使用入力
6. ControlPanel 側 I2C/電源コネクタ（5P: `I2C_SDA`/`I2C_SCL`/`3V3`/`+5V`/`D_GND`）の物理実装（フェルール/スプリッタ分岐）
7. `PowerModule` の生成コードが現図より1世代古い（PD 前段のみ。`+15V`/`-15V` 改名は反映済み。`drift` で検出済み。手編集所有なので実害は無いが要追従）
8. `relay_board_wired()` / `amp_module_wired()` デッドコードの削除（§2.8）
9. `PARTS.md` §4.2「選定・実装メモ」の AmpBank 実態への書き換え（TODO 注記のみ済み）

### 検証

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
docker/kicad-cloud-build/kicad-run.sh erc      # AudioV2 全体の ERC
docker/kicad-cloud-build/kicad-run.sh netlist  # ネットリスト
docker/kicad-cloud-build/kicad-run.sh drift    # 生成コード所有シートと現図の差分
python3 AudioV2/scripts/gen_parts_bom.py --check   # PARTS.md の BOM ブロック
```

`kicad-run.sh` は Docker イメージ `kicad-cloud:10.0.6` があればそれを、無ければホストの
`kicad-cli` を使う。出力は `out/`（gitignore 済み）。

**2026-09-01 §2.9 手順3〜5 完了時点の値**（このローカル Windows 環境で実測。次回はここから増減を見る）:
`check_sexpr` 10ファイル / 問題0、ERC **60件**（うち新規10件は AmpBank VSS 警告の既知誤検知）、
`drift` 生成コード所有 4/4（AmpBank/AmpChannel/Control/親）一致・手編集所有2件は既知差分のみ、
`gen_parts_bom --check` rc=0。

**この環境固有の前提**（他マシンでは不要な場合あり）:
- `C:\tmp\kicad-symbols` → KiCad の `share/kicad/symbols` へのディレクトリジャンクション
  （`sch_helpers.py` のピン数ルックアップに必要。無いと `wire_circuit_design.py` が
  `FileNotFoundError` で落ちる）
- `kicad-run.sh` に `PYTHONUTF8=1` を追加済み（Windows コンソールの cp932 が `drift` の
  UTF-8 出力でクラッシュするため）

Windows: Git Bash + KiCad CLI（`.cursor/rules/kicad-cli-git-bash.mdc`）。

---

## 6. 会話タイムライン要約（追記）

…（〜08-30: ラベル結線・アノテ・クラウド切替）

11. Power をラベル→ワイヤへ整理。−12 レールのデカップリングと 7809 出力側コンデンサを追加
12. Case=論理、SW/Volume 実体は子シート。SW/LED を一度 Power に寄せ→**Control に戻す**
13. 外付け 50224 前提。`PD module in` / `VCC_TONE OUT` の2端子台を新設。R.C. 明示 NC
14. PD 入口 A vs B・往復端子の議論 → **一旦終了**（図は A）
15. 本メモ更新 → `main` に commit/push（クラウド同期用）
16. 手持ちオペアンプリストを `Audio/OPAMP_INVENTORY.md` に登録
17. AmpModuleを高速石対応で再版。代表1シートを親へ統合し、独立PCBを×10仕様で生成
18. RelayBoard本配線。未給電Ampへの信号印加を避け、audio入力＋±12 Vを同時切替。全体ERC 207→66
19. 番地ストラップを `SolderJumper` → **0 Ω / 1206** に変更（§2.6）。入口パスコン 100 nF ×2 は I2C/電源コネクタ側、ストラップは MCP23017 脇へ。レビュー指摘を §2.7 に記録。全体ERC 56（Relay 0）
20. `kicad-run.sh` / `sch_drift.py` / `gen_parts_bom.py` を整備。再アノテーションで58参照が変化したのを受け、**「回路図から導出できる情報は文書に書かない」方針**を `SOURCE_OF_TRUTH.md` に制定（Cursor / Claude 双方から読める形に）
21. AZ850 のコイル駆動マージンをデータシートで検算 → **仕様割れ**（§2.7-3）。原因は Darlington の約1 V ドロップが 5 V レールの2割を食うこと
22. v1 の Pico 制御プログラムとガーバーを確認。「v1 にバルクコンデンサは無かった」というユーザーの指摘が正しいことを git ログで確認（schematic には `e1f965e` で入ったが基板には届いていない）
23. 「電源も切替える」構造が諸問題（突入電流・スタック枚数・寄生）の根であると特定 → **アーキテクチャ刷新を決定**（§2.9）。10ch を1枚に統合、切替は TMUX7612、電源は常時給電、レールは ±15 V
24. `TMUX7612` シンボル作成、`AmpChannel` / `AmpBank` の生成コードを実装しサンドボックスで検証。カップリング位置とプルダウン位置は ngspice で決めた（`AudioV2/spice/`）。`1d42401` を push
25. §2.9 手順3〜5実施（ローカル Windows 環境、このセッション）: `RelayBoard.kicad_sch`/`AmpModule.kicad_sch` を削除、`wire_circuit_design.py` に `channel`/`bank` ターゲットを追加して `AmpBank.kicad_sch`/`AmpChannel.kicad_sch` を生成、親を差し替え、`+12V`/`-12V` → `+15V`/`-15V` へ全シート改名。PowerModule は手編集所有だが KiCad GUI が無い環境のため sexpr 直接編集で `DKMW20F-12`→`-15` を差替え（v1 `Audio/DKMW20.kicad_sym` から移植）。副産物として Windows 固有の環境不備を2件発見・修正（`KICAD_SYM_ROOT` 用ジャンクション、`kicad-run.sh` の `PYTHONUTF8=1`）。ERC 47→60件（新規はAmpBankのVSS警告10件、既知）。`gen_parts_bom.py` を `AmpBank.kicad_sch` 対象へ切替（ch1代表+共通部の制約を注記）。未コミット

---

## 7. 別チャット再開プロンプト（コピペ用）

```
AudioV2/AGENT_HANDOFF.md を読んで続きから。ブランチは main（origin と同期済み、HEAD 1c9a359）。
**作業ツリーは dirty — §2.9 手順3〜5の変更が未コミット。まずコミットするか確認すること。**

§2.9（RelayBoard+AmpModule → AmpBank 1枚統合）の手順3〜5が完了:
- RelayBoard.kicad_sch / AmpModule.kicad_sch を削除
- AmpBank.kicad_sch / AmpChannel.kicad_sch を生成しリポジトリに追加
  （wire_circuit_design.py に "channel"/"bank" ターゲットを追加）
- 親 AudioV2Case.kicad_sch を AmpBank 1枚に差し替え
- +12V/-12V → +15V/-15V に全シート改名。PowerModule の DKMW20F-12 → -15 差替え含む
  （PowerModule は手編集所有だが KiCad GUI 環境が無かったため sexpr 直接編集。
  次に KiCad で開いたとき壊れていないか確認すること）

残っている作業:
- §2.8 所有権表は更新済みだが、relay_board_wired()/amp_module_wired() のデッドコードは未削除
- WIRING.md（全面）/ CIRCUIT_DESIGN.md §5 / DECISIONS.md の RelayBoard・AmpModule 前提の
  記述はまだ書き換えていない（重要箇所に注意書きのみ追記済み）
- PARTS.md §4.2「選定・実装メモ」も AmpBank の実態に未更新（TODO注記のみ）
- ERC 60件の仕分け（新規10件はAmpBank各chのground_pin_not_ground、TMUX7612 VSS=-15Vの既知誤検知）

検証は docker/kicad-cloud-build/kicad-run.sh の erc / netlist / drift と
python3 Audio/scripts/check_sexpr.py -q AudioV2、python3 AudioV2/scripts/gen_parts_bom.py --check。
このローカル Windows 環境固有の前提: C:\tmp\kicad-symbols が KiCad の
share/kicad/symbols へのジャンクションとして必要（無いと wire_circuit_design.py が落ちる）。
kicad-run.sh には PYTHONUTF8=1 を追加済み（Windows コンソールの cp932 対策）。
今回時点の値: check_sexpr 10ファイル/0、ERC 60件、drift 生成コード所有4/4一致、BOM check rc=0。

I2C/電源はスター確定。端子台は Phoenix MKDS-1,5 系（v1 と同一/互換）。
A_GND/D_GND の NetTie は ControlPanel 側（Pico 直近）1点。
generate_kicad_scaffold.py は再実行しない。手編集所有シート（§2.8、Power/Output）は機械的に上書きしない。
文書は designator でなくネット名・機能名で書く（SOURCE_OF_TRUTH.md §3）。
§2.9 末尾の「実装で踏んだ落とし穴」は必ず読むこと（NE5532 のピン番号、Screw_Terminal の x 座標、
PIN_NUMBERS 登録漏れ、座標衝突など、同じ轍を踏みやすい）。
```

---

## 8. 触ってよい／だめ

| OK | NG |
|---|---|
| `AudioV2/**` の sch / スクリプト / 文書 | `Audio/` 既存製造図の無闇な改変 |
| `wire_circuit_design.py` での再生成（**手編集所有シートは除く**、§2.8） | `generate_kicad_scaffold.py` 再実行 |
| RelayBoardのロジック変更を **KiCad側で直接** 行う | RelayBoardを `wire_circuit_design.py relay --force-relay` で機械的に上書き |
| sexpr 編集後は必ず `check_sexpr.py` | `--no-verify` でコミット |
| 新規作業は **`main`** | 旧 `cursor/audiov2-*` を base |
| `AmpBank` の生成コードを直す（§2.9） | 旧シート削除・親の差し替え（§2.9 手順3〜7）を**合意なしで**実行 |

---

## 9. 変更履歴（このメモ）

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — クラウド／ローカル会話の長期記憶化 |
| 2026-08-31 | Power 端子・SW 配置・PD A/B・VCC_TONE/GND 方針を追記 |
| 2026-08-31 | 手持ちオペアンプ在庫 → `Audio/OPAMP_INVENTORY.md` |
| 2026-08-31 | AmpModule再版 — 高速石対応、独立PCB、親代表1シート、×10 |
| 2026-08-31 | RelayBoard本配線 — 5ch×2、入力＋電源連動、各インスタンスERC 0 |
| 2026-08-31 | 番地ストラップ 0 Ω/1206 化（§2.6）＋レビュー指摘の記録（§2.7）。スクリプト非同期の警告あり |
| 2026-08-31 | `wire_circuit_design.py` に `relay` 書き込みの安全装置（`--force-relay` 必須化）を追加。`work-on-main.mdc` にも注記（§2.6） |
| 2026-08-31 | `wire_circuit_design.py` の `addr_strap`/`C301`/`C302`/`J_I2C`（スクリプト内識別子）と階層ラベルを現図の座標へコード同期（§2.6）。`ADDR_A0`/`ADDR_A1` ラベルも復活（§2.7-1）。実機（KiCad）未検証のため安全装置は解除せず |
| 2026-09-01 | 再アノテーションで58参照が変更。`AmpModule.kicad_pcb` と `build_amp_pcb.py` を削除し **PCB を未設計扱いに戻した**（§2.5）。Power / Output を手編集所有へ移動（§2.8）。`kicad-run.sh` に `drift` 追加、`PARTS.md` の部品表を BOM 生成化 |
| 2026-08-31 | シート所有権モデル（§2.8）を制定。RelayBoardを手編集所有に |
| 2026-08-31 | ControlPanel↔RelayBoardのI2C/電源をスター確定（daisy不採用）。WIRING.md / DECISIONS.md 更新。実装（ControlPanel側コネクタ、フェルール/スプリッタ分岐）は未着手 |
| 2026-09-01 | `SOURCE_OF_TRUTH.md` を制定（回路図から導出できる情報は文書に書かない）。`kicad-run.sh` / `sch_drift.py` / `gen_parts_bom.py` を整備 |
| 2026-09-01 | AZ850 コイル駆動マージンの検算 → 仕様割れを記録（§2.7-3、不採用経路） |
| 2026-09-01 | **アーキテクチャ刷新を決定（§2.9）** — RelayBoard + AmpModule を `AmpBank` 1枚へ統合。TMUX7612 / 常時給電 / ±15 V |
| 2026-09-01 | `TMUX7612` シンボルと `AmpChannel` / `AmpBank` 生成コードを追加（サンドボックス検証済み、回路図ファイルは未書き込み）。`1d42401` を push。§1 / §5 / §7 を現状に合わせて更新 |
| 2026-08-31 | `amp_module_wired()`を信号順配線に修正（OpAmpユニット配置入れ替え＋入出力バス配線）。コード変更のみ、`AmpModule.kicad_sch`の再生成・KiCad検証は未実施（§2.5） |
| 2026-08-31 | ユーザーがローカルKiCadでRelayBoardのAZ850リレー10個を270°回転＋チャンネル間隔拡張、配線・ラベルを追従修正（main直push）。取り込み確認し、addr strap同期は無傷と確認 |
| 2026-08-31 | A_GND/D_GND NetTie位置を確定: **ControlPanelのPico直近**（D_GNDの発生源）。RelayBoardは両ネットを受け取るが結合しない、とWIRING.md/DECISIONS.mdを訂正（従来「RelayBoardで結合」と誤読していた） |
| 2026-08-31 | 手持ちオペアンプに **MUSE03**（2石→DIP化・2ch変換基板）を追記。DS PDF も `Audio/datasheets/opamps/` に追加 |
| 2026-08-31 | MUSE03 の DS 要点・製品ページ・REFINE 表への参照を追加 |
| 2026-09-01 | 再アノテーション（58件）を受け、本メモと `WIRING.md` の記述を designator ベースから**ネット名・機能名（回路図 Value）ベース**へ改訂（[`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §3）。番地ストラップ表（§2.6）・シート所有権と参照対応（§2.8）・生成スクリプト内の識別子は「参照が主題そのもの」なので意図的に残した |
| 2026-09-01 | **§2.9 手順3〜5 実施**（ローカル Windows、このセッション）。`RelayBoard.kicad_sch`/`AmpModule.kicad_sch` 削除、`AmpBank.kicad_sch`/`AmpChannel.kicad_sch` を生成しコミット対象に追加、親を差し替え、`+12V`/`-12V`→`+15V`/`-15V` を全シート改名（`DKMW20F-15` シンボルを v1 `Audio/DKMW20.kicad_sym` から移植し `PowerModule.kicad_sch` の部品を差替え）。`gen_parts_bom.py` の対象を `AmpBank.kicad_sch` へ切替（kicad-cli の制約で ch1代表+共通部のみ出力される旨を注記）。副産物としてこの Windows 環境の不備を2件修正: `sch_helpers.py` の `KICAD_SYM_ROOT` 用に `C:\tmp\kicad-symbols` ジャンクションを作成、`kicad-run.sh`/`gen_parts_bom.py` に UTF-8 まわりの修正（`§2.8`表記の§記号がsedのマルチバイト処理を壊していた点をASCII化、`PYTHONUTF8=1`追加）。§2.8所有権表・§1/§4/§5/§7を現状に更新。CIRCUIT_DESIGN.md/PARTS.md/WIRING.mdの一部記述にも「旧アーキテクチャの記録」フラグを追記（全面書き換えは未着手）。**作業ツリーは未コミット** |
| 2026-09-02 | ユーザーが `AmpCh2` を KiCad で手直し → `AmpBank`/`AmpChannel` を手編集所有へ卒業（`wire_circuit_design.py` の `HAND_EDITED`/`GENERATED` 更新、`drift` で確認）。バルクコンデンサ周りの未接続配線1件を発見・ユーザーが修正、ERC 60件に復帰。C_BULK_P/N・MCP23017 A0-A2=D_GND を実配線で検証。PROCUREMENT.xlsx（AudioV2全体の発注リスト）を新規作成。PowerModule の絶縁型DC-DCコンバータ（DKMW20F-15、$30.75）のコスト代替調査を開始（§2.10、途中・未反映。DigiKeyフィルタ済みCSVを `dc_dc.csv` として追加） |
| 2026-09-02 | §2.10継続: `AudioV2Case.kicad_pcb`（空スキャフォールド）をコミット。Aimtec `AM10TW-LPZ` データシートを一次資料で確認し、**Cout上限（±15V品330µF・±12V品470µF）とRemote ON/OFF論理（Open/pulled-high=ON、DKMW20F-15と同一）の両方が問題ないと確定**。§2.10の候補比較表・次のアクションを更新（残るは電圧確定のみ） |
