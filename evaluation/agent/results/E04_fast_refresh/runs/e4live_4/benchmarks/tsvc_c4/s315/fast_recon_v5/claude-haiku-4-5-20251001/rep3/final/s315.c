#include "data.h"
#include <stdlib.h>

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;

    // Allocate arrays for chunk-wise maximum search
    #define CHUNK_SIZE 4096
    int num_chunks = (LEN_1D + CHUNK_SIZE - 1) / CHUNK_SIZE;
    real_t *chunk_maxes = (real_t *)malloc(num_chunks * sizeof(real_t));
    int *chunk_indices = (int *)malloc(num_chunks * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        index = 0;

        // Process each chunk independently (no loop-carried dependencies)
        #pragma omp parallel for firstprivate(num_chunks) shared(chunk_indices,chunk_maxes) 
        for (int chunk = 0; chunk < num_chunks; ++chunk) {
            int chunk_start = chunk * CHUNK_SIZE;
            int chunk_end = chunk_start + CHUNK_SIZE;
            if (chunk_end > LEN_1D) chunk_end = LEN_1D;

            real_t chunk_max = a[chunk_start];
            int chunk_idx = chunk_start;

            for (int i = chunk_start + 1; i < chunk_end; ++i) {
                if (a[i] > chunk_max) {
                    chunk_max = a[i];
                    chunk_idx = i;
                }
            }

            chunk_maxes[chunk] = chunk_max;
            chunk_indices[chunk] = chunk_idx;
        }

        // Merge results: find global maximum from all chunks
        x = chunk_maxes[0];
        index = chunk_indices[0];
        for (int i = 1; i < num_chunks; ++i) {
            if (chunk_maxes[i] > x) {
                x = chunk_maxes[i];
                index = chunk_indices[i];
            }
        }

        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }

    free(chunk_maxes);
    free(chunk_indices);

    return index + x + 1;
}
