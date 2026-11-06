real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulators for u
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }

            // Parallel loop: each thread accumulates into its local_u
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u[ju[i]] += w[kw[i]] * c[i];
            }

            // Merge per-thread local_u into shared u
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }

            free(local_u);

            // Barrier to ensure all threads finish merging before v and w loops
            #pragma omp barrier

            // Parallel loop for v (independent writes to v[jv[i]])
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }

            // Parallel loop for w (independent writes to w[jw[i]])
            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}