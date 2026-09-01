# AudioV2 箱配線 IF 素案（draft）

> **未更新（2026-09-01 のアーキテクチャ刷新未反映）:** RelayBoard と AmpModule ×10 は
> `AmpBank` 1枚へ統合され、`RelayBoard.kicad_sch` / `AmpModule.kicad_sch` は削除済み
> （[AGENT_HANDOFF.md §2.9](AGENT_HANDOFF.md)）。以下の「RelayBoard」「AMPn」を含む記述
> （音声幹線・Amp再版の節、番地ストラップの製造ロット言及など）は旧アーキテクチャの記録で、
> 現行の物理配線（AmpBank への `+15V/-15V/A_GND` 星型・`TONE_L/R`・`AMP_SEL_L/R`・I2C 各1本）
> を反映していない。書き換えは未着手。電源星型節のネット名（`+12V`/`-12V`）は
> `+15V`/`-15V` に読み替えること。

**目的:** AudioV2基板間と、KiCad図外の流用基板との端子接続一覧。

> **記法:** 端子台は参照(designator)ではなく **ネット名と回路図の Value 欄の名前**で指す。
> 参照は再アノテーションで動くが（2026-09-01 に58件が動いた）、ネット名と Value は設計者が付けた名前なので動かない。
> 方針は [`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md) §3。ピン番号は現物の締め付け順なので併記する。

## 電源星型（PowerModule → 各所）

| Net | 源 | 先 | 形式 |
|---|---|---|---|
| `+12V` | PowerModule `+12/-12/A_GND out` 端子台-1 | RelayBoard_A/B `RAIL IN` 端子台-1, ControlPanel | 端子台 3P 幹線 ×2本 |
| `A_GND` | PowerModule `+12/-12/A_GND out` 端子台-2 | RelayBoard `RAIL IN`-2 → 各 `AMPn PWR` 端子台-2（非切替）、全アナログ島 | 端子台 |
| `-12V` | PowerModule `+12/-12/A_GND out` 端子台-3 | 同上 `RAIL IN`-3 | 同上 |
| PD 入 | 外付け **50224 等** → Power `PD module in` 端子台（1=GND 2=+12） | 板上 `PD_12V` / `PD_GND` | 2P（トポロジ A） |
| `PD_12V` | Power（PD 入力端子台の直後、ヒューズ前） | ControlPanel パネル PWR SW 入力 | **往復用端子まだ**（A のまま要追加） |
| `PD_12V_SW` | ControlPanel パネル PWR SW 出力 | Power ヒューズ(3A slow) → DKMW +Vin | 2P 戻り。12 V パネル LED もこの戻り側に付く（SW 後なので通電表示になる） |
| `PD_GND` | PD 入力端子台 / DKMW −Vin | Panel LED 戻り | 上記とセット |
| `VCC_TONE` | Power LM7809 → `VCC_TONE OUT` 端子台（1=A_GND 2=+9） | ControlPanel PT2314 | 2P（星型 A_GND と二重ループにしない） |

## A_GND / D_GND の分離（2026-08-31 確定）

`D_GND`（デジタル/コイル駆動）と`A_GND`（アナログ/音声・±12V帰路）は**システム全体で1箇所だけ**NetTieで結合する（DECISIONS.md G1/G2）。

- **NetTie位置: ControlPanel**（`D_GND`の発生源＝操作Picoの直近。G2「操作PicoのD_GND」参照）
- **RelayBoardでは結合しない。** RelayBoardは`A_GND`（PowerModuleから `RAIL IN` 端子台経由、Amp接点/電源用）と`D_GND`（ControlPanelから I2C/電源コネクタ経由、MCP23017/ULN2803コイル駆動用）の**両方を受け取るが、両者は基板上で最後まで別ネットのまま**。ここで繋ぐとNetTieが2箇所目になり、A_GND側にコイル駆動ノイズが回り込むグラウンドループになる
- G1「リレー盤=...結合はNetTie一点」は、RelayBoard上に結合点を置けという意味ではなく、システム全体で見た「一点」原則をリレー盤の文脈で言及したもの（G2のControlPanel側の記述と同じ1点を指す）

## デジタル / I²C（2026-08-31 スター確定）

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `I2C_SDA/SCL` | ControlPanel Pico GP20/21 | RelayBoard_A/B MCP23017, SSD1306, PT2314 | **スター確定**（daisy不採用）。ControlPanel 側 I2C/電源コネクタ出力から板の枚数分ホームラン |
| `3V3` / `+5V` / `D_GND` | ControlPanel Pico / BP5293 | RelayBoard の I2C/電源コネクタ（`CTRL`）5P | +5 VはAZ850コイル、3V3はMCPロジック |

I2C/電源コネクタのピン順は、RelayBoard 側（回路図 Value `CTRL`）が **1=`I2C_SDA` / 2=`I2C_SCL` / 3=`3V3` / 4=`+5V` / 5=`D_GND`**。**ControlPanel 側のコネクタは回路図にまだ存在しない**（現状 4P の OLED 用のみ）ので、実装するときにこの順へ合わせる。

**スターを選んだ理由:** (1) 板の抜き差しで他板を巻き込まない（daisyは中継コネクタ不良で下流が全滅）、(2) `+5V`にリレーパルス電流(§AGENT_HANDOFF 2.7-2)が乗るため、daisyだと板Aのノイズが板Bの給電経路を直列で通過してしまう。starなら各板の帰路が独立し、ノイズ源(ControlPanel)止まりで完結する。(3) I2Cプルアップ（`I2C_SDA`/`I2C_SCL` → `3V3`、4.7 kΩ ×2）を **ControlPanel 一箇所に集約**しており、starの方が電気的中心と一致する（板側にも置くと枚数ぶん並列になる。AGENT_HANDOFF §2.6）。

**実装:** ControlPanel 基板上のコネクタは1個で設計する**方針**（`Conn_01x05_Pin` 想定、シンボル未配置・footprint未定）。板の本数分の分岐は**箱内配線**で行う — フェルール端子で複数本を1端子にまとめる、またはスプリッタケーブルで分岐。PCB側の物理コネクタ選定（端子台 vs ピンヘッダ）は、この分岐方式が確定してから決める（footprint未定のまま、AGENT_HANDOFF §5参照）。

**製造ロット:** RelayBoard PCBは5枚発注。番地ストラップは2bit（A1/A0）で最大4枚(0x20–0x23)までしか同時稼働できないため、5枚目は予備。ストラップの実装対応表は AGENT_HANDOFF §2.6。

## 音声幹線

| Net | 源 | 先 | 備考 |
|---|---|---|---|
| `COMMON_L/R` | 外部ソース入力 | ControlPanel PT2314入力 | 親では箱外スタブ |
| `TONE_L/R` | ControlPanel PT2314出力 | RelayBoard_A/B `TONE IN` 端子台 2P → 選択されたAmpの `AMP_IN L/R` 端子台 | **2芯シールド**。芯=L/R。シールドはControl側の`A_GND`のみ（Relay側の ±12/A_GND 幹線とループさせない） |
| Amp入力 `AMPn_L/R` | RelayBoard `AMPn IN` 端子台（1=L / 2=R） | Amp の `AMP_IN L/R` 端子台 | L/R 2P。長い引き回しは2芯シールドで、シールドは `AMPn PWR` 端子台-2 側の `A_GND` へ |
| Amp電源 `AMPn_V+ / AMPn_V-` | RelayBoard `AMPn PWR` 端子台（1=V+ / 2=`A_GND` / 3=V−） | Amp の `+12V / A_GND / -12V` 端子台 | 3P。**±12 Vのみリレー切替、`A_GND`は直結**（切替中も帰路が浮かない） |
| `AMP_SEL_L/R` | Amp×10 の `AMP_OUT L/R` 端子台 | 共通ハーネス → OutputStage の `RAIL IN` 端子台（1=`AMP_SEL_L` / 2=`A_GND` / 3=`AMP_SEL_R`） | 各Ampの 47 Ω＋470 µF の後で共通化。**同名の `RAIL IN` が RelayBoard 側にもあるが別物**（あちらは Power からの ±12/A_GND） |
| `PHONE_L/R` | OutputStage HP 音量ポット（A50k 2連）のワイパ | `to Audio HP Buffer` 端子台 → **Audio/ HeadphoneBuffer** 入力 | 0 Ω 固定パッド廃止 |
| `LINE_L/R` | OutputStage LINE 音量ポット（A50k 2連）のワイパ | `LINE OUT` 端子台 → 前面 LINE OUT | |

## Amp再版とAudio/流用

| 基板 | 接続 |
|---|---|
| AudioV2 AmpModule ×10 | `AMP_IN L/R` 端子台=Relay選択済みの `TONE_L/R`、`AMP_OUT L/R` 端子台=`AMP_SEL_L/R` 共通ハーネス、`+12V / A_GND / -12V` 端子台=Relay選択済み ±12 V（`A_GND` は直結）。親は代表1シート |
| HeadphoneBufferModule | OutputStage `PHONE_L/R`, ±12V |
| AdcBuffer / MeasurementADC | ±12V + 測定タップ（**位置 MD で固定**） |

## 意図的未決

- **Q3** I²C トポロジー（daisy / スター）
- GND NetTie 物理位置
- PD 入口トポロジ **A（いまの図）vs B（パネル入口）** — 議論打ち切り。A なら Power↔Panel 往復端子が追加で必要
- ENC / ノブの正確な秋月コード（在庫次第）
- ERC / ネットリスト整合
