#include "data.h"

#define S322_NB 256

real_t kernel_s322(void)
{
    long n = (long)LEN_1D - 2;           /* elements i = 2 .. LEN_1D-1 */
    long chunk = (n + S322_NB - 1) / S322_NB;

    /* per-block end state (value at e-1, value at e-2) for the
       particular (zero-start) run and two homogeneous runs */
    real_t yc[S322_NB], yp[S322_NB];
    real_t uc[S322_NB], up[S322_NB];
    real_t wc[S322_NB], wp[S322_NB];
    /* per-block correct incoming state: a_new[s-1], a_new[s-2] */
    real_t in1[S322_NB], in2[S322_NB];

    for (int nl = 0; nl < iterations; nl++) {
        int k;

        /* Phase 1: independent per-block summaries (read-only on a) */
#pragma omp parallel for default(none) shared(a, b, c, yc, yp, uc, up, wc, wp) firstprivate(chunk, n) schedule(static)
        for (k = 0; k < S322_NB; k++) {
            long s = 2 + (long)k * chunk;
            long end = s + chunk;
            if (end > 2 + n) end = 2 + n;
            real_t y1 = 0, y2 = 0;
            real_t u1 = 1, u2 = 0;
            real_t w1 = 0, w2 = 1;
            for (long i = s; i < end; i++) {
                real_t bi = b[i], ci = c[i];
                real_t ty = a[i] + y1 * bi + y2 * ci;
                real_t tu = u1 * bi + u2 * ci;
                real_t tw = w1 * bi + w2 * ci;
                y2 = y1; y1 = ty;
                u2 = u1; u1 = tu;
                w2 = w1; w1 = tw;
            }
            yc[k] = y1; yp[k] = y2;
            uc[k] = u1; up[k] = u2;
            wc[k] = w1; wp[k] = w2;
        }

        /* Phase 2: sequential carry propagation across blocks */
        {
            real_t x1 = a[1], x2 = a[0];
            for (k = 0; k < S322_NB; k++) {
                in1[k] = x1;
                in2[k] = x2;
                real_t n1 = yc[k] + uc[k] * x1 + wc[k] * x2;
                real_t n2 = yp[k] + up[k] * x1 + wp[k] * x2;
                x1 = n1;
                x2 = n2;
            }
        }

        /* Phase 3: each block recomputes with the original formula */
#pragma omp parallel for default(none) shared(a, b, c, in1, in2) firstprivate(chunk, n) schedule(static)
        for (k = 0; k < S322_NB; k++) {
            long s = 2 + (long)k * chunk;
            long end = s + chunk;
            if (end > 2 + n) end = 2 + n;
            real_t x1 = in1[k], x2 = in2[k];
            for (long i = s; i < end; i++) {
                real_t t = a[i] + x1 * b[i] + x2 * c[i];
                a[i] = t;
                x2 = x1;
                x1 = t;
            }
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
