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
    /* Inspector (index arrays are constant): who last wrote v[kv[i]] before i,
     * which i is the final writer of v[jv[i]], and whether the fast path is valid. */
    int *last = (int *)malloc(sizeof(int) * (size_t)LEN_1D);
    int *src = (int *)malloc(sizeof(int) * (size_t)LEN_1D);
    unsigned char *lastw = (unsigned char *)malloc((size_t)LEN_1D);
    unsigned char *mark = (unsigned char *)malloc((size_t)LEN_1D);
    real_t *vnew = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    int ok = (last && src && lastw && mark && vnew) ? 1 : 0;
    if (ok) {
        for (long i = 0; i < LEN_1D; i++) { last[i] = -1; mark[i] = 0; lastw[i] = 0; }
        src[0] = -1;
        #pragma omp parallel for lastprivate(ok) shared(last,src,mark) 
        for (long i = 1; i < LEN_1D; i++) {
            long a1 = (long)ju[i], a2 = (long)kv[i], a3 = (long)jv[i], a4 = (long)ku[i];
            if (a1 < 0 || a1 >= LEN_1D || a2 < 0 || a2 >= LEN_1D ||
                a3 < 0 || a3 >= LEN_1D || a4 < 0 || a4 >= LEN_1D) { ok = 0; }
            else {
                if (mark[a1]) ok = 0;
                mark[a1] = 1;
                src[i] = last[a2];
                last[a3] = (int)i;
            }
        }
        if (ok) {
            for (long i = 1; i < LEN_1D; i++)
                if (mark[(long)ku[i]]) ok = 0;
        }
        if (ok) {
            for (long i = 1; i < LEN_1D; i++)
                lastw[i] = (last[(long)jv[i]] == (int)i) ? 1 : 0;
        }
    }

    for (int nl = 0; nl < R; nl++) {
        if (ok) {
            for (long i = 1; i < LEN_1D; i++) {
                vnew[i] = u[ku[i]] * d[i] + c[i];
            }
            for (long i = 1; i < LEN_1D; i++) {
                int s = src[i];
                real_t vv = (s >= 0) ? vnew[s] : v[kv[i]];
                u[ju[i]] += vv * c[i];
            }
            for (long i = 1; i < LEN_1D; i++) {
                if (lastw[i]) v[jv[i]] = vnew[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(last); free(src); free(lastw); free(mark); free(vnew);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
