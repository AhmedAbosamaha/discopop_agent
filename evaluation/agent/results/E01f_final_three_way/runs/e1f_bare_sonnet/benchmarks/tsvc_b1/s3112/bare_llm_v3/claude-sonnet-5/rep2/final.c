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

static real_t kernel_s3112(void)
{
    real_t sum;
    /* Fixed number of blocks for the chunked prefix scan below. Independent
     * of LEN_1D and of the thread count, so these arrays never grow with
     * the problem size and are safe to keep on the stack. */
    enum { NCHUNKS = 256 };
    real_t chunkSum[NCHUNKS];
    real_t offset[NCHUNKS];

    for (int nl = 0; nl < R; nl++) {
        /* Phase 1: each chunk c sums its own disjoint slice of a[] into
         * chunkSum[c]. Chunks never touch the same element of a[] or the
         * same slot of chunkSum[], so a and chunkSum stay shared with no
         * extra clause; lo, hi, s, i are declared inside the loop body so
         * they are already private per iteration and must not be listed. */
        #pragma omp parallel for schedule(static) shared(a, chunkSum)
        for (int c = 0; c < NCHUNKS; c++) {
            long lo = (long)c * LEN_1D / NCHUNKS;
            long hi = (long)(c + 1) * LEN_1D / NCHUNKS;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++) s += a[i];
            chunkSum[c] = s;
        }

        /* Phase 2: turn the per-chunk sums into exclusive prefix offsets.
         * offset[c] genuinely depends on offset[c-1], and NCHUNKS is tiny,
         * so this stays a plain sequential loop. running ends up holding
         * the grand total, i.e. exactly what the original sequential loop
         * left in sum after its last iteration. */
        real_t running = (real_t)0.0;
        for (int c = 0; c < NCHUNKS; c++) {
            offset[c] = running;
            running += chunkSum[c];
        }
        sum = running;

        /* Phase 3: each chunk redoes its own local scan, starting from its
         * precomputed offset, and writes its disjoint slice of b[]. a, b
         * and offset stay shared (disjoint access per chunk); lo, hi, s, i
         * are declared inside the loop body, so again no clause for them. */
        #pragma omp parallel for schedule(static) shared(a, b, offset)
        for (int c = 0; c < NCHUNKS; c++) {
            long lo = (long)c * LEN_1D / NCHUNKS;
            long hi = (long)(c + 1) * LEN_1D / NCHUNKS;
            real_t s = offset[c];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }

        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
