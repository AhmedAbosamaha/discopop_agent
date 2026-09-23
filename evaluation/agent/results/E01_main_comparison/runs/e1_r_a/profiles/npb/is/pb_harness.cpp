#include "pb_harness.hpp"

/* ---- output: digest by default, exact values with -DPB_FULL_DUMP --------- */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#ifdef PB_FULL_DUMP
/* PB_DUMP_FORMAT is the recipe's, because the dump is compared against the ORIGINAL's own
   printing. %.17g by default: md's energies span 1e+03 to 1e-11, and fixed decimals would
   print half the table as 0.000000. Where the original prints with %g (hotspot's
   writeoutput), the dump must use %g too — rounding an already-rounded value in the
   comparison cannot recover the digit the original never printed, and 0.47 % of hotspot's
   values at SMALL sit exactly on that boundary. */
#ifndef PB_DUMP_FORMAT
# define PB_DUMP_FORMAT "%.17g\n"
#endif
void pb_emit(double v) { fprintf(stdout, PB_DUMP_FORMAT, v); }
void pb_report(void) { }
#else
static unsigned long long pb_count = 0;
static double pb_sum = 0.0;
static double pb_wsum = 0.0;
void pb_emit(double v)
{
  pb_count++;
  pb_sum += v;
  pb_wsum += v * (double)((pb_count % 9973) + 1);
}
void pb_report(void)
{
  printf("pb_values %llu\n", pb_count);
  printf("pb_sum %.17g\n", pb_sum);
  printf("pb_wsum %.17g\n", pb_wsum);
}
#endif

/* ---- optional perturbed input: argv[1] = seed ------------------------------
   A shipped input can be one the kernel leaves unchanged, and an output check on such an
   input cannot tell a changed algorithm from the original (seidel-2d, §2). With a seed the
   generated input moves deterministically, so the rewrite is also checked on an input the
   profile was never taken on. */
static unsigned long long pb_state = 88172645463325252ULL;
void pb_seed(const char* s)
{
  pb_state = strtoull(s, NULL, 10) * 0x9E3779B97F4A7C15ULL + 1ULL;
}
double pb_uniform(void)
{
  pb_state = pb_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(pb_state >> 11) / 9007199254740992.0;
}

/* ---- timed region: the computation only -------------------------------------
   Allocation, input generation and output stay outside it, so the ratio the gate and the
   harness compute belongs to the computation. Elapsed time goes to stderr as
   "DP_TIMED_REGION_SECONDS <s>"; stdout stays deterministic. */
static struct timespec pb_t0;
void pb_timer_start(void) { clock_gettime(CLOCK_MONOTONIC, &pb_t0); }
void pb_timer_stop(void)
{
  struct timespec t1;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  fprintf(stderr, "DP_TIMED_REGION_SECONDS %.9f\n",
          (double)(t1.tv_sec - pb_t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - pb_t0.tv_nsec));
}
