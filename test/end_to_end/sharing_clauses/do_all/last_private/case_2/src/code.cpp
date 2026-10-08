#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
  static int n = 12;
  static double a[12] = {1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0};
  int z = -1;

  // NOT DO-ALL: z is assigned in some iterations only and read after the loop.
  // lastprivate(z) would hand back the value of the last chunk, not of the last assignment.
  for (int i = 0; i < n; i++) {
    if (a[i] < 0.0) {
      z = i;
    }
  }

  int x = z;
}
