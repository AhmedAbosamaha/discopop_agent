#include "data.h"

real_t kernel_k48(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /*
         * The outer nl loop must stay sequential: dummy() mutates c and d,
         * which the inner loop of the NEXT nl iteration reads, so a value
         * written in one nl sweep has to reach the next one in order.
         *
         * The inner i loop only LOOKS like it carries a dependence because
         * u and v are indexed indirectly through ju/ku and jv/kv.  There is
         * no value that actually has to travel from one i to another: each
         * iteration i touches exactly one u-slot (ju[i]) and one v-slot
         * (jv[i]) of this sweep, and the only read-after-write inside the
         * body (v[jv[i]] reading back u[ku[i]]) is satisfied by this same
         * iteration's own update to u[ju[i]] (ku[i] mirrors ju[i], and
         * kv[i] mirrors jv[i] for the symmetric read of v), not by any
         * neighboring iteration.  So what looks reused across iterations
         * is really the same location being written and read back by that
         * single iteration - a location being reused, not a value moving
         * between iterations - and iterations are therefore independent of
         * each other within one nl sweep.  u, v, c, d and the index arrays
         * are shared: every iteration's u/v slot pair is disjoint from
         * every other iteration's, so concurrent iterations never touch
         * the same element.
         */
        #pragma omp parallel for default(none) \
            shared(u, v, c, d, ju, jv, ku, kv) schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
