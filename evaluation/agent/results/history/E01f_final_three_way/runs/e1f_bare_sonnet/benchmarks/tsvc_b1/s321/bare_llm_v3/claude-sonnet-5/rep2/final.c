/* TSVC-2 loop s321, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s321.h"
#include <stdlib.h>

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

/* Cap on the number of blocks the recurrence below is split into.  Fixing this
 * independently of the thread count (instead of tying it to the number of
 * running threads) keeps the block partition - and therefore the
 * floating-point operation order - identical no matter how many threads or
 * which schedule actually execute the parallel loops below. */
#define S321_MAX_BLOCKS 256

/*
 * a[i] += a[i-1]*b[i] for i = 1..LEN_1D-1 is a first-order linear recurrence:
 * a[i] genuinely needs the value left in a[i-1] by the previous iteration, so
 * the dependence cannot be deleted, only moved.  It is moved from "every
 * element depends on its immediate predecessor" to "every block depends on
 * one scalar handed to it by the previous block", via the block-scan
 * identity
 *
 *     true[i] = local[i] + gain[i] * boundary_in
 *
 * where local[i] is what the recurrence produces inside a block if the value
 * entering the block were 0, and gain[i] is the cumulative product of b[]
 * from the block's first index up to i.  local[] and gain[] depend only on
 * data inside their own block, so every block is computed independently in
 * parallel (pass 1).  The true value entering each block is then obtained
 * with a short sequential scan over just the block boundaries - O(nblocks),
 * not O(LEN_1D) (pass 2).  Finally every element is corrected using its own
 * block's boundary value, again independently per block (pass 3).
 */
static real_t kernel_s321(void)
{
    const int n = LEN_1D - 1; /* number of recurrence steps per repetition: indices i = 1..n */
    int nblocks = 0;
    real_t *gain = NULL; /* heap, size LEN_1D: cumulative product of b[] from a block's start up to i */
    real_t boundary[S321_MAX_BLOCKS + 1]; /* true recurrence value entering block k; count is fixed, not LEN_1D-sized */

    if (n > 0) {
        nblocks = n < S321_MAX_BLOCKS ? n : S321_MAX_BLOCKS;
        gain = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
        if (!gain) nblocks = 0; /* malloc failed: fall back to the plain sequential recurrence below */
    }

    for (int nl = 0; nl < R; nl++) {
        if (n > 0 && gain) {
            /* Pass 1: independent per block.  blk is the loop index (private);
             * s, e, i, local, g are declared inside the loop body, so each is
             * already per-iteration scratch and must not appear in any clause.
             * a, b, gain are shared arrays but each block only reads/writes its
             * own disjoint index range [s,e], so there is no race between
             * blocks.  n and nblocks are read-only block-geometry values,
             * shared. */
            #pragma omp parallel for default(none) shared(a, b, gain, n, nblocks) schedule(static)
            for (int blk = 0; blk < nblocks; blk++) {
                int s = 1 + (int)((long)n * blk / nblocks);
                int e = (int)((long)n * (blk + 1) / nblocks);
                real_t local = (real_t)0;
                real_t g = (real_t)1;
                for (int i = s; i <= e; i++) {
                    local = local * b[i] + a[i];
                    g = g * b[i];
                    a[i] = local;
                    gain[i] = g;
                }
            }

            /* Pass 2: sequential scan over the nblocks block boundaries only
             * (nblocks <= S321_MAX_BLOCKS, not LEN_1D).  This is the moved
             * dependence: the true value carried out of block blk must reach
             * block blk+1 before block blk+1's elements are corrected, so this
             * whole pass completes before pass 3 (a separate parallel region)
             * starts. */
            boundary[0] = a[0];
            for (int blk = 0; blk < nblocks; blk++) {
                int e = (int)((long)n * (blk + 1) / nblocks);
                boundary[blk + 1] = a[e] + gain[e] * boundary[blk];
            }

            /* Pass 3: independent per block again.  Each block only reads the
             * single boundary value pass 2 produced for it and corrects its
             * own disjoint range [s,e] of a[] using gain[]; blocks don't
             * interact, so there is no race. */
            #pragma omp parallel for default(none) shared(a, gain, boundary, n, nblocks) schedule(static)
            for (int blk = 0; blk < nblocks; blk++) {
                int s = 1 + (int)((long)n * blk / nblocks);
                int e = (int)((long)n * (blk + 1) / nblocks);
                real_t bnd = boundary[blk];
                for (int i = s; i <= e; i++) {
                    a[i] = a[i] + gain[i] * bnd;
                }
            }
        } else if (n > 0) {
            /* Only reached if the gain[] allocation above failed. */
            for (int i = 1; i < LEN_1D; i++) {
                a[i] += a[i-1] * b[i];
            }
        }
        pb_mix(nl);
    }

    if (gain) free(gain);
    return (real_t)0;
}

PB_MAIN(kernel_s321)
