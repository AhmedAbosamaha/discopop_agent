#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
  static int n = 1000;
  double *x = (double *)malloc(n * sizeof(double));
  // DOALL
  for (int i = 0; i < n; ++i) {
    x[i] = (double)((i * 37) % n);
  }
  double largest = x[0];
  // REDUCTION (max)
  for (int i = 1; i < n; ++i) {
    largest = fmax(largest, x[i]);
  }
  double smallest = x[0];
  // REDUCTION (min)
  for (int i = 1; i < n; ++i) {
    smallest = fmin(smallest, x[i]);
  }
  float smallest_f = (float)x[0];
  // REDUCTION (min), the variable as the second argument and single precision
  for (int i = 1; i < n; ++i) {
    smallest_f = fminf((float)x[i], smallest_f);
  }
  printf("%f %f %f\n", largest, smallest, smallest_f);
  free(x);
  return 0;
}
