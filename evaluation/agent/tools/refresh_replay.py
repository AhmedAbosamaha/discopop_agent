#!/usr/bin/env python3
"""E4, step 1 — the fast refresh on the model's own rewrites, replayed without a model.

For every pragma-free rewrite that passed the gate's checks in the archived trials of the given runs and arm (the
`phase: "A"`, `passed` records of `agent_patches/candidates.jsonl`), the program as it stood before the rewrite is
profiled in full, and the rewritten program is then judged twice with the agent's own functions, in the trial's
own configuration (the archived `agent_cmd`):

  fast   `profiling.runner._reprofil_fast`, exactly as phase A calls it: compile only, the dependences of the
         profile before the rewrite carried over; where it reports itself unusable the agent falls back to a
         full re-profile, and so does the read-out (`fallback`)
  full   `profiling.runner._reprofil`: instrument, run, explore — what every archived trial did

and after each, as phase A does: the runtimes re-measured, the regions rebuilt (`plan.build_candidates`), and
DiscoPoP's verdict on the rewritten lines taken with `phases.verdicts._verify_rewrite(validate_patterns=False)`
— `exposed`, `no_pattern` or `no_usable_pragma` — together with the loops it reports as parallel there and the
directive it writes for each. Where that verdict is `exposed`, the agent's next step is taken as well, its
safety half only (`phases.verdicts.judge_as_shipped` with `measure=None`): DiscoPoP's directives for the exposed
loops through the gate's safety checks, outermost first, one directive per nest, then the safe ones together —
`safe_deferred` (the rewrite would be kept, speed aside) or `pattern_broken` (it would be reverted); where the
directives cannot be staged the agent leaves the question to its final annotation, and so does this (`exposed`,
counted apart). The gate
judges against the ORIGINAL program's output, captured once per trial as a run does, and each kind of refresh
has a gate cache of its own.

The control: the full re-profile is taken a SECOND time on the same rewritten program and judged the same way
(`full2`, with the full re-profile's gate cache). What differs between the two full re-profiles is what one
program's profile differs in from run to run; the fast refresh's differences are read against it.
One line per rewrite goes to `results.jsonl`; nothing is decided here.

The program before a rewrite is rebuilt from the trial's own files: the original (`<file>.original`) and the
rewrites the trial kept (`accepted.json`), in order; a rewrite whose diff applies to none of those states is
counted and left out. No model is called; speed is not measured (the judgement's timing half is left out).

    venv/bin/python evaluation/agent/tools/refresh_replay.py --runs e3_r_1,e3_r_2 --arm default_v5 \\
        --out evaluation/agent/runs/e4_replay/e3_r_12 [--only tsvc_c2/s244] [--limit N]
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ["DP_REPLAY_REPO"]).resolve() if os.environ.get("DP_REPLAY_REPO") else HERE.parents[2]
TOOLS = REPO / "evaluation" / "agent" / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / "evaluation" / "shared"))
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

PREPARED = REPO / "evaluation" / "agent" / "prepared"
VERDICT_LINE = re.compile(r"\[Phase-A\] exposure verdict: (\w+)")


def pass_digest() -> Optional[str]:
    """sha256 of the installed DiscoPoP pass — which profiler build answered."""
    hits = sorted(h for h in (REPO / "venv").glob("lib/python*/site-packages/**/LLVMDiscoPoP*") if h.is_file())
    return hashlib.sha256(hits[0].read_bytes()).hexdigest() if hits else None


def apply_patch(base: str, patch_file: Path, name: str) -> Optional[str]:
    """`base` with the unified diff of `patch_file` applied, or None when it does not apply cleanly (no fuzz)."""
    with tempfile.TemporaryDirectory(prefix="replay_patch_") as tmp:
        src, out, diff = Path(tmp) / name, Path(tmp) / "out", Path(tmp) / "diff"
        src.write_text(base)
        text = patch_file.read_text()
        # the trial saved its diffs without the last line's newline; `patch` needs it for a hunk that reaches the end
        diff.write_text(text if text.endswith("\n") else text + "\n")
        r = subprocess.run(["patch", "-s", "-F", "0", "-o", str(out), str(src), str(diff)],
                           capture_output=True, text=True)
        return out.read_text() if r.returncode == 0 and out.is_file() else None


def rewrites_of(trial: Path, kernel_file: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """The pragma-free rewrites of one trial that passed the checks, each with the program before and after it."""
    ap = trial / "agent_patches"
    counts = {"passed": 0, "replayable": 0, "base_unknown": 0, "kept_chain_broken": 0}
    original = (ap / f"{kernel_file}.original").read_text()
    cands = [json.loads(ln) for ln in (ap / "candidates.jsonl").read_text().splitlines() if ln.strip()]
    passed = [c for c in cands if str(c.get("phase")) == "A" and c.get("passed")]
    counts["passed"] = len(passed)
    # the states the file went through: the original, then one more per kept rewrite
    kept_files = []
    if (ap / "accepted.json").is_file():
        for e in json.loads((ap / "accepted.json").read_text()):
            if e.get("tier") == 2 and e.get("patch_file"):
                kept_files.append(ap / Path(e["patch_file"]).name)
    states = [original]
    for kf in kept_files:
        nxt = apply_patch(states[-1], kf, kernel_file) if kf.is_file() else None
        if nxt is None:
            counts["kept_chain_broken"] += 1
            break
        states.append(nxt)
    # which candidate each keep was: the first one, in order, that turns state k into state k+1
    keep_at: List[int] = []
    k = 0
    for c in passed:
        if k + 1 >= len(states):
            break
        got = apply_patch(states[k], ap / c["patch"], kernel_file)
        if got is not None and got == states[k + 1]:
            keep_at.append(int(c["n"]))
            k += 1
    out: List[Dict[str, Any]] = []
    for c in passed:
        n = int(c["n"])
        at = sum(1 for kn in keep_at if kn < n)
        order = [at] + [i for i in range(len(states) - 1, -1, -1) if i != at]
        post = base = None
        for i in order:
            post = apply_patch(states[i], ap / c["patch"], kernel_file)
            if post is not None:
                base = i
                break
        if post is None or base is None:
            counts["base_unknown"] += 1
            continue
        counts["replayable"] += 1
        out.append({"n": n, "region_id": c.get("region_id"), "base": base, "kept": n in keep_at,
                    "pre": states[base], "post": post, "diff": (ap / c["patch"]).read_text()})
    return out, counts


class Bench:
    """One work directory per (package, program before the rewrite): the profile is taken and refreshed in place,
    as the agent does it, so the absolute paths DiscoPoP keys its file mapping on never change."""

    def __init__(self, work: Path, package: Path, kernel_file: str, agent_cmd: List[str], log: io.TextIOBase,
                 original: str, judge: bool):
        self.work, self.kernel_file, self.log = work, kernel_file, log
        self.original, self.judge = original, judge
        self.ref: Tuple[Any, Any, Any] = (None, None, None)
        self.gate_cache: Dict[str, Dict[str, Any]] = {"fast": {}, "full": {}}
        self.last: Tuple[List[Any], Any] = ([], None)
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        for f in package.iterdir():
            if f.suffix in (".c", ".h", ".cpp", ".hpp"):
                shutil.copy2(f, work / f.name)
        self.src = work / kernel_file
        self.dp = work / ".discopop"
        self.snap = work / "_profile_before"
        flags = agent_cmd[agent_cmd.index("discopop_agent") + 1:]
        os.chdir(work)
        from discopop_agent import args as args_mod
        from discopop_agent import project as project_mod
        argv = sys.argv
        try:
            sys.argv = ["discopop_agent"] + flags
            with contextlib.redirect_stdout(log):
                self.args = args_mod.parse_args()
        finally:
            sys.argv = argv
        project_mod.activate(self.args.project)
        if self.args.project is not None:
            project_mod.set_focus(self.args.source_file)
        from discopop_agent.profiling import tools as profiling_tools
        profiling_tools.set_explorer_timeout(self.args.explorer_timeout)
        if judge:
            # as a run does at its start, on the original program: the reference output of every check input and
            # the numerical noise floor the output check allows
            from discopop_agent.gate import capture_reference, numerical_noise_floor
            a = self.args
            self.src.write_text(original)
            with contextlib.redirect_stdout(log):
                self.ref = capture_reference(a.source_file, a.reprofil_args or None,
                                             extra_inputs=a.check_inputs or None, timing_flags=None)
                if a.numeric_tolerance and self.ref[0] is not None:
                    a.noise_floor = numerical_noise_floor(a.source_file, a.reprofil_args or None,
                                                          extra_inputs=a.check_inputs or None).value

    def profile_before(self, pre: str) -> bool:
        from discopop_agent.profiling import _reprofil
        self.src.write_text(pre)
        shutil.rmtree(self.dp, ignore_errors=True)
        with contextlib.redirect_stdout(self.log):
            ok = _reprofil(self.args.source_file, self.dp, self.args.reprofil_args or None)
        shutil.rmtree(self.snap, ignore_errors=True)
        if ok:
            shutil.copytree(self.dp, self.snap)
        return bool(ok)

    def restore_before(self, pre: str) -> None:
        self.src.write_text(pre)
        shutil.rmtree(self.dp, ignore_errors=True)
        shutil.copytree(self.snap, self.dp)

    def verdict(self, diff: str) -> Dict[str, Any]:
        """DiscoPoP's verdict on the rewritten lines from the profile now in place — phase A's own sequence."""
        from discopop_agent.phases.verdicts import _verify_rewrite, exposed_in, pragma_patch
        from discopop_agent.plan import build_candidates
        from discopop_agent.plan import impact as impact_mod
        from discopop_agent.pragmas.parse import _touched_span
        from discopop_agent.profiling import _measure_hotspots
        a = self.args
        with contextlib.redirect_stdout(self.log):
            impact = impact_mod.ImpactModel(threads=os.cpu_count() or 1)
            remeasured = False
            if a.hotspots:
                ok_hs, _note = _measure_hotspots(a, self.dp, force=True)
                fresh = impact_mod.load_hotspots(self.dp, threads=impact.threads) if ok_hs else None
                if fresh is not None and fresh.available:
                    impact.adopt(fresh)
                    remeasured = True
            cands = build_candidates(self.dp, a.source_file, a.lambda_penalty, a.min_workload, impact=impact,
                                     min_impact=a.min_impact, min_runtime_share=a.min_runtime_share,
                                     exclude_functions=a.exclude_functions)
            touched = _touched_span(diff)
            out = _verify_rewrite(cands, touched, self.dp, a, None, None, None, validate_patterns=False,
                                  gate_cache={})
            exposed = []
            for c in exposed_in(cands, touched, a.source_file):
                patch = pragma_patch(c, self.dp, a.source_file) or ""
                prag = sorted(re.sub(r"\s+", " ", ln[1:].strip()) for ln in patch.splitlines()
                              if ln.startswith("+") and "#pragma" in ln)
                exposed.append([c.region.start_line, c.region.end_line, c.pattern_type or "", prag])
        self.last = (cands, touched)
        return {"status": out.status, "exposed": sorted(exposed, key=json.dumps), "touched": list(touched or ()),
                "runtimes_remeasured": remeasured, "regions": len(cands)}

    def judged(self, arm: str, pre: str) -> Dict[str, Any]:
        """The safety half of the agent's judgement of an exposed rewrite, on the profile now in place."""
        from discopop_agent.gate.validate import _validate_cached
        from discopop_agent.phases.verdicts import exposed_in, judge_as_shipped
        a = self.args
        cands, touched = self.last
        checks: List[Dict[str, Any]] = []

        def _safe(diff: str, c: Any) -> Tuple[bool, str]:
            res, cached, _bfp = _validate_cached(
                self.gate_cache[arm], diff, a, self.ref[0], a.reprofil_args or None, self.ref[1],
                reference_outputs=self.ref[2], mode="safety",
                dep_region=(c.region.file_id, c.region.start_line, c.region.end_line) if c is not None else None)
            checks.append({"lines": [c.region.start_line, c.region.end_line] if c is not None else None,
                           "pragmas": sorted(re.sub(r"\s+", " ", ln[1:].strip()) for ln in diff.splitlines()
                                             if ln.startswith("+") and "#pragma" in ln),
                           "passed": bool(res.passed), "stage": res.stage, "from_cache": bool(cached)})
            return bool(res.passed), f"{res.stage}: {res.diagnostic or ''}"[:300]

        t0 = time.monotonic()
        with contextlib.redirect_stdout(self.log):
            out = judge_as_shipped(exposed_in(cands, touched, a.source_file), pre, self.dp, a.source_file,
                                   threshold=0.0, validate=_safe, measure=None)
        return {"judged": out.status, "checks": checks, "judge_seconds": round(time.monotonic() - t0, 2)}

    def fast(self, pre: str, post: str, diff: str) -> Dict[str, Any]:
        from discopop_agent.profiling.runner import _reprofil_fast
        self.restore_before(pre)
        self.src.write_text(post)
        scratch = self.work / "_refresh"
        scratch.mkdir(exist_ok=True)
        t0 = time.monotonic()
        with contextlib.redirect_stdout(self.log):
            ok, note = _reprofil_fast(self.args.source_file, self.dp, pre, post, scratch)
        res: Dict[str, Any] = {"usable": bool(ok), "note": str(note)[:300], "seconds": round(time.monotonic() - t0, 2)}
        if ok:
            res.update(self.verdict(diff))
            if self.judge and res["status"] == "exposed":
                res.update(self.judged("fast", pre))
        return res

    def full(self, pre: str, post: str, diff: str) -> Dict[str, Any]:
        from discopop_agent.profiling import _reprofil
        self.src.write_text(post)
        shutil.rmtree(self.dp, ignore_errors=True)
        t0 = time.monotonic()
        with contextlib.redirect_stdout(self.log):
            ok = _reprofil(self.args.source_file, self.dp, self.args.reprofil_args or None)
        res: Dict[str, Any] = {"usable": bool(ok), "seconds": round(time.monotonic() - t0, 2)}
        if ok:
            res.update(self.verdict(diff))
            if self.judge and res["status"] == "exposed":
                res.update(self.judged("full", pre))
        return res


def classify(full: Dict[str, Any], fast: Dict[str, Any]) -> str:
    """How the verdict after one refresh (`fast`: the fast refresh, or the second full re-profile of the control)
    stands against the full re-profile's."""
    if not full.get("usable"):
        return "full re-profile failed"
    if not fast.get("usable"):
        return "fast refresh unusable: the agent falls back to the full re-profile"
    fe, ue = full["status"] == "exposed", fast["status"] == "exposed"
    if fe and ue:
        return "same: parallel in both, the same directives" if full["exposed"] == fast["exposed"] \
            else "parallel in both, other loops or other directives"
    if ue and not fe:
        return "parallel only after the fast refresh"
    if fe and not ue:
        return "parallel only after the full re-profile"
    return "same: not parallel in either"


def kept_directives(arm: Dict[str, Any]) -> Optional[List[List[Any]]]:
    """The directives a rewrite would be kept with (the safety half of the judgement), or None when it would be
    reverted: the single checks that passed, or the outermost one alone when the set of them failed together."""
    if arm.get("status") != "exposed" or arm.get("judged") != "safe_deferred":
        return None
    singles = [c for c in arm.get("checks", []) if c["lines"] is not None and c["passed"]]
    together = [c for c in arm.get("checks", []) if c["lines"] is None]
    if together and not together[-1]["passed"]:
        singles = singles[:1]
    return [[c["lines"], c["pragmas"]] for c in singles]


def decision(full: Dict[str, Any], fast: Dict[str, Any]) -> str:
    """Kept or reverted, speed aside, after each refresh — the unit of E4's hypotheses."""
    if not full.get("usable"):
        return "full re-profile failed"
    if not fast.get("usable"):
        return "fast refresh unusable: the agent falls back to the full re-profile"
    if "exposed" in (full.get("judged"), fast.get("judged")):
        # the judgement could not stage its directives: the agent keeps such a rewrite and leaves the question to
        # the final annotation — neither "kept with these directives" nor "reverted", so it is counted apart
        return "judgement left to the final annotation after one of the two"
    kf, ku = kept_directives(full), kept_directives(fast)
    if kf is None and ku is None:
        return "reverted after both"
    if kf is not None and ku is not None:
        return "kept after both, the same directives" if kf == ku else "kept after both, other directives"
    return "kept only after the full re-profile" if kf is not None else "kept only after the fast refresh"


def trials(runs: List[str], arm: str, only: Optional[str]) -> Iterator[Path]:
    for run in runs:
        root = campaign.find_run(run)
        if root is None:
            raise SystemExit(f"run {run} is not in the archive")
        for t in sorted(root.glob(f"benchmarks/*/*/{arm}/*/rep*")):
            if (t / "trial.json").is_file() and (t / "agent_patches" / "candidates.jsonl").is_file():
                if only is None or f"{t.parts[-5]}/{t.parts[-4]}" == only:
                    yield t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="comma-separated run ids (found through the registry)")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", help="one benchmark, SUITE/NAME")
    ap.add_argument("--limit", type=int, default=0, help="stop after N rewrites (a smoke)")
    ap.add_argument("--no-judge", action="store_true", help="the verdicts only, without the gate's safety checks")
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    runs = [r for r in a.runs.split(",") if r]
    results = out / "results.jsonl"
    done = {(json.loads(ln)["trial"], json.loads(ln)["n"]) for ln in results.read_text().splitlines() if ln.strip()} \
        if results.is_file() else set()
    manifest: Dict[str, Any] = {
        "tool": "refresh_replay.py", "runs": runs, "arm": a.arm, "only": a.only, "host": platform.node(),
        "commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "discopop_pass_sha256": pass_digest(), "judged": not a.no_judge, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "trials": 0, "passed": 0, "replayable": 0, "base_unknown": 0, "kept_chain_broken": 0, "before_profile_failed": 0}
    cwd = Path.cwd()
    n_done = 0
    root = Path(tempfile.mkdtemp(prefix="refresh_replay_"))
    try:
        for trial in trials(runs, a.arm, a.only):
            tj = json.loads((trial / "trial.json").read_text())
            bench_id = str(tj["benchmark"])
            editable = tj.get("editable")
            kernel_file = str(editable[0]) if isinstance(editable, list) and editable else \
                (str(editable).split(",")[0] if editable else f"{tj['kernel']}.c")
            rel = "/".join(trial.parts[-7:])     # run/benchmarks/suite/kernel/arm/model/rep
            rewrites, counts = rewrites_of(trial, kernel_file)
            manifest["trials"] += 1
            for k in ("passed", "replayable", "base_unknown", "kept_chain_broken"):
                manifest[k] += counts[k]
            verdict_lines = VERDICT_LINE.findall((trial / "agent.log").read_text(errors="replace")) \
                if (trial / "agent.log").is_file() else []
            logged = verdict_lines if len(verdict_lines) == counts["passed"] else None
            by_pre: Dict[str, List[Dict[str, Any]]] = {}
            for rw in rewrites:
                by_pre.setdefault(hashlib.sha256(rw["pre"].encode()).hexdigest(), []).append(rw)
            passed_order = [int(json.loads(ln)["n"]) for ln in (trial / "agent_patches" / "candidates.jsonl").read_text().splitlines()
                            if ln.strip() and str(json.loads(ln).get("phase")) == "A" and json.loads(ln).get("passed")]
            for pre_hash, group in by_pre.items():
                todo = [rw for rw in group if (rel, rw["n"]) not in done]
                if not todo:
                    continue
                log_path = out / "logs" / (rel.replace("/", "__") + f"__{pre_hash[:8]}.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a") as log:
                    original = (trial / "agent_patches" / f"{kernel_file}.original").read_text()
                    bench = Bench(root / "work", PREPARED / bench_id, kernel_file, list(tj["agent_cmd"]), log,
                                  original, not a.no_judge)
                    t0 = time.monotonic()
                    ok_before = bench.profile_before(todo[0]["pre"])
                    before_s = round(time.monotonic() - t0, 2)
                    for rw in todo:
                        rec: Dict[str, Any] = {"trial": rel, "run": trial.parts[-7], "benchmark": bench_id, "arm": a.arm,
                                               "repeat": tj.get("repeat"), "n": rw["n"], "region_id": rw["region_id"],
                                               "base": "original" if rw["base"] == 0 else f"after kept rewrite {rw['base']}",
                                               "kept_in_trial": rw["kept"],
                                               "trial_verdict": logged[passed_order.index(rw["n"])] if logged else None,
                                               "before_profile_ok": ok_before, "before_profile_seconds": before_s}
                        if not ok_before:
                            manifest["before_profile_failed"] += 1
                            rec["class"] = "profile before the rewrite failed"
                        else:
                            rec["fast"] = bench.fast(rw["pre"], rw["post"], rw["diff"])
                            rec["full"] = bench.full(rw["pre"], rw["post"], rw["diff"])
                            rec["full2"] = bench.full(rw["pre"], rw["post"], rw["diff"])
                            rec["class"] = classify(rec["full"], rec["fast"])
                            rec["control_class"] = classify(rec["full"], rec["full2"]).replace(
                                "fast refresh unusable: the agent falls back to the full re-profile", "second full re-profile failed")
                            if not a.no_judge:
                                rec["decision"] = decision(rec["full"], rec["fast"])
                                rec["control_decision"] = decision(rec["full"], rec["full2"]).replace(
                                    "fast refresh unusable: the agent falls back to the full re-profile", "second full re-profile failed")
                        with open(results, "a") as f:
                            f.write(json.dumps(rec) + "\n")
                        n_done += 1
                        print(f"{rel} #{rw['n']}: {rec['class']}" + (f" -> {rec['decision']}" if "decision" in rec else "")
                              + (f"  [full {rec['full'].get('status')} {rec['full'].get('seconds')} s · fast "
                                 f"{rec['fast'].get('status', 'unusable')} {rec['fast'].get('seconds')} s · trial said {rec['trial_verdict']}]"
                                 if "full" in rec else ""), flush=True)
                        if a.limit and n_done >= a.limit:
                            raise StopIteration
                    os.chdir(cwd)
    except StopIteration:
        pass
    finally:
        os.chdir(cwd)
        shutil.rmtree(root, ignore_errors=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["rewrites_written"] = n_done
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({k: manifest[k] for k in ("trials", "passed", "replayable", "base_unknown", "kept_chain_broken",
                                               "before_profile_failed", "rewrites_written")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
