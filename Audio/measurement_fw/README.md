# MeasurementADC ファームウェア

計測モジュール側 Pico2（A702）の MicroPython コード。
ハードの立ち上げ経緯は `../MeasurementADC_BRINGUP.md`、進捗は `../MeasurementADC_STATUS.md`。

## 構成

| ファイル | 役割 |
|---|---|
| `i2s_rx.py` | PIO による I2S スレーブ受信（PCM1804 がマスタ） |
| `adc_check.py` | クロック実測と I2S 受信のブリングアップ確認 |

## 使い方

```bash
cd Audio/measurement_fw
mpremote connect <port> cp i2s_rx.py :i2s_rx.py + run adc_check.py
```

正常なら次のようになる。

```
SCKI  12288338 Hz   BCK  3072038 Hz   LRCK  48000.8 Hz
SCKI/LRCK = 256.003     BCK/LRCK = 64.000
```

## ピン割当

A702（Pico2）の実配線。GP9 と GP15 は基板上では未接続で、飛ばし配線で使っている。

| GPIO | 物理ピン | ネット |
|---|---|---|
| GP0 | 1 | `ADC_DATA` |
| GP1 | 2 | `ADC_BCK` |
| GP2 | 4 | `ADC_LRCK` |
| GP3 | 5 | `LCD_SCK` |
| GP4 | 6 | `LCD_MOSI` |
| GP5 | 7 | `LCD_CS` |
| GP6 | 9 | `LCD_DC` |
| GP7 | 10 | `LCD_RST` |
| GP8 | 11 | `LCD_EN` |
| GP9 | 12 | **飛ばし配線** CN3F-1（SCKI）。測定プローブ専用 |
| GP10 | 14 | `TP_SDA` |
| GP11 | 15 | `TP_SCL` |
| GP12 | 16 | `TP_INT` |
| GP13 | 17 | `TP_RST` |
| GP15 | 20 | **飛ばし配線** `ADC_nRST` |

Pico は基板上で横向きに寝ている。**南の列が西から東へ 1〜20、
北の列が東から西へ 21〜40。** 物理12番(GP9) は「南の列を USB 側から 12 個目」。

## 注意

- **GP9 を出力にしないこと。** Y701 と R718(33Ω) を挟んで衝突し SCKI が化ける。
  衝突させると SCKI/LRCK が 256 ではない中途半端な値（実測で 149.2）になる。
  標準にない分周比が出たら、まずドライバの衝突を疑う
- **`machine.I2S` は使えない。** rp2 の実装はクロックを自分で生成するマスタ専用で、
  マスタである PCM1804 と衝突する
- DATA / BCK / LRCK は**連番の GPIO** である必要がある。
  PIO の `wait` が in_base からの相対インデックスでピンを見るため
- RST の H は駆動しない。R719 のプルアップに任せて監視 IC とワイヤ AND にする

## 応急構成（初号機）

`ADC_nRST` は U710 の RESET 出力が L 固定だったため **U710 の 1番をリフト**している。
Y701 は初号 FP の GND/VDD 入れ替えのため空中配線。詳細は `../MeasurementADC_BRINGUP.md`。
