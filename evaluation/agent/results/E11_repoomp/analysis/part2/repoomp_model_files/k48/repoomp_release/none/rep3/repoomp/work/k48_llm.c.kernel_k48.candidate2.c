real_t kernel_k48(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            // Per-thread local accumulation arrays
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }

            // Parallel accumulation into local arrays
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += v[kv[li]] * c[li];
            }

            // Merge local arrays into shared u inside critical section
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }

            free(local_u);

            // Barrier to ensure all u updates are visible before v writes
            #pragma omp barrier

            // Parallel independent writes to v
            #pragma omp for
            for (long i = 1; i < LEN_1D; i++) {
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}