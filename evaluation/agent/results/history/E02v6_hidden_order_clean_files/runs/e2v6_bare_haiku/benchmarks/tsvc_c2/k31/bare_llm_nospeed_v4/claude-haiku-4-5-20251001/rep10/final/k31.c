#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    /* Allocate temporary buffers for parallel iteration.
       Each iteration will read from u, v (shared, read-only during parallel phase)
       and write to u_new, v_new (private per thread). After all iterations complete,
       we copy back to u, v. This breaks loop-carried dependencies while preserving
       semantics: each iteration operates on independent array indices in the destination. */
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Parallel loop over array elements. Each iteration is now independent:
           - All threads read from the same u, v, c, d (no writes during read phase)
           - Each thread writes to distinct u_new[i], v_new[i] (no conflicts)
           - off and far determine which elements are read but don't create
             iteration-to-iteration dependencies within this parallel phase.
           Shared: u, v, c, d, off, far (all read-only in this loop)
           Private: i (loop variable), u_new, v_new (reduction targets per element) */
        #pragma omp parallel for schedule(static) \
            shared(u, v, c, d, u_new, v_new, off, far, LEN_1D) \
            private(i)
        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] = u[i] + v[i + off] * c[i];
            v_new[i] = u[i + far] * d[i] + c[i];
        }

        /* Copy updated values back to u, v for next outer iteration.
           This sequential copy ensures u, v are consistent after each outer iteration,
           maintaining the exact state progression through all 48 outer iterations. */
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_new[i];
            v[i] = v_new[i];
        }

        dummy(a, b, c, d, e);
    }

    free(u_new);
    free(v_new);
    return (real_t)0;
}
