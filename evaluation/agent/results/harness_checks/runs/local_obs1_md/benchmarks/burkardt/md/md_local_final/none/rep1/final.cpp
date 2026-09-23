# include <cmath>
# include <cstdlib>
using namespace std;

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
# define MD_ND 3
# define MD_NP 50
# define MD_STEPS 10
#endif
#ifdef SMALL_DATASET
# define MD_ND 3
# define MD_NP 500
# define MD_STEPS 20
#endif
#ifdef STANDARD_DATASET
# define MD_ND 3
# define MD_NP 1000
# define MD_STEPS 50
#endif
#ifdef LARGE_DATASET
# define MD_ND 3
# define MD_NP 2000
# define MD_STEPS 100
#endif
#ifdef EXTRALARGE_DATASET
# define MD_ND 3
# define MD_NP 4000
# define MD_STEPS 200
#endif
#ifndef MD_ND
# define MD_ND 3
# define MD_NP 1000
# define MD_STEPS 50
#endif

void compute ( int np, int nd, double pos[], double vel[], double mass, double f[],
  double *pot, double *kin );
double dist ( int nd, double r1[], double r2[], double dr[] );
void initialize ( int np, int nd, double box[], int *seed, double pos[], double vel[],
  double acc[] );
double r8_uniform_01 ( int *seed );
void update ( int np, int nd, double pos[], double vel[], double f[], double acc[],
  double mass, double dt );

/* ---- driver ---------------------------------------------------------------
   The original reported ten energy rows to stdout while timing itself with
   omp_get_wtime. Here the same ten rows become digest values, the step loop is the timed
   region, and the final positions are folded in so a rewrite cannot match the energies
   while moving the particles. */
int main ( int argc, char *argv[] )
{
  int nd = MD_ND, np = MD_NP, step_num = MD_STEPS;
  double dt = 0.0001, mass = 1.0;
  double e0, kinetic, potential;
  int seed = 123456789;
  int step, step_print, step_print_index, step_print_num;
  double *acc = new double[nd*np];
  double *box = new double[nd];
  double *force = new double[nd*np];
  double *pos = new double[nd*np];
  double *vel = new double[nd*np];

  for ( int i = 0; i < nd; i++ ) box[i] = 10.0;

  initialize ( np, nd, box, &seed, pos, vel, acc );
  if ( argc > 1 )
    {
      /* Perturbed input: every particle nudged deterministically before the run. */
      pb_seed ( argv[1] );
      for ( int i = 0; i < nd*np; i++ ) pos[i] += pb_uniform() * 0.01;
    }

  compute ( np, nd, pos, vel, mass, force, &potential, &kinetic );
  e0 = potential + kinetic;

  step_print = 0;
  step_print_index = 0;
  step_print_num = 10;
  pb_emit ( potential );
  pb_emit ( kinetic );
  pb_emit ( ( potential + kinetic - e0 ) / e0 );
  step_print_index = step_print_index + 1;
  step_print = ( step_print_index * step_num ) / step_print_num;

  /* Precompute which steps will emit output to break loop-carried dependency
     on step_print_index. Store in a lookup array for O(1) checks. */
  bool *should_emit = new bool[step_num + 1];
  for ( int i = 0; i <= step_num; i++ ) should_emit[i] = false;
  for ( int i = 0; i <= step_print_num; i++ )
    {
      int emit_at = ( i * step_num ) / step_print_num;
      if ( emit_at >= 1 && emit_at <= step_num ) should_emit[emit_at] = true;
    }

  pb_timer_start ( );
  for ( step = 1; step <= step_num; step++ )
    {
      compute ( np, nd, pos, vel, mass, force, &potential, &kinetic );
      if ( should_emit[step] )
        {
          pb_emit ( potential );
          pb_emit ( kinetic );
          pb_emit ( ( potential + kinetic - e0 ) / e0 );
        }
      update ( np, nd, pos, vel, force, acc, mass, dt );
    }
  pb_timer_stop ( );
  delete [] should_emit;

#ifndef PB_FULL_DUMP
  /* Digest only. The original never prints positions, so the full dump stays exactly the
     original's energy table; the digest still folds them in, which stops a rewrite that
     reproduces the energies while moving the particles. */
  for ( int i = 0; i < nd*np; i++ ) pb_emit ( pos[i] );
#endif
  pb_report ( );

  delete [] acc;
  delete [] box;
  delete [] force;
  delete [] pos;
  delete [] vel;
  return 0;
}

void compute ( int np, int nd, double pos[], double vel[], 
  double mass, double f[], double *pot, double *kin )

//****************************************************************************80
//
//  Purpose:
//
//    COMPUTE computes the forces and energies.
//
//  Discussion:
//
//    The computation of forces and energies is fully parallel.
//
//    The potential function V(X) is a harmonic well which smoothly
//    saturates to a maximum value at PI/2:
//
//      v(x) = ( sin ( min ( x, PI2 ) ) )**2
//
//    The derivative of the potential is:
//
//      dv(x) = 2.0 * sin ( min ( x, PI2 ) ) * cos ( min ( x, PI2 ) )
//            = sin ( 2.0 * min ( x, PI2 ) )
//
//  Licensing:
//
//    This code is distributed under the GNU LGPL license. 
//
//  Modified:
//
//    21 November 2007
//
//  Author:
//
//    Original FORTRAN90 version by Bill Magro.
//    C++ version by John Burkardt.
//
//  Parameters:
//
//    Input, int NP, the number of particles.
//
//    Input, int ND, the number of spatial dimensions.
//
//    Input, double POS[ND*NP], the position of each particle.
//
//    Input, double VEL[ND*NP], the velocity of each particle.
//
//    Input, double MASS, the mass of each particle.
//
//    Output, double F[ND*NP], the forces.
//
//    Output, double *POT, the total potential energy.
//
//    Output, double *KIN, the total kinetic energy.
//
{
  double d;
  double d2;
  int i;
  int j;
  int k;
  double ke = 0.0;
  double pe = 0.0;
  double PI2 = 3.141592653589793 / 2.0;
  double rij[3];

#pragma omp parallel for ordered \
  shared(f, nd, np, pos, vel, mass, PI2, pe, ke) \
  private(i, j, rij, d, d2)
  for ( k = 0; k < np; k++ )
  {
//
//  Compute the potential energy and forces.
//
    for ( i = 0; i < nd; i++ )
    {
      f[i+k*nd] = 0.0;
    }

    double d2_vals[np];
    double d_vals[np];
    double rij_vals[np][3];

    for ( j = 0; j < np; j++ )
    {
      if ( k != j )
      {
        d = dist ( nd, pos+k*nd, pos+j*nd, rij );
        d_vals[j] = d;
        for ( i = 0; i < nd; i++ )
        {
          rij_vals[j][i] = rij[i];
        }

        if ( d < PI2 )
        {
          d2_vals[j] = d;
        }
        else
        {
          d2_vals[j] = PI2;
        }
      }
    }

//
//  Compute the kinetic energy.
//
    double ke_local = 0.0;
    for ( i = 0; i < nd; i++ )
    {
      ke_local = ke_local + vel[i+k*nd] * vel[i+k*nd];
    }

#pragma omp ordered
    {
      for ( j = 0; j < np; j++ )
      {
        if ( k != j )
        {
          pe = pe + 0.5 * pow ( sin ( d2_vals[j] ), 2 );

          for ( i = 0; i < nd; i++ )
          {
            f[i+k*nd] = f[i+k*nd] - rij_vals[j][i] * sin ( 2.0 * d2_vals[j] ) / d_vals[j];
          }
        }
      }
      ke = ke + ke_local;
    }
  }

  ke = ke * 0.5 * mass;
  
  *pot = pe;
  *kin = ke;

  return;
}
double dist ( int nd, double r1[], double r2[], double dr[] )

//****************************************************************************80
//
//  Purpose:
//
//    DIST computes the displacement (and its norm) between two particles.
//
//  Licensing:
//
//    This code is distributed under the GNU LGPL license.
//
//  Modified:
//
//    21 November 2007
//
//  Author:
//
//    Original FORTRAN90 version by Bill Magro.
//    C++ version by John Burkardt.
//
//  Parameters:
//
//    Input, int ND, the number of spatial dimensions.
//
//    Input, double R1[ND], R2[ND], the positions of the particles.
//
//    Output, double DR[ND], the displacement vector.
//
//    Output, double D, the Euclidean norm of the displacement.
//
{
  double d;
  int i;

  d = 0.0;
#pragma omp parallel for reduction(+:d)
  for ( i = 0; i < nd; i++ )
  {
    dr[i] = r1[i] - r2[i];
    d = d + dr[i] * dr[i];
  }
  d = sqrt ( d );

  return d;
}
void initialize ( int np, int nd, double box[], int *seed, double pos[], 
  double vel[], double acc[] )

//****************************************************************************80
//
//  Purpose:
//
//    INITIALIZE initializes the positions, velocities, and accelerations.
//
//  Licensing:
//
//    This code is distributed under the GNU LGPL license. 
//
//  Modified:
//
//    21 November 2007
//
//  Author:
//
//    Original FORTRAN90 version by Bill Magro.
//    C++ version by John Burkardt.
//
//  Parameters:
//
//    Input, int NP, the number of particles.
//
//    Input, int ND, the number of spatial dimensions.
//
//    Input, double BOX[ND], specifies the maximum position
//    of particles in each dimension.
//
//    Input, int *SEED, a seed for the random number generator.
//
//    Output, double POS[ND*NP], the position of each particle.
//
//    Output, double VEL[ND*NP], the velocity of each particle.
//
//    Output, double ACC[ND*NP], the acceleration of each particle.
//
{
  int i;
  int j;
//
//  Give the particles random positions within the box.
//
  for ( i = 0; i < nd; i++ )
  {
    for ( j = 0; j < np; j++ )
    {
      pos[i+j*nd] = box[i] * r8_uniform_01 ( seed );
    }
  }

  for ( j = 0; j < np; j++ )
  {
    for ( i = 0; i < nd; i++ )
    {
      vel[i+j*nd] = 0.0;
    }
  }
  for ( j = 0; j < np; j++ )
  {
    for ( i = 0; i < nd; i++ )
    {
      acc[i+j*nd] = 0.0;
    }
  }

  return;
}
double r8_uniform_01 ( int *seed )

//****************************************************************************80
//
//  Purpose:
//
//    R8_UNIFORM_01 is a unit pseudorandom R8.
//
//  Discussion:
//
//    This routine implements the recursion
//
//      seed = 16807 * seed mod ( 2**31 - 1 )
//      unif = seed / ( 2**31 - 1 )
//
//    The integer arithmetic never requires more than 32 bits,
//    including a sign bit.
//
//  Licensing:
//
//    This code is distributed under the GNU LGPL license. 
//
//  Modified:
//
//    11 August 2004
//
//  Author:
//
//    John Burkardt
//
//  Reference:
//
//    Paul Bratley, Bennett Fox, Linus Schrage,
//    A Guide to Simulation,
//    Springer Verlag, pages 201-202, 1983.
//
//    Bennett Fox,
//    Algorithm 647:
//    Implementation and Relative Efficiency of Quasirandom
//    Sequence Generators,
//    ACM Transactions on Mathematical Software,
//    Volume 12, Number 4, pages 362-376, 1986.
//
//  Parameters:
//
//    Input/output, int *SEED, a seed for the random number generator.
//
//    Output, double R8_UNIFORM_01, a new pseudorandom variate, strictly between
//    0 and 1.
//
{
  int k;
  double r;

  k = *seed / 127773;

  *seed = 16807 * ( *seed - k * 127773 ) - k * 2836;

  if ( *seed < 0 )
  {
    *seed = *seed + 2147483647;
  }

  r = ( double ) ( *seed ) * 4.656612875E-10;

  return r;
}
void update ( int np, int nd, double pos[], double vel[], double f[], 
  double acc[], double mass, double dt )

//****************************************************************************80
//
//  Purpose:
//
//    UPDATE updates positions, velocities and accelerations.
//
//  Discussion:
//
//    The time integration is fully parallel.
//
//    A velocity Verlet algorithm is used for the updating.
//
//    x(t+dt) = x(t) + v(t) * dt + 0.5 * a(t) * dt**2
//    v(t+dt) = v(t) + 0.5 * ( a(t) + a(t+dt) ) * dt
//    a(t+dt) = f(t) / m
//
//  Licensing:
//
//    This code is distributed under the GNU LGPL license. 
//
//  Modified:
//
//    21 November 2007
//
//  Author:
//
//    Original FORTRAN90 version by Bill Magro.
//    C++ version by John Burkardt.
//
//  Parameters:
//
//    Input, int NP, the number of particles.
//
//    Input, int ND, the number of spatial dimensions.
//
//    Input/output, double POS[ND*NP], the position of each particle.
//
//    Input/output, double VEL[ND*NP], the velocity of each particle.
//
//    Input, double F[ND*NP], the force on each particle.
//
//    Input/output, double ACC[ND*NP], the acceleration of each particle.
//
//    Input, double MASS, the mass of each particle.
//
//    Input, double DT, the time step.
//
{
  int i;
  int j;
  double rmass;

  rmass = 1.0 / mass;

//# pragma omp parallel \
  shared ( acc, dt, nd, np, pos, rmass, vel ) \
  private ( i, j )

//# pragma omp for

  for ( j = 0; j < np; j++ )
  {
    for ( i = 0; i < nd; i++ )
    {
      pos[i+j*nd] = pos[i+j*nd] + vel[i+j*nd] * dt + 0.5 * acc[i+j*nd] * dt * dt;
      vel[i+j*nd] = vel[i+j*nd] + 0.5 * dt * ( f[i+j*nd] * rmass + acc[i+j*nd] );
      acc[i+j*nd] = f[i+j*nd] * rmass;
    }
  }

  return;
}
