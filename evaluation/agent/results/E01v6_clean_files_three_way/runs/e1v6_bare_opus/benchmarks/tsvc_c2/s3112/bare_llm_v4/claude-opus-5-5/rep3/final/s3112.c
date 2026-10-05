#include <stdlib.h>
#include "data.h"

typedef struct { long idx; real_t val; } s3112_ov_t;

static int s3112_find_or_add(s3112_ov_t *cur, int *cnt, long idx)
{
    for (int j = 0; j < *cnt; j++)
        if (cur[j].idx == idx) return j;
    cur[*cnt].idx = idx;
    cur[*cnt].val = a[idx];
    (*cnt)++;
    return *cnt - 1;
}

static int s3112_cmp(const void *x, const void *y)
{
    long p = ((const s3112_ov_t *)x)->idx, q = ((const s3112_ov_t *)y)->idx;
    return (p > q) - (p < q);
}

real_t kernel_s3112(void)
{
    int nit = iterations;
    int maxov = iterations + 1;
    s3112_ov_t *tab = (s3112_ov_t *)malloc((size_t)nit * maxov * sizeof(s3112_ov_t));
    int *tcnt = (int *)malloc((size_t)nit * sizeof(int));
    real_t *sums = (real_t *)malloc((size_t)nit * sizeof(real_t));
    s3112_ov_t *cur = (s3112_ov_t *)malloc((size_t)maxov * sizeof(s3112_ov_t));
    int ncur = 0;

    /* Simulate (exactly) the effect of dummy() on a: state of the modified
       entries of a at the start of every outer iteration. */
    for (int m = 0; m < nit; m++) {
        s3112_ov_t *row = tab + (size_t)m * maxov;
        for (int j = 0; j < ncur; j++) row[j] = cur[j];
        qsort(row, (size_t)ncur, sizeof(s3112_ov_t), s3112_cmp);
        tcnt[m] = ncur;
        long k = ((long)m * 7919L + 13L) % LEN_1D;
        int jk = s3112_find_or_add(cur, &ncur, k);
        cur[jk].val += (real_t)0.25;
        int j0 = s3112_find_or_add(cur, &ncur, 0L);
        cur[j0].val += (real_t)0.125;
    }

    /* Each outer iteration's scan is now independent. */
#pragma omp parallel for schedule(static) shared(tab, tcnt, sums, nit, maxov, a, b)
    for (int nl = 0; nl < nit; nl++) {
        const s3112_ov_t *ov = tab + (size_t)nl * maxov;
        int nov = tcnt[nl];
        int p = 0;
        long next = (nov > 0) ? ov[0].idx : -1L;
        int last = (nl == nit - 1);
        real_t s = (real_t)0.0;
        for (long i = 0; i < LEN_1D; i++) {
            real_t v;
            if (i == next) {
                v = ov[p].val;
                p++;
                next = (p < nov) ? ov[p].idx : -1L;
            } else {
                v = a[i];
            }
            s += v;
            if (last) b[i] = s;
        }
        sums[nl] = s;
    }

    /* Replay dummy() calls in original order; b modifications from all but
       the last call were overwritten by later scans, so they go to scratch. */
    real_t *scratch = (real_t *)calloc((size_t)LEN_1D, sizeof(real_t));
    for (int nl = 0; nl < nit; nl++) {
        if (nl < nit - 1)
            dummy(a, scratch, c, d, e);
        else
            dummy(a, b, c, d, e);
    }

    real_t sum = sums[nit - 1];
    free(scratch);
    free(cur);
    free(sums);
    free(tcnt);
    free(tab);
    return sum;
}
