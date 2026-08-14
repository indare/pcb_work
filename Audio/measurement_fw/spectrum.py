"""I2S 受信から 10 バンドスペクトルまでの実時間経路。

1 フレームの内訳は n=2048 でおおよそ
取り込み 43ms（48kHz で 2048 サンプル）＋ FFT 22ms×2ch ＋ 集計 5ms で
約 90ms。LCD 表示は 10fps 前後になる見込み。
"""

import math
from array import array

from fft import FFTFixed, ISO_CENTERS, band_power_i, interpolate_peak, octave_bins, peak_bin
from i2s_rx import I2SReceiver

FULL_SCALE = 1 << 23
FLOOR_DB = -120.0


class SpectrumAnalyzer:
    def __init__(self, n=2048, fs=48000.0, data_pin=0, reset_pin=15,
                 centers=ISO_CENTERS):
        self.n = n
        self.fs = fs
        self.centers = centers
        self.rx = I2SReceiver(data_pin=data_pin, reset_pin=reset_pin)
        self.fft = FFTFixed(n)
        self.bins = octave_bins(n, fs, centers)
        self.raw = array('I', bytearray(8 * n))
        self.left = array('i', bytearray(4 * n))
        self.right = array('i', bytearray(4 * n))

    def reset_adc(self):
        self.rx.reset()

    def close(self):
        self.rx.close()

    def _analyze(self, dst, offset):
        self.fft.unpack(dst, self.raw, offset, 2)
        pw = self.fft.power(dst)
        denom = self.fft.full_scale_power(FULL_SCALE)
        bands = []
        for p in band_power_i(pw, self.bins):
            bands.append(10.0 * math.log10(p / denom) if p > 0.0 else FLOOR_DB)
        k = peak_bin(pw)
        peak_hz = interpolate_peak(pw, k) * self.fs / self.n
        peak_db = 10.0 * math.log10(pw[k] / denom) if pw[k] > 0 else FLOOR_DB
        return bands, peak_hz, peak_db

    def frame(self):
        """1 回取り込んで L/R それぞれの (バンド dBFS, ピーク Hz, ピーク dBFS)。"""
        self.rx.read_into(self.raw)
        return (self._analyze(self.left, 0), self._analyze(self.right, 1))

    def levels(self):
        """バンドを介さない全体レベル。ピークとおおよその RMS を dBFS で。"""
        self.rx.read_into(self.raw)
        out = []
        for dst, offset in ((self.left, 0), (self.right, 1)):
            self.fft.unpack(dst, self.raw, offset, 2)
            n = self.n
            s = 0
            for i in range(n):
                s += dst[i]
            dc = s // n
            pk = 0
            acc = 0.0
            for i in range(n):
                v = dst[i] - dc
                acc += float(v) * v
                if v < 0:
                    v = -v
                if v > pk:
                    pk = v
            rms = (acc / n) ** 0.5
            out.append((_db(pk), _db(rms * (2.0 ** 0.5)), dc))
        return out


def _db(v):
    return 20.0 * math.log10(v / FULL_SCALE) if v > 0 else FLOOR_DB


def bar(db, lo=-90.0, hi=0.0, width=32):
    """dBFS を横棒に。表示器ができるまでのシリアル用。"""
    if db <= lo:
        return ""
    k = int((db - lo) / (hi - lo) * width + 0.5)
    return "#" * min(width, max(0, k))
