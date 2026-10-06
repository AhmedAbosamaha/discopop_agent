#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    real_t *uu = u, *vv = v, *cc = c, *dd = d;
    long lo = off, lf = far;
    real_t *w = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        if (lf > 0 && w != NULL) {
            /* new v depends only on old u (u[i+far] not yet updated) */
#pragma omp parallel for default(none) shared(uu, cc, dd, w, lf)
            for (long i = 1; i < LEN_1D; i++) {
                w[i] = uu[i + lf] * dd[i] + cc[i];
            }
            /* u update: v[i+off] is new only if it was written earlier in the sweep */
#pragma omp parallel for default(none) shared(uu, vv, cc, w, lo)
            for (long i = 1; i < LEN_1D; i++) {
                long j = i + lo;
                real_t vr = (lo < 0 && j >= 1) ? w[j] : vv[j];
                uu[i] += vr * cc[i];
            }
#pragma omp parallel for default(none) shared(vv, w)
            for (long i = 1; i < LEN_1D; i++) {
                vv[i] = w[i];
            }
        } else if (lf == 0 && lo >= 0) {
            /* v[i+off] is always old; v[i] uses the new u[i] */
#pragma omp parallel for default(none) shared(uu, vv, cc, lo)
            for (long i = 1; i < LEN_1D; i++) {
                uu[i] += vv[i + lo] * cc[i];
            }
#pragma omp parallel for default(none) shared(uu, vv, cc, dd)
            for (long i = 1; i < LEN_1D; i++) {
                vv[i] = uu[i] * dd[i] + cc[i];
            }
        } else {
            /* genuine recurrence: keep the original order */
            for (long i = 1; i < LEN_1D; i++) {
                uu[i] += vv[i + lo] * cc[i];
                vv[i] = uu[i + lf] * dd[i] + cc[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(w);
    return (real_t)0;
}
