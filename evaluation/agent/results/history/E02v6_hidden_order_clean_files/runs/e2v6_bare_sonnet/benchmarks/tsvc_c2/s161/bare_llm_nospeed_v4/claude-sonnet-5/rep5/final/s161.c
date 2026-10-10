#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /*
         * Original loop carried a dependence through c[]: when b[i] < 0,
         * iteration i writes c[i+1]; when b[i+1] >= 0, iteration i+1 reads
         * that same c[i+1] as "c[i]".  The branch taken at each i depends
         * only on b[i] (not on any value produced inside this loop), and
         * the value written to c[i+1] depends only on the pre-loop values
         * of a[i] and d[i] (a[i] is never written by the b[i]<0 branch, so
         * it still holds its pre-loop value when read here).  So the
         * dependence is a value moving from iteration i to iteration i+1
         * through c[i+1]/c[i] -- not just a reused location.  We preserve
         * it by splitting the loop into two independent passes with a
         * barrier between them: pass 1 performs every c[i+1] write (all
         * distinct locations, so iterations are independent); pass 2,
         * which runs only after pass 1 has fully completed, reads c[i]
         * (now holding whatever pass 1 wrote for it, exactly as the
         * sequential order would have left it) and performs every a[i]
         * write (again all distinct locations).
         */
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        #pragma omp parallel for shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
