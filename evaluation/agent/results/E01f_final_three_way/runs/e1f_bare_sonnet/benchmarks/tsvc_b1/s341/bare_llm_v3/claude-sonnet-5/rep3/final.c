/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

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

static real_t kernel_s341(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* cnt is the scan (reduction(inscan,+:cnt)) variable: at the point of the "omp scan"
         * directive it holds the exclusive prefix sum of the predicate (b[i] > 0) over all
         * iterations strictly before i, i.e. exactly the compaction index the original code
         * built incrementally via "j++; a[j] = b[i];". After the directive it is advanced by
         * this iteration's own predicate value so the next iteration sees the updated count.
         * This replaces the loop-carried dependence on j (a value that moved from one
         * iteration to the next) with the same dependence expressed as a parallel scan, which
         * OpenMP is allowed to compute out of textual order while still producing, for every
         * iteration, the identical prefix count the sequential loop would have produced. */
        int cnt = 0;
        #pragma omp parallel for reduction(inscan, +:cnt)
        for (int i = 0; i < LEN_1D; i++) {
            int p = (b[i] > (real_t)0.) ? 1 : 0; /* per-iteration predicate; declared in the
                                                     loop body, so it is private automatically
                                                     and needs no data-sharing clause */
            if (p) {
                a[cnt] = b[i]; /* cnt: exclusive prefix count of valid b[i] before this i */
            }
            #pragma omp scan exclusive(cnt)
            cnt += p;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
