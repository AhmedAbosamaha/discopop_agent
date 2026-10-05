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

/* Inspector: decide whether the iterations of the i loop are independent.
 * They are iff
 *   - ju[] is injective on 1..LEN_1D-1 (each u cell updated by at most one iteration),
 *   - jv[] is injective on 1..LEN_1D-1 (each v cell written by at most one iteration),
 *   - u[ku[i]] is a cell no OTHER iteration updates,
 *   - v[kv[i]] is a cell no OTHER iteration writes.
 * The index arrays are never modified by the kernel (pb_mix only touches a..e),
 * so one inspection per call is enough.  Returns 1 if independent, 0 otherwise. */
static int k19_independent(void)
{
    const long n = (long)LEN_1D;
    long *ownU = (long *)malloc(sizeof(long) * (size_t)n);
    long *ownV = (long *)malloc(sizeof(long) * (size_t)n);
    int ok = 1;
    int bad = 0;

    if (ownU == NULL || ownV == NULL) {
        free(ownU);
        free(ownV);
        return 0;
    }

    for (long x = 0; x < n; x++) {
        ownU[x] = -1;
        ownV[x] = -1;
    }

    /* Owner tables; duplicates / out-of-range indices => dependent. */
    for (long i = 1; i < n; i++) {
        long wu = (long)ju[i];
        long wv = (long)jv[i];
        if (wu < 0 || wu >= n || wv < 0 || wv >= n) {
            ok = 0;
        } else if (ownU[wu] != -1 || ownV[wv] != -1) {
            ok = 0;
        } else {
            ownU[wu] = i;
            ownV[wv] = i;
        }
    }

    if (ok) {
        /* Reads must not touch a cell owned by a different iteration. */
#pragma omp parallel for shared(ownU, ownV, ku, kv) reduction(|:bad) schedule(static)
        for (long i = 1; i < n; i++) {
            long ru = (long)ku[i];
            long rv = (long)kv[i];
            if (ru < 0 || ru >= n || rv < 0 || rv >= n) {
                bad |= 1;
            } else if ((ownU[ru] != -1 && ownU[ru] != i) ||
                       (ownV[rv] != -1 && ownV[rv] != i)) {
                bad |= 1;
            }
        }
        if (bad) {
            ok = 0;
        }
    }

    free(ownU);
    free(ownV);
    return ok;
}

static real_t kernel_k19(void)
{
    const int indep = k19_independent();

    for (int nl = 0; nl < R; nl++) {
        if (indep) {
            /* Every iteration owns distinct u/v cells and reads only cells that
             * no other iteration writes: iterations are independent. */
#pragma omp parallel for shared(u, v, c, d, ju, jv, ku, kv) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        } else {
            /* Index arrays carry a real dependence: keep the original order. */
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k19)
