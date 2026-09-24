# 手持ちオペアンプ在庫（ユーザー申告）

**更新:** 2026-09-24  
**用途:** AmpModule / AudioV2 AmpChannel DIP 差し替え比較・計測まわりの候補把握。数量は未記入（都度確認）。

標準実装（基板に載っている／載せる前提）は [README.md](README.md) のソケット表を正とする。  
データシート PDF: [datasheets/opamps/](datasheets/opamps/README.md)  

**高速寄りの DS 精査（対象・根拠・高速娘の対応策）:** [OPAMP_FAST_DS_REVIEW.md](OPAMP_FAST_DS_REVIEW.md)

## 手持ちリスト

| 表記（手元） | 解釈・備考 | Amp DIP-8 差し替え | DS |
|---|---|---|---|
| OPA828 のデュアル実装 DIP 版 | OPA828×2 を DIP 化した完成基板／モジュール想定 | 可（高速・CL 隔離。詳細は FAST 精査） | [PDF](datasheets/opamps/TI_OPA828.pdf) |
| **NJM5532DD** | 5532 系 DIP | 可（NE5532 相当） | [PDF](datasheets/opamps/NJR_NJM5532.pdf) |
| **NJM4580DD** | DIP | 可 | [PDF](datasheets/opamps/NJR_NJM4580.pdf) |
| **OPA2134PA** | DIP（デュアル JFET） | 可 | [PDF](datasheets/opamps/TI_OPA2134.pdf) |
| **OPA1656ID** | SOIC-8（MeasurementADC 用石。DIP ソケット直挿し不可） | 要変換 or SOP 実装のみ | [PDF](datasheets/opamps/TI_OPA1656.pdf) |
| **OPA2604AQ** | （表記 AQ — パッケージ要実物確認） | 要確認 | [PDF](datasheets/opamps/TI_OPA2604.pdf) |
| **LME49860NA** | DIP | 可（高速・20 k 網では電流ノイズ注意） | [PDF](datasheets/opamps/TI_LME49860.pdf) |
| **「OPA1652」DIP 化モジュール** | 共立 Q5M411 系。AdcBuffer 標準 | Amp にも挿せるが測定基準は固定推奨 | [PDF](datasheets/opamps/TI_OPA1652.pdf) |
| **OPA627AU** 2 回路 DIP 化完成基板 | シングル×2 の DIP 化モジュール | 可 | [PDF](datasheets/opamps/TI_OPA627.pdf) |
| **MUSES02D** | DIP | 可 | [PDF](datasheets/opamps/NJR_MUSES02.pdf) |
| **OPA1612** 2 回路 8Pin DIP 化完成基板 | DIP 化モジュール | 可（20 k 網では電流ノイズ不利） | [PDF](datasheets/opamps/TI_OPA1612.pdf) |
| **LT1364CN8** | DIP | 可（GBW 高くデカップ／帰還注意） | [PDF](datasheets/opamps/AD_LT1364.pdf) |
| **OPA2140AIDR** 2 回路 JFET DIP | DIP 化／変換実装 | 可 | [PDF](datasheets/opamps/TI_OPA2140.pdf) |
| **MUSE01**（×2 → 1×DIP 変換） | シングル相当 **2 個**を 1 個の DIP-8 に挿す変換基板。表記は MUSE01（MUSES01 ではない） | 可（変換ごと Amp ソケットへ） | [PDF](datasheets/opamps/NJR_MUSES01.pdf) |
| **MUSE03**（×2 → DIP 化・2ch 変換基板） | シングル相当 **2 個**を DIP 化し 2ch にした変換基板あり。表記は MUSE03（製品 DS 名は **MUSES03**）。J-FET、en 7.5 nV/√Hz、GBW 12 MHz、SR 35 V/µs、Vs ±3.5〜±18（[DS 要点](datasheets/opamps/README.md#muses03-ds-要点)） | 可（変換ごと Amp ソケットへ） | [PDF](datasheets/opamps/NJR_MUSES03.pdf) |
| **AD797**（シングル×2） | 超低ノイズ。L/R で **2 個**（Dual 化変換）。ゲイン 2 は DS Table 6 で可。詳細は FAST 精査 | 可（変換基板。20 k 網では電流ノイズ不利） | メーカー PDF（ローカル未保管。リンクは FAST 精査） |

## AudioV2 ±15 V 電源での可否

AudioV2 のアナログレールは **±15 V**（2026-09-01 に ±12 V から変更。DC-DC の型番と経緯は [AudioV2/DECISIONS.md §8](../AudioV2/DECISIONS.md) が正）。
2026-08-31 の初版は ±12 V（DKMW20F-12）前提だったので、この表は ±15 V で見直した。  
前提: 推奨動作範囲に **±15 V が入るか**（絶対最大だけの「壊れない」判定ではない）。

| 石 | 推奨／動作 Vs（目安） | ±15 V | 備考 |
|---|---|---|---|
| OPA828（×2 DIP 化） | ±4〜±18 | **OK** | |
| NJM5532DD | ±3〜±22 級（5532 系） | **OK** | Amp 標準相当 |
| NJM4580DD | ±2〜±18 級 | **OK** | |
| OPA2134PA | ±2.5〜±18 | **OK** | |
| OPA1656ID | ±2.25〜±18 | **OK** | 計測 SOP。Amp DIP 直挿しは別問題 |
| OPA2604AQ | ±4.5〜±24 級 | **OK** | |
| LME49860NA | ±2.5〜±22 級 | **OK** | |
| OPA1652 DIP 化 | ±2.25〜±18 | **OK** | |
| OPA627AU DIP 化 | ±4.5〜±18 | **OK** | |
| MUSES02D | ±3.5〜±16 | **OK** | 上限 ±16。**余裕 1 V**（DC-DC の出力誤差に注意） |
| OPA1612 DIP 化 | ±2.25〜±18 | **OK** | |
| LT1364CN8 | ±2.5〜±18 級（特性は ±15 表記多い） | **OK** | |
| OPA2140 AIDR DIP | ±2.25〜±18 | **OK** | |
| MUSE01（2→1 DIP） | **±9〜±16**（MUSES01 DS） | **OK** | 上限 ±16。**余裕 1 V**（DC-DC の出力誤差に注意） |
| MUSE03（2→DIP・2ch） | **±3.5〜±18**（MUSES03 DS） | **OK** | J-FET シングル×2 の変換基板 |
| AD797×2 | ±5〜±18（DS の動作範囲。特性は ±5 / ±15 V で規定） | **OK** | シングル×2。ゲイン 2 可（FAST 精査） |

**結論:** 手持ちリストは **すべて ±15 V で電源的に足りる**。落ちる石は無し。上限 ±16 V の MUSES01/02 だけ余裕が 1 V。

電源以外で効く制約（差し替え時）— **AudioV2 `AmpChannel` の帰還網は旧 Amp 図面（47 k）と違う**（値は回路図 `AudioV2/AmpChannel.kicad_sch` が正）:

- 詳細・高速娘の実装案は **[OPAMP_FAST_DS_REVIEW.md](OPAMP_FAST_DS_REVIEW.md)**
- LT1364 / OPA828 / OPA1656 / LME49860 → レイアウト・デカップ・CL（出力 47 Ω は DS の隔離と整合）
- OPA1612 / LME49860 / AD797 → 20 k 網では電流ノイズ不利（高速娘で 2 k へ）
- OPA1656ID → パッケージが SOIC（変換なしでは Amp ソケット不可）

## 基板標準（参考・README と同一）

| 場所 | 標準石 |
|---|---|
| AmpModule `AMP401` | NE5532（ソケット） |
| AdcBuffer `AMP801` | OPA1652AID-DIP（原則固定） |
| HeadphoneBuffer `AMP901` | NJM4556A（**差し替え不可**・電流不足リスク） |

## 差し替え時の注意（要約）

- AudioV2: **[OPAMP_FAST_DS_REVIEW.md](OPAMP_FAST_DS_REVIEW.md)**（DS 根拠・高速娘 Rf/Rg=2 k）
- v1 Amp 時代の抵抗網議論: [AmpModule_OPAMP_REFINE.md](AmpModule_OPAMP_REFINE.md)（前提が古い箇所あり。AudioV2 判断は FAST 精査を正）
- **バイポーラ超低ノイズ**（OPA1612 / LME49860 / AD797）は 20 k 網では電流ノイズで不利になりやすい
- HP バッファに電圧アンプ系（MUSES / OPA 汎用）を入れない
- SOIC 単体（OPA1656ID）は Amp DIP ソケットにそのまま挿せない

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | ユーザー申告リストで初版 |
| 2026-08-31 | MUSE01 = 2 石→1 DIP 変換と訂正 |
| 2026-08-31 | AudioV2 ±12 V 電源可否表を追加（全石 OK） |
| 2026-08-31 | 手持ち全石の DS を `datasheets/opamps/` に保管・索引リンク |
| 2026-08-31 | MUSE03 = 2 石→DIP 化・2ch 変換基板あり、と追記 |
| 2026-08-31 | MUSE03 DS 要点・製品ページ参照を `datasheets/opamps/README.md` に追加 |
| 2026-09-24 | AD797 を手持ちに追加。FAST DS 精査へリンク。AudioV2 20 k 前提の注意に更新 |
| 2026-09-25 | 電源可否表を ±15 V（AudioV2 の現行レール）で見直し。±12 V は 09-01 に廃止済みだった |
