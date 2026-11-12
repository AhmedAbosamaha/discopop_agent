#include "data.h"
#include <stdlib.h>

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *delta = (real_t *)malloc(LEN_1D * sizeof(real_t));
        // Pipeline stage 1: compute cumulative update contributions into delta (no loop-carried dependence on a/b)
        delta[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            delta[i] = a[i-1] * b[i];
        }
        // Pipeline stage 2: apply updates (each iteration independent in a)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += delta[i];
        }
        free(delta);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
