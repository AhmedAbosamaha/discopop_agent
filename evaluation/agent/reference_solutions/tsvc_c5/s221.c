#include "data.h"

real_t kernel_s221(void)
{
    enum { NB = 64 };
    for (int nl = 0; nl < iterations; nl++) {
        real_t total[NB], offset[NB + 1];
        long n = (long)LEN_1D - 1;
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += c[i] * d[i];
        }
        #pragma omp parallel for
        for (int k = 0; k < NB; k++) {
            long lo = 1 + n * k / NB, hi = 1 + n * (k + 1) / NB;
            real_t run = (real_t)0.;
            for (long i = lo; i < hi; i++) {
                run = run + a[i] + d[i];
                b[i] = run;
            }
            total[k] = run;
        }
        offset[0] = b[0];
        for (int k = 0; k < NB; k++) {
            offset[k + 1] = offset[k] + total[k];
        }
        #pragma omp parallel for
        for (int k = 0; k < NB; k++) {
            long lo = 1 + n * k / NB, hi = 1 + n * (k + 1) / NB;
            for (long i = lo; i < hi; i++) {
                b[i] += offset[k];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
