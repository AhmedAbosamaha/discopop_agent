#!/usr/bin/env python3
"""T0.16's read-out over BOTH server draws: a difference between the layouts counts only if both draws show it.
Also: do two draws of ONE layout agree on WAR/WAW when every dependence is read by its own type (D12), where the
reading of versions 1-3 differs?  (The claim that T0.15's "draw noise" was the parser.)

    python t016_two_draws.py <draw a dir> <draw b dir> <profiles a> <profiles b> <out.md>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[6]))
from discopop_agent.evidence.deps import _load_dependencies  # noqa: E402

A, B, PA, PB, OUT = (Path(x) for x in sys.argv[1:6])
CRITERIA = ("candidates", "do_all", "blocker", "repetition", "statement")
names = sorted(p.stem for p in A.glob("*.json"))
rows, kept, one_draw = [], {}, {}
ratios = {}
for n in names:
    a, b = json.loads((A / f"{n}.json").read_text()), json.loads((B / f"{n}.json").read_text())
    ratios[n] = a.get("time_ratio")
    cells = []
    for c in CRITERIA:
        da, db = not a["same"].get(c, False), not b["same"].get(c, False)
        cells.append("DIFF in both" if da and db else "one draw only" if da or db else "same")
        if da and db:
            kept.setdefault(n, []).append(c)
        elif da or db:
            one_draw.setdefault(n, []).append(c)
    out_same = a["output_identical"] and b["output_identical"]
    rows.append([n, "same" if out_same else "DIFF", str(a.get("time_ratio")), *cells])


def deps(profile: Path, name: str, typed: bool):
    """WAR and WAW between lines of the benchmark's file, by line TEXT."""
    src = profile / f"{name}.c"
    lines = src.read_text().splitlines()
    project = (profile / "main.c").exists()
    raw, war, waw = _load_dependencies(profile / ".discopop" / "profiler", 1, len(lines), 1 if project else None, typed)

    def t(k: int) -> str:
        return lines[k - 1].strip() if 1 <= k <= len(lines) else ""
    return {(d.dep_type, t(d.from_line), t(d.to_line), d.variable) for d in war + waw}, \
           {(d.dep_type, t(d.from_line), t(d.to_line), d.variable) for d in raw}


stat = {"untyped differ": 0, "typed differ": 0, "raw differ": 0, "profiles": 0}
typed_diff = []
for n in names:
    for suite in ("tsvc_b1", "tsvc_c1"):
        pa, pb = PA / f"{n}_{suite}", PB / f"{n}_{suite}"
        if not (pa / ".discopop").exists() or not (pb / ".discopop").exists():
            continue
        stat["profiles"] += 1
        ua, ra = deps(pa, n, False)
        ub, rb = deps(pb, n, False)
        ta, _ = deps(pa, n, True)
        tb, _ = deps(pb, n, True)
        stat["untyped differ"] += ua != ub
        stat["raw differ"] += ra != rb
        if ta != tb:
            stat["typed differ"] += 1
            typed_diff.append(f"{n} ({suite}): only a {sorted(ta - tb)[:2]} | only b {sorted(tb - ta)[:2]}")

head = ["loop", "output", "time new/old (LARGE)", *("candidates", "Do-All set", "blocker of the loop under study",
                                                    "repetition loop", "order statement (version 4)")]
table = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
vals = sorted((v, k) for k, v in ratios.items() if v)
text = "\n".join(table) + f"""

{len(rows)} loops, two draws on the server. Output identical in both draws: {sum(1 for r in rows if r[1] == 'same')}.
The same on every criterion in both draws: {len(rows) - len(kept) - len([n for n in one_draw if n not in kept])};
a difference in BOTH draws (kept): {len(kept)} — {'; '.join(f'{k}: {", ".join(v)}' for k, v in kept.items()) or 'none'};
a difference in one draw only (not kept): {'; '.join(f'{k}: {", ".join(v)}' for k, v in one_draw.items() if k not in kept) or 'none'}.
Sequential time new/old at LARGE (draw a): within 0.96-1.04 for {sum(1 for v, _ in vals if 0.96 <= v <= 1.04)} of {len(vals)};
outside: {', '.join(f'{k} {v}' for v, k in vals if not 0.96 <= v <= 1.04)}.

WAR/WAW between two draws of ONE layout ({stat['profiles']} loop-layout pairs): the reading of versions 1-3 differs on
{stat['untyped differ']}; read by each dependence's own type (D12) it differs on {stat['typed differ']}; RAW differs on {stat['raw differ']}.
""" + ("".join(f"  typed difference — {x}\n" for x in typed_diff[:12]))
OUT.write_text(text)
print(text[text.index(f"{len(rows)} loops"):])
