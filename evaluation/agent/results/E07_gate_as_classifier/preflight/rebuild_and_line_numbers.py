#!/usr/bin/env python3
"""E7 pre-flight (9 Oct 2026) — can every saved candidate be rebuilt as the gate saw it, and at which line did the
gate's dependence check look up each directive of the final pass? Text only: nothing is compiled, run or judged.

    venv/bin/python evaluation/agent/results/E07_gate_as_classifier/preflight/rebuild_and_line_numbers.py \\
        --groups E1-v6,E2-v6b
    venv/bin/python evaluation/agent/results/E07_gate_as_classifier/preflight/rebuild_and_line_numbers.py \\
        --runs t0_11_c3_b19r_a,t0_11_c3_b19r_b,t0_11_c3_b19r_c,t0_11_b19r_apps_a,t0_11_b19r_apps_b,t0_11_b19r_apps_c

Rebuild. A trial's candidates are replayed in the order the agent judged them (`agent_patches/candidates.jsonl`; the floor step's own file `agent_patches/floor/candidates.jsonl` likewise):
a model's rewrite (phase A) is judged on the kept state; DiscoPoP's directives for that rewrite (A-D40) on the
rewritten text, one at a time and then together; the rewrite is then kept or undone — kept exactly when
`accepted.json` holds its patch; the final pass (B) inserts DiscoPoP's directives one after the other. Patches are
applied the way the gate applies them (`gate.patching`: hunk headers re-derived, a trailing newline, GNU patch;
tried without fuzz first). A trial's history counts as verified when its end state equals the archived final file
byte for byte. This first version does not follow every path of the agent (a directive tried in phase A on a
region DiscoPoP already parallelises, a region handed back to the model after the final pass); what it cannot
rebuild is counted and named, never left out.

Line numbers. The dependence check takes the loop's line from the candidate's diff, i.e. in the working file,
and looks it up among records that carry the PROFILE's line numbers (the file before the final pass inserted
anything). For every directive of the final pass this prints how many directive lines the working file already
held above the loop (the shift), and — where the shift is not zero — whether a loop starts at the shifted line in
the profiled text (the check then read another loop's records) or not (the check found no record and said
nothing)."""
import argparse
import collections
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO, EVAL = HERE.parents[5], HERE.parents[4]
sys.path[:0] = [str(EVAL / "agent/tools"), str(EVAL / "shared"), str(REPO)]
import campaign  # noqa: E402
from discopop_agent.gate.dependences import annotated_loop_lines  # noqa: E402
from discopop_agent.gate.patching import fix_hunk_headers, run_patch  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--groups", default="")
ap.add_argument("--runs", default="")
a = ap.parse_args()
reg = json.loads((EVAL / "agent/results/campaign.json").read_text())
runs = sorted(r for r, v in reg["runs"].items()
              if v.get("status") == "valid" and (v.get("group") in a.groups.split(",") or r in a.runs.split(",")))
OMP_ADDED = re.compile(r"^\+\s*#\s*pragma\s+omp\b", re.M)
OMP = re.compile(r"^\s*#\s*pragma\s+omp\b")
LOOP = re.compile(r"^\s*(for|while)\b")
TMP = Path(tempfile.mkdtemp(prefix="e7_preflight_"))


def body(text: str) -> str:
    return "\n".join(ln.rstrip() for ln in text.splitlines() if not ln.startswith(("--- ", "+++ "))).strip()


def apply(base: str, patch_text: str, name: str, exact: bool):
    dst = TMP / name
    dst.write_text(base)
    lines = [(f"--- {dst}" if ln.startswith("--- ") else f"+++ {dst}" if ln.startswith("+++ ") else ln)
             for ln in fix_hunk_headers(patch_text).splitlines()]
    pp = TMP / "candidate.patch"
    pp.write_text("\n".join(lines) + "\n")
    ok, _ = run_patch(dst, pp, exact=exact)
    return dst.read_text() if ok else None


rebuilt = collections.Counter()
verdicts = collections.Counter()
phases = collections.Counter()
trials = collections.Counter()
lines_b = collections.Counter()
floors = collections.Counter()
programs = collections.defaultdict(set)
not_rebuilt, not_verified, misread = [], [], []
shift_trials = set()
for run in runs:
    root = campaign.find_run(run)
    for index in sorted(list(root.glob("benchmarks/**/agent_patches/candidates.jsonl"))
                        + list(root.glob("benchmarks/**/agent_patches/floor/candidates.jsonl"))):
        floor = index.parent.name == "floor"          # the agent's floor step: DiscoPoP's directives on the original
        trial = index.parent.parent.parent if floor else index.parent.parent
        rel = trial.relative_to(root).parts
        bench, arm, rep = f"{rel[1]}/{rel[2]}", rel[3], rel[-1]
        name = json.loads((EVAL / "agent/prepared" / bench / "meta.json").read_text())["file"]
        ext = Path(name).suffix
        o_dir, f_dir = trial / "original", trial / "final"
        orig = (o_dir / name if o_dir.is_dir() else trial / f"original{ext}").read_text()
        fin = f_dir / name if f_dir.is_dir() else trial / f"final{ext}"
        entries = [json.loads(ln) for ln in index.read_text().splitlines() if ln.strip()]
        texts = [(index.parent / e["patch"]).read_text(errors="replace") for e in entries]
        acc = json.loads((index.parent / "accepted.json").read_text()) if (index.parent / "accepted.json").is_file() else []
        kept = set()                                   # the model rewrites the agent kept
        for entry in acc:
            pf = index.parent / Path(str(entry.get("patch_file") or "-")).name
            if pf.is_file():
                hits = [i for i, e in enumerate(entries)
                        if e.get("phase") == "A" and e.get("passed") and body(texts[i]) == body(pf.read_text(errors="replace"))]
                if hits:
                    kept.add(hits[-1])
        state, tentative, keep_it, complete = orig, None, False, True
        for i, e in enumerate(entries):
            ph = "floor" if floor else str(e.get("phase"))
            kind = "directive" if OMP_ADDED.search(texts[i]) else "rewrite"
            verdict = "accepted" if e.get("passed") else str(e.get("stage"))
            phases[ph] += 1
            verdicts[(kind, verdict)] += 1
            if ph in ("A", "B") and tentative is not None:        # the rewrite before this one is settled
                state, tentative = (tentative if keep_it else state), None
            bases = [tentative] if ph == "A-D40" else ([state] if tentative is None else [state, tentative])
            if ph in ("B", "floor"):
                loops = annotated_loop_lines(fix_hunk_headers(texts[i]))
                held = state.splitlines()
                profiled = [x for x in held if not OMP.match(x)]
                for line in loops or []:
                    shift = sum(1 for x in held[:line - 1] if OMP.match(x))
                    cached = "verdict reused" if e.get("from_cache") else "judged"
                    if shift == 0:
                        lines_b[("no directive above: the line numbers agree", cached)] += 1
                    else:
                        other = line - 1 < len(profiled) and bool(LOOP.match(profiled[line - 1]))
                        lines_b[("directive(s) above: " + ("ANOTHER loop starts at the shifted line" if other
                                                             else "no loop starts at the shifted line"), cached)] += 1
                        shift_trials.add((run, bench, arm, rep))
                        if other:
                            misread.append(f"{run} {bench} {arm} {rep} n{e['n']}: shift {shift}, read line {line} "
                                           f"`{profiled[line - 1].strip()[:70]}` — gate: {verdict}")
                if loops is None:
                    lines_b[("not a pure annotation", "-")] += 1
            prog = None
            for b in (x for x in bases if x is not None):
                prog = apply(b, texts[i], name, True) or apply(b, texts[i], name, False)
                if prog is not None:
                    break
            if prog is None:
                rebuilt[(ph, "not rebuilt")] += 1
                not_rebuilt.append(f"{run} {bench} {arm} {rep} n{e['n']} ({ph}, {kind}, {verdict})")
                complete = False
                continue
            rebuilt[(ph, "rebuilt")] += 1
            programs[kind].add(hashlib.sha256((bench + "\0" + prog).encode()).hexdigest())
            if ph == "A" and e.get("passed"):
                tentative, keep_it = prog, i in kept
            elif ph in ("B", "floor") and e.get("passed"):
                state = prog
        if tentative is not None and keep_it:
            state = tentative
        if floor:                                      # its program is not the trial's final file
            floors[("every candidate rebuilt" if complete else "a candidate not rebuilt")] += 1
            continue
        same = fin.is_file() and fin.read_text() == state
        trials[("end state equals the final file" if same else "end state differs from the final file")
               + (", every candidate rebuilt" if complete else ", a candidate not rebuilt")] += 1
        if not (same and complete):
            not_verified.append(f"{run} {bench} {arm} {rep}")

n = sum(phases.values())
print(f"runs with candidates searched: {len(runs)} valid run(s); trials with candidates: {sum(trials.values())}; "
      f"candidates: {n}")
print("by phase:", ", ".join(f"{k} {v}" for k, v in sorted(phases.items())))
print("by kind and the gate's verdict:", ", ".join(f"{k[0]} {k[1]} {v}" for k, v in sorted(verdicts.items())))
print(f"rebuilt: {sum(v for k, v in rebuilt.items() if k[1] == 'rebuilt')} of {n} "
      f"(not rebuilt: {', '.join(f'{k[0]} {v}' for k, v in sorted(rebuilt.items()) if k[1] != 'rebuilt') or 'none'})")
print(f"distinct programs among the rebuilt (benchmark + file text): {len(programs['rewrite'] | programs['directive'])} "
      f"— {len(programs['rewrite'])} without a directive, {len(programs['directive'])} with one")
print("trials:", "; ".join(f"{k}: {v}" for k, v in sorted(trials.items())))
print("floor steps (DiscoPoP's directives on the original at the start of an agent trial):",
      "; ".join(f"{k}: {v}" for k, v in sorted(floors.items())) or "none")
print(f"\nthe dependence check's line in the final pass and the floor step ({sum(v for k, v in lines_b.items())} loop(s) under directives):")
for k, v in sorted(lines_b.items()):
    print(f"  {k[0]} · {k[1]}: {v}")
print(f"trials with a directive looked up at a shifted line: {len(shift_trials)}")
for m in misread:
    print("  read another loop:", m)
print("\ncandidates not rebuilt:")
print("\n".join("  " + x for x in not_rebuilt) or "  none")
print("trials whose history is not verified:")
print("\n".join("  " + x for x in not_verified) or "  none")
