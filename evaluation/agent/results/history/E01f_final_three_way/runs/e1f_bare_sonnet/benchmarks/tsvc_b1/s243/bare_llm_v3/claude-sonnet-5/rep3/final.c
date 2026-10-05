/* TSVC-2 loop s243, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s243.h"
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

static real_t kernel_s243(void)
{
    /* The third statement in the i-loop reads a[i+1], the value a[] held
     * *before* this i-loop started touching it (iteration i+1 hasn't run
     * yet when the sequential code reaches iteration i). That is a reused
     * location, not a value that needs to keep flowing forward: snapshot
     * a[] into a heap buffer once per nl-repetition and read the shifted
     * term from the snapshot instead of from the array the loop is
     * concurrently writing. That removes the anti-dependence between
     * iteration i (reader of a[i+1]) and iteration i+1 (writer of a[i+1])
     * so the i-loop can run its iterations in any order/partition.
     * a[i] is written then re-read within the very same iteration i, and
     * b[i]/c[i]/d[i]/e[i] are only ever touched at index i, so none of
     * that is loop-carried. */
    real_t *olda = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot of a[] as it stood right before this repetition's
         * i-loop modifies it. Disjoint read/write per i, fully
         * independent. */
        #pragma omp parallel for default(none) shared(a, olda)
        for (int i = 0; i < LEN_1D; i++) {
            olda[i] = a[i];
        }

        /* Each iteration i only ever writes a[i] and b[i], and only ever
         * reads c[i], d[i], e[i] and the pre-loop snapshot olda[i+1].
         * No iteration reads or writes a location another iteration
         * writes, so the iterations are independent. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, olda)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + olda[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(olda);
    return (real_t)0;
}

PB_MAIN(kernel_s243)
