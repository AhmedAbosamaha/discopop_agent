"""Every archived trial in which Settle dropped an orphan rewrite and something
else then failed to apply ("depended on a change that was dropped"): for each
orphan, was it BUILT ON by a later accepted rewrite?

  reshaped  — a later accepted rewrite changed a region the orphan exposed (one of
              its exposed regions' text is in the file before that rewrite and
              gone after it);
  needs     — a later accepted rewrite does not apply (exact, as Settle replays)
              without the orphan.

No model, no gate: the original file, the archived candidate patches and the
spans the log names.  Usage: venv/bin/python settle_archive.py RESULTS_DIR
"""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.environ.get("DISCOPOP_AGENT_REPO", os.getcwd()))   # run from the repo root
from discopop_agent.gate.patching import fix_hunk_headers, run_patch  # noqa: E402

BLOCK = re.compile(r"^┌─ \[depth=(\d+)\] \S+ (\S+) \(lines (\d+)–(\d+)\)")
FINDS = re.compile(r"(\w+) @ lines (\d+)–(\d+)")


def body(text: str, a: int, b: int) -> str:
    lines = text.splitlines()[a - 1:b]
    return "\n".join(ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("//"))


def norm(text: str) -> str:
    return "\n".join(ln.strip() for ln in text.splitlines()
                     if ln.strip() and not ln.strip().startswith("//"))


def present(b: str, text: str) -> bool:
    if not b:
        return False
    hay = "\n" + norm(text) + "\n"
    return ("\n" + b + "\n") in hay


def apply(text: str, diff: str, name: str) -> "str | None":
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / name
        f.write_text(text)
        pf = Path(tmp) / "x.patch"
        pf.write_text(fix_hunk_headers(diff) + "\n")
        ok, _ = run_patch(f, pf, exact=True)
        return f.read_text() if ok else None


def accepted_rewrites(log: str):
    """[(rid, depth, [spans exposed])] for every Phase-A block that ended ACCEPTED."""
    out = []
    cur = None
    for ln in log.splitlines():
        m = BLOCK.match(ln)
        if m:
            cur = {"rid": m.group(2), "depth": int(m.group(1)), "finds": []}
            continue
        if cur is None:
            continue
        if "DiscoPoP now finds:" in ln:
            cur["finds"] = [(int(a), int(b)) for _t, a, b in FINDS.findall(ln)]
        if ln.startswith("└─ ACCEPTED"):
            out.append(cur)
            cur = None
        elif ln.startswith("└─") and not ln.startswith("└─ retry"):
            cur = None
    return out


def analyse(rep: Path):
    log = (rep / "agent.log").read_text(errors="replace")
    settle = log.split("SETTLING", 1)[1]
    notes = re.findall(r"^\s+· (.*)$", settle, re.M)
    orphan_notes = [n for n in notes if "none kept a pragma" in n]
    rws = accepted_rewrites(log)
    cands = [json.loads(l) for l in (rep / "agent_patches" / "candidates.jsonl").read_text().splitlines() if l.strip()]
    # the accepted patch of each block: the last passed Phase-A candidate for (rid, depth)
    for r in rws:
        hits = [c for c in cands if c.get("phase") == "A" and c.get("passed")
                and c.get("region_id") == r["rid"] and c.get("depth") == r["depth"]]
        r["patch"] = (rep / "agent_patches" / hits[-1]["patch"]).read_text() if hits else None
    src_name = None
    for r in rws:
        if r["patch"]:
            m = re.search(r"^--- (\S+)", r["patch"], re.M)
            src_name = Path(m.group(1)).name
            break
    orig_file = rep / "original" / src_name
    if not orig_file.exists():
        orig_file = rep / "agent_patches" / f"{src_name}.original"
    if not orig_file.exists():
        return {"rep": str(rep), "error": "no original file archived"}
    original = orig_file.read_text()
    texts = [original]
    for r in rws:
        t = apply(texts[-1], r["patch"], src_name)
        if t is None:
            return {"rep": str(rep), "error": f"rewrite {r['rid']}@{r['depth']} does not re-apply"}
        texts.append(t)
    # which accepted rewrites are the orphans (by region id and exposed count, in order)
    orphan_idx = []
    for n in orphan_notes:
        m = re.match(r"rewrite of (\S+) — exposed (\d+) region", n)
        rid, k = m.group(1), int(m.group(2))
        cand = [i for i, r in enumerate(rws) if r["rid"] == rid and i not in orphan_idx]
        orphan_idx.append(cand[0] if len(cand) == 1 else
                          next((i for i in cand if len(rws[i]["finds"]) == k), cand[0]))
    res = []
    for i in orphan_idx:
        bodies = [body(texts[i + 1], a, b) for a, b in rws[i]["finds"]]
        built = []
        for j in range(i + 1, len(rws)):
            reshaped = any(present(b, texts[j]) and not present(b, texts[j + 1]) for b in bodies)
            # replay without the orphan: everything accepted before j except i, then j
            t = original
            ok = True
            for k in range(j):
                if k == i:
                    continue
                t2 = apply(t, rws[k]["patch"], src_name)
                if t2 is None:
                    ok = False
                    break
                t = t2
            needs = (not ok) or apply(t, rws[j]["patch"], src_name) is None
            built.append({"later": f"{rws[j]['rid']}@{rws[j]['depth']}", "reshaped": reshaped, "needs": needs})
        res.append({"orphan": f"{rws[i]['rid']}@{rws[i]['depth']}", "exposed": rws[i]["finds"], "later": built})
    kinds = {"rewrite": sum(1 for n in notes if n.startswith("rewrite for") and "depended" in n),
             "pragma": sum(1 for n in notes if n.startswith("pragma for") and "depended" in n)}
    return {"rep": str(rep), "cascade": kinds, "orphans": res}


def main():
    root = Path(sys.argv[1])
    rows = []
    for dirpath, _dirs, files in os.walk(root):
        if "agent.log" not in files:
            continue
        rep = Path(dirpath)
        log = (rep / "agent.log").read_text(errors="replace")
        if "SETTLING" not in log:
            continue
        notes = re.findall(r"^\s+· (.*)$", log.split("SETTLING", 1)[1], re.M)
        if any("none kept a pragma" in n for n in notes) and any("depended on" in n for n in notes):
            rows.append(analyse(rep))
    for r in rows:
        print(json.dumps(r))
    # tally
    t = {"trials": len(rows), "errors": 0, "reshaped_any": 0, "needs_any": 0, "either": 0, "neither": 0}
    for r in rows:
        if "error" in r:
            t["errors"] += 1
            continue
        rs = any(l["reshaped"] for o in r["orphans"] for l in o["later"])
        nd = any(l["needs"] for o in r["orphans"] for l in o["later"])
        t["reshaped_any"] += rs
        t["needs_any"] += nd
        t["either"] += (rs or nd)
        t["neither"] += not (rs or nd)
    print("TALLY", json.dumps(t))


if __name__ == "__main__":
    main()
