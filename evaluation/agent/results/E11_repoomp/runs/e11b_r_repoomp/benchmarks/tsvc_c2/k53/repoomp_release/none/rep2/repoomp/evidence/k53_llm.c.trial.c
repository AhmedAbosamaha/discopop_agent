#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulation arrays
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            
            // Initialize local_u to zero
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            // Parallel loop: each thread accumulates into its local_u
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += v[kv[li]] * c[li];
            }
            
            // Merge local_u into global u
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }
            
            free(local_u);
            
            // Barrier to ensure u is updated before computing v
            #pragma omp barrier
            
            // Parallel loop: update v (no accumulation, direct write)
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
            }
        }
        
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}