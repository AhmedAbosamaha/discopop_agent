#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *indices = malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        j = -1;

        // Pass 1: Identify selected elements (sequential scan)
        int num_selected = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                indices[num_selected] = i;
                num_selected++;
            }
        }

        // Pass 2: Write selected elements to output (Do-All)
        for (int j_out = 0; j_out < num_selected; j_out++) {
            int i = indices[j_out];
            a[j_out] = b[i];
        }

        j = num_selected - 1;

        dummy(a, b, c, d, e);
    }

    free(indices);
    return (real_t)0;
}
