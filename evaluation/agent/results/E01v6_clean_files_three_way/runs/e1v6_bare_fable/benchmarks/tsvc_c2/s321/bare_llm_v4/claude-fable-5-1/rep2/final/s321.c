#include "data.h"
#include <stdlib.h>
#include <string.h>

/* Number of independent index segments [1, LEN_1D) is cut into.  It is a
   fixed constant (not derived from the thread count) so that every thread
   count and every schedule sees identical segment boundaries and therefore
   performs bit-identical arithmetic. */
#define S321_NCHUNK 128

/* Exact recurrence over [lo, hi):
       dst[i] = src[i] + dst[i-1] * b[i]
   where the value preceding dst[lo] is supplied as 'prev'.  The expression
   has the same shape as the original "a[i] += a[i-1] * b[i]" (one multiply
   feeding one add), so the rounding - including any FMA contraction the
   compiler applies - is identical to the sequential program. */
static void s321_chain(real_t *dst, const real_t *src, const real_t *bb,
                       long lo, long hi, real_t prev)
{
    for (long i = lo; i < hi; i++) {
        dst[i] = src[i] + prev * bb[i];
        prev = dst[i];
    }
}

real_t kernel_s321(void)
{
    long n = LEN_1D;
    real_t *orig = a;
    real_t *buf = (real_t *)malloc((size_t)n * sizeof(real_t));

    if (buf == NULL || n < 2) {
        /* No scratch memory: fall back to the original sequential code. */
        if (buf != NULL) free(buf);
        for (int nl = 0; nl < iterations; nl++) {
            for (int i = 1; i < LEN_1D; i++) {
                a[i] += a[i-1] * b[i];
            }
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }

    real_t *cur = orig;   /* holds the values at the start of this iteration */
    real_t *nxt = buf;    /* receives the values at the end of this iteration */

    real_t Y[S321_NCHUNK];  /* per segment: chain from start 0 -> value at end */
    real_t P[S321_NCHUNK];  /* per segment: product of b over the segment */
    real_t S[S321_NCHUNK];  /* per segment: speculated value at segment end */

    for (int nl = 0; nl < iterations; nl++) {

        /* ---- Phase A: speculative affine map of every segment -----------
           For segment k the exact chain satisfies x_end = Y[k] + P[k]*x_start
           up to rounding.  Four interleaved sub-chains keep this phase
           throughput-bound instead of latency-bound.  Only used to guess the
           starting values; exactness is restored in phases C/D. */
        #pragma omp parallel for shared(cur, b, Y, P, n)
        for (int k = 0; k < S321_NCHUNK; k++) {
            long lo = 1 + (long)(((long long)(n - 1) * k) / S321_NCHUNK);
            long hi = 1 + (long)(((long long)(n - 1) * (k + 1)) / S321_NCHUNK);
            long len = hi - lo;
            long q = len / 4;
            const real_t *a0 = cur + lo, *a1 = a0 + q, *a2 = a1 + q, *a3 = a2 + q;
            const real_t *b0 = b + lo,   *b1 = b0 + q, *b2 = b1 + q, *b3 = b2 + q;
            real_t y0 = (real_t)0, y1 = (real_t)0, y2 = (real_t)0, y3 = (real_t)0;
            real_t p0 = (real_t)1, p1 = (real_t)1, p2 = (real_t)1, p3 = (real_t)1;
            for (long j = 0; j < q; j++) {
                y0 = a0[j] + y0 * b0[j]; p0 = p0 * b0[j];
                y1 = a1[j] + y1 * b1[j]; p1 = p1 * b1[j];
                y2 = a2[j] + y2 * b2[j]; p2 = p2 * b2[j];
                y3 = a3[j] + y3 * b3[j]; p3 = p3 * b3[j];
            }
            for (long j = q; j < len - 3 * q; j++) {
                y3 = a3[j] + y3 * b3[j]; p3 = p3 * b3[j];
            }
            /* compose the four sub-segment maps in order */
            real_t y = y0, p = p0;
            y = y1 + p1 * y; p = p * p1;
            y = y2 + p2 * y; p = p * p2;
            y = y3 + p3 * y; p = p * p3;
            Y[k] = y;
            P[k] = p;
        }

        /* ---- Phase B: propagate speculated segment-end values (serial) -- */
        S[0] = Y[0] + P[0] * cur[0];
        for (int k = 1; k < S321_NCHUNK; k++) {
            S[k] = Y[k] + P[k] * S[k-1];
        }
        nxt[0] = cur[0];   /* index 0 is never written by the recurrence */

        /* ---- Phase C: exact chain per segment from its (speculated) start.
           Reads cur/b only, writes disjoint ranges of nxt. ---------------- */
        #pragma omp parallel for shared(cur, nxt, b, S, n)
        for (int k = 0; k < S321_NCHUNK; k++) {
            long lo = 1 + (long)(((long long)(n - 1) * k) / S321_NCHUNK);
            long hi = 1 + (long)(((long long)(n - 1) * (k + 1)) / S321_NCHUNK);
            real_t start = (k == 0) ? cur[0] : S[k-1];
            s321_chain(nxt, cur, b, lo, hi, start);
        }

        /* ---- Phase D: verify every segment boundary bit-for-bit (serial).
           Segment 0 is exact by construction.  If the exact value preceding
           segment k differs from the start it was computed with, recompute
           segment k from the exact value (cur is still the untouched input).
           By induction the final nxt equals the sequential result exactly. */
        for (int k = 1; k < S321_NCHUNK; k++) {
            long lo = 1 + (long)(((long long)(n - 1) * k) / S321_NCHUNK);
            long hi = 1 + (long)(((long long)(n - 1) * (k + 1)) / S321_NCHUNK);
            if (memcmp(&nxt[lo-1], &S[k-1], sizeof(real_t)) != 0) {
                s321_chain(nxt, cur, b, lo, hi, nxt[lo-1]);
            }
        }

        /* swap buffers; expose the current one through the global pointer */
        {
            real_t *tmp = cur;
            cur = nxt;
            nxt = tmp;
        }
        a = cur;
        dummy(a, b, c, d, e);
    }

    /* Leave the original buffer holding the final values. */
    if (cur != orig) {
        memcpy(orig, cur, (size_t)n * sizeof(real_t));
    }
    a = orig;
    free(buf);

    return (real_t)0;
}
