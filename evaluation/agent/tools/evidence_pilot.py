#!/usr/bin/env python3
"""Evidence-mechanism pilot: does DiscoPoP's evidence change what the model writes where it is decisive?

Pre-registered in THESIS_EXPERIMENTS.md §6 (28 Sep 2026, "Evidence-mechanism pilot on ORDER-2"). ORDER-2 is a
loop of two statements whose fission order is decided by index tables in a hidden header:

    u[ju[i]] += v[kv[i]] * c[i];      /* S1 */
    v[jv[i]] += u[ku[i]] * d[i];      /* S2 */

  version X (id k17): kv[i] = i-1, ku[i] = LEN_1D+i — S2 feeds S1, the loop must be split S2 first;
  version Y (id k42): ku[i] = i-1, kv[i] = LEN_1D+i — S1 feeds S2, the textual order is right.

The model's file is byte-identical between the versions up to the opaque id; DiscoPoP's evidence names the
carrier (RAW on `v` in X, on `u` in Y). Every call is ONE model turn in the agent's direct mode with the agent's
own system prompt and request (llm/prompts._system_prompt, llm/request._build_direct_prompt), the file tools
confined to a fresh workspace holding only the model's file — no agent loop, no gate, no feedback.

Arms: full evidence (`full`), full minus the generic fix note (`no_note`), no evidence (`none`).
Success per call: the returned file compiles against its header, prints exactly the original's output on the
shipped and the perturbed input, contains no `#pragma omp`, and DiscoPoP's re-profile reports every loop of the
kernel that writes `u` or `v` as an applicable Do-All. Everything else is classed.

    venv/bin/python evaluation/agent/tools/evidence_pilot.py --out <dir> [--n 10] [--jobs 4]
    venv/bin/python evaluation/agent/tools/evidence_pilot.py --out <dir> --score-only   (re-score saved answers)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
import hot_loop_coverage  # noqa: E402

MODEL = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5"
# arm -> (model, evidence: "full" | "no_note" | "none" | "order"). The first pilot ran full, no_note, none (Haiku);
# the follow-up (pre-registered 28 Sep) runs order (Haiku), sonnet_full, sonnet_none.
ARM_SPECS: Dict[str, Tuple[str, str]] = {
    "full": (MODEL, "full"), "no_note": (MODEL, "no_note"), "none": (MODEL, "none"),
    "order": (MODEL, "order"), "sonnet_full": (SONNET, "full"), "sonnet_none": (SONNET, "none"),
}
LEN = 32000
VERSIONS = {"X": ("k17", "kv[i] = (int)(i - 1); ku[i] = (int)(LEN_1D + i);"),
            "Y": ("k42", "ku[i] = (int)(i - 1); kv[i] = (int)(LEN_1D + i);")}
ARMS = ("full", "no_note", "none")      # the first pilot's arms (the default of --arms)

MODEL_FILE = """#include "evk/%(id)s.h"

static real_t kernel_%(id)s(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] += u[ku[i]] * d[i];
    }
    return (real_t)0;
}

PB_MAIN(kernel_%(id)s)
"""

HEADER = """/* Measurement harness (hidden from the model): data, index tables, perturbed input, digest, main. */
#ifndef PB_EVK_HARNESS
#define PB_EVK_HARNESS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef double real_t;
#define LEN_1D %(len)d
static real_t *u, *v, *c, *d;
static int *ju, *jv, *ku, *kv;
static unsigned long long pb_state = 88172645463325252ULL;
static double pb_uniform(void) { pb_state ^= pb_state << 13; pb_state ^= pb_state >> 7; pb_state ^= pb_state << 17;
                                 return (double)(pb_state %% 1000003ULL) / 1000003.0; }
static void pb_setup(int argc, char **argv) {
  u = (real_t *)malloc(sizeof(real_t) * 2 * LEN_1D); v = (real_t *)malloc(sizeof(real_t) * 2 * LEN_1D);
  c = (real_t *)malloc(sizeof(real_t) * LEN_1D); d = (real_t *)malloc(sizeof(real_t) * LEN_1D);
  ju = (int *)malloc(sizeof(int) * LEN_1D); jv = (int *)malloc(sizeof(int) * LEN_1D);
  ku = (int *)malloc(sizeof(int) * LEN_1D); kv = (int *)malloc(sizeof(int) * LEN_1D);
  for (long i = 0; i < 2L * LEN_1D; i++) {
    u[i] = (real_t)0.75 + (real_t)((i * 37L) %% 1000) * (real_t)0.0005;
    v[i] = (real_t)0.75 + (real_t)((i * 53L) %% 997) * (real_t)0.0005; }
  for (long i = 0; i < LEN_1D; i++) {
    c[i] = (real_t)0.75 + (real_t)((i * 71L) %% 991) * (real_t)0.0005;
    d[i] = (real_t)0.75 + (real_t)((i * 89L) %% 983) * (real_t)0.0005;
    ju[i] = (int)i; jv[i] = (int)i;
    %(tables)s
  }
  if (argc > 1) {                       /* the perturbed input: values change, the index tables never do */
    pb_state ^= (unsigned long long)strtoull(argv[1], NULL, 10) * 2654435761ULL;
    for (long i = 0; i < 2L * LEN_1D; i++) { u[i] *= 1.0 + 0.2 * pb_uniform(); v[i] *= 1.0 + 0.2 * pb_uniform(); }
    for (long i = 0; i < LEN_1D; i++) { c[i] *= 1.0 + 0.1 * pb_uniform(); d[i] *= 1.0 + 0.1 * pb_uniform(); }
  }
}
static void pb_finish(real_t r) {
  double su = 0, sv = 0, wu = 0, wv = 0;
  for (long i = 0; i < 2L * LEN_1D; i++) { su += u[i]; sv += v[i]; wu += u[i] * (double)(i %% 13); wv += v[i] * (double)(i %% 11); }
  printf("%%.17g %%.17g %%.17g %%.17g %%.17g\\n", (double)r, su, sv, wu, wv);
}
#define PB_MAIN(K) int main(int argc, char **argv) { pb_setup(argc, argv); real_t pb_r = K(); pb_finish(pb_r); return 0; }
#endif
"""

PROTECTED_NOTE = ("`PB_MAIN(kernel_%s)` expands to `main`: it sets up the data the included header declares, calls "
                  "`kernel_%s` once and prints its result. `LEN_1D`, the length of the arrays, is set in the included "
                  "header: " + str(LEN) + ".")


def _run(cmd: List[str], cwd: Path, env: Optional[Dict[str, str]] = None, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def _cc() -> List[str]:
    if sys.platform == "darwin":
        sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True).stdout.strip()
        return ["/usr/local/Cellar/llvm@19/19.1.7/bin/clang"] + (["-isysroot", sdk] if sdk else [])
    return [shutil.which("clang-20") or "clang"]


def package(out: Path) -> Dict[str, Dict[str, Path]]:
    """The two versions: the model file in pkg/<id>/, the header in hdr/evk/<id>.h (outside every package)."""
    pk: Dict[str, Dict[str, Path]] = {}
    for ver, (kid, tables) in VERSIONS.items():
        hdr = out / "hdr" / "evk" / f"{kid}.h"
        hdr.parent.mkdir(parents=True, exist_ok=True)
        hdr.write_text(HEADER % {"len": LEN, "tables": tables})
        d = out / "pkg" / kid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{kid}.c").write_text(MODEL_FILE % {"id": kid})
        pk[ver] = {"id": kid, "dir": d, "src": d / f"{kid}.c", "inc": out / "hdr"}  # type: ignore[dict-item]
    return pk


def outputs(src: Path, inc: Path, work: Path) -> Tuple[Optional[str], Optional[str], str]:
    """(shipped output, perturbed output, compile error text) of a program."""
    exe = work / (src.stem + ".bin")
    r = _run(_cc() + ["-O2", "-I", str(inc), str(src), "-o", str(exe)], work)
    if r.returncode != 0:
        return None, None, r.stderr[-800:]
    a = _run([str(exe)], work, timeout=120)
    b = _run([str(exe), "7"], work, timeout=120)
    return (a.stdout if a.returncode == 0 else None), (b.stdout if b.returncode == 0 else None), ""


def profile(src: Path, inc: Path, work: Path) -> Optional[Path]:
    """DiscoPoP on a copy of `src` in a CLEAN `work`; the profile directory, or None. (DiscoPoP reuses what it
    finds in an existing .discopop: a second profile in the same directory mixed with the first — 28 Sep.)"""
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, work / src.name)
    env = {**os.environ, "CPATH": str(inc), "PATH": f"{REPO / 'venv' / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    if _run(["discopop_cc", src.name, "-o", "a.out"], work, env).returncode != 0 or not (work / "a.out").exists():
        return None
    if _run(["./a.out"], work, env).returncode != 0:
        return None
    dp = work / ".discopop"
    for _ in range(5):
        try:
            if _run(["discopop_explorer"], dp, env, timeout=300).returncode == 0:
                return dp
        except subprocess.TimeoutExpired:
            pass
        shutil.rmtree(dp / "explorer", ignore_errors=True)
    return None


def order_note(ev: Any, src_lines: List[str], lo: int, hi: int) -> str:
    """The follow-up pilot's `order` arm: each loop-carried RAW between two different lines of the loop, restated
    as the order it imposes — built mechanically from DiscoPoP's records (from_line = the reading line, the sink;
    to_line = the writing line, the source; evidence/deps.py), the same rule for any record."""
    out: List[str] = []
    seen: Set[Tuple[int, int, str]] = set()
    for d in getattr(ev, "raw_deps", []) or []:
        s_ln, w_ln, var = int(d.from_line), int(d.to_line), str(d.variable)
        if not (lo <= s_ln <= hi and lo <= w_ln <= hi) or s_ln == w_ln or (s_ln, w_ln, var) in seen:
            continue
        if getattr(d, "kind", "") != "array":       # array elements only: not the loop counter or a scalar
            continue
        seen.add((s_ln, w_ln, var))
        name = re.sub(r"^GEPRESULT_", "", var)
        s_txt, w_txt = src_lines[s_ln - 1].strip(), src_lines[w_ln - 1].strip()
        out.append(f"- Line {s_ln} (`{s_txt}`) reads an element of `{name}` that line {w_ln} (`{w_txt}`) wrote in an "
                   f"EARLIER iteration of this loop. The value must flow from line {w_ln} to line {s_ln}: if you split "
                   f"the loop, the loop holding line {w_ln} has to run completely before the loop holding line {s_ln}; "
                   f"reading `{name}`'s values from before the loop would change the result.")
    if not out:
        return ""
    return "### What the observed dependence means for a rewrite (from DiscoPoP's records)\n" + "\n".join(out) + "\n\n"


def requests(pk: Dict[str, Dict[str, Any]], out: Path, arms: Tuple[str, ...] = ARMS) -> Dict[Tuple[str, str], Tuple[str, str]]:
    """(version, arm) -> (system prompt, request) for the kernel loop region, as the agent builds them."""
    from discopop_agent.args import parse_args
    from discopop_agent.evidence import assemble
    from discopop_agent.llm.prompts import _system_prompt
    from discopop_agent.llm.render import EVIDENCE_SECTIONS
    from discopop_agent.llm.request import _build_direct_prompt
    from discopop_agent.plan import build_candidates
    from discopop_agent.types import GateFacts
    res: Dict[Tuple[str, str], Tuple[str, str]] = {}
    for ver, p in pk.items():
        dp = profile(p["src"], p["inc"], out / "profile" / p["id"])
        if dp is None:
            raise SystemExit(f"{ver}: DiscoPoP profile failed")
        saved = sys.argv
        sys.argv = ["x", "--discopop-dir", str(dp), "--source-file", str(dp.parent / p["src"].name),
                    "--min-runtime-share", "0"]
        try:
            args = parse_args()
        finally:
            sys.argv = saved
        cands = build_candidates(dp, str(dp.parent / p["src"].name), args.lambda_penalty, args.min_workload,
                                 impact=None, min_impact=args.min_impact, min_runtime_share=0.0,
                                 exclude_functions=("main",))
        loop = next(c for c in cands if c.region.region_type == "loop")
        if loop.tier != 2:
            raise SystemExit(f"{ver}: the loop is Tier {loop.tier}, not Tier 2 — the model would not be asked")
        ev = assemble(loop, dp / "profiler", p["id"])
        gate = GateFacts(require_speedup=False, n_inputs=2, numeric=False, stress=True,
                         protected=(f'#include "evk/{p["id"]}.h"', f'PB_MAIN(kernel_{p["id"]})'),
                         protected_note=PROTECTED_NOTE % (p["id"], p["id"]))
        ws_file = Path("/workspace") / p["src"].name          # replaced per call by the real workspace path
        src_lines = p["src"].read_text().splitlines()
        for arm in arms:
            mode = ARM_SPECS[arm][1]
            inc: Optional[Set[str]] = (None if mode in ("full", "order") else set(EVIDENCE_SECTIONS) - {"array_note"}
                                       if mode == "no_note" else set())
            req = _build_direct_prompt(ev, ws_file, inc, False, gate)
            if mode == "order":
                note = order_note(ev, src_lines, loop.region.start_line, loop.region.end_line)
                if not note:
                    raise SystemExit(f"{ver}: no carried RAW between two lines to restate")
                # placed just before the closing task instruction, which the request ends with
                cut = req.rfind("Edit `")
                req = req[:cut] + note + req[cut:] if cut > 0 else req + "\n" + note
            res[(ver, arm)] = (_system_prompt("direct", False, False, gate, inc), req)
    return res


def call(system: str, request: str, src: Path, ws: Path, model: str = MODEL) -> Dict[str, Any]:
    from discopop_agent.llm.providers import _complete_claude_agent_sdk
    ws.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, ws / src.name)
    req = request.replace(str(Path("/workspace") / src.name), str(ws / src.name))
    t0 = time.time()
    try:
        reply = _complete_claude_agent_sdk(model, system, [{"role": "user", "content": req}],
                                           session_key=f"pilot-{ws.name}", workspace=ws, stateless=True)
        err = ""
    except Exception as e:  # noqa: BLE001 — a failed call is a recorded outcome
        reply, err = "", f"{type(e).__name__}: {e}"
    return {"seconds": round(time.time() - t0, 1), "reply": reply[-2000:], "error": err}


def score(ver: str, pk: Dict[str, Any], answer: Path, ref: Tuple[str, str], work: Path) -> Dict[str, Any]:
    text = answer.read_text()
    if re.search(r"#\s*pragma\s+omp", text):
        return {"class": "pragma-written", "success": False}
    if text == pk["src"].read_text():
        return {"class": "unchanged", "success": False}
    a, b, cerr = outputs(answer, pk["inc"], work)
    if cerr:
        return {"class": "compile-error", "success": False, "detail": cerr}
    if a is None or b is None:
        return {"class": "run-failed", "success": False}
    if (a, b) != ref:
        return {"class": "wrong-output", "success": False}
    dp = profile(answer, pk["inc"], work / "dp")
    if dp is None:
        return {"class": "profile-failed", "success": False}
    pats = json.loads((dp / "explorer" / "patterns.json").read_text()).get("patterns", {})
    doall = {int(str(x.get("start_line", "0:0")).split(":")[1]) for x in pats.get("do_all", [])
             if str(x.get("applicable_pattern")) == "True"}
    prog = hot_loop_coverage.Program(text, f"kernel_{pk['id']}")
    f = prog.funcs.get(f"kernel_{pk['id']}")
    loops = []
    if f is not None:
        for kw, _c, end in prog.for_loops(f.lo + 1, f.hi - 1):
            w = prog.region_writes(f, kw, end)
            if w & {"u", "v"}:
                loops.append((prog.toks[kw].line, sorted(w)))
    blocked = [ln for ln, _w in loops if ln not in doall]
    inspector = bool(re.search(r"\bkv\s*\[|\bku\s*\[", text) and re.search(r"\bif\s*\(", text))
    if not loops or blocked:
        return {"class": "correct-not-parallel", "success": False, "loops": loops, "doall": sorted(doall),
                "inspector_like": inspector}
    return {"class": "success", "success": True, "loops": loops, "inspector_like": inspector}


def _one(job: Tuple[str, str, int, str, str, str, str]) -> Dict[str, Any]:
    """One call in its own process; skipped when its record exists (a resumed pilot)."""
    ver, arm, k, system, request, src, out = job
    ws = Path(out) / "calls" / f"{ver}_{arm}_{k:02d}"
    if (ws / "call.json").exists():
        return dict(json.loads((ws / "call.json").read_text()))
    rec = {"version": ver, "arm": arm, "rep": k, "model": ARM_SPECS[arm][0],
           **call(system, request, Path(src), ws, ARM_SPECS[arm][0])}
    (ws / "call.json").write_text(json.dumps(rec, indent=1))
    print(f"called {ver} {arm} {k:2d} ({rec['seconds']} s){' ERROR ' + str(rec['error'])[:80] if rec['error'] else ''}",
          flush=True)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--arms", default=",".join(ARMS), help="comma-separated arms of ARM_SPECS")
    ap.add_argument("--n-arm", action="append", default=[], help="arm=N: a per-arm number of calls per version")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--score-only", action="store_true")
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    pk = package(out)
    refs = {}
    with tempfile.TemporaryDirectory() as t:
        for ver, p in pk.items():
            s, pt, e = outputs(p["src"], p["inc"], Path(t))
            if e or s is None or pt is None:
                raise SystemExit(f"{ver}: the original does not build or run: {e}")
            refs[ver] = (s, pt)
    if not a.score_only:
        arms = tuple(x for x in a.arms.split(",") if x)
        unknown = [x for x in arms if x not in ARM_SPECS]
        if unknown:
            ap.error(f"unknown arm(s): {unknown}")
        n_of = {x: a.n for x in arms}
        n_of.update({k: int(v) for k, v in (x.split("=", 1) for x in a.n_arm)})
        reqs = requests(pk, out, arms)
        (out / "requests.json").write_text(json.dumps({f"{v}/{arm}": {"system": s, "request": r}
                                                       for (v, arm), (s, r) in reqs.items()}, indent=1))
        jobs = [(ver, arm, k, reqs[(ver, arm)][0], reqs[(ver, arm)][1], str(pk[ver]["src"]), str(out))
                for arm in arms for k in range(1, n_of[arm] + 1) for ver in VERSIONS]
        # one process per call: the model client runs an event loop and a CLI subprocess per call, and
        # calls sharing one process through threads were not isolated enough (28 Sep: a first launch
        # was stopped after 5 calls, one of whose answers did not land; those calls were discarded)
        with concurrent.futures.ProcessPoolExecutor(max_workers=a.jobs) as ex:
            list(ex.map(_one, jobs))
    results: List[Dict[str, Any]] = []
    for ws in sorted((out / "calls").glob("*_*_*")):
        rec = json.loads((ws / "call.json").read_text())
        ver = rec["version"]
        answer = ws / pk[ver]["src"].name
        with tempfile.TemporaryDirectory() as t:
            sc = score(ver, pk[ver], answer, refs[ver], Path(t)) if not rec.get("error") else {"class": "call-error", "success": False}
        results.append({**{k: rec[k] for k in ("version", "arm", "rep", "seconds", "error")}, **sc})
        print(f"scored {ver} {rec['arm']:7s} {rec['rep']:2d}: {sc['class']}", flush=True)
    (out / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    lines = ["| version | arm | success | classes |", "|---|---|---:|---|"]
    table: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for r in results:
        table.setdefault((r["version"], r["arm"]), []).append(r)
    for (ver, arm), rs in sorted(table.items()):
        classes: Dict[str, int] = {}
        for r in rs:
            classes[r["class"]] = classes.get(r["class"], 0) + 1
        lines.append(f"| {ver} | {arm} | {sum(r['success'] for r in rs)}/{len(rs)} | "
                     + ", ".join(f"{k} {v}" for k, v in sorted(classes.items())) + " |")
    def rate(ver: str, arm: str) -> Tuple[int, int]:
        rs = table.get((ver, arm), [])
        return sum(r["success"] for r in rs), len(rs)
    def frac(ver: str, arm: str) -> float:
        k, n = rate(ver, arm)
        return k / n if n else float("nan")
    lines.append("")
    if ("X", "full") in table and ("X", "none") in table:          # the first pilot (pre-registered 28 Sep)
        fx, nx = rate("X", "full"); ox, _ = rate("X", "none"); fy, ny = rate("Y", "full"); oy, _ = rate("Y", "none")
        go = nx > 0 and fx >= 0.7 * nx and ox <= 0.3 * nx and (fy >= oy - 0.2 * ny)
        lines.append(f"**Go/no-go (pre-registered): {'GO' if go else 'NO-GO'}** — X full {fx}/{nx} (≥ 7/10 needed), "
                     f"X none {ox}/{nx} (≤ 3/10 needed), Y full {fy}/{ny} vs none {oy}/{ny} (full ≥ none − 2/10 needed)")
    if ("X", "order") in table:                                     # the follow-up (pre-registered 28 Sep)
        go = frac("X", "order") >= 0.7 and frac("Y", "order") >= 0.8
        lines.append(f"**order (Haiku + the generated order note): {'GO' if go else 'NO-GO'}** — X {rate('X', 'order')[0]}/"
                     f"{rate('X', 'order')[1]} (≥ 7/10 needed; Haiku without evidence 0/10), Y {rate('Y', 'order')[0]}/"
                     f"{rate('Y', 'order')[1]} (≥ 8/10 needed)")
    if ("X", "sonnet_full") in table and ("X", "sonnet_none") in table:
        go = (frac("X", "sonnet_full") >= 0.7 and frac("X", "sonnet_full") - frac("X", "sonnet_none") >= 0.4
              and frac("Y", "sonnet_full") >= frac("Y", "sonnet_none") - 0.2)
        lines.append(f"**sonnet_full (Sonnet, evidence as rendered): {'GO' if go else 'NO-GO'}** — X {rate('X', 'sonnet_full')[0]}/"
                     f"{rate('X', 'sonnet_full')[1]} vs Sonnet without {rate('X', 'sonnet_none')[0]}/{rate('X', 'sonnet_none')[1]} "
                     f"(≥ 7/10 and ≥ 0.4 above needed); Y {rate('Y', 'sonnet_full')[0]}/{rate('Y', 'sonnet_full')[1]} vs "
                     f"{rate('Y', 'sonnet_none')[0]}/{rate('Y', 'sonnet_none')[1]} (no more than 0.2 below)")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
