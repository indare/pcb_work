# AudioV2 品番（回路から決めた第一候補）

**目的:** 回路が要求する電気・機械条件から、まだ空欄だった型番を埋める。在庫は変動するので **機能等価の代替** を併記する。

**実装の型（既存 `Audio/` と同じ）:** RV / SW_DEST / ENC / PWR SW は **パネル実装**。基板はヘッダ＋リード。RK27 を Control PCB に直付けしない。

参照: [DECISIONS.md](DECISIONS.md) §0・§3・§9・§10、[CIRCUIT_DESIGN.md](CIRCUIT_DESIGN.md)、[DEST_SENSE_LADDER.md](DEST_SENSE_LADDER.md)。

> **この文書の読み方 — どこが生成で、どこが手書きか**
>
> `<!-- BEGIN GENERATED: ... -->` 〜 `<!-- END GENERATED: ... -->` で囲まれたブロックは
> **回路図から自動生成**したもの（現在は §4.1 の AmpModule 部品表）。
> **手で編集しても次の再生成で消える。** 直すときは KiCad の回路図側を直して再生成する。
>
> それ以外はすべて**手書きで、こちらが正**。調達先・代替品・選定理由・C&K の現物端子対応・
> パネル/箱配線など、**回路図から導出できない情報**を置く場所。方針は
> [SOURCE_OF_TRUTH.md](../SOURCE_OF_TRUTH.md)。
>
> ```bash
> python3 AudioV2/scripts/gen_parts_bom.py          # 再生成して埋め込み直す
> python3 AudioV2/scripts/gen_parts_bom.py --check  # 実図とズレていれば非ゼロ終了（検査のみ）
> ```

---

## 0. 回路が課す制約（品番を決める前に）

| ブロック | 電気 | 機械 |
|---|---|---|
| **RV_HP / RV_LINE** | A カーブ 50 kΩ デュアル。Amp 後 ~7 Vrms → 素子 0.05 W で十分（7²/50k ≈ 1 mW） | **目立つノブ**。6 ピン（1/3=A, 4/6=B, 2/5=wiper）。基板はヘッダ |
| **SW_DEST** | 3 極 × ON-OFF-ON。音声 L/R + センス 1 極。電流 ≈ 7 V / 50 kΩ = **0.14 mA**（信号級で足りる） | パネル φ6.35 mm 級。はんだラグ → ヘッダ |
| **PWR SW** | DKMW 一次 ≈ **2 A @ 12 V**（20 W / η）+ LED | 3 A 以上。信号用ミニスイッチは不可 |
| **ENC×3** | A/B/SW、Pico 内部プルアップ | EC11、押し SW、D カット、固定足東西 |
| **DEST LED** | GP14/15、3.3 V、直列 1 kΩ | パネル 3–5 mm |
| **12 V LED** | SW 後 12 V、内蔵抵抗 ~10–15 mA | パネル 5 mm |
| **PT2314** | VDD 9 V、I²C、28 pin | **DIP-28**（ソケット可） |
| **AZ850** | コイルはControlPanel BP5293の **+5 V**（RelayBoardへ5P配線） | 2コイル・ラッチDPDT。audio/powerを同時駆動 |
| **OLED 制御** | I²C 0x3C、128×64、3.3 V、**SSD1306 互換**（実機は SSD1309 可） | 4 線（VCC/GND/SCL/SDA）。パネル or ヘッダ |
| **LCD スペアナ** | SPI（ST7796S）+ I²C タッチ（FT6336U）、5 V 可 | Waveshare **29318**。計測盤のみ |

---

## 1. 表示デバイス（v1 実装あり・確定）

AudioV2 は **表示が 2 系統**。DECISIONS の「OLED×2」は言い方が粗い — 実体は次。

| 役割 | 部品 | v1 実装 | AudioV2 での置き場 |
|---|---|---|---|
| **操作 UI** | **2.42″ OLED 128×64 I²C** | `Control/ssd1306.py` + `main.py`（`WIDTH=128 HEIGHT=64`、addr 0x3C、I2C0 GP20/21） | **ControlPanel** |
| **スペアナ** | **Waveshare 3.5″ タッチ LCD 320×480** | `Audio/measurement_fw/`（`lcd.py` ST7796S / `touch.py` FT6336U） | **MeasurementADC（`Audio/` 流用）**。AudioV2 KiCad には載せない |

### 1.0a 制御 OLED — AliExpress 2.42″（SSD1309 / SSD1306 互換）

| | |
|---|---|
| 例リンク | [a.aliexpress.com/_c3yp3JiX](https://a.aliexpress.com/_c3yp3JiX) → item **4000002579405** |
| 解像度 | **128×64**（v1 ファームと一致。**128×32 / 0.91″ は不可**） |
| コントローラ | 表記は **SSD1309** が多い。コマンドは SSD1306 と同系 → **既存 `ssd1306.py` のまま** |
| 配線 | Controll J17 と同型: **GND / 3V3 / SCL / SDA** → Pico GP21 / GP20 |
| バス | I²C0 **400 kHz**（100 kHz だと 1 KB フレームがタイムアウト — `Control/README.md`） |
| 表示内容 | CH / DEST / Bass / Treble。**音量は出さない** |

**代替:** 同ピン配列の **0.96″ SSD1306 128×64 I²C**（4 ピン）。ソフト変更なし。パネル穴・見た目だけ変わる。

**KiCad 注意:** 素案の `Display_Graphic:SSD1306-128x64` は埋め込み元が **ER_OLEDM0.91（128×32）** になっている。ピンは 4 本で足りるが **FP・寸法は 2.42″ 用に差し替え**（当面は `PinHeader_1x04` + 注記で可）。

### 1.0b スペアナ LCD — Waveshare **29318**（スイッチサイエンス）

| | |
|---|---|
| 販売 | [スイッチサイエンス 10138](https://www.switch-science.com/products/10138) / メーカー SKU **29318** |
| 表示 | 3.5″ IPS **320×480**、ST7796S、**4 線 SPI** |
| タッチ | FT6336U、**I²C**（静電容量） |
| 接続 | GH1.25 15P 付属 → 基板側 **1×15 ピンヘッダ**（`Audio/MeasurementADC_Extras:WAVESHARE-29318`） |
| 電源 | 3.3 / 5 V（オンボード LDO・レベルシフタ）。計測盤では `LCD_EN` で VCC 切 |

AudioV2 では **計測 Pico 配下のまま**。操作 Pico の I²C0 / SPI には載せない（DECISIONS §6・独立計測）。

---

## 2. 今回決めた第一候補（未定だったパネル部品）

### 2.1 SW_DEST — **C&K 7303SYZQE**

| | |
|---|---|
| 機能 | **3PDT ON-OFF-ON**（中央オープン＝MUTE） |
| 端子 | はんだラグ、パネル 1/4-40（穴 **φ6.35 mm**） |
| 定格 | 5 A / 120 VAC — 音声 0.14 mA に対し余裕。銀接点（QE）で可 |
| 並び（DECISIONS） | **上 LINE / 中 MUTE / 下 PHONE** |
| KiCad | 論理は `SW_DP3T`（L/R）+ `SW_SP3T`（センス）。**1 個の現物** |

**C&K 端子 → AudioV2 ネット**（DS: Pos1=2-3/5-6/8-9、Pos3=2-1/5-4/8-7、COM=2/5/8）

取り付けで「下＝PHONE」になるよう、レバー下向きで Pos1 が PHONE 側端子に来る向きにする。

| 現物端子 | 役割 | 基板ヘッダ（音声 2×4 + センス 1×3） |
|---|---|---|
| 2 | L COM | SW601-3 `AMP_SEL_L` |
| 3 | L PHONE（Pos1） | SW601-1 → RV601 |
| 1 | L LINE（Pos3） | SW601-4 → RV602 |
| （L MUTE） | 開放 | SW601-2 NC |
| 5 | R COM | SW602-3 `AMP_SEL_R` |
| 6 | R PHONE | SW602-1 → RV601 |
| 4 | R LINE | SW602-4 → RV602 |
| 8 | センス COM | → DEST_ADC（GP26） |
| 9 | センス PHONE | → Rs=1 kΩ → GND |
| 7 | センス LINE | → Rs=1 kΩ → 3V3 |
| （センス MUTE） | 開放 | ラダー中点のまま |

**代替**

| 状況 | 型番 | 備考 |
|---|---|---|
| 7303 欠品 | **NKK S38** | 同じく 3PDT ON-OFF-ON。穴 **φ12.5 mm**・大きい。RS 流通 |
| ミニ 3PDT 全滅 | **C&K 7203SYZQE**（音声 DPDT）+ **7103SYZQE**（センス SPDT） | 穴 2 個。UX は劣るが両方とも流通が多い |
| NKK ミニ | M2033SSxxW01 | 機能は同じだが **一部 suffix が EOL**。在庫確認必須 |

4PDT（C&K 7403）は余 1 極を NC にして使ってよい（将来アース切等）。

### 2.2 RV_HP / RV_LINE — **Alps RK27112A00CF** ×2

| | |
|---|---|
| 機能 | **A（対数）50 kΩ デュアル**、カーボン、1 回転 |
| 外形 | RK27 **27 mm**、軸 φ6 × 20 mm、取付 M9 |
| 電力 | 0.05 W — 本回路の ~1 mW に対し十分 |
| ギャング誤差 | DS 目安 2 dB（-60〜0 dB）— ステレオ音量として実用 |
| 実装 | **パネル**。基板は 6P ヘッダ（`Device:R_Potentiometer_Dual` ピン番号のまま） |
| なぜ RK097 でないか | 現行 Audio は RK097 水平実装。AudioV2 は **ノブを主操作子**にするので 27 mm を第一にする |

**代替**

| 状況 | 内容 |
|---|---|
| RK27 欠品・高い | パネル用 **A50k デュアル**ならピン互換で可（台湾 Alpha RD901 系など）。カーブが **A** であること |
| 現行機と見た目を揃える | Alps **RK097 デュアル A50k**（水平ピン）。9 mm で「目立たない」。回路は同一 |
| A100k | 可（DECISIONS）。中点 Zout が上がるので **A50k 優先** |

RK097 のカタログ現役は 10 kΩ デュアルが多く、**A50k デュアルは RK27 の方が型番が取りやすい**。

### 2.3 その他・回路上まだ曖昧だったもの

| 用途 | 第一候補 | 理由 |
|---|---|---|
| **ENC×3** | 秋月 **EC11 系・押し SW 付き**（D カット、固定足東西） | DECISIONS どおり。PPR は CH/Bass/Treble では何周でも可。購入品の寸法で FP を切る |
| **操作 Pico** | **Raspberry Pi Pico 2**（RP2350、**W なし**、SC0915 相当） | Wi-Fi 不要。ヘッダ後付け可 |
| **OLED（制御）** | **2.42″ 128×64 I²C**（SSD1309、SSD1306 互換）— [AliExpress 例](https://a.aliexpress.com/_c3yp3JiX) / item `4000002579405` | v1 `Control/` と同じ。`WIDTH=128 HEIGHT=64`、addr **0x3C**、GP20/21。**0.96″ でも動くが、現行機は 2.42″** |
| **LCD（スペアナ）** | **Waveshare 29318**（スイッチサイエンス [10138](https://www.switch-science.com/products/10138)） | v1 `Audio/measurement_fw/`。ST7796S SPI + FT6336U I²C。**MeasurementADC 流用**（AudioV2 Control には載せない） |
| **PWR SW** | **C&K 7101SYZQE**（SPDT ON-ON、5 A、ラグ）を SPST として使用 | 12 V / ~2 A。ミニ信号 SW 禁止 |
| **12 V LED** | **12 V 内蔵抵抗付き 5 mm**（緑または青、~10 mA） | DECISIONS §9。素 LED なら 680 Ω–1 kΩ |
| **DEST LED×2** | 3 mm 通常 LED（Vf≈2 V）+ 既存 **1 kΩ** | 3.3 V で ~1.3 mA。暗ければ 330 Ω に落とす |
| **AZ850** | **AZ850P2-5**（秋月 118017） | コイル **5 V** / 125 Ω / ~40 mA。ULN2803 + BP5293-50 と一致。**12 V コイルは使わない** |
| **MCP23017** | **MCP23017-E/SP**（DIP-28）×盤ごとに1 | JP A1/A0 で 0x20–0x23（最大4枚）。A2=0 |
| **ULN2803** | **ULN2803AN**（DIP-18）×4（各RelayBoardに2） | SET用/RESET用。1出力でaudio+pwr 2コイル（約80 mA）、COMは+5 V |
| **PT2314** | **PT2314 DIP-28**（回路値 `PT2314-D`） | Princeton DS 28 pin。SOP は初号では使わない |
| **+9 V LDO** | **ST L7809CV**（TO-220） | PT2314 typ 30 mA → 散逸 (12-9)×30 mA ≈ 0.09 W |
| **F201** | **5×20 mm T3.15 A**（または図の 3 A スロー） | 一次 ~2 A。ガラス管スローブロー |
| **BP5293** | **BP5293-50**（秋月 111188） | 現行 Audio と同じ +5 V |
| **DKMW / CH224** | **DKMW20F-12** / **50224（CH224K 12 V）** | 既確定 |
| **USB-C** | USB2.0 16P レセプタクル（KiCad `USB_C_Receptacle_USB2.0_16P`） | CC はモジュール側。基板は VBUS/GND が主 |
| **ラダー R** | 10 k / 10 k / 1 k **1%**（1206 可） | ±5% でも間隔は足りるが、初号は 1% |
| **J_I2C（ControlPanel↔RelayBoard 5P）** | **Phoenix Contact MKDS-1,5シリーズ**（5.08 mmピッチ、ネジ式）互換品または同一品。KiCad FP: `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-N-5.08_1xNN_P5.08mm_Horizontal`（Nはピン数、5Pなら`5`/`05`） | `Audio/Controll.kicad_sch`（v1の「リレー＋端子台＋ULN」原型）で13箇所使用実績あり。フェルール対応で、スター配線をControlPanel側1コネクタ＋箱内フェルール束ね/スプリッタで実現する方針（WIRING.md）と合う |

---

## 3. ピン・配線メモ（購入後に間違えないため）

```text
Amp 選択後 L/R
    → 7303 極1/極2 COM
         下 PHONE → RK27 (RV601) CW ← wiper → HP Buffer
         中 MUTE  → NC
         上 LINE  → RK27 (RV602) CW ← wiper → LINE OUT
    → 7303 極3 COM → ADC
         下 → Rs → GND     = PHONE
         上 → Rs → 3V3     = LINE
```

ポット: **CW（時計回りで音量大）= SW 側（HOT）**、CCW = `A_GND`、ワイパー = 出力。A カーブは CCW 側が急に落ちる。

---

## 4. AmpModule 再版（1枚あたり、×10）

### 4.1 部品表（回路図から自動生成）

<!-- BEGIN GENERATED: ampmodule-bom -->
**AmpModule 1 枚あたりの部品表** — 下の表は `AudioV2/AmpModule.kicad_sch` から自動生成しています。
**手で編集しないでください**（次の再生成で消えます）。値・フットプリント・役割を直すときは KiCad の回路図側を直し、
`python3 AudioV2/scripts/gen_parts_bom.py` で再生成します。

> `Refs` 列と `Value` / `Role` 列に**位置の対応はありません**。kicad-cli はグループ内の値を重複除去してアルファベット順に並べるため、「n 番目の参照 = n 番目の役割」とは読めません。

| Refs | Value | Footprint | Qty | Role |
|---|---|---|---|---|
| AMP701 | NE5532 / DIP-8 compatible | `Package_DIP:DIP-8_W7.62mm_Socket` | 1 | AudioV2 replaceable dual op amp; high-speed decoupling fitted |
| C701,C704 | 100nF film | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 2 | L input film coupling / R input film coupling |
| C702,C705 | 10uF | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` | 2 | L input electrolytic coupling / R input electrolytic coupling |
| C703,C706 | 470uF 25V | `Capacitor_THT:CP_Radial_D12.5mm_P5.00mm` | 2 | L output coupling; compact D12.5/P5 / R output coupling; compact D12.5/P5 |
| C707,C708 | 100uF 35V polymer | `Capacitor_SMD:CP_Elec_10x12.6` | 2 | V+ local bulk at power connector / V- local bulk at power connector |
| C709,C710 | 100nF 50V X7R | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 2 | V+ local decoupling / V- local decoupling |
| C711,C712 | 1nF 50V C0G | `Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder` | 2 | V+ high-speed bypass / V- high-speed bypass |
| J701 | AMP_IN L/R | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | 1 |  |
| J702 | AMP_OUT L/R | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | 1 |  |
| J703 | +12V / A_GND / -12V | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 1 |  |
| R701,R706 | 220k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L input pulldown / R input pulldown |
| R702,R707 | 1k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L non-inverting bias; 1/10 refine / R non-inverting bias; 1/10 refine |
| R703,R708 | 47R | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 2 | L output isolation / R output isolation |
| R704,R705,R709,R710 | 20k | `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | 4 | L feedback; gain 2 / L gain resistor; Rf=Rg=20k / R feedback; gain 2 / R gain resistor; Rf=Rg=20k |
<!-- END GENERATED: ampmodule-bom -->

### 4.2 選定・実装メモ（回路図から導出できない＝ここが正）

| 項目 | 内容 |
|---|---|
| **OpAmp の差し替え条件** | 基準は **NE5532P**。DIP-8 **ソケット**実装なので現物差し替えで聴き比べできる。他の DIP-8 互換デュアルに替えるときは **±12 V 動作・ユニティゲイン安定・容量負荷耐性** を DS で確認する（手持ち在庫は [`Audio/OPAMP_INVENTORY.md`](../Audio/OPAMP_INVENTORY.md)） |
| **SMD バイパスコンデンサの寸法** | `100nF X7R` / `1nF C0G` とも **1206 が既定**（回路図の Footprint も 1206）。ハンドはんだ前提のため大きめを選んでいる。**レイアウト都合で 0603 まで下げるのは可**（削除した旧 PCB では `1nF C0G` を裏面 0603 にしていた）。下げる場合は回路図の Footprint も合わせて変更すること |
| **PCB 外形（未設計・着手時の要件）** | AmpModule の PCB はまだ設計していない。着手するときは `Audio/split/AudioCase_4_amp.kicad_pcb` を参考に、**端子位置と 4 穴位置を維持**し、100 µF ポリマー×2 を載せるため**上辺のみ 15 mm 拡張**する。ソースの `Audio/` 基板は変更しない |

## 5. まだ買わなくてよい / レイアウト時

| 項目 | 状態 |
|---|---|
| ENC 正確な秋月コード | 在庫を見て同一外形を 3 個 |
| PT2314 入手先 | DigiKey に無いことが多い。LCSC / モジュール屋。DIP ソケット推奨 |
| ノブ（φ6 D カット） | RK27 用に大きめ。ENC 用は小さめ |
| RelayBoard シルク | JP横に A1/A0→0x20–0x23 早見表（同一PCB使い回し） |

---

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-30 | 初版 — 回路制約から SW_DEST / RV / 周辺の第一候補を固定 |
| 2026-08-30 | 表示 — 制御 OLED=2.42″ SSD1309（AliExpress）、スペアナ=Waveshare 29318（v1 実装） |
| 2026-08-31 | AmpModule再版 — ゲイン2（20k/20k）、バルク/高速バイパス、出力C小型化 |
| 2026-08-31 | J_I2C端子台をPhoenix MKDS-1,5シリーズ（v1 `Audio/Controll.kicad_sch`と同一/互換）に確定。§11 Q3（JST-XH vs 2.54）は解消 |
| 2026-09-01 | AmpModule 部品表を回路図からの**自動生成**に切替（§4.1）。手書きの designator 表を廃止し、非導出情報だけを §4.2 に残した。生成: `AudioV2/scripts/gen_parts_bom.py` |
