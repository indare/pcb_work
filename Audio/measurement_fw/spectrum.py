"""I2S 受信から N バンドスペクトルまでの実時間経路。

`frame()` はダブルバッファで、次フレームの DMA 取り込みと FFT を重ねる。
n=2048 の直列時は取り込み 43ms ＋ FFT 22ms×2ch ＋ 集計 5ms で約 90ms。
"""

import math
from array import array

from fft import (FFTFixed, ISO_CENTERS, LowBandIir, band_power_i,
                 interpolate_peak, octave_bins, peak_bin, iir_band_count)
from i2s_rx import I2SReceiver

FULL_SCALE = 1 << 23
FLOOR_DB = -120.0


def _iir_q(octaves):
    """RBJ バンドパスの Q。1/3 oct ≈4.32、1/1 系の低域分離は従来どおり 2.15。"""
    return 4.32 if octaves < 0.5 else 2.15


class SpectrumAnalyzer:
    def __init__(self, n=2048, fs=48000.0, data_pin=0, reset_pin=15,
                 centers=ISO_CENTERS, octaves=1.0):
        self.n = n
        self.fs = fs
        self.rx = I2SReceiver(data_pin=data_pin, reset_pin=reset_pin)
        self.fft = FFTFixed(n)
        self._bufs = (
            array('I', bytearray(8 * n)),
            array('I', bytearray(8 * n)),
        )
        self.raw = self._bufs[0]
        self._i = 0
        self._primed = False
        self.left = array('i', bytearray(4 * n))
        self.right = array('i', bytearray(4 * n))
        self.iir = None
        self.set_centers(centers, octaves)

    def set_centers(self, centers, octaves=1.0):
        """バンド定義だけ差し替える。FFT バッファは再利用する。"""
        self.centers = centers
        self.octaves = octaves
        self.bins = octave_bins(self.n, self.fs, centers, octaves=octaves)
        self._iir_n = iir_band_count(self.n, self.fs, centers, octaves=octaves)
        if self._iir_n:
            self.iir = LowBandIir(self.fs, centers[:self._iir_n], q=_iir_q(octaves))
        else:
            self.iir = None

    def reset_adc(self):
        self.rx.reset()

    def close(self):
        self.rx.close()

    def _analyze(self, dst, offset, raw, ch):
        self.fft.unpack(dst, raw, offset, 2)
        pw = self.fft.power(dst)
        denom = self.fft.full_scale_power(FULL_SCALE)
        bands = []
        for p in band_power_i(pw, self.bins):
            bands.append(10.0 * math.log10(p / denom) if p > 0.0 else FLOOR_DB)
        k = peak_bin(pw)
        peak_hz = interpolate_peak(pw, k) * self.fs / self.n
        peak_db = 10.0 * math.log10(pw[k] / denom) if pw[k] > 0 else FLOOR_DB
        if self.iir is not None:
            for i, db in enumerate(self.iir.block(dst, ch)):
                bands[i] = db
        return bands, peak_hz, peak_db

    def frame(self):
        """1 回分を返す。次フレームの DMA は FFT 中に走らせる。"""
        cur = self._bufs[self._i]
        if not self._primed:
            self.rx.read_into(cur)
            self._primed = True
        nxt = self._bufs[1 - self._i]
        self.rx.start_into(nxt)
        out = (self._analyze(self.left, 0, cur, 0), self._analyze(self.right, 1, cur, 1))
        self.rx.wait()
        self._i ^= 1
        self.raw = self._bufs[self._i]
        return out

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
