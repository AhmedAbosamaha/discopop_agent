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
    long j;
    const long n = (long)LEN_1D;
    const long bs = (n + S341_NB - 1) / S341_NB;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for shared(b, s341_cnt) firstprivate(n, bs) schedule(static)
        for (int blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > n) hi = n;
            long c = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c++;
                }
            }
            s341_cnt[blk] = c;
        }
        /* serial exclusive scan over block counts */
        long total = 0;
        for (int blk = 0; blk < S341_NB; blk++) {
            s341_off[blk] = total;
            total += s341_cnt[blk];
        }
        /* pass 2: scatter each block into its own range of a */
        #pragma omp parallel for shared(a, b, s341_off) firstprivate(n, bs) schedule(static)
        for (int blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > n) hi = n;
            long jj = s341_off[blk];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[jj] = b[i];
                    jj++;
                }
            }
        }
        j = total - 1;
        (void)j;
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
