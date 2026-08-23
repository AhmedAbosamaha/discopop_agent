"""
Asking the model whether a static dependence is real
------------------------------------------------------
Static analysis reports a dependence whenever it cannot prove there is none, so
freshly written code is usually blocked by something that does not happen — and
there is no dynamic data for new code to settle it.

This is the one place a model's claim enters DiscoPoP's analysis, so the question
is kept as narrow as possible: only Do-All BLOCKERS are asked about, only
STATIC-origin ones are eligible, and the model is told to answer REAL when
unsure, since a dependence wrongly called real costs only a missed
parallelization while the reverse produces a racy loop.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

from .. import viz
from ..evidence import load_prevented_deps
from ..profiling import fast_refresh
from ..profiling.tools import _explorer_cmd, _venv_env
from .prompts import _SYSTEM_DEPS
from .providers import _complete, _make_client

if TYPE_CHECKING:                      # imported for typing only — avoids a cycle
    from ..args import AgentArguments


_DEP_VERDICT_RE = re.compile(r"^\s*(\d+)\s*[:.]\s*(REAL|SPURIOUS)\b[\s-]*(.*)$",
                             re.IGNORECASE | re.MULTILINE)


def review_dependences(
    items: List[Dict[str, Any]],
    code: str,
    model: str,
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
    verbose: bool = False,
) -> Dict[int, Tuple[bool, str]]:
    """Ask the model which of these static dependences are real.

    Returns {index: (is_real, reason)}.  An item the model does not answer for
    is absent from the result, and the caller must treat that as REAL — silence
    is not permission.
    """
    if not items:
        return {}

    lines = [
        "Here is the code under review:",
        "",
        "```cpp",
        code,
        "```",
        "",
        f"DiscoPoP reports {len(items)} static dependence(s) blocking "
        f"parallelization of the lines that were just rewritten:",
        "",
    ]
    for i, it in enumerate(items, 1):
        carried = " (loop-carried)" if it.get("loop_carried") else ""
        loop = f", blocking the loop at lines {it['loop']}" if it.get("loop") else ""
        lines.append(
            f"{i}. {it['dep_type']} on `{it['var']}`{carried}{loop}: "
            f"line {it['sink_line']} depends on line {it['source_line']}"
        )
        if it.get("sink_text"):
            lines.append(f"     line {it['sink_line']}: {it['sink_text'].strip()}")
        if it.get("source_text"):
            lines.append(f"     line {it['source_line']}: {it['source_text'].strip()}")
    lines += ["", "Give your verdict for each, one per line."]
    prompt = "\n".join(lines)

    client = _make_client(provider, api_key, api_base)
    if verbose:
        viz.llm_request(model, provider, _SYSTEM_DEPS, prompt, attempt=0)
    text = _complete(provider, client, model,
                     [{"role": "user", "content": prompt}], _SYSTEM_DEPS,
                     session_key="dep-review")
    if verbose:
        viz.llm_response(text, kind="dep verdicts")

    out: Dict[int, Tuple[bool, str]] = {}
    for m in _DEP_VERDICT_RE.finditer(text or ""):
        idx = int(m.group(1))
        if 1 <= idx <= len(items):
            out[idx] = (m.group(2).upper() == "REAL", m.group(3).strip()[:120])
    return out


def _llm_dep_review(
    args: AgentArguments, dp_dir: Path, old_text: str, new_text: str,
    output_dir: Path, file_id: int,
) -> str:
    """--llm-deps: let the model discharge static dependences that block a Do-All.

    Why this exists.  A fast refresh leaves rewritten code covered by STATIC
    dependences only, and static analysis reports a dependence whenever it
    cannot prove there is none.  A freshly written loop is therefore usually
    blocked by something that does not actually happen, with no dynamic data to
    settle it — and since a rewrite CREATES regions, and depth > 0 exists to
    parallelize them, static caution alone would keep them sequential forever.

    Two rules keep the question narrow, and both matter:

      * only DiscoPoP's own Do-All BLOCKERS are reviewed, not every dependence
        in the region.  On example4 the unfiltered version asked about 76
        dependences of which 37 were induction variables and 3 were body-locals
        — things the agent already knows are never blockers.  Asking a model 40
        questions whose answers are already known is how it learns to answer
        carelessly.
      * only STATIC-origin blockers are reviewable.  A dependence DiscoPoP
        actually observed at run time is ground truth and is never up for
        discussion.

    Every judgement is recorded in llm_deps.json.  This is the one place a
    model's claim enters DiscoPoP's analysis, so be plain about the exposure: a
    wrong SPURIOUS produces a racy loop, and what stands behind it is the gate.
    """
    profiler = (dp_dir / "profiler").resolve()
    static_file = profiler / "static_dependencies.txt"
    if not static_file.exists():
        return ""

    lmap = fast_refresh.line_map(old_text, new_text)
    carried_over = set(lmap.values())
    new_lines = new_text.splitlines()
    rewritten = [n for n in range(1, len(new_lines) + 1) if n not in carried_over]
    if not rewritten:
        return "nothing was rewritten — no dependences to review"

    blockers = load_prevented_deps(dp_dir, file_id, min(rewritten), max(rewritten))
    # A dependence that was actually observed is not a candidate for discharge,
    # whatever a model thinks of it.
    blockers = [b for b in blockers
                if "STATIC" in str(b.get("origin", "")).upper()]
    if not blockers:
        return "no static Do-All blockers in the rewritten lines"

    def _ln(v: object) -> "int | None":
        try:
            return int(str(v).split(":")[-1])
        except (TypeError, ValueError):
            return None

    items: List[Dict[str, Any]] = []
    for b in blockers:
        snk, src = _ln(b.get("sink_line")), _ln(b.get("source_line"))
        ls, le = b.get("loop_start"), b.get("loop_end")
        items.append({
            "dep_type": str(b.get("dep_type", "?")).split(".")[-1],
            "var": str(b.get("var_name", "?")),
            "sink_line": snk,
            "source_line": src,
            "sink_text": new_lines[snk - 1] if snk and snk <= len(new_lines) else "",
            "source_text": new_lines[src - 1] if src and src <= len(new_lines) else "",
            "loop": f"{ls}-{le}" if ls is not None else "",
            "loop_carried": snk is not None and src is not None and src >= snk,
        })

    lo = max(min(rewritten) - 3, 1)
    hi = min(max(rewritten) + 3, len(new_lines))
    excerpt = "\n".join(f"{n:4d}  {new_lines[n - 1]}" for n in range(lo, hi + 1))

    try:
        verdicts = review_dependences(
            items, excerpt, args.model, api_key=args.api_key,
            provider=args.provider, api_base=args.api_base, verbose=args.verbose,
        )
    except Exception as e:                      # a review failure must not fail the run
        return f"dependence review unavailable ({str(e)[:60]}) — keeping every blocker"

    # Silence means REAL: an unanswered blocker keeps blocking.
    discharged = [items[i - 1] for i, (real, _r) in verdicts.items() if not real]
    record = [
        {**items[i - 1], "verdict": "REAL" if real else "SPURIOUS", "reason": reason}
        for i, (real, reason) in sorted(verdicts.items())
    ]
    log = output_dir / "llm_deps.json"
    existing = json.loads(log.read_text()) if log.exists() else []
    existing.append({"source": args.source_file, "reviewed": record})
    log.write_text(json.dumps(existing, indent=2))

    if not discharged:
        return f"reviewed {len(items)} static blocker(s) — none discharged"

    # Translate the discharged blockers back into the static dependence lines
    # that produced them, matched on (type, variable, both endpoints).
    fwd, _rev = fast_refresh.load_instruction_keys(
        profiler / "instructionID_to_lineID_mapping.txt"
    )

    def _line_of(token: str) -> "int | None":
        key = fwd.get(token.split("@")[0])
        return key[1] if key else None

    targets = {(d["dep_type"], d["var"], d["sink_line"], d["source_line"])
               for d in discharged}
    raw_lines = static_file.read_text().splitlines()
    keep: List[str] = []
    removed = 0
    for raw in raw_lines:
        f = raw.split()
        if len(f) >= 4 and f[1] == "NOM" and "|" in f[3]:
            src_tok, _, var_part = f[3].partition("|")
            key = (f[2], var_part.split("(")[0], _line_of(f[0]),
                   _line_of(src_tok) if src_tok not in ("*", "0@0") else None)
            if key in targets:
                removed += 1
                continue
        keep.append(raw)

    if not removed:
        return (f"reviewed {len(items)} static blocker(s), {len(discharged)} judged "
                f"spurious, but none matched a dependence line — nothing changed")

    static_file.write_text("\n".join(keep) + "\n")
    r = subprocess.run([_explorer_cmd()], capture_output=True, text=True,
                       cwd=dp_dir.resolve(), env=_venv_env())
    if r.returncode != 0:
        static_file.write_text("\n".join(raw_lines) + "\n")
        return (f"discharged {len(discharged)} blocker(s) but the explorer then "
                f"failed — restored the original analysis")
    return (f"reviewed {len(items)} static blocker(s), discharged {len(discharged)} "
            f"({removed} dependence line(s) removed, recorded in {log.name})")
