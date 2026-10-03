/* TSVC-2 loop s161, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s161.h"

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

/* Original body used a goto to pick, per i, between writing a[i] (reading c[i])
 * or writing c[i+1] (reading a[i]).  The only cross-iteration dependence is that
 * c[i] read by iteration i may have been overwritten by iteration i-1's
 * c[i+1]-write.  Whether that overwrite happened is decided purely by b[i-1],
 * which this loop never modifies, and the value written is a[i-1]+d[i-1]*d[i-1]
 * where a[i-1] itself is never written in that case (iteration i-1 only writes
 * a[i-1] in the branch where b[i-1]>=0, mutually exclusive with the overwrite
 * branch).  So each iteration can recompute, from the untouched originals of
 * a/b/d at index i-1, the same value c[i] would have held at the moment it is
 * read, without needing iteration i-1 to have run first.  Each iteration then
 * writes to exactly one of a[i] or c[i+1], both unique per i, so the writes
 * themselves never overlap across iterations. */
static real_t kernel_s161(void)
{
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            real_t cur_c;
            if (i > 0 && b[i-1] < (real_t)0.) {
                cur_c = a[i-1] + d[i-1] * d[i-1];
            } else {
                cur_c = c[i];
            }
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                a[i] = cur_c + d[i] * e[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s161)
