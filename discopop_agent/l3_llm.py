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

import re
import textwrap
from typing import Any, Optional

import anthropic

from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

_SYSTEM_CORE = textwrap.dedent("""\
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
    A change that alters the observable result is REJECTED, no matter how clean
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
""")

# Output-format instruction appended per edit mode.
_OUTPUT_DIFF = textwrap.dedent("""\

    >>> OUTPUT A UNIFIED DIFF ONLY. <<<
    No prose, no explanation, no markdown, no code fences. Your ENTIRE response
    must be the diff itself, beginning with '--- ' and containing '+++ ' and
    '@@ ' markers. Any text that is not part of the diff causes the response to
    be rejected.
""")

_OUTPUT_FUNCTION = textwrap.dedent("""\

    >>> OUTPUT THE COMPLETE REWRITTEN FUNCTION ONLY. <<<
    Return the ENTIRE function — its signature and full body, from the opening
    `{` to the closing `}` — as a single C++ code block.  Do NOT output a diff,
    line numbers, markers, or prose.  Rewrite only this one function; do not
    rename it or change its signature.  The agent applies your function verbatim
    in place, so it must compile as-is.
""")

# Diff mode keeps the original system prompt verbatim; function mode swaps the
# trailing output instruction.
_SYSTEM = _SYSTEM_CORE + _OUTPUT_DIFF
_SYSTEM_FUNCTION = _SYSTEM_CORE + _OUTPUT_FUNCTION

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


def _fmt_deps(deps: list, label: str) -> str:
    if not deps:
        return f"  {label}: none\n"
    lines = [f"  {label}:"]
    for d in deps[:20]:
        lines.append(f"    line {d.from_line} → {d.to_line}  variable: {d.variable}")
    return "\n".join(lines) + "\n"


def _build_function_prompt(evidence: EvidencePackage) -> str:
    """Prompt for --edit-mode function: show the whole enclosing function and the
    target region's dependence profile, and ask for the complete rewritten
    function back (no diff)."""
    region_label = {
        "loop": "loop", "function": "function body", "cu": "basic block",
    }.get(evidence.region_type, "code region")
    fname = evidence.enclosing_function_name or "(enclosing function)"

    parts = [
        f"## Source file: {evidence.source_file}",
        f"## Function to rewrite: {fname}  "
        f"(lines {evidence.enclosing_function_start}–{evidence.enclosing_function_end})",
        f"## Target region: {region_label} {evidence.region_id} at lines "
        f"{evidence.start_line}–{evidence.end_line}\n",
        "### Current function (rewrite this whole function):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
        "### Runtime data dependences in the target region (observed)",
        _fmt_deps(evidence.raw_deps, "RAW — read-after-write (the blocking ones)"),
        _fmt_deps(evidence.war_deps, "WAR — write-after-read"),
        _fmt_deps(evidence.waw_deps, "WAW — write-after-write"),
    ]
    if evidence.reduction_vars:
        parts.append(f"### Reduction variables: {', '.join(evidence.reduction_vars)}\n")
    if evidence.tier1_failure_reason:
        parts.append(f"### What went wrong\n{evidence.tier1_failure_reason}\n")

    parts.append(
        "### Task\n"
        f"Restructure the {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` so that DiscoPoP can detect a "
        "parallelism pattern after re-profiling, preserving exact program "
        "semantics.\n"
        "\n"
        ">>> OUTPUT THE COMPLETE REWRITTEN FUNCTION ONLY. <<<\n"
        "Return the entire function (signature + full body) as one ```cpp code "
        "block. No diff, no line numbers, no markers, no prose. Keep the same "
        "function name and signature."
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


_CODE_FENCE_RE = re.compile(r"```(?:cpp|c\+\+|cxx|c)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_code(text: str) -> Optional[str]:
    """For --edit-mode function: pull the rewritten function out of the response.
    Prefer a fenced ```cpp block; otherwise use the raw text.  Returns None if it
    doesn't look like a function (no braces)."""
    m = _CODE_FENCE_RE.search(text)
    code = (m.group(1) if m else text).strip("\n")
    if "{" in code and "}" in code:
        return code
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_MANUAL_EOF = "---END---"


def call_manual(
    evidence: EvidencePackage,
    messages: Optional[list] = None,
    edit_mode: str = "diff",
) -> tuple[Optional[str], list]:
    """Print the prompt (or full conversation history) to stdout and read the
    response from stdin.

    In edit_mode="diff" the expected response is a unified diff; in
    edit_mode="function" it is the complete rewritten function.

    On the first call for a region pass messages=None — the system prompt and
    initial user prompt are printed in full.  On subsequent budget retries pass
    the list returned by the previous call so the full conversation history is
    printed.

    Interactive: paste the response and type '---END---' on its own line to
    submit.  Piped input: separate responses with '---END---' lines; EOF works.
    """
    function_mode = edit_mode == "function"
    system = _SYSTEM_FUNCTION if function_mode else _SYSTEM
    what = "complete rewritten function" if function_mode else "diff"

    if messages is None:
        user_prompt = _build_function_prompt(evidence) if function_mode else _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

        print("\n" + "=" * 70)
        print("  SYSTEM PROMPT (send to LLM)")
        print("=" * 70)
        print(system)
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
    print(f"  Paste the new {what} below, then type '{_MANUAL_EOF}' on its own line (or Ctrl-D):")
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

    if function_mode:
        code = _extract_code(text)
        if code is not None:
            return code, list(messages) + [{"role": "assistant", "content": code}]
        print("│  [Manual-LLM] Response does not look like a function (needs braces).")
        return None, list(messages)

    diff = _extract_diff(text)
    if diff and _is_valid_diff(diff):
        return diff, list(messages) + [{"role": "assistant", "content": diff}]

    print("│  [Manual-LLM] Response does not look like a valid unified diff.")
    return None, list(messages)


def _make_client(provider: str, api_key: Optional[str], api_base: Optional[str]) -> Any:
    """Create the provider client.  'anthropic' (default) uses the Anthropic SDK;
    'openai-compat' uses the OpenAI SDK pointed at an OpenAI-compatible endpoint
    (e.g. a self-hosted vLLM server) via api_base."""
    if provider == "openai-compat":
        try:
            import openai
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "provider 'openai-compat' requires the openai package "
                "(`venv/bin/pip install openai`)."
            ) from e
        return openai.OpenAI(api_key=api_key or "EMPTY", base_url=api_base)
    return anthropic.Anthropic(api_key=api_key)


def _complete(provider: str, client: Any, model: str, current: list, system: str) -> str:
    """Run one completion against the chosen provider and return the raw text.

    Both providers receive the same `system` instructions and the same
    user/assistant conversation; only the wire format differs (Anthropic takes
    `system` separately, OpenAI takes it as the first message)."""
    if provider == "openai-compat":
        resp = client.chat.completions.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "system", "content": system}] + current,
        )
        return resp.choices[0].message.content or ""
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=current,
    )
    return str(resp.content[0].text)


def call_llm(
    evidence: EvidencePackage,
    model: str,
    api_key: Optional[str] = None,
    max_format_retries: int = 2,
    messages: Optional[list] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
    edit_mode: str = "diff",
) -> tuple[Optional[str], list]:
    """Call the LLM and return (output or None, updated messages).

    In edit_mode="diff" (default) the output is a unified diff.  In
    edit_mode="function" it is the complete rewritten enclosing function (the
    controller splices it in by line range and generates the diff itself), which
    avoids the LLM having to produce a byte-exact diff.

    On the first call for a region pass messages=None — the initial prompt is
    built from evidence.  Pass the list returned by the previous call on
    subsequent budget retries so the model sees the full conversation history.

    `provider` selects the backend: "anthropic" (default) or "openai-compat"
    (any OpenAI-compatible endpoint at `api_base`, e.g. a self-hosted vLLM).
    """
    function_mode = edit_mode == "function"
    system = _SYSTEM_FUNCTION if function_mode else _SYSTEM
    client = _make_client(provider, api_key, api_base)

    if messages is None:
        # First attempt for this region — build initial prompt from evidence.
        user_prompt = _build_function_prompt(evidence) if function_mode else _build_prompt(evidence)
        messages = [{"role": "user", "content": user_prompt}]

    current = list(messages)

    for attempt in range(max_format_retries + 1):
        text = _complete(provider, client, model, current, system)
        out = _extract_code(text) if function_mode else _extract_diff(text)
        valid = out is not None if function_mode else bool(out and _is_valid_diff(out))

        if valid:
            # Return messages with assistant turn appended so the controller
            # can extend the conversation with quality-gate feedback and retry.
            return out, current + [{"role": "assistant", "content": text}]

        # Free format re-prompt — doesn't consume a budget slot.
        if attempt < max_format_retries:
            reprompt = (
                "Your response must be the complete rewritten function as a single "
                "```cpp code block — signature and full body, no diff, no prose."
                if function_mode else
                "Your response must be a unified diff only.\n"
                "Start with '--- <original_file>' on its own line,\n"
                "then '+++ <modified_file>', then one or more '@@ … @@' hunks.\n"
                "No prose, no code fences."
            )
            current = current + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": reprompt},
            ]

    return None, current
