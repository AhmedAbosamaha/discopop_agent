#include "data.h"
#include <stdlib.h>

real_t kernel_s316(void)
{
    real_t x;
    real_t* temp = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        int size = LEN_1D;

        // First pass: merge adjacent pairs from a directly into temp
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D / 2; ++i) {
            temp[i] = (a[2*i] < a[2*i+1]) ? a[2*i] : a[2*i+1];
        }
        if (LEN_1D % 2 == 1) {
            temp[LEN_1D / 2] = a[LEN_1D - 1];
        }
        size = (LEN_1D + 1) / 2;

        // Subsequent passes: merge pairs in temp
        while (size > 1) {
            for (int i = 0; i < size / 2; ++i) {
                temp[i] = (temp[2*i] < temp[2*i+1]) ? temp[2*i] : temp[2*i+1];
            }
            if (size % 2 == 1) {
                temp[size / 2] = temp[size - 1];
            }
            size = (size + 1) / 2;
        }

        x = temp[0];
        dummy(a, b, c, d, e, x);
    }

    free(temp);
    return x;
}
