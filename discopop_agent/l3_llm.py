"""
L3 LLM Code Modification Engine
---------------------------------
Sends an EvidencePackage to Claude and expects a valid unified diff back.

The target is any code region (loop, function body, CU) — not just loops.
The LLM restructures the source so that DiscoPoP can detect parallelism;
it does NOT add OpenMP pragmas itself.

Prompt caching is applied to the stable system prompt.
On a bad-format response a free format re-prompt fires before consuming
a budget slot.
"""
from __future__ import annotations

import textwrap
from typing import Optional

import anthropic

from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

_SYSTEM = textwrap.dedent("""\
    You are an expert in parallel programming and OpenMP for C/C++.

    Your task: given a C/C++ code region with its runtime data-dependence
    profile, restructure the source so that an automated profiler (DiscoPoP)
    can detect and apply OpenMP parallelization patterns to it.

    The region can be any hotspot: a loop, a function body, a block of
    statements, or any other sequential section identified as compute-heavy.

    DiscoPoP recognises three main patterns after re-profiling:
      1. Do-All       — no loop-carried or cross-iteration data dependences
      2. Reduction    — only reduction-type dependences (e.g. sum +=, max =)
      3. Pipeline     — producer→consumer stages with no cross-iteration deps
      4. Task parallel — independent task regions with explicit data flow

    Your responsibilities:
      - Preserve exact program semantics (identical observable results)
      - Target the specific blocking dependences shown in the profile
      - Use standard techniques as appropriate:
            loop fission, scalar temporaries, temporary arrays,
            reduction-variable privatization, loop interchange,
            hoisting loop-invariant code, separating independent statements
      - Do NOT add OpenMP pragmas — DiscoPoP will do that after re-profiling
      - Output ONLY a valid unified diff. No explanation, no code fences.
        The diff must begin with '--- ' and include '+++ ' and '@@ ' markers.
""")

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(evidence: EvidencePackage, prior_diff: Optional[str] = None) -> str:
    def fmt_deps(deps, label):
        if not deps:
            return f"  {label}: none\n"
        lines = [f"  {label}:"]
        for d in deps[:20]:
            lines.append(
                f"    line {d.from_line} → {d.to_line}  variable: {d.variable}"
            )
        return "\n".join(lines) + "\n"

    region_label = {
        "loop": "loop",
        "function": "function body",
        "cu": "basic block",
    }.get(evidence.region_type, "code region")

    exec_info = (
        f"{evidence.iteration_count:,} iterations"
        if evidence.region_type == "loop"
        else f"executed (region id: {evidence.region_id})"
    )

    parts = [
        f"## Source file: {evidence.source_file}",
        f"## Region: {evidence.region_id}  type={region_label}  ({exec_info})\n",
        "### Source (>>> marks the target region)\n```cpp",
        evidence.source_region,
        "```\n",
        "### Runtime data dependences (observed across all executions)",
        fmt_deps(evidence.raw_deps, "RAW — read-after-write (the blocking ones)"),
        fmt_deps(evidence.war_deps, "WAR — write-after-read"),
        fmt_deps(evidence.waw_deps, "WAW — write-after-write"),
    ]

    if evidence.reduction_vars:
        parts.append(
            f"### Reduction variables: {', '.join(evidence.reduction_vars)}\n"
        )

    if prior_diff:
        parts.append(
            f"### Your previous attempt (FAILED)\n"
            f"```diff\n{prior_diff}\n```\n"
        )

    if evidence.tier1_failure_reason:
        parts.append(
            f"### What went wrong\n{evidence.tier1_failure_reason}\n"
        )

    parts.append(
        f"### Task\n"
        f"Restructure the {region_label} at lines "
        f"{evidence.region_id} in {evidence.source_file} "
        f"so that DiscoPoP can detect a parallelism pattern after re-profiling.\n"
        f"Output a unified diff only."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Diff validation
# ---------------------------------------------------------------------------

def _extract_diff(text: str) -> Optional[str]:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("--- ") or line.startswith("diff --git"):
            start = i
            break
    return "\n".join(lines[start:]) if start is not None else None


def _is_valid_diff(diff: str) -> bool:
    return "---" in diff and "+++" in diff and "@@" in diff


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def call_llm(
    evidence: EvidencePackage,
    model: str,
    api_key: Optional[str] = None,
    max_format_retries: int = 2,
    prior_diff: Optional[str] = None,
) -> Optional[str]:
    """Call the LLM and return a valid unified diff, or None on failure.

    api_key:    resolved from LLM_API_KEY env var or --api-key CLI arg.
    prior_diff: the diff produced by the previous budget iteration, if any.
                Included in the prompt so the LLM can see what it tried and
                avoid repeating the same mistake.
    """
    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = _build_prompt(evidence, prior_diff=prior_diff)
    messages = [{"role": "user", "content": user_prompt}]

    for attempt in range(max_format_retries + 1):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": _SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=messages,
        )

        text = response.content[0].text
        diff = _extract_diff(text)

        if diff and _is_valid_diff(diff):
            return diff

        # Free format re-prompt — doesn't consume budget
        if attempt < max_format_retries:
            messages.append({"role": "assistant", "content": text})
            messages.append({
                "role": "user",
                "content": (
                    "Your response must be a unified diff only.\n"
                    "Start with '--- <original_file>' on its own line,\n"
                    "then '+++ <modified_file>', then one or more '@@ … @@' hunks.\n"
                    "No prose, no code fences."
                ),
            })

    return None
