# AudioV2 箱配線 IF

**目的:** 基板間の物理配線と、KiCad 図の外にある流用基板（`Audio/`）との接続を決める。

> **この文書に書くこと / 書かないこと**
>
> どの端子台がどのネットに繋がるかは**回路図から導出できる**ので書かない
> （`kicad-run.sh netlist` で出る）。ここに書くのは導出できないもの
> — **ケーブルの種類・シールドの落とし方・分岐の方法・図の外にある基板との接続・未決事項**。
> 方針は [`SOURCE_OF_TRUTH.md`](../SOURCE_OF_TRUTH.md)。
>
> **記法:** 端子台は参照(designator)ではなく **ネット名と回路図の Value 欄の名前**で指す。
> 参照は再アノテーションで動く（2026-09-01 に58件、2026-09-02 に AmpChannel で320件が動いた）が、
> ネット名と Value は設計者が付けた名前なので動かない。

## 基板構成（2026-09-01 の刷新後）

`PowerModule` / `ControlPanel` / `AmpBank` / `OutputStage` の **4枚**。
`AmpBank` は 10ch 分のアンプと切替を1枚に載せたもので、旧 `RelayBoard` ×2 と
`AmpModule` ×10 を置き換えた（[AGENT_HANDOFF.md §2.9](AGENT_HANDOFF.md)）。

**箱配線が劇的に減ったのが刷新の実利。** 旧構成では Amp 1台につき電源3線＋入力2線の
端子台が要り、10台で 30本以上のケーブルがあった。いまは `AmpBank` へ行くのが
**電源3線・音声入力2線・音声出力2線・I²C 4線の計4本**だけで、ch 間の配線は基板上のパターンになった。

## 電源

| 系統 | 源（Value） | 先（Value） | 形式・注意 |
|---|---|---|---|
| アナログ ±15 V | PowerModule `+15/-15/A_GND out` | AmpBank `+15V / A_GND / -15V` | 端子台 3P。**1本だけ**（旧構成は RelayBoard ×2 へ2本） |
| トーン用 +9 V | PowerModule `VCC_TONE OUT` | ControlPanel PT2314 | 2P。星型の `A_GND` と二重ループにしない |
| PD 入力 | 外付け **50224 等** → PowerModule `PD module in` | 板上の PD 一次側 | 2P（トポロジ A） |
| PD 往復 | PowerModule（ヒューズ前） ⇄ ControlPanel パネル PWR SW | | **往復用端子が未実装**（下記「意図的未決」） |

12 V パネル LED は PWR SW の**後**に入れてあるので通電表示になる。
一次（`PD_GND`）と二次（`A_GND`）は DC-DC で絶縁されており、**繋がない**。

## A_GND / D_GND の分離（2026-08-31 確定）

`D_GND`（デジタル）と `A_GND`（アナログ・音声・±15 V 帰路）は
**システム全体で1箇所だけ** NetTie で結合する（[DECISIONS.md](DECISIONS.md) G1/G2）。

- **NetTie 位置: ControlPanel**（`D_GND` の発生源＝操作 Pico の直近）
- **AmpBank では結合しない。** AmpBank は `A_GND`（電源端子台経由、オペアンプとアナログスイッチ用）と
  `D_GND`（I²C コネクタ経由、MCP23017 用）の**両方を受け取るが、基板上で最後まで別ネットのまま**。
  ここで繋ぐと NetTie が2箇所目になり、グラウンドループになる

> 刷新でこの論点は**軽くなった**。旧 RelayBoard は AZ850 のコイル駆動電流が `D_GND` に流れており、
> それが `A_GND` へ回り込むことを警戒していた。アナログスイッチにはコイルが無く、
> `D_GND` 側に流れるのは MCP23017 のロジック電流だけになった。

## I²C

**ControlPanel → AmpBank の1本だけ。** コネクタは **4P**（`I2C_SDA` / `I2C_SCL` / `3V3` / `D_GND`）。

> **⚠ `+5V` は不要になった。** 旧 RelayBoard は AZ850 のコイル駆動に `+5V` が要ったので 5P だったが、
> AmpBank の I²C 機器は MCP23017（3.3 V ロジック）だけ。**旧文書の「5P」記述は古い。**

I²C 機器は PT2314 と OLED が ControlPanel 上、MCP23017 が AmpBank 上。
**基板をまたぐ I²C 配線は1本しかない**ので、旧「スター vs デイジー」の議論は実質消えた
（枝が1本ならどちらも同じ）。プルアップ（`I2C_SDA`/`I2C_SCL` → `3V3`、4.7 kΩ ×2）は
**ControlPanel の1箇所**に置いてある。

**番地ストラップは不要になった。** MCP23017 が1個だけなので A0–A2 は `D_GND` 固定（0x20）。
旧 RelayBoard の 2bit ストラップ（0x20–0x23、最大4枚）は
[AGENT_HANDOFF.md §2.6](AGENT_HANDOFF.md) に**不採用経路の記録**として残っている。

**ControlPanel 側のコネクタは回路図にまだ存在しない**（現状は OLED 用 4P のみ）。
実装時に AmpBank 側と同じピン順へ合わせる。

## 音声

| 系統 | 源（Value） | 先（Value） | ケーブル・シールド |
|---|---|---|---|
| トーン出力 | ControlPanel PT2314 出力 | AmpBank `TONE IN L/R` | **2芯シールド**。芯 = L/R。**シールドは ControlPanel 側の `A_GND` のみに落とす**（電源幹線とループさせない） |
| 選択アンプ出力 | AmpBank `AMP_SEL OUT L/R` | OutputStage `RAIL IN` | **2芯シールド**。シールドは OutputStage 側の `A_GND` のみ。`RAIL IN` は 3P で中央が `A_GND` |
| ヘッドホン | OutputStage `to Audio HP Buffer` | **`Audio/` HeadphoneBufferModule** 入力 | 図の外。0 Ω 固定パッドは廃止済み |
| ライン出力 | OutputStage `LINE OUT` | 前面 LINE OUT ジャック | |
| 外部入力 | 外部ソース | ControlPanel PT2314 入力 | 親では箱外スタブ（`COMMON_L/R`） |

音量ポット（HP / LINE とも A カーブ 50 kΩ 2連）と行き先スイッチ（`DEST L/R`）は
**パネル実装**で、基板へはリードで戻す（[PARTS.md](PARTS.md)）。

**ch 間の配線は箱内に無い。** 10ch 分の入力分配（`TONE_L/R`）と出力集約（`AMP_SEL_L/R`）は
AmpBank の基板パターンで、切替素子はオペアンプの直近にある。

## `Audio/`（v1）流用基板との接続

| 基板 | 接続 | 備考 |
|---|---|---|
| HeadphoneBufferModule | OutputStage `to Audio HP Buffer` ＋ ±15 V | |
| AdcBuffer / MeasurementADC | ±15 V ＋ 測定タップ（**位置 MD で固定**） | 別電源系統。**⚠ 2026-09-03 にスタック化へ方針変更**（[DECISIONS.md](DECISIONS.md)）。回路は v1 `rev 0.4` のまま、**外形とヘッダだけ AudioV2 のスタック規格へ合わせる**。この行のワイヤ接続は暫定 |
| v1 RelayBoard / AmpModule | **±15 V と音声で直結できる** | v1 の AmpModule は `NE5532` ＋受動部品だけで、電源は `AMP_V+_IN`/`AMP_V-_IN` という電圧非依存のネット名で受ける。**新旧アーキテクチャの実機比較用**（[DECISIONS.md §8](DECISIONS.md)） |

## 意図的未決

- **PD 入口トポロジ A（いまの図）vs B（パネル入口）** — 議論打ち切り。A なら Power↔Panel 往復端子が追加で必要
- ControlPanel 側 I²C コネクタ（4P）の物理選定（端子台 vs ピンヘッダ）と footprint
- GND NetTie の物理位置（ControlPanel 上のどこか）
- ENC / ノブの正確な秋月コード（在庫次第）
