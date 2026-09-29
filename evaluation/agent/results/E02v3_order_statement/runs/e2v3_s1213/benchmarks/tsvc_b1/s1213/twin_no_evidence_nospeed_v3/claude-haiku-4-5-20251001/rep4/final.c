/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"

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

static real_t kernel_s1213(void)
{
    real_t* b_new = malloc(LEN_1D * sizeof(real_t));
    real_t* a_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        // Copy b and a to temporary buffers
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            b_new[i] = b[i];
            a_new[i] = a[i];
        }

        // Compute new b values (can be parallelized)
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = a[i+1] * d[i];
        }

        // Compute new a values (can be parallelized)
        #pragma omp parallel for shared(a_new,b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            a_new[i] = b_new[i-1] + c[i];
        }

        // Copy results back
        #pragma omp parallel for shared(a_new,b_new) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a_new[i];
            b[i] = b_new[i];
        }

        pb_mix(nl);
    }

    free(a_new);
    free(b_new);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
