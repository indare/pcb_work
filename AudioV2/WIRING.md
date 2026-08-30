# AudioV2 箱配線 IF 素案（draft）

**目的:** KiCad 図外（`Audio/` 流用基板）との端子接続一覧。回路レビュー前のたたき台。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule **J201**-1 | RelayBoard×2, ControlPanel, Amp×10 `V+` 端子 | 端子台 3P 幹線 |
| `-12V` | PowerModule **J201**-2 | 同上 `V-` | 同上 |
| `A_GND` | PowerModule **J201**-3 | 全アナログ島（NetTie 一点 — **位置未決**） | 端子台 |
| PD 入 | 外付け **50224 等** → Power **J202**（1=GND 2=+12） | 板上 `PD_12V` / `PD_GND` | 2P（トポロジ A） |
| `PD_12V` | Power（J202 後） | ControlPanel PWR SW 入力 | **往復用端子まだ**（A のまま要追加） |
| `PD_12V_SW` | ControlPanel SW1 出力 | Power F1 → DKMW +Vin | 2P 戻り |
| `PD_GND` | J202 / DKMW −Vin | Panel LED 戻り | 上記とセット |
| `VCC_TONE` | Power LM7809 → **J203**（1=A_GND 2=+9） | ControlPanel PT2314 | 2P（星型 A_GND と二重ループにしない） |

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
- PD 入口トポロジ **A（いまの図）vs B（パネル入口）** — 議論打ち切り。A なら Power↔Panel 往復端子が追加で必要
- ENC / ノブの正確な秋月コード（在庫次第）
- ERC / ネットリスト整合
