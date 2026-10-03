/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"

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

static real_t kernel_s322(void)
{
    /* Dependence analysis for the i-loop (the loop under study):
     *   a[i] = a[i] + a[i-1]*b[i] + a[i-2]*c[i]
     * a[i-1] and a[i-2] are VALUES produced by the immediately preceding
     * iterations of this same loop (flow/true dependences with distance
     * 1 and 2, not a reused-but-independent location), so every
     * iteration needs the exact floating-point result its two
     * predecessors just wrote. That chain has no slack to redistribute:
     * splitting the range into chunks only moves the same dependence to
     * the chunk boundary (chunk k+1's first element still needs chunk
     * k's last two results before it can do anything), so chunks cannot
     * run concurrently without either (a) reordering the additions and
     * multiplications - which changes the rounding of every element and
     * would make the result diverge from the sequential reference, and
     * diverge differently under static/dynamic/guided schedules, since
     * the chunking itself would change the arithmetic - or (b) serializing
     * the chunks end to end, which reproduces the original order but
     * removes any possibility of overlap. Neither satisfies the
     * requirement to reproduce the sequential output exactly while also
     * running measurably faster, so this loop is left sequential: no
     * `#pragma omp` is attached to it. (The outer nl loop is excluded by
     * construction: pb_mix() below mutates a[], b[], c[] in a way that
     * the next repetition's i-loop reads, so repetitions must also run
     * in program order.)
     */
    for (int nl = 0; nl < R; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s322)
