#include "data.h"

real_t kernel_k48(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local arrays for indirect accumulation
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            
            // Initialize local array
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            // Parallel loop with private local accumulation
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += v[kv[li]] * c[li];
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
            }
            
            // Merge per-thread results into shared array
            #pragma omp critical
            {
                int mi;
                for (mi = 0; mi < LEN_1D; mi++) {
                    u[mi] += local_u[mi];
                }
            }
            
            free(local_u);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}