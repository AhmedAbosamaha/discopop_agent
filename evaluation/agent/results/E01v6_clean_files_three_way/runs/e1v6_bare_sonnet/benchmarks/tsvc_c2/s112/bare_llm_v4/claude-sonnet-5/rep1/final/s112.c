#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    /* Number of elements the recurrence reads/updates per activation:
       i ranges over [0, LEN_1D-2], i.e. n = LEN_1D-1 values. */
    const int n = LEN_1D - 1;
    /* Heap-allocated scratch snapshot of a[0..n-1] as it stood at the
       start of the activation (size grows with LEN_1D, so it must not
       be a stack array). Allocated once, outside the nl loop, since its
       size never changes across activations. */
    real_t *tmp = (real_t *)malloc((size_t)n * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot a[0..n-1] before any update in this activation can
           touch it. Each iteration writes a distinct tmp[i] from a
           distinct a[i]: no overlap, trivially race-free. */
        #pragma omp parallel for shared(a, tmp) firstprivate(n) schedule(static)
        for (int i = 0; i < n; i++) {
            tmp[i] = a[i];
        }

        /* a[i+1] = a[i] + b[i], but reading from the pre-activation
           snapshot tmp instead of the live array a. In the original
           backward-order loop, every read of a[i] happened before any
           write could reach that slot, so the sequential result is
           exactly "a[i+1] = (value of a[i] at loop entry) + b[i]" for
           every i -- which is what tmp captures. Reads (tmp) and writes
           (a) now hit disjoint arrays and each i writes a unique a[i+1],
           so this is safe under any iteration order/schedule. */
        #pragma omp parallel for shared(a, b, tmp) firstprivate(n) schedule(static)
        for (int i = 0; i < n; i++) {
            a[i+1] = tmp[i] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(tmp);
    return (real_t)0;
}
