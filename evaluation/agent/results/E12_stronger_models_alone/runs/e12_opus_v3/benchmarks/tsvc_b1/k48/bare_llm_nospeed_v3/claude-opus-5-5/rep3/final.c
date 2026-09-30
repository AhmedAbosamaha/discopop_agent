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

/* Returns 1 when the iterations i = 1..LEN_1D-1 of the kernel loop touch
 * pairwise-disjoint locations of u and v (so they may run in any order). */
static int k48_independent(void)
{
    long n = (long)LEN_1D;
    long *wu = (long *)malloc((size_t)n * sizeof(long));
    long *wv = (long *)malloc((size_t)n * sizeof(long));
    if (wu == NULL || wv == NULL) { free(wu); free(wv); return 0; }

    #pragma omp parallel for schedule(static) shared(wu, wv, n)
    for (long x = 0; x < n; x++) { wu[x] = -1; wv[x] = -1; }

    int bad = 0;
    for (long i = 1; i < n && !bad; i++) {
        long xu = (long)ju[i], xv = (long)jv[i];
        long ru = (long)ku[i], rv = (long)kv[i];
        if (xu < 0 || xu >= n || xv < 0 || xv >= n ||
            ru < 0 || ru >= n || rv < 0 || rv >= n) { bad = 1; }
        else {
            if (wu[xu] != -1 || wv[xv] != -1) bad = 1;
            else { wu[xu] = i; wv[xv] = i; }
        }
    }

    if (!bad) {
        #pragma omp parallel for schedule(static) shared(wu, wv, n) reduction(|:bad)
        for (long i = 1; i < n; i++) {
            long ou = wu[(long)ku[i]];
            long ov = wv[(long)kv[i]];
            if ((ou != -1 && ou != i) || (ov != -1 && ov != i)) bad |= 1;
        }
    }

    free(wu); free(wv);
    return !bad;
}

static real_t kernel_k48(void)
{
    int indep = k48_independent();
    for (int nl = 0; nl < R; nl++) {
        if (indep) {
            #pragma omp parallel for schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k48)
