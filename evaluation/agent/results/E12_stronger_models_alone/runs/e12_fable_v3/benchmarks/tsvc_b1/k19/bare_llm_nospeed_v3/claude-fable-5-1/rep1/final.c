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
    const long n = (long)LEN_1D;

    /* Inspector/executor: iteration i touches u[ju[i]] (RMW), u[ku[i]] (R),
     * v[jv[i]] (W), v[kv[i]] (R).  Assign every iteration a level such that
     * all iterations of one level touch pairwise-distinct elements whenever a
     * write is involved; chains on one element keep their original order. */
    long *lastWU = (long *)malloc(sizeof(long) * (size_t)n);
    long *lastRU = (long *)malloc(sizeof(long) * (size_t)n);
    long *lastWV = (long *)malloc(sizeof(long) * (size_t)n);
    long *lastRV = (long *)malloc(sizeof(long) * (size_t)n);
    long *lvl    = (long *)malloc(sizeof(long) * (size_t)n);
    long *order  = (long *)malloc(sizeof(long) * (size_t)n);

    if (!lastWU || !lastRU || !lastWV || !lastRV || !lvl || !order) {
        free(lastWU); free(lastRU); free(lastWV); free(lastRV); free(lvl); free(order);
        for (int nl = 0; nl < R; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            pb_mix(nl);
        }
        return (real_t)0;
    }

    #pragma omp parallel for shared(lastWU, lastRU, lastWV, lastRV) firstprivate(n)
    for (long i = 0; i < n; i++) {
        lastWU[i] = 0; lastRU[i] = 0; lastWV[i] = 0; lastRV[i] = 0;
    }

    /* Sequential inspector (index arrays are constant across repetitions). */
    long maxL = 0;
    for (long i = 1; i < n; i++) {
        const long x = (long)ju[i];
        const long y = (long)ku[i];
        const long z = (long)jv[i];
        const long w = (long)kv[i];
        long L = 0;
        if (lastWU[x] > L) L = lastWU[x];
        if (lastRU[x] > L) L = lastRU[x];
        if (lastWU[y] > L) L = lastWU[y];
        if (lastWV[z] > L) L = lastWV[z];
        if (lastRV[z] > L) L = lastRV[z];
        if (lastWV[w] > L) L = lastWV[w];
        L += 1;
        lvl[i] = L;
        lastWU[x] = L;
        if (L > lastRU[y]) lastRU[y] = L;
        lastWV[z] = L;
        if (L > lastRV[w]) lastRV[w] = L;
        if (L > maxL) maxL = L;
    }

    long *start = (long *)calloc((size_t)(maxL + 2), sizeof(long));
    long *pos   = (long *)malloc(sizeof(long) * (size_t)(maxL + 2));
    if (!start || !pos) {
        free(start); free(pos);
        free(lastWU); free(lastRU); free(lastWV); free(lastRV); free(lvl); free(order);
        for (int nl = 0; nl < R; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            pb_mix(nl);
        }
        return (real_t)0;
    }

    /* Counting sort of iterations by level: level l occupies order[start[l] .. start[l+1]). */
    for (long i = 1; i < n; i++) start[lvl[i]]++;
    {
        long run = 0;
        for (long l = 1; l <= maxL; l++) {
            const long t = start[l];
            start[l] = run;
            run += t;
        }
        start[maxL + 1] = run;
        start[0] = 0;
    }
    for (long l = 0; l <= maxL + 1; l++) pos[l] = start[l];
    for (long i = 1; i < n; i++) order[pos[lvl[i]]++] = i;

    /* Executor: levels in order, iterations within a level independent. */
    for (int nl = 0; nl < R; nl++) {
        for (long l = 1; l <= maxL; l++) {
            const long lo = start[l];
            const long hi = start[l + 1];
            if (hi - lo < 64) {
                for (long p = lo; p < hi; p++) {
                    const long i = order[p];
                    u[ju[i]] += v[kv[i]] * c[i];
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
            } else {
                #pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) firstprivate(lo, hi)
                for (long p = lo; p < hi; p++) {
                    const long i = order[p];
                    u[ju[i]] += v[kv[i]] * c[i];
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
            }
        }
        pb_mix(nl);
    }

    free(start); free(pos);
    free(lastWU); free(lastRU); free(lastWV); free(lastRV); free(lvl); free(order);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
