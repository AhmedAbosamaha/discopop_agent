/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"
#ifdef _OPENMP
#include <omp.h>
#endif

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

/* The inner loop is a stream compaction: j is a running output index that only ever
 * advances, so a[j] for the k-th positive b[i] (in increasing i order) depends on how
 * many earlier elements were positive. That is a value (the count-so-far) moving
 * between iterations, not just a reused location, so a straight "parallel for" would
 * race on j and could also scramble which a[] slot each b[i] lands in.
 *
 * We remove the dependence by splitting the single running count into two phases:
 *   1. Divide the index range into NB independent blocks. Each block counts its own
 *      positives with a private sequential scan -> blockCount[blk]. Blocks don't
 *      touch each other's data, so this pass is embarrassingly parallel.
 *   2. Turn the per-block counts into per-block starting offsets with an exclusive
 *      prefix sum. This is the only part of the original dependence that survives,
 *      but it now runs over NB (a small, thread-count-sized) values instead of over
 *      LEN_1D, so it stays O(LEN_1D) overall while being negligible in practice.
 *   3. Re-scan each block, now starting its local counter at blockOffset[blk] instead
 *      of 0. Every block writes into its own disjoint slice of a[], so the writes may
 *      run in any order/interleaving and still reproduce exactly the same a[] values,
 *      in exactly the same order, that the original running counter produced -
 *      including leaving a[] untouched past the last written slot.
 * NB is sized off the thread count purely for load balance; correctness does not
 * depend on it, so querying omp_get_max_threads() here is only a tuning choice.
 */
static real_t kernel_s341(void)
{
    enum { MAX_BLOCKS = 4096 };
    int blockCount[MAX_BLOCKS];
    int blockOffset[MAX_BLOCKS];

    int nthreads = 1;
#ifdef _OPENMP
    nthreads = omp_get_max_threads();
    if (nthreads < 1) nthreads = 1;
#endif
    int NB = nthreads * 4;
    if (NB > LEN_1D) NB = LEN_1D;
    if (NB < 1) NB = 1;
    if (NB > MAX_BLOCKS) NB = MAX_BLOCKS;
    int blockSize = (LEN_1D + NB - 1) / NB;

    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: count positives per block independently; no cross-block state. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(b, blockCount, NB, blockSize)
        for (int blk = 0; blk < NB; blk++) {
            int start = blk * blockSize;
            int end = start + blockSize;
            if (end > LEN_1D) end = LEN_1D;
            int cnt = 0;
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) cnt++;
            }
            blockCount[blk] = cnt;
        }

        /* Sequential exclusive prefix sum over the NB block counts: this carries the
         * "how many positives came before" value across blocks, the one dependence
         * that is real, now over NB elements instead of LEN_1D. */
        blockOffset[0] = 0;
        for (int blk = 1; blk < NB; blk++) {
            blockOffset[blk] = blockOffset[blk - 1] + blockCount[blk - 1];
        }

        /* Pass 2: each block writes its compacted elements starting at its own
         * precomputed offset, so blocks no longer depend on each other here. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(a, b, blockOffset, NB, blockSize)
        for (int blk = 0; blk < NB; blk++) {
            int start = blk * blockSize;
            int end = start + blockSize;
            if (end > LEN_1D) end = LEN_1D;
            int j = blockOffset[blk];
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    a[j] = b[i];
                    j++;
                }
            }
        }

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
