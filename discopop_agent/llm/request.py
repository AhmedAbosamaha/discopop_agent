"""
Building the per-request prompt for each edit mode
----------------------------------------------------
Three shapes of the same request: a unified diff, the complete rewritten
function, or an instruction to edit a private copy of the file directly.  They
share the evidence sections and differ only in what the model is asked to
produce.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Set

from ..types import EvidencePackage, GateFacts
from .render import _evidence_sections, _fmt_digest


def _goal(llm_pragmas: bool, gate: GateFacts) -> str:
    """What the rewrite has to achieve — in the words of the mode that is running.

    The task text used to be one constant: "after re-profiling, DiscoPoP must detect
    a genuinely parallel pattern … and achieves measurable speedup".  In the default
    mode nothing re-profiles the rewrite to judge it and no speed is measured, and
    the system prompt says so — so the two halves of one request contradicted each
    other (review P2)."""
    if llm_pragmas:
        checks = ["compiles", "is race-free under ThreadSanitizer"]
        if gate.stress:
            checks.append("gives the same result at every thread count and schedule")
        checks.append("reproduces the original program's results")
        if gate.require_speedup:
            checks.append("runs faster than the same build on one thread")
        return ("restructured so that its iterations are independent, and ANNOTATED BY "
                "YOU: every loop you make parallel carries its own `#pragma omp` with "
                "explicit data-sharing clauses.  The result has to be code that "
                + ", ".join(checks[:-1]) + ", and " + checks[-1]
                + ".  Nothing re-profiles your rewrite, and nothing adds a pragma for you.")
    tail = "race-free under ThreadSanitizer and output-preserving"
    if gate.require_speedup:
        tail += ", and achieve measurable speedup"
    return ("restructured so that, after re-profiling, DiscoPoP detects a genuinely "
            "parallel pattern (Do-All, Reduction, Pipeline, or Task-Parallel) in the "
            "lines you changed.  The pragma it then inserts must compile cleanly, be "
            + tail + ".  Do not write `#pragma omp` yourself.")


def _task_checklist(gate: GateFacts, include: Optional[Set[str]]) -> str:
    """The three analysis steps every edit mode asks for."""
    shown = include is None or "loop_nest" in include
    if gate.require_speedup:
        second = ("  - Does the loop you are making parallel have enough work per activation\n"
                  "    to be worth it?"
                  + ("  The loop structure above says which do.\n" if shown else "\n"))
    else:
        second = ("  - Which is the OUTERMOST loop whose iterations can be made independent?\n"
                  "    That is the one to make parallel — speed is not judged at this input\n"
                  "    size, so a small iteration count is no reason to leave a loop serial.\n")
    return ("  - Which dependence is actually blocking this, and is it a value moving\n"
            "    between iterations or just a location being reused?\n"
            + second +
            "  - Re-derive any bound the old execution order made safe.\n")


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def _build_prompt(evidence: EvidencePackage,
                  include: Optional[Set[str]] = None,
                  llm_pragmas: bool = False,
                  gate: GateFacts = GateFacts()) -> str:
    region_label = {
        "loop": "loop",
        "function": "function body",
        "cu": "basic block",
    }.get(evidence.region_type, "code region")

    # The observed iteration count is profile data: it goes with the `loop_nest`
    # section, or `--evidence none` would still carry it in the header.
    exec_info = (
        f"{evidence.iteration_count:,} iterations"
        if evidence.region_type == "loop" and (include is None or "loop_nest" in include)
        else f"region id: {evidence.region_id}"
    )

    parts = [
        f"## Source file: {evidence.source_file}",
        f"## Target region: {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line}  "
        f"(DiscoPoP id {evidence.region_id}; {exec_info})\n",
        _fmt_digest(evidence, include),
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
    ]
    parts.extend(_evidence_sections(evidence, "### Runtime data dependences "
                                              "(observed across all executions)",
                                    include, gate.require_speedup, llm_pragmas))

    parts.append(
        f"### Task\n"
        f"The {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line} in {evidence.source_file} "
        f"is to be {_goal(llm_pragmas, gate)}\n"
        f"\n"
        f"Worth settling before you write:\n"
        f"{_task_checklist(gate, include)}\n"
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT as specified in the system instructions: the short plan, "
        f"then the unified diff, and end the response there."
    )
    return "\n".join(p for p in parts if p)


def _build_function_prompt(evidence: EvidencePackage,
                           include: Optional[Set[str]] = None,
                           llm_pragmas: bool = False,
                           gate: GateFacts = GateFacts()) -> str:
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
        _fmt_digest(evidence, include),
        "### Current function (rewrite this whole function):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)",
        include, gate.require_speedup, llm_pragmas))

    parts.append(
        "### Task\n"
        f"The {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` is to be {_goal(llm_pragmas, gate)}\n"
        "\n"
        "Worth settling before you write:\n"
        f"{_task_checklist(gate, include)}"
        "\n"
        ">>> OUTPUT as specified in the system instructions: the short plan, "
        "then the ENTIRE rewritten function as ONE ```cpp code block, and end "
        "there. Keep the same function name and signature."
    )
    return "\n".join(p for p in parts if p)


def _build_direct_prompt(evidence: EvidencePackage, ws_file: Path,
                         include: Optional[Set[str]] = None,
                         llm_pragmas: bool = False,
                         gate: GateFacts = GateFacts()) -> str:
    """Prompt for --edit-mode direct: the model edits `ws_file` (a private
    working copy of the source) with its own Read/Edit/Write tools instead of
    emitting an edit as text.  The excerpt below is context only — the file on
    disk is the authority, and the model is told to read it."""
    region_label = {
        "loop": "loop", "function": "function body", "cu": "basic block",
    }.get(evidence.region_type, "code region")
    fname = evidence.enclosing_function_name or "(enclosing function)"

    from .. import project as project_mod
    proj = project_mod.active()
    context = []
    if proj is not None:
        rel = proj.rel(evidence.source_file) or Path(evidence.source_file).name
        others = [u for u in proj.units if u != rel]
        context = [
            f"## This file is `{rel}` of a multi-file program.  The directory it sits in "
            f"is a copy of the whole program — read its headers and the other units "
            f"({', '.join(others[:8]) or 'none'}) for context.  Only your changes to "
            f"`{rel}` are used; an edit to any other file is discarded."]
    parts = [
        f"## File to edit: {ws_file}",
        *context,
        f"## Function containing the target region: {fname}  "
        f"(lines {evidence.enclosing_function_start}–{evidence.enclosing_function_end})",
        f"## Target region: {region_label} {evidence.region_id} at lines "
        f"{evidence.start_line}–{evidence.end_line}\n",
        _fmt_digest(evidence, include),
        "### The function as it currently stands in the file (excerpt — read the "
        "file itself before editing; line numbers here are the file's own):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)",
        include, gate.require_speedup, llm_pragmas))

    parts.append(
        "### Task\n"
        f"Edit `{ws_file}`: the {region_label} (lines "
        f"{evidence.start_line}–{evidence.end_line}) inside `{fname}` is to be "
        f"{_goal(llm_pragmas, gate)}\n"
        "\n"
        "Worth settling before you write:\n"
        f"{_task_checklist(gate, include)}"
        "\n"
        ">>> Read the file, give the short plan, then APPLY the rewrite with the "
        "Edit tool. Do not print a diff or the rewritten code — the file's "
        "content is what is used. Keep the function's name and signature."
    )
    return "\n".join(p for p in parts if p)
