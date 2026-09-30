/* Kernel k48. */
#include "tsvc_b1/k48.h"
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

static real_t kernel_k48(void)
{
    /* Inspector: index arrays are fixed during the kernel.  Parallel path is valid when
     * ju and jv are injective and no iteration reads a u/v location written by an
     * EARLIER iteration (only anti-dependences / same-iteration reuse remain). */
    int ok = 1;
    long *wu = (long *)calloc((size_t)LEN_1D, sizeof(long));
    long *wv = (long *)calloc((size_t)LEN_1D, sizeof(long));
    real_t *tv = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *ou = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (!wu || !wv || !tv || !ou) ok = 0;
    if (ok) {
        for (long i = 1; i < LEN_1D; i++) {
            long rv = (long)kv[i], wuI = (long)ju[i], ru = (long)ku[i], wvI = (long)jv[i];
            if (wv[rv] != 0) ok = 0;                 /* v read written earlier */
            if (wu[wuI] != 0) ok = 0;                /* duplicate u write */
            wu[wuI] = i + 1;
            if (wu[ru] != 0 && wu[ru] != i + 1) ok = 0; /* u read written earlier */
            if (wv[wvI] != 0) ok = 0;                /* duplicate v write */
            wv[wvI] = i + 1;
        }
    }
    free(wu);
    free(wv);

    for (int nl = 0; nl < R; nl++) {
        if (ok) {
            #pragma omp parallel for shared(u, v, c, ku, kv, tv, ou)
            for (long i = 1; i < LEN_1D; i++) {
                tv[i] = v[kv[i]] * c[i];
                ou[i] = u[ku[i]];
            }
            #pragma omp parallel for shared(u, v, c, d, ju, jv, ku, tv, ou)
            for (long i = 1; i < LEN_1D; i++) {
                real_t uu = (ku[i] == ju[i]) ? (ou[i] + tv[i]) : ou[i];
                u[ju[i]] += tv[i];
                v[jv[i]] = uu * d[i] + c[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(tv);
    free(ou);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
