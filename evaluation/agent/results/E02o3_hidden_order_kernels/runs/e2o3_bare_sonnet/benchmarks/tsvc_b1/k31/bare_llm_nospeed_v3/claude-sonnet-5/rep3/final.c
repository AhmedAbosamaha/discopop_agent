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

/* The inner loop over i is the one under study.  Per iteration it does:
 *     u[i] += v[i + off] * c[i];           (A)
 *     v[i]  = u[i + far] * d[i] + c[i];     (B)
 * Each iteration only ever WRITES u[i] and v[i] (distinct locations across
 * iterations), so the only thing that can make iterations depend on each
 * other is whether the value an iteration READS at an offset index was
 * already overwritten, this same pass, by some other iteration, or is
 * still the value the pass started with:
 *   - (A) reads v[i+off]. In the original sequential (increasing i) order,
 *     index i+off has already been finalized by (B) of iteration i+off
 *     iff i+off < i, i.e. iff off < 0. If off >= 0 the read always sees
 *     the pre-pass value of v.
 *   - (B) reads u[i+far]. Index i+far has already been finalized by (A)
 *     of iteration i+far (which precedes (B) of the same iteration when
 *     i+far == i) iff i+far <= i, i.e. iff far <= 0. If far > 0 the read
 *     always sees the pre-pass value of u.
 * off and far are fixed for the whole run, so exactly one of four regimes
 * applies every time; each is handled below by moving the "value written
 * by one iteration, read by another" dependence across an explicit full
 * barrier (the end of one parallel-for region) instead of deleting it:
 *   1) off >= 0 and far <= 0: (A) only ever needs pre-pass v (still
 *      untouched when (A) runs), so (A) can run fully first; (B) then
 *      needs the now-fully-written u, which is ready after (A)'s barrier.
 *   2) off <  0 and far >  0: symmetric - (B) only needs pre-pass u, so it
 *      runs fully first; (A) then needs the fully-written v.
 *   3) off >= 0 and far >  0: neither statement ever needs a same-pass
 *      value from the other array, but under an arbitrary parallel order
 *      a racing iteration could still overwrite the value before it is
 *      read, so both reads are taken from explicit pre-pass snapshots
 *      (u_old, v_old) copied before the single combined pass runs.
 *   4) off <  0 and far <= 0: (A) needs a same-pass value of v that is
 *      only finalized by (B), and (B) needs a same-pass value of u that
 *      is only finalized by (A) - a genuine mutual recurrence with no
 *      parallel decomposition, so this regime is left sequential.
 * u_old/v_old are heap-allocated (sized from the real arrays via sizeof,
 * so this works whatever padding LEN_1D/off/far require) and sized once
 * outside the repetition loop since their size never changes across
 * repetitions. */
static real_t kernel_k31(void)
{
    const size_t n_u = sizeof(u) / sizeof(u[0]);
    const size_t n_v = sizeof(v) / sizeof(v[0]);
    const int need_snapshot = (off >= 0 && far > 0);
    real_t *u_old = NULL;
    real_t *v_old = NULL;

    if (need_snapshot) {
        u_old = (real_t *)malloc(n_u * sizeof(real_t));
        v_old = (real_t *)malloc(n_v * sizeof(real_t));
    }

    for (int nl = 0; nl < R; nl++) {
        if (off >= 0 && far <= 0) {
            /* (A) first, using the still-untouched v; then (B), using the
             * now fully written u. */
            #pragma omp parallel for default(none) shared(u, v, c) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
            #pragma omp parallel for default(none) shared(u, v, d, c) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
        } else if (off < 0 && far > 0) {
            /* (B) first, using the still-untouched u; then (A), using the
             * now fully written v. */
            #pragma omp parallel for default(none) shared(u, v, d, c) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
            #pragma omp parallel for default(none) shared(u, v, c) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
        } else if (need_snapshot) {
            /* Neither statement needs a same-pass value from the other
             * array, but both reads must be pinned to the pre-pass value
             * so that a racing iteration elsewhere can't change what is
             * read: snapshot first, then compute both results from the
             * snapshot in one combined independent pass. */
            #pragma omp parallel for default(none) shared(u, u_old, n_u) schedule(static)
            for (size_t j = 0; j < n_u; j++) {
                u_old[j] = u[j];
            }
            #pragma omp parallel for default(none) shared(v, v_old, n_v) schedule(static)
            for (size_t j = 0; j < n_v; j++) {
                v_old[j] = v[j];
            }
            #pragma omp parallel for default(none) shared(u, v, u_old, v_old, c, d) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                real_t new_u = u_old[i] + v_old[i + off] * c[i];
                real_t new_v = u_old[i + far] * d[i] + c[i];
                u[i] = new_u;
                v[i] = new_v;
            }
        } else {
            /* off < 0 and far <= 0: a genuine mutual recurrence between u
             * and v with no cross-iteration independence to exploit. */
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
                v[i] = u[i + far] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }

    free(u_old);
    free(v_old);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
