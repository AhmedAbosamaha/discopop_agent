/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif

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

/* Evaluate the recurrence on the block [lo, hi) exactly as the sequential loop does,
 * reading the OLD a[i] from the snapshot a0 and carrying a[i-1], a[i-2] in private
 * scalars seeded with the block's two entry values (am1 = a[lo-1], am2 = a[lo-2]).
 * The expression keeps the shape of the original statement so rounding is identical. */
static void s322_block(const real_t *a0, int lo, int hi, real_t am2, real_t am1)
{
    real_t y = am2;   /* a[i-2] */
    real_t x = am1;   /* a[i-1] */
    for (int i = lo; i < hi; i++) {
        real_t v = a0[i] + x * b[i] + y * c[i];
        a[i] = v;
        y = x;
        x = v;
    }
}

static real_t kernel_s322(void)
{
    const long n = (long)LEN_1D - 2;      /* trip count of the recurrence loop */

    int nb = 1;                           /* number of blocks (= threads) */
#ifdef _OPENMP
    nb = omp_get_max_threads();
#endif
    if (nb < 1) nb = 1;
    if (n > 0 && (long)nb > n) nb = (int)n;

    real_t *a0   = (n > 0) ? (real_t *)malloc((size_t)LEN_1D * sizeof(real_t)) : NULL;
    int    *lo   = (int *)malloc((size_t)(nb + 1) * sizeof(int));
    int    *list = (int *)malloc((size_t)nb * sizeof(int));
    real_t *ent  = (real_t *)malloc((size_t)(2 * nb) * sizeof(real_t));

    /* Blocked evaluation is used unless there is nothing to do or no scratch memory. */
    const int blocked = (n > 0 && a0 != NULL && lo != NULL && list != NULL && ent != NULL);

    /* Block j covers [lo[j], lo[j+1]); lo[0] = 2, lo[nb] = LEN_1D. */
    if (blocked) {
        for (int j = 0; j <= nb; j++) lo[j] = (int)(2 + (n * (long)j) / nb);
    }

    for (int nl = 0; nl < R; nl++) {
        if (!blocked) {
            /* Original sequential form. */
            for (int i = 2; i < LEN_1D; i++) {
                a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
            }
        } else {
            /* Snapshot of a before this sweep: the in-place a[i] term on the right-hand side. */
#pragma omp parallel for schedule(static) shared(a0)
            for (int i = 0; i < LEN_1D; i++) {
                a0[i] = a[i];
            }

            /* Round 0: every block, seeded with the current (possibly stale) entry values. */
            int cnt = nb;
            for (int j = 0; j < nb; j++) {
                list[j]        = j;
                ent[2 * j]     = a[lo[j] - 2];
                ent[2 * j + 1] = a[lo[j] - 1];
            }

            /* Block j is exact once its entries are the exact a[lo-2], a[lo-1]; block 0
             * always is, and each round makes one more block exact, so nb rounds suffice.
             * A block is only redone when its entries changed bit for bit since it was
             * last evaluated. */
            for (int round = 0; round < nb && cnt > 0; round++) {
#pragma omp parallel for schedule(dynamic, 1) shared(a0, lo, list, ent) firstprivate(cnt)
                for (int t = 0; t < cnt; t++) {
                    int j = list[t];
                    s322_block(a0, lo[j], lo[j + 1], ent[2 * j], ent[2 * j + 1]);
                }

                cnt = 0;
                for (int j = 1; j < nb; j++) {
                    real_t am2 = a[lo[j] - 2];
                    real_t am1 = a[lo[j] - 1];
                    if (memcmp(&am2, &ent[2 * j], sizeof(real_t)) != 0 ||
                        memcmp(&am1, &ent[2 * j + 1], sizeof(real_t)) != 0) {
                        ent[2 * j]     = am2;
                        ent[2 * j + 1] = am1;
                        list[cnt++]    = j;
                    }
                }
            }
        }
        pb_mix(nl);
    }

    free(a0); free(lo); free(list); free(ent);
    return (real_t)0;
}

PB_MAIN(kernel_s322)
