# tap.md 照合結果（verify_tap.md）の再照合

- 日付: 2026-09-25
- 対象: [`../ds_facts/verify_tap.md`](../ds_facts/verify_tap.md) が「誤り」「一致・補足あり」とした行、および「tap.md に無い」として挙げた項目。照合される側は [`../ds_facts/tap.md`](../ds_facts/tap.md)
- やり方: 各項目の DS ページを `pdftoppm -png` で画像にして自分で見た（表は 100〜150 dpi、グラフは 300〜400 dpi の切り出し、JT-11P-1 の低域は 800 dpi）。グラフは枠線と格子線の画素位置で軸を合わせ、指定周波数の列で曲線の画素を拾って換算した（素の Python で PPM を読んだ。PIL は壊れていた）。表の値は `pdftotext -layout` で見当をつけてから画像で列を確かめた。作業ファイルは scratchpad の `tap_errata/`
- 判定の語: **照合が正**（verify_tap.md の指摘が DS と合う）／**tap.md が正**（指摘は当たらない。tap.md のままでよい）／**どちらも不正確**（どちらの数値も DS と合わない）
- 「目読み」の値は規定値ではない。対数軸での読み取り誤差は tap.md の凡例どおり ±20〜30 % 程度はある。その範囲内のずれは「合う」と扱った

## 集計

| 区分 | 件数 | 照合が正 | tap.md が正 | どちらも不正確 |
|---|---|---|---|---|
| 誤り | 13 | 13 | 0 | 0 |
| 一致・補足あり | 23 | 23 | 0 | 0 |
| tap.md に無い（照合が挙げたもの） | 17 | 15 | 1 | 1 |

- 誤り #9（JT-11P-1）は、指摘の本体（+4 dBu の 130 Hz）は照合が正。ただし照合が同じ行で書いた **「+20 dBu は 30 Hz で約 0.11 %」は誤り**（30 Hz では約 0.06 %、0.1 % を切るのは約 27 Hz）。tap.md の「約 30 Hz で 0.1 %」はおおむね合っている。この部分は照合の読みを採らなかった
- 一致・補足ありのうち 3 件（INA1650 Fig 12、SSM2141 CMR、AD8274 Fig 15）は、補足の方向は正しいが一部の数値を私の読みで置き換えた（下の表）
- 「tap.md に無い」の「どちらも不正確」1 件は **AMC3336 Figure 6-35**。照合は「高調波は約 −117〜−125 dBV」としたが、**3 次（3 kHz）は約 −109 dBV、2 次（2 kHz）は約 −115 dBV** まで出ている。tap.md には元々この図の行が無い
- 「tap.md が正」1 件は ISO7741 の 50 / 100 Mbps。tap.md は食い違いを原文どおり書いており、照合のクロック換算（24.576 MHz → 49.152 Mbps）は設計の読みなので tap.md には入れない

---

## 1. 誤り（13 件）

| # | 部品・項目 | 照合の主張 | 私が DS で見たもの | 判定 | tap.md への反映 |
|---|---|---|---|---|---|
| 1 | ISOW7741 ジッタ／tie（Q4-9） | 「DS に無い」は誤り。tie は p27〜p30 に TYP 0.7 / 0.65 / 0.7 / 0.7 ns | p28 §7.20 を画像で確認: 最終行 "tie Time interval error 2^16 – 1 PRBS data at 100 Mbps"、TYP 列に 0.65 ns。p27（5 V）0.7、p29（2.5 V）0.7、p30（1.8 V）0.7 ns を抽出で確認 | 照合が正 | 行を tie の値に差し替え |
| 2 | Q4「無かった項目」: 規定があるのは ISO7741 / ISO7762 の tie と Si864x の 350 ps だけ | Si860x の 350 ps と ISO7762 Fig 5-17 が漏れ | Si860x p16 Table 5.4（非 I2C チャネル）に "Peak Eye Diagram Jitter tJIT(PK) — 350 — ps"（Typ 列）。ISO7762 p25 Figure 5-17 "Peak-to-Peak Output Jitter vs Data Rate"（TA = 25°C、2.5 / 3.3 / 5 V の立上り・立下り 6 本）。私の読み: 10 Mbps で約 0.76〜0.94 ns、50 Mbps で約 0.93〜1.09 ns、100 Mbps で約 1.09〜1.29 ns（立上りが低く、立下りが高い） | 照合が正 | 箇条を訂正。ISO7762 と Si860x に行を追加 |
| 3 | Q4「無かった項目」: ADuM1400・ADuM5401・ISOW7741 はジッタ・tie なし | ISOW7741 だけ誤り | ADuM1400・ADuM5401 は全文に jitter / interval error が 0 件。ISOW7741 は #1 | 照合が正 | 箇条を訂正 |
| 4 | HCPL-7800 雑音密度（Q3「無かった項目」） | p19 の FAQ に入力換算 約 500 nV/√Hz | p19 を画像で確認: "The noise spectral density is roughly 500 nV/s Hz below 20 kHz (input referred)."（印字は "nV/s Hz"） | 照合が正 | 箇条を訂正、行を追加 |
| 5 | INA1620 Figure 14 | −128 dB ではなく G = −1 約 −126、G = +1 約 −132.5 dB | p9 を 400 dpi で読んだ: 破線（G = −1、3 負荷）約 −126 dB、実線（G = +1、3 負荷）約 −132.5 dB、負荷差はほぼ無い。実線は約 1 kHz から上がり 2 kHz で約 −131 dB、20 kHz で約 −118 dB | 照合が正 | 行を訂正 |
| 6 | INA1650 Figure 9（100 kHz） | GND 約 73、VMID 約 74 dB。78 dB は約 60 kHz | 400 dpi で画素を拾った: 100 kHz で GND 約 73.5、VMID 約 74.5 dB。GND が 78 dB になるのは約 63 kHz。低域 GND 91.0 / VMID 86.0、10 kHz で 89.0 / 85.3 dB | 照合が正 | 行を訂正（10 kHz も 89 dB に） |
| 7 | INA137 高調波（1 kHz の 2 次） | 約 0.00007 % | p4 を 400 dpi で読んだ: 2 次は 20 Hz 約 0.00018 %、約 800 Hz から平坦で約 0.00007 %。3 次（"Noise Limited" の破線）約 0.00004 % | 照合が正 | 行を訂正 |
| 8 | SSM2141 THD（600 Ω・20 kHz） | 約 0.018 %。0.01 % は約 10 kHz | p3 の AP 画面を 400 dpi で読んだ: 600 Ω は 10 kHz で約 0.009 %、20 kHz で約 0.017 %。低域は両負荷とも約 0.0008 %、100 kΩ の 20 kHz は約 0.002 % | 照合が正 | 行を訂正 |
| 9 | JT-11P-1 左の図（+4 dBu の 130 Hz） | 130 Hz で約 0.0016 %、0.001 % は約 240 Hz | 400 dpi で画素、800 dpi で曲線の識別を確認: +4 dBu は 20 Hz 約 0.023 %、60 Hz 約 0.0045 %、130 Hz 約 0.0016 %、0.001 %（図の下端）に届くのは約 245 Hz。+14 dBu は 20 Hz 約 0.052 %、50 Hz 約 0.010 %。**+20 dBu は 20 Hz 約 1 %、0.1 % を切るのは約 27 Hz、30 Hz では約 0.06 %**（照合の「30 Hz 約 0.11 %」は誤り） | 照合が正（+20 dBu の 30 Hz だけ照合を採らない） | 行を訂正 |
| 10 | Q5「無かった項目」: 20〜50 Hz の THD のグラフは Jensen だけ | Hammond 560G p3 にもある | `Hammond_560.pdf` p3 に "560G Rs-150 Rl=150 THD+N"（10 Hz〜100 kHz、0 / 10 / 27 dbm）。縦軸は線形 −20〜50「THD+N (%)」で負の値まで描かれている | 照合が正 | 箇条を訂正 |
| 11 | SSM2143 5 Ω 不整合で 71 dB のページ | p6 ではなく p7 | PDF p7（下端 "–7–"、"APPLICATIONS INFORMATION"）に "a CMRR of 71 dB at dc"。挿入ページは無い | 照合が正 | 出典を p7 に |
| 12 | ADuM1400 3 V CRW 伝搬遅延のページ | p8 ではなく p7 | p7（"Table 2. (Continued)"、下端 "Rev. M \| 7 of 33"）の CRW 欄に 20 / 34 / 45 ns | 照合が正 | 出典を p5, p7 に |
| 13 | ADuM1400 3 V CRW PWD のページ | p8 ではなく p7 | 同じ p7 に 0.5 / 2 ns。p8 にあるのは Refresh Rate 1.1 Mbps | 照合が正 | 出典を p5, p7 に |

## 2. 一致・補足あり（23 件）

| # | 部品・項目 | 照合の補足 | 私が DS で見たもの | 判定 | tap.md への反映 |
|---|---|---|---|---|---|
| 1 | INA134 版 | p1 下に "PDS-1390A … July, 1997" | p1 に "©1997 Burr-Brown Corporation PDS-1390A Printed in U.S.A. July, 1997" | 照合が正 | 反映せず（版の表は「改訂日の印字なし」で誤りではない） |
| 2 | INA137 版 | "PDS-1391B … July, 1997" | 同様に PDS-1391B | 照合が正 | 反映せず |
| 3 | ACPL-C87x 版 | 表紙に "September 16, 2024" | 表紙に AV02-3563EN と September 16, 2024 | 照合が正 | 反映せず |
| 4 | HCPL-7800 版 | 表紙に "November 19, 2020" | 表紙に AV02-0410EN と November 19, 2020 | 照合が正 | 反映せず |
| 5 | INA1620 冒頭の注意（差動アンプの CMRR 規定なし） | p21 Figure 52 に同じ石の全抵抗の最大–最小マッチングの典型分布 | p21 §8.1.2 に Figure 52 "Matching Histogram, Maximum to Minimum"。私の読み: 山は約 0.15〜0.25 %、大半は約 0.35 % 以下、裾は約 1.5 % まで（0.05 % 刻みの棒） | 照合が正（山の位置は照合の「0.15〜0.3 %」より少し狭く読んだ） | 行を追加、「無かった項目」を訂正 |
| 6 | INA1650 Figure 12 | 600 Ω は 20 Hz 約 −106.4、10 kHz 約 −105.5 dB | 2 kΩ は約 −108 dB で平坦。600 Ω は 20 Hz 約 −106.3 dB、中域 約 −108 dB、10 kHz 約 −106.5 dB、20 kHz 約 −101 dB | 照合が正（10 kHz は私の読みで約 −106.5 dB） | 行を訂正 |
| 7 | INA1650 Figure 14 | 最小は約 9.8 Vrms の約 −115 dB、そこから約 −112 dB へ跳ね、約 12 Vrms でクリップ | 1 Vrms で −100 dB。最小は約 9.7 Vrms で約 −115 dB、直後に約 −111〜−112 dB、約 11.5 Vrms で急増 | 照合が正 | 行を訂正 |
| 8 | INA134 CMR vs 周波数 | 20 kHz は約 84.7 dB | 画素で拾った: 平坦部 90.6、10 kHz 89.8、20 kHz 84.6、100 kHz 70.4 dB | 照合が正 | 行を訂正 |
| 9 | INA137 CMR vs 周波数 | 90.9 dB は約 60 kHz まで、95 kHz で 87.7 dB | 平坦部 91.0 dB、折れ始めは約 57 kHz、100 kHz 約 87.5 dB、1 MHz 約 64.3 dB | 照合が正 | 行を訂正 |
| 10 | SSM2141 CMR vs 周波数 | 平坦は約 200 Hz まで、1 kHz 約 96、100 kHz 約 58 dB | 平坦（100 dB）は約 200 Hz まで、1 kHz 約 96 dB、20 kHz 約 72 dB、100 kHz 約 57 dB（スキャン画像で線が太い） | 照合が正（100 kHz は約 57 dB と読んだ。tap.md の 55 dB も誤差の端） | 行を訂正 |
| 11 | AD8274 Figure 15 | G = ½ は約 25 kHz まで平坦、100 kHz では両方約 82 dB | G = ½ 約 94.3 dB で約 20〜25 kHz まで平坦、G = 2 約 100 dB で約 12 kHz まで。100 kHz は両方約 83 dB | 照合が正（100 kHz は約 83 dB） | 行を訂正 |
| 12 | Q2「無い」: INA1620 の差動アンプ CMRR | 値は無い。ペア外のマッチングは Fig 52 | 全文に差動アンプ構成の CMRR 値は無い。Fig 52 は #5 | 照合が正 | 箇条を訂正 |
| 13 | Q2「無い」: 20〜50 Hz のグラフの列挙 | SSM2141 の THD vs 周波数と INA1650 Fig 54 が漏れ | SSM2141 p3 の AP 画面は 20 Hz から（振幅の記載なし）。INA1650 p24 Fig 54 は 20 Hz から 4 dBu / 22 dBu | 照合が正 | 箇条を訂正 |
| 14 | AMC3330 DC/DC の周波数 | 数値は無い。同期先の変調器 20 MHz は p25 本文 | p22 に数値なし。p25 §7.2.2.1 に "the sampling frequency (20 MHz) of the internal ΔΣ modulator" | 照合が正 | 行を訂正 |
| 15 | AMC3336 DC/DC の周波数 | 数値は無い。変調器クロックは CLKIN 9〜21 MHz | p23 に数値なし。CLKIN 9 / 20 / 21 MHz は p4 | 照合が正 | 行を訂正 |
| 16 | AD215 同相入力インピーダンス | 同じ枠に差動 16 MΩ、1 行上に CMRR of Input Op Amp 100 dB | PDF p3 を画像で確認: INPUT IMPEDANCE Differential G = 1 V/V **16 MΩ**（Typ）、INPUT VOLTAGE RATINGS に **CMRR of Input Op Amp 100 dB**（Typ、条件なし） | 照合が正 | 行を 2 つ追加 |
| 17 | AD215 絶縁側電源 | 電流 ±10 mA は Typ 列だけ。注 9 で ±15 V 以上なら ±15 mA | PDF p4 を画像で確認: Voltage は Min / Typ / Max、Current at Rated Supply Voltage は Typ 列に ±10 mA のみ。注 9 の原文も確認 | 照合が正 | 行を訂正 |
| 18 | HCPL-7800 THD / SNR | 規定値は無い。p19 FAQ に SNR 改善の説明と雑音密度 | 同左 | 照合が正 | 行を訂正 |
| 19 | Si8920 高圧側電源 | p7 の図は CMTI の試験回路。応用例の根拠は p5 本文 | p7 Figure 4.1 "Common-Mode Transient Immunity Characterization Circuit" の "Isolated Supply"。p5 に浮動電源から VDDA を作る本文 | 照合が正 | 行を訂正 |
| 20 | Q3「無い」#5 AMC3330 / AMC3336 | 同期先のクロックは DS にある | #14・#15 と同じ | 照合が正 | 箇条を訂正 |
| 21 | Si860x 非 I2C チャネル | 同じ表に PWD max 12 ns と Peak Eye Diagram Jitter 350 ps | p16 Table 5.4 を画像で確認: PWD Max 12 ns、tJIT(PK) Typ 350 ps | 照合が正 | 行を 2 つ追加 |
| 22 | Q4「無い」#3 ISOW1044 Figure 9-4 | p35 の放射のグラフ。p11 の VCM も同じ番号を参照 | p35 "Figure 9-4. ISOW1044 Radiated Emissions Versus CISPR32B Line"。p11 の VCM 行ほか数行が "See Figure 9-4 and Table 9-1" | 照合が正 | 箇条を訂正 |
| 23 | JT-11P-1 右の図 | 50 Hz は −15〜+7 dBu で約 0.006 %、−25 dBu で約 0.004 % | 20 Hz 0.021〜0.024 %、30 Hz 0.012〜0.014 %、50 Hz は −15〜約 +8 dBu で約 0.006 %、−25 dBu で約 0.0043 %。上がり始めは 20 Hz で約 +5、30 Hz で約 +7、50 Hz で約 +10 dBu | 照合が正 | 行を訂正 |

## 3. 照合が「tap.md に無い」として挙げたもの

| # | 部品・項目 | 照合の記述 | 私が DS で見たもの | 判定 | tap.md への反映 |
|---|---|---|---|---|---|
| 1 | INA1650 個別高調波（p24 Fig 56 / 57、p23 本文） | 22 dBu で HD2 −133.2、HD3 −142.1、HD4 −152.7 dBc。4 dBu は 2 次がかろうじて見える | Fig 57 の図中に "HD2: -111.2 dBu (-133.2 dBc)" "HD3: -120.1 dBu (-142.1 dBc)" "HD4: -130.7 dBu (-152.7 dBc)"。基本波は図から約 1 kHz（図に周波数の印字なし）。本文 p23 も同じ値と「4 dBu では 2 次が −140 dBu の雑音床からかろうじて見える」 | 照合が正 | 行を追加 |
| 2 | INA1650 本文「THD+N は雑音が決めている」 | p23 の引用 | p23 §8.2.1.3 に原文あり（Figure 55 は 22-kHz 帯域） | 照合が正 | 行を追加 |
| 3 | INA1650 応用回路の CMRR（Fig 53） | 1 kHz で 94 dB、10 Ω 不整合で 92 dB | p23 本文にそのとおり | 照合が正 | 行を追加 |
| 4 | INA1650 Figure 54 | 22 dBu は 20 Hz で約 −111 dB、4 dBu 約 −101.6 dB | 22 dBu は 20 Hz 約 −111.7 dB、中域 約 −115 dB、約 7 kHz から上昇。4 dBu 約 −101.6 dB で平坦 | 照合が正 | 行を追加 |
| 5 | AD8274 Figure 34（G = ½、1 kHz、THD+N vs 出力振幅） | 約 19 dBu まで下がり、最小約 0.0002 %（約 −114 dB）、約 21.5 dBu でクリップ | 0 dBu で約 0.0006 %、最小は約 19〜20 dBu で約 0.00018 %（約 −115 dB）、600 Ω は約 21.5 dBu、"RL = 2kΩ, 100Ω"（原文の印字）は約 22 dBu で急増 | 照合が正 | 行を追加（Figure 35 は読んでいないので載せない） |
| 6 | AD8274 Figure 36 の H3 | 約 0.00023 %（約 −113 dBc） | 3 次（全負荷）約 0.00023 %、2 次 600 Ω 約 0.000044 %、2 次 100 kΩ/2 kΩ 約 0.000016 %、約 10 kHz から上昇 | 照合が正。tap.md の「約 0.00025 %」も目読み誤差の範囲で合う | 反映せず |
| 7 | SSM2143 Figure 4 / 6 | THD+N vs 振幅と vs 負荷。10 kΩ 以上で約 0.00045 % | Fig 4（RL = 10 kΩ、80 kHz、横軸 dBu、周波数の記載なし）: 0 dBu 約 0.0019 %、約 28 dBu で約 0.0005 %、約 29 dBu で急増、途中にレンジ切替の段差。Fig 6（10 V rms、1 kHz、80 kHz）: 10 kΩ 以上 約 0.00045 %、1 kΩ 約 0.0011 %、約 300 Ω 未満で急増 | 照合が正 | 行を 2 つ追加 |
| 8 | AMC3336 Figure 6-35（1 kHz・2 Vpp のスペクトル） | 高調波は約 −117〜−125 dBV | 400 dpi で画素を拾った: 基本波 約 −3 dBV、**2 次 約 −115 dBV、3 次 約 −109 dBV**、4 次 約 −120.5、5 次 約 −119.5、6 次 約 −125 dBV、約 17 kHz に約 −124 dBV の線、雑音床 約 −130〜−135 dBV | **どちらも不正確**（照合は 2 次・3 次を低く読んでいる。tap.md には行が無い） | 私の読みで行を追加 |
| 9 | INA1620 Figure 52 | 典型分布 | 一致・補足あり #5 と同じ | 照合が正 | 行を追加 |
| 10 | AD215 差動 16 MΩ・入力オペアンプ CMRR 100 dB | PDF p3 | 一致・補足あり #16 と同じ | 照合が正 | 行を追加 |
| 11 | ADuM3190 オペアンプの Common-Mode Rejection 72 dB | PDF p4 | PDF p4（印刷 p3）Table 1 の OP AMP 欄に Common-Mode Rejection 72 dB（Typ、条件なし） | 照合が正 | 行を追加 |
| 12 | HCPL-7800 Equivalent Input Impedance 500 kΩ・クリップ前 308 mV | p7 | p7 を画像で確認: RIN 500 kΩ（Typ）、\|VIN+\|MAX 308.0 mV（Typ、Figure 10） | 照合が正 | 行を追加 |
| 13 | ISOW1044 GPIO の PWD 3.5 / 10 ns | p15 | p15 の GPIO Channel に PWD 3.5（TYP）/ 10（MAX）ns | 照合が正 | 行を追加 |
| 14 | Si860x 非 I2C の PWD max 12 ns | p16 | 一致・補足あり #21 と同じ | 照合が正 | 行を追加 |
| 15 | ISO7741 の 50 Mbps（表）と 100 Mbps（注・Features・§8.2.3） | クロックを通すなら 49.152 Mbps で余裕 2 % 弱 | p7 §5.3 を画像で確認: DR の MAX 列 50 Mbps、注 (2) "100 Mbps is the maximum specified data rate, although higher data rates are possible."。改訂履歴（H→I→J→K）にデータレートの記載は無い | **tap.md が正**（食い違いは tap.md に原文どおり書いてある。クロック換算と余裕は設計の読みなので tap.md に入れない） | 反映せず |
| 16 | AMC1311B の IDD1（3.0〜3.6 V） | 6.0 / 8.4 mA が tap.md に無い | p11 に "3.0 V < VDD1 < 3.6 V, SHTDN = low, AMC1311B only 6.0 8.4 mA" | 照合が正 | 行を訂正 |
| 17 | HCPL-7800 雑音密度の単位の誤植 | "nV/s Hz" | 誤り #4 と同じページで確認 | 照合が正 | 追加行の引用に原文の印字のまま残した |

照合の「DS の中の食い違い」のうち AMC1300 Figure 7-26 の軸単位は、tap.md が既に原文どおりと明記しているので再照合の対象から外した。

## 4. tap.md に加えた変更の一覧

訂正（行の最後の欄に〔2026-09-25 照合で訂正〕）:
INA1620 Fig 14／INA1650 Fig 12・Fig 14・Fig 9／INA134 CMR vs 周波数／INA137 CMR vs 周波数・高調波／SSM2141 CMR vs 周波数・THD+N vs 周波数／SSM2143 5 Ω 不整合のページ／AD8274 Fig 15／AMC1311 IDD1／AMC3330・AMC3336 DC/DC の方式／AD215 絶縁側電源／HCPL-7800 THD・SNR／Si8920 高圧側電源／ADuM1400 CRW 伝搬遅延・PWD のページ／ISOW7741 ジッタ／tie／JT-11P-1 左右の図、および「探したが DS に無かった項目」の Q2・Q3・Q4・Q5 の該当箇条（箇条の末尾に同じ印）

表の形だけの修正（印なし。内容は変えていない）: 引用の中の `|` がエスケープされておらず列数が崩れていた既存の 4 行（INA1620 入力インピーダンス、AMC3330 動作同相入力、ISO7741 PWD、ISO7762 PWD）の `|` を `\|` にした。

追加（〔2026-09-25 照合で追加〕）:
INA1620 Fig 52／INA1650 Fig 53（本文）・Fig 54・Fig 56/57・本文の雑音の記述／SSM2143 Fig 4・Fig 6／AD8274 Fig 34／AMC3336 Fig 6-35／AD215 差動入力インピーダンス・入力オペアンプ CMRR／ADuM3190 オペアンプ CMR／HCPL-7800 入力インピーダンス・クリップ前入力・雑音密度／ISO7762 Fig 5-17／Si860x 非 I2C の PWD・ピーク・アイ・ジッタ／ISOW1044 GPIO の PWD
