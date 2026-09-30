/* Kernel k19. */
#include "tsvc_b1/k19.h"

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

static real_t kernel_k19(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Each iteration i only ever touches slot i of u/v: the four index
         * arrays are read-only permutations fixed for the whole run, and the
         * apparent u[ku[i]]/v[kv[i]] "gather" in the second statement reads
         * back exactly the value the first statement in the SAME iteration
         * just scattered into u[ju[i]] (and, for v, the value produced for
         * this same i).  That is a location reused within one iteration,
         * not a value carried from a different iteration, so ordering i's
         * against each other changes nothing: the two statements for a
         * given i always run on the same thread in their original order,
         * which is all the correctness of this loop ever required.  Only
         * u, v, c, d and the index arrays are touched here (a, b, e are
         * only touched by pb_mix, outside this loop), so all of them can be
         * shared with no data-sharing clause needed for i itself, since the
         * loop variable of a canonical omp for is private by construct.
         */
        #pragma omp parallel for default(none) shared(u, v, c, d, ju, jv, ku, kv)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k19)
