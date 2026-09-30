/* Kernel k19. */
#include "tsvc_b1/k19.h"
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

static real_t kernel_k19(void)
{
    /* read_val[i] captures, for each i, the value v[kv[i]] held at the
     * exact point in the sequence where the original line
     * "u[ju[i]] += v[kv[i]] * c[i];" would have read it -- i.e. after all
     * v-writes from iterations 1..i-1 of the same nl round and before the
     * v-write of iteration i itself.  u[ku[i]] is never written by this
     * region's u[ju[i]] scatter (no such dependence was ever observed), so
     * the v-write value at line 20 does not depend on anything the i-loop
     * itself has computed; capturing it here does not change what gets
     * stored into v, only decouples the later u update from it. */
    real_t *read_val = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            read_val[i] = v[kv[i]];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += read_val[i] * c[i];
        }
        pb_mix(nl);
    }
    free(read_val);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
