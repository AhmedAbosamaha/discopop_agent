#include "data.h"

real_t kernel_s315(void)
{
    int index = 0;
    real_t x = 0, chksum = 0;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        x = a[0];
        {
            real_t best = a[0];
            int where = 0;
            for (int i = 0; i < LEN_1D; i++) {
                real_t v = a[i];
                if (v > best) {
                    best = v;
                    where = i;
                }
            }
            {
                if (best > x || (best == x && where < index)) {
                    x = best;
                    index = where;
                }
            }
        }
        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return index + x + 1;
}
