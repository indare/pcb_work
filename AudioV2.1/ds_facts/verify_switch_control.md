# switch_control.md の独立照合

- 照合日: 2026-09-25
- 対象: `AudioV2.1/ds_facts/switch_control.md`（このファイルは書き換えていない）
- 方法: 出典に書かれたページを `pdftoppm -r 150` で画像にし、表の見出しの MIN/TYP/MAX 列位置・表見出しと脚注の条件・原文を目で突き合わせた。グラフは 600〜1200 dpi に切り出し、軸目盛りから画素換算で読んだ（TMUX7612 Figure 5-4 / 5-19、PT2314E p14）。作業ファイルは scratchpad の `verify_ctrl/` にある。
- 照合した行数: **227**（表の行 222 ＋ 表の外に書かれた事実の主張 5）。ほかに「探したが DS に無かった項目」36 件を別に確かめた（最後の節）。
- 判定の内訳:

| 判定 | 件数 |
|---|---|
| 一致 | 224（うち 3 件は「一致・補足あり」。値は正しいが DS に条件か注がもう 1 つある） |
| 誤り | 2（どちらも軽微: 目読みの言い過ぎ 1、ページ範囲 1） |
| 条件の誤り | 0 |
| 列の誤り | 0 |
| 引用が無い | 0 |
| 確かめられず | 1（ADC1804_F 組立説明書。PDF は取得できたが、この環境では日本語フォントが描画されない） |

**設計の判断を変えうる誤りは見つからなかった。** min/typ/max の列、±15 V 表の電源電流が VDD = ±16.5 V 条件であること、ACPSRR の表値が f = 1 MHz であること、PT2314E の電源電圧が表ごとに min 4 V / 5 V と食い違うことは、どれも DS のとおりに書かれていた。

---

## 1. TI TMUX7612（TI_TMUX7612.pdf）

### 構成・制御

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| TMUX7612 | 構成 | SPST×4、独立選択 | 一致 | p1 Description | "with four independently selectable 1:1, single-pole, single-throw (SPST) switch channels" |
| TMUX7612 | 制御ピン | SEL1〜4、内部プルダウン | 一致 | p3 Table 4-1 | "SEL1 ... Logic control input 1, has internal pull-down resistor." |
| TMUX7612 | 真理値 | 0→OFF、1→ON | 一致 | p29 Table 7-1 | "0 Channel x OFF" / "1 Channel x ON" |
| TMUX7612 | 外付け部品 | デカップリングのみ | 一致 | p28 §7.4 | "can be operated without any external components except for the supply decoupling capacitors." |
| TMUX7612 | 論理入力の上限 | 1.8 V〜44 V | 一致 | p28 §7.4 | "The control pins operate down to 1.8 V logic and can be as high as 44 V." |
| TMUX7612 | VIH | 1.3 / 44 V、min/max | 一致 | p6 §5.6、MIN 1.3・MAX 44、–40〜+125°C | "VIH Logic voltage high –40°C to +125°C 1.3 44" |
| TMUX7612 | VIL | 0 / 0.8 V、min/max | 一致 | p6、MIN 0・MAX 0.8 | "VIL ... 0 0.8" |
| TMUX7612 | IIH | 0.005 / 2 µA、typ/max | 一致 | p6、TYP 0.005・MAX 2 | "IIH ... 0.005 2 µA" |
| TMUX7612 | IIL | –2 / –0.005 µA、min/typ | 一致 | p6、MIN –2・TYP –0.005 | "IIL ... –2 –0.005 µA" |
| TMUX7612 | CIN | 4 pF typ | 一致 | p6、TYP | "CIN Logic input capacitance ... 4 pF" |
| TMUX7612 | TSD / ヒステリシス | 165 / 15 °C typ | 一致 | p6、TYP、温度条件欄は空 | "TSD Thermal shutdown 165" / "TSD_HYST ... 15" |
| TMUX7612 | N.C. ピン | GND 短絡か浮かし | 一致 | p3 Table 4-1 | "No internal connection. Can be shorted to GND or left floating" |
| TMUX7612 | サーマルパッド | VSS 推奨 | 一致 | p3 Table 4-1 | "It is recommended that the pad be tied to VSS for best performance." |

§5.6 の表見出しは "Typical at VDD = +15 V, VSS = –15 V, VL = 3.3V, TA = 25℃"（p6）。switch_control.md はこの見出しに触れていないが、typ 値の条件としては見出しのとおり。

### 電源電圧

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | 両電源範囲 | ±4.5〜±25 V | 一致 | p1 Features | "Dual supply range: ±4.5V to ±25V" |
| TMUX7612 | 単電源範囲 | 4.5〜50 V | 一致 | p1 | "Single supply range: 4.5V to 50V" |
| TMUX7612 | 推奨 VDD–VSS | 4.5 / 50 V、NOM 空欄 | 一致 | p5 §5.5、MIN・MAX、NOM 空 | "VDD – VSS (1) Power supply voltage differential 4.5 50 V" |
| TMUX7612 | 推奨 VDD | 4.5 / 50 V | 一致 | p5 | "VDD Positive power supply voltage 4.5 50" |
| TMUX7612 | 推奨の注 | 4.5 ≤ VDD–VSS ≤ 50 | 一致 | p5 注(1) | "VDD and VSS can be any value as long as 4.5 V ≤ (VDD – VSS) ≤ 50 V, and the minimum VDD is met." |
| TMUX7612 | 推奨 VS/VD | VSS / VDD | 一致 | p5 | "Signal path input/output voltage (source or drain pin) (Sx, D) VSS VDD" |
| TMUX7612 | 推奨 VSEL | 0 / 44 V | 一致 | p5 | "VSEL Logic Supply Voltage ... 0 44 V" |
| TMUX7612 | 推奨 TA | –40 / 125 °C | 一致 | p5 | "TA Ambient temperature –40 125 °C" |
| TMUX7612 | 絶対最大 VDD–VSS | 53 V max | 一致 | p4 §5.1、MAX のみ | "VDD – VSS 53 V" |
| TMUX7612 | 絶対最大 VDD | –0.5 / 53 V | 一致 | p4 | "VDD Supply voltage –0.5 53" |
| TMUX7612 | 絶対最大 VSS | –32 / 0.5 V | 一致 | p4 | "VSS –32 0.5" |
| TMUX7612 | 絶対最大 VSEL | –0.5 / 53 V | 一致 | p4 | "VSEL Logic Supply Voltage –0.5 53" |
| TMUX7612 | 絶対最大 ISEL | ±30 mA | 一致 | p4 | "ISEL Logic control input pin current (SEL pins) –30 30 mA" |
| TMUX7612 | 絶対最大 VS/VD | VSS–0.5 / VDD+0.5 | 一致 | p4 | "VS or VD Source or drain voltage (Sx, Dx) VSS–0.5 VDD+0.5" |
| TMUX7612 | 絶対最大 IIK | ±30 mA、注(3) | 一致 | p4 | "IIK Diode clamp current(3) –30 30 mA" / "(3) Pins are diode-clamped to the power-supply rails." |
| TMUX7612 | IDC | 470/470/470/309/143/100/60 mA | 一致 | p5 §5.4、列は TJ = 25/50/85/105/125/135/150°C | "IDC (1) VSS to VDD - 2.5V 470 470 470 309 143 100 60 mA" |
| TMUX7612 | ESD | HBM ±3000、CDM ±1500 | 一致 | p4 §5.2 | "Human body model (HBM) ... ±3000" / "Charged device model (CDM) ... ±1500" |

### IDD / ISS

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | 表見出しの主張（md 56 行目: 電源電流の行は VDD = 16.5 V, VSS = –16.5 V） | — | 一致 | p7 見出し "VDD = +15 V ± 10%, VSS = –15 V ±10%"、電源電流の TEST CONDITIONS はすべて "VDD = 16.5 V, VSS = –16.5 V" | 画像で確認 |
| TMUX7612 | IDDQ | 35/45（25°C）、55、65 µA | 一致 | p7、25°C は TYP 35・MAX 45、温度行は MAX | "IDDQ ... All switches OFF 25°C 35 45 ... 55 ... 65" |
| TMUX7612 | IDD | 435/480、520、545 µA | 一致 | p7、同上 | "IDD ... All switches ON 25°C 435 480 ... 520 ... 545" |
| TMUX7612 | ISSQ | 15/20、25、40 µA | 一致 | p7、同上 | "ISSQ ... 25°C 15 20 ... 25 ... 40" |
| TMUX7612 | ISS | 340/380、410、425 µA | 一致 | p8（§5.7 続き） | "ISS VSS supply current ... 25°C 340 380 ... 410 ... 425" |
| TMUX7612 | ±20 V 表 IDD/ISS | 435/480、340/400 | 一致 | p10 §5.9、VDD = 22 V, VSS = –22 V | "IDD ... 435 480" / "ISS ... 340 400" |
| TMUX7612 | 12 V 単電源 IDD | 385/440 | 一致 | p15 §5.13、VDD = 12 V | "IDD ... 25°C 385 440" |

### Ron

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | RON ±15 V | 1.1/1.4、1.6/1.8/2.2 Ω | 一致 | p7、25°C は TYP 1.1・MAX 1.4、温度行 MAX | "VS = –10 V to +10 V ID = –10 mA 25°C 1.1 1.4 ... 1.6 ... 1.8 ... 2.2" |
| TMUX7612 | ΔRON ±15 V | 0.005 typ、0.045/0.055/0.060 max | 一致 | p7、25°C は TYP 列のみ | "ΔRON ... 25°C 0.005 ... 0.045 ... 0.055 ... 0.060" |
| TMUX7612 | RON FLAT ±15 V | 0.0003 typ（max 空欄）、0.045/0.055/0.060 | 一致 | p7、25°C は TYP 列に 0.0003、MAX 空欄（画像で確認） | "RON FLAT ... 25°C 0.0003 ... 0.045 ... 0.055 ... 0.060" |
| TMUX7612 | RON DRIFT | 0.006 Ω/°C typ | 一致 | p7、VS = 0 V, IS = –10 mA、–40〜+125°C | "RON DRIFT ... 0.006 Ω/°C" |
| TMUX7612 | RON ±20 V | 1.1/1.4、1.6/1.9/2.2 | 一致 | p10、VS = –15〜+15 V | "25°C 1.1 1.4 ... 1.6 ... 1.9 ... 2.2" |
| TMUX7612 | RON FLAT ±20 V | 0.006、0.065/0.070/0.075 | 一致 | p10 | "25°C 0.006 ... 0.065 ... 0.070 ... 0.075" |
| TMUX7612 | RON +37.5/–12.5 V | 1.1/1.35、1.6/1.8/2.1 | 一致 | p12 §5.11、VS = –7.5〜32.5 V | "25°C 1.1 1.35 ... 1.6 ... 1.8 ... 2.1" |
| TMUX7612 | RON FLAT +37.5/–12.5 V | 0.006、0.075/0.080/0.085 | 一致 | p12 | "25°C 0.006 ... 0.075 ... 0.080 ... 0.085" |
| TMUX7612 | RON 12 V | 1.15/1.6、1.75/2/2.3 | 一致 | p15、VS = 3〜9 V | "25°C 1.15 1.6 ... 1.75 ... 2 ... 2.3" |
| TMUX7612 | RON FLAT 12 V | 0.084、0.13/0.15/0.16 | 一致 | p15 | "25°C 0.084 ... 0.13 ... 0.15 ... 0.16" |
| TMUX7612 | 平坦域の本文 | VSS+5〜VDD–5 V | 一致 | p27 §7.3.4 | "The flattest on-resistance region extends roughly from 5 V above VSS to 5 V below VDD." |

### Figure 5-4（p17）目読みの照合

1200 dpi で切り出し、横軸 1 V ≈ 46 px、縦軸 1 Ω ≈ 218 px で読んだ。凡例の色は ±10 V 赤 / ±12 V 灰 / ±13.5 V 青 / ±15 V 緑 / ±16.5 V 紫で、switch_control.md の読みと同じ。

| 部品 | 項目 | switch_control.md の値 | 判定 | 自分の読み | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | Fig 5-4 概要（md 87 行目）: 底 約 1.1 Ω、正側は「7.5 Ω 超まで」立ち上がる、負側は端で約 1.25 Ω | — | **誤り（軽微）** | 底は約 1.11 Ω で一致。負側も一致（どの曲線も VSS から約 0.9 V は 1.25 Ω で水平、そこから下がる）。**正側の曲線は約 7.4 Ω で水平になって VDD まで続き、7.5 Ω（軸の上限）は越えていない。** 図が 7.5 Ω を越えていることを示しているわけではない（頭打ちが測定上限か描画の切り詰めかも図からは分からない） | p17 Figure 5-4 画像 |
| TMUX7612 | ±10 V | 離れ始め +5.6 / 1.5 Ω 越え +8.1 / 縦の立ち上がり +8.7〜9.0 / VSS 端 1.25 Ω、–6 V で底 | 一致 | +5.6 / +8.2 / +8.6〜9.0 / 1.25 Ω、約 –5.9 V で底 | 同上 |
| TMUX7612 | ±12 V | +7.6 / +10.0 / +10.6〜11 / –8 V | 一致 | +7.5 / +10.0〜10.2 / +10.5〜11.0 / 約 –8.2 V | 同上 |
| TMUX7612 | ±13.5 V | +9.0 / +11.6 / +12.2〜12.5 / –9.5 V | 一致 | +9.0〜9.1 / +11.5 / +12.0〜12.5 / 約 –9.5 V | 同上 |
| TMUX7612 | ±15 V | +10.6 / +13.1 / +13.8〜14 / –11.5 V | 一致 | +10.7 / +13.1 / +13.4〜14.0 / 約 –11 V（曲線が重なって ±0.5 V 程度は判別できない） | 同上 |
| TMUX7612 | ±16.5 V | +12.0 / +14.6 / +15.2〜15.5 / –12.5 V | 一致 | +12.1 / +14.6〜14.7 / +14.9〜15.5 / 約 –12 V（同上） | 同上 |

補足（switch_control.md に無い観察）: 同じページの **Figure 5-1（VDD = 15 V, VSS = –15 V, 温度別）では 25°C の線が約 0.95 Ω** で、Figure 5-4 の底（約 1.1 Ω）や表の RON typ 1.1 Ω と合わない。DS の中の食い違い。

### ACPSRR

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | ACPSRR ±15 V | –80 dB typ、f = 1 MHz | 一致 | p9 §5.8、TYP | "VPP = 0.62 V on VDD and VSS RL = 50 Ω , CL = 5 pF, f = 1 MHz 25°C –80 dB" |
| TMUX7612 | ACPSRR ±20 V | –76 dB | 一致 | p11 §5.10、VPP = 0.62 V, f = 1 MHz | "ACPSRR ... 25°C –76" |
| TMUX7612 | ACPSRR +37.5/–12.5 V | –80 dB | 一致 | p14 §5.12、同条件 | "ACPSRR ... –80" |
| TMUX7612 | ACPSRR 12 V | –78 dB | 一致 | p16 §5.14、同条件 | "ACPSRR ... –78" |
| TMUX7612 | 測定法の食い違い | 本文 100 mVPP、図 620 mVPP | 一致 | p26 §6.11 と Figure 6-11 | "modulated by a sine wave of 100 mVPP" / 図中 "620 mVPP"、"With & Without Capacitor"、"0.1 µF" |
| TMUX7612 | Fig 5-19 目読み | 10 kHz: –89/–80/–78/–88、20 kHz: –86/–77/–72/–82、100 kHz: –85/–76/–57/–68、1 MHz: –83/–77/–38/–46 dB（VDD with cap / VSS with cap / VSS without cap / VDD without cap の順） | 一致 | 600 dpi で読んだ値: 10 kHz –89/–80/–78/–88、20 kHz –86/–77/–72/–82、100 kHz –85/–76/–57/–68、1 MHz –83/–77/–38/–46。10 Hz〜1 kHz は 4 本とも –100〜–115（1 kHz 付近で VDD 側に –125 までの谷）。図に電源電圧の注記なし | p20 Figure 5-19 |

### OFF アイソレーション ほか

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | OISO 100 kHz | –105 dB | 一致 | p9、TYP | "OISO Off-isolation ... f = 100 kHz 25°C –105" |
| TMUX7612 | OISO 1 MHz | –74 dB | 一致 | p9 | "... f = 1 MHz 25°C –74" |
| TMUX7612 | XTALK 100 kHz | –114 dB | 一致 | p9 | "XTALK Crosstalk ... f = 100 kHz 25°C –114" |
| TMUX7612 | XTALK 1 MHz | –105 dB | 一致 | p9 | "... f = 1MHz 25°C –105" |
| TMUX7612 | Fig 5-15 目読み | 10 Hz〜約 300 kHz で –100〜–105 dB | 一致 | 10 Hz〜約 200 kHz で –98〜–107 dB、200〜300 kHz から上昇。凡例 "VDD/SS = ±15V" | p19 |
| TMUX7612 | Fig 5-16 目読み | 100 Hz〜約 3 MHz で –100〜–110 dB | 一致 | 100 Hz〜3〜5 MHz で –100〜–113 dB、隣接と非隣接はほぼ重なる | p19 |
| TMUX7612 | THD+N | 0.0006 % | 一致 | p9、VPP = 15 V, RL = 110 Ω, f = 20 Hz〜20 kHz | "THD+N ... 0.0006 %" |
| TMUX7612 | QINJ | –2 pC | 一致 | p9、VS = 0 V, CL = 100 pF | "QINJ ... -2 pC" |
| TMUX7612 | CS(OFF)/CD(OFF)/C(ON) | 27/27/22 pF | 一致 | p9、VS = 0 V, f = 1 MHz | "27" / "27" / "22" |
| TMUX7612 | tON / tOFF | 2.0/2.5、1.7/2.2 µs | 一致 | p9、25°C TYP/MAX | "tON ... 2.0 2.5" / "tOFF ... 1.7 2.2" |
| TMUX7612 | tBBM | 310 typ、125 min | 一致 | p9、温度行の 125 は MIN 列（画像で確認） | "tBBM ... 25°C 310 ... 125 ... 125" |

### 電源シーケンス・デカップリング

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TMUX7612 | 電源シーケンス | 任意の順 | 一致 | p28 §7.3.5 "Power-Up Sequence Free" | "The TMUX7612 supports any power up sequencing." |
| TMUX7612 | GND の先行接続 | GND を先に | 一致 | p33 §8.4 | "Always make sure a solid ground (GND) connection is established before supplies are ramped." |
| TMUX7612 | ピンのクランプ | ダイオードクランプ | 一致 | p4 注(3) | "Pins are diode-clamped to the power-supply rails." |
| TMUX7612 | デカップリング値 | 0.1〜10 µF | 一致 | p3 Table 4-1 | "connect a decoupling capacitor ranging from 0.1 µF to 10 µF between VDD and GND" |
| TMUX7612 | 推奨組み合わせ | 0.1 µF＋1 µF | 一致 | p34（§8.5.1 の続き） | "We recommend a 0.1 µF and 1 µF capacitor, placing the lowest value capacitor as close to the pin as possible." |
| TMUX7612 | 種類 | MLCC | 一致 | p33 §8.4 | "TI recommends using multi-layer ceramic chip capacitors (MLCCs)" |

---

## 2. Zettler AZ850（Zettler_AZ850.pdf）

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| AZ850 | 型番の付け方（md 154 行目） | nil / P1 / P2 | 一致 | p2 ORDERING DATA | "nil: monostable non-latching / P1: bistable single coil latching / P2: bistable dual coil latching" |
| AZ850 | 接点構成 | DPDT、バイファーケート | 一致 | p1 CONTACTS | "Arrangement DPDT (2 Form C) Bifurcated crossbar contacts" |
| AZ850 | P1 5 V 抵抗 | 250 Ω ±10 % | 一致 | p2 Single coil latching、注 2 で 20°C | "5 3.75 14.5 250" |
| AZ850 | P1 Must Operate | 3.75 V | 一致 | p2 | 同上 |
| AZ850 | P1 Max. Continuous | 14.5 V | 一致 | p2 | 同上 |
| AZ850 | P2 5 V 抵抗 | 125 Ω | 一致 | p2 Dual coil latching | "5 3.75 10.0 125" |
| AZ850 | P2 Must Operate | 3.75 V | 一致 | p2 | 同上 |
| AZ850 | P2 Max. Continuous | 10.0 V | 一致 | p2 | 同上 |
| AZ850 | 非ラッチ 5 V | 178 Ω、3.75、12.5 V | 一致 | p2 Monostable | "5 3.75 12.5 178" |
| AZ850 | コイル電力 | 感動電圧で 56–84 / 113–169 / 79–113 mW | 一致 | p1 COIL、"(typ.)" | "Power at pickup voltage (typ.) monostable non-latching 79 - 113 mW bistable single coil latching 56 - 84 mW bistable dual coil latching 113 - 169 mW" |
| AZ850 | セット時間 | 2 ms typ | 一致 | p1 | "Set Time at nominal coil voltage latching types 2 ms (typ.)" |
| AZ850 | リセット時間 | 1 ms typ | 一致 | p1 | "Reset Time ... latching types 1 ms (typ.)" |
| AZ850 | 動作／復帰（非ラッチ） | 2 / 1 ms | 一致 | p1 | "Operate Time ... 2 ms (typ.)" / "Release Time ... w/o coil suppression ... 1 ms (typ.)" |
| AZ850 | コイル極性 | 固定 | 一致 | p2 NOTES 5 | "Relay has fixed coil polarity" |
| AZ850 | 感動 | Must Operate 未満でも吸引 | 一致 | p2 NOTES 3 | "Relay may pull in with less than “Must Operate” value." |
| AZ850 | 並列サプレッサ | 復帰が延びる | 一致 | p2 NOTES 4 | "... will lengthen the release time." |
| AZ850 | 接点定格 | 30 W / 62.5 VA、1 A、2 A、220 VDC / 250 VAC | 一致・補足あり | p1。220 VDC に注 "*" がある: 30 VDC を越える開閉は要相談 | "switched voltage 220 VDC* or 250 VAC" / "* Note: If switching voltage is greater than 30 VDC, special precautions must be taken." |
| AZ850 | UL 定格負荷 | 1 A@30 VDC、0.5 A@125 VAC | 一致 | p1 | "UL, CUR 1 A at 30 VDC, resistive 0.5 A at 125 VAC, resistive" |
| AZ850 | 最小開閉 | 10 mV、10 µA | 一致 | p1 | "Minimum switching voltage 10 mV current 10 µA" |
| AZ850 | 接点材質 | AgPd 金クラッド | 一致 | p1 | "AgPd - silver palladium, gold clad" |
| AZ850 | 初期接触抵抗 | < 50 mΩ | 一致 | p1 | "Initial resistance < 50 mΩ" |
| AZ850 | 機械寿命 | 1×10^6 | 一致 | p1 | "mechanical 1 x 10^6" |
| AZ850 | 電気寿命 | 2×10^5 / 1×10^5 | 一致 | p1 | "electrical 2 x 10^5 at 1 A 30 VDC resistive 1 x 10^5 at 0.5 A 125 VAC resistive" |
| AZ850 | 動作温度 | –40〜85 °C | 一致 | p1 | "operating -40°C (-40°F) to 85°C (158°F)" |
| AZ850 | 温度上昇 | 18 K | 一致 | p1 | "Temperature Rise at nominal coil voltage 18 K" |
| AZ850 | 静電容量 | 0.9 / 0.2 / 0.4 pF | 一致 | p1、typ | "coil to contacts 0.9 pF between contact sets 0.2 pF between open contacts 0.4 pF" |
| AZ850 | 絶縁抵抗 | 1000 MΩ min | 一致 | p1 | "1000 MΩ (min.) at 20°C, 500 VDC, 50% RH" |
| AZ850 | 隣接間隔 | 5.0 mm | 一致 | p2 NOTES 6 | "a .197" (5.0 mm) space be provided between adjacent relays." |

---

## 3. Toshiba TBD62083A（Toshiba_TBD62083A.pdf）

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| TBD62083A | 概要（md 199 行目） | シンク型 DMOS 8 回路、各出力にクランプダイオード | 一致 | p1 | "8channel sink type DMOS transistor array" / "It has a clamp diode for switching inductive loads built-in in each output." |
| TBD62083A | 絶対最大 IOUT | 500 mA/ch | 一致 | p3、表見出し Ta = 25 °C | "Output current IOUT 500 mA/ch" |
| TBD62083A | 絶対最大 VOUT | 50 V | 一致 | p3 | "Output voltage VOUT 50 V" |
| TBD62083A | 絶対最大 VCOM | –0.5〜50 V | 一致 | p3（条件欄「—」だが表見出しは Ta = 25 °C） | "COMMON pin voltage VCOM −0.5 to 50 V" |
| TBD62083A | 絶対最大 VIN | –0.5〜30 V | 一致 | p3 | "Input voltage VIN −0.5 to 30 V" |
| TBD62083A | 動作 IOUT 1 回路 | 0〜400 mA | 一致 | p4、表見出し Ta = −40〜85 °C、行条件 Ta = 25°C、Min/Max 列 | "1 circuits ON, Ta = 25°C 0 ― 400" |
| TBD62083A | 8 回路 Duty 10 % | 390 / 320 / 320 / 370 | 一致 | p4、Max 列 | "tpw = 25 ms ... Duty = 10% 0 ― 390"（PG）ほか |
| TBD62083A | 8 回路 Duty 50 % | 170 / 140 / 140 / 160 | 一致 | p4 | "Duty = 50% 0 ― 170"（PG）ほか |
| TBD62083A | 動作範囲の注 | PG/FG device alone、FNG/FWG は基板 | 一致 | p4 Note1〜3（PG・FG が Note1） | "Note1: Device alone." / "Note2: On PCB (Size: 50 mm × 50 mm ...)" / "Note3: ... 75 mm × 114 mm ..." |
| TBD62083A | VDS 350 mA | 0.7 / 1.14 V（2.0 / 3.25 Ω） | 一致 | p5、Typ/Max 列、VIN = 5.0 V | "IOUT = 350 mA, VIN =5.0V ― 0.7 (2.0) 1.14 (3.25)" |
| TBD62083A | VDS 200 mA | 0.4 / 0.65 V | 一致 | p5 | "IOUT = 200 mA ... 0.4 (2.0) 0.65 (3.25)" |
| TBD62083A | VDS 100 mA | 0.2 / 0.325 V | 一致 | p5 | "IOUT = 100 mA ... 0.2 (2.0) 0.325 (3.25)" |
| TBD62083A | 入力電圧（ON）動作範囲 | 2.5 / 25 V | 一致 | p4 | "IOUT = 100 mA or upper, VOUT = 2 V 2.5 ― 25" |
| TBD62083A | 入力電圧（OFF）動作範囲 | 0 / 0.6 V | 一致 | p4 | "IOUT = 100 μA or less, VOUT = 2 V 0 ― 0.6" |
| TBD62083A | VIN(ON) 電気的特性 | 2.5 V max | 一致 | p5、Max 列、試験回路 5 | "IOUT = 100 mA, VOUT = 2 V ― ― 2.5" |
| TBD62083A | IIN(ON) | 0.1 mA max @ 2.5 V | 一致 | p5 | "VIN = 2.5 V ― ― 0.1" |
| TBD62083A | IIN(OFF) | 1.0 µA max | 一致 | p5 | "IIN (OFF) 4 VIN = 0 V, Ta = 85°C ― ― 1.0" |
| TBD62083A | 出力リーク | 1.0 µA max | 一致 | p5 | "Ileak 1 VOUT = 50V, Ta = 85°C VIN = 0 V ― ― 1.0" |
| TBD62083A | クランプ VR（絶対最大） | 50 V | 一致 | p3 | "Clamp diode reverse voltage VR 50 V" |
| TBD62083A | クランプ IF（絶対最大） | 500 mA | 一致 | p3 | "Clamp diode forward current IF 500 mA" |
| TBD62083A | クランプ IF（動作範囲） | 400 mA max | 一致 | p4 | "Clamp diode forward current IF ― ― ― 400" |
| TBD62083A | クランプ VF | 2.0 V max @ 350 mA | 一致 | p5 | "IF = 350 mA ― ― 2.0" |
| TBD62083A | クランプ IR | 1.0 µA max | 一致 | p5 | "VR = 50 V, Ta = 85°C ― ― 1.0" |
| TBD62083A | クランプ接続 | カソードが COMMON | 一致 | p2 等価回路（画像で確認: アノードが OUTPUT、カソードが COMMON。GND→COMMON 向きのダイオードも別にある） | 図 "COMMON / Clamp diode / OUTPUT" |
| TBD62083A | PD | 1.47 / 0.96 / 0.96 / 1.31 W | 一致 | p3 | "PG (Note1) 1.47 FG (Note2) 0.96 FNG (Note3) 0.96 FWG (Note4) 1.31" |
| TBD62083A | PD の軽減 | 11.8 / 7.7 / 7.7 / 10.48 mW/°C | 一致 | p3 Note1〜4 | "derating with 11.8 mW/°C" ほか |
| TBD62083A | tON / tOFF | 0.4 / 0.8 µs typ | 一致・補足あり | p5、Typ 列。試験条件は p7 試験回路 8 の注に続く: 入力パルス幅 50 µs・Duty 10 %・**VIH = 5.0 V（TBD62083A）**・tr ≤ 5 ns | "Turn−on delay tON ... ― 0.4 ―" / p7 "Note 1: Pulse width 50 μs, Duty cycle 10% ... TBD62083A series 5.0 V" |
| TBD62083A | 動作温度 | –40〜85 °C | 一致 | p3 | "Operating temperature Topr −40 to 85 °C" |
| TBD62083A | 保護回路なし | 過電流・過電圧保護なし | 一致 | p7 Precautions for Using | "This IC does not include built-in protection circuits for excess current or overvoltage." |

---

## 4. Microchip MCP23017（Microchip_MCP23017.pdf）

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| MCP23017 | VDD（DC 特性） | 1.8 / 5.5 V | 一致 | p4 Table 1-1 D001、Min/Max。表見出し 1.8 ≤ VDD ≤ 5.5 V, –40〜+125°C | "D001 Supply Voltage VDD 1.8 — 5.5 V" |
| MCP23017 | 動作電圧（Features） | 3 行、2 行目も –40〜+85 °C | 一致 | p1（DS の原文も 2 行目が –40〜+85 °C） | "- 1.8V to 5.5V @ -40°C to +85°C - 2.7V to 5.5V @ -40°C to +85°C - 4.5V to 5.5V @ -40°C to +125°C" |
| MCP23017 | 絶対最大 VDD | –0.3〜+5.5 V | 一致 | p3 | "Voltage on VDD with respect to VSS ... -0.3V to +5.5V" |
| MCP23017 | 絶対最大 他ピン | –0.6〜VDD+0.6 V | 一致 | p3 | "-0.6V to (VDD + 0.6V)" |
| MCP23017 | POR 後 IODIR | 1111 1111 | 一致 | p16 Table 3-2/3-3、p17 Table 3-4/3-5 | "IODIRA 00 IO7 ... IO0 1111 1111" |
| MCP23017 | IODIR の意味 | 1 入力、0 出力 | 一致 | p18 Register 3-1（R/W-1） | "1 = Pin is configured as an input. 0 = Pin is configured as an output." |
| MCP23017 | Features 既定入力 | 既定で入力 | 一致 | p1 | "I/O pins default to input" |
| MCP23017 | POR 後のその他 | すべて 0000 0000 | 一致・補足あり | p17 Table 3-4 に全レジスタがある。Table 3-5（BANK = 0）の INTF〜OLAT は p18 に続く | "IOCON 05 BANK MIRROR ... 0000 0000"、"OLATA 0A ... 0000 0000" |
| MCP23017 | 内部プルアップ | GPPU、入力時のみ、100 kΩ | 一致 | p22 §3.5.7 | "the corresponding port pin is internally pulled up with a 100 kΩ resistor." |
| MCP23017 | プルアップ既定 | 無効 | 一致 | p16、p22 Register 3-7 R/W-0 | "GPPUA 06 ... 0000 0000" / "1 = Pull-up enabled" |
| MCP23017 | IPU | 40 / 75 / 115 µA | 一致 | p4 D070、Min/Typ/Max、VDD = 5 V。Typ 列は注 1（特性値、全数試験でない） | "D070 GPIO weak pull-up current IPU 40 75 115 µA VDD = 5V GP pins = VSS" |
| MCP23017 | VOL GPIO | 0.6 V max | 一致 | p4 D080 | "GPIO VOL — — 0.6 V IOL = 8.0 mA VDD = 4.5V" |
| MCP23017 | VOH 4.5 V | VDD–0.7 min | 一致 | p4 D090 | "VDD – 0.7 — — V IOH = -3.0 mA VDD = 4.5V" |
| MCP23017 | VOH 1.8 V | VDD–0.7 min | 一致 | p4 D090 | "IOH = -400 µA VDD = 1.8V" |
| MCP23017 | ピン電流（絶対最大） | 25 / 25 mA | 一致 | p3 | "Maximum output current sunk by any output pin ... 25 mA" |
| MCP23017 | VSS / VDD ピン | 150 / 125 mA | 一致 | p3 | "Maximum current out of VSS pin ... 150 mA" / "into VDD pin ... 125 mA" |
| MCP23017 | 総損失 | 700 mW | 一致 | p3 | "Total power dissipation ... 700 mW" |
| MCP23017 | VIL / VIH（シュミット） | VSS〜0.2 VDD / 0.8 VDD〜VDD | 一致 | p4 D031/D041 | "D031 ... VIL VSS — 0.2 VDD" / "D041 ... VIH 0.8 VDD — VDD V For entire VDD range" |
| MCP23017 | IDD | 1 mA max | 一致 | p4 D004 | "IDD — — 1 mA SCL/SCK = 1 MHz" |
| MCP23017 | IDDS | 1 µA、3 µA max | 一致 | p4 D005 | "1 µA -40°C ≤ TA ≤ +85°C" / "3 µA 4.5V ≤ VDD ≤ 5.5V +85°C ≤ TA ≤ +125°C (Note 1)" |
| MCP23017 | VPOR / SVDD | VSS typ、0.05 V/ms min | 一致 | p4 D002/D003 | "VPOR — VSS —" / "SVDD 0.05 — — V/ms Design guidance only. Not tested." |
| MCP23017 | POR の動作 | 十分上がるまで保持 | 一致 | p12 §3.1 | "The on-chip POR circuit holds the device in reset until VDD has reached a high enough voltage" |
| MCP23017 | RESET ピン | 外部バイアス必須 | 一致 | p11 Table 2-1 | "RESET 14 18 I Hardware reset. Must be externally biased." |
| MCP23017 | A0–A2 | 外部バイアス必須 | 一致 | p11 Table 2-1 | "Hardware address pin. Must be externally biased." |
| MCP23017 | RESET パルス幅 | 1 µs min | 一致 | p5 Table 1-2 | "30 RESET Pulse Width TRSTL 1 — — µs" |
| MCP23017 | CIO | 50 pF max | 一致 | p4 D101 | "D101 GPIO, SO, INT CIO — — 50 pF" |

---

## 5. Princeton PT2314E（Princeton_PT2314E.pdf）

p12 の表見出し: "Unless otherwise specified: Ta=25℃, VDD=9V, RL=10KΩ, Rg=20Ω, all controls flat, F=1KHz"。switch_control.md の条件欄はこれと一致する。

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| PT2314E | 電源電圧（EC） | 5 / 9 / 10 V | 一致 | p12、Min/Typ/Max | "Supply voltage VDD - 5 9 10 V" |
| PT2314E | 電源電圧（Quick Ref） | 4 / 9 / 10 V | 一致 | p11 | "Supply voltage VDD 4 9 10 V" |
| PT2314E | Features | 4〜10 V | 一致 | p1 | "Wide operation range (VDD=4V to 10V)" |
| PT2314E | 絶対最大 VDD | 10 V | 一致 | p11、Max | "Operating supply voltage VDD - 10 V" |
| PT2314E | 絶対最大 Vin | –0.3 / VDD+0.3 | 一致 | p11 | "Input voltage Vin -0.3 VDD+0.3 V" |
| PT2314E | Is 9 V | 30 / 40 mA | 一致 | p12、Typ/Max | "VDD=9V - 30 40" |
| PT2314E | Is 5 V | 25 / 32 mA | 一致 | p12 | "VDD=5V - 25 32" |
| PT2314E | Vimax | 2.3 / 2.6 Vrms、min/typ | 一致 | p12、Max は "-" | "Max. input level Vimax All Gain=0dB; THD=1% 2.3 2.6 - Vrms" |
| PT2314E | 最大入力（Quick Ref） | 2.3 / 2.6 | 一致 | p11 | "Max. input signal handling VCL 2.3 2.6 - Vrms" |
| PT2314E | VOMAX | 2.3 / 2.6 Vrms | 一致 | p12 Audio Outputs | "VOMAX THD=1% 2.3 2.6 - Vrms" |
| PT2314E | RIN 入力セレクタ | 35 / 50 / 70 kΩ | 一致 | p12 | "Input 1, 2, 3, 4 35 50 70 KΩ" |
| PT2314E | RIN 音量 | 13 / 20 / 27 kΩ | 一致 | p12 | "VOL=0dB 13 20 27 KΩ" |
| PT2314E | 最小負荷 LOUT/ROUT | 5 kΩ min | 一致 | p12 | "Vo=2Vrms, LOUT, ROUT 5 - - KΩ" |
| PT2314E | 最小負荷 出力 | 5 kΩ min | 一致 | p12 Audio Outputs | "Minimum load RL - 5 - - KΩ" |
| PT2314E | 出力 DC レベル | 0.49 / 0.5 / 0.51 VDD | 一致 | p12 | "VOUT - 0.49 0.5 0.51 VDD" |
| PT2314E | DC オフセット（入力セレクタ） | 3 / 10 mV、min 空欄 | 一致 | p12、Min 列は空（"-" も無い。画像で確認） | "DC offset VDCO 0dB to +11.25dB 3 10 mV" |
| PT2314E | DC オフセット（アッテネータ） | 5 / 10 mV | 一致 | p12 | "0dB to MUTE - 5 10 mV" |
| PT2314E | THD 1 Vrms | 0.03 / 0.07 % | 一致 | p12 | "All Gain=0, Vin=1Vrms - 0.03 0.07" |
| PT2314E | THD "100Vrms" | 0.01 / 0.03 % | 一致 | p12（原文の表記どおり） | "All Gain=0, Vin=100Vrms - 0.01 0.03" |
| PT2314E | S/N | 100 dBV typ | 一致 | p12 | "All Gain=0dB, A-weighted - 100 - dBV" |
| PT2314E | S/N ミュート | 100 dBV | 一致 | p12 | "All Gains=0dB, Muted - 100 -" |
| PT2314E | 残留雑音グラフ | 9 V で A 約 7、20–20k 約 9、80k 約 12 µV | 一致 | 自分の読み: A-weighted 約 7.0、20–20KHz 約 9.2、80KHz LPF 約 12.3 µV。グラフにゲイン等の条件なし | p14 "Residual Noise" |
| PT2314E | チャンネル分離 | 90 / 100 dB | 一致 | p12 | "L to R or R to L channel 90 100 - dB" |
| PT2314E | 入力分離 | 90 / 100 dB | 一致 | p12 | "F=20~20KHz 90 100 - dB" |
| PT2314E | リップル除去 | 75 dB typ | 一致 | p12 | "CREF=22µF, F=100Hz - 75 - dB" |
| PT2314E | ミュート減衰 | 100 dB typ | 一致 | p12 | "AMUTE - - 100 - dB" |
| PT2314E | I2C VIL / VIH | 1 V max / 3 V min | 一致 | p12 | "VIL VDD=9V - - 1 V" / "VIH VDD=9V 3 - - V" |
| PT2314E | I2C データレート | 3.3 V MCU: 4〜7 V F、8〜9 V S、10 V x | 一致 | p7 DATA RATE | "3.3V F F F F S S x" / "Data rate specification is design guarantee only, not fully tested in every combination." |
| PT2314E | I2C 初期化時間 | Td 推奨 50 ms | 一致 | p7 | "in this period access the I2C bus is prohibited." / "recommended Td timing shown on next page is 50mS." |
| PT2314E | チップアドレス | 88H | 一致 | p6 | "The PT2314E chip address is 88H" |
| PT2314E | 最大出力 vs 負荷 | 3.5 kΩ 以上で約 2.85 V、1 kΩ で約 1.25 V | 一致 | 自分の読み: 約 3.5 kΩ から 2.83 V で水平、1 kΩ で 1.25 V。VDD の記載なし | p14 "Maximum Output Level VS RLOAD" |

---

## 6. TI PCM1804（TI_PCM1804.pdf）／ ADC1804_F

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| PCM1804 | VCC 推奨 | 4.75 / 5 / 5.25 V | 一致 | p5、MIN/NOM/MAX | "Analog supply voltage, VCC 4.75 5 5.25 V" |
| PCM1804 | VDD 推奨 | 3 / 3.3 / 3.6 V | 一致 | p5 | "Digital supply voltage, VDD 3 3.3 3.6 V" |
| PCM1804 | 電源電圧範囲（EC） | 同上、min/typ/max | 一致 | p8 | "VCC 4.75 5 5.25 ... VDD 3 3.3 3.6" |
| PCM1804 | 絶対最大 VCC/VDD | –0.3〜6.5 / –0.3〜4 V | 一致 | p5 | "VCC –0.3 V to 6.5 V ... VDD –0.3 V to 4 V" |
| PCM1804 | 電源差 | VCC – VDD < 3 V | 一致 | p5 | "Supply voltage difference VCC, VDD VCC – VDD < 3 V" |
| PCM1804 | ICC | 35 / 45 mA | 一致 | p8、TYP/MAX、注 (9)(10)(11) の 1 行 | "ICC VCC = 5 V (9) (10) (11) 35 45" |
| PCM1804 | IDD シングル | 15 / 20 mA | 一致 | p8 | "VDD = 3.3 V (9) (12) 15 20" |
| PCM1804 | IDD デュアル | 27 mA typ | 一致 | p8、TYP 列のみ（画像で確認） | "(10) (12) 27" |
| PCM1804 | IDD クアッド | 18 mA typ | 一致 | p8 | "(11) (12) 18" |
| PCM1804 | 注の定義 | (9)〜(12) | 一致 | p8 | "(9) Single rate, fS = 48 kHz ... (12) Minimum load on DATA/DSDR (pin 15)" |
| PCM1804 | 表の共通条件 | TA 25°C, VCC 5 V, VDD 3.3 V ... | 一致 | p8 見出し | "All specifications at TA = 25°C, VCC = 5 V, VDD = 3.3 V, master mode, single-speed mode, fS = 48 kHz, system clock = 256 fS, 24-bit data" |
| PCM1804 | PD | 225/290、265、235 mW | 一致 | p8、デュアル・クアッドは TYP のみ | "225 290" / "265" / "235" |
| PCM1804 | PD パワーダウン | 5 mW | 一致 | p8 | "Power down, VCC = 5 V, VDD = 3.3 V 5" |
| PCM1804 | 動作温度 | –10 / 70 °C | 一致 | p8（p5 推奨条件も同じ） | "Operation temperature –10 70" |
| PCM1804 | 内部 POR | VDD > 2 V、VCC > 4 V（typ）、RST 内部プルダウン | 一致 | p18 | "when the power supply VDD exceeds 2 V (typical) and VCC exceeds 4 V (typical)." / "Because an internal pulldown resistor terminates RST" |
| PCM1804 | POR とクロック | 3 クロック以上 | 一致 | p18 | "at least three system clocks are required prior to VDD > 2 V, VCC > 4 V, and RST = high." |
| PCM1804 | バイパス | 0.1 µF＋10 µF、共通 1 系統推奨 | 一致 | p29 | "0.1-μF ceramic and 10-μF tantalum capacitors" / "using one common power supply is recommended" |
| PCM1804 | 代表特性の見出しの食い違い | p9〜11 が "VCC = 3.3 V, VDD = 5 V" | **誤り（軽微）** | 見出しの内容は正しい。ただし **同じ見出しは p9〜12 の 4 ページ**（p12 は "master mode, and 24-bit data" の短い形） | p12 "All specifications at TA = 25°C, VCC = 3.3 V, VDD = 5 V, master mode, and 24-bit data, unless otherwise noted." |
| ADC1804_F | 製品ページの電源 | 3.3 V・5 V（2 電源） | 一致 | 2026-09-25 に https://digit.kyohritsu.com/PRODUCT/ADC1804_F.html を取得して確認（DS PDF ではなく Web） | "・電源電圧：3.3V・5V（2電源）" / "●電源電圧：3.3・5V(2電源)" |
| ADC1804_F | 組立説明書の電源 | +3.3 V と +5 V の 2 電源 | 確かめられず | PDF（10 ページ）は取得できたが、この環境では日本語フォントが描画されず文字を読めない。1 ページ目の基板写真のシルクに "+3.3V" と "+5V" の端子があることだけ確かめた | — |

---

## 7. Abracon ASFL1（Abracon_ASFL1.pdf）

| 部品 | 項目 | switch_control.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|---|
| ASFL1 | SHA-256・12.288 MHz の区分（md 364 行目） | 1ea3fb87…956b、0.321〜29.9 MHz | 一致 | リポジトリの PDF の SHA-256 が同じ。区分は p1 の表どおり | `sha256sum` / "0.321MHz ~ 29.9MHz" |
| ASFL1 | 入力電流 | 8 / 15 mA | 一致 | p1、Typical/Maximum、Minimum は "-----" | "Input Current 0.321MHz ~ 29.9MHz ----- 8 15 mA" |
| ASFL1 | 他の区分 | 20/45、28/85 mA | 一致 | p1 | "30MHz ~ 79.9MHz ----- 20 45" / "80MHz ~ 133.33MHz ----- 28 85" |
| ASFL1 | Vdd | 2.97 / 3.3 / 3.63 V | 一致 | p1 | "Supply Voltage (Vdd) 2.97 3.3 3.63 V" |
| ASFL1 | 出力負荷 | 15 pF / 5 TTL max | 一致 | p1、Maximum | "----- ----- 15 pF" / "5 TTL" |
| ASFL1 | VOH / VOL | 0.9 Vdd min / 0.1 Vdd max | 一致 | p1 | "VOH 0.9*Vdd" / "VOL 0.1*Vdd" |
| ASFL1 | Tr/Tf | 5 / 10 ns | 一致 | p1、0.321〜29.9 MHz | "0.321MHz ~ 29.9MHz ----- 5 10 ns" |
| ASFL1 | デューティ | 40 / 50 / 60 %、S で 45/55 | 一致 | p1、OPTIONS "S: 45/55% @1/2Vdd" | "Symmetry (@ 1/2Vdd) 40 50 60 % See options" |
| ASFL1 | トライステート | "1"/Open 発振、"0" Hi-Z、0.7 / 0.3 Vdd | 一致 | p1 | "VIH 0.7*Vdd ... "1" or Open: Oscillation" / "VIL ... 0.3*Vdd ... "0": Ouput disable (Hi Z)" |
| ASFL1 | ディセーブル電流 | 10 µA max | 一致 | p1、Maximum 列（画像で確認） | "Disable Current 10 µA" |
| ASFL1 | 起動時間 | 1 / 10 ms | 一致 | p1 | "0.321MHz ~ 29.9MHz ----- 1 10 ms" |
| ASFL1 | 位相ジッタ | 1 ps max、参考値 | 一致 | p1 | "Phase Jitter RMS (12kHz to 20MHz) ----- ----- 1 ps Reference only." |
| ASFL1 | 周波数安定度 | ±100 ppm | 一致 | p1 | "Overall Frequency Stability -100 ----- +100 ppm See options" |
| ASFL1 | 動作温度 | –10 / +70 °C | 一致 | p1 | "Operating Temperature -10 ----- +70 °C See options" |
| ASFL1 | バイパス | 約 0.01 µF、PIN 2–4 | 一致 | p2 | "Note: Recommend using an approximately 0.01uF bypass capacitor between PIN 2 and 4." |
| ASFL1 | ピン配置 | 1 Tri-State、2 GND、3 Output、4 Vdd | 一致 | p2 | "1 Tri-State / 2 GND / 3 Output / 4 Vdd" |

---

## 無いとされていたが DS にあった項目

**無し。** 「探したが DS に無かった項目」36 件を本文検索（`pdftotext` 全ページ）と該当ページの画像で確かめ、どれも DS に数値は無かった。確かめた要点:

- TMUX7612: 電源 OFF 時の信号許容・フェイルセーフの記述は無い（"power-off" "unpowered" "fail-safe" で当たらない。当たるのは §7.3.5 のシーケンスの記述だけ）。SELx プルダウンの抵抗値は無い（Table 4-1 と §7.4 に "internal pull-down resistor" とあるだけ）。ACPSRR・OISO・XTALK の音声帯域の表値は無い（表は 100 kHz / 1 MHz、ACPSRR は 1 MHz のみ）。
- AZ850: 最小パルス幅、Must Release／リセット電圧、接触抵抗の測定条件は無い。定格電圧でのコイル電力も文字としては無い（表の定格電圧とコイル抵抗から V²/R で計算はできる）。
- TBD62083A: 入力抵抗の値は無い（p2 等価回路に直列抵抗・プルダウン抵抗・Clamp の記号はあるが値は無い）。熱抵抗は 11 ページのどこにも無い。
- MCP23017: 3.3 V での VOL/VOH/IPU は無い。POR 解除電圧の数値は無い（D002 VPOR は "VDD Start Voltage" で解除電圧ではない）。
- PT2314E: 最大入力の max、残留雑音の表値、出力段の独立した DC オフセットは無い。
- PCM1804: ICC のレート別の値、IDD のデュアル／クアッド max、スレーブモードの電源電流は無い。
- ASFL1: 入力電流の測定条件、12.288 MHz 固有の値、位相雑音は無い。

参考として、switch_control.md に載っていないが DS にある値（「無い」とは書かれていないので誤りではない）:

- PCM1804 p8: θJA 100 °C/W（TYP 列）。
- TMUX7612 p5 §5.4: Ipeak 470 mA（1 ms パルス・Duty 10 %、TJ = 25〜150°C すべて 470 mA）。
- PT2314E p12: I2C Input current –5〜+5 µA、I2C crosstalk 90 dB typ。
- AZ850 p1: コイル最高温度 105 °C、絶縁耐圧 1 kVRMS（コイル–接点・接点組間・開接点間）。
- ASFL1 p1: エージング ±5 ppm（+25°C、1 年目）。
