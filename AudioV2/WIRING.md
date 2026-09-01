# AudioV2 箱配線 IF 素案（draft）

**目的:** AudioV2基板間と、KiCad図外の流用基板との端子接続一覧。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule **J201**-1 | RelayBoard_A/B `J_RAIL`-1, ControlPanel | 端子台 3P 幹線 ×2本 |
| `A_GND` | PowerModule **J201**-2 | RelayBoard `J_RAIL`-2 → 各 `J_PWR`-2（非切替）、全アナログ島 | 端子台 |
| `-12V` | PowerModule **J201**-3 | 同上 `J_RAIL`-3 | 同上 |
| PD 入 | 外付け **50224 等** → Power **J202**（1=GND 2=+12） | 板上 `PD_12V` / `PD_GND` | 2P（トポロジ A） |
| `PD_12V` | Power（J202 後） | ControlPanel PWR SW 入力 | **往復用端子まだ**（A のまま要追加） |
| `PD_12V_SW` | ControlPanel SW502 出力 | Power F201 → DKMW +Vin | 2P 戻り |
| `PD_GND` | J202 / DKMW −Vin | Panel LED 戻り | 上記とセット |
| `VCC_TONE` | Power LM7809 → **J203**（1=A_GND 2=+9） | ControlPanel PT2314 | 2P（星型 A_GND と二重ループにしない） |

## A_GND / D_GND の分離（2026-08-31 確定）

`D_GND`（デジタル/コイル駆動）と`A_GND`（アナログ/音声・±12V帰路）は**システム全体で1箇所だけ**NetTieで結合する（DECISIONS.md G1/G2）。

- **NetTie位置: ControlPanel**（`D_GND`の発生源＝操作Picoの直近。G2「操作PicoのD_GND」参照）
- **RelayBoardでは結合しない。** RelayBoardは`A_GND`（PowerModule `J_RAIL`経由、Amp接点/電源用）と`D_GND`（ControlPanel `J_I2C`経由、MCP23017/ULN2803コイル駆動用）の**両方を受け取るが、両者は基板上で最後まで別ネットのまま**。ここで繋ぐとNetTieが2箇所目になり、A_GND側にコイル駆動ノイズが回り込むグラウンドループになる
- G1「リレー盤=...結合はNetTie一点」は、RelayBoard上に結合点を置けという意味ではなく、システム全体で見た「一点」原則をリレー盤の文脈で言及したもの（G2のControlPanel側の記述と同じ1点を指す）

## デジタル / I²C（2026-08-31 スター確定）

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `I2C_SDA/SCL` | ControlPanel Pico GP20/21 | RelayBoard_A/B MCP23017, SSD1306, PT2314 | **スター確定**（daisy不採用）。ControlPanel `J_I2C`出力から板の枚数分ホームラン |
| `3V3` / `+5V` / `D_GND` | ControlPanel Pico / BP5293 | RelayBoard `J_I2C` 5P | +5 VはAZ850コイル、3V3はMCPロジック |

**スターを選んだ理由:** (1) 板の抜き差しで他板を巻き込まない（daisyは中継コネクタ不良で下流が全滅）、(2) `+5V`にリレーパルス電流(§AGENT_HANDOFF 2.7-2)が乗るため、daisyだと板Aのノイズが板Bの給電経路を直列で通過してしまう。starなら各板の帰路が独立し、ノイズ源(ControlPanel)止まりで完結する。(3) I2Cプルアップが`ControlPanel`の`R501`/`R502`一箇所に集約されており、starの方が電気的中心と一致する。

**実装:** ControlPanel基板上のコネクタは1個のまま（`Conn_01x05_Pin`、footprint未定）。板の本数分の分岐は**箱内配線**で行う — フェルール端子で複数本を1端子にまとめる、またはスプリッタケーブルで分岐。PCB側の物理コネクタ選定（端子台 vs ピンヘッダ）は、この分岐方式が確定してから決める（footprint未定のまま、AGENT_HANDOFF §5参照）。

**製造ロット:** RelayBoard PCBは5枚発注。番地ストラップ(JP301/JP302)は2bitで最大4枚(0x20–0x23)までしか同時稼働できないため、5枚目は予備。

## 音声幹線

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `COMMON_L/R` | 外部ソース入力 | ControlPanel PT2314入力 | 親では箱外スタブ |
| `TONE_L/R` | ControlPanel PT2314出力 | RelayBoard_A/B `J_TONE` 2P → 選択Amp `J701` | **2芯シールド**。芯=L/R。シールドはControl側の`A_GND`のみ（Relayの`J_RAIL`とループさせない） |
| Amp入力 `J701` | RelayBoard `J_AUD{n}` | AudioV2 Amp×10 | L/R 2P。長い引き回しは2芯シールドで、シールドは`J_PWR`-2側の`A_GND`へ |
| Amp電源 `J703` | RelayBoard `J_PWR{n}` | AudioV2 Amp×10 | 3P（+12/A_GND/-12）。±12 Vのみリレー切替、`A_GND`は直結 |
| Amp出力 `J702` | AudioV2 Amp×10 | `AMP_SEL_L/R`共通ハーネス → OutputStage | 47 Ω＋470 µF後で共通化 |
| `PHONE_L/R` | OutputStage RV601 | **Audio/ HeadphoneBuffer** | 0 Ω 固定パッド廃止 |
| `LINE_L/R` | OutputStage RV602 | LINE 端子 | |
| `PHONE_L/R` | OutputStage J_HP601 | Audio/ HeadphoneBuffer 入力 | |
| `LINE_L/R` | OutputStage J_LINE601 | 前面 LINE OUT | |

## Amp再版とAudio/流用

| 基板 | 接続 |
|---|---|
| AudioV2 AmpModule ×10 | `J701`=Relay選択済みTONE L/R、`J702`=AMP_SEL共通、`J703`=Relay選択済み+12/A_GND/-12。親は代表1シート |
| HeadphoneBufferModule | OutputStage `PHONE_L/R`, ±12V |
| AdcBuffer / MeasurementADC | ±12V + 測定タップ（**位置 MD で固定**） |

## 意図的未決

- **Q3** I²C トポロジー（daisy / スター）
- GND NetTie 物理位置
- PD 入口トポロジ **A（いまの図）vs B（パネル入口）** — 議論打ち切り。A なら Power↔Panel 往復端子が追加で必要
- ENC / ノブの正確な秋月コード（在庫次第）
- ERC / ネットリスト整合
