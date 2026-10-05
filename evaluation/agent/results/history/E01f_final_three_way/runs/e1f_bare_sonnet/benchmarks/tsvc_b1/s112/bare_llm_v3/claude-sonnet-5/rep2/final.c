/* TSVC-2 loop s112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s112.h"
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

static real_t kernel_s112(void)
{
    /* The inner loop walks i downward and writes a[i+1] = a[i] + b[i]. Because i
     * decreases, the read of a[i] at step i always happens before the write that
     * later overwrites that same slot (at step i-1). So every read in the original
     * execution order sees the value a had before this activation of the loop
     * started, never a value written earlier in the same activation: the only
     * thing blocking a parallel, order-independent loop is that reliance on
     * execution order, not a value genuinely produced by one iteration for
     * another. Making the old values explicit in a read-only snapshot removes
     * that anti-dependence: each iteration then writes a disjoint index (i+1)
     * and reads only from the snapshot and from b, so iterations may run in any
     * order or interleaving.
     *
     * The outer nl loop stays sequential: pb_mix mutates a, b, c, d and e between
     * repetitions, so each repetition genuinely depends on the previous one's
     * output.
     *
     * LEN_1D can be up to 192,000,000, so the snapshot buffer is heap-allocated
     * (never a stack array) and is allocated once outside the R loop and reused,
     * so the extra work stays a constant factor, not a growing one. */
    real_t *old_a = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot of a's pre-activation values; elementwise copy, no
         * cross-iteration dependence. old_a is private per index (each i writes
         * a distinct slot), a and old_a are shared. */
        #pragma omp parallel for shared(a, old_a) schedule(static)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            old_a[i] = a[i];
        }

        /* a[i+1] now depends only on the read-only snapshot old_a[i] and b[i],
         * both unchanged by this loop, and writes land on a distinct index
         * (i+1) per iteration, so iterations are independent. old_a and b are
         * read-only (shared); a is written at disjoint indices (shared). */
        #pragma omp parallel for shared(a, b, old_a) schedule(static)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            a[i+1] = old_a[i] + b[i];
        }

        pb_mix(nl);
    }

    free(old_a);
    return (real_t)0;
}

PB_MAIN(kernel_s112)
