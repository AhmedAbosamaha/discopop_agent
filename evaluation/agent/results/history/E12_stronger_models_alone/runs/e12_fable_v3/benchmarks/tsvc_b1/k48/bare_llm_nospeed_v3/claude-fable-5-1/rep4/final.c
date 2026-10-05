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

/* One iteration of the original inner loop, body unchanged. */
static inline void k48_iter(long i)
{
    u[ju[i]] += v[kv[i]] * c[i];
    v[jv[i]] = u[ku[i]] * d[i] + c[i];
}

/* Minimum number of iterations in a level before it is worth a parallel region. */
#define K48_PAR_MIN 64

static real_t kernel_k48(void)
{
    const long n = LEN_1D;

    /* ---------------------------------------------------------------
     * Inspector (run once): the index arrays ju/ku/kv/jv never change,
     * so the dependence structure of the inner loop is the same for
     * every repetition.  Assign each iteration i a level such that it is
     * strictly above every earlier iteration it conflicts with through
     * u[] or v[] (flow, anti and output dependences).  Iterations of one
     * level touch no common location with a write and may run in any
     * order; levels are executed in increasing order.
     * --------------------------------------------------------------- */
    long mx = 0;
    #pragma omp parallel for reduction(max:mx)
    for (long i = 1; i < n; i++) {
        long t;
        t = (long)ju[i]; if (t > mx) mx = t;
        t = (long)ku[i]; if (t > mx) mx = t;
        t = (long)kv[i]; if (t > mx) mx = t;
        t = (long)jv[i]; if (t > mx) mx = t;
    }
    const long m = mx + 1;

    int *wU = (int *)calloc((size_t)m, sizeof(int));   /* level of last writer of u[x] */
    int *rU = (int *)calloc((size_t)m, sizeof(int));   /* max level of readers of u[x] */
    int *wV = (int *)calloc((size_t)m, sizeof(int));   /* level of last writer of v[x] */
    int *rV = (int *)calloc((size_t)m, sizeof(int));   /* max level of readers of v[x] */
    int *lev = (int *)malloc((size_t)(n > 1 ? n : 1) * sizeof(int));
    long *off = NULL;    /* level l (1-based) spans perm[off[l-1] .. off[l]) */
    long *perm = NULL;   /* iteration indices sorted by level, stable */
    long *cur = NULL;
    int nlev = 0;
    int ok = (wU != NULL) && (rU != NULL) && (wV != NULL) && (rV != NULL) && (lev != NULL);

    if (ok) {
        for (long i = 1; i < n; i++) {
            long xu = (long)ju[i];   /* u[xu]: read + write */
            long yu = (long)ku[i];   /* u[yu]: read         */
            long xv = (long)kv[i];   /* v[xv]: read         */
            long yv = (long)jv[i];   /* v[yv]: write        */
            int l = 1, t;
            t = wU[xu] + 1; if (t > l) l = t;
            t = rU[xu] + 1; if (t > l) l = t;
            t = wU[yu] + 1; if (t > l) l = t;
            t = wV[xv] + 1; if (t > l) l = t;
            t = wV[yv] + 1; if (t > l) l = t;
            t = rV[yv] + 1; if (t > l) l = t;
            lev[i] = l;
            wU[xu] = l; if (rU[xu] < l) rU[xu] = l;
            if (rU[yu] < l) rU[yu] = l;
            if (rV[xv] < l) rV[xv] = l;
            wV[yv] = l;
            if (l > nlev) nlev = l;
        }
    }
    free(wU); free(rU); free(wV); free(rV);

    if (ok) {
        off = (long *)calloc((size_t)nlev + 1, sizeof(long));
        cur = (long *)malloc((size_t)(nlev > 0 ? nlev : 1) * sizeof(long));
        perm = (long *)malloc((size_t)(n > 1 ? n - 1 : 1) * sizeof(long));
        ok = (off != NULL) && (cur != NULL) && (perm != NULL);
    }
    if (ok) {
        /* counting sort of iterations by level, stable in i */
        for (long i = 1; i < n; i++) off[lev[i]]++;
        long s = 0;
        for (int l = 1; l <= nlev; l++) {
            long cnt = off[l];
            off[l - 1] = s;
            cur[l - 1] = s;
            s += cnt;
        }
        off[nlev] = s;
        for (long i = 1; i < n; i++) {
            long p = cur[lev[i] - 1]++;
            perm[p] = i;
        }
    }
    free(lev); free(cur);

    /* ---------------------------------------------------------------
     * Executor: the repetitions stay in order; inside each, levels run
     * in order and the iterations of a level run in parallel.
     * --------------------------------------------------------------- */
    for (int nl = 0; nl < R; nl++) {
        if (ok) {
            for (int l = 0; l < nlev; l++) {
                long lo = off[l], hi = off[l + 1];
                if (hi - lo < K48_PAR_MIN) {
                    for (long p = lo; p < hi; p++) k48_iter(perm[p]);
                } else {
                    #pragma omp parallel for firstprivate(lo, hi) shared(perm)
                    for (long p = lo; p < hi; p++) {
                        k48_iter(perm[p]);
                    }
                }
            }
        } else {
            /* allocation failed: original sequential loop */
            for (long i = 1; i < n; i++) k48_iter(i);
        }
        pb_mix(nl);
    }

    free(off); free(perm);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
