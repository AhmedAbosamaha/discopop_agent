real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
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
            
            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}