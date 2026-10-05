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
    real_t *a_save = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *b_save = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        memcpy(a_save, a, LEN_1D * sizeof(real_t));
        memcpy(b_save, b, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; i++) {
                if (a_save[i] >= (real_t)0.) {
                    goto L20;
                }
                if (b_save[i] >= (real_t)0.) {
                    goto L30;
                }
                a[i] += c[i] * d[i];
L30:
                b[i+1] = c[i] + d[i] * e[i];
L20:
;
        }
        pb_mix(nl);
    }

    free(a_save);
    free(b_save);

    return (real_t)0;
}

PB_MAIN(kernel_s277)
