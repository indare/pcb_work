"""FrontPanel MCP23017 — ENC×3 と DEST LED。

操作は ENC のみ（タッチで切替しない）。INTA/INTB で起こして GPIO を読む。
ピン割当の正は FrontPanel の U1610 ネット。
"""

try:
    from machine import I2C, Pin
except ImportError:  # host syntax check
    I2C = Pin = None

import board

# MCP23017 レジスタ（BANK=0）
IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13
GPPUA = 0x0C
GPPUB = 0x0D
GPINTENA = 0x04
GPINTENB = 0x05
INTCONA = 0x08
INTCONB = 0x09
IOCON = 0x0A

# U1610: GPA0=ENC3_SW, GPA1=LED_DEST2, GPA2=LED_DEST1
#         GPB0..7 = ENC1_A/B/SW, ENC2_A/B/SW, ENC3_A/B
ENC_CH = 0
ENC_BASS = 1
ENC_TREBLE = 2


class UiMcp:
    def __init__(self, i2c, addr=board.MCP_UI_ADDR):
        self.i2c = i2c
        self.addr = addr
        self._inta = Pin(board.ENC_INTA, Pin.IN, Pin.PULL_UP)
        self._intb = Pin(board.ENC_INTB, Pin.IN, Pin.PULL_UP)
        self._setup()

    def _w(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes((val,)))

    def _r(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _setup(self):
        # A: bit0 ENC3_SW in, bit1-2 LED out, rest in
        self._w(IODIRA, 0b11111001)
        self._w(IODIRB, 0xFF)
        self._w(GPPUA, 0b11111001)
        self._w(GPPUB, 0xFF)
        # 変化で INT（両ポート）
        self._w(GPINTENA, 0b11111001)
        self._w(GPINTENB, 0xFF)
        self._w(INTCONA, 0x00)
        self._w(INTCONB, 0x00)
        self._w(IOCON, 0x00)
        self.set_dest_leds(False, False)

    def raw(self):
        return self._r(GPIOA), self._r(GPIOB)

    def set_dest_leds(self, phone, line):
        a = self._r(GPIOA)
        a = (a & ~0b00000110) | ((1 if line else 0) << 1) | ((1 if phone else 0) << 2)
        self._w(GPIOA, a)

    def irq_pending(self):
        return (self._inta.value() == 0) or (self._intb.value() == 0)


def open_bus():
    return I2C(board.I2C_ID, sda=Pin(board.I2C_SDA), scl=Pin(board.I2C_SCL),
               freq=board.I2C_FREQ_HZ)
