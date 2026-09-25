# 境界スイッチ候補 DS 事実表の独立照合（boundary.md）

- 照合日: 2026-09-25
- 対象: `AudioV2.1/ds_facts/boundary.md`（書き換えていない）
- DS: `AudioV2.1/datasheets/boundary/` の 14 本と、`AudioV2.1/datasheets/` の `TI_TMUX7612.pdf` / `ADI_MAX14778.pdf` / `Zettler_AZ850.pdf` / `Panasonic_AQW212EH.pdf`
- やり方: 出典に書かれたページをすべて `pdftoppm -png -r 150` で画像にし、表の罫線・列見出し・ページ見出しの条件・脚注を目で確かめた。
  Panasonic TQ は poppler では文字が描かれないので（`pdftotext` は 150 バイト、`pdftoppm` の画像は罫線だけ。boundary.md §3.3 の記述どおり）、scratchpad に置いた PyMuPDF 1.28.2 で本文を抜き、ページ画像も PyMuPDF で描いた。
  「DS に無い」とされた項目は、各 DS の全文（`pdftotext -layout`）をキーワードで探したうえで、該当しそうなページを画像で見た。
  グラフは boundary.md の数値を見る前に自分で読んだ。TMUX4821 Figure 13-21 と DG458 の「Input Leakage vs. Input Voltage」は PyMuPDF で 400〜576 dpi 相当に描き、軸ラベルの座標から較正して画素で境界・曲線を拾った。そのほかのグラフは 5 倍に拡大して目で読んだ。
  作業ファイルは scratchpad の `verify_boundary/` にある。
- 照合した行: **表の行 337 行**（boundary.md の表の全データ行）＋ **表の外の記述 30 件**（「取得した DS」の下の文 2 件、§1.0 の総論 1 件、§1.6 の前書き 1 件、他のスイッチ DS の検索結果 1 件、§2 冒頭 1 件、§3.3 の poppler の注 1 件、「どの DS にも無かった項目」の箇条 23 件）＝ **367 件**
- 判定の内訳: **一致 330**／**一致・補足あり 27**／**誤り 7**／**条件の誤り 1**／列の誤り 0／引用が無い 0／**確かめられず 2**

## 要約

**(a) 電源断保護つきアナログスイッチ・(b) PhotoMOS・(c) ラッチリレーのどれを選ぶかを変える誤りは無かった。** 比較の決め手になる行は、どれも DS の値・列・条件・ページどおりだった。

- **電源断時の漏れ（列・条件つき）:** TMUX4821 の IS(POFF)/ID(POFF)（25°C は typ 0.02 µA だけ、VDD = 0 V・VS = ±15 V）、TMUX741xF / TMUX7462F の IS(FA)/ID(FA) Grounded・Floating（VS = ±60 V、IS(FA) は typ だけ）、ADG5412F/BF の ±40 µA（typ、−40〜+125°C 列だけに印刷）と ±10 nA typ / ±30 nA max、DG458 の ±2 µA（A suffix）/ ±5 µA（D suffix）（VS = ±25 V）は、すべて一致した。
- **どちらの側が守られるか:** TMUX741xF・TMUX7462F・ADG5412F は source 側だけ（drain は電源へダイオード、絶対最大は電源 ±0.7 V）。ADG5412BF は両側。TMUX4821 は S/D 両方の漏れを規定し、本文でも S と D を切り離すと書いている。ここも一致した。TMUX741xF の DS 内の食い違い（§9.3.2.2 は「source と drain の ±60 V を電源断時に遮断」、§9.3.2.5 と絶対最大は「drain は電源を超えてはならない」）も原文どおりだった。
- **TMUX7612 に電源断時の規定が無いこと:** boundary.md のキーワードに加えて absent / removed / no supply / power loss / power down / isolat などでも全文を探したが、電源を切ったときの漏れ・Hi-Z の規定は無かった。あるのは §7.3.5 の電源シーケンス自由と、絶対最大のダイオードクランプの注だけ。
- **TMUX4821:** 単電源 1.8〜5.5 V で VS/VD = −15〜+15 V を通すこと、RON、OISO（−50 dB、**f = 100 kHz**）、CS(OFF) 70 pF、THD+N（表は **VPP = 0.5 V** だけ）はすべて一致した。**Figure 13-21 は自分で画素較正して読んだ値が boundary.md の値と読み誤差の範囲で合った**（推奨領域の上限は 18 Vpp で約 15 kHz、そのすぐ上の約 16.5 kHz から "No Operation Region"。逆に 20 kHz で推奨領域に入るのは約 16.7 Vpp まで。どちらも VDD = 5 V）。
- **ADG5412F/BF:** VS = ±9 V の RON（9.5 Ω typ、10.7 / 13.5 / 16 Ω max。節見出しの条件は VDD = ±13.5 V）、THD+N（0.0015 %、15 V p-p、10 kΩ）、QINJ（−680 pC、CL = 1 nF）は一致した。DYNAMIC CHARACTERISTICS の注 1 に「設計保証、製造試験なし」とある（補足）。
- **DG458:** VD = ±9.5 V の RDS(on) と、電源断時の入力漏れのグラフ（V+ = V− = 0 V）は一致した。グラフの細かい値は、自分の読みの方が少し小さい（下の表）。
- **HI-548:** 「電源喪失時は各入力が 1 kΩ」は p1 の原文どおりだった。
- **MAX14778:** 電源を入れていないときの本文（typ で 1 µA 未満、個体によっては mA 域）は p12 の原文どおりだった。
- **PhotoMOS:** オン抵抗・漏れ・出力容量（TLP241A だけが表値、ほかはグラフ）・LED 電流は、4 品とも値・条件・列が一致した。
- **リレー:** AZ850 の抵抗値（178 / 250 / 125 Ω）と、そこから計算した電流・電力は正しい。DS の「感動電圧での電力」の下限（79 / 56 / 113 mW）は 3.75² を 178 / 250 / 125 Ω で割った値と一致するので、**P2 の 125 Ω は 1 コイルあたりと読むのが DS の中で整合する**（補足）。G6K の最小セット/リセット信号幅 10 ms、TQ の「10 ms 以上を推奨」、TQ の「セットとリセットのコイルに同時に電圧を加えないこと」、G6K・TQ の「リセット位置で出荷、衝撃で変わりうる、初期化せよ」、接点材質、最小開閉負荷、外形は一致した。

### 誤り（7 件と条件の誤り 1 件。どれも選択を変えない）

1. **DG458 の「電荷注入 DS に無い」**（§1.7 の行と §1 末尾の箇条の 2 件）: p6 に典型値のグラフ "QINJ vs. VS"（V± = 15 V、CL = 1 nF で約 −35〜−46 pC、10 nF で約 −45〜−52 pC）がある。表値が無いのは正しい。
2. **§1 末尾「音声帯域の OFF アイソレーション … 1 kHz〜20 kHz はグラフ（ADG5412F Figure 20）だけ」**: DG458 p6 の "Off Isolation and XTALK vs. Frequency"（V± = 15 V、RL = 1 kΩ）が 10 kHz から始まっていて、10 kHz で約 −103 dB。10〜20 kHz はこのグラフにもある。
3. **§2 末尾「オン抵抗は電流 = 最大（1〜2.5 A）での 1 点だけ」**: AQW212EH は IL = Max. = 0.5 A、VO14642A の AC/DC 接続は IL = 1 A（2 A は DC 接続）なので、範囲は 0.5〜2.5 A。また、原点を通る出力の I–V グラフ（AQV252G 図 8、AQW212EH 図 8-1〜8-3、TLP241A Fig. 14.4）がある。直線性や歪みの規定値が無いのは正しい。
4. **G5V-2 の「バウンス時間 DS に無い」**: p3 に "Distribution of Bounce Time"（非ラッチ、Standard / High-sensitivity、各 50 個）がある。
5. **FTR-B3 の「バウンス時間 DS に無い」**: p6 REFERENCE DATA に "Distribution of Bounce Time"（試料 FBR-B3GA4.5Z = 標準型（非ラッチ）、N = 100）がある。
6. **§3 末尾「値として出ているのは G6K の非ラッチ試料のヒストグラムだけ」**: 4・5 のとおり G5V-2 と FTR-B3 にも非ラッチのヒストグラムがある。「ラッチ型のバウンス時間はどの DS にも無い」という前半は正しい。
7. （条件の誤り）**HI-548 の rON の Note 2**: DS は「VOUT = ±10V, IOUT = ∓100µA」。boundary.md は符号が落ちて「VOUT = 10 V、IOUT = 100 µA」になっている（pdftotext が ± を落とす。Note 4 の「±33V」も同じ）。

「誤り」のうち 1・2・4・5・6 は「DS に無い」という主張で、DS にあったもの。

凡例: 「同上」は「boundary.md の値・列・条件・ページのとおり」という意味。引用は DS の画像から読んだ原文。「私の読み」はこの照合で読んだグラフの値。

---

## 0. 取得した DS と版

| 部品 | 項目 | boundary.md の値 | 判定 | DS の実際 | 根拠（原文の引用） |
|---|---|---|---|---|---|
| TMUX4821 | 版・ページ数・同一文書 | SCDS487A – OCTOBER 2025 – REVISED DECEMBER 2025、37 p、TMUX4819 と同一文書 | 一致・補足あり | 各ページの見出しと `pdfinfo`（37 p）どおり。**補足:** `tmux4819.pdf` が手元に無いのでバイト一致は確かめていない。前の作業が scratchpad に残した `TI_TMUX4819.txt` と `TI_TMUX4821.txt` は中身が一致した | "SCDS487A – OCTOBER 2025 – REVISED DECEMBER 2025" |
| TMUX7412F | 版・ページ数・同一文書 | SCDS404B – MARCH 2021 – REVISED NOVEMBER 2022、48 p、7411F / 7413F と同一文書 | 一致・補足あり | 同上（48 p）。**補足:** PDF は 1 本だけ。scratchpad に残る 7411F / 7412F / 7413F の抽出テキストは 3 本とも一致した | "SCDS404B – MARCH 2021 – REVISED NOVEMBER 2022" |
| TMUX7462F | 版・ページ数 | SCDS394B – MARCH 2021 – REVISED JUNE 2023、43 p | 一致 | 同上 | "SCDS394B – MARCH 2021 – REVISED JUNE 2023" |
| ADG5412F | 版・ページ数・作成ソフト | Rev. B（"1/16—Rev. A to Rev. B"）、28 p、Creator: PDFium | 一致 | 改版履歴・ページ下端・`pdfinfo` どおり（Creator / Producer とも PDFium） | "Rev. B \| Page 3 of 28" / "1/16—Rev. A to Rev. B" |
| ADG5412BF | 同上 | Rev. B、28 p | 一致 | 同上 | "1/16—Rev. A to Rev. B" |
| DG458 | 版・ページ数 | Document Number: 70064, S11-1029–Rev. H, 23-May-11、10 p | 一致 | 各ページの下端 | "S11-1029–Rev. H, 23-May-11" |
| HI-546〜549 | 版・ページ数 | FN3150 Rev 7.00, Jun 15, 2016、25 p | 一致 | p1 右上と各ページの下端 | "FN3150 Rev 7.00 Jun 15, 2016" |
| AQV252G | 版・ページ数 | ASCTB144E 202204、15 p | 一致 | 各ページの下端 | "ASCTB144E 202204" |
| TLP241A | 版・ページ数 | Rev.5.0, 2018-01-30、18 p | 一致 | 各ページの右下 | "2018-01-30 Rev.5.0" |
| VO14642A | 版・ページ数 | Rev. 1.8, 21-Aug-2023, Document Number: 81646、11 p | 一致 | 各ページの下端 | "Rev. 1.8, 21-Aug-2023 ... Document Number: 81646" |
| G6K | 版・ページ数 | Cat. No. K106-E1-11、10 p | 一致 | p10 の下端 | "Cat. No. K106-E1-11" |
| G5V-2 | 版・ページ数 | Cat. No. K046-E1-06、4 p | 一致 | p4 の下端 | "Cat. No. K046-E1-06" |
| TQ | 版・ページ数・メタデータ・暗号化 | ASCTB14E 202507、22 p、"Issued Date: July 10,2025"、AES 暗号化 | 一致・補足あり | `pdfinfo` で Keywords "Issued Date: July 10,2025"、"Encrypted: yes (... algorithm:AES)"。**補足:** PDF p18〜p21 は下端が **"ASCTB414E 202408"** で、TQ 本体ではなく汎用の "GUIDELINES FOR SIGNAL RELAYS USAGE" が綴じ込まれている（§3.3 の p18 を引いた行に効く） | "ASCTB14E 202507"（p2〜p17）/ "ASCTB414E 202408"（p18〜p21） |
| FTR-B3 | 版・ページ数 | "Rev. 03/2002"、10 p | 一致 | 最終ページ | "© 2002 Fujitsu Components America, Inc. ... Rev. 03/2002" |
| 既存 4 本 | 版 | TMUX7612 SCDS466A、MAX14778 19-5929; Rev 3; 7/20、AQW212EH ASCTB53J 202601、AZ850 2019-03-26 | 一致 | 各 DS の表紙・下端どおり | "SCDS466A – AUGUST 2023 – REVISED DECEMBER 2024" / "19-5929; Rev 3; 7/20" / "ASCTB53J 202601" / "page 2 of 2 2019-03-26" |
| MAX4533 | 取れなかった | — | 確かめられず | DS が手元に無い | — |

## 1. アナログスイッチ

| 部品 | 項目 | boundary.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| （総論 §1.0） | 電源断時の漏れの試験条件 | どれも ±15〜±60 V の大きな電圧で、±9 Vpk 程度で規定したものは無い（例外は DG458 のグラフ） | 一致 | TMUX4821 ±15 V、TMUX741xF / 7462F ±60 V、ADG5412F/BF ±55 V、DG458 ±25 V。MAX14778 の本文は電圧を書いていない。HI-548 は表値が無い | 各行を参照 |
| TMUX7612 | 電源断時の漏れ・Hi-Z の規定 | DS に無い | 一致 | boundary.md のキーワードに加え、absent / removed / no supply / power loss / power down / isolat でも全文を探した。該当は §7.3.5 と絶対最大の注だけ。"floating" は N.C. ピンと漏れ測定条件の注だけ | "N.C. ... Can be shorted to GND or left floating" / "When VS is at a voltage potential, VD is floating, ..." |
| TMUX7612 | 電源シーケンス | 任意の順 | 一致 | p28 §7.3.5 | "The TMUX7612 supports any power up sequencing. ... when powering down the supply rails can be powered down in any order." |
| TMUX7612 | 端子のクランプ | 注(3) ダイオードクランプ | 一致・補足あり | p4 §5.1。**補足:** 注(3) が付いているのは "IIK Diode clamp current" の行で、VS/VD の行ではない（内容は boundary.md のとおり） | "IIK Diode clamp current(3) –30 30 mA" / "(3) Pins are diode-clamped to the power-supply rails." |
| TMUX7612 | 絶対最大 VS/VD | VSS–0.5 / VDD+0.5 | 一致 | p4 MIN / MAX 列 | "VS or VD Source or drain voltage (Sx, Dx) VSS–0.5 VDD+0.5 V" |
| TMUX4821 | 構成 | 4821 = SPST × 2、4819 = SPDT × 1 | 一致 | p1 Description | 同上 |
| TMUX4821 | パッケージ | DSG (SON, 8) 2 mm × 2 mm | 一致 | p1 Package Information | "DSG (SON, 8) 2mm × 2mm" |
| TMUX4821 | 推奨 VDD | 1.8 / 5.5 V | 一致 | p5 §8 MIN / MAX 列 | "VDD Positive power supply voltage 1.8 5.5 V" |
| TMUX4821 | 推奨 VS/VD | −15 / 15 V | 一致 | 同上 | "VS or VD Signal path input/output voltage (source or drain pin) (Sx, D) -15 15 V" |
| TMUX4821 | 推奨 VSEL | 0 / 5.5 V | 一致 | 同上 | "VSEL Address/Select pin voltage 0 5.5 V" |
| TMUX4821 | 絶対最大 VDD | −0.5 / 6 V | 一致 | p3 §5 | "VDD to GND Supply voltage -0.5 6 V" |
| TMUX4821 | 絶対最大 VS/VD 対 GND | −17 / 17 V | 一致 | 同上 | "Source or drain voltage (Sx, Dx) to ground -17 17 V" |
| TMUX4821 | 絶対最大 同一 ch | −18 / 18 V、注(4) | 一致 | 同上。注(4) は p4 | "(4) Maximum voltage between source and drain pins within the same channel. For example: S1A to D1 or S1A to S1B" |
| TMUX4821 | 絶対最大 別 ch | −24 / 24 V、注(3) | 一致 | 同上 | "Source to drain or source (seperate channel)(3) -24 24 V" |
| TMUX4821 | 注(3) | ダイオードクランプ | 一致 | p4 | "(3) Pins are diode-clamped to the power-supply rails. Over voltage signals must be voltage and current limited to maximum ratings." |
| TMUX4821 | IDC | 1.1 / 0.87 / 0.27 A、VDD = 3.3 V | 一致 | p5 §9 | "DSG 1.1 0.87 0.27 A" |
| TMUX4821 | **IS(POFF)** | 0.02 µA（25°C、typ だけ）、±0.1 / ±2 µA（min / max）、VDD = 0 V、VS = ±15 V / 0 V、VD = 0 V / ±15 V、注(1) | 一致 | p6 §11。25°C 行は TYP 列だけ、温度行は MIN / MAX 列。注(1) は p7 | "(1) When VS is at a voltage potential, VD is 0 V, or when VS is 0 V, VD is at a voltage potential." |
| TMUX4821 | **ID(POFF)** | 同上 | 一致 | 同上 | "ID(POFF) Drain powered-off leakage current(1) VDD = 0 V ..." |
| TMUX4821 | 真理値（VDD = 0） | 全 ch OFF（Hi-Z）、power-off protection | 一致 | p21 Table 15-1 / 15-2 | "0 X(1) All channels are off (Hi-Z). Device is in power-off protection." |
| TMUX4821 | 本文 §15.3.3 | S/D を高インピーダンスで切り離す | 一致 | p22 | "... isolates the source (Sx) and drain (Dx) pins when the supply is removed (Vdd = 0V)." |
| TMUX4821 | 本文（保護が無い場合） | ESD ダイオード経由で逆給電 | 一致 | p1 §3 | "Without this protection feature, any voltage on the switch can back-power the supply rail through an internal ESD diode ..." |
| TMUX4821 | フェイルセーフ論理 | VDD = 0 V で SEL 5.5 V まで、負は保護なし | 一致 | p22 §15.3.6 | 同上 |
| TMUX4821 | プルダウン | 約 6 MΩ | 一致 | p22 §15.3.5 | "The value of this pull-down resistor is approximately 6MΩ." |
| TMUX4821 | 応用例 §16.2.1 | GPIO で電源を切ると高電圧は出力へ伝わらない | 一致・補足あり | p23。**補足:** §16 の冒頭（p23）に「この節は TI の部品仕様ではない」とある。規定値ではなく説明文 | "Information in the following applications sections is not part of the TI component specification, and TI does not warrant its accuracy or completeness." |
| TMUX4821 | RON | 0.16 / 0.20 Ω（25°C）、0.225 / 0.3 Ω、VDD = 2.5〜5.5 V | 一致 | p6 §11。25°C は TYP / MAX、温度行は MAX。VDD = 1.8〜2.5 V の行（0.16 / 0.25、0.26 / 0.3 Ω）もある | "VDD = 2.5 V to 5.5 V VS = –15 V to +15 V ID = –100 mA 25°C 0.16 0.20" |
| TMUX4821 | RON FLAT | 0.0001 / 0.01 Ω（25°C）、0.05 / 0.07 Ω | 一致・補足あり | p6。**補足（DS 内の食い違い）:** p1 は "1mΩ RON-flatness" と書くが、表の typ は 0.0001 Ω（0.1 mΩ） | "RON FLAT ... 25°C 0.0001 0.01" / "With 0.001% THD+N and 1mΩ RON-flatness" |
| TMUX4821 | ΔRON | 0.0008 / 0.03 Ω | 一致 | p6 | 同上 |
| TMUX4821 | IS(OFF) | 0.001 µA、±0.1 / ±1 µA | 一致 | p6 | 同上 |
| TMUX4821 | IDD | 55 / 125 µA | 一致 | p7 | "Logic inputs = 0 V, 5 V, or VDD 25°C 55 125 µA" |
| TMUX4821 | **OISO** | −50 dB、RL = 50 Ω、CL = 5 pF、200 mVRMS、f = 100 kHz、typ | 一致 | p8 §12 TYP 列 | "RL = 50 Ω , CL = 5 pF VS = 200 mVRMS, VBIAS = 0 V, f = 100 kHz 25°C -50 dB" |
| TMUX4821 | XTALK | −100 dB（4821）/ −55 dB（4819） | 一致 | p8 | 同上 |
| TMUX4821 | **CS(OFF)** | 70 pF、VS = 0 V、1 MHz | 一致 | p8 TYP 列 | "CS(OFF) Source off capacitance VS = 0 V, f = 1 MHz 25°C 70 pF" |
| TMUX4821 | CS(ON), CD(ON) | 40 pF | 一致 | p8 | 同上 |
| TMUX4821 | CD(OFF) | DS に無い | 一致 | 表に行が無い。全文にも "CD(OFF)" "drain off capacitance" は無い | — |
| TMUX4821 | QINJ | 5 pC | 一致 | p8 | "QINJ Charge injection VS = 0 V, CL = 100 pF 25°C 5 pC" |
| TMUX4821 | tON / tOFF | 155 / 300 µs、14 µs | 一致 | p8 | 同上 |
| TMUX4821 | tON(VDD) | 175 µs | 一致 | p8 | 同上 |
| TMUX4821 | ACPSRR | −100 dB | 一致 | p8 | 同上 |
| TMUX4821 | **THD+N（表）600 Ω** | −107 / −105 dB、**VPP = 0.5 V** | 一致 | p9 §12 TYP 列。条件は VPP = 0.5 V だけ | "VPP = 0.5 V, VBIAS = 0 V RL = 600 Ω f = 20 Hz to 20 kHz 25°C -107" |
| TMUX4821 | THD+N（表）32 Ω | −102 dB | 一致 | p9 | 同上 |
| TMUX4821 | THD+N（Features） | 0.001 %（−100 dB）、条件なし | 一致 | p1 | "Low THD+N: 0.001% (-100dB)" |
| TMUX4821 | Figure 13-16 | 15 Vpp: 約 −125〜−118 dB、0.5 Vpp: 約 −107 dB | 一致 | p12。私の読み: 15 Vpp は 20〜200 Hz で約 −124 dB、それより上で約 −120〜−117 dB。0.5 Vpp は約 −106〜−107 dB | 図下 "VDD = 3.3V, RLOAD = 600Ω, TA = 25°C" |
| TMUX4821 | Figure 13-18 | 0.5 V で約 0.00058 %、15 V で約 0.00018 % | 一致 | p12 | 凡例 "1kHz, 32 Ω"、横軸 "Source Voltage (V)" |
| TMUX4821 | **Figure 13-21** | 推奨領域の上限: 13 Vpp まで約 1 MHz、15 Vpp 約 40 kHz、17 Vpp 約 19 kHz、18 Vpp 約 15 kHz、19 Vpp 約 13 kHz、29 Vpp 約 4.5 kHz。No Operation Region は 18 Vpp で約 16 kHz 以上。VDD = 5V | 一致・補足あり | p13。軸ラベルの座標で較正（1 桁 = 32 pt）し、576 dpi 相当で色境界を拾った。**私の読み（推奨領域の上限）:** 13 Vpp まで 1 MHz、14 Vpp 約 98 kHz、15 Vpp 約 37 kHz、16 Vpp 約 23 kHz、17 Vpp 約 18.5 kHz、**18 Vpp 約 14.7 kHz**、19 Vpp 約 12.3 kHz、20 Vpp 約 10.5 kHz、29 Vpp 約 4.7 kHz。**No Operation の下端:** 15 Vpp 約 55 kHz、17 Vpp 約 21 kHz、**18 Vpp 約 16.5 kHz**、29 Vpp 約 5.7 kHz。**補足:** 20 kHz で推奨領域に入る振幅は約 16.7 Vpp まで（計算ではなく図の読み） | 凡例 "No Operation Region / >-100dB Operation Region / Recommended Operation Region"、図下 "VDD = 5V" |
| TMUX4821 | Figure 13-21 の説明文 | DS に無い | 一致 | "Stopping" は図の縦軸ラベルだけ、"13-21" は図題だけ | — |
| TMUX741xF | 構成 | 7411F logic low、7412F logic high、7413F 混在 | 一致 | p3 Device Comparison Table | "TMUX7412F ±60 V fault-protected, latch-up immune, quad SPST switch (logic high)" |
| TMUX741xF | パッケージ | PW (TSSOP, 16) 5.00 × 4.40（Preview）、RRP 4.00 × 4.00 | 一致 | p1 | "PW (TSSOP, 16) (2) 5.00 mm × 4.40 mm" / "(2) Preview package." |
| TMUX741xF | 電源範囲（Features） | 単 8〜44 V、両 ±5〜±22 V | 一致 | p1 | "Single supply: 8 V to 44 V – Dual supply: ±5 V to ±22 V" |
| TMUX741xF | 推奨 VDD – VSS | 8 / 44 V | 一致 | p5 §7.4 | "VDD – VSS (1) Power supply voltage differential 8 44" |
| TMUX741xF | 推奨 VS（非 fault） | VSS / VDD | 一致 | p5 | 同上 |
| TMUX741xF | 推奨 VS（fault） | −60 / 60 V 対 GND | 一致 | p5 | "VS to GND Source pin (Sx) voltage to GND (fault condition) –60 60" |
| TMUX741xF | **推奨 VD** | VSS / VDD | 一致 | p5 | "VD Drain pin (Dx) voltage VSS VDD" |
| TMUX741xF | 絶対最大 VS 対 GND | −65 / 65 V | 一致 | p4 | 同上 |
| TMUX741xF | **絶対最大 VD** | VSS−0.7 / VDD+0.7 V | 一致 | p4 | "VD Drain pin (Dx) voltage VSS–0.7 VDD+0.7 V" |
| TMUX741xF | IDC（WQFN） | 150 / 100 / 60 mA、max | 一致 | p5 MAX 列 | 同上 |
| TMUX741xF | VT | 0.7 V typ | 一致 | p6 | "VT Threshold voltage for fault detector 25°C 0.7 V" |
| TMUX741xF | UVLO | 5.1 / 5.8 / 6.4 V、5 / 5.7 / 6.3 V | 一致 | p6 | 同上 |
| TMUX741xF | **IS(FA) Grounded** | ±125 µA、VS = ±60 V、VDD = VSS = 0 V、typ | 一致 | p7 §7.6。値は TYP 列（MIN / MAX 空欄）、TA は −40〜+125°C の 1 行だけ | "IS(FA) Grounded ... VS = ± 60 V, GND = 0 V VDD = VSS = 0 V –40°C to +125°C ±125 µA" |
| TMUX741xF | IS(FA) Floating | ±125 µA typ | 一致 | 同上 | 同上 |
| TMUX741xF | IS(FA)（電源あり） | ±100 µA typ | 一致 | p7 | 同上 |
| TMUX741xF | **ID(FA) Grounded** | ±0.01 typ、±30 / ±50 / ±90 nA | 一致 | p7。25°C は MIN / TYP / MAX、温度行は MIN / MAX | "25°C –30 ±0.01 30 ... –50 50 ... –90 90 nA" |
| TMUX741xF | ID(FA) Floating | ±2 / ±3 / ±4 µA typ | 一致 | p7 TYP 列 | 同上 |
| TMUX741xF | 電源断・±9〜±15 V での漏れ | DS に無い | 一致 | 表は VS = ±60 V だけ。Figure 7-19〜7-23 はどれも電源あり | — |
| TMUX741xF | Figure 7-23 | +30 V 約 +27 µA、−30 V 約 −33〜−38、+60 V 約 +78〜+88、−60 V 約 −85〜−100 µA、電源 ±15 V | 一致 | p20（私の読み: +30 V は +25→+28、−60 V は −86→−100 µA） | 図下 "±15 V Dual Supply" |
| TMUX741xF | 本文 §9.3.2.2 | 電源を外すと source は Hi-Z、GND 基準必要、±60 V 遮断 | 一致 | p33 | "Source and drain voltage levels of up to ±60 V are blocked in the powered-off condition." |
| TMUX741xF | 本文 §9.3.2.5 | drain は電源へ ESD ダイオード、source は ±60 V 可 | 一致 | p33 | "The drain pins (Dx) have internal ESD protection diodes to the supplies VDD and VSS, therefore the voltage at the drain pins must not exceed the supply voltages ..." |
| TMUX741xF | **DS 内の食い違い** | §9.3.2.2 と §9.3.2.5・絶対最大の食い違い | 一致・補足あり | 原文どおり。**補足:** p1 Description は "The devices block fault voltages up to +60 V or −60 V relative to ground in powered and powered-off conditions" と端子を書かずに言っている。また、電源断時は VDD = VSS = 0 V なので、絶対最大の VD は −0.7〜+0.7 V になる | p33 / p4 / p1 |
| TMUX741xF | 電源なし時の論理 | ch は OFF、論理入力は無視 | 一致 | p1 | 同上 |
| TMUX741xF | フェイルセーフ論理 | +44 V まで、負は保護なし | 一致 | p33 §9.3.2.3 | 同上 |
| TMUX741xF | RON | 8.3 / 11、14、16.5 Ω | 一致 | p7 | 同上 |
| TMUX741xF | RFLAT | 0.01 / 0.4、0.4、0.4 Ω | 一致 | p7 | 同上 |
| TMUX741xF | IS(OFF) / ID(OFF) | 0.03、±0.7、±2、±10 / ±12 nA | 一致 | p7（IS は ±10、ID は ±12 nA） | 同上 |
| TMUX741xF | THD+N | 0.0006 %、VS = 15 VPP、RL = 10 kΩ | 一致 | p8 | 同上 |
| TMUX741xF | OISO | −60 dB、f = 1 MHz | 一致 | p8 | 同上 |
| TMUX741xF | Figure 7-29 | 100 kHz 付近で約 −80〜−90 dB | 一致・補足あり | p21。**私の読み:** 左端の 100 kHz では約 −95〜−100 dB（ノイズで揺れる）。−80〜−90 dB になるのは約 150〜300 kHz。boundary.md の値は安全側（悪い側）に寄っている | 図題 "Crosstalk and Off Isolation vs Frequency" |
| TMUX741xF | XTALK | −100 dB | 一致 | p8 | 同上 |
| TMUX741xF | CS(OFF) / CD(OFF) / CON | 10 / 12 / 14 pF | 一致 | p8 | 同上 |
| TMUX741xF | QJ | −300 pC | 一致 | p8 | 同上 |
| TMUX741xF | tON / tOFF | 480 / 680、50 / 100 ns | 一致 | p8 | 同上 |
| TMUX741xF | IDD / ISS | 0.32 / 0.5、0.26 / 0.4 mA | 一致 | p8 | 同上 |
| TMUX7462F | 構成 | 選択ピン不要の 4 ch プロテクタ | 一致 | p1 | "Channel protector without need for dedicated select pin per channel" |
| TMUX7462F | パッケージ | PW 5 × 6.4、RRP 4 × 4 mm | 一致 | p1 | 同上 |
| TMUX7462F | ON の条件 | VDD – VSS ≥ 8 V ほか | 一致 | p28 §8.4.1 | 同上 |
| TMUX7462F | 電源断時（本文） | 0 V・浮き・UV 未満で source は Hi-Z | 一致 | p26 §8.3.2.2 | 同上 |
| TMUX7462F | **IS(FA) Grounded** | ±135 µA typ | 一致 | p6 §6.6 TYP 列 | "VDD = VSS = VFP = VFN= 0 V –40°C to +125°C ±135 µA" |
| TMUX7462F | IS(FA) Floating | ±140 µA typ | 一致 | p6 | 同上 |
| TMUX7462F | **ID(FA) Grounded** | ±0.01、±30 / ±50 / ±90 nA | 一致 | p6 | 同上 |
| TMUX7462F | ID(FA) Floating | ±0.6 / ±1.2 / ±2.2 µA | 一致 | p6 TYP 列 | 同上 |
| TMUX7462F | drain 側の保護 | 無し、常に VFP〜VFN | 一致 | p28 §8.4.2 | "The overvoltage protection is provided only for the source (Sx) input pins. ..." |
| TMUX7462F | 絶対最大 VD | VFN−0.7 / VFP+0.7 V | 一致 | p4 | 同上 |
| TMUX7462F | RON | 8.3 / 10.7、13.5、16 Ω | 一致 | p6 | 同上 |
| TMUX7462F | RFLAT | 0.005 / 0.4 Ω | 一致 | p6 | 同上 |
| TMUX7462F | THD+N | 0.0006 %、15 VPP | 一致 | p7 | 同上 |
| TMUX7462F | CS(ON), CD(ON) | 14 pF | 一致 | p7 | 同上 |
| TMUX7462F | OISO・OFF 容量 | DS に無い | 一致 | p6〜p7 に行が無い。全文に "Off-isolation" "OISO" "off-capacitance" は無い | — |
| TMUX7462F | IDD / ISS | 0.32 / 0.5、0.26 / 0.4 mA | 一致 | p7 | 同上 |
| ADG5412F | 構成 | 5412F は Logic 1 で全 ON、5413F は 2 / 2 | 一致 | p1 | 同上 |
| ADG5412F | パッケージ | 16-Lead TSSOP / LFCSP | 一致 | p12 Table 6 | "16-Lead TSSOP (4-Layer Board) 112.6°C/W" |
| ADG5412F | 電源範囲 | ±5〜±22 V、8〜44 V | 一致 | p1 | 同上 |
| ADG5412F | 信号範囲 | VDD to VSS（−40〜+125°C 列） | 一致 | p3 Table 1 | 同上 |
| ADG5412F | Features | ±55 V まで電源断保護 | 一致 | p1 | "Power-off protection up to −55 V and +55 V" |
| ADG5412F | **Source Leakage, Grounded or Floating** | ±40 µA、"µA typ"、−40〜+125°C 列だけ、VS = ±55 V | 一致 | p3。+25°C・−40〜+85°C 列は空欄 | "Power Supplies Grounded or Floating ±40 µA typ VDD = 0 V or floating, ..." |
| ADG5412F | Source Leakage, With Overvoltage | ±78 µA typ、"VSS = 16.5 V"（原文の符号のまま） | 一致 | p3。画像でも "VSS = 16.5 V" | 同上 |
| ADG5412F | **Drain Leakage, Grounded** | ±10 nA typ、±30 / ±50 / ±100 nA max | 一致 | p3。typ 行は +25°C 列だけ | 同上 |
| ADG5412F | Drain Leakage, Floating | ±10 µA typ（3 列） | 一致 | p3 | 同上 |
| ADG5412F | 電源断・±9〜±15 V | DS に無い | 一致 | 表は ±55 V だけ。Figure 38 も ±55 V の条件を指す | — |
| ADG5412F | 本文（Power-Off Protection） | OFF、入力は高インピーダンス、出力は仮想開放、GND 基準必要 | 一致・補足あり | p26。**補足:** 同じ段落の最後に「±55 V までの信号は電源断時に遮断」とあり、端子を書いていない（TMUX741xF と同じあいまいさ。drain は p25 で電源を超えてはならないとしている） | "Signal levels of up to ±55 V are blocked in the unpowered condition." |
| ADG5412F | 本文（ESD） | drain は電源へダイオード | 一致 | p25 | "The drain pins have ESD protection diodes to the rails and the voltage at these pins must not exceed supply voltage." |
| ADG5412F | 絶対最大 Dx | VSS − 0.7〜VDD + 0.7 V または 30 mA | 一致 | p12 Table 6、注 1 | "Overvoltages at the Dx pins are clamped by internal diodes." |
| ADG5412F | BF 版の案内 | 両側保護のピン互換品 | 一致 | p25 | 同上 |
| ADG5412F | **RON（±9 V）** | 9.5 Ω typ、10.7 / 13.5 / 16 Ω max、節見出し VDD = 13.5 V、VSS = −13.5 V | 一致 | p3。typ 行と max 行 | "9.5 Ω typ VS = ±9 V, IS = −10 mA / 10.7 13.5 16 Ω max" |
| ADG5412F | RON（±10 V） | 10 / 11.2 / 14 / 16.5 Ω | 一致 | p3 | 同上 |
| ADG5412F | RFLAT（±9 V） | 0.1、0.4 / 0.5 / 0.5 Ω | 一致 | p3 | 同上 |
| ADG5412F | RFLAT（±10 V） | 0.6、0.9 / 1.1 / 1.1 Ω | 一致 | p3 | 同上 |
| ADG5412F | IS(Off) / ID(Off) | ±0.1、±1.5 / ±5.0 / ±21（ID ±18）nA | 一致 | p3 | 同上 |
| ADG5412F | **THD+N** | 0.0015 %、RL = 10 kΩ、15 V p-p | 一致・補足あり | p4 +25°C 列。**補足:** DYNAMIC CHARACTERISTICS 全体に注 1 が付いている（QINJ・Off Isolation も同じ） | "1 Guaranteed by design; not subject to production test." |
| ADG5412F | Figure 25 | 15 V p-p で約 0.0015 % | 一致 | p17（私の読みは約 0.0012〜0.0015 %） | 凡例 "VDD = 15V, VSS = −15V, VS = 15V p-p" |
| ADG5412F | Off Isolation | −70 dB、1 MHz | 一致 | p4 | 同上 |
| ADG5412F | Figure 20 | 1〜10 kHz 約 −110 dB、100 kHz 約 −100 dB | 一致 | p16（私の読みは 100 kHz で約 −95 dB） | 図中 "VDD = +15V VSS = −15V TA = 25°C" |
| ADG5412F | CS(Off) / CD(Off) / CON | 13 / 12 / 24 pF | 一致 | p4 | 同上 |
| ADG5412F | **QINJ** | −680 pC、VS = 0 V、RS = 0 Ω、CL = 1 nF | 一致 | p4 | "Charge Injection, QINJ −680 pC typ VS = 0 V, RS = 0 Ω, CL = 1 nF" |
| ADG5412F | tON / tOFF | 400 / 495、410 / 510 ns | 一致 | p4 | 同上 |
| ADG5412F | IDD / ISS | 0.9 / 1.2、0.5 / 0.65 mA | 一致 | p4 | 同上 |
| ADG5412F | Figure 31 | ±10 V で 1〜約 3 MHz は 20 V p-p まで | 一致 | p18 | 図中 "DISTORTIONLESS OPERATING REGION" |
| ADG5412BF | 同じ値の範囲（節の前書き） | RON・RFLAT・THD+N・容量・QINJ・時間・Off Isolation が同じ | 一致 | BF の p3〜p4 の画像で 1 行ずつ突き合わせた。違うのは漏れの行と ISS の単位だけ | — |
| ADG5412BF | 保護対象 | source と drain | 一致 | p1 | "Switch pins are protected against voltages between −55 V and +55 V, in an unpowered state." |
| ADG5412BF | 絶対最大 Sx and Dx | −55〜+55 V | 一致 | p12 | "Sx and Dx −55 V to +55 V" |
| ADG5412BF | ESD | 3 kV（5412F は 5.5 kV） | 一致 | p12（I/O port は BF も 5.5 kV）。F の p12 は All Other Pins 5.5 kV | "All Other Pins 3 kV" |
| ADG5412BF | **Input Leakage, Grounded or Floating** | ±40 µA typ、VS or VD = ±55 V | 一致 | p3、−40〜+125°C 列だけ | 同上 |
| ADG5412BF | **Output Leakage, Grounded** | ±10 nA typ、±30 / ±50 / ±100 nA | 一致 | p3 | 同上 |
| ADG5412BF | Output Leakage, Floating | ±10 µA typ | 一致 | p3 | 同上 |
| ADG5412BF | Output Leakage, With Overvoltage | ±20、±200 / ±250 / ±250 nA | 一致 | p3 | 同上 |
| ADG5412BF | IS(Off) / ID(Off) | ±1.5 / ±5.5 / ±24（ID ±20）nA | 一致 | p3 | 同上 |
| ADG5412BF | 本文 | 5412F と同文 | 一致 | p26 | 同上 |
| ADG5412BF | ISS max の単位 | "0.7 μA max" | 一致 | p4 の画像でも "µA max" | "0.65 0.7 μA max" |
| DG458 | 構成 | n-p-n 直列 MOSFET | 一致 | p1 | 同上 |
| DG458 | パッケージ | 16-pin Plastic DIP | 一致 | p2 | 同上 |
| DG458 | 電源範囲 | ±4.5 / ±18 V | 一致 | p4 | 同上 |
| DG458 | 信号範囲 | −10 / 10 V（A・D） | 一致 | p3。注 e（設計保証）付き | "Analog Signal Range(e) VANALOG Full - 10 10 - 10 10 V" |
| DG458 | 絶対最大 電源断時 | −35〜+35 V | 一致 | p2 | "VS, Analog Input Overvoltage with Power Off - 35 to + 35" |
| DG458 | **Input Leakage (Power Supplies Off)** | 0.001 µA typ、±2 µA（A）/ ±5 µA（D）、VS = ±25 V、VSUPS = 0 V、Room | 一致 | p3。Typ 列、A / D の Min / Max 列 | "Input Leakage Current (with Power Supplies Off) VS = ± 25 V, VSUPS = 0 V VD = A0, A1, A2, EN = 0 V Room 0.001 - 2 2 - 5 5 µA" |
| DG458 | **Input Leakage vs. Input Voltage** | V+ = V− = 0 V：−10 V 約 7 pA、−30 V 約 15 pA、+10 V 約 2 pA、+30 V 約 4 pA、約 −45 V より負で急増 | 一致・補足あり | p5 左上。軸ラベルで較正（1 pA〜1 mA、1 桁 = 68 px、1000 dpi 相当）して画素で読んだ。**私の読み:** −10 V 約 5.5 pA、−15 V 約 6 pA、−25 V 約 7.6 pA、**−30 V 約 10 pA**、−35 V 約 15 pA、+10 V 約 2.0 pA、+20 V 約 2.5 pA、+30 V 約 3.1 pA。−45 V より負で急増するのは同じ。boundary.md の −30 V は私の読みの 1.5 倍（対数目盛りで 0.2 桁）。**図には ±35 V の破線で "Operating Range" が描いてある** | 図題 "Input Leakage vs. Input Voltage"、図中 "V+ = V- = 0 V" |
| DG458 | 本文 | 電源喪失時の負荷は無視できる | 一致 | p9 | 同上 |
| DG458 | RDS(on) ±5 V | 180 / 400 Ω | 一致 | p3 | 同上 |
| DG458 | **RDS(on) ±9.5 V** | 0.45 kΩ typ、1.2 kΩ（A Room）/ 1.5 kΩ（D Room） | 一致 | p3。Full は A 1.5 / D 1.8 kΩ | "VD = ± 9.5 V, IS = - 400 µA Room 0.45 1.2 ... 1.5 kΩ" |
| DG458 | 注 g | +13.5 V / −12 V を超えると RDS(on) が上がる | 一致 | p4 | 同上 |
| DG458 | OIRR | 90 dB、100 kHz | 一致 | p4 | 同上 |
| DG458 | CS(off) / CD(off) / CD(on) | 5 / 15 / 40 pF | 一致 | p4 | 同上 |
| DG458 | THD、電荷注入 | DS に無い | **誤り** | THD は無い。**電荷注入は p6 に典型値のグラフ "QINJ vs. VS"（V+ = 15 V、V− = −15 V）がある。** 私の読み: CL = 1 nF で約 −38 pC（VS = −10 V）、約 −45 pC（−5〜0 V）、約 −35 pC（+10 V）。CL = 10 nF で約 −50〜−52 pC（−10〜−5 V）、約 −45 pC（+10 V）。表値は無い | 図題 "QINJ vs. VS"、凡例 "CL = 1 nF / CL = 10 nF" |
| DG458 | I+ | 0.05 / 0.1 mA | 一致 | p4 | 同上 |
| HI-548 | **電源喪失時の入力** | 各入力が 1 kΩ | 一致 | p1 | "In addition, signal sources are protected from short circuiting should multiplexer supply loss occur. Each input presents 1kΩ of resistance under this condition." |
| HI-548 | 構成 | 16 / 差動 8 / 8 / 差動 4 | 一致 | p1 | 同上 |
| HI-548 | 供給状況 | "No longer available" | 一致 | p2 | 同上 |
| HI-548 | パッケージ | CERDIP / PDIP / SOIC | 一致 | p2 | 同上 |
| HI-548 | 信号範囲 | −15 / +15 V | 一致 | p9 | 同上 |
| HI-548 | rON | 1.2 / 1.5 kΩ（−2）、1.5 / 1.8 kΩ（−5, −9）、Note 2: VOUT = 10 V、IOUT = 100 µA | **条件の誤り** | 値と列は正しい（p9。Full は 1.5 / 1.8、1.8 / 2.0 kΩ）。**Note 2 は "VOUT = ±10V, IOUT = ∓100µA"** で、boundary.md は符号が落ちている | "2. VOUT = ±10V, IOUT = ∓100µA." |
| HI-548 | Off Isolation | 50 dB min、68 dB typ、Note 6 | 一致 | p8 | "6. VEN = 0.8V, RL = 1K, CL = 15pF, VS = 7VRMS, f = 100kHz." |
| HI-548 | CS(OFF) / CD(OFF) | 10 / 25 pF | 一致 | p8 | 同上 |
| HI-548 | 電源断時の漏れの表値 | DS に無い | 一致・補足あり | 無いのは正しい。**補足:** 引用の "Analog Overvoltage = 33V" は画像では **"±33V"**。Figure 3（p11）も電源 ±15 V のときの図 | "4. Analog Overvoltage = ±33V." |
| MAX14778 | 構成・電源 | デュアル 4:1、3.0〜5.5 V、±25 V | 一致 | p1 | 同上 |
| MAX14778 | パッケージ | 20-pin TQFN 5 × 5 mm | 一致 | p1 | 同上 |
| MAX14778 | **電源断時（本文）** | typ 1 µA 未満、個体によって mA 域 | 一致 | p12 Non-Powered Condition。A_・B_ と ACOM・BCOM の両方が対象 | "When VDD = 0V, the DC input leakage current into the A_, B_, ACOM or BCOM pins will typically be below 1µA. Some devices can have a larger leakage current up to mA range due to technology spread." |
| MAX14778 | 過渡電流 | 100 nF で dv/dt ≤ 3 V/µs | 一致 | p12 | 同上 |
| MAX14778 | RON | 0.84 / 1.7、0.84 / 1.5 Ω（行を分ける条件欄は空） | 一致 | p3 | 同上 |
| MAX14778 | RFLAT(ON) | 3 mΩ | 一致 | p3 | 同上 |
| MAX14778 | THD+N | 0.003 %、RS = RL = 1 kΩ | 一致 | p4 | 同上 |
| MAX14778 | Off-Isolation | −80 dB、100 kHz | 一致 | p4 | 同上 |
| MAX14778 | CIN | 78 pF | 一致 | p4 | 同上 |
| MAX14778 | 電荷注入 | 1720 pC | 一致 | p4 | 同上 |
| MAX14778 | IDD | 2.54 / 6、4.27 / 10 mA | 一致 | p3 | 同上 |
| MAX14778 | tPOR | 404 ms | 一致 | p4 | 同上 |
| 他のスイッチ DS | 電源断時の記述 | ADG1406/1407・MAX14752/14753・DG506B/507B は該当なし | 一致 | 同じキーワードに power loss / no power / supplies removed を足して探したが 0 件 | — |

### §1 末尾「どの DS にも無かった項目」の照合

| 箇条 | 判定 | DS の実際 |
|---|---|---|
| 電源断時の漏れを ±9〜±15 V 程度で規定した表値 | 一致・補足あり | 表値が低い電圧に無いのは正しい。**補足:** 同じ箇条の中で「TMUX4821 が ±15 V」と書いており、±15 V は箇条が言う「±9〜±15 V 程度」の上端に入る。「±15 V より低い電圧では無い」と読むのが正確 |
| 電源断時の OFF アイソレーション・OFF 容量 | 一致 | どの DS にも無い |
| 電源断時に drain 側へ信号が来た場合の規定。両側保護の明記は ADG5412BF と TMUX4821 | 一致・補足あり | 正しい。**補足:** MAX14778 も本文（p12）で A_・B_ と ACOM・BCOM の両方について電源断時の ±25 V を許容すると書いている（数値は typ の文だけ） |
| 電源断時の漏れの 25°C max | 一致 | TMUX4821 は 25°C が TYP 列だけ。ADG5412F/BF の ±40 µA、TMUX741xF の ±125 µA、TMUX7462F の ±135 µA も typ だけ |
| 音声帯域の OFF アイソレーション表値。1 kHz〜20 kHz はグラフ（ADG5412F Figure 20）だけ | **誤り** | 表値がどれも 100 kHz か 1 MHz なのは正しい。**DG458 p6 の "Off Isolation and XTALK vs. Frequency"（V± = 15 V、RL = 1 kΩ）が 10 kHz から始まり、10 kHz で約 −103 dB、20 kHz で約 −97 dB（私の読み）。** 10〜20 kHz は DG458 のグラフにもある。TMUX741xF の Figure 7-29 と MAX14778 の TOC08 は 100 kHz 以上だけ |
| TMUX4821 の CD(OFF)、"Stopping Frequency" の定義 | 一致 | どちらも無い |
| DG458 の THD・電荷注入、HI-548 の電源断時漏れの表値 | **誤り** | DG458 の THD と HI-548 の表値は無い。**DG458 の電荷注入は p6 にグラフがある**（上の DG458 の行） |
| TMUX4821 の THD+N を 18 Vpp で規定した表値 | 一致 | 表は VPP = 0.5 V だけ。15 Vpp は Figure 13-16（600 Ω）と Figure 13-17（32 Ω）、振幅の依存は Figure 13-18（1 kHz、32 Ω、0.5〜15 V） |

## 2. PhotoMOS / 光半導体リレー

| 部品 | 項目 | boundary.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| （§2 冒頭） | オン抵抗の直線性・歪みを規定した DS は無い | 無い | 一致 | 規定値としては 4 品とも無い（全文に "THD" "distortion" "linear" "dB" の規定は無い）。近い情報は下の §2 末尾の表に書いた | — |
| AQV252G | 負荷電圧 | 60 V（peak AC） | 一致 | PDF p3、AQV252G (A) 列 | "Load voltage (peak AC) VL - 30 V 60 V" |
| AQV252G | 連続負荷電流 | A 2.5 / B 3.5 / C 5.0 A | 一致 | PDF p3 | 同上 |
| AQV252G | 推奨 LED 電流 | 5 / 30 mA | 一致 | PDF p4 Min. / Max. 列 | "LED current IF 5 30 mA" |
| AQV252G | 推奨 負荷電圧 | 48 V | 一致 | PDF p4 | 同上 |
| AQV252G | IFon | 0.5 mA typ、3 mA max、IL = 100 mA | 一致 | PDF p3。3 mA は 251G・252G の結合セル | 同上 |
| AQV252G | IFoff | 0.2 mA min、0.45 mA typ | 一致 | PDF p3（結合セル） | 同上 |
| AQV252G | VF | 1.14 V typ（50 mA で 1.32 V）、1.5 V max、IF = 5 mA | 一致 | PDF p3 | 同上 |
| AQV252G | **Ron（A）** | 0.08 Ω typ、0.12 Ω max、IF = 5 mA、IL = Max.、1 秒以内 | 一致 | PDF p3、AQV252G (A) 列の Typical / Maximum 行 | "0.08 Ω / 0.12 Ω ... IF = 5 mA IL = Max. Within 1 s" |
| AQV252G | Ron（B / C） | 0.04 / 0.06、0.02 / 0.03 Ω | 一致 | PDF p3 | 同上 |
| AQV252G | **ILeak** | 1 µA max、IF = 0 mA、VL = Max. | 一致 | PDF p3（結合セル） | "Off state leakage current Maximum ILeak - 1 μA IF = 0 mA VL = Max." |
| AQV252G | 図 9 | 10 V 約 2 × 10⁻¹⁰ A、60 V 約 5 × 10⁻¹⁰ A | 一致 | PDF p5（私の読み: 1.8 × 10⁻¹⁰、5.3 × 10⁻¹⁰ A） | "Measured portion: between terminals 4 and 6; Ambient temperature: 25°C" |
| AQV252G | **出力容量の表値** | DS に無い | 一致 | PDF p3 の表は Ciso だけ | — |
| AQV252G | 図 12 | 0 V 約 230、10 V 約 100、20 V 約 80、60 V 約 55 pF | 一致 | PDF p5 | "Frequency: 1 MHz; Ambient temperature: 25°C" |
| AQV252G | Ciso | 0.8 / 1.5 pF | 一致 | PDF p3 | 同上 |
| AQV252G | Ton | 1.1 / 5.0 ms | 一致 | PDF p3 | 同上 |
| AQV252G | Toff | 0.25 / 0.5 ms | 一致 | PDF p3 | 同上 |
| AQV252G | 耐電圧 | 1,500 Vrms | 一致 | PDF p3 | 同上 |
| AQV252G | パッケージ | DIP 6、AQV252G / AQV252GA | 一致 | PDF p2 TYPES | "60 V 2.5 A AQV252G AQV252GA AQV252GAX" |


| 部品 | 項目 | boundary.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| AQW212EH | 負荷電圧 | 60 V | 一致 | PDF p3、AQW212EH (A) 列 | "負荷電圧 ( ピークAC ) VL 60 V" |
| AQW212EH | 連続負荷電流 | 0.5 A（0.6 A） | 一致 | PDF p3 | 同上 |
| AQW212EH | IFon | 1.2 / 3.0 mA、IL = Max. | 一致 | PDF p3（全品種の結合セル） | 同上 |
| AQW212EH | IFoff | 0.4 / 1.1 mA | 一致 | PDF p3 | 同上 |
| AQW212EH | **Ron** | 0.83 Ω 平均、2.5 Ω 最大、IF = 5 mA、IL = Max.、1 秒以下 | 一致 | PDF p3 | "0.83 Ω / 2.5 Ω IF = 5 mA IL = Max. 通電時間 = 1秒以下" |
| AQW212EH | **開路時漏れ** | 1 µA 最大 | 一致 | PDF p3 | 同上 |
| AQW212EH | 図 9-2 | 20 V 約 6 × 10⁻¹²、60 V 約 2 × 10⁻¹¹ A | 一致 | PDF p6（私の読み: 6.4 × 10⁻¹²、2.1 × 10⁻¹¹ A） | "測定箇所：5−6端子間、7−8端子間 測定温度：25°C" |
| AQW212EH | 出力容量の表値 | DS に無い | 一致 | PDF p3 | — |
| AQW212EH | 図 12-2 | 0 V 約 80、10 V 約 33、30 V 約 20 pF | 一致・補足あり | PDF p6。**私の読み:** 0 V 約 80、10 V 約 30、20 V 約 20、**30 V 約 15 pF**。20 pF は 30 V ではなく 20 V あたり | "周波数：1MHz 周囲温度：25°C" |
| AQW212EH | Ciso | 0.8 / 1.5 pF | 一致 | PDF p3 | 同上 |
| AQW212EH | Ton | 1 / 4 ms | 一致 | PDF p3 | 同上 |
| AQW212EH | Toff | 0.08 / 1.0 ms | 一致 | PDF p3 | 同上 |
| AQW212EH | 耐電圧 | 5,000 V rms | 一致 | PDF p3 | 同上 |
| AQW212EH | パッケージ | DIP 8、2a | 一致 | PDF p1 | "GE DIP8 2a" |
| TLP241A | 構成 | 1-Form-A、4 ピン DIP、MOSFET 2 個直列 | 一致 | p1 §3、p2 §6（ピン配置図・内部回路図） | 同上 |
| TLP241A | VOFF | 40 V | 一致 | p3 §8 | 同上 |
| TLP241A | ION | 2.0 A | 一致 | p3 §8 | 同上 |
| TLP241A | 推奨 IF | 5 / 7.5 / 25 mA | 一致 | p3 §9 | 同上 |
| TLP241A | 推奨 VDD | 32 V | 一致 | p3 §9 | 同上 |
| TLP241A | IFT | 0.5 / 3 mA、ION = 1.0 A | 一致 | p4 §11 | 同上 |
| TLP241A | IFC | 0.1 mA min、IOFF = 10 µA | 一致 | p4 §11 | 同上 |
| TLP241A | **RON** | 60 / 100 mΩ、ION = 2.0 A、IF = 5 mA、t < 1 s | 一致 | p4 §11 | 同上 |
| TLP241A | RON（連続） | 90 / 150 mΩ | 一致 | p4 §11 | "Note 1: Thermally saturated state." |
| TLP241A | **IOFF** | 1000 nA max、VOFF = 40 V | 一致 | p4 §10 Max 列 | 同上 |
| TLP241A | **COFF** | 300 pF typ、V = 0 V、1 MHz | 一致 | p4 §10 Typ. 列 | "Output capacitance COFF V = 0 V, f = 1 MHz 300 pF" |
| TLP241A | CS | 0.8 pF | 一致 | p4 §12 | 同上 |
| TLP241A | tON / tOFF | 2.8 / 5、0.3 / 1 ms | 一致 | p4 §13 | 同上 |
| TLP241A | BVS | 5000 Vrms min | 一致 | p4 §12 | 同上 |
| VO14642A | 構成 | SPST 1 Form A、AC/DC または DC | 一致 | p1 | 同上 |
| VO14642A | VL | 60 V | 一致 | p2 | "DC or peak AC load voltage VL 60 V" |
| VO14642A | 負荷電流 | 2000 mA（DC only） | 一致 | p2 | "Load current (DC only) IL 2000 mA" |
| VO14642A | IFon | 0.5 / 2 mA | 一致 | p3 | 同上 |
| VO14642A | IFoff | 50 µA min | 一致 | p3 | 同上 |
| VO14642A | **RON（AC/DC）** | 0.18 / 0.25 Ω、IF = 10 mA、IL = 1 A | 一致 | p3 | 同上 |
| VO14642A | RON（DC only） | 0.05 / 0.07 Ω、IL = 2 A | 一致 | p3 | 同上 |
| VO14642A | **ILEAK** | 1 µA max、VL = 60 V | 一致 | p3 | 同上 |
| VO14642A | Fig. 6 | 25°C 付近 ≈ 0、85°C 約 20 nA | 一致 | p5 | 図中 "VLOAD = 60 V" |
| VO14642A | 出力容量の表値 | DS に無い | 一致 | p3 | — |
| VO14642A | Fig. 14 | 0 V 約 205、5 V 約 80、10 V 約 65、20 V 約 52、40 V 以上 約 42 pF、Tamb = −55 °C | 一致・補足あり | p6。**私の読み:** 0 V 約 202、**5 V 約 87、10 V 約 70**、20 V 約 53、40 V 以上 約 41 pF。図の温度が −55 °C なのと、接続の記載が無いのは boundary.md のとおり | 図中 "Tamb = -55 °C" |
| VO14642A | ton / toff | 370 / 800、50 / 800 µs | 一致 | p3 | 同上 |
| VO14642A | 絶縁試験電圧 | 5300 VRMS | 一致 | p1 | 同上 |
| VO14642A | パッケージ | DIP-6 / SMD-6 | 一致 | p1 | 同上 |

### §2 末尾「どの DS にも無かった項目」の照合

| 箇条 | 判定 | DS の実際 |
|---|---|---|
| オン抵抗の直線性・歪み・電圧依存が無い。オン抵抗は電流 = 最大（1〜2.5 A）の 1 点だけ | **誤り** | 直線性・歪みの規定値が無いのは正しい。ただし (1) 電流は **AQW212EH が IL = Max. = 0.5 A**、VO14642A（AC/DC）が 1 A なので「1〜2.5 A」ではなく **0.5〜2.5 A**。(2) 出力の I–V 特性のグラフがある: AQV252G 図 8（PDF p4、±0.4 V・±5 A、25°C）、AQW212EH 図 8-1〜8-3（PDF p5、8-2 が AQW212EH で ±1 V・±0.6 A）、TLP241A Fig. 14.4（p5、±0.2 V・±3 A、IF = 5 mA、t < 1 s）。どれも原点を通る直線に見える。オン抵抗の温度特性（AQV252G 図 2、AQW212EH 図 2-2、TLP241A Fig. 14.5、VO14642A Fig. 9）もある |
| 出力容量の表値は TLP241A の COFF だけ | 一致 | |
| OFF アイソレーション（dB） | 一致 | どれにも無い |
| 25°C・低電圧の漏れの表値。低電圧はグラフだけ | 一致 | TLP241A Fig. 14.9 と VO14642A Fig. 6 は温度特性（40 V・60 V）なので低電圧ではない |
| 「LED 電源が落ちたとき」を別に規定した DS は無い | 一致 | |
| TLP241A の最新版の中身 | 確かめられず | 手元は Rev.5.0 だけ |

## 3. 信号リレー

| 部品 | 項目 | boundary.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|---|
| AZ850 | **外形** | 高さ 5、長さ 14、幅 9 mm | 一致 | p1 FEATURES、p2 MECHANICAL DATA（.551 [14.0]、.354 [9.00]、.197 [5.0]） | "Height: 0.197“ (5 mm); Length: 0.551“ (14 mm); Width: 0.354“ (9 mm)" |
| AZ850 | **接点材質** | AgPd、金クラッド | 一致 | p1 CONTACTS | "Contact materials AgPd - silver palladium, gold clad" |
| AZ850 | 初期接触抵抗 | < 50 mΩ、条件なし | 一致 | p1 | "Initial resistance < 50 mΩ" |
| AZ850 | **最小開閉負荷** | 10 mV、10 µA | 一致 | p1 | "Minimum switching voltage 10 mV current 10 µA" |
| AZ850 | **非ラッチ 5 V 抵抗** | 178 Ω ±10 % | 一致 | p2 Monostable non-latching の 5 V 行（画像で確認） | "5 3.75 12.5 178" |
| AZ850 | 非ラッチ Must Operate / Max. Continuous | 3.75 / 12.5 VDC | 一致 | 同上 | 同上 |
| AZ850 | Dropout | > 10 % | 一致 | p1 COIL | "Dropout non-latching types > 10% of nominal coil voltage" |
| AZ850 | **非ラッチ 5 V 電流・電力** | DS に無い。計算 28.1 mA、140 mW | 一致 | DS に無いのは正しい。計算: 5 / 178 = 28.09 mA、25 / 178 = 140.4 mW | — |
| AZ850 | 感動電圧での電力（非ラッチ） | 79〜113 mW | 一致 | p1 | "monostable non-latching 79 - 113 mW" |
| AZ850 | 動作 / 復帰 | 2 / 1 ms typ | 一致 | p1 | 同上 |
| AZ850 | **P1 5 V** | 250 Ω、3.75、14.5 V | 一致 | p2 Single coil latching の 5 V 行 | "5 3.75 14.5 250" |
| AZ850 | **P1 5 V 電流・電力** | DS に無い。計算 20 mA、100 mW | 一致 | 5 / 250 = 20 mA、25 / 250 = 100 mW | — |
| AZ850 | **P2 5 V** | 125 Ω、3.75、10.0 V。1 コイルあたりかは DS に書いていない | 一致・補足あり | p2 Dual coil latching の 5 V 行。列見出しは "Resistance Ohm ± 10%" だけで、1 コイルあたりとは書いていない（正しい）。**補足（計算）:** p1 の「感動電圧での電力」の下限は 3.75² ÷ 抵抗と一致する: 非ラッチ 3.75² / 178 = 79.0 mW（DS 79）、P1 3.75² / 250 = 56.3 mW（DS 56）、**P2 3.75² / 125 = 112.5 mW（DS 113）**。P2 の 125 Ω を 1 コイルの抵抗と読むと DS の中で整合する | "5 3.75 10.0 125" / "bistable dual coil latching 113 - 169 mW" |
| AZ850 | **P2 5 V 電流・電力** | DS に無い。計算（1 コイル）40 mA、200 mW | 一致 | 5 / 125 = 40 mA、200 mW | — |
| AZ850 | 感動電圧での電力（ラッチ） | P1 56〜84、P2 113〜169 mW | 一致 | p1 | 同上 |
| AZ850 | セット / リセット時間 | 2 / 1 ms typ | 一致 | p1 | 同上 |
| AZ850 | **最小パルス幅** | DS に無い | 一致 | 全文に "pulse" は無い | — |
| AZ850 | 連続通電 | "Max. Continuous VDC" の列だけ | 一致 | p2 | 同上 |
| AZ850 | **2 コイルの同時通電** | DS に無い | 一致 | "simultan" "same time" "both" は無い | — |
| AZ850 | Must Release | DS に無い | 一致 | p2 の表は 4 列だけ | — |
| AZ850 | コイル極性 | 固定 | 一致 | p2 NOTES 5 | "Relay has fixed coil polarity" |
| AZ850 | **出荷時の状態** | DS に無い | 一致 | "shipped" は無い。配線図の注だけ | "Viewed towards terminals, shown in deenergized / reset condition." |
| AZ850 | 衝撃・振動 | 50 g、3 / 5 mm DA | 一致 | p1 | 同上 |
| AZ850 | バウンス時間 | DS に無い | 一致 | "bounce" は無い | — |
| AZ850 | 静電容量 | 0.9 / 0.2 / 0.4 pF | 一致 | p1 | 同上 |
| AZ850 | 隣接間隔 | 5.0 mm | 一致 | p2 NOTES 6 | 同上 |
| G6K | **外形** | 5.2 × 6.5 × 10 mm | 一致 | p1 | "Subminiature model as small as 5.2 (H) × 6.5 (W) × 10 (L) mm ..." |
| G6K | **接点材質** | Ag (Au-Alloy contact) | 一致 | p3 Contacts | 同上 |
| G6K | 接触抵抗 | 100 mΩ max、10 mA 1 VDC | 一致 | p3 | 同上 |
| G6K | 故障率（P 水準） | 10 µA at 10 mVDC | 一致 | p3、*3 | 同上 |
| G6K | **非ラッチ 5 VDC** | 21.1 mA、237 Ω、80 % / 10 %、150 %、約 100 mW | 一致 | p3 Single-side Stable Models | 同上 |
| G6K | **単巻線ラッチ 5 VDC** | 21.1 mA、237 Ω、75 % / 75 %、150 %、約 100 mW | 一致 | p3 Single-winding Latching Models | 同上 |
| G6K | 最大電圧の定義 | 瞬時に加えてよい最高電圧 | 一致 | p3 Note 3 | 同上 |
| G6K | 動作 / 復帰 | 3 / 3 ms max | 一致 | p3 | 同上 |
| G6K | **最小セット/リセット信号幅** | 10 ms | 一致 | p3 Characteristics。単巻線ラッチ列だけ 10 ms、非ラッチ列は "−" | "Minimum set/reset signal width − 10 ms" |
| G6K | 連続通電 | ラッチ専用の規定は無い、一般注意だけ | 一致 | p9 | 同上 |
| G6K | コイル極性 | 確認せよ | 一致 | p6〜p7 | "Note: Check carefully the coil polarity of the Relay." |
| G6K | **出荷時の状態・衝撃** | リセットで出荷、衝撃でセットされうる、使用前にリセット | 一致 | p9 Latching Relay Mounting | "The Latching Relay is reset before shipping. ... Be sure to apply a reset signal before use." |
| G6K | 衝撃 | 750 / 1,000 m/s² | 一致 | p3 | 同上 |
| G6K | 振動（誤動作） | 1.65 mm 片振幅、200 m/s² | 一致 | p3 | 同上 |
| G6K | バウンス時間（ヒストグラム） | 約 0.2〜0.8 ms、試料 G6K-2G 50 個 | 一致 | p5 | "Sample: G6K-2G Number of Relays: 50 pcs" |
| G6K | ラッチ型のバウンス | DS に無い | 一致 | 試料はどれも G6K-2G（非ラッチ） | — |
| G6K | 長期連続 ON | ラッチを推奨 | 一致 | p9 | 同上 |
| G6K | 動作温度 | −40〜70°C | 一致 | p3 | 同上 |
| TQ | **外形** | PC 板 14 × 9 × 5、表面実装 14 × 9 × 5.6 mm | 一致・補足あり | PDF p2 の写真の寸法どおり。**補足:** PDF p13 の外形図では PC 板品の高さは "5 +0.4/−0.2"（括弧で (4.75)）。PDF p14 の表面実装は SA が 5.6、SL・SS の側面図には "Max.7.5" がある | 図中 "14 / 9 / 5"、"14 / 9 / 5.6" |
| TQ | **接点材質（PC 板）** | Ag ＋ Au clad | 一致 | PDF p6 | "Contact material Ag ＋ Au clad" |
| TQ | 接点材質（表面実装） | AgNi ＋ Au clad | 一致 | PDF p8 | "Contact material AgNi ＋ Au clad" |
| TQ | 接触抵抗 | 50 / 75 mΩ max、6 V DC 1 A | 一致 | PDF p6 / p8 | 同上 |
| TQ | **最小開閉負荷** | 10 µA 10 mV DC（参考値） | 一致 | PDF p6 / p8 | "Min. switching load ( reference value )*1 10 µA 10 mV DC" |
| TQ | 注 *1 の追記 | TX 系の AgPd 品 | 一致 | PDF p6 / p8 | 同上 |
| TQ | **非ラッチ 5 V（PC 板）** | 28.1 mA、178 Ω、140 mW、75 % / 10 %、150 % | 一致 | PDF p5 | "5 V DC ... 28.1 mA 178 Ω" / "140 mW" |
| TQ | **1 コイルラッチ 5 V（PC 板）** | 20 mA、250 Ω、100 mW | 一致 | PDF p5 | "20 mA 250 Ω" / "100 mW" |
| TQ | **2 コイルラッチ 5 V（PC 板）** | 各 40 mA、各 125 Ω、各 200 mW | 一致 | PDF p5。Set coil / Reset coil の列が別 | "40 mA 40 mA 125 Ω 125 Ω 200 mW 200 mW" |
| TQ | 非ラッチ 5 V（表面実装） | 28.1 mA、178 Ω、140 mW | 一致 | PDF p7 | 同上 |
| TQ | **1 コイルラッチ 5 V（表面実装）** | 14 mA、357 Ω、70 mW | 一致 | PDF p7 | "14 mA 357 Ω" / "70 mW" |
| TQ | **2 コイルラッチ 5 V（表面実装）** | 各 28.1 mA、178 Ω、140 mW | 一致 | PDF p7 | 同上 |
| TQ | 型番注 *2 | 5 V トランジスタ駆動なら 4.5 V 品 | 一致 | PDF p2 | 同上 |
| TQ | 使用電圧 | ±5 % 以内 | 一致 | PDF p5 | 同上 |
| TQ | 動作 / 復帰 | PC 板 3 / 3 ms、表面実装 4 / 4 ms | 一致 | PDF p6 / p8 | 同上 |
| TQ | **セット/リセットのパルス幅** | 10 ms 以上を推奨 | 一致 | PDF p17（TQ 本体の "Cautions for usage of TQ relay"） | "we recommend setting the coil applied set and reset pulse time to 10 ms or more at the rated coil voltage." |
| TQ | 連続通電 | DS に無い（最大許容 150 % の列だけ） | 一致 | コイルの連続通電の可否を書いた文は無い。PDF p17 の "Use latching when conditions involve continuous carrying current." は接点の電流の話 | — |
| TQ | **2 コイルラッチの同時通電** | セットとリセットに同時に電圧を加えないこと | 一致・補足あり | PDF p18 Coil connection。**補足:** PDF p18 は TQ 本体ではなく、綴じ込みの汎用 "GUIDELINES FOR SIGNAL RELAYS USAGE"（ASCTB414E 202408）の頁 | "Avoid impressing voltages to the set coil and reset coil at the same time." |
| TQ | コイル極性 | 内部接続図で確認 | 一致・補足あり | PDF p18（同じく汎用ガイドラインの頁） | 同上 |
| TQ | **出荷時の状態・衝撃** | リセット位置で出荷、衝撃で変わりうる、電源投入直後に初期化 | 一致 | PDF p17（TQ 本体） | "The relay is shipped in the reset position. ... advisable to build a circuit in which the relay can be initialized ( set and reset ) just after turning on the power." |
| TQ | 衝撃 | PC 板 490 / 980、表面実装 750 / 1,000 m/s² | 一致 | PDF p6 / p8 | 同上 |
| TQ | 振動 | 3 / 5 mm | 一致 | PDF p6 | 同上 |
| TQ | バウンス時間 | DS に無い | 一致 | "bounce" は "without bounce" と M.B.B. の注だけ | 同上 |
| TQ | 長期連続通電 | ラッチを使うこと | 一致・補足あり | PDF p18（汎用ガイドラインの頁）。TQ 本体の PDF p17 にも "Use latching when conditions involve continuous carrying current." がある | "For circuits such as these, please use a magnetic-hold type latching relay." |
| TQ | 電気的寿命の字句 | "0.5 A 125 V DC"（接点定格は AC） | 一致 | PDF p6 の画像でも "0.5 A 125 V DC" | 同上 |
| G5V-2 | 外形 | 20.5 × 10.1 × 11.5 max | 一致 | p4 | 同上 |
| G5V-2 | 接点材質 | Ag + Au-alloy | 一致 | p2 | 同上 |
| G5V-2 | 接触抵抗 | 50 / 100 mΩ max | 一致 | p1 | 同上 |
| G5V-2 | 故障率 | 10 µA at 10 mVDC | 一致 | p1 | 同上 |
| G5V-2 | 5 VDC Standard | 100 mA、50 Ω、75 % / 5 %、120 %、約 500 mW | 一致 | p2 | 同上 |
| G5V-2 | 5 VDC H1 | 30 mA、166.7 Ω、75 % / 5 %、180 %、約 150 mW | 一致 | p2 | 同上 |
| G5V-2 | 動作 / 復帰 | 7 / 3 ms | 一致 | p1 | 同上 |
| G5V-2 | 衝撃（誤動作） | 200 / 100 m/s² | 一致 | p1 | 同上 |
| G5V-2 | バウンス時間 | DS に無い | **誤り** | **p3 に "Distribution of Bounce Time *1" が 2 枚ある**（Standard: G5V-2 12 VDC 50 個、High-sensitivity: G5V-2-H1 50 個、23°C）。私の読み: Standard は動作バウンス 約 0.1〜1 ms、復帰バウンス 約 1.5〜4 ms。H1 は動作 約 0.3〜1.3 ms、復帰 約 1.5〜5.5 ms。規定値は無い | "●Distribution of Bounce Time *1" / "Sample: G5V-2 12 VDC Number of Relays: 50 pcs" |
| FTR-B3 | 外形 | 10.6 ± 0.2 × 7.2 ± 0.2、高さ 5.25 ± 0.2 mm | 一致・補足あり | p1・p7〜p8 に原文どおりの字句がある。**補足（DS 内の食い違い）:** p1 の 1 行目は "5.2±0.2mm height"、2 行目は "5.25±0.2 mm height"。外形図の高さの公差は "±0.02" | "flat type ultra miniature (SMT), 5.2±0.2mm height" / "Ultra slim and light weight with a 5.25±0.2 mm height" |
| FTR-B3 | 接点材質 | Gold overlay silver alloy | 一致 | p4 | 同上 |
| FTR-B3 | 接触抵抗 | 75 mΩ max、6 VDC 1 A | 一致 | p4 | 同上 |
| FTR-B3 | 最小開閉負荷 | 10 mVDC、0.01 mA | 一致 | p4 | 同上 |
| FTR-B3 | 静電容量 | 0.4 / 0.5 / 1.0 pF | 一致 | p4 | 同上 |
| FTR-B3 | 非ラッチ 4.5 V | 145 Ω、+3.38 / +0.45 V、140 mW | 一致 | p3 | 同上 |
| FTR-B3 | 1 コイルラッチ 4.5 V | 203 Ω、セット +3.38、リセット −3.38 V、100 mW | 一致・補足あり | p3。値は正しい。**補足:** 列見出しは "Set voltage" と **"Release voltage*"**（"* Pulse driven"）で、「リセット」ではない | "FTR-B3 ( )B4.5Z 4.5VDC 203 Ω +3.38V -3.38V 100mW" |
| FTR-B3 | 5 V 品 | DS に無い | 一致 | p3 の表と p2 の型番の (d) は 1.5 / 3 / 4.5 / 12 / 24 V だけ | — |
| FTR-B3 | 定格電力 / 動作電力 | 140 / 80、100 / 57 mW | 一致 | p4 | 同上 |
| FTR-B3 | 動作 / 復帰 | 3 / 3 ms | 一致 | p4 | 同上 |
| FTR-B3 | Pulse characteristics | 1 ms で約 80 %、約 5 ms 以上で約 57 % | 一致 | p5（私の読み: 1 ms で 82 %、2 ms で約 62 %、5 ms で 57 %、以後一定。横軸の目盛りは 0.5 / 1 / 2 / 5 / 10 / 20 / 50 / 100 / 200 ms が等間隔） | 凡例 "At set/reset" |
| FTR-B3 | 最小パルス幅の表値 | DS に無い | 一致 | | — |
| FTR-B3 | 出荷時の状態 | DS に無い | 一致 | "ship" は無い | — |
| FTR-B3 | 機械的寿命 | 50 × 10⁶ / 20 × 10⁶ | 一致 | p5 | 同上 |
| FTR-B3 | 衝撃 | 750 / 1000 m/s² | 一致 | p5 | 同上 |
| FTR-B3 | バウンス時間 | DS に無い | **誤り** | **p6 REFERENCE DATA に "Distribution of Bounce Time" がある**（試料 FBR-B3GA4.5Z、N = 100。型番の "A" は標準型（非ラッチ））。私の読み: 動作・復帰ともほぼ全数が 0.5 ms 以下。規定値は無い | "Distribution of Bounce Time FBR-B3GA4.5Z N=100 Operate Release" |
| （§3.3 の注） | poppler で文字が出ない | 表の罫線だけ | 一致 | `pdftotext` は 150 バイト、`pdftoppm` の画像は罫線と帯だけ（確認した） | — |

### §3 末尾「どの DS にも無かった項目」の照合

| 箇条 | 判定 | DS の実際 |
|---|---|---|
| ラッチ型のバウンス時間。値は G6K の非ラッチ試料のヒストグラムだけ | **誤り** | ラッチ型のバウンス時間がどの DS にも無いのは正しい。**非ラッチのヒストグラムは G6K のほかに G5V-2（p3、2 枚）と FTR-B3（p6）にもある** |
| 2 コイルラッチの同時通電の明記は TQ だけ | 一致・補足あり | 正しい。出典の PDF p18 は綴じ込みの汎用ガイドライン（ASCTB414E） |
| 最小パルス幅の表値は G6K の 10 ms だけ | 一致 | |
| ラッチ型の連続通電の可否はどの DS も明示していない | 一致 | |
| 出荷時の状態は G6K と TQ だけ | 一致 | |
| AZ850 の定格電圧での電流・電力と P2 の抵抗の意味は DS に無い | 一致・補足あり | 正しい。感動電圧での電力の下限が 3.75² ÷ 抵抗と一致するので、P2 の 125 Ω は 1 コイルあたりと読むのが整合する（上の AZ850 の行） |
| FTR-B3 の 5 V 品は無い | 一致 | |
| 微小電流での接触抵抗は無い | 一致 | |
| ラッチ型の Must Release: AZ850 無し、G6K・TQ 75 % max、FTR-B3 は −（定格の 75 %）の電圧値 | 一致・補足あり | 値は正しい（−3.38 V / 4.5 V = 75 %）。FTR-B3 の列見出しは "Release voltage*" |
