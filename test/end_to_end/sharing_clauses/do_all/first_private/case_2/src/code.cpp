#include <stdio.h>
#include <stdlib.h>

// writes the three elements of the array it is handed
static void fill(double base, double out[]) {
  out[0] = base;
  out[1] = base + 1.0;
  out[2] = base + 2.0;
}

int main(int argc, const char *argv[]) {
  static int n = 4000;
  static double res[4000];
  double Arr[3];

  // DO-ALL firstprivate(Arr): a work array on the stack that a called function fills on every pass and the
  // loop then reads -- every thread needs the array for itself; shared(Arr) would be a race
  for (int k = 0; k < n; k++) {
    fill((double)k, Arr);
    res[k] = Arr[0] + Arr[1] + Arr[2];
  }

  double x = res[n - 1];
}
