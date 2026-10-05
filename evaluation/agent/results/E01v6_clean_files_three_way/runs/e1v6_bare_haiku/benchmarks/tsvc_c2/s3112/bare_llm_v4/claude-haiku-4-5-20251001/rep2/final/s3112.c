#include "data.h"
#include <stdlib.h>

real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    int chunk_size = 4096;
    int num_chunks = (LEN_1D + chunk_size - 1) / chunk_size;
    real_t *chunk_sums = malloc((num_chunks + 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        chunk_sums[0] = (real_t)0.0;

        /* Pass 1: Compute local prefix sums for each chunk in parallel.
           Each thread processes a disjoint chunk, computing prefix sums locally.
           Threads write to disjoint ranges of b[], and each writes its chunk total to chunk_sums[c+1].
           Variables: c is loop index (implicit private); local_sum, start, end are private to each iteration;
           a, b, chunk_sums are shared (no races: non-overlapping accesses). */
        #pragma omp parallel for schedule(static) default(none) \
            shared(a, b, chunk_sums, LEN_1D, chunk_size, num_chunks)
        for (int c = 0; c < num_chunks; c++) {
            real_t local_sum = (real_t)0.0;
            int start = c * chunk_size;
            int end = (c + 1) * chunk_size < LEN_1D ? (c + 1) * chunk_size : LEN_1D;
            for (int i = start; i < end; i++) {
                local_sum += a[i];
                b[i] = local_sum;
            }
            chunk_sums[c + 1] = local_sum;
        }

        /* Pass 2: Compute prefix sum of chunk totals (sequential).
           This is necessary to determine the global offset for each chunk.
           Must run sequentially since each iteration depends on the previous one. */
        for (int c = 1; c <= num_chunks; c++) {
            chunk_sums[c] += chunk_sums[c - 1];
        }

        /* Pass 3: Add global offsets to local prefix sums in parallel.
           Each thread processes a disjoint chunk and adds the global offset (chunk_sums[c])
           to all elements in its range. Threads access disjoint ranges of b[].
           Variables: c is loop index (implicit private); offset, start, end are private;
           chunk_sums is shared (read-only from each thread's perspective). */
        #pragma omp parallel for schedule(static) default(none) \
            shared(b, chunk_sums, LEN_1D, chunk_size, num_chunks)
        for (int c = 0; c < num_chunks; c++) {
            real_t offset = chunk_sums[c];
            int start = c * chunk_size;
            int end = (c + 1) * chunk_size < LEN_1D ? (c + 1) * chunk_size : LEN_1D;
            for (int i = start; i < end; i++) {
                b[i] += offset;
            }
        }

        sum = b[LEN_1D - 1];
        dummy(a, b, c, d, e);
    }

    free(chunk_sums);
    return sum;
}
