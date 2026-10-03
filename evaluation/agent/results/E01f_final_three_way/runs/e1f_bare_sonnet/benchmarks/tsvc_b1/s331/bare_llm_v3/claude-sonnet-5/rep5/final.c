/* TSVC-2 loop s331, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s331.h"

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

static real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < R; nl++) {
        j = -1;
        /* j is a running "last index where a[i] < 0"; since i increases
         * monotonically, this is equivalent to a max-reduction over indices
         * satisfying the condition (identity -1 when none match). a is only
         * read here, so it stays shared/read-only across iterations. */
        #pragma omp parallel for reduction(max:j)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                if (i > j) {
                    j = i;
                }
            }
        }
        chksum = (real_t) j;
        pb_mix(nl);
    }
    return j+1;
}

PB_MAIN(kernel_s331)
