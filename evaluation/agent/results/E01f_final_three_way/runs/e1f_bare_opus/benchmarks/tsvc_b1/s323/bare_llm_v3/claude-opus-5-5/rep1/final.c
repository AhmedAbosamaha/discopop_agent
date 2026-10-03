/* TSVC-2 loop s323, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s323.h"
#include <stdlib.h>
#include <string.h>

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

static real_t kernel_s323(void)
{
    const long n = (long)LEN_1D;
    const long BS = 2048;
    const long nb = (n - 1 + BS - 1) / BS;   /* blocks covering i = 1 .. n-1 */
    real_t *carry = (real_t *)malloc((size_t)(nb > 0 ? nb : 1) * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* speculative incoming boundary of each block: current b[lo-1] */
#pragma omp parallel for schedule(static) shared(carry)
        for (long t = 0; t < nb; t++) {
            carry[t] = b[t * BS];
        }

        /* run every block from its speculative boundary */
#pragma omp parallel for schedule(static) shared(carry)
        for (long t = 0; t < nb; t++) {
            long lo = 1 + t * BS;
            long hi = lo + BS;
            if (hi > n) hi = n;
            real_t prev = carry[t];
            for (long i = lo; i < hi; i++) {
                a[i] = prev + c[i] * d[i];
                b[i] = a[i] + c[i] * e[i];
                prev = b[i];
            }
        }

        /* validate in order; recompute any block whose boundary guess was wrong */
        for (long t = 1; t < nb; t++) {
            long lo = 1 + t * BS;
            if (memcmp(&b[lo - 1], &carry[t], sizeof(real_t)) != 0) {
                long hi = lo + BS;
                if (hi > n) hi = n;
                for (long i = lo; i < hi; i++) {
                    a[i] = b[i-1] + c[i] * d[i];
                    b[i] = a[i] + c[i] * e[i];
                }
            }
        }
        pb_mix(nl);
    }
    free(carry);
    return (real_t)0;
}

PB_MAIN(kernel_s323)
