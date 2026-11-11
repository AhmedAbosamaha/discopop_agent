#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *temp = malloc(LEN_1D * sizeof(real_t));
        memcpy(temp, a, LEN_1D * sizeof(real_t));

        // Parallel scan: multiple stages to expose parallelism
        // Each stage combines elements at increasing distances
        for (int dist = 1; dist < LEN_1D; dist *= 2) {
            real_t *temp_in = malloc(LEN_1D * sizeof(real_t));
            memcpy(temp_in, temp, LEN_1D * sizeof(real_t));

            // Stage: combine elements at distance `dist` in parallel
            for (int i = dist; i < LEN_1D; i++) {
                real_t mult = 1.0;
                for (int j = i - dist + 1; j <= i; j++) {
                    mult *= b[j];
                }
                temp[i] += temp_in[i - dist] * mult;
            }

            free(temp_in);
        }

        memcpy(a, temp, LEN_1D * sizeof(real_t));
        free(temp);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
