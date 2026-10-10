#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    for (int nl = 0; nl < iterations; nl++) {
        x = b[LEN_1D-1];
        y = b[LEN_1D-2];
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t x_i, y_i;
            if (i == 0) {
                x_i = b[LEN_1D-1];
                y_i = b[LEN_1D-2];
            } else if (i == 1) {
                x_i = b[0];
                y_i = b[LEN_1D-1];
            } else {
                x_i = b[i-1];
                y_i = b[i-2];
            }
            a[i] = (b[i] + x_i + y_i) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
