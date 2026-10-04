#include "data.h"

real_t kernel_s313(void)
{
    real_t dot;
    dot = (real_t)0.;
    for (int i = 0; i < LEN_1D; i++) {
        dot += a[i] * b[i];
    }
    return dot;
}
