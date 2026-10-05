/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"
#include <stdlib.h>

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
    /* pos[i] = number of elements among b[0..i-1] that are > 0 (exclusive prefix count
       of the "hit" predicate). This is exactly the value the original scalar counter j
       held right before it wrote a[j] for element i, so once pos[] is filled every
       iteration of the write loop below targets a distinct, already-known a[] slot and
       no longer depends on any other iteration. Sized by LEN_1D, so heap-allocated
       (LEN_1D can be far larger than a stack array could hold) and allocated once
       outside the nl loop since it is reused, unchanged in size, every repetition. */
    int *pos = (int *)malloc((size_t)LEN_1D * sizeof(int));

    for (int nl = 0; nl < R; nl++) {
        /* True sequential dependence: pos[i] depends on pos[i-1] and on whether
           b[i-1] was a hit, so this scan must run in index order. It is cheap (one
           compare plus a conditional increment per element) and is what frees the
           much heavier per-element write below to run in any order. */
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            pos[i] = count;
            if (b[i] > (real_t)0.) count++;
        }

        /* Independent now: every i that is a "hit" writes to a[pos[i]], a slot no
           other iteration touches (pos[] strictly increases across hits); every i
           that is not a hit touches nothing. b is only read. a[] indices at or past
           the final count keep whatever value they already held, exactly as in the
           original scalar version.
           Data sharing: a, b, pos are the shared global/heap arrays being read and
           written at disjoint locations; i is the loop variable, predetermined
           private by the worksharing construct; count is only read (used to derive
           pos[] before the parallel region) and not referenced inside the loop. */
        #pragma omp parallel for default(none) shared(a, b, pos) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }

        pb_mix(nl);
    }

    free(pos);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
