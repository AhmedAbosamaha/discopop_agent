/* TSVC-2 loop s321, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s321.h"

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

#include <stdlib.h>

/* First-order linear recurrence a[i] = a[i] + b[i]*a[i-1].  The dependence is a true
 * value flow, but the recurrence is affine in its carry-in, so it is solved as a
 * blocked scan: lanes of S321_LANE elements, processed S321_GROUP lanes at a time
 * (interleaved, so the per-lane latency chains overlap).  The decomposition is fixed
 * and independent of the thread count, so every run computes the same thing. */
#define S321_LANE  256L
#define S321_GROUP 8

static real_t kernel_s321(void)
{
    const long len     = (long)LEN_1D;
    const long n       = len - 1;                                   /* elements 1..len-1 */
    const long nlanes  = n > 0 ? (n + S321_LANE - 1) / S321_LANE : 0;
    const long ngroups = (nlanes + S321_GROUP - 1) / S321_GROUP;
    const size_t nalloc = (size_t)(nlanes > 0 ? nlanes : 1);
    real_t *endv  = (real_t *)malloc(nalloc * sizeof(real_t));   /* lane end value, carry-in 0 */
    real_t *prodv = (real_t *)malloc(nalloc * sizeof(real_t));   /* product of b over the lane */
    real_t *carry = (real_t *)malloc(nalloc * sizeof(real_t));   /* true carry-in of each lane */

    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: per lane, local recurrence with carry-in 0 and product of b.
         * Reads a and b only; each group writes only its own endv/prodv slots. */
        #pragma omp parallel for schedule(static) shared(a, b, endv, prodv, nlanes, ngroups, len)
        for (long g = 0; g < ngroups; g++) {
            const long l0   = g * S321_GROUP;
            const long nlg  = (nlanes - l0 < S321_GROUP) ? (nlanes - l0) : S321_GROUP;
            const long base = 1 + l0 * S321_LANE;
            const long lstart = base + (nlg - 1) * S321_LANE;
            const long lend   = (lstart + S321_LANE < len) ? (lstart + S321_LANE) : len;
            const long lastlen = lend - lstart;          /* 1..S321_LANE; other lanes are full */
            real_t y[S321_GROUP], p[S321_GROUP];
            for (long l = 0; l < nlg; l++) {
                y[l] = a[base + l * S321_LANE];
                p[l] = b[base + l * S321_LANE];
            }
            for (long j = 1; j < lastlen; j++) {
                for (long l = 0; l < nlg; l++) {
                    const long i = base + l * S321_LANE + j;
                    y[l] = a[i] + y[l] * b[i];
                    p[l] = p[l] * b[i];
                }
            }
            for (long j = lastlen; j < S321_LANE; j++) {
                for (long l = 0; l < nlg - 1; l++) {
                    const long i = base + l * S321_LANE + j;
                    y[l] = a[i] + y[l] * b[i];
                    p[l] = p[l] * b[i];
                }
            }
            for (long l = 0; l < nlg; l++) {
                endv[l0 + l]  = y[l];
                prodv[l0 + l] = p[l];
            }
        }

        /* Pass 2 (sequential, O(n / S321_LANE)): propagate the carry across lanes. */
        if (nlanes > 0) {
            carry[0] = a[0];
            for (long l = 1; l < nlanes; l++) {
                carry[l] = endv[l - 1] + prodv[l - 1] * carry[l - 1];
            }
        }

        /* Pass 3: per lane, the original recurrence started from its own carry-in.
         * Each lane keeps its running value in a local, so it never reads the
         * neighbouring lane's a[] and writes only its own range of a[]. */
        #pragma omp parallel for schedule(static) shared(a, b, carry, nlanes, ngroups, len)
        for (long g = 0; g < ngroups; g++) {
            const long l0   = g * S321_GROUP;
            const long nlg  = (nlanes - l0 < S321_GROUP) ? (nlanes - l0) : S321_GROUP;
            const long base = 1 + l0 * S321_LANE;
            const long lstart = base + (nlg - 1) * S321_LANE;
            const long lend   = (lstart + S321_LANE < len) ? (lstart + S321_LANE) : len;
            const long lastlen = lend - lstart;
            real_t prev[S321_GROUP];
            for (long l = 0; l < nlg; l++) {
                prev[l] = carry[l0 + l];
            }
            for (long j = 0; j < lastlen; j++) {
                for (long l = 0; l < nlg; l++) {
                    const long i = base + l * S321_LANE + j;
                    a[i] += prev[l] * b[i];
                    prev[l] = a[i];
                }
            }
            for (long j = lastlen; j < S321_LANE; j++) {
                for (long l = 0; l < nlg - 1; l++) {
                    const long i = base + l * S321_LANE + j;
                    a[i] += prev[l] * b[i];
                    prev[l] = a[i];
                }
            }
        }

        pb_mix(nl);
    }

    free(endv);
    free(prodv);
    free(carry);
    return (real_t)0;
}

PB_MAIN(kernel_s321)
