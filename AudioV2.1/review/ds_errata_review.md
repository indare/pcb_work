# DS 事実表と照合結果の再判定（switch_control / power / opamps）

- 実施日: 2026-09-24（ファイル内の日付は 09-25 表記のものがあるが、同じ作業の続き）
- 対象: `AudioV2.1/ds_facts/{switch_control,power,opamps}.md`（facts）と `verify_*.md`（照合）
- 範囲: 照合側が「誤り」「条件の誤り」「一致・補足あり／一致（注記）」「無いとされていたが DS にあった」「facts に載っていない」と書いた行を全部。照合が「一致」とした行は、いくつか抜き取って見ただけで、全部はやり直していない
- 方法: 引用されたページを `pdftoppm` で画像にした（150 dpi、グラフは 300〜600 dpi で切り出し）。グラフは、両者の数値を見る前に自分で読んだ。PIL が壊れていたので、PPM を素の Python で読み、格子線を画素で検出して軸を合わせた（TMUX7612 Fig 5-1/5-4、TPS7A49 Fig 18、TPS7A30 Fig 14/16/18、LT1763 p11、OPA2604 Fig 15、OPA1612 Fig 27、MUSES01 p10）。作業ファイルは scratchpad の `errata/` にある
- リポジトリのファイルは書き換えていない。このファイルだけを書いた

判定の意味: **facts が正** ＝照合の指摘は当たらない／**照合が正** ＝facts を直す（照合の文面どおりで良いとは限らない）／**どちらも不正確**／**判定不能**。
「補足」は、facts の値は正しく、書き足すかどうかだけの話。

---

## 0. 総括

| # | 項目 | 判定 | facts の修正 | v2.1 の設計判断に効くか |
|---|---|---|---|---|
| S1 | TMUX7612 Fig 5-4「正側は 7.5 Ω 超まで」 | 照合が正 | 要（文言） | 効かない（効くのは立ち上がり始めの VS で、そこは両者一致） |
| S2 | TMUX7612 Fig 5-1 の 25°C ≈ 0.95 Ω（表 typ 1.1 Ω と食い違う） | 照合が正（facts に記載なし） | 追記推奨 | 効かない（直列 1 Ω 前後の差） |
| S3 | PCM1804 見出しの食い違いは p9〜11 か p9〜12 か | 照合が正 | 要（ページ範囲） | 効かない |
| S4 | AZ850 220 VDC の注（30 VDC 超は要相談） | 補足（照合が正） | 追記推奨 | 効かない |
| S5 | TBD62083A tON/tOFF は VIH = 5.0 V で測定 | 補足（照合が正） | 追記推奨 | 小（3.3 V 駆動なら時間は保証外。リレー駆動では実害なし） |
| S6 | MCP23017 Table 3-5 は p18 に続く | 補足（照合が正）＋照合の見落とし 1 件 | 要（ページ、アドレス） | ファームのみ（引用のアドレスは BANK=1 の配置） |
| P1 | RS6「無負荷入力電流」 | 補足（照合が正） | 要（項目名） | 小 |
| P2 | TPS7A49 Features「≥ 52 dB（〜400 kHz）」と Fig 18 | 照合が正（facts の表は既に 50 dB を載せている） | 注記追加 | **効く**（200 kHz 超の除去比） |
| P3 | TPS7A30 Features「≥ 55 dB（〜700 kHz）」と Fig 18 | 照合が正、ただし**照合も甘い**（700 kHz では約 45 dB） | 注記追加 | **効く** |
| P4 | TPS7A30 Do's「2.2 µF 以上」 | **facts が正**（同じページの §10 に "at least a 2.2-μF capacitor"） | 出典に §10 を足すだけ | 効かない |
| P5 | LT1763 の PDF は BDTIC のミラー | 照合が正 | 要（出典の注記） | 効かない（中身は Rev G） |
| P6 | LT1763 Note 7（「VOUT(NOMINAL) のみ」） | 照合が正 | 要（1 行） | 効かない（-5/-3.3 品は VOUT の方が大きい） |
| P7 | LT1763 Ripple Rejection 50 dB は 25°C のみ | 照合が正 | 要（条件欄） | 小 |
| P8 | LT1763 PSRR の周波数特性（p11） | 照合が正（facts の抜け） | **追記必須** | **効く**（200 kHz で約 30 dB） |
| P9 | LT1763 最小 ESR（p16 Figure 3） | 照合が正（facts の抜け） | **追記必須** | **効く**（セラミック出力の容量下限） |
| P10 | TPS7A49 EN ヒステリシス「Figure 13 のグラフのみ」 | 照合が正 | 要（括弧内） | 効かない |
| P11 | TPS7A49/TPS7A30 絶対最大の FB・NR/SS 対 IN、TPS7A30 Eq.8 15.4 µF、TPS7A49 p16 ヘッドルームの食い違い | 照合が正（抜け・DS 内の食い違い） | 追記は任意 | 小 |
| O1 | OPA1652 入力間の back-to-back ダイオード | 照合が正（facts は「無い」と書いた） | **要** | **効く**（G = 1 と ch の電源断） |
| O2 | OPA1612 同上 | 照合が正 | **要** | **効く** |
| O3 | NJM5532 入力ダイオードの注意（p5）・V+ 開放時の寄生電流（p6） | 照合が正（facts は「無い」と書いた）。p6 は照合も補足扱いで軽い | **要** | **最も効く**（ch ごとに電源を落とす構成そのもの） |
| O4 | OPA2134 Headroom 21.3 dBu と 23.6 dBu | 照合が正 | 注記追加 | 小（±12 V ではどちらも当たらない） |
| O5 | OPA2604 Fig 15 26 Vp-p | 照合が正（24 Vp-p） | 要 | 小〜中（最大レベルの見積もり） |
| O6 | OPA1612 Fig 27 負側 −14.6 V | 照合が正（facts の誤り）。照合の −14.0 V 端は別の温度の線の疑い | 要 | 小 |
| O7 | MUSES01 ±15 V・2 kΩ +13.5 V | 照合が正（+14.0 V） | 要 | 小 |
| O8 | OPA627 Fig 5-23「RL = 10 kΩ」 | 照合が正 | 要。横軸が 100 kHz から始まることも書く | 効かない |
| O9 | LME49860 Fig 4/8/12、OPA1656 Fig 6-8、OPA2140 Fig 6-22、NE5532 Fig 7-2〜7-4 | 照合が正（存在と読みを確認） | 追記は任意。LME49860 の ±12 V の図は追記推奨 | LME49860 の ±12 V の図は効く（±12 V で直接の資料） |

**facts の誤りのうち設計に効くのは、O1〜O3（「入力保護ダイオードの記述は無い」と書いたのに実はあった）と、P8・P9（LT1763 の抜け）。**
目で読んだグラフの値の誤り（S1、O5〜O7）は、どれも 0.1〜2 V・0.1 Ω 程度で、設計の結論は変わらない。

---

## 1. switch_control.md

| 項目 | facts の記載 | 照合側の主張 | 私の読み（ページ・引用） | 判定 | facts の直し方 |
|---|---|---|---|---|---|
| S1 TMUX7612 Fig 5-4 の正側の上端 | 87 行「正側（VDD 側）は急峻に **7.5 Ω 超まで**立ち上がる」、89 行の表見出し「縦に立ち上がる（〜7.5 Ω）」 | 約 7.4 Ω で水平になり、軸の上限 7.5 Ω は越えない | p17 Figure 5-4、600 dpi。上の枠線（7.5 Ω）と 7.0 Ω の格子線の間は 100 px。5 本とも上端の水平部は枠線の約 15 px 下で、**約 7.42 Ω**。水平部は各曲線の VDD（±10 V の赤なら +9.5〜+10 V）まで続く。7.5 Ω を越える描画は無い | **照合が正** | 87 行を「正側（VDD 側）は急峻に立ち上がり、**約 7.4 Ω（軸上限 7.5 Ω のすぐ下）で水平になって VDD まで続く**。この水平部は測定上限か作図の打ち切りとみられ、実際の Ron を表すものではない（目読み）」に。89 行の見出しは「縦に立ち上がる（〜7.4 Ω で頭打ち）VS」に |
| S2 TMUX7612 Fig 5-1（facts に記載なし） | — | Fig 5-1（±15 V・温度別）では 25°C の線が約 0.95 Ω で、表の typ 1.1 Ω・Fig 5-4 の底 約 1.1 Ω と合わない | p17 Figure 5-1、600 dpi。1.2 Ω と 1.6 Ω の格子線の間は 244 px。薄茶の線（凡例で 25°C）は 1.2 Ω 線の 150 px 下で **0.954 Ω**。青（50°C）1.06、緑（85°C）1.23、紫（125°C）1.45、赤（−40°C）0.73 Ω。どれも VS = −10〜+10 V で完全に水平。Fig 5-4 の底は約 1.12 Ω | **照合が正**（DS の中の食い違い） | Ron の節に 1 行足す:「DS 内の食い違い: p17 Figure 5-1（VDD = 15 V, VSS = −15 V）の 25°C の線は約 0.95 Ω（目読み）で、表 §5.7 の typ 1.1 Ω・Figure 5-4 の底（約 1.1 Ω）と合わない。数値の根拠には表を使う」 |
| S3 PCM1804 見出しの食い違いのページ | 349 行「p9〜11」 | 同じ見出しは p9〜12 の 4 ページ | pdftotext と p12 の画像で確認。p9・p10・p11 上段（SINGLE RATE）は "VCC = 3.3 V, VDD = 5 V, master mode, fS = 48 kHz, …"。p11 下段（DUAL RATE）と p12（QUAD RATE・DSD MODE）も "VCC = 3.3 V, VDD = 5 V"（fS の句が無い短い形）。p13〜14 は見出しなし。**p15 は "VCC = 5 V, VDD = 3.3 V" で正しい向き** | **照合が正** | 「p9〜12 の TYPICAL PERFORMANCE CURVES（SINGLE / DUAL / QUAD / DSD の各見出し）。p15 の見出しは "VCC = 5 V, VDD = 3.3 V" で推奨条件と同じ向き」に |
| S4 AZ850 開閉電圧の注 | 173 行、"220 VDC* or 250 VAC" を引用しているが "*" の中身が無い | 注「30 VDC を越える開閉は要相談」がある | p1 CONTACTS。"\* Note: If switching voltage is greater than 30 VDC, special precautions must be taken. Please contact the factory." | **補足（照合が正）** | 条件欄に「220 VDC には注: 30 VDC を越える開閉は要相談（"special precautions must be taken. Please contact the factory."）」を足す |
| S5 TBD62083A tON/tOFF の試験条件 | 228 行、VOUT = 50 V, RL = 125 Ω, CL = 15 pF | p7 試験回路 8 の注: 入力パルス 50 µs・Duty 10 %・VIH = 5.0 V（TBD62083A）・tr ≤ 5 ns | p5 表の Test Circuit 欄は "8"。p7 "Note 1: Pulse width 50 μs, Duty cycle 10% / Output impedance 50 Ω, tr ≤ 5 ns, tf ≤ 10 ns / … TBD62083A series 5.0 V"、"Note 2: CL includes the probe and the test board capacitance." | **補足（照合が正）** | 条件欄に「試験回路 8（p7）: 入力パルス 50 µs・Duty 10 %・**VIH = 5.0 V**・tr ≤ 5 ns・tf ≤ 10 ns。CL はプローブ・基板を含む」を足す |
| S6 MCP23017 POR 後のレジスタ | 253 行、出典「p17 Table 3-4/3-5」、例に "IOCON 05 …"、"OLATA 0A …" | Table 3-5（BANK = 0）の INTF〜OLAT は p18 に続く | p17 に Table 3-4（BANK = 1）と Table 3-5 の前半、p18 に "TABLE 3-5 … (CONTINUED)"（INTFA 0E〜OLATB 15）。**照合が触れていない点:** 引用の "IOCON 05" と "OLATA 0A" は **BANK = 1 の番地**（Table 3-4）。POR 後は IOCON = 0000 0000 で BANK = 0 なので、POR 直後の番地は IOCON 0A/0B、OLATA 14 | **補足（照合が正）＋照合の見落とし** | 出典を「p16 Table 3-2/3-3、p17 Table 3-4、p17〜18 Table 3-5」に。例の引用のあとに「（引用の番地は BANK = 1 の Table 3-4 のもの。POR 後は BANK = 0 なので番地は Table 3-5: IOCON 0x0A/0x0B、OLATA 0x14）」を足す |

TMUX7612 の Fig 5-4 の他の読み（離れ始め・1.5 Ω 越え・縦の立ち上がり・負側）は、照合も facts と一致としていて、私の 150 dpi の読みとも食い違わない。
ADC1804_F 組立説明書（照合で「確かめられず」）は、誤りの主張ではないので扱っていない。

---

## 2. power.md

| 項目 | facts の記載 | 照合側の主張 | 私の読み（ページ・引用） | 判定 | facts の直し方 |
|---|---|---|---|---|---|
| P1 RS6 "Quiescent Current" の項目名 | 35 行「無負荷入力電流（"Quiescent Current"）」55 mA Max、印字 "2VDC" | 「無負荷」は DS の字句ではない（見出し条件は full load） | p2 画像。行は "Quiescent Current / nom. Vin= 5VDC 2VDC 24VDC 48VDC / 105mA 55mA 28mA 14mA"（Max 列）。条件欄に負荷の記載なし。値・列・誤植 "2VDC" は facts のとおり | **補足（照合が正）** | 項目名を「"Quiescent Current"（DS の字句のまま。負荷の条件は書かれていない。値の大きさからは無負荷時と読めるが DS はそう書いていない）」に |
| P2 TPS7A49 PSRR（Features） | 199 行「≥ 52 dB（10 Hz〜400 kHz）」、Figure 29 の構成 | Fig 14・18（IOUT = 150 mA、10 µF/10 nF）では 400 kHz で約 50 dB と読め、52 dB を下回る | p9 Figure 18、300 dpi・画素換算。CFF = 10 nF の線: 120 Hz 72.6、1 kHz 71.6、10 kHz 58.7、100 kHz 53.8、200 kHz 61.5、**400 kHz 50.1 dB**。p14 §9.1.5 は "above 52 dB from 10 Hz to 400 kHz; **see Figure 18** and Figure 25" と自分でこの図を指している | **照合が正**（DS の中の食い違い。facts の表 211 行は既に 400 kHz = 50 と書いており、値の誤りではない） | 199 行の条件欄に「DS 内の食い違い: この文が参照する Figure 18（VOUT = 5 V, IOUT = 150 mA, COUT = 10 µF, CNR/SS = CFF = 10 nF）は 400 kHz で約 50 dB（目読み）。52 dB の条件は DS に書かれていない」を足す |
| P3 TPS7A30 PSRR（Features） | 325 行「≥ 55 dB（10 Hz〜700 kHz）」 | Fig 18（CFF = 10 nF）は 400 kHz で約 54 dB、Fig 14/16（CFF = 0）は 100 kHz で約 53 dB | p10、300 dpi・画素換算。Figure 18 CFF = 10 nF: 100 kHz 55.7、200 kHz 60.9、300 kHz 59.5、**400 kHz 53.9**、500 kHz 49.4、**700 kHz 44.8 dB**。Figure 14 COUT = 10 µF: 100 kHz 53.2、**700 kHz 44.6 dB**。p18 §9.1.3 は "above 55 dB from 10 Hz to 700 kHz; **see Figure 18** and Figure 26" | **照合が正。ただし照合は 400 kHz までしか見ておらず、食い違いは 700 kHz の端で約 10 dB ある** | 325 行の条件欄に「DS 内の食い違い: この文が参照する Figure 18（VOUT = −5 V, IOUT = 200 mA, COUT = 10 µF, CNR/SS = CFF = 10 nF）は 400 kHz で約 54 dB、**700 kHz で約 45 dB**（目読み）。Figure 14（COUT = 10 µF, CFF = 0）も 700 kHz で約 45 dB」を足す |
| P4 TPS7A30 Do's and Don'ts | 359 行「2.2 µF 以上を IN・OUT の近くに」 | 原文の「at least」は個数に掛かる。容量の下限は別の箇所（p18） | p23 §9.3 は "Place at least one low-ESR, 2.2-μF capacitor …"（照合の言うとおり個数）。ところが**同じ p23 の §10 Power Supply Recommendations** に "The input and output supplies must also be bypassed with **at least a 2.2-μF capacitor** located near the input and output pins. There must be no other components located between these capacitors and the pins." とある | **facts が正**（照合の注記は §10 を見落としている） | 値は直さない。出典を「p23 §9.3・§10」にして、§10 の原文を引用に足せばよい。§10 の「コンデンサとピンの間に他の部品を置かない」も配置の制約として書く価値がある |
| P5 LT1763 の出典 | 377 行、"1763fg"・Rev G。README の "1763fh" と違う | PDF は各ページ下に "www.BDTIC.com/Linear" の透かし、Author も www.BDTIC.com（第三者のミラー） | `pdfinfo`: Author "www.BDTIC.com"、Creator InDesign CS2、CreationDate 2010-05-17、ModDate 2013-08-07。p1・p5・p11・p16 の下端に "www.BDTIC.com/Linear" | **照合が正** | 出典に「PDF は Linear Technology の Rev G（"1763fg"）を第三者サイト（BDTIC）が配布したもの。ADI の現行版ではない」を足す |
| P6 LT1763 GND ピン電流の試験条件 | 401 行は Note 7 の後半のみ。417 行「試験は VIN = VOUT(NOMINAL) のみ」 | 前半は「VOUT(NOMINAL) または 2.3 V（C/I）/ 2.35 V（MP）の大きい方、電流源負荷」 | p6 Note 7 "GND pin current is tested with VIN = VOUT(NOMINAL) or VIN = 2.3V (C, I grade) or 2.35V (MP grade), whichever is greater, and a current source load." | **照合が正** | 417 行を「試験は VIN = VOUT(NOMINAL) と 2.3 V（C/I）／2.35 V（MP）の大きい方、電流源負荷（Note 7）。これより高い VIN の規定値は無い」に |
| P7 LT1763 Ripple Rejection | 407 行、50 / 65 dB MIN/TYP、120 Hz、500 mA | この行に ● は無く、50 dB の最小値は 25°C だけ | p5 画像。Ripple Rejection の行の ● 欄は空。見出し "The ● denotes the specifications which apply over the full operating temperature range, otherwise specifications are at TA = 25°C." | **照合が正** | 条件欄に「TA = 25°C（● なし。全温度の規定ではない）」を足す |
| P8 LT1763 PSRR の周波数特性（facts に無い） | 120 Hz の 50/65 dB だけ | p11 "Input Ripple Rejection" 2 枚、COUT = 10 µF で 100 kHz 約 40、200 kHz 約 30、1 MHz 約 22 dB | p11、300 dpi・画素換算（2 枚とも IL = 500 mA、VIN = VOUT(NOMINAL) + 1 V + 50 mVRMS）。**左図（CBYP = 0、COUT = 10 µF / 4.7 µF）**: 10 µF の線は 1 kHz 約 49、約 30 kHz に約 49 dB の山、100 kHz 約 37、200 kHz 約 28、1 MHz 約 21 dB。**右図（COUT = 10 µF、CBYP = 0.01 µF / 1000 pF / 100 pF）**: 30 kHz 以上で 3 本が重なり、100 kHz 約 41、200 kHz 約 32、500 kHz 約 24、1 MHz 約 22 dB | **照合が正**（値は ±3 dB の範囲で一致） | LT1763 の節に行を足す:「グラフ: Input Ripple Rejection vs 周波数（p11、目読み）。IL = 500 mA、VIN = VOUT(NOMINAL) + 1 V + 50 mVRMS。COUT = 10 µF で 100 kHz 約 37〜41 dB、200 kHz 約 28〜32 dB、1 MHz 約 21〜22 dB（CBYP による差は 30 kHz 以上でほぼ無い）」 |
| P9 LT1763 最小 ESR（facts に無い） | 412 行、「最小 3.3 µF・ESR 3 Ω 以下」と CBYP 別の推奨容量のみ | p16 Figure 3。最小 ESR はバイパス容量で決まり、COUT が小さいと ESR ≈ 0 は安定域の外 | p16 本文 "The shaded region of Figure 3 defines the range over which the LT1763 regulators are stable. The minimum ESR needed is defined by the amount of bypass capacitance used, while the maximum ESR is 3Ω."。Figure 3（400 dpi）: 安定域の下限の線が ESR = 0 に届く COUT は、**CBYP = 0 で約 2.7〜3 µF、100 pF で約 4 µF、330 pF で約 5 µF、≥ 1000 pF で約 6 µF**。それより小さい COUT では、ESR 0.2〜0.8 Ω 程度より上でないと安定域に入らない。横軸は 10 µF まで | **照合が正** | 412 行の次に足す:「安定域（p16 Figure 3、目読み）: 最大 ESR は 3 Ω。最小 ESR は CBYP で決まり、ESR ≈ 0（セラミック）で安定になる COUT は CBYP = 0 で約 3 µF 以上、100 pF で約 4 µF、330 pF で約 5 µF、1000 pF 以上で約 6 µF 以上。原文 "The minimum ESR needed is defined by the amount of bypass capacitance used, while the maximum ESR is 3Ω."。同じページの本文に "When used with a 5V regulator, a 16V 10µF Y5V capacitor can exhibit an effective value as low as 1µF to 2µF for the DC bias voltage applied and over the operating temperature range." とある（Figure 4・5）」 |
| P10 TPS7A49 EN のヒステリシス | 248 行「EN の閾値のヒステリシスの規定値（Figure 13 のグラフのみ）」 | Figure 13 は境界の線が 1 本だけで、ヒステリシスはグラフにも無い | p9 Figure 13。ON/OFF の境界は 1 本（−40°C 約 1.9 V、25°C 約 1.7 V、125°C 約 1.4 V）。EC 表（p6）は VEN(high) min 2.1 V、VEN(low) max 0.4 V のみ | **照合が正** | 「EN の閾値のヒステリシス: 規定値もグラフも無い（Figure 13 は ON/OFF の境界を 1 本の線で示すだけ。25°C で約 1.7 V、目読み）」に |
| P11a 絶対最大の FB・NR/SS 対 IN の行（facts に無い） | 省略 | TPS7A49 −36/+0.3 V、TPS7A30 −0.3/+36 V | p5 の両方で確認（"FB pin to IN pin"、"NR/SS pin to IN pin"、ほかに "EN pin to IN pin"、"OUT pin to IN pin" も同じ値） | **照合が正**（抜け） | 追記は任意 |
| P11b TPS7A30 の設計例 Eq.8（facts に無い） | TPS7A49 の 35 µF だけ | TPS7A30 は ICL(min) = 220 mA で 15.4 µF | p21 Eq.7・8。「ソフトスタートを支配的にするため、電流制限での立ち上がりをソフトスタート時間の 2 桁下（140 µs）に置く」という設計例で、VOUT = −2 V の例の値。上限の規定ではない。TPS7A49 の例は ICL(max)、TPS7A30 の例は ICL(min) を使っていて、式の置き方も揃っていない | **照合が正**（抜け） | 追記は任意。書くなら「設計例（VOUT = 2 V、tSS = 14 ms）での目安で、規定値ではない」と明記 |
| P11c TPS7A49 p16 のヘッドルーム | 228 行、定義の文のみ | 同じ段落で 1.8 V を「ヘッドルーム」と呼んでいて定義と合わない | p16 "the dropout headroom of 1.8 V is sufficient …" の直後に "Dropout headroom is calculated as VIN – VOUT – VDO(max), and for optimal performance must be at least 1 V." | **照合が正**（DS 内の不整合。facts の誤りではない） | 直さなくてよい |

LT1763 の SHDN 閾値の温度グラフ、GND ピン電流の VIN 依存のグラフ、TPS7A49 のソフトスタート波形（照合が「近い情報がある」とした残り）は、ページにあることだけ確かめた。facts の「規定値は無い」は正しい。

---

## 3. opamps.md

| 項目 | facts の記載 | 照合側の主張 | 私の読み（ページ・引用） | 判定 | facts の直し方 |
|---|---|---|---|---|---|
| O1 OPA1652 入力間ダイオード | 208 行「差動入力（絶対最大）規定なし」、213 行「探したが無かった: 入力間の保護ダイオードの記述」 | p15 §7.3.2 に back-to-back ダイオード、入力電流 10 mA 以下 | p15 画像。§7.3.2 Input Protection "The input terminals of the OPA1652 and OPA1654 are protected from excessive differential voltage with back-to-back diodes, as Figure 36 illustrates. … in low-gain or G = 1 circuits, fast ramping input signals can forward bias these diodes … the input signal current must be limited to 10 mA or less."。Figure 36 に入力間の逆並列ダイオードが描かれている。§7.3.3 に ESD の current-steering diodes の説明が別にある | **照合が正（facts の誤り）** | 213 行から「入力間の保護ダイオードの記述」を消す。行を足す:「入力保護（本文）: 入力間に back-to-back ダイオード。G = 1 など低利得で入力が速く動くと順バイアスになりうるので、入力信号電流を 10 mA 以下に制限（入力直列抵抗か帰還抵抗で）。p15 §7.3.2・Figure 36」 |
| O2 OPA1612 入力間ダイオード | 257 行「規定なし」、262 行「入力間の保護ダイオードの有無の記述（ESD 用 steering diodes の説明 p.13 のみ）」 | p14 §7.3.4 に back-to-back ダイオード | p14 §7.3.4 "The input terminals of the OPA1611 and the OPA1612 are protected from excessive differential voltage with back-to-back diodes, as Figure 31 shows. … If the input signal is fast enough to create this forward bias condition, the input signal current must be limited to 10 mA or less."（Figure 17 の Typical Characteristics に現象の図があるとも書いてある） | **照合が正（facts の誤り）** | O1 と同じ形で直す。出典は p14 §7.3.4・Figure 31 |
| O3 NJM5532 入力ダイオード | 62 行「探したが無かった: 入力保護ダイオードの有無の記述」 | p5 NOTICE、p1 等価回路、p6 寄生回路の注意 | p5 NOTICE "When used in voltage follower circuit, put a current limit resistor into non-inverting input terminal in order to avoid inside input diode destruction when the power supply is turned on. ( ref.Fig.1 )"、Fig.1 は入力直列 1k。p1 EQUIVALENT CIRCUIT に +INPUT と −INPUT の間の逆並列ダイオード 2 個が描かれている。**p6 "Countermeasure to Excess Current by Parasitic Circuit"**: "When the NJM5532 V+ is open (Fig.2), the NJM5532 may be burnt flowing the excess current by internal parasitic circuit"。起こる条件は「入力と V− の電位差が大きい」「入力に 1 kΩ 以上の抵抗が無い」「V+ 端子が低インピーダンスにつながっている」。対策は SBD の挿入（Fig.4-1/4-2）か 1 kΩ 以上の抵抗（Fig.5） | **照合が正（facts の誤り）**。照合は p6 を補足の一言で済ませているが、中身は p5 より重い | 62 行から「入力保護ダイオードの有無の記述」を消す。行を 2 つ足す:「入力保護: 入力間に逆並列ダイオード（p1 等価回路）。ボルテージフォロワでは電源投入時の入力ダイオード破壊を避けるため、非反転入力に電流制限抵抗（図は 1 kΩ）。p5 NOTICE」／「V+ 開放時の過電流: V+ が開放で、入力と V− の電位差が大きく、入力に 1 kΩ 以上の抵抗が無いと、内部の寄生回路で過電流が流れ焼損しうる。対策は SBD か 1 kΩ 以上の入力抵抗。p6」。差動入力の絶対最大 ±0.5 V（59 行）はこのダイオードと合う |
| O4 OPA2134 Headroom | 102 行、typ 21.3 dBu、"VS = 18V"（原文どおり） | p13 §6.2.1 と p9 Figure 5-4 は ±18 V・THD+N < 0.01 % で 11.7 Vrms = 23.6 dBu | p7 表 "Headroom(1) THD < 0.01%, RL = 2kΩ, VS = 18V 21.3 dBu"。p13 "…maximum allowable output voltage level of 11.7Vrms (THD+Noise < 0.01%), have a headroom specification of 23.6dBu. See Figure 5-4."。p9 Figure 5-4 の凡例 "VS = ±18V, RL = 2kΩ, f = 1kHz / THD < 0.01% / OPA134 – 11.7Vrms"。20·log(11.7/0.7746) = 23.6 dBu で本文と合う。21.3 dBu は 9.0 Vrms（12.7 Vpk）で、±18 V でのクリップ手前としては低い（±15 V 程度の値に見えるが、DS はそう書いていないので推測） | **照合が正** | 102 行の条件欄に「DS 内の食い違い: p13 §6.2.1 と p9 Figure 5-4 は VS = ±18 V・THD+N < 0.01 % で 11.7 Vrms = 23.6 dBu。表の 21.3 dBu（= 9.0 Vrms）とは 2.3 dB 違う。表の "VS = 18V" の意味（±18 V か 18 V 単電源か）は DS から決められない」を足す |
| O5 OPA2604 Fig 15 | 154 行「低域で約 26 Vp-p」 | 平坦部は 24 Vp-p の目盛線の上 | p8 Figure 15、400 dpi。縦軸は 0〜30 Vp-p で細目盛 2 Vp-p（30 の枠線 y≈42、20 の太線 y≈258、10 の太線 y≈474 → 2 Vp-p = 43 px）。平坦部は y ≈ 172 で **24 Vp-p の細目盛線に重なる**。約 350 kHz から下がる | **照合が正** | 「低域（10 kHz〜約 300 kHz）で約 24 Vp-p（目読み。負荷の表記なし）」に |
| O6 OPA1612 Fig 27 | 253 行「25°C で 0〜約 45 mA で約 +14.1 V / 約 −14.6 V」 | 正側 +14.35（0 mA）〜+14.2（43 mA）、負側 −14.35（0 mA）〜−14.0（43 mA） | p11 Figure 27、400 dpi・画素換算（上側は 14.5 V と 14.0 V の格子線の間 126 px、下側は −14.0 と −14.5 の間 125 px）。+25°C の引き出し線が指す実線は、正側 **+14.35 V（0 mA）→ +14.2 V（44 mA）**、負側 **−14.3 V（0 mA）→ −14.2 V（44 mA）**。負側で −14.0 V 付近まで上がるのは一点鎖線（+85°C）で、44 mA で約 −14.0 V | **照合が正（facts の −14.6 V は誤り）**。照合の負側の「−14.0 V」の端は +85°C の線を拾った可能性があり、25°C の線としては −14.2 V 付近 | 「25°C の線で、0〜約 45 mA の範囲で約 +14.35〜+14.2 V / 約 −14.3〜−14.2 V（目読み。+85°C の線は負側が約 −14.0 V まで上がる）」に |
| O7 MUSES01 ±15 V 負荷抵抗グラフ | 356 行「±15 V で 2 kΩ 約 +13.5 / 約 −13 V」 | +14.0 / −13.2〜−13.4 V。facts 自身の温度グラフの行（+14）とも合わない | p10 右下 "MAXIMUM OUTPUT VOLTAGE vs LOAD RESISTANCE (TEMPERATURE) V+/V-=±15V"、400 dpi・画素換算（縦 1 V = 27.2 px）。2 kΩ で、3 本（赤・青・黒）の正側は **+13.9〜+14.2 V**、負側は **−13.0〜−13.3 V**（黒 −13.1 V）。10 kΩ で +14.1〜+14.4 / −13.2〜−13.6 V | **照合が正** | 「±15 V で 2 kΩ 約 +14.0 / 約 −13.1 V（目読み。温度 3 本の幅 ±0.2 V）」に |
| O8 OPA627 Fig 5-23 | 229 行「低域で約 25 Vp-p、条件 VS = ±15 V、**RL = 10 kΩ**」 | ページにも図にも負荷の記載は無い | p16 見出し "at TA = 25°C and VS = ±15V (unless otherwise noted)"。図中は "OPA627"・"OPA637" のラベルだけで負荷の記載なし。値は 25 Vp-p（私の読み 25.2）。**加えて: 横軸は 100 kHz〜100 MHz で、「低域」は 100 kHz〜約 1.5 MHz の平坦部のこと** | **照合が正** | 「100 kHz〜約 1.5 MHz の平坦部で約 25 Vp-p（目読み。横軸は 100 kHz から。負荷の記載なし）」、条件「VS = ±15 V、25°C（ページ既定）」に |
| O9a LME49860 ±12 V の THD+N vs Output Voltage | 188 行ほか。±12 V は Fig 96（THD+N = 1 % の Vrms）のみ | p5 Figure 4・8、p6 Figure 12 に ±12 V（2 kΩ / 600 Ω / 10 kΩ）がある。2 kΩ の急増は約 8 V | p5 画像。Figure 4 "VCC = 12V, VEE = −12V, RL = 2kΩ"、Figure 8 同 600 Ω。p6 Figure 12 同 10 kΩ。Figure 4 の急増は約 7〜8 V（横軸は "OUTPUT VOLTAGE (V)" で rms か peak かの表記なし） | **照合が正**（抜け） | 追記推奨:「グラフ: THD+N vs Output Voltage、±12 V（Figure 4 = 2 kΩ、Figure 8 = 600 Ω、Figure 12 = 10 kΩ）。2 kΩ で約 7〜8 V から急増（目読み。単位は "V" のみ）」 |
| O9b OPA1656 Fig 6-8 | 137 行ほか。±15 V の振幅グラフに触れていない | ±15 V の THD+N Ratio vs Output Amplitude、急増は約 10 Vrms | p9 Figure 6-8、ページ見出し "VS = ±15 V, RL = 2 kΩ"。6 本（G = ±1、600 Ω / 2 kΩ / 10 kΩ）。約 7〜8 Vrms から上がり始め、10 Vrms 付近で急増 | **照合が正**（抜け） | 追記は任意 |
| O9c OPA2140 Fig 6-22 | 313 行ほか | ±15 V の線、低域で約 29 Vpp | p12 Figure 6-22 "Maximum Output Voltage vs Frequency"、"VS = ±15 V" の線は約 29 Vpp（ページ既定は ±18 V だが線に ±15 V と明記） | **照合が正**（抜け） | 追記は任意 |
| O9d NE5532 Fig 7-2〜7-4 | 触れていない | 単電源 15 V の応用例の伝達特性。仕様ではない | p9 に Figure 7-2〜7-4。p7 "Information in the following applications sections is not part of the TI component specification" | **照合が正**（ただし仕様ではない） | 追記不要 |

照合の「誤り（目読み）」3 件（O5〜O7）の許容幅「最も細かい目盛の半分」は妥当だった。O6 のみ、照合自身の読みも温度の線を取り違えている疑いがある。

---

## 4. 照合が見落としていたもの（facts・照合とも書いていない）

| 項目 | ページ・原文 | 意味 |
|---|---|---|
| TPS7A30 の PSRR は 700 kHz で約 45 dB | p10 Figure 18（CFF = 10 nF）44.8 dB、Figure 14（COUT = 10 µF）44.6 dB。§9.1.3 の「700 kHz まで ≥ 55 dB」とは約 10 dB 違う | P3 の食い違いは 400 kHz の 1 dB ではなく、帯域の端で 10 dB |
| TPS7A30 §10 の 2.2 µF と配置 | p23 "bypassed with at least a 2.2-μF capacitor located near the input and output pins. There must be no other components located between these capacitors and the pins." | P4 の照合の注記を打ち消す。配置の制約でもある |
| MCP23017 の引用番地は BANK = 1 の配置 | p17 Table 3-4（BANK = 1）の IOCON 05・OLATA 0A。POR 後は BANK = 0（Table 3-5: IOCON 0A/0B、OLATA 14） | ファームで番地を facts から写すと外れる |
| NJM5532 p6 の寄生回路（照合は補足の一言だけ） | 上の O3 | ch ごとに電源を落とす構成に直接かかわる（次節） |
| OPA627 Fig 5-23 の横軸は 100 kHz から | p16 | 「低域 25 Vp-p」は音声帯域の値ではない |
| NJM4580 の等価回路には入力間ダイオードが描かれていない | p1 EQUIVALENT CIRCUIT（画像） | NJR 品のうち NJM5532 だけが該当。MUSES01/02/03 は本文検索で diode・follower・parasitic が 0 件（等価回路の画像は見ていない） |

---

## 5. v2.1 の設計判断に効きうるもの

前提（依頼文のとおり）: ch ごとのソケット電源 ±12 V を TPS7A49 / TPS7A30 で ±15 V から作る。ADC の LDO は LT1763 で PD 12 V の枝から。DC-DC は RS6-1215D。TMUX7612 は ±15 V。

1. **ch ごとに電源を落とす構成と、入力ダイオード（O1〜O3）** — 効く、優先度は最も高い。
   NJM5532 の p6 は「V+ が開放で、入力に 1 kΩ 以上の抵抗が無く、入力と V− の差が大きいと焼損しうる」と書いている。
   v2.1 は「選んだ ch だけ電源と入力を生かす」構成なので、次の点を設計で決めておく必要がある。
   - 正負の LDO を必ず同時に落とすか（片側だけ生きている状態を作らない）
   - 電源を落とした ch の入力を、TMUX7612 などで確実に切り離すか
   - 切り離せない経路があるなら、非反転入力に 1 kΩ 以上の直列抵抗を置くか

   OPA1652 / OPA1612 の入力間ダイオードも、G = 1 のバッファで速い立ち上がりが来たときに 10 mA の制限がかかる。
   facts は 3 石とも「記述は無い」と書いていたので、facts を根拠に「入力保護は気にしなくてよい」と判断していたなら、その判断は根拠を失う。

2. **LDO の除去比を 200 kHz より上で見積もること（P2・P3・P8）** — 効く。
   - RS6 の内部動作周波数は **Min 200 kHz しか規定がない**（p2。Typ・Max は空欄）。リップルの基本波は 200 kHz より上にありうるし、高調波はさらに上に出る
   - TPS7A49 は 400 kHz で約 50 dB。TPS7A30 は 400 kHz で約 54 dB、700 kHz で約 45 dB（どちらも 10 µF / 10 nF / 10 nF のとき）。Features の「≥ 52 / ≥ 55 dB」で見積もると、700 kHz 付近で約 10 dB 楽観的になる
   - **LT1763 は 200 kHz で約 30 dB、1 MHz で約 22 dB** しかない（120 Hz の 50/65 dB とは別物）。PD 12 V の枝に DC-DC の反射リップルや PD 電源自体のスイッチングが乗るなら、LDO の前に LC か RC の前段フィルタを置くかどうかは、この数字で決まる
   - ただし、どのグラフも LDO の入出力差が 1〜1.2 V 程度の条件で測っている。v2.1 の入出力差（15→12 V で 3 V、12→5 V で 7 V）では、実際の除去比はこれより良い方に振れうる。DS にはその条件のグラフが無い

3. **LT1763 の出力コンデンサ（P9）** — 効く。
   ESR ≈ 0 のセラミックだけで組むなら、COUT は約 3〜6 µF 以上（CBYP による）が安定の条件で、CBYP ≥ 1000 pF なら DS の推奨は 6.8 µF。
   同じページの本文には「5 V レギュレータで使うと、16 V・10 µF の Y5V は DC バイアスと温度で実効 1〜2 µF まで下がりうる」とある（Figure 4・5）。
   X5R / X7R で、5 V バイアスをかけた実効値が 6.8 µF を割らない部品を選ぶこと。最大 ESR は 3 Ω。

4. **TMUX7612 の Ron（S1・S2）** — 効かない。
   ±15 V 電源で正側の Ron が底から離れ始めるのは約 +10.6 V、1.5 Ω を越えるのは約 +13.1 V。ここは facts と照合で一致している。
   ±12 V 電源の石の出力（最大でも ±11 V 程度）が来ると、正側の上端だけが Ron の立ち上がりの手前にかかる。これは facts の既存の行から言えることで、7.4 か 7.5 Ω か、0.95 か 1.1 Ω かは関係しない。

5. **最大出力レベルの見積もり（O4〜O7、O9a）** — 小〜中。
   ±15 V のグラフを ±12 V に読み替えるなら、OPA2604 はレールから約 3 V 手前（24 Vp-p）で、facts の 26 Vp-p では 1 V 楽観的だった。
   OPA1612 は負側 −14.3 V でレールまで 0.7 V（facts の −14.6 V では 0.4 V で、楽観的だった）。
   ±12 V で直接の資料があるのは LME49860 の Figure 4・8・12 と Fig 96（約 7.9 Vrms、THD+N 1 %）で、これは facts に足しておくとよい。
   OPA2134 の Headroom は ±18 V（または不明な条件）の値なので、±12 V の見積もりには使えない。

6. **その他（S3〜S6、P1、P4〜P7、P10〜P11、O8、O9b〜d）** — 設計判断には効かない。
   ただし次の 2 つは実装で踏みうる。
   - TBD62083A の tON/tOFF は VIH = 5.0 V での値。3.3 V ロジックで駆動するなら保証外。リレー駆動なので時間の差は実害にならない
   - MCP23017 の番地は、BANK = 0 の表から取ること
