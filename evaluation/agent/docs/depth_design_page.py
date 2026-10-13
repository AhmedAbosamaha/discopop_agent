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
P.append("""<header><p class="k">Put to the author 13 Oct 2026 · nothing built, nothing run · two decisions wait for you</p>
<h1>The depth experiment</h1>
<p class="lede">When the agent keeps a rewrite, it profiles the program again and may find new regions. So far, in every experiment, such a region gets DiscoPoP's pragma at most and is never rewritten a second time. “Depth 1” would let the model be asked about it once more, “depth 2” twice. The experiment was planned to show whether that gains anything and what it costs.</p></header>""")

P.append('<div class="card"><h3>The two decisions, in short</h3>')
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
P.append("<h2>How I read your answer</h2>")
P.append("<p>“ok” means: no depth trials (option A), and the model writes the pragmas in the experiments that remain. For anything else — a depth run, DiscoPoP writing, or both on the large code — please say so. No model is called for the depth experiment before you have answered.</p>")
P.append("</main>")
OUT.write_text("\n".join(P) + "\n")
print(f"{OUT}: {OUT.stat().st_size} bytes; estimates: B ${B_COST[0]:.1f}–${B_COST[1]:.1f}, C ${C_COST[0]:.1f}–${C_COST[1]:.1f}; per call ${per_call:.3f}; "
      f"per trial ${per_trial:.2f} / ${per_trial_c:.2f}; profiles ratio {dp['full_reprofiles'] / mo['full_reprofiles']:.2f}")
