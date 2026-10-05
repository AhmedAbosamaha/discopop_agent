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
    /* Scratch copy of the products v[i+off]*c[i] taken from the OLD v, so the
     * anti-dependence on v can be broken.  Heap allocated: grows with LEN_1D. */
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        if (far > 0 && off >= 0) {
            /* Iteration i of the original reads v[i+off] and u[i+far] before
             * they are overwritten: both are OLD values.  Split into three
             * passes with disjoint read/write sets. */
            #pragma omp parallel for shared(tmp, v, c)
            for (long i = 1; i < LEN_1D; i++) {
                tmp[i] = v[i + off] * c[i];
            }
            #pragma omp parallel for shared(u, v, c, d)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
            #pragma omp parallel for shared(u, tmp)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += tmp[i];
            }
        } else if (far > 0) {
            /* off < 0: the original reads the NEW v[i+off] (already written by
             * iteration i+off), and v[j] itself only depends on OLD u.  So
             * compute all of v first, then update u from the final v. */
            #pragma omp parallel for shared(u, v, c, d)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
            #pragma omp parallel for shared(u, v, c)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
        } else if (far == 0 && off >= 0) {
            /* v[i] uses the freshly updated u[i] of the same iteration; the
             * only cross-iteration access is the OLD v[i+off]. */
            #pragma omp parallel for shared(tmp, v, c)
            for (long i = 1; i < LEN_1D; i++) {
                tmp[i] = v[i + off] * c[i];
            }
            #pragma omp parallel for shared(u, v, c, d, tmp)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += tmp[i];
                v[i] = u[i] * d[i] + c[i];
            }
        } else {
            /* True recurrence (value flows forward through u): keep serial. */
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
                v[i] = u[i + far] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(tmp);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
