#include "data.h"
#include <stdlib.h>
#ifdef _OPENMP
#include <omp.h>
#endif

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        /* Parallel prefix sum (scan): b[i] = a[0]+...+a[i].
         * Split the range into `nthreads` contiguous chunks. Pass 1 computes
         * each chunk's own local prefix sum and its chunk total,
         * independently. Pass 2 adds the sum of all preceding chunks
         * (computed sequentially in between, O(nthreads) work) as an
         * offset to every element of a chunk. */
        int nthreads = 1;
#ifdef _OPENMP
        nthreads = omp_get_max_threads();
#endif
        if (nthreads > LEN_1D) nthreads = LEN_1D;
        if (nthreads < 1) nthreads = 1;

        int chunk = (LEN_1D + nthreads - 1) / nthreads;

        real_t *chunk_sum = (real_t *)malloc(sizeof(real_t) * (size_t)nthreads);

        #pragma omp parallel for default(none) \
            shared(a, b, chunk_sum) firstprivate(chunk, nthreads)
        for (int t = 0; t < nthreads; t++) {
            int start = t * chunk;
            int end = start + chunk;
            if (end > LEN_1D) end = LEN_1D;
            real_t local_sum = (real_t)0.0;
            for (int i = start; i < end; i++) {
                local_sum += a[i];
                b[i] = local_sum;
            }
            chunk_sum[t] = local_sum;
        }

        /* Exclusive prefix sum over the (small) per-chunk totals: turns
         * chunk_sum[t] into "sum of all elements in chunks before t", and
         * accumulates the grand total into `sum` (read after the loop). */
        real_t running = (real_t)0.0;
        for (int t = 0; t < nthreads; t++) {
            real_t cs = chunk_sum[t];
            chunk_sum[t] = running;
            running += cs;
        }
        sum = running;

        #pragma omp parallel for default(none) \
            shared(b, chunk_sum) firstprivate(chunk, nthreads)
        for (int t = 0; t < nthreads; t++) {
            int start = t * chunk;
            int end = start + chunk;
            if (end > LEN_1D) end = LEN_1D;
            real_t offset = chunk_sum[t];
            for (int i = start; i < end; i++) {
                b[i] += offset;
            }
        }

        free(chunk_sum);

        dummy(a, b, c, d, e);
    }
    return sum;
}
