# AudioV2.1 firmware（MicroPython / Pico 2）

1 台の Pico（`MeasureControl` の Pico）向けの**骨格**。v2 から写したままで、v2.1 の制御の木（電源用・音声用リレー、ch の LDO の EN、レール監視）はまだ入っていない。
v2.1 でファームが守ること・ハードが保証することの正は [DECISIONS.md](../DECISIONS.md) §6。コード中のコメントで v1・v2 を引いているところは v2 のときの記録。

## 方針（今の骨格の形）

| | |
|---|---|
| 操作 | ENC×3 / DEST SW / ポット（回路どおり。タッチ必須にしない） |
| 表示 | Waveshare LCD に CH / DEST / Bass / Treble（OLED なし） |
| Amp 切替 | `amp_select.py` が入口。今は v2 の 2 版（Switch / Relay）用の形。v2.1 の娘は 1 種類で、娘の MCP を残すかは未決（V21-未決-03） |
| I²C0 | PT2314E 同居のため **100 kHz** |
| 計測 | スペアナ／キャプチャは v2.1 には無い。後で同じ LCD 上にモードとして足す |

ピン・アドレスの正は回路図（MeasureControl の Pico 注記、FrontPanel の MCP）。ここに数値を複製しない。

### Switch SEL（起動、今の骨格）

外付け SEL→`D_GND` プルは回路に置かない（TMUX7612 内蔵プルダウン）。
v2.1 では EN は既定 OFF のデコーダと ±15 V の確認の後にだけ出す（DECISIONS §2-9・§6）。詳細は [`amp_select.py`](amp_select.py) 先頭（v2 の形）。

## ディレクトリ

```
firmware/
  README.md
  main.py           # 起動（状態表示＋ENC ループ）
  board.py          # ネット名 → GP / I²C の対応（回路図と揃える）
  encoders.py       # FrontPanel MCP23017（INTA/INTB）
  tone.py           # PT2314E（Bass/Treble）
  amp_select.py     # CH 切替の共通入口
  ui_status.py      # LCD 上の状態バー
  vendor/
    lcd_st7796.py   # Waveshare ST7796S（v1 の計測ファームの LCD ドライバから分岐）
```

## 書き込み（骨格）

```bash
cd AudioV2.1/firmware
mpremote connect <port> fs cp board.py encoders.py tone.py amp_select.py ui_status.py main.py :
mpremote connect <port> fs cp vendor/lcd_st7796.py :lcd_st7796.py
mpremote connect <port> reset
```

実機未検証の骨格。動かすときはまず `ui_status` の静的表示、次に ENC INT、最後に Amp 切替。
