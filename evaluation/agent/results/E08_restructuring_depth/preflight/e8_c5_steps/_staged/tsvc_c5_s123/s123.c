#include <stdlib.h>
#include "data.h"

real_t kernel_s123(void)
{
    enum { NB = 64 };
    int *pos = (int *)malloc((size_t)(LEN_1D/2) * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        long count[NB], first[NB + 1];
        long n = (long)(LEN_1D/2);
        for (int k = 0; k < NB; k++) {
            long lo = n * k / NB;
            long hi = n * (k + 1) / NB;
            long m = 0;
            for (long i = lo; i < hi; i++) {
                m++;
                if (c[i] > (real_t)0.) {
                    m++;
                }
            }
            count[k] = m;
        }
        first[0] = 0;
        for (int k = 0; k < NB; k++) {
            first[k + 1] = first[k] + count[k];
        }
        for (int k = 0; k < NB; k++) {
            long lo = n * k / NB;
            long hi = n * (k + 1) / NB;
            long j = first[k] - 1;
            for (long i = lo; i < hi; i++) {
                j++;
                pos[i] = (int)j;
                if (c[i] > (real_t)0.) {
                    j++;
                }
            }
        }
        for (int i = 0; i < (LEN_1D/2); i++) {
            a[pos[i]] = b[i] + d[i] * e[i];
            if (c[i] > (real_t)0.) {
                a[pos[i] + 1] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(pos);
    return (real_t)0;
}
