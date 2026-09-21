from __future__ import annotations
import argparse
import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

from .project import Project


@dataclass
class AgentArguments:
    discopop_dir: str
    source_file: str
    budget: int
    model: str
    api_key: Optional[str]      # LLM_API_KEY — provider-agnostic
    provider: str               # "anthropic" | "openai-compat"
    api_base: Optional[str]     # base URL for openai-compat (e.g. vLLM endpoint)
    lambda_penalty: float
    min_workload: float
    output_dir: str
    dry_run: bool
    edit_mode: str              # "diff" | "function" | "direct" — how the LLM returns edits
    llm_pragmas: bool           # LLM writes the OpenMP pragmas itself alongside the rewrite
    pragma_arbitration: bool    # Fix 85: on a collision, keep whichever pragma measures faster
    fast_refresh: bool          # skip the instrumented run; translate dependences instead
    llm_deps: bool              # let the LLM judge static deps in code it just wrote
    hotspots: bool              # measure per-region runtime and rank by time saved
    min_impact: float           # skip regions predicted to save less than this (seconds)
    restructure_depth: int      # max discovery depth at which Tier-2 (LLM) is applied
    require_speedup: bool       # gate pragma patches on measured wall-clock speedup
    build_retries: int          # apply/compile retries that do not consume budget
    apply_patches: bool         # write accepted Tier-1 pragmas into the source file
    min_measured_speedup: float # minimum measured parallel speedup to accept
    check_inputs: List[List[str]]          # extra argv sets the rewrite must also reproduce
    reprofil_args: List[str]         # extra arguments forwarded to ./a.out during re-profiling
    verbose: bool               # render the full LLM I/O and gate stages in the terminal
    # Correctness-gate calibration.  Defaults keep the gate strict on programs
    # that do not need slack: an integer-only program measures a floor of 0 and
    # is compared byte-for-byte exactly as before.
    # Proceed with no reference output at all (correctness gate OFF). Defaulted
    # so it stays opt-in and existing constructors keep working.
    allow_unverified: bool = False
    # --llm-recon: the model reports the dependences for code it just
    # wrote, in the same call as the rewrite.  Adds dependences; the
    # opposite direction to llm_deps, which removes them.
    llm_recon: bool = False
    # 'followup' = a separate turn after the gate; 'folded' = appended
    # to the rewrite prompt.  See --llm-recon-mode.
    llm_recon_mode: str = "followup"
    # Ablation control (--evidence): which evidence sections render.
    # None means all of them, which is the default behaviour.
    evidence_sections: Optional[Set[str]] = None
    numeric_tolerance: bool = True   # measure the program's numerical noise floor
    schedule_stress: bool = True     # vary threads/schedule instead of one run
    stress_threads: Tuple[int, ...] = (1, 2, 4)  # thread counts the matrix covers
    # Computed at startup by run.py, not parsed: how far this program's own
    # numbers move under legal build variation.  0.0 means byte-exact.
    noise_floor: float = 0.0
    # --min-runtime-share: skip regions below this fraction of the measured runtime
    # (and, when hotspots were measured, regions the detector did not report).
    min_runtime_share: float = 0.0
    # --exclude-functions: functions (and every region inside them) never ranked —
    # e.g. a benchmark harness's output and setup code.
    exclude_functions: Tuple[str, ...] = ()
    # --timing-cflags: extra compile flags for the builds the speed check TIMES
    # (never for profiling or any correctness check), e.g. a larger dataset.
    timing_cflags: Tuple[str, ...] = ()
    # --budget-policy: "fixed" gives every region --budget attempts; "share" scales a
    # region's attempts with its measured runtime share, between --budget-min and
    # --budget (plan.scoring.region_budget). Decision D3: "share" becomes the default
    # once a calibration run has fixed its values.
    budget_policy: str = "fixed"
    budget_min: int = 1
    # --project-dir: the program is several files (project.py).  None — the default —
    # is the single-file program every earlier run used, handled exactly as before.
    # In a project `source_file` is the file CURRENTLY under work: the phases point
    # it at each region's own file in turn.
    project: Optional[Project] = None
    profile_only: bool = False


def parse_args() -> AgentArguments:
    p = argparse.ArgumentParser(
        description="DiscoPoP Agentic Controller — LLM-driven parallelization"
    )
    p.add_argument("--discopop-dir", required=True,
                   help="Path to the .discopop directory produced by DiscoPoP")
    p.add_argument("--source-file", default=None,
                   help=("Path to the C/C++ source file that was profiled. Required for a "
                         "single-file program; with --project-dir it is optional."))
    p.add_argument("--project-dir", default=None,
                   help=("Root of a MULTI-FILE program. The agent then profiles the whole "
                         "program (through a generated unity translation unit, so DiscoPoP "
                         "sees every function's loops — see docs/MULTIFILE.md), builds the "
                         "real multi-file program for every check, and edits each region in "
                         "the file it lives in. --discopop-dir must be <project-dir>/.discopop."))
    p.add_argument("--project-units", default="",
                   help=("Comma-separated translation units, relative to --project-dir, in "
                         "build order (default: every .c/.cpp/.cc/.cxx under it, sorted)."))
    p.add_argument("--project-include", default=None,
                   help=("Comma-separated include directories relative to --project-dir "
                         "(default: every directory under it that holds a header)."))
    p.add_argument("--project-cflags", default="",
                   help="Extra compile flags for every build of the project, e.g. '-DCLASS_S'.")
    p.add_argument("--project-ldflags", default="",
                   help="Extra link flags for every build of the project.")
    p.add_argument("--build-cmd", default="",
                   help=("The project's own build command, run in a staged copy of the tree, "
                         "for programs a plain compile of the units cannot build. The gate's "
                         "flags arrive as CC/CXX/CFLAGS/CXXFLAGS/LDFLAGS and as {cc} {cxx} "
                         "{flags} {out}; the result must land at {out} or --project-binary."))
    p.add_argument("--profile-only", action="store_true",
                   help=("Take the initial DiscoPoP profile and stop — for a project, through "
                         "the unity unit. Lets a harness profile a program once and reuse "
                         "that profile across runs, exactly as it does for one file."))
    p.add_argument("--project-binary", default="a.out",
                   help="What --build-cmd produces, relative to the project root (default: a.out).")
    p.add_argument("--budget", type=int, default=3,
                   help="Max LLM retry attempts per region (default: 3)")
    p.add_argument("--budget-policy", choices=["fixed", "share"], default="fixed",
                   help=("How many attempts each region gets. 'fixed' (default): --budget for "
                         "every region. 'share': scaled with the region's measured runtime share "
                         "relative to the largest in the queue, from --budget-min up to --budget; "
                         "regions without a measurement get --budget-min."))
    p.add_argument("--budget-min", type=int, default=1,
                   help="Fewest attempts a region gets under --budget-policy share (default: 1)")
    p.add_argument("--model", default=None,
                   help=("LLM model ID. The default follows --provider, because the two "
                         "name models differently: 'haiku' for claude-agent-sdk (Claude "
                         "Code's own aliases), 'claude-opus-5' otherwise (a full API "
                         "model ID). Passing a Claude Code alias to the anthropic "
                         "provider is a 404 at the first call, which is why this is not "
                         "one fixed string."))
    p.add_argument("--api-key", default=None,
                   help="LLM API key — falls back to LLM_API_KEY env var")
    p.add_argument("--provider", choices=["anthropic", "openai-compat", "claude-agent-sdk"],
                   default="claude-agent-sdk",
                   help="LLM backend: 'anthropic' (default, billed API key), "
                        "'openai-compat' (any OpenAI-compatible endpoint, e.g. a "
                        "self-hosted vLLM server), or 'claude-agent-sdk' (runs the "
                        "local `claude` CLI headlessly, billed against your Claude "
                        "Code subscription instead of a per-token API key — no "
                        "--api-key needed, just `claude login` once)")
    p.add_argument("--api-base", default=None,
                   help="Base URL for --provider openai-compat (e.g. "
                        "http://localhost:18000/v1) — falls back to LLM_API_BASE env var")
    p.add_argument("--lambda-penalty", type=float, default=1.0,
                   help="Score penalty λ for invoking LLM tier (default: 1.0)")
    p.add_argument("--min-workload", type=float, default=0.0,
                   help=("Minimum region workload (profiled instruction-count proxy) to "
                         "consider a region a candidate (default: 0.0). This is a cheap "
                         "static pre-filter, NOT a measured speedup. It defaults to 0 so "
                         "FUNCTION regions are included: Data.xml reports their workload "
                         "as 0 (only CU nodes carry instructionsCount), so any positive "
                         "threshold silently excludes every function in the program."))
    p.add_argument("--output-dir", default=None,
                   help="Where to write patches (default: <discopop-dir>/agent_patches)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show plan without calling the LLM or modifying files")
    p.add_argument("--edit-mode", choices=["diff", "function", "direct"], default=None,
                   help="How the LLM returns a Tier-2 edit (default: computed from "
                        "--provider — 'direct' for claude-agent-sdk, 'diff' otherwise). "
                        "'diff' (unified diff), "
                        "'function' (the complete rewritten enclosing function, which the "
                        "agent splices in by line range — avoids diff-apply failures), or "
                        "'direct' (the model edits a private copy of the file itself with "
                        "its Read/Edit/Write tools; the agent diffs that copy against the "
                        "real source and gates it as usual — requires "
                        "--provider claude-agent-sdk)")
    p.add_argument("--llm-pragmas", action=argparse.BooleanOptionalAction, default=False,
                   help=("Let the LLM write the OpenMP pragmas itself, in the same edit as "
                         "the restructuring, instead of leaving them to DiscoPoP "
                         "(default: OFF since 2026-09-20). Off, the division of labour is "
                         "the one the pipeline was designed around and the one the thesis "
                         "argues for: the model restructures, DiscoPoP re-discovers what "
                         "the rewrite exposed, and Phase B annotates once at the end — so "
                         "a rewrite is kept only if the ANALYSIS finds parallelism in it, "
                         "never on the model's say-so. On, the rewrite is judged on its own "
                         "merits instead (clause check, ThreadSanitizer, identical output "
                         "from the PARALLEL build, measured speedup), which is a sound but "
                         "different question — turn it on for the experiment that asks it "
                         "(E3), not by default. It was the default until 20 Sep 2026; E10 "
                         "showed the cost (jacobi-2d: the model annotated loops DiscoPoP "
                         "had already claimed, and its clauses were 2.4x slower), which "
                         "Fix 85 now bounds but does not make into a reason to keep it on."))
    p.add_argument("--print-config", action="store_true",
                   help=("Print the fully resolved configuration as JSON and exit, without "
                         "reading a profile or calling anything. The experiment harness uses "
                         "it to check that every argument an experiment's arm DECLARES is "
                         "what the agent actually parsed, so a changed default can never "
                         "silently change what an arm means."))
    p.add_argument("--pragma-arbitration", action=argparse.BooleanOptionalAction, default=True,
                   help=("With --llm-pragmas and --require-speedup: where the model has "
                         "annotated a loop DiscoPoP had already claimed, build DiscoPoP's "
                         "pragma as an alternative, gate it, time the two against each other "
                         "and keep the faster (default: on, Fix 85). The model reaches such a "
                         "loop through an ENCLOSING region even though the loop itself was "
                         "deferred to Phase B; without this, Phase B finds it annotated, "
                         "reports no applicable pattern, and DiscoPoP's pragma is never "
                         "measured. Turn it off to study the two authorships in isolation "
                         "(E3), not to save time: it costs one gate run and one timing pair "
                         "per collision, and only where a collision exists."))
    p.add_argument("--fast-refresh", action=argparse.BooleanOptionalAction, default=False,
                   help=("After a kept rewrite, refresh the profile WITHOUT re-running "
                         "the instrumented program (default: OFF since 2026-09-21). Off, "
                         "a kept rewrite is followed by a FULL re-profile: instrument, run, "
                         "explore — so every later decision rests on dependences DiscoPoP "
                         "actually observed in the rewritten code, which is what the thesis "
                         "argues for. On, it is an optimisation that trades accuracy for "
                         "time, and E3 is where that trade is measured; turn it on for that "
                         "experiment, not by default. Note --llm-recon only takes effect "
                         "with this on, since reconstruction exists to repair what the fast "
                         "refresh could not translate. Only `discopop_cxx` "
                         "runs — about a second — and the previous run's observed "
                         "dependences are translated onto the new instruction numbering; "
                         "anything that cannot be translated with certainty is dropped, "
                         "leaving the rewritten region covered by static (over-approximate) "
                         "dependences. The instrumented run is what scales with the "
                         "workload (17x native on a 104M-op kernel here), so this is worth "
                         "most on exactly the programs that cost most to profile. A FULL "
                         "re-profile still happens before restructuring at a deeper level "
                         "and once before Phase B, so no decision rests on carried-forward "
                         "data for long."))
    p.add_argument("--llm-deps", action=argparse.BooleanOptionalAction, default=None,
                   help=("With --fast-refresh: ask the LLM to judge the STATIC dependences "
                         "DiscoPoP reports for code the LLM itself just wrote (default: "
                         "OFF). Kept for comparison experiments, not recommended: it is the "
                         "only place a model's claim EDITS DiscoPoP's analysis instead of "
                         "being tested against the program, and --llm-pragmas is the sound "
                         "channel for the same judgement (the model writes the pragma; the "
                         "gate has to be convinced). It also rarely pays for itself — a "
                         "fast refresh saves only the instrumented run (8.6 s and 7.9 s on "
                         "the two benchmark cases), and one LLM call usually costs more. "
                         "It only DELETES over-cautious static dependences; it never adds "
                         "one, and observed (dynamic) dependences are filtered out before "
                         "the model sees them. Static analysis is over-approximate, so a newly written "
                         "loop is usually blocked by a dependence that does not really "
                         "occur — and there is no dynamic data for new code to settle it. "
                         "Every judgement is written to <output-dir>/llm_deps.json, and a "
                         "pragma resting on one still has to pass ThreadSanitizer, the "
                         "byte-identical output check and the speedup gate."))
    p.add_argument("--llm-recon", action=argparse.BooleanOptionalAction, default=False,
                   help=("With --fast-refresh: have the LLM report the dependences "
                         "in the code it just wrote, IN THE SAME CALL as the "
                         "rewrite (default: off). A fast refresh cannot carry a "
                         "dependence whose endpoint is in new code — the previous "
                         "run predates it — and measured across two chains, 39 of "
                         "39 dependences a refresh lacks have an endpoint on a "
                         "rewritten line and NONE were carryable. That gap is the "
                         "one thing a model that just wrote the code can close. "
                         "It works the OPPOSITE way to --llm-deps: it ADDS "
                         "dependences (more conservative, closer to what a run "
                         "would have measured) rather than deleting them, and it "
                         "costs no extra call. The model speaks in source terms "
                         "only — loop line, type, variable, writer and reader "
                         "lines — and the agent resolves those to instruction ids "
                         "itself; a claim it cannot place is dropped, not guessed."))
    p.add_argument("--llm-recon-mode", choices=["followup", "folded"],
                   default="followup",
                   help=("How --llm-recon asks (default: followup). `followup` "
                         "asks in a SEPARATE turn after the rewrite has passed "
                         "the gate and the refresh has run — the rewrite is "
                         "written with the model's whole attention on it, the "
                         "instruction mapping the claims resolve against already "
                         "exists, and only KEPT rewrites cost a request. "
                         "`folded` appends the request to the rewrite prompt "
                         "instead: no extra request at all, but the model splits "
                         "its attention while writing, which may cost rewrite "
                         "quality. Which produces better dependences is an open "
                         "question — the two modes exist to be measured against "
                         "each other."))
    p.add_argument("--hotspots", action=argparse.BooleanOptionalAction, default=True,
                   help=("Measure how long each region actually takes, with DiscoPoP's "
                         "own hotspot detection, and rank candidates by the time "
                         "parallelizing them would SAVE rather than by an instruction "
                         "count (default: on). Costs one extra instrumented run of the "
                         "program, once. Without it the old workload proxy is used, which "
                         "ranked example4's sortedness check above the sort it verifies "
                         "and array_accumulator's serial inner recurrence above the outer "
                         "Do-All holding 99.7%% of the runtime."))
    p.add_argument("--min-impact", type=float, default=0.0,
                   help=("Skip any region predicted to save less than this many SECONDS "
                         "(default: 0.0 — off). Unlike --min-workload this is a real "
                         "unit: it is Amdahl's law applied to the region's measured share "
                         "of runtime at this machine's thread count, so 0.05 means "
                         "'do not spend an LLM attempt on anything that cannot save 50 ms'. "
                         "Needs --hotspots; regions with no measurement fall back to "
                         "--min-workload."))
    p.add_argument("--min-runtime-share", type=float, default=0.0,
                   help=("Skip any region whose measured share of the program's runtime is "
                         "below this fraction (default: 0.0 — off; 0.05 = regions under 5%%). "
                         "Unlike --min-impact (seconds) it does not depend on the problem "
                         "size the program was profiled at. When hotspots were measured, a "
                         "region the detector did not report is skipped too, instead of "
                         "competing for model calls on the static proxy. Needs --hotspots."))
    p.add_argument("--exclude-functions", default="",
                   help=("Comma-separated function names that are out of scope: the "
                         "functions and every region inside them are never ranked or "
                         "attempted (default: none). Meant for code that is not the "
                         "computation under study — a benchmark harness's output, timing "
                         "and setup routines — so it cannot win model calls."))
    p.add_argument("--restructure-depth", type=int, default=0,
                   help=(
                       "Maximum discovery depth at which Tier-2 LLM restructuring is "
                       "applied (default: 0). "
                       "Depth 0 = only the initial DiscoPoP candidates may be restructured. "
                       "After each accepted Tier-2 patch the source is re-profiled; newly "
                       "exposed candidates are assigned depth+1. "
                       "Candidates at depth > restructure-depth are processed with Tier-1 "
                       "only — no LLM call, no further code restructuring. "
                       "This bounds the restructuring chain and prevents the source from "
                       "drifting arbitrarily far from the original."
                   ))
    p.add_argument("--require-speedup", action=argparse.BooleanOptionalAction, default=True,
                   help=(
                       "Only accept a parallelization (a patch that adds a "
                       "#pragma omp) if the parallel build measurably runs faster "
                       "than the sequential build of the same source (default: on). "
                       "Pass --no-require-speedup to accept correct-but-not-faster "
                       "parallelizations, e.g. when profiling a workload too small "
                       "to amortise thread overhead."
                   ))
    p.add_argument("--apply-patches", action=argparse.BooleanOptionalAction, default=True,
                   help=("Write accepted Tier-1 pragmas into the source file (default: on; "
                         "the original is backed up to <output-dir>/<name>.original). "
                         "Tier-2 rewrites are always written — they are what gets "
                         "re-profiled. With --no-apply-patches an accepted Tier-1 pattern "
                         "is only recorded in accepted.json and its patch left in "
                         "patch_generator/, so the source is never modified for Tier-1."))
    p.add_argument("--evidence", default="full",
                   help=("Which parts of DiscoPoP's evidence the LLM is shown "
                         "(default: full). An ABLATION control: the point of the "
                         "agent is that profiling data helps a model parallelize, "
                         "and that claim is testable by removing the data. "
                         "`full` = everything; `none` = source and task only, no "
                         "DiscoPoP data at all; a comma list SELECTS sections "
                         "(`deps,blockers`); a list of `-name` entries SUBTRACTS "
                         "from full — write that form with an equals sign, "
                         "`--evidence=-classification,-loop_nest`, since a "
                         "leading dash is otherwise read as a flag. Sections: "
                         "deps, reductions, classification, extra_vars, "
                         "array_note, loop_nest, calls, blockers, failure. "
                         "NOTE `failure` is the GATE's diagnostic, not DiscoPoP's "
                         "— leaving it in means a no-evidence run still gets "
                         "empirical feedback, so pair the ablation with "
                         "--budget 1 to isolate the two."))
    p.add_argument("--allow-unverified", action="store_true",
                   help=("Continue even when the ORIGINAL program cannot be built or "
                         "run, which leaves the correctness gate with nothing to compare "
                         "against and therefore switched off (default: off — the run "
                         "aborts instead). Without a reference, a rewrite's output is "
                         "never checked, so patches can be accepted that were never "
                         "shown to preserve semantics."))
    p.add_argument("--build-retries", type=int, default=2,
                   help=("Retries that do NOT consume budget when the LLM's rewrite "
                         "fails to apply or compile (default: 2). A build error is a "
                         "mechanical fix, not a failed parallelization idea; capped so "
                         "a model that cannot produce compiling code still terminates."))
    # 1.1 rather than 1.0: whole-program wall-time ratios carry a few percent of
    # noise even with interleaved measurement, so near-parity must not pass.
    p.add_argument("--min-measured-speedup", type=float, default=1.1,
                   help=("Minimum measured wall-clock speedup (parallel vs sequential) "
                         "required when --require-speedup is set (default: 1.1)"))
    p.add_argument("--timing-cflags", default="",
                   help=("Extra compiler flags for the builds the speed check TIMES — the "
                         "gate's performance stage, Phase B's noise floor and marginal "
                         "measurement, Settle's final timing, and the timed reference "
                         "(default: none). Profiling and every correctness check keep the "
                         "plain build. For programs whose size is fixed at compile time: "
                         "profile and check at a small size, measure speed where it is "
                         "measurable, e.g. --timing-cflags=-DLARGE_DATASET (write it with "
                         "'=', a leading dash is otherwise read as a flag). Only used with "
                         "--require-speedup."))
    p.add_argument("--check-input", action="append", default=[], metavar="ARGS",
                   help=("Extra program arguments the rewrite must ALSO reproduce, "
                         "repeatable (e.g. --check-input '0' --check-input '1' "
                         "--check-input '9999'). Correctness is otherwise judged on a "
                         "single input, so a rewrite that is right for the profiled "
                         "size and wrong at 0, 1 or an odd count would pass. Each value "
                         "is split like a shell command line; inputs the ORIGINAL "
                         "program cannot run are dropped with a warning."))
    p.add_argument("--reprofil-args", nargs=argparse.REMAINDER, default=[],
                   help="Arguments forwarded to ./a.out during re-profiling (e.g. -- sort input.txt)")
    p.add_argument("--numeric-tolerance", action=argparse.BooleanOptionalAction, default=True,
                   help=("Before judging anything, measure how far this program's own "
                         "numbers move under semantically neutral build variation — "
                         "vectorization, FMA contraction, optimization level — and allow "
                         "a rewrite's values to move that far (default: on). Programs "
                         "whose output holds no floating point measure a floor of zero "
                         "and stay byte-exact, so this changes nothing for them. It "
                         "exists because parallelizing a reduction reorders the "
                         "additions, which moves the last digits: LULESH's own reference "
                         "OpenMP disagrees with its serial build from the sixteenth "
                         "digit, and a byte-identical gate reverts it. Everything that "
                         "is not a number — labels, line structure, how many values are "
                         "printed — must still match exactly, and integers are never "
                         "given slack."))
    p.add_argument("--schedule-stress", action=argparse.BooleanOptionalAction, default=True,
                   help=("Run a pragma-bearing patch across several thread counts and "
                         "OpenMP schedules instead of once (default: on). A single run "
                         "samples a single interleaving, which is why an output diff "
                         "alone cannot catch a race. Output that moves between runs at "
                         "the SAME thread count is a race and fails at any magnitude; "
                         "output stable at fixed threads that moves across thread counts "
                         "is reordered arithmetic and is judged against the noise floor."))
    p.add_argument("--stress-threads", default="1,2,4",
                   help=("Thread counts the schedule matrix covers (default: 1,2,4). "
                         "Small on purpose — a race needs more than one thread, not many "
                         "— so the gate stays usable on a shared machine."))
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Visualize the whole process in the terminal: the exact prompt "
                        "sent to the LLM, its raw response, the extracted edit, and each "
                        "quality-gate stage (apply/compile/TSan/correctness/speedup).")
    a = p.parse_args()

    # Three defaults are coupled to another flag, so they are resolved here rather
    # than fixed in add_argument.  Each of them was a footgun as a fixed default:
    # changing only --provider would otherwise fail at the first LLM call with an
    # unrelated-looking error about the model or the edit mode.
    sdk = a.provider == "claude-agent-sdk"
    if a.model is None:
        if a.provider == "openai-compat":
            p.error("--model is required with --provider openai-compat: the name is "
                    "whatever your endpoint serves (e.g. a local Qwen build), and "
                    "guessing it would send a Claude model ID to your own server")
        a.model = "haiku" if sdk else "claude-opus-5"
    if a.edit_mode is None:
        a.edit_mode = "direct" if sdk else "diff"
    explicit_llm_deps = a.llm_deps is not None
    if a.llm_deps is None:
        # OFF by default (it used to follow --fast-refresh).  It is the one place
        # a model's claim edits DiscoPoP's own analysis rather than being tested
        # against the program, and the honest channel for the same judgement is
        # --llm-pragmas, where the model writes the pragma and the gate has to be
        # convinced by TSan, the schedule matrix and the clock.  It is also
        # unlikely to pay for itself: a fast refresh saves only the instrumented
        # run (measured 8.6 s on prefix_sum, 7.9 s on array_accumulator), and one
        # LLM call per kept rewrite typically costs more than that.
        a.llm_deps = False

    # Direct editing needs a backend with file tools; the HTTP providers only
    # return text.
    if a.edit_mode == "direct" and not sdk:
        p.error("--edit-mode direct requires --provider claude-agent-sdk "
                f"(got '{a.provider}') — it is the only backend that can edit files itself")

    # Only complain when it was ASKED for: with --no-fast-refresh it simply
    # follows along and switches itself off.
    if a.llm_recon and not a.fast_refresh:
        p.error("--llm-recon only applies with --fast-refresh: a full re-profile "
                "measures the new code, so there is no gap to reconstruct")
    if a.llm_recon and a.llm_deps:
        p.error("--llm-recon and --llm-deps pull in opposite directions — one adds "
                "dependences for new code, the other deletes ones it judges "
                "spurious — so running both lets the model argue with itself "
                "inside one profile. Choose one")

    if a.llm_deps and not a.fast_refresh:
        if explicit_llm_deps:
            p.error("--llm-deps only applies with --fast-refresh: without it every "
                    "region has freshly measured dependences and there is no gap to fill")
        a.llm_deps = False

    # --evidence: full | none | a,b,c (select) | -a,-b (subtract from full)
    from .llm.render import EVIDENCE_SECTIONS
    raw = (a.evidence or "full").strip()
    if raw == "full":
        evidence_sections = None
    elif raw == "none":
        evidence_sections = set()
    else:
        picks = [t.strip() for t in raw.split(",") if t.strip()]
        unknown = [t.lstrip("-") for t in picks if t.lstrip("-") not in EVIDENCE_SECTIONS]
        if unknown:
            p.error(f"--evidence: unknown section(s) {', '.join(unknown)}; "
                    f"choose from {', '.join(EVIDENCE_SECTIONS)}")
        if all(t.startswith("-") for t in picks):
            evidence_sections = set(EVIDENCE_SECTIONS) - {t[1:] for t in picks}
        elif any(t.startswith("-") for t in picks):
            p.error("--evidence: mixing selected and -subtracted sections is "
                    "ambiguous; use one form or the other")
        else:
            evidence_sections = set(picks)

    # Resolve API key: CLI arg > LLM_API_KEY env var
    api_key = a.api_key or os.environ.get("LLM_API_KEY")
    # Resolve openai-compat base URL: CLI arg > LLM_API_BASE env var
    api_base = a.api_base or os.environ.get("LLM_API_BASE")

    project: Optional[Project] = None
    if a.project_dir:
        project = Project.discover(
            a.project_dir,
            units=[u.strip() for u in a.project_units.split(",") if u.strip()] or None,
            include_dirs=([d.strip() for d in a.project_include.split(",") if d.strip()]
                          if a.project_include is not None else None),
            cflags=shlex.split(a.project_cflags), ldflags=shlex.split(a.project_ldflags),
            build_cmd=a.build_cmd, binary=a.project_binary)
        if not project.units:
            p.error(f"--project-dir {a.project_dir}: no C/C++ translation unit found")
        missing = [u for u in project.units if not (project.root / u).is_file()]
        if missing:
            p.error(f"--project-units: not found under the project root: {', '.join(missing)}")
        suffixes = {Path(u).suffix == ".c" for u in project.units}
        if len(suffixes) > 1 and not a.build_cmd:
            p.error("the project mixes C and C++ units; one compiler invocation cannot "
                    "build that — give the project's own build with --build-cmd")
        if Path(a.discopop_dir).resolve() != (project.root / ".discopop").resolve():
            p.error("--discopop-dir must be <project-dir>/.discopop: DiscoPoP writes its "
                    "profile into the directory the program is built in")
        if a.source_file and not project.contains(a.source_file):
            p.error(f"--source-file {a.source_file} is not inside --project-dir")
        if not a.source_file:
            a.source_file = str(project.root / project.units[0])
    elif not a.source_file:
        p.error("--source-file is required (or give --project-dir for a multi-file program)")
    elif a.build_cmd or a.project_units or a.project_include is not None:
        p.error("--build-cmd / --project-units / --project-include need --project-dir")

    args = AgentArguments(
        project=project,
        profile_only=a.profile_only,
        discopop_dir=a.discopop_dir,
        source_file=a.source_file,
        budget=a.budget,
        budget_policy=a.budget_policy,
        budget_min=a.budget_min,
        model=a.model,
        api_key=api_key,
        provider=a.provider,
        api_base=api_base,
        lambda_penalty=a.lambda_penalty,
        min_workload=a.min_workload,
        output_dir=a.output_dir or f"{a.discopop_dir}/agent_patches",
        dry_run=a.dry_run,
        edit_mode=a.edit_mode,
        llm_pragmas=a.llm_pragmas,
        pragma_arbitration=a.pragma_arbitration,
        fast_refresh=a.fast_refresh,
        llm_deps=a.llm_deps,
        hotspots=a.hotspots,
        min_impact=a.min_impact,
        min_runtime_share=a.min_runtime_share,
        exclude_functions=tuple(x.strip() for x in a.exclude_functions.split(",") if x.strip()),
        timing_cflags=tuple(shlex.split(a.timing_cflags)),
        restructure_depth=a.restructure_depth,
        require_speedup=a.require_speedup,
        build_retries=a.build_retries,
        allow_unverified=a.allow_unverified,
        llm_recon=a.llm_recon,
        llm_recon_mode=a.llm_recon_mode,
        evidence_sections=evidence_sections,
        apply_patches=a.apply_patches,
        min_measured_speedup=a.min_measured_speedup,
        check_inputs=[shlex.split(x) for x in a.check_input],
        reprofil_args=a.reprofil_args,
        verbose=a.verbose,
        numeric_tolerance=a.numeric_tolerance,
        schedule_stress=a.schedule_stress,
        stress_threads=tuple(
            int(x) for x in str(a.stress_threads).split(",") if x.strip()
        ) or (1, 2, 4),
    )

    if a.print_config:
        # What the agent ACTUALLY parsed, for the harness to check an experiment's arms
        # against what that experiment declared (every argument set on purpose, nothing
        # inherited by accident).  Printed as JSON and nothing else; the process then exits.
        import dataclasses
        import json as _json

        def _plain(v: Any) -> Any:
            if isinstance(v, (str, int, float, bool)) or v is None:
                return v
            if isinstance(v, (list, tuple)):
                return [_plain(x) for x in v]
            if dataclasses.is_dataclass(v) and not isinstance(v, type):
                return {k: _plain(x) for k, x in dataclasses.asdict(v).items()}
            return str(v)

        # A credential must never reach a log, a run manifest or a terminal, and this
        # output is written to all three.
        secret = {"api_key", "api_base"}
        print(_json.dumps({f.name: ("<set>" if getattr(args, f.name) else None)
                           if f.name in secret else _plain(getattr(args, f.name))
                           for f in dataclasses.fields(args)}, indent=2, sort_keys=True))
        raise SystemExit(0)
    return args
