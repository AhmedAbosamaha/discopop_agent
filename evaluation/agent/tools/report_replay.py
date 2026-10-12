#!/usr/bin/env python3
"""E4 step 2 — the model's own account of the dependences of its rewrite, replayed on the saved rewrites.

For each selected pragma-free rewrite that passed the checks in an archived trial (the population of step 1,
`refresh_replay.py`), in the trial's own configuration:

  1. the program before the rewrite is profiled in full, and the rewritten program gets a FAST refresh from that
     profile — as step 1; DiscoPoP's verdict and the safety half of the agent's judgement are taken again;
  2. THE REPORT (`--llm-recon`, the separate request): from that refreshed profile, the request the agent sends
     after a rewrite has passed the checks (`dep_reconstruct.ask_after_gate`: the rewritten lines with six lines
     around them, the loops shown) goes to the model; its reply goes through the agent's own `reconstruct` (parsed,
     resolved, placed rows appended to the dependence file), the explorer runs again where a row was placed, and
     the rewrite is judged again;
  3. THE DELETION (`--llm-deps`): from the refreshed profile again — the agent never combines the two — the
     agent's own `_llm_dep_review` asks the model which of DiscoPoP's static Do-All blockers in the rewritten
     lines are not real, removes those, runs the explorer again, and the rewrite is judged again;
  4. the full re-profile, judged the same way: what each of the above is compared with.

`--report dry` / `--deletion dry` build every request exactly as the agent would and record it WITHOUT calling a
model (the reply is empty, so nothing is merged or removed): how many calls a run would make, and where the
deletion has anything to ask about. `ask` makes the calls. The model and provider are the trial's own.

A replay has no earlier conversation: under the SDK provider the live agent resumes the session in which the model
wrote the rewrite; here the request is sent alone, in a session of its own.

A rewrite whose model call failed is not written to the results — a resumed run asks again — and three failures
in a row stop the run.

    venv/bin/python evaluation/agent/tools/report_replay.py --runs e3b_1,e3b_2 --arm default_v5 \\
        --report dry --deletion dry --out /tmp/x [--select FILE] [--select-deletion FILE] [--only SUITE/NAME]
        [--limit N] [--no-full]

`--select` names the rewrites the report is asked on and `--select-deletion` those the deletion is asked on (by
default the same); a rewrite in either list is replayed, and gets only what its list asks for.

Output: `<out>/results.jsonl` (one record per rewrite), `<out>/manifest.json`, `<out>/logs/`.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
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
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refresh_replay as rr  # noqa: E402

FAILED_REVIEW = "dependence review unavailable"


def followup_request(pre: str, post: str) -> Optional[Tuple[str, List[str], List[int]]]:
    """The excerpt and the loop list of the request sent after a rewrite has passed the checks, built as phase A
    builds them (`phases/phase_a.py`, the `followup` branch of `--llm-recon`): the lines the rewrite added or
    changed with six lines around them, each with its line number, and the header lines of the loops shown.
    None when the rewrite left no new line — phase A then asks nothing."""
    from discopop_agent.profiling import fast_refresh
    lines = post.splitlines()
    lm = fast_refresh.line_map(pre or "", post)
    new = {n for n in range(1, len(lines) + 1) if n not in set(lm.values())}
    if not new:
        return None
    lo, hi = max(min(new) - 6, 1), min(max(new) + 6, len(lines))
    excerpt = "\n".join(f"{n:4d}  {lines[n - 1]}" for n in range(lo, hi + 1))
    loops = [str(n) for n in range(lo, hi + 1) if re.match(r"\s*(for|while)\s*\(", lines[n - 1])]
    return excerpt, loops, sorted(new)


def without_claims_inside_independent_loops(reply: str, post: str) -> Tuple[str, List[List[Any]]]:
    """A WHAT-IF, not the agent as built (`--placement respect-none`): the reply with every claimed dependence left
    out whose two lines both lie inside a loop that the same reply declares independent (`LOOP <line> NONE`).

    As built, a claim is placed by its two lines and its variable; the loop the model names for it is not carried
    into the dependence file, so a dependence claimed for one loop also counts against every other loop around both
    lines — including one the reply itself calls independent. Returns the filtered reply (in the format the agent's
    parser reads) and the claims left out."""
    from discopop_agent.llm.dep_reconstruct import parse_claims
    from discopop_agent.pragmas.parse import _loop_span
    lines = post.splitlines()
    claims, clean = parse_claims(reply)
    spans = []
    for head in clean:
        sp = _loop_span(lines, head - 1) if 1 <= head <= len(lines) else None
        if sp is not None:
            spans.append((sp[0] + 1, sp[1] + 1))
    keep: List[Any] = []
    dropped: List[Any] = []
    for c in claims:
        inside = any(a <= c.writer_line <= b and a <= c.reader_line <= b for a, b in spans)
        (dropped if inside else keep).append(c)
    text = "\n".join([f"LOOP {c.loop_line} {c.dep_type} {c.var} {c.writer_line} {c.reader_line}" for c in keep]
                     + [f"LOOP {h} NONE" for h in clean])
    return text, [[c.loop_line, c.dep_type, c.var, c.writer_line, c.reader_line] for c in dropped]


class _Calls:
    """Stands in for a module's `_complete`: records each request, and in dry mode answers nothing."""

    def __init__(self, module: Any, dry: bool, usage_log: Path):
        self.module, self.dry, self.usage_log = module, dry, usage_log
        self.real = module._complete
        self.made: List[Dict[str, Any]] = []

    def __enter__(self) -> "_Calls":
        def _complete(provider: str, client: Any, model: str, convo: List[Dict[str, str]], system: str,
                      **kw: Any) -> str:
            rec: Dict[str, Any] = {"model": model, "provider": provider, "messages_sent": len(convo),
                                   "system_sha256": hashlib.sha256(system.encode()).hexdigest()[:16],
                                   "system_chars": len(system), "prompt": convo[-1]["content"]}
            self.made.append(rec)
            if self.dry:
                return ""
            before = len(self.usage_log.read_text().splitlines()) if self.usage_log.is_file() else 0
            t0 = time.monotonic()
            reply = str(self.real(provider, client, model, convo, system, **kw))
            rec["seconds"] = round(time.monotonic() - t0, 2)
            rec["reply"] = reply
            used = self.usage_log.read_text().splitlines()[before:] if self.usage_log.is_file() else []
            rec["usage"] = [json.loads(u) for u in used]
            rec["cost_usd"] = round(sum(float(u.get("cost_usd") or 0) for u in rec["usage"]), 6)
            return reply

        self.module._complete = _complete
        return self

    def __exit__(self, *exc: Any) -> None:
        self.module._complete = self.real


class ReportBench(rr.Bench):
    """Step 1's work directory with the two things step 2 adds on top of a fast refresh."""

    def keep_refreshed(self) -> None:
        self.refreshed = self.work / "_profile_refreshed"
        shutil.rmtree(self.refreshed, ignore_errors=True)
        shutil.copytree(self.dp, self.refreshed)

    def back_to_refreshed(self, post: str) -> None:
        self.src.write_text(post)
        shutil.rmtree(self.dp, ignore_errors=True)
        shutil.copytree(self.refreshed, self.dp)

    def _judge(self, arm: str, rw: Dict[str, Any], res: Dict[str, Any]) -> None:
        self.gate_cache.setdefault(arm, {})
        res.update(self.verdict(rw["diff"]))
        if self.judge and res["status"] == "exposed":
            res.update(self.judged(arm, rw["pre"]))

    def report(self, rw: Dict[str, Any], key: str, dry: bool, usage_log: Path, saved_reply: Optional[str] = None,
               placement: str = "as-built") -> Dict[str, Any]:
        """Phase A's `--llm-recon` step in the `followup` form, on the refreshed profile now in place. With
        `saved_reply`, no model is called: a reply an earlier run recorded is placed again."""
        from discopop_agent.llm import dep_reconstruct
        from discopop_agent.profiling.tools import run_explorer
        a = self.args
        self.back_to_refreshed(rw["post"])
        req = followup_request(rw["pre"], rw["post"])
        if req is None:
            return {"asked": False, "why": "the rewrite left no new line: the agent asks nothing"}
        excerpt, loops, new = req
        res: Dict[str, Any] = {"asked": True, "dry": dry, "new_lines": new, "loops": loops}
        if saved_reply is not None:
            reply = saved_reply
            res.update(replayed=True, placement=placement, request={"reply": saved_reply})
            if placement == "respect-none":
                reply, left_out = without_claims_inside_independent_loops(saved_reply, rw["post"])
                res["claims_left_out"] = left_out
        else:
            with _Calls(dep_reconstruct, dry, usage_log) as calls:
                try:
                    with contextlib.redirect_stdout(self.log):
                        reply = dep_reconstruct.ask_after_gate(
                            excerpt, loops, a.model, session_key=f"replay:{key}", messages=None, api_key=a.api_key,
                            provider=a.provider, api_base=a.api_base)
                except Exception as e:                   # noqa: BLE001 - recorded; the rewrite is asked again
                    res.update(call_failed=True, error=str(e)[:300], request=calls.made[-1] if calls.made else None)
                    return res
            res["request"] = calls.made[-1] if calls.made else None
            if dry:
                return res
        res["reply_empty"] = not reply
        res["profile_changed"] = False                   # True only where a row was placed in the dependence file
        if reply:                                        # phase A: `if args.llm_recon and reply_text:`
            audit = self.work / "_refresh" / "llm_recon.json"
            audit.unlink(missing_ok=True)
            with contextlib.redirect_stdout(self.log):
                rep = dep_reconstruct.reconstruct(
                    (self.dp / "profiler").resolve(), "", [], set(new), a.model, reply=reply, audit_path=audit,
                    source_file=a.source_file, source_lines=rw["post"].splitlines())
                explorer_rc = run_explorer(self.dp).returncode if rep.rows else None
            res.update(summary=rep.summary(), claims=[[c.loop_line, c.dep_type, c.var, c.writer_line, c.reader_line]
                                                      for c in rep.claims],
                       loops_declared_independent=list(rep.loops_declared_clean), rows=list(rep.rows),
                       unresolved=[[c.loop_line, c.dep_type, c.var, c.writer_line, c.reader_line, why]
                                   for c, why in rep.unresolved],
                       contradicting_static=[list(x) for x in rep.contradicted], explorer_rc=explorer_rc,
                       profile_changed=bool(rep.rows))
        self._judge("report", rw, res)
        return res

    def deletion(self, rw: Dict[str, Any], dry: bool, usage_log: Path) -> Dict[str, Any]:
        """Phase A's `--llm-deps` step, on the refreshed profile now in place."""
        from discopop_agent.evidence.blockers import load_all_prevented
        from discopop_agent.llm import dep_review
        from discopop_agent.profiling.runner import _file_id_of
        a = self.args
        self.back_to_refreshed(rw["post"])
        prevented = load_all_prevented(self.dp)
        origins: Dict[str, int] = {}
        for b in prevented:
            o = str(b.get("origin", "")).split(".")[-1]
            origins[o] = origins.get(o, 0) + 1
        res: Dict[str, Any] = {"dry": dry, "blockers_recorded": len(prevented), "blockers_by_origin": origins}
        out = self.work / "_refresh" / "deletion"
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        fid = _file_id_of(self.dp, self.src)
        with _Calls(dep_review, dry, usage_log) as calls:
            with contextlib.redirect_stdout(self.log):
                note = dep_review._llm_dep_review(a, self.dp, rw["pre"], rw["post"], out, int(fid) if fid else 1)
        res.update(asked=bool(calls.made), note=str(note)[:300], request=calls.made[-1] if calls.made else None,
                   profile_changed="removed, recorded" in str(note))
        if (out / "llm_deps.json").is_file():
            res["reviewed"] = json.loads((out / "llm_deps.json").read_text())[-1].get("reviewed")
        if calls.made and not dry and FAILED_REVIEW in str(note):
            res["call_failed"] = True
            return res
        if dry or not calls.made:
            return res
        self._judge("deletion", rw, res)
        return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="comma-separated run ids (found through the registry)")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", choices=("dry", "ask", "replay"), help="the model's report of the dependences")
    ap.add_argument("--replies", type=Path,
                    help="with --report replay: the directory of an earlier run whose recorded replies are placed again (no model)")
    ap.add_argument("--placement", choices=("as-built", "respect-none"), default="as-built",
                    help="with --report replay — respect-none (a what-if, not the agent as built): a claimed dependence is left "
                         "out where both of its lines lie inside a loop the same reply declares independent")
    ap.add_argument("--deletion", choices=("dry", "ask"), help="the model's review of static blockers")
    ap.add_argument("--select", type=Path, help="a JSON list of {trial, n}: only these rewrites")
    ap.add_argument("--select-deletion", type=Path,
                    help="a JSON list of {trial, n}: the rewrites the deletion is asked on (default: those of --select)")
    ap.add_argument("--only", help="one benchmark, SUITE/NAME")
    ap.add_argument("--limit", type=int, default=0, help="stop after N rewrites (a smoke)")
    ap.add_argument("--no-full", action="store_true", help="without the full re-profile (a dry pass needs none)")
    a = ap.parse_args()
    if not a.report and not a.deletion:
        ap.error("nothing to do: give --report and/or --deletion")
    if (a.report == "replay") != bool(a.replies):
        ap.error("--report replay and --replies go together")
    replies: Dict[Tuple[str, int], str] = {}
    if a.replies:
        for f in sorted(a.replies.resolve().glob("*/results.jsonl")):
            for ln in f.read_text().splitlines():
                if ln.strip():
                    r0 = json.loads(ln)
                    q0 = (r0.get("report") or {}).get("request") or {}
                    if "reply" in q0:
                        replies[(r0["trial"], int(r0["n"]))] = str(q0["reply"])
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    runs = [r for r in a.runs.split(",") if r]
    chosen = {(x["trial"], int(x["n"])) for x in json.loads(a.select.read_text())} if a.select else None
    chosen_del = {(x["trial"], int(x["n"])) for x in json.loads(a.select_deletion.read_text())} \
        if a.select_deletion else chosen
    results = out / "results.jsonl"
    done = {(json.loads(ln)["trial"], json.loads(ln)["n"]) for ln in results.read_text().splitlines() if ln.strip()} \
        if results.is_file() else set()
    usage_log = out / "usage.jsonl"
    os.environ["DP_LLM_USAGE_LOG"] = str(usage_log)
    manifest: Dict[str, Any] = {
        "tool": "report_replay.py", "runs": runs, "arm": a.arm, "only": a.only, "report": a.report,
        "replies": str(a.replies) if a.replies else None, "placement": a.placement if a.replies else None,
        "deletion": a.deletion, "select": str(a.select) if a.select else None,
        "select_deletion": str(a.select_deletion) if a.select_deletion else None, "host": platform.node(),
        "commit": subprocess.run(["git", "-C", str(rr.REPO), "rev-parse", "HEAD"], capture_output=True,
                                 text=True).stdout.strip(),
        "discopop_pass_sha256": rr.pass_digest(), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "trials": 0, "rewrites_written": 0, "before_profile_failed": 0, "report_calls": 0, "deletion_calls": 0,
        "calls_failed": 0, "cost_usd": 0.0}
    cwd = Path.cwd()
    failed_in_a_row = 0
    root = Path(tempfile.mkdtemp(prefix="report_replay_"))
    try:
        for trial in rr.trials(runs, a.arm, a.only):
            tj = json.loads((trial / "trial.json").read_text())
            bench_id = str(tj["benchmark"])
            editable = tj.get("editable")
            kernel_file = str(editable[0]) if isinstance(editable, list) and editable else \
                (str(editable).split(",")[0] if editable else f"{tj['kernel']}.c")
            rel = "/".join(trial.parts[-7:])
            rewrites, _counts = rr.rewrites_of(trial, kernel_file)
            rewrites = [rw for rw in rewrites if chosen is None or (rel, rw["n"]) in chosen
                        or (chosen_del is not None and (rel, rw["n"]) in chosen_del)]
            if not rewrites:
                continue
            manifest["trials"] += 1
            by_pre: Dict[str, List[Dict[str, Any]]] = {}
            for rw in rewrites:
                by_pre.setdefault(hashlib.sha256(rw["pre"].encode()).hexdigest(), []).append(rw)
            for pre_hash, group in by_pre.items():
                todo = [rw for rw in group if (rel, rw["n"]) not in done]
                if not todo:
                    continue
                log_path = out / "logs" / (rel.replace("/", "__") + f"__{pre_hash[:8]}.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a") as log:
                    original = (trial / "agent_patches" / f"{kernel_file}.original").read_text()
                    bench = ReportBench(root / "work", rr.PREPARED / bench_id, kernel_file, list(tj["agent_cmd"]), log,
                                        original, True)
                    ok_before = bench.profile_before(todo[0]["pre"])
                    for rw in todo:
                        rec: Dict[str, Any] = {"trial": rel, "run": trial.parts[-7], "benchmark": bench_id,
                                               "arm": a.arm, "repeat": tj.get("repeat"), "n": rw["n"],
                                               "region_id": rw["region_id"], "kept_in_trial": rw["kept"],
                                               "model": bench.args.model, "before_profile_ok": ok_before}
                        failed = False
                        if not ok_before:
                            manifest["before_profile_failed"] += 1
                        else:
                            rec["fast"] = bench.fast(rw["pre"], rw["post"], rw["diff"])
                            if rec["fast"].get("usable"):
                                bench.keep_refreshed()
                                key = (rel, rw["n"])
                                if a.report == "replay":
                                    if key in replies and (chosen is None or key in chosen):
                                        rec["report"] = bench.report(rw, "", False, usage_log, saved_reply=replies[key],
                                                                     placement=a.placement)
                                elif a.report and (chosen is None or key in chosen):
                                    rec["report"] = bench.report(rw, f"{rel}#{rw['n']}:{time.time_ns()}",
                                                                 a.report == "dry", usage_log)
                                if a.deletion and (chosen_del is None or key in chosen_del):
                                    rec["deletion"] = bench.deletion(rw, a.deletion == "dry", usage_log)
                            if not a.no_full:
                                rec["full"] = bench.full(rw["pre"], rw["post"], rw["diff"])
                            for arm, count in (("report", "report_calls"), ("deletion", "deletion_calls")):
                                part = rec.get(arm) or {}
                                if part.get("asked") and part.get("request") and not part.get("replayed"):
                                    manifest[count] += 1
                                    manifest["cost_usd"] += float((part["request"] or {}).get("cost_usd") or 0)
                                failed = failed or bool(part.get("call_failed"))
                        if failed:
                            # never counted: left out of the results, so that a resumed run asks again
                            manifest["calls_failed"] += 1
                            failed_in_a_row += 1
                            with open(out / "call_failed.jsonl", "a") as f:
                                f.write(json.dumps(rec) + "\n")
                            print(f"{rel} #{rw['n']}: MODEL CALL FAILED — not counted", flush=True)
                            if failed_in_a_row >= 3:
                                raise StopIteration
                            continue
                        failed_in_a_row = 0
                        with open(results, "a") as f:
                            f.write(json.dumps(rec) + "\n")
                        manifest["rewrites_written"] += 1
                        rp, dl = rec.get("report") or {}, rec.get("deletion") or {}
                        print(f"{rel} #{rw['n']}: fast {rec.get('fast', {}).get('status', '-')}/"
                              f"{rec.get('fast', {}).get('judged', '-')}"
                              + (f" · report {'asked' if rp.get('asked') else 'not asked'}"
                                 f"{'' if rp.get('dry', True) else ' → ' + str(rp.get('status')) + '/' + str(rp.get('judged'))}"
                                 if a.report else "")
                              + (f" · deletion {'asked' if dl.get('asked') else 'nothing to ask'}"
                                 f" ({dl.get('blockers_by_origin')})"
                                 f"{'' if dl.get('dry', True) or not dl.get('asked') else ' → ' + str(dl.get('status')) + '/' + str(dl.get('judged'))}"
                                 if a.deletion else "")
                              + (f" · full {rec['full'].get('status')}/{rec['full'].get('judged')}" if "full" in rec else ""),
                              flush=True)
                        if a.limit and manifest["rewrites_written"] >= a.limit:
                            raise StopIteration
                    os.chdir(cwd)
    except StopIteration:
        pass
    finally:
        os.chdir(cwd)
        shutil.rmtree(root, ignore_errors=True)
    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["cost_usd"] = round(manifest["cost_usd"], 4)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({k: manifest[k] for k in ("trials", "rewrites_written", "before_profile_failed", "report_calls",
                                               "deletion_calls", "calls_failed", "cost_usd")}))
    return 1 if failed_in_a_row >= 3 else 0


if __name__ == "__main__":
    sys.exit(main())
