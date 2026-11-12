#include <stdatomic.h>
#include "data.h"

real_t kernel_s341(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        atomic_int j;
        atomic_store(&j, -1);
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                int idx = atomic_fetch_add(&j, 1) + 1;
                a[idx] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
