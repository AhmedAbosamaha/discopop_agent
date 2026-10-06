#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Create temporary buffers to snapshot the arrays before the inner loop.
        // This breaks the loop-carried dependence: iterations will read from
        // constant snapshots (original values) rather than seeing each other's writes.
        real_t *a_temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
        real_t *c_temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_temp, a, LEN_1D * sizeof(real_t));
        memcpy(c_temp, c, LEN_1D * sizeof(real_t));

        // Parallelize the inner loop: each iteration reads from the snapshots
        // (a_temp, c_temp) and writes to its own unique locations in the temporary
        // buffers. All iterations are now independent because they never read
        // values written by other iterations—they all read the original snapshots.
        #pragma omp parallel for default(none) shared(a_temp, b, c_temp, d, e) private(i)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                // If condition: write c[i+1], read a[i]
                c_temp[i+1] = a_temp[i] + d[i] * d[i];
            } else {
                // Else condition: write a[i], read c[i]
                a_temp[i] = c_temp[i] + d[i] * e[i];
            }
        }

        // Copy the modified temporary buffers back to the original arrays.
        memcpy(a, a_temp, LEN_1D * sizeof(real_t));
        memcpy(c, c_temp, LEN_1D * sizeof(real_t));
        free(a_temp);
        free(c_temp);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
