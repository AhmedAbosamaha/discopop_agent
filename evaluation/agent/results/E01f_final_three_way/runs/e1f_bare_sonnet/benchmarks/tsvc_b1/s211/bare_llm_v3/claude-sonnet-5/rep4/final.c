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
    /* b_old holds a snapshot of b taken before each sweep. In the original
     * sequential order, a[i] reads the value b[i-1] *after* iteration i-1
     * has written it, and b[i] reads b[i+1] *before* it has been written
     * (since the sweep goes left to right). Solving that recurrence shows
     * every a[i]/b[i] in a sweep is actually a function of only the
     * pre-sweep b (plus c, d, e):
     *   b_new[i] = b_old[i+1] - e[i]*d[i]
     *   a[i]     = b_old[0]               + c[1]*d[1]   (i == 1)
     *   a[i]     = (b_old[i] - e[i-1]*d[i-1]) + c[i]*d[i] (i > 1)
     * so once b_old is captured, the i-loop below has no dependence left
     * between iterations. b_old must be heap-allocated: LEN_1D can be up
     * to 192,000,000, far too large for a stack array. */
    real_t *b_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot: each b_old[i] is just a copy of b[i], independent of
         * every other index, so this copy loop parallelizes trivially. */
        #pragma omp parallel for default(none) shared(b, b_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            b_old[i] = b[i];
        }

        /* Each iteration writes only a[i] and b[i] (distinct i -> no
         * write-write or write-read races on a/b) and reads only b_old,
         * c, d, e at fixed, iteration-local indices -> fully independent
         * across i. bim1 is scratch declared inside the loop body, so it
         * is private by construction and needs no clause. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, b_old) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t bim1 = (i == 1) ? b_old[0] : (b_old[i] - e[i - 1] * d[i - 1]);
            a[i] = bim1 + c[i] * d[i];
            b[i] = b_old[i + 1] - e[i] * d[i];
        }
        pb_mix(nl);
    }

    free(b_old);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
