#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 0; j < LEN_2D; j++) {
                a[i] = aa[j][i] - a[i-1];
                aa[j][i] = a[i] + bb[j][i];
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
