# スペアナ ADC（PCM1804）への信号タップ候補 — データシートの事実

2026-09-25 収集。値は DS の原文で裏が取れたものだけ。設計判断は書かない。
対象は Q2（差動抵抗タップ＋高 CMRR 差動アンプ）／Q3（アイソレーション・アンプ）／Q4（デジタル・アイソレータ）／Q5（小型ライン・トランス）。

- 出典のページは **PDF のページ番号**。印刷ページ番号とずれる DS はその都度「PDF pN（印刷 pM）」と書いた（ミラーから取った ADI の一部は、先頭付近に ADI の "Product Page Quick Links" ページが 1 枚挟まっていて 1 ずれる）。PDF はすべて `AudioV2.1/datasheets/tap/` にある。
- 「列」はその値が表のどの列に印刷されているか。表に min/typ/max の列が無いものは「値の列のみ」と書き、値に付いた `typ.` などの字句はそのまま残した。パッケージ別の列（DW/DBQ など）の表は「パッケージ列」と書いた。
- 「画像で確認」は、ページを `pdftoppm -r 90〜150` で画像にして、表の罫線と列見出しを目で確かめたもの。
- 「目読み」はグラフの値。ページを画像にして格子線から読んだ。規定値ではない。読み取り誤差は目盛の刻みの半分程度（対数軸では ±20〜30 % 程度）はある。
- 原文の引用は `pdftotext -layout` の抽出そのまま。抽出でギリシャ文字が化けたもの（例: ADI 旧 DS の `±` が `6`、Ω が `V`）は画像で確かめて直した字で書いた。
- 値の換算（dBu↔Vrms、%↔dB、入力換算↔出力換算など）はしていない。

## 取得元と版

analog.com は proxy 経由で接続が切られた（HTTP/2 `INTERNAL_ERROR`、HTTP/1.1 でも `Empty reply`）。ADI の DS はミラーから取った。**ミラー版が ADI 公式の最新版と同一かは確認していない**（版記号は PDF 内の印字で読んだ）。

| ファイル | 品名 | 版（PDF 内の印字） | 取得元 URL |
|---|---|---|---|
| `TI_INA1620.pdf` | INA1620 | SBOS859B – MARCH 2018 – REVISED JULY 2018 | https://www.ti.com/lit/ds/symlink/ina1620.pdf |
| `TI_INA1650.pdf` | INA1650/INA1651 | SBOS818B – DECEMBER 2016 – REVISED NOVEMBER 2018 | https://www.ti.com/lit/ds/symlink/ina1650.pdf |
| `TI_INA134.pdf` | INA134/INA2134 | SBOS071（改訂日の印字なし。Burr-Brown 版） | https://www.ti.com/lit/ds/symlink/ina134.pdf |
| `TI_INA137.pdf` | INA137/INA2137 | SBOS072（改訂日の印字なし。Burr-Brown 版） | https://www.ti.com/lit/ds/symlink/ina137.pdf |
| `THAT_1200.pdf` | THAT 1200/1203/1206 | Document 600033 Rev 01（© 2017） | https://www.thatcorp.com/datashts/THAT_1200-Series_Datasheet.pdf |
| `ADI_SSM2141.pdf` | SSM2141 | REV. C | ミラー https://datasheet4u.com/pdf/501868/SSM2141.pdf |
| `ADI_SSM2143.pdf` | SSM2143 | REV. 0 | ミラー https://datasheet4u.com/pdf/501875/SSM2143.pdf |
| `ADI_AD8274.pdf` | AD8274 | Rev. C（PDF p2 が挿入ページ。PDF p3 以降は印刷 +1） | ミラー https://datasheet4u.com/pdf/648890/AD8274.pdf |
| `TI_AMC1311.pdf` | AMC1311/AMC1311B | SBAS786C – DECEMBER 2017 – REVISED JUNE 2022 | https://www.ti.com/lit/ds/symlink/amc1311.pdf |
| `TI_AMC1300.pdf` | AMC1300/AMC1300B | SBAS895D – MAY 2018 – REVISED MAY 2022 | https://www.ti.com/lit/ds/symlink/amc1300.pdf |
| `TI_ISO224.pdf` | ISO224A/B | SBAS738A – JUNE 2018 – REVISED OCTOBER 2018 | https://www.ti.com/lit/ds/symlink/iso224.pdf |
| `TI_AMC3330.pdf` | AMC3330 | SBASA34B – JUNE 2020 – REVISED AUGUST 2024 | https://www.ti.com/lit/ds/symlink/amc3330.pdf |
| `TI_AMC3336.pdf` | AMC3336 | SBASA70 – APRIL 2021 | https://www.ti.com/lit/ds/symlink/amc3336.pdf |
| `ADI_AD215.pdf` | AD215 | REV. 0（© 1996。PDF p2 が挿入ページ "Last Content Update: 08/30/2016"。PDF p3 以降は印刷 +1） | ミラー https://www.farnell.com/datasheets/2170142.pdf |
| `ADI_ADuM3190.pdf` | ADuM3190 | Rev. A（PDF p3 以降は印刷 +1） | ミラー https://datasheet4u.com/pdf/759865/ADUM3190.pdf |
| `Broadcom_ACPL-C87x.pdf` | ACPL-C87B/C87A/C870 | AV02-3563EN（© 2016–2024） | https://docs.broadcom.com/doc/AV02-3563EN |
| `Broadcom_HCPL-7800.pdf` | HCPL-7800A/HCPL-7800 | AV02-0410EN（© 2008–2020） | https://docs.broadcom.com/doc/HCPL-7800-7800A-Isolation-Amplifier-DS |
| `Skyworks_Si8920.pdf` | Si8920 | 206333A • July 26, 2022（Skyworks 公式 URL は 404。ミラー） | ミラー https://datasheet4u.com/pdf/1499508/Si8920.pdf |
| `TI_ISO7741.pdf` | ISO7740/7741/7742 | SLLSEP4K – MARCH 2016 – REVISED AUGUST 2026 | https://www.ti.com/lit/ds/symlink/iso7741.pdf |
| `TI_ISO7762.pdf` | ISO7760〜7763 | SLLSER1H – AUGUST 2017 – REVISED JANUARY 2024 | https://www.ti.com/lit/ds/symlink/iso7762.pdf |
| `TI_ISO1540.pdf` | ISO1540/ISO1541 | SLLSEB6F – JULY 2012 – REVISED DECEMBER 2022 | https://www.ti.com/lit/ds/symlink/iso1540.pdf |
| `ADI_ADuM1250.pdf` | ADuM1250/ADuM1251 | Rev. L（9/2025） | ミラー https://datasheet4u.com/pdf/563618/ADUM1250.pdf |
| `ADI_ADuM1400.pdf` | ADuM1400/1401/1402 | Rev. M（2/2025） | ミラー https://datasheet4u.com/pdf/944584/ADuM1401.pdf |
| `Skyworks_Si864x.pdf` | Si864x | 206329A • July 26, 2022（改訂履歴の最新 Revision 2.16） | https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/si864x-datasheet.pdf |
| `Skyworks_Si860x.pdf` | Si860x | Rev. 206852A • February 23, 2024 | https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/si860x.pdf |
| `ADI_ADuM5401.pdf` | ADuM5401〜5404 | Rev. C | ミラー https://datasheet4u.com/pdf/623246/ADUM5401.pdf |
| `TI_ISOW7741.pdf` | ISOW7740〜7744 | SLLSFK1C – SEPTEMBER 2021 – REVISED APRIL 2022（本文 © 2023） | https://www.ti.com/lit/ds/symlink/isow7741.pdf |
| `TI_ISOW1044.pdf` | ISOW1044 | SLLSFF7B – MAY 2021 – REVISED AUGUST 2026 | https://www.ti.com/lit/ds/symlink/isow1044.pdf |
| `Jensen_JT-11P-1.pdf` | JT-11P-1 | 版の印字なし（PDF 作成日 2014-10-27） | https://www.jensen-transformers.com/wp-content/uploads/2014/08/jt-11p-1.pdf |
| `Lundahl_LL1540.pdf` | LL1540 | 右下に "R980616" の印字 | http://www.lundahl.se/wp-content/uploads/datasheets/1540.pdf |
| `Hammond_560.pdf` | 560G | 版の印字なし | https://www.hammfg.com/files/parts/pdf/560G.pdf |
| `Hammond_560_series.pdf` | 560 シリーズ一覧 | © 2026 | https://www.hammfg.com/electronics/transformers/audio/560.pdf |
| `Hammond_101-106.pdf` | 101 シリーズ一覧 | © 2026 | https://www.hammfg.com/electronics/transformers/audio/101.pdf |
| `Triad_TY-250P.pdf` | TY-250P | Publish Date: May 31, 2019 | https://catalog.triadmagnetics.com/asset/ty-250p.pdf |
| `Triad_TY-146P.pdf` | TY-146P | Publish Date: May 31, 2019 | https://catalog.triadmagnetics.com/asset/ty-146p.pdf |

---

# Q2 差動抵抗タップ＋高 CMRR 差動アンプ

## Q2-1. TI INA1620（抵抗ペア内蔵の低雑音デュアル・オペアンプ、QFN-24）

出典: `TI_INA1620.pdf`。表の既定条件（p5, p6）: "at TA = 25°C, VS = ±2 V to ±18 V, VCM = VOUT = midsupply, and RL = 1 kΩ (unless otherwise noted)"。表 p5 は画像で確認（THD+N の % 値は MIN〜MAX にまたがるセルの中央、dB 値は TYP 列）。

**⚠ この DS の CMRR・入力インピーダンスは内蔵オペアンプ単体の値。** 内蔵 1 kΩ 抵抗ペアで差動アンプを組んだときの CMRR の規定は表に無い（抵抗ペアのマッチングだけが規定されている）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨） | 単電源 4〜36 V／両電源 ±2〜±18 V | — | MIN / MAX | p4 §6.3 | "Single-supply 4 36 / Dual-supply ±2 ±18" |
| THD+N | 0.000025 % / −132 dB | G = 1, f = 1 kHz, VOUT = 3.5 VRMS, RL = 2 kΩ, 80-kHz measurement bandwidth | TYP | p5 §6.5（画像で確認） | "G = 1, f = 1 kHz, VOUT = 3.5 VRMS, RL = 2 kΩ, 80-kHz measurement bandwidth 0.000025% –132 dB" |
| THD+N | 0.000025 % / −132 dB | 同上、RL = 600 Ω | TYP | p5 | 同表 |
| THD+N vs 周波数 | 20 Hz〜2 kHz で約 −128 dB（目読み。10 kΩ/2 kΩ/600 Ω 負荷、G = ±1） | 3.5 VRMS, 80-kHz measurement bandwidth | グラフ | p9 Figure 14（画像で確認） | "Figure 14. THD+N Ratio vs Frequency" / "3.5 VRMS, 80-kHz measurement bandwidth" |
| 入力電圧雑音 | 2.1 µVPP | f = 20 Hz to 20 kHz | TYP | p5 | "Input voltage noise f = 20 Hz to 20 kHz 2.1 μVPP" |
| 入力電圧雑音密度 | 6.5 / 3.5 / 2.8 nV/√Hz | f = 10 Hz / 100 Hz / 1 kHz | TYP | p5 | "f = 10 Hz 6.5 / f = 100 Hz 3.5 / f = 1 kHz 2.8 nV/√Hz" |
| 入力電流雑音密度 | 1.6 / 0.8 pA/√Hz | f = 10 Hz / 1 kHz | TYP | p5 | "f = 10 Hz 1.6 / f = 1 kHz 0.8 pA/√Hz" |
| CMRR（オペアンプ単体） | 108 / 127 dB | (V–) + 1.5 V ≤ VCM ≤ (V+) – 1 V, TA = –40°C to 125°C, VS = ±18 V | MIN / TYP | p5 | "CMRR Common-mode rejection ratio ... VS = ±18 V 108 127 dB" |
| CMRR vs 周波数（オペアンプ単体、入力換算） | 約 127 dB（〜100 Hz）、約 115 dB（1 kHz）、約 97 dB（10 kHz）、約 78 dB（100 kHz）（目読み） | TA = 25°C, VS = ±18 V, RL = 2 kΩ | グラフ | p10 Figure 22（画像で確認） | "Figure 22. CMRR vs Frequency (Referred to Input)" |
| 入力インピーダンス（オペアンプ単体） | 差動 60k ‖ 0.8、同相 500M ‖ 0.9（Ω ‖ pF） | — | TYP | p6 | "Differential 60k || 0.8 / Common-mode 500M || 0.9 Ω || pF" |
| 抵抗ペアの比マッチング | 0.004 % / 0.02 %（TA = –40〜125°C で max 0.023 %） | Resistors in same pair | TYP / MAX | p6 | "Resistor ratio matching (3) Resistors in same pair 0.004% 0.02%" |
| 抵抗ペアの比の温度係数 | ±0.07 / ±0.15 ppm/°C | 同上 | TYP / MAX | p6 | "Resistors in same pair ±0.07 ±0.15 ppm/°C" |
| 個別抵抗値 | 0.84 / 1 / 1.15 kΩ | — | MIN / TYP / MAX | p6 | "Individual resistor value 0.84 1 1.15 kΩ" |
| 静止電流（1 ch あたり） | 2.6 / 3.3 mA（−40〜125°C で max 4.2） | VEN = 2 V, IOUT = 0 A | TYP / MAX | p6 | "Quiescent current (per channel) VEN = 2 V, IOUT = 0 A 2.6 3.3 mA" |

## Q2-2. TI INA1650/INA1651（SoundPlus 差動ライン・レシーバ、G = 1）

出典: `TI_INA1650.pdf`。表の既定条件（p6, p7）: "at TA = 25°C, VS = ±2.25 V to ±18 V, VCM = VOUT = midsupply, and RL = 2 kΩ (unless otherwise noted)"。p6・p7 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨） | 4.5 (±2.25)〜36 (±18) V | — | MIN / MAX | p5 §6.3 | "Supply voltage (V+ – V–) 4.5 (±2.25) 36 (±18) V" |
| THD+N | 0.00039 % / −108.1 dB | VO = 3 VRMS, f = 1kHz, 90-kHz measurement bandwidth, VS = ±18 V | TYP | p6（画像で確認） | "VO = 3 VRMS, f = 1kHz, 90-kHz measurement bandwidth, VS = ±18 V 0.00039% –108.1 dB" |
| THD+N | 0.000174 % / −115.2 dB | VIN = 22 dBu (9.7516 VRMS), FIN = 1 kHz, VS = ±18 V, 90-kHz measurement bandwidth | TYP | p6 | "VIN = 22 dBu (9.7516 VRMS) , FIN = 1 kHz, VS = ±18 V, 90-kHz measurement bandwidth 0.000174% –115.2 dB" |
| THD+N vs 周波数 | 20 Hz〜10 kHz で約 0.0004 %（約 −108 dB）、ほぼ平坦（目読み） | 3 VRMS, 90-kHz Measurement Bandwidth, 600 Ω / 2 kΩ | グラフ | p9 Figure 12（画像で確認） | "3 VRMS, 90-kHz Measurement Bandwidth" |
| THD+N vs 出力振幅 | 1 VRMS で約 −100 dB、10 VRMS 付近で約 −112 dB（目読み。振幅に反比例して下がる形） | 1 kHz, 90-kHz Measurement Bandwidth | グラフ | p10 Figure 14 | "1 kHz, 90-kHz Measurement Bandwidth" |
| 出力電圧雑音 | 4.5 µVRMS / −104.7 dBu | f = 20 Hz to 20 kHz, no weighting | TYP | p6 | "Output voltage noise f = 20 Hz to 20 kHz, no weighting 4.5 μVRMS –104.7 dBu" |
| 出力電圧雑音密度 | 47 / 31 nV/√Hz | f = 100 Hz / 1 kHz | TYP | p6 | "Output voltage noise density(2) f = 100 Hz 47 / f = 1 kHz 31 nV/√Hz" |
| CMRR | 85 / 91 dB（−40〜125°C: 82 / 89） | (V–) + 0.25 V ≤ VCM ≤ (V+) – 2 V, REF and COM pins connected to ground, VS = ±18 V | MIN / TYP | p6 | "REF and COM pins connected to ground, VS = ±18 V 85 91 dB" |
| CMRR | 82 / 86 dB（−40〜125°C: 76 / 84） | 同、REF and COM pins connected to VMID(OUT) | MIN / TYP | p6 | "connected to VMID(OUT), VS = ±18 V 82 86" |
| CMRR（信号源不整合） | 84 dB | 同（ground）、RS mismatch = 20 Ω | TYP | p6 | "RS mismatch = 20 Ω 84 dB" |
| CMRR vs 周波数 | REF/COM→GND: 約 91 dB（10 Hz〜1 kHz）、約 88 dB（10 kHz）、約 78 dB（100 kHz）。REF/COM→VMID: 約 86 dB（〜10 kHz）（目読み） | TA = 25°C, VS = ±18 V | グラフ | p9 Figure 9（画像で確認） | "Figure 9. Common-Mode Rejection Ratio vs Frequency" |
| CMRR と RCOM（本文） | 20 Ω の不整合で 92 dB → 83.7 dB（RCOM = 0）、89.6 dB（RCOM = 1 MΩ） | Figure 43 | 本文 | p18 §8.1.2 | "a 20-Ω source impedance mismatch degrades the CMRR from 92 dB to 83.7 dB. However, if RCOM has a value of 1 MΩ, the CMRR only degrades to 89.6 dB" |
| 入力インピーダンス | 差動 850 / 1000 / 1150 kΩ、同相 212.5 / 250 / 287.5 kΩ | — | MIN / TYP / MAX | p7（画像で確認） | "Differential 850 1000 1150 kΩ / Common-mode 212.5 250 287.5 kΩ" |
| 入力抵抗の不整合 | 0.01 % / 0.25 % | — | TYP / MAX | p7 | "Input resistance mismatch 0.01% 0.25%" |
| 利得誤差 | 0.04 % / 0.05 % | 25°C | TYP / MAX | p6 | "Gain error 0.04% 0.05%" |
| 利得非直線性 | 1 / 5 ppm | VS = ±18 V, –10 V < VO < 10 V | TYP / MAX | p6 | "Gain nonlinearity VS = ±18 V, –10 V < VO < 10 V (2) 1 5 ppm" |
| 静止電流 | INA1650: 8 / 10.5 / 12 mA（−40〜125°C で max 14） | IOUT = 0 A | MIN / TYP / MAX | p7 | "IOUT = 0 A, INA1650 8 10.5 12 ... 14 mA"（「1 ch あたり」の字句は無い） |

## Q2-3. TI INA134/INA2134（差動ライン・レシーバ、0 dB）

出典: `TI_INA134.pdf`。表の既定条件（p2）: "At TA = +25°C, VS = ±18V, RL = 2kΩ, and Ref Pin connected to Ground, unless otherwise noted."。p2 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| THD+N | 0.0005 % | f = 1kHz, VIN = 10Vrms（測定帯域の記載なし） | TYP | p2（画像で確認） | "Total Harmonic Distortion + Noise, f = 1kHz VIN = 10Vrms 0.0005 %" |
| Noise Floor | −100 dBu | 20kHz BW | TYP | p2 | "Noise Floor(1) 20kHz BW –100 dBu" |
| 出力雑音電圧 | 7 µVrms（20 Hz〜20 kHz）／52 nV/√Hz（1 kHz） | 注 (2) アンプの電流雑音と抵抗網の熱雑音を含む | TYP | p2 | "f = 20Hz to 20kHz 7 µVrms / f = 1kHz 52 nV/√HZ" |
| CMR | 74 / 90 dB | VCM = ±31V, RS = 0Ω | MIN / TYP | p2 | "Common-Mode Rejection VCM = ±31V, RS = 0Ω 74 90 dB" |
| CMR vs 周波数 | 約 90 dB（1〜10 kHz）、約 86 dB（20 kHz）、約 70 dB（100 kHz）（目読み） | TA = +25°C, VS = ±18V | グラフ | p5（画像で確認） | "COMMON-MODE REJECTION vs FREQUENCY" |
| CMR と信号源不整合（本文） | 10 Ω の不整合で典型品が約 74 dB | — | 本文 | p8 | "A 10Ω mismatch in source impedance will degrade the common-mode rejection of a typical device to approximately 74dB." |
| THD+N vs 周波数 | VO = 10Vrms で 20 Hz〜約 5 kHz ほぼ 0.0005〜0.0006 %、20 kHz で 0.001〜0.002 %（負荷で違う）（目読み） | TA = +25°C, VS = ±18V | グラフ | p4 | "TOTAL HARMONIC DISTORTION+NOISE vs FREQUENCY" / "VO = 10Vrms" |
| 高調波成分 vs 周波数 | VO = 1Vrms、RL = 2kΩ の 2 次: 1 kHz で約 0.00006 %。"noise limited" の線は約 0.00004 %（目読み） | — | グラフ | p4 | "HARMONIC DISTORTION PRODUCTS vs FREQUENCY" / "VO = 1Vrms" |
| 入力インピーダンス | 差動 50 kΩ、同相 50 kΩ | 注 (4) 25kΩ 抵抗は比マッチ、絶対値 ±25 % | TYP | p2 | "Differential 50 kΩ / Common-Mode 50 kΩ" / "(4) 25kΩ resistors are ratio matched but have ±25% absolute value." |
| 利得誤差／非直線性 | ±0.02 / ±0.1 %、非直線性 0.0001 % | VO = –16V to 16V | TYP / MAX（非直線性は TYP） | p2 | "Error VO = –16V to 16V ±0.02 ±0.1 % / Nonlinearity 0.0001 %" |
| 電源電圧範囲 | ±4 / ±18 V | — | MIN / MAX | p2 | "Voltage Range ±4 ±18 V" |
| 静止電流（アンプ 1 個あたり） | ±2.4 / ±2.9 mA | IO = 0 | TYP / MAX | p2 | "Quiescent Current (per Amplifier) IO = 0 ±2.4 ±2.9 mA" |

## Q2-4. TI INA137/INA2137（差動ライン・レシーバ、G = 1/2 または 2）

出典: `TI_INA137.pdf`。表の既定条件（p2）: "At TA = +25°C, VS = ±18V, RL = 2kΩ, G = 1/2, and Ref Pin connected to Ground, unless otherwise noted."。p2 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| THD+N | 0.0005 % | f = 1kHz, VIN = 10Vrms（測定帯域の記載なし） | TYP | p2（画像で確認） | "Total Harmonic Distortion + Noise, f = 1kHz VIN = 10Vrms 0.0005 %" |
| Noise Floor, RTO | −106 dBu | 20kHz BW | TYP | p2 | "Noise Floor, RTO(1) 20kHz BW –106 dBu" |
| 出力雑音電圧 | 3.5 µVrms（20 Hz〜20 kHz）／26 nV/√Hz（1 kHz） | — | TYP | p2 | "f = 20Hz to 20kHz 3.5 µVrms / f = 1kHz 26 nV/√HZ" |
| CMR | 74 / 90 dB | VCM = ±46.5V, RS = 0Ω | MIN / TYP | p2 | "Common-Mode Rejection VCM = ±46.5V, RS = 0Ω 74 90 dB" |
| CMR vs 周波数（RTO） | 約 90 dB（1 kHz〜約 90 kHz）、1 MHz で約 64 dB（目読み） | G = 1/2 | グラフ | p5（画像で確認） | "COMMON-MODE REJECTION vs FREQUENCY" / "RTO" |
| CMR と信号源不整合（本文） | 5 Ω の不整合で約 77 dB（RTO） | — | 本文 | p8 | "A 5Ω mismatch in source impedance will degrade the common-mode rejection of a typical device to approximately 77dB (RTO)." |
| THD+N vs 周波数 | VO = 5Vrms で約 0.0005 %（〜数 kHz）、20 kHz で約 0.001 %（目読み） | — | グラフ | p4 | "VO = 5Vrms" |
| 高調波成分 vs 周波数 | VO = 1Vrms の 2 次: 20 Hz で約 0.00017 %、1 kHz で約 0.00005 %（目読み） | — | グラフ | p4 | "HARMONIC DISTORTION PRODUCTS vs FREQUENCY" |
| 入力インピーダンス | 差動 24 kΩ、同相 18 kΩ | 注 (4) 比マッチ、絶対値 ±25 % | TYP | p2 | "Differential 24 kΩ / Common-Mode 18 kΩ" |
| 利得 | 0.5 V/V、誤差 ±0.01 / ±0.1 % | VO = –10V to 10V | TYP / MAX | p2 | "Initial 0.5 V/V / Error VO = –10V to 10V ±0.01 ±0.1 %" |
| 電源電圧範囲／静止電流 | ±4〜±18 V／±2.4 / ±2.9 mA（アンプ 1 個あたり） | IO = 0 | MIN・MAX／TYP・MAX | p2 | "Voltage Range ±4 ±18 V / Quiescent Current (per Amplifier) IO = 0 ±2.4 ±2.9 mA" |

## Q2-5. THAT 1200 / 1203 / 1206（InGenius 高 CMRR ライン・レシーバ）

出典: `THAT_1200.pdf`。表の既定条件（p2 注 2）: "Unless otherwise noted, TA = 25°C, VCC = +15V, VEE = -15V"。注 3: "See test circuit in Figure 2."。p2 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧 | ±3 / ±18 V | — | Min / Max | p2 | "Supply Voltage VCC, VEE ±3 ±18 V" |
| 電源電流 | 4.7 / 8.0 mA | No Signal | Typ / Max | p2 | "Supply Current ICC No Signal — 4.7 8.0 mA" |
| 入力インピーダンス | 差動 48.0 kΩ、同相（bootstrap 付き）10.0 MΩ @60 Hz／3.2 MΩ @20 kHz | — | Typ | p2（画像で確認） | "Differential 48.0 kΩ / Common mode with bootstrap 60 Hz 10.0 MΩ 20 kHz 3.2 MΩ" |
| CMRR1（整合した信号源） | DC 70/90、60 Hz 70/90、20 kHz —/85 dB | Matched source impedances; VCM = ±10V | Min / Typ | p2 | "CMRR1 Matched source impedances; VCM = ±10V DC 70 90 / 60 Hz 70 90 / 20 kHz — 85" |
| CMRR_IEC（10 Ω 不整合） | DC 90、60 Hz 90、20 kHz 85 dB | 10Ω unmatched source impedances; VCM = ±10V。注 5: IEC 60268-3 | Typ | p2 | "CMRRIEC 10Ω unmatched source impedances; VCM = ±10V ... 90 / 90 / 85" |
| CMRR2（600 Ω 不整合） | 60 Hz 70、20 kHz 65 dB | 600Ω unmatched source impedances; VCM = ±10V | Typ | p2 | "CMRR2 600Ω unmatched source impedances ... 60 Hz 70 / 20 kHz 65" |
| 入力電圧範囲 | 同相 ±12.5 / ±13.0 V、差動 THAT1200 21.0 / 21.5 dBu（1203/1206 は 24.0 / 24.5 dBu） | — | Min / Typ | p2 | "Common mode ±12.5 ±13.0 V / THAT 1200 21.0 21.5 dBu" |
| THD | 0.0005 % | VIN_DIFF = 10 dBu; BW = 20 kHz; f = 1 kHz, RL = 2 kΩ | Typ | p3 | "THD VIN_DIFF = 10 dBu; BW = 20 kHz; f = 1 kHz RL = 2 kΩ — 0.0005 — %" |
| 出力雑音 | 1200: −105、1203: −104、1206: −106 dBu | BW = 20 kHz | Typ | p3 | "Output Noise eN(OUT) BW = 20 kHz THAT1200 — -105" |
| 出力利得誤差 | 0 / ±0.05 dB | f = 1 kHz, RL = 2 kΩ | Typ / Max | p3 | "Output Gain Error GER(OUT) f = 1 kHz, RL = 2 kΩ — 0 ±0.05 dB" |
| PSRR | 1200: 82 dB | At 60 Hz, with VCC = -VEE | Typ | p2 | "At 60 Hz, with VCC = -VEE THAT 1200 — 82" |

## Q2-6. ADI SSM2141（差動ライン・レシーバ、G = 1）

出典: `ADI_SSM2141.pdf`（REV. C、ミラー）。表の条件（p2）: "@ VS = ±18 V, TA = +25°C, unless otherwise noted"（抽出では "618 V"。画像で ±18 V を確認）。p2〜p5 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| CMR | 80 / 100 dB（−40〜+85°C: 75 / 90） | VCM = ±10 V | Min / Typ | p2（画像で確認） | "COMMON-MODE REJECTION CMR VCM = ±10 V 80 100 dB" |
| CMR（Features） | DC 100、60 Hz 100、20 kHz 70、40 kHz 62 dB typ | — | 字句 "typ" | p1 | "DC: 100 dB typ / 60 Hz: 100 dB typ / 20 kHz: 70 dB typ / 40 kHz: 62 dB typ" |
| CMR vs 周波数 | 約 100 dB（〜1 kHz）、約 72 dB（20 kHz）、約 55 dB（100 kHz）（目読み） | TA = 25°C, VS = ±15V | グラフ | p3（画像で確認） | "Common-Mode Rejection vs. Frequency" |
| CMR と信号源不整合（本文） | 5 Ω の不整合で DC CMR が 20 dB 劣化 | — | 本文 | p6 | "even a 5 Ω imbalance will degrade CMR by 20 dB" |
| THD | 0.001 %（RL = 100 kΩ）、0.01 %（RL = 600 Ω） | 振幅・周波数・帯域の記載なし | Typ | p2 | "TOTAL HARMONIC DISTORTION RL = 100 kΩ 0.001 / THD RL = 600 Ω 0.01 %" |
| THD+N vs 周波数 | RL = 100 kΩ: 20 Hz〜約 1 kHz で約 0.001 %、20 kHz で約 0.002 %。RL = 600 Ω: 20 kHz で約 0.01 %（目読み。振幅・帯域の記載なし） | TA = +25°C, VS = ±15V, AV = −1 | グラフ（Audio Precision 画面） | p3 | "Total Harmonic Distortion vs. Frequency" |
| 電圧雑音密度 | 約 22 nV/√Hz（約 200 Hz 以上）（目読み。RTI/RTO の記載なし） | TA = +25°C, VS = ±15V | グラフ | p5（画像で確認） | "Voltage Noise Density vs. Frequency" |
| 利得誤差 | 0.001 / 0.01 % | No Load, VIN = ±10 V, RS = 0 Ω | Typ / Max | p2 | "GAIN ERROR No Load, VIN = ±10 V, RS = 0 Ω 0.001 0.01 %" |
| 電源電流 | 2.5 / 3.5 mA | No Load | Typ / Max | p2 | "SUPPLY CURRENT ISY No Load 2.5 3.5 mA" |
| 電源電圧（絶対最大） | ±18 V | — | — | p3 | "Supply Voltage ... ±18 V" |
| 内部抵抗（ブロック図） | 25 kΩ × 4 | — | 図の記載 | p1 | "25kΩ 25kΩ"（入力インピーダンスの表の値は無い） |

## Q2-7. ADI SSM2143（差動ライン・レシーバ、G = 1/2 または 2）

出典: `ADI_SSM2143.pdf`（REV. 0、ミラー）。表の条件（p2）: "(VS = ±15 V, –40°C ≤ TA ≤ +85°C, G = 1/2, unless otherwise noted. Typical specifications apply at TA = +25°C)"。p2〜p5 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| THD+N | 0.0006 % | VIN = 10 V rms, RL = 10 kΩ, f = 1 kHz | Typ | p2（画像で確認） | "THD+N VIN = 10 V rms, RL = 10 kΩ, f = 1 kHz 0.0006 %" |
| SNR | −107.3 dBu | 0 dBu = 0.775 V rms, 20 kHz BW, RTI | Typ | p2 | "Signal-to-Noise Ratio SNR 0 dBu = 0.775 V rms, 20 kHz BW, RTI –107.3 dBu" |
| THD+N vs 周波数 | 20 Hz で約 0.0008 %、100 Hz〜2 kHz で約 0.0006 %、20 kHz で約 0.002〜0.004 %（2 本の線）（目読み） | VS = ±15 V, VIN = 10 V rms, with 80 kHz Filter | グラフ | p3 Figure 3（画像で確認） | "Figure 3. THD+N vs. Frequency (VS = ±15 V, VIN = 10 V rms, with 80 kHz Filter)" |
| CMR | dc 70 / 90、60 Hz 90、20 kHz 85、400 kHz 60 dB | VCM = ±10 V, RTO | Min / Typ | p2 | "CMR VCM = ±10 V, RTO f = dc 70 90 / f = 60 Hz 90 / f = 20 kHz 85 / f = 400 kHz 60" |
| CMR vs 周波数 | 約 88 dB（〜10 kHz）、約 70 dB（100 kHz）（目読み） | VS = ±15V, TA = +25°C | グラフ | p4 Figure 10 | "Figure 10. Common-Mode Rejection vs. Frequency" |
| CMR と信号源不整合（本文） | 5 Ω の不整合で dc CMRR 71 dB | — | 本文 | p6 | "a 5 Ω source imbalance will result in a CMRR of 71 dB at dc" |
| 電圧雑音密度 | 約 14 nV/√Hz（1 kHz）（目読み） | VS = ±15V, TA = +25°C | グラフ | p5 Figure 16（画像で確認） | "Figure 16. Voltage Noise Density vs. Frequency" |
| 入力電圧範囲 | 同相 ±15 V、差動 ±28 V | — | Typ | p2 | "Input Voltage Range IVR Common Mode ±15 / Differential ±28 V" |
| 利得精度 | −0.1 / 0.03 / 0.1 % | — | Min / Typ / Max | p2 | "Gain Accuracy –0.1 0.03 0.1 %" |
| 電源 | ±6〜±18 V、電流 ±2.7 / ±4.0 mA | VCM = 0 V, RL = ∞ | Min・Max／Typ・Max | p2 | "Supply Voltage Range ±6 ±18 V / Supply Current VCM = 0 V, RL = ∞ ±2.7 ±4.0 mA" |
| 内部抵抗（ブロック図） | 12 kΩ / 6 kΩ | — | 図の記載 | p1 | "12k Ω 6k Ω"（入力インピーダンスの表の値は無い。REFERENCE 入力抵抗は 18 kΩ typ） |

## Q2-8. ADI AD8274（低歪み精密差動アンプ、G = 1/2 または 2）

出典: `ADI_AD8274.pdf`（Rev. C、ミラー）。表の条件（PDF p4＝印刷 p3）: "VS = ±15 V, VREF = 0 V, TA = 25°C, RL = 2 kΩ, unless otherwise noted."。PDF p4・p8・p11・p12 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源範囲（Features） | ±2.5 V〜±18 V | — | — | PDF p1 | "Supply range: ±2.5 V to ±18 V" |
| THD + Noise | G = ½: 0.00025 %、G = 2: 0.00035 % | f = 1 kHz, VOUT = 10 V p-p, 600 Ω load | Typ（各 G の列） | PDF p4 Table 2（画像で確認） | "THD + Noise f = 1 kHz, VOUT = 10 V p-p, 600 Ω load 0.00025 ... 0.00035 %" |
| Noise Floor, RTO | G = ½: −106、G = 2: −100 dBu | 20 kHz BW | Typ | PDF p4 | "Noise Floor, RTO2 20 kHz BW −106 −100 dBu" |
| 出力電圧雑音（RTO） | G = ½: 3.5 µV rms（20 Hz〜20 kHz）・26 nV/√Hz（1 kHz）。G = 2: 7 µV rms・52 nV/√Hz | 注 1: アンプの電圧・電流雑音と内部抵抗の雑音を含む | Typ | PDF p4 | "Output Voltage Noise (Referred to Output) f = 20 Hz to 20 kHz 3.5 7 µV rms / f = 1 kHz 26 52 nV/√Hz" |
| CMRR | G = ½: 77 / 86 dB、G = 2: 83 / 92 dB | VCM = ±40 V, RS = 0 Ω, referred to input | Min / Typ | PDF p4 | "Common-Mode Rejection Ratio VCM = ±40 V, RS = 0 Ω, referred to input 77 86 83 92 dB" |
| CMRR vs 周波数（入力換算） | G = ½: 約 94 dB（〜約 15 kHz）、100 kHz で約 80 dB。G = 2: 約 100 dB（〜約 15 kHz）（目読み） | — | グラフ | PDF p8 Figure 15（画像で確認） | "Figure 15. Common-Mode Rejection Ratio vs. Frequency, Referred to Input" |
| THD + N vs 周波数（22 kHz フィルタ） | 20 Hz〜20 kHz で G = ½ 約 0.00025 %、G = 2 約 0.00035 %（目読み） | 22kHz FILTER, VOUT = 10V p-p, RL = 600Ω | グラフ | PDF p11 Figure 32（画像で確認） | "Figure 32. THD + N vs. Frequency, Filter = 22k Hz" |
| 高調波成分 vs 周波数（G = ½） | 3 次（全負荷）約 0.00025 %、2 次（600 Ω）約 0.00005 %、2 次（100 kΩ/2 kΩ）約 0.00002 %（20 Hz〜10 kHz、目読み） | GAIN = ½, VOUT = 10V p-p | グラフ | PDF p12 Figure 36（画像で確認） | "Figure 36. Harmonic Distortion Products vs. Frequency, G = ½" |
| 入力インピーダンス | G = ½: 差動 36 kΩ・同相 9 kΩ、G = 2: 差動 9 kΩ・同相 9 kΩ | VCM = 0 V。注 6: 片側入力だけの同相インピーダンスは 18 kΩ。注 5: 抵抗は比マッチ、絶対精度 ±20 % | Typ | PDF p4 | "Differential VCM = 0 V 36 9 kΩ / Common Mode6 9 9 kΩ" / "6 ... The common-mode impedance at only one input is 18 kΩ." |
| 利得誤差／非直線性 | 0.03 %（max）／2 ppm | 非直線性: VOUT = 10 V p-p, 600 Ω load | Max／Typ | PDF p4 | "Gain Error 0.03 0.03 % / Gain Nonlinearity VOUT = 10 V p-p, 600 Ω load 2 2 ppm" |
| 電源電流（アンプ 1 個あたり） | 2.3 / 2.6 mA | — | Typ / Max | PDF p4 | "Supply Current (per Amplifier) 2.3 2.6 mA" |

### Q2 で探したが DS に無かった項目

- INA1620: **内蔵抵抗で差動アンプを組んだときの CMRR**（表の CMRR はオペアンプ単体。抵抗ペアのマッチングだけ規定）
- INA134 / INA137: THD+N の**測定帯域**（表・グラフとも記載なし）
- SSM2141: THD の振幅・周波数・測定帯域、**入力インピーダンス**（ブロック図の 25 kΩ のみ）、雑音密度の表の値（グラフのみ）
- SSM2143: 差動・同相の入力インピーダンスの表の値（ブロック図の 12 k/6 k のみ）
- THAT 1200: 雑音密度、CMRR・THD の周波数特性グラフ
- どの DS にも、**20〜50 Hz・7〜9 Vpk 相当での THD の規定値は無い**（グラフで読めるのは INA1620 Fig 14、INA1650 Fig 12、INA134/137、SSM2143 Fig 3、AD8274 Fig 32/36）

---

# Q3 アイソレーション・アンプ

## Q3-1. TI AMC1311 / AMC1311B（2 V 入力、高入力インピーダンス）

出典: `TI_AMC1311.pdf`。EC の条件（p10）: "minimum and maximum specifications of the AMC1311 apply from TA = –40°C to +125°C, VDD1 = 4.5 V to 5.5 V, VDD2 = 3.0 V to 5.5 V, VIN = –0.1 V to 2 V, and SHTDN = GND1 = 0 V; ... typical specifications are at TA = 25°C, VDD1 = 5 V, and VDD2 = 3.3 V"。p10 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 高圧側電源 VDD1 | AMC1311: 4.5 / 5 / 5.5 V、AMC1311B: 3 / 5 / 5.5 V | VDD1 to GND1 | MIN / NOM / MAX | p6 §7.3 | "VDD1 to GND1, AMC1311 4.5 5 5.5 / AMC1311B 3 5 5.5" |
| 低圧側電源 VDD2 | 3 / 3.3 / 5.5 V | — | MIN / NOM / MAX | p6 | "Low-side power supply VDD2 to GND2 3 3.3 5.5 V" |
| 線形入力範囲 VFSR | −0.1〜2 V | IN to GND1 | MIN / MAX | p6 | "VFSR Specified linear full-scale voltage IN to GND1 –0.1 2 V" |
| クリップ前入力 | 2.516 V | — | NOM | p6 | "VClipping Input voltage before clipping output IN to GND1 2.516 V" |
| 入力抵抗 | 1 GΩ | TA = 25℃ | TYP | p10 | "RIN Input resistance TA = 25℃ 1 GΩ" |
| 利得／利得誤差 | 1 V/V／AMC1311: −1 / 0.4 / 1 %、AMC1311B: −0.2 / ±0.05 / 0.2 % | TA = 25℃ | MIN / TYP / MAX | p10（画像で確認） | "EG Gain error(1) TA = 25℃, AMC1311 –1% 0.4% 1%" |
| 非直線性 | −0.04 / ±0.01 / 0.04 % | — | MIN / TYP / MAX | p10 | "Nonlineartity(1) –0.04% ±0.01% 0.04%"（原文の綴りのまま） |
| THD | −87 dB | VIN = 2 VPP, VIN > 0 V, fIN = 10 kHz, BW = 10 kHz。注 4: 最初の 5 つの高調波 | TYP | p10 | "THD Total harmonic distortion(4) VIN = 2 VPP, VIN > 0 V, fIN = 10 kHz, BW = 10 kHz –87 dB" |
| SNR | 79 / 82.6 dB | VIN = 2 VPP, fIN = 1 kHz, BW = 10 kHz | MIN / TYP | p10 | "VIN = 2 VPP, fIN = 1 kHz, BW = 10 kHz 79 82.6" |
| SNR | 70.9 dB | VIN = 2 VPP, fIN = 10 kHz, BW = 100 kHz | TYP | p10 | "VIN = 2 VPP, fIN = 10 kHz, BW = 100 kHz 70.9" |
| 出力雑音 | 220 µVrms | VIN = GND1, BW = 100 kHz | TYP | p10 | "Output noise VIN = GND1, BW = 100 kHz 220 µVrms" |
| 入力換算雑音密度 | 約 0.5 µV/√Hz（0.1〜30 kHz）、100 kHz 超で上昇（目読み） | VDD1 = 5 V, VDD2 = 3.3 V, fIN = 10 kHz, BW = 100 kHz | グラフ | p17 Figure 7-23（画像で確認） | "Figure 7-23. Input-Referred Noise Density vs Frequency" |
| THD vs 電源電圧 | 約 −85〜−88 dB（目読み） | 同上 | グラフ | p16 Figure 7-21 | "Figure 7-21. Total Harmonic Distortion vs Supply Voltage" |
| 出力帯域 | AMC1311: 100 / 220 kHz、AMC1311B: 220 / 275 kHz | — | MIN / TYP | p10 | "BW Output bandwidth AMC1311 100 220 / AMC1311B 220 275 kHz" |
| バリア容量 CIO | ~1.5 pF | VIO = 0.5 VPP at 1 MHz | 値の列のみ | p8 §7.6 | "CIO Barrier capacitance, VIO = 0.5 VPP at 1 MHz ~1.5 pF" |
| 高圧側電流 IDD1 | 7.1 / 9.7 mA | 4.5 V < VDD1 < 5.5 V, SHTDN = low | TYP / MAX | p11 | "4.5 V < VDD1 < 5.5 V, SHTDN = low 7.1 9.7" |
| 低圧側電流 IDD2 | 5.3 / 7.2 mA（3.0〜3.6 V）、5.9 / 8.1 mA（4.5〜5.5 V） | — | TYP / MAX | p11 | "3.0 V < VDD2 < 3.6 V 5.3 7.2 / 4.5 V < VDD2 < 5.5 V 5.9 8.1" |
| 高圧側電源の作り方（本文） | 高圧側の接地基準電源か、VDD2 から絶縁 DC/DC（SN6501＋トランスの例）で作る | — | 本文 | p27 | "Alternatively, the high-side supply can be generated from the low-side supply (VDD2) by an isolated DC/DC converter." |
| 内部の周波数（本文） | 内部 ΔΣ 変調器のサンプリング 20 MHz、バリアを渡る搬送波 480 MHz | — | 本文 | p25, p21 | "(20 MHz) of the internal ΔΣ modulator" / "The nominal frequency of the carrier used inside the AMC1311 is 480 MHz." |

## Q3-2. TI AMC1300 / AMC1300B（±250 mV 入力、利得 8.2）

出典: `TI_AMC1300.pdf`。EC の条件（p9）: "... VDD1 = 4.5 V to 5.5 V, VDD2 = 3.0 V to 5.5 V, INP = – 250 mV to + 250 mV, and INN = GND1; ... typical specifications are at TA = 25°C, VDD1 = 5 V, and VDD2 = 3.3 V"。p9 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 線形入力範囲 VFSR | −250〜250 mV（差動） | VIN = VINP - VINN | MIN / MAX | p5 §7.3 | "VFSR Specified linear differential full-scale voltage –250 250 mV" |
| 動作同相入力 | −0.16〜VDD1 – 2.1 V | (VINP+VINN) / 2 to GND1 | MIN / MAX | p5 | "VCM Operating common-mode input voltage –0.16 VDD1 – 2.1 V" |
| 入力抵抗 | 片側 19 kΩ、差動 22 kΩ | — | TYP | p9 | "RIN Single-ended input resistance INN = GND1 19 / RIND Differential input resistance 22 kΩ" |
| 利得／誤差 | 8.2／AMC1300: −1 / 0.4 / 1 %、AMC1300B: −0.3 / ±0.05 / 0.3 % | initial, at TA = 25°C | MIN / TYP / MAX | p9（画像で確認） | "Nominal gain 8.2 / AMC1300, initial, at TA = 25°C –1% 0.4% 1%" |
| 非直線性 | −0.03 / ±0.01 / 0.03 % | — | MIN / TYP / MAX | p9 | "Nonlinearity(1) –0.03 ±0.01 0.03 %" |
| THD | −85 dB | fIN = 10 kHz（振幅は表の既定条件） | TYP | p9 | "THD Total harmonic distortion(3) fIN = 10 kHz –85 dB" |
| SNR | 81.5 / 85 dB（fIN = 1 kHz, BW = 10 kHz）、72 dB（fIN = 10 kHz, BW = 100 kHz） | — | MIN / TYP | p9 | "fIN = 1 kHz, BW = 10 kHz 81.5 85 / fIN = 10 kHz, BW = 100 kHz 72" |
| 出力雑音 | 230 µVRMS | INP = INN = GND1, fIN = 0 Hz, BW = 100 kHz brickwall filter | TYP | p9 | "Output noise ... BW = 100 kHz brickwall filter 230 µVRMS" |
| 入力換算雑音密度 | 約 70（軸ラベルは原文どおり µV/√Hz）、100 kHz 超で上昇（目読み） | VDD1 = 5 V, VDD2 = 3.3 V | グラフ | p16 Figure 7-26（画像で確認） | "Figure 7-26. Input-Referred Noise Density vs Frequency" / 軸 "Noise Density (µV/√Hz)" |
| CMRR | −100 dB（0 Hz）、−98 dB（10 kHz） | VCM min ≤ VCM ≤ VCM max | TYP | p9 | "CMRR fIN = 0 Hz ... –100 / fIN = 10 kHz ... –98 dB" |
| 出力帯域 | AMC1300: 170 / 230 kHz、AMC1300B: 250 / 310 kHz | — | MIN / TYP | p10 | "BWOUT Output bandwidth AMC1300 170 230 / AMC1300B 250 310 kHz" |
| バリア容量 CIO | ~1.5 pF | VIO = 0.4 × sin (2πft), f = 1 MHz | 値の列のみ | p7 | "CIO Barrier capacitance, input to output(4) VIO = 0.4 × sin (2 πft), f = 1 MHz ~1.5 pF" |
| 電源電流 | IDD1 7.2 / 9.8 mA（4.5〜5.5 V）、IDD2 5.3 / 7.2 mA（3.0〜3.6 V） | — | TYP / MAX | p10 | "4.5 V ≤ VDD1 ≤ 5.5 V 7.2 9.8 / 3.0 V ≤ VDD2 ≤ 3.6 V 5.3 7.2" |
| 高圧側電源 | 高圧側電源 VDD1（3.3 V または 5 V）が別に要る（p1 のブロック図 "High-side supply (3.3 V or 5 V)"） | — | 図の記載 | p1 | "High-side supply (3.3 V or 5 V)" |
| 搬送波（本文） | 480 MHz | — | 本文 | p21 | "carrier used inside the AMC1300 is 480 MHz." |

## Q3-3. TI ISO224A / ISO224B（±12 V 単端入力）

出典: `TI_ISO224.pdf`。EC の条件（p7, p8）: "minimum and maximum specifications apply from TA = –55°C to +125°C, VDD1 = 4.5 V to 18 V, VDD2 = 4.5 V to 5.5 V, VIN = –12 V to 12 V, and RLOAD = 10 kΩ; typical specifications are at TA = 25°C, and VDD1 = VDD2 = 5 V"。p8 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 高圧側電源 VDD1 | 4.5 / 5 / 18 V | VDD1 to GND1 | MIN / NOM / MAX | p4 §7.3 | "High-side power supply VDD1 to GND1 4.5 5 18 V" |
| 低圧側電源 VDD2 | 4.5 / 5 / 5.5 V | — | MIN / NOM / MAX | p4 | "Low-side power supply VDD2 to GND2 4.5 5 5.5 V" |
| 線形入力範囲 VFSR | −12〜12 V | IN to GND1 | MIN / MAX | p4 | "VFSR Specified linear input full-scale voltage (1) IN to GND1 –12 12 V" |
| クリップ前入力 | ±13.8 V | — | NOM | p4 | "VClipping Input voltage before clipping output (1) IN to GND1 ±13.8 V" |
| 入力抵抗 | 1 / 1.25 MΩ | IN to GND1 | MIN / TYP | p7 | "RIN Input resistance IN to GND1 1 1.25 MΩ" |
| 入力換算雑音密度 | ISO224B: 3、ISO224A: 4 µV/√Hz | — | TYP | p7 | "Input-referred noise density ISO224B 3 / ISO224A 4 µV/√Hz" |
| 利得 | 1/3 V/V | (VOUTP – VOUTN) / VIN | TYP | p8（画像で確認） | "Nominal gain (VOUTP – VOUTN) / VIN 1/3 V/V" |
| 利得誤差 | ISO224B: −0.3 / ±0.05 / 0.3 %、ISO224A: −1 / 0.4 / 1 % | Initial, at TA = 25°C | MIN / TYP / MAX | p8 | "Initial, at TA = 25°C, ISO224B –0.3% ±0.05% 0.3%" |
| 非直線性 | ISO224B: −0.01 / ±0.003 / 0.01 %、ISO224A: −0.02 / ±0.003 / 0.02 % | — | MIN / TYP / MAX | p8 | "Nonlinearity ISO224B –0.01% ±0.003% 0.01%" |
| THD | −84 dB | fIN = 10 kHz（振幅は表の既定条件 VIN = –12 V to 12 V） | TYP | p8 | "THD Total harmonic distortion fIN = 10 kHz –84 dB" |
| THD vs 電源電圧・温度 | VDD1 に対して約 −84 dB 一定、VDD2 = 4.5 V で約 −93 dB〜5.5 V で約 −81 dB（目読み） | TA = 25°C, VDD1 = VDD2 = 5 V, VINP = –12 V to 12 V | グラフ | p14 Figure 26, 27（画像で確認） | "Figure 27. Total Harmonic Distortion vs Low-Side Supply Voltage" |
| 出力雑音 | 300 µVRMS（BW = 10 kHz）、360 µVRMS（BW = 100 kHz） | IN = GND1, fIN = 0 Hz | TYP | p8 | "IN = GND1, fIN = 0 Hz, BW = 10 kHz 300 / BW = 100 kHz 360 µVRMS" |
| 小信号出力帯域 | ISO224B: 220 / 275 kHz、ISO224A: 150 / 185 kHz | — | MIN / TYP | p8 | "Small signal output bandwidth ISO224B 220 275 / ISO224A 150 185 kHz" |
| バリア容量 CIO | ~1 pF | VIO = 0.5 VPP at 1 MHz | 値の列のみ | p6 | "CIO VIO = 0.5 VPP at 1 MHz ~1 pF" |
| 電源電流 | IDD1 6.1 / 7.8 mA、IDD2 7.8 / 9.9 mA | — | TYP / MAX | p8 | "IDD1 High-side supply current 6.1 7.8 mA / IDD2 Low-side supply current 7.8 9.9 mA" |
| 高圧側電源の作り方（本文） | VDD1 は VDD2 から絶縁 DC/DC（SN6501＋トランス）で作るのが典型 | — | 本文 | p25 | "In a typical application, the high-side power supply (VDD1) for the ISO224 is generated from the low-side supply (VDD2) of the device by an isolated DC/DC converter circuit." |
| SNR | — | — | — | — | DS に無い |

## Q3-4. TI AMC3330（±1 V 入力、絶縁 DC/DC 内蔵）

出典: `TI_AMC3330.pdf`。EC の条件（p8, p9）: "minimum and maximum specifications apply from TA = –40°C to +125°C, VDD = 3.0 V to 5.5 V, INP = –1 V to +1 V, and INN = HGND = 0 V; typical specifications are at TA = 25°C, and VDD = 3.3 V"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | 低圧側 VDD 3.0 / 3.3 / 5.5 V のみ（高圧側は内蔵 DC/DC） | VDD to GND | MIN / NOM / MAX | p4 §5.3 | "VDD Low-side supply voltage VDD to GND 3.0 3.3 5.5 V" |
| 線形入力範囲 VFSR | −1〜1 V（差動）、クリップ前 ±1.25 V | VIN = VINP – VINN | MIN / MAX（クリップは NOM） | p4 | "VFSR Specified linear differential full-scale voltage –1 1 V" |
| 動作同相入力 | −1.4〜1.6 V（VINP = VINN）、−0.925〜0.725 V（\|VINP – VINN\| = 1.0 V） | (VINP + VINN) / 2 to HGND | MIN / MAX | p4 | "VINP = VINN –1.4 1.6 / |VINP – VINN| = 1.0 V (2) –0.925 0.725 V" |
| 入力抵抗 | 片側 0.1 / 0.8 GΩ、差動 0.1 / 1.2 GΩ | — | MIN / TYP | p8 | "RIN Single-ended input resistance INN = HGND 0.1 0.8 / RIND Differential input resistance 0.1 1.2 GΩ" |
| 利得／誤差 | 2 V/V／−0.2 / −0.08 / 0.2 % | TA = 25°C | MIN / TYP / MAX | p8 | "Nominal gain 2 V/V / EG Gain error TA = 25°C –0.2% –0.08% 0.2%" |
| 非直線性 | −0.02 / 0.01 / 0.02 % | — | MIN / TYP / MAX | p8 | "Nonlinearity –0.02% 0.01% 0.02%" |
| SNR | 81 / 85 dB | VIN = 2 VPP, fIN = 1 kHz, BW = 10 kHz, 10 kHz filter | MIN / TYP | p8 | "VIN = 2 VPP, fIN = 1 kHz, BW = 10 kHz, 10 kHz filter 81 85" |
| SNR | 72 dB | VIN = 2 VPP, fIN = 10 kHz, BW = 100 kHz, 1 MHz filter | TYP | p8 | "VIN = 2 VPP, fIN = 10 kHz, BW = 100 kHz, 1 MHz filter 72" |
| THD | −84 dB | VIN = 2 Vpp, fIN = 10 kHz, BW = 100 kHz | TYP | p8 | "THD Total harmonic distortion(3) VIN = 2 Vpp, fIN = 10 kHz, BW = 100 kHz –84 dB" |
| 出力雑音 | 250 µVRMS | INP = INN = HGND, fIN = 0 Hz, BW = 100 kHz | TYP | p8 | "Output noise ... BW = 100 kHz 250 µVRMS" |
| 入力換算雑音密度 | 約 300 nV/√Hz（0.01〜約 30 kHz）、それより上で上昇（目読み） | VDD = 3.3 V | グラフ | p16 Figure 5-29（画像で確認） | "Figure 5-29. Input-Referred Noise Density vs Frequency" |
| CMRR | −100 dB（0 Hz）、−86 dB（10 kHz） | VCM min ≤ VCM ≤ VCM max | TYP | p8 | "CMRR fIN = 0 Hz ... –100 / fIN = 10 kHz ... –86 dB" |
| CMRR vs 周波数 | 約 −102 dB（〜1 kHz）、10 kHz で約 −85 dB（目読み） | — | グラフ | p16 Figure 5-30（画像で確認） | "Figure 5-30. Common-Mode Rejection Ratio vs Input Frequency" |
| 出力帯域 | 300 / 375 kHz | — | MIN / TYP | p8 | "BWOUT Output bandwidth 300 375 kHz" |
| バリア容量 CIO | ~4.5 pF | VIO = 0.5 VPP at 1MHz | 値の列のみ | p6 | "CIO VIO = 0.5 VPP at 1MHz ~4.5 pF" |
| 電源電流 IDD | 28.5 / 41 mA（HLDO 無負荷）、30.5 / 43 mA（HLDO 1 mA 負荷） | — | TYP / MAX | p9 | "IDD Low-side supply current No external load on HLDO 28.5 41 mA" |
| 補助回路に取れる電流 IH | 1 mA（3 V ≤ VDD < 4.5 V）、4.3 mA（4.5 V ≤ VDD ≤ 5.5 V） | load connected from HLDO_OUT to HGND, non-switching | MAX | p9 | "IH High-side supply current for auxiliary circuitry ... 1 / ... 4.3 mA" |
| DC/DC の方式（本文） | spread-spectrum、共振器の周波数は ΔΣ 変調器に同期。**周波数の数値は無い** | — | 本文 | p22 §6.3.4 | "The DC/DC converter uses a spread-spectrum clock generation technique to reduce the spectral density of the electromagnetic radiation. The resonator frequency is synchronous to the operation of the ΔΣ modulator" |
| EMI（Features） | CISPR-11 と CISPR-25 に適合 | — | — | p1 | "Meets CISPR-11 and CISPR-25 EMI standards" |
| 搬送波（本文） | 480 MHz | — | 本文 | p19 | "an internally generated, 480-MHz carrier" |

## Q3-5. TI AMC3336（±1 V 入力の絶縁 ΔΣ **変調器**、DC/DC 内蔵。出力はビットストリーム）

出典: `TI_AMC3336.pdf`。EC の条件（p8）: "all minimum and maximum specifications are at TA = –40°C to 125°C, VDD = 3.0 V to 5.5 V, INP = –1 V to +1 V, INN = 0 V, and sinc3 filter with OSR = 256 (unless otherwise noted); typical values are at TA = 25°C, CLKIN = 20 MHz, VDD = 3.3 V"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力形式 | ΔΣ 変調器（外部クロック CLKIN、DOUT ビットストリーム） | — | 本文 | p1 | "The AMC3336 is a precision, isolated delta-sigma (ΔΣ) modulator" |
| 入力クロック | 9 / 20 / 21 MHz | — | MIN / NOM / MAX | p4 §6.3 | "fCLKIN Input clock frequency 9 20 21 MHz" |
| 線形入力範囲 VFSR | −1〜1 V（差動） | — | MIN / MAX | p4 | "VFSR Specified linear differential full-scale voltage –1 1 V" |
| 入力抵抗 | 0.06 / 1 GΩ（片側・差動とも） | — | MIN / TYP | p8 | "RIN Single-ended input resistance INN = HGND 0.06 1 GΩ" |
| SNR | 80 / 84 dB | fIN = 1 kHz（sinc3, OSR = 256） | MIN / TYP | p8 | "SNR Signal-to-noise ratio fIN = 1 kHz 80 84 dB" |
| SINAD | 77 / 84 dB | fIN = 1 kHz | MIN / TYP | p8 | "SINAD Signal-to-noise + distortion fIN = 1 kHz 77 84 dB" |
| THD | −93 / −80 dB | VIN = 2 VPP, fIN = 1 kHz | TYP / MAX | p8 | "THD Total harmonic distortion(3) VIN = 2 VPP, fIN = 1 kHz –93 –80 dB" |
| SFDR | 79 / 96 dB | VIN = 2 VPP, fIN = 1 kHz | MIN / TYP | p8 | "SFDR Spurious-free dynamic range VIN = 2 VPP, fIN = 1 kHz 79 96 dB" |
| SNR・SINAD vs 入力周波数 | SNR 約 84 dB（10 Hz〜約 3 kHz）、SINAD 約 83.5 dB（〜1 kHz）→10 kHz で約 80.5 dB（目読み） | sinc3, OSR = 256, 16-bit | グラフ | p14 Figure 6-20（画像で確認） | "Figure 6-20. Signal-to-Noise Ratio and Signal-to-Noise + Distortion vs Input Signal Frequency" |
| 雑音密度 | 約 1〜2 × 10² nVrms/√Hz（0.1〜約 30 kHz）、それより上で上昇（目読み） | sinc3, OSR = 1; Frequency bin-width equals 1 Hz、入力を HGND に短絡 | グラフ | p16 Figure 6-34（画像で確認） | "Figure 6-34. Noise Density With Both Inputs Shorted to HGND" |
| INL | 差動 −4〜4 LSB、単端 −6〜6 LSB | Resolution: 16 bits | MIN / MAX | p8 | "INL Integral nonlinearity Differential measurement; Resolution: 16 bits –4 4" |
| 利得誤差 | −0.2〜0.2 % | TA = 25°C | MIN / MAX | p8 | "EG Gain error TA = 25°C –0.2% 0.2%" |
| CMRR | −104 dB（0 Hz）、−89 dB（10 kHz, –0.5 V ≤ VIN ≤ 0.5 V） | INP = INN | TYP | p8 | "CMRR ... fIN = 0 Hz ... –104 / fIN = 10 kHz, –0.5 V ≤ VIN ≤ 0.5 V –89 dB" |
| バリア容量 CIO | ~4.5 pF | VIO = 0.5 VPP at 1 MHz | 値の列のみ | p6 | "CIO VIO = 0.5 VPP at 1 MHz ~4.5 pF" |
| 電源電流 IDD | 28.5 / 42.5 mA（HLDO 無負荷）、30.5 / 44.5 mA（1 mA 負荷） | — | TYP / MAX | p9 | "IDD Low-side supply current no external load on HLDO 28.5 42.5" |
| DC/DC の方式（本文） | spread-spectrum、共振器は ΔΣ 変調器に同期。**周波数の数値は無い** | — | 本文 | p23 | "The DC/DC converter uses a spread-spectrum clock generation technique ... The resonator frequency is synchronized to the operation of the ΔΣ modulator" |
| 搬送波（本文） | 480 MHz | — | 本文 | p21 | "carrier used inside the AMC3336 is 480 MHz." |

## Q3-6. ADI AD215（変調搬送波＋トランス結合、±15 V 絶縁電源出力つき）

出典: `ADI_AD215.pdf`（REV. 0、Farnell ミラー）。表の条件（PDF p3＝印刷 −2−）: "(Typical @ +25°C, VS = ±15 V dc, 2 kΩ output load, unless otherwise noted.)"（抽出では "2 kV"。画像で kΩ を確認）。PDF p3 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧 | ±14.5 / ±15 / ±16.5 V dc（Rated Performance）、動作 ±14.25〜±17 V dc | — | Min / Typ / Max | PDF p4（印刷 −3−） | "Supply Voltage Rated Performance ± 14.5 ± 15 ± 16.5 V dc / Operating10 ± 14.25 ± 17 V dc" |
| 電源電流 | +40 / −18 mA | Operating (+15 V dc/–15 V dc Supplies) | Typ | PDF p4 | "Current Operating (+15 V dc/–15 V dc Supplies) +40/–18 mA" |
| 入力電圧範囲 | ±10 V（min） | G = 1 V/V | Min | PDF p3（画像で確認） | "Input Voltage Rating G = 1 V/V ± 10 V" |
| 利得範囲／誤差 | 1〜10 V/V／±0.5 / ±2 % | G = 1 V/V, No Load on VISO | Min・Max／Typ・Max | PDF p3 | "Error G = 1 V/V, No Load on VISO ± 0.5 ±2 %" |
| 非直線性 | BY: ±0.005 / ±0.015 %、AY: ±0.01 / ±0.025 %（G = 1） | ± 10 V Output Swing, G = 1 V/V | Typ / Max | PDF p3 | "AD215BY Grade ± 10 V Output Swing, G = 1 V/V ± 0.005 ± 0.015 %" |
| 高調波成分 | −80 dB @1 kHz、−65 dB @10 kHz | 2 kΩ Load | Typ | PDF p4 | "Harmonic Distortion Components @ 1 kHz –80 dB / @ 10 kHz –65 dB" |
| 入力電圧雑音 | 20 nV/√Hz | Frequency > 10 Hz | Typ | PDF p3 | "Input Voltage Noise Frequency > 10 Hz 20 nV/√Hz" |
| 出力リップル＆雑音 | 10 mV pk-pk（1 MHz BW）、2.5 mV pk-pk（50 kHz BW） | 注 7: ±15 V を 2.2 µF でバイパス | Typ | PDF p4 | "Output Ripple and Noise7 1 MHz Bandwidth 10 / 50 kHz Bandwidth 2.5 mV pk-pk" |
| 帯域 | 100 / 120 kHz | G = 1 V/V, 20 V pk-pk Signal | Min / Typ | PDF p3 | "Full Signal Bandwidth (–3 dB) G = 1 V/V, 20 V pk-pk Signal 100 120 kHz" |
| IMRR | RS ≤ 100 Ω: 120 dB（60 Hz）/ 100 dB（1 kHz）/ 80 dB（10 kHz）。RS ≤ 1 kΩ: 105 / 85 / 65 dB | G = 1 V/V | Typ | PDF p3 | "IMRR (Isolation Mode Rejection Ratio) RS ≤ 100 Ω (IN+ & IN–), G = 1 V/V, 60 Hz 120 dB" |
| 同相入力インピーダンス | 2 ‖ 4.5 GΩ ‖ pF | — | Typ | PDF p3 | "Common Mode 2i4.5 GΩipF"（画像で 2‖4.5） |
| 同相容量（本文） | 4.5 pF（dc/dc 電源の絶縁を含む） | — | 本文 | PDF p1 | "Both grades feature a low common-mode capacitance of 4.5 pF inclusive of the dc/dc power isolation." |
| 絶縁側電源（出力） | ±15 V（±14.25 / ±15 / ±17.25 V、無負荷）、±10 mA | — | Min / Typ / Max | PDF p4 | "ISOLATED POWER OUTPUT8 Voltage No Load ± 14.25 ± 15 ± 17.25 V / Current at Rated Supply Voltage2, 9 ± 10 mA" |
| 絶縁側電源のリップル | 50 mV rms | 1 MHz Bandwidth, No Load | Typ | PDF p4 | "Ripple 1 MHz Bandwidth, No Load2 50 mV rms" |
| 搬送波・電源発振（本文・図） | 信号の搬送波 約 430 kHz、ブロック図の電源発振器 "430kHz"、出力 LPF "150kHz" | — | 本文・図 | PDF p5, p1 | "it is modulated at a carrier frequency of approximately 430 kHz" |
| バリア容量（CIO の表の値） | — | — | — | — | DS に無い（同相容量 4.5 pF の本文と、同相インピーダンス 2‖4.5 GΩ‖pF のみ） |

## Q3-7. ADI ADuM3190（絶縁エラーアンプ。DS に「絶縁アンプ回路」の節あり）

出典: `ADI_ADuM3190.pdf`（Rev. A、ミラー）。表の条件（PDF p4＝印刷 p3）: "VDD1 = VDD2 = 3 V to 20 V for TA = TMIN to TMAX. All typical specifications are at TA = 25°C and VDD1 = VDD2 = 5 V, unless otherwise noted."

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | 側 1・側 2 とも 3.0〜20 V | — | Min / Max | PDF p5（印刷 p4） | "Operating Range, Side 1 VDD1 3.0 20 V" |
| 電源電流 | IDD1 1.4 / 2.0 mA、IDD2 2.9 / 5.0 mA | — | Typ / Max | PDF p5 | "IDD1 See Figure 4 1.4 2.0 mA / IDD2 See Figure 5 2.9 5.0 mA" |
| 出力利得（A/B/S/T） | COMP→EAOUT 0.9 / 1.0 / 1.1 V/V | 0.4 V to 2.1 V, ±3 mA | Min / Typ / Max | PDF p4 | "From COMP to EAOUT, 0.4 V to 2.1 V, ±3 mA 0.9 1.0 1.1 V/V" |
| 出力直線性 | −1.0 / +0.15 / +1.0 % | 同上 | Min / Typ / Max | PDF p4 | "Output Linearity2 From COMP to EAOUT ... −1.0 +0.15 +1.0 %" |
| 出力 −3 dB 帯域 | A/S/WS: 100 / 200 kHz、B/T/WT: 250 / 400 kHz | — | Min / Typ | PDF p4 | "B, T, and WT Grades 250 400 kHz" |
| 雑音 | EAOUT 1.7 mV rms、EAOUT2 4.8 mV rms | See Figure 15（帯域の記載は表に無い） | Typ | PDF p4 | "Noise, EAOUT See Figure 15 1.7 mV rms" |
| 入力範囲（op amp 同相） | 0.35〜1.5 V | — | Min / Max | PDF p4 | "Input Common-Mode Range 0.35 1.5 V" |
| 入出力間容量 CI-O | 2.2 pF | f = 1 MHz | 値の列（Typ） | PDF p6（印刷 p5） | "Input-to-Output1 CI-O 2.2 pF f = 1 MHz" |
| 絶縁アンプ回路（本文） | 入力側アンプをユニティ・バッファにした構成。線形アイソレータは約 400 kHz に極 | — | 本文 | PDF p15（印刷 p14） | "the linear isolator ... introduces a pole at approximately 400 kHz" |
| THD / SNR | — | — | — | — | DS に無い |

## Q3-8. Broadcom ACPL-C87B / C87A / C870（光結合、0〜2 V 入力）

出典: `Broadcom_ACPL-C87x.pdf`（AV02-3563EN）。表 7 の条件（p6）: "Unless otherwise noted, TA = –40°C to +105°C, VDD1 = 4.5V to 5.5V, VDD2 = 3.3V to 5.5V, VIN = 0V to 2V, and VSD = 0V."。注 a: "All Typical values are under Typical Operating Conditions at TA = 25°C, VDD1 = 5V, VDD2 = 5V."

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | VDD1 4.5〜5.5 V、VDD2 3.0〜5.5 V | — | Min / Max | p5 Table 6 | "VDD1 Supply Voltage VDD1 4.5 5.5 V / VDD2 Supply Voltage VDD2 3.0 5.5 V" |
| 入力範囲 | 0〜2.0 V（注: 2 V が公称、FSR は 2.46 V） | — | Min / Max | p5 | "Input Voltage Rangea VIN 0 2.0 V" / "a. 2V is the nominal input range. Full scale input range (FSR) is 2.46V." |
| 利得 | C87B: 0.995 / 1 / 1.005、C87A: 0.99 / 1 / 1.01、C870: 0.97 / 1 / 1.03 V/V | TA = 25°C（C87B は VDD2 = 5V） | Min / Typ / Max | p6 Table 7 | "Gain (ACPL-C87B, ± 0.5%) G0 0.995 1 1.005 V/V TA = 25°C; VDD2 = 5V" |
| 非直線性 | 0.05 / 0.1 % | VIN = 0 to 2V, TA = 25°C | Typ / Max | p6 | "Nonlinearity NL — 0.05 0.1 % VIN = 0 to 2V, TA = 25°C" |
| 入力インピーダンス | 1000 MΩ | — | Typ | p6 | "Equivalent Input Impedance RIN — 1000 — MΩ" |
| 出力雑音 | 0.013 mVrms | Vin = 0V; output low-pass filtered to 180 KHz。注 d: 差動→単端の後段アンプの出力で測定 | Typ | p6 | "Vout Noise Nout — 0.013 — mVrms Vin = 0V; output low-pass filtered to 180 KHz." |
| AC 雑音 vs フィルタ周波数 | 20 kHz フィルタで Vin = 0 V: ほぼ 0、Vin = 1 V: 約 2.2 mVrms、Vin = 2 V: 約 4.5 mVrms（目読み。入力電圧で雑音が増える） | — | グラフ | p9 Figure 12（画像で確認） | "Figure 12: AC Noise vs. Filter Freq vs. Vin" |
| 帯域 | 70 / 100 kHz | Guaranteed by design | Min / Typ | p6 | "Small-Signal Bandwidth (–3 dB) f–3 dB 70 100 — kHz" |
| 入出力間容量 CI-O | 0.5 pF | f = 1 MHz | Typ | p7 Table 8 | "Capacitance (Input-Output) CI-O — 0.5 — pF f = 1 MHz" |
| 電源電流 | IDD1 10.5 / 15 mA、IDD2 6.5 / 12 mA（5 V）・6.1 / 11 mA（3.3 V） | VSD = 0V | Typ / Max | p7 | "Input Side Supply Current IDD1 — 10.5 15 mA VSD = 0V / IDD2 — 6.5 12 mA 5V supply" |
| THD / SNR | — | — | — | — | DS に無い |

## Q3-9. Broadcom HCPL-7800A / HCPL-7800（光結合、±200 mV 入力、利得 8）

出典: `Broadcom_HCPL-7800.pdf`（AV02-0410EN）。DC/AC 表の条件（p7, p8）: "Unless otherwise noted, all typicals and figures are at the nominal operating conditions of VIN+ = 0V, VIN– = 0V, VDD1 = VDD2 = 5V and TA = 25°C; all Min./Max. specifications are within the recommended operating conditions."。p8 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | VDD1, VDD2 4.5〜5.5 V | — | Min / Max | p6 | "Supply Voltage VDD1, VDD2 4.5 5.5 V" |
| 入力（線形） | −200〜200 mV | — | Min / Max | p6 | "Input Voltage (accurate and linear) VIN+, VIN– –200 200 mV" |
| 利得 | 7800A: 7.92 / 8.00 / 8.08、7800: 7.76 / 8.00 / 8.24 V/V | –200 mV < VIN+ < 200 mV, TA = 25°C | Min / Typ / Max | p7 | "Gain (HCPL-7800A) G1 7.92 8.00 8.08 V/V" |
| 非直線性 | NL200: 0.0037 / 0.35 %、NL100: 0.0027 / 0.2 % | ±200 mV / ±100 mV | Typ / Max | p7 | "VOUT 200 mV Nonlinearity NL200 — 0.0037 0.35 %" |
| 帯域 | 50 / 100 kHz | VIN+ = 200 mVpk-pk | Min / Typ | p8（画像で確認） | "VOUT Bandwidth (–3 dB) BW 50 100 — kHz VIN+ = 200 mVpk-pk" |
| 出力雑音 | 31.5 mVrms | VIN+ = 0.0V。注 a: チョッパ雑音（典型 400 kHz）と ΣΔ 量子化雑音 | Typ | p8 | "VOUT Noise NOUT — 31.5 — mVrms VIN+ = 0.0V" / "(typically 400 kHz at room temperature)" |
| 入力 DC 同相除去 | 76 dB | — | Typ | p7 | "Input DC Common-Mode CMRRIN — 76 — dB" |
| 入出力間容量 CI-O | 1.2 pF | ƒ = 1 MHz | Typ | p9 | "Capacitance (Input-Output) CI-O — 1.2 — pF ƒ = 1 MHz" |
| 電源電流 | IDD1 10.86 / 16.0 mA（VIN+ = 400 mV）、IDD2 11.56 / 16.0 mA（VIN+ = –400 mV） | — | Typ / Max | p7 | "Input Supply Current IDD1 — 10.86 16.0 mA VIN+ = 400 mV" |
| THD / SNR | — | — | — | — | DS に無い |

## Q3-10. Skyworks（旧 Silicon Labs）Si8920（シャント用、±100 / ±200 mV）

出典: `Skyworks_Si8920.pdf`（206333A, July 26 2022、ミラー）。表 4.1 の条件（p6）: "VDDA, VDDB = 5 V, TA = –40 to +125 °C; typical specs at 25 °C"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | VDDA・VDDB とも 3.0〜5.5 V | — | Min / Max | p6 Table 4.1 | "Input Side Supply Voltage VDDA 3.0 5.5 V" |
| 電源電流 | IVDDA 3.2 / 4.2 / 5.5 mA、IVDDB 2.7 / 3.8 / 4.9 mA | VDDA = VDDB = 3.3 V | Min / Typ / Max | p6 | "Input Supply Current IVDDA VDDA = VDDB = 3.3 V 3.2 4.2 5.5 mA" |
| 入力範囲 | Si8920A: −100〜100 mV、Si8920B: −200〜200 mV | VAIP – VAIN | Min / Max | p6 | "Specified Full-Scale Input Amplitude Si8920A –100 100 mV / Si8920B –200 200 mV" |
| 差動入力インピーダンス | A: 20 kΩ、B: 37.2 kΩ | — | Typ | p6 | "Differential Input impedance Si8920A 20 / Si8920B 37.2 kΩ" |
| 帯域 | 950 kHz | — | Typ | p6 | "Amplifier Bandwidth 950 kHz" |
| 利得誤差 | −0.5〜0.5 % | TA = 25 °C | Min / Max | p6 | "Gain Error TA = 25 °C –0.5 0.5 %" |
| 非直線性 | A: 0.04 / 0.15 %、B: 0.025 / 0.1 % | — | Typ / Max | p6 | "Nonlinearity Si8920A 0.04 0.15 / Si8920B 0.025 0.1 %" |
| 出力雑音 | A: 0.14 / 0.28 mVrms、B: 0.10 / 0.20 mVrms | 100 kHz bandwidth | Typ / Max | p6 | "Output Noise Si8920A 100 kHz bandwidth 0.14 0.28 mVrms" |
| 入出力間容量 CIO | 1 pF（GW DIP-8）、1 pF（WB SOIC-16） | f = 1 MHz | パッケージ列（画像で確認） | p13 Table 4.6 | "Capacitance (Input-Output)2 CIO f = 1 MHz 1 1 pF" |
| 高圧側電源 | 入力側 VDDA が別に要る（図の "Isolated Supply"） | — | 図の記載 | p7 | "Isolated Supply" |
| THD / SNR | — | — | — | — | DS に無い |

### Q3 で探したが DS に無かった項目

- **1 kHz 未満（20〜50 Hz）での THD・SNR の規定**（TI は fIN = 1 kHz または 10 kHz のみ。AD215 は 1 kHz / 10 kHz）
- THD: ACPL-C87x、HCPL-7800、Si8920、ADuM3190 は THD の規定なし
- SNR: ISO224、AD215、ACPL-C87x、HCPL-7800、Si8920、ADuM3190 は SNR の規定なし
- AD215 のバリア容量 CIO（「同相容量 4.5 pF」の本文と同相インピーダンスのみ）
- AMC3330 / AMC3336 の **DC/DC の動作周波数の数値**（spread-spectrum とだけ書いてある）、放射の数値（CISPR 適合の記載のみ）
- 雑音密度の表の値: AMC1311 / AMC1300 / AMC3330 / AMC3336 はグラフのみ（表は帯域積分の µVrms）。ACPL-C87x、HCPL-7800、Si8920 は密度なし

---

# Q4 デジタル・アイソレータ（I2S / I2C / 制御）

## Q4-1. TI ISO7741（4 ch、3 順 1 逆）

出典: `TI_ISO7741.pdf`（SLLSEP4K）。p7 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源 | VCC1, VCC2 2.25〜5.5 V | — | MIN / MAX | p7 §5.3（画像で確認） | "VCC1, VCC2 Supply Voltage 2.25 5.5 V" |
| データレート（推奨動作条件） | **表は MAX 50 Mbps、注 (2) は 100 Mbps** | — | MAX | p7（画像で確認） | "DR Data Rate(2) 50 Mbps" / "(2) 100 Mbps is the maximum specified data rate, although higher data rates are possible." |
| 伝搬遅延 | 3.3 V: 6 / 13.5 / 18.5 ns（5 V: 6 / 12.7 / 17、2.5 V: 7.5 / 14 / 21） | See Figure 6-1 | MIN / TYP / MAX | p20 §5.16（5 V は p19、2.5 V は p21） | "tPLH, tPHL Propagation delay time 6 13.5 18.5 ns" |
| パルス幅歪み PWD | 5.9 ns | 各電源 | MAX | p19〜p21 | "PWD Pulse width distortion(1) |tPHL – tPLH| 5.9 ns" |
| 時間間隔誤差 tie | 1.4 ns（5 V）、1.3 ns（3.3 V）、1.5 ns（2.5 V） | 2^16 – 1 PRBS data at 100 Mbps | TYP | p19, p20, p21 | "tie Time interval error 216 – 1 PRBS data at 100 Mbps 1.3 ns" |
| スキュー | tsk(o) 4.4 ns、tsk(pp) 5 ns（3.3 V） | — | MAX | p20 | "tsk(o) ... Same-direction channels 4.4 ns / tsk(pp) Part-to-part skew time(3) 5 ns" |
| バリア容量 CIO | ≅1 pF（DW-16 / DUW-16 / DBQ-16 とも） | VIO = 0.4 x sin (2πft), f = 1 MHz | パッケージ列 | p9 §5.6 | "CIO Barrier capacitance, input to output(6) VIO = 0.4 x sin (2πft), f = 1 MHz ≅1 ≅1 ≅1 pF" |
| 電源電流（ISO7741、3.3 V） | 1 Mbps: ICC1 3.2 / 4.7、ICC2 2.7 / 4.5 mA。10 Mbps: 3.5 / 5.2、3.7 / 5.8。100 Mbps: 8 / 11、15 / 19.5 mA | All channels switching with square wave clock input; CL = 15 pF | TYP / MAX | p16 §5.12 | "All channels switching with square wave clock input; CL = 15 pF ... 100 Mbps ICC1 8 11 / ICC2 15 19.5" |
| 電源電流（ISO7741、5 V） | 10 Mbps: ICC1 3.7 / 5.5、ICC2 4.2 / 6.4。100 Mbps: 11.4 / 14.4、21 / 25 mA | 同上 | TYP / MAX | p14 §5.10 | "10 Mbps ICC1 3.7 5.5 / ICC2 4.2 6.4 / 100 Mbps ICC1 11.4 14.4 / ICC2 21 25" |
| アイダイアグラム（本文） | 100 Mbps PRBS 2^16 – 1 の典型アイ | — | 本文・図 | p33 §8.2.3 | "The following typical eye diagrams of the ISO774x family of devices indicates low jitter and wide open eye at the maximum data rate of 100 Mbps." |

## Q4-2. TI ISO7762（6 ch、4 順 2 逆）

出典: `TI_ISO7762.pdf`（SLLSER1H）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| データレート | 0〜100 Mbps | — | MIN / MAX | p7 §5.3 | "DR(2) Data Rate 0 100 Mbps" |
| 伝搬遅延 | 3.3 V: 6 / 12 / 18.5 ns（5 V: 6 / 11 / 17、2.5 V: 7.5 / 13 / 21） | — | MIN / TYP / MAX | p20（p19, p21） | "tPLH, tPHL Propagation delay time 6 12 18.5 ns" |
| PWD | 3.3 V: 0.5 / 5.9 ns（5 V: 0.4 / 5.9、2.5 V: 0.6 / 5.9） | — | TYP / MAX | p20 | "PWD Pulse width distortion(1) |tPHL – tPLH| 0.5 5.9 ns" |
| tie | 1.3 ns（5 V・3.3 V・2.5 V とも） | 2^16 – 1 PRBS data at 100 Mbps | TYP | p19〜p21 | "tie Time interval error 216 – 1 PRBS data at 100 Mbps 1.3 ns" |
| バリア容量 CIO | ~1.1 pF（DW-16）、~0.9 pF（DBQ-16） | VIO = 0.4 x sin (2πft), f = 1 MHz | パッケージ列 | p9 | "CIO Barrier capacitance, input to output(6) ... ~1.1 ~0.9 pF" |
| 電源電流（ISO7762、3.3 V） | 1 Mbps: ICC1 4.4 / 6.6、ICC2 3.9 / 6.3。10 Mbps: 5.2 / 7.5、5.4 / 8.1。100 Mbps: 12.9 / 16.9、19.5 / 26 mA | All channels switching with square wave clock input; CL = 15 pF | TYP / MAX | p16 §5.12 | "100 Mbps ICC1 12.9 16.9 / ICC2 19.5 26" |

## Q4-3. TI ISO1540 / ISO1541（I2C アイソレータ）

出典: `TI_ISO1540.pdf`（SLLSEB6F）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 動作周波数 | 1 MHz | 注 (1): 最大バス負荷・最大シンク電流での値 | MAX | p6 | "fMAX Operating frequency(1) 1 MHz" |
| 伝搬遅延（3〜3.6 V） | tpLH1-2 33 / 65 ns、tPHL1-2 90 / 181 ns、tPLH2-1 47 / 68 ns、tPHL2-1 67 / 109 ns | R1 = 953 Ω, R2 = 95.3 Ω, C1, C2 = 10 pF | TYP / MAX | p12 §6.12 | "tpLH1-2 ... 0.55 V to 0.7 × VCC2 33 65 ns / tPHL1-2 0.7 V to 0.4 V 90 181 ns" |
| バリア容量 CIO | ~1 pF | VIO = 0.4 sin (2πft), f = 1 MHz | 値の列のみ | p8 | "CIO Barrier capacitance, input to output(4) VIO = 0.4 sin (2πft), f = 1 MHz ~1 pF" |
| 電源電流（ISO1540、3〜3.6 V） | ICC1 2.4 / 7.1 mA（バス Low）・2.5 / 4 mA（バス High）。ICC2 1.7 / 6.7 mA・1.9 / 3.5 mA | R1, R2 = Open; C1, C2 = Open | TYP / MAX | p11 §6.10 | "VSDA1, VSCL1 = GND1; VSDA2, VSCL2 = GND2; R1, R2 = Open; C1, C2 = Open 2.4 7.1" |

## Q4-4. ADI ADuM1250 / ADuM1251（ホットスワップ I2C アイソレータ）

出典: `ADI_ADuM1250.pdf`（Rev. L、ミラー）。p5 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 最大周波数 | 1000 kHz | — | **Min**（画像で確認） | p5 Table 2 | "MAXIMUM FREQUENCY 1000 kHz" |
| 伝搬遅延（3 V） | tPLH12 82 / 125、tPHL12 196 / 340、tPLH21 32 / 75、tPHL21 110 / 210 ns | 3.0 V ≤ VDD1, VDD2 ≤ 3.6 V, CL1 = CL2 = 0 pF, R1 = 1.0 kΩ, R2 = 120 Ω | Typ / Max | p5（画像で確認） | "Side 1 to Side 2, Rising Edge 1 tPLH12 82 125 ns" |
| 電源電流（ADuM1250、3.3 V） | IDD1 1.9 / 3.0 mA、IDD2 1.7 / 3.0 mA | VDD1 = 3.3 V / VDD2 = 3.3 V | Typ / Max | p4 Table 1 | "Input Supply Current, Side 1, 3.3 V IDD1 1.9 3.0 mA VDD1 = 3.3 V" |
| 入出力間容量 CIO | 1.0 pF | fTEST = 1 MHz | 値の列（Typ） | p6 | "Capacitance (Input to Output)1 CIO 1.0 pF fTEST = 1 MHz" |

## Q4-5. ADI ADuM1400 / ADuM1401 / ADuM1402（4 ch、iCoupler）

出典: `ADI_ADuM1400.pdf`（Rev. M、ミラー）。p5 を画像で確認。5 V 表（p4〜p5）の条件: "4.5 V ≤ VDD1 ≤ 5.5 V, 4.5 V ≤ VDD2 ≤ 5.5 V ... all typical specifications are at TA = 25°C, VDD1 = VDD2 = 5 V."。3 V 表（p6〜p8）: "2.7 V ≤ VDD1 ≤ 3.6 V, 2.7 V ≤ VDD2 ≤ 3.6 V ... VDD1 = VDD2 = 3.0 V."

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 最大データレート | ARW 1 Mbps、BRW 10 Mbps、CRW 90 / 120 Mbps | CL = 15 pF, CMOS signal levels。注 3: 規定 PWD を保証する最速レート | Min（CRW は Min / Typ） | p5（画像で確認） | "ADuM1400CRW/... Maximum Data Rate3 90 120 Mbps" |
| 伝搬遅延（CRW） | 5 V: 18 / 27 / 32 ns、3 V: 20 / 34 / 45 ns | CL = 15 pF | Min / Typ / Max | p5, p8 | "Propagation Delay4 tPHL, tPLH 18 27 32 ns" |
| PWD（CRW） | 5 V・3 V とも 0.5 / 2 ns | CL = 15 pF | Typ / Max | p5, p8 | "Pulse Width Distortion, |tPLH − tPHL|4 PWD 0.5 2 ns" |
| リフレッシュ・レート | 1.2 Mbps（5 V）、1.1 Mbps（3 V 表） | — | Typ | p5, p8 | "Refresh Rate fr 1.2 Mbps" |
| 入出力間容量 CI-O | 2.2 pF | f = 1 MHz | 値の列（Typ） | p20 | "Capacitance (Input to Output)1 CI-O 2.2 pF f = 1 MHz" |
| 電源電流（ADuM1400、5 V） | 10 Mbps: IDD1 8.6 / 10.6、IDD2 2.6 / 3.5 mA（5 MHz logic signal freq.）。90 Mbps: IDD1 70 / 100、IDD2 18 / 25 mA（45 MHz） | 4 ch 合計 | Typ / Max | p4 Table 1 | "90 Mbps (CRW Grade Only) VDD1 Supply Current IDD1 (90) 70 100 mA 45 MHz logic signal freq." |
| 電源電流（ADuM1400、3 V） | 10 Mbps: IDD1 4.5 / 6.5、IDD2 1.4 / 2.0 mA。90 Mbps: IDD1 37 / 65、IDD2 11 / 15 mA | 4 ch 合計 | Typ / Max | p6 Table 2 | "IDD1 (90) 37 65 mA 45 MHz logic signal freq." |
| ジッタ | — | — | — | — | DS に無い |

## Q4-6. Skyworks Si864x（4 ch、〜150 Mbps）

出典: `Skyworks_Si864x.pdf`（206329A）。表 4.3 の条件（p17）: "(VDD1 = 3.3 V ±10%, VDD2 = 3.3 V ±10%, TA = –40 to 125 °C)"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 最大データレート | 0〜150 Mbps | Si864xBx, Ex | Min / Max | p19 Table 4.3 | "Maximum Data Rate 0 — 150 Mbps" |
| 伝搬遅延 | 5.0 / 8.0 / 13 ns（3.3 V）、5.0 / 8.0 / 14 ns（2.5 V） | See Figure 4.2 | Min / Typ / Max | p19（p23） | "Propagation Delay tPHL, tPLH See Figure 4.2 Propagation 5.0 8.0 13 ns" |
| PWD | 0.2 / 4.5 ns | — | Typ / Max | p19 | "Pulse Width Distortion ... PWD — 0.2 4.5 ns" |
| ピーク・アイ・ジッタ | 350 ps | See Figure 2.3 Eye Diagram | Typ | p19（5 V 表 p15、2.5 V 表 p23 も同値） | "Peak Eye Diagram Jitter tJIT(PK) See Figure 2.3 Eye Diagram — 350 — ps" |
| アイ測定の説明（本文） | Si8640 で 150 Mbps、PWD 2 ns・ピーク・ジッタ 350 ps | Anritsu MP1763C | 本文 | p7 | "The results also show that 2 ns pulse width distortion and 350 ps peak jitter were exhibited." |
| 入出力間容量 CIO | 2.0 pF（WB SOIC-16 / NB SOIC-16 / QSOP-16 とも） | f = 1 MHz | パッケージ列 | p25 Table 4.6 | "Capacitance (Input-Output) 2 CIO f = 1 MHz 2.0 2.0 2.0 pF" |
| 電源電流（Si8641Bx、3.3 V） | 1 Mbps: VDD1 3.4 / 4.8、VDD2 3.3 / 4.6 mA。10 Mbps: 3.5 / 4.9、3.6 / 5.1。100 Mbps: 5.9 / 7.9、10.3 / 13.4 mA | All Inputs = 500 kHz / 5 MHz / 50 MHz Square Wave, CI = 15 pF on All Outputs | Typ / Max | p18〜p19 | "100 Mbps Supply Current (All Inputs = 50 MHz Square Wave, CI = 15 pF on All Outputs) ... Si8641Bx, Ex VDD1 5.9 7.9 mA / VDD2 10.3 13.4" |

## Q4-7. Skyworks Si860x（I2C アイソレータ）

出典: `Skyworks_Si860x.pdf`（206852A）。表 5.2/5.3 の条件: "3.0 V < VDD < 5.5 V. TA = –40 to +125 °C. Typical specs at 25 °C"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 最大 I2C バス周波数 | 1.7 MHz | — | Max | p15 | "Maximum I2C Bus Frequency Fmax — — 1.7 MHz" |
| 伝搬遅延（3.3 V） | A→B 立上り 44 / 55、立下り 17 / 29、B→A 立上り 30 / 40、立下り 14 / 27 ns | No bus capacitance, R1 = 806, R2 = 499 | Typ / Max | p15 | "3.3 V Operation Tphab ... 44 55 ns" |
| 非 I2C チャネル | 0〜10 Mbps、伝搬遅延 max 20 ns（Si8602/05/06） | — | Min・Max／Max | p16 Table 5.4 | "Maximum Data Rate 0 — 10 Mbps / Propagation Delay tPHL, tPLH — — 20 ns" |
| 入出力間容量 CIO | 1.0 pF（NB SOIC-8）、2.0 pF（NB SOIC-16）、2.0 pF（WB SOIC-16） | f = 1 MHz | パッケージ列 | p19 | "Capacitance (Input-Output)2 CIO f = 1 ΜΗz 1.0 2.0 2.0 pF" |
| 電源電流（Si8600） | 1.7 MHz: Idda 3.3 / 5.0、Iddb 2.6 / 3.9 mA | All channels = 1.7 MHz | Typ / Max | p13 | "All channels = 1.7 MHz AVDD Current Idda 3.3 5.0 mA / BVDD Current Iddb 2.6 3.9" |

## Q4-8. ADI ADuM5401〜5404（isoPower、絶縁 DC/DC 内蔵 4 ch）

出典: `ADI_ADuM5401.pdf`（Rev. C、ミラー）。5 V/5 V 表の条件（p4）: "Typical specifications are at TA = 25°C, VDD1 = VSEL = VISO = 5 V. Minimum/maximum specifications apply over the entire recommended operation range which is 4.5 V ≤ VDD1, VSEL, VISO ≤ 5.5 V; and −40°C ≤ TA ≤ +105°C ... Switching specifications are tested with CL = 15 pF and CMOS signal levels"。p4 を画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 出力電力（Features） | 最大 500 mW | — | — | p1 | "Up to 500 mW output power" |
| VISO 設定値 | 5 V 出力: 4.7 / 5.0 / 5.4 V。3.3 V 出力（3.3 V 入力）: 3.0 / 3.3 / 3.6 V | IISO = 0 mA | Min / Typ / Max | p4 Table 2, p6 Table 6 | "Setpoint VISO 4.7 5.0 5.4 V IISO = 0 mA" |
| 出力電流 IISO(MAX) | 5 V/5 V: 100 mA（VISO > 4.5 V）、3.3 V/3.3 V: 60 mA、5 V/3.3 V: 100 mA | — | Min | p4, p6, p8 | "Output Supply Current IISO (MAX) 100 mA VISO > 4.5 V" |
| 効率 | 34 %（5 V/5 V, IISO = 100 mA）、33 %（3.3/3.3, 60 mA）、30 %（5/3.3, 90 mA） | — | Typ | p4, p6, p8 | "Efficiency at IISO (MAX) 34 % IISO = 100 mA" |
| **スイッチング周波数** | **180 MHz** | — | Typ | p4（p6, p8 も同値） | "Switching Frequency fOSC 180 MHz" |
| **PWM 周波数** | **625 kHz** | — | Typ | p4（p6, p8 も同値） | "PWM Frequency fPWM 625 kHz" |
| 出力リップル／雑音 | 75 mV p-p（20 MHz BW）／200 mV p-p | CBO = 0.1 µF‖10 µF, IISO = 90 mA | Typ | p4 | "Output Ripple VISO (RIP) 75 mV p-p 20 MHz bandwidth ... / Output Noise VISO (NOISE) 200 mV p-p" |
| 入力電流 IDD1 | 5 V: 無負荷 19 / 30 mA、全負荷 290 mA。3.3 V: 14 / 20 mA、175 mA | — | Typ / Max | p4, p6 | "IDD1, No VISO Load IDD1 (Q) 19 30 mA / IDD1, Full VISO Load IDD1 (MAX) 290 mA" |
| データレート | A grade 1 Mbps、C grade 25 Mbps | Within PWD limit | Max | p4 Table 4（画像で確認） | "Data Rate 1 25 Mbps Within PWD limit" |
| 伝搬遅延／PWD（5 V） | A: 55 / 100 ns・PWD 40 ns。C: 45 / 60 ns・PWD 6 ns | 50% input to 50% output | Typ / Max | p4 | "Propagation Delay tPHL, tPLH 55 100 45 60 ns / Pulse Width Distortion PWD 40 6 ns" |
| 入出力間容量 CI-O | 2.2 pF | f = 1 MHz | 値の列（Typ） | p10 | "Capacitance (Input-to-Output)1 CI-O 2.2 pF f = 1 MHz" |
| EMI（本文） | DC/DC 部は 180 MHz で動作し、GND/電源プレーンに高周波電流が流れて端面放射と一次・二次 GND 間のダイポール放射を生む。接地した筐体を推奨 | — | 本文 | p22 "EMI CONSIDERATIONS" | "must operate at 180 MHz to allow efficient power transfer through the small transformers. This creates high frequency currents that can propagate in circuit board ground and power planes, causing edge emissions and dipole radiation between the primary and secondary ground planes. Grounded enclosures are recommended" |
| ジッタ | — | — | — | — | DS に無い |

## Q4-9. TI ISOW7741（4 ch＋低放射 DC/DC 内蔵）

出典: `TI_ISOW7741.pdf`（SLLSFK1C）。電力変換部の条件（p13）: "VDD = 5 V ±10% or 3.3 V ±10% and VISOIN power externally, GND1 = GNDIO, GND2 = GISOIN"。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| データレート | 100 Mbps | — | MAX | p9 | "DR Data rate 100 Mbps" |
| 出力電力（Features） | 最大 0.55 W、最大負荷効率 46 % | — | — | p1 | "Up to 0.55-W output power" / "Efficiency at max load: 46%" |
| **変換器の周波数** | **25 MHz**（Features と本文） | — | 本文 | p1, p43 | "Low frequency power converter at 25 MHz" / "Reduced power converter switching frequency to 25 Mhz to reduce strength of high frequency components in emissions spectrum" |
| 放射（Features） | CISPR 32 と EN 55032 Class B に 2 層基板で >5 dB 余裕 | — | — | p1 | "Emission optimized to meet CISPR 32 and EN 55032 Class B with >5 dB margin on 2 layer" |
| VISOOUT（5 V→5 V） | 4.5 / 5 / 5.25 V（0〜110 mA）、効率 46 %、リップル 24 mV pk-pk | リップル: 20-MHz bandwidth, CLOAD = 0.01 µF ‖ 20 µF, IISOOUT = 110 mA | MIN / TYP / MAX（効率・リップルは TYP） | p13 §7.9 | "External IISOOUT = 0 to 110 mA 4.5 5 5.25 V" / "EFF ... 46%" / "VISOOUT(RIP) ... 24 mV" |
| VISOOUT（5 V→3.3 V） | 3.135 / 3.3 / 3.465 V（0〜140 mA）、効率 36 %、リップル 30 mV | — | 同上 | p13 | "External IISOOUT = 0 to 140 mA 3.135 3.3 3.465 V" / "36%" |
| VISOOUT（3.3 V→3.3 V） | 3.135 / 3.3 / 3.465 V（0〜60 mA）、効率 43 %、リップル 14 mV | — | 同上 | p13 | "External IISOOUT = 0 to 60 mA" / "43%" / "14 mV" |
| 変換器の入力電流 | 5 V→5 V: 225 / 316 mA（110 mA 負荷）。3.3→3.3: 143 / 216 mA（60 mA 負荷） | — | TYP / MAX | p14 §7.10 | "VDD = 5 V, VSEL = VISOOUT ILOAD = 110 mA 225 316 mA" |
| 伝搬遅延／PWD（3.3 V） | 6 / 11 / 16.2 ns、PWD 0.6 / 4.7 ns | — | MIN / TYP / MAX、TYP / MAX | p28 §7.20 | "tPLH, tPHL Propagation delay time ... 6 11 16.2 ns / PWD ... 0.6 4.7 ns" |
| バリア容量 CIO | ~3.5 pF | VIO = 0.4 × sin (2πft), f = 1 MHz | 値の列のみ | p11 | "CIO Barrier capacitance, input to output(5) VIO = 0.4 × sin (2πft), f = 1 MHz ~3.5 pF" |
| ジッタ／tie | — | — | — | — | DS に無い |

## Q4-10. TI ISOW1044（絶縁 CAN FD トランシーバ＋DC/DC 内蔵）

出典: `TI_ISOW1044.pdf`（SLLSFF7B）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 信号 | CAN 5 Mbps、GPIO チャネル 10 Mbps | — | MAX | p7 | "1/tUI Signaling rate CAN 5 Mbps / DR Data rate for extra GPIO channel GPIO 10 Mbps" |
| 変換器の周波数 | 25 MHz | — | Features | p1 | "Low frequency power converter at 25MHz" |
| 効率 | 47 %（typ） | — | Features | p1 | "Typical efficiency: 47%" |
| 放射 | CISPR 32 / EN 55032 Class B に適合（2 層基板＋フェライトビーズ） | — | 本文 | p1, p2 | "Meets CISPR 32 and EN 55032 Class B" |
| VISOOUT | 4.75 / 5 / 5.25 V | EN=VDD, STB, TXD, IN floating | MIN / TYP / MAX | p10 | "VISOOUT Isolated Output supply voltage EN=VDD, STB, TXD, IN floating 4.75 5 5.25 V" |
| 外部に取れる電流 | 20 mA | VDD = 4.5 to 5.5V, CAN full loaded 60Ω, TXD toggling 5Mbps, IN toggling 10Mbps | TYP | p10 | "Iout Extra current available on Visoout ... 20 mA" |
| 変換器の電源電流 | 76 / 123 mA（TXD 1 Mbps）、26 / 46 mA（recessive） | RL = 60Ω | TYP / MAX | p13 §6.10 | "IDD TXD = 1Mbps 50% duty square wave, RL = 60Ω 76 123 mA" |
| バリア容量 CIO | ≅3.5 pF | VIO = 0.4 sin (2πft), f = 1MHz | 値の列のみ | p8 | "CIO Barrier capacitance, input to output(5) VIO = 0.4 sin (2πft), f = 1MHz ≅3.5 pF" |

### Q4 で探したが DS に無かった項目

- **周期ジッタ／位相雑音（クロック信号を通したときの jitter、たとえば 24.576 MHz の MCLK 相当）**はどの DS にも規定が無い。あるのは ISO7741 / ISO7762 の tie（100 Mbps PRBS の時間間隔誤差）と Si864x のピーク・アイ・ジッタ 350 ps だけ
- ADuM1400、ADuM5401、ISOW7741 はジッタ・tie の規定なし
- 放射の**数値**（dBµV/m）: ISOW7741 / ISOW1044 は CISPR 適合の記載とグラフ（ISOW1044 Figure 9-4 は未読）、ADuM5401 は本文の注意のみ
- ISO7741 のデータレートは推奨動作条件の表（50 Mbps）と注（100 Mbps）が食い違う（原文のまま）

---

# Q5 小型ライン・トランス

## Q5-1. Jensen JT-11P-1（1:1 ブリッジング入力用）

出典: `Jensen_JT-11P-1.pdf`。p2 の表は抽出で崩れるため画像で確認（見出し "JT-11P-1 SPECIFICATIONS (all levels are input unless noted)"、注 "Unless noted otherwise, all specifications apply at 25°C"）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 帯域（Features） | −3 dB at 0.25 Hz and 95 kHz | — | — | p1 | "Wide bandwidth: -3 dB at 0.25 Hz and 95 kHz" |
| 推奨レベル（Features） | +20 dBu at 20 Hz まで | — | — | p1 | "Recommended for levels up to +20 dBu at 20 Hz" |
| 入力インピーダンス | 12.3 / 13.0 / 13.7 kΩ | 1 kHz, +4 dBu, test circuit 1（負荷 10 kΩ） | MINIMUM / TYPICAL / MAXIMUM | p2（画像で確認） | "Input impedance, Zi 1 kHz, +4 dBu, test circuit 1 12.3 kΩ 13.0 kΩ 13.7 kΩ" |
| 電圧利得 | −2.6 / −2.3 / −2.0 dB | 同上 | MIN / TYP / MAX | p2 | "Voltage gain ... –2.6 dB –2.3 dB –2.0 dB" |
| 振幅特性（1 kHz 基準） | 20 Hz: −0.15 / −0.04 / 0.0 dB、20 kHz: −0.15 / −0.05 / 0.0 dB | +4 dBu, test circuit 1, Rs=600 Ω | MIN / TYP / MAX | p2 | "20 Hz, +4 dBu, test circuit 1, Rs=600 Ω –0.15 dB –0.04 dB 0.0 dB" |
| THD | 1 kHz: <0.001 %、20 Hz: 0.025 % / 0.10 % | +4 dBu, test circuit 1, Rs=600 Ω | TYPICAL（20 Hz は TYP / MAX） | p2 | "Distortion (THD) 1 kHz ... <0.001% / 20 Hz ... 0.025% 0.10%" |
| 20 Hz 最大入力 | +18 / +20 dBu | 1% THD, test circuit 1, Rs=600 Ω | MIN / TYP | p2 | "Maximum 20 Hz input level 1% THD ... +18 dBu +20 dBu" |
| THD+N vs 周波数 | +4 dBu: 20 Hz 約 0.025 %、約 60 Hz で 0.004 %、約 130 Hz で 0.001 %。+14 dBu: 20 Hz 約 0.055 %、50 Hz 約 0.012 %。+20 dBu: 20 Hz 約 1 %、約 30 Hz で 0.1 %（目読み） | "THD at FIXED INPUT LEVELS" | グラフ（Audio Precision） | p2（画像で確認） | "THD at FIXED INPUT LEVELS THD+N (%) vs FREQUENCY (Hz)" |
| THD+N vs 入力レベル | 20 Hz: 約 0.02〜0.025 %（−25〜+5 dBu）、30 Hz: 約 0.012 %、50 Hz: 約 0.005 %（〜+10 dBu 付近まで平坦）（目読み） | "THD at FIXED FREQUENCIES" | グラフ | p2 | "THD at FIXED FREQUENCIES THD+N (%) vs INPUT LEVEL(dBu)" |
| CMRR（50 Ω 平衡信号源） | 60 Hz 107 dB、3 kHz 65 / 73 dB | test circuit 2 | TYP（3 kHz は MIN / TYP） | p2 | "60 Hz, test circuit 2 107 dB / 3 kHz, test circuit 2 65 dB 73 dB" |
| CMRR（600 Ω 不平衡信号源） | 60 Hz 100 dB、3 kHz 68 dB | test circuit 3 | TYP | p2 | "60 Hz, test circuit 3 100 dB / 3 kHz, test circuit 3 68 dB" |
| 出力インピーダンス | 2.34 kΩ | 1 kHz, test circuit 1, Rs=50 Ω | TYP | p2 | "Output impedance, Zo ... 2.34 kΩ" |
| 直流抵抗 | 一次 1.45 kΩ、二次 1.55 kΩ | — | TYP | p2 | "primary (RED to BRN) 1.45 kΩ / secondary (YEL to ORG) 1.55 kΩ" |
| 容量 @1 kHz | 一次–シールド・ケース 98 pF、二次–シールド・ケース 110 pF | — | TYP | p2 | "Capacitances @ 1 kHz primary to shield and case 98 pF / secondary to shield and case 110 pF" |
| 巻数比 | 0.999:1 / 1.000:1 / 1.001:1 | — | MIN / TYP / MAX | p2 | "Turns ratio 0.999:1 1.000:1 1.001:1" |
| 磁気シールド（本文） | 30 dB の磁気シールド・パッケージが標準 | — | 本文 | p1 | "A 30 dB magnetic shield package is standard." |
| 耐圧 | 250 V RMS（一次または二次–シールド・ケース、60 Hz、1 分） | — | MIN | p2 | "Breakdown voltage ... 250 V RMS" |
| 温度範囲 | 0〜70 °C | operation or storage | MIN / MAX | p2 | "Temperature range operation or storage 0° C 70° C" |

## Q5-2. Lundahl LL1540（高インピーダンス・高レベルのライン入力）

出典: `Lundahl_LL1540.pdf`（1 ページ。表は値の列のみ）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構造 | 2 コイル、各コイルに一次・二次を静電シールドで分離。高透磁率ミューメタル・コア、ミューメタル缶 | — | 本文 | p1 | "The transformer consists of two coils, each with one primary and one secondary part separated by a electrostatic shield. The core is a high permeability mu-metal core, and the transformer is housed in a mu-metal can." |
| 巻数比 | 1+1:1+1 | — | 値の列のみ | p1 | "Turns ratio: 1+1:1+1" |
| 歪み | +20 dBu で <0.1 % @50 Hz、+30 dBu で <1 % @50 Hz | source impedance 600Ω | 値の列のみ | p1 | "Distortion (source impedance 600Ω ): + 20 dBU < 0.1% @ 50 Hz +30 dBU < 1 % @ 50 Hz" |
| 周波数特性 | 5 Hz〜50 kHz ±0.2 dB | source 600Ω, load 15 kΩ | 値の列のみ | p1 | "Frequency response (source 600Ω, load 15 k Ω ) 5 Hz -- 50 kHz +/- 0.2 dB" |
| 損失 | 0.5 dB | at 1 kHz with above termination | 値の列のみ | p1 | "Loss across transformer (at 1 kHz with above termination): 0.5 dB" |
| 自己共振 | > 60 kHz | — | 値の列のみ | p1 | "Self resonance point : > 60 kHz" |
| 推奨負荷 | 22 kΩ と 1 nF の直列 | 方形波応答用 | 値の列のみ | p1 | "Recommended load for best square-wave response: 22 kΩ in series with 1nF" |
| 直流抵抗 | 一次 610 Ω（各）、二次 800 Ω（各） | — | 値の列のみ | p1 | "Static resistance of each primary: 610Ω / Static resistance of each secondary: 800Ω" |
| 絶縁 | 巻線間 4 kV、巻線–シールド間 2 kV | — | 値の列のみ | p1 | "Isolation between windings / between windings and shield: 4 kV / 2 kV" |
| CMRR（接続例の注記） | 非対称入力アンプ接続では 2 × 12 k が >60 dB CMRR に必要 | — | 本文 | p1 | "2 x 12 k resistors required for > 60 dB CMRR." |
| 寸法・質量 | 38 × 24 × 17 mm、47 g | — | 値の列のみ | p1 | "Dims ... 38 x 24 x 17 / Weight: 47 g" |

## Q5-3. Hammond 560G（1:1、150/600 Ω、エポキシ・ポッティング PCB 実装）

出典: `Hammond_560.pdf`（560G 個別）と `Hammond_560_series.pdf`（シリーズ一覧）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構造 | 一次・二次間の静電シールド（コアに接続し "SH" ピンへ）、ハムバッキング構造 | — | 本文 | `Hammond_560.pdf` p1 | "Electrostatic shield between primary & secondary connected to core and pin "SH"" / "Humbucking construction" |
| 周波数範囲 | 0 dbm: 30 Hz〜30 kHz ±0.5 db typ、+10 dbm: ±1.0 db typ、+27 dbm: ±1.0 db typ | "Freq. measurements with no D.C. saturation." | 値の列のみ | p1 | "-Freq. range @ +0 dbm is 30 Hz. to 30 Khz. +/- 0.5db typ" |
| 周波数特性（表） | ±1.0 db（30 Hz〜30 kHz） | — | Typical 列 | p1 ELECTRICAL SPECIFICATIONS | "Frequency Response ±1.0db from 30Hz to 30KHz" |
| 挿入損失（シリーズ） | 1 db max | — | — | `Hammond_560_series.pdf` p1 | "Insertion loss of 1 db maximum" |
| インダクタンス | 一次・二次 0.824 H、漏れ 0.509 mH | @ 1.0 kHz, 1.0 V OC | Typical 列 | p1 | "Inductance @ 1.0 kHz, 1.0 V OC Primary 0.824 H / Leakage Inductance 0.509 mH" |
| 直流抵抗 | 一次 13.30 Ω、二次 15.30 Ω | — | Typical 列 | p1 | "DCR Primary 1-4 13.30 Ω Secondary 5-8 15.30 Ω" |
| 巻数比／耐圧 | 1:1／500 Vrms | — | Typical 列 | p1 | "Turns ratio 1:1 / Dielectric Strength 500 Vrms" |
| 周波数特性グラフ | 0 dbm: 20 Hz で約 −0.9 dB。27 dbm: 約 40 Hz で −2 dB（目読み） | Rs=150 Rl=150, Winding Parallel Connected | グラフ | p3（画像で確認） | "560G Rs=150 Rl=150 Frequency Response Winding Parallel Conected" |
| THD+N グラフ | 縦軸は線形で −20〜50「THD+N (%)」と印字。0 dbm の線は 10 Hz で約 7、30 Hz 以上で約 0（目読み。軸表記は原文のまま） | 同上 | グラフ | p3（画像で確認） | "560G Rs-150 Rl=150 THD+N" |

## Q5-4. Hammond 101 シリーズ（小型ポッティング PCB 実装。101F = 600 ct : 600 ct）

出典: `Hammond_101-106.pdf`（シリーズ一覧、個別 DS ではない）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 周波数範囲 | 300 Hz〜100 kHz ±0.5 db @100 mw。+10 dbm・+15 dbm で 200 Hz〜100 kHz、+20 dbm で 300 Hz〜100 kHz | "Frequency measurements with no D.C. current saturation." | 値の列のみ | p1 | "Power level: Minimum frequency range: 300 Hz. to 100 Khz. +/- 0.5 db @ 100 mw" |
| 101F | 一次 600 ct、二次 600 ct、DCR 44 / 52 Ω | — | 表 | p1 | "101F 600 ct 600 ct 44 52 300/300 1200/1200" |
| THD・シールド・容量 | — | — | — | — | DS に無い |

## Q5-5. Triad TY-250P（1000 CT、20 Hz〜20 kHz）／TY-146P（600 CT / 150）

出典: `Triad_TY-250P.pdf`、`Triad_TY-146P.pdf`（各 1 ページ。"Electrical Specifications at 25º C"）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| TY-250P 周波数特性 | ±1 db（20〜20,000 Hz） | — | 値の列のみ | TY-250P p1 | "5. Frequency Response: + 1db from 20 to 20,000 Hz" |
| TY-250P 周波数特性グラフ | 20 Hz で約 −0.4〜−0.55 dB（負荷による）、30 kHz で 600 Ω 負荷 約 −0.4 dB、開放 約 +1.25 dB（目読み） | 600 Ω〜開放の負荷 | グラフ | TY-250P p1（画像で確認） | "TY-250P FREQUENCY RESPONSE" |
| TY-250P インピーダンス等 | 一次 1000 CT、二次 1000 CT / 250、出力 20 mW、挿入損失 <2.8 db、DCR 172 Ω | — | 値の列のみ | TY-250P p1 | "1. Primary Impedance: 1000Ω CT * / 3. Output: 20mW * / 8. Insertion Loss @ 1K Hz: < 2.8db" |
| TY-250P 使用条件の注 | 600:600 等は入力 ≤4.2 Vrms・電流 ≤7 mA の範囲で可 | — | 注 | TY-250P p1 | "optional as long as input voltage is ≤4.2Vrms and current is ≤7mA." |
| TY-250P 耐圧 | 1500 V（一次–二次） | — | 値の列のみ | TY-250P p1 | "13. Dielectric Strength 1500V Primary to Secondary" |
| TY-146P 周波数特性 | ±2 db（200〜15,000 Hz） | — | 値の列のみ | TY-146P p1 | "5. Frequency Response: + 2db from 200 to 15,000 Hz" |
| TY-146P THD | < 0.5 %（275 Hz〜3.5 kHz） | — | 値の列のみ | TY-146P p1 | "10. Total Harmonic Distortion < 0.5% between 275Hz and3.5KHz" |
| TY-146P 縦平衡 | > 45 db | — | 値の列のみ | TY-146P p1 | "7. Longitudinal Balance > 45db" |
| TY-146P 耐圧 | 1500 V（一次–二次–コア） | — | 値の列のみ | TY-146P p1 | "13. Dielectric Strength 1500V Pri to Sec to Core" |

### Q5 で探したが DS に無かった項目

- **一次–二次間の巻線間容量**: どの DS にも無い（Jensen は巻線–シールド・ケース間のみ、Lundahl・Hammond・Triad は容量の記載なし）
- THD の周波数・レベル依存: Lundahl は 50 Hz の 2 点（+20 / +30 dBu）のみ、Hammond 101 と Triad TY-250P は THD の記載なし、TY-146P は 275 Hz〜3.5 kHz のみ
- 20〜50 Hz での THD のグラフ: Jensen JT-11P-1 だけ（p2 の 2 枚）
- 磁気シールドの減衰量: Jensen（30 dB）以外は無い（Lundahl はミューメタル缶、Hammond はハムバッキング構造の記載のみ）
- CMRR: Jensen（50 Ω / 600 Ω 信号源）と Lundahl（接続例の >60 dB）以外は無い（TY-146P は縦平衡 >45 db）
