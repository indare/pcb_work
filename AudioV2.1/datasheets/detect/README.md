# detect/ — 娘のレール検知（RAIL_GOOD）の検討で取った DS

2026-09-25 取得。検討の本文は `out/v21/rail_detect.md`（リポジトリ外・gitignore）。
版は各 PDF の表紙・フッタの文字列（自分で `pdftotext` して確かめた）。SHA-256 は先頭 12 桁。

| ファイル | 版 | ページ | URL | SHA-256 |
|---|---|---:|---|---|
| TI_TPS3701.pdf | SBVS240C – NOV 2014 – REVISED FEB 2019 | 28 | https://www.ti.com/lit/ds/symlink/tps3701.pdf | 27c94a6c3a24 |
| TI_TLV6710.pdf | SNVSAV4B – JAN 2018 – REVISED OCT 2018 | 28 | https://www.ti.com/lit/ds/symlink/tlv6710.pdf | f068d52942be |
| TI_TPS3700.pdf | SBVS187G – FEB 2012 – REVISED FEB 2019 | 27 | https://www.ti.com/lit/ds/symlink/tps3700.pdf | 3bb7daed20b1 |
| TI_TLV6700.pdf | SNVSAV2B – JAN 2018 – REVISED NOV 2019 | 42 | https://www.ti.com/lit/ds/symlink/tlv6700.pdf | b97ac5c46caa |
| TI_TLV6703.pdf | SBOS865B – JAN 2018 – REVISED NOV 2019 | 27 | https://www.ti.com/lit/ds/symlink/tlv6703.pdf | c8e463db96bd |
| TI_TPS3808.pdf | SBVS050N – MAY 2004 – REVISED AUGUST 2026 | 39 | https://www.ti.com/lit/ds/symlink/tps3808.pdf | 74d889c0f68a |
| TI_TPS3890.pdf | SLVSD65A – MAR 2016 – REVISED MAY 2016 | 27 | https://www.ti.com/lit/ds/symlink/tps3890.pdf | ee79599730e7 |
| TI_LM8364.pdf | SNVS232B – MAR 2003 – REVISED APR 2013 | 15 | https://www.ti.com/lit/ds/symlink/lm8364.pdf | 8c9a15853973 |
| TI_TLV1702.pdf | SBOS589D – DEC 2013 – REVISED JUN 2015 | 39 | https://www.ti.com/lit/ds/symlink/tlv1702.pdf | b971c8ca9ae7 |
| TI_TLV3202.pdf | SBOS561C – MAR 2012 – REVISED MAY 2024 | 40 | https://www.ti.com/lit/ds/symlink/tlv3202.pdf | 1777bba814c7 |
| TI_LM393.pdf | SLCS005AH – OCT 1979 – REVISED APR 2025 | 56 | https://www.ti.com/lit/ds/symlink/lm393.pdf | dd9f3d029261 |
| TI_TLV431.pdf | SLVS139Z – JUL 1996 – REVISED JUN 2024 | 58 | https://www.ti.com/lit/ds/symlink/tlv431.pdf | 6999c7cde8d7 |
| TI_LM4040-N.pdf | SNOS633N – DEC 1991 – REVISED AUG 2025 | 86 | https://www.ti.com/lit/ds/symlink/lm4040-n.pdf | f3977fc3d89b |
| TI_SN74LVC1G123.pdf | SCES586E – JUL 2004 – REVISED MAR 2024 | 32 | https://www.ti.com/lit/ds/symlink/sn74lvc1g123.pdf | 7248ef0ff62a |
| TI_SN74LVC1G14.pdf | SCES218AA – APR 1999 – REVISED OCT 2025 | 52 | https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf | d64e41f0a267 |
| TI_SN74LVC1G08.pdf | SCES217AA – APR 1999 – REVISED AUGUST 2026 | 50 | https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf | 30b963cc4423 |
| TI_SN74LVC1G32.pdf | SCES219W – APR 1999 – REVISED AUGUST 2026 | 51 | https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf | b64786a568ab |
| TI_SN74LVC2G08.pdf | SCES198N – APR 1999 – REVISED DEC 2015 | 26 | https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf | 75dff6a7b9ba |
| TI_SLVA600.pdf | SLVA600 – July 2013（応用ノート: TPS3700 で負レール） | 6 | https://www.ti.com/lit/an/slva600/slva600.pdf | 63304853b7a2 |
| TI_SLVA450.pdf | SLVA450B – FEB 2011 – REVISED APR 2021（応用ノート: 分圧と精度） | 10 | https://www.ti.com/lit/an/slva450/slva450.pdf | 44f8564ad047 |
| Diodes_BAT54.pdf | DS11005 Rev. 34 - 2（November 2023） | 5 | https://www.diodes.com/assets/Datasheets/ds11005.pdf | 50b04e4e17bc |
| Diodes_BZX84C.pdf | DS18001 Rev. 33 - 2 | 5 | https://www.diodes.com/assets/Datasheets/ds18001.pdf | 70c346b571aa |
| AmericanZettler_AZ850.pdf | 本文は `../Zettler_AZ850.pdf` と同じ 2019-03-26 版（3 ページ目に販売拠点が付いただけ。PDF ModDate 2023-09-24） | 3 | https://www.azettler.com/pdfs/az850.pdf | e6e0129d0fdc |

取れなかったもの（この環境から `analog.com` は接続が落ちる。DigiKey API の `DatasheetUrl` は analog.com を指す）:
LTC2914（`2914fc.pdf`）・LTC2966・ADM12914・MAX16054 ほか ADI/Maxim の監視 IC。Zettler の `ApplicationNotes.pdf`（DS が参照する URL は 404）。
