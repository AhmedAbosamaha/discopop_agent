#include <stdlib.h>
#include "data.h"

real_t kernel_s127(void)
{
    // Allocate staging buffer for pipeline: decouples compute from dummy()
    real_t *a_pipeline = (real_t *)malloc(LEN_1D * sizeof(real_t));
    if (a_pipeline == NULL) return (real_t)0;

    // Initialize: compute for first iteration into main array
    if (iterations > 0) {
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        // Copy to pipeline buffer for first dummy() call
        #pragma omp parallel for shared(a_pipeline) 
        for (int i = 0; i < LEN_1D; i++) {
            a_pipeline[i] = a[i];
        }
    }

    // Pipelined loop: dummy() on previous, then compute current (into a, decoupled via a_pipeline)
    for (int nl = 1; nl < iterations; nl++) {
        dummy(a_pipeline, b, c, d, e);
        // Compute writes to a (independent of a_pipeline which dummy just read)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        // Copy computed a to pipeline buffer for next iteration's dummy()
        #pragma omp parallel for shared(a_pipeline) 
        for (int i = 0; i < LEN_1D; i++) {
            a_pipeline[i] = a[i];
        }
    }

    // Finalize: dummy() for last iteration (on actual a, not pipeline copy)
    if (iterations > 0) {
        dummy(a, b, c, d, e);
    }

    free(a_pipeline);
    return (real_t)0;
}
