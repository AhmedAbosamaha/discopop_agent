#include "data.h"

real_t kernel_s316(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        int num_chunks = 8;
        int chunk_size = LEN_1D / num_chunks;
        real_t chunk_mins[8];

 #pragma omp parallel for firstprivate(num_chunks) shared(chunk_mins) 
        for (int c = 0; c < num_chunks; c++) {
            int start = c * chunk_size;
            int end = (c == num_chunks - 1) ? LEN_1D : (c + 1) * chunk_size;

            chunk_mins[c] = a[start];
            for (int i = start + 1; i < end; ++i) {
                if (a[i] < chunk_mins[c]) {
                    chunk_mins[c] = a[i];
                }
            }
        }

        x = chunk_mins[0];
        for (int c = 1; c < num_chunks; c++) {
            if (chunk_mins[c] < x) {
                x = chunk_mins[c];
            }
        }

        dummy(a, b, c, d, e, x);
    }
    return x;
}
