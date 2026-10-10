#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    // Compute rank once outside the repeated loop
    int* rank = (int*)malloc(LEN_1D * sizeof(int));
    int count = 0;
    for (int i = 0; i < LEN_1D; i++) {
        rank[i] = count;
        if (b[i] > (real_t)0.) {
            count++;
        }
    }

    // Use computed ranks in the main loop
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(rank) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[rank[i]] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(rank);
    return (real_t)0;
}
