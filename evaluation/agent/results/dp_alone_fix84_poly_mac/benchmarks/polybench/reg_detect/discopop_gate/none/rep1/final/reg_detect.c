/**
 * reg_detect.c: This file is part of the PolyBench/C 3.2 test suite.
 *
 *
 * Contact: Louis-Noel Pouchet <pouchet@cse.ohio-state.edu>
 * Web address: http://polybench.sourceforge.net
 */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include "pb_harness.h"
#include <polybench.h>

/* Include benchmark-specific header. */
/* Default data type is int, default size is 50. */
#include "reg_detect.h"


/* Array initialization. */
static
void init_array(int maxgrid,
		DATA_TYPE POLYBENCH_2D(sum_tang,MAXGRID,MAXGRID,maxgrid,maxgrid),
		DATA_TYPE POLYBENCH_2D(mean,MAXGRID,MAXGRID,maxgrid,maxgrid),
		DATA_TYPE POLYBENCH_2D(path,MAXGRID,MAXGRID,maxgrid,maxgrid))
{
  int i, j;

  for (i = 0; i < maxgrid; i++)
    for (j = 0; j < maxgrid; j++) {
      sum_tang[i][j] = (DATA_TYPE)((i+1)*(j+1));
      mean[i][j] = ((DATA_TYPE) i-j) / maxgrid;
      path[i][j] = ((DATA_TYPE) i*(j-1)) / maxgrid;
    }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int maxgrid,
		 DATA_TYPE POLYBENCH_2D(path,MAXGRID,MAXGRID,maxgrid,maxgrid))
{
  int i, j;

  for (i = 0; i < maxgrid; i++)
    for (j = 0; j < maxgrid; j++) {
      pb_emit(path[i][j]);
      if ((i * maxgrid + j) % 20 == 0) pb_newline();
    }
  pb_newline();
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
/* Source (modified): http://www.cs.uic.edu/~iluican/reg_detect.c */
static
void kernel_reg_detect(int niter, int maxgrid, int length,
		       DATA_TYPE POLYBENCH_2D(sum_tang,MAXGRID,MAXGRID,maxgrid,maxgrid),
		       DATA_TYPE POLYBENCH_2D(mean,MAXGRID,MAXGRID,maxgrid,maxgrid),
		       DATA_TYPE POLYBENCH_2D(path,MAXGRID,MAXGRID,maxgrid,maxgrid),
		       DATA_TYPE POLYBENCH_3D(diff,MAXGRID,MAXGRID,LENGTH,maxgrid,maxgrid,length),
		       DATA_TYPE POLYBENCH_3D(sum_diff,MAXGRID,MAXGRID,LENGTH,maxgrid,maxgrid,length))
{
  int t, i, j, cnt;

#pragma scop
  for (t = 0; t < _PB_NITER; t++)
    {
      #pragma omp parallel for firstprivate(length,maxgrid) private(i,cnt) shared(diff,sum_tang) 
      for (j = 0; j <= _PB_MAXGRID - 1; j++)
	for (i = j; i <= _PB_MAXGRID - 1; i++)
	  for (cnt = 0; cnt <= _PB_LENGTH - 1; cnt++)
	    diff[j][i][cnt] = sum_tang[j][i];

      #pragma omp parallel for firstprivate(length,maxgrid) private(i,cnt) shared(mean,sum_diff,diff) 
      for (j = 0; j <= _PB_MAXGRID - 1; j++)
        {
	  for (i = j; i <= _PB_MAXGRID - 1; i++)
            {
	      sum_diff[j][i][0] = diff[j][i][0];
	      for (cnt = 1; cnt <= _PB_LENGTH - 1; cnt++)
		sum_diff[j][i][cnt] = sum_diff[j][i][cnt - 1] + diff[j][i][cnt];
	      mean[j][i] = sum_diff[j][i][_PB_LENGTH - 1];
            }
        }

      for (i = 0; i <= _PB_MAXGRID - 1; i++)
	path[0][i] = mean[0][i];

      for (j = 1; j <= _PB_MAXGRID - 1; j++)
	#pragma omp parallel for firstprivate(j,maxgrid) shared(mean,path) 
	for (i = j; i <= _PB_MAXGRID - 1; i++)
	  path[j][i] = path[j - 1][i - 1] + mean[j][i];
    }
#pragma endscop

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int niter = NITER;
  int maxgrid = MAXGRID;
  int length = LENGTH;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(sum_tang, DATA_TYPE, MAXGRID, MAXGRID, maxgrid, maxgrid);
  POLYBENCH_2D_ARRAY_DECL(mean, DATA_TYPE, MAXGRID, MAXGRID, maxgrid, maxgrid);
  POLYBENCH_2D_ARRAY_DECL(path, DATA_TYPE, MAXGRID, MAXGRID, maxgrid, maxgrid);
  POLYBENCH_3D_ARRAY_DECL(diff, DATA_TYPE, MAXGRID, MAXGRID, LENGTH, maxgrid, maxgrid, length);
  POLYBENCH_3D_ARRAY_DECL(sum_diff, DATA_TYPE, MAXGRID, MAXGRID, LENGTH, maxgrid, maxgrid, length);

  /* Initialize array(s). */
  init_array (maxgrid,
	      POLYBENCH_ARRAY(sum_tang),
	      POLYBENCH_ARRAY(mean),
	      POLYBENCH_ARRAY(path));

  /* Optional perturbed input, see PB_PERTURB. */
  if (argc > 1)
    {
      unsigned long long pb_state = pb_seed(argv[1]);
      PB_PERTURB(sum_tang, (MAXGRID + POLYBENCH_PADDING_FACTOR) * (MAXGRID + POLYBENCH_PADDING_FACTOR));
      PB_PERTURB(mean, (MAXGRID + POLYBENCH_PADDING_FACTOR) * (MAXGRID + POLYBENCH_PADDING_FACTOR));
      PB_PERTURB(path, (MAXGRID + POLYBENCH_PADDING_FACTOR) * (MAXGRID + POLYBENCH_PADDING_FACTOR));
      PB_PERTURB(diff, (MAXGRID + POLYBENCH_PADDING_FACTOR) * (MAXGRID + POLYBENCH_PADDING_FACTOR) * (LENGTH + POLYBENCH_PADDING_FACTOR));
      PB_PERTURB(sum_diff, (MAXGRID + POLYBENCH_PADDING_FACTOR) * (MAXGRID + POLYBENCH_PADDING_FACTOR) * (LENGTH + POLYBENCH_PADDING_FACTOR));
    }


  /* Start timer. */
  pb_timer_start();

  /* Run kernel. */
  kernel_reg_detect (niter, maxgrid, length,
		     POLYBENCH_ARRAY(sum_tang),
		     POLYBENCH_ARRAY(mean),
		     POLYBENCH_ARRAY(path),
		     POLYBENCH_ARRAY(diff),
		     POLYBENCH_ARRAY(sum_diff));

  /* Stop and print timer. */
  pb_timer_stop();
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(maxgrid, POLYBENCH_ARRAY(path)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(sum_tang);
  POLYBENCH_FREE_ARRAY(mean);
  POLYBENCH_FREE_ARRAY(path);
  POLYBENCH_FREE_ARRAY(diff);
  POLYBENCH_FREE_ARRAY(sum_diff);

  pb_report();

  return 0;
}
