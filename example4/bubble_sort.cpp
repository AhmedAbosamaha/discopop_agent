#include <stdio.h>
#include <stdlib.h>

#define N 513

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
