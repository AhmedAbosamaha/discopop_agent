#include "data.h"
#include <math.h>

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;
    for (int nl = 0; nl < iterations; nl++) {
        /* Phase 1: Find the maximum value in parallel.
           Each thread independently processes its range,
           removing the loop-carried dependence on x. */
        x = a[0];
        #pragma omp parallel for reduction(max:x)
        for (int i = 0; i < LEN_1D; ++i) {
            x = fmax(x, a[i]);
        }

        /* Phase 2: Find the first index with the maximum value (sequential).
           This preserves the original semantics and is fast enough. */
        index = 0;
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
