#!/usr/bin/env python3
"""Exhibits for the thesis, built from archived runs (`agent/results/`): for each chosen
trial a case-study folder with

  before_after.png/.pdf  BEFORE | AFTER side by side: removed red, added green, parallel
                  regions yellow, a minimap of the whole file, and the counts (lines changed,
                  regions added, candidates kept, restructuring level)
  diff.tex        the change as a LaTeX `lstlisting` (language=diff) — what the thesis includes
  diff.png        the same change rendered as an image (slides, quick look)
  console.png     the agent's console for that trial: the lines that tell the story
                  (ranking, model call, gate stages, verdict) rendered like a terminal
  console.txt     those lines as text
  facts.json      the numbers to quote: the verdict AGAINST DISCOPOP ALONE (the campaign's main
                  comparison, computed by figures.vs_discopop_alone exactly as the statistics
                  compute it), outcome, speedups per thread count, calls, seconds, verification
                  size, integrity digests, run id and trial path
  attempts.md     every candidate the agent built in the trial, in order: phase, region, the
                  gate's verdict and diagnostic, and the patch itself

What the BEFORE | AFTER picture shows is stated on it. A trial that shipped a change shows that
change. A trial that shipped NOTHING shows what it did instead, because "nothing changed" is not
what happened: the program the agent had built before Settle dropped it (rebuilt from the
archived patches), or else the first rewrite the gate rejected, with the gate's diagnostic.

    python3 agent/tools/thesis_material.py --out agent/thesis_material \\
        pilot4:polybench/jacobi-2d-imper/full pilot3:polybench/floyd-warshall/full ...
    python3 agent/tools/thesis_material.py --rebuild          # every exhibit, from its facts.json

A spec is `<run>:<suite>/<kernel>/<arm>[@<rep>][:<label>]`; the first model is taken, rep1 unless given.
Nothing is measured here — every number comes from the archived trial record.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figures  # noqa: E402  — the same pairing and verdicts as the statistics

AGENT_DIR = HERE.parent
RESULTS = AGENT_DIR / "results"
# The lines of an agent log that tell a trial's story, from the ranking on. The start-up banner
# ("Quality gate : …", "→ the run beats DiscoPoP …") is left out: it describes the configuration,
# not what happened, and it used to fill the top of every console picture.
STORY = re.compile(r"┌─|└─|Calling|Quality gate PASSED|gate failed|DiscoPoP now finds|DiscoPoP still finds|"
                   r"DiscoPoP sees|reverting|marginal|Applied to|Dropped \d|^\s+· |\[repair\]|SUMMARY|"
                   r"finished source verified|the finished file|Re-measured|No applicable pattern|"
                   r"already has a pattern|PHASE [AB]|SETTLING|Restructuring not allowed")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# The DiscoPoP-alone baseline of a run that did not carry its own: E10 measured it in a separate
# run (agent/results/_analysis/e10_main_comparison/README.md), and its exhibits are paired with it.
DEFAULT_BASELINES = {"e10": ["e10_dp_alone"]}
RUNTIME_STAGES = ("correctness", "tsan", "schedules")


def _render(lines: List[str], path: Path, title: str, diff: bool = False) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lines = [l.rstrip("\n").replace("\t", "    ")[:150] for l in lines][:70]
    h = 0.19 * (len(lines) + 3)
    fig = plt.figure(figsize=(11.5, max(h, 1.2)), facecolor="#16191d")
    fig.text(0.012, 1 - 0.19 / max(h, 1.2), title, color="#8ea9e6", family="monospace", fontsize=9, va="top", weight="bold")
    for i, l in enumerate(lines):
        color = "#d8dee4"
        if diff:
            color = "#7cc39e" if l.startswith("+") and not l.startswith("+++") else \
                    "#e29468" if l.startswith("-") and not l.startswith("---") else \
                    "#8ea9e6" if l.startswith("@@") else "#aab2ba"
        elif "✗" in l or "FAILED" in l or "Race" in l or "race" in l:
            color = "#e29468"
        elif "✓" in l or "PASSED" in l:
            color = "#7cc39e"
        fig.text(0.012, 1 - (i + 2.2) * 0.19 / max(h, 1.2), l, color=color, family="monospace", fontsize=8, va="top")
    fig.savefig(path, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)


def _changed_file(trial: Path, t: dict) -> tuple:
    """(original text, final text, file name) of the file the trial changed (first one in a project)."""
    if (trial / "original").is_dir():
        names = t.get("files_changed") or []
        if not names:
            return None, None, None
        return ((trial / "original" / names[0]).read_text(errors="replace"),
                (trial / "final" / names[0]).read_text(errors="replace"), names[0])
    o = sorted(trial.glob("original.*"))
    f = sorted(trial.glob("final.*"))
    if not o or not f:
        return None, None, None
    return o[0].read_text(errors="replace"), f[0].read_text(errors="replace"), t.get("source", o[0].name)


def _side_by_side(before: Optional[str], after: Optional[str], fname: Optional[str], trial: Path, t: dict,
                  path: Path, label: str = "AFTER", context: int = 5) -> dict:
    """BEFORE | AFTER, the changed parts of the file only, line numbers kept: removed lines
    red on the left, added lines green on the right, every `#pragma omp` line marked as a
    parallel region, and a minimap of the whole file showing how much of it was touched.
    Returns the counts written into facts.json."""
    import difflib
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    if before is None or after is None or before == after:
        return {}
    a, b = before.splitlines(), after.splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    rows: list = []                       # (left no, left text, left kind, right no, right text, right kind)
    touched_a: set = set()
    touched_b: set = set()
    for group in sm.get_grouped_opcodes(context):
        if rows:
            rows.append((None, "⋯", "gap", None, "⋯", "gap"))
        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for k in range(i2 - i1):
                    rows.append((i1 + k + 1, a[i1 + k], "same", j1 + k + 1, b[j1 + k], "same"))
            else:
                touched_a.update(range(i1, i2)); touched_b.update(range(j1, j2))
                for k in range(max(i2 - i1, j2 - j1)):
                    left: tuple = (i1 + k + 1, a[i1 + k], "del") if i1 + k < i2 else (None, "", "pad")
                    right: tuple = (j1 + k + 1, b[j1 + k], "add") if j1 + k < j2 else (None, "", "pad")
                    rows.append((*left, *right))
    rows = rows[:95]
    cands = []
    cj = trial / "agent_patches" / "candidates.jsonl"
    if cj.exists():
        cands = [json.loads(l) for l in cj.read_text().splitlines() if l.strip()]
    depth = max([c.get("depth") or 0 for c in cands if c.get("passed")] or [0])
    pragmas_after = [i for i, l in enumerate(b) if "#pragma omp" in l]
    # What KIND of change this is, stated rather than left to the reader to infer from a
    # line count. A pragma is not a restructuring, and neither is a comment the model wrote to
    # explain itself: on `2mm` and `lu` every "added line" beyond the pragmas is commentary.
    # Counting those as changed code overstated the agent's work in the first exhibits.
    def _code_lines(lines: List[str]) -> Set[int]:
        """Indices of lines that carry code — block comments tracked across lines, because a
        model explains itself in multi-line `/* ... */`, whose middle lines start with a word
        and were being counted as restructuring (`lu`, `2mm`)."""
        out: Set[int] = set()
        in_block = False
        for i, line in enumerate(lines):
            rest, code = line, ""
            while rest:
                if in_block:
                    end = rest.find("*/")
                    if end < 0:
                        rest = ""
                    else:
                        rest, in_block = rest[end + 2:], False
                    continue
                start = rest.find("/*")
                line_cmt = rest.find("//")
                if line_cmt >= 0 and (start < 0 or line_cmt < start):
                    code += rest[:line_cmt]
                    break
                if start < 0:
                    code += rest
                    break
                code += rest[:start]
                rest, in_block = rest[start + 2:], True
            if code.strip() and "#pragma" not in code:
                out.add(i)
        return out

    code_a, code_b = _code_lines(a), _code_lines(b)
    code_added = len(touched_b & code_b)
    code_removed = len(touched_a & code_a)
    kind = ("restructuring" if (code_added or code_removed)
            else "annotation" if len(pragmas_after) > len([l for l in a if "#pragma omp" in l])
            else "unchanged")
    facts = {"file": fname, "change_kind": kind,
             "code_lines_added": code_added, "code_lines_removed": code_removed,
             "lines_before": len(a), "lines_after": len(b), "lines_removed": len(touched_a),
             "lines_added": len(touched_b),
             # the SHIPPED program's count comes from the trial record; any other program shown is counted
             "pragmas_added": (t.get("pragmas_added", len(pragmas_after)) if label == "AFTER"
                               else len(pragmas_after) - sum(1 for l in a if "#pragma omp" in l)),
             "candidates_judged": len(cands), "candidates_kept": sum(1 for c in cands if c.get("passed")),
             "rejected_at": sorted({c.get("stage") for c in cands if not c.get("passed")}),
             "deepest_restructuring_level_kept": depth}
    BG, INK, DIM = "#16191d", "#d8dee4", "#6f7a85"
    COL = {"del": "#4a2a20", "add": "#1f3d31", "pad": "#1b1f24", "same": BG, "gap": BG}
    n = len(rows)
    lh = 0.185
    H = lh * (n + 7)
    fig = plt.figure(figsize=(15.5, max(H, 2.0)), facecolor=BG)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    y0 = 1 - 4.6 * lh / H
    ax.text(0.012, 1 - 1.0 * lh / H, f"{t['benchmark']} · {fname} · {t['arm']} · {t['model']} · {t['outcome']}"
            + ("" if label == "AFTER" else f"   ·   RIGHT = {label}"),
            color="#8ea9e6", family="monospace", fontsize=10, weight="bold", va="top")
    ax.text(0.012, 1 - 2.2 * lh / H,
            f"−{facts['lines_removed']} / +{facts['lines_added']} lines of {len(a)}   ·   {facts['pragmas_added']} parallel region(s) added"
            f"   ·   {facts['candidates_kept']} of {facts['candidates_judged']} candidate(s) kept"
            f"   ·   {kind.upper()}"
            + (f" ({code_added} code line(s) added, {code_removed} removed)" if kind == "restructuring" else "")
            + f"   ·   restructuring level {depth}",
            color=INK, family="monospace", fontsize=8.5, va="top")
    ax.text(0.03, y0 + 0.2 * lh / H, "BEFORE", color=DIM, family="monospace", fontsize=8, weight="bold")
    ax.text(0.50, y0 + 0.2 * lh / H, label.split(" (")[0].upper()[:60], color=DIM, family="monospace",
            fontsize=8, weight="bold")
    for idx, (ln, lt, lk, rn, rt, rk) in enumerate(rows):
        y = y0 - (idx + 1) * lh / H
        for x, w, kind, no, text in ((0.012, 0.462, lk, ln, lt), (0.482, 0.462, rk, rn, rt)):
            ax.add_patch(Rectangle((x, y - 0.12 * lh / H), w, lh / H, color=COL[kind], lw=0))
            is_pragma = "#pragma omp" in text
            if is_pragma and kind in ("add", "same"):
                ax.add_patch(Rectangle((x, y - 0.12 * lh / H), 0.004, lh / H, color="#e6c45c", lw=0))
            ax.text(x + 0.006, y, f"{no:>4}" if no else "    ", color=DIM, family="monospace", fontsize=7.2, va="bottom")
            color = "#e6c45c" if is_pragma else ("#e29468" if kind == "del" else "#9fe0bd" if kind == "add" else
                                                 DIM if kind == "gap" else INK)
            ax.text(x + 0.036, y, text.replace("\t", "    ")[:78], color=color, family="monospace", fontsize=7.2, va="bottom")
    # minimap of the whole AFTER file: where the change sits, and where parallel regions now are
    mx, mw, top, bot = 0.958, 0.03, y0, y0 - n * lh / H
    ax.add_patch(Rectangle((mx, bot), mw, top - bot, color="#20262c", lw=0))
    for i in range(len(b)):
        yy = top - (i + 1) / max(len(b), 1) * (top - bot)
        if i in touched_b:
            ax.add_patch(Rectangle((mx, yy), mw, (top - bot) / max(len(b), 1) + 0.0008, color="#2f8f63", lw=0))
        if i in pragmas_after:
            ax.add_patch(Rectangle((mx, yy), mw, (top - bot) / max(len(b), 1) + 0.0015, color="#e6c45c", lw=0))
    ax.text(mx, top + 0.2 * lh / H, "file", color=DIM, family="monospace", fontsize=7)
    ax.text(0.012, 0.6 * lh / H, "red = removed   green = added   yellow = parallel region (#pragma omp)   right strip = the whole file: "
            "green where changed, yellow where a parallel region now is", color=DIM, family="monospace", fontsize=7)
    fig.savefig(path, dpi=170, facecolor=BG)
    fig.savefig(path.with_suffix(".pdf"), facecolor=BG)
    plt.close(fig)
    return facts


def _apply(text: str, name: str, patches: List[Path]) -> Tuple[str, List[str]]:
    """`text` with `patches` applied in order, and the names of those that did not apply.

    `--forward --force`: Apple's patch otherwise REVERSES a patch that looks already applied, on
    its own, and reports success. A patch that leaves the file unchanged counts as not applied."""
    skipped: List[str] = []
    with tempfile.TemporaryDirectory(prefix="exhibit_") as tmp:
        f = Path(tmp) / name
        f.write_text(text)
        for p in patches:
            prev = f.read_text()
            r = subprocess.run(["patch", "-p0", "-F0", "--forward", "--force", "--silent", str(f), str(p)],
                               capture_output=True, text=True, cwd=tmp, stdin=subprocess.DEVNULL)
            if r.returncode != 0 or f.read_text() == prev:
                f.write_text(prev)
                skipped.append(p.name)
            for junk in Path(tmp).glob(name + ".*"):
                junk.unlink()
        return f.read_text(), skipped


def _candidates(trial: Path) -> List[dict]:
    cj = trial / "agent_patches" / "candidates.jsonl"
    return [json.loads(l) for l in cj.read_text().splitlines() if l.strip()] if cj.exists() else []


def _built_program(trial: Path, original: str, name: str, cands: List[dict]) -> Tuple[str, List[str]]:
    """The most complete program the agent built: its KEPT rewrites (the `region_*_tier2.patch`
    files the agent writes when a rewrite is accepted, in the order they were accepted) and every
    DiscoPoP pragma that passed the gate on them. What Settle judged, whatever it then did."""
    ap = trial / "agent_patches"
    kept = {p.name[len("region_"):-len("_tier2.patch")].replace("_", ":", 1): p for p in ap.glob("region_*_tier2.patch")}
    order = {c.get("region_id"): i for i, c in enumerate(cands) if c.get("phase") == "A" and c.get("passed")}
    rewrites = [kept[r] for r in sorted(kept, key=lambda r: order.get(r, 10**6))]
    pragmas = [ap / c["patch"] for c in cands if c.get("phase") == "B" and c.get("passed") and c.get("patch")]
    return _apply(original, name, rewrites + pragmas)


def _what_happened(log_lines: List[str]) -> List[str]:
    """Phase B's verdict on each pragma and Settle's list of what it dropped, as the log says it."""
    out: List[str] = []
    for i, l in enumerate(log_lines):
        s_ = l.strip()
        if s_.startswith("┌─ pattern #"):
            verdict = next((x.strip() for x in log_lines[i + 1:i + 12] if x.strip().startswith("└─")), "")
            marg = next((x.strip("│ ").strip() for x in log_lines[i + 1:i + 12] if "marginal" in x or "gate failed" in x), "")
            out.append(f"{s_[3:]}: {verdict[3:]}" + (f" ({marg[:90]})" if marg else ""))
        elif s_.startswith("· ") or s_.startswith("Dropped ") or s_.startswith("[repair]"):
            out.append(s_[:160])
    return out


def _main_comparison(run: str, t: dict, baseline_runs: List[str]) -> dict:
    """The verdict of this trial against DiscoPoP alone, by `figures.vs_discopop_alone` — the
    function the campaign's statistics use — over the DiscoPoP-alone trials of its benchmark in
    its own run, or in the named baseline runs when its run has none."""
    bench = str(t["benchmark"])
    trials: List[dict] = []
    for r in [run, *baseline_runs]:
        for p in sorted((RESULTS / r / "benchmarks" / bench).glob("*/*/rep*/trial.json")):
            x = json.loads(p.read_text())
            x.setdefault("run_id", r)
            if r != run and x.get("arm") != figures.BASELINE_ARM:
                continue
            trials.append(x)
    rows = [row for row in figures.vs_discopop_alone(trials)
            if row["run_id"] == run and row["arm"] == t.get("arm") and row["repeat"] == t.get("repeat")
            and row["model"] == t.get("model")]
    if not rows:
        return {"verdict": "—"}
    keep = ("verdict", "class", "dp_alone_trials", "dp_alone_outcomes", "dp_alone_speedup_vs_seq",
            "agent_outcome", "agent_speedup_vs_seq", "agent_vs_dp_alone", "timing_comparable")
    out = {k: rows[0].get(k) for k in keep}
    out["baseline_runs"] = sorted({str(x["run_id"]) for x in trials if x.get("arm") == figures.BASELINE_ARM})
    return out


def _attempts_md(t: dict, trial: Path, cands: List[dict]) -> str:
    lines = [f"# Every candidate of {t['benchmark']} · {t['arm']} · rep{t.get('repeat')} ({trial.relative_to(RESULTS)})", "",
             "In the order the agent built them. `passed` = the gate accepted it; what happened to it after "
             "(kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.", ""]
    for i, c in enumerate(cands, 1):
        verdict = "passed the gate" if c.get("passed") else f"rejected at `{c.get('stage')}`"
        lines.append(f"## {i}. Phase {c.get('phase')} · region {c.get('region_id')}"
                     + (f" · {c.get('pattern_type')}" if c.get("pattern_type") else "") + f" — {verdict}")
        diag = (c.get("diagnostic") or "").strip()
        if diag:
            lines += ["", "```", *[d[:160] for d in diag.splitlines()[:6]], "```"]
        pf = trial / "agent_patches" / str(c.get("patch") or "")
        if c.get("patch") and pf.exists():
            body = pf.read_text(errors="replace").splitlines()
            lines += ["", "```diff", *body[:80], *(["… (truncated)"] if len(body) > 80 else []), "```"]
        lines.append("")
    return "\n".join(lines) + "\n"


def build(run: str, trial: Path, label: str, out: Path, baseline_runs: Optional[List[str]] = None) -> Path:
    t = json.loads((trial / "trial.json").read_text())
    d = out / label
    d.mkdir(parents=True, exist_ok=True)
    for stale in ("before_after.png", "before_after.pdf", "diff.tex", "diff.png", "attempts.md",
                  "rejected_attempt.png", "rejected_attempt.pdf", "rejected_attempt.tex"):
        (d / stale).unlink(missing_ok=True)
    v = t.get("verify", {})
    baselines = list(baseline_runs if baseline_runs is not None else DEFAULT_BASELINES.get(run, []))
    facts = {"run": run, "trial": str(trial.relative_to(RESULTS)), "benchmark": t["benchmark"], "arm": t["arm"],
             "model": t["model"], "repeat": t.get("repeat"), "outcome": t["outcome"],
             "vs_discopop_alone": _main_comparison(run, t, baselines),
             "llm_calls": t.get("llm_calls"), "agent_s": t.get("agent_s"),
             "verify_size": v.get("verify_size"), "verify_status": v.get("status"),
             "seq_kernel_s": v.get("seq_kernel_median_s"),
             "kernel_speedup_by_threads": {k: p.get("kernel_speedup") for k, p in (v.get("par") or {}).items()},
             "dump_max_rel_err": v.get("dump_max_rel_err"), "dump_seeded_max_rel_err": v.get("dump_seeded_max_rel_err"),
             "pragmas_discopop": t.get("pragmas_discopop"), "pragmas_llm": t.get("pragmas_llm"),
             "rewrites_kept": t.get("rewrites_kept"), "scaffold_ok": (t.get("scaffold") or {}).get("ok"),
             "package_integrity_ok": ((t.get("package_integrity") or {}).get("after") or {}).get("ok")}
    before, after, fname = _changed_file(trial, t)
    if before is None and (trial / "original").is_dir():
        # A project whose files did not change: the benchmark's own file is the one the agent
        # worked on (`source` in the trial record).
        src = t.get("source")
        if src and (trial / "original" / src).exists():
            before = after = (trial / "original" / src).read_text(errors="replace")
            fname = src
    cands = _candidates(trial)
    log = trial / "agent.log"
    log_lines = [ANSI.sub("", l) for l in log.read_text(errors="replace").splitlines()] if log.exists() else []
    facts["change"] = _side_by_side(before, after, fname, trial, t, d / "before_after.png")
    shown: Dict[str, object] = {"what": "the final program" if facts["change"] else "nothing: the final program is the original"}
    diff_text = (trial / "changes.diff").read_text(errors="replace") if (trial / "changes.diff").exists() else ""
    after_text = after                       # the program the picture's right side shows
    if not facts["change"] and before is not None and fname and cands:
        built, skipped = _built_program(trial, before, fname, cands)
        runtime_rejects = [c for c in cands if not c.get("passed") and c.get("stage") in RUNTIME_STAGES and c.get("patch")]
        if built != before:
            label_ = "the program the agent built, then dropped (never shipped)"
            shown = {"what": label_, "rebuilt_from": "agent_patches: kept rewrites + gate-passed pragmas",
                     "patches_not_applicable": skipped, "what_happened": _what_happened(log_lines)}
            shown["change"] = _side_by_side(before, built, fname, trial, t, d / "before_after.png", label_)
            after_text = built
        elif runtime_rejects:
            c = runtime_rejects[0]
            tried, skipped = _apply(before, fname, [trial / "agent_patches" / str(c["patch"])])
            label_ = f"a rewrite the gate rejected at '{c.get('stage')}'"
            shown = {"what": label_, "attempt": cands.index(c) + 1, "of": len(cands),
                     "diagnostic": (c.get("diagnostic") or "").strip().splitlines()[:3],
                     "rejected_attempts": {st: sum(1 for x in cands if not x.get("passed") and x.get("stage") == st)
                                           for st in RUNTIME_STAGES},
                     "patches_not_applicable": skipped}
            shown["change"] = _side_by_side(before, tried, fname, trial, t, d / "before_after.png", label_)
            after_text = tried
        else:
            after_text = before
        if after_text != before:
            import difflib
            diff_text = "".join(difflib.unified_diff(before.splitlines(True), after_text.splitlines(True),
                                                     f"original/{fname}", f"shown/{fname}"))
    # A trial in which the gate caught wrong rewrites gets that shown too, whatever else it shows:
    # the first one rejected at a runtime stage, with the gate's own diagnostic.
    rejects = [c for c in cands if not c.get("passed") and c.get("stage") in RUNTIME_STAGES and c.get("patch")]
    if rejects and before is not None and fname:
        c = rejects[0]
        tried, _sk = _apply(before, fname, [trial / "agent_patches" / str(c["patch"])])
        if tried == before and after_text not in (None, before):
            # a later attempt, made against a rewrite that was kept at the time
            tried, _sk = _apply(str(after_text), fname, [trial / "agent_patches" / str(c["patch"])])
        if tried != before:
            lab = f"attempt {cands.index(c) + 1} of {len(cands)}, rejected by the gate at '{c.get('stage')}'"
            _side_by_side(before, tried, fname, trial, t, d / "rejected_attempt.png", lab)
            import difflib
            rd = "".join(difflib.unified_diff(before.splitlines(True), tried.splitlines(True),
                                              f"original/{fname}", f"rejected/{fname}"))
            diag = " / ".join((c.get("diagnostic") or "").strip().splitlines()[:2]).replace("{", "(").replace("}", ")")
            (d / "rejected_attempt.tex").write_text(
                "\\begin{lstlisting}[language=diff,basicstyle=\\ttfamily\\scriptsize,breaklines=true,"
                f"caption={{{t['benchmark']} — {lab}: {diag[:160]}}}]\n" + rd + "\\end{lstlisting}\n")
            shown["rejected_attempt"] = {"attempt": cands.index(c) + 1, "of": len(cands), "stage": c.get("stage"),
                                         "diagnostic": (c.get("diagnostic") or "").strip().splitlines()[:3],
                                         "rejected_at": {st: sum(1 for x in cands if not x.get("passed")
                                                                 and x.get("stage") == st) for st in RUNTIME_STAGES}}
    facts["shown"] = shown
    (d / "facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    if diff_text:
        cap = f"{t['benchmark']} — {t['outcome']} ({run})" + ("" if shown["what"] == "the final program"
                                                              else f" — shown: {shown['what']}")
        (d / "diff.tex").write_text("\\begin{lstlisting}[language=diff,basicstyle=\\ttfamily\\scriptsize,breaklines=true,"
                                    f"caption={{{cap}}}]\n" + diff_text + "\\end{lstlisting}\n")
        _render(diff_text.splitlines(), d / "diff.png", cap, diff=True)
    if cands:
        (d / "attempts.md").write_text(_attempts_md(t, trial, cands))
    if log_lines:
        story: List[str] = []
        if any("Initial candidates" in l for l in log_lines):
            i = next(k for k, l in enumerate(log_lines) if "Initial candidates" in l)
            for l in log_lines[i:i + 14]:
                if story and not l.strip():
                    break
                if l.strip() and not set(l.strip()) <= set("-="):
                    story.append(l)
        start = next((k for k, l in enumerate(log_lines) if "PHASE A" in l), 0)
        story += [l for l in log_lines[start:] if STORY.search(l) and len(l.strip()) > 3
                  and not set(l.strip()) <= set("=-")]
        (d / "console.txt").write_text("\n".join(story) + "\n")
        _render(story, d / "console.png", f"agent console — {t['benchmark']} ({run})")
    return d


def build_spec(spec: str, out: Path, baseline_runs: Optional[List[str]] = None) -> Path:
    run, rest = spec.split(":", 1)
    path, _, label = rest.partition(":")
    # `<suite>/<kernel>/<arm>@3` names a repeat other than the first.
    path, _, rep = path.partition("@")
    arm_dir = RESULTS / run / "benchmarks" / path
    trials = sorted(arm_dir.glob(f"*/rep{rep or 1}"))
    if not trials:
        raise SystemExit(f"no trial under {arm_dir}")
    return build(run, trials[0], label or f"{run}_{path.replace('/', '_')}", out, baseline_runs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(AGENT_DIR / "thesis_material"))
    ap.add_argument("--baseline-runs", default=None,
                    help="comma-separated runs holding the DiscoPoP-alone trials when the exhibit's own run has none")
    ap.add_argument("--rebuild", action="store_true", help="rebuild every exhibit in --out from its facts.json")
    ap.add_argument("specs", nargs="*")
    a = ap.parse_args()
    out = Path(a.out)
    baselines = [r for r in a.baseline_runs.split(",") if r] if a.baseline_runs else None
    for spec in a.specs:
        d = build_spec(spec, out, baselines)
        print(f"{spec} -> {d}")
    if a.rebuild:
        for fp in sorted(out.glob("*/facts.json")):
            f = json.loads(fp.read_text())
            kept = (f.get("vs_discopop_alone") or {}).get("baseline_runs")
            runs = [r for r in (kept or []) if r != f["run"]] or None
            d = build(f["run"], RESULTS / f["trial"], fp.parent.name, out, runs)
            print(f"rebuilt {d.name}")
    index = ["# Thesis material — case studies", "",
             "Built by `agent/tools/thesis_material.py` from the archived runs; every number is in "
             "`facts.json`. Grouped by what the agent actually DID, because that is the question a "
             "reader asks first and a line count does not answer it: a pragma is not a "
             "restructuring, and neither is a comment the model wrote to explain itself.", "",
             "Every line leads with the verdict against **DiscoPoP alone** — the campaign's main "
             "comparison, computed as the statistics compute it — then the program speedups over the "
             "sequential original (DiscoPoP alone → agent). Where the shipped program is the original, "
             "the exhibit shows what the agent did instead, and says so.", ""]
    groups: Dict[str, List[str]] = {"restructuring": [], "annotation": [], "unchanged": []}
    for d in sorted(p for p in out.iterdir() if p.is_dir()):
        fp = d / "facts.json"
        if not fp.exists():
            continue
        f = json.loads(fp.read_text())
        c = f.get("change") or {}
        kind = c.get("change_kind", "unchanged")
        detail = (f"code +{c.get('code_lines_added', 0)}/−{c.get('code_lines_removed', 0)}, "
                  f"{c.get('pragmas_added', 0)} pragma(s)" if kind == "restructuring"
                  else f"{c.get('pragmas_added', 0)} pragma(s), no code changed" if kind == "annotation"
                  else "nothing changed")
        mc = f.get("vs_discopop_alone") or {}
        def _x(v: object) -> str:
            return f"{v:.2f}×" if isinstance(v, (int, float)) else "1.00×" if v is None else str(v)
        vs = ("no DiscoPoP-alone trial to pair with" if mc.get("verdict") in (None, "—", "no-baseline")
              else f"vs DiscoPoP alone: **{mc['verdict']}** ({_x(mc.get('dp_alone_speedup_vs_seq'))} → "
                   f"{_x(mc.get('agent_speedup_vs_seq'))})")
        sh = f.get("shown") or {}
        what = "" if sh.get("what") in (None, "the final program") else f" · shows: {sh['what']}"
        groups.setdefault(kind, []).append(
            f"- **{d.name}** — {f['benchmark']}, `{f['arm']}` ({f['run']}, rep {f.get('repeat', 1)}) · {vs} · "
            f"{f['outcome']}, {detail}{what} · {f['llm_calls']} call(s), {f['agent_s']} s")
    titles = {"restructuring": "## The agent changed the code",
              "annotation": "## The agent only added pragmas",
              "unchanged": "## The agent changed nothing (declined)"}
    for kind in ("restructuring", "annotation", "unchanged"):
        if groups.get(kind):
            index += [titles[kind], ""] + groups[kind] + [""]
    (out / "INDEX.md").write_text("\n".join(index) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
