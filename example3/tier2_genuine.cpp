/*
 * GENUINE TIER-2 CASE — no false positive involved.
 *
 * The function normalize_batch() contains a perfectly parallelizable loop.
 * But in the profiling run, main() never calls it (it calls the slow
 * element-wise path instead).
 *
 *   DiscoPoP output for normalize_batch's loop:
 *     → no BGN entry in dynamic_dependencies.txt   (never executed)
 *     → loop_iterations = -1
 *     → no entry in patterns.json
 *     → l1_planner assigns tier = 2
 *     → controller routes to Tier-2 (LLM)
 *
 * LLM restructuring:
 *   The LLM sees normalize_batch() in the source, recognises that
 *   its inner loop is a true Do-All, and rewrites main() to call it
 *   instead of the manual element-wise loop.
 *
 * After restructuring + re-profiling:
 *     → normalize_batch's loop now has loop_iterations > 0
 *     → patterns.json gets  do_all: start=1:NN  applicable=True
 *     → l1_planner: tier = 1  → accepted at Tier-1
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 60000

/* ---------------------------------------------------------------
 * This function is COMPILED but NEVER CALLED in the profiling run.
 * DiscoPoP therefore has no runtime data for the loop inside it.
 * The loop is a pure Do-All (each output element is independent),
 * but DiscoPoP cannot detect that without profiling data.
 * --------------------------------------------------------------- */
void normalize_batch(const float *input, float *output,
                     float scale, int n) {
    for (int i = 0; i < n; i++) {          /* ← tier-2 target loop */
        output[i] = input[i] * scale;
    }
}

/* ---------------------------------------------------------------
 * What main() actually does during profiling:
 * a manual element-wise version that skips normalize_batch().
 * The manual loop IS profiled and gets a Do-All pattern, but it
 * is fused with a printf that prevents vectorisation — so the LLM
 * has good reason to prefer normalize_batch instead.
 * --------------------------------------------------------------- */
int main(void) {
    float *in  = (float *)malloc(N * sizeof(float));
    float *out = (float *)calloc(N, sizeof(float));
    float scale = 0.5f;

    for (int i = 0; i < N; i++) in[i] = (float)(i + 1);

    /* Profiled path — does NOT call normalize_batch() */
    for (int i = 0; i < N; i++) {
        out[i] = in[i] * scale;            /* same work, but inline */
    }

    printf("out[0]=%.2f  out[N-1]=%.2f\n", out[0], out[N - 1]);

    free(in);
    free(out);
    return 0;
}
