#include "data.h"
#include <stdlib.h>

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t** aa_new = (real_t**)malloc(LEN_2D * sizeof(real_t*));
        for (int ii = 0; ii < LEN_2D; ii++) {
            aa_new[ii] = (real_t*)malloc(LEN_2D * sizeof(real_t));
        }

        // Compute aa values in temporary buffer, update a sequentially
        for (int i = 1; i < LEN_2D; i++) {
            real_t a_temp;
            #pragma omp parallel for firstprivate(i) lastprivate(a_temp) shared(aa_new) 
            for (int j = 0; j < LEN_2D; j++) {
                a_temp = aa[j][i] - a[i-1];
                aa_new[j][i] = a_temp + bb[j][i];
            }
            a[i] = a_temp;
        }

        // Copy new aa values back to aa
 #pragma omp parallel for shared(aa_new) 
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 0; j < LEN_2D; j++) {
                aa[j][i] = aa_new[j][i];
            }
        }

        #pragma omp parallel for shared(aa_new) 
        for (int ii = 0; ii < LEN_2D; ii++) {
            free(aa_new[ii]);
        }
        free(aa_new);

        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
