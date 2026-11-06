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

            #pragma omp for private(i)
            for (long i = 1; i < LEN_1D; i++) {
                local_u_acc[ju[i]] += w[kw[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }

            #pragma omp critical
            {
                for (li = 0; li < LEN_1D; li++) {
                    u[li] += local_u_acc[li];
                }
            }

            free(local_u_acc);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}