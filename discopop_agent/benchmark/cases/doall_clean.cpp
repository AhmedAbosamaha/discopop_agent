// BASELINE — the loop is already a clean Do-All.
// Cause: none.  Expected path: DiscoPoP detects do_all, Tier-1 validates it,
// the LLM is never called.  Guards against the agent "fixing" working code.
#include <cstdio>

static const int N = 200000;
static const int WORK = 520;

int main() {
    static double a[N], out[N];
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;

    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
    }

    long long chk = 0;
    for (int i = 0; i < N; i++) chk += (long long)(out[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
