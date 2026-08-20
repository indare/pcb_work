"""ST7796S bring-up on MeasurementADC (Waveshare 29318).

Pins are not a hardware SPI pair (SCK=GP3, MOSI=GP4), so this uses SoftSPI.
Do not touch GP9 (SCKI sense) or GP15 (ADC_nMR; OD only, do not drive H).
"""
import time
from machine import Pin, SoftSPI

LCD_W = 320
LCD_H = 480

# RGB565
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
WHITE = 0xFFFF
BLACK = 0x0000
YELLOW = 0xFFE0
CYAN = 0x07FF


def _u16(c):
    return bytes((c >> 8, c & 0xFF))


class Lcd:
    def __init__(self):
        self.en = Pin(8, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(6, Pin.OUT, value=1)
        self.rst = Pin(7, Pin.OUT, value=1)
        self.spi = SoftSPI(
            baudrate=4_000_000,
            polarity=0,
            phase=0,
            sck=Pin(3),
            mosi=Pin(4),
            miso=Pin(14),
        )
        self._init()

    def _cmd(self, c, data=b""):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytes((c,)))
        if data:
            self.dc(1)
            self.spi.write(data if isinstance(data, (bytes, bytearray)) else bytes(data))
        self.cs(1)

    def _init(self):
        self.rst(0)
        time.sleep_ms(100)
        self.rst(1)
        time.sleep_ms(10)
        self._cmd(0x11)
        time.sleep_ms(120)
        self._cmd(0x36, b"\x08")
        self._cmd(0x3A, b"\x05")
        self._cmd(0xF0, b"\xC3")
        self._cmd(0xF0, b"\x96")
        self._cmd(0xB4, b"\x01")
        self._cmd(0xB7, b"\xC6")
        self._cmd(0xC0, b"\x80\x45")
        self._cmd(0xC1, b"\x13")
        self._cmd(0xC2, b"\xA7")
        self._cmd(0xC5, b"\x0A")
        self._cmd(0xE8, b"\x40\x8A\x00\x00\x29\x19\xA5\x33")
        self._cmd(0xE0, b"\xD0\x08\x0F\x06\x06\x33\x30\x33\x47\x17\x13\x13\x2B\x31")
        self._cmd(0xE1, b"\xD0\x0A\x11\x0B\x09\x07\x2F\x33\x47\x38\x15\x16\x2C\x32")
        self._cmd(0xF0, b"\x3C")
        self._cmd(0xF0, b"\x69")
        time.sleep_ms(120)
        self._cmd(0x21)
        self._cmd(0x29)

    def window(self, x0, y0, x1, y1):
        self._cmd(0x2A, bytes((x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)))
        self._cmd(0x2B, bytes((y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)))
        self._cmd(0x2C)

    def fill_rect(self, x, y, w, h, color):
        self.window(x, y, x + w - 1, y + h - 1)
        pix = _u16(color)
        line = pix * w
        self.dc(1)
        self.cs(0)
        for _ in range(h):
            self.spi.write(line)
        self.cs(1)

    def fill(self, color):
        self.fill_rect(0, 0, LCD_W, LCD_H, color)


def main():
    print("lcd init")
    lcd = Lcd()
    print("fill bars")
    lcd.fill(BLACK)
    lcd.fill_rect(0, 0, LCD_W, 160, RED)
    lcd.fill_rect(0, 160, LCD_W, 160, GREEN)
    lcd.fill_rect(0, 320, LCD_W, 160, BLUE)
    lcd.fill_rect(20, 20, LCD_W - 40, 40, WHITE)
    lcd.fill_rect(20, 220, LCD_W - 40, 40, YELLOW)
    lcd.fill_rect(20, 420, LCD_W - 40, 40, CYAN)
    print("done")


main()
