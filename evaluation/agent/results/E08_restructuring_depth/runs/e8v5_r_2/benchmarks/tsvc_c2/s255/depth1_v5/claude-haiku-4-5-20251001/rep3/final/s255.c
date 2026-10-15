#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            // Use modular arithmetic to handle wraparound indices without conditionals
            // Equivalent to: x = b[i==0 ? LEN_1D-1 : (i==1 ? 0 : i-1)]
            //              y = b[i==0 ? LEN_1D-2 : (i==1 ? LEN_1D-1 : i-2)]
            real_t x = b[(i - 1 + LEN_1D) % LEN_1D];
            real_t y = b[(i - 2 + LEN_1D) % LEN_1D];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
