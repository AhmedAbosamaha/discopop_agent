#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    char* matches = (char*) malloc(LEN_1D * sizeof(char));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(matches) 
        for (int i = 0; i < LEN_1D; i++) {
            matches[i] = (a[i] < (real_t)0.) ? 1 : 0;
        }
        j = -1;
        for (int i = LEN_1D - 1; i >= 0; i--) {
            if (matches[i]) {
                j = i;
                break;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    free(matches);
    return j+1;
}
