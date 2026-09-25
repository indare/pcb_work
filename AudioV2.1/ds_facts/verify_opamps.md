# opamps.md の独立照合（手持ちオペアンプ 17 石）

- **照合日**: 2026-09-25
- **対象**: `AudioV2.1/ds_facts/opamps.md`（このファイルでは書き換えていない）
- **DS**: `AudioV2.1/datasheets/opamps/*.pdf`
- **方法**: 出典ページを `pdftoppm -r 150` でページ画像にして目で読んだ。数値・列・条件（表の見出しと脚注を含む）・引用・ページを確かめた。
  グラフは目で読んだうえで、画像のピクセル列を走査して曲線の位置を目盛から換算した（作業ファイルは scratchpad の `verify_opamps/`）。
  「目読み」の許容幅は **その軸の最も細かい目盛の半分**。これを超えたものを「誤り（目読み）」にした
- **照合した行数**: **277 行**（各石の表 232 行と、付録「出力振幅の規定値だけの一覧」45 行）。
  各節の頭書き（DS の版、表の既定条件、型番の注記など）も確かめたが、上の数には入れていない（末尾の「頭書き」節を参照）

## 判定の内訳

| 判定 | 行数 | 該当 |
|---|---|---|
| 一致 | **273** | 下の表で「一致」とした行。うち 3 行は値としては一致だが補足がある（OPA2134 の Headroom、OPA1652・OPA1612 の差動入力） |
| 誤り（目読み） | **3** | OPA2604 の Figure 15（26 → **24 Vp-p**）、OPA1612 の Figure 27 の負側（−14.6 → **−14.0〜−14.35 V**）、MUSES01 の負荷抵抗グラフ ±15 V の正側（+13.5 → **+14.0 V**） |
| 条件の誤り | **1** | OPA627 の Figure 5-23 に「RL = 10 kΩ」と書いているが、そのページにも図にも負荷の記載は無い |
| 列の誤り | 0 | — |
| 引用が無い | 0 | 引用はすべて DS に実在した（TI 版 NE5532 の注 (5) の文法の崩れ、OPA1656 の "groundinsymmetrical" の詰まり、MUSES03 の「VOM2」重複も原文どおり） |
| 確かめられず | 0 | — |

これとは別に、**「探したが DS に無かった」としていたが DS にあったもの**が 3 件、関連するグラフの書き漏れが 5 件ある（末尾の節）。
3 件のうち重いのは、**OPA1652 と OPA1612 の入力間に back-to-back ダイオードがある**という記述（入力保護の扱いと、差動入力が大きく振れる回路での使い方を変える）と、
**NJM5532 のボルテージフォロワでの入力ダイオード破壊の注意**。

---

## 判定表

列の読み方: 「DS の実際」が「同左」なら、値・列・条件・ページとも opamps.md のとおり。目読みの行は、自分の読みを必ず書いた。

### 1. NE5532（TI_NE5532.pdf, SLOS075K）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| NE5532 | 電源電圧（推奨動作） | VCC+ 5〜15 V、VCC– −5〜−15 V | 一致 | 同左。p.3 §5.3、MIN/MAX 列 | `VCC+ Supply voltage 5 15 V` / `VCC– Supply voltage –5 –15 V` |
| NE5532 | 電源電圧（本文） | ±5〜±15 V | 一致 | 同左。p.9 §7.2 | "specified for operation over the range of ±5 to ±15 V" |
| NE5532 | 電源電圧（絶対最大・表） | 0〜+18 V / −18〜0 V | 一致 | 同左。p.3 §5.1、MIN/MAX 列。表見出しは "over operating free-air temperature range" | `VCC+ 0 +18` / `VCC– –18 0` |
| NE5532 | 電源電圧（絶対最大・本文の注意） | ±22 V（表と食い違い） | 一致 | 同左。p.9 CAUTION と p.11 改訂履歴の両方を確認 | "Supply voltages outside of the ±22 V range…" / "Changed Supply voltage positive and negative from 22V to 18V" |
| NE5532 | 静止電流 | typ 6 / max 16 mA（Total） | 一致 | 同左。p.4 §5.5、TYP/MAX 列、VO = 0, No load | `ICC Total supply current VO = 0, No load 6 16 mA` |
| NE5532 | 出力電圧振幅 | 規定なし（削除） | 一致 | p.4 の表に項目なし。p.11 改訂履歴に削除の記載 | "Removed Maximum peak-to-peak output voltage swing, …" |
| NE5532 | 参考: AVD の試験条件 | VO = ±10 V、min 15/25、全温度 10/15 V/mV | 一致 | 同左。p.4、MIN 列（TYP 50/100） | `RL ≥ 600Ω, VO = ±10 V … 15 50` / `RL ≥ 2kΩ, VO±10 V … 25 100` |
| NE5532 | 同相入力電圧範囲 | min ±12 / typ ±13 V | 一致 | 同左。p.4、MIN/TYP 列 | `VICR … ±12 ±13 V` |
| NE5532 | 入力電圧（絶対最大） | −15〜+15 V | 一致 | 同左。p.3、注 (3) も実在 | "The magnitude of the input voltage must never exceed the magnitude of the supply voltage." |
| NE5532 | 差動入力（絶対最大） | 電圧値なし、入力電流 ±10 mA、約 0.6 V 注記 | 一致 | 同左。p.3、注 (4) | "Excessive input current flows if a differential input voltage in exceeding approximately 0.6V is applied…" |
| NE5532 | 入力保護ダイオード | 記述あり | 一致 | p.1 §3、p.6 §6.1 の両方 | "…high slew rate, input-protection diodes, and output short-circuit protection." |
| NE5532 | 出力短絡電流 | typ 38 mA | 一致 | 同左。p.4、TYP 列 | `IOS Output short-circuit current 38 mA` |
| NE5532 | 出力短絡時間（絶対最大） | Unlimited | 一致 | 同左。p.3、注 (5) | "The output can be shorted to ground or either power supply. …" |

### 2. NJM5532（NJR_NJM5532.pdf, 20250306）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| NJM5532 | 電源電圧（推奨動作） | ±3〜±22 V | 一致 | 同左。p.2、Ta=25°C | `RECOMMENDED OPERATING VOLTAGE (Ta=25°C) … ±3~±22` |
| NJM5532 | 電源電圧（特長） | ±3〜±22 V | 一致 | 同左。p.1 | `Operating Voltage ±3V~±22V` |
| NJM5532 | 電源電圧（絶対最大） | ±22 V | 一致 | 同左。p.2、見出し Ta=25°C | `Supply Voltage V+/V- ±22 V` |
| NJM5532 | 静止電流 | typ 9 / max 16 mA | 一致 | 同左。p.2、TYP/MAX 列、RL=∞。p.5 にも "ICCMAX=16mA at V+/V-=±15V" | `Supply Current ICC RL=∞ - 9 16 mA` |
| NJM5532 | 出力電圧振幅 1 | min ±12 / typ ±13 V、RL ≥ 600 Ω | 一致 | 同左。p.2、MIN/TYP 列 | `Maximum Output Voltage1 VOM1 RL≥600Ω ± 12 ± 13` |
| NJM5532 | 出力電圧振幅 2 | min ±15 / typ ±16 V、±18 V | 一致 | 同左。p.2、行の条件に V+/V-=±18V | `Maximum Output Voltage2 VOM2 RL≥600Ω, V+/V-=±18V ± 15 ± 16` |
| NJM5532 | 出力（特長） | 600 Ω に 10 Vrms typ | 一致 | 同左。p.1 | `Output Drive Capability 600Ω,10Vrms typ.` |
| NJM5532 | 参考: 電力帯域 | 140 kHz / 100 kHz typ | 一致 | 同左。p.2 AC 表、TYP 列 | `WPG VO=±10V - 140` / `VO=±14V, RL=600Ω, V+/V-=±18V - 100` |
| NJM5532 | グラフ: 最大出力電圧 vs 電源電圧 | ±12 V で約 +11 / −11 V | 一致 | p.4。自分の読み（ピクセル換算）: **2 kΩ で +11.2 / −10.8 V、600 Ω で +10.8 / −10.3 V**。縦軸は 5 V 刻みなので許容内。ただし「2 線はほぼ重なる」は負側で約 0.5 V 離れている | 図題 "Maximum Output Voltage vs. Supply Voltage RL=2kΩ, Ta=25ºC" |
| NJM5532 | グラフ: 最大出力電圧 vs 温度 | 25°C で約 +13.7 / −13 V | 一致 | p.4。自分の読み +13.6 / −13.0 V | 図題 "…vs. Temperature V+/V-=±15V, RL=600Ω" |
| NJM5532 | グラフ: 最大出力電圧 vs 負荷抵抗 | 1 kΩ 以上で約 ±14 V | 一致 | p.3。自分の読み: 1 kΩ で +14.05 / −13.6 V、3 kΩ で +14.3 / −13.9 V | 図題 "…vs. Load Resistance V+/V-=±15V, Ta=25ºC" |
| NJM5532 | グラフ: 最大出力電圧振幅 vs 周波数 | 低域で約 26 Vpp | 一致 | p.3。自分の読み 26.3 Vpp | 図題 "Maximum Output Voltage Swing vs. Frequency" |
| NJM5532 | 同相入力電圧範囲 | min ±12 / typ ±13 V | 一致 | 同左。p.2 | `Common Mode Input Voltage Range VICM ± 12 ± 13` |
| NJM5532 | 同相入力電圧（絶対最大） | V+/V- | 一致 | 同左。p.2 | `Common Mode Input Voltage Range VICM V+/V- V` |
| NJM5532 | 差動入力（絶対最大） | ±0.5 V | 一致 | 同左。p.2 | `Differential Input Voltage Range VID ±0.5 V` |
| NJM5532 | 出力短絡電流 | typ 38 mA | 一致 | 同左。p.2、TYP 列 | `Short Circuit Output Current IOS - 38 -` |

### 3. NJM4580（NJR_NJM4580.pdf, 20250303）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| NJM4580 | 電源電圧（推奨動作） | ±2 / ±18 V | 一致 | 同左。p.2、MIN/MAX 列、Ta=25°C | `Supply Voltage V+/V- ±2 - ±18 V` |
| NJM4580 | 電源電圧（特長） | ±2〜±18 V | 一致 | 同左。p.1 | `Operating Voltage ±2V~±18V` |
| NJM4580 | 電源電圧（絶対最大） | ±18 V | 一致 | 同左。p.2、見出し "Ta=25°C, unless otherwise noted." | `Supply Voltage V+/V- ±18 V` |
| NJM4580 | 静止電流 | typ 6 / max 9 mA | 一致 | 同左。p.2、行に条件なし | `Supply Current ICC - 6 9 mA` |
| NJM4580 | 出力電圧振幅 | min ±12 / typ ±13.5 V、RL ≥ 2 kΩ | 一致 | 同左。p.2 | `Maximum Output Voltage VOM RL≥2kΩ ±12 ±13.5` |
| NJM4580 | グラフ: vs 電源電圧 | ±12 V で約 ±10.8 V | 一致 | p.4。自分の読み **+10.9〜11.0 / −11.0〜−11.1 V**（細目盛 2 V、許容内） | 図題 "Maximum Output Voltage vs. Supply Voltage RL=2kΩ, Ta=25ºC" |
| NJM4580 | グラフ: vs 負荷抵抗 | 2 kΩ で約 +14 / −13.7 V | 一致 | p.3。自分の読み +13.95 / −13.8 V | 図題 "…vs. Load Resistance V+/V-=±15V, Ta=25ºC" |
| NJM4580 | グラフ: vs 温度 | 25°C で約 +13.7 / −13.2 V | 一致 | p.4。自分の読み +13.7 / −13.4 V | 図題 "…vs. Temperature V+/V-=±15V, RL=2kΩ" |
| NJM4580 | グラフ: vs 出力電流 | 1〜10 mA で約 +14 / −13.5、100 mA で約 +4.5 / −10.5 V | 一致 | p.3。自分の読み 1 mA +14.05 / −13.6、10 mA +14.1 / −13.25、約 95 mA +4.8 / −10.3 V | 図題 "…vs. Output Current V+/V-=±15V, Ta=25ºC" |
| NJM4580 | グラフ: vs 周波数 | 低域で約 27.5 Vpp | 一致 | p.3。自分の読み 27.7 Vpp | 図題 "…vs. Frequency V+/V-=±15V, RL=2kΩ, Ta=25ºC" |
| NJM4580 | 同相入力電圧範囲 | min ±12 / typ ±13.5 V | 一致 | 同左。p.2 | `VICM ±12 ±13.5` |
| NJM4580 | 入力電圧（絶対最大） | ±15 V（Note1） | 一致 | 同左。p.2、Note1 実在 | "(Note1) For supply voltage less than ±15V, the absolute maximum input voltage is equal to supply voltage." |
| NJM4580 | 差動入力（絶対最大） | ±30 V（Note1） | 一致 | 同左。p.2 | `Differential Input Voltage VID ±30 (Note1)` |

### 4. OPA2134（TI_OPA2134.pdf, SBOS058B）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA2134 | 電源電圧（推奨動作） | ±2.5/±15/±18、5/30/36 V | 一致 | 同左。p.5 §5.3、MIN/NOM/MAX 列 | `Dual supply ±2.5 ±15 ±18` / `Single supply 5 30 36` |
| OPA2134 | 電源電圧（絶対最大） | 36 V | 一致 | 同左。p.5 §5.1、MAX 列 | `Supply voltage, (V+) – (V–) Single supply 36` |
| OPA2134 | 静止電流 | typ 4 / max 5 mA（per amplifier） | 一致 | 同左。p.8、TYP/MAX 列 | `IQ Quiescent current (per amplifier) IO = 0mA 4 5 mA` |
| OPA2134 | 出力電圧振幅（10 kΩ） | (V+)–1.2 / (V–)+0.5 | 一致 | 同左。p.8。正側は MIN 列に左寄せ、負側は MAX 列に右寄せ（画像で確認） | `RL = 10kΩ Positive (V+) – 1.2` / `Negative (V–) + 0.5` |
| OPA2134 | 出力電圧振幅（2 kΩ） | (V+)–1.5 / (V–)+1.2 | 一致 | 同左。p.8、同じ配置 | `RL = 2kΩ Positive (V+) – 1.5` / `Negative (V–) + 1.2` |
| OPA2134 | 参考: AOL の試験条件 | 10 kΩ: −14.5〜13.8 V、2 kΩ: −13.8〜13.5 V | 一致 | 同左。p.7、MIN 104 / TYP 120 | `RL = 10kΩ, –14.5V ≤ VO ≤ 13.8V 104 120` |
| OPA2134 | 参考: Headroom | typ 21.3 dBu、"VS = 18V" | 一致（補足あり） | 表の値・文言は同左（p.7、TYP 列）。**ただし同じ DS の p.13 §6.2.1 と p.9 Figure 5-4 は、VS = ±18 V・THD+N < 0.01% で 11.7 Vrms = 23.6 dBu としており、表の 21.3 dBu と食い違う**。表の値だけを「±18 V での Headroom」と読むと外れる | p.13: "…maximum allowable output voltage level of 11.7Vrms (THD+Noise < 0.01%), have a headroom specification of 23.6dBu. See Figure 5-4." |
| OPA2134 | 本文の記述 | レールから 1 V 以内 | 一致 | 同左。p.13 §6.1 | "the OPA134 has a wide output swing, to within 1V of the rails" |
| OPA2134 | グラフ: vs 周波数 | ±15 V 約 27.5、±5 V 約 8.5、±2.5 V 約 3.5 Vpp | 一致 | p.11 Figure 5-13。自分の読み 27.8 / 8.9 / 3.8 Vpp（細目盛 2 Vpp、許容内）。図中に負荷の記載はなく、ページ既定 RL = 2 kΩ | "Maximum output voltage without slew-rate induced distortion" |
| OPA2134 | 同相入力電圧範囲 | (V–)+2.5 / ±13 / (V+)–3.5 | 一致 | 同左。p.7、MIN/TYP/MAX 列 | `VCM Common-mode voltage (V–) + 2.5 ±13 (V+) – 3.5` |
| OPA2134 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.5、注 (2) 実在 | "Input pins are diode-clamped to the power-supply rails. …" |
| OPA2134 | 差動入力（絶対最大） | 規定なし | 一致 | p.5 §5.1 に項目なし。本文にも入力間ダイオードの記述なし | — |
| OPA2134 | 出力短絡電流 | +36 / −30 mA | 一致 | 同左。p.8、TYP 列 | `ISC Short-circuit current Sourcing 36` / `Sinking –30` |
| OPA2134 | 出力電流制限（本文） | 約 36 / −30 mA、温度で低下 | 一致 | 同左。p.15 §6.2.5 | "Output current is limited by internal circuitry to approximately sourcing 36mA and sinking –30mA at 25°C. …" |
| OPA2134 | 出力短絡（絶対最大） | Continuous（GND、1 パッケージ 1 回路） | 一致 | 同左。p.5、注 (3) | "Short-circuit to ground, one amplifier per package." |

### 5. OPA1656（TI_OPA1656.pdf, SBOS901C）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA1656 | 電源電圧（推奨動作） | ±2.25〜±18 V、4.5〜36 V | 一致 | 同左。p.4 §6.3、MIN/MAX 列 | `Single supply 4.5 36` / `Dual supply ±2.25 ±18` |
| OPA1656 | 電源電圧（絶対最大） | 40 V | 一致 | 同左。p.4 §6.1 | `Supply voltage, VS = (V+) – (V–) 40` |
| OPA1656 | 静止電流 | typ 3.9 / max 4.6 mA（per channel）、全温度 max 5.0 | 一致 | 同左。p.7。25°C 行の条件は VS = ±2.25〜±18 V、温度行は注 (2) "Specified by design and characterization." | `IQ … IO = 0 A, VS = ±2.25 V to ±18 V 3.9 4.6` / `IO = 0 A, TA = –40°C to +125°C 5.0` |
| OPA1656 | 出力電圧振幅 | (V–)+0.25〜(V+)–0.25、**±18 V** | 一致 | 同左。p.7、MIN/MAX 列。表見出しは "VS = ±18 V, RL = 2 kΩ" | `VO Voltage output (V–) + 0.25 (V+) – 0.25 V` |
| OPA1656 | 参考: AOL の試験条件 | 600 Ω: ±1.3、2 kΩ: ±0.5 V 内側、min 134 dB | 一致 | 同左。p.6、MIN/TYP 134/150、134/154 | `(V–) + 1.3 V ≤ VO ≤ (V+) – 1.3 V RL = 600 Ω 134 150` |
| OPA1656 | 本文の記述 | 2 kΩ でレールから 250 mV 以内 | 一致 | 同左。p.1 §3 | "rail-to-rail output swing to within 250 mV of the power supplies with a 2‑kΩ load" |
| OPA1656 | グラフ: 出力電圧 vs 出力電流 | 18/−18 V から、25°C で約 90 / 100 mA で急落 | 一致 | p.13 Figure 6-32/6-33。縦軸は 12〜18 V と −18〜−12 V で、曲線は 18 / −18 から始まる。25°C の急落は吐き 約 88〜90 mA、吸い 約 98〜100 mA。ページ既定は ±15 V、図中に電源の記載なし（opamps.md の注記どおり） | 図題 "Output Voltage vs Output Current (Sourcing)" / "(Sinking)" |
| OPA1656 | グラフ: 最大出力電圧 vs 周波数 | ±18 V 約 36、±15 V 約 30（縦軸 "VP"） | 一致 | p.8 Figure 6-4。自分の読み 35.7 / 30.0。縦軸ラベルは "Output Voltage (VP)" | 凡例 "Vs=±18 V / Vs=±15 V / Vs=±2.25 V" |
| OPA1656 | 同相入力電圧範囲 | (V–)〜(V+)–2.25 V | 一致 | 同左。p.6、MIN/MAX 列 | `VCM Common-mode voltage range (V–) (V+) – 2.25` |
| OPA1656 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.4 | `Input (V–) – 0.5 (V+) + 0.5` / `Input (all pins except power-supply pins) –10 10 mA` |
| OPA1656 | 差動入力（絶対最大） | 規定なし | 一致 | p.4 に項目なし。本文にも入力間ダイオードの記述なし | — |
| OPA1656 | 入力保護（本文） | ESD 用 current-steering diodes | 一致 | 同左。p.16（§7.3.2 Electrical Overstress の続き。節の見出しは p.15） | "protection circuitry involves several current-steering diodes connected from the input and output pins …" |
| OPA1656 | 出力短絡電流 | typ ±100 mA（1 ch ずつ） | 一致 | 同左。p.7、TYP 列、注 (4) | `ISC Short-circuit current(4) ±100 mA`、"One channel at a time." |
| OPA1656 | 出力短絡（絶対最大） | Continuous（VS/2、1 パッケージ 1 回路） | 一致 | 同左。p.4、注 (2) | "Short-circuit to VS / 2 (groundinsymmetrical dual-supply setups), one amplifier per package." |

### 6. OPA2604（TI_OPA2604.pdf, SBOS006A）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA2604 | 電源電圧（推奨動作） | ±4.5 / ±15 / ±24 V | 一致 | 同左。p.4 §6.3、MIN/NOM/MAX 列 | `V+, V– Power supply voltage ±4.5 ±15 ±24 V` |
| OPA2604 | 電源電圧（電気的特性表） | ±4.5〜±24 V、Specified ±15 V | 一致 | 同左。p.5。Operating は MIN/MAX 列、Specified は TYP 列 | `Operating voltage range ±4.5 ±24` / `Specified operating voltage ±15` |
| OPA2604 | 電源電圧（絶対最大） | ±25 V | 一致 | 同左。p.4、MAX 列 | `Power supply voltage ±25` |
| OPA2604 | 静止電流 | typ ±10.5 / max ±12 mA（total both） | 一致 | 同左。p.5、TYP/MAX 列 | `Current, total both amplifiers IO = 0 ±10.5 ±12 mA` |
| OPA2604 | 出力電圧振幅 | min ±11 / typ ±12 V、600 Ω | 一致 | 同左。p.5、MIN/TYP 列 | `Voltage output RL = 600 Ω ±11 ±12 V` |
| OPA2604 | 出力電流 | typ ±35 mA、VO = ±12 V | 一致 | 同左。p.5、TYP 列 | `Current output VO = ±12 V ±35 mA` |
| OPA2604 | グラフ: 最大出力電圧振幅 vs 周波数 | 低域で約 **26** Vp-p | **誤り（目読み）** | p.8 Figure 15。平坦部は **24 Vp-p の目盛線の上**にある（細目盛 2 Vp-p、ピクセル換算 24.0）。26 Vp-p の目盛線は曲線より上。24 Vp-p は表の 600 Ω typ ±12 V と同じ値 | 図題 "Maximum Output Voltage Swing vs Frequency"、図中 "VS = ±15V" |
| OPA2604 | 同相入力電圧範囲 | min ±12 / typ ±13 V | 一致 | 同左。p.5 | `Common-mode input range ±12 ±13 V` |
| OPA2604 | 入力電圧（絶対最大） | (V–)–1〜(V+)+1 V | 一致 | 同左。p.4 | `Input voltage (V–)–1 (V+)+1 V` |
| OPA2604 | 差動入力（絶対最大） | 規定なし | 一致 | p.4 に項目なし | — |
| OPA2604 | 出力短絡電流 | typ ±40 mA | 一致 | 同左。p.5、TYP 列 | `Short circuit current ±40 mA` |
| OPA2604 | 出力短絡（絶対最大） | Continuous（GND） | 一致 | 同左。p.4 | `Output short-circuit to ground Continuous` |

### 7. LME49860（TI_LME49860.pdf, SNAS389C）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| LME49860 | 電源電圧（動作） | ±2.5〜±22 V | 一致 | 同左。p.3 OPERATING RATINGS | `Supply Voltage Range ±2.5V ≤ VS ≤ ±22V` |
| LME49860 | 電源電圧（絶対最大） | 46 V | 一致 | 同左。p.3 | `Power Supply Voltage (VS = V+ - V-) 46V` |
| LME49860 | 静止電流 | ±18 V typ 10.2、±22 V typ 10.5 / Limit 13 mA | 一致 | 同左。p.4、Typical/Limit 列 | `IS Total Quiescent Current IOUT = 0mA VS = ±18V 10.2` / `VS = ±22V 10.5 13 mA (max)` |
| LME49860 | 出力振幅（600 Ω） | ±16.7 / ±20.4、Limit ±19.0 (min) | 一致 | 同左。p.4。Limit は ±22 V の行だけ | `RL = 600Ω VS = ±18V ±16.7` / `VS = ±22V ±20.4 ±19.0 V (min)` |
| LME49860 | 出力振幅（2 kΩ） | ±17.0 / ±21.0（Limit なし） | 一致 | 同左。p.4 | `RL = 2kΩ … ±17.0 / ±21.0` |
| LME49860 | 出力振幅（10 kΩ） | ±17.1 / ±21.2（Limit なし） | 一致 | 同左。p.4 | `RL = 10kΩ … ±17.1 / ±21.2` |
| LME49860 | グラフ: vs 負荷抵抗（±15 V） | 600 Ω 9.9、2 kΩ 10.1、10 kΩ 10.2 Vrms | 一致 | p.20 Figure 95。自分の読み 9.9 / 10.1 / 10.2 Vrms | 図題 "Output Voltage vs Load Resistance VCC = 15V, VEE = –15V THD+N = 1%" |
| LME49860 | グラフ: vs 負荷抵抗（±12 V） | 7.8 / 7.9 / 8.0 Vrms | 一致 | p.20 Figure 96。自分の読み 7.80 / 7.93 / 8.03 Vrms | 図題 "…VCC = 12V, VEE = –12V THD+N = 1%" |
| LME49860 | グラフ: vs 総電源電圧 | 3 枚、24 V で約 8 Vrms | 一致 | p.21 Figure 99–101。自分の読み（2 kΩ、24 V）約 8.1 Vrms | 図題 "Output Voltage vs Total Power Supply Voltage RL = 2kΩ, THD+N = 1%" |
| LME49860 | 同相入力電圧範囲 | ±18 V: +17.1 / −16.9、±22 V: +21.0 / −20.8、Limit ±2.0 V 内側 | 一致 | 同左。p.4、Typical/Limit 列 | `VS = ±18V +17.1 (V+) – 2.0 V (min) –16.9 (V-) + 2.0 V (min)` |
| LME49860 | 入力電圧（絶対最大） | (V-)–0.7〜(V+)+0.7 V | 一致 | 同左。p.3 | `Input Voltage (V-) - 0.7V to (V+) + 0.7V` |
| LME49860 | 差動入力（絶対最大） | 規定なし | 一致 | p.3 に項目なし。本文にも入力ダイオードの記述なし | — |
| LME49860 | 出力電流 | ±20 V typ ±31、±22 V typ ±37 / Limit ±30 mA | 一致 | 同左。p.4 | `IOUT Output Current RL = 600Ω VS = ±20V ±31` / `VS = ±22V ±37 ±30 mA (min)` |
| LME49860 | 瞬時短絡電流 | +53 / −42 mA | 一致 | 同左。p.4、Typical 列、条件欄は空（表の既定） | `IOUT-CC Instantaneous Short Circuit Current +53 –42 mA` |
| LME49860 | 出力短絡（絶対最大） | Continuous（何回路でも） | 一致 | 同左。p.3、注 (4) | "Amplifier output connected to GND, any number of amplifiers within a package." |

### 8. OPA1652（TI_OPA1652.pdf, SBOS477B）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA1652 | 電源電圧（推奨動作） | 4.5 (±2.25)〜36 (±18) V | 一致 | 同左。p.5 §6.3 | `Supply voltage 4.5 (±2.25) 36 (±18) V` |
| OPA1652 | 電源電圧（電気的特性表） | ±2.25〜±18 V | 一致 | 同左。p.7、MIN/MAX 列 | `VS Specified voltage ±2.25 ±18 V` |
| OPA1652 | 電源電圧（絶対最大） | 40 V | 一致 | 同左。p.5 §6.1 | `Supply voltage, VS = (V+) – (V–) 40` |
| OPA1652 | 静止電流 | typ 2 / max 2.5 mA（per channel）、全温度 2.8 | 一致 | 同左。p.7、温度行に注 (2) | `IQ Quiescent current (per channel) IOUT = 0 A 2 2.5 mA` / `…TA = –40°C to 85°C (2) 2.8 mA` |
| OPA1652 | 出力電圧振幅 | (V–)+0.8〜(V+)–0.8、±15 V | 一致 | 同左。p.7、MIN/MAX 列。表題 "6.6 Electrical Characteristics: VS = ±15 V" | `VOUT Voltage output RL = 2 kΩ (V–) + 0.8 (V+) – 0.8 V` |
| OPA1652 | 本文の記述 | 800 mV 以内、±30 mA | 一致 | 同左。p.1 §3 | "…rail-to-rail output swing to within 800 mV with a 2-kΩ load …" |
| OPA1652 | グラフ: 最大出力電圧 vs 周波数 | ±15 V で約 14.7 | 一致 | p.8 Figure 4。自分の読み 14.75。**注: 縦軸の目盛ラベルは 0, 2, 5, 8, 10, 12, 15, 18, 20 と不等間隔に見えるが、目盛線は等間隔（2.5 V 刻みを丸めた表記）** | 図題 "Maximum Output Voltage vs Frequency" |
| OPA1652 | グラフ: 出力電圧 vs 出力電流 | 0 mA 付近で約 ±35（値として採れない） | 一致 | p.12 Figure 27。自分の読み +35.8 / −35.8。縦軸 ±40、図中に電源の記載なし（opamps.md の注記どおり） | 図題 "Output Voltage vs Output Current"、縦軸 "Output Volage Swing (V)" |
| OPA1652 | 同相入力電圧範囲 | (V–)+0.5〜(V+)–2 V | 一致 | 同左。p.7 | `VCM Common-mode voltage range (V–) + 0.5 (V+) – 2 V` |
| OPA1652 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.5 | `Input (V–) – 0.5 (V+) + 0.5` / `Input (all pins except power-supply pins) –10 10 mA` |
| OPA1652 | 差動入力（絶対最大） | 規定なし | 一致（補足あり） | 絶対最大の表に項目が無いのは同左。**ただし p.15 §7.3.2 に「入力間は back-to-back ダイオードで過大な差動電圧から保護」とあり、順バイアス時は入力電流を 10 mA 以下に制限せよと書かれている**（末尾の節） | "The input terminals of the OPA1652 and OPA1654 are protected from excessive differential voltage with back-to-back diodes, as Figure 36 illustrates." |
| OPA1652 | 出力電流 | See Typical Characteristics | 一致 | 同左。p.7 | `IOUT Output current See Typical Characteristics mA` |
| OPA1652 | 出力短絡電流 | typ ±50 mA（1 ch ずつ） | 一致 | 同左。p.7、注 (3) | `ISC Short-circuit current (3) ±50 mA` |
| OPA1652 | 出力短絡（絶対最大） | Continuous（VS/2、1 パッケージ 1 回路） | 一致 | 同左。p.5、注 (2) | "Short-circuit to VS / 2 (ground in symmetrical dual supply setups), one amplifier per package." |

### 9. OPA627（TI_OPA627.pdf, SBOS165C、§5.6 OPA627BU/AU）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA627 | 電源電圧（推奨動作） | ±4.5/±15/±18、9/30/36 V | 一致 | 同左。p.4 §5.3、MIN/NOM/MAX 列 | `Single supply 9 30 36` / `Dual supply ±4.5 ±15 ±18` |
| OPA627 | 電源電圧（絶対最大） | 36 V、±18 V | 一致 | 同左。p.4 §5.1、MAX 列 | `Single supply 36` / `Dual supply ±18` |
| OPA627 | 静止電流 | typ 7 / max 7.5 mA（per amplifier） | 一致 | 同左。p.7、TYP/MAX 列 | `IQ Quiescent current per amplifier IO = 0mA 7 7.5 mA` |
| OPA627 | 出力電圧振幅（25°C） | min ±11.5 / typ ±12.3 V、RL = 1 kΩ | 一致 | 同左。p.7、MIN/TYP 列 | `VO Output voltage RL = 1kΩ ±11.5 ±12.3` |
| OPA627 | 出力電圧振幅（全温度） | min ±11 / typ ±11.5 V | 一致 | 同左。p.7 | `TA = –25°C to +85°C ±11 ±11.5` |
| OPA627 | 出力電流 | typ ±30 mA、−10〜+10 V | 一致 | 同左。p.7、TYP 列 | `IO Current output –10V < VO < +10V ±30 mA` |
| OPA627 | グラフ: 最大出力電圧 vs 周波数 | 約 25 Vp-p、条件「VS = ±15 V、**RL = 10 kΩ**」 | **条件の誤り** | 値は一致（自分の読み 24.9 Vp-p）。**p.16 のページ既定は "at TA = 25°C and VS = ±15V (unless otherwise noted)" だけで、図にも負荷の記載は無い**。RL = 10 kΩ は §5.6 の電気的特性表の既定で、このグラフには付いていない | p.16 見出し "at TA = 25°C and VS = ±15V (unless otherwise noted)"、図題 "Figure 5-23. Maximum Output Voltage vs Frequency" |
| OPA627 | 同相入力電圧範囲 | 25°C ±11/±11.5、全温度 ±10.5/±11 V | 一致 | 同左。p.6、MIN/TYP 列 | `VCM Common-mode voltage ±11 ±11.5` / `TA = –25°C to +85°C ±10.5 ±11` |
| OPA627 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.4 | `Input voltage Common-mode (V–) – 0.5 (V+) + 0.5` / `Input pin current ±10` |
| OPA627 | 差動入力（絶対最大） | (V+)–(V–) | 一致 | 同左。p.4、MAX 列 | `Differential (V+) – (V–)` |
| OPA627 | 入力保護（本文） | +VS+0.5〜–VS–0.5 V | 一致 | 同左。p.23 §6.3.7 | "The inputs of the OPA6x7 are protected for voltages from +VS + 0.5V to –VS – 0.5V. …" |
| OPA627 | 出力短絡電流 | typ ±45 mA | 一致 | 同左。p.7、TYP 列 | `ISC Short-circuit current ±45 mA` |

### 10. OPA1612（TI_OPA1612.pdf, SBOS450C）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA1612 | 電源電圧（推奨動作） | 4.5 (±2.25)〜36 (±18) V | 一致 | 同左。p.4 §6.3 | `Supply voltage (V+ – V–) 4.5 (±2.25) 36 (±18) V` |
| OPA1612 | 電源電圧（電気的特性表） | ±2.25〜±18 V | 一致 | 同左。p.6（§6.4 の続き） | `VS Specified voltage ±2.25 ±18 V` |
| OPA1612 | 電源電圧（絶対最大） | 40 V | 一致 | 同左。p.4 §6.1 | `Supply voltage VS = (V+) – (V–) 40` |
| OPA1612 | 静止電流 | typ 3.6 / max 4.5 mA、全温度 5.5 | 一致 | 同左。p.6、注 (3) | `IQ Quiescent current (per channel) IOUT = 0 A 3.6 4.5` / `IQ over Temperature (3) TA = –40°C to +85°C 5.5` |
| OPA1612 | 出力電圧振幅（10 kΩ） | (V–)+0.2〜(V+)–0.2、AOL ≥ 114 dB | 一致 | 同左。p.6、MIN/MAX 列。表題 "VS = ±2.25 V to ±18 V" | `RL = 10 kΩ, AOL ≥ 114 dB (V–) + 0.2 (V+) – 0.2` |
| OPA1612 | 出力電圧振幅（2 kΩ） | (V–)+0.6〜(V+)–0.6、AOL ≥ 110 dB | 一致 | 同左。p.6 | `RL = 2 kΩ, AOL ≥ 110 dB (V–) + 0.6 (V+) – 0.6` |
| OPA1612 | 本文の記述 | 600 mV 以内 | 一致 | 同左。p.1 §3 | "…rail-to-rail output swing to within 600 mV with a 2-kΩ load" |
| OPA1612 | グラフ: 出力電圧 vs 出力電流 | 25°C、0〜約 45 mA で約 +14.1 / **−14.6** V | **誤り（目読み）** | p.11 Figure 27（縦軸は 13〜15 と −13〜−15 の途切れ軸、細目盛 0.5 V）。自分の読み（ピクセル換算）: 正側 **+14.35（0 mA）〜+14.2（43 mA）**、負側 **−14.35（0 mA）〜−14.0（43 mA）**。負側は −14.6 の線（−14.5 と −15 の間）まで届いていない。正側 +14.1 は許容内 | 図中 "VS = ±15V / Dual version with both channels driven simultaneously" |
| OPA1612 | グラフ: 最大出力電圧 vs 周波数 | ±15 V で約 28.8 Vpp | 一致 | p.7 Figure 4。自分の読み 28.8 Vpp | 縦軸 "Output Voltage (VPP)" |
| OPA1612 | 同相入力電圧範囲 | (V–)+2〜(V+)–2 V | 一致 | 同左。p.5 §6.4 | `VCM Common-mode voltage range (V–) + 2 (V+) – 2 V` |
| OPA1612 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.4 | `Input voltage (V–) – 0.5 (V+) + 0.5 V` / `Input current (all pins except power-supply pins) ±10 mA` |
| OPA1612 | 差動入力（絶対最大） | 規定なし（差動入力インピーダンス 20k ‖ 8） | 一致（補足あり） | 絶対最大に項目が無いこと、インピーダンス値は同左（p.5）。**ただし p.14 §7.3.4 に「入力間は back-to-back ダイオードで保護」の記述がある**（末尾の節） | "The input terminals of the OPA1611 and the OPA1612 are protected from excessive differential voltage with back-to-back diodes, as Figure 31 shows." |
| OPA1612 | 出力電流 | See Figure 27 | 一致 | 同左。p.6 | `IOUT Output current See Figure 27 mA` |
| OPA1612 | 出力短絡電流 | +55 / −62 mA | 一致 | 同左。p.6、TYP 列。条件欄は空 | `ISC Short-circuit current +55 mA` / `–62 mA` |
| OPA1612 | 出力短絡（絶対最大） | Continuous（VS/2、1 パッケージ 1 回路） | 一致 | 同左。p.4、注 (2) | "Short-circuit to VS / 2 (ground in symmetrical dual supply setups), one amplifier per package." |

### 11. LT1364（AD_LT1364.pdf）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| LT1364 | 電源電圧（推奨動作） | 節なし、±2.5/±5/±15 V で規定 | 一致 | 推奨動作の節は無い（p.2 は Operating/Specified Temperature Range のみ）。p.1 特長に同左 | `Specified at ±2.5V, ±5V, and ±15V` |
| LT1364 | 電源電圧（絶対最大） | 36 V | 一致 | 同左。p.2 | `Total Supply Voltage (V+ to V–) … 36V` |
| LT1364 | 静止電流 | ±15 V 6.3/7.5、±5 V 6.0/7.2、0〜70°C 8.7/8.4、–40〜85°C 9.0/8.7 mA | 一致 | 同左。p.3（TYP/MAX）、p.4・p.5（MAX）、Each Amplifier | `IS Supply Current Each Amplifier ±15V 6.3 7.5 mA` |
| LT1364 | 出力振幅（25°C） | 13.5/14.0、13.0/13.7、3.5/4.1、3.4/3.8、1.3/1.7 ±V | 一致 | 同左。p.3、MIN/TYP 列、単位 ±V | `VOUT Output Swing RL = 1k, VIN = ±40mV ±15V 13.5 14.0 ±V` |
| LT1364 | 出力振幅（0〜70°C） | 13.4、12.8、3.4、3.3、1.2 | 一致 | 同左。p.4、MIN 列（●） | `RL = 1k … ±15V ● 13.4` / `RL = 500Ω … ±15V ● 12.8` |
| LT1364 | 出力振幅（–40〜85°C） | 13.4、12.7、3.4、3.2、1.2 | 一致 | 同左。p.5、MIN 列、見出しに (Note 9) | `RL = 500Ω, VIN = ±40mV ±15V ● 12.7` |
| LT1364 | 出力（特長） | 150 Ω へ min ±7.5 V、±15 V | 一致 | p.1。特長の行には電源の記載が無いが、同じページの本文に "with ±15V supplies" | `±7.5V Minimum Output Swing into 150Ω` / "Each output drives a 150Ω load to ±7.5V with ±15V supplies" |
| LT1364 | グラフ: 振幅 vs 電源電圧 | ±12 V で 正 1k 1.25 / 500 Ω 1.35、負 1k 1.28 / 500 Ω 1.47 V | 一致 | p.6。自分の読み 正 1.22 / 1.33、負 1.29 / 1.49 V | 図題 "Output Voltage Swing vs Supply Voltage"、図中 TA = 25°C |
| LT1364 | グラフ: 振幅 vs 負荷電流 | ±5 V のみ | 一致 | 同左。p.6 | 図中 "VS = ±5V, VIN = 100mV" |
| LT1364 | 同相入力範囲（+） | 12.0/13.4、2.5/3.4、0.5/1.1 V | 一致 | 同左。p.3、MIN/TYP 列 | `Input Voltage Range + ±15V 12.0 13.4 V` |
| LT1364 | 同相入力範囲（−） | −13.2/−12.0 など、TYP/MAX 列 | 一致 | 同左。p.3。保証値は MAX 列（−12.0） | `Input Voltage Range – ±15V –13.2 –12.0 V` |
| LT1364 | 入力電圧（絶対最大） | ±VS | 一致 | 同左。p.2 | `Input Voltage … ±VS` |
| LT1364 | 差動入力（絶対最大） | ±10 V（過渡のみ） | 一致 | 同左。p.2、Note 2 は p.5 | "Differential inputs of ±10V are appropriate for transient operation only, …" |
| LT1364 | 入力保護（本文） | 10 V までの過渡差動入力に耐える | 一致 | 同左。p.9 Input Considerations | "The inputs can withstand transient differential input voltages up to 10V without damage …" |
| LT1364 | 出力電流 | 25°C 50/60・23/29、0〜70°C 25・22、–40〜85°C 25・21 mA | 一致 | 同左。p.3・p.4・p.5。温度表の VOUT 条件（±12.8/±3.3、±12.7/±3.2 V）も同左 | `IOUT Output Current VOUT = ±7.5V ±15V 50 60 mA` / `VOUT = ±12.8V ±15V ● 25` |
| LT1364 | 出力短絡電流 | 70/105、55、50 mA | 一致 | 同左。p.3・p.4・p.5 | `ISC Short-Circuit Current VOUT = 0V, VIN = ±3V ±15V 70 105 mA` |
| LT1364 | 出力短絡（絶対最大） | Indefinite（Note 3） | 一致 | 同左。p.2、Note 3 は p.5 | "A heat sink may be required to keep the junction temperature below absolute maximum when the output is shorted indefinitely." |

### 12. OPA2140（TI_OPA2140.pdf, SBOS498F）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA2140 | 電源電圧（推奨動作） | ±2.25〜±18 V、4.5〜36 V | 一致 | 同左。p.5 §6.3 | `Dual supply ±2.25 ±18` / `Single supply 4.5 36` |
| OPA2140 | 電源電圧（絶対最大） | ±20 V、40 V | 一致 | 同左。p.5 §6.1 | `Dual supply ±20` / `Single supply 40` |
| OPA2140 | 静止電流 | typ 1.8 / max 2、全温度 2.7 mA | 一致 | 同左。p.8 §6.7 の続き | `IQ Quiescent current per amplifier IO = 0 mA 1.8 2` / `TA = –40°C to +125°C 2.7` |
| OPA2140 | 出力振幅（10 kΩ） | (V–)+0.2〜(V+)–0.2 | 一致 | 同左。p.7、MIN/MAX 列。表見出し "VS = 4.5 V (±2.25) to 36 V (±18 V)" | `RL = 10 kΩ, AOL ≥ 108 dB (V–) + 0.2 (V+) – 0.2` |
| OPA2140 | 出力振幅（2 kΩ） | (V–)+0.35〜(V+)–0.35 | 一致 | 同左。p.7 | `RL = 2 kΩ, AOL ≥ 108 dB (V–) + 0.35 (V+) – 0.35` |
| OPA2140 | グラフ: 振幅 vs 出力電流 | 25°C、約 30 mA まで約 +17.5 / −17.7 V | 一致 | p.10 Figure 6-6。自分の読み 正 +17.8（3 mA）〜+17.6（28 mA）、負 −17.75〜−17.65 V（細目盛 0.5 V、許容内） | 図題 "Output Voltage Swing vs Output Current (Maximum Supply)" |
| OPA2140 | 同相入力電圧範囲 | (V–)–0.1〜(V+)–3.5 V、全温度 | 一致 | 同左。p.7 | `VCM Common-mode voltage TA = –40°C to +125°C (V–) – 0.1 (V+) – 3.5 V` |
| OPA2140 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.5、注 (2) | "Input pins are diode-clamped to the power-supply rails. …" |
| OPA2140 | 差動入力（絶対最大） | 規定なし | 一致 | p.5 に項目なし。本文にも入力間ダイオードの記述なし | — |
| OPA2140 | 出力短絡電流 | +36 / −30 mA | 一致 | 同左。p.7、TYP 列 | `ISC Short-circuit current Source 36` / `Sink –30` |
| OPA2140 | 出力短絡（絶対最大） | Continuous（VS/2、1 パッケージ 1 回路） | 一致 | 同左。p.5、注 (3) | "Short-circuit to VS / 2 (ground in symmetrical dual-supply setups), one amplifier per package." |

### 13. OPA828（TI_OPA828.pdf, SBOS671D）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| OPA828 | 電源電圧（推奨動作） | ±4〜±18 V、8〜36 V | 一致 | 同左。p.4 §6.3 | `Single supply 8 36` / `Dual supply ±4 ±18` |
| OPA828 | 電源電圧（絶対最大） | ±20 V、40 V | 一致 | 同左。p.4 §6.1 | `Single-supply 40` / `Dual-supply ±20` |
| OPA828 | 静止電流 | typ 5.5 / max 6.2、7.1、7.9 mA | 一致 | 同左。p.6、TYP/MAX 列 | `IQ Quiescent current (per amplifier) IO = 0 A 5.5 6.2` / `7.1` / `7.9` |
| OPA828 | 出力振幅（10 kΩ） | typ 0.9 / max 1.2 V（基準の文言なし） | 一致 | 同左。p.6、TYP/MAX 列 | `Output voltage swing RL = 10 kΩ 0.9 1.2 V` |
| OPA828 | 出力振幅（600 Ω） | typ 1.2 V | 一致 | 同左。p.6、TYP 列（MAX 空） | `RL = 600 Ω 1.2` |
| OPA828 | 参考: AOL の試験条件 | 600 Ω ±1.6、10 kΩ ±1.5 V 内側、min 120 dB | 一致 | 同左。p.6 | `(V–) + 1.6 V< VO < (V+) – 1.6 V, RL = 600 Ω 120 130` |
| OPA828 | グラフ: 振幅 vs 吐き出し電流 | 約 +13 V、約 48 mA まで平坦 | 一致 | p.10 Figure 6-18。同左。**注: Typical Characteristics のページ既定は VS = ±18 V だが、この図は図下に VS = ±15 V と明記**（opamps.md の条件どおり） | 図下 "VS = ±15 V" |
| OPA828 | グラフ: 振幅 vs 吸い込み電流 | 約 −13 V、約 49 mA まで平坦 | 一致 | p.11 Figure 6-19。同左 | 図下 "VS = ±15 V" |
| OPA828 | 同相入力電圧範囲 | (V–)+2.5〜(V+)–3.5 V | 一致 | 同左。p.5 | `VCM Common-mode voltage (V–) + 2.5 (V+) – 3.5 V` |
| OPA828 | 入力電圧（絶対最大） | (V–)–0.5〜(V+)+0.5、±10 mA | 一致 | 同左。p.4、注 (3) | "Input terminals are diode-clamped to the power-supply rails. …" |
| OPA828 | 差動入力（絶対最大） | (V+)–(V–)、逆並列ダイオードなし | 一致 | 同左。p.4、注 (2) | "Input terminals are not clamped to each other with anti-parallel diodes. …" |
| OPA828 | 出力電流 | typ ±30 mA | 一致 | 同左。p.6 | `IO Output current For linear operation, AOL ≥ 120 dB ±30 mA` |
| OPA828 | 出力短絡電流 | typ ±50 mA | 一致 | 同左。p.6 | `ISC Short-circuit current ±50 mA` |
| OPA828 | 出力短絡（絶対最大） | Continuous（GND、1 パッケージ 1 回路） | 一致 | 同左。p.4、注 (4) | "Short circuit to ground, one amplifier per package." |

### 14. MUSES01（NJR_MUSES01.pdf, 20250321）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| MUSES01 | 電源電圧（推奨動作） | ±9 / ±16 V | 一致 | 同左。p.2、MIN/MAX 列、Ta=25°C | `Supply Voltage V+/V- - ±9 - ±16 V` |
| MUSES01 | 電源電圧（特長） | ±9〜±16 V | 一致 | 同左。p.1 | `Operating Voltage Vopr=±9V to ±16V` |
| MUSES01 | 電源電圧（絶対最大） | ±18 V | 一致 | 同左。表は p.2、見出し "(Ta=25°C)" は p.1 末尾 | `Supply Voltage V+/V- ±18 V` |
| MUSES01 | 静止電流 | typ 8.5 / max 12.0 mA | 一致 | 同左。p.2 | `Operating Current Icc No Signal, RL=∞ - 8.5 12.0 mA` |
| MUSES01 | 出力電圧振幅 1 | min ±12 / typ ±13.5 V、10 kΩ | 一致 | 同左。p.2 | `Max Output Voltage 1 VOM1 RL=10kΩ ±12 ±13.5` |
| MUSES01 | 出力電圧振幅 2 | min ±10 / typ ±12.5 V、2 kΩ | 一致 | 同左。p.2 | `Max Output Voltage 2 VOM2 RL=2kΩ ±10 ±12.5` |
| MUSES01 | グラフ: vs 温度（2 kΩ） | ±15: +14/−13.3、±16: +15/−14.5、±9: +8/−7.4 V | 一致 | p.11。自分の読み ±15: +14.05/−13.2、±16: +15.0/−14.2、±9: +8.1/−7.4 V（細目盛 1 V 程度、許容内） | 図題 "…vs TEMPERATURE (SUPPLY VOLTAGE) Gv=open,RL=2kohm to 0V" |
| MUSES01 | グラフ: vs 温度（10 kΩ） | ±15: +14/−13.5 V | 一致 | p.11。自分の読み +14.3 / −13.5 V | 図題 "…Gv=open,RL=10kohm to 0V" |
| MUSES01 | グラフ: vs 負荷抵抗 | 3 枚、±15 V・2 kΩ で約 **+13.5** / −13 V | **誤り（目読み・軽微）** | p.10（±16、±15）と p.11（±9）の 3 枚は同左。±15 V の図で 2 kΩ の値は、自分の読みで **+14.0 / −13.2〜−13.4 V**（細目盛 1 V、正側のずれ 0.5 V は許容の上限）。**opamps.md 自身の温度グラフの行（2 kΩ・25°C・±15 V で +14）とも合わない** | 図題 "MAXIMUM OUTPUT VOLTAGE vs LOAD RESISTANCE (TEMPERATURE) V+/V-=±15V,Gv=open,RL to 0V" |
| MUSES01 | 同相入力電圧範囲 | min ±8 / typ ±9.5 V | 一致 | 同左。p.2 | `Input Common Mode Voltage Range VICM CMR≥60dB ±8 ±9.5` |
| MUSES01 | 同相入力電圧（絶対最大） | ±15 V（Note1） | 一致 | 同左。p.2 | "(Note1) For supply Voltages less than ±15 V, the maximum input voltage is equal to the Supply Voltage." |
| MUSES01 | 差動入力（絶対最大） | ±30 V | 一致 | 同左。p.2 | `Differential Input Voltage VID ±30 V` |
| MUSES01 | 出力電流（絶対最大） | ±25 mA | 一致 | 同左。p.2 | `Output Current IO ±25 mA` |

### 15. MUSES02（NJR_MUSES02.pdf, 20250319）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| MUSES02 | 電源電圧（推奨動作） | ±3.5 / ±16 V | 一致 | 同左。p.2、MIN/MAX 列 | `Supply Voltage V+/V- - ±3.5 - ±16 V` |
| MUSES02 | 電源電圧（絶対最大） | ±18 V | 一致 | 同左。p.2 | `Supply Voltage V+/V- ±18 V` |
| MUSES02 | 静止電流 | typ 8.0 / max 12.0 mA | 一致 | 同左。p.2 | `Operating Current Icc No Signal, RL=∞ - 8.0 12.0 mA` |
| MUSES02 | 出力電圧振幅 | min ±12 / typ ±13.5 V、2 kΩ | 一致 | 同左。p.2 | `Max Output Voltage VOM RL=2kΩ ±12 ±13.5` |
| MUSES02 | グラフ: vs 温度 | ±15: +14/−13.3、±16: +15/−14.3、±3.5: +2.7/−1.8 V | 一致 | p.11。自分の読み ±15: +14.0/−13.4、±16: +15.1/−14.3、±3.5: +2.7/−2.1 V（細目盛 2 V、許容内） | 図題 "Maximum Output Voltage vs. Temperature (Supply Voltage) GV=open,RL=2k,RL to 0V" |
| MUSES02 | グラフ: vs 負荷抵抗 | 3 枚、±15 V・2 kΩ で約 +14 / −13.3 V | 一致 | p.10（±16、±15）と p.11（±3.5）。自分の読み +14.1 / −13.3〜−13.45 V | 図題 "Maximum Output Voltage vs. Load Resistance (Temperature) V+/V-=±15V, GV=open, RL to 0V" |
| MUSES02 | 同相入力電圧範囲 | min ±12 / typ ±13.5 V | 一致 | 同左。p.2 | `VICM CMR≥80dB ±12 ±13.5` |
| MUSES02 | 同相入力電圧（絶対最大） | ±15 V（Note1） | 一致 | 同左。p.2 | "(Note1) For supply Voltages less than ±15 V, …" |
| MUSES02 | 差動入力（絶対最大） | ±30 V | 一致 | 同左。p.2 | `Differential Input Voltage VID ±30 V` |
| MUSES02 | 出力電流（絶対最大） | ±50 mA | 一致 | 同左。p.2 | `Output Current IO ±50 mA` |

### 16. MUSES03（NJR_MUSES03.pdf, Ver.4.2）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| MUSES03 | 電源電圧（推奨動作） | ±3.5〜±18 V | 一致 | 同左。p.2 | `推奨動作条件 電源電圧 V+-V- ±3.5 to ±18 V` |
| MUSES03 | 電源電圧（絶対最大） | ±19 V | 一致 | 同左。p.2 | `電源電圧 V+-V- ±19 V` |
| MUSES03 | 静止電流 | typ 5.8 / max 10 mA | 一致 | 同左。p.4、標準/最大列 | `消費電流 Icc RL=∞, 無信号時 - 5.8 10 mA` |
| MUSES03 | 出力電圧振幅 1 | ±13.0 / ±14.0 V、10 kΩ | 一致 | 同左。p.4、最小/標準列 | `最大出力電圧 1 VOM1 RL=10kΩ ±13.0 ±14.0` |
| MUSES03 | 出力電圧振幅 2 | ±12.8 / ±13.8 V、2 kΩ | 一致 | 同左。p.4 | `最大出力電圧 2 VOM2 RL=2kΩ ±12.8 ±13.8` |
| MUSES03 | 出力電圧振幅 3 | ±12.5 / ±13.5 V、600 Ω | 一致 | 同左。p.4。記号が VOM2 のまま（原文どおり） | `最大出力電圧 3 VOM2 RL=600Ω ±12.5 ±13.5` |
| MUSES03 | 参考: 電圧利得の試験条件 | Vo = ±13 / ±12.8 / ±12.5 V、min 90 dB | 一致 | 同左。p.4 | `電圧利得 2 AV2 RL=2kΩ, Vo=±12.8V 90 115` |
| MUSES03 | グラフ: vs 負荷抵抗／vs 出力電流 | ±15 V のみ、1 kΩ 以上で約 ±14 V | 一致 | p.6。150 dpi で確認し、自分の読み 1 kΩ で +14.2 / −14.2 V | 図題 "Output Voltage vs. Load Resistance V+/V-=±15V, VIN=±1V" |
| MUSES03 | 同相入力電圧範囲 | ±12.0 / ±13.0 V | 一致 | 同左。p.4 | `同相入力電圧範囲 VICM CMR≥70dB ±12.0 ±13.0` |
| MUSES03 | 同相入力電圧（絶対最大） | ±18 V（注 1） | 一致 | 同左。p.2 | 「(注 1) 電源電圧が±18V 以下の場合は、電源電圧と等しくなります。」 |
| MUSES03 | 差動入力（絶対最大） | ±6 V | 一致 | 同左。p.2 | `差動入力電圧 VID ±6 V` |
| MUSES03 | 最大出力尖頭電流（絶対最大） | 250 mA | 一致 | 同左。p.2 | `最大出力尖頭電流 IOP 250 mA` |
| MUSES03 | 使用上の注意（出力） | 保護抵抗、例 18 V/0.2 A = 90 Ω 以上 | 一致 | 同左。p.4 | 「出力端子の短絡など、出力電流が瞬間的に絶対最大定格の 250mA を越える可能性がある場合には、…」 |

### 17. AD797（AD_AD797.pdf, Rev. K）

| 石 | 項目 | opamps.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| AD797 | 電源電圧（動作範囲） | ±5〜±18 V | 一致 | 同左。p.4 Table 2 の続き、A・B とも MIN/MAX 列 | `Operating Range ±5 ±18 ±5 ±18 V` |
| AD797 | 電源電圧（特長） | ±5 V と ±15 V で規定 | 一致 | 同左。p.1 | "Specified for ±5 V and ±15 V power supplies" |
| AD797 | 電源電圧（絶対最大） | ±18 V | 一致 | 同左。p.5 Table 3 | `Supply Voltage ±18 V` |
| AD797 | 静止電流 | typ 8.2 / max 10.5 mA | 一致 | 同左。p.4、A・B とも | `Quiescent Current ±5 V, ±15 V 8.2 10.5 8.2 10.5 mA` |
| AD797 | 出力電圧振幅（2 kΩ） | ±12 / ±13 V | 一致 | 同左。p.3 Table 2、A・B とも MIN/TYP 列 | `RLOAD = 2 kΩ ±15 V ±12 ±13 ±12 ±13` |
| AD797 | 出力電圧振幅（600 Ω、±15 V） | ±11 / ±13 V | 一致 | 同左。p.3 | `RLOAD = 600 Ω ±15 V ±11 ±13 ±11 ±13` |
| AD797 | 出力電圧振幅（600 Ω、±5 V） | ±2.5 / ±3 V | 一致 | 同左。p.3 | `RLOAD = 600 Ω ±5 V ±2.5 ±3 ±2.5 ±3` |
| AD797 | グラフ: 振幅 vs 電源電圧 | ±12 V で約 10.8（−VOUT）/ 10.4（+VOUT）、負荷記載なし | 一致 | p.6 Figure 4。自分の読み 上の線 10.8、下の線 10.4 V。ラベルは "−VOUT" が線の左上、"+VOUT" が線の右下にあり、どちらの線かは図から一意には決まらない（opamps.md の留保どおり）。負荷の記載なしも同左 | 図題 "Output Voltage Swing vs. Supply Voltage" |
| AD797 | グラフ: 振幅 vs 負荷抵抗 | ±15 V で 200 Ω 以上 約 27 Vp-p、±5 V で約 6 Vp-p | 一致 | p.6 Figure 5。自分の読み ±15 V: 250 Ω 26.9、1 kΩ 27.4、7 kΩ 27.8 Vp-p。±5 V: 5.7〜6.4 Vp-p | 図題 "Output Voltage Swing vs. Load Resistance" |
| AD797 | 同相入力電圧範囲 | ±15: ±11/±12、±5: ±2.5/±3 V | 一致 | 同左。p.3 | `INPUT COMMON-MODE VOLTAGE RANGE ±15 V ±11 ±12 …` |
| AD797 | 入力電圧（絶対最大） | ±VS | 一致 | 同左。p.5 | `Input Voltage ±VS` |
| AD797 | 差動入力（絶対最大） | ±0.7 V、back-to-back ダイオード | 一致 | 同左。p.5、注 1 | "The AD797 inputs are protected by back-to-back diodes. …" |
| AD797 | 出力電流 | min 30 / typ 50 mA | 一致 | 同左。p.3、MIN/TYP 列（Max 空）。注 3 は p.4 | "Output current for \|VS − VOUT\| > 4 V, AOL > 200 kΩ." |
| AD797 | 出力短絡電流 | typ 80 mA | 一致 | 同左。p.3 | `Short-Circuit Current ±5 V, ±15 V 80 80 mA` |
| AD797 | 出力短絡（絶対最大） | 内部最大損失の範囲で無期限 | 一致 | 同左。p.5 | `Output Short-Circuit Duration Indefinite within maximum internal power dissipation` |

### 付録「出力振幅の規定値だけの一覧」（45 行）

45 行すべてを各石の表の行・DS の値と突き合わせ、**45 行とも一致**（値・電源・負荷・温度・min/typ の割り当て・出典ページ）。
行ごとの対応は次のとおり。

| 石 | 付録の行数 | 対応する上の行 | 判定 |
|---|---|---|---|
| NE5532 | 1 | 出力電圧振幅（規定なし） | 一致 |
| NJM5532 | 2 | 出力電圧振幅 1・2 | 一致 |
| NJM4580 | 1 | 出力電圧振幅 | 一致 |
| OPA2134 | 2 | 10 kΩ・2 kΩ（正側 MIN 列・負側 MAX 列） | 一致 |
| OPA1656 | 1 | 出力電圧振幅（±18 V） | 一致 |
| OPA2604 | 1 | 出力電圧振幅 | 一致 |
| LME49860 | 6 | 600 Ω・2 kΩ・10 kΩ × ±18/±22 V（Limit は ±22 V・600 Ω のみ） | 一致 |
| OPA1652 | 1 | 出力電圧振幅 | 一致 |
| OPA627 | 2 | 25°C・全温度 | 一致 |
| OPA1612 | 2 | 10 kΩ・2 kΩ | 一致 |
| LT1364 | 13 | 25°C 5 行、0〜70°C 4 行、–40〜85°C 4 行 | 一致 |
| OPA2140 | 2 | 10 kΩ・2 kΩ | 一致 |
| OPA828 | 2 | 10 kΩ（typ 0.9 / max 1.2）・600 Ω（typ 1.2） | 一致 |
| MUSES01 | 2 | 10 kΩ・2 kΩ | 一致 |
| MUSES02 | 1 | 2 kΩ | 一致 |
| MUSES03 | 3 | 10 kΩ・2 kΩ・600 Ω | 一致 |
| AD797 | 3 | 2 kΩ・600 Ω（±15 V）・600 Ω（±5 V） | 一致 |

付録末尾の文「±12 V（またはそれを含む電源範囲）での規定値があるのは OPA1612 と OPA2140 の 2 つだけ」も DS と合う（OPA1656 の VO は ±18 V 規定のみ）。
ただし「グラフがあるのは NJM5532・NJM4580・LME49860（Vrms, THD+N = 1%）・LT1364・AD797」の LME49860 は、Figure 96 のほかに **±12 V の THD+N vs Output Voltage（Figure 4・8・12、p.5〜6）** もある（下の節）。

### 頭書き（行数に入れていない）

| 石 | 頭書きの記述 | 判定 | 根拠 |
|---|---|---|---|
| 全体 | 出典は PDF のページ番号で、印刷ページと一致 | 一致 | 開いたページはすべてフッタのページ番号と一致（MUSES03 も「- 2 -」「- 4 -」） |
| NE5532 | SLOS075K、既定 ±15 V・25°C | 一致 | p.4 "VCC± = ±15V, TA = 25°C (unless otherwise noted)" |
| NJM5532 / NJM4580 / MUSES01 / MUSES02 | NRND の表記、表の既定条件 | 一致 | 各 p.2 の見出し |
| OPA2134 / OPA1656 / OPA1652 / OPA1612 / OPA2140 / OPA828 | 版と表の既定条件（OPA1656 は ±18 V、OPA1612・OPA2140 は範囲） | 一致 | 各電気的特性表の見出し |
| OPA2604 | 注文情報に AQ が無い | 一致 | p.24 に OPA2604AP / APG4 / AU 系のみ |
| LME49860 | Typical / Limit の 2 列、注 (2)(3) の文言 | 一致 | p.3 脚注 |
| OPA627 | §5.6 を使い §5.7・§5.8 は別品種 | 一致 | 目次と p.6〜7 の表題 |
| LT1364 | Note 9 の文言 | 一致 | p.5 Note 9 |
| MUSES03 | 1 回路入り、既定 ±15 V・RL=GND・25°C | 一致 | p.1 題、p.4 見出し |
| AD797 | Rev. K、A/B 列、既定 ±15 V・25°C | 一致 | p.3 見出し |

---

## 無いとされていたが DS にあった項目

### 「探したが無かった」と書かれていたが、DS にあったもの

| 石 | opamps.md の「無かった」 | DS にあったもの | ページ | 原文 |
|---|---|---|---|---|
| **OPA1652** | 入力間の保護ダイオードの記述 | **入力間に back-to-back ダイオード**。G = 1 などで入力が速く動くと順バイアスになりうるので、入力信号電流を 10 mA 以下に制限せよ（入力直列抵抗か帰還抵抗で） | p.15 §7.3.2 Input Protection（Figure 36） | "The input terminals of the OPA1652 and OPA1654 are protected from excessive differential voltage with back-to-back diodes, as Figure 36 illustrates. … the input signal current must be limited to 10 mA or less." |
| **OPA1612** | 入力間の保護ダイオードの有無の記述（ESD 用 steering diodes の説明 p.13 のみ） | **入力間に back-to-back ダイオード**（上と同じ趣旨） | p.14 §7.3.4 Input Protection（Figure 31） | "The input terminals of the OPA1611 and the OPA1612 are protected from excessive differential voltage with back-to-back diodes, as Figure 31 shows." |
| **NJM5532** | 入力保護ダイオードの有無の記述 | **内部に入力ダイオードがある**旨の注意: ボルテージフォロワでは電源投入時の入力ダイオード破壊を避けるため、非反転入力に電流制限抵抗を入れよ（図は 1 kΩ）。p.1 の等価回路図にも入力間のダイオードが描かれている。p.6 に V+ 開放時の寄生回路による過電流の注意（SBD か 1 kΩ 以上の抵抗） | p.5 NOTICE、p.1 EQUIVALENT CIRCUIT、p.6 | "When used in voltage follower circuit, put a current limit resistor into non-inverting input terminal in order to avoid inside input diode destruction when the power supply is turned on. ( ref.Fig.1 )" |

### 「無かった」とは書かれていないが、振幅の議論に関わるのに表に載っていない DS の図・記述

| 石 | DS にあったもの | ページ | 自分の読み・原文 |
|---|---|---|---|
| OPA2134 | Headroom の本文と図が表と違う値: **VS = ±18 V、THD+N < 0.01% で 11.7 Vrms = 23.6 dBu**（表は 21.3 dBu、"VS = 18V"） | p.13 §6.2.1、p.9 Figure 5-4 | "…maximum allowable output voltage level of 11.7Vrms (THD+Noise < 0.01%), have a headroom specification of 23.6dBu. See Figure 5-4." / 図中 "VS = ±18V, RL = 2kΩ, f = 1kHz … OPA134 – 11.7Vrms" |
| LME49860 | **±12 V の THD+N vs Output Voltage**（RL = 2 kΩ / 600 Ω / 10 kΩ）。±15・±22・±2.5 V もある | p.5 Figure 4・8、p.6 Figure 12 | 図題 "THD+N vs Output Voltage VCC = 12V, VEE = –12V RL = 2kΩ" ほか。±12 V・2 kΩ の急増点は約 8 V（横軸の単位表記は "V" のみ） |
| OPA1656 | **±15 V（ページ既定）の THD+N Ratio vs Output Amplitude**。600 Ω / 2 kΩ / 10 kΩ、G = ±1 の 6 本 | p.9 Figure 6-8 | 横軸 "Output Amplitude (VRMS)"、急増点は約 10 Vrms。ページ見出し "VS = ±15 V, RL = 2 kΩ" |
| OPA2140 | **Maximum Output Voltage vs Frequency に VS = ±15 V の線**（ほか ±5、±2.25 V） | p.12 Figure 6-22 | 低域で約 29 Vpp（縦軸 "Output Voltage (VPP)"） |
| NE5532 | 単電源 15 V の応用回路の実測伝達特性（出力が飽和する様子が出ている）。仕様ではなく応用例 | p.9 Figure 7-2〜7-4 | Figure 7-3 の VOUT+ は下側で約 1.3 V に張り付き、Figure 7-4 の VOUT– は上側で約 10.7 V、下側で約 1.3 V に張り付く。p.7 に "Information in the following applications sections is not part of the TI component specification" |

上以外の「探したが無かった」項目は、該当ページとテキスト全体の検索（diode / clamp / short / 短絡 / 保護 など）で、DS に無いことを確かめた。
