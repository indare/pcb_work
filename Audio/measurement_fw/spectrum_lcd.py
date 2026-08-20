"""スペアナ UI（既定は 1/3 oct 30 本・白パレット）。

縦・横目盛はガター（棒の隙間）に静的描画。棒更新時は復元しない。
下端メニューはタッチで切替。レンジ / L+R / 色 / 30|20|15 / 1k|2k / ピークホールド。
"""
import time

from lcd import Lcd, BLACK, GREEN, YELLOW, RED, WHITE, CYAN, ORANGE, WIDTH, HEIGHT

try:
    import _thread
except ImportError:
    _thread = None

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
# 既定は 30（1/3 oct）。20 は低域を 1 oct にした応答重視モード。
BAND_MODES = (
    (GEQ30, 1.0 / 3.0, "30", LABELS30, 12),
    (HYBRID20, HYBRID20_WIDTHS, "20", LABELS20, 18),
    (GEQ15, 2.0 / 3.0, "15", LABELS15, 22),
)

GRID = 0x7BEF
VGRID = 0x2104
HGRID = 0x3186
MENU_BG = 0x1082
MENU_N = 6

# 解析が落ちたあと作り直すまでの待ち。
RETRY_MS = 2000

# FFT 点数。2k は低域分解能が良いが取り込みが約 43ms になり fps が落ちる。
FFT_SIZES = (1024, 2048)
FFT_LABS = ("1k", "2k")

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
        self.ni = 0
        self.peak = False

    def db_lo(self):
        return RANGES[self.ri][0]

    def db_hi(self):
        return RANGES[self.ri][1]

    def pal(self):
        return PALETTES[self.pi][0]

    def band_mode(self):
        return BAND_MODES[self.bi]

    def fft_n(self):
        return FFT_SIZES[self.ni]

    def layout(self):
        centers, _oct, _lab, _labs, bar_w = self.band_mode()
        return Layout(len(centers), bar_w)

    def tap(self, x, y):
        if y < MENU_Y:
            return False, False, False
        slot = x // (WIDTH // MENU_N)
        band_changed = False
        n_changed = False
        if slot == 0:
            self.ri = (self.ri + 1) % len(RANGES)
        elif slot == 1:
            self.ci = (self.ci + 1) % 3
        elif slot == 2:
            self.pi = (self.pi + 1) % len(PALETTES)
        elif slot == 3:
            self.bi = (self.bi + 1) % len(BAND_MODES)
            band_changed = True
        elif slot == 4:
            self.ni = (self.ni + 1) % len(FFT_SIZES)
            n_changed = True
        else:
            self.peak = not self.peak
        return True, band_changed, n_changed


def _h_of(ui, db):
    lo = ui.db_lo()
    hi = ui.db_hi()
    if db <= lo:
        return 2
    if db >= hi:
        return MAX_H
    # 1px ジッタで fill_rect が走らないよう偶数に揃える。MAX_H も偶数。
    h = 2 + int((db - lo) / (hi - lo) * (MAX_H - 2))
    return h - (h & 1)


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
        n = layout.n
        # 棒座標は固定。毎フレーム bar_x を計算しない。
        self.xs = [layout.bar_x(i) for i in range(n)]
        self.bw = layout.bar_w
        self.h = [0] * n
        self.col = [BG] * n
        self.peak = [0] * n
        self.hold = [0] * n

    def set(self, i, db):
        h = _h_of(self.ui, db)
        col = _color(self.ui, db)
        old_h = self.h[i]
        use_pk = self.ui.peak
        old_p = self.peak[i]
        now = time.ticks_ms()

        if use_pk:
            if h >= self.peak[i]:
                self.peak[i] = h
                self.hold[i] = now
            elif time.ticks_diff(now, self.hold[i]) > PEAK_HOLD_MS:
                nxt = self.peak[i] - PEAK_FALL
                self.peak[i] = h if nxt < h else nxt
            p = self.peak[i]
        else:
            p = 0
            self.peak[i] = 0

        # 見た目が変わらないなら SPI しない。
        if h == old_h and col == self.col[i] and p == old_p:
            return

        x = self.xs[i]
        bw = self.bw

        if use_pk and old_p > 0 and old_p != p and old_p > h:
            # 目盛は棒の下に置いていないので、BG だけで足りる。
            self.lcd.fill_rect(x, self.floor - old_p, bw, PEAK_H, BG)

        if h < old_h:
            self.lcd.fill_rect(x, self.floor - old_h, bw, old_h - h, BG)
        elif h > old_h:
            self.lcd.fill_rect(x, self.floor - h, bw, h - old_h, col)
        if col != self.col[i] and h > 0:
            self.lcd.fill_rect(x, self.floor - h, bw, h, col)

        if use_pk and p > 0:
            self.lcd.fill_rect(x, self.floor - p, bw, PEAK_H, WHITE)

        self.h[i] = h
        self.col[i] = col


def _live_pair(an):
    (lb, _, _), (rb, _, _) = an.frame()
    return lb, rb


class BandWorker:
    """解析を第2コアで回し、最新の L/R バンドだけ渡す。

    Pico 2 の `_thread` はもう一方のコアで動く。LCD SPI は core0 のまま。
    """

    def __init__(self):
        self._lock = _thread.allocate_lock() if _thread is not None else None
        self._keep = True
        self._run = False
        self._idle = True
        self._started = False
        self._an = None
        self.lb = None
        self.rb = None
        self.gen = 0
        self.err = None

    def start(self, an):
        self._an = an
        self.err = None
        self._run = an is not None
        if _thread is None or an is None:
            return False
        if not self._started:
            _thread.start_new_thread(self._loop, ())
            self._started = True
            print("analyzer thread")
        return True

    def set_analyzer(self, an):
        self._an = an
        self.lb = None
        self.rb = None
        self.gen = 0
        self.err = None

    def pause(self):
        self._run = False
        if not self._started:
            self._idle = True
            return
        t0 = time.ticks_ms()
        while not self._idle:
            if time.ticks_diff(time.ticks_ms(), t0) > 800:
                break
            time.sleep_ms(2)

    def resume(self):
        if self._an is not None:
            self._run = True

    def snapshot(self):
        lock = self._lock
        if lock is None:
            return self.lb, self.rb, self.gen, self.err
        lock.acquire()
        try:
            return self.lb, self.rb, self.gen, self.err
        finally:
            lock.release()

    def _loop(self):
        while self._keep:
            if (not self._run) or self._an is None:
                self._idle = True
                time.sleep_ms(2)
                continue
            self._idle = False
            try:
                (lb, _, _), (rb, _, _) = self._an.frame()
            except Exception as e:
                lock = self._lock
                lock.acquire()
                self.err = e
                lock.release()
                self._run = False
                continue
            lock = self._lock
            lock.acquire()
            self.lb = lb
            self.rb = rb
            self.gen += 1
            self.err = None
            lock.release()


def _draw_menu(lcd, ui):
    lcd.fill_rect(0, MENU_Y, WIDTH, HEIGHT - MENU_Y, MENU_BG)
    labs = (
        RANGES[ui.ri][2],
        CH_LAB[ui.ci],
        PALETTES[ui.pi][1],
        ui.band_mode()[2],
        FFT_LABS[ui.ni],
        "PK" if ui.peak else "--",
    )
    slot = WIDTH // MENU_N
    for i, lab in enumerate(labs):
        tx = i * slot + (slot - len(lab) * 8) // 2
        lcd.text(lab, tx, MENU_Y + 6, WHITE, MENU_BG)


def _draw_hgrid_gutters(lcd, layout, y):
    """横目盛は棒の下を避け、スロット隙間と右端だけ描く。"""
    slot = layout.slot
    bw = layout.bar_w
    x0 = layout.x0
    for i in range(layout.n):
        slot_l = x0 + i * slot
        bx = slot_l + (slot - bw) // 2
        if bx > slot_l:
            lcd.fill_rect(slot_l, y, bx - slot_l, 1, HGRID)
        be = bx + bw
        slot_r = slot_l + slot
        if slot_r > be:
            lcd.fill_rect(be, y, slot_r - be, 1, HGRID)
    end = x0 + layout.n * slot
    if end < WIDTH:
        lcd.fill_rect(end, y, WIDTH - end, 1, HGRID)


def _draw_db_grid(lcd, ui, layout, floor, top_y):
    """横目盛（ガターのみ）と右端の dB ラベル。"""
    for y, db in _db_grid(ui, floor):
        if y < top_y:
            continue
        _draw_hgrid_gutters(lcd, layout, y)
        lab = "%d" % int(db)
        tx = WIDTH - len(lab) * 8
        lcd.text(lab, tx, y - 4, GRID, BG)


def _draw_static(lcd, ui, layout):
    lcd.fill(BG)
    lcd.fill_rect(0, DIV_Y, WIDTH, 3, WHITE)
    lcd.text("L", 0, 2, CYAN, BG)
    lcd.text("R", 0, DIV_Y + 6, YELLOW, BG)
    # 縦グリッドは棒中央ではなくスロット境界（ガター）に静的描画する。
    for i in range(1, layout.n):
        gx = layout.x0 + i * layout.slot
        lcd.fill_rect(gx, 8, 1, L_FLOOR - 8, VGRID)
        lcd.fill_rect(gx, DIV_Y + 8, 1, R_FLOOR - DIV_Y - 8, VGRID)
    labels = ui.band_mode()[3]
    for i, lab in enumerate(labels):
        x = layout.bar_x(i) + layout.bar_w // 2
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
    _draw_db_grid(lcd, ui, layout, L_FLOOR, 8)
    _draw_db_grid(lcd, ui, layout, R_FLOOR, DIV_Y + 8)
    _draw_menu(lcd, ui)


def _apply_band_mode(an, ui):
    import gc
    centers, octaves, lab, _labels, _bw = ui.band_mode()
    if an is not None:
        gc.collect()
        an.set_centers(centers, octaves)
        print("bands", lab, "n", len(centers), "fft_n", an.n,
              "iir", an._iir_n, "free", gc.mem_free())
    return ui.layout()


def _make_analyzer(ui):
    """2k 分の領域を一度確保する。1k/2k 切替は set_n で使い回す。"""
    import gc
    from spectrum import SpectrumAnalyzer
    gc.collect()
    gc.collect()
    centers, octaves, lab, _labels, _bw = ui.band_mode()
    n = ui.fft_n()
    an = SpectrumAnalyzer(n=n, max_n=max(FFT_SIZES),
                          centers=centers, octaves=octaves)
    an.reset_adc()
    print("adc live bands", lab, "cap", an.n, "fft_n", an._fft_n(),
          "iir", an._iir_n, "fft", an.fft_backend, "free", gc.mem_free())
    return an


def _drop_analyzer(worker, an):
    """ワーカーとローカルの参照を切ってから GC。2k 確保の前に必須。"""
    import gc
    worker.pause()
    worker.set_analyzer(None)
    if an is not None:
        try:
            an.close()
        except Exception:
            pass
        del an
    gc.collect()
    gc.collect()
    return None


def _rebuild_analyzer(worker, an, ui):
    _drop_analyzer(worker, an)
    return _make_analyzer(ui)


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

    worker = BandWorker()
    an = None
    use_worker = False
    retry_at = None
    try:
        an = _make_analyzer(ui)
        use_worker = worker.start(an)
    except Exception as e:
        print("analyzer fail", repr(e))
        retry_at = time.ticks_add(time.ticks_ms(), RETRY_MS)

    n = 0
    t0 = time.ticks_ms()
    last_gen = -1
    lb = rb = None
    while True:
        if an is None and retry_at is not None and \
                time.ticks_diff(time.ticks_ms(), retry_at) >= 0:
            retry_at = None
            try:
                an = _make_analyzer(ui)
                worker.set_analyzer(an)
                use_worker = worker.start(an)
                last_gen = -1
                print("analyzer back")
            except Exception as e:
                print("retry fail", repr(e))
                retry_at = time.ticks_add(time.ticks_ms(), RETRY_MS)
        if tp is not None:
            hit = tp.read()
            if hit is not None:
                x, y, tx, ty = hit
                print("tap", x, y, "raw", tx, ty)
                changed, band_changed, n_changed = ui.tap(x, y)
                if changed:
                    try:
                        worker.pause()
                        if n_changed:
                            if an is None:
                                an = _make_analyzer(ui)
                                worker.set_analyzer(an)
                                use_worker = worker.start(an)
                            else:
                                an.set_n(ui.fft_n())
                            layout = ui.layout()
                            print("cap", an.n, "fft_n", an._fft_n())
                        elif band_changed:
                            layout = _apply_band_mode(an, ui)
                        else:
                            layout = ui.layout()
                        last_gen = -1
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
                    worker.resume()
        try:
            nb = layout.n
            if use_worker:
                lb, rb, gen, err = worker.snapshot()
                if err is not None:
                    raise err
                if lb is None or gen == last_gen:
                    time.sleep_ms(1)
                    continue
                last_gen = gen
            elif an is not None:
                lb, rb = _live_pair(an)
            else:
                # 解析が無いときにモックを描くと、実測との区別がつかない。
                time.sleep_ms(20)
                continue
            if len(lb) != nb or len(rb) != nb:
                raise ValueError("bands %d/%d want %d" % (len(lb), len(rb), nb))
            for i in range(nb):
                if ui.ci != 2:
                    left_bars.set(i, lb[i])
                if ui.ci != 1:
                    right_bars.set(i, rb[i])
        except Exception as e:
            import sys
            print("live fail", repr(e))
            sys.print_exception(e)
            worker.pause()
            an = _drop_analyzer(worker, an)
            use_worker = False
            last_gen = -1
            retry_at = time.ticks_add(time.ticks_ms(), RETRY_MS)
            floor = ui.db_lo()
            for i in range(layout.n):
                if ui.ci != 2:
                    left_bars.set(i, floor)
                if ui.ci != 1:
                    right_bars.set(i, floor)
            continue
        n += 1
        if n % 15 == 0:
            dt = time.ticks_diff(time.ticks_ms(), t0)
            fps = (15000.0 / dt) if dt else 0.0
            t0 = time.ticks_ms()
            pk_l = 0
            pk_r = 0
            for i in range(1, len(lb)):
                if lb[i] > lb[pk_l]:
                    pk_l = i
                if rb[i] > rb[pk_r]:
                    pk_r = i
            # 1 行を短く保つ。CDC が詰まると print がブロックし、描画ごと止まる。
            print("fps", round(fps, 1), "n", layout.n, "fft", ui.fft_n(),
                  "pkL", pk_l, round(lb[pk_l], 1),
                  "pkR", pk_r, round(rb[pk_r], 1))


if __name__ == "__main__":
    main()
