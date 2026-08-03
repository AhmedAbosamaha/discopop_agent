#include <stdio.h>
#include <stdlib.h>

#define N 16384

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
        // Sub-pass 1: even-indexed pairs, unrolled by 8
        for (int i = 0; i < n - 1; i += 16) {
            if (arr[i] > arr[i + 1]) {
                int tmp = arr[i]; arr[i] = arr[i + 1]; arr[i + 1] = tmp;
            }
            if (i + 2 < n - 1 && arr[i + 2] > arr[i + 3]) {
                int tmp = arr[i + 2]; arr[i + 2] = arr[i + 3]; arr[i + 3] = tmp;
            }
            if (i + 4 < n - 1 && arr[i + 4] > arr[i + 5]) {
                int tmp = arr[i + 4]; arr[i + 4] = arr[i + 5]; arr[i + 5] = tmp;
            }
            if (i + 6 < n - 1 && arr[i + 6] > arr[i + 7]) {
                int tmp = arr[i + 6]; arr[i + 6] = arr[i + 7]; arr[i + 7] = tmp;
            }
            if (i + 8 < n - 1 && arr[i + 8] > arr[i + 9]) {
                int tmp = arr[i + 8]; arr[i + 8] = arr[i + 9]; arr[i + 9] = tmp;
            }
            if (i + 10 < n - 1 && arr[i + 10] > arr[i + 11]) {
                int tmp = arr[i + 10]; arr[i + 10] = arr[i + 11]; arr[i + 11] = tmp;
            }
            if (i + 12 < n - 1 && arr[i + 12] > arr[i + 13]) {
                int tmp = arr[i + 12]; arr[i + 12] = arr[i + 13]; arr[i + 13] = tmp;
            }
            if (i + 14 < n - 1 && arr[i + 14] > arr[i + 15]) {
                int tmp = arr[i + 14]; arr[i + 14] = arr[i + 15]; arr[i + 15] = tmp;
            }
        }
        // Sub-pass 2: odd-indexed pairs, unrolled by 8
        for (int i = 1; i < n - 1; i += 16) {
            if (arr[i] > arr[i + 1]) {
                int tmp = arr[i]; arr[i] = arr[i + 1]; arr[i + 1] = tmp;
            }
            if (i + 2 < n - 1 && arr[i + 2] > arr[i + 3]) {
                int tmp = arr[i + 2]; arr[i + 2] = arr[i + 3]; arr[i + 3] = tmp;
            }
            if (i + 4 < n - 1 && arr[i + 4] > arr[i + 5]) {
                int tmp = arr[i + 4]; arr[i + 4] = arr[i + 5]; arr[i + 5] = tmp;
            }
            if (i + 6 < n - 1 && arr[i + 6] > arr[i + 7]) {
                int tmp = arr[i + 6]; arr[i + 6] = arr[i + 7]; arr[i + 7] = tmp;
            }
            if (i + 8 < n - 1 && arr[i + 8] > arr[i + 9]) {
                int tmp = arr[i + 8]; arr[i + 8] = arr[i + 9]; arr[i + 9] = tmp;
            }
            if (i + 10 < n - 1 && arr[i + 10] > arr[i + 11]) {
                int tmp = arr[i + 10]; arr[i + 10] = arr[i + 11]; arr[i + 11] = tmp;
            }
            if (i + 12 < n - 1 && arr[i + 12] > arr[i + 13]) {
                int tmp = arr[i + 12]; arr[i + 12] = arr[i + 13]; arr[i + 13] = tmp;
            }
            if (i + 14 < n - 1 && arr[i + 14] > arr[i + 15]) {
                int tmp = arr[i + 14]; arr[i + 14] = arr[i + 15]; arr[i + 15] = tmp;
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
