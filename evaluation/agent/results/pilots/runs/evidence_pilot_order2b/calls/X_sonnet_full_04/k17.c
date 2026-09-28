#include "evk/k17.h"
#include <stdlib.h>

static real_t kernel_k17(void)
{
    const long N = LEN_1D;

    /* Inverse of jv: for a v-address, which iteration (if any) writes it
       there.  jv is injective here (no WAW was observed on v), so this
       map is well defined. */
    long *inv_jv = (long *)malloc((size_t)N * sizeof(long));
    for (long idx = 0; idx < N; idx++) {
        inv_jv[idx] = -1;
    }
    for (long i = 1; i < N; i++) {
        inv_jv[jv[i]] = i;
    }

    /* Express the value eventually written to u[ju[i]] as a linear
       function of the value written to u[ju[p]] by the unique, strictly
       earlier iteration p whose v-write is what i's v-read observes (the
       observed dependences establish p < i whenever such a p exists, and
       that no OTHER iteration's u-write is ever observed, so all reads
       below are of untouched, original u[]/v[] data). */
    long   *parent = (long *)malloc((size_t)N * sizeof(long));
    real_t *coefA  = (real_t *)malloc((size_t)N * sizeof(real_t));
    real_t *coefB  = (real_t *)malloc((size_t)N * sizeof(real_t));

    for (long i = 1; i < N; i++) {
        long p = inv_jv[kv[i]];
        if (p >= 1 && p < i && ku[p] == ju[p]) {
            parent[i] = p;
            coefA[i]  = c[i] * d[p];
            coefB[i]  = u[ju[i]] + c[i] * v[kv[i]];
        } else if (p >= 1 && p < i) {
            parent[i] = -1;
            coefA[i]  = (real_t)0;
            coefB[i]  = u[ju[i]] + c[i] * (v[kv[i]] + u[ku[p]] * d[p]);
        } else {
            parent[i] = -1;
            coefA[i]  = (real_t)0;
            coefB[i]  = u[ju[i]] + c[i] * v[kv[i]];
        }
    }

    /* Resolve U[i] = coefA[i]*U[parent[i]] + coefB[i] by pointer doubling:
       parent[i] < i always, so every chain is shorter than N and
       ceil(log2(N)) rounds fully resolve all of them.  Each round reads
       the previous round's arrays and writes fresh ones, so every round
       is an independent, per-i computation. */
    long   *parent2 = (long *)malloc((size_t)N * sizeof(long));
    real_t *coefA2  = (real_t *)malloc((size_t)N * sizeof(real_t));
    real_t *coefB2  = (real_t *)malloc((size_t)N * sizeof(real_t));

    for (long step = 1; step < N; step *= 2) {
        for (long i = 1; i < N; i++) {
            long p = parent[i];
            if (p == -1) {
                parent2[i] = -1;
                coefA2[i]  = coefA[i];
                coefB2[i]  = coefB[i];
            } else {
                parent2[i] = parent[p];
                coefA2[i]  = coefA[i] * coefA[p];
                coefB2[i]  = coefA[i] * coefB[p] + coefB[i];
            }
        }
        long   *tmp_p = parent; parent = parent2; parent2 = tmp_p;
        real_t *tmp_a = coefA;  coefA  = coefA2;  coefA2  = tmp_a;
        real_t *tmp_b = coefB;  coefB  = coefB2;  coefB2  = tmp_b;
    }

    /* v[jv[i]] is written by exactly one iteration each (jv injective), so
       this pass writes disjoint elements.  The u value it needs is either
       this iteration's own resolved result or an original u[] element
       that the writes below never touch, so reading u[] here is safe. */
    for (long i = 1; i < N; i++) {
        real_t u_at_line7 = (ku[i] == ju[i]) ? coefB[i] : u[ku[i]];
        v[jv[i]] += u_at_line7 * d[i];
    }

    /* u[ju[i]] is written by exactly one iteration each (ju injective). */
    for (long i = 1; i < N; i++) {
        u[ju[i]] = coefB[i];
    }

    free(inv_jv);
    free(parent);
    free(coefA);
    free(coefB);
    free(parent2);
    free(coefA2);
    free(coefB2);

    return (real_t)0;
}

PB_MAIN(kernel_k17)
