real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulation arrays for u
            long *local_u = (long *)malloc(LEN_1D * sizeof(long));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0;
            }
            
            // Parallel loop: each thread accumulates into its own local_u
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u[ju[i]] += w[kw[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
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