
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
# define HS_ROWS 64
# define HS_COLS 64
# define HS_ITERATIONS 10
#endif
#ifdef SMALL_DATASET
# define HS_ROWS 512
# define HS_COLS 512
# define HS_ITERATIONS 100
#endif
#ifdef STANDARD_DATASET
# define HS_ROWS 1024
# define HS_COLS 1024
# define HS_ITERATIONS 500
#endif
#ifdef LARGE_DATASET
# define HS_ROWS 2048
# define HS_COLS 2048
# define HS_ITERATIONS 1000
#endif
#ifdef EXTRALARGE_DATASET
# define HS_ROWS 4096
# define HS_COLS 4096
# define HS_ITERATIONS 2000
#endif
#ifndef HS_ROWS
# define HS_ROWS 1024
# define HS_COLS 1024
# define HS_ITERATIONS 500
#endif
#define BLOCK_SIZE 16
#define BLOCK_SIZE_C BLOCK_SIZE
#define BLOCK_SIZE_R BLOCK_SIZE

#define STR_SIZE	256

/* maximum power density possible (say 300W for a 10mm x 10mm chip)	*/
#define MAX_PD	(3.0e6)
/* required precision in degrees	*/
#define PRECISION	0.001
#define SPEC_HEAT_SI 1.75e6
#define K_SI 100
/* capacitance fitting factor	*/
#define FACTOR_CHIP	0.5
#define OPEN
//#define NUM_THREAD 4

typedef float FLOAT;

/* chip parameters	*/
const FLOAT t_chip = 0.0005;
const FLOAT chip_height = 0.016;
const FLOAT chip_width = 0.016;

#ifdef OMP_OFFLOAD

#endif

/* ambient temperature, assuming no package at all	*/
const FLOAT amb_temp = 80.0;

void single_iteration(FLOAT *result, FLOAT *temp, FLOAT *power, int row, int col,
					  FLOAT Cap_1, FLOAT Rx_1, FLOAT Ry_1, FLOAT Rz_1, 
					  FLOAT step)
{
    FLOAT delta;
    int r, c;
    int chunk;
    int num_chunk = row*col / (BLOCK_SIZE_R * BLOCK_SIZE_C);
    int chunks_in_row = col/BLOCK_SIZE_C;
    int chunks_in_col = row/BLOCK_SIZE_R;

#ifdef OPEN
    #ifndef __MIC__
    #endif
    
#endif
    for ( chunk = 0; chunk < num_chunk; ++chunk )
    {
        int r_start = BLOCK_SIZE_R*(chunk/chunks_in_col);
        int c_start = BLOCK_SIZE_C*(chunk%chunks_in_row); 
        int r_end = r_start + BLOCK_SIZE_R > row ? row : r_start + BLOCK_SIZE_R;
        int c_end = c_start + BLOCK_SIZE_C > col ? col : c_start + BLOCK_SIZE_C;
       
        if ( r_start == 0 || c_start == 0 || r_end == row || c_end == col )
        {
            for ( r = r_start; r < r_start + BLOCK_SIZE_R; ++r ) {
                for ( c = c_start; c < c_start + BLOCK_SIZE_C; ++c ) {
                    /* Corner 1 */
                    if ( (r == 0) && (c == 0) ) {
                        delta = (Cap_1) * (power[0] +
                            (temp[1] - temp[0]) * Rx_1 +
                            (temp[col] - temp[0]) * Ry_1 +
                            (amb_temp - temp[0]) * Rz_1);
                    }	/* Corner 2 */
                    else if ((r == 0) && (c == col-1)) {
                        delta = (Cap_1) * (power[c] +
                            (temp[c-1] - temp[c]) * Rx_1 +
                            (temp[c+col] - temp[c]) * Ry_1 +
                        (   amb_temp - temp[c]) * Rz_1);
                    }	/* Corner 3 */
                    else if ((r == row-1) && (c == col-1)) {
                        delta = (Cap_1) * (power[r*col+c] + 
                            (temp[r*col+c-1] - temp[r*col+c]) * Rx_1 + 
                            (temp[(r-1)*col+c] - temp[r*col+c]) * Ry_1 + 
                        (   amb_temp - temp[r*col+c]) * Rz_1);					
                    }	/* Corner 4	*/
                    else if ((r == row-1) && (c == 0)) {
                        delta = (Cap_1) * (power[r*col] + 
                            (temp[r*col+1] - temp[r*col]) * Rx_1 + 
                            (temp[(r-1)*col] - temp[r*col]) * Ry_1 + 
                            (amb_temp - temp[r*col]) * Rz_1);
                    }	/* Edge 1 */
                    else if (r == 0) {
                        delta = (Cap_1) * (power[c] + 
                            (temp[c+1] + temp[c-1] - 2.0*temp[c]) * Rx_1 + 
                            (temp[col+c] - temp[c]) * Ry_1 + 
                            (amb_temp - temp[c]) * Rz_1);
                    }	/* Edge 2 */
                    else if (c == col-1) {
                        delta = (Cap_1) * (power[r*col+c] + 
                            (temp[(r+1)*col+c] + temp[(r-1)*col+c] - 2.0*temp[r*col+c]) * Ry_1 + 
                            (temp[r*col+c-1] - temp[r*col+c]) * Rx_1 + 
                            (amb_temp - temp[r*col+c]) * Rz_1);
                    }	/* Edge 3 */
                    else if (r == row-1) {
                        delta = (Cap_1) * (power[r*col+c] + 
                            (temp[r*col+c+1] + temp[r*col+c-1] - 2.0*temp[r*col+c]) * Rx_1 + 
                            (temp[(r-1)*col+c] - temp[r*col+c]) * Ry_1 + 
                            (amb_temp - temp[r*col+c]) * Rz_1);
                    }	/* Edge 4 */
                    else if (c == 0) {
                        delta = (Cap_1) * (power[r*col] + 
                            (temp[(r+1)*col] + temp[(r-1)*col] - 2.0*temp[r*col]) * Ry_1 + 
                            (temp[r*col+1] - temp[r*col]) * Rx_1 + 
                            (amb_temp - temp[r*col]) * Rz_1);
                    }
                    result[r*col+c] =temp[r*col+c]+ delta;
                }
            }
            continue;
        }

        #pragma omp parallel for firstprivate(temp,Ry_1,Cap_1,col,Rz_1,r_start,c_start,Rx_1) private(c) shared(result,power) 
        for ( r = r_start; r < r_start + BLOCK_SIZE_R; ++r ) {
    
            for ( c = c_start; c < c_start + BLOCK_SIZE_C; ++c ) {
            /* Update Temperatures */
                result[r*col+c] =temp[r*col+c]+ 
                     ( Cap_1 * (power[r*col+c] + 
                    (temp[(r+1)*col+c] + temp[(r-1)*col+c] - 2.f*temp[r*col+c]) * Ry_1 + 
                    (temp[r*col+c+1] + temp[r*col+c-1] - 2.f*temp[r*col+c]) * Rx_1 + 
                    (amb_temp - temp[r*col+c]) * Rz_1));
            }
        }
    }
}
void compute_tran_temp(FLOAT *result, int num_iterations, FLOAT *temp, FLOAT *power, int row, int col) 
{
	#ifdef VERBOSE
	int i = 0;
	#endif

	FLOAT grid_height = chip_height / row;
	FLOAT grid_width = chip_width / col;

	FLOAT Cap = FACTOR_CHIP * SPEC_HEAT_SI * t_chip * grid_width * grid_height;
	FLOAT Rx = grid_width / (2.0 * K_SI * t_chip * grid_height);
	FLOAT Ry = grid_height / (2.0 * K_SI * t_chip * grid_width);
	FLOAT Rz = t_chip / (K_SI * grid_height * grid_width);

	FLOAT max_slope = MAX_PD / (FACTOR_CHIP * t_chip * SPEC_HEAT_SI);
    FLOAT step = PRECISION / max_slope / 1000.0;

    FLOAT Rx_1=1.f/Rx;
    FLOAT Ry_1=1.f/Ry;
    FLOAT Rz_1=1.f/Rz;
    FLOAT Cap_1 = step/Cap;
	#ifdef VERBOSE
	fprintf(stdout, "total iterations: %d s\tstep size: %g s\n", num_iterations, step);
	fprintf(stdout, "Rx: %g\tRy: %g\tRz: %g\tCap: %g\n", Rx, Ry, Rz, Cap);
	#endif

        {
            FLOAT* r = result;
            FLOAT* t = temp;
            for (int i = 0; i < num_iterations ; i++)
            {
                #ifdef VERBOSE
                fprintf(stdout, "iteration %d\n", i++);
                #endif
                single_iteration(r, t, power, row, col, Cap_1, Rx_1, Ry_1, Rz_1, step);
                FLOAT* tmp = t;
                t = r;
                r = tmp;
            }	
        }
	#ifdef VERBOSE
	fprintf(stdout, "iteration %d\n", i++);
	#endif
}

/* ---- hotspot, packaged -----------------------------------------------------
   Sizes come from the dataset guard; the temperature and power grids are generated here
   instead of read from files (the harness passes no arguments). -DPB_EMIT_INPUT writes the
   generated grids in the original's format so the validator can give the original exactly
   the same input. compute_tran_temp is the timed region. */
void single_iteration(FLOAT *result, FLOAT *temp, FLOAT *power, int row, int col,
                      FLOAT Cap_1, FLOAT Rx_1, FLOAT Ry_1, FLOAT Rz_1, FLOAT step);
void compute_tran_temp(FLOAT *result, int num_iterations, FLOAT *temp, FLOAT *power,
                       int row, int col);

/* Three decimals, so the file the original reads and the value held here are one float. */
static void hs_generate(FLOAT* temp, FLOAT* power, int n)
{
  for (int i = 0; i < n; i++)
    {
      temp[i]  = (FLOAT)((323000 + (int)(pb_uniform() * 2000.0)) / 1000.0);
      power[i] = (FLOAT)((int)(pb_uniform() * 300.0) / 1000.0);
    }
}

int main(int argc, char** argv)
{
  int grid_rows = HS_ROWS, grid_cols = HS_COLS, sim_time = HS_ITERATIONS;
  int n = grid_rows * grid_cols;
  FLOAT* temp = (FLOAT*)calloc(n, sizeof(FLOAT));
  FLOAT* power = (FLOAT*)calloc(n, sizeof(FLOAT));
  FLOAT* result = (FLOAT*)calloc(n, sizeof(FLOAT));
  if (!temp || !power || !result) { fprintf(stderr, "cannot allocate\n"); return 1; }

  if (argc > 1) pb_seed(argv[1]);
  hs_generate(temp, power, n);

#ifdef PB_EMIT_INPUT
  /* The original's format: one value per line, read back with %f. */
  FILE* ft = fopen("temp.in", "w");
  FILE* fp = fopen("power.in", "w");
  if (!ft || !fp) { fprintf(stderr, "cannot write the generated input\n"); return 1; }
  for (int i = 0; i < n; i++) fprintf(ft, "%.6f\n", (double)temp[i]);
  for (int i = 0; i < n; i++) fprintf(fp, "%.6f\n", (double)power[i]);
  fclose(ft);
  fclose(fp);
  return 0;
#else
  pb_timer_start();
  compute_tran_temp(result, sim_time, temp, power, grid_rows, grid_cols);
  pb_timer_stop();

  /* compute_tran_temp swaps two local pointers each iteration, so the answer ends in one
     buffer or the other depending on the parity. This is the original's own expression from
     its writeoutput call — `result` for an odd count, `temp` for an even one. Reversing it
     still agrees at 10 iterations by luck and differs in 1,241 of 262,144 cells at 100. */
  FLOAT* answer = (1 & sim_time) ? result : temp;
  for (int i = 0; i < n; i++) pb_emit((double)answer[i]);
  pb_report();

  free(temp);
  free(power);
  free(result);
  return 0;
#endif
}
