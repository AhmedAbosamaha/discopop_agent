#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
  static int n = 100;
  double *x = (double *)malloc(n * sizeof(double));
  double *y = (double *)malloc(n * sizeof(double));

  for (int j = 0; j < n; j++) {
    x[j] = 1.0;
    y[j] = 0.5;
  }

  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < n; j++) {
      x[j] = i + j;
    }
    for (int j = 0; j < n; j++) {
      y[j] = y[j] + x[j];
    }
  }

  printf("%f\n", y[n - 1]);
  free(x);
  free(y);
  return 0;
}
