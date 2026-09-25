# 手持ちオペアンプ（ユーザー申告）

v2.1 のソケットに挿して聴き比べる石の一覧。**数量は書かない**（都度ユーザーに確認）。
2026-09-25 に v1 の在庫表（2026-09-24 版）から、一覧とパッケージ・変換基板の注記だけを写した。
**v2.1 ではこのファイルが在庫の正。** 在庫が変わったらここを直す。

- DS の PDF は [datasheets/opamps/](datasheets/opamps/)。DS から読んだ事実は [ds_facts/opamps.md](ds_facts/opamps.md)
- 電源（ソケットのレール）で挿せるかどうかは、v2.1 のレールで [ds_facts/opamps.md](ds_facts/opamps.md) から判断する（v1・v2 のレールでの可否表は写していない）
- 高速寄りの石の DS の読み（v1/v2 のころの分析）は [review/opamp_fast_ds_review_v1.md](review/opamp_fast_ds_review_v1.md)

## 一覧

| 表記（手元） | パッケージ・変換基板（申告の解釈） | DS |
|---|---|---|
| OPA828 のデュアル実装 DIP 版 | OPA828 ×2 を DIP-8 にした完成基板／モジュール | [TI_OPA828.pdf](datasheets/opamps/TI_OPA828.pdf) |
| NJM5532DD | DIP-8（5532 系） | [NJR_NJM5532.pdf](datasheets/opamps/NJR_NJM5532.pdf) |
| NJM4580DD | DIP-8 | [NJR_NJM4580.pdf](datasheets/opamps/NJR_NJM4580.pdf) |
| OPA2134PA | DIP-8（デュアル JFET） | [TI_OPA2134.pdf](datasheets/opamps/TI_OPA2134.pdf) |
| OPA1656ID | **SOIC-8**。DIP ソケットに直接は挿せない（変換基板か SOP 実装） | [TI_OPA1656.pdf](datasheets/opamps/TI_OPA1656.pdf) |
| OPA2604AQ | 表記「AQ」。パッケージは実物で要確認 | [TI_OPA2604.pdf](datasheets/opamps/TI_OPA2604.pdf) |
| LME49860NA | DIP-8 | [TI_LME49860.pdf](datasheets/opamps/TI_LME49860.pdf) |
| 「OPA1652」DIP 化モジュール | 共立 Q5M411 系の DIP-8 化モジュール | [TI_OPA1652.pdf](datasheets/opamps/TI_OPA1652.pdf) |
| OPA627AU 2 回路 DIP 化完成基板 | シングル ×2 を DIP-8 にしたモジュール | [TI_OPA627.pdf](datasheets/opamps/TI_OPA627.pdf) |
| MUSES02D | DIP-8 | [NJR_MUSES02.pdf](datasheets/opamps/NJR_MUSES02.pdf) |
| OPA1612 2 回路 8Pin DIP 化完成基板 | DIP-8 化モジュール | [TI_OPA1612.pdf](datasheets/opamps/TI_OPA1612.pdf) |
| LT1364CN8 | DIP-8 | [AD_LT1364.pdf](datasheets/opamps/AD_LT1364.pdf) |
| OPA2140AIDR 2 回路 JFET DIP | DIP 化／変換実装 | [TI_OPA2140.pdf](datasheets/opamps/TI_OPA2140.pdf) |
| MUSE01（×2 → 1×DIP 変換） | シングル **2 個**を 1 個の DIP-8 に挿す変換基板。表記は MUSE01、製品の DS 名は **MUSES01** | [NJR_MUSES01.pdf](datasheets/opamps/NJR_MUSES01.pdf) |
| MUSE03（×2 → DIP 化・2ch 変換基板） | シングル **2 個**を DIP-8・2ch にした変換基板。表記は MUSE03、製品の DS 名は **MUSES03**（J-FET） | [NJR_MUSES03.pdf](datasheets/opamps/NJR_MUSES03.pdf) |
| AD797（シングル ×2） | L/R で **2 個**。デュアル化の変換基板 | [AD_AD797.pdf](datasheets/opamps/AD_AD797.pdf)（Rev. K） |

参考（手持ちではない）: NE5532 本家の DS [TI_NE5532.pdf](datasheets/opamps/TI_NE5532.pdf)（`ds_facts/opamps.md` の比較の基準）。

## DS の出どころ（取得メモ）

- TI: `https://www.ti.com/lit/ds/symlink/<part>.pdf`
- Nisshinbo（NJR）: 製品ページの DS PDF。MUSES03 は秋月公開 PDF（`MUSES03_J-1.pdf`）を `NJR_MUSES03.pdf` として保管
- LT1364: メーカーの URL が不安定だったため Internet Archive 経由
- OPA2604: TI のリダイレクトを避けて DigiKey 公開 PDF
- AD797: Analog Devices Rev. K（2015-03）
