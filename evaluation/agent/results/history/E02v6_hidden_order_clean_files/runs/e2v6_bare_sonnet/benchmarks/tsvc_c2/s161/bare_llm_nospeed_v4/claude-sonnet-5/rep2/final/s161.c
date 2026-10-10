#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    /* Scratch buffers holding the new values of a[] and c[] computed from
       the *original* (pre-sweep) data, so the parallel loop below never
       reads a value that another iteration of the same loop has written.
       Heap-allocated (not a local array) because LEN_1D can be huge, and
       allocated once outside the nl-loop so the extra cost stays O(1)
       relative to the original work, not O(iterations). */
    real_t *ta = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *tc = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        const int n = LEN_1D - 1;

        /* Pass 1: compute every iteration's result purely from the
           untouched a,b,c,d,e arrays. The only cross-iteration value is
           the "effective" c[i] that the else-branch would read, which is
           either the original c[i] (if iteration i-1 took the a[i]-branch)
           or a[i-1]+d[i-1]*d[i-1] (if iteration i-1 took the c-branch) --
           in both cases built only from original, never-written-here
           values of a/d at index i-1, so this is safe to recompute
           independently per i without any serial carry. Each iteration
           writes a disjoint scratch slot: ta[i] or tc[i+1]. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, ta, tc) firstprivate(n) schedule(static)
        for (int i = 0; i < n; ++i) {
            if (b[i] < (real_t)0.) {
                tc[i+1] = a[i] + d[i] * d[i];
            } else {
                real_t cval;
                if (i == 0 || b[i-1] >= (real_t)0.) {
                    cval = c[i];
                } else {
                    cval = a[i-1] + d[i-1] * d[i-1];
                }
                ta[i] = cval + d[i] * e[i];
            }
        }

        /* Pass 2: commit the results. b[] is read-only here (not touched
           by pass 1), so re-checking b[i] to pick which array to update
           is race-free and reproduces exactly what the sequential version
           would have stored at a[i] / c[i+1]. */
        #pragma omp parallel for default(none) shared(a, b, c, ta, tc) firstprivate(n) schedule(static)
        for (int i = 0; i < n; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = tc[i+1];
            } else {
                a[i] = ta[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(ta);
    free(tc);
    return (real_t)0;
}
