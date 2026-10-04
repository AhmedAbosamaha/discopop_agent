#include "data.h"
#include <stdlib.h>

/*
 * Original loop carries a dependence through b[]:
 *   a[i] = b[i-1] + c[i]*d[i]
 *   b[i] = b[i+1] - e[i]*d[i]
 * In the sequential order, by the time iteration i reads b[i-1], that
 * slot has already been overwritten by iteration i-1 (b[i-1] = old
 * b[i] - e[i-1]*d[i-1]), while the b[i+1] read in the same iteration is
 * still the pristine value (iteration i+1 hasn't run yet).
 *
 * To break the carry we snapshot the original b[] into b_old (heap
 * allocated, size grows with LEN_1D) before touching anything, then:
 *   1. compute every new b[i] from b_old[i+1] (the pristine neighbor) --
 *      iterations are now independent of each other.
 *   2. compute every a[i] from the now-finalized b[i-1]. Since the first
 *      loop has fully completed before the second starts, b[i-1] holds
 *      exactly the value the sequential version would have had at that
 *      point (either freshly written by loop 1, or, for i==1, the
 *      untouched b[0], which the first loop also never modifies).
 *
 * This reproduces the original values exactly while removing the
 * loop-carried dependence from both loops.
 */
real_t kernel_s211(void)
{
    real_t *b_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    #pragma omp parallel for schedule(static) shared(b, b_old)
    for (int i = 0; i < LEN_1D; i++) {
        b_old[i] = b[i];
    }

    #pragma omp parallel for schedule(static) shared(b, b_old, e, d)
    for (int i = 1; i < LEN_1D-1; i++) {
        b[i] = b_old[i + 1] - e[i] * d[i];
    }

    #pragma omp parallel for schedule(static) shared(a, b, c, d)
    for (int i = 1; i < LEN_1D-1; i++) {
        a[i] = b[i - 1] + c[i] * d[i];
    }

    free(b_old);

    return (real_t)0;
}
