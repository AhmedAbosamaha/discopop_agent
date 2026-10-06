#include <stdlib.h>
#include "data.h"

/*
 * Inspector / executor parallelization.
 *
 * The loop body reads and writes u and v through the index arrays
 * ju, jv, ku, kv, so iterations may carry true dependences through
 * memory.  The index arrays never change inside the kernel (dummy only
 * touches a..e), so we inspect them once: every iteration i gets a
 * dependence "level" such that all iterations in the same level touch
 * no common location that any of them writes, and every RAW / WAW / WAR
 * pair lies in strictly increasing levels.  Executing the levels in
 * order, with the iterations of one level in parallel, reproduces the
 * sequential result exactly (each location sees its updates in the
 * original order, and each read sees the same value as before).
 */
real_t kernel_k19(void)
{
    const long n = LEN_1D;
    const long cnt = (n > 1) ? (n - 1) : 0;   /* iterations i = 1 .. n-1 */

    /* ---------- inspector ---------- */
    long lo_u = 0, hi_u = 0, lo_v = 0, hi_v = 0;
    if (cnt > 0) {
        lo_u = hi_u = ju[1];
        lo_v = hi_v = jv[1];
        for (long i = 1; i < n; i++) {
            long a1 = ju[i], a2 = ku[i], b1 = jv[i], b2 = kv[i];
            if (a1 < lo_u) lo_u = a1;
            if (a1 > hi_u) hi_u = a1;
            if (a2 < lo_u) lo_u = a2;
            if (a2 > hi_u) hi_u = a2;
            if (b1 < lo_v) lo_v = b1;
            if (b1 > hi_v) hi_v = b1;
            if (b2 < lo_v) lo_v = b2;
            if (b2 > hi_v) hi_v = b2;
        }
    }
    const long range_u = hi_u - lo_u + 1;
    const long range_v = hi_v - lo_v + 1;

    int *uW = (int *)malloc((size_t)range_u * sizeof(int)); /* last writer level of u[x] */
    int *uR = (int *)malloc((size_t)range_u * sizeof(int)); /* last reader level of u[x] */
    int *vW = (int *)malloc((size_t)range_v * sizeof(int)); /* last writer level of v[x] */
    int *vR = (int *)malloc((size_t)range_v * sizeof(int)); /* last reader level of v[x] */
    int *level = (int *)malloc((size_t)(cnt > 0 ? cnt : 1) * sizeof(int));

    for (long x = 0; x < range_u; x++) { uW[x] = -1; uR[x] = -1; }
    for (long x = 0; x < range_v; x++) { vW[x] = -1; vR[x] = -1; }

    int maxlvl = -1;
    for (long i = 1; i < n; i++) {
        long A = ju[i] - lo_u;   /* u: read + write */
        long B = ku[i] - lo_u;   /* u: read         */
        long C = kv[i] - lo_v;   /* v: read         */
        long D = jv[i] - lo_v;   /* v: write        */
        int lvl = 0;
        int t;
        t = uW[A] + 1; if (t > lvl) lvl = t;   /* WAW / RAW on u[ju[i]] */
        t = uR[A] + 1; if (t > lvl) lvl = t;   /* WAR on u[ju[i]]       */
        t = uW[B] + 1; if (t > lvl) lvl = t;   /* RAW on u[ku[i]]       */
        t = vW[C] + 1; if (t > lvl) lvl = t;   /* RAW on v[kv[i]]       */
        t = vW[D] + 1; if (t > lvl) lvl = t;   /* WAW on v[jv[i]]       */
        t = vR[D] + 1; if (t > lvl) lvl = t;   /* WAR on v[jv[i]]       */

        uW[A] = lvl;
        if (lvl > uR[A]) uR[A] = lvl;
        if (lvl > uR[B]) uR[B] = lvl;
        if (lvl > vR[C]) vR[C] = lvl;
        vW[D] = lvl;

        level[i - 1] = lvl;
        if (lvl > maxlvl) maxlvl = lvl;
    }
    free(uW); free(uR); free(vW); free(vR);

    const int nlev = maxlvl + 1;   /* 0 when cnt == 0 */

    /* counting sort of the iterations by level (CSR layout) */
    long *off = (long *)malloc((size_t)(nlev + 1) * sizeof(long));
    long *pos = (long *)malloc((size_t)(nlev > 0 ? nlev : 1) * sizeof(long));
    int  *order = (int *)malloc((size_t)(cnt > 0 ? cnt : 1) * sizeof(int));

    for (int l = 0; l <= nlev; l++) off[l] = 0;
    for (long i = 1; i < n; i++) off[level[i - 1] + 1]++;
    for (int l = 0; l < nlev; l++) off[l + 1] += off[l];
    for (int l = 0; l < nlev; l++) pos[l] = off[l];
    for (long i = 1; i < n; i++) order[pos[level[i - 1]]++] = (int)i;

    free(pos);
    free(level);

    /* ---------- executor ---------- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int lv = 0; lv < nlev; lv++) {
            long lo = off[lv];
            long hi = off[lv + 1];
#pragma omp parallel for shared(u, v, c, d, ju, jv, ku, kv, order) firstprivate(lo, hi)
            for (long k = lo; k < hi; k++) {
                const long i = order[k];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(off);
    free(order);
    return (real_t)0;
}
