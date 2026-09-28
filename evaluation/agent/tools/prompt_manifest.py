#!/usr/bin/env python3
"""Every arm's prompt, hashed: which arms a change to the prompt code touches (prompt review M2, 28 Sep 2026).

The texts the models read are assembled from shared blocks: the agent's system prompt and request, the
twin's copies of them, the model alone's mirror.  A change to one block reaches every arm that shares it,
and an exact-substring replace whose target moved silently stops applying.  So a change declares the arms
it is meant to touch, and this check proves it did exactly that: for every arm in config/arms.json it
renders the system prompt and the first request with the arm's OWN runner code (the agent, its twin, the
model alone) on fixed fixtures, and compares their hashes with the stored manifest.

    venv/bin/python evaluation/agent/tools/prompt_manifest.py capture NAME DIR SRC   # a fixture, once
    venv/bin/python evaluation/agent/tools/prompt_manifest.py build [--agent-root DIR]
    venv/bin/python evaluation/agent/tools/prompt_manifest.py diff [--expect ARM,ARM | --expect-none]
    venv/bin/python evaluation/agent/tools/prompt_manifest.py show ARM FIXTURE

A fixture (tools/fixtures/prompt/<name>/) is a source file and exactly the files of its DiscoPoP profile
that the agent reads to build the evidence — recorded while the agent builds it, so nothing else is
copied.  `--agent-root` renders from another checkout of the agent (a worktree of an earlier commit):
the manifest the first change is compared with was built from the code BEFORE that change.

Settings a run measures (the numerical noise floor) are fixed stand-ins here: they are the same before
and after a change, which is all a comparison needs.  The benchmark's protected lines are one fixed
set for every fixture, for the same reason.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FIXTURES = HERE / "fixtures" / "prompt"
MANIFEST = HERE.parent / "config" / "prompt_manifest.json"
BENCH = "polybench/2mm"            # the timeable kernel test_arms.py resolves arms on
PROTECTED = ('#include "pb_harness.h"', "PB_MAIN(kernel)")
PROTECTED_NOTE = "The harness calls the kernel once per repetition."
FIRST_REASON = "DiscoPoP found no applicable parallelism pattern for this region"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "shared"))


def _import_agent(root: Optional[Path]) -> None:
    sys.path.insert(0, str(root or REPO))


# ---- fixtures ---------------------------------------------------------------------------------

def _fixture_meta(name: str) -> Dict[str, Any]:
    return dict(json.loads((FIXTURES / name / "fixture.json").read_text()))


def _evidence(dp: Path, src: Path, exclude: Tuple[str, ...], line: int = 0) -> Tuple[Any, Any]:
    """(candidate, evidence) for the fixture's region: the first Tier-2 loop in the agent's rank order
    (as the evidence pilot picks it), or the loop starting at `line`."""
    from discopop_agent.args import parse_args
    from discopop_agent.evidence import assemble
    from discopop_agent.plan import build_candidates
    saved = sys.argv
    sys.argv = ["x", "--discopop-dir", str(dp), "--source-file", str(src), "--min-runtime-share", "0"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            args = parse_args()
    finally:
        sys.argv = saved
    cands = build_candidates(dp, str(src), args.lambda_penalty, args.min_workload, impact=None,
                             min_impact=args.min_impact, min_runtime_share=0.0, exclude_functions=exclude)
    loops = [c for c in cands if c.region.region_type == "loop" and c.tier == 2
             and (not line or c.region.start_line == line)]
    if not loops:
        raise SystemExit(f"{src.name}: no Tier-2 loop" + (f" at line {line}" if line else ""))
    with contextlib.redirect_stdout(io.StringIO()):
        return loops[0], assemble(loops[0], dp / "profiler", FIRST_REASON)


def capture(name: str, origin: Path, src_name: str, exclude: Tuple[str, ...], line: int) -> None:
    """Copy `origin`/SRC and the profile files the agent reads into tools/fixtures/prompt/NAME."""
    opened: Set[str] = set()
    root = str(origin.resolve())

    def hook(event: str, args: Tuple[Any, ...]) -> None:
        if event == "open" and isinstance(args[0], (str, Path)) and str(Path(args[0]).resolve()).startswith(root):
            opened.add(str(Path(args[0]).resolve()))
    sys.addaudithook(hook)
    cand, ev = _evidence(origin / ".discopop", origin / src_name, exclude, line)
    dest = FIXTURES / name
    shutil.rmtree(dest, ignore_errors=True)
    files = sorted(p for p in opened if Path(p).is_file())
    for p in files:
        rel = Path(p).relative_to(origin.resolve())
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest / rel)
    shutil.copy2(origin / src_name, dest / src_name)
    (dest / "fixture.json").write_text(json.dumps({
        "source": src_name, "exclude_functions": list(exclude), "region_line": cand.region.start_line,
        "origin": str(origin.resolve().relative_to(REPO)) if origin.resolve().is_relative_to(REPO) else str(origin),
        "files": [str(Path(p).relative_to(origin.resolve())) for p in files]}, indent=1) + "\n")
    print(f"{name}: loop at line {cand.region.start_line}, {len(files)} profile file(s): "
          + ", ".join(str(Path(p).relative_to(origin.resolve())) for p in files))


def fixture_evidence(name: str) -> Tuple[Any, Any]:
    m = _fixture_meta(name)
    d = FIXTURES / name
    return _evidence(d / ".discopop", d / m["source"], tuple(m["exclude_functions"]), int(m["region_line"]))


# ---- rendering, with each arm's own runner code -------------------------------------------------

def _agent_args(spec: Dict[str, Any], dp: Path, src: Path) -> Any:
    import cli
    from discopop_agent.args import parse_args
    argv = ["x", "--discopop-dir", str(dp), "--source-file", str(src), *cli._common_flags(),
            *spec.get("flags", []), *cli._timing_flags(spec, BENCH),
            *cli._evidence_file_flags(spec, BENCH, None, "", ""), "--edit-mode", "direct",
            *[x for p in PROTECTED for x in ("--protected-line", p)], "--protected-note", PROTECTED_NOTE]
    saved = sys.argv
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            args = parse_args()
    finally:
        sys.argv = saved
    args.noise_floor = 1e-9 if args.numeric_tolerance else 0.0      # the measured floor's stand-in
    return args


def _gate(args: Any, as_shipped: bool) -> Any:
    """The run's GateFacts through the agent's own function; before it existed (the code the first
    manifest was built from), the construction phase_a.py and twin.py each wrote inline."""
    try:
        from discopop_agent.args import gate_facts
        return gate_facts(args, as_shipped=as_shipped)
    except ImportError:
        from discopop_agent.types import GateFacts
        return GateFacts(require_speedup=args.require_speedup, n_inputs=1 + len(args.check_inputs or []),
                         numeric=args.noise_floor > 0.0, stress=args.schedule_stress,
                         omit=tuple(args.prompt_omit or ()), external_evidence=args.external_evidence or "",
                         protected=tuple(args.protected_lines or ()), protected_note=args.protected_note or "",
                         judge_as_shipped=bool(args.judge_as_shipped) if as_shipped else False)


def _blockers(prevented: List[Dict[str, Any]], gate: Any) -> str:
    """The Do-All blockers as the agent's 'no pattern' feedback renders them (phases/verdicts.py)."""
    from discopop_agent.llm.render import fmt_blockers
    try:
        return str(fmt_blockers(prevented[:12], frozenset(getattr(gate, "changes", ()))))  # type: ignore[call-arg]
    except TypeError:
        return str(fmt_blockers(prevented[:12]))


def _flag(flags: List[str], name: str, default: str) -> str:
    return flags[flags.index(name) + 1] if name in flags else default


def render(arm: str, spec: Dict[str, Any], fixture: str, ev: Any) -> Dict[str, str]:
    """{'system', 'request'[, 'feedback']} for one arm on one fixture."""
    d = FIXTURES / fixture
    m = _fixture_meta(fixture)
    src = d / m["source"]
    ws = Path("/workspace") / m["source"]
    runner = spec.get("runner")
    if runner == "bare_llm":
        from discopop_agent import bare_llm
        flags = list(spec.get("flags", []))
        prompt = _flag(flags, "--prompt", "mirror")
        speed = "--no-require-speedup" not in flags
        try:
            gate = bare_llm.mirror_gate(speed, int(_flag(flags, "--prompt-version", "1")))  # type: ignore[call-arg]
        except TypeError:
            gate = bare_llm.mirror_gate(speed)
        excl = list(m["exclude_functions"])
        request = (bare_llm._request_mirror([m["source"]], excl, PROTECTED, PROTECTED_NOTE, gate) if prompt == "mirror"
                   else {"minimal": bare_llm._request_minimal, "contract": bare_llm._request}[prompt]([m["source"]], excl))
        return {"system": bare_llm._system(prompt, gate), "request": request}
    from discopop_agent.llm.request import _build_direct_prompt
    args = _agent_args(spec, d / ".discopop", src)
    if runner == "twin":
        from discopop_agent import twin
        gate = _gate(args, as_shipped=False)
        return {"system": twin._system(gate, args.evidence_sections, args.llm_pragmas),
                "request": twin._request(_build_direct_prompt(ev, ws, args.evidence_sections, args.llm_pragmas, gate))}
    from discopop_agent.llm.prompts import _system_prompt
    gate = _gate(args, as_shipped=True)
    return {"system": _system_prompt("direct", args.llm_pragmas, args.llm_recon and args.llm_recon_mode == "folded",
                                     gate, args.evidence_sections),
            "request": _build_direct_prompt(ev, ws, args.evidence_sections, args.llm_pragmas, gate),
            "feedback": _blockers(list(ev.prevented_deps or []), gate)}


def _arms() -> Dict[str, Dict[str, Any]]:
    import cli
    doc = json.loads((HERE.parent / "config" / "arms.json").read_text())
    return dict(cli.resolve_twins(doc["arms"]))


def _h(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def render_all() -> Dict[str, Any]:
    fixtures = sorted(p.name for p in FIXTURES.iterdir() if (p / "fixture.json").exists())
    evs = {f: fixture_evidence(f)[1] for f in fixtures}
    out: Dict[str, Any] = {"fixtures": {f: {"region_line": _fixture_meta(f)["region_line"]} for f in fixtures},
                           "arms": {}}
    for arm, spec in sorted(_arms().items()):
        per: Dict[str, str] = {}
        for f in fixtures:
            texts = render(arm, spec, f, evs[f])
            per["system"] = _h(texts["system"])          # the same on every fixture
            for part, text in texts.items():
                if part != "system":
                    per[f"{part}:{f}"] = _h(text)
        out["arms"][arm] = per
    return out


def _head(root: Path) -> str:
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "discopop_agent"],
                           capture_output=True, text=True).stdout.strip()
    return sha[:8] + (" + uncommitted changes to discopop_agent/" if dirty else "")


def changed(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, List[str]]:
    """arm -> the parts whose hash differs (an arm added or removed counts whole)."""
    out: Dict[str, List[str]] = {}
    for arm in sorted(set(old["arms"]) | set(new["arms"])):
        a, b = old["arms"].get(arm), new["arms"].get(arm)
        if a is None or b is None:
            out[arm] = ["(arm added)" if a is None else "(arm removed)"]
            continue
        parts = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if parts:
            out[arm] = parts
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("name")
    c.add_argument("dir", type=Path, help="a directory holding the source and its .discopop")
    c.add_argument("src")
    c.add_argument("--exclude", default="main", help="comma list of functions out of scope")
    c.add_argument("--line", type=int, default=0, help="the region's first line (default: the first Tier-2 loop)")
    b = sub.add_parser("build")
    b.add_argument("--agent-root", type=Path, default=None, help="render with the agent code of this checkout")
    d = sub.add_parser("diff")
    d.add_argument("--agent-root", type=Path, default=None)
    g = d.add_mutually_exclusive_group()
    g.add_argument("--expect", default=None, help="comma list: exactly these arms may change")
    g.add_argument("--expect-none", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("arm")
    s.add_argument("fixture")
    a = ap.parse_args()
    _import_agent(getattr(a, "agent_root", None))
    if a.cmd == "capture":
        capture(a.name, a.dir, a.src, tuple(x for x in a.exclude.split(",") if x), a.line)
        return 0
    if a.cmd == "show":
        texts = render(a.arm, _arms()[a.arm], a.fixture, fixture_evidence(a.fixture)[1])
        for part, text in texts.items():
            print(f"===== {part} =====\n{text}")
        return 0
    new = render_all()
    new["built_from"] = _head(a.agent_root or REPO)
    if a.cmd == "build":
        MANIFEST.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        print(f"{MANIFEST.relative_to(REPO)}: {len(new['arms'])} arms × {len(new['fixtures'])} fixtures, "
              f"built from {new['built_from']}")
        return 0
    old = json.loads(MANIFEST.read_text())
    diff = changed(old, new)
    print(f"manifest built from {old.get('built_from')}; rendered now from {new['built_from']}")
    for arm, parts in diff.items():
        print(f"  changed  {arm}: {', '.join(parts)}")
    if not diff:
        print("  no arm's text changed")
    want = set() if a.expect_none else set(a.expect.split(",")) if a.expect else None
    if want is None:
        return 0
    got = set(diff)
    if got != want:
        print(f"FAIL: expected exactly {sorted(want) or 'none'}; unexpected {sorted(got - want)}, "
              f"unchanged {sorted(want - got)}")
        return 1
    print("OK: exactly the declared arms changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
