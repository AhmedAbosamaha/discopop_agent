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
    /* Holds, per repetition, the values b[1..LEN_1D-2] will take on after the
     * inner loop, plus newb[0] mirroring the untouched b[0]. Materializing them
     * here breaks the b[i] <-> b[i-1]/b[i+1] recurrence into two independent
     * passes. Heap-allocated because LEN_1D can be far larger than the stack. */
    real_t *newb = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* b[0] is never written by the loop below, so it carries over unchanged;
         * record it so the i==1 case of the second pass can read it uniformly
         * through newb[i-1]. */
        newb[0] = b[0];

        /* Pass 1: new b[i] depends only on the OLD b[i+1] (never written by this
         * loop before being read, in any order) and e[i], d[i]. Writes land in
         * newb, a location nothing else in this pass reads, so iterations are
         * fully independent. */
        #pragma omp parallel for default(none) shared(b, d, e, newb) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            newb[i] = b[i + 1] - e[i] * d[i];
        }

        /* Pass 2: a[i] needs the NEW b[i-1], i.e. newb[i-1], which pass 1 has
         * already fully computed (separate parallel-for region = implicit
         * barrier before this one starts). b[i] is simply published from newb[i].
         * Each iteration writes its own a[i]/b[i] and only reads newb, so
         * iterations are independent regardless of execution order. */
        #pragma omp parallel for default(none) shared(a, b, c, d, newb) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = newb[i - 1] + c[i] * d[i];
            b[i] = newb[i];
        }

        pb_mix(nl);
    }

    free(newb);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
