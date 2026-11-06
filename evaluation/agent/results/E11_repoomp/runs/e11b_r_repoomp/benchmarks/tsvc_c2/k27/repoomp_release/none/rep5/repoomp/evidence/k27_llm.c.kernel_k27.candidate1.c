real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local arrays for indirect accumulation
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }
            
            // Parallel loop: accumulate into per-thread local arrays
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += w[kw[li]] * c[li];
            }
            
            // Merge per-thread local arrays into shared u
            #pragma omp critical
            {
                int mi;
                for (mi = 0; mi < LEN_1D; mi++) {
                    u[mi] += local_u[mi];
                }
            }
            
            free(local_u);
            
            // Independent loops: v and w writes (each iteration writes distinct element)
            #pragma omp for
            for (li = 1; li < LEN_1D; li++) {
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
            }
            
            #pragma omp for
            for (li = 1; li < LEN_1D; li++) {
                w[jw[li]] = v[kv[li]] * e[li] + d[li];
            }
        }
        
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}