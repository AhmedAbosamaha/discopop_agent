#include "data.h"

real_t kernel_s322(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Track propagating values explicitly through scalar chain variables
        // to make the pipeline of computed values clear
        real_t carry_i_minus_1 = a[1];
        real_t carry_i_minus_2 = a[0];
        for (int i = 2; i < LEN_1D; i++) {
            real_t new_a_i = a[i] + carry_i_minus_1 * b[i] + carry_i_minus_2 * c[i];
            a[i] = new_a_i;
            carry_i_minus_2 = carry_i_minus_1;
            carry_i_minus_1 = new_a_i;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
