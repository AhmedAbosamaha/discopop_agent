#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;

    /* Phase 1: Save state of a before each dummy() call, then execute dummy() */
    real_t **a_states = (real_t **)malloc(iterations * sizeof(real_t *));
    for (int nl = 0; nl < iterations; nl++) {
        a_states[nl] = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_states[nl], a, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    /* Phase 2: Compute j for each nl using saved states (no loop-carried dependence on a) */
    #pragma omp parallel for private(chksum) lastprivate(j) shared(a_states) 
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a_states[nl][i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
    }

    /* Cleanup */
    for (int nl = 0; nl < iterations; nl++) {
        free(a_states[nl]);
    }
    free(a_states);

    return j+1;
}
