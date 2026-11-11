#!/usr/bin/env python3
"""E7 — the gate as a classifier: every candidate the gate judged, judged again by the harness. No model.

The agent's gate accepted or refused every candidate change of a trial; the harness judged only each trial's
FINAL program. So what the gate refused was never judged by anything else, and neither was what it accepted on
the way and the agent later undid. This tool closes that: it rebuilds every saved candidate as the gate saw it,
has the harness judge each distinct program, replays the gate's checks one at a time, and reads the two against
each other (record §6: the design of 9 Oct 2026 and its reopening on 11 Nov 2026).

    corpus    rebuild every candidate of the given runs from the archive (text only) and write the distinct
              programs with a table of the candidates and the gate's recorded verdicts
    judge     (server) the harness on each distinct program: J1 `verify-source` exactly as a trial is judged;
              J2, for a program that holds a directive, the harness's build at the verification size under
              ThreadSanitizer with archer, 12 threads, 3 runs
    checks    (server) the gate again on each candidate, at the gate's own size: the whole safety gate (the
              fidelity against the recorded verdict), then each check on its own
    readout   the tables: gate x judge, each check alone, the second input

Programs are keyed by sha256(benchmark, NUL, text of the benchmark's file): the same text judged in two trials is
one program. A candidate that cannot be rebuilt is listed by name and left out, never silently.
"""
from __future__ import annotations

import argparse
import collections
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
from typing import Any, Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
EVAL = HERE.parents[1]
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EVAL / "shared"))   # cli.py's run store
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402

PREPARED = HERE.parent / "prepared"
OMP_ADDED = re.compile(r"^\+\s*#\s*pragma\s+omp\b", re.M)
OMP_LINE = re.compile(r"^\s*#\s*pragma\s+omp\b", re.M)
SEED = "7"                      # the campaign's perturbed input (`--check-input 7`, the harness's `--check-seed 7`)
RIGHT = ("FASTER", "parallel-not-faster", "parallel-speed-not-measurable", "changed-not-parallel", "no-change")


def sha_of(bench: str, text: str) -> str:
    return hashlib.sha256((bench + "\0" + text).encode()).hexdigest()


def _body(text: str) -> str:
    return "\n".join(ln.rstrip() for ln in text.splitlines() if not ln.startswith(("--- ", "+++ "))).strip()


def _meta(bench: str) -> Dict[str, Any]:
    return dict(json.loads((PREPARED / bench / "meta.json").read_text()))


# ------------------------------------------------------------------------------------------------ corpus


def _apply(base: str, patch_text: str, name: str, exact: bool, tmp: Path) -> Optional[str]:
    """`patch_text` on `base`, the way the gate applies a candidate (`gate.patching`)."""
    from discopop_agent.gate.patching import fix_hunk_headers, run_patch

    dst = tmp / name
    dst.write_text(base)
    lines = [(f"--- {dst}" if ln.startswith("--- ") else f"+++ {dst}" if ln.startswith("+++ ") else ln)
             for ln in fix_hunk_headers(patch_text).splitlines()]
    pp = tmp / "candidate.patch"
    pp.write_text("\n".join(lines) + "\n")
    ok, _ = run_patch(dst, pp, exact=exact)
    return dst.read_text() if ok else None


def build_corpus(runs: List[str], out: Path, name: str) -> Dict[str, Any]:
    """Replay every trial's candidates in the order the agent judged them (the pre-flight's replay, 9 Oct):
    a model's rewrite (phase A) on the kept state; DiscoPoP's directives for it (A-D40) on the rewritten text; the
    rewrite then kept exactly when `accepted.json` holds its patch; the final pass (B) and the floor step one
    directive after the other. A trial's history counts as verified when its end state equals the archived final
    file byte for byte."""
    tmp = Path(tempfile.mkdtemp(prefix="e7_corpus_"))
    programs: Dict[str, Dict[str, Any]] = {}
    texts: Dict[str, str] = {}
    cands: List[Dict[str, Any]] = []
    not_rebuilt: List[str] = []
    not_verified: List[str] = []
    package_differs: set[str] = set()         # the harness judges against the package: it must be the trial's original
    n_trials = 0

    def keep(bench: str, fname: str, text: str) -> str:
        h = sha_of(bench, text)
        if h not in programs:
            programs[h] = {"benchmark": bench, "file": fname, "directive": bool(OMP_LINE.search(text)),
                           "final_of": [], "original": False}
            texts[h] = text
        return h

    for run in runs:
        root = campaign.find_run(run)
        if root is None:
            sys.exit(f"run {run} is not in the archive")
        indexes = sorted(list(root.glob("benchmarks/**/agent_patches/candidates.jsonl"))
                         + list(root.glob("benchmarks/**/agent_patches/floor/candidates.jsonl")))
        for index in indexes:
            floor = index.parent.name == "floor"      # the agent's floor step: DiscoPoP's directives on the original
            trial = index.parent.parent.parent if floor else index.parent.parent
            rel = trial.relative_to(root).parts
            bench, arm, rep = f"{rel[1]}/{rel[2]}", rel[3], rel[-1]
            fname = str(_meta(bench)["file"])
            ext = Path(fname).suffix
            o_dir, f_dir = trial / "original", trial / "final"
            orig = (o_dir / fname if o_dir.is_dir() else trial / f"original{ext}").read_text()
            fin = f_dir / fname if f_dir.is_dir() else trial / f"final{ext}"
            entries = [json.loads(ln) for ln in index.read_text().splitlines() if ln.strip()]
            ptexts = [(index.parent / e["patch"]).read_text(errors="replace") for e in entries]
            acc_file = index.parent / "accepted.json"
            acc = json.loads(acc_file.read_text()) if acc_file.is_file() else []
            kept = set()                              # the model rewrites the agent kept
            for entry in acc:
                pf = index.parent / Path(str(entry.get("patch_file") or "-")).name
                if pf.is_file():
                    hits = [i for i, e in enumerate(entries) if e.get("phase") == "A" and e.get("passed")
                            and _body(ptexts[i]) == _body(pf.read_text(errors="replace"))]
                    if hits:
                        kept.add(hits[-1])
            for f in ([x for x in sorted(o_dir.rglob("*")) if x.is_file()] if o_dir.is_dir() else []):
                pk = PREPARED / bench / f.relative_to(o_dir)
                if not pk.is_file() or pk.read_bytes() != f.read_bytes():
                    package_differs.add(f"{run} {bench}: {f.relative_to(o_dir)}")
            if not o_dir.is_dir() and (PREPARED / bench / fname).read_text() != orig:
                package_differs.add(f"{run} {bench}: {fname}")
            h_orig = keep(bench, fname, orig)
            programs[h_orig]["original"] = True
            state, tentative, keep_it, complete = orig, None, False, True
            trial_id = f"{run} {bench} {arm} {rep}" + (" floor" if floor else "")
            for i, e in enumerate(entries):
                ph = "floor" if floor else str(e.get("phase"))
                kind = "directive" if OMP_ADDED.search(ptexts[i]) else "rewrite"
                verdict = "accepted" if e.get("passed") else str(e.get("stage"))
                if ph in ("A", "B") and tentative is not None:        # the rewrite before this one is settled
                    state, tentative = (tentative if keep_it else state), None
                bases = [tentative] if ph == "A-D40" else ([state] if tentative is None else [state, tentative])
                prog, base_used = None, None
                for b in (x for x in bases if x is not None):
                    prog = _apply(b, ptexts[i], fname, True, tmp) or _apply(b, ptexts[i], fname, False, tmp)
                    if prog is not None:
                        base_used = b
                        break
                cid = f"{trial_id} n{e['n']}"
                if prog is None or base_used is None:
                    not_rebuilt.append(f"{cid} ({ph}, {kind}, {verdict})")
                    complete = False
                    continue
                cands.append({"id": cid, "run": run, "benchmark": bench, "arm": arm, "rep": rep, "n": e["n"],
                              "phase": ph, "kind": kind, "gate": verdict, "from_cache": bool(e.get("from_cache")),
                              "base": keep(bench, fname, base_used), "program": keep(bench, fname, prog),
                              "patch": str((index.parent / e["patch"]).relative_to(campaign.RESULTS))})
                if ph == "A" and e.get("passed"):
                    tentative, keep_it = prog, i in kept
                elif ph in ("B", "floor") and e.get("passed"):
                    state = prog
            if tentative is not None and keep_it:
                state = tentative
            if floor:                                 # its program is not the trial's final file
                continue
            n_trials += 1
            if fin.is_file():
                programs[keep(bench, fname, fin.read_text())]["final_of"].append(trial_id)
            if not (fin.is_file() and fin.read_text() == state and complete):
                not_verified.append(trial_id)
    shutil.rmtree(tmp, ignore_errors=True)

    # the distinct programs as files: a directory that holds the benchmark's own file, which is what
    # `verify-source` takes for a multi-file package (and the file itself for a single-file one)
    shutil.rmtree(out / "programs", ignore_errors=True)
    by_bench: Dict[str, List[str]] = collections.defaultdict(list)
    for h in sorted(programs):
        by_bench[programs[h]["benchmark"]].append(h)
    for bench, hs in by_bench.items():
        for k, h in enumerate(hs, 1):
            d = out / "programs" / bench / h[:16]
            d.mkdir(parents=True, exist_ok=True)
            (d / programs[h]["file"]).write_text(texts[h])
            programs[h]["index"] = k                  # the `--repeat` under which the harness judges it
            programs[h]["path"] = str((d / programs[h]["file"]).relative_to(out))
    judged = {c["program"] for c in cands}
    corpus = {
        "name": name, "runs": runs, "trials": n_trials, "seed": SEED,
        "commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "programs": programs, "candidates": cands, "not_rebuilt": not_rebuilt, "not_verified": not_verified,
        "package_differs": sorted(package_differs),
        "summary": {
            "candidates": len(cands) + len(not_rebuilt), "rebuilt": len(cands),
            "by_kind_and_verdict": dict(sorted(collections.Counter(f"{c['kind']} {c['gate']}" for c in cands).items())),
            "distinct_programs_judged": len(judged),
            "with_a_directive": sum(1 for h in judged if programs[h]["directive"]),
            "distinct_accepted": len({c["program"] for c in cands if c["gate"] == "accepted"}),
            "distinct_refused": len({c["program"] for c in cands if c["gate"] != "accepted"}),
            "bases_only": len(set(programs) - judged),
        },
    }
    (out / "corpus.json").write_text(json.dumps(corpus, indent=1, sort_keys=True) + "\n")
    return corpus


def cmd_corpus(a: argparse.Namespace) -> int:
    reg = campaign.load()
    groups = [g for g in a.groups.split(",") if g]
    named = [r for r in a.runs.split(",") if r]
    left_out = [r for r in a.exclude_runs.split(",") if r]
    runs = sorted(r for r, v in reg["runs"].items()
                  if v.get("status") == "valid" and (v.get("group") in groups or r in named) and r not in left_out)
    if not runs:
        sys.exit("no valid run matches --groups / --runs")
    c = build_corpus(runs, a.out, a.name)
    s = c["summary"]
    print(f"{a.name}: {len(runs)} run(s), {c['trials']} trial(s) with candidates; candidates {s['candidates']}, "
          f"rebuilt {s['rebuilt']}; distinct programs judged {s['distinct_programs_judged']} "
          f"({s['with_a_directive']} with a directive); accepted {s['distinct_accepted']}, refused "
          f"{s['distinct_refused']}; bases that are no candidate: {s['bases_only']}")
    print("by kind and the gate's verdict: " + ", ".join(f"{k} {v}" for k, v in s["by_kind_and_verdict"].items()))
    for label, rows in (("not rebuilt", c["not_rebuilt"]), ("history not verified", c["not_verified"]),
                        ("the trial's original differs from today's package", c["package_differs"])):
        print(f"{label}: {len(rows)}")
        for r in rows:
            print("  " + r)
    return 0


# ------------------------------------------------------------------------------------------------ shared


def _load(corpus_dir: Path) -> Dict[str, Any]:
    c = dict(json.loads((corpus_dir / "corpus.json").read_text()))
    if c.get("package_differs"):
        sys.exit("the corpus names trials whose original differs from today's package: the harness would judge "
                 "them against other data than the gate saw")
    return c


def _slice(items: List[str], part: str) -> List[str]:
    """`k/n`: every n-th item starting at the k-th, so that the lanes get programs of every benchmark."""
    k, n = (int(x) for x in part.split("/"))
    if not 1 <= k <= n:
        sys.exit(f"--part {part}: expected k/n with 1 <= k <= n")
    return items[k - 1::n]


def _sample(c: Dict[str, Any], spec: str, seed: int) -> List[Dict[str, Any]]:
    """The pilot's draw: so many rewrites and so many directives, with a fixed seed, over candidates sorted by id."""
    import random

    n_rw, n_dir = (int(x) for x in spec.split(","))
    rng = random.Random(seed)
    out: List[Dict[str, Any]] = []
    for kind, n in (("rewrite", n_rw), ("directive", n_dir)):
        pool = sorted((x for x in c["candidates"] if x["kind"] == kind), key=lambda x: str(x["id"]))
        out += rng.sample(pool, min(n, len(pool)))
    return out


def _per_benchmark(c: Dict[str, Any], n: int) -> List[Dict[str, Any]]:
    """The second pilot's draw: of every benchmark the candidates of its first n distinct programs (by hash), so
    that every package of a corpus goes through each step once."""
    by_bench: Dict[str, List[str]] = collections.defaultdict(list)
    for h in sorted({str(x["program"]) for x in c["candidates"]}):
        if not c["programs"][h]["original"]:
            by_bench[str(c["programs"][h]["benchmark"])].append(h)
    keep = {h for hs in by_bench.values() for h in hs[:n]}
    return [x for x in c["candidates"] if str(x["program"]) in keep]


def _draw(c: Dict[str, Any], a: argparse.Namespace) -> Optional[List[Dict[str, Any]]]:
    """A pilot's candidates (`--sample` or `--per-benchmark`), or None for the whole corpus."""
    if a.sample:
        return _sample(c, a.sample, a.seed)
    if a.per_benchmark:
        return _per_benchmark(c, a.per_benchmark)
    return None


def _pairs(cands: Iterable[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """The distinct (base, program) pairs of some candidates: the gate judges a patch on a base."""
    return sorted({(str(x["base"]), str(x["program"])) for x in cands})


def _append(path: Path, rec: Dict[str, Any]) -> None:
    with path.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def _done(path: Path, key: str) -> set[str]:
    return {str(json.loads(ln)[key]) for ln in path.read_text().splitlines() if ln.strip()} if path.is_file() else set()


def _manifest(out: Path, extra: Dict[str, Any]) -> None:
    from discopop_agent.gate.toolchain import _find_clangpp, find_archer

    m = {"tool": "gate_study.py", "host": platform.node(), "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
         "commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
         "clangpp": _find_clangpp(), "archer": find_archer(),
         "cpus_available": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()}
    m.update(extra)
    (out / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")


# ------------------------------------------------------------------------------------------------ judge


def _tsan_at_size(bench: str, prog_file: Path, runs: int, threads: int, limit: int = 1800) -> Dict[str, Any]:
    """J2: the harness's build of the program at the verification size, under ThreadSanitizer with archer.

    The build is `cli.verify`'s own (`-O2`, the size flag, every unit of a multi-file package, the harness's
    toolchain flags) with `-fsanitize=thread -g` added; the runs use the gate's ThreadSanitizer environment
    (`halt_on_error=1`, archer when found) and the gate's test for a report."""
    import cli
    from discopop_agent.gate.toolchain import _tsan_env

    bench_dir = cli._prepared_benchmarks()[bench]
    src_name = cli._source_name(bench_dir)
    is_c = Path(src_name).suffix == ".c"
    compiler = (cli._find_tool(None, "AGENT_CC", cli._CC_CANDIDATES, "clang") if is_c
                else cli._find_tool(None, "AGENT_CXX", cli._CXX_CANDIDATES, "clang++"))
    vsize, _ = cli._verify_size("per_kernel", bench)
    proj = cli._project_of(bench_dir)
    rec: Dict[str, Any] = {"verify_size": vsize, "threads": threads, "limit_s": limit, "runs": []}
    with tempfile.TemporaryDirectory(prefix="e7_tsan_") as tmp:
        work = Path(tmp)
        if proj is None:
            shutil.copy2(prog_file, work / src_name)
            inputs, tail = [str(work / src_name)], []
        else:
            cli._copy_tree(bench_dir, work / "p")
            shutil.copy2(prog_file, work / "p" / src_name)
            inputs = ([str(work / "p" / u) for u in proj["units"]]
                      + [f"-I{work / 'p' / d}" for d in proj.get("include_dirs") or []] + list(proj.get("cflags") or []))
            tail = list(proj.get("ldflags") or [])
        cmd = [compiler, "-O2", f"-D{vsize}_DATASET", "-fsanitize=thread", "-g", *inputs, "-o", str(work / "tsan_par"),
               *tail, *cli._toolchain_flags(True, is_c)]
        b = subprocess.run(cmd, capture_output=True, text=True, cwd=work, timeout=900)
        if b.returncode != 0:
            rec.update(verdict="build-failed", build_error=b.stderr[-600:])
            return rec
        env = _tsan_env()
        env["OMP_NUM_THREADS"] = str(threads)
        for _ in range(runs):
            t0 = time.time()
            try:
                r = subprocess.run([str(work / "tsan_par")], capture_output=True, text=True, cwd=work, env=env, timeout=limit)
                err, rc, timed_out = r.stderr, r.returncode, False
            except subprocess.TimeoutExpired:
                err, rc, timed_out = "", -9, True
            race = "WARNING: ThreadSanitizer" in err or "DATA RACE" in err
            i = err.find("WARNING: ThreadSanitizer")
            rec["runs"].append({"rc": rc, "seconds": round(time.time() - t0, 1), "race": race, "timed_out": timed_out,
                                "report": err[i:i + 1500] if i >= 0 else (err[-300:] if rc != 0 else "")})
    rr = rec["runs"]
    rec["verdict"] = ("race" if any(x["race"] for x in rr) else "timed-out" if any(x["timed_out"] for x in rr)
                      else "failed" if any(x["rc"] != 0 for x in rr) else "clean")
    return rec


def cmd_judge(a: argparse.Namespace) -> int:
    c = _load(a.corpus)
    progs = c["programs"]
    draw = _draw(c, a)
    wanted = _slice(sorted({str(x["program"]) for x in (draw if draw is not None else c["candidates"])}), a.part)
    wanted = [h for h in wanted if not progs[h]["original"]]     # the original is right by definition
    run_dir = EVAL / "agent" / "runs" / a.run_id
    side = run_dir / "gate_study"
    side.mkdir(parents=True, exist_ok=True)
    _manifest(side, {"step": "judge", "corpus": c["name"], "corpus_commit": c["commit"], "part": a.part,
                     "sample": a.sample, "seed": a.seed, "per_benchmark": a.per_benchmark, "programs": len(wanted),
                     "threads": a.threads,
                     "repeats": a.repeats, "tsan_runs": a.tsan_runs, "tsan_threads": a.tsan_threads,
                     "tsan_limit": a.tsan_limit})
    j2_path = side / "j2.jsonl"
    j2_done = _done(j2_path, "program")
    print(f"{len(wanted)} program(s) of corpus {c['name']} → run {a.run_id}", flush=True)
    for i, h in enumerate(wanted, 1):
        pr = progs[h]
        bench, idx = str(pr["benchmark"]), int(pr["index"])
        prog_file = a.corpus / str(pr["path"])
        trial = run_dir / "benchmarks" / bench / "e7" / "none" / f"rep{idx}" / "trial.json"
        t0 = time.time()
        if not trial.is_file():
            proj = _meta(bench).get("project")
            src = prog_file.parent if proj else prog_file
            r = subprocess.run([sys.executable, str(EVAL / "agent" / "benchmark"), "verify-source", bench, "--label", "e7",
                                "--repeat", str(idx), "--source", str(src), "--threads", a.threads,
                                "--repeats", str(a.repeats), "--check-seed", SEED, "--run-id", a.run_id],
                               capture_output=True, text=True, cwd=EVAL)
            if r.returncode != 0 or not trial.is_file():
                _append(side / "j1_errors.jsonl", {"program": h, "benchmark": bench, "index": idx, "rc": r.returncode,
                                                   "stderr": r.stderr[-800:], "stdout": r.stdout[-400:]})
        outcome = json.loads(trial.read_text()).get("outcome") if trial.is_file() else "NOT-JUDGED"
        j1_s = round(time.time() - t0, 1)
        j2 = "-"
        if pr["directive"] and not a.skip_j2:
            if h not in j2_done:
                t1 = time.time()
                try:
                    rec = _tsan_at_size(bench, prog_file, a.tsan_runs, a.tsan_threads, a.tsan_limit)
                except Exception as e:      # one program must not end a lane: no race verdict, listed by the read-out
                    rec = {"verdict": "error", "error": f"{type(e).__name__}: {e}"[:600], "runs": []}
                rec.update(program=h, benchmark=bench, index=idx, seconds=round(time.time() - t1, 1))
                _append(j2_path, rec)
                j2 = str(rec["verdict"])
            else:
                j2 = "done"
        _append(side / "times.jsonl", {"program": h, "benchmark": bench, "index": idx, "j1_s": j1_s,
                                        "total_s": round(time.time() - t0, 1), "outcome": outcome, "j2": j2})
        print(f"[{i}/{len(wanted)}] {bench} #{idx}: {outcome}; races: {j2}; {round(time.time() - t0, 1)} s", flush=True)
    m = json.loads((side / "manifest.json").read_text())
    m["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (side / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return 0


# ------------------------------------------------------------------------------------------------ checks


def _unified_diff(original: Path, final: Path) -> str:
    # `diff -u`, as race_check.py: it writes the "\ No newline at end of file" markers that `patch` needs
    return subprocess.run(["diff", "-u", str(original), str(final)], capture_output=True, text=True).stdout


def cmd_checks(a: argparse.Namespace) -> int:
    """The gate on each distinct (base, program) pair at the gate's own size, with the reference outputs and the
    numerical noise floor taken on the ORIGINAL as the agent takes them at the start of a run.

    G   the whole safety gate, as the final pass calls it (`validate(mode="safety")`): the fidelity against the
        recorded verdict
    T   the ThreadSanitizer stage alone (no schedule matrix, no output check)           — directives, 3 times
    S   the schedule matrix alone, the sanitizer not run; its verdict kept (hard / soft) — directives, 3 times
    O1  the output check on the shipped input alone                                      — once (3 times with a directive)
    O2  the output check on the perturbed input alone                                    — once (3 times with a directive)
    """
    import harness_include
    harness_include.install()   # every build finds prepared/_harness (D39)
    import importlib

    from discopop_agent import project as project_mod
    from discopop_agent.gate.equivalence import numerical_noise_floor
    from discopop_agent.gate.timing import capture_reference
    from discopop_agent.gate.validate import validate

    # the module, not the function of the same name that the package exports
    gv: Any = importlib.import_module("discopop_agent.gate.validate")
    seen: List[Any] = []
    real_stress = gv.stress_schedules

    def spy(*args: Any, **kw: Any) -> Any:      # the matrix's own verdict (hard or soft), which validate() folds away
        r = real_stress(*args, **kw)
        seen.append(r)
        return r

    gv.stress_schedules = spy

    c = _load(a.corpus)
    progs = c["programs"]
    draw = _draw(c, a)
    todo = [tuple(x.split(" ")) for x in _slice([f"{b} {p}" for b, p in _pairs(draw if draw is not None else c["candidates"])],
                                                a.part)]
    a.out.mkdir(parents=True, exist_ok=True)
    _manifest(a.out, {"step": "checks", "corpus": c["name"], "corpus_commit": c["commit"], "part": a.part,
                      "sample": a.sample, "seed": a.seed, "per_benchmark": a.per_benchmark, "pairs": len(todo),
                      "check_inputs": [[SEED]],
                      "gate": "validate(): G whole safety gate; T tsan alone; S matrix alone; O1/O2 one input alone"})
    res_path = a.out / "checks.jsonl"
    done = _done(res_path, "pair")
    refs: Dict[str, Any] = {}
    print(f"{len(todo)} (base, program) pair(s) of corpus {c['name']} → {a.out}", flush=True)
    for i, (hb, hp) in enumerate(todo, 1):
        key = f"{hb} {hp}"
        if key in done:
            continue
        pb, pp = progs[hb], progs[hp]
        bench = str(pp["benchmark"])
        meta = _meta(bench)
        proj = meta.get("project")
        fname = str(meta["file"])
        t0 = time.time()
        rec: Dict[str, Any] = {"pair": key, "base": hb, "program": hp, "benchmark": bench}
        try:                                   # one pair must not end a lane: the record keeps the error
            with tempfile.TemporaryDirectory(prefix="e7_checks_") as tmp:
                project_mod.activate(None)
                if proj:
                    root = Path(tmp) / "program"
                    shutil.copytree(PREPARED / bench, root)
                    src = root / fname
                    project_mod.activate(project_mod.Project.discover(
                        root, units=list(proj["units"]), include_dirs=list(proj.get("include_dirs") or ["."]),
                        editable=list(proj.get("editable") or [fname]), cflags=list(proj.get("cflags") or []),
                        ldflags=list(proj.get("ldflags") or [])))
                    project_mod.set_focus(str(src))
                else:
                    src = Path(tmp) / fname
                    shutil.copy2(PREPARED / bench / fname, src)
                if bench not in refs:                     # on the ORIGINAL, once per benchmark
                    ref_out, _t, ref_pairs = capture_reference(str(src), None, extra_inputs=[[SEED]])
                    refs[bench] = (ref_out, ref_pairs, numerical_noise_floor(str(src), None, extra_inputs=[[SEED]]).value)
                ref_out, ref_pairs, floor = refs[bench]
                rec["noise_floor"], rec["reference_inputs"] = floor, len(ref_pairs or [])
                src.write_text((a.corpus / str(pb["path"])).read_text())            # the base the gate judged on
                diff = _unified_diff(src, a.corpus / str(pp["path"]))
                has_pragma = "pragma omp" in diff
                rec["has_pragma"] = has_pragma

                def one(**kw: Any) -> Dict[str, Any]:
                    seen.clear()
                    r = validate(diff, str(src), mode="safety", noise_floor=floor, **kw)
                    d: Dict[str, Any] = {"passed": r.passed, "stage": r.stage, "diagnostic": r.diagnostic[:400],
                                         "evidence": {k: v for k, v in r.evidence.items() if k != "schedules"}}
                    if seen:
                        d["matrix"] = {"ok": seen[-1].ok, "verdict": seen[-1].verdict, "hard": seen[-1].hard,
                                       "max_deviation": seen[-1].max_deviation}
                    return d

                if not diff:
                    rec["note"] = "the program equals its base"
                elif ref_out is None or not ref_pairs or len(ref_pairs) < 2:
                    rec["note"] = "no reference output on both inputs for the original"
                else:
                    reps = 3 if has_pragma else 1
                    rec["G"] = one(reference_output=ref_out, reference_outputs=ref_pairs, stress=True)
                    if has_pragma:
                        rec["T"] = [one(reference_output=None, stress=False) for _ in range(reps)]
                        rec["S"] = [one(reference_output=None, stress=True, skip_race_check=True) for _ in range(reps)]
                    rec["O1"] = [one(reference_output=ref_out, reference_outputs=[ref_pairs[0]], stress=False,
                                     skip_race_check=True) for _ in range(reps)]
                    rec["O2"] = [one(reference_output=ref_out, reference_outputs=[ref_pairs[1]], stress=False,
                                     skip_race_check=True) for _ in range(reps)]
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"[:600]
        project_mod.activate(None)
        rec["seconds"] = round(time.time() - t0, 1)
        _append(res_path, rec)
        g = rec.get("G") or {}
        print(f"[{i}/{len(todo)}] {bench} {hp[:10]}: gate {'accepted' if g.get('passed') else g.get('stage', rec.get('note'))}"
              f"  {rec['seconds']} s", flush=True)
    m = json.loads((a.out / "manifest.json").read_text())
    m["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return 0


# ------------------------------------------------------------------------------------------------ Part B: DataRaceBench


DRB = EVAL / "benchmarks" / "LLNL_DataRaceBench" / "micro-benchmarks"
OMP_DIRECTIVE = re.compile(r"\s*#\s*pragma\s+omp\b")
THREADS = re.compile(r"\b(parallel|task|taskloop|sections|teams|target)\b")

def _strip_omp(text: str) -> str:
    """The file with every OpenMP directive line removed (a directive continued with a backslash goes whole)."""
    out: List[str] = []
    skipping = False
    for ln in text.splitlines(keepends=True):
        if skipping or OMP_DIRECTIVE.match(ln):
            skipping = ln.rstrip().endswith("\\")
            continue
        out.append(ln)
    return "".join(out)


def _drb_class(text: str) -> str:
    """What kind of construct the kernel's directives are: only a kernel that starts threads on the host is the
    gate's case; offloading and SIMD-only kernels get rows of their own."""
    lines = [ln for ln in text.splitlines() if OMP_DIRECTIVE.match(ln)]
    if any(re.search(r"\btarget\b", ln) for ln in lines):
        return "offloading"
    if not any(THREADS.search(ln) for ln in lines):
        return "simd-only" if lines else "no-directive"
    return "threads"


def cmd_drb(a: argparse.Namespace) -> int:
    """Each kernel as one candidate: the reference is the file without its directive lines, the candidate the file
    as shipped, judged by the gate's safety validation as `race_check.py` calls it; `--runs` times per kernel."""
    import importlib

    from discopop_agent import project as project_mod
    from discopop_agent.gate.equivalence import numerical_noise_floor
    from discopop_agent.gate.timing import capture_reference
    from discopop_agent.gate.validate import validate

    gv: Any = importlib.import_module("discopop_agent.gate.validate")
    seen: List[Any] = []
    real_stress = gv.stress_schedules

    def spy(*args: Any, **kw: Any) -> Any:
        r = real_stress(*args, **kw)
        seen.append(r)
        return r

    gv.stress_schedules = spy
    kernels = _slice(sorted(p.name for p in DRB.iterdir() if p.suffix in (".c", ".cpp")), a.part)
    if a.only:
        kernels = [k for k in kernels if any(k.startswith(o) for o in a.only.split(","))]
    a.out.mkdir(parents=True, exist_ok=True)
    _manifest(a.out, {"step": "drb", "part": a.part, "kernels": len(kernels), "runs": a.runs,
                      "source": (DRB.parent / "PROVENANCE.txt").read_text()[:400]})
    res_path = a.out / "drb.jsonl"
    done = _done(res_path, "kernel")
    print(f"{len(kernels)} kernel(s) → {a.out}", flush=True)
    for i, name in enumerate(kernels, 1):
        if name in done:
            continue
        shipped = (DRB / name).read_text(errors="replace")
        label = "yes" if "-yes." in name else "no" if "-no." in name else "?"
        rec: Dict[str, Any] = {"kernel": name, "label": label, "class": _drb_class(shipped), "runs": []}
        t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="e7_drb_") as tmp:
            root = Path(tmp) / "k"
            root.mkdir()
            src = root / name
            src.write_text(_strip_omp(shipped))
            (root / "shipped").mkdir()
            (root / "shipped" / name).write_text(shipped)
            project_mod.activate(None)
            diff = _unified_diff(src, root / "shipped" / name)
            poly = "polybench/" in shipped
            ref_out, _t, ref_pairs = (None, None, None) if poly else capture_reference(str(src), None)
            if poly:
                # six kernels: DataRaceBench builds them from two files (its utilities/polybench.c) with a timer that
                # prints the run time, another number in every run — no single program text with a comparable output
                rec["note"] = "a PolyBench kernel of DataRaceBench: two source files and a printed run time"
            elif ref_out is None:
                rec["note"] = "the file without its directives does not build or run here"
            elif not diff:
                rec["note"] = "the file holds no directive line"
            else:
                floor = numerical_noise_floor(str(src), None).value
                rec["noise_floor"] = floor
                for _ in range(a.runs):
                    seen.clear()
                    r = validate(diff, str(src), reference_output=ref_out, reference_outputs=ref_pairs, mode="safety",
                                 noise_floor=floor, stress=True)
                    d: Dict[str, Any] = {"passed": r.passed, "stage": r.stage, "diagnostic": r.diagnostic[:300]}
                    if seen:
                        d["matrix"] = {"verdict": seen[-1].verdict, "hard": seen[-1].hard}
                    rec["runs"].append(d)
        project_mod.activate(None)
        rec["seconds"] = round(time.time() - t0, 1)
        _append(res_path, rec)
        shown = [("accepted" if x["passed"] else x["stage"]) for x in rec["runs"]] or rec.get("note")
        print(f"[{i}/{len(kernels)}] {name} ({label}, {rec['class']}): {shown}  {rec['seconds']} s", flush=True)
    m = json.loads((a.out / "manifest.json").read_text())
    m["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (a.out / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return 0


def cmd_readout_drb(a: argparse.Namespace) -> int:
    d = _run_dir(a.run)
    if d is None:
        sys.exit(f"run {a.run}: neither archived nor fetched")
    recs: Dict[str, Dict[str, Any]] = {}
    for f in sorted(d.rglob("drb.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                r = json.loads(ln)
                recs[str(r["kernel"])] = r
    out: List[str] = [f"# E7, Part B — the gate on DataRaceBench 1.4.1 ({len(recs)} kernels)\n",
                      f"*Generated by `tools/gate_study.py readout-drb` from run `{a.run}`. Each kernel is one candidate: the file "
                      "without its OpenMP directive lines is the reference, the file as shipped the candidate, judged by the "
                      "gate's safety validation several times. A kernel named `-yes` holds a documented data race, one named "
                      "`-no` none.*\n"]
    data: Dict[str, Any] = {"run": a.run, "kernels": len(recs)}

    def why_not(r: Dict[str, Any]) -> str:
        """Why a kernel has no verdict, in the read-out's words."""
        note = str(r.get("note") or "")
        if note.startswith("a PolyBench kernel"):
            return "one of DataRaceBench's PolyBench kernels: two source files and a printed run time"
        if note.startswith("the file without its directives"):
            text = (DRB / str(r["kernel"])).read_text(errors="replace") if (DRB / str(r["kernel"])).is_file() else ""
            if re.search(r"#\s*error\b", text):
                return ("its own `#error` demands an OpenMP 4.5 compiler, and the reference is built without OpenMP")
            return ("without its directives it is no sequential program: it does not end, crashes, fails its own assertion "
                    "or exits with an error code")
        if note:
            return note
        if any("timed out" in str(x.get("diagnostic")) for x in r["runs"]):
            return "a run exceeds the gate's time limit (120 s plain, 300 s under the sanitizer)"
        return ""

    for r in recs.values():
        r["why_not"] = why_not(r)
        r["judged"] = bool(r["runs"]) and not r["why_not"]
    out.append("| class | label | kernels | judged | refused in the first run | refused in at least one run | refused in every run |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    table: Dict[str, Any] = {}
    for cls in ("threads", "simd-only", "offloading", "no-directive"):
        for label in ("yes", "no"):
            sel = [r for r in recs.values() if r["class"] == cls and r["label"] == label]
            if not sel:
                continue
            judged = [r for r in sel if r["judged"]]
            first = [r for r in judged if not r["runs"][0]["passed"]]
            some = [r for r in judged if any(not x["passed"] for x in r["runs"])]
            every = [r for r in judged if all(not x["passed"] for x in r["runs"])]
            out.append(f"| {cls} | {label} | {len(sel)} | {len(judged)} | {len(first)} | {len(some)} | {len(every)} |")
            table[f"{cls} {label}"] = {"kernels": len(sel), "judged": len(judged), "first": len(first), "any": len(some),
                                       "every": len(every),
                                       "never_refused": sorted(str(r["kernel"]) for r in judged if r not in some),
                                       "refused": sorted(str(r["kernel"]) for r in some),
                                       "not_judged": sorted(f"{r['kernel']}: {r['why_not']}" for r in sel if not r["judged"])}
    data["table"] = table
    out.append("")
    th_yes, th_no = table.get("threads yes") or {}, table.get("threads no") or {}
    if th_yes:
        out.append(f"**Kernels that start threads on the host, with a documented race:** refused by one call of the gate "
                   f"{_wilson(th_yes['first'], th_yes['judged'])}; in at least one of the runs {_wilson(th_yes['any'], th_yes['judged'])}.")
    if th_no:
        out.append(f"**Without a race:** refused by one call of the gate {_wilson(th_no['first'], th_no['judged'])}; "
                   f"in at least one of the runs {_wilson(th_no['any'], th_no['judged'])}.\n")
    stages: collections.Counter[str] = collections.Counter()
    for r in recs.values():
        if r["class"] == "threads" and r["judged"] and not r["runs"][0]["passed"]:
            stages[f"{r['label']}: {r['runs'][0]['stage']}"] += 1
    out.append("First run's refusals by check (kernels that start threads): "
               + (", ".join(f"{k} {v}" for k, v in sorted(stages.items())) or "none") + ".\n")
    data["first_run_stage"] = dict(stages)
    def pattern(r: Dict[str, Any]) -> str:
        return " ".join("accepted" if x["passed"] else str(x["stage"]) for x in r["runs"])

    th = [r for r in recs.values() if r["class"] == "threads" and r["judged"]]
    some_not_all = [r for r in th if r["label"] == "yes" and any(not x["passed"] for x in r["runs"])
                    and any(x["passed"] for x in r["runs"])]
    out.append(f"### Racy kernels the gate refused in some runs and accepted in others: {len(some_not_all)}\n")
    out += [f"- `{r['kernel']}` — {pattern(r)}" for r in sorted(some_not_all, key=lambda r: str(r["kernel"]))] + [""]
    never = [r for r in th if r["label"] == "yes" and all(x["passed"] for x in r["runs"])]
    out.append(f"### Racy kernels the gate never refused: {len(never)}\n")
    out += [f"- `{r['kernel']}`" for r in sorted(never, key=lambda r: str(r["kernel"]))] + [""]
    wrongly = [r for r in th if r["label"] == "no" and any(not x["passed"] for x in r["runs"])]
    out.append(f"### Race-free kernels the gate refused at least once: {len(wrongly)}\n")
    by_check: collections.Counter[str] = collections.Counter()
    for r in sorted(wrongly, key=lambda r: str(r["kernel"])):
        stages_r = sorted({str(x["stage"]) for x in r["runs"] if not x["passed"]})
        by_check[" + ".join(stages_r)] += 1
        out.append(f"- `{r['kernel']}` — {pattern(r)}")
    out.append("")
    out.append("By check: " + (", ".join(f"{k} {v}" for k, v in sorted(by_check.items())) or "none") + ".\n")
    data["no_refused_by_check"] = dict(by_check)
    data["yes_some_runs"] = {str(r["kernel"]): pattern(r) for r in some_not_all}
    not_j = [r for r in recs.values() if not r["judged"]]
    reasons: Dict[str, List[str]] = collections.defaultdict(list)
    for r in not_j:
        reasons[str(r["why_not"]) or "no run recorded"].append(f"{r['kernel']} ({r['label']}, {r['class']})")
    out.append(f"### Kernels not judged: {len(not_j)}\n")
    for why, names in sorted(reasons.items(), key=lambda kv: -len(kv[1])):
        out.append(f"- **{len(names)}** — {why}: " + ", ".join(f"`{n}`" for n in sorted(names)))
    out.append("")
    data["not_judged"] = {k: sorted(v) for k, v in reasons.items()}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "readout_drb.md").write_text("\n".join(out) + "\n")
    (a.out / "readout_drb.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print("\n".join(out[:40]))
    return 0


# ------------------------------------------------------------------------------------------------ readout


def _wilson(k: int, n: int) -> str:
    """95 % Wilson interval of k/n; with no event (or only events) the one-sided 95 % bound."""
    if n == 0:
        return "—"
    if k == 0:
        return f"0 of {n} (one-sided 95 % bound: at most {100 * (1 - 0.05 ** (1 / n)):.1f} %)"
    if k == n:
        return f"{n} of {n} (one-sided 95 % bound: at least {100 * 0.05 ** (1 / n):.1f} %)"
    z, ph = 1.959964, k / n
    den = 1 + z * z / n
    mid = (ph + z * z / (2 * n)) / den
    half = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / den
    return f"{k} of {n} ({100 * ph:.1f} %, 95 % interval {100 * (mid - half):.1f}–{100 * (mid + half):.1f} %)"


def _run_dir(run_id: str) -> Optional[Path]:
    d = campaign.find_run(run_id)
    if d is not None:
        return d
    local = EVAL / "agent" / "runs" / run_id
    return local if local.is_dir() else None


def _j1_class(rec: Dict[str, Any]) -> Tuple[str, str]:
    """The harness's verdict on a program, from its verification record. `verify-source` files a program that
    crashes or does not finish under VERIFY_FAILED with a build that fails (its records are baselines); here the
    two are kept apart: a program that does not run where the original runs is wrong."""
    if (rec.get("scaffold") or {}).get("ok") is False:
        return "not-judgeable", "the candidate changed the measuring code"
    v = rec.get("verify") or {}
    st = str(v.get("status"))
    if st == "verify_build_failed":
        return "no-build", st
    if st.startswith("final_run_failed"):
        f = v.get("final_run_failure") or {}
        return "wrong", st + (" (timed out)" if f.get("timed_out") else f" (rc {f.get('rc')})")
    if st != "ok":
        return "not-judged", st
    if rec.get("outcome") == "BROKEN":
        why = []
        if (v.get("dump_max_rel_err") or 0) > 1e-9:
            why.append(f"values differ on the shipped input (max rel. {v.get('dump_max_rel_err'):.2e})")
        if (v.get("dump_seeded_max_rel_err") or 0) > 1e-9:
            why.append(f"values differ on the perturbed input (max rel. {v.get('dump_seeded_max_rel_err'):.2e})")
        if (v.get("digest_max_rel_err") or 0) > 1e-9:
            why.append(f"digest differs at the verification size (max rel. {v.get('digest_max_rel_err'):.2e})")
        if (v.get("digest_seeded_rel_err") or 0) > 1e-9:
            why.append("digest differs on the perturbed input at the verification size")
        if v.get("stable_at_fixed_threads") is False:
            why.append("result changes from run to run at a fixed thread count")
        return "wrong", "; ".join(why) or "BROKEN"
    return "right", ("the verification passes; " + (str(rec.get("outcome")) if rec.get("pragmas_in_final") else "no directive"))


def cmd_readout(a: argparse.Namespace) -> int:
    import cli

    c = _load(a.corpus)
    progs, cands = c["programs"], c["candidates"]
    wanted = sorted(h for h in {str(x["program"]) for x in cands} if not progs[h]["original"])

    def name(h: str) -> str:
        return f"{progs[h]['benchmark']} #{progs[h]['index']}"       # the suite stays: s331 is in tsvc_c2 and tsvc_c3

    # ---- the judge, per distinct program; a record counts only when it judged this corpus's file
    j1: Dict[str, Tuple[str, str]] = {}
    j2: Dict[str, Dict[str, Any]] = {}
    foreign: List[str] = []
    by_key = {(str(v["benchmark"]), int(v["index"])): h for h, v in progs.items()}
    digest: Dict[str, str] = {}
    for run_id in [r for r in a.judge.split(",") if r]:
        d = _run_dir(run_id)
        if d is None:
            sys.exit(f"judge run {run_id}: neither archived nor fetched")
        for tj in sorted(d.glob("benchmarks/*/*/e7/none/rep*/trial.json")):
            rec = json.loads(tj.read_text())
            h = by_key.get((str(rec["benchmark"]), int(rec["repeat"])))
            if h is None:
                continue
            if h not in digest:
                f = a.corpus / str(progs[h]["path"])
                digest[h] = (cli._tree_digest(f.parent) if _meta(str(progs[h]["benchmark"])).get("project")
                             else hashlib.sha256(f.read_bytes()).hexdigest())
            if rec.get("candidate_sha256") != digest[h]:
                foreign.append(f"{run_id}: {rec['benchmark']} rep{rec['repeat']}")
                continue
            j1[h] = _j1_class(rec)
        f2 = d / "gate_study" / "j2.jsonl"
        for ln in (f2.read_text().splitlines() if f2.is_file() else []):
            if ln.strip():
                r = json.loads(ln)
                if str(r["program"]) in progs:
                    j2[str(r["program"])] = r

    def race(h: str) -> str:
        """`clean`, `race`, or the reason there is no verdict; `n/a` without a directive."""
        if not progs[h]["directive"]:
            return "n/a"
        return str(j2[h]["verdict"]) if h in j2 else "not run"

    def judge(h: str) -> Tuple[str, str]:
        if progs[h]["original"]:
            return "right", "the original"
        if h not in j1:
            return "not-judged", "no record of the harness"
        cls, why = j1[h]
        rv = race(h)
        if cls == "wrong" and rv == "race":
            return cls, why + "; a data race reported at the verification size"
        if cls == "right" and rv == "race":
            return "wrong", "the harness finds the output right; a data race reported at the verification size"
        if cls == "right" and rv not in ("clean", "n/a"):
            return "no-race-verdict", f"the harness finds the output right; the race check at the verification size: {rv}"
        return cls, why

    # ---- the checks, per (base, program) pair
    checks: Dict[str, Dict[str, Any]] = {}
    for run_id in [r for r in a.checks.split(",") if r]:
        d = _run_dir(run_id)
        if d is None:
            sys.exit(f"checks run {run_id}: neither archived nor fetched")
        for fc in sorted(d.rglob("checks.jsonl")):
            for ln in fc.read_text().splitlines():
                if ln.strip():
                    r = json.loads(ln)
                    checks[str(r["pair"])] = r

    verdict = {h: judge(h) for h in set(wanted) | {str(x["base"]) for x in cands}}
    rows: List[Dict[str, Any]] = []
    for x in cands:
        cls, why = verdict[str(x["program"])]
        bcls = verdict[str(x["base"])][0]
        rows.append({**x, "judge": cls, "why": why, "pair": f"{x['base']} {x['program']}",
                     "base_state": "passes" if bcls == "right" else "fails" if bcls in ("wrong", "no-build") else "no verdict",
                     "accepted": x["gate"] == "accepted", "pre_program": x["gate"] in ("compile", "openmp_compile", "apply"),
                     "checks": checks.get(f"{x['base']} {x['program']}")})

    out: List[str] = []
    data: Dict[str, Any] = {"corpus": c["name"], "judge_runs": a.judge, "checks_runs": a.checks}
    out.append(f"# E7 — the gate against the harness, corpus {c['name'].upper()}\n")
    out.append(f"*Generated by `tools/gate_study.py readout` from the corpus (`corpus/{c['name']}/corpus.json`), the judge's runs "
               f"({a.judge}) and the replayed checks ({a.checks or 'none'}). Definitions: the record's row of 11 Nov 2026 "
               "(\"E7 reopened and registered as it will run\").*\n")

    # ---- coverage: what is counted below, and what is missing by name
    no_j1 = [h for h in wanted if h not in j1]
    with_dir = [h for h in wanted if progs[h]["directive"]]
    no_j2 = [h for h in with_dir if h in j1 and j1[h][0] == "right" and race(h) not in ("clean", "race")]
    pairs_all = sorted({r["pair"] for r in rows})
    no_replay = [p for p in pairs_all if "G" not in (checks.get(p) or {})]
    out.append("## What is counted\n")
    out.append(f"- {len(cands)} candidates on {len(wanted)} distinct programs in {len({str(x['benchmark']) for x in cands})} "
               f"benchmarks; {len(c['not_rebuilt'])} candidate(s) could not be rebuilt and are left out by name (`corpus.json`).")
    out.append(f"- The harness judged {len(wanted) - len(no_j1)} of the {len(wanted)} programs"
               + ("." if not no_j1 else f"; **without a record: {len(no_j1)}** — " + ", ".join(name(h) for h in no_j1[:15])
                  + (" …" if len(no_j1) > 15 else "") + "."))
    out.append(f"- {len(with_dir)} programs hold a directive; of those the harness finds right, the race check at the verification "
               f"size gave a verdict for all but {len(no_j2)}"
               + ("." if not no_j2 else " — " + ", ".join(f"{name(h)} ({race(h)})" for h in no_j2[:15])
                  + (" …" if len(no_j2) > 15 else "") + ". They enter no rate."))
    if a.checks:
        why_none = collections.Counter(
            ("error: " + str((checks.get(p) or {}).get("error"))[:60]) if (checks.get(p) or {}).get("error")
            else str((checks.get(p) or {}).get("note") or "not replayed") for p in no_replay)
        out.append(f"- The gate was replayed on {len(pairs_all) - len(no_replay)} of the {len(pairs_all)} (base, program) pairs"
                   + ("." if not no_replay else "; **without a replay: " + "; ".join(f"{v} × {k}" for k, v in why_none.most_common()) + "**."))
    if foreign:
        out.append(f"- {len(foreign)} record(s) of the given runs judged another file than this corpus's and are ignored: "
                   + ", ".join(foreign[:8]) + (" …" if len(foreign) > 8 else "") + ".")
    complete = not no_j1 and not (a.checks and no_replay)
    if not complete:
        out.append("\n**This read-out is PARTIAL: the tables below hold only what has a verdict.**")
    out.append("")
    data["coverage"] = {"candidates": len(cands), "programs": len(wanted), "programs_judged": len(wanted) - len(no_j1),
                        "programs_without_record": [name(h) for h in no_j1], "programs_with_directive": len(with_dir),
                        "right_without_race_verdict": {name(h): race(h) for h in no_j2},
                        "pairs": len(pairs_all), "pairs_replayed": len(pairs_all) - len(no_replay),
                        "foreign_records": foreign, "complete": complete}

    def by_program(sel: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """One row per distinct program. A program's verdicts are its own; its base passes when it does in one candidate."""
        grp: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        for r in sel:
            grp[str(r["program"])].append(r)
        res = []
        for rs in grp.values():
            states = {r["base_state"] for r in rs}
            res.append({**rs[0], "n_candidates": len(rs),
                        "base_state": "passes" if "passes" in states else "fails" if "fails" in states else "no verdict"})
        return res

    def cell(r: Dict[str, Any]) -> str:
        if r["judge"] in ("right", "wrong"):
            return r["judge"] if r["base_state"] == "passes" else "base fails" if r["base_state"] == "fails" else "no verdict"
        return "no build" if r["judge"] == "no-build" else "no verdict"

    # ---- R1: gate x judge
    out.append("## R1 — what the gate decided against what the judge found\n")
    out.append("*Right:* the harness's verification passes (values on both inputs, the digest at the verification size, the same "
               "result in repeated runs at a fixed thread count) and, with a directive, ThreadSanitizer reports no race at that "
               "size. *Wrong:* one of them fails. *Base fails:* the program the candidate was applied to is itself wrong, so the "
               "candidate is counted apart. *No verdict:* not judged, not judgeable, or right without a race verdict.\n")
    r1: Dict[str, Any] = {}
    for unit in ("distinct program", "candidate"):
        out.append(f"### per {unit}\n")
        out.append("| | judge: right | judge: wrong | does not build | base fails | no verdict |")
        out.append("|---|---:|---:|---:|---:|---:|")
        for kind in ("rewrite", "directive"):
            for acc in (True, False):
                sel = [r for r in rows if r["kind"] == kind and r["accepted"] == acc]
                if unit != "candidate":
                    sel = by_program(sel)
                cnt = collections.Counter(cell(r) for r in sel)
                label = f"{kind}, gate {'accepted' if acc else 'refused'}"
                out.append(f"| {label} | {cnt['right']} | {cnt['wrong']} | {cnt['no build']} | {cnt['base fails']} | {cnt['no verdict']} |")
                r1[f"{unit} | {label}"] = dict(cnt)
        out.append("")
    data["R1"] = r1

    def clean(kind: str) -> List[Dict[str, Any]]:      # the candidates that enter a rate
        return [r for r in rows if r["kind"] == kind and r["base_state"] == "passes" and r["judge"] in ("right", "wrong")
                and not r["pre_program"]]

    out.append("### the two error rates\n")
    out.append("Entered: candidates with a program (not refused at `compile`, `openmp_compile` or `apply`), on a base that "
               "passes, with a verdict of the judge. The distinct program is the unit to read first: the model writes the same "
               "wrong rewrite many times, and each time is a candidate.\n")
    rates: Dict[str, Any] = {}
    for kind in ("rewrite", "directive"):
        sel = clean(kind)
        per: Dict[str, Tuple[int, int, int, int]] = {}
        for unit, key in (("distinct program", "program"), ("candidate", "id"), ("loop", "benchmark")):
            u_right = {str(r[key]) for r in sel if r["judge"] == "right"}
            u_wrong = {str(r[key]) for r in sel if r["judge"] == "wrong"}
            u_fr = {str(r[key]) for r in sel if r["judge"] == "right" and not r["accepted"]}
            u_fa = {str(r[key]) for r in sel if r["judge"] == "wrong" and r["accepted"]}
            per[unit] = (len(u_fr), len(u_right), len(u_fa), len(u_wrong))
        out.append(f"**{kind}s**\n")
        out.append("| unit | right, but the gate refused (false refusals) | wrong, but the gate accepted (false accepts) |")
        out.append("|---|---|---|")
        for unit, (kfr, nr, kfa, nw) in per.items():
            out.append(f"| per {unit} | {_wilson(kfr, nr)} | {_wilson(kfa, nw)} |")
        loops_fr = sorted({str(r["benchmark"]).split("/")[-1] for r in sel if r["judge"] == "right" and not r["accepted"]})
        loops_fa = sorted({str(r["benchmark"]).split("/")[-1] for r in sel if r["judge"] == "wrong" and r["accepted"]})
        if loops_fr or loops_fa:
            out.append("")
            out.append((f"Loops with a false refusal: {', '.join(loops_fr)}. " if loops_fr else "")
                       + (f"Loops with a false accept: {', '.join(loops_fa)}." if loops_fa else ""))
        out.append("")
        rates[kind] = {u: {"false_refusals": v[0], "right": v[1], "false_accepts": v[2], "wrong": v[3]} for u, v in per.items()}
        rates[kind]["loops_false_refusal"], rates[kind]["loops_false_accept"] = loops_fr, loops_fa
    data["rates"] = rates

    pre = by_program([r for r in rows if r["pre_program"]])
    agree = sum(1 for r in pre if r["judge"] == "no-build")
    others = collections.Counter(str(r["judge"]) for r in pre if r["judge"] != "no-build")
    out.append(f"**Refused before a program exists** (`compile`, `openmp_compile`): {sum(r['n_candidates'] for r in pre)} candidates "
               f"on {len(pre)} distinct texts; the judge's own build fails for {agree} of them"
               + ("." if agree == len(pre) else "; the others: " + ", ".join(f"{k} {v}" for k, v in sorted(others.items()))
                  + " — " + ", ".join([f"{name(str(r['program']))} ({r['gate']} → {r['judge']})"
                                       for r in sorted(pre, key=lambda r: name(str(r['program']))) if r["judge"] != "no-build"][:12])
                  + (" …" if len(pre) - agree > 12 else "") + ".")
               + "\n")
    data["pre_program"] = {"candidates": sum(r["n_candidates"] for r in pre), "texts": len(pre), "judge_build_fails": agree,
                           "others": {name(str(r["program"])): [r["gate"], r["judge"], r["why"]] for r in pre if r["judge"] != "no-build"}}

    for key, title, pick in (("false_accepts", "False accepts — the gate accepted, the judge finds the program wrong",
                              lambda r: r["accepted"] and r["judge"] == "wrong"),
                             ("false_refusals", "False refusals — the gate refused, the judge finds the program right",
                              lambda r: (not r["accepted"]) and r["judge"] == "right")):
        sel = by_program([r for r in rows if r["base_state"] == "passes" and not r["pre_program"] and pick(r)])
        out.append(f"### {title}: {len(sel)} distinct program(s), {sum(r['n_candidates'] for r in sel)} candidate(s)\n")
        if sel:
            out.append("| program | kind | candidates | the gate | the judge | a trial's final file | file |")
            out.append("|---|---|---:|---|---|---|---|")
            for r in sorted(sel, key=lambda r: (str(r["benchmark"]), int(progs[str(r["program"])]["index"]))):
                h = str(r["program"])
                out.append(f"| {name(h)} | {r['kind']} ({r['phase']}) | {r['n_candidates']} | {r['gate']} | {r['why']} | "
                           f"{'yes' if progs[h]['final_of'] else 'no'} | `{progs[h]['path']}` |")
            out.append("")
        data[key] = [{"program": name(str(r["program"])), "hash": str(r["program"]), "kind": r["kind"], "phase": r["phase"],
                      "candidates": r["n_candidates"], "gate": r["gate"], "judge": r["why"],
                      "final_of": progs[str(r["program"])]["final_of"], "path": progs[str(r["program"])]["path"]} for r in sel]

    # ---- the judge against the trials' own verdicts (its repeatability)
    finals = [h for h, v in progs.items() if v["final_of"] and not v["original"] and h in set(wanted)]
    fin_cnt = collections.Counter(verdict[h][0] for h in finals)
    out.append(f"**The judge beside the trials.** {len(finals)} of the distinct programs are a trial's final file, which the harness "
               f"verified in that trial; judged again here: " + ", ".join(f"{k} {v}" for k, v in sorted(fin_cnt.items())) + ".\n")
    data["finals_rejudged"] = dict(fin_cnt)
    data["finals_not_right"] = {name(h): list(verdict[h]) for h in finals if verdict[h][0] != "right"}

    # ---- fidelity, R2, R3: on the pairs that were replayed
    have = [r for r in rows if r["checks"] is not None and "G" in r["checks"]]
    if have:
        def by_pair(sel: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            grp: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
            for r in sel:
                grp[str(r["pair"])].append(r)
            return [{**rs[0], "n_candidates": len(rs)} for rs in grp.values()]

        out.append("## Fidelity — the whole safety gate replayed against the recorded verdict\n")
        prs = by_pair(have)
        dis: List[Dict[str, Any]] = []
        for r in prs:
            g = r["checks"]["G"]
            replay = "accepted" if g["passed"] else str(g["stage"])
            if replay != r["gate"]:
                kind_of = ("by construction: the replay does not hold this stage" if r["gate"] in ("clause", "dependences")
                           else "run-dependent check (ThreadSanitizer or the schedule matrix)"
                           if {str(r["gate"]), replay} & {"tsan", "schedules"} else "other")
                dis.append({"program": name(str(r["program"])), "recorded": r["gate"], "replayed": replay, "class": kind_of,
                            "judge": r["judge"], "candidates": r["n_candidates"], "diagnostic": str(g.get("diagnostic", ""))[:160]})
        same_c = sum(r["n_candidates"] for r in prs) - sum(x["candidates"] for x in dis)
        out.append(f"{len(prs) - len(dis)} of {len(prs)} (base, program) pairs get the recorded verdict again "
                   f"({same_c} of {sum(r['n_candidates'] for r in prs)} candidates); {len(dis)} differ" + (":" if dis else "."))
        if dis:
            out.append("")
            out.append("| program | candidates | recorded | replayed | the judge | kind of difference |")
            out.append("|---|---:|---|---|---|---|")
            for dd in sorted(dis, key=lambda x: (x["class"], x["program"])):
                out.append(f"| {dd['program']} | {dd['candidates']} | {dd['recorded']} | {dd['replayed']} | {dd['judge']} | {dd['class']} |")
        out.append("")
        data["fidelity"] = {"pairs": len(prs), "pairs_same": len(prs) - len(dis), "candidates": sum(r["n_candidates"] for r in prs),
                            "candidates_same": same_c, "disagreements": dis}

        def refuses(r: Dict[str, Any], nme: str, mode: str = "any") -> Optional[bool]:
            runs = r["checks"].get(nme)
            if nme == "G":
                runs = [runs] if runs else None
            if not runs:
                return None
            bad = [not x["passed"] for x in runs]
            return any(bad) if mode == "any" else all(bad)

        out.append("## R2 — each check on its own\n")
        out.append("A check *refuses* a pair when it fails in at least one of its runs (the run-dependent checks ran three times; in "
                   "brackets: in all of them). G: the whole safety gate as replayed, once; T: ThreadSanitizer alone; S: the "
                   "schedule matrix alone, the sanitizer not run; O1: the output on the shipped input alone; O2: on the perturbed "
                   "input alone. Counted per distinct (base, program) pair, the candidates they stand for in round brackets.\n")
        r2: Dict[str, Any] = {}
        for kind, names in (("directive", ("G", "T", "S", "O1", "O2")), ("rewrite", ("G", "O1", "O2"))):
            sel = by_pair([r for r in have if r["kind"] == kind and r["base_state"] == "passes" and r["judge"] in ("right", "wrong")
                           and not r["pre_program"]])
            wrong, right = [r for r in sel if r["judge"] == "wrong"], [r for r in sel if r["judge"] == "right"]
            alone = [n for n in names if n != "G"]

            def nc(rs: List[Dict[str, Any]]) -> str:
                return f"{len(rs)} ({sum(r['n_candidates'] for r in rs)})"

            out.append(f"### {kind}s — {nc(wrong)} wrong and {nc(right)} right pairs\n")
            out.append("| check | wrong pairs it refuses | wrong pairs ONLY it refuses | right pairs it refuses |")
            out.append("|---|---:|---:|---:|")
            for nme in names:
                w_any = [r for r in wrong if refuses(r, nme)]
                w_all = [r for r in wrong if refuses(r, nme, "all")]
                only = [] if nme == "G" else [r for r in w_any if not any(refuses(r, o) for o in alone if o != nme)]
                rt = [r for r in right if refuses(r, nme)]
                rt_all = [r for r in right if refuses(r, nme, "all")]
                out.append(f"| {nme} | {nc(w_any)} [{len(w_all)}] of {len(wrong)} | {'—' if nme == 'G' else nc(only)} | "
                           f"{nc(rt)} [{len(rt_all)}] of {len(right)} |")
                r2[f"{kind} {nme}"] = {"wrong": len(wrong), "refuses_wrong": len(w_any), "refuses_wrong_all_runs": len(w_all),
                                       "only_it": len(only), "only_it_programs": sorted(name(str(r["program"])) for r in only),
                                       "right": len(right), "refuses_right": len(rt), "refuses_right_all_runs": len(rt_all),
                                       "refuses_right_programs": sorted(name(str(r["program"])) for r in rt)}
            none = [r for r in wrong if not any(refuses(r, o) for o in alone)]
            out.append(f"\nWrong pairs that no check alone refuses: {nc(none)}"
                       + (" — " + ", ".join(name(str(r["program"])) for r in none[:20]) if none else "") + ".")
            r2[f"{kind} none"] = sorted(name(str(r["program"])) for r in none)
            if kind == "directive":
                soft = [r for r in sel if any((x.get("matrix") or {}).get("verdict") == "beyond-floor" for x in r["checks"].get("S") or [])]
                out.append(f"The matrix's soft verdict (a difference between thread counts beyond the noise, which the gate lets "
                           f"stand on a clean sanitizer run): on {len(soft)} pairs — {sum(1 for r in soft if r['judge'] == 'wrong')} "
                           f"wrong, {sum(1 for r in soft if r['judge'] == 'right')} right.")
                r2["directive soft"] = {"pairs": len(soft), "wrong": sum(1 for r in soft if r["judge"] == "wrong"),
                                        "right": sum(1 for r in soft if r["judge"] == "right"),
                                        "programs": sorted(name(str(r["program"])) for r in soft)}
            out.append("")
        data["R2"] = r2
        out.append("## R3 — the second input\n")
        r3: Dict[str, Any] = {}
        for kind in ("rewrite", "directive"):
            sel = by_pair([r for r in have if r["kind"] == kind and r["base_state"] == "passes" and r["judge"] == "wrong"
                           and not r["pre_program"]])
            only2 = [r for r in sel if refuses(r, "O2") and not refuses(r, "O1")]
            only1 = [r for r in sel if refuses(r, "O1") and not refuses(r, "O2")]
            both = [r for r in sel if refuses(r, "O1") and refuses(r, "O2")]
            neither = [r for r in sel if not refuses(r, "O1") and not refuses(r, "O2")]

            def nc2(rs: List[Dict[str, Any]]) -> str:
                return f"{len(rs)} ({sum(r['n_candidates'] for r in rs)} candidates)"

            # with a directive the output can depend on the run: "in every run" = refused on that input in all three runs
            # and passed on the other in all three
            steady2 = [r for r in only2 if refuses(r, "O2", "all")]
            steady1 = [r for r in only1 if refuses(r, "O1", "all")]
            out.append(f"- **{kind}s**, {nc2(sel)} wrong pairs: the output check refuses {nc2(both)} on both inputs, "
                       f"{nc2(only1)} on the shipped input only"
                       + (f" (in every run: {len(steady1)})" if kind == "directive" and only1 else "")
                       + f", **{nc2(only2)} on the perturbed input only**"
                       + (f" (in every run: {len(steady2)})" if kind == "directive" and only2 else "")
                       + (" — " + ", ".join(sorted({name(str(r['program'])) for r in only2})[:25])
                          + (" …" if len(only2) > 25 else "") if only2 else "")
                       + f"; {nc2(neither)} on neither.")
            r3[kind] = {"wrong": len(sel), "both": len(both), "shipped_only": len(only1), "perturbed_only": len(only2),
                        "neither": len(neither), "perturbed_only_programs": sorted(name(str(r["program"])) for r in only2),
                        "shipped_only_programs": sorted(name(str(r["program"])) for r in only1),
                        "neither_programs": sorted(name(str(r["program"])) for r in neither),
                        "perturbed_only_every_run": len(steady2), "shipped_only_every_run": len(steady1),
                        "perturbed_only_candidates": sum(r["n_candidates"] for r in only2)}
        data["R3"] = r3
        out.append("")
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / f"readout_{c['name']}.md").write_text("\n".join(out) + "\n")
    (a.out / f"readout_{c['name']}.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print("\n".join(out[:70]))
    if not complete and not a.partial:
        print("\nPARTIAL: not every program has a verdict or not every pair a replay (pass --partial for a pilot)", file=sys.stderr)
        return 1
    return 0


# ------------------------------------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("corpus", help="rebuild every candidate of the given runs from the archive (text only)")
    sp.add_argument("--groups", default="", help="comma-separated registry groups, e.g. E1-v6,E2-v6b")
    sp.add_argument("--runs", default="", help="comma-separated run ids")
    sp.add_argument("--exclude-runs", default="", help="runs of those groups to leave out, by name")
    sp.add_argument("--name", required=True)
    sp.add_argument("--out", type=Path, required=True)
    sp.set_defaults(fn=cmd_corpus)

    for name, fn, hlp in (("judge", cmd_judge, "the harness on each distinct program (J1, J2)"),
                          ("checks", cmd_checks, "the gate's checks on each candidate, one at a time")):
        sp = sub.add_parser(name, help=hlp)
        sp.add_argument("--corpus", type=Path, required=True)
        sp.add_argument("--part", default="1/1", help="k/n: this lane's share")
        sp.add_argument("--sample", default="", help="the pilot: REWRITES,DIRECTIVES candidates drawn with --seed")
        sp.add_argument("--seed", type=int, default=7)
        sp.add_argument("--per-benchmark", type=int, default=0,
                        help="a pilot: the first N distinct programs of every benchmark (by hash)")
        if name == "judge":
            sp.add_argument("--run-id", required=True)
            sp.add_argument("--threads", default="6,12")
            sp.add_argument("--repeats", type=int, default=5)
            sp.add_argument("--tsan-runs", type=int, default=3)
            sp.add_argument("--tsan-threads", type=int, default=12)
            sp.add_argument("--tsan-limit", type=int, default=1800, help="seconds one sanitizer run may take")
            sp.add_argument("--skip-j2", action="store_true")
        else:
            sp.add_argument("--out", type=Path, required=True)
        sp.set_defaults(fn=fn)
    sp = sub.add_parser("drb", help="Part B: the gate's safety validation on every DataRaceBench kernel")
    sp.add_argument("--part", default="1/1")
    sp.add_argument("--runs", type=int, default=5)
    sp.add_argument("--only", default="", help="kernel name prefixes, comma-separated (a tooling test)")
    sp.add_argument("--out", type=Path, required=True)
    sp.set_defaults(fn=cmd_drb)
    sp = sub.add_parser("readout-drb", help="Part B's table")
    sp.add_argument("--run", required=True)
    sp.add_argument("--out", type=Path, required=True)
    sp.set_defaults(fn=cmd_readout_drb)
    sp = sub.add_parser("readout", help="the tables: gate x judge, each check alone, the second input")
    sp.add_argument("--corpus", type=Path, required=True)
    sp.add_argument("--judge", required=True, help="comma-separated judge run ids")
    sp.add_argument("--checks", default="", help="comma-separated checks run ids")
    sp.add_argument("--partial", action="store_true", help="a pilot: do not fail when programs or pairs have no verdict")
    sp.add_argument("--out", type=Path, required=True)
    sp.set_defaults(fn=cmd_readout)
    a = ap.parse_args()
    return int(a.fn(a))


if __name__ == "__main__":
    sys.exit(main())
