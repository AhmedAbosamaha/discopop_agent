#include "data.h"

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: mark which elements pass the filter
        int* pass_filter = (int*)malloc(sizeof(int) * LEN_1D);
        for (int i = 0; i < LEN_1D; i++) {
            pass_filter[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        // Phase 2: compute target index for each element via prefix sum
        int* target_index = (int*)malloc(sizeof(int) * LEN_1D);
        j = 0;
        for (int i = 0; i < LEN_1D; i++) {
            target_index[i] = j;
            j += pass_filter[i];
        }

        // Phase 3: copy filtered elements (no loop-carried dependencies—Do-All)
        for (int i = 0; i < LEN_1D; i++) {
            if (pass_filter[i]) {
                a[target_index[i]] = b[i];
            }
        }

        free(pass_filter);
        free(target_index);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
