#include "data.h"

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        index = 0;

        // Parallel pass: find maximum value across all threads
        // max_val: reduction variable to track the maximum
        // a: shared array being read by all threads
        real_t max_val = a[0];
        #pragma omp parallel for reduction(max:max_val) shared(a)
        for (int i = 1; i < LEN_1D; ++i) {
            if (a[i] > max_val) {
                max_val = a[i];
            }
        }
        x = max_val;

        // Sequential pass: find first index where value equals maximum
        // This preserves the original semantics of finding the first occurrence
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
