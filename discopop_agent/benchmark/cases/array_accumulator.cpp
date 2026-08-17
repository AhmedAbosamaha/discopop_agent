// CAUSE 2 — accumulation hidden behind an array slot.
// The running total lives in acc[0], so the profiler reports a loop-carried
// RAW on the array rather than a reduction candidate, and DiscoPoP will not
// emit `reduction(+:...)`.  Fix: accumulate into a plain scalar (which the
// re-profile then recognises as a reduction) and store it back afterwards.
// The accumulator is integer, so any summation order gives the same total.
#include <cstdio>

static const int N = 200000;
static const int WORK = 520;

int main() {
    static double a[N], out[N];
    static long long acc[1] = {0};
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;

    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
        acc[0] += (long long)(x * 1000.0);
    }

    printf("checksum %lld\n", acc[0]);
    return 0;
}
