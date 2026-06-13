#include <stdio.h>
#include <stdlib.h>

#define N 1024

/*
 * Odd-even transposition sort — LLM restructured from bubble sort.
 *
 * Each pass has two independent phases:
 *   Even phase: compares (0,1), (2,3), (4,5) ... no overlap → Do-All
 *   Odd  phase: compares (1,2), (3,4), (5,6) ... no overlap → Do-All
 *
 * Each inner loop is a genuine Do-All: iteration i only touches
 * arr[i] and arr[i+1], which are disjoint across iterations (step=2).
 */
void bubble_sort(int *arr, int n) {
    for (int pass = 0; pass < n; pass++) {
        int start = pass % 2;
        for (int i = start; i + 1 < n; i += 2) {
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
