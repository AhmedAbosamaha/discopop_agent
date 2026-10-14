#include "data.h"

real_t kernel_s2111(void)
{
    enum { NT = 32 };
    for (int nl = 0; nl < iterations; nl++) {
        int edge = (LEN_2D - 1 + NT - 1) / NT;
        for (int w = 0; w < 2 * NT - 1; w++) {
            int first = w < NT ? 0 : w - NT + 1;
            int last = w < NT ? w : NT - 1;
            for (int tj = first; tj <= last; tj++) {
                int ti = w - tj;
                int jlo = 1 + tj * edge;
                int ilo = 1 + ti * edge;
                int jhi = jlo + edge < LEN_2D ? jlo + edge : LEN_2D;
                int ihi = ilo + edge < LEN_2D ? ilo + edge : LEN_2D;
                for (int j = jlo; j < jhi; j++) {
                    for (int i = ilo; i < ihi; i++) {
                        aa[j][i] = (aa[j][i-1] + aa[j-1][i])/1.9;
                    }
                }
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
