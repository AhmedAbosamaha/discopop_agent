// CAUSE 3a — in-place coupling, same-sweep read-back = NO.
// Each iteration writes a[i] after reading a[i] and a[i+1]; a[i+1] is still
// the previous sweep's value when it is read, so every input is an OLD value.
// A sweep is therefore a pure map old -> new and DOUBLE-BUFFERING is valid
// (write into a second array, swap after the sweep) — partitioning is not
// needed.  Results are bit-identical because each element's arithmetic is
// unchanged; only the storage differs.
#include <cstdio>

static const int N = 40000;
static const int SWEEPS = 6;
static const int WORK = 400;

int main() {
    static double a[N];
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;

    for (int s = 0; s < SWEEPS; s++) {
        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            a[i] = x;
        }
    }

    long long chk = 0;
    for (int i = 0; i < N; i++) chk += (long long)(a[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
