#include "data.h"
#include <omp.h>
#include <stdlib.h>

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        int num_threads = omp_get_max_threads();
        real_t *local_max = (real_t *)malloc(num_threads * sizeof(real_t));
        int *local_index = (int *)malloc(num_threads * sizeof(int));

        /* Initialize thread-local accumulators */
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();
            local_max[tid] = ABS(a[0]);
            local_index[tid] = 0;
        }

        /* Parallel search: each thread updates only its local max/index (no synchronization) */
        #pragma omp parallel for private(k)
        for (int i = 1; i < LEN_1D; i++) {
            k = i * inc;
            int tid = omp_get_thread_num();
            if (ABS(a[k]) > local_max[tid]) {
                local_max[tid] = ABS(a[k]);
                local_index[tid] = i;
            }
        }

        /* Sequential merge to find global max */
        for (int t = 0; t < num_threads; t++) {
            if (local_max[t] > max) {
                max = local_max[t];
                index = local_index[t];
            }
        }

        free(local_max);
        free(local_index);

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
