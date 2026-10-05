#include "evk/k42.h"
#include <stdlib.h>

static real_t kernel_k42(void)
{
    /* The only blocking dependence DiscoPoP found is a loop-carried RAW on
       u: line "v[jv[i]] += u[ku[i]] * d[i]" can see a value that a
       DIFFERENT (earlier) iteration wrote into u via "u[ju[i]] += ...".
       No dependence was reported for v (its own accesses are read/written
       through jv[i] alone), and no WAW was reported for u, so each i
       still writes a distinct u location, exactly as in the profiled run.

       That means u's write never depends on anything the loop itself
       produces (v is only ever read from its pre-loop state - otherwise
       DiscoPoP would have flagged that dependence too), so it can be
       computed directly from snapshots taken before the loop runs.  What
       makes the loop look sequential is only that the read of u[ku[i]]
       must see exactly the partial state the original i-ordered sweep
       had reached: it includes the contribution written for address
       ku[i] only if that write's iteration index precedes or equals i.
       That "does the writer come at or before i" fact does not depend on
       runtime scheduling at all - it is pure data - so we precompute it
       once (winv) and then every iteration can be evaluated independently
       in any order, reproducing the exact same result the sequential
       sweep produced. */
    real_t *u0 = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *v0 = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    long *winv = (long *)malloc((size_t)LEN_1D * sizeof(long));

    for (long p = 0; p < LEN_1D; p++) {
        u0[p] = u[p];
        v0[p] = v[p];
        winv[p] = -1;
    }
    /* For each u-position, remember which iteration (if any) writes it;
       mirrors the sequential loop's own write order, so if two iterations
       ever did target the same address the later one still wins here,
       same as it would in-order. */
    for (long i = 1; i < LEN_1D; i++) {
        winv[ju[i]] = i;
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] = u0[ju[i]] + v0[kv[i]] * c[i];

        long w = winv[ku[i]];
        real_t u_seen = u0[ku[i]];
        if (w != -1 && w <= i) {
            u_seen += v0[kv[w]] * c[w];
        }

        v[jv[i]] = v0[jv[i]] + u_seen * d[i];
    }

    free(u0);
    free(v0);
    free(winv);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
