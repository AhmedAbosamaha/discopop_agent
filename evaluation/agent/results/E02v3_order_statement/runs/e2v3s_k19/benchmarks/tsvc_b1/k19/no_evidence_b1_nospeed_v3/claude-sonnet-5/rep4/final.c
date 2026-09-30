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
    /* Marker buffers for the per-repetition inspector below; heap
     * allocated because LEN_1D can be very large at full verification
     * size, freed again before returning. */
    char *seen_u = (char *)malloc((size_t)LEN_1D * sizeof(char));
    char *seen_v = (char *)malloc((size_t)LEN_1D * sizeof(char));

    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for 
        for (long i = 0; i < LEN_1D; i++) {
            seen_u[i] = 0;
            seen_v[i] = 0;
        }

        /* Inspector: for this repetition, check whether every i reads
         * back exactly the u/v slot it itself just wrote (ku[i]==ju[i],
         * kv[i]==jv[i]) and that no two iterations touch the same slot.
         * When that holds, each iteration owns two private locations
         * that no other iteration can observe, so the statement pair
         * below may run in any order across i without changing the
         * result. When it does not hold, we fall back to running the
         * exact original sequential statements for this repetition, so
         * correctness never depends on this check succeeding. */
        int safe = 1;
        for (long i = 1; i < LEN_1D; i++) {
            long pu = ju[i];
            long pv = jv[i];
            if (pu != ku[i] || pv != kv[i] ||
                pu < 0 || pu >= LEN_1D || pv < 0 || pv >= LEN_1D ||
                seen_u[pu] || seen_v[pv]) {
                safe = 0;
                break;
            }
            seen_u[pu] = 1;
            seen_v[pv] = 1;
        }

        if (safe) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }

        pb_mix(nl);
    }

    free(seen_u);
    free(seen_v);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
