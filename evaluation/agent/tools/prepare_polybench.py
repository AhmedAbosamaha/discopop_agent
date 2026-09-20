#!/usr/bin/env python3
"""Turn a PolyBench/C 3.2 kernel into one self-contained source file the agent can take.

Why this exists
---------------
The DiscoPoP agent builds exactly one source file (C with ``clang``, C++ with
``clang++``) and judges correctness by comparing the program's **stdout**. A
PolyBench kernel breaks both assumptions: it needs ``utilities/polybench.{h,c}``
as a second translation unit plus ``-I`` paths, and it prints its results to
**stderr** (and only when ``POLYBENCH_DUMP_ARRAYS`` is defined). Run as-is, the
agent would see empty stdout and its correctness gate would compare nothing.

The output is always C, the suite's own language. The kernel code is never
translated to another language: a translation changes what DiscoPoP instruments,
so it would no longer be the same benchmark.

What the generated file contains, in order
------------------------------------------
1. The kernel's own system includes, plus ``<stdlib.h>``.
2. A default dataset (the *agent* size) that applies only when no
   ``-D*_DATASET`` is given, so the SAME file can later be rebuilt at a larger
   size for independent timing (``-DLARGE_DATASET``) without regenerating it.
3. ``POLYBENCH_DUMP_ARRAYS`` defined, so the output code is live.
4. ``polybench.h`` verbatim (macros only).
5. The only two functions the kernels use from ``polybench.c``
   (``xmalloc``, ``polybench_alloc_data``), so no second translation unit is needed.
6. The kernel header and body, with ``#include`` lines and the polyhedral
   ``#pragma scop/endscop`` markers removed, and every result print rewritten:

   * default build: each printed value is folded into a digest, and three lines
     (value count, sum, position-weighted sum, ``%.17g``) go to stdout at exit.
     The weighted sum catches values that are right but in the wrong place.
     The digest keeps stdout small — a full dump of 2mm at STANDARD is 23 MB,
     and the agent's gate captures stdout on every run.
   * ``-DPB_FULL_DUMP``: the original ``DATA_PRINTF_MODIFIER`` dump, but to
     stdout. Used by ``--validate`` to prove the conversion is exact, and by the
     independent verifier after a run.

Usage
-----
    prepare_polybench.py --out agent/prepared/polybench [--size SMALL] [kernel ...]
    prepare_polybench.py --out ... --validate          # compile + compare all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

HARNESS_ROOT = Path(__file__).resolve().parents[2]
POLYBENCH = HARNESS_ROOT / "benchmarks" / "polybench-c-3.2"
DATASETS = ["MINI", "SMALL", "STANDARD", "LARGE", "EXTRALARGE"]
GENERATOR_VERSION = 5  # v2: C only; v3: optional perturbed input; v4: timed kernel region; v5: project layout

_DIGEST_AND_DUMP = r"""
/* ---- output: digest by default, full dump with -DPB_FULL_DUMP ------------ */
#ifdef PB_FULL_DUMP
# define pb_emit(v) fprintf(stdout, DATA_PRINTF_MODIFIER, v)
# define pb_newline() fprintf(stdout, "\n")
# define pb_report() ((void)0)
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
# define pb_newline() ((void)0)
static void pb_report(void)
{
  printf("pb_values %llu\n", pb_count);
  printf("pb_sum %.17g\n", pb_sum);
  printf("pb_wsum %.17g\n", pb_wsum);
}
#endif
"""

_PERTURB = r"""
/* ---- optional perturbed input: argv[1] = seed ------------------------------
   Some shipped inputs are fixed points of their own kernels (seidel-2d starts from a
   bilinear field that both a Gauss-Seidel and a Jacobi sweep leave unchanged), so an
   output check on them cannot tell a changed algorithm from the original. With a
   seed, every array gets deterministic noise in [0, 3) right after init_array. */
static unsigned long long pb_seed(const char* s)
{
  return strtoull(s, NULL, 10) * 0x9E3779B97F4A7C15ULL + 1ULL;
}
static double pb_uniform(unsigned long long* state)
{
  *state = *state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (double)(*state >> 11) / 9007199254740992.0;
}
#define PB_PERTURB(arr, count)                                              \
  do {                                                                      \
    DATA_TYPE* pb_p = (DATA_TYPE*)(arr);                                    \
    unsigned long long pb_k, pb_n = (unsigned long long)(count);            \
    for (pb_k = 0; pb_k < pb_n; pb_k++)                                     \
      pb_p[pb_k] += (DATA_TYPE)(pb_uniform(&pb_state) * 3.0);               \
  } while (0)
"""

_TIMER = r"""
/* ---- timed region: the kernel only ------------------------------------------
   PolyBench's own convention (POLYBENCH_TIME) times the kernel between
   polybench_start_instruments and polybench_stop_instruments, excluding allocation,
   initialisation and output. The elapsed time goes to stderr as
   "DP_TIMED_REGION_SECONDS <s>" so stdout stays deterministic; the agent's gate and
   the harness read it and fall back to whole-program time when it is absent. */
static struct timespec pb_t0;
static void pb_timer_start(void)
{
  clock_gettime(CLOCK_MONOTONIC, &pb_t0);
}
static void pb_timer_stop(void)
{
  struct timespec t1;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  fprintf(stderr, "DP_TIMED_REGION_SECONDS %.9f\n",
          (double)(t1.tv_sec - pb_t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - pb_t0.tv_nsec));
}
"""

_ALLOC = r"""
/* ---- from utilities/polybench.c: the only functions the kernels call ------- */
static void* xmalloc(size_t num)
{
  void* ptr = NULL;
  int ret = posix_memalign(&ptr, 32, num);
  if (!ptr || ret)
    {
      fprintf(stderr, "[PolyBench] posix_memalign: cannot allocate memory");
      exit(1);
    }
  return ptr;
}

void* polybench_alloc_data(unsigned long long int n, int elt_size)
{
  size_t val = n;
  val *= elt_size;
  return xmalloc(val);
}
"""

_PRINT_VALUE = re.compile(r"fprintf\s*\(\s*stderr\s*,\s*DATA_PRINTF_MODIFIER\s*,\s*(.+?)\)\s*;")
_PRINT_NEWLINE = re.compile(r'fprintf\s*\(\s*stderr\s*,\s*"\\n"\s*\)\s*;')
_INCLUDE = re.compile(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"].*$", re.M)
_SCOP = re.compile(r"^\s*#\s*pragma\s+(end)?scop\s*$\n?", re.M)


def discover() -> Dict[str, Path]:
    """Kernel name -> kernel directory: every directory of the suite that holds `<name>.c` and
    `<name>.h` (PolyBench's own layout; `utilities/` has neither). Until 2026-09-20 this went
    through the config directories the group's harness keeps beside each kernel
    (`.discopop/project/configs`); those are not part of PolyBench and are not in this
    repository — a fresh clone found no kernel at all. Same 30 kernels either way."""
    found = {}
    for c_file in sorted(POLYBENCH.glob("**/*.c")):
        kdir = c_file.parent
        if c_file.stem == kdir.name and (kdir / f"{kdir.name}.h").exists():
            found[kdir.name] = kdir
    return found


def _sha256(paths: List[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()


def generate(name: str, kdir: Path, agent_size: str) -> str:
    c_src = (kdir / f"{name}.c").read_text()
    h_src = (kdir / f"{name}.h").read_text()
    pb_h = (POLYBENCH / "utilities" / "polybench.h").read_text()

    system_includes = [inc for inc in _INCLUDE.findall(c_src)
                       if inc != "polybench.h" and inc != f"{name}.h"]
    for needed in ("stdlib.h", "time.h"):
        if needed not in system_includes:
            system_includes.append(needed)

    body = _INCLUDE.sub("", c_src)
    body = _SCOP.sub("", body)
    n_values = len(_PRINT_VALUE.findall(body))
    body = _PRINT_VALUE.sub(r"pb_emit(\1);", body)
    body = _PRINT_NEWLINE.sub("pb_newline();", body)
    for marker, call in (("polybench_start_instruments", "pb_timer_start();"),
                         ("polybench_stop_instruments", "pb_timer_stop();")):
        body, n = re.subn(rf"{marker}\s*;", call, body)
        if n != 1:
            raise ValueError(f"{name}: expected one `{marker};`, found {n}")
    if n_values == 0 or "fprintf" in body and re.search(r"fprintf\s*\(\s*stderr", body):
        raise ValueError(f"{name}: unexpected print shape — refusing to generate a file "
                         f"whose output might not reach stdout")

    main_at = body.find("int main(")
    if main_at < 0:
        raise ValueError(f"{name}: no main()")

    # Perturbed input: after the one init_array call in main, add noise to every array
    # main declares (all are DATA_TYPE heap blocks of the static dimensions).
    perturb = []
    for nd, argstr in re.findall(r"POLYBENCH_(\d)D_ARRAY_DECL\s*\(([^;]*)\)\s*;", body[main_at:]):
        parts = [p.strip() for p in argstr.split(",")]
        var, typ, dims = parts[0], parts[1], parts[2:2 + int(nd)]
        if typ != "DATA_TYPE":
            raise ValueError(f"{name}: array {var} is {typ}, not DATA_TYPE")
        count = " * ".join(f"({d} + POLYBENCH_PADDING_FACTOR)" for d in dims)
        perturb.append(f"      PB_PERTURB({var}, {count});")
    init = re.compile(r"init_array\s*\([^;]*\)\s*;", re.S).search(body, main_at)
    if init is None or not perturb:
        raise ValueError(f"{name}: no init_array call or no arrays in main")
    block = ("\n\n  /* Optional perturbed input, see PB_PERTURB. */\n"
             "  if (argc > 1)\n    {\n      unsigned long long pb_state = pb_seed(argv[1]);\n"
             + "\n".join(perturb) + "\n    }\n")
    body = body[:init.end()] + block + body[init.end():]

    # The digest is printed once, just before main returns.
    ret_at = body.rfind("return 0;")
    if ret_at < main_at:
        raise ValueError(f"{name}: could not find main's final `return 0;`")
    body = body[:ret_at] + "pb_report();\n\n  " + body[ret_at:]

    guard = " && ".join(f"!defined({d}_DATASET)" for d in DATASETS)
    header = (
        f"/* Generated by agent/tools/prepare_polybench.py (v{GENERATOR_VERSION}) from\n"
        f" * PolyBench/C 3.2 {kdir.relative_to(POLYBENCH)}/{name}.c — do not edit by hand.\n"
        f" * Default dataset {agent_size}; override with -D<SIZE>_DATASET.\n"
        f" * Prints a value digest to stdout; -DPB_FULL_DUMP prints every value. */\n"
    )
    parts = [
        header,
        "\n".join(f"#include <{inc}>" for inc in system_includes),
        f"\n#if {guard}\n# define {agent_size}_DATASET\n#endif\n",
        "#define POLYBENCH_DUMP_ARRAYS\n",
        pb_h,
        _ALLOC,
        h_src,
        _DIGEST_AND_DUMP,
        _PERTURB,
        _TIMER,
        body,
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Project layout: the kernel in its original files, the harness in one header
# ---------------------------------------------------------------------------
# Decision D6 (THESIS_EXPERIMENTS.md §5g): merging is no longer needed.  The kernel keeps its
# own file, `<kernel>.h`, `polybench.h` and `polybench.c` are copied VERBATIM, and everything
# the harness adds — digest/dump, perturbed input, timed region, the default dataset — is
# one header, `pb_harness.h`, included at the top of the kernel file.  The edits to the
# kernel file are the same three as before (prints to pb_emit, timers to pb_timer_*, the
# perturbation block and the report in main); nothing else moves.  The `#pragma scop`
# markers stay, as in the original.

POLYBENCH_C_FUNCTIONS = ["rtclock", "polybench_flush_cache", "polybench_linux_fifo_scheduler",
                         "polybench_linux_standard_scheduler", "test_fail", "polybench_papi_init",
                         "polybench_papi_close", "polybench_papi_start_counter",
                         "polybench_papi_stop_counter", "polybench_papi_print",
                         "polybench_prepare_instruments", "polybench_timer_start",
                         "polybench_timer_stop", "polybench_timer_print", "xmalloc",
                         "polybench_alloc_data"]
PROJECT_UNITS = lambda name: [f"{name}.c", "polybench.c"]   # noqa: E731


def _edit_kernel(name: str, c_src: str) -> str:
    """The kernel file with the harness's three edits, and nothing else touched."""
    body = c_src
    n_values = len(_PRINT_VALUE.findall(body))
    body = _PRINT_VALUE.sub(r"pb_emit(\1);", body)
    body = _PRINT_NEWLINE.sub("pb_newline();", body)
    for marker, call in (("polybench_start_instruments", "pb_timer_start();"),
                         ("polybench_stop_instruments", "pb_timer_stop();")):
        body, n = re.subn(rf"{marker}\s*;", call, body)
        if n != 1:
            raise ValueError(f"{name}: expected one `{marker};`, found {n}")
    if n_values == 0 or re.search(r"fprintf\s*\(\s*stderr", body):
        raise ValueError(f"{name}: unexpected print shape — refusing to generate a file "
                         f"whose output might not reach stdout")
    main_at = body.find("int main(")
    if main_at < 0:
        raise ValueError(f"{name}: no main()")
    perturb = []
    for nd, argstr in re.findall(r"POLYBENCH_(\d)D_ARRAY_DECL\s*\(([^;]*)\)\s*;", body[main_at:]):
        parts = [p.strip() for p in argstr.split(",")]
        var, typ, dims = parts[0], parts[1], parts[2:2 + int(nd)]
        if typ != "DATA_TYPE":
            raise ValueError(f"{name}: array {var} is {typ}, not DATA_TYPE")
        count = " * ".join(f"({d} + POLYBENCH_PADDING_FACTOR)" for d in dims)
        perturb.append(f"      PB_PERTURB({var}, {count});")
    init = re.compile(r"init_array\s*\([^;]*\)\s*;", re.S).search(body, main_at)
    if init is None or not perturb:
        raise ValueError(f"{name}: no init_array call or no arrays in main")
    block = ("\n\n  /* Optional perturbed input, see PB_PERTURB. */\n"
             "  if (argc > 1)\n    {\n      unsigned long long pb_state = pb_seed(argv[1]);\n"
             + "\n".join(perturb) + "\n    }\n")
    body = body[:init.end()] + block + body[init.end():]
    ret_at = body.rfind("return 0;")
    if ret_at < main_at:
        raise ValueError(f"{name}: could not find main's final `return 0;`")
    body = body[:ret_at] + "pb_report();\n\n  " + body[ret_at:]
    # The harness header goes in front of polybench.h: it sets the default dataset that
    # <kernel>.h reads, and defines POLYBENCH_DUMP_ARRAYS so the output code is live.
    inc = re.search(r'^\s*#\s*include\s*[<"]polybench\.h[>"].*$', body, re.M)
    if inc is None:
        raise ValueError(f"{name}: no `#include <polybench.h>`")
    body = body[:inc.start()] + '#include "pb_harness.h"\n' + body[inc.start():]
    return body


def generate_project(name: str, kdir: Path, agent_size: str) -> Dict[str, str]:
    """{relative path: text} for the project layout of one kernel."""
    guard = " && ".join(f"!defined({d}_DATASET)" for d in DATASETS)
    harness = (
        f"/* Generated by agent/tools/prepare_polybench.py (v{GENERATOR_VERSION}) — the harness's own\n"
        f" * code, kept out of the kernel file: output digest (full dump with -DPB_FULL_DUMP),\n"
        f" * optional perturbed input (argv[1] = seed), the timed region, and the default\n"
        f" * dataset ({agent_size}; override with -D<SIZE>_DATASET).  Included by {name}.c only. */\n"
        "#ifndef PB_HARNESS_H\n#define PB_HARNESS_H\n"
        "#include <stdio.h>\n#include <stdlib.h>\n#include <time.h>\n"
        f"\n#if {guard}\n# define {agent_size}_DATASET\n#endif\n"
        "#define POLYBENCH_DUMP_ARRAYS\n"
        + _DIGEST_AND_DUMP + _PERTURB + _TIMER + "\n#endif /* PB_HARNESS_H */\n")
    return {
        f"{name}.c": _edit_kernel(name, (kdir / f"{name}.c").read_text()),
        f"{name}.h": (kdir / f"{name}.h").read_text(),
        "polybench.h": (POLYBENCH / "utilities" / "polybench.h").read_text(),
        "polybench.c": (POLYBENCH / "utilities" / "polybench.c").read_text(),
        "pb_harness.h": harness,
    }


# ---------------------------------------------------------------------------
# Validation: the converted file must print exactly what the original prints
# ---------------------------------------------------------------------------

def _sdk_flags() -> List[str]:
    if platform.system() != "Darwin":
        return []
    try:
        sdk = subprocess.check_output(["xcrun", "--show-sdk-path"], text=True,
                                      stderr=subprocess.DEVNULL).strip()
        return ["-isysroot", sdk] if sdk else []
    except (OSError, subprocess.CalledProcessError):
        return []


def _find(candidates: List[str]) -> Optional[str]:
    for c in candidates:
        found = shutil.which(c)
        if found:
            return found
    return None


def _build(cmd: List[str], cwd: Path) -> Optional[str]:
    r = subprocess.run(cmd + _sdk_flags(), cwd=cwd, capture_output=True, text=True)
    return None if r.returncode == 0 else (r.stderr.strip().splitlines() or ["?"])[-1]


def _run(binary: Path, stream: str, timeout: int = 600,
         args: Optional[List[str]] = None) -> "tuple[int, str, float]":
    t0 = time.perf_counter()
    r = subprocess.run([str(binary), *(args or [])], capture_output=True, text=True,
                       timeout=timeout)
    return r.returncode, getattr(r, stream), time.perf_counter() - t0


def validate(name: str, kdir: Path, cpp: Path, work: Path, cc: str, cxx: str,
             sizes: List[str]) -> dict:
    """Original C (stderr dump) vs converted C++ (stdout full dump) must be identical,
    and the digest build must run and print its three lines."""
    work.mkdir(parents=True, exist_ok=True)
    row: dict = {"kernel": name}
    for size in sizes:
        orig_bin = work / f"orig_{size}"
        err = _build([cc, "-O2", f"-I{POLYBENCH / 'utilities'}", f"-I{kdir}",
                      f"-D{size}_DATASET", "-DPOLYBENCH_DUMP_ARRAYS",
                      str(POLYBENCH / "utilities" / "polybench.c"), str(kdir / f"{name}.c"),
                      "-lm", "-o", str(orig_bin)], work)
        if err:
            row[size] = f"original build failed: {err}"
            continue
        dump_bin, digest_bin = work / f"dump_{size}", work / f"digest_{size}"
        if cpp.is_dir():                                  # project layout
            conv, link = cc, ["-lm"]
            inputs = [str(cpp / u) for u in PROJECT_UNITS(name)] + [f"-I{cpp}"]
        else:
            is_c = cpp.suffix == ".c"
            conv, link = (cc, ["-lm"]) if is_c else (cxx, [])
            inputs = [str(cpp)]
        err = _build([conv, "-O2", f"-D{size}_DATASET", "-DPB_FULL_DUMP", *inputs,
                      "-o", str(dump_bin), *link], work)
        err = err or _build([conv, "-O2", f"-D{size}_DATASET", *inputs, "-o", str(digest_bin),
                             *link], work)
        if err:
            row[size] = f"converted build failed: {err}"
            continue
        rc_o, out_o, _ = _run(orig_bin, "stderr")
        rc_d, out_d, _ = _run(dump_bin, "stdout")
        rc_g, out_g, t_g = _run(digest_bin, "stdout")
        same = rc_o == 0 and rc_d == 0 and out_o == out_d and len(out_o) > 0
        digest_ok = rc_g == 0 and out_g.count("\n") == 3 and out_g.startswith("pb_values ")
        # Perturbed input: deterministic, and actually different from the shipped input.
        rc_s1, out_s1, _ = _run(digest_bin, "stdout", args=["7"])
        rc_s2, out_s2, _ = _run(digest_bin, "stdout", args=["7"])
        row[size] = {"dump_identical": same, "dump_bytes": len(out_o),
                     "digest_ok": digest_ok, "digest_run_s": round(t_g, 3),
                     "perturb_deterministic": rc_s1 == 0 and rc_s2 == 0 and out_s1 == out_s2,
                     "perturb_changes_output": out_s1 != out_g,
                     "perturb_finite": not re.search(r"nan|inf", out_s1, re.I)}
    return row


def main() -> int:
    kernels = discover()
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("kernels", nargs="*", help=f"default: all {len(kernels)}")
    p.add_argument("--out", required=True, type=Path, help="output directory")
    p.add_argument("--size", default="SMALL", choices=DATASETS,
                   help="default dataset baked into the file (the size the agent runs at)")
    p.add_argument("--validate", action="store_true",
                   help="compile original and converted builds and compare their output")
    p.add_argument("--validate-sizes", default="MINI,SMALL")
    p.add_argument("--layout", choices=["project", "single"], default="project",
                   help=("project (default since D6): the kernel in its original files plus "
                         "pb_harness.h; single: the earlier one-file merge, for comparison studies"))
    a = p.parse_args()
    a.out = a.out.resolve()        # the validator builds with cwd elsewhere

    unknown = set(a.kernels) - set(kernels)
    if unknown:
        print(f"unknown kernel(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    selected = a.kernels or list(kernels)

    cc = _find(["clang-20", "clang-19", "clang"]) if a.validate else None
    cxx = _find(["clang++-20", "clang++-19", "clang++"]) if a.validate else None
    if a.validate and not (cc and cxx):
        print("--validate needs clang and clang++ on PATH", file=sys.stderr)
        return 2

    failures = 0
    rows = []
    for name in selected:
        kdir = kernels[name]
        out_dir = a.out / name
        if out_dir.exists():
            shutil.rmtree(out_dir)                 # never mix the two layouts in one directory
        out_dir.mkdir(parents=True, exist_ok=True)
        inputs = [kdir / f"{name}.c", kdir / f"{name}.h", POLYBENCH / "utilities" / "polybench.h"]
        # Not the computation under study (PolyBench times the kernel only): output, setup,
        # allocation, the suite's own utilities and the packaging's helpers — and `main`,
        # which in every PolyBench kernel holds only calls to those (D4, from T0.5/T0.6).
        # Passed to the agent as --exclude-functions so they cannot win model calls.
        excluded = ["print_array", "init_array", "main",
                    "pb_emit", "pb_report", "pb_seed", "pb_uniform",
                    "pb_timer_start", "pb_timer_stop"]
        try:
            if a.layout == "project":
                files = generate_project(name, kdir, a.size)
                for rel, text in files.items():
                    (out_dir / rel).write_text(text)
                cpp = out_dir                        # the validator builds the directory
                digest_of = "".join(files[k] for k in sorted(files)).encode()
                excluded += POLYBENCH_C_FUNCTIONS
            else:
                cpp = out_dir / f"{name}.c"
                cpp.write_text(generate(name, kdir, a.size))
                digest_of = cpp.read_bytes()
                excluded += ["xmalloc", "polybench_alloc_data"]
        except ValueError as e:
            print(f"  FAIL  {name}: {e}")
            failures += 1
            continue
        meta = {
            "suite": "polybench-c-3.2", "kernel": name,
            "source": str(kdir.relative_to(HARNESS_ROOT)),
            "category": str(kdir.relative_to(POLYBENCH).parent),
            "file": f"{name}.c", "language": "c",
            "layout": a.layout,
            "exclude_functions": excluded,
            "agent_dataset": a.size, "generator_version": GENERATOR_VERSION,
            "inputs_sha256": _sha256(inputs + [POLYBENCH / "utilities" / "polybench.c"]),
            "output_sha256": hashlib.sha256(digest_of).hexdigest(),
        }
        if a.layout == "project":
            meta["project"] = {"units": PROJECT_UNITS(name), "include_dirs": ["."]}
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        if not a.validate:
            print(f"  ok    {name} -> {out_dir}")
            continue
        assert cc is not None and cxx is not None
        row = validate(name, kdir, cpp, out_dir / "validate", cc, cxx, a.validate_sizes.split(","))
        rows.append(row)
        bad = [s for s in a.validate_sizes.split(",")
               if not (isinstance(row.get(s), dict) and row[s]["dump_identical"] and row[s]["digest_ok"]
                       and row[s]["perturb_deterministic"] and row[s]["perturb_changes_output"])]
        failures += bool(bad)
        detail = "  ".join(
            f"{s}:{'identical' if isinstance(row[s], dict) and row[s]['dump_identical'] else row[s]}"
            f"({row[s]['digest_run_s']}s)" if isinstance(row[s], dict) else f"{s}:{row[s]}"
            for s in a.validate_sizes.split(","))
        print(f"  {'FAIL' if bad else 'ok  '}  {name:18} {detail}")
        shutil.rmtree(out_dir / "validate", ignore_errors=True)

    if a.validate:
        (a.out / "validation.json").write_text(json.dumps(
            {"cc": cc, "cxx": cxx, "sizes": a.validate_sizes.split(","), "rows": rows}, indent=2) + "\n")
    print(f"\n{len(selected) - failures}/{len(selected)} kernels OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
