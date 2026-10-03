/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"
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

/* The inner loop a[i] = a[i] + a[i-1]*b[i] + a[i-2]*c[i] is an order-2 linear
 * recurrence: a[i] genuinely needs the just-written a[i-1] and a[i-2]. That
 * dependence cannot be deleted, only moved. We split [2, LEN_1D) into fixed
 * blocks (boundaries depend only on LEN_1D, never on thread count/schedule,
 * so every run agrees):
 *   pass 1 (parallel, per block): using only the still-unmodified a[],b[],c[]
 *     of that block, compute the block's affine map (M_k, v_k) with
 *     (a[hi],a[hi-1]) = M_k * (a[lo-1],a[lo-2]) + v_k, via three independent
 *     runs of the same recurrence formula seeded (1,0), (0,1) and (0,0).
 *   pass 2 (serial, over the O(#blocks) blocks only): chain the per-block
 *     maps to get each block's true boundary pair. This is the moved
 *     dependence - cheap because it runs once per block, not once per i.
 *   pass 3 (parallel, per block): replay the exact original formula, in the
 *     same operand order, from the now-known true boundary, writing a[].
 * Blocks touch disjoint index ranges in pass 1/3, so no block ever races
 * another. */
#define S322_BLOCK 1024

static real_t kernel_s322(void)
{
    const int lo_bound = 2;
    int n_elems = LEN_1D - lo_bound;
    if (n_elems < 0) n_elems = 0;
    int nblocks = (n_elems + S322_BLOCK - 1) / S322_BLOCK;

    real_t *m00 = NULL, *m01 = NULL, *m10 = NULL, *m11 = NULL;
    real_t *v0 = NULL, *v1 = NULL, *entry0 = NULL, *entry1 = NULL;
    if (nblocks > 0) {
        m00 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        m01 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        m10 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        m11 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        v0  = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        v1  = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        entry0 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
        entry1 = (real_t *)malloc(sizeof(real_t) * (size_t)nblocks);
    }

    for (int nl = 0; nl < R; nl++) {
        if (nblocks > 0) {
            /* Pass 1: a,b,c are read-only here (pass 3 hasn't written yet).
             * m00/m01/m10/m11/v0/v1 are written once per block, each at its
             * own index blk: disjoint writes, no race. nblocks/n_elems/
             * lo_bound are read-only loop-invariant bounds. */
            #pragma omp parallel for default(none) \
                shared(a, b, c, m00, m01, m10, m11, v0, v1, nblocks, n_elems, lo_bound)
            for (int blk = 0; blk < nblocks; blk++) {
                int lo = lo_bound + blk * S322_BLOCK;
                int hi = lo + S322_BLOCK - 1;
                int last = lo_bound + n_elems - 1;
                if (hi > last) hi = last;

                real_t pb1 = (real_t)1, pb2 = (real_t)0; /* column for seed (1,0) */
                real_t pc1 = (real_t)0, pc2 = (real_t)1; /* column for seed (0,1) */
                real_t pd1 = (real_t)0, pd2 = (real_t)0; /* forced response, seed (0,0) */

                for (int i = lo; i <= hi; i++) {
                    real_t nb = pb1 * b[i] + pb2 * c[i];
                    real_t nc = pc1 * b[i] + pc2 * c[i];
                    real_t nd = a[i] + pd1 * b[i] + pd2 * c[i];
                    pb2 = pb1; pb1 = nb;
                    pc2 = pc1; pc1 = nc;
                    pd2 = pd1; pd1 = nd;
                }
                m00[blk] = pb1; m10[blk] = pb2;
                m01[blk] = pc1; m11[blk] = pc2;
                v0[blk]  = pd1; v1[blk]  = pd2;
            }

            /* Pass 2: the genuine cross-block dependence, kept strictly
             * sequential but now only O(nblocks) steps instead of O(LEN_1D). */
            real_t e0 = a[lo_bound - 1];
            real_t e1 = a[lo_bound - 2];
            for (int blk = 0; blk < nblocks; blk++) {
                entry0[blk] = e0;
                entry1[blk] = e1;
                real_t ne0 = m00[blk] * e0 + m01[blk] * e1 + v0[blk];
                real_t ne1 = m10[blk] * e0 + m11[blk] * e1 + v1[blk];
                e0 = ne0; e1 = ne1;
            }

            /* Pass 3: a is read then written per element, same as the
             * original formula and operand order, but each block only
             * touches its own disjoint index range [lo,hi] - no race.
             * entry0/entry1 are read-only (each block reads only its own
             * index blk). b,c are read-only. */
            #pragma omp parallel for default(none) \
                shared(a, b, c, entry0, entry1, nblocks, n_elems, lo_bound)
            for (int blk = 0; blk < nblocks; blk++) {
                int lo = lo_bound + blk * S322_BLOCK;
                int hi = lo + S322_BLOCK - 1;
                int last = lo_bound + n_elems - 1;
                if (hi > last) hi = last;

                real_t prev1 = entry0[blk];
                real_t prev2 = entry1[blk];
                for (int i = lo; i <= hi; i++) {
                    real_t val = a[i] + prev1 * b[i] + prev2 * c[i];
                    a[i] = val;
                    prev2 = prev1;
                    prev1 = val;
                }
            }
        }
        pb_mix(nl);
    }

    if (nblocks > 0) {
        free(m00); free(m01); free(m10); free(m11);
        free(v0); free(v1); free(entry0); free(entry1);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s322)
