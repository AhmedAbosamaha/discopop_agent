#!/usr/bin/env python3
"""Replay the order statement on archived profiles — before a rule is changed, and as its truth table.

The order statement (`discopop_agent/llm/render.order_statement`: "the loop holding line 7 has to run
completely before the loop holding line 6") is what E2-V3's and E2-O3's results rest on. T0.16 (4 Oct 2026)
found its rule unreliable where two statements also feed each other the other way, and the record requires
that no rule is changed on reasoning alone: every candidate is replayed on the screen's 86 profiles
(`results/T0_instruments/T0.16_clean_layout/preflight/screen_profiles.tar.gz`: 43 loops, packaging v4 and
the clean two-file layout) and compared with the ground truth written down below by reading each loop.

No model, no profiling: the archive holds the profiler's and the explorer's files; the agent's own
`build_candidates`, `assemble` and `order_statement` are run on them, per prompt version.

    venv/bin/python evaluation/agent/tools/order_replay.py <screen_profiles.tar.gz | directory> [--md OUT.md]

Exit status 1 when a version that is checked (`--check 4`, the default) disagrees with the ground truth.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from discopop_agent import project as project_mod                 # noqa: E402
from discopop_agent.args import parse_args                         # noqa: E402
from discopop_agent.evidence import assemble                       # noqa: E402
from discopop_agent.llm.prompts import PROMPT_VERSIONS             # noqa: E402
from discopop_agent.llm.render import order_statement              # noqa: E402
from discopop_agent.plan import build_candidates                   # noqa: E402
from discopop_agent.plan import impact as impact_mod               # noqa: E402

# What is TRUE of each loop, from reading it — per pair of statements of the loop under study:
#   ("order", first, second)  the loop holding `first` has to run completely before the loop holding `second`
#                             (a value flows first -> second between iterations, nothing flows back inside one
#                             activation, and `second` reads no element `first` overwrites later in it)
#   ("mutual", a, b)          values flow both ways inside one activation: no split between them
# A loop that is absent, or has an empty list, admits NO statement. Statements are named by a fragment of
# their text. Only loops with two statements that exchange array values can have an entry.
TRUTH: Dict[str, List[Tuple[str, str, str]]] = {
    # the constructed kernels: S1 `u[..] += v[..] * c[i]`, S2 `v[..] = u[..] * d[i] + c[i]` (k17, k42: `v[..] += u[..] * d[i]`)
    "k17": [("order", "v[jv[i]] +=", "u[ju[i]] +=")],     # X: S1 reads the v element S2 wrote one iteration earlier
    "k19": [("order", "v[jv[i]] =", "u[ju[i]] +=")],
    "k23": [("order", "v[i] = x[i]", "u[i] += w[i]")],
    "k31": [("order", "v[i] = u[i + far]", "u[i] += v[i + off]")],
    "k36": [("order", "v[i] = AT2", "u[i] += AT1")],
    "k42": [("order", "u[ju[i]] +=", "v[jv[i]] +=")],     # Y: S2 reads the u element S1 wrote one iteration earlier
    "k48": [("order", "u[ju[i]] +=", "v[jv[i]] =")],
    # ORDER-4 (4 Oct). k27, the chain: S3 reads the v element S2 wrote one iteration earlier, S1 the w element S3
    # wrote one iteration earlier — two orders, S2 before S3 before S1. k53, the cycle: k19's text, but S2 reads
    # the u element S1 wrote in the SAME iteration while S1 reads the v element S2 wrote one iteration earlier
    "k27": [("order", "v[jv[i]] = u[ku[i]]", "w[jw[i]] = v[kv[i]]"), ("order", "w[jw[i]] = v[kv[i]]", "u[ju[i]] += w[kw[i]]")],
    "k53": [("mutual", "u[ju[i]] +=", "v[jv[i]] =")],
    # s211: a[i] = b[i-1] + c[i]*d[i]; b[i] = b[i+1] - e[i]*d[i] — S1 reads the b element S2 wrote one iteration
    # earlier; S2 reads nothing S1 writes
    "s211": [("order", "b[i] = b[i + 1]", "a[i] = b[i - 1]")],
    # s1213: a[i] = b[i-1]+c[i]; b[i] = a[i+1]*d[i] — the same flow on b; S2 reads a[i+1] BEFORE S1 writes it
    # (an old value: the previous repetition's), which the order "S2's loop first" keeps
    "s1213": [("order", "b[i] = a[i+1]", "a[i] = b[i-1]")],
    # s323: a[i] = b[i-1] + c[i]*d[i]; b[i] = a[i] + c[i]*e[i] — S2 reads the a element S1 wrote in the SAME
    # iteration and S1 the b element S2 wrote one iteration earlier: a true recurrence
    "s323": [("mutual", "a[i] = b[i-1]", "b[i] = a[i]")],
    # s161: `if (b[i] < 0) c[i+1] = a[i] + d[i]*d[i]; else a[i] = c[i] + d[i]*e[i];` with b negative at every
    # odd i (the harness's data): the c statement runs at odd i and writes c[i+1], which the a statement reads
    # one iteration later; the a statement writes even elements only, which the c statement never reads
    "s161": [("order", "c[i+1] = a[i]", "a[i] = c[i]")],
    # s281: x = a[LEN_1D-i-1] + b[i]*c[i]; a[i] = x-1.0; b[i] = x — the first statement reads a elements the
    # second wrote in earlier iterations (the upper half), and the second reads x of the same iteration
    "s281": [("mutual", "x = a[LEN_1D-i-1]", "a[i] = x-")],
}


def _extract(src: Path, dest: Path) -> Path:
    """The profiles as directories under `dest`, every FileMapping.txt pointing at the copy."""
    if src.is_dir():
        root = src
    else:
        with tarfile.open(src) as tar:
            tar.extractall(dest)
        root = next(p for p in dest.iterdir() if p.is_dir())
    for d in sorted(root.iterdir()):
        fm = d / ".discopop" / "FileMapping.txt"
        if not fm.exists():
            continue
        lines = []
        for raw in fm.read_text().splitlines():
            fid, _, path = raw.partition("\t") if "\t" in raw else raw.partition(" ")
            name = Path(path.strip()).name
            inside = d / name
            lines.append(f"{fid}\t{inside if inside.exists() else path.strip()}")
        fm.write_text("\n".join(lines) + "\n")
    return root


def _statements(work: Path, name: str, version: int) -> Dict[str, Any]:
    """The order statement of every candidate of the loop under study, under one prompt version: a set of
    ("order", first text, second text, variable) and ("mutual", text, text)."""
    dp = work / ".discopop"
    project = (work / "main.c").exists()
    project_mod.activate(None)
    if project:
        units = [f"{name}.c", "main.c"]
        project_mod.activate(project_mod.Project.discover(work, units=units, include_dirs=["."],
                                                          editable=[f"{name}.c"]))
        project_mod.set_focus(str(work / f"{name}.c"))
        argv = ["--project-dir", str(work), "--project-units", ",".join(units), "--project-include", ".",
                "--project-editable", f"{name}.c"]
    else:
        argv = ["--source-file", str(work / f"{name}.c")]
    old = sys.argv
    sys.argv = ["x", "--discopop-dir", str(dp), *argv, "--exclude-functions", "main,pb_mix",
                "--min-runtime-share", "0.01", "--prompt-version", str(version)]
    try:
        args = parse_args()
    finally:
        sys.argv = old
    try:
        impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
        cands = build_candidates(dp, args.source_file, args.lambda_penalty, args.min_workload, impact=impact,
                                 min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                                 exclude_functions=args.exclude_functions)
        found: set = set()
        for c in cands:
            lines = Path(c.source_file).read_text().splitlines()
            if "nl < R" in (lines[c.region.start_line - 1] if c.region.start_line <= len(lines) else ""):
                continue                                   # v4's repetition loop: measurement, not the loop under study
            ev = assemble(c, dp / "profiler", "")
            note = order_statement(ev, frozenset(PROMPT_VERSIONS[version]))
            for b in (l.strip() for l in note.splitlines() if l.strip().startswith("- ")):
                m = re.match(r"- Line \d+ \(`(?P<s>.*?)`\) reads an element of `(?P<x>.*?)` that line \d+ "
                             r"\(`(?P<w>.*?)`\) writes", b)
                if m:
                    found.add(("order", m.group("w"), m.group("s"), m.group("x")))
                    continue
                m = re.match(r"- Lines \d+ \(`(?P<a>.*?)`\) and \d+ \(`(?P<b>.*?)`\) feed each other", b)
                if m:
                    found.add(("mutual", m.group("a"), m.group("b")))
        return {"statements": found, "candidates": len(cands)}
    finally:
        project_mod.activate(None)


def _judge(name: str, found: set) -> List[str]:
    """Differences between what a version says and the ground truth."""
    want = TRUTH.get(name, [])
    problems: List[str] = []
    for kind, a, b in want:
        if kind == "order":
            if not any(f[0] == "order" and a in f[1] and b in f[2] for f in found):
                problems.append(f"no order `{a}` before `{b}`")
        else:
            if not any(f[0] == "mutual" and {True} == {any(t in x for x in f[1:3]) for t in (a, b)} for f in found):
                problems.append(f"`{a}` and `{b}` not called mutual")
    for f in found:
        if f[0] == "order" and not any(k == "order" and a in f[1] and b in f[2] for k, a, b in want):
            problems.append(f"a FALSE order: `{f[1]}` before `{f[2]}` ({f[3]})")
        if f[0] == "mutual" and not any(k == "mutual" and all(any(t in x for x in f[1:3]) for t in (a, b))
                                        for k, a, b in want):
            problems.append(f"a FALSE mutual: `{f[1]}` / `{f[2]}`")
    return problems


def _show(found: set) -> str:
    if not found:
        return "—"
    out = []
    for f in sorted(found):
        out.append(f"{f[1]} ⟶ {f[2]} [{f[3]}]" if f[0] == "order" else f"{f[1]} ⟷ {f[2]}")
    return "<br>".join(f"`{o}`" if "⟶" not in o and "⟷" not in o else o for o in out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profiles", type=Path, help="screen_profiles.tar.gz, or the directory it extracts to")
    ap.add_argument("--versions", default="3,4", help="prompt versions to replay (default 3,4)")
    ap.add_argument("--check", default="4", help="versions that must agree with the ground truth (default 4)")
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()
    versions = [int(v) for v in a.versions.split(",") if v]
    check = {int(v) for v in a.check.split(",") if v}
    rows: List[List[str]] = []
    wrong: Dict[int, List[str]] = {v: [] for v in versions}
    with tempfile.TemporaryDirectory(prefix="order_replay_") as tmp:
        root = _extract(a.profiles, Path(tmp))
        for d in sorted(root.iterdir()):
            # `<loop>_v4` / `<loop>_v5` (the Mac screen) or `<loop>_<suite>` (layout_equivalence.py's profiles)
            m = re.match(r"^(?P<name>.+?)_(?P<layout>v\d|tsvc_[a-z0-9]+)$", d.name)
            if not m or not (d / ".discopop").exists():
                continue
            name, layout = m.group("name"), m.group("layout")
            row = [name, layout, "; ".join(f"{k}: {x} / {y}" for k, x, y in TRUTH.get(name, [])) or "none"]
            for v in versions:
                res = _statements(d, name, v)
                problems = _judge(name, res["statements"])
                if problems:
                    wrong[v].append(f"{name} ({layout}): {'; '.join(problems)}")
                row.append(("right" if not problems else "WRONG") + " — " + _show(res["statements"]))
            rows.append(row)
    head = ["loop", "layout", "true"] + [f"version {v}" for v in versions]
    table = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
    summary = [f"{len(rows)} profiles."] + [
        f"Version {v}: {len(rows) - len(wrong[v])} right, {len(wrong[v])} wrong"
        + (": " + " | ".join(wrong[v]) if wrong[v] else "") + "." for v in versions]
    text = "\n".join(table) + "\n\n" + "\n".join(summary) + "\n"
    print(text)
    if a.md:
        a.md.write_text(text)
    return 1 if any(wrong[v] for v in versions if v in check) else 0


if __name__ == "__main__":
    sys.exit(main())
