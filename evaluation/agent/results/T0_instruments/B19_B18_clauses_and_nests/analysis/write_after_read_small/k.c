#include <stdio.h>
#define N 2000
static double x[N + 1], y[N + 1];
int main(void) {
    for (int i = 0; i <= N; i++) {
        x[i] = i * 0.5;
        y[i] = i * 0.25;
    }
    for (int i = 0; i < N; i++)
        x[i] = x[i + 1] * 0.5;
    for (int i = 1; i <= N; i++)
        y[i] = y[i - 1] * 0.5;
    double s = 0.0;
    for (int i = 0; i <= N; i++)
        s += x[i] + y[i];
    printf("%f\n", s);
    return 0;
}
