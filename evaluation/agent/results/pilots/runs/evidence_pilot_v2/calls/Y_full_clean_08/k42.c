#include "evk/k42.h"

static real_t kernel_k42(void)
{
    // Allocate temporary buffers to decouple u and v updates
    real_t *temp_u = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_v = (real_t*)malloc(LEN_1D * sizeof(real_t));

    // Initialize temporary buffers with current values
    memcpy(temp_u, u, LEN_1D * sizeof(real_t));
    memcpy(temp_v, v, LEN_1D * sizeof(real_t));

    // First loop: compute all u updates from v (original values)
    for (long i = 1; i < LEN_1D; i++) {
        temp_u[ju[i]] += temp_v[kv[i]] * c[i];
    }

    // Second loop: compute all v updates from u (now using updated u values)
    for (long i = 1; i < LEN_1D; i++) {
        temp_v[jv[i]] += temp_u[ku[i]] * d[i];
    }

    // Copy the results back to the original arrays
    for (long i = 0; i < LEN_1D; i++) {
        u[i] = temp_u[i];
        v[i] = temp_v[i];
    }

    // Free temporary buffers
    free(temp_u);
    free(temp_v);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
