# AudioV2 箱配線 IF 素案（draft）

**目的:** AudioV2基板間と、KiCad図外の流用基板との端子接続一覧。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule **J201**-1 | RelayBoard_A/B `J_RAIL`-1, ControlPanel | 端子台 3P 幹線 ×2本 |
| `A_GND` | PowerModule **J201**-2 | RelayBoard `J_RAIL`-2 → 各 `J_PWR`-2（非切替）、全アナログ島（NetTie 一点 — **位置未決**） | 端子台 |
| `-12V` | PowerModule **J201**-3 | 同上 `J_RAIL`-3 | 同上 |
| PD 入 | 外付け **50224 等** → Power **J202**（1=GND 2=+12） | 板上 `PD_12V` / `PD_GND` | 2P（トポロジ A） |
| `PD_12V` | Power（J202 後） | ControlPanel PWR SW 入力 | **往復用端子まだ**（A のまま要追加） |
| `PD_12V_SW` | ControlPanel SW1 出力 | Power F1 → DKMW +Vin | 2P 戻り |
| `PD_GND` | J202 / DKMW −Vin | Panel LED 戻り | 上記とセット |
| `VCC_TONE` | Power LM7809 → **J203**（1=A_GND 2=+9） | ControlPanel PT2314 | 2P（星型 A_GND と二重ループにしない） |

## デジタル / I²C（Q3 拓扑 **保留**）

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `I2C_SDA/SCL` | ControlPanel Pico GP20/21 | RelayBoard_A/B MCP23017, SSD1306, PT2314 | daisy vs スター — **未決** |
| `3V3` / `+5V` / `D_GND` | ControlPanel Pico / BP5293 | RelayBoard `J_I2C` 5P | +5 VはAZ850コイル、3V3はMCPロジック |

## 音声幹線

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `COMMON_L/R` | 外部ソース入力 | ControlPanel PT2314入力 | 親では箱外スタブ |
| `TONE_L/R` | ControlPanel PT2314出力 | RelayBoard_A/B `J_TONE` 2P → 選択Amp `J701` | **2芯シールド**。芯=L/R。シールドはControl側の`A_GND`のみ（Relayの`J_RAIL`とループさせない） |
| Amp入力 `J701` | RelayBoard `J_AUD{n}` | AudioV2 Amp×10 | L/R 2P。長い引き回しは2芯シールドで、シールドは`J_PWR`-2側の`A_GND`へ |
| Amp電源 `J703` | RelayBoard `J_PWR{n}` | AudioV2 Amp×10 | 3P（+12/A_GND/-12）。±12 Vのみリレー切替、`A_GND`は直結 |
| Amp出力 `J702` | AudioV2 Amp×10 | `AMP_SEL_L/R`共通ハーネス → OutputStage | 47 Ω＋470 µF後で共通化 |
| `PHONE_L/R` | OutputStage RV101 | **Audio/ HeadphoneBuffer** | 0 Ω 固定パッド廃止 |
| `LINE_L/R` | OutputStage RV102 | LINE 端子 | |
| `PHONE_L/R` | OutputStage J_HP | Audio/ HeadphoneBuffer 入力 | |
| `LINE_L/R` | OutputStage J_LINE | 前面 LINE OUT | |

## Amp再版とAudio/流用

| 基板 | 接続 |
|---|---|
| AudioV2 AmpModule ×10 | `J701`=Relay選択済みTONE L/R、`J702`=AMP_SEL共通、`J703`=Relay選択済み+12/A_GND/-12。親は代表1シート |
| HeadphoneBufferModule | OutputStage `PHONE_L/R`, ±12V |
| AdcBuffer / MeasurementADC | ±12V + 測定タップ（**位置 MD で固定**） |

## 意図的未決

- **Q3** I²C 拓扑（daisy / スター）
- GND NetTie 物理位置
- PD 入口トポロジ **A（いまの図）vs B（パネル入口）** — 議論打ち切り。A なら Power↔Panel 往復端子が追加で必要
- ENC / ノブの正確な秋月コード（在庫次第）
- ERC / ネットリスト整合
