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
    /* The original loop reads a[i] and writes a[i+1] while walking i from
     * LEN_1D-2 down to 0.  The only iteration that ever reads index i+1 is
     * the one whose own loop variable equals i+1, and in this descending
     * order that iteration always runs BEFORE the iteration that writes
     * a[i+1] (loop variable i runs after loop variable i+1).  So every
     * read in this loop sees the value a[] held before the loop started:
     * the computation is a pure shift-and-add, new_a[i+1] = old_a[i] +
     * b[i], not a true running recurrence -- the dependence is on the
     * reused array location, not on a value actually carried forward.
     * To run the iterations in arbitrary order/parallel, snapshot the
     * pre-loop values of a[0..LEN_1D-2] into a heap buffer first (so the
     * dependence still reaches every read, just via the snapshot instead
     * of in-place order), then compute every new a[i+1] from that
     * snapshot.  b is only read here, so it needs no snapshot.  The
     * buffer is sized once since LEN_1D is constant across repetitions. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)(LEN_1D - 1));

    for (int nl = 0; nl < R; nl++) {
        /* a_old: shared snapshot buffer, each iteration writes its own
         * distinct element a_old[i] from a[i] -- no overlap between
         * threads. a: shared, read-only in this loop. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            a_old[i] = a[i];
        }

        /* a: shared, each iteration writes its own distinct element
         * a[i+1] -- no two iterations touch the same index, and the
         * value read (a_old[i]) was fully populated by the barrier at
         * the end of the copy loop above. b, a_old: shared, read-only
         * in this loop. */
        #pragma omp parallel for default(none) shared(a, b, a_old)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            a[i+1] = a_old[i] + b[i];
        }

        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s112)
