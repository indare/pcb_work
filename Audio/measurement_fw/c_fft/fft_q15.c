#include "fft_q15.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static int is_pow2(int n) {
    return n >= 4 && (n & (n - 1)) == 0;
}

size_t fft_q15_store_words(int n) {
    if (!is_pow2(n)) {
        return 0;
    }
    int half = n >> 1;
    /* cos,sin,rev,win,re,im,pw */
    return (size_t)half + half + n + n + n + n + (half + 1);
}

int fft_q15_init_with(fft_q15_t *f, int n, int32_t *store) {
    if (!f || !store || !is_pow2(n)) {
        return -1;
    }
    memset(f, 0, sizeof(*f));
    f->n = n;
    int half = n >> 1;
    f->store = store;
    memset(store, 0, fft_q15_store_words(n) * sizeof(int32_t));
    int32_t *p = f->store;
    f->cos = p;
    p += half;
    f->sin = p;
    p += half;
    f->rev = p;
    p += n;
    f->win = p;
    p += n;
    f->re = p;
    p += n;
    f->im = p;
    p += n;
    f->pw = p;

    const int scale = (1 << FFT_Q15_Q) - 1;
    double wsum = 0.0;
    for (int i = 0; i < half; i++) {
        f->cos[i] = (int32_t)lround(cos(2.0 * M_PI * i / n) * scale);
        f->sin[i] = (int32_t)lround(sin(2.0 * M_PI * i / n) * scale);
    }
    int bits = 0;
    while ((1 << bits) < n) {
        bits++;
    }
    for (int i = 0; i < n; i++) {
        int r = 0;
        int v = i;
        for (int b = 0; b < bits; b++) {
            r = (r << 1) | (v & 1);
            v >>= 1;
        }
        f->rev[i] = r;
    }
    for (int i = 0; i < n; i++) {
        double w = 0.5 - 0.5 * cos(2.0 * M_PI * i / (n - 1));
        wsum += w;
        f->win[i] = (int32_t)lround(w * scale);
    }
    f->cg = wsum / n;
    return 0;
}

int fft_q15_init(fft_q15_t *f, int n) {
    size_t words = fft_q15_store_words(n);
    if (!f || words == 0) {
        return -1;
    }
    int32_t *store = (int32_t *)calloc(words, sizeof(int32_t));
    if (!store) {
        return -1;
    }
    if (fft_q15_init_with(f, n, store) != 0) {
        free(store);
        return -1;
    }
    f->owns_store = 1;
    return 0;
}

void fft_q15_free(fft_q15_t *f) {
    if (!f) {
        return;
    }
    if (f->owns_store) {
        free(f->store);
    }
    memset(f, 0, sizeof(*f));
}

static int32_t sum_coarse(const int32_t *src, int n, int shift) {
    int32_t s = 0;
    for (int i = 0; i < n; i++) {
        s += src[i] >> shift;
    }
    return s;
}

static int32_t max_abs(const int32_t *src, int n, int32_t dc) {
    int32_t m = 0;
    for (int i = 0; i < n; i++) {
        int32_t v = src[i] - dc;
        if (v < 0) {
            v = -v;
        }
        if (v > m) {
            m = v;
        }
    }
    return m;
}

static void load_win(int32_t *dst, const int32_t *src, int32_t *imag, const int32_t *win,
                     int n, int32_t dc, int sh) {
    if (sh >= 0) {
        for (int i = 0; i < n; i++) {
            dst[i] = (int32_t)(((((int64_t)(src[i] - dc) << sh) * win[i]) + 16384) >> 15);
            imag[i] = 0;
        }
    } else {
        int r = -sh;
        int32_t rnd = 1 << (r - 1);
        for (int i = 0; i < n; i++) {
            int32_t t = (src[i] - dc + rnd) >> r;
            dst[i] = (int32_t)(((int64_t)t * win[i] + 16384) >> 15);
            imag[i] = 0;
        }
    }
}

static void bitrev(int32_t *re, int32_t *im, const int32_t *rev, int n) {
    for (int i = 0; i < n; i++) {
        int j = rev[i];
        if (j > i) {
            int32_t t = re[i];
            re[i] = re[j];
            re[j] = t;
            t = im[i];
            im[i] = im[j];
            im[j] = t;
        }
    }
}

static void stages(int32_t *re, int32_t *im, const int32_t *coss, const int32_t *sinn, int n) {
    int size = 2;
    int step = n >> 1;
    while (size <= n) {
        int half = size >> 1;
        for (int base = 0; base < n; base += size) {
            int k = 0;
            for (int j = base; j < base + half; j++) {
                int l = j + half;
                int32_t c = coss[k];
                int32_t s = sinn[k];
                int32_t xr = re[l];
                int32_t xi = im[l];
                int32_t tr = (int32_t)(((int64_t)xr * c + (int64_t)xi * s + 16384) >> 15);
                int32_t ti = (int32_t)(((int64_t)xi * c - (int64_t)xr * s + 16384) >> 15);
                int32_t ar = re[j];
                int32_t ai = im[j];
                re[l] = (ar - tr + 1) >> 1;
                im[l] = (ai - ti + 1) >> 1;
                re[j] = (ar + tr + 1) >> 1;
                im[j] = (ai + ti + 1) >> 1;
                k += step;
            }
        }
        size <<= 1;
        step >>= 1;
    }
}

static void power_side(int32_t *pw, const int32_t *re, const int32_t *im, int half1) {
    for (int i = 0; i < half1; i++) {
        int64_t r = re[i];
        int64_t m = im[i];
        int64_t p = r * r + m * m;
        /* match MicroPython int32 store; clamp if needed */
        if (p > INT32_MAX) {
            p = INT32_MAX;
        }
        pw[i] = (int32_t)p;
    }
}

const int32_t *fft_q15_power(fft_q15_t *f, const int32_t *samples) {
    int n = f->n;
    const int coarse = 5;
    int32_t dc = (sum_coarse(samples, n, coarse) << coarse) / n;
    int32_t peak = max_abs(samples, n, dc);

    int sh = 0;
    if (peak > 0) {
        int bits = 0;
        uint32_t v = (uint32_t)peak;
        while (v) {
            bits++;
            v >>= 1;
        }
        sh = FFT_Q15_NORM_BITS - bits;
    }
    f->shift = sh;

    load_win(f->re, samples, f->im, f->win, n, dc, sh);
    bitrev(f->re, f->im, f->rev, n);
    stages(f->re, f->im, f->cos, f->sin, n);
    power_side(f->pw, f->re, f->im, (n >> 1) + 1);
    return f->pw;
}

double fft_q15_full_scale_power(const fft_q15_t *f, double ref) {
    double a = ref * f->cg * pow(2.0, (double)(f->shift - 1));
    return a * a;
}
