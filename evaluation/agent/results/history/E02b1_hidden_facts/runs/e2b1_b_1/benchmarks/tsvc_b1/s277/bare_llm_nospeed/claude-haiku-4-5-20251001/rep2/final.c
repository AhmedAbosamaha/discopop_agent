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
        /* Pass 1: Even iterations process indices 0,2,4,...
           These write to b[1],b[3],b[5],... and update a[0],a[2],a[4],...
           No dependencies between even iterations. */
        #pragma omp parallel for schedule(static) shared(a,b,c,d,e) private(i)
        for (int i = 0; i < LEN_1D-1; i += 2) {
                if (a[i] >= (real_t)0.) {
                    goto L20_even;
                }
                if (b[i] >= (real_t)0.) {
                    goto L30_even;
                }
                a[i] += c[i] * d[i];
L30_even:
                b[i+1] = c[i] + d[i] * e[i];
L20_even:
;
        }

        /* Pass 2: Odd iterations process indices 1,3,5,...
           These read b[1],b[3],b[5],... (written by Pass 1)
           and write to b[2],b[4],b[6],... and update a[1],a[3],a[5],...
           No dependencies between odd iterations. */
        #pragma omp parallel for schedule(static) shared(a,b,c,d,e) private(i)
        for (int i = 1; i < LEN_1D-1; i += 2) {
                if (a[i] >= (real_t)0.) {
                    goto L20_odd;
                }
                if (b[i] >= (real_t)0.) {
                    goto L30_odd;
                }
                a[i] += c[i] * d[i];
L30_odd:
                b[i+1] = c[i] + d[i] * e[i];
L20_odd:
;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
