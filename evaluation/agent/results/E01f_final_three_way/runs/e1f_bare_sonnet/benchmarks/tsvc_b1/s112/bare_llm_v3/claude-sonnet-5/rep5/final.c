/* TSVC-2 loop s112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s112.h"
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

static real_t kernel_s112(void)
{
    /* The original loop walks i from LEN_1D-2 down to 0 doing a[i+1]=a[i]+b[i].
     * In that descending order every read of a[i] happens before the write
     * that would update a[i] (that write occurs at iteration i-1, which runs
     * later), so the whole sweep only ever reads pre-sweep values of a[] and
     * b[] -- it is equivalent to computing new_a[j] = old_a[j-1] + old_b[j-1]
     * for j = 1..LEN_1D-1 all at once from the old arrays. That "read old,
     * write new" property is what the reversed sequential order guaranteed;
     * arbitrary parallel interleaving does not preserve it, because a[i+1]
     * written by one iteration is the very value a later/earlier (in
     * parallel, unordered) iteration reads. We break that loop-carried true
     * dependence by materializing the new values into a separate heap buffer
     * tmp (read-old / write-new split across two independent passes), then
     * publishing tmp back into a[] in a second pass; the implicit barrier
     * between the two parallel loops guarantees all old values are captured
     * before any new value is published, matching the original semantics. */
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for default(none) shared(a, b, tmp)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            tmp[i+1] = a[i] + b[i];
        }
        #pragma omp parallel for default(none) shared(a, tmp)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            a[i+1] = tmp[i+1];
        }
        pb_mix(nl);
    }
    free(tmp);
    return (real_t)0;
}

PB_MAIN(kernel_s112)
