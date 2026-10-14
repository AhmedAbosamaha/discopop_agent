#ifndef DATA_H
#define DATA_H

#if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) \
    && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
# define SMALL_DATASET
#endif
#ifdef MINI_DATASET
# define LEN_1D 2000
# define LEN_2D 64
#endif
#ifdef SMALL_DATASET
# define LEN_1D 32000
# define LEN_2D 256
#endif
#ifdef STANDARD_DATASET
# define LEN_1D 32000
# define LEN_2D 1024
#endif
#ifdef LARGE_DATASET
# define LEN_1D 32000
# define LEN_2D 2048
#endif
#ifdef EXTRALARGE_DATASET
# define LEN_1D 32000
# define LEN_2D 4096
#endif
#define iterations 48

typedef double real_t;

extern real_t *a, *b, *c, *d, *e;
extern real_t (*aa)[LEN_2D], (*bb)[LEN_2D], (*cc)[LEN_2D];

int dummy(real_t *, real_t *, real_t *, real_t *, real_t *, real_t (*)[LEN_2D], real_t (*)[LEN_2D], real_t (*)[LEN_2D]);
real_t kernel_s233(void);

#endif
