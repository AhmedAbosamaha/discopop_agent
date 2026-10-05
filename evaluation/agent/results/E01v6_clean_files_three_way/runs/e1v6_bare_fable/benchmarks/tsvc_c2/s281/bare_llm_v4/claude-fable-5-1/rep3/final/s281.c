#include "data.h"

real_t kernel_s281(void)
{
    /* Split point: for i < half the read a[LEN_1D-i-1] hits an index >= i
     * (not yet written this pass); for i >= half it hits an index < half
     * that was written by the first loop.  Running the two halves as two
     * separate loops (first finishes before second starts) keeps that
     * value flow intact while making each loop's iterations independent. */
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        /* First half: reads original a[] values only. */
#pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* Second half: reads a[] values produced by the first loop. */
#pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = half; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
