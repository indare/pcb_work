"""LCD 状態バー — CH / DEST / Bass / Treble。

スペアナ本体は後で同画面に載せる。操作は ENC（ここは描画だけ）。
"""

try:
    import lcd_st7796 as lcd_mod
except ImportError:
    try:
        from vendor import lcd_st7796 as lcd_mod
    except ImportError:
        lcd_mod = None


class StatusUi:
    def __init__(self, lcd=None):
        if lcd is not None:
            self.lcd = lcd
        elif lcd_mod is not None:
            self.lcd = lcd_mod.Lcd()
        else:
            self.lcd = None
        self._last = None

    def show(self, *, ch, dest, bass, treble, backend):
        key = (ch, dest, bass, treble, backend)
        if key == self._last:
            return
        self._last = key
        line = "CH%d  %s  B%+d  T%+d  [%s]" % (
            ch, dest, bass, treble, backend)
        if self.lcd is None:
            print(line)
            return
        # 上端ステータス帯だけ塗る（全画面は触らない）
        self.lcd.fill_rect(0, 0, lcd_mod.WIDTH, 24, lcd_mod.NAVY)
        self.lcd.text(line, 4, 6, lcd_mod.WHITE, lcd_mod.NAVY)
