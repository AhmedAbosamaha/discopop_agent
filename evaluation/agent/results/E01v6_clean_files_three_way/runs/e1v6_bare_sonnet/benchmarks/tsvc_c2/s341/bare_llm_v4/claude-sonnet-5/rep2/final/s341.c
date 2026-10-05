#include "data.h"
#include <stdlib.h>

/* Fixed number of chunks used to parallelize the compaction loop below.
   Independent of thread count (work is distributed across whichever
   threads run via normal OpenMP scheduling) and clamped to LEN_1D so we
   never create more chunks than elements. */
#define S341_MAX_CHUNKS 1024

real_t kernel_s341(void)
{
    int n = LEN_1D;
    int num_chunks = (n < S341_MAX_CHUNKS) ? n : S341_MAX_CHUNKS;

    /* chunk_count[ci]  : number of elements with b[i] > 0 inside chunk ci.
       chunk_offset[ci] : exclusive prefix sum of chunk_count, i.e. the
                           index in a[] at which chunk ci's first kept
                           element must be written.
       Both are heap allocated: num_chunks is a runtime value and must not
       become a stack array. */
    int *chunk_count  = (int *)malloc((size_t)num_chunks * sizeof(int));
    int *chunk_offset = (int *)malloc((size_t)num_chunks * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: count, independently per chunk, how many elements will
           be kept. Chunks are disjoint, contiguous index ranges, so each
           iteration ci only reads its own slice of b[] and writes its own
           slot of chunk_count[]: no dependence between iterations. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(b, chunk_count, num_chunks, n)
        for (int ci = 0; ci < num_chunks; ci++) {
            int chunk_start = (int)((long)ci * n / num_chunks);
            int chunk_end   = (int)((long)(ci + 1) * n / num_chunks);
            int count = 0;
            for (int i = chunk_start; i < chunk_end; i++) {
                if (b[i] > (real_t)0.) count++;
            }
            chunk_count[ci] = count;
        }

        /* Sequential exclusive prefix sum over the per-chunk counts. This
           is the loop-carried dependence from the original algorithm,
           moved here: its length is num_chunks (small, fixed), not
           LEN_1D, so it stays cheap at every problem size and is left
           serial. It must finish before pass 2 reads chunk_offset[]. */
        int running = 0;
        for (int ci = 0; ci < num_chunks; ci++) {
            chunk_offset[ci] = running;
            running += chunk_count[ci];
        }

        /* Pass 2: write the kept elements into their final, globally
           compacted position. chunk_offset[] was fully computed above
           before this loop starts, so each chunk writes to a disjoint,
           pre-determined slice of a[] matching the original left-to-right
           visiting order: iterations are independent. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(a, b, chunk_offset, num_chunks, n)
        for (int ci = 0; ci < num_chunks; ci++) {
            int chunk_start = (int)((long)ci * n / num_chunks);
            int chunk_end   = (int)((long)(ci + 1) * n / num_chunks);
            int pos = chunk_offset[ci];
            for (int i = chunk_start; i < chunk_end; i++) {
                if (b[i] > (real_t)0.) {
                    a[pos] = b[i];
                    pos++;
                }
            }
        }

        dummy(a, b, c, d, e);
    }

    free(chunk_count);
    free(chunk_offset);

    return (real_t)0;
}
