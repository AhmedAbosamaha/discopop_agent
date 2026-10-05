/* TSVC-2 loop s252, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s252.h"

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

static real_t kernel_s252(void)
{
    real_t t, s;
    real_t* s_vals = (real_t*)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Parallel loop 1: compute all products s[i] = b[i] * c[i] independently.
           No loop-carried dependencies; each iteration computes its own s value. */
        #pragma omp parallel for private(s)
        for (int i = 0; i < LEN_1D; i++) {
            s_vals[i] = b[i] * c[i];
        }

        /* Compute a values using the precomputed s values.
           a[0] = s[0], and for i >= 1: a[i] = s[i] + s[i-1].
           No loop-carried dependencies; each iteration reads only the already-computed s values. */
        a[0] = s_vals[0];
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = s_vals[i] + s_vals[i-1];
        }

        pb_mix(nl);
    }

    free(s_vals);
    return (real_t)0;
}

PB_MAIN(kernel_s252)
