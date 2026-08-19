"""実数信号の FFT とオクターブバンド集計。

素の MicroPython には ulab が無いので基数 2 の反復 FFT を自前で持つ。
クラスは 2 つある。

- `FFT`      : 浮動小数点。正確だが遅い（n=2048 で約 950ms）。検証と解析用
- `FFTFixed` : Q15 固定小数点を viper で回す。n=2048 で約 20ms。表示用

浮動小数点版が遅いのは MicroPython の float が boxed で、`@micropython.native`
にしても演算がランタイム呼び出しのままだから（実測で 1 割しか速くならない）。
viper なら整数演算が素のマシン命令になり 50 倍以上速い。その代わり
int32 に収める必要があるので、段ごとに 1/2 して桁あふれを防いでいる。
"""

import math
import micropython
from array import array

ISO_CENTERS = (31.5, 63.0, 125.0, 250.0, 500.0,
               1000.0, 2000.0, 4000.0, 8000.0, 16000.0)

# ISO 1/3 oct（25 Hz〜20 kHz）。詳細表示用。
ISO_THIRD_CENTERS = (
    25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 125.0, 160.0, 200.0,
    250.0, 315.0, 400.0, 500.0, 630.0, 800.0, 1000.0, 1250.0, 1600.0, 2000.0,
    2500.0, 3150.0, 4000.0, 5000.0, 6300.0, 8000.0, 10000.0, 12500.0, 16000.0, 20000.0,
)

Q = 15          # 回転因子と窓の小数ビット数
NORM_BITS = 15  # 入力の正規化目標ビット数
# 回転は複素振幅を保つので |xr*c + xi*s| <= |X| * 2^15 * sqrt(2)。
# |X| <= 2^15 なら 1.52e9 で int32 に収まる。|xr| + |xi| の粗い上界だと
# 1 ビット損するので、ここは複素振幅で見積もる。


def _bitrev_table(n):
    bits = 0
    while (1 << bits) < n:
        bits += 1
    rev = array('i', bytearray(4 * n))
    for i in range(n):
        r = 0
        v = i
        for _ in range(bits):
            r = (r << 1) | (v & 1)
            v >>= 1
        rev[i] = r
    return rev


def _hann(n):
    return [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]


def _check_pow2(n):
    if n < 4 or (n & (n - 1)):
        raise ValueError("n は 4 以上の 2 の冪であること")


# --------------------------------------------------------------------------
# 浮動小数点版（基準）
# --------------------------------------------------------------------------

class FFT:
    def __init__(self, n):
        _check_pow2(n)
        self.n = n
        half = n >> 1
        self.cos = array('f', (math.cos(2 * math.pi * i / n) for i in range(half)))
        self.sin = array('f', (math.sin(2 * math.pi * i / n) for i in range(half)))
        self.rev = _bitrev_table(n)
        self.win = array('f', _hann(n))
        self.cg = sum(self.win) / n
        self.re = array('f', bytearray(4 * n))
        self.im = array('f', bytearray(4 * n))
        self.pw = array('f', bytearray(4 * (half + 1)))

    def _transform(self):
        n = self.n
        re = self.re
        im = self.im
        rev = self.rev
        for i in range(n):
            j = rev[i]
            if j > i:
                t = re[i]
                re[i] = re[j]
                re[j] = t
                t = im[i]
                im[i] = im[j]
                im[j] = t

        cos = self.cos
        sin = self.sin
        size = 2
        while size <= n:
            half = size >> 1
            step = n // size
            for base in range(0, n, size):
                k = 0
                for j in range(base, base + half):
                    l = j + half
                    c = cos[k]
                    s = sin[k]
                    xr = re[l]
                    xi = im[l]
                    tr = xr * c + xi * s        # 順変換なので W = cos - j sin
                    ti = xi * c - xr * s
                    ar = re[j]
                    ai = im[j]
                    re[l] = ar - tr
                    im[l] = ai - ti
                    re[j] = ar + tr
                    im[j] = ai + ti
                    k += step
            size <<= 1

    def power(self, samples, window=True, remove_dc=True):
        """時系列から片側パワースペクトル（0 〜 n/2）。戻り値は内部バッファ。"""
        n = self.n
        if len(samples) < n:
            raise ValueError("サンプルが %d 個必要" % n)
        re = self.re
        im = self.im
        dc = 0.0
        if remove_dc:
            s = 0.0
            for i in range(n):
                s += samples[i]
            dc = s / n
        win = self.win
        for i in range(n):
            v = samples[i] - dc
            re[i] = v * win[i] if window else v
            im[i] = 0.0

        self._transform()

        pw = self.pw
        for i in range(len(pw)):
            pw[i] = re[i] * re[i] + im[i] * im[i]
        return pw

    def full_scale_power(self, ref):
        """フルスケール正弦波がピークビンに出すパワー。dBFS 換算の分母。"""
        return (ref * self.n * self.cg / 2.0) ** 2


# --------------------------------------------------------------------------
# 固定小数点版（viper）
# --------------------------------------------------------------------------

@micropython.viper
def _sum_coarse(src: ptr32, n: int, shift: int) -> int:
    """総和が int32 を超えないよう粗く落としてから足す。DC 推定にしか使わない。"""
    s = 0
    for i in range(n):
        s += src[i] >> shift
    return s


@micropython.viper
def _max_abs(src: ptr32, n: int, dc: int) -> int:
    m = 0
    for i in range(n):
        v = src[i] - dc
        if v < 0:
            v = 0 - v
        if v > m:
            m = v
    return m


@micropython.viper
def _load(dst: ptr32, src: ptr32, imag: ptr32, win: ptr32,
          n: int, dc: int, sh: int):
    """DC を抜き、正規化してから窓を掛ける。積を int32 に収める順序が要。"""
    if sh >= 0:
        for i in range(n):
            dst[i] = (((src[i] - dc) << sh) * win[i] + 16384) >> 15
            imag[i] = 0
    else:
        r = 0 - sh
        rnd = 1 << (r - 1)      # ここも切り捨てると信号に相関した歪みが出る
        for i in range(n):
            dst[i] = ((((src[i] - dc) + rnd) >> r) * win[i] + 16384) >> 15
            imag[i] = 0


@micropython.viper
def _bitrev(re: ptr32, im: ptr32, rev: ptr32, n: int):
    for i in range(n):
        j = int(rev[i])
        if j > i:
            t = re[i]
            re[i] = re[j]
            re[j] = t
            t = im[i]
            im[i] = im[j]
            im[j] = t


@micropython.viper
def _stages(re: ptr32, im: ptr32, cos: ptr32, sin: ptr32, n: int):
    size = 2
    step = n >> 1
    while size <= n:
        half = size >> 1
        base = 0
        while base < n:
            k = 0
            j = base
            end = base + half
            while j < end:
                l = j + half
                c = cos[k]
                s = sin[k]
                xr = re[l]
                xi = im[l]
                # 切り捨てだと誤差が毎段 -0.5LSB に偏ってスパーになる。
                # 半 LSB 足して丸め、誤差を平均ゼロにする（実測で 30dB 改善）
                tr = (xr * c + xi * s + 16384) >> 15
                ti = (xi * c - xr * s + 16384) >> 15
                ar = re[j]
                ai = im[j]
                re[l] = (ar - tr + 1) >> 1  # 段ごとに 1/2 して桁あふれを防ぐ
                im[l] = (ai - ti + 1) >> 1
                re[j] = (ar + tr + 1) >> 1
                im[j] = (ai + ti + 1) >> 1
                k += step
                j += 1
            base += size
        size <<= 1
        step >>= 1


@micropython.viper
def _power(pw: ptr32, re: ptr32, im: ptr32, half1: int):
    for i in range(half1):
        r = re[i]
        m = im[i]
        pw[i] = r * r + m * m


@micropython.viper
def _unpack(dst: ptr32, src: ptr32, n: int, offset: int, stride: int):
    """PIO が積んだ 24bit ワードを符号付きに直しつつ L/R を分ける。"""
    j = offset
    for i in range(n):
        v = src[j] & 0xFFFFFF
        if v >= 0x800000:
            v -= 0x1000000
        dst[i] = v
        j += stride


@micropython.viper
def _band_sum(pw: ptr32, lo: int, hi: int, shift: int) -> int:
    s = 0
    for i in range(lo, hi + 1):
        s += pw[i] >> shift
    return s


class FFTFixed:
    """Q15 固定小数点 FFT。表示用の実時間経路。

    段ごとに 1/2 するため出力の絶対値は入力に依存しない。代わりに入力を
    毎回 14bit いっぱいに正規化し、その分の指数を `shift` に持って
    dBFS 換算のときに戻す。1 フレーム内で見えるダイナミックレンジは
    おおよそ 80dB 台で、10 バンド表示には十分。
    """

    def __init__(self, n):
        _check_pow2(n)
        self.n = n
        half = n >> 1
        scale = (1 << Q) - 1
        self.cos = array('i', (int(round(math.cos(2 * math.pi * i / n) * scale))
                               for i in range(half)))
        self.sin = array('i', (int(round(math.sin(2 * math.pi * i / n) * scale))
                               for i in range(half)))
        self.rev = _bitrev_table(n)
        w = _hann(n)
        self.win = array('i', (int(round(v * scale)) for v in w))
        self.cg = sum(w) / n
        self.re = array('i', bytearray(4 * n))
        self.im = array('i', bytearray(4 * n))
        self.pw = array('i', bytearray(4 * (half + 1)))
        self.shift = 0

    def power(self, samples):
        """時系列から片側パワースペクトル。戻り値は内部バッファ。"""
        n = self.n
        if len(samples) < n:
            raise ValueError("サンプルが %d 個必要" % n)

        coarse = 5
        dc = (_sum_coarse(samples, n, coarse) << coarse) // n
        peak = _max_abs(samples, n, dc)

        sh = 0
        if peak > 0:
            bits = 0
            v = peak
            while v:
                bits += 1
                v >>= 1
            sh = NORM_BITS - bits   # 正規化目標いっぱいまで持ち上げる
        self.shift = sh

        _load(self.re, samples, self.im, self.win, n, dc, sh)
        _bitrev(self.re, self.im, self.rev, n)
        _stages(self.re, self.im, self.cos, self.sin, n)
        _power(self.pw, self.re, self.im, (n >> 1) + 1)
        return self.pw

    def full_scale_power(self, ref):
        """今回の正規化量を踏まえた、フルスケール正弦波のピークパワー。"""
        return (ref * self.cg * (2.0 ** (self.shift - 1))) ** 2

    def unpack(self, dst, raw, offset, stride=2):
        _unpack(dst, raw, self.n, offset, stride)
        return dst

    def buffer(self):
        return array('i', bytearray(4 * self.n))


# --------------------------------------------------------------------------
# 共通ヘルパ
# --------------------------------------------------------------------------

def to_dbfs(power, denom, floor=-200.0):
    out = []
    for p in power:
        out.append(10.0 * math.log10(p / denom) if p > 0.0 else floor)
    return out


def peak_bin(power, skip_dc=2):
    best = skip_dc
    for i in range(skip_dc, len(power)):
        if power[i] > power[best]:
            best = i
    return best


def interpolate_peak(power, k):
    """放物線補間でビン間の真のピーク位置を求める。窓の走査損失を減らす。"""
    if k <= 0 or k >= len(power) - 1:
        return float(k)
    a = float(power[k - 1])
    b = float(power[k])
    c = float(power[k + 1])
    d = a - 2.0 * b + c
    if d == 0.0:
        return float(k)
    return k + 0.5 * (a - c) / d


def octave_bins(n, fs, centers=ISO_CENTERS, octaves=1.0):
    """各バンドが占めるビン範囲。

    `octaves` はバンド幅（1.0=1/1 oct、1/3≈0.333=1/3 oct）。
    端は中心 × 2^{±octaves/2}。
    """
    half = n >> 1
    r = 2.0 ** (0.5 * octaves)
    out = []
    for c in centers:
        lo = int(c / r * n / fs + 0.5)
        hi = int(c * r * n / fs + 0.5)
        if lo < 1:
            lo = 1
        if hi > half:
            hi = half
        if hi < lo:
            hi = lo
        out.append((lo, hi))
    return out


def band_power(power, bins):
    out = []
    for lo, hi in bins:
        s = 0.0
        for i in range(lo, hi + 1):
            s += power[i]
        out.append(s)
    return out


def band_power_i(power, bins):
    """`FFTFixed.power()` の int 配列向け。

    1 ビンが最大 2^30 あり、広いバンドは 480 本以上足すので int32 を超える。
    バンドごとに本数から決めた分だけ落としてから足し、あとで戻す。
    落とされるのはピークから 60dB 以上下のビンで、バンド合計には効かない。
    """
    out = []
    for lo, hi in bins:
        nb = hi - lo + 1
        sh = 0
        while (nb >> sh) > 1:
            sh += 1
        out.append(float(_band_sum(power, lo, hi, sh)) * (1 << sh))
    return out


def _rbj_bp(f, fs, q):
    """RBJ bandpass（ピーク 0dB）。戻り値は (b0, b2, a1, a2)。b1=0。"""
    w0 = 2.0 * math.pi * f / fs
    alpha = math.sin(w0) / (2.0 * q)
    a0 = 1.0 + alpha
    b0 = alpha / a0
    return b0, -b0, -2.0 * math.cos(w0) / a0, (1.0 - alpha) / a0


@micropython.viper
def _decim16(src: ptr32, n: int, dst: ptr32) -> int:
    m = n >> 4
    i = 0
    j = 0
    while j < m:
        s = 0
        k = 0
        while k < 16:
            s += int(src[i])
            i += 1
            k += 1
        dst[j] = s >> 4
        j += 1
    return m


def iir_band_count(n, fs, centers, min_bins=2.5, octaves=1.0):
    """FFT ビンが足りない先頭バンド数。

    判定幅は表示バンド幅 `octaves`。ただし 1/1 表示では従来どおり 2/3 oct 幅で
    低域分離を確保する。
    """
    bin_hz = fs / n
    width = (2.0 / 3.0) if octaves >= 0.9 else octaves
    r = 2.0 ** (0.5 * width)
    bw_ratio = r - 1.0 / r
    k = 0
    for c in centers:
        if c * bw_ratio < min_bins * bin_hz:
            k += 1
        else:
            break
    return k


@micropython.viper
def _iir_ssq_q15(x: ptr32, n: int, b0: int, b2: int, a1: int, a2: int, st: ptr32) -> int:
    s1 = int(st[0])
    s2 = int(st[1])
    acc = 0
    i = 0
    while i < n:
        xi = int(x[i]) >> 8
        w = xi - ((a1 * s1 + a2 * s2) >> 15)
        if w > 32767:
            w = 32767
        elif w < -32767:
            w = -32767
        y = (b0 * w + b2 * s2) >> 15
        s2 = s1
        s1 = w
        acc += (y * y) >> 6
        i += 1
    st[0] = s1
    st[1] = s2
    return acc


class LowBandIir:
    """低域専用。16 分の 1 に間引いてからバンドパスする。

    同じ 1024 点 FFT では 25Hz と 40Hz が同じビンになる。IIR は状態が
    フレームをまたぐので分離できる。Q は 2/3 オクターブ相当。
    """

    DEC = 16

    def __init__(self, fs, centers, q=2.15):
        self.n = len(centers)
        fs_d = fs / self.DEC
        self.coeff = []
        for f in centers:
            b0, b2, a1, a2 = _rbj_bp(f, fs_d, q)
            self.coeff.append((
                int(b0 * 32767.0), int(b2 * 32767.0),
                int(a1 * 32767.0), int(a2 * 32767.0),
            ))
        self.st = [array('i', [0, 0]) for _ in range(2 * self.n)]
        self.env = [0.0] * (2 * self.n)
        self._buf = array('i', bytearray(4 * 512))

    def block(self, samples, ch):
        m = _decim16(samples, len(samples), self._buf)
        out = []
        for k in range(self.n):
            b0, b2, a1, a2 = self.coeff[k]
            idx = ch * self.n + k
            acc = _iir_ssq_q15(self._buf, m, b0, b2, a1, a2, self.st[idx])
            rms = math.sqrt(acc * 64.0 / m) * 256.0
            e = self.env[idx]
            if rms > e:
                e = e * 0.35 + rms * 0.65
            else:
                e = e * 0.92 + rms * 0.08
            self.env[idx] = e
            if e > 0.0:
                out.append(20.0 * math.log10(e / 8388608.0))
            else:
                out.append(-120.0)
        return out
