#include "data.h"

#define S121_NB 1024

real_t kernel_s121(void)
{
    const long long N = (long long)LEN_1D - 1;
    real_t bnd[S121_NB];
    int k;
    for (int nl = 0; nl < iterations; nl++) {
        /* save old value at each block's right boundary (a[hi]) */
        for (k = 0; k < S121_NB; k++) {
            long long hi = (k + 1) * N / S121_NB;
            bnd[k] = a[hi];
        }
#pragma omp parallel for default(none) shared(a, b, bnd) firstprivate(N) schedule(static)
        for (k = 0; k < S121_NB; k++) {
            long long lo = k * N / S121_NB;
            long long hi = (k + 1) * N / S121_NB;
            if (lo < hi) {
                for (long long i = lo; i < hi - 1; i++) {
                    a[i] = a[i + 1] + b[i];
                }
                a[hi - 1] = bnd[k] + b[hi - 1];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
