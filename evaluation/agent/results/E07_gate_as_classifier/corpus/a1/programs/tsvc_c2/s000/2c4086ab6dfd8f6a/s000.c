#include "data.h"

real_t kernel_s000(void)
{
    if (iterations > 0) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] + 1;
        }
        for (int nl = 1; nl < iterations; nl++) {
            dummy(a, b, c, d, e);
            #pragma omp parallel for 
            for (int i = 0; i < LEN_1D; i++) {
                a[i] = b[i] + 1;
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
