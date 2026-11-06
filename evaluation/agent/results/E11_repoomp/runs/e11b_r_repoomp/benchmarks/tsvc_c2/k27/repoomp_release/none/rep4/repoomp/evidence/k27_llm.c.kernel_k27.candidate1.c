real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulators for u array
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            // Parallel accumulation into local arrays
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u[ju[i]] += w[kw[i]] * c[i];
            }
            
            // Merge local accumulators into global u array
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }
            
            free(local_u);
            
            // Barrier to ensure u is fully updated before computing v and w
            #pragma omp barrier
            
            // Parallel computation of v and w (independent writes)
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }
        }
        
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}