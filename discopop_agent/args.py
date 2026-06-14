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
    lambda_penalty: float
    min_speedup: float
    output_dir: str
    dry_run: bool
    mock_llm: bool              # bypass real API; use pre-computed diffs for testing
    manual_llm: bool            # print prompt to stdout, read diff from stdin
    distance: int               # number of additional discovery passes (0 = original regions only)
    reprofil_args: list         # extra arguments forwarded to ./a.out during re-profiling


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
    p.add_argument("--lambda-penalty", type=float, default=1.0,
                   help="Score penalty λ for invoking LLM tier (default: 1.0)")
    p.add_argument("--min-speedup", type=float, default=1.0,
                   help="Minimum estimated speedup to process a region (default: 1.0)")
    p.add_argument("--output-dir", default=None,
                   help="Where to write patches (default: <discopop-dir>/agent_patches)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show plan without calling the LLM or modifying files")
    p.add_argument("--mock-llm", action="store_true",
                   help="Use pre-computed diffs instead of a live LLM call (for testing)")
    p.add_argument("--manual-llm", action="store_true",
                   help="Print the LLM prompt to stdout and read the diff from stdin")
    p.add_argument("--distance", type=int, default=0,
                   help=(
                       "Number of additional discovery passes after the initial run (default: 0). "
                       "Pass 0 processes only the original candidates from the initial profile. "
                       "Each subsequent pass re-profiles the (now-modified) source and processes "
                       "any newly discovered candidates. --distance 2 means: initial pass + 2 "
                       "discovery passes."
                   ))
    p.add_argument("--reprofil-args", nargs=argparse.REMAINDER, default=[],
                   help="Arguments forwarded to ./a.out during re-profiling (e.g. -- sort input.txt)")
    a = p.parse_args()

    # Resolve API key: CLI arg > LLM_API_KEY env var
    api_key = a.api_key or os.environ.get("LLM_API_KEY")

    return AgentArguments(
        discopop_dir=a.discopop_dir,
        source_file=a.source_file,
        budget=a.budget,
        model=a.model,
        api_key=api_key,
        lambda_penalty=a.lambda_penalty,
        min_speedup=a.min_speedup,
        output_dir=a.output_dir or f"{a.discopop_dir}/agent_patches",
        dry_run=a.dry_run,
        mock_llm=a.mock_llm,
        manual_llm=a.manual_llm,
        distance=a.distance,
        reprofil_args=a.reprofil_args,
    )
