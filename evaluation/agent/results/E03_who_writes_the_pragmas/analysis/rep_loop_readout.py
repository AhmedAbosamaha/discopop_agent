#!/usr/bin/env python3
"""E3, descriptive read-out: what every final program did to the repetition loop and to the `dummy` call.

E1-v6's instrument (`E01v6_clean_files_three_way/analysis/rep_loop_readout.py`), its `classify` taken over
unchanged, per setup of E3 — and one tag added on 10 Oct 2026, after E3's programs were read:

  work outside    a `for` loop of the kernel function in front of or behind the repetition loop: work the
                  original does in every repetition is done once (`s341`: the positions are computed once and
                  reused by every repetition; `s000`: the loop itself runs once, after the repetitions)

Categories of E1-v6's instrument, from the text of each trial's final benchmark file (comments removed):

  kept            one repetition loop, sequential, one `dummy` call inside it, no parallel region around it
  region around   a `#pragma omp parallel` region opened in front of the repetition loop
  loop parallel   a worksharing directive directly on the repetition loop
  dummy != 1      the call removed or written more than once
  loops != 1      the repetition loop removed or written more than once

    python3 rep_loop_readout.py RUNS_DIR [RUNS_DIR ...] [--md OUT.md]

Run on E3's runs and, for the added tag, on E1-v6's (the agent's programs there are `default_v4`).
"""
import collections
import glob
import json
import re
import sys

args = [a for a in sys.argv[1:]]
md = None
if "--md" in args:
    md = args[args.index("--md") + 1]
    del args[args.index("--md"):args.index("--md") + 2]
bases = args
R = "s112 s121 s1213 s127 s211 s212 s241 s243 s244 s252 s254 s255 s281 s291 s292 s293 s331 s341".split()
A = "s000 vpvtv s313".split()
D = "s321 s322 s323 s3112".split()
cls = {**{n: "R" for n in R}, **{n: "A" for n in A}, **{n: "D" for n in D}}
SETUP = {"default_v5": "E3, DiscoPoP writes the pragma", "llm_pragmas_v5": "E3, the model writes the pragma",
         "default_v4": "E1-v6, the agent"}
REP = r"\bfor\s*\(\s*(int\s+)?nl\b"


def strip(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def classify(src):  # E1-v6's, unchanged
    s = strip(src)
    lines = [l for l in s.splitlines() if l.strip()]
    loops = [i for i, l in enumerate(lines) if re.search(REP, l)]
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
        pos_loop = re.search(REP, s)
        alloc = "before the repetition loop" if (pos_loop and m.start() < pos_loop.start()) else "inside or after it"
    elif re.search(r"\bstatic\s+real_t\s*\*|\bstatic\s+real_t\s+\w+\s*\[", s):
        alloc = "static"
    return (", ".join(tags) or "kept"), alloc


def work_outside(src):
    """`for` loops of the kernel function outside the first repetition loop's body (added 10 Oct 2026)."""
    s = strip(src)
    m = re.search(REP, s)
    if not m:
        return 0
    start = s.find("{", m.end())
    depth, end = 0, len(s)
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    fn = re.search(r"\bkernel_\w+\s*\(", s)
    head = s[fn.start() if fn else 0:m.start()]
    return len(re.findall(r"\bfor\s*\(", head)) + len(re.findall(r"\bfor\s*\(", s[end:]))


tab = collections.defaultdict(collections.Counter)
allocs = collections.defaultdict(collections.Counter)
before = collections.defaultdict(collections.Counter)
cases, hoists = [], []
seen = set()
for base in bases:
    for f in sorted(glob.glob(base + "/*/benchmarks/**/trial.json", recursive=True)):
        t = json.load(open(f))
        if (t.get("llm_call_failures") or 0) > 0 or t["arm"] not in SETUP:
            continue
        k = t["benchmark"].split("/")[-1]
        d = f.rsplit("/", 1)[0]
        try:
            src = open(f"{d}/final/{k}.c", errors="replace").read()
        except OSError:
            continue
        run = f[len(base):].strip("/").split("/")[0]
        cat, alloc = classify(src)
        setup = SETUP[t["arm"]]
        key = (setup, cls[k])
        tab[key][(cat, t.get("outcome"))] += 1
        allocs[key][alloc] += 1
        nb = work_outside(src)
        before[key][("work outside" if nb else "none", t.get("outcome"))] += 1
        rep = f.rsplit("/", 2)[1]
        if cat != "kept":
            cases.append((setup, cls[k], k, run, rep, cat, str(t.get("outcome"))))
        if nb:
            hoists.append((setup, cls[k], k, run, rep, f"{nb} loop(s) outside the repetition loop", str(t.get("outcome"))))

out = []
for key in sorted(tab):
    n = sum(tab[key].values())
    kept = sum(v for (c, _o), v in tab[key].items() if c == "kept")
    out.append(f"{key[0]:32} class {key[1]}: {n:3} programs, repetition loop and `dummy` kept as they are in {kept}"
               + "".join(f"\n      {c} -> {o}: {v}" for (c, o), v in sorted(tab[key].items()) if c != "kept"))
    out.append(f"      temporary memory: {dict(allocs[key])}")
    wb = {o: v for (c, o), v in sorted(before[key].items()) if c == "work outside"}
    out.append(f"      a loop of the kernel outside the repetition loop: {sum(wb.values())}" + (f" {wb}" if wb else ""))
out.append("")
out.append("every program that changed the repetition loop or the `dummy` call:")
out += ["  " + " | ".join(c) for c in cases] or ["  none"]
out.append("")
out.append("every program with a loop of the kernel outside the repetition loop:")
out += ["  " + " | ".join(c) for c in hoists] or ["  none"]
text = "\n".join(out)
print(text)
if md:
    open(md, "w").write("```\n" + text + "\n```\n")
