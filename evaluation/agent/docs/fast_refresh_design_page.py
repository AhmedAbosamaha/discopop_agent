#!/usr/bin/env python3
"""The page of the fast-refresh experiment (E4) for the author: where it stands, what is asked of him, the design
as decided, and the texts a model would read, verbatim from the agent's code. First built 10 Oct 2026; since 12 Oct
with the results of the steps that need no model.

    venv/bin/python <this file> OUT.html        (from the repository root)
"""
import html
import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from discopop_agent.llm import dep_reconstruct, dep_review, prompts  # noqa: E402

OUT = Path(sys.argv[1])
SYSTEM = prompts._SYSTEM_RECONSTRUCT
FOLDED = prompts._RECON_ADDENDUM
# the follow-up request, as `ask_after_gate` builds it; every literal line is checked against the function's source
FOLLOWUP_LINES = [
    "Your rewrite passed the checks and is in the file.",
    "",
    "The profiler has not been run on it, so no dependence has been measured in the code you just wrote. Report what a run would have observed.",
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
for probe in ("Your rewrite passed the checks and is in the file.", "The profiler has not been run on it, so no dependence has been measured ",
              "in the code you just wrote. Report what a run would have observed.", "whether the loop iterations are independent. If your rewrite carried no ",
              "so ThreadSanitizer had nothing to race and its silence is not evidence. ", "Report what the CODE does, not what the checks did.",
              "One line per dependence, or `LOOP <line> NONE` for an independent loop."):
    assert probe in flat, probe


# the request of the opposite direction, as `dep_review.review_dependences` builds it — taken from the function itself
_seen = {}
_real_complete = dep_review._complete
dep_review._complete = lambda provider, client, model, convo, system, **kw: _seen.update(prompt=convo[-1]["content"], system=system) or ""
dep_review.review_dependences(
    [{"dep_type": "<RAW|WAR|WAW>", "var": "<variable>", "memory_region": "", "sink_line": None, "source_line": None,
      "sink_text": "", "source_text": "", "loop": "<first line>-<last line>", "loop_carried": True,
      "loop_lines": "<the lines of that loop and the six after it, each with its line number>"}],
    "<the rewritten lines with three lines around them, each with its line number>", "model", provider="claude-agent-sdk")
dep_review._complete = _real_complete
DELETION_SYSTEM, DELETION_REQUEST = _seen["system"], _seen["prompt"]
assert DELETION_SYSTEM == prompts._SYSTEM_DEPS


WHATIF_HTML = ("<p><strong>A check on the saved answers, without a model.</strong> The same 116 answers were added again. Added the agent's way, every decision came out as before (116 of 116). Then with one rule changed: a reported dependence is left out where it lies inside a loop that the same answer calls independent.</p>"
               + "@@WHATIF_TABLE@@"
               + "<p>So the rule gives back every win the report had cost — which confirms where the damage comes from. But it loses three of the regained reductions, because there the model calls the <em>repetition</em> loop independent and the rule then throws away the dependence of the loop inside it; and three rewrites again keep a parallel loop that the full profile does not support — the agent's way had removed all four of those. It trades one error for another. A placing that is right both ways has to tell DiscoPoP which loop carries the dependence; I have not examined whether its data can be made to. I tried no second rule: choosing rules on these 116 rewrites until one fits would prove nothing.</p>")
WHATIF_ROWS = [
    ["Wins the fast refresh loses, kept again (of 22)", "20", "17"],
    ["Wins lost among the 58 rewrites the fast refresh had right", "4", "0"],
    ["Those 58 kept with another pragma or one loop fewer", "7", "7"],
    ["Rewrites that keep a parallel loop the full profile does not keep (4 after the fast refresh alone)", "0", "3"],
]
STEP3_STATE = '<span class="st ok">done 12 Oct</span>'
STEP3_LINE = "Where the run is long, one fast refresh saves 21 to 36 s — a third to two thirds of one refresh, and 1.5 to 7.5 % of a trial."
STEP3_ROWS = [
    ["<code>hotspot</code>", "108 s", "72 s", "36 s (33 %)", "2.6 to 5.2 %"],
    ["<code>is</code>", "41 s", "14 s", "27 s (66 %)", "1.5 to 7.5 %"],
    ["<code>md</code>", "34 s", "13 s", "21.5 s (63 %)", "2.6 to 6.8 %"],
    ["<code>correlation</code> (PolyBench's longest)", "7.7 s", "3.5 s", "4.2 s (54 %)", "no agent trial in the archive"],
]
STEP3_HTML = (
    "<p>On the three programs whose profiling run is long and on PolyBench's longest, without a model: after an edit that changes nothing "
    "(one comment line), the fast refresh and the full profile were each taken five times. Middle values:</p>"
    + "@@TABLE@@"
    + "<p><strong>It saves the run and nothing else.</strong> Carrying the dependences over costs hundredths of a second. On <code>hotspot</code> "
    "DiscoPoP's own analysis takes anything between 52 and 129 s from one time to the next — more than the run that is skipped (50 s) — so in one "
    "of the five pairs the fast refresh was not the shorter one.</p>"
    "<p><strong>It is a few per cent of a trial,</strong> because a trial on these programs is mostly model time and checks. The share comes from "
    "September's agent trials on these programs: the number of full profiles in each trial times the saving measured now, over the trial's duration.</p>"
    "<p><strong>On an unchanged program the fast refresh gives the parallel loops and clauses of a full profile</strong> — in all 20 cases. On "
    "<code>md</code> and <code>correlation</code> two full profiles of the same program do not always agree with each other; there the fast refresh "
    "gives one of their answers.</p>"
    "<p><strong>Together with step 1:</strong> the fast refresh saves a few per cent of a trial where the run is long and nothing on the loops, and "
    "on the model's real rewrites it throws away the wins that rest on a dependence the rewrite created.</p>")


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
.st{display:inline-block;font-size:12.5px;letter-spacing:.03em;padding:1px 7px;border:1px solid var(--line);border-radius:10px;color:var(--mute);white-space:nowrap}
.st.ok{color:var(--ok);border-color:var(--ok)}
.st.wait{color:var(--warn);border-color:var(--warn)}
ul,ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;max-width:68ch}
</style>
<main>""")
P.append("""<header><p class="k">Put to the author 10 Oct 2026 · decided 12 Oct · steps 1 to 3 done 13 Oct · live trials reopened 13 Oct (the author: “run both”) · their benchmark: screened 14 Oct, two candidates, not ready · 18 Oct: the later experiments dropped; your go — the live trials run on the loops</p>
<h1>The fast-refresh experiment</h1>
<p class="lede">After the model rewrites a loop, the agent profiles the whole program again: it compiles it with DiscoPoP's instrumentation, runs it, and lets DiscoPoP analyse the run. The fast refresh skips the run. It compiles only, and carries the dependences of the last run over to the new code. For the lines the model just wrote there is then no measurement. The second idea is to ask the model itself which dependences those lines have.</p></header>""")

# ---- where it stands (12 Oct, evening): the steps that need no model ------------------------------------------------
P.append('<h2 id="now">Where it stands</h2>')
P.append(table(["Step", "State", "In one line"], [
    ["1. Replay, no model", '<span class="st ok">done 12 Oct</span>',
     "The fast refresh changes whether the agent keeps a rewrite in 58 of 599 rewrites; two full profiles of the same program never disagree (0 of 599). 22 wins are thrown away. No time is saved."],
    ["2. The model's report", '<span class="st ok">done 13 Oct</span>',
     "The model's report gives back 20 of the 22 lost wins, but damages 11 of 58 rewrites the fast refresh had right — about 100 of all 541. Deleting dependences changed nothing. 136 calls, $8.53."],
    ["3. Time on long programs, no model", STEP3_STATE, STEP3_LINE],
    ["4. Live trials", '<span class="st wait">running on the loops since 18 Oct</span>', "First dropped (your “ok go ahead”), then reopened by you the same night (“run both”). On 18 Oct you made this and depth the last experiments and said “go with the fast refresh’s live trials”: they run on the loops, as priced — see below."],
]))
# ---- 18 Oct: the live trials, on the loops ----------------------------------------------------------------------------
import base64  # noqa: E402
_FIG10 = (Path("evaluation/agent/results/E04_fast_refresh/analysis/fig_refresh_decisions.png")).read_bytes()
P.append('<div class="card"><h3>18 Oct — the live trials run, on the loops</h3>')
P.append("<p>You made the fast refresh and depth the last two experiments, dropped the rest, and said “go with the fast refresh’s live trials”. I read that as the route I had priced: the agent with the fast refresh and the model’s report, five trials on each of the 18 loops and of the contrast set with its control — 125 trials, about $100 — beside the trials of the same agent with the full re-profile from the pragma experiment and the contrast set. The route through NPB’s EP and CG is not taken: its packages were the RepoOMP work that was dropped, their form was never decided, and it was not priced; it can be added if you say so.</p>")
P.append("<p><strong>What these trials can show and what they cannot.</strong> They show whether the decisions the fast refresh changes cost the agent wins in whole trials, where the model may try again — most of the lost wins of step 1 are on the contrast loops. They cannot show time saved: on these loops the run a refresh skips is a fraction of a second, so the saving is reported as estimated from step 1 and step 3.</p>")
P.append("<p><strong>Before the 125:</strong> two trials as a test run, with a rule written before it ran — both must finish without a failed model call, and at least one must show a fast refresh after a kept rewrite followed by the model’s answered report. If it passes, the 125 start without another question; if not, it comes back to you.</p>")
P.append("<figure style=\"margin:16px 0 0\"><img alt=\"Fig. 10: the agent's decision after a fast refresh against the full re-profile on 599 saved rewrites, and what the model's report repaired and broke\" style=\"max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px\" src=\"data:image/png;base64," + base64.b64encode(_FIG10).decode() + "\">"
         "<figcaption style=\"font-size:14px;color:var(--mute);margin-top:6px\">The thesis’s figure for this experiment (Fig. 10, drawn 18 Oct from the saved read-outs): (a) step 1 — the agent’s decision after a fast refresh against the full re-profile, with the control; (b) step 2 — what the model’s report repaired and broke. A third panel, the live trials, is added when they are read out.</figcaption></figure>")
P.append("</div>")

# ---- the benchmark for the live trials: the screen of 14 Oct (no model) ---------------------------------------------
_SCR = Path("evaluation/agent/results/E04_fast_refresh/preflight/e4_refresh_screen_npbc")
_PRB = Path("evaluation/agent/results/E11_repoomp/preflight/e11_npbc_probe_server")


def _cell(path):
    j = json.loads(path.read_text())["rows"][0]
    return j, (j.get("instrument_s", 0) + j.get("run_s", 0) + j.get("explore_s", 0))


_rows = []
for _k, _what in (("EP", "random pairs"), ("IS", "integer sort"), ("CG", "conjugate gradient")):
    for _c in ("S", "W", "A", "B"):
        _f = (_PRB / _k / "summary.json") if _c == "S" else (_SCR / _c / _k / "summary.json")
        if not _f.exists():
            continue
        _j, _tot = _cell(_f)
        if _j.get("error"):
            _rows.append([f"<code>{_k}</code>", _c, f"crashes after {_j['run_s']:.0f} s", "—", "—", '<span class="st wait">no</span>'])
            continue
        _ok = _j["run_s"] >= 60 and _j["run_s"] >= _tot / 2
        _rows.append([f"<code>{_k}</code> ({_what})" if _c == "S" else f"<code>{_k}</code>", _c, f"{_j['run_s']:.1f} s", f"{_tot:.0f} s",
                      f"{_j['run_s'] / _tot * 100:.0f} %", '<span class="st ok">yes</span>' if _ok else '<span class="st wait">no</span>'])
_lt = json.loads(Path("evaluation/agent/results/E06_lulesh/preflight/e6_lulesh_smoke3/results.json").read_text())
_lp = (_lt.get("runs") or _lt.get("trials"))[0]["profile"]
_ltot = _lp["instrument_s"] + _lp["profiled_run_s"] + _lp["explore_s"]
_rows.append(["LULESH", "its profile size", f"{_lp['profiled_run_s']:.1f} s", f"{_ltot:.0f} s", f"{_lp['profiled_run_s'] / _ltot * 100:.0f} %", '<span class="st wait">no</span>'])
_ep = _cell(_SCR / "B" / "EP" / "summary.json")
_cg = _cell(_SCR / "A" / "CG" / "summary.json")
assert _ep[0]["run_s"] > 200 and _cg[0]["run_s"] > 120
P.append('<h2 id="bench">The benchmark for the live trials — where it stands (14 Oct, no model, no cost)</h2>')
P.append("<p>You said the fast refresh needs a benchmark on which profiling is slow, or its effect cannot show. A refresh skips one thing: the run of the instrumented program. So a program qualifies only if that run is long <em>and</em> is the larger part of a profile. I measured the candidates I had named in advance on the server: the three NPB programs DiscoPoP can profile (EP, IS, CG), each at NPB’s input classes from the smallest up, and LULESH.</p>")
P.append(table(["Program", "NPB input class", "The run a refresh would skip", "One whole profile", "The run’s share", "Run ≥ 1 min and ≥ half"], _rows))
P.append(f"<p><strong>Two pass on these numbers:</strong> EP at class B (the run is {_ep[0]['run_s']:.0f} s of a {_ep[1]:.0f} s profile) and CG at class A ({_cg[0]['run_s']:.0f} s of {_cg[1]:.0f} s). IS stays under a minute at class A and its instrumented run crashes at class B. On LULESH the profile is almost all analysis, which no refresh shortens. The three programs of step 3 (<code>hotspot</code>, <code>is</code>, <code>md</code>) save 36, 27 and 21.5 s — under the minute, as said before.</p>")
P.append('<div class="card"><h3>Why the set is not ready: two things I cannot settle without you</h3>')
P.append("<ol><li><strong>The form of the package.</strong> In these NPB programs <code>main</code>, NPB’s own timer and its own check of the result stand in the same file as the computation. Your rule of 4 Oct says the model’s file is an ordinary code file with nothing of ours in it. Two ways: <em>(a)</em> leave the file exactly as RepoOMP ships it and let our harness read NPB’s own printed result and time — nothing of ours in the file, but the model could touch NPB’s timer or check, so the harness must refuse a trial that changes those lines; <em>(b)</em> move <code>main</code> into a second file as we did for the loops — cleaner for us, but the program is then no longer the file RepoOMP used. I would take (a): it keeps the programs identical to RepoOMP’s, which the later comparison with RepoOMP needs anyway.</li>"
         "<li><strong>Whether the model is ever asked there.</strong> A refresh happens only after a rewrite is kept. RepoOMP made these files by deleting the pragmas from NPB’s parallel code, and DiscoPoP already reports 5 parallel loops in EP and 19 in CG. If every hot loop already has one, the agent never asks the model, nothing is profiled a second time, and a refresh has nothing to skip. That takes one run of the agent without a model on the package — so it waits for the package.</li></ol></div>")
P.append('<div class="card"><h3>A candidate outside the list I registered — yours to allow</h3>')
P.append("<p>The 18 loops themselves, profiled with a larger input. They need restructuring, they are packaged in the clean form, and in the pragma experiment the agent profiled them again in full 227 times — the model <em>is</em> asked there. Their profiling run is short only because the agent profiles at the smallest input size. With a larger one the run takes a minute or more, and the same trials would show what a refresh saves.</p>")
P.append("<p><strong>The case against it,</strong> and why I did not simply do it: the list of candidates was written and closed before measuring, and this is not on it. And the input size is our choice — a reader can say we made profiling slow on purpose. The answer to that is that the saving is, by construction, as large as the run is long: the experiment would show <em>how</em> the saving grows with the input a user profiles with, not that it exists on a toy input. The NPB programs do not have this weakness — their classes are NPB’s own — but they may fail on point 2.</p></div>")

P.append("<h2>Step 1: the fast refresh changes the agent's decisions</h2>")
P.append("<p>Each of the 599 saved rewrites was judged three times on the server, without a model: after a full profile, after the fast refresh, and after a second full profile — the control, which shows how much one profile of a program differs from the next.</p>")
P.append(table(["What the agent would do with the rewrite", "Rewrites"], [
    ["The same after the fast refresh as after the full profile", "541"],
    ["<strong>Kept only after the full profile</strong> — a win the fast refresh throws away", "<strong>22</strong>"],
    ["Kept only after the fast refresh", "2"],
    ["Kept after both, but with other pragmas", "34"],
    ["<em>The control: differs between two full profiles</em>", "<em>0</em>"],
]))
P.append("<p><strong>The 22 lost wins are nearly all one thing: a reduction the model created</strong> — 20 of the 22. The model rewrites the loop so that DiscoPoP can see a minimum, a maximum or a sum:</p>")
P.append(code("before the rewrite     if (a[i] < x) { x = a[i]; }\nthe model's rewrite    x = fmin(x, a[i]);\n\nafter a full profile   #pragma omp parallel for reduction(min:x)      passes every check; the rewrite is kept\nafter a fast refresh   #pragma omp parallel for firstprivate(x)       would lose the result; refused; the rewrite is thrown away"))
P.append("<p>After the fast refresh nothing was ever measured on the new line. DiscoPoP therefore sees a loop without any dependence and treats <code>x</code> as an input. The agent's own check on the clauses refuses that pragma in all 20 cases. <strong>13 of the 22 are rewrites that a trial shipped as its result.</strong></p>")
P.append("<p><strong>The 2 kept only after the fast refresh.</strong> One is a loop that records the position of the largest element: with two equal largest elements two threads could write the position at once, and the test data hold only one largest element, so no check can see it. The full profile reports no parallel loop there. The other looks like a correct pragma that the full profile blocks. Both are my reading of the code, not checked by a run; neither was shipped by its trial.</p>")
P.append("<p><strong>The 34 with other pragmas.</strong> In 27 the only difference is a <code>shared(...)</code> clause that the full profile writes and the fast refresh leaves out. OpenMP shares those variables anyway, so the programs are the same. Counted that way 31 rewrites differ, not 58.</p>")
P.append("<p><strong>No time is saved on these loops.</strong> One fast refresh takes 1.54 s against 1.75 s. But after it DiscoPoP offers many more pragmas — 1,099 against 634 — and checking them costs more than the skipped run saved: 1,758 s against 1,730 s in all.</p>")
P.append("<p><strong>Your written-down claim that the fast refresh changes no decision is refuted</strong> by the test fixed before the run: p = 0.0003, and at most 0.018 when it is counted with every other test of the thesis. With the 27 counted as the same it is still refuted as a single test (p = 0.001), but not within that whole family (0.053).</p>")

P.append('<h2 id="step2">Step 2: what the model\'s own report does</h2>')
P.append("<p>You said “ok” to the smaller set on 12 Oct. The model that wrote the rewrites was asked 136 times, for $8.53: on 116 rewrites for its report of the dependences in its own code, and on the 20 rewrites where deleting dependences had anything to ask. No call failed. Every answer was fed through the agent's own code and the rewrite was judged again.</p>")
P.append("<h3>On the 58 rewrites the fast refresh decides differently</h3>")
P.append(table(["After the fast refresh alone", "Rewrites", "With the model's report"], [
    ["A win thrown away", "22", "<strong>20 are kept again</strong>, with the full profile's pragmas — all 20 reductions. The other 2 were no reductions."],
    ["Kept, but the full profile would not keep it", "2", "<strong>Both are no longer kept.</strong> On the loop with the hidden race the model names the dependence on <code>index</code> that no test data shows."],
    ["Kept after both, other pragmas", "34", "6 now have the full profile's pragmas; 27 still differ (24 of them only in the <code>shared</code> clause that changes nothing); 1 loses its win."],
]))
P.append("<h3>On 58 of the 541 rewrites the fast refresh had right</h3>")
P.append(table(["With the model's report", "Rewrites"], [
    ["Unchanged", "47"],
    ["<strong>A win lost</strong> — the pragma is gone", "<strong>4</strong>"],
    ["Still kept, with another pragma or one loop fewer", "7"],
]))
P.append("<p><strong>Scaled to all 541, that is about 100 damaged rewrites</strong> (between 60 and 159), against the 28 the report repairs. For wins alone: about 38 lost (between 13 and 82) against 20 regained. So the report, as the agent uses it, most likely costs more than it gives back. The ranges are wide because only 58 of the 541 were asked — that was the price of the smaller set.</p>")
P.append("<h3>Why — and it is not the model's mistake</h3>")
P.append("<p>In all 12 damaged rewrites the model said that the loop is independent, as the full profile does. What damages the loop is a dependence the model reported for <em>another</em> loop. One of them:</p>")
P.append(code("10    for (int nl = 0; nl < iterations; nl++) {        the repetition loop\n12        memcpy(a_copy, a, LEN_1D * sizeof(real_t));\n14        for (int i = 0; i < LEN_1D-1; i++) {           the loop that should become parallel\n15            a[i] = a_copy[i] * c[i];\n16            b[i] += a_copy[i + 1] * d[i];\n17        }\n\nthe model's answer      LOOP 10 RAW a 15 12      true: each repetition reads what the last one wrote\n                        LOOP 10 RAW b 16 16      true, for the repetition loop\n                        LOOP 14 NONE             true: the inner loop is independent\n\nwhat the agent does     writes “line 16 depends on line 16, variable b” into DiscoPoP's file — without the loop\nwhat DiscoPoP then sees a dependence inside the inner loop; it turns the loop into reduction(+:b) on an array,\n                        which the agent's checks reject before it can run; the win is lost"))
P.append("<p>My way of adding the model's answer writes the dependence without saying which loop carries it, and DiscoPoP then counts it against the inner loop too. The answer was right; the adding is what breaks it.</p>")
P.append(WHATIF_HTML.replace("@@WHATIF_TABLE@@", table(["", "Added the agent's way", "With the changed rule"], WHATIF_ROWS)))
P.append("<h3>The opposite direction: letting the model delete dependences</h3>")
P.append("<p>Asked on 20 rewrites about 41 dependences that block a loop: the model called 16 real and 19 not real (6 unanswered, which count as real). All 19 are in four rewrites of one loop, and reading the code its reasons are right. <strong>No decision changed on any of the 21 rewrites.</strong></p>")
P.append("<p><strong>Your third claim — deleting is unsafe, adding is not — is not supported by this measurement:</strong> neither direction produced a keep the full profile would not make (0 and 0). The reason is structural: after a fast refresh there is almost nothing to delete (21 of 599 rewrites), and never on the rewrites the refresh gets wrong. The claim stays an argument about the design; it is not a measured result.</p>")
P.append("<h3>What it means</h3>")
P.append("""<ul><li><strong>The fast refresh is not adopted</strong> — the plan's rule for this outcome. It loses wins, saves nothing on the loops, and 1.5 to 7.5 % of a trial where the run is long.</li>
<li><strong>The model can report the dependences of its own code</strong> — it named the missing one for every reduction it built. That part of your second claim holds.</li>
<li><strong>The report as built does not make the fast refresh usable:</strong> it repairs 28 decisions and damages at least 60. On the whole set your second claim fails.</li></ul>""")
P.append("<h3>Reopened on 13 Oct, late</h3>")
P.append("<p>You asked why the live trials were skipped (“we just need to experiment them and see the results”) and decided: <strong>run them</strong>. You added that the fast refresh needs a benchmark that can show it saves time; on the 18 loops the run it skips is 0.08 % of the agent's time. So the live trials run on the 18 loops as the reference and on programs whose profiling run is long. I find those by measuring, without a model, what one fast refresh saves on each candidate. Nothing is launched before you have seen the set and its cost. The other two points below stand as you decided them.</p>")
P.append("<h3>Decided on 13 Oct, evening</h3>")
P.append("""<p>Your answer “ok go ahead” to the three questions below, each as I had recommended. The experiment is closed with the results above.</p>
<ol class="ask"><li><strong>Live trials (step 4): not run.</strong> They would have cost $55 to $60 and measured a setup that steps 1 to 3 already decide against. What stays unknown without them: whether the model reports better inside the conversation in which it wrote the rewrite.</li>
<li><strong>The model asked about all 599 rewrites: no.</strong> The damage among the rewrites the fast refresh had right stays a range (“between 60 and 159” of 541), not one number.</li>
<li><strong>How the agent adds the model's answer: recorded as a finding, the agent unchanged.</strong> A real repair has to tell DiscoPoP which loop carries a reported dependence; whether that can be done without changing DiscoPoP was not examined.</li></ol>
<p><strong>What the thesis says from this:</strong> the fast refresh is not adopted — the full re-profile after a kept rewrite stays — with these measured reasons; the model's report as built does not rescue it; “deleting is unsafe, adding is not” stays an argument of the design, not a result.</p>""")
P.append("<h3>Before the calls: what was shown without a model</h3>")
P.append("<p>A correct report, written by hand, gave the reduction back on three of the lost rewrites (a minimum, a sum, a maximum). A pass that built every request without sending it showed 599 requests for the report and only 21 rewrites where deleting had anything to ask. The fast refresh, taken a second time, gave the same decision on 599 of 599.</p>")
P.append("<h3>The second text, with the two sentences corrected</h3>")
P.append("<p>What the model read when it was asked to delete dependences — word for word from the agent's code, with the two sentences corrected on 12 Oct as you approved.</p>")
P.append('<div class="card"><h3>The instructions</h3>' + code(DELETION_SYSTEM) + "</div>")
P.append('<div class="card"><h3>The request</h3>' + code(DELETION_REQUEST) + "</div>")
P.append(table(["The text said", "What the agent does", "It says now"], [
    ["“You are given the variable, the loop it blocks, and the two source lines.”", "The two lines are named only where DiscoPoP recorded them. It did not in any of the 21 requests; the request then shows the loop instead.", "“You are given the variable and the loop it blocks.”"],
    ["“a dependence wrongly called spurious produces a racy parallel loop”", "The loop can then look parallel to DiscoPoP; a pragma written on it still has to pass the race check and the output check.", "“a dependence wrongly called spurious can make a sequential loop look parallel”"],
]))

P.append('<h2 id="step3">Step 3: what one fast refresh saves where the run is long</h2>')
P.append(STEP3_HTML.replace("@@TABLE@@", table(["Program", "Full profile", "Fast refresh", "Saved by one refresh", "Share of an agent trial"], STEP3_ROWS)))

P.append('<h2 id="design">The design as decided on 12 Oct</h2>')
P.append("<p>Below is the page as it was put to you on 10 Oct, with the decisions of 12 Oct.</p>")

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
P.append("<p>Word for word from the agent's code as it stands — since 12 Oct with the three sentences below corrected as approved. Nothing has been sent to a model.</p>")
P.append('<div class="card"><h3>The instructions of the report request</h3>' + code(SYSTEM) + "</div>")
P.append('<div class="card"><h3>The request itself, sent after a rewrite has passed the checks</h3>' + code("\n".join(FOLLOWUP_LINES)) + "</div>")
P.append('<div class="card"><h3>The other form: the same request appended to the rewrite instructions (no extra call)</h3>' + code(FOLDED) + "<p>I propose not to use this form: it changes the text of the rewrite request itself, so the rewrites would no longer be comparable with the pragma experiment's.</p></div>")
P.append("<p><strong>Three sentences were not exactly true of what the agent does; corrected on 12 Oct as you approved.</strong> The texts above show the corrected wording; the table shows what was changed.</p>")
P.append(table(["The text said", "What the agent does", "It says now"], [
    ["“Your rewrite was accepted and written to the file.”", "It has passed the checks and is in the file. Whether it is kept is decided afterwards, by what DiscoPoP finds in it and by its speed.", "“Your rewrite passed the checks and is in the file.”"],
    ["“The profiler will NOT be run on it …”", "Not now. Before the pragmas are written at the end, the whole program is profiled in full once.", "“The profiler has not been run on it …”"],
    ["“A dependence you omit makes a sequential loop look parallel, which is a race.”", "The loop can then look parallel to DiscoPoP; a pragma written on it still has to pass the race check and the output check.", "“A dependence you omit can make a sequential loop look parallel.” — and nothing about what follows."],
]))
P.append("<p>The honest case for leaving the third as it is: the warning pushes the model to report when unsure, which is the safe direction, and a softer sentence may make it report less.</p>")

P.append("<h2>What I asked you on 10 Oct</h2>")
P.append("""<ol class="ask"><li><strong>The design:</strong> the four steps (my recommendation), or live trials from the start.</li>
<li><strong>The three sentences:</strong> corrected as proposed, or left.</li>
<li><strong>The form of the request:</strong> a separate request after the rewrite (my recommendation), not the appended form.</li></ol>""")
P.append("<p><strong>Decided 12 Oct (\"ok i agree go ahead\"):</strong> the four steps; the three sentences corrected; the separate request.</p>")
P.append("</main>")
OUT.write_text("\n".join(P) + "\n")
print(f"{OUT}: {OUT.stat().st_size} bytes")
