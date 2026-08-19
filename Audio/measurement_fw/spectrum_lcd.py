"""スペアナ UI（既定は 1/3 oct 30 本・白パレット）。

縦グリッド付きの棒。下端メニューはタッチで切替。
レンジ / L+R / 色 / 30|H20|15 / ピークホールド。
"""
import math
import time

from lcd import Lcd, BLACK, GREEN, YELLOW, RED, WHITE, CYAN, ORANGE, WIDTH, HEIGHT

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

GEQ15 = (
    25.0, 40.0, 63.0, 100.0, 160.0, 250.0, 400.0, 630.0,
    1000.0, 1600.0, 2500.0, 4000.0, 6300.0, 10000.0, 16000.0,
)
LABELS15 = (
    "25", "", "63", "", "160", "", "400", "",
    "1k", "", "2.5k", "", "6.3k", "", "16k",
)

GEQ30 = (
    25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 125.0, 160.0, 200.0,
    250.0, 315.0, 400.0, 500.0, 630.0, 800.0, 1000.0, 1250.0, 1600.0, 2000.0,
    2500.0, 3150.0, 4000.0, 5000.0, 6300.0, 8000.0, 10000.0, 12500.0, 16000.0, 20000.0,
)
# 30 本は全部は書けないので代表だけ
LABELS30 = (
    "", "31", "", "", "63", "", "", "125", "", "",
    "250", "", "", "500", "", "", "1k", "", "", "2k",
    "", "", "4k", "", "", "8k", "", "", "16k", "",
)

# 低域は 1/1 oct（40〜500 Hz）、800 Hz 以上は 1/3 oct。
# 1/3 oct の 25 Hz は帯域幅 5.8 Hz しかなく応答が 170ms 級になる。1/1 oct なら
# 40 Hz でも 28 Hz 幅（約 35ms）で追従する。IIR は 40〜125 Hz の 3 本だけ。
HYBRID20 = (
    40.0, 63.0, 125.0, 250.0, 500.0,
    800.0, 1000.0, 1250.0, 1600.0, 2000.0, 2500.0, 3150.0,
    4000.0, 5000.0, 6300.0, 8000.0, 10000.0, 12500.0, 16000.0, 20000.0,
)
HYBRID20_WIDTHS = (1.0,) * 5 + (1.0 / 3.0,) * 15
LABELS20 = (
    "40", "63", "125", "250", "500", "800", "", "", "2k", "",
    "", "4k", "", "", "8k", "", "", "16k", "", "",
)

# centers, octaves（固定値またはバンド別 tuple）, menu label, bar labels, bar_w
# 既定は 30（1/3 oct）。H20 は低域を 1 oct にした応答重視モード。
BAND_MODES = (
    (GEQ30, 1.0 / 3.0, "30", LABELS30, 12),
    (HYBRID20, HYBRID20_WIDTHS, "H20", LABELS20, 18),
    (GEQ15, 2.0 / 3.0, "15", LABELS15, 22),
)

GRID = 0x7BEF
VGRID = 0x2104
HGRID = 0x3186
MENU_BG = 0x1082
MENU_N = 5

RANGES = (
    (-48.0, -12.0, "-48"),
    (-60.0, -18.0, "-60"),
    (-72.0, -18.0, "-72"),
    (-90.0, 0.0, "-90"),
)
CH_LAB = ("L+R", "L", "R")
PALETTES = (
    ((WHITE, WHITE, WHITE), "WHT"),
    ((GREEN, YELLOW, RED), "GYR"),
    ((CYAN, 0x001F, WHITE), "CYN"),
    ((ORANGE, YELLOW, RED), "AMB"),
)


def _db_step(lo, hi):
    """表示レンジに合わせて目盛間隔を選ぶ。"""
    span = hi - lo
    for step in (6.0, 12.0, 18.0, 24.0):
        if span / step <= 5.0:
            return step
    return 30.0


def _db_grid(ui, floor):
    """(y, db) のリスト。床と天井は線を引かない。中間は最大 2 本。"""
    lo = ui.db_lo()
    hi = ui.db_hi()
    step = _db_step(lo, hi)
    out = []
    db = lo + step
    while db < hi - 0.5:
        h = 2 + int((db - lo) / (hi - lo) * (MAX_H - 2))
        out.append((floor - h, db))
        db += step
    # 描き直しコストを抑えるため、多いときは端の 2 本だけ残す。
    # 既定 −60〜−18 なら −48/−36/−24 → −48/−24。
    if len(out) > 2:
        out = [out[0], out[-1]]
    return out




class Layout:
    def __init__(self, n, bar_w):
        self.n = n
        self.bar_w = bar_w
        self.slot = WIDTH // n
        self.x0 = (WIDTH - n * self.slot) // 2

    def bar_x(self, i):
        return self.x0 + i * self.slot + (self.slot - self.bar_w) // 2


class Ui:
    def __init__(self):
        self.ri = 1
        self.ci = 0
        self.pi = 0
        self.bi = 0
        self.peak = False

    def db_lo(self):
        return RANGES[self.ri][0]

    def db_hi(self):
        return RANGES[self.ri][1]

    def pal(self):
        return PALETTES[self.pi][0]

    def band_mode(self):
        return BAND_MODES[self.bi]

    def layout(self):
        centers, _oct, _lab, _labs, bar_w = self.band_mode()
        return Layout(len(centers), bar_w)

    def tap(self, x, y):
        if y < MENU_Y:
            return False, False
        slot = x // (WIDTH // MENU_N)
        band_changed = False
        if slot == 0:
            self.ri = (self.ri + 1) % len(RANGES)
        elif slot == 1:
            self.ci = (self.ci + 1) % 3
        elif slot == 2:
            self.pi = (self.pi + 1) % len(PALETTES)
        elif slot == 3:
            self.bi = (self.bi + 1) % len(BAND_MODES)
            band_changed = True
        else:
            self.peak = not self.peak
        return True, band_changed


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
    def __init__(self, lcd, ui, floor_y, layout):
        self.lcd = lcd
        self.ui = ui
        self.floor = floor_y
        self.layout = layout
        # 目盛の y は毎フレーム引き直すので、ここで確定させておく。
        # レンジやバンドを変えると Bars ごと作り直されるので取り違えない。
        self.grid_y = tuple(y for y, _db in _db_grid(ui, floor_y))
        n = layout.n
        self.h = [0] * n
        self.col = [BG] * n
        self.peak = [0] * n
        self.hold = [0] * n

    def _hgrid(self, x, w, y0, h):
        """棒を消した矩形に重なる横目盛だけ描き直す。"""
        y1 = y0 + h
        for y in self.grid_y:
            if y0 <= y < y1:
                self.lcd.fill_rect(x, y, w, 1, HGRID)

    def set(self, i, db):
        h = _h_of(self.ui, db)
        col = _color(self.ui, db)
        lay = self.layout
        x = lay.bar_x(i)
        bw = lay.bar_w
        old_h = self.h[i]
        gx = x + bw // 2
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
                self.lcd.fill_rect(x, self.floor - old_p, bw, PEAK_H, BG)
                self.lcd.fill_rect(gx, self.floor - old_p, 1, PEAK_H, VGRID)
                self._hgrid(x, bw, self.floor - old_p, PEAK_H)
        else:
            p = 0
            self.peak[i] = 0

        if h < old_h:
            self.lcd.fill_rect(x, self.floor - old_h, bw, old_h - h, BG)
            self.lcd.fill_rect(gx, self.floor - old_h, 1, old_h - h, VGRID)
            self._hgrid(x, bw, self.floor - old_h, old_h - h)
        elif h > old_h:
            self.lcd.fill_rect(x, self.floor - h, bw, h - old_h, col)
        if col != self.col[i] and h > 0:
            self.lcd.fill_rect(x, self.floor - h, bw, h, col)

        if use_pk and p > 0:
            self.lcd.fill_rect(x, self.floor - p, bw, PEAK_H, WHITE)

        self.h[i] = h
        self.col[i] = col


def _mock_pair(t_ms, n):
    t = t_ms * 0.001
    left = []
    right = []
    for i in range(n):
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
        ui.band_mode()[2],
        "PK" if ui.peak else "--",
    )
    slot = WIDTH // MENU_N
    for i, lab in enumerate(labs):
        tx = i * slot + (slot - len(lab) * 8) // 2
        lcd.text(lab, tx, MENU_Y + 6, WHITE, MENU_BG)


def _draw_db_grid(lcd, ui, floor, top_y):
    """横目盛と右端の dB ラベル。"""
    for y, db in _db_grid(ui, floor):
        if y < top_y:
            continue
        lcd.fill_rect(0, y, WIDTH, 1, HGRID)
        lab = "%d" % int(db)
        tx = WIDTH - len(lab) * 8
        lcd.text(lab, tx, y - 4, GRID, BG)


def _draw_static(lcd, ui, layout):
    lcd.fill(BG)
    lcd.fill_rect(0, DIV_Y, WIDTH, 3, WHITE)
    lcd.text("L", 0, 2, CYAN, BG)
    lcd.text("R", 0, DIV_Y + 6, YELLOW, BG)
    labels = ui.band_mode()[3]
    for i, lab in enumerate(labels):
        x = layout.bar_x(i) + layout.bar_w // 2
        lcd.fill_rect(x, 8, 1, L_FLOOR - 8, VGRID)
        lcd.fill_rect(x, DIV_Y + 8, 1, R_FLOOR - DIV_Y - 8, VGRID)
        lcd.fill_rect(x - 2, L_FLOOR, 5, 1, GRID)
        lcd.fill_rect(x - 2, R_FLOOR, 5, 1, GRID)
        if not lab:
            continue
        tx = x - len(lab) * 4
        if tx < 0:
            tx = 0
        if tx + len(lab) * 8 > WIDTH:
            tx = WIDTH - len(lab) * 8
        lcd.text(lab, tx, L_LABEL_Y, GRID, BG)
        lcd.text(lab, tx, R_LABEL_Y, GRID, BG)
    _draw_db_grid(lcd, ui, L_FLOOR, 8)
    _draw_db_grid(lcd, ui, R_FLOOR, DIV_Y + 8)
    _draw_menu(lcd, ui)


def _apply_band_mode(an, ui):
    import gc
    centers, octaves, lab, _labels, _bw = ui.band_mode()
    if an is not None:
        gc.collect()
        an.set_centers(centers, octaves)
        print("bands", lab, "n", len(centers), "iir", an._iir_n, "free", gc.mem_free())
    return ui.layout()


def main():
    print("lcd")
    lcd = Lcd()
    ui = Ui()
    layout = ui.layout()
    _draw_static(lcd, ui, layout)
    left_bars = Bars(lcd, ui, L_FLOOR, layout)
    right_bars = Bars(lcd, ui, R_FLOOR, layout)

    tp = None
    try:
        from touch import Touch
        tp = Touch()
    except Exception as e:
        print("touch fail", e)

    an = None
    try:
        from spectrum import SpectrumAnalyzer
        centers, octaves, lab, _labels, _bw = ui.band_mode()
        an = SpectrumAnalyzer(n=1024, centers=centers, octaves=octaves)
        an.reset_adc()
        print("adc live bands", lab, "iir", an._iir_n, "fft", an.fft_backend)
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
                changed, band_changed = ui.tap(x, y)
                if changed:
                    try:
                        if band_changed:
                            layout = _apply_band_mode(an, ui)
                        else:
                            layout = ui.layout()
                        _draw_static(lcd, ui, layout)
                        left_bars = Bars(lcd, ui, L_FLOOR, layout)
                        right_bars = Bars(lcd, ui, R_FLOOR, layout)
                    except Exception as e:
                        print("ui fail", e)
                        import gc
                        gc.collect()
                        layout = ui.layout()
                        _draw_static(lcd, ui, layout)
                        left_bars = Bars(lcd, ui, L_FLOOR, layout)
                        right_bars = Bars(lcd, ui, R_FLOOR, layout)
        try:
            nb = layout.n
            lb, rb = _live_pair(an) if an else _mock_pair(time.ticks_ms(), nb)
            if len(lb) != nb or len(rb) != nb:
                raise ValueError("bands %d/%d want %d" % (len(lb), len(rb), nb))
            for i in range(nb):
                if ui.ci != 2:
                    left_bars.set(i, lb[i])
                if ui.ci != 1:
                    right_bars.set(i, rb[i])
        except Exception as e:
            print("live fail", e)
            an = None
            lb, rb = _mock_pair(time.ticks_ms(), layout.n)
            for i in range(layout.n):
                if ui.ci != 2:
                    left_bars.set(i, lb[i])
                if ui.ci != 1:
                    right_bars.set(i, rb[i])
        n += 1
        if n % 5 == 0:
            dt = time.ticks_diff(time.ticks_ms(), t0)
            fps = (5000.0 / dt) if dt else 0.0
            t0 = time.ticks_ms()
            print("fps", round(fps, 2), "bands", layout.n,
                  "L", [round(v, 1) for v in lb[: min(6, len(lb))]])


if __name__ == "__main__":
    main()
