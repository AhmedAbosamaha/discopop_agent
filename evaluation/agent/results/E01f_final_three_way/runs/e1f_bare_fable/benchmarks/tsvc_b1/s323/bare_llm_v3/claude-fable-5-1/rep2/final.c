/* TSVC-2 loop s323, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s323.h"
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

/* Elements per chunk of the speculative parallel pass.  Chunk j covers
 * i in [1 + j*S323_CH, min(1 + (j+1)*S323_CH, LEN_1D)); its exact start
 * value is b[j*S323_CH] (the last element of chunk j-1, or b[0] for j==0). */
#define S323_CH 512L

static real_t kernel_s323(void)
{
    long n = LEN_1D;
    long nch = (n - 1 + S323_CH - 1) / S323_CH;          /* number of chunks */
    real_t *cand = (real_t *)malloc((size_t)(nch > 0 ? nch : 1) * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Predicted start value of every chunk: b[s-1] as the previous
         * repetition left it.  Snapshot BEFORE the parallel pass, because
         * chunk j-1 overwrites b[j*S323_CH]. */
        for (long j = 0; j < nch; j++)
            cand[j] = b[j * S323_CH];

        /* Speculative pass: each chunk runs the exact recurrence from its
         * predicted start value.  Chunks write disjoint ranges of a and b and
         * read only c, d, e (globals, shared) and cand; nothing reads b here. */
#pragma omp parallel for shared(cand) firstprivate(nch, n)
        for (long j = 0; j < nch; j++) {
            long s = 1 + j * S323_CH;
            long t = s + S323_CH;
            if (t > n) t = n;
            real_t bp = cand[j];
            for (long i = s; i < t; i++) {
                real_t ai = bp + c[i] * d[i];
                a[i] = ai;
                bp = ai + c[i] * e[i];
                b[i] = bp;
            }
        }

        /* Sequential validation / repair, carrying the exact chain value bx.
         * A chunk whose prediction matched bit-for-bit already holds the exact
         * sequential results; otherwise recompute it from the exact start. */
        real_t bx = b[0];
        for (long j = 0; j < nch; j++) {
            long s = 1 + j * S323_CH;
            long t = s + S323_CH;
            if (t > n) t = n;
            if (memcmp(&bx, &cand[j], sizeof(real_t)) != 0) {
                real_t bp = bx;
                for (long i = s; i < t; i++) {
                    real_t ai = bp + c[i] * d[i];
                    a[i] = ai;
                    bp = ai + c[i] * e[i];
                    b[i] = bp;
                }
                bx = bp;
            } else {
                bx = b[t - 1];
            }
        }
        pb_mix(nl);
    }
    free(cand);
    return (real_t)0;
}

PB_MAIN(kernel_s323)
