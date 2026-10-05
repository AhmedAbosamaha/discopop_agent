/* TSVC-2 loop s151, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s151.h"

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

void s151s(real_t a[LEN_1D], real_t b[LEN_1D],  int m)
{
    /* Allocate temporary buffer to break backward loop-carried dependence:
     * original loop reads a[i+m] before it's overwritten by iteration i+m.
     * Use two-pass approach: compute into tmp (parallel), then copy back (parallel) */
    real_t *tmp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    /* First pass: compute new values using original a and b (fully parallel).
     * Reads: a (shared, read-only), b (shared, read-only), m (shared, read-only).
     * Writes: tmp (shared, each iteration writes tmp[i]).
     * Loop variable i is implicitly private. */
    #pragma omp parallel for shared(a, b, tmp, m)
    for (int i = 0; i < LEN_1D-1; i++) {
        tmp[i] = a[i + m] + b[i];
    }

    /* Second pass: copy results back to a (fully parallel).
     * Reads: tmp (shared, read-only).
     * Writes: a (shared, each iteration writes a[i]).
     * Loop variable i is implicitly private. */
    #pragma omp parallel for shared(a, tmp)
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = tmp[i];
    }

    free(tmp);
}

static real_t kernel_s151(void)
{
    for (int nl = 0; nl < R; nl++) {
        s151s(a, b,  1);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s151)
