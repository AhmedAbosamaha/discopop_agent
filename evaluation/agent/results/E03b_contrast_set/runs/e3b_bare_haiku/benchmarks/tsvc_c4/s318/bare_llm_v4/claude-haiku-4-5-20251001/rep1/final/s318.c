#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        k = 0;
        index = 0;
        max = ABS(a[0]);

        // Parallel phase: compute maximum absolute value across all elements
        // Each thread independently scans its chunk and computes a local max,
        // which are then combined using the max reduction operator.
        #pragma omp parallel for reduction(max: max)
        for (int i = 1; i < LEN_1D; i++) {
            real_t val = ABS(a[i * inc]);
            if (val > max) {
                max = val;
            }
        }

        // Sequential phase: find the index of the maximum value.
        // We scan through once more to find which index holds the maximum.
        // If multiple elements have the same maximum value, the last index wins
        // (matching the original behavior where sequential updates overwrite).
        for (int i = 1; i < LEN_1D; i++) {
            if (ABS(a[i * inc]) == max) {
                index = i;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
