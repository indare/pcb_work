"""ST7796S on MeasurementADC (Waveshare 29318).

SCK/MOSI は初号ジャンパで GP18/GP19（SPI0）。ヘッダの GP3/GP4 は入力のまま。
GP9（SCKI プローブ）と GP15（ADC_nRST）は触らない。
"""
import framebuf
import time
from machine import Pin, SPI

# MADCTL 0xE8 = MY|MX|MV|BGR。GP18/19 ジャンパ＋実機の置き方で確認した向き。
WIDTH = 480
HEIGHT = 320
MADCTL = b"\xE8"

RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
WHITE = 0xFFFF
BLACK = 0x0000
YELLOW = 0xFFE0
CYAN = 0x07FF
ORANGE = 0xFD20
NAVY = 0x0010


def _u16(c):
    return bytes((c >> 8, c & 0xFF))


class Lcd:
    def __init__(self):
        self.en = Pin(8, Pin.OUT, value=1)
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(6, Pin.OUT, value=1)
        self.rst = Pin(7, Pin.OUT, value=1)
        Pin(3, Pin.IN)
        Pin(4, Pin.IN)
        self.spi = SPI(
            0,
            baudrate=20_000_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(19),
            miso=Pin(16),
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
        self._cmd(0x36, MADCTL)
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
        if w <= 0 or h <= 0:
            return
        self.window(x, y, x + w - 1, y + h - 1)
        pix = _u16(color)
        row = pix * w
        block_h = 32 if h >= 32 else h
        block = row * block_h
        self.dc(1)
        self.cs(0)
        n, rem = divmod(h, block_h)
        for _ in range(n):
            self.spi.write(block)
        if rem:
            self.spi.write(row * rem)
        self.cs(1)

    def fill(self, color):
        self.fill_rect(0, 0, WIDTH, HEIGHT, color)

    def text(self, s, x, y, color, bg=BLACK):
        w = len(s) * 8
        if w <= 0:
            return
        buf = bytearray(w * 8 * 2)
        fb = framebuf.FrameBuffer(buf, w, 8, framebuf.RGB565)
        fb.fill(bg)
        fb.text(s, 0, 0, color)
        self.window(x, y, x + w - 1, y + 7)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
