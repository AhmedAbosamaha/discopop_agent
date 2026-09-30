/* Kernel k19. */
#include "tsvc_b1/k19.h"
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

static real_t kernel_k19(void)
{
    const long n = (long)LEN_1D;
    long *scr = (long *)malloc((size_t)n * sizeof(long));
    unsigned char *ownU = (unsigned char *)malloc((size_t)n);
    unsigned char *lastV = (unsigned char *)malloc((size_t)n);
    real_t *nu = (real_t *)malloc((size_t)n * sizeof(real_t));
    real_t *tv = (real_t *)malloc((size_t)n * sizeof(real_t));
    int bad = (scr == NULL || ownU == NULL || lastV == NULL || nu == NULL || tv == NULL);

    if (!bad) {
        /* index range check */
        #pragma omp parallel for reduction(||:bad)
        for (long i = 1; i < n; i++) {
            long x1 = (long)ju[i], x2 = (long)ku[i], x3 = (long)jv[i], x4 = (long)kv[i];
            if (x1 < 0 || x1 >= n || x2 < 0 || x2 >= n ||
                x3 < 0 || x3 >= n || x4 < 0 || x4 >= n)
                bad = 1;
        }
    }
    if (!bad) {
        /* u: writer of each location (must be unique) */
        #pragma omp parallel for
        for (long x = 0; x < n; x++)
            scr[x] = -1;
        for (long i = 1; i < n; i++) {
            long x = (long)ju[i];
            if (scr[x] != -1) bad = 1;
            scr[x] = i;
        }
    }
    if (!bad) {
        /* u[ku[i]] must be either this iteration's update or untouched before i */
        #pragma omp parallel for reduction(||:bad)
        for (long i = 1; i < n; i++) {
            long w = scr[(long)ku[i]];
            ownU[i] = (unsigned char)(w == i);
            if (w != -1 && w < i) bad = 1;
        }
    }
    if (!bad) {
        /* v: first writer of each location */
        #pragma omp parallel for
        for (long x = 0; x < n; x++)
            scr[x] = -1;
        for (long i = 1; i < n; i++) {
            long x = (long)jv[i];
            if (scr[x] == -1) scr[x] = i;
        }
        /* v[kv[i]] must not have been written by an earlier iteration */
        #pragma omp parallel for reduction(||:bad)
        for (long i = 1; i < n; i++) {
            long f = scr[(long)kv[i]];
            if (f != -1 && f < i) bad = 1;
        }
    }
    if (!bad) {
        /* v: last writer of each location */
        for (long i = 1; i < n; i++)
            scr[(long)jv[i]] = i;
        #pragma omp parallel for
        for (long i = 1; i < n; i++)
            lastV[i] = (unsigned char)(scr[(long)jv[i]] == i);
    }

    for (int nl = 0; nl < R; nl++) {
        if (!bad) {
            /* phase A: read-only, compute new values */
            #pragma omp parallel for
            for (long i = 1; i < n; i++) {
                real_t nv = u[ju[i]] + v[kv[i]] * c[i];
                real_t uu = ownU[i] ? nv : u[ku[i]];
                nu[i] = nv;
                tv[i] = uu * d[i] + c[i];
            }
            /* phase B: scatter to distinct locations */
            #pragma omp parallel for
            for (long i = 1; i < n; i++) {
                u[ju[i]] = nu[i];
                if (lastV[i]) v[jv[i]] = tv[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(scr); free(ownU); free(lastV); free(nu); free(tv);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
