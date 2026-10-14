#!/usr/bin/env python3
"""The page of the depth experiment (E8) for the author: what the saved trials already answer, what depth as built
would blur, the options, and the decision he deferred on 10 Oct — who writes the pragmas in the experiments that
remain. Built 13 Oct 2026. Every number is read from a saved read-out:

    results/E08_restructuring_depth/preflight/depth_from_the_archive.json   (and .md for the example loop)
    results/E03_who_writes_the_pragmas/analysis/corrected/e3_tests.json
    results/E03b_contrast_set/analysis/corrected/e3b_tests.json

    venv/bin/python evaluation/agent/docs/depth_design_page.py OUT.html        (from the repository root)
"""
import html
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
RES = Path("evaluation/agent/results")
J = json.loads((RES / "E08_restructuring_depth/preflight/depth_from_the_archive.json").read_text())
MD = (RES / "E08_restructuring_depth/preflight/depth_from_the_archive.md").read_text()
T3 = json.loads((RES / "E03_who_writes_the_pragmas/analysis/corrected/e3_tests.json").read_text())
T3B = json.loads((RES / "E03b_contrast_set/analysis/corrected/e3b_tests.json").read_text())

A = "the pragma experiment, the 18 loops — the corrected table"
A0 = "the pragma experiment, the 18 loops — as first run"
B = "the contrast set, the six loops under test — the corrected table"
dp, mo = J[f"{A} | DiscoPoP writes"], J[f"{A} | the model writes"]
dp0, mo0 = J[f"{A0} | DiscoPoP writes"], J[f"{A0} | the model writes"]
cdp, cmo = J[f"{B} | DiscoPoP writes"], J[f"{B} | the model writes"]

# the two experiments on who writes the pragma, corrected tables
m18, d18 = T3["h6"]["model"][0], T3["h6"]["discopop"][0]            # [race-free FASTER, trials]
p18 = T3["h6"]["cmh"]["p_one_sided_corrected"]
m6, d6 = T3B["e3b_1"]["model"][0], T3B["e3b_1"]["discopop"][0]
assert T3["h6"]["model"][1] == T3["h6"]["discopop"][1] == 90 and T3B["e3b_1"]["model"][1] == T3B["e3b_1"]["discopop"][1] == 30
p6 = T3B["e3b_1"]["exact"]["p_greater"]
un = (T3["unusable"]["discopop_writes"], T3["unusable"]["model_writes"], T3B["unusable"]["discopop_writes"], T3B["unusable"]["model_writes"])
assert (m18, d18, m6, d6) == (mo["faster"], dp["faster"], cmo["faster"], cdp["faster"]), (m18, d18, m6, d6)
assert all(u["unusable"] == 0 for u in un)

# cost estimates for the options, from measured cost only (where DiscoPoP writes, the 18 loops)
per_call = dp["cost"] / dp["calls"]
per_trial = dp["cost"] / dp["trials"]
per_trial_c = cdp["cost"] / cdp["trials"]
share = dp["ask"] / dp["trials"]                                  # trials in which a deeper level has regions
saved_first = dp["not_faster_verdicts"] / dp["trials"] * per_call  # nothing is sent back at the first level
extra_lo, extra_hi = share * 2 * 1 * per_call, share * 2 * 3 * per_call
d1 = (per_trial - saved_first + extra_lo, per_trial - saved_first + extra_hi)
d2 = (d1[0], d1[1] + extra_hi)
C_COST = (54 * d1[0] + 54 * d2[0], 54 * d1[1] + 54 * d2[1])
B_COST = (25 * per_trial + 25 * per_trial, 25 * per_trial_c + 25 * (per_trial_c + 3 * per_call))
r10 = lambda x: int(round(x / 10.0)) * 10
r5 = lambda x: int(round(x / 5.0)) * 5

# the loop a rewrite left sequential, as an example: the first one the read-out lists
m = re.search(r"`s252` rep\d, the trial ended parallel-not-faster — a loop beside them, lines \d+–\d+:\n\n  ```c\n(.*?)\n  ```", MD, re.S)
assert m
EXAMPLE = "\n".join(ln[2:] if ln.startswith("  ") else ln for ln in m.group(1).splitlines())


def code(text: str) -> str:
    return '<div class="code"><pre>' + html.escape(text.rstrip("\n")) + "</pre></div>"


def table(head, rows):
    return ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


loops = lambda d: ", ".join(f"<code>{k}</code> ×{v}" for k, v in d.items()) or "none"
P = []
P.append("""<title>Depth Experiment Design</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1c1a;--mute:#66625b;--line:#dedad2;--card:#ffffff;--accent:#8a4b12;--ok:#1f6b3a;--warn:#9a5a00;--code:#f3f0ea}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#171614;--fg:#ebe7df;--mute:#a39d92;--line:#35322d;--card:#1f1e1b;--accent:#e0a064;--ok:#7ec795;--warn:#e2b25c;--code:#23211e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171614;--fg:#ebe7df;--mute:#a39d92;--line:#35322d;--card:#1f1e1b;--accent:#e0a064;--ok:#7ec795;--warn:#e2b25c;--code:#23211e;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.55 Georgia,"Iowan Old Style","Times New Roman",serif;padding-block:28px 60px;padding-inline:16px}
main{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:20px}
h1{font-size:28px;line-height:1.2;margin:0;text-wrap:balance}
h2{font-size:19px;margin:14px 0 0;padding-top:14px;border-top:1px solid var(--line);text-wrap:balance}
h3{font-size:15.5px;margin:0}
p{margin:0;max-width:68ch}
.lede{color:var(--mute)}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:14px 16px;display:flex;flex-direction:column;gap:10px;min-width:0}
.code{overflow-x:auto;background:var(--code);border-radius:4px;border:1px solid var(--line)}
pre{margin:0;padding:10px 12px;font:12.5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-break:break-word}
code{font:0.9em ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:0 3px;border-radius:3px}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{text-align:left;vertical-align:top;padding:7px 10px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--mute);font-size:12.5px;letter-spacing:.04em;text-transform:uppercase}
.k{color:var(--mute);font-size:13px;letter-spacing:.04em;text-transform:uppercase}
.ask{border-left:3px solid var(--accent);padding-left:12px}
.st{display:inline-block;font-size:12.5px;letter-spacing:.03em;padding:1px 7px;border:1px solid var(--line);border-radius:10px;color:var(--mute);white-space:nowrap}
.st.ok{color:var(--ok);border-color:var(--ok)}
.st.wait{color:var(--warn);border-color:var(--warn)}
ul,ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;max-width:68ch}
</style>
<main>""")
P.append("""<header><p class="k">Put to the author 13 Oct 2026 · depth trials reopened 13 Oct, late (the author: “run both”) · the benchmark is built and checked (14 Oct): three loops · the model writes the pragmas in the later experiments</p>
<h1>The depth experiment</h1>
<p class="lede">When the agent keeps a rewrite, it profiles the program again and may find new regions. So far, in every experiment, such a region gets DiscoPoP's pragma at most and is never rewritten a second time. “Depth 1” would let the model be asked about it once more, “depth 2” twice. The experiment was planned to show whether that gains anything and what it costs.</p></header>""")

# ---- the benchmark for depth, built and checked without a model (14 Oct) -------------------------------------
import csv as _csv
sys.path.insert(0, "evaluation/agent/tools")
import prepare_tsvc as _pt  # noqa: E402  (the packager renders the files a model would read)

_E8 = RES / "E08_restructuring_depth/preflight"


def _trials(run):
    r = json.loads((_E8 / run / "results.json").read_text())
    return r.get("runs", r.get("trials", []))


def _sp(t):
    return {k: v["speedup"] for k, v in (t.get("verify") or {}).get("par", {}).items()}


_draws, _refs, _steps = {}, {}, {}
for _run in ("e8_c5_classes_a", "e8_c5_classes_b", "e8_c5_classes_c", "e8_c5_s2111_a", "e8_c5_s2111_b", "e8_c5_s2111_c"):
    for _t in _trials(_run):
        _draws.setdefault(_t["benchmark"].split("/")[1], []).append(_t["outcome"])
for _run in ("e8_c5_refs", "e8_c5_s2111_refs"):
    for _t in _trials(_run):
        _refs[(_t["benchmark"].split("/")[1], _t["arm"])] = (_t["outcome"], _sp(_t))
for _run in ("e8_c5_steps", "e8_c5_s2111_steps"):
    for _r in _csv.DictReader(open(_E8 / _run / "ceiling.csv")):
        _n = _r["loop"].split("/")[1]
        _form = "original" if _r["source"].endswith(f"{_n}/{_n}.c") else "step1" if _r["source"].endswith(".step1.c") else "final"
        _steps[(_n, _form)] = _r
SET_IN, SET_OUT = ("s2251", "s221", "s257"), ("s233", "s123", "s2111")
assert all(_draws[n] == ["no-change"] * 3 for n in SET_IN + ("s123", "s2111")) and _draws["s233"] == ["FASTER"] * 3
assert all(_steps[(n, "step1")]["result"] == "KEPT" and _steps[(n, "final")]["result"] == "KEPT" and _refs[(n, "expert_openmp")][0] == "FASTER" for n in SET_IN)
assert _steps[("s123", "step1")]["result"] == "NO_PATTERN" and all(_steps[("s2111", f)]["result"] == "NO_PATTERN" for f in ("original", "step1", "final"))


def _kept(n, form):
    r = _steps[(n, form)]
    return "nothing" if r["result"] == "NO_PATTERN" else f"{r['applied']} loop{'s' if r['applied'] != '1' else ''}"


def _x(n, label):
    o, sp_ = _refs[(n, label)]
    return f"{sp_['6']:.2f}× / {sp_['12']:.2f}×"


WHAT = {"s2251": "a value carried from one pass to the next, while the array it comes from is overwritten",
        "s221": "an independent statement and a running sum in one loop",
        "s257": "a vector element overwritten in every pass of an inner loop",
        "s233": "two inner loops that share one outer loop",
        "s123": "a write position that depends on how many earlier elements were positive",
        "s2111": "every element needs its left and its upper neighbour"}
WHY_OUT = {"s233": "DiscoPoP alone already makes it faster (3 of 3 runs): nothing to restructure for a first step",
           "s123": "after the first rewrite DiscoPoP finds nothing, although that program is correct and faster with the right pragma — the agent would undo the rewrite",
           "s2111": "DiscoPoP finds nothing after the first rewrite and nothing in the finished program either"}
new_lo = 15 * per_trial + 15 * d1[0] + 15 * d2[0]
new_hi = 15 * per_trial + 15 * d1[1] + 15 * d2[1]
P.append('<div class="card"><h3>The benchmark for depth is built and checked — 14 Oct, no model, no cost</h3>')
P.append(f"<p>You asked for a benchmark that can test several depths. I took the loops our September screening had marked for this, packaged six of them in the same clean form as the contrast set, wrote for each the solution <em>in two steps</em>, and ran every check that needs no model on the server. <strong>Three loops qualify: <code>s2251</code>, <code>s221</code>, <code>s257</code>.</strong> On each, DiscoPoP alone changes nothing; after the first rewrite the agent's own pipeline keeps a pragma on one loop while another loop is still sequential; after the second rewrite the whole computation is parallel and clearly faster. That is exactly the situation in which a second round of asking the model can do something.</p>")
P.append(table(["Loop", "What is in it", "DiscoPoP alone (3 runs)", "After the 1st rewrite the pipeline keeps a pragma on", "After the 2nd", "Speedup of the solution: after step 1 → finished (6 / 12 threads)", ""],
               [[f"<code>{n}</code>", WHAT[n], _draws[n][0].replace("no-change", "no change").replace("FASTER", "already faster"), _kept(n, "step1"), _kept(n, "final"),
                 f"{_x(n, 'step1')} → {_x(n, 'expert_openmp')}", '<span class="st ok">in</span>'] for n in SET_IN]
               + [[f"<code>{n}</code>", WHAT[n], _draws[n][0].replace("no-change", "no change").replace("FASTER", "already faster"), _kept(n, "step1"), _kept(n, "final"),
                   f"{_x(n, 'step1')} → {_x(n, 'expert_openmp')}", f'<span class="st wait">out</span> {WHY_OUT[n]}'] for n in SET_OUT]))
P.append("<p>The three that are out are out by the rule I wrote down before measuring, each for a measured reason. Two of them (<code>s123</code>, <code>s2111</code>) show a limit worth a line in the thesis: the agent keeps a rewrite only if DiscoPoP then finds a parallel loop in it — so a first step that only <em>prepares</em> the second is undone, and no deeper level is ever reached. On these two, DiscoPoP misses a loop that is in fact parallel (a weakness of DiscoPoP I found on the way; it is in the bug list as candidate B27 with a 12-line example). I can run them too, to show that limit on real trials — your choice.</p>")
P.append("<p><strong>Three loops are few.</strong> The other candidates of the screening are either the same idea as one of these, or need data the original benchmark does not have, or are weak cases in which the second step is optional, or sit in programs we have not packaged in the clean form. If you want more, I would have to build loops for the purpose, as we did once for the evidence experiment.</p></div>")
P.append('<div class="card"><h3>The three files a model would read</h3><p>Each is an ordinary code file: the loop exactly as in TSVC, inside TSVC’s repetition loop, nothing of ours in it. These are the texts I owe you before any model sees them.</p>')
for _n in SET_IN:
    _loop = [l for l in _pt.SUITES[_pt.V9_SUITE] if l.name == _n][0]
    P.append(f"<p><code>{_n}.c</code></p>" + code(_pt.v9_files(_loop)[f"{_n}.c"]))
P.append("<p>Beside it the model can see the small header with the array declarations and sizes, and <code>main.c</code>, which holds <code>dummy</code> (it changes a few input values between repetitions, so no repetition can be skipped). For the 2-D loop the three arrays <code>aa</code>, <code>bb</code>, <code>cc</code> are passed to <code>dummy</code> as in TSVC.</p></div>")
P.append('<div class="card"><h3>What the two steps are (the solutions I wrote; no model sees them)</h3>')
for _n in SET_IN:
    _body = lambda f: "\n".join((RES.parent / "reference_solutions/tsvc_c5" / f).read_text().split("{\n", 1)[1].rsplit("    return", 1)[0].rstrip().splitlines())
    P.append(f"<p><code>{_n}</code> — after step 1:</p>" + code(_body(f"{_n}.step1.c")) + "<p>finished:</p>" + code(_body(f"{_n}.c")))
P.append("</div>")
P.append('<div class="card"><h3>What it would cost</h3>')
P.append(table(["What", "Trials", "My estimate"],
               [["The three new loops: no second round, one, two — 5 runs each", "45", f"about ${r10(new_lo)} to ${r10(new_hi)}"],
                ["The 18 loops as the reference, as registered: one and two rounds, 3 runs each (the runs without a second round exist)", "108", f"about ${r10(C_COST[0])} to ${r10(C_COST[1])}"],
                ["Optional: the two loops that cannot be won, to show the limit on trials", "30", f"about ${r10(new_lo * 2 / 3)} to ${r10(new_hi * 2 / 3)}"]]))
P.append(f"<p>The estimates come from the measured cost of the pragma experiment (${per_call:.2f} per call, ${per_trial:.2f} per trial without a second round); how many extra calls a second round really makes is what the experiment will show. Before the full run I would first run each new setting once or twice (a few dollars) to see that a second round really happens and is logged.</p></div>")
P.append('<div class="card"><h3>One thing only you can settle: does this set test two rounds, or also three?</h3>')
P.append("<p>You asked for several depths. All three loops need <em>two</em> rewrites in a row — that tests one extra round (“depth 1”). Whether any of them tests a second extra round depends on how one counts the finished form of <code>s221</code>: its running sum is made parallel in three phases (a sum per block, the blocks’ totals added up, each block shifted by its offset). Counted as three steps, <code>s221</code> is a test of “depth 2”; counted as one known trick, no loop of this set is. The screening left that to you.</p>")
P.append("<p>Either way I run the setting with two extra rounds on all loops, as registered: if nothing needs a third rewrite, the result is that the second extra round adds nothing here — a result, by your rule that a planned experiment is run and reported whatever it shows. A real test of three rewrites in a row would need loops built for it.</p></div>")

P.append('<div class="card"><h3>Reopened on 13 Oct, late</h3>')
P.append("<p>You asked why depth was skipped (“we just need to experiment them and see the results”) and decided: <strong>run it</strong>. The rule written in advance had said the same; my advice to skip had been my own reading of the logs. You added that depth needs a benchmark that tests several depths. That is your rule of 26 Sep: the expert's solution must need two rewrites in a row, the second on code the first created, and three for depth 2. The screening of September lists candidates (<code>s2251</code>, <code>s2111</code>, the family of <code>s341</code>, and others); I build and check that set without a model. The trials then run on it and on the 18 loops as the reference, on the agent as it is. Nothing is launched before you have seen the set and its cost. The second decision below — the model writes the pragmas in the later experiments — stands.</p></div>")
P.append('<div class="card"><h3>Decided on 13 Oct, evening (the depth part was reversed later)</h3>')
P.append("<p>Your answer “ok” to the two questions below, each as I had recommended: <strong>no depth trials</strong> — the count from our saved trials is the answer for these loops, and the two points about depth as built are stated as limits — and <strong>the model writes the pragmas in the experiments that remain</strong>. What a second round would have done with the few loops that leave a second task stays unknown, and is said as a limit. The text below is as it was put to you.</p></div>")
P.append('<div class="card"><h3>The two decisions, in short (as put to you)</h3>')
P.append(f"""<ol class="ask"><li><strong>Depth:</strong> I recommend <em>no depth trials</em>. Our saved trials already show that on the 18 loops a second round has new work in {dp['other']} of {dp['ask']} trials; in the others it would only ask again about the loop over the repetitions, which the model was already asked about, and the function around it. The experiment as planned would also mix depth with two other differences. The reasons are below.</li>
<li><strong>Who writes the pragmas in the experiments that remain</strong> (the decision you postponed on 10 Oct): I recommend <em>the model</em>. The rule shown to you before that comparison is met, the contrast set agrees, and it needs fewer calls and profiles. The case for DiscoPoP is below.</li></ol>
<p>If you answer “ok”, I read it as: no depth trials, and the model writes the pragmas in the experiments that remain. Anything else, please say.</p></div>""")

P.append("<h2>What the experiment would tell us that our runs cannot</h2>")
P.append("<p>Whether a second round of rewriting makes more programs fast and right, and at what price in model calls, profiles and speed. Our runs so far all stop after the first round.</p>")

P.append("<h2>What our saved trials already answer</h2>")
P.append("<p>Even at depth 0 the agent profiles again after a kept rewrite and lists what it would look at next. It then skips every region that has no DiscoPoP pragma, only because of the depth limit. Those skipped regions are exactly what a second round would send to the model, and they are in every saved log. I counted them, without a model, in the 90 trials per setup of the experiment on who writes the pragma.</p>")
P.append(table(["", "DiscoPoP writes the pragmas", "The model writes the pragmas"], [
    ["Trials", dp["trials"], mo["trials"]],
    ["Trials in which a rewrite was accepted", dp["accepted"], mo["accepted"]],
    ["A second round would ask the model", f"{dp['ask']} of {dp['accepted']}", f"{mo['ask']} of {mo['accepted']}"],
    ["— only about the repetition loop and the function around it", dp["ask"] - dp["other"], mo["ask"] - mo["other"]],
    ["— also about a different loop the rewrite left sequential", f"{dp['other']} ({loops(dp['other_loops'])})", f"{mo['other']}"],
]))
P.append(f"""<ul><li><strong>Where DiscoPoP writes, a second round is entered in every trial with a kept rewrite</strong> — but about the loop over the repetitions, which the model had already been asked about in the first round in {dp['asked_before']['the repetition loop']} of {dp['regions']['the repetition loop']} trials, and about the function around it.</li>
<li><strong>A different loop is left in {dp['other']} trials, on {len(dp['other_loops'])} of the 18 loops.</strong> That is the case the experiment was planned for.</li>
<li><strong>Where the model writes, a second round has no new loop in any trial.</strong></li></ul>""")
P.append("<p>The clearest case where a second round could gain is <code>s252</code>: the model split the loop, DiscoPoP made the first half parallel, and this second half stayed sequential. Both such trials ended not faster.</p>")
P.append(code(EXAMPLE))
P.append(f"""<p><strong>How to read these numbers.</strong> I defined the kinds of region after reading the logs, so this is a description of our trials, not a measure fixed in advance. The table uses the corrected results of that experiment. In my last message I gave the count before the correction of one loop: another loop in {dp0['other']} of {dp0['ask']} trials. On the six loops of the contrast set a different loop is listed more often ({cdp['other']} of {cdp['ask']} trials where DiscoPoP writes), but half of those loops lie inside a loop that DiscoPoP is about to make parallel.</p>""")
P.append("<p><strong>Why the two setups differ.</strong> A rewrite without a pragma counts as having made nothing parallel yet, so the loop around it and the function keep their full share of the time and are offered again. A rewrite that carries the model's pragmas counts as parallel, and what is around it is offered again only where 1 % of the time or more is still sequential.</p>")

P.append("<h2>Two things in the agent that would blur a depth experiment</h2>")
P.append(f"""<ol><li><strong>The first round changes too.</strong> Today the agent sends a rewrite back when the program is not faster than before, and the model tries again. With a second round to come, the agent no longer does that in the first round: it keeps every safe rewrite and asks about speed only at the end. That was your decision of 26 Sep, for a good reason then — a later rewrite may be what makes an earlier one pay. But in our saved trials this “not faster, try again” fired in {dp['trials_sent_back_not_faster']} of {dp['trials']} trials, and {dp['sent_back_ended'].get('FASTER', 0)} of those ended faster. So “depth 0 against depth 1” would differ in two things, not one.</li>
<li><strong>A second rewrite can take the credit of the first.</strong> A rewrite is kept if the program with DiscoPoP's pragmas on the loops near the changed lines is not slower than the program before it — and that program has no pragmas yet. If the second rewrite touches the loops the first one made parallel, it is timed as if it had made them parallel itself. A second rewrite that adds nothing, or loses part of the gain, would be kept. The final check against the original program still holds, so no wrong result would be reported; but “what the second round gained” could not be read off.</li></ol>
<p>Both are read in the agent's code. Neither has been shown by a run.</p>""")

P.append("<h2>The options for depth</h2>")
P.append(table(["Option", "What it gives", "Cost", "The case for it"], [
    ["<strong>A. No depth trials</strong> (my recommendation)",
     f"The thesis answers the question for these loops from the saved trials: after the first kept rewrite nothing new is left to rewrite in {dp['ask'] - dp['other']} of {dp['ask']} trials. The two points above are stated as limits. Depth stays in the agent, switched off, described as not evaluated by trials.",
     "Nothing.",
     "The count answers the question the experiment was planned for, without the two blurs. Whether depth is tried on the large code is decided with that experiment."],
    ["<strong>B. Repair depth, then a small run</strong>",
     "Three changes to the agent that act only when a second round is allowed, a pilot without a model, then about five loops that leave a second loop, 5 repeats, two levels: about 50 trials.",
     f"About ${r5(B_COST[0])} to ${r5(B_COST[1])} (my estimate from the measured cost per call), and one to two days of building first.",
     "Only trials can show whether a second round turns the not-faster trials of <code>s252</code> into faster ones. Against it: the loops would be chosen after looking at their trials, and the effect can be small at best."],
    ["<strong>C. The experiment as planned, on the agent as it is</strong>",
     "Depth 0, 1 and 2 on the 18 loops, 3 repeats, 108 new trials.",
     f"About ${r10(C_COST[0])} to ${r10(C_COST[1])} (my estimate), the matching model-only trials on top.",
     "It is the experiment as written down, and it was expected to show no difference on these loops. Against it: it would mostly measure asking again about code the model has just rewritten, mixed with the two points above."],
]))

P.append("<h2>Who writes the pragmas in the experiments that remain</h2>")
P.append("<p>On 10 Oct you kept DiscoPoP writing the pragmas for the fast-refresh experiment, because the refresh decides something only in that setup, and postponed the choice for the later experiments until that experiment was read out. It is closed now. What we have, from the corrected results:</p>")
P.append(table(["", "DiscoPoP writes", "The model writes"], [
    ["The 18 loops: right, race-free and faster", f"{d18} of 90", f"{m18} of 90 (difference not established, p = {p18:.3f})"],
    ["The six contrast loops", f"{d6} of 30", f"{m6} of 30 (p = {p6:.3f} as a single test)"],
    ["Unusable programs", f"{un[0]['unusable']} of {un[0]['n']} and {un[2]['unusable']} of {un[2]['n']}", f"{un[1]['unusable']} of {un[1]['n']} and {un[3]['unusable']} of {un[3]['n']}"],
    ["Model calls: 18 loops · contrast loops", f"{dp['calls']} · {cdp['calls']}", f"{mo['calls']} · {cmo['calls']}"],
    ["Cost: 18 loops · contrast loops", f"${dp['cost']:.2f} · ${cdp['cost']:.2f}", f"${mo['cost']:.2f} · ${cmo['cost']:.2f}"],
    ["Full profiles after a rewrite: 18 loops · contrast loops", f"{dp['full_reprofiles']} · {cdp['full_reprofiles']}", f"{mo['full_reprofiles']} · {cmo['full_reprofiles']}"],
]))
P.append(f"""<ul><li><strong>The rule shown to you before that comparison:</strong> the model writes from then on only if it ships no unusable program and is right in at least 5 more of the 90 trials. It is met exactly ({m18} − {d18} = 5). You had not approved the rule before the result, and you set it aside for the fast-refresh experiment only.</li>
<li><strong>What changes if the model writes:</strong> after a rewrite, DiscoPoP's analysis confirms almost nothing any more; the checks decide. DiscoPoP's part is then the evidence the model is shown, the choice of where to look first, the dependence check among the checks, and the pragmas of loops that need no rewrite. The sentence “the model removes the dependence, DiscoPoP confirms and writes the pragma” would describe the main comparison and the evidence experiments, not the later ones.</li>
<li><strong>What remains to run:</strong> where to look first, the large code, and the comparison with RepoOMP. On the large code one profile takes about 44 seconds and 28 GB at the small problem size we measured, and where DiscoPoP writes the agent profiles about {dp['full_reprofiles'] / mo['full_reprofiles']:.1f} times as often.</li></ul>""")
P.append(table(["Option", "The case for it"], [
    ["<strong>The model writes</strong> (my recommendation)",
     "The rule is met; the contrast set, whose loops are of the kind our record names in the large code (a minimum with its index), shows the same direction with a third of the calls; fewer profiles where one is expensive. The main comparison stays as it is, and the experiment on who writes already holds the same 18 loops in this setup, so nothing has to be run again."],
    ["<strong>DiscoPoP writes</strong>",
     "One setup for the whole thesis — the one of every finished experiment and of the thesis's stated idea. The lead of the other setup on the 18 loops is not established, and the contrast set was chosen to show a contrast."],
    ["<strong>Both, on the large code only</strong>",
     "It would carry the comparison to a real application for the price of one more setup there. It can be decided with that experiment's design; I would propose it there if its cost allows."],
]))
P.append("<h2>How I read your answer (14 Oct)</h2>")
P.append(f"""<p class="ask"><strong>“ok” means:</strong> the depth experiment starts, with DiscoPoP writing the pragmas as registered — first each new setting once on one loop, to see that a second round really happens (a few dollars); then the three new loops (45 trials) and the 18 loops (108 trials), about ${r10(new_lo + C_COST[0])} to ${r10(new_hi + C_COST[1])} together. The two loops that cannot be won are <em>not</em> run. The fast-refresh trials do <em>not</em> start — their benchmark is not ready; that is on the other page.</p>
<p>Anything else — only the new loops, the two unwinnable loops as well, more loops built for the purpose, a different count for <code>s221</code> — please say so. Until you answer, no model is called.</p>
<p class="lede">Earlier on this page: your “ok” of 13 Oct (no depth trials) and your “run both” later that night, which reversed it; then your remark that depth needs its own benchmark, which is what the first card answers.</p>""")
P.append("</main>")
OUT.write_text("\n".join(P) + "\n")
print(f"{OUT}: {OUT.stat().st_size} bytes; estimates: B ${B_COST[0]:.1f}–${B_COST[1]:.1f}, C ${C_COST[0]:.1f}–${C_COST[1]:.1f}; per call ${per_call:.3f}; "
      f"per trial ${per_trial:.2f} / ${per_trial_c:.2f}; profiles ratio {dp['full_reprofiles'] / mo['full_reprofiles']:.2f}")
