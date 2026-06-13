/*
 * TIER-1 FAILURE CASE
 *
 * This file demonstrates DiscoPoP's false-positive Do-All detection.
 *
 * prefix_sum has a loop-carried RAW dependency:
 *   iteration i writes a[i], iteration i+1 reads a[i] as a[i-1].
 *
 * DiscoPoP reports it as Do-All (applicable=True) because the dependency-edge
 * lookup maps use source-line IDs but the profiler emits instruction IDs —
 * the mismatch means no dep edge ever blocks the Do-All detector.
 *
 * Applying the generated #pragma omp parallel for WILL PRODUCE WRONG RESULTS,
 * which the agent validation layer should catch to trigger Tier-2.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 16

/* Loop-carried RAW dependency: a[i] = a[i] + a[i-1]
 * Each iteration needs the result from the previous one.
 * Correct sequential output for input [1..16]:
 *   1 3 6 10 15 21 28 36 45 55 66 78 91 105 120 136
 */
void prefix_sum(int *a, int n) {
    for (int i = 1; i < n; i++) {
        a[i] = a[i] + a[i-1];
    }
}

int main(void) {
    int *a = (int*)malloc(N * sizeof(int));
    for (int i = 0; i < N; i++) a[i] = i + 1;

    prefix_sum(a, N);

    printf("Result: ");
    for (int i = 0; i < N; i++) printf("%d ", a[i]);
    printf("\n");
    printf("Expected: 1 3 6 10 15 21 28 36 45 55 66 78 91 105 120 136\n");

    free(a);
    return 0;
}
