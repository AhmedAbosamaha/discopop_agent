#include "data.h"

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);
        #pragma omp parallel
        {
            real_t local_max = ABS(a[0]);
            int local_index = 0;

            #pragma omp for
            for (int i = 1; i < LEN_1D; i++) {
                int k = inc * i;
                real_t val = ABS(a[k]);
                if (val > local_max) {
                    local_max = val;
                    local_index = i;
                }
            }

            #pragma omp critical
            {
                if (local_max > max) {
                    max = local_max;
                    index = local_index;
                }
            }
        }
        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
