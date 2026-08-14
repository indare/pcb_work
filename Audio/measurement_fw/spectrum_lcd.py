"""10 バンド試作スペアナ（オクターブ）。

縦グリッド付きの棒。下端メニューはタッチで切替。
レンジ / L+R / 色 / ピークホールド。
"""
import math
import time

from lcd import Lcd, BLACK, GREEN, YELLOW, RED, WHITE, CYAN, ORANGE, WIDTH, HEIGHT

N = 10
SLOT = WIDTH // N
BAR_W = 26
X0 = (WIDTH - N * SLOT) // 2
MAX_H = 108
BG = BLACK
PEAK_H = 2
PEAK_HOLD_MS = 500
PEAK_FALL = 2

L_FLOOR = 118
L_LABEL_Y = 124
DIV_Y = 156
R_FLOOR = 278
R_LABEL_Y = 284
MENU_Y = 300

GEQ10 = (31.5, 63.0, 125.0, 250.0, 500.0,
         1000.0, 2000.0, 4000.0, 8000.0, 16000.0)
LABELS = ("", "62", "", "250", "", "1k", "", "4k", "", "16k")
GRID = 0x7BEF
VGRID = 0x2104
MENU_BG = 0x1082

RANGES = (
    (-48.0, -12.0, "-48"),
    (-60.0, -18.0, "-60"),
    (-72.0, -18.0, "-72"),
    (-90.0, 0.0, "-90"),
)
CH_LAB = ("L+R", "L", "R")
PALETTES = (
    ((GREEN, YELLOW, RED), "GYR"),
    ((CYAN, 0x001F, WHITE), "CYN"),
    ((WHITE, WHITE, WHITE), "WHT"),
    ((ORANGE, YELLOW, RED), "AMB"),
)


class Ui:
    def __init__(self):
        self.ri = 1
        self.ci = 0
        self.pi = 0
        self.peak = False

    def db_lo(self):
        return RANGES[self.ri][0]

    def db_hi(self):
        return RANGES[self.ri][1]

    def pal(self):
        return PALETTES[self.pi][0]

    def tap(self, x, y):
        if y < MENU_Y:
            return False
        slot = x // (WIDTH // 4)
        if slot == 0:
            self.ri = (self.ri + 1) % len(RANGES)
        elif slot == 1:
            self.ci = (self.ci + 1) % 3
        elif slot == 2:
            self.pi = (self.pi + 1) % len(PALETTES)
        else:
            self.peak = not self.peak
        return True


def _bar_x(i):
    return X0 + i * SLOT + (SLOT - BAR_W) // 2


def _h_of(ui, db):
    lo = ui.db_lo()
    hi = ui.db_hi()
    if db <= lo:
        return 2
    if db >= hi:
        return MAX_H
    return 2 + int((db - lo) / (hi - lo) * (MAX_H - 2))


def _color(ui, db):
    lo, mid, hi = ui.pal()
    if db < -36.0:
        return lo
    if db < -18.0:
        return mid
    return hi


class Bars:
    def __init__(self, lcd, ui, floor_y):
        self.lcd = lcd
        self.ui = ui
        self.floor = floor_y
        self.h = [0] * N
        self.col = [BG] * N
        self.peak = [0] * N
        self.hold = [0] * N

    def set(self, i, db):
        h = _h_of(self.ui, db)
        col = _color(self.ui, db)
        x = _bar_x(i)
        old_h = self.h[i]
        gx = x + BAR_W // 2
        use_pk = self.ui.peak
        now = time.ticks_ms()
        old_p = self.peak[i]

        if use_pk:
            if h >= self.peak[i]:
                self.peak[i] = h
                self.hold[i] = now
            elif time.ticks_diff(now, self.hold[i]) > PEAK_HOLD_MS:
                nxt = self.peak[i] - PEAK_FALL
                self.peak[i] = h if nxt < h else nxt
            p = self.peak[i]
            if old_p > 0 and old_p != p and old_p > h:
                self.lcd.fill_rect(x, self.floor - old_p, BAR_W, PEAK_H, BG)
                self.lcd.fill_rect(gx, self.floor - old_p, 1, PEAK_H, VGRID)
        else:
            p = 0
            self.peak[i] = 0

        if h < old_h:
            self.lcd.fill_rect(x, self.floor - old_h, BAR_W, old_h - h, BG)
            self.lcd.fill_rect(gx, self.floor - old_h, 1, old_h - h, VGRID)
        elif h > old_h:
            self.lcd.fill_rect(x, self.floor - h, BAR_W, h - old_h, col)
        if col != self.col[i] and h > 0:
            self.lcd.fill_rect(x, self.floor - h, BAR_W, h, col)

        if use_pk and p > 0:
            self.lcd.fill_rect(x, self.floor - p, BAR_W, PEAK_H, WHITE)

        self.h[i] = h
        self.col[i] = col


def _mock_pair(t_ms):
    t = t_ms * 0.001
    left = []
    right = []
    for i in range(N):
        left.append(-55.0 + 28.0 * math.sin(t * 1.7 + i * 0.45) + 8.0 * math.sin(t * 3.1 + i))
        right.append(-58.0 + 26.0 * math.sin(t * 1.4 + i * 0.5 + 1.1) + 7.0 * math.sin(t * 2.6 + i))
    return left, right


def _live_pair(an):
    (lb, _, _), (rb, _, _) = an.frame()
    return lb, rb


def _draw_menu(lcd, ui):
    lcd.fill_rect(0, MENU_Y, WIDTH, HEIGHT - MENU_Y, MENU_BG)
    labs = (
        RANGES[ui.ri][2],
        CH_LAB[ui.ci],
        PALETTES[ui.pi][1],
        "PK" if ui.peak else "--",
    )
    slot = WIDTH // 4
    for i, lab in enumerate(labs):
        tx = i * slot + (slot - len(lab) * 8) // 2
        lcd.text(lab, tx, MENU_Y + 6, WHITE, MENU_BG)


def _draw_static(lcd, ui):
    lcd.fill(BG)
    lcd.fill_rect(0, DIV_Y, WIDTH, 3, WHITE)
    lcd.text("L", 0, 2, CYAN, BG)
    lcd.text("R", 0, DIV_Y + 6, YELLOW, BG)
    for i, lab in enumerate(LABELS):
        x = _bar_x(i) + BAR_W // 2
        lcd.fill_rect(x, 8, 1, L_FLOOR - 8, VGRID)
        lcd.fill_rect(x, DIV_Y + 8, 1, R_FLOOR - DIV_Y - 8, VGRID)
        lcd.fill_rect(x - 2, L_FLOOR, 5, 1, GRID)
        lcd.fill_rect(x - 2, R_FLOOR, 5, 1, GRID)
        if not lab:
            continue
        tx = x - len(lab) * 4
        if tx < 0:
            tx = 0
        lcd.text(lab, tx, L_LABEL_Y, GRID, BG)
        lcd.text(lab, tx, R_LABEL_Y, GRID, BG)
    _draw_menu(lcd, ui)


def main():
    print("lcd")
    lcd = Lcd()
    ui = Ui()
    _draw_static(lcd, ui)
    left_bars = Bars(lcd, ui, L_FLOOR)
    right_bars = Bars(lcd, ui, R_FLOOR)

    tp = None
    try:
        from touch import Touch
        tp = Touch()
    except Exception as e:
        print("touch fail", e)

    an = None
    try:
        from spectrum import SpectrumAnalyzer
        an = SpectrumAnalyzer(n=1024, centers=GEQ10)
        an.reset_adc()
        print("adc live iir", an._iir_n)
    except Exception as e:
        print("mock", e)

    n = 0
    t0 = time.ticks_ms()
    while True:
        if tp is not None:
            hit = tp.read()
            if hit is not None:
                x, y, tx, ty = hit
                print("tap", x, y, "raw", tx, ty)
                if ui.tap(x, y):
                    _draw_static(lcd, ui)
                    left_bars = Bars(lcd, ui, L_FLOOR)
                    right_bars = Bars(lcd, ui, R_FLOOR)
        try:
            lb, rb = _live_pair(an) if an else _mock_pair(time.ticks_ms())
        except Exception as e:
            print("live fail", e)
            an = None
            lb, rb = _mock_pair(time.ticks_ms())
        for i in range(N):
            if ui.ci != 2:
                left_bars.set(i, lb[i])
            if ui.ci != 1:
                right_bars.set(i, rb[i])
        n += 1
        if n % 5 == 0:
            dt = time.ticks_diff(time.ticks_ms(), t0)
            fps = (5000.0 / dt) if dt else 0.0
            t0 = time.ticks_ms()
            print("fps", round(fps, 2), "L", [round(v, 1) for v in lb])


if __name__ == "__main__":
    main()
