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
    /* xx[i+1] writes flat_2d_array[i + (vl+1)]; the loop reads flat_2d_array[i].
     * So this is a true, loop-carried recurrence with CONSTANT distance (vl+1):
     * iteration i's write is read back by iteration i+(vl+1). The write index
     * i+(vl+1) and the read index i both have the same residue mod (vl+1), so
     * the recurrence never crosses residue classes: splitting i by i % (vl+1)
     * yields (vl+1) independent chains, each of which must keep its original
     * ascending-i order (that order is what the sequential code executed).
     * Parallelizing across chains (the outer "r" loop below) is therefore safe;
     * the inner chain loop keeps the dependence and must stay sequential. */
    for (int nl = 0; nl < R; nl++) {
        int stride = vl + 1;
        #pragma omp parallel for schedule(static) firstprivate(stride) shared(xx, flat_2d_array, a)
        for (int r = 0; r < stride; r++) {
            for (int i = r; i < LEN_1D - 1; i += stride) {
                xx[i+1] = flat_2d_array[i] + a[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s424)
