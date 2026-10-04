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
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_calib import SCAFFOLD, _cc, _sysroot  # noqa: E402  (the same packaging code)
import hot_loop_coverage  # noqa: E402  (E2-B1's hot loop is read by the parser that judges it)

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
                 pre: str = "", globals_: str = "", suite: str = "tsvc", emit_extra: str = "",
                 hot_function: str = "", hot_writes: Tuple[str, ...] = (),
                 hot_aliases: Tuple[str, ...] = (), body: Optional[Tuple[str, str]] = None,
                 source: str = "") -> None:
        self.name, self.expected, self.transformation, self.why = name, expected, transformation, why
        # `pre`: the argument declarations TSVC passes through `func_args` (set in its main), which
        # the extracted body does not contain; `globals_`: file-scope code the loop needs (TSVC's
        # `f`, the index array).  Neither may say anything about how to parallelize (D36).
        self.pre, self.globals_ = pre, globals_
        # `emit_extra` (v4 only): harness code that adds to the digest what the loop writes beyond
        # TSVC's five vectors (s424's flat array); empty for every loop that writes only a..e
        self.emit_extra = emit_extra
        self.expert, self.init_extra, self.reps = expert, init_extra, reps
        # the suite the package belongs to (its directory under prepared/, its header's directory
        # under prepared/_harness/, meta.json's `suite`): `tsvc` for every loop of E1-E2, `tsvc_b1` for
        # E2-B1's (packaging v4 only, D39 reversed for E2-B1 alone)
        self.suite = suite
        # E2-B1's hot loop (see `hot_loop` below): the function that holds it (default: the kernel)
        # and what it writes, declared by hand from reading the loop — the packager refuses a
        # package whose parsed hot loop writes anything else; `hot_aliases`, other names of that
        # memory bound in the harness header, where the coverage check cannot see them (s424)
        self.hot_function, self.hot_writes, self.hot_aliases = hot_function, hot_writes, hot_aliases
        # A constructed kernel instead of a TSVC function (ORDER-2, 29 Sep): (category, the body of one
        # repetition). None for every TSVC loop, whose body is read from tsvc.c.
        self.body = body
        # meta.json's `source` for a constructed kernel other than ORDER-2's (ORDER-3, 3 Oct); "" keeps the default
        self.source = source


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


def _tsvc_callee(name: str) -> str:
    """A helper TSVC's loop calls (`s151s`), verbatim from tsvc.c with its comments removed — a
    comment in TSVC's source can name what the loop tests (D36)."""
    text = TSVC.read_text()
    m = re.search(r"^void %s\(.*?\n\{\n.*?^\}\n" % re.escape(name), text, re.S | re.M)
    if not m:
        raise ValueError(f"{name}: not found in {TSVC}")
    lines = [re.sub(r"\s*//.*$", "", l) for l in m.group(0).splitlines()]
    return "\n".join(l for l in lines if l.strip())


# E2-B1 (the evidence experiment on hidden facts; the author, 26 Sep): loops whose deciding fact — whether
# the loop may run in parallel — is NOT in the loop's own statements. Packaging v4 only, in their own suite
# (`prepared/tsvc_b1`), so that a fact set in the harness is truly out of the model's file while DiscoPoP
# still measures the dependence it causes. Chosen from the screen (docs/screening/) by the selection rule
# recorded before the screen; every unit still has to pass its measured conditions before any trial
# (record §6, 26-27 Sep). Tier 1: the fact sits outside the loop's function; tier 2 (reported apart): in
# the same function. Direction (a) hides a dependence, (b) an independence (the author's decisions, 27 Sep;
# docs/e2b1/PREPARATION.md). s258 of (b) is not packaged: see s482 below.
_B1A = "hidden dependence (E2-B1 a)"
_B1A2 = "hidden dependence (E2-B1 a, tier 2)"
_B1B = "hidden independence (E2-B1 b)"
B1_LOOPS: List[Loop] = [
    # tier 1 (a): the distance is the caller's argument — `s151s(a, b, 1)`: a[i] = a[i + 1] + b[i]
    Loop("s151", _B1A, "the distance m of the callee's loop is the caller's argument",
         "with m = 1 each iteration reads the element the next one overwrites",
         globals_=_tsvc_callee("s151s"), suite="tsvc_b1", hot_function="s151s", hot_writes=("a",)),
    # tier 1 (a): which branch runs is decided by b's sign pattern in TSVC's initial data (common.c:
    # b = +1 at even, -1 at odd indices), set in the harness: an odd iteration writes c[i+1], which the
    # next (even) iteration reads. The packaging's own values are all positive and lose it, so the
    # pattern is reproduced on its magnitudes (pb_mix adds at most 0.25 once per element and the
    # perturbation scales by 0.8-1.2: no sign changes).
    Loop("s161", _B1A, "whether a later iteration reads what an earlier one wrote depends on b's signs",
         "b alternates in sign, so an odd iteration writes c[i+1] and the next one reads it",
         init_extra="    for (int i = 1; i < LEN_1D; i += 2) b[i] = -b[i];", suite="tsvc_b1",
         hot_writes=("a", "c")),
    # tier 2 (a), the fact in the loop's own function (the author, 27 Sep: reported apart from tier 1).
    # s131 is the first of its group (s131, s421, s422, s423): `int m  = 1;` stands one line above the
    # repetition loop in TSVC, after the timer starts, so the extraction's declarations carry it verbatim.
    Loop("s131", _B1A2, "the distance m is a local set just above the repetition loop",
         "m = 1 makes each iteration read the element the following iteration overwrites",
         suite="tsvc_b1", hot_writes=("a",)),
    # tier 2 (a): TSVC sets `vl = 63; xx = flat_2d_array + vl;` in the function, before its timer, so the
    # two lines are the kernel's first (`pre`, verbatim; neither is a harness binding, so neither is
    # protected). `xx` and `flat_2d_array` are TSVC's globals, declared in its header (array_defs.h) — here
    # in the harness header, `xx` WITHOUT TSVC's `__restrict__`: xx aliases flat_2d_array by design, and
    # restrict on an alias is undefined behaviour (the screen, s421-s424). Length of the flat array: TSVC's
    # is LEN_2D*LEN_2D = 65536 for LEN_1D = 32000, about two vectors; so is this one (2 * LEN_1D), which
    # holds everything the loop reads (flat_2d_array[0 .. LEN_1D-2]) and writes (xx[1 .. LEN_1D-1] =
    # flat_2d_array[64 .. LEN_1D+62]) at every dataset size. Its values are the packaging's O(1) periodic
    # ones (TSVC zeroes the first LEN_1D elements; the values decide nothing here, the alias does), and
    # the digest covers the whole array (`emit_extra`): the five vectors' alone would miss every store.
    Loop("s424", _B1A2, "xx is flat_2d_array shifted by vl, set in the same function",
         "with vl = 63 the store to xx[i+1] lands where iteration i+64 reads: a flow at distance 64",
         globals_=("static real_t *flat_2d_array;   /* TSVC's flat array (array_defs.h), set in init_array */\n"
                   "static real_t *xx;              /* TSVC's pointer into it (array_defs.h), without restrict */"),
         init_extra=("    flat_2d_array = (real_t *)malloc((size_t)(2L * LEN_1D) * sizeof(real_t));\n"
                     "    for (long i = 0; i < 2L * LEN_1D; i++)\n"
                     "        flat_2d_array[i] = (real_t)0.75 + (real_t)((i * 61L) % 971) * (real_t)0.0005;"),
         pre="    int vl = 63;\n    xx = flat_2d_array + vl;",
         emit_extra="  pb_emit_array(flat_2d_array); pb_emit_array(flat_2d_array + LEN_1D);\n",
         suite="tsvc_b1", hot_writes=("xx",), hot_aliases=("flat_2d_array",)),
    # ---- direction (b), hidden independence: DESCRIPTIVE (the author, 27 Sep) — the loop's text suggests
    # a dependence that the fact outside its function rules out. All tier 1.
    # s152: whether the call conflicts across iterations is decided in the callee, written in the file
    # verbatim without its comments (as s151s); TSVC's data decides nothing.
    Loop("s152", _B1B, "none: the callee the loop calls touches only element i",
         "s152s updates a[i] from b[i] and c[i] alone, so no two iterations share an element",
         globals_=_tsvc_callee("s152s"), suite="tsvc_b1", hot_writes=("a", "b")),
    # s171: `inc` is s171's argument, `n1 = 1` in TSVC's main (tsvc.c: `time_function(&s171, &n1)`). It
    # is declared in the harness header and set when the harness sets up the data, the way TSVC's main
    # sets it before the call: the model's file uses `inc` without seeing its value. Not a `pre` line — a
    # binding in the file would show the value, and a protected one is presented as measurement code.
    Loop("s171", _B1B, "none: the stride inc is set outside the function (TSVC's main passes 1)",
         "with inc = 1 each iteration updates its own a[i]; with inc = 0 all would update a[0]",
         globals_="static int inc;   /* s171's argument: TSVC's main passes n1 (tsvc.c), set in init_array */",
         init_extra="    inc = 1;", suite="tsvc_b1", hot_writes=("a",)),
    # s481: the exit test reads d, which TSVC sets to 1/(i+1) > 0 (common.c, s481), so no iteration exits.
    # The packaging's own d is positive already (0.75-1.25, scaled by 1.0-1.1 on the perturbed input,
    # +0.125 from pb_mix): the deciding property holds with no init_extra.
    Loop("s481", _B1B, "none: the exit test never fires on TSVC's data",
         "d is positive everywhere (TSVC: d = 1/(i+1)), so no iteration exits and each updates its own a[i]",
         suite="tsvc_b1", hot_writes=("a",)),
    # s258: the scalar s is set under `a[i] > 0` and read by the next two statements, so the text shows a
    # value carried to the next iteration whenever the test fails; TSVC's a is `any,frac` (common.c, s258),
    # positive, so s is set in every iteration and nothing is carried. The packaging's a is positive already
    # (0.75-1.25, scaled by 1.0-1.2 on the perturbed input, only raised by pb_mix): no init_extra for it.
    # The loop runs TSVC's LEN_2D (256) iterations over 1-D arrays and reads row 0 of the 2-D `aa`: the
    # recorded deviation (the author, 27 Sep; record §6) defines LEN_2D as LEN_1D in the header — the trip
    # count raised to the 1-D length, so the loop does measurable work at the campaign's sizes — and builds
    # `aa` as the one row it reads, with the packaging's O(1) positive values (TSVC's are `any,frac`). The
    # loop's text is verbatim; neither value is in the model's file. The digest covers b and e (TSVC's
    # checksum for s258, common.c); aa is only read.
    Loop("s258", _B1B, "none: with TSVC's data the guard holds in every iteration, so s is never carried",
         "a > 0 everywhere (TSVC: a = any,frac), so s is set before every use and each iteration is independent",
         globals_=("#define LEN_2D LEN_1D   /* E2-B1 deviation (27 Sep): TSVC's 256 raised to the 1-D length */\n"
                   "static real_t (*aa)[LEN_1D];   /* TSVC's 2-D aa (array_defs.h): the one row s258 reads */"),
         init_extra=("    aa = (real_t (*)[LEN_1D])malloc((size_t)LEN_1D * sizeof(real_t));\n"
                     "    for (long i = 0; i < LEN_1D; i++)\n"
                     "        aa[0][i] = (real_t)0.75 + (real_t)((i * 43L) % 967) * (real_t)0.0005;"),
         suite="tsvc_b1", hot_writes=("b", "e")),
    # s277: TSVC's a = 1 (common.c, s277), so the first test jumps past both updates in every iteration:
    # the loop does no work with TSVC's data (the screen) — admitted by the author as TSVC ships it (27 Sep).
    # The packaging's a is positive already; b's signs are reproduced as TSVC sets them (first half +1,
    # second half -1) on the packaging's magnitudes. pb_mix raises b[LEN_1D-1] by 0.125 per repetition,
    # which turns that one element positive, but the loop never tests it (i <= LEN_1D-2).
    Loop("s277", _B1B, "none: with TSVC's data the guard skips both updates in every iteration",
         "a >= 0 everywhere (TSVC: a = 1), so the b[i+1] to b[i] flow the text shows never happens",
         init_extra="    for (int i = LEN_1D / 2; i < LEN_1D; i++) b[i] = -b[i];",
         suite="tsvc_b1", hot_writes=("a", "b")),
    # vas, the first of the index-permutation group started at vas (the author, 27 Sep; s491 and s4113
    # stay dropped from new trials): ip is TSVC's permutation (common.c), the harness global the T0.11
    # probes use.
    Loop("vas", _B1B, "none: the index array is a permutation, set outside the function",
         "ip sends distinct iterations to distinct elements of a, so no two iterations write the same one",
         init_extra=_IP_INIT, globals_=_IP_GLOBAL, pre=_IP, suite="tsvc_b1", hot_writes=("a",)),
    # s482: TSVC's b and c are both 1/(i+1) (common.c, s482), so `c[i] > b[i]` never holds and the loop
    # runs to the end; with the packaging's own values it breaks at i = 1 (c[1] > b[1]) and does no work.
    # Equal values would not survive the perturbed input (b scaled by 1.0-1.2, c by 1.0-1.1,
    # independently): c is set to half of b, which keeps c below b under the perturbation and pb_mix
    # (it adds 0.25 to b[k] and only 0.125 to c[k]).
    Loop("s482", _B1B, "none: the early exit never fires on TSVC's data (c is never above b)",
         "c <= b everywhere (TSVC: b = c = 1/(i+1)), so every iteration runs and updates its own a[i]",
         init_extra="    for (int i = 0; i < LEN_1D; i++) c[i] = b[i] * (real_t)0.5;",
         suite="tsvc_b1", hot_writes=("a",)),
]
# ORDER-2 (the evidence pilots of 28 Sep, packaged for the agent on 29 Sep): two statements whose split order
# is decided by index tables the harness sets — X (k17): kv[i] = i-1, so S2 feeds S1 and a split must run
# S2's loop first; Y (k42): ku[i] = i-1, so the textual order is right. The model's files are identical up to
# the opaque id. u and v are 2*LEN_1D long; ju = jv = identity. One repetition (R = 1): with more, u and v
# (updated with +=) would carry a dependence across repetitions too, which is not the fact under test.
_ORDER2_BODY = ("constructed / statement order decided by hidden index tables (ORDER-2)",
                """        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }""")
_ORDER2_GLOBALS = "static real_t *u, *v;\nstatic int *ju, *jv, *ku, *kv;"
_ORDER2_INIT = """    u = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t)); v = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t));
    ju = (int*)malloc((size_t)LEN_1D * sizeof(int)); jv = (int*)malloc((size_t)LEN_1D * sizeof(int));
    ku = (int*)malloc((size_t)LEN_1D * sizeof(int)); kv = (int*)malloc((size_t)LEN_1D * sizeof(int));
    for (long i = 0; i < 2L * LEN_1D; i++) {
      u[i] = (real_t)0.75 + (real_t)((i * 37L) % 1000) * (real_t)0.0005;
      v[i] = (real_t)0.75 + (real_t)((i * 53L) % 997) * (real_t)0.0005;
    }
    for (long i = 0; i < LEN_1D; i++) { ju[i] = (int)i; jv[i] = (int)i; @TABLES@ }"""
_ORDER2_EMIT = "  pb_emit_array(u); pb_emit_array(u + LEN_1D); pb_emit_array(v); pb_emit_array(v + LEN_1D);\n"
B1_LOOPS += [
    Loop("k17", "restructure (ORDER-2 X)", "loop distribution with the second statement's loop first",
         "kv[i] = i-1: line S1 reads the element of v that S2 wrote one iteration earlier; ku[i] = LEN_1D+i: "
         "S2 reads u elements nothing writes", reps=1, globals_=_ORDER2_GLOBALS,
         init_extra=_ORDER2_INIT.replace("@TABLES@", "kv[i] = (int)(i - 1); ku[i] = (int)(LEN_1D + i);"), emit_extra=_ORDER2_EMIT,
         suite="tsvc_b1", hot_writes=("u", "v"), body=_ORDER2_BODY),
    Loop("k42", "restructure (ORDER-2 Y)", "loop distribution in the textual order",
         "ku[i] = i-1: S2 reads the element of u that S1 wrote one iteration earlier; kv[i] = LEN_1D+i: "
         "S1 reads v elements nothing writes", reps=1, globals_=_ORDER2_GLOBALS,
         init_extra=_ORDER2_INIT.replace("@TABLES@", "ku[i] = (int)(i - 1); kv[i] = (int)(LEN_1D + i);"), emit_extra=_ORDER2_EMIT,
         suite="tsvc_b1", hot_writes=("u", "v"), body=_ORDER2_BODY),
]
# E2-V3 (29 Sep): two E1-E2 loops in the v4 layout, so the hot-loop coverage check reads them as it reads every
# E2-B1 unit — s1213, where prompt version 3's order statement fires (line 139's loop first), and s211, where
# it stays silent (DiscoPoP names b on two loops). Their TSVC text, class and notes are E1-E2's.
for _n in ("s1213", "s211"):
    _base = next(l for l in LOOPS if l.name == _n)
    B1_LOOPS.append(Loop(_n, _base.expected, _base.transformation, _base.why, init_extra=_base.init_extra,
                         reps=_base.reps, pre=_base.pre, globals_=_base.globals_, suite="tsvc_b1", hot_writes=("a", "b")))
# ORDER-2b (29 Sep, the author: "Ok"): k17/k42 had one repetition, and the one-iteration repetition loop was a
# trivial Do-All that "covered" the hot loop (DiscoPoP alone 3/3; record §6). Repackaged with TSVC's 48
# repetitions: u accumulates (+=), so the repetition loop is sequential and a wrong split order corrupts every u
# through the first repetition; v is assigned, so its RAW is carried by the inner loop only — the loop
# DiscoPoP's blockers name, which is what version 3's order statement needs. The model's files of X (k19) and
# Y (k48) are identical up to the id; on the Mac's profile (29 Sep) DiscoPoP names only the inner loop in both,
# so the statement fires in Y too, stating the textual order (the control: the evidence must not harm).
_ORDER2B_BODY = ("constructed / statement order decided by hidden index tables (ORDER-2b)",
                 """        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }""")
B1_LOOPS += [
    Loop("k19", "restructure (ORDER-2b X)", "loop distribution with the second statement's loop first",
         "kv[i] = i-1: S1 reads the element of v that S2 wrote one iteration earlier; ku[i] = LEN_1D+i: "
         "S2 reads u elements nothing writes", globals_=_ORDER2_GLOBALS,
         init_extra=_ORDER2_INIT.replace("@TABLES@", "kv[i] = (int)(i - 1); ku[i] = (int)(LEN_1D + i);"),
         emit_extra=_ORDER2_EMIT, suite="tsvc_b1", hot_writes=("u", "v"), body=_ORDER2B_BODY),
    Loop("k48", "restructure (ORDER-2b Y)", "loop distribution in the textual order",
         "ku[i] = i-1: S2 reads the element of u that S1 wrote one iteration earlier; kv[i] = LEN_1D+i: "
         "S1 reads v elements nothing writes", globals_=_ORDER2_GLOBALS,
         init_extra=_ORDER2_INIT.replace("@TABLES@", "ku[i] = (int)(i - 1); kv[i] = (int)(LEN_1D + i);"),
         emit_extra=_ORDER2_EMIT, suite="tsvc_b1", hot_writes=("u", "v"), body=_ORDER2B_BODY),
]
# E1-final (2 Oct, the author: one version — packaging v4 — for every remaining experiment): E1c's population in
# the v4 layout — the 18 class-R loops (s1213 and s211 above), class A s000, vpvtv, s313 and class D s321, s322,
# s323, s3112. TSVC text, class and notes are E1-E2's; the hot loop's writes declared from reading each loop (the
# packager refuses a package whose parsed hot loop writes anything else). s331's hot loop writes only the scalar
# it searches with, which the coverage check does not count — an empty set.
_E1_FINAL_WRITES: Dict[str, Tuple[str, ...]] = {
    "s112": ("a",), "s121": ("a",), "s127": ("a", "j"), "s212": ("a", "b"), "s241": ("a", "b"), "s243": ("a", "b"),
    "s244": ("a", "b"), "s252": ("a",), "s254": ("a",), "s255": ("a",), "s281": ("a", "b"), "s291": ("a",),
    "s292": ("a",), "s293": ("a",), "s331": (), "s341": ("a", "j"),
    "s000": ("a",), "vpvtv": ("a",), "s313": ("dot",),
    "s321": ("a",), "s322": ("a",), "s323": ("a", "b"), "s3112": ("b", "sum"),
}
for _n, _w in _E1_FINAL_WRITES.items():
    _base = next(l for l in LOOPS if l.name == _n)
    B1_LOOPS.append(Loop(_n, _base.expected, _base.transformation, _base.why, init_extra=_base.init_extra,
                         reps=_base.reps, pre=_base.pre, globals_=_base.globals_, suite="tsvc_b1", hot_writes=_w))
# ORDER-3 (3 Oct, the author: "yes the design is ok go ahead"; record §6): more hidden-order kernels, because
# E2-V3's evidence effect rests on ORDER-2 X alone. The same two statements as ORDER-2b X — S1 accumulates into u
# what S2 wrote into v one iteration earlier, S2 reads u elements nothing writes — so the only legal split runs
# S2's loop FIRST, against the text; each kernel hides the deciding fact a different way, always in the harness
# header no model's working copy holds (v4), never in the file:
#   k23 — an offset pointer (`w` is `v` shifted by one element, as f2c-translated code shifts its arrays);
#   k31 — an offset variable (`v[i + off]`, `off` set with the data, as a stencil's offsets often are);
#   k36 — an accessor macro (`AT1(v, i)` reads the element before `i`, defined in the header).
# The control stays ORDER-2b Y (k48). Kept only where DiscoPoP's evidence states the order (prompt v3, D4) —
# checked on a profile before any trial; a mechanism it cannot state is recorded as a finding.
_ORDER3_INIT = """    for (long i = 0; i < 2L * LEN_1D; i++) u[i] = (real_t)0.75 + (real_t)((i * 37L) % 1000) * (real_t)0.0005;
    for (long i = 0; i < LEN_1D; i++) v[i] = (real_t)0.75 + (real_t)((i * 53L) % 997) * (real_t)0.0005;"""
_ORDER3_EMIT = "  pb_emit_array(u); pb_emit_array(u + LEN_1D); pb_emit_array(v);\n"
_ORDER3_SRC = "constructed: ORDER-3 (THESIS_EXPERIMENTS §6, 3 Oct)"
B1_LOOPS += [
    Loop("k23", "restructure (ORDER-3 offset pointer)", "loop distribution with the second statement's loop first",
         "w = v - 1 (the harness allocates one element more and sets v = w + 1): S1 reads the element of v that S2 "
         "wrote one iteration earlier; x = u + LEN_1D: S2 reads u elements nothing writes",
         globals_="static real_t *u, *v, *w, *x;",
         init_extra=("    u = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t));\n"
                     "    w = (real_t*)malloc(((size_t)LEN_1D + 1) * sizeof(real_t)); v = w + 1; x = u + LEN_1D;\n"
                     + _ORDER3_INIT),
         emit_extra=_ORDER3_EMIT, suite="tsvc_b1", hot_writes=("u", "v"), hot_aliases=("w", "x"), source=_ORDER3_SRC,
         body=("constructed / statement order decided by an offset pointer (ORDER-3)",
               """        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }""")),
    Loop("k31", "restructure (ORDER-3 offset variable)", "loop distribution with the second statement's loop first",
         "off = -1: S1 reads the element of v that S2 wrote one iteration earlier; far = LEN_1D: S2 reads u "
         "elements nothing writes",
         globals_="static real_t *u, *v;\nstatic long off, far;",
         init_extra=("    u = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t)); v = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));\n"
                     "    off = -1; far = LEN_1D;\n" + _ORDER3_INIT),
         emit_extra=_ORDER3_EMIT, suite="tsvc_b1", hot_writes=("u", "v"), source=_ORDER3_SRC,
         body=("constructed / statement order decided by an offset variable (ORDER-3)",
               """        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
            v[i] = u[i + far] * d[i] + c[i];
        }""")),
    Loop("k36", "restructure (ORDER-3 accessor macro)", "loop distribution with the second statement's loop first",
         "AT1(p, i) is p[i - 1]: S1 reads the element of v that S2 wrote one iteration earlier; AT2(p, i) is "
         "p[i + LEN_1D]: S2 reads u elements nothing writes",
         globals_=("#define AT1(p, i) ((p)[(i) - 1])\n#define AT2(p, i) ((p)[(i) + LEN_1D])\n"
                   "static real_t *u, *v;"),
         init_extra=("    u = (real_t*)malloc(2 * (size_t)LEN_1D * sizeof(real_t)); v = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));\n"
                     + _ORDER3_INIT),
         emit_extra=_ORDER3_EMIT, suite="tsvc_b1", hot_writes=("u", "v"), source=_ORDER3_SRC,
         body=("constructed / statement order decided by an accessor macro (ORDER-3)",
               """        for (long i = 1; i < LEN_1D; i++) {
            u[i] += AT1(v, i) * c[i];
            v[i] = AT2(u, i) * d[i] + c[i];
        }""")),
]
SUITES: Dict[str, List[Loop]] = {"tsvc": LOOPS, "tsvc_b1": B1_LOOPS}
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
#include "%(suite)s/%(name)s.h"
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
%(emit_extra)s  pb_report();
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


# E2-B1 only (the author, 28 Sep; record §6): v4 hides the harness header, and with it the size table the v3
# file showed every model — in E2-B1's first smoke trial the agent's model sized a stack copy by LEN_1D, which
# passed its gate at SMALL and crashed at the verification size. The fact is restored in the words every arm
# already receives about the harness (the protected note): what LEN_1D is, never how to use it.
B1_SIZE_NOTE = (" `LEN_1D`, the length of the arrays, is set in the included header: " + SIZES["SMALL"]
                + " in the default build, and up to " + SIZES["EXTRALARGE"] + " in the builds that verify the result.")


def protected_note(loop: "Loop") -> str:
    """What every arm is told about the harness lines (meta.json `protected_note`); E2-B1's suite adds the size."""
    return PROTECTED_NOTE + (B1_SIZE_NOTE if loop.suite == "tsvc_b1" else "")


def _is_harness_global(g: str) -> bool:
    """File-scope code that is the harness's, as opposed to TSVC's own code the loop calls
    (s4121's `f`, s151's `s151s`), which stays with the loop. The line is the one TSVC draws:
    its DATA is set up outside the loop's function — declared in its headers (array_defs.h),
    initialised in common.c, passed from main — so a data declaration goes to the header (the
    index array `pb_ip`; E2-B1's `inc` of s171 and flat array of s424), where the model's file
    uses it without seeing its value; a FUNCTION definition (a parameter list followed by a
    body) is TSVC's code and stays in the file. Until E2-B1 the only data global was `pb_ip`,
    so every earlier package renders as before; an empty `g` is nobody's."""
    return bool(g.strip()) and not re.search(r"\)\s*\{", g)


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


def _loop_function(loop: Loop) -> Tuple[str, str, str, str]:
    """_tsvc_function for a TSVC loop; a constructed kernel's own (category, no declarations, body, 0)."""
    if loop.body is not None:
        return loop.body[0], "", loop.body[1], "(real_t)0"
    return _tsvc_function(loop.name)


def render_harness(loop: Loop) -> str:
    """The measurement header for one loop (v4): everything of v3's file except the loop."""
    return (HARNESS_HEAD % {"name": loop.name, "version": GENERATOR_VERSION}
            + SIZE_BLOCK % {"reps": loop.reps} + SCAFFOLD
            + DATA % {"init_extra": loop.init_extra,
                      "harness_globals": (loop.globals_ + "\n") if _is_harness_global(loop.globals_) else ""}
            + DRIVER % {"emit_extra": loop.emit_extra})


def render(loop: Loop, expert: bool = False) -> str:
    """The benchmark's own file (v4) — or, with `expert`, the reference solution in the same
    layout, which declares what the reference needs before including the harness."""
    category, decls, rep, ret = _loop_function(loop)
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
                + pre + f'#include "{loop.suite}/{loop.name}.h"\n' + PB_MIX)
        kernel = f"static real_t kernel_{loop.name}(void)\n{{\n{loop.expert}\n}}\n"
    else:
        head = (f'/* Kernel {loop.name}. */\n#include "{loop.suite}/{loop.name}.h"\n' if loop.body   # constructed: no TSVC provenance
                else KERNEL_HEAD % {"name": loop.name, "suite": loop.suite, "provenance": f"sha256 {sha}"}) + PB_MIX
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
    lines = [f'#include "{loop.suite}/{loop.name}.h"'] + PB_MIX_LINES
    lines += [l.strip() for l in loop.pre.splitlines() if "pb_" in l]
    lines += ["pb_mix(nl);", f"PB_MAIN(kernel_{loop.name})"]
    return lines


def hot_loop(loop: Loop) -> Optional[Dict[str, Any]]:
    """E2-B1's hot loop, for meta.json (`hot_loop`): the author's decision 3 (27 Sep) counts an E2-B1
    program in the primary outcome only when its parallel construct covers this loop, checked by
    hot_loop_coverage.py. The first `for` of `hot_function` that is not the repetition loop (the rule
    of naive_pragma.py, whose loop it must be), its line in the package source, and what it writes —
    read by the same parser that later judges the final program, and checked against the writes
    declared by hand. None outside E2-B1 (suite `tsvc`), so every E1-E2 package stays byte for byte
    what it was. It names the loop under study, so it may only sit where no arm looks: meta.json never
    enters a trial's working copy (cli.run_trial copies the sources and the profile only; D36)."""
    if loop.suite != "tsvc_b1":
        return None
    entry = f"kernel_{loop.name}"
    hot = hot_loop_coverage.describe(render(loop), entry, loop.hot_function or entry)
    if hot["writes"] != sorted(loop.hot_writes):
        raise ValueError(f"{loop.name}: the hot loop at line {hot['line']} writes {hot['writes']}, "
                         f"declared {sorted(loop.hot_writes)} — read the loop again")
    if loop.hot_aliases:
        hot["aliases"] = sorted(loop.hot_aliases)
    return hot



# ---- packaging v5 (the author, 4 Oct 2026; record §6; T0.16): the model's file is an ordinary code file ----
# The author, on the note above `pb_mix` and the harness lines of v4's file: "can't we just have a clean file
# with a code like a normal scenario … the only thing we should do if we receive a benchmark, we have to make
# sure to remove the comments". So a package is a small PROJECT of three files, and one outside it:
#   <name>.c   the benchmark's: one `#include "data.h"` and the loop's function — TSVC's loop text verbatim,
#              one repetition of it. No comment, no line of ours. The ONLY file a model's changes are taken
#              from (meta.json `project.editable`).
#   data.h     ours, declarations only: the type, the size table, the arrays, the function's prototype.
#   main.c     ours: `main` — set-up, the repetition loop calling the function, `pb_mix` between two calls,
#              the timer. It is inside the package because DiscoPoP has to instrument `main` to follow the
#              call path into the function (MULTIFILE.md) and `pb_mix` to see that the repetitions depend
#              on each other (T0.15); a model can read it, a change to it is discarded.
#   prepared/_harness/<suite>/<name>.h   as in v4, outside the package: the data, its initial values, the
#              perturbed input, the digest, the timer. `main.c` includes it after data.h.
# The program is v4's, statement for statement: T0.16 measured identical output on every loop. What a model
# can no longer do is touch the repetitions — move work in front of them, merge or copy them.
# No comment and no `pb_` name may appear in a file a model reads (test_integrity 1d).
V5_SUITE = "tsvc_c1"
V5_HEADER, V5_MAIN = "data.h", "main.c"
# A harness value TSVC's own driver hands to the loop as an ARGUMENT (tsvc.c: `time_function(&vas, ip)`): in
# v4 a protected line bound it inside the function (`int * __restrict__ ip = pb_ip;`); here it is the
# function's parameter and main.c passes it, so no harness name is left in the benchmark's file.
V5_PARAMS: Dict[str, Tuple[str, str]] = {"vas": ("int * __restrict__ ip", "pb_ip")}
# Not in the suite: k36 hides its deciding fact in two accessor MACROS — code, which only a header no model
# can open could hide; k19, k23 and k31 hide the same fact as data (the author, 4 Oct: "ok" to leaving it out).
V5_LEFT_OUT = ("k36",)

V5_HARNESS_HEAD = """/* Measurement harness for %(name)s (packaging v%(version)d): the data, its initial values, the perturbed
 * input, the digest and the timer. Generated by agent/tools/prepare_tsvc.py — do not edit by hand. It lives
 * OUTSIDE the package: the package's main.c includes it after data.h, DiscoPoP instruments only code inside
 * the project root, and no model's working copy holds it. Default dataset SMALL; override with
 * -D<SIZE>_DATASET. Digest on stdout; -DPB_FULL_DUMP prints every value; argv[1] is a perturbation seed. */
#ifndef PB_TSVC_HARNESS
#define PB_TSVC_HARNESS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define R %(reps)d
"""


def _exact(text: str, old: str, new: str) -> str:
    """`text.replace(old, new)` on a shared template — raising when the anchor is gone, so an edit to v4's
    templates cannot silently change what v5 renders."""
    if text.count(old) != 1:
        raise ValueError(f"template anchor found {text.count(old)} times: {old[:50]!r}")
    return text.replace(old, new)


def _no_comments(code: str) -> str:
    """C code without its comments (the author's one preparation step); blank lines a comment leaves go too."""
    out = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    out = re.sub(r"[ \t]*//[^\n]*", "", out)
    return "\n".join(l.rstrip() for l in out.splitlines() if l.strip())


def _dedent4(code: str) -> str:
    """One repetition's statements, taken out of the repetition loop: four spaces less. A line that starts
    further left stays where it is — TSVC writes its `goto` labels in the first column (s161)."""
    return "\n".join((l[4:] if l.startswith("    ") else l) if l.strip() else "" for l in code.splitlines())


def _v5_split_globals(loop: Loop) -> Tuple[List[str], List[str]]:
    """A loop's harness data (`globals_`) as (declarations for data.h, definitions for the header outside
    the package). A value handed to the function as an argument (V5_PARAMS) stays the harness's own."""
    decl: List[str] = []
    defn: List[str] = []
    if not _is_harness_global(loop.globals_):
        return decl, defn
    passed = V5_PARAMS.get(loop.name, ("", ""))[1]
    for line in loop.globals_.splitlines():
        code = re.sub(r"\s*/\*.*?\*/\s*$", "", line).rstrip()
        if not code:
            continue
        if code.startswith("#define"):
            decl.append(code)
        elif code.startswith("static "):
            if passed and re.search(r"\b%s\b" % re.escape(passed), code):
                defn.append(code)
            else:
                decl.append("extern " + code[len("static "):])
                defn.append(code[len("static "):])
        else:
            raise ValueError(f"{loop.name}: harness data line of an unknown form: {line!r}")
    return decl, defn


def render_v5_header(loop: Loop) -> str:
    """data.h: what the benchmark's code uses — declarations, nothing else, no comment."""
    decl, _defn = _v5_split_globals(loop)
    sizes = "\n".join(l for l in (SIZE_BLOCK % {"reps": loop.reps}).strip("\n").splitlines()
                      if not l.startswith("#define R "))
    param = V5_PARAMS.get(loop.name, ("void", ""))[0]
    return ("#ifndef DATA_H\n#define DATA_H\n\n" + sizes + "\n\ntypedef double real_t;\n\n"
            + "extern real_t *a, *b, *c, *d, *e;\n" + "".join(l + "\n" for l in decl)
            + f"\nreal_t kernel_{loop.name}({param});\n\n#endif\n")


def _v5_expert_body(loop: Loop) -> Tuple[str, str]:
    """(function body, the standard headers it needs) of the expert reference as ONE repetition: what stands
    before v4's repetition loop, the loop's body, what follows it. Its scratch vector — the harness's `pb_tmp`
    in v4, allocated outside the timed region — is the function's own here, allocated at the first call and
    kept between calls: all a solution inside the function can do."""
    m = re.search(r"\A(?P<head>.*?)^    for \(int nl = 0; nl < R; nl\+\+\) \{\n(?P<body>.*?)^        pb_mix\(nl\);\n"
                  r"    \}\n(?P<tail>.*)\Z", loop.expert or "", re.S | re.M)
    if not m:
        raise ValueError(f"{loop.name}: the expert reference is not `declarations; repetition loop; tail`")
    body = m.group("head") + _dedent4(m.group("body").rstrip("\n")) + "\n" + m.group("tail").rstrip("\n")
    includes = ""
    if "pb_tmp" in body:
        if re.search(r"\btmp\b", body):
            raise ValueError(f"{loop.name}: the expert reference already uses the name `tmp`")
        body = ("    static real_t *tmp;\n"
                "    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));\n" + body.replace("pb_tmp", "tmp"))
    if re.search(r"\b(malloc|calloc|free)\s*\(", body):
        includes += "#include <stdlib.h>\n"
    if "omp_get" in body:
        includes += "#include <omp.h>\n"
    return body, includes


def render_v5_kernel(loop: Loop, expert: bool = False) -> str:
    """The benchmark's own file (v5) — or, with `expert`, the reference solution as the same file."""
    _category, decls, rep, ret = _loop_function(loop)
    kernel_globals = "" if _is_harness_global(loop.globals_) else _no_comments(loop.globals_)
    param = V5_PARAMS.get(loop.name, ("void", ""))[0]
    if expert:
        if loop.expert is None:
            raise ValueError(f"{loop.name}: no expert reference (class {loop.expected})")
        body, includes = _v5_expert_body(loop)
    else:
        pre = "\n".join(l for l in loop.pre.splitlines() if "pb_" not in l)      # a harness binding is the parameter
        body = "\n".join(x for x in (_no_comments(pre), _no_comments(decls), _no_comments(_dedent4(rep)),
                                     f"    return {ret};") if x)
        includes = "#include <stdlib.h>\n" if re.search(r"\bexit\s*\(", rep) else ""     # s481 calls exit()
    return (includes + f'#include "{V5_HEADER}"\n' + ("\n" + kernel_globals + "\n" if kernel_globals else "")
            + f"\nreal_t kernel_{loop.name}({param})\n{{\n" + body + "\n}\n")


def render_v5_main(loop: Loop) -> str:
    """main.c: ours, inside the package so that DiscoPoP instruments it; no comment — a model can read it."""
    mix = "\n".join(l for l in PB_MIX.strip("\n").splitlines() if not l.lstrip().startswith(("/*", "*")))
    arg = V5_PARAMS.get(loop.name, ("", ""))[1]
    return (f'#include "{V5_HEADER}"\n#include "{loop.suite}/{loop.name}.h"\n\n' + mix + "\n\n"
            "int main(int argc, char** argv)\n{\n"
            "  if (pb_setup(argc, argv)) return 1;\n"
            "  pb_timer_start();\n"
            "  real_t pb_result = (real_t)0;\n"
            "  for (int nl = 0; nl < R; nl++) {\n"
            f"    pb_result = kernel_{loop.name}({arg});\n"
            "    pb_mix(nl);\n"
            "  }\n"
            "  pb_timer_stop();\n"
            "  pb_finish(pb_result);\n"
            "  return 0;\n}\n")


def render_v5_harness(loop: Loop) -> str:
    """The measurement header outside the package (v5): v4's without `PB_MAIN`, the type and the sizes (they
    are data.h's, included first), and with the data the function uses given external linkage."""
    _decl, defn = _v5_split_globals(loop)
    data = DATA % {"init_extra": loop.init_extra, "harness_globals": "".join(l + "\n" for l in defn)}
    data = _exact(data, "static real_t *a, *b, *c, *d, *e;", "real_t *a, *b, *c, *d, *e;")
    data = _exact(data, "#ifdef PB_EXPERT_TMP\nstatic real_t *pb_tmp;   /* an expert reference's scratch vector */\n#endif\n", "")
    driver = (DRIVER % {"emit_extra": loop.emit_extra}).split("/* `main`, expanded", 1)[0]
    driver = _exact(driver, "#ifdef PB_EXPERT_TMP\n  pb_tmp = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));\n#endif\n", "")
    driver = _exact(driver, "/* ---- main, in the order v3's main ran it ------------------------------------------ */",
                    "/* ---- what main.c calls: set-up before the timed region, the digest after it ------- */")
    return (V5_HARNESS_HEAD % {"name": loop.name, "version": 5, "reps": loop.reps} + SCAFFOLD + data
            + driver.rstrip("\n") + "\n\n#endif\n")


def v5_files(loop: Loop) -> Dict[str, str]:
    """The package's files (v5), by name."""
    return {f"{loop.name}.c": render_v5_kernel(loop), V5_HEADER: render_v5_header(loop), V5_MAIN: render_v5_main(loop)}


def hot_loop_v5(loop: Loop) -> Dict[str, Any]:
    """meta.json's `hot_loop` (v5): the first `for` of the function that holds the loop under study — there is
    no repetition loop in the file — and what it writes, checked against the writes declared by hand."""
    entry = f"kernel_{loop.name}"
    hot = hot_loop_coverage.describe(render_v5_kernel(loop), entry, loop.hot_function or entry)
    if hot["writes"] != sorted(loop.hot_writes):
        raise ValueError(f"{loop.name}: the hot loop at line {hot['line']} writes {hot['writes']}, "
                         f"declared {sorted(loop.hot_writes)} — read the loop again")
    if loop.hot_aliases:
        hot["aliases"] = sorted(loop.hot_aliases)
    return hot


def v5_digest(files: Dict[str, str]) -> str:
    """sha256 of the package as cli._package_digest computes it for a project: every file's text, in sorted
    order of the names."""
    return hashlib.sha256("".join(files[n] for n in sorted(files)).encode()).hexdigest()


def _as_v5(loop: Loop) -> Loop:
    """A `tsvc_b1` loop as a loop of the v5 suite: the same record, with the expert reference of the TSVC
    loop of that name (the `tsvc` suite's records carry them)."""
    c = copy.copy(loop)
    c.suite = V5_SUITE
    base = BY_NAME.get(loop.name)
    c.expert = base.expert if base is not None else None
    return c


# The v5 suite: every loop of `tsvc_b1` (E1-final's 25, E2-B1's units, the constructed kernels) but V5_LEFT_OUT.
SUITES[V5_SUITE] = [_as_v5(l) for l in B1_LOOPS if l.name not in V5_LEFT_OUT]


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
    if loop.emit_extra:
        # v3's digest covers the five vectors only: a loop writing more would be checked on part of its output
        raise ValueError(f"{loop.name}: its digest needs the v4 harness (emit_extra)")
    category, decls, rep, ret = _loop_function(loop)
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


def _build_run_units(srcs: List[Path], include: Path, out: Path, flags: List[str], args: List[str],
                     threads: Optional[int], cpath: Optional[Path] = None) -> Tuple[bool, str]:
    """`_build_run` for a package of several units (v5): every unit compiled as it is, `include` on the path;
    `cpath` puts another harness directory first (the v4 rendering the output is compared with)."""
    omp = []
    if "-fopenmp" in flags and sys.platform == "darwin" and Path("/usr/local/opt/libomp").exists():
        omp = ["-I/usr/local/opt/libomp/include", "-L/usr/local/opt/libomp/lib"]
    env = dict(os.environ)
    if cpath is not None:
        env["CPATH"] = os.pathsep.join([str(cpath)] + [p for p in env.get("CPATH", "").split(os.pathsep) if p])
    r = subprocess.run([_cc(), "-O2", *_sysroot(), *flags, *omp, f"-I{include}", *map(str, srcs), "-o", str(out), "-lm"],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return False, "build: " + r.stderr[-300:]
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    r = subprocess.run([str(out), *args], capture_output=True, text=True, timeout=600, env=env)
    if r.returncode != 0:
        return False, f"run rc={r.returncode}: {r.stderr[-200:]}"
    return True, r.stdout


def validate_v5(loop: Loop, package: Path, reference: Optional[Path]) -> List[str]:
    """v5: the package runs, its output is finite and changes with the perturbed input; it is BYTE FOR BYTE
    the output of the same loop in layout v4 — the full dump on both inputs and the digest (the layout must
    not change the program; T0.16); and the expert reference, put in the benchmark's file's place and built
    with OpenMP at 4 threads, computes the same values on both inputs."""
    problems: List[str] = []
    units = [package / f"{loop.name}.c", package / V5_MAIN]
    b1 = next(l for l in B1_LOOPS if l.name == loop.name)
    with tempfile.TemporaryDirectory(prefix=f"tsvc_{loop.name}_") as tmp:
        t = Path(tmp)
        (t / "h" / b1.suite).mkdir(parents=True)
        (t / "h" / b1.suite / f"{b1.name}.h").write_text(render_harness(b1))
        (t / f"{b1.name}_v4.c").write_text(render(b1))
        outs: Dict[str, str] = {}
        for tag, flags, args in (("default", ["-DPB_FULL_DUMP"], []), ("seeded", ["-DPB_FULL_DUMP"], ["7"]),
                                 ("digest", [], [])):
            ok, out = _build_run_units(units, package, t / "orig", [*flags, "-DSMALL_DATASET"], args, None)
            if not ok:
                return [f"original ({tag}): {out}"]
            outs[tag] = out
            if tag != "digest" and any(v != v or abs(v) == float("inf") for v in map(float, out.split())):
                problems.append(f"original ({tag}): non-finite values")
            ok, old = _build_run_units([t / f"{b1.name}_v4.c"], t, t / "v4", [*flags, "-DSMALL_DATASET"], args, None,
                                       cpath=t / "h")
            if not ok:
                problems.append(f"layout v4 ({tag}): {old}")
            elif old != out:
                problems.append(f"the output differs from layout v4's ({tag})")
        if outs["default"] == outs["seeded"]:
            problems.append("the perturbed input does not change the output")
        ok, again = _build_run_units(units, package, t / "orig", ["-DPB_FULL_DUMP", "-DSMALL_DATASET"], [], None)
        if ok and again != outs["default"]:
            problems.append("the original is not deterministic")
        if reference is not None:
            for tag, args in (("default", []), ("seeded", ["7"])):
                ok, out = _build_run_units([reference, package / V5_MAIN], package, t / "ref",
                                           ["-DPB_FULL_DUMP", "-DSMALL_DATASET", "-fopenmp"], args, 4)
                if not ok:
                    problems.append(f"reference ({tag}): {out}")
                    continue
                err = _max_rel(outs[tag], out)
                if err > 1e-9:
                    problems.append(f"reference ({tag}) differs from the original: max rel err {err:.2e}")
    return problems


def write_v5(loop: Loop, out: Path, harness_root: Path, refs: Path, check: bool) -> Tuple[List[str], bool]:
    """One v5 package: its three files, the header outside it, the reference, meta.json. Returns
    (validation problems, validated)."""
    d = out / loop.name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    files = v5_files(loop)
    for fname, text in files.items():
        (d / fname).write_text(text)
    hdr = harness_root / loop.suite / f"{loop.name}.h"
    hdr.write_text(render_v5_harness(loop))
    ref: Optional[Path] = None
    if loop.expert is not None:
        ref = refs / f"{loop.name}.c"
        ref.write_text(render_v5_kernel(loop, expert=True))
    (d / "meta.json").write_text(json.dumps({
        "suite": loop.suite, "kernel": loop.name,
        "source": (loop.source or ("constructed: ORDER-2 (THESIS_EXPERIMENTS §6, 28 Sep; tools/evidence_pilot.py)"
                                   if loop.body else "benchmarks/TSVC_2/src/tsvc.c")),
        "category": _loop_function(loop)[0], "file": f"{loop.name}.c", "language": "c", "layout": "project",
        # `editable`: the one file a model's changes are taken from — the agent, its twin and the model alone
        # alike; the judge marks a trial that changed any other file
        "project": {"units": [f"{loop.name}.c", V5_MAIN], "include_dirs": ["."], "editable": [f"{loop.name}.c"]},
        "restructuring_class": loop.expected, "transformation": loop.transformation, "why": loop.why,
        "reference_solution": (str(ref.relative_to(HARNESS_ROOT)) if ref.is_relative_to(HARNESS_ROOT)
                               else str(ref)) if ref else None,
        # the functions of main.c: nothing in them is the benchmark's (the agent's queue leaves them out)
        "exclude_functions": ["main", "pb_mix"],
        "harness": f"{loop.suite}/{loop.name}.h",
        "harness_sha256": hashlib.sha256(hdr.read_bytes()).hexdigest(),
        "hot_loop": hot_loop_v5(loop),
        "agent_dataset": "SMALL", "generator_version": 5,
        "inputs_sha256": hashlib.sha256(TSVC.read_bytes()).hexdigest(),
        "output_sha256": v5_digest(files),
    }, indent=2) + "\n")
    return (validate_v5(loop, d, ref) if check else []), check


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help=f"default: all {len(LOOPS)}")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--harness-out", type=Path, default=None,
                    help="where the measurement headers go (default: <out>/../_harness — outside every "
                         "package, D39); builds find them through CPATH (harness_include.py)")
    ap.add_argument("--references-out", type=Path, default=REFERENCES,
                    help="where the expert references go (default: the tracked agent/reference_solutions/tsvc)")
    ap.add_argument("--layout", choices=("v3", "v4", "v5"), default="v3",
                    help="v3 (default): the one-file layout of E1 and E2; v4 (D39): the measurement in a "
                         "header outside the package — E2-B1 to E2-O3; v5 (the author, 4 Oct): the benchmark's "
                         "file holds only the loop's function, `main` in a second file (suite tsvc_c1)")
    ap.add_argument("--suite", choices=sorted(SUITES), default="tsvc",
                    help="which loops: `tsvc` (E1-E2, v3 or v4), `tsvc_b1` (v4 only) or `tsvc_c1` (v5 only)")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    if (a.suite == V5_SUITE) != (a.layout == "v5"):
        ap.error(f"layout v5 and suite {V5_SUITE} go together")
    if a.suite == "tsvc_b1" and a.layout != "v4":
        ap.error(f"--suite {a.suite} is packaged in layout v4 only")
    loops = SUITES[a.suite]
    by_name = {l.name: l for l in loops}
    unknown = [n for n in a.names if n not in by_name]
    if unknown:
        ap.error(f"not in suite {a.suite}: {', '.join(unknown)}")
    harness_root = (a.harness_out or a.out.parent / "_harness").resolve()
    refs: Path = a.references_out
    if a.layout == "v5" and refs == REFERENCES:
        refs = REFERENCES.parent / V5_SUITE          # a reference is the benchmark's FILE of this layout
    # The validation builds must find the headers exactly as every other build does.
    os.environ["CPATH"] = os.pathsep.join([str(harness_root)] + [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p])
    failed = 0
    refs.mkdir(parents=True, exist_ok=True)
    if a.layout in ("v4", "v5"):
        (harness_root / a.suite).mkdir(parents=True, exist_ok=True)
    for loop in [by_name[n] for n in a.names] if a.names else loops:
        if a.layout == "v5":
            problems, checked = write_v5(loop, a.out, harness_root, refs, a.validate)
            failed += bool(problems)
            note = ("  OK" if not problems else "  FAILED: " + "; ".join(problems)) if checked else ""
            print(f"{loop.name:7s} {loop.expected:11s} {loop.transformation[:52]:52s}{note}", flush=True)
            continue
        d = a.out / loop.name
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        src = d / f"{loop.name}.c"
        v4 = a.layout == "v4"
        src.write_text(render(loop) if v4 else render_v3(loop))
        hdr = harness_root / loop.suite / f"{loop.name}.h"
        if v4:
            hdr.write_text(render_harness(loop))
        ref: Optional[Path] = None
        if loop.expert is not None:
            ref = refs / f"{loop.name}.c"
            ref.write_text(render(loop, expert=True) if v4 else render_v3(loop, expert=True))
        category = _loop_function(loop)[0]
        hot = hot_loop(loop) if v4 else None
        (d / "meta.json").write_text(json.dumps({
            "suite": loop.suite, "kernel": loop.name,
            "source": (loop.source or ("constructed: ORDER-2 (THESIS_EXPERIMENTS §6, 28 Sep; tools/evidence_pilot.py)"
                                       if loop.body else "benchmarks/TSVC_2/src/tsvc.c")),
            "category": category, "file": src.name, "language": "c", "layout": "single",
            "restructuring_class": loop.expected, "transformation": loop.transformation, "why": loop.why,
            "reference_solution": (str(ref.relative_to(HARNESS_ROOT)) if ref.is_relative_to(HARNESS_ROOT)
                                   else str(ref)) if ref else None,
            **({
                # v4: the harness's code is not in the package: `main` (PB_MAIN) and `pb_mix`
                # are the only functions of the file that are not the benchmark's.
                "exclude_functions": ["main", "pb_mix"],
                "harness": f"{loop.suite}/{loop.name}.h",
                "harness_sha256": hashlib.sha256(hdr.read_bytes()).hexdigest(),
                "protected": protected_lines(loop),
                "protected_note": protected_note(loop),
                # E2-B1 only: the loop the primary outcome's coverage check looks for (hot_loop above)
                **({"hot_loop": hot} if hot else {}),
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
    print(f"{len(a.names) or len(loops)} loops -> {a.out} (harness headers in {harness_root / a.suite})"
          + (f"   ({failed} failed validation)" if a.validate else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
