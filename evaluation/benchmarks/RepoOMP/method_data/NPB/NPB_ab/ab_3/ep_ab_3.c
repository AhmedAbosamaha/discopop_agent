#include "npb-C.h"
#include "npbparams.h"
#define	MK		16
#define	MM		(M - MK)
#define	NN		(1 << MM)
#define	NK		(1 << MK)
#define	NQ		10
#define EPSILON		1.0e-8
#define	A		1220703125.0
#define	S		271828183.0
#define	TIMERS_ENABLED	FALSE

static double x[2*NK];
#pragma omp threadprivate(x)
static double q[NQ];

int main(int argc, char **argv) {

    double Mops, t1, t2, t3, t4, x1, x2, sx, sy, tm, an, tt, gc;
    double dum[3] = { 1.0, 1.0, 1.0 };
    int np, ierr, node, no_nodes, i, ik, kk, l, k, nit, ierrcode,
	no_large_nodes, np_add, k_offset, j;
    int nthreads = 1;
    boolean verified;
    char size[13+1];	

    sprintf(size, "%12.0f", pow(2.0, M+1));
    for (j = 13; j >= 1; j--) {
	if (size[j] == '.') size[j] = ' ';
    }
    verified = FALSE;

    np = NN;

    vranlc(0, &(dum[0]), dum[1], &(dum[2]));
    dum[0] = randlc(&(dum[1]), dum[2]);
    
    
#pragma omp parallel for default(shared) private(i) schedule(static, (2*NK)/32)
    for (i = 0; i < 2*NK; i++) x[i] = -1.0e99;
    
    Mops = log(sqrt(fabs(max(1.0, 1.0))));

    timer_clear(1);
    timer_clear(2);
    timer_clear(3);
    timer_start(1);

    vranlc(0, &t1, A, x);

    t1 = A;

    for ( i = 1; i <= MK+1; i++) {
	t2 = randlc(&t1, t1);
    }

    an = t1;
    tt = S;
    gc = 0.0;
    sx = 0.0;
    sy = 0.0;

    for ( i = 0; i <= NQ - 1; i++) {
	q[i] = 0.0;
    }

    k_offset = -1;

    
#pragma omp parallel copyin(x) firstprivate(k_offset, an)
    {
        double t1, t2, t3, t4, x1, x2;
        int kk, i, ik, l;
        double qq[NQ];		

        
        #pragma GCC ivdep
        for (i = 0; i < NQ; i++) qq[i] = 0.0;

        
        
        int chunk_size = (np > 32) ? ((np + 31) / 32) : 1;

#pragma omp for reduction(+:sx,sy) schedule(static, chunk_size)
        for (k = 1; k <= np; k++) {
            kk = k_offset + k;
            t1 = S;
            t2 = an;

            
            for (i = 1; i <= 100; i++) {
                ik = kk / 2;
                if (2 * ik != kk) t3 = randlc(&t1, t2);
                if (ik == 0) break;
                t3 = randlc(&t2, t2);
                kk = ik;
            }

            if (TIMERS_ENABLED == TRUE) timer_start(3);
            vranlc(2*NK, &t1, A, x-1);
            if (TIMERS_ENABLED == TRUE) timer_stop(3);

            if (TIMERS_ENABLED == TRUE) timer_start(2);

            
            int NK_unroll = NK - (NK % 2);
            for ( i = 0; i < NK_unroll; i += 2) {
                
                register double x1_0 = 2.0 * x[2*i] - 1.0;
                register double x2_0 = 2.0 * x[2*i+1] - 1.0;
                register double x1_1 = 2.0 * x[2*(i+1)] - 1.0;
                register double x2_1 = 2.0 * x[2*(i+1)+1] - 1.0;
                
                register double t1_0 = pow2(x1_0) + pow2(x2_0);
                register double t1_1 = pow2(x1_1) + pow2(x2_1);
                
                if (t1_0 <= 1.0) {
                    register double t2_0 = sqrt(-2.0 * log(t1_0) / t1_0);
                    register double t3_0 = (x1_0 * t2_0);				
                    register double t4_0 = (x2_0 * t2_0);				
                    register int l_0 = max(fabs(t3_0), fabs(t4_0));
                    qq[l_0] += 1.0;				
                    sx += t3_0;				
                    sy += t4_0;				
                }
                if (t1_1 <= 1.0) {
                    register double t2_1 = sqrt(-2.0 * log(t1_1) / t1_1);
                    register double t3_1 = (x1_1 * t2_1);				
                    register double t4_1 = (x2_1 * t2_1);				
                    register int l_1 = max(fabs(t3_1), fabs(t4_1));
                    qq[l_1] += 1.0;				
                    sx += t3_1;				
                    sy += t4_1;				
                }
            }
            
            
            for (i = NK_unroll; i < NK; i++) {
                x1 = 2.0 * x[2*i] - 1.0;
                x2 = 2.0 * x[2*i+1] - 1.0;
                t1 = pow2(x1) + pow2(x2);
                if (t1 <= 1.0) {
                    t2 = sqrt(-2.0 * log(t1) / t1);
                    t3 = (x1 * t2);				
                    t4 = (x2 * t2);				
                    l = max(fabs(t3), fabs(t4));
                    qq[l] += 1.0;				
                    sx = sx + t3;				
                    sy = sy + t4;				
                }
            }
            if (TIMERS_ENABLED == TRUE) timer_stop(2);
        }
        
        
        for (i = 0; i <= NQ - 1; i++) {
            if (qq[i] != 0.0) {  
#pragma omp atomic
                q[i] += qq[i];
            }
        }

#if defined(_OPENMP)
#pragma omp master
        nthreads = omp_get_num_threads();
