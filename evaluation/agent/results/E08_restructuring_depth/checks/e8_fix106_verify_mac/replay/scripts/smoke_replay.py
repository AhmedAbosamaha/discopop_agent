"""Replay an archived trial's change log through the agent's Settle, without a model.

The change log is rebuilt from the archive: the rewrites Phase A kept (the accepted patch of every
block that ended ACCEPTED, in order), each with the fingerprints of the regions its log line names
("DiscoPoP now finds: ..."), and the pragmas Phase B applied (in order), each fingerprinted the way
Phase B does it — from the working file at the profile's line numbers, earlier pragmas included.
Region names are not archived; one constant name on both sides leaves the matching to the text,
which is what decides it.  The gate Settle calls on the finished file is stood in (passes), so
what is replayed is Settle's DECISION; the finished file is saved for the harness's own verdict.

    venv/bin/python smoke_replay.py TRIAL_DIR OUT_DIR
Prints the survivors, Settle's notes and whether they equal the archived ones, and writes
OUT_DIR/<source> (the finished file) and OUT_DIR/replay.json.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, os.environ.get("DISCOPOP_AGENT_REPO", os.getcwd()))   # run from the repo root
sys.path.insert(0, str(Path(__file__).parent))
from discopop_agent.phases import settle as settle_mod  # noqa: E402
from discopop_agent.plan.regions import region_fingerprint  # noqa: E402
from settle_archive import accepted_rewrites, apply  # noqa: E402

PATTERN = re.compile(r"^┌─ pattern #\d+\s+\S+ @ lines (\d+)–(\d+)")


def applied_patterns(log: str):
    """[(start, end)] of every Phase-B block that ended APPLIED, in order."""
    out, cur = [], None
    for ln in log.splitlines():
        m = PATTERN.match(ln)
        if m:
            cur = (int(m.group(1)), int(m.group(2)))
            continue
        if cur is not None and ln.startswith("└─"):
            if ln.startswith("└─ APPLIED"):
                out.append(cur)
            cur = None
    return out


def main() -> None:
    trial, out = Path(sys.argv[1]), Path(sys.argv[2])
    log = (trial / "agent.log").read_text(errors="replace")
    cands = [json.loads(l) for l in (trial / "agent_patches" / "candidates.jsonl").read_text().splitlines()
             if l.strip()]
    rws = accepted_rewrites(log)
    for r in rws:
        hits = [c for c in cands if c.get("phase") == "A" and c.get("passed")
                and c.get("region_id") == r["rid"] and c.get("depth") == r["depth"]]
        r["patch"] = (trial / "agent_patches" / hits[-1]["patch"]).read_text()
    name = Path(re.search(r"^--- (\S+)", rws[0]["patch"], re.M).group(1)).name
    out.mkdir(parents=True, exist_ok=True)
    work = out / "work"
    if work.exists():
        shutil.rmtree(work)
    if (trial / "original").is_dir():
        shutil.copytree(trial / "original", work)
    else:                                   # older archives: only the agent's backup of the source
        work.mkdir(parents=True)
        shutil.copy2(trial / "agent_patches" / f"{name}.original", work / name)
    src = work / name
    original = src.read_text()

    log_entries = []
    text = original
    for r in rws:
        text = apply(text, r["patch"], name)
        assert text is not None, f"rewrite {r['rid']}@{r['depth']} does not re-apply"
        src.write_text(text)
        prints = [region_fingerprint(str(src), a, b, "") for a, b in r["finds"]]
        log_entries.append({"kind": "rewrite", "region_id": r["rid"], "diff": r["patch"],
                            "file": str(src.resolve()), "exposed": prints, "self_annotated": False,
                            "pragmas": 0, "_depth": r["depth"]})
    spans = applied_patterns(log)
    brecs = [c for c in cands if c.get("phase") == "B" and c.get("passed") and c.get("stage") == "accepted"]
    assert len(spans) == len(brecs), f"{len(spans)} applied blocks, {len(brecs)} passed B records"
    for (a, b), c in zip(spans, brecs):
        src.write_text(text)
        fp = region_fingerprint(str(src), a, b, "")          # Phase B's fp_before, shift and all
        diff = (trial / "agent_patches" / c["patch"]).read_text()
        text = apply(text, diff, name)
        assert text is not None, f"pragma {c['region_id']} does not re-apply"
        log_entries.append({"kind": "pragma", "region_id": c["region_id"], "diff": diff,
                            "fingerprint": fp, "file": str(src.resolve())})
    src.write_text(text)                                       # the file as Settle finds it

    args = SimpleNamespace(source_file=str(src), noise_floor=0.0, schedule_stress=True,
                           stress_threads=None, require_speedup=False, timing_cflags=())
    settle_mod._check_final_source = lambda *a, **k: (True, "stood in")   # type: ignore[assignment]
    originals = {str(src.resolve()): original}
    survivors, notes = settle_mod._settle(originals, log_entries, args, out, None, None, None, None)  # type: ignore[arg-type]

    archived = re.findall(r"^\s+· (.*)$", log.split("SETTLING", 1)[1], re.M)
    finished = src.read_text()
    (out / name).write_text(finished)
    rec = {
        "trial": str(trial),
        "change_log": [f"{c['kind']} {c['region_id']}" + (f"@{c['_depth']}" if "_depth" in c else "")
                       for c in log_entries],
        "survivors": [f"{c['kind']} {c['region_id']}" + (f"@{c['_depth']}" if "_depth" in c else "")
                      for c in survivors],
        "notes": notes,
        "archived_notes": archived,
        "notes_equal_archived": notes == archived,
        "finished_differs_from_original": finished != original,
        "pragmas_in_finished": finished.count("#pragma omp"),
    }
    (out / "replay.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
