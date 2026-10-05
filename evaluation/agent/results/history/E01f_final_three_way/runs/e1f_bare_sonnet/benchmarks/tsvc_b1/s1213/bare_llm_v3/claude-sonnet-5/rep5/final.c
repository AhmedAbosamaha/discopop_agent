/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"
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

static real_t kernel_s1213(void)
{
    /* The i-loop looks like it carries two dependences (a[i] on b[i-1],
     * b[i] on a[i+1]), but tracing the serial execution shows both are
     * only ever satisfied by values that already existed before this
     * pass of the i-loop started:
     *   - b[i] = a[i+1]*d[i] always reads a[i+1] before the iteration
     *     that would overwrite it (i+1 runs strictly later), so it only
     *     ever sees the pre-loop value of a[i+1].
     *   - a[i] = b[i-1]+c[i] for i>=2 reads b[i-1], but b[i-1] was itself
     *     just computed as a_old[i]*d[i-1] (same argument as above, with
     *     i-1 in place of i). Substituting that in gives
     *     a[i] = a_old[i]*d[i-1]+c[i] for i>=2 -- a closed form that
     *     depends only on the pre-loop snapshot of a[], not on any value
     *     produced earlier in this same pass. For i==1, b[0] is never
     *     written by this loop, so reading it live is already safe.
     * So the loop becomes independent across i once every read of a[]
     * is redirected to a heap snapshot (a_old) taken before the loop
     * runs; the arithmetic performed is byte-for-byte the same
     * multiply-then-add as the original, just without the redundant
     * store/reload through b[i-1]. a_old is heap-allocated since its
     * size tracks LEN_1D, which can be very large. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot: a_old captures a[] exactly as it stood before this
         * pass, i.e. the values every iteration below is entitled to
         * see regardless of execution order. */
        #pragma omp parallel for shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* Each iteration now only writes a[i] and b[i] and only reads
         * the read-only snapshot a_old, the read-only b[0] (never
         * written by this loop), and the read-only c[]/d[]: no
         * cross-iteration dependence remains. */
        #pragma omp parallel for shared(a, b, c, d, a_old) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            if (i == 1) {
                a[1] = b[0] + c[1];
            } else {
                a[i] = a_old[i]*d[i-1] + c[i];
            }
            b[i] = a_old[i+1]*d[i];
        }
        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
