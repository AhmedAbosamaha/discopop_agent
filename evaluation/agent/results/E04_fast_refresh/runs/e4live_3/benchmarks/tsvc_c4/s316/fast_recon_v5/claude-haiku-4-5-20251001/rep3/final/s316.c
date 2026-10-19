#include "data.h"
#include <stdlib.h>

real_t kernel_s316(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        #define CHUNK_SIZE 256
        int num_chunks = (LEN_1D + CHUNK_SIZE - 1) / CHUNK_SIZE;
        real_t *chunk_mins = (real_t *)malloc(num_chunks * sizeof(real_t));

        #pragma omp parallel for firstprivate(num_chunks) shared(chunk_mins) 
        for (int chunk_idx = 0; chunk_idx < num_chunks; ++chunk_idx) {
            int start = chunk_idx * CHUNK_SIZE;
            int end = start + CHUNK_SIZE < LEN_1D ? start + CHUNK_SIZE : LEN_1D;
            real_t min_in_chunk = a[start];
            for (int i = start + 1; i < end; ++i) {
                if (a[i] < min_in_chunk) {
                    min_in_chunk = a[i];
                }
            }
            chunk_mins[chunk_idx] = min_in_chunk;
        }

        x = chunk_mins[0];
        for (int i = 1; i < num_chunks; ++i) {
            if (chunk_mins[i] < x) {
                x = chunk_mins[i];
            }
        }

        free(chunk_mins);
        dummy(a, b, c, d, e, x);
    }
    return x;
}
