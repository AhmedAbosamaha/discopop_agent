#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static double min2(double p, double q) { return p < q ? p : q; }

int main(int argc, const char *argv[]) {
  static int n = 1000;
  double *x = (double *)malloc(n * sizeof(double));
  // DOALL
  for (int i = 0; i < n; ++i) {
    x[i] = (double)((i * 37) % n) / n + 0.5;
  }
  double largest_abs = 0.0;
  // REDUCTION (max): the variable is one argument, the other is a function of the element
  for (int i = 0; i < n; ++i) {
    largest_abs = fmax(largest_abs, fabs(x[i]));
  }
  double by_helper = x[0];
  // NO PATTERN: a helper function of the variable (it computes a minimum; the profiler cannot read that)
  for (int i = 1; i < n; ++i) {
    by_helper = min2(by_helper, x[i]);
  }
  double by_hypot = 1.0;
  // NO PATTERN: another function of the variable
  for (int i = 1; i < n; ++i) {
    by_hypot = hypot(by_hypot, x[i]);
  }
  double by_abs = 0.0;
  // NO PATTERN: no reduction at all
  for (int i = 1; i < n; ++i) {
    by_abs = fabs(by_abs - x[i]);
  }
  double by_division = 1.0;
  // NO PATTERN: a division
  for (int i = 0; i < n; ++i) {
    by_division = by_division / (1.0 + x[i]);
  }
  double with_itself = 0.0;
  // NO PATTERN: a maximum with the variable in both arguments
  for (int i = 0; i < n; ++i) {
    with_itself = fmax(with_itself, with_itself + x[i]);
  }
  printf("%f %f %f %f %f %f\n", largest_abs, by_helper, by_hypot, by_abs, by_division, with_itself);
  free(x);
  return 0;
}
