/* Kernel k48. */
#include "tsvc_b1/k48.h"

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

#include <stdlib.h>

static real_t kernel_k48(void)
{
    /* Inspector: the index arrays ju/jv/ku/kv never change, so build once a
     * wavefront schedule.  level[i] = 1 + max level of any earlier iteration
     * touching the same u or v element.  Iterations sharing a level touch
     * pairwise-disjoint u and v elements and may run in any order; levels run
     * in increasing order so every dependence keeps its original direction. */
    int *level = (int *)malloc(sizeof(int) * (size_t)LEN_1D);
    int *lastU = (int *)calloc((size_t)LEN_1D, sizeof(int));
    int *lastV = (int *)calloc((size_t)LEN_1D, sizeof(int));
    long *order = (long *)malloc(sizeof(long) * (size_t)LEN_1D);
    long *start = NULL;
    int L = 0;

    if (level && lastU && lastV && order) {
        for (long i = 1; i < LEN_1D; i++) {
            long iu = (long)ju[i];
            long ou = (long)ku[i];
            long iv = (long)jv[i];
            long ov = (long)kv[i];
            int m = lastU[iu];
            if (lastU[ou] > m) m = lastU[ou];
            if (lastV[iv] > m) m = lastV[iv];
            if (lastV[ov] > m) m = lastV[ov];
            m += 1;
            level[i] = m;
            lastU[iu] = m; lastU[ou] = m;
            lastV[iv] = m; lastV[ov] = m;
            if (m > L) L = m;
        }
        start = (long *)calloc((size_t)L + 2, sizeof(long));
        if (start) {
            /* counting sort of iterations by level: start[l] .. start[l+1] */
            for (long i = 1; i < LEN_1D; i++) start[level[i] + 1]++;
            for (int l = 1; l <= L + 1; l++) start[l] += start[l - 1];
            /* start[l] now holds begin of level l (levels are 1-based); use
             * level[] slots to place iterations in original order. */
            for (long i = 1; i < LEN_1D; i++) {
                int l = level[i];
                order[start[l]] = i;
                start[l]++;
            }
            /* restore begins: start[l] currently == end of level l == begin of l+1 */
            for (int l = L; l >= 1; l--) start[l] = start[l - 1];
            start[0] = 0;
        }
    }
    free(lastU);
    free(lastV);
    free(level);

    for (int nl = 0; nl < R; nl++) {
        if (start) {
            for (int l = 1; l <= L; l++) {
                long lo = start[l];
                long hi = start[l + 1];
                #pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) firstprivate(lo, hi) schedule(static)
                for (long t = lo; t < hi; t++) {
                    long i = order[t];
                    u[ju[i]] += v[kv[i]] * c[i];
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
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

PB_MAIN(kernel_k48)
