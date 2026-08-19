#include <stdio.h>
#include <stdlib.h>

#define N 4

/*
 * Bubble sort — inner loop has a cross-iteration swap dependency.
 *
 * Iteration i  writes arr[i] and arr[i+1].
 * Iteration i+1 reads  arr[i+1] (just written by iteration i).
 *
 * This is a RAW dependency: the inner loop is NOT safe to parallelize.
 * DiscoPoP will incorrectly label it as Do-All (applicable=True).
 * Applying the pragma causes races on arr[i+1] at thread-chunk boundaries.
 * TSan catches it → Tier-1 validation FAILS → agent escalates to Tier-2.
 *
 * LLM restructures to odd-even transposition sort:
 *   Even phase: independent pairs (0,1), (2,3), (4,5) ... → Do-All
 *   Odd  phase: independent pairs (1,2), (3,4), (5,6) ... → Do-All
 */
void bubble_sort(int *arr, int n) {
    for (int pass = 0; pass < n - 1; pass++) {
        for (int i = 0; i < n - pass - 1; i++) {
            if (arr[i] > arr[i + 1]) {
                int tmp   = arr[i];
                arr[i]    = arr[i + 1];
                arr[i + 1] = tmp;
            }
        }
    }
}

int main(void) {
    int *arr = (int *)malloc(N * sizeof(int));
    for (int i = 0; i < N; i++) arr[i] = N - i;   /* reverse order: worst case */

    bubble_sort(arr, N);

    int ok = 1;
    for (int i = 0; i < N - 1; i++)
        if (arr[i] > arr[i + 1]) { ok = 0; break; }

    printf("N=%d  sorted: %s\n", N, ok ? "YES" : "NO");
    printf("arr[0]=%d  arr[N-1]=%d\n", arr[0], arr[N - 1]);

    free(arr);
    return 0;
}
