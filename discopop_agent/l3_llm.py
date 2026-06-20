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

    CRITICAL — every loop you intend to be parallelized (including any new
    loops your restructuring creates) MUST be in OpenMP-canonical form, or
    DiscoPoP's generated `#pragma omp parallel for` will fail to compile:
      - The loop condition must compare the loop variable DIRECTLY against a
        loop-invariant bound: `i < bound`, `i <= bound`, `i > bound`,
        `i >= bound`, or `i != bound`.
        WRONG:  for (int i = 0; i + 1 < n; i += 2)   ← compound expression
        RIGHT:  for (int i = 0; i < n - 1; i += 2)   ← precompute the bound
      - The increment must be `i++`, `i--`, `i += c`, or `i -= c` with a
        loop-invariant `c`.
      - NO `break`, `continue`, `return`, or `goto` inside the loop body.
        Convert early-exit searches / flag-setting loops into a full scan that
        accumulates into a variable (e.g. `found |= (cond);` then test `found`
        after the loop), so the loop body has a single straight-line path.
      - The trip count must be computable before the loop runs (no data- or
        condition-dependent termination).

    CORRECTNESS — your change is AUTOMATICALLY VERIFIED: the program is run
    before and after your patch and the outputs are compared byte-for-byte.
    A patch that alters the observable result is REJECTED, no matter how clean
    it looks.  To pass:
      - Preserve the algorithm's FULL work.  If you replace an algorithm with an
        equivalent one (e.g. an in-place sweep with a transposition-network
        sweep), reproduce its exact termination/convergence — do not shorten the
        pass or phase count.  (E.g. odd-even transposition sort needs N phases
        for N elements, NOT N-1; a Jacobi sweep needs the same number of steps.)
      - Do not drop boundary elements or tighten loop bounds in a way that skips
        work the original performed.
      - Prefer the smallest transformation that removes the specific dependency
        shown in the profile (loop fission, a temp array, privatization) over a
        wholesale algorithm rewrite — smaller changes are far less likely to
        change results.
      - Re-derive the result the same way: same accumulation, same comparisons,
        same rounding/order where it affects floating-point output.

    >>> OUTPUT A UNIFIED DIFF ONLY. <<<
    No prose, no explanation, no markdown, no code fences. Your ENTIRE response
    must be the diff itself, beginning with '--- ' and containing '+++ ' and
    '@@ ' markers. Any text that is not part of the diff causes the response to
    be rejected.
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
        (
            "### Source\n"
            "(Each line is shown as `NNNN >>> code` where `NNNN` is the line number "
            "and `>>>` marks the target region. "
            "These prefixes are display-only — they are NOT part of the actual source file. "
            "When writing diff context lines (lines starting with a single space), "
            "copy only the raw code indentation, never the `NNNN >>>` prefix.)\n"
            "```cpp"
        ),
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
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT A UNIFIED DIFF ONLY. <<<\n"
        f"No prose, no explanation, no markdown, no code fences. Your entire "
        f"response must be the diff itself, beginning with '--- ' and containing "
        f"'+++ ' and '@@ ' markers. Any text that is not part of the diff will "
        f"cause the response to be rejected."
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

_MANUAL_EOF = "---END---"


def call_manual(
    evidence: EvidencePackage,
    messages: Optional[list] = None,
) -> tuple[Optional[str], list]:
    """Print the prompt (or full conversation history) to stdout and read a diff from stdin.

    On the first call for a region pass messages=None — the system prompt and
    initial user prompt are printed in full.  On subsequent budget retries pass
    the list returned by the previous call: the full conversation history
    (prior diffs + quality-gate diagnostics appended by the controller) is
    printed so the user sees exactly what a real LLM would see before entering
    the next diff.

    Interactive: paste the diff and type '---END---' on its own line to submit.
    Piped input: separate multiple diffs with '---END---' lines; true EOF also works.
    """
    if messages is None:
        user_prompt = _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

        print("\n" + "=" * 70)
        print("  SYSTEM PROMPT (send to LLM)")
        print("=" * 70)
        print(_SYSTEM)
        print("=" * 70)
        print("  USER PROMPT (send to LLM)")
        print("=" * 70)
        print(user_prompt)
    else:
        print("\n" + "=" * 70)
        print(f"  CONVERSATION HISTORY ({len(messages)} turn(s))")
        print("=" * 70)
        for turn in messages:
            role = "USER" if turn["role"] == "user" else "ASSISTANT"
            print(f"\n{'─' * 70}")
            print(f"  [{role}]")
            print(f"{'─' * 70}")
            print(turn["content"])

    print("\n" + "=" * 70)
    print(f"  Paste the new diff below, then type '{_MANUAL_EOF}' on its own line (or Ctrl-D):")
    print("=" * 70 + "\n")

    lines = []
    try:
        while True:
            line = input()
            if line == _MANUAL_EOF:
                break
            lines.append(line)
    except EOFError:
        pass

    text = "\n".join(lines).strip()
    if not text:
        return None, list(messages)

    diff = _extract_diff(text)
    if diff and _is_valid_diff(diff):
        return diff, list(messages) + [{"role": "assistant", "content": diff}]

    print("│  [Manual-LLM] Response does not look like a valid unified diff.")
    return None, list(messages)


def call_llm(
    evidence: EvidencePackage,
    model: str,
    api_key: Optional[str] = None,
    max_format_retries: int = 2,
    messages: Optional[list] = None,
) -> tuple[Optional[str], list]:
    """Call the LLM and return (diff or None, updated messages).

    On the first call for a region pass messages=None — the initial prompt is
    built from evidence.  Pass the list returned by the previous call on
    subsequent budget retries: the LLM then sees the full conversation history
    (all prior attempts plus quality-gate diagnostics appended by the
    controller) instead of a fresh, context-free prompt each time.
    """
    client = anthropic.Anthropic(api_key=api_key)

    if messages is None:
        # First attempt for this region — build initial prompt from evidence.
        user_prompt = _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

    current = list(messages)

    for attempt in range(max_format_retries + 1):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": _SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=current,
        )

        text = response.content[0].text
        diff = _extract_diff(text)

        if diff and _is_valid_diff(diff):
            # Return messages with assistant turn appended so the controller
            # can extend the conversation with quality-gate feedback and retry.
            return diff, current + [{"role": "assistant", "content": text}]

        # Free format re-prompt — doesn't consume a budget slot.
        if attempt < max_format_retries:
            current = current + [
                {"role": "assistant", "content": text},
                {
                    "role": "user",
                    "content": (
                        "Your response must be a unified diff only.\n"
                        "Start with '--- <original_file>' on its own line,\n"
                        "then '+++ <modified_file>', then one or more '@@ … @@' hunks.\n"
                        "No prose, no code fences."
                    ),
                },
            ]

    return None, current
