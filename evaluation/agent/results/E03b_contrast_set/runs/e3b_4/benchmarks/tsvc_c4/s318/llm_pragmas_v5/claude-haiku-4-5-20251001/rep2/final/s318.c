#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        // Pass 1: Find the maximum absolute value in parallel
        // Removes RAW on max by computing it with a reduction
        #pragma omp parallel for reduction(max:max)
        for (int i = 1; i < LEN_1D; i++) {
            int k_local = i * inc;  // Compute k locally, removing RAW on k
            real_t val = ABS(a[k_local]);
            if (val > max) {
                max = val;
            }
        }

        // Pass 2: Find the first index where maximum occurs in parallel
        // This finds the minimum i where ABS(a[i*inc]) == max
        if (ABS(a[0]) >= max) {
            // a[0] has the maximum value
            index = 0;
        } else {
            // Search for the first index with the maximum value
            int best_index = LEN_1D;
            #pragma omp parallel for reduction(min:best_index)
            for (int i = 1; i < LEN_1D; i++) {
                int k_local = i * inc;
                real_t val = ABS(a[k_local]);
                if (val == max) {
                    best_index = (i < best_index) ? i : best_index;
                }
            }
            index = best_index;
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
