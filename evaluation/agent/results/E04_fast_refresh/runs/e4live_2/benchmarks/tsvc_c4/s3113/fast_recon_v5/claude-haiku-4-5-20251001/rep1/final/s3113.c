#include "data.h"
#include <stdlib.h>

real_t kernel_s3113(void)
{
    real_t max;
    for (int nl = 0; nl < iterations; nl++) {
        int block_size = 1024;
        int num_blocks = (LEN_1D + block_size - 1) / block_size;
        real_t *block_max = malloc(num_blocks * sizeof(real_t));

 #pragma omp parallel for firstprivate(num_blocks) shared(block_max) 
        for (int b = 0; b < num_blocks; b++) {
            int start = b * block_size;
            int end = (b + 1) * block_size;
            if (end > LEN_1D) end = LEN_1D;

            real_t bmax = ABS(a[start]);
            for (int i = start + 1; i < end; i++) {
                if ((ABS(a[i])) > bmax) {
                    bmax = ABS(a[i]);
                }
            }
            block_max[b] = bmax;
        }

        max = block_max[0];
        for (int b = 1; b < num_blocks; b++) {
            if (block_max[b] > max) {
                max = block_max[b];
            }
        }

        free(block_max);
        dummy(a, b, c, d, e, max);
    }
    return max;
}
