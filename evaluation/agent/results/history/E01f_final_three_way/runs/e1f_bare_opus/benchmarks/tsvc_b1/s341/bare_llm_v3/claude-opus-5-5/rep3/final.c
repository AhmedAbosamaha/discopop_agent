/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

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

#define S341_NB 256
static long s341_cnt[S341_NB];
static long s341_off[S341_NB];

static real_t kernel_s341(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for schedule(static) shared(s341_cnt)
        for (int t = 0; t < S341_NB; t++) {
            long lo = (long)LEN_1D * t / S341_NB;
            long hi = (long)LEN_1D * (t + 1) / S341_NB;
            long c = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c++;
                }
            }
            s341_cnt[t] = c;
        }
        /* exclusive scan of block counts (serial, S341_NB elements) */
        long run = 0;
        for (int t = 0; t < S341_NB; t++) {
            s341_off[t] = run;
            run += s341_cnt[t];
        }
        /* pass 2: each block compacts into its own disjoint range of a */
        #pragma omp parallel for schedule(static) shared(s341_off)
        for (int t = 0; t < S341_NB; t++) {
            long lo = (long)LEN_1D * t / S341_NB;
            long hi = (long)LEN_1D * (t + 1) / S341_NB;
            long j = s341_off[t] - 1;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    j++;
                    a[j] = b[i];
                }
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
