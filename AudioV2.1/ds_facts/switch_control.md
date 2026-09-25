# 切り替え・制御・音声 IC — データシートの事実

2026-09-25 収集。値は DS の原文で裏が取れたものだけ。設計判断は書かない。
2026-09-25 にページ画像と照合した（照合結果 [verify_switch_control.md](verify_switch_control.md)、その再判定 [../review/ds_errata_review.md](../review/ds_errata_review.md)）。その結果で直した行・足した行は、行末に 〔2026-09-25 照合で訂正〕／〔2026-09-25 照合で追加〕 を付けた。

- 表は `pdftotext -layout` で抜き、**min/typ/max の列はすべてページ画像（pdftoppm）で目視して確かめた**。
- 「列」欄は DS の表で値が載っている列。空欄の列は書かない（例: typ 列が空なら typ は DS に無い）。
- グラフからの読み取りは「**画像で目読み**」と明記した。精度はグラフの目盛り相当（数値保証ではない）。
- 出典のページ番号は PDF のページ番号（DS の印刷ページ番号と同じものは同じ）。

---

## 1. TI TMUX7612（`TI_TMUX7612.pdf`、SCDS466A – AUGUST 2023 – REVISED DECEMBER 2024）

### 構成・制御

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 構成 | 1:1 (SPST) × 4 ch、各 ch 独立選択 | — | — | TI_TMUX7612.pdf p1 | "four independently selectable 1:1, single-pole, single-throw (SPST) switch channels" |
| 制御ピン | SEL1〜SEL4（ch ごとに 1 本）、内部プルダウンあり | — | — | p3 Table 4-1 | "SEL1 ... Logic control input 1, has internal pull-down resistor. Controls channel 1 state as provided in Table 7-1." |
| 真理値 | SELx=0 → ch x OFF、SELx=1 → ch x ON | — | — | p29 Table 7-1 | "0 Channel x OFF" / "1 Channel x ON" |
| 外付け部品 | デカップリング以外不要、SELx は内部プルダウン | — | — | p28 §7.4 | "The TMUX7612 devices can be operated without any external components except for the supply decoupling capacitors. The SELx pins have internal pull-down resistors." |
| 論理入力の上限 | 制御ピンは 1.8 V ロジックから 44 V まで | — | — | p28 §7.4 | "The control pins operate down to 1.8 V logic and can be as high as 44 V." |
| VIH | 1.3 V / 44 V | –40〜+125°C | min / max | p6 §5.6 | "VIH Logic voltage high –40°C to +125°C 1.3 44 V" |
| VIL | 0 V / 0.8 V | –40〜+125°C | min / max | p6 §5.6 | "VIL Logic voltage low –40°C to +125°C 0 0.8 V" |
| IIH | 0.005 µA / 2 µA | –40〜+125°C | typ / max | p6 §5.6 | "IIH Input leakage current –40°C to +125°C 0.005 2 µA" |
| IIL | –2 µA / –0.005 µA | –40〜+125°C | min / typ | p6 §5.6 | "IIL Input leakage current –40°C to +125°C –2 –0.005 µA" |
| CIN | 4 pF | –40〜+125°C | typ | p6 §5.6 | "CIN Logic input capacitance –40°C to +125°C 4 pF" |
| 熱遮断 TSD / ヒステリシス | 165 °C / 15 °C | — | typ | p6 §5.6 | "TSD Thermal shutdown 165 °C" / "TSD_HYST Thermal shutdown hysteresis 15 °C" |
| N.C. ピン | GND へ短絡または浮かしてよい | — | — | p3 Table 4-1 | "No internal connection. Can be shorted to GND or left floating" |
| サーマルパッド（WQFN） | VSS へつなぐことを推奨 | — | — | p3 Table 4-1 | "The thermal exposed pad is connected internally. It is recommended that the pad be tied to VSS for best performance." |

### 電源電圧（推奨・絶対最大）

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 両電源範囲（Features） | ±4.5 V〜±25 V | — | — | p1 | "Dual supply range: ±4.5V to ±25V" |
| 単電源範囲（Features） | 4.5 V〜50 V | — | — | p1 | "Single supply range: 4.5V to 50V" |
| 推奨 VDD – VSS | 4.5 V / 50 V | — | min / max（nom 空欄） | p5 §5.5 | "VDD – VSS (1) Power supply voltage differential 4.5 50 V" |
| 推奨 VDD | 4.5 V / 50 V | — | min / max | p5 §5.5 | "VDD Positive power supply voltage 4.5 50 V" |
| 推奨の注 | 4.5 V ≤ (VDD–VSS) ≤ 50 V かつ最小 VDD を満たせば任意 | — | — | p5 §5.5 注(1) | "VDD and VSS can be any value as long as 4.5 V ≤ (VDD – VSS) ≤ 50 V, and the minimum VDD is met." |
| 推奨 VS/VD（信号） | VSS / VDD | — | min / max | p5 §5.5 | "Signal path input/output voltage (source or drain pin) (Sx, D) VSS VDD V" |
| 推奨 VSEL | 0 V / 44 V | — | min / max | p5 §5.5 | "VSEL Logic Supply Voltage ... 0 44 V" |
| 推奨 TA | –40 °C / 125 °C | — | min / max | p5 §5.5 | "TA Ambient temperature –40 125 °C" |
| 絶対最大 VDD – VSS | 53 V | — | max（min 空欄） | p4 §5.1 | "VDD – VSS ... 53 V" |
| 絶対最大 VDD | –0.5 V / 53 V | — | min / max | p4 §5.1 | "VDD Supply voltage –0.5 53 V" |
| 絶対最大 VSS | –32 V / 0.5 V | — | min / max | p4 §5.1 | "VSS –32 0.5 V" |
| 絶対最大 VSEL | –0.5 V / 53 V | — | min / max | p4 §5.1 | "VSEL Logic Supply Voltage –0.5 53 V" |
| 絶対最大 ISEL | –30 mA / 30 mA | SEL ピン | min / max | p4 §5.1 | "ISEL Logic control input pin current (SEL pins) –30 30 mA" |
| 絶対最大 VS/VD | VSS–0.5 / VDD+0.5 | — | min / max | p4 §5.1 | "VS or VD Source or drain voltage (Sx, Dx) VSS–0.5 VDD+0.5 V" |
| 絶対最大 IIK（ダイオードクランプ電流） | –30 mA / 30 mA | — | min / max | p4 §5.1 | "IIK Diode clamp current(3) –30 30 mA" / 注(3) "Pins are diode-clamped to the power-supply rails. Over voltage signals must be voltage and current limited to maximum ratings." |
| スイッチ連続電流 IDC | 470 mA（TJ=25/50/85°C）、309（105°C）、143（125°C）、100（135°C）、60（150°C） | VSS to VDD - 2.5V | 表（列区分なし） | p5 §5.4 | "IDC (1) VSS to VDD - 2.5V 470 470 470 309 143 100 60 mA" |
| ESD | HBM ±3000 V、CDM ±1500 V | all pins | 値 | p4 §5.2 | "Human body model (HBM) ... ±3000" / "Charged device model (CDM) ... ±1500" |

### IDD / ISS（±15 V 両電源の表）

表見出し: "VDD = +15 V ± 10%, VSS = –15 V ±10% GND = 0 V (unless otherwise noted) / Typical at VDD = +15 V, VSS = –15 V, TA = 25℃"（p7）。**電源電流の行の測定条件は VDD = 16.5 V, VSS = –16.5 V**（±15 V ではない）。

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| IDDQ（全 SW OFF） | 35 µA / 45 µA（25°C）、55 µA（–40〜+85°C）、65 µA（–40〜+125°C） | VDD=16.5 V, VSS=–16.5 V, All switches OFF | typ / max（温度範囲行は max のみ） | p7 §5.7 | "IDDQ VDD quiescent supply current VDD = 16.5 V, VSS = –16.5 V All switches OFF 25°C 35 45 ... 55 ... 65 µA" |
| IDD（全 SW ON） | 435 µA / 480 µA（25°C）、520 µA（–40〜+85°C）、545 µA（–40〜+125°C） | VDD=16.5 V, VSS=–16.5 V, All switches ON | typ / max（同上） | p7 §5.7 | "IDD VDD supply current VDD = 16.5 V, VSS = –16.5 V All switches ON 25°C 435 480 ... 520 ... 545 µA" |
| ISSQ（全 SW OFF） | 15 µA / 20 µA（25°C）、25 µA（–40〜+85°C）、40 µA（–40〜+125°C） | VDD=16.5 V, VSS=–16.5 V, All switches OFF | typ / max（同上） | p7 §5.7 | "ISSQ VSS quiescent supply current ... 25°C 15 20 ... 25 ... 40 µA" |
| ISS（全 SW ON） | 340 µA / 380 µA（25°C）、410 µA（–40〜+85°C）、425 µA（–40〜+125°C） | VDD=16.5 V, VSS=–16.5 V, All switches ON | typ / max（同上） | p8 §5.7（続き） | "ISS VSS supply current VDD = 16.5 V, VSS = –16.5 V All switches ON 25°C 340 380 ... 410 ... 425 µA" |
| 参考: ±20 V 表の IDD / ISS（全 ON） | IDD 435/480 µA、ISS 340/400 µA（25°C） | VDD=22 V, VSS=–22 V | typ / max | p10 §5.9 | "IDD ... VDD = 22 V, VSS = –22 V ... 25°C 435 480" / "ISS ... 25°C 340 400" |
| 参考: 12 V 単電源 IDD（全 ON） | 385 µA / 440 µA（25°C） | VDD=12 V, VSS=0 V | typ / max | p15 §5.13 | "IDD VDD supply current ... VDD = 12 V, VSS = 0 V ... 25°C 385 440" |

### Ron とその平坦度

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| RON（±15 V 表） | 1.1 Ω / 1.4 Ω（25°C）、1.6（–40〜+50°C）、1.8（–40〜+85°C）、2.2 Ω（–40〜+125°C） | VS = –10 V〜+10 V, ID = –10 mA | 25°C は typ / max、温度範囲行は max | p7 §5.7 | "RON On-resistance VS = –10 V to +10 V ID = –10 mA 25°C 1.1 1.4 ... 1.6 ... 1.8 ... 2.2 Ω" |
| ΔRON（ch 間不一致、±15 V） | 0.005 Ω（25°C）、0.045 / 0.055 / 0.060 Ω | 同上 | 25°C は **typ のみ**、温度範囲行は max | p7 §5.7 | "ΔRON ... 25°C 0.005 ... 0.045 ... 0.055 ... 0.060 Ω" |
| RON FLAT（±15 V） | **0.0003 Ω（25°C）**、0.045（–40〜+50°C）、0.055（–40〜+85°C）、0.060 Ω（–40〜+125°C） | VS = –10 V〜+10 V, ID = –10 mA | **25°C は typ のみ（max 空欄）**、温度範囲行は max | p7 §5.7 | "RON FLAT On-resistance flatness VS = –10 V to +10 V ID = –10 mA 25°C 0.0003 ... 0.045 ... 0.055 ... 0.060 Ω" |
| RON DRIFT（±15 V） | 0.006 Ω/°C | VS = 0 V, IS = –10 mA, –40〜+125°C | typ | p7 §5.7 | "RON DRIFT On-resistance drift VS = 0 V, IS = –10 mA –40°C to +125°C 0.006 Ω/°C" |
| RON（±20 V） | 1.1 / 1.4 Ω（25°C）、1.6 / 1.9 / 2.2 Ω | VS = –15〜+15 V, ID = –10 mA | typ / max、温度行 max | p10 §5.9 | "VS = –15 V to +15 V ... 25°C 1.1 1.4 ... 1.6 ... 1.9 ... 2.2" |
| RON FLAT（±20 V） | 0.006 Ω（25°C）、0.065 / 0.070 / 0.075 Ω | VS = –15〜+15 V | 25°C typ、温度行 max | p10 §5.9 | "RON FLAT ... 25°C 0.006 ... 0.065 ... 0.070 ... 0.075" |
| RON（+37.5/–12.5 V） | 1.1 / 1.35 Ω（25°C）、1.6 / 1.8 / 2.1 Ω | VS = –7.5〜32.5 V | typ / max、温度行 max | p12 §5.11 | "VS = –7.5 V to 32.5 V ... 25°C 1.1 1.35 ... 1.6 ... 1.8 ... 2.1" |
| RON FLAT（+37.5/–12.5 V） | 0.006 Ω（25°C）、0.075 / 0.080 / 0.085 Ω | 同上 | 25°C typ、温度行 max | p12 §5.11 | "RON FLAT ... 25°C 0.006 ... 0.075 ... 0.080 ... 0.085" |
| RON（12 V 単電源） | 1.15 / 1.6 Ω（25°C）、1.75 / 2 / 2.3 Ω | VS = 3〜9 V | typ / max、温度行 max | p15 §5.13 | "VS = 3 V to 9 V ... 25°C 1.15 1.6 ... 1.75 ... 2 ... 2.3" |
| RON FLAT（12 V 単電源） | 0.084 Ω（25°C）、0.13 / 0.15 / 0.16 Ω | VS = 3〜9 V | 25°C typ、温度行 max | p15 §5.13 | "RON FLAT ... 25°C 0.084 ... 0.13 ... 0.15 ... 0.16" |
| 平坦域の説明（本文） | 概ね VSS+5 V〜VDD–5 V | — | — | p27 §7.3.4 | "The flattest on-resistance region extends roughly from 5 V above VSS to 5 V below VDD. As long as this headroom is maintained, the TMUX7612 exhibits an extremely linear response." |
| DS 内の食い違い: Figure 5-1 の 25°C の線（**画像で目読み**） | 約 0.95 Ω（VS = –10〜+10 V で水平）。表 §5.7 の typ 1.1 Ω・Figure 5-4 の底（約 1.1 Ω）と合わない。数値の根拠には表を使う | VDD = 15 V, VSS = –15 V（温度別の線のうち 25°C） | グラフ | p17 Figure 5-1 | 図題 "Figure 5-1. On-Resistance vs Source or Drain Operational Voltage"、図中 "VDD=15V, VSS=-15V" 〔2026-09-25 照合で追加〕 |

### Figure 5-4（Ron vs VS/VD、両電源 ±10/±12/±13.5/±15/±16.5 V、TA = 25°C）— **画像で目読み**

出典: TI_TMUX7612.pdf p17 Figure 5-4 "On-Resistance vs Source or Drain Voltage for dual supply"、凡例 "VDD/SS = ±10V / ±12V / ±13.5V / ±15V / ±16.5V"、"TA = 25°"。縦軸 1〜7.5 Ω（0.5 Ω 目盛り）、横軸 –20〜20 V（5 V 目盛り）。400〜900 dpi に拡大して読んだ。読み取り誤差は横軸 ±0.3〜0.5 V 程度。

平坦部の底はどの曲線も約 1.1 Ω（目読み）。**正側（VDD 側）は急峻に立ち上がり、約 7.4 Ω（軸上限 7.5 Ω のすぐ下）で水平になって VDD まで続く。この水平部は測定上限か作図の打ち切りとみられ、実際の Ron を表すものではない（目読み）。負側（VSS 側）は立ち上がりが小さく、端で約 1.25 Ω に上がるだけ**（目読み）。 〔2026-09-25 照合で訂正〕

| 電源 | 正側: 底から離れ始める VS（目読み） | 正側: 1.5 Ω を越える VS（目読み） | 正側: 縦に立ち上がる（〜7.4 Ω で頭打ち）VS（目読み） | 負側: 端（VSS）での Ron と、底に戻る VS（目読み） 〔2026-09-25 照合で訂正〕 |
|---|---|---|---|---|
| ±10 V | 約 +5.6 V | 約 +8.1 V | 約 +8.7〜9.0 V | VSS 端 約 1.25 Ω、約 –6 V で底へ |
| ±12 V | 約 +7.6 V | 約 +10.0 V | 約 +10.6〜11 V | VSS 端 約 1.25 Ω、約 –8 V で底へ |
| ±13.5 V | 約 +9.0 V | 約 +11.6 V | 約 +12.2〜12.5 V | VSS 端 約 1.25 Ω、約 –9.5 V で底へ |
| ±15 V | 約 +10.6 V | 約 +13.1 V | 約 +13.8〜14 V | VSS 端 約 1.25 Ω、約 –11.5 V で底へ |
| ±16.5 V | 約 +12.0 V | 約 +14.6 V | 約 +15.2〜15.5 V | VSS 端 約 1.25 Ω、約 –12.5 V で底へ |

注: 「離れ始める」点は、後ろの曲線が手前の曲線（±16.5 V の紫が最前面）に隠れるため、色が見え始める点で読んでいる。定量的な根拠には表の RON / RON FLAT を使うこと（表の条件範囲は ±15 V で VS = –10〜+10 V）。

### ACPSRR

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| ACPSRR（±15 V） | –80 dB | VPP = 0.62 V on VDD and VSS, RL = 50 Ω, CL = 5 pF, **f = 1 MHz**, 25°C | typ | p9 §5.8 | "ACPSRR AC Power Supply Rejection Ratio VPP = 0.62 V on VDD and VSS RL = 50 Ω , CL = 5 pF, f = 1 MHz 25°C –80 dB" |
| ACPSRR（±20 V） | –76 dB | 同上（f = 1 MHz） | typ | p11 §5.10 | "ACPSRR ... 25°C –76 dB" |
| ACPSRR（+37.5/–12.5 V） | –80 dB | 同上（f = 1 MHz） | typ | p14 §5.12 | "ACPSRR ... 25°C –80 dB" |
| ACPSRR（12 V 単電源） | –78 dB | 同上（f = 1 MHz） | typ | p16 §5.14 | "ACPSRR ... 25°C –78 dB" |
| 測定法の本文 | 本文は 100 mVPP、表と図 6-11 は 620 mVPP（DS 内で食い違い、原文のまま） | — | — | p26 §6.11 / Figure 6-11 | "The DC voltage on the device supply is modulated by a sine wave of 100 mVPP." / 図中 "620 mVPP"、"With & Without Capacitor"、"0.1 µF" |
| Figure 5-19 ACPSRR vs Frequency（**画像で目読み**） | 10 Hz〜1 kHz: 4 曲線とも約 –100〜–115 dB。10 kHz: VDD with cap 約 –89、VSS with cap 約 –80、VSS without cap 約 –78、VDD without cap 約 –88 dB。20 kHz: VDD with cap 約 –86、VSS with cap 約 –77、VSS without cap 約 –72、VDD without cap 約 –82 dB。100 kHz: 約 –85 / –76 / –57 / –68 dB（同順）。1 MHz: 約 –83 / –77 / –38 / –46 dB（同順） | 凡例 "VDD with cap / VSS with cap / VSS without cap / VDD without cap"。図に電源電圧の注記なし（ページ見出し "at TA = 25°C (unless otherwise noted)"） | グラフ | p20 Figure 5-19 | 図題 "Figure 5-19. ACPSRR vs Frequency" |

### OFF アイソレーション・クロストーク・その他 AC（±15 V 表）

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| OISO | –105 dB | RL = 50 Ω, CL = 5 pF, VS = 200 mVRMS, VBIAS = 0 V, f = 100 kHz | typ | p9 §5.8 | "OISO Off-isolation RL = 50 Ω , CL = 5 pF VS = 200 mVRMS, VBIAS = 0 V, f = 100 kHz 25°C –105 dB" |
| OISO | –74 dB | 同上、f = 1 MHz | typ | p9 §5.8 | "OISO Off-isolation ... f = 1 MHz 25°C –74 dB" |
| XTALK | –114 dB | 同上、f = 100 kHz | typ | p9 §5.8 | "XTALK Crosstalk ... f = 100 kHz 25°C –114 dB" |
| XTALK | –105 dB | 同上、f = 1 MHz | typ | p9 §5.8 | "XTALK Crosstalk ... f = 1MHz 25°C –105 dB" |
| Figure 5-15 Off-Isolation vs Frequency（**画像で目読み**） | 10 Hz〜約 300 kHz で約 –100〜–105 dB、それ以上で上昇 | VDD/SS = ±15V | グラフ | p19 Figure 5-15 | 凡例 "VDD/SS = ±15V" |
| Figure 5-16 Crosstalk vs Frequency（**画像で目読み**） | 100 Hz〜約 3 MHz で約 –100〜–110 dB（隣接・非隣接ほぼ同じ） | VDD/SS = ±15V Adjacent / Non-adjacent channels | グラフ | p19 Figure 5-16 | 凡例 "VDD/SS = ±15V Adjacent channels" / "Non-adjacent channels" |
| THD+N | 0.0006 % | VPP = 15 V, VBIAS = 0 V, RL = 110 Ω, CL = 5 pF, f = 20 Hz〜20 kHz | typ | p9 §5.8 | "THD+N ... VPP = 15 V, VBIAS = 0 V RL = 110 Ω , CL = 5 pF, f = 20 Hz to 20 kHz 25°C 0.0006 %" |
| QINJ | –2 pC | VS = 0 V, CL = 100 pF | typ | p9 §5.8 | "QINJ Charge injection VS = 0 V, CL = 100 pF 25°C -2 pC" |
| CS(OFF) / CD(OFF) / C(ON) | 27 / 27 / 22 pF | VS = 0 V, f = 1 MHz | typ | p9 §5.8 | "CS(OFF) ... 27 pF" / "CD(OFF) ... 27 pF" / "On capacitance to ground ... 22 pF" |
| tON / tOFF | 2.0 / 2.5 µs、1.7 / 2.2 µs（25°C） | VS = 10 V, RL = 300 Ω, CL = 35 pF | typ / max | p9 §5.8 | "tON ... 25°C 2.0 2.5 µs" / "tOFF ... 25°C 1.7 2.2 µs" |
| tBBM | 310 ns（25°C typ）、125 ns（–40〜+85 / +125°C min） | 同上 | 25°C typ、温度行 **min** | p9 §5.8 | "tBBM ... 25°C 310 ns ... –40°C to +85°C 125 ns ... –40°C to +125°C 125 ns"（画像で 125 は MIN 列） |

### 電源を入れていないとき・電源シーケンス

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 電源シーケンス | 任意の順で投入・遮断してよい | — | — | p28 §7.3.5 | "The TMUX7612 supports any power up sequencing. With the supply rails (VDD and VSS), any rail can be powered on first. Similarly, when powering down the supply rails can be powered down in any order." |
| GND の先行接続 | 電源を立ち上げる前に GND を確立 | — | — | p33 §8.4 | "Always make sure a solid ground (GND) connection is established before supplies are ramped." |
| ピンのクランプ | Sx/Dx 等は電源レールへダイオードクランプ | — | — | p4 §5.1 注(3) | "Pins are diode-clamped to the power-supply rails." |

### 推奨デカップリング

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| VDD/VSS–GND 間 | 0.1 µF〜10 µF | 各ピン | — | p3 Table 4-1 | "For reliable operation, connect a decoupling capacitor ranging from 0.1 µF to 10 µF between VDD and GND" |
| 推奨組み合わせ | 0.1 µF と 1 µF、小さい方をピンの近くに | — | — | p34 §8.5.1 | "We recommend a 0.1 µF and 1 µF capacitor, placing the lowest value capacitor as close to the pin as possible. Make sure that the capacitor voltage rating is sufficient for the supply voltage." |
| 種類 | MLCC（低 ESR・ESL） | — | — | p33 §8.4 | "TI recommends using multi-layer ceramic chip capacitors (MLCCs) that offer low equivalent series resistance (ESR) and inductance (ESL) characteristics for power-supply decoupling purposes." |

### 探したが DS に無かった項目

- **電源を入れていないとき（VDD=VSS=0）に Sx/Dx へ信号が来た場合の挙動・許容**（パワーオフ保護・フェイルセーフの記述）: 無い。あるのは上記のシーケンス自由・ダイオードクランプ・絶対最大 VS/VD = VSS–0.5〜VDD+0.5 だけ。
- **ACPSRR の音声帯域（20 Hz〜20 kHz）の表値**: 表は f = 1 MHz のみ。音声帯域は Figure 5-19 の目読みしかない。
- **±15 V での OISO / XTALK の 1 kHz・20 kHz の表値**: 表は 100 kHz と 1 MHz のみ。
- **SELx 内部プルダウンの抵抗値**: 記載無し（IIH / IIL のみ）。
- **±15 V 表で RON FLAT の 25°C max**: 空欄（typ 0.0003 Ω のみ）。

---

## 2. Zettler AZ850（`Zettler_AZ850.pdf`、2 ページ、2019-03-26）

型番の付け方: "AZ850 [P1/P2] - [Nominal coil voltage]"、"nil: monostable non-latching / P1: bistable single coil latching / P2: bistable dual coil latching"（p2 ORDERING DATA）。

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 接点構成 | DPDT (2 Form C)、バイファーケート・クロスバー接点 | — | — | Zettler_AZ850.pdf p1 CONTACTS | "Arrangement DPDT (2 Form C) Bifurcated crossbar contacts" |
| 5 V 単コイルラッチ（P1）コイル抵抗 | 250 Ω ±10 % | 20°C（注 2） | 表値 | p2 "Single coil latching" | "5 3.75 14.5 250"（列見出し "Nominal Coil VDC / Must Operate VDC / Max. Continuous VDC / Resistance Ohm ± 10%"） |
| 5 V 単コイルラッチ（P1）Must Operate | 3.75 VDC | 20°C | 表値 | p2 同上 | 同上 |
| 5 V 単コイルラッチ（P1）Max. Continuous | 14.5 VDC | 20°C | 表値 | p2 同上 | 同上 |
| 5 V 2 コイルラッチ（P2）コイル抵抗 | 125 Ω ±10 % | 20°C | 表値 | p2 "Dual coil latching" | "5 3.75 10.0 125" |
| 5 V 2 コイルラッチ（P2）Must Operate | 3.75 VDC | 20°C | 表値 | p2 同上 | 同上 |
| 5 V 2 コイルラッチ（P2）Max. Continuous | 10.0 VDC | 20°C | 表値 | p2 同上 | 同上 |
| 参考: 5 V 非ラッチ | 抵抗 178 Ω、Must Operate 3.75 V、Max. Continuous 12.5 V | 20°C | 表値 | p2 "Monostable non-latching" | "5 3.75 12.5 178" |
| コイル電力（**感動電圧での値**） | 単コイルラッチ 56〜84 mW、2 コイルラッチ 113〜169 mW、非ラッチ 79〜113 mW | "Power at pickup voltage" | typ（範囲表記） | p1 COIL | "Power at pickup voltage (typ.) monostable non-latching 79 - 113 mW bistable single coil latching 56 - 84 mW bistable dual coil latching 113 - 169 mW" |
| セット時間（ラッチ型） | 2 ms | 定格コイル電圧 | typ | p1 GENERAL DATA | "Set Time at nominal coil voltage latching types 2 ms (typ.)" |
| リセット時間（ラッチ型） | 1 ms | 定格コイル電圧 | typ | p1 GENERAL DATA | "Reset Time at nominal coil voltage latching types 1 ms (typ.)" |
| 動作時間 / 復帰時間（非ラッチ） | 2 ms / 1 ms | 定格コイル電圧、復帰はコイルサプレッションなし | typ | p1 | "Operate Time ... non-latching types 2 ms (typ.)" / "Release Time at nominal coil voltage, w/o coil suppression non-latching types 1 ms (typ.)" |
| コイル極性 | 固定 | — | — | p2 NOTES 5 | "Relay has fixed coil polarity" |
| 感動 | Must Operate 未満でも吸引しうる | — | — | p2 NOTES 3 | "Relay may pull in with less than “Must Operate” value." |
| コイル並列サプレッサ | 復帰時間が延びる | — | — | p2 NOTES 4 | "Coil suppression circuits such as diodes, etc. in parallel to the coil will lengthen the release time." |
| 接点定格（抵抗負荷、max） | 30 W または 62.5 VA、開閉電流 1 A、通電電流 2 A、開閉電圧 220 VDC または 250 VAC | resistive load。220 VDC には注: 30 VDC を越える開閉は要相談（"\* Note: If switching voltage is greater than 30 VDC, special precautions must be taken. Please contact the factory."） | max | p1 CONTACTS | "Ratings (max.) (resistive load) switched power 30 W or 62.5 VA switched current 1A carry current 2A switched voltage 220 VDC* or 250 VAC" 〔2026-09-25 照合で訂正〕 |
| 定格負荷（UL, CUR） | 1 A at 30 VDC、0.5 A at 125 VAC（抵抗負荷） | — | — | p1 | "UL, CUR 1 A at 30 VDC, resistive 0.5 A at 125 VAC, resistive" |
| 最小開閉 | 10 mV、10 µA | — | — | p1 | "Minimum switching voltage 10 mV current 10 µA" |
| 接点材質 | AgPd（銀パラジウム）、金クラッド | — | — | p1 | "Contact materials AgPd - silver palladium, gold clad" |
| 初期接触抵抗 | < 50 mΩ | — | max（"<" 表記） | p1 | "Initial resistance < 50 mΩ" |
| 寿命（機械） | 1 × 10^6 回 | — | min（"minimum operations"） | p1 GENERAL DATA | "Life Expectancy (minimum operations) mechanical 1 x 10^6" |
| 寿命（電気） | 2 × 10^5 回 at 1 A 30 VDC、1 × 10^5 回 at 0.5 A 125 VAC（抵抗負荷） | — | min | p1 | "electrical 2 x 10^5 at 1 A 30 VDC resistive 1 x 10^5 at 0.5 A 125 VAC resistive" |
| 動作温度 | –40〜85 °C | 定格コイル電圧 | — | p1 | "Temperature Range (at nominal coil voltage) operating -40°C (-40°F) to 85°C (158°F)" |
| 温度上昇 | 18 K | 定格コイル電圧 | — | p1 COIL | "Temperature Rise at nominal coil voltage 18 K (32°F)" |
| 静電容量 | コイル–接点 0.9 pF、接点組間 0.2 pF、開接点間 0.4 pF | — | typ | p1 | "Capacitance (typ.) coil to contacts 0.9 pF between contact sets 0.2 pF between open contacts 0.4 pF" |
| 絶縁抵抗 | 1000 MΩ | 20°C, 500 VDC, 50 % RH | min | p1 | "Insulation Resistance 1000 MΩ (min.) at 20°C, 500 VDC, 50% RH" |
| 隣接リレー間隔 | 5.0 mm 推奨（磁界の分離） | — | — | p2 NOTES 6 | "For complete isolation between the relay’s magnetic fields, it is recommended that a .197" (5.0 mm) space be provided between adjacent relays." |

### 探したが DS に無かった項目

- **セット/リセットに要る最小パルス幅**: 無い（あるのはセット時間 2 ms typ・リセット時間 1 ms typ のみ）。
- **定格電圧でのコイル電力**: 無い（DS の電力は "Power at pickup voltage" のみ）。
- **ラッチ型の Must Release / リセット電圧**（逆極性・リセットコイル側の必要電圧）: 無い。表は "Must Operate" と "Max. Continuous" のみ。
- **接触抵抗の測定条件**（電流・電圧）: 無い。
- **ラッチ型の非ラッチ用 Dropout 相当**: Dropout は "non-latching types > 10% of nominal coil voltage" のみ。
- 物性の詳細は DS が "application notes"（www.ZETTLERelectronics.com/pdfs/relais/ApplicationNotes.pdf）を参照せよとしている（p2 DISCLAIMER）。未取得。

---

## 3. Toshiba TBD62083A（`Toshiba_TBD62083A.pdf`、11 ページ、2026-05-13 版）

8 回路のシンク型 DMOS トランジスタアレイ、各出力にクランプダイオード（p1 "8channel sink type DMOS transistor array"、"It has a clamp diode for switching inductive loads built-in in each output."）。パッケージ PG（P-DIP18）/ FG（SOP18）/ FNG（SSOP18）/ FWG（P-SOP18）。

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 絶対最大 出力電流 | 500 mA/ch | Ta = 25 °C | 定格値 | Toshiba_TBD62083A.pdf p3 | "Output current IOUT 500 mA/ch" |
| 絶対最大 出力電圧 | 50 V | Ta = 25 °C | 定格値 | p3 | "Output voltage VOUT 50 V" |
| 絶対最大 COMMON 電圧 | –0.5〜50 V | — | 定格値 | p3 | "COMMON pin voltage VCOM −0.5 to 50 V" |
| 絶対最大 入力電圧 | –0.5〜30 V | — | 定格値 | p3 | "Input voltage VIN −0.5 to 30 V" |
| 動作範囲 出力電流（1 回路 ON） | 0〜400 mA/ch（PG/FG/FNG/FWG 共通） | Ta = 25°C | min / max | p4 Operating Ranges | "1 circuits ON, Ta = 25°C 0 ― 400" |
| 動作範囲 出力電流（8 回路同時 ON、Duty 10 %） | PG 390、FG 320、FNG 320、FWG 370 mA/ch | tpw = 25 ms, 8 circuits ON, Ta = 85°C, Tj = 120°C, Duty = 10% | max | p4 | "tpw = 25 ms 8 circuits ON Ta = 85°C Tj = 120°C Duty = 10% 0 ― 390"（PG）ほか |
| 動作範囲 出力電流（8 回路同時 ON、Duty 50 %） | PG 170、FG 140、FNG 140、FWG 160 mA/ch | 同上、Duty = 50% | max | p4 | "Duty = 50% 0 ― 170"（PG）ほか |
| 動作範囲の注 | PG/FG は Device alone、FNG は 50×50×1.6 mm・Cu 40 %、FWG は 75×114×1.6 mm・Cu 20 %（片面ガラエポ） | — | — | p4 注 | "Note1: Device alone." / "Note2: On PCB (Size: 50 mm × 50 mm × 1.6 mm, Cu area: 40%, single-side glass epoxy)." / "Note3: On PCB (Size: 75 mm × 114 mm × 1.6 mm, Cu area: 20%, single-side glass epoxy)." |
| 出力電圧 VDS（出力 ON 抵抗） | 0.7 V / 1.14 V（RON 2.0 / 3.25 Ω） | IOUT = 350 mA, VIN = 5.0 V | typ / max | p5 Electrical Characteristics | "IOUT = 350 mA, VIN =5.0V ― 0.7 (2.0) 1.14 (3.25)" |
| 同上 | 0.4 V / 0.65 V（2.0 / 3.25 Ω） | IOUT = 200 mA, VIN = 5.0 V | typ / max | p5 | "IOUT = 200 mA, VIN =5.0V ― 0.4 (2.0) 0.65 (3.25)" |
| 同上 | 0.2 V / 0.325 V（2.0 / 3.25 Ω） | IOUT = 100 mA, VIN = 5.0 V | typ / max | p5 | "IOUT = 100 mA, VIN =5.0V ― 0.2 (2.0) 0.325 (3.25)" |
| 入力電圧（出力 ON）動作範囲 | 2.5 V / 25 V | IOUT = 100 mA or upper, VOUT = 2 V | min / max | p4 | "TBD62083A series ... IOUT = 100 mA or upper, VOUT = 2 V 2.5 ― 25" |
| 入力電圧（出力 OFF）動作範囲 | 0 V / 0.6 V | IOUT = 100 µA or less, VOUT = 2 V | min / max | p4 | "IOUT = 100 μA or less, VOUT = 2 V 0 ― 0.6" |
| VIN(ON)（電気的特性） | 2.5 V | IOUT = 100 mA, VOUT = 2 V | max | p5 | "Input voltage (Output on) ... VIN (ON) 5 IOUT = 100 mA, VOUT = 2 V ― ― 2.5" |
| 入力電流（出力 ON） | 0.1 mA | VIN = 2.5 V | max | p5 | "TBD62083A series VIN = 2.5 V ― ― 0.1 mA" |
| 入力電流（出力 OFF） | 1.0 µA | VIN = 0 V, Ta = 85°C | max | p5 | "Input current(Output off) IIN (OFF) 4 VIN = 0 V, Ta = 85°C ― ― 1.0 μA" |
| 出力リーク | 1.0 µA | VOUT = 50 V, Ta = 85°C, VIN = 0 V | max | p5 | "Output leakage current Ileak 1 VOUT = 50V, Ta = 85°C VIN = 0 V ― ― 1.0 μA" |
| クランプダイオード 逆電圧（絶対最大） | 50 V | — | 定格値 | p3 | "Clamp diode reverse voltage VR 50 V" |
| クランプダイオード 順電流（絶対最大） | 500 mA | — | 定格値 | p3 | "Clamp diode forward current IF 500 mA" |
| クランプダイオード 順電流（動作範囲） | 400 mA | — | max | p4 | "Clamp diode forward current IF ― ― ― 400 mA" |
| クランプダイオード VF | 2.0 V | IF = 350 mA | max | p5 | "Clamp diode forward voltage VF 7 IF = 350 mA ― ― 2.0 V" |
| クランプダイオード IR | 1.0 µA | VR = 50 V, Ta = 85°C | max | p5 | "Clamp diode reverse current IR ― ― 1.0 μA" |
| クランプ接続 | 各出力のクランプダイオードのカソードは COMMON ピン（等価回路） | — | — | p2 Equivalent circuit | 等価回路図 "COMMON / Clamp diode / OUTPUT" |
| 許容損失 PD | PG 1.47 W、FG 0.96 W、FNG 0.96 W、FWG 1.31 W | Ta = 25 °C | 定格値 | p3 | "Power dissipation PD PG (Note1) 1.47 FG (Note2) 0.96 FNG (Note3) 0.96 FWG (Note4) 1.31 W" |
| PD の軽減 | PG 11.8 mW/°C、FG 7.7 mW/°C、FNG 7.7 mW/°C、FWG 10.48 mW/°C（Ta > 25 °C） | PG/FG は Device alone、FNG/FWG は上記基板 | — | p3 注 1〜4 | "Note1: Device alone. When Ta exceeds 25 °C, it is necessary to do the derating with 11.8 mW/°C." ほか |
| tON / tOFF | 0.4 µs / 0.8 µs | VOUT = 50 V, RL = 125 Ω, CL = 15 pF。試験回路 8（p7）: 入力パルス 50 µs・Duty 10 %・**VIH = 5.0 V**・tr ≤ 5 ns・tf ≤ 10 ns。CL はプローブ・基板を含む | typ | p5 | "Turn−on delay tON ... ― 0.4 ―" / "Turn−off delay tOFF ... ― 0.8 ―" / p7 "Note 1: Pulse width 50 μs, Duty cycle 10%"、"TBD62083A series 5.0 V"、"Note 2: CL includes the probe and the test board capacitance." 〔2026-09-25 照合で訂正〕 |
| 動作温度 | –40〜85 °C | — | — | p3 | "Operating temperature Topr −40 to 85 °C" |
| 保護回路 | 過電流・過電圧保護は内蔵しない | — | — | p7 Precautions | "This IC does not include built-in protection circuits for excess current or overvoltage." |

### 探したが DS に無かった項目

- **入力抵抗（入力の直列抵抗・プルダウン抵抗の値）**: 無い。等価回路（p2）に抵抗の記号はあるが値は書かれていない。入力側の電気量は IIN(ON) max 0.1 mA @ VIN = 2.5 V と IIN(OFF) のみ。
- **入力しきい値の typ**: 無い（動作範囲の min/max と VIN(ON) max のみ）。
- **全 ch 同時の Ta = 25 °C での出力電流**: 無い（8 回路同時は Ta = 85°C, Tj = 120°C, tpw = 25 ms の条件のみ）。
- **連続（デューティ 100 %）で 8 回路同時の値**: 無い。
- 熱抵抗（Rth(j-a)）の明示値: 無い（PD と軽減率のみ）。

---

## 4. Microchip MCP23017（`Microchip_MCP23017.pdf`、DS20001952C）

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 電源電圧 VDD（DC 特性） | 1.8 V / 5.5 V | 表見出し "1.8V ≤ VDD ≤ 5.5V at -40°C ≤ TA ≤ +125°C" | min / max | Microchip_MCP23017.pdf p4 Table 1-1 D001 | "D001 Supply Voltage VDD 1.8 — 5.5 V" |
| 動作電圧（Features） | 1.8〜5.5 V @ –40〜+85 °C、2.7〜5.5 V @ –40〜+85 °C、4.5〜5.5 V @ –40〜+125 °C | — | — | p1 Features | "Operating Voltage: - 1.8V to 5.5V @ -40°C to +85°C - 2.7V to 5.5V @ -40°C to +85°C - 4.5V to 5.5V @ -40°C to +125°C"（原文のまま。2 行目も –40〜+85 °C と書かれている） |
| 絶対最大 VDD | –0.3 V〜+5.5 V | VSS 基準 | 定格値 | p3 | "Voltage on VDD with respect to VSS ... -0.3V to +5.5V" |
| 絶対最大 他ピン | –0.6 V〜(VDD + 0.6 V) | VSS 基準 | 定格値 | p3 | "Voltage on all other pins with respect to VSS (except VDD) ... -0.6V to (VDD + 0.6V)" |
| POR 後の IODIRA / IODIRB | 1111 1111（全ピン入力） | POR/RST 値 | — | p16 Table 3-2/3-3、p17 Table 3-4/3-5 | "IODIRA 00 IO7 ... IO0 1111 1111" / "IODIRB ... 1111 1111" |
| IODIR ビットの意味 | 1 = 入力、0 = 出力 | — | — | p18 Register 3-1 | "1 = Pin is configured as an input. 0 = Pin is configured as an output." |
| Features の記述 | I/O は既定で入力 | — | — | p1 | "I/O pins default to input" |
| POR 後のその他レジスタ | IPOL、GPINTEN、DEFVAL、INTCON、IOCON、GPPU、INTF、INTCAP、GPIO、OLAT はすべて 0000 0000 | POR/RST 値 | — | p16 Table 3-2/3-3、p17 Table 3-4、p17〜18 Table 3-5 | 例 "IOCON 05 BANK MIRROR SEQOP DISSLW HAEN ODR INTPOL — 0000 0000"、"OLATA 0A ... 0000 0000"（引用の番地は BANK = 1 の Table 3-4 のもの。POR 後は BANK = 0 なので番地は Table 3-5: IOCON 0x0A/0x0B、OLATA 0x14） 〔2026-09-25 照合で訂正〕 |
| 内部プルアップ | あり（GPPU で ch ごとに有効化、入力設定時のみ）。本文は 100 kΩ | — | — | p22 §3.5.7 | "If a bit is set and the corresponding pin is configured as an input, the corresponding port pin is internally pulled up with a 100 kΩ resistor." |
| 内部プルアップの既定 | 無効（GPPU = 0000 0000、R/W-0） | POR | — | p16 Table 3-2/3-3、p22 Register 3-7 | "GPPUA 06 PU7 ... PU0 0000 0000" / "R/W-0 R/W-0 ..." / "1 = Pull-up enabled" |
| プルアップ電流 IPU | 40 µA / 75 µA / 115 µA | VDD = 5V, GP pins = VSS | min / typ / max | p4 D070 | "D070 GPIO weak pull-up current IPU 40 75 115 µA VDD = 5V GP pins = VSS" |
| VOL（GPIO） | 0.6 V | IOL = 8.0 mA, VDD = 4.5V | max | p4 D080 | "D080 GPIO VOL — — 0.6 V IOL = 8.0 mA VDD = 4.5V" |
| VOH（GPIO, INT, SO） | VDD – 0.7 V | IOH = –3.0 mA, VDD = 4.5V | min | p4 D090 | "D090 GPIO, INT, SO VOH VDD – 0.7 — — V IOH = -3.0 mA VDD = 4.5V" |
| VOH（同） | VDD – 0.7 V | IOH = –400 µA, VDD = 1.8V | min | p4 D090 | "VDD – 0.7 — — IOH = -400 µA VDD = 1.8V" |
| 1 ピンのシンク / ソース電流（絶対最大） | 25 mA / 25 mA | — | 定格値 | p3 | "Maximum output current sunk by any output pin ... 25 mA" / "Maximum output current sourced by any output pin ... 25 mA" |
| VSS 流出 / VDD 流入（絶対最大） | 150 mA / 125 mA | — | 定格値 | p3 | "Maximum current out of VSS pin ... 150 mA" / "Maximum current into VDD pin ... 125 mA" |
| 総損失（絶対最大） | 700 mW | — | 定格値 | p3 | "Total power dissipation ... 700 mW" |
| 入力 VIL / VIH（GPIO, SCL, SDA, RESET、シュミット） | VSS〜0.2 VDD / 0.8 VDD〜VDD | — | min / max | p4 D031/D041 | "D031 CS, GPIO, SCL/SCK, SDA, RESET (Schmitt Trigger) VIL VSS — 0.2 VDD V" / "D041 ... VIH 0.8 VDD — VDD V For entire VDD range" |
| 電源電流 IDD | 1 mA | SCL/SCK = 1 MHz | max | p4 D004 | "D004 Supply Current IDD — — 1 mA SCL/SCK = 1 MHz" |
| 待機電流 IDDS | 1 µA（–40〜+85°C）、3 µA（4.5〜5.5 V、+85〜+125°C） | — | max | p4 D005 | "D005 Standby current IDDS8 — — 1 µA -40°C ≤ TA ≤ +85°C" / "— — 3 µA 4.5V ≤ VDD ≤ 5.5V +85°C ≤ TA ≤+125°C (Note 1)" |
| POR 開始電圧 / 立ち上がり速度 | VPOR = VSS（typ）、SVDD ≥ 0.05 V/ms（設計指針・非試験） | — | typ / min | p4 D002/D003 | "D002 VDD Start Voltage to ensure Power-on Reset VPOR — VSS — V" / "D003 VDD Rise Rate to ensure Power-on Reset SVDD 0.05 — — V/ms Design guidance only. Not tested." |
| POR の動作 | VDD が十分上がるまでリセット保持、解除後は動作条件を満たす必要 | — | — | p12 §3.1 | "The on-chip POR circuit holds the device in reset until VDD has reached a high enough voltage to deactivate the POR circuit" |
| RESET ピン | 外部でバイアス必須 | — | — | p11 Table 2-1 | "RESET 14 18 I Hardware reset. Must be externally biased." |
| アドレスピン A0–A2 | 外部でバイアス必須 | — | — | p11 Table 2-1 | "A0 ... Hardware address pin. Must be externally biased." |
| RESET パルス幅 | 1 µs | — | min | p5 Table 1-2 | "30 RESET Pulse Width TRSTL 1 — — µs" |
| 出力の容量負荷 | GPIO, SO, INT 50 pF | — | max | p4 D101 | "D101 GPIO, SO, INT CIO — — 50 pF" |

### 探したが DS に無かった項目

- **GPIO の VOL / VOH の 3.3 V 条件の値**: 無い（VOL は VDD = 4.5 V のみ、VOH は 4.5 V と 1.8 V のみ）。
- **プルアップ電流の VDD = 3.3 V の値**: 無い（IPU は VDD = 5 V のみ）。なお本文の "100 kΩ" と表の IPU（5 V で 40〜115 µA）は別々に書かれている。
- **POR のしきい値電圧（リセット解除電圧）の数値**: 無い。
- 1 ポート（8 ピン）合計の電流制限: 無い（ピン単位 25 mA と VSS/VDD ピン合計のみ）。

---

## 5. Princeton PT2314E（`Princeton_PT2314E.pdf`、V1.0 January 2010）

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 電源電圧（Electrical Characteristics） | 5 V / 9 V / 10 V | Ta=25℃, VDD=9V, RL=10KΩ, Rg=20Ω, all controls flat, F=1KHz | min / typ / max | Princeton_PT2314E.pdf p12 | "Supply voltage VDD - 5 9 10 V" |
| 電源電圧（Quick Reference Data） | 4 V / 9 V / 10 V | — | min / typ / max | p11 | "Supply voltage VDD 4 9 10 V"（EC 表の min 5 V と食い違い。原文のまま） |
| 電源電圧（Features） | 4 V〜10 V | — | — | p1 | "Wide operation range (VDD=4V to 10V)" |
| 絶対最大 電源電圧 | 10 V | — | max | p11 | "Operating supply voltage VDD - 10 V" |
| 絶対最大 入力電圧 | –0.3 V / VDD+0.3 V | — | min / max | p11 | "Input voltage Vin -0.3 VDD+0.3 V" |
| 消費電流 Is | 30 mA / 40 mA | VDD=9V | typ / max | p12 | "Supply current Is VDD=9V - 30 40 mA" |
| 消費電流 Is | 25 mA / 32 mA | VDD=5V | typ / max | p12 | "VDD=5V - 25 32" |
| 最大入力レベル Vimax | 2.3 Vrms / 2.6 Vrms | All Gain=0dB; THD=1%（VDD=9V） | **min / typ**（max は "-"） | p12 Input Selectors | "Max. input level Vimax All Gain=0dB; THD=1% 2.3 2.6 - Vrms" |
| 最大入力（Quick Reference） | 2.3 / 2.6 Vrms | — | min / typ | p11 | "Max. input signal handling VCL 2.3 2.6 - Vrms" |
| 最大出力レベル VOMAX | 2.3 Vrms / 2.6 Vrms | THD=1%（VDD=9V, RL=10KΩ） | min / typ | p12 Audio Outputs | "Max. output level VOMAX THD=1% 2.3 2.6 - Vrms" |
| 入力抵抗（入力セレクタ） | 35 / 50 / 70 kΩ | Input 1, 2, 3, 4 | min / typ / max | p12 | "Input resistance RIN Input 1, 2, 3, 4 35 50 70 KΩ" |
| 入力抵抗（音量） | 13 / 20 / 27 kΩ | VOL=0dB | min / typ / max | p12 | "Input resistance RIN VOL=0dB 13 20 27 KΩ" |
| 最小負荷（入力セレクタ出力 LOUT/ROUT） | 5 kΩ | Vo=2Vrms, LOUT, ROUT | min | p12 | "Minimum load RL Vo=2Vrms, LOUT, ROUT 5 - - KΩ" |
| 最小負荷（オーディオ出力） | 5 kΩ | — | min | p12 Audio Outputs | "Minimum load RL - 5 - - KΩ" |
| 出力 DC レベル | 0.49 / 0.5 / 0.51 VDD | — | min / typ / max | p12 | "DC voltage level VOUT - 0.49 0.5 0.51 VDD" |
| DC オフセット（入力セレクタ） | 3 mV / 10 mV | 0dB to +11.25dB | typ / max（min 空欄） | p12 Input Selectors | "DC offset VDCO 0dB to +11.25dB 3 10 mV" |
| DC オフセット（スピーカアッテネータ） | 5 mV / 10 mV | 0dB to MUTE | typ / max | p12 Speaker Attenuators | "DC offset VDCO 0dB to MUTE - 5 10 mV" |
| THD | 0.03 % / 0.07 % | All Gain=0, Vin=1Vrms | typ / max | p12 General | "Distortion THD All Gain=0, Vin=1Vrms - 0.03 0.07 %" |
| THD | 0.01 % / 0.03 % | All Gain=0, "Vin=100Vrms"（原文のまま） | typ / max | p12 General | "All Gain=0, Vin=100Vrms - 0.01 0.03" |
| S/N | 100 dBV | All Gain=0dB, A-weighted | typ | p12 | "Signal to noise ratio SNR All Gain=0dB, A-weighted - 100 - dBV" |
| S/N（ミュート時） | 100 dBV | All Gains=0dB, Muted | typ | p12 | "All Gains=0dB, Muted - 100 -" |
| 残留雑音（グラフ "Residual Noise"、**画像で目読み**） | VDD = 9 V で A-weighted 約 7 µV、20–20KHz 約 9 µV、80KHz LPF 約 12 µV | 横軸 Supply Voltage 3〜12 V。その他の条件はグラフに記載なし | グラフ | p14 "Residual Noise" | 凡例 "80KHz LPF" / "20-20KHz" / "A-weighted"、縦軸 "Output Noise (uV)" |
| チャンネル分離 | 90 / 100 dB | L to R or R to L channel | min / typ | p12 | "Channel separation Cs L to R or R to L channel 90 100 - dB" |
| 入力分離 | 90 / 100 dB | F=20~20KHz | min / typ | p12 | "Input separation ISIN F=20~20KHz 90 100 - dB" |
| リップル除去 | 75 dB | CREF=22µF, F=100Hz | typ | p12 | "Ripple rejection PSRR CREF=22µF, F=100Hz - 75 - dB" |
| ミュート減衰 | 100 dB | — | typ | p12 | "Output mute attenuation AMUTE - - 100 - dB" |
| I2C VIL / VIH | 1 V（max）/ 3 V（min） | VDD=9V | max / min | p12 I2C Bus | "Input low voltage VIL VDD=9V - - 1 V" / "Input high voltage VIH VDD=9V 3 - - V" |
| I2C データレート | 3.3 V MCU レベル: VDD 4〜7 V で Fast、8〜9 V で Standard、10 V 不可 | 設計保証のみ | 表 | p7 DATA RATE | "3.3V F F F F S S x"（列 "4V 5V 6V 7V 8V 9V 10V"）/ "Data rate specification is design guarantee only, not fully tested in every combination." |
| I2C 初期化時間 | 電源投入後 I2C アクセス禁止期間あり、Td 推奨 50 ms | CREF 依存 | — | p7 I2C BUS INITIAL TIME | "each time the supply voltage applied to chip it needs an initial time to reset all of the internal decoder register, in this period access the I2C bus is prohibited." / "recommended Td timing shown on next page is 50mS." |
| チップアドレス | 88H | — | — | p6 | "The PT2314E chip address is 88H" |
| 最大出力 vs 負荷（グラフ、**画像で目読み**） | 負荷約 3.5 kΩ 以上で約 2.85 V で頭打ち、1 kΩ で約 1.25 V | VDD の記載なし | グラフ | p14 "Maximum Output Level VS RLOAD" | 縦軸 "Output voltage (V)"、横軸 "Load (Kohm)" |

### 探したが DS に無かった項目

- **最大入力レベルの max 値**: "-"（無い）。min 2.3 / typ 2.6 Vrms は VDD = 9 V（表の共通条件）。**VDD = 9 V 以外での表値は無い**（p14 の "Maximum Output Level (RL=100KΩ)" グラフのみ。縦軸は "V" で rms/peak の明記なし）。
- **残留雑音の表値**（µV）: 表には無い。グラフ（p14）のみで、ゲイン設定などの条件はグラフに書かれていない。
- **出力 DC オフセット（出力 OUT_L/OUT_R の対 REF オフセット）の独立した項目**: 無い。あるのは入力セレクタ段とスピーカアッテネータ段の "DC offset VDCO"。
- **S/N の測定帯域・基準レベルの詳細**: "A-weighted" 以外無い。
- 入力 "Vin=100Vrms" は原文のまま（DS 上の記載）。

---

## 6. TI PCM1804（`TI_PCM1804.pdf`、SLES022C – DECEMBER 2001 – REVISED OCTOBER 2007）／ 共立 ADC1804_F モジュール

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| VCC（アナログ）推奨 | 4.75 / 5 / 5.25 V | — | min / nom / max | TI_PCM1804.pdf p5 RECOMMENDED OPERATING CONDITIONS | "Analog supply voltage, VCC 4.75 5 5.25 V" |
| VDD（デジタル）推奨 | 3 / 3.3 / 3.6 V | — | min / nom / max | p5 | "Digital supply voltage, VDD 3 3.3 3.6 V" |
| 電源電圧範囲（EC 表） | VCC 4.75 / 5 / 5.25 V、VDD 3 / 3.3 / 3.6 V | — | min / typ / max | p8 POWER SUPPLY REQUIREMENTS | "VCC 4.75 5 5.25 Supply voltage range Vdc VDD 3 3.3 3.6" |
| 絶対最大 VCC / VDD | –0.3〜6.5 V / –0.3〜4 V | — | 定格値 | p5 ABSOLUTE MAXIMUM RATINGS | "VCC –0.3 V to 6.5 V Supply voltage VDD –0.3 V to 4 V" |
| 絶対最大 電源差 | VCC – VDD < 3 V | — | 定格値 | p5 | "Supply voltage difference VCC, VDD VCC – VDD < 3 V" |
| ICC（アナログ） | 35 mA / 45 mA | VCC = 5 V、注 (9)(10)(11)＝シングル/デュアル/クアッドレート共通の 1 行 | typ / max | p8 | "ICC VCC = 5 V (9) (10) (11) 35 45" |
| IDD（デジタル） | 15 mA / 20 mA | VDD = 3.3 V、(9) シングルレート fS = 48 kHz、(12) DATA/DSDR 最小負荷 | typ / max | p8 | "IDD VDD = 3.3 V (9) (12) 15 20" |
| IDD（デジタル） | 27 mA | VDD = 3.3 V、(10) デュアルレート fS = 96 kHz、(12) | typ（max 空欄） | p8 | "VDD = 3.3 V (10) (12) 27" |
| IDD（デジタル） | 18 mA | VDD = 3.3 V、(11) クアッドレート fS = 192 kHz、(12) | typ（max 空欄） | p8 | "VDD = 3.3 V (11) (12) 18" |
| 注の定義 | (9) Single rate, fS = 48 kHz / (10) Dual rate, fS = 96 kHz / (11) Quad rate, fS = 192 kHz / (12) Minimum load on DATA/DSDR (pin 15) | — | — | p8 | 同左 |
| 表の共通条件 | TA = 25°C, VCC = 5 V, VDD = 3.3 V, master mode, single-speed mode, fS = 48 kHz, system clock = 256 fS, 24-bit data | — | — | p8 | "All specifications at TA = 25°C, VCC = 5 V, VDD = 3.3 V, master mode, single-speed mode, fS = 48 kHz, system clock = 256 fS, 24-bit data, unless otherwise noted." |
| PD（動作） | 225 mW / 290 mW（シングル）、265 mW（デュアル）、235 mW（クアッド） | VCC = 5 V, VDD = 3.3 V | typ / max（デュアル・クアッドは typ のみ） | p8 | "Operation, VCC = 5 V, VDD = 3.3 V (9) (12) 225 290" / "(10) (12) 265" / "(11) (12) 235" |
| PD（パワーダウン） | 5 mW | VCC = 5 V, VDD = 3.3 V | typ | p8 | "Power down, VCC = 5 V, VDD = 3.3 V 5" |
| 動作温度 | –10 / 70 °C | — | min / max | p8 | "Operation temperature –10 70 °C" |
| 内部 POR | VDD > 2 V (typ) かつ VCC > 4 V (typ) で自動初期化。RST は内部プルダウン | — | typ | p18 POWER-ON AND RESET FUNCTIONS | "initialization (reset) is performed automatically at the time when the power supply VDD exceeds 2 V (typical) and VCC exceeds 4 V (typical)." / "Because an internal pulldown resistor terminates RST, no connection of RST is equivalent to a low-level input." |
| POR とクロック | 電源投入と同時にシステムクロックが必要（VDD>2 V, VCC>4 V, RST=H より前に 3 クロック以上） | — | — | p18 | "the system clock must be supplied as soon as power is supplied; more specifically, at least three system clocks are required prior to VDD > 2 V, VCC > 4 V, and RST = high." |
| 電源のバイパス | 0.1 µF セラミック＋10 µF タンタルをピン近くに。電源は共通 1 系統を推奨 | — | — | p29 BOARD DESIGN AND LAYOUT CONSIDERATIONS | "should be bypassed to the corresponding ground pins with 0.1-μF ceramic and 10-μF tantalum capacitors placed as close to the pins as possible" / "using one common power supply is recommended to avoid unexpected power-supply trouble like latch-up or power-supply sequence." |
| DS 内の記載の食い違い（事実として） | 代表特性曲線の見出しが "VCC = 3.3 V, VDD = 5 V" となっている（推奨条件と逆）。p15 の見出しは "VCC = 5 V, VDD = 3.3 V" で推奨条件と同じ向き | — | — | p9〜12 の TYPICAL PERFORMANCE CURVES（SINGLE / DUAL / QUAD / DSD の各見出し）。p15 | "All specifications at TA = 25°C, VCC = 3.3 V, VDD = 5 V, master mode, fS = 48 kHz, system clock = 256 fS, 24-bit data"（p11 下段・p12 は fS の句が無い短い形） 〔2026-09-25 照合で訂正〕 |
| ADC1804_F モジュールの電源 | 3.3 V・5 V（2 電源） | — | — | 共立 デジット製品ページ https://digit.kyohritsu.com/PRODUCT/ADC1804_F.html（2026-09-25 取得） | "電源電圧：3.3V・5V（2電源）" |
| ADC1804_F 組立説明書 | 電源は +3.3 V と +5 V の 2 電源 | — | — | http://www.kyohritsu.jp/eclib/DIGIT/KIT/adc1804f.pdf（ADC_1804_F_160802）p1 | "電源は+3.3Vと+5Vの2電源です。" / "電源 :+3.3V、+5V(2電源)" |

### 探したが DS に無かった項目

- **ICC のレート別の値・max 以外の温度条件**: ICC は全レート共通の 1 行（typ 35 / max 45 mA）のみ。
- **IDD のデュアル／クアッドレートの max**: 空欄。
- **ADC1804_F モジュールとしての消費電流**（オンボード部品を含む値）: 製品ページ・組立説明書（10 ページ）とも記載無し。説明書は PDF のみ参照（リポジトリには保存していない）。
- PCM1804 のスレーブモード時の電源電流: 別項目は無い（表は master mode 条件）。

---

## 7. Abracon ASFL1（`Abracon_ASFL1.pdf`、2 ページ、Revised: 04.13.11）

取得元: https://abracon.com/Oscillators/ASFL1.pdf（2026-09-25 取得、SHA-256 `1ea3fb87c7a018d96a49ef20f9d355191db8df35c609831bdf0d3a6808f1956b`）。12.288 MHz は "0.321MHz ~ 29.9MHz" の区分に入る。

| 項目 | 値 | 条件 | 列（min/typ/max） | 出典（ファイル名・ページ） | 原文の引用（そのまま） |
|---|---|---|---|---|---|
| 入力電流（消費電流） | 8 mA / 15 mA | 0.321MHz ~ 29.9MHz | typ / max（min "-----"） | Abracon_ASFL1.pdf p1 STANDARD SPECIFICATIONS | "Input Current 0.321MHz ~ 29.9MHz ----- 8 15 mA" |
| 参考: 他の周波数区分 | 20 / 45 mA（30〜79.9 MHz）、28 / 85 mA（80〜133.33 MHz） | — | typ / max | p1 | "30MHz ~ 79.9MHz ----- 20 45" / "80MHz ~ 133.33MHz ----- 28 85" |
| 電源電圧 Vdd | 2.97 / 3.3 / 3.63 V | — | min / typ / max | p1 | "Supply Voltage (Vdd) 2.97 3.3 3.63 V" |
| 出力負荷 | 15 pF または 5 TTL | — | max | p1 | "Output Load ----- ----- 15 pF / ----- ----- 5 TTL" |
| VOH / VOL | 0.9*Vdd（min）/ 0.1*Vdd（max） | — | min / max | p1 | "Output Voltage VOH 0.9*Vdd" / "VOL 0.1*Vdd" |
| 立ち上がり/立ち下がり | 5 / 10 ns | 0.321MHz ~ 29.9MHz | typ / max | p1 | "Rise and Fall Time (Tr/Tf) 0.321MHz ~ 29.9MHz ----- 5 10 ns" |
| デューティ | 40 / 50 / 60 % | @ 1/2Vdd（S オプションで 45/55 %） | min / typ / max | p1 | "Symmetry (@ 1/2Vdd) 40 50 60 % See options" |
| トライステート | "1" または Open: 発振、"0": 出力ディセーブル（Hi-Z）。VIH ≥ 0.7*Vdd、VIL ≤ 0.3*Vdd | — | min / max | p1 | "Tri-state Function VIH 0.7*Vdd ... "1" or Open: Oscillation" / "VIL ... 0.3*Vdd ... "0": Ouput disable (Hi Z)" |
| ディセーブル電流 | 10 µA | — | max | p1 | "Disable Current 10 µA" |
| 起動時間 | 1 / 10 ms | 0.321MHz ~ 29.9MHz | typ / max | p1 | "Start-up Time 0.321MHz ~ 29.9MHz ----- 1 10 ms" |
| 位相ジッタ RMS | 1 ps | 12kHz to 20MHz | max（"Reference only."） | p1 | "Phase Jitter RMS (12kHz to 20MHz) ----- ----- 1 ps Reference only. Please contact Abracon for specific frequencies" |
| 周波数安定度 | –100 / +100 ppm（標準、オプションあり） | — | min / max | p1 | "Overall Frequency Stability -100 ----- +100 ppm See options" |
| 動作温度 | –10 / +70 °C（標準、オプションあり） | — | min / max | p1 | "Operating Temperature -10 ----- +70 °C See options" |
| バイパスコンデンサ | 約 0.01 µF を PIN 2（GND）–4（Vdd）間に推奨 | — | — | p2 OUTLINE DRAWING | "Note: Recommend using an approximately 0.01uF bypass capacitor between PIN 2 and 4." |
| ピン配置 | 1 Tri-State、2 GND、3 Output、4 Vdd | — | — | p2 | "1 Tri-State / 2 GND / 3 Output / 4 Vdd" |

### 探したが DS に無かった項目

- **入力電流の測定条件**（負荷容量・Vdd・温度）: 無い。周波数区分ごとの typ / max のみ。
- **12.288 MHz 固有の値**: 無い（区分値のみ）。
- 位相雑音（dBc/Hz）: 無い。
