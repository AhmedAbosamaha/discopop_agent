#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Create temporary buffers to hold input values and break dependencies
        // Need extra space to handle positive offsets beyond LEN_1D-1
        long buf_size = LEN_1D + 1024;
        real_t *u_save = (real_t *)malloc(buf_size * sizeof(real_t));
        real_t *v_save = (real_t *)malloc(buf_size * sizeof(real_t));

        memcpy(u_save, u, buf_size * sizeof(real_t));
        memcpy(v_save, v, buf_size * sizeof(real_t));

        // Parallel loop: read from saved buffers, write to original arrays
        #pragma omp parallel for shared(u, v, c, d, u_save, v_save, off, far)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_save[i] + v_save[i + off] * c[i];
            v[i] = u_save[i + far] * d[i] + c[i];
        }

        free(u_save);
        free(v_save);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
