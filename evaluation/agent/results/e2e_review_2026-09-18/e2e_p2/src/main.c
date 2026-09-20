#include <stdio.h>
#include "kern.h"
int main(void) {
  int i;
  for (i = 0; i < R; i++) { a[i][0] = 1.0 + (i % 17) * 0.25; b[i] = 0.0; }
  kernel(R);
  smooth(R);
  double s = 0.0;
  for (i = 0; i < R; i++) s += b[i];
  printf("%.10f\n", s);
  return 0;
}
