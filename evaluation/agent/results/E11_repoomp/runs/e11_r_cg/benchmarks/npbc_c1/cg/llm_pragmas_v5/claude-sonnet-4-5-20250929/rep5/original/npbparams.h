#if defined(MINI_DATASET)
#define	NA	1400
#define	NONZER	7
#define	NITER	15
#define	SHIFT	10.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#elif defined(SMALL_DATASET)
#define	NA	1400
#define	NONZER	7
#define	NITER	15
#define	SHIFT	10.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#elif defined(STANDARD_DATASET)
#define	NA	7000
#define	NONZER	8
#define	NITER	15
#define	SHIFT	12.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#elif defined(LARGE_DATASET)
#define	NA	14000
#define	NONZER	11
#define	NITER	15
#define	SHIFT	20.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#elif defined(EXTRALARGE_DATASET)
#define	NA	75000
#define	NONZER	13
#define	NITER	75
#define	SHIFT	60.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#else
#define	NA	1400
#define	NONZER	7
#define	NITER	15
#define	SHIFT	10.0
#define	RCOND	1.0e-1
#define	CONVERTDOUBLE	FALSE
#define COMPILETIME "packaged"
#define NPBVERSION "3.0 structured"
#define CS1 "gcc"
#define CS2 "gcc"
#define CS3 "-lm"
#define CS4 "-I../common"
#define CS5 "-O0 -fopenmp "
#define CS6 "-fopenmp -lm"
#define CS7 "randdp"
#endif
