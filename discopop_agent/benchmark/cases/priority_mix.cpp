// PRIORITIZATION — a cold loop with a huge instruction count, and a hot loop
// with a small one.  The static workload proxy ranks the cold loop first
// because it executes more instructions; measured runtime ranks the hot loop
// first because that is where the time actually goes.
//
// COLD: 4,000,000 trivial integer stores, a few ms.
// HOT:  2,000 iterations of a long floating-point chain, most of the runtime.
#include <cstdio>

static const int COLD_N = 4000000;
static const int HOT_N = 2000;
static const int HOT_WORK = 20000;

int main() {
    static int cold[COLD_N];
    static double hot[HOT_N];

    for (int i = 0; i < COLD_N; i++) cold[i] = i & 1023;

    for (int i = 0; i < HOT_N; i++) {
        double x = 1.0 + (i % 97) * 0.01;
        for (int k = 0; k < HOT_WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        hot[i] = x;
    }

    long long chk = 0;
    for (int i = 0; i < COLD_N; i += 4096) chk += cold[i];
    for (int i = 0; i < HOT_N; i++) chk += (long long)(hot[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
