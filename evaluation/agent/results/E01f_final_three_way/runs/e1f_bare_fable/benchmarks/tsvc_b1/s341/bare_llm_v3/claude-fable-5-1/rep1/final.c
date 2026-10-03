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

static real_t kernel_s341(void)
{
    int j;
    long cnt[S341_NB + 1];
    const long chunk = ((long)LEN_1D + S341_NB - 1) / S341_NB;
    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: count positives per block (independent blocks). */
#pragma omp parallel for schedule(static) shared(b, cnt) firstprivate(chunk)
        for (int c = 0; c < S341_NB; c++) {
            long start = (long)c * chunk;
            long end = start + chunk;
            if (end > (long)LEN_1D) end = (long)LEN_1D;
            long n = 0;
            for (long i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    n++;
                }
            }
            cnt[c] = n;
        }
        /* Exclusive scan: cnt[c] becomes the output offset of block c. */
        {
            long run = 0;
            for (int c = 0; c < S341_NB; c++) {
                long t = cnt[c];
                cnt[c] = run;
                run += t;
            }
            cnt[S341_NB] = run;
        }
        /* Pass 2: each block writes its positives to its own disjoint range of a. */
#pragma omp parallel for schedule(static) shared(a, b, cnt) firstprivate(chunk)
        for (int c = 0; c < S341_NB; c++) {
            long start = (long)c * chunk;
            long end = start + chunk;
            if (end > (long)LEN_1D) end = (long)LEN_1D;
            long pos = cnt[c];
            for (long i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    a[pos] = b[i];
                    pos++;
                }
            }
        }
        j = (int)cnt[S341_NB] - 1;
        pb_mix(nl);
    }
    (void)j;
    return (real_t)0;
}

PB_MAIN(kernel_s341)
