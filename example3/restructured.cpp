/*
 * TIER-2 RESTRUCTURED VERSION (LLM output)
 *
 * The LLM recognized that prefix_sum has a loop-carried dependency
 * and restructured it using the Hillis-Steele parallel prefix scan algorithm.
 *
 * Key insight:
 *   Instead of accumulating in-place (sequential), we use two ping-pong
 *   buffers so that within each "level" d, every iteration reads only
 *   from the previous level's buffer (prev[]) and writes to the current
 *   level's buffer (cur[]).  No cross-iteration dependency exists within
 *   a single level → the inner loop is genuinely Do-All.
 *
 * DiscoPoP will correctly report the inner loop as Do-All (applicable=True).
 * Applying #pragma omp parallel for to it produces CORRECT results.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 16

/*
 * Hillis-Steele parallel prefix scan.
 *
 * For each doubling stride d, the inner loop is a true Do-All:
 *   - Reads from prev[] which is read-only for the entire level
 *   - Writes to independent positions cur[i]
 *   - No iteration i depends on any other iteration i' at the same level
 *
 * Complexity: O(n log n) work, O(log n) depth.
 */
void prefix_sum_parallel(const int *a, int *out, int n) {
    int *buf  = (int*)malloc(n * sizeof(int));
    int *cur  = out;
    int *prev = buf;

    /* Init pass — genuine Do-All: each output element is independent */
    for (int i = 0; i < n; i++) {
        cur[i] = a[i];
    }

    /* Scan: O(log n) sequential levels, each level is a Do-All inner loop */
    for (int d = 1; d < n; d *= 2) {
        /* Swap ping-pong buffers so prev[] is frozen for this level */
        int *tmp = cur; cur = prev; prev = tmp;

        /*
         * INNER LOOP — Do-All (DiscoPoP detects this correctly):
         *   - prev[i] and prev[i-d] are from the frozen previous-level buffer
         *   - cur[i] is written to a unique position per iteration
         *   - No iteration reads a value written by another iteration at this level
         */
        for (int i = 0; i < n; i++) {
            cur[i] = (i >= d) ? prev[i] + prev[i - d] : prev[i];
        }
    }

    if (cur != out) {
        memcpy(out, cur, n * sizeof(int));
    }
    free(buf);
}

int main(void) {
    int a[N];
    int out[N];
    for (int i = 0; i < N; i++) a[i] = i + 1;

    prefix_sum_parallel(a, out, N);

    printf("Result: ");
    for (int i = 0; i < N; i++) printf("%d ", out[i]);
    printf("\n");
    printf("Expected: 1 3 6 10 15 21 28 36 45 55 66 78 91 105 120 136\n");

    return 0;
}
