from __future__ import annotations
import argparse
import os
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
    edit_mode: str              # "diff" | "function" — how the LLM returns edits
    restructure_depth: int      # max discovery depth at which Tier-2 (LLM) is applied
    require_speedup: bool       # gate pragma patches on measured wall-clock speedup
    min_measured_speedup: float # minimum measured parallel speedup to accept
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
    p.add_argument("--model", default="claude-opus-4-8",
                   help="LLM model ID (default: claude-opus-4-8)")
    p.add_argument("--api-key", default=None,
                   help="LLM API key — falls back to LLM_API_KEY env var")
    p.add_argument("--provider", choices=["anthropic", "openai-compat", "claude-agent-sdk"],
                   default="anthropic",
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
    p.add_argument("--min-workload", type=float, default=1.0,
                   help=("Minimum region workload (profiled instruction-count proxy) to "
                         "consider a region a candidate (default: 1.0). This is a cheap "
                         "static pre-filter, NOT a measured speedup — use 0 to include "
                         "function regions whose workload is reported as 0."))
    p.add_argument("--output-dir", default=None,
                   help="Where to write patches (default: <discopop-dir>/agent_patches)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show plan without calling the LLM or modifying files")
    p.add_argument("--edit-mode", choices=["diff", "function"], default="diff",
                   help="How the LLM returns a Tier-2 edit: 'diff' (unified diff, default) "
                        "or 'function' (the complete rewritten enclosing function, which the "
                        "agent splices in by line range — avoids diff-apply failures)")
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
    p.add_argument("--require-speedup", action="store_true",
                   help=(
                       "Only accept a parallelization (a patch that adds a "
                       "#pragma omp) if the parallel build measurably runs faster "
                       "than the sequential build of the same source. Note: tiny "
                       "workloads may not show speedup due to thread overhead."
                   ))
    # 1.1 rather than 1.0: whole-program wall-time ratios carry a few percent of
    # noise even with interleaved measurement, so near-parity must not pass.
    p.add_argument("--min-measured-speedup", type=float, default=1.1,
                   help=("Minimum measured wall-clock speedup (parallel vs sequential) "
                         "required when --require-speedup is set (default: 1.1)"))
    p.add_argument("--reprofil-args", nargs=argparse.REMAINDER, default=[],
                   help="Arguments forwarded to ./a.out during re-profiling (e.g. -- sort input.txt)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Visualize the whole process in the terminal: the exact prompt "
                        "sent to the LLM, its raw response, the extracted edit, and each "
                        "quality-gate stage (apply/compile/TSan/correctness/speedup).")
    a = p.parse_args()

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
        restructure_depth=a.restructure_depth,
        require_speedup=a.require_speedup,
        min_measured_speedup=a.min_measured_speedup,
        reprofil_args=a.reprofil_args,
        verbose=a.verbose,
    )
