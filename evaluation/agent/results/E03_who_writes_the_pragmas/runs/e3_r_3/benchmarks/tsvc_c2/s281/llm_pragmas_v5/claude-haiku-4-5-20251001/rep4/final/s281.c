#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(x)
        for (int i = 0; i < (LEN_1D + 1) / 2; i++) {
            // First iteration: i reads from reverse index, writes a[i]
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;

            // Second iteration: LEN_1D-1-i reads the a[i] just written
            // This executes atomically with the first to satisfy RAW
            if (i != LEN_1D-1-i) {
                x = a[i] + b[LEN_1D-1-i] * c[LEN_1D-1-i];
                a[LEN_1D-1-i] = x-(real_t)1.0;
                b[LEN_1D-1-i] = x;
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
