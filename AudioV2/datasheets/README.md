# AudioV2 予定部品 — データシート

設計判断（[DECISIONS.md](../DECISIONS.md)）で確定・想定している部品の一次資料。オフライン参照用にローカル PDF を置く。

## 電源・PD

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **[50224] CH224** | USB-PD 入力（デフォルト） | [StrawberryLinux_CH224K_manual.pdf](StrawberryLinux_CH224K_manual.pdf) / [50224 メモ](StrawberryLinux_50224_CH224K.md) / [WCH_CH224.pdf](WCH_CH224.pdf) | [50224 商品](https://strawberry-linux.com/catalog/items?code=50224) / [説明書 PDF](https://strawberry-linux.com/pub/ch224k-manual.pdf) |
| **DKMW20F-12** | ±12 V DC-DC（AudioV2 PowerModule） | [MeanWell_SKMW20_DKMW20.pdf](MeanWell_SKMW20_DKMW20.pdf) | [Mean Well SKMW20/DKMW20](https://www.meanwell.com/webapp/product/search.aspx?prod=DKMW20)。F-12 は ±12 V / ±830 mA |
| **BP5293-50** | 操作板 +5 V（Controll 系） | [ROHM_BP5293-xx.pdf](ROHM_BP5293-xx.pdf) | [ROHM BP5293-xx](https://www.rohm.com/products/power-management/switching-regulators-integrated-fet/bp5293-xx-series) |

## 音量・トーン

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PGA2310PA** ×2 | HP / LINE 音量（SPI、Amp 後） | [TI_PGA2310.pdf](TI_PGA2310.pdf) | [TI SBOS187C](https://www.ti.com/lit/ds/symlink/pga2310.pdf) |
| **PT2314** | Bass / Treble（I²C、Amp 前） | [Princeton_PT2314.pdf](Princeton_PT2314.pdf) | Princeton Technology PT2314 v1.1 |

## リレー盤（B2-exp）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **MCP23017** | I²C GPIO 拡張 | [Microchip_MCP23017.pdf](Microchip_MCP23017.pdf) | [Microchip DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf) |
| **ULN2803A** | コイル駆動 | [ST_ULN2803A.pdf](ST_ULN2803A.pdf) | [ST ULN2803A](https://www.st.com/resource/en/datasheet/uln2803a.pdf) |
| **AZ850P2-x** | ラッチング DPDT | [Zettler_AZ850.pdf](Zettler_AZ850.pdf) | [Zettler AZ850](https://zettlerelectronics.com/products/AZ850.pdf) |

## UI・MCU

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **SSD1306** | OLED ×2 | [Solomon_SSD1306.pdf](Solomon_SSD1306.pdf) | [Solomon Systech SSD1306](https://www.solomon-systech.com/product/ssd1306/) |
| **RP2350** | Pico 2 | [RaspberryPi_RP2350.pdf](RaspberryPi_RP2350.pdf) | [Raspberry Pi RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |
| **ロータリ ENC ×6** | 操作パネル | [RotaryEncoder_EC11_generic.md](RotaryEncoder_EC11_generic.md) | 汎用 EC11 系（固定足東西・D カット）。PDF 不要 |

## 計測（独立・参考）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PCM1804** | 計測 ADC | [TI_PCM1804.pdf](TI_PCM1804.pdf) | [TI PCM1804](https://www.ti.com/lit/ds/symlink/pcm1804.pdf) |

## AudioV2 に置かないもの（`Audio/` 流用）

- **AmpModule / HeadphoneBuffer** のオペアンプ → 現行 `Audio/` 参照。ローカル DS 不要
- 計測フロントの **OPA1656** も MeasurementADC 流用のため AudioV2 では未収録

## 未収録（回路起こし時に追加）

- PD モジュールの差し替え候補（CH224 以外を試す場合）
- 購入 ENC のメーカー寸法図（フットプリント作成時）

## 更新

- 2026-08-30: 初回一括取得
- 2026-08-30: CH224 [50224]、ENC 機械仕様、Amp/HP 流用方針。OPA1656 削除
- 2026-08-30: `ch224k-manual.pdf` を `StrawberryLinux_CH224K_manual.pdf` としてローカル保存
