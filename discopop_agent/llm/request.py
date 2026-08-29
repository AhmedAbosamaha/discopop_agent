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

from ..types import EvidencePackage
from .render import _evidence_sections, _fmt_digest


# The three analysis steps every edit mode asks for, verbatim.
_TASK_CHECKLIST = (
    "  - Which dependence is actually blocking this, and is it a value moving\n"
    "    between iterations or just a location being reused?\n"
    "  - Does the loop you are making parallel have enough work per activation\n"
    "    to be worth it?  The loop structure above says which do.\n"
    "  - Re-derive any bound the old execution order made safe.\n"
)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def _build_prompt(evidence: EvidencePackage,
                  include: Optional[Set[str]] = None) -> str:
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
        f"## Target region: {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line}  "
        f"(DiscoPoP id {evidence.region_id}; {exec_info})\n",
        _fmt_digest(evidence),
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
                                    include))

    parts.append(
        f"### Task\n"
        f"Restructure the {region_label} at lines "
        f"{evidence.start_line}–{evidence.end_line} in {evidence.source_file} "
        f"so that after re-profiling DiscoPoP detects a genuinely parallel "
        f"pattern (Do-All, Reduction, Pipeline, or Task-Parallel) that compiles "
        f"cleanly, is race-free under ThreadSanitizer, and achieves measurable "
        f"speedup.\n"
        f"\n"
        f"Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}\n"
        f"IMPORTANT: diff context lines (lines beginning with a single space) must match "
        f"the actual file content exactly — use only the raw code indentation, "
        f"not the `NNNN >>>` display prefix shown in the Source section above.\n"
        f"\n"
        f">>> OUTPUT as specified in the system instructions: the short plan, "
        f"then the unified diff, and end the response there."
    )
    return "\n".join(parts)


def _build_function_prompt(evidence: EvidencePackage,
                           include: Optional[Set[str]] = None) -> str:
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
        _fmt_digest(evidence),
        "### Current function (rewrite this whole function):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)",
        include))

    parts.append(
        "### Task\n"
        f"Restructure the {region_label} (lines {evidence.start_line}–"
        f"{evidence.end_line}) inside `{fname}` so that after re-profiling "
        "DiscoPoP detects a genuinely parallel pattern (Do-All, Reduction, "
        "Pipeline, or Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> OUTPUT as specified in the system instructions: the short plan, "
        "then the ENTIRE rewritten function as ONE ```cpp code block, and end "
        "there. Keep the same function name and signature."
    )
    return "\n".join(parts)


def _build_direct_prompt(evidence: EvidencePackage, ws_file: Path,
                         include: Optional[Set[str]] = None) -> str:
    """Prompt for --edit-mode direct: the model edits `ws_file` (a private
    working copy of the source) with its own Read/Edit/Write tools instead of
    emitting an edit as text.  The excerpt below is context only — the file on
    disk is the authority, and the model is told to read it."""
    region_label = {
        "loop": "loop", "function": "function body", "cu": "basic block",
    }.get(evidence.region_type, "code region")
    fname = evidence.enclosing_function_name or "(enclosing function)"

    parts = [
        f"## File to edit: {ws_file}",
        f"## Function containing the target region: {fname}  "
        f"(lines {evidence.enclosing_function_start}–{evidence.enclosing_function_end})",
        f"## Target region: {region_label} {evidence.region_id} at lines "
        f"{evidence.start_line}–{evidence.end_line}\n",
        _fmt_digest(evidence),
        "### The function as it currently stands in the file (excerpt — read the "
        "file itself before editing; line numbers here are the file's own):",
        "```cpp",
        evidence.enclosing_function_source,
        "```\n",
    ]
    parts.extend(_evidence_sections(
        evidence, "### Runtime data dependences in the target region (observed)",
        include))

    parts.append(
        "### Task\n"
        f"Edit `{ws_file}` so that the {region_label} (lines "
        f"{evidence.start_line}–{evidence.end_line}) inside `{fname}` is "
        "restructured for parallelism: after re-profiling, DiscoPoP must detect "
        "a genuinely parallel pattern (Do-All, Reduction, Pipeline, or "
        "Task-Parallel) that compiles cleanly, is race-free under "
        "ThreadSanitizer, and achieves measurable speedup.\n"
        "\n"
        "Worth settling before you write:\n"
        f"{_TASK_CHECKLIST}"
        "\n"
        ">>> Read the file, give the short plan, then APPLY the rewrite with the "
        "Edit tool. Do not print a diff or the rewritten code — the file's "
        "content is what is used. Keep the function's name and signature."
    )
    return "\n".join(parts)
