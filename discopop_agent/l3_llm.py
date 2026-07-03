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

from . import viz
from .types import EvidencePackage

# ---------------------------------------------------------------------------
# System prompt (cached across all calls in a session)
# ---------------------------------------------------------------------------

_SYSTEM_CORE = textwrap.dedent("""\
    You are an expert in C/C++ parallelization and compiler dependency analysis,
    acting as the restructuring stage of DiscoPoP, an automatic OpenMP parallelism
    profiler.

    ------------------------------------------------------------------
    HOW YOUR OUTPUT IS USED  (read this — it defines the constraints)
    ------------------------------------------------------------------
    DiscoPoP profiled ONE code region and could not extract safe parallelism from
    it: either it found no pattern, or the pattern it found produced an OpenMP
    pragma that failed validation (did not compile, raced under ThreadSanitizer,
    changed the program's output, or gave no speedup).

    You rewrite the region's SEQUENTIAL source so that the parallelism becomes
    explicit and safe.  You do NOT insert OpenMP pragmas — DiscoPoP re-profiles
    your rewrite and inserts them itself.

    Your rewrite is then compiled, run, and its output is compared BYTE-FOR-BYTE
    with the original program.  Any difference is an automatic rejection.
    Correctness is an absolute constraint, never traded against performance.

    ------------------------------------------------------------------
    WHAT COUNTS AS SUCCESS
    ------------------------------------------------------------------
    DiscoPoP can only exploit these patterns, so your rewrite must expose at
    least one of them:
      - Do-All        — loop iterations are fully independent.
      - Reduction     — iterations combine into an associative/commutative accumulator.
      - Pipeline      — ordered producer -> consumer stages with no back-edges.
      - Task-parallel — independent regions connected by explicit data flow.
    Aim for a rewrite that not only is detectable but actually pays off: coarse
    enough that thread-spawn overhead is amortised.

    Your job is to EXPOSE PARALLELISM, not to speed up the sequential version.
    A faster serial algorithm is NOT a valid answer.  In particular, do NOT:
      - add an early-termination / "did anything change this pass" shortcut,
      - substitute a lower-complexity but still-serial algorithm,
      - reorder work to finish sooner while keeping the same loop-carried
        dependence.
    None of these remove the blocking dependence; they leave the region just as
    unparallelizable as before (and are often rejected outright).  Every rewrite
    must make some loop's iterations genuinely independent (Do-All / Reduction)
    or split it into independent stages/tasks.

    ------------------------------------------------------------------
    READ THE EVIDENCE FIRST — REASON FROM IT, NOT FROM THE ALGORITHM'S NAME
    ------------------------------------------------------------------
    Each request gives you the region source, the runtime dependences observed
    (RAW / WAR / WAW with line and variable), any reduction variables, DiscoPoP's
    exact Do-All blockers, and — when a pragma was already tried — why it failed.
    Do not guess from what the code "looks like"; decide from this evidence.
      - RAW (read-after-write) across iterations is the real blocker: some
        iteration reads a value another iteration wrote.  Removing these is the job.
      - WAR / WAW are usually STORAGE conflicts (a variable reused across
        iterations), not true data flow — they typically dissolve under
        privatization or renaming.
      - A blocker marked STATIC origin may be a dependence DiscoPoP could not rule
        out rather than one that truly occurs — often removable by privatizing or
        first-writing the variable inside the loop.  A DYNAMIC origin blocker was
        actually observed at run time and must be genuinely broken.

    ------------------------------------------------------------------
    METHOD — CLASSIFY EACH BLOCKING DEPENDENCE BY ITS CAUSE, THEN FIX THE CAUSE
    ------------------------------------------------------------------
    For every RAW / blocker, decide which cause below it is; the cause dictates
    the fix.  Match on the DATA FLOW, not on the surface syntax or algorithm.

      1. STORAGE / FALSE DEPENDENCE — a scalar or buffer is REUSED across
         iterations (a temp, an index, scratch space) but carries no real value
         from one iteration to the next.
         Fix: give each iteration its own instance — declare the variable inside
              the loop body (privatize) or rename to break the reuse.  No
              algorithmic change.

      2. ACCUMULATION / REDUCTION — every iteration reads AND writes the same
         variable through an associative, commutative operator
         (+, *, min, max, count, logical and/or).
         Fix: isolate it as a clean reduction — one accumulation per iteration
              into one variable, with no other writes to shared state in the body.
              Strip unrelated work that hides the reduction (see cause 6).

      3. IN-PLACE COUPLING — within ONE sweep, an iteration reads array elements
         that another iteration of the SAME sweep writes (updates that touch an
         element and its neighbour, a compare-and-swap of adjacent items, or
         writing back into the array being read).

         DECIDE FIRST — what does each new value depend on?  This choice is
         mandatory; picking the wrong branch does NOT remove the dependence:
           - If every element's new value depends ONLY on the PREVIOUS sweep's
             values (a pure map / stencil, e.g. new[i] = f(old[i-1], old[i],
             old[i+1]), and no element written this sweep is read again this
             sweep) -> use (a).
           - If an element's new value depends on another element's value that
             was WRITTEN earlier in the SAME sweep (the update propagates /
             cascades along the array, e.g. a swap that may move a value across
             several positions) -> (a) is INVALID; you MUST use (b).

         Fix:
           a) DOUBLE-BUFFER: allocate a separate output array; read every input
              exclusively from the previous-sweep buffer, write every result into
              the new buffer, then swap the two buffers after the sweep.  Valid
              ONLY when no element written this sweep is read again this sweep.
           b) PARTITION / COLOUR: keep the updates in place, but split each sweep
              into ordered sub-passes whose iterations touch DISJOINT,
              non-adjacent elements (e.g. even-indexed pairs, then odd-indexed
              pairs; or "red" cells, then "black").  Within one sub-pass every
              iteration is independent -> Do-All; running the sub-passes in order
              reproduces the sequential result.  Preserve the SAME total work —
              do not drop sub-passes or shorten the sweep count.

         WRONG (removes NOTHING): copying the array into a renamed buffer and then
              performing the SAME order-dependent, in-place updates on the copy.
              A rename is not a decoupling: `temp[i] > temp[i+1]` with an in-place
              swap carries the identical loop-carried dependence that `arr[...]`
              did.  Real double-buffering (a) reads OLD and writes NEW and is only
              valid for the map/stencil case above; a cascading in-place update
              needs (b).

      4. TRUE RECURRENCE / SCAN — iteration i's result is defined in terms of
         iteration i-1's result (running total, propagation, chained state).
         Fix: reformulate, do not privatize.  Options: a closed-form expression
              of i, a parallel prefix-scan, or a blocked / recursive-doubling
              formulation.  If the recurrence is genuinely serial and cannot be
              reassociated, leave it unparallelized rather than emit an unsafe
              rewrite.

      5. NON-CANONICAL CONTROL FLOW — the loop can't be parallelized because its
         trip count is not known up front: break, continue, return, goto, or a
         non-affine bound.
         Fix: convert to a fixed-trip-count loop with IDENTICAL results — replace
              early exit with a flag/mask evaluated every iteration and tested
              after the loop; move compound conditions into the bound.  Change the
              control structure only, never what is computed.

      6. SERIALIZATION BY MIXED CONCERNS — the body fuses independent
         computations, or repeats loop-invariant work, hiding the parallel part.
         Fix: hoist invariant work out of the loop; SPLIT (fission) a loop whose
              statements are independent across iterations into separate loops,
              each parallelizable on its own; conversely FUSE trivially small
              parallel loops to raise granularity.

    ------------------------------------------------------------------
    TRANSFORM ONLY WHAT THE EVIDENCE JUSTIFIES
    ------------------------------------------------------------------
    Make the SMALLEST change that removes the specific blocking dependences
    reported.  Preserve every other line, the algorithm's full amount of work
    (same passes / sweeps / iterations — never shorten a convergence loop or drop
    boundary elements), and the exact order of floating-point operations.
    When the failure was "no speedup" (not a race), the dependence is already
    gone — restructure for GRANULARITY (coarsen, fuse, hoist, move parallelism to
    an outer level), not for correctness.

    ------------------------------------------------------------------
    OPENMP-CANONICAL FORM (every loop you intend to be parallel must satisfy ALL)
    ------------------------------------------------------------------
      - Condition compares the loop variable DIRECTLY against a loop-invariant
        bound:  RIGHT `i < n - 1`   WRONG `i + 1 < n`  (compound left-hand side).
      - Increment is i++, i--, i += c, or i -= c with loop-invariant c.
      - Body has NO break, continue, return, or goto.
      - Trip count is computable before the loop begins.

    NEVER INTRODUCE new break, continue, return, or goto as part of a
    transformation — not in the target loop and not in any enclosing loop you
    touch.  Adding control flow that exits a loop early makes its trip count
    unknown and DISQUALIFIES it from parallelization (the opposite of the goal).
    If the existing code has such control flow, convert it to canonical form
    (cause 5); do not add more.

    ------------------------------------------------------------------
    BEFORE YOU WRITE CODE, verify silently:
    ------------------------------------------------------------------
      1. Which cause (1-6) does each reported RAW / blocker fall under?
      2. Does my transformation REMOVE that exact dependence, or merely relabel it
         (or just make the sequential version finish faster)?
      3. Can iteration i and iteration i+1 now run simultaneously with no
         read/write conflict on any shared location?
      4. Does the rewrite compute a byte-for-byte identical result, in the same
         operation order?
      5. Is every loop I want parallelized in canonical form, and did I avoid
         adding ANY break/continue/return?

    ------------------------------------------------------------------
    CORRECTNESS CONTRACT (verified automatically, byte-for-byte)
    ------------------------------------------------------------------
      - The sequential output of your rewrite must be IDENTICAL to the original
        before any OpenMP pragma is applied.
      - Preserve full work: same passes / sweeps, same bounds, same boundary
        handling, same rounding.
      - Do not rename the function or change its signature; do not add or reorder
        I/O or change output formatting.
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

def _build_prompt(evidence: EvidencePackage) -> str:
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

    blockers = _fmt_blockers(evidence.prevented_deps)
    if blockers:
        parts.append(blockers)

    if evidence.tier1_failure_reason:
        parts.append(
            f"### What went wrong\n{evidence.tier1_failure_reason}\n"
        )

    parts.append(
        f"### Task\n"
        f"Restructure the {region_label} at lines "
        f"{evidence.region_id} in {evidence.source_file} "
        f"so that after re-profiling DiscoPoP detects a genuinely parallel "
        f"pattern (Do-All, Reduction, Pipeline, or Task-Parallel) that compiles "
        f"cleanly, is race-free under ThreadSanitizer, and achieves measurable "
        f"speedup.\n"
        f"\n"
        f"Follow the three-step process from the system instructions:\n"
        f"  1. Identify the dependency category from the profile above.\n"
        f"  2. Apply the matching transformation (not a superficial workaround).\n"
        f"  3. Verify the dependency is structurally gone before writing code.\n"
        f"\n"
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


def _fmt_blockers(prevented: list) -> str:
    """Render DiscoPoP's exact Do-All blockers (from doall_prevented.json).
    Returns '' when none are available (old explorer / clean loop)."""
    if not prevented:
        return ""
    out = [
        "### Why DiscoPoP could not parallelize (Do-All blockers)",
        "DiscoPoP identified these exact dependences as what blocks Do-All — "
        "target these specifically:",
    ]
    for b in prevented[:20]:
        origin = str(b.get("origin", "")).upper()
        note = ("dynamic — a real, observed dependency; it must be removed"
                if "DYNAMIC" in origin
                else "static — may be resolvable by privatizing / first-writing the variable inside the loop")
        # Strip enum prefixes (DepType.RAW -> RAW), tidy the variable name.
        dtype = str(b.get("dep_type", "?")).split(".")[-1]
        var = str(b.get("var_name", "?"))
        # Line info is optional in the new detector; show it only when present.
        src = str(b.get("source_line") or "").split(":")[-1]
        snk = str(b.get("sink_line") or "").split(":")[-1]
        if src and snk and src != "None" and snk != "None":
            where = f"line {src} → {snk}"
        else:
            ls, le = b.get("loop_start"), b.get("loop_end")
            where = f"loop-carried (loop at line{'s' if ls != le else ''} {ls}" + (f"–{le}" if ls != le else "") + ")"
        out.append(f"  - {dtype} on `{var}`  {where}  [{note}]")
    return "\n".join(out) + "\n"


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
    blockers = _fmt_blockers(evidence.prevented_deps)
    if blockers:
        parts.append(blockers)
    if evidence.tier1_failure_reason:
        parts.append(f"### What went wrong\n{evidence.tier1_failure_reason}\n")

    parts.append(
        "### Task\n"
        f"Restructure the {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` so that after re-profiling "
        "DiscoPoP detects a genuinely parallel pattern (Do-All, Reduction, "
        "Pipeline, or Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Follow the three-step process from the system instructions:\n"
        "  1. Identify the dependency category from the profile above.\n"
        "  2. Apply the matching transformation (not a superficial workaround).\n"
        "  3. Verify the dependency is structurally gone before writing code.\n"
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
    verbose: bool = False,
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
    kind = "function" if function_mode else "diff"

    for attempt in range(max_format_retries + 1):
        if verbose:
            last_user = next(
                (m["content"] for m in reversed(current) if m["role"] == "user"), ""
            )
            viz.llm_request(model, provider, system, last_user, attempt=attempt)

        text = _complete(provider, client, model, current, system)

        if verbose:
            viz.llm_response(text, kind=kind)

        out = _extract_code(text) if function_mode else _extract_diff(text)
        valid = out is not None if function_mode else bool(out and _is_valid_diff(out))

        if verbose:
            viz.llm_extracted(kind, out if valid else None)

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
