/* TSVC-2 loop s3112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s3112.h"

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

#define S3112_NCHUNK 256

static real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    /* fixed number of chunks: the set of additions performed does not depend on
       the thread count or the schedule */
    real_t csum[S3112_NCHUNK];
    real_t coff[S3112_NCHUNK];
    long chunk = ((long)LEN_1D + S3112_NCHUNK - 1) / S3112_NCHUNK;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: per-chunk local sums, chunks independent */
#pragma omp parallel for schedule(static) shared(a, csum) firstprivate(chunk)
        for (int c = 0; c < S3112_NCHUNK; c++) {
            long lo = (long)c * chunk;
            long hi = lo + chunk;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++) {
                s += a[i];
            }
            csum[c] = s;
        }
        /* sequential: entry offset of each chunk (the carried dependence lives here) */
        {
            real_t run = (real_t)0.0;
            for (int c = 0; c < S3112_NCHUNK; c++) {
                coff[c] = run;
                run += csum[c];
            }
        }
        /* pass 2: running sum within each chunk, starting from its offset */
#pragma omp parallel for schedule(static) shared(a, b, coff) firstprivate(chunk)
        for (int c = 0; c < S3112_NCHUNK; c++) {
            long lo = (long)c * chunk;
            long hi = lo + chunk;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            real_t s = coff[c];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        /* the original's sum after the loop is the last value written to b,
           taken before pb_mix touches b[LEN_1D-1] */
        sum = ((long)LEN_1D > 0) ? b[LEN_1D - 1] : (real_t)0.0;
        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
