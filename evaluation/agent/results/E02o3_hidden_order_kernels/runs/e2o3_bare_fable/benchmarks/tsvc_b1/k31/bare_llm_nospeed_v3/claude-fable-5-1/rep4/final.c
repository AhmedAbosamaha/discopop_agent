/* Kernel k31. */
#include "tsvc_b1/k31.h"
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

static real_t kernel_k31(void)
{
    const long n = (long)LEN_1D;
    const long o = (long)(off);
    const long f = (long)(far);
    real_t *ubuf = NULL;

    /* Snapshot of the old u, needed only when v[i] reads u ahead of its update
     * while u[i] itself reads v ahead of its update. */
    if (o >= 0 && f > 0) {
        ubuf = (real_t *)malloc((size_t)(n + f) * sizeof(real_t));
    }

    for (int nl = 0; nl < R; nl++) {
        if (o >= 0 && f >= 0) {
            /* Both reads are ahead of the writes: anti-dependences only.
             * Pass 1 updates u from the (still old) v; pass 2 builds v from
             * the old u (snapshot) when far > 0, or the new u[i] when far == 0. */
            if (f > 0) {
                #pragma omp parallel for shared(ubuf, u, n, f) schedule(static)
                for (long j = 1 + f; j < n + f; j++) {
                    ubuf[j] = u[j];
                }
            }
            #pragma omp parallel for shared(u, v, c, n, o) schedule(static)
            for (long i = 1; i < n; i++) {
                u[i] += v[i + o] * c[i];
            }
            if (f > 0) {
                #pragma omp parallel for shared(v, c, d, ubuf, n, f) schedule(static)
                for (long i = 1; i < n; i++) {
                    v[i] = ubuf[i + f] * d[i] + c[i];
                }
            } else {
                #pragma omp parallel for shared(u, v, c, d, n) schedule(static)
                for (long i = 1; i < n; i++) {
                    v[i] = u[i] * d[i] + c[i];
                }
            }
        } else if (o < 0 && f > 0) {
            /* v[i] depends only on the old u; u[i] reads the new v behind it:
             * finish the whole v pass, then do the u pass. */
            #pragma omp parallel for shared(u, v, c, d, n, f) schedule(static)
            for (long i = 1; i < n; i++) {
                v[i] = u[i + f] * d[i] + c[i];
            }
            #pragma omp parallel for shared(u, v, c, n, o) schedule(static)
            for (long i = 1; i < n; i++) {
                u[i] += v[i + o] * c[i];
            }
        } else if (o >= 0 && f < 0) {
            /* u[i] depends only on the old v; v[i] reads the new u behind it:
             * finish the whole u pass, then do the v pass. */
            #pragma omp parallel for shared(u, v, c, n, o) schedule(static)
            for (long i = 1; i < n; i++) {
                u[i] += v[i + o] * c[i];
            }
            #pragma omp parallel for shared(u, v, c, d, n, f) schedule(static)
            for (long i = 1; i < n; i++) {
                v[i] = u[i + f] * d[i] + c[i];
            }
        } else {
            /* o < 0 and f <= 0: a true recurrence of stride m.  Every iteration in
             * a block [b, b+m) reads only values produced by earlier blocks, so
             * blocks run in order and the iterations inside a block run in parallel. */
            long m = -o;
            if (f < 0 && -f < m) {
                m = -f;
            }
            for (long b = 1; b < n; b += m) {
                const long e = (b + m < n) ? (b + m) : n;
                #pragma omp parallel for shared(u, v, c, d, b, e, o, f) schedule(static)
                for (long i = b; i < e; i++) {
                    u[i] += v[i + o] * c[i];
                    v[i] = u[i + f] * d[i] + c[i];
                }
            }
        }
        pb_mix(nl);
    }

    free(ubuf);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
