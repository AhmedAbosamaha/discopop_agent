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
    real_t *temp_updates_u = malloc(LEN_1D * sizeof(real_t));
    real_t *temp_v_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            temp_updates_u[i] = v[kv[i]] * c[i];
            temp_v_new[i] = u[ku[i]] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += temp_updates_u[i];
            v[jv[i]] = temp_v_new[i];
        }

        pb_mix(nl);
    }

    free(temp_updates_u);
    free(temp_v_new);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
