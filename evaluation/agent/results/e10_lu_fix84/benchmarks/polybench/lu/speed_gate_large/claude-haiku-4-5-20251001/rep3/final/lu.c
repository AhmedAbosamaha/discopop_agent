/**
 * lu.c: This file is part of the PolyBench/C 3.2 test suite.
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
/* Default data type is double, default size is 1024. */
#include "lu.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      A[i][j] = ((DATA_TYPE) (i+1)*(j+1)) / n;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n))

{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      pb_emit(A[i][j]);
      if ((i * n + j) % 20 == 0) pb_newline();
    }
  pb_newline();
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_lu(int n,
	       DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int i, j, k;

#pragma scop
  for (k = 0; k < _PB_N; k++)
    {
#pragma omp parallel for
      for (j = k + 1; j < _PB_N; j++)
	A[k][j] = A[k][j] / A[k][k];
#pragma omp parallel for collapse(2)
      for(i = k + 1; i < _PB_N; i++)
	for (j = k + 1; j < _PB_N; j++)
	  A[i][j] = A[i][j] - A[i][k] * A[k][j];
    }
#pragma endscop

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, N, N, n, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A));

  /* Optional perturbed input, see PB_PERTURB. */
  if (argc > 1)
    {
      unsigned long long pb_state = pb_seed(argv[1]);
      PB_PERTURB(A, (N + POLYBENCH_PADDING_FACTOR) * (N + POLYBENCH_PADDING_FACTOR));
    }


  /* Start timer. */
  pb_timer_start();

  /* Run kernel. */
  kernel_lu (n, POLYBENCH_ARRAY(A));

  /* Stop and print timer. */
  pb_timer_stop();
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(A)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);

  pb_report();

  return 0;
}
