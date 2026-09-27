#!/usr/bin/env python3
"""E2-B1's Rodinia unit: bfs, packaged in layout v4 (the measurement outside the model's file).

Why bfs (record §6, 26-27 Sep; the screen, docs/screening/, row R3). E2-B1 direction (a), tier 1: the
fact that decides whether the hot loop may run in parallel is not in the loop's own statements, and not
in its function. Rodinia 3.1's bfs expands a frontier level by level; its hot loop stores
`h_cost[id]` and `h_updating_graph_mask[id]` for every unvisited neighbour `id` of a frontier node.
Whether two iterations store to the same element — two frontier nodes sharing an unvisited neighbour —
is a property of the EDGE LIST, which Rodinia reads from an input file. Read alone, the loop admits a
parallel reading: Rodinia's own OpenMP version puts `parallel for` on it (with same-value races, the
screen's "defective shipped expert"). Of the screen's group bfs -> kmeans -> streamcluster the rule
keeps the first, bfs (the author's decision, 27 Sep).

What is taken and what is not. Rodinia 3.1 has no serial bfs: `benchmarks/rodinia_3.1/openmp/bfs/bfs.cpp`
(verbatim, PROVENANCE.txt one level up) switches its OpenMP code on with `#define OPEN`. The model's
file holds the TRAVERSAL of its BFSGraph — `int k=0;` and the `do { … } while(stop);` with both loops,
copied verbatim — with every `#ifdef OPEN` block (the pragmas, `omp_get_wtime`, the offload
directives) and every comment removed (D36: the one comment left inside says a THREAD changes
`stop`). The head names Rodinia's file without its `openmp/` directory, for the same reason.
Everything else of the program is measurement and lives in a header OUTSIDE the package,
`prepared/_harness/rodinia_b1/bfs.h` (found through CPATH, harness_include.py; D39, reversed for
E2-B1 alone): Rodinia's `struct Node` and the arrays the traversal uses, their initial values (as
BFSGraph sets them after reading its file), the sizes, the perturbed input, the digest of the cost
array (Rodinia writes it to result.txt), the timed region and main's body. `main` itself is
`PB_MAIN(kernel_bfs)` in the file, expanded there so DiscoPoP instruments it, as in TSVC's v4
(prepare_tsvc.py).

The recorded deviation — the graph (record §6, 27 Sep: "a deterministic synthetic graph as its input").
Rodinia reads it from a file (graph4096.txt, graph65536.txt, graph1MW_6.txt); the harness GENERATES it,
deterministically, with the structure of Rodinia's own input generator (data/bfs/inputGen/graphgen.cpp,
PROVENANCE.txt): every node draws 2-4 edges to uniformly random nodes, each edge is stored in both
directions in the order drawn (mean degree 6: three draws on average, each stored twice), multiple
edges and self-loops are kept, and the source is drawn after the edges. In such a graph frontier nodes
share unvisited neighbours — the hidden dependence, which `--validate` counts (27 Sep: about half of the
hot loop's stores at MINI and at SMALL go to an element another iteration of the level stored to;
every node is reached, in 8 and 10 passes of the level loop). The draws come from the
packaging's generator (`pb_uniform`), from a fixed state, or seeded by argv[1]: the perturbed input is
another graph and another source. Sizes (every parameter needs a reason): MINI, SMALL and STANDARD are
the node counts of Rodinia's three shipped graphs; LARGE and EXTRALARGE continue by TSVC's ratios from
STANDARD (x8, x6). The agent profiles at SMALL, as for every v4 package.

Validation (`--validate`; MINI and SMALL; every build and run one after the other):
  1. the package builds with the harness through CPATH, runs, prints finite values, the digest build
     prints its three lines and the timed region; the perturbed input changes the output; two runs
     agree;
  2. the ORIGINAL computes the same: the harness writes its graph in Rodinia's file format
     (-DPB_EMIT_INPUT, graphgen's layout), Rodinia's bfs.cpp as shipped (-fopenmp, one thread) reads
     it, and its result.txt equals the package's full dump — on the default and the perturbed input;
  3. the property: a checker built on the same header runs the same traversal and counts the stores
     of the hot loop to an element another iteration of the same level already stored to; it must be
     > 0 on both inputs (it also reports the levels and the nodes reached).

Usage:
  python3 agent/tools/prepare_bfs.py --out agent/prepared/rodinia_b1 [--validate]
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
from prepare_apps import _sysroot  # noqa: E402  (macOS SDK and Homebrew's keg-only libomp)
from prepare_calib import SCAFFOLD  # noqa: E402  (the same digest, seed and timer as TSVC's v4)

AGENT_DIR = Path(__file__).resolve().parent.parent
HARNESS_ROOT = AGENT_DIR.parent
RODINIA = HARNESS_ROOT / "benchmarks" / "rodinia_3.1"
SOURCE = RODINIA / "openmp" / "bfs" / "bfs.cpp"
SUITE, NAME = "rodinia_b1", "bfs"
KERNEL = "kernel_bfs"
GENERATOR_VERSION = 1

# Rodinia's graph4096 / graph65536 / graph1MW_6, then TSVC's ratios (x8, x6) from STANDARD.
SIZES = {"MINI": 4096, "SMALL": 65536, "STANDARD": 1000000, "LARGE": 8000000, "EXTRALARGE": 48000000}

# The traversal in BFSGraph (lines are 1-based, inclusive): `int k=0;` … `while(stop);`. Checked
# against the text below, so a different bfs.cpp fails loudly instead of packaging something else.
TRAVERSAL = (116, 170)

# What every arm is told about the lines the file shares with the harness (llm/request.py renders it
# for the agent, its twins and the model alone). Nothing about the graph: its shape is the hidden fact.
PROTECTED_NOTE = ("`PB_MAIN(kernel_bfs)` expands to `main`: it sets up the data the included header declares, "
                  "times one call of `kernel_bfs` and prints its result.")

# The deciding fact, in meta.json only (never in a source the model reads; test_integrity 1b checks it).
TRANSFORMATION = "whether two iterations of the frontier loop store to the same element depends on the edge list"
WHY = ("frontier nodes that share an unvisited neighbour store to the same h_cost and h_updating_graph_mask "
       "element in one level; the edge list is the input graph, generated outside the file")


def _inputs_sha() -> str:
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def _strip_openmp_blocks(lines: List[str]) -> Tuple[List[str], int]:
    """Remove every `#ifdef OPEN` / `#ifdef OMP_OFFLOAD` block, nested ones included (bfs.cpp puts
    an `#ifdef OMP_OFFLOAD` inside an `#ifdef OPEN`, so a non-greedy regex, as nw's, would stop at
    the inner `#endif` and leave the outer one). No block has an `#else`: what is removed is exactly
    what `#define OPEN` switched on."""
    out: List[str] = []
    depth, removed = 0, 0
    for line in lines:
        s = line.strip()
        if depth == 0:
            if re.match(r"#\s*ifdef\s+(OPEN|OMP_OFFLOAD)\b", s):
                depth, removed = 1, removed + 1
                continue
            out.append(line)
            continue
        if re.match(r"#\s*if", s):
            depth += 1
        elif re.match(r"#\s*else|#\s*elif", s):
            raise SystemExit(f"bfs: an #else inside an OpenMP block ({s!r}) — the stripping would drop code")
        elif re.match(r"#\s*endif", s):
            depth -= 1
    if depth:
        raise SystemExit("bfs: an #ifdef OPEN block is not closed inside the traversal")
    return out, removed


def traversal() -> Tuple[str, List[str]]:
    """The traversal as the model's file holds it, and what was removed from Rodinia's lines."""
    lines = SOURCE.read_text().splitlines()[TRAVERSAL[0] - 1:TRAVERSAL[1]]
    if lines[0].strip() != "int k=0;" or lines[-1].strip() != "while(stop);":
        raise SystemExit(f"bfs: {SOURCE} lines {TRAVERSAL} are not BFSGraph's traversal — the file changed")
    lines, n_blocks = _strip_openmp_blocks(lines)
    n_comments = sum(1 for l in lines if l.strip().startswith("//"))
    lines = [l for l in lines if not l.strip().startswith("//")]
    text = "\n".join(lines) + "\n"
    if "//" in text or "/*" in text:
        raise SystemExit("bfs: a comment is left in the traversal (D36)")
    if re.search(r"pragma|\bomp_|\bOPEN\b|OMP_OFFLOAD|thread", text, re.I):
        raise SystemExit("bfs: OpenMP text left in the traversal after stripping (§1a, D36)")
    removed = [
        f"{n_blocks} #ifdef OPEN / OMP_OFFLOAD block(s) in the traversal: both `#pragma omp parallel for`, "
        "the offload directives, the commented omp_set_num_threads and the start of the omp_get_wtime timing",
        f"{n_comments} comment line(s) left in the traversal (D36: it says a thread changes `stop`)",
        "with the rest of BFSGraph: the block after the traversal (the timing's end, its `Compute time` "
        "line), #include <omp.h>, `#define OPEN`, the commented `#define NUM_THREAD 4`, Usage() and the "
        "argv interface (thread count, input file)",
        "the graph file reading, replaced by the harness's generated graph (the recorded deviation)",
        "the progress printf lines and the result.txt file, replaced by the digest of h_cost",
    ]
    return text, removed


# ---- the model's file ----------------------------------------------------------------------------------
KERNEL_HEAD = """/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 %(sha)s; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "%(suite)s/%(name)s.h"
"""


def render() -> str:
    """The benchmark's own file: the traversal, verbatim, as `kernel_bfs`, and `main` by macro."""
    body, _ = traversal()
    return (KERNEL_HEAD % {"sha": _inputs_sha()[:12], "suite": SUITE, "name": NAME}
            + f"\nstatic void {KERNEL}(void)\n{{\n" + body + "}\n"
            + f"\nPB_MAIN({KERNEL})\n")


def protected_lines() -> List[str]:
    """The lines of the model's file the harness depends on, whitespace-stripped (meta.json's
    `protected`: the agent's gate refuses a change to them, every arm is told about them)."""
    return [f'#include "{SUITE}/{NAME}.h"', f"PB_MAIN({KERNEL})"]


# ---- the measurement harness, outside the package -------------------------------------------------------
HARNESS_HEAD = """/* Measurement harness for Rodinia 3.1 bfs: Rodinia's graph structure and arrays, the graph itself
 * (generated here, in place of Rodinia's input file), sizes, initial values, perturbed input, digest,
 * timing and main. Generated by agent/tools/prepare_bfs.py (v%(version)d) — do not edit by hand. It
 * lives OUTSIDE the benchmark's directory (D39): DiscoPoP instruments only code inside the project
 * root, and no model's working copy holds this file. Default dataset SMALL; override with
 * -D<SIZE>_DATASET. Digest on stdout; -DPB_FULL_DUMP prints every value; argv[1] is a perturbation
 * seed; -DPB_EMIT_INPUT also writes the graph to pb_graph.txt in Rodinia's file format. */
#ifndef PB_BFS_HARNESS
#define PB_BFS_HARNESS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
"""

SIZE_BLOCK = """
#if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) \\
    && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
# define SMALL_DATASET
#endif
""" + "".join(f"#ifdef {k}_DATASET\n# define PB_NODES {v}\n#endif\n" for k, v in SIZES.items())

DATA = """
/* ---- data: Rodinia's node structure (bfs.cpp, verbatim) and the arrays of BFSGraph ------------ */
//Structure to hold a node information
struct Node
{
	int starting;
	int no_of_edges;
};

static int no_of_nodes;
static int edge_list_size;
static Node* h_graph_nodes;
static bool *h_graph_mask;
static bool *h_updating_graph_mask;
static bool *h_graph_visited;
static int* h_graph_edges;
static int* h_cost;

/* ---- the graph: generated, in place of Rodinia's input file ------------------------------------
 * The structure of Rodinia's own generator (data/bfs/inputGen/graphgen.cpp): every node draws 2-4
 * edges to uniformly random nodes; each edge is stored in both directions, in the order drawn;
 * multiple edges and self-loops are kept; the source is drawn after the edges. The adjacency is laid
 * out as Rodinia's file lays it out (node i's edges from h_graph_nodes[i].starting on), in two passes
 * over the same draws — the first counts, the second places — so no list of edges is kept. The draws
 * are the packaging's generator's, from a fixed state or from the perturbation seed. */
#define PB_GRAPH_STATE 88172645463325252ULL

static int pb_graph(unsigned long long state0)
{
  unsigned long long st;
  int i, j, n, d, source;
  int* fill = (int*)malloc(sizeof(int) * (size_t)no_of_nodes);
  if (!fill) return -1;
  for (i = 0; i < no_of_nodes; i++) h_graph_nodes[i].no_of_edges = 0;
  st = state0;
  for (i = 0; i < no_of_nodes; i++) {
    n = 2 + (int)(pb_uniform(&st) * 3.0);
    for (j = 0; j < n; j++) {
      d = (int)(pb_uniform(&st) * (double)no_of_nodes);
      h_graph_nodes[i].no_of_edges++;
      h_graph_nodes[d].no_of_edges++;
    }
  }
  edge_list_size = 0;
  for (i = 0; i < no_of_nodes; i++) {
    h_graph_nodes[i].starting = edge_list_size;
    fill[i] = edge_list_size;
    edge_list_size += h_graph_nodes[i].no_of_edges;
  }
  h_graph_edges = (int*)malloc(sizeof(int) * (size_t)edge_list_size);
  if (!h_graph_edges) { free(fill); return -1; }
  st = state0;
  for (i = 0; i < no_of_nodes; i++) {
    n = 2 + (int)(pb_uniform(&st) * 3.0);
    for (j = 0; j < n; j++) {
      d = (int)(pb_uniform(&st) * (double)no_of_nodes);
      h_graph_edges[fill[i]++] = d;
      h_graph_edges[fill[d]++] = i;
    }
  }
  source = (int)(pb_uniform(&st) * (double)no_of_nodes);
  free(fill);
  return source;
}

#ifdef PB_EMIT_INPUT
/* The graph in Rodinia's file format (graphgen.cpp's output), for the packager's validation: Rodinia's
 * bfs.cpp as shipped reads it, so the original and the package run on the same graph. bfs reads the
 * edge weights and ignores them; written as 1. */
static void pb_write_graph(int source)
{
  FILE* f = fopen("pb_graph.txt", "w");
  if (!f) { fprintf(stderr, "cannot write pb_graph.txt\\n"); exit(1); }
  fprintf(f, "%d\\n", no_of_nodes);
  for (int i = 0; i < no_of_nodes; i++) fprintf(f, "%d %d\\n", h_graph_nodes[i].starting, h_graph_nodes[i].no_of_edges);
  fprintf(f, "\\n%d\\n\\n%d\\n", source, edge_list_size);
  for (int i = 0; i < edge_list_size; i++) fprintf(f, "%d 1\\n", h_graph_edges[i]);
  fclose(f);
}
#endif
"""

DRIVER = """
/* ---- main: BFSGraph around its traversal ---------------------------------------------------------- */
static int pb_setup(int argc, char** argv)
{
  int source;
  no_of_nodes = PB_NODES;
  h_graph_nodes = (Node*) malloc(sizeof(Node)*(size_t)no_of_nodes);
  h_graph_mask = (bool*) malloc(sizeof(bool)*(size_t)no_of_nodes);
  h_updating_graph_mask = (bool*) malloc(sizeof(bool)*(size_t)no_of_nodes);
  h_graph_visited = (bool*) malloc(sizeof(bool)*(size_t)no_of_nodes);
  h_cost = (int*) malloc(sizeof(int)*(size_t)no_of_nodes);
  if (!h_graph_nodes || !h_graph_mask || !h_updating_graph_mask || !h_graph_visited || !h_cost)
    { fprintf(stderr, "out of memory\\n"); return 1; }
  /* Optional perturbed input: another graph, and another source. */
  source = pb_graph(argc > 1 ? pb_seed(argv[1]) : PB_GRAPH_STATE);
  if (source < 0) { fprintf(stderr, "out of memory\\n"); return 1; }
#ifdef PB_EMIT_INPUT
  pb_write_graph(source);
#endif
  /* Rodinia's initial values, as BFSGraph sets them around reading its file. */
  for (int i = 0; i < no_of_nodes; i++) {
    h_graph_mask[i]=false;
    h_updating_graph_mask[i]=false;
    h_graph_visited[i]=false;
  }
  h_graph_mask[source]=true;
  h_graph_visited[source]=true;
  for(int i=0;i<no_of_nodes;i++)
    h_cost[i]=-1;
  h_cost[source]=0;
  return 0;
}

static void pb_finish(void)
{
  /* Rodinia's result: every node's cost, in node order (its result.txt). */
  for (int i = 0; i < no_of_nodes; i++) pb_emit(h_cost[i]);
  pb_report();
  free(h_graph_nodes); free(h_graph_edges); free(h_graph_mask);
  free(h_updating_graph_mask); free(h_graph_visited); free(h_cost);
}

/* `main`, expanded in the benchmark's file so that DiscoPoP instruments it: the timed region is the
 * traversal, as Rodinia's own omp_get_wtime region is. */
#define PB_MAIN(K)                                        \\
  int main(int argc, char** argv)                         \\
  {                                                       \\
    if (pb_setup(argc, argv)) return 1;                   \\
    pb_timer_start();                                     \\
    K();                                                  \\
    pb_timer_stop();                                      \\
    pb_finish();                                          \\
    return 0;                                             \\
  }

#endif
"""


def render_harness() -> str:
    """The measurement header (v4): everything of the program except the traversal."""
    return HARNESS_HEAD % {"version": GENERATOR_VERSION} + SIZE_BLOCK + SCAFFOLD + DATA + DRIVER


# ---- validation ------------------------------------------------------------------------------------------
# The property check: the same traversal, counting the stores of the hot loop to an element that another
# iteration of the same level already stored to. An element is stored to only in the level that reaches
# it (it is visited from then on), so the last writer needs no reset between levels.
CHECKER = """#include "%(suite)s/%(name)s.h"

int main(int argc, char** argv)
{
  if (pb_setup(argc, argv)) return 1;
  int* last = (int*)malloc(sizeof(int) * (size_t)no_of_nodes);
  long levels = 0, frontier = 0, stores = 0, shared = 0, reached = 0;
  for (int i = 0; i < no_of_nodes; i++) last[i] = -1;
  bool stop;
  do {
    stop = false;
    levels++;
    for (int tid = 0; tid < no_of_nodes; tid++) {
      if (h_graph_mask[tid] == true) {
        h_graph_mask[tid] = false;
        frontier++;
        for (int i = h_graph_nodes[tid].starting;
             i < (h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++) {
          int id = h_graph_edges[i];
          if (!h_graph_visited[id]) {
            stores++;
            if (last[id] >= 0 && last[id] != tid) shared++;
            last[id] = tid;
            h_cost[id] = h_cost[tid] + 1;
            h_updating_graph_mask[id] = true;
          }
        }
      }
    }
    for (int tid = 0; tid < no_of_nodes; tid++) {
      if (h_updating_graph_mask[tid] == true) {
        h_graph_mask[tid] = true;
        h_graph_visited[tid] = true;
        stop = true;
        h_updating_graph_mask[tid] = false;
      }
    }
  } while (stop);
  for (int i = 0; i < no_of_nodes; i++) reached += h_cost[i] >= 0;
  printf("%%ld %%ld %%ld %%ld %%ld %%d\\n", levels, frontier, stores, shared, reached, no_of_nodes);
  free(last);
  return 0;
}
"""


def _cxx() -> str:
    """The C++ compiler to validate with: $DP_CXX, else the first that exists — the names the
    server (clang++-20) and the Mac (Homebrew's clang++-19) have, as prepare_calib's `_cc`."""
    for c in [os.environ.get("DP_CXX", ""), "clang++-20", "clang++-19", "clang++", "c++"]:
        if c and shutil.which(c):
            return c
    return "c++"


def _build(src: Path, out: Path, flags: List[str]) -> Optional[str]:
    r = subprocess.run([_cxx(), "-O2", *_sysroot(), *flags, str(src), "-o", str(out), "-lm"],
                       capture_output=True, text=True)
    return None if r.returncode == 0 else r.stderr[-400:]


def _run(binary: Path, args: List[str], cwd: Path, threads: Optional[int] = None) -> Tuple[int, str, str]:
    env = dict(os.environ)
    if threads:
        env["OMP_NUM_THREADS"] = str(threads)
    r = subprocess.run([str(binary), *args], cwd=cwd, capture_output=True, text=True, timeout=900, env=env)
    return r.returncode, r.stdout, r.stderr


def _values(text: str) -> Optional[List[float]]:
    try:
        return [float(v) for v in text.split()]
    except ValueError:
        return None


def validate(package: Path, sizes: List[str]) -> Tuple[List[str], List[str]]:
    """(problems, notes) — see the module docstring for the three checks."""
    problems: List[str] = []
    notes: List[str] = []
    with tempfile.TemporaryDirectory(prefix="bfs_b1_") as tmp:
        t = Path(tmp)
        checker = t / "checker.cpp"
        checker.write_text(CHECKER % {"suite": SUITE, "name": NAME})
        orig = t / "orig"
        err = _build(SOURCE, orig, ["-fopenmp"])
        if err:
            return [f"Rodinia's bfs.cpp does not build: {err}"], notes
        for size in sizes:
            dump, digest, emit, check = (t / f"{what}_{size}" for what in ("dump", "digest", "emit", "check"))
            for binary, flags, what in ((dump, ["-DPB_FULL_DUMP"], "full dump"), (digest, [], "digest"),
                                        (emit, ["-DPB_FULL_DUMP", "-DPB_EMIT_INPUT"], "input writer")):
                err = _build(package, binary, [f"-D{size}_DATASET", *flags])
                if err:
                    return problems + [f"{size}: the package ({what}) does not build: {err}"], notes
            err = _build(checker, check, [f"-D{size}_DATASET"])
            if err:
                return problems + [f"{size}: the property checker does not build: {err}"], notes
            # 1. runs, finite, perturbed input changes it, deterministic; the digest build's format
            outs: Dict[str, str] = {}
            for tag, args in (("default", []), ("seeded", ["7"])):
                rc, out, e = _run(dump, args, t)
                if rc != 0:
                    problems.append(f"{size} {tag}: rc={rc} {e[-200:]}")
                    continue
                vals = _values(out)
                if vals is None or not vals or any(v != v or abs(v) == float("inf") for v in vals):
                    problems.append(f"{size} {tag}: output not finite numbers")
                outs[tag] = out
            if len(outs) < 2:
                continue
            if outs["default"] == outs["seeded"]:
                problems.append(f"{size}: the perturbed input does not change the output")
            for tag, args in (("default", []), ("seeded", ["7"])):
                if _run(dump, args, t)[1] != outs[tag]:
                    problems.append(f"{size} {tag}: not deterministic")
            rc, out, e = _run(digest, [], t)
            if rc != 0 or out.count("\n") != 3 or not out.startswith("pb_values ") \
                    or "DP_TIMED_REGION_SECONDS" not in e:
                problems.append(f"{size}: the digest build does not print the digest and the timed region")
            # 2. the original, as shipped, on the same graph
            for tag, args in (("default", []), ("seeded", ["7"])):
                (t / "result.txt").unlink(missing_ok=True)
                rc, out, e = _run(emit, args, t)
                if rc != 0 or out != outs[tag]:
                    problems.append(f"{size} {tag}: the input-writing build differs from the package")
                    continue
                rc, _, e = _run(orig, ["1", "pb_graph.txt"], t, threads=1)
                res = t / "result.txt"
                if rc != 0 or not res.exists():
                    problems.append(f"{size} {tag}: Rodinia's bfs did not run: rc={rc} {e[-200:]}")
                    continue
                got = [int(m.group(2)) for m in re.finditer(r"^(\d+)\) cost:(-?\d+)$", res.read_text(), re.M)]
                mine = [int(v) for v in outs[tag].split()]
                if got != mine:
                    diff = next((i for i, (x, y) in enumerate(zip(got, mine)) if x != y), min(len(got), len(mine)))
                    problems.append(f"{size} {tag}: differs from Rodinia's bfs on the same graph "
                                    f"({len(got)} vs {len(mine)} values, first difference at node {diff})")
            # 3. the property: iterations of one level store to the same element
            for tag, args in (("default", []), ("seeded", ["7"])):
                rc, out, e = _run(check, args, t)
                if rc != 0 or len(out.split()) != 6:
                    problems.append(f"{size} {tag}: the property checker failed: {e[-200:]}")
                    continue
                levels, frontier, stores, shared, reached, nodes = (int(v) for v in out.split())
                notes.append(f"{size} {tag}: {levels} levels, {reached}/{nodes} nodes reached, {stores} stores "
                             f"in the hot loop, {shared} to an element another iteration of the level stored to")
                if shared == 0:
                    problems.append(f"{size} {tag}: no two iterations of a level store to the same element")
    return problems, notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path, help="the suite directory, e.g. agent/prepared/rodinia_b1")
    ap.add_argument("--harness-out", type=Path, default=None,
                    help="where the measurement header goes (default: <out>/../_harness — outside every "
                         "package, D39); builds find it through CPATH (harness_include.py)")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--validate-sizes", default="MINI,SMALL")
    a = ap.parse_args()
    harness_root = (a.harness_out or a.out.parent / "_harness").resolve()
    # The validation builds must find the header exactly as every other build does.
    os.environ["CPATH"] = os.pathsep.join([str(harness_root)]
                                          + [p for p in os.environ.get("CPATH", "").split(os.pathsep) if p])
    d = a.out / NAME
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    src = d / f"{NAME}.cpp"
    src.write_text(render())
    hdr = harness_root / SUITE / f"{NAME}.h"
    hdr.parent.mkdir(parents=True, exist_ok=True)
    hdr.write_text(render_harness())
    _, removed = traversal()
    (d / "meta.json").write_text(json.dumps({
        "suite": SUITE, "kernel": NAME, "source": str(SOURCE.relative_to(HARNESS_ROOT)),
        "category": "graph-traversal", "file": src.name, "language": "cpp", "layout": "single",
        "restructuring_class": "hidden dependence (E2-B1 a, tier 1)",
        "transformation": TRANSFORMATION, "why": WHY, "reference_solution": None,
        # v4: the harness's code is not in the package; `main` (PB_MAIN) is the one function of the
        # file that is not the benchmark's.
        "exclude_functions": ["main"],
        "harness": f"{SUITE}/{NAME}.h",
        "harness_sha256": hashlib.sha256(hdr.read_bytes()).hexdigest(),
        "protected": protected_lines(),
        "protected_note": PROTECTED_NOTE,
        "agent_dataset": "SMALL", "generator_version": GENERATOR_VERSION,
        "sizes": {k: {"PB_NODES": str(v)} for k, v in SIZES.items()},
        "removed": removed,
        "deviations": [
            "the graph is generated in the harness (deterministic; the structure of Rodinia's graphgen.cpp: "
            "2-4 random edges drawn per node, stored both ways, the source drawn after the edges) instead of "
            "read from Rodinia's input file; MINI/SMALL/STANDARD have the node counts of Rodinia's graph4096, "
            "graph65536 and graph1MW_6",
            "argv[1] seeds the generator: the perturbed input is another graph and another source",
        ],
        "inputs_sha256": _inputs_sha(),
        "output_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
    }, indent=2) + "\n")
    note = ""
    failed = False
    if a.validate:
        problems, notes = validate(src, [s for s in a.validate_sizes.split(",") if s])
        for n in notes:
            print(f"    {n}")
        failed = bool(problems)
        note = "  OK" if not problems else "  FAILED: " + "; ".join(problems)
    print(f"{NAME}: {src} ({len(src.read_text().splitlines())} lines), harness {hdr}{note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
