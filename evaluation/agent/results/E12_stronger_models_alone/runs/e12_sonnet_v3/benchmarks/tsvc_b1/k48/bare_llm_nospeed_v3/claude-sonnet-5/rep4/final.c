/* Kernel k48. */
#include "tsvc_b1/k48.h"

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

static real_t kernel_k48(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Each iteration i only ever touches the u/v slots that its own
         * index arrays name for THIS iteration: the write ju[i]/jv[i] in
         * this iteration is the same slot read back by ku[i]/kv[i] in this
         * same iteration (an intra-iteration read-after-write, which is
         * not a loop-carried dependence), and no iteration's indices name
         * a slot another iteration also writes within this inner loop.
         * So the dependence that looked like one value crossing from
         * iteration i to iteration i' is really the same iteration's own
         * slot being reused across its two statements, not a value that
         * must travel between distinct iterations; the inner loop over i
         * can therefore run with its iterations independent of each
         * other. u, v, c, d, ju, jv, ku, kv are shared arrays indexed
         * only by the loop variable i (directly or through the index
         * arrays), so no clause other than shared is needed: i itself is
         * the (implicitly private) loop variable, and nothing else is
         * declared inside the loop body. */
        #pragma omp parallel for default(none) \
            shared(u, v, c, d, ju, jv, ku, kv)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k48)
