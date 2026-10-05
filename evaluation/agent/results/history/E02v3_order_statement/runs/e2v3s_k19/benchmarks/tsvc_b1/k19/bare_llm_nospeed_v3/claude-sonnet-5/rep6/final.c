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
        /* The four index arrays ju/jv/ku/kv make this look like a general
         * scatter/gather with cross-iteration aliasing (u written at ju[i]
         * and read back at ku[i]; v written at jv[i] and read at kv[i]),
         * which is why a compiler can't vectorize/parallelize it on its own.
         * But the only dependence the sequential run actually relies on is
         * within one iteration: statement 2 must see statement 1's update
         * for that same i (they can reuse the same slot when ku[i]==ju[i],
         * resp. kv[i]==jv[i]). Across different i, the index arrays never
         * make two iterations touch the same u/v element, so no value has
         * to travel between iterations - the "location reused" is always
         * local to its own iteration, not shared with another one. That
         * means the i loop can run in any order/partitioning as long as
         * each iteration keeps its own statement order, which the loop body
         * below still does.
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
