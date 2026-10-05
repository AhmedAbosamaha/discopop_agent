#include "data.h"

/*
 * Not parallelized: a[i] depends on the already-updated a[i-1] and
 * a[i-2] (a genuine second-order linear recurrence, not reused storage),
 * so every element's value transitively depends on every earlier
 * element's final value within this same loop. Breaking that chain
 * (e.g. via a parallel-prefix/matrix-doubling reformulation of the
 * recurrence) would regroup the floating-point multiplies/adds
 * differently from the strict left-to-right sequential evaluation,
 * which changes rounding of double results and would no longer be
 * byte-identical to the original output. The outer nl loop is likewise
 * sequential: each iteration both consumes the a[] state left by the
 * previous iteration's inner loop and calls dummy(), whose effects
 * (driven by a static counter in main.c, mutating a/b/c/d/e) are read
 * by the next iteration. Running either loop with iterations out of
 * order would be a real data race and/or produce numerically different
 * (non-bit-exact) results, so no #pragma omp is applied here.
 */
real_t kernel_s322(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
