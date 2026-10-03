/* Kernel k31. */
#include "tsvc_b1/k31.h"

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
    for (int nl = 0; nl < R; nl++) {
        /* Allocate temporary buffers to capture old values of u and v.
           This removes the forward dependence: each parallel iteration reads
           from the old state, not from concurrent writes. */
        real_t *u_old = malloc(LEN_1D * sizeof(real_t));
        real_t *v_old = malloc(LEN_1D * sizeof(real_t));

        /* Copy old values before parallel loop */
        for (long i = 0; i < LEN_1D; i++) {
            u_old[i] = u[i];
            v_old[i] = v[i];
        }

        /* Parallel loop: each iteration (i) is independent because it reads from
           u_old and v_old (shared buffers, read-only) and writes to unique
           locations u[i] and v[i].
           Data-sharing: i is implicitly private (loop variable);
           u_old, v_old are shared read-only buffers;
           u, v are shared, each iteration writes to a unique element;
           c, d, off, far are shared read-only. */
        #pragma omp parallel for
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_old[i] + v_old[i + off] * c[i];
            v[i] = u_old[i + far] * d[i] + c[i];
        }

        /* Free temporary buffers */
        free(u_old);
        free(v_old);

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k31)
