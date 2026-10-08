#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int *selected = (int *)malloc(LEN_1D * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                selected[count] = i;
                count++;
            }
        }
        for (int j = 0; j < count; j++) {
            a[j] = b[selected[j]];
        }
        dummy(a, b, c, d, e);
    }
    free(selected);
    return (real_t)0;
}
