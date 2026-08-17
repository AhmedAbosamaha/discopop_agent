// CAUSE 6 — granularity, not correctness.
// The inner loop IS a Do-All, but it runs 64 cheap iterations per activation:
// parallelizing it directly costs more in thread startup than it saves, so the
// pragma is correct yet not faster.  This is the case that must reach the
// "correct but no speedup" feedback path.  The fix is to raise granularity —
// e.g. collapse/flatten the two loops so one parallel region covers all the
// work instead of one per outer step.
#include <cstdio>

// Sized so the inner loop is DECISIVELY too small to parallelize: one parallel
// region covers M*WORK = 4160 flops (~1-2 us), well under thread-spawn cost.
// Total work is unchanged from the obvious sizing (N*M*WORK is constant) — it
// is only redistributed into 8x more, 8x smaller parallel regions.  An earlier
// sizing put a region at ~33k flops, which measured 0.89x on one run and 1.10x
// on the next and so flipped the case between Tier-1 and Tier-2 at random.
static const int N = 24000;
static const int M = 64;
static const int WORK = 65;

int main() {
    static double a[N * M], out[N * M];
    for (int i = 0; i < N * M; i++) a[i] = 1.0 + (i % 97) * 0.01;

    for (int s = 0; s < N; s++) {
        for (int j = 0; j < M; j++) {
            double x = a[s * M + j];
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            out[s * M + j] = x;
        }
    }

    long long chk = 0;
    for (int i = 0; i < N * M; i++) chk += (long long)(out[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
