#!/usr/bin/env python3
"""Read-out of the v4-against-v5 DiscoPoP screen by the PRE-REGISTERED criteria (§6 4 Oct): the agent's candidates
on the benchmark's own code (tier, pattern), the Do-All set, the Do-All blockers (variable, loop), the order
statement's bullets. A difference in the raw dependence list is NOT a failure: T0.15 (26/27 Sep) measured that two
draws of ONE layout differ there on 17 of 33 packages (WAW/WAR of the store line between repetitions).

    python v5_readout.py <dir written by v5_discopop.py> [--md out.md]
"""
import json
import re
import sys
from pathlib import Path

D = Path(sys.argv[1])
MD = Path(sys.argv[sys.argv.index("--md") + 1]) if "--md" in sys.argv else None
MIX = ("a[k] +=", "d[k] +=", "a[0] +=", "long k =", "pb_mix(")


def files_of(work: Path) -> dict:
    out = {}
    f = work / ".discopop" / "FileMapping.txt"
    for raw in f.read_text().splitlines() if f.exists() else []:
        parts = raw.split("\t") if "\t" in raw else raw.split(None, 1)
        if len(parts) == 2:
            out[int(parts[0])] = Path(parts[1].strip())
    return out


def text_at(files: dict, fid: int, line: int) -> str:
    try:
        return files[fid].read_text().splitlines()[line - 1].strip()
    except (KeyError, OSError, IndexError):
        return f"?{fid}:{line}"


def var(name: str) -> str:
    return re.sub(r"^GEPRESULT_", "", str(name))


def view(work: Path, p: dict) -> dict:
    files = files_of(work)
    f = work / ".discopop" / "explorer" / "doall_prevented.json"
    blockers = set()
    for b in json.loads(f.read_text()) if f.exists() else []:
        blockers.add((var(b.get("var_name")), str(b.get("dep_type", "")).split(".")[-1],
                      text_at(files, int(b.get("loop_file") or 0), int(b.get("loop_start") or 0))))
    ks = [c for c in p.get("candidates", []) if "nl < R" not in c["text"]]
    order = set()
    for c in ks:
        order |= {re.sub(r" and \d+ \(", " and N (", l.strip()) for l in c["order"].splitlines() if l.strip().startswith("- ")}

    def mine(t: str) -> bool:
        return bool(t) and "nl < R" not in t and not t.startswith(MIX)
    return {"candidates": sorted((c["type"], c["text"].replace("static ", ""), c["tier"], str(c["pattern"])) for c in ks),
            "do_all": sorted(d["text"] for d in p.get("do_all", [])),
            "blockers": sorted(b for b in blockers if "nl < R" not in b[2]),
            "repetition": "blocked" if any("nl < R" in b[2] for b in blockers) else "not blocked",
            "order": sorted(order),
            "first": [c["text"] for c in p.get("candidates", [])][:1],
            "raw": sorted({(d[1], d[2], d[3]) for c in ks for d in c["deps"] if d[0] == "RAW" and mine(d[1]) and mine(d[2])}),
            "other": sorted({(d[0], d[1], d[2], d[3]) for c in ks for d in c["deps"] if d[0] != "RAW" and mine(d[1]) and mine(d[2])})}


rows, fails, redraw = [], [], []
for j in sorted(D.glob("*.json")):
    n = j.stem
    d = json.loads(j.read_text())
    if "error" in d["v4"] or "error" in d["v5"]:
        rows.append((n, "PROFILE ERROR", "", "", "", "", "", ""))
        fails.append(n)
        continue
    a, b = view(D / "work" / f"{n}_v4", d["v4"]), view(D / "work" / f"{n}_v5", d["v5"])
    keys = ("candidates", "do_all", "blockers", "repetition", "order")
    same = {k: a[k] == b[k] for k in keys}
    raw_same, other_same = a["raw"] == b["raw"], a["other"] == b["other"]
    if not all(same.values()):
        fails.append(n)
    elif not (raw_same and other_same):
        redraw.append(n)
    rows.append((n, *("same" if same[k] else "DIFF" for k in keys), "same" if raw_same else "differ",
                 "same" if other_same else "differ"))
    for k in keys:
        if not same[k]:
            print(f"  {n} {k}:\n     v4 {a[k]}\n     v5 {b[k]}")
    if not raw_same:
        print(f"  {n} RAW records: only v4 {[x for x in a['raw'] if x not in b['raw']]} | only v5 {[x for x in b['raw'] if x not in a['raw']]}")
head = ("| loop | candidates (tier, pattern) | Do-All set | blocker of the loop under study (variable, kind) | "
        "repetition loop blocked | order statement | RAW records in the loop | WAR/WAW records |")
lines = [head, "|---|---|---|---|---|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in rows]
print("\n".join(lines))
summary = (f"\n{len(rows)} loops: {len(rows) - len(fails)} pass the criteria; "
           f"{len(fails)} differ ({', '.join(fails) or '—'}); of the passing, {len(redraw)} differ in the raw "
           f"dependence records ({', '.join(redraw) or '—'}) — a second draw decides, not a failure.")
print(summary)
if MD:
    MD.write_text("\n".join(lines) + "\n" + summary + "\n")
