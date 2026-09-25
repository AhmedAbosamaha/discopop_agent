#!/usr/bin/env python3
"""The campaign's registry, its folder layout, its reports, and the check that nothing is missing.

`agent/results/campaign.json` names every run, read-out and exhibit, the experiment it belongs
to, what it is for and whether it is still valid. From it:

  * the LAYOUT of agent/results/ — one folder per experiment or instrument, each holding its
    REPORT.md, analysis/ (statistics, verdict tables, figures), exhibits/ (case studies),
    runs/ (the archived runs), checks/ (verifications made during the read-out), preflight/
    (smokes before the launch) and superseded/ (runs a later one replaced);
  * the INDEXES — results/INDEX.md (every run, by experiment) and results/EXHIBITS.md (every
    case study, by experiment, with the claim it supports);
  * the REPORTS — one REPORT.md per experiment: question, status, headline, what the folder
    holds, the runs, and the experiment record's own entries for them (copied, so the report
    never disagrees with THESIS_EXPERIMENTS.md — regenerate, do not edit);
  * the CHECK — the definition of done in the RUNBOOK, as a program.

    agent/tools/campaign.py check            # exit 1 and a list when anything is missing
    agent/tools/campaign.py reports          # REPORT.md per experiment + INDEX.md + EXHIBITS.md
    agent/tools/campaign.py adopt            # ARCHIVE.json for study folders copied by hand
    agent/tools/campaign.py migrate [--apply]  # move folders to where the registry puts them

Run ids never change: every trial record, manifest and figure cites them. Only the folder a run
sits in follows the registry, and `find_run` finds it wherever it is.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
AGENT_DIR = HERE.parent
RESULTS = AGENT_DIR / "results"
REGISTRY = RESULTS / "campaign.json"
RECORD = AGENT_DIR / "docs" / "THESIS_EXPERIMENTS.md"
SECTIONS = ("runs", "checks", "preflight", "superseded")


def load() -> dict:
    return json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {"groups": [], "runs": {}, "exhibits": {}}


def _groups(reg: dict) -> Dict[str, dict]:
    return {g["id"]: g for g in reg.get("groups", [])}


def group_dir(gid: str, reg: Optional[dict] = None) -> Path:
    reg = reg or load()
    return RESULTS / _groups(reg)[gid]["folder"]


def run_home(run_id: str, reg: Optional[dict] = None) -> Path:
    """Where a run's archive belongs. Unregistered runs land in results/_unregistered/, which
    the check reports: a run is registered before it is launched."""
    reg = reg or load()
    r = reg.get("runs", {}).get(run_id)
    if not r:
        return RESULTS / "_unregistered" / run_id
    base = group_dir(r["group"], reg)
    if r["group"] == "logs":
        return base / r["section"]
    return base / r["section"] / run_id


def find_run(run_id: str, reg: Optional[dict] = None) -> Optional[Path]:
    """The archived run, wherever it sits: its registered home, the old flat layout, or a search."""
    home = run_home(run_id, reg)
    if home.exists():
        return home
    flat = RESULTS / run_id
    if flat.exists():
        return flat
    for p in RESULTS.rglob(run_id):
        if p.is_dir() and p.name == run_id:
            return p
    return None


def trial_path(run_id: str, trial_rel: str, reg: Optional[dict] = None) -> Path:
    """A trial recorded as `<...>/<run_id>/benchmarks/...` relative to results/, in today's layout."""
    root = find_run(run_id, reg)
    tail = trial_rel.split(run_id + "/", 1)[1] if run_id + "/" in trial_rel else trial_rel
    return (root / tail) if root else RESULTS / trial_rel


def exhibit_dirs() -> List[Path]:
    return sorted(p.parent for p in RESULTS.glob("**/exhibits/*/facts.json"))


def _archive_meta(d: Path) -> dict:
    try:
        return json.loads((d / "ARCHIVE.json").read_text())
    except (OSError, ValueError):
        return {}


def _files(d: Path) -> List[Path]:
    return sorted(p for p in d.rglob("*") if p.is_file() and p.name not in ("ARCHIVE.json", ".DS_Store"))


# ---------------------------------------------------------------------------------------------
# migrate / adopt
# ---------------------------------------------------------------------------------------------

def _git_mv(src: Path, dst: Path, apply: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True) if apply else None
    if apply:
        r = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=AGENT_DIR)
        if r.returncode != 0:                      # untracked content: a plain move
            src.rename(dst)
    return f"{src.relative_to(AGENT_DIR)} -> {dst.relative_to(AGENT_DIR)}"


def migrate(apply: bool) -> List[str]:
    reg = load()
    moves: List[str] = []
    for run_id in reg.get("runs", {}):
        flat, home = RESULTS / run_id, run_home(run_id, reg)
        if flat.exists() and flat != home:
            moves.append(_git_mv(flat, home, apply))
    for old, spec in reg.get("analysis", {}).items():
        src, dst = RESULTS / old, group_dir(spec["group"], reg) / spec["into"]
        if src.exists() and not dst.exists():
            moves.append(_git_mv(src, dst, apply))
    tm = AGENT_DIR / "thesis_material"
    for name, spec in reg.get("exhibits", {}).items():
        src, dst = tm / name, group_dir(spec["group"], reg) / "exhibits" / name
        if src.exists() and not dst.exists():
            moves.append(_git_mv(src, dst, apply))
    if apply:
        for leftover in (RESULTS / "_analysis", tm):
            if leftover.exists():
                for junk in ("INDEX.md", ".DS_Store"):
                    j = leftover / junk
                    if j.exists():
                        subprocess.run(["git", "rm", "-q", "--cached", str(j)], cwd=AGENT_DIR, capture_output=True)
                        j.unlink()
                if not any(leftover.iterdir()):
                    leftover.rmdir()
    return moves


def adopt() -> List[str]:
    """ARCHIVE.json for registered study folders that were copied in by hand (T0.10's, T0.13's …),
    so every folder can be checked the same way: which files, their sizes and sha256."""
    reg = load()
    done: List[str] = []
    for run_id, r in reg.get("runs", {}).items():
        if r["group"] == "logs":
            continue
        d = find_run(run_id, reg)
        if d is None or (d / "ARCHIVE.json").exists():
            continue
        files = [{"path": str(p.relative_to(d)), "bytes": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in _files(d)]
        (d / "ARCHIVE.json").write_text(json.dumps({
            "run_id": run_id, "kind": "study", "study": r["role"], "run_status": "files",
            "archived_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "archived_by": "campaign.py adopt (the folder was copied by hand)",
            "trials": 0, "outcomes": {}, "files": files, "bytes": sum(f["bytes"] for f in files)}, indent=2) + "\n")
        done.append(run_id)
    return done


# ---------------------------------------------------------------------------------------------
# indexes and reports
# ---------------------------------------------------------------------------------------------

def _record_parts() -> Tuple[List[Tuple[str, str]], List[str], List[str]]:
    """(run-log entries as (heading, body)), change-log rows, instrument-table rows."""
    text = RECORD.read_text() if RECORD.exists() else ""
    runlog = text.split("\n## 7. Run log", 1)[1] if "\n## 7. Run log" in text else ""
    entries: List[Tuple[str, str]] = []
    for chunk in re.split(r"\n(?=### )", runlog):
        if chunk.startswith("### "):
            head, _, body = chunk.partition("\n")
            entries.append((head[4:].strip(), body.strip()))
    change = text.split("\n## 6. Change log", 1)[1].split("\n## 6a.", 1)[0] if "\n## 6. Change log" in text else ""
    rows = [l for l in change.splitlines() if l.startswith("| 20")]
    inst = [l for l in text.splitlines() if re.match(r"^\| T0\.\d+ \|", l)]
    return entries, rows, inst


def _terms(gid: str, reg: dict) -> List[str]:
    terms = [rid for rid, r in reg.get("runs", {}).items() if r["group"] == gid and not rid.startswith("_")]
    terms += [Path(k).name for k, v in reg.get("analysis", {}).items() if v["group"] == gid]
    return terms


def _mentions(text: str, terms: List[str]) -> bool:
    spans = re.findall(r"`([^`]+)`", text)
    return any(t == s or s.startswith(t + "/") or s.startswith(t) and s[len(t):len(t) + 1] in ("/", "") for s in spans for t in terms)


def _rel(p: Path, base: Path) -> str:
    return str(p.relative_to(base)).replace(" ", "%20")


def _run_rows(gid: str, reg: dict, base: Path) -> List[str]:
    rows = ["| run | where | what it is | status | trials | outcomes |", "|---|---|---|---|---:|---|"]
    for rid, r in reg.get("runs", {}).items():
        if r["group"] != gid:
            continue
        d = find_run(rid, reg)
        meta = _archive_meta(d) if d else {}
        out = ", ".join(f"{k} {v}" for k, v in sorted((meta.get("outcomes") or {}).items()))
        where = f"[`{_rel(d, base)}/`]({_rel(d, base)}/)" if d else "not archived yet"
        rows.append(f"| `{rid}` | {where} | {r['role']} | {r['status']} | {meta.get('trials', '') if d else ''} | {out} |")
    return rows


def _exhibit_line(d: Path, reg: dict, base: Path) -> str:
    f = json.loads((d / "facts.json").read_text())
    mc = f.get("vs_discopop_alone") or {}
    shows = (reg.get("exhibits", {}).get(d.name) or {}).get("shows", "(not registered)")

    def _x(v: object) -> str:
        return f"{v:.2f}×" if isinstance(v, (int, float)) else "1.00×"
    vs = ("no DiscoPoP-alone trial to pair with" if mc.get("verdict") in (None, "—", "no-baseline")
          else f"**{mc['verdict']}** vs DiscoPoP alone ({_x(mc.get('dp_alone_speedup_vs_seq'))} → "
               f"{_x(mc.get('agent_speedup_vs_seq'))})")
    return (f"- [`{d.name}`]({_rel(d, base)}/) — {shows}  \n  {vs} · {f['benchmark']}, `{f['arm']}`, "
            f"{f['run']} rep {f.get('repeat', 1)} · pictures: `before_after.png`"
            + (", `rejected_attempt.png`" if (d / "rejected_attempt.png").exists() else "") + ", `console.png`")


def write_reports() -> List[Path]:
    reg = load()
    entries, rows, inst = _record_parts()
    written: List[Path] = []
    for g in reg.get("groups", []):
        gid, base = g["id"], group_dir(g["id"], reg)
        if g["kind"] == "logs" or not base.exists():
            continue
        terms = _terms(gid, reg)
        L = [f"# {g['title']}", "",
             "*Generated by `agent/tools/campaign.py reports` from `results/campaign.json` and the experiment "
             "record (`agent/THESIS_EXPERIMENTS.md`). Edit those, then regenerate — not this file.*", "",
             f"**Status:** {g['status']}", "", "## The question", "", g["question"], ""]
        if g.get("headline"):
            L += ["## Result in one paragraph", "", g["headline"], ""]
        an = base / "analysis"
        figs = [p for p in (an / "tsvc" / "fig_verdict_matrix.png", an / "fig_verdict_matrix.png",
                            an / "tsvc" / "fig_vs_discopop_alone.png", an / "fig_vs_discopop_alone.png") if p.exists()]
        if figs:
            L += ["## Figures", ""] + [f"![{p.stem}]({_rel(p, base)})" for p in figs[:2]] + [""]
        L += ["## What is in this folder", ""]
        if an.exists():
            L.append(f"- [`analysis/`](analysis/) — the read-out: " + ", ".join(
                f"[`{_rel(p, an)}`]({_rel(p, base)})" for p in sorted(an.rglob("*.md"))))
        ex = sorted((base / "exhibits").glob("*/facts.json"))
        if ex:
            L.append(f"- [`exhibits/`](exhibits/) — {len(ex)} case studies, below")
        for sec in SECTIONS:
            n = len([p for p in (base / sec).glob("*") if p.is_dir()]) if (base / sec).exists() else 0
            if n:
                L.append(f"- [`{sec}/`]({sec}/) — {n} " + {"runs": "archived run(s): the evidence",
                                                            "checks": "verification(s) made during the read-out",
                                                            "preflight": "smoke run(s) before the launch",
                                                            "superseded": "run(s) a later one replaced"}[sec])
        L += ["", "## Runs", ""] + _run_rows(gid, reg, base) + [""]
        if ex:
            L += ["## Exhibits", ""] + [_exhibit_line(p.parent, reg, base) for p in ex] + [""]
        mine = [(h, b) for h, b in entries if _mentions(h, terms)]
        instrument_rows = [r for r in inst if r.startswith(f"| {gid} |")]
        if instrument_rows:
            L += ["## The instrument, as the record defines it (§5e)", "",
                  "| ID | Question | Tool | How it measures | Output | Status |", "|---|---|---|---|---|---|"] + instrument_rows + [""]
        if mine:
            L += ["## From the experiment record (§7 run log)", ""]
            for h, b in mine:
                L += [f"### {h}", "", b, ""]
        log_rows = [r for r in rows if _mentions(r, terms)]
        if log_rows:
            L += ["## Change-log rows that name these runs (§6)", "", "| Date | Repo | Change | Why |", "|---|---|---|---|"] + log_rows + [""]
        (base / "REPORT.md").write_text("\n".join(L) + "\n")
        written.append(base / "REPORT.md")
    written += write_indexes(reg)
    return written


def write_indexes(reg: Optional[dict] = None) -> List[Path]:
    reg = reg or load()
    L = ["# Every archived run, by experiment", "",
         "*Generated by `agent/tools/campaign.py` from `campaign.json`. Start at [README.md](README.md).*", ""]
    X = ["# Every exhibit, by experiment", "",
         "*Generated by `agent/tools/campaign.py` from `campaign.json` and each exhibit's `facts.json`. Each "
         "exhibit is a folder with `before_after.png` (the change, or what the agent did instead when it shipped "
         "nothing), `diff.tex`, `console.png`, `attempts.md` and `facts.json`; where the gate caught a wrong rewrite, "
         "also `rejected_attempt.png`.*", ""]
    for g in reg.get("groups", []):
        base = group_dir(g["id"], reg)
        L += [f"## [{g['title']}]({_rel(base, RESULTS)}/" + ("REPORT.md" if (base / "REPORT.md").exists() else "") + ")",
              "", f"Status: {g['status']}", ""] + _run_rows(g["id"], reg, RESULTS) + [""]
        ex = sorted((base / "exhibits").glob("*/facts.json")) if base.exists() else []
        if ex:
            X += [f"## [{g['title']}]({_rel(base, RESULTS)}/REPORT.md)", ""] + [_exhibit_line(p.parent, reg, RESULTS) for p in ex] + [""]
    (RESULTS / "INDEX.md").write_text("\n".join(L) + "\n")
    (RESULTS / "EXHIBITS.md").write_text("\n".join(X) + "\n")
    return [RESULTS / "INDEX.md", RESULTS / "EXHIBITS.md"]


# ---------------------------------------------------------------------------------------------
# the check: the definition of done, as a program
# ---------------------------------------------------------------------------------------------

def check() -> List[str]:
    reg = load()
    P: List[str] = []
    groups = _groups(reg)
    record = RECORD.read_text() if RECORD.exists() else ""
    # 1. every folder under results/ is accounted for
    known = {group_dir(g, reg) for g in groups} | {RESULTS / "T0_instruments"}
    for p in sorted(RESULTS.iterdir()):
        if p.is_dir() and p not in known and p.name not in ("_unregistered",):
            P.append(f"results/{p.name}/ is not in the layout (register it in campaign.json, then `campaign.py migrate --apply`)")
    for p in (RESULTS / "_unregistered").glob("*") if (RESULTS / "_unregistered").exists() else []:
        P.append(f"run {p.name} was archived without being registered (results/_unregistered/)")
    # 2. every registered run: archived where it belongs, complete, and in the record
    for rid, r in reg.get("runs", {}).items():
        if r["group"] not in groups:
            P.append(f"run {rid}: unknown group {r['group']}")
            continue
        if r["group"] == "logs":
            continue
        d = find_run(rid, reg)
        if d is None:
            # registered before launch (RUNBOOK) or running: not archived YET is not a problem
            if r["status"] not in ("running", "registered"):
                P.append(f"run {rid}: not archived (status {r['status']})")
            continue
        if d != run_home(rid, reg):
            P.append(f"run {rid}: at {d.relative_to(RESULTS)}, belongs at {run_home(rid, reg).relative_to(RESULTS)} (`campaign.py migrate --apply`)")
        meta = _archive_meta(d)
        if not meta:
            P.append(f"run {rid}: no ARCHIVE.json (`campaign.py adopt`)")
        else:
            listed = {f["path"] for f in meta.get("files", [])}
            on_disk = {str(p.relative_to(d)) for p in _files(d)}
            if listed and on_disk - listed - {"overview.md"}:
                extra = sorted(on_disk - listed)[:3]
                P.append(f"run {rid}: {len(on_disk - listed)} file(s) not in its ARCHIVE.json, e.g. {extra}")
            if listed - on_disk:
                P.append(f"run {rid}: {len(listed - on_disk)} archived file(s) missing on disk, e.g. {sorted(listed - on_disk)[:3]}")
        if f"`{rid}" not in record and rid not in record:
            P.append(f"run {rid}: never named in THESIS_EXPERIMENTS.md")
    # 3. every finished experiment has its report; a comparison has its read-out
    for gid, g in groups.items():
        base = group_dir(gid, reg)
        if g["kind"] == "logs" or g["status"] in ("running", "pre-flight"):
            continue
        if not (base / "REPORT.md").exists():
            P.append(f"{gid}: no REPORT.md (`campaign.py reports`)")
        if g["kind"] == "experiment" and g["status"] == "done":
            for need in ("analysis/main_comparison_stats.md", "analysis/fig_vs_discopop_alone.png", "analysis/vs_discopop_alone.md"):
                if gid == "E10" and need.endswith("main_comparison_stats.md"):
                    continue                        # E10 predates the statistics tool (recorded)
                if not (base / need).exists():
                    P.append(f"{gid}: missing {need}")
    # 4. every exhibit is registered, current, and points at an archived trial
    for d in exhibit_dirs():
        spec = reg.get("exhibits", {}).get(d.name)
        if not spec:
            P.append(f"exhibit {d.name}: not registered (add it with the claim it supports)")
        elif d.parent.parent != group_dir(spec["group"], reg):
            P.append(f"exhibit {d.name}: in {d.parent.parent.name}, registered under {spec['group']}")
        f = json.loads((d / "facts.json").read_text())
        if "vs_discopop_alone" not in f:
            P.append(f"exhibit {d.name}: built before the main comparison was recorded (`thesis_material.py --rebuild`)")
        if not (trial_path(f["run"], f["trial"], reg) / "trial.json").exists():
            P.append(f"exhibit {d.name}: its trial {f['trial']} is not in the archive")
    for name in reg.get("exhibits", {}):
        if not any(d.name == name for d in exhibit_dirs()):
            P.append(f"exhibit {name}: registered but not built")
    # 5. nothing under results/ left uncommitted
    st = subprocess.run(["git", "status", "--porcelain", "--", str(RESULTS)], capture_output=True, text=True, cwd=AGENT_DIR)
    dirty = [l for l in st.stdout.splitlines() if l.strip()]
    if dirty:
        P.append(f"{len(dirty)} uncommitted change(s) under results/, e.g. {dirty[:2]}")
    # 6. fetched but not archived: a working copy in runs/ whose archive is missing
    runs_dir = AGENT_DIR / "runs"
    for p in sorted(runs_dir.iterdir()) if runs_dir.exists() else []:
        if p.is_dir() and not p.name.startswith("_") and any(p.iterdir()):
            r = reg.get("runs", {}).get(p.name)
            if r is None:
                P.append(f"runs/{p.name}: a fetched run that is not registered")
            elif r["status"] != "running" and find_run(p.name, reg) is None:
                P.append(f"runs/{p.name}: fetched but never archived (`agent/benchmark archive {p.name}`)")
    return P


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("reports")
    sub.add_parser("adopt")
    m = sub.add_parser("migrate")
    m.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        problems = check()
        for msg in problems:
            print(f"  ✗ {msg}")
        print(f"{'NOT DONE' if problems else 'OK'} — {len(problems)} problem(s)")
        return 1 if problems else 0
    if a.cmd == "reports":
        for p in write_reports():
            print(f"wrote {p.relative_to(AGENT_DIR)}")
        return 0
    if a.cmd == "adopt":
        print("\n".join(f"ARCHIVE.json for {r}" for r in adopt()) or "nothing to adopt")
        return 0
    moves = migrate(a.apply)
    print("\n".join(moves) or "nothing to move")
    print(f"{len(moves)} move(s)" + ("" if a.apply else " (dry run: --apply to perform)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
