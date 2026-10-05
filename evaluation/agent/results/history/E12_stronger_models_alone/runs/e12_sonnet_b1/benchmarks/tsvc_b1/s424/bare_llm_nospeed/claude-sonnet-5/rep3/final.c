/* TSVC-2 loop s424, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s424.h"

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

static real_t kernel_s424(void)
{
    int vl = 63;
    xx = flat_2d_array + vl;
    /* xx[i+1] is flat_2d_array[i+dist] with dist = vl+1: a true flow
     * dependence of distance `dist` runs through flat_2d_array. Indices
     * are independent across residue classes mod `dist` (writing i+dist
     * never touches a different class than reading i), so the dist
     * sequential chains can be run in parallel; within each chain the
     * original ascending visiting order is preserved. */
    int dist = vl + 1;
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for default(none) shared(flat_2d_array, a) firstprivate(dist)
        for (int r = 0; r < dist; r++) {
            for (int i = r; i < LEN_1D - 1; i += dist) {
                flat_2d_array[i + dist] = flat_2d_array[i] + a[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s424)
