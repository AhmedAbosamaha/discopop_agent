#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
  static int n = 5000;
  double Arr[5000];

  // DO-ALL shared(Arr): an array on the stack, filled by the loop and read after it
  for (int i = 0; i < n; i++) {
    Arr[i] = i;
  }

  double x = Arr[n - 1];
}
