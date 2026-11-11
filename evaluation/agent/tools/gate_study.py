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


def _tsan_at_size(bench: str, prog_file: Path, runs: int, threads: int) -> Dict[str, Any]:
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
    rec: Dict[str, Any] = {"verify_size": vsize, "threads": threads, "runs": []}
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
                r = subprocess.run([str(work / "tsan_par")], capture_output=True, text=True, cwd=work, env=env, timeout=1800)
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
    if a.sample:
        wanted = sorted({str(x["program"]) for x in _sample(c, a.sample, a.seed)})
    else:
        wanted = _slice(sorted({str(x["program"]) for x in c["candidates"]}), a.part)
    run_dir = EVAL / "agent" / "runs" / a.run_id
    side = run_dir / "gate_study"
    side.mkdir(parents=True, exist_ok=True)
    _manifest(side, {"step": "judge", "corpus": c["name"], "corpus_commit": c["commit"], "part": a.part,
                     "sample": a.sample, "seed": a.seed, "programs": len(wanted), "threads": a.threads,
                     "repeats": a.repeats, "tsan_runs": a.tsan_runs, "tsan_threads": a.tsan_threads})
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
                rec = _tsan_at_size(bench, prog_file, a.tsan_runs, a.tsan_threads)
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
    pairs = _pairs(_sample(c, a.sample, a.seed)) if a.sample else _slice([f"{b} {p}" for b, p in _pairs(c["candidates"])], a.part)
    todo = [tuple(x.split(" ")) if isinstance(x, str) else x for x in pairs]
    a.out.mkdir(parents=True, exist_ok=True)
    _manifest(a.out, {"step": "checks", "corpus": c["name"], "corpus_commit": c["commit"], "part": a.part,
                      "sample": a.sample, "seed": a.seed, "pairs": len(todo), "check_inputs": [[SEED]],
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
        if name == "judge":
            sp.add_argument("--run-id", required=True)
            sp.add_argument("--threads", default="6,12")
            sp.add_argument("--repeats", type=int, default=5)
            sp.add_argument("--tsan-runs", type=int, default=3)
            sp.add_argument("--tsan-threads", type=int, default=12)
            sp.add_argument("--skip-j2", action="store_true")
        else:
            sp.add_argument("--out", type=Path, required=True)
        sp.set_defaults(fn=fn)
    a = ap.parse_args()
    return int(a.fn(a))


if __name__ == "__main__":
    sys.exit(main())
