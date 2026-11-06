real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            int li;
            real_t *local_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
            for (li = 0; li < LEN_1D; li++) {
                local_u[li] = 0.0;
            }

            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u[ju[li]] += v[kv[li]] * c[li];
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
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