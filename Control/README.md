# Pico 2 Control Notes

## Board

- Board: Raspberry Pi Pico 2
- MCU: RP2350
- Firmware: MicroPython v1.28.0
- USB serial port during this test: COM3
- Bootloader drive name before flashing: RP2350

## OLED Connection

The OLED is connected by I2C.

| Pico 2 physical pin | Pico 2 signal | OLED signal |
| --- | --- | --- |
| 26 | GP20 / I2C0 SDA | SDA |
| 27 | GP21 / I2C0 SCL | SCL |
| 36 | 3V3 OUT | VCC |
| GND | GND | GND |

MicroPython I2C setup:

```python
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400_000)
```

## Confirmed Results

- Pico 2 was visible as `RP2350` in BOOTSEL mode.
- MicroPython firmware was copied to the RP2350 mass storage drive.
- After reboot, Pico 2 appeared as USB serial `COM3`.
- Onboard green LED blink test worked.
- OLED I2C scan found address `0x3c`.
- The OLED worked as an SSD1306-compatible `128x64` monochrome display.
- Valid pixel area is `x=0..127`, `y=0..63`.
- Drawing at or beyond `x=128` / `y=64` is outside the visible area.
- 8px text placed at `y=57` is clipped at the bottom, so safe text rows are `0, 8, 16, 24, 32, 40, 48, 56`.

## Current Test Program

- `main.py` initializes I2C on GP20/GP21.
- `ssd1306.py` provides the minimal I2C SSD1306 driver.
- The current display output draws only a 1px border around the full OLED area.
- The onboard LED is turned off after startup.

## Upload Commands

Run from the repository root:

```powershell
py -3.13 -m mpremote connect COM3 fs cp "Control/ssd1306.py" ":/ssd1306.py"
py -3.13 -m mpremote connect COM3 fs cp "Control/main.py" ":/main.py"
py -3.13 -m mpremote connect COM3 reset
```

If the Pico 2 is in BOOTSEL mode, flash MicroPython first by copying the Pico 2 UF2 firmware to the `RP2350` drive.
