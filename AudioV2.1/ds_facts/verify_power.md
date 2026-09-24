# 電源系 DS 事実表の独立照合（power.md）

- 照合日: 2026-09-25
- 対象: `AudioV2.1/ds_facts/power.md`（書き換えていない）
- DS: `AudioV2.1/datasheets/` の `Recom_RS6.pdf` / `TI_TPS7A49.pdf` / `TI_TPS7A30.pdf` / `ADI_LT1763.pdf` / `ST_L78.pdf`
- やり方: 出典に書かれたページをすべて `pdftoppm -r 150` で画像にし、表の罫線・列見出し・脚注・ページ見出しの条件を目で確かめた。
  PSRR のグラフ（TPS7A49 p9、TPS7A30 p10）と L78 Figure 28（p31）は 300 dpi にして、枠線と格子線を画素で探して軸を合わせ、
  指定の周波数（温度）の列で曲線の画素を拾って換算した（PIL が壊れていたので PPM を素の Python で読んだ）。power.md の数値は見ずに読み、あとで突き合わせた。
  寸法図（RS6 p7）は 400 dpi で拡大した。作業ファイルは scratchpad の `verify_power/` にある。
- 照合した行: **表の行 244 行**（power.md の表の全データ行。PSRR グラフは曲線 1 本＝1 行）＋ **表の外の記述 9 件**（各 DS の出典行・見出し条件・「同じ DS の中での食い違い」）＝ **253 件**
- 判定の内訳: **一致 253**（うち注記つき 9）／誤り 0／条件の誤り 0／列の誤り 0／引用が無い 0／確かめられず 0
- 注記つきの 9 件は、値・列・ページは正しいが、言い回しが DS の字句より一歩踏み込んでいるもの（例: DS は "Quiescent Current" と書いているのに「無負荷」と書き足している）。判定を変えるほどではないが、各行の「DS の実際」の欄に書いた。
- 「探したが DS に無かった項目」は 27 項目すべて、たしかに DS に無かった（規定値としては無い）。ただし、それに近い情報（典型値のグラフや設計例）が DS にあるものを、最後の節にまとめた。

凡例: 「同上」は「power.md の値・列・条件・ページのとおり」という意味。引用は DS の画像から読んだ原文。

---

## 1. Recom RS6-1215D

| 部品 | 項目 | power.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| RS6 | 出典（REV.、ページ数） | REV.: 10/2024、全 7 ページ | 一致 | 各ページの下に "REV.: 10/2024"、ECO-1〜ECO-7 | "REV.: 10/2024" |
| RS6 | 見出し条件（p2〜p7） | Ta=25°C・公称入力・全負荷・ウォームアップ後 | 一致 | p2〜p7 の黄色い帯に同じ文。p1 には無い | "Specifications (measured @ Ta= 25°C, nominal input voltage, full load and after warm up unless otherwise specified)" |
| RS6 | 選定表 入力電圧範囲 | 9 - 18 VDC | 一致 | p1 選定表 RS6-1215D の行。min/typ/max の列は無い | "RS6-1215D 9 - 18 ±15 ±200 87 ±660" |
| RS6 | 選定表 出力電圧 | ±15 VDC | 一致 | 同上 | 同上 |
| RS6 | 選定表 出力電流 | ±200 mA | 一致 | 同上。列見出しは "Output Current [mA]" | 同上 |
| RS6 | 選定表 効率 | 87 %、列 "Efficiency typ. (1)" | 一致 | 同上。Note1 も原文どおり | "Note1: Efficiency is tested by nominal input and full load at +25°C ambient" |
| RS6 | 選定表 最大容量性負荷 | ±660 µF、列 "max. Capacitive Load (2)" | 一致 | 同上。Note2 も原文どおり | "Note2: Max Cap Load is tested by minimum input and constant resistor load" |
| RS6 | 入力フィルタ | capacitor（Min〜Max の結合セル） | 一致 | p2。Min〜Max をまたぐセルに右寄せ | "Input Filter ... capacitor" |
| RS6 | 入力電圧範囲 | 9 / 12 / 18 VDC、Min/Typ/Max | 一致 | p2。nom. Vin=12VDC の行 | "12VDC 9VDC 12VDC 18VDC" |
| RS6 | 入力サージ電圧 | 25 VDC、Max、1 second max. | 一致 | p2。Max 列 | "Input Surge Voltage 1 second max. ... 12VDC ... 25VDC" |
| RS6 | "Quiescent Current" | 55 mA、Max、条件の印字は "2VDC" | 一致（注記） | p2。値・Max 列・"2VDC" の誤植は画像でもそのとおり。**注記:** power.md の項目名「無負荷入力電流」の「無負荷」は DS の字句ではない（条件欄に負荷の記載は無く、見出し条件は "full load"）。55 mA という値から無負荷と読むのは妥当だが、DS がそう書いているわけではない | "Quiescent Current nom. Vin= 5VDC 2VDC 24VDC 48VDC ... 105mA 55mA 28mA 14mA" |
| RS6 | 出力電圧トリム | +10 % / -8 %、Max | 一致 | p2。Max 列 | "Output Voltage Trimming see calculation on next page Trim up +10% Trim down -8%" |
| RS6 | 起動時間 | 2 ms、Typ | 一致 | p2。Typ 列 | "Start-up Time 2ms" |
| RS6 | 低電圧ロックアウト | ON 9 VDC / OFF 7 VDC、Typ | 一致 | p2。nom. Vin=12V の行、Typ 列 | "nom. Vin= 12V DC-DC ON 9VDC DC-DC OFF 7VDC" |
| RS6 | ON/OFF CTRL（ON） | Open（結合セル、右寄せ） | 一致 | p2 | "ON/OFF CTRL DC-DC ON ... Open" |
| RS6 | ON/OFF CTRL（OFF） | 5V < Vr < 12VDC | 一致 | p2 | "DC-DC OFF ... 5V<Vr<12VDC" |
| RS6 | CTRL の論理（Note7） | high=OFF、high Z=ON、low 不可 | 一致 | p7 Note7 | "When the pin is 'high' the converter is OFF and when the pin is high 'Z' the converter is ON. There is no allowed low state for this pin" |
| RS6 | CTRL ピン入力電流 | 1.5 / 2.5 / 3.3 mA、Min/Typ/Max | 一致 | p2。条件欄は空 | "Input Current of CTRL Pin 1.5mA 2.5mA 3.3mA" |
| RS6 | 待機電流 | 2 mA、Typ | 一致 | p2 | "Standby Current 2mA" |
| RS6 | 内部動作周波数 | 200 kHz、**Min 列**、条件 "0-100% load" | 一致 | p2。"200kHz" の文字の中心（150 dpi で x≈808）は Min. 列の中心と同じ。Typ・Max は空欄 | "Internal Operating Frequency 0-100% load 200kHz" |
| RS6 | 最小負荷 | 0 %、Typ | 一致 | p2。Typ 列 | "Minimum Load 0%" |
| RS6 | 出力リップル＆ノイズ | 50 / 75 mVp-p、Typ/Max、20MHz BW、Note3 1.0 µF MLCC | 一致 | p2 | "Output Ripple and Noise (3) 20MHz BW 50mVp-p 75mVp-p" / "Note3: Measurements are made with a 1.0µF MLCC across output (low ESR)" |
| RS6 | トリム回路の対象 | 3.3V/5V/12V/15V の単出力のみ | 一致 | p3・p4。計算表の表題は "RS6-xx03.3S / xx05S / xx12S / xx15S" で S（単出力）だけ。定数表の列見出しは "Vout 3.3V 5V 12V 15V" で、「単出力」とは書いていない | "RS6-xx15S" / "Vout 3.3V 5V 12V 15V" |
| RS6 | デュアル品の 5 番ピン | NC（単出力では Trim） | 一致 | p7 ピン表 | "5 Trim NC" |
| RS6 | 15V 品の内部定数 | R1=50 kΩ、R2=10 kΩ、R3=68 kΩ、Vref=2.5 V | 一致 | p3 定数表の 15V 列（R2 と Vref は結合セル） | "R1 ... 50kΩ / R2 10kΩ / R3 ... 68kΩ / Vref ... 2.5V" |
| RS6 | 出力精度 | ±1.0 % typ.（値の列のみ） | 一致 | p4 REGULATIONS。列は Parameter / Condition / Values の 3 列 | "Output Accuracy ±1.0% typ." |
| RS6 | ライン・レギュレーション | ±0.2 % typ.、low line to high line | 一致 | p4 | "Line Regulation low line to high line ±0.2% typ." |
| RS6 | ロード・レギュレーション | 1.0 % typ.、0%〜100% load | 一致 | p4（± は付いていない。そのまま） | "Load Regulation 0% to 100% load 1.0% typ." |
| RS6 | クロス・レギュレーション | ±5.0 % typ.、25%〜100% load | 一致 | p4 | "Cross Regulation 25% to 100% load ±5.0% typ." |
| RS6 | 過渡応答 | 500 µs typ.、25% load step | 一致 | p4 | "Transient Response 25% load step change 500µs typ." |
| RS6 | 短絡保護 | continuous, automatic recovery、below 100 mΩ | 一致 | p5。画像では "100mΩ"、pdftotext では "100mW" に化ける（確認済み） | "Short Circuit Protection (SCP) below 100mΩ continuous, automatic recovery" |
| RS6 | 過負荷保護 | 150% load, continuous, automatic recovery | 一致 | p5 | "Over Load Protection (OLP) 150% load, continuous, automatic recovery" |
| RS6 | 絶縁耐圧 | 2 kVDC（1 秒試験）/ 1.6 kVDC（1 分定格） | 一致 | p5 | "I/P to O/P tested for 1 second 2kVDC rated for 1 minute 1.6kVDC" |
| RS6 | 絶縁容量 | 110 pF max. | 一致 | p5 | "Isolation Capacitance 110pF max." |
| RS6 | 絶縁抵抗 | 1 GΩ typ. | 一致 | p5 | "Isolation Resistance 1GΩ typ." |
| RS6 | 絶縁グレード | functional | 一致 | p5 | "Isolation Grade functional" |
| RS6 | 動作温度 | -40〜+75 °C、full load (see graph)、Note5 | 一致 | p5。ディレーティング図は 75 °C まで 100 %、85 °C 付近で折れて約 100 °C で 0 % | "Operating Temperature Range (5) full load (see graph) -40°C to +75°C" / "Note5: Derating Graph is referring to RS6-0505S." |
| RS6 | 最大ケース温度 | +105 °C | 一致 | p5 | "Maximum Case Temperature +105°C" |
| RS6 | 温度係数 | ±0.02 %/°C | 一致 | p5 | "Temperature Coefficient ±0.02%/°C" |
| RS6 | EMC フィルタの対象モデル | 053.3S / 1205S / 2412D / 483.3S・4815S のみ、1215D は無い | 一致 | p6 の表と Note6 | "Note6: Filter suggestions are valid for indicated part numbers only. For other part numbers, please contact RECOM tech support for advice." |
| RS6 | EMC フィルタ（RS6-1205S） | A: C1 10µF, L1 47µH, C3 1nF / B: C2 4.7µF, L1 18µH(RLS-186), CMC1 1mH, C3 100pF, C4 100pF, CMC2 11µH | 一致 | p6 | "RS6-1205S A 10µF N/A 47µH N/A 1nF N/A N/A / B N/A 4.7µF 18µH, RLS-186 1mH 100pF 100pF 11µH" |
| RS6 | サージ保護 | Csurge 100V 220µF E/Cap、Dsurge N/A（12/24/48V）、±1kVDC | 一致 | p6。Csurge と max. Surge は 5V 行と 12/24/48V 行の結合セル。5V 行だけ TVS (P4SMAJ15CA) | "12, 24, 48VDC ... 100V, 220µF E/Cap ... N/A ... ±1kVDC" |
| RS6 | ピン配置（Dual） | 1 -Vin / 2 +Vin / 3 CTRL / 5 NC / 6 +Vout / 7 Com / 8 -Vout、4 番無し | 一致 | p7 ピン表・Bottom View・Top View とも 1 2 3 _ 5 6 7 8 | "1 -Vin -Vin 2 +Vin +Vin 3 CTRL (7) CTRL (7) 5 Trim NC 6 +Vout +Vout 7 -Vout Com 8 NC -Vout" |
| RS6 | 外形 | 21.8 x 9.2 x 11.1 mm | 一致 | p7 | "Dimension (LxWxH) 21.8 x 9.2 x 11.1mm" |
| RS6 | ピンピッチ | 2.54 mm、7 x 2.54 = 17.78 mm、±0.25 mm | 一致 | p7 Bottom View と公差欄 | "7x2.54= 17.78" / "Pin pitch: ±0.25mm" |
| RS6 | 1 番ピン〜筐体端 | 2.00 mm | 一致 | p7 Bottom View（筐体左端〜1 番ピン中心。400 dpi で確認） | "2.00" |
| RS6 | ピン列〜筐体面 | 3.20 mm（図の下辺まで） | 一致 | p7 Bottom View。ピン列の中心線から図の下辺まで（400 dpi で確認）。幅 9.2 mm の中央ではない | "3.20" |
| RS6 | ピン断面 | 0.51 (+0.10/-0.05) x 0.25 ±0.05 mm | 一致 | p7 | "0.51+0.10/-0.05" "0.25±0.05" |
| RS6 | ピン長 / スタンドオフ | 4.10 / 0.50 mm | 一致 | p7 側面図 | "4.10" "0.50" |
| RS6 | 推奨穴径 | Ø 1.00 +0.15/-0 mm | 一致 | p7 | "Recommended Footprint Details 1.00 Ø +0.15/-0" |
| RS6 | 寸法公差 | xx.x ±0.5、xx.xx ±0.25、ピン ±0.1 mm | 一致 | p7 | "Tolerance: xx.x= ±0.5mm xx.xx= ±0.25mm Pin dimension: ±0.1mm" |
| RS6 | 質量 | 4.0 g | 一致 | p7 | "Weight 4.0g" |
| RS6 | DS 内の食い違い（絶縁） | Features "1.6kVDC/1 minute"、Description "2kVDC" | 一致 | p1 Features と Description に原文どおり | "1.6kVDC/1 minute isolation" / "2kVDC isolation" |

## 2. TI TPS7A49

| 部品 | 項目 | power.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| TPS7A49 | 出典（版） | SBVS121E、REVISED MAY 2015 | 一致 | 各ページの見出し | "SBVS121E – AUGUST 2010 – REVISED MAY 2015" |
| TPS7A49 | EC 表の見出し条件（p6） | TJ -40〜125°C、VIN=VOUT(nom)+1V or 3V、IOUT=1mA、CIN=COUT=2.2µF、CNR/SS=0nF、FB=OUT、Typ は TA=25°C | 一致 | p6 6.5 の見出し。p9 のグラフの見出しも同じ文 | "At TJ = –40°C to 125°C, VIN = VOUT(nom) + 1 V or VIN = 3 V (whichever is greater), VEN = VIN, IOUT = 1 mA, CIN = 2.2 μF, COUT = 2.2 μF, CNR/SS = 0 nF, and the FB pin tied to OUT, unless otherwise noted." |
| TPS7A49 | ピン配置 | 1 OUT / 2 FB / 3 NC / 4 GND / 5 EN / 6 NR/SS / 7 DNC / 8 IN / PowerPAD | 一致 | p4。DGN・DRB とも同じ番号 | "OUT 1 8 IN / FB 2 7 DNC / NC 3 6 NR/SS / GND 4 5 EN" |
| TPS7A49 | DNC（7） | どのネットにもつながない | 一致 | p4 | "Do not connect. Do not route this pin to any electrical net, not even GND or IN." |
| TPS7A49 | NC（3） | 開放または GND | 一致 | p4（"can either"。TPS7A30 は "must either"） | "Not internally connected. This pin can either be left open or tied to GND." |
| TPS7A49 | OUT（1） | ≥ 2.2 µF を GND へ | 一致 | p4 | "A capacitor ≥ 2.2 μF must be tied from this pin to ground to ensure stability." |
| TPS7A49 | PowerPAD | 開放または GND、プレーンにはんだ付け | 一致 | p4 | "Must either be left open or tied to ground. Solder to the printed-circuit-board (PCB) plane to enhance thermal performance." |
| TPS7A49 | EN（5） | 未使用なら IN へ、VEN ≤ VIN | 一致 | p4 | "The EN pin can be connected to IN, if not used. VEN ≤ VIN." |
| TPS7A49 | 絶対最大 IN–GND | -0.3 / 36 V | 一致 | p5 MIN/MAX | "IN pin to GND pin –0.3 36 V" |
| TPS7A49 | 絶対最大 OUT–GND | -0.3 / 33 V | 一致 | p5 | "OUT pin to GND pin –0.3 33 V" |
| TPS7A49 | 絶対最大 OUT–IN | -36 / 0.3 V | 一致 | p5 | "OUT pin to IN pin –36 0.3 V" |
| TPS7A49 | 絶対最大 FB–GND | -0.3 / 2 V | 一致 | p5 | "FB pin to GND pin –0.3 2 V" |
| TPS7A49 | 絶対最大 EN–IN | -36 / 0.3 V | 一致 | p5 | "EN pin to IN pin –36 0.3 V" |
| TPS7A49 | 絶対最大 EN–GND | -0.3 / 36 V | 一致 | p5 | "EN pin to GND pin –0.3 36 V" |
| TPS7A49 | 絶対最大 NR/SS–GND | -0.3 / 2 V | 一致 | p5 | "NR/SS pin to GND pin –0.3 2 V" |
| TPS7A49 | 絶対最大 TJ | -40 / 125 °C | 一致 | p5 | "Operating virtual junction, TJ –40 125 °C" |
| TPS7A49 | 推奨 VIN | 3 / 35 V | 一致 | p5 MIN/MAX | "VIN Input supply voltage 3 35 V" |
| TPS7A49 | 推奨 VEN | 0 / VIN | 一致 | p5 | "VEN Enable supply voltage 0 VIN V" |
| TPS7A49 | 推奨 VOUT | VFB / 33 V | 一致 | p5 | "VOUT Output voltage VFB 33 V" |
| TPS7A49 | 推奨 IOUT | 0 / 150 mA | 一致 | p5 | "IOUT Output current 0 150 mA" |
| TPS7A49 | 推奨 CIN | 2.2 / 10 µF、MIN/NOM | 一致 | p5。10 は NOM 列（MAX は空） | "CIN Input capacitor 2.2 10 µF" |
| TPS7A49 | 推奨 COUT | 2.2 / 10 µF、MIN/NOM | 一致 | p5 | "COUT Output capacitor 2.2 10 µF" |
| TPS7A49 | 推奨 CNR | 0 / 10 nF、MIN/NOM | 一致 | p5 | "CNR Noise reduction capacitor 0 10 nF" |
| TPS7A49 | 推奨 CFF | 0 / 10 nF、MIN/NOM | 一致 | p5 | "CFF Feed-forward capacitor 0 10 nF" |
| TPS7A49 | 推奨 R2 | 237 kΩ、MAX | 一致 | p5 MAX 列 | "R2 Lower feedback resistor 237 kΩ" |
| TPS7A49 | RθJA | 63.4（DGN）/ 47.7（DRB） | 一致 | p6 | "RθJA ... 63.4 47.7 °C/W" |
| TPS7A49 | RθJC(top) | 53 / 55.3 | 一致 | p6 | "RθJC(top) ... 53 55.3" |
| TPS7A49 | RθJB | 37.4 / 23.3 | 一致 | p6 | "RθJB ... 37.4 23.3" |
| TPS7A49 | ψJT / ψJB | 3.7 / 37.1（DGN） | 一致 | p6（DRB は 1.1 / 23.5） | "ψJT ... 3.7 1.1" "ψJB ... 37.1 23.5" |
| TPS7A49 | RθJC(bot) | 13.5 / 7.0 | 一致 | p6 | "RθJC(bot) ... 13.5 7.0" |
| TPS7A49 | VREF | 1.176 / 1.188 / 1.212 V、TJ=25°C、注1 | 一致 | p6 MIN/TYP/MAX | "VREF Internal reference (1) TJ = 25°C, VNR/SS = VREF 1.176 1.188 1.212 V" / "(1) VREF is measured at the NR/SS pin." |
| TPS7A49 | VFB | 1.185 V、TYP | 一致 | p6 TYP 列 | "VFB Feedback voltage 1.185 V" |
| TPS7A49 | 出力電圧範囲 | VREF〜33 V、注2（≥ 5 µA） | 一致 | p6 MIN/MAX | "(2) To ensure stability at no load conditions, a current from the feedback resistive network equal to or greater than 5 μA is required." |
| TPS7A49 | 公称精度 | ±1.5 %VOUT、TJ=25°C、VIN=VOUT(nom)+0.5V | 一致 | p6 MIN/MAX | "Nominal accuracy TJ = 25°C, VIN = VOUT(nom) + 0.5 V –1.5 1.5 %VOUT" |
| TPS7A49 | 総合精度 | ±2.5 %VOUT | 一致 | p6 | "VOUT(nom) + 1 V ≤ VIN ≤ 35 V, 1 mA ≤ IOUT ≤ 150 mA –2.5 2.5 %VOUT" |
| TPS7A49 | ライン・レギュレーション | 0.086 %VOUT、TYP | 一致 | p6 | "Line regulation TJ = 25°C, VOUT(nom) + 1 V ≤ VIN ≤ 35 V 0.086 %VOUT" |
| TPS7A49 | ロード・レギュレーション | 0.04 %VOUT、TYP | 一致 | p6 | "Load regulation TJ = 25°C, 1 mA ≤ IOUT ≤ 150 mA 0.04 %VOUT" |
| TPS7A49 | ドロップアウト（100 mA） | 260 mV、TYP（MAX 空欄） | 一致 | p6 | "VIN = 95% VOUT(nom), IOUT = 100 mA 260 mV" |
| TPS7A49 | ドロップアウト（150 mA） | 333 / 600 mV、TYP/MAX | 一致 | p6 | "VIN = 95% VOUT(nom), IOUT = 150 mA 333 600 mV" |
| TPS7A49 | 電流制限 | 220 / 309 / 500 mA | 一致 | p6 MIN/TYP/MAX | "ILIM Current limit VOUT = 90% VOUT(nom) 220 309 500 mA" |
| TPS7A49 | GND 電流（0 mA） | 49 / 100 µA | 一致 | p6 TYP/MAX | "IOUT = 0 mA 49 100 μA" |
| TPS7A49 | GND 電流（100 mA） | 800 µA、TYP | 一致 | p6 | "IOUT = 100 mA 800 μA" |
| TPS7A49 | シャットダウン電流 | 0.8 / 3 µA、VEN=0.4V | 一致 | p6 | "ISHDN Shutdown supply current VEN = 0.4 V 0.8 3 μA" |
| TPS7A49 | FB 電流 | 3 / 100 nA、注3（流れ出す向き） | 一致 | p6 | "IFB Feedback current (3) 3 100 nA" / "(3) IFB > 0 flows out of the device." |
| TPS7A49 | EN 電流 | 0.02/1、0.2/1 µA | 一致 | p6 | "VEN = VIN = VOUT(nom) + 1 V 0.02 1 μA / VEN = VIN = 35 V 0.2 1 μA" |
| TPS7A49 | EN high | 2.1 V〜VIN | 一致 | p6 MIN/MAX | "VEN(high) Enable high-level voltage 2.1 VIN V" |
| TPS7A49 | EN low | 0〜0.4 V | 一致 | p6 | "VEN(low) Enable low-level voltage 0 0.4 V" |
| TPS7A49 | 出力雑音（VREF 出力） | 15.4 µVRMS、条件どおり | 一致 | p6 TYP | "VIN = 3 V, VOUT(nom) = VREF, COUT = 10 μF, CNR/SS = 10 nF, BW = 10 Hz to 100 kHz 15.4 μVRMS" |
| TPS7A49 | 出力雑音（5 V 出力） | 21.15 µVRMS | 一致 | p6 TYP | "VIN = 6.2 V, VOUT(nom) = 5 V, COUT = 10 μF, CNR/SS = CFF (4) = 10 nF, BW = 10 Hz to 100 kHz 21.15 μVRMS" |
| TPS7A49 | PSRR（表） | 72 dB、f=120 Hz、IOUT は見出しの 1 mA | 一致 | p6 TYP。行の条件に IOUT は無いので見出しの 1 mA が効く、という読みも正しい | "PSRR ... VIN = 6.2 V, VOUT(nom) = 5 V, COUT = 10 μF, CNR/SS = CFF (4) = 10 nF, f = 120 Hz 72 dB" |
| TPS7A49 | 熱遮断 | 170 / 150 °C | 一致 | p6 TYP | "Shutdown, temperature increasing 170 / Reset, temperature decreasing 150" |
| TPS7A49 | 雑音（Features） | 12.7 µVRMS（20 Hz〜20 kHz）/ 15.4 µVRMS（10 Hz〜100 kHz） | 一致 | p1 | "12.7 μVRMS (20 Hz to 20 kHz) – 15.4 μVRMS (10 Hz to 100 kHz)" |
| TPS7A49 | PSRR（Features） | 72 dB (120 Hz)、≥ 52 dB (10 Hz〜400 kHz)、9.1.5 の Figure 29 構成 | 一致 | p1・p14。**注記:** 同じ DS のグラフ（p9 Figure 14・18、IOUT=150 mA、10 µF/10 nF）では 400 kHz で約 50 dB と読め、52 dB を下回る（最後の「参考」節） | "≥ 52 dB (10 Hz to 400 kHz)" / "The solution illustrated in Figure 29 delivers minimum noise levels of 15.4 μVRMS and power-supply rejection levels above 52 dB from 10 Hz to 400 kHz" |
| TPS7A49 | Fig14 COUT=10µF（目読み） | 73 / 71 / 59 / 54 / 62 / 50 | 一致 | p9。自分の読み: 72.6 / 71.5 / 58.6 / 54.1 / 61.9 / 50.2。山は 211 kHz・62.8 dB。引き出し線は 200 kHz 付近の山を指す（ピンクの曲線） | 凡例 "VOUT = 5V VIN = 6.2V IOUT = 150mA CNR/SS = 10nF CFF = 10nF"、"COUT = 10μF" |
| TPS7A49 | Fig14 COUT=2.2µF（目読み） | 70 / 69 / 61 / 48 / 44 / 46 | 一致 | p9。自分の読み: 69.8 / 69.1 / 61.4 / 48.2 / 43.7 / 46.0。山は 542 kHz・51.4 dB | "COUT = 2.2μF" |
| TPS7A49 | Fig16 CNR/SS=10nF（目読み） | 70 / 69 / 61 / 54 / 61 / 52 | 一致 | p9。自分の読み: 70.1 / 68.8 / 60.9 / 53.8 / 60.8 / 51.8 | 凡例 "VOUT = 1.2V VIN = 3.2V IOUT = 150mA COUT = 10μF CFF = 0nF" |
| TPS7A49 | Fig16 CNR/SS=0nF（目読み） | 71 / 62 / 45 / 46 / 57 / 51 | 一致 | p9。自分の読み: 70.9 / 61.8 / 45.1 / 46.2 / 56.5 / 50.7 | "CNR/SS = 0nF" |
| TPS7A49 | Fig18 CFF=10nF（目読み） | 73 / 72 / 59 / 54 / 62 / 50 | 一致 | p9。自分の読み: 72.6 / 71.6 / 58.6 / 54.0 / 61.7 / 49.7 | 凡例 "VOUT = 5V VIN = 6.2V IOUT = 150mA COUT = 10μF CNR/SS = 10nF" |
| TPS7A49 | Fig18 CFF=0nF（目読み） | 64 / 54 / 45 / 48 / 56 / 51 | 一致 | p9。自分の読み: 64.2 / 53.6 / 45.4 / 47.8 / 56.3 / 51.0 | "CFF = 0nF" |
| TPS7A49 | PSRR の本文（p15） | 10 nF CNR で最大 15 dB 改善（110 Hz〜200 kHz）、CFF は 10 Hz〜200 kHz を改善 | 一致 | p15 9.1.8 | "achieving up to 15 dB of additional power-supply rejection for frequencies between 110 Hz and 200 kHz" |
| TPS7A49 | 出力電圧の式 | R1 = R2 (VOUT/VFB(nom) – 1)、VFB(nom)/R2 > 5 µA | 一致 | p14 Equation 2。画像では µA、pdftotext では "mA" に化ける（確認済み） | "R1 = R2 (VOUT/VFB(nom) − 1), where VFB(nom)/R2 > 5 μA" |
| TPS7A49 | R2 の上限（設計例） | R2 < 242.4 kΩ | 一致 | p17 Equation 4 | "VREF(max)/R2 > 5μA → R2 < 242.4 kΩ" |
| TPS7A49 | ソフトスタート時間 | tSS (ms) = 1.4 × CNR/SS (nF) | 一致 | p12 Equation 1 | "tSS (ms) = 1.4 × CNR/SS (nF)" |
| TPS7A49 | CIN / COUT | 最小 2.2 µF、10 µF を強く推奨 | 一致 | p14 9.1.3 | "achieve stability with a minimum input and output capacitance of 2.2 μF; however, TI highly recommends using a 10-μF capacitor to maximize ac performance." |
| TPS7A49 | ESR | < 200 mΩ | 一致 | p14 9.1.2 | "High ESR capacitors can degrade PSRR. To ensure stability, maximum ESR must be less than 200 mΩ." |
| TPS7A49 | 誘電体 | X7R / X5R | 一致 | p14 | "Ceramic capacitors with X7R and X5R dielectrics are preferred." |
| TPS7A49 | CNR/SS・CFF | 安定には不要、10 nF を強く推奨 | 一致 | p14 9.1.4、p6 注4 | "Although noise-reduction and feed-forward capacitors (CNR/SS and CFF, respectively) are not needed to achieve stability, TI highly recommends using 10-nF capacitors" |
| TPS7A49 | CNR の雑音低減 | 69 → 17 µVRMS（約 75 %） | 一致 | p15 9.1.6 | "the output noise is reduced by approximately 75% (from 69 μVRMS to 17 μVRMS); see Figure 26." |
| TPS7A49 | ヘッドルーム（設計例） | VIN – VOUT – VDO(max) ≥ 1 V | 一致 | p16 9.2.2 | "Dropout headroom is calculated as VIN – VOUT – VDO(max), and for optimal performance must be at least 1 V." |
| TPS7A49 | 入出力コンデンサの位置 | 近く、同じ面、ビア無し | 一致 | p14 9.1.3 | "Place the input and output capacitors as close to the pin as possible, on the same side as the device; do not use vias between the capacitor and the pin." |
| TPS7A49 | 距離の上限 | 10 mm 以内 | 一致 | p19 9.3 | "Do not place the input or output capacitor more than 10 mm away from the regulator." |
| TPS7A49 | EN | 浮かせない | 一致 | p19 | "Do not float the enable (EN) pin." |
| TPS7A49 | NR/SS | 抵抗性・誘導性の負荷をつけない | 一致 | p19 | "Do not resistively or inductively load the NR/SS pin." |
| TPS7A49 | 全コンデンサの配置 | 近く・同じ面、反対面に置かない | 一致 | p19 11.1 | "Every capacitor (CIN, COUT, CNR/SS, and CFF) must be placed as close as possible to the device and on the same side of the PCB as the regulator itself." / "Do not place any of the capacitors on the opposite side of the PCB" |
| TPS7A49 | GND と PowerPAD | GND を直下の PowerPAD に直結、直下の複数ビア | 一致 | p19 11.1 | "The GND pin must be tied directly to the PowerPAD under the device. Connect the PowerPAD to any internal PCB ground planes using multiple vias directly under the device." |
| TPS7A49 | GND プレーン | VIN 側と VOUT 側を分け GND ピンで一点接続 | 一致 | p19 11.1.1 | "separate ground planes for VIN and VOUT, with each ground plane star-connected only at the GND pin of the device." |
| TPS7A49 | レイアウト例の部品サイズ | CIN・COUT 1206、CNR・R1・R2 0402 | 一致 | p21 Figure 37 の注 | "NOTE: CIN and COUT are size 1206 capacitors and CNR, R1, and R2 are size 0402." |

## 3. TI TPS7A30

| 部品 | 項目 | power.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| TPS7A30 | 出典（版） | SBVS125D、REVISED JUNE 2015 | 一致 | 各ページの見出し | "SBVS125D – AUGUST 2010 – REVISED JUNE 2015" |
| TPS7A30 | EC 表の見出し条件（p7） | \|VIN\|=\|VOUT(nom)\|+1V or 3V、IOUT=1mA、CIN=COUT=2.2µF、CNR/SS=0nF | 一致 | p7。p10 のグラフの見出しは末尾が "VOUT = VFB"（EC 表は "FB pin tied to OUT"）で同じ意味 | "At TJ = –40°C to 125°C, \|VIN\| = \|VOUT(nom)\| + 1 V or \|VIN\| = 3 V (whichever is greater), VEN = VIN, IOUT = 1 mA, CIN = 2.2 µF, COUT = 2.2 µF, CNR/SS = 0 nF, and the FB pin tied to OUT, unless otherwise noted." |
| TPS7A30 | ピン配置 | TPS7A49 と同じ並び | 一致 | p4 | "OUT 1 8 IN / FB 2 7 DNC / NC 3 6 NR/SS / GND 4 5 EN" |
| TPS7A30 | NC（3） | 開放または GND（"must"） | 一致 | p4 | "Not internally connected. This pin must either be left open or tied to GND." |
| TPS7A30 | EN（5） | 正負どちらでも動作、未使用なら IN、\|VEN\| ≤ \|VIN\| | 一致 | p4 | "If VEN ≥ VEN(+HI, min) or VEN ≤ VEN(–HI, max), the regulator is enabled. If VEN(+LO, max) ≥ VEN ≥ VEN(–LO, min), the regulator is disabled. The EN pin can be connected to IN, if not used. \|VEN\| ≤ \|VIN\|." |
| TPS7A30 | PowerPAD | 開放または GND | 一致 | p4 | "Must either be left open or tied to GND. Solder to printed-circuit-board (PCB) plane to enhance thermal performance." |
| TPS7A30 | 絶対最大 IN–GND | -36 / 0.3 V | 一致 | p5 | "IN pin to GND pin –36 0.3 V" |
| TPS7A30 | 絶対最大 OUT–GND | -33 / 0.3 V | 一致 | p5 | "OUT pin to GND pin –33 0.3 V" |
| TPS7A30 | 絶対最大 OUT–IN | -0.3 / 36 V | 一致 | p5 | "OUT pin to IN pin –0.3 36 V" |
| TPS7A30 | 絶対最大 FB–GND | -2 / 0.3 V | 一致 | p5 | "FB pin to GND pin –2 0.3 V" |
| TPS7A30 | 絶対最大 EN–IN | -0.3 / 36 V | 一致 | p5 | "EN pin to IN pin –0.3 36 V" |
| TPS7A30 | 絶対最大 EN–GND | -36 / 36 V | 一致 | p5 | "EN pin to GND pin –36 36 V" |
| TPS7A30 | 絶対最大 NR/SS–GND | -2 / 0.3 V | 一致 | p5 | "NR/SS pin to GND pin –2 0.3 V" |
| TPS7A30 | 絶対最大 TJ | -40 / 125 °C | 一致 | p5 | "Operating virtual junction, TJ –40 125 °C" |
| TPS7A30 | 推奨 VIN | -35 / -3 V | 一致 | p6 MIN/MAX | "VIN Input supply voltage –35 –3 V" |
| TPS7A30 | 推奨 VEN | 0 / VIN（印字のまま） | 一致 | p6 | "VEN Enable supply voltage 0 VIN V" |
| TPS7A30 | 推奨 VOUT | VREF / 33 V（印字のまま） | 一致 | p6。EC 表（p7）では "–33 ... VREF" | "VOUT Output voltage VREF 33 V" |
| TPS7A30 | 推奨 IOUT | 0 / 200 mA | 一致 | p6 | "IOUT Output current 0 200 mA" |
| TPS7A30 | 推奨 CIN / COUT | 2.2 / 10 µF、MIN/NOM | 一致 | p6 | "CIN Input capacitor 2.2 10 µF" "COUT Output capacitor 2.2 10 µF" |
| TPS7A30 | 推奨 CNR / CFF | 0 / 10 nF、MIN/NOM | 一致 | p6 | "CNR Noise reduction capacitor 0 10 nF" "CFF Feed-forward capacitor 0 10 nF" |
| TPS7A30 | 推奨 R2 | 237 kΩ、MAX | 一致 | p6 | "R2 Lower feedback resistor 237 kΩ" |
| TPS7A30 | RθJA | 63.4 / 47.7 | 一致 | p6 | "RθJA ... 63.4 47.7 °C/W" |
| TPS7A30 | RθJB / ψJB / RθJC(bot) | 37.4 / 37.1 / 13.5（DGN） | 一致 | p6 | "RθJB ... 37.4" "ψJB ... 37.1" "RθJC(bot) ... 13.5" |
| TPS7A30 | EC VIN | -35 / -3 V | 一致 | p7 | "VIN Input voltage –35 –3 V" |
| TPS7A30 | VREF | -1.202 / -1.179 / -1.166 V | 一致 | p7 MIN/TYP/MAX の列の印字どおり | "VREF Internal reference (2) TJ = 25°C, VNR/SS = VREF –1.202 –1.179 –1.166 V" |
| TPS7A30 | VFB | -1.176 V、TYP | 一致 | p7 | "VFB Feedback voltage –1.176 V" |
| TPS7A30 | 出力電圧範囲 | -33 V〜VREF、注3 | 一致 | p7 | "Output voltage range (3) \|VIN\| ≥ \|VOUT(nom)\| + 1 V –33 VREF V" |
| TPS7A30 | 公称 / 総合精度 | ±1.5 / ±2.5 %VOUT | 一致 | p7 | "Nominal accuracy ... –1.5 1.5" "Overall accuracy ... 1 mA ≤ IOUT ≤ 200 mA –2.5 2.5 %VOUT" |
| TPS7A30 | ライン / ロード | 0.14 / 0.04 %VOUT、TYP | 一致 | p7 | "Line regulation ... 0.14 %VOUT" "Load regulation ... 0.04 %VOUT" |
| TPS7A30 | ドロップアウト（100 mA） | 216 mV、TYP | 一致 | p7 | "VIN = 95% VOUT(nom), IOUT = 100 mA 216 mV" |
| TPS7A30 | ドロップアウト（200 mA） | 325 / 600 mV | 一致 | p7 TYP/MAX | "VIN = 95% VOUT(nom), IOUT = 200 mA 325 600 mV" |
| TPS7A30 | 電流制限 | 220 / 330 / 500 mA | 一致 | p7 | "ICL Current limit VOUT = 90% VOUT(nom) 220 330 500 mA" |
| TPS7A30 | GND 電流 | 55/100 µA、950 µA | 一致 | p7 | "IOUT = 0 mA 55 100 μA IOUT = 100 mA 950 μA" |
| TPS7A30 | シャットダウン電流 | 1 / 3 µA（±0.4 V） | 一致 | p7 | "VEN = 0.4 V 1 3 μA VEN = –0.4 V 1 3 μA" |
| TPS7A30 | FB 電流 | 14 / 100 nA、注4（流れ込む向き） | 一致 | p7 | "IFB Feedback current (4) 14 100 nA" / "(4) IFB > 0 V flows into the device." |
| TPS7A30 | EN 電流 | 0.48/1、0.51/1、0.5/1 µA | 一致 | p7 | "0.48 1 ... VIN = VEN = –35 V 0.51 1 ... VIN = –21 V, VEN = 15 V 0.5 1 μA" |
| TPS7A30 | 正側 EN high | 2〜15 V（-40〜125 °C）、1.8〜15 V（-40〜85 °C） | 一致 | p7 MIN/MAX | "TJ = –40°C to 125°C 2 15 V TJ = –40°C to 85°C 1.8 15 V" |
| TPS7A30 | 正側 EN low | 0〜0.4 V | 一致 | p7 | "VEN(+LO) ... 0 0.4 V" |
| TPS7A30 | 負側 EN high | VIN〜-2 V | 一致 | p7 | "VEN(–HI) ... VIN –2 V" |
| TPS7A30 | 負側 EN low | -0.4〜0 V | 一致 | p7 | "VEN(–LO) ... –0.4 0 V" |
| TPS7A30 | EN の説明（本文） | \|VEN\| > 2 V で動作 | 一致 | p15 8.3.3 | "turns on the regulator when \|VEN\| > 2 V, whether the voltage is positive or negative" |
| TPS7A30 | 出力雑音（VREF 出力） | 15.1 µVRMS | 一致 | p7 TYP | "VIN = –3 V, VOUT(nom) = VREF, COUT = 10 μF, CNR/SS = 10 nF, BW = 10 Hz to 100 kHz 15.1 μVRMS" |
| TPS7A30 | 出力雑音（-5 V 出力） | 17.5 µVRMS | 一致 | p7 TYP | "VIN = –6.2 V, VOUT(nom) = –5 V, COUT = 10 μF, CNR/SS = CFF (5) = 10 nF, BW = 10 Hz to 100 kHz 17.5 μVRMS" |
| TPS7A30 | PSRR（表） | 72 dB、f=120 Hz | 一致 | p7 TYP | "PSRR ... VIN = –6.2 V, VOUT(nom) = –5 V, COUT = 10 μF, CNR/SS = CFF (5) = 10 nF, f = 120 Hz 72 dB" |
| TPS7A30 | 熱遮断 | 170 / 150 °C | 一致 | p7 | "TSD ... 170 ... 150 °C" |
| TPS7A30 | PSRR（Features） | 72 dB、≥ 55 dB（10 Hz〜700 kHz） | 一致 | p1・p18 9.1.3。**注記:** p10 Figure 18（CFF=10 nF）は 400 kHz で約 54 dB、Figure 14/16（CFF=0）は 100 kHz で約 53 dB と読め、55 dB を下回る（最後の「参考」節） | "≥ 55 dB (10 Hz to 700 kHz)" / "delivers minimum noise levels of 15.1 μVRMS and power-supply rejection levels above 55 dB from 10 Hz to 700 kHz" |
| TPS7A30 | 雑音（Features） | 14 / 15.1 µVRMS | 一致 | p1 | "14 μVRMS (20 Hz to 20 kHz) – 15.1 μVRMS (10 Hz to 100 kHz)" |
| TPS7A30 | Fig14 COUT=10µF（目読み） | 69 / 68 / 60 / 53 / 57 / 57、山 約 300 kHz・約 62 dB | 一致 | p10。自分の読み: 68.7 / 67.8 / 60.1 / 53.3 / 57.7 / 56.3、山 278 kHz・62.6 dB。軸 10〜90 dB | 凡例 "VOUT = –5V VIN = –6.2V IOUT = 200mA CNR/SS = 10nF CFF = 0μF" |
| TPS7A30 | Fig14 COUT=2.2µF（目読み） | 69 / 68 / 61 / 49 / 45 / 46、山 約 600 kHz・約 53 dB | 一致 | p10。自分の読み: 69.3 / 68.4 / 60.6 / 48.6 / 45.0 / 46.6、山 610 kHz・53.4 dB | "COUT = 2.2μF" |
| TPS7A30 | Fig16 CNR/SS=10nF（目読み） | 69 / 68 / 60 / 53 / 57 / 57 | 一致 | p10。自分の読み: 69.1 / 67.9 / 60.3 / 53.3 / 57.7 / 56.4 | 凡例 "VOUT = –5V VIN = –6.2V IOUT = 200mA COUT = 10μF CFF = 0μF" |
| TPS7A30 | Fig16 CNR/SS=0nF（目読み） | 69 / 60 / 41 / 41 / 49 / 54 | 一致 | p10。自分の読み: 68.7 / 59.8 / 41.3 / 40.6 / 49.7 / 53.7 | "CNR/SS = 0nF" |
| TPS7A30 | Fig18 CFF=10nF（目読み） | 73 / 70 / 57 / 56 / 61 / 54 | 一致 | p10。自分の読み: 73.2 / 70.2 / 57.1 / 55.7 / 60.9 / 53.5 | 凡例 "VOUT = –5V VIN = –6.2V IOUT = 200mA CNR/SS = 10nF COUT = 10μF" |
| TPS7A30 | Fig18 CFF=0nF（目読み） | 65 / 59 / 53 / 54 / 58 / 61 | 一致 | p10。自分の読み: 64.5 / 59.2 / 52.6 / 54.1 / 57.8 / 60.3 | "CFF = 0nF" |
| TPS7A30 | PSRR の本文（p18） | CNR で最大 20 dB 改善（110 Hz〜400 kHz）、CFF は 10 Hz〜200 kHz | 一致 | p18 9.1.5 | "achieving up to 20 dB of additional power-supply rejection for frequencies between 110 Hz and 400 kHz" |
| TPS7A30 | 出力電圧の式 | R1 = R2 (VOUT/VFB(nom) – 1)、\|VFB(nom)\|/R2 > 5 µA | 一致 | p17 Equation 2 | "R1 = R2 (VOUT/VFB(nom) − 1), where \|VFB(nom)\|/R2 > 5μA" |
| TPS7A30 | 出力電圧範囲（本文） | -1.174 V〜-33 V（Features は -1.18 V〜） | 一致 | p17 9.1.1、p1 | "The TPS7A3001 has an output voltage range of –1.174 V to –33 V." / "Adjustable Output: –1.18 V to –33 V" |
| TPS7A30 | 1 % 抵抗の例（-15 V） | R1 = 118 kΩ、R2 = 10 kΩ | 一致 | p17 Table 2 | "–15 118 10" |
| TPS7A30 | ソフトスタート時間 | tSS (ms) = 0.9 × CNR/SS (nF)、Figure 29 は CFF なし | 一致 | p15 Equation 1 | "tSS (ms) = 0.9 × CNR/SS (nF)" / "Figure 29 shows the relationship between the CNR/SS size and the start-up time without a CFF." |
| TPS7A30 | 設計例のソフトスタート | 14 ms、CSS = 15 nF（原文のまま） | 一致 | p21 Equation 6（0.9 × 15 = 13.5 だが印字は 14 ms） | "tSS (ms) = 0.9 × CNR/SS = 14 ms CSS = 15 nF" |
| TPS7A30 | CIN / COUT | 最小 2.2 µF、10 µF を強く推奨 | 一致 | p18 9.1.2.1 | "achieve stability with a minimum input and output capacitance of 2.2 μF; however, TI highly recommends using a 10-μF capacitor to maximize ac performance." |
| TPS7A30 | コンデンサの種類 | 低 ESR、X7R/X5R、高 ESR は PSRR を悪化 | 一致 | p17 9.1.2 と NOTE | "Ceramic capacitors with X7R and X5R dielectrics are preferred." / "High-ESR capacitors can degrade PSRR." |
| TPS7A30 | CNR/SS・CFF | 安定には不要、10 nF を強く推奨 | 一致 | p18 9.1.2.2 | "Although noise-reduction and feed-forward capacitors (CNR/SS and CFF, respectively) are not needed to achieve stability, TI highly recommends using 10-nF capacitors" |
| TPS7A30 | CNR の雑音低減 | 80 → 17 µVRMS（約 80 %） | 一致 | p18 9.1.4 | "the output noise is reduced by approximately 80% (from 80 μVRMS to 17 μVRMS); see Figure 27." |
| TPS7A30 | Do's and Don'ts | 2.2 µF 以上を IN・OUT の近くに／10 mm／EN／NR/SS | 一致（注記） | p23 9.3。**注記:** 原文は「低 ESR の 2.2 µF を少なくとも 1 個」で、「以上」が掛かるのは個数。容量の下限は別に p18 で 2.2 µF と書いてあるので、意味は変わらない | "Place at least one low-ESR, 2.2-μF capacitor as close as possible to both the IN and OUT pins" / "Do not place the input or output capacitor more than 10 mm away from the regulator." |
| TPS7A30 | 全コンデンサの配置 | 近く・同じ面、反対面に置かない、ビア・長配線を避ける | 一致 | p24 11.1 | "Every capacitor (CIN, COUT, CNR/SS, and CFF) must be placed as close as possible to the device and on the same side of the PCB as the regulator itself." |
| TPS7A30 | GND と PowerPAD | 直結、直下の複数ビア | 一致 | p24 11.1 | "The GND pin must be tied directly to the PowerPAD under the device. The PowerPAD must be connected to any internal PCB ground planes using multiple vias directly under the device." |
| TPS7A30 | GND プレーン | VIN 側と VOUT 側を分け一点接続 | 一致 | p24 11.1.1 | "separate ground planes for VIN and VOUT, with each ground plane star-connected only at the GND pin of the device." |
| TPS7A30 | レイアウト例の部品サイズ | CIN・COUT 1206、CNR・R1・R2 0402 | 一致 | p25 Figure 40 の注 | "NOTE: CIN and COUT are size 1206 capacitors, and CNR, R1, and R2 are size 0402." |
| TPS7A30 | DS 内の食い違い（電流） | 表題・Features は 200 mA、8.1 Overview は 150 mA | 一致 | p1 と p14 | "Maximum Output Current: 200 mA" / "low-noise, 150-mA linear regulators (LDOs)" |

## 4. ADI（旧 Linear）LT1763

| 部品 | 項目 | power.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| LT1763 | 出典（版） | 全 22 ページ、"1763fg"、Rev G 5/10。README の "1763fh" と違う | 一致（注記） | 各ページ下 "1763fg"、p21 Revision History の最終行 "G 5/10"。README.md 58・60 行目は "1763fh"。**注記:** この PDF は各ページ下に "www.BDTIC.com/Linear" の透かしが入り、PDF の Author も "www.BDTIC.com"（第三者のミラー）。power.md は ADI 版と読めるが、中身は Linear の Rev G をミラーが配ったもの | "1763fg" / "G 5/10" |
| LT1763 | EC 表の見出し条件 | ● は全温度、それ以外は TA=25°C（Note 2） | 一致 | p4〜p6 の見出し | "The ● denotes the specifications which apply over the full operating temperature range, otherwise specifications are at TA = 25°C. (Note 2)" |
| LT1763 | IN の絶対最大 | ±20 V | 一致 | p2 | "IN Pin Voltage ........ ±20V" |
| LT1763 | 入出力差の絶対最大 | ±20 V | 一致 | p2 | "Input to Output Differential Voltage ....... ±20V" |
| LT1763 | SHDN の絶対最大 | ±20 V | 一致 | p2 | "SHDN Pin Voltage ........ ±20V" |
| LT1763 | 入力電圧範囲（Features） | 1.8〜20 V | 一致 | p1 | "Wide Input Voltage Range: 1.8V to 20V" |
| LT1763 | 最小動作電圧 | 1.8 / 2.3 V、C/I グレード、500 mA、● | 一致 | p4 TYP/MAX（MP グレードは 1.8 / 2.35） | "C, I Grade: ILOAD = 500mA (Notes 3, 11) ● 1.8 2.3 V" |
| LT1763 | 出力電圧（-5、1 mA） | 4.950 / 5 / 5.050 V、VIN=5.5V | 一致 | p4。● 無し＝25 °C | "LT1763-5 VIN = 5.5V, ILOAD = 1mA 4.950 5 5.050 V" |
| LT1763 | 出力電圧（-5、全範囲） | 4.875 / 5 / 5.125 V、6V<VIN<20V、1mA<ILOAD<500mA、● | 一致 | p4 | "6V < VIN < 20V, 1mA < ILOAD < 500mA ● 4.875 5 5.125 V" |
| LT1763 | ドロップアウト 10 mA | 0.13 / 0.19、● 0.25 V | 一致 | p5。上の行 TYP/MAX（25 °C）、下の行 ● MAX | "ILOAD = 10mA 0.13 0.19 V / ILOAD = 10mA ● 0.25 V" |
| LT1763 | ドロップアウト 50 mA | 0.17 / 0.22、● 0.32 V | 一致 | p5 | "ILOAD = 50mA 0.17 0.22 ... ● 0.32" |
| LT1763 | ドロップアウト 100 mA | 0.20 / 0.24、● 0.34 V | 一致 | p5 | "ILOAD = 100mA 0.20 0.24 ... ● 0.34" |
| LT1763 | ドロップアウト 500 mA | 0.30 / 0.35、● 0.45 V | 一致 | p5 | "ILOAD = 500mA 0.30 0.35 ... ● 0.45" |
| LT1763 | ドロップアウトの定義 | Note 6 | 一致 | p6 | "Note 6: Dropout voltage is the minimum input to output voltage differential needed to maintain regulation at a specified output current." |
| LT1763 | GND ピン電流 0 mA | 30 / 75 µA、● | 一致 | p5 | "ILOAD = 0mA ● 30 75 μA" |
| LT1763 | GND ピン電流 1 mA | 65 / 120 µA | 一致 | p5 | "ILOAD = 1mA ● 65 120 μA" |
| LT1763 | GND ピン電流 50 mA | 1.1 / 1.6 mA | 一致 | p5 | "ILOAD = 50mA ● 1.1 1.6 mA" |
| LT1763 | GND ピン電流 100 mA | 2 / 3 mA | 一致 | p5 | "ILOAD = 100mA ● 2 3 mA" |
| LT1763 | GND ピン電流 250 mA | 5 / 8 mA | 一致 | p5 | "ILOAD = 250mA ● 5 8 mA" |
| LT1763 | GND ピン電流 500 mA | 11 / 16 mA | 一致 | p5 | "ILOAD = 500mA ● 11 16 mA" |
| LT1763 | GND ピン電流の試験条件 | ドロップアウト領域で試験、最悪値 | 一致（注記） | p6 Note 7。**注記:** 原文の前半は「VIN = VOUT(NOMINAL) または 2.3 V（C/I）/ 2.35 V（MP）の大きい方、電流源負荷」。power.md の「探したが無かった」節の「試験は VIN = VOUT(NOMINAL) のみ」は、この「2.3 V の大きい方」を落としている（-5 品では VOUT(NOMINAL) の方が大きいので実害は無い） | "Note 7: GND pin current is tested with VIN = VOUT(NOMINAL) or VIN = 2.3V (C, I grade) or 2.35V (MP grade), whichever is greater, and a current source load. This means the device is tested while operating in its dropout region." |
| LT1763 | SHDN 閾値 Off→On | 0.8 / 2 V、TYP/MAX、● | 一致 | p5（MIN は空） | "Shutdown Threshold VOUT = Off to On ● 0.8 2 V" |
| LT1763 | SHDN 閾値 On→Off | 0.25 / 0.65 V、MIN/TYP、● | 一致 | p5（MAX は空） | "VOUT = On to Off ● 0.25 0.65 V" |
| LT1763 | SHDN ピン電流 | 0.1 µA / 1 µA、TYP | 一致 | p5（MAX は空） | "SHDN Pin Current (Note 9) VSHDN = 0V 0.1 μA VSHDN = 20V 1 μA" |
| LT1763 | シャットダウン時静止電流 | 0.1 / 1 µA | 一致 | p5 TYP/MAX | "Quiescent Current in Shutdown VIN = 6V, VSHDN = 0V 0.1 1 μA" |
| LT1763 | SHDN の未接続 | 未接続ならシャットダウン、未使用時は VIN へ | 一致 | p14 | "If unused, the SHDN pin must be connected to VIN. The device will be in the low power shutdown state if the SHDN pin is not connected." |
| LT1763 | Ripple Rejection | 50 / 65 dB、MIN/TYP、120 Hz、500 mA | 一致（注記） | p5。**注記:** この行に ● は無いので、50 dB の最小値は TA=25 °C だけの規定（power.md の条件欄はこれを書いていないが、見出し条件の行で ● の意味は書いてある） | "Ripple Rejection VIN – VOUT = 1.5V (Avg), VRIPPLE = 0.5VP-P, fRIPPLE = 120Hz, ILOAD = 500mA 50 65 dB" |
| LT1763 | 熱抵抗（DE） | θJA 40、θJC 5 °C/W、TJMAX 125 °C | 一致 | p2 ピン配置図の注記 | "TJMAX = 125°C, θJA = 40°C/W, θJC = 5°C/W" |
| LT1763 | 熱抵抗（S8） | θJA 70、θJC 35 °C/W、TJMAX 150 °C | 一致 | p2 | "TJMAX = 150°C, θJA = 70°C/W, θJC = 35°C/W" |
| LT1763 | θJA（DE、銅面積別） | 40 / 45 / 50 / 60 °C/W | 一致 | p17 Table 1。表面 2500/1000/225/100 mm²、裏面・基板 2500 mm² | "All measurements were taken in still air on 3/32" FR-4 board with one ounce copper." |
| LT1763 | θJA（S8、銅面積別） | 60 / 60 / 68 / 74 / 86 °C/W | 一致 | p18 Table 2。表面 2500/1000/225/100/50 mm² | "2500mm2 ... 60°C/W ... 50mm2 ... 86°C/W" |
| LT1763 | 出力コンデンサ | 最小 3.3 µF・ESR ≤ 3 Ω、CBYP 100 pF で 4.7 µF、≥1000 pF で 6.8 µF | 一致 | p16 | "A minimum output capacitor of 3.3μF with an ESR of 3Ω, or less, is recommended to prevent oscillations." / "For 100pF of bypass capacitance, 4.7μF of output capacitor is recommended. With a 1000pF bypass capacitor or larger, a 6.8μF output capacitor is recommended." |

## 5. ST L7809

| 部品 | 項目 | power.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| L7809 | 出典（版） | DocID2143 Rev 34、November 2016、全 54 ページ、Author "STMICROELECTRONICS" | 一致 | 各ページ下 "DocID2143 Rev 34"、改版履歴の最終行は 28-Nov-2016 / 34、PDF の Author も一致 | "DocID2143 Rev 34" / "28-Nov-2016 34" |
| L7809C | 表の見出し条件と脚注 a | TJ 0〜125°C、VI=15V、IO=500mA、CI=0.33µF、CO=0.1µF、最小負荷 5 mA | 一致 | p18 | "Refer to the test circuits, TJ = 0 to 125 °C, VI = 15 V, IO = 500 mA, CI = 0.33 µF, CO = 0.1 µF unless otherwise specified" / "Minimum load current for regulation is 5 mA." |
| L7809C | 出力電圧（25 °C） | 8.64 / 9 / 9.36 V | 一致 | p18 Min/Typ/Max | "VO Output voltage TJ = 25 °C 8.64 9 9.36 V" |
| L7809C | 出力電圧（負荷・入力範囲） | 8.55 / 9 / 9.45 V、IO 5 mA〜1 A、VI 11.5〜22 V | 一致 | p18 | "IO = 5 mA to 1 A, VI = 11.5 to 22 V 8.55 9 9.45 V" |
| L7809C | 出力電圧（1 A、22〜26 V） | 8.55 / 9 / 9.45 V | 一致 | p18 | "IO = 1 A, VI = 22 to 26 V, TJ = 25 °C 8.55 9 9.45 V" |
| L7809C | ライン・レギュレーション | 180 / 90 mV、Max（Typ 空） | 一致 | p18 | "VI = 11.5 to 26 V, TJ = 25 °C 180 / VI = 12 to 18 V, TJ = 25 °C 90 mV" |
| L7809C | ロード・レギュレーション | 180 / 90 mV、Max | 一致 | p18 | "IO = 5 mA to 1.5 A, TJ = 25 °C 180 / IO = 250 to 750 mA, TJ = 25 °C 90 mV" |
| L7809C | 静止電流 | 8 mA、Max（Typ 空）、IO は見出しの 500 mA | 一致 | p18 | "Id Quiescent current TJ = 25 °C 8 mA" |
| L7809C | 静止電流の変化 | 0.5 / 1 mA、Max | 一致 | p18 | "∆Id ... IO = 5 mA to 1 A 0.5 / VI = 11.5 to 26 V 1 mA" |
| L7809C | ドロップアウト | 2 V、Typ（Min・Max 空）、IO = 1 A、TJ = 25 °C | 一致 | p18 | "Vd Dropout voltage IO = 1 A, TJ = 25 °C 2 V" |
| L7809C | SVR | 55 dB、Min | 一致 | p18 Min 列 | "SVR Supply voltage rejection VI = 12 to 23 V, f = 120 Hz 55 dB" |
| L7809C | 出力雑音 | 70 µV/VO、Typ | 一致 | p18 | "eN Output noise voltage B = 10 Hz to 100 kHz, TJ = 25 °C 70 µV/VO" |
| L7809C | 出力抵抗 | 17 mΩ、Typ | 一致 | p18 | "RO Output resistance f = 1 kHz 17 mΩ" |
| L7809C | 短絡電流 / ピーク | 0.40 / 2.2 A、Typ | 一致 | p18 | "Isc Short circuit current VI = 35 V, TJ = 25 °C 0.40 A / Iscp ... TJ = 25 °C 2.2 A" |
| L7809C | 出力電圧ドリフト | -1 mV/°C、Typ | 一致 | p18 | "∆VO/∆T Output voltage drift IO = 5 mA -1 mV/°C" |
| L7809C | 最小負荷 | 5 mA（脚注 a） | 一致 | p18 | "Minimum load current for regulation is 5 mA." |
| L7809A | 表の見出し条件 | VI=15V、IO=1A、TJ 0〜125（AC）/ -40〜125（AB） | 一致 | p10 | "VI = 15 V, IO = 1 A, TJ = 0 to 125 °C (L7809AC), TJ = -40 to 125 °C (L7809AB), unless otherwise specified" |
| L7809A | 出力電圧（25 °C） | 8.82 / 9 / 9.18 V | 一致 | p10 | "VO Output voltage TJ = 25 °C 8.82 9 9.18 V" |
| L7809A | 出力電圧（範囲） | 8.65 / 9 / 9.35 V、VI 10.6〜22 V | 一致 | p10 | "IO = 5 mA to 1 A, VI = 10.6 to 22 V 8.65 9 9.35 V" |
| L7809A | ライン・レギュレーション | 12 / 90 mV、Typ/Max | 一致 | p10（他に 3 条件の行がある） | "VI = 10.6 to 25 V, IO = 500 mA, TJ = 25 °C 12 90 mV" |
| L7809A | 静止電流 | 4.3 / 6 mA（25 °C）、6 mA | 一致 | p10 | "Iq Quiescent current TJ = 25 °C 4.3 6 mA / 6 mA" |
| L7809A | ドロップアウト | 2 V、Typ | 一致 | p10 | "Vd Dropout voltage IO = 1 A, TJ = 25 °C 2 V" |
| L7809A | SVR | 61 dB、Typ | 一致 | p10 Typ 列 | "SVR Supply voltage rejection VI = 11.5 to 21.5 V, f = 120 Hz, IO = 500 mA 61 dB" |
| L78 | 入力電圧の絶対最大 | 35 V（VO = 5〜18 V） | 一致 | p5 Table 1（VO = 20, 24 V は 40 V） | "VI DC input voltage for VO= 5 to 18 V 35" |
| L78 | 動作接合温度 | 0〜125（C, AC）/ -40〜125（AB） | 一致 | p5 | "TOP Operating junction temperature range for L78xxC, L78xxAC 0 to 125 for L78xxAB -40 to 125" |
| L78 | 熱抵抗 | TO-220 50/5、TO-220FP 60/5、D²PAK 62.5/3、DPAK 100/8 | 一致 | p5 Table 2 | "RthJC ... 3 8 5 5" "RthJA ... 62.5 100 50 60" |
| L78 | ピン配置 | TO-220/FP 上から OUTPUT / GROUND / INPUT、TO-220 のタブは GND | 一致 | p4 Figure 2。GND の字はタブ側に TO-220・D²PAK・DPAK で付き、TO-220FP には無い。ピン番号の記載は無い | "Figure 2: Pin connections (top view)" |
| L78 | 入力コンデンサ | 0.33 µF 以上、低インピーダンス、最短 | 一致 | p23 6.1 | "A 0.33 µF or larger tantalum, mylar or other capacitor having low internal impedance at high frequencies should be chosen." |
| L78 | 出力コンデンサ | 安定には不要、過渡応答が改善 | 一致 | p23 Figure 8 の注 1 | "Although no output capacitor is need for stability, it does improve transient response." |
| L78 | ドロップアウトの温度特性（目読み） | 25 °C: 1 A ≈ 2.0、500 mA ≈ 1.75、200 mA ≈ 1.6、20 mA ≈ 1.5、0 mA ≈ 0.95 V | 一致 | p31 Figure 28（L78XX、∆VO = 5% of VO）。自分の読み（300 dpi、25 °C の格子線の両隣 4 列の平均）: 2.01 / 1.75 / 1.59 / 1.49 / 0.96 V | "Figure 28: Dropout voltage vs junction temperature ... L78XX ... DROPOUT CONDITIONS ∆VO = 5% of VO" |

---

## 無いとされていたが DS にあった項目

**「探したが DS に無かった」とされた 27 項目のうち、規定値として実は DS にあったものは無かった。** 全文検索（pdftotext）と該当ページの画像で確かめた
（RS6 の "fuse" は 0 件、TPS7A30 の "ESR" は "High-ESR capacitors can degrade PSRR." ほかの定性的な文だけ、L7809C の表に VI 範囲・Vd の Max・Id の Typ の行は無い、など）。

ただし、規定値ではないが近い情報が DS にあるものが次のとおり。power.md の書き方（「規定値は無い」）は正しいが、読む人は「何も無い」と受け取りかねない。

| 部品 | power.md で「無い」とされた項目 | DS にあったもの（ページ） |
|---|---|---|
| LT1763 | GND ピン電流の VIN = 20 V 付近での規定値 | 規定値は無い。ただし p9〜p10 に **GND Pin Current vs 入力電圧の典型値グラフ**が品種ごとにある（LT1763-5 は 100 / 300 / 500 mA 負荷、**VIN 10 V まで**）。p10 に "GND Pin Current vs ILOAD"（VIN = VOUT(NOMINAL) + 1V）もある。また Note 7 の試験条件は「VOUT(NOMINAL) **または 2.3 V の大きい方**」（上の表の注記） |
| LT1763 | SHDN 閾値の Off→On の MIN、On→Off の MAX | 規定値は無い。p10 に **SHDN Pin Threshold（On-to-Off / Off-to-On）の温度特性グラフ**（典型値。Off-to-On は 1 mA と 500 mA の 2 本、-50 °C で約 0.8 V が最大） |
| TPS7A49 | ソフトスタートの式の適用範囲 | 規定は無い。p10 に Figure 19・20 "Capacitor-Programmable Soft-Start" の波形（VOUT = 1.2 V、VIN = 3 V、IOUT = 100 mA、COUT = 10 µF、CNR/SS = 0 nF / 10 nF）がある |
| TPS7A49 | 出力コンデンサの上限容量 | power.md のとおり規定値は無く、設計例 Eq.8（p17）で ICL(max) = 500 mA を使って 35 µF。**TPS7A30 の同じ設計例（p21 Eq.8）は ICL(min) = 220 mA を使って 15.4 µF** で、power.md の TPS7A30 の節にはこの対の値が載っていない |
| TPS7A49 | PSRR の 100 kHz 以上の保証値 | 保証値は無い。p16 9.1.10 に「オーディオ帯で PSRR > 55 dB」という文がある（"The very high power-supply ratio (> 55 dB) and low noise at the audio band ... see Figure 18."）。規定ではなく説明文 |

### power.md に載っていないが、同じページにあって設計に効きそうなもの（参考）

「無い」と書かれてはいないので誤りではない。power.md は自分で拾う範囲を決めているので、足りない指摘ではなく、読む人へのメモ。

- **LT1763 の PSRR の周波数特性（p11、典型値）:** "Input Ripple Rejection" の 2 枚のグラフ（IL = 500 mA、VIN = VOUT(NOMINAL) + 1V + 50mVRMS）。COUT = 10 µF のとき、**100 kHz で約 40 dB、200 kHz で約 30 dB、1 MHz で約 22 dB**（自分の目読み、250 dpi）。power.md が載せているのは 120 Hz の 50 / 65 dB だけ。RS6 のスイッチング周波数の下限 200 kHz では、この石の除去比は 120 Hz の値よりずっと小さい。
- **LT1763 の最小 ESR（p16 Figure 3）:** 「最大 ESR は 3 Ω、**最小 ESR はバイパス容量で決まる**」とあり、COUT が小さいと ESR ≈ 0（セラミック）では安定域の外になる。power.md は最大 3 Ω だけ載せている。原文: "The minimum ESR needed is defined by the amount of bypass capacitance used, while the maximum ESR is 3Ω."（README.md の LT1763 の行はこの図に触れている）
- **TPS7A49 / TPS7A30 の絶対最大定格:** power.md は "FB pin to IN pin" と "NR/SS pin to IN pin" の行（TPS7A49: -36 / 0.3 V、TPS7A30: -0.3 / 36 V）を省いている（p5）。

### DS の中の数字の食い違い（power.md の誤りではない）

- **TPS7A49:** Features と 9.1.5（p14）は「10 Hz〜400 kHz で ≥ 52 dB」。ところが 9.1.5 が参照している Figure 18（p9、10 µF/10 nF/10 nF、IOUT = 150 mA）を自分で読むと、**400 kHz で 49.7 dB**（Figure 14 の 10 µF 曲線も 50.2 dB）。52 dB が成り立つのは、グラフと違う条件（たとえば見出しの IOUT = 1 mA）のときかもしれない。**RS6 の 200 kHz では約 62 dB（共振の山）なので、この食い違いは 200 kHz の評価には効かない。**
- **TPS7A30:** Features と 9.1.3（p18）は「10 Hz〜700 kHz で ≥ 55 dB」。Figure 18（p10、CFF = 10 nF）を読むと **400 kHz で 53.5 dB**、Figure 14 / 16（CFF = 0）は 100 kHz で 53.3 dB。200 kHz では CFF = 10 nF で 60.9 dB、CFF = 0 で 57.7 dB。
- **TPS7A49 p16:** 9.2.2 は「ドロップアウト・ヘッドルーム ＝ VIN – VOUT – VDO(max)、1 V 以上」と定義しながら、同じ段落で VIN – VOUT = 1.8 V を「ヘッドルーム 1.8 V」と呼んでいる（その定義で計算すると 3 – 1.2 – 0.6 = 1.2 V）。power.md は定義の文だけを引いているので問題ない。
