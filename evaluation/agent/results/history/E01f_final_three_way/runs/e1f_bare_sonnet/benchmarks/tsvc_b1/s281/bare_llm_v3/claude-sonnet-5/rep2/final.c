/* TSVC-2 loop s281, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s281.h"
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

static real_t kernel_s281(void)
{
    /* Within one nl-sweep, a[i] = a[LEN-i-1] + b[i]*c[i] - 1 makes half the
     * iterations read a[LEN-i-1] before it is overwritten this sweep, and the
     * other half read it after.  Snapshotting a and b as they stood BEFORE
     * the sweep turns that into a pure function of read-only data, so every
     * i becomes independent; a/b are heap buffers since LEN_1D can be huge. */
    const int M = LEN_1D - 1;
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    real_t *b_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        memcpy(a_old, a, sizeof(real_t) * (size_t)LEN_1D);
        memcpy(b_old, b, sizeof(real_t) * (size_t)LEN_1D);
        /* a_old, b_old, c: read-only snapshots/input, shared.
         * a, b: shared; each iteration writes only its own index j, so no
         * two iterations touch the same element -> race-free.
         * M: loop-invariant bound, shared, read-only.
         * j, jp and all scratch (x, xjp, ajp_new, xj) are declared inside the
         * loop body, so they are already per-iteration and need no clause. */
        #pragma omp parallel for default(none) shared(a, b, c, a_old, b_old, M)
        for (int j = 0; j < LEN_1D; j++) {
            int jp = M - j;
            if (j <= jp) {
                /* a[jp] not yet touched this sweep: original sequential
                 * read saw the pre-sweep value, i.e. a_old[jp]. */
                real_t x = a_old[jp] + b_old[j] * c[j];
                a[j] = x - (real_t)1.0;
                b[j] = x;
            } else {
                /* a[jp] (jp is a first-half index) was already overwritten
                 * earlier in the sequential sweep; reproduce the exact same
                 * sequence of operations that produced that overwritten
                 * value, purely from the pre-sweep snapshot, so the result
                 * is bit-identical to the original order. */
                real_t xjp = a_old[j] + b_old[jp] * c[jp];
                real_t ajp_new = xjp - (real_t)1.0;
                real_t xj = ajp_new + b_old[j] * c[j];
                a[j] = xj - (real_t)1.0;
                b[j] = xj;
            }
        }
        pb_mix(nl);
    }
    free(a_old);
    free(b_old);
    return (real_t)0;
}

PB_MAIN(kernel_s281)
