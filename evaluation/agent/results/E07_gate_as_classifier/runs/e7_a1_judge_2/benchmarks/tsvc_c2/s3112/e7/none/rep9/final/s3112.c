#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        // Allocate temporary buffers for parallel prefix sum computation
        real_t *in = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *out = (real_t *)malloc(LEN_1D * sizeof(real_t));

        // Copy input array a into working buffer in
        for (int i = 0; i < LEN_1D; i++) {
            in[i] = a[i];
        }

        // Compute prefix sums using logarithmic-depth algorithm
        // Each pass: stride doubling allows iterations to run independently
        for (int stride = 1; stride < LEN_1D; stride *= 2) {
            for (int i = 0; i < LEN_1D; i++) {
                if (i < stride) {
                    out[i] = in[i];
                } else {
                    out[i] = in[i] + in[i - stride];
                }
            }
            // Swap buffers: out becomes input for next pass
            real_t *tmp = in;
            in = out;
            out = tmp;
        }

        // Copy computed prefix sums to output array b
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = in[i];
        }

        // Extract final sum (last element of prefix sum array)
        sum = in[LEN_1D - 1];

        // Free temporary buffers
        free(in);
        free(out);

        dummy(a, b, c, d, e);
    }
    return sum;
}
