/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s211.h"
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

static real_t kernel_s211(void)
{
    /* The sequential loop carries a true dependence through b: a[i] reads
     * b[i-1] AFTER it has already been overwritten by the previous
     * iteration (b[i-1] = b[i] - e[i-1]*d[i-1] computed when the loop was
     * at index i-1), while b[i] itself is built from b[i+1], an index the
     * sequential order has not reached yet and which is therefore still
     * the pre-iteration value. So every b[i+1] read in this loop is really
     * reading the snapshot of b taken before the loop started, and every
     * b[i-1] read by a[i] is really "pre-loop b[i] combined with e[i-1]
     * and d[i-1]" (the value the previous iteration would have written).
     * Capturing that pre-loop snapshot of b in bold lets every iteration
     * compute a[i] and b[i] straight from bold, c, d, e with no
     * iteration-to-iteration dependence left, so the i-loop can run in
     * any order/split across threads and still match the original
     * sequential result. The repetition loop over nl stays sequential
     * (pb_mix feeds forward into the next repetition's snapshot). */
    real_t *bold = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* bold: snapshot of b as it stood before this repetition's
         * update loop runs (shared, each iteration writes a distinct
         * index, so this copy loop is race-free). */
        #pragma omp parallel for default(none) shared(b, bold) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            bold[i] = b[i];
        }
        /* a, b, c, d, e, bold: shared arrays. Each iteration i writes
         * only a[i] and b[i] (disjoint across iterations) and reads only
         * from bold/c/d/e, which are never written inside this loop, so
         * there is no dependence left between iterations. bim1 is
         * declared inside the loop body, so it is already private to
         * each iteration and must not appear in any clause. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, bold) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t bim1 = (i == 1) ? bold[0] : bold[i] - e[i - 1] * d[i - 1];
            a[i] = bim1 + c[i] * d[i];
            b[i] = bold[i + 1] - e[i] * d[i];
        }
        pb_mix(nl);
    }
    free(bold);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
