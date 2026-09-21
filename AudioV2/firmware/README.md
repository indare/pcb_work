# AudioV2 firmware（MicroPython / Pico 2）

1 台の Pico（`MeasureControl` の `A1602`）向け。v1 の `Control/`（OLED＋リレーGPIO）と
`Audio/measurement_fw/`（スペアナ）は**参照用**。ここに AudioV2 用を置く。

## 方針

| | |
|---|---|
| 操作 | ENC×3 / DEST SW / ポット（回路どおり。タッチ必須にしない） |
| 表示 | Waveshare LCD に CH / DEST / Bass / Treble（OLED なし） |
| Amp 切替 | **Switch / Relay 共通 API**（`amp_select.py`）。裏の I²C／SEL だけ差し替え |
| I²C0 | PT2314E 同居のため **100 kHz**（OLED が居ないので足りる） |
| 計測 | スペアナ／キャプチャは後で同じ LCD 上にモード追加。当面は `Audio/measurement_fw/` |

ピン・アドレスの正は回路図（MeasureControl の Pico 注記、FrontPanel の MCP）。  
ここに数値を複製しない（[SOURCE_OF_TRUTH.md](../../SOURCE_OF_TRUTH.md)）。

## ディレクトリ

```
firmware/
  README.md
  main.py           # 起動（状態表示＋ENC ループ）
  board.py          # ネット名 → GP / I²C の対応（回路図と揃える）
  encoders.py       # FrontPanel MCP23017（INTA/INTB）
  tone.py           # PT2314E（Bass/Treble）
  amp_select.py     # CH 切替の共通入口（switch / relay）
  ui_status.py      # LCD 上の状態バー
  vendor/
    lcd_st7796.py   # Waveshare ST7796S（measurement_fw から分岐）
```

## 書き込み（骨格）

```bash
cd AudioV2/firmware
mpremote connect <port> fs cp board.py encoders.py tone.py amp_select.py ui_status.py main.py :
mpremote connect <port> fs cp vendor/lcd_st7796.py :lcd_st7796.py
mpremote connect <port> reset
```

実機未検証の骨格。動かすときはまず `ui_status` の静的表示、次に ENC INT、最後に Amp 切替。
