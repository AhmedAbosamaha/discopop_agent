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
        /* Loop 1: Handle conditional logic and update to a[i].
           Each iteration i independently reads a[i], b[i], c[i], d[i]
           and possibly writes to a[i]. No loop-carried dependence. */
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] >= (real_t)0.) {
                    /* Skip both a and b updates */
                }
                else if (b[i] >= (real_t)0.) {
                    /* Skip a update, but b will be written in Loop 2 */
                }
                else {
                    a[i] += c[i] * d[i];
                }
        }

        /* Implicit barrier after Loop 1 ensures all a[i] updates are visible.
           Loop 2: Write to b[i+1] for all i where a[i] < 0.
           Each iteration i independently computes and writes b[i+1].
           No loop-carried dependence since we only write, never read b[i+1]. */
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] < (real_t)0.) {
                    b[i+1] = c[i] + d[i] * e[i];
                }
        }

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
