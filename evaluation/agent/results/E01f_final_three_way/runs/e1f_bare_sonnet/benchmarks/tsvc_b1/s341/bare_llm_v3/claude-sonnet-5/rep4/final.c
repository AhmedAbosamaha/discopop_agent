/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"
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

/* The sequential inner loop keeps a running output index j: it is incremented once per
 * kept element (b[i] > 0) and used immediately as the target slot a[j] = b[i].  That is a
 * prefix-sum dependence, not a real need for order: the final index of a kept element i is
 * exactly the count of kept elements before i.  We compute that count explicitly -- an
 * exclusive prefix sum of the 0/1 predicate "b[i] > 0" -- so every iteration knows its own
 * target slot in advance and the iterations become independent.
 *
 * The prefix sum is built from ordinary "#pragma omp parallel for" worksharing loops only,
 * in the classic two-pass, block-parallel way: pass 1 marks kept elements, pass 2 totals
 * each disjoint block in parallel, a short *serial* pass turns the per-block totals into
 * per-block offsets (true carried dependence, but over nblk = n/BLOCK entries, not n), and
 * pass 3 turns per-block flags into final global indices in parallel using those offsets.
 * Pass 4 then scatters the kept values into a[] at their precomputed, pairwise-distinct
 * indices. Total work is still O(n) per repetition, same order as the original. */
static real_t kernel_s341(void)
{
    const long n = LEN_1D;
    const long BLOCK = 1024;                 /* elements per block for the block-parallel scan */
    const long nblk = (n + BLOCK - 1) / BLOCK;
    int  *pos        = (int  *)malloc((size_t)n    * sizeof(int));   /* pos[i]: flag, then final target index, of element i */
    long *blockCount = (long *)malloc((size_t)nblk * sizeof(long));  /* blockCount[blk]: kept-element count within block blk */
    long *blockOff   = (long *)malloc((size_t)nblk * sizeof(long));  /* blockOff[blk]: exclusive prefix of blockCount over blocks */

    if (!pos || !blockCount || !blockOff) {
        free(pos); free(blockCount); free(blockOff);
        return (real_t)0;
    }

    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: independent across i -- iteration i only reads b[i] and writes pos[i]. */
        #pragma omp parallel for default(none) shared(b, pos, n) schedule(static)
        for (long i = 0; i < n; i++) {
            pos[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Pass 2: independent across blk -- each block reduces its own disjoint slice of
         * pos[] (read-only here) into its own blockCount[blk] slot. */
        #pragma omp parallel for default(none) shared(pos, blockCount, n, nblk, BLOCK) schedule(static)
        for (long blk = 0; blk < nblk; blk++) {
            long start = blk * BLOCK;
            long end = start + BLOCK;
            if (end > n) end = n;
            long cnt = 0;
            for (long i = start; i < end; i++) cnt += pos[i];
            blockCount[blk] = cnt;
        }

        /* Exclusive prefix sum over the per-block totals -- a genuine carried dependence,
         * but it walks only nblk = n/BLOCK entries, so it stays cheap next to the O(n)
         * parallel passes around it. */
        long running = 0;
        for (long blk = 0; blk < nblk; blk++) {
            blockOff[blk] = running;
            running += blockCount[blk];
        }

        /* Pass 3: independent across blk -- each block turns its own disjoint slice of
         * pos[] (0/1 flags) into final target indices, seeded from that block's exclusive
         * offset computed above, so the whole array ends up with one consistent count. */
        #pragma omp parallel for default(none) shared(pos, blockOff, n, nblk, BLOCK) schedule(static)
        for (long blk = 0; blk < nblk; blk++) {
            long start = blk * BLOCK;
            long end = start + BLOCK;
            if (end > n) end = n;
            long t = blockOff[blk];
            for (long i = start; i < end; i++) {
                int flag = pos[i];
                pos[i] = (int)t;
                t += flag;
            }
        }

        /* Pass 4: independent across i -- pos[] is now a strictly increasing injection over
         * the kept indices, so every kept i writes a distinct a[pos[i]]; dropped elements
         * (b[i] <= 0) touch nothing. */
        #pragma omp parallel for default(none) shared(a, b, pos, n) schedule(static)
        for (long i = 0; i < n; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }

        pb_mix(nl);
    }

    free(pos);
    free(blockCount);
    free(blockOff);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
