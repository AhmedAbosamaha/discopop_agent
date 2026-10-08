#include <stdio.h>
#include <stdlib.h>

static double g[40][40];
static double h[40];

int main(int argc, const char *argv[]) {
  int i, j;

  for (j = 0; j < 40; j++) {
    h[j] = j;
  }

  // DO-ALL private(j): the counter of the inner loop is declared at the top of the function
  // and was used before; its one-line header initialises, tests and increments it
  for (i = 0; i < 40; i++)
    for (j = 0; j < 40; j++)
      g[i][j] = h[j] * 2.0 + i;

  double x = g[39][39];
}
