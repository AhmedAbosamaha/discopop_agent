#include "data.h"
#include <math.h>

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        index = 0;
        #pragma omp parallel for reduction(max:x) 
        for (int i = 1; i < LEN_1D; ++i) {
            x = fmax(x, a[i]);
        }
        for (int i = 0; i < LEN_1D; ++i) {
            if (a[i] == x) {
                index = i;
                break;
            }
        }
        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return index + x + 1;
}
