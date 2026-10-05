#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    /* Parallelize outer loop: each iteration independently computes cumulative sum,
     * then modifies arrays via dummy(). Inner loop is kept sequential since it has
     * a loop-carried dependence through sum (each b[i] = sum of a[0..i]).
     * Atomic writes to b[i] prevent races between threads writing to same array.
     * Critical section on dummy() preserves call ordering and prevents races on
     * array accesses within dummy(). lastprivate ensures final sum is returned. */
    #pragma omp parallel for lastprivate(sum) shared(a, b, c, d, e)
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
            #pragma omp atomic write
            b[i] = sum;
        }
        #pragma omp critical
        dummy(a, b, c, d, e);
    }
    return sum;
}
