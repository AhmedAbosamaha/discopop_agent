#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    /* Allocate auxiliary array for prefix sum computation, reused across iterations */
    int *pos = (int *)malloc((LEN_1D + 1) * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        pos[0] = 0;

        /* Phase 1 (parallel): Mark which elements satisfy condition b[i] > 0
           Each thread i writes pos[i+1] independently, no race since disjoint indices */
        #pragma omp parallel for schedule(static) shared(pos, b) firstprivate(LEN_1D)
        for (int i = 0; i < LEN_1D; i++) {
            pos[i+1] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Phase 2 (sequential): Compute inclusive prefix sum to get output positions
           Sequential because each pos[i] depends on pos[i-1] */
        for (int i = 1; i <= LEN_1D; i++) {
            pos[i] += pos[i-1];
        }

        /* Phase 3 (parallel): Write filtered elements to array a at computed positions
           pos[i] is the cumulative count before position i (exclusive prefix sum),
           so elements satisfying the condition are written to a[pos[i]]
           Shared: a, b, pos; private: i (implicit loop variable) */
        #pragma omp parallel for schedule(static) shared(a, b, pos) firstprivate(LEN_1D)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }

        /* Final value of j: number of elements written minus 1 */
        j = pos[LEN_1D] - 1;

        dummy(a, b, c, d, e);
    }

    free(pos);
    return (real_t)0;
}
