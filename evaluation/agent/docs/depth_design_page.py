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
P.append("""<header><p class="k">Put to the author 13 Oct 2026 · depth trials reopened 13 Oct, late (the author: “run both”) · the benchmark is built and checked (14 Oct): three loops · your “ok” (14 Oct, 07:45 UTC) · the short test run found that the agent’s last check drops a second rewrite built on the first · your “ok” (13:23 UTC): that check repaired · the second short test run found a second defect · your “ok” (18:12 UTC): repaired too · the third short test run held the launch by my rule, though nothing in it is a defect — the launch is yours · the model writes the pragmas in the later experiments</p>
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
# ---- your third "ok" (14 Oct, 18:12 UTC): the crash check at every round, checked without a model, the third short run ----
_V8 = RES / "E08_restructuring_depth/checks/e8_fix108_verify"
_rl = json.loads((_V8 / "replay/size_replay_server_large.json").read_text())
_cen = (_V8 / "replay/crash_census.txt").read_text()
_cn = {m.group(1): (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))) for m in re.finditer(
    r"^(E3b? \w+): trials (\d+); trials whose model was told 'CRASHED at the timing size' (\d+); messages (\d+); "
    r"answers naming the stack in (\d+)", _cen, re.M)}
_cs = [c for c in _rl["cases"]]
assert _rl["timing_flags"] == ["-DLARGE_DATASET"] and [(c["as_it_stood"]["status"], c["repaired"]["status"]) for c in _cs] == [
    ("safe_deferred", "pattern_broken"), ("safe_deferred", "pattern_broken"), ("pattern_broken", "exposed")]
assert "FAIL" in (_V8 / "features_before.txt").read_text() and "ok" in (_V8 / "features_after.txt").read_text()
_S3 = RES / "E08_restructuring_depth/preflight/e8v5_smoke3"
_s3 = {}
for _tj in sorted(_S3.glob("benchmarks/*/*/*/*/rep*/trial.json")):
    _t = json.loads(_tj.read_text())
    _log = (_tj.parent / "agent.log").read_text(errors="replace")
    _head, _, _settle = _log.partition("SETTLING")
    _deeper, _depth = 0, None
    for _ln in _head.splitlines():
        _m = re.match(r"┌─ \[depth=(\d+)\]", _ln)
        if _m:
            _depth = int(_m.group(1))
        elif _ln.startswith("└─ ACCEPTED") and _depth is not None and _depth >= 1:
            _deeper += 1
    _s3[_t["arm"]] = {"t": _t, "keep": len(re.findall(r"^\s+\[keep\] ", _settle, re.M)),
                      "dropped": re.findall(r"^\s+· (.*)$", _settle, re.M),
                      "repair": re.findall(r"slower than the original: ([0-9.]+)x", _settle),
                      "size_runs": re.findall(r"D40 size run: (\w+)", _head), "kept_deeper": _deeper}
_c3 = sum(float((_r["t"].get("llm_usage") or {}).get("cost_usd") or 0) for _r in _s3.values())
P.append('<div class="card"><h3>Your “ok” (14 Oct, 18:12 UTC): the crash check now runs at every round — and the third short '
         'test run held the launch by the rule I wrote, although nothing in it is a defect</h3>')
_e3, _e3b = _cn["E3 default_v5"], _cn["E3b default_v5"]
P.append(f"<p><strong>A correction first.</strong> This afternoon I told you this crash never appeared in our saved trials of the "
         f"18 loops. That was wrong: I had counted in the agent’s log, which cuts the message to the model short. Counted in "
         f"what the model was actually sent, the check without extra rounds told the model its rewrite crashed at the timing "
         f"size in {_e3[1]} of the pragma experiment’s {_e3[0]} trials, and in {_e3b[1]} of the contrast set’s {_e3b[0]} — each "
         f"time the rewrite’s own crash, and in {_e3[3] + _e3b[3]} of the {_e3[1] + _e3b[1]} the model’s answer names the stack. "
         f"So the model writes "
         f"such arrays often, the check is what catches them, and without the repair the deeper settings would have lost "
         f"trials to this regularly — the case for launching as built was weaker than I said.</p>")
P.append("<p><strong>The repair.</strong> At every round the program with DiscoPoP’s pragmas now runs once at the size where speed "
         "is measured; a crash sends the rewrite back at once, in exactly the words the model gets without extra rounds. When "
         "the timing fails on the program <em>before</em> a rewrite, the rewrite is no longer blamed: it is kept for the later "
         "checks to decide, and the agent’s log says which program failed. That is the form “the message says which program "
         "crashed” took: the model only ever hears about its own program, in words it already reads, and the other case goes to "
         "the log — so no text the model reads is new.</p>")
P.append("<p><strong>Checked without a model.</strong> A new test of the agent fails on the agent as it stood — its 20-line program "
         "shows this afternoon’s run in miniature: the stack version kept untested, the heap version blamed twice for its crash — "
         "and passes on the repaired one: the stack version is sent back at once, the heap version kept. I also replayed this "
         "afternoon’s two-round run from its saved files, on the server, at the size it was timed at:</p>")
_lab = {"safe_deferred": "kept, untested at that size", "pattern_broken": "sent back: “crashed at the timing size”",
        "exposed": "not blamed; the log names the program before it"}
P.append(table(["The rewrite", "As the agent stood", "Repaired"], [
    ["the first rewrite (an array as long as the loop, on the stack)", _lab[_cs[0]["as_it_stood"]["status"]], _lab[_cs[0]["repaired"]["status"]]],
    ["the second rewrite (another such array)", _lab[_cs[1]["as_it_stood"]["status"]], _lab[_cs[1]["repaired"]["status"]]],
    ["the model’s heap version, at the last round", "sent back: “crashed at the timing size” — wrongly", _lab[_cs[2]["repaired"]["status"]]],
]))
P.append("<p>Alone at that size, the program before the heap version crashes and the heap version with its pragmas runs. All of the "
         "agent’s own tests pass (71 checks, 38 end-to-end tests), and no text the model reads changed.</p>")
if _s3:
    _cells = []
    for _arm in ("depth1_v5", "depth2_v5"):
        _rec = _s3[_arm]
        _t = _rec["t"]
        _sp = {k: v.get("speedup") for k, v in ((_t.get("verify") or {}).get("par") or {}).items()}
        _cells.append(["one extra round" if _arm == "depth1_v5" else "two extra rounds", str(_rec["kept_deeper"]),
                       ", ".join(_rec["size_runs"]) or "—",
                       f"{_t.get('rewrites_kept')} rewrite{'s' if _t.get('rewrites_kept') != 1 else ''}, "
                       f"{_t.get('pragmas_in_final')} pragma{'s' if _t.get('pragmas_in_final') != 1 else ''}",
                       f"{_t.get('outcome')}", " / ".join(f"{_sp[k]:.2f}×" for k in sorted(_sp, key=int)) if _sp else "—",
                       f"${float((_t.get('llm_usage') or {}).get('cost_usd') or 0):.2f}"])
    P.append(f"<p><strong>The third short test run</strong> (<code>s2251</code>, ${_c3:.2f}):</p>")
    P.append(table(["Setting", "Later rewrites kept along the way", "New run at the timing size", "In the finished program",
                    "The harness’s verdict", "Speed-up at 6 / 12 threads", "Cost"], _cells))
    _r2 = _s3["depth2_v5"]
    P.append("<p><strong>One extra round:</strong> the whole chain shipped — two rewrites and three of DiscoPoP’s pragmas, about "
             "2.4 times as fast as the original.</p>")
    P.append(f"<p><strong>Two extra rounds:</strong> the first two rewrites were kept without a speed check — by design, the speed "
             f"question waits for the last round — and made the program several times slower; the last round’s rewrite won 3.74× "
             f"against that slowed program, but the finished program still ran at {_r2['repair'][0] if _r2['repair'] else '?'}× "
             f"the original, so the agent’s final check removed it and the program stayed unchanged. That is the property of depth "
             f"we wrote down in advance, and what the experiment measures — not a defect. The new crash check ran "
             f"{sum(len(r['size_runs']) for r in _s3.values())} times and found nothing to send back this time, so its "
             f"evidence stays the test and the replay.</p>")
P.append("<p><strong>Why nothing is launched.</strong> I wrote the rule for this run before it ran: launch only if none of the "
         "defects found so far shows. My automatic check flags the two-round trial with the sign of the weakness I found this "
         "afternoon and did not repair (an earlier pragma shifting the lines the agent reads). Read by hand, it is not that: "
         "there was only one pragma, which the final speed check removed, and the rewrites then went with it, as the rule says. "
         "My sign did not foresee that case. The rule says hold, so I hold — your decision.</p>")
P.append(table(["Your choice", "What happens", "Cost"], [
    ["<strong>Launch now</strong> (recommended)",
     "The 153 trials as registered, on the repaired agent; the read-out’s sign is corrected so that such a case is read by hand. "
     "This run already showed what the short runs were for: the new check running where it should, and a chain of rewrites "
     "reaching the finished program.",
     "about $110–250; they start within minutes of your answer"],
    ["<strong>One more short run first</strong>",
     "Correct the automatic check the same way, run the two short trials again, then launch if they pass. The rule’s own path, "
     "but it would show nothing about the repair that this run did not.",
     "about $2–4 more (the last two short runs cost $3.92 and $1.90), and another round of messages"],
]))
P.append("<p class=\"ask\"><strong>How I read your answer:</strong> “ok” means launch the 153 trials now. “smoke again” means one "
         "more short run first. Until you answer, no model is called.</p>")
P.append("</div>")
# ---- your second "ok" (14 Oct, 13:23 UTC): the check repaired, checked without a model, the short test run again ----
_MAC = RES / "E08_restructuring_depth/checks/e8_fix106_verify_mac"
_after = {c: json.loads((_MAC / "replay/after" / c / "replay.json").read_text()) for c in ("depth1_v5", "depth2_v5")}
_before = {c: json.loads((_MAC / "replay/before" / c / "replay.json").read_text()) for c in ("depth1_v5", "depth2_v5")}
_vrf = {c: json.loads(next((_MAC / "benchmarks/tsvc_c5/s2251").glob(f"fix106_replay_{c[:6]}/*/rep1/trial.json")).read_text())
        for c in ("depth1_v5", "depth2_v5")}
_tally = json.loads(re.search(r"^TALLY (.*)$", (_MAC / "replay/settle_archive.txt").read_text(), re.M).group(1))
assert all(_before[c]["notes_equal_archived"] and not _before[c]["survivors"] for c in _before)
assert all(len(_after[c]["survivors"]) == 6 and not _after[c]["notes"] for c in _after)
assert all(_vrf[c]["verify"]["dump_exact"] and _vrf[c]["verify"]["dump_exact_seeded"] for c in _vrf)
_S2 = RES / "E08_restructuring_depth/preflight/e8v5_smoke2"
_s2 = {}
for _tj in sorted(_S2.glob("benchmarks/*/*/*/*/rep*/trial.json")):
    _t = json.loads(_tj.read_text())
    _log = (_tj.parent / "agent.log").read_text(errors="replace")
    _head, _, _settle = _log.partition("SETTLING")
    _deeper, _depth = 0, None
    for _ln in _head.splitlines():
        _m = re.match(r"┌─ \[depth=(\d+)\]", _ln)
        if _m:
            _depth = int(_m.group(1))
        elif _ln.startswith("└─ ACCEPTED") and _depth is not None and _depth >= 1:
            _deeper += 1
    _s2[_t["arm"]] = {"t": _t, "keep": len(re.findall(r"^\s+\[keep\] ", _settle, re.M)),
                      "dropped": re.findall(r"^\s+· (.*)$", _settle, re.M),
                      "repairs": re.findall(r"^\s+\[(?:repair|revert)\] (.*)$", _settle, re.M),
                      "kept_deeper": _deeper}
P.append('<div class="card"><h3>Your “ok” (14 Oct, 13:23 UTC): the check is repaired — and the second short test run found a second defect; nothing more is launched</h3>')
P.append("<p><strong>The repair.</strong> A rewrite now stays when a rewrite kept after it was built on it — the later one changed a "
         "loop the earlier one produced, or cannot be applied without it. Nothing else in the check changed: a rewrite that "
         "nothing was built on is dropped as before, and the finished program is still judged against the original.</p>")
P.append(f"<p><strong>Checked without a model.</strong> I rebuilt this morning’s two test runs from their saved files and ran them "
         f"through the agent’s last check. As the check stood, it gives exactly what happened this morning — everything removed. "
         f"With the repair, both keep all six changes, and the harness finds both finished programs giving exactly the original’s "
         f"results ({_after['depth1_v5']['pragmas_in_finished']} and {_after['depth2_v5']['pragmas_in_finished']} of DiscoPoP’s "
         f"pragmas in them). All of the agent’s own tests pass, and a new test fails on the old check and passes on the repaired one.</p>")
P.append(f"<p><strong>In all our saved trials</strong> the old check broke something this way in {_tally['trials']} trials. In "
         f"{_tally['either']} a later rewrite was built on the one it dropped — the repair acts there. In none of the pragma "
         f"experiment’s 90 trials, so nothing reported so far changes. The other {_tally['neither']} (all on Rodinia "
         f"<code>bfs</code>, in an older experiment) are a <strong>different weakness</strong>: when the agent applies DiscoPoP’s "
         f"pragmas one after another, it identifies a loop by its text at line numbers an earlier pragma has already moved, so a "
         f"rewrite can look useless although its loop did get a pragma. I have not repaired it — that is your decision — and wrote "
         f"down beforehand: if it showed in the second test run, nothing more would be launched.</p>")
if _s2:
    _cells = []
    for _arm in ("depth1_v5", "depth2_v5"):
        _rec = _s2[_arm]
        _t = _rec["t"]
        _sp = {k: v.get("speedup") for k, v in ((_t.get("verify") or {}).get("par") or {}).items()}
        _cells.append([f"one extra round" if _arm == "depth1_v5" else "two extra rounds", str(_rec["kept_deeper"]),
                       f"{_t.get('rewrites_kept')} rewrite{'s' if _t.get('rewrites_kept') != 1 else ''}, "
                       f"{_t.get('pragmas_in_final')} pragma{'s' if _t.get('pragmas_in_final') != 1 else ''}",
                       str(len(_rec["dropped"])), f"{_t.get('outcome')}",
                       " / ".join(f"{_sp[k]:.2f}×" for k in sorted(_sp, key=int)) if _sp else "—",
                       f"${float((_t.get('llm_usage') or {}).get('cost_usd') or 0):.2f}"])
    P.append(table(["Setting", "Later rewrites kept along the way", "In the finished program", "Changes the last check dropped",
                    "The harness’s verdict", "Speed-up at 6 / 12 threads", "Cost"], _cells))
P.append("<p><strong>One extra round:</strong> the second rewrite reached the finished program, with two of DiscoPoP’s "
         "pragmas; the program runs at about the original’s speed.</p>")
P.append("<p><strong>Two extra rounds: a second defect.</strong> The first rewrite moved a value into a temporary array as "
         "long as the loop, placed on the stack — 256 KB at the small size the agent tests with, 256 MB at the size where "
         "speed is measured, far beyond the 8 MB stack the server allows. When a deeper round is allowed, the agent does "
         "not time the earlier rounds’ rewrites (the speed question waits for the last round), so the crash went unnoticed. "
         "At the last round every new rewrite is timed against the program before it — which crashes — and the crash is "
         "reported to the model as its own. The model even named the cause and moved the array to the heap; that program "
         "gives exactly the original’s results, and it was turned back all the same. In the end no pragma could be timed, "
         "nothing parallel was kept, and the last check rightly left the program unchanged.</p>")
P.append("<p>The repaired check was not needed in either run — no chain this time had a kept rewrite on a dropped one — so "
         "the replay without a model remains where it is shown. The run cost $3.92, not the $1–2 I said: the two-round run "
         "spent 8 calls at its last round on attempts that could not pass.</p>")
P.append(table(["Your choice", "What happens", "Cost"], [
    ["<strong>Repair this too</strong> (recommended)",
     "The crash check runs at every round: a rewrite that crashes at the measuring size is sent back at once, as at depth "
     "0, and the message says which program crashed. Checked without a model first (a test that fails before and passes "
     "after; this run’s two-round trial replayed), one more short test, then the 153 trials as planned. The repaired "
     "agent is then the one version for everything that remains.",
     "about $4 more, then about $110–250 (the two-round setting may cost more); 1–2 hours before the launch"],
    ["<strong>Launch as built</strong>",
     "The 153 trials now, with the repaired last check. It is what “the agent as built” meant, and the read-out counts "
     "how often this happens. But wherever it does, a deeper setting loses the trial to a crash blamed on the wrong "
     "rewrite, and the comparison on the three loops cannot be read.",
     "about $110–250"],
]))
P.append("<p class=\"ask\"><strong>How I read your answer then (you said “ok” at 18:12 UTC):</strong> “ok” means repair the crash check as described, check "
         "it without a model, run the short test once more, and then launch the 153 trials. “launch as built” means the 153 "
         "trials now. Until you answer, no model is called.</p>")
P.append("</div>")
P.append('<div class="card"><h3>The short test run found a defect in the agent — nothing more is launched (14 Oct, morning)</h3>')
P.append("<p>After your “ok” I wrote the design down before any trial and ran each new setting once on <code>s2251</code> ($1.10). "
         "<strong>The extra rounds work:</strong> with one extra round the model rewrote the loop a second time and the agent kept it "
         "(1.76× faster than the program before it); with two extra rounds it kept three rewrites in a row, the last at 2.69×; "
         "DiscoPoP’s pragmas were then applied, each 1.2× to 1.9×.</p>")
P.append("<p><strong>Then the agent’s last check threw everything away, and both runs ended with the program unchanged.</strong> "
         "That check keeps a rewrite only if a final pragma lands on a loop that rewrite itself produced. The second rewrite "
         "reshapes those loops, so the pragmas land on <em>its</em> loops; the first rewrite then looks useless and is removed, and "
         "the second, built on it, can no longer be applied. So the agent as built cannot deliver a second rewrite that reshapes "
         "what the first one produced — and that is what the second round does here, and on the 18 loops too, where it is "
         "asked about the same repetition loop again.</p>")
P.append("<p>It is not new: at depth 0 it happened where a loop sent back to the model was rewritten on top of a kept rewrite — "
         "4 trials of the main comparison on <code>s331</code> (since replaced) and a few in older runs; <strong>never in the 90 "
         "trials of the pragma experiment</strong> (the last check removed nothing in any of them), which are the depth-0 "
         "comparison for the 18 loops, so nothing reported so far changes.</p>")
P.append(table(["Your choice", "What happens", "Cost"], [
    ["<strong>Repair the check</strong> (recommended)",
     "A rewrite stays when a later kept rewrite was built on it. Checked without a model first (the agent’s tests; the two "
     "test runs replayed through the new check), then one more short test, then the 153 trials as planned. The repaired agent "
     "is then the one version for everything that remains.",
     "about $1–2 more, then about $110–250 as before; 1–2 hours before the launch"],
    ["<strong>Run as built</strong>",
     "The 153 trials now, on the agent as it is. It is what “the agent as built” meant, and the result is a finding about it. "
     "But it pays for what two runs already show, and the experiment’s question — does a second round help? — cannot be answered.",
     "about $110–250"],
]))
P.append("<p class=\"ask\"><strong>How I read your answer then (you said “ok” at 13:23 UTC):</strong> “ok” means repair the check as described, check it without a "
         "model, run the short test again, and if the extra rounds now reach the final program, launch the 153 trials. "
         "“run as built” means the 153 trials now, unchanged. Until you answer, no model is called.</p></div>")
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
P.append("<h2>How I read your answer before the test run (14 Oct, early morning — you said “ok”)</h2>")
P.append(f"""<p class="ask"><strong>“ok” means:</strong> the depth experiment starts, with DiscoPoP writing the pragmas as registered — first each new setting once on one loop, to see that a second round really happens (a few dollars); then the three new loops (45 trials) and the 18 loops (108 trials), about ${r10(new_lo + C_COST[0])} to ${r10(new_hi + C_COST[1])} together. The two loops that cannot be won are <em>not</em> run. The fast-refresh trials do <em>not</em> start — their benchmark is not ready; that is on the other page.</p>
<p>Anything else — only the new loops, the two unwinnable loops as well, more loops built for the purpose, a different count for <code>s221</code> — please say so. Until you answer, no model is called.</p>
<p class="lede">Earlier on this page: your “ok” of 13 Oct (no depth trials) and your “run both” later that night, which reversed it; then your remark that depth needs its own benchmark, which is what the first card answers.</p>""")
P.append("</main>")
OUT.write_text("\n".join(P) + "\n")
print(f"{OUT}: {OUT.stat().st_size} bytes; estimates: B ${B_COST[0]:.1f}–${B_COST[1]:.1f}, C ${C_COST[0]:.1f}–${C_COST[1]:.1f}; per call ${per_call:.3f}; "
      f"per trial ${per_trial:.2f} / ${per_trial_c:.2f}; profiles ratio {dp['full_reprofiles'] / mo['full_reprofiles']:.2f}")
