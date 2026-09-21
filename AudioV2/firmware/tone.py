"""PT2314E — Bass / Treble（I²C）。音量は手回しポットなので触らない。"""

try:
    from machine import I2C
except ImportError:
    I2C = None

# 7-bit。図の正に合わせる（未実測ならスキャンで確認）。
PT2314_ADDR = 0x44


class Tone:
    def __init__(self, i2c, addr=PT2314_ADDR):
        self.i2c = i2c
        self.addr = addr
        self.bass = 0  # 表示用 -14..+14 相当の整数（実装で DS に合わせる）
        self.treble = 0

    def present(self):
        try:
            self.i2c.writeto(self.addr, b"")
            return True
        except OSError:
            return False

    def nudge_bass(self, delta):
        self.bass = max(-14, min(14, self.bass + delta))
        self._apply()

    def nudge_treble(self, delta):
        self.treble = max(-14, min(14, self.treble + delta))
        self._apply()

    def _apply(self):
        # TODO: DS の Bass/Treble コマンドバイトを書く
        pass
