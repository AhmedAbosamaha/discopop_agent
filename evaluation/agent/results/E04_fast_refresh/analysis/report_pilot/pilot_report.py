#!/usr/bin/env python3
"""E4 step 2, the mechanism pilot — no model. For a rewrite whose reduction the fast refresh loses: rebuild the
fast-refreshed profile with the replay tool, feed a HAND-WRITTEN dependence report through the agent's own
`reconstruct`, run the explorer again and judge the rewrite again. Run on the Mac on 12 Oct (TSVC loops only).

    venv/bin/python evaluation/agent/results/E04_fast_refresh/analysis/report_pilot/pilot_report.py OUT_DIR [LOOP]

The output of the run of 12 Oct is `pilot_report_output.txt`.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "evaluation/agent/tools"))
sys.path.insert(0, str(REPO / "evaluation/shared"))
import refresh_replay as rr  # noqa: E402

R = REPO / "evaluation/agent/results"
CASES = [
    ("e3b_1/benchmarks/tsvc_c4/s316/default_v5/claude-haiku-4-5-20251001/rep1", 1, {
        "inner RAW only": "LOOP 9 RAW x 10 10",
        "inner RAW+WAW, outer WAW": "LOOP 9 RAW x 10 10\nLOOP 9 WAW x 10 10\nLOOP 7 WAW x 8 8",
        "says independent": "LOOP 9 NONE\nLOOP 7 NONE"}),
    ("e3b_2/benchmarks/tsvc_c4/s319/default_v5/claude-haiku-4-5-20251001/rep1", 2, {
        "inner RAW only": "LOOP 8 RAW sum 11 11",
        "inner RAW+WAW, outer WAW": "LOOP 8 RAW sum 11 11\nLOOP 8 WAW sum 11 11\nLOOP 6 WAW sum 7 7\nLOOP 6 WAW a 9 9\nLOOP 6 WAW b 10 10"}),
    ("e3b_2/benchmarks/tsvc_c4/s3113/default_v5/claude-haiku-4-5-20251001/rep2", 1, {
        "inner RAW only": "LOOP 8 RAW max 10 10",
        "inner RAW+WAW, outer WAW": "LOOP 8 RAW max 10 10\nLOOP 8 WAW max 10 10\nLOOP 6 WAW max 7 7"}),
]


def brief(res):
    out = {"status": res.get("status"), "judged": res.get("judged"),
           "exposed": [(e[0], e[1], e[2], e[3]) for e in res.get("exposed", [])],
           "checks": [(c["lines"], c["pragmas"], "passed" if c["passed"] else c["stage"]) for c in res.get("checks", [])]}
    return json.dumps(out)


def main() -> int:
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    only = sys.argv[2] if len(sys.argv) > 2 else None
    root = Path(tempfile.mkdtemp(prefix="pilot_report_"))
    cwd = Path.cwd()
    from discopop_agent.llm.dep_reconstruct import reconstruct
    from discopop_agent.profiling import fast_refresh
    from discopop_agent.profiling.tools import run_explorer
    from discopop_agent.evidence.blockers import load_all_prevented
    try:
        for rel, n, reports in CASES:
            if only and only not in rel:
                continue
            trial = next(p for p in R.glob(f"*/runs/{rel}") if p.is_dir())
            tj = json.loads((trial / "trial.json").read_text())
            kernel = str(tj["editable"][0]) if isinstance(tj.get("editable"), list) else f"{tj['kernel']}.c"
            rw = next(x for x in rr.rewrites_of(trial, kernel)[0] if x["n"] == n)
            print(f"\n===== {rel.split('/benchmarks/')[1]} #{n}", flush=True)
            with open(out / (rel.replace("/", "__") + ".log"), "a") as log:
                original = (trial / "agent_patches" / f"{kernel}.original").read_text()
                bench = rr.Bench(root / "work", rr.PREPARED / str(tj["benchmark"]), kernel, list(tj["agent_cmd"]), log,
                                 original, True)
                assert bench.profile_before(rw["pre"]), "profile before failed"
                fast = bench.fast(rw["pre"], rw["post"], rw["diff"])
                print("FAST          :", fast.get("note"))
                print("               ", brief(fast))
                prof = (bench.dp / "profiler").resolve()
                red = (prof / "reduction.txt").read_text() if (prof / "reduction.txt").is_file() else "(no reduction.txt)"
                print("reduction.txt after the fast refresh:", " | ".join(x.strip() for x in red.splitlines()) or "(empty)")
                stat = (prof / "static_dependencies.txt").read_text().splitlines() if (prof / "static_dependencies.txt").is_file() else []
                prevented = load_all_prevented(bench.dp)
                print(f"static_dependencies.txt: {len(stat)} lines; doall_prevented records: {len(prevented)}; "
                      f"origins: {sorted({str(b.get('origin')) for b in prevented})}")
                for b in prevented[:6]:
                    print("    prevented:", {k: b.get(k) for k in ("loop_start", "loop_end", "var_name", "dep_type", "origin")})
                snap = root / "fast_profile"
                shutil.rmtree(snap, ignore_errors=True)
                shutil.copytree(bench.dp, snap)
                lmap = fast_refresh.line_map(rw["pre"], rw["post"])
                nl = len(rw["post"].splitlines())
                rewritten = {k for k in range(1, nl + 1) if k not in set(lmap.values())}
                print("rewritten lines:", sorted(rewritten))
                for name, reply in reports.items():
                    shutil.rmtree(bench.dp, ignore_errors=True)
                    shutil.copytree(snap, bench.dp)
                    bench.src.write_text(rw["post"])
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        rep = reconstruct(prof, "", [], rewritten, "", reply=reply, audit_path=out / "llm_recon.json",
                                          source_file=bench.args.source_file, source_lines=rw["post"].splitlines())
                        rc = run_explorer(bench.dp).returncode if rep.rows else None
                    bench.gate_cache.setdefault("report:" + name, {})
                    res = bench.verdict(rw["diff"])
                    if res["status"] == "exposed":
                        res.update(bench.judged("report:" + name, rw["pre"]))
                    print(f"REPORT [{name}]: {rep.summary()} | rows {rep.rows} | unresolved "
                          f"{[(c.var, why) for c, why in rep.unresolved]} | contradicted {rep.contradicted} | explorer rc {rc}")
                    print("               ", brief(res))
                full = bench.full(rw["pre"], rw["post"], rw["diff"])
                print("FULL          :", brief(full))
                red = (prof / "reduction.txt").read_text() if (prof / "reduction.txt").is_file() else ""
                print("reduction.txt after the full re-profile:", " | ".join(x.strip() for x in red.splitlines()) or "(empty)")
            import os
            os.chdir(cwd)
    finally:
        import os
        os.chdir(cwd)
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
