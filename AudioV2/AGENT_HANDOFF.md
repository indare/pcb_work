# AudioV2 エージェント引き継ぎメモ

**更新:** 2026-09-01（ローカル `DESK01`）  
**目的:** クラウド↔ローカル切替で会話 UI が分岐／短く見えることがあるため、別チャットからでも再開できるようにする。  
**作業の正:** 常に git ブランチ **`main`**（歴史的な `cursor/audiov2-*` 等は base にしない）。

関連:

- ルール: `.cursor/rules/work-on-main.mdc`
- ローカル会話: [Power/PD 整理系](37c7411c-c7bb-4644-9194-686ff5fe1fd5)

---

## 1. いま何をしているか（一言）

**AudioV2 AmpModuleを回路図として再版し、親へ代表1シートで統合した。PCB は未設計（§2.5）。**
ゲイン2（20k/20k）、±12 V、100 µF/rail + 100 nF + 1 nF、DIP-8ソケット。物理は×10製造。
RelayBoardは5ch×2枚の入力＋電源連動配線まで完了し、両インスタンスERC 0件。
番地ストラップは 0 Ω/1206（§2.6）。`wire_circuit_design.py` はRelayBoard/AmpModule双方とも現図へコード同期済みだが**実機KiCad検証は未実施**。RelayBoardは「手編集所有」（§2.8）に切替済みで、`--force-relay` なしでは書き込まない安全装置あり。ユーザーがローカルKiCadでRelayBoardのAZ850×10を270°回転＋チャンネル間隔拡張し、配線も追従済み（`main`にpush済み、addr strap等は無傷と確認済み）。

I2C/電源トポロジは**スター確定**（daisy不採用、§WIRING.md）。端子台はv1 `Audio/Controll.kicad_sch`と同じPhoenix MKDS-1,5系。A_GND/D_GNDのNetTieは**ControlPanel側**（Pico直近）に1点、RelayBoardでは結合しない、と確定（WIRING.md）。

**KiCad 10.0.6をクラウド環境にビルド中/ビルド済み**（別セッション `session_01XMzAwTNj2AzF2SjKNLmC32`、ブランチ`claude/kicad-cloud-build-env-2jgp6g`、Docker）。このセッション（会話の続き）からは直接メッセージを送れないので、そちらを開いて`main`を取り込ませ、`wire_circuit_design.py amp`/`relay --force-relay`の実行検証を依頼する必要がある。

**要対処（設計上の実害）: コイル駆動マージンが仕様割れ（§2.7-3）。40 ℃ 超で Must Operate を満たさない。** 対策候補は `TBD62083APG` へのドロップイン差替（検算・DS確認済み）。

次の話題候補: 上記KiCad実機検証、Relayレビュー指摘（§2.7）、Control未接続、親の箱外dangling label整理、ControlPanel側 I2C/電源コネクタ（5P: `I2C_SDA`/`I2C_SCL`/`3V3`/`+5V`/`D_GND`）の物理実装（フェルール/スプリッタ分岐）。

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
| Output / Amp | Outputは`SW_SP3T`×2。Ampは代表1シート、同一仕様×10を製造（PCB は未設計） |

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

### 2.6 RelayBoard 番地ストラップ（2026-08-31 更新）

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

### 2.7 RelayBoard レビュー指摘（2026-08-31、いずれも接続ミスではない。未対応）

1. **A0/A1 ネットが無名** — MCP23017 の A0/A1 に付くネットに名前が無く、KiCad が参照から自動生成した名前（`Net-(U302-A0)` 形式）になっている。`ADDR_A0`/`ADDR_A1` ラベルを戻すとネットリスト差分と ERC ログが読みやすい。**自動生成名は参照を含むので、再アノテーションのたびにネット名まで動く**（＝ `SOURCE_OF_TRUTH.md` §3 の語彙ルールが効かない状態）のも名前を付けたい理由。**→ `wire_circuit_design.py` のスクリプト同期（§2.6）でラベルを復活させた。`--force-relay` で実図に反映するまでは無名のまま**
2. **IC 直近パスコン不足** — 既存の 100 nF ×2 は方針どおり I2C/電源コネクタ入口（`3V3` 側・`+5V` 側）に置いてある。別途 MCP23017 の 9/10 ピン間、ULN2803A 2個の 10/9 ピン間に 100 nF が欲しい。`+5V` はリレーパルスが乗るので、リレー群近傍にバルク 100–220 µF も検討
3. **コイル駆動マージン不足 — 仕様上アウト（2026-09-01 検算済み・要対処）**

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
| **生成コード所有** | `wire_circuit_design.py <target>` を回せばそのまま正 | Amp, Control, 親 |
| **手編集所有** | KiCad上の手編集が正。生成コードはロジック（ネット/ピン対応）のドキュメントとして残すが、機械的に上書きしてはいけない | **RelayBoard**（2026-08-31〜）, **Power**（2026-09-01〜）, **Output**（2026-09-01〜） |

**2026-09-01 の実測による更新:** サンドボックスで `all --force-relay` を再生成して実図と突き合わせたところ、Power と Output は「回せばそのまま正」ではなかったため所有権を移した。

| シート | 再生成 vs 実図 |
|---|---|
| Amp / Control / 親 | ✅ 参照・値とも完全一致。Amp は座標が2件相違していた（`AMP701` のユニット入れ替えが未再生成、§2.5）が 2026-09-01 に再生成して解消済み |
| RelayBoard | 参照・値は一致するが座標24個が相違（手調整レイアウト。所有権は従来どおり手編集） |
| **Output** | Amp 共通ハーネス受けの `RAIL IN` 端子台（3P: `AMP_SEL_L` / `A_GND` / `AMP_SEL_R`）が生成されない。部品5個の座標も相違 |
| **Power** | **一世代古い。** 生成側は USB-C + CH224 の PD 前段（スクリプト内の `J1`/`U2`/`J_PD`）を出すが、実図は PD モジュール外付け（`PD module in` / `VCC_TONE OUT` 端子台、§2.1）。コンデンサも生成6個 対 実図8個 |

**参照の対応表（生成スクリプト側 → 実図）:** ここは参照そのものが主題なので designator で書く。
Power は `F1→F201` / `U1→U201` / `U3→U202` / `J202→J201` のみ確実に対応が取れたため修正済み。
コンデンサ群（`C101-104`/`C301-302` 対 `C201-C208`）は一意に決まらないため未着手。

**運用ルール:**
- 手編集所有シートへの**ロジック変更**（ネットの追加/変更、部品の追加）は **KiCad側で直接行う**。`wire_circuit_design.py` 側のコードは追随してドキュメント更新するが、それを起点に書き戻さない
- `relay` への書き込みはデフォルトで無効（§2.6 安全装置）。`--force-relay` は「シートを丸ごと作り直す」ときだけの脱出ハッチで、通常運用では使わない
- 新しいシートが今後同様に手編集され始めたら、この表に追記して所有権を切り替えること

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

作業ブランチは **`main`**。クラウド切替前に **push して origin/main と揃える**こと。

履歴ブランチ（`cursor/audiov2-*` 等）は base にしない。クラウドが古い `branchName` を fetch して落ちることがある → tip が必要なら一時復帰のみ。

---

## 5. 回路の完成度

### できている

- Power: PD モジュール入・DKMW・7809・端子台3種（§2.1）・パネル SW ループ（論理）
- Control: パネル PWR SW（`PD_12V` → `PD_12V_SW`）＋ 12 V パネル LED（`PD_12V_SW` → `PD_GND`。SW 後に入れてあるので通電表示になる）、PT2314 / Pico / ENC 等
- Output / ラベル結線素案（#27）
- AmpModule回路図、代表親シート（×10）。**PCB は未設計**（§2.5）
- RelayBoard本配線: 各盤MCP23017×1、ULN2803×2、AZ850×10。Amp入力＋±12 Vを同時切替。番地はJP A1/A0で0x20–0x23（最大4枚）

### 未着手・優先候補

1. **`wire_circuit_design.py relay --force-relay` をKiCadのあるマシンで実行し、netlist/ERCで検証** — コード上の同期（§2.6）は完了。実行検証と `check_sexpr.py` 通過確認が残作業
2. **RelayBoard レビュー指摘の消化**（§2.7）— 特に 3 の AZ850 set voltage 実測確認
3. PD 往復端子（A のままなら Power↔Panel 用コネクタ追加）or トポロジ B への図変更
4. **ControlPanel未接続ピンの整理**
5. ERC 残り（Relay/Amp/Power/Outputは0件。Control 32件＋親の箱外ラベルが主）
6. OLED FP、PT2314 未使用入力
7. RelayBoard PCB時: 番地ストラップ横の F.Silk に番地早見表（0x20–0x23）。FP は RelayBoard 全体で未割当（MCP23017 含む）

### 検証

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
cd AudioV2 && kicad-cli sch export netlist -o /tmp/audiov2.net AudioV2Case.kicad_sch
```

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

---

## 7. 別チャット再開プロンプト（コピペ用）

```
AudioV2/AGENT_HANDOFF.md を読んで続きから。
ブランチは main（origin と同期済み前提）。
AmpModuleは代表1シート（同一仕様×10を製造）。ゲイン2、±12 V、バルク/1nF対応済み。**PCB は未設計**（2026-09-01 に削除、§2.5）。
RelayBoardは入力＋電源連動、各盤MCP×1/ULN×2/AZ850×10、ERC 0。AZ850は270°回転済み（ユーザーがKiCadで手編集、main反映済み）。
番地ストラップは0Ω/1206（§2.6）、ストラップ・I2C/電源コネクタ入口パスコン・階層ラベルはwire_circuit_design.pyへコード同期済みだが実機未検証（§2.6）。
AmpModuleも信号順配線をコードに追加済みだが同様に実機未検証（§2.5）。
RelayBoardは「手編集所有」（§2.8）。I2C/電源はスター確定、端子台はPhoenix MKDS-1,5系（v1と同一/互換）。
A_GND/D_GNDのNetTieはControlPanel側（Pico直近）1点、RelayBoardでは結合しない。
KiCad 10.0.6クラウド環境が別セッション（claude/kicad-cloud-build-env-2jgp6gブランチ）でビルド済み/ビルド中 — そこにmainを取り込ませてwire_circuit_design.py amp / relay --force-relayの実行検証を依頼するのが次の一歩。
レビュー指摘は §2.7 に未対応で置いてある。
次候補: 上記KiCad実機検証 / Relayレビュー指摘 / Control未接続 / 親の箱外dangling label整理 / ControlPanel側 I2C/電源コネクタ（5P）実装。
generate_kicad_scaffold.py は再実行しない。wire_circuit_design.py relay/ampは実機検証後にのみ書き込み確認すること（relayは--force-relay必須）。
文書は designator でなくネット名・機能名で書く（SOURCE_OF_TRUTH.md §3）。参照が主題の箇所（番地ストラップ表・所有権/参照対応・スクリプト内識別子）だけ例外。
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
| 2026-08-31 | `amp_module_wired()`を信号順配線に修正（OpAmpユニット配置入れ替え＋入出力バス配線）。コード変更のみ、`AmpModule.kicad_sch`の再生成・KiCad検証は未実施（§2.5） |
| 2026-08-31 | ユーザーがローカルKiCadでRelayBoardのAZ850リレー10個を270°回転＋チャンネル間隔拡張、配線・ラベルを追従修正（main直push）。取り込み確認し、addr strap同期は無傷と確認 |
| 2026-08-31 | A_GND/D_GND NetTie位置を確定: **ControlPanelのPico直近**（D_GNDの発生源）。RelayBoardは両ネットを受け取るが結合しない、とWIRING.md/DECISIONS.mdを訂正（従来「RelayBoardで結合」と誤読していた） |
| 2026-08-31 | 手持ちオペアンプに **MUSE03**（2石→DIP化・2ch変換基板）を追記。DS PDF も `Audio/datasheets/opamps/` に追加 |
| 2026-08-31 | MUSE03 の DS 要点・製品ページ・REFINE 表への参照を追加 |
| 2026-09-01 | 再アノテーション（58件）を受け、本メモと `WIRING.md` の記述を designator ベースから**ネット名・機能名（回路図 Value）ベース**へ改訂（[`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §3）。番地ストラップ表（§2.6）・シート所有権と参照対応（§2.8）・生成スクリプト内の識別子は「参照が主題そのもの」なので意図的に残した |
