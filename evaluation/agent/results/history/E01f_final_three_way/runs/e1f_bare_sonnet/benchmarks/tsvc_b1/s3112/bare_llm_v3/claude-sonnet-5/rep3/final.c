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

/* The inner loop over i carries "sum" as a true running-prefix (scan) dependence:
 * b[i] is not just the final total but the partial sum after each element, so it
 * cannot become a plain reduction. We split LEN_1D into NUM_BLOCKS independent,
 * data-value-independent chunks (their boundaries depend only on LEN_1D, so they
 * are computed once per call, not per repetition):
 *   1) each chunk computes its own local left-to-right prefix sum into b[] in
 *      parallel, remembering its chunk total in block_sum[];
 *   2) a short sequential pass turns block_sum[] into an EXCLUSIVE prefix - the
 *      carry-in value each chunk would have received from everything before it
 *      in the original single loop. This is the one true dependence, now spanning
 *      only NUM_BLOCKS values instead of LEN_1D of them, and it runs between the
 *      two parallel passes so every write it depends on has already landed;
 *   3) a second parallel pass adds each chunk's carry-in to every element of that
 *      chunk, independently of every other chunk.
 * block_start/block_end/block_sum are fixed-size (NUM_BLOCKS) arrays, not sized by
 * LEN_1D, so they stay on the stack even at the largest verified LEN_1D. */
static real_t kernel_s3112(void)
{
    enum { NUM_BLOCKS = 256 };
    int block_start[NUM_BLOCKS];
    int block_end[NUM_BLOCKS];
    real_t block_sum[NUM_BLOCKS];
    int nb = LEN_1D < NUM_BLOCKS ? LEN_1D : NUM_BLOCKS;
    if (nb < 1) nb = 1;
    {
        int base = LEN_1D / nb;
        int rem = LEN_1D % nb;
        int start = 0;
        for (int blk = 0; blk < nb; blk++) {
            int len = base + (blk < rem ? 1 : 0);
            block_start[blk] = start;
            block_end[blk] = start + len;
            start += len;
        }
    }

    real_t sum;
    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: independent per-block local prefix sums. block_start/block_end
         * are read-only here (shared); block_sum is shared but each block writes
         * only its own index blk, so there is no overlap between iterations. */
        #pragma omp parallel for default(none) \
            shared(a, b, block_start, block_end, block_sum, nb) schedule(static)
        for (int blk = 0; blk < nb; blk++) {
            real_t local_sum = (real_t)0.0;
            int start = block_start[blk];
            int end = block_end[blk];
            for (int i = start; i < end; i++) {
                local_sum += a[i];
                b[i] = local_sum;
            }
            block_sum[blk] = local_sum;
        }

        /* Sequential fold: block_sum[blk] becomes the carry-in from all blocks
         * before it (exclusive prefix); carry ends up holding the grand total,
         * which is what the original loop returned as "sum". */
        real_t carry = (real_t)0.0;
        for (int blk = 0; blk < nb; blk++) {
            real_t total = block_sum[blk];
            block_sum[blk] = carry;
            carry += total;
        }
        sum = carry;

        /* Pass 2: add each block's carry-in to its own elements, independently. */
        #pragma omp parallel for default(none) \
            shared(b, block_start, block_end, block_sum, nb) schedule(static)
        for (int blk = 0; blk < nb; blk++) {
            real_t off = block_sum[blk];
            int start = block_start[blk];
            int end = block_end[blk];
            for (int i = start; i < end; i++) {
                b[i] += off;
            }
        }

        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
