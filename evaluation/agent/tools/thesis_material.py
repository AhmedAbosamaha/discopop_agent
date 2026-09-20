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
  facts.json      the numbers to quote: outcome, speedups per thread count, calls, seconds,
                  verification size, integrity digests, run id and trial path

    python3 agent/tools/thesis_material.py --out agent/thesis_material \\
        pilot4:polybench/jacobi-2d-imper/full pilot3:polybench/floyd-warshall/full ...

A spec is `<run>:<suite>/<kernel>/<arm>[:<label>]`; the first model and rep1 are taken.
Nothing is measured here — every number comes from the archived trial record.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import List

AGENT_DIR = Path(__file__).resolve().parents[1]
RESULTS = AGENT_DIR / "results"
KEEP = re.compile(r"Region ID|Tier-2\]|Quality gate|✓|✗|stage|SUMMARY|Race detected|data race|"
                  r"semantically|rejected|reverted|kept|Phase [AB]|Settle|speedup|DiscoPoP now finds|→")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


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


def _side_by_side(trial: Path, t: dict, path: Path, context: int = 5) -> dict:
    """BEFORE | AFTER, the changed parts of the file only, line numbers kept: removed lines
    red on the left, added lines green on the right, every `#pragma omp` line marked as a
    parallel region, and a minimap of the whole file showing how much of it was touched.
    Returns the counts written into facts.json."""
    import difflib
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    before, after, fname = _changed_file(trial, t)
    if before is None or before == after:
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
    facts = {"file": fname, "lines_before": len(a), "lines_after": len(b), "lines_removed": len(touched_a),
             "lines_added": len(touched_b), "pragmas_added": t.get("pragmas_added", len(pragmas_after)),
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
    ax.text(0.012, 1 - 1.0 * lh / H, f"{t['benchmark']} · {fname} · {t['arm']} · {t['model']} · {t['outcome']}",
            color="#8ea9e6", family="monospace", fontsize=10, weight="bold", va="top")
    ax.text(0.012, 1 - 2.2 * lh / H,
            f"−{facts['lines_removed']} / +{facts['lines_added']} lines of {len(a)}   ·   {facts['pragmas_added']} parallel region(s) added"
            f"   ·   {facts['candidates_kept']} of {facts['candidates_judged']} candidate(s) kept"
            f"   ·   restructuring level {depth}", color=INK, family="monospace", fontsize=8.5, va="top")
    ax.text(0.03, y0 + 0.2 * lh / H, "BEFORE", color=DIM, family="monospace", fontsize=8, weight="bold")
    ax.text(0.50, y0 + 0.2 * lh / H, "AFTER", color=DIM, family="monospace", fontsize=8, weight="bold")
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


def build(spec: str, out: Path) -> Path:
    run, rest = spec.split(":", 1)
    path, _, label = rest.partition(":")
    arm_dir = RESULTS / run / "benchmarks" / path
    trials = sorted(arm_dir.glob("*/rep1"))
    if not trials:
        raise SystemExit(f"no trial under {arm_dir}")
    trial = trials[0]
    t = json.loads((trial / "trial.json").read_text())
    name = label or f"{run}_{path.replace('/', '_')}"
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    v = t.get("verify", {})
    facts = {"run": run, "trial": str(trial.relative_to(RESULTS)), "benchmark": t["benchmark"], "arm": t["arm"],
             "model": t["model"], "outcome": t["outcome"], "llm_calls": t.get("llm_calls"), "agent_s": t.get("agent_s"),
             "verify_size": v.get("verify_size"), "verify_status": v.get("status"),
             "seq_kernel_s": v.get("seq_kernel_median_s"),
             "kernel_speedup_by_threads": {k: p.get("kernel_speedup") for k, p in (v.get("par") or {}).items()},
             "dump_max_rel_err": v.get("dump_max_rel_err"), "dump_seeded_max_rel_err": v.get("dump_seeded_max_rel_err"),
             "pragmas_discopop": t.get("pragmas_discopop"), "pragmas_llm": t.get("pragmas_llm"),
             "rewrites_kept": t.get("rewrites_kept"), "scaffold_ok": (t.get("scaffold") or {}).get("ok"),
             "package_integrity_ok": ((t.get("package_integrity") or {}).get("after") or {}).get("ok")}
    facts["change"] = _side_by_side(trial, t, d / "before_after.png")
    (d / "facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    diff_file = trial / "changes.diff"
    if diff_file.exists():
        diff = diff_file.read_text(errors="replace")
        (d / "diff.tex").write_text("\\begin{lstlisting}[language=diff,basicstyle=\\ttfamily\\scriptsize,breaklines=true,"
                                    f"caption={{{t['benchmark']} — {t['outcome']} ({run})}}]\n" + diff + "\\end{lstlisting}\n")
        _render(diff.splitlines(), d / "diff.png", f"{t['benchmark']} · {t['arm']} · {t['model']} · {t['outcome']}", diff=True)
    log = trial / "agent.log"
    if log.exists():
        lines = [ANSI.sub("", l) for l in log.read_text(errors="replace").splitlines()]
        story = [l for l in lines if KEEP.search(l) and len(l.strip()) > 3]
        (d / "console.txt").write_text("\n".join(story) + "\n")
        _render(story, d / "console.png", f"agent console — {t['benchmark']} ({run})")
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(AGENT_DIR / "thesis_material"))
    ap.add_argument("specs", nargs="+")
    a = ap.parse_args()
    out = Path(a.out)
    for spec in a.specs:
        d = build(spec, out)
        print(f"{spec} -> {d}")
    index = ["# Thesis material — case studies", "",
             "Built by `agent/tools/thesis_material.py` from the archived runs; every number is in `facts.json`.", ""]
    for d in sorted(p for p in out.iterdir() if p.is_dir()):
        f = json.loads((d / "facts.json").read_text())
        index.append(f"- **{d.name}** — {f['benchmark']}, `{f['arm']}`, {f['model']}: **{f['outcome']}**, "
                     f"kernel speedup {f['kernel_speedup_by_threads']}, {f['llm_calls']} call(s), {f['agent_s']} s")
    (out / "INDEX.md").write_text("\n".join(index) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
