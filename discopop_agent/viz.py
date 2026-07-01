"""
Terminal visualization for the agent.
-------------------------------------
Rich, boxed panels that show *exactly* what the agent does at each step:
the prompt sent to the LLM, the raw response it returned, the extracted
edit, and the outcome of every quality-gate stage.

Everything here degrades gracefully:
  - colors are emitted only to a real TTY (respects $NO_COLOR),
  - panels use a left gutter (no right border) so arbitrarily wide code
    lines never misalign,
  - it is a no-op unless the caller opts in with --verbose.
"""

from __future__ import annotations

import os
import shutil
import sys
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Color handling
# ---------------------------------------------------------------------------


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


_COLOR = _supports_color()


def _c(code: str) -> str:
    return code if _COLOR else ""


RESET = _c("\033[0m")
BOLD = _c("\033[1m")
DIM = _c("\033[2m")
CYAN = _c("\033[36m")
BLUE = _c("\033[34m")
GREEN = _c("\033[32m")
YELLOW = _c("\033[33m")
RED = _c("\033[31m")
MAGENTA = _c("\033[35m")
GREY = _c("\033[90m")

# Set by enable(); when False every public function is a no-op.
_ENABLED = False
# The full system prompt is large and identical on every call — show it once.
_system_shown = False


def enable(on: bool = True) -> None:
    global _ENABLED
    _ENABLED = on


def is_enabled() -> bool:
    return _ENABLED


def _width() -> int:
    return min(shutil.get_terminal_size((100, 24)).columns, 100)


# ---------------------------------------------------------------------------
# Panel primitives
# ---------------------------------------------------------------------------


def _top(title: str, color: str) -> str:
    w = _width()
    label = f" {title} "
    dashes = max(0, w - 4 - len(_strip(label)))
    return f"{color}╭─{RESET}{color}{BOLD}{label}{RESET}{color}{'─' * dashes}╮{RESET}"


def _bottom(color: str) -> str:
    return f"{color}╰{'─' * (_width() - 2)}╯{RESET}"


def _strip(s: str) -> str:
    """Visible length helper — strips ANSI so titles size correctly."""
    import re

    return re.sub(r"\033\[[0-9;]*m", "", s)


def panel(
    title: str,
    body: str,
    color: str = CYAN,
    colorize: Optional[Callable[[str], str]] = None,
    max_lines: Optional[int] = None,
) -> None:
    """Print a titled panel with a colored left gutter.

    `colorize` optionally maps a raw body line -> a colored line (used for diffs).
    `max_lines` truncates very long bodies with a "… N more lines" note.
    """
    if not _ENABLED:
        return
    bar = f"{color}│{RESET} "
    print(_top(title, color))
    lines = body.rstrip("\n").split("\n")
    truncated = 0
    if max_lines is not None and len(lines) > max_lines:
        truncated = len(lines) - max_lines
        lines = lines[:max_lines]
    for ln in lines:
        rendered = colorize(ln) if colorize else ln
        print(f"{bar}{rendered}")
    if truncated:
        print(f"{bar}{DIM}… {truncated} more line{'s' if truncated != 1 else ''}{RESET}")
    print(_bottom(color))


def note(text: str, color: str = GREY) -> None:
    if not _ENABLED:
        return
    print(f"{color}   ┄ {text}{RESET}")


# ---------------------------------------------------------------------------
# Diff coloring
# ---------------------------------------------------------------------------


def _color_diff_line(line: str) -> str:
    if line.startswith("+++") or line.startswith("---"):
        return f"{BOLD}{line}{RESET}"
    if line.startswith("@@"):
        return f"{CYAN}{line}{RESET}"
    if line.startswith("+"):
        return f"{GREEN}{line}{RESET}"
    if line.startswith("-"):
        return f"{RED}{line}{RESET}"
    return f"{DIM}{line}{RESET}"


# ---------------------------------------------------------------------------
# High-level renderers used by the pipeline
# ---------------------------------------------------------------------------


def llm_request(model: str, provider: str, system: str, user: str, attempt: int = 0) -> None:
    """Show what is being sent to the LLM: the system prompt (once) and the
    full user prompt for this turn."""
    if not _ENABLED:
        return
    global _system_shown
    tag = f"→ {provider}:{model}" if provider != "anthropic" else f"→ {model}"
    if attempt > 0:
        tag += f"  (re-prompt {attempt})"
    print()
    if not _system_shown:
        panel(f"LLM SYSTEM PROMPT (shown once)  {tag}", system, color=MAGENTA)
        _system_shown = True
    else:
        note(f"system prompt: unchanged ({len(system.splitlines())} lines) — sending to {model}")
    panel(f"LLM REQUEST  {tag}", user, color=BLUE)


def llm_response(text: str, kind: str = "diff") -> None:
    """Show the raw text the LLM returned."""
    if not _ENABLED:
        return
    panel("LLM RAW RESPONSE", text, color=CYAN)


def llm_extracted(kind: str, code: str | None) -> None:
    """Show the edit the agent extracted from the response (diff or function)."""
    if not _ENABLED:
        return
    if code is None:
        note("could not extract a valid edit from the response — will re-prompt / retry", color=YELLOW)
        return
    if kind == "diff":
        panel("EXTRACTED DIFF", code, color=GREEN, colorize=_color_diff_line)
    else:
        panel("EXTRACTED FUNCTION (rewritten)", code, color=GREEN)


# Human-readable, ordered gate stages.
_GATE_ORDER = ["apply", "compile", "openmp_compile", "tsan", "correctness", "performance"]
_GATE_LABEL = {
    "apply": "apply patch",
    "compile": "compile (sequential)",
    "openmp_compile": "compile (-fopenmp)",
    "tsan": "ThreadSanitizer (data race)",
    "correctness": "correctness (output vs reference)",
    "performance": "measured speedup",
    "accepted": "accepted",
}


def gate_result(passed: bool, stage: str, diagnostic: str = "", measured_speedup: Optional[float] = None) -> None:
    """Render the quality-gate outcome as a checklist: every stage up to the
    failing one passed; the failing one is marked, with its diagnostic."""
    if not _ENABLED:
        return
    color = GREEN if passed else RED
    title = "QUALITY GATE — PASSED" if passed else f"QUALITY GATE — FAILED at '{stage}'"
    lines = []
    reached = True
    for st in _GATE_ORDER:
        label = _GATE_LABEL.get(st, st)
        if not reached:
            lines.append(f"{GREY}  ·  {label}  (not reached){RESET}")
            continue
        if passed or st != stage:
            extra = ""
            if st == "performance" and measured_speedup:
                extra = f"  ({measured_speedup:.2f}×)"
            lines.append(f"{GREEN}  ✓  {label}{extra}{RESET}")
        else:
            lines.append(f"{RED}  ✗  {label}{RESET}")
            reached = False
    if passed and measured_speedup:
        # performance stage may not be in the list if speedup wasn't required
        pass
    body = "\n".join(lines)
    if diagnostic and not passed:
        snippet = diagnostic.strip()
        body += f"\n{DIM}{'─' * 40}{RESET}\n{DIM}diagnostic:{RESET}\n{snippet}"
    panel(title, body, color=color, max_lines=40)
