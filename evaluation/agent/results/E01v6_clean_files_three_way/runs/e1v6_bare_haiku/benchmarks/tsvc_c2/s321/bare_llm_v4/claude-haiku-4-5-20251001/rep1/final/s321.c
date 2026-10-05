#include "data.h"

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Allocate work arrays for parallel inclusive scan
        real_t *sum = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *prod = (real_t *)malloc(LEN_1D * sizeof(real_t));

        if (!sum || !prod) {
            free(sum);
            free(prod);
            return (real_t)0;
        }

        // Initialize: sum[i] = a[i], prod[i] = b[i] (or 1 for i=0)
        // These track: sum[i] = accumulated value, prod[i] = product of b values
        #pragma omp parallel for schedule(static) private(i) shared(sum, prod, a, b)
        for (int i = 0; i < LEN_1D; i++) {
            sum[i] = a[i];
            prod[i] = (i == 0) ? (real_t)1 : b[i];
        }

        // Parallel inclusive scan using logarithmic stages
        // Each stage processes pairs at increasing distances
        // Stage d combines elements that are 2^d apart
        for (int d = 1; d < LEN_1D; d *= 2) {
            #pragma omp parallel for schedule(static) private(i) shared(sum, prod, d)
            for (int i = d; i < LEN_1D; i++) {
                // Combine position i with position i-d
                // new_sum[i] = sum[i] + sum[i-d] * prod[i]
                // new_prod[i] = prod[i] * prod[i-d]
                real_t temp_sum = sum[i] + sum[i-d] * prod[i];
                real_t temp_prod = prod[i] * prod[i-d];
                sum[i] = temp_sum;
                prod[i] = temp_prod;
            }
        }

        // Copy computed values back to a
        // sum[i] now contains the correctly accumulated value
        #pragma omp parallel for schedule(static) private(i) shared(a, sum)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = sum[i];
        }

        free(sum);
        free(prod);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
