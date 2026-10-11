#include <stdlib.h>
#include "data.h"

real_t kernel_s316(void)
{
    real_t x;
    int chunks = 256;
    real_t *chunk_mins = malloc(chunks * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        int chunk_size = (LEN_1D + chunks - 1) / chunks;

        // Compute minimum for each chunk (parallel over chunks, no loop-carried dependence)
 #pragma omp parallel for firstprivate(chunks) shared(chunk_mins) 
        for (int c = 0; c < chunks; ++c) {
            int start = c * chunk_size;
            int end = (c + 1) * chunk_size;
            if (end > LEN_1D) end = LEN_1D;

            if (start < LEN_1D) {
                real_t m = a[start];
                for (int i = start + 1; i < end; ++i) {
                    m = a[i] < m ? a[i] : m;
                }
                chunk_mins[c] = m;
            }
        }

        // Combine chunk minimums (sequential, small overhead)
        x = chunk_mins[0];
        for (int c = 1; c < chunks; ++c) {
            if (chunk_mins[c] < x) {
                x = chunk_mins[c];
            }
        }

        dummy(a, b, c, d, e, x);
    }

    free(chunk_mins);
    return x;
}
