"""
Agentic Controller — ties L1 → L2 → L3 → L4 together.

Targets any hotspot code region (loop, function body, CU), not just loops.

Main loop (per thesis flowchart, slide 9):

DiscoPoP's own pragma gets only a REDUCED gate — compile and output, never
races or timing — and a failure there just means the pragma is not inserted.
A region with an applicable pattern therefore never reaches the LLM either
way; the full gate exists to prove that code the LLM restructured is valid.

  For each candidate (priority order):
    ┌─ Tier-1: DiscoPoP pattern found & applicable?
    │    Yes → reduced gate: compiles, race-free, output unchanged?
    │              PASS → apply the pragma → ACCEPT (no LLM, no re-profile)
    │              FAIL → leave the pragma out → SKIP (still no LLM)
    │    No  → Tier-2 allowed at this depth?
    │              No  → SKIP
    │              Yes → Tier-2:
    │                      assemble evidence (L2)
    │                      call LLM (L3) → valid diff?
    │                        No  → format re-prompt (free), then retry
    │                        Yes → quality gate (L4) → pass?
    │                                Yes → apply patch, re-profile, discover new
    │                                No  → diagnostic → retry (decrement budget)
    └─ continue to next candidate

Discovery depth (--restructure-depth N):
  Every candidate carries a discovery_depth.  Initial candidates are depth=0.
  After each accepted Tier-2 patch the source is re-profiled; newly exposed
  candidates (IDs not yet seen) are enqueued at depth=current+1.

  Tier-2 (LLM restructuring) is only applied to candidates at depth ≤ N.
  Candidates at depth > N are processed with Tier-1 only — if no pattern is
  found they are skipped without any LLM call.

  With --restructure-depth 0 (default):
    depth=0 (initial)  → Tier-1 or Tier-2
    depth=1 (discovered after first restructuring) → Tier-1 only → terminates

  With --restructure-depth 1:
    depth=0 → Tier-1 or Tier-2 → re-profile → depth=1 → Tier-1 or Tier-2
    depth=2 → Tier-1 only → terminates

  Termination is guaranteed: at depth N+1 the source is never modified again,
  so no further re-profiling occurs and the queue drains.

Why Tier-1 validation matters:
  DiscoPoP's Do-All detector never sees cross-iteration deps for scalar
  variables (instruction-ID / source-line-ID mismatch in the dep graph).
  A loop like `a[i] = a[i] + a[i-1]` gets flagged as Do-All even though
  it has a genuine loop-carried RAW dependency.  Running TSan with -fopenmp
  on the generated patch exposes the data race before we commit the change.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from . import fast_refresh, viz
from .args import AgentArguments
from .l1_planner import build_candidates, region_fingerprint
from .l2_evidence import _brace_match_end, assemble, load_prevented_deps
from .l3_llm import (LLMConnectionError, call_llm, fmt_blockers, make_diff,
                      normalize_code, review_dependences)
from .l4_validator import (capture_reference, check_pragma_compiles,
                           find_archer, fix_hunk_headers, measure_marginal,
                           noise_floor, run_patch, time_source, validate)
from .types import ValidationResult

_LLVM_LIBCXX = "/usr/local/Cellar/llvm@19/19.1.7/lib/c++"
_REGION_LABEL = {"loop": "loop", "function": "function", "cu": "block"}


def _cxx_wrapper() -> str:
    return str(Path(sys.executable).parent / "discopop_cxx")


def _explorer_cmd() -> str:
    return str(Path(sys.executable).parent / "discopop_explorer")


_OUTLINED_RE = re.compile(r"\.omp_outlined[A-Za-z0-9_.]*")

# Constructs that remove the barrier this reasoning depends on.  `nowait` drops
# the implicit barrier at the end of a worksharing region outright; a task can
# outlive the region that spawned it.  Either makes two distinct outlined
# regions genuinely concurrent, so Variant 3 must not fire.
_NO_BARRIER_RE = re.compile(r"\bnowait\b|#\s*pragma\s+omp\s+(?:task|taskloop)\b")


# TSan opens the first access with "Write of size 4 at 0x... by thread T1:" and
# the second with "Previous write of size 4 ... by main thread:" — capitalised
# only on the first.  Matching on "Read"/"Write" therefore saw ONE of the two
# accesses, which silently weakened every rule phrased as "all racing accesses".
_ACCESS_RE = re.compile(
    r"^\s*(?:Previous\s+)?(?:atomic\s+)?(?:read|write)\s+of size\s+\d+.*"
    r"\bby (?:main thread|thread T\d+):\s*$",
    re.IGNORECASE,
)


def _access_blocks(lines: List[str]) -> List[List[str]]:
    """The stack frames of each racing access in a TSan report, in order.

    An access line opens the block and the next blank line closes it; everything
    between is that access's stack.
    """
    blocks: List[List[str]] = []
    for idx, line in enumerate(lines):
        if _ACCESS_RE.search(line):
            frames = []
            for j in range(idx + 1, len(lines)):
                if not lines[j].strip():
                    break
                frames.append(lines[j])
            blocks.append(frames)
    return blocks


def _is_omp_barrier_false_positive(diagnostic: str, code: str = "") -> bool:
    """Detect macOS TSan false positive: OMP worker accesses memory, main thread
    accesses it sequentially after the parallel-for barrier exits.

    Real race:   both accesses are .omp_outlined  (two workers conflict)
    False positive: one access is .omp_outlined (worker), the other is the
    main thread running sequential code after the barrier — TSan on macOS
    does not model the implicit barrier at the end of #pragma omp parallel for.

    Covers three location variants:
      - "Location is heap block allocated by main thread"  (vector data on heap)
      - "Location is stack of main thread"                 (vector object / local var)
      - "Location is global '<name>'"                      (static / file-scope array)
    The location clause only establishes the main-thread-vs-worker shape; the
    reasoning is about WHERE THE ACCESSES RUN, so it holds for any storage
    class.  Omitting globals made the agent escalate correctly-parallel loops
    over `static` arrays to the LLM — caught by the benchmark's Do-All baseline.
    In both cases the main thread's access must be sequential (no .omp_outlined
    in its call stack), confirming it runs outside any parallel region.
    """
    lines = diagnostic.splitlines()
    access_blocks = _access_blocks(lines)

    # Variant 1: OpenMP REDUCTION gather.  libomp combines per-thread partials
    # inside its barrier (`.omp.reduction.reduction_func` called from
    # `__kmp_*barrier_gather`), under runtime-internal synchronization TSan
    # cannot see because libomp is not TSan-instrumented.  Conservative rule:
    # EVERY racing access must sit inside those runtime frames — an access in
    # plain user code (a genuine missing-reduction race) disqualifies.
    if access_blocks and all(
        any(".omp.reduction.reduction_func" in f or
            ("__kmp_" in f and "barrier" in f) for f in frames)
        for frames in access_blocks
    ):
        return True

    # Variant 3: two DIFFERENT parallel regions.  Every racing access sits
    # inside an outlined region, but not the SAME one — so a barrier separates
    # them and they cannot overlap.  Verified on this host: a program whose
    # second `parallel for` reads what the first one wrote (indices reversed, so
    # a different thread reads each element) is reported as a race, while being
    # bit-deterministic over 20 runs at 1/2/4/8/16 threads.  The distinction is
    # exact rather than statistical:
    #   same outlined function on both sides  -> one region, genuinely concurrent
    #   different outlined functions          -> a barrier between them
    # (Homebrew's libomp carries no TSan annotations — there is no libarcher —
    # so TSan sees none of OpenMP's synchronization.)  `code` is the source this
    # patch produces; when it uses `nowait` or tasks the barrier is not there to
    # reason about and this variant is skipped.
    if not (code and _NO_BARRIER_RE.search(code)):
        outlined: List[str] = []
        for frames in access_blocks:
            hit = next((_OUTLINED_RE.search(f) for f in frames
                        if ".omp_outlined" in f), None)
            if hit is None:
                outlined = []
                break
            outlined.append(hit.group(0))
        if len(outlined) >= 2 and len(set(outlined)) >= 2:
            return True

    # Variant 2: OMP worker vs. the main thread running sequential code after
    # the parallel-for barrier — TSan on macOS does not model that implicit
    # barrier.
    is_heap = (
        "Location is heap block" in diagnostic
        and "allocated by main thread" in diagnostic
    )
    is_stack = "Location is stack of main thread" in diagnostic
    is_global = "Location is global" in diagnostic
    if not (is_heap or is_stack or is_global):
        return False
    if ".omp_outlined" not in diagnostic:
        return False
    for idx, line in enumerate(lines):
        # Match only ACCESS lines ("Write ... by main thread:" / "Read ... by main thread:"),
        # not allocation lines ("allocated by main thread:") which appear in heap-location
        # blocks and do not indicate that the main thread is one of the racing accessors.
        if "by main thread:" in line and ("Write" in line or "Read" in line):
            # Collect only the stack frames that belong to THIS access block.
            # TSan separates access blocks with a blank line; stop there so we
            # don't accidentally include the next access's .omp_outlined frames.
            main_frames = []
            for j in range(idx + 1, len(lines)):
                if not lines[j].strip():
                    break
                main_frames.append(lines[j])
            if not any(".omp_outlined" in f for f in main_frames):
                return True
    return False


def _venv_env() -> "dict[str, str]":
    """Environment with our venv's bin dir prepended to PATH.

    The agent is typically launched as `venv/bin/python -m discopop_agent`
    WITHOUT activating the venv, so `venv/bin` is not on PATH.  The explorer we
    spawn shells out to a BARE `discopop_patch_generator` (resolved via PATH);
    without this, PATH may resolve it to a stale/global DiscoPoP install
    (e.g. ~/.local/bin) that doesn't understand newer pattern types
    (`ValueError: Unknown task type: PARALLELREGION`) and exits 1, aborting the
    re-profile.  Prepending our venv's bin guarantees the matching tool wins.
    """
    import os

    env = dict(os.environ)
    venv_bin = str(Path(sys.executable).parent)
    env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    return env


# Artifacts the instrumented RUN produces.  A fast refresh re-runs only the
# compile, which does not write these, so they are preserved across it and
# translated onto the new numbering instead.
_RUN_ARTIFACTS = (
    "dynamic_dependencies.txt",
    "loop_counter_output.txt",
    "reduction.txt",
    "memory_regions.txt",
)


def _reprofil_fast(
    source_file: str, discopop_dir: Path, old_text: str, new_text: str,
    output_dir: Path,
) -> "tuple[bool, str]":
    """Refresh the profile WITHOUT running the instrumented program.

    The instrumented run is the step that scales with the workload — 17x native
    on a 104M-operation kernel here, and worse the more memory traffic there is.
    Everything else DiscoPoP needs is static: re-running `discopop_cxx` alone
    regenerates `Data.xml`, `static_dependencies.txt` and the instruction
    mapping for the new code in about a second.

    So the compile runs, and the PREVIOUS run's observed dependences are
    translated onto the new instruction numbering (fast_refresh.py) rather than
    re-measured.  A dependence that cannot be translated with certainty is
    dropped, never guessed: the rewritten region ends up covered by static
    dependences alone, which are over-approximate and can only make the agent
    more cautious.

    Returns (ok, human-readable note).  On any doubt it returns False so the
    caller can fall back to a full re-profile — a wrong dependence is far worse
    than a slow one.
    """
    src = Path(source_file).resolve()
    binary = src.parent / "a.out"
    profiler = (discopop_dir / "profiler").resolve()
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    lmap = fast_refresh.line_map(old_text, new_text)
    problems = fast_refresh.verify_translation(old_text, new_text, lmap)
    if problems:
        return False, f"line map failed its own check ({problems[0][:80]})"

    # The compile overwrites the instruction mapping, so the old one — the half
    # of the translation that describes where the dependences came from — has to
    # be taken out of the way first.
    saved: "dict[str, str]" = {}
    for name in _RUN_ARTIFACTS + ("instructionID_to_lineID_mapping.txt",):
        f = profiler / name
        if f.exists():
            saved[name] = f.read_text()
    if "dynamic_dependencies.txt" not in saved or "instructionID_to_lineID_mapping.txt" not in saved:
        return False, "no previous profile to carry forward"

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent, env=env,
    )
    if r.returncode != 0:
        return False, f"instrumentation failed: {r.stderr[-200:]}"

    old_map = output_dir / ".fast_refresh_old_mapping.txt"
    old_map.write_text(saved["instructionID_to_lineID_mapping.txt"])
    new_map = profiler / "instructionID_to_lineID_mapping.txt"

    dep_text, stats = fast_refresh.remap_dependencies(
        saved["dynamic_dependencies.txt"], old_map, new_map, lmap
    )
    (profiler / "dynamic_dependencies.txt").write_text(dep_text)
    if "loop_counter_output.txt" in saved:
        (profiler / "loop_counter_output.txt").write_text(
            fast_refresh.remap_loop_counters(saved["loop_counter_output.txt"], lmap)
        )
    if "reduction.txt" in saved:
        (profiler / "reduction.txt").write_text(
            fast_refresh.remap_reduction(saved["reduction.txt"], lmap)
        )
    # Memory-region ids are runtime identities the carried dependences still
    # refer to by name, so this file travels unchanged.
    if "memory_regions.txt" in saved:
        (profiler / "memory_regions.txt").write_text(saved["memory_regions.txt"])
    old_map.unlink(missing_ok=True)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(), env=env,
    )
    if r.returncode != 0:
        return False, f"explorer failed on the refreshed profile: {r.stderr[-200:]}"

    return True, stats.summary()


def _llm_dep_review(
    args: AgentArguments, dp_dir: Path, old_text: str, new_text: str,
    output_dir: Path, file_id: int,
) -> str:
    """--llm-deps: let the model discharge static dependences that block a Do-All.

    Why this exists.  A fast refresh leaves rewritten code covered by STATIC
    dependences only, and static analysis reports a dependence whenever it
    cannot prove there is none.  A freshly written loop is therefore usually
    blocked by something that does not actually happen, with no dynamic data to
    settle it — and since a rewrite CREATES regions, and depth > 0 exists to
    parallelize them, static caution alone would keep them sequential forever.

    Two rules keep the question narrow, and both matter:

      * only DiscoPoP's own Do-All BLOCKERS are reviewed, not every dependence
        in the region.  On example4 the unfiltered version asked about 76
        dependences of which 37 were induction variables and 3 were body-locals
        — things the agent already knows are never blockers.  Asking a model 40
        questions whose answers are already known is how it learns to answer
        carelessly.
      * only STATIC-origin blockers are reviewable.  A dependence DiscoPoP
        actually observed at run time is ground truth and is never up for
        discussion.

    Every judgement is recorded in llm_deps.json.  This is the one place a
    model's claim enters DiscoPoP's analysis, so be plain about the exposure: a
    wrong SPURIOUS produces a racy loop, and what stands behind it is the gate.
    """
    profiler = (dp_dir / "profiler").resolve()
    static_file = profiler / "static_dependencies.txt"
    if not static_file.exists():
        return ""

    lmap = fast_refresh.line_map(old_text, new_text)
    carried_over = set(lmap.values())
    new_lines = new_text.splitlines()
    rewritten = [n for n in range(1, len(new_lines) + 1) if n not in carried_over]
    if not rewritten:
        return "nothing was rewritten — no dependences to review"

    blockers = load_prevented_deps(dp_dir, file_id, min(rewritten), max(rewritten))
    # A dependence that was actually observed is not a candidate for discharge,
    # whatever a model thinks of it.
    blockers = [b for b in blockers
                if "STATIC" in str(b.get("origin", "")).upper()]
    if not blockers:
        return "no static Do-All blockers in the rewritten lines"

    def _ln(v: object) -> "int | None":
        try:
            return int(str(v).split(":")[-1])
        except (TypeError, ValueError):
            return None

    items: List[Dict[str, Any]] = []
    for b in blockers:
        snk, src = _ln(b.get("sink_line")), _ln(b.get("source_line"))
        ls, le = b.get("loop_start"), b.get("loop_end")
        items.append({
            "dep_type": str(b.get("dep_type", "?")).split(".")[-1],
            "var": str(b.get("var_name", "?")),
            "sink_line": snk,
            "source_line": src,
            "sink_text": new_lines[snk - 1] if snk and snk <= len(new_lines) else "",
            "source_text": new_lines[src - 1] if src and src <= len(new_lines) else "",
            "loop": f"{ls}-{le}" if ls is not None else "",
            "loop_carried": snk is not None and src is not None and src >= snk,
        })

    lo = max(min(rewritten) - 3, 1)
    hi = min(max(rewritten) + 3, len(new_lines))
    excerpt = "\n".join(f"{n:4d}  {new_lines[n - 1]}" for n in range(lo, hi + 1))

    try:
        verdicts = review_dependences(
            items, excerpt, args.model, api_key=args.api_key,
            provider=args.provider, api_base=args.api_base, verbose=args.verbose,
        )
    except Exception as e:                      # a review failure must not fail the run
        return f"dependence review unavailable ({str(e)[:60]}) — keeping every blocker"

    # Silence means REAL: an unanswered blocker keeps blocking.
    discharged = [items[i - 1] for i, (real, _r) in verdicts.items() if not real]
    record = [
        {**items[i - 1], "verdict": "REAL" if real else "SPURIOUS", "reason": reason}
        for i, (real, reason) in sorted(verdicts.items())
    ]
    log = output_dir / "llm_deps.json"
    existing = json.loads(log.read_text()) if log.exists() else []
    existing.append({"source": args.source_file, "reviewed": record})
    log.write_text(json.dumps(existing, indent=2))

    if not discharged:
        return f"reviewed {len(items)} static blocker(s) — none discharged"

    # Translate the discharged blockers back into the static dependence lines
    # that produced them, matched on (type, variable, both endpoints).
    fwd, _rev = fast_refresh.load_instruction_keys(
        profiler / "instructionID_to_lineID_mapping.txt"
    )

    def _line_of(token: str) -> "int | None":
        key = fwd.get(token.split("@")[0])
        return key[1] if key else None

    targets = {(d["dep_type"], d["var"], d["sink_line"], d["source_line"])
               for d in discharged}
    raw_lines = static_file.read_text().splitlines()
    keep: List[str] = []
    removed = 0
    for raw in raw_lines:
        f = raw.split()
        if len(f) >= 4 and f[1] == "NOM" and "|" in f[3]:
            src_tok, _, var_part = f[3].partition("|")
            key = (f[2], var_part.split("(")[0], _line_of(f[0]),
                   _line_of(src_tok) if src_tok not in ("*", "0@0") else None)
            if key in targets:
                removed += 1
                continue
        keep.append(raw)

    if not removed:
        return (f"reviewed {len(items)} static blocker(s), {len(discharged)} judged "
                f"spurious, but none matched a dependence line — nothing changed")

    static_file.write_text("\n".join(keep) + "\n")
    r = subprocess.run([_explorer_cmd()], capture_output=True, text=True,
                       cwd=dp_dir.resolve(), env=_venv_env())
    if r.returncode != 0:
        static_file.write_text("\n".join(raw_lines) + "\n")
        return (f"discharged {len(discharged)} blocker(s) but the explorer then "
                f"failed — restored the original analysis")
    return (f"reviewed {len(items)} static blocker(s), discharged {len(discharged)} "
            f"({removed} dependence line(s) removed, recorded in {log.name})")


def _reprofil(source_file: str, discopop_dir: Path, binary_args: list | None = None) -> bool:
    """Re-instrument, run, and re-explore after a Tier-2 patch is accepted."""
    src = Path(source_file).resolve()   # absolute path avoids CWD confusion
    binary = src.parent / "a.out"
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent, env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] instrumentation failed:\n{r.stderr[-500:]}")
        return False

    run_cmd = [str(binary)] + (binary_args or [])
    subprocess.run(run_cmd, capture_output=True, text=True, cwd=src.parent, env=env)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(), env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] explorer failed:\n{r.stderr[-500:]}")
        return False

    return True


def _function_edit_to_diff(
    source_file: str, start_line: int, end_line: int, new_code: str
) -> str | None:
    """--edit-mode function: splice the LLM's rewritten function into the file
    over [start_line, end_line] and return a unified diff of the change.

    The diff is generated from the actual on-disk content, so it always applies
    cleanly — eliminating the diff-apply failure class.  Returns None if the span
    is invalid or the edit is a no-op (ignoring comments and whitespace)."""
    old_text = Path(source_file).read_text()
    old_lines = old_text.splitlines(keepends=True)
    if start_line < 1 or end_line > len(old_lines) or start_line > end_line:
        return None
    new_block = [ln + "\n" for ln in new_code.splitlines()]
    new_lines = old_lines[: start_line - 1] + new_block + old_lines[end_line:]
    old_span = "".join(old_lines[start_line - 1: end_line])
    if normalize_code(new_code) == normalize_code(old_span):
        return None
    return make_diff(old_text, "".join(new_lines), source_file)


def _apply_to_source(diff: str, source_file: str, output_dir: Path, label: str) -> bool:
    """Write a validated patch into the real source file, backing the original
    up first.  Returns True if the file now carries the change.

    Tier-2 rewrites were always written back, but a validated Tier-1 pragma used
    to be recorded and then left on disk in patch_generator/ — so a run that
    proved a 5x parallelization ended with the user's source untouched and
    nothing to show for it.  The agent's output is a parallelized program, so
    accepted patches of either tier land in the file.
    """
    src = Path(source_file).resolve()
    backup = output_dir / f"{src.name}.original"
    if not backup.exists():
        shutil.copy2(src, backup)
        print(f"│  [{label}] Original backed up → {backup.name}")
    patch_path = output_dir / f".apply_{label.lower()}.patch"
    patch_path.write_text(fix_hunk_headers(diff) + "\n")
    ok, diag = run_patch(src, patch_path)
    patch_path.unlink(missing_ok=True)
    if not ok:
        print(f"│  [{label}] WARNING: could not apply the validated patch to "
              f"{src.name}: {diag[:160]}")
        return False
    print(f"│  [{label}] Applied to {src.name}")
    return True


_PRAGMA_SHARED_RE = re.compile(r"\bshared\s*\(([^)]*)\)")
_HUNK_OLD_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _declared_in(lines: List[str], name: str) -> bool:
    """Is `name` DECLARED anywhere in these lines (not merely used)?"""
    decl = re.compile(
        r"(?:^|[;{}(,]|\s)"                       # statement boundary
        r"(?:const\s+|static\s+|volatile\s+|unsigned\s+|signed\s+)*"
        r"(?:auto|bool|char|short|int|long|float|double|size_t|"
        r"[A-Za-z_]\w*(?:::\w+)*)"                # a type name
        r"[\s*&]+"
        r"(?:[\w\s,*&]*?\b)?"                     # other names in the same decl
        + re.escape(name) + r"\b\s*(?=[=;,\[)])"
    )
    return any(decl.search(ln) for ln in lines)


def _repair_pragma_clauses(diff: "str | None", source_file: str) -> "str | None":
    """Drop names from a generated pragma's `shared()` clause when they are not
    in scope at the pragma.

    DiscoPoP sometimes lists a loop-BODY local in `shared()`.  Observed on
    example4: for a loop whose body opens `int tmp = arr[i];` it emitted
    `shared(tmp,arr)`, and the -fopenmp build then fails outright with
    "use of undeclared identifier 'tmp'".  The gate correctly rejects that
    pattern, but the only recovery was Tier-2 — an LLM call, gated by
    --restructure-depth — for what is a one-token defect in a generated clause.
    Deleting the name is not restructuring, so it happens here instead: at any
    depth, for free, before the gate.

    Only `shared()` is touched, and that makes the repair semantically free:
    a variable from an enclosing scope is shared by DEFAULT in a `parallel for`,
    so removing it from the clause cannot change the meaning — it is either
    redundant or (the bug case) not in scope at all.  `private`, `firstprivate`,
    `lastprivate` and `reduction` are left alone, since removing a name there
    WOULD change semantics.  A pragma carrying `default(none)` is skipped
    entirely, because there the clause is load-bearing.

    Returns the diff unchanged (same object) when there is nothing to fix, so
    the gate cache key is unaffected.
    """
    if not diff or "#pragma omp" not in diff:
        return diff

    try:
        src_lines = Path(source_file).read_text().splitlines()
    except OSError:
        return diff

    out: List[str] = []
    old_line = 0           # 1-based line in the ORIGINAL file
    changed = False

    for line in diff.splitlines():
        m = _HUNK_OLD_RE.match(line)
        if m:
            old_line = int(m.group(1))
            out.append(line)
            continue

        if line.startswith("+") and "#pragma omp" in line and "default(none)" not in line:
            # The pragma is inserted BEFORE original line `old_line`, which is
            # the loop it applies to.  Its body is that loop's brace span.
            body: List[str] = []
            if 0 < old_line <= len(src_lines):
                end = _brace_match_end(source_file, old_line)
                if end >= old_line:
                    body = src_lines[old_line - 1:end]
            if body:
                def _strip(mm: "re.Match") -> str:
                    names = [n.strip() for n in mm.group(1).split(",") if n.strip()]
                    kept = [n for n in names if not _declared_in(body, n)]
                    if len(kept) == len(names):
                        return str(mm.group(0))
                    dropped = [n for n in names if n not in kept]
                    print(f"│  [Tier-1] Repairing the generated pragma: "
                          f"{', '.join(dropped)} "
                          f"{'is' if len(dropped) == 1 else 'are'} declared inside "
                          f"the loop body, so cannot appear in shared()")
                    return f"shared({','.join(kept)})" if kept else ""

                fixed = str(_PRAGMA_SHARED_RE.sub(_strip, line))
                if fixed != line:
                    changed = True
                    line = fixed.rstrip() + " "
            out.append(line)
            continue

        if not line.startswith("+"):
            # context and removed lines both advance the original-file position
            if not line.startswith("---") and not line.startswith("\\"):
                old_line += 1
        out.append(line)

    return "\n".join(out) + ("\n" if diff.endswith("\n") else "") if changed else diff


_PRIVATE_CLAUSE_RE = re.compile(r"\b(private|firstprivate)\s*\(([^)]*)\)")
_LOOP_HEAD_RE = re.compile(r"^\s*(for|while)\s*\(")


def _loop_span(lines: List[str], head_idx: int) -> "tuple[int, int] | None":
    """Line range of the loop whose header is at `head_idx`, by brace balance.

    Returns (first, last) 0-based inclusive.  A brace-less single-statement body
    ends at the first line that closes the header's parentheses and then carries
    a `;`, which covers the common `for (...)\n    stmt;` shape.
    """
    depth = 0
    seen_brace = False
    for i in range(head_idx, min(len(lines), head_idx + 400)):
        ln = lines[i]
        for ch in ln:
            if ch == "{":
                depth += 1
                seen_brace = True
            elif ch == "}":
                depth -= 1
                if seen_brace and depth <= 0:
                    return head_idx, i
        if not seen_brace and i > head_idx and ln.rstrip().endswith(";"):
            return head_idx, i
        if not seen_brace and i == head_idx and ln.rstrip().endswith(";") and ")" in ln:
            return head_idx, i
    return None


def _read_after(lines: List[str], name: str, after_idx: int, limit: int = 60) -> bool:
    """Is `name` READ somewhere after line `after_idx`, before it is redeclared?

    Deliberately crude and deliberately conservative in the direction that
    matters: any mention that is not a plain assignment to the name counts as a
    read.  A false "yes" costs one rejected pragma; a false "no" ships a silently
    wrong program.
    """
    word = re.compile(r"\b" + re.escape(name) + r"\b")
    assign_only = re.compile(r"^\s*" + re.escape(name) + r"\s*=[^=]")
    for ln in lines[after_idx + 1: after_idx + 1 + limit]:
        if not word.search(ln):
            continue
        if _declared_in([ln], name):     # shadowed / redeclared — stop looking
            return False
        if assign_only.match(ln):
            continue
        return True
    return False


def _declared_as_array(lines: List[str], name: str) -> bool:
    """Is `name` declared with ARRAY storage, as opposed to a pointer to it?

    The distinction decides whether writing `name[i]` counts as writing `name`
    for the clause rules.  `private` on an array gives each thread its own
    copy, so the element writes are thrown away; `private` on a POINTER copies
    the pointer, and the writes still land in the one shared buffer.  Treating
    the two alike would reject correct pointer pragmas.
    """
    sub = re.compile(r"\b" + re.escape(name) + r"\s*\[")
    return any(_declared_in([ln], name) and sub.search(ln) for ln in lines)


def _written_in(lines: List[str], name: str, subscript: bool = False) -> bool:
    """Is `name` ASSIGNED anywhere in these lines?

    The write-back rule only bites when the loop actually produces a value.  A
    read-only scalar in `firstprivate` — a loop bound, a size, a function
    parameter — is correct and idiomatic OpenMP, and rejecting it was throwing
    away five of six good pragmas.

    `subscript` also counts `name[expr] = ...`, which is what an array-valued
    clause turns into.  Off by default because it is only sound once the name
    is known to BE an array — see _declared_as_array.
    """
    pat = re.compile(
        r"\b" + re.escape(name) + r"\s*(?:"
        r"(?<![=!<>+\-*/%&|^])=(?!=)"      # x = ...   (not ==, !=, <=, +=, ...)
        r"|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>="
        r"|\+\+|--"                        # x++ / x--
        r")"
    )
    pre = re.compile(r"(?:\+\+|--)\s*\b" + re.escape(name) + r"\b")   # ++x / --x
    elem = re.compile(
        r"\b" + re.escape(name) + r"\s*\[[^\]]*\]\s*"
        r"(?:(?<![=!<>+\-*/%&|^])=(?!=)|\+=|-=|\*=|/=|%=|&=|\|=|\^=)"
    ) if subscript else None
    return any(pat.search(ln) or pre.search(ln)
               or (elem is not None and elem.search(ln)) for ln in lines)


def _pragma_and_anchor(diff: str) -> "tuple[str, str] | None":
    """From a generated patch, the pragma line it adds and the loop header that
    follows it.  Together those are everything needed to place the pragma
    against ANY version of the file — which is what makes replaying a stored
    diff unnecessary."""
    dl = diff.splitlines()
    pi = next((i for i, l in enumerate(dl)
               if l.startswith("+") and "#pragma omp" in l), None)
    if pi is None:
        return None
    pragma = dl[pi][1:]
    for l in dl[pi + 1:]:
        if l.startswith("-"):
            continue
        text = l[1:] if l[:1] in ("+", " ") else l
        st = text.strip()
        if not st or st.startswith("//") or st.startswith("/*") or st.startswith("*"):
            continue                      # a comment may sit between the two
        if _LOOP_HEAD_RE.match(text):
            return pragma, text
        break
    return None


def _locate_header(src: List[str], header: str, near: int) -> "int | None":
    """Index of `header` in `src`, nearest to `near`.  Identical sibling loops
    are common, so proximity to the patch's own hunk breaks the tie."""
    cands = [i for i, l in enumerate(src) if l.strip() == header.strip()]
    if not cands:
        return None
    return min(cands, key=lambda i: abs(i - near))


def derive_pragma_patch(stored_diff: "str | None", source_file: str) -> "str | None":
    """Rebuild a generated pragma's patch against the CURRENT file.

    DiscoPoP's patches are produced once, against the source as it was profiled.
    Phase B then applies them one after another, and every applied pragma shifts
    every line below it — so the second stored patch already describes a file
    that no longer exists, and `patch` refuses it.  Before `--forward` that hung
    the run; after it, the pragma is silently skipped, which works directly
    against the goal of ending up with MORE pragmas.

    Replaying the stored diff is the mistake.  A pragma is really just two
    facts: the text to insert, and the loop it belongs to.  Locate that loop in
    the file as it stands now and emit a fresh diff, and it applies by
    construction no matter how much has moved above it.
    """
    if not stored_diff:
        return None
    pa = _pragma_and_anchor(stored_diff)
    if pa is None:
        return stored_diff              # not a shape we understand — leave it alone
    pragma, header = pa
    try:
        old_text = Path(source_file).read_text()
    except OSError:
        return stored_diff
    src = old_text.splitlines()
    span = _touched_span(stored_diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return None                     # the loop is gone; the pragma is meaningless
    if head > 0 and src[head - 1].strip() == pragma.strip():
        return None                     # already carries exactly this pragma
    new = src[:head] + [pragma] + src[head:]
    return make_diff(old_text, "\n".join(new) + "\n", source_file)


def check_pragma_clauses(diff: "str | None", source_file: str) -> "str | None":
    """Reject a generated pragma whose data-sharing clauses cannot be right.

    Returns None when the pragma is acceptable, or a one-line reason when it is
    not.  Static: nothing is compiled or executed.

    This exists because the runtime gate structurally cannot see the worst case.
    On example4, DiscoPoP emitted `private(ok)` for

        int ok = 1;
        for (...) if (arr[i] > arr[i+1]) ok = 0;
        printf(... ok ? "YES" : "NO");

    `private` gives each thread its own uninitialised copy and discards it at
    the end of the region, so the writes never reach the `ok` that printf reads.
    The program then prints "sorted: YES" even with the sort deleted — verified.
    It compiles, races nowhere (each thread owns its copy), and prints
    byte-identical output whenever the array really is sorted, so compile, TSan
    and correctness all pass it.  Only this check sees it.

    Two rules, both about a name that must not be in the clause at all:
      - read after the loop  -> its value has to survive; `private` severs that
        and `firstprivate` copies in without copying out.
      - declared inside the body -> not in scope at the pragma; the -fopenmp
        build fails with "use of undeclared identifier" (the `private(tmp)`
        case, which at least fails loudly).
    """
    if not diff or "#pragma omp" not in diff:
        return None
    try:
        src = Path(source_file).read_text().splitlines()
    except OSError:
        return None

    # The pragma and the loop it governs, as they will look once applied.
    added = [l[1:] for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    pragma = next((l for l in added if "#pragma omp" in l), None)
    if pragma is None:
        return None
    # The loop this pragma governs is the next loop header AFTER IT IN THE DIFF.
    # Line arithmetic from the hunk start does not work: it picks up whichever
    # loop happens to sit nearby, which on example4 meant checking the array-init
    # loop instead of the one the pragma was attached to.
    pa = _pragma_and_anchor(diff)
    if pa is None:
        return None
    _pragma_text, header = pa
    span = _touched_span(diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return None
    return _clause_problem(src, pragma, head)


def _clause_problem(src: List[str], pragma: str, head: int) -> "str | None":
    """The two rules above, applied to ONE pragma governing the loop at `head`.

    Split out from check_pragma_clauses because the rules do not care who wrote
    the pragma — DiscoPoP's generated clauses and the LLM's own are wrong in
    exactly the same two ways, and `private(ok)` is invisible to compile, TSan
    and output whichever of them produced it.
    """
    names: List[str] = []
    for kind, body in _PRIVATE_CLAUSE_RE.findall(pragma):
        for n in body.split(","):
            n = n.strip()
            if n:
                names.append(n)
    if not names:
        return None

    loop = _loop_span(src, head)
    if loop is None:
        return None
    body = src[loop[0]: loop[1] + 1]

    for n in names:
        if _declared_in(body[1:], n):
            return (f"clause names `{n}`, which is declared inside the loop body — "
                    f"it is already per-iteration and is not in scope at the pragma")
        # The write-back rule needs BOTH halves: the loop has to produce a value
        # AND something after the loop has to read it.  A read-only scalar in
        # firstprivate (a bound, a size, a parameter) is perfectly correct.
        is_array = _declared_as_array(src, n)
        if (_written_in(body[1:], n, subscript=is_array)
                and _read_after(src, n, loop[1])):
            what = "fills and later code reads" if is_array else "writes and later code reads"
            return (f"clause names `{n}`, which the loop {what} — "
                    f"private/firstprivate discard those writes, so that "
                    f"read would see a stale value")
    return None


_PRAGMA_LINE_RE = re.compile(r"^\s*#\s*pragma\s+omp\b")


def _next_loop_header(src: List[str], after: int, limit: int = 6) -> "int | None":
    """Index of the loop header a pragma at `after` applies to, or None.

    Only blank lines, comments and continued pragma lines may sit between the
    two; anything else means the pragma is not annotating a loop (a `parallel`
    block, a `task`, a `barrier`) and the clause rules do not apply to it.
    """
    for i in range(after + 1, min(len(src), after + 1 + limit)):
        st = src[i].strip()
        if not st or st.startswith("//") or st.startswith("/*") or st.startswith("*"):
            continue
        if src[i - 1].rstrip().endswith("\\") or _PRAGMA_LINE_RE.match(src[i]):
            continue
        return i if _LOOP_HEAD_RE.match(src[i]) else None
    return None


def check_llm_pragmas(diff: "str | None", source_file: str) -> "str | None":
    """The clause rules, run over every pragma the LLM's OWN edit introduces.

    check_pragma_clauses above reads a generated patch: one pragma, inserted
    before a loop that already exists in the file.  An LLM rewrite is neither —
    it may carry several pragmas, and the loops they govern are new code that
    the current file does not contain yet.  So the check runs against the
    PATCHED text instead, over the lines the diff actually wrote.

    Returns None when every pragma is acceptable, or a one-line reason naming
    the offending pragma.  This is the one gate stage that can see a clause
    which compiles, races nowhere, and still silently drops the loop's results
    — see check_pragma_clauses for the `private(ok)` case that motivated it.
    """
    if not diff or "#pragma omp" not in diff:
        return None
    patched = _apply_in_memory(diff, source_file)
    if patched is None:
        return None            # it does not even apply; that is stage 1's answer
    src = patched.splitlines()
    span = _touched_span(diff)
    lo, hi = ((span[0] - 1, span[1] - 1) if span else (0, len(src) - 1))
    for i in range(max(lo, 0), min(hi, len(src) - 1) + 1):
        if not _PRAGMA_LINE_RE.match(src[i]):
            continue
        head = _next_loop_header(src, i)
        if head is None:
            continue
        problem = _clause_problem(src, src[i], head)
        if problem:
            return f"`{src[i].strip()}` — {problem}"
    return None


def _read_tier1_patch(patch_dir: Path) -> str | None:
    """Return the content of the first .patch file DiscoPoP generated for a
    pattern, or None if the patch_generator directory is missing / empty."""
    if not patch_dir.exists():
        return None
    for f in sorted(patch_dir.glob("*.patch")):
        return f.read_text()
    return None


def _snapshot_profile(dp_dir: Path, output_dir: Path) -> Path:
    """Copy the current DiscoPoP profile (.discopop) to a snapshot under the
    agent's output dir (kept inside the project, not the OS temp dir), excluding
    the output dir itself when it lives inside .discopop.  Restoring this snapshot
    is far cheaper than re-running instrument+run+explore to rebuild the same
    pre-patch state on a revert."""
    snap_root = output_dir / ".profile_snapshots"
    snap_root.mkdir(parents=True, exist_ok=True)
    snap = Path(tempfile.mkdtemp(prefix="snap_", dir=snap_root))
    ignore = None
    if output_dir.resolve().parent == dp_dir.resolve():
        # output_dir (and thus the snapshot under it) lives inside .discopop —
        # exclude it so we never copy the snapshot into itself.
        ignore = shutil.ignore_patterns(output_dir.name)
    shutil.copytree(dp_dir, snap, dirs_exist_ok=True, ignore=ignore)
    return snap


def _restore_profile(snap: Path, dp_dir: Path, output_dir: Path) -> None:
    """Restore the profile from a snapshot taken by _snapshot_profile, preserving
    the agent's output dir (accepted.json, patches, backups) when it lives inside
    .discopop.  Replaces re-profiling on a revert."""
    keep = output_dir.name if output_dir.resolve().parent == dp_dir.resolve() else None
    for item in dp_dir.iterdir():
        if item.name == keep:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in snap.iterdir():
        dst = dp_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def _write_record(output_dir: Path, record: dict, dry_run: bool = False) -> None:
    """Append one accepted region to accepted.json.

    A dry run still evaluates Tier-1 patches for real (it only skips the LLM),
    so its verdicts belong in the printed summary — but --dry-run promises no
    file changes, so nothing is written."""
    if dry_run:
        return
    f = output_dir / "accepted.json"
    records: List[dict] = json.loads(f.read_text()) if f.exists() else []
    records.append(record)
    f.write_text(json.dumps(records, indent=2))


def _print_candidates(candidates: list) -> None:
    """Print candidate table. candidates is a list of (depth, HotspotCandidate)."""
    print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Depth':>5}  {'Workload':>12}  Name")
    print("-" * 76)
    for depth, c in candidates:
        r = c.region
        name = r.name or f"lines {r.start_line}–{r.end_line}"
        print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {depth:>5}  {c.workload_estimate:>12,.0f}  {name}")
    print()


def _print_banner(args: AgentArguments) -> None:
    print(f"\n{'='*60}")
    print("  DiscoPoP Agentic Controller")
    print(f"{'='*60}")
    print(f"  Source         : {args.source_file}")
    print(f"  DiscoPoP dir   : {args.discopop_dir}")
    print(f"  Model          : {args.model}")
    print(f"  Budget         : {args.budget} LLM retries/region "
          f"(+{args.build_retries} free build fixes)")
    print(f"  λ penalty      : {args.lambda_penalty}")
    print(f"  Min workload   : {args.min_workload}")
    print(f"  Restruct. depth: {args.restructure_depth} "
          f"(Tier-2 allowed at depth 0–{args.restructure_depth})")
    print(f"  Quality gate   : Tier-1 = all but speed, no escalation; "
          f"Tier-2 = full")
    _archer = find_archer()
    print(f"  TSan           : "
          + (f"barrier-aware (archer: {_archer})" if _archer else
             "no libarcher — TSan cannot see OpenMP barriers and will report "
             "any two parallel regions as racing; falling back to the "
             "barrier heuristic. Build one: discopop_agent/tools/build_archer.sh"))
    print(f"  Speedup gate   : "
          + (f"require ≥ {args.min_measured_speedup}× measured"
             if args.require_speedup else "OFF (--no-require-speedup)"))
    print(f"  Dry run        : {args.dry_run}")
    if args.provider == "openai-compat":
        llm_mode = f"{args.model} @ {args.api_base} (openai-compat)"
    else:
        llm_mode = args.model
    print(f"  LLM mode       : {llm_mode}")
    print(f"  Edit mode      : {args.edit_mode}")
    print(f"  Re-profiling   : "
          + ("fast refresh (compile only) between rewrites; full before a deeper "
             "level and before Phase B" if args.fast_refresh
             else "full (instrument + run + explore) after every kept rewrite")
          + ("; LLM judges static deps in new code" if args.llm_deps else ""))
    print(f"  Pragmas        : "
          + ("LLM writes them with the rewrite, gate decides (--llm-pragmas)"
             if args.llm_pragmas else "DiscoPoP writes them in Phase B"))
    print(f"{'='*60}\n")


_HUNK_NEW_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _touched_span(diff: str) -> "tuple[int, int] | None":
    """Line range the patch rewrote, in NEW-file coordinates, from its @@ headers.

    Used to ask the post-restructuring question precisely: did DiscoPoP find a
    pattern *in the code the model actually changed*?  A pattern somewhere else
    in the file proves nothing about this rewrite.  Returns None when no hunk
    header parses (then the caller falls back to file scope).
    """
    lo = hi = None
    for line in diff.splitlines():
        m = _HUNK_NEW_RE.match(line)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        end = start + max(count, 1) - 1
        lo = start if lo is None else min(lo, start)
        hi = end if hi is None else max(hi, end)
    return (lo, hi) if lo is not None and hi is not None else None


def _added_pragmas(diff: str) -> List[str]:
    """The `#pragma omp` lines a diff introduces, in order.

    Under --llm-pragmas this is what turns a restructuring into a
    parallelization: the gate's TSan, correctness and timing stages all key on
    the diff carrying a pragma, and an empty list here means the LLM produced a
    sequential rewrite that still needs DiscoPoP's verdict.
    """
    return [l[1:].strip() for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++") and "#pragma omp" in l]


def _gate_key(diff: str, source_file: str, mode: str) -> str:
    """Identity of one gate run: this patch, against this exact source text,
    asking this set of questions.

    The source hash is what makes reuse safe — a patch validated before another
    region's pragma was applied says nothing about the file afterwards, and that
    case really happens (a rewrite exposes two loops; applying the first one's
    pragma changes the file the second is measured against).

    `mode` is in the key because the modes are not interchangeable: "safety"
    skips the timing runs, so serving one of its results to a "full" caller
    would silently report an unmeasured patch as fast enough.
    """
    h = hashlib.sha1()
    h.update(Path(source_file).read_bytes())
    h.update(b"\0")
    h.update(diff.encode())
    h.update(b"\0")
    h.update(mode.encode())
    return h.hexdigest()


def _validate_cached(
    cache: dict,
    diff: str,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    reference_outputs: "list | None" = None,
    mode: str = "full",
) -> "tuple[ValidationResult, bool, bool]":
    """Run the gate on `diff`, or return the answer already computed for it.

    Returns (result, served_from_cache, barrier_false_positive_suspected).

    Both gate sites come through here: Tier-1 in mode="safety", the post-rewrite
    verification in mode="full".  Two reasons it is worth the indirection.

    The cache: one verification measures every pattern a rewrite exposed, and a
    later region can present an identical patch against identical source bytes —
    a full duplicate gate run (three compiles, a sanitizer run, a correctness
    run, and up to five timing pairs) for a verdict already known.

    The macOS OMP-barrier false-positive re-check: TSan reports a race between a
    write inside `.omp_outlined` and the main thread's read after the region,
    with no barrier edge it can see.  Legitimate pragmas trip it, so a `tsan`
    failure carrying that signature is re-verified with the race check off
    rather than being trusted.  Any caller that skips this wrapper rejects
    correct pragmas on macOS.
    """
    key = _gate_key(diff, args.source_file, mode)
    hit = cache.get(key)
    if hit is not None:
        return hit, True, False

    def _run(skip: bool) -> ValidationResult:
        return validate(
            diff, args.source_file,
            reference_output=reference_output,
            reference_outputs=reference_outputs,
            binary_args=binary_args,
            require_speedup=args.require_speedup,
            min_speedup=args.min_measured_speedup,
            skip_race_check=skip,
            reference_time=reference_time,
            mode=mode,
        )

    res = _run(False)
    barrier_fp = (
        not res.passed and res.stage == "tsan"
        and _is_omp_barrier_false_positive(res.diagnostic)
    )
    if barrier_fp:
        # Suspected macOS barrier artefact: re-verify against the correctness
        # and performance gates rather than accepting on the heuristic alone.
        res = _run(True)
    cache[key] = res
    return res, False, barrier_fp


@dataclass
class RewriteOutcome:
    """Did the restructuring achieve what it exists to achieve?

    status:
      "ok"             — DiscoPoP found a pattern in the rewritten code and its
                         pragma passed the gate (and was fast enough, if required)
      "exposed"        — a pattern was found; validating it is deferred to the
                         next depth, which is allowed to restructure it further
      "self_annotated" — --llm-pragmas: the rewrite carries its own pragmas and
                         has already passed the full gate, so DiscoPoP's opinion
                         of it is not what decides
      "no_pattern"     — DiscoPoP re-profiled the rewrite and still found nothing
      "pattern_broken" — a pattern was found but its pragma fails the gate
      "no_speedup"     — the pragma is correct but not faster
    """
    status: str
    speedup: "float | None" = None
    pattern_label: str = ""
    diagnostic: str = ""
    # Content fingerprints of the regions this rewrite exposed.  A rewrite is
    # justified at the end only if Phase B applied a pragma to one of them —
    # matched on identity, not on line numbers, which drift as later changes
    # land above them.
    exposed_prints: List[str] = field(default_factory=list)


def _verify_rewrite(
    fresh: list,
    touched: "tuple[int, int] | None",
    dp_dir: Path,
    args: AgentArguments,
    reference_output: "str | None",
    binary_args: "list | None",
    reference_time: "float | None",
    validate_patterns: bool,
    gate_cache: dict,
    reference_outputs: "list | None" = None,
) -> RewriteOutcome:
    """Decide whether an accepted-by-the-gate rewrite actually did its job.

    A rewrite exists for exactly one reason: to let DiscoPoP parallelize code it
    previously could not.  Compiling and preserving output is necessary but says
    nothing about that — so after re-profiling we check what DiscoPoP now
    reports for the rewritten lines, and (when this is the last chance to act on
    it) run its generated pragma through the full gate.

    Patterns are tried largest-workload-first and the FIRST qualifying one wins:
    the decision is "did anything pay off", so validating the rest only burns
    time on a question already answered.
    """
    exposed = [
        c for c in fresh
        if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")
        and (touched is None
             or not (c.region.end_line < touched[0] or c.region.start_line > touched[1]))
    ]
    if not exposed:
        return RewriteOutcome("no_pattern")

    exposed.sort(key=lambda c: c.workload_estimate, reverse=True)
    label = ", ".join(
        f"{c.pattern_type or 'pattern'} @ lines {c.region.start_line}–{c.region.end_line}"
        for c in exposed[:3]
    )
    prints = [
        region_fingerprint(args.source_file, c.region.start_line,
                           c.region.end_line, c.region.name)
        for c in exposed
    ]
    if not validate_patterns:
        # "A pattern appeared" is a weaker claim than "a pragma works", and
        # DiscoPoP makes the first one for loops clang rejects outright — a
        # runtime bound, a surviving `break`.  Keeping such a rewrite spends an
        # LLM call and a re-profile on something that can never pay off, so
        # check the cheap half now: the clauses, and one -fopenmp build.
        for c in exposed:
            cpid = c.pattern.get("pattern_id", "?") if c.pattern else "?"
            patch = derive_pragma_patch(
                _read_tier1_patch(dp_dir / "patch_generator" / str(cpid)),
                args.source_file,
            )
            if not patch or check_pragma_clauses(patch, args.source_file):
                continue
            ok_c, _diag = check_pragma_compiles(patch, args.source_file)
            if ok_c:
                return RewriteOutcome("exposed", pattern_label=label,
                                      exposed_prints=prints)
        return RewriteOutcome(
            "no_usable_pragma", pattern_label=label, exposed_prints=prints,
            diagnostic="DiscoPoP reports a pattern for the rewritten lines, but "
                       "every pragma it generates for them is rejected before it "
                       "can run — the clauses are wrong, or the loop is not in a "
                       "form OpenMP accepts.",
        )


    worst = RewriteOutcome("pattern_broken", pattern_label=label)
    for cand in exposed:
        pid = cand.pattern.get("pattern_id", "?") if cand.pattern else "?"
        patch = _read_tier1_patch(dp_dir / "patch_generator" / str(pid))
        if not patch:
            continue
        res, _cached, _fp = _validate_cached(
            gate_cache, patch, args, reference_output, binary_args, reference_time,
            reference_outputs=reference_outputs,
        )
        if res.passed:
            return RewriteOutcome("ok", res.measured_speedup, label)
        # "no speedup" is closer to success than "still racing": prefer to
        # report it, so the retry prompt talks about granularity, not correctness.
        if res.stage == "performance":
            worst = RewriteOutcome("no_speedup", res.measured_speedup, label, res.diagnostic)
        elif worst.status != "no_speedup":
            worst = RewriteOutcome("pattern_broken", None, label, res.diagnostic)
    return worst


_OUTCOME_LABEL = {
    "no_pattern": "DiscoPoP still finds no parallelism in the rewritten lines",
    "pattern_broken": "DiscoPoP found a pattern, but its pragma fails validation",
    "no_speedup": "DiscoPoP parallelized it, but it is not faster",
    "reprofile_failed": "the rewrite broke DiscoPoP's profiling run",
    "no_usable_pragma": "DiscoPoP sees a pattern, but no pragma it generates for it can run",
}


# Fallback only.  The real threshold is measured per run by noise_floor() — an
# unchanged program does not measure 1.000, and how far off it lands depends on
# the host and the program, not on a number chosen here.  This value is used
# only when that calibration cannot run.
_MARGINAL_NOISE = 0.97


def _apply_in_memory(diff: str, source_file: str) -> "str | None":
    """What `source_file` would contain with `diff` applied — without touching
    the real file.  Stages a candidate pragma so it can be timed before the
    decision to keep it is made."""
    with tempfile.TemporaryDirectory(prefix="dp_agent_stage_") as tmp:
        work = Path(tmp)
        dst = work / Path(source_file).name
        shutil.copy2(source_file, dst)
        pf = work / "stage.patch"
        pf.write_text(fix_hunk_headers(diff) + "\n")
        ok, _diag = run_patch(dst, pf)
        return dst.read_text() if ok else None


def _apply_change_log(original_text: str, keep: list, args: AgentArguments) -> list:
    """Write `original_text` to the source, then re-apply `keep` in order.

    Returns the subset that actually applied.  Nothing is ever un-applied, so a
    change that stood on one that has been dropped simply fails here — which is
    the signal that it has to go too.
    """
    src = Path(args.source_file)
    src.write_text(original_text)
    landed: list = []
    with tempfile.TemporaryDirectory(prefix="dp_agent_apply_") as tmp:
        work = Path(tmp)
        for ch in keep:
            pf = work / "rb.patch"
            pf.write_text(fix_hunk_headers(ch["diff"]) + "\n")
            ok, _diag = run_patch(src, pf)
            if ok:
                landed.append(ch)
    return landed


def _check_final_source(
    args: AgentArguments, original_text: str, reference_output: "str | None",
    reference_outputs: "list | None", binary_args: "list | None",
    reference_time: "float | None",
) -> "tuple[bool, str]":
    """Is the file ON DISK sound, and is it better than what the user started with?

    Every gate before this validated a candidate patch against a temp copy.  The
    file that ends up on disk is a RECONSTRUCTION — the survivors re-applied
    onto the original — and that is not automatically the thing any gate looked
    at.  Trusting the reconstruction is how a pragma the gate rejects
    deterministically ended up in the source.

    So this re-runs the real gate against the actual final content: compile, the
    -fopenmp build, ThreadSanitizer, and output.  Speed is asked only under
    --require-speedup, and separately, because it is the user's switch for
    whether that question is asked at all.
    """
    final_text = Path(args.source_file).read_text()
    if normalize_code(final_text) == normalize_code(original_text):
        return True, "source unchanged"

    with tempfile.TemporaryDirectory(prefix="dp_agent_check_") as tmp:
        base = Path(tmp) / Path(args.source_file).name
        base.write_text(original_text)
        cumulative = make_diff(original_text, final_text, str(base))
        def _run(skip: bool) -> ValidationResult:
            return validate(
                cumulative, str(base), reference_output=reference_output,
                reference_outputs=reference_outputs, binary_args=binary_args,
                require_speedup=False, reference_time=reference_time,
                skip_race_check=skip, mode="safety",
            )

        res = _run(False)
        # The macOS OMP-barrier artefact applies here exactly as it does to a
        # single pragma, and forgetting it is worse at this end: every pragma
        # would pass its own gate (which does re-check) and then be thrown away
        # by this one, so the run could never keep anything on this platform.
        if (not res.passed and res.stage == "tsan"
                and _is_omp_barrier_false_positive(res.diagnostic)):
            print(f"  [note] TSan OMP-barrier false positive on the finished file "
                  f"— re-verifying on output instead")
            res = _run(True)
        if not res.passed:
            return False, (f"the finished file fails at '{res.stage}': "
                           f"{res.diagnostic[:160].replace(chr(10), ' ')}")

        if args.require_speedup and reference_time is not None:
            ok_t, t_final, _out, tdiag = time_source(
                final_text, args.source_file, Path(tmp), "final", binary_args, repeats=5
            )
            if not ok_t:
                return False, f"could not time the finished program: {tdiag[:120]}"
            if t_final > reference_time:
                return False, (f"slower than the original: {t_final*1e3:.1f} ms vs "
                               f"{reference_time*1e3:.1f} ms")
            return True, (f"output matches, {t_final*1e3:.1f} ms vs "
                          f"{reference_time*1e3:.1f} ms original")
    return True, "output matches the original"


def _settle(
    original_text: str, change_log: list, args: AgentArguments,
    output_dir: Path, reference_output: "str | None",
    reference_outputs: "list | None", binary_args: "list | None",
    reference_time: "float | None",
) -> "tuple[list, list]":
    """Reduce the run to a set of changes that is sound AND worth keeping.

    Three things happen here, in one loop, because they are the same operation:

      1. ORPHANS.  A Phase-A rewrite exists to let DiscoPoP parallelize
         something.  If no kept pragma targets a region it exposed, it achieved
         nothing — and it is not free, so it goes.  Justification is by region
         FINGERPRINT, not line containment: regions nest, and their line spans
         drift as changes land above them.  A rewrite that carries its OWN
         pragmas (--llm-pragmas) is its own justification and is never an
         orphan — the parallelism is in the change itself, not in what DiscoPoP
         made of it afterwards.

      2. RECONSTRUCTION.  Rebuild by re-applying survivors onto a fresh copy of
         the original rather than un-applying anything, so no patch is ever
         reversed and dependence is discovered instead of computed.

      3. VERIFICATION.  Re-gate the RESULT.  Every earlier gate judged a
         candidate patch against a temp copy; the reconstruction is a different
         artifact and has to earn its own verdict.  While it fails, drop the
         most recently applied pragma and rebuild again — newest first, because
         later pragmas are the least likely to be load-bearing and the most
         likely to be the interaction that broke it.

    Returns (surviving change log, human-readable notes about what was dropped).
    """
    notes: list = []
    keep = list(change_log)

    while True:
        applied_prints = {c["fingerprint"] for c in keep
                          if c["kind"] == "pragma" and c.get("fingerprint")}
        pruned: list = []
        for ch in keep:
            if ch["kind"] == "pragma":
                pruned.append(ch)
            elif ch.get("self_annotated"):
                pruned.append(ch)
            elif applied_prints & set(ch.get("exposed", [])):
                pruned.append(ch)
            else:
                notes.append(f"rewrite of {ch['region_id']} — exposed "
                             f"{len(ch.get('exposed', []))} region(s), none kept a pragma")
        keep = pruned

        landed = _apply_change_log(original_text, keep, args)
        for ch in keep:
            if ch not in landed:
                notes.append(f"{ch['kind']} for {ch['region_id']} — depended on a "
                             f"change that was dropped, so it no longer applies")
        keep = landed

        ok, why = _check_final_source(args, original_text, reference_output,
                                      reference_outputs, binary_args, reference_time)
        if ok:
            if why != "source unchanged":
                print(f"  [ok] finished source verified — {why}")
            return keep, notes

        # Newest first, and DiscoPoP's pragmas before the LLM's own: a pragma
        # applied on top of finished code is the cheaper thing to lose than a
        # restructuring that carries its parallelism with it.
        droppable = ([c for c in keep if c["kind"] == "pragma"]
                     or [c for c in keep if c.get("self_annotated")])
        if not droppable:
            # Nothing left to drop and it still does not hold up: the rewrites
            # alone are the problem, so put the user back where they started.
            Path(args.source_file).write_text(original_text)
            notes.append(f"everything reverted — {why}")
            print(f"  [revert] {why}")
            return [], notes

        victim = droppable[-1]
        what = ("pragma" if victim["kind"] == "pragma"
                else "self-annotated rewrite")
        keep.remove(victim)
        notes.append(f"{what} for {victim['region_id']} — dropped because {why}")
        print(f"  [repair] {why}")
        print(f"           → dropping the {what} for {victim['region_id']} and re-checking")


def _already_annotated(diff: str, source_file: str) -> bool:
    """Does the loop this generated patch targets already carry a pragma?

    Under --llm-pragmas this really happens: the LLM annotates a loop, the
    re-profile runs on the annotated source — the instrumented build has no
    -fopenmp, so the pragmas are ignored and the dependences come out
    sequential, exactly as they should — and DiscoPoP then proposes a pattern
    for a loop that is already parallel.  Applying its pragma on top would put
    one worksharing construct directly inside another.
    """
    pa = _pragma_and_anchor(diff)
    if pa is None:
        return False
    _pragma, header = pa
    try:
        src = Path(source_file).read_text().splitlines()
    except OSError:
        return False
    span = _touched_span(diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return False
    for j in range(head - 1, max(head - 4, -1), -1):
        st = src[j].strip()
        if not st or st.startswith("//"):
            continue
        return bool(_PRAGMA_LINE_RE.match(src[j]))
    return False


def _phase_b(
    args: AgentArguments, dp_dir: Path, output_dir: Path,
    reference_output: "str | None", reference_outputs: "list | None",
    binary_args: "list | None", reference_time: "float | None",
    gate_cache: dict, change_log: list,
) -> list:
    """Annotate: apply every DiscoPoP pragma that survives validation.

    Runs ONCE, after all restructuring, and never re-profiles.  That is the
    whole point: the source is pragma-free on entry, so the profile in dp_dir
    describes exactly the code being annotated.  Interleaving this with
    restructuring is what used to leave every queued patch racing a file that
    had already shifted under it.

    Order is by workload, largest first, so the pragma most likely to matter is
    measured against the cleanest baseline.  Each patch is re-derived against
    the CURRENT file rather than replayed from a stored diff, so applying one
    pragma cannot invalidate the next.
    """
    kept: list = []
    fresh = build_candidates(dp_dir, args.source_file, args.lambda_penalty,
                             args.min_workload)
    todo = [c for c in fresh
            if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")]
    todo.sort(key=lambda c: c.workload_estimate, reverse=True)

    print(f"\n{'='*60}")
    print(f"  PHASE B — annotate  ({len(todo)} candidate pragma(s))")
    print(f"{'='*60}\n")
    if not todo:
        print("  DiscoPoP proposes no applicable pattern for the final source.\n")
        return kept

    # What counts as "not slower" is whatever this machine's jitter can already
    # produce for an unchanged file.  One compile, then alternating runs.
    threshold = _MARGINAL_NOISE
    if args.require_speedup and not args.dry_run:
        ok_n, floor, ndiag = noise_floor(
            Path(args.source_file).read_text(), args.source_file, binary_args
        )
        if ok_n:
            threshold = min(floor - 0.01, 0.99)
            print(f"  Timing noise floor on this machine: {floor:.3f} "
                  f"→ keep anything at or above {threshold:.3f}\n")
        else:
            print(f"  [warn] could not calibrate timing noise ({ndiag[:60]}); "
                  f"falling back to {threshold:.2f}\n")

    for cand in todo:
        rid = cand.region.region_id
        pid = cand.pattern.get("pattern_id", "?") if cand.pattern else "?"
        pragma = (cand.pattern or {}).get("pragma", "")
        lines = f"{cand.region.start_line}–{cand.region.end_line}"
        print(f"┌─ pattern #{pid}  {cand.pattern_type or 'pattern'} @ lines {lines}"
              f"  (W={cand.workload_estimate:.0f})")
        print(f"│  {pragma}")

        if cand.workload_estimate < args.min_workload:
            print(f"│  workload below --min-workload → not worth a thread")
            print(f"└─ SKIPPED\n")
            continue

        # Re-derive against the file as it stands: earlier pragmas in this same
        # phase have already moved every line below them.
        diff = _repair_pragma_clauses(
            derive_pragma_patch(
                _read_tier1_patch(dp_dir / "patch_generator" / str(pid)),
                args.source_file,
            ),
            args.source_file,
        )
        if not diff:
            print(f"│  no generated patch on disk")
            print(f"└─ SKIPPED\n")
            continue

        if _already_annotated(diff, args.source_file):
            print(f"│  this loop is already annotated in the source")
            print(f"└─ SKIPPED (nothing to add)\n")
            continue

        # 1. static — the only check that sees a clause handing back a value it
        #    cannot hand back.
        problem = check_pragma_clauses(diff, args.source_file)
        if problem:
            print(f"│  clause check: {problem}")
            print(f"└─ DROPPED (bad data-sharing clause)\n")
            continue

        if args.dry_run:
            print(f"└─ DRY RUN — not applied\n")
            continue

        # 2. does it work?  Everything except the timing.
        res, from_cache, barrier_fp = _validate_cached(
            gate_cache, diff, args, reference_output, binary_args,
            reference_time, reference_outputs=reference_outputs, mode="safety",
        )
        if barrier_fp:
            print(f"│  TSan OMP-barrier false positive — re-verified on output")
        if not res.passed:
            print(f"│  gate failed at '{res.stage}': "
                  f"{res.diagnostic[:150].replace(chr(10), ' ')}")
            print(f"└─ DROPPED\n")
            continue

        # 3. is it worth it?  Only when the user asked for that question.
        marginal = None
        if args.require_speedup:
            before = Path(args.source_file).read_text()
            after = _apply_in_memory(diff, args.source_file)
            if after is None:
                print(f"│  could not stage the patch for measurement")
                print(f"└─ DROPPED\n")
                continue
            ok_m, marginal, mdiag = measure_marginal(
                before, after, args.source_file, binary_args
            )
            if not ok_m:
                print(f"│  measurement failed: {mdiag[:120]}")
                print(f"└─ DROPPED\n")
                continue
            if marginal < threshold:
                print(f"│  marginal {marginal:.2f}× — costs more than it saves")
                print(f"└─ DROPPED (slower)\n")
                continue
            print(f"│  marginal {marginal:.2f}×")

        fp_before = region_fingerprint(args.source_file, cand.region.start_line,
                                       cand.region.end_line, cand.region.name)
        if not _apply_to_source(diff, args.source_file, output_dir, "Phase-B"):
            print(f"└─ DROPPED (patch would not apply)\n")
            continue

        record = {
            "region_id": rid,
            "region_type": cand.region.region_type,
            "phase": "B",
            "pattern_id": pid,
            "pragma": pragma,
            "lines": lines,
            "marginal_speedup": marginal,
            "applied_to_source": True,
        }
        # Identity of the region this pragma landed on, taken BEFORE the patch
        # went in, so it matches what Phase A recorded as exposed.
        change_log.append({
            "kind": "pragma", "region_id": rid, "diff": diff,
            "fingerprint": fp_before,
        })
        kept.append(record)
        _write_record(output_dir, record, args.dry_run)
        print(f"└─ APPLIED\n")
    return kept


def _rewrite_feedback(
    outcome: RewriteOutcome, dp_dir: Path, file_id: int,
    touched: "tuple[int, int] | None",
) -> str:
    """Turn a failed post-restructuring verdict into the message the LLM sees.

    This is the only place DiscoPoP's own opinion of the model's rewrite reaches
    the model.  Each verdict gets a different instruction, because they mean
    opposite things: "no pattern" means the dependence is still there, while
    "no speedup" means it is gone and only granularity is wrong — telling the
    model to keep hunting for dependences in that case sends it backwards.
    """
    if outcome.status == "no_pattern":
        msg = (
            "DiscoPoP re-profiled your rewrite. Your code compiles and its output is "
            "correct, but DiscoPoP STILL finds no parallel pattern in the lines you "
            "changed — so the rewrite achieved nothing and has been reverted.\n\n"
            "The blocking dependence is therefore still present. Do not re-submit a "
            "variation of the same structure — the blockers below are DiscoPoP's "
            "analysis OF YOUR REWRITE, not of the original code, so read them as a "
            "description of what you just wrote."
        )
        blockers = fmt_blockers(
            load_prevented_deps(dp_dir, file_id, *(touched or (1, 10**9)))[:12]
        )
        if blockers:
            msg += (
                "\n\nWhat DiscoPoP reports about YOUR REWRITTEN CODE:\n" + blockers
            )
        else:
            msg += (
                "\n\nDiscoPoP reported no specific Do-All blocker for those lines, "
                "which usually means the loop is not in a form it analyses at all: "
                "check that the loop you intended to be parallel has a computable "
                "trip count, a simple `i < bound` condition, and no break/continue/"
                "return in its body."
            )
        return msg

    if outcome.status == "pattern_broken":
        return (
            f"Progress: after your rewrite DiscoPoP DID detect parallelism "
            f"({outcome.pattern_label}).\n\n"
            f"Your rewrite is correct on its own — it already passed the sequential "
            f"output check. What failed is running it in parallel: DiscoPoP added "
            f"its `#pragma omp` to your code and that build broke. The rewrite has "
            f"been reverted.\n\n"
            f"So the thing to find is not a bug in your logic but an ordering "
            f"assumption — something in the body that only holds when iterations run "
            f"one after another. Keep the structure that made the loop detectable.\n\n"
            f"Reading the diagnostic: it comes from validating YOUR CODE PLUS THAT "
            f"PRAGMA, so a complaint that the program is not semantically equivalent "
            f"is not about your rewrite alone. And if the outputs differ only in the "
            f"last digits of floating-point values, a parallel reduction reassociated "
            f"the arithmetic — that is not a dependence.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:1200]}"
        )

    if outcome.status == "no_usable_pragma":
        return (
            f"Close: after your rewrite DiscoPoP DOES report parallelism "
            f"({outcome.pattern_label}). But every pragma it generates for those "
            f"lines is rejected before it can run, so the rewrite cannot lead to "
            f"a parallel build and has been reverted.\n\n"
            f"That is almost always the loop's SHAPE. OpenMP needs the trip count "
            f"known before the loop starts: the condition has to compare the loop "
            f"variable directly against a bound that does not change inside the "
            f"loop, and the body must contain no break, continue, return or goto. "
            f"A bound computed at run time — `for (i = start; ...)` where `start` "
            f"is set inside an enclosing loop — reads as parallel to the profiler "
            f"and is rejected by the compiler.\n\n"
            f"Rewrite the loop so its bounds are plain expressions of the loop "
            f"variable and loop-invariant values.\n\n"
            f"{outcome.diagnostic}"
        )

    if outcome.status == "no_speedup":
        got = f"{outcome.speedup:.2f}x" if outcome.speedup else "no measurable gain"
        return (
            f"Your rewrite worked in every respect except the one that matters: "
            f"DiscoPoP parallelized it ({outcome.pattern_label}) and the parallel "
            f"build is CORRECT, but it is not faster ({got}). It has been reverted.\n\n"
            f"The dependence is already gone, so do not go looking for one again. "
            f"The parallel work is too fine-grained to cover thread startup: each "
            f"iteration needs to do more, or the parallelism needs to move to a "
            f"level that has more work per activation.\n\n"
            f"Diagnostic:\n{outcome.diagnostic[:800]}"
        )

    return (
        "Your rewrite compiled and produced correct output, but DiscoPoP could not "
        "instrument or profile it, so it cannot be parallelized at all. It has been "
        "reverted. Avoid constructs that change the program's structure in ways the "
        "profiler cannot follow (unusual templates, macros, computed control flow); "
        "prefer a plain loop rewrite.\n\n"
        f"{outcome.diagnostic}"
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(args: AgentArguments) -> None:
    dp_dir = Path(args.discopop_dir)
    profiler_dir = dp_dir / "profiler"
    output_dir = Path(args.output_dir)
    # A dry run promises no file changes, so don't even create the output dir.
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    viz.enable(args.verbose)
    _print_banner(args)

    # Golden reference output: the unmodified program's stdout.  Every patched
    # version must reproduce it (semantic-equivalence gate).  None if the program
    # can't be built/run cleanly up front, in which case correctness is skipped.
    binary_args = args.reprofil_args or None
    reference_output, reference_time, reference_outputs = capture_reference(
        args.source_file, binary_args, extra_inputs=args.check_inputs or None
    )
    if reference_output is None:
        print("  [warn] Could not capture reference output — correctness gate disabled.\n")
    else:
        rt = f", {reference_time*1e3:.1f} ms baseline" if reference_time else ""
        n = len(reference_outputs or [])
        extra = f" on {n} inputs" if n > 1 else " on 1 input"
        print(f"  [ok] Captured reference output{extra} ({len(reference_output)} bytes{rt}) "
              f"for the correctness/performance gates.")
        if n == 1:
            print("  [note] one input only — a rewrite that is wrong for other sizes "
                  "would still pass. Add --check-input to widen the check.")
        print()

    # Gate results for this run, keyed by (patch, source text).
    # A pattern measured by the post-rewrite verification is normally measured
    # again by the Tier-1 pass that applies it, one queue position later; this
    # lets the second ask reuse the first answer.  Scoped to the run rather than
    # module-global so nothing leaks between runs.
    gate_cache: dict = {}

    # Set only when a kept rewrite could not be re-profiled (--llm-pragmas keeps
    # such a rewrite because the gate, not DiscoPoP, judged it).  Phase B has no
    # profile it can trust after that, so it does not run.
    profile_stale = False
    # True once a fast refresh has left carried-forward dependence data in the
    # profile.  Phase B annotates from measured data, so this is settled with one
    # full re-profile before it runs rather than being allowed to accumulate.
    profile_is_fast = False

    accepted: List[dict] = []
    # Regions DiscoPoP can already parallelize: Phase A skips them, Phase B
    # picks them up from the final profile.
    deferred: List[tuple] = []
    original_text = Path(args.source_file).read_text()
    # Ordered record of every change written to the source, so the end of the
    # run can rebuild from the original keeping only what earned its place.
    change_log: List[dict] = []
    # Each entry is (region_id, discovery_depth).  A region ID can appear more
    # than once (different content versions across re-profiles reuse IDs); the
    # summary de-duplicates and drops IDs that were ultimately accepted.
    skipped: List[tuple] = []

    # Tracks the CONTENT fingerprint of every region ever enqueued across all
    # re-profile cycles.  Region IDs drift after a patch (global counter), so
    # identity is keyed on source text instead — see region_fingerprint() in l1_planner.py.
    all_seen_prints: set = set()

    initial = build_candidates(
        dp_dir, args.source_file, args.lambda_penalty, args.min_workload
    )
    if not initial:
        print("No hotspot regions found. Run discopop_explorer first.")
        return

    # candidates: list of (discovery_depth, HotspotCandidate)
    # depth=0 → initial profile; depth=N → discovered after N Tier-2 re-profiles
    # P0 — what DiscoPoP achieves unaided.  Counted to the SAME standard the
    # run's own output is held to: a pattern DiscoPoP merely claims is not a
    # working pragma.  On example4 the one "applicable" pattern is
    # `private(ok)` on the sortedness check, which compiles into a program that
    # reports success even with the sort deleted — so the honest baseline there
    # is 0, and counting it as 1 made every run look like a regression.
    claimed = [c for c in initial
               if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")]
    baseline_pragmas = 0
    for c in claimed:
        cpid = c.pattern.get("pattern_id", "?") if c.pattern else "?"
        d = derive_pragma_patch(
            _read_tier1_patch(dp_dir / "patch_generator" / str(cpid)),
            args.source_file,
        )
        if not d or check_pragma_clauses(d, args.source_file):
            continue
        ok_c, _diag = check_pragma_compiles(d, args.source_file)
        baseline_pragmas += 1 if ok_c else 0
    dropped_baseline = len(claimed) - baseline_pragmas
    print(f"  Baseline       : DiscoPoP proposes {len(claimed)} applicable "
          f"pattern(s) unaided; {baseline_pragmas} of them produce a usable pragma"
          + (f" ({dropped_baseline} rejected before it could run)"
             if dropped_baseline else ""))
    print(f"                   → the run beats DiscoPoP by ending with more than "
          f"{baseline_pragmas}\n")

    candidates: list = [(0, c) for c in initial]
    all_seen_prints.update(
        region_fingerprint(args.source_file, c.region.start_line, c.region.end_line, c.region.name)
        for c in initial
    )

    print("  Initial candidates")
    _print_candidates(candidates)

    print(f"{'='*60}")
    print(f"  PHASE A — restructure  (the source stays pragma-free)")
    print(f"{'='*60}\n")

    # ── Candidate loop ────────────────────────────────────────────────────────
    # Index-based so candidates appended mid-run (from re-profiling) are
    # picked up automatically.
    i = 0
    while i < len(candidates):
        depth, candidate = candidates[i]
        i += 1
        region = candidate.region
        rid = region.region_id
        rtype = _REGION_LABEL.get(region.region_type, region.region_type)
        label = f"{rtype} {rid} (lines {region.start_line}–{region.end_line})"

        # Tier-2 (LLM restructuring) is only allowed up to restructure_depth.
        tier2_allowed = (depth <= args.restructure_depth)

        print(f"┌─ [depth={depth}] {label}  score={candidate.score:.1f}")

        # ── Tier-1 ───────────────────────────────────────────────────────────
        failure_reason = "DiscoPoP found no applicable parallelism pattern for this region"
        if candidate.tier == 1 and candidate.pattern and candidate.pattern.get("applicable_pattern"):
            # PHASE A leaves this alone.  DiscoPoP can already parallelize it,
            # so there is nothing to restructure — and inserting its pragma now
            # is exactly what used to invalidate the profile every later
            # decision depends on.  Phase B collects it from the final profile
            # and applies it there, once, with nothing left to shift underneath.
            pragma = candidate.pattern.get("pragma", "")
            print(f"│  [Phase-A] DiscoPoP already has a pattern here "
                  f"({candidate.pattern_type or 'pattern'}) — deferred to Phase B")
            print(f"└─ DEFERRED\n")
            deferred.append((rid, depth))
            continue

        # ── Tier-2: LLM restructuring ─────────────────────────────────────────
        if candidate.tier != 1:
            print(f"│  [Tier-1] No applicable pattern → Tier-2 (LLM)")

        if not tier2_allowed:
            print(f"│  [Tier-2] Restructuring not allowed at depth {depth} "
                  f"(--restructure-depth={args.restructure_depth}) → SKIP")
            print(f"└─ SKIPPED\n")
            skipped.append((rid, depth))
            continue

        if args.dry_run:
            print(f"│  [Tier-2] DRY RUN — skipping LLM call")
            print(f"└─ SKIPPED\n")
            skipped.append((rid, depth))
            continue

        budget = args.budget
        tier2_messages: list | None = None

        # Any restructuring may need reverting — it is kept only if DiscoPoP can
        # parallelize it afterwards — so snapshot the profile ONCE up front and
        # restore by file-copy instead of a full re-profile.  The pre-patch
        # source is identical across retries (revert restores it), so one
        # snapshot serves every attempt for this candidate.
        dp_snapshot: Path | None = None
        pre_patch_src: str | None = None
        pre_patch_src = Path(args.source_file).resolve().read_text()
        dp_snapshot = _snapshot_profile(dp_dir, output_dir)

        # Build errors (bad syntax, non-canonical loop) are mechanical fixes that
        # say nothing about the model's parallelization idea; spending a whole
        # budget slot on one wastes the region's real attempts.  They get their
        # own small allowance instead, capped so a model that cannot produce
        # compiling code still terminates.
        build_retries = args.build_retries

        while budget > 0:
            budget -= 1
            print(f"│  [Tier-2] Assembling evidence (budget remaining: {budget})")

            evidence = assemble(candidate, profiler_dir, failure_reason)

            print(f"│  [Tier-2] Calling {args.model}...")
            try:
                diff, tier2_messages = call_llm(
                    evidence, args.model,
                    api_key=args.api_key,
                    messages=tier2_messages,
                    provider=args.provider,
                    api_base=args.api_base,
                    edit_mode=args.edit_mode,
                    llm_pragmas=args.llm_pragmas,
                    verbose=args.verbose,
                )
            except LLMConnectionError as e:
                # Fatal for the whole run: every region needs the endpoint.
                print(f"│  [Tier-2] FATAL: {e}")
                print(f"└─ aborting — start the LLM server (or fix --api-base) and re-run\n")
                sys.exit(1)
            except Exception as e:                   # noqa: BLE001 - reported below
                # The backend failed this call even after its own retries.  That
                # is a bad attempt, not a broken run: everything already accepted
                # stays, and the next region still gets its chance.  Losing an
                # entire run to one flaky call is how a 20-minute job ends with
                # nothing to show.
                print(f"│  [Tier-2] LLM call failed: {str(e)[:120]}")
                print(f"│           counting it as a failed attempt and moving on")
                diff, tier2_messages = None, tier2_messages

            # In function mode the LLM returns the rewritten enclosing function;
            # splice it in and turn it into a guaranteed-apply diff.  In direct
            # mode it edited a copy of the file itself and call_llm already
            # returned that copy's diff ("" if it changed nothing).
            unchanged = False
            if diff is not None and args.edit_mode == "function":
                diff = _function_edit_to_diff(
                    args.source_file,
                    evidence.enclosing_function_start,
                    evidence.enclosing_function_end,
                    diff,
                )
                unchanged = diff is None
            elif diff == "":
                diff, unchanged = None, True

            if unchanged:
                what = ("You left the file UNCHANGED"
                        if args.edit_mode == "direct"
                        else "You returned the function UNCHANGED")
                print(f"│  [Tier-2] LLM produced no change"
                      f"{' — retrying' if budget > 0 else ''}")
                # Without feedback the next call would replay the same
                # conversation and get the same null answer — tell the model
                # explicitly that returning the input is not a valid move.
                if tier2_messages is not None:
                    tier2_messages = tier2_messages + [{
                        "role": "user",
                        "content": (
                            f"{what} (comment or formatting edits do not count). "
                            "That is not an answer: the blocking dependence has to be "
                            "gone. If your last attempt failed validation, do not fall "
                            "back to the original — restructure it a different way."
                        ),
                    }]

            if diff is None:
                if unchanged:
                    pass  # already reported above
                elif budget > 0:
                    print(f"│  [Tier-2] LLM returned invalid output — retrying")
                else:
                    print(f"│  [Tier-2] LLM returned invalid output")
                continue

            # Under --llm-pragmas a diff that carries a pragma is a finished
            # parallelization, not a step towards one: validate() then runs its
            # -fopenmp build, ThreadSanitizer, the output check against the
            # PARALLEL binary and (with --require-speedup) the timing — all of
            # which it skips for a pragma-less diff, because there is nothing
            # there to race or to speed up.
            pragmas = _added_pragmas(diff) if args.llm_pragmas else []
            self_annotated = bool(pragmas)
            if self_annotated:
                stages = ("apply/compile/openmp/TSan/output"
                          + ("/speed" if args.require_speedup else ""))
                print(f"│  [Tier-2] Diff received with {len(pragmas)} pragma(s) — "
                      f"running quality gate ({stages})")
                for pr in pragmas[:4]:
                    print(f"│           {pr}")
            else:
                print(f"│  [Tier-2] Diff received — running quality gate "
                      f"(apply/compile/correctness)")

            # Cheapest stage first, and the only one that can see a clause which
            # compiles, races nowhere, prints the right answer, and still throws
            # the loop's results away.
            result = None
            barrier_fp = False
            if self_annotated:
                problem = check_llm_pragmas(diff, args.source_file)
                if problem:
                    result = ValidationResult(passed=False, stage="clause",
                                              diagnostic=problem)
            if result is None:
                # Through _validate_cached, not validate() directly: this is
                # where a suspected OMP-barrier false positive is re-verified
                # against output instead of being trusted.  Phase A used to call
                # validate() raw, so that re-check never applied to an LLM
                # rewrite — which only started to matter once the rewrite could
                # carry pragmas of its own, and TSan on this platform reports a
                # race between any two parallel regions.
                result, _cached, barrier_fp = _validate_cached(
                    gate_cache, diff, args, reference_output, binary_args,
                    reference_time, reference_outputs=reference_outputs,
                )
            if barrier_fp:
                print(f"│  [Tier-2] TSan flagged two DIFFERENT parallel regions — a "
                      f"barrier separates them, so this is the libomp/TSan artefact. "
                      f"Re-verified on output instead.")
            # The clause check is the controller's stage, not validate()'s, so
            # it has to declare itself skipped when it does not apply — the
            # renderer would otherwise show a green tick for a check that never ran.
            gate_skipped = list(result.skipped_stages)
            if not self_annotated:
                gate_skipped.insert(0, "clause")
            viz.gate_result(result.passed, result.stage, result.diagnostic,
                            result.measured_speedup, skipped_stages=gate_skipped)

            if result.passed:
                print(f"│  [Tier-2] Quality gate PASSED")

                clean_diff = fix_hunk_headers(diff)
                patch_file = output_dir / f"region_{rid.replace(':', '_')}_tier2.patch"
                patch_file.write_text(clean_diff)

                src_abs = Path(args.source_file).resolve()

                # Snapshot the CONTENT fingerprint of each still-queued candidate
                # BEFORE the patch touches the file.  A survivor (a region we
                # haven't processed and didn't patch) has identical text before
                # and after, so its fingerprint matches a fresh candidate even
                # though its ID drifted and its line numbers may have shifted.
                # NOTE: candidates[i:] is NOT deleted yet — if the restructuring
                # turns out not to pay off we revert and keep the queue intact.
                old_prints = [
                    (
                        d,
                        region_fingerprint(args.source_file, c.region.start_line,
                                     c.region.end_line, c.region.name),
                    )
                    for d, c in candidates[i:]
                ]

                if _apply_to_source(clean_diff, args.source_file, output_dir, "Tier-2"):
                    viz.panel(f"APPLIED PATCH -> {src_abs.name}", clean_diff,
                              color=viz.GREEN, colorize=viz._color_diff_line, max_lines=60)

                record = {
                    "region_id": rid,
                    "region_type": region.region_type,
                    "tier": 2,
                    "patch_file": str(patch_file),
                    "reprofiled": False,
                    "discovery_depth": depth,
                }

                # A deeper Tier-2 pass restructures from this profile, so it
                # gets measured data; a refresh that only has to relocate the
                # queue and find new regions does not.  Phase B is covered
                # separately, by one full re-profile before it runs.
                deeper_coming = (depth + 1) <= args.restructure_depth
                use_fast = args.fast_refresh and not deeper_coming
                if use_fast:
                    print(f"│  [Tier-2] Fast refresh (compile only, no instrumented run)...")
                    reprofile_ok, note = _reprofil_fast(
                        args.source_file, dp_dir, pre_patch_src or "",
                        Path(args.source_file).read_text(), output_dir,
                    )
                    if reprofile_ok:
                        print(f"│           {note}")
                        profile_is_fast = True
                        if args.llm_deps:
                            gaps = _llm_dep_review(
                                args, dp_dir, pre_patch_src or "",
                                Path(args.source_file).read_text(), output_dir,
                                region.file_id,
                            )
                            if gaps:
                                print(f"│           {gaps}")
                    else:
                        print(f"│           fast refresh not usable ({note}) "
                              f"— falling back to a full re-profile")
                        reprofile_ok = _reprofil(
                            args.source_file, dp_dir, args.reprofil_args or None
                        )
                else:
                    if args.fast_refresh and deeper_coming:
                        print(f"│  [Tier-2] Full re-profile — depth {depth + 1} will "
                              f"restructure from this data")
                    else:
                        print(f"│  [Tier-2] Re-profiling to refresh data and discover new candidates...")
                    reprofile_ok = _reprofil(
                        args.source_file, dp_dir, args.reprofil_args or None
                    )

                # rebuilt / discovered are computed read-only first; the queue and
                # all_seen_prints are only mutated once we decide to COMMIT.
                rebuilt: list = []
                discovered: list = []   # (depth+1, candidate, fingerprint)
                fresh_all: list = []
                if reprofile_ok:
                    fresh_all = build_candidates(
                        dp_dir, args.source_file, args.lambda_penalty, args.min_workload
                    )
                    fresh_by_print: dict = defaultdict(list)
                    for nc in fresh_all:
                        fp = region_fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        fresh_by_print[fp].append(nc)

                    consumed: set = set()
                    for old_depth, fp in old_prints:
                        for nc in fresh_by_print.get(fp, []):
                            if id(nc) not in consumed:
                                rebuilt.append((old_depth, nc))
                                consumed.add(id(nc))
                                break

                    for nc in fresh_all:
                        if id(nc) in consumed:
                            continue
                        fp = region_fingerprint(args.source_file, nc.region.start_line,
                                          nc.region.end_line, nc.region.name)
                        if fp not in all_seen_prints:
                            discovered.append((depth + 1, nc, fp))

                # ── THE POINT OF THE WHOLE EXERCISE ───────────────────────────
                # Compiling and preserving output only makes the rewrite HARMLESS.
                # It is WORTH keeping only if DiscoPoP can now parallelize the
                # lines that changed.  Ask it, every time — never assume.
                if self_annotated:
                    # The question Phase A normally asks DiscoPoP — "can you
                    # parallelize this now?" — has already been answered, by the
                    # model, in the diff.  The gate above judged that answer the
                    # hard way: sanitizer, output from the parallel build, clock.
                    # Re-profiling still runs, but only to refresh line numbers
                    # and find new candidates; its verdict no longer decides.
                    outcome = RewriteOutcome(
                        "self_annotated", speedup=result.measured_speedup,
                        pattern_label=f"{len(pragmas)} LLM pragma(s): "
                                      + "; ".join(pragmas[:2]),
                    )
                    if not reprofile_ok:
                        # The parallelization is validated and stays.  What is
                        # unusable is the PROFILE, so put the coherent one back
                        # and stop trusting DiscoPoP for the rest of this run.
                        if dp_snapshot is not None:
                            _restore_profile(dp_snapshot, dp_dir, output_dir)
                        profile_stale = True
                        print(f"│  [Tier-2] Re-profiling failed — the rewrite is kept "
                              f"(it passed the whole gate), but Phase B is skipped: "
                              f"there is no profile that describes this file")
                elif not reprofile_ok:
                    outcome = RewriteOutcome(
                        "reprofile_failed",
                        diagnostic="DiscoPoP could not instrument, run, or analyse the "
                                   "rewritten program (see the log above).",
                    )
                else:
                    # Validating the exposed pragma is deferred only when a deeper
                    # Tier-2 pass is still allowed to work on it.
                    # Phase A asks one question: did the rewrite expose a
                    # pattern in the lines it changed?  Whether the resulting
                    # pragma works is Phase B's question, asked once, later.
                    print(f"│  [Phase-A] Asking DiscoPoP what it now finds in the "
                          f"rewritten lines...")
                    outcome = _verify_rewrite(
                        fresh_all, _touched_span(clean_diff), dp_dir, args,
                        reference_output, binary_args, reference_time,
                        validate_patterns=False, gate_cache=gate_cache,
                        reference_outputs=reference_outputs,
                    )

                if outcome.status not in ("ok", "exposed", "self_annotated"):
                    # REVERT — the restructuring did not achieve its purpose.
                    # Restore source + the pre-patch profile from the snapshot
                    # (file copy) instead of re-profiling — far cheaper.
                    if pre_patch_src is not None:
                        src_abs.write_text(pre_patch_src)
                    if dp_snapshot is not None:
                        _restore_profile(dp_snapshot, dp_dir, output_dir)
                    patch_file.unlink(missing_ok=True)
                    msg = _rewrite_feedback(
                        outcome, dp_dir, region.file_id, _touched_span(clean_diff)
                    )
                    print(f"│  [Tier-2] {_OUTCOME_LABEL[outcome.status]} — reverting "
                          f"(snapshot restore)")
                    viz.panel("DISCOPOP → LLM FEEDBACK", msg, color=viz.YELLOW, max_lines=30)
                    failure_reason = msg
                    if tier2_messages is not None:
                        tier2_messages = tier2_messages + [
                            {"role": "user", "content": msg}
                        ]
                    print(f"└─ retry (budget remaining: {budget})\n")
                    continue  # budget already decremented at loop top

                exposed_speedup = outcome.speedup

                # ── COMMIT ────────────────────────────────────────────────────
                del candidates[i:]
                candidates.extend(rebuilt)
                candidates.extend((d, nc) for d, nc, _ in discovered)
                for _d, _nc, fp in discovered:
                    all_seen_prints.add(fp)
                if reprofile_ok:
                    print(f"│  [Tier-2] {len(rebuilt)} survivor(s) rebuilt, "
                          f"{len(discovered)} new at depth {depth + 1}")
                    record["reprofiled"] = True
                record["exposed_pattern"] = outcome.pattern_label
                if self_annotated:
                    record["pragmas"] = len(pragmas)
                    record["pragma_text"] = pragmas
                    record["self_annotated"] = True
                change_log.append({
                    "kind": "rewrite", "region_id": rid, "diff": clean_diff,
                    "exposed": outcome.exposed_prints,
                    "self_annotated": self_annotated,
                    "pragmas": len(pragmas),
                })
                if self_annotated:
                    print(f"│  [Tier-2] Kept on its own pragmas: {len(pragmas)} "
                          f"annotated loop(s), gate passed end to end")
                else:
                    print(f"│  [Tier-2] DiscoPoP now finds: {outcome.pattern_label}")
                if exposed_speedup is not None:
                    record["exposed_speedup"] = exposed_speedup
                    print(f"│  [Tier-2] Restructuring pays off "
                          f"({'measured' if self_annotated else 'best exposed loop'} "
                          f"{exposed_speedup:.2f}×)")
                elif outcome.status == "exposed":
                    print(f"│  [Tier-2] Pragma validation deferred to depth "
                          f"{depth + 1} (still allowed to restructure)")

                accepted.append(record)
                _write_record(output_dir, record, args.dry_run)
                print(f"└─ ACCEPTED\n")
                break

            else:
                # A failure-stage → plain-English instruction for the LLM, so the
                # next prompt always says WHY (apply/compile/openmp_compile/tsan/
                # correctness/performance) and what to do about it.
                _STAGE_GUIDANCE = {
                    "clause": "A data-sharing clause on a pragma YOU wrote cannot be "
                             "right. Fix the clause — this is not a reason to change "
                             "the parallelization strategy. A name declared inside the "
                             "loop body belongs in no clause at all; a name the loop "
                             "writes and later code reads needs reduction or "
                             "lastprivate, never private or firstprivate.",
                    "apply": "The diff did not apply — its context lines must match the "
                             "current file exactly (raw indentation, no line-number prefix).",
                    "compile": "The patched code does not compile. Fix the C/C++ error "
                             "without changing what the code computes.",
                    "openmp_compile": "A loop you want parallelized is not in OpenMP-canonical "
                             "form: it needs a simple `i < bound` condition and no "
                             "break/continue/return in the body.",
                    "tsan": "ThreadSanitizer found a REAL data race — the loop still carries a "
                            "cross-iteration dependence. Identify its cause (in-place coupling, "
                            "hidden reduction, storage reuse, or a true recurrence) and make the "
                            "iterations independent — do not merely rename storage.",
                    "correctness": "The program's output CHANGED — your restructuring is not "
                            "semantically equivalent. Diagnose WHICH kind of error this is "
                            "before rewriting:\n"
                            "(a) WRONG TRANSFORMATION — you assumed an independence the "
                            "code does not have, or reordered operations whose order affects "
                            "the result. Re-check that against the evidence and restructure "
                            "differently.\n"
                            "(b) RIGHT TRANSFORMATION, carried-over detail — the strategy is "
                            "sound but some bound, initial value, or boundary handling was "
                            "copied from the old schedule. Re-derive each such detail for the "
                            "new schedule instead of copying it: a loop bound or skipped "
                            "element that was safe because of the OLD update order is not "
                            "automatically safe under the new one. Keep the strategy and fix "
                            "only that.",
                    "performance": "The parallel build was correct but NOT faster than "
                            "sequential. The dependence is already gone; the parallel work is "
                            "just too fine-grained to cover thread startup.",
                }
                guidance = _STAGE_GUIDANCE.get(result.stage, "")
                refunded = ""
                if result.stage in ("apply", "compile", "openmp_compile") and build_retries > 0:
                    build_retries -= 1
                    budget += 1     # a build error must not cost a real attempt
                    refunded = f" (build fix — budget not charged, {build_retries} left)"
                print(f"│  [Tier-2] Stage '{result.stage}' failed{refunded}: "
                      f"{result.diagnostic[:200].replace(chr(10), ' ')}")
                # Keep enough of the diagnostic that the correctness expected-vs-got
                # comparison survives (it can run ~1.3 KB).
                diag_full = (result.diagnostic or "(no diagnostic)")[:1400]
                failure_reason = (
                    f"Validation failed at stage '{result.stage}'. {guidance}\n\n"
                    f"Diagnostic:\n{diag_full}"
                )
                # Build failures need the same approach with the error fixed;
                # semantic failures need an explicit decision about whether the
                # STRATEGY or a DETAIL was wrong (a blanket "switch strategy"
                # pushes the model off correct-but-buggy transformations).
                if result.stage in ("apply", "compile", "openmp_compile"):
                    retry_instr = (
                        "Keep your transformation approach and fix ONLY the reported "
                        "error — do not change strategy over a build problem."
                    )
                else:
                    retry_instr = (
                        "Do not resubmit a variation of the same code. Say in one line "
                        "which of (a) or (b) this was and what you are changing because "
                        "of it — then make sure the code you write actually differs in "
                        "that way. Stating the right bound and then writing the old one "
                        "is the most common way this retry fails."
                    )
                if tier2_messages is not None:
                    tier2_messages = tier2_messages + [{
                        "role": "user",
                        "content": (
                            f"Your diff failed at the '{result.stage}' stage. {guidance}\n\n"
                            f"Diagnostic:\n{diag_full}\n\n"
                            f"{retry_instr}"
                        ),
                    }]
        else:
            print(f"└─ SKIPPED (budget exhausted)\n")
            skipped.append((rid, depth))

        # Clean up the per-candidate profile snapshot (commit or skip — either way
        # we no longer need it).
        if dp_snapshot is not None and dp_snapshot.exists():
            shutil.rmtree(dp_snapshot, ignore_errors=True)

    # ── Phase B: annotate ────────────────────────────────────────────────────
    # Everything above only restructured code.  Now, once, from the profile the
    # last kept rewrite produced, apply every pragma that survives validation.
    if profile_is_fast and not profile_stale and not args.dry_run:
        print(f"\n  One full re-profile before Phase B — it annotates from measured "
              f"dependences, not carried-forward ones.")
        if not _reprofil(args.source_file, dp_dir, args.reprofil_args or None):
            print(f"  [warn] that re-profile failed; Phase B will be skipped.")
            profile_stale = True

    if profile_stale:
        print(f"\n{'='*60}")
        print(f"  PHASE B — skipped (no profile describes the current source)")
        print(f"{'='*60}\n")
        annotated: List[Dict[str, Any]] = []
    else:
        annotated = _phase_b(
            args, dp_dir, output_dir, reference_output, reference_outputs,
            binary_args, reference_time, gate_cache, change_log,
        )
    accepted.extend(annotated)

    # ── Settle: drop orphans, rebuild, verify the result, repair ─────────────
    # This is the only check against the program the user actually started with,
    # and the only one that looks at the file as it finally exists rather than
    # at a candidate patch on a temp copy.
    if not args.dry_run and change_log:
        print(f"{'='*60}")
        print(f"  SETTLING — verify the finished source, drop what does not hold up")
        print(f"{'='*60}")
        survivors, notes = _settle(
            original_text, change_log, args, output_dir, reference_output,
            reference_outputs, binary_args, reference_time,
        )
        if notes:
            print(f"  Dropped {len(notes)} change(s):")
            for n in notes:
                print(f"    · {n}")
        print()

        # accepted.json must describe the file on disk, not everything that was
        # ever provisionally accepted.
        kept_pragma_ids = {c["region_id"] for c in survivors if c["kind"] == "pragma"}
        kept_rewrite_ids = {c["region_id"] for c in survivors if c["kind"] == "rewrite"}
        accepted = [
            r for r in accepted
            if (r.get("phase") == "B" and r["region_id"] in kept_pragma_ids)
            or (r.get("tier") == 2 and r["region_id"] in kept_rewrite_ids)
        ]
        f = output_dir / "accepted.json"
        f.write_text(json.dumps(accepted, indent=2))

    # ── Summary ──────────────────────────────────────────────────────────────
    # De-duplicate skipped IDs and drop any that were ultimately accepted in
    # some version (e.g. a loop skipped at depth 0 but accepted at depth 1 after
    # an enclosing region's restructuring made it parallelisable).  Keep the
    # lowest depth at which each remaining ID was skipped.
    accepted_ids = {r["region_id"] for r in accepted}
    skipped_by_id: dict = {}
    for rid, d in skipped:
        if rid in accepted_ids:
            continue
        if rid not in skipped_by_id or d < skipped_by_id[rid]:
            skipped_by_id[rid] = d

    # The metric is pragmas that survive in the finished file, whoever wrote
    # them: Phase B's, plus the ones an --llm-pragmas rewrite carries itself.
    n_dp_pragmas = len([r for r in accepted if r.get("phase") == "B"])
    n_llm_pragmas = sum(r.get("pragmas", 0) for r in accepted if r.get("tier") == 2)
    n_pragmas = n_dp_pragmas + n_llm_pragmas
    n_rewrites = len([r for r in accepted if r.get("tier") == 2])
    print(f"\n{'='*60}")
    breakdown = (f" ({n_dp_pragmas} DiscoPoP + {n_llm_pragmas} LLM)"
                 if n_llm_pragmas else "")
    print(f"  SUMMARY: {n_rewrites} rewrite(s) kept  |  {n_pragmas} pragma(s) applied"
          f"{breakdown}  |  {len(skipped_by_id)} skipped")
    verdict = ("BEAT" if n_pragmas > baseline_pragmas
               else "MATCHED" if n_pragmas == baseline_pragmas else "BELOW")
    print(f"  DiscoPoP unaided: {baseline_pragmas} usable pragma(s)  →  this run: "
          f"{n_pragmas}   [{verdict}]")
    for r in accepted:
        d = r.get("discovery_depth", 0)
        # Phase-B records carry "phase", Phase-A ones carry "tier".
        kind = "Phase-B pragma" if r.get("phase") == "B" else f"Tier-{r.get('tier', '?')}"
        extra = ""
        if r.get("marginal_speedup") is not None:
            extra = f"  marginal {r['marginal_speedup']:.2f}×"
        elif r.get("self_annotated"):
            extra = f"  {r.get('pragmas', 0)} own pragma(s)"
            if r.get("exposed_speedup") is not None:
                extra += f", {r['exposed_speedup']:.2f}×"
        print(f"    ✓  {r.get('region_type', '?')} {r['region_id']}  "
              f"[{kind}]  depth={d}{extra}")
    for rid, d in skipped_by_id.items():
        print(f"    ✗  {rid}  [skipped]  depth={d}")
    print(f"\n  Results → {output_dir}/accepted.json")
    print(f"{'='*60}\n")
