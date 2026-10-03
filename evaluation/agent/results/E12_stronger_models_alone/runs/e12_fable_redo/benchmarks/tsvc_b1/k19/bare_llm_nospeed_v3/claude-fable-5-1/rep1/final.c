/* Kernel k19. */
#include "tsvc_b1/k19.h"
#include <stdlib.h>

#if defined(LEN_1D) && (LEN_1D) < 1000000000
typedef int k19_idx_t;
#else
typedef long k19_idx_t;
#endif

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
    const long cnt = (n > 1) ? (n - 1) : 0;   /* iterations i = 1 .. n-1 */

    /* Index range touched by ju/jv/ku/kv (they are constant inside the kernel). */
    long mn = 0, mx = -1;
    if (cnt > 0) {
        mn = (long)ju[1];
        mx = (long)ju[1];
#pragma omp parallel for reduction(min:mn) reduction(max:mx)
        for (long i = 1; i < n; i++) {
            long x0 = (long)ju[i], x1 = (long)jv[i], x2 = (long)ku[i], x3 = (long)kv[i];
            if (x0 < mn) mn = x0;
            if (x0 > mx) mx = x0;
            if (x1 < mn) mn = x1;
            if (x1 > mx) mx = x1;
            if (x2 < mn) mn = x2;
            if (x2 > mx) mx = x2;
            if (x3 < mn) mn = x3;
            if (x3 > mx) mx = x3;
        }
    }
    const long m = (cnt > 0) ? (mx - mn + 1) : 1;

    /* Inspector tables (sizes grow with the problem -> heap). */
    k19_idx_t *Lu = (k19_idx_t *)calloc((size_t)m, sizeof(k19_idx_t));   /* level of last writer of u[x] (0: none) */
    k19_idx_t *Lv = (k19_idx_t *)calloc((size_t)m, sizeof(k19_idx_t));
    k19_idx_t *Wu = (k19_idx_t *)malloc((size_t)m * sizeof(k19_idx_t));  /* last writer iteration of u[x] (-1: none) */
    k19_idx_t *Wv = (k19_idx_t *)malloc((size_t)m * sizeof(k19_idx_t));
    k19_idx_t *pu = (k19_idx_t *)malloc((size_t)n * sizeof(k19_idx_t));  /* producer of old u[ju[i]] */
    k19_idx_t *rv = (k19_idx_t *)malloc((size_t)n * sizeof(k19_idx_t));  /* producer of v[kv[i]] */
    k19_idx_t *ru = (k19_idx_t *)malloc((size_t)n * sizeof(k19_idx_t));  /* producer of u[ku[i]] */
    k19_idx_t *l1 = (k19_idx_t *)malloc((size_t)n * sizeof(k19_idx_t));  /* level of statement 1 of i */
    k19_idx_t *l2 = (k19_idx_t *)malloc((size_t)n * sizeof(k19_idx_t));  /* level of statement 2 of i */
    real_t *wu = (real_t *)malloc((size_t)n * sizeof(real_t));           /* slot: value written to u by i */
    real_t *wv = (real_t *)malloc((size_t)n * sizeof(real_t));           /* slot: value written to v by i */
    unsigned char *lastU = (unsigned char *)malloc((size_t)n);           /* i is final writer of u[ju[i]] */
    unsigned char *lastV = (unsigned char *)malloc((size_t)n);           /* i is final writer of v[jv[i]] */
    k19_idx_t *order = (k19_idx_t *)malloc((size_t)(2 * cnt + 1) * sizeof(k19_idx_t));
    long *off = NULL;
    long nlev = 0;

    int ok = (Lu && Lv && Wu && Wv && pu && rv && ru && l1 && l2 && wu && wv && lastU && lastV && order);

    if (ok) {
        for (long x = 0; x < m; x++) { Wu[x] = (k19_idx_t)-1; Wv[x] = (k19_idx_t)-1; }

        /* Sequential dependence inspection: who produces each operand, and at which level. */
        for (long i = 1; i < n; i++) {
            long a0 = (long)ju[i] - mn;
            long a1 = (long)jv[i] - mn;
            long a2 = (long)ku[i] - mn;
            long a3 = (long)kv[i] - mn;
            /* S1: u[ju[i]] = u[ju[i]] + v[kv[i]] * c[i] */
            k19_idx_t lv1 = (Lv[a3] > Lu[a0]) ? Lv[a3] : Lu[a0];
            lv1 = lv1 + 1;
            rv[i] = Wv[a3];
            pu[i] = Wu[a0];
            l1[i] = lv1;
            Lu[a0] = lv1;
            Wu[a0] = (k19_idx_t)i;
            /* S2: v[jv[i]] = u[ku[i]] * d[i] + c[i] */
            ru[i] = Wu[a2];
            k19_idx_t lv2 = Lu[a2] + 1;
            l2[i] = lv2;
            Lv[a1] = lv2;
            Wv[a1] = (k19_idx_t)i;
            if ((long)lv1 > nlev) nlev = (long)lv1;
            if ((long)lv2 > nlev) nlev = (long)lv2;
        }

        /* Final-writer flags. */
#pragma omp parallel for shared(lastU, lastV, Wu, Wv, mn)
        for (long i = 1; i < n; i++) {
            lastU[i] = (Wu[(long)ju[i] - mn] == (k19_idx_t)i) ? 1 : 0;
            lastV[i] = (Wv[(long)jv[i] - mn] == (k19_idx_t)i) ? 1 : 0;
        }

        free(Lu); Lu = NULL;
        free(Lv); Lv = NULL;
        free(Wu); Wu = NULL;
        free(Wv); Wv = NULL;

        off = (long *)calloc((size_t)(nlev + 1), sizeof(long));
        ok = (off != NULL);
    }

    if (ok) {
        /* Counting sort of statement instances by level; item = 2*i + stmt. */
        for (long i = 1; i < n; i++) { off[l1[i]]++; off[l2[i]]++; }
        {
            long s = 0;
            for (long L = 1; L <= nlev; L++) { long cL = off[L]; off[L] = s; s += cL; }
            off[0] = 0;
        }
        for (long i = 1; i < n; i++) {
            order[off[l1[i]]++] = (k19_idx_t)(2 * i);
            order[off[l2[i]]++] = (k19_idx_t)(2 * i + 1);
        }
        /* now level L occupies [off[L-1], off[L]) */
        free(l1); l1 = NULL;
        free(l2); l2 = NULL;
    }

    for (int nl = 0; nl < R; nl++) {
        if (ok) {
            for (long L = 1; L <= nlev; L++) {
                const long lo = off[L - 1];
                const long hi = off[L];
#pragma omp parallel for shared(lo, hi, order, pu, rv, ru, wu, wv) if(hi - lo >= 1024)
                for (long t = lo; t < hi; t++) {
                    k19_idx_t item = order[t];
                    long i = (long)(item >> 1);
                    if ((item & 1) == 0) {
                        real_t uprev = (pu[i] < 0) ? u[ju[i]] : wu[pu[i]];
                        real_t vval  = (rv[i] < 0) ? v[kv[i]] : wv[rv[i]];
                        wu[i] = uprev + vval * c[i];
                    } else {
                        real_t uval = (ru[i] < 0) ? u[ku[i]] : wu[ru[i]];
                        wv[i] = uval * d[i] + c[i];
                    }
                }
            }
            /* Write back final values: distinct i with a flag set target distinct locations. */
#pragma omp parallel for shared(lastU, lastV, wu, wv)
            for (long i = 1; i < n; i++) {
                if (lastU[i]) u[ju[i]] = wu[i];
                if (lastV[i]) v[jv[i]] = wv[i];
            }
        } else {
            /* Allocation failure: original sequential computation. */
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(Lu); free(Lv); free(Wu); free(Wv);
    free(pu); free(rv); free(ru); free(l1); free(l2);
    free(wu); free(wv); free(lastU); free(lastV); free(order); free(off);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
