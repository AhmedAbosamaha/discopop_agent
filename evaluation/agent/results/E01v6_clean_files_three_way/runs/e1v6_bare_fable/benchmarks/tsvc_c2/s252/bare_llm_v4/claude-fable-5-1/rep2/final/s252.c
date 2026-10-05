#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* The scalar t carried b[i-1]*c[i-1] from the previous iteration.
           b and c are not written inside the loop, so each iteration
           recomputes its predecessor's product directly (0 for i == 0),
           making every iteration independent. */
#pragma omp parallel for default(none) shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t = (i > 0) ? b[i - 1] * c[i - 1] : (real_t) 0.;
            a[i] = s + t;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
