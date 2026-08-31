# AudioV2 エージェント引き継ぎメモ

**更新:** 2026-08-31（ローカル `DESK01`）  
**目的:** クラウド↔ローカル切替で会話 UI が分岐／短く見えることがあるため、別チャットからでも再開できるようにする。  
**作業の正:** 常に git ブランチ **`main`**（歴史的な `cursor/audiov2-*` 等は base にしない）。

関連:

- ルール: `.cursor/rules/work-on-main.mdc`
- ローカル会話: [Power/PD 整理系](37c7411c-c7bb-4644-9194-686ff5fe1fd5)

---

## 1. いま何をしているか（一言）

**AudioV2 AmpModuleを回路図・独立PCBとして再版し、親へ代表1シートで統合した。**
ゲイン2（20k/20k）、±12 V、100 µF/rail + 100 nF + 1 nF、DIP-8ソケット。物理は×10製造。
RelayBoardは5ch×2枚の入力＋電源連動配線まで完了し、両インスタンスERC 0件。
番地ストラップは 0 Ω/1206（§2.6）。**`wire_circuit_design.py relay` はスクリプト同期まで回さない。**
次の話題候補: Relayレビュー指摘（§2.7）、Control未接続、親の箱外dangling label整理。

---

## 2. 設計の確定事項（忘れないこと）

| 項目 | 内容 |
|---|---|
| 最終音量 | **手回しデュアルポット**（PGA / digipot 不採用） |
| DEST | トグル＋抵抗ラダー |
| Tone | PT2314。電源は **`VCC_TONE`(+9)** ← Power LM7809 |
| 基板分割 | **Power ≠ Control**。Control+Output 同居可。Power 同居は非推奨（GND/熱/EMI） |
| 隔離 | 一次 `PD_GND` ≠ 二次 `A_GND`。DKMW **R.C. = NC（オープン=ON）** |
| Output / Amp | Outputは`SW_SP3T`×2。Ampは代表1シート＋独立PCB、同一仕様×10 |

詳細: `DECISIONS.md` / `CIRCUIT_DESIGN.md` / `PARTS.md` / `WIRING.md`

### 2.1 PowerModule 現状（2026-08-31）

```text
J202 ← PD module (1=GND 2=+12)
        → PD_12V ──(Case)──► ControlPanel SW1 + D503 LED
                              → PD_12V_SW ──(Case)──► F201 → U201 DKMW +Vin
        PD_GND ←→ 一次（LED 戻りもここ）

U201 → ±12 / A_GND → J201（星型幹線 3P）
+12 → U202 LM7809 → J203 VCC_TONE OUT (1=A_GND 2=+9) → ControlPanel PT2314
```

| コネクタ | 役割 |
|---|---|
| **J202** | PD 給電モジュール入（外付け 50224 可） |
| **J201** | `+12` / `-12` / `A_GND` 星型出 |
| **J203** | `VCC_TONE` 出（2P。戻りは星点側 A_GND。幹線 A_GND と二重ループにしない） |

- シート注記も上記に更新済み
- **PWR SW / 12V LED の実体は ControlPanel**（フロント PCB）。Power に置かない
- オンボード USB-C / CH224 は外してよい（50224 モジュール代用がデフォルト想定の一つ）

### 2.2 PD 配線トポロジ（未決・議論メモ）

どちらも「SW 後で DKMW」は同じ。違うのは **PD モジュールの差し込み位置**。

| | 入口 | 実配線 |
|---|---|---|
| **A（いまの図）** | Power `J202` | Power→Panel へ未スイッチ HOT+GND、Panel→Power へ SW 済み HOT（**往復端子が必要**） |
| **B** | ControlPanel | Panel で SW 後、Power は `PD_12V_SW`+`PD_GND` だけ（往復の「出し」不要） |

- 守りたい本体は **Power**。ホット切り離しは **ControlPanel**
- 実配線の自然さは B 寄り、電源室に PD を集めるなら A
- **この話題は一旦打ち切り**（2026-08-31）。図は A のまま

### 2.3 GND / VCC_TONE

- `VCC_TONE` 戻り = 二次 `A_GND`（7809 GND と同一。衝突ではなく共用）
- 星型 `A_GND` とトーン用戻りを別ケーブルで両端接続すると **ループ**しやすい → J203 で寄り道（専用 2P）が方針

### 2.4 手持ちオペアンプ（2026-08-31 申告）

正本: **[`Audio/OPAMP_INVENTORY.md`](../Audio/OPAMP_INVENTORY.md)**  
DS PDF: **[`Audio/datasheets/opamps/`](../Audio/datasheets/opamps/README.md)**（全石ローカル保管済み）

NJM5532DD / NJM4580DD / OPA2134PA / OPA1656ID / OPA2604AQ / LME49860NA / LT1364CN8 / **MUSE01**（2石→1DIP変換）・MUSES02D、および OPA828・OPA627AU・OPA1612・OPA2140・OPA1652 の DIP 化モジュール等。  
±12 V（DKMW）電源定格は **全石 OK**（詳細は在庫表）。

### 2.5 AmpModule再版（2026-08-31）

- `AudioV2/AmpModule.kicad_sch`: L/R非反転、ゲイン `1+20k/20k=2`
- `AudioV2/AmpModule.kicad_pcb`: `Audio/split/AudioCase_4_amp.kicad_pcb`を元に端子・4穴を維持
- バルク: C709/C710 = 100 µF 35 V polymer（各レール）
- 高周波: C705/C706 = 100 nF X7R、C711/C712 = 1 nF C0G
- 出力: C707/C708 = 470 µF 25 V D12.5/P5、R709/R710 = 47 Ω
- 親は`AmpModule_Reference` 1シート。回路/BOM代表であり、Relay端子配線で物理×10を選択
- PCB再生成: `python3 AudioV2/scripts/build_amp_pcb.py`（ソースの`Audio/`基板は変更しない）

### 2.6 RelayBoard 番地ストラップ（2026-08-31 更新）

結線は **`3V3 → JP → A0/A1 → 10 kΩ → D_GND`**。プルダウンはジャンパ**後段**。JP 手前で分岐すると JP 未実装時に A0/A1 が浮くので不可。

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
- I2C プルアップは **ControlPanel の `R210`/`R211` 4.7 kΩ のみ**。RelayBoard 側には置かない（並列化を避ける）
- 参照接頭辞は `Device:R` に対し `JP` のまま（ストラップである意図を残す）。**KiCad で「既存アノテーションをリセット」して再アノテートすると `R3xx` に振り直される**ので実行しない

**⚠ スクリプトと図が非同期（未解消）:** `wire_circuit_design.py` の `addr_strap` は今も `SolderJumper_2_Open` を y≈152/168 に生成する。`wire_circuit_design.py relay`（または引数省略の `all`）を再生成すると、手編集ぶん（ストラップの U301 脇配置・0 Ω 化・1206 FP・`J_I2C`/`C301`/`C302` の位置・階層ラベル位置）が**全部戻る**。回すなら先にスクリプトへ写すこと。

**安全装置（2026-08-31 追加）:** `main()` は `relay` への書き込みをデフォルトでスキップし、警告を出すだけになった。上書きするには明示的に `--force-relay` を付ける（`python3 wire_circuit_design.py relay --force-relay`）。誤操作（Cursorエージェントが `.cursor/rules/work-on-main.mdc` を見て「再生成は wire_circuit_design.py」とだけ理解し `all` を回すケースなど）を防ぐための保険であり、根本対応（スクリプトの同期）の代わりにはならない。

### 2.7 RelayBoard レビュー指摘（2026-08-31、いずれも接続ミスではない。未対応）

1. **A0/A1 ネットが無名** — 現在 `Net-(U301-A0)` / `Net-(U301-A1)`。`ADDR_A0`/`ADDR_A1` ラベルを戻すとネットリスト差分と ERC ログが読みやすい
2. **IC 直近パスコン不足** — `C301`/`C302` は方針どおり `J_I2C` 入口。別途 U301 の 9/10 ピン間、`U302`/`U303` の 10/9 ピン間に 100 nF が欲しい。`+5V` はリレーパルスが乗るので、リレー群近傍にバルク 100–220 µF も検討
3. **コイル駆動マージンが薄い** — `CHn_SET` は audio/power 2 個のコイルを並列駆動 → 125 Ω∥125 Ω = 62.5 Ω ≈ 80 mA。ULN2803A の VCE(sat) は同電流で 0.9–1.1 V なのでコイル印加は約 3.9–4.1 V。AZ850P2-5 の must-set（定格の 70–75 % = 3.5–3.75 V）に対し余裕が 1 割程度。BP5293 からの 5P 配線の電圧降下も乗る。**`Zettler_AZ850.pdf` の set voltage 実値を確認すること**
4. **A/B は同一番地に見える** — 親で 2 回インスタンス化しているため、ネットリスト上は A/B が同じ JP 状態＝同じ番地。実装時に基板ごとに JP を変える運用（シルク早見表が前提）
5. **起動時 I2C スキャン** — 0x20–0x23 を叩いて応答番地をログ出力。JP 未実装のまま 2 枚組むと両方 0x20 で応答し、配線不良に見える化け方をするため
6. `R302` の参照テキストが MCP のピン番号「17」と軽く重なる（可読性のみ）

**確認済み・問題なし:** 3.3 V ロジック → ULN2803A 入力は IB ≈ 0.7 mA、必要 hFE ≈ 114 に対しダーリントンは 1000 以上。

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

- Power: PD モジュール入・DKMW・7809・J201/J202/J203・パネル SW ループ（論理）
- Control: SW1 PWR SW + D503 12V LED、PT2314 / Pico / ENC 等
- Output / ラベル結線素案（#27）
- AmpModule回路図、独立PCB、代表親シート（×10）
- RelayBoard本配線: 各盤MCP23017×1、ULN2803×2、AZ850×10。Amp入力＋±12 Vを同時切替。番地はJP A1/A0で0x20–0x23（最大4枚）

### 未着手・優先候補

1. **`wire_circuit_design.py` の `addr_strap` を現図（0 Ω / 1206 / U301 脇）へ同期** — 未実施のまま `relay` を再生成すると手編集が消える（§2.6 の警告）
2. **RelayBoard レビュー指摘の消化**（§2.7）— 特に 3 の AZ850 set voltage 実測確認
3. PD 往復端子（A のままなら Power↔Panel 用コネクタ追加）or トポロジ B への図変更
4. **ControlPanel未接続ピンの整理**
5. ERC 残り（Relay/Amp/Power/Outputは0件。Control 32件＋親の箱外ラベルが主）
6. OLED FP、PT2314 未使用入力
7. RelayBoard PCB時: JP横 F.Silk に番地早見表（0x20–0x23）。FP は RelayBoard 全体で未割当（U301 含む）

### 検証

```bash
python3 Audio/scripts/check_sexpr.py -q AudioV2
cd AudioV2 && kicad-cli sch export netlist -o /tmp/audiov2.net AudioV2Case.kicad_sch
kicad-cli pcb drc --refill-zones -o /tmp/amp-drc.json --format json AmpModule.kicad_pcb
```

Windows: Git Bash + KiCad CLI（`.cursor/rules/kicad-cli-git-bash.mdc`）。

---

## 6. 会話タイムライン要約（追記）

…（〜08-30: ラベル結線・アノテ・クラウド切替）

11. Power をラベル→ワイヤへ整理。−12 デカップ・C217=7809 Cout・C219
12. Case=論理、SW/Volume 実体は子シート。SW/LED を一度 Power に寄せ→**Control に戻す**
13. 外付け 50224 前提。`J202` PD in、`J203` VCC_TONE out。R.C. 明示 NC
14. PD 入口 A vs B・往復端子の議論 → **一旦終了**（図は A）
15. 本メモ更新 → `main` に commit/push（クラウド同期用）
16. 手持ちオペアンプリストを `Audio/OPAMP_INVENTORY.md` に登録
17. AmpModuleを高速石対応で再版。代表1シートを親へ統合し、独立PCBを×10仕様で生成
18. RelayBoard本配線。未給電Ampへの信号印加を避け、audio入力＋±12 Vを同時切替。全体ERC 207→66
19. 番地ストラップを `SolderJumper` → **0 Ω / 1206** に変更（§2.6）。`C301`/`C302` は `J_I2C` 入口、ストラップは U301 脇へ。レビュー指摘を §2.7 に記録。全体ERC 56（Relay 0）

---

## 7. 別チャット再開プロンプト（コピペ用）

```
AudioV2/AGENT_HANDOFF.md を読んで続きから。
ブランチは main（origin と同期済み前提）。
AmpModuleは代表1シート＋独立PCB（同一仕様×10）。ゲイン2、±12 V、バルク/1nF対応済み。
RelayBoardは入力＋電源連動、各盤MCP×1/ULN×2/AZ850×10、ERC 0。
番地ストラップは0Ω/1206（AGENT_HANDOFF §2.6）。レビュー指摘は §2.7 に未対応で置いてある。
次候補: addr_strapのスクリプト同期 / Relayレビュー指摘 / Control / 親の箱外dangling label整理。
generate_kicad_scaffold.py は再実行しない。wire_circuit_design.py relay も同期まで回さない。
```

---

## 8. 触ってよい／だめ

| OK | NG |
|---|---|
| `AudioV2/**` の sch / スクリプト / 文書 | `Audio/` 既存製造図の無闇な改変 |
| `wire_circuit_design.py` での再生成 | `generate_kicad_scaffold.py` 再実行 |
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
