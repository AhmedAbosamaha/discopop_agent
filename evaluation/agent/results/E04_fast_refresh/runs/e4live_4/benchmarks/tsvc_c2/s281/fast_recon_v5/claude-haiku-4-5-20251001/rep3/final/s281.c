#include "data.h"

real_t kernel_s281(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First half: i reads from second half (unmodified), writes to first half
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D/2; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        // Second half: i reads from modified first half, writes to second half
 #pragma omp parallel for 
        for (int i = LEN_1D/2; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
