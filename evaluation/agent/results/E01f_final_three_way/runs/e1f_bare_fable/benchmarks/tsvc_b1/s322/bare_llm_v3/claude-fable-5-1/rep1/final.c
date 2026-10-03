/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"
#include <stdlib.h>
#include <string.h>

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

/* Elements handled by one block of the recurrence (i = 2 .. LEN_1D-1 is cut into blocks). */
#define S322_BS 1024L

/* Bitwise comparison: never loops forever on NaN, distinguishes -0.0 from +0.0, so the
 * fixed point reached below is exactly the state the sequential loop produces. */
static int s322_same_bits(real_t x, real_t y)
{
    return memcmp(&x, &y, sizeof(real_t)) == 0;
}

static real_t kernel_s322(void)
{
    long n     = LEN_1D;
    long first = 2;                                   /* original loop: i = 2 .. n-1 */
    long nb    = (n > first) ? (n - first + S322_BS - 1) / S322_BS : 0;
    long nalloc = (nb > 0) ? nb : 1;

    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)(n > 0 ? n : 1));
    real_t *g1    = (real_t *)malloc(sizeof(real_t) * (size_t)nalloc);  /* a[s-1] a block ran with */
    real_t *g2    = (real_t *)malloc(sizeof(real_t) * (size_t)nalloc);  /* a[s-2] a block ran with */
    long   *list  = (long *)malloc(sizeof(long) * (size_t)nalloc);      /* blocks that must rerun */

    /* If any allocation failed, the blocked scheme is skipped and the original sequential
     * recurrence runs instead (same repetition loop, same pb_mix call). */
    int fallback = (a_old == NULL || g1 == NULL || g2 == NULL || list == NULL);
    if (fallback) nb = 0;

    for (int nl = 0; nl < R; nl++) {
        if (fallback) {
            for (int i = 2; i < LEN_1D; i++) {
                a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
            }
        }

        /* Snapshot the two input values of every block (sequential: nothing is being written). */
        for (long j = 0; j < nb; j++) {
            long s = first + j * S322_BS;
            g1[j] = a[s - 1];
            g2[j] = a[s - 2];
        }

        /* Pass 1: every block computes the recurrence from its snapshot inputs and saves the
         * original a[] of its range in a_old.  Blocks write disjoint ranges of a[] and a_old[]
         * and read neighbours only through g1/g2, so iterations are independent.
         * a, b, c are file-scope arrays and are shared. */
#pragma omp parallel for schedule(static) shared(a_old, g1, g2) firstprivate(nb, n, first)
        for (long j = 0; j < nb; j++) {
            long s = first + j * S322_BS;
            long e = s + S322_BS;
            if (e > n) e = n;
            real_t p1 = g1[j];              /* plays a[i-1] */
            real_t p2 = g2[j];              /* plays a[i-2] */
            for (long i = s; i < e; i++) {
                real_t old = a[i];
                a_old[i] = old;
                real_t v = old + p1 * b[i] + p2 * c[i];
                a[i] = v;
                p2 = p1;
                p1 = v;
            }
        }

        /* Which blocks ran with inputs that differ from what their predecessor produced? */
        long m = 0;
        for (long j = 1; j < nb; j++) {
            long s = first + j * S322_BS;
            if (!s322_same_bits(a[s - 1], g1[j]) || !s322_same_bits(a[s - 2], g2[j])) {
                g1[j] = a[s - 1];
                g2[j] = a[s - 2];
                list[m++] = j;
            }
        }

        /* Settle: rerun the blocks whose inputs changed, from a_old, with the new inputs.
         * Block 0 never reruns (a[0], a[1] are never written), so exactness propagates one
         * block per pass and this terminates after at most nb passes; usually 2 in total. */
        while (m > 0) {
#pragma omp parallel for schedule(static) shared(a_old, g1, g2, list) firstprivate(m, n, first)
            for (long t = 0; t < m; t++) {
                long j = list[t];
                long s = first + j * S322_BS;
                long e = s + S322_BS;
                if (e > n) e = n;
                real_t p1 = g1[j];
                real_t p2 = g2[j];
                int prev_same = 0;
                int settled = 0;
                long i = s;
                /* Once two consecutive recomputed values are bit-identical to the stored ones,
                 * every later value of the block is unchanged too, so stop early. */
                while (i < e && !settled) {
                    real_t v = a_old[i] + p1 * b[i] + p2 * c[i];
                    int cur_same = s322_same_bits(v, a[i]);
                    settled = cur_same && prev_same;
                    prev_same = cur_same;
                    a[i] = v;
                    p2 = p1;
                    p1 = v;
                    i++;
                }
            }

            /* Only successors of rerun blocks can see changed inputs.  list[] is increasing,
             * so successors are distinct and m2 <= t keeps the in-place rewrite safe. */
            long m2 = 0;
            for (long t = 0; t < m; t++) {
                long j = list[t] + 1;
                if (j < nb) {
                    long s = first + j * S322_BS;
                    if (!s322_same_bits(a[s - 1], g1[j]) || !s322_same_bits(a[s - 2], g2[j])) {
                        g1[j] = a[s - 1];
                        g2[j] = a[s - 2];
                        list[m2++] = j;
                    }
                }
            }
            m = m2;
        }

        pb_mix(nl);
    }

    free(a_old);
    free(g1);
    free(g2);
    free(list);
    return (real_t)0;
}

PB_MAIN(kernel_s322)
