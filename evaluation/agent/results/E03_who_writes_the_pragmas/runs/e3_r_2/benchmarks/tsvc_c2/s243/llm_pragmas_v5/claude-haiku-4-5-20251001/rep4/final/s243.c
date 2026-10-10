#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    // Allocate once outside the nl loop to avoid repeated malloc/free overhead
    real_t *a_old = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save a[] before the inner loop since line 9 reads a[i+1]
        // In sequential execution, that read gets the old value (before iteration i+1 updates it).
        // Snapshot it so parallel iterations are independent.
        memcpy(a_old, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for schedule(auto)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_old[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
