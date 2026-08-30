# AudioV2 回路設計メモ（#19 作業中）

**目的:** 素案 KiCad の **ピン番号・部品値**をデータシートと突き合わせ、机上で確定してから ERC/配線を詰める。

**参照 DS:** `datasheets/` ローカル PDF。KiCad シンボルは `AudioV2.kicad_sym` + 標準 lib。

---

## 1. ピン照合サマリー（素案 vs DS）

| 部品 | 素案の問題 | DS 正 | 対応 |
|---|---|---|---|
| **PGA2310PA** | ピン名・番号が TI PDIP-16 と **不一致**（例: pin16=V+ は誤り、正しく VINL） | [TI_PGA2310.pdf](datasheets/TI_PGA2310.pdf) §5 | **シンボル修正済み**（本 PR） |
| **PT2314** | **TSSOP-20 8pin 仮シンボル** — 実体は **28pin DIP/SOP** | [Princeton_PT2314.pdf](datasheets/Princeton_PT2314.pdf) p.3–4 | **28pin シンボルへ差替**（本 PR） |
| **PT2314 バス** | SDA/SCL 命名 | pin26=**DATA**, pin27=**CLK**（I²C 様シリアル、標準 I²C ではない） | ネット名は `PT2314_DATA/CLK`、ファームは専用ドライバ |
| **CH224_50224** | 4pin 抽象（VBUS/GND/12V/PG） | [50224 マニュアル](datasheets/StrawberryLinux_CH224K_manual.pdf) | モジュール **端子台/ヘッダは実機配置に合わせる**。PG は OD・プルアップ要 |
| **DKMW20F-12** | pin1=+Vin, 2=−Vin, 3=+Vout, 4=Common, 5=−Vout, 6=R.C. | MeanWell DS + `PowerModule_TEC3_REDESIGN.md` | **OK**（Audio 流用ピン定義と一致） |
| **MCP23017** | 標準 KiCad lib 使用想定 | [Microchip_MCP23017.pdf](datasheets/Microchip_MCP23017.pdf) | A0–A2 で **0x20 / 0x21**（Relay A/B） |
| **Pico 2 GPIO** | §10 表 | [RP2350.pdf](datasheets/RaspberryPi_RP2350.pdf) | **OK** — GP20/21=I²C0, GP18/19=SPI0, GP16/17=MUTE/CS |
| **ENC 1×3** | 1=A, 2=B, 3=SW, 4=3V3, 5=GND | `Control/README.md` + EC11 | **OK** |

---

## 2. PGA2310PA — PDIP-16（確定ピン表）

TI SBOS207C §5「Top View」どおり。**AudioV2 は ±12 V アナログ、VD+ = +5 V（BP5293）。**

| Pin | 名前 | 接続 |
|:---:|---|---|
| 1 | ZCEN | **VD+（5 V）** — ゼロクロス常時 ON |
| 2 | CS | Pico **GP17**（両 IC 共通、Active Low） |
| 3 | SDI | Pico **GP19** → U_HP；U_HP **SDO(7)** → U_LINE **SDI(3)** |
| 4 | VD+ | **+5 V（D_GND デカップ 0.1 µF + 10 µF）** |
| 5 | DGND | **D_GND** |
| 6 | SCLK | Pico **GP18** |
| 7 | SDO | → 2 個目 SDI のみ。**Pico へ接続しない**（5 V 出力） |
| 8 | MUTE | Pico **GP16** + **10 kΩ → DGND**（起動ミュート） |
| 9 | VINR | アナログ入力 R（Amp 後） |
| 10 | AGNDR | **A_GND** |
| 11 | VOUTR | アナログ出力 R |
| 12 | VA+ | **+12 V** + 0.1 µF + 10 µF |
| 13 | VA− | **−12 V** + 0.1 µF + 10 µF |
| 14 | VOUTL | アナログ出力 L |
| 15 | AGNDL | **A_GND** |
| 16 | VINL | アナログ入力 L |

**デイジーチェーン:** U_HP（1 個目）SDO pin7 → U_LINE（2 個目）SDI pin3。

---

## 3. PT2314 — 28pin（AudioV2 最小接続）

**パッケージ:** 28pin **DIP 300mil**（または SOP — 設計時にどちらか固定）。

**電源:** VDD typ **9 V**（6–10 V）。**±12 V 直結不可。** PowerModule から **+9 V（VCC_TONE）** を生成。

### 3.1 ピン表（使用ピンのみ）

| Pin | 名前 | AudioV2 接続 |
|:---:|---|---|
| 1 | VDD | **+9 V** |
| 2 | AGND | **A_GND** |
| 3 | TREB_L | **C 2.2 µF + R 2.4 kΩ** → ネットワーク（DS 図 C3/C8 + R） |
| 4 | TREB_R | 同上 R 系 |
| 5 | RIN | **COMMON_R** 経 **C 2.2 µF** |
| 17 | LIN | **COMMON_L** 経 **C 2.2 µF** |
| 19 | BIN_L | **R 2.4 kΩ + C 100 nF / 2.7 nF**（DS C12–C19 系） |
| 20 | BOUT_L | 同上 |
| 21 | BIN_R | 同上 |
| 22 | BOUT_R | 同上 |
| 23 | OUT_R | **→ Amp 系統へ**（2.2 µF 結合） |
| 24 | OUT_L | **→ Amp 系統へ** |
| 25 | DGND | **D_GND** |
| 26 | DATA | Pico GP20 経 **4.7 kΩ → 3.3 V**（バスは 3.3 V 世界） |
| 27 | CLK | Pico GP21 経 **4.7 kΩ → 3.3 V** |
| 28 | REF | **R 5.6 kΩ → AGND**, **C 22 µF → AGND**（DS 図） |

**未使用入力（RIN1–4, LIN1–4 等）:** DS 図に合わせ **2.2 µF + R 2.4 kΩ で AC グランド** または入力セレクタで Main のみ — 詳細は §3.3 シミュ後に確定。

### 3.2 外部 C/R（DS Application Circuit より）

| 素子 | 値 | 備考 |
|---|---|---|
| 入力結合 C | **2.2 µF** | LIN/RIN 各 1 |
| トーン R | **2.4 kΩ** | 推奨値（範囲 2.0–3.6 kΩ） |
| トーン C | **100 nF**, **2.7 nF** | Mylar 推奨（C12–C19） |
| REF R | **5.6 kΩ** | pin28 |
| REF C | **22 µF** | pin28–AGND |
| I²C プルアップ | **4.7 kΩ ×2** | DATA/CLK → **3.3 V**（Pico 側） |

### 3.3 机上検算（電源）

| 項目 | 計算 |
|---|---|
| PT2314 Is | typ **30 mA**, max **40 mA** @ 9 V |
| 9 V 生成 | **LM7809**（+12 V → 9 V, Vin−Vout=3 V > 2 V dropout） |
| 7809 散逸 | (12−9) V × 40 mA ≈ **0.12 W** — 余裕 |
| REF 電圧 | VREF ≈ VDD/2 ≈ **4.5 V**（REF ネットワーク経由） |

**未検証（要 LTspice / 実機）:** DATA/CLK の 3.3 V 駆動で VDD=9 V の PT2314 が満足するか — DS は「positive supply」へプルアップと記載。**レベルシフタ不要の報告多いが、波形確認推奨。**

---

## 4. PowerModule — 部品値（案）

| Ref | 部品 | 値 | 根拠 |
|---|---|---|---|
| U1 | DKMW20F-12 | — | ±12 V / ±830 mA |
| U2 | 50224 CH224 | 12 V ジャンパ | §9 |
| F1 | ヒューズ | **3 A slow** | Audio PowerModule 同型（12 V PD ≈1.5 A） |
| U3 | LM7809 | +9 V / ≥100 mA | PT2314 VDD |
| C7809 in/out | 10 µF + 0.1 µF | 7809 定番 |
| DKMW20 Cout | **820 µF/rail** | DS 800 µF each |

**PD 配線（§9）:** CH224 12 V → 端子 `PD_12V` → パネル PWR SW → `PD_12V_SW` → F1 → DKMW20 +Vin。

---

## 5. MCP23017 + ENC ヘッダ（RelayBoard / ControlPanel）

| 項目 | 確定値 |
|---|---|
| Relay A I²C addr | **0x20**（A2:A1:A0 = 000, ハードウェアで確認） |
| Relay B I²C addr | **0x21**（001） |
| MCP INT | 任意 — 初版はポーリング可 |
| ENC J×6 | **1×3 ピン:** 1=A, 2=B, 3=SW；**4=3V3, 5=GND**（Control README 同型） |

---

## 6. シミュレーション計画

| 対象 | 方法 | 状態 |
|---|---|---|
| PT2314 REF (R5.6k/C22µ) | RC 定常 → VREF≈4.5 V | ✅ 机上 OK |
| PGA2310 デカップリング | DS 推奨 C 値 | ✅ 0.1+10 µF ×3 レール |
| 7809 9 V レール | 負荷 40 mA | ✅ 余裕 |
| PT2314 トーン RC | f_c ≈ 1/(2π×2.4k×C) | ⬜ C=100n → ≈663 Hz 級（要 DS 意図と照合） |
| DEST リレー + PGA ノイズ | SPICE 簡易 | ⬜ Q2-A vs Q2-B は PCB 時 |

---

## 7. KiCad 更新チェックリスト

- [x] PGA2310PA シンボル — 16pin DS 一致
- [x] PT2314 シンボル — 28pin DIP 全ピン
- [x] ControlPanel — PT2314 周辺 C/R 配置（`wire_circuit_design.py`）
- [x] PowerModule — LM7809 + F1 3A、配線
- [x] 親シート — グローバルバス ↔ 子シート pin 配線
- [ ] ERC — 未接続・未使用入力の整理
- [ ] RelayBoard / OutputStage 配線

## 8. 配置・配線（2026-08-30）

`python3 AudioV2/scripts/wire_circuit_design.py` で以下を生成:

| シート | 内容 |
|---|---|
| PowerModule | CH224→F1→DKMW20、7809→VCC_TONE、J202 出力 |
| ControlPanel | PT2314 電源/入力/REF/トーン RC/PGA2310×2/SPI |
| AudioV2Case | +12V/A_GND/I²C グローバルバス配線 |

KiCad で **ControlPanel ページ 5** を開き、U2 周辺の C/R 配置と net 名を確認。

---

## 9. 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 素案ピン監査、PT2314 28pin 判明、PGA2310 修正方針 |
