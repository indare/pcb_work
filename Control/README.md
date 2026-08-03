# Pico 2 Control Notes

## Board

- Board: Raspberry Pi Pico 2
- MCU: RP2350
- Firmware: MicroPython v1.28.0
- Bootloader drive name before flashing: `RP2350`

## Dual-board layout

| | Parent | Expansion (child) |
| --- | --- | --- |
| Firmware | `main.py` | `slave.py`（書き込み時は `:main.py`） |
| OLED | あり（J17） | なし |
| Encoder | あり（J13） | なし |
| Relays | UI CH1–5 | UI CH6–10（基板上はローカルCH1–5） |
| I2C role | master `400kHz` | slave `0x42` |

Parent J17（`GND` / `3V3` / `SCL` / `SDA`）を child J17 に延長する。エンコーダは親だけ。

## OLED Connection

| Pico 2 physical pin | Pico 2 signal | OLED signal |
| --- | --- | --- |
| 26 | GP20 / I2C0 SDA | SDA |
| 27 | GP21 / I2C0 SCL | SCL |
| 36 | 3V3 OUT | VCC |
| GND | GND | GND |

## I2C expansion protocol

Shared constants live in `protocol.py`.

| Register | Meaning |
| --- | --- |
| 0 | command（親が書く） |
| 1 | status |
| 2 | completion counter（コマンド完了で +1） |

| Command | Meaning |
| --- | --- |
| `0x00` | 全ローカルCH RESET |
| `0x01`–`0x05` | ローカルCH apply（ポップ対策シーケンス込み） |
| `0x10` | ping → status `0xA5` |

バス速度は 400kHz。100kHz に落とすと SSD1306 の 1KB フレーム転送が I2C タイムアウトに掛かり、描画が砂嵐になる。カスケードで波形が厳しい場合は速度を下げるのではなく `show()` をページ分割すること。

親の挙動:

- 起動時に `0x42` を scan + ping。いなければ **CH1–5 のみ**
- CH1–5 apply 時: 子へ RESET → 親ローカル apply
- CH6–10 apply 時: 親ローカル RESET → 子へ apply(`CH-5`)

## Files

| File | Role |
| --- | --- |
| `main.py` | 親UI（エンコーダ / OLED / 振り分け） |
| `slave.py` | 子I2Cスレーブ |
| `relays.py` | リレーGPIOと切替シーケンス |
| `protocol.py` | アドレス・コマンド定義 |
| `ssd1306.py` | OLEDドライバ |
| `encoder_debug.py` | エンコーダ生ログ |

## Rotary Encoder Connection

| Pico physical pin | Pico signal | Encoder signal |
| --- | --- | --- |
| 29 | GP22 | ENC_A |
| 31 | GP26 / ADC0 | ENC_B |
| 32 | GP27 / ADC1 | ENC_SW |

J13 pinout: `1=ENC_A`, `2=ENC_B`, `3=ENC_SW`, `4=3V3`, `5=GND`  
（逆挿しすると 3V3–GND 短絡でハングするので向き注意）

## Relay mapping (local board)

| Local CH | AUDIO | PWR |
| --- | --- | --- |
| 1 | K4 | K3 |
| 2 | K2 | K1 |
| 3 | K8 | K5 |
| 4 | K9 | K6 |
| 5 | K10 | K7 |

Apply sequence: AUDIO RESET → 0.1s → PWR RESET → selected PWR SET → 0.3s → selected AUDIO SET。コイルは 0.1s パルス。

## Upload

macOS example（親）:

```bash
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/protocol.py :protocol.py
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/relays.py :relays.py
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/ssd1306.py :ssd1306.py
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/main.py :main.py
python3 -m mpremote connect /dev/cu.usbmodem* reset
```

macOS example（子 / 拡張）:

```bash
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/protocol.py :protocol.py
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/relays.py :relays.py
python3 -m mpremote connect /dev/cu.usbmodem* fs cp Control/slave.py :main.py
python3 -m mpremote connect /dev/cu.usbmodem* reset
```

Windows では `py -3.13 -m mpremote connect COMx ...`。

BOOTSEL 時は Pico 2 の UF2 を `RP2350` ドライブへコピーして MicroPython を入れる。

## Confirmed so far (single board)

- MicroPython v1.28.0 on Pico 2
- OLED `0x3c` SSD1306 128x64
- Encoder channel select + relay apply on CH1–5
- Controll schematic ERC 0
