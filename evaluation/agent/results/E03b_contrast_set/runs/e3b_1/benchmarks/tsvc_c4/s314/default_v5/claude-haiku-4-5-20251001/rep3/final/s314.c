#include "data.h"
#include <stdlib.h>

real_t kernel_s314(void)
{
    real_t x;

    // Allocate outside outer loop to avoid repeated allocations
    int chunk_size = 1024;
    int num_chunks = (LEN_1D + chunk_size - 1) / chunk_size;
    real_t *chunk_max = (real_t *)malloc(num_chunks * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Compute max of each chunk independently (parallelizable loop)
 #pragma omp parallel for firstprivate(num_chunks) shared(chunk_max) 
        for (int chunk = 0; chunk < num_chunks; chunk++) {
            int start = chunk * chunk_size;
            int end = start + chunk_size;
            if (end > LEN_1D) end = LEN_1D;

            chunk_max[chunk] = a[start];
            for (int i = start + 1; i < end; i++) {
                if (a[i] > chunk_max[chunk]) {
                    chunk_max[chunk] = a[i];
                }
            }
        }

        // Combine chunk maxima to get global maximum
        x = chunk_max[0];
        for (int chunk = 1; chunk < num_chunks; chunk++) {
            if (chunk_max[chunk] > x) {
                x = chunk_max[chunk];
            }
        }

        dummy(a, b, c, d, e, x);
    }

    free(chunk_max);
    return x;
}
