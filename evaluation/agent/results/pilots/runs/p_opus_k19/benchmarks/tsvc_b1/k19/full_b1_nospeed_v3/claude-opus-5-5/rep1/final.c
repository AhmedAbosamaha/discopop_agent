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
    /* Inspector: index arrays are invariant, so schedule iterations into
     * conflict-free levels once (dependence order between conflicting
     * iterations is preserved; iterations within a level are independent). */
    long nu = 1, nv = 1;
    for (long i = 1; i < LEN_1D; i++) {
        long x;
        x = (long)ju[i] + 1; if (x > nu) nu = x;
        x = (long)ku[i] + 1; if (x > nu) nu = x;
        x = (long)kv[i] + 1; if (x > nv) nv = x;
        x = (long)jv[i] + 1; if (x > nv) nv = x;
    }
    int *wU = (int *)calloc((size_t)nu, sizeof(int));
    int *rU = (int *)calloc((size_t)nu, sizeof(int));
    int *wV = (int *)calloc((size_t)nv, sizeof(int));
    int *rV = (int *)calloc((size_t)nv, sizeof(int));
    int *lev = (int *)malloc((size_t)LEN_1D * sizeof(int));
    long nlev = 0;
    for (long i = 1; i < LEN_1D; i++) {
        long uj = (long)ju[i], uk = (long)ku[i];
        long vk = (long)kv[i], vj = (long)jv[i];
        int lv = 0;
        if (wU[uj] > lv) lv = wU[uj];
        if (rU[uj] > lv) lv = rU[uj];
        if (wU[uk] > lv) lv = wU[uk];
        if (wV[vk] > lv) lv = wV[vk];
        if (wV[vj] > lv) lv = wV[vj];
        if (rV[vj] > lv) lv = rV[vj];
        lev[i] = lv;
        int nx = lv + 1;
        wU[uj] = nx;
        if (rU[uj] < nx) rU[uj] = nx;
        if (rU[uk] < nx) rU[uk] = nx;
        if (rV[vk] < nx) rV[vk] = nx;
        wV[vj] = nx;
        if ((long)nx > nlev) nlev = nx;
    }
    free(wU); free(rU); free(wV); free(rV);
    long *off = (long *)calloc((size_t)(nlev + 1), sizeof(long));
    long *order = (long *)malloc((size_t)LEN_1D * sizeof(long));
    for (long i = 1; i < LEN_1D; i++)
        off[lev[i] + 1]++;
    for (long L = 0; L < nlev; L++)
        off[L + 1] += off[L];
    {
        long *pos = (long *)malloc((size_t)(nlev + 1) * sizeof(long));
        for (long L = 0; L <= nlev; L++)
            pos[L] = off[L];
        for (long i = 1; i < LEN_1D; i++)
            order[pos[lev[i]]++] = i;
        free(pos);
    }
    free(lev);

    /* Executor */
    for (int nl = 0; nl < R; nl++) {
        for (long L = 0; L < nlev; L++) {
            long s = off[L];
            long e = off[L + 1];
 #pragma omp parallel for firstprivate(s,e) shared(order) 
            for (long t = s; t < e; t++) {
                long i = order[t];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(off);
    free(order);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
