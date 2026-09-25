# 境界スイッチ候補 — データシートの事実

2026-09-25 収集。値は DS の原文で裏が取れたものだけ。設計判断は書かない（どれが使えるか・足りるかは書かない）。

- 出典のページは **PDF のページ番号**。印刷ページ番号と違う DS は、その部品の見出しに対応を書いた。
- 「列」はその値が表のどの列に印刷されているか。表に min/typ/max の列が無いものは「値の列のみ」と書き、値に付いた `typ.` `max.` などの字句はそのまま残した。空欄の列は書かない（typ 列が空なら typ は DS に無い）。
- 「画像で確認」は、`pdftoppm`（Panasonic TQ だけは PyMuPDF。理由は §3.3）でページを画像にし、表の罫線と列見出しを目で確かめたもの。
- 「目読み」はグラフの値。ページを 100〜300 dpi の画像にして格子線から目で読んだ（`power.md` のような画素較正はしていない）。精度は目盛り 1/5 程度で、数値保証ではない。
- 「計算」は DS の数値どうしの四則演算。**DS 自身には書かれていない**ことを示すために付けた。
- 「DS に無い」は、本文・表・注・グラフを探して見つからなかったもの。

## 取得した DS（`AudioV2.1/datasheets/boundary/`）

| ファイル | 版（DS の表記） | 取得元 | 備考 |
|---|---|---|---|
| `TI_TMUX4821.pdf` | SCDS487A – OCTOBER 2025 – REVISED DECEMBER 2025（37 p） | https://www.ti.com/lit/ds/symlink/tmux4821.pdf | TMUX4819 と同一文書（`tmux4819.pdf` はバイト一致だったので置かない） |
| `TI_TMUX7412F.pdf` | SCDS404B – MARCH 2021 – REVISED NOVEMBER 2022（48 p） | https://www.ti.com/lit/ds/symlink/tmux7412f.pdf | TMUX7411F / 7413F と同一文書 |
| `TI_TMUX7462F.pdf` | SCDS394B – MARCH 2021 – REVISED JUNE 2023（43 p） | https://www.ti.com/lit/ds/symlink/tmux7462f.pdf | |
| `ADI_ADG5412F_5413F.pdf` | Rev. B（改版履歴の最終 "1/16—Rev. A to Rev. B"、28 p） | ミラー https://datasheet4u.com/pdf/1100881/ADG5412F.pdf | analog.com は不通（HTTP/2 stream INTERNAL_ERROR、Farnell も空応答）。PDF は PDFium で作り直されたもの（Creator: PDFium）。**analog.com 上の最新版がこれかは未確認** |
| `ADI_ADG5412BF_5413BF.pdf` | Rev. B（"1/16—Rev. A to Rev. B"、28 p） | ミラー https://datasheet4u.com/pdf/991256/ADG5412BF.pdf | 同上 |
| `Vishay_DG458_DG459.pdf` | Document Number: 70064, S11-1029–Rev. H, 23-May-11（10 p） | https://www.vishay.com/docs/70064/dg458.pdf | |
| `Renesas_HI-546_547_548_549.pdf` | FN3150 Rev 7.00, Jun 15, 2016（25 p） | https://www.renesas.com/en/document/dst/hi-546-hi-547-hi-548-hi-549-datasheet | |
| `Panasonic_AQV252G.pdf` | ASCTB144E 202204（15 p） | https://industry.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_he1a_aqv25_g.pdf | |
| `Toshiba_TLP241A.pdf` | Rev.5.0, 2018-01-30（18 p） | ミラー https://download.mikroe.com/documents/datasheets/TLP241A.pdf | 東芝の `TLP241A_datasheet_en_20230525.pdf` は 403。**手元は旧版（2018）** |
| `Vishay_VO14642A.pdf` | Rev. 1.8, 21-Aug-2023, Document Number: 81646（11 p） | https://www.vishay.com/docs/81646/vo14642a.pdf | 検索結果には Rev. 1.9（2026-01）の記載があったが、vishay.com から落ちたのは 1.8 |
| `Omron_G6K.pdf` | Cat. No. K106-E1-11（10 p） | https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf | |
| `Omron_G5V-2.pdf` | Cat. No. K046-E1-06（4 p） | https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v_2.pdf | |
| `Panasonic_TQ.pdf` | ASCTB14E 202507（22 p、メタデータ "Issued Date: July 10,2025"） | https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_tq.pdf | AES 暗号化 PDF。poppler では文字が描画されない（§3.3） |
| `Fujitsu_FTR-B3.pdf` | "Rev. 03/2002"（Fujitsu Components America、10 p） | ミラー http://www.konkurel.ru/fujitsu/relay/pdfrelay/Signal/ftr-b3.pdf | fujitsu.com は 429、Mouser は HTML。**2002 年版** |

リポジトリに既にあって、この文書でも引いたもの（`AudioV2.1/datasheets/`）: `TI_TMUX7612.pdf`（SCDS466A）、`ADI_MAX14778.pdf`（19-5929; Rev 3; 7/20）、`Panasonic_AQW212EH.pdf`（ASCTB53J 202601、日本語）、`Zettler_AZ850.pdf`（2019-03-26）。

取れなかったもの: **Maxim MAX4533**（"±40V with power off" を謳う fault-protected SPDT。analog.com 不通、alldatasheet 403、datasheet4u に無し）。以下では扱わない。

---

## 1. アナログスイッチ（電源断時の保護・高インピーダンス）

### 1.0 この節で言う「電源断時の規定」の見方

DS ごとに「電源を切ったとき」の書き方が違う。以下の3種類を区別して書いた。

- **(a) 表の項目として漏れ電流を規定**（条件に VDD = 0 V や VDD = VSS = 0 V が入っている）
- **(b) 本文だけで「高インピーダンス」「OFF のまま」と書く**（数値なし）
- **(c) 何も書かない**

どの DS も、**電源断時の漏れ電流の試験条件は「端子に大きな電圧（±15〜±60 V）」**で、この箱の信号振幅（±9 Vpk 程度）で規定したものは無い（例外は DG458 のグラフ）。

### 1.1 TI TMUX7612（既存採用品。`../datasheets/TI_TMUX7612.pdf`、SCDS466A）

電源断時の扱いは **(c)**。事実の本体は [switch_control.md §1](switch_control.md) にある。ここでは電源断に関する部分だけ、テキスト全文を `power-off / powered-off / unpowered / VDD = 0 / floating / back-power / fail-safe / sequenc` で検索し直して確かめた。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 電源断時の漏れ・高インピーダンスの規定 | **DS に無い**（上のキーワードはどれも該当なし。"floating" は N.C. ピンと漏れ測定条件の注だけ） | — | — | 全文検索 | — |
| 電源シーケンス | 任意の順で投入・遮断してよい | — | — | p28 §7.3.5 | "The TMUX7612 supports any power up sequencing. ... any rail can be powered on first. Similarly, when powering down the supply rails can be powered down in any order." |
| 端子のクランプ | Sx/Dx は電源レールへダイオードクランプ | — | — | p4 §5.1 注(3) | "Pins are diode-clamped to the power-supply rails." |
| 絶対最大 VS/VD | VSS–0.5 / VDD+0.5 | — | min / max | p4 §5.1 | "VS or VD Source or drain voltage (Sx, Dx) VSS–0.5 VDD+0.5 V" |

### 1.2 TI TMUX4821（1:1 × 2 ch）/ TMUX4819（2:1 × 1 ch）（`TI_TMUX4821.pdf`、SCDS487A）

電源断時の扱いは **(a)**。**単電源 1.8〜5.5 V で ±15 V の信号を通す（"Beyond the Supply"）**。VSS ピンは無い。

#### 構成・電源・信号範囲

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | TMUX4821 = 1:1 (SPST) × 2 ch、TMUX4819 = 2:1 (SPDT) × 1 ch | — | — | p1 | "1:1, single-pole, single-throw (SPST) 2-channel (TMUX4821) and 2:1, single-pole, double-throw (SPDT) 1-channel (TMUX4819)" |
| パッケージ | DSG (SON, 8)、2 mm × 2 mm | — | — | p1 Package Information | "DSG (SON, 8) 2mm × 2mm" |
| 推奨 VDD | 1.8 V / 5.5 V | — | min / max（画像で確認） | p5 §8 | "VDD Positive power supply voltage 1.8 5.5 V" |
| 推奨 VS/VD（信号） | −15 V / 15 V | — | min / max | p5 §8 | "VS or VD Signal path input/output voltage (source or drain pin) (Sx, D) -15 15 V" |
| 推奨 VSEL | 0 V / 5.5 V | — | min / max | p5 §8 | "VSEL Address/Select pin voltage 0 5.5 V" |
| 絶対最大 VDD | −0.5 V / 6 V | — | min / max | p3 §5 | "VDD to GND Supply voltage -0.5 6 V" |
| 絶対最大 VS/VD 対 GND | −17 V / 17 V | — | min / max | p3 §5 | "Source or drain voltage (Sx, Dx) to ground -17 17 V" |
| 絶対最大 同一 ch の S–D 間 | −18 V / 18 V | 注(4): 同一 ch の source と drain（または source 同士）の間 | min / max | p3 §5 | "Source to drain or source (same channel)(4) -18 18 V" |
| 絶対最大 別 ch 間 | −24 V / 24 V | 注(3) | min / max | p3 §5 | "Source to drain or source (seperate channel)(3) -24 24 V" |
| 絶対最大表の注(3) | 端子は電源レールへダイオードクランプ | — | — | p4 §5 注(3) | "Pins are diode-clamped to the power-supply rails. Over voltage signals must be voltage and current limited to maximum ratings." |
| 連続電流 IDC | 1.1 A（25°C）/ 0.87 A（85°C）/ 0.27 A（125°C） | VDD = 3.3 V | 表（温度別の列） | p5 §9 | "DSG 1.1 0.87 0.27 A" |

#### 電源断時（VDD = 0 V）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| **IS(POFF) 電源断時の source 漏れ** | **0.02 µA（25°C）**、±0.1 µA（−40〜+85°C）、±2 µA（−40〜+125°C） | **VDD = 0 V、VS = ±15 V / 0 V、VD = 0 V / ±15 V**（注(1): 片方に電圧、他方 0 V） | 25°C は **typ のみ**、温度範囲行は min / max（画像で確認） | p6 §11 | "IS(POFF) Source powered-off leakage current(1) VDD = 0 V VS = ±15 V / 0 V VD = 0 V / ± 15 V 25°C 0.02 ... –40°C to +85°C -0.1 0.1 ... –40°C to +125°C -2 2 uA" |
| **ID(POFF) 電源断時の drain 漏れ** | **0.02 µA（25°C）**、±0.1 µA（−40〜+85°C）、±2 µA（−40〜+125°C） | 同上 | 同上（画像で確認） | p6 §11 | "ID(POFF) Drain powered-off leakage current(1) VDD = 0 V ..." |
| 真理値（VDD = 0） | 全 ch OFF（Hi-Z）、"power-off protection" 状態 | VDD = 0、SELx = X | — | p21 Table 15-1 / 15-2 | "0 X(1) All channels are off (Hi-Z). Device is in power-off protection." |
| 本文 | 電源が無い（VDD = 0 V）とき ±15 V まで高インピーダンスで S/D を切り離す | — | — | p22 §15.3.3 | "The TMUX48xx has powered-off protection up to ±15V on the switch path. This keeps the switch in a high impedance mode and isolates the source (Sx) and drain (Dx) pins when the supply is removed (Vdd = 0V)." |
| 本文（保護が無い場合の説明） | 保護が無いと端子電圧が内部 ESD ダイオード経由で電源レールを逆給電しうる | — | — | p1 §3 | "Without this protection feature, any voltage on the switch can back-power the supply rail through an internal ESD diode and cause potential damage to the rest of the system." |
| 論理入力のフェイルセーフ | VDD = 0 V のまま SEL を 5.5 V まで上げてよい。負側は保護なし | — | — | p22 §15.3.6 | "the Fail-Safe Logic feature allows the logic input pin of the TMUX48xx to be ramped to 5.5V while VDD = 0V. ... does not offer protection against negative overvoltage conditions." |
| 論理ピンのプルダウン | 約 6 MΩ | — | — | p22 §15.3.5 | "The value of this pull-down resistor is approximately 6MΩ." |
| 応用例（本文） | 電源を GPIO で直接駆動して超低消費モードにでき、そのとき入力の高電圧は出力へ伝わらない | — | — | p23 §16.2.1 | "The supply can also be driven directly with a GPIO, allowing the user to put the device into ultra-low power mode. In this mode, the TMUX48xx operates with powered-off protection, so any high voltage present on the inputs will not propagate to the outputs." |

#### 電源投入時の特性（表見出し: "Typical at VDD = 3.3 V TA = 25℃"）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| RON | 0.16 Ω / 0.20 Ω（25°C）、0.225 Ω（−40〜+85°C）、0.3 Ω（−40〜+125°C） | VDD = 2.5〜5.5 V、VS = −15〜+15 V、ID = −100 mA | 25°C は typ / max、温度行は max（画像で確認） | p6 §11 | "RON On-resistance VDD = 2.5 V to 5.5 V VS = –15 V to +15 V ID = –100 mA 25°C 0.16 0.20 ... 0.225 ... 0.3 Ω" |
| RON FLAT | 0.0001 Ω / 0.01 Ω（25°C）、0.05 Ω（−40〜+85°C）、0.07 Ω（−40〜+125°C） | 同上 | 同上（画像で確認） | p6 §11 | "RON FLAT On-resistance flatness ... 25°C 0.0001 0.01 ... 0.05 ... 0.07 Ω" |
| ΔRON | 0.0008 Ω / 0.03 Ω（25°C） | 同上 | typ / max | p6 §11 | "ΔRON ... 25°C 0.0008 0.03 Ω" |
| IS(OFF) | 0.001 µA（25°C）、±0.1 µA（−40〜+85°C）、±1 µA（−40〜+125°C） | スイッチ OFF、VS = ±15 V / 0 V、VD = 0 V / ±15 V | 25°C typ、温度行 min / max | p6 §11 | "IS(OFF) Source off leakage current(1) Switch state is off VS = ±15 V / 0 V VD = 0 V / ±15 V 25°C 0.001 ..." |
| IDD | 55 µA / 125 µA（25°C） | Logic inputs = 0 V, 5 V, or VDD | typ / max | p7 §11 | "IDD VDD supply current Logic inputs = 0 V, 5 V, or VDD 25°C 55 125 µA" |
| **OISO（OFF アイソレーション）** | **−50 dB** | RL = 50 Ω、CL = 5 pF、VS = 200 mVRMS、VBIAS = 0 V、**f = 100 kHz** | typ（画像で確認） | p8 §12 | "OISO Off-isolation RL = 50 Ω , CL = 5 pF VS = 200 mVRMS, VBIAS = 0 V, f = 100 kHz 25°C -50 dB" |
| XTALK | −100 dB（4821）、−55 dB（4819） | 同上、f = 100 kHz | typ | p8 §12 | "Crosstalk - 4821 ... -100" / "Crosstalk - 4819 ... -55" |
| CS(OFF) | 70 pF | VS = 0 V、f = 1 MHz | typ | p8 §12 | "CS(OFF) Source off capacitance VS = 0 V, f = 1 MHz 25°C 70 pF" |
| CS(ON), CD(ON) | 40 pF | 同上 | typ | p8 §12 | "CS(ON), CD(ON) On capacitance VS = 0 V, f = 1 MHz 25°C 40 pF" |
| CD(OFF) | **DS に無い**（表に行が無い） | — | — | p8 §12 | — |
| QINJ | 5 pC | VS = 0 V、CL = 100 pF | typ | p8 §12 | "QINJ Charge injection VS = 0 V, CL = 100 pF 25°C 5 pC" |
| tON / tOFF | 155 µs / 300 µs（tON、25°C）、14 µs（tOFF） | VS = 3.3 V、RL = 50 Ω、CL = 35 pF | tON は typ / max、tOFF は typ | p8 §12 | "tON ... 25°C 155 300 us" / "tOFF ... 25°C 14 us" |
| tON(VDD)（電源投入から出力まで） | 175 µs | VDD rise time = 1 µs、RL = 50 Ω、CL = 35 pF | typ | p8 §12 | "tON (VDD) Device turn on time (VDD to output) VDD rise time = 1 µs ... 175 us" |
| ACPSRR | −100 dB | VPP = 0.62 V on VDD、RL = 32 Ω、CL = 5 pF、f = 20 kHz | typ | p8 §12 | "ACPSRR ... f = 20 kHz 25°C -100 dB" |
| THD+N（表） | −107 dB（25°C）、−105 dB（−40〜+125°C） | **VPP = 0.5 V**、VBIAS = 0 V、RL = 600 Ω、f = 20 Hz〜20 kHz | typ（画像で確認） | p9 §12 | "THD+N ... VPP = 0.5 V, VBIAS = 0 V RL = 600 Ω f = 20 Hz to 20 kHz 25°C -107" |
| THD+N（表） | −102 dB | VPP = 0.5 V、RL = 32 Ω | typ | p9 §12 | "RL = 32 Ω ... -102" |
| THD+N（Features の字句） | 0.001 %（−100 dB） | 条件の記載なし | — | p1 | "Low THD+N: 0.001% (-100dB)" |
| Figure 13-16 THD+N vs Frequency（目読み） | 15 Vpp: 約 −125〜−118 dB、0.5 Vpp: 約 −107 dB（20 Hz〜20 kHz） | VDD = 3.3 V、RLOAD = 600 Ω | グラフ | p12 | 凡例 "0.5Vpp / 15Vpp" |
| Figure 13-18 THD+N vs Peak-to-Peak Voltage（目読み） | 0.5 V で約 0.00058 %、15 V で約 0.00018 % | 1 kHz、32 Ω、VDD = 3.3 V | グラフ | p12 | 凡例 "1kHz, 32 Ω"（横軸ラベルは "Source Voltage (V)"） |
| **Figure 13-21 Maximum Sinusoidal Signal Swing（目読み）** | 横軸 Amplitude (Vpp)、縦軸 "Stopping Frequency (Hz)"。"Recommended Operation Region" の上限: 13 Vpp まで約 1 MHz、15 Vpp で約 40 kHz、17 Vpp で約 19 kHz、**18 Vpp で約 15 kHz**、19 Vpp で約 13 kHz、29 Vpp で約 4.5 kHz。その上に細い ">-100dB Operation Region"、さらに上が "No Operation Region"（18 Vpp で約 16 kHz 以上） | VDD = 5V | グラフ（300 dpi で読んだ。縦軸は対数で読み誤差が大きい） | p13 Figure 13-21 | 凡例 "No Operation Region / >-100dB Operation Region / Recommended Operation Region"、図下 "VDD = 5V" |
| Figure 13-21 の説明文 | **DS に無い**（"Stopping Frequency" の定義も本文に無い） | — | — | 全文検索 | — |

### 1.3 TI TMUX7411F / TMUX7412F / TMUX7413F（1:1 × 4 ch、fault protected）（`TI_TMUX7412F.pdf`、SCDS404B）

電源断時の扱いは **(a)**。ただし表の条件は **VS = ±60 V**。**保護されるのは source (Sx) 側だけ**で、drain (Dx) は電源へ ESD ダイオードがある。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | 1:1 (SPST) × 4 ch。7411F = logic low で ON、7412F = logic high、7413F = 混在 | — | — | p1, p3 Device Comparison Table | "TMUX7412F ±60 V fault-protected, latch-up immune, quad SPST switch (logic high)" |
| パッケージ | PW (TSSOP, 16) 5.00 × 4.40 mm（**DS 上は "Preview package"**）、RRP (WQFN, 16) 4.00 × 4.00 mm | — | — | p1 | "PW (TSSOP, 16) (2) 5.00 mm × 4.40 mm ... RRP (WQFN, 16) 4.00 mm × 4.00 mm" / "(2) Preview package." |
| 電源範囲（Features） | 単電源 8〜44 V、両電源 ±5〜±22 V | — | — | p1 | "Single supply: 8 V to 44 V – Dual supply: ±5 V to ±22 V" |
| 推奨 VDD – VSS | 8 V / 44 V | — | min / max | p5 §7.4 | "VDD – VSS (1) Power supply voltage differential 8 44" |
| 推奨 VS（非 fault 時） | VSS / VDD | — | min / max | p5 §7.4 | "VS Source pin (Sx) voltage (non-fault condition) VSS VDD" |
| 推奨 VS（fault 時） | −60 V / 60 V（対 GND） | — | min / max | p5 §7.4 | "VS to GND Source pin (Sx) voltage to GND (fault condition) –60 60" |
| **推奨 VD（drain）** | **VSS / VDD** | — | min / max | p5 §7.4 | "VD Drain pin (Dx) voltage VSS VDD" |
| 絶対最大 VS 対 GND | −65 V / 65 V | — | min / max | p4 §7.1 | "VS to GND Source input pin (Sx) voltage to GND –65 65 V" |
| **絶対最大 VD** | **VSS−0.7 V / VDD+0.7 V** | — | min / max | p4 §7.1 | "VD Drain pin (Dx) voltage VSS–0.7 VDD+0.7 V" |
| 連続電流 IDC（WQFN） | 150 mA（25°C）/ 100 mA（85°C）/ 60 mA（125°C） | — | max | p5 §7.4 | "IDC Continuous current through switch, WQFN package TA = 25°C 150 ... TA = 85°C 100 ... TA = 125°C 60 mA" |
| fault 検出しきい値 VT | 0.7 V | 25°C | typ | p6 §7.5 | "VT Threshold voltage for fault detector 25°C 0.7 V" |
| UVLO（VDD – VSS） | 立ち上がり 5.1 / 5.8 / 6.4 V、立ち下がり 5 / 5.7 / 6.3 V | 単電源 | min / typ / max | p6 §7.5 | "Rising edge, single supply –40°C to +125°C 5.1 5.8 6.4 V ... Falling edge ... 5 5.7 6.3 V" |

#### 電源断時（±15 V 表 §7.6。表見出し "VDD = +15 V ± 10%, VSS = –15 V ±10%"。以下の行は条件で電源を 0 V／浮きに上書きしている）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| **IS(FA) Grounded（電源 0 V 時の source 漏れ）** | **±125 µA** | **VS = ±60 V、GND = 0 V、VDD = VSS = 0 V**、−40〜+125°C | **typ**（画像で確認） | p7 §7.6 | "IS(FA) Grounded Input leakage current during overvoltage with grounded supply voltages VS = ± 60 V, GND = 0 V VDD = VSS = 0 V –40°C to +125°C ±125 µA" |
| IS(FA) Floating（電源浮き時） | ±125 µA | VS = ±60 V、VDD = VSS = floating | typ（画像で確認） | p7 §7.6 | "IS(FA) Floating ... VDD = VSS = floating ... ±125 µA" |
| IS(FA)（電源あり・過電圧） | ±100 µA | VS = ±60 V、VDD = 16.5 V、VSS = −16.5 V | typ | p7 §7.6 | "IS(FA) Input leakage current durring overvoltage VS = ± 60 V, GND = 0 V, VDD = 16.5 V, VSS = –16.5 V ... ±100 µA" |
| **ID(FA) Grounded（電源 0 V 時の drain 漏れ）** | **±0.01 nA typ、±30 nA max（25°C）**、±50 nA（−40〜+85°C）、±90 nA（−40〜+125°C） | VS = ±60 V、GND = 0 V、VDD = VSS = 0 V | 25°C は min / typ / max、温度行は min / max（画像で確認） | p7 §7.6 | "ID(FA) Grounded Output leakage current during overvoltage with grounded supply voltages VS = ± 60 V, GND = 0 V, VDD = VSS = 0 V 25°C –30 ±0.01 30 ... –50 50 ... –90 90 nA" |
| ID(FA) Floating | ±2 µA（25°C）、±3 µA（85°C）、±4 µA（125°C） | VS = ±60 V、VDD = VSS = floating | typ（画像で確認） | p7 §7.6 | "ID(FA) Floating ... ±2 ... ±3 ... ±4 µA" |
| 電源断・VS = ±9〜±15 V 程度での漏れ | **DS に無い**（表は VS = ±60 V だけ） | — | — | — | — |
| Figure 7-23 IS(FA) vs Temperature（目読み、**電源 ±15 V あり**） | VS = +30 V: 約 +27 µA、−30 V: 約 −33〜−38 µA、+60 V: 約 +78〜+88 µA、−60 V: 約 −85〜−100 µA（−40〜+120°C） | ±15 V Dual Supply | グラフ | p20 Figure 7-23 | 凡例 "VS = -30 V / VS = 30 V / VS = -60 V / VS = 60 V" |
| 本文（Powered-Off Protection） | 電源を外す（VDD/VSS = 0 V または浮き）と source ピンは Hi-Z、漏れ規定内。GND 基準は常に必要。±60 V まで遮断 | — | — | p33 §9.3.2.2 | "When the supplies ... are removed (VDD/ VSS = 0 V or floating), the source (Sx) pins of the device remain in high impedance (Hi-Z) state, and the device performance remains within the leakage performance. ... A GND reference must always be present to ensure proper operation. Source and drain voltage levels of up to ±60 V are blocked in the powered-off condition." |
| 本文（ESD 保護） | **drain ピンは電源への ESD ダイオードがあり、電源電圧を超えてはならない**。source ピンは電源に依らず ±60 V まで可 | — | — | p33 §9.3.2.5 | "The drain pins (Dx) have internal ESD protection diodes to the supplies VDD and VSS, therefore the voltage at the drain pins must not exceed the supply voltages to prevent excessive diode current. The source pins have specialized ESD protection that allows the signal voltage to reach ±60 V regardless of the supply voltage level." |
| DS 内の食い違い | §9.3.2.2 は "Source and drain voltage levels of up to ±60 V are blocked in the powered-off condition" と書くが、§9.3.2.5 と絶対最大（VD = VSS−0.7〜VDD+0.7）は drain が電源を超えられないとする。原文のまま両方を記録 | — | — | p33 / p4 | 上の2行 |
| 電源なし時の論理 | 電源が無いと ch は OFF、論理入力は無視 | — | — | p1 §3 | "When no power supplies are present, the switch channels remain in the OFF state regardless of the switch input conditions, and any control signal present on the logic pins is ignored." |
| フェイルセーフ論理 | 電源断時に論理入力は +44 V まで。負側は保護なし | — | — | p33 §9.3.2.3 | "The logic inputs are protected against positive faults of up to +44 V in powered-off condition, but do not offer protection against negative overvoltage condition." |

#### 電源投入時の特性（±15 V 表 §7.6）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| RON | 8.3 Ω / 11 Ω（25°C）、14 Ω（−40〜+85°C）、16.5 Ω（−40〜+125°C） | VS = −10〜+10 V、ID = −10 mA | 25°C typ / max、温度行 max（画像で確認） | p7 §7.6 | "RON On-resistance VS = –10 V to +10 V ID = –10 mA 25°C 8.3 11 ... 14 ... 16.5" |
| RFLAT | 0.01 Ω / 0.4 Ω（25°C）、0.4 Ω（温度行） | 同上 | typ / max（画像で確認） | p7 §7.6 | "RFLAT On-resistance flatness ... 25°C 0.01 0.4 ... 0.4 ... 0.4" |
| IS(OFF) / ID(OFF) | 0.03 nA typ、±0.7 nA max（25°C）、±2 nA（85°C）、±10 / ±12 nA（125°C） | VDD = 16.5 V、VSS = −16.5 V、OFF、VS = +10 / −10 V、VD = −10 / +10 V | min / typ / max（画像で確認） | p7 §7.6 | "IS(OFF) ... 25°C –0.7 0.03 0.7 ... –2 2 ... –10 10 nA" |
| THD+N | 0.0006 % | RS = 50 Ω、RL = 10 kΩ、**VS = 15 VPP**、VBIAS = 0 V、f = 20 Hz〜20 kHz | typ | p8 §7.6 | "THD+N ... RS = 50 Ω, RL = 10 kΩ, VS = 15 VPP, VBIAS = 0 V, f = 20 Hz to 20 kHz 25°C 0.0006 %" |
| OISO | −60 dB | RS = RL = 50 Ω、CL = 5 pF、VS = 200 mVRMS、**f = 1 MHz** | typ | p8 §7.6 | "OISO Off-isolation ... f = 1 MHz 25°C –60 dB" |
| Figure 7-29 Off Isolation vs Frequency（目読み） | 100 kHz 付近で約 −80〜−90 dB（グラフの下端が 100 kHz） | ページ見出し "at TA = 25°C, VDD = 15 V, and VSS = –15 V" | グラフ | p21 Figure 7-29 | 図題 "Crosstalk and Off Isolation vs Frequency" |
| XTALK | −100 dB | 同上、f = 1 MHz | typ | p8 §7.6 | "XTALK Crosstalk ... f = 1 MHz 25°C –100 dB" |
| CS(OFF) / CD(OFF) / CS(ON),CD(ON) | 10 / 12 / 14 pF | f = 1 MHz、VS = 0 V | typ | p8 §7.6 | "CS(OFF) Input off-capacitance ... 10 pF" / "CD(OFF) Output off-capacitance ... 12 pF" / "Input/Output on-capacitance ... 14 pF" |
| QJ | −300 pC | VS = 0 V、CL = 1 nF | typ | p8 §7.6 | "QJ Charge injection VS = 0 V, CL = 1 nF 25°C –300 pC" |
| tON / tOFF | 480 / 680 ns、50 / 100 ns（25°C） | VS = 10 V、RL = 300 Ω、CL = 12 pF | typ / max | p8 §7.6 | "tON ... 25°C 480 680" / "tOFF ... 25°C 50 100" |
| IDD / ISS | 0.32 / 0.5 mA、0.26 / 0.4 mA（25°C） | VDD = 16.5 V、VSS = −16.5 V | typ / max | p8 §7.6 | "IDD ... 25°C 0.32 0.5" / "ISS ... 25°C 0.26 0.4" |

### 1.4 TI TMUX7462F（4 ch プロテクタ、選択ピンなし）（`TI_TMUX7462F.pdf`、SCDS394B）

電源断時の扱いは **(a)**（条件 VS = ±60 V）。**ch ごとの選択ピンが無い**。電源が正常で信号が範囲内なら ON、fault か電源断なら OFF。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | 4 ch プロテクタ、ch ごとの選択ピン不要 | — | — | p1 | "Channel protector without need for dedicated select pin per channel" |
| パッケージ | PW (TSSOP, 16) 5 × 6.4 mm、RRP (WQFN, 16) 4 × 4 mm | — | — | p1 | "PW (TSSOP, 16) 5 mm × 6.4 mm ... RRP (WQFN, 16) 4 mm × 4 mm" |
| ON の条件（本文） | VDD – VSS ≥ 8 V、VFP = 3 V〜VDD・VFN = VSS〜0 V、信号が VFP+VT〜VFN−VT の間 | — | — | p28 §8.4.1 | "The difference between the primary supplies (VDD – VSS) must be higher or equal to 8 V. • VFP must be between 3 V and VDD, and VFN must be between VSS and 0 V. • The input signals on the source (Sx) or the drain (Dx) must be between VFP+ VT and VFN – VT." |
| 電源断時（本文） | 電源 0 V・浮き・UV しきい値未満で source は Hi-Z | — | — | p26 §8.3.2.2 | "The source (Sx) pins of the device remain in the high impedance (Hi-Z) state ... when the supplies of TMUX7462F are removed (VDD/ VSS = 0 V or floating) or at a level that is below the undervoltage (UV) threshold." |
| **IS(FA) Grounded** | **±135 µA** | VS = ±60 V、VDD = VSS = VFP = VFN = 0 V、−40〜+125°C | typ | p6 §6.6 | "IS(FA) Grounded ... VS = ± 60 V, GND = 0 V, VDD = VSS = VFP = VFN= 0 V –40°C to +125°C ±135 µA" |
| IS(FA) Floating | ±140 µA | 同、floating | typ | p6 §6.6 | "IS(FA) Floating ... ±140 µA" |
| **ID(FA) Grounded** | ±0.01 nA typ、±30 nA max（25°C）、±50 / ±90 nA | VS = ±60 V、電源すべて 0 V | min / typ / max | p6 §6.6 | "ID(FA) Grounded ... 25°C –30 ±0.01 30 ... –50 50 ... –90 90 nA" |
| ID(FA) Floating | ±0.6 / ±1.2 / ±2.2 µA | 電源すべて floating | typ | p6 §6.6 | "ID(FA) Floating ... ±0.6 ... ±1.2 ... ±2.2 µA" |
| drain 側の保護 | **drain は過電圧保護なし**。入力に使うなら常に VFP〜VFN の間 | — | — | p28 §8.4.2 | "The overvoltage protection is provided only for the source (Sx) input pins. The drain (Dx) pin, if used as signal input, must stay in between VFP and VFN at all time since no overvoltage protection is implemented on the drain pin." |
| 絶対最大 VD | VFN−0.7 V / VFP+0.7 V | — | min / max | p4 §6.1 | "VD Drain pin (Dx) voltage VFN–0.7 VFP+0.7 V" |
| RON | 8.3 Ω / 10.7 Ω（25°C）、13.5 / 16 Ω | VS = −10〜+10 V、ID = −10 mA（±15 V 表） | typ / max、温度行 max | p6 §6.6 | "RON ... 25°C 8.3 10.7 ... 13.5 ... 16" |
| RFLAT | 0.005 Ω / 0.4 Ω（25°C） | 同上 | typ / max | p6 §6.6 | "RFLAT ... 25°C 0.005 0.4" |
| THD+N | 0.0006 % | RS = 50 Ω、RL = 10 kΩ、VS = 15 VPP、f = 20 Hz〜20 kHz | typ | p7 §6.6 | "THD+N ... VS = 15 VPP ... 0.0006 %" |
| CS(ON), CD(ON) | 14 pF | f = 1 MHz、VS = 0 V | typ | p7 §6.6 | "Input/Output on-capacitance f = 1 MHz, VS = 0 V 25°C 14 pF" |
| OFF アイソレーション・OFF 容量 | **DS に無い**（±15 V 表に OISO・CS(OFF)・CD(OFF) の行が無い。選択ピンが無いため） | — | — | p6–7 §6.6 | — |
| IDD / ISS | 0.32 / 0.5 mA、0.26 / 0.4 mA（25°C） | VDD = VFP = 16.5 V、VSS = VFN = −16.5 V | typ / max | p7 §6.6 | "IDD ... 25°C 0.32 0.5" / "ISS ... 25°C 0.26 0.4" |

### 1.5 ADI ADG5412F / ADG5413F（4 × SPST、source 側 fault protected）（`ADI_ADG5412F_5413F.pdf`、Rev. B）

電源断時の扱いは **(a)**（条件 VS = ±55 V）。ページは PDF = 印刷（"Rev. B | Page N of 28"）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | 4 × SPST。5412F は Logic 1 で全 ON、5413F は 2 ON / 2 OFF | — | — | p1 | "The ADG5412F has four switches that turn on with Logic 1 inputs. The ADG5413F has two switches that turn on and two switches that turn off with Logic 1 inputs." |
| パッケージ | 16-Lead TSSOP、16-Lead LFCSP | — | — | p12 Table 6 | "16-Lead TSSOP (4-Layer Board) 112.6°C/W / 16-Lead LFCSP (4-Layer Board) 30.4°C/W" |
| 電源範囲 | ±5〜±22 V 両電源、8〜44 V 単電源 | — | — | p1 | "±5 V to ±22 V dual supply operation / 8 V to 44 V single-supply operation" |
| 信号範囲（電源あり） | VDD to VSS | — | −40〜+125°C 列 | p3 Table 1 | "Analog Signal Range VDD to VSS V" |
| 電源断時（Features） | ±55 V まで電源断保護 | — | — | p1 | "Power-off protection up to −55 V and +55 V" |
| **Source Leakage, Power Supplies Grounded or Floating** | **±40 µA** | VDD = 0 V または浮き、VSS = 0 V または浮き、GND = 0 V、INx = 0 V または浮き、**VS = ±55 V** | **"µA typ"、−40〜+125°C の列に印刷**（25°C 列は空、画像で確認） | p3 Table 1 | "Power Supplies Grounded or Floating ±40 µA typ VDD = 0 V or floating, VSS = 0 V or floating, GND = 0 V, INx = 0 V or floating, VS = ±55 V, see Figure 38" |
| Source Leakage, With Overvoltage（電源あり） | ±78 µA | "VDD = 16.5 V, VSS = 16.5 V"（原文のまま。VSS の符号が + で印刷）、VS = ±55 V | "µA typ"、−40〜+125°C 列 | p3 Table 1 | "With Overvoltage ±78 µA typ VDD = 16.5 V, VSS = 16.5 V, GND = 0 V, VS = ±55 V" |
| **Drain Leakage, Power Supplies Grounded** | **±10 nA typ（25°C）、±30 / ±50 / ±100 nA max**（25°C / −40〜+85 / −40〜+125°C） | VDD = VSS = 0 V、GND = 0 V、VS = ±55 V、INx = 0 V | typ 行と max 行（画像で確認） | p3 Table 1 | "Power Supplies Grounded ±10 nA typ ... ±30 ±50 ±100 nA max" |
| Drain Leakage, Power Supplies Floating | ±10 µA typ（3 列とも） | VDD = VSS = floating、VS = ±55 V | "µA typ" | p3 Table 1 | "Power Supplies Floating ±10 ±10 ±10 µA typ" |
| 電源断・VS = ±9〜±15 V 程度での漏れ | **DS に無い** | — | — | — | — |
| 本文（Power-Off Protection） | 電源が無いと OFF、入力は高インピーダンス、出力は仮想開放。VDD/VSS が 0 V でも浮きでも同じ。GND 基準は必要 | — | — | p26 | "When no power supplies are present, the switch remains in the off condition, and the switch inputs are high impedance. ... The switch output is a virtual open circuit. The switch remains off regardless of whether the VDD and VSS supplies are 0 V or floating. A GND reference must always be present to ensure proper operation." |
| 本文（ESD） | **drain ピンは電源への ESD ダイオードあり、電源電圧を超えてはならない** | — | — | p25 | "The drain pins have ESD protection diodes to the rails and the voltage at these pins must not exceed supply voltage." |
| 絶対最大 Dx | VSS − 0.7 V〜VDD + 0.7 V または 30 mA の先に来る方 | 注1: Dx の過電圧は内部ダイオードでクランプ | — | p12 Table 6 | "Dx Pins1 VSS − 0.7 V to VDD + 0.7 V or 30 mA, whichever occurs first" |
| 本文（BF 版の案内） | 5412BF/5413BF は source・drain 両方が過電圧保護のピン互換品 | — | — | p25 | "The ADG5412BF/ADG5413BF are pin-compatible devices that are overvoltage protected on both the source and drain pins." |
| RON | 9.5 Ω typ、10.7 / 13.5 / 16 Ω max | **VS = ±9 V**、IS = −10 mA（ANALOG SWITCH 節の条件 VDD = 13.5 V、VSS = −13.5 V） | typ 行と max 行 | p3 Table 1 | "9.5 Ω typ VS = ±9 V, IS = −10 mA / 10.7 13.5 16 Ω max" |
| RON | 10 Ω typ、11.2 / 14 / 16.5 Ω max | VS = ±10 V、同上 | 同上 | p3 Table 1 | "10 Ω typ VS = ±10 V, IS = −10 mA / 11.2 14 16.5 Ω max" |
| RFLAT(ON) | 0.1 Ω typ、0.4 / 0.5 / 0.5 Ω max | VS = ±9 V | 同上 | p3 Table 1 | "0.1 Ω typ VS = ±9 V ... 0.4 0.5 0.5 Ω max" |
| RFLAT(ON) | 0.6 Ω typ、0.9 / 1.1 / 1.1 Ω max | VS = ±10 V | 同上 | p3 Table 1 | "0.6 Ω typ VS = ±10 V ... 0.9 1.1 1.1 Ω max" |
| IS(Off) / ID(Off) | ±0.1 nA typ、±1.5 / ±5.0 / ±21（ID は ±18）nA max | VDD = 16.5 V、VSS = −16.5 V、VS = ±10 V、VD = ∓10 V | typ / max | p3 Table 1 | "Source Off Leakage ... ±0.1 nA typ ±1.5 ±5.0 ±21 nA max" |
| THD+N | 0.0015 % | RL = 10 kΩ、VS = 15 V p-p、f = 20 Hz〜20 kHz | typ（25°C 列） | p4 Table 1 | "Total Harmonic Distortion Plus Noise, THD + N 0.0015 % typ RL = 10 kΩ, VS = 15 V p-p, f = 20 Hz to 20 kHz" |
| Figure 25 THD+N vs Frequency（目読み） | ±15 V・15 V p-p で 0〜20 kHz 約 0.0015 % | Load = 10 kΩ | グラフ | p17 Figure 25 | 凡例 "VDD = 15V, VSS = −15V, VS = 15V p-p" |
| Off Isolation | −70 dB | RL = 50 Ω、CL = 5 pF、f = 1 MHz | typ | p4 Table 1 | "Off Isolation −70 dB typ RL = 50 Ω, CL = 5 pF, f = 1 MHz" |
| Figure 20 Off Isolation vs Frequency（目読み） | 1〜10 kHz 約 −110 dB（ノイズで揺れる）、100 kHz 約 −100 dB | ±15 V、25°C | グラフ | p16 Figure 20 | 図中 "VDD = +15V VSS = −15V TA = 25°C" |
| CS(Off) / CD(Off) / CD(On),CS(On) | 13 / 12 / 24 pF | VS = 0 V、f = 1 MHz | typ | p4 Table 1 | "CS (Off ) 13 pF typ / CD (Off ) 12 pF typ / CD (On), CS (On) 24 pF typ" |
| QINJ | −680 pC | VS = 0 V、RS = 0 Ω、CL = 1 nF | typ | p4 Table 1 | "Charge Injection, QINJ −680 pC typ" |
| tON / tOFF | 400 / 495 ns、410 / 510 ns（25°C） | RL = 300 Ω、CL = 35 pF、VS = 10 V | typ / max | p4 Table 1 | "tON 400 ns typ 495 ... ns max" |
| IDD / ISS（Normal Mode） | 0.9 / 1.2 mA、0.5 / 0.65 mA（25°C） | VDD = 16.5 V、VSS = −16.5 V | typ / max | p4 Table 1 | "IDD 0.9 mA typ 1.2 ... mA max" / "ISS 0.5 mA typ 0.65 ..." |
| Figure 31 Large Voltage Signal Tracking vs Frequency（目読み） | ±10 V 電源で 1〜約 3 MHz は 20 V p-p まで "DISTORTIONLESS OPERATING REGION"、それ以上で下がる（横軸 1〜100 MHz） | TA = 25°C、VDD = +10 V、VSS = −10 V | グラフ | p18 Figure 31 | 図中 "DISTORTIONLESS OPERATING REGION" |

### 1.6 ADI ADG5412BF / ADG5413BF（4 × SPST、source・drain 両側 fault protected）（`ADI_ADG5412BF_5413BF.pdf`、Rev. B）

ADG5412F との違いだけを書く（RON・RFLAT・THD+N・容量・QINJ・時間・Off Isolation は ±15 V 表で同じ値。p3–4 Table 1 で確認）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 保護対象 | source と drain（"Switch pins"）の両方 | — | — | p1 | "Overvoltage detection on source and drain pins" / "Switch pins are protected against voltages between −55 V and +55 V, in an unpowered state." |
| 絶対最大 Sx and Dx | −55 V〜+55 V | — | — | p12 Table 6 | "Sx and Dx −55 V to +55 V" |
| ESD（All Other Pins） | 3 kV（5412F は 5.5 kV） | HBM | — | p12 Table 6 / p1 | "All Other Pins 3 kV" / "3 kV human body model (HBM) ESD rating" |
| **Input Leakage IS or ID, Power Supplies Grounded or Floating** | **±40 µA** | VDD・VSS = 0 V または浮き、INx = 0 V または浮き、**VS or VD = ±55 V** | "µA typ"、−40〜+125°C 列 | p3 Table 1 | "Power Supplies Grounded or Floating ±40 μA typ VDD = 0 V or floating, VSS = 0 V or floating, GND = 0 V, INx = 0 V or floating, VS or VD = ±55 V" |
| **Output Leakage IS or ID, Power Supplies Grounded** | **±10 nA typ（25°C）、±30 / ±50 / ±100 nA max** | VDD = VSS = 0 V、VS or VD = ±55 V、INx = 0 V | typ 行と max 行（画像で確認） | p3 Table 1 | "Power Supplies Grounded ±10 nA typ ... ±30 ±50 ±100 nA max" |
| Output Leakage, Power Supplies Floating | ±10 µA typ（3 列とも） | VDD = VSS = floating | "µA typ"（画像で確認） | p3 Table 1 | "Power Supplies Floating ±10 ±10 ±10 μA typ" |
| Output Leakage, With Overvoltage（電源あり） | ±20 nA typ、±200 / ±250 / ±250 nA max | "VDD = 16.5 V, VSS = 16.5 V"（原文のまま）、VS or VD = ±55 V | typ / max | p3 Table 1 | "With Overvoltage ±20 nA typ ... ±200 ±250 ±250 nA max" |
| IS(Off) / ID(Off) | ±0.1 nA typ、±1.5 / ±5.5 / ±24（ID は ±20）nA max | VDD = 16.5 V、VSS = −16.5 V、VS = ±10 V、VD = ∓10 V | typ / max | p3 Table 1 | "±1.5 ±5.5 ±24 nA max" |
| 本文（Power-Off Protection） | 5412F と同文 | — | — | p26 | "When no power supplies are present, the switch remains in the off condition, and the switch inputs are high impedance." |
| ISS max の単位（原文のまま） | "0.7 μA max"（同じ行の typ は mA。5412F は "0.7 mA max"） | Normal Mode | — | p4 Table 1 | "ISS 0.5 mA typ 0.65 0.7 μA max" |

### 1.7 Vishay DG458 / DG459（fault protected 8:1 / 差動 4:1 マルチプレクサ）（`Vishay_DG458_DG459.pdf`、Rev. H）

電源断時の扱いは **(a)**（条件 VS = ±25 V）＋**電源断時の入力漏れのグラフあり**。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | DG458 = シングルエンド 8 ch、DG459 = 差動 4 ch。各 ch は n-p-n 直列 MOSFET | — | — | p1 | "8-channel single-ended and 4-channel differential analog multiplexers ... A series n-p-n MOSFET structure provides device and signal-source protection in the event of power loss or overvoltages." |
| 注文型番のパッケージ | 16-pin Plastic DIP（DG458DJ / DG459DJ、−40〜85°C） | — | — | p2 ORDERING INFORMATION | "- 40 to 85 °C 16-pin Plastic DIP DG458DJ DG458DJ-E3" |
| 電源範囲（連続動作） | ±4.5 V / ±18 V | Room | min / max | p4 | "Power Supply Range for Continuous Operation Room ± 4.5 ± 18 V" |
| 信号範囲 | −10 V / 10 V | V+ = 15 V、V− = −15 V、Full | min / max（A・D とも、画像で確認） | p3 | "Analog Signal Range VANALOG Full - 10 10 - 10 10 V" |
| 絶対最大 電源断時の入力過電圧 | −35〜+35 V | — | — | p2 | "VS, Analog Input Overvoltage with Power Off - 35 to + 35" |
| **Input Leakage (with Power Supplies Off)** | **0.001 µA typ、±2 µA（A suffix）/ ±5 µA（D suffix）** | **VS = ±25 V、VSUPS = 0 V、VD = A0, A1, A2, EN = 0 V**、Room | typ / min / max（画像で確認） | p3 | "Input Leakage Current (with Power Supplies Off) VS = ± 25 V, VSUPS = 0 V VD = A0, A1, A2, EN = 0 V Room 0.001 - 2 2 - 5 5 µA" |
| Input Leakage vs. Input Voltage（目読み、**V+ = V− = 0 V**） | VS = −10 V で約 7 pA、−30 V で約 15 pA、+10 V で約 2 pA、+30 V で約 4 pA。約 −45 V より負で急増（µA 域） | 25°C | グラフ（縦軸対数 1 pA〜1 mA） | p5 左上 | 図題 "Input Leakage vs. Input Voltage"、図中 "V+ = V- = 0 V" |
| 本文 | 電源喪失時、変換器・信号源に掛かる負荷は無視できる | — | — | p9 DETAILED DESCRIPTION | "in case of power loss to the multiplexer, the loading caused on the transducers and signal sources is insignificant" |
| RDS(on) | 180 Ω typ、400 Ω max | VD = ±5 V、IS = −400 µA、Room | typ / max | p3 | "VD = ± 5 V, IS = - 400 µA Room 180 400" |
| RDS(on) | **0.45 kΩ typ、1.2 kΩ（A Room）/ 1.5 kΩ（D Room）max** | VD = ±9.5 V、IS = −400 µA | typ / max（画像で確認） | p3 | "VD = ± 9.5 V, IS = - 400 µA Room 0.45 1.2 ... 1.5 kΩ" |
| 注 g | 信号が +13.5 V または −12 V を超えると RDS(on) が上がり始め、漏れ電流だけになる | — | — | p4 注 g | "When the analog signal exceeds the + 13.5 V or - 12 V,RDS(on) starts to rise until only leakage currents flow." |
| Off Isolation（OIRR） | 90 dB | VEN = 0 V、RL = 1 kΩ、CL = 15 pF、VS = 3 VRMS、f = 100 kHz | typ | p4 | "Off Isolation OIRR VEN = 0 V, RL = 1 k CL = 15 pF, VS = 3 VRMS f = 100 kHz Room 90 dB" |
| CS(off) / CD(off) / CD(on) | 5 / 15（DG458）/ 40（DG458）pF | f = 1 MHz | typ | p4 | "Source Off Capacitance CS(off) Room 5" / "DG458 Room 15" / "DG458 Room 40" |
| THD、電荷注入 | **DS に無い** | — | — | — | — |
| 正電源電流 I+ | 0.05 mA typ、0.1 mA max（Room） | VEN = 5 or 0 V、VA = 0 V | typ / max | p4 | "Positive Supply Current I+ Room 0.05 0.1" |

### 1.8 Renesas HI-546 / 547 / 548 / 549（過電圧保護マルチプレクサ）（`Renesas_HI-546_547_548_549.pdf`、FN3150 Rev 7.00）

電源断時の扱いは **(b)**。しかも「高インピーダンス」ではなく **1 kΩ** と書いている。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| **電源喪失時の入力** | **各入力が 1 kΩ を呈する**（信号源の短絡を防ぐ、という文脈） | マルチプレクサの電源喪失時 | — | p1 | "In addition, signal sources are protected from short circuiting should multiplexer supply loss occur. Each input presents 1kΩ of resistance under this condition." |
| 構成 | HI-546 16 ch、HI-547 差動 8 ch、HI-548 8 ch、HI-549 差動 4 ch | — | — | p1 | "The HI-546 is a single 16-Channel, the HI-547 is an 8-Channel differential, the HI-548 is a single 8-Channel and the HI-549 is a 4-Channel differential device." |
| 供給状況（注文情報の注記） | HI3-0546-5Z・HI4P0547-5Z は "No longer available" | — | — | p2 Ordering Information | "HI3-0546-5Z (Note) (No longer available, recommended replacement: HI9P0546-9Z, HI4P0546-5Z)" |
| HI-548 のパッケージ | 16 Ld CERDIP / 16 Ld PDIP / 16 Ld SOIC | — | — | p2 | "HI1-0548-2 ... 16 Ld CERDIP / HI3-0548-5Z ... 16 LEAD PDIP / HI9P0548-9Z ... 16 Ld SOIC" |
| 信号範囲 | −15 V / +15 V | Supplies = +15 V, −15 V、Full | min / max | p9 | "Analog Signal Range, VIN Full -15 - +15 V" |
| rON | 1.2 kΩ typ、1.5 kΩ max（−2 品、25°C）/ 1.5 / 1.8 kΩ（−5, −9 品） | Note 2: VOUT = 10 V、IOUT = 100 µA | typ / max | p9 | "On Resistance, rON Note 2 25 - 1.2 1.5 - 1.5 1.8 k" |
| Off Isolation | 50 dB min、68 dB typ | Note 6: VEN = 0.8 V、RL = 1 kΩ、CL = 15 pF、VS = 7 VRMS、f = 100 kHz | min / typ | p8 | "Off Isolation Note 6 25 50 68 - 50 68 - dB" |
| CS(OFF) / CD(OFF)（HI-548） | 10 / 25 pF | 25°C | typ | p8 | "Channel Input Capacitance, CS(OFF) 25 - 10" / "HI-548 25 - 25" |
| 電源断時の漏れ電流の表値 | **DS に無い**（ID(OFF) With Input Overvoltage は電源あり・Note 4: 33 V） | — | — | p9 | "ID(OFF) With Input Overvoltage Applied Note 4 25 - 4.0 - nA" / "4. Analog Overvoltage = 33V." |

### 1.9 参考: ADI MAX14778（既存の DS、`../datasheets/ADI_MAX14778.pdf`、19-5929; Rev 3; 7/20）

電源断時の扱いは **(b)**（数値は本文の「typ」だけ）。単電源 3.0〜5.5 V で ±25 V を通す 4:1 × 2。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成・電源 | デュアル 4:1、単電源 3.0〜5.5 V、信号 ±25 V | — | — | p1 | "The MAX14778 dual 4:1 analog multiplexer supports analog signals up to ±25V with a single 3.0 to 5.5V supply." |
| パッケージ | 20-pin TQFN 5 × 5 mm | — | — | p1 | "20-Pin TQFN (5mm x 5mm) Package" |
| **電源断時（本文）** | ±25 V を許容。**VDD = 0 V で入力漏れは typ 1 µA 未満、ばらつきで mA 域になる個体もある** | VDD = 0 V | 本文の字句 "typically" | p12 Non-Powered Condition | "The MAX14778 can tolerate input voltages on the A_, B_, ACOM, and BCOM pins in the ±25V range when it is not powered. When VDD = 0V, the DC input leakage current into the A_, B_, ACOM or BCOM pins will typically be below 1µA. Some devices can have a larger leakage current up to mA range due to technology spread." |
| 電源断時の過渡電流（本文） | 内部ダイオードが VP/VN の外付けコンデンサを充電し過渡電流が流れる。100 nF のとき dv/dt ≤ 3 V/µs | VDD 非給電 | — | p12 | "With VDD not powered, internal diodes between the analog pins and the VP and VN will charge up the external capacitors on VP and VN ... This causes transient input current flow. ... With 100nF capacitors on VP and VN, the dv/dt must be limited to 3V/µs" |
| RON | 0.84 Ω typ、1.7 Ω / 1.5 Ω max（2 行。行を分ける条件欄は空） | ICOM = ±300 mA、VIN = ±25 V | typ / max（画像で確認） | p3 | "On-Resistance RON Figure 1, ICOM = ±300mA, VIN = ±25V 0.84 1.7 / 0.84 1.5 Ω" |
| RFLAT(ON) | 3 mΩ | −25 V ≤ VIN ≤ +25 V、ICOM = ±300 mA | typ | p3 | "On-Resistance Flatness RFLAT(ON) ... 3 mΩ" |
| THD+N | 0.003 % | RS = RL = 1 kΩ、f = 20 Hz〜20 kHz | typ | p4 | "THD+N RS = RL = 1kΩ, f = 20Hz to 20kHz 0.003 %" |
| Off-Isolation | −80 dB | VA_ = 1 VRMS、f = 100 kHz、RL = 50 Ω、CL = 15 pF | typ | p4 | "Off-Isolation VISO Figure 6, VA_ = 1VRMS, f = 100kHz, RL = 50Ω, CL = 15pF -80 dB" |
| CIN（A_, B_） | 78 pF | — | typ | p4 | "Input Capacitance CIN A_, B_ pins 78 pF" |
| 電荷注入 | 1720 pC | VA_ = 0 V、CL = 1 nF | typ | p4 | "Charge Injection Q Figure 5, VA_ = 0V, CL = 1nF 1720 pC" |
| IDD | 2.54 mA typ / 6 mA max（VDD > VDDTH）、4.27 / 10 mA（VDD ≤ VDDTH） | ENA = ENB = high | typ / max | p3 | "Supply Current IDD ENA = ENB = high VDD ≤ VDDTH 4.27 10 / VDD > VDDTH 2.54 6 mA" |
| Power-Up Time tPOR | 404 ms | — | typ | p4 | "Power-Up Time tPOR 404 ms" |

リポジトリにある他のスイッチ DS（`ADI_ADG1406_1407.pdf`、`ADI_MAX14752_MAX14753.pdf`、`Vishay_DG506B_DG507B.pdf`）は、テキストを `power off / powered off / unpowered / VDD = 0 / VCC = 0 / V+ = 0 / without power` で検索して該当なし（電源断時の扱いは (c)）。

### どの DS にも無かった項目（アナログスイッチ）

- **電源断時の漏れ電流を、±9〜±15 V 程度の信号電圧で規定した表値**: どの DS にも無い。表の条件は TMUX4821 が ±15 V、TMUX741xF / 7462F が ±60 V、ADG5412F/BF が ±55 V、DG458 が ±25 V。低い電圧での値は DG458 のグラフ（V+ = V− = 0 V、目読み pA 域）だけ。
- **電源断時の OFF アイソレーション・OFF 容量**（VDD = VSS = 0 V のときの CS(OFF)/CD(OFF) や OISO）: どの DS にも無い。容量・アイソレーションはすべて電源投入時の値。
- **電源断時に drain 側（非保護側）へ信号が来た場合の規定**: TMUX741xF・TMUX7462F・ADG5412F は drain が電源へのダイオード付きで、電源断時の drain 電圧の許容を別に規定していない（TMUX741xF は本文に「source and drain ... ±60 V are blocked」とあり、同じ DS の ESD 節・絶対最大と食い違う）。**両側保護を明記しているのは ADG5412BF と TMUX4821（S/D とも IS(POFF)/ID(POFF) を規定）**。
- **電源断時の漏れの 25°C max**: TMUX4821 は 25°C が typ のみ（max は −40〜+85°C の ±0.1 µA から）。ADG5412F/BF の source 側 ±40 µA は typ のみ。TMUX741xF の IS(FA) Grounded ±125 µA も typ のみ。
- **音声帯域の OFF アイソレーション表値**: どれも 100 kHz か 1 MHz。1 kHz〜20 kHz はグラフ（ADG5412F Figure 20）だけ。
- **TMUX4821 の CD(OFF)**、**Figure 13-21 の "Stopping Frequency" の定義**: DS に無い。
- **DG458 の THD・電荷注入**、**HI-548 の電源断時漏れの表値**: DS に無い。
- **TMUX4821 の THD+N を ±9 Vpk（18 Vpp）で規定した表値**: 表は VPP = 0.5 V だけ。15 Vpp はグラフ（Figure 13-16）だけ。

---

## 2. PhotoMOS / 光半導体リレー（LED 消灯で開、1 Form A）

どの DS も「LED 電流 0 で開」は IFoff / IFC / "normally open" として書いている。**オン抵抗の直線性・歪みを規定した DS は無い**（§2 末尾）。

### 2.1 Panasonic AQV252G（HE 1 Form A、DIP6、60 V）（`Panasonic_AQV252G.pdf`、ASCTB144E 202204）

ページ対応: PDF p3 = 印刷「ー2ー」、PDF p4 = 「ー3ー」、PDF p5 = 「ー4ー」（PDF p1 は表紙）。表は AQV251G（30 V）と並記。以下は AQV252G の列。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 負荷電圧（絶対最大） | 60 V（peak AC） | 25°C | 値の列のみ | PDF p3 Absolute maximum ratings | "Load voltage (peak AC) VL - 30 V 60 V" |
| 連続負荷電流 | A 接続 2.5 A、B 接続 3.5 A、C 接続 5.0 A | A: Peak AC, DC、B/C: DC | 値の列のみ | PDF p3 | "Continuous load current IL A ... 2.5 A / B ... 3.5 A / C ... 5.0 A" |
| 推奨 LED 電流 | 5 mA / 30 mA | — | min / max | PDF p4 Recommended operating conditions | "LED current IF 5 30 mA" |
| 推奨 負荷電圧（AQV252G） | 48 V（peak AC） | — | max | PDF p4 | "AQV252G (A) Load voltage (Peak AC) VL - 48 V" |
| 動作 LED 電流 IFon | 0.5 mA typ、3 mA max | IL = 100 mA | Typical / Maximum 行 | PDF p3 Electrical characteristics | "LED operate current Typical 0.55 mA 0.5 mA IFon - IL = 100 mA Maximum 3 mA" |
| 復帰 LED 電流 IFoff | 0.2 mA min、0.45 mA typ | IL = 100 mA | Minimum / Typical 行 | PDF p3 | "LED turn off current Minimum 0.2 mA ... Typical 0.45 mA" |
| LED 順電圧 VF | 1.14 V typ（IF = 50 mA で 1.32 V）、1.5 V max | IF = 5 mA | Typical / Maximum | PDF p3 | "LED dropout voltage Typical 1.14 V (1.32 V at IF = 50 mA) VF - IF = 5 mA Maximum 1.5 V" |
| **オン抵抗 Ron（A 接続）** | **0.08 Ω typ、0.12 Ω max** | IF = 5 mA、IL = Max.、Within 1 s | Typical / Maximum | PDF p3 | "On resistance ... Ron A Typical 0.035 Ω 0.08 Ω IF = 5 mA ... Maximum 0.08 Ω 0.12 Ω IL = Max. Within 1 s" |
| オン抵抗（B / C 接続） | B: 0.04 / 0.06 Ω、C: 0.02 / 0.03 Ω | 同上 | Typical / Maximum | PDF p3 | "Ron B Typical ... 0.04 Ω ... Maximum ... 0.06 Ω" / "Ron C ... 0.02 Ω ... 0.03 Ω" |
| **開路時漏れ電流 ILeak** | **1 µA max** | IF = 0 mA、VL = Max. | Maximum | PDF p3 | "Off state leakage current Maximum ILeak - 1 μA IF = 0 mA VL = Max." |
| 図 9 漏れ電流 vs 負荷電圧（目読み） | AQV252G: 10 V で約 2 × 10⁻¹⁰ A、60 V で約 5 × 10⁻¹⁰ A | 端子 4–6 間、25°C | グラフ | PDF p5 図 9 | "9.Off state leakage current vs. load voltage characteristics" |
| **出力容量（表値）** | **DS に無い**（表にあるのは入出力間容量 Ciso のみ） | — | — | PDF p3 | — |
| 図 12 出力容量 vs 印加電圧（目読み） | AQV252G: 0 V で約 230 pF、10 V で約 100 pF、20 V で約 80 pF、60 V で約 55 pF | 端子 4–6 間、1 MHz、25°C | グラフ | PDF p5 図 12 | "12.Output capacitance vs. applied voltage characteristics" |
| 入出力間容量 Ciso | 0.8 pF typ、1.5 pF max | f = 1 MHz、VB = 0 V | Typical / Maximum | PDF p3 | "I/O capacitance Typical 0.8 pF Ciso - f = 1 MHz Maximum 1.5 pF VB = 0 V" |
| ターンオン時間 Ton | 1.1 ms typ、5.0 ms max | IF = 5 mA、IL = 100 mA、VL = 10 V | Typical / Maximum | PDF p3 | "Turn on time* Typical 1.1 ms ... Maximum 5.0 ms" |
| ターンオフ時間 Toff | 0.25 ms typ、0.5 ms max | 同上 | Typical / Maximum | PDF p3 | "Turn off time* Typical 0.1 ms 0.25 ms ... Maximum 0.5 ms" |
| 耐電圧（入出力間） | 1,500 Vrms | — | — | PDF p3 | "I/O isolation voltage Viso - 1,500 Vrms" |
| パッケージ | DIP 6 ピン（スルーホール AQV252G、表面実装 AQV252GA） | — | — | PDF p2 TYPES | "60 V 2.5 A AQV252G AQV252GA AQV252GAX" |

### 2.2 Panasonic AQW212EH（GE DIP8 2a、60 V、2 回路）（既存 `../datasheets/Panasonic_AQW212EH.pdf`、ASCTB53J 202601、日本語）

ページ対応: PDF p3 = 印刷「ー2ー」、PDF p6 = 「ー5ー」。表は AQW210EH 等と並記。以下は AQW212EH の列（画像で確認）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 負荷電圧 | 60 V（ピーク AC） | 25°C | 値の列のみ | PDF p3 絶対最大定格 | "負荷電圧 ( ピークAC ) VL 60 V" |
| 連続負荷電流 | 0.5 A（1a 1 回路のみ使用時 0.6 A） | ピーク AC、DC | 値の列のみ | PDF p3 | "連続負荷電流 IL 0.5 A ( 0.6 A )" / "( ) 内は1a 1回路のみの使用の場合" |
| 動作 LED 電流 IFon | 1.2 mA 平均、3.0 mA 最大 | IL = Max. | 平均 / 最大 | PDF p3 性能概要 | "動作LED電流 平均 1.2 mA 最大 3.0 mA" |
| 復帰 LED 電流 IFoff | 0.4 mA 最小、1.1 mA 平均 | IL = Max. | 最小 / 平均 | PDF p3 | "復帰LED電流 最小 0.4 mA 平均 1.1 mA" |
| **オン抵抗 Ron** | **0.83 Ω 平均、2.5 Ω 最大** | IF = 5 mA、IL = Max.、通電時間 1 秒以下 | 平均 / 最大 | PDF p3 | "オン抵抗 平均 0.83 Ω 最大 2.5 Ω IF = 5 mA IL = Max. 通電時間 = 1秒以下" |
| **開路時漏れ電流** | **1 µA 最大** | IF = 0 mA、VL = Max. | 最大 | PDF p3 | "開路時漏れ電流 最大 ILeak 1 µA IF = 0 mA VL = Max." |
| 図 9-2 漏れ電流 vs 負荷電圧（目読み） | AQW212EH: 20 V で約 6 × 10⁻¹² A、60 V で約 2 × 10⁻¹¹ A | 5–6、7–8 端子間、25°C | グラフ | PDF p6 図 9-2 | "9-2. 開路時漏れ電流−負荷電圧特性" |
| 出力容量（表値） | **DS に無い**（表は入出力端子間容量のみ） | — | — | PDF p3 | — |
| 図 12-2 出力端子間容量 vs 印加電圧（目読み） | AQW212EH: 0 V で約 80 pF、10 V で約 33 pF、30 V で約 20 pF | 1 MHz、25°C | グラフ | PDF p6 図 12-2 | "12-2. 出力端子間容量−印加電圧特性" |
| 入出力端子間容量 Ciso | 0.8 pF 平均、1.5 pF 最大 | f = 1 MHz、VB = 0 V | 平均 / 最大 | PDF p3 | "入出力端子間容量 平均 0.8 pF 最大 1.5 pF" |
| 動作時間 Ton | 1 ms 平均、4 ms 最大 | IF = 5 mA、IL = Max. | 平均 / 最大 | PDF p3 | "動作時間 平均 1 ms 最大 4 ms" |
| 復帰時間 Toff | 0.08 ms 平均、1.0 ms 最大 | 同上 | 平均 / 最大 | PDF p3 | "復帰時間 平均 0.08 ms 最大 1.0 ms" |
| 耐電圧 | 5,000 V rms | — | — | PDF p3 | "耐電圧 Viso 5,000 V rms" |
| パッケージ | DIP 8 ピン、2a（2 回路） | — | — | PDF p1 | "GE DIP8 2a" |

### 2.3 Toshiba TLP241A（1-Form-A、DIP4、40 V）（`Toshiba_TLP241A.pdf`、Rev.5.0 2018-01-30）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | 1-Form-A、4 ピン DIP。ピン配置図は出力 MOSFET 2 個の直列（ソース共通）を描く | — | — | p1 §3、p2 §6 | "Normally opened (1-Form-A)" / "They are housed in a 4-pin DIP package." |
| OFF 時出力端子電圧 VOFF | 40 V | 絶対最大 | 値の列のみ | p3 §8 | "OFF-state output terminal voltage VOFF 40 V" |
| ON 電流 ION | 2.0 A | 絶対最大 | 値の列のみ | p3 §8 | "ON-state current ION 2.0 A" |
| 推奨 入力電流 IF | 5 / 7.5 / 25 mA | — | min / typ / max | p3 §9 | "Input forward current IF 5 7.5 25 mA" |
| 推奨 電源電圧 VDD | 32 V | — | max | p3 §9 | "Supply voltage VDD 32 V" |
| トリガ LED 電流 IFT | 0.5 mA typ、3 mA max | ION = 1.0 A | typ / max（画像で確認） | p4 §11 | "Trigger LED current IFT ION = 1.0 A 0.5 3 mA" |
| 復帰 LED 電流 IFC | 0.1 mA min | IOFF = 10 µA | min（画像で確認） | p4 §11 | "Return LED current IFC IOFF = 10 µA 0.1" |
| **ON 抵抗 RON** | **60 mΩ typ、100 mΩ max** | ION = 2.0 A、IF = 5 mA、t < 1 s | typ / max（画像で確認） | p4 §11 | "ON-state resistance RON ION = 2.0 A, IF = 5 mA, t < 1 s 60 100 mΩ" |
| ON 抵抗（連続・熱飽和） | 90 mΩ typ、150 mΩ max | ION = 2.0 A、IF = 5 mA、Continuous（Note 1: Thermally saturated state） | typ / max | p4 §11 | "(Note 1) ION = 2.0 A, IF = 5 mA, Continuous 90 150" |
| **OFF 電流 IOFF** | **1000 nA max** | VOFF = 40 V | max（画像で確認） | p4 §10 | "OFF-state current IOFF VOFF = 40 V 1000 nA" |
| **出力容量 COFF** | **300 pF typ** | V = 0 V、f = 1 MHz | typ（画像で確認） | p4 §10 | "Output capacitance COFF V = 0 V, f = 1 MHz 300 pF" |
| 入出力間容量 CS | 0.8 pF typ | VS = 0 V、f = 1 MHz | typ | p4 §12 | "Total capacitance (input to output) CS ... 0.8 pF" |
| ターンオン / オフ時間 | 2.8 / 5 ms、0.3 / 1 ms | RL = 200 Ω、VDD = 20 V、IF = 10 mA | typ / max | p4 §13 | "Turn-on time tON ... 2.8 5 ms" / "Turn-off time tOFF 0.3 1" |
| 絶縁耐圧 BVS | 5000 Vrms min | AC, 60 s | min | p4 §12 | "Isolation voltage BVS (Note 1) AC, 60 s 5000 Vrms" |

### 2.4 Vishay VO14642AT / VO14642AABTR（1 Form A、DIP-6 / SMD-6、60 V）（`Vishay_VO14642A.pdf`、Rev. 1.8）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 構成 | SPST 1 Form A、出力は AC/DC 接続または DC のみ接続 | — | — | p1 | "high speed single channel normally open solid-state relay (SPST - 1 form A) in a DIP-6 package ... can be configured for AC/DC or DC only operation." |
| 負荷電圧 VL | 60 V（DC または peak AC） | 絶対最大 | 値の列のみ | p2 | "DC or peak AC load voltage VL 60 V" |
| 負荷電流 | 2000 mA（DC only） | 絶対最大 | 値の列のみ | p2 | "Load current (DC only) IL 2000 mA" |
| 動作 LED 電流 IFon | 0.5 mA typ、2 mA max | IL = 1 A、VL ≤ 0.5 V、t = 10 ms | typ / max（画像で確認） | p3 | "LED forward current, switch turn-on IL = 1 A, VL ≤ 0.5 V, t = 10 ms IFon - 0.5 2 mA" |
| 復帰 LED 電流 IFoff | 50 µA min | VL = 60 V、IL < 1 µA | min（画像で確認） | p3 | "LED forward current, switch turn-off VL = 60 V, IL < 1 μA IFoff 50 - - μA" |
| **オン抵抗（AC/DC）** | **0.18 Ω typ、0.25 Ω max** | IF = 10 mA、IL = 1 A | typ / max（画像で確認） | p3 | "On-resistance (AC/DC) IF = 10 mA, IL = 1 A RON - 0.18 0.25 Ω" |
| オン抵抗（DC only） | 0.05 Ω typ、0.07 Ω max | IF = 10 mA、IL = 2 A | typ / max | p3 | "On-resistance (DC only) IF = 10 mA, IL = 2 A RON - 0.05 0.07 Ω" |
| **OFF 漏れ ILEAK** | **1 µA max** | IF = 0 mA、VL = 60 V | max（画像で確認） | p3 | "Off-state leakage current IF = 0 mA, VL = 60 V ILEAK - - 1 μA" |
| Fig. 6 漏れ vs 温度（目読み） | 25°C 付近ではほぼ 0 nA、45°C を超えて増え 85°C で約 20 nA | VLOAD = 60 V | グラフ | p5 Fig. 6 | 図題 "Leakage Current vs. Temperature"、図中 "VLOAD = 60 V" |
| 出力容量（表値） | **DS に無い** | — | — | p3 | — |
| Fig. 14 Switch Capacitance vs Applied Voltage（目読み） | 0 V で約 205 pF、5 V で約 80 pF、10 V で約 65 pF、20 V で約 52 pF、40 V 以上で約 42 pF。**図中の温度は Tamb = −55 °C**。AC/DC・DC のどちらの接続かは図に無い | Tamb = −55 °C | グラフ | p6 Fig. 14 | 図中 "Tamb = -55 °C" |
| ターンオン / オフ時間（AC/DC） | 370 / 800 µs、50 / 800 µs | IF = 10 mA、VL = 30 V、IL = 200 mA | typ / max | p3 | "Turn-on time IF = 10 mA, VL = 30 V, IL = 200 mA ton - 370 800 μs" / "Turn-off time ... toff - 50 800 μs" |
| 絶縁試験電圧 | 5300 VRMS | — | — | p1 | "Isolation test voltage 5300 VRMS" |
| パッケージ | DIP-6（VO14642AT）、SMD-6（VO14642AABTR） | — | — | p1 | "SMD-6, tape and reel VO14642AABTR / DIP-6, Tubes VO14642AT" |

### どの DS にも無かった項目（PhotoMOS / 光リレー）

- **オン抵抗の直線性・歪み（THD）・オン抵抗の電圧依存**: 4 品ともどの DS にも無い。オン抵抗は電流 = 最大（1〜2.5 A）での1点だけで、信号レベル（mA 以下）での値も無い。
- **出力容量の表値**: TLP241A の COFF 300 pF typ（V = 0 V）だけ。AQV252G・AQW212EH・VO14642A はグラフのみ（しかも電圧で大きく変わる曲線）。
- **OFF アイソレーション（dB）**: どの DS にも無い。
- **25°C・低電圧（±10 V 程度）での漏れの表値**: どれも VL = Max.（40〜60 V）での max のみ。低電圧はグラフ（AQV252G 図 9、AQW212EH 図 9-2）だけ。
- **LED 消灯時に出力が開であることの保証値としての「LED 0 mA での状態」**: 表の形では IFoff / IFC（この電流以下で開）として書かれているだけで、「LED 電源が落ちたとき」を別に規定した DS は無い。
- **TLP241A の最新版（2023-05-25 版）の中身**: 取得できず未確認（403）。

---

## 3. 信号リレー（非ラッチ・ラッチ）

ラッチ型について、依頼された項目（セット/リセットのコイル電流・電力、最小パルス幅と連続通電の扱い、2 コイルの同時通電、動作/復帰時間、出荷時の状態と衝撃による反転、バウンス時間）は各部品の表に「ラッチ型」の行として入れ、無いものは「DS に無い」と書いた。

### 3.1 Zettler AZ850（DPDT、5 × 14 × 9 mm）（既存 `../datasheets/Zettler_AZ850.pdf`、2019-03-26、2 p）

ラッチ型の一部は [switch_control.md §2](switch_control.md) にある。ここでは原文 p1–p2 を読み直し、非ラッチ 5 V と依頼のラッチ項目を足した。表はすべて "All values at 20°C (68°F) unless otherwise stated"（p2 NOTES 2）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 外形 | 高さ 5 mm、長さ 14 mm、幅 9 mm | — | — | p1 FEATURES | "Compact size: Height: 0.197“ (5 mm); Length: 0.551“ (14 mm); Width: 0.354“ (9 mm)" |
| 接点材質 | AgPd（銀パラジウム）、金クラッド | — | — | p1 CONTACTS | "Contact materials AgPd - silver palladium, gold clad" |
| 初期接触抵抗 | < 50 mΩ（測定条件は DS に無い） | — | "<" 表記 | p1 | "Initial resistance < 50 mΩ" |
| 最小開閉負荷 | 10 mV、10 µA | — | — | p1 | "Minimum switching voltage 10 mV current 10 µA" |
| **非ラッチ 5 V: コイル抵抗** | **178 Ω ±10 %** | 20°C | 表値 | p2 "Monostable non-latching" | "5 3.75 12.5 178"（列見出し "Nominal Coil VDC / Must Operate VDC / Max. Continuous VDC / Resistance Ohm ± 10%"） |
| 非ラッチ 5 V: Must Operate / Max. Continuous | 3.75 VDC / 12.5 VDC | 20°C | 表値 | p2 | 同上 |
| 非ラッチ: Dropout（復帰電圧） | 定格コイル電圧の 10 % 超 | — | — | p1 COIL | "Dropout non-latching types > 10% of nominal coil voltage" |
| 非ラッチ 5 V: 定格電圧でのコイル電流・電力 | **DS に無い**。計算: 5 V / 178 Ω ≈ 28.1 mA、5² / 178 ≈ 140 mW | — | 計算 | — | — |
| 非ラッチ: 感動電圧での電力 | 79〜113 mW | "Power at pickup voltage" | typ（範囲表記） | p1 COIL | "Power at pickup voltage (typ.) monostable non-latching 79 - 113 mW" |
| 非ラッチ: 動作 / 復帰時間 | 2 ms / 1 ms | 定格コイル電圧、復帰はサプレッションなし | typ | p1 GENERAL DATA | "Operate Time at nominal coil voltage non-latching types 2 ms (typ.)" / "Release Time ... w/o coil suppression non-latching types 1 ms (typ.)" |
| ラッチ P1（単コイル）5 V | 250 Ω ±10 %、Must Operate 3.75 V、Max. Continuous 14.5 V | 20°C | 表値 | p2 "Single coil latching" | "5 3.75 14.5 250" |
| ラッチ P1 5 V: セット/リセット電流・電力 | **DS に無い**。計算: 5 / 250 = 20 mA、100 mW | — | 計算 | — | — |
| ラッチ P2（2 コイル）5 V | 125 Ω ±10 %、Must Operate 3.75 V、Max. Continuous 10.0 V。**表の抵抗が 1 コイルあたりかは DS に書いていない** | 20°C | 表値 | p2 "Dual coil latching" | "5 3.75 10.0 125" |
| ラッチ P2 5 V: セット/リセット電流・電力 | **DS に無い**。計算（125 Ω を 1 コイルとして）: 40 mA、200 mW | — | 計算 | — | — |
| ラッチ: 感動電圧での電力 | P1 56〜84 mW、P2 113〜169 mW | "Power at pickup voltage" | typ | p1 COIL | "bistable single coil latching 56 - 84 mW bistable dual coil latching 113 - 169 mW" |
| ラッチ: セット / リセット時間 | 2 ms / 1 ms | 定格コイル電圧 | typ | p1 GENERAL DATA | "Set Time at nominal coil voltage latching types 2 ms (typ.)" / "Reset Time ... latching types 1 ms (typ.)" |
| ラッチ: 最小パルス幅 | **DS に無い** | — | — | — | — |
| ラッチ: 連続通電 | "Max. Continuous VDC" の列がラッチ型にもある（P1 5 V 品 14.5 V、P2 5 V 品 10.0 V）。連続通電の可否を述べた本文は無い | 20°C | 表値 | p2 | 同上 |
| ラッチ P2: セット・リセットコイルの同時通電 | **DS に無い** | — | — | — | — |
| ラッチ: Must Release / リセット電圧 | **DS に無い**（表は Must Operate と Max. Continuous のみ） | — | — | p2 | — |
| コイル極性 | 固定 | — | — | p2 NOTES 5 | "Relay has fixed coil polarity" |
| 出荷時の状態 | **DS に無い**（配線図の注は「図はリセット状態で描いた」だけ） | — | — | p2 WIRING DIAGRAMS | "Viewed towards terminals, shown in deenergized / reset condition." |
| 衝撃・振動 | 衝撃（動作中）50 g、振動 動作 3 mm DA / 破壊 5 mm DA（10–55 Hz）。**ラッチ状態が衝撃で変わることへの言及は無い** | — | — | p1 GENERAL DATA | "Shock operating 50 g" / "Vibration resistance operating 3 mm (0.118") DA at 10–55 Hz damage 5 mm (0.197") DA at 10–55 Hz" |
| バウンス時間 | **DS に無い** | — | — | — | — |
| 静電容量 | コイル–接点 0.9 pF、接点組間 0.2 pF、開接点間 0.4 pF | — | typ | p1 | "Capacitance (typ.) coil to contacts 0.9 pF between contact sets 0.2 pF between open contacts 0.4 pF" |
| 隣接リレー間隔 | 5.0 mm 推奨（磁界の分離） | — | — | p2 NOTES 6 | "it is recommended that a .197" (5.0 mm) space be provided between adjacent relays." |

### 3.2 Omron G6K（DPDT、表面実装・PCB 端子）（`Omron_G6K.pdf`、Cat. No. K106-E1-11）

ラッチ型は **単巻線ラッチ（G6KU-2F-Y / 2G-Y / 2P-Y）だけ**。2 巻線ラッチは型番表に無い。p3 の Ratings・Characteristics は画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 外形 | 5.2 (H) × 6.5 (W) × 10 (L) mm（G6K(U)-2F(-Y)） | — | — | p1 | "Subminiature model as small as 5.2 (H) × 6.5 (W) × 10 (L) mm ... (G6K(U)-2F(-Y))." |
| 接点材質 | Ag (Au-Alloy contact) | — | — | p3 Contacts | "Contact material Ag (Au-Alloy contact)" |
| 接触抵抗 | 100 mΩ max | *1: 10 mA、1 VDC、電圧降下法 | max | p3 Characteristics | "Contact resistance *1 100 mΩ max." / "*1. The contact resistance was measured with 10 mA at 1 VDC with a voltage-drop method." |
| 故障率（P 水準） | 10 µA at 10 mVDC | *3: 120 回/分、判定 50 Ω | — | p3 | "Failure rate (P level) *3 10 μA at 10 mVDC" |
| **非ラッチ 5 VDC** | 定格電流 21.1 mA、コイル抵抗 237 Ω、Must operate 80 % max、Must release 10 % min、最大電圧 150 %、消費電力 約 100 mW | 23°C、±10 % | 表値 | p3 "Coil: Single-side Stable Models" | "5 VDC 21.1 237 80% max. 10% min. 150% Approx. 100" |
| **ラッチ（単巻線）5 VDC** | 定格電流 21.1 mA、コイル抵抗 237 Ω、**Must operate 75 % max、Must release 75 % max**、最大電圧 150 %、消費電力 約 100 mW | 23°C、±10 % | 表値 | p3 "Coil: Single-winding Latching Models" | "5 VDC 21.1 237 75% max. 75% max. 150% Approx. 100" |
| 最大電圧の定義 | 瞬時に加えてよい最高電圧 | — | — | p3 Note 3 | "The maximum voltage is the highest voltage that can be imposed on the relay coil instantaneously." |
| 動作（セット）/ 復帰（リセット）時間 | 3 ms max / 3 ms max | — | max | p3 Characteristics | "Operating (set) time 3 ms max." / "Release (reset) time 3 ms max." |
| **ラッチ: 最小セット/リセット信号幅** | **10 ms** | 単巻線ラッチ型 | — | p3 Characteristics | "Minimum set/reset signal width − 10 ms" |
| ラッチ: 連続通電 | ラッチ専用の規定は **DS に無い**。一般注意として連続電圧印加はコイル温度を上げ寿命・絶縁に影響 | — | — | p9 Maximum Allowable Voltage | "It must be noted that continuous voltage application to the coil will cause a coil temperature increase thus affecting characteristics such as electrical life and resulting in the deterioration of coil insulation." |
| ラッチ: コイル極性 | 端子配置図に「コイル極性を確認せよ」 | — | — | p6–p7 Terminal Arrangement | "Note: Check carefully the coil polarity of the Relay." |
| **ラッチ: 出荷時の状態・衝撃での反転** | **出荷時はリセット**。過大な振動・衝撃で誤ってセットされうる。使用前にリセット信号を与えよ。同一パネル上の他リレー等からの振動・衝撃が定格を超えるとセット→リセット（逆も）がありうる | — | — | p9 Latching Relay Mounting | "Make sure that the vibration or shock that is generated from other devices, such as relays in operation, on the same panel and imposed on the Latching Relay does not exceed the rated value, otherwise the Latching Relay that has been set may be reset or vice versa. The Latching Relay is reset before shipping. If excessive vibration or shock is imposed, however, the Latching Relay may be set accidentally. Be sure to apply a reset signal before use." |
| 衝撃 | 誤動作 750 m/s²、破壊 1,000 m/s² | — | — | p3 | "Shock resistance Destruction 1,000 m/s2 Malfunction 750 m/s2" |
| 振動（誤動作） | 10-55-10 Hz、片振幅 1.65 mm（複振幅 3.3 mm）および 55〜500 Hz 200 m/s² | — | — | p3 | "Malfunction 10-55-10 Hz, 1.65 mm single amplitude (3.3 mm double amplitude) and 55 to 500 Hz, 200 m/s2" |
| バウンス時間（目読み） | "Must Operate and Must Release Bounce Time Distribution": 約 0.2〜0.8 ms に分布 | **試料は非ラッチ G6K-2G、50 個**、23°C | グラフ（ヒストグラム） | p5 | "Sample: G6K-2G Number of Relays: 50 pcs"、凡例 "Must operate bounce time / Must release bounce time" |
| ラッチ型のバウンス時間 | **DS に無い** | — | — | — | — |
| 長期連続 ON の推奨 | 長期連続 ON の回路にはラッチリレーを推奨 | — | — | p9 Long-term Continuously ON Contacts | "We recommend using a latching relay (magnetic-holding relay) in this kind of circuit." |
| 動作温度 | −40〜70°C | — | — | p3 | "Ambient operating temperature -40 to 70°C" |

### 3.3 Panasonic TQ（2 Form C、14 × 9 × 5 mm）（`Panasonic_TQ.pdf`、ASCTB14E 202507）

**⚠ この PDF は AES 暗号化されていて、poppler（`pdftotext` / `pdftoppm`）では文字が出ない**（表の罫線だけ描画される）。PyMuPDF（scratchpad に一時インストール）でテキストを抜き、ページ画像も PyMuPDF で描いて表を確認した。ページ対応: **PDF ページ = 印刷ページ + 1**（例: PDF p5 = 「ー4ー」）。

**PC 板端子品と表面実装品で仕様が違う**（接点材質・接触抵抗・時間・電流）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 外形 | PC 板端子 14 × 9 × 5 mm、表面実装 14 × 9 × 5.6 mm | — | 外形図の寸法 | PDF p2（画像で確認） | 図中 "14 / 9 / 5" と "14 / 9 / 5.6"、"（Unit：mm）" |
| **接点材質（PC 板端子）** | Ag ＋ Au clad | — | — | PDF p6 Specifications（画像で確認） | "Contact material Ag ＋ Au clad" |
| 接点材質（表面実装） | AgNi ＋ Au clad | — | — | PDF p8 Specifications | "Contact material AgNi ＋ Au clad" |
| 接触抵抗（初期） | PC 板端子 50 mΩ max、表面実装 75 mΩ max | 電圧降下法 6 V DC 1 A | Max. | PDF p6 / PDF p8 | "Max. 50 mΩ (by voltage drop 6 V DC 1 A)" / "Max. 75 mΩ ( by voltage drop 6 V DC 1 A )" |
| 最小開閉負荷（参考値） | 10 µA 10 mV DC | *1: 微小負荷での下限の目安 | — | PDF p6 | "Min. switching load ( reference value )*1 10 µA 10 mV DC" |
| 注 *1 の追記 | 低レベル負荷のアナログ回路（10 V DC、10 mA 以下）には TX/TX-S/TX-D の AgPd 接点品がある | — | — | PDF p6 / p8 | "TX/TX-S/TX-D relay AgPd contact type are available for low level load analog circuit ( 10 V DC, 10 mA max. level )." |
| **非ラッチ 5 V（PC 板・標準接点）** | 28.1 mA、178 Ω、140 mW、Operate 75 % max、Release 10 % min、最大許容 150 % | 20°C、±10 % | 表値 | PDF p5（画像で確認） | "5 V DC ... 28.1 mA 178 Ω 140 mW" / "Max. 75 % V of rated coil voltage ( Initial )" / "Min. 10 % V of rated coil voltage ( Initial )" |
| **1 コイルラッチ 5 V（PC 板）** | **20 mA、250 Ω、100 mW**、Set 75 % max、Reset 75 % max、最大許容 150 % | 同上 | 表値 | PDF p5（画像で確認） | "5 V DC ... 20 mA 250 Ω 100 mW" |
| **2 コイルラッチ 5 V（PC 板）** | **セット・リセット各 40 mA、各 125 Ω、各 200 mW**、Set/Reset 75 % max、最大許容 150 % | 同上 | 表値（Set coil / Reset coil の列） | PDF p5（画像で確認） | "5 V DC ... 40 mA 40 mA 125 Ω 125 Ω 200 mW 200 mW" |
| 非ラッチ 5 V（表面実装） | 28.1 mA、178 Ω、140 mW | 同上 | 表値 | PDF p7（画像で確認） | "5 V DC ... 28.1 mA 178 Ω 140 mW" |
| **1 コイルラッチ 5 V（表面実装）** | **14 mA、357 Ω、70 mW** | 同上 | 表値 | PDF p7（画像で確認） | "5 V DC ... 14 mA 357 Ω 70 mW" |
| **2 コイルラッチ 5 V（表面実装）** | **各 28.1 mA、各 178 Ω、各 140 mW** | 同上 | 表値 | PDF p7（画像で確認） | "5 V DC ... 28.1 mA 28.1 mA 178 Ω 178 Ω 140 mW 140 mW" |
| 型番注 *2 | 5 V のトランジスタ駆動では 4.5 V 品を推奨 | — | — | PDF p2 / p3 | "*2: In case of 5 V transistor drive circuit, it is recommended to use 4.5 V type relay." |
| 使用電圧 | 定格コイル電圧の ±5 % 以内で使う | — | — | PDF p5 Coil data | "Therefore, please use the relay within ±5 % of rated coil voltage." |
| 動作（セット）/ 復帰（リセット）時間 | PC 板 3 ms max / 3 ms max、表面実装 4 ms max / 4 ms max | 定格コイル電圧、20°C、バウンス除く、復帰はダイオードなし | Max. | PDF p6 / PDF p8 | "Operate [ Set ] time Max. 3 ms at rated coil voltage ( at 20 ℃, without bounce )" / "Max. 4 ms at rated coil voltage ( at 20 ℃ , without bounce )" |
| **ラッチ: セット/リセットのパルス幅** | 定格電圧で **10 ms 以上を推奨** | 温度変動・動作条件の差に対する確実な動作のため | — | PDF p17 GUIDELINES FOR USAGE ● Latching | "we recommend setting the coil applied set and reset pulse time to 10 ms or more at the rated coil voltage." |
| ラッチ: 連続通電 | ラッチ型の連続通電の可否を述べた本文は **DS に無い**。表の「最大許容電圧」150 % は 1/2 コイルラッチにもある | — | — | PDF p5 | — |
| **2 コイルラッチ: 同時通電** | **セットコイルとリセットコイルに同時に電圧を加えないこと** | — | — | PDF p18 Coil connection | "Avoid impressing voltages to the set coil and reset coil at the same time." |
| コイル極性 | 有極リレーは内部接続図で極性を確認 | — | — | PDF p18 Coil connection | "When connecting coils of polarized relays, please check coil polarity ( ＋, － ) at the internal connection diagram ( Schematic )." |
| **ラッチ: 出荷時の状態・衝撃** | **リセット位置で出荷**。輸送中の揺れや取り付け時の衝撃で変わりうる。電源投入直後に初期化（セットとリセット）できる回路を推奨 | — | — | PDF p17 ● Latching | "The relay is shipped in the reset position. But jolts during transport or impacts during installation can change the reset position. It is, therefore, advisable to build a circuit in which the relay can be initialized ( set and reset ) just after turning on the power." |
| 衝撃 | PC 板: 機能 490 m/s²（11 ms、検出 10 µs）、破壊 980 m/s²。表面実装: 機能 750 m/s²（6 ms）、破壊 1,000 m/s² | — | — | PDF p6 / PDF p8 | "Functional 490 m/s2 ( half-sine shock pulse: 11 ms, detection time: 10 µs )" / "Functional 750 m/s2 ( half-sine shock pulse: 6 ms, detection time: 10 µs )" |
| 振動 | 機能 10〜55 Hz 複振幅 3 mm（検出 10 µs）、破壊 複振幅 5 mm | — | — | PDF p6 | "Functional 10 to 55 Hz ( at double amplitude of: 3 mm, detection time: 10 µs )" |
| バウンス時間 | **DS に無い**（時間は "without bounce" と除外。バウンスへの言及は MBB 接点の注だけ） | — | — | PDF p17 | "A small OFF time may be generated by the contact bounce during contact switching."（M.B.B. contact の項） |
| 長期連続通電 | 長期間の通電回路には磁気保持（ラッチ）型を使うこと | — | — | PDF p18 Long term current carrying | "For circuits such as these, please use a magnetic-hold type latching relay." |
| 電気的寿命の表の字句（原文のまま） | PC 板品の表に "0.5 A 125 V DC"（同じページの接点定格は "0.5 A 125 V AC"） | — | — | PDF p6 Electrical life | "0.5 A 125 V DC Min. 100 × 103 ope." |

### 3.4 Omron G5V-2（DPDT、非ラッチのみ）（`Omron_G5V-2.pdf`、Cat. No. K046-E1-06）

ラッチ型は型番表に無い（Standard と High-sensitivity の2系列のみ）。p1–p2 は画像で確認。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 外形 | 20.5 max × 10.1 max × 11.5 max mm | 各値 ±0.3 mm | 寸法図 | p4 Dimensions | "20.5max. ... 10.1max. ... 11.5max." |
| 接点材質 | Ag + Au-alloy | — | — | p2 Contacts | "Contact material Ag + Au-alloy" |
| 接触抵抗 | Standard 50 mΩ max、High-sensitivity 100 mΩ max | *1: 10 mA、1 VDC、電圧降下法 | max | p1 Characteristics | "Contact resistance *1 50 mΩ max. 100 mΩ max." |
| 故障率（P 水準、参考値） | 10 µA at 10 mVDC | — | — | p1 | "Failure rate (P level) (reference value) *3 10 μA at 10 m VDC" |
| **5 VDC Standard** | 100 mA、50 Ω、Must operate 75 % max、Must release 5 % min、最大 120 %、約 500 mW | 23°C、±10 % | 表値 | p2 Coil | "5 VDC 100 50 75% max. 5% min. 120% (at 23°C) Approx. 500" |
| **5 VDC High-sensitivity（G5V-2-H1）** | 30 mA、166.7 Ω、75 % max、5 % min、最大 180 %、約 150 mW | 同上 | 表値 | p2 Coil | "5 VDC 30 166.7 75% max. 5% min. 180% (at 23°C) Approx. 150" |
| 動作 / 復帰時間 | 7 ms max / 3 ms max | — | max | p1 | "Operate time 7 ms max. / Release time 3 ms max." |
| 衝撃（誤動作） | Standard 200 m/s²、High-sensitivity 100 m/s² | — | — | p1 | "Malfunction 200 m/s2 100 m/s2" |
| バウンス時間 | **DS に無い** | — | — | — | — |

### 3.5 Fujitsu FTR-B3（2 Form C、非ラッチ・1 コイルラッチ）（`Fujitsu_FTR-B3.pdf`、Rev. 03/2002）

**⚠ この DS のコイル表に 5 V 品は無い**（1.5 / 3 / 4.5 / 12 / 24 VDC）。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 外形 | 10.6 ± 0.2 mm × 7.2 ± 0.2 mm、高さ 5.25 ± 0.2 mm | — | 寸法図 | p1, p7–p8 | "Ultra slim and light weight with a 5.25±0.2 mm height" / 図中 "10.6 ±0.2 ... 7.2 ±0.2" |
| 接点材質 | 金被覆銀合金（Gold overlay silver alloy） | — | — | p4（画像で確認） | "Contact material Gold overlay silver alloy" |
| 接触抵抗 | 75 mΩ max | 6 VDC 1 A | maximum | p4 | "Contact resistance (initial value) 75mΩ, maximum at 6VDC 1A" |
| 最小開閉負荷（参考値） | 10 mVDC、0.01 mA | *1 | — | p4 | "Minimum switching load *1 10mVDC, 0.01mA*1" |
| 静電容量 | 開接点間 約 0.4 pF、隣接接点間 約 0.5 pF、コイル–接点 約 1.0 pF | — | Approximately | p4 | "Approximately 0.4pF (between open contacts) Approimately 0.5pF (adjacent contacts) Approximately 1.0pF *1(between coil and contacts)" |
| コイル（非ラッチ）4.5 V | 145 Ω、動作 +3.38 V、復帰 +0.45 V、140 mW | 20°C | 表値 | p3 COIL DATA CHART | "FTR-B3( )A4.5Z 4.5VDC 145 Ω +3.38V +0.45V 140mW" |
| コイル（1 コイルラッチ）4.5 V | 203 Ω、セット +3.38 V、リセット −3.38 V、100 mW | 20°C | 表値 | p3 | "FTR-B3 ( )B4.5Z 4.5VDC 203 Ω +3.38V -3.38V 100mW" |
| 5 V コイル品 | **DS に無い** | — | — | p3 | — |
| 定格電力 / 動作電力 | 非ラッチ 140 mW / 80 mW、ラッチ 100 mW / 57 mW | 20°C | 表値 | p4（画像で確認） | "Nominal power (at 20˚ C) 140mW 100mW / Operate power (at 20˚ C0 80mW 57mW" |
| 動作 / 復帰時間 | 3 ms max / 3 ms max | 定格電圧、バウンス除く | maximum | p4 | "Operate (at nominal voltage, without bounce) 3ms maximum / Release (at nominal voltage, without bounce) 3ms maximum" |
| ラッチ: パルス幅（目読み） | "Pulse characteristics": セット/リセットに要る電圧（定格比）は パルス幅 1 ms で約 80 %、約 5 ms 以上で約 57 % に下がって横ばい | "At set/reset" | グラフ | p5（画像で確認） | 図題 "Pulse characteristics"、凡例 "At set/reset"、横軸 "Pulse width (ms)" |
| ラッチ: 最小パルス幅の表値 | **DS に無い** | — | — | — | — |
| ラッチ: 出荷時の状態・衝撃での反転 | **DS に無い** | — | — | — | — |
| 機械的寿命 | 非ラッチ 50 × 10⁶ 回、ラッチ 20 × 10⁶ 回（3 Hz） | — | min. | p5（画像で確認） | "50 x 10⁶ operations min. (at 3Hz) / 20 x 10⁶ operations min.(at 3Hz)" |
| 衝撃 | 誤動作 750 m/s² 以上、耐久 1000 m/s² 以上 | — | Min. | p5 | "Shock resistance Malfunction Min. 750 m/s2 Endurance Min. 1000 m/s2" |
| バウンス時間 | **DS に無い** | — | — | — | — |

### どの DS にも無かった項目（信号リレー）

- **ラッチ型のバウンス時間**: どの DS にも無い。値として出ているのは G6K の**非ラッチ試料（G6K-2G）**のヒストグラム（約 0.2〜0.8 ms、目読み）だけ。TQ・FTR-B3 は時間を "without bounce" で除外している。
- **2 コイルラッチの同時通電**: 明記は **TQ の「同時に加えないこと」だけ**。AZ850 P2 には無い（G6K・FTR-B3 は 2 コイルラッチ品が無い）。
- **最小セット/リセットパルス幅**: 表値は G6K の 10 ms だけ。TQ は「10 ms 以上を推奨」（注意事項の本文）。FTR-B3 はグラフのみ。AZ850 は無い。
- **ラッチ型の連続通電の可否**: どの DS も明示していない（AZ850 は "Max. Continuous VDC" の列、G6K・TQ は最大電圧 150 % の列があるだけ）。
- **出荷時の状態**: G6K と TQ は「リセットで出荷、衝撃で変わりうる、使用前に初期化」と明記。AZ850・FTR-B3 には無い。
- **AZ850 の定格電圧でのコイル電流・電力**（非ラッチ・ラッチとも）と、P2 の抵抗が 1 コイルあたりか: DS に無い（抵抗から計算するしかない）。
- **FTR-B3 の 5 V コイル品**: DS に無い。
- **接触抵抗の微小電流（mV・µA 級）での値**: どれも 10 mA / 1 V（Omron）か 1 A / 6 V（TQ・FTR-B3）の測定。AZ850 は測定条件も無い。
- **ラッチ型の Must Release（リセット電圧）**: AZ850 は無い。G6K・TQ は「75 % max」、FTR-B3 は −（定格の 75 %）の電圧値で書いている。
