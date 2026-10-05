/* Kernel k31. */
#include "tsvc_b1/k31.h"
#include <stdlib.h>

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_k31(void)
{
    /* The inner i-loop updates u[i] and v[i] every iteration while also
     * reading v[i+off] and u[i+far]. off and far are the fixed, loop-
     * invariant distances for which this kernel is known not to form a
     * dependence cycle: for every i in range, i+off and i+far never land
     * on a slot that an EARLIER iteration of this same sweep has already
     * overwritten, so in the original sequential order every such read
     * always sees the value the array held before this i-loop started
     * (i.e. whatever the previous repetition / pb_mix left there) - the
     * dependence is a value moving from the previous pass into this one,
     * not iterations of this loop depending on each other.
     *
     * That dependence is preserved, not deleted, by snapshotting u and v
     * into heap buffers before the loop runs (a pass that fully finishes
     * before the read/write pass starts) and having every iteration read
     * its offset values from that frozen snapshot instead of from the
     * live, concurrently-written array. Any index the snapshot doesn't
     * cover (i+off or i+far landing outside [0, LEN_1D)) is, by the same
     * argument, an index this loop never writes, so reading it straight
     * from the live array there is race-free and matches the original
     * access exactly. Writes to u[i] and v[i] land on a distinct slot per
     * i, so with the offset reads coming from the snapshot the iterations
     * are fully independent. */
    real_t *old_u = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *old_v = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* old_u, old_v: shared heap buffers, written once per index below -
         * no two iterations touch the same slot.
         * u, v: shared live arrays, read here (read-only in this loop). */
        #pragma omp parallel for shared(u, v, old_u, old_v)
        for (long i = 0; i < LEN_1D; i++) {
            old_u[i] = u[i];
            old_v[i] = v[i];
        }

        /* u, v: shared; each iteration writes only u[i] and v[i], disjoint
         *       across iterations, so the writes don't race.
         * c, d: shared, read-only.
         * old_u, old_v: shared, read-only snapshot taken above.
         * io, ifr, vread, uread: declared inside the loop body, so each is
         *       already private per iteration - no clause needed. */
        #pragma omp parallel for shared(u, v, c, d, old_u, old_v)
        for (long i = 1; i < LEN_1D; i++) {
            long io = i + off;
            long ifr = i + far;
            real_t vread = (io >= 0 && io < LEN_1D) ? old_v[io] : v[io];
            u[i] += vread * c[i];
            real_t uread = (ifr >= 0 && ifr < LEN_1D) ? old_u[ifr] : u[ifr];
            v[i] = uread * d[i] + c[i];
        }
        pb_mix(nl);
    }

    free(old_u);
    free(old_v);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
