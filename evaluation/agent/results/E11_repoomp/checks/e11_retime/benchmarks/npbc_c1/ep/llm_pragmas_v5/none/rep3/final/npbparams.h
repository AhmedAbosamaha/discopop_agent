#if defined(MINI_DATASET)
#define	CLASS	 'S'
#define	M	24
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
#define	CLASS	 'S'
#define	M	24
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
#define	CLASS	 'W'
#define	M	25
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
#define	CLASS	 'A'
#define	M	28
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
#define	CLASS	 'B'
#define	M	30
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
#define	CLASS	 'S'
#define	M	24
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
