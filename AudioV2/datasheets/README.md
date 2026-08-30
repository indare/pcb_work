# AudioV2 予定部品 — データシート

設計判断（[DECISIONS.md](../DECISIONS.md)）で確定・想定している部品の一次資料。オフライン参照用にローカル PDF を置く。

## 電源・PD

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **[50224] CH224** | USB-PD（PowerModule 内蔵） | [StrawberryLinux_CH224K_manual.pdf](StrawberryLinux_CH224K_manual.pdf) 他 | AudioV2 PowerModule **再設計**に統合 |
| **DKMW20F-12** | ±12 V DC-DC（AudioV2 PowerModule） | [MeanWell_SKMW20_DKMW20.pdf](MeanWell_SKMW20_DKMW20.pdf) | [Mean Well SKMW20/DKMW20](https://www.meanwell.com/webapp/product/search.aspx?prod=DKMW20)。F-12 は ±12 V / ±830 mA |
| **BP5293-50** | 操作板 +5 V（Controll 系） | [ROHM_BP5293-xx.pdf](ROHM_BP5293-xx.pdf) | [ROHM BP5293-xx](https://www.rohm.com/products/power-management/switching-regulators-integrated-fet/bp5293-xx-series) |

## 音量・トーン

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PT2314 DIP-28** | Bass / Treble（I²C、Amp 前） | [Princeton_PT2314.pdf](Princeton_PT2314.pdf) | Princeton Technology PT2314 v1.1 |
| **Alps RK27112A00CF** ×2 | HP / LINE 手回し音量（A50k Dual） | （メーカーカタログ） | [PARTS.md](../PARTS.md) |
| **C&K 7303SYZQE** | DEST 3PDT ON-OFF-ON | [C&K 7000 Series](https://media.digikey.com/pdf/Data%20Sheets/C&K/7000%20Mini%20Toggle%20Series.pdf) | [PARTS.md](../PARTS.md) |
| ~~PGA2310PA~~ | **不採用**（調査アーカイブ） | [TI_PGA2310.pdf](TI_PGA2310.pdf) | [VOLUME_IC_COMPARISON.md](../VOLUME_IC_COMPARISON.md) |

## リレー盤（B2-exp）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **MCP23017** | I²C GPIO 拡張 | [Microchip_MCP23017.pdf](Microchip_MCP23017.pdf) | [Microchip DS20001952C](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf) |
| **ULN2803A** | コイル駆動 | [ST_ULN2803A.pdf](ST_ULN2803A.pdf) | [ST ULN2803A](https://www.st.com/resource/en/datasheet/uln2803a.pdf) |
| **AZ850P2-5** | ラッチング DPDT（**5 V コイル**） | [Zettler_AZ850.pdf](Zettler_AZ850.pdf) | 秋月 [118017](https://akizukidenshi.com/catalog/g/g118017/) |

## UI・MCU

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **SSD1306 / SSD1309** | 制御 OLED 128×64 I²C（**2.42″** 第一） | [Solomon_SSD1306.pdf](Solomon_SSD1306.pdf) | v1 `Control/`。[PARTS.md](../PARTS.md) AliExpress 例 |
| **WAVESHARE-29318** | スペアナ 3.5″ タッチ LCD（ST7796S + FT6336U） | （Wiki） | [スイッチサイエンス 10138](https://www.switch-science.com/products/10138)。`Audio/measurement_fw/` |
| **RP2350** | Pico 2 | [RaspberryPi_RP2350.pdf](RaspberryPi_RP2350.pdf) | [Raspberry Pi RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |
| **ロータリ ENC ×3** | CH / BASS / TREBLE | [RotaryEncoder_EC11_generic.md](RotaryEncoder_EC11_generic.md) | **GPIO 直結**（§10）。押し SW 付き EC11 |

## 計測（独立・参考）

| 部品 | 用途 | ローカル | 取得元 |
|---|---|---|---|
| **PCM1804** | 計測 ADC | [TI_PCM1804.pdf](TI_PCM1804.pdf) | [TI PCM1804](https://www.ti.com/lit/ds/symlink/pcm1804.pdf) |

## AudioV2 に置かないもの（`Audio/` 流用）

- **AmpModule / HeadphoneBuffer** のオペアンプ → [Audio/datasheets/opamps/](../../Audio/datasheets/opamps/README.md)（手持ち在庫のローカル PDF）
- 計測フロントの **OPA1656** も同ディレクトリ（`TI_OPA1656.pdf`）。AudioV2 には複製しない

## 未収録（回路起こし時に追加）

- PD モジュールの差し替え候補（CH224 以外を試す場合）
- 購入 ENC のメーカー寸法図（フットプリント作成時）
- Alps RK27 / C&K 7000 の紙 DS（メーカーページで足りる。必要なら追加）

## 更新

- 2026-08-30: 初回一括取得
- 2026-08-30: CH224 [50224]、ENC 機械仕様、Amp/HP 流用方針。OPA1656 削除
- 2026-08-30: ENC×3 **GPIO 直結**確定（§10）
- 2026-08-30: 表示 — 制御 OLED 2.42″ / スペアナ Waveshare 29318（v1）
- 2026-08-31: Amp/HP OPA DS は `Audio/datasheets/opamps/` を正と明記
