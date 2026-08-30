# AudioV2 予定部品 — データシート

設計判断（[DECISIONS.md](../DECISIONS.md)）で確定・想定している部品の一次資料。オフライン参照用にローカル PDF を置く。

## 電源・PD

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **DKMW20F-12** | ±12 V DC-DC（AudioV2 PowerModule） | [MeanWell_SKMW20_DKMW20.pdf](MeanWell_SKMW20_DKMW20.pdf) | [Mean Well SKMW20/DKMW20](https://www.meanwell.com/webapp/product/search.aspx?prod=DKMW20)。F-12 は ±12 V / ±830 mA。`Audio/datasheets/` と同内容 |
| **BP5293-50** | 操作板 +5 V（Controll 系） | [ROHM_BP5293-xx.pdf](ROHM_BP5293-xx.pdf) | [ROHM BP5293-xx](https://www.rohm.com/products/power-management/switching-regulators-integrated-fet/bp5293-xx-series)（7–26 V in → 5 V / 1 A） |

## 音量・トーン

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PGA2310PA** ×2 | HP / LINE 音量（SPI、Amp 後） | [TI_PGA2310.pdf](TI_PGA2310.pdf) | [TI SBOS187C](https://www.ti.com/lit/ds/symlink/pga2310.pdf) |
| **PT2314** | Bass / Treble（I²C、Amp 前） | [Princeton_PT2314.pdf](Princeton_PT2314.pdf) | Princeton Technology PT2314 v1.1（TDA7313/7314 系 1 バイト I²C） |

## リレー盤（B2-exp）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **MCP23017** | I²C GPIO 拡張（コイル駆動ビット） | [Microchip_MCP23017.pdf](Microchip_MCP23017.pdf) | [Microchip DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf) |
| **ULN2803A** | ダーリントン（コイル電流） | [ST_ULN2803A.pdf](ST_ULN2803A.pdf) | [ST ULN2803A](https://www.st.com/resource/en/datasheet/uln2803a.pdf) |
| **AZ850P2-x** | ラッチング DPDT リレー | [Zettler_AZ850.pdf](Zettler_AZ850.pdf) | [Zettler AZ850](https://zettlerelectronics.com/products/AZ850.pdf)（P2 = デュアルコイル） |

## UI・MCU

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **SSD1306** | 制御 OLED ×2 / 計測 OLED | [Solomon_SSD1306.pdf](Solomon_SSD1306.pdf) | [Solomon Systech SSD1306](https://www.solomon-systech.com/product/ssd1306/) |
| **RP2350** | Pico 2（操作・計測） | [RaspberryPi_RP2350.pdf](RaspberryPi_RP2350.pdf) | [Raspberry Pi RP2350 Datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |

## 計測（独立・参考）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PCM1804** | 計測 ADC（I²S マスタ） | [TI_PCM1804.pdf](TI_PCM1804.pdf) | [TI PCM1804](https://www.ti.com/lit/ds/symlink/pcm1804.pdf) |
| **OPA1656** | 計測フロントエンド | [TI_OPA1656.pdf](TI_OPA1656.pdf) | [TI OPA1656](https://www.ti.com/lit/ds/symlink/opa1656.pdf) |

## 未収録（回路起こし時に追加）

- PD 給電モジュール（差し替え可・型未定）
- ロータリエンコーダー（機械部品）
- Amp / HeadphoneBuffer 用オペアンプ（`Audio/` 参照のまま）

## 更新

2026-08-30: 初回一括取得（DECISIONS 確定部品 + 計測参考 + RP2350）。
