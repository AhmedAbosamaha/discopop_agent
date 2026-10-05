#include "data.h"

real_t kernel_s292(void)
{
    int im1, im2;
    for (int nl = 0; nl < iterations; nl++) {
        /* wrap-around indices in closed form: peel i=0 and i=1 */
        im1 = LEN_1D-1;
        im2 = LEN_1D-2;
        a[0] = (b[0] + b[im1] + b[im2]) * (real_t).333;
        a[1] = (b[1] + b[0] + b[LEN_1D-1]) * (real_t).333;
        #pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1] + b[i-2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
