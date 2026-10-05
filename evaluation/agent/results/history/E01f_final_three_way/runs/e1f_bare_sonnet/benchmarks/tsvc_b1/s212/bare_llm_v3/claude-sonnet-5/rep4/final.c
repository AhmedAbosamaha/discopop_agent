/* TSVC-2 loop s212, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s212.h"
#include <stdlib.h>
#include <string.h>

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

static real_t kernel_s212(void)
{
    /* a_old: snapshot of a[] taken before each repetition's i-loop runs. The i-loop
     * reads a[i] and a[i+1] with the values they held at the start of the repetition
     * (that's what the original sequential order actually delivered to iteration i,
     * since index i is only ever written by iteration i, and index i+1 only by
     * iteration i+1, which in the old order had not run yet). Reading from this
     * read-only snapshot instead of the live, concurrently-written a[] removes the
     * loop-carried dependence and makes the iterations independent. Size follows
     * LEN_1D, which can be very large, so it is heap-allocated, not a local array. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
        /* a_old: shared, read-only snapshot for this repetition (no writes inside the loop).
         * a, b, c, d: shared; each iteration i writes only a[i] and b[i], and reads only
         * c[i], d[i] and a_old[i], a_old[i+1] — disjoint across iterations, so no race.
         * i: loop variable, private by default under omp for. */
        #pragma omp parallel for default(none) shared(a, b, c, d, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_old[i] * c[i];
            b[i] += a_old[i + 1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s212)
