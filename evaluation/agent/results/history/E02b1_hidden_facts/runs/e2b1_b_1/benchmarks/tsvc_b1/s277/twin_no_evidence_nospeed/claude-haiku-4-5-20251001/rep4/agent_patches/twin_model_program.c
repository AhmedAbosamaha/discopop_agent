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
        // Create snapshot of original b to break loop-carried dependence
        real_t *b_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int j = 0; j < LEN_1D; j++) {
            b_snapshot[j] = b[j];
        }

        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] >= (real_t)0.) {
                    // skip both a and b updates
                }
                else if (b_snapshot[i] >= (real_t)0.) {
                    // skip a update, do b update
                    b[i+1] = c[i] + d[i] * e[i];
                }
                else {
                    // do both updates
                    a[i] += c[i] * d[i];
                    b[i+1] = c[i] + d[i] * e[i];
                }
        }

        free(b_snapshot);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
