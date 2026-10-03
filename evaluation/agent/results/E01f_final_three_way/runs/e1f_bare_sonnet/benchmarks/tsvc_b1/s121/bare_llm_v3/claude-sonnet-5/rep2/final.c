/* TSVC-2 loop s121, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s121.h"
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

static real_t kernel_s121(void)
{
    int j;
    /* Heap buffer (size scales with LEN_1D, so it must not be a stack array) that
     * holds a snapshot of 'a' taken before each repetition's inner loop runs.
     * Allocated once and reused across all R repetitions. */
    real_t *old_a = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* In the original sequential order, a[i] is written only when the loop
         * variable reaches i, and a[i+1] is read while the loop variable is still
         * at i (i.e. strictly before a[i+1] gets written at the later iteration
         * i+1). So every read in the serial run sees the value 'a' held before
         * this repetition's inner loop started: the loop reuses storage, it does
         * not carry a value forward between iterations. Running iterations out of
         * order (as a parallel schedule will) could let a thread read a[i+1]
         * *after* another thread already overwrote it, which would change the
         * result. We make the required "read sees pre-loop value" ordering
         * explicit by copying 'a' into old_a first (this copy loop's iterations
         * are independent: each writes a distinct old_a[i] from a distinct a[i])
         * and finishing that copy before the compute loop starts.
         * shared(a, old_a): both are the full arrays; each iteration i touches
         * only its own index i, so no two iterations conflict. */
        #pragma omp parallel for shared(a, old_a)
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }

        /* Now every iteration writes only a[i] and reads only old_a[i+1] and
         * b[i] (the pre-repetition snapshot and the untouched b array), so
         * iterations are fully independent and may run in any order or be split
         * across threads with any schedule.
         * private(j): j is scratch computed fresh each iteration from i and not
         * used after the loop, so each thread needs its own copy.
         * shared(a, b, old_a): a is written at disjoint indices per iteration;
         * b and old_a are read-only here. */
        #pragma omp parallel for private(j) shared(a, b, old_a)
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = old_a[j] + b[i];
        }
        pb_mix(nl);
    }
    free(old_a);
    return (real_t)0;
}

PB_MAIN(kernel_s121)
