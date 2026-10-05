/* Measurement harness (hidden from the model): data, index tables, perturbed input, digest, main. */
#ifndef PB_EVK_HARNESS
#define PB_EVK_HARNESS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef double real_t;
#define LEN_1D 32000
static real_t *u, *v, *c, *d;
static int *ju, *jv, *ku, *kv;
static unsigned long long pb_state = 88172645463325252ULL;
static double pb_uniform(void) { pb_state ^= pb_state << 13; pb_state ^= pb_state >> 7; pb_state ^= pb_state << 17;
                                 return (double)(pb_state % 1000003ULL) / 1000003.0; }
static void pb_setup(int argc, char **argv) {
  u = (real_t *)malloc(sizeof(real_t) * 2 * LEN_1D); v = (real_t *)malloc(sizeof(real_t) * 2 * LEN_1D);
  c = (real_t *)malloc(sizeof(real_t) * LEN_1D); d = (real_t *)malloc(sizeof(real_t) * LEN_1D);
  ju = (int *)malloc(sizeof(int) * LEN_1D); jv = (int *)malloc(sizeof(int) * LEN_1D);
  ku = (int *)malloc(sizeof(int) * LEN_1D); kv = (int *)malloc(sizeof(int) * LEN_1D);
  for (long i = 0; i < 2L * LEN_1D; i++) {
    u[i] = (real_t)0.75 + (real_t)((i * 37L) % 1000) * (real_t)0.0005;
    v[i] = (real_t)0.75 + (real_t)((i * 53L) % 997) * (real_t)0.0005; }
  for (long i = 0; i < LEN_1D; i++) {
    c[i] = (real_t)0.75 + (real_t)((i * 71L) % 991) * (real_t)0.0005;
    d[i] = (real_t)0.75 + (real_t)((i * 89L) % 983) * (real_t)0.0005;
    ju[i] = (int)i; jv[i] = (int)i;
    kv[i] = (int)(i - 1); ku[i] = (int)(LEN_1D + i);
  }
  if (argc > 1) {                       /* the perturbed input: values change, the index tables never do */
    pb_state ^= (unsigned long long)strtoull(argv[1], NULL, 10) * 2654435761ULL;
    for (long i = 0; i < 2L * LEN_1D; i++) { u[i] *= 1.0 + 0.2 * pb_uniform(); v[i] *= 1.0 + 0.2 * pb_uniform(); }
    for (long i = 0; i < LEN_1D; i++) { c[i] *= 1.0 + 0.1 * pb_uniform(); d[i] *= 1.0 + 0.1 * pb_uniform(); }
  }
}
static void pb_finish(real_t r) {
  double su = 0, sv = 0, wu = 0, wv = 0;
  for (long i = 0; i < 2L * LEN_1D; i++) { su += u[i]; sv += v[i]; wu += u[i] * (double)(i % 13); wv += v[i] * (double)(i % 11); }
  printf("%.17g %.17g %.17g %.17g %.17g\n", (double)r, su, sv, wu, wv);
}
#define PB_MAIN(K) int main(int argc, char **argv) { pb_setup(argc, argv); real_t pb_r = K(); pb_finish(pb_r); return 0; }
#endif
