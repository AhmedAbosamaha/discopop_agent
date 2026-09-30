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

#define K48_MAX(x, y) ((x) > (y) ? (x) : (y))

static real_t kernel_k48(void)
{
    const long n = (long)LEN_1D;

    /* ---- inspector: one sequential pass over the (constant) index arrays ----
     * Iteration i is given the smallest level strictly above every earlier
     * iteration it conflicts with (RAW, WAR or WAW on u or v).  Iterations in
     * the same level therefore never touch a common location with a write, and
     * for every location the level order equals the original program order. */
    long maxidx = 0;
    for (long i = 1; i < n; i++) {
        long t;
        t = (long)ju[i]; maxidx = K48_MAX(maxidx, t);
        t = (long)jv[i]; maxidx = K48_MAX(maxidx, t);
        t = (long)ku[i]; maxidx = K48_MAX(maxidx, t);
        t = (long)kv[i]; maxidx = K48_MAX(maxidx, t);
    }
    const long nloc = maxidx + 1;

    int  *lastWu = (int *)malloc((size_t)nloc * sizeof(int));
    int  *lastRu = (int *)malloc((size_t)nloc * sizeof(int));
    int  *lastWv = (int *)malloc((size_t)nloc * sizeof(int));
    int  *lastRv = (int *)malloc((size_t)nloc * sizeof(int));
    int  *level  = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));
    long *order  = (long *)malloc((size_t)(n > 0 ? n : 1) * sizeof(long));

    if (!lastWu || !lastRu || !lastWv || !lastRv || !level || !order) {
        /* allocation failed: fall back to the original sequential schedule */
        free(lastWu); free(lastRu); free(lastWv); free(lastRv); free(level); free(order);
        for (int nl = 0; nl < R; nl++) {
            for (long i = 1; i < n; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            pb_mix(nl);
        }
        return (real_t)0;
    }

    for (long l = 0; l < nloc; l++) {
        lastWu[l] = -1; lastRu[l] = -1; lastWv[l] = -1; lastRv[l] = -1;
    }

    int nlev = 0;
    for (long i = 1; i < n; i++) {
        long wu = (long)ju[i];   /* u[wu] read+written */
        long ru = (long)ku[i];   /* u[ru] read          */
        long rv = (long)kv[i];   /* v[rv] read          */
        long wv = (long)jv[i];   /* v[wv] written       */
        int lvl = 0;
        lvl = K48_MAX(lvl, lastWv[rv] + 1);                 /* RAW on v */
        lvl = K48_MAX(lvl, lastWu[ru] + 1);                 /* RAW on u */
        lvl = K48_MAX(lvl, lastWu[wu] + 1);                 /* RAW/WAW on u */
        lvl = K48_MAX(lvl, lastRu[wu] + 1);                 /* WAR on u */
        lvl = K48_MAX(lvl, lastWv[wv] + 1);                 /* WAW on v */
        lvl = K48_MAX(lvl, lastRv[wv] + 1);                 /* WAR on v */
        lastRv[rv] = K48_MAX(lastRv[rv], lvl);
        lastRu[ru] = K48_MAX(lastRu[ru], lvl);
        lastWu[wu] = lvl;
        lastWv[wv] = lvl;
        level[i] = lvl;
        if (lvl + 1 > nlev) nlev = lvl + 1;
    }
    free(lastWu); free(lastRu); free(lastWv); free(lastRv);

    /* counting sort of the iterations by level (stable: original order kept inside a level) */
    long *start = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
    if (!start) {
        free(level); free(order);
        for (int nl = 0; nl < R; nl++) {
            for (long i = 1; i < n; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            pb_mix(nl);
        }
        return (real_t)0;
    }
    for (int l = 0; l <= nlev + 1; l++) start[l] = 0;
    for (long i = 1; i < n; i++) start[level[i] + 2]++;
    for (int l = 0; l < nlev; l++) start[l + 2] += start[l + 1];
    for (long i = 1; i < n; i++) order[start[level[i] + 1]++] = i;
    /* now start[l] .. start[l+1]-1 are the positions of level l in order[] */
    free(level);

    /* ---- executor ---- */
    for (int nl = 0; nl < R; nl++) {
        for (int l = 0; l < nlev; l++) {
            const long s = start[l];
            const long e = start[l + 1];
#pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) firstprivate(s, e) schedule(static) if (e - s > 32)
            for (long p = s; p < e; p++) {
                const long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(start);
    free(order);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
