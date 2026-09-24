#!/usr/bin/env python3
"""Agent experiment harness — runs DiscoPoP-agent configurations over prepared benchmarks.

The other harnesses in this repository compare DiscoPoP *versions*. This one compares
*configurations of the agent* ("arms", defined in ``agent/config/arms.json``) and models, on
single-file benchmarks produced by ``agent/tools/prepare_polybench.py`` (C or C++; the
language is taken from each benchmark's ``meta.json``).

One trial = (benchmark, arm, model, repeat):

1. **profile** — DiscoPoP instruments, runs and analyses the benchmark once per benchmark
   per run; every trial starts from a copy of that same profile, so arms are compared on
   identical evidence (DiscoPoP's own run-to-run variation is studied separately).
2. **agent** — ``python -m discopop_agent`` with the arm's flags; its log streams to
   ``agent.log`` (watch it with ``tail -f``).
3. **verify** — independent of the agent's own verdicts: the original source built
   sequentially against the agent's final source built with ``-fopenmp``,
   (a) full value dump at the agent size, compared exactly;
   (b) digest at the verify size, at each thread count, repeated — values must agree
       within a relative tolerance and be stable across repeats at a fixed thread count;
   (c) wall-clock medians, giving the speedup.

Layout: ``agent/runs/<run_id>/`` holds ``manifest.json``, ``results.json``,
``overview.md``, ``tables/`` and ``benchmarks/<suite>/<kernel>/<arm>/<model>/rep<k>/``
(original.<ext>, final.<ext>, changes.diff, agent.log, agent_patches/, trial.json).

Usage:
    agent/benchmark prepare --size SMALL
    agent/benchmark list-benchmarks
    agent/benchmark list-arms
    agent/benchmark run polybench/seidel-2d --arms full --models haiku
    agent/benchmark report [--run RUN_ID]
    agent/benchmark list-runs
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import math
import os
import platform
import re
import shutil
import signal
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from run_store import RunStore
import scaffold

AGENT_DIR = Path(__file__).resolve().parents[1]
HARNESS_ROOT = AGENT_DIR.parent
PREPARED = AGENT_DIR / "prepared"
ARMS_FILE = AGENT_DIR / "config" / "arms.json"
# Per-kernel sizes fixed by the T0.1 study (agent/tools/size_table.py → chosen.json, committed here).
KERNEL_SIZES_FILE = AGENT_DIR / "config" / "kernel_sizes.json"
def _default_agent_repo() -> Path:
    """The agent repository. Since 2026-09-20 `evaluation/` (this harness) lives INSIDE it;
    before that the two were sibling checkouts (`new_benchmark_harness`, `discopop_agent`)."""
    for cand in (HARNESS_ROOT.parent, HARNESS_ROOT.parent / "discopop_agent"):
        if (cand / "discopop_agent" / "__main__.py").exists():
            return cand
    return HARNESS_ROOT.parent


DEFAULT_AGENT_REPO = _default_agent_repo()

# Relative tolerance for comparing digests between the original and the agent's
# final program. A correct parallel reduction reorders additions and moves the
# last digits (~1e-16 relative); a wrong result moves them by far more.
DIGEST_REL_TOL = 1e-9
FASTER_THRESHOLD = 1.1
# Attempts of DiscoPoP's explorer on one profile before a benchmark is given up (profile_once).
EXPLORER_ATTEMPTS = 20
# One explorer attempt's limit and how many stalled draws are repeated — the agent's own
# values (discopop_agent/profiling/tools.py), so the harness's profile and the agent's
# re-profiles treat a stall alike.
EXPLORER_STALL_S = 600
EXPLORER_STALL_ATTEMPTS = 5
# The agent's own limit inside a trial, per benchmark (the author, 23 Sep): 10x this benchmark's
# own successful explorer run, never under 60 s. A stall costs the whole limit before the draw
# is repeated, and in E1 26 stalls x 600 s were a third of all trial time (record §6, 23 Sep);
# a legitimate run of a campaign benchmark took at most 33 s over 166 draws, and a large
# program measures its own (LULESH at -s 5: 16 s -> 160 s). The harness's FIRST explorer run
# of a benchmark has nothing to scale from and keeps EXPLORER_STALL_S.
AGENT_EXPLORER_FLOOR_S = 60
AGENT_EXPLORER_FACTOR = 10

# Same preference order as the agent's gate/toolchain.py, so the harness verifies
# with the compiler the agent validated with.
_CXX_CANDIDATES = ["/usr/local/Cellar/llvm@19/19.1.7/bin/clang++", "clang++-20", "clang++-19", "clang++"]
_CC_CANDIDATES = ["/usr/local/Cellar/llvm@19/19.1.7/bin/clang", "clang-20", "clang-19", "clang"]


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def _git_state(repo: Path) -> dict:
    """HEAD plus a hash of uncommitted changes — enough to prove two checkouts match."""
    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    diff = git("diff", "HEAD")
    untracked = git("ls-files", "--others", "--exclude-standard")
    return {
        "path": str(repo), "head": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty_sha256": hashlib.sha256((diff + "\n" + untracked).encode()).hexdigest()
        if (diff or untracked) else None,
    }


def _tool_versions(agent_repo: Path) -> dict:
    """Versions that can change a model-driven result between runs."""
    py = str(agent_repo / "venv" / "bin" / "python")
    out: dict = {}
    probes = {
        "claude_agent_sdk": [py, "-c", "import claude_agent_sdk as s; print(getattr(s, '__version__', '?'))"],
        "claude_cli_bundled": [py, "-c", "import claude_agent_sdk, pathlib, subprocess; "
                               "c = pathlib.Path(claude_agent_sdk.__file__).parent / '_bundled' / 'claude'; "
                               "print(subprocess.run([str(c), '--version'], capture_output=True, text=True).stdout.strip() "
                               "if c.exists() else 'not bundled')"],
    }
    for name, cmd in probes.items():
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            out[name] = r.stdout.strip() or r.stderr.strip()[-200:]
        except (OSError, subprocess.TimeoutExpired) as e:
            out[name] = f"unavailable: {e}"
    return out


def _find_tool(explicit: Optional[str], env_var: str, candidates: List[str], what: str) -> str:
    for c in ([explicit] if explicit else []) + [os.environ.get(env_var, "")] + candidates:
        if not c:
            continue
        if os.path.isabs(c) and os.path.exists(c):
            return c
        found = shutil.which(c)
        if found:
            return found
    sys.exit(f"no {what} found — set {env_var} or pass the matching option")


def _is_c(path: Path) -> bool:
    return path.suffix == ".c"


def _toolchain_flags(openmp: bool, c_source: bool) -> List[str]:
    flags: List[str] = []
    if platform.system() == "Darwin":
        try:
            sdk = subprocess.check_output(["xcrun", "--show-sdk-path"], text=True,
                                          stderr=subprocess.DEVNULL).strip()
            if sdk:
                flags += ["-isysroot", sdk]
        except (OSError, subprocess.CalledProcessError):
            pass
    if openmp:
        flags.append("-fopenmp")
        libomp = Path("/usr/local/opt/libomp/lib")
        if libomp.exists():
            # the header too: a candidate may include <omp.h> (the s341 reference does), and
            # Homebrew's clang does not find libomp's on its own
            flags += [f"-I{libomp.parent / 'include'}", f"-L{libomp}", f"-Wl,-rpath,{libomp}"]
    if c_source:
        flags.append("-lm")
    return flags


def _agent_env(agent_repo: Path) -> Dict[str, str]:
    env = dict(os.environ)
    venv_bin = agent_repo / "venv" / "bin"
    extra = [str(venv_bin), str(Path.home() / ".local" / "bin")]
    env["PATH"] = os.pathsep.join(extra + [env.get("PATH", "")])
    env["PYTHONPATH"] = os.pathsep.join([str(agent_repo), env.get("PYTHONPATH", "")])
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _load_arms() -> Dict[str, dict]:
    return resolve_twins(json.loads(ARMS_FILE.read_text())["arms"])


# What a twin (D38) takes from the agent arm it is the twin of: everything that says what the
# agent is given and how it is configured, so the twin's model is handed exactly the agent's
# DiscoPoP information. Its own `runner`, `description`, `why` and `ids` stay its own.
TWIN_INHERITS = ("flags", "settings", "timing_size", "evidence_file")


def resolve_twins(arms: Dict[str, dict]) -> Dict[str, dict]:
    """Fill each `"runner": "twin"` arm from its `twin_of`. Every check made on an agent arm —
    the settings verified against the parser, the confound printout, the flags a trial runs
    with — then applies to its twin unchanged, and a twin cannot drift from its agent arm."""
    out = dict(arms)
    for name, spec in arms.items():
        if spec.get("runner") != "twin":
            continue
        of = spec.get("twin_of")
        if of not in arms or arms[of].get("runner"):
            sys.exit(f"arms.json: twin {name!r} names twin_of={of!r}, which is not an agent arm")
        out[name] = {**spec, **{k: arms[of][k] for k in TWIN_INHERITS if k in arms[of]}}
    return out


def _common_flags() -> List[str]:
    """Flags every arm passes before its own (fixed configuration, see arms.json)."""
    return list(json.loads(ARMS_FILE.read_text()).get("common_flags", []))


def _sizes_for(benchmark: str) -> Dict[str, Any]:
    """T0.1's entry for a benchmark, looked up by its FULL name (suite/benchmark).

    Bare names collide — `lu` is both polybench/lu and npb/lu — so a table keyed on the bare
    name hands one of them the other's sizes. Older tables written before this was noticed are
    keyed by the bare name; those are accepted only while no other suite claims the same name.
    """
    if not KERNEL_SIZES_FILE.exists():
        sys.exit(f"{KERNEL_SIZES_FILE} is missing — run T0.1 (agent/tools/size_table.py) and "
                 f"commit its chosen.json there")
    table = json.loads(KERNEL_SIZES_FILE.read_text())["kernels"]
    if benchmark in table:
        return dict(table[benchmark])
    bare = benchmark.split("/")[-1]
    clashes = [b for b in _prepared_benchmarks() if b.split("/")[-1] == bare]
    if bare in table and len(clashes) == 1:
        return dict(table[bare])
    if bare in table:
        sys.exit(f"{KERNEL_SIZES_FILE.name} keys {bare!r} by its bare name, but "
                 f"{' and '.join(clashes)} share it — re-run T0.1 to key sizes by full name")
    return {}


def _timing_size(kernel: str) -> Optional[str]:
    """The benchmark's timing size from T0.1, or None when no size reached the target.

    Eight of the packaged kernels have none (atax, bicg, gemver, gesummv, jacobi-1d, mvt,
    reg_detect, trisolv): they run in milliseconds at every size the harness can build. This
    used to exit, which was right while only E10's arms asked for a timing size; since the
    speed check became the campaign default (2026-09-20) it would have made those kernels
    unrunnable — including `bicg`, one of the few class-R benchmarks E1 needs.
    """
    size = _sizes_for(kernel).get("timing_size")
    return str(size) if size else None


# Flags that are part of the FIXED configuration: two arms of one comparison must agree on
# them, or the comparison measures them as well as its own variable. `--require-speedup` and
# the timing size are here because changing the campaign default on 2026-09-20 silently
# confounded E3, E4, E8 and E9, whose variant arms were paired against `full`.
# Every boolean that changes what an arm DOES. `llm-recon` and `llm-deps` were missing, so the
# check reported "no differences" for E4 — whose entire variable is those two — and would have
# passed an E4 whose cells were identical.
_FIXED_CONFIG_SWITCHES = ("require-speedup", "hotspots", "llm-pragmas", "fast-refresh",
                          "pragma-arbitration", "llm-recon", "llm-deps", "apply-patches",
                          "numeric-tolerance", "schedule-stress")


def _effective_config(spec: dict, benchmark: str) -> Dict[str, Any]:
    """What an arm actually runs with, for the compatibility check below."""
    flags = _common_flags() + list(spec.get("flags", []))
    cfg: Dict[str, Any] = {"timing_size": spec.get("timing_size", _common_timing_size())}
    for name in _FIXED_CONFIG_SWITCHES:
        cfg[name] = _last_switch_in(flags, name)
    for opt in ("--budget", "--evidence", "--restructure-depth", "--llm-recon-mode",
                "--min-runtime-share", "--prompt-omit", "--prompt"):
        vals = [flags[i + 1] for i, f in enumerate(flags[:-1]) if f == opt]
        cfg[opt] = vals[-1] if vals else None
    # Added per benchmark by _evidence_file_flags, not in `flags`: without it the launch
    # printout showed compiler_remarks_b1 and no_evidence_b1 as identical (e2_smoke, 23 Sep).
    cfg["--evidence-file"] = spec.get("evidence_file")
    cfg["runner"] = spec.get("runner", "agent")
    cfg["twin_of"] = spec.get("twin_of")
    return cfg


def _last_switch_in(flags: List[str], name: str) -> Optional[bool]:
    value: Optional[bool] = None
    for f in flags:
        if f == f"--{name}":
            value = True
        elif f == f"--no-{name}":
            value = False
    return value


def verify_arm_settings(arm_names: List[str], arms: Dict[str, dict], agent_repo: Path,
                        benchmarks: "str | List[str]") -> List[str]:
    """Ask the agent what it parsed, and compare with what each arm DECLARED.

    An arm's `settings` block names every argument that carries its purpose. Building the
    command line from flags and inheritance is not enough on its own: a changed default, a
    flag inherited from `common_flags`, or a typo can all leave an arm running something
    other than the experiment it serves — which happened twice on 2026-09-20 (the speed check
    became the default and confounded four matrix experiments; `--llm-pragmas` stopped being
    the default and changed the meaning of five arms). So the check is made against the
    agent's OWN parser, not against the harness's model of it: `--print-config` resolves the
    arguments and prints them, and every declared key must match.

    An arm's flags depend on the BENCHMARK too: under per-kernel timing a kernel with no
    timing size gets `--no-require-speedup` (`_timing_flags`). Checked against the run's first
    benchmark only, as this was until 2026-09-21, the answer depended on the order of the list:
    a timeable first benchmark hid that the untimeable ones run with the speed check off, and
    an untimeable first benchmark REFUSED the whole run, every arm "declaring
    require_speedup=True but parsed False" — E1's class R holds both kinds. So one
    representative of each timing situation present is checked, and where the harness itself
    switched the speed check off, what must hold is that consequence: `require_speedup` False,
    and `pragma_arbitration` — which decides by timing — False with it (D28).

    Returns a list of human-readable problems; empty means every arm runs what it declares.
    """
    problems: List[str] = []
    py = str(agent_repo / "venv" / "bin" / "python")
    wanted = [benchmarks] if isinstance(benchmarks, str) else list(benchmarks)
    for name in arm_names:
        # One representative per timing situation: timeable, and not.
        reps: Dict[bool, str] = {}
        for b in wanted or [""]:
            reps.setdefault("--no-require-speedup" in _timing_flags(arms[name], b), b)
        for speed_off, benchmark in sorted(reps.items()):
            problems += _verify_one_arm(name, arms[name], py, agent_repo, benchmark, speed_off)
    return problems


def _verify_one_arm(name: str, spec: dict, py: str, agent_repo: Path, benchmark: str,
                    speed_off: bool) -> List[str]:
    """`verify_arm_settings` for one arm on one benchmark; `speed_off` = the harness turned
    the speed check off for this kernel, which overrides what the arm declares for it."""
    where = f" [{benchmark}: no timing size, speed check off]" if speed_off else ""
    if spec.get("runner") and spec["runner"] != "twin":
        return []            # not the agent: no agent arguments exist to be declared or parsed
    # A twin (D38) parses the agent arm's arguments with the agent's own parser; its inherited
    # declaration is checked against what the TWIN parsed.
    module = "discopop_agent.twin" if spec.get("runner") == "twin" else "discopop_agent"
    declared = spec.get("settings")
    if not declared:
        return [f"{name}: no `settings` block — every arm must declare the arguments that "
                f"carry its purpose (arms.json `settings_note`)"]
    cmd = [py, "-m", module, "--discopop-dir", ".", "--source-file", "x.c",
           *_common_flags(), *spec.get("flags", []), *_timing_flags(spec, benchmark),
           *_evidence_file_flags(spec, benchmark, None, "", ""), "--print-config"]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          env={**os.environ, **_agent_env(agent_repo)}, timeout=120)
    if proc.returncode != 0:
        return [f"{name}{where}: the agent rejected this arm's arguments "
                f"({(proc.stderr or proc.stdout).strip().splitlines()[-1:] or ['?']})"]
    try:
        actual = json.loads(proc.stdout)
    except ValueError:
        return [f"{name}{where}: could not read the agent's resolved configuration"]
    problems: List[str] = []
    for key, want in declared.items():
        if speed_off and key in ("require_speedup", "pragma_arbitration"):
            want = False
        got = actual.get(key, "<absent>")
        if got != want:
            problems.append(f"{name}{where}: declares {key}={want!r} but the agent parsed {got!r}")
    return problems


def silent_interactions(arm_names: List[str], arms: Dict[str, dict], benchmark: str) -> List[str]:
    """Settings an arm passes that another of its settings makes INERT.

    These do not error — the agent accepts them and they simply stop meaning anything — so
    they are the ones that quietly change what an experiment measures. The prerequisites that
    DO error (`--llm-recon` without `--fast-refresh`, `--pragma-arbitration` without
    `--llm-pragmas`) are the agent's own job and are covered by its `arg-dependencies` check.
    """
    out: List[str] = []
    for name in arm_names:
        cfg = _effective_config(arms[name], benchmark)
        if cfg.get("hotspots") is False:
            share = cfg.get("--min-runtime-share")
            if share not in (None, "0", "0.0"):
                out.append(f"{name}: --min-runtime-share={share} is INERT — the share is a share "
                           f"of MEASURED runtime, and --no-hotspots removes the measurement; "
                           f"ranking falls back to the workload proxy and --min-workload, so this "
                           f"arm also queues regions the filter would have dropped")
        depth = cfg.get("--restructure-depth")
        if depth not in (None, "0") and cfg.get("fast-refresh"):
            out.append(f"{name}: --fast-refresh applies only at the LAST of {depth} levels; "
                       f"deeper ones get a full re-profile either way")
        if cfg.get("require-speedup") is False and cfg.get("timing_size") == "per_kernel":
            out.append(f"{name}: a timing size is set but the speed check is off — nothing times at it")
    return out


def check_arm_compatibility(arm_names: List[str], arms: Dict[str, dict]) -> List[str]:
    """Differences between the arms of one run, as human-readable lines.

    An experiment varies ONE thing. Two arms that also differ in the speed check, the timing
    size or the pragma mode measure that difference too, and the result cannot be attributed.
    This lists every setting on which the arms disagree so the caller can say whether each
    one is the experiment's variable or an accident.
    """
    if len(arm_names) < 2:
        return []
    cfgs = {n: _effective_config(arms[n], "") for n in arm_names}
    out: List[str] = []
    for key in sorted({k for c in cfgs.values() for k in c}):
        values = {n: c.get(key) for n, c in cfgs.items()}
        if len(set(map(str, values.values()))) > 1:
            out.append(f"{key}: " + ", ".join(f"{n}={v}" for n, v in values.items()))
    return out


def _common_timing_size() -> str:
    """The timing size every arm inherits (arms.json `common_timing_size`); "per_kernel" since
    2026-09-20 (D8). An arm overrides it with its own `timing_size`, e.g. "agent"."""
    return str(json.loads(ARMS_FILE.read_text()).get("common_timing_size", "agent"))


def _timing_flags(spec: dict, benchmark: str) -> List[str]:
    """Per-benchmark timing flags, and the speed check turned OFF where nothing is timeable.

    On a kernel with no timing size the speed check can only ever REJECT: every measurement is
    noise, and E10 showed what that costs — at the agent's small size the check deleted
    DiscoPoP's own pragmas in 10 of 21 trials. So rather than time such a kernel badly, the
    check is switched off for it and the fact is recorded per trial (`speed_check_off`) and in
    the manifest. The harness's own verification judges its speed afterwards, as always.
    """
    if spec.get("timing_size", _common_timing_size()) != "per_kernel":
        return []
    size = _timing_size(benchmark)
    if size is None:
        return ["--no-require-speedup"]
    return [f"--timing-cflags=-D{size}_DATASET"]


def _evidence_file_flags(spec: dict, bench: str, run_dir: Optional[Path], cc: str, cxx: str) -> List[str]:
    """`--evidence-file` for an arm whose evidence comes from ANOTHER tool (E2, D16).

    `"evidence_file": "compiler_remarks"` in an arm means: what the campaign's compiler itself
    reports about this benchmark's kernel (tools/compiler_remarks.py), generated once per
    benchmark per run under `<run>/evidence/<bench>/` — beside the profile, never inside it —
    with the commands that produced it. A kernel the compiler has nothing to say about still
    gets a file that SAYS so: that is a state of this evidence source, and an empty file
    would make the arm silently identical to `no_evidence` (the agent refuses one).
    """
    kind = spec.get("evidence_file")
    if not kind:
        return []
    if kind != "compiler_remarks":
        sys.exit(f"arms.json: unknown evidence_file kind {kind!r} (known: compiler_remarks)")
    if run_dir is None:                               # argument verification: any readable text
        probe = Path(tempfile.gettempdir()) / "dp_evidence_probe.txt"
        probe.write_text("probe: a remark\n")
        return ["--evidence-file", str(probe)]
    import compiler_remarks
    out_dir = run_dir / "evidence" / bench
    txt = out_dir / "compiler_remarks.txt"
    if not txt.exists():
        compiler_remarks.write(bench, out_dir, cc, cxx)
        if not txt.read_text().strip():
            txt.write_text("(the compiler's vectorizer and Polly report nothing about this code)\n")
    return ["--evidence-file", str(txt.resolve())]


def _verify_size(requested: str, kernel: str) -> tuple[str, Optional[bool]]:
    """(dataset size, speed measurable) for verification.

    ``per_kernel`` takes the kernel's verification size from T0.1. A kernel whose serial
    run reached the 1 s target at no runnable size is verified at the longest size T0.1
    could run and marked not speed-measurable: its correctness verdict stands, but a
    speedup cannot show on it. An explicit size is used as given (measurability unknown).
    """
    if requested != "per_kernel":
        return requested, None
    entry = _sizes_for(kernel) or None
    if entry is None:
        sys.exit(f"{kernel} is not in {KERNEL_SIZES_FILE.name}; run T0.1 for it or pass an "
                 f"explicit --verify-size")
    if entry.get("verification_size"):
        return str(entry["verification_size"]), True
    return str(entry["longest_measured"]["size"]), False


def _prepared_benchmarks() -> Dict[str, Path]:
    """'<suite>/<kernel>' -> directory holding the source file and meta.json."""
    out = {}
    for meta in sorted(PREPARED.glob("*/*/meta.json")):
        out[f"{meta.parent.parent.name}/{meta.parent.name}"] = meta.parent
    return out


def _source_name(bench_dir: Path) -> str:
    meta = json.loads((bench_dir / "meta.json").read_text())
    return meta.get("file") or f"{bench_dir.name}.cpp"


def _project_of(bench_dir: Path) -> Optional[dict]:
    """The `project` block of a MULTI-FILE benchmark's meta.json, or None for one file.

    {"units": [...], "include_dirs": [...], "cflags": [...], "ldflags": [...]} — paths
    relative to the benchmark directory. `file` in meta.json then names the unit that
    holds `main` and the packaging's own code."""
    meta = json.loads((bench_dir / "meta.json").read_text())
    proj = meta.get("project")
    return dict(proj) if proj else None


_TREE_SKIP = {".discopop", "__pycache__", "meta.json"}


def _copy_tree(src: Path, dst: Path) -> None:
    """Copy a project benchmark's sources (never a profile, never build products)."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        if any(part in _TREE_SKIP or part.endswith(".dSYM") for part in rel.parts):
            continue
        if item.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
        elif item.suffix in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".inc"):
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst / rel)


def _project_sources(root: Path) -> List[str]:
    """Every source and header of a project tree, relative, in a fixed order."""
    return sorted(str(p.relative_to(root)) for p in root.rglob("*")
                  if p.is_file() and p.suffix in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".inc")
                  and not any(part in _TREE_SKIP for part in p.relative_to(root).parts))


def _project_text(root: Path) -> str:
    """The whole project as one text, files in a fixed order — what `source_changed`, the
    pragma count and the scaffolding check are computed on."""
    return "".join(f"/* ==== {rel} ==== */\n{(root / rel).read_text(errors='replace')}\n"
                   for rel in _project_sources(root))


def _pragmas_added(original_text: str, final_text: str) -> int:
    """`#pragma omp` lines in the final text beyond those the original already had."""
    from collections import Counter as _Counter
    before = _Counter(l.strip() for l in original_text.splitlines() if "#pragma omp" in l)
    after = _Counter(l.strip() for l in final_text.splitlines() if "#pragma omp" in l)
    return sum((after - before).values())


def _project_agent_flags(proj: dict) -> List[str]:
    return ["--project-dir", ".",
            "--project-units", ",".join(proj["units"]),
            "--project-include", ",".join(proj.get("include_dirs") or []),
            *(["--project-cflags", " ".join(proj["cflags"])] if proj.get("cflags") else []),
            *(["--project-ldflags", " ".join(proj["ldflags"])] if proj.get("ldflags") else [])]


UNITY_NAME = "dp_harness_unity"


class PackageCorrupted(RuntimeError):
    """A packaged benchmark, or the run's archived copy of it, no longer matches what the
    packager wrote.  Raised instead of running, so one damaged trial can never feed the
    next: every trial starts from the archived copy, and this is what proves that copy."""


def _package_digest(root: Path, meta: dict) -> str:
    """sha256 of the benchmark's sources under `root`, computed exactly as the packagers
    compute `output_sha256`: one file's bytes, or — for a project — the texts of every
    generated file concatenated in sorted order of their relative paths."""
    if meta.get("project"):
        blob = "".join((root / rel).read_text() for rel in _project_sources(root)).encode()
        return hashlib.sha256(blob).hexdigest()
    return hashlib.sha256((root / Path(meta["file"]).name).read_bytes()).hexdigest()


def _tree_digest(root: Path) -> str:
    """sha256 over every file of a tree: relative path, size and bytes, in sorted order."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            rel = str(p.relative_to(root)).encode()
            h.update(rel + b"\0" + str(p.stat().st_size).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def check_package(bench: str, bench_dir: Path, profile_dir: Optional[Path] = None,
                  when: str = "") -> Dict[str, Any]:
    """Prove that what a trial starts from is exactly what the packager and the profiler
    produced.  Returns the record stored with the trial; raises PackageCorrupted on any
    difference.

    Three things are compared:
      * the prepared package against `output_sha256` in its meta.json — the packager's
        digest of the sources it generated;
      * the run's archived copy of the sources under `profiles/<bench>` against the
        prepared package;
      * the run's archived DiscoPoP profile (`profiles/<bench>/.discopop`, every file)
        against `profile_sha256` in profile.json, recorded when the profile was taken.
    The package is what every run copies from and the archived copy is what every trial
    copies from; no trial ever writes to either (the agent works in a fresh `work/` copy).
    This check turns that from an assumption into a guarantee: it runs at run start,
    before every trial and after every trial, and a difference stops the run instead of
    handing a modified program or profile to the next trial."""
    meta = json.loads((bench_dir / "meta.json").read_text())
    want = meta.get("output_sha256")
    got = _package_digest(bench_dir, meta)
    rec: Dict[str, Any] = {"checked": when or "now", "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                           "prepared_sha256": got, "packager_sha256": want}
    if want and got != want:
        raise PackageCorrupted(f"{bench}: the prepared package under {bench_dir} no longer matches "
                               f"what the packager wrote ({got[:12]} != {want[:12]}); regenerate it "
                               f"with the prepare tool — never run on a modified package")
    if profile_dir is not None and profile_dir.exists():
        try:
            copy = _package_digest(profile_dir, meta)
        except OSError as e:
            raise PackageCorrupted(f"{bench}: the run's archived sources under {profile_dir} "
                                   f"cannot be read ({e}); delete that directory to re-profile "
                                   f"from the package")
        rec["archived_sha256"] = copy
        if copy != got:
            raise PackageCorrupted(f"{bench}: the run's archived copy of the sources under "
                                   f"{profile_dir} differs from the prepared package "
                                   f"({copy[:12]} != {got[:12]}) — something wrote where no trial "
                                   f"may; delete that directory to re-profile from the package")
        prof_json = profile_dir / "profile.json"
        if (profile_dir / ".discopop").exists() and prof_json.exists():
            prof = json.loads(prof_json.read_text())
            now = _tree_digest(profile_dir / ".discopop")
            rec["profile_sha256"] = now
            if "profile_sha256" not in prof:
                # a profile taken before digests were recorded: fixed from this moment on
                prof["profile_sha256"], prof["profile_sha256_recorded"] = now, when or "now"
                prof_json.write_text(json.dumps(prof, indent=2) + "\n")
            elif prof["profile_sha256"] != now:
                raise PackageCorrupted(f"{bench}: the run's archived DiscoPoP profile under "
                                       f"{profile_dir / '.discopop'} changed since it was taken "
                                       f"({now[:12]} != {prof['profile_sha256'][:12]}) — delete "
                                       f"that directory to re-profile from the package")
    rec["ok"] = True
    return rec


def _excluded_functions(bench_dir: Path) -> List[str]:
    """Functions the packaging declares out of scope (output, setup, its own helpers)."""
    meta = json.loads((bench_dir / "meta.json").read_text())
    return list(meta.get("exclude_functions") or [])


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def _kill_group(p: "subprocess.Popen[Any]") -> None:
    """Kill the whole process group, not just the child.

    `subprocess.run(timeout=…)` kills only the process it started. DiscoPoP's wrappers are
    shell scripts that exec the compiler, so a timeout left `clang` running: T0.6's compile
    of NPB `lu` kept a core busy for over an hour after its timeout, with no parent left to
    wait for it. Every command here therefore starts in its own process group, which is then
    killed as a whole.
    """
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        p.kill()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def _run(cmd: List[str], cwd: Path, env: Optional[dict] = None, timeout: int = 3600,
         log: Optional[Path] = None) -> Tuple[int, float, str]:
    """Run a command; stream its output to `log` if given. Returns (rc, seconds, tail)."""
    t0 = time.perf_counter()
    if log is not None:
        with log.open("w") as fh:
            p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                _kill_group(p)
                rc = -9
        tail = "\n".join(log.read_text(errors="replace").splitlines()[-15:])
        return rc, time.perf_counter() - t0, tail
    q = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        out, err = q.communicate(timeout=timeout)
        return q.returncode, time.perf_counter() - t0, (out + err)[-2000:]
    except subprocess.TimeoutExpired:
        _kill_group(q)
        return -9, time.perf_counter() - t0, "timeout"


# A program may report the time of its computation (PolyBench: the kernel) on stderr.
REGION_RE = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)\s*$", re.M)


def _run_binary_full(binary: Path, cwd: Path, threads: Optional[int], timeout: int = 1800,
                     args: Optional[List[str]] = None) -> Tuple[int, float, str, Optional[float]]:
    """(rc, wall seconds, stdout, timed-region seconds or None)."""
    env = dict(os.environ)
    if threads is not None:
        env["OMP_NUM_THREADS"] = str(threads)
    t0 = time.perf_counter()
    try:
        p = subprocess.run([str(binary), *(args or [])], cwd=cwd, env=env, capture_output=True,
                           text=True, timeout=timeout)
        marks = REGION_RE.findall(p.stderr)
        region = sum(float(x) for x in marks) if marks else None
        return p.returncode, time.perf_counter() - t0, p.stdout, region
    except subprocess.TimeoutExpired:
        return -9, time.perf_counter() - t0, "", None


def _run_binary(binary: Path, cwd: Path, threads: Optional[int], timeout: int = 1800,
                args: Optional[List[str]] = None) -> Tuple[int, float, str]:
    rc, wall, out, _ = _run_binary_full(binary, cwd, threads, timeout, args)
    return rc, wall, out


def _dump_rel_err(a: str, b: str) -> Optional[float]:
    """Largest relative difference between two full value dumps, or None/inf.

    The dump is one value per line. Comparing the text byte-for-byte treats a correct
    parallel REDUCTION as a wrong answer: summing in a different order moves the last
    digits (`md`: 0.00042827175869921715 against …42, a relative 1e-16), and `md`'s final
    program was classified BROKEN although its digest agreed exactly. The same relative
    tolerance the digest already uses is applied here instead, so reordered arithmetic
    passes while a real change does not — the Jacobi-for-Gauss-Seidel rewrite differs by
    3.8e-7, eight orders of magnitude above the tolerance.

    Returns inf when the dumps cannot be compared at all (different length, empty, or a
    non-numeric token), which is treated exactly as a wrong answer.
    """
    la, lb = a.split(), b.split()
    if not la or len(la) != len(lb):
        return float("inf")
    worst = 0.0
    for x, y in zip(la, lb):
        if x == y:
            continue
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            return float("inf")
        if math.isnan(fx) or math.isnan(fy):
            return float("inf")
        scale = max(abs(fx), abs(fy), 1e-300)
        worst = max(worst, abs(fx - fy) / scale)
    return worst


def _digest(text: str) -> Optional[Dict[str, float]]:
    vals = dict(re.findall(r"^(pb_\w+) (\S+)$", text, re.M))
    try:
        return {k: float(v) for k, v in vals.items()} if len(vals) == 3 else None
    except ValueError:
        return None


def _digest_rel_err(a: Dict[str, float], b: Dict[str, float]) -> float:
    if a["pb_values"] != b["pb_values"]:
        return float("inf")
    err = 0.0
    for k in ("pb_sum", "pb_wsum"):
        scale = max(abs(a[k]), abs(b[k]), 1e-300)
        err = max(err, abs(a[k] - b[k]) / scale)
    return err


# ---------------------------------------------------------------------------
# Trial phases
# ---------------------------------------------------------------------------

def profile_once(bench_dir: Path, src_name: str, dest: Path, agent_repo: Path, timeout: int) -> dict:
    """DiscoPoP instrument -> run -> explore, into `dest`. The trials copy from here."""
    dest.mkdir(parents=True, exist_ok=True)
    env = _agent_env(agent_repo)
    is_c = _is_c(Path(src_name))
    wrapper = "discopop_cc" if is_c else "discopop_cxx"
    rec: dict = {"wrapper": wrapper}
    proj = _project_of(bench_dir)
    unity: Optional[Path] = None
    shutil.copy2(bench_dir / "meta.json", dest / "meta.json")   # provenance: which package
    if proj is None:
        shutil.copy2(bench_dir / src_name, dest / src_name)
        instrument = [wrapper, src_name, "-o", "a.out"] + (["-lm"] if is_c else [])
    else:
        # A multi-file program is profiled through ONE generated unit that includes every
        # unit. Profiled unit by unit, this DiscoPoP build gives loops outside main's unit
        # no loop states and reports recurrences there as Do-All; through a unity unit the
        # analysis equals that of the merged file, and FileMapping still names the real
        # files and lines (THESIS_EXPERIMENTS.md §5g D6; agent docs/MULTIFILE.md).
        _copy_tree(bench_dir, dest)
        unity = dest / f"{UNITY_NAME}{'.c' if is_c else '.cpp'}"
        unity.write_text("".join(f'#include "{u}"\n' for u in proj["units"]))
        # By ABSOLUTE path: compiled by a relative name, clang records the included units
        # as "./src/x.c", and the explorer's AST-based variable classification then
        # matched nothing — every Do-All lost its clauses (a missing `private` is a race).
        instrument = ([wrapper, str(unity.resolve()), f"-I{dest.resolve()}",
                       *[f"-I{(dest / d).resolve()}" for d in proj.get("include_dirs") or []],
                       *(proj.get("cflags") or []), "-o", "a.out", *(proj.get("ldflags") or [])]
                      + (["-lm"] if is_c else []))
        rec["layout"] = "project"
        rec["units"] = list(proj["units"])
    steps = [
        ("instrument", instrument, dest),
        ("profiled_run", ["./a.out"], dest),
    ]
    for step, cmd, cwd in steps:
        rc, secs, tail = _run(cmd, cwd, env, timeout, log=dest / f"{step}.log")
        rec[f"{step}_s"] = round(secs, 2)
        if unity is not None and step == "instrument":
            unity.unlink(missing_ok=True)      # not part of the program
        if rc != 0:
            rec["error"] = f"{step} failed (rc={rc}): {tail[-500:]}"
            return rec
    # DiscoPoP's explorer is not deterministic on a fixed profile and can crash on one
    # attempt and succeed on the next (an IndexError in TaskGraph.recursive_assignment:
    # `pathfinder` crashed in 15 of 20 attempts on one profile, T0.7; 20 attempts leave a
    # 0.75^20 ≈ 0.3 % chance of losing the benchmark). The profile is
    # already taken and stays untouched, so another attempt is only another draw of the
    # explorer's output; every failed attempt is recorded, and a benchmark is lost only
    # when all attempts fail.
    # A STALL is a draw too — corrected 2026-09-21. The night the stall was found it looked
    # like a property of two loops (`s291` 5,403 s, `s3112` still running at 80 minutes, 4 s
    # for every other loop), so a timeout stopped the loop: 20 retries at the 90-minute phase
    # limit is 30 hours for one benchmark. The next draws showed it is RANDOM (`s3112`: 5.8 s),
    # and over 166 draws of the campaign's benchmarks the explorer needed a median of 3.5 s and
    # at most 33 s while 7 % of the draws never finished — each of which cost a benchmark its
    # whole run, all arms and repeats, because a run profiles once. So an attempt gets a SHORT
    # limit (the agent's own, `profiling/tools.py`: ~18x the slowest legitimate run) and a
    # stalled draw is repeated, at most EXPLORER_STALL_ATTEMPTS times: worst case 50 minutes,
    # typical cost of a stall 10.
    failures: List[str] = []
    total = 0.0
    stalls = 0
    stall_limit = min(timeout, EXPLORER_STALL_S) if EXPLORER_STALL_S > 0 else timeout
    for attempt in range(1, EXPLORER_ATTEMPTS + 1):
        shutil.rmtree(dest / ".discopop" / "explorer", ignore_errors=True)
        rc, secs, tail = _run(["discopop_explorer"], dest / ".discopop", env, int(stall_limit),
                              log=dest / f"explore_{attempt}.log")
        total += secs
        if rc == 0:
            break
        failures.append(tail.strip().splitlines()[-1][:200] if tail.strip() else f"rc={rc}")
        if rc == -9:
            stalls += 1
            failures[-1] = f"stalled: no result after {secs:.0f}s (a random stall, L5; draw repeated)"
            if stalls >= EXPLORER_STALL_ATTEMPTS:
                break
    timed_out = rc == -9
    rec["explore_stalls"] = stalls
    rec["explore_s"] = round(total, 2)
    rec["explore_success_s"] = round(secs, 2) if rc == 0 else None   # the draw that finished
    rec["explore_attempts"] = attempt
    rec["explore_timed_out"] = timed_out
    rec["explore_failures"] = failures
    if rc != 0:
        rec["error"] = f"explore failed on all {attempt} attempts ({stalls} stalled): {failures[-1]}"
        return rec
    patterns = dest / ".discopop" / "explorer" / "patterns.json"
    if patterns.exists():
        data = json.loads(patterns.read_text()).get("patterns", {})
        rec["patterns"] = {k: len(v) for k, v in data.items()}
    rec["profile_sha256"] = _tree_digest(dest / ".discopop")   # verified around every trial
    return rec


def _parse_agent_log(log: str) -> dict:
    rec: dict = {
        "llm_calls": log.count("] Calling "),
        # A failed call yields no candidate, so a trial's call count overstates
        # the work done unless the failures are counted beside it. The first
        # server pilot recorded 9 calls and a clean "no-change" while all 9 had
        # failed on a rejected credential (§5c).
        "llm_call_failures": log.count("LLM call failed"),
        # DiscoPoP's explorer crashing on an unchanged profile and being retried by the
        # agent (profiling/tools.py run_explorer); a draw, not a verdict, but counted.
        "explorer_retries": len(re.findall(r"\[explorer\] attempt \d+ failed", log)),
        "explorer_stalls": len(re.findall(r"\[explorer\] attempt \d+ stalled", log)),
        "reverts": log.count("— reverting"),
        # What each profile refresh after a rewrite actually WAS. `fallback` = a fast
        # refresh that proved unusable and was replaced by a full re-profile: a trial of a
        # fast-refresh arm with a fallback in it did not get the treatment its arm names, and
        # E3's read-out has to be able to say how often that happened.
        "refresh_fast": log.count("[refresh] kind=fast"),
        "refresh_full": log.count("[refresh] kind=full"),
        "refresh_fallback": log.count("[refresh] kind=fallback"),
        "runtime_remeasurements": log.count("Re-measured runtimes:"),
        # D33: pragmas that were safe but slower ALONE, deferred to a joint judgement, and
        # the sets that judgement kept (one per file). A trial whose win came from a set is
        # a D33 result — E1 had none, the agent could not build one.
        # Only Phase B's marker: Phase A prints a bare "└─ DEFERRED" for a region DiscoPoP
        # already has a pattern for (deferred to Phase B), which counted as D33 until the
        # E2 smoke of 23 Sep showed 2 on a trial with no D33 deferral at all.
        "phase_b_deferred": log.count("└─ DEFERRED (slower alone)"),
        "phase_b_joint_kept": log.count("pragma(s) APPLIED together"),
        # D32: what the floor (DiscoPoP's own program) decided. `original` — DiscoPoP alone
        # keeps nothing, so the floor is the original (every class-R loop of E1); `same` — the
        # finished program is DiscoPoP's own; `agent` — the agent's program kept, not slower
        # than the floor; `discopop` — the agent's program was slower and DiscoPoP's shipped.
        # None: no floor was built (the DiscoPoP-alone arm itself, or a run before D32).
        "dp_floor": ("discopop" if "[floor] shipped DiscoPoP's own program" in log
                     else "agent" if "[floor] kept the agent's program" in log
                     else "same" if "[floor] the finished program is DiscoPoP's own" in log
                     else "original" if "[floor] DiscoPoP alone keeps nothing" in log else None),
        # Gate attribution. Phase A judges the model's rewrites ("Stage 'x' failed"),
        # Phase B judges DiscoPoP's pragmas ("gate failed at 'x'").
        "gate_failures_phase_a": dict(Counter(re.findall(r"Stage '([a-z_]+)' failed", log))),
        "gate_failures_phase_b": dict(Counter(re.findall(r"gate failed at '([a-z_]+)'", log))),
        "gate_passes_phase_a": log.count("Quality gate PASSED"),
        "region_verdicts": dict(Counter(re.findall(r"└─ ([A-Z]+)", log))),
        "settle_dropped": len(re.findall(r"^\s+· ", log.split("SETTLING", 1)[1], re.M))
        if "SETTLING" in log else 0,
    }
    m = re.search(r"DiscoPoP proposes (\d+) applicable pattern\(s\) unaided; (\d+) of them", log)
    if m:
        rec["baseline_claimed"], rec["baseline_pragmas"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"SUMMARY: (\d+) rewrite\(s\) kept\s+\|\s+(\d+) pragma\(s\) applied"
                  r"(?: \((\d+) DiscoPoP \+ (\d+) LLM\))?\s+\|\s+(\d+) skipped", log)
    if m:
        rec["rewrites_kept"], rec["pragmas_applied"] = int(m.group(1)), int(m.group(2))
        rec["pragmas_discopop"] = int(m.group(3)) if m.group(3) else int(m.group(2))
        rec["pragmas_llm"] = int(m.group(4)) if m.group(4) else 0
        rec["regions_skipped"] = int(m.group(5))
    m = re.search(r"\[(BEAT|MATCHED|BELOW)\]", log)
    if m:
        rec["agent_verdict"] = m.group(1)
    # A twin (D38): how many regions its model was asked about, how many it edited, and how
    # many DiscoPoP pragmas went in afterwards with nothing checked — the model's share and
    # DiscoPoP's unchecked share of the result, told apart.
    m = re.search(r"SUMMARY: (\d+) region\(s\) asked\s+\|\s+(\d+) edited\s+\|\s+(\d+) DiscoPoP "
                  r"pragma\(s\) inserted unchecked", log)
    if m:
        rec["twin_asked"], rec["twin_edited"], rec["twin_dp_inserted"] = map(int, m.groups())
        rec["twin_reprofile_failed"] = "the re-profile failed" in log
    return rec


def _summarise_usage(path: Path) -> Optional[dict]:
    """Token and cost totals from the agent's per-call usage log (None if absent)."""
    if not path.exists():
        return None
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue

    def tok(r: dict, *keys: str) -> int:
        u = r.get("usage") or {}
        return sum(int(u.get(k) or 0) for k in keys)
    return {
        "calls_recorded": len(rows),
        "input_tokens": sum(tok(r, "input_tokens", "prompt_tokens") for r in rows),
        "output_tokens": sum(tok(r, "output_tokens", "completion_tokens") for r in rows),
        "cache_read_input_tokens": sum(tok(r, "cache_read_input_tokens") for r in rows),
        "cache_creation_input_tokens": sum(tok(r, "cache_creation_input_tokens") for r in rows),
        "cost_usd": round(sum(float(r.get("cost_usd") or 0) for r in rows), 4),
        "model_seconds": round(sum(float(r.get("duration_ms") or 0) for r in rows) / 1000, 1),
    }


def verify(trial: Path, ext: str, cc: str, cxx: str, verify_size: str, threads: List[int],
           repeats: int, seed: Optional[str] = None,
           final_flags: Optional[List[str]] = None, project: Optional[dict] = None) -> dict:
    """The driver's own verdict on the candidate source — never the agent's.

    `final_flags` are extra compile flags for the CANDIDATE build only, never for the
    original it is judged against. That is what lets a compiler baseline be verified the
    same way as a rewrite: Polly is the unchanged source built with its own flags, so the
    candidate differs from the original by the compiler, not by the code.
    """
    vdir = trial / "verify"
    vdir.mkdir(exist_ok=True)
    # One file, or — for a project benchmark — the directory holding the whole program.
    orig, final = ((trial / "original", trial / "final") if project is not None
                   else (trial / f"original{ext}", trial / f"final{ext}"))
    is_c = ext == ".c"
    compiler = cc if is_c else cxx
    rec: dict = {"verify_size": verify_size, "threads": threads, "repeats": repeats,
                 "compiler": compiler, "final_flags": list(final_flags or [])}

    def build(src: Path, out: str, extra: List[str], openmp: bool) -> bool:
        if project is not None:
            # Every unit of the program, the way it is really built — not a merged file.
            inputs = ([str(src / u) for u in project["units"]]
                      + [f"-I{src / d}" for d in project.get("include_dirs") or []]
                      + list(project.get("cflags") or []))
            tail_flags = list(project.get("ldflags") or [])
        else:
            inputs, tail_flags = [str(src)], []
        rc, _, tail = _run([compiler, "-O2", *extra, *inputs, "-o", str(vdir / out),
                            *tail_flags, *_toolchain_flags(openmp, is_c)], vdir, timeout=600)
        if rc != 0:
            rec.setdefault("build_errors", {})[out] = tail[-400:]
        return rc == 0

    # (a) exact full dump at the agent size, with the parallel build at max threads
    if build(orig, "orig_dump", ["-DPB_FULL_DUMP"], False) and \
            build(final, "final_dump", ["-DPB_FULL_DUMP", *(final_flags or [])], True):
        _, _, out_o = _run_binary(vdir / "orig_dump", vdir, None)
        _, _, out_f = _run_binary(vdir / "final_dump", vdir, max(threads))
        rec["dump_exact"] = out_o == out_f and len(out_o) > 0
        # Byte-equality is recorded, but the verdict uses the same relative tolerance as
        # the digest: a correct parallel reduction reorders additions (see _dump_rel_err).
        rec["dump_max_rel_err"] = _dump_rel_err(out_o, out_f) if len(out_o) > 0 else float("inf")
        if seed:
            # The shipped input can be a fixed point of the kernel (seidel-2d); the
            # perturbed one is not, so an algorithm change shows up here.
            _, _, so = _run_binary(vdir / "orig_dump", vdir, None, args=[seed])
            _, _, sf = _run_binary(vdir / "final_dump", vdir, max(threads), args=[seed])
            rec["seed"] = seed
            rec["dump_exact_seeded"] = so == sf and len(so) > 0
            rec["dump_seeded_max_rel_err"] = _dump_rel_err(so, sf) if len(so) > 0 else float("inf")
    else:
        rec["dump_exact"] = None
        rec["dump_max_rel_err"] = None

    # (b)+(c) digest at the verify size, timed
    size_flag = [f"-D{verify_size}_DATASET"]
    if not (build(orig, "orig_seq", size_flag, False)
            and build(final, "final_par", [*size_flag, *(final_flags or [])], True)):
        rec["status"] = "verify_build_failed"
        return rec
    seq_times: List[float] = []
    seq_kernel: List[float] = []
    seq_digest = None
    for _ in range(repeats):
        rc, t, out, region = _run_binary_full(vdir / "orig_seq", vdir, None)
        if rc != 0:
            rec["status"] = "original_run_failed"
            return rec
        seq_times.append(t)
        if region is not None:
            seq_kernel.append(region)
        seq_digest = _digest(out)
    rec["seq_median_s"] = round(statistics.median(seq_times), 4)
    # Speedup is judged on the timed computation when the original reports it for every
    # run; whole-program time (allocation, initialisation, output) is kept alongside.
    kernel_basis = len(seq_kernel) == repeats
    if kernel_basis:
        rec["seq_kernel_median_s"] = round(statistics.median(seq_kernel), 6)
    rec["timing_basis"] = "kernel" if kernel_basis else "program"

    rec["par"] = {}
    worst_err, stable = 0.0, True
    for t_count in threads:
        times, digests = [], []
        kernels: List[float] = []
        for _ in range(repeats):
            rc, t, out, region = _run_binary_full(vdir / "final_par", vdir, t_count)
            if rc != 0:
                rec["status"] = f"final_run_failed_T{t_count}"
                return rec
            times.append(t)
            if region is not None:
                kernels.append(region)
            digests.append(_digest(out))
        if seq_digest is None or any(d is None for d in digests):
            rec["status"] = "no_digest"
            return rec
        errs = [_digest_rel_err(seq_digest, d) for d in digests]  # type: ignore[arg-type]
        if len({json.dumps(d, sort_keys=True) for d in digests}) > 1:
            stable = False
        worst_err = max(worst_err, *errs)
        med = statistics.median(times)
        program_speedup = round(rec["seq_median_s"] / med, 3) if med else None
        entry = {"median_s": round(med, 4), "program_speedup": program_speedup,
                 "max_rel_err": max(errs)}
        if kernel_basis and len(kernels) == repeats:
            kmed = statistics.median(kernels)
            entry["kernel_median_s"] = round(kmed, 6)
            entry["kernel_speedup"] = round(rec["seq_kernel_median_s"] / kmed, 3) if kmed else None
            entry["speedup"] = entry["kernel_speedup"]
        else:
            # The final program lost its timer (a rewrite removed the markers): fall back to
            # whole-program time for this thread count, and say so.
            entry["speedup"] = program_speedup
            if kernel_basis:
                entry["timer_missing_in_final"] = True
        rec["par"][str(t_count)] = entry
    rec["digest_max_rel_err"] = worst_err
    rec["stable_at_fixed_threads"] = stable
    # Moving work out of the timed region would show up as a kernel gain the whole program
    # does not share. Recorded, not re-classified: initialisation loops also speed up.
    rec["kernel_program_disagree"] = any(
        (p.get("kernel_speedup") or 0) >= FASTER_THRESHOLD and (p.get("program_speedup") or 0) < 1.0
        for p in rec["par"].values())
    if seed:
        _, _, so = _run_binary(vdir / "orig_seq", vdir, None, args=[seed])
        _, _, sf = _run_binary(vdir / "final_par", vdir, max(threads), args=[seed])
        do, df = _digest(so), _digest(sf)
        if do is None or df is None or not all(math.isfinite(x) for x in (*do.values(), *df.values())):
            rec["digest_seeded_rel_err"] = None  # perturbed input not usable for this kernel
        else:
            rec["digest_seeded_rel_err"] = _digest_rel_err(do, df)
    rec["status"] = "ok"
    for p in vdir.iterdir():  # binaries are regenerable; keep the trial directory small
        p.unlink()
    vdir.rmdir()
    return rec


def classify(t: dict) -> str:
    """One outcome per trial, judged from the independent verification."""
    if t.get("status") in ("profile_error", "agent_timeout", "agent_error"):
        return t["status"].upper()
    if (t.get("scaffold") or {}).get("ok") is False:
        # The rewrite changed the instrument — the timer, the perturbed input or the digest —
        # so neither the speed nor the correctness verdict measures the program any more.
        # Checked before them, and never counted as a result (see scaffold.py).
        return "SCAFFOLD_MODIFIED"
    v = t.get("verify", {})
    if v.get("status") != "ok":
        # The ORIGINAL ran (its sequential timing was taken) and the FINAL program did not,
        # on the same input: that is a wrong program, not a broken instrument.  pilot3,
        # floyd-warshall: a rewrite added `DATA_TYPE temp[N][N]` on the stack — fine at the
        # agent's SMALL size, a segmentation fault at LARGE.  Every other non-ok status
        # (a build that failed, the original not running, no digest) stays VERIFY_FAILED.
        if str(v.get("status", "")).startswith("final_run_failed") and t.get("kind") != "baseline":
            return "BROKEN"
        return "VERIFY_FAILED"
    # The dumps are judged by relative error, not byte-equality: a correct parallel
    # reduction moves the last digits (md, 2026-09-17). Older records have no
    # `dump_max_rel_err`; for those the exact flags still decide, so a re-scored old run
    # keeps its verdict rather than silently turning green.
    dump_err = v.get("dump_max_rel_err")
    seeded_err = v.get("dump_seeded_max_rel_err")
    dump_wrong = (dump_err > DIGEST_REL_TOL if dump_err is not None
                  else v.get("dump_exact") is False)
    seeded_wrong = (seeded_err > DIGEST_REL_TOL if seeded_err is not None
                    else v.get("dump_exact_seeded") is False)
    if (v.get("digest_max_rel_err", 0) > DIGEST_REL_TOL or not v.get("stable_at_fixed_threads", True)
            or dump_wrong or seeded_wrong
            or (v.get("digest_seeded_rel_err") or 0) > DIGEST_REL_TOL):
        return "BROKEN"
    if t.get("kind") != "baseline":
        # A baseline is a parallelization by construction — an expert's pragmas, another
        # system's released output, or a compiler flag that changes no source at all — so
        # only the agent's own trials can land in "no-change" or "changed-not-parallel".
        if not t.get("source_changed"):
            return "no-change"
        if t.get("pragmas_in_final", 0) == 0:
            return "changed-not-parallel"
    if v.get("speed_measurable") is False:
        # T0.1 found no runnable size at which this kernel's serial run reaches 1 s:
        # thread start-up outweighs the computation, so its ratio is no speed verdict.
        # Correctness was judged above; speed statistics leave this trial out.
        return "parallel-speed-not-measurable"
    best = max((p.get("speedup") or 0) for p in v.get("par", {}).values()) if v.get("par") else 0
    return "FASTER" if best >= FASTER_THRESHOLD else "parallel-not-faster"


def _agent_explorer_limit(profile_dir: Path) -> int:
    """The agent's explorer limit for this benchmark: AGENT_EXPLORER_FACTOR x its own measured
    explorer run, at least AGENT_EXPLORER_FLOOR_S; EXPLORER_STALL_S when nothing was measured.
    Profiles taken before the field existed: the total minus the stalled draws' limits."""
    try:
        prof = json.loads((profile_dir / "profile.json").read_text())
    except (OSError, ValueError):
        return EXPLORER_STALL_S
    t = prof.get("explore_success_s")
    if t is None and prof.get("explore_s") is not None and not prof.get("explore_timed_out"):
        t = float(prof["explore_s"]) - EXPLORER_STALL_S * int(prof.get("explore_stalls") or 0)
    if not t or t <= 0:
        return EXPLORER_STALL_S
    return int(max(AGENT_EXPLORER_FLOOR_S, math.ceil(AGENT_EXPLORER_FACTOR * float(t))))


def run_trial(bench: str, bench_dir: Path, profile_dir: Path, trial: Path, arm: str,
              arm_flags: List[str], model: str, a: argparse.Namespace, cc: str, cxx: str) -> dict:
    src_name = _source_name(bench_dir)
    ext = Path(src_name).suffix
    trial.mkdir(parents=True, exist_ok=True)
    work = trial / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    proj = _project_of(bench_dir)
    if proj is None:
        shutil.copy2(profile_dir / src_name, work / src_name)
    else:
        _copy_tree(profile_dir, work)
    shutil.copytree(profile_dir / ".discopop", work / ".discopop", symlinks=True)
    # DiscoPoP identifies source files by ABSOLUTE path (FileMapping.txt). The copy
    # lives elsewhere, so a tool that registers the source again — the agent's hotspot
    # detection does — would add it as a NEW file id, and no measurement would match
    # the profile's regions: ranking silently fell back to the static proxy (found on
    # the seidel-2d smoke run). Point the mapping at the copy.
    fmap = work / ".discopop" / "FileMapping.txt"
    if fmap.exists():
        text = fmap.read_text()
        if proj is None:
            for old in {str(profile_dir / src_name), str((profile_dir / src_name).resolve())}:
                text = text.replace(old, str((work / src_name).resolve()))
        else:
            # every file of the project moved with it
            for old in {str(profile_dir) + os.sep, str(profile_dir.resolve()) + os.sep}:
                text = text.replace(old, str(work.resolve()) + os.sep)
        fmap.write_text(text)
    if proj is None:
        shutil.copy2(profile_dir / src_name, trial / f"original{ext}")
    else:
        shutil.rmtree(trial / "original", ignore_errors=True)
        _copy_tree(profile_dir, trial / "original")

    rec: dict = {"benchmark": bench, "kernel": bench_dir.name, "source": src_name, "arm": arm,
                 "model": model, "arm_flags": arm_flags,
                 "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "host": socket.gethostname(),
                 "host_load_start": list(os.getloadavg())}
    if _load_arms().get(arm, {}).get("runner") == "bare_llm":
        # The bare-LLM baseline (discopop_agent/bare_llm.py): the same model through the same
        # client, given the program and asked to parallelize it — no DiscoPoP, no gate, one
        # attempt. It takes none of the agent's arguments, so none are passed: common flags,
        # timing flags and --check-input all configure a pipeline this arm does not have.
        # Only the runner arm's OWN flags (e.g. `--prompt contract`, D37), never the common ones.
        cmd = [str(Path(a.agent_repo) / "venv" / "bin" / "python"), "-m", "discopop_agent.bare_llm",
               *(["--source-file", src_name] if proj is None else _project_agent_flags(proj)),
               "--model", model, *_load_arms().get(arm, {}).get("flags", []),
               *(["--exclude-functions", ",".join(_excluded_functions(bench_dir))]
                 if _excluded_functions(bench_dir) else [])]
    else:
        # The agent — or its twin (D38), which takes the agent arm's arguments unchanged (they
        # are inherited in `resolve_twins`) and runs the agent's own code up to each model call,
        # with no gate after it.
        twin = _load_arms().get(arm, {}).get("runner") == "twin"
        cmd = [str(Path(a.agent_repo) / "venv" / "bin" / "python"), "-m",
               "discopop_agent.twin" if twin else "discopop_agent",
               *(["--source-file", src_name] if proj is None else _project_agent_flags(proj)),
               "--discopop-dir", ".discopop",
               "--provider", a.provider, "--model", model, "--edit-mode", a.edit_mode,
               *arm_flags, *(["--check-input", a.check_seed] if a.check_seed else []),
               *(["--exclude-functions", ",".join(_excluded_functions(bench_dir))]
                 if _excluded_functions(bench_dir) else []),
               *(["--min-runtime-share", str(a.min_runtime_share)] if a.min_runtime_share else []),
               "--explorer-timeout", str(_agent_explorer_limit(profile_dir)),
               *a.agent_arg]
    rec["agent_cmd"] = cmd
    print(f"    agent: {' '.join(cmd[3:])}", flush=True)
    print(f"    log:   tail -f {trial / 'agent.log'}", flush=True)
    env = _agent_env(Path(a.agent_repo))
    usage_file = trial / "llm_usage.jsonl"          # written by the agent, one line per call
    usage_file.unlink(missing_ok=True)
    env["DP_LLM_USAGE_LOG"] = str(usage_file)
    rc, secs, tail = _run(cmd, work, env, a.timeout, log=trial / "agent.log")
    rec["agent_s"], rec["agent_rc"] = round(secs, 1), rc
    rec.update(_parse_agent_log((trial / "agent.log").read_text(errors="replace")))
    rec["llm_usage"] = _summarise_usage(usage_file)
    if rc == -9:
        rec["status"] = "agent_timeout"
    elif rc != 0:
        rec["status"], rec["agent_error"] = "agent_error", tail[-800:]

    if proj is None:
        final_text = (work / src_name).read_text()
        original_text = (trial / f"original{ext}").read_text()
        (trial / f"final{ext}").write_text(final_text)
    else:
        # The program is a set of files: everything below — changed or not, the
        # scaffolding check, the pragma count, the diff — is computed on all of them.
        shutil.rmtree(trial / "final", ignore_errors=True)
        _copy_tree(work, trial / "final")
        final_text, original_text = _project_text(trial / "final"), _project_text(trial / "original")
        rec["layout"] = "project"
        rec["files_changed"] = [r for r in _project_sources(trial / "original")
                                if not (trial / "final" / r).exists()
                                or (trial / "final" / r).read_text(errors="replace")
                                != (trial / "original" / r).read_text(errors="replace")]
    rec["source_changed"] = final_text != original_text
    rec["scaffold"] = scaffold.check(original_text, final_text)
    # Pragmas the run ADDED.  In a project the count must not include pragmas the original
    # carries in code that is never compiled (polybench.c holds nine inside its PAPI
    # block), or "changed-not-parallel" could never be reached.
    rec["pragmas_added"] = _pragmas_added(original_text, final_text)
    if rec["scaffold"]["ok"] is False:
        print("    scaffolding modified: " + "; ".join(rec["scaffold"]["problems"][:2]), flush=True)
    rec["pragmas_in_final"] = (final_text.count("#pragma omp") if proj is None
                               else rec["pragmas_added"])
    if rec["source_changed"]:
        (trial / "changes.diff").write_text("".join(difflib.unified_diff(
            original_text.splitlines(True), final_text.splitlines(True),
            f"original{ext}", f"final{ext}")))
    patches = work / ".discopop" / "agent_patches"
    if patches.exists():
        shutil.copytree(patches, trial / "agent_patches", dirs_exist_ok=True)
    index = trial / "agent_patches" / "candidates.jsonl"
    rec["candidates_recorded"] = sum(1 for _ in index.open()) if index.exists() else 0

    if rec.get("status") is None:
        print("    verify ...", flush=True)
        t0 = time.perf_counter()
        vsize, measurable = _verify_size(a.verify_size, bench)
        rec["verify"] = verify(trial, ext, cc, cxx, vsize, a.threads, a.repeats,
                               a.check_seed or None, project=proj)
        rec["verify"]["speed_measurable"] = measurable
        rec["verify_s"] = round(time.perf_counter() - t0, 1)
        rec["status"] = "done"
    rec["outcome"] = classify(rec)
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    rec["host_load_end"] = list(os.getloadavg())
    if not a.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    (trial / "trial.json").write_text(json.dumps(rec, indent=2) + "\n")
    return rec


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _collect(run_dir: Path) -> List[dict]:
    return [json.loads(p.read_text()) for p in sorted((run_dir / "benchmarks").glob("**/trial.json"))]


def write_report(store: RunStore, run_id: str) -> Path:
    run_dir = store.run_dir(run_id)
    trials = _collect(run_dir)
    store.write_results(run_id, trials)
    _host = ((store.read_manifest(run_id) or {}).get("invocation") or {}).get("host")
    for t in trials:
        t.setdefault("host", _host)
    rows = ["| Benchmark | Arm | Model | Rep | Outcome | Best speedup | Pragmas (DP+LLM) | "
            "Rewrites | Baseline | LLM calls | Agent s |",
            "|---|---|---|---:|---|---:|---|---:|---:|---:|---:|"]
    for t in trials:
        par = t.get("verify", {}).get("par", {})
        best = max((p.get("speedup") or 0) for p in par.values()) if par else None
        rows.append(
            f"| {t['benchmark']} | {t['arm']} | {t['model']} | {t.get('repeat', 1)} | "
            f"{t['outcome']} | {f'{best:.2f}x' if best else '—'} | "
            f"{t.get('pragmas_discopop', '—')}+{t.get('pragmas_llm', '—')} | "
            f"{t.get('rewrites_kept', '—')} | {t.get('baseline_pragmas', '—')} | "
            f"{t.get('llm_calls', 0)} | {t.get('agent_s', '—')} |")
    trials_md = "\n".join(rows) + "\n"

    groups: Dict[Tuple[str, str], List[dict]] = {}
    for t in trials:
        groups.setdefault((t["arm"], t["model"]), []).append(t)
    outcomes = ["FASTER", "parallel-not-faster", "parallel-speed-not-measurable",
                "changed-not-parallel", "no-change",
                "BROKEN", "SCAFFOLD_MODIFIED", "VERIFY_FAILED", "AGENT_ERROR", "AGENT_TIMEOUT", "PROFILE_ERROR"]
    srows = ["| Arm | Model | Trials | " + " | ".join(outcomes) + " | Median agent s | LLM calls |",
             "|---|---|---:|" + "---:|" * len(outcomes) + "---:|---:|"]
    for (arm, model), ts in sorted(groups.items()):
        counts = [sum(1 for t in ts if t["outcome"] == o) for o in outcomes]
        med = statistics.median([t.get("agent_s", 0) for t in ts]) if ts else 0
        srows.append(f"| {arm} | {model} | {len(ts)} | " + " | ".join(map(str, counts))
                     + f" | {med:.0f} | {sum(t.get('llm_calls', 0) for t in ts)} |")
    summary_md = "\n".join(srows) + "\n"
    short = [t for t in trials if t.get("outcome") == "parallel-speed-not-measurable"]
    if short:
        # Listed, never aggregated: these ratios measure thread start-up, not the kernel.
        rows_short = ["", "### Kernels too short to time (T0.1) — ratios are not speedups", "",
                      "| Benchmark | Arm | Model | Rep | Verify size | Best ratio over threads |",
                      "|---|---|---|---:|---|---:|"]
        for t in short:
            v = t.get("verify") or {}
            ratios = [p.get("speedup") or 0 for p in (v.get("par") or {}).values()]
            ratio = f"{max(ratios):.2f}" if ratios else "—"
            rows_short.append(f"| {t['benchmark']} | {t['arm']} | {t['model']} | {t.get('repeat', 1)} | "
                              f"{v.get('verify_size', '—')} | {ratio} |")
        summary_md += "\n".join(rows_short) + "\n"

    # The main comparison (D19): every agent trial against DiscoPoP alone on its benchmark.
    import figures as _figures  # noqa: E402  (pure data here; matplotlib is only loaded for plots)
    pair_md = _figures.vs_discopop_alone_md(trials)
    has_agent_arm = any(t.get("arm") != _figures.BASELINE_ARM and t.get("kind") != "baseline" for t in trials)
    main_md = ""
    if pair_md:
        main_md = ("## Main comparison: DiscoPoP alone vs DiscoPoP + agent\n\n"
                   "The sequential original is the reference both are measured against, not the comparison.\n\n"
                   + pair_md + "\n")
    if has_agent_arm and not any(t.get("arm") == _figures.BASELINE_ARM for t in trials):
        main_md = ("## Main comparison: DiscoPoP alone vs DiscoPoP + agent\n\n"
                   "**MISSING — this run has no `discopop_gate` trials.** Run that arm on the same benchmarks "
                   "(no model, no cost) and rebuild with `plots --runs <this>,<that>`; speedups over the "
                   "sequential original alone do not show what the agent adds.\n\n")

    tables = store.tables_dir(run_id)
    tables.mkdir(parents=True, exist_ok=True)
    if pair_md:
        (tables / "vs_discopop_alone.md").write_text(pair_md)
    (tables / "trials.md").write_text(trials_md)
    (tables / "summary.md").write_text(summary_md)
    m = store.read_manifest(run_id) or {}
    inv = m.get("invocation", {})
    overview = run_dir / "overview.md"
    overview.write_text(
        f"# Agent experiment run `{run_id}`\n\n"
        f"- status: {m.get('status')} (created {m.get('created_at')}, finished {m.get('finished_at')})\n"
        f"- host: `{inv.get('host')}`, compilers `{inv.get('cc')}` / `{inv.get('cxx')}`\n"
        f"- agent: `{inv.get('agent_git', {}).get('head')}` "
        f"(uncommitted diff sha256 `{inv.get('agent_git', {}).get('dirty_sha256')}`)\n"
        f"- harness: `{inv.get('harness_git', {}).get('head')}` on `{inv.get('harness_git', {}).get('branch')}`\n"
        f"- verify size `{inv.get('verify_size')}`, threads {inv.get('threads')}, repeats {inv.get('repeats')}\n\n"
        f"Outcomes are judged by the harness, not by the agent: `BROKEN` means the final program's "
        f"values differ from the original's (relative error > {DIGEST_REL_TOL}) or move between "
        f"repeats at a fixed thread count; `SCAFFOLD_MODIFIED` means the rewrite edited the packaging's own code (the timer, the perturbed-input machinery or the digest), so the trial measures nothing and is never counted as a result; `FASTER` means correct and ≥ {FASTER_THRESHOLD}× at some "
        f"thread count.\n\n{main_md}## Summary\n\n{summary_md}\n## Trials\n\n{trials_md}")
    return overview


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_prepare(a: argparse.Namespace) -> int:
    cmd = [sys.executable, str(AGENT_DIR / "tools" / "prepare_polybench.py"),
           "--out", str(PREPARED / "polybench"), "--size", a.size, *a.kernels]
    if a.validate:
        cmd.append("--validate")
    return subprocess.call(cmd)


def cmd_list_benchmarks(_a: argparse.Namespace) -> int:
    benches = _prepared_benchmarks()
    if not benches:
        print("no prepared benchmarks — run `agent/benchmark prepare` first")
        return 1
    for b, d in benches.items():
        meta = json.loads((d / "meta.json").read_text())
        print(f"  {b:32} {meta.get('category', ''):28} {meta.get('language', 'cpp'):4} "
              f"agent size {meta.get('agent_dataset')}")
    return 0


def cmd_list_arms(_a: argparse.Namespace) -> int:
    print(f"  every arm: {' '.join(_common_flags()) or '(no common flags)'}")
    for arm, spec in _load_arms().items():
        print(f"  {arm:20} {'/'.join(spec.get('ids', [])):12} {' '.join(spec['flags']) or '(defaults)'}")
        print(f"  {'':20} {spec['description']}")
    return 0


def cmd_list_runs(_a: argparse.Namespace) -> int:
    store = RunStore(AGENT_DIR, "agent")
    for m in store.list_runs():
        inv = m.get("invocation", {})
        print(f"  {m['run_id']}  {m.get('status', '?'):9} {','.join(inv.get('benchmarks', []))}  "
              f"arms={','.join(inv.get('arms', []))}  models={','.join(inv.get('models', []))}")
    return 0


def cmd_run(a: argparse.Namespace) -> int:
    benches = _prepared_benchmarks()
    wanted = list(benches) if a.benchmarks == ["all"] else a.benchmarks
    unknown = [b for b in wanted if b not in benches]
    if unknown:
        sys.exit(f"unknown benchmark(s): {', '.join(unknown)} — see `list-benchmarks`")
    arms = _load_arms()
    bad = [x for x in a.arms if x not in arms]
    if bad:
        sys.exit(f"unknown arm(s): {', '.join(bad)} — see `list-arms`")
    # Every setting on which this run's arms disagree, printed before anything runs: an
    # experiment varies ONE thing, and the reader has to be able to see that the list holds
    # only that thing. Changing the campaign default on 2026-09-20 silently confounded four
    # planned experiments whose variant arms were paired against `full`; this makes that
    # class of mistake visible at launch instead of at analysis.
    # Every argument an arm declares must be what the agent actually parses. Checked against
    # the agent's own parser before anything runs, so nothing inherited or mistyped can
    # silently change what an experiment measures.
    problems = verify_arm_settings(list(a.arms), arms, Path(a.agent_repo).resolve(),
                                   list(wanted))
    if problems:
        print("arm settings do NOT match what the agent parses:")
        for pr in problems:
            print(f"    {pr}")
        sys.exit("refusing to run: fix arms.json `settings` or the arm's flags")
    print(f"arm settings verified against the agent's own parser ({len(a.arms)} arm(s))")

    inert = silent_interactions(list(a.arms), arms, wanted[0] if wanted else "")
    if inert:
        print("settings made INERT by another setting of the same arm:")
        for line in inert:
            print(f"    {line}")
        print("    ^ not an error, but it must be stated wherever this arm's result is reported.")

    differences = check_arm_compatibility(list(a.arms), arms)
    if differences:
        print("arms differ in:")
        for d in differences:
            print(f"    {d}")
        print("    ^ each line must be this experiment's variable; anything else is a confound.")
    elif len(a.arms) > 1:
        print("arms differ in: nothing — identical configuration (a repeatability check)")

    # Checked before the run is created: a kernel without a timing size would
    # otherwise stop the run halfway through.
    timing_sizes: Dict[str, str] = {}
    no_timing: List[str] = []
    if any(arms[x].get("timing_size", _common_timing_size()) == "per_kernel" for x in a.arms):
        for b in wanted:
            size = _timing_size(b)
            if size is None:
                no_timing.append(b)
            else:
                timing_sizes[b] = size
    if no_timing:
        print(f"speed check OFF for {len(no_timing)} benchmark(s) with no timing size (T0.1): "
              f"{', '.join(no_timing)}")
        print("    every size runs in milliseconds there, so the check could only reject noise.")
    verify_sizes = {b: _verify_size(a.verify_size, b)[0] for b in wanted}
    agent_repo = Path(a.agent_repo).resolve()
    if not (agent_repo / "venv" / "bin" / "python").exists():
        sys.exit(f"agent venv not found under {agent_repo}")
    cxx = _find_tool(a.cxx, "AGENT_CXX", _CXX_CANDIDATES, "clang++")
    cc = _find_tool(a.cc, "AGENT_CC", _CC_CANDIDATES, "clang")

    store = RunStore(AGENT_DIR, "agent")
    run_id = a.run_id or store.new_run_id()
    resuming = store.run_dir(run_id).exists()
    invocation = {
        "benchmarks": wanted, "arms": a.arms, "models": a.models, "repeats_per_trial": a.trials,
        "provider": a.provider, "edit_mode": a.edit_mode, "extra_agent_args": a.agent_arg,
        "verify_size": a.verify_size, "threads": a.threads, "repeats": a.repeats,
        "timeout_s": a.timeout, "check_seed": a.check_seed,
        "min_runtime_share": a.min_runtime_share, "cc": cc, "cxx": cxx, "host": socket.gethostname(),
        "platform": platform.platform(), "agent_git": _git_state(agent_repo),
        "harness_git": _git_state(HARNESS_ROOT), "argv": sys.argv,
        "tool_versions": _tool_versions(agent_repo),
        "common_flags": _common_flags(),
        "timing_sizes": timing_sizes, "speed_check_off": no_timing,
        "verify_sizes": verify_sizes,
        "arm_flags": {x: arms[x]["flags"] for x in a.arms},
    }
    if not resuming:
        store.create_run(run_id, invocation)
    run_dir = store.run_dir(run_id)
    total = len(wanted) * len(a.arms) * len(a.models) * a.trials
    print(f"agent harness run {run_id} — {total} trial(s) → {run_dir}", flush=True)
    print(f"  agent {invocation['agent_git']['head'][:10]}"
          f"{' (+uncommitted)' if invocation['agent_git']['dirty_sha256'] else ''}, cc {cc}, cxx {cxx}",
          flush=True)

    done = 0
    status = "finished"
    try:
        for bench in wanted:
            bench_dir = benches[bench]
            src_name = _source_name(bench_dir)
            profile_dir = run_dir / "profiles" / bench
            prof_json = profile_dir / "profile.json"
            # The package must be exactly what the packager wrote before anything is taken
            # from it; a modified package aborts the run rather than contaminating it.
            check_package(bench, bench_dir, when="run start")
            if prof_json.exists():
                prof = json.loads(prof_json.read_text())
            else:
                print(f"\n== {bench}: profiling {src_name} with DiscoPoP", flush=True)
                prof = profile_once(bench_dir, src_name, profile_dir, agent_repo, a.timeout)
                prof_json.write_text(json.dumps(prof, indent=2) + "\n")
            print(f"   profile: {prof}", flush=True)
            for arm in a.arms:
                for model in a.models:
                    for rep in range(1, a.trials + 1):
                        done += 1
                        trial = run_dir / "benchmarks" / bench / arm / model / f"rep{rep}"
                        label = f"[{done}/{total}] {bench} · {arm} · {model} · rep{rep}"
                        if (trial / "trial.json").exists():
                            print(f"\n{label}: already done, skipping", flush=True)
                            continue
                        print(f"\n{label}", flush=True)
                        if "error" in prof:
                            rec = {"benchmark": bench, "kernel": bench_dir.name, "arm": arm,
                                   "model": model, "status": "profile_error", "detail": prof["error"]}
                        else:
                            # Before: the package, the archived sources and the archived
                            # profile are intact, so this trial starts from the real program.
                            # After: they still are, so the NEXT trial does too.  A failure
                            # after the trial keeps the trial's record (it ran on an intact
                            # copy) and then stops the run.
                            integrity: Dict[str, Any] = {
                                "before": check_package(bench, bench_dir, profile_dir, "before trial")}
                            rec = run_trial(bench, bench_dir, profile_dir, trial, arm,
                                            [*_common_flags(), *arms[arm]["flags"],
                                             *_timing_flags(arms[arm], bench),
                                             *_evidence_file_flags(arms[arm], bench, run_dir, cc, cxx)],
                                            model, a, cc, cxx)
                            rec["profile"] = prof
                            rec["package_integrity"] = integrity
                            # What the agent's own speed check was given for THIS kernel: the
                            # harness switches it off where no size can be timed, and a gain on
                            # such a kernel was never speed-judged inside the agent. It was
                            # promised "per trial" and written to the manifest only until
                            # 2026-09-21, where no per-trial analysis could see it.
                            _tf = _timing_flags(arms[arm], bench)
                            rec["speed_check_off"] = ("--no-require-speedup" in _tf
                                                      or "--no-require-speedup" in arms[arm]["flags"])
                            rec["timing_flags"] = _tf
                            try:
                                integrity["after"] = check_package(bench, bench_dir, profile_dir,
                                                                   "after trial")
                            except PackageCorrupted as e:
                                integrity["after"] = {"ok": False, "error": str(e)}
                                _save_trial(trial, rec, rep)
                                raise
                        _save_trial(trial, rec, rep)
                        write_report(store, run_id)
    except KeyboardInterrupt:
        status = "interrupted"
        print("\ninterrupted — report covers the finished trials", flush=True)
    except PackageCorrupted as e:
        status = "aborted_package_corrupted"
        print(f"\nABORTED — {e}", flush=True)
        print("nothing further was run: a modified package or profile would contaminate every "
              "later trial", flush=True)
    store.finish_run(run_id, status, {"trials_done": len(_collect(run_dir)), "trials_planned": total})
    overview = write_report(store, run_id)
    print(f"\nreport: {overview}")
    _build_figures(_trials_for_runs(store, [run_id]), run_dir / "figures")
    return 2 if status == "aborted_package_corrupted" else 0


def _save_trial(trial: Path, rec: dict, rep: int) -> None:
    rec["repeat"] = rep
    rec["outcome"] = classify(rec)
    trial.mkdir(parents=True, exist_ok=True)
    (trial / "trial.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(f"    → {rec['outcome']}  (agent {rec.get('agent_s', '—')}s, "
          f"{rec.get('llm_calls', 0)} LLM calls)", flush=True)


def _run_root(store: RunStore, rid: str) -> Path:
    """The working copy in runs/ when it is here, the tracked archive otherwise — so every figure
    can be regenerated from a fresh clone."""
    if store.run_dir(rid).exists():
        return store.run_dir(rid)
    import campaign
    return campaign.find_run(rid) or store.run_dir(rid)


def _trials_for_runs(store: RunStore, run_ids: List[str]) -> List[dict]:
    trials = []
    for rid in run_ids:
        root = _run_root(store, rid)
        try:
            manifest = json.loads((root / "manifest.json").read_text())
        except (OSError, ValueError):
            manifest = {}
        host = (manifest.get("invocation") or {}).get("host")
        for t in _collect(root):
            t["run_id"] = rid
            t.setdefault("host", host)          # trials recorded before 2026-09-19 carry no host
            trials.append(t)
    return trials


def _build_figures(trials: List[dict], out: Path) -> None:
    """CSV + figures after every run. A plotting failure must never cost a finished run."""
    try:
        import figures
        written = figures.build(trials, out)
        print(f"figures + data: {out} ({len(written)} files)")
    except Exception as e:  # noqa: BLE001 — report and keep the run
        print(f"[warn] figures not generated ({type(e).__name__}: {e}); "
              f"re-run later with `agent/benchmark plots`")


def _resolve_runs(store: RunStore, spec: Optional[str]) -> List[str]:
    if not spec:
        latest = store.latest_run_id()
        return [latest] if latest else []
    ids = [s for s in spec.split(",") if s]
    missing = [i for i in ids if not _run_root(store, i).exists()]
    if missing:
        sys.exit(f"no such run(s) in runs/ or the archive: {', '.join(missing)}")
    return ids


def cmd_plots(a: argparse.Namespace) -> int:
    """Figures + CSV for one run (into the run) or several runs combined (into agent/analysis/<name>)."""
    store = RunStore(AGENT_DIR, "agent")
    ids = _resolve_runs(store, a.runs)
    if not ids:
        sys.exit("no runs")
    out = store.run_dir(ids[0]) / "figures" if len(ids) == 1 and not a.name \
        else AGENT_DIR / "analysis" / (a.name or "_".join(ids))
    trials = _trials_for_runs(store, ids)
    if a.suite:
        # the primary set of D30 (`tsvc`), drawn beside the registered set — never instead of it
        trials = [t for t in trials if str(t.get("benchmark", "")).startswith(a.suite + "/")]
    _build_figures(trials, out)
    return 0


RESULTS = AGENT_DIR / "results"          # tracked in git: the thesis's record of every run

# What an archived run keeps: everything a reader of the thesis could ask for — trial
# records, agent logs and LLM usage, diffs, the candidates the agent produced, the sources
# every trial started from, DiscoPoP's profile summary and logs, the tables, the CSVs and
# the figures. What it drops: the DiscoPoP profile trees (MBs each, regenerable, digested
# in profile.json), the trials' scratch copies, and binaries.
_ARCHIVE_SKIP_DIRS = {".discopop", "work", "__pycache__"}
_ARCHIVE_SKIP_FILES = {"a.out", ".DS_Store"}
_ARCHIVE_SKIP_SUFFIXES = {".o", ".so", ".dylib", ".pyc", ".exe"}


def _archive_keep(rel: Path) -> bool:
    if any(part in _ARCHIVE_SKIP_DIRS or part.endswith(".dSYM") for part in rel.parts):
        return False
    return rel.name not in _ARCHIVE_SKIP_FILES and rel.suffix not in _ARCHIVE_SKIP_SUFFIXES


def archive_run(run_dir: Path, dest: Path, max_file_mb: float = 25.0) -> dict:
    """Copy a run's results into `dest` (replaced), with a manifest that names every file
    and its sha256, so the archive can be checked against the run it came from."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    files: List[dict] = []
    skipped: List[dict] = []
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(run_dir)
        if not _archive_keep(rel):
            continue
        size = p.stat().st_size
        if size > max_file_mb * 1e6:
            skipped.append({"path": str(rel), "bytes": size, "why": f"larger than {max_file_mb} MB"})
            continue
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest / rel)
        files.append({"path": str(rel), "bytes": size,
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    # A trial run carries manifest.json; an instrument study (T0.x) carries a
    # summary.json / chosen.json with `study` and `host`.
    manifest: dict = {}
    study: dict = {}
    for name, target in (("manifest.json", "manifest"), ("summary.json", "study"),
                         ("chosen.json", "study")):
        if (run_dir / name).exists():
            try:
                loaded = json.loads((run_dir / name).read_text())
                if target == "manifest":
                    manifest = loaded
                elif not study:
                    study = loaded
            except json.JSONDecodeError:
                pass
    trials = _collect(run_dir) if (run_dir / "benchmarks").exists() else []
    mtimes = [p.stat().st_mtime for p in run_dir.rglob("*") if p.is_file()]
    stamp = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t))  # noqa: E731
    record = {
        "run_id": run_dir.name,
        "kind": "trials" if manifest else ("instrument" if study else "other"),
        "study": study.get("study"),
        "archived_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "archived_on": socket.gethostname(),
        "source": str(run_dir),
        "run_host": (manifest.get("invocation") or {}).get("host") or study.get("host"),
        "run_status": manifest.get("status") or ("files" if files else "empty"),
        "created": manifest.get("created_at") or study.get("started")
                   or (stamp(min(mtimes)) if mtimes else None),
        "finished": manifest.get("finished_at") or study.get("finished")
                    or (stamp(max(mtimes)) if mtimes else None),
        "trials": len(trials),
        "outcomes": dict(sorted(Counter(t.get("outcome", "?") for t in trials).items())),
        "agent_git": (manifest.get("invocation") or {}).get("agent_git"),
        "harness_git": (manifest.get("invocation") or {}).get("harness_git"),
        "files": files, "bytes": sum(f["bytes"] for f in files),
        "skipped": skipped,
        "excluded": "DiscoPoP profile trees (.discopop/, digested in profile.json), trial scratch "
                    "copies (work/), binaries",
    }
    (dest / "ARCHIVE.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def _archive_index() -> Path:
    """results/INDEX.md and EXHIBITS.md — by experiment, from the registry (tools/campaign.py)."""
    import campaign
    return campaign.write_indexes()[0]


def cmd_archive(a: argparse.Namespace) -> int:
    """Archive runs into the tracked results/ directory (then commit; RUNBOOK §archive)."""
    store = RunStore(AGENT_DIR, "agent")
    if a.all:
        ids = [d.name for d in sorted(store.runs_dir.iterdir())
               if d.is_dir() and not d.name.startswith("_")]
    else:
        ids = a.runs
    if not ids:
        sys.exit("nothing to archive: name run ids or pass --all")
    missing = [i for i in ids if not store.run_dir(i).exists()]
    if missing:
        sys.exit(f"no such run(s) under {store.runs_dir}: {', '.join(missing)}")
    RESULTS.mkdir(exist_ok=True)
    import campaign
    reg = campaign.load()
    for rid in ids:
        if not any(p.is_file() and _archive_keep(p.relative_to(store.run_dir(rid)))
                   for p in store.run_dir(rid).rglob("*")):
            print(f"skipped {rid}: nothing to archive")
            continue
        # Into its experiment's folder (results/campaign.json); an unregistered run lands in
        # results/_unregistered/ and `campaign.py check` fails until it is registered.
        dest = campaign.run_home(rid, reg)
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = archive_run(store.run_dir(rid), dest, a.max_file_mb)
        note = f", {len(r['skipped'])} file(s) over {a.max_file_mb} MB skipped" if r["skipped"] else ""
        print(f"archived {rid}: {len(r['files'])} files, {r['bytes'] / 1e6:.1f} MB, "
              f"{r['trials']} trial(s){note} → {dest.relative_to(AGENT_DIR)}/"
              + ("   ← NOT REGISTERED: add it to results/campaign.json" if rid not in reg.get("runs", {}) else ""))
    print(f"index: {_archive_index()}")
    return 0


def cmd_report(a: argparse.Namespace) -> int:
    store = RunStore(AGENT_DIR, "agent")
    run_id = store.resolve_run_id(a.run)
    if not run_id:
        sys.exit("no such run")
    print(write_report(store, run_id))
    return 0


def cmd_rescore(a: argparse.Namespace) -> int:
    """Re-apply the scaffolding check and the outcome rules to a finished run.

    Both read only files every trial already keeps (`original.*`, `final.*`, the recorded
    verification), so a run made before a rule existed can be judged by it without being
    re-run. Each changed outcome is printed and the old one kept in the record."""
    store = RunStore(AGENT_DIR, "agent")
    run_id = store.resolve_run_id(a.run)
    if not run_id:
        sys.exit("no such run")
    changed = 0
    for p in sorted((store.run_dir(run_id) / "benchmarks").glob("**/trial.json")):
        t = json.loads(p.read_text())
        if t.get("kind") == "baseline":
            continue
        if (p.parent / "original").is_dir() and (p.parent / "final").is_dir():
            # a project trial keeps whole trees
            orig_text = _project_text(p.parent / "original")
            final_text = _project_text(p.parent / "final")
            t["pragmas_added"] = _pragmas_added(orig_text, final_text)
            t["pragmas_in_final"] = t["pragmas_added"]
        else:
            orig = next(p.parent.glob("original.*"), None)
            final = next(p.parent.glob("final.*"), None)
            if orig is None or final is None:
                print(f"  {p.parent}: no original/final source kept — skipped")
                continue
            orig_text, final_text = orig.read_text(), final.read_text()
        t["scaffold"] = scaffold.check(orig_text, final_text)
        # The facts read from the agent's log, re-read with the current parser: a counter
        # fixed after a run (phase_b_deferred, 23 Sep) must reach that run's records too.
        log_file = p.parent / "agent.log"
        if log_file.exists():
            facts = _parse_agent_log(log_file.read_text(errors="replace"))
            # only facts the trial already records: a run older than a field keeps its shape
            old = {k: t[k] for k, v in facts.items() if k in t and t[k] != v}
            if old:
                print(f"  {t.get('benchmark')} · {t.get('arm')} · rep{t.get('repeat')}: log facts "
                      + ", ".join(f"{k} {old[k]} -> {facts[k]}" for k in sorted(old)))
                t.setdefault("log_facts_history", []).append(
                    {"old": old, "replaced_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "reason": "rescore"})
                t.update(facts)
        new = classify(t)
        if new != t.get("outcome"):
            changed += 1
            t.setdefault("outcome_history", []).append(
                {"outcome": t.get("outcome"), "replaced_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "reason": "rescore"})
            print(f"  {t.get('benchmark')} · {t.get('arm')} · rep{t.get('repeat')}: "
                  f"{t.get('outcome')} -> {new}  {t['scaffold']['problems'][:1]}")
            t["outcome"] = new
        p.write_text(json.dumps(t, indent=2) + "\n")
    print(f"{run_id}: {changed} outcome(s) changed")
    write_report(store, run_id)
    return 0


def cmd_verify_source(a: argparse.Namespace) -> int:
    """Judge a given source — or the original under different compiler flags — as a trial is judged.

    The baselines a reviewer asks for are not agent runs: an expert's OpenMP version, another
    system's released output, or Polly on the untouched source. They still have to face the
    harness's own verification, at the same size, on the same machine, or the comparison is
    not one. The record lands in the same run store as trials, so `report` and `plots` include
    it without caring where the source came from; `kind: baseline` marks its origin.
    """
    benches = _prepared_benchmarks()
    if a.benchmark not in benches:
        sys.exit(f"unknown benchmark: {a.benchmark} — see `list-benchmarks`")
    bench_dir = benches[a.benchmark]
    src_name = _source_name(bench_dir)
    ext = Path(src_name).suffix
    original = bench_dir / src_name
    candidate = Path(a.source).resolve() if a.source else original
    if not candidate.exists():
        sys.exit(f"no such source: {candidate}")
    if candidate.is_dir():
        # Only a project benchmark takes a directory, and it must hold the benchmark's own file.
        if _project_of(bench_dir) is None:
            sys.exit(f"{candidate} is a directory, but {a.benchmark} is a single-file benchmark")
        if not (candidate / src_name).is_file():
            sys.exit(f"{candidate} holds no {src_name} — not a version of {a.benchmark}")
    elif candidate.suffix != ext:
        sys.exit(f"{candidate.name} is a {candidate.suffix} file, the benchmark is {ext}")
    flags = a.final_flags.split()
    if candidate == original and not flags:
        sys.exit("that is the benchmark's own source with no extra flags — nothing to compare")

    cxx = _find_tool(a.cxx, "AGENT_CXX", _CXX_CANDIDATES, "clang++")
    cc = _find_tool(a.cc, "AGENT_CC", _CC_CANDIDATES, "clang")
    # The FULL name (suite/benchmark), never `bench_dir.name`: bare names collide
    # (`lu` is both polybench/lu and npb/lu) and `md` is not a key at all, so this
    # refused to verify any application source.
    vsize, measurable = _verify_size(a.verify_size, a.benchmark)

    store = RunStore(AGENT_DIR, "agent")
    run_id = a.run_id or store.new_run_id()
    if not store.run_dir(run_id).exists():
        store.create_run(run_id, {
            "kind": "baselines", "benchmarks": [a.benchmark], "verify_size": a.verify_size,
            "threads": a.threads, "repeats": a.repeats, "check_seed": a.check_seed,
            "cc": cc, "cxx": cxx, "host": socket.gethostname(), "platform": platform.platform(),
            "harness_git": _git_state(HARNESS_ROOT), "argv": sys.argv,
        })
    trial = store.run_dir(run_id) / "benchmarks" / a.benchmark / a.label / "none" / "rep1"
    trial.mkdir(parents=True, exist_ok=True)
    proj = _project_of(bench_dir)
    if proj is None:
        shutil.copy2(original, trial / f"original{ext}")
        shutil.copy2(candidate, trial / f"final{ext}")
        text, orig_text = candidate.read_text(), original.read_text()
    else:
        # A project: the whole tree is the original; a given --source replaces the unit
        # that holds main (an expert version of the benchmark file), a compiler baseline
        # replaces nothing.
        for d in ("original", "final"):
            shutil.rmtree(trial / d, ignore_errors=True)
            _copy_tree(bench_dir, trial / d)
        if candidate.is_dir():
            # An expert version that is several files (LLNL's LULESH needs its own header and
            # init unit beside lulesh.cc): every file of the given directory replaces its
            # namesake; the rest of the package stays.
            for f in sorted(candidate.rglob("*")):
                if f.is_file():
                    (trial / "final" / f.relative_to(candidate)).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, trial / "final" / f.relative_to(candidate))
        elif candidate != original:
            shutil.copy2(candidate, trial / "final" / src_name)
        text, orig_text = _project_text(trial / "final"), _project_text(trial / "original")

    rec: dict = {
        "benchmark": a.benchmark, "kernel": bench_dir.name, "source": src_name,
        "arm": a.label, "model": "none", "repeat": 1, "kind": "baseline",
        "candidate": str(candidate),
        "candidate_sha256": (_tree_digest(candidate) if candidate.is_dir()
                             else hashlib.sha256(candidate.read_bytes()).hexdigest()),
        "source_changed": text != orig_text,
        "pragmas_in_final": (text.count("#pragma omp") if proj is None
                             else _pragmas_added(orig_text, text)),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "host": socket.gethostname(),
        "host_load_start": list(os.getloadavg()),
    }
    shown = f"{candidate.name}" + (f" + {' '.join(flags)}" if flags else "")
    print(f"verify {a.benchmark} · {a.label}: {shown} at {vsize}", flush=True)
    t0 = time.perf_counter()
    rec["verify"] = verify(trial, ext, cc, cxx, vsize, a.threads, a.repeats,
                           a.check_seed or None, final_flags=flags or None, project=proj)
    rec["verify"]["speed_measurable"] = measurable
    rec["verify_s"] = round(time.perf_counter() - t0, 1)
    rec["status"] = "done"
    rec["outcome"] = classify(rec)
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    rec["host_load_end"] = list(os.getloadavg())
    (trial / "trial.json").write_text(json.dumps(rec, indent=2) + "\n")
    par = rec["verify"].get("par") or {}
    best = max((p.get("speedup") or 0) for p in par.values()) if par else 0
    print(f"  {rec['outcome']}" + (f", best {best:.2f}× over {len(a.threads)} thread count(s)"
                                   if best else "")
          + (f"  [{rec['verify'].get('status')}]" if rec["verify"].get("status") != "ok" else ""))
    print(write_report(store, run_id))
    return 0


def main() -> None:
    p = argparse.ArgumentParser(prog="agent/benchmark", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("prepare", help="generate single-file benchmarks into agent/prepared/")
    sp.add_argument("kernels", nargs="*")
    sp.add_argument("--size", default="SMALL")
    sp.add_argument("--validate", action="store_true")
    sp.set_defaults(func=cmd_prepare)

    sub.add_parser("list-benchmarks", aliases=["lb"]).set_defaults(func=cmd_list_benchmarks)
    sub.add_parser("list-arms", aliases=["la"]).set_defaults(func=cmd_list_arms)
    sub.add_parser("list-runs", aliases=["lr"]).set_defaults(func=cmd_list_runs)

    sp = sub.add_parser("run", help="run trials")
    sp.add_argument("benchmarks", nargs="+", help="e.g. polybench/2mm, or `all`")
    sp.add_argument("--arms", type=lambda s: s.split(","), default=["full"])
    sp.add_argument("--models", type=lambda s: s.split(","), default=["haiku"])
    sp.add_argument("--trials", type=int, default=1, help="repeats of each (benchmark, arm, model)")
    sp.add_argument("--provider", default="claude-agent-sdk")
    sp.add_argument("--edit-mode", default="direct")
    sp.add_argument("--agent-arg", action="append", default=[],
                    help="extra flag passed to the agent verbatim (repeatable)")
    sp.add_argument("--agent-repo", default=os.environ.get("AGENT_REPO", str(DEFAULT_AGENT_REPO)))
    sp.add_argument("--cc", default=None)
    sp.add_argument("--cxx", default=None)
    sp.add_argument("--verify-size", default="per_kernel",
                    help="PolyBench dataset for verification, or per_kernel (default): each "
                         "kernel's size from agent/config/kernel_sizes.json (T0.1)")
    sp.add_argument("--threads", type=lambda s: [int(x) for x in s.split(",")],
                    default=[min(8, os.cpu_count() or 1)])
    sp.add_argument("--repeats", type=int, default=3, help="timed repeats per build in verify")
    sp.add_argument("--timeout", type=int, default=5400, help="seconds per phase")
    sp.add_argument("--run-id", default=None, help="name the run; reuse one to resume it")
    sp.add_argument("--keep-work", action="store_true", help="keep each trial's .discopop copy")
    sp.add_argument("--min-runtime-share", type=float, default=0.0,
                    help="passed to every arm alike: skip regions below this share of measured "
                         "runtime (pre-register the value; default 0 = off)")
    sp.add_argument("--check-seed", default="7",
                    help="perturbed-input seed given to the agent (--check-input) and to "
                         "verification; empty string disables (default: 7)")
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("verify-source", aliases=["vs"],
                        help="verify a given source (or the original under other compiler "
                             "flags) as a baseline, without running the agent")
    sp.add_argument("benchmark", help="e.g. polybench/2mm — supplies the original to judge against")
    sp.add_argument("--label", required=True,
                    help="what this baseline is, e.g. polly, expert_openmp, repoomp_aaai; "
                         "appears where an arm's name appears in reports and figures")
    sp.add_argument("--source", default=None,
                    help="the source to judge (default: the benchmark's own, for compiler baselines)")
    sp.add_argument("--final-flags", default="",
                    help="extra compile flags for the candidate build only, split on whitespace, "
                         "e.g. \"-mllvm -polly -mllvm -polly-parallel -mllvm -polly-process-unprofitable\". "
                         "A SINGLE flag must be written with '=' (--final-flags=-funroll-loops): "
                         "argparse reads a lone dashed word as an option, while a quoted string "
                         "containing spaces is taken as a value")
    sp.add_argument("--cc", default=None)
    sp.add_argument("--cxx", default=None)
    sp.add_argument("--verify-size", default="per_kernel")
    sp.add_argument("--threads", type=lambda s: [int(x) for x in s.split(",")],
                    default=[min(8, os.cpu_count() or 1)])
    sp.add_argument("--repeats", type=int, default=3)
    sp.add_argument("--check-seed", default="7")
    sp.add_argument("--run-id", default=None, help="reuse a run id to collect baselines together")
    sp.set_defaults(func=cmd_verify_source)

    sp = sub.add_parser("plots", help="trials.csv, gate_failures.csv and thesis figures")
    sp.add_argument("--runs", default=None, help="run id, or comma-separated ids to combine (default: latest)")
    sp.add_argument("--name", default=None, help="output folder under agent/analysis/ when combining")
    sp.add_argument("--suite", default=None, help="only benchmarks of this suite (e.g. tsvc)")
    sp.set_defaults(func=cmd_plots)

    sp = sub.add_parser("rescore", help="re-apply the scaffolding check and outcome rules to a finished run")
    sp.add_argument("run", help="run id")
    sp.set_defaults(func=cmd_rescore)

    sp = sub.add_parser("report", help="rebuild overview.md and tables for a run")
    sp.add_argument("--run", default=None)
    sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("archive",
                        help="copy runs' results (no profile trees, scratch copies or binaries) "
                             "into the tracked agent/results/ and rebuild its index")
    sp.add_argument("runs", nargs="*", help="run ids (default with --all: every run)")
    sp.add_argument("--all", action="store_true")
    sp.add_argument("--max-file-mb", type=float, default=25.0,
                    help="skip (and list) files larger than this (default 25)")
    sp.set_defaults(func=cmd_archive)

    a = p.parse_args()
    sys.exit(a.func(a))


if __name__ == "__main__":
    main()
