/* Measurement harness (prototype v5): data, initial values, perturbed input, digest, timing.
 * Outside the package; included by the package's main.c after data.h. */
#ifndef PB_TSVC_HARNESS
#define PB_TSVC_HARNESS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define R 48

/* ---- output: digest by default, full dump with -DPB_FULL_DUMP ------------ */
#ifdef PB_FULL_DUMP
# define pb_emit(v) fprintf(stdout, "%0.17g\n", (double)(v))
# define pb_report() ((void)0)
#else
static unsigned long long pb_count = 0;
static double pb_sum = 0.0;
static double pb_wsum = 0.0;
static void pb_emit(double v)
{
  pb_count++;
  pb_sum += v;
  pb_wsum += v * (double)((pb_count % 9973) + 1);
}
static void pb_report(void)
{
  printf("pb_values %llu\n", pb_count);
  printf("pb_sum %.17g\n", pb_sum);
  printf("pb_wsum %.17g\n", pb_wsum);
}
#endif

/* ---- optional perturbed input: argv[1] = seed ---------------------------- */
static unsigned long long pb_seed(const char* s)
{
  return strtoull(s, NULL, 10) * 0x9E3779B97F4A7C15ULL + 1ULL;
}
static double pb_uniform(unsigned long long* state)
{
  *state = *state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(*state >> 11) / 9007199254740992.0;
}
#define PB_PERTURB(arr, count)                                              \
  do {                                                                      \
    double* pb_p = (double*)(arr);                                          \
    unsigned long long pb_k, pb_n = (unsigned long long)(count);            \
    for (pb_k = 0; pb_k < pb_n; pb_k++)                                     \
      pb_p[pb_k] += (double)(pb_uniform(&pb_state) * 3.0);                  \
  } while (0)

/* ---- timed region: the kernel only --------------------------------------- */
static struct timespec pb_t0;
static void pb_timer_start(void)
{
  clock_gettime(CLOCK_MONOTONIC, &pb_t0);
}
static void pb_timer_stop(void)
{
  struct timespec t1;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  fprintf(stderr, "DP_TIMED_REGION_SECONDS %.9f\n",
          (double)(t1.tv_sec - pb_t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - pb_t0.tv_nsec));
}

/* ---- data: TSVC's five vectors ------------------------------------------------ */
real_t *a, *b, *c, *d, *e;
real_t *u, *v;
int *ju, *jv, *ku, *kv;
#ifdef PB_EXPERT_TMP
static real_t *pb_tmp;   /* an expert reference's scratch vector */
#endif


static void init_array(void)
{
  for (int i = 0; i < LEN_1D; i++) {
    a[i] = (real_t)0.75 + (real_t)((i * 37L) % 1000) * (real_t)0.0005;
    b[i] = (real_t)0.75 + (real_t)((i * 53L) % 997) * (real_t)0.0005;
    c[i] = (real_t)0.75 + (real_t)((i * 71L) % 991) * (real_t)0.0005;
    d[i] = (real_t)0.75 + (real_t)((i * 89L) % 983) * (real_t)0.0005;
    e[i] = (real_t)0.75 + (real_t)((i * 97L) % 977) * (real_t)0.0005;
  }
    u = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t)); v = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t));
    ju = (int*)malloc((size_t)LEN_1D * sizeof(int)); jv = (int*)malloc((size_t)LEN_1D * sizeof(int));
    ku = (int*)malloc((size_t)LEN_1D * sizeof(int)); kv = (int*)malloc((size_t)LEN_1D * sizeof(int));
    for (long i = 0; i < 2L * LEN_1D; i++) {
      u[i] = (real_t)0.75 + (real_t)((i * 37L) % 1000) * (real_t)0.0005;
      v[i] = (real_t)0.75 + (real_t)((i * 53L) % 997) * (real_t)0.0005;
    }
    for (long i = 0; i < LEN_1D; i++) { ju[i] = (int)i; jv[i] = (int)i; kv[i] = (int)(i - 1); ku[i] = (int)(LEN_1D + i); }
}

static void pb_emit_array(const real_t* v)
{
#ifdef PB_FULL_DUMP
  for (long i = 0; i < LEN_1D; i++) pb_emit(v[i]);
#else
  /* both ends and the middle in full, the rest sampled */
  long step = LEN_1D / 2000 > 0 ? LEN_1D / 2000 : 1;
  for (long i = 0; i < 32 && i < LEN_1D; i++) pb_emit(v[i]);
  for (long i = LEN_1D / 2 - 16; i < LEN_1D / 2 + 16; i++) if (i >= 32 && i < LEN_1D) pb_emit(v[i]);
  for (long i = LEN_1D - 32; i < LEN_1D; i++) if (i >= LEN_1D / 2 + 16) pb_emit(v[i]);
  for (long i = 32; i < LEN_1D - 32; i += step) pb_emit(v[i]);
#endif
}

/* ---- main, in the order v3's main ran it ------------------------------------------ */
static int pb_setup(int argc, char** argv)
{
  a = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  b = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  c = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  d = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  e = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
#ifdef PB_EXPERT_TMP
  pb_tmp = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
#endif
  if (!a || !b || !c || !d || !e) { fprintf(stderr, "out of memory\n"); return 1; }
  init_array();
  /* Optional perturbed input, see PB_PERTURB: magnitudes and signs of the data are kept. */
  if (argc > 1) {
    unsigned long long pb_state = pb_seed(argv[1]);
    for (long pb_i = 0; pb_i < LEN_1D; pb_i++) {
      a[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      b[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      c[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      d[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      e[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
    }
  }
  return 0;
}

static void pb_finish(real_t result)
{
  pb_emit(result);
  pb_emit_array(a); pb_emit_array(b); pb_emit_array(c); pb_emit_array(d); pb_emit_array(e);
  pb_emit_array(u); pb_emit_array(u + LEN_1D); pb_emit_array(v); pb_emit_array(v + LEN_1D);
  pb_report();
  free(a); free(b); free(c); free(d); free(e);
}


#endif
