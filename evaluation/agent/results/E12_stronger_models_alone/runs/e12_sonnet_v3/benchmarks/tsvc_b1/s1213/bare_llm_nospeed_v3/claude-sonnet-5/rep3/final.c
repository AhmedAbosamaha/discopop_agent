/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"

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

static real_t kernel_s1213(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original interleaved loop had a[i] use the freshly-written b[i-1] while
         * b[i] used a[i+1] from before this inner loop began (a[i+1] is always
         * read before iteration i+1 can overwrite it). Splitting into two passes
         * makes both independent: pass 1 only reads the untouched a[] and writes
         * b[]; pass 2 only reads the now-complete b[] and writes a[]. b[0], never
         * written by pass 1, still holds the same value pass 2's i==1 case read
         * in the original. */
        #pragma omp parallel for default(none) shared(a, b, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        #pragma omp parallel for default(none) shared(a, b, c)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
