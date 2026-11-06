real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                long idx_u = ju[i];
                local_u[idx_u] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }
            
            free(local_u);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}