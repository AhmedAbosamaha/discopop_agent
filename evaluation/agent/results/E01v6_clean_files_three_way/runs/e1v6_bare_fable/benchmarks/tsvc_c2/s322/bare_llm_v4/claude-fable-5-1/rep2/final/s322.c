#include "data.h"

/*
 * s322: second-order linear recurrence
 *     a[i] = a[i] + a[i-1]*b[i] + a[i-2]*c[i]
 *
 * Each iteration consumes the VALUES produced by the two previous
 * iterations, so this is a true flow dependence, not a reused location.
 * The only parallel formulation (a prefix scan over 3x3 affine matrices,
 * or matrix-derived chunk seeds) reassociates the floating-point
 * operations and changes the rounding, so it cannot reproduce the
 * sequential output bit-for-bit.  The outer nl loop is likewise serial
 * because dummy() perturbs a, b, c between passes.  The kernel is
 * therefore left sequential on purpose: no legal OpenMP annotation
 * exists that keeps the output byte-identical.
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
