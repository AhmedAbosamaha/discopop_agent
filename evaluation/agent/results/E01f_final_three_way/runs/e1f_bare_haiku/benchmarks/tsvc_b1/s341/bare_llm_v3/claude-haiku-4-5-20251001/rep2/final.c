/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

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

static real_t kernel_s341(void)
{
    int j;
    int *count = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < R; nl++) {
        j = -1;
        int total_count = 0;

        // Phase 1: Count elements where b[i] > 0 (parallel)
        // total_count: accumulator for number of qualifying elements
        // b: shared, read-only array
        #pragma omp parallel for shared(b) reduction(+:total_count)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                total_count++;
            }
        }

        // Phase 2: Compute exclusive prefix sum of the condition
        // count[i] = number of elements before i that satisfy b[j] > 0
        // This is sequential due to loop-carried dependency, but O(LEN_1D) like original
        count[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            count[i] = count[i-1] + (b[i-1] > (real_t)0. ? 1 : 0);
        }

        // Phase 3: Write results in parallel using precomputed indices
        // a: shared array being written (different indices per thread, no race)
        // b: shared read-only array
        // count: shared read-only array with target indices
        #pragma omp parallel for shared(a, b, count)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[count[i]] = b[i];
            }
        }

        j = total_count - 1;
        pb_mix(nl);
    }

    free(count);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
