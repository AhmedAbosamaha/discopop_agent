/* Kernel k31. */
#include "tsvc_b1/k31.h"
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

static real_t kernel_k31(void)
{
    const long n = LEN_1D;
    const long fo = (long)(far);
    real_t *tmp = (real_t *)malloc((size_t)n * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        if ((long)(off) < 0 || tmp == NULL) {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
                v[i] = u[i + far] * d[i] + c[i];
            }
        } else {
            /* pass 1: new u values (v still holds pre-sweep values) */
            #pragma omp parallel for shared(tmp, n)
            for (long i = 1; i < n; i++) {
                real_t t = u[i];
                t += v[i + off] * c[i];
                tmp[i] = t;
            }
            /* pass 2: new v values; u still holds pre-sweep values */
            #pragma omp parallel for shared(tmp, n, fo)
            for (long i = 1; i < n; i++) {
                long j = i + fo;
                real_t uu = (fo > 0 || j < 1) ? u[j] : tmp[j];
                v[i] = uu * d[i] + c[i];
            }
            /* pass 3: commit u */
            #pragma omp parallel for shared(tmp, n)
            for (long i = 1; i < n; i++) {
                u[i] = tmp[i];
            }
        }
        pb_mix(nl);
    }
    free(tmp);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
