/* TSVC-2 loop s277, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s277.h"

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

static real_t kernel_s277(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Create a snapshot of b to allow parallel reads of b[i] without races.
         * Each iteration i only writes to b[i+1], so no write-write conflicts.
         * This breaks the carry-in read-after-write dependence by ensuring all
         * iterations read from a consistent pre-iteration-loop state of b. */
        real_t *b_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(b_snapshot, b, LEN_1D * sizeof(real_t));

        /* Each iteration i can run in any order since:
         * - each reads only b_snapshot[i], c[i], d[i], e[i] (constant across iterations)
         * - each reads and may write a[i] (unique index per thread)
         * - each writes only b[i+1] (unique index per thread, disjoint from all other writes)
         * Clauses: b_snapshot is read-only so shared; a, c, d, e are shared but
         * accesses are independent; b is shared but each write is to a distinct location. */
        #pragma omp parallel for shared(a, b, c, d, e, b_snapshot) private(i)
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] >= (real_t)0.) {
                    /* Skip: don't execute lines below, equivalent to goto L20 */
                } else {
                    if (b_snapshot[i] < (real_t)0.) {
                        /* Executed when a[i] < 0 and b[i] < 0, equivalent to skipping L30 branch */
                        a[i] += c[i] * d[i];
                    }
                    /* Always executed when a[i] < 0, equivalent to label L30 */
                    b[i+1] = c[i] + d[i] * e[i];
                }
                /* Label L20: end of iteration, always reached */
        }

        free(b_snapshot);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
