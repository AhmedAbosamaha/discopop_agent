#!/usr/bin/env python3
"""Package the application benchmarks as single self-contained files, like the kernels.

`prepare_polybench.py` does this for the kernels; this is the same contract for the
applications (agent/docs/THESIS_EXPERIMENTS.md §2 and §1a), and it exists because the
applications as shipped break three rules the harness depends on:

* **Size comes from argv.** The harness runs a benchmark with no arguments except the
  perturbation seed, so every size becomes a compile-time `#define` behind a dataset
  guard (MINI / SMALL / STANDARD / LARGE / EXTRALARGE) — which is also what lets T0.1
  pick a verification size per benchmark.
* **Output is not deterministic.** `md` prints two wall-clock timestamps, the processor
  and thread counts, and its own elapsed time. Stdout becomes the three-line digest the
  kernels already print (`pb_values`, `pb_sum`, `pb_wsum`), with the exact values under
  `-DPB_FULL_DUMP`, and the timed region goes to stderr.
* **The answer is in the file.** `md` carries its OpenMP pragmas as comments (§1a), so a
  model would read the solution; the dead OpenMP code is removed and what was removed is
  recorded in `meta.json`.

The computation is never rewritten. Each recipe copies the original's computational
functions **verbatim** and synthesises only what surrounds them: input generation, the
timed call sequence, and the digest. `--validate` then builds the ORIGINAL program and the
packaged one and compares the original's deterministic output (each recipe says which
lines those are) against the packaged full dump.

    agent/tools/prepare_apps.py --out agent/prepared --validate
    agent/tools/prepare_apps.py md --out agent/prepared --size SMALL
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

AGENT_DIR = Path(__file__).resolve().parent.parent
HARNESS_ROOT = AGENT_DIR.parent
BENCHMARKS = HARNESS_ROOT / "benchmarks"
GENERATOR_VERSION = 1  # v1: md, pathfinder

SIZES = ["MINI", "SMALL", "STANDARD", "LARGE", "EXTRALARGE"]

# Identical in behaviour to prepare_polybench.py, so a packaged application and a packaged
# kernel are read the same way by the agent's gate and by the harness.
_PRELUDE = r"""
/* ---- output: digest by default, exact values with -DPB_FULL_DUMP --------- */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#ifdef PB_FULL_DUMP
/* PB_DUMP_FORMAT is the recipe's, because the dump is compared against the ORIGINAL's own
   printing. %.17g by default: md's energies span 1e+03 to 1e-11, and fixed decimals would
   print half the table as 0.000000. Where the original prints with %g (hotspot's
   writeoutput), the dump must use %g too — rounding an already-rounded value in the
   comparison cannot recover the digit the original never printed, and 0.47 % of hotspot's
   values at SMALL sit exactly on that boundary. */
#ifndef PB_DUMP_FORMAT
# define PB_DUMP_FORMAT "%.17g\n"
#endif
static void pb_emit(double v) { fprintf(stdout, PB_DUMP_FORMAT, v); }
static void pb_report(void) { }
#else
static unsigned long long pb_count = 0;
static double pb_sum = 0.0;
static double pb_wsum = 0.0;
static void pb_emit(double v)
{
  pb_count++;
  pb_sum += v;
  pb_wsum += v * (double)((pb_count % 9973) + 1);
}
static void pb_report(void)
{
  printf("pb_values %llu\n", pb_count);
  printf("pb_sum %.17g\n", pb_sum);
  printf("pb_wsum %.17g\n", pb_wsum);
}
#endif

/* ---- optional perturbed input: argv[1] = seed ------------------------------
   A shipped input can be one the kernel leaves unchanged, and an output check on such an
   input cannot tell a changed algorithm from the original (seidel-2d, §2). With a seed the
   generated input moves deterministically, so the rewrite is also checked on an input the
   profile was never taken on. */
static unsigned long long pb_state = 88172645463325252ULL;
static void pb_seed(const char* s)
{
  pb_state = strtoull(s, NULL, 10) * 0x9E3779B97F4A7C15ULL + 1ULL;
}
static double pb_uniform(void)
{
  pb_state = pb_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(pb_state >> 11) / 9007199254740992.0;
}

/* ---- timed region: the computation only -------------------------------------
   Allocation, input generation and output stay outside it, so the ratio the gate and the
   harness compute belongs to the computation. Elapsed time goes to stderr as
   "DP_TIMED_REGION_SECONDS <s>"; stdout stays deterministic. */
static struct timespec pb_t0;
static void pb_timer_start(void) { clock_gettime(CLOCK_MONOTONIC, &pb_t0); }
static void pb_timer_stop(void)
{
  struct timespec t1;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  fprintf(stderr, "DP_TIMED_REGION_SECONDS %.9f\n",
          (double)(t1.tv_sec - pb_t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - pb_t0.tv_nsec));
}
"""


def _guard(sizes: Dict[str, Dict[str, str]]) -> str:
    """The dataset guard, with STANDARD as the default when no size is given."""
    names = list(next(iter(sizes.values())))
    out = ["", "/* ---- problem size: compile-time, the harness passes no arguments ------- */"]
    for size in SIZES:
        if size in sizes:
            out.append(f"#ifdef {size}_DATASET")
            out += [f"# define {k} {v}" for k, v in sizes[size].items()]
            out.append("#endif")
    out.append(f"#ifndef {names[0]}")
    out += [f"# define {k} {v}" for k, v in sizes["STANDARD"].items()]
    out.append("#endif")
    return "\n".join(out) + "\n"


def _lines(path: Path, first: int, last: int) -> str:
    """Lines [first, last] of a file, 1-based and inclusive — a function copied verbatim."""
    return "\n".join(path.read_text().splitlines()[first - 1:last]) + "\n"


@dataclass
class Recipe:
    name: str
    suite: str
    category: str
    source: Path                           # the original, as shipped
    language: str                          # "c" or "cpp"
    sizes: Dict[str, Dict[str, str]]       # dataset -> #defines
    original_args: Dict[str, List[str]]    # dataset -> the original program's arguments
    original_build: List[str]              # extra flags the ORIGINAL needs (e.g. -fopenmp)
    deterministic: Callable[[str], str]    # the original's output, reduced to what must match
    assemble: Callable[["Recipe"], Tuple[str, List[str]]]  # -> (source, what was removed)
    exclude_functions: List[str]
    note: str
    # Some originals write their result to a file instead of stdout (nw's result.txt), so
    # that file, not stdout, is what `deterministic` must be given.
    result_file: Optional[str] = None
    # hotspot reads its grids from files. The packaged source can write the grids it
    # generated (-DPB_EMIT_INPUT), and the validator runs that first so the original is
    # given exactly the same input instead of a second, separately written generator.
    emits_input: bool = False
    # How the full dump prints a value. It has to match the ORIGINAL's own formatting, or the
    # comparison fails on digits the original never printed rather than on the computation.
    dump_format: str = "%.17g\\n"
    # An original that is not one translation unit: NPB links its benchmark against four
    # files from common/ and includes npbparams.hpp from its own directory. Without these
    # the validator cannot build the program it is supposed to compare against.
    original_sources: Callable[["Recipe"], List[str]] = lambda r: []
    original_includes: Callable[["Recipe"], List[str]] = lambda r: []
    # NPB checks its own answer against fixed reference values, so a perturbed input would
    # fail that verification: for those benchmarks the seed is ignored and the check is
    # reported as not applicable rather than as a pass.
    perturbable: bool = True
    # NPB only: the benchmark's own timer calls, where pb_timer_start/stop are injected;
    # an optional (declaration, replacement) pair hoisting a result variable to file scope;
    # and the digest emitted after the benchmark returns.
    npb_timer: Tuple[str, str] = ("", "")
    # (declaration to replace, its replacement, the file-scope declaration to add). The
    # verdict and the verified result live in locals of the benchmark's main; the driver
    # has to see them, and moving a declaration changes no computation.
    npb_hoist: Tuple[Tuple[str, str, str], ...] = ()
    npb_digest_body: str = ""
    npb_digest_note: str = ""
    # The benchmark in its original file layout (decision D6): -> ({relative path: text},
    # what was removed), or None for a program that is one file to begin with.
    assemble_project: Optional[Callable[["Recipe"], Tuple[Dict[str, str], List[str]]]] = None
    project_units: List[str] = field(default_factory=list)
    project_include_dirs: List[str] = field(default_factory=list)
    # Compile flags the packaged PROJECT needs on every build (LULESH: -DUSE_MPI=0). They go
    # into meta.json's `project.cflags`, which the harness and the agent pass to every build.
    project_cflags: List[str] = field(default_factory=list)
    # The benchmark's own EXPERT parallel version, unmodified, when the package can be derived
    # from it by the same edits (LULESH: LLNL's release). `--references` writes it in package
    # form under agent/reference_solutions/<suite>/<name>/ for `verify-source --source DIR`.
    reference_dir: Optional[Path] = None
    # Extra macros for the VALIDATOR's dump build only. The full dump has two readers with
    # different needs: the validator compares it with what the ORIGINAL prints, the harness
    # compares it between the original and a changed program under a relative tolerance. Where
    # the original prints something that is not a result (LULESH's symmetry differences: the
    # residue of subtracting equal numbers, which any reordered addition moves by tens of
    # percent), the package emits it under this macro alone and keeps it out of the harness's
    # comparison.
    validate_macros: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# burkardt md — molecular dynamics; the force loop carries a reduction
# ---------------------------------------------------------------------------

_MD_ROW = re.compile(r"^\s+\d+\s+([-\d.e+]+)\s+([-\d.e+]+)\s+([-\d.e+]+)\s*$", re.M)


def _md_deterministic(out: str) -> str:
    """md's energy table: the only output independent of the clock and the thread count.

    Dropped: the two `timestamp()` dates, the processors/threads banner (it prints
    omp_get_max_threads()), and the elapsed-time line.
    """
    return "\n".join(
        "\n".join(repr(float(v)) for v in m.groups()) for m in _MD_ROW.finditer(out)
    )


def _md_assemble(r: Recipe) -> Tuple[str, List[str]]:
    src = r.source
    # The computation, copied exactly as shipped: compute, dist, initialize, r8_uniform_01,
    # update. `timestamp` (wall-clock printing) and the original `main` are left behind.
    verbatim = "".join(_lines(src, a, b) for a, b in
                       ((207, 331), (334, 378), (381, 450), (453, 519), (569, 643)))
    removed = [
        "4 commented-out OpenMP pragmas (§1a: the model would read the answer)",
        "omp.h, omp_get_num_procs/omp_get_max_threads banner, omp_get_wtime timing",
        "timestamp() wall-clock lines and the cout banner",
        "the original main(), replaced by a fixed-size, seeded driver",
    ]
    if "# pragma omp" not in src.read_text():
        removed[0] = "no commented-out pragmas found in this copy"
    forward = """
void compute ( int np, int nd, double pos[], double vel[], double mass, double f[],
  double *pot, double *kin );
double dist ( int nd, double r1[], double r2[], double dr[] );
void initialize ( int np, int nd, double box[], int *seed, double pos[], double vel[],
  double acc[] );
double r8_uniform_01 ( int *seed );
void update ( int np, int nd, double pos[], double vel[], double f[], double acc[],
  double mass, double dt );
"""
    driver = """
/* ---- driver ---------------------------------------------------------------
   The original reported ten energy rows to stdout while timing itself with
   omp_get_wtime. Here the same ten rows become digest values, the step loop is the timed
   region, and the final positions are folded in so a rewrite cannot match the energies
   while moving the particles. */
int main ( int argc, char *argv[] )
{
  int nd = MD_ND, np = MD_NP, step_num = MD_STEPS;
  double dt = 0.0001, mass = 1.0;
  double e0, kinetic, potential;
  int seed = 123456789;
  int step, step_print, step_print_index, step_print_num;
  double *acc = new double[nd*np];
  double *box = new double[nd];
  double *force = new double[nd*np];
  double *pos = new double[nd*np];
  double *vel = new double[nd*np];

  for ( int i = 0; i < nd; i++ ) box[i] = 10.0;

  initialize ( np, nd, box, &seed, pos, vel, acc );
  if ( argc > 1 )
    {
      /* Perturbed input: every particle nudged deterministically before the run. */
      pb_seed ( argv[1] );
      for ( int i = 0; i < nd*np; i++ ) pos[i] += pb_uniform() * 0.01;
    }

  compute ( np, nd, pos, vel, mass, force, &potential, &kinetic );
  e0 = potential + kinetic;

  step_print = 0;
  step_print_index = 0;
  step_print_num = 10;
  pb_emit ( potential );
  pb_emit ( kinetic );
  pb_emit ( ( potential + kinetic - e0 ) / e0 );
  step_print_index = step_print_index + 1;
  step_print = ( step_print_index * step_num ) / step_print_num;

  pb_timer_start ( );
  for ( step = 1; step <= step_num; step++ )
    {
      compute ( np, nd, pos, vel, mass, force, &potential, &kinetic );
      if ( step == step_print )
        {
          pb_emit ( potential );
          pb_emit ( kinetic );
          pb_emit ( ( potential + kinetic - e0 ) / e0 );
          step_print_index = step_print_index + 1;
          step_print = ( step_print_index * step_num ) / step_print_num;
        }
      update ( np, nd, pos, vel, force, acc, mass, dt );
    }
  pb_timer_stop ( );

#ifndef PB_FULL_DUMP
  /* Digest only. The original never prints positions, so the full dump stays exactly the
     original's energy table; the digest still folds them in, which stops a rewrite that
     reproduces the energies while moving the particles. */
  for ( int i = 0; i < nd*np; i++ ) pb_emit ( pos[i] );
#endif
  pb_report ( );

  delete [] acc;
  delete [] box;
  delete [] force;
  delete [] pos;
  delete [] vel;
  return 0;
}
"""
    body = _PRELUDE + _guard(r.sizes) + forward + driver + "\n" + verbatim
    return "# include <cmath>\n# include <cstdlib>\nusing namespace std;\n" + body, removed


MD = Recipe(
    name="md",
    suite="burkardt",
    category="molecular-dynamics",
    source=BENCHMARKS / "burkardt" / "md" / "md.cpp",
    language="cpp",
    sizes={
        "MINI": {"MD_ND": "3", "MD_NP": "50", "MD_STEPS": "10"},
        "SMALL": {"MD_ND": "3", "MD_NP": "500", "MD_STEPS": "20"},
        "STANDARD": {"MD_ND": "3", "MD_NP": "1000", "MD_STEPS": "50"},
        "LARGE": {"MD_ND": "3", "MD_NP": "2000", "MD_STEPS": "100"},
        "EXTRALARGE": {"MD_ND": "3", "MD_NP": "4000", "MD_STEPS": "200"},
    },
    original_args={s: [v["MD_ND"], v["MD_NP"], v["MD_STEPS"]] for s, v in {
        "MINI": {"MD_ND": "3", "MD_NP": "50", "MD_STEPS": "10"},
        "SMALL": {"MD_ND": "3", "MD_NP": "500", "MD_STEPS": "20"},
        "STANDARD": {"MD_ND": "3", "MD_NP": "1000", "MD_STEPS": "50"},
        "LARGE": {"MD_ND": "3", "MD_NP": "2000", "MD_STEPS": "100"},
        "EXTRALARGE": {"MD_ND": "3", "MD_NP": "4000", "MD_STEPS": "200"},
    }.items()},
    original_build=["-fopenmp"],
    deterministic=_md_deterministic,
    assemble=_md_assemble,
    exclude_functions=["timestamp", "initialize", "r8_uniform_01", "pb_emit", "pb_report",
                       "pb_seed", "pb_uniform", "pb_timer_start", "pb_timer_stop"],
    note="the force loop in compute() carries a reduction over potential and kinetic energy",
)


# ---------------------------------------------------------------------------
# Rodinia pathfinder — dynamic programming over a grid, row by row
# ---------------------------------------------------------------------------

def _pathfinder_deterministic(out: str) -> str:
    """The original prints the whole wall, then `data`, then `dst`; the last row is the result.

    The packaged version emits the same numbers in the same order (wall row by row, then
    dst), so the two dumps compare as a whole. Dropped: `timer: <cycles>` from
    `pin_stats_dump` — a measurement, and an rdtsc count that changes every run.
    """
    return "\n".join(v for line in out.splitlines() if not line.startswith("timer:")
                     for v in line.split())


def _pathfinder_assemble(r: Recipe) -> Tuple[str, List[str]]:
    driver = """
/* ---- pathfinder, packaged --------------------------------------------------
   The original took its size from argv, filled the grid with rand() under a fixed seed,
   timed itself with rdtsc (x86-only inline assembly) and printed the whole grid. Here the
   size is a define, the grid is filled by the packaging's own generator so a seed can
   perturb it, the row loop is the timed region, and the values become digest output.
   The row update itself is copied unchanged. */
#define MIN(a, b) ((a)<=(b) ? (a) : (b))

static int rows, cols;
static int* data_;
static int** wall;
static int* result;

static void pf_init(int argc, char** argv)
{
  rows = PF_ROWS;
  cols = PF_COLS;
  data_ = new int[rows*cols];
  wall = new int*[rows];
  for (int n = 0; n < rows; n++) wall[n] = data_ + cols*n;
  result = new int[cols];
  /* Unperturbed, this is the original's own generation (srand(M_SEED), rand()%10), so the
     packaged dump can be compared value for value against the original program. A seed
     switches to the packaging's generator, which is what perturbs the input. */
  if (argc > 1)
    {
      pb_seed(argv[1]);
      for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
          wall[i][j] = (int)(pb_uniform() * 10.0);
    }
  else
    {
      srand(PF_SEED);
      for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
          wall[i][j] = rand() % 10;
    }
  for (int j = 0; j < cols; j++) result[j] = wall[0][j];
}

int main(int argc, char** argv)
{
  pf_init(argc, argv);

  int *src, *dst, *temp;
  int min;

  dst = result;
  src = new int[cols];

  pb_timer_start();
  for (int t = 0; t < rows-1; t++) {
      temp = src;
      src = dst;
      dst = temp;
      for(int n = 0; n < cols; n++){
        min = src[n];
        if (n > 0)
          min = MIN(min, src[n-1]);
        if (n < cols-1)
          min = MIN(min, src[n+1]);
        dst[n] = wall[t+1][n]+min;
      }
  }
  pb_timer_stop();

  /* The original's print order exactly: the whole wall (from init), then `data` — its
     first row, printed a second time — then the result row `dst`. */
  for (int i = 0; i < rows; i++)
    for (int j = 0; j < cols; j++)
      pb_emit((double)wall[i][j]);
  for (int i = 0; i < cols; i++) pb_emit((double)data_[i]);
  for (int i = 0; i < cols; i++) pb_emit((double)dst[i]);
  pb_report();

  delete [] data_;
  delete [] wall;
  delete [] dst;
  delete [] src;
  return 0;
}
"""
    removed = [
        "timer.h: rdtsc inline assembly and the pin_stats_* macros (x86-only, replaced by the timed region)",
        "BENCH_PRINT block, replaced by the digest",
        "argv sizes, replaced by the dataset guard",
        "the `timer: <cycles>` line (a measurement, not a result)",
    ]
    return _PRELUDE + _guard(r.sizes) + driver, removed


PATHFINDER = Recipe(
    name="pathfinder",
    suite="rodinia-3.1",
    category="dynamic-programming",
    source=BENCHMARKS / "rodinia_3.1" / "serial" / "pathfinder" / "pathfinder.cpp",
    language="cpp",
    sizes={
        "MINI": {"PF_COLS": "1000", "PF_ROWS": "10", "PF_SEED": "9"},
        "SMALL": {"PF_COLS": "10000", "PF_ROWS": "50", "PF_SEED": "9"},
        "STANDARD": {"PF_COLS": "100000", "PF_ROWS": "100", "PF_SEED": "9"},
        "LARGE": {"PF_COLS": "200000", "PF_ROWS": "500", "PF_SEED": "9"},
        "EXTRALARGE": {"PF_COLS": "400000", "PF_ROWS": "1000", "PF_SEED": "9"},
    },
    original_args={"MINI": ["1000", "10"], "SMALL": ["10000", "50"],
                   "STANDARD": ["100000", "100"], "LARGE": ["200000", "500"],
                   "EXTRALARGE": ["400000", "1000"]},
    original_build=[],
    deterministic=_pathfinder_deterministic,
    assemble=_pathfinder_assemble,
    exclude_functions=["pf_init", "pb_emit", "pb_report", "pb_seed", "pb_uniform",
                       "pb_timer_start", "pb_timer_stop"],
    note=("unperturbed, the grid is generated exactly as the original does (srand(9), "
          "rand()%10), so the dumps compare value for value; a seed switches to the "
          "packaging's generator, which is what perturbs the input"),
)


# ---------------------------------------------------------------------------
# Rodinia nw — Needleman-Wunsch; a wavefront where order matters (category C)
# ---------------------------------------------------------------------------

_NW_OPENMP_BLOCK = re.compile(
    r"^[ \t]*#[ \t]*ifdef[ \t]+(?:OPENMP|OMP_OFFLOAD)\b.*?^[ \t]*#[ \t]*endif.*?$\n",
    re.M | re.S)


def _nw_deterministic(out: str) -> str:
    """nw writes its traceback to result.txt, not to stdout; the validator passes it here."""
    return "\n".join(v for line in out.splitlines()
                     if not line.startswith("print traceback") for v in line.split())


def _nw_assemble(r: Recipe) -> Tuple[str, List[str]]:
    src = r.source
    # maximum(), blosum62 and nw_optimized() are the computation, copied as shipped — except
    # that the disabled OpenMP inside nw_optimized is removed first (§1a: with `//#define
    # OPENMP` this file IS the OpenMP version, so the model would read the answer).
    verbatim = _lines(src, 30, 44) + _lines(src, 50, 75)
    kernel = _lines(src, 103, 226)
    kernel, n_omp = _NW_OPENMP_BLOCK.subn("", kernel)
    # The kernel carries the original's progress prose ("Processing bottom-right matrix").
    # Stdout must hold nothing but the digest, so those lines go; they are not results.
    kernel, n_print = re.subn(r"^[ \t]*printf\s*\(\s*\"[^\"]*\"\s*\)\s*;\s*\n", "", kernel, flags=re.M)
    removed = [
        f"{n_omp} disabled #ifdef OPENMP / OMP_OFFLOAD block(s) inside nw_optimized "
        "(§1a: the serial file is the OpenMP version with //#define OPENMP)",
        f"{n_print} progress printf line(s) inside the kernel — stdout carries the digest only",
        "omp.h, the num_threads argument and the 'Num of threads' line",
        "get_time()/gettimeofday timing and the 'Total time' line",
        "the traceback's result.txt file, replaced by the digest",
    ]
    driver = """
/* ---- nw, packaged ----------------------------------------------------------
   The original took dimension, penalty and a thread count from argv, printed progress
   lines and wrote its traceback to result.txt. Here the size is a define, the sequences are
   generated as the original generates them (srand(7)), nw_optimized is the timed region,
   and the traceback values become the digest. */
int maximum(int a, int b, int c);
void nw_optimized(int *input_itemsets, int *output_itemsets, int *referrence,
                  int max_rows, int max_cols, int penalty);

int main(int argc, char** argv)
{
  int max_rows = NW_DIM + 1, max_cols = NW_DIM + 1, penalty = NW_PENALTY;
  int *referrence = (int*)malloc(max_rows * max_cols * sizeof(int));
  int *input_itemsets = (int*)malloc(max_rows * max_cols * sizeof(int));
  int *output_itemsets = (int*)malloc(max_rows * max_cols * sizeof(int));
  if (!input_itemsets || !referrence || !output_itemsets)
    { fprintf(stderr, "error: can not allocate memory\\n"); return 1; }

  for (int i = 0; i < max_cols; i++)
    for (int j = 0; j < max_rows; j++)
      input_itemsets[i*max_cols+j] = 0;

  /* Unperturbed this is the original's own generation, so the dumps compare value for
     value; a seed switches to the packaging's generator and moves the sequences. */
  if (argc > 1)
    {
      pb_seed(argv[1]);
      for (int i = 1; i < max_rows; i++) input_itemsets[i*max_cols] = (int)(pb_uniform()*10.0)+1;
      for (int j = 1; j < max_cols; j++) input_itemsets[j] = (int)(pb_uniform()*10.0)+1;
    }
  else
    {
      srand(7);
      for (int i = 1; i < max_rows; i++) input_itemsets[i*max_cols] = rand() % 10 + 1;
      for (int j = 1; j < max_cols; j++) input_itemsets[j] = rand() % 10 + 1;
    }

  for (int i = 1; i < max_cols; i++)
    for (int j = 1; j < max_rows; j++)
      referrence[i*max_cols+j] = blosum62[input_itemsets[i*max_cols]][input_itemsets[j]];
  for (int i = 1; i < max_rows; i++) input_itemsets[i*max_cols] = -i * penalty;
  for (int j = 1; j < max_cols; j++) input_itemsets[j] = -j * penalty;

  pb_timer_start();
  nw_optimized(input_itemsets, output_itemsets, referrence, max_rows, max_cols, penalty);
  pb_timer_stop();

  /* The original's traceback, emitting the same values in the same order. */
  for (int i = max_rows - 2, j = max_rows - 2; i >= 0 && j >= 0;)
    {
      int nw, n, w, traceback;
      if (i == max_rows - 2 && j == max_rows - 2)
        pb_emit((double)input_itemsets[i * max_cols + j]);
      if (i == 0 && j == 0) break;
      if (i > 0 && j > 0)
        {
          nw = input_itemsets[(i - 1) * max_cols + j - 1];
          w  = input_itemsets[ i * max_cols + j - 1];
          n  = input_itemsets[(i - 1) * max_cols + j];
        }
      else if (i == 0) { nw = n = LIMIT; w = input_itemsets[i * max_cols + j - 1]; }
      else if (j == 0) { nw = w = LIMIT; n = input_itemsets[(i - 1) * max_cols + j]; }
      else { break; }
      int new_nw = nw + referrence[i * max_cols + j];
      int new_w = w - penalty;
      int new_n = n - penalty;
      traceback = maximum(new_nw, new_w, new_n);
      if (traceback == new_nw) traceback = nw;
      if (traceback == new_w) traceback = w;
      if (traceback == new_n) traceback = n;
      pb_emit((double)traceback);
      if (traceback == nw) { i--; j--; continue; }
      else if (traceback == w) { j--; continue; }
      else if (traceback == n) { i--; continue; }
    }
  pb_report();

  free(referrence);
  free(input_itemsets);
  free(output_itemsets);
  return 0;
}
"""
    # Ahead of the copied kernel, as in the original (its lines 1 and 12): nw_optimized
    # uses both, and a #define that arrives with the driver arrives too late.
    defines = "\n#define LIMIT -999\n#define BLOCK_SIZE 16\n"
    return _PRELUDE + _guard(r.sizes) + defines + verbatim + kernel + driver, removed


NW = Recipe(
    name="nw",
    suite="rodinia-3.1",
    category="dynamic-programming",
    source=BENCHMARKS / "rodinia_3.1" / "serial" / "nw" / "needle.cpp",
    language="cpp",
    sizes={
        "MINI": {"NW_DIM": "512", "NW_PENALTY": "10"},
        "SMALL": {"NW_DIM": "2048", "NW_PENALTY": "10"},
        "STANDARD": {"NW_DIM": "8192", "NW_PENALTY": "10"},
        "LARGE": {"NW_DIM": "16384", "NW_PENALTY": "10"},
        "EXTRALARGE": {"NW_DIM": "32768", "NW_PENALTY": "10"},
    },
    original_args={"MINI": ["512", "10", "1"], "SMALL": ["2048", "10", "1"],
                   "STANDARD": ["8192", "10", "1"], "LARGE": ["16384", "10", "1"],
                   "EXTRALARGE": ["32768", "10", "1"]},
    original_build=["-fopenmp"],
    deterministic=_nw_deterministic,
    assemble=_nw_assemble,
    exclude_functions=["maximum", "pb_emit", "pb_report", "pb_seed", "pb_uniform",
                       "pb_timer_start", "pb_timer_stop"],
    note=("the original writes its traceback to result.txt; the packaged version emits the "
          "same values as the digest, and the validator reads the original's file"),
    result_file="result.txt",
)


# ---------------------------------------------------------------------------
# NPB is / mg / lu — the reference suite; each verifies its own result
# ---------------------------------------------------------------------------
# A benchmark is the .cpp plus npbparams.hpp plus four files from common/. They concatenate
# into one translation unit (checked: the merge compiles and prints "Verification =
# SUCCESSFUL"), so the recipe merges rather than rewrites. The benchmarks print from 14, 33
# and 39 places; rewriting that by pattern is what went wrong on md, so instead the
# benchmark's own main is renamed and its stdout is redirected to stderr for its duration —
# the prose is kept, out of the way, and stdout carries the digest alone.
NPB_ROOT = BENCHMARKS / "NPB"
_NPB_COMMON = ("c_print_results", "c_randdp", "c_timers", "wtime")

# Sizes are NPB's own classes. `is` derives everything from CLASS; mg and lu take explicit
# parameters, so the guard emits the values the suite's setparams would have written.
_MG_CLASS = {
    "S": {"NX_DEFAULT": "32", "NY_DEFAULT": "32", "NZ_DEFAULT": "32", "NIT_DEFAULT": "4",
          "LM": "5", "LT_DEFAULT": "5"},
    "W": {"NX_DEFAULT": "128", "NY_DEFAULT": "128", "NZ_DEFAULT": "128", "NIT_DEFAULT": "4",
          "LM": "7", "LT_DEFAULT": "7"},
    "A": {"NX_DEFAULT": "256", "NY_DEFAULT": "256", "NZ_DEFAULT": "256", "NIT_DEFAULT": "4",
          "LM": "8", "LT_DEFAULT": "8"},
    "B": {"NX_DEFAULT": "256", "NY_DEFAULT": "256", "NZ_DEFAULT": "256", "NIT_DEFAULT": "20",
          "LM": "8", "LT_DEFAULT": "8"},
}
_LU_CLASS = {
    "S": {"ISIZ1": "12", "ISIZ2": "12", "ISIZ3": "12", "ITMAX_DEFAULT": "50",
          "INORM_DEFAULT": "50", "DT_DEFAULT": "0.5"},
    "W": {"ISIZ1": "33", "ISIZ2": "33", "ISIZ3": "33", "ITMAX_DEFAULT": "300",
          "INORM_DEFAULT": "300", "DT_DEFAULT": "1.5e-3"},
    "A": {"ISIZ1": "64", "ISIZ2": "64", "ISIZ3": "64", "ITMAX_DEFAULT": "250",
          "INORM_DEFAULT": "250", "DT_DEFAULT": "2.0"},
    "B": {"ISIZ1": "102", "ISIZ2": "102", "ISIZ3": "102", "ITMAX_DEFAULT": "250",
          "INORM_DEFAULT": "250", "DT_DEFAULT": "2.0"},
}
# The other npbparams entries are strings c_print_results echoes; they are not parameters.
_NPB_FIXED = {"DEBUG_DEFAULT": "0", "NDIM1": "8", "NDIM2": "8", "NDIM3": "8", "ONE": "1",
              "CONVERTDOUBLE": "FALSE", "COMPILETIME": '"packaged"', "NPBVERSION": '"4.1"',
              "COMPILERVERSION": '"packaged"', "CS1": '"(none)"', "CS2": '"(none)"',
              "CS3": '"(none)"', "CS4": '"(none)"', "CS5": '"(none)"', "CS6": '"(none)"',
              "CS7": '"randdp"'}


def _npb_deterministic(out: str) -> str:
    """NPB checks its own answer; the verdict line is what must survive packaging."""
    return "1" if re.search(r"Verification\s*=\s*SUCCESSFUL", out) else "0"


def _npb_assemble(r: Recipe) -> Tuple[str, List[str]]:
    """Merge one NPB benchmark with the common sources and drive it from a new main."""
    bench = r.source                                   # …/NPB/<B>/NPB-SER/<B>/<b>.cpp
    common = bench.parent.parent / "common"
    header = (common / "npb-CPP.hpp").read_text().replace('#include "wtime.hpp"', "")
    header += (common / "wtime.hpp").read_text()

    body = bench.read_text()
    body = body.replace('#include "../common/npb-CPP.hpp"', "")
    body = body.replace('#include "npbparams.hpp"', "")
    # The benchmark's own main becomes npb_main; the synthesised one below calls it.
    body, n_main = re.subn(r"^int main\s*\(", "int npb_main(", body, count=1, flags=re.M)
    if n_main != 1:
        raise SystemExit(f"{r.name}: expected exactly one main(), found {n_main}")
    # The timed region is inside the benchmark, so the timer is injected at its own
    # timer_start/stop lines (each a single, unambiguous occurrence — checked).
    start, stop = r.npb_timer
    body, n_s = re.subn(re.escape(start), f"pb_timer_start();\n\t{start}", body, count=1)
    body, n_e = re.subn(re.escape(stop), f"{stop}\n\tpb_timer_stop();", body, count=1)
    if n_s != 1 or n_e != 1:
        raise SystemExit(f"{r.name}: timer injection matched {n_s}/{n_e} sites, expected 1/1")
    removed = [
        "npbparams.hpp replaced by the dataset guard (NPB's own class parameters)",
        "the compile-date and compiler-version strings c_print_results echoes",
        f"the benchmark's main renamed to npb_main; its output ({r.note}) goes to stderr",
    ]
    # The verdict and the result values live in locals of the benchmark's main, where the
    # driver cannot see them. Each hoist replaces one DECLARATION and renames that variable
    # to a file-scope one; no computation is touched.
    hoisted = ""
    for decl, keep, declare in r.npb_hoist:
        if decl not in body:
            raise SystemExit(f"{r.name}: declaration to hoist not found: {decl!r}")
        body = body.replace(decl, keep, 1)
        hoisted += declare + "\n"
        removed.append(f"hoisted a result variable to file scope so the digest can read it: "
                       f"{decl.strip()} (declaration only)")

    common_src = ""
    for name in _NPB_COMMON:
        text = (common / f"{name}.cpp").read_text()
        for inc in ('#include "npb-CPP.hpp"', '#include "wtime.hpp"',
                    '#include "../common/npb-CPP.hpp"'):
            text = text.replace(inc, "")
        common_src += text + "\n"

    driver = f"""
/* ---- NPB {r.name}, packaged ------------------------------------------------------
   The benchmark runs unchanged and checks its own answer against NPB's reference values.
   Its printing — banner, iteration numbers, c_print_results — goes to stderr, so stdout
   carries the digest alone: the verification verdict, and {r.npb_digest_note}.
   The input cannot be perturbed: NPB compares against fixed reference values, so a
   perturbed input would fail its own verification. argv is passed through untouched. */
int npb_main(int argc, char** argv);

int main(int argc, char** argv)
{{
  fflush(stdout);
  int saved = dup(1);
  dup2(2, 1);                 /* the benchmark's own output -> stderr */
  int rc = npb_main(argc, argv);
  fflush(stdout);
  dup2(saved, 1);             /* stdout back, for the digest */
  close(saved);
{r.npb_digest_body}  pb_report();
  return rc;
}}
"""
    text = ("#include <unistd.h>\n" + _PRELUDE + _guard(r.sizes)
            + "\n/* ---- npb-CPP.hpp and wtime.hpp, inlined ---- */\n" + header
            + hoisted + "\n/* ---- the benchmark, as shipped ---- */\n" + body
            + "\n/* ---- common/: c_print_results, c_randdp, c_timers, wtime ---- */\n"
            + common_src + driver)
    return text, removed


_NPB_HARNESS_HPP = """/* Generated by agent/tools/prepare_apps.py — the harness's own code: output digest
   (full dump with -DPB_FULL_DUMP), the timed region, the optional seed. Defined in
   pb_harness.cpp; declared here so the benchmark unit and the driver share ONE digest. */
#ifndef PB_HARNESS_HPP
#define PB_HARNESS_HPP
void pb_emit(double v);
void pb_report(void);
void pb_seed(const char* s);
double pb_uniform(void);
void pb_timer_start(void);
void pb_timer_stop(void);
#endif
"""


def _npb_assemble_project(r: Recipe) -> Tuple[Dict[str, str], List[str]]:
    """The benchmark in its original layout: `<B>/<b>.cpp` plus `common/` as separate units.

    Decision D6 (THESIS_EXPERIMENTS.md §5g). The edits to the benchmark file are the SAME
    as the merged recipe's — its main becomes npb_main, the timer is injected at its own
    timer calls, a result declaration is hoisted to file scope — plus the harness driver
    appended at the end of the same file (it reads the benchmark's file-scope results, so
    it belongs to that unit). Everything under common/ is copied verbatim; npbparams.hpp is
    the dataset guard; the harness helpers are their own unit, so the digest is one object
    for the whole program."""
    bench = r.source
    upper = bench.parent.name                              # LU
    common = bench.parent.parent / "common"
    body = bench.read_text()
    body, n_main = re.subn(r"^int main\s*\(", "int npb_main(", body, count=1, flags=re.M)
    if n_main != 1:
        raise SystemExit(f"{r.name}: expected exactly one main(), found {n_main}")
    start, stop = r.npb_timer
    body, n_s = re.subn(re.escape(start), f"pb_timer_start();\n\t{start}", body, count=1)
    body, n_e = re.subn(re.escape(stop), f"{stop}\n\tpb_timer_stop();", body, count=1)
    if n_s != 1 or n_e != 1:
        raise SystemExit(f"{r.name}: timer injection matched {n_s}/{n_e} sites, expected 1/1")
    removed = [
        "npbparams.hpp replaced by the dataset guard (NPB's own class parameters)",
        "the compile-date and compiler-version strings c_print_results echoes",
        f"the benchmark's main renamed to npb_main; its output ({r.note}) goes to stderr",
    ]
    hoisted = ""
    for decl, keep, declare in r.npb_hoist:
        if decl not in body:
            raise SystemExit(f"{r.name}: declaration to hoist not found: {decl!r}")
        body = body.replace(decl, keep, 1)
        hoisted += declare + "\n"
        removed.append(f"hoisted a result variable to file scope so the digest can read it: "
                       f"{decl.strip()} (declaration only)")
    inc = '#include "npbparams.hpp"'
    if body.count(inc) != 1:
        raise SystemExit(f"{r.name}: expected one `{inc}`")
    body = body.replace(inc, inc + '\n#include "../pb_harness.hpp"\n' + hoisted, 1)
    driver = f"""

/* ---- packaged by agent/tools/prepare_apps.py: driver and digest ---------------------
   The benchmark above runs unchanged and checks its own answer against NPB's reference
   values. Its printing — banner, iteration numbers, c_print_results — goes to stderr, so
   stdout carries the digest alone: the verification verdict, and {r.npb_digest_note}.
   The input cannot be perturbed: NPB compares against fixed reference values, so a
   perturbed input would fail its own verification. argv is passed through untouched. */
#include <unistd.h>

int main(int argc, char** argv)
{{
  fflush(stdout);
  int saved = dup(1);
  dup2(2, 1);                 /* the benchmark's own output -> stderr */
  int rc = npb_main(argc, argv);
  fflush(stdout);
  dup2(saved, 1);             /* stdout back, for the digest */
  close(saved);
{r.npb_digest_body}  pb_report();
  return rc;
}}
"""
    files: Dict[str, str] = {
        f"{upper}/{bench.name}": body + driver,
        f"{upper}/npbparams.hpp": ("/* Generated by agent/tools/prepare_apps.py: NPB's class parameters as a "
                                   "dataset guard (-D<SIZE>_DATASET), in place of the shipped file. */\n"
                                   + _guard(r.sizes)),
        "pb_harness.hpp": _NPB_HARNESS_HPP,
        "pb_harness.cpp": ('#include "pb_harness.hpp"\n'
                           + re.sub(r"^static (void|double) (pb_\w+\()", r"\1 \2", _PRELUDE, flags=re.M)),
    }
    for name in _NPB_COMMON:
        files[f"common/{name}.cpp"] = (common / f"{name}.cpp").read_text()
    for hdr in ("npb-CPP.hpp", "wtime.hpp"):
        files[f"common/{hdr}"] = (common / hdr).read_text()
    return files, removed


def _npb(name: str, cls_sizes: Dict[str, Dict[str, str]], timer: Tuple[str, str],
         digest_body: str, digest_note: str, note: str,
         hoist: Tuple[Tuple[str, str, str], ...] = ()) -> Recipe:
    upper = name.upper()
    sizes = {}
    for size, cls in zip(SIZES, ("S", "W", "A", "B")):
        if cls in cls_sizes:
            sizes[size] = dict(cls_sizes[cls], **_NPB_FIXED)
        elif name == "is":
            sizes[size] = dict({"CLASS": f"'{cls}'"}, **_NPB_FIXED)
    return Recipe(
        name=name, suite="npb", category="nas-parallel-benchmarks",
        source=NPB_ROOT / upper / "NPB-SER" / upper / f"{name}.cpp",
        language="cpp", sizes=sizes,
        original_args={s: [] for s in sizes},
        # NPB-SER uses no OpenMP (checked: no omp include or pragma in the benchmark or
        # common/); the -fopenmp the earlier recipe passed only failed on a machine whose
        # default clang++ has no libomp on its link path.
        original_build=[],
        deterministic=_npb_deterministic,
        assemble=_npb_assemble,
        # `main` is excluded (D4): T0.6 found no loop pattern of DiscoPoP's inside NPB's main
        # that is not on the packaging's own code; `npb_main` (the benchmark's driver) stays.
        exclude_functions=["pb_emit", "pb_report", "pb_seed", "pb_uniform",
                           "pb_timer_start", "pb_timer_stop", "c_print_results",
                           "timer_start", "timer_stop", "timer_read", "timer_clear",
                           "wtime", "elapsed_time", "randlc", "vranlc", "main"],
        # An NPB benchmark is not one translation unit: it links the four common sources and
        # includes npbparams.hpp from its own directory.
        original_sources=lambda rr: [str(rr.source.parent.parent / "common" / f"{n}.cpp")
                                     for n in _NPB_COMMON],
        original_includes=lambda rr: [str(rr.source.parent),
                                      str(rr.source.parent.parent / "common")],
        note=note, perturbable=False, npb_timer=timer, npb_hoist=hoist,
        npb_digest_body=digest_body, npb_digest_note=digest_note,
        assemble_project=_npb_assemble_project,
        project_units=[f"{upper}/{name}.cpp", "pb_harness.cpp"]
                      + [f"common/{n}.cpp" for n in _NPB_COMMON],
        project_include_dirs=[upper, "common"],
    )


# The dump carries the VERDICT, which is the only thing the original also prints; the result
# values go to the digest. Comparing the original's verdict against the packaged one is then
# a real comparison, and a rewrite still cannot change the norms unnoticed.
_VERDICT = "#ifdef PB_FULL_DUMP\n  pb_emit((double)({}));\n#else\n{}#endif\n"

IS = _npb(
    "is",
    {},  # `is` derives its sizes from CLASS alone
    ("timer_start( T_BENCHMARKING );", "timer_stop( T_BENCHMARKING );"),
    _VERDICT.format(
        "passed_verification == 5*MAX_ITERATIONS + 1",
        "  pb_emit((double)passed_verification);\n"
        "  for (int i = 0; i < TEST_ARRAY_SIZE; i++) pb_emit((double)partial_verify_vals[i]);\n"),
    "the partial verification values",
    note="integer bucket sort; the ranking loop is the timed region",
)

MG = _npb(
    "mg", _MG_CLASS,
    ("timer_start(T_BENCH);", "timer_stop(T_BENCH);"),
    _VERDICT.format("verified", "  pb_emit(rnm2);\n"),
    "the residual norm rnm2 the verification compares",
    note="multigrid V-cycles; the residual norm is the verified result",
    hoist=(("double rnm2, rnmu, epsilon;", "double rnmu, epsilon;", "static double rnm2;"),
           ("boolean verified;", "", "static boolean verified;")),
)

LU = _npb(
    "lu", _LU_CLASS,
    ("timer_start(1);", "timer_stop(1);"),
    _VERDICT.format("verified",
                    "  for (int i = 0; i < 5; i++) pb_emit(rsdnm[i]);\n"
                    "  for (int i = 0; i < 5; i++) pb_emit(errnm[i]);\n"
                    "  pb_emit(frc);\n"),
    "the residual and error norms and the surface integral",
    note="SSOR solver; rsdnm, errnm and frc are already file scope",
    hoist=(("boolean verified;", "", "static boolean verified;"),),
)


# ---------------------------------------------------------------------------
# Rodinia hotspot — transient thermal simulation on a grid
# ---------------------------------------------------------------------------
# The only application whose input is a FILE: the original takes a temperature grid and a
# power grid (one value per line) and writes its result to a third file. The harness passes
# no arguments, so the packaged version generates both grids in-process — a change of DATA,
# not of computation. To keep the comparison honest the packaged source can write the grids
# it generated (-DPB_EMIT_INPUT) in the original's own format, and the validator feeds those
# very files to the original: one generator, two programs, no duplicated arithmetic.
#
# The generated values carry three decimals (323.000-324.999 and 0.000-0.299), so the text
# the original parses and the value the packaged program holds are the same float — at more
# decimals the two would differ in the last bits and the comparison would fail on formatting
# rather than on the computation.

_HS_OPENMP_BLOCK = re.compile(
    r"^[ \t]*#[ \t]*ifdef[ \t]+OMP_OFFLOAD\b.*?^[ \t]*#[ \t]*endif.*?$\n", re.M | re.S)


def _hotspot_deterministic(out: str) -> str:
    """The original's output file: `<index>\\t<value>` per line; the values are the result."""
    return "\n".join(line.split("\t")[1] for line in out.splitlines() if "\t" in line)


def _hotspot_assemble(r: Recipe) -> Tuple[str, List[str]]:
    src = r.source
    constants = _lines(src, 17, 48)                      # defines, FLOAT, chip parameters
    kernel = _lines(src, 54, 149) + _lines(src, 159, 209)  # single_iteration, compute_tran_temp
    kernel, n_omp = _HS_OPENMP_BLOCK.subn("", kernel)
    # single_iteration sets the thread count for a `#pragma omp parallel for` that this
    # serial file has disabled, so the call is runtime plumbing rather than computation and
    # goes with omp.h. Its declaration lives in the copied constants and goes with it.
    kernel, n_set = re.subn(r"^[ \t]*omp_set_num_threads\s*\([^)]*\)\s*;\s*\n", "", kernel, flags=re.M)
    constants = re.sub(r"^int num_omp_threads;\s*\n", "", constants, flags=re.M)
    removed = [
        f"{n_omp} disabled #ifdef OMP_OFFLOAD block(s) in the kernel (§1a)",
        f"{n_set} omp_set_num_threads() call(s) and the num_omp_threads declaration — the "
        "pragma they configure is disabled in the serial file",
        "omp.h and the thread-count argument",
        "get_time()/gettimeofday timing and the 'Start computing' line",
        "read_input() and writeoutput(): the grids are generated in-process and the result "
        "becomes the digest, because the harness passes no arguments",
    ]
    driver = """
/* ---- hotspot, packaged -----------------------------------------------------
   Sizes come from the dataset guard; the temperature and power grids are generated here
   instead of read from files (the harness passes no arguments). -DPB_EMIT_INPUT writes the
   generated grids in the original's format so the validator can give the original exactly
   the same input. compute_tran_temp is the timed region. */
void single_iteration(FLOAT *result, FLOAT *temp, FLOAT *power, int row, int col,
                      FLOAT Cap_1, FLOAT Rx_1, FLOAT Ry_1, FLOAT Rz_1, FLOAT step);
void compute_tran_temp(FLOAT *result, int num_iterations, FLOAT *temp, FLOAT *power,
                       int row, int col);

/* Three decimals, so the file the original reads and the value held here are one float. */
static void hs_generate(FLOAT* temp, FLOAT* power, int n)
{
  for (int i = 0; i < n; i++)
    {
      temp[i]  = (FLOAT)((323000 + (int)(pb_uniform() * 2000.0)) / 1000.0);
      power[i] = (FLOAT)((int)(pb_uniform() * 300.0) / 1000.0);
    }
}

int main(int argc, char** argv)
{
  int grid_rows = HS_ROWS, grid_cols = HS_COLS, sim_time = HS_ITERATIONS;
  int n = grid_rows * grid_cols;
  FLOAT* temp = (FLOAT*)calloc(n, sizeof(FLOAT));
  FLOAT* power = (FLOAT*)calloc(n, sizeof(FLOAT));
  FLOAT* result = (FLOAT*)calloc(n, sizeof(FLOAT));
  if (!temp || !power || !result) { fprintf(stderr, "cannot allocate\\n"); return 1; }

  if (argc > 1) pb_seed(argv[1]);
  hs_generate(temp, power, n);

#ifdef PB_EMIT_INPUT
  /* The original's format: one value per line, read back with %f. */
  FILE* ft = fopen("temp.in", "w");
  FILE* fp = fopen("power.in", "w");
  if (!ft || !fp) { fprintf(stderr, "cannot write the generated input\\n"); return 1; }
  for (int i = 0; i < n; i++) fprintf(ft, "%.6f\\n", (double)temp[i]);
  for (int i = 0; i < n; i++) fprintf(fp, "%.6f\\n", (double)power[i]);
  fclose(ft);
  fclose(fp);
  return 0;
#else
  pb_timer_start();
  compute_tran_temp(result, sim_time, temp, power, grid_rows, grid_cols);
  pb_timer_stop();

  /* compute_tran_temp swaps two local pointers each iteration, so the answer ends in one
     buffer or the other depending on the parity. This is the original's own expression from
     its writeoutput call — `result` for an odd count, `temp` for an even one. Reversing it
     still agrees at 10 iterations by luck and differs in 1,241 of 262,144 cells at 100. */
  FLOAT* answer = (1 & sim_time) ? result : temp;
  for (int i = 0; i < n; i++) pb_emit((double)answer[i]);
  pb_report();

  free(temp);
  free(power);
  free(result);
  return 0;
#endif
}
"""
    return _PRELUDE + _guard(r.sizes) + constants + kernel + driver, removed


HOTSPOT = Recipe(
    name="hotspot",
    suite="rodinia-3.1",
    category="thermal-simulation",
    source=BENCHMARKS / "rodinia_3.1" / "serial" / "hotspot" / "hotspot_serial.cpp",
    language="cpp",
    sizes={
        "MINI": {"HS_ROWS": "64", "HS_COLS": "64", "HS_ITERATIONS": "10"},
        "SMALL": {"HS_ROWS": "512", "HS_COLS": "512", "HS_ITERATIONS": "100"},
        "STANDARD": {"HS_ROWS": "1024", "HS_COLS": "1024", "HS_ITERATIONS": "500"},
        "LARGE": {"HS_ROWS": "2048", "HS_COLS": "2048", "HS_ITERATIONS": "1000"},
        "EXTRALARGE": {"HS_ROWS": "4096", "HS_COLS": "4096", "HS_ITERATIONS": "2000"},
    },
    original_args={
        "MINI": ["64", "64", "10", "1", "temp.in", "power.in", "out.txt"],
        "SMALL": ["512", "512", "100", "1", "temp.in", "power.in", "out.txt"],
        "STANDARD": ["1024", "1024", "500", "1", "temp.in", "power.in", "out.txt"],
        "LARGE": ["2048", "2048", "1000", "1", "temp.in", "power.in", "out.txt"],
        "EXTRALARGE": ["4096", "4096", "2000", "1", "temp.in", "power.in", "out.txt"],
    },
    original_build=["-fopenmp"],
    deterministic=_hotspot_deterministic,
    assemble=_hotspot_assemble,
    # `main` excluded (D4): T0.6 found no loop pattern of DiscoPoP's inside hotspot's main
    # beyond the packaging's own loops.
    exclude_functions=["hs_generate", "pb_emit", "pb_report", "pb_seed", "pb_uniform",
                       "pb_timer_start", "pb_timer_stop", "main"],
    note=("the grids are generated in-process, not read from files, because the harness "
          "passes no arguments; -DPB_EMIT_INPUT writes them in the original's format so the "
          "validator gives the original the same input"),
    result_file="out.txt",
    emits_input=True,
    # writeoutput prints "%d\t%g\n": six significant digits. The dump prints the same way, so
    # both sides are one formatter's output and nothing is rounded twice.
    dump_format="%g\\n",
)


# ---------------------------------------------------------------------------
# LLNL LULESH 2.0 — the application-scale program (E6), serial path
# ---------------------------------------------------------------------------
# Source: benchmarks/LULESH/LULESH_SERIAL_PATH, which agent/tools/lulesh_serial_path.py derives
# from LLNL's release by removing the preprocessor-dead OpenMP code and folding every
# `if (numthreads > 1)` to its serial branch (validated there: the deterministic output lines
# are identical to the original's). What THIS recipe adds is the harness contract, by the same
# rules as the NPB recipes — the computation is never touched:
#   * `main` becomes `lulesh_main`; the problem size (-s) and the iteration cap (-i) come from
#     the dataset guard, and the command-line parser is not called (argv carries the seed only);
#   * the timer goes where LULESH takes its own (`gettimeofday` around the time-step loop);
#   * the Domain is handed to the driver instead of deleted, so the digest can read it;
#   * LULESH's own report (with its elapsed time and FOM) goes to stderr, stdout is the digest.
# The seeded input scales the deposited energy AND moves every node that lies on no boundary
# plane by at most 0.1 % of a cell. The second part matters: the Sedov problem is symmetric in
# x, y and z, so a rewrite that mixes two of the three up could otherwise leave every value
# unchanged. Boundary planes keep their coordinates, so the symmetry conditions still hold.

LULESH_DIR = BENCHMARKS / "LULESH" / "LULESH_SERIAL_PATH"
_LULESH_OTHER_UNITS = ["lulesh-init.cc", "lulesh-util.cc", "lulesh-viz.cc", "lulesh-comm.cc"]
_LULESH_SIZES = {          # -s (elements per edge), -i (iteration cap)
    "MINI": ("5", "10"), "SMALL": ("8", "20"), "STANDARD": ("15", "50"),
    "LARGE": ("30", "100"), "EXTRALARGE": ("45", "200"),
}


def _lulesh_deterministic(out: str) -> str:
    """Iteration count, final origin energy and the three symmetry differences."""
    vals = []
    for label in ("Iteration count", "Final Origin Energy", "MaxAbsDiff", "TotalAbsDiff", "MaxRelDiff"):
        m = re.search(re.escape(label) + r"\s*=\s*([-+0-9.eE]+)", out)
        if not m:
            return ""
        vals.append(m.group(1))
    return "\n".join(vals)


def _lulesh_assemble_project(r: Recipe, src_dir: Optional[Path] = None) -> Tuple[Dict[str, str], List[str]]:
    """`src_dir` = LLNL's unmodified release gives the EXPERT REFERENCE in package form: the very
    same edits applied to LLNL's own OpenMP program, so the harness judges it like any trial."""
    src_dir = src_dir or LULESH_DIR
    body = (src_dir / "lulesh.cc").read_text()

    def once(old: str, new: str, what: str) -> None:
        nonlocal body
        if body.count(old) != 1:
            raise SystemExit(f"lulesh: expected exactly one `{old.strip()}` ({what}), found {body.count(old)}")
        body = body.replace(old, new, 1)

    once('#include "lulesh.h"',
         '#include "lulesh.h"\n#include "pb_harness.hpp"\n'
         "/* packaging: the Domain outlives lulesh_main so that the driver can digest it, and the\n"
         "   seeded input is applied right after the mesh is built (both defined at the end). */\n"
         "static Domain* pb_lulesh_domain = 0;\n"
         "static void pb_lulesh_perturb(Domain& domain, int argc, char** argv);\n", "include")
    once("int main(int argc, char *argv[])", "int lulesh_main(int argc, char *argv[])", "main")
    once("   opts.its = 9999999;", "   opts.its = PB_ITS;", "iteration cap")
    once("   opts.nx  = 30;", "   opts.nx  = PB_NX;", "problem size")
    once("   ParseCommandLineOptions(argc, argv, myRank, &opts);",
         "   /* packaging: sizes come from the dataset guard; argv carries only the harness's seed */",
         "command-line parser")
    once("                       side, opts.numReg, opts.balance, opts.cost) ;\n",
         "                       side, opts.numReg, opts.balance, opts.cost) ;\n"
         "   pb_lulesh_perturb(*locDom, argc, argv);\n", "after the mesh is built")
    once("   gettimeofday(&start, NULL) ;", "   pb_timer_start();\n   gettimeofday(&start, NULL) ;", "timer start")
    once("   gettimeofday(&end, NULL) ;", "   gettimeofday(&end, NULL) ;\n   pb_timer_stop();", "timer stop")
    once("   delete locDom; ", "   pb_lulesh_domain = locDom;   /* packaging: deleted by the driver, after the digest */",
         "domain lifetime")
    driver = r"""

/* ---- packaged by agent/tools/prepare_apps.py: seeded input, driver and digest -----------
   The program above runs unchanged. Its own report — with the elapsed time and the figure of
   merit, which differ from run to run — goes to stderr; stdout carries the digest alone. */
#include <unistd.h>

static void pb_lulesh_perturb(Domain& domain, int argc, char** argv)
{
   if (argc < 2) return;
   pb_seed(argv[1]);
   /* a change of DATA, not of computation */
   domain.e(0) *= (Real_t(1.0) + Real_t(0.05) * Real_t(pb_uniform()));
   const Index_t edgeNodes = domain.sizeX() + 1;
   const Real_t jitter = Real_t(1.0e-3) * Real_t(1.125) / Real_t(domain.sizeX());
   for (Index_t plane = 1; plane < edgeNodes - 1; ++plane)
      for (Index_t row = 1; row < edgeNodes - 1; ++row)
         for (Index_t col = 1; col < edgeNodes - 1; ++col) {
            const Index_t n = plane * edgeNodes * edgeNodes + row * edgeNodes + col;
            domain.x(n) += jitter * Real_t(pb_uniform() - 0.5);
            domain.y(n) += jitter * Real_t(pb_uniform() - 0.5);
            domain.z(n) += jitter * Real_t(pb_uniform() - 0.5);
         }
}

int main(int argc, char** argv)
{
   fflush(stdout);
   int saved = dup(1);
   dup2(2, 1);                       /* LULESH's own output -> stderr */
   int rc = lulesh_main(argc, argv);
   std::cout.flush();
   fflush(stdout);
   dup2(saved, 1);                   /* stdout back, for the digest */
   close(saved);
   Domain& domain = *pb_lulesh_domain;
#ifdef PB_ORIGINAL_REPORT
   /* For the packaging validator ONLY: exactly what the original prints that is deterministic —
      the iteration count, the final origin energy and the three symmetry differences
      (VerifyAndWriteFinalOutput). The three differences are NOT results: they subtract
      energies that are mathematically equal, so on the symmetric input they are rounding
      residue (1e-11 against energies of 1e+5), and a correct parallel version that adds in
      another order moves them by tens of percent — LLNL's own OpenMP release differs from
      its serial path by 25 % there while every energy agrees to 2e-16. They therefore stay
      out of what the harness compares (below). */
   const Index_t nx = domain.sizeX();
   Real_t maxAbsDiff = Real_t(0.0), totalAbsDiff = Real_t(0.0), maxRelDiff = Real_t(0.0);
   for (Index_t j = 0; j < nx; ++j)
      for (Index_t k = j + 1; k < nx; ++k) {
         Real_t absDiff = FABS(domain.e(j * nx + k) - domain.e(k * nx + j));
         totalAbsDiff += absDiff;
         if (maxAbsDiff < absDiff) maxAbsDiff = absDiff;
         Real_t relDiff = absDiff / domain.e(k * nx + j);
         if (maxRelDiff < relDiff) maxRelDiff = relDiff;
      }
   pb_emit((double)domain.cycle());
   pb_emit((double)domain.e(0));
   pb_emit((double)maxAbsDiff);
   pb_emit((double)totalAbsDiff);
   pb_emit((double)maxRelDiff);
#else
   /* The program's RESULT, for the digest and for the full dump alike: the whole final state —
      every element's energy, pressure and relative volume, every node's position and velocity
      (the final origin energy LLNL reports is the first energy). */
   pb_emit((double)domain.cycle());
   for (Index_t i = 0; i < domain.numElem(); ++i) {
      pb_emit((double)domain.e(i)); pb_emit((double)domain.p(i)); pb_emit((double)domain.v(i));
   }
   for (Index_t i = 0; i < domain.numNode(); ++i) {
      pb_emit((double)domain.x(i));  pb_emit((double)domain.y(i));  pb_emit((double)domain.z(i));
      pb_emit((double)domain.xd(i)); pb_emit((double)domain.yd(i)); pb_emit((double)domain.zd(i));
   }
#endif
   pb_report();
   delete pb_lulesh_domain;
   return rc;
}
"""
    files: Dict[str, str] = {
        "lulesh.cc": body + driver,
        "pb_sizes.h": ("/* Generated by agent/tools/prepare_apps.py: LULESH's -s (elements per edge) and -i\n"
                       "   (iteration cap) as a dataset guard (-D<SIZE>_DATASET). */\n" + _guard(r.sizes)),
        "pb_harness.hpp": _NPB_HARNESS_HPP.replace("#define PB_HARNESS_HPP\n",
                                                   '#define PB_HARNESS_HPP\n#include "pb_sizes.h"\n', 1),
        "pb_harness.cpp": ('#include "pb_harness.hpp"\n'
                           + re.sub(r"^static (void|double) (pb_\w+\()", r"\1 \2", _PRELUDE, flags=re.M)),
        "lulesh.h": (src_dir / "lulesh.h").read_text(),
    }
    for name in _LULESH_OTHER_UNITS:
        files[name] = (src_dir / name).read_text()
    if (src_dir / "lulesh_tuple.h").exists() and "lulesh_tuple.h" in "".join(files.values()):
        files["lulesh_tuple.h"] = (src_dir / "lulesh_tuple.h").read_text()
    removed = [
        "main renamed to lulesh_main; its report (elapsed time, FOM, progress) goes to stderr",
        "the command-line parser is not called: -s and -i come from the dataset guard",
        "the Domain is deleted by the driver after the digest instead of at the end of lulesh_main",
        "OpenMP: none left to remove — the source is the validated serial path "
        "(benchmarks/LULESH/LULESH_SERIAL_PATH/SERIAL_PATH.json lists what that step removed)",
    ]
    return files, removed


LULESH = Recipe(
    name="lulesh", suite="llnl", category="hydrodynamics-proxy-application",
    source=LULESH_DIR / "lulesh.cc", language="cpp",
    sizes={size: {"PB_NX": nx, "PB_ITS": its} for size, (nx, its) in _LULESH_SIZES.items()},
    original_args={size: ["-s", nx, "-i", its] for size, (nx, its) in _LULESH_SIZES.items()},
    original_build=["-DUSE_MPI=0"],
    deterministic=_lulesh_deterministic,
    assemble=lambda r: (_ for _ in ()).throw(SystemExit("lulesh is packaged as a project only (--layout project)")),
    # Out of scope for the agent: the packaging's own code, LULESH's I/O and option handling,
    # and the one-time mesh and region SETUP (the constructor and what it calls) — like
    # `init_array` in a kernel. `lulesh_main` stays in: it holds the time-step loop.
    exclude_functions=["main", "pb_lulesh_perturb", "pb_emit", "pb_report", "pb_seed", "pb_uniform",
                       "pb_timer_start", "pb_timer_stop",
                       "ParseCommandLineOptions", "PrintCommandLineOptions", "ParseError", "StrToInt",
                       "VerifyAndWriteFinalOutput", "DumpToVisit", "DumpDomainToVisit", "DumpMultiblockObjects",
                       "InitMeshDecomp", "Domain", "BuildMesh", "SetupCommBuffers",
                       "CreateRegionIndexSets", "SetupSymmetryPlanes", "SetupElementConnectivities",
                       "SetupBoundaryConditions", "AllocateElemPersistent", "AllocateNodePersistent",
                       "AllocateGradients", "DeallocateGradients", "AllocateStrains", "DeallocateStrains"],
    note="Sedov blast on an unstructured hex mesh; the time-step loop is the timed region",
    # LULESH prints `std::scientific << std::setprecision(6)`: seven significant digits. The
    # validator rounds both sides to six, and re-rounding an already rounded number can land on
    # the other side of a half (3.245955e+04 -> 32459.5, but the exact 32459.5524 -> 32459.6),
    # so the dump prints in the original's own format and the two texts agree digit for digit.
    dump_format="%.6e\\n",
    validate_macros=["PB_ORIGINAL_REPORT"],
    original_sources=lambda rr: [str(LULESH_DIR / n) for n in _LULESH_OTHER_UNITS],
    original_includes=lambda rr: [str(LULESH_DIR)],
    assemble_project=_lulesh_assemble_project,
    project_units=["lulesh.cc", "pb_harness.cpp", *_LULESH_OTHER_UNITS],
    project_include_dirs=["."],
    project_cflags=["-DUSE_MPI=0"],
    reference_dir=BENCHMARKS / "LULESH" / "LULESH_LLNL_OMP",
)


RECIPES: Dict[str, Recipe] = {r.name: r for r in (MD, PATHFINDER, NW, IS, MG, LU, HOTSPOT, LULESH)}


# ---------------------------------------------------------------------------
# Build, run, validate
# ---------------------------------------------------------------------------

def _find(names: List[str]) -> Optional[str]:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def _sysroot() -> List[str]:
    """macOS needs an explicit SDK for a Homebrew clang; on Linux this is empty."""
    if sys.platform != "darwin":
        return []
    r = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True)
    path = r.stdout.strip()
    flags = ["-isysroot", path] if r.returncode == 0 and path else []
    # Homebrew's libomp is keg-only: the ORIGINALS of md, nw and hotspot include <omp.h>,
    # which a Homebrew clang does not find on its own.
    libomp = Path("/usr/local/opt/libomp")
    if libomp.exists():
        flags += [f"-I{libomp / 'include'}", f"-L{libomp / 'lib'}"]
    return flags


def _build(cmd: List[str], cwd: Path) -> Optional[str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return None if r.returncode == 0 else r.stderr[-600:]


def _run(binary: Path, cwd: Path, args: Optional[List[str]] = None,
         timeout: int = 900) -> Tuple[int, str, str, float]:
    t0 = time.perf_counter()
    try:
        r = subprocess.run([str(binary), *(args or [])], cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout", time.perf_counter() - t0
    return r.returncode, r.stdout, r.stderr, time.perf_counter() - t0


def validate(r: Recipe, packaged: Path, work: Path, cxx: str,
             sizes: List[str]) -> Dict[str, Any]:
    """The original's deterministic output must equal the packaged full dump."""
    row: Dict[str, Any] = {"app": r.name}
    for size in sizes:
        orig_bin, dump_bin, digest_bin = work / f"o_{size}", work / f"d_{size}", work / f"g_{size}"
        if r.emits_input:
            # The original reads files the packaged source generates; write them first, from
            # the packaged generator itself, so both programs see identical input.
            gen_bin = work / f"gen_{size}"
            gen_inputs = ([str(packaged / u) for u in r.project_units]
                          + [f"-I{packaged / d}" for d in r.project_include_dirs]
                          if packaged.is_dir() else [str(packaged)])
            err = _build([cxx, "-O2", f"-D{size}_DATASET", "-DPB_EMIT_INPUT", *_sysroot(),
                          *gen_inputs, "-o", str(gen_bin)], work)
            if err:
                row[size] = f"input generator build failed: {err.strip().splitlines()[-1][:120]}"
                continue
            rc_i, _, err_i, _ = _run(gen_bin, work)
            if rc_i != 0:
                row[size] = f"input generator failed: {err_i.strip()[:120]}"
                continue
        err = _build([cxx, "-O2", *r.original_build, *_sysroot(),
                      *[f"-I{d}" for d in r.original_includes(r)],
                      str(r.source), *r.original_sources(r),
                      "-o", str(orig_bin), "-lm"], work)
        if err:
            row[size] = f"original build failed: {err.strip().splitlines()[-1][:120]}"
            continue
        if packaged.is_dir():
            inputs = ([str(packaged / u) for u in r.project_units]
                      + [f"-I{packaged / d}" for d in r.project_include_dirs]
                      + list(r.project_cflags))
        else:
            inputs = [str(packaged)]
        err = _build([cxx, "-O2", f"-D{size}_DATASET", "-DPB_FULL_DUMP",
                      *[f"-D{m}" for m in r.validate_macros],
                      f'-DPB_DUMP_FORMAT="{r.dump_format}"', *_sysroot(),
                      *inputs, "-o", str(dump_bin)], work)
        err = err or _build([cxx, "-O2", f"-D{size}_DATASET", *_sysroot(), *inputs,
                             "-o", str(digest_bin)], work)
        if err:
            row[size] = f"packaged build failed: {err.strip().splitlines()[-1][:120]}"
            continue
        rc_o, out_o, _, _ = _run(orig_bin, work, r.original_args[size])
        if r.result_file:
            produced = work / r.result_file
            out_o = produced.read_text() if produced.exists() else ""
            rc_o = rc_o if produced.exists() else 1
        rc_d, out_d, _, _ = _run(dump_bin, work)
        rc_g, out_g, err_g, t_g = _run(digest_bin, work)
        # Compared at the ORIGINAL's own precision. md's stream prints 6 significant digits
        # (1221.16, 1.5278e-08) while the dump prints %.17g, so the packaged values are
        # rounded to 6 before comparing — anything finer would fail on the original's own
        # rounding rather than on a difference in the computation.
        def _values(text: str, whose: str) -> Optional[str]:
            """Every token as a number, or None with a note: a dump is numbers, nothing else."""
            out = []
            for v in text.split():
                try:
                    out.append(f"{float(v):.6g}")
                except ValueError:
                    row[size] = f"{whose} is not numeric: {v!r} — prose left in the output?"
                    return None
            return "\n".join(out)

        want = _values(r.deterministic(out_o), "the original's deterministic output")
        got = _values(out_d, "the packaged dump")
        if want is None or got is None:
            continue
        result: Dict[str, Any] = {
            "original_ok": rc_o == 0,
            "dump_identical": rc_d == 0 and len(want) > 0 and want == got,
            "dump_values": len(got.split()),
            "digest_ok": rc_g == 0 and out_g.count("\n") == 3 and out_g.startswith("pb_values "),
            "timed_region": "DP_TIMED_REGION_SECONDS" in err_g,
            "digest_run_s": round(t_g, 3),
        }
        if r.perturbable:
            rc_s1, out_s1, _, _ = _run(digest_bin, work, ["7"])
            rc_s2, out_s2, _, _ = _run(digest_bin, work, ["7"])
            result.update({
                "perturb_deterministic": rc_s1 == 0 and rc_s2 == 0 and out_s1 == out_s2,
                "perturb_changes_output": out_s1 != out_g,
                "perturb_finite": not re.search(r"nan|inf", out_s1, re.I),
            })
        else:
            # Not a pass and not a failure: this benchmark verifies against fixed reference
            # values, so there is no input it may be given that it would still accept.
            result["perturbation"] = "n/a — verifies against NPB's reference values"
        row[size] = result
    return row


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("apps", nargs="*", help=f"default: all ({', '.join(RECIPES)})")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--size", default="SMALL", help="dataset the agent profiles at")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--references", action="store_true",
                   help="also write each benchmark's expert version in package form under "
                        "agent/reference_solutions/ (recipes that name a reference_dir)")
    p.add_argument("--validate-sizes", default="MINI,SMALL")
    p.add_argument("--cxx", default=None)
    p.add_argument("--layout", choices=["project", "single"], default="project",
                   help=("project (default since D6): a benchmark that is several files stays "
                         "several files; single: the earlier one-file merge, for comparison studies. "
                         "A program that is one file to begin with is the same in both."))
    a = p.parse_args()
    a.out = a.out.resolve()

    names = a.apps or list(RECIPES)
    unknown = [n for n in names if n not in RECIPES]
    if unknown:
        sys.exit(f"unknown app(s): {', '.join(unknown)} — known: {', '.join(RECIPES)}")
    cxx = a.cxx or _find(["clang++-20", "clang++", "g++"])
    if a.validate and not cxx:
        sys.exit("no C++ compiler found for --validate (pass --cxx)")

    rows = []
    for name in names:
        r = RECIPES[name]
        if not r.source.exists():
            sys.exit(f"{r.name}: original not found at {r.source}")
        out_dir = a.out / r.suite / r.name
        if out_dir.exists():
            shutil.rmtree(out_dir)                 # never mix the two layouts in one directory
        out_dir.mkdir(parents=True, exist_ok=True)
        meta: Dict[str, Any] = {
            "suite": r.suite, "kernel": r.name,
            "source": str(r.source.relative_to(HARNESS_ROOT)),
            "category": r.category, "language": r.language,
            "exclude_functions": r.exclude_functions,
            "agent_dataset": a.size, "generator_version": GENERATOR_VERSION,
            "sizes": r.sizes, "note": r.note,
            "inputs_sha256": hashlib.sha256(r.source.read_bytes()).hexdigest(),
        }
        if a.layout == "project" and r.assemble_project is not None:
            files, removed = r.assemble_project(r)
            for rel, text in files.items():
                (out_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                (out_dir / rel).write_text(text)
            packaged = out_dir
            main_unit = r.project_units[0]
            meta.update({"file": main_unit, "layout": "project",
                         "project": {"units": r.project_units,
                                     "include_dirs": r.project_include_dirs,
                                     **({"cflags": r.project_cflags} if r.project_cflags else {})}})
            digest_of = "".join(files[k] for k in sorted(files)).encode()
            what = f"{len(files)} files, {main_unit}"
        else:
            text, removed = r.assemble(r)
            packaged = out_dir / f"{r.name}.{'c' if r.language == 'c' else 'cpp'}"
            packaged.write_text(text)
            meta.update({"file": packaged.name, "layout": "single"})
            digest_of = packaged.read_bytes()
            what = f"{packaged.name}, {len(text.splitlines())} lines"
        if a.references and r.reference_dir is not None and r.assemble_project is not None:
            ref_files, _ = r.assemble_project(r, r.reference_dir)          # type: ignore[call-arg]
            ref_out = AGENT_DIR / "reference_solutions" / r.suite / r.name
            shutil.rmtree(ref_out, ignore_errors=True)
            for rel, text in ref_files.items():
                (ref_out / rel).parent.mkdir(parents=True, exist_ok=True)
                (ref_out / rel).write_text(text)
            print(f"    expert reference ({r.reference_dir.name}, same edits) -> {ref_out.relative_to(HARNESS_ROOT)}")
        meta["removed"] = removed
        meta["output_sha256"] = hashlib.sha256(digest_of).hexdigest()
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"{r.name:14s} -> {out_dir.relative_to(a.out)}  ({what})")
        for line in removed:
            print(f"    removed: {line}")
        if a.validate:
            assert cxx is not None
            with tempfile.TemporaryDirectory(prefix=f"apps_{r.name}_") as tmp:
                rows.append(validate(r, packaged, Path(tmp), cxx,
                                     [s for s in a.validate_sizes.split(",") if s]))
                print("    " + json.dumps(rows[-1], indent=None)[:400])
    if rows:
        (a.out / "apps_validation.json").write_text(json.dumps(rows, indent=2) + "\n")
        print(f"\nvalidation -> {a.out / 'apps_validation.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
