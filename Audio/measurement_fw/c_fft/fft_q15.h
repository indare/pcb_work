/* Q15 fixed-point real FFT — port of measurement_fw/fft.py FFTFixed hot path.
 *
 * Host-testable first. Later: wrap as MicroPython USER_C_MODULE.
 */
#ifndef FFT_Q15_H
#define FFT_Q15_H

#include <stddef.h>
#include <stdint.h>

#define FFT_Q15_Q 15
#define FFT_Q15_NORM_BITS 15

typedef struct {
    int n;
    int shift; /* last power() normalization shift */
    int32_t *cos;
    int32_t *sin;
    int32_t *rev;
    int32_t *win;
    int32_t *re;
    int32_t *im;
    int32_t *pw; /* length n/2+1 */
    double cg;   /* coherent gain of Hann */
    /* backing store (single allocation) */
    int32_t *store;
    int owns_store; /* only free what we allocated ourselves */
} fft_q15_t;

/* Words of int32 that init_with expects in store. 0 if n is not usable. */
size_t fft_q15_store_words(int n);

/* Build the tables inside a caller-owned store of fft_q15_store_words(n).
 * Lets an embedder allocate from its own heap; MicroPython must, because the
 * GC heap covers the RAM that libc malloc would otherwise hand out.
 * Returns 0 on success. */
int fft_q15_init_with(fft_q15_t *f, int n, int32_t *store);

/* Same, allocating the store with calloc. For hosted builds. */
int fft_q15_init(fft_q15_t *f, int n);

void fft_q15_free(fft_q15_t *f);

/* In-place style: samples[0..n) int32 → power spectrum in f->pw (n/2+1).
 * Returns pointer to f->pw (owned by fft_q15_t). */
const int32_t *fft_q15_power(fft_q15_t *f, const int32_t *samples);

/* Same transform, writing the n/2+1 powers directly into caller memory.
 * This avoids a second copy in language bindings. */
void fft_q15_power_into(fft_q15_t *f, const int32_t *samples, int32_t *pw);

/* Denominator for dBFS: (ref * cg * 2^(shift-1))^2 */
double fft_q15_full_scale_power(const fft_q15_t *f, double ref);

#endif
