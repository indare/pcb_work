"""10 バンドスペクトルをシリアルに出し続ける。LCD ができるまでの表示器。

    mpremote connect <port> cp fft.py i2s_rx.py spectrum.py : + run spectrum_monitor.py
"""

import time

from spectrum import SpectrumAnalyzer, bar

N = 2048
REPEAT = 8


def show(tag, centers, result, elapsed):
    bands, peak_hz, peak_db = result
    print("%s  ピーク %8.1f Hz  %7.2f dBFS   （%d ms）"
          % (tag, peak_hz, peak_db, elapsed))
    for c, db in zip(centers, bands):
        print("   %8.1f Hz %7.1f dBFS |%s" % (c, db, bar(db)))


sa = SpectrumAnalyzer(n=N)
sa.reset_adc()
print("n=%d  分解能 %.1f Hz  取り込み %.1f ms 相当"
      % (N, sa.fs / N, N / sa.fs * 1000))

try:
    for _ in range(REPEAT):
        t0 = time.ticks_ms()
        l, r = sa.frame()
        dt = time.ticks_diff(time.ticks_ms(), t0)
        print("=" * 60)
        show("L", sa.centers, l, dt)
        show("R", sa.centers, r, dt)
        time.sleep_ms(200)
finally:
    sa.close()
