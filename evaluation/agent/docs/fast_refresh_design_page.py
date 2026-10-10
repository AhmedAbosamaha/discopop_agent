#!/usr/bin/env python3
"""The page that puts the design of the fast-refresh experiment (E4) to the author, with the texts a model would
read, verbatim from the agent's code (10 Oct 2026). Nothing is built or run.

    venv/bin/python <this file> OUT.html        (from the repository root)
"""
import html
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from discopop_agent.llm import dep_reconstruct, prompts  # noqa: E402

OUT = Path(sys.argv[1])
SYSTEM = prompts._SYSTEM_RECONSTRUCT
FOLDED = prompts._RECON_ADDENDUM
# the follow-up request, as `ask_after_gate` builds it; every literal line is checked against the function's source
FOLLOWUP_LINES = [
    "Your rewrite was accepted and written to the file.",
    "",
    "The profiler will NOT be run on it, so no dependence has been measured in the code you just wrote. Report what a run would have observed.",
    "",
    "IMPORTANT — the checks your rewrite just passed say nothing about whether the loop iterations are independent. If your rewrite carried no pragma, it was compiled and run SEQUENTIALLY: nothing ran in parallel, so ThreadSanitizer had nothing to race and its silence is not evidence. Report what the CODE does, not what the checks did.",
    "",
    "```cpp",
    "<the lines the rewrite added or changed, with six lines around them, each with its line number>",
    "```",
    "",
    "Loops to report on, by header line: <the header lines of the loops shown>",
    "",
    "One line per dependence, or `LOOP <line> NONE` for an independent loop.",
]
src = inspect.getsource(dep_reconstruct.ask_after_gate)
flat = "".join(part for part in __import__("re").findall(r'"((?:[^"\\]|\\.)*)"', src))
for probe in ("Your rewrite was accepted and written to the file.", "The profiler will NOT be run on it, so no dependence has been measured ",
              "in the code you just wrote. Report what a run would have observed.", "whether the loop iterations are independent. If your rewrite carried no ",
              "so ThreadSanitizer had nothing to race and its silence is not evidence. ", "Report what the CODE does, not what the checks did.",
              "One line per dependence, or `LOOP <line> NONE` for an independent loop."):
    assert probe in flat, probe


def code(text: str) -> str:
    return '<div class="code"><pre>' + html.escape(text.rstrip("\n")) + "</pre></div>"


def table(head, rows):
    return ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


P = []
P.append("""<title>Fast Refresh Design</title>
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
ul,ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;max-width:68ch}
</style>
<main>""")
P.append("""<header><p class="k">For your decision · 10 Oct 2026 · nothing is built or run</p>
<h1>The fast-refresh experiment: a design</h1>
<p class="lede">After the model rewrites a loop, the agent profiles the whole program again: it compiles it with DiscoPoP's instrumentation, runs it, and lets DiscoPoP analyse the run. The fast refresh skips the run. It compiles only, and carries the dependences of the last run over to the new code. For the lines the model just wrote there is then no measurement. The second idea is to ask the model itself which dependences those lines have.</p></header>""")

P.append("<h2>What it would tell us that our runs cannot</h2>")
P.append("""<ol><li><strong>Does skipping the run change what DiscoPoP says about the model's real rewrites?</strong> We only know it for three small programs written for the purpose: in 7 of 18 comparisons the fast refresh suggested a parallel loop that the full profile does not support.</li>
<li><strong>Does the model's own report of the dependences repair that?</strong> Never measured.</li>
<li><strong>How many seconds does it save where the run is long?</strong> We know how long the runs are, not what one refresh saves.</li></ol>""")

P.append("<h2>What our runs already say</h2>")
P.append("<p><strong>On the 18 loops there is no time to save.</strong> From the 90 agent trials of the main comparison:</p>")
P.append(table(["One profile of such a program", "Time", "Skipped by the fast refresh"],
               [["compile with instrumentation", "0.20 s", "no"], ["run", "0.17 s", "yes"], ["DiscoPoP's analysis", "1.41 s", "no"]]))
P.append("<p>The skipped runs add up to 0.08 % of the agent's time. So on these loops the fast refresh can only be harmless or harmful, never useful.</p>")
P.append("<p><strong>The run is long on three whole programs</strong> (DiscoPoP alone, three draws): <code>hotspot</code> 53.0 s, <code>is</code> 30.6 s, <code>md</code> 21.4 s. It is over one second on eight programs in all; on PolyBench the middle value is 0.11 s and the longest 4.4 s.</p>")
P.append("<p><strong>The profile after a rewrite matters only where DiscoPoP writes the pragmas</strong> — which is the setup you chose for this experiment. There every rewrite that passes the checks is kept or thrown away by what DiscoPoP says about it.</p>")
P.append("<p><strong>We already hold 601 real rewrites to test it on.</strong> Every rewrite of the model that passed the checks is saved with its trial:</p>")
P.append(table(["Experiment, setup in which DiscoPoP writes the pragmas", "Trials", "Saved rewrites that passed the checks"],
               [["The pragma experiment, 18 loops", "90", "227"], ["The pragma experiment, the four recurrence loops", "12", "52"],
                ["The contrast set", "35", "144"], ["The main comparison, 18 loops", "90", "178"], ["<strong>Together</strong>", "227", "<strong>601</strong>"]]))

P.append("<h2>The design I propose: four steps, the cheap ones first</h2>")
P.append(table(["Step", "Model?", "What runs", "What it reads out", "Cost"], [
    ["<strong>1. Replay</strong>", "no", "Each of the 601 saved rewrites, on the server: the program before it is profiled in full; then the rewritten program once with the full profile and once with the fast refresh.",
     "How often DiscoPoP says the same about the rewrite. Where it differs: <em>parallel only after the fast refresh</em> (the dangerous side — and whether the agent's checks then stop the pragma) or <em>parallel only after the full profile</em> (a lost chance). Per loop.",
     "No model. A new tool, about a day to build and test; about an hour of server time."],
    ["<strong>2. The model's report</strong>", "yes, one call per rewrite, no agent run", "On the rewrites where step 1 found a difference, and as many where it found none: the model is asked for the dependences of the new lines (the text below), its answer is added, DiscoPoP analyses again.",
     "Differences removed; agreeing cases it breaks; answers that could not be placed. And the opposite direction on the same rewrites — the model <em>deletes</em> dependences it calls unreal — which the thesis argues is the unsafe one.",
     "About $15 to $40, fixed when step 1 shows how many rewrites differ."],
    ["<strong>3. Time</strong>", "no", "On the three programs with a long run and on PolyBench's longest: an edit that changes nothing, then full profile against fast refresh, five times each.",
     "Seconds saved by one refresh, and what share of an agent run that would be.", "No model. Minutes of server time."],
    ["<strong>4. Live trials</strong> — only if steps 1 and 2 say the refresh keeps DiscoPoP's verdicts", "yes", "The agent with the fast refresh and the model's report on the 18 loops × 5, against the pragma experiment's setup with the full profile (its 90 trials exist).",
     "Whether the finished programs are as often correct, race-free and faster, and whether anything unusable is shipped.", "90 trials, about $55 to $60."],
]))
P.append("<p><strong>If steps 1 and 2 show that the refresh changes verdicts and the report does not repair it,</strong> step 4 is not run. The thesis then says the fast refresh is not adopted, with the measured reason — the agent has profiled in full by default since 21 September.</p>")
P.append("<p><strong>What the steps answer.</strong> Your three written-down claims are all about <em>decisions that differ from a full profile</em>: that the refresh changes none; that the model's report reduces the ones it changes; that letting the model delete dependences is unsafe while letting it add them is not. Steps 1 and 2 count exactly those decisions, on 601 real rewrites instead of trial by trial.</p>")

P.append("<h2>The other way: live trials from the start</h2>")
P.append("<p>September's plan: three setups × 18 loops × 3 = 162 agent trials, about $100.</p>")
P.append("""<ul><li><strong>For it:</strong> it measures the whole agent, including how a different verdict changes what the model tries next; and the report is asked in the model's own conversation, as the agent would do it. A replay asks the model fresh, and judges one rewrite at a time.</li>
<li><strong>Against it:</strong> on these loops there is nothing to save, so the trials can only show harm or no harm; the replay shows the same on four times as many rewrites, without the noise between trials, and for a fraction of the cost. Step 4 keeps the live check for the case in which it is worth running.</li></ul>""")

P.append("<h2>The texts a model would read</h2>")
P.append("<p>Word for word from the agent's code, unchanged since September. Nothing has been sent to a model.</p>")
P.append('<div class="card"><h3>The instructions of the report request</h3>' + code(SYSTEM) + "</div>")
P.append('<div class="card"><h3>The request itself, sent after a rewrite has passed the checks</h3>' + code("\n".join(FOLLOWUP_LINES)) + "</div>")
P.append('<div class="card"><h3>The other form: the same request appended to the rewrite instructions (no extra call)</h3>' + code(FOLDED) + "<p>I propose not to use this form: it changes the text of the rewrite request itself, so the rewrites would no longer be comparable with the pragma experiment's.</p></div>")
P.append("<p><strong>Three sentences are not exactly true of what the agent does.</strong> Your rule is that a text must be true; these are yours to decide.</p>")
P.append(table(["The text says", "What the agent does", "I would write"], [
    ["“Your rewrite was accepted and written to the file.”", "It has passed the checks and is in the file. Whether it is kept is decided afterwards, by what DiscoPoP finds in it and by its speed.", "“Your rewrite passed the checks and is in the file.”"],
    ["“The profiler will NOT be run on it …”", "Not now. Before the pragmas are written at the end, the whole program is profiled in full once.", "“The profiler has not been run on it …”"],
    ["“A dependence you omit makes a sequential loop look parallel, which is a race.”", "The loop can then look parallel to DiscoPoP; a pragma written on it still has to pass the race check and the output check.", "“A dependence you omit can make a sequential loop look parallel.” — and nothing about what follows."],
]))
P.append("<p>The honest case for leaving the third as it is: the warning pushes the model to report when unsure, which is the safe direction, and a softer sentence may make it report less.</p>")

P.append("<h2>What I need from you</h2>")
P.append("""<ol class="ask"><li><strong>The design:</strong> the four steps (my recommendation), or live trials from the start.</li>
<li><strong>The three sentences:</strong> corrected as proposed, or left.</li>
<li><strong>The form of the request:</strong> a separate request after the rewrite (my recommendation), not the appended form.</li></ol>""")
P.append("<p>Nothing starts before your answer. The 15 trials of the repaired loop come first in any case.</p>")
P.append("</main>")
OUT.write_text("\n".join(P) + "\n")
print(f"{OUT}: {OUT.stat().st_size} bytes")
