# AudioV2 箱配線 IF 素案（draft）

**目的:** KiCad 図外（`Audio/` 流用基板）との端子接続一覧。回路レビュー前のたたき台。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule J202-1 | RelayBoard×2, ControlPanel, Amp×10 `V+` 端子 | 端子台 3P 幹線 |
| `-12V` | PowerModule J202-2 | 同上 `V-` | 同上 |
| `A_GND` | PowerModule J202-3 | 全アナログ島（NetTie 一点 — **位置未決**） | 端子台 |
| `PD_12V` | PowerModule J_PD | ControlPanel PWR SW 入力 | 2P ケーブル |
| `PD_12V_SW` | ControlPanel SW 出力 | PowerModule F1/DKMW20 +Vin | 2P 戻り |
| `PD_GND` | CH224/DKMW −Vin | Panel LED 戻り | 2P |
| `VCC_TONE` | PowerModule LDO | ControlPanel PT2314 | 2P or 同一 PCB |

## デジタル / I²C（Q3 拓扑 **保留**）

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `I2C_SDA/SCL` | ControlPanel Pico GP20/21 | RelayBoard_A MCP23017, RelayBoard_B, SSD1306, PT2314 | daisy vs スター — **未決** |
| `3V3` / `D_GND` | ControlPanel BP5293 | RelayBoard J_I2C | |

## 音声幹線

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `COMMON_L/R` | RelayBoard_A/B 合流 → Control PT2314 入力 | §11.8 共通バス | 4P コネクタ想定 |
| PT2314 OUT → | ControlPanel | **Audio/ Amp×10 入力端子**（図外） | 箱配線 |
| Amp 出力（選択後）→ | Audio/ 製造済み | ControlPanel **AMP_SEL_L/R** → SW_DEST | 図外 |
| `PHONE_L/R` | OutputStage RV101 | **Audio/ HeadphoneBuffer** | 0 Ω 固定パッド廃止 |
| `LINE_L/R` | OutputStage RV102 | LINE 端子 | |
| `PHONE_L/R` | OutputStage J_HP | Audio/ HeadphoneBuffer 入力 | |
| `LINE_L/R` | OutputStage J_LINE | 前面 LINE OUT | |

## Audio/ 流用（図に載せない）

| 基板 | 接続 |
|---|---|
| AmpModule ×10 | RelayBoard `AMP{n}_L/R`, `AMP{n}_V±` |
| HeadphoneBufferModule | OutputStage `PHONE_L/R`, ±12V |
| AdcBuffer / MeasurementADC | ±12V + 測定タップ（**位置 MD で固定**） |

## 意図的未決

- **Q3** I²C 拓扑（daisy / スター）
- GND NetTie 物理位置
- ENC / ノブの正確な秋月コード（在庫次第）
- ERC / ネットリスト整合
