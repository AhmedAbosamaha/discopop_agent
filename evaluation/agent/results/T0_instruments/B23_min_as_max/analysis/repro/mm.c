#include <math.h>
#include <stdio.h>
#define N 200000
double a[N];
int ia[N];

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
float f_minf_call(void) {
    float x = (float)a[0];
    for (int i = 1; i < N; i++) {
        x = fminf(x, (float)a[i]);
    }
    return x;
}
double f_min_call_swapped(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = fmin(a[i], x);
    }
    return x;
}
double f_max_sel(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        double v = a[i];
        x = (v > x) ? v : x;
    }
    return x;
}
double f_min_sel(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        double v = a[i];
        x = (v < x) ? v : x;
    }
    return x;
}
double f_min_sel_flipped(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        double v = a[i];
        x = (x > v) ? v : x;
    }
    return x;
}
int f_imin_sel(void) {
    int x = ia[0];
    for (int i = 1; i < N; i++) {
        int v = ia[i];
        x = (v < x) ? v : x;
    }
    return x;
}
double f_max_if(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        if (a[i] > x) {
            x = a[i];
        }
    }
    return x;
}
double f_min_if(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        if (a[i] < x) {
            x = a[i];
        }
    }
    return x;
}
double f_max_ternary_array(void) {
    double x = a[0];
    for (int i = 1; i < N; i++) {
        x = (a[i] > x) ? a[i] : x;
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
int main(void) {
    for (int i = 0; i < N; i++) {
        a[i] = (double)((i * 7919 + 13) % N) / N - 0.5;
        ia[i] = (i * 7919 + 13) % N;
    }
    double r = f_max_call() + f_min_call() + f_minf_call() + f_min_call_swapped() + f_max_sel() + f_min_sel()
             + f_min_sel_flipped() + f_imin_sel() + f_max_if() + f_min_if() + f_max_ternary_array()
             + f_other_function() + f_abs_of_difference();
    printf("%.6f\n", r);
    return 0;
}
