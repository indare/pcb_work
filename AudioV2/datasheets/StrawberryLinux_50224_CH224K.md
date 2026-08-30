# CH224 USB-PD 電源モジュール [50224] — 参照メモ

ストロベリー・リナックス製 PD トリガー基板。AudioV2 PowerModule の **デフォルト PD 入力**（差し替え可）。

- 商品: [50224 CH224 USB-PD電源モジュール](https://strawberry-linux.com/catalog/items?code=50224)
- コントローラ: WCH **CH224K**（昇降圧なし・PD/QC ネゴシエーションのみ）
- モジュール説明書: [StrawberryLinux_CH224K_manual.pdf](StrawberryLinux_CH224K_manual.pdf)（[ch224k-manual.pdf](https://strawberry-linux.com/pub/ch224k-manual.pdf) と同内容）
- チップ DS: [WCH_CH224.pdf](WCH_CH224.pdf)

## 仕様（メーカー記載）

| 項目 | 内容 |
|---|---|
| 出力電圧 | **5 / 9 / 12 / 15 / 20 V**（ジャンパ J1–J3。AC アダプタが対応した電圧のみ） |
| 出力電流 | 接続 PD 電源の能力内（最大 5 A 級。基板側に過電流保護なし） |
| 入力 | USB Type-C（PD）。USB-A QC も可 |
| 付加 | **PG** 端子、**3.3 V**（VDD）端子 |
| サイズ | 約 33.5 × 23 mm、厚み約 5 mm（部品実装前） |
| 内容 | はんだ付き基板、ピンヘッダ、ジャンパ、端子台 |

## AudioV2 での使い方

| 用途 | 推奨ジャンパ | 備考 |
|---|---|---|
| **DKMW20F-12** 一次 | **12 V** または **15 V** | F 系入力 9–36 V。12 V で足りる |
| パネル **12 V LED** | **12 V** タップ | ±12 V アナログレールとは別系統で配線 |
| 将来 20 V PD | 20 V | 余裕確保用。F-12 の入力上限 36 V 内 |

実装は **端子台ワイヤリング**でも **PowerModule へ部品移設**でも可（DECISIONS §8）。

## ジャンパと CH224K CFG

モジュールは抵抗／ジャンパで CFG1–3 を固定。レベル設定表は WCH DS §5.2 参照。

| CFG1 | CFG2 | CFG3 | 要求電圧 |
|:---:|:---:|:---:|:---:|
| 1 | - | - | 5 V |
| 0 | 0 | 0 | 9 V |
| 0 | 0 | 1 | 12 V |
| 0 | 1 | 1 | 15 V |
| 0 | 1 | 0 | 20 V |

（ストロベリー FAQ: モジュールのジャンパ表記は DS 表と読み方が異なる場合あり → 実機で PG と DMM 確認）

## 関連リンク

- [CH224 データシート（WCH）](https://www.wch.cn/downloads/CH224DS1_PDF.html)
- [50224 サポート FAQ](https://strawberry-linux.com/support/50224/260850)
