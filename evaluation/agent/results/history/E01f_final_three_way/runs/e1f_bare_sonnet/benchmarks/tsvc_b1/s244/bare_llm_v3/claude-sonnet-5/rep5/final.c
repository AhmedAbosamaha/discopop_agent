/* TSVC-2 loop s244, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s244.h"

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

static real_t kernel_s244(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* a[i+1] written here by each iteration i < n-1 is always overwritten by
         * iteration i+1's write to a[i+1] (the "a[i]=..." statement), so it is dead
         * except for the final iteration i = n-1, whose write to a[n] survives.
         * Drop the dead write from the parallel loop (each iteration then touches
         * only its own index i) and apply the one surviving write afterward, using
         * the final b[n-1] produced by the loop and the original a[n] it never
         * touches. */
        int n = LEN_1D - 1;
        #pragma omp parallel for default(none) shared(a, b, c, d) firstprivate(n)
        for (int i = 0; i < n; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        if (n > 0) {
            a[n] = b[n-1] + a[n] * d[n-1];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s244)
