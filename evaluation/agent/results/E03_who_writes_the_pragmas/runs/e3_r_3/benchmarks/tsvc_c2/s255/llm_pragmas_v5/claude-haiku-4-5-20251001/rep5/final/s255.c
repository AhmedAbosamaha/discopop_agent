#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            real_t x_val, y_val;
            if (i == 0) {
                x_val = b[LEN_1D - 1];
                y_val = b[LEN_1D - 2];
            } else if (i == 1) {
                x_val = b[0];
                y_val = b[LEN_1D - 1];
            } else {
                x_val = b[i - 1];
                y_val = b[i - 2];
            }
            a[i] = (b[i] + x_val + y_val) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
