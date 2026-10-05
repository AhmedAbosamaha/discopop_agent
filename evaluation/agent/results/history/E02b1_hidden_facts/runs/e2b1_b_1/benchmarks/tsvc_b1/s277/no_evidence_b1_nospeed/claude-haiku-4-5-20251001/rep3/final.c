/* TSVC-2 loop s277, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s277.h"

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

static real_t kernel_s277(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Create temporary buffer for new b values */
        real_t *b_new = malloc(LEN_1D * sizeof(real_t));
        memcpy(b_new, b, LEN_1D * sizeof(real_t));

        /* First pass: compute all b[i+1] values independently based on a[i] */
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] < (real_t)0.) {
                    b_new[i+1] = c[i] + d[i] * e[i];
                }
        }

        /* Second pass: update a[i] values using the pre-computed b_new values */
        #pragma omp parallel for shared(b_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] >= (real_t)0.) {
                    /* Skip: a[i] is non-negative */
                } else if (b_new[i] >= (real_t)0.) {
                    /* Skip: b[i] is non-negative */
                } else {
                    /* Both a[i] and b[i] are negative */
                    a[i] += c[i] * d[i];
                }
        }

        /* Copy computed b values back to b */
        memcpy(b, b_new, LEN_1D * sizeof(real_t));
        free(b_new);

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
