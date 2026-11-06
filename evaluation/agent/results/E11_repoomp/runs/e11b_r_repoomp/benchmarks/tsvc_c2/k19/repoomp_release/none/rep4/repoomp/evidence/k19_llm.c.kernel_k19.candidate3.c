real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            long *local_u = (long *)malloc(LEN_1D * sizeof(long));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0;
            }
            
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += v[kv[li]] * c[li];
            }
            
            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u[li];
                }
            }
            
            free(local_u);
            
            #pragma omp for
            for (long i = 1; i < LEN_1D; i++) {
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}