// CAUSE 3b — in-place coupling, same-sweep read-back = YES.
// A swap performed at index j is compared again at j+1 within the SAME sweep,
// so the update cascades and double-buffering is INVALID; the sweep must be
// split into disjoint sub-passes (odd-even transposition), with bounds
// re-derived for the new schedule.  The sorted array is unique, so a correct
// partitioned schedule still reproduces the output exactly.
//
// NOTE: sorting is memory-bound, so the profiled run limits N and the timed
// run is too short to measure a 1.1x speedup reliably — this case runs with
// --no-require-speedup (see manifest.json).
#include <cstdio>

static const int N = 2000;

int main() {
    static int arr[N];
    unsigned s = 12345u;
    for (int i = 0; i < N; i++) { s = s * 1103515245u + 12345u; arr[i] = (int)(s >> 16); }

    for (int pass = 0; pass < N - 1; pass++) {
        for (int j = 0; j < N - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }

    long long chk = 0;
    for (int i = 0; i < N; i++) chk += (long long)arr[i] * (i + 1);
    printf("checksum %lld\n", chk);
    return 0;
}
