#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            long *local_u_accum_idx = (long *)malloc(LEN_1D * sizeof(long));
            real_t *local_u_accum_val = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int local_count = 0;
            
            #pragma omp for private(i, idx)
            for (long i = 1; i < LEN_1D; i++) {
                long idx = ju[i];
                real_t val = v[kv[i]] * c[i];
                
                local_u_accum_idx[local_count] = idx;
                local_u_accum_val[local_count] = val;
                local_count++;
                
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            
            #pragma omp critical
            {
                for (int li = 0; li < local_count; li++) {
                    u[local_u_accum_idx[li]] += local_u_accum_val[li];
                }
            }
            
            free(local_u_accum_idx);
            free(local_u_accum_val);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}