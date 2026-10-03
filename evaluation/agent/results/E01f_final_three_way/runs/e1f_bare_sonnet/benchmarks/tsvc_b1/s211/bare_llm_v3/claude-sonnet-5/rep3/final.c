/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s211.h"
#include <stdlib.h>

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_s211(void)
{
    /* Heap-allocated staging buffer for the new b[] values (size grows with
     * LEN_1D, so it must not be a stack array). Reused across all R
     * repetitions. */
    real_t *bnew = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Original loop carried a true dependence: a[i] read b[i-1] after
         * iteration i-1 had already overwritten it with
         * b[i-1] = b_old[i] - e[i-1]*d[i-1] (b[i+1] used for computing b[i]
         * was always still the pre-loop value, so that part was never a
         * real cross-iteration dependence, just reuse of the same array).
         * Substituting that definition in place makes every i a function of
         * only the pre-loop (shared, read-only in this region) b, c, d, e
         * arrays:
         *   i == 1: a[1] = b_old[0] + c[1]*d[1]           (b[0] never written)
         *   i >= 2: a[i] = (b_old[i] - e[i-1]*d[i-1]) + c[i]*d[i]
         * which keeps the exact same operation order as the original
         * two-statement computation, so results stay bit-identical. The new
         * b[i] = b_old[i+1] - e[i]*d[i] is staged into bnew[i] (private
         * per-iteration index, no array aliasing with the reads above)
         * instead of written back into b[] immediately, so no iteration can
         * read a value another iteration already overwrote. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, bnew)
        for (int i = 1; i < LEN_1D - 1; i++) {
            real_t anew;
            if (i == 1) {
                anew = b[0] + c[1] * d[1];
            } else {
                anew = (b[i] - e[i - 1] * d[i - 1]) + c[i] * d[i];
            }
            bnew[i] = b[i + 1] - e[i] * d[i];
            a[i] = anew;
        }

        /* Commit the staged b[] values. Independent per index; must run
         * after every index of the loop above has been read, which the
         * region boundary above already guarantees. */
        #pragma omp parallel for default(none) shared(b, bnew)
        for (int i = 1; i < LEN_1D - 1; i++) {
            b[i] = bnew[i];
        }

        pb_mix(nl);
    }

    free(bnew);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
