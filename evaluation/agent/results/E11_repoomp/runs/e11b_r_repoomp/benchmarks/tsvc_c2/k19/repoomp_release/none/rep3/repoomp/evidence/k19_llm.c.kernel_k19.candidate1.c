real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            real_t *local_v = (real_t *)malloc(LEN_1D * sizeof(real_t));
            
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
                local_v[li] = 0.0;
            }
            
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u[ju[i]] += v[kv[i]] * c[i];
                local_v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                    v[li] = local_v[li];
                }
            }
            
            free(local_u);
            free(local_v);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}