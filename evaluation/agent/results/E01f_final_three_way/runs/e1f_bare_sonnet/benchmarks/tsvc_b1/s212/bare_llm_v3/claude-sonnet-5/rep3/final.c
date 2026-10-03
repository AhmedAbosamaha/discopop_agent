/* TSVC-2 loop s212, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s212.h"

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

static real_t kernel_s212(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original body, per i: a[i] *= c[i]; then b[i] += a[i+1]*d[i].
         * The read of a[i+1] in iteration i always sees the value a[i+1]
         * had on entry to this loop: a[i+1] is only ever written by
         * iteration i+1, which (in the original sequential order) runs
         * strictly after iteration i has already read it. So the only
         * cross-iteration dependence is that every b[i] update must see
         * the pre-loop value of a, not a value some other iteration has
         * already overwritten. Splitting into two full passes reproduces
         * that exactly: pass 1 computes all b[i] from the untouched a
         * array (true read-only, no writes to a happen until pass 1 is
         * done), pass 2 then updates a[i] in place. Each pass now has
         * independent iterations (distinct i writes distinct b[i] or
         * a[i]), so each can be parallelized on its own. */
        #pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        #pragma omp parallel for default(none) shared(a, c) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s212)
