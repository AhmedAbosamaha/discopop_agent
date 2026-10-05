/* Kernel k31. */
#include "tsvc_b1/k31.h"
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

static real_t kernel_k31(void)
{
    /* Snapshots of u and v taken before each sweep: the loop reads
     * v[i+off] / u[i+far] which later iterations overwrite, so the reads
     * must see the values from before the sweep (anti-dependence). */
    const long nu = (long)LEN_1D + (long)(far);
    const long nv = (long)LEN_1D + (long)(off);
    real_t *uold = (real_t *)malloc((size_t)nu * sizeof(real_t));
    real_t *vold = (real_t *)malloc((size_t)nv * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
#pragma omp parallel for shared(uold, u, nu) schedule(static)
        for (long j = 0; j < nu; j++) {
            uold[j] = u[j];
        }
#pragma omp parallel for shared(vold, v, nv) schedule(static)
        for (long j = 0; j < nv; j++) {
            vold[j] = v[j];
        }
#pragma omp parallel for shared(u, v, c, d, uold, vold) schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += vold[i + off] * c[i];
            /* far == 0 reads the u[i] just updated in this iteration;
             * otherwise it reads a not-yet-updated element: the snapshot. */
            v[i] = (((long)(far) == 0) ? u[i] : uold[i + far]) * d[i] + c[i];
        }
        pb_mix(nl);
    }

    free(uold);
    free(vold);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
