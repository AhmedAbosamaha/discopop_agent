#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Hillis-Steele parallel prefix scan.
// Outer loop (stride d) is sequential; inner loop is Do-All:
//   each iteration reads only from the frozen prev[] buffer
//   and writes to an independent cur[i] slot.
void compute_prefix_sum(int *arr, int *result, int n) {
    int *buf  = (int *)malloc(n * sizeof(int));
    int *cur  = result;
    int *prev = buf;
    for (int i = 0; i < n; i++) cur[i] = arr[i];
    for (int d = 1; d < n; d *= 2) {
        int *tmp = cur; cur = prev; prev = tmp;
        for (int i = 0; i < n; i++)
            cur[i] = (i >= d) ? prev[i] + prev[i - d] : prev[i];
    }
    if (cur != result) memcpy(result, cur, n * sizeof(int));
    free(buf);
}

int main(void) {
    int arr[]    = {3, 1, 4, 1, 5, 9, 2, 6};
    int n        = 8;
    int result[8];

    compute_prefix_sum(arr, result, n);

    for (int i = 0; i < n; i++)
        printf("%d ", result[i]);  // → 3 4 8 9 14 23 25 31
    printf("\n");
}
