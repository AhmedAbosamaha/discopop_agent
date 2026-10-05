/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"
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

#define S322_MAXCH 256

static real_t kernel_s322(void)
{
    const long n = (long)LEN_1D;
    long nch = (n - 2) / 2048;
    if (nch < 1) nch = 1;
    if (nch > S322_MAXCH) nch = S322_MAXCH;
    long cs[S322_MAXCH + 1];
    for (long k = 0; k <= nch; k++)
        cs[k] = 2 + ((n > 2 ? n - 2 : 0) * k) / nch;

    double Py1[S322_MAXCH], Py2[S322_MAXCH];
    double U1[S322_MAXCH], U2[S322_MAXCH], V1[S322_MAXCH], V2[S322_MAXCH];
    real_t B1[S322_MAXCH], B2[S322_MAXCH];
    real_t *t = (real_t *)malloc((size_t)(n > 0 ? n : 1) * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        if (n > 2) {
            /* Phase 1: save inputs, compute each chunk's affine transfer map. */
            #pragma omp parallel for schedule(static) shared(t, cs, Py1, Py2, U1, U2, V1, V2) firstprivate(nch)
            for (long k = 0; k < nch; k++) {
                long s = cs[k], e = cs[k + 1];
                double y1 = 0.0, y2 = 0.0, u1 = 1.0, u2 = 0.0, v1 = 0.0, v2 = 1.0;
                for (long i = s; i < e; i++) {
                    real_t ai = a[i];
                    double bi = (double)b[i], ci = (double)c[i];
                    t[i] = ai;
                    double y = (double)ai + y1 * bi + y2 * ci;
                    double u = u1 * bi + u2 * ci;
                    double v = v1 * bi + v2 * ci;
                    y2 = y1; y1 = y;
                    u2 = u1; u1 = u;
                    v2 = v1; v1 = v;
                }
                Py1[k] = y1; Py2[k] = y2;
                U1[k] = u1; U2[k] = u2;
                V1[k] = v1; V2[k] = v2;
            }

            /* Phase 2 (serial, O(#chunks)): estimate incoming boundary of each chunk. */
            {
                double x1 = (double)a[1], x2 = (double)a[0];
                for (long k = 0; k < nch; k++) {
                    B1[k] = (real_t)x1;
                    B2[k] = (real_t)x2;
                    double nx1 = Py1[k] + U1[k] * x1 + V1[k] * x2;
                    double nx2 = Py2[k] + U2[k] * x1 + V2[k] * x2;
                    x1 = nx1; x2 = nx2;
                }
                B1[0] = a[1];
                B2[0] = a[0];
            }

            /* Phase 3: run the original recurrence per chunk from its boundary. */
            #pragma omp parallel for schedule(static) shared(t, cs, B1, B2) firstprivate(nch)
            for (long k = 0; k < nch; k++) {
                long s = cs[k], e = cs[k + 1];
                real_t p1 = B1[k], p2 = B2[k];
                for (long i = s; i < e; i++) {
                    real_t v = t[i] + p1 * b[i] + p2 * c[i];
                    a[i] = v;
                    p2 = p1; p1 = v;
                }
            }

            /* Phase 4 (serial): exact fix-up from the final values of the previous
             * chunk, until two consecutive values agree bit for bit. */
            for (long k = 1; k < nch; k++) {
                long s = cs[k], e = cs[k + 1];
                real_t p1 = a[s - 1], p2 = a[s - 2];
                long i = s;
                int same = 0;
                while (i < e && same < 2) {
                    real_t v = t[i] + p1 * b[i] + p2 * c[i];
                    if (memcmp(&v, &a[i], sizeof(real_t)) == 0) {
                        same++;
                    } else {
                        same = 0;
                        a[i] = v;
                    }
                    p2 = p1; p1 = v;
                    i++;
                }
            }
        }
        pb_mix(nl);
    }
    free(t);
    return (real_t)0;
}

PB_MAIN(kernel_s322)
