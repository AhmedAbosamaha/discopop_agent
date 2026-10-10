#include "data.h"

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        index = 0;
        #pragma omp parallel
        {
            real_t local_x = a[0];
            int local_index = 0;

            #pragma omp for
            for (int i = 0; i < LEN_1D; ++i) {
                if (a[i] > local_x) {
                    local_x = a[i];
                    local_index = i;
                }
            }

            #pragma omp critical
            {
                if (local_x > x) {
                    x = local_x;
                    index = local_index;
                }
            }
        }
        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return index + x + 1;
}
