#include "data.h"
#include <stdlib.h>

real_t kernel_s316(void)
{
    real_t x;
    int num_chunks = (LEN_1D + 255) / 256;
    real_t* chunk_mins = (real_t*)malloc(num_chunks * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for firstprivate(num_chunks) shared(chunk_mins) 
        for (int chunk = 0; chunk < num_chunks; ++chunk) {
            int start = chunk * 256;
            int end = start + 256;
            if (end > LEN_1D) end = LEN_1D;

            real_t min_in_chunk = a[start];
            for (int i = start + 1; i < end; ++i) {
                if (a[i] < min_in_chunk) {
                    min_in_chunk = a[i];
                }
            }
            chunk_mins[chunk] = min_in_chunk;
        }

        x = chunk_mins[0];
        for (int chunk = 1; chunk < num_chunks; ++chunk) {
            if (chunk_mins[chunk] < x) {
                x = chunk_mins[chunk];
            }
        }

        dummy(a, b, c, d, e, x);
    }

    free(chunk_mins);
    return x;
}
