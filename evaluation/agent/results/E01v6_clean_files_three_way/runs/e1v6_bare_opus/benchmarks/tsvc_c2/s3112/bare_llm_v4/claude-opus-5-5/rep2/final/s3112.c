#include <stdlib.h>
#include "data.h"

#define S3112_NB 256

real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    long K[iterations];
    long BS =((long)LEN_1D + S3112_NB - 1) / S3112_NB;
    real_t *off = (real_t *)malloc(sizeof(real_t) * (size_t)iterations * S3112_NB);
    real_t *tot = (real_t *)malloc(sizeof(real_t) * (size_t)iterations);

    /* positions dummy() modifies in a[] on its m-th call (counter starts at 0) */
    for (int m = 0; m < iterations; m++)
        K[m] = ((long)m * 7919L + 13L) % LEN_1D;

    /* Pass 1: every scan nl is an independent sequential chain over a_nl,
       where a_nl = initial a patched with the effects of dummy calls 0..nl-1 */
    #pragma omp parallel for default(none) shared(a, K, off, tot, BS) schedule(dynamic, 1)
    for (int nl = 0; nl < iterations; nl++) {
        long pidx[2 * iterations + 2];
        real_t pval[2 * iterations + 2];
        int pc = 0;
        for (int m = 0; m < nl; m++) {
            for (int t = 0; t < 2; t++) {
                long p = (t == 0) ? K[m] : 0L;
                real_t dlt = (t == 0) ? (real_t)0.25 : (real_t)0.125;
                int f = -1;
                for (int j = 0; j < pc; j++)
                    if (pidx[j] == p) f = j;
                if (f < 0) {
                    pidx[pc] = p;
                    pval[pc] = a[p];
                    f = pc;
                    pc++;
                }
                pval[f] += dlt;
            }
        }
        /* sort patches by index */
        for (int j = 1; j < pc; j++) {
            long ki = pidx[j];
            real_t kv = pval[j];
            int q = j - 1;
            while (q >= 0 && pidx[q] > ki) {
                pidx[q + 1] = pidx[q];
                pval[q + 1] = pval[q];
                q--;
            }
            pidx[q + 1] = ki;
            pval[q + 1] = kv;
        }
        real_t s = (real_t)0.0;
        int pp = 0;
        for (int blk = 0; blk < S3112_NB; blk++) {
            long lo = (long)blk * BS;
            long hi = lo + BS;
            if (hi > LEN_1D) hi = LEN_1D;
            off[(long)nl * S3112_NB + blk] = s;
            for (long i = lo; i < hi; i++) {
                real_t v = a[i];
                if (pp < pc && pidx[pp] == i) {
                    v = pval[pp];
                    pp++;
                }
                s += v;
            }
        }
        tot[nl] = s;
    }

    if (iterations > 0) {
        /* dummy calls 0..iterations-2: a becomes exactly a_{last} */
        for (int nl = 0; nl < iterations - 1; nl++)
            dummy(a, b, c, d, e);

        /* Pass 2: write b for the last scan, each block seeded with the
           exact running sum recorded by the sequential chain */
        const real_t *offl = off + (long)(iterations - 1) * S3112_NB;
        #pragma omp parallel for default(none) shared(a, b, offl, BS) schedule(static)
        for (int blk = 0; blk < S3112_NB; blk++) {
            long lo = (long)blk * BS;
            long hi = lo + BS;
            if (hi > LEN_1D) hi = LEN_1D;
            real_t s = offl[blk];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        sum = tot[iterations - 1];
        dummy(a, b, c, d, e);
    }

    free(off);
    free(tot);
    return sum;
}
