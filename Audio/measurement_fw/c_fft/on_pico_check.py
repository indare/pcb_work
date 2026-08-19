# Statements fed to pico_exec.pl, one per line, no indentation.
# The REPL is driven line by line, so multi-line blocks are folded onto
# single lines rather than written as suites.
print("PING")
import sys, math, gc, time
print("IMPL", sys.implementation)
import fft_q15
print("FFTOK", fft_q15.FFT(256).n())
from array import array
from fft import FFTFixed
N = 1024
FS = 1 << 23
x = array('i', bytearray(4 * N))
for i in range(N): x[i] = int(FS * 0.5 * math.sin(2 * math.pi * 21 * i / N))
out = array('i', bytearray(4 * ((N >> 1) + 1)))
fc = fft_q15.FFT(N)
fp = FFTFixed(N)
fc.power_into(x, out)
pw = fp.power(x)
dc = fc.full_scale_power(FS)
dp = fp.full_scale_power(FS)
kc = max(range(2, len(out)), key=lambda i: out[i])
kp = max(range(2, len(pw)), key=lambda i: pw[i])
print("PEAKBIN", kc, kp)
print("PEAKDB", round(10 * math.log10(out[kc] / dc), 2), round(10 * math.log10(pw[kp] / dp), 2))
gc.collect()
t0 = time.ticks_us()
for _ in range(20): fc.power_into(x, out)
print("C_MS", round(time.ticks_diff(time.ticks_us(), t0) / 20000.0, 3))
gc.collect()
t0 = time.ticks_us()
for _ in range(20): fp.power(x)
print("PY_MS", round(time.ticks_diff(time.ticks_us(), t0) / 20000.0, 3))
