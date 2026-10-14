#include <stdlib.h>
#include "data.h"

real_t kernel_s123(void)
{
    int *pos = (int *)malloc((size_t)(LEN_1D/2) * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        for (int i = 0; i < (LEN_1D/2); i++) {
            j++;
            pos[i] = j;
            if (c[i] > (real_t)0.) {
                j++;
            }
        }
        for (int i = 0; i < (LEN_1D/2); i++) {
            a[pos[i]] = b[i] + d[i] * e[i];
            if (c[i] > (real_t)0.) {
                a[pos[i] + 1] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(pos);
    return (real_t)0;
}
