real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulation arrays
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            
            // Thread-local loop variable for initialization
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            // Parallel loop: each thread accumulates into its local_u
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            
            // Merge per-thread local_u into shared u
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