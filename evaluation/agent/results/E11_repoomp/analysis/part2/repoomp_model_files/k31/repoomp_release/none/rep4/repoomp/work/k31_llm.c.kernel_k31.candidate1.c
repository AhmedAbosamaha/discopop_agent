real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        
        u_new[0] = u[0];
        v_new[0] = v[0];
        
        #pragma omp parallel for private(i)
        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] = u[i] + v[i + off] * c[i];
            v_new[i] = u[i + far] * d[i] + c[i];
        }
        
        #pragma omp parallel for private(i)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_new[i];
            v[i] = v_new[i];
        }
        
        free(u_new);
        free(v_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}