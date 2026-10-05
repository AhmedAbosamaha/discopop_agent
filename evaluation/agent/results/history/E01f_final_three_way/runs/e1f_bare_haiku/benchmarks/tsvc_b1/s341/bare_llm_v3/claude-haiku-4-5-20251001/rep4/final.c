/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_s341(void)
{
    // Allocate temporary buffers for parallelization
    // is_pos[i]: marks whether b[i] is positive
    // offsets[i]: target index in a[] for element i (if positive)
    int *is_pos = (int *)malloc(LEN_1D * sizeof(int));
    int *offsets = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < R; nl++) {
        // Phase 1: Identify positive elements in parallel
        // Each thread independently checks b[i] and writes is_pos[i] (no races: disjoint writes)
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            is_pos[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        // Phase 2: Compute prefix sum to determine write positions
        // offsets[i] = count of positive elements in b[0..i-1]
        // This is sequential because each offsets[i] depends on all previous is_pos values
        offsets[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            offsets[i] = offsets[i-1] + is_pos[i-1];
        }

        // Phase 3: Write positive elements to their computed offsets in parallel
        // Each thread i writes a[offsets[i]] = b[i] if b[i] > 0
        // No races: all offsets[i] are distinct for positive elements (monotonic prefix sum)
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            if (is_pos[i]) {
                a[offsets[i]] = b[i];
            }
        }

        pb_mix(nl);
    }

    free(is_pos);
    free(offsets);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
