/* Host self-test for fft_q15 (no MicroPython).
 *
 *   make -C Audio/measurement_fw/c_fft test
 */
#include "fft_q15.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define FULL_SCALE (1 << 23)

static void sine(int32_t *a, int n, int bin, double ratio) {
    double amp = FULL_SCALE * ratio;
    for (int i = 0; i < n; i++) {
        a[i] = (int32_t)(amp * sin(2.0 * M_PI * bin * i / n));
    }
}

static int peak_bin(const int32_t *pw, int n, int skip_dc) {
    int best = skip_dc;
    for (int i = skip_dc; i < n; i++) {
        if (pw[i] > pw[best]) {
            best = i;
        }
    }
    return best;
}

static double to_dbfs(int32_t p, double denom) {
    if (p <= 0 || denom <= 0.0) {
        return -200.0;
    }
    return 10.0 * log10((double)p / denom);
}

static uint32_t spectrum_hash(const fft_q15_t *f) {
    uint32_t h = 2166136261u;
    int half1 = (f->n >> 1) + 1;
    for (int i = 0; i < half1; i++) {
        h ^= (uint32_t)f->pw[i];
        h *= 16777619u;
    }
    h ^= (uint32_t)f->shift;
    h *= 16777619u;
    return h;
}

static void fill_vector(int32_t *x, int n, int kind) {
    memset(x, 0, (size_t)n * sizeof(*x));
    if (kind == 0) {
        x[17 % n] = FULL_SCALE / 2;
    } else if (kind == 1) {
        for (int i = 0; i < n; i++) {
            double v = 0.45 * sin(2.0 * M_PI * 7 * i / n)
                     + 0.12 * sin(2.0 * M_PI * 31 * i / n)
                     + 0.01 * cos(2.0 * M_PI * 63 * i / n);
            x[i] = (int32_t)(FULL_SCALE * v);
        }
    } else {
        uint32_t s = 0x12345678u;
        for (int i = 0; i < n; i++) {
            s = s * 1664525u + 1013904223u;
            x[i] = ((int32_t)(s >> 8) - 0x800000) / 2;
        }
    }
}

static int test_golden(void) {
    static const struct {
        int n;
        int kind;
        uint32_t hash;
    } cases[] = {
        {256, 0, 0xab192ae6u},
        {256, 1, 0xb2f8caacu},
        {256, 2, 0xc2d1a7c5u},
        {1024, 0, 0x5f4b80b2u},
        {1024, 1, 0x1b3a3711u},
        {1024, 2, 0x5db5d172u},
    };
    int ok = 1;
    for (size_t c = 0; c < sizeof(cases) / sizeof(cases[0]); c++) {
        fft_q15_t f;
        int32_t *x = calloc((size_t)cases[c].n, sizeof(*x));
        int half1 = (cases[c].n >> 1) + 1;
        int32_t *direct = calloc((size_t)half1, sizeof(*direct));
        if (!x || !direct || fft_q15_init(&f, cases[c].n) != 0) {
            free(x);
            free(direct);
            return 0;
        }
        fill_vector(x, cases[c].n, cases[c].kind);
        fft_q15_power(&f, x);
        uint32_t got = spectrum_hash(&f);
        fft_q15_power_into(&f, x, direct);
        int direct_equal = memcmp(direct, f.pw, (size_t)half1 * sizeof(*direct)) == 0;
        int in_q15 = 1;
        for (int i = 0; i < cases[c].n; i++) {
            if (f.re[i] < -32768 || f.re[i] > 32767
                || f.im[i] < -32768 || f.im[i] > 32767) {
                in_q15 = 0;
                break;
            }
        }
        int pass = got == cases[c].hash && in_q15 && direct_equal;
        printf("  n=%-4d vector=%d hash=%08x  %s\n",
               cases[c].n, cases[c].kind, got, pass ? "OK" : "NG");
        ok &= pass;
        free(x);
        free(direct);
        fft_q15_free(&f);
    }
    return ok;
}

static int test_init_contract(void) {
    int32_t store[fft_q15_store_words(16)];
    fft_q15_t f;
    int ok = fft_q15_store_words(3) == 0
          && fft_q15_store_words(12) == 0
          && fft_q15_init_with(&f, 16, store) == 0
          && f.store == store
          && f.owns_store == 0;
    fft_q15_free(&f);
    ok &= f.store == NULL && f.n == 0;
    printf("  caller-owned store and invalid sizes  %s\n", ok ? "OK" : "NG");
    return ok;
}

static int test_q15_stress(void) {
    static const int sizes[] = {16, 64, 256, 1024};
    uint32_t s = 0x6d2b79f5u;
    int ok = 1;
    for (size_t z = 0; z < sizeof(sizes) / sizeof(sizes[0]); z++) {
        int n = sizes[z];
        int half1 = (n >> 1) + 1;
        fft_q15_t f;
        int32_t *x = calloc((size_t)n, sizeof(*x));
        int32_t *out = calloc((size_t)half1, sizeof(*out));
        if (!x || !out || fft_q15_init(&f, n) != 0) {
            free(x);
            free(out);
            return 0;
        }
        for (int trial = 0; trial < 32 && ok; trial++) {
            for (int i = 0; i < n; i++) {
                s = s * 1664525u + 1013904223u;
                x[i] = (int32_t)(s >> 8) - 0x800000;
            }
            fft_q15_power_into(&f, x, out);
            for (int i = 0; i < n; i++) {
                if (f.re[i] < -32768 || f.re[i] > 32767
                    || f.im[i] < -32768 || f.im[i] > 32767) {
                    ok = 0;
                    break;
                }
            }
            for (int i = 0; i < half1; i++) {
                if (out[i] < 0) {
                    ok = 0;
                    break;
                }
            }
        }
        free(x);
        free(out);
        fft_q15_free(&f);
    }
    printf("  random 24-bit inputs stay in Q15  %s\n", ok ? "OK" : "NG");
    return ok;
}

static int test_levels(void) {
    const int n = 1024;
    fft_q15_t f;
    if (fft_q15_init(&f, n) != 0) {
        fprintf(stderr, "init fail\n");
        return 0;
    }
    int32_t *x = calloc((size_t)n, sizeof(int32_t));
    if (!x) {
        fft_q15_free(&f);
        return 0;
    }
    const double ratios[] = {1.0, 0.5, 0.1, 0.01, 0.001, 0.0001};
    int ok = 1;
    printf("  %-10s %10s %10s %8s\n", "input", "read", "err", "peak");
    for (size_t i = 0; i < sizeof(ratios) / sizeof(ratios[0]); i++) {
        double ratio = ratios[i];
        sine(x, n, 21, ratio);
        const int32_t *pw = fft_q15_power(&f, x);
        double denom = fft_q15_full_scale_power(&f, FULL_SCALE);
        int k = peak_bin(pw, (n >> 1) + 1, 2);
        double db = to_dbfs(pw[k], denom);
        double want = 20.0 * log10(ratio);
        double err = db - want;
        int pass = fabs(err) <= 0.5 && k == 21;
        printf("  %7.1f dB %9.2f dB %+9.2f dB %8d  %s\n", want, db, err, k,
               pass ? "OK" : "NG");
        if (!pass) {
            ok = 0;
        }
    }
    free(x);
    fft_q15_free(&f);
    return ok;
}

static int test_speed(void) {
    const int n = 1024;
    fft_q15_t f;
    if (fft_q15_init(&f, n) != 0) {
        return 0;
    }
    int32_t *x = calloc((size_t)n, sizeof(int32_t));
    if (!x) {
        fft_q15_free(&f);
        return 0;
    }
    sine(x, n, 37, 0.5);
    fft_q15_power(&f, x);
    const int loops = 200;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < loops; i++) {
        fft_q15_power(&f, x);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms = (t1.tv_sec - t0.tv_sec) * 1000.0 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
    printf("  n=%d  host C: %.3f ms/call  (%.0f fps equiv)\n", n, ms / loops,
           loops * 1000.0 / (ms > 0 ? ms : 1));
    free(x);
    fft_q15_free(&f);
    return 1;
}

int main(void) {
    printf("c_fft host tests\n");
    int ok = 1;
    printf("init contract:\n");
    if (!test_init_contract()) {
        ok = 0;
    }
    printf("golden spectra:\n");
    if (!test_golden()) {
        ok = 0;
    }
    printf("range stress:\n");
    if (!test_q15_stress()) {
        ok = 0;
    }
    printf("levels:\n");
    if (!test_levels()) {
        ok = 0;
    }
    printf("speed:\n");
    if (!test_speed()) {
        ok = 0;
    }
    printf("%s\n", ok ? "ALL OK" : "FAILED");
    return ok ? 0 : 1;
}
