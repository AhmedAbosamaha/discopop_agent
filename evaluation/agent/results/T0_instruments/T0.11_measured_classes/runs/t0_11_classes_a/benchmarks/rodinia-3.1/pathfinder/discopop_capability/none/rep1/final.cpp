
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
static void pb_emit(double v) { fprintf(stdout, PB_DUMP_FORMAT, v); }
static void pb_report(void) { }
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

/* ---- optional perturbed input: argv[1] = seed ------------------------------
   A shipped input can be one the kernel leaves unchanged, and an output check on such an
   input cannot tell a changed algorithm from the original (seidel-2d, §2). With a seed the
   generated input moves deterministically, so the rewrite is also checked on an input the
   profile was never taken on. */
static unsigned long long pb_state = 88172645463325252ULL;
static void pb_seed(const char* s)
{
  pb_state = strtoull(s, NULL, 10) * 0x9E3779B97F4A7C15ULL + 1ULL;
}
static double pb_uniform(void)
{
  pb_state = pb_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(pb_state >> 11) / 9007199254740992.0;
}

/* ---- timed region: the computation only -------------------------------------
   Allocation, input generation and output stay outside it, so the ratio the gate and the
   harness compute belongs to the computation. Elapsed time goes to stderr as
   "DP_TIMED_REGION_SECONDS <s>"; stdout stays deterministic. */
static struct timespec pb_t0;
static void pb_timer_start(void) { clock_gettime(CLOCK_MONOTONIC, &pb_t0); }
static void pb_timer_stop(void)
{
  struct timespec t1;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  fprintf(stderr, "DP_TIMED_REGION_SECONDS %.9f\n",
          (double)(t1.tv_sec - pb_t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - pb_t0.tv_nsec));
}

/* ---- problem size: compile-time, the harness passes no arguments ------- */
#ifdef MINI_DATASET
# define PF_COLS 1000
# define PF_ROWS 10
# define PF_SEED 9
#endif
#ifdef SMALL_DATASET
# define PF_COLS 10000
# define PF_ROWS 50
# define PF_SEED 9
#endif
#ifdef STANDARD_DATASET
# define PF_COLS 100000
# define PF_ROWS 100
# define PF_SEED 9
#endif
#ifdef LARGE_DATASET
# define PF_COLS 200000
# define PF_ROWS 500
# define PF_SEED 9
#endif
#ifdef EXTRALARGE_DATASET
# define PF_COLS 400000
# define PF_ROWS 1000
# define PF_SEED 9
#endif
#ifndef PF_COLS
# define PF_COLS 100000
# define PF_ROWS 100
# define PF_SEED 9
#endif

/* ---- pathfinder, packaged --------------------------------------------------
   The original took its size from argv, filled the grid with rand() under a fixed seed,
   timed itself with rdtsc (x86-only inline assembly) and printed the whole grid. Here the
   size is a define, the grid is filled by the packaging's own generator so a seed can
   perturb it, the row loop is the timed region, and the values become digest output.
   The row update itself is copied unchanged. */
#define MIN(a, b) ((a)<=(b) ? (a) : (b))

static int rows, cols;
static int* data_;
static int** wall;
static int* result;

static void pf_init(int argc, char** argv)
{
  rows = PF_ROWS;
  cols = PF_COLS;
  data_ = new int[rows*cols];
  wall = new int*[rows];
  for (int n = 0; n < rows; n++) wall[n] = data_ + cols*n;
  result = new int[cols];
  /* Unperturbed, this is the original's own generation (srand(M_SEED), rand()%10), so the
     packaged dump can be compared value for value against the original program. A seed
     switches to the packaging's generator, which is what perturbs the input. */
  if (argc > 1)
    {
      pb_seed(argv[1]);
      for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
          wall[i][j] = (int)(pb_uniform() * 10.0);
    }
  else
    {
      srand(PF_SEED);
      for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
          wall[i][j] = rand() % 10;
    }
  for (int j = 0; j < cols; j++) result[j] = wall[0][j];
}

int main(int argc, char** argv)
{
  pf_init(argc, argv);

  int *src, *dst, *temp;
  int min;

  dst = result;
  src = new int[cols];

  pb_timer_start();
  for (int t = 0; t < rows-1; t++) {
      temp = src;
      src = dst;
      dst = temp;
      #pragma omp parallel for firstprivate(t,src) private(min) shared(dst) 
      for(int n = 0; n < cols; n++){
        min = src[n];
        if (n > 0)
          min = MIN(min, src[n-1]);
        if (n < cols-1)
          min = MIN(min, src[n+1]);
        dst[n] = wall[t+1][n]+min;
      }
  }
  pb_timer_stop();

  /* The original's print order exactly: the whole wall (from init), then `data` — its
     first row, printed a second time — then the result row `dst`. */
  for (int i = 0; i < rows; i++)
    for (int j = 0; j < cols; j++)
      pb_emit((double)wall[i][j]);
  for (int i = 0; i < cols; i++) pb_emit((double)data_[i]);
  for (int i = 0; i < cols; i++) pb_emit((double)dst[i]);
  pb_report();

  delete [] data_;
  delete [] wall;
  delete [] dst;
  delete [] src;
  return 0;
}
