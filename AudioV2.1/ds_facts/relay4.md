# 4 極ラッチ信号リレー／小電流 DC 電源用 2 極ラッチ — データシートの事実

2026-09-25 収集。値は DS（とメーカーの注意事項ページ）の原文で裏が取れたものだけ。設計判断は書かない（どれが使えるか・足りるかは書かない）。

- 出典のページは **PDF のページ番号**。印刷ページ番号と違う DS は、その部品の見出しに対応を書いた。
- 「列」はその値が表のどの列に印刷されているか。表に min/typ/max の列が無いものは「値の列のみ」と書き、値に付いた `Max.` `Approx.` `typ.` などの字句はそのまま残した。
- 「画像で確認」は、ページを画像にして（poppler の `pdftoppm -r 150`。AES 暗号化 PDF は PyMuPDF で 150 dpi）表の罫線と列見出しを目で確かめたもの。「抽出のみ」は `pdftotext` / PyMuPDF のテキスト抽出だけで、画像では見ていないもの。
- 「目読み」はグラフの値。300 dpi の画像で格子線から目で読んだ（画素較正はしていない）。精度は目盛り 1/5 程度で、数値保証ではない。
- 「計算」は DS の数値どうしの四則演算。**DS 自身には書かれていない**ことを示すために付けた。
- 「DS に無い」は、本文・表・注・グラフを探して見つからなかったもの。
- 部品が「在る」「ラッチ版が在る」と書くのは、その DS の型番表に載っているときだけ。

---

## 取得した DS（`AudioV2.1/datasheets/relay4/`）

| ファイル | 版（DS の表記） | 取得元 | 備考 |
|---|---|---|---|
| `Panasonic_DS_EU_110509J.pdf` | フッタ "ds_61005_0001_en_ds: 110509J"（7 p。PDF メタデータ ModDate 2011-02-04） | https://mediap.industry.panasonic.eu/assets/download-files/import/ds_ds_en_discon2009.pdf | **DS1E/DS2E/DS4E の DS で 4 Form C を含む最新の手元版**。全ページ上部に赤字の廃止告知（§1.0）。印刷ページ = PDF ページ |
| `Panasonic_DS_MEW2007.pdf` | 版表記なし。"All Rights Reserved © COPYRIGHT Matsushita Electric Works, Ltd."、PDF 作成 2007-06-08（pdftk、Jameco の表紙付き 7 p） | https://datasheet.octopart.com/DS4E-S-DC5V-Panasonic-datasheet-10039363.pdf | PDF p1 は Jameco の表紙。本文は PDF p2〜p7（印刷ページ番号なし）。**1 コイルラッチのコイル表と「接点組間」耐電圧はこちらにだけある** |
| `Panasonic_DS_2019.pdf` | ASCTB17E 201903（9 p、メタデータ "Issued Date: July 5, 2019"） | Panasonic NA の DS2 廃止告知 zip に同梱（下行） | **1 Form C / 2 Form C のみ**（§1.0 の根拠） |
| `Panasonic_DS2_PDN_2021.pdf` | "PDN.PG0001.3.15.2021"（1 p） | https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/244683 （zip。na.industrial.panasonic.com の DS2E-SL2-DC5V 型番ページに添付） | DS2 シリーズの廃止告知 |
| （既存）`../datasheets/arch/Panasonic_DS.pdf` | メタデータ "Issued Date: July 01,2026"（12 p） | https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_ds.pdf | 2026-09-25 に同 URL から取り直したものとバイト一致。NA の型番ページの "Panasonic DS Series Relays Datasheet"（fileversion/263704）ともバイト一致 |
| `Fujitsu_RA4.pdf` | "Rev. January 23, 2008."（8 p）。全ページに透かし "DISCONTINUED (2009)" | https://www.fcl-components.com/downloads/MICRO/fcai/relays/ra4.pdf | 印刷ページ = PDF ページ。透かしで一部の文字が欠ける（下の表で注記） |
| `Fujitsu_Relay_Engineering_Reference.pdf` | 版表記なし（31 p、PDF 作成 2009-04-22、印刷ページ 505〜） | https://www.fcl-components.com/storage/en/support/relays/engineering-ref.pdf | Fujitsu のリレー共通技術資料 |
| `Panasonic_S.pdf` | ASCTB207E 202607（13 p、"Issued Date: July 01,2026"） | https://industry.panasonic.com/ac/cdn/e/control/relay/power/catalog/mech_eng_s.pdf | AES 暗号化。PyMuPDF で抽出・描画。**PDF ページ = 印刷ページ + 1** |
| `Panasonic_SP.pdf` | ASCTB208E 202607（15 p、"Issued Date: July 01,2026"） | https://industry.panasonic.com/ac/cdn/e/control/relay/power/catalog/mech_eng_sp.pdf | 同上。**PDF ページ = 印刷ページ + 1** |
| `Panasonic_NF_2000.pdf` | 版表記なし（2 p、PDF 作成 2000-09-04） | https://datasheet.octopart.com/NF4EB-24V-Panasonic-datasheet-9651265.pdf | 4 Form C だが**ラッチ型は型番表に無い**（§6） |
| `TE_4-1617631-1_product_summary.pdf` | TE の製品ページ印刷（3 p、"03/27/2025"） | https://docs.rs-online.com/3377/A700000013652897.pdf | **DS ではない**（§6） |

取得したが置かなかったもの: Omron "Electrical Mechanical Relay Selection Guide"（Y225-E1-02、https://omronfs.omron.com/en_US/ecb/products/pdf/Y225-E1-02.pdf、16.5 MB）。§6 で引く。

メーカーの共通注意事項（PDF でなく Web ページ。2026-09-25 閲覧）: Panasonic "Relays Cautions for Use" https://industry.panasonic.com/global/en/products/control/relay/cautions_use （S・SP・TQ の DS が "GUIDELINES FOR RELAY USAGE" としてこの URL を指している）。§5 で引く。

---

## 1. Panasonic DS4E（4 Form C、DS リレー）

### 1.0 型番の存在と供給状況

| 項目 | 事実 | 出典 | 原文の引用 |
|---|---|---|---|
| 4 Form C のラッチ型が型番表にあるか | **ある**。2011 年版は単安定と **2 コイルラッチ**（DS4E-ML2-DC5V / DS4E-SL2-DC5V など）。2007 年版は単安定・**1 コイルラッチ**（DS4E-ML-DC5V / DS4E-SL-DC5V）・2 コイルラッチ | EU 110509J p2（画像で確認）、MEW2007 PDF p3 | "2 coil latching type ... DS4E-ML2-DC5V"、"1 coil latching ... DS4E-ML-DC5V ... DS4E-SL-DC5V" |
| 1 コイルラッチの受注生産 | 1 コイルラッチ型は受注ロット生産 | EU 110509J p1, p2 | "Note: 1 coil latching type are manufactured by lot upon receipt of order." |
| **廃止告知（2011 年版）** | 4 Form C の全型番に ⚠ 印。見出しに「⚠ 印の製品は … をもって廃止」。**日付は非埋め込みフォントのため文字化けしていて読めない**（月日は 1 字ずらしで "December 31" と読めるが年の 2 桁は □□ 表示）。ファイル名は `ds_ds_en_discon2009.pdf` | EU 110509J p1–p4（画像で確認） | "Products marked ⚠ are discontinued as of 'HFHPEHU31, 20□□"、"⚠ Products to be discontinued." |
| 2019 年版カタログ | **1 Form C / 2 Form C のみ**。4 Form C は載っていない | `Panasonic_DS_2019.pdf` p1 | "1 Form C / 2 Form C, 2 A,"、"Contact arrangement 1: 1 Form C 2: 2 Form C" |
| 2026 年版カタログ | **1 Form C のみ** | `arch/Panasonic_DS.pdf` p2 | "High sensitivity 200 mW Rated operating power, 1 Form C, 2 A relays" |
| Panasonic NA のシリーズページ | 型番一覧は DS1E-M / -ML2 / -S / -SL2 各 16、DS2E-S / -SL2 各 7。**DS4E は 0 件** | https://na.industrial.panasonic.com/products/relays-contactors/mechanical-signal-relays/series/119573 （2026-09-25 取得、HTML 内の型番を数えた） | — |
| 参考: DS2 の廃止 | DS2 シリーズ廃止。Effective 2021-03-26、Last Time Buy 2021-09-28、Last Eligible Ship 2021-12-31。直接の代替なし（TX を検討せよ）。DS1 は対象外で継続 | `Panasonic_DS2_PDN_2021.pdf` p1（画像で確認） | "The DS2 Series Relays are being discontinued due to low market demand." / "DS1 Series Relays are not included in this Product Notice and remain active." |

### 1.1 仕様（以下は 2011 年版 EU 110509J を主、2007 年版で補った）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| 接点構成 | 4 Form C | — | 値の列のみ | EU p4（画像で確認） | "Arrangement 1 Form C 2 Form C ⚠ 4 Form C" |
| 接点材質 | Ag+Au clad（2007 年版は "Gold-clad silver"） | — | 同上 | EU p4 / MEW2007 PDF p2（画像で確認） | "Contact material Ag+Au clad" |
| 初期接触抵抗 | Max. 50 mΩ | 電圧降下法 6 V DC 1 A | Max. | EU p4 | "Max. 50 mΩ (By voltage drop 6 V DC 1A)" |
| 微小電流での接触抵抗 | **DS に無い** | — | — | — | — |
| 最小開閉容量（参考値） | 10 µA 10 mV DC。注 *1: 低レベル負荷（10 V DC、10 mA 以下）には SX リレーがある | — | 値の列のみ | EU p4 | "Min. switching capacity (Reference value)*1 10μA 10m V DC" / "(SX relays are available for low level load switching [10V DC, 10mA max. level])" |
| 定格開閉容量 | 2 A 30 V DC（抵抗負荷） | — | 同上 | EU p4 | "Nominal switching capacity (resistive load) 2 A 30 V DC" |
| 最大開閉電力 / 電圧 | 60 W, 125 VA / 220 V DC, 250 V AC | 抵抗負荷 | 同上 | EU p4 | "60 W, 125 VA" / "220 V DC, 250 V AC" |
| 最大開閉電流 | 2 A DC, AC | 抵抗負荷 | 同上 | MEW2007 PDF p2 | "Max. switching current 2 A DC, AC" |
| 最大通電電流 | 3 A | — | 同上 | EU p4 / MEW2007 PDF p2 | "Max. carrying current 3 A" |
| 耐電圧（開接点間） | 1,000 Vrms 1 min | 検出電流 10 mA | 同上 | EU p4 | "Between open contacts 1,000 Vrms for 1min." |
| 耐電圧（接点–コイル間） | 1,500 Vrms 1 min | 同上 | 同上 | EU p4 | "Between contact and coil 1,500 Vrms for 1min." |
| **耐電圧（接点組間）** | **1,000 Vrms**（2007 年版のみ。2011 年版の表にはこの行が無い） | 検出電流 10 mA | "(Other types)" の列 | MEW2007 PDF p2（画像で確認） | "Between contacts sets — 1,000 Vrms" |
| 絶縁抵抗 | Min. 100 MΩ（500 V DC） | — | Min. | EU p4 | "Min. 100MΩ (at 500V DC)" |
| **静電容量（開接点間・接点組間・コイル–接点）** | **DS に無い**（2011・2007 とも） | — | — | — | — |
| 動作（セット）時間 | Max. 10 ms [セット Max. 10 ms] | 定格電圧、20 °C、バウンス除く | Max. | EU p4 | "Operate time [Set time] (at 20°C) Max. 10 ms [10 ms] (Nominal voltage applied to the coil, excluding contact bounce time.)" |
| 復帰（リセット）時間 | Max. 5 ms [リセット Max. 10 ms] | 定格電圧、20 °C、バウンス除く、ダイオードなし | Max. | EU p4 | "Release time [Reset time] (at 20°C) Max. 5 ms [10 ms] ... (without diode)" |
| バウンス時間 | **DS に無い**（時間は "excluding contact bounce time"） | — | — | — | — |
| 衝撃（機能） | 4 Form C: Min. 294 m/s²（1C・2C は 490 m/s²） | 半波正弦 11 ms、検出 10 µs | Min.（4 Form C の列） | EU p4（画像で確認） | "Min. 294 m/s²" |
| 衝撃（破壊） | Min. 980 m/s² | 半波正弦 6 ms | Min. | EU p4 | "Min. 980 m/s² (Half-wave pulse of sine wave: 6 ms.)" |
| 寿命 | 機械 Min. 10⁸（1 Form C ラッチは 10⁷）、電気 Min. 5×10⁵（定格負荷、60 cpm） | — | Min. | EU p4 | "Min. 10⁸ (10⁷: 1 Form C latching type) (at 600 cpm)" / "Min. 5×10⁵ rated load (at 60 cpm)" |
| 重量 | 4 Form C 約 7 g | — | 4 Form C の列 | EU p4 | "Approx. 7g" |
| 外形 | 図中の寸法数字: 長さ 35.24、幅 9.9、高さ方向に 9.9 / 9.3、端子長 3.4（mm）。2011 年版本文は「1c・2c・4c とも高さ 9.8 mm、幅 9.9 mm」 | — | 寸法図 | MEW2007 PDF p6（画像で確認）/ EU p1 | "1c, 2c, and 4c all have the same height (9.8 mm .386 inch). The width of the relay is also the same (9.9 mm .390 inch)." |
| ピン数 | 単安定・1 コイルラッチ **14 本**、2 コイルラッチ **16 本**（穴 φ0.9、2.54 mm 格子、列間 7.62 mm） | — | 基板パターン図 | MEW2007 PDF p6（画像で確認） | "14-0.9 dia" / "16-0.9 dia" |
| IC ソケット | 4C は 14 ピン IC ソケット 2 個で使える | — | — | MEW2007 PDF p2 | "4C type can be used with 2 sets of 14 pin IC sockets" |

### 1.2 コイル（ラッチ型、5 V。20 °C）

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| **2 コイルラッチ M 型 5 V**（DS4E-ML2-DC5V） | セット・リセット各 **72 mA、69.4 Ω、360 mW** | 20 °C、電流・抵抗 ±10 % | 表値（Set coil / Reset coil の列） | EU p3（画像で確認） | "5V DC ... 72mA 72mA 69.4Ω 69.4Ω"、"360mW 360mW" |
| **2 コイルラッチ S 型 5 V**（DS4E-SL2-DC5V） | セット・リセット各 **36 mA、139 Ω、180 mW** | 同上 | 同上 | EU p3（画像で確認） | "5V DC ... 36mA 36mA 139Ω 139Ω"、"180mW 180mW" |
| 2 コイルラッチ: セット / リセット電圧 | 2 Form C・4 Form C: 定格の 70 %V 以下（初期）。M・S とも | 20 °C | 値の列のみ | EU p3 | "2 Form C, 4 Form C: 70%V or less of nominal voltage (Initial)" |
| 2 コイルラッチ: 最大許容電圧 | M 型 150 %V、S 型 200 %V（2・4 Form C） | **50 °C** | 同上 | EU p3 | "Max. allowable voltage (at 50°C) ... 2 Form C, 4 Form C: 150%V" / "200%V" |
| **1 コイルラッチ M 型 5 V**（DS4E-ML-DC5V） | 139 Ω ±10 %、Reset/Set 3.5 V DC max、最大許容 7.5 V DC（50 °C） | 20 °C | 表値（"2, 4 Form C" の列） | MEW2007 PDF p4（画像で確認） | "5 3.5 3.5 139 6 7.5" |
| 1 コイルラッチ M 型 5 V: 電流・電力 | **DS に無い**（電力は仕様表の "Nominal set and reset power Approx. 180 mW"）。計算: 5 / 139 ≈ 36 mA、5² / 139 ≈ 180 mW | — | 計算 | MEW2007 PDF p2 | "1 coil latching Nominal set and reset power Approx. 180 mW" |
| **1 コイルラッチ S 型 5 V**（DS4E-SL-DC5V） | 278 Ω ±10 %、Reset/Set 3.5 V DC max（2・4 Form C）、最大許容 10 V DC | 同上 | 同上 | MEW2007 PDF p4（画像で確認） | "5 4.0 3.5 278 8.0 10" |
| 1 コイルラッチ S 型 5 V: 電流・電力 | **DS に無い**（仕様表 "Approx. 90 mW"）。計算: ≈ 18 mA、≈ 90 mW | — | 計算 | MEW2007 PDF p2 | "Nominal set and reset power Approx. 90 mW" |
| 2 コイルラッチの端子 | 16 ピン品で 2・15 に通電で「リセット」、1・16 に通電で転換 | — | 回路図注記 | MEW2007 PDF p6（画像で確認） | "Diagram shows the “reset” position when terminals 2 and 15 are energized. Energize terminals 1 and 16 to transfer contacts." |
| 1 コイルラッチの端子 | 1・16 に通電でリセット、逆極性で転換 | — | 同上 | MEW2007 PDF p6 | "Diagram shows the “reset” position when terminals 1 and 16 are energized. Energize with reverse polarity to transfer contacts." |
| 最小セット/リセットパルス幅 | **DS に無い**（Panasonic 共通注意事項の目安は §5.1） | — | — | — | — |
| 連続通電 | ラッチ型の連続通電の可否は **DS に無い**。参考データに **DS4E-ML2-DC12V** のコイル温度上昇グラフ（印加 100〜110 %V、接点電流 0 / 2 / 3 A、セット・リセットコイル別）がある | — | グラフ | EU p5 | "4-(4). Coil temperature rise (4 Form C 2 coil latching type) Tested sample: DS4E-ML2-DC12V" |
| 2 コイルの同時通電 | **DS に無い**（Panasonic 共通注意事項は §5.1） | — | — | — | — |
| 出荷時の状態 | **DS に無い**（回路図注記は「図はリセット位置」だけ。共通注意事項は §5.1） | — | — | — | — |
| 隣接実装の影響 | 4 Form C の感動・開放電圧の変化率を隣接距離 10・20 mm で示すグラフがある（ラッチ型の図ではない） | — | グラフ | EU p5 / MEW2007 PDF p7 | "6-(3). Influence of adjacent mounting (4 Form C)" |

---

## 2. Fujitsu（Takamisawa）RA4（4 Form C、RA4 / RA4L / RA4L-D）

**⚠ 全ページに "DISCONTINUED (2009)" の透かし**（画像で確認）。p1 の特徴欄は「Latching type available」。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ラッチ型が型番表にあるか | **ある**: 単巻線ラッチ RA4L-( ) W-K、2 巻線ラッチ RA4L-D ( ) W-K | — | — | p1, p3（画像で確認） | "(b) Operation Function Nil : Standard type L : Latching type" / "(c) Number of Coil Nil : Single winding type D : Double winding type" |
| 金接点品 | 可動・固定とも金被覆品は末尾 "-OH" | — | — | p1 | "For movable and stationary contact with gold overlay type, add suffix ““-OH””." |
| 接点構成 | 4 form C (4PDT)、二股（クロスバー） | — | 値の列のみ | p4（画像で確認） | "Arrangement 4 form C (4PDT)" / "Style Bifurcated (cross bar)" |
| 接点材質 | Gold overlay silver palladium | — | 同上 | p4 | "Material Gold overlay silver palladium" |
| 初期接触抵抗 | Maximum 100 mΩ | 1 A 6 VDC | Maximum | p4 | "Resistance (initial) Maximum 100 mΩ (at 1 A 6 VDC)" |
| 定格（抵抗） | 0.5 A 120 VAC または 1 A 24 VDC | — | 値の列のみ | p4 | "Rating (resistive) 0.5 A 120 VAC or 1 A 24 VDC" |
| 最大通電 / 開閉電流 | 2 A / 2 A | — | 同上（透かしで項目名の一部が欠ける。値は読める） | p4（画像で確認） | "Maximum Carrying Current 2A" / "Maximum Switching Current 2A" |
| 最大開閉電力 / 電圧 | 60 VA, 24 W / 250 VAC, 220 VDC | — | 同上 | p4 | "60 VA, 24 W" / "250 VAC, 220 VDC" |
| 最小開閉負荷（参考値） | 0.01 mA 10 mVDC | *1 参考値 | 同上 | p4 | "Minimum Switching Load*1 0.01 mA 10 mVDC" |
| **静電容量（10 MHz）** | 開接点間 約 1.4 pF、**隣接接点間 約 1.3 pF**、コイル–接点間 約 2.4 pF | 10 MHz | "Approximately" | p4（画像で確認） | "Approximately 1.4 pF (between open contacts), 1.3 pF (adjacent contacts) Approximately 2.4 pF (between coil and contacts)" |
| 耐電圧 | 開接点間 1,500 VAC 1 min、コイル–接点間／隣接接点間 1,500 VAC 1 min | — | 3 型共通の結合セル | p4（画像で確認） | "open contacts 1,500VAC 1 min." / "coil and contacts/ adjacent contact 1,500VAC 1 min." |
| 絶縁抵抗 | Minimum 1,000 MΩ（500 VDC） | — | Minimum | p4 | "Minimum 1,000 MΩ (at 500VDC)" |
| アイソレーション（目読み） | 共通–メーク接点間（開接点）: 約 2〜3 MHz で 約 74〜76 dB、50 MHz で 約 52〜55 dB（2 本の曲線）。**音声帯域の値は DS に無い**（横軸は 0〜50 MHz の線形） | 試料 RA4-12W-K、n = 5、伝送インピーダンス 75 Ω | グラフ | p6（300 dpi で目読み） | "High Frequency Characteristics (Isolation)"、"between common and make contacts" |
| **単巻線ラッチ 5 V**（RA4L-5 W-K） | 278 Ω ±10 %、セット +3.5 VDC、リセット −3.5 VDC、定格電力 90 mW | 20 °C。注 *1: セット/リセット電圧はパルス波電圧での規定 | 表値 | p3（画像で確認） | "RA4L- 5 W-K 5 VDC 278Ω +3.5 VDC –3.5 VDC 90 mW" / "Note: *1 Specified values are subject to pulse wave voltage." |
| 単巻線ラッチ 5 V: 電流 | **DS に無い**。計算: 5 / 278 ≈ 18 mA | — | 計算 | — | — |
| **2 巻線ラッチ 5 V**（RA4L-D 5 W-K） | 一次（P）139 Ω でセット +3.5 VDC、二次（S）139 Ω でリセット +3.5 VDC、定格電力 180 mW（表は 1 型番 1 セル） | 20 °C | 表値 | p3（画像で確認） | "RA4L-D 5 W-K 5 VDC P 139Ω +3.5 VDC 180 mW / S 139Ω +3.5 VDC" / "P: Primary coil S: Secondary coil" |
| 2 巻線ラッチ 5 V: 電流 | **DS に無い**。計算（139 Ω を 1 コイルとして）: ≈ 36 mA、≈ 180 mW | — | 計算 | — | — |
| 動作電力 | 単巻線ラッチ 45 mW、2 巻線ラッチ 90 mW | 20 °C | 型別の列 | p4 | "Operate Power (at 20°C) ... 45 mW 90 mW" |
| 時間 | ラッチ型: セット Maximum 6 ms、リセット Maximum 6 ms（標準型は動作 6 ms・復帰 4 ms） | 定格電圧 | Maximum | p4（画像で確認。透かしで標準型の値の一部が欠ける） | "Maximum 6 ms (set)" / "Maximum 6 ms (reset)" |
| バウンス時間 | **DS に無い** | — | — | — | — |
| 最小パルス幅 | **DS に無い**（共通技術資料は「通常 10 ms 程度で十分」。§5.2） | — | — | — | — |
| 2 コイル同時通電・出荷時状態 | **DS に無い**（同時通電は共通技術資料 §5.2） | — | — | — | — |
| 寿命 | 機械 2×10⁷ 回 min、電気 2×10⁵（0.5 A 120 VAC）/ 5×10⁵（1 A 24 VDC） | — | minimum | p4 | "2 × 10⁷ operations minimum" |
| 外形 | 35.24 (+0.2) × 10.0 × 9.9 (+0.1) mm | — | 寸法図 | p6（画像で確認） | "35.24 +0.2"、"10.0 +0"、"9.9 +0.1" |
| ピン数 | RA4 / RA4L **14 本**、RA4L-D **16 本**（φ0.8） | — | 基板穴図 | p6（画像で確認） | "14-φ0"（透かしで欠け）/ "16-φ0.8" |
| 重量 | 約 6.4 g | — | — | p4 | "Approximately 6.4 g" |

---

## 3. Panasonic S リレー（4 Form A ほか、パワーリレー区分）

**⚠ カタログの区分は "Power Relays ( Over 2 A )"。4 極は 4 Form A（4 PST-NO）で、4 Form C の型は無い**（型番表は 2a2b / 3a1b / 4a）。ページ対応: PDF p4 = 「ー3ー」。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ラッチ型が型番表にあるか | 4 Form A の **2 コイルラッチ S4EB-L2-5V** がある。1 コイルラッチ（L）は型番構成にあるが受注ロット生産で、TYPES 表とコイル表には無い | — | — | PDF p3 | "S4EB-L2-5V AG324960" / "* 1 coil latching type are manufactured by lot upon receipt of order." |
| 状態 | 2026 年 7 月版カタログに掲載。廃止の記載なし | — | — | PDF p1–p3 | "ASCTB207E 202607" |
| 保護構造 | 密閉型 | — | — | PDF p2 | "Protective construction：Sealed type" |
| 熱起電力 | 約 3 µV | — | "Approx." | PDF p2 | "Low thermal electromotive force: Approx. 3 µV" |
| 接点材質 | AgNi-AgSnO₂ 系、2 層接点に Au クラッド | — | 値の列のみ | PDF p4（画像で確認） | "AgNi-AgSnO2 type, Au clad on double-layer contact" |
| 初期接触抵抗 | Max. 50 mΩ | 電圧降下法 6 V DC 1 A | Max. | PDF p4 | "Max. 50 mΩ ( by voltage drop 6 V DC 1 A )" |
| **最小開閉負荷（参考値）** | **100 µA 100 mV DC** | *1 | 値の列のみ | PDF p4（画像で確認） | "Min. switching load ( reference value ) *1 100 µA 100 mV DC" |
| 接点定格（抵抗） | 4 A 250 V AC、3 A 30 V DC | — | 同上 | PDF p4 | "4 A 250 V AC, 3 A 30 V DC" |
| 最大開閉電力 / 電圧 / 電流 | 1,000 VA, 90 W / 250 V AC, 48 V DC / 4 A (AC), 3 A (DC)（30〜48 V DC は 0.5 A 未満） | 抵抗負荷 | 同上 | PDF p4 | "4 A ( AC ) , 3 A ( DC ) ( 30 to 48 V DC at less than 0.5 A )" |
| 最大通電電流 | **DS に無い**（本体の表に項目なし。ソケット S-PS の定格は 4 A） | — | — | PDF p8 | "Maximum carrying current 4 A"（PC board socket の表） |
| 耐電圧 | 開接点間 750 V rms、**接点組間 1,000 V rms**、接点–コイル間 1,500 V rms（各 1 min、検出 10 mA） | 初期 | 値の列のみ | PDF p4（画像で確認） | "Between contact sets 1,000 V rms for 1 min ( detection current: 10 mA )" |
| 絶縁抵抗 | 10,000 MΩ（500 V DC） | 初期 | 同上 | PDF p4 | "10,000 MΩ ( at 500 V DC ...)" |
| 静電容量 | **DS に無い** | — | — | — | — |
| **2 コイルラッチ 5 V** | セット・リセット各 **38.5 mA、130 Ω、192 mW**。セット/リセット電圧 Max. 70 %V（初期）、最大許容 180 %V（40 °C） | 20 °C、±10 %。注 "* Square, pulse drive" | 表値（Set coil / Reset coil の列） | PDF p4（画像で確認） | "5 V DC ... 38.5 mA 38.5 mA 130 Ω 130 Ω 192 mW 192 mW" |
| 使用電圧 | 定格コイル電圧の ±5 % 以内 | — | — | PDF p4 | "please use the relay within ±5 % of rated coil voltage." |
| 時間 | 動作（セット）Max. 15 ms（Max. 15 ms）、復帰（リセット）Max. 10 ms（Max. 15 ms） | 定格電圧、20 °C、バウンス除く、復帰はダイオードなし | Max. | PDF p4（画像で確認） | "Max. 15 ms ( Max. 15 ms )" / "Max. 10 ms ( Max. 15 ms )" |
| バウンス時間 | **DS に無い** | — | — | — | — |
| セット/リセットのパルス幅 | 本 DS の共通注意は「製品ごとに異なるので個別仕様を見よ」とするが、**個別の値はこの DS に無い**（Panasonic 共通注意事項の目安は §5.1） | — | — | PDF p10 | "the set/reset pulse time of latching type relay differs for each relays, please refer to the relay's individual specifications." |
| 2 コイル同時通電 | セットとリセットに同時に電圧を加えないこと | — | — | PDF p10 | "Avoid impressing voltages to the set coil and reset coil at the same time." |
| 連続通電 | 連続通電の条件ではラッチ型を推奨（ラッチ型の連続通電の可否は無い） | — | — | PDF p7 | "If using under conditions in which the relay will be continually powered, we recommend the latching type." |
| 端子間の負荷接続の制限 | 絶縁距離の規定により、端子 2,3 と 4,5 の間、8,9 と 10,11 の間で**異なるチャンネル**の負荷を接続してはいけない（同じチャンネルなら可） | — | 図 | PDF p7（画像で確認は未。抽出のみ） | "Based on regulations regarding insulation distance, there is a restriction on same-channel load connections between terminals No. 2, 3 and 4, 5, as well as between No. 8, 9 and 10, 11." / "different channels, therefore not possible" |
| 出荷時の状態 | **DS に無い**（共通注意事項 §5.1） | — | — | — | — |
| 外形・ピン | 28 ± 0.5 × 12 ± 0.5 × 10 ± 0.5 mm、**12 ピン**（φ1.3、2.54 mm 格子、列間 7.62 mm） | — | 寸法図 | PDF p6（画像で確認） | "28±0.5"、"12±0.5"、"10±0.5"、"12-φ1.3" |
| 2 コイルラッチのコイル端子 | 図ではコイルが 1–12 と 6–7 | — | 回路図 | PDF p6（画像で確認） | 図 "2 coil latching ( Reset )" |
| 隣接実装 | 他の S リレーの近くに置くとき、外部磁界の影響がないようにするには 10 mm 以上離すこと | — | — | PDF p5（抽出のみ） | "be sure to leave at least 10mm between relays in order to achieve the performance listed in the catalog." |
| 重量 | 約 8 g | — | — | PDF p4 | "Approx. 8 g" |

---

## 4. Panasonic SP リレー（4 Form C、パワーリレー区分）

**⚠ 区分は "Power Relays ( Over 2 A )"、4 Form C 10 A。** ページ対応: PDF p3 = 「ー2ー」、PDF p4 = 「ー3ー」。

| 項目 | 値 | 条件 | 列 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| ラッチ型が型番表にあるか | 4 Form C の **2 コイルラッチ SP4-L2-DC5V** がある（プラグイン端子）。PC 板端子型と 1 コイルラッチ型は受注ロット生産 | — | — | PDF p3（画像で確認）、PDF p2 | "SP4-L2-DC5V AR1249" / "Notes：PC board type and 1 coil latching type are manufactured by lot upon receipt of order." |
| 状態 | 2026 年 7 月版カタログに掲載。廃止の記載なし | — | — | — | "ASCTB208E 202607" |
| 保護構造 | ダストカバー型 | — | — | PDF p2 | "Protective construction：Dust cover type" |
| 接点材質 | 固定接点 Au フラッシュ AgSnO₂ 系、可動接点 AgSnO₂ 系 | — | 値の列のみ | PDF p4（画像で確認） | "Stationary contact: Au flashed AgSnO2 type, Movable contact: AgSnO2 type" |
| 初期接触抵抗 | Max. 30 mΩ | 6 V DC 1 A | Max. | PDF p4 | "Max. 30 mΩ ( by voltage drop 6 V DC 1 A )" |
| **最小開閉負荷（参考値）** | **100 mA 5 V DC** | *1 | 値の列のみ | PDF p4（画像で確認） | "Min. switching load ( reference value ) *1 100 mA 5 V DC" |
| 接点定格（4 Form C） | 10 A 250 V AC、10 A 30 V DC | 抵抗負荷 | 4 Form C の列 | PDF p4 | "10 A 250 V AC, 10 A 30 V DC" |
| 耐電圧 | 開接点間 1,500 V rms、**接点組間 3,000 V rms**、接点–コイル間 3,000 V rms | 1 min、検出 10 mA | 値の列のみ | PDF p4（画像で確認） | "Between contact sets 3,000 V rms for 1 min" |
| 静電容量 | **DS に無い** | — | — | — | — |
| **2 コイルラッチ 5 V** | セット・リセット各 **60.2 mA、83 Ω、300 mW**。セット/リセット Max. 70 %V、最大許容 150 %V（20 °C） | 20 °C、±10 %。"* square, pulse drive" | 表値 | PDF p3（画像で確認） | "5 V DC 60.2 mA 60.2 mA 83 Ω 83 Ω"、"300 mW 300 mW" |
| 時間 | 動作（セット）Max. 50 ms（Max. 50 ms）、復帰（リセット）Max. 20 ms（Max. 50 ms） | 定格電圧、20 °C、バウンス除く | Max. | PDF p4（画像で確認） | "Max. 50 ms ( Max. 50 ms )" / "Max. 20 ms ( Max. 50 ms )" |
| 2 コイル同時通電 | 同時に加えないこと | — | — | PDF p12 | "Avoid impressing voltages to the set coil and reset coil at the same time." |
| パルス幅 | **DS に無い**（「個別仕様を見よ」の共通文のみ） | — | — | PDF p12 | — |
| 外形・ピン | 4 Form C: 50 × 36.8 × 20.5 mm。PC 板端子の穴 16-φ2.5 | — | 寸法図 | PDF p2, p6（抽出のみ） | "5050 ... 36.836.8 ... 20.520.5"、"16ｰφ2.5" |
| 重量 | 4 Form C 約 65 g | — | 4 Form C の列 | PDF p4 | "Approx. 65 g" |

---

## 5. メーカー共通の注意事項（ラッチの駆動・容量負荷）

### 5.1 Panasonic "Relays Cautions for Use"（Web ページ、2026-09-25 閲覧）

URL は冒頭。**個別の DS ではない**。DS・TQ・S・SP それぞれの DS がこのページを参照している（TQ PDF p17、S PDF p10、SP PDF p12 の "For cautions for use, please read ..."）。

| 項目 | 内容 | 原文の引用 |
|---|---|---|
| 出荷時の状態 | ラッチリレーはリセット状態で出荷。輸送・取付時の衝撃でセットに変わりうる。電源投入時に初期化する回路を推奨 | "Latching relays are shipped from the factory in the reset state. A shock to the relay during shipping or installation may cause it to change to the set state. Therefore, it is recommended that the relay be used in a circuit which initializes the relay to the required state (set or reset) whenever the power is turned on." |
| 2 コイル同時通電 | 同時に加えないこと | "Avoid impressing voltages to the set coil and reset coil at the same time." |
| **コイルの並列接続** | セットコイル同士・リセットコイル同士を並列にするときは各コイルに直列ダイオード。あるリレーのセットと別のリレーのリセットを並列にするときも同じ。誘導負荷と並列のときも同じ。ダイオードは平均整流電流がコイル電流以上 | "If set coils or reset coils are to be connected together in parallel, connect a diode in series to each coil. Fig. 17 (a), (b)" / "Use a diode having an ample margin of safety for repeated DC reverse voltage and peak reverse voltage applications and having an average rectified current greater than or equal to the coil current." |
| **最小パルス幅** | 目安として**各製品のセット／リセット時間の 5 倍以上**、定格電圧の矩形波。取れないときは問い合わせ。コンデンサ駆動も問い合わせ | "As a guide, make the minimum pulse width in order to set or reset a latching relay at least 5 times the set time or reset time of each product and apply a rectangular-wave rated voltage. ... Also, please inquire regarding capacitor drive." |
| 同上を各 DS の値に当てた計算 | 計算（DS の Max. 値 × 5）: DS4E 10 ms → 50 ms、S 15 ms → 75 ms、SP 50 ms → 250 ms、TQ（PC 板）3 ms → 15 ms。**TQ の DS 自身は「10 ms 以上を推奨」**（`boundary.md` §3.3、TQ PDF p17）で、この目安と一致しない | 計算 |
| 4 端子ラッチ結線 | セットとリセットの片端を共通にして同極性で駆動する回路では表の 2 端子を短絡せよ（DS 1〜2 Form C は 15 & 16、SP は 2 & 4）。**DSP・TQ・S は極性の都合で不適用**。表に DS 4 Form C の行は無い | "Relay Type Terminal Nos. DS 1 Form C - 2 Form C 15 & 16 ST * SP 2 & 4" / "DSP, TQ, S relays are not applicable due to polarity." |
| 2 コイルの誘導電圧 | 片方のコイルの通電・遮断で反対側コイルに定格電圧程度の誘導電圧。トランジスタ駆動の逆バイアスに注意 | "Although the amount of induction voltage is about the same as the rated relay voltage, you must be careful of the reverse bias voltage when driving transistors." |
| 容量負荷の突入電流 | 容量負荷の突入電流は定常電流の 20〜40 倍（負荷種別の表） | "Capacitive load 20 to 40 times the steady state current" |
| DC 容量負荷と溶着 | DC の誘導・容量負荷で電流が大きいとき、突入電流が大きいとき（数 A〜数十 A）に接点転移で溶着のように固着する。DC 容量負荷（数 A〜数十 A）は実機確認が必須 | "For DC capacitive loads (several amperes to several tens of amperes), it is always necessary to conduct actual confirmation tests." |
| **大負荷と微小負荷を 1 個で開閉** | 1 個のリレーで大負荷と低レベル負荷の両方を開閉するのは望ましくない（大負荷の開閉で飛散した接点材が低レベル負荷の接点に付き接触不良）。低レベル負荷の接点を大負荷の接点の下にしない | "Furthermore, it is not desirable to switch both a large load and a low level load with a single relay. The scattered contact material produced when switching the large load adheres to the contacts when switching the low level load and may cause contact failure." |
| 多極リレーで異電圧 | 多極リレーの極間に異なる電圧がかかる回路、特に 2 つの異なる電源回路を開閉するときは、沿面・空間距離・隔壁を構造から確かめ余裕を取ること | "care must be taken when selecting the type of relay in circuits where different voltages are applied between electrodes in a multi-pole relay, especially when switching two different power supply circuits." |
| ドライ回路 | 低電流回路（ドライ回路）では接点電圧が低く導通不良になりやすい。負荷に並列のダミー抵抗で電流を上げる方法がある | "Since voltage levels at the contacts used in low current circuits (dry circuits) are low, poor conduction is often the result. One method to increase reliability is to add a dummy resistor in parallel with the load" |

### 5.2 Fujitsu Engineering Reference（`Fujitsu_Relay_Engineering_Reference.pdf`）

| 項目 | 内容 | 出典 | 原文の引用 |
|---|---|---|---|
| パルス幅の目安 | 有極ラッチは通常 10 ms 程度のパルス幅で十分（RA を含む） | PDF p5（印刷 p513 付近） | "Usually, a pulse width of around 10 ms is sufficient to set or reset a polarized type relay." / "A, FBR46 and RA type relays have variations of the polarized latching type relay." |
| 2 コイル同時通電 | 避けること | PDF p27（印刷 p535） | "Avoid simultaneous application of voltage to set and reset coils. (In case of 2-coils latching relay.)" |
| コイルの並列接続 | 複数のセット／リセットコイルを接続するときは各コイルに直列ダイオード（コイル間の逆起電力による誤動作を避ける） | PDF p27 | "For connection of more than one set coils or reset coils, use diode(s), arranging in series with magnet coil in a manner as shown in Fig. 2.22, to avoid malfunctions caused by back electromotive forces among coils." |
| パルスの幅と電圧 | 各カタログを参照 | PDF p27 | "As to the widths and voltages of drive pulses for operate and release of latching relays, refer to appropriate catalogs." |

---

## 6. 調べたが対象にならなかったもの・取れなかったもの

| メーカー／系列 | 結果 | 根拠 |
|---|---|---|
| Panasonic TX / TX-S / TX-D | **2 Form C のみ**（4 極なし） | mech_eng_tx.pdf（ASCTB18E 202408）、mech_eng_txs.pdf（ASCTB15E 202607）、mech_eng_txd.pdf（ASCTB19E 202501）、いずれも https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/ 。抽出テキストに現れる接点構成は "2 Form C" だけ（リポジトリには置いていない） |
| Panasonic TQ | 2 Form C / 2 Form D のみ | `boundary.md` §3.3 |
| Panasonic NF（NF4EB） | 4 Form C だが**ラッチ型は型番表に無い**（Form C / 2MBB / 4MBB のみ）。参考: 静電容量 接点–接点 約 4 pF、接点–コイル 約 7 pF、接点–アース 約 6 pF、コンタクトバウンス 約 1.5 ms | `Panasonic_NF_2000.pdf` p1 "MBB function Nil: Form C type 2M: 2MBB (2 Form D) 4M: 4MBB (4 Form D)"、"Contact/Contact Approx. 4 pF"、"Contact bounce Approx. 1.5 ms"（抽出のみ） |
| Omron | 信号リレー（2 A 未満）の選定表は接点構成 **1c・2c のみ**（G5V-1, G5V-2, G6E, G6A, G6S, G6J-Y, G6K, G6K-RF 等）。4 極の信号リレーは見つからなかった | Omron Y225-E1-02 PDF p2 "Contact form 1c ... 2c"（PyMuPDF 抽出のみ） |
| TE（CII 3SBM など） | TE の製品ページ印刷に「4 Form C 4PDT-CO、Polarized, Bistable, Latching、2 A、26.5 VDC、975 Ω、.72 W、Hermetically Sealed、−65〜125 °C、Coil Suppression Diode、EU RoHS Not Compliant、ACTIVE」。**DS 本体（"5-1773450-5_sec1_3SBM"）は te.com が 403 で取れず**、5 V コイル品の有無・パルス幅・静電容量は未確認 | `TE_4-1617631-1_product_summary.pdf` p1–p3 |
| TE Axicom（IM, P2） | 4 極品は見つからなかった（DS 未取得） | — |
| Hongfa | 4 極ラッチ信号リレーは見つからなかった（hongfa.com の一覧は JavaScript 描画で読めず。DS 未取得） | — |
| Teledyne | 見つけたのは 2 極（420/422 系 TO-5）の記述だけ。製品カタログ PDF は teledynedefenseelectronics.com が HTML を返して取れず | — |
| Coto / Zettler | 4 極ラッチ信号リレーは見つからなかった（DS 未取得） | — |
| Fujitsu のほかの 4 極 | 見つからなかった | — |

---

## 7. 小さな DC 電源の開閉という役割から見た 2 極ラッチ（既存 DS の再読）

コイル・時間・出荷状態は [boundary.md §3](boundary.md) にある。ここでは**接点電流・通電電流・容量負荷／突入の記載**だけを足した。

| 部品 | 接点定格・最大開閉 | 最大通電電流 | 容量負荷・突入電流の記載 | 出典 | 原文の引用 |
|---|---|---|---|---|---|
| Zettler AZ850（P1 / P2） | 開閉電力 30 W / 62.5 VA、開閉電流 1 A、開閉電圧 220 VDC* / 250 VAC（*30 VDC 超は要相談）。UL 定格 1 A 30 VDC 抵抗 | **2 A**（"carry current"） | **DS に無い** | `../datasheets/Zettler_AZ850.pdf` p1（抽出のみ） | "switched current 1A carry current 2A" / "* Note: If switching voltage is greater than 30 VDC, special precautions must be taken." |
| Omron G6KU（単巻線ラッチ） | 定格負荷 0.3 A 125 VAC、1 A 30 VDC。最大開閉電圧 125 VAC / 60 VDC、最大開閉電流 1 A。UL: 2 A 30 VDC at 40 °C（6,000 回） | **2 A**（"Rated carry current"） | **DS に無い**。p4 に "Ambient Temperature vs. Carry Current" のグラフあり（値は読んでいない） | `../datasheets/boundary/Omron_G6K.pdf` p3, p9（抽出のみ） | "Rated carry current 2A" / "Max. switching current 1A" / "2 A, 30 VDC at 40°C" |
| Panasonic TQ（PC 板端子） | 1 A 30 V DC、0.5 A 125 V AC、30 W / 62.5 VA、110 V DC / 125 V AC、最大 1 A | **DS に無い** | **DS に無い**（共通注意事項 §5.1 に容量負荷 20〜40 倍の表） | `../datasheets/boundary/Panasonic_TQ.pdf` PDF p6（画像で確認） | "Contact rating (resistive) 1 A 30 V DC, 0.5 A 125 V AC" / "Max. switching current 1 A ( DC ), 1 A ( AC )" |
| Panasonic TQ（表面実装） | 2 A 30 V DC、0.5 A 125 V AC、60 W、220 V DC、最大 2 A。接点材質 AgNi + Au clad | **DS に無い** | **DS に無い** | 同 PDF p8（抽出のみ） | "2 A 30 V DC, 0.5 A 125 V AC" |

---

## どの DS にも無かった項目

- **4 Form C の現行（廃止告知の無い）ラッチ型信号リレー**: 見つからなかった。4 極でラッチ型が型番表にあったのは **DS4E（2011 年版で廃止告知、2019・2026 年版に無し、NA サイトの型番一覧に無し）**、**RA4L / RA4L-D（"DISCONTINUED (2009)"）**、**S（4 Form A、パワーリレー区分、最小開閉負荷 100 µA 100 mV）**、**SP（4 Form C、パワーリレー区分、最小開閉負荷 100 mA 5 V、65 g）**。TE CII は DS 本体が取れていない。
- **DS4E の廃止日付**: 2011 年版の見出しが文字化けしていて年が読めない。
- **4 極品の静電容量（接点組間＝チャンネル間）**: RA4 の「隣接接点間 約 1.3 pF（10 MHz）」だけ。DS4E・S・SP には無い（NF は非ラッチで 約 4 pF）。
- **音声帯域での接点組間アイソレーション／クロストーク**: どの DS にも無い（RA4 のアイソレーション図は 2〜50 MHz の開接点間だけ）。
- **微小電流（mV・µA 級）での接触抵抗**: どれも 6 V 1 A（DS・S・SP）か 1 A 6 VDC（RA4）の測定だけ。
- **ラッチ型のバウンス時間**: どれにも無い（DS・S・SP は時間を "without bounce" で除外。NF の 約 1.5 ms は非ラッチ）。
- **最小セット/リセットパルス幅の表値**: DS4E・RA4・S・SP のどの DS にも無い。あるのはメーカー共通資料の目安（Panasonic「セット/リセット時間の 5 倍以上」、Fujitsu「通常 10 ms 程度で十分」）だけ。
- **ラッチ型の連続通電の可否**: どれも明示なし（DS4E-ML2 のコイル温度上昇グラフ、S・SP の最大許容電圧の列があるだけ）。
- **出荷時の状態**: 個別 DS には無い。Panasonic 共通注意事項に「リセットで出荷、衝撃で変わりうる、電源投入時に初期化を推奨」。
- **2 コイル同時通電の禁止**: S・SP の DS と、Panasonic・Fujitsu の共通資料にある。DS4E・RA4 の DS そのものには無い。
- **多数のコイルを同時にパルスしたときの規定**（同時通電数・電源の要件）: どこにも無い。あるのは「並列にするなら各コイルに直列ダイオード」（Panasonic・Fujitsu 共通資料）だけ。
- **最大通電電流**: TQ（PC 板・表面実装とも）と S 本体には無い。
- **容量負荷・突入電流の個別規定**: AZ850・G6K・TQ・DS4E・RA4・S・SP のどの DS にも無い。Panasonic 共通注意事項の一般表（容量負荷 20〜40 倍）と「DC 容量負荷は実機確認が必須」だけ。
- **1 つのリレーで信号と電源を混ぜることへの個別規定**: 個別 DS には無い。Panasonic 共通注意事項に「大負荷と低レベル負荷を 1 個で開閉するのは望ましくない」「多極で異なる電源回路を開閉するときは沿面・空間距離を確かめよ」、S の DS に「端子 2,3–4,5 と 8,9–10,11 の間で異なるチャンネルの負荷を接続しない」。
