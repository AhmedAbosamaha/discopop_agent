/* TSVC-2 loop s161, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s161.h"

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

static real_t kernel_s161(void)
{
    int *c_updated = (int *)malloc(LEN_1D * sizeof(int));
    real_t *c_new_values = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        memset(c_updated, 0, LEN_1D * sizeof(int));

        // Phase 1: Collect all updates to c
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c_new_values[i+1] = a[i] + d[i] * d[i];
                c_updated[i+1] = 1;
            }
        }

        // Phase 2: Apply c updates and compute a values
        #pragma omp parallel for shared(c_updated,c_new_values) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (c_updated[i]) {
                c[i] = c_new_values[i];
            }
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        pb_mix(nl);
    }

    free(c_updated);
    free(c_new_values);
    return (real_t)0;
}

PB_MAIN(kernel_s161)
