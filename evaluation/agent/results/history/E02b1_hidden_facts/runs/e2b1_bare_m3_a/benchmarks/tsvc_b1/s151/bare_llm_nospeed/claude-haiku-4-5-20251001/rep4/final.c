/* TSVC-2 loop s151, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s151.h"
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

void s151s(real_t a[LEN_1D], real_t b[LEN_1D],  int m)
{
    // Allocate temporary buffer to eliminate anti-dependence on a[i+m]
    real_t *temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    // First pass: compute all values in parallel using original a array
    // Anti-dependence removed: each iteration i reads a[i+m] and b[i], writes temp[i]
    // No iteration-to-iteration dependencies since all reads precede all writes
    #pragma omp parallel for shared(a, b, temp, m)
    for (int i = 0; i < LEN_1D-1; i++) {
        temp[i] = a[i + m] + b[i];
    }

    // Second pass: copy computed values back to array a in parallel
    // Each iteration i independently writes a[i] from temp[i]
    #pragma omp parallel for shared(a, temp)
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = temp[i];
    }

    free(temp);
}

static real_t kernel_s151(void)
{
    for (int nl = 0; nl < R; nl++) {
        s151s(a, b,  1);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s151)
