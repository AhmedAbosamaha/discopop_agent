#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    /* a_old: heap-allocated snapshot of 'a' taken before each activation's
       update, sized to the (input-dependent) array length LEN_1D.  Reading
       from this snapshot instead of the live array removes the
       anti-dependence between iteration i (reads a[i+1]) and iteration i+1
       (writes a[i+1]), making the update loop's iterations independent of
       execution order. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot pass: each a_old[i] depends only on a[i]; iterations are
           fully independent. a and a_old are shared arrays written/read at
           disjoint, per-iteration indices. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* Update pass: each iteration writes a[i] using only b[i] and the
           pre-update snapshot a_old[i+1], so no iteration depends on
           another iteration's write. j is declared inside the loop body,
           so it is private to each iteration by construction. */
        #pragma omp parallel for default(none) shared(a, a_old, b)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = a_old[j] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
