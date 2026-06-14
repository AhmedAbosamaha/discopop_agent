#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N     256
#define STEPS 50

/*
 * 1D Jacobi smoother -- in-place version creates a RAW chain.
 *
 * Iteration i   writes u[i].
 * Iteration i+1 reads  u[i] (as u[(i+1)-1]).
 *
 * This is actually Gauss-Seidel (uses already-updated neighbours).
 * True Jacobi requires reading from a frozen snapshot of u[]:
 *   allocate tmp[], read from u[], write to tmp[], then copy back.
 * After double-buffering, the inner loop is Do-All:
 *   every iteration reads from the frozen u[] and writes to a
 *   disjoint tmp[i] slot -- no cross-iteration dependency.
 *
 * DiscoPoP detects the RAW chain and finds no applicable pattern.
 * The agent therefore escalates directly to Tier-2 (LLM restructuring).
 */
void smooth(float *u, int n, int steps) {
    for (int step = 0; step < steps; step++) {
        float *tmp = new float[n];
        for (int i = 1; i < n - 1; i++) {
            tmp[i] = 0.5f * (u[i - 1] + u[i + 1]);
        }
        for (int i = 1; i < n - 1; i++) {
            u[i] = tmp[i];
        }
        delete[] tmp;
    }
}

int main(void) {
    float *u = (float *)malloc(N * sizeof(float));

    /* Step-function initial condition; boundaries pinned at 0 and 1 */
    u[0] = 0.0f;
    u[N - 1] = 1.0f;
    for (int i = 1; i < N - 1; i++) u[i] = (i < N / 2) ? 0.0f : 1.0f;

    smooth(u, N, STEPS);

    /* After smoothing: values must stay in [0, 1] and boundaries unchanged */
    int ok = 1;
    if (u[0] != 0.0f || u[N - 1] != 1.0f) ok = 0;
    for (int i = 0; i < N; i++)
        if (u[i] < -0.01f || u[i] > 1.01f) { ok = 0; }

    printf("u[0]=%.4f  u[N/4]=%.4f  u[N/2]=%.4f  u[N-1]=%.4f\n",
           u[0], u[N / 4], u[N / 2], u[N - 1]);
    printf("Values in [0,1]: %s\n", ok ? "YES" : "NO");

    free(u);
    return 0;
}
