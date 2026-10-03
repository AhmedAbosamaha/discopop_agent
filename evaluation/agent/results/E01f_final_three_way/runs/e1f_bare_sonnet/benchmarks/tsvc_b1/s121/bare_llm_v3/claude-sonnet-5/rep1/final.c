/* TSVC-2 loop s121, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s121.h"
#include <stdlib.h>
#include <string.h>

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
    /* Heap-allocated snapshot of a's pre-sweep values; LEN_1D can be up to
     * 192000000, so this must never be a stack array. */
    real_t *a_snapshot = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* The inner loop reads a[i+1] before that slot is ever written in
         * this sweep (a write to index k only happens when the loop
         * variable reaches k, which is after it was read at i = k-1), so
         * every read sees the value a held before this sweep started.
         * Copying those pre-sweep values into a_snapshot and reading from
         * there (instead of from a itself) removes the anti-dependence
         * between iterations without changing a single computed value. */
        memcpy(a_snapshot, a, (size_t)LEN_1D * sizeof(real_t));
        #pragma omp parallel for default(none) shared(a, b, a_snapshot) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = a_snapshot[j] + b[i];
        }
        pb_mix(nl);
    }
    free(a_snapshot);
    return (real_t)0;
}

PB_MAIN(kernel_s121)
