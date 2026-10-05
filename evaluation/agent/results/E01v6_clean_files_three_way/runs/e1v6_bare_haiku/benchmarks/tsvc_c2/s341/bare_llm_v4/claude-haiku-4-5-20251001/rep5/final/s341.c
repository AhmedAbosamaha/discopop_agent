#include "data.h"

real_t kernel_s341(void)
{
    // Allocate work buffers for the three-phase filtering algorithm
    char *marks = malloc(LEN_1D * sizeof(char));
    int *offsets = malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Identify which elements pass the filter (parallel)
        // marks[i] = 1 if b[i] > 0, else 0
        // Each thread i independently computes marks[i]; no dependence.
        #pragma omp parallel for shared(marks, b)
        for (int i = 0; i < LEN_1D; i++) {
            marks[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        // Phase 2: Compute output positions via prefix sum (sequential)
        // offsets[i] = index in output array a[] for element i (if marks[i]).
        // This must be sequential because each offsets[i] depends on all marks[0..i-1].
        offsets[0] = marks[0] ? 0 : -1;
        int count = marks[0] ? 1 : 0;
        for (int i = 1; i < LEN_1D; i++) {
            if (marks[i]) {
                offsets[i] = count;
                count++;
            } else {
                offsets[i] = -1;
            }
        }

        // Phase 3: Write passing elements to output array (parallel)
        // Each thread i writes b[i] to a[offsets[i]] if marks[i].
        // No race: offsets[i] is unique for each i with marks[i]=1 by construction.
        #pragma omp parallel for shared(marks, offsets, a, b)
        for (int i = 0; i < LEN_1D; i++) {
            if (marks[i]) {
                a[offsets[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(offsets);
    free(marks);

    return (real_t)0;
}
