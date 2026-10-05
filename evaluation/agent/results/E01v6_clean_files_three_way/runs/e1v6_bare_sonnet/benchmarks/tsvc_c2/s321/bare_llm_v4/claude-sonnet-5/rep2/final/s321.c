#include "data.h"

/*
 * This kernel is a first-order linear recurrence: a[i] = a[i] + b[i]*a[i-1],
 * where a[i-1] is the value just written by the previous loop iteration of
 * this same sweep (a genuine value dependence, not a reused location), and
 * array `a` is carried (not reset) across the outer `nl` sweeps, with
 * dummy() further mutating a[0]/a[k]/b[...] between sweeps. Any correct
 * closed-form way to skip ahead (parallel scan / recursive doubling) would
 * re-associate the floating-point multiply-adds and change rounding versus
 * the strictly sequential chain computed here, and any scheme that instead
 * replays the full prefix chain to seed a chunk costs as much as the
 * original loop already does, so it cannot yield a net speedup either way.
 * There is no race-free, bit-exact-preserving #pragma omp worksharing
 * decomposition of this loop nest, so it is intentionally left sequential.
 */
real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += a[i-1] * b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
