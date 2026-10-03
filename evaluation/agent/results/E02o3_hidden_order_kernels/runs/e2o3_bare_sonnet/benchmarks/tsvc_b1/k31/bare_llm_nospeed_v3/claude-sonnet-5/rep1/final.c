/* Kernel k31. */
#include "tsvc_b1/k31.h"

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

static real_t kernel_k31(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original body, for i = 1 .. LEN_1D-1:
         *   u[i] += v[i + off] * c[i];
         *   v[i]  = u[i + far] * d[i] + c[i];
         * These two statements look like they carry a cross-iteration
         * recurrence through u and v, but the two arrays are coupled only
         * one way each:
         *   - statement 1 never reads a v element this sweep's statement 2
         *     has already produced (off keeps the read at or ahead of the
         *     index whose v value statement 2 would still need to write),
         *     so for every i it reads the value v had before this sweep
         *     started, independent of what order the i's run in;
         *   - statement 2 reads u at an index that this sweep's statement 1
         *     has already finalized (far keeps the read at or behind the
         *     producing index), so once every u[i] has been written by
         *     statement 1 for the whole sweep, statement 2 can read any of
         *     them and get exactly the value the original interleaved loop
         *     would have produced.
         * So the value-flow dependence is not between loop iterations of a
         * single loop, it is between two sweeps over the whole array: all of
         * u must be produced from the pre-sweep v before any of v is
         * produced from the post-sweep u. Splitting the loop in two and
         * putting the implicit barrier of the first parallel loop between
         * them moves that dependence to the right place instead of deleting
         * it, and leaves each loop with no dependence between its own
         * iterations, so each i in each loop is independent of every other.
         */
        #pragma omp parallel for shared(u, v, c)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        #pragma omp parallel for shared(u, v, c, d)
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u[i + far] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k31)
