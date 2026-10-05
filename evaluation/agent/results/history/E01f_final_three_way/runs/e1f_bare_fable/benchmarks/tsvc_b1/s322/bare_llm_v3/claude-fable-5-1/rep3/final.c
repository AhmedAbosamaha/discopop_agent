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

/* Bitwise comparison (NaN-safe, distinguishes -0 from +0: stricter is safe here). */
static int s322_same_bits(real_t x, real_t y)
{
    return memcmp(&x, &y, sizeof(real_t)) == 0;
}

static real_t kernel_s322(void)
{
    /* Elements i in [2, LEN_1D) are updated; a[0], a[1] are never written by the kernel. */
    const long n = (long)LEN_1D - 2;
    long nch = n / 128;                 /* chunk count depends only on LEN_1D */
    if (nch < 1) nch = 1;
    if (nch > 2048) nch = 2048;
    if (n <= 0) nch = 0;

    real_t *orig = (real_t *)malloc((size_t)(LEN_1D > 0 ? LEN_1D : 1) * sizeof(real_t));
    size_t csz = (size_t)(nch > 0 ? nch : 1);
    real_t *P1 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *Q1 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *R1 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *P2 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *Q2 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *R2 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *Xg = (real_t *)malloc(csz * sizeof(real_t));
    real_t *Yg = (real_t *)malloc(csz * sizeof(real_t));
    real_t *E1 = (real_t *)malloc(csz * sizeof(real_t));
    real_t *E2 = (real_t *)malloc(csz * sizeof(real_t));

    int have_bufs = (orig && P1 && Q1 && R1 && P2 && Q2 && R2 && Xg && Yg && E1 && E2);

    for (int nl = 0; nl < R; nl++) {
        if (!have_bufs) {
            /* Allocation failure: original sequential recurrence. */
            for (int i = 2; i < LEN_1D; i++) {
                a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
            }
        } else {
            /* Pass 1: per chunk, express the chunk's last two values as a linear form
             * p + q*X + r*Y in the (unknown) entry values X = x[lo-1], Y = x[lo-2].
             * Reads a,b,c only; writes orig[] and this chunk's own coefficient slots. */
#pragma omp parallel for schedule(static) shared(a, b, c, orig, P1, Q1, R1, P2, Q2, R2) firstprivate(n, nch)
            for (long ch = 0; ch < nch; ch++) {
                long lo = 2 + (n * ch) / nch;
                long hi = 2 + (n * (ch + 1)) / nch;
                real_t p1 = (real_t)0, q1 = (real_t)1, r1 = (real_t)0;  /* form of x[i-1] */
                real_t p2 = (real_t)0, q2 = (real_t)0, r2 = (real_t)1;  /* form of x[i-2] */
                for (long i = lo; i < hi; i++) {
                    real_t ai = a[i], bi = b[i], ci = c[i];
                    orig[i] = ai;
                    real_t np = ai + p1 * bi + p2 * ci;
                    real_t nq = q1 * bi + q2 * ci;
                    real_t nr = r1 * bi + r2 * ci;
                    p2 = p1; q2 = q1; r2 = r1;
                    p1 = np; q1 = nq; r1 = nr;
                }
                P1[ch] = p1; Q1[ch] = q1; R1[ch] = r1;
                P2[ch] = p2; Q2[ch] = q2; R2[ch] = r2;
            }

            /* Serial, O(#chunks): guessed entry values of every chunk. */
            if (nch > 0) {
                Xg[0] = a[1];
                Yg[0] = a[0];
            }
            for (long ch = 1; ch < nch; ch++) {
                real_t xp = Xg[ch - 1], yp = Yg[ch - 1];
                Xg[ch] = P1[ch - 1] + Q1[ch - 1] * xp + R1[ch - 1] * yp;
                Yg[ch] = P2[ch - 1] + Q2[ch - 1] * xp + R2[ch - 1] * yp;
            }

            /* Pass 2: run the original recurrence inside each chunk from its guessed
             * entry values.  Each chunk reads/writes only its own a[lo..hi) range. */
#pragma omp parallel for schedule(static) shared(a, b, c, Xg, Yg, E1, E2) firstprivate(n, nch)
            for (long ch = 0; ch < nch; ch++) {
                long lo = 2 + (n * ch) / nch;
                long hi = 2 + (n * (ch + 1)) / nch;
                real_t x1 = Xg[ch], x2 = Yg[ch];
                for (long i = lo; i < hi; i++) {
                    a[i] = a[i] + x1 * b[i] + x2 * c[i];
                    x2 = x1;
                    x1 = a[i];
                }
                E1[ch] = x1;
                E2[ch] = x2;
            }

            /* Serial verification: a chunk whose guessed entry values are bit-identical to
             * the exact end values of its predecessor already holds the exact sequential
             * result; otherwise recompute it sequentially from the saved inputs. */
            if (nch > 0) {
                real_t ex1 = E1[0], ex2 = E2[0];   /* chunk 0 started from exact values */
                for (long ch = 1; ch < nch; ch++) {
                    if (s322_same_bits(ex1, Xg[ch]) && s322_same_bits(ex2, Yg[ch])) {
                        ex1 = E1[ch];
                        ex2 = E2[ch];
                    } else {
                        long lo = 2 + (n * ch) / nch;
                        long hi = 2 + (n * (ch + 1)) / nch;
                        real_t x1 = ex1, x2 = ex2;
                        for (long i = lo; i < hi; i++) {
                            a[i] = orig[i] + x1 * b[i] + x2 * c[i];
                            x2 = x1;
                            x1 = a[i];
                        }
                        ex1 = x1;
                        ex2 = x2;
                    }
                }
            }
        }
        pb_mix(nl);
    }

    free(orig);
    free(P1); free(Q1); free(R1);
    free(P2); free(Q2); free(R2);
    free(Xg); free(Yg); free(E1); free(E2);
    return (real_t)0;
}

PB_MAIN(kernel_s322)
