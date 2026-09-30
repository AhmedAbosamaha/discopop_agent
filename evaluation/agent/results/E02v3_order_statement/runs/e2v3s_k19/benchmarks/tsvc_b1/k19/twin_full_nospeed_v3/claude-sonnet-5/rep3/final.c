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
        /* The value line 19 used to read from v may have been produced by
         * any earlier iteration's line 20 within this same activation (a
         * RAW carried by the i loop).  That value must still reach its
         * reader, so instead of deleting the dependence we move it: the
         * loop producing v runs to completion before the loop that
         * consumes v to update u starts.  u is not touched in the first
         * loop and v is not touched in the second, so within each loop the
         * iterations only ever touch their own v[jv[i]] / u[ju[i]]
         * element and are independent of one another. */
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k19)
