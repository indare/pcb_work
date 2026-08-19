/* Host self-test for fft_q15 (no MicroPython).
 *
 *   make -C Audio/measurement_fw/c_fft test
 */
#include "fft_q15.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
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
