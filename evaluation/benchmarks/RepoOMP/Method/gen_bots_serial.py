#!/usr/bin/env python3
"""Generate BOTS serial baselines from omp-tasks versions.

Strategy: copy each omp-tasks benchmark dir, strip all #pragma omp lines
from .c files. Verification logic (KERNEL_CHECK + verify funcs + _seq funcs)
lives in app-desc.h and .c, preserved. Stripping pragmas turns task-parallel
code into serial recursive code with identical results.
"""
import re, shutil, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BOTS = os.path.join(ROOT, "..", "benchmark", "bots")
SRC = os.path.join(BOTS, "omp-tasks")
DST = os.path.join(BOTS, "serial_repo")

# BOTS_SOURCE paths (relative to omp-tasks)
SOURCES = {
    "alignment": "alignment/alignment_for/alignment.c",
    "fft": "fft/fft.c",
    "floorplan": "floorplan/floorplan.c",
    "health": "health/health.c",
    "nqueens": "nqueens/nqueens.c",
    "sort": "sort/sort.c",
    "sparselu": "sparselu/sparselu_for/sparselu.c",
    "strassen": "strassen/strassen.c",
}

PRAGMA_RE = re.compile(r"^\s*#\s*pragma\s+omp\b")

def strip_pragmas(text):
    """Remove #pragma omp lines including backslash-continuation lines.
    Keep braces (becomes plain block)."""
    lines = text.splitlines(keepends=True)
    out = []
    skip_cont = False
    for line in lines:
        if skip_cont:
            # continuation line of a pragma (ends with backslash)
            if line.rstrip().endswith("\\"):
                continue
            skip_cont = False
            continue
        if PRAGMA_RE.match(line):
            if line.rstrip().endswith("\\"):
                skip_cont = True
            continue
        out.append(line)
    return "".join(out)

def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)
    # copy common, run, config, inputs, templates (dirs) + Makefile, Makefile.version (files)
    for item in ["common", "run", "config", "inputs", "templates"]:
        s = os.path.join(BOTS, item)
        d = os.path.join(DST, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks=True)
    for item in ["Makefile"]:
        s = os.path.join(BOTS, item)
        d = os.path.join(DST, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
    # Makefile.version: copy from omp-tasks verbatim (VERSION=omp-tasks).
    # serial_repo keeps omp-tasks build system (omp.h, KERNEL_SEQ verify),
    # but .c files have no pragmas -> runs serial, verifies via _seq compare.
    mv_src = os.path.join(SRC, "Makefile.version")
    mv_dst = os.path.join(DST, "Makefile.version")
    shutil.copy2(mv_src, mv_dst)
    # copy each benchmark dir, strip pragmas from .c files
    for name, rel in SOURCES.items():
        src_dir = os.path.join(SRC, os.path.dirname(rel))
        dst_dir = os.path.join(DST, name)
        shutil.copytree(src_dir, dst_dir, symlinks=True)
        # strip pragmas from all .c files
        for root, dirs, files in os.walk(dst_dir):
            for f in files:
                if f.endswith(".c"):
                    p = os.path.join(root, f)
                    text = open(p).read()
                    stripped = strip_pragmas(text)
                    open(p, "w").write(stripped)
        # Fix Makefile paths: omp-tasks subdirs (alignment_for, sparselu_for)
        # use ../../../ and ../../Makefile.version. serial_repo is flat, so
        # normalize to ../../ and ../Makefile.version.
        mf = os.path.join(dst_dir, "Makefile")
        if os.path.isfile(mf):
            t = open(mf).read()
            t = t.replace("../../../", "../../")
            t = t.replace("../../Makefile.version", "../Makefile.version")
            open(mf, "w").write(t)
        print(f"{name}: stripped {rel}")
    print(f"Serial baselines written to {DST}")

if __name__ == "__main__":
    main()
