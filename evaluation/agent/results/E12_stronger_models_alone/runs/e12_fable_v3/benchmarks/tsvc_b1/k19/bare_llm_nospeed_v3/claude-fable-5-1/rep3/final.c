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
    const long n = LEN_1D;

    /* ---- Inspector: the index arrays never change, so compute once a
     * level schedule in which iterations of the same level touch pairwise
     * disjoint u/v locations, and every location is visited in its original
     * program order across levels. ---- */
    long mx = 0;
    #pragma omp parallel for reduction(max:mx)
    for (long i = 1; i < n; i++) {
        long t = ju[i]; if (t > mx) mx = t;
        t = jv[i];      if (t > mx) mx = t;
        t = ku[i];      if (t > mx) mx = t;
        t = kv[i];      if (t > mx) mx = t;
    }

    int *lastU = (int *)malloc((size_t)(mx + 1) * sizeof(int));
    int *lastV = (int *)malloc((size_t)(mx + 1) * sizeof(int));
    int *lvl   = (int *)malloc((size_t)n * sizeof(int));

    #pragma omp parallel for shared(lastU, lastV) firstprivate(mx)
    for (long j = 0; j <= mx; j++) {
        lastU[j] = 0;
        lastV[j] = 0;
    }

    int nlev = 0;
    for (long i = 1; i < n; i++) {           /* sequential: chain through lastU/lastV */
        long a1 = ju[i], a2 = ku[i], b1 = kv[i], b2 = jv[i];
        int l = lastU[a1];
        if (lastU[a2] > l) l = lastU[a2];
        if (lastV[b1] > l) l = lastV[b1];
        if (lastV[b2] > l) l = lastV[b2];
        l += 1;
        lastU[a1] = l; lastU[a2] = l; lastV[b1] = l; lastV[b2] = l;
        lvl[i] = l;
        if (l > nlev) nlev = l;
    }
    free(lastU);
    free(lastV);

    /* Counting sort of iterations by level: start[l] .. start[l+1]-1 in order[]. */
    long *start = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
    int  *order = (int *)malloc((size_t)n * sizeof(int));
    for (int l = 0; l <= nlev + 1; l++) start[l] = 0;
    for (long i = 1; i < n; i++) start[lvl[i] + 1]++;
    for (int l = 1; l <= nlev + 1; l++) start[l] += start[l - 1];
    for (long i = 1; i < n; i++) order[start[lvl[i]]++] = (int)i;
    for (int l = nlev; l >= 1; l--) start[l] = start[l - 1];
    free(lvl);

    /* ---- Executor ---- */
    for (int nl = 0; nl < R; nl++) {
        for (int l = 1; l <= nlev; l++) {
            long lo = start[l];
            long hi = start[l + 1];
            #pragma omp parallel for shared(u, v, c, d, ju, jv, ku, kv, order) firstprivate(lo, hi) if(hi - lo >= 512)
            for (long p = lo; p < hi; p++) {
                const long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(order);
    free(start);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
