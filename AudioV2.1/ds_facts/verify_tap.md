# 信号タップ候補 DS 事実表の独立照合（tap.md）

- 照合日: 2026-09-25
- 対象: `AudioV2.1/ds_facts/tap.md`（705 行。書き換えていない）
- DS: `AudioV2.1/datasheets/tap/` の 35 ファイル（tap.md の「取得元と版」の表のとおり）
- 照合の範囲: 比較を決める項目を持つ行 — THD / THD+N / SINAD / SNR / 高調波（値・列・レベル・周波数・測定帯域・負荷・利得）、雑音密度・帯域積分雑音、CMRR / CMR（周波数特性と信号源不整合を含む）、入力範囲・入力インピーダンス、バリア・絶縁・同相容量と巻線–シールド容量、絶縁側の電源の要否と電源電流、内蔵 DC/DC のスイッチング／搬送波周波数、ジッタ / TIE / PWD、データレート（ISO7741 の 50 / 100 Mbps の食い違いを含む）、トランスの THD（レベル・周波数、JT-11P-1 の 20 Hz 付近）と周波数特性。これらについての「DS に無い」の主張もすべて。
  範囲外の行（ゲイン誤差・オフセット・寸法・安全規格など）は、同じページを見たついでに目に入ったものだけ触れ、件数には入れていない。
- やり方: 出典のページを `pdftoppm -r 150` で画像にし、表の罫線・列見出し・表の見出し条件・脚注を目で確かめた。ADI のミラー版は挿入ページ（"Product Page Quick Links"）の有無を確かめ、PDF ページと印刷ページの両方を合わせた。
  「目読み」のグラフは **tap.md の数値を見る前に自分で読んだ**。300〜400 dpi で切り出し、グレースケールの PGM を素の Python で読み（PIL は壊れていた）、枠線と格子線の画素位置から軸を合わせ、指定周波数の列で曲線の画素を拾って換算した。細かい曲線の識別が必要な図（INA134 の高調波図の矢印、JT-11P-1 の +4 dBu 曲線）は 800 dpi まで拡大した。
  「DS に無い」の主張は、各 PDF の `pdftotext -layout` 全文を正規表現で探し、当たったページを画像で確かめた。作業ファイルは scratchpad の `verify_tap/` にある。
- 照合した件数: **369 件** = 出典と版 35 ＋ Q2 の行 77・「無い」6 ＋ Q3 の行 126・「無い」6 ＋ Q4 の行 76・「無い」4 ＋ Q5 の行 34・「無い」5
- 判定の内訳: **一致 333 ／ 一致・補足あり 23 ／ 誤り 13**（うち 3 件は出典ページだけの誤り）／ 条件の誤り 0 ／ 列の誤り 0 ／ 引用が無い 0 ／ 確かめられず 0

凡例: 「同上」は「tap.md の値・列・条件・ページのとおり」。引用は DS の画像から読んだ原文（`pdftotext` で化けた字は画像で直した）。

---

## 要約 — 比較（目標 約 −106 dBc、−3.4 dBFS・1320 Hz の H3 差の検出）を動かしうるもの

**誤り（13 件）**

| # | 部品 | tap.md の記述 | DS の実際 | 比較への影響 |
|---|---|---|---|---|
| 1 | **ISOW7741**（Q4-9） | 「ジッタ／tie — DS に無い」。Q4 のまとめでも「ISOW7741 はジッタ・tie の規定なし」 | **tie が規定されている**: 2^16−1 PRBS・100 Mbps で TYP **0.7 ns**（5 V、p27）/ **0.65 ns**（3.3 V、p28）/ 0.7 ns（2.5 V、p29）/ 0.7 ns（1.8 V、p30） | **Q4 を動かしうる。** DC/DC 内蔵の ISOW7741 は、tie が ISO7741（1.3〜1.5 ns）の約半分。「ISOW7741 はジッタが分からない」と読むと、DC/DC 内蔵案が不当に不利になる |
| 2 | Q4 のまとめ | 「規定があるのは ISO7741 / ISO7762 の tie と Si864x のピーク・アイ・ジッタ 350 ps だけ」 | 上の ISOW7741 の tie に加え、**Si860x の非 I2C チャネルにピーク・アイ・ジッタ TYP 350 ps**（p16 Table 5.4）がある。**ISO7762 には p25 Figure 5-17「Peak-to-Peak Output Jitter vs Data Rate」**（TA = 25 °C、典型値）があり、目読みで 10 Mbps 付近 約 0.75〜0.95 ns、100 Mbps で約 1.1〜1.3 ns | 同上。周期ジッタ／位相雑音の「規定」が無いのは正しい |
| 3 | Q4 のまとめ | 「ADuM1400、ADuM5401、ISOW7741 はジッタ・tie の規定なし」 | ADuM1400・ADuM5401 は正しい（全文に jitter / tie の語が無い）。ISOW7741 は誤り（#1） | 同上 |
| 4 | **HCPL-7800**（Q3 のまとめ） | 「雑音密度の表の値: … ACPL-C87x、HCPL-7800、Si8920 は密度なし」 | 表には無いが、**p19 の FAQ に入力換算の雑音密度がある**: "The noise spectral density is roughly 500 nV/√Hz below 20 kHz (input referred)."（印字は "nV/s Hz" の誤植）。ACPL-C87x と Si8920 は密度の記載が無いのを確かめた | 小。±200 mV 入力に対して 500 nV/√Hz は大きく、HCPL-7800 が −106 dBc に届かない結論は変わらない |
| 5 | **INA1620**（Q2-1）Figure 14 | 「20 Hz〜2 kHz で約 −128 dB（10 kΩ/2 kΩ/600 Ω 負荷、G = ±1）」 | 利得で 2 群に分かれていて、−128 dB はどちらでもない: **G = −1（破線）約 −126 dB、G = +1（実線）約 −132.5 dB**（20 Hz〜約 1 kHz で平坦。実線は 1 kHz から上がり、2 kHz で約 −131 dB）。400 dpi で読んだ | 小。内蔵抵抗で差動アンプを組むと反転構成に近いので、見るべきは G = −1 の −126 dB（THD+N、3.5 Vrms・80 kHz 帯域）。−106 dBc より十分に下なのは変わらない |
| 6 | **INA1650**（Q2-2）Figure 9 | 「REF/COM→GND: … 約 78 dB（100 kHz）」 | 100 kHz で **GND 接続 約 73 dB、VMID 接続 約 74 dB**（300 dpi で画素を拾った）。約 78 dB になるのは約 60 kHz。10 kHz の 88〜89 dB は正しい | 無し（1320 Hz とその高調波の帯域では 90 dB 前後で、tap.md の値のとおり） |
| 7 | **INA137**（Q2-4）高調波の図 | 「VO = 1Vrms の 2 次: … 1 kHz で約 0.00005 %」 | 1 kHz で **約 0.00007 %**（約 −123 dB。800 Hz 付近から平坦）。20 Hz の 0.00017〜0.00018 % は正しい | 小（約 3 dB の読み違い。−106 dBc との比較は変わらない） |
| 8 | **SSM2141**（Q2-6）THD の図 | 「RL = 600 Ω: 20 kHz で約 0.01 %」 | 600 Ω の曲線は **20 kHz で約 0.018 %**。0.01 % になるのは約 10 kHz。100 kΩ の値（低域 約 0.0008 %、20 kHz 約 0.002 %）は正しい | 無し（600 Ω 負荷・20 kHz は比較の条件から外れる） |
| 9 | **JT-11P-1**（Q5-1）左の図 | 「+4 dBu: 20 Hz 約 0.025 %、約 60 Hz で 0.004 %、約 130 Hz で 0.001 %」 | 20 Hz 約 0.023 %、60 Hz 約 0.0045 % は正しい。**130 Hz では約 0.0016 %**で、0.001 % まで下がるのは約 **240 Hz**（800 dpi で曲線の識別を確かめた） | 無し（1320 Hz は図の下限 0.001 % より下で、DS の規定は 1 kHz で "<0.001 %"） |
| 10 | Q5 のまとめ | 「20〜50 Hz での THD のグラフ: Jensen JT-11P-1 だけ」 | **Hammond 560G の p3 にも "560G Rs-150 Rl=150 THD+N" の図**（10 Hz〜100 kHz、0 / 10 / 27 dbm）がある。tap.md 自身が Q5-3 に載せている。ただし縦軸は線形で −20〜50「THD+N (%)」と壊れた表記で、数値としては使えない | 無し |
| 11 | SSM2143（Q2-7） | 5 Ω の不整合で 71 dB の本文を **p6** | 本文は **p7**（印刷 −7−、"APPLICATIONS INFORMATION" の CMRR の節）。値と引用は正しい | 無し（ページのみ） |
| 12 | ADuM1400（Q4-5） | 3 V の CRW の伝搬遅延 20 / 34 / 45 ns を **p8** | **p7**（Table 2 の続き）。値は正しい | 無し（ページのみ） |
| 13 | ADuM1400（Q4-5） | 3 V の CRW の PWD 0.5 / 2 ns を **p8** | **p7**。値は正しい（p8 にあるのは 3 V 表の Refresh Rate 1.1 Mbps） | 無し（ページのみ） |

**誤りではないが、比較の読み方を変える DS 上の情報（tap.md に無いもの。詳しくは最後の節）**

- **INA1650 の個別高調波（p24 Figure 57、1 kHz・22 dBu 出力）: HD2 −133.2 dBc、HD3 −142.1 dBc、HD4 −152.7 dBc。** tap.md が載せている INA1650 の THD+N（3 Vrms で −108.1 dB など）は、本文の説明（p23）のとおり**雑音が支配している値**で、H3 の −106 dBc と直接は比べられない。Q2 の比較には、この図と AD8274 Figure 36（H3 約 0.00023 %＝約 −113 dBc、10 Vp-p、G = ½）、INA134 / INA137 の高調波の図のほうが効く。
- **ISO7741 の 50 Mbps（推奨動作条件の表の MAX）** は、クロックを通すなら効く。クロックは 1 周期で 2 ビット分なので、24.576 MHz のクロックは 49.152 Mbps になる。表の 50 Mbps の内側だが余裕は 2 % 弱。注 (2) と Features・§8.2.3 は 100 Mbps。改訂履歴（Rev. J→K）はこの食い違いに触れていない。
- AD215 の**差動入力インピーダンス 16 MΩ**と**入力オペアンプの CMRR 100 dB**（PDF p3）、ADuM3190 の**オペアンプの Common-Mode Rejection 72 dB**（PDF p4）、HCPL-7800 の **Equivalent Input Impedance 500 kΩ**（p7）が tap.md に無い。どれも範囲内の項目だが、比較の結論は変わらない。

絶縁アンプ（Q3）の THD・SNR の行は全部一致した。どの品種も THD は −84〜−93 dB、SNR は 70〜85 dB で、−106 dBc から大きく離れている。

---

## 0. 出典と版

tap.md が「PDF 内の印字」とした版を、各 PDF の表紙・ページ下端・改訂履歴で確かめた。取得元 URL（ミラーかどうか）は tap.md の記載で、PDF から確かめられるのは版の印字だけ。

| ファイル | tap.md の版 | 判定 | PDF の実際 |
|---|---|---|---|
| TI_INA1620 | SBOS859B – MARCH 2018 – REVISED JULY 2018 | 一致 | 各ページの見出し |
| TI_INA1650 | SBOS818B – DEC 2016 – REVISED NOV 2018 | 一致 | 同上 |
| TI_INA134 | SBOS071（改訂日の印字なし。Burr-Brown 版） | 一致・補足あり | p1 下に "©1997 Burr-Brown Corporation PDS-1390A Printed in U.S.A. July, 1997"。改訂日ではないが、発行年月と PDS 番号の印字はある |
| TI_INA137 | SBOS072（同上） | 一致・補足あり | p1 下に "PDS-1391B Printed in U.S.A. July, 1997" |
| THAT_1200 | Document 600033 Rev 01（© 2017） | 一致 | 各ページ右上と下端 |
| ADI_SSM2141 | REV. C（ミラー） | 一致 | 各ページ下端。挿入ページは無い（PDF ページ＝印刷ページ） |
| ADI_SSM2143 | REV. 0（ミラー） | 一致 | 同上。挿入ページは無い |
| ADI_AD8274 | Rev. C（PDF p2 が挿入ページ、PDF p3 以降は印刷 +1） | 一致 | PDF p2 は "AD8274* Product Page Quick Links / Last Content Update: 11/01/2016"。PDF p4 の下端が "Rev. C \| Page 3 of 16" |
| TI_AMC1311 | SBAS786C – REVISED JUNE 2022 | 一致 | |
| TI_AMC1300 | SBAS895D – REVISED MAY 2022 | 一致 | |
| TI_ISO224 | SBAS738A – REVISED OCTOBER 2018 | 一致 | |
| TI_AMC3330 | SBASA34B – REVISED AUGUST 2024 | 一致 | |
| TI_AMC3336 | SBASA70 – APRIL 2021 | 一致 | |
| ADI_AD215 | REV. 0（© 1996。PDF p2 が挿入ページ "Last Content Update: 08/30/2016"。PDF p3 以降は印刷 +1） | 一致 | PDF p3 の下端が "–2–" |
| ADI_ADuM3190 | Rev. A（PDF p3 以降は印刷 +1） | 一致 | PDF p2 が挿入ページ（"Last Content Update: 08/30/2016"）。PDF p4 の下端が "Rev. A \| Page 3 of 18" |
| Broadcom_ACPL-C87x | AV02-3563EN（© 2016–2024） | 一致・補足あり | 表紙に発行日 "September 16, 2024" もある |
| Broadcom_HCPL-7800 | AV02-0410EN（© 2008–2020） | 一致・補足あり | 表紙に発行日 "November 19, 2020" もある |
| Skyworks_Si8920 | 206333A • July 26, 2022（ミラー） | 一致 | 各ページ下端 |
| TI_ISO7741 | SLLSEP4K – REVISED AUGUST 2026 | 一致 | 改訂履歴の最新が "Revision J (October 2024) to Revision K (August 2026)" |
| TI_ISO7762 | SLLSER1H – REVISED JANUARY 2024 | 一致 | |
| TI_ISO1540 | SLLSEB6F – REVISED DECEMBER 2022 | 一致 | |
| ADI_ADuM1250 | Rev. L（9/2025）（ミラー） | 一致 | 改訂履歴 "9/2025—Rev. K to Rev. L"。挿入ページは無い |
| ADI_ADuM1400 | Rev. M（2/2025）（ミラー） | 一致 | "2/2025—Rev. L to Rev. M"。挿入ページは無い |
| Skyworks_Si864x | 206329A • July 26, 2022（改訂履歴の最新 Revision 2.16） | 一致 | |
| Skyworks_Si860x | Rev. 206852A • February 23, 2024 | 一致 | |
| ADI_ADuM5401 | Rev. C（ミラー） | 一致 | 挿入ページは無い（PDF p4 ＝ "Rev. C \| Page 4 of 28"） |
| TI_ISOW7741 | SLLSFK1C – REVISED APRIL 2022（本文 © 2023） | 一致 | |
| TI_ISOW1044 | SLLSFF7B – REVISED AUGUST 2026 | 一致 | |
| Jensen_JT-11P-1 | 版の印字なし（PDF 作成日 2014-10-27） | 一致 | `pdfinfo` の CreationDate "Mon Oct 27 18:54:14 2014" |
| Lundahl_LL1540 | 右下に "R980616" | 一致 | |
| Hammond_560 | 版の印字なし | 一致 | |
| Hammond_560_series | © 2026 | 一致 | |
| Hammond_101-106 | © 2026 | 一致 | |
| Triad_TY-250P | Publish Date: May 31, 2019 | 一致 | |
| Triad_TY-146P | Publish Date: May 31, 2019 | 一致 | |

---

## Q2 差動抵抗タップ＋差動アンプ

### Q2-1. TI INA1620

| 項目 | tap.md の値 | 判定 | DS の実際（値・列・条件・ページ） | 根拠（原文の引用） |
|---|---|---|---|---|
| THD+N（2 kΩ） | 0.000025 % / −132 dB、TYP、G = 1, 1 kHz, 3.5 VRMS, 80 kHz | 一致 | p5。% は MIN〜MAX にまたがるセル、dB は TYP 列。表の見出しは RL = 1 kΩ だが行の条件が RL = 2 kΩ | "G = 1, f = 1 kHz, VOUT = 3.5 VRMS, RL = 2 kΩ, 80-kHz measurement bandwidth 0.000025% –132 dB" |
| THD+N（600 Ω） | 同、RL = 600 Ω | 一致 | p5 | 同表 |
| THD+N vs 周波数（Fig 14） | 20 Hz〜2 kHz で約 −128 dB（G = ±1） | **誤り** | p9 Figure 14。**G = −1 の 3 本（破線）が約 −126 dB、G = +1 の 3 本（実線）が約 −132.5 dB** に分かれる。負荷による差はほぼ無い。実線は 1 kHz から上がり、2 kHz で約 −131 dB、20 kHz で約 −118 dB | "Figure 14. THD+N Ratio vs Frequency" / "3.5 VRMS, 80-kHz measurement bandwidth" |
| 入力電圧雑音 | 2.1 µVPP、20 Hz〜20 kHz、TYP | 一致 | p5 | "Input voltage noise f = 20 Hz to 20 kHz 2.1 μVPP" |
| 入力電圧雑音密度 | 6.5 / 3.5 / 2.8 nV/√Hz | 一致 | p5。注 (2) "Specified by design and characterization" | 同上 |
| 入力電流雑音密度 | 1.6 / 0.8 pA/√Hz | 一致 | p5 | 同上 |
| CMRR（オペアンプ単体） | 108 / 127 dB、MIN / TYP | 一致 | p5。条件に TA = –40〜125 °C が入っているのも原文どおり | "(V–) + 1.5 V ≤ VCM ≤ (V+) – 1 V, TA = –40°C to 125°C, VS = ±18 V 108 127 dB" |
| CMRR vs 周波数（Fig 22） | 約 127（〜100 Hz）/ 115（1 kHz）/ 97（10 kHz）/ 78（100 kHz） | 一致 | p10。自分の読み（300 dpi）: 127 / 117 / 97 / 76 dB | "Figure 22. CMRR vs Frequency (Referred to Input)" |
| 入力インピーダンス | 差動 60k ‖ 0.8、同相 500M ‖ 0.9（Ω ‖ pF）、TYP | 一致 | p6 | "Differential 60k \|\| 0.8 / Common-mode 500M \|\| 0.9" |
| 抵抗ペアの比マッチング | 0.004 % / 0.02 %（全温度で max 0.023 %） | 一致 | p6、注 (3) | "Resistors in same pair 0.004% 0.02%" |
| ⚠ 差動アンプを組んだときの CMRR は規定なし（冒頭の注意） | — | 一致・補足あり | 規定は無い（全文検索）。ただし p21 §8.1.2 に **Figure 52「Matching Histogram, Maximum to Minimum」**（同じ石の全抵抗の最大と最小のマッチング、典型分布）があり、分布の山は約 0.15〜0.3 %、裾は約 1.5 % まで。ペア内（0.004 %）より 2 桁悪い。ペアの外で比を作る結線では、こちらが効く | "Figure 52 shows a typical distribution of the worst-case matching across all resistors on a single INA1620." |

### Q2-2. TI INA1650 / INA1651

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| THD+N（3 Vrms） | 0.00039 % / −108.1 dB、TYP、90 kHz、±18 V | 一致 | p6 | "VO = 3 VRMS, f = 1kHz, 90-kHz measurement bandwidth, VS = ±18 V 0.00039% –108.1 dB" |
| THD+N（22 dBu） | 0.000174 % / −115.2 dB | 一致 | p6 | "VIN = 22 dBu (9.7516 VRMS) , FIN = 1 kHz …" |
| THD+N vs 周波数（Fig 12） | 20 Hz〜10 kHz で約 0.0004 %（約 −108 dB）、ほぼ平坦 | 一致・補足あり | p9。2 kΩ は −108.1 dB で平坦。**600 Ω は 20 Hz で約 −106.4 dB、10 kHz で約 −105.5 dB**（両端で少し上がる） | "3 VRMS, 90-kHz Measurement Bandwidth" |
| THD+N vs 出力振幅（Fig 14） | 1 Vrms で約 −100 dB、10 Vrms 付近で約 −112 dB | 一致・補足あり | p10。1 Vrms で −100 dB。**最小は約 9.8 Vrms の約 −115 dB**で、そこから約 −112 dB に跳ね、約 12 Vrms でクリップ | "1 kHz, 90-kHz Measurement Bandwidth" |
| 出力電圧雑音 | 4.5 µVRMS / −104.7 dBu | 一致 | p6 | "f = 20 Hz to 20 kHz, no weighting 4.5 μVRMS –104.7 dBu" |
| 出力電圧雑音密度 | 47 / 31 nV/√Hz | 一致 | p6 | 同上 |
| CMRR（REF/COM→GND） | 85 / 91 dB（全温度 82 / 89） | 一致 | p6 | "REF and COM pins connected to ground, VS = ±18 V 85 91 dB" |
| CMRR（→VMID） | 82 / 86 dB（全温度 76 / 84） | 一致 | p6 | 同上 |
| CMRR（RS 不整合 20 Ω） | 84 dB、TYP | 一致 | p6 | "RS mismatch = 20 Ω 84" |
| CMRR vs 周波数（Fig 9） | GND: 約 91（10 Hz〜1 kHz）/ 88（10 kHz）/ **78（100 kHz）**。VMID: 約 86（〜10 kHz） | **誤り**（100 kHz のみ） | p9。300 dpi で画素を拾った: GND 90.9（1.35 kHz）/ 89.0（10.5 kHz）/ **73.3（105 kHz）**。VMID 86.0（1.35 kHz）/ 85.3（10.5 kHz）/ 74.4（105 kHz） | "Figure 9. Common-Mode Rejection Ratio vs Frequency" |
| CMRR と RCOM（本文） | 92 → 83.7 dB（RCOM = 0）、89.6 dB（1 MΩ） | 一致 | p18 §8.1.2 | 原文どおり |
| 入力インピーダンス | 差動 850 / 1000 / 1150 kΩ、同相 212.5 / 250 / 287.5 kΩ | 一致 | p7 | 同上 |
| 入力抵抗の不整合 | 0.01 % / 0.25 % | 一致 | p7 | "Input resistance mismatch 0.01% 0.25%" |
| 利得非直線性 | 1 / 5 ppm | 一致 | p6 | "VS = ±18 V, –10 V < VO < 10 V 1 5 ppm" |

### Q2-3. TI INA134 / INA2134

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| THD+N | 0.0005 %、TYP、1 kHz、VIN = 10 Vrms（帯域の記載なし） | 一致 | p2 | "Total Harmonic Distortion + Noise, f = 1kHz VIN = 10Vrms 0.0005" |
| Noise Floor | −100 dBu、20 kHz BW | 一致 | p2。注 (1) は dBu の定義 | "Noise Floor(1) 20kHz BW –100" |
| 出力雑音電圧 | 7 µVrms / 52 nV/√Hz | 一致 | p2、注 (2) | 同上 |
| CMR | 74 / 90 dB、VCM = ±31 V、RS = 0 Ω | 一致 | p2 | 同上 |
| CMR vs 周波数 | 約 90（1〜10 kHz）/ 86（20 kHz）/ 70（100 kHz） | 一致・補足あり | p5。画素で拾った値: 90.6（2〜5 kHz）/ 90.0（10 kHz）/ **84.7（20 kHz）** / 70.5（100 kHz） | "COMMON-MODE REJECTION vs FREQUENCY" |
| CMR と信号源不整合（本文） | 10 Ω で約 74 dB | 一致 | p8 | 原文どおり |
| THD+N vs 周波数 | VO = 10 Vrms、〜5 kHz で 0.0005〜0.0006 %、20 kHz で 0.001〜0.002 % | 一致 | p4。自分の読み: 平坦部 0.00052 %、20 kHz で 0.0011〜0.0015 % | "VO = 10Vrms" |
| 高調波成分 vs 周波数 | 1 Vrms・2 kΩ の 2 次: 1 kHz で約 0.00006 %。noise limited 約 0.00004 % | 一致 | p4。800 dpi で矢印を確かめた: "RL = 2kΩ, 2nd Harmonic" の矢印は 1 kHz で約 0.000065 % の曲線を指す。600 Ω の 2 次は約 0.00009 %。noise limited（2 kΩ の 3 次）約 0.00004 % | "HARMONIC DISTORTION PRODUCTS vs FREQUENCY" / "VO = 1Vrms" |
| 入力インピーダンス | 差動・同相とも 50 kΩ、注 (4) | 一致 | p2 | "(4) 25kΩ resistors are ratio matched but have ±25% absolute value." |
| 非直線性 | 0.0001 %、TYP | 一致 | p2 | 同上 |

### Q2-4. TI INA137 / INA2137

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| THD+N | 0.0005 %、1 kHz、VIN = 10 Vrms | 一致 | p2 | 同上 |
| Noise Floor, RTO | −106 dBu | 一致 | p2 | 同上 |
| 出力雑音電圧 | 3.5 µVrms / 26 nV/√Hz | 一致 | p2 | 同上 |
| CMR | 74 / 90 dB、VCM = ±46.5 V | 一致 | p2 | 同上 |
| CMR vs 周波数（RTO） | 約 90 dB（1 kHz〜約 90 kHz）、1 MHz で約 64 dB | 一致・補足あり | p5。画素で拾った値: 90.9 dB は約 60 kHz まで。**95 kHz では 87.7 dB**、105 kHz 86.7、210 kHz 80.0、950 kHz 64.5 dB | "COMMON-MODE REJECTION vs FREQUENCY" / "RTO" |
| CMR と信号源不整合（本文） | 5 Ω で約 77 dB（RTO） | 一致 | p8 | 同上 |
| THD+N vs 周波数 | VO = 5 Vrms、約 0.0005 %、20 kHz で約 0.001 % | 一致 | p4。平坦部 0.00054 %、20 kHz で 0.0008〜0.001 % | "VO = 5Vrms" |
| 高調波成分 vs 周波数 | 1 Vrms の 2 次: 20 Hz で約 0.00017 %、**1 kHz で約 0.00005 %** | **誤り**（1 kHz のみ） | p4。400 dpi で読んだ: 20 Hz 0.00018 %、**1 kHz 約 0.00007 %**（約 800 Hz から平坦）。3 次（noise limited）は約 0.00004 % | "HARMONIC DISTORTION PRODUCTS vs FREQUENCY" |
| 入力インピーダンス | 差動 24 kΩ、同相 18 kΩ | 一致 | p2 | 同上 |

### Q2-5. THAT 1200 / 1203 / 1206

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 入力インピーダンス | 差動 48.0 kΩ、同相（bootstrap）10.0 MΩ @60 Hz / 3.2 MΩ @20 kHz、Typ | 一致 | p2 | 同上 |
| CMRR1 | DC 70/90、60 Hz 70/90、20 kHz —/85 | 一致 | p2 | 同上 |
| CMRR_IEC（10 Ω 不整合） | 90 / 90 / 85、Typ | 一致 | p2、注 5 | "Per IEC Standard 60268-3 for testing CMRR of balanced inputs." |
| CMRR2（600 Ω 不整合） | 60 Hz 70、20 kHz 65 | 一致 | p2 | 同上 |
| 入力電圧範囲 | 同相 ±12.5 / ±13.0 V、差動 21.0 / 21.5 dBu（1200） | 一致 | p2。差動は "equal and opposite swing" | 同上 |
| THD | 0.0005 %、10 dBu、BW = 20 kHz、1 kHz、2 kΩ | 一致 | p3 | 同上 |
| 出力雑音 | −105 / −104 / −106 dBu、BW = 20 kHz | 一致 | p3 | 同上 |

### Q2-6. ADI SSM2141

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| CMR | 80 / 100 dB（全温度 75 / 90） | 一致 | p2 | "COMMON-MODE REJECTION CMR VCM = ±10 V 80 100" |
| CMR（Features） | DC 100、60 Hz 100、20 kHz 70、40 kHz 62 dB typ | 一致 | p1 | 同上 |
| CMR vs 周波数 | 約 100 dB（〜1 kHz）/ 72（20 kHz）/ 55（100 kHz） | 一致・補足あり | p3。400 dpi で読んだ: 100 dB で平坦なのは約 200 Hz まで、**1 kHz で約 96 dB**、20 kHz 約 72 dB、**100 kHz 約 58 dB** | "Common-Mode Rejection vs. Frequency" |
| CMR と信号源不整合（本文） | 5 Ω で DC CMR が 20 dB 劣化 | 一致 | p6 | 同上 |
| THD | 0.001 %（100 kΩ）/ 0.01 %（600 Ω）、振幅・周波数・帯域なし | 一致 | p2 | 同上 |
| THD+N vs 周波数（AP 画面） | 100 kΩ: 20 Hz〜1 kHz 約 0.001 %、20 kHz 約 0.002 %。**600 Ω: 20 kHz で約 0.01 %** | **誤り**（600 Ω のみ） | p3。400 dpi で読んだ: 低域は両負荷とも約 0.0008 %、100 kΩ の 20 kHz は約 0.002 %。**600 Ω は 20 kHz で約 0.018 %、10 kHz で約 0.01 %**（1 kHz から上がり始める） | "Total Harmonic Distortion vs. Frequency" |
| 電圧雑音密度 | 約 22 nV/√Hz（約 200 Hz 以上） | 一致 | p5。約 21 nV/√Hz で、約 100 Hz から平坦 | "Voltage Noise Density vs. Frequency" |
| 内部抵抗（ブロック図） | 25 kΩ × 4、表に入力インピーダンスは無い | 一致 | p1 | 同上 |

### Q2-7. ADI SSM2143

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| THD+N | 0.0006 %、10 V rms、10 kΩ、1 kHz | 一致 | p2 | 同上 |
| SNR | −107.3 dBu、20 kHz BW、RTI | 一致 | p2 | 同上 |
| THD+N vs 周波数（Fig 3） | 20 Hz 約 0.0008 %、100 Hz〜2 kHz 約 0.0006 %、20 kHz 約 0.002〜0.004 % | 一致 | p3。自分の読み: 0.0007 / 0.0006 / 0.0019〜0.0035 % | "Figure 3. THD+N vs. Frequency (VS = ±15 V, VIN = 10 V rms, with 80 kHz Filter)" |
| CMR | dc 70/90、60 Hz 90、20 kHz 85、400 kHz 60 | 一致 | p2 | 同上 |
| CMR vs 周波数（Fig 10） | 約 88 dB（〜10 kHz）、約 70 dB（100 kHz） | 一致 | p4。88 dB / 約 70 dB | 同上 |
| CMR と信号源不整合（本文） | 5 Ω で dc 71 dB、**p6** | **誤り**（ページのみ） | **p7**（印刷 −7−）。値と引用は正しい | "a 5 Ω source imbalance will result in a CMRR of 71 dB at dc" |
| 電圧雑音密度（Fig 16） | 約 14 nV/√Hz（1 kHz） | 一致 | p5。13.7 nV/√Hz | 同上 |
| 入力電圧範囲 | 同相 ±15 V、差動 ±28 V、Typ | 一致 | p2 | 同上 |
| 内部抵抗（ブロック図） | 12 kΩ / 6 kΩ、REF 入力抵抗 18 kΩ | 一致 | p1、p2 | 同上 |

### Q2-8. ADI AD8274

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| THD + Noise | G = ½ 0.00025 %、G = 2 0.00035 %、1 kHz、10 V p-p、600 Ω | 一致 | PDF p4（印刷 p3） | 同上 |
| Noise Floor, RTO | −106 / −100 dBu | 一致 | PDF p4 | 同上 |
| 出力電圧雑音 | 3.5 / 7 µV rms、26 / 52 nV/√Hz | 一致 | PDF p4、注 1 | 同上 |
| CMRR | 77/86（G = ½）、83/92（G = 2）、VCM = ±40 V、RTI | 一致 | PDF p4 | 同上 |
| CMRR vs 周波数（Fig 15） | G = ½ 約 94 dB（〜約 15 kHz）、100 kHz 約 80。G = 2 約 100 dB（〜約 15 kHz） | 一致・補足あり | PDF p8（印刷 p7）。G = ½ は約 94.4 dB で**約 25 kHz まで平坦**、G = 2 は約 99.6 dB で約 13 kHz まで。100 kHz では両方とも約 82 dB | 同上 |
| THD + N vs 周波数（Fig 32） | G = ½ 約 0.00025 %、G = 2 約 0.00035 % | 一致 | PDF p11（印刷 p10）。画素で拾った値: G = ½ 0.00023 %、G = 2 0.00033 %（25 Hz〜19 kHz でほぼ一定） | "Figure 32. THD + N vs. Frequency, Filter = 22k Hz" |
| 高調波成分（Fig 36、G = ½） | 3 次 約 0.00025 %、2 次 600 Ω 約 0.00005 %、2 次 100 kΩ/2 kΩ 約 0.00002 % | 一致 | PDF p12（印刷 p11）。自分の読み: 0.00023 / 0.000045 / 0.000017 %。10 kHz から上で増える | "Figure 36. Harmonic Distortion Products vs. Frequency, G = ½" / "GAIN = ½ VOUT = 10V p-p" |
| 入力インピーダンス | G = ½ 差動 36 kΩ・同相 9 kΩ、G = 2 差動 9 kΩ・同相 9 kΩ、注 5・6 | 一致 | PDF p4 | 同上 |
| 利得非直線性 | 2 ppm | 一致 | PDF p4 | 同上 |

### Q2 で「DS に無い」とされた項目

| 主張 | 判定 | 確かめた内容 |
|---|---|---|
| INA1620: 内蔵抵抗で差動アンプを組んだときの CMRR | 一致・補足あり | CMRR の値は無い（全文検索。§8.3.1 の本文は定性的に "high common-mode rejection" と言うだけ）。ペアの外の抵抗どうしのマッチングは p21 Figure 52 に典型分布がある（上の表） |
| INA134 / INA137: THD+N の測定帯域 | 一致 | 表・グラフとも無い。"BW = 100kHz" は DIM の図だけ。INA134 p8 の本文に "Up to approximately 10kHz distortion is below the measurement limit of commonly used test equipment." |
| SSM2141: THD の振幅・周波数・帯域、入力インピーダンス、雑音密度の表の値 | 一致 | 3 つとも表に無い。表にある入力関係は IVR ±10 V（Min、注 1 "Guaranteed by CMR test"）だけ |
| SSM2143: 入力インピーダンスの表の値 | 一致 | 表にあるのは REFERENCE 入力抵抗 18 kΩ だけ |
| THAT 1200: 雑音密度、CMRR・THD の周波数特性グラフ | 一致 | DS の図は等価回路・試験回路・応用回路だけ。本文 p7 に「RFI 用コンデンサで同相入力インピーダンスが 20 kHz で約 80 kΩ に下がる」という記述がある |
| どの DS にも 20〜50 Hz・7〜9 Vpk での THD の規定値は無い（読めるグラフの列挙） | 一致・補足あり | 規定値が無いのは正しい。グラフの列挙からは **SSM2141 の THD vs 周波数（p3、振幅不明）** と **INA1650 p24 Figure 54（4 dBu と 22 dBu で 20 Hz から。22 dBu は 20 Hz で約 −111 dB）** が漏れている |

---

## Q3 アイソレーション・アンプ

### Q3-1. TI AMC1311 / AMC1311B

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 高圧側電源 VDD1 | 4.5/5/5.5 V（1311）、3/5/5.5 V（1311B） | 一致 | p6 §7.3 | 同上 |
| 低圧側電源 VDD2 | 3 / 3.3 / 5.5 V | 一致 | p6 | 同上 |
| VFSR | −0.1〜2 V | 一致 | p6 | 同上 |
| クリップ前入力 | 2.516 V、NOM | 一致 | p6 | 同上 |
| 入力抵抗 | 1 GΩ、TYP | 一致 | p10。入力容量は 7 pF（fIN = 275 kHz） | "RIN Input resistance TA = 25℃ 1 GΩ" |
| 非直線性 | −0.04 / ±0.01 / 0.04 % | 一致 | p10 | "Nonlineartity(1)"（原文の綴り） |
| THD | −87 dB、2 VPP、VIN > 0 V、10 kHz、BW = 10 kHz、注 4（5 次まで） | 一致 | p10、注 (4) は p11 | "THD is the ratio of the rms sum of the amplitudes of first five higher harmonics to the amplitude of the fundamental." |
| SNR（1 kHz） | 79 / 82.6 dB、BW = 10 kHz | 一致 | p10 | 同上 |
| SNR（10 kHz） | 70.9 dB、BW = 100 kHz | 一致 | p10 | 同上 |
| 出力雑音 | 220 µVrms、BW = 100 kHz | 一致 | p10 | 同上 |
| 入力換算雑音密度（Fig 7-23） | 約 0.5 µV/√Hz（0.1〜30 kHz）、100 kHz 超で上昇 | 一致 | p17。自分の読み: 0.49 µV/√Hz。約 50 kHz から上がり始める | 同上 |
| THD vs 電源電圧（Fig 7-21） | 約 −85〜−88 dB | 一致 | p16。VDD1 に対し −84.6〜−88.1、VDD2 に対し −87.0〜−88.2 dB。見出し条件は fIN = 10 kHz、BW = 100 kHz | 同上 |
| バリア容量 CIO | ~1.5 pF、値の列のみ | 一致 | p8。列見出しは PARAMETER / TEST CONDITIONS / VALUE / UNIT | "CIO VIO = 0.5 VPP at 1 MHz ~1.5 pF" |
| IDD1 | 7.1 / 9.7 mA（4.5〜5.5 V） | 一致 | p11。1311B の 3.0〜3.6 V は 6.0 / 8.4 mA（tap.md には無い） | 同上 |
| IDD2 | 5.3 / 7.2、5.9 / 8.1 mA | 一致 | p11 | 同上 |
| 高圧側電源の作り方（本文） | VDD2 から絶縁 DC/DC（SN6501） | 一致 | p27 | 同上 |
| 内部の周波数（本文） | ΔΣ 20 MHz（p25）、搬送波 480 MHz（p21） | 一致 | 同上 | 同上 |

### Q3-2. TI AMC1300 / AMC1300B

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| VFSR | −250〜250 mV | 一致 | p5 | 同上 |
| 動作同相入力 | −0.16〜VDD1 − 2.1 V | 一致 | p5 | 同上 |
| 入力抵抗 | 片側 19 kΩ、差動 22 kΩ | 一致 | p9 | 同上 |
| 非直線性 | −0.03 / ±0.01 / 0.03 % | 一致 | p9 | 同上 |
| THD | −85 dB、fIN = 10 kHz、注 3 | 一致 | p9、注 (3) は p10（5 次まで） | 同上 |
| SNR | 81.5 / 85（1 kHz、10 kHz BW）、72（10 kHz、100 kHz BW） | 一致 | p9。改訂履歴に "Changed SNR (min), fIN = 1 kHz from 80 dB to 81.5 dB" | 同上 |
| 出力雑音 | 230 µVRMS | 一致 | p9 | 同上 |
| 入力換算雑音密度（Fig 7-26） | 約 70（軸は µV/√Hz） | 一致 | p16。約 68、約 50 kHz から上がる。軸の単位の印字も原文どおり | 同上 |
| CMRR | −100 dB（0 Hz）、−98 dB（10 kHz） | 一致 | p9 | 同上 |
| バリア容量 CIO | ~1.5 pF | 一致 | p7。改訂履歴に "Changed CIO from ~1 pF to ~1.5 pF" | 同上 |
| 電源電流 | IDD1 7.2 / 9.8、IDD2 5.3 / 7.2 mA | 一致 | p10 | 同上 |
| 高圧側電源 | "High-side supply (3.3 V or 5 V)" | 一致 | p1 | 同上 |
| 搬送波 | 480 MHz | 一致 | p21 | 同上 |

### Q3-3. TI ISO224A / B

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| VDD1 | 4.5 / 5 / 18 V | 一致 | p4 | 同上 |
| VDD2 | 4.5 / 5 / 5.5 V | 一致 | p4 | 同上 |
| VFSR | −12〜12 V | 一致 | p4 | 同上 |
| クリップ前 | ±13.8 V | 一致 | p4 | 同上 |
| 入力抵抗 | 1 / 1.25 MΩ | 一致 | p7 | 同上 |
| 入力換算雑音密度 | 3（B）/ 4（A）µV/√Hz、TYP | 一致 | p7 | 同上 |
| 非直線性 | B ±0.003（max 0.01）、A ±0.003（max 0.02）% | 一致 | p8 | 同上 |
| THD | −84 dB、fIN = 10 kHz | 一致 | p8。脚注は無い | 同上 |
| THD vs 電源（Fig 26, 27） | VDD1 に対し約 −84 一定、VDD2 4.5 V 約 −93〜5.5 V 約 −81 | 一致 | p14。自分の読み: −92.5 / −81.1 dB | 同上 |
| 出力雑音 | 300 / 360 µVRMS | 一致 | p8 | 同上 |
| CIO | ~1 pF | 一致 | p6 | 同上 |
| 電源電流 | IDD1 6.1 / 7.8、IDD2 7.8 / 9.9 mA | 一致 | p8 | 同上 |
| 高圧側電源の作り方（本文） | 絶縁 DC/DC で作るのが典型 | 一致 | p25 | 同上 |
| SNR — DS に無い | — | 一致 | 全文に signal-to-noise / SNR / SINAD の語が無い | — |

### Q3-4. TI AMC3330

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | VDD 3.0 / 3.3 / 5.5 V のみ | 一致 | p4 | 同上 |
| VFSR / クリップ | −1〜1 V / ±1.25 V | 一致 | p4 | 同上 |
| 動作同相入力 | −1.4〜1.6 V、−0.925〜0.725 V | 一致 | p4 | 同上 |
| 入力抵抗 | 片側 0.1 / 0.8 GΩ、差動 0.1 / 1.2 GΩ | 一致 | p8 | 同上 |
| 非直線性 | −0.02 / 0.01 / 0.02 % | 一致 | p8 | 同上 |
| SNR（1 kHz） | 81 / 85 dB、10 kHz filter | 一致 | p8 | 同上 |
| SNR（10 kHz） | 72 dB、1 MHz filter | 一致 | p8 | 同上 |
| THD | −84 dB、2 Vpp、10 kHz、BW = 100 kHz | 一致 | p8、注 (3) は p9 | 同上 |
| 出力雑音 | 250 µVRMS | 一致 | p8 | 同上 |
| 入力換算雑音密度（Fig 5-29） | 約 300 nV/√Hz | 一致 | p16。約 310、約 50 kHz まで平坦 | 同上 |
| CMRR | −100 / −86 dB | 一致 | p8 | 同上 |
| CMRR vs 周波数（Fig 5-30） | 約 −102（〜1 kHz）、10 kHz で約 −85 | 一致 | p16。約 −101 / −86 dB。約 400 kHz で約 −41 dB まで悪化する | 同上 |
| CIO | ~4.5 pF | 一致 | p6。改訂履歴に "Updated Barrier capacitance specification from 3.5 pF to 4.5 pF" | 同上 |
| IDD | 28.5 / 41、30.5 / 43 mA | 一致 | p9 | 同上 |
| IH | 1 / 4.3 mA、MAX | 一致 | p9 | 同上 |
| DC/DC の方式（本文） | spread-spectrum、同期、周波数の数値は無い | 一致・補足あり | p22。数値は無い。ただし同期先の ΔΣ 変調器のサンプリング周波数 20 MHz は p25 の本文にある（"sampling frequency (20 MHz) of the internal ΔΣ modulator"） | 同上 |
| EMI（Features） | CISPR-11 / CISPR-25 | 一致 | p1 | 同上 |
| 搬送波 | 480 MHz | 一致 | p19 | 同上 |

### Q3-5. TI AMC3336

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 入力クロック | 9 / 20 / 21 MHz | 一致 | p4 | 同上 |
| VFSR | −1〜1 V | 一致 | p4 | 同上 |
| 入力抵抗 | 0.06 / 1 GΩ | 一致 | p8 | 同上 |
| SNR | 80 / 84 dB | 一致 | p8（sinc3、OSR = 256 は表の見出し条件） | 同上 |
| SINAD | 77 / 84 dB | 一致 | p8 | 同上 |
| THD | −93 / −80 dB、TYP / MAX | 一致 | p8 | 同上 |
| SFDR | 79 / 96 dB | 一致 | p8 | 同上 |
| SNR・SINAD vs 周波数（Fig 6-20） | SNR 約 84、SINAD 約 83.5 → 10 kHz で約 80.5 | 一致 | p14。83.9 / 83.5 / 80.4 dB | 同上 |
| 雑音密度（Fig 6-34） | 約 1〜2 × 10² nVrms/√Hz | 一致 | p16。約 190 nVrms/√Hz、約 30 kHz から上がる | 同上 |
| INL | 差動 ±4、単端 ±6 LSB | 一致 | p8 | 同上 |
| CMRR | −104（0 Hz）、−89 dB（10 kHz） | 一致 | p8 | 同上 |
| CIO | ~4.5 pF | 一致 | p6 | 同上 |
| IDD | 28.5 / 42.5、30.5 / 44.5 mA | 一致 | p9 | 同上 |
| DC/DC の方式（本文） | spread-spectrum、周波数の数値は無い | 一致・補足あり | p23。数値は無い。変調器のクロックは外部 CLKIN（9〜21 MHz、公称 20 MHz） | 同上 |
| 搬送波 | 480 MHz | 一致 | p21 | 同上 |

### Q3-6. ADI AD215

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源電圧 | ±14.5 / ±15 / ±16.5、動作 ±14.25〜±17 V dc | 一致 | PDF p4（印刷 −3−） | 同上 |
| 電源電流 | +40 / −18 mA、Typ | 一致 | PDF p4 | 同上 |
| 入力電圧範囲 | ±10 V、Min | 一致 | PDF p3（印刷 −2−） | 同上 |
| 非直線性 | BY ±0.005 / ±0.015、AY ±0.01 / ±0.025 % | 一致 | PDF p3 | 同上 |
| 高調波成分 | −80 dB @1 kHz、−65 dB @10 kHz、2 kΩ Load | 一致 | PDF p4。振幅の記載は無い（DYNAMIC RESPONSE (2 kΩ Load) の見出しの下） | "Harmonic Distortion Components @ 1 kHz –80 dB / @ 10 kHz –65 dB" |
| 入力電圧雑音 | 20 nV/√Hz、> 10 Hz | 一致 | PDF p3 | 同上 |
| 出力リップル＆雑音 | 10 / 2.5 mV pk-pk、注 7 | 一致 | PDF p4 | 同上 |
| 帯域 | 100 / 120 kHz | 一致 | PDF p3 | 同上 |
| IMRR | 120/100/80、105/85/65 dB | 一致 | PDF p3 | 同上 |
| 同相入力インピーダンス | 2 ‖ 4.5 GΩ ‖ pF | 一致・補足あり | PDF p3。同じ枠に **差動 16 MΩ（G = 1 V/V）** もあるが tap.md に無い。1 行上に **"CMRR of Input Op Amp 100 dB"** もある | "INPUT IMPEDANCE Differential G = 1 V/V 16 MΩ / Common Mode 2‖4.5 GΩ‖pF" |
| 同相容量（本文） | 4.5 pF（dc/dc の絶縁を含む） | 一致 | PDF p1 | 同上 |
| 絶縁側電源（出力） | ±14.25 / ±15 / ±17.25 V、±10 mA、Min / Typ / Max | 一致・補足あり | PDF p4。電圧は Min / Typ / Max、**電流 ±10 mA は Typ 列だけ**。注 9: 電源電圧 ±15 V 以上なら ±15 mA まで取れる | "9 With an input power supply voltage greater than or equal ±15 V dc, the AD215 may supply up to ±15 mA from the isolated power supplies." |
| 絶縁側電源のリップル | 50 mV rms | 一致 | PDF p4 | 同上 |
| 搬送波・電源発振 | 約 430 kHz、図の "430kHz"、LPF "150kHz" | 一致 | PDF p5（本文）、PDF p1（図） | 同上 |
| CIO の表の値 — DS に無い | — | 一致 | 容量の表の値は無い | — |

### Q3-7. ADI ADuM3190

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | 側 1・側 2 とも 3.0〜20 V | 一致 | PDF p5（印刷 p4） | 同上 |
| 電源電流 | IDD1 1.4 / 2.0、IDD2 2.9 / 5.0 mA | 一致 | PDF p5 | 同上 |
| 出力直線性 | −1.0 / +0.15 / +1.0 % | 一致 | PDF p4 | 同上 |
| 雑音 | EAOUT 1.7、EAOUT2 4.8 mV rms、帯域の記載なし | 一致 | PDF p4。参照先の Figure 15（PDF p11）はオシロの波形（10 mV/DIV）で帯域の記載は無い | 同上 |
| 入力範囲（op amp 同相） | 0.35〜1.5 V | 一致 | PDF p4。同じ OP AMP の枠に **Common-Mode Rejection 72 dB（Typ）** があるが tap.md に無い | 同上 |
| CI-O | 2.2 pF、f = 1 MHz、Typ | 一致 | PDF p6（印刷 p5） | 同上 |
| 絶縁アンプ回路（本文） | ユニティ・バッファ、約 400 kHz の極 | 一致 | PDF p15（印刷 p14）。どちらの文も同じページ | 同上 |
| THD / SNR — DS に無い | — | 一致 | 全文に distortion / THD / SNR の語が無い | — |

### Q3-8. Broadcom ACPL-C87B / C87A / C870

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | VDD1 4.5〜5.5、VDD2 3.0〜5.5 V | 一致 | p5 | 同上 |
| 入力範囲 | 0〜2.0 V、注 a（FSR 2.46 V） | 一致 | p5 | 同上 |
| 非直線性 | 0.05 / 0.1 % | 一致 | p6 | 同上 |
| 入力インピーダンス | 1000 MΩ、Typ | 一致 | p6 | 同上 |
| 出力雑音 | 0.013 mVrms、180 kHz LPF、注 d | 一致 | p6 | 同上 |
| AC 雑音 vs フィルタ周波数（Fig 12） | 20 kHz で Vin 0 V ほぼ 0、1 V 約 2.2、2 V 約 4.5 mVrms | 一致 | p9。自分の読み: 約 0 / 2.15 / 4.4 mVrms | "Figure 12: AC Noise vs. Filter Freq vs. Vin" |
| CI-O | 0.5 pF | 一致 | p7 | 同上 |
| 電源電流 | IDD1 10.5 / 15、IDD2 6.5 / 12・6.1 / 11 mA | 一致 | p7 | 同上 |
| THD / SNR — DS に無い | — | 一致 | 全文に harmonic / distortion / SNR の語が無い | — |

### Q3-9. Broadcom HCPL-7800A / HCPL-7800

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | 4.5〜5.5 V | 一致 | p6 | 同上 |
| 入力（線形） | −200〜200 mV | 一致 | p6。p7 に "Maximum Input Voltage before VOUT Clipping 308.0 mV"、**"Equivalent Input Impedance 500 kΩ"**（tap.md に無い） | 同上 |
| 非直線性 | 0.0037 / 0.35、0.0027 / 0.2 % | 一致 | p7 | 同上 |
| 出力雑音 | 31.5 mVrms、VIN+ = 0 V、注 a | 一致 | p8 | 同上 |
| 入力 DC 同相除去 | 76 dB、注 k | 一致 | p7 | 同上 |
| CI-O | 1.2 pF | 一致 | p9 | 同上 |
| 電源電流 | IDD1 10.86 / 16.0、IDD2 11.56 / 16.0 mA | 一致 | p7 | 同上 |
| THD / SNR — DS に無い | — | 一致・補足あり | 規定値は無い。p19 の FAQ "Can the signal to noise ratio be improved?" に後段フィルタで雑音を下げる説明と、雑音密度（下の「無い」の #6）がある | — |

### Q3-10. Skyworks Si8920

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | VDDA・VDDB 3.0〜5.5 V | 一致 | p6 | 同上 |
| 電源電流 | 3.2 / 4.2 / 5.5、2.7 / 3.8 / 4.9 mA | 一致 | p6 | 同上 |
| 入力範囲 | ±100 / ±200 mV | 一致 | p6 | 同上 |
| 差動入力インピーダンス | 20 / 37.2 kΩ | 一致 | p6 | 同上 |
| 非直線性 | 0.04 / 0.15、0.025 / 0.1 % | 一致 | p6 | 同上 |
| 出力雑音 | 0.14 / 0.28、0.10 / 0.20 mVrms、100 kHz BW | 一致 | p6 | 同上 |
| CIO | 1 pF（GW DIP-8 / WB SOIC-16）、パッケージ列 | 一致 | p13 Table 4.6 | 同上 |
| 高圧側電源（図の "Isolated Supply"） | 入力側 VDDA が別に要る | 一致・補足あり | p7 の図は **CMTI の試験回路**（Figure 4.1）。応用例としての根拠は p5 の本文のほうが強い（ゲート駆動の浮動電源から VDDA を作る例） | "The Q1 gate driver has a floating supply, 24 V in this example. …" |
| THD / SNR — DS に無い | — | 一致 | THD の語は無い。SNR は p5 の定性的な一文だけ | — |

### Q3 で「DS に無い」とされた項目

| # | 主張 | 判定 | 確かめた内容 |
|---|---|---|---|
| 1 | 1 kHz 未満（20〜50 Hz）の THD・SNR の規定は無い | 一致 | TI は fIN = 1 kHz / 10 kHz のみ。AD215 は 1 kHz / 10 kHz |
| 2 | ACPL-C87x、HCPL-7800、Si8920、ADuM3190 は THD の規定なし | 一致 | 全文検索で 0 件 |
| 3 | ISO224、AD215、ACPL-C87x、HCPL-7800、Si8920、ADuM3190 は SNR の規定なし | 一致 | HCPL-7800 と Si8920 は定性的な文だけ |
| 4 | AD215 の CIO | 一致 | — |
| 5 | AMC3330 / AMC3336 の DC/DC の周波数の数値、放射の数値 | 一致・補足あり | 数値は無い。同期先の変調器のクロック（AMC3330 は 20 MHz、AMC3336 は CLKIN 9〜21 MHz）は DS にある |
| 6 | 雑音密度: AMC1311 / 1300 / 3330 / 3336 はグラフのみ。**ACPL-C87x、HCPL-7800、Si8920 は密度なし** | **誤り**（HCPL-7800） | HCPL-7800 p19: "The noise spectral density is roughly 500 nV/√Hz below 20 kHz (input referred)."（印字 "nV/s Hz"）。ほかの部分は正しい |

---

## Q4 デジタル・アイソレータ

### Q4-1. TI ISO7741

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 電源 | 2.25〜5.5 V | 一致 | p7 §5.3 | 同上 |
| データレート | 表は MAX 50 Mbps、注 (2) は 100 Mbps | 一致 | p7。画像で確かめた: DR の行の MAX 列が "50"、単位 Mbps。注 (2) は 100 Mbps。p1 Features も "100Mbps data rate"。改訂履歴（Rev. H→I→J→K）にデータレートの変更の記載は無い | "DR Data Rate(2) 50 Mbps" / "(2) 100 Mbps is the maximum specified data rate, although higher data rates are possible." |
| 伝搬遅延 | 3.3 V 6 / 13.5 / 18.5 ns（5 V・2.5 V も） | 一致 | p20（p19、p21） | 同上 |
| PWD | 5.9 ns、MAX（TYP は空欄） | 一致 | p19〜p21 | 同上 |
| tie | 1.4 / 1.3 / 1.5 ns、TYP、2^16−1 PRBS・100 Mbps | 一致 | p19 / p20 / p21 | 同上 |
| スキュー | tsk(o) 4.4、tsk(pp) 5 ns | 一致 | p20 | 同上 |
| CIO | ≅1 pF（DW-16 / DUW-16 / DBQ-16） | 一致 | p9。パッケージ列 | 同上 |
| 電源電流（3.3 V） | 1 / 10 / 100 Mbps の値 | 一致 | p16 §5.12 | 同上 |
| 電源電流（5 V） | 10 / 100 Mbps の値 | 一致 | p14 §5.10 | 同上 |
| アイダイアグラム（本文） | 100 Mbps の典型アイ | 一致 | p33 §8.2.3 | 同上 |

### Q4-2. TI ISO7762

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| データレート | 0〜100 Mbps | 一致 | p7。ISO7741 のような食い違いは無い | "DR(2) Data Rate 0 100 Mbps" |
| 伝搬遅延 | 3.3 V 6 / 12 / 18.5 ns ほか | 一致 | p19〜p21 | 同上 |
| PWD | 0.5 / 5.9 ns ほか | 一致 | p19〜p21 | 同上 |
| tie | 1.3 ns（3 電源とも） | 一致 | p19〜p21 | 同上 |
| CIO | ~1.1（DW-16）/ ~0.9 pF（DBQ-16） | 一致 | p9。改訂履歴 "Changed the CIO value for the DBQ package from 1.1 to 0.9 pF" | 同上 |
| 電源電流（3.3 V） | 1 / 10 / 100 Mbps の値 | 一致 | p16 | 同上 |

### Q4-3. TI ISO1540 / ISO1541

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 動作周波数 | 1 MHz、MAX、注 (1) | 一致 | p6 | 同上 |
| 伝搬遅延（3〜3.6 V） | 33/65、90/181、47/68、67/109 ns | 一致 | p12 | 同上 |
| CIO | ~1 pF | 一致 | p8 | 同上 |
| 電源電流（3〜3.6 V） | ICC1 2.4 / 7.1・2.5 / 4、ICC2 1.7 / 6.7・1.9 / 3.5 mA | 一致 | p11 §6.10（画像で確かめた） | 同上 |

### Q4-4. ADI ADuM1250 / ADuM1251

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 最大周波数 | 1000 kHz、Min | 一致 | p5 Table 2。Min 列 | "MAXIMUM FREQUENCY 1000 kHz" |
| 伝搬遅延（3 V） | 82/125、196/340、32/75、110/210 ns | 一致 | p5 | 同上 |
| 電源電流（3.3 V） | 1.9 / 3.0、1.7 / 3.0 mA | 一致 | p4 Table 1 | 同上 |
| CIO | 1.0 pF | 一致 | p6 | 同上 |

### Q4-5. ADI ADuM1400 / 1401 / 1402

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 最大データレート | ARW 1、BRW 10、CRW 90 / 120 Mbps、注 3 | 一致 | p5。ARW・BRW は Min 列、CRW は Min / Typ | "3 The maximum data rate is the fastest data rate at which the specified pulse width distortion is guaranteed." |
| 伝搬遅延（CRW） | 5 V 18 / 27 / 32、3 V 20 / 34 / 45 ns、**p5, p8** | **誤り**（3 V のページのみ） | 5 V は p5。**3 V は p7**。値は正しい | 同上 |
| PWD（CRW） | 5 V・3 V とも 0.5 / 2 ns、**p5, p8** | **誤り**（3 V のページのみ） | 5 V は p5。**3 V は p7** | 同上 |
| リフレッシュ・レート | 1.2（5 V）/ 1.1 Mbps（3 V） | 一致 | p5 / p8 | 同上 |
| CI-O | 2.2 pF | 一致 | p20 | 同上 |
| 電源電流（5 V） | 10 Mbps 8.6/10.6・2.6/3.5、90 Mbps 70/100・18/25 mA | 一致 | p4 | 同上 |
| 電源電流（3 V） | 10 Mbps 4.5/6.5・1.4/2.0、90 Mbps 37/65・11/15 mA | 一致 | p6 | 同上 |
| ジッタ — DS に無い | — | 一致 | 全文に jitter / time interval error の語が無い | — |

### Q4-6. Skyworks Si864x

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 最大データレート | 0〜150 Mbps、Si864xBx, Ex | 一致 | p19 Table 4.3 | 同上 |
| 伝搬遅延 | 5.0 / 8.0 / 13（3.3 V）、5.0 / 8.0 / 14 ns（2.5 V） | 一致 | p19、p23 | 同上 |
| PWD | 0.2 / 4.5 ns | 一致 | p19 | 同上 |
| ピーク・アイ・ジッタ | 350 ps、Typ | 一致 | p15 / p19 / p23 | 同上 |
| アイ測定の説明（本文） | Si8640、150 Mbps、PWD 2 ns・ジッタ 350 ps | 一致 | p7 §2.2 | 同上 |
| CIO | 2.0 pF（3 パッケージ） | 一致 | p25 | 同上 |
| 電源電流（Si8641Bx, 3.3 V） | 1 / 10 / 100 Mbps の値 | 一致 | p18〜p19 | 同上 |

### Q4-7. Skyworks Si860x

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 最大 I2C バス周波数 | 1.7 MHz | 一致 | p15 | 同上 |
| 伝搬遅延（3.3 V） | 44/55、17/29、30/40、14/27 ns | 一致 | p15 | 同上 |
| 非 I2C チャネル | 0〜10 Mbps、伝搬遅延 max 20 ns | 一致・補足あり | p16 Table 5.4。同じ表に **PWD max 12 ns** と **Peak Eye Diagram Jitter tJIT(PK) TYP 350 ps** があるが tap.md に無い | "Peak Eye Diagram Jitter tJIT(PK) — 350 — ps" |
| CIO | 1.0 / 2.0 / 2.0 pF | 一致 | p19 | 同上 |
| 電源電流（Si8600） | 1.7 MHz: Idda 3.3 / 5.0、Iddb 2.6 / 3.9 mA | 一致 | p13 Table 5.2（3.0 V < VDD < 5.5 V） | 同上 |

### Q4-8. ADI ADuM5401〜5404

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 出力電力 | 最大 500 mW | 一致 | p1 | 同上 |
| VISO 設定値 | 4.7 / 5.0 / 5.4、3.0 / 3.3 / 3.6 V | 一致 | p4、p6 | 同上 |
| IISO(MAX) | 100 / 60 / 100 mA、Min | 一致 | p4、p6、p8。Min 列 | 同上 |
| 効率 | 34 / 33 / 30 % | 一致 | 同上 | 同上 |
| スイッチング周波数 | 180 MHz、Typ | 一致 | p4、p6、p8 | "Switching Frequency fOSC 180 MHz" |
| PWM 周波数 | 625 kHz、Typ | 一致 | 同上 | "PWM Frequency fPWM 625 kHz" |
| 出力リップル／雑音 | 75 / 200 mV p-p | 一致 | p4 | 同上 |
| 入力電流 IDD1 | 19 / 30、290 mA（5 V）、14 / 20、175 mA（3.3 V） | 一致 | p4、p6。全負荷の値は Typ 列だけ | 同上 |
| データレート | A 1、C 25 Mbps、Max、Within PWD limit | 一致 | p4 Table 4 | 同上 |
| 伝搬遅延／PWD（5 V） | A 55/100・40、C 45/60・6 ns | 一致 | p4 | 同上 |
| CI-O | 2.2 pF | 一致 | p10 | 同上 |
| EMI（本文） | 180 MHz で動作、接地筐体を推奨 | 一致 | p22 | 同上 |
| ジッタ — DS に無い | — | 一致 | 全文に jitter の語が無い | — |

### Q4-9. TI ISOW7741

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| データレート | 100 Mbps、MAX | 一致 | p9 | 同上 |
| 出力電力・効率（Features） | 0.55 W、46 % | 一致 | p1 | 同上 |
| 変換器の周波数 | 25 MHz | 一致 | p1、p43 | 同上 |
| 放射（Features） | CISPR 32 / EN 55032 Class B、>5 dB 余裕 | 一致 | p1 | 同上 |
| VISOOUT（5 V→5 V） | 4.5 / 5 / 5.25 V（0〜110 mA）、46 %、24 mV | 一致 | p13 §7.9。同じ表に 0〜55 mA の行（4.75 / 5 / 5.25 V）もある | 同上 |
| VISOOUT（5 V→3.3 V） | 3.135 / 3.3 / 3.465 V（0〜140 mA）、36 %、30 mV | 一致 | p13。0〜70 mA の行もある | 同上 |
| VISOOUT（3.3 V→3.3 V） | 同（0〜60 mA）、43 %、14 mV | 一致 | p13。0〜30 mA の行もある | 同上 |
| 変換器の入力電流 | 225 / 316、143 / 216 mA | 一致 | p14 | 同上 |
| 伝搬遅延／PWD（3.3 V） | 6 / 11 / 16.2、0.6 / 4.7 ns | 一致 | p28 §7.20 | 同上 |
| CIO | ~3.5 pF | 一致 | p11 | 同上 |
| **ジッタ／tie — DS に無い** | — | **誤り** | **tie がある**: 5 V 0.7 ns（p27 §7.19）、**3.3 V 0.65 ns（p28 §7.20、上の伝搬遅延と同じ表の最終行）**、2.5 V 0.7 ns（p29）、1.8 V 0.7 ns（p30）。いずれも TYP、2^16−1 PRBS・100 Mbps | "tie Time interval error 2^16 – 1 PRBS data at 100 Mbps 0.65 ns" |

### Q4-10. TI ISOW1044

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 信号 | CAN 5 Mbps、GPIO 10 Mbps | 一致 | p7 | 同上 |
| 変換器の周波数 | 25 MHz | 一致 | p1 | 同上 |
| 効率 | 47 % | 一致 | p1 | 同上 |
| 放射 | CISPR 32 / EN 55032 Class B | 一致 | p1、p2 | 同上 |
| VISOOUT | 4.75 / 5 / 5.25 V | 一致 | p10 | 同上 |
| 外部に取れる電流 | 20 mA、TYP | 一致 | p10（画像で TYP 列を確かめた） | 同上 |
| 変換器の電源電流 | 76 / 123、26 / 46 mA | 一致 | p13 §6.10 | 同上 |
| CIO | ≅3.5 pF | 一致 | p8 | 同上 |

### Q4 で「DS に無い」とされた項目

| # | 主張 | 判定 | 確かめた内容 |
|---|---|---|---|
| 1 | 周期ジッタ／位相雑音の規定はどの DS にも無い。**あるのは ISO7741 / ISO7762 の tie と Si864x のピーク・アイ・ジッタ 350 ps だけ** | **誤り**（後半） | 周期ジッタ・位相雑音の規定が無いのは正しい。後半から漏れているもの: **ISOW7741 の tie 0.65〜0.7 ns**（p27〜p30）、**Si860x のピーク・アイ・ジッタ 350 ps**（p16）、**ISO7762 p25 Figure 5-17「Peak-to-Peak Output Jitter vs Data Rate」**（典型値のグラフ。0〜100 Mbps、2.5 / 3.3 / 5 V の立上り・立下り。目読みで 10 Mbps 付近 約 0.75〜0.95 ns、100 Mbps で約 1.1〜1.3 ns） |
| 2 | ADuM1400、ADuM5401、**ISOW7741** はジッタ・tie の規定なし | **誤り**（ISOW7741） | ADuM1400・ADuM5401 は正しい |
| 3 | 放射の数値: ISOW7741 / ISOW1044 は CISPR 適合の記載とグラフ（ISOW1044 Figure 9-4 は未読）、ADuM5401 は本文の注意のみ | 一致・補足あり | 数値の規定が無いのは正しい。ISOW1044 の Figure 9-4 は p35 "ISOW1044 Radiated Emissions Versus CISPR32B Line"（放射のグラフ）。DS の中で Figure 9-4 はこれ 1 枚だけ（p11 の VCM の行も "See Figure 9-4 and Table 9-1" とこの番号を参照しているが、内容は合わない。DS 側の参照の誤りとみられる） |
| 4 | ISO7741 のデータレートの食い違い（表 50 Mbps、注 100 Mbps） | 一致 | 上の Q4-1 |

---

## Q5 小型ライン・トランス

### Q5-1. Jensen JT-11P-1

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 帯域（Features） | −3 dB at 0.25 Hz and 95 kHz | 一致 | p1 | 同上 |
| 推奨レベル（Features） | +20 dBu at 20 Hz まで | 一致 | p1 | 同上 |
| 入力インピーダンス | 12.3 / 13.0 / 13.7 kΩ、1 kHz、+4 dBu、試験回路 1 | 一致 | p2（画像） | 同上 |
| 電圧利得 | −2.6 / −2.3 / −2.0 dB | 一致 | p2 | 同上 |
| 振幅特性（1 kHz 基準） | 20 Hz −0.15 / −0.04 / 0.0、20 kHz −0.15 / −0.05 / 0.0 dB | 一致 | p2 | 同上 |
| THD | 1 kHz <0.001 %（TYPICAL）、20 Hz 0.025 % / 0.10 %（TYP / MAX） | 一致 | p2。+4 dBu、試験回路 1、Rs = 600 Ω。p2 下端に "All minimum and maximum specifications are guaranteed." | 同上 |
| 20 Hz 最大入力 | +18 / +20 dBu、1 % THD | 一致 | p2 | 同上 |
| THD+N vs 周波数（左の図） | +4 dBu: 20 Hz 約 0.025 %、約 60 Hz で 0.004 %、**約 130 Hz で 0.001 %**。+14 dBu: 20 Hz 約 0.055 %、50 Hz 約 0.012 %。+20 dBu: 20 Hz 約 1 %、約 30 Hz で 0.1 % | **誤り**（+4 dBu の 130 Hz のみ） | p2。400 dpi で画素を拾い、800 dpi で曲線の識別を確かめた: +4 dBu は 20 Hz 0.023 %、30 Hz 0.012 %、50 Hz 0.0059 %、60 Hz 0.0045 %、**130 Hz 0.0016 %、0.001 % になるのは約 240 Hz**。+14 dBu は 20 Hz 0.052〜0.055 %、50 Hz 約 0.010 %。+20 dBu は 20 Hz 約 1 %、30 Hz 約 0.11 % | "THD at FIXED INPUT LEVELS THD+N (%) vs FREQUENCY (Hz)" |
| THD+N vs 入力レベル（右の図） | 20 Hz 約 0.02〜0.025 %（−25〜+5 dBu）、30 Hz 約 0.012 %、50 Hz 約 0.005 %（〜+10 dBu 付近まで平坦） | 一致・補足あり | p2。20 Hz 0.021〜0.024 %、30 Hz 0.012〜0.014 %。**50 Hz は −15〜+7 dBu で約 0.006 %**（−25 dBu で約 0.004 %）。平坦なのは約 +8〜+10 dBu まで | "THD at FIXED FREQUENCIES THD+N (%) vs INPUT LEVEL(dBu)" |
| CMRR（50 Ω 平衡） | 60 Hz 107、3 kHz 65 / 73 dB | 一致 | p2 | 同上 |
| CMRR（600 Ω 不平衡） | 60 Hz 100、3 kHz 68 dB | 一致 | p2 | 同上 |
| 容量 @1 kHz | 一次–シールド・ケース 98 pF、二次–シールド・ケース 110 pF | 一致 | p2 | 同上 |
| 磁気シールド（本文） | 30 dB | 一致 | p1 | 同上 |

### Q5-2. Lundahl LL1540

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 構造 | 静電シールド、ミューメタル・コアと缶 | 一致 | p1 | 同上 |
| 歪み | +20 dBu <0.1 %、+30 dBu <1 %（@50 Hz、600 Ω） | 一致 | p1 | 同上 |
| 周波数特性 | 5 Hz〜50 kHz ±0.2 dB | 一致 | p1 | 同上 |
| 損失 | 0.5 dB | 一致 | p1 | 同上 |
| 自己共振 | > 60 kHz | 一致 | p1 | 同上 |
| 絶縁 | 4 kV / 2 kV | 一致 | p1 | 同上 |
| CMRR（接続例の注記） | 非対称入力アンプでは 2 × 12 k で >60 dB | 一致 | p1。対称入力アンプの接続例には "recommended for very high CMRR" とあり、数値は無い | 同上 |

### Q5-3. Hammond 560G

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 構造 | 静電シールド（SH ピン）、ハムバッキング | 一致 | p1 | 同上 |
| 周波数範囲 | 0 dbm ±0.5 db、+10 / +27 dbm ±1.0 db typ（30 Hz〜30 kHz） | 一致 | p1 | 同上 |
| 周波数特性（表） | ±1.0 db（30 Hz〜30 kHz）、Typical | 一致 | p1 | 同上 |
| 挿入損失（シリーズ） | 1 db max | 一致 | `Hammond_560_series.pdf` p1 | 同上 |
| 周波数特性グラフ | 0 dbm: 20 Hz で約 −0.9 dB。27 dbm: 約 40 Hz で −2 dB | 一致 | p3。自分の読み: −0.92 dB、約 41 Hz | 同上 |
| THD+N グラフ | 縦軸は線形 −20〜50「THD+N (%)」、0 dbm は 10 Hz で約 7、30 Hz 以上で約 0 | 一致 | p3。10 dbm の曲線は高域で −19 まで下がり、軸の表記ともども数値としては意味をなさない | 同上 |

### Q5-4. Hammond 101 シリーズ

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| 周波数範囲 | 300 Hz〜100 kHz ±0.5 db @100 mw ほか | 一致 | p1 | 同上 |
| THD・シールド・容量 — DS に無い | — | 一致 | 全文検索で 0 件 | — |

### Q5-5. Triad TY-250P / TY-146P

| 項目 | tap.md の値 | 判定 | DS の実際 | 根拠 |
|---|---|---|---|---|
| TY-250P 周波数特性 | ±1 db（20〜20,000 Hz） | 一致 | p1（画像では ± の字。抽出では "+"） | 同上 |
| TY-250P 周波数特性グラフ | 20 Hz 約 −0.4〜−0.55 dB、30 kHz で 600 Ω 約 −0.4、開放 約 +1.25 dB | 一致 | p1。自分の読み: 20 Hz −0.43（600 Ω）〜−0.58 dB、30 kHz −0.39 / +1.28 dB | 同上 |
| TY-250P 挿入損失ほか | <2.8 db ほか | 一致 | p1 | 同上 |
| TY-146P 周波数特性 | ±2 db（200〜15,000 Hz） | 一致 | p1 | 同上 |
| TY-146P THD | <0.5 %（275 Hz〜3.5 kHz） | 一致 | p1 | 同上 |
| TY-146P 縦平衡 | > 45 db | 一致 | p1 | 同上 |

### Q5 で「DS に無い」とされた項目

| 主張 | 判定 | 確かめた内容 |
|---|---|---|
| 一次–二次間の巻線間容量はどの DS にも無い | 一致 | Jensen は巻線–シールド・ケース間だけ。ほかは容量の記載が無い |
| THD の周波数・レベル依存（Lundahl 2 点、Hammond 101・TY-250P は記載なし、TY-146P は帯域のみ） | 一致 | — |
| 20〜50 Hz の THD のグラフは Jensen だけ | **誤り** | Hammond 560G p3 にも THD+N vs 周波数の図（10 Hz〜）がある（軸が壊れていて数値としては使えない） |
| 磁気シールドの減衰量は Jensen（30 dB）だけ | 一致 | — |
| CMRR は Jensen と Lundahl だけ（TY-146P は縦平衡） | 一致 | — |

---

## tap.md に無いが、同じ DS にあって比較に効くもの（参考）

誤りではない（tap.md は拾う範囲を自分で決めている）。H3 の −106 dBc との比較で効くものだけを挙げる。

- **INA1650 の個別高調波（p24 Figure 56 / 57、§8.2.1.3 の本文 p23）:** 1 kHz、22 dBu 出力で **HD2 −111.2 dBu（−133.2 dBc）、HD3 −120.1 dBu（−142.1 dBc）、HD4 −130.7 dBu（−152.7 dBc）**。4 dBu では 2 次が −140 dBu の雑音床からかろうじて見える程度。本文は THD+N vs 振幅が雑音で決まっていると明言している: "The constant downward slope indicates that noise from the device dominates THD+N at this frequency instead of distortion harmonics." 同じ節に、応用回路の CMRR が 1 kHz で 94 dB、10 Ω の不整合で 92 dB という実測（Figure 53）もある。
- **INA1650 Figure 54（p24）:** 22 dBu（9.75 Vrms）で 20 Hz から THD+N 約 −111 dB、4 dBu で約 −101.6 dB（90 kHz 帯域）。
- **AD8274 Figure 34 / 35（PDF p11 / p12）:** 1 kHz の THD+N vs 出力振幅。G = ½ で約 19 dBu まで下がり続け、最小は約 0.0002 %（約 −114 dB）。約 21.5 dBu でクリップ。
- **SSM2143 Figure 4 / 6（p3）:** THD+N vs 振幅（RL = 10 kΩ、80 kHz）と vs 負荷（10 V rms、1 kHz）。10 kΩ 以上で約 0.00045 %。
- **AMC3336 Figure 6-35（p16）:** 1 kHz・2 Vpp のスペクトル（sinc3、OSR = 256）。高調波は目読みで約 −117〜−125 dBV 付近。規定の THD は −93 dB typ / −80 dB max（tap.md のとおり）。
- **INA1620 Figure 52（p21）:** 同じ石の全抵抗の最大–最小マッチングの典型分布（上の Q2-1）。
- **AD215:** 差動入力インピーダンス 16 MΩ、入力オペアンプの CMRR 100 dB（PDF p3）。**ADuM3190:** オペアンプの CMR 72 dB（PDF p4）。**HCPL-7800:** 入力インピーダンス 500 kΩ、クリップ前 308 mV（p7）。
- **ISOW1044:** PWD 3.5 / 10 ns（p15）。**Si860x:** 非 I2C チャネルの PWD max 12 ns（p16）。

### DS の中の食い違い（tap.md の誤りではない）

- **ISO7741:** 推奨動作条件の表の DR が MAX 50 Mbps、同じ表の注 (2)・Features・§8.2.3 が 100 Mbps。tie・電源電流の条件も 100 Mbps。tap.md の書き方どおり。
- **HCPL-7800 p19:** 雑音密度の単位が "nV/s Hz" と誤植（文脈から nV/√Hz）。
- **AMC1300 Figure 7-26:** 雑音密度の軸が "µV/√Hz" だが、値（約 70）と表の出力雑音から見て nV/√Hz のはず。tap.md は原文どおりと明記している。
- **Hammond 560G p3:** THD+N の図の縦軸が線形の −20〜50「%」で、負の値まで描かれている。
