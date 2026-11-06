real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            long *local_u_acc = (long *)malloc(LEN_1D * sizeof(long));
            int li;
            for (li = 0; li < LEN_1D; li++) {
                local_u_acc[li] = 0;
            }

            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                local_u_acc[ju[li]] += w[kw[li]] * c[li];
            }

            #pragma omp critical
            {
                int lj;
                for (lj = 0; lj < LEN_1D; lj++) {
                    u[lj] += local_u_acc[lj];
                }
            }

            free(local_u_acc);

            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                v[jv[li]] = u[ku[li]] * d[li] + c[li];
            }

            #pragma omp for private(li)
            for (li = 1; li < LEN_1D; li++) {
                w[jw[li]] = v[kv[li]] * e[li] + d[li];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}