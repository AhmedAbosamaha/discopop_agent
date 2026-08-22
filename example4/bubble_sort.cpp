#include <stdio.h>
#include <stdlib.h>

#define N 513

void bubble_sort(int *arr, int n) {
    /* Odd-even sort: parallelizes by doing non-overlapping comparisons in each phase.
       Odd phases compare pairs (0,1), (2,3), (4,5), ...; even phases compare (1,2), (3,4), ...
       Iterations within each phase are independent and run in parallel.
       arr: shared (all threads read/write); i: induction variable (auto private);
       tmp: declared inside loop (auto private). */
    for (int phase = 0; phase < n; phase++) {
        if (phase % 2 == 0) {
            /* Odd phase: compare elements at even indices with their right neighbors */
            #pragma omp parallel for shared(arr)
            for (int i = 0; i < n - 1; i += 2) {
                if (arr[i] > arr[i + 1]) {
                    int tmp   = arr[i];
                    arr[i]    = arr[i + 1];
                    arr[i + 1] = tmp;
                }
            }
        } else {
            /* Even phase: compare elements at odd indices with their right neighbors */
            #pragma omp parallel for shared(arr)
            for (int i = 1; i < n - 1; i += 2) {
                if (arr[i] > arr[i + 1]) {
                    int tmp   = arr[i];
                    arr[i]    = arr[i + 1];
                    arr[i + 1] = tmp;
                }
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
