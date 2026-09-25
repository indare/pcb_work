# 電源系 — データシートの事実

2026-09-25 収集。値は DS の原文で裏が取れたものだけ。設計判断は書かない。
2026-09-25 にページ画像と照合した（照合結果 [verify_power.md](verify_power.md)、その再判定 [../review/ds_errata_review.md](../review/ds_errata_review.md)）。その結果で直した行・足した行は、行末に 〔2026-09-25 照合で訂正〕／〔2026-09-25 照合で追加〕 を付けた。

- 出典のページは PDF のページ番号（どの DS も印刷ページ番号と一致）。PDF はすべて `AudioV2.1/datasheets/` にある。
- 「列」はその値が表のどの列に印刷されているか。表に min/typ/max の列が無いものは「値の列のみ」と書き、値に付いた `typ.` などの字句はそのまま残した。
- 「画像で確認」は、`pdftotext` の抽出で列や記号が崩れる／紛らわしいため、ページを画像にして表の罫線と列見出しを目で確かめたもの。
- 「目読み」はグラフの値。ページを 300 dpi の画像にして、軸の格子線の画素位置で目盛りを較正し、指定した周波数の列で曲線の画素を拾って換算した（誤差 ±2 dB 程度。PSRR が急に変わる帯域ではもっと大きい）。

---

## 1. Recom RS6-1215D（RS6 シリーズ、SIP8、6 W）

出典: `Recom_RS6.pdf`（REV.: 10/2024、全 7 ページ。2026-09-24 に recom-power.com から取り直したものとバイト一致）

**⚠ p2〜p7 の各ページ見出しにある測定条件:** *"Specifications (measured @ Ta= 25°C, nominal input voltage, full load and after warm up unless otherwise specified)"*。以下で「見出し条件」と書くのはこれ。

### 選定表（p1、モデル別の行）

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 入力電圧範囲 | 9 - 18 VDC | RS6-1215D の行 | 選定表（min/typ/max の列なし） | Recom_RS6.pdf p1 | "RS6-1215D 9 - 18 ±15 ±200 87 ±660" |
| 出力電圧 | ±15 VDC | 同上 | 同上 | p1 | 同上 |
| 出力電流 | ±200 mA | 同上 | 同上（"Output Current [mA]"。min/max の区別なし） | p1 | 同上 |
| 効率 | 87 % | Note1: 公称入力・全負荷・+25°C | 列見出し "Efficiency typ. (1)" | p1 | "Note1: Efficiency is tested by nominal input and full load at +25°C ambient" |
| 最大容量性負荷 | ±660 µF | Note2: 最小入力・定抵抗負荷で試験 | 列見出し "max. Capacitive Load (2)" | p1 | "Note2: Max Cap Load is tested by minimum input and constant resistor load" |

### BASIC CHARACTERISTICS（p2）— 表全体を画像で確認

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 入力フィルタ | capacitor | — | Min〜Max の結合セル | p2 | "Input Filter ... capacitor" |
| 入力電圧範囲 | 9 / 12 / 18 VDC | nom. Vin = 12VDC | Min / Typ / Max | p2 | "Input Voltage Range nom. Vin= ... 12VDC 9VDC 12VDC 18VDC" |
| 入力サージ電圧 | 25 VDC | 1 second max.、nom. Vin = 12VDC | Max | p2 | "Input Surge Voltage 1 second max. nom. Vin= ... 12VDC ... 25VDC" |
| "Quiescent Current"（DS の字句のまま。負荷の条件は書かれていない。値の大きさからは無負荷時と読めるが DS はそう書いていない） | 55 mA | nom. Vin の2行目。**条件欄の印字は "2VDC"**（行の並びは 5VDC / 2VDC / 24VDC / 48VDC で、12VDC の位置。画像でも "2VDC"） | **Max** | p2 | "Quiescent Current nom. Vin= 5VDC 2VDC 24VDC 48VDC ... 105mA 55mA 28mA 14mA" 〔2026-09-25 照合で訂正〕 |
| 出力電圧トリム | +10 % / -8 % | Trim up / Trim down、"see calculation on next page" | Max | p2 | "Output Voltage Trimming see calculation on next page Trim up +10% Trim down -8%" |
| 起動時間 | 2 ms | — | Typ | p2 | "Start-up Time 2ms" |
| 低電圧ロックアウト | ON 9 VDC / OFF 7 VDC | nom. Vin = 12V | Typ | p2 | "nom. Vin= 12V DC-DC ON 9VDC DC-DC OFF 7VDC" |
| ON/OFF CTRL（ON） | Open | DC-DC ON | Min〜Max の結合セル（右寄せ） | p2 | "ON/OFF CTRL DC-DC ON Open" |
| ON/OFF CTRL（OFF） | 5V < Vr < 12VDC | DC-DC OFF | Min〜Max の結合セル（右寄せ） | p2 | "DC-DC OFF 5V<Vr<12VDC" |
| CTRL の論理（注記） | high = OFF、high Z = ON、low は不可 | Note7（p7） | — | p7 | "Note7: This pin provides an Off function which puts the converter into a low power mode. When the pin is 'high' the converter is OFF and when the pin is high 'Z' the converter is ON. There is no allowed low state for this pin" |
| CTRL ピン入力電流 | 1.5 / 2.5 / 3.3 mA | 条件欄空 | Min / Typ / Max | p2 | "Input Current of CTRL Pin 1.5mA 2.5mA 3.3mA" |
| 待機電流 | 2 mA | 条件欄空 | Typ | p2 | "Standby Current 2mA" |
| **内部動作周波数** | **200 kHz** | 条件欄 **"0-100% load"**（見出し条件の "full load" ではなく、行の条件欄で 0〜100 % 負荷と明示） | **Min. 列**（Typ・Max は空欄。画像で確認） | p2 | "Internal Operating Frequency 0-100% load 200kHz" |
| 最小負荷 | 0 % | 条件欄空 | **Typ**（画像で確認） | p2 | "Minimum Load 0%" |
| 出力リップル＆ノイズ | 50 mVp-p / 75 mVp-p | 20MHz BW。Note3: 出力に 1.0 µF MLCC。負荷・入力は見出し条件（公称入力・全負荷） | Typ / Max | p2 | "Output Ripple and Noise (3) 20MHz BW 50mVp-p 75mVp-p" / "Note3: Measurements are made with a 1.0µF MLCC across output (low ESR)" |

### 出力電圧トリム（p3〜p4）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| トリム回路の対象 | 回路図と計算表は **3.3V / 5V / 12V / 15V の単出力**（表題 "RS6-xx03.3S / xx05S / xx12S / xx15S"）のみ | — | — | p3, p4 | "Vout 3.3V 5V 12V 15V"、"RS6-xx15S Trim up ..." |
| デュアル品の 5 番ピン | NC（単出力では Trim） | ピン表 | — | p7 | "Pin # Single Dual ... 5 Trim NC" |
| 15V 品の内部定数 | R1 = 50 kΩ、R2 = 10 kΩ、R3 = 68 kΩ、Vref = 2.5 V | 単出力 15V の列 | — | p3（画像で確認） | "Vout ... 15V / R1 ... 50kΩ / R2 10kΩ / R3 ... 68kΩ / Vref ... 2.5V" |

### REGULATIONS（p4）— 表の列は Parameter / Condition / Values の3列のみ（画像で確認）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力精度 | ±1.0 % typ. | 条件欄空 | 値の列のみ（字句 "typ."。max は記載なし） | p4 | "Output Accuracy ±1.0% typ." |
| ライン・レギュレーション | ±0.2 % typ. | low line to high line | 同上 | p4 | "Line Regulation low line to high line ±0.2% typ." |
| ロード・レギュレーション | 1.0 % typ. | 0% to 100% load | 同上 | p4 | "Load Regulation 0% to 100% load 1.0% typ." |
| クロス・レギュレーション | ±5.0 % typ. | 25% to 100% load | 同上 | p4 | "Cross Regulation 25% to 100% load ±5.0% typ." |
| 過渡応答 | 500 µs typ. | 25% load step change | 同上 | p4 | "Transient Response 25% load step change 500µs typ." |

### PROTECTIONS / ENVIRONMENTAL（p5）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 短絡保護 | continuous, automatic recovery | 条件 "below 100mΩ"（**抽出テキストでは "100mW" と化けるが、画像では mΩ**） | 値の列のみ | p5（画像で確認） | "Short Circuit Protection (SCP) below 100mΩ continuous, automatic recovery" |
| 過負荷保護 | 150% load, continuous, automatic recovery | — | 値の列のみ | p5 | "Over Load Protection (OLP) 150% load, continuous, automatic recovery" |
| 絶縁耐圧 | 2 kVDC（1 秒試験）/ 1.6 kVDC（1 分定格） | I/P to O/P | 値の列のみ | p5 | "Isolation Voltage (4) I/P to O/P tested for 1 second 2kVDC rated for 1 minute 1.6kVDC" |
| **絶縁容量** | **110 pF max.** | 条件欄空 | 値の列のみ（字句 "max."） | p5 | "Isolation Capacitance 110pF max." |
| 絶縁抵抗 | 1 GΩ typ. | — | 値の列のみ | p5 | "Isolation Resistance 1GΩ typ." |
| 絶縁グレード | functional | — | — | p5 | "Isolation Grade functional" |
| 動作温度 | -40 °C 〜 +75 °C | full load (see graph)。ディレーティング図は RS6-0505S のもの（Note5） | 値の列のみ | p5 | "Operating Temperature Range (5) full load (see graph) -40°C to +75°C" / "Note5: Derating Graph is referring to RS6-0505S." |
| 最大ケース温度 | +105 °C | — | 値の列のみ | p5 | "Maximum Case Temperature +105°C" |
| 温度係数 | ±0.02 %/°C | — | 値の列のみ | p5 | "Temperature Coefficient ±0.02%/°C" |

### 外付け部品の推奨（p6）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| EMC フィルタ推奨値の対象モデル | RS6-053.3S / RS6-1205S / RS6-2412D / RS6-483.3S・RS6-4815S のみ。**RS6-1215D の行は無い** | Note6 | — | p6（画像で確認） | "Note6: Filter suggestions are valid for indicated part numbers only. For other part numbers, please contact RECOM tech support for advice." |
| EMC フィルタ（参考: RS6-1205S） | Class A: C1 10µF, L1 47µH, C3 1nF / Class B: C2 4.7µF, L1 18µH (RLS-186), CMC1 1mH, C3 100pF, C4 100pF, CMC2 11µH | 12V 入力の単出力品 | — | p6（画像で確認） | "RS6-1205S A 10µF N/A 47µH N/A 1nF N/A N/A / B N/A 4.7µF 18µH, RLS-186 1mH 100pF 100pF 11µH" |
| サージ保護（EN61000-4-5） | Csurge = 100V, 220µF E/Cap（5V / 12・24・48V 共通の結合セル）、Dsurge = N/A（12・24・48V）、max. Surge ±1kVDC | nom. VIN = 12, 24, 48VDC | — | p6（画像で確認） | "12, 24, 48VDC ... 100V, 220µF E/Cap ... N/A ... ±1kVDC" |

### ピン配置・外形（p7）— 図を画像で確認

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ピン配置（Dual） | 1 -Vin / 2 +Vin / 3 CTRL / 5 NC / 6 +Vout / 7 Com / 8 -Vout。**4 番ピンは無い**（図・表とも 1 2 3 _ 5 6 7 8） | — | — | p7 | "Pin # Single Dual 1 -Vin -Vin 2 +Vin +Vin 3 CTRL (7) CTRL (7) 5 Trim NC 6 +Vout +Vout 7 -Vout Com 8 NC -Vout / NC= no connection" |
| 外形 | 21.8 x 9.2 x 11.1 mm（L x W x H） | — | — | p7 | "Dimension (LxWxH) 21.8 x 9.2 x 11.1mm" |
| ピンピッチ | 2.54 mm、1 番〜8 番ピン中心間 7 x 2.54 = 17.78 mm | 公差 Pin pitch ±0.25mm | — | p7 | "7x2.54= 17.78" / "Pin pitch: ±0.25mm" |
| 1 番ピン中心〜筐体端 | 2.00 mm | Bottom View | — | p7 | "2.00" |
| ピン列〜筐体面 | 3.20 mm | Bottom View（ピン列から図の下辺まで） | — | p7 | "3.20" |
| ピン断面 | 0.51 (+0.10/-0.05) x 0.25 ±0.05 mm | — | — | p7 | "0.51+0.10/-0.05" "0.25±0.05" |
| ピン長 / スタンドオフ | 4.10 mm / 0.50 mm | 側面図 | — | p7 | "4.10" "0.50" |
| 推奨穴径 | Ø 1.00 +0.15/-0 mm | Recommended Footprint Details | — | p7 | "Recommended Footprint Details 1.00 Ø +0.15/-0" |
| 寸法公差 | xx.x = ±0.5 mm、xx.xx = ±0.25 mm、ピン寸法 ±0.1 mm | — | — | p7 | "Tolerance: xx.x= ±0.5mm xx.xx= ±0.25mm Pin dimension: ±0.1mm" |
| 質量 | 4.0 g | — | — | p7 | "Weight 4.0g" |

**同じ DS の中での食い違い（原文のまま）:** p1 Features は "1.6kVDC/1 minute isolation"、p1 Description は "2kVDC isolation"（p5 の表では 2 kVDC は 1 秒試験、1.6 kVDC は 1 分定格）。

### 探したが DS に無かった項目（RS6）

- **推奨入力ヒューズ**（"fuse" は文書中に 0 件）
- 外付けの入出力コンデンサの推奨値（EMC フィルタとサージ保護の例のみ。RS6-1215D は EMC 表の対象外）
- 最小負荷の max／min 値（Typ 0 % のみ）
- 内部動作周波数の Typ・Max 値、軽負荷での周波数の振る舞い（Min 200 kHz・"0-100% load" のみ）
- 出力精度・ライン・負荷・クロスレギュレーションの **max 値**（すべて typ. のみ）
- CTRL の電圧 Vr の基準ピン（"5V<Vr<12VDC" とあるだけで、どのピン基準かは書いていない）
- **デュアル品の出力電圧トリム**（トリムの回路・表は単出力のみ。デュアルの 5 番ピンは NC。「デュアルは不可」と明記した文は無い）
- 12V 入力品の "Quiescent Current" 行の条件の正しい表記（印字は "2VDC"）
- RS6-1215D のディレーティング曲線（図は RS6-0505S のもの）

---

## 2. TI TPS7A49（正電圧 LDO、36 V / 150 mA）

出典: `TI_TPS7A49.pdf`（SBVS121E – AUGUST 2010 – REVISED MAY 2015、Rev. E。2026-09-24 に ti.com の symlink から取り直したものとバイト一致）

**EC 表（p6）の見出し条件:** *"At TJ = –40°C to 125°C, VIN = VOUT(nom) + 1 V or VIN = 3 V (whichever is greater), VEN = VIN, IOUT = 1 mA, CIN = 2.2 μF, COUT = 2.2 μF, CNR/SS = 0 nF, and the FB pin tied to OUT, unless otherwise noted. Typical values are at TA = 25°C."*（EC 表は画像で列を確認）

### ピン配置（DGN = 8-Pin HVSSOP PowerPAD、p4）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ピン配置 | 1 OUT / 2 FB / 3 NC / 4 GND / 5 EN / 6 NR/SS / 7 DNC / 8 IN / PowerPAD | DGN（DRB VSON-8 も同じ番号） | — | p4（画像で確認） | "OUT 1 8 IN / FB 2 7 DNC / NC 3 6 NR/SS / GND 4 5 EN" |
| DNC（7） | どのネットにもつながない | — | — | p4 | "Do not connect. Do not route this pin to any electrical net, not even GND or IN." |
| NC（3） | 開放または GND | — | — | p4 | "Not internally connected. This pin can either be left open or tied to GND." |
| OUT（1） | ≥ 2.2 µF を GND へ | — | — | p4 | "A capacitor ≥ 2.2 μF must be tied from this pin to ground to ensure stability." |
| PowerPAD | 開放または GND。基板のプレーンにはんだ付け | — | — | p4 | "Must either be left open or tied to ground. Solder to the printed-circuit-board (PCB) plane to enhance thermal performance." |
| EN（5） | 未使用なら IN へ接続可。VEN ≤ VIN | — | — | p4 | "The EN pin can be connected to IN, if not used. VEN ≤ VIN." |

### 絶対最大定格（p5）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| IN – GND | -0.3 / 36 V | — | MIN / MAX | p5 | "IN pin to GND pin –0.3 36 V" |
| OUT – GND | -0.3 / 33 V | — | MIN / MAX | p5 | "OUT pin to GND pin –0.3 33 V" |
| OUT – IN | -36 / 0.3 V | — | MIN / MAX | p5 | "OUT pin to IN pin –36 0.3 V" |
| FB – GND | -0.3 / 2 V | — | MIN / MAX | p5 | "FB pin to GND pin –0.3 2 V" |
| FB – IN | -36 / 0.3 V | — | MIN / MAX | p5 | "FB pin to IN pin –36 0.3 V" 〔2026-09-25 照合で追加〕 |
| EN – IN | -36 / 0.3 V | — | MIN / MAX | p5 | "EN pin to IN pin –36 0.3 V" |
| EN – GND | -0.3 / 36 V | — | MIN / MAX | p5 | "EN pin to GND pin –0.3 36 V" |
| NR/SS – GND | -0.3 / 2 V | — | MIN / MAX | p5 | "NR/SS pin to GND pin –0.3 2 V" |
| NR/SS – IN | -36 / 0.3 V | — | MIN / MAX | p5 | "NR/SS pin to IN pin –36 0.3 V" 〔2026-09-25 照合で追加〕 |
| TJ | -40 / 125 °C | Operating virtual junction | MIN / MAX | p5 | "Operating virtual junction, TJ –40 125 °C" |

### 推奨動作条件（p5）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| VIN | 3 / 35 V | — | MIN / MAX | p5 | "VIN Input supply voltage 3 35 V" |
| VEN | 0 / VIN | — | MIN / MAX | p5 | "VEN Enable supply voltage 0 VIN V" |
| VOUT | VFB / 33 V | — | MIN / MAX | p5 | "VOUT Output voltage VFB 33 V" |
| IOUT | 0 / 150 mA | — | MIN / MAX | p5 | "IOUT Output current 0 150 mA" |
| CIN | 2.2 / 10 µF | — | MIN / NOM | p5 | "CIN Input capacitor 2.2 10 µF" |
| COUT | 2.2 / 10 µF | — | MIN / NOM | p5 | "COUT Output capacitor 2.2 10 µF" |
| CNR | 0 / 10 nF | — | MIN / NOM | p5 | "CNR Noise reduction capacitor 0 10 nF" |
| CFF | 0 / 10 nF | — | MIN / NOM | p5 | "CFF Feed-forward capacitor 0 10 nF" |
| R2（下側帰還抵抗） | 237 kΩ | — | MAX | p5 | "R2 Lower feedback resistor 237 kΩ" |

### 熱特性（p6）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| RθJA | 63.4 °C/W（DGN）/ 47.7 °C/W（DRB） | — | パッケージ別の列 | p6 | "RθJA Junction-to-ambient thermal resistance 63.4 47.7 °C/W" |
| RθJC(top) | 53 / 55.3 °C/W | — | 同上 | p6 | "RθJC(top) ... 53 55.3" |
| RθJB | 37.4 / 23.3 °C/W | — | 同上 | p6 | "RθJB ... 37.4 23.3" |
| ψJT / ψJB | 3.7 / 37.1 °C/W（DGN） | — | 同上 | p6 | "ψJT ... 3.7 1.1" "ψJB ... 37.1 23.5" |
| RθJC(bot) | 13.5 / 7.0 °C/W | — | 同上 | p6 | "RθJC(bot) ... 13.5 7.0" |

### 電気的特性（p6）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| VREF | 1.176 / 1.188 / 1.212 V | TJ = 25°C, VNR/SS = VREF（NR/SS ピンで測定、注1） | MIN / TYP / MAX | p6 | "VREF Internal reference (1) TJ = 25°C, VNR/SS = VREF 1.176 1.188 1.212 V" |
| VFB | 1.185 V | — | TYP | p6 | "VFB Feedback voltage 1.185 V" |
| 出力電圧範囲 | VREF 〜 33 V | VIN ≥ VOUT(nom) + 1 V。注2: 無負荷安定に帰還抵抗網の電流 ≥ 5 µA | MIN / MAX | p6 | "(2) To ensure stability at no load conditions, a current from the feedback resistive network equal to or greater than 5 μA is required." |
| 公称精度 | ±1.5 %VOUT | TJ = 25°C, VIN = VOUT(nom) + 0.5 V | MIN / MAX | p6 | "Nominal accuracy TJ = 25°C, VIN = VOUT(nom) + 0.5 V –1.5 1.5 %VOUT" |
| 総合精度 | ±2.5 %VOUT | VOUT(nom)+1 V ≤ VIN ≤ 35 V, 1 mA ≤ IOUT ≤ 150 mA | MIN / MAX | p6 | "Overall accuracy ... –2.5 2.5 %VOUT" |
| ライン・レギュレーション | 0.086 %VOUT | TJ = 25°C, VOUT(nom)+1 V ≤ VIN ≤ 35 V | TYP | p6 | "Line regulation ... 0.086 %VOUT" |
| ロード・レギュレーション | 0.04 %VOUT | TJ = 25°C, 1 mA ≤ IOUT ≤ 150 mA | TYP | p6 | "Load regulation ... 0.04 %VOUT" |
| ドロップアウト | 260 mV | VIN = 95% VOUT(nom), IOUT = 100 mA | TYP（MAX 空欄） | p6 | "VDO Dropout voltage VIN = 95% VOUT(nom), IOUT = 100 mA 260 mV" |
| ドロップアウト | 333 / 600 mV | VIN = 95% VOUT(nom), IOUT = 150 mA | TYP / MAX | p6 | "VIN = 95% VOUT(nom), IOUT = 150 mA 333 600 mV" |
| 電流制限 | 220 / 309 / 500 mA | VOUT = 90% VOUT(nom) | MIN / TYP / MAX | p6 | "ILIM Current limit VOUT = 90% VOUT(nom) 220 309 500 mA" |
| GND 電流 | 49 / 100 µA | IOUT = 0 mA | TYP / MAX | p6 | "IGND Ground current IOUT = 0 mA 49 100 μA" |
| GND 電流 | 800 µA | IOUT = 100 mA | TYP | p6 | "IOUT = 100 mA 800 μA" |
| シャットダウン電流 | 0.8 / 3 µA | VEN = 0.4 V | TYP / MAX | p6 | "ISHDN Shutdown supply current VEN = 0.4 V 0.8 3 μA" |
| FB 電流 | 3 / 100 nA | 注3: 流れ出す向きが正 | TYP / MAX | p6 | "IFB Feedback current (3) 3 100 nA" |
| EN 電流 | 0.02 / 1 µA、0.2 / 1 µA | VEN = VIN = VOUT(nom)+1 V ／ VEN = VIN = 35 V | TYP / MAX | p6 | "IEN Enable current ... 0.02 1 μA ... VEN = VIN = 35 V 0.2 1 μA" |
| **EN high 閾値** | 2.1 V 〜 VIN | — | MIN / MAX | p6 | "VEN(high) Enable high-level voltage 2.1 VIN V" |
| **EN low 閾値** | 0 〜 0.4 V | — | MIN / MAX | p6 | "VEN(low) Enable low-level voltage 0 0.4 V" |
| 出力雑音 | 15.4 µVRMS | VIN = 3 V, VOUT(nom) = VREF, COUT = 10 µF, CNR/SS = 10 nF, 10 Hz〜100 kHz | TYP | p6 | "VIN = 3 V, VOUT(nom) = VREF, COUT = 10 μF, CNR/SS = 10 nF, BW = 10 Hz to 100 kHz 15.4 μVRMS" |
| 出力雑音 | 21.15 µVRMS | VIN = 6.2 V, VOUT(nom) = 5 V, COUT = 10 µF, CNR/SS = CFF = 10 nF, 10 Hz〜100 kHz | TYP | p6 | "... CNR/SS = CFF (4) = 10 nF, BW = 10 Hz to 100 kHz 21.15 μVRMS" |
| PSRR（表） | 72 dB | VIN = 6.2 V, VOUT(nom) = 5 V, COUT = 10 µF, CNR/SS = CFF = 10 nF, f = 120 Hz（IOUT は見出し条件の 1 mA） | TYP | p6 | "PSRR Power-supply rejection ratio VIN = 6.2 V, VOUT(nom) = 5 V, COUT = 10 μF, CNR/SS = CFF (4) = 10 nF, f = 120 Hz 72 dB" |
| 熱遮断 | 170 °C / 150 °C | 上昇時遮断 / 下降時復帰 | TYP | p6 | "Tsd ... Shutdown, temperature increasing 170 ... Reset, temperature decreasing 150" |
| 雑音（Features） | 12.7 µVRMS（20 Hz〜20 kHz）/ 15.4 µVRMS（10 Hz〜100 kHz） | Features 欄には条件なし | — | p1 | "Noise: – 12.7 μVRMS (20 Hz to 20 kHz) – 15.4 μVRMS (10 Hz to 100 kHz)" |
| PSRR（Features） | 72 dB (120 Hz)、≥ 52 dB (10 Hz〜400 kHz) | 9.1.5 で Figure 29 の構成（入出力 10 µF 以上、CNR・CFF 10 nF）の結果とされている。**DS 内の食い違い:** この文が参照する Figure 18（VOUT = 5 V, IOUT = 150 mA, COUT = 10 µF, CNR/SS = CFF = 10 nF）は 400 kHz で約 50 dB（目読み）。52 dB の条件は DS に書かれていない | — | p1, p14 | "– ≥ 52 dB (10 Hz to 400 kHz)" / "The solution illustrated in Figure 29 delivers minimum noise levels of 15.4 μVRMS and power-supply rejection levels above 52 dB from 10 Hz to 400 kHz; see Figure 18 and Figure 25" 〔2026-09-25 照合で訂正〕 |

### PSRR のグラフ（p9、**目読み**。値は dB）

グラフの共通見出し条件は EC 表と同じ（p9）。図ごとの条件は凡例の記載。

| 図と条件 | 曲線 | 120 Hz | 1 kHz | 10 kHz | 100 kHz | 200 kHz | 400 kHz |
|---|---|---|---|---|---|---|---|
| Figure 14（vs COUT）: VOUT = 5V, VIN = 6.2V, IOUT = 150mA, CNR/SS = 10nF, CFF = 10nF | COUT = 10 µF | 73 | 71 | 59 | 54 | 62（10 µF 曲線の山がこの付近） | 50 |
| 同上 | COUT = 2.2 µF | 70 | 69 | 61 | 48 | 44（谷の付近） | 46 |
| Figure 16（vs CNR/SS）: VOUT = 1.2V, VIN = 3.2V, IOUT = 150mA, COUT = 10µF, CFF = 0nF | CNR/SS = 10 nF | 70 | 69 | 61 | 54 | 61 | 52（2 曲線がほぼ重なる） |
| 同上 | CNR/SS = 0 nF | 71 | 62 | 45 | 46 | 57 | 51 |
| Figure 18（vs CFF）: VOUT = 5V, VIN = 6.2V, IOUT = 150mA, COUT = 10µF, CNR/SS = 10nF | CFF = 10 nF | 73 | 72 | 59 | 54 | 62 | 50 |
| 同上 | CFF = 0 nF | 64 | 54 | 45 | 48 | 56 | 51 |

曲線の割り当て: 各図の引き出し線（"COUT = 10μF" は 200 kHz 付近の山、"CNR/SS = 10nF" / "CFF = 10nF" は上側の曲線）を画像で確認。原文（p15）: *"The 10-nF noise-reduction capacitor greatly improves the TPS7A49 power-supply rejection, achieving up to 15 dB of additional power-supply rejection for frequencies between 110 Hz and 200 kHz."* / *"adding a 10-nF bypass capacitor (CFF) from the FB pin to the OUT pin. This capacitor greatly improves power-supply rejection at lower frequencies for the band from 10 Hz to 200 kHz; see Figure 18."*

### 出力電圧・ソフトスタート・コンデンサ（p12〜p17）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力電圧の式 | R1 = R2 (VOUT / VFB(nom) – 1)、VFB(nom) / R2 > 5 µA | Equation 2（画像で確認。抽出テキストでは µA が "mA" に化ける） | — | p14 | "R1 = R2 (VOUT/VFB(nom) − 1), where VFB(nom)/R2 > 5 μA" |
| R2 の上限（設計例） | R2 < 242.4 kΩ | Equation 4、VREF(max) / R2 > 5 µA（推奨動作条件の R2 max は 237 kΩ） | — | p17 | "VREF(max)/R2 > 5μA → R2 < 242.4 kΩ" |
| ソフトスタート時間 | tSS (ms) = 1.4 × CNR/SS (nF) | Equation 1 | — | p12 | "tSS (ms) = 1.4 × CNR/SS (nF)" |
| CIN / COUT | 最小 2.2 µF、10 µF を強く推奨 | — | — | p14 | "achieve stability with a minimum input and output capacitance of 2.2 μF; however, TI highly recommends using a 10-μF capacitor to maximize ac performance." |
| コンデンサの ESR | < 200 mΩ | 安定のため | — | p14 | "High ESR capacitors can degrade PSRR. To ensure stability, maximum ESR must be less than 200 mΩ." |
| 誘電体 | X7R / X5R を推奨 | — | — | p14 | "Ceramic capacitors with X7R and X5R dielectrics are preferred." |
| CNR/SS・CFF | 安定には不要、10 nF を強く推奨 | CFF は FB–OUT 間（注4） | — | p14, p6 | "Although noise-reduction and feed-forward capacitors (CNR/SS and CFF, respectively) are not needed to achieve stability, TI highly recommends using 10-nF capacitors" |
| CNR の雑音低減 | 69 → 17 µVRMS（約 75 %） | 10 nF | — | p15 | "By using a 10-nF noise reduction capacitor, the output noise is reduced by approximately 75% (from 69 μVRMS to 17 μVRMS); see Figure 26." |
| ヘッドルーム（設計例） | VIN – VOUT – VDO(max) ≥ 1 V（最適性能のため） | 9.2.2 | — | p16 | "Dropout headroom is calculated as VIN – VOUT – VDO(max), and for optimal performance must be at least 1 V." |

### レイアウト（p19〜p21）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 入出力コンデンサの位置 | ピンの近く、同じ面、ピンとの間にビアを入れない | — | — | p14 | "Place the input and output capacitors as close to the pin as possible, on the same side as the device; do not use vias between the capacitor and the pin." |
| 距離の上限 | 10 mm 以内 | Do's and Don'ts | — | p19 | "Do not place the input or output capacitor more than 10 mm away from the regulator." |
| EN | 浮かせない | 同上 | — | p19 | "Do not float the enable (EN) pin." |
| NR/SS | 抵抗性・誘導性の負荷をつけない | 同上 | — | p19 | "Do not resistively or inductively load the NR/SS pin." |
| 全コンデンサの配置 | CIN・COUT・CNR/SS・CFF をデバイスの近く、同じ面に。反対面に置かない | — | — | p19 | "Every capacitor (CIN, COUT, CNR/SS, and CFF) must be placed as close as possible to the device and on the same side of the PCB as the regulator itself. Do not place any of the capacitors on the opposite side of the PCB" |
| GND と PowerPAD | GND ピンを直下の PowerPAD に直結、PowerPAD は直下の複数ビアで内層 GND へ | — | — | p19 | "The GND pin must be tied directly to the PowerPAD under the device. Connect the PowerPAD to any internal PCB ground planes using multiple vias directly under the device." |
| GND プレーン | VIN 側と VOUT 側を分け、GND ピンで一点接続。バイパスコンデンサの GND は GND ピンへ直接 | 11.1.1 | — | p19 | "separate ground planes for VIN and VOUT, with each ground plane star-connected only at the GND pin of the device. In addition, the ground connection for the bypass capacitor must connect directly to the GND pin of the device." |
| レイアウト例の部品サイズ | CIN・COUT 1206、CNR・R1・R2 0402 | Figure 37 の注 | — | p21 | "NOTE: CIN and COUT are size 1206 capacitors and CNR, R1, and R2 are size 0402." |

### 探したが DS に無かった項目（TPS7A49）

- ソフトスタートの式の適用範囲（CNR/SS の範囲・CFF ありの場合）
- PSRR の表の値は 120 Hz の 1 点のみ。100 kHz 以上の保証値は無い（グラフの typ のみ）
- 出力コンデンサの上限容量（設計例 Eq. 8 に「電流制限による立ち上がり時間」から出す 35 µF の計算例はあるが、規定値ではない）
- EN の閾値のヒステリシス: 規定値もグラフも無い（Figure 13 は ON/OFF の境界を 1 本の線で示すだけ。25°C で約 1.7 V、目読み） 〔2026-09-25 照合で訂正〕

---

## 3. TI TPS7A30（負電圧 LDO、-35 V / -200 mA）

出典: `TI_TPS7A30.pdf`（SBVS125D – AUGUST 2010 – REVISED JUNE 2015、Rev. D。2026-09-24 に ti.com の symlink から取り直したものとバイト一致）

**EC 表（p7）の見出し条件:** *"At TJ = –40°C to 125°C, |VIN| = |VOUT(nom)| + 1 V or |VIN| = 3 V (whichever is greater), VEN = VIN, IOUT = 1 mA, CIN = 2.2 µF, COUT = 2.2 µF, CNR/SS = 0 nF, and the FB pin tied to OUT, unless otherwise noted. Typical values are at TA = 25°C."*（EC 表・推奨動作条件は画像で列を確認）

### ピン配置（DGN、p4）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ピン配置 | 1 OUT / 2 FB / 3 NC / 4 GND / 5 EN / 6 NR/SS / 7 DNC / 8 IN / PowerPAD（TPS7A49 と同じ並び） | DGN（DRB も同じ番号） | — | p4 | "OUT 1 8 IN / FB 2 7 DNC / NC 3 6 NR/SS / GND 4 5 EN" |
| NC（3） | 開放または GND（"must"） | — | — | p4 | "Not internally connected. This pin must either be left open or tied to GND." |
| EN（5） | VEN ≥ VEN(+HI, min) または VEN ≤ VEN(–HI, max) で動作、VEN(+LO, max) ≥ VEN ≥ VEN(–LO, min) で停止。未使用なら IN へ。\|VEN\| ≤ \|VIN\| | — | — | p4 | "If VEN ≥ VEN(+HI, min) or VEN ≤ VEN(–HI, max), the regulator is enabled. If VEN(+LO, max) ≥ VEN ≥ VEN(–LO, min), the regulator is disabled. The EN pin can be connected to IN, if not used. \|VEN\| ≤ \|VIN\|." |
| PowerPAD | 開放または GND。基板のプレーンにはんだ付け | — | — | p4 | "Must either be left open or tied to GND. Solder to printed-circuit-board (PCB) plane to enhance thermal performance." |

### 絶対最大定格（p5）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| IN – GND | -36 / 0.3 V | — | MIN / MAX | p5 | "IN pin to GND pin –36 0.3 V" |
| OUT – GND | -33 / 0.3 V | — | MIN / MAX | p5 | "OUT pin to GND pin –33 0.3 V" |
| OUT – IN | -0.3 / 36 V | — | MIN / MAX | p5 | "OUT pin to IN pin –0.3 36 V" |
| FB – GND | -2 / 0.3 V | — | MIN / MAX | p5 | "FB pin to GND pin –2 0.3 V" |
| FB – IN | -0.3 / 36 V | — | MIN / MAX | p5 | "FB pin to IN pin –0.3 36 V" 〔2026-09-25 照合で追加〕 |
| EN – IN | -0.3 / 36 V | — | MIN / MAX | p5 | "EN pin to IN pin –0.3 36 V" |
| **EN – GND** | **-36 / 36 V** | — | MIN / MAX | p5 | "EN pin to GND pin –36 36 V" |
| NR/SS – GND | -2 / 0.3 V | — | MIN / MAX | p5 | "NR/SS pin to GND pin –2 0.3 V" |
| NR/SS – IN | -0.3 / 36 V | — | MIN / MAX | p5 | "NR/SS pin to IN pin –0.3 36 V" 〔2026-09-25 照合で追加〕 |
| TJ | -40 / 125 °C | — | MIN / MAX | p5 | "Operating virtual junction, TJ –40 125 °C" |

### 推奨動作条件（p6、画像で確認）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| VIN | -35 / -3 V | — | MIN / MAX | p6 | "VIN Input supply voltage –35 –3 V" |
| VEN | 0 / VIN（原文の印字のまま） | — | MIN / MAX | p6 | "VEN Enable supply voltage 0 VIN V" |
| VOUT | VREF / 33 V（原文の印字のまま。符号の表記は EC 表の "–33 ... VREF" と異なる） | — | MIN / MAX | p6 | "VOUT Output voltage VREF 33 V" |
| IOUT | 0 / 200 mA | — | MIN / MAX | p6 | "IOUT Output current 0 200 mA" |
| CIN / COUT | 2.2 / 10 µF | — | MIN / NOM | p6 | "CIN Input capacitor 2.2 10 µF" "COUT Output capacitor 2.2 10 µF" |
| CNR / CFF | 0 / 10 nF | — | MIN / NOM | p6 | "CNR Noise reduction capacitor 0 10 nF" "CFF Feed-forward capacitor 0 10 nF" |
| R2 | 237 kΩ | — | MAX | p6 | "R2 Lower feedback resistor 237 kΩ" |

### 熱特性（p6）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| RθJA | 63.4 °C/W（DGN）/ 47.7 °C/W（DRB） | — | パッケージ別の列 | p6 | "RθJA Junction-to-ambient thermal resistance 63.4 47.7 °C/W" |
| RθJB / ψJB / RθJC(bot) | 37.4 / 37.1 / 13.5 °C/W（DGN） | — | 同上 | p6 | "RθJB ... 37.4" "ψJB ... 37.1" "RθJC(bot) ... 13.5" |

### 電気的特性（p7、画像で確認）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| VIN | -35 / -3 V | — | MIN / MAX | p7 | "VIN Input voltage –35 –3 V" |
| VREF | -1.202 / -1.179 / -1.166 V | TJ = 25°C, VNR/SS = VREF（NR/SS で測定、注2） | MIN / TYP / MAX | p7 | "VREF Internal reference (2) TJ = 25°C, VNR/SS = VREF –1.202 –1.179 –1.166 V" |
| VFB | -1.176 V | — | TYP | p7 | "VFB Feedback voltage –1.176 V" |
| 出力電圧範囲 | -33 V 〜 VREF | \|VIN\| ≥ \|VOUT(nom)\| + 1 V。注3: 帰還抵抗網の電流 ≥ 5 µA | MIN / MAX | p7 | "Output voltage range (3) \|VIN\| ≥ \|VOUT(nom)\| + 1 V –33 VREF V" |
| 公称精度 / 総合精度 | ±1.5 / ±2.5 %VOUT | TJ = 25°C, \|VIN\| = \|VOUT(nom)\| + 0.5 V ／ \|VOUT(nom)\|+1 V ≤ \|VIN\| ≤ 35 V, 1 mA ≤ IOUT ≤ 200 mA | MIN / MAX | p7 | "Nominal accuracy ... –1.5 1.5" "Overall accuracy ... –2.5 2.5 %VOUT" |
| ライン / ロード・レギュレーション | 0.14 / 0.04 %VOUT | TJ = 25°C | TYP | p7 | "Line regulation ... 0.14 %VOUT" "Load regulation ... 0.04 %VOUT" |
| ドロップアウト | 216 mV | VIN = 95% VOUT(nom), IOUT = 100 mA | TYP | p7 | "\|VDO\| Dropout voltage VIN = 95% VOUT(nom), IOUT = 100 mA 216 mV" |
| ドロップアウト | 325 / 600 mV | VIN = 95% VOUT(nom), IOUT = 200 mA | TYP / MAX | p7 | "VIN = 95% VOUT(nom), IOUT = 200 mA 325 600 mV" |
| 電流制限 | 220 / 330 / 500 mA | VOUT = 90% VOUT(nom) | MIN / TYP / MAX | p7 | "ICL Current limit VOUT = 90% VOUT(nom) 220 330 500 mA" |
| GND 電流 | 55 / 100 µA、950 µA | IOUT = 0 mA ／ IOUT = 100 mA | TYP / MAX、TYP | p7 | "IGND Ground current IOUT = 0 mA 55 100 μA IOUT = 100 mA 950 μA" |
| シャットダウン電流 | 1 / 3 µA | VEN = 0.4 V、VEN = -0.4 V | TYP / MAX | p7 | "\|ISHDN\| ... VEN = 0.4 V 1 3 μA VEN = –0.4 V 1 3 μA" |
| FB 電流 | 14 / 100 nA | 注4: 流れ込む向きが正 | TYP / MAX | p7 | "IFB Feedback current (4) 14 100 nA" |
| EN 電流 | 0.48 / 1、0.51 / 1、0.5 / 1 µA | VEN = \|VIN\| = \|VOUT(nom)\|+1 V ／ VIN = VEN = -35 V ／ VIN = -21 V, VEN = 15 V | TYP / MAX | p7 | "\|IEN\| Enable current ... 0.48 1 ... 0.51 1 ... VIN = –21 V, VEN = 15 V 0.5 1 μA" |
| **正側 EN high** | 2 V 〜 15 V（TJ -40〜125 °C）、1.8 V 〜 15 V（TJ -40〜85 °C） | — | MIN / MAX | p7 | "VEN(+HI) Positive enable high-level voltage TJ = –40°C to 125°C 2 15 V TJ = –40°C to 85°C 1.8 15 V" |
| **正側 EN low** | 0 〜 0.4 V | — | MIN / MAX | p7 | "VEN(+LO) Positive enable low-level voltage 0 0.4 V" |
| **負側 EN high** | VIN 〜 -2 V | — | MIN / MAX | p7 | "VEN(–HI) Negative enable high-level voltage VIN –2 V" |
| **負側 EN low** | -0.4 〜 0 V | — | MIN / MAX | p7 | "VEN(–LO) Negative enable low-level voltage –0.4 0 V" |
| EN の説明（本文） | \|VEN\| > 2 V で正負どちらでも動作 | 8.3.3 | — | p15 | "The TPS7A30 provides a dual-polarity enable pin (EN) that turns on the regulator when \|VEN\| > 2 V, whether the voltage is positive or negative" |
| 出力雑音 | 15.1 µVRMS | VIN = -3 V, VOUT(nom) = VREF, COUT = 10 µF, CNR/SS = 10 nF, 10 Hz〜100 kHz | TYP | p7 | "... CNR/SS = 10 nF, BW = 10 Hz to 100 kHz 15.1 μVRMS" |
| 出力雑音 | 17.5 µVRMS | VIN = -6.2 V, VOUT(nom) = -5 V, COUT = 10 µF, CNR/SS = CFF = 10 nF, 10 Hz〜100 kHz | TYP | p7 | "... CNR/SS = CFF (5) = 10 nF, BW = 10 Hz to 100 kHz 17.5 μVRMS" |
| PSRR（表） | 72 dB | VIN = -6.2 V, VOUT(nom) = -5 V, COUT = 10 µF, CNR/SS = CFF = 10 nF, f = 120 Hz | TYP | p7 | "PSRR ... f = 120 Hz 72 dB" |
| 熱遮断 | 170 / 150 °C | 上昇時 / 下降時 | TYP | p7 | "TSD ... 170 ... 150 °C" |
| PSRR（Features） | 72 dB (120 Hz)、≥ 55 dB (10 Hz〜700 kHz) | 9.1.3 で Figure 32 の構成（10 µF 以上・10 nF）の結果とされている。**DS 内の食い違い:** この文が参照する Figure 18（VOUT = −5 V, IOUT = 200 mA, COUT = 10 µF, CNR/SS = CFF = 10 nF）は 400 kHz で約 54 dB、**700 kHz で約 45 dB**（目読み）。Figure 14（COUT = 10 µF, CFF = 0）も 700 kHz で約 45 dB | — | p1, p18 | "– ≥ 55 dB (10 Hz to 700 kHz)" / "delivers minimum noise levels of 15.1 μVRMS and power-supply rejection levels above 55 dB from 10 Hz to 700 kHz; see Figure 18 and Figure 26" 〔2026-09-25 照合で訂正〕 |
| 雑音（Features） | 14 µVRMS（20 Hz〜20 kHz）/ 15.1 µVRMS（10 Hz〜100 kHz） | 条件なし | — | p1 | "– 14 μVRMS (20 Hz to 20 kHz) – 15.1 μVRMS (10 Hz to 100 kHz)" |

### PSRR のグラフ（p10、**目読み**。値は dB。縦軸は 10〜90 dB）

| 図と条件 | 曲線 | 120 Hz | 1 kHz | 10 kHz | 100 kHz | 200 kHz | 400 kHz |
|---|---|---|---|---|---|---|---|
| Figure 14（vs COUT）: VOUT = -5V, VIN = -6.2V, IOUT = 200mA, CNR/SS = 10nF, CFF = 0µF | COUT = 10 µF | 69 | 68 | 60 | 53 | 57 | 57（山は約 300 kHz・約 62 dB） |
| 同上 | COUT = 2.2 µF | 69 | 68 | 61 | 49 | 45 | 46（山は約 600 kHz・約 53 dB） |
| Figure 16（vs CNR/SS）: VOUT = -5V, VIN = -6.2V, IOUT = 200mA, COUT = 10µF, CFF = 0µF | CNR/SS = 10 nF | 69 | 68 | 60 | 53 | 57 | 57 |
| 同上 | CNR/SS = 0 nF | 69 | 60 | 41 | 41 | 49 | 54 |
| Figure 18（vs CFF）: VOUT = -5V, VIN = -6.2V, IOUT = 200mA, CNR/SS = 10nF, COUT = 10µF | CFF = 10 nF | 73 | 70 | 57 | 56 | 61 | 54 |
| 同上 | CFF = 0 nF | 65 | 59 | 53 | 54 | 58 | 61（山の付近） |

原文（p18）: *"The 10-nF noise-reduction capacitor greatly improves TPS7A30 power-supply rejection, achieving up to 20 dB of additional power-supply rejection for frequencies between 110 Hz and 400 kHz."* / *"adding a 10-nF bypass capacitor (CFF) from the FB pin to the OUT pin. This capacitor greatly improves power-supply rejection at lower frequencies, for the band from 10 Hz to 200 kHz; see Figure 18."*

### 出力電圧・ソフトスタート・コンデンサ（p15〜p21）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力電圧の式 | R1 = R2 (VOUT / VFB(nom) – 1)、\|VFB(nom)\| / R2 > 5 µA | Equation 2（画像で確認） | — | p17 | "R1 = R2 (VOUT/VFB(nom) − 1), where \|VFB(nom)\|/R2 > 5μA" |
| 出力電圧範囲（本文） | -1.174 V 〜 -33 V（Features は "–1.18 V to –33 V"） | 9.1.1 | — | p17, p1 | "The TPS7A3001 has an output voltage range of –1.174 V to –33 V." |
| 1 % 抵抗の例 | VOUT = -15 V: R1 = 118 kΩ, R2 = 10 kΩ | Table 2 | — | p17 | "–15 118 10" |
| ソフトスタート時間 | tSS (ms) = 0.9 × CNR/SS (nF) | Equation 1。Figure 29 は CFF なしの場合 | — | p15 | "tSS (ms) = 0.9 × CNR/SS (nF)" / "Figure 29 shows the relationship between the CNR/SS size and the start-up time without a CFF." |
| 設計例のソフトスタート | 14 ms、CSS = 15 nF（原文の数値のまま） | Equation 6 | — | p21 | "tSS (ms) = 0.9 × CNR/SS = 14 ms CSS = 15 nF" |
| 設計例の COUT(max) | 15.4 µF（**設計例（VOUT = 2 V、tSS = 14 ms）での目安で、規定値ではない**）。電流制限での立ち上がりをソフトスタート時間の 2 桁下（140 µs）に置く前提。Eq.8 は ICL(min) = 220 mA を使う（Eq.7 と TPS7A49 の同じ設計例は ICL(max)） | Equation 7・8 | — | p21 | "For the soft-start to dominate the start-up conditions, ideally place the start-up time as a result of the current limit at two decades below the soft-start time (at 140 µs)." / Eq.8 "COUT(max) = tSS(CL) × ICL(min) / VOUT = 140 µs × 220 mA / 2V = 15.4 µF"（抽出テキストでは µ が "m" に化ける） 〔2026-09-25 照合で追加〕 |
| CIN / COUT | 最小 2.2 µF、10 µF を強く推奨 | — | — | p18 | "achieve stability with a minimum input and output capacitance of 2.2 μF; however, TI highly recommends using a 10-μF capacitor to maximize ac performance." |
| コンデンサの種類 | 低 ESR、X7R / X5R を推奨。高 ESR は PSRR を悪化 | — | — | p17 | "Ceramic capacitors with X7R and X5R dielectrics are preferred." / "High-ESR capacitors can degrade PSRR." |
| CNR/SS・CFF | 安定には不要、10 nF を強く推奨 | — | — | p18 | "Although noise-reduction and feed-forward capacitors (CNR/SS and CFF, respectively) are not needed to achieve stability, TI highly recommends using 10-nF capacitors" |
| CNR の雑音低減 | 80 → 17 µVRMS（約 80 %） | 10 nF | — | p18 | "the output noise is reduced by approximately 80% (from 80 μVRMS to 17 μVRMS); see Figure 27." |

### レイアウト（p23〜p25）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| Do's and Don'ts | 2.2 µF 以上を IN・OUT の近くに／コンデンサとピンの間に他の部品を置かない（§10）／10 mm 以内／EN を浮かせない／NR/SS に抵抗・誘導性の負荷をつけない | 9.3・10 | — | p23 §9.3・§10 | "Do not place the input or output capacitor more than 10 mm away from the regulator." "Do not float the enable (EN) pin." "Do not resistively or inductively load the NR/SS pin." / §10: "The input and output supplies must also be bypassed with at least a 2.2-μF capacitor located near the input and output pins. There must be no other components located between these capacitors and the pins." 〔2026-09-25 照合で訂正〕 |
| 全コンデンサの配置 | CIN・COUT・CNR/SS・CFF をデバイスの近く、同じ面。反対面に置かない。ビア・長い配線は避ける | 11.1 | — | p24 | "Every capacitor (CIN, COUT, CNR/SS, and CFF) must be placed as close as possible to the device and on the same side of the PCB as the regulator itself." |
| GND と PowerPAD | GND ピンを直下の PowerPAD に直結、PowerPAD は直下の複数ビアで内層 GND へ | 11.1 | — | p24 | "The GND pin must be tied directly to the PowerPAD under the device. The PowerPAD must be connected to any internal PCB ground planes using multiple vias directly under the device." |
| GND プレーン | VIN 側と VOUT 側を分け、GND ピンで一点接続 | 11.1.1 | — | p24 | "separate ground planes for VIN and VOUT, with each ground plane star-connected only at the GND pin of the device." |
| レイアウト例の部品サイズ | CIN・COUT 1206、CNR・R1・R2 0402 | Figure 40 の注 | — | p25 | "NOTE: CIN and COUT are size 1206 capacitors, and CNR, R1, and R2 are size 0402." |

**同じ DS の中での食い違い（原文のまま）:** 表題と Features は "–200-mA" / "Maximum Output Current: 200 mA"、8.1 Overview（p14）は *"The TPS7A30 family of devices are wide VIN, low-noise, 150-mA linear regulators (LDOs)."*

### 探したが DS に無かった項目（TPS7A30）

- コンデンサ ESR の上限値（TPS7A49 の "< 200 mΩ" に相当する文は無い。"High-ESR capacitors can degrade PSRR." のみ）
- PSRR の 100 kHz 以上の保証値（グラフの typ のみ）
- 推奨動作条件の VEN の負側の範囲（表の印字は "0 ... VIN"。EC 表と絶対最大定格では負側まで規定）

---

## 4. ADI（旧 Linear）LT1763

出典: `ADI_LT1763.pdf`（全 22 ページ。**各ページ下の版記号は "1763fg"**、Revision History の最新行は "G 5/10"。`datasheets/README.md` の記述 "`1763fh`" とは版記号が違う — 本ファイルで見えるのは Rev G）。PDF は Linear Technology の Rev G（"1763fg"）を第三者サイト（BDTIC）が配布したもの（`pdfinfo` の Author が "www.BDTIC.com"、各ページ下に "www.BDTIC.com/Linear" の透かし）。ADI の現行版ではない 〔2026-09-25 照合で訂正〕

**EC 表（p4〜p6）の見出し条件:** *"The ● denotes the specifications which apply over the full operating temperature range, otherwise specifications are at TA = 25°C. (Note 2)"*（p5 の表は画像で ● と列を確認）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| IN の絶対最大 | ±20 V | — | 絶対最大 | p2 | "IN Pin Voltage ........ ±20V" |
| 入出力差の絶対最大 | ±20 V | — | 絶対最大 | p2 | "Input to Output Differential Voltage ....... ±20V" |
| SHDN の絶対最大 | ±20 V | — | 絶対最大 | p2 | "SHDN Pin Voltage ........ ±20V" |
| 入力電圧範囲（Features） | 1.8 V 〜 20 V | 条件なし | — | p1 | "Wide Input Voltage Range: 1.8V to 20V" |
| 最小動作電圧 | 1.8 / 2.3 V | C, I Grade: ILOAD = 500mA（●、Notes 3, 11） | TYP / MAX | p4 | "Minimum Operating Voltage C, I Grade: ILOAD = 500mA (Notes 3, 11) ● 1.8 2.3 V" |
| 出力電圧（-5） | 4.950 / 5 / 5.050 V | LT1763-5, VIN = 5.5V, ILOAD = 1mA | MIN / TYP / MAX | p4 | "LT1763-5 VIN = 5.5V, ILOAD = 1mA 4.950 5 5.050 V" |
| 出力電圧（-5） | 4.875 / 5 / 5.125 V | 6V < VIN < 20V, 1mA < ILOAD < 500mA（●） | MIN / TYP / MAX | p4 | "6V < VIN < 20V, 1mA < ILOAD < 500mA ● 4.875 5 5.125 V" |
| ドロップアウト | 0.13 / 0.19 V、● 0.25 V | ILOAD = 10mA | TYP / MAX、MAX（全温度） | p5（画像で確認） | "Dropout Voltage VIN = VOUT(NOMINAL) (Notes 5, 6, 11) ILOAD = 10mA 0.13 0.19 V ILOAD = 10mA ● 0.25 V" |
| ドロップアウト | 0.17 / 0.22 V、● 0.32 V | ILOAD = 50mA | 同上 | p5 | "ILOAD = 50mA 0.17 0.22 ... ● 0.32" |
| ドロップアウト | 0.20 / 0.24 V、● 0.34 V | ILOAD = 100mA | 同上 | p5 | "ILOAD = 100mA 0.20 0.24 ... ● 0.34" |
| ドロップアウト | 0.30 / 0.35 V、● 0.45 V | ILOAD = 500mA | 同上 | p5 | "ILOAD = 500mA 0.30 0.35 ... ● 0.45" |
| ドロップアウトの定義 | 規定電流で調整を保つ最小の入出力差 | Note 6 | — | p6 | "Note 6: Dropout voltage is the minimum input to output voltage differential needed to maintain regulation at a specified output current." |
| GND ピン電流 | 30 / 75 µA | ILOAD = 0mA（●）、VIN = VOUT(NOMINAL) | TYP / MAX | p5 | "GND Pin Current VIN = VOUT(NOMINAL) (Notes 5, 7) ILOAD = 0mA ● 30 75 μA" |
| GND ピン電流 | 65 / 120 µA | ILOAD = 1mA（●） | TYP / MAX | p5 | "ILOAD = 1mA ● 65 120 μA" |
| GND ピン電流 | 1.1 / 1.6 mA | ILOAD = 50mA（●） | TYP / MAX | p5 | "ILOAD = 50mA ● 1.1 1.6 mA" |
| GND ピン電流 | 2 / 3 mA | ILOAD = 100mA（●） | TYP / MAX | p5 | "ILOAD = 100mA ● 2 3 mA" |
| GND ピン電流 | 5 / 8 mA | ILOAD = 250mA（●） | TYP / MAX | p5 | "ILOAD = 250mA ● 5 8 mA" |
| GND ピン電流 | 11 / 16 mA | ILOAD = 500mA（●） | TYP / MAX | p5 | "ILOAD = 500mA ● 11 16 mA" |
| GND ピン電流の試験条件 | ドロップアウト領域で試験＝最悪値。入力が高いとわずかに減る | Note 7 | — | p6 | "This means the device is tested while operating in its dropout region. This is the worst-case GND pin current. The GND pin current will decrease slightly at higher input voltages." |
| **SHDN 閾値（Off→On）** | 0.8 / 2 V | ● | TYP / MAX | p5（画像で確認） | "Shutdown Threshold VOUT = Off to On ● 0.8 2 V" |
| **SHDN 閾値（On→Off）** | 0.25 / 0.65 V | ● | MIN / TYP | p5（画像で確認） | "VOUT = On to Off ● 0.25 0.65 V" |
| SHDN ピン電流 | 0.1 µA / 1 µA | VSHDN = 0V ／ VSHDN = 20V | TYP | p5 | "SHDN Pin Current (Note 9) VSHDN = 0V 0.1 μA VSHDN = 20V 1 μA" |
| シャットダウン時静止電流 | 0.1 / 1 µA | VIN = 6V, VSHDN = 0V | TYP / MAX | p5 | "Quiescent Current in Shutdown VIN = 6V, VSHDN = 0V 0.1 1 μA" |
| SHDN の未接続 | 未接続ならシャットダウン。未使用時は VIN へ | ピン説明 | — | p14 | "If unused, the SHDN pin must be connected to VIN. The device will be in the low power shutdown state if the SHDN pin is not connected." |
| Ripple Rejection | 50 / 65 dB | VIN – VOUT = 1.5V (Avg), VRIPPLE = 0.5VP-P, fRIPPLE = 120Hz, ILOAD = 500mA。**TA = 25°C（● なし。全温度の規定ではない）** | MIN / TYP | p5（画像で確認） | "Ripple Rejection VIN – VOUT = 1.5V (Avg), VRIPPLE = 0.5VP-P, fRIPPLE = 120Hz, ILOAD = 500mA 50 65 dB" 〔2026-09-25 照合で訂正〕 |
| グラフ: Input Ripple Rejection vs 周波数（目読み） | COUT = 10 µF で 100 kHz 約 37〜41 dB、200 kHz 約 28〜32 dB、1 MHz 約 21〜22 dB（CBYP による差は 30 kHz 以上でほぼ無い）。左図（CBYP = 0、COUT = 10 µF / 4.7 µF）の 10 µF の線は 1 kHz 約 49、約 30 kHz に約 49 dB の山。右図（COUT = 10 µF、CBYP = 0.01 µF / 1000 pF / 100 pF）は 30 kHz 以上で 3 本が重なる | IL = 500 mA、VIN = VOUT(NOMINAL) + 1 V + 50 mVRMS（2 枚とも） | typ（グラフ） | p11 | 図題 "Input Ripple Rejection" 〔2026-09-25 照合で追加〕 |
| 熱抵抗（DE、12-Lead DFN） | θJA = 40 °C/W、θJC = 5 °C/W、TJMAX = 125 °C | ピン配置図の注記 | — | p2（画像で確認） | "TJMAX = 125°C, θJA = 40°C/W, θJC = 5°C/W" |
| 熱抵抗（S8） | θJA = 70 °C/W、θJC = 35 °C/W、TJMAX = 150 °C | 同上 | — | p2（画像で確認） | "TJMAX = 150°C, θJA = 70°C/W, θJC = 35°C/W" |
| θJA（DE、銅面積別） | 40 / 45 / 50 / 60 °C/W | 表面銅 2500 / 1000 / 225 / 100 mm²、裏面 2500 mm²、基板 2500 mm²。静止空気、3/32" FR-4、1 oz | — | p17 | "Table 1. DE Package, 12-Lead DFN ... 2500mm2 2500mm2 2500mm2 40°C/W ..." / "All measurements were taken in still air on 3/32" FR-4 board with one ounce copper." |
| θJA（S8、銅面積別） | 60 / 60 / 68 / 74 / 86 °C/W | 表面銅 2500 / 1000 / 225 / 100 / 50 mm²、他同上 | — | p18 | "Table 2. SO-8 Package, 8-Lead SO 2500mm2 ... 60°C/W ... 50mm2 ... 86°C/W" |
| 出力コンデンサ | 最小 3.3 µF・ESR 3 Ω 以下を推奨。CBYP 100 pF で 4.7 µF、1000 pF 以上で 6.8 µF | — | — | p16 | "A minimum output capacitor of 3.3μF with an ESR of 3Ω, or less, is recommended to prevent oscillations." / "For 100pF of bypass capacitance, 4.7μF of output capacitor is recommended. With a 1000pF bypass capacitor or larger, a 6.8μF output capacitor is recommended." |
| 出力コンデンサの安定域（目読み） | 最大 ESR は 3 Ω。最小 ESR は CBYP で決まり、ESR ≈ 0（セラミック）で安定になる COUT は CBYP = 0 で約 3 µF 以上、100 pF で約 4 µF、330 pF で約 5 µF、1000 pF 以上で約 6 µF 以上（横軸は 10 µF まで） | Figure 3 の網掛けが安定域。同じページの本文に 16 V・10 µF の Y5V の実効容量の記述（Figure 4・5） | — | p16 Figure 3 | "The shaded region of Figure 3 defines the range over which the LT1763 regulators are stable. The minimum ESR needed is defined by the amount of bypass capacitance used, while the maximum ESR is 3Ω." / "When used with a 5V regulator, a 16V 10µF Y5V capacitor can exhibit an effective value as low as 1µF to 2µF for the DC bias voltage applied and over the operating temperature range." 〔2026-09-25 照合で追加〕 |

### 探したが DS に無かった項目（LT1763）

- SHDN 閾値の Off→On の MIN 値、On→Off の MAX 値（表の該当欄は空）
- GND ピン電流の VIN = 20 V 付近での規定値（試験は VIN = VOUT(NOMINAL) と 2.3 V（C/I）／2.35 V（MP）の大きい方、電流源負荷（Note 7）。これより高い VIN の規定値は無い） 〔2026-09-25 照合で訂正〕
- `1763fh`（Rev H）のファイル — リポジトリの PDF は Rev G（"1763fg"）

---

## 5. ST L7809（L78 シリーズ）

出典: `ST_L78.pdf`（**DocID2143 Rev 34、November 2016**、全 54 ページ。st.com は接続が落ちて取れず（curl で "Empty reply" / HTTP/2 INTERNAL_ERROR、WebFetch で 503）、Farnell のミラー `farnell.com/datasheets/2307057.pdf` から取得。PDF の Author は "STMICROELECTRONICS"。**検索結果では st.com の現行版は DS0422 Rev 38 とされているが、その版は取得できていない**）

### L7809C（Table 14、p18）— 表全体を画像で確認

**表の見出し条件:** *"Refer to the test circuits, TJ = 0 to 125 °C, VI = 15 V, IO = 500 mA, CI = 0.33 µF, CO = 0.1 µF unless otherwise specified"*、脚注 a *"Minimum load current for regulation is 5 mA."*

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力電圧 | 8.64 / 9 / 9.36 V | TJ = 25 °C | Min. / Typ. / Max. | ST_L78.pdf p18 | "VO Output voltage TJ = 25 °C 8.64 9 9.36 V" |
| 出力電圧 | 8.55 / 9 / 9.45 V | IO = 5 mA to 1 A, **VI = 11.5 to 22 V** | Min. / Typ. / Max. | p18 | "IO = 5 mA to 1 A, VI = 11.5 to 22 V 8.55 9 9.45 V" |
| 出力電圧 | 8.55 / 9 / 9.45 V | IO = 1 A, VI = 22 to 26 V, TJ = 25 °C | Min. / Typ. / Max. | p18 | "IO = 1 A, VI = 22 to 26 V, TJ = 25 °C 8.55 9 9.45 V" |
| ライン・レギュレーション | 180 mV / 90 mV | VI = 11.5 to 26 V, TJ = 25 °C ／ VI = 12 to 18 V, TJ = 25 °C | **Max.**（Typ. 空欄） | p18 | "Line regulation VI = 11.5 to 26 V, TJ = 25 °C 180 / VI = 12 to 18 V, TJ = 25 °C 90 mV" |
| ロード・レギュレーション | 180 mV / 90 mV | IO = 5 mA to 1.5 A, TJ = 25 °C ／ IO = 250 to 750 mA, TJ = 25 °C | **Max.** | p18 | "Load regulation IO = 5 mA to 1.5 A, TJ = 25 °C 180 / IO = 250 to 750 mA, TJ = 25 °C 90 mV" |
| **静止電流** | **8 mA** | TJ = 25 °C（IO は見出し条件の 500 mA） | **Max.**（Typ. 空欄） | p18 | "Id Quiescent current TJ = 25 °C 8 mA" |
| 静止電流の変化 | 0.5 mA / 1 mA | IO = 5 mA to 1 A ／ VI = 11.5 to 26 V | Max. | p18 | "∆Id Quiescent current change IO = 5 mA to 1 A 0.5 / VI = 11.5 to 26 V 1 mA" |
| **ドロップアウト** | **2 V** | **IO = 1 A, TJ = 25 °C** | **Typ.**（Min.・Max. 空欄） | p18 | "Vd Dropout voltage IO = 1 A, TJ = 25 °C 2 V" |
| SVR | 55 dB | VI = 12 to 23 V, f = 120 Hz | Min. | p18 | "SVR Supply voltage rejection VI = 12 to 23 V, f = 120 Hz 55 dB" |
| 出力雑音 | 70 µV/VO | B = 10 Hz to 100 kHz, TJ = 25 °C | Typ. | p18 | "eN Output noise voltage B = 10 Hz to 100 kHz, TJ = 25 °C 70 µV/VO" |
| 出力抵抗 | 17 mΩ | f = 1 kHz | Typ. | p18 | "RO Output resistance f = 1 kHz 17 mΩ" |
| 短絡電流 / ピーク | 0.40 A / 2.2 A | VI = 35 V, TJ = 25 °C ／ TJ = 25 °C | Typ. | p18 | "Isc Short circuit current VI = 35 V, TJ = 25 °C 0.40 A / Iscp ... 2.2 A" |
| 出力電圧ドリフト | -1 mV/°C | IO = 5 mA | Typ. | p18 | "∆VO/∆T Output voltage drift IO = 5 mA -1 mV/°C" |
| 最小負荷 | 5 mA | 脚注 a | — | p18 | "Minimum load current for regulation is 5 mA." |

### L7809A（Table 6、p10）— 参考。表全体を画像で確認

**表の見出し条件:** *"VI = 15 V, IO = 1 A, TJ = 0 to 125 °C (L7809AC), TJ = -40 to 125 °C (L7809AB), unless otherwise specified"*

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力電圧 | 8.82 / 9 / 9.18 V | TJ = 25 °C | Min. / Typ. / Max. | p10 | "VO Output voltage TJ = 25 °C 8.82 9 9.18 V" |
| 出力電圧 | 8.65 / 9 / 9.35 V | IO = 5 mA to 1 A, **VI = 10.6 to 22 V** | Min. / Typ. / Max. | p10 | "IO = 5 mA to 1 A, VI = 10.6 to 22 V 8.65 9 9.35 V" |
| ライン・レギュレーション | 12 / 90 mV | VI = 10.6 to 25 V, IO = 500 mA, TJ = 25 °C | Typ. / Max. | p10 | "VI = 10.6 to 25 V, IO = 500 mA, TJ = 25 °C 12 90 mV" |
| 静止電流 | 4.3 / 6 mA（TJ = 25 °C）、6 mA（条件欄空） | — | Typ. / Max.、Max. | p10 | "Iq Quiescent current TJ = 25 °C 4.3 6 mA / 6 mA" |
| ドロップアウト | 2 V | IO = 1 A, TJ = 25 °C | Typ. | p10 | "Vd Dropout voltage IO = 1 A, TJ = 25 °C 2 V" |
| SVR | 61 dB | VI = 11.5 to 21.5 V, f = 120 Hz, IO = 500 mA | Typ. | p10 | "SVR Supply voltage rejection VI = 11.5 to 21.5 V, f = 120 Hz, IO = 500 mA 61 dB" |

### シリーズ共通（p5、p23、p31）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 入力電圧の絶対最大 | 35 V | VO = 5 to 18 V | 値の列のみ | p5 | "VI DC input voltage for VO= 5 to 18 V 35" |
| 動作接合温度 | 0 to 125 °C（L78xxC, L78xxAC）/ -40 to 125 °C（L78xxAB） | — | 値の列のみ | p5 | "TOP Operating junction temperature range for L78xxC, L78xxAC 0 to 125 for L78xxAB -40 to 125" |
| 熱抵抗 | RthJA 50 / RthJC 5 °C/W（TO-220）、60 / 5（TO-220FP）、62.5 / 3（D²PAK）、100 / 8（DPAK） | — | パッケージ別の列 | p5 | "RthJC ... 3 8 5 5" "RthJA ... 62.5 100 50 60" |
| ピン配置（図） | TO-220 / TO-220FP の上面図でリード3本に上から OUTPUT / GROUND / INPUT。TO-220 のタブは GND（ピン番号の記載なし） | Figure 2 | — | p4（画像で確認） | "Figure 2: Pin connections (top view)" |
| 入力コンデンサ | 0.33 µF 以上（タンタル・マイラ等、高周波で低インピーダンス）を入力端子に最短で | 電源フィルタから配線が長い、または出力負荷容量が大きい場合 | — | p23 | "A 0.33 µF or larger tantalum, mylar or other capacitor having low internal impedance at high frequencies should be chosen." |
| 出力コンデンサ | 安定には不要、過渡応答が改善（Figure 8 は CO = 0.1 µF） | Figure 8 の注1 | — | p23（画像で確認） | "Although no output capacitor is need for stability, it does improve transient response." |
| ドロップアウトの温度特性（図） | 目読み・TJ = 25 °C: IO = 1 A ≈ 2.0 V、500 mA ≈ 1.75 V、200 mA ≈ 1.6 V、20 mA ≈ 1.5 V、0 mA ≈ 0.95 V | Figure 28。**品種は "L78XX"（9 V 品の指定なし）**。"DROPOUT CONDITIONS ∆VO = 5% of VO"。凡例の電流は原文では "Tj = 500 mA" などと印字 | 目読み（300 dpi 画像を画素で計測、±0.05 V 程度） | p31 | "Figure 28: Dropout voltage vs junction temperature ... L78XX ... DROPOUT CONDITIONS ∆VO = 5% of VO" |

### 探したが DS に無かった項目（L7809）

- **「入力電圧範囲」という規定項目**（L7809C に Vi min の行は無い。11.5 V は出力電圧・ライン・静止電流変化の試験条件の下限として出てくるだけ。L7809A では同じ位置が 10.6 V）
- **ドロップアウトの Max 値**（L7809C・L7809A とも Typ 2 V のみ、条件は IO = 1 A・TJ = 25 °C）
- 1 A 以外の電流でのドロップアウトの規定値（Figure 28 のシリーズ共通グラフのみ）
- L7809C の静止電流の Typ 値（Max 8 mA のみ）
- 静止電流の入力電圧依存のグラフの 9 V 品版（Figure 36 は L7805 のみ）
- 現行版 DS0422 Rev 38 での値の照合（未取得）
