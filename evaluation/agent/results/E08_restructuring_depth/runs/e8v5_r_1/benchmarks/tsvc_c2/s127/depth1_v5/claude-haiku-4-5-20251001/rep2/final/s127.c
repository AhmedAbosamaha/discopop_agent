#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Move dummy() call to beginning of next iteration to restructure dependence
        if (nl > 0) {
            dummy(a, b, c, d, e);
        }

        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
    }

    // Call dummy() for the last iteration
    dummy(a, b, c, d, e);

    return (real_t)0;
}
