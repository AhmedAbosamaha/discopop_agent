#!/usr/bin/env python3
"""Restructuring benchmarks from TSVC-2 — loops whose parallelization REQUIRES a code change.

Why this suite exists (THESIS_EXPERIMENTS.md §5k). The thesis's central claim is that
restructuring parallelizes what DiscoPoP alone cannot. PolyBench cannot test it: its kernels
are parallel as written (pilot4/E10: 21 of 25 FASTER results were pragmas on loops DiscoPoP
also reports as Do-All; only floyd-warshall was ever restructured). TSVC — the Test Suite
for Vectorizing Compilers (Callahan, Dongarra, Levine 1988; C version Maleki et al. 2011;
TSVC-2, UoB-HPC) — is the recognised collection of loops classified by the TRANSFORMATION a
tool must apply before the loop can run in parallel: statement reordering, loop
distribution, node splitting, scalar expansion, index-set splitting, peeling, induction
variable substitution, search loops, packing — and genuine recurrences, where the right
answer is to decline. LLM-Vectorizer (2024) and VecTrans (2025) evaluate LLM loop
restructuring on it.

What is taken and what is not. The LOOP BODY of every benchmark is copied verbatim from
`benchmarks/TSVC_2/src/tsvc.c` (commit in PROVENANCE below; University of Illinois licence,
kept in that directory). Everything around it is this harness's own packaging, the same as
for every other benchmark: `double` data (TSVC's `float` cannot meet the oracle's 1e-9
tolerance once a reduction is reordered), heap arrays with dataset sizes, O(1) periodic
initial values (TSVC's 1/(i+1) patterns fall below the tolerance at large N, which would
blind the oracle), a perturbed input, a value digest / full dump, the timed region, and
R DEPENDENT repetitions (`pb_mix` changes a few input elements between repetitions, so a
repetition can neither be skipped nor run out of order — the hole found with the
calibration programs on 18 Sep).

Three classes, each loop labelled before any run:
  restructure  the loop as written carries a dependence; a known transformation removes it.
               An EXPERT REFERENCE solution is kept OUTSIDE the package
               (`agent/reference_solutions/tsvc/`), verified by the same oracle: it proves
               the task solvable and gives the speedup ceiling.
  annotate     parallel as written (the control group): a pragma is all it needs.
  decline      a genuine recurrence: the correct outcome is no parallelization (or an
               order-preserving one that passes every check).

From v4 (D39, 25 Sep 2026) the package holds only the loop; the packaging above lives in a
header per loop under `prepared/_harness/tsvc/`, outside the package — see the v4 note at the
templates below.

Usage:
  python3 agent/tools/prepare_tsvc.py --out agent/prepared/tsvc [--validate] [names...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_calib import SCAFFOLD, _cc, _sysroot  # noqa: E402  (the same packaging code)

AGENT_DIR = Path(__file__).resolve().parent.parent
HARNESS_ROOT = AGENT_DIR.parent
TSVC = HARNESS_ROOT / "benchmarks" / "TSVC_2" / "src" / "tsvc.c"
REFERENCES = AGENT_DIR / "reference_solutions" / "tsvc"
GENERATOR_VERSION = 4

# T0.10 on the server (19 Sep): with R = 8 and 64M elements the serial kernels ran 0.16-0.46 s,
# below the 1 s a timing needs. Additive loops now repeat 48 times; loops whose values grow
# multiplicatively (and the recurrences) keep 8 repetitions and rely on the largest size.
SIZES = {"MINI": "2000", "SMALL": "32000", "STANDARD": "4000000", "LARGE": "32000000",
         "EXTRALARGE": "192000000"}


class Loop:
    def __init__(self, name: str, expected: str, transformation: str, why: str,
                 expert: Optional[str] = None, init_extra: str = "", reps: int = 48,
                 pre: str = "", globals_: str = "") -> None:
        self.name, self.expected, self.transformation, self.why = name, expected, transformation, why
        # `pre`: the argument declarations TSVC passes through `func_args` (set in its main), which
        # the extracted body does not contain; `globals_`: file-scope code the loop needs (TSVC's
        # `f`, the index array).  Neither may say anything about how to parallelize (D36).
        self.pre, self.globals_ = pre, globals_
        self.expert, self.init_extra, self.reps = expert, init_extra, reps


# --------------------------------------------------------------------------------------
# The selection. `expert` is the body of the reference kernel (between the braces); `TMP`
# is a scratch array of LEN_1D doubles the reference may use (allocated once, outside the
# timed loop nest of the ORIGINAL there is none — extra memory is part of the solution).
# --------------------------------------------------------------------------------------
_COPY = "#pragma omp parallel for\n        for (int i = 0; i < LEN_1D; i++) pb_tmp[i] = %s[i];"

LOOPS: List[Loop] = [
    # ---- statement reordering / loop distribution ------------------------------------
    Loop("s211", "restructure", "statement reordering + loop distribution",
         "a[i] needs b[i-1] written by the PREVIOUS iteration, b[i] needs the OLD b[i+1]",
         expert="""    for (int nl = 0; nl < R; nl++) {
        """ + _COPY % "b" + """
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) b[i] = pb_tmp[i + 1] - e[i] * d[i];
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) a[i] = b[i - 1] + c[i] * d[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s212", "restructure", "statement reordering (dependency needing a temporary)",
         "b[i] reads a[i+1] before iteration i+1 scales it: the OLD value",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) b[i] += a[i + 1] * d[i];
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) a[i] *= c[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s1213", "restructure", "statement reordering (dependency needing a temporary)",
         "a[i] needs the NEW b[i-1], b[i] the OLD a[i+1]: a cycle that distribution breaks",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) b[i] = a[i+1]*d[i];
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) a[i] = b[i-1]+c[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- node splitting --------------------------------------------------------------
    Loop("s241", "restructure", "node splitting (preload the old a[i+1])",
         "b[i] reads a[i+1] before it is overwritten: needs a copy of the old values",
         reps=8,
         expert="""    for (int nl = 0; nl < R; nl++) {
        """ + _COPY % "a" + """
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * pb_tmp[i+1] * d[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s243", "restructure", "node splitting (false dependence cycle)",
         "the last statement reads the OLD a[i+1]; a copy breaks the cycle",
         reps=8,
         expert="""    for (int nl = 0; nl < R; nl++) {
        """ + _COPY % "a" + """
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + pb_tmp[i+1] * d[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s244", "restructure", "node splitting (dead store except in the last iteration)",
         "a[i+1] written by iteration i is overwritten by iteration i+1 without being read: "
         "only the last iteration's store survives",
         expert="""    for (int nl = 0; nl < R; nl++) {
        real_t last_old = a[LEN_1D-1];
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + last_old * d[LEN_1D-2];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- scalar expansion / carry-around variables ------------------------------------
    Loop("s252", "restructure", "scalar expansion (t carries the previous iteration's s)",
         "t = s of iteration i-1: substitute b[i-1]*c[i-1]",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t = (i > 0) ? b[i-1] * c[i-1] : (real_t) 0.;
            a[i] = s + t;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s254", "restructure", "carry-around variable (x = b[i-1], wrapping)",
         "x carries b[i-1]; the first iteration uses b[LEN_1D-1]",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            real_t x = (i > 0) ? b[i-1] : b[LEN_1D-1];
            a[i] = (b[i] + x) * (real_t).5;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s255", "restructure", "carry-around variables, two levels",
         "x = b[i-1], y = b[i-2], both wrapping around the array end",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            real_t x = b[(i + LEN_1D - 1) % LEN_1D];
            real_t y = b[(i + LEN_1D - 2) % LEN_1D];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- index-set splitting, peeling -------------------------------------------------
    Loop("s281", "restructure", "index-set splitting (crossing threshold)",
         "the first half reads the OLD upper half, the second half reads the NEW lower half",
         expert="""    for (int nl = 0; nl < R; nl++) {
        int half = (LEN_1D + 1) / 2;
        #pragma omp parallel for
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        #pragma omp parallel for
        for (int i = half; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s291", "restructure", "loop peeling (wrap-around index, one level)",
         "im1 is i-1 except in the first iteration",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i > 0) ? i - 1 : LEN_1D-1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s292", "restructure", "loop peeling (wrap-around index, two levels)",
         "im1 = i-1 and im2 = i-2, wrapping",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i + LEN_1D - 1) % LEN_1D;
            int im2 = (i + LEN_1D - 2) % LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s293", "restructure", "loop peeling (a[i] = a[0] with a[0] written first)",
         "every iteration reads a[0], which the first iteration writes (with its own value)",
         expert="""    for (int nl = 0; nl < R; nl++) {
        real_t a0 = a[0];
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) a[i] = a0;
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- induction variables, reversal ------------------------------------------------
    Loop("s121", "restructure", "induction variable + old-value read (needs a copy)",
         "j = i+1: a[i] reads a[i+1] before it is overwritten",
         expert="""    for (int nl = 0; nl < R; nl++) {
        """ + _COPY % "a" + """
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) a[i] = pb_tmp[i + 1] + b[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s112", "restructure", "loop reversal with an anti-dependence (needs a copy)",
         "running downwards, a[i+1] is written from the OLD a[i]",
         expert="""    for (int nl = 0; nl < R; nl++) {
        """ + _COPY % "a" + """
        #pragma omp parallel for
        for (int i = LEN_1D - 2; i >= 0; i--) a[i+1] = pb_tmp[i] + b[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s127", "restructure", "induction variable with multiple increments",
         "j advances twice per iteration: j = 2i and 2i+1",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- search loops, packing --------------------------------------------------------
    Loop("s331", "restructure", "search loop -> max-index reduction",
         "j = the LAST index with a[i] < 0: a reduction(max) in disguise",
         init_extra="    for (int i = 0; i < LEN_1D - LEN_1D/7; i++) if ((i * 31) % 101 == 0) a[i] = -a[i];",
         expert="""    int j = -1;
    real_t chksum = 0;
    for (int nl = 0; nl < R; nl++) {
        j = -1;
        #pragma omp parallel for reduction(max:j)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                if (i > j) j = i;
            }
        }
        chksum = (real_t) j;
        pb_mix(nl);
    }
    (void)chksum;
    return j+1;"""),
    Loop("s341", "restructure", "packing (stream compaction): count, prefix offsets, scatter",
         "the output position j depends on how many earlier elements were positive",
         init_extra="    for (int i = 0; i < LEN_1D; i++) if ((i * 17) % 5 < 2) b[i] = -b[i];",
         expert="""    for (int nl = 0; nl < R; nl++) {
        int nthreads = 1;
        long* counts = NULL;
        #pragma omp parallel
        {
            #pragma omp single
            {
                nthreads = omp_get_num_threads();
                counts = (long*)calloc((size_t)nthreads + 1, sizeof(long));
            }
            int tid = omp_get_thread_num();
            long lo = (long)LEN_1D * tid / nthreads, hi = (long)LEN_1D * (tid + 1) / nthreads;
            long n = 0;
            for (long i = lo; i < hi; i++) if (b[i] > (real_t)0.) n++;
            counts[tid + 1] = n;
            #pragma omp barrier
            #pragma omp single
            for (int t = 0; t < nthreads; t++) counts[t + 1] += counts[t];
            long j = counts[tid] - 1;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    j++;
                    a[j] = b[i];
                }
            }
        }
        free(counts);
        pb_mix(nl);
    }
    return (real_t)0;"""),
    # ---- genuine recurrences: the right answer is to decline ----------------------------
    # (coefficients scaled below 1 so the recurrence stays finite over LEN_1D elements)
    Loop("s321", "decline", "first-order linear recurrence", "a[i] needs a[i-1] of the same sweep",
         init_extra="    for (int i = 0; i < LEN_1D; i++) b[i] *= (real_t)0.5;", reps=8),
    Loop("s322", "decline", "second-order linear recurrence", "a[i] needs a[i-1] and a[i-2]",
         init_extra="    for (int i = 0; i < LEN_1D; i++) { b[i] *= (real_t)0.3; c[i] *= (real_t)0.3; }", reps=8),
    Loop("s323", "decline", "coupled recurrence", "a[i] needs b[i-1], b[i] needs a[i]", reps=8),
    Loop("s3112", "decline", "running sum saved per element (prefix sum)",
         "b[i] is the sum of a[0..i]; a parallel scan reorders the additions"),
    # ---- parallel as written: the control group ---------------------------------------
    Loop("s000", "annotate", "none (no dependence)", "each element from its own input",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) a[i] = b[i] + 1;
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("vpvtv", "annotate", "none (no dependence)", "a[i] += b[i]*c[i]",
         expert="""    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) a[i] += b[i] * c[i];
        pb_mix(nl);
    }
    return (real_t)0;"""),
    Loop("s313", "annotate", "none (a sum reduction clause)", "dot product",
         expert="""    real_t dot = 0;
    for (int nl = 0; nl < R; nl++) {
        dot = (real_t)0.;
        #pragma omp parallel for reduction(+:dot)
        for (int i = 0; i < LEN_1D; i++) dot += a[i] * b[i];
        pb_mix(nl);
    }
    return dot;"""),
]
# T0.11 probe (the author's decision 8, 24 Sep): TSVC's indirect-addressing loops, whose iterations
# conflict or not depending on the VALUES of an index array — which DiscoPoP observes at run time and a
# reader can only derive from the initialization.  Class unknown until measured (no model); s4116 is left
# out, it needs TSVC's 2-D arrays, which this packaging does not build.
_IP_GLOBAL = "static int *pb_ip;   /* TSVC's index array (common.c), set in init_array */"
_IP_INIT = ("    pb_ip = (int *)malloc((size_t)LEN_1D * sizeof(int));\n"
            "    for (int i = 0; i < LEN_1D; i += 5) {\n"
            "        pb_ip[i] = i + 4; pb_ip[i + 1] = i + 2; pb_ip[i + 2] = i; pb_ip[i + 3] = i + 3; pb_ip[i + 4] = i + 1;\n"
            "    }")
_IP = "    int * __restrict__ ip = pb_ip;"
_PROBE = ("probe", "to be measured (T0.11): indirect addressing",
          "whether iterations conflict depends on the values in the index array")
LOOPS += [
    Loop("s4112", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP + "\n    real_t s = (real_t)1.0;"),
    Loop("s4113", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP),
    Loop("s4114", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP + "\n    int n1 = 1;"),
    Loop("s4115", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP),
    Loop("s4117", *_PROBE),
    Loop("s4121", *_PROBE, globals_="static real_t f(real_t a, real_t b)\n{\n    return a*b;\n}"),
    Loop("s491", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP),
    Loop("s353", *_PROBE, init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP),
]
BY_NAME = {l.name: l for l in LOOPS}

# ---- packaging v4 (D39, 25 Sep): the model's file holds only the loop ------------------------
# Until v3 the package was ONE file: our measurement (sizes, data, initial values, perturbed
# input, digest, timing, the per-repetition perturbation, `main`) — 160 of its 174 lines — in
# front of the loop. The models read it, DiscoPoP profiled it (87 % of its dependence records,
# 117 task patterns over `main`), and its dependences reached the agent's evidence. From v4 the
# measurement lives in a header generated per loop under `prepared/_harness/tsvc/`, OUTSIDE the
# package: DiscoPoP instruments only code inside the project root, no model's working copy holds
# it, and every build finds it through CPATH (tools/harness_include.py). What stays in the file:
#   * the licence line;
#   * `#include "tsvc/<name>.h"`;
#   * TSVC's loop, verbatim, in `static real_t kernel_<name>(void)`; the repetition bound is
#     our `R` and the per-repetition call is our `pb_mix(nl)` where TSVC calls its own empty
#     `dummy(...)` (whose 2-D arguments this packaging does not build);
#   * `PB_MAIN(kernel_<name>)`, which expands to `main`: `main` has to be instrumented for
#     DiscoPoP to follow the call path into the kernel (MULTIFILE.md), and a macro expanded in
#     this file is attributed to this file.
# `pb_mix` stays in the file (see PB_MIX below). As a macro its code was attributed to the
# kernel and moved the kernel's recorded start line onto the repetition loop (s313, 25 Sep).
# The lines the benchmark code shares with the harness are listed in meta.json (`protected`):
# every arm is told about them in the same words, the agent's gate refuses a change to them.
# `pb_mix` stays IN the benchmark's file, verbatim as in v3: it is where the repetitions depend
# on each other, and DiscoPoP has to observe that — measured, T0.15 on the Mac, 25 Sep: with
# `pb_mix` in the outside header (uninstrumented) DiscoPoP reported the REPETITION loop of s211
# and s212 as a Do-All and the agent's queue changed. Its lines are protected like the others.
PB_MIX = """
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
"""
PB_MIX_LINES = [l.strip() for l in PB_MIX.splitlines()
                if l.strip() and not l.strip().startswith(("/*", "*")) and l.strip() not in ("{", "}")]

KERNEL_HEAD = """/* TSVC-2 loop %(name)s, from TSVC-2 src/tsvc.c (%(provenance)s; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc/%(name)s.h"
"""

HARNESS_HEAD = """/* Measurement harness for TSVC-2 loop %(name)s: data, sizes, initial values, perturbed input,
 * digest, timing, the per-repetition perturbation and main. Generated by
 * agent/tools/prepare_tsvc.py (v%(version)d) — do not edit by hand. It lives OUTSIDE the
 * benchmark's directory (D39): DiscoPoP instruments only code inside the project root, and no
 * model's working copy holds this file. Default dataset SMALL; override with -D<SIZE>_DATASET.
 * Digest on stdout; -DPB_FULL_DUMP prints every value; argv[1] is a perturbation seed. */
#ifndef PB_TSVC_HARNESS
#define PB_TSVC_HARNESS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

typedef double real_t;
"""

SIZE_BLOCK = """
#if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) \\
    && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
# define SMALL_DATASET
#endif
""" + "".join(f"#ifdef {k}_DATASET\n# define LEN_1D {v}\n#endif\n" for k, v in SIZES.items()) + """#define R %(reps)d
"""

DATA = """
/* ---- data: TSVC's five vectors ------------------------------------------------ */
static real_t *a, *b, *c, *d, *e;
%(harness_globals)s#ifdef PB_EXPERT_TMP
static real_t *pb_tmp;   /* an expert reference's scratch vector */
#endif


static void init_array(void)
{
  for (int i = 0; i < LEN_1D; i++) {
    a[i] = (real_t)0.75 + (real_t)((i * 37L) %% 1000) * (real_t)0.0005;
    b[i] = (real_t)0.75 + (real_t)((i * 53L) %% 997) * (real_t)0.0005;
    c[i] = (real_t)0.75 + (real_t)((i * 71L) %% 991) * (real_t)0.0005;
    d[i] = (real_t)0.75 + (real_t)((i * 89L) %% 983) * (real_t)0.0005;
    e[i] = (real_t)0.75 + (real_t)((i * 97L) %% 977) * (real_t)0.0005;
  }
%(init_extra)s
}

static void pb_emit_array(const real_t* v)
{
#ifdef PB_FULL_DUMP
  for (long i = 0; i < LEN_1D; i++) pb_emit(v[i]);
#else
  /* both ends and the middle in full, the rest sampled */
  long step = LEN_1D / 2000 > 0 ? LEN_1D / 2000 : 1;
  for (long i = 0; i < 32 && i < LEN_1D; i++) pb_emit(v[i]);
  for (long i = LEN_1D / 2 - 16; i < LEN_1D / 2 + 16; i++) if (i >= 32 && i < LEN_1D) pb_emit(v[i]);
  for (long i = LEN_1D - 32; i < LEN_1D; i++) if (i >= LEN_1D / 2 + 16) pb_emit(v[i]);
  for (long i = 32; i < LEN_1D - 32; i += step) pb_emit(v[i]);
#endif
}
"""

DRIVER = """
/* ---- main, in the order v3's main ran it ------------------------------------------ */
static int pb_setup(int argc, char** argv)
{
  a = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  b = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  c = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  d = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  e = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
#ifdef PB_EXPERT_TMP
  pb_tmp = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
#endif
  if (!a || !b || !c || !d || !e) { fprintf(stderr, "out of memory\\n"); return 1; }
  init_array();
  /* Optional perturbed input, see PB_PERTURB: magnitudes and signs of the data are kept. */
  if (argc > 1) {
    unsigned long long pb_state = pb_seed(argv[1]);
    for (long pb_i = 0; pb_i < LEN_1D; pb_i++) {
      a[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      b[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      c[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      d[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      e[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
    }
  }
  return 0;
}

static void pb_finish(real_t result)
{
  pb_emit(result);
  pb_emit_array(a); pb_emit_array(b); pb_emit_array(c); pb_emit_array(d); pb_emit_array(e);
  pb_report();
  free(a); free(b); free(c); free(d); free(e);
}

/* `main`, expanded in the benchmark's file so that DiscoPoP instruments it: the timed region is
 * the kernel call, as in v3. */
#define PB_MAIN(K)                                        \\
  int main(int argc, char** argv)                         \\
  {                                                       \\
    if (pb_setup(argc, argv)) return 1;                   \\
    pb_timer_start();                                     \\
    real_t pb_result = K();                               \\
    pb_timer_stop();                                      \\
    pb_finish(pb_result);                                 \\
    return 0;                                             \\
  }

#endif
"""

# What every arm is told about the lines the loop shares with the harness — the same words for
# the agent, its twins and the model alone (rendered by the agent, `llm/request.py`).
PROTECTED_NOTE = ("`pb_mix(nl)` changes a few input values between two repetitions of the `nl` loop, so the "
                  "repetitions depend on each other and must run in order; the loop under study is the one "
                  "inside it.")


def _is_harness_global(g: str) -> bool:
    """File-scope code that is the harness's (the index array TSVC's common.c sets up), as
    opposed to TSVC's own code the loop calls (s4121's `f`), which stays with the loop."""
    return "pb_ip" in g


def _tsvc_function(name: str) -> Tuple[str, str, str, str]:
    """(category comment, local declarations, repetition body, return expression) of a TSVC
    function, verbatim from tsvc.c."""
    text = TSVC.read_text()
    m = re.search(r"^real_t %s\(struct args_t \* func_args\)\n\{\n(.*?)^\}" % re.escape(name), text, re.S | re.M)
    if not m:
        raise ValueError(f"{name}: not found in {TSVC}")
    body = m.group(1)
    category = " / ".join(l.strip("/ ").strip() for l in body.splitlines() if l.strip().startswith("//") and l.strip("/ ").strip())
    after_t1 = body.split("gettimeofday(&func_args->t1, NULL);", 1)[1]
    head, rest = re.split(r"^\s*for \(int nl = 0;[^\n]*\{\n", after_t1, maxsplit=1, flags=re.M)
    decls = "\n".join(l for l in head.splitlines() if l.strip() and not l.strip().startswith("//"))
    rep, tail = re.split(r"^\s*dummy\([^\n]*\n", rest, maxsplit=1, flags=re.M)
    ret = re.search(r"return ([^;]+);", tail)
    expr = ret.group(1).strip() if ret else "0"
    if "calc_checksum" in expr:
        expr = "(real_t)0"
    return category, decls, rep.rstrip("\n"), expr


def render_harness(loop: Loop) -> str:
    """The measurement header for one loop (v4): everything of v3's file except the loop."""
    return (HARNESS_HEAD % {"name": loop.name, "version": GENERATOR_VERSION}
            + SIZE_BLOCK % {"reps": loop.reps} + SCAFFOLD
            + DATA % {"init_extra": loop.init_extra,
                      "harness_globals": (loop.globals_ + "\n") if _is_harness_global(loop.globals_) else ""}
            + DRIVER)


def render(loop: Loop, expert: bool = False) -> str:
    """The benchmark's own file (v4) — or, with `expert`, the reference solution in the same
    layout, which declares what the reference needs before including the harness."""
    category, decls, rep, ret = _tsvc_function(loop.name)
    sha = hashlib.sha256(TSVC.read_bytes()).hexdigest()[:12]
    kernel_globals = "" if _is_harness_global(loop.globals_) else loop.globals_
    if expert:
        if loop.expert is None:
            raise ValueError(f"{loop.name}: no expert reference (class {loop.expected})")
        needs_tmp = "pb_tmp" in loop.expert
        needs_omp = "omp_get" in loop.expert
        pre = ("#define PB_EXPERT_TMP\n" if needs_tmp else "") + ("#include <omp.h>\n" if needs_omp else "")
        head = (f"/* EXPERT REFERENCE for TSVC-2 {loop.name} ({loop.transformation}). Not part of the\n"
                f" * package: it shows the task is solvable and gives the speedup ceiling. */\n"
                + pre + f'#include "tsvc/{loop.name}.h"\n' + PB_MIX)
        kernel = f"static real_t kernel_{loop.name}(void)\n{{\n{loop.expert}\n}}\n"
    else:
        head = KERNEL_HEAD % {"name": loop.name, "provenance": f"sha256 {sha}"} + PB_MIX
        kernel = (f"static real_t kernel_{loop.name}(void)\n{{\n"
                  + (loop.pre + "\n" if loop.pre else "")
                  + (decls + "\n" if decls else "")
                  + "    for (int nl = 0; nl < R; nl++) {\n" + rep + "\n        pb_mix(nl);\n    }\n"
                  + f"    return {ret};\n}}\n")
    return (head + ("\n" + kernel_globals + "\n" if kernel_globals else "")
            + "\n" + kernel + f"\nPB_MAIN(kernel_{loop.name})\n")


def protected_lines(loop: Loop) -> List[str]:
    """The lines of the benchmark's file the harness depends on, whitespace-stripped: the
    include, the per-repetition call, `main`, and any line binding a harness array (the
    probes' `ip`). Driven from here into meta.json, the gate and every arm's prompt."""
    lines = [f'#include "tsvc/{loop.name}.h"'] + PB_MIX_LINES
    lines += [l.strip() for l in loop.pre.splitlines() if "pb_" in l]
    lines += ["pb_mix(nl);", f"PB_MAIN(kernel_{loop.name})"]
    return lines



# ---- packaging v3, kept verbatim: every run up to E2 used it, and it stays the default until T0.15 ---------
# shows v4 leaves DiscoPoP's view of every loop unchanged (it does not yet: s211, 25 Sep).
V3_HEADER = """/* Generated by agent/tools/prepare_tsvc.py (v%(version)d) — do not edit by hand.
 * TSVC-2 loop %(name)s. The loop body is verbatim from TSVC-2 (src/tsvc.c, %(provenance)s; University of
 * Illinois licence, see benchmarks/TSVC_2/license.txt). The packaging around it — data type,
 * sizes, initial values, repetitions, output, timing — is this harness's.
 * Default dataset SMALL; override with -D<SIZE>_DATASET. Digest on stdout;
 * -DPB_FULL_DUMP prints every value; argv[1] is a perturbation seed. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
%(omp_include)s
typedef double real_t;
"""

V3_SIZE_BLOCK = """
#if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) \\
    && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
# define SMALL_DATASET
#endif
""" + "".join(f"#ifdef {k}_DATASET\n# define LEN_1D {v}\n#endif\n" for k, v in SIZES.items()) + """#define R %(reps)d
"""

V3_DATA = """
/* ---- data: TSVC's five vectors ------------------------------------------------ */
static real_t *a, *b, *c, *d, *e;
%(tmp_decl)s
/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) %% LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static void init_array(void)
{
  for (int i = 0; i < LEN_1D; i++) {
    a[i] = (real_t)0.75 + (real_t)((i * 37L) %% 1000) * (real_t)0.0005;
    b[i] = (real_t)0.75 + (real_t)((i * 53L) %% 997) * (real_t)0.0005;
    c[i] = (real_t)0.75 + (real_t)((i * 71L) %% 991) * (real_t)0.0005;
    d[i] = (real_t)0.75 + (real_t)((i * 89L) %% 983) * (real_t)0.0005;
    e[i] = (real_t)0.75 + (real_t)((i * 97L) %% 977) * (real_t)0.0005;
  }
%(init_extra)s
}

static void pb_emit_array(const real_t* v)
{
#ifdef PB_FULL_DUMP
  for (long i = 0; i < LEN_1D; i++) pb_emit(v[i]);
#else
  /* both ends and the middle in full, the rest sampled */
  long step = LEN_1D / 2000 > 0 ? LEN_1D / 2000 : 1;
  for (long i = 0; i < 32 && i < LEN_1D; i++) pb_emit(v[i]);
  for (long i = LEN_1D / 2 - 16; i < LEN_1D / 2 + 16; i++) if (i >= 32 && i < LEN_1D) pb_emit(v[i]);
  for (long i = LEN_1D - 32; i < LEN_1D; i++) if (i >= LEN_1D / 2 + 16) pb_emit(v[i]);
  for (long i = 32; i < LEN_1D - 32; i += step) pb_emit(v[i]);
#endif
}
"""

V3_MAIN = """
int main(int argc, char** argv)
{
  a = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  b = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  c = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  d = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
  e = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
%(tmp_alloc)s  if (!a || !b || !c || !d || !e) { fprintf(stderr, "out of memory\\n"); return 1; }
  init_array();
  /* Optional perturbed input, see PB_PERTURB: magnitudes and signs of the data are kept. */
  if (argc > 1) {
    unsigned long long pb_state = pb_seed(argv[1]);
    for (long pb_i = 0; pb_i < LEN_1D; pb_i++) {
      a[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      b[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
      c[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      d[pb_i] *= (real_t)(1.0 + 0.1 * pb_uniform(&pb_state));
      e[pb_i] *= (real_t)(1.0 + 0.2 * pb_uniform(&pb_state));
    }
  }

  pb_timer_start();
  real_t result = kernel_%(name)s();
  pb_timer_stop();

  pb_emit(result);
  pb_emit_array(a); pb_emit_array(b); pb_emit_array(c); pb_emit_array(d); pb_emit_array(e);
  pb_report();
  free(a); free(b); free(c); free(d); free(e);
  return 0;
}
"""


def render_v3(loop: Loop, expert: bool = False) -> str:
    """Packaging v3 (the layout of every run up to E2): one file, our measurement in front of the loop."""
    category, decls, rep, ret = _tsvc_function(loop.name)
    sha = hashlib.sha256(TSVC.read_bytes()).hexdigest()[:12]
    needs_tmp = expert and loop.expert is not None and "pb_tmp" in loop.expert
    needs_omp = expert and loop.expert is not None and "omp_get" in loop.expert
    if expert:
        if loop.expert is None:
            raise ValueError(f"{loop.name}: no expert reference (class {loop.expected})")
        kernel = (f"/* EXPERT REFERENCE for TSVC-2 {loop.name} ({loop.transformation}). Not part of the\n"
                  f" * package: it shows the task is solvable and gives the speedup ceiling. */\n"
                  f"static real_t kernel_{loop.name}(void)\n{{\n{loop.expert}\n}}\n")
    else:
        kernel = (f"static real_t kernel_{loop.name}(void)\n{{\n"
                  + (loop.pre + "\n" if loop.pre else "")
                  + (decls + "\n" if decls else "")
                  + "    for (int nl = 0; nl < R; nl++) {\n" + rep + "\n        pb_mix(nl);\n    }\n"
                  + f"    return {ret};\n}}\n")
    return (V3_HEADER % {"version": 3, "name": loop.name, "category": category,
                      "expected": loop.expected, "transformation": loop.transformation,
                      "provenance": f"sha256 {sha}", "omp_include": "#include <omp.h>" if needs_omp else ""}
            + V3_SIZE_BLOCK % {"reps": loop.reps} + SCAFFOLD
            + V3_DATA % {"init_extra": loop.init_extra,
                      "tmp_decl": "\n".join(x for x in (
                          "static real_t *pb_tmp;   /* the reference's scratch vector */" if needs_tmp else "",
                          loop.globals_) if x)}
            + "\n" + kernel
            + V3_MAIN % {"name": loop.name,
                      "tmp_alloc": "  pb_tmp = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));\n" if needs_tmp else ""})


def _build_run(src: Path, out: Path, flags: List[str], args: List[str], threads: Optional[int]) -> Tuple[bool, str]:
    omp = []
    if "-fopenmp" in flags and sys.platform == "darwin" and Path("/usr/local/opt/libomp").exists():
        omp = ["-I/usr/local/opt/libomp/include", "-L/usr/local/opt/libomp/lib"]
    r = subprocess.run([_cc(), "-O2", *_sysroot(), *flags, *omp, str(src), "-o", str(out), "-lm"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "build: " + r.stderr[-300:]
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    r = subprocess.run([str(out), *args], capture_output=True, text=True, timeout=600, env=env)
    if r.returncode != 0:
        return False, f"run rc={r.returncode}: {r.stderr[-200:]}"
    return True, r.stdout


def _max_rel(x: str, y: str) -> float:
    xs, ys = x.split(), y.split()
    if len(xs) != len(ys) or not xs:
        return float("inf")
    worst = 0.0
    for p, q in zip(xs, ys):
        u, v = float(p), float(q)
        if u != u or v != v or abs(u) == float("inf") or abs(v) == float("inf"):
            return float("inf")
        worst = max(worst, abs(u - v) / max(abs(u), abs(v), 1e-300))
    return worst


def validate(loop: Loop, package: Path, reference: Optional[Path]) -> List[str]:
    """The package runs, its output is finite, the perturbed input changes it, and the expert
    reference — built with OpenMP, 4 threads — computes the same values on both inputs."""
    problems: List[str] = []
    with tempfile.TemporaryDirectory(prefix=f"tsvc_{loop.name}_") as tmp:
        t = Path(tmp)
        outs: Dict[str, str] = {}
        for tag, args in (("default", []), ("seeded", ["7"])):
            ok, out = _build_run(package, t / "orig", ["-DPB_FULL_DUMP", "-DSMALL_DATASET"], args, None)
            if not ok:
                return [f"original ({tag}): {out}"]
            outs[tag] = out
            vals = [float(v) for v in out.split()]
            if any(v != v or abs(v) == float("inf") for v in vals):
                problems.append(f"original ({tag}): non-finite values")
        if outs["default"] == outs["seeded"]:
            problems.append("the perturbed input does not change the output")
        ok, again = _build_run(package, t / "orig", ["-DPB_FULL_DUMP", "-DSMALL_DATASET"], [], None)
        if ok and again != outs["default"]:
            problems.append("the original is not deterministic")
        if reference is not None:
            for tag, args in (("default", []), ("seeded", ["7"])):
                ok, out = _build_run(reference, t / "ref", ["-DPB_FULL_DUMP", "-DSMALL_DATASET", "-fopenmp"], args, 4)
                if not ok:
                    problems.append(f"reference ({tag}): {out}")
                    continue
                err = _max_rel(outs[tag], out)
                if err > 1e-9:
                    problems.append(f"reference ({tag}) differs from the original: max rel err {err:.2e}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help=f"default: all {len(LOOPS)}")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--harness-out", type=Path, default=None,
                    help="where the measurement headers go (default: <out>/../_harness — outside every "
                         "package, D39); builds find them through CPATH (harness_include.py)")
    ap.add_argument("--references-out", type=Path, default=REFERENCES,
                    help="where the expert references go (default: the tracked agent/reference_solutions/tsvc)")
    ap.add_argument("--layout", choices=("v3", "v4"), default="v3",
                    help="v3 (default): the one-file layout of every run so far; v4 (D39): the measurement "
                         "in a header outside the package — BLOCKED until T0.15 shows DiscoPoP's view of every "
                         "loop is unchanged (it is not yet: s211, 25 Sep)")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    harness_root = (a.harness_out or a.out.parent / "_harness").resolve()
    refs: Path = a.references_out
    # The validation builds must find the headers exactly as every other build does.
    os.environ["CPATH"] = os.pathsep.join([str(harness_root)] + [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p])
    failed = 0
    refs.mkdir(parents=True, exist_ok=True)
    if a.layout == "v4":
        (harness_root / "tsvc").mkdir(parents=True, exist_ok=True)
    for loop in [BY_NAME[n] for n in a.names] if a.names else LOOPS:
        d = a.out / loop.name
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        src = d / f"{loop.name}.c"
        v4 = a.layout == "v4"
        src.write_text(render(loop) if v4 else render_v3(loop))
        hdr = harness_root / "tsvc" / f"{loop.name}.h"
        if v4:
            hdr.write_text(render_harness(loop))
        ref: Optional[Path] = None
        if loop.expert is not None:
            ref = refs / f"{loop.name}.c"
            ref.write_text(render(loop, expert=True) if v4 else render_v3(loop, expert=True))
        category = _tsvc_function(loop.name)[0]
        (d / "meta.json").write_text(json.dumps({
            "suite": "tsvc", "kernel": loop.name, "source": "benchmarks/TSVC_2/src/tsvc.c",
            "category": category, "file": src.name, "language": "c", "layout": "single",
            "restructuring_class": loop.expected, "transformation": loop.transformation, "why": loop.why,
            "reference_solution": (str(ref.relative_to(HARNESS_ROOT)) if ref.is_relative_to(HARNESS_ROOT)
                                   else str(ref)) if ref else None,
            **({
                # v4: the harness's code is not in the package: `main` (PB_MAIN) and `pb_mix`
                # are the only functions of the file that are not the benchmark's.
                "exclude_functions": ["main", "pb_mix"],
                "harness": f"tsvc/{loop.name}.h",
                "harness_sha256": hashlib.sha256(hdr.read_bytes()).hexdigest(),
                "protected": protected_lines(loop),
                "protected_note": PROTECTED_NOTE,
            } if v4 else {
                "exclude_functions": ["init_array", "pb_mix", "pb_emit", "pb_emit_array", "pb_report", "pb_seed",
                                      "pb_uniform", "pb_timer_start", "pb_timer_stop", "main"],
            }),
            "agent_dataset": "SMALL", "generator_version": GENERATOR_VERSION if v4 else 3,
            "inputs_sha256": hashlib.sha256(TSVC.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        }, indent=2) + "\n")
        note = ""
        if a.validate:
            problems = validate(loop, src, ref)
            failed += bool(problems)
            note = "  OK" if not problems else "  FAILED: " + "; ".join(problems)
        print(f"{loop.name:7s} {loop.expected:11s} {loop.transformation[:52]:52s}{note}", flush=True)
    print(f"{len(a.names) or len(LOOPS)} loops -> {a.out} (harness headers in {harness_root / 'tsvc'})"
          + (f"   ({failed} failed validation)" if a.validate else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
