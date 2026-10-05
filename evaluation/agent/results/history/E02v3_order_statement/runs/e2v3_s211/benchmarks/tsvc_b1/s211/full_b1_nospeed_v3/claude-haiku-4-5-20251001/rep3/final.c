/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s211.h"

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

static real_t kernel_s211(void)
{
    for (int nl = 0; nl < R; nl++) {
        real_t *b_save = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(b_save, b, LEN_1D * sizeof(real_t));
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_save[i + 1] - e[i] * d[i];
        }
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }
        free(b_save);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s211)
