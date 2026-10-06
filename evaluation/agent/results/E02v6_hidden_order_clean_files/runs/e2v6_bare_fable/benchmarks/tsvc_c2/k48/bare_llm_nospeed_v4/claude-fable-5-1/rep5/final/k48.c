#include "data.h"
#include <stdlib.h>

real_t kernel_k48(void)
{
    /*
     * Inspector (run once: ju/jv/ku/kv are never modified by this program).
     * Decide whether the original i-loop can be split exactly into two
     * independent sweeps:
     *      sweep 1:  u[ju[i]] += v[kv[i]] * c[i]          (all i)
     *      sweep 2:  v[jv[i]]  = u[ku[i]] * d[i] + c[i]   (all i)
     * This is exact iff
     *   (A) no sweep-1 read of v[kv[i]] sees a v cell that an EARLIER
     *       iteration writes            -> firstV[kv[i]] >= i
     *   (B) no sweep-2 read of u[ku[i]] sees a u cell that a LATER
     *       iteration updates           -> lastU[ku[i]]  <= i
     *   (C) ju is injective, so every u cell receives exactly one update
     *       (otherwise the FP accumulation order would matter)
     * Duplicate jv entries are handled exactly: only the last writer of a
     * v cell (lastV[jv[i]] == i) performs the store.
     */
    long *lastU  = (long *)malloc(sizeof(long) * (size_t)LEN_1D);
    long *firstV = (long *)malloc(sizeof(long) * (size_t)LEN_1D);
    long *lastV  = (long *)malloc(sizeof(long) * (size_t)LEN_1D);
    int safe = (lastU != NULL && firstV != NULL && lastV != NULL);

    if (safe) {
        for (long k = 0; k < LEN_1D; k++) {
            lastU[k]  = -1;
            firstV[k] = LEN_1D;
            lastV[k]  = -1;
        }
        for (long i = 1; i < LEN_1D && safe; i++) {
            long a1 = ju[i], a2 = jv[i], a3 = ku[i], a4 = kv[i];
            if (a1 < 0 || a1 >= LEN_1D || a2 < 0 || a2 >= LEN_1D ||
                a3 < 0 || a3 >= LEN_1D || a4 < 0 || a4 >= LEN_1D) {
                safe = 0;
            } else {
                if (lastU[a1] != -1) safe = 0;      /* ju not injective (C) */
                lastU[a1] = i;
                if (firstV[a2] == LEN_1D) firstV[a2] = i;
                lastV[a2] = i;
            }
        }
    }

    if (safe) {
        long bad = 0;
        #pragma omp parallel for shared(ku, kv, firstV, lastU) reduction(+:bad)
        for (long i = 1; i < LEN_1D; i++) {
            if (firstV[kv[i]] < i) bad++;           /* violates (A) */
            if (lastU[ku[i]] > i)  bad++;           /* violates (B) */
        }
        if (bad != 0) safe = 0;
    }

    for (int nl = 0; nl < iterations; nl++) {
        if (safe) {
            /* sweep 1: ju injective -> each iteration updates a distinct u cell;
               v and c are only read. */
            #pragma omp parallel for shared(u, v, c, ju, kv)
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
            }
            /* sweep 2: only the last writer of each v cell stores ->
               distinct write locations; u, c, d, lastV are only read. */
            #pragma omp parallel for shared(u, v, c, d, jv, ku, lastV)
            for (long i = 1; i < LEN_1D; i++) {
                if (lastV[jv[i]] == i) {
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
            }
        } else {
            /* index pattern carries a true recurrence: keep the serial order */
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(lastU);
    free(firstV);
    free(lastV);
    return (real_t)0;
}
