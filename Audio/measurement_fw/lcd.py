"""ST7796S on MeasurementADC (Waveshare 29318).

SCK/MOSI は初号ジャンパで GP18/GP19（SPI0）。ヘッダの GP3/GP4 は入力のまま。
GP9（SCKI プローブ）と GP15（ADC_nMR。TPS3307 の ~MR、H は駆動しない）は触らない。
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

# スペアナ棒幅など、よく使う幅の 1 行バッファを先に持てるようにする。
_COMMON_WIDTHS = (1, 5, 8, 12, 18, 22, 32)

# 塗りバッファのキャッシュ上限。ここが太ると I2S / FFT の確保が MemoryError になる。
# 全画面塗りの 1 塊だけで 480*32*2 = 30720 byte あるので、大物は使い捨てる。
_CACHE_BUDGET = 24576
_CACHE_MAX_ENTRY = 8192
# 1 回の SPI 転送で作る塗り塊の上限。棒（幅 12〜22）は 1 回で収まる。
_MAX_BLOCK_BYTES = 4096


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
            baudrate=40_000_000,
            polarity=0,
            phase=0,
            sck=Pin(18),
            mosi=Pin(19),
            miso=Pin(16),
        )
        # color -> 2byte, (color, w) -> 1 行 bytes。fill_rect の毎回生成を避ける。
        self._pix = {}
        self._row = {}
        self._row_bytes = 0
        self._cmd1 = bytearray(1)
        self._cas = bytearray(4)
        self._ras = bytearray(4)
        self._init()

    def _pix_of(self, color):
        pix = self._pix.get(color)
        if pix is None:
            pix = _u16(color)
            self._pix[color] = pix
        return pix

    def _cache_put(self, key, buf):
        n = len(buf)
        if n > _CACHE_MAX_ENTRY:
            return
        if self._row_bytes + n > _CACHE_BUDGET:
            self._row.clear()
            self._row_bytes = 0
        self._row[key] = buf
        self._row_bytes += n

    def _row_of(self, color, w):
        key = (color, w)
        row = self._row.get(key)
        if row is None:
            row = self._pix_of(color) * w
            self._cache_put(key, row)
        return row

    def _cmd(self, c, data=b""):
        cmd = self._cmd1
        cmd[0] = c
        self.dc(0)
        self.cs(0)
        self.spi.write(cmd)
        if data:
            self.dc(1)
            self.spi.write(data if isinstance(data, (bytes, bytearray)) else bytes(data))
        self.cs(1)

    def _block_of(self, color, w, h):
        """高さ h の塗りつぶしバッファ。h=1 は 1 行そのもの。"""
        if h <= 1:
            return self._row_of(color, w)
        bkey = (color, w, h)
        block = self._row.get(bkey)
        if block is None:
            block = self._row_of(color, w) * h
            self._cache_put(bkey, block)
        return block

    def _begin_window(self, x0, y0, x1, y1):
        """CS を下げたまま CASET/RASET/RAMWR。呼び出し側が画素を書いて cs(1)。"""
        cas = self._cas
        ras = self._ras
        cmd = self._cmd1
        cas[0] = x0 >> 8
        cas[1] = x0 & 0xFF
        cas[2] = x1 >> 8
        cas[3] = x1 & 0xFF
        ras[0] = y0 >> 8
        ras[1] = y0 & 0xFF
        ras[2] = y1 >> 8
        ras[3] = y1 & 0xFF
        spi = self.spi
        dc = self.dc
        self.cs(0)
        dc(0)
        cmd[0] = 0x2A
        spi.write(cmd)
        dc(1)
        spi.write(cas)
        dc(0)
        cmd[0] = 0x2B
        spi.write(cmd)
        dc(1)
        spi.write(ras)
        dc(0)
        cmd[0] = 0x2C
        spi.write(cmd)
        dc(1)

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
        # 棒描画で使う幅を温めておく
        for w in _COMMON_WIDTHS:
            self._row_of(BLACK, w)
            self._row_of(WHITE, w)

    def window(self, x0, y0, x1, y1):
        self._begin_window(x0, y0, x1, y1)
        self.cs(1)

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        self._begin_window(x, y, x + w - 1, y + h - 1)
        write = self.spi.write
        # 一度に作る塊を byte で縛る。全画面塗りの 30KB 一時確保が
        # 解析用の RAM とぶつかって MemoryError になっていた。
        rows = _MAX_BLOCK_BYTES // (w * 2)
        if rows < 1:
            rows = 1
        if h <= rows:
            write(self._block_of(color, w, h))
        else:
            block = self._block_of(color, w, rows)
            n, rem = divmod(h, rows)
            for _ in range(n):
                write(block)
            if rem:
                write(self._block_of(color, w, rem))
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
        self._begin_window(x, y, x + w - 1, y + 7)
        self.spi.write(buf)
        self.cs(1)
