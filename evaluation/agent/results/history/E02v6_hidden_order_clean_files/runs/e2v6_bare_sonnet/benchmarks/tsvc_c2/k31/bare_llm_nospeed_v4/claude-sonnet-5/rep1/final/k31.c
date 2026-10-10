#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    /*
     * Original body, i = 1 .. LEN_1D-1 run in ascending order each pass:
     *   u[i] += v[i + off] * c[i];     (A_i)
     *   v[i]  = u[i + far] * d[i] + c[i]; (B_i)
     *
     * A value written by one iteration can be read by another: v[i] can be
     * read back as v[i'+off] (i' = i-off), and u[i] can be read back as
     * u[i'+far] (i' = i-far). Whether such a read sees the pre-pass value
     * or the value already produced this pass depends only on the sign of
     * off/far (fixed for the whole run): u is touched only by A-steps and
     * v only by B-steps, and in the original order every A-step with
     * index <= i has already run by the time B_i executes, regardless of
     * interleaving. So:
     *   - off >= 0: v[i+off] is always still the pre-pass value (no B-step
     *     has touched it yet), so all A-steps can be computed first,
     *     reading v in place.
     *   - far <= 0: u[i+far] is always the value already produced by that
     *     index's own A-step this pass.
     *   - far > 0: u[i+far] is still the pre-pass value, which the A pass
     *     above is about to overwrite, so it must be snapshotted first.
     *   - off < 0: v[i+off] needs the value produced by that index's own
     *     B-step this pass, so (assuming far > 0, so B only needs u's
     *     untouched pre-pass value) all B-steps are computed first,
     *     reading u in place, then all A-steps read the now-updated v.
     *
     * Either way the single loop becomes two passes, each of which only
     * writes its own index and reads data that is either never written
     * during that pass or fully settled before the pass starts -- so each
     * pass's iterations are mutually independent and may run in any order.
     */
    real_t *u_snapshot = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        if (off >= 0) {
            if (far > 0) {
                /* Capture u[i+far] before the A pass below overwrites u. */
                #pragma omp parallel for shared(u_snapshot, u, far)
                for (long i = 1; i < LEN_1D; i++) {
                    u_snapshot[i] = u[i + far];
                }
            }

            #pragma omp parallel for shared(u, v, c, off)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }

            #pragma omp parallel for shared(v, u, u_snapshot, c, d, far)
            for (long i = 1; i < LEN_1D; i++) {
                real_t uf = (far > 0) ? u_snapshot[i] : u[i + far];
                v[i] = uf * d[i] + c[i];
            }
        } else {
            #pragma omp parallel for shared(v, u, c, d, far)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }

            #pragma omp parallel for shared(u, v, c, off)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(u_snapshot);
    return (real_t)0;
}
