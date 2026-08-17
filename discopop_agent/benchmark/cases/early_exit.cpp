// CAUSE 5 — non-canonical control flow.
// The `break` makes the trip count unknown before the loop starts, so OpenMP
// cannot parallelize it (and -fopenmp refuses to compile the pragma).  The
// guard never fires for this input, but a correct rewrite may not assume that:
// find the first offending index first, then run a canonical loop up to it.
#include <cstdio>

static const int N = 200000;
static const int WORK = 520;

int main() {
    static double a[N], out[N];
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;

    for (int i = 0; i < N; i++) {
        if (a[i] < 0.0) break;
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
    }

    long long chk = 0;
    for (int i = 0; i < N; i++) chk += (long long)(out[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
