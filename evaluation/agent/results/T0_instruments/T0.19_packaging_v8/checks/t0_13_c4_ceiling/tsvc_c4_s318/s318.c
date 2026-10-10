#include "data.h"

real_t kernel_s318(void)
{
    int index = 0;
    real_t max = 0, chksum = 0;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);
        {
            real_t best = ABS(a[0]);
            int where = 0;
            for (int i = 1; i < LEN_1D; i++) {
                real_t v = ABS(a[(long)i * inc]);
                if (v > best) {
                    best = v;
                    where = i;
                }
            }
            {
                if (best > max || (best == max && where < index)) {
                    max = best;
                    index = where;
                }
            }
        }
        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
