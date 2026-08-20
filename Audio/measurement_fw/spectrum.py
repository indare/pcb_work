"""I2S 受信から N バンドスペクトルまでの実時間経路。

`frame()` はダブルバッファで、次フレームの DMA 取り込みと FFT を重ねる。
FFT はカスタム UF2 の `fft_q15` があればそれを使い、無ければ viper の
`FFTFixed` にフォールバックする。
"""

import math
from array import array

from fft import (FFTFixed, ISO_CENTERS, LowBandIir, band_power_i,
                 interpolate_peak, octave_bins, peak_bin, iir_band_count,
                 unpack_i2s)
from i2s_rx import I2SReceiver

FULL_SCALE = 1 << 23
FLOOR_DB = -120.0
# 起動時に確保する最大点数。1k/2k 切替はこの領域を使い回す。
MAX_N = 2048
# IIR と FFT の境を決めるときの基準点数。実際の取り込み点数では判定しない。
# 2k にすると低域のビンが増えるぶん境が 500Hz から 250Hz へ動き、そこで
# 追従の違う 2 種類のバンドが入れ替わって見え方が変わってしまうため。
IIR_SPLICE_N = 1024
# FFT バンドの下り平滑係数（フレームあたり）。~12fps で半減期 約 0.1 秒。
FFT_RELEASE = 0.5

try:
    import fft_q15
except ImportError:
    fft_q15 = None


def _iir_q(octaves):
    """RBJ バンドパスの Q。狭いバンドほど Q を上げる。"""
    if octaves < 0.4:
        return 4.32   # 1/3 oct
    if octaves < 0.8:
        return 2.15   # 2/3 oct 付近
    return 1.41       # 1/1 oct


class SpectrumAnalyzer:
    def __init__(self, n=1024, fs=48000.0, data_pin=0, reset_pin=15,
                 centers=ISO_CENTERS, octaves=1.0, max_n=MAX_N):
        if n > max_n:
            raise ValueError("n > max_n")
        self.max_n = max_n
        self.n = n
        self.fs = fs
        self.rx = I2SReceiver(data_pin=data_pin, reset_pin=reset_pin)
        self._bufs = (
            array('I', bytearray(8 * max_n)),
            array('I', bytearray(8 * max_n)),
        )
        self.raw = self._bufs[0]
        self._i = 0
        self._primed = False
        self.left = array('i', bytearray(4 * max_n))
        self.right = array('i', bytearray(4 * max_n))
        if fft_q15 is not None:
            # 2k 分のテーブルを一度だけ取る。set_n があれば 1k に縮小できる。
            self._cfft = fft_q15.FFT(max_n)
            self._pw = array('i', bytearray(4 * ((max_n >> 1) + 1)))
            self.fft = None
            self.fft_backend = "c"
            if hasattr(self._cfft, "set_n") and n != max_n:
                self._cfft.set_n(n)
        else:
            self._cfft = None
            self._pw = None
            self.fft = FFTFixed(max_n)
            self.fft_backend = "viper"
        self.iir = None
        self.set_centers(centers, octaves)

    def _fft_n(self):
        if self._cfft is not None:
            return self._cfft.n()
        return self.fft.n

    def set_n(self, n):
        """取り込み点数を変える。バッファは作り直さない。"""
        if n > self.max_n or n < 4 or (n & (n - 1)):
            raise ValueError("n")
        if n == self.n:
            return
        self.n = n
        if self._cfft is not None and hasattr(self._cfft, "set_n"):
            self._cfft.set_n(n)
        self.set_centers(self.centers, self.octaves)
        self._primed = False

    def set_centers(self, centers, octaves=1.0):
        """バンド定義だけ差し替える。FFT バッファは再利用する。"""
        self.centers = centers
        self.octaves = octaves
        self.bins = octave_bins(self._fft_n(), self.fs, centers, octaves=octaves)
        self._iir_n = iir_band_count(IIR_SPLICE_N, self.fs, centers,
                                     octaves=octaves)
        if self._iir_n:
            if isinstance(octaves, (tuple, list)):
                q = [_iir_q(width) for width in octaves[:self._iir_n]]
            else:
                q = _iir_q(octaves)
            self.iir = LowBandIir(self.fs, centers[:self._iir_n], q=q)
        else:
            self.iir = None
        # FFT バンドの表示 envelope（dB）。attack は即時、release だけ緩める。
        # 狭い 1/3 oct はビン平均本数が少なく素で暴れるので、IIR より軽めに掛ける。
        n = len(centers)
        self._env = [[FLOOR_DB] * n, [FLOOR_DB] * n]

    def reset_adc(self):
        self.rx.reset()

    def close(self):
        """I2S を止め、大きなバッファへの参照を切る。呼び出し側が gc.collect する。"""
        self.rx.close()
        self._cfft = None
        self.fft = None
        self._bufs = None
        self.raw = None
        self.left = None
        self.right = None
        self._pw = None
        self.iir = None

    def _power(self, samples):
        if self._cfft is not None:
            self._cfft.power_into(samples, self._pw)
            return self._pw, self._cfft.full_scale_power(FULL_SCALE)
        pw = self.fft.power(samples)
        return pw, self.fft.full_scale_power(FULL_SCALE)

    def _analyze(self, dst, offset, raw, ch):
        unpack_i2s(dst, raw, self.n, offset, 2)
        nfft = self._fft_n()
        if nfft > self.n:
            for i in range(self.n, nfft):
                dst[i] = 0
        pw, denom = self._power(dst)
        bands = []
        # 帯域密度: ビン平均パワーをフルスケール正弦波ピークと比較する。
        # 合計のままだと広いバンドほど音楽で棒が伸びる。単音は属するバンドの
        # ビン数ぶん 10·log10(nb) 低く見える（意図どおり）。
        env = self._env[ch]
        for i, ((lo, hi), p) in enumerate(zip(self.bins, band_power_i(pw, self.bins))):
            dens = p / float(hi - lo + 1)
            db = 10.0 * math.log10(dens / denom) if dens > 0.0 else FLOOR_DB
            e = env[i]
            # 上りは即時、下りだけ緩める（IIR バンドはこの後で上書きされる）。
            e = db if db >= e else e * FFT_RELEASE + db * (1.0 - FFT_RELEASE)
            env[i] = e
            bands.append(e)
        k = peak_bin(pw)
        peak_hz = interpolate_peak(pw, k) * self.fs / nfft
        peak_db = 10.0 * math.log10(pw[k] / denom) if pw[k] > 0 else FLOOR_DB
        if self.iir is not None:
            for i, db in enumerate(self.iir.block(dst, ch, self.n)):
                bands[i] = db
        return bands, peak_hz, peak_db

    def frame(self):
        """1 回分を返す。次フレームの DMA は FFT 中に走らせる。"""
        words = self.n * 2
        cur = self._bufs[self._i]
        if not self._primed:
            self.rx.read_into(cur, count=words)
            self._primed = True
        nxt = self._bufs[1 - self._i]
        self.rx.start_into(nxt, count=words)
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
            unpack_i2s(dst, self.raw, self.n, offset, 2)
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
