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
- Channel 5 relay SET test worked: K10/K7 moved to SET and continuity was confirmed at four contact points.
- During probing, OLED `CH1` selected the AMP2 connector pair (`J19`/`J20`), so firmware channel numbering uses the probed connector order rather than the relay net suffix order for channels 1 and 2.
- KiCad CLI netlist export confirmed the relay/GPIO mapping below.
- KiCad CLI ERC reported 0 violations for `Audio/Controll.kicad_sch`.

## Pico ADC Pin Status

OLED does not use the Pico ADC pins. In the current schematic:

| Pico physical pin | Pico signal | Current net |
| --- | --- | --- |
| 31 | GP26 / ADC0 | ENC_B |
| 32 | GP27 / ADC1 | ENC_SW |
| 34 | GP28 / ADC2 | Unconnected |
| 35 | ADC_VREF | Unconnected |

## Rotary Encoder Connection

| Pico physical pin | Pico signal | Encoder signal |
| --- | --- | --- |
| 29 | GP22 | ENC_A |
| 31 | GP26 / ADC0 | ENC_B |
| 32 | GP27 / ADC1 | ENC_SW |

## Current Test Program

- `main.py` initializes I2C on GP20/GP21.
- `ssd1306.py` provides the minimal I2C SSD1306 driver.
- The current program runs a rotary encoder channel selector.
- On startup, all relay channels receive a RESET pulse to establish a known state, then channel 1 is applied.
- Turning the encoder changes the selected channel on the OLED.
- Pressing the encoder switch applies the selected channel: all channels RESET, then the selected AUDIO/PWR relay pair SET.
- Relay coils are pulsed for 0.1 seconds and are not held on.
- The OLED shows the selected channel and the currently active channel.

## Relay Test Mapping

Relay pairs by channel:

| Channel | AUDIO relay | PWR relay |
| --- | --- | --- |
| 1 | K4 | K3 |
| 2 | K2 | K1 |
| 3 | K8 | K5 |
| 4 | K9 | K6 |
| 5 | K10 | K7 |

GPIO assignment by channel:

| Channel | Relay | Reset signal | Reset GPIO | Reset physical pin | Set signal | Set GPIO | Set physical pin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | K4 AUDIO | AUDIO_RESET_GPIO_2 | GP5 | 7 | AUDIO_SET_GPIO_2 | GP4 | 6 |
| 1 | K3 PWR | PWR_RESET_GPIO_2 | GP7 | 10 | PWR_SET_GPIO_2 | GP6 | 9 |
| 2 | K2 AUDIO | AUDIO_RESET_GPIO_1 | GP1 | 2 | AUDIO_SET_GPIO_1 | GP0 | 1 |
| 2 | K1 PWR | PWR_RESET_GPIO_1 | GP3 | 5 | PWR_SET_GPIO_1 | GP2 | 4 |
| 3 | K8 AUDIO | AUDIO_RESET_GPIO_3 | GP9 | 12 | AUDIO_SET_GPIO_3 | GP8 | 11 |
| 3 | K5 PWR | PWR_RESET_GPIO_3 | GP11 | 15 | PWR_SET_GPIO_3 | GP10 | 14 |
| 4 | K9 AUDIO | AUDIO_RESET_GPIO_4 | GP13 | 17 | AUDIO_SET_GPIO_4 | GP12 | 16 |
| 4 | K6 PWR | PWR_RESET_GPIO_4 | GP15 | 20 | PWR_SET_GPIO_4 | GP14 | 19 |
| 5 | K10 AUDIO | AUDIO_RESET_GPIO_5 | GP18 | 24 | AUDIO_SET_GPIO_5 | GP19 | 25 |
| 5 | K7 PWR | PWR_RESET_GPIO_5 | GP16 | 21 | PWR_SET_GPIO_5 | GP17 | 22 |

Previous channel 5 firmware test target:

| Relay | Function | Reset signal | Set signal | Pico GPIO |
| --- | --- | --- | --- | --- |
| K10 | AUDIO relay 5 | AUDIO_RESET_GPIO_5 | AUDIO_SET_GPIO_5 | RESET=GP18, SET=GP19 |
| K7 | PWR relay 5 | PWR_RESET_GPIO_5 | PWR_SET_GPIO_5 | RESET=GP16, SET=GP17 |

## Upload Commands

Run from the repository root:

```powershell
py -3.13 -m mpremote connect COM3 fs cp "Control/ssd1306.py" ":/ssd1306.py"
py -3.13 -m mpremote connect COM3 fs cp "Control/main.py" ":/main.py"
py -3.13 -m mpremote connect COM3 reset
```

If the Pico 2 is in BOOTSEL mode, flash MicroPython first by copying the Pico 2 UF2 firmware to the `RP2350` drive.
