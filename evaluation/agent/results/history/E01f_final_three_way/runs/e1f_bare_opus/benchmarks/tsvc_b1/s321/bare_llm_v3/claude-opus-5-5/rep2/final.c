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

#define S321_NCH 256

static real_t kernel_s321(void)
{
    static double Ysum[S321_NCH];
    static double Pprod[S321_NCH];
    static real_t carry[S321_NCH];
    const long n = (long)LEN_1D;
    const long cs = (n - 1 + S321_NCH - 1) / S321_NCH;

    for (int nl = 0; nl < R; nl++) {
        /* phase 1: per-chunk affine summary out = Y + in * P (reads a only) */
#pragma omp parallel for shared(a, b, Ysum, Pprod) firstprivate(n, cs) schedule(static)
        for (int c = 0; c < S321_NCH; c++) {
            long s = 1 + (long)c * cs;
            long e = s + cs;
            if (e > n) e = n;
            double y = 0.0, p = 1.0;
            for (long i = s; i < e; i++) {
                y = (double)a[i] + y * (double)b[i];
                p = p * (double)b[i];
            }
            Ysum[c] = y;
            Pprod[c] = p;
        }

        /* phase 2: propagate carries across chunks in order */
        carry[0] = a[0];
        for (int c = 0; c + 1 < S321_NCH; c++) {
            carry[c + 1] = (real_t)(Ysum[c] + (double)carry[c] * Pprod[c]);
        }

        /* phase 3: rerun original recurrence inside each chunk from its carry */
#pragma omp parallel for shared(a, b, carry) firstprivate(n, cs) schedule(static)
        for (int c = 0; c < S321_NCH; c++) {
            long s = 1 + (long)c * cs;
            long e = s + cs;
            if (e > n) e = n;
            real_t prev = carry[c];
            for (long i = s; i < e; i++) {
                a[i] += prev * b[i];
                prev = a[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s321)
