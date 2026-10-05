/* TSVC-2 loop s3112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s3112.h"

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

static real_t kernel_s3112(void)
{
    enum { NB = 256 };
    real_t tot[NB];
    real_t sum = (real_t)0.0;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: per-block totals */
        #pragma omp parallel for schedule(static) shared(tot)
        for (int j = 0; j < NB; j++) {
            long lo = (long)LEN_1D * j / NB;
            long hi = (long)LEN_1D * (j + 1) / NB;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++)
                s += a[i];
            tot[j] = s;
        }
        /* exclusive scan of block totals (serial, NB steps) */
        real_t run = (real_t)0.0;
        for (int j = 0; j < NB; j++) {
            real_t t = tot[j];
            tot[j] = run;
            run += t;
        }
        /* pass 2: each block scans from its carried-in offset */
        #pragma omp parallel for schedule(static) shared(tot)
        for (int j = 0; j < NB; j++) {
            long lo = (long)LEN_1D * j / NB;
            long hi = (long)LEN_1D * (j + 1) / NB;
            real_t s = tot[j];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        sum = b[LEN_1D - 1];
        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
