#ifndef DATA_H
#define DATA_H

#if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) \
    && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
# define SMALL_DATASET
#endif
#ifdef MINI_DATASET
# define LEN_1D 2000
#endif
#ifdef SMALL_DATASET
# define LEN_1D 32000
#endif
#ifdef STANDARD_DATASET
# define LEN_1D 4000000
#endif
#ifdef LARGE_DATASET
# define LEN_1D 32000000
#endif
#ifdef EXTRALARGE_DATASET
# define LEN_1D 192000000
#endif
#define iterations 48

typedef double real_t;

extern real_t *a, *b, *c, *d, *e;

int dummy(real_t *, real_t *, real_t *, real_t *, real_t *);
real_t kernel_s292(void);

#endif
