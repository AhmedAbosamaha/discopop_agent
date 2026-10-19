#!/usr/bin/env python3
"""The thesis's figures for the fast refresh (Fig. 10, section 7.7.2) and restructuring depth (Fig. 11, section 7.8),
drawn from the saved read-outs only — nothing is recomputed from the trials here, so a figure says what the registered
read-out says.

    venv/bin/python evaluation/agent/tools/fig_e4_e8.py

Fig. 11 → results/E08_restructuring_depth/analysis/fig_depth_gain_cost.{pdf,png}, from analysis/e8_readout.json (the
          trials), analysis/by_hand/forms_depth_set.md (the form `s257` reached, read by hand) and
          preflight/depth_from_the_archive.json (what a second round would have been asked about, from the saved trials
          of the pragma experiment)
Fig. 10 → results/E04_fast_refresh/analysis/fig_refresh_decisions.{pdf,png}, from analysis/e4_replay_readout.md
          (step 1, its table 2), analysis/e4_report_readout.md (step 2, its tables 1 and 2) and, once it exists,
          analysis/e4live_readout.json (step 4, the live trials)
The captions go to each folder's figures_e4_e8.md.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import campaign  # noqa: E402
from figures import AXIS, CRITICAL, GOOD, GRID, INK_2, MUTED, SERIES, SURFACE, _plt, _save  # noqa: E402

E8 = campaign.RESULTS / "E08_restructuring_depth"
E4 = campaign.RESULTS / "E04_fast_refresh"
DEPTHS = ("default_v5", "depth1_v5", "depth2_v5")
AMBER = "#eda100"            # the outcome palette's "changed" hue (figures.OUTCOME_ORDER)


def md_table(path: Path, header_start: str) -> List[List[str]]:
    """The body rows of the first Markdown table whose header line starts with `header_start`."""
    lines = path.read_text().splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(header_start):
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                rows.append([c.strip().strip("*") for c in row.strip("|").split("|")])
            return rows
    raise SystemExit(f"{path}: no table starting with {header_start!r}")


def _bar_labels(ax: Any, bars: Any, texts: Sequence[str], dy: float) -> None:
    for b, t in zip(bars, texts):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + dy, t, ha="center", va="bottom", fontsize=7.5,
                color=INK_2)


def fig_depth() -> List[Path]:
    plt = _plt()
    r = json.loads((E8 / "analysis" / "e8_readout.json").read_text())
    arch = json.loads((E8 / "preflight" / "depth_from_the_archive.json").read_text())
    forms = (E8 / "analysis" / "by_hand" / "forms_depth_set.md").read_text()
    m = re.search(r"The final form: (\d+) of 5 at depth 0, (\d+) of 5 at depth 1, (\d+) of 5 at depth 2", forms)
    final = [int(x) for x in m.groups()] if m else None
    set_loops = ("tsvc_c5/s2251", "tsvc_c5/s221", "tsvc_c5/s257")
    loops18 = sorted({k.split("|")[0] for k in r["loop_cells"]})
    fig, axs = plt.subplots(2, 3, figsize=(10.0, 5.6))
    labels = ["no extra round", "one", "two"]
    # (a) the depth set
    ax = axs[0][0]
    w = 0.26
    for j, arm in enumerate(DEPTHS):
        ys = [r["set_cells"][f"{lp}|{arm}"]["faster_race_free"] for lp in set_loops]
        bars = ax.bar([i + (j - 1) * w for i in range(3)], ys, width=w, color=SERIES[j], label=labels[j])
        _bar_labels(ax, bars, [str(y) for y in ys], 0.08)
    ax.set_xticks(range(3), [lp.split("/")[1] for lp in set_loops])
    ax.set_ylim(0, 6.2)
    ax.set_yticks(range(0, 6))
    ax.set_ylabel("race-free faster, of 5 trials")
    ax.set_title("(a) the three loops built for depth", loc="left")
    if final:
        ax.text(2, 5.75, f"outer loop parallel: {final[0]} · {final[1]} · {final[2]}", ha="center", fontsize=7.5,
                color=INK_2)
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 0.93))   # above s221, which has no bars
    # the 18 loops, pooled per depth
    pooled: Dict[str, Dict[str, Any]] = {}
    for arm in DEPTHS:
        cs = [r["loop_cells"][f"{lp}|{arm}"] for lp in loops18]
        pooled[arm] = {"f": sum(c["faster_race_free"] for c in cs), "n": sum(c["n"] for c in cs),
                       "u": sum(c["unusable"] for c in cs),
                       "calls": statistics.median(x for c in cs for x in c["calls"]),
                       "min": statistics.median(x for c in cs for x in c["agent_s"]) / 60}
    xs = range(3)
    ax = axs[0][1]
    bars = ax.bar(xs, [100 * pooled[a]["f"] / pooled[a]["n"] for a in DEPTHS], color=SERIES, width=0.6)
    _bar_labels(ax, bars, [f"{pooled[a]['f']} of {pooled[a]['n']}" for a in DEPTHS], 1.5)
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 100)
    ax.set_ylabel("race-free faster, % of trials")
    ax.set_title("(b) the 18 loops", loc="left")
    ax = axs[0][2]
    bars = ax.bar(xs, [pooled[a]["u"] for a in DEPTHS], color=CRITICAL, width=0.6)
    _bar_labels(ax, bars, [str(pooled[a]["u"]) for a in DEPTHS], 0.05)
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 3)
    ax.set_yticks(range(0, 4))
    ax.set_ylabel("wrong programs shipped")
    ax.set_title("(c) the 18 loops: unusable programs", loc="left")
    ax = axs[1][0]
    bars = ax.bar(xs, [pooled[a]["calls"] for a in DEPTHS], color=SERIES, width=0.6)
    _bar_labels(ax, bars, [f"{pooled[a]['calls']:g}" for a in DEPTHS], 0.1)
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 6)
    ax.set_ylabel("model calls per trial (median)")
    ax.set_title("(d) the 18 loops: model calls", loc="left")
    ax = axs[1][1]
    bars = ax.bar(xs, [pooled[a]["min"] for a in DEPTHS], color=SERIES, width=0.6)
    _bar_labels(ax, bars, [f"{pooled[a]['min']:.1f}" for a in DEPTHS], 0.2)
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 14)
    ax.set_ylabel("agent minutes per trial (median)")
    ax.set_title("(e) the 18 loops: agent time", loc="left")
    # (f) what a second round would have been asked about, from the saved trials (no extra round ran there)
    ax = axs[1][2]
    keys = [("DiscoPoP writes", "the pragma experiment, the 18 loops — the corrected table | DiscoPoP writes"),
            ("the model writes", "the pragma experiment, the 18 loops — the corrected table | the model writes")]
    for j, (name, key) in enumerate(keys):
        a = arch[key]
        vals = [a["accepted"], a["ask"], a["other"]]
        bars = ax.bar([i + (j - 0.5) * 0.36 for i in range(3)], vals, width=0.36, color=[SERIES[0], SERIES[1]][j],
                      label=name)
        _bar_labels(ax, bars, [str(v) for v in vals], 1.0)
    ax.set_xticks(range(3), ["a kept\nrewrite", "a second round\nwould ask", "about a\nnew loop"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("trials of 90")
    ax.set_title("(f) saved trials: what a second round meets", loc="left")
    ax.legend(fontsize=7.5, loc="upper right")
    for row in axs:
        for ax in row:
            ax.yaxis.grid(True, color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
    fig.tight_layout(h_pad=2.2, w_pad=1.6)
    paths = _save(fig, E8 / "analysis", "fig_depth_gain_cost")
    plt.close(fig)
    cap = ("**Fig. 11 — gain and cost per restructuring depth** (E8, read out 15 Oct 2026; `fig_depth_gain_cost`). "
           "(a) The three loops whose expert version needs two dependent rewrites: trials of 5 that ended race-free and "
           "verified faster with no extra round of restructuring, one and two; above `s257`, the trials whose shipped "
           "program reached the final form (the outer loop parallel), read by hand. (b)–(e) The 18 loops: depth 0 is the "
           f"pragma experiment's cells (E3, {pooled['default_v5']['n']} trials), depth 1 and 2 are E8's "
           f"({pooled['depth1_v5']['n']} each); race-free faster, wrong programs shipped, model calls and agent minutes "
           "per trial (medians). (f) From the saved trials of the pragma experiment (no extra round ran there): trials "
           "with a kept rewrite, those in which a second round would have asked the model again, and those in which it "
           "would have met a loop the first round had not been asked about — per setup.")
    (E8 / "analysis" / "figures_e4_e8.md").write_text(cap + "\n")
    return paths


def fig_refresh() -> List[Path]:
    plt = _plt()
    rows = md_table(E4 / "analysis" / "e4_replay_readout.md", "| rewrites of | judged | reverted after both")
    names = {"the pragma experiment, the 18 loops": "the 18 loops (E3)",
             "the pragma experiment, the recurrence loops": "4 recurrences (E3)",
             "the contrast set": "the contrast set (E3b)", "the main comparison, the 18 loops": "the 18 loops (E1-v6)"}
    sets = []
    for row in rows:
        if row[0] in names:
            judged, rev, same, other, only_full, only_fast = (int(x) for x in row[1:7])
            sets.append((names[row[0]], judged, rev + same, other, only_full, only_fast))
    total = rows[[r[0] for r in rows].index("all")]
    live_path = E4 / "analysis" / "e4live_readout.json"
    live: Optional[Dict[str, Any]] = json.loads(live_path.read_text()) if live_path.exists() else None
    ncol = 3 if live else 2
    fig, axs = plt.subplots(1, ncol, figsize=(4.2 * ncol, 3.3), gridspec_kw={"width_ratios": [1.5, 1] + ([1] if live else [])})
    ax = axs[0]
    segs = [("the same decision", AXIS), ("kept, other pragmas", AMBER), ("a win lost: kept only after the full "
            "re-profile", CRITICAL), ("kept only after the fast refresh", SERIES[0])]
    labels = [s[0] for s in sets] + ["control: two full\nre-profiles, all"]
    data = [list(s[2:]) for s in sets] + [[int(total[1]), 0, 0, 0]]
    for yi, vals in enumerate(data):
        left = 0
        for (name, color), v in zip(segs, vals):
            if v:
                ax.barh(yi, v, left=left, height=0.55, color=color, edgecolor=SURFACE, linewidth=1.5)
                left += v
        ax.text(left + 4, yi, f"{sum(vals)}", va="center", fontsize=7.5, color=INK_2)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("saved rewrites")
    ax.set_title("(a) step 1: the agent's decision after a fast refresh", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c) for _, c in segs]
    ax.legend(handles, [n for n, _ in segs], fontsize=7, loc="center right",   # beside the three middle rows,
              bbox_to_anchor=(1.0, 0.5))                                     # which end below 200
    ax.set_xlim(0, 1.12 * int(total[1]))
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    # (b) step 2: the model's report on the rewrites drawn
    r1 = md_table(E4 / "analysis" / "e4_report_readout.md", "| after the fast refresh alone (F against P) | rewrites | repaired")
    r2 = md_table(E4 / "analysis" / "e4_report_readout.md", "| after the fast refresh alone (F equals P) | rewrites | intact")
    a1 = r1[[r[0] for r in r1].index("all")]
    a2 = r2[[r[0] for r in r2].index("all")]
    ax = axs[1]
    pairs = [("58 that differed", [(int(a1[2]), GOOD, "repaired"), (int(a1[1]) - int(a1[2]), AMBER, "still differ")]),
             ("58 of the 541\nthat agreed", [(int(a2[2]), AXIS, "intact"), (int(a2[1]) - int(a2[2]), CRITICAL, "broken")])]
    for yi, (lab, parts) in enumerate(pairs):
        left = 0
        for v, color, word in parts:
            ax.barh(yi, v, left=left, height=0.5, color=color, edgecolor=SURFACE, linewidth=1.5)
            if v >= 15:
                ax.text(left + v / 2, yi, f"{word} {v}", ha="center", va="center", fontsize=7.5,
                        color="white" if color in (CRITICAL, GOOD) else INK_2)
            else:                                  # too narrow to hold its label: write it after the bar
                ax.text(left + v + 1, yi, f"{word} {v}", ha="left", va="center", fontsize=7.5, color=INK_2)
            left += v
    ax.set_yticks(range(2), [p[0] for p in pairs])
    ax.set_xlim(0, 75)
    ax.invert_yaxis()
    ax.set_xlabel("rewrites")
    ax.set_title("(b) step 2: with the model's report", loc="left")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if live:
        ax = axs[2]
        titles = list(live["sets"].keys())
        for yi, t in enumerate(titles):
            c = live["sets"][t]
            for j, (k, color) in enumerate((("full", MUTED), ("fast", SERIES[0]))):
                v, n = c[k]["faster_race_free"], c[k]["n"]
                ax.barh(yi + (j - 0.5) * 0.36, 100 * v / n if n else 0, height=0.34, color=color,
                        label=("full re-profile (E3/E3b)" if k == "full" else "fast refresh + report") if yi == 0 else None)
                ax.text((100 * v / n if n else 0) + 1.5, yi + (j - 0.5) * 0.36, f"{v} of {n}", va="center", fontsize=7.5,
                        color=INK_2)
        ax.set_yticks(range(len(titles)), ["the 18 loops" if "18" in t else "the contrast set\nand control" for t in titles])
        ax.invert_yaxis()
        ax.set_xlim(0, 115)
        ax.set_xlabel("race-free faster, % of trials")
        ax.set_title("(c) step 4: whole trials", loc="left")
        ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2,   # under the axis: inside,
                  frameon=False)                                                  # it covered a bar
    fig.tight_layout(w_pad=2.0)
    paths = _save(fig, E4 / "analysis", "fig_refresh_decisions")
    plt.close(fig)
    cap = ("**Fig. 10 — decisions under the fast refresh against the full re-profile** (E4; `fig_refresh_decisions`). "
           f"(a) Step 1, no model: each of the {total[1]} saved pragma-free rewrites of the main comparison (E1-v6), the "
           "pragma experiment (E3) and the contrast set (E3b) judged by the agent's own functions after a fast refresh "
           "and after a full re-profile; the bottom bar is the control, a second full re-profile against the first. "
           "(b) Step 2: the model asked for the dependences of its new lines on the 58 rewrites whose decision differs "
           "and on 58 drawn from the 541 that agree; repaired and still differing, intact and broken, against the full "
           "re-profile."
           + (" (c) Step 4: whole trials of the agent with the fast refresh and the model's report beside the cells of "
              "the same agent with the full re-profile (E3, E3b)." if live else ""))
    (E4 / "analysis" / "figures_e4_e8.md").write_text(cap + "\n")
    return paths


def main() -> int:
    for p in fig_depth() + fig_refresh():
        print(p.relative_to(campaign.RESULTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
