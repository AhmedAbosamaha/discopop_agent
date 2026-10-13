#!/usr/bin/env python3
"""E8 (restructuring depth), read from the archive before any trial — no model, nothing run.

At the campaign's depth 0 the agent still profiles the program again after every rewrite it accepts and lists what
it now finds as candidates of depth 1. Those without a DiscoPoP pattern end `SKIPPED` with "Restructuring not
allowed at depth 1": they are exactly the regions a run at `--restructure-depth 1` would send to the model. Every
saved `agent.log` holds them, so what a deeper level would have had to do can be counted without running it.

What is read, per trial of an agent setup:
  * the candidate blocks of the log (`[depth=N] loop|function ID (lines a–b)` up to their closing line);
  * the benchmark's file as it stood when a block was listed: the saved original plus the saved patch of every
    rewrite accepted before it (`agent_patches/<file>.original`, `region_<id>_tier2.patch`);
  * `trial.json` for the outcome, the calls, the cost, the re-profiles and the speed verdicts.

A region a deeper level would send to the model is placed as
  the repetition loop     its first line is the loop over `nl` (TSVC's repetitions);
  the function            the candidate is the kernel function;
  a loop inside …         it lies inside a loop that is or will be parallel (a loop DiscoPoP has a pattern for in the
                          same listing, or a parallel construct standing in the file, read with the agent's own
                          `existing_parallel_spans`);
  a loop around …         it contains such a loop and is not the repetition loop;
  a loop beside them      neither — a loop of its own that the rewrite left sequential.

THE RULE FOR THESE KINDS WAS WRITTEN ON 13 OCT 2026, AFTER THE LOGS HAD BEEN READ. It is a description of the
archive, not a registered measure.

    venv/bin/python evaluation/agent/results/E08_restructuring_depth/preflight/depth_from_the_archive.py

Writes `depth_from_the_archive.md` beside itself (or into the folder given as the first argument).
"""
import collections
import json
import os
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = Path(os.environ.get("DP_RESULTS") or HERE.parents[1])
sys.path.insert(0, str(RESULTS.parents[2]))
from discopop_agent.pragmas.parse import existing_parallel_spans  # noqa: E402

HEAD = re.compile(r"^┌─ \[depth=(\d+)\] (\w+) (\S+) \(lines (\d+)–(\d+)\)")
END = re.compile(r"^└─ (.*)")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
LOOP = re.compile(r"\s*(for|while)\s*\(")
REP = re.compile(r"\bfor\s*\(\s*(int\s+)?nl\b")
LIMIT = "Restructuring not allowed at depth"
E3, E3B, E1 = "E03_who_writes_the_pragmas", "E03b_contrast_set", "E01v6_clean_files_three_way"
R4 = lambda stem: {f"{stem}_{i}" for i in (1, 2, 3, 4)}
# name -> (folder, which (run, loop) belong to it, the setups)
SETS = {
    "the pragma experiment, the 18 loops — the corrected table": (
        E3, lambda run, k: (run in R4("e3_r") and k != "s341") or run == "e3c_v8_s341",
        {"default_v5": "DiscoPoP writes", "llm_pragmas_v5": "the model writes"}),
    "the pragma experiment, the 18 loops — as first run": (
        E3, lambda run, k: run in R4("e3_r"),
        {"default_v5": "DiscoPoP writes", "llm_pragmas_v5": "the model writes"}),
    "the contrast set, the six loops under test — the corrected table": (
        E3B, lambda run, k: k != "s311" and ((run in R4("e3b") and k != "s316") or run == "e3bc_s316"),
        {"default_v5": "DiscoPoP writes", "llm_pragmas_v5": "the model writes"}),
    "the main comparison, the 18 loops — as first run (an earlier version of the texts)": (
        E1, lambda run, k: run in R4("e1v6_r"), {"default_v4": "DiscoPoP writes"}),
}
KINDS = ["the repetition loop", "the function", "a loop around a parallel one", "a loop inside a parallel one",
         "a loop beside them"]


def blocks(text):
    out, cur = [], None
    for ln in text.splitlines():
        m = HEAD.match(ln)
        if m:
            cur = {"depth": int(m.group(1)), "type": m.group(2), "rid": m.group(3), "a": int(m.group(4)),
                   "b": int(m.group(5)), "body": [], "end": None}
            continue
        if cur is None:
            continue
        e = END.match(ln)
        if e and not e.group(1).startswith("retry"):
            cur["end"] = e.group(1).strip()
            out.append(cur)
            cur = None
        else:
            cur["body"].append(ln)
    if cur is not None:
        cur["end"] = "(the log ends inside the block)"
        out.append(cur)
    return out


def apply(old, diff):
    """A unified diff applied to a list of lines; None where it does not apply."""
    new, pos, dl, i = [], 0, diff.splitlines(), 0
    while i < len(dl):
        m = HUNK.match(dl[i])
        if not m:
            i += 1
            continue
        start = int(m.group(1)) - 1 if (m.group(2) is None or int(m.group(2)) > 0) else int(m.group(1))
        if start < pos:
            return None
        new.extend(old[pos:start])
        pos = start
        i += 1
        while i < len(dl) and not HUNK.match(dl[i]):
            ln = dl[i]
            if ln.startswith("\\") or ln.startswith(("--- ", "+++ ", "diff ", "index ")):
                pass
            elif ln.startswith("+"):
                new.append(ln[1:])
            elif ln.startswith("-"):
                if pos >= len(old) or old[pos].rstrip() != ln[1:].rstrip():
                    return None
                pos += 1
            elif ln.startswith(" ") or ln == "":
                if pos >= len(old) or old[pos].rstrip() != ln[1:].rstrip():
                    return None
                new.append(old[pos])
                pos += 1
            else:
                return None
            i += 1
    new.extend(old[pos:])
    return new


def states(tdir, src, accepted_ids):
    """The benchmark's file: [as saved before the first rewrite, after the first accepted rewrite, ...]."""
    ap = tdir / "agent_patches"
    orig = ap / f"{src}.original"
    if not orig.exists():
        orig = tdir / "original" / src
    out = [orig.read_text().splitlines()]
    for rid in accepted_ids:
        pf = ap / f"region_{rid.replace(':', '_')}_tier2.patch"
        res = apply(out[-1], pf.read_text()) if pf.exists() else None
        if res is None:
            return out, f"the patch of region {rid} is missing or does not apply"
        out.append(res)
    return out, ""


def inside(c, p):
    return p[0] <= c[0] and c[1] <= p[1] and tuple(c) != tuple(p)


def read_trial(log):
    t = json.loads((log.parent / "trial.json").read_text())
    bl = blocks(log.read_text(errors="replace"))
    acc = [b for b in bl if b["end"].startswith("ACCEPTED")]
    row = {"t": t, "accepted": len(acc), "regions": [], "problem": ""}
    if not acc:
        return row
    st, why = states(log.parent, t["source"], [b["rid"] for b in acc])
    if why:
        row["problem"] = why
        return row
    k, asked = 0, {"the repetition loop": False, "the function": False}
    listing = collections.defaultdict(list)
    for b in bl:
        b["k"] = k
        lines = st[k]
        b["rep"] = b["type"] == "loop" and b["a"] <= len(lines) and bool(REP.search(lines[b["a"] - 1]))
        if b["depth"] == 0 and any("] Calling " in x for x in b["body"]):
            asked["the function" if b["type"] == "function" else "the repetition loop" if b["rep"] else "x"] = True
        b["asked_before"] = dict(asked)
        if b["end"].startswith("ACCEPTED"):
            k += 1
        elif k >= 1:
            listing[b["k"]].append(b)
    for kk, listed in listing.items():
        lines = st[kk]
        par = [(a, b) for a, b in existing_parallel_spans("\n".join(lines) + "\n")]
        par += [(b["a"], b["b"]) for b in listed if b["end"].startswith("DEFERRED")]
        for b in listed:
            if b["depth"] == 0 or not any(LIMIT in x for x in b["body"]):
                continue
            c = (b["a"], b["b"])
            if b["type"] == "loop" and not (c[0] <= len(lines) and LOOP.match(lines[c[0] - 1])):
                row["problem"] = f"line {c[0]} of the rebuilt file is no loop head"
            if b["type"] == "function":
                kind = "the function"
            elif b["rep"]:
                kind = "the repetition loop"
            elif any(inside(c, p) for p in par):
                kind = "a loop inside a parallel one"
            elif any(inside(p, c) for p in par):
                kind = "a loop around a parallel one"
            else:
                kind = "a loop beside them"
            row["regions"].append({"kind": kind, "span": c, "asked_before": b["asked_before"].get(kind),
                                   "code": [x.rstrip() for x in lines[c[0] - 1:c[1]]]})
    return row


def table(head, body):
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"] \
        + ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
md = ["# E8 (restructuring depth) — what the saved trials already say about a deeper level", "",
      "Built by `depth_from_the_archive.py`. No model, nothing run: every number is read from saved trials that ran at "
      "depth 0. A region counted here is one the agent listed after an accepted rewrite and skipped only because of "
      "the depth limit — the region a run at depth 1 would have sent to the model.", "",
      "**The kinds below were defined on 13 Oct 2026, after the logs had been read** (the script's head has the rule). "
      "A description of the archive, not a registered measure.", ""]
problems, flagged, cases = [], 0, []
summary = {}
for name, (folder, pick, setups) in SETS.items():
    head = ["setup", "trials", "a rewrite accepted", "a deeper level would ask the model", "— only about the repetition loop and the function",
            "— also about another loop", "loops with such a trial"]
    body, kinds_body, speed_body = [], [], []
    for arm, setup in setups.items():
        rows = []
        for log in sorted((RESULTS / folder / "runs").glob(f"*/benchmarks/*/*/{arm}/*/rep*/agent.log")):
            run, _, suite, k = log.relative_to(RESULTS / folder / "runs").parts[:4]
            if not pick(run, k):
                continue
            r = read_trial(log)
            r.update(run=run, loop=k, rep=log.parent.name)
            if r["problem"]:
                problems.append(f"{run} {k} {log.parent.name} {arm}: {r['problem']}")
            if (r["t"].get("llm_call_failures") or 0) > 0 or "--restructure-depth" in " ".join(r["t"].get("agent_cmd") or []):
                flagged += 1
            rows.append(r)
        acc = [r for r in rows if r["accepted"]]
        ask = [r for r in acc if r["regions"]]
        other = [r for r in ask if any(x["kind"] not in KINDS[:2] for x in r["regions"])]
        body.append([setup, len(rows), len(acc), f"{len(ask)} of {len(acc)}", len(ask) - len(other), len(other),
                     ", ".join(f"`{k}` ({v})" for k, v in sorted(collections.Counter(r["loop"] for r in other).items())) or "—"])
        cnt = collections.Counter(x["kind"] for r in ask for x in r["regions"])
        before = collections.Counter(x["kind"] for r in ask for x in r["regions"] if x["asked_before"])
        kinds_body.append([setup, sum(cnt.values())] + [
            (f"{cnt[kd]} ({before[kd]} asked about before, at depth 0)" if kd in KINDS[:2] else cnt[kd]) for kd in KINDS])
        v: "collections.Counter[str]" = collections.Counter()
        for r in rows:
            v.update(r["t"].get("d40_verdicts") or {})
        nf = [r for r in rows if (r["t"].get("d40_verdicts") or {}).get("not_faster", 0) > 0]
        cost = sum((r["t"].get("llm_usage") or {}).get("cost_usd") or 0 for r in rows)
        calls = sum(r["t"]["llm_calls"] for r in rows)
        speed_body.append([setup, len(rows), sum(1 for r in rows if r["t"]["outcome"] == "FASTER"), calls,
                           statistics.median(r["t"]["llm_calls"] for r in rows) if rows else "—", f"${cost:.2f}",
                           f"${cost / max(calls, 1):.3f}", sum(r["t"].get("refresh_full") or 0 for r in rows),
                           f"{len(nf)} of {len(rows)} ({v.get('not_faster', 0)} verdicts)",
                           ", ".join(f"{k} {n}" for k, n in sorted(collections.Counter(r["t"]["outcome"] for r in nf).items())) or "—"])
        for r in other:
            for x in r["regions"]:
                if x["kind"] not in KINDS[:2]:
                    cases.append((name, setup, r, x))
        summary[(name, setup)] = {
            "trials": len(rows), "accepted": len(acc), "ask": len(ask), "other": len(other),
            "other_loops": dict(sorted(collections.Counter(r["loop"] for r in other).items())),
            "regions": dict(cnt), "asked_before": dict(before),
            "faster": sum(1 for r in rows if r["t"]["outcome"] == "FASTER"), "calls": calls, "cost": round(cost, 2),
            "full_reprofiles": sum(r["t"].get("refresh_full") or 0 for r in rows),
            "trials_sent_back_not_faster": len(nf), "not_faster_verdicts": v.get("not_faster", 0),
            "sent_back_ended": dict(sorted(collections.Counter(r["t"]["outcome"] for r in nf).items()))}
    md += [f"## {name[0].upper() + name[1:]}", ""] + table(head, body) + ["",
           "The regions a deeper level would send to the model, by kind:", ""] + \
          table(["setup", "regions"] + KINDS, kinds_body) + ["",
           "The trials themselves (outcomes as the harness verified them; the speed verdict is the agent's own on a "
           "rewrite without a pragma — \"not faster than before the rewrite\" sends the model back to try again):", ""] + \
          table(["setup", "trials", "FASTER", "model calls", "median per trial", "cost", "per call", "full re-profiles",
                 "trials with a rewrite sent back as not faster", "how those trials ended"], speed_body) + [""]

md += ["## Every other loop a deeper level would have sent to the model", "",
       "Not the repetition loop and not the function. The premise of the depth experiment — a rewrite leaves or exposes "
       "another task — holds only for the loops *beside* the parallel ones; a loop *inside* a loop that is about to be "
       "parallel has nothing left to win.", ""]
for name, setup, r, x in cases:
    md += [f"- **{name.split(' — ')[0]}** ({name.split(' — ')[1]}), {setup}: `{r['run']}` `{r['loop']}` {r['rep']}, the trial ended "
           f"{r['t']['outcome']} — {x['kind']}, lines {x['span'][0]}–{x['span'][1]}:", "", "  ```c"] + \
          ["  " + ln for ln in x["code"][:9]] + (["  ..."] if len(x["code"]) > 9 else []) + ["  ```", ""]
md += ["## Checks on this read-out", "",
       f"- trials whose file could not be rebuilt, or whose listed loop is no loop in the rebuilt file: {len(problems)}"]
md += [f"  - {p}" for p in problems]
md += [f"- trials with a failed model call or run with the depth flag (they would not belong here): {flagged}", ""]
(out_dir / "depth_from_the_archive.md").write_text("\n".join(md) + "\n")
(out_dir / "depth_from_the_archive.json").write_text(json.dumps(
    {f"{n} | {s}": v for (n, s), v in summary.items()}, indent=1, ensure_ascii=False) + "\n")
print("\n".join(md))
