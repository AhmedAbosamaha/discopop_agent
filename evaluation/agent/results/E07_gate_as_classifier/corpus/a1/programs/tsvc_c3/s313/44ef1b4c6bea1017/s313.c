#include "data.h"

real_t kernel_s313(void)
{
    real_t dot;
    real_t *dots = (real_t *)malloc(iterations * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        dots[nl] = (real_t)0.;
        for (int i = 0; i < LEN_1D; i++) {
            dots[nl] += a[i] * b[i];
        }
    }

    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e, dots[nl]);
    }

    dot = dots[iterations - 1];
    free(dots);
    return dot;
}
