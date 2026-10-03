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

#define S321_NB 256
static long double s321_M[S321_NB];
static long double s321_C[S321_NB];
static long double s321_carry[S321_NB];

static real_t kernel_s321(void)
{
    const long n = (long)LEN_1D - 1;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: per-block affine map  a_out = M * a_in + C  (original a, b) */
        #pragma omp parallel for schedule(static) shared(s321_M, s321_C)
        for (int j = 0; j < S321_NB; j++) {
            long s = 1 + ((long)j * n) / S321_NB;
            long e = 1 + ((long)(j + 1) * n) / S321_NB;
            long double M = 1.0L, C = 0.0L;
            for (long i = s; i < e; i++) {
                long double bi = (long double)b[i];
                C = (long double)a[i] + bi * C;
                M = bi * M;
            }
            s321_M[j] = M;
            s321_C[j] = C;
        }
        /* pass 2: carry-in value a[s_j - 1] for every block (sequential, NB steps) */
        s321_carry[0] = (long double)a[0];
        for (int j = 0; j + 1 < S321_NB; j++) {
            s321_carry[j + 1] = s321_M[j] * s321_carry[j] + s321_C[j];
        }
        /* pass 3: rerun the recurrence inside each block from its carry-in */
        #pragma omp parallel for schedule(static) shared(s321_carry)
        for (int j = 0; j < S321_NB; j++) {
            long s = 1 + ((long)j * n) / S321_NB;
            long e = 1 + ((long)(j + 1) * n) / S321_NB;
            real_t x = (real_t)s321_carry[j];
            for (long i = s; i < e; i++) {
                x = a[i] + x * b[i];
                a[i] = x;
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s321)
