#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    /* off and far are fixed for the whole call. The i-loop's only cross-
     * element references are v[i+off] (read while computing u[i]) and
     * u[i+far] (read while computing v[i]); with the sweep running low to
     * high, both references always land on data that has not been touched
     * yet this sweep (off>=0, far>=0), except u[i+far] when far==0, which
     * is exactly the value this same iteration just produced for u[i].
     * old_u/old_v freeze the pre-sweep contents of u/v; the previous sweep
     * (or dummy()) has already completed sequentially before this copy is
     * taken, so that write-before-read ordering is preserved even though
     * the i-loop below now runs with iterations in any order. */
    long size_u = LEN_1D + (far > 0 ? far : 0);
    long size_v = LEN_1D + (off > 0 ? off : 0);
    real_t *old_u = (real_t *)malloc(sizeof(real_t) * (size_t)size_u);
    real_t *old_v = (real_t *)malloc(sizeof(real_t) * (size_t)size_v);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(old_u, u, sizeof(real_t) * (size_t)size_u);
        memcpy(old_v, v, sizeof(real_t) * (size_t)size_v);

        #pragma omp parallel for default(none) \
            shared(u, v, c, d, old_u, old_v, off, far)
        for (long i = 1; i < LEN_1D; i++) {
            real_t new_ui = old_u[i] + old_v[i + off] * c[i];
            u[i] = new_ui;
            real_t u_for_v = (far == 0) ? new_ui : old_u[i + far];
            v[i] = u_for_v * d[i] + c[i];
        }

        dummy(a, b, c, d, e);
    }

    free(old_u);
    free(old_v);
    return (real_t)0;
}
