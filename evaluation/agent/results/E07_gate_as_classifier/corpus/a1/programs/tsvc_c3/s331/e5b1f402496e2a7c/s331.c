#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;

    // Scan and call dummy for iterations 0 through 46
    for (int nl = 0; nl < iterations - 1; nl++) {
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }

    // Compute final j (iteration 47's scan, from a's state after 47 prior dummy calls)
    j = -1;
    for (int i = 0; i < LEN_1D; i++) {
        if (a[i] < (real_t)0.) {
            j = i;
        }
    }
    chksum = (real_t) j;

    // Call dummy for iteration 47 (after j is computed)
    dummy(a, b, c, d, e, chksum);

    return j+1;
}
