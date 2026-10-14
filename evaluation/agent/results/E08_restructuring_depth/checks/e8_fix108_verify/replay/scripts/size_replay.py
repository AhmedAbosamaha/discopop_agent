"""Replay E8's second smoke's depth-2 trial through D40 as it stood and as repaired by Fix 108 — no model.

Everything comes from the archive: the original files, the rewrites the trial's gate passed (`agent_patches/
candidates/`), DiscoPoP's pragma for each exposed loop as D40 recorded it, and the agent's command line (the
project layout, the timing flags).  D40 itself is the agent's (`phases.verdicts.judge_as_shipped`, staging its own
pragmas); the safety gate is stood in by the trial's recorded verdict (every pragma here passed it); the run at
the timing size is phase_a's `_at_size` and the paired timing its `_time`, written out the same way, with the real
build and the real run.

  A  the depth-0 rewrite (`0000`: `s_vals[LEN_1D + 1]` on the stack), a deeper level to come — as it stood: kept
     with the speed question deferred; repaired: run once at the timing size.
  B  the depth-1 rewrite on it (`0004`: adds `b_snapshot[LEN_1D]`) — the same two ways.
  C  the model's second depth-2 attempt (`0013`: `s_vals` moved to the heap, the snapshot dropped) at the last level,
     timed against the program before it (the two kept rewrites) — as it stood: the paired timing's failure taken
     as the rewrite's; repaired: named.  Then the two programs run alone at the timing size.

    venv/bin/python size_replay.py TRIAL_DIR OUT.json [--timing-flag -DSTANDARD_DATASET]
(run from the repository root; without --timing-flag the trial's own --timing-cflags are used).
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

REPO = Path(os.environ.get("DISCOPOP_AGENT_REPO", os.getcwd())).resolve()
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "evaluation" / "agent" / "tools"))
import harness_include  # noqa: E402  (every build finds prepared/_harness, as in every harness tool — D39)
harness_include.install()
from discopop_agent import project as project_mod  # noqa: E402
from discopop_agent.args import parse_args  # noqa: E402
from discopop_agent.gate.timing import measure_marginal, time_source  # noqa: E402
from discopop_agent.phases.verdicts import judge_as_shipped  # noqa: E402
from discopop_agent.sources import _apply_in_memory  # noqa: E402

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def apply(text: str, diff: str, name: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / name
        f.write_text(text)
        out = _apply_in_memory(diff, str(f))
    assert out is not None, "an archived patch does not re-apply"
    return out


def pragma_line(diff: str) -> int:
    """The line, in the file without it, of the loop a one-pragma diff annotates."""
    new = 0
    for ln in diff.splitlines():
        m = HUNK.match(ln)
        if m:
            new = int(m.group(1)) - 1
            continue
        if ln.startswith(("+++", "---")):
            continue
        if ln.startswith("+"):
            new += 1
            if "#pragma omp" in ln:
                return new
        elif ln.startswith(" "):
            new += 1
    raise ValueError("no pragma in the diff")


def loop_end(text: str, head: int) -> int:
    lines, depth = text.splitlines(), 0
    for i in range(head - 1, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth == 0 and "{" in "".join(lines[head - 1:i + 1]):
            return i + 1
    return head


def candidates(text: str, rows, patches: Path, dp: Path, src: Path):
    out = []
    for k, row in enumerate(rows, start=1):
        diff = (patches / row["patch"]).read_text()
        head = pragma_line(diff)
        pdir = dp / "patch_generator" / str(k)
        pdir.mkdir(parents=True)
        (pdir / "1.patch").write_text(diff)
        out.append(SimpleNamespace(
            region=SimpleNamespace(start_line=head, end_line=loop_end(text, head), file_id=1,
                                   name=row["exposed_region"], region_id=row["exposed_region"]),
            pattern={"pattern_id": k, "applicable_pattern": True}, pattern_type="do_all",
            source_file=str(src), tier=1, workload_estimate=100.0))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trial")
    ap.add_argument("out")
    ap.add_argument("--timing-flag", default=None)
    a = ap.parse_args()
    trial = Path(a.trial).resolve()
    out_path = Path(a.out).resolve()
    t = json.loads((trial / "trial.json").read_text())
    rows = [json.loads(x) for x in (trial / "agent_patches" / "candidates.jsonl").read_text().splitlines() if x.strip()]
    patches = trial / "agent_patches"
    by_n = {r["n"]: r for r in rows}
    work = Path(tempfile.mkdtemp(prefix="fix108_replay_"))
    shutil.copytree(trial / "original", work, dirs_exist_ok=True)
    (work / ".discopop").mkdir()
    os.chdir(work)
    sys.argv = ["x"] + t["agent_cmd"][3:]
    args = parse_args()
    project_mod.activate(args.project)
    project_mod.set_focus(args.source_file)
    flags = [a.timing_flag] if a.timing_flag else list(args.timing_cflags)
    src = Path(args.source_file)
    name = src.name
    original = src.read_text()
    report = {"trial": str(trial.relative_to(REPO)) if REPO in trial.parents else str(trial),
              "timing_flags": flags, "stack_limit_kb": os.popen("sh -c 'ulimit -s'").read().strip(),
              "agent_cmd": t["agent_cmd"][3:], "cases": []}

    def at_size(staged: str):                      # phase_a's _at_size
        with tempfile.TemporaryDirectory(prefix="dp_agent_size_") as tmp:
            ok_s, _t, _o, sdiag = time_source(staged, args.source_file, Path(tmp), "size", None,
                                              repeats=1, extra_flags=flags or None)
        seen.append(staged)
        return ok_s, sdiag

    def timed(named: bool):                        # phase_a's _time, with or without Fix 108's naming
        return lambda b, s: measure_marginal(b, s, args.source_file, None, extra_flags=flags or None,
                                             name_sides=named)

    def safe(diff, c):                             # the trial's safety gate: every pragma here passed
        return True, ""

    r0 = apply(original, (patches / by_n[0]["patch"]).read_text(), name)
    r1 = apply(r0, (patches / by_n[4]["patch"]).read_text(), name)
    heap = apply(r1, (patches / by_n[13]["patch"]).read_text(), name)
    for label, before, after, members, set_n, last in (
            ("A depth-0 rewrite 0000, a deeper level to come", original, r0, (1, 2), 3, False),
            ("B depth-1 rewrite 0004 on it, a deeper level to come", r0, r1, (5, 6), 7, False),
            ("C the heap version 0013 at the last level, against the two kept rewrites", r1, heap, (14, 15), 16, True)):
        src.write_text(after)
        dp = Path(tempfile.mkdtemp(prefix="fix108_dp_"))
        cands = candidates(after, [by_n[n] for n in members], patches, dp, src)
        archived_staged = apply(after, (patches / by_n[set_n]["patch"]).read_text(), name)
        case = {"case": label}
        seen: list = []
        if not last:
            old = judge_as_shipped(cands, before, dp, str(src), threshold=0.0, validate=safe, measure=None)
            new = judge_as_shipped(cands, before, dp, str(src), threshold=0.0, validate=safe, measure=None,
                                   run_at_size=at_size)
        else:
            old = judge_as_shipped(cands, before, dp, str(src), threshold=0.97, validate=safe, measure=timed(False))
            new = judge_as_shipped(cands, before, dp, str(src), threshold=0.97, validate=safe, measure=timed(True))
            ok_b, _tb, _ob, db = time_source(before, args.source_file, dp, "alone_before", None, repeats=1,
                                             extra_flags=flags or None)
            staged = archived_staged
            ok_h, _th, _oh, dh = time_source(staged, args.source_file, dp, "alone_after", None, repeats=1,
                                             extra_flags=flags or None)
            case["alone_at_size"] = {"program before (0000 + 0004)": "runs" if ok_b else db.strip()[:80],
                                     "0013 with its pragmas": "runs" if ok_h else dh.strip()[:80]}
        case["as_it_stood"] = {"status": old.status, "diagnostic": old.diagnostic[:200]}
        case["repaired"] = {"status": new.status, "diagnostic": new.diagnostic[:200]}
        if seen:
            case["size_run_got_the_trial's_staged_program"] = seen[-1] == archived_staged
        report["cases"].append(case)
        shutil.rmtree(dp, ignore_errors=True)
    src.write_text(original)
    project_mod.activate(None)
    os.chdir(REPO)
    shutil.rmtree(work, ignore_errors=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
