#include <math.h>
#include <stdio.h>
#define N 200000
double a[N];
double b[N];

static double min2(double p, double q) {
    return p < q ? p : q;
}
double f_max_call(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = fmax(x, a[i]);
    }
    return x;
}
double f_min_call(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = fmin(x, a[i]);
    }
    return x;
}
double f_max_of_abs(void) {
    double x = 0.0;
    for (int i = 0; i < N; i++) {
        x = fmax(x, fabs(a[i]));
    }
    return x;
}
float f_max_converted(void) {
    float x = (float)a[0];
    for (int i = 1; i < N; i++) {
        x = fmax(x, a[i]);
    }
    return x;
}
double f_max_nested(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = fmax(fmax(x, a[i]), b[i]);
    }
    return x;
}
double f_clamp(void) {
    double x = 0.0;
    for (int i = 0; i < N; i++) {
        x = fmin(fmax(x, a[i]), 0.25);
    }
    return x;
}
double f_max_with_itself(void) {
    double x = 0.0;
    for (int i = 0; i < N; i++) {
        x = fmax(x, x + a[i]);
    }
    return x;
}
double f_helper_function(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = min2(x, a[i]);
    }
    return x;
}
double f_other_function(void) {
    double x = 1.0;
    for (int i = 1; i < N; i++) {
        x = hypot(x, a[i]);
    }
    return x;
}
double f_abs_of_difference(void) {
    double x = 0.0;
    for (int i = 1; i < N; i++) {
        x = fabs(x - a[i]);
    }
    return x;
}
double f_division(void) {
    double x = 1.0;
    for (int i = 0; i < N; i++) {
        x = x / (2.0 + b[i]);
    }
    return x;
}
double f_copy_of_first(void) {
    for (int i = 0; i < N; i++) {
        b[i] = b[0];
    }
    return b[N - 1];
}
int main(void) {
    for (int i = 0; i < N; i++) {
        a[i] = (double)((i * 7919 + 13) % N) / N - 0.5;
        b[i] = (double)((i * 104729 + 7) % N) / N - 0.5;
    }
    double r = f_max_call() + f_min_call() + f_max_of_abs() + f_max_converted() + f_max_nested() + f_clamp()
             + f_max_with_itself() + f_helper_function() + f_other_function() + f_abs_of_difference()
             + f_division() + f_copy_of_first();
    printf("%.6f\n", r);
    return 0;
}
