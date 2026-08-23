from __future__ import annotations
import argparse
import os
import shlex
from dataclasses import dataclass
from typing import Optional


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
    fast_refresh: bool          # skip the instrumented run; translate dependences instead
    llm_deps: bool              # let the LLM judge static deps in code it just wrote
    hotspots: bool              # measure per-region runtime and rank by time saved
    min_impact: float           # skip regions predicted to save less than this (seconds)
    restructure_depth: int      # max discovery depth at which Tier-2 (LLM) is applied
    require_speedup: bool       # gate pragma patches on measured wall-clock speedup
    build_retries: int          # apply/compile retries that do not consume budget
    apply_patches: bool         # write accepted Tier-1 pragmas into the source file
    min_measured_speedup: float # minimum measured parallel speedup to accept
    check_inputs: list          # extra argv sets the rewrite must also reproduce
    reprofil_args: list         # extra arguments forwarded to ./a.out during re-profiling
    verbose: bool               # render the full LLM I/O and gate stages in the terminal


def parse_args() -> AgentArguments:
    p = argparse.ArgumentParser(
        description="DiscoPoP Agentic Controller — LLM-driven parallelization"
    )
    p.add_argument("--discopop-dir", required=True,
                   help="Path to the .discopop directory produced by DiscoPoP")
    p.add_argument("--source-file", required=True,
                   help="Path to the C/C++ source file that was profiled")
    p.add_argument("--budget", type=int, default=3,
                   help="Max LLM retry attempts per region (default: 3)")
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
                   help="How the LLM returns a Tier-2 edit: 'diff' (unified diff, default), "
                        "'function' (the complete rewritten enclosing function, which the "
                        "agent splices in by line range — avoids diff-apply failures), or "
                        "'direct' (the model edits a private copy of the file itself with "
                        "its Read/Edit/Write tools; the agent diffs that copy against the "
                        "real source and gates it as usual — requires "
                        "--provider claude-agent-sdk)")
    p.add_argument("--llm-pragmas", action=argparse.BooleanOptionalAction, default=True,
                   help=("Let the LLM write the OpenMP pragmas itself, in the same "
                         "edit as the restructuring, instead of leaving them to "
                         "DiscoPoP (default: off). The rewrite is then judged on its "
                         "own merits — static clause check, ThreadSanitizer, "
                         "byte-identical output from the PARALLEL build, and measured "
                         "speedup — rather than on whether re-profiling makes DiscoPoP "
                         "find a pattern. A rewrite that carries no pragma still falls "
                         "back to DiscoPoP's verdict, and Phase B still annotates every "
                         "region the LLM did not touch."))
    p.add_argument("--fast-refresh", action=argparse.BooleanOptionalAction, default=True,
                   help=("After a kept rewrite, refresh the profile WITHOUT re-running "
                         "the instrumented program (default: off). Only `discopop_cxx` "
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
                         "off). Static analysis is over-approximate, so a newly written "
                         "loop is usually blocked by a dependence that does not really "
                         "occur — and there is no dynamic data for new code to settle it. "
                         "Every judgement is written to <output-dir>/llm_deps.json, and a "
                         "pragma resting on one still has to pass ThreadSanitizer, the "
                         "byte-identical output check and the speedup gate."))
    p.add_argument("--hotspots", action=argparse.BooleanOptionalAction, default=True,
                   help=("Measure how long each region actually takes, with DiscoPoP's "
                         "own hotspot detection, and rank candidates by the time "
                         "parallelizing them would SAVE rather than by an instruction "
                         "count (default: on). Costs one extra instrumented run of the "
                         "program, once. Without it the old workload proxy is used, which "
                         "ranked example4's sortedness check above the sort it verifies "
                         "and array_accumulator's serial inner recurrence above the outer "
                         "Do-All holding 99.7% of the runtime."))
    p.add_argument("--min-impact", type=float, default=0.0,
                   help=("Skip any region predicted to save less than this many SECONDS "
                         "(default: 0.0 — off). Unlike --min-workload this is a real "
                         "unit: it is Amdahl's law applied to the region's measured share "
                         "of runtime at this machine's thread count, so 0.05 means "
                         "'do not spend an LLM attempt on anything that cannot save 50 ms'. "
                         "Needs --hotspots; regions with no measurement fall back to "
                         "--min-workload."))
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
        a.llm_deps = a.fast_refresh

    # Direct editing needs a backend with file tools; the HTTP providers only
    # return text.
    if a.edit_mode == "direct" and not sdk:
        p.error("--edit-mode direct requires --provider claude-agent-sdk "
                f"(got '{a.provider}') — it is the only backend that can edit files itself")

    # Only complain when it was ASKED for: with --no-fast-refresh it simply
    # follows along and switches itself off.
    if a.llm_deps and not a.fast_refresh:
        if explicit_llm_deps:
            p.error("--llm-deps only applies with --fast-refresh: without it every "
                    "region has freshly measured dependences and there is no gap to fill")
        a.llm_deps = False

    # Resolve API key: CLI arg > LLM_API_KEY env var
    api_key = a.api_key or os.environ.get("LLM_API_KEY")
    # Resolve openai-compat base URL: CLI arg > LLM_API_BASE env var
    api_base = a.api_base or os.environ.get("LLM_API_BASE")

    return AgentArguments(
        discopop_dir=a.discopop_dir,
        source_file=a.source_file,
        budget=a.budget,
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
        fast_refresh=a.fast_refresh,
        llm_deps=a.llm_deps,
        hotspots=a.hotspots,
        min_impact=a.min_impact,
        restructure_depth=a.restructure_depth,
        require_speedup=a.require_speedup,
        build_retries=a.build_retries,
        apply_patches=a.apply_patches,
        min_measured_speedup=a.min_measured_speedup,
        check_inputs=[shlex.split(x) for x in a.check_input],
        reprofil_args=a.reprofil_args,
        verbose=a.verbose,
    )
