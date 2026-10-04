#include <stdlib.h>
#include <omp.h>
#include "data.h"

real_t kernel_s341(void)
{
    int nthreads = 1;
    long* counts = NULL;
    #pragma omp parallel
    {
        #pragma omp single
        {
            nthreads = omp_get_num_threads();
            counts = (long*)calloc((size_t)nthreads + 1, sizeof(long));
        }
        int tid = omp_get_thread_num();
        long lo = (long)LEN_1D * tid / nthreads, hi = (long)LEN_1D * (tid + 1) / nthreads;
        long n = 0;
        for (long i = lo; i < hi; i++) if (b[i] > (real_t)0.) n++;
        counts[tid + 1] = n;
        #pragma omp barrier
        #pragma omp single
        for (int t = 0; t < nthreads; t++) counts[t + 1] += counts[t];
        long j = counts[tid] - 1;
        for (long i = lo; i < hi; i++) {
            if (b[i] > (real_t)0.) {
                j++;
                a[j] = b[i];
            }
        }
    }
    free(counts);
    return (real_t)0;
}
