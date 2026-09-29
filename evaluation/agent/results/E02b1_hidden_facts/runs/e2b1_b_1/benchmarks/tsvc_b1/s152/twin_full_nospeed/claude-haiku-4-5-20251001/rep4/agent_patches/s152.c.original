/* TSVC-2 loop s152, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s152.h"

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

void s152s(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], int i)
{
    for (int j = 0; j < LEN_1D; j++) {
        b[j] = d[j] * e[j];
    }
    for (int j = 0; j < LEN_1D; j++) {
        a[j] += b[j] * c[j];
    }
}

static real_t kernel_s152(void)
{
    for (int nl = 0; nl < R; nl++) {
        s152s(a, b, c, 0);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s152)
