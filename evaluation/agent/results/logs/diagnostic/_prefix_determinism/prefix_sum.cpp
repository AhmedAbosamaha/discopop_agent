// CAUSE 4 — true recurrence (running total), mixed with independent work.
// out[i] depends on out[i-1], so the loop cannot become a Do-All as written.
// The per-element work that feeds the total is independent, though: split the
// loop (fission) into a parallel phase that computes each element's
// contribution and a scan that combines them.  The accumulator is integer, so
// a blocked / prefix-scan formulation reproduces the totals exactly.
#include <cstdio>

static const int N = 200000;
static const int WORK = 520;

int main() {
    static double a[N];
    static long long out[N];
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;

    long long running = 0;
    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        running += (long long)(x * 1000.0);
        out[i] = running;
    }

    long long chk = 0;
    for (int i = 0; i < N; i++) chk ^= out[i] * (i + 1);
    printf("checksum %lld\n", chk);
    return 0;
}
