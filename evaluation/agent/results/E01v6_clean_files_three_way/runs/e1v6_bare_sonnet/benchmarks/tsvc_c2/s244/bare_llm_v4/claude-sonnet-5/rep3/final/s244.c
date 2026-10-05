#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /*
         * Original body per i:
         *   a[i]   = b[i] + c[i]*d[i];        // uses OLD b[i]
         *   b[i]   = c[i] + b[i];             // update b[i] in place
         *   a[i+1] = b[i] + a[i+1]*d[i];      // uses NEW b[i] and OLD a[i+1]
         *
         * The third statement writes a[i+1], a location that iteration
         * i+1's first statement (a[i+1] = b[i+1] + c[i+1]*d[i+1]) always
         * overwrites afterward in the original sequential order -- except
         * at the very last index (i == LEN_1D-2), where a[LEN_1D-1] is
         * never touched by any first statement.  So for every i except
         * the last, the value the third statement writes is dead (it is
         * unconditionally clobbered before being read).  The only write
         * to a[i+1] that actually survives is the boundary case
         * i == LEN_1D-2, writing a[LEN_1D-1].
         *
         * That lets us drop the third statement from the per-i loop body
         * (removing the WAW hazard on a[i+1] between iterations i and
         * i+1 that would otherwise race under arbitrary iteration order)
         * and instead compute the single surviving boundary update once,
         * sequentially, after the parallel loop -- using the exact same
         * formula and operand values, so results stay bit-identical.
         *
         * What remains inside the loop (a[i] from old b[i], then b[i]
         * updated in place) touches only index i per iteration: no
         * cross-iteration dependence, so it parallelizes directly.
         */
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
