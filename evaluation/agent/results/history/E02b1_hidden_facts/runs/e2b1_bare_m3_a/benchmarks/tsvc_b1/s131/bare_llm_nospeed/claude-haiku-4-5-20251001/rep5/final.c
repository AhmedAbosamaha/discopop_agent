/* TSVC-2 loop s131, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s131.h"

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

static real_t kernel_s131(void)
{
    int m  = 1;
    real_t* temp = (real_t*)malloc(sizeof(real_t) * (LEN_1D - 1));
    for (int nl = 0; nl < R; nl++) {
        /* First pass: read a[i+m] and b[i] into temp[i] in parallel.
         * Each iteration i independently reads a[i+1] and b[i], writes temp[i].
         * No loop-carried dependence: iterations are independent. */
        #pragma omp parallel for schedule(static) shared(a, b, temp, m)
        for (int i = 0; i < LEN_1D - 1; i++) {
            temp[i] = a[i + m] + b[i];
        }
        /* Second pass: write temp[i] back to a[i] in parallel.
         * Each iteration i independently reads temp[i], writes a[i].
         * No dependence: temp and a write/read to distinct positions. */
        #pragma omp parallel for schedule(static) shared(a, temp)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = temp[i];
        }
        pb_mix(nl);
    }
    free(temp);
    return (real_t)0;
}

PB_MAIN(kernel_s131)
