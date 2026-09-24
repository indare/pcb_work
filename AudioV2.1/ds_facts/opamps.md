# 手持ちオペアンプ（ソケットに挿す石）— DS の事実

2026-09-25 収集。値は DS の原文で裏が取れたものだけ。設計判断は書かない。
2026-09-25 にページ画像と照合した（照合結果 [verify_opamps.md](verify_opamps.md)、その再判定 [../review/ds_errata_review.md](../review/ds_errata_review.md)）。その結果で直した行・足した行は、行末に 〔2026-09-25 照合で訂正〕／〔2026-09-25 照合で追加〕 を付けた。

- 対象: `Audio/OPAMP_INVENTORY.md` の手持ちリストの石（＋ NE5532 本家）。DS は `Audio/datasheets/opamps/`
- **出典のページは PDF のページ番号**（1 始まり）。TI/ADI/NJR とも、この版では印刷ページ番号と一致している
- **「列」**は DS の表のどの列に値があるかを、PDF をページ画像にして目で確かめたもの。
  TI の新しい表で「MIN 列」「MAX 列」とあるのは、1 つのセルに左寄せ・右寄せで置かれた値を、位置で読んだもの（下の各項目に注記）
- **（目読み）**はグラフから目で読んだ値。規定値ではない。読み取り誤差は目盛の刻みの半分程度はある
- 原文の引用は DS の文言そのまま（PDF のテキスト抽出で `±` が落ちた MUSES01/02 は画像で ± を確かめて補った）
- 値の換算（Vrms↔Vp、±12 V への換算など）はしていない

---

## 1. NE5532（TI 本家）

`TI_NE5532.pdf`（SLOS075K, REVISED DECEMBER 2025）。表の既定条件は「VCC± = ±15V, TA = 25°C (unless otherwise noted)」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | VCC+ 5〜15 V、VCC– −5〜−15 V | — | MIN / MAX | p.3 §5.3 | `VCC+ Supply voltage 5 15 V` / `VCC– Supply voltage –5 –15 V` |
| 電源電圧（本文） | ±5〜±15 V | — | —（本文） | p.9 §7.2 | "The NE5532x and SA5532x devices are specified for operation over the range of ±5 to ±15 V" |
| 電源電圧（絶対最大・表） | VCC+ 0〜+18 V、VCC– −18〜0 V | — | MIN / MAX | p.3 §5.1 | `VCC+ 0 +18 V` / `VCC– –18 0 V` |
| 電源電圧（絶対最大・本文の注意） | ±22 V | — | —（本文） | p.9 §7.2 | "Supply voltages outside of the ±22 V range are able to permanently damage the device (see Section 5.1)." ※表（18 V）と食い違う。改訂履歴 p.11 に "Changed Supply voltage positive and negative from 22V to 18V" |
| 静止電流 | typ 6 mA / max 16 mA（**Total supply current**＝パッケージ全体と読める表記） | ±15 V、VO = 0、無負荷、25°C | TYP / MAX | p.4 §5.5 | `ICC Total supply current VO = 0, No load 6 16 mA` |
| 出力電圧振幅 | **規定なし**（この版で削除） | — | — | p.11 改訂履歴 | "Removed Maximum peak-to-peak output voltage swing, Small-signal differential-voltage amplification, Maximum output-swing bandwidth, Output impedance, Crosstalk attenuation" |
| 参考: AVD の試験条件の出力電圧 | VO = ±10 V で AVD min 15 V/mV（25°C, RL ≥ 600 Ω）／min 25 V/mV（25°C, RL ≥ 2 kΩ）。全温度: min 10 / min 15 V/mV | ±15 V | MIN | p.4 §5.5 | `RL ≥ 600Ω, VO = ±10 V TA = 25°C 15 50` / `RL ≥ 2kΩ, VO±10 V TA = 25°C 25 100`（振幅の規定ではない） |
| 同相入力電圧範囲 | min ±12 V / typ ±13 V | ±15 V、25°C | MIN / TYP | p.4 §5.5 | `VICR Common-mode input-voltage range ±12 ±13 V` |
| 入力電圧（絶対最大） | −15〜+15 V（各入力） | — | MIN / MAX | p.3 §5.1 | `Input voltage, either input(2) (3) –15 +15 V`、注(3) "The magnitude of the input voltage must never exceed the magnitude of the supply voltage." |
| 差動入力（絶対最大） | 電圧値での規定なし。入力電流 ±10 mA、差動 約 0.6 V 超で過大電流の注記 | — | MIN / MAX | p.3 §5.1 | `Input current(4) –10 10 mA`、注(4) "Excessive input current flows if a differential input voltage in exceeding approximately 0.6V is applied between the inputs, unless some limiting resistance is used." |
| 入力保護ダイオード | 「input-protection diodes」を持つ旨の記述 | — | —（本文） | p.1, p.6 | "…high slew rate, input-protection diodes, and output short-circuit protection." |
| 出力短絡電流 | typ 38 mA | ±15 V、25°C | TYP | p.4 §5.5 | `IOS Output short-circuit current 38 mA` |
| 出力短絡時間（絶対最大） | Unlimited | — | — | p.3 §5.1 | `Duration of output short circuit(5) Unlimited`、注(5) "The output can be shorted to ground or either power supply. Temperature and/or supply voltages must be limited to the maximum dissipation rating is not exceeded." |

探したが DS に無かった項目: 出力電圧振幅の規定値（表・グラフとも無い。Typical Characteristics は雑音 2 枚と Output Swing Bandwidth vs Temperature（VCC = ±10 V）だけ）、差動入力電圧の絶対最大（電圧値）、出力電流の規定（短絡電流以外）、±15 V 以外の電源での電気的特性。

---

## 2. NJM5532（NJM5532DD）

`NJR_NJM5532.pdf`（20250306）。ページ上部に "NJM5532D is the NRND product."。表の既定条件は「V+/V-=±15V, Ta=25˚C, unless otherwise noted.」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | ±3〜±22 V | Ta = 25°C | RATING | p.2 | `RECOMMENDED OPERATING VOLTAGE (Ta=25°C) Supply Voltage V+/V- ±3~±22 V` |
| 電源電圧（特長） | ±3〜±22 V | — | — | p.1 | `Operating Voltage ±3V~±22V` |
| 電源電圧（絶対最大） | ±22 V | Ta = 25°C | RATING | p.2 | `Supply Voltage V+/V- ±22 V` |
| 静止電流 | typ 9 mA / max 16 mA（パッケージ全体か 1 回路かの記載なし） | ±15 V、RL = ∞、25°C | TYP / MAX | p.2 | `Supply Current ICC RL=∞ - 9 16 mA` |
| 出力電圧振幅 1 | min ±12 V / typ ±13 V | ±15 V、RL ≥ 600 Ω、25°C | MIN / TYP | p.2 | `Maximum Output Voltage1 VOM1 RL≥600Ω ± 12 ± 13 - V` |
| 出力電圧振幅 2 | min ±15 V / typ ±16 V | **±18 V**、RL ≥ 600 Ω、25°C | MIN / TYP | p.2 | `Maximum Output Voltage2 VOM2 RL≥600Ω, V+/V-=±18V ± 15 ± 16 - V` |
| 出力（特長） | 600 Ω に 10 Vrms typ | — | — | p.1 | `Output Drive Capability 600Ω,10Vrms typ.` |
| 参考: 電力帯域の試験条件 | VO = ±10 V で 140 kHz typ／VO = ±14 V, RL = 600 Ω, ±18 V で 100 kHz typ | 既定 ±15 V | TYP | p.2 | `Power Bandwidth WPG VO=±10V - 140 - kHz` / `WPG VO=±14V, RL=600Ω, V+/V-=±18V - 100 - kHz` |
| グラフ: 最大出力電圧 vs 電源電圧 | ±12 V で **約 +11 V / 約 −11 V**（目読み。縦軸目盛 5 V 刻み、2 kΩ と 600 Ω の線はほぼ重なる） | RL = 2 kΩ（題）、図中に RL=2kΩ と RL=600Ω の 2 線、Ta = 25°C | typ（グラフ） | p.4 | 図題 "Maximum Output Voltage vs. Supply Voltage RL=2kΩ, Ta=25ºC" |
| グラフ: 最大出力電圧 vs 温度 | 25°C で 約 +13.7 V / 約 −13 V（目読み） | ±15 V、RL = 600 Ω | typ（グラフ） | p.4 | 図題 "Maximum Output Voltage vs. Temperature V+/V-=±15V, RL=600Ω" |
| グラフ: 最大出力電圧 vs 負荷抵抗 | 1 kΩ 以上で約 +14 V / 約 −14 V に飽和（目読み） | ±15 V、Ta = 25°C | typ（グラフ） | p.3 | 図題 "Maximum Output Voltage vs. Load Resistance V+/V-=±15V, Ta=25ºC" |
| グラフ: 最大出力電圧振幅 vs 周波数 | 低域で 約 26 Vpp（目読み） | ±15 V、Ta = 25°C | typ（グラフ） | p.3 | 図題 "Maximum Output Voltage Swing vs. Frequency V+/V-=±15V, Ta=25ºC" |
| 同相入力電圧範囲 | min ±12 V / typ ±13 V | ±15 V、25°C | MIN / TYP | p.2 | `Common Mode Input Voltage Range VICM ± 12 ± 13 - V` |
| 同相入力電圧（絶対最大） | V+/V- | — | RATING | p.2 | `Common Mode Input Voltage Range VICM V+/V- V` |
| 差動入力（絶対最大） | ±0.5 V | Ta = 25°C | RATING | p.2 | `Differential Input Voltage Range VID ±0.5 V` |
| 入力保護 | 入力間に逆並列ダイオード（p.1 等価回路）。ボルテージフォロワでは電源投入時の入力ダイオード破壊を避けるため、非反転入力に電流制限抵抗（図は 1 kΩ） | — | —（本文・図） | p.1 EQUIVALENT CIRCUIT、p.5 NOTICE・Fig.1 | "When used in voltage follower circuit, put a current limit resistor into non-inverting input terminal in order to avoid inside input diode destruction when the power supply is turned on. ( ref.Fig.1 )" 〔2026-09-25 照合で追加〕 |
| V+ 開放時の過電流 | V+ が開放で、入力と V− の電位差が大きく、入力に 1 kΩ 以上の抵抗が無く、V+ 端子が低インピーダンスにつながっていると、内部の寄生回路で過電流が流れ焼損しうる。対策は SBD の挿入（Fig.4-1/4-2）か 1 kΩ 以上の入力抵抗（Fig.5） | — | —（本文） | p.6 Countermeasure to Excess Current by Parasitic Circuit | "When the NJM5532 V+ is open (Fig.2), the NJM5532 may be burnt flowing the excess current by internal parasitic circuit(Fig.3)." / "Between input terminal and V- voltage difference is higher." / "Input terminal has no resistance of 1kΩ or more." / "V+ terminal is connected with low impedance." 〔2026-09-25 照合で追加〕 |
| 出力短絡電流 | typ 38 mA | ±15 V、25°C | TYP | p.2 | `Short Circuit Output Current IOS - 38 - mA` |

探したが DS に無かった項目: 出力短絡の継続時間の規定、全温度での出力振幅の規定値（温度はグラフのみ）、静止電流がパッケージ全体か 1 回路かの明記。 〔2026-09-25 照合で訂正〕

---

## 3. NJM4580（NJM4580DD）

`NJR_NJM4580.pdf`（20250303）。ページ上部に "NJM4580D / NJM4580L are the NRND products."。表の既定条件は「V+/V-=±15V, Ta=25°C, unless otherwise noted.」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | min ±2 V / max ±18 V | Ta = 25°C | MIN / MAX | p.2 | `Supply Voltage V+/V- ±2 - ±18 V` |
| 電源電圧（特長） | ±2〜±18 V | — | — | p.1 | `Operating Voltage ±2V~±18V` |
| 電源電圧（絶対最大） | ±18 V | Ta = 25°C | RATING | p.2 | `Supply Voltage V+/V- ±18 V` |
| 静止電流 | typ 6 mA / max 9 mA（行に条件記載なし。パッケージ全体か 1 回路かの記載なし） | ±15 V、25°C（表の既定） | TYP / MAX | p.2 | `Supply Current ICC - 6 9 mA` |
| 出力電圧振幅 | min ±12 V / typ ±13.5 V | ±15 V、RL ≥ 2 kΩ、25°C | MIN / TYP | p.2 | `Maximum Output Voltage VOM RL≥2kΩ ±12 ±13.5 - V` |
| グラフ: 最大出力電圧 vs 電源電圧 | ±12 V で **約 +10.8 V / 約 −10.8 V**（目読み。縦軸の細目盛 2 V） | RL = 2 kΩ、Ta = 25°C | typ（グラフ） | p.4 | 図題 "Maximum Output Voltage vs. Supply Voltage RL=2kΩ, Ta=25ºC" |
| グラフ: 最大出力電圧 vs 負荷抵抗 | 2 kΩ で 約 +14 V / 約 −13.7 V（目読み） | ±15 V、Ta = 25°C | typ（グラフ） | p.3 | 図題 "Maximum Output Voltage vs. Load Resistance V+/V-=±15V, Ta=25ºC" |
| グラフ: 最大出力電圧 vs 温度 | 25°C で 約 +13.7 V / 約 −13.2 V（目読み） | ±15 V、RL = 2 kΩ | typ（グラフ） | p.4 | 図題 "Maximum Output Voltage vs. Temperature V+/V-=±15V, RL=2kΩ" |
| グラフ: 最大出力電圧 vs 出力電流 | 1〜10 mA で 約 +14 V / 約 −13.5 V、100 mA で 約 +4.5 V / 約 −10.5 V（目読み） | ±15 V、Ta = 25°C | typ（グラフ） | p.3 | 図題 "Maximum Output Voltage vs. Output Current V+/V-=±15V, Ta=25ºC" |
| グラフ: 最大出力電圧 vs 周波数 | 低域で 約 27.5 Vpp（目読み） | ±15 V、RL = 2 kΩ、Ta = 25°C | typ（グラフ） | p.3 | 図題 "Maximum Output Voltage vs. Frequency V+/V-=±15V, RL=2kΩ, Ta=25ºC" |
| 同相入力電圧範囲 | min ±12 V / typ ±13.5 V | ±15 V、25°C | MIN / TYP | p.2 | `Common Mode Input Voltage Range VICM ±12 ±13.5 - V` |
| 入力電圧（絶対最大） | ±15 V（Note1） | — | RATING | p.2 | `Input Voltage VICM ±15 (Note1) V`、"(Note1) For supply voltage less than ±15V, the absolute maximum input voltage is equal to supply voltage." |
| 差動入力（絶対最大） | ±30 V（Note1 付き） | — | RATING | p.2 | `Differential Input Voltage VID ±30 (Note1) V` |

探したが DS に無かった項目: 出力短絡電流・出力短絡時間の規定（表に無い。出力電流はグラフのみ）、入力保護ダイオードの記述、全温度での出力振幅の規定値、静止電流の回路数の明記。

---

## 4. OPA2134（OPA2134PA）

`TI_OPA2134.pdf`（SBOS058B, REVISED NOVEMBER 2024）。表の既定条件は「at TA = 25°C, VS = ±15V, RL = 2kΩ connected to midsupply, and VCM = VOUT = midsupply (unless otherwise noted)」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | Dual: min ±2.5 / nom ±15 / max ±18 V、Single: 5 / 30 / 36 V | — | MIN / NOM / MAX | p.5 §5.3 | `Dual supply ±2.5 ±15 ±18` / `Single supply 5 30 36` |
| 電源電圧（絶対最大） | 36 V（(V+) – (V–)） | — | MAX | p.5 §5.1 | `VS Supply voltage, (V+) – (V–) Single supply 36 V` |
| 静止電流 | typ 4 mA / max 5 mA（**per amplifier**） | ±15 V、IO = 0 mA、25°C | TYP / MAX | p.8 §5.7 | `IQ Quiescent current (per amplifier) IO = 0mA 4 5 mA` |
| 出力電圧振幅（RL = 10 kΩ） | 正側 (V+) – 1.2 V、負側 (V–) + 0.5 V（レール基準）。typ 値なし | ±15 V、RL = 10 kΩ、25°C | 正側は MIN 列位置（左寄せ）、負側は MAX 列位置（右寄せ）。1 セルにまたがる表記 | p.8 §5.7 | `VO Voltage output RL = 10kΩ Positive (V+) – 1.2` / `Negative (V–) + 0.5` |
| 出力電圧振幅（RL = 2 kΩ） | 正側 (V+) – 1.5 V、負側 (V–) + 1.2 V（レール基準）。typ 値なし | ±15 V、RL = 2 kΩ、25°C | 同上 | p.8 §5.7 | `RL = 2kΩ Positive (V+) – 1.5` / `Negative (V–) + 1.2` |
| 参考: AOL の試験条件の出力範囲 | RL = 10 kΩ: –14.5 V ≤ VO ≤ 13.8 V、RL = 2 kΩ: –13.8 V ≤ VO ≤ 13.5 V で AOL min 104 dB | ±15 V、25°C | MIN | p.7 §5.7 | `RL = 10kΩ, –14.5V ≤ VO ≤ 13.8V 104 120` / `RL = 2kΩ, –13.8V ≤ VO ≤ 13.5V 104 120`（振幅の規定ではない） |
| 参考: Headroom | typ 21.3 dBu | THD < 0.01%、RL = 2 kΩ、"VS = 18V"（原文どおり）。**DS 内の食い違い:** p.13 §6.2.1 と p.9 Figure 5-4 は VS = ±18 V・THD+N < 0.01 % で 11.7 Vrms = 23.6 dBu。表の 21.3 dBu（= 9.0 Vrms）とは 2.3 dB 違う。表の "VS = 18V" の意味（±18 V か 18 V 単電源か）は DS から決められない | TYP | p.7 §5.7、p.13 §6.2.1、p.9 Figure 5-4 | `Headroom(1) THD < 0.01%, RL = 2kΩ, VS = 18V 21.3 dBu`、注(1) "dBu = 20 × log (Vrms / 0.7746) where Vrms is the maximum output voltage for which THD+Noise is less than 0.01%." / p.13 "…maximum allowable output voltage level of 11.7Vrms (THD+Noise < 0.01%), have a headroom specification of 23.6dBu. See Figure 5-4." / Figure 5-4 凡例 "VS = ±18V, RL = 2kΩ, f = 1kHz" "OPA134 – 11.7Vrms" 〔2026-09-25 照合で訂正〕 |
| 本文の記述 | レールから 1 V 以内 | — | —（本文） | p.13 §6.1 | "the OPA134 has a wide output swing, to within 1V of the rails" |
| グラフ: 最大出力電圧 vs 周波数 | 低域で ±15 V: 約 27.5 Vpp、±5 V: 約 8.5 Vpp、±2.5 V: 約 3.5 Vpp（目読み） | RL = 2 kΩ（ページ既定）、25°C | typ（グラフ） | p.11 Figure 5-13 | "Maximum output voltage without slew-rate induced distortion" |
| 同相入力電圧範囲 | min (V–) + 2.5 V / typ ±13 V / max (V+) – 3.5 V | ±15 V、25°C | MIN / TYP / MAX | p.7 §5.7 | `VCM Common-mode voltage (V–) + 2.5 ±13 (V+) – 3.5 V` |
| 入力電圧（絶対最大） | (V–) – 0.5 〜 (V+) + 0.5 V、入力電流 ±10 mA | — | MIN / MAX | p.5 §5.1 | `Input voltage(2) (V–) – 0.5 (V+) + 0.5 V` / `Input current(2) ±10 mA`、注(2) "Input pins are diode-clamped to the power-supply rails. Input signals that can swing more than 0.5V beyond the supply rails must be current limited to 10mA or less." |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 出力短絡電流 | Sourcing typ 36 mA / Sinking typ –30 mA | ±15 V、25°C | TYP | p.8 §5.7 | `ISC Short-circuit current Sourcing 36` / `Sinking –30 mA` |
| 出力電流制限（本文） | 約 36 mA 吐き / –30 mA 吸い（25°C）、温度上昇で低下 | — | —（本文） | p.15 §6.2.5 | "Output current is limited by internal circuitry to approximately sourcing 36mA and sinking –30mA at 25°C. The limit current decreases with increasing temperature, as shown in Figure 5-19." |
| 出力短絡（絶対最大） | Continuous（GND へ、1 パッケージ 1 回路） | — | — | p.5 §5.1 | `ISC Output short-circuit(3) Continuous`、注(3) "Short-circuit to ground, one amplifier per package." |

探したが DS に無かった項目: 出力振幅の typ 値・全温度での規定値、差動入力電圧の絶対最大、±12 V での規定・グラフ（Figure 5-13 は ±15/±5/±2.5 V のみ）。改訂履歴 p.21 に "Deleted old Figure 20, Output Voltage Swing vs Output Current" とあり、出力振幅 vs 出力電流のグラフはこの版に無い。

---

## 5. OPA1656（OPA1656ID）

`TI_OPA1656.pdf`（SBOS901C, REVISED SEPTEMBER 2022）。**電気的特性表の既定条件は ±18 V**:「at TA = 25°C, VS = ±18 V, RL = 2 kΩ, and VCM = VOUT = VS/2 (unless otherwise noted)」。Typical Characteristics の既定は「VS = ±15 V, RL = 2 kΩ」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | Dual ±2.25〜±18 V、Single 4.5〜36 V | — | MIN / MAX | p.4 §6.3 | `Single supply 4.5 36` / `Dual supply ±2.25 ±18` |
| 電源電圧（絶対最大） | 40 V（(V+) – (V–)） | — | MAX | p.4 §6.1 | `Supply voltage, VS = (V+) – (V–) 40 V` |
| 静止電流 | typ 3.9 mA / max 4.6 mA（**per channel**）。全温度 max 5.0 mA | IO = 0 A、VS = ±2.25〜±18 V、25°C／TA = –40〜+125°C（設計・特性評価による） | TYP / MAX | p.7 §6.6 | `IQ Quiescent current (per channel) IO = 0 A, VS = ±2.25 V to ±18 V 3.9 4.6` / `IO = 0 A, TA = –40°C to +125°C(2) 5.0 mA` |
| 出力電圧振幅 | (V–) + 0.25 V 〜 (V+) – 0.25 V（レール基準）。typ 値なし | **±18 V**、RL = 2 kΩ（表の既定）、25°C | MIN 列 (V–)+0.25 / MAX 列 (V+)–0.25 | p.7 §6.6 | `VO Voltage output (V–) + 0.25 (V+) – 0.25 V` |
| 参考: AOL の試験条件の出力範囲 | RL = 600 Ω: (V–) + 1.3 V ≤ VO ≤ (V+) – 1.3 V、RL = 2 kΩ: (V–) + 0.5 V ≤ VO ≤ (V+) – 0.5 V で AOL min 134 dB | ±18 V、25°C | MIN | p.6 §6.6 | `(V–) + 1.3 V ≤ VO ≤ (V+) – 1.3 V RL = 600 Ω 134 150` / `(V–) + 0.5 V ≤ VO ≤ (V+) – 0.5 V RL = 2 kΩ 134 154`（振幅の規定ではない） |
| 本文の記述 | 2 kΩ でレールから 250 mV 以内 | — | —（本文） | p.1 | "offering rail-to-rail output swing to within 250 mV of the power supplies with a 2‑kΩ load" |
| グラフ: 出力電圧 vs 出力電流（吐き／吸い） | 0 mA で縦軸 18 V／–18 V から始まる曲線（25°C で 吐き 約 90 mA、吸い 約 100 mA で急落。目読み） | ページ見出しの既定は VS = ±15 V だが、**図中に電源電圧の表記なし**、曲線は ±18 V 相当の位置から始まる | typ（グラフ） | p.13 Figure 6-32, 6-33 | 図題 "Output Voltage vs Output Current (Sourcing)" / "(Sinking)" |
| グラフ: 最大出力電圧 vs 周波数 | 低域で VS = ±18 V の線が 約 36、±15 V の線が 約 30（縦軸ラベルは "Output Voltage (VP)"。目読み） | RL = 2 kΩ（ページ既定） | typ（グラフ） | p.8 Figure 6-4 | 凡例 "Vs=±18 V / Vs=±15 V / Vs=±2.25 V" |
| グラフ: THD+N Ratio vs Output Amplitude | 6 本（G = ±1、600 Ω / 2 kΩ / 10 kΩ）。約 7〜8 Vrms から上がり始め、10 Vrms 付近で急増（目読み。横軸 "Output Amplitude (VRMS)"） | ページ見出し VS = ±15 V, RL = 2 kΩ | typ（グラフ） | p.9 Figure 6-8 | ページ見出し "VS = ±15 V, RL = 2 kΩ" 〔2026-09-25 照合で追加〕 |
| 同相入力電圧範囲 | (V–) 〜 (V+) – 2.25 V | ±18 V、25°C | MIN / MAX | p.6 §6.6 | `VCM Common-mode voltage range (V–) (V+) – 2.25 V` |
| 入力電圧（絶対最大） | (V–) – 0.5 〜 (V+) + 0.5 V、入力電流 ±10 mA | — | MIN / MAX | p.4 §6.1 | `Input (V–) – 0.5 (V+) + 0.5 V` / `Input (all pins except power-supply pins) –10 10 mA` |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 入力保護（本文） | ESD 用の current-steering diodes が入出力ピンから内部電源線へ（通常動作では非動作） | — | —（本文） | p.16 §7.3.2 | "protection circuitry involves several current-steering diodes connected from the input and output pins and routed back to the internal power-supply lines … This protection circuitry is intended to remain inactive during normal circuit operation." |
| 出力短絡電流 | typ ±100 mA（1 チャンネルずつ） | ±18 V、25°C | TYP | p.7 §6.6 | `ISC Short-circuit current(4) ±100 mA`、注(4) "One channel at a time." |
| 出力短絡（絶対最大） | Continuous（VS/2 へ、1 パッケージ 1 回路） | — | — | p.4 §6.1 | `Output short-circuit(2) Continuous`、注(2) "Short-circuit to VS / 2 (groundinsymmetrical dual-supply setups), one amplifier per package." |

探したが DS に無かった項目: ±15 V・±12 V での出力振幅の規定値（表は ±18 V のみ）、出力振幅の typ 値・全温度での規定値、差動入力電圧の絶対最大、入力間の保護ダイオードの記述。

---

## 6. OPA2604（OPA2604AQ）

`TI_OPA2604.pdf`（SBOS006A, REVISED DECEMBER 2015）。表の既定条件は「at TA = 25°C, VS = ±15 V (unless otherwise noted)」。
**型番末尾**: DS の注文情報（p.24）にあるのは `OPA2604AP`（PDIP）と `OPA2604AU`（SOIC）系だけで、`AQ` は DS に無い。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | min ±4.5 / nom ±15 / max ±24 V | — | MIN / NOM / MAX | p.4 §6.3 | `V+, V– Power supply voltage ±4.5 ±15 ±24 V` |
| 電源電圧（電気的特性表） | Operating voltage range ±4.5〜±24 V、Specified operating voltage ±15 V | — | MIN / MAX、TYP | p.5 §6.5 | `Operating voltage range ±4.5 ±24 V` / `Specified operating voltage ±15 V` |
| 電源電圧（絶対最大） | ±25 V | — | MAX | p.4 §6.1 | `Power supply voltage ±25 V` |
| 静止電流 | typ ±10.5 mA / max ±12 mA（**total both amplifiers**。原文も ± 付き） | ±15 V、IO = 0、25°C | TYP / MAX | p.5 §6.5 | `Current, total both amplifiers IO = 0 ±10.5 ±12 mA` |
| 出力電圧振幅 | min ±11 V / typ ±12 V | ±15 V、RL = 600 Ω、25°C | MIN / TYP | p.5 §6.5 | `Voltage output RL = 600 Ω ±11 ±12 V` |
| 出力電流 | typ ±35 mA | ±15 V、VO = ±12 V、25°C | TYP | p.5 §6.5 | `Current output VO = ±12 V ±35 mA` |
| グラフ: 最大出力電圧振幅 vs 周波数 | 低域（10 kHz〜約 300 kHz）で約 24 Vp-p（目読み。負荷の表記なし） | VS = ±15 V、25°C | typ（グラフ） | p.8 Figure 15 | 図題 "Maximum Output Voltage Swing vs Frequency"、図中 "VS = ±15V" 〔2026-09-25 照合で訂正〕 |
| 同相入力電圧範囲 | min ±12 V / typ ±13 V | ±15 V、25°C | MIN / TYP | p.5 §6.5 | `Common-mode input range ±12 ±13 V` |
| 入力電圧（絶対最大） | (V–)–1 〜 (V+)+1 V | — | MIN / MAX | p.4 §6.1 | `Input voltage (V–)–1 (V+)+1 V` |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 出力短絡電流 | typ ±40 mA | ±15 V、25°C | TYP | p.5 §6.5 | `Short circuit current ±40 mA` |
| 出力短絡（絶対最大） | Continuous（GND へ） | — | — | p.4 §6.1 | `Output short-circuit to ground Continuous` |

探したが DS に無かった項目: 型番 `AQ` のパッケージ、出力振幅の全温度での規定値、±15 V 以外での出力振幅の規定・グラフ、差動入力電圧の絶対最大、入力保護ダイオードの記述。

---

## 7. LME49860（LME49860NA）

`TI_LME49860.pdf`（SNAS389C, REVISED APRIL 2013）。表の既定条件は「The following specifications apply for VS = ±18V and ±22V, RL = 2kΩ, RSOURCE = 10Ω, fIN = 1kHz, TA = 25°C, unless otherwise specified.」。
**列の形式が min/typ/max ではない**: 「Typical (2)」と「Limit (3)」の 2 列で、Limit の単位欄に (min)/(max) が付く。注(2) "Typical specifications are specified at +25ºC and represent the most likely parametric norm." 注(3) "Tested limits are ensured to AOQL (Average Outgoing Quality Level)."

| 項目 | 値 | 条件（電源・負荷・温度） | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（動作） | ±2.5 V ≤ VS ≤ ±22 V | — | OPERATING RATINGS | p.3 | `Supply Voltage Range ±2.5V ≤ VS ≤ ±22V` |
| 電源電圧（絶対最大） | 46 V（V+ – V–） | — | — | p.3 | `Power Supply Voltage (VS = V+ - V-) 46V` |
| 静止電流 | ±18 V: typ 10.2 mA、±22 V: typ 10.5 mA / Limit 13 mA (max)（**Total**） | IOUT = 0 mA、25°C | Typical / Limit | p.4 | `IS Total Quiescent Current IOUT = 0mA VS = ±18V 10.2` / `VS = ±22V 10.5 13 mA (max)` |
| 出力電圧振幅（RL = 600 Ω） | ±18 V: typ ±16.7 V、±22 V: typ ±20.4 V / **Limit ±19.0 V (min)** | 25°C | Typical / Limit | p.4 | `VOUTMAX Maximum Output Voltage Swing RL = 600Ω VS = ±18V ±16.7` / `VS = ±22V ±20.4 ±19.0 V (min)` |
| 出力電圧振幅（RL = 2 kΩ） | ±18 V: typ ±17.0 V、±22 V: typ ±21.0 V（Limit なし） | 25°C | Typical | p.4 | `RL = 2kΩ VS = ±18V ±17.0` / `VS = ±22V ±21.0` |
| 出力電圧振幅（RL = 10 kΩ） | ±18 V: typ ±17.1 V、±22 V: typ ±21.2 V（Limit なし） | 25°C | Typical | p.4 | `RL = 10kΩ VS = ±18V ±17.1` / `VS = ±22V ±21.2` |
| グラフ: 出力電圧 vs 負荷抵抗（±15 V） | 600 Ω 約 9.9 Vrms、2 kΩ 約 10.1 Vrms、10 kΩ 約 10.2 Vrms（目読み） | VCC = 15 V, VEE = –15 V、THD+N = 1% | typ（グラフ） | p.20 Figure 95 | 図題 "Output Voltage vs Load Resistance VCC = 15V, VEE = –15V THD+N = 1%" |
| グラフ: 出力電圧 vs 負荷抵抗（**±12 V**） | 600 Ω 約 7.8 Vrms、2 kΩ 約 7.9 Vrms、10 kΩ 約 8.0 Vrms（目読み） | VCC = 12 V, VEE = –12 V、THD+N = 1% | typ（グラフ） | p.20 Figure 96 | 図題 "Output Voltage vs Load Resistance VCC = 12V, VEE = –12V THD+N = 1%" |
| グラフ: THD+N vs Output Voltage（**±12 V**） | Figure 4 = 2 kΩ、Figure 8 = 600 Ω、Figure 12 = 10 kΩ。2 kΩ で約 7〜8 V から急増（目読み。横軸の単位は "V" のみで rms か peak かの表記なし） | VCC = 12 V, VEE = –12 V | typ（グラフ） | p.5 Figure 4・8、p.6 Figure 12 | 図題 "THD+N vs Output Voltage VCC = 12V, VEE = –12V RL = 2kΩ" ほか 〔2026-09-25 照合で追加〕 |
| グラフ: 出力電圧 vs 総電源電圧 | RL = 2 kΩ / 600 Ω / 10 kΩ の 3 枚（THD+N = 1%、縦軸 VRMS）。総電源 24 V で約 8 Vrms（目読み） | THD+N = 1% | typ（グラフ） | p.21 Figure 99–101 | 図題 "Output Voltage vs Total Power Supply Voltage RL = 2kΩ, THD+N = 1%" ほか |
| 同相入力電圧範囲 | ±18 V: typ +17.1 / –16.9 V、Limit (V+) – 2.0 / (V-) + 2.0 V (min)。±22 V: typ +21.0 / –20.8 V、Limit 同 | 25°C | Typical / Limit | p.4 | `VIN-CM Common-Mode Input Voltage Range VS = ±18V +17.1 (V+) – 2.0 V (min) –16.9 (V-) + 2.0 V (min)` |
| 入力電圧（絶対最大） | (V-) – 0.7 V 〜 (V+) + 0.7 V | — | — | p.3 | `Input Voltage (V-) - 0.7V to (V+) + 0.7V` |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 出力電流 | RL = 600 Ω: ±20 V で typ ±31 mA、±22 V で typ ±37 mA / Limit ±30 mA (min) | 25°C | Typical / Limit | p.4 | `IOUT Output Current RL = 600Ω VS = ±20V ±31` / `VS = ±22V ±37 ±30 mA (min)` |
| 瞬時短絡電流 | typ +53 / –42 mA | 表の既定（±18 V / ±22 V）、25°C | Typical | p.4 | `IOUT-CC Instantaneous Short Circuit Current +53 –42 mA` |
| 出力短絡（絶対最大） | Continuous（GND へ、パッケージ内の何回路でも） | — | — | p.3 | `Output Short Circuit (4) Continuous`、注(4) "Amplifier output connected to GND, any number of amplifiers within a package." |

探したが DS に無かった項目: **±15 V・±12 V での出力振幅の規定値**（表は ±18 V と ±22 V だけ。±15/±12 V はグラフのみ: THD+N = 1% の Vrms 表記の Figure 95/96 と、±12 V の THD+N vs Output Voltage の Figure 4・8・12）、±18 V での出力振幅の Limit、全温度での出力振幅、差動入力電圧の絶対最大、入力保護ダイオードの記述。 〔2026-09-25 照合で訂正〕

---

## 8. OPA1652（「OPA1652」DIP 化モジュール）

`TI_OPA1652.pdf`（SBOS477B, REVISED DECEMBER 2016）。表は「6.6 Electrical Characteristics: VS = ±15 V」「at TA = 25°C, RL = 2 kΩ, and VCM = VOUT = midsupply, unless otherwise noted」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | 4.5 (±2.25) 〜 36 (±18) V | — | MIN / MAX | p.5 §6.3 | `Supply voltage 4.5 (±2.25) 36 (±18) V` |
| 電源電圧（電気的特性表） | Specified voltage ±2.25〜±18 V | — | MIN / MAX | p.7 §6.6 | `VS Specified voltage ±2.25 ±18 V` |
| 電源電圧（絶対最大） | 40 V（(V+) – (V–)） | — | MAX | p.5 §6.1 | `Supply voltage, VS = (V+) – (V–) 40 V` |
| 静止電流 | typ 2 mA / max 2.5 mA（**per channel**）。全温度 max 2.8 mA | ±15 V、IOUT = 0 A、25°C／TA = –40〜85°C（設計・特性評価による） | TYP / MAX | p.7 §6.6 | `IQ Quiescent current (per channel) IOUT = 0 A 2 2.5 mA` / `IOUT = 0 A, TA = –40°C to 85°C (2) 2.8 mA` |
| 出力電圧振幅 | (V–) + 0.8 V 〜 (V+) – 0.8 V（レール基準）。typ 値なし | ±15 V、RL = 2 kΩ、25°C | MIN 列 (V–)+0.8 / MAX 列 (V+)–0.8 | p.7 §6.6 | `VOUT Voltage output RL = 2 kΩ (V–) + 0.8 (V+) – 0.8 V` |
| 本文の記述 | 2 kΩ でレールから 800 mV 以内、出力 ±30 mA | — | —（本文） | p.1 | "The OPA1652 and OPA1654 op amps offer rail-to-rail output swing to within 800 mV with a 2-kΩ load … These devices also have a high output drive capability of ±30 mA." |
| グラフ: 最大出力電圧 vs 周波数 | 低域で VS = ±15 V の線が 約 14.7（縦軸ラベル "Output Voltage (V)"。目読み） | RL = 2 kΩ（ページ既定）、図中 VS = ±15 V / ±2.25 V | typ（グラフ） | p.8 Figure 4 | 図題 "Maximum Output Voltage vs Frequency" |
| グラフ: 出力電圧 vs 出力電流 | 縦軸 "Output Volage Swing (V)"（原文の綴り）は ±40 V 目盛で、0 mA 付近で約 +35 / 約 –35 を示す。ページ既定 VS = ±15 V と整合しない値で、図中に電源電圧の表記なし（目読み。値としては採れない） | ページ既定 ±15 V、RL = 2 kΩ | typ（グラフ） | p.12 Figure 27 | 図題 "Output Voltage vs Output Current" |
| 同相入力電圧範囲 | (V–) + 0.5 V 〜 (V+) – 2 V | ±15 V、25°C | MIN / MAX | p.7 §6.6 | `VCM Common-mode voltage range (V–) + 0.5 (V+) – 2 V` |
| 入力電圧（絶対最大） | (V–) – 0.5 〜 (V+) + 0.5 V、入力電流 ±10 mA | — | MIN / MAX | p.5 §6.1 | `Input (V–) – 0.5 (V+) + 0.5 V` / `Input (all pins except power-supply pins) –10 10 mA` |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 入力保護（本文） | 入力間に back-to-back ダイオード。G = 1 など低利得で入力が速く動くと順バイアスになりうるので、入力信号電流を 10 mA 以下に制限（入力直列抵抗か帰還抵抗で）。ESD 用の current-steering diodes の説明は別に §7.3.3 | — | —（本文） | p.15 §7.3.2・Figure 36 | "The input terminals of the OPA1652 and OPA1654 are protected from excessive differential voltage with back-to-back diodes, as Figure 36 illustrates. … in low-gain or G = 1 circuits, fast ramping input signals can forward bias these diodes … the input signal current must be limited to 10 mA or less." 〔2026-09-25 照合で追加〕 |
| 出力電流 | 表では「See Typical Characteristics」 | — | — | p.7 §6.6 | `IOUT Output current See Typical Characteristics mA` |
| 出力短絡電流 | typ ±50 mA（1 チャンネルずつ） | ±15 V、25°C | TYP | p.7 §6.6 | `ISC Short-circuit current (3) ±50 mA`、注(3) "One channel at a time." |
| 出力短絡（絶対最大） | Continuous（VS/2 へ、1 パッケージ 1 回路） | — | — | p.5 §6.1 | `Output short-circuit (2) Continuous`、注(2) "Short-circuit to VS / 2 (ground in symmetrical dual supply setups), one amplifier per package." |

探したが DS に無かった項目: 出力振幅の typ 値・全温度での規定値、±15 V 以外での出力振幅の規定値、差動入力電圧の絶対最大。 〔2026-09-25 照合で訂正〕

---

## 9. OPA627（OPA627AU を 2 回路 DIP 化）

`TI_OPA627.pdf`（SBOS165C, REVISED JANUARY 2025）。使ったのは **§5.6 OPA627BU, OPA627AU** の表（既定「at TA = 25°C, VS = ±15V, VCM = VOUT = midsupply, and RL = 10kΩ connected to VS / 2 (unless otherwise noted)」）。§5.7（AM/BM/SM）と §5.8（OPA637）は別品種なので使っていない。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | Dual: min ±4.5 / nom ±15 / max ±18 V、Single: 9 / 30 / 36 V | — | MIN / NOM / MAX | p.4 §5.3 | `Single supply 9 30 36` / `Dual supply ±4.5 ±15 ±18` |
| 電源電圧（絶対最大） | Single 36 V、Dual ±18 V | — | MAX | p.4 §5.1 | `Single supply 36` / `Dual supply ±18` |
| 静止電流 | typ 7 mA / max 7.5 mA（**per amplifier**） | ±15 V、IO = 0 mA、25°C | TYP / MAX | p.7 §5.6 | `IQ Quiescent current per amplifier IO = 0mA 7 7.5 mA` |
| 出力電圧振幅（25°C） | min ±11.5 V / typ ±12.3 V | ±15 V、**RL = 1 kΩ**、25°C | MIN / TYP | p.7 §5.6 | `VO Output voltage RL = 1kΩ ±11.5 ±12.3 V` |
| 出力電圧振幅（全温度） | min ±11 V / typ ±11.5 V | ±15 V、RL = 1 kΩ、TA = –25〜+85°C | MIN / TYP | p.7 §5.6 | `TA = –25°C to +85°C ±11 ±11.5` |
| 出力電流 | typ ±30 mA | ±15 V、–10 V < VO < +10 V、25°C | TYP | p.7 §5.6 | `IO Current output –10V < VO < +10V ±30 mA` |
| グラフ: 最大出力電圧 vs 周波数 | OPA627 は 100 kHz〜約 1.5 MHz の平坦部で約 25 Vp-p（目読み。横軸は 100 kHz から。負荷の記載なし） | VS = ±15 V、25°C（ページ既定 "at TA = 25°C and VS = ±15V (unless otherwise noted)"） | typ（グラフ） | p.16 Figure 5-23 | 図題 "Maximum Output Voltage vs Frequency" 〔2026-09-25 照合で訂正〕 |
| 同相入力電圧範囲 | 25°C: min ±11 V / typ ±11.5 V、全温度: min ±10.5 V / typ ±11 V | ±15 V、TA = –25〜+85°C（全温度） | MIN / TYP | p.6 §5.6 | `VCM Common-mode voltage ±11 ±11.5` / `TA = –25°C to +85°C ±10.5 ±11 V` |
| 入力電圧（絶対最大） | Common-mode (V–) – 0.5 〜 (V+) + 0.5 V、入力ピン電流 ±10 mA | — | MIN / MAX | p.4 §5.1 | `Input voltage Common-mode (V–) – 0.5 (V+) + 0.5` / `Input pin current ±10 mA` |
| 差動入力（絶対最大） | (V+) – (V–) | — | MAX | p.4 §5.1 | `Differential (V+) – (V–)` |
| 入力保護（本文） | 入力は +VS + 0.5 V 〜 –VS – 0.5 V まで保護。超えるときは入力電流を制限 | — | —（本文） | p.23 §6.3.7 | "The inputs of the OPA6x7 are protected for voltages from +VS + 0.5V to –VS – 0.5V. If the input voltage can exceed these limits, protect the amplifier by limiting the current into the input pins." |
| 出力短絡電流 | typ ±45 mA | ±15 V、25°C | TYP | p.7 §5.6 | `ISC Short-circuit current ±45 mA` |

探したが DS に無かった項目: 出力短絡の継続時間（§5.1 に項目なし）、±15 V 以外での出力振幅の規定・グラフ、RL = 2 kΩ 以上での出力振幅の規定値（表は 1 kΩ のみ）。

---

## 10. OPA1612（2 回路 8 ピン DIP 化完成基板）

`TI_OPA1612.pdf`（SBOS450C, REVISED AUGUST 2014）。**表の電源条件は範囲**:「6.4 Electrical Characteristics: VS = ±2.25 V to ±18 V」「At TA = +25°C and RL = 2 kΩ, unless otherwise noted. VCM = VOUT = midsupply, unless otherwise noted.」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | 4.5 (±2.25) 〜 36 (±18) V | — | MIN / MAX | p.4 §6.3 | `Supply voltage (V+ – V–) 4.5 (±2.25) 36 (±18) V` |
| 電源電圧（電気的特性表） | Specified voltage ±2.25〜±18 V | — | MIN / MAX | p.6 | `VS Specified voltage ±2.25 ±18 V` |
| 電源電圧（絶対最大） | 40 V | — | MAX | p.4 §6.1 | `Supply voltage VS = (V+) – (V–) 40 V` |
| 静止電流 | typ 3.6 mA / max 4.5 mA（**per channel**）。全温度 max 5.5 mA | IOUT = 0 A、25°C／TA = –40〜+85°C（設計・特性評価による） | TYP / MAX | p.6 | `IQ Quiescent current (per channel) IOUT = 0 A 3.6 4.5 mA` / `IQ over Temperature (3) TA = –40°C to +85°C 5.5 mA` |
| 出力電圧振幅（RL = 10 kΩ） | (V–) + 0.2 V 〜 (V+) – 0.2 V（レール基準）。typ 値なし | VS = ±2.25〜±18 V、RL = 10 kΩ、AOL ≥ 114 dB、25°C | MIN 列 / MAX 列 | p.6 | `VOUT Voltage output RL = 10 kΩ, AOL ≥ 114 dB (V–) + 0.2 (V+) – 0.2 V` |
| 出力電圧振幅（RL = 2 kΩ） | (V–) + 0.6 V 〜 (V+) – 0.6 V（レール基準）。typ 値なし | VS = ±2.25〜±18 V、RL = 2 kΩ、AOL ≥ 110 dB、25°C | MIN 列 / MAX 列 | p.6 | `RL = 2 kΩ, AOL ≥ 110 dB (V–) + 0.6 (V+) – 0.6 V` |
| 本文の記述 | 2 kΩ でレールから 600 mV 以内 | — | —（本文） | p.1 | "The OPA1611 and OPA1612 offer rail-to-rail output swing to within 600 mV with a 2-kΩ load" |
| グラフ: 出力電圧 vs 出力電流 | 25°C の線で、0〜約 45 mA の範囲で約 +14.35〜+14.2 V / 約 –14.3〜–14.2 V（目読み。+85°C の線は負側が約 –14.0 V まで上がる） | VS = ±15 V、"Dual version with both channels driven simultaneously" | typ（グラフ） | p.11 Figure 27 | 図題 "Output Voltage vs Output Current" 〔2026-09-25 照合で訂正〕 |
| グラフ: 最大出力電圧 vs 周波数 | 低域で VS = ±15 V: 約 28.8 Vpp（目読み）。±5 V・±2.25 V の線もある | RL = 2 kΩ（ページ既定） | typ（グラフ） | p.7 Figure 4 | 図中 "Maximum output voltage range without slew-rate induced distortion"、縦軸 "Output Voltage (VPP)" |
| 同相入力電圧範囲 | (V–) + 2 V 〜 (V+) – 2 V | VS = ±2.25〜±18 V、25°C | MIN / MAX | p.5 §6.4 | `VCM Common-mode voltage range (V–) + 2 (V+) – 2 V` |
| 入力電圧（絶対最大） | (V–) – 0.5 〜 (V+) + 0.5 V、入力電流 ±10 mA | — | MIN / MAX | p.4 §6.1 | `Input voltage (V–) – 0.5 (V+) + 0.5 V` / `Input current (all pins except power-supply pins) ±10 mA` |
| 差動入力（絶対最大） | 規定なし（差動入力インピーダンスは typ 20k ‖ 8 Ω ‖ pF） | — | — | p.5 §6.4 | `Differential 20k || 8 Ω || pF` |
| 入力保護（本文） | 入力間に back-to-back ダイオード。G = +1 など低利得で入力が速く動くと順バイアスになりうるので、入力信号電流を 10 mA 以下に制限（入力直列抵抗か帰還抵抗で）。現象の図は Typical Characteristics の Figure 17。ESD 用 steering diodes の説明は別に p.13 | — | —（本文） | p.14 §7.3.4・Figure 31 | "The input terminals of the OPA1611 and the OPA1612 are protected from excessive differential voltage with back-to-back diodes, as Figure 31 shows. … If the input signal is fast enough to create this forward bias condition, the input signal current must be limited to 10 mA or less." 〔2026-09-25 照合で追加〕 |
| 出力電流 | 表では「See Figure 27」 | — | — | p.6 | `IOUT Output current See Figure 27 mA` |
| 出力短絡電流 | typ +55 mA / –62 mA | 25°C | TYP | p.6 | `ISC Short-circuit current +55 mA` / `–62 mA` |
| 出力短絡（絶対最大） | Continuous（VS/2 へ、1 パッケージ 1 回路） | — | — | p.4 §6.1 | `Output short-circuit (2) Continuous`、注(2) "Short-circuit to VS / 2 (ground in symmetrical dual supply setups), one amplifier per package." |

探したが DS に無かった項目: 出力振幅の typ 値・全温度での規定値、差動入力電圧の絶対最大。 〔2026-09-25 照合で訂正〕

---

## 11. LT1364（LT1364CN8）

`AD_LT1364.pdf`（LT1364/LT1365）。表は電源電圧を列（VSUPPLY）で持つ。25°C 表は「TA = 25°C, VCM = 0V unless otherwise noted.」、温度表は ● 付きで 0〜70°C と –40〜85°C の 2 枚。
Note 9: "The LT1364C/LT1365C are guaranteed to meet specified performance from 0°C to 70°C. The LT1364C/LT1365C are designed, characterized and expected to meet specified performance from –40°C to 85°C, but are not tested or QA sampled at these temperatures."

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | 推奨動作条件の節なし。特性は ±2.5 / ±5 / ±15 V で規定 | — | — | p.1 | `Specified at ±2.5V, ±5V, and ±15V` |
| 電源電圧（絶対最大） | 36 V（V+ – V–） | — | — | p.2 | `Total Supply Voltage (V + to V –) ............ 36V` |
| 静止電流 | ±15 V: typ 6.3 / max 7.5 mA、±5 V: typ 6.0 / max 7.2 mA（**Each Amplifier**）。0〜70°C: max 8.7（±15 V）/ 8.4（±5 V）。–40〜85°C: max 9.0 / 8.7 | 25°C／温度範囲 | TYP / MAX、温度表は MAX | p.3、p.4、p.5 | `IS Supply Current Each Amplifier ±15V 6.3 7.5 mA` / `Each Amplifier ±5V 6.0 7.2 mA` |
| 出力電圧振幅（25°C） | ±15 V, RL = 1k: min 13.5 / typ 14.0 ±V。±15 V, RL = 500 Ω: min 13.0 / typ 13.7。±5 V, 500 Ω: 3.5 / 4.1。±5 V, 150 Ω: 3.4 / 3.8。±2.5 V, 500 Ω: 1.3 / 1.7 | VIN = ±40 mV、25°C | MIN / TYP（単位 ±V） | p.3 | `VOUT Output Swing RL = 1k, VIN = ±40mV ±15V 13.5 14.0 ±V` / `RL = 500Ω, VIN = ±40mV ±15V 13.0 13.7 ±V` |
| 出力電圧振幅（0〜70°C） | ±15 V, 1k: min 13.4。±15 V, 500 Ω: min 12.8。±5 V, 500 Ω: 3.4。±5 V, 150 Ω: 3.3。±2.5 V, 500 Ω: 1.2 | VIN = ±40 mV、0°C ≤ TA ≤ 70°C | MIN | p.4 | `VOUT Output Swing RL = 1k, VIN = ±40mV ±15V ● 13.4 ±V` / `RL = 500Ω … ±15V ● 12.8` |
| 出力電圧振幅（–40〜85°C） | ±15 V, 1k: min 13.4。±15 V, 500 Ω: min 12.7。±5 V, 500 Ω: 3.4。±5 V, 150 Ω: 3.2。±2.5 V, 500 Ω: 1.2 | VIN = ±40 mV、–40°C ≤ TA ≤ 85°C（Note 9） | MIN | p.5 | `RL = 1k, VIN = ±40mV ±15V ● 13.4` / `RL = 500Ω, VIN = ±40mV ±15V ● 12.7` |
| 出力（特長） | 150 Ω へ min ±7.5 V | ±15 V | — | p.1 | `±7.5V Minimum Output Swing into 150Ω` |
| グラフ: 出力電圧振幅 vs 電源電圧（レール基準） | **±12 V で**: 正側 RL = 1k 約 V+ – 1.25 V、500 Ω 約 V+ – 1.35 V。負側 1k 約 V– + 1.28 V、500 Ω 約 V– + 1.47 V（目読み） | TA = 25°C、RL = 1k / 500 Ω | typ（グラフ） | p.6 | 図題 "Output Voltage Swing vs Supply Voltage"、縦軸 "OUTPUT VOLTAGE SWING (V)"（V+ / V– からの距離） |
| グラフ: 出力電圧振幅 vs 負荷電流 | VS = ±5 V のみ | VS = ±5V, VIN = 100mV | typ（グラフ） | p.6 | 図題 "Output Voltage Swing vs Load Current" |
| 同相入力電圧範囲（+側） | ±15 V: min 12.0 / typ 13.4 V、±5 V: 2.5 / 3.4、±2.5 V: 0.5 / 1.1 | 25°C | MIN / TYP | p.3 | `Input Voltage Range + ±15V 12.0 13.4 V` |
| 同相入力電圧範囲（–側） | ±15 V: typ –13.2 / max –12.0 V、±5 V: –3.2 / –2.5、±2.5 V: –0.9 / –0.5 | 25°C | **TYP / MAX**（負側は MAX 列が保証値） | p.3 | `Input Voltage Range – ±15V –13.2 –12.0 V` |
| 入力電圧（絶対最大） | ±VS | — | — | p.2 | `Input Voltage ............ ±VS` |
| 差動入力（絶対最大） | ±10 V（**過渡のみ**、Note 2） | — | — | p.2 | `Differential Input Voltage (Transient Only, Note 2) ............ ±10V`、Note 2 "Differential inputs of ±10V are appropriate for transient operation only, such as during slewing. Large, sustained differential inputs will cause excessive power dissipation and may damage the part." |
| 入力保護（本文） | 10 V までの過渡差動入力はクランプ・直列抵抗なしで耐える。持続的な差動入力は電源電流増で破損のおそれ | — | —（本文） | p.9 Input Considerations | "The inputs can withstand transient differential input voltages up to 10V without damage and need no clamping or source resistance for protection. Differential inputs, however, generate large supply currents (tens of mA) as required for high slew rates." |
| 出力電流 | 25°C: ±15 V, VOUT = ±7.5 V で min 50 / typ 60 mA、±5 V, VOUT = ±3.4 V で 23 / 29 mA。0〜70°C: ±15 V, VOUT = ±12.8 V で min 25、±5 V, ±3.3 V で 22。–40〜85°C: ±15 V, ±12.7 V で 25、±5 V, ±3.2 V で 21 | — | MIN / TYP、温度表は MIN | p.3、p.4、p.5 | `IOUT Output Current VOUT = ±7.5V ±15V 50 60 mA` / `VOUT = ±12.8V ±15V ● 25 mA` |
| 出力短絡電流 | 25°C: min 70 / typ 105 mA、0〜70°C: min 55、–40〜85°C: min 50 | ±15 V、VOUT = 0 V, VIN = ±3 V | MIN / TYP、温度表は MIN | p.3、p.4、p.5 | `ISC Short-Circuit Current VOUT = 0V, VIN = ±3V ±15V 70 105 mA` |
| 出力短絡（絶対最大） | Indefinite（Note 3） | — | — | p.2 | `Output Short-Circuit Duration (Note 3) ............ Indefinite`、Note 3 "A heat sink may be required to keep the junction temperature below absolute maximum when the output is shorted indefinitely." |

探したが DS に無かった項目: 推奨動作電源電圧範囲（節が無い）、±12 V での出力振幅の規定値（グラフのみ）、RL = 1 kΩ より軽い負荷での出力振幅の規定値。

---

## 12. OPA2140（OPA2140AIDR を DIP 化）

`TI_OPA2140.pdf`（SBOS498F, REVISED MARCH 2023）。**表の電源条件は範囲**:「at TA = 25°C, VS = 4.5 V (±2.25) to 36 V (±18 V), RL = 2 kΩ connected to midsupply, and VCM = VOUT = midsupply (unless otherwise noted)」。Typical Characteristics の既定は ±18 V。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | Dual ±2.25〜±18 V、Single 4.5〜36 V | — | MIN / MAX | p.5 §6.3 | `Dual supply ±2.25 ±18` / `Single supply 4.5 36` |
| 電源電圧（絶対最大） | Dual ±20 V、Single 40 V | — | MAX | p.5 §6.1 | `Dual supply ±20` / `Single supply 40` |
| 静止電流 | typ 1.8 mA / max 2 mA（**per amplifier**）。全温度 max 2.7 mA | IO = 0 mA、25°C／TA = –40〜+125°C | TYP / MAX | p.8 §6.7 | `IQ Quiescent current per amplifier IO = 0 mA 1.8 2` / `TA = –40°C to +125°C 2.7 mA` |
| 出力電圧振幅（RL = 10 kΩ） | (V–) + 0.2 V 〜 (V+) – 0.2 V（レール基準）。typ 値なし | VS = 4.5〜36 V、RL = 10 kΩ、AOL ≥ 108 dB、25°C | MIN 列 / MAX 列 | p.7 §6.7 | `VO Voltage output RL = 10 kΩ, AOL ≥ 108 dB (V–) + 0.2 (V+) – 0.2` |
| 出力電圧振幅（RL = 2 kΩ） | (V–) + 0.35 V 〜 (V+) – 0.35 V（レール基準）。typ 値なし | VS = 4.5〜36 V、RL = 2 kΩ、AOL ≥ 108 dB、25°C | MIN 列 / MAX 列 | p.7 §6.7 | `RL = 2 kΩ, AOL ≥ 108 dB (V–) + 0.35 (V+) – 0.35 V` |
| グラフ: 出力電圧振幅 vs 出力電流 | 25°C で 約 30 mA まで 約 +17.5 V / 約 –17.7 V 付近（目読み） | "(Maximum Supply)"、ページ既定 VS = ±18 V | typ（グラフ） | p.10 Figure 6-6 | 図題 "Output Voltage Swing vs Output Current (Maximum Supply)" |
| グラフ: 最大出力電圧 vs 周波数 | 低域で VS = ±15 V の線が約 29 Vpp（目読み。縦軸 "Output Voltage (VPP)"）。ほか ±5 V・±2.25 V の線 | ページ既定は ±18 V だが線に ±15 V と明記 | typ（グラフ） | p.12 Figure 6-22 | 図題 "Maximum Output Voltage vs Frequency" 〔2026-09-25 照合で追加〕 |
| 同相入力電圧範囲 | (V–) – 0.1 V 〜 (V+) – 3.5 V | VS = 4.5〜36 V、TA = –40〜+125°C | MIN / MAX | p.7 §6.7 | `VCM Common-mode voltage TA = –40°C to +125°C (V–) – 0.1 (V+) – 3.5 V` |
| 入力電圧（絶対最大） | (V–) – 0.5 〜 (V+) + 0.5 V、電流 ±10 mA | — | MIN / MAX | p.5 §6.1 | `Signal input pins(2) Voltage (V–) – 0.5 (V+) + 0.5 V` / `Current ±10 mA`、注(2) "Input pins are diode-clamped to the power-supply rails. Input signals that can swing more than 0.5 V beyond the supply rails must be current limited to 10 mA or less." |
| 差動入力（絶対最大） | 規定なし | — | — | — | — |
| 出力短絡電流 | Source typ 36 mA / Sink typ –30 mA | 25°C | TYP | p.7 §6.7 | `ISC Short-circuit current Source 36` / `Sink –30 mA` |
| 出力短絡（絶対最大） | Continuous（VS/2 へ、1 パッケージ 1 回路） | — | — | p.5 §6.1 | `Output short-circuit(3) Continuous`、注(3) "Short-circuit to VS / 2 (ground in symmetrical dual-supply setups), one amplifier per package." |

探したが DS に無かった項目: 出力振幅の typ 値・全温度での規定値、±18 V 以外での出力振幅 vs 出力電流のグラフ、差動入力電圧の絶対最大。

---

## 13. OPA828（OPA828 ×2 の DIP 化）

`TI_OPA828.pdf`（OPA828, OPA2828。SBOS671D, REVISED DECEMBER 2022）。表の既定条件は「at TA = 25°C, (V+) = 15 V, (V–) = –15 V, VCM = VO = midsupply, CL = 20 pF, and RL = 2 kΩ connected to midsupply (unless otherwise noted)」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | Dual ±4〜±18 V、Single 8〜36 V | — | MIN / MAX | p.4 §6.3 | `Single supply 8 36` / `Dual supply ±4 ±18` |
| 電源電圧（絶対最大） | Dual ±20 V、Single 40 V | — | MAX | p.4 §6.1 | `Single-supply 40` / `Dual-supply ±20` |
| 静止電流 | typ 5.5 mA / max 6.2 mA（**per amplifier**）。0〜85°C: max 7.1、–40〜+125°C: max 7.9 | ±15 V、IO = 0 A | TYP / MAX | p.6 §6.5 | `IQ Quiescent current (per amplifier) IO = 0 A 5.5 6.2` / `TA = 0°C to 85°C 7.1` / `TA = –40°C to +125°C 7.9 mA` |
| 出力電圧振幅（RL = 10 kΩ） | typ 0.9 V / max 1.2 V（**表中に「レールから」の文言なし**。原文の項目名は "Output voltage swing"、単位 V） | ±15 V、RL = 10 kΩ、25°C | TYP / MAX | p.6 §6.5 | `Output voltage swing RL = 10 kΩ 0.9 1.2 V` |
| 出力電圧振幅（RL = 600 Ω） | typ 1.2 V（max なし。同上、表中に基準の文言なし） | ±15 V、RL = 600 Ω、25°C | TYP | p.6 §6.5 | `RL = 600 Ω 1.2` |
| 参考: AOL の試験条件の出力範囲 | RL = 600 Ω: (V–) + 1.6 V < VO < (V+) – 1.6 V、RL = 10 kΩ: (V–) + 1.5 V < VO < (V+) – 1.5 V で AOL min 120 dB（25°C） | ±15 V | MIN | p.6 §6.5 | `(V–) + 1.6 V< VO < (V+) – 1.6 V, RL = 600 Ω 120 130` / `(V–) + 1.5 V < VO < (V+) – 1.5 V, RL = 10 kΩ 120 130`（振幅の規定ではない） |
| グラフ: 出力電圧振幅 vs 吐き出し電流 | 約 +13 V で約 48 mA まで平坦（–40/25/85/125°C の 4 本ほぼ重なる。目読み） | **VS = ±15 V**（図下の表記）、RL = 2 kΩ（ページ既定） | typ（グラフ） | p.10 Figure 6-18 | 図題 "Output Voltage Swing vs Output Sourcing Current"、図下 "VS = ±15 V" |
| グラフ: 出力電圧振幅 vs 吸い込み電流 | 約 –13 V で約 49 mA まで平坦（目読み） | **VS = ±15 V**（図下の表記） | typ（グラフ） | p.11 Figure 6-19 | 図題 "Output Voltage Swing vs Output Sinking Current"、図下 "VS = ±15 V" |
| 同相入力電圧範囲 | (V–) + 2.5 V 〜 (V+) – 3.5 V | ±15 V、25°C | MIN / MAX | p.5 §6.5 | `VCM Common-mode voltage (V–) + 2.5 (V+) – 3.5 V` |
| 入力電圧（絶対最大） | Common-mode (V–) – 0.5 〜 (V+) + 0.5 V、電流 ±10 mA | — | MIN / MAX | p.4 §6.1 | `Common-mode(3) (V–) – 0.5 (V+) + 0.5` / `Current(3) ±10 mA`、注(3) "Input terminals are diode-clamped to the power-supply rails. Current-limit input signals that can swing more than 0.5 V beyond the supply rails to 10 mA or less." |
| 差動入力（絶対最大） | (V+) – (V–)。入力間に逆並列ダイオード**なし** | — | MAX | p.4 §6.1 | `Differential(2) (V+) – (V–)`、注(2) "Input terminals are not clamped to each other with anti-parallel diodes. The JFET input stage allows large differential voltage values up to the supply voltage of the device." |
| 出力電流 | typ ±30 mA（線形動作、AOL ≥ 120 dB） | ±15 V、25°C | TYP | p.6 §6.5 | `IO Output current For linear operation, AOL ≥ 120 dB ±30 mA` |
| 出力短絡電流 | typ ±50 mA | ±15 V、25°C | TYP | p.6 §6.5 | `ISC Short-circuit current ±50 mA` |
| 出力短絡（絶対最大） | Continuous（GND へ、1 パッケージ 1 回路） | — | — | p.4 §6.1 | `Output short current(4) Continuous`、注(4) "Short circuit to ground, one amplifier per package." |

探したが DS に無かった項目: 表の "Output voltage swing" がレールからの距離か否かの明記（表中にも本文にも見つからず。値だけがある）、出力振幅の min 値・全温度での規定値、±15 V 以外での出力振幅の規定。

---

## 14. MUSES01（MUSE01 ×2 → 1×DIP 変換）

`NJR_MUSES01.pdf`（20250321）。ページ上部に "MUSES01 is the NRND product."。題は "High Quality Audio , J-FET Input, Dual Operational Amplifier"（**DS 上は 2 回路入り**）。特長欄には "Bipolar Technology" の行もある（原文どおり）。DC 特性の既定は「V+/V-=±15V, Ta=25°C unless otherwise specified」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | min ±9 V / max ±16 V | Ta = 25°C | MIN / MAX | p.2 | `RECOMMENDED OPERATING CONDITION (Ta=25°C) Supply Voltage V+/V- - ±9 - ±16 V` |
| 電源電圧（特長） | ±9〜±16 V | — | — | p.1 | `Operating Voltage Vopr=±9V to ±16V` |
| 電源電圧（絶対最大） | ±18 V | Ta = 25°C | RATING | p.2 | `Supply Voltage V+/V- ±18 V` |
| 静止電流 | typ 8.5 mA / max 12.0 mA（パッケージ全体か 1 回路かの記載なし） | ±15 V、無信号、RL = ∞、25°C | TYP / MAX | p.2 | `Operating Current Icc No Signal, RL=∞ - 8.5 12.0 mA` |
| 出力電圧振幅 1 | min ±12 V / typ ±13.5 V | ±15 V、RL = 10 kΩ、25°C | MIN / TYP | p.2 | `Max Output Voltage 1 VOM1 RL=10kΩ ±12 ±13.5 - V` |
| 出力電圧振幅 2 | min ±10 V / typ ±12.5 V | ±15 V、RL = 2 kΩ、25°C | MIN / TYP | p.2 | `Max Output Voltage 2 VOM2 RL=2kΩ ±10 ±12.5 - V` |
| グラフ: 最大出力電圧 vs 温度（RL = 2 kΩ） | 25°C で ±15 V: 約 +14 / 約 –13.3 V、±16 V: 約 +15 / 約 –14.5 V、±9 V: 約 +8 / 約 –7.4 V（目読み） | Gv = open, RL = 2kohm to 0V | typ（グラフ） | p.11 | 図題 "MAXIMUM OUTPUT VOLTAGE vs TEMPERATURE (SUPPLY VOLTAGE) Gv=open,RL=2kohm to 0V" |
| グラフ: 最大出力電圧 vs 温度（RL = 10 kΩ） | 25°C で ±15 V: 約 +14 / 約 –13.5 V（目読み）。±16 V・±9 V の線もある | Gv = open, RL = 10kohm to 0V | typ（グラフ） | p.11 | 図題 "MAXIMUM OUTPUT VOLTAGE vs TEMPERATURE (SUPPLY VOLTAGE) Gv=open,RL=10kohm to 0V" |
| グラフ: 最大出力電圧 vs 負荷抵抗 | ±16 V・±15 V・±9 V の 3 枚（温度別）。±15 V で 2 kΩ 約 +14.0 / 約 –13.1 V（目読み。温度 3 本の幅 ±0.2 V） | Gv = open, RL to 0V | typ（グラフ） | p.10、p.11 | 図題 "MAXIMUM OUTPUT VOLTAGE vs LOAD RESISTANCE (TEMPERATURE) V+/V-=±15V,Gv=open,RL to 0V" ほか 〔2026-09-25 照合で訂正〕 |
| 同相入力電圧範囲 | min ±8 V / typ ±9.5 V（CMR ≥ 60 dB） | ±15 V、25°C | MIN / TYP | p.2 | `Input Common Mode Voltage Range VICM CMR≥60dB ±8 ±9.5 - V` |
| 同相入力電圧（絶対最大） | ±15 V（Note1） | — | RATING | p.2 | `Common Mode Input Voltage VICM ±15 (Note1) V`、"(Note1) For supply Voltages less than ±15 V, the maximum input voltage is equal to the Supply Voltage." |
| 差動入力（絶対最大） | ±30 V | — | RATING | p.2 | `Differential Input Voltage VID ±30 V` |
| 出力電流（絶対最大） | ±25 mA | Ta = 25°C | RATING | p.2 | `Output Current IO ±25 mA` |

探したが DS に無かった項目: 出力短絡電流・短絡時間の規定、入力保護ダイオードの記述、±12 V での出力振幅の規定・グラフ（グラフは ±9 / ±15 / ±16 V）、静止電流の回路数の明記、全温度での出力振幅の規定値。

---

## 15. MUSES02（MUSES02D）

`NJR_MUSES02.pdf`（20250319）。ページ上部に "MUSES02D is the NRND product."。題は "High Quality Audio, Bipolar Input, Dual Operational Amplifier"。DC 特性の既定は「V+/V-=±15V, Ta=25°C unless otherwise specified」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | min ±3.5 V / max ±16 V | Ta = 25°C | MIN / MAX | p.2 | `RECOMMENDED OPERATING CONDITION (Ta=25°C) Supply Voltage V+/V- - ±3.5 - ±16 V` |
| 電源電圧（絶対最大） | ±18 V | Ta = 25°C | RATING | p.2 | `Supply Voltage V+/V- ±18 V` |
| 静止電流 | typ 8.0 mA / max 12.0 mA（パッケージ全体か 1 回路かの記載なし） | ±15 V、無信号、RL = ∞、25°C | TYP / MAX | p.2 | `Operating Current Icc No Signal, RL=∞ - 8.0 12.0 mA` |
| 出力電圧振幅 | min ±12 V / typ ±13.5 V | ±15 V、RL = 2 kΩ、25°C | MIN / TYP | p.2 | `Max Output Voltage VOM RL=2kΩ ±12 ±13.5 - V` |
| グラフ: 最大出力電圧 vs 温度 | 25°C で ±15 V: 約 +14 / 約 –13.3 V、±16 V: 約 +15 / 約 –14.3 V、±3.5 V: 約 +2.7 / 約 –1.8 V（目読み） | Gv = open, RL = 2k, RL to 0V | typ（グラフ） | p.11 | 図題 "Maximum Output Voltage vs. Temperature (Supply Voltage) GV=open,RL=2k,RL to 0V" |
| グラフ: 最大出力電圧 vs 負荷抵抗 | ±16 V・±15 V・±3.5 V の 3 枚（温度別）。±15 V で 2 kΩ 約 +14 / 約 –13.3 V（目読み） | GV = open, RL to 0V | typ（グラフ） | p.10、p.11 | 図題 "Maximum Output Voltage vs. Load Resistance (Temperature) V+/V-=±15V, GV=open, RL to 0V" ほか |
| 同相入力電圧範囲 | min ±12 V / typ ±13.5 V（CMR ≥ 80 dB） | ±15 V、25°C | MIN / TYP | p.2 | `Input Common Mode Voltage Range VICM CMR≥80dB ±12 ±13.5 - V` |
| 同相入力電圧（絶対最大） | ±15 V（Note1） | — | RATING | p.2 | `Common Mode Input Voltage VICM ±15 (Note1) V`、"(Note1) For supply Voltages less than ±15 V, the maximum input voltage is equal to the Supply Voltage." |
| 差動入力（絶対最大） | ±30 V | — | RATING | p.2 | `Differential Input Voltage VID ±30 V` |
| 出力電流（絶対最大） | ±50 mA | Ta = 25°C | RATING | p.2 | `Output Current IO ±50 mA` |

探したが DS に無かった項目: 出力短絡電流・短絡時間の規定、入力保護ダイオードの記述、±12 V での出力振幅の規定・グラフ（グラフは ±3.5 / ±15 / ±16 V）、RL = 2 kΩ 以外での出力振幅の規定値、静止電流の回路数の明記、全温度での出力振幅の規定値。

---

## 16. MUSES03（MUSE03 ×2 → DIP 化・2ch 変換基板）

`NJR_MUSES03.pdf`（Ver.4.2、日本語版）。題は「プレミアムオーディオ機器向け 1 回路入り J-FET 入力高音質オペアンプ」（**DS 上は 1 回路入り**）。DC 特性の既定は「指定無き場合には V+/V-=±15V, RL=GND, Ta=25ºC」。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（推奨動作） | ±3.5〜±18 V | — | 値 | p.2 | `推奨動作条件 電源電圧 V+-V- ±3.5 to ±18 V` |
| 電源電圧（絶対最大） | ±19 V | — | 定格 | p.2 | `電源電圧 V+-V- ±19 V` |
| 静止電流 | typ 5.8 mA / max 10 mA（1 回路入り品） | ±15 V、RL = ∞、無信号時、25°C | 標準 / 最大 | p.4 | `消費電流 Icc RL=∞, 無信号時 - 5.8 10 mA` |
| 出力電圧振幅 1 | min ±13.0 V / typ ±14.0 V | ±15 V、RL = 10 kΩ、25°C | 最小 / 標準 | p.4 | `最大出力電圧 1 VOM1 RL=10kΩ ±13.0 ±14.0 - V` |
| 出力電圧振幅 2 | min ±12.8 V / typ ±13.8 V | ±15 V、RL = 2 kΩ、25°C | 最小 / 標準 | p.4 | `最大出力電圧 2 VOM2 RL=2kΩ ±12.8 ±13.8 - V` |
| 出力電圧振幅 3 | min ±12.5 V / typ ±13.5 V | ±15 V、RL = 600 Ω、25°C | 最小 / 標準 | p.4 | `最大出力電圧 3 VOM2 RL=600Ω ±12.5 ±13.5 - V`（記号が VOM2 のまま。原文どおり） |
| 参考: 電圧利得の試験条件の出力電圧 | RL = 10 kΩ, Vo = ±13 V／RL = 2 kΩ, Vo = ±12.8 V／RL = 600 Ω, Vo = ±12.5 V で AV min 90 dB | ±15 V、25°C | 最小 | p.4 | `電圧利得 2 AV2 RL=2kΩ, Vo=±12.8V 90 115 - dB`（振幅の規定ではない） |
| グラフ: 出力電圧 vs 負荷抵抗／vs 出力電流 | ±15 V のみ（負荷抵抗 1 kΩ 以上で約 ±14 V 付近。目読み、低解像度で確認） | V+/V-=±15V, VIN=±1V | typ（グラフ） | p.6 | 図題 "Output Voltage vs. Load Resistance V+/V-=±15V, VIN=±1V" / "Output Voltage vs. Output Current" |
| 同相入力電圧範囲 | min ±12.0 V / typ ±13.0 V（CMR ≥ 70 dB） | ±15 V、25°C | 最小 / 標準 | p.4 | `同相入力電圧範囲 VICM CMR≥70dB ±12.0 ±13.0 - V` |
| 同相入力電圧（絶対最大） | ±18 V（注 1） | — | 定格 | p.2 | `同相入力電圧 VIN ±18 注(1) V`、「(注 1) 電源電圧が±18V 以下の場合は、電源電圧と等しくなります。」 |
| 差動入力（絶対最大） | **±6 V** | — | 定格 | p.2 | `差動入力電圧 VID ±6 V` |
| 最大出力尖頭電流（絶対最大） | 250 mA | — | 定格 | p.2 | `最大出力尖頭電流 IOP 250 mA` |
| 使用上の注意（出力） | 瞬間的に 250 mA を越えるおそれがあれば出力に保護抵抗を（例: 18 V/0.2 A = 90 Ω 以上） | — | —（本文） | p.4 | 「出力端子の短絡など、出力電流が瞬間的に絶対最大定格の 250mA を越える可能性がある場合には、過電流保護の為に下図のように保護抵抗を挿入し、余裕をもった設計を行う事を推奨致します。」「※抵抗値は参考値であり、製品の特性を保証するものではありません。」 |

探したが DS に無かった項目: 出力短絡電流（連続）の規定、入力保護ダイオードの記述、±15 V 以外での出力振幅の規定・グラフ、全温度での出力振幅の規定値。

---

## 17. AD797（シングル ×2 の Dual 化変換）

`AD_AD797.pdf`（Rev. K）。表は「TA = 25°C and VS = ±15 V dc, unless otherwise noted.」、Supply Voltage 列つき、AD797A と AD797B で列が分かれる（出力振幅・同相範囲・電源・出力電流は A/B 同値）。

| 項目 | 値 | 条件（電源・負荷・温度） | 列（min/typ/max） | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源電圧（動作範囲） | ±5〜±18 V | — | MIN / MAX（A・B とも） | p.4 Table 2 | `POWER SUPPLY Operating Range ±5 ±18 ±5 ±18 V` |
| 電源電圧（特長） | ±5 V と ±15 V で規定 | — | — | p.1 | "Specified for ±5 V and ±15 V power supplies" |
| 電源電圧（絶対最大） | ±18 V | — | — | p.5 Table 3 | `Supply Voltage ±18 V` |
| 静止電流 | typ 8.2 mA / max 10.5 mA（1 回路入り品） | ±5 V, ±15 V、25°C | TYP / MAX（A・B とも） | p.4 Table 2 | `Quiescent Current ±5 V, ±15 V 8.2 10.5 8.2 10.5 mA` |
| 出力電圧振幅 | min ±12 V / typ ±13 V | ±15 V、RLOAD = 2 kΩ、25°C | MIN / TYP（A・B とも） | p.3 Table 2 | `OUTPUT VOLTAGE SWING RLOAD = 2 kΩ ±15 V ±12 ±13 ±12 ±13 V` |
| 出力電圧振幅 | min ±11 V / typ ±13 V | ±15 V、RLOAD = 600 Ω、25°C | MIN / TYP（A・B とも） | p.3 Table 2 | `RLOAD = 600 Ω ±15 V ±11 ±13 ±11 ±13 V` |
| 出力電圧振幅 | min ±2.5 V / typ ±3 V | ±5 V、RLOAD = 600 Ω、25°C | MIN / TYP（A・B とも） | p.3 Table 2 | `RLOAD = 600 Ω ±5 V ±2.5 ±3 ±2.5 ±3 V` |
| グラフ: 出力電圧振幅 vs 電源電圧 | **±12 V で** 約 10.8 V（–VOUT の線）/ 約 10.4 V（+VOUT の線）（目読み。どちらの線がどちらかはラベル位置からの判断）。**負荷の表記なし** | 負荷記載なし | typ（グラフ） | p.6 Figure 4 | 図題 "Output Voltage Swing vs. Supply Voltage"、縦軸 "OUTPUT VOLTAGE SWING (±V)" |
| グラフ: 出力電圧振幅 vs 負荷抵抗 | VS = ±15 V で 約 200 Ω 以上 約 27 Vp-p、VS = ±5 V で 約 6 Vp-p 前後（目読み） | VS = ±15V / ±5 | typ（グラフ） | p.6 Figure 5 | 図題 "Output Voltage Swing vs. Load Resistance"、縦軸 "OUTPUT VOLTAGE SWING (V p-p)" |
| 同相入力電圧範囲 | ±15 V: min ±11 / typ ±12 V、±5 V: min ±2.5 / typ ±3 V | 25°C | MIN / TYP（A・B とも） | p.3 Table 2 | `INPUT COMMON-MODE VOLTAGE RANGE ±15 V ±11 ±12 ±11 ±12 V` / `±5 V ±2.5 ±3 ±2.5 ±3 V` |
| 入力電圧（絶対最大） | ±VS | — | — | p.5 Table 3 | `Input Voltage ±VS` |
| 差動入力（絶対最大） | **±0.7 V**。入力は逆並列（back-to-back）ダイオードで保護、内部に電流制限抵抗なし | — | — | p.5 Table 3 | `Differential Input Voltage1 ±0.7 V`、注1 "The AD797 inputs are protected by back-to-back diodes. To achieve low noise, internal current-limiting resistors are not incorporated into the design of this amplifier. If the differential input voltage exceeds ±0.7 V, the input current should be limited to less than 25 mA by series protection resistors. Note, however, that this degrades the low noise performance of the device." |
| 出力電流 | min 30 mA / typ 50 mA（\|VS − VOUT\| > 4 V、AOL > 200 kΩ） | ±5 V, ±15 V、25°C | MIN / TYP | p.3 Table 2 | `Output Current3 ±5 V, ±15 V 30 50 30 50 mA`、注3 "Output current for \|VS − VOUT\| > 4 V, AOL > 200 kΩ." |
| 出力短絡電流 | typ 80 mA | ±5 V, ±15 V、25°C | TYP | p.3 Table 2 | `Short-Circuit Current ±5 V, ±15 V 80 80 mA` |
| 出力短絡（絶対最大） | 内部最大損失の範囲で無期限 | — | — | p.5 Table 3 | `Output Short-Circuit Duration Indefinite within maximum internal power dissipation` |

探したが DS に無かった項目: 推奨動作電源電圧範囲の節（Table 2 の Operating Range がそれに当たる）、全温度での出力振幅の規定値、±12 V での出力振幅の規定値（グラフのみ・負荷不明）。

---

## 付録: 出力振幅の規定値だけの一覧

表の規定値（グラフは除く）だけを並べた。値は DS の表記のまま（レール基準のものはレール基準のまま）。換算はしていない。
「温度」が空欄のものは 25°C の表。

| 石 | 電源 | 負荷 | 温度 | min（保証） | typ | 表記の形 | 出典 |
|---|---|---|---|---|---|---|---|
| NE5532（TI） | — | — | — | 規定なし | 規定なし | （この版で削除） | TI_NE5532.pdf p.11 |
| NJM5532 | ±15 V | RL ≥ 600 Ω | 25°C | ±12 V | ±13 V | 絶対値 | NJR_NJM5532.pdf p.2 |
| NJM5532 | ±18 V | RL ≥ 600 Ω | 25°C | ±15 V | ±16 V | 絶対値 | NJR_NJM5532.pdf p.2 |
| NJM4580 | ±15 V | RL ≥ 2 kΩ | 25°C | ±12 V | ±13.5 V | 絶対値 | NJR_NJM4580.pdf p.2 |
| OPA2134 | ±15 V | RL = 10 kΩ | 25°C | (V+) – 1.2 V / (V–) + 0.5 V | — | レール基準（正側 MIN 列・負側 MAX 列） | TI_OPA2134.pdf p.8 |
| OPA2134 | ±15 V | RL = 2 kΩ | 25°C | (V+) – 1.5 V / (V–) + 1.2 V | — | レール基準（同上） | TI_OPA2134.pdf p.8 |
| OPA1656 | **±18 V** | RL = 2 kΩ | 25°C | (V–) + 0.25 V 〜 (V+) – 0.25 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA1656.pdf p.7 |
| OPA2604 | ±15 V | RL = 600 Ω | 25°C | ±11 V | ±12 V | 絶対値 | TI_OPA2604.pdf p.5 |
| LME49860 | ±18 V | RL = 600 Ω | 25°C | — | ±16.7 V | 絶対値（Typical 列） | TI_LME49860.pdf p.4 |
| LME49860 | ±22 V | RL = 600 Ω | 25°C | ±19.0 V (min) | ±20.4 V | 絶対値（Limit 列） | TI_LME49860.pdf p.4 |
| LME49860 | ±18 V | RL = 2 kΩ | 25°C | — | ±17.0 V | 絶対値 | TI_LME49860.pdf p.4 |
| LME49860 | ±22 V | RL = 2 kΩ | 25°C | — | ±21.0 V | 絶対値 | TI_LME49860.pdf p.4 |
| LME49860 | ±18 V | RL = 10 kΩ | 25°C | — | ±17.1 V | 絶対値 | TI_LME49860.pdf p.4 |
| LME49860 | ±22 V | RL = 10 kΩ | 25°C | — | ±21.2 V | 絶対値 | TI_LME49860.pdf p.4 |
| OPA1652 | ±15 V | RL = 2 kΩ | 25°C | (V–) + 0.8 V 〜 (V+) – 0.8 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA1652.pdf p.7 |
| OPA627AU/BU | ±15 V | RL = 1 kΩ | 25°C | ±11.5 V | ±12.3 V | 絶対値 | TI_OPA627.pdf p.7 |
| OPA627AU/BU | ±15 V | RL = 1 kΩ | –25〜+85°C | ±11 V | ±11.5 V | 絶対値 | TI_OPA627.pdf p.7 |
| OPA1612 | ±2.25〜±18 V（表の範囲） | RL = 10 kΩ（AOL ≥ 114 dB） | 25°C | (V–) + 0.2 V 〜 (V+) – 0.2 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA1612.pdf p.6 |
| OPA1612 | ±2.25〜±18 V（表の範囲） | RL = 2 kΩ（AOL ≥ 110 dB） | 25°C | (V–) + 0.6 V 〜 (V+) – 0.6 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA1612.pdf p.6 |
| LT1364 | ±15 V | RL = 1k（VIN = ±40 mV） | 25°C | 13.5 ±V | 14.0 ±V | 絶対値 | AD_LT1364.pdf p.3 |
| LT1364 | ±15 V | RL = 500 Ω（VIN = ±40 mV） | 25°C | 13.0 ±V | 13.7 ±V | 絶対値 | AD_LT1364.pdf p.3 |
| LT1364 | ±5 V | RL = 500 Ω | 25°C | 3.5 ±V | 4.1 ±V | 絶対値 | AD_LT1364.pdf p.3 |
| LT1364 | ±5 V | RL = 150 Ω | 25°C | 3.4 ±V | 3.8 ±V | 絶対値 | AD_LT1364.pdf p.3 |
| LT1364 | ±2.5 V | RL = 500 Ω | 25°C | 1.3 ±V | 1.7 ±V | 絶対値 | AD_LT1364.pdf p.3 |
| LT1364 | ±15 V | RL = 1k | 0〜70°C | 13.4 ±V | — | 絶対値 | AD_LT1364.pdf p.4 |
| LT1364 | ±15 V | RL = 500 Ω | 0〜70°C | 12.8 ±V | — | 絶対値 | AD_LT1364.pdf p.4 |
| LT1364 | ±5 V | RL = 500 Ω / 150 Ω | 0〜70°C | 3.4 / 3.3 ±V | — | 絶対値 | AD_LT1364.pdf p.4 |
| LT1364 | ±2.5 V | RL = 500 Ω | 0〜70°C | 1.2 ±V | — | 絶対値 | AD_LT1364.pdf p.4 |
| LT1364 | ±15 V | RL = 1k | –40〜85°C（Note 9） | 13.4 ±V | — | 絶対値 | AD_LT1364.pdf p.5 |
| LT1364 | ±15 V | RL = 500 Ω | –40〜85°C（Note 9） | 12.7 ±V | — | 絶対値 | AD_LT1364.pdf p.5 |
| LT1364 | ±5 V | RL = 500 Ω / 150 Ω | –40〜85°C（Note 9） | 3.4 / 3.2 ±V | — | 絶対値 | AD_LT1364.pdf p.5 |
| LT1364 | ±2.5 V | RL = 500 Ω | –40〜85°C（Note 9） | 1.2 ±V | — | 絶対値 | AD_LT1364.pdf p.5 |
| OPA2140 | 4.5〜36 V（±2.25〜±18 V、表の範囲） | RL = 10 kΩ（AOL ≥ 108 dB） | 25°C | (V–) + 0.2 V 〜 (V+) – 0.2 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA2140.pdf p.7 |
| OPA2140 | 4.5〜36 V（±2.25〜±18 V、表の範囲） | RL = 2 kΩ（AOL ≥ 108 dB） | 25°C | (V–) + 0.35 V 〜 (V+) – 0.35 V | — | レール基準（MIN 列 / MAX 列） | TI_OPA2140.pdf p.7 |
| OPA828 | ±15 V | RL = 10 kΩ | 25°C | —（max 1.2 V） | 0.9 V | "Output voltage swing"（基準の明記なし） | TI_OPA828.pdf p.6 |
| OPA828 | ±15 V | RL = 600 Ω | 25°C | — | 1.2 V | 同上 | TI_OPA828.pdf p.6 |
| MUSES01 | ±15 V | RL = 10 kΩ | 25°C | ±12 V | ±13.5 V | 絶対値 | NJR_MUSES01.pdf p.2 |
| MUSES01 | ±15 V | RL = 2 kΩ | 25°C | ±10 V | ±12.5 V | 絶対値 | NJR_MUSES01.pdf p.2 |
| MUSES02 | ±15 V | RL = 2 kΩ | 25°C | ±12 V | ±13.5 V | 絶対値 | NJR_MUSES02.pdf p.2 |
| MUSES03 | ±15 V | RL = 10 kΩ | 25°C | ±13.0 V | ±14.0 V | 絶対値 | NJR_MUSES03.pdf p.4 |
| MUSES03 | ±15 V | RL = 2 kΩ | 25°C | ±12.8 V | ±13.8 V | 絶対値 | NJR_MUSES03.pdf p.4 |
| MUSES03 | ±15 V | RL = 600 Ω | 25°C | ±12.5 V | ±13.5 V | 絶対値 | NJR_MUSES03.pdf p.4 |
| AD797 | ±15 V | RLOAD = 2 kΩ | 25°C | ±12 V | ±13 V | 絶対値 | AD_AD797.pdf p.3 |
| AD797 | ±15 V | RLOAD = 600 Ω | 25°C | ±11 V | ±13 V | 絶対値 | AD_AD797.pdf p.3 |
| AD797 | ±5 V | RLOAD = 600 Ω | 25°C | ±2.5 V | ±3 V | 絶対値 | AD_AD797.pdf p.3 |

**±12 V（またはそれを含む電源範囲）での規定値があるのは**、表の電源条件が範囲になっている OPA1612（±2.25〜±18 V）と OPA2140（4.5〜36 V）の 2 つだけ。ほかは ±12 V の規定値が DS に無い（グラフがあるのは NJM5532・NJM4580・LME49860（Vrms, THD+N = 1%）・LT1364（レール基準）・AD797（負荷不明）。上の各石の節を参照）。
