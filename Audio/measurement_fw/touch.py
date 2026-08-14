"""FT6336U（Waveshare 29318）。I2C1 = GP10/GP11、RST=GP13、INT=GP12。"""
from machine import Pin, I2C
import time

ADDR = 0x38


class Touch:
    def __init__(self):
        self.rst = Pin(13, Pin.OUT, value=1)
        self.irq = Pin(12, Pin.IN, Pin.PULL_UP)
        self.i2c = I2C(1, scl=Pin(11), sda=Pin(10), freq=400_000)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(80)
        found = self.i2c.scan()
        self.ok = ADDR in found
        self._down = False
        print("i2c", found, "ft6336", self.ok)

    def read(self):
        """押し下がりの瞬間だけ (disp_x, disp_y, raw_x, raw_y)。それ以外は None。"""
        if not self.ok:
            return None
        try:
            buf = self.i2c.readfrom_mem(ADDR, 0x02, 5)
        except OSError:
            return None
        n = buf[0] & 0x0F
        if n == 0 or n > 2:
            self._down = False
            return None
        tx = ((buf[1] & 0x0F) << 8) | buf[2]
        ty = ((buf[3] & 0x0F) << 8) | buf[4]
        # パネル素の 320×480 → MADCTL 0xE8 の 480×320。
        # 実測: ty が横（左=大）、tx が縦（上=小、下≈319）。
        x = 479 - ty
        y = tx
        if x < 0:
            x = 0
        elif x > 479:
            x = 479
        if y < 0:
            y = 0
        elif y > 319:
            y = 319
        if self._down:
            return None
        self._down = True
        return x, y, tx, ty
