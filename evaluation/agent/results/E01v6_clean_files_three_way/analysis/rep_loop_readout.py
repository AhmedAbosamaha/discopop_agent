#!/usr/bin/env python3
"""E1-v6, secondary read-out (a): what every final program did to the repetition loop and to the `dummy` call.

Read from the text of each trial's final benchmark file (comments removed): how many repetition loops
(`for (… nl …)`) and `dummy(` calls it has, whether a directive stands directly on a repetition loop, whether a
`#pragma omp parallel` region (not `parallel for`) is opened before the first repetition loop, and where the
first heap allocation stands. Categories:

  kept            one repetition loop, sequential, one `dummy` call inside it, no parallel region around it
  region around   a `#pragma omp parallel` region opened in front of the repetition loop
  loop parallel   a worksharing directive directly on the repetition loop
  dummy != 1      the call removed or written more than once
  loops != 1      the repetition loop removed or written more than once

    python3 rep_loop_readout.py RESULTS_DIR/runs [--md OUT.md]
"""
import collections
import glob
import json
import re
import sys

base = sys.argv[1]
md = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else None
R = "s112 s121 s1213 s127 s211 s212 s241 s243 s244 s252 s254 s255 s281 s291 s292 s293 s331 s341".split()
A = "s000 vpvtv s313".split()
D = "s321 s322 s323 s3112".split()
cls = {**{n: "R" for n in R}, **{n: "A" for n in A}, **{n: "D" for n in D}}


def strip(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def classify(src):
    s = strip(src)
    lines = [l for l in s.splitlines() if l.strip()]
    loops = [i for i, l in enumerate(lines) if re.search(r"\bfor\s*\(\s*(int\s+)?nl\b", l)]
    dummies = len(re.findall(r"\bdummy\s*\(", s))
    tags = []
    if len(loops) != 1:
        tags.append(f"loops={len(loops)}")
    if dummies != 1:
        tags.append(f"dummy={dummies}")
    for i in loops:
        j = i - 1
        while j >= 0 and lines[j].strip().startswith("#pragma") is False and lines[j].strip() == "":
            j -= 1
        if j >= 0 and re.match(r"\s*#\s*pragma\s+omp\s+(parallel\s+for|for)\b", lines[j]):
            tags.append("loop parallel")
    if loops:
        before = "\n".join(lines[:loops[0]])
        if re.search(r"#\s*pragma\s+omp\s+parallel\b(?!\s+for)", before):
            tags.append("region around")
    alloc = "none"
    m = re.search(r"\b(malloc|calloc|aligned_alloc|posix_memalign)\s*\(", s)
    if m:
        first_loop = s.find("nl", s.find("for")) if loops else -1
        pos_loop = re.search(r"\bfor\s*\(\s*(int\s+)?nl\b", s)
        alloc = "before the repetition loop" if (pos_loop and m.start() < pos_loop.start()) else "inside or after it"
    elif re.search(r"\bstatic\s+real_t\s*\*|\bstatic\s+real_t\s+\w+\s*\[", s):
        alloc = "static"
    return (", ".join(tags) or "kept"), alloc


tab = collections.defaultdict(collections.Counter)
allocs = collections.defaultdict(collections.Counter)
cases = []
for f in sorted(glob.glob(base + "/*/benchmarks/**/trial.json", recursive=True)):
    t = json.load(open(f))
    if (t.get("llm_call_failures") or 0) > 0 or t["arm"].startswith("discopop_gate"):
        continue
    k = t["benchmark"].split("/")[-1]
    d = f.rsplit("/", 1)[0]
    try:
        src = open(f"{d}/final/{k}.c", errors="replace").read()
    except OSError:
        continue
    cat, alloc = classify(src)
    setup = ("agent (Haiku)" if t["arm"].startswith("default") else t["model"].replace("claude-", "").split("-2025")[0] + " alone")
    tab[(setup, cls[k])][(cat, t.get("outcome"))] += 1
    allocs[(setup, cls[k])][alloc] += 1
    if cat != "kept":
        cases.append((setup, cls[k], k, f.rsplit("/", 2)[1], cat, t.get("outcome")))

out = []
for key in sorted(tab):
    n = sum(tab[key].values())
    kept = sum(v for (c, _o), v in tab[key].items() if c == "kept")
    out.append(f"{key[0]:16} class {key[1]}: {n:3} programs, repetition loop and `dummy` kept as they are in {kept}"
               + "".join(f"\n      {c} -> {o}: {v}" for (c, o), v in sorted(tab[key].items()) if c != "kept"))
    out.append(f"      temporary memory: {dict(allocs[key])}")
out.append("")
out.append("every program that changed them:")
for c in cases:
    out.append("  " + " | ".join(c))
text = "\n".join(out)
print(text)
if md:
    open(md, "w").write("```\n" + text + "\n```\n")
