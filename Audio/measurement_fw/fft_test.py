"""fft.py の自己検証と速度計測。

浮動小数点版を素直な DFT と突き合わせて基準を作り、固定小数点版をその基準と
比べる。最後に n ごとの所要時間とバンド割当を出す。

    mpremote connect <port> cp fft.py :fft.py + run fft_test.py
"""

import gc
import math
import micropython
import time
from array import array

from fft import (FFT, FFTFixed, ISO_CENTERS, band_power_i, interpolate_peak,
                 octave_bins, peak_bin, to_dbfs)

FULL_SCALE = 1 << 23
FSAMP = 48000.0


@micropython.viper
def _shift_check(v: int) -> int:
    return v >> 1


def sine(n, bin_index, ratio, typecode='i'):
    a = array(typecode, bytearray(4 * n))
    amp = FULL_SCALE * ratio
    for i in range(n):
        a[i] = int(amp * math.sin(2.0 * math.pi * bin_index * i / n))
    return a


def naive_dft_power(x):
    n = len(x)
    out = []
    for k in range(n // 2 + 1):
        sr = 0.0
        si = 0.0
        for t in range(n):
            a = -2.0 * math.pi * k * t / n
            sr += x[t] * math.cos(a)
            si += x[t] * math.sin(a)
        out.append(sr * sr + si * si)
    return out


def test_shift():
    ok = _shift_check(-8) == -4 and _shift_check(-1) == -1
    print("  viper の >> は算術シフト: %s  (-8>>1 = %d)"
          % ("OK" if ok else "★NG★", _shift_check(-8)))
    return ok


def test_float_against_dft():
    n = 64
    f = FFT(n)
    x = array('f', bytearray(4 * n))
    for i in range(n):
        x[i] = (math.sin(2 * math.pi * 5 * i / n) * 1000.0
                + math.sin(2 * math.pi * 17 * i / n + 0.7) * 400.0
                + ((i * 37) % 11) - 5.0)
    got = f.power(x, window=False, remove_dc=False)
    want = naive_dft_power(x)
    scale = max(want)
    worst = max(abs(got[i] - want[i]) / scale for i in range(len(want)))
    print("  素の DFT との最大相対誤差: %.3e  %s"
          % (worst, "OK" if worst < 1e-4 else "★NG★"))
    return worst < 1e-4


def dbfs_of(engine, x):
    pw = engine.power(x)
    denom = engine.full_scale_power(FULL_SCALE)
    return to_dbfs(pw, denom)


def test_fixed_vs_float():
    n = 1024
    x = array('i', bytearray(4 * n))
    for i in range(n):
        x[i] = int(FULL_SCALE * (0.5 * math.sin(2 * math.pi * 21 * i / n)
                                 + 0.1 * math.sin(2 * math.pi * 133 * i / n + 1.1)
                                 + 0.01 * math.sin(2 * math.pi * 400 * i / n)))
    xf = array('f', bytearray(4 * n))
    for i in range(n):
        xf[i] = x[i]

    ref = dbfs_of(FFT(n), xf)
    got = dbfs_of(FFTFixed(n), x)

    worst = 0.0
    for i in range(1, len(ref)):
        if ref[i] > -70.0:                  # 有意なビンだけ比べる
            d = abs(got[i] - ref[i])
            if d > worst:
                worst = d
    print("  -70dBFS 以上のビンでの浮動小数点版との差: 最大 %.3f dB  %s"
          % (worst, "OK" if worst < 0.5 else "★NG★"))
    for k in (21, 133, 400):
        print("    bin %3d  浮動 %7.2f dBFS   固定 %7.2f dBFS" % (k, ref[k], got[k]))
    return worst < 0.5


def test_fixed_levels():
    n = 1024
    print("  %-10s %10s %10s %8s" % ("入力", "読み", "誤差", "ピーク位置"))
    ok = True
    for ratio in (1.0, 0.5, 0.1, 0.01, 0.001, 0.0001):
        x = sine(n, 21, ratio)
        db = dbfs_of(FFTFixed(n), x)
        k = peak_bin(db)
        want = 20.0 * math.log10(ratio)
        err = db[k] - want
        print("  %7.1f dB %9.2f dB %+9.2f dB %8d" % (want, db[k], err, k))
        if abs(err) > 0.5 or k != 21:
            ok = False
    return ok


def test_noise_floor():
    n = 1024
    x = sine(n, 21, 1.0)
    for name, engine, src in (("浮動", FFT(n), array('f', (float(v) for v in x))),
                              ("固定", FFTFixed(n), x)):
        db = dbfs_of(engine, src)
        worst = -300.0
        for i in range(1, len(db)):
            if abs(i - 21) > 3 and db[i] > worst:
                worst = db[i]
        print("  %s小数点: フルスケール正弦波のとき、ピーク以外の最大は %.1f dBFS"
              % (name, worst))


def _time_float(n):
    gc.collect()
    x = sine(n, 37, 0.5, 'f')
    f = FFT(n)
    f.power(x)
    t0 = time.ticks_us()
    f.power(x)
    return time.ticks_diff(time.ticks_us(), t0) / 1000.0


def _time_fixed(n):
    gc.collect()
    x = sine(n, 37, 0.5)
    f = FFTFixed(n)
    f.power(x)
    t0 = time.ticks_us()
    for _ in range(5):
        f.power(x)
    return time.ticks_diff(time.ticks_us(), t0) / 5000.0


def test_speed():
    print("  %-6s %9s %11s %11s %s" % ("n", "分解能", "浮動", "固定", "固定の上限"))
    for n in (256, 512, 1024, 2048, 4096):
        try:
            tf = _time_float(n)
            tfs = "%8.1f ms" % tf
        except MemoryError:
            tfs = "  メモリ不足"
        gc.collect()
        try:
            tx = _time_fixed(n)
        except MemoryError:
            print("  %-6d %6.1f Hz %s   メモリ不足" % (n, FSAMP / n, tfs))
            continue
        print("  %-6d %6.1f Hz %s %8.1f ms %7.1f fps"
              % (n, FSAMP / n, tfs, tx, 1000.0 / tx))
        gc.collect()


def test_bands():
    n = 2048
    bins = octave_bins(n, FSAMP)
    x = sine(n, 128, 0.5)          # 3000 Hz = 4k バンド
    fx = FFTFixed(n)
    pw = fx.power(x)
    denom = fx.full_scale_power(FULL_SCALE)
    bp = band_power_i(pw, bins)
    print("  3000 Hz を -6dBFS で入れたときの 10 バンド（n=%d, %.1f Hz 分解能）"
          % (n, FSAMP / n))
    for c, (lo, hi), p in zip(ISO_CENTERS, bins, bp):
        db = 10.0 * math.log10(p / denom) if p > 0 else -200.0
        bar = "#" * max(0, int((db + 90) / 3))
        print("    %8.1f Hz  bin %4d-%-4d %7.1f dBFS %s" % (c, lo, hi, db, bar))


print("=" * 78)
print("1. viper の算術シフト")
test_shift()

print("")
print("2. 浮動小数点版の正しさ（素の DFT と比較）")
test_float_against_dft()

print("")
print("3. 固定小数点版と浮動小数点版の一致")
test_fixed_vs_float()

print("")
print("4. 固定小数点版のレベル読み")
test_fixed_levels()

print("")
print("5. 実効ノイズフロア")
test_noise_floor()

print("")
print("6. 速度")
test_speed()

print("")
print("7. バンド表示")
test_bands()
print("=" * 78)
