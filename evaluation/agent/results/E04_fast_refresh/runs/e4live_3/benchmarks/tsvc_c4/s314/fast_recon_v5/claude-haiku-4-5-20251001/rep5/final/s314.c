#include "data.h"
#include <stdlib.h>

real_t kernel_s314(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        // Divide array into segments and compute max of each segment independently
        int segment_size = 1024;
        int num_segments = (LEN_1D + segment_size - 1) / segment_size;
        real_t* segment_max = (real_t*)malloc(num_segments * sizeof(real_t));

        // Each segment iteration is independent (Do-All pattern)
 #pragma omp parallel for firstprivate(num_segments) shared(segment_max) 
        for (int seg = 0; seg < num_segments; seg++) {
            int start = seg * segment_size;
            int end = (seg + 1) * segment_size < LEN_1D ? (seg + 1) * segment_size : LEN_1D;

            real_t max_val = a[start];
            for (int i = start + 1; i < end; i++) {
                if (a[i] > max_val) {
                    max_val = a[i];
                }
            }
            segment_max[seg] = max_val;
        }

        // Combine segment maxes to find overall maximum
        x = segment_max[0];
        for (int seg = 1; seg < num_segments; seg++) {
            if (segment_max[seg] > x) {
                x = segment_max[seg];
            }
        }

        free(segment_max);
        dummy(a, b, c, d, e, x);
    }
    return x;
}
