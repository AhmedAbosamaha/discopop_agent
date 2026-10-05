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
    const long n = (long)LEN_1D;

    /* ---- Inspector (serial, run once: the index arrays never change) ----
     * Assign every iteration i a wavefront level such that any iteration that
     * writes a location read/written by i, or reads a location written by i,
     * has a strictly smaller level.  Iterations of equal level are independent. */
    long maxu = 0, maxv = 0;
    for (long i = 1; i < n; i++) {
        long t;
        t = (long)ju[i]; if (t > maxu) maxu = t;
        t = (long)ku[i]; if (t > maxu) maxu = t;
        t = (long)jv[i]; if (t > maxv) maxv = t;
        t = (long)kv[i]; if (t > maxv) maxv = t;
    }

    int *ulw = (int *)calloc((size_t)(maxu + 1), sizeof(int)); /* level of last writer of u[x] */
    int *ulr = (int *)calloc((size_t)(maxu + 1), sizeof(int)); /* max level of readers of u[x] since */
    int *vlw = (int *)calloc((size_t)(maxv + 1), sizeof(int));
    int *vlr = (int *)calloc((size_t)(maxv + 1), sizeof(int));
    int *lev = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));

    long nlev = 0;
    for (long i = 1; i < n; i++) {
        long xju = (long)ju[i], xku = (long)ku[i], xjv = (long)jv[i], xkv = (long)kv[i];
        int dep = 0;
        /* reads: v[kv[i]], u[ku[i]], u[ju[i]] -> after last writer */
        if (vlw[xkv] > dep) dep = vlw[xkv];
        if (ulw[xku] > dep) dep = ulw[xku];
        /* writes: u[ju[i]], v[jv[i]] -> after last writer and all readers */
        if (ulw[xju] > dep) dep = ulw[xju];
        if (ulr[xju] > dep) dep = ulr[xju];
        if (vlw[xjv] > dep) dep = vlw[xjv];
        if (vlr[xjv] > dep) dep = vlr[xjv];
        int L = dep + 1;
        lev[i] = L;
        if ((long)L > nlev) nlev = L;
        /* record this iteration's accesses */
        if (vlr[xkv] < L) vlr[xkv] = L;
        if (ulr[xku] < L) ulr[xku] = L;
        ulw[xju] = L; ulr[xju] = L;
        vlw[xjv] = L; vlr[xjv] = L;
    }
    free(ulw); free(ulr); free(vlw); free(vlr);

    /* Bucket iterations by level (CSR), keeping increasing i within a level. */
    long *off = (long *)calloc((size_t)(nlev + 2), sizeof(long));
    for (long i = 1; i < n; i++) off[lev[i] + 1]++;
    for (long l = 1; l <= nlev; l++) off[l + 1] += off[l];
    long *fill = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
    for (long l = 0; l <= nlev + 1; l++) fill[l] = off[l];
    int *order = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));
    for (long i = 1; i < n; i++) order[fill[lev[i]]++] = (int)i;
    free(fill);
    free(lev);

    /* ---- Executor ---- */
    for (int nl = 0; nl < R; nl++) {
        for (long l = 1; l <= nlev; l++) {
            const long lo = off[l];
            const long hi = off[l + 1];
#pragma omp parallel for default(shared) shared(order, lo, hi)
            for (long p = lo; p < hi; p++) {
                long i = (long)order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(order);
    free(off);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
