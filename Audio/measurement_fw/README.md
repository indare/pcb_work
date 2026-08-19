# MeasurementADC ファームウェア

計測モジュール側 Pico2（A702）の MicroPython コード。
ハードの現状は `../MeasurementADC_STATUS.md`、切り分け履歴は `../MeasurementADC_BRINGUP.md`。

## 構成

| ファイル | 役割 |
|---|---|
| `i2s_rx.py` | PIO I2S スレーブ受信（PCM1804 がマスタ）。`start_into` / `wait` で DMA 重ね取り可 |
| `fft.py` | FFT とオクターブ集計。固定小数点＋低域 IIR |
| `spectrum.py` | 受信→10 バンド。ダブルバッファで DMA と FFT を重ねる |
| `lcd.py` | ST7796S（SPI0 GP18/19、MADCTL `0xE8`） |
| `touch.py` | FT6336U（I2C1 GP10/11） |
| `spectrum_lcd.py` | LCD 10 バンド UI＋下端タッチメニュー |
| `adc_check.py` | クロック実測と I2S ブリングアップ |
| `fft_test.py` | `fft.py` の自己検証 |
| `spectrum_monitor.py` | 10 バンドをシリアル表示 |
| `lcd_test.py` | LCD 単体確認 |
| `main.py` | 電源投入で `spectrum_lcd.main()` を起動 |

## 使い方

```bash
cd Audio/measurement_fw

# ハード確認
mpremote connect COMx cp i2s_rx.py : + run adc_check.py

# LCD スペアナ一式＋起動用 main.py
mpremote connect COMx fs cp lcd.py touch.py fft.py i2s_rx.py spectrum.py spectrum_lcd.py main.py :
# 以降はリセット／電源投入でスペアナが自動起動する
```

`adc_check.py` が正常ならおおよそ次のとおり。

```
SCKI  12288215 Hz   BCK  3072015 Hz   LRCK  48000.5 Hz
SCKI/LRCK = 256.002     BCK/LRCK = 64.000
```

## LCD スペアナ UI

- 既定 **30**（1/3 oct, 25…20k）。タッチで **15**（2/3 oct 系 GEQ, 25…16k）と切替
- 低域（FFT ビン不足）は IIR バンドパス（バンド幅に応じた Q）
- 表示レンジ既定 −60〜−18 dBFS。タッチで切替可
- 下端メニュー（左→右）: レンジ / L+R|L|R / 色 / **30|15** / ピーク
- タッチ座標（MADCTL `0xE8`）: `x = 479 - ty`, `y = tx`

## ピン割当

基板ヘッダのネット名と、**初号の実配線**が違うものに注意。

| GPIO | 物理 | 設計ネット | 初号の実体 |
|---|---|---|---|
| GP0 | 1 | `ADC_DATA` | そのまま |
| GP1 | 2 | `ADC_BCK` | そのまま |
| GP2 | 4 | `ADC_LRCK` | そのまま |
| GP3 | 5 | `LCD_SCK` | **未使用（入力）**。SCK は GP18 |
| GP4 | 6 | `LCD_MOSI` | **未使用（入力）**。MOSI は GP19 |
| GP5 | 7 | `LCD_CS` | そのまま |
| GP6 | 9 | `LCD_DC` | そのまま |
| GP7 | 10 | `LCD_RST` | そのまま |
| GP8 | 11 | `LCD_EN` | High で LCD_VCC ON |
| GP9 | 12 | （空き） | **飛ばし** CN3F-1（SCKI センス）。**駆動禁止** |
| GP10 | 14 | `TP_SDA` | そのまま |
| GP11 | 15 | `TP_SCL` | そのまま |
| GP12 | 16 | `TP_INT` | そのまま |
| GP13 | 17 | `TP_RST` | そのまま |
| GP15 | 20 | （空き） | **飛ばし** `ADC_nRST`（OD） |
| GP16 | — | （空き） | SPI0 ダミー MISO |
| GP18 | 24 | （空き） | **LCD SCLK 飛ばし** |
| GP19 | 25 | （空き） | **LCD MOSI 飛ばし** |

Pico は横向き。**南の列が西→東 1〜20、北の列が東→西 21〜40。**

## 注意

- **GP9 を出力にしない**（Y701 と衝突して SCKI が化ける）
- **`machine.I2S` は使えない**（rp2 はマスタ専用）
- DATA/BCK/LRCK は連番 GPIO（PIO の相対ピン）
- RST の H は駆動しない（R719 プルアップ＋ワイヤ AND）
- ノイズ床の引き算はしていない。棒が短いのは表示下限（既定 −60 dBFS）による

## 応急構成（初号機）

U710 1番リフト、Y701 空中配線、LCD SPI 飛ばし。詳細は `../MeasurementADC_BRINGUP.md`。
