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

static real_t kernel_s341(void)
{
    enum { NB = 256 };
    long cnt[NB];
    long base[NB];
    int blk;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for shared(cnt, b) schedule(static)
        for (blk = 0; blk < NB; blk++) {
            long lo = (long)blk * (long)LEN_1D / NB;
            long hi = (long)(blk + 1) * (long)LEN_1D / NB;
            long c0 = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) c0++;
            }
            cnt[blk] = c0;
        }
        /* exclusive scan: first kept element goes to a[0] (j starts at -1) */
        long run = 0;
        for (int t = 0; t < NB; t++) {
            base[t] = run;
            run += cnt[t];
        }
        /* pass 2: scatter into disjoint output ranges */
        #pragma omp parallel for shared(base, a, b) schedule(static)
        for (blk = 0; blk < NB; blk++) {
            long lo = (long)blk * (long)LEN_1D / NB;
            long hi = (long)(blk + 1) * (long)LEN_1D / NB;
            long off = base[blk];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[off] = b[i];
                    off++;
                }
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
