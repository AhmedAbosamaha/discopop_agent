# Prompt review — prioritized change plan (28 Sep 2026)

Produced by a read-only review (four lenses and a verifying synthesis) of the real prompts the model received (ORDER-2 pilot, V3 pilot s211/s244, E2-B1 smoke s151/bfs). Nothing here is adopted yet: each change is the author's decision and is tested by a pilot before adoption (rule: pilot the mechanism first).

## Status (28 Sep evening)

- **Stage 0 done** (THESIS_EXPERIMENTS §6, 28 Sep): M1, M2, M3 and the must-changes D1, D2, D3, D5, D10, A1 as prompt version 2 (`--prompt-version 2`; default 1). Every registered arm unchanged except `bare_llm_nospeed` (M3), proven by `tools/prompt_manifest.py`; `tools/test_prompt_v2.py` passes.
- Known limit of v2's D5: a scalar whose RAW records all cross the region's edge is left out of the dependence list; the digest still names it (its scalar line lists every scalar RAW).
- Not yet: D4 and the 'should' items; Stage 1–3 pilots (pre-registered before they run, after E2-B1's re-runs).

## Summary

Scope: one prioritized change set for the prompt the restructuring model receives. The system prompt is built in llm/prompts.py (plus twin._given/_judged and bare_llm), the request in llm/request.py, and the evidence in llm/render.py. The repository root is /Users/ahmedsamir/discopop_agent. Every claim below was checked against the code, the samples and the archived pilot calls. I dropped or corrected claims I could not confirm.

**What the samples show**
- **The direction of a dependence never reaches the model.** The deps arrow prints sink→source ('v at lines 6→7', although line 7 writes v and line 6 reads it). In the first ORDER-2 pilot, 30 of 30 X answers kept the textual order, in every arm, so they failed.
- **The text tells the model to delete a RAW.** The blockers say 'it must be removed' and the contract says 'The blocking dependence has to be gone'.
- **The generic array_note prescribes the wrong fixes for a RAW.** It offers a second buffer, or red-black sub-passes, which gave the s211 odd/even splits. All 5 Y failures in the evidence arms (full 3, no_note 2) are buffer or snapshot rewrites. Y/none had no buffers and scored 10/10.
- **Several evidence lines are false.**
  - c, d and v are called 'loop-carried RAW' in s211/s244, though the region never writes c or d and v is another function's parameter.
  - An array is tagged 'read-only: never a source of a dependence' while a RAW names it.
  - When the only RAW is inside a called function, the digest says the blocker is 'structural (control flow)' (s151).
  - In bfs region 2 the target loop is listed as 'already parallel inside'.
  - After a TSan timeout, the requeue text asserts an unobserved dependence.
- **The model-alone speed-off prompt leaks.** bare_llm_nospeed (E2-B1, now running) reads 'The program was profiled … iteration counts in the evidence'. I rendered it to confirm.
- **The pilot instrument has a bug.** It passes the kernel id as failure_reason, so the evidence arms carry '### What went wrong\nk17' and the none arms do not. Clean contrasts: full vs no_note, and order vs full. Confounded: full vs none, and sonnet_full vs sonnet_none.

**The order2b pilot**
summary.md does not exist yet: the sonnet_full arm is still running and sonnet_none has not started. I compiled and ran the saved answers on both inputs in the scratchpad. This is an output check only, not the pilot's scoring, which also needs DiscoPoP's re-profile.
- X/order: 8/10 answers put line 7's loop first and give the original output, against X/full 0/10.
- Y/order: 10/10 give the original output.
- Sonnet with today's evidence (3 finished X calls): none splits the loop in the right order. Two build an inspector-executor level schedule and one keeps the loop.

So a restatement generated from DiscoPoP's records moves Haiku, and today's rendering does not.

**Conflicts between the reviews, and how I resolved them**
1. **Hedging DiscoPoP's loop attribution.** The misleading lens wanted the header to say the attribution 'can be wrong'. The actionable-evidence lens wanted the agent to cross-check against subscripts. I rejected both.
   - The standing user rule says DiscoPoP's analysis is never hedged in the prompt and its defects are fixed in DiscoPoP.
   - An agent-side subscript analyser would also change what the evidence arm measures.
   - Instead, the s244 inner-loop blocker becomes a DiscoPoP item (M4). The V3 pilot and E2 A+B ran on the explorer from before the B4 fix. The 20 Sep t0_11 profile charges s244's RAW to the nl loop.
2. **Rewrite or drop array_note.** Stage 1 empties it but keeps the section name. Stage 2 fills it with a generated order statement, only where DiscoPoP itself names the carrying loop.
   - The pilot's rule, applied to s244's records ('a 137→135', 'b 135→136'), would demand a wrong fission. Both RAWs are carried by nl.
   - On s211 it is right. Textual order cannot tell the two apart.
3. **Rules the structure lens found.** A change to shared text is a new prompt version for every arm. Nothing in the shared or evidence text changes while E2-B1 runs.
4. **Abstention and cost wording.** Abstention conflicts with the L3/L4 rule (the model always aims for a parallel version), so I don't recommend it for the agent. The buffer and cost wording is a speed question, and D40 put cost advice into feedback, so it is marked 'could'.

**Arm codes used below**
- A: every arm (agent, twins, bare mirror; the bare 'contract' prompt where noted).
- B2: the no-pragma agent arms and their twins.
- C: the evidence arms' system prompt, plus the twin._given copy.
- D: evidence-arm requests, plus their twins. The none arms and bare stay byte-identical.
- F: agent feedback only.
- P: the pilot only.

## Changes

### [must] M1 — Pilot instrument: pass the first-attempt reason, and put the note before the Task heading (evidence_pilot.py)

**What.** evaluation/agent/tools/evidence_pilot.py:230
- Before: `ev = assemble(loop, dp / "profiler", p["id"])`.
- After: `ev = assemble(loop, dp / "profiler", FIRST_REASON)`, with `from discopop_agent.twin import FIRST_REASON`.
- The request then reads '### Why this region is here\nDiscoPoP found no applicable parallelism pattern for this region', as on the agent's and the twins' first attempts.

evidence_pilot.py:246
- Before: `cut = req.rfind("Edit `")`. This lands after the '### Task' heading, so the request reads '### Task\n### What the observed dependence means…'.
- After: `cut = req.rfind("### Task")`. The note becomes the last evidence section, which is where D4 would render it.

Record both points as deviations of evidence_pilot_order2 and evidence_pilot_order2b before either is read out.

**Why.** - assemble()'s third positional parameter is failure_reason (evidence/package.py:25-29).
- order2_requests.json: X/full, X/no_note, Y/full and Y/no_note contain '### What went wrong\nk17' (or k42); the none arms do not.
- order2b/requests.json: present in X/order, X/sonnet_full, Y/order and Y/sonnet_full; absent in the sonnet_none arms.
- Contrasts that survive: full vs no_note, and order vs full.
- Confounded: full vs none (Y 7/10 vs 10/10) and sonnet_full vs sonnet_none.

**Arms.** P only. No agent, twin or bare text changes.

**Risk.** None to production. The archived pilots stay valid as results of instrument v1, with the deviation recorded.

**Test.** - Re-render with requests().
- Assert that no request contains 'What went wrong' and that none contains '### Task\n###'.
- Diff against the archived requests.json: only those lines may differ.

### [must] M2 — Guard every derived prompt text before any shared block is edited

**What.** (1) Make each exact-substring .replace() that derives an arm's text fail loudly when its target is absent. Use a helper that raises instead of returning the input. The sites:
- prompts.py:331-333 (_ASK, speed off)
- twin.py:147 (EARLIER_TURN), 153-155 (_ASK, speed off) and 163 (SPEED_ONE_THREAD)
- bare_llm.py:91 ('not only the one that was profiled'), 95-97 (granularity, speed on), 110-117 (three _ASK_ANNOTATE replaces) and 135-137 (two _goal replaces)

(2) Add a render-hash check. For every arm in config/arms.json, render the system prompt and the first request on test_features' evidence fixture and on the ORDER-2 k17/k42 profiles, and store a manifest. A change must declare which arms it touches, and the set of changed hashes must equal that set.

(3) Add the existing feature checks to the harness test list in CLAUDE.md: check_twin_prompt, check_bare_llm, check_bare_speed_off and the gate-facts checks (test_features.py ~2470-2510).

**Why.** - Several anchors contain wrapped line breaks, for example 'race-free, output-preserving,\nand faster than the sequential build.'. A rewrap makes the replace a silent no-op, and the speed-off arms would keep a speed goal.
- check_twin_prompt compares agent and twin, which would both no-op the same way, so it cannot catch this.
- M3's leak is exactly such an unguarded replace.
- Every A-, B2- and C-change below edits one of these anchors.

**Arms.** No text changes. The check proves which arms a later change touches.

**Risk.** Low. A replace that is conditional on purpose must be marked as such.

**Test.** - On today's code every assertion passes except bare_llm.py:95-97 under mirror_gate(False). That is M3, which should fail until it is fixed.
- Build the hash manifest once, before any other change.

### [must] D1 — Blockers: drop 'it must be removed', say what each type means, use source names

**What.** render.py fmt_blockers

Header (render.py:536-537)
- Before: 'DiscoPoP identified these exact dependences as what blocks Do-All — target these specifically:'
- After: 'DiscoPoP's Do-All check stopped at these.  Each names the variable and the loop it blocks; the line pairs are in the dependence list, when it is shown.'

Dynamic note (render.py:541)
- Before: 'dynamic — a real, observed dependency; it must be removed'
- After, chosen by dep_type:
  - RAW: 'observed: an iteration of this loop read a value an earlier iteration wrote — that value must keep reaching its reader, so the dependence can be moved out of the loop you make parallel, not deleted'
  - WAR: 'observed: an element was overwritten after an earlier iteration read its old value — a copy of the old values or a second array removes it'
  - WAW: 'observed: two iterations write the same element — the write that comes last in the original order must survive'

Static note (render.py:543)
- Before: 'static — may be resolvable by privatizing / first-writing the variable inside the loop'
- After: 'static: not observed on the profiling input, and DiscoPoP could not rule it out from the code — a scalar every iteration writes before reading is removed by declaring it inside the loop body'

Name (render.py:546)
- Before: `var = str(b.get("var_name", "?"))`
- After: `var = _classify_var(raw)[0]`, with a trailing '[]' removed. It renders 'RAW on `v`' and 'RAW on `h_cost`'.

Not adopted: the header 'that can be wrong … check each one against the subscripts' and the subscript cross-check (see the resolution in the summary). fmt_blockers is also used in the agent's 'no_pattern' feedback (phases/verdicts.py:383), so the new wording reaches that retry too.

**Why.** - ORDER-2 X/full reads '- RAW on `GEPRESULT_v` loop-carried (loop at line 5) [dynamic — a real, observed dependency; it must be removed]'.
- The replies echo it: X_full_01 'the RAW on v is eliminated'; X_full_02 'I'm breaking the loop-carried RAW dependence on v by using a read-only snapshot … Copy v before the loop'.
- My classification of the archived answer files: all 5 Y failures in the evidence arms are buffer or snapshot rewrites, while Y/none used none and scored 10/10.
- GEPRESULT names verified: ORDER-2 'GEPRESULT_v' vs deps 'v'; bfs 'GEPRESULT__ZL6h_cost'.

**Arms.** D: evidence arms that include blockers, and their twins, which use the same _build_direct_prompt. Also F, the agent's 'no_pattern' feedback. The none arms and bare stay byte-identical.

**Risk.** - The RAW note is only as right as DiscoPoP's loop attribution. Under the V3 s244 profile (blocker 'RAW on a, loop 134', pre-B4 explorer) it would argue against the pre-loop copy, which is the correct fix inside the i loop. Pair with M4.
- The feedback wording changes too, relative to archived agent runs.

**Test.** - Re-render from the archived profiles: ORDER-2 k17/k42, v3_pilot_3 s244, s211, and the E2-B1 smoke s151/bfs.
- Assert no 'must be removed' and no 'GEPRESULT'.
- Model test only within the P2 bundle.

### [must] D2 — Dependence pairs in value-flow order, with verbs

**What.** render.py:166 (_fmt_deps)
- Before: `shown = ", ".join(f"{a}→{b}" for a, b in inside[:8])`. Here a = from_line (the sink, the later access) and b = to_line (the source, the earlier access); see deps.py:6-8 and 131-151. It renders 'v [array element] at lines 6→7', although line 7 writes v and line 6 reads it.
- After: one rule for every class, earlier access → later access (to_line → from_line), with verbs:
  - RAW: f"line {b} writes → line {a} reads"
  - WAR: f"line {b} reads → line {a} overwrites"
  - WAW: f"line {b} writes → line {a} overwrites"
  - Example: '`v` [array element]: line 7 writes → line 6 reads'.

Sub-header (render.py:94)
- Before: '(grouped per variable, each tagged [array element] or [scalar])'
- After: '(grouped per variable, each tagged [array element] or [scalar]; each pair is the earlier access → the later one)'

RAW label (render.py:95)
- Before: 'RAW — read-after-write (the blocking ones)'
- After: 'RAW — read-after-write (a value written by one access and read by a later one)'

fmt_blockers:551
- Before: f"line {src} → {snk}" (source is the earlier access).
- After: the same verbs.

**Why.** - ORDER-2 X: 'v … at lines 6→7'. The profile record '43@31 NOM RAW 79@37|GEPRESULT_v' has sink 43 on line 6 and source 79 on line 7.
- ORDER-2 Y: 'u … at lines 7→6', where line 7 only reads u.
- In the first pilot, 30 of 30 X answers kept the textual order (line 6's loop first) in every arm, so the direction never got through.
- The order2b 'order' arm stated the same record in words; 8 of its 10 X answers put line 7 first (my check of the saved files).
- 'the blocking ones' is false for a RAW within one iteration (s244: 'b … 137→136').

**Arms.** D.

**Risk.** Low: the information is unchanged. The arrow alone may be too weak; P1's arrow_only arm measures that.

**Test.** Unit test from the archived profiles:
- k17 renders 'line 7 writes → line 6 reads'.
- k42 renders 'line 6 writes → line 7 reads'.
- s211 renders 'line 136 writes → line 135 reads'.
- Plus one synthetic Dependency per class.

### [must] D3 — Empty the generic array_note; keep the section name; remove the digest's pointer to it

**What.** render.py:507-526 (_array_dep_note)
- Before: '### Choosing the fix for this array dependence … 1. WHICH LOOP carries it … then the answer is a pragma on THAT loop, not a rewrite.  2. … can a value written during one sweep be read again LATER IN THE SAME SWEEP?  - No — … Read from one buffer and write to another (or copy just the elements that are read across iterations before the sweep starts).  - Yes — … Split each sweep into ordered sub-passes over disjoint elements instead; …'
- After: return "" in stage 1 (D4 fills it later).
- Keep 'array_note' in EVIDENCE_SECTIONS, so every --evidence list, test_arms.py and the pilot's no_note arm stay valid.

Digest pointer (render.py:216-218)
- Before: '— a value moves between iterations through the data; see 'Choosing the fix' below.'
- After: deleted (D5 rewrites the line).
- Today this pointer dangles in every arm without array_note, including the pilot's no_note and E2-C's ev_without_howto_b1.

**Why.** Both branches prescribe transformations that are wrong for a RAW carried by the loop:
- The 'No' branch applies the WAR fix to a RAW. Y_full_03: 'two-buffer strategy … line 7 reads from the original u'; bfs record 0: double buffering.
- The 'Yes' branch describes red-black sub-passes. s211 V3: 'Odd pass … Even pass', wrong output; E2 had odd/even splits in 7/18 with evidence vs 0/13 without.
- Step 1 says 'the answer is a pragma on THAT loop, not a rewrite' in the no-pragma mode.
- Removing the note alone does not fix direction: X is 0/10 in no_note too. This is a harm fix, not the success lever.

**Arms.** D. E2-C's 'howto' group (ev_only_howto_b1, ev_without_howto_b1) becomes empty until D4 lands, so re-register E2-C.

**Risk.** It loses the one warning that a second buffer changes a travelling value; D10 and A1/A3 carry that instead.

**Test.** - Re-render: no 'sub-passes', 'second buffer' or 'Choosing the fix' anywhere.
- Model: the P2 bundle; the s211 replay counts odd/even splits.

### [must] D5 — Digest and deps: list only in-region pairs as RAW; state crossing values honestly

**What.** (a) Digest (render.py:205-219): build array_raw only from records with both ends inside the region.
- Before: '  - Loop-carried RAW on ARRAY ELEMENTS of: {vars} — a value moves between iterations through the data; see 'Choosing the fix' below.'
- After: '  - RAW on array elements within these lines: {vars}.'
- When some variables have only crossing records, add: '  - Values that cross the region's edge only — written outside and read here: {vars_in}; written here and read after the region: {vars_out}.'

(b) Fallback (render.py:173-176)
- Before: '(loop-carried; the profiler did not resolve exact in-region line pairs — see the Do-All blockers section)'
- After: the variable is left out of the RAW/WAR/WAW lists and appears only in the crossing line.

(c) Suffix (render.py:168-172)
- Before: '(+{crossing} with an endpoint outside the region: values produced here are consumed by later code — the rewrite must preserve them)'
- After, on RAW rows, by which end is inside: '(+N read after the region)' or '(+N written outside the region and read here)'. WAR and WAW rows get no suffix.

(d) render.py:233
- Before: 'read as (not read)'
- After: 'and not read in these lines'.

Names that occur in none of the region's lines (s211/s244 'v', pb_emit_array's parameter) go into the crossing line only.

**Why.** - s244's digest reads 'Loop-carried RAW on ARRAY ELEMENTS of: a, b, c, d, v'. c and d are only read in the kernel and written by pb_mix() (s244.c:100-101, called at line 139); v is pb_emit_array's parameter (s244.c:117).
- The fallback claims the profiler did not resolve pairs it did resolve: one end lies outside.
- s211 carries 5 fallback rows (525 chars) and 8 suffixes (976 chars), 20% of a 7,652-char request.
- The suffix tells the model to preserve 'values produced here' for c, which the region never writes.
- bfs region 2 reads 'Loop-carried RAW … h_graph_mask' next to '`h_graph_mask` is written as [tid] and read as (not read)'.

**Arms.** D.

**Risk.** Low: it removes false text. Naming the outside writer (pb_mix) needs a line→function map; that part is optional.

**Test.** Re-render s211, s244 and bfs:
- c, d, e and v are absent from the RAW list and from the digest's RAW line.
- ORDER-2 is unchanged except for wording.
- Record character counts before and after.

### [must] D10 — System prompt, evidence arms: say what a RAW is (prompts._given, and twin._given in the same commit)

**What.** prompts.py:111-118 and twin.py:88-95, byte-identical.

- Before: 'Work from that evidence rather than from what the algorithm is called.  Two things in it are easy to misread on inspection: WAR and WAW usually mean a location is reused, not that a value travels between iterations; and a dependence on a loop's own counter is never the blocker, because privatising the counter removes it.'
- After: 'Work from that evidence rather than from what the algorithm is called.  Three things in it are easy to misread.  A RAW carried by a loop is a value in transit: the reading line needs what the writing line stored, so the dependence can be moved (the writing loop finishing before the reading loop starts) but not deleted, and handing the reader a copy taken before the loop changes the result.  WAR and WAW usually mean a location is reused, and there a copy of the old values or a private variable does remove them.  A dependence on a loop's own counter is never the blocker, because privatising the counter removes it.'

_GIVEN_ITEMS 'deps' (prompts.py:79-81)
- Before: 'the dependences observed at run time (RAW / WAR / WAW, grouped per variable, tagged array or scalar, quoted against the statements they point at)'
- After: 'the dependences observed at run time (RAW / WAR / WAW, grouped per variable, each pair given as the earlier access → the later one)'.

**Why.** - The only standing guidance on reading dependences covers WAR/WAW and counters, and says nothing about RAW, the case the models broke: X_full_02's snapshot, Y_full_03's two buffers, and Y_no_note_02 'read all values u[ku[i]] into a temporary buffer before any writes to u'.
- The item text describes the rendering that D2 replaces.

**Arms.** C: the evidence arms' system prompt in both pragma modes, and the twins through twin._given. The none arms keep their 174-char text; bare is unaffected.

**Risk.** - The twin copy can drift; check_twin_prompt catches that.
- The same attribution caveat as D1.
- Adds about 280 characters.

**Test.** - check_twin_prompt.
- The M2 hash check: only the evidence arms' system prompts change.
- Model: the P2 bundle.

### [must] A1 — Contract: a dependence is moved, not deleted (shared by every arm)

**What.** prompts.py:157-161 (_CONTRACT_CLOSE), wrapped as the block is today.
- Before: '  - The original code returned unchanged — renamed, reordered, unrolled, or wrapped in an early-exit shortcut — is not an answer, and neither is a faster serial algorithm.  The blocking dependence has to be gone.'
- After: '  - The original code returned unchanged — renamed, reordered, unrolled, or wrapped in an early-exit shortcut — is not an answer, and neither is a faster serial algorithm.  The loop you make parallel must no longer carry a dependence between its iterations, but a dependence is moved, not deleted: a value one iteration writes and a later one reads must still reach that read (for example, the writing loop finishes before the reading loop starts).  The exception is an accumulator whose running value feeds nothing but its own total: that may become a reduction.'

The agent's re-prompt for an unchanged file (phases/phase_a.py:402-403)
- Before: 'That is not an answer: the blocking dependence has to be gone.'
- After: 'That is not an answer: a loop in the region has to end up with iterations that no longer depend on each other, while the program computes what it computed before.'

Freeze today's _CONTRACT_CLOSE for bare_llm's --prompt contract (bare_llm.py:165), so E1-bare stays reproducible.

**Why.** - 'has to be gone' frames every dependence as something to delete, and the replies echo it while they cut a value flow. X_full_01: 'the RAW on v is eliminated'. X_order_01 even had the order note: 'Remove blocking dependence … u updates using original v values', in the wrong order.
- In the mirror, 'The blocking dependence' has no referent, because nothing there names one. The new sentence needs none.
- The carve-out keeps Reduction, a target pattern, allowed without claiming that a float reduction is byte-identical; the gate decides that.

**Arms.** A: agent arms (both modes), twins (twin._system uses _contract) and the bare mirror; not the frozen bare 'contract' prompt. The re-prompt: F. All three columns stay matched within the new version.

**Risk.** - It changes every arm, so archived E1/E1c/E2/E2-B1 results belong to prompt v1.
- Longer text; the model may become more conservative, with more unchanged answers.
- Deploy only after E2-B1 finishes.

**Test.** - check_bare_llm (the mirror's contract must equal the agent's), check_twin_prompt, check_bare_speed_off.
- Model: P3 (the none arm isolates shared text), then the P2+P3 bundle.

### [must] M3 — The model alone, speed off: remove the 'profiled … evidence' leak and test for it

**What.** bare_llm.py:95-97 replaces only the speed-on granularity sentence.

Add a second replace for the speed-off text (prompts.py:195-198):
- Before: 'The program was profiled on a deliberately\nsmall input, so the iteration counts in the evidence are far below what\nthe code runs in practice, and its speed is measured afterwards at full\nsize'
- After: 'Its speed is measured afterwards, at sizes far larger\nthan any you can see'.

Give check_bare_speed_off (test_features.py:1941-) the mirror's leak list: 'DiscoPoP', 'profil', 'evidence', 'RAW', 're-profile'. Today it has none. If A1 is not adopted, also drop 'The blocking dependence has to be gone.' from the mirror under D37.

**Why.** - I rendered bare_llm._system('mirror', mirror_gate(False)) in the venv, without any model call. The 6,567-character prompt contains 'The program was profiled on a deliberately small input, so the iteration counts in the evidence are …'.
- check_bare_llm's leak loop (test_features.py:1921-1924) runs only on the speed-on mirror.

**Arms.** The mirror only: bare_llm_nospeed, the E2-B1 model-alone arm. The fix restores D37.

**Risk.** None to other arms. E2-B1 is running with the leak: do not change it mid-run, and record a deviation for bare_llm_nospeed now. Whether that arm is re-run (single calls, cheap) is the author's call.

**Test.** - Render mirror_gate(False) and grep for profil|evidence.
- The extended check fails on today's code and passes after the fix.

### [should] M4 — DiscoPoP, not the prompt: check the s244 inner-loop blocker on the fixed explorer; have doall_prevented name line pairs

**What.** No prompt text.

(1) On the server, re-run the fixed explorer (B4, B9, B10, B13, B15) on these profiles, with no model:
- the archived s244 profile of v3_pilot_3
- E2's s244 profiles (e2c_ab_2)

Then compare doall_prevented.json:
- V3 names 'RAW on a, loop 134' (the inner i loop) and 'RAW on b, loop 133'.
- t0_11_classes_a (20 Sep) names only 'RAW on a, loop 136', which is the nl loop.
- In the i loop no iteration reads an element of a that an earlier iteration of the same sweep wrote: line 137 reads a[i+1] before line 135 overwrites it at i+1, which is a WAR.
- If the inner-loop blocker persists on the fixed explorer, log it in docs/DISCOPOP_BUG_REPORTS.md (B14 is the nearest known shape) and fix it.

(2) Have explorer/…/new_do_all_detector.py fill source_line/sink_line in doall_prevented.json. Today they are 'None' for these entries (FIXES.md:829). The line ids would come from the task graph, so DiscoPoP itself states which line pair carries the dependence for each blocked loop.

**Why.** - User rule: DiscoPoP's analysis is never hedged in the prompt, and its defects are fixed in DiscoPoP and used in every arm.
- D1's RAW note, D10 and D4 are only as right as DiscoPoP's loop attribution.
- E2 A+B and the V3 pilot ran before B4 (the explorer's output varied between runs on one profile) was fixed on 26 Sep (commit f9fab174).
- (2) is the only route to a correct order statement in regions that also contain the repetition loop.

**Arms.** DiscoPoP is shared by every arm, including DiscoPoP alone.

**Risk.** (2) is a new explorer output, not a bug fix. Keep it additive: the agent falls back to today's rendering when it is absent.

**Test.** - The explorer only, no model: doall_prevented.json for s244 and s211 on the fixed DiscoPoP.
- For (2): an end-to-end test that k17 yields source 7 → sink 6 for v on loop 5.

### [should] D4 — Stage 2: a generated order statement in the array_note section, only where DiscoPoP names the carrying loop

**What.** The _array_dep_note body, under the section name array_note, rendered as the last evidence section before '### Task'.

One bullet per RAW record where the reader s = from_line differs from the writer w = to_line and both are inside the target. Generate it only when DiscoPoP gives the carrying loop:
- either doall_prevented names the pair for loop L (after M4-2),
- or the blockers name x on the innermost loop L containing both lines, and name no other loop inside the region for x.

Text: '### What the observed flow means for a rewrite\n  - `{x}`: line {w} (`{stmt_w}`) writes it and line {s} (`{stmt_s}`) reads what it wrote; DiscoPoP names the loop at line {L} as carrying it.  If you split that loop between these lines, the loop holding line {w} runs to completion first; giving line {s} `{x}`'s values from before the loop changes the result.'

When the reverse record also exists (reader w, writer s): '  - Lines {w} and {s} feed each other, so splitting the loop between them changes the result.'

No bullet for a same-line pair, and no 'EARLIER iteration' claim: the rendered records carry no iteration distance.

Rejected: the actionable lens's subscript tiers (a)-(c) and its 'blocks of d / chains' rules. They add an agent-side dependence analysis to what E2 defines as DiscoPoP's evidence, and they can contradict DiscoPoP (user rule).

**Why.** - The pilot's generated note took Haiku on ORDER-2 X from 0/10 to 8/10 answers with the right order and the original output on both inputs, and Y to 10/10. This is my scratchpad compile-and-run check, not the pilot's scoring, which also re-profiles; summary.md is not written yet.
- Applied without the gate to s244's records ('a 137→135', 'b 135→136'), the rule demands '135's loop first' and '136's loop first'. Both RAWs are carried by nl, so that split gives the wrong output.
- On s211 ('b 135→136', carried by i) the rule is right.
- Textual order cannot tell these apart; only the carrying loop can, hence the gate.

**Arms.** D. E2-C's howto group then measures this text; re-register.

**Risk.** - Wrong advice if the attribution is wrong or ambiguous (the s244 shape).
- Without M4-2 it rarely fires on TSVC, because every region contains the nl loop.

**Test.** - A truth table with no model: for the 18 E2 TSVC loops, ORDER-2 k17/k42 and s151/bfs, hand-derive the correct fission order inside the target loop. Every generated bullet must agree, and none may fire on s244-like records.
- Then P1's order_clean and the P4 replays.

### [should] A2 — Plan instruction: name the writer and the reader instead of 'removing'

**What.** prompts.py:350-353 (_PLAN_SPEC)
- Before: 'Before the code, a short plain-text plan: which dependence you are removing and\nhow, and any bound or initial value you had to re-derive because the new\nschedule visits the data in a different order.  A few lines is enough.'
- After: 'Before the code, a short plain-text plan: which dependence keeps the loop\nsequential; if it carries a value from one iteration to a later one, which\nline writes it, which line reads it, and how your version still delivers it;\nand any bound or initial value you had to re-derive because the new schedule\nvisits the data in a different order.  A few lines is enough.'

**Why.** - The plans copy the heading: X_full_10 '**Dependence to remove**: Loop-carried RAW on `v`'. 56 of 60 ORDER-2 plans use remove/eliminate/break (coarse regex, per the task lens).
- None of the plans states who feeds whom, which is the fact ORDER-2 turns on.

**Arms.** A: every arm, in every edit mode. The mirror includes _PLAN_SPEC, and check_bare_llm requires it to be the agent's exact text, which still holds.

**Risk.** Longer plans; a new version for every arm.

**Test.** - check_bare_llm and check_twin_prompt.
- Within P3: the share of plans that name a writer→reader pair in the correct direction (X: 7→6; Y: 6→7).

### [should] A3 — Checklist item 1: say what follows from 'a value moving'

**What.** request.py:91-92 (_task_checklist)
- Before: '  - Which dependence is actually blocking this, and is it a value moving\n    between iterations or just a location being reused?\n'
- After: '  - Which dependence is actually blocking this, and is it a value moving\n    between iterations or just a location being reused?  A moving value\n    (one iteration writes it, a later one reads it) must still reach that\n    read — if you split the loop, the loop that writes it runs first.  A\n    reused location (read, then overwritten by a later iteration) is what a\n    copy of the old values or a private variable fixes.\n'

Keep the opening words, which check_bare_llm pins.

**Why.** - The ORDER-2 replies answer the question correctly ('a value moving') and then break the flow anyway.
- This is the one version of the direction rule that needs no evidence and reads the same in every arm.

**Arms.** A: every arm, including evidence=none, the twins, and the mirror through _task_checklist. Only --prompt-omit checklist lacks it.

**Risk.** On the none arm it cannot fix ORDER-2 X, whose direction is unknowable from the text. It can only curb the snapshot shortcut.

**Test.** - check_bare_llm and check_bare_speed_off.
- P3 on the none arm: Y must not drop, and snapshot/buffer rewrites should fall.

### [should] A4 — Success in the right order: first the output, then the pattern (no-pragma ASK, goal, and the 'merely' paragraph)

**What.** _checked paragraph (prompts.py:230-234)
- Before: 'Steps 1-2 run your code sequentially, so passing them says nothing about\nstep 4, which runs it with iterations overlapping in arbitrary order.  A\nloop you intend to be parallel has to give the same result whatever order\nits iterations run in — that, not merely reproducing the output in serial,\nis what is being asked for.'
- After: 'Both halves are required.  Steps 1-2 run your code in order and must\nreproduce the original output; step 4 runs the loop with iterations\noverlapping in arbitrary order and must give that same output again.\nIterations made independent by changing which value a statement reads pass\nthe race check and fail step 2.'

twin.py:136-139, in lockstep
- Before: '…that, not merely reproducing the output\nin serial, is what is being asked for.'
- After: '…Both are required: the program has to reproduce the original output, and a\nloop you intend to be parallel has to give that same output whatever order\nits iterations run in.  Iterations made independent by changing which value a\nstatement reads are race-free and still wrong.'

_ASK success sentence (prompts.py:56-59)
- Before: 'You have succeeded when DiscoPoP finds one of the four patterns it can\nexploit — Do-All, Reduction, Pipeline, Task-parallel — in the lines you\nchanged, and the pragma it then generates is race-free, output-preserving,\nand faster than the sequential build.'
- After: 'You have succeeded when, in this order: your code, run as written, gives\nthe original program's output; DiscoPoP then finds a Do-All or Reduction\nin the lines you changed; and the pragma it inserts there is race-free,\nkeeps that output, and is faster than the sequential build.'
- Update the speed-off replace targets in prompts.py:331-333 and twin.py:153-155 to the new line breaks. M2's assertion catches a miss.

_goal(False) (request.py:43-46)
- Before: 'restructured so that, after re-profiling, DiscoPoP detects a genuinely parallel pattern (Do-All, Reduction, Pipeline, or Task-Parallel) in the lines you changed.'
- After: 'rewritten so that it still gives exactly the original program's output and, after re-profiling, DiscoPoP detects a Do-All or Reduction in the lines you changed.'
- Keep 'after re-profiling', which the gate-facts check pins.

**Why.** - The paragraph demotes serial correctness ('not merely reproducing the output'). X_full_05 reasons that the output stays the same 'because … only the execution interleaving changes (which is valid when loop-carried dependence is removed)'.
- DiscoPoP generates no patch for task entries (plan/regions.py:322-333), so naming Pipeline/Task-parallel as targets promises what no arm can get.

**Arms.** B2: the no-pragma agent arms and their twins (through _ASK and the agent's request). The mirror uses _ASK_ANNOTATE and _goal(True) and is unaffected. check_twin_prompt cannot see a twin/agent drift inside the gate block, so edit both in one commit.

**Risk.** - A new version.
- The replace targets, if M2 is not in place.
- Narrowing to Do-All/Reduction is a scope statement the author should confirm.

**Test.** - Render for speed on and off, and for judge_as_shipped.
- check_twin_prompt and the gate-facts checks.
- Model: inside the P3 bundle.

### [should] F1 — Agent feedback: no invented race after a TSan timeout; 'rewrite' not 'diff' in direct mode

**What.** phases/phase_a.py:266-272 (requeue failure_reason)
- Before: '…fails the check at '{stage}': {diag}  So a dependence DiscoPoP did not observe is carried here, and the region stays sequential unless it is restructured.'
- After, when the diagnostic says 'timed out': 'That check could not finish, so nothing is known about a race here; DiscoPoP's pragma could not be verified, which is why the region is sent to you.'
- Keep today's sentence only for a race report, an output mismatch or a schedule disagreement.
- Whether a timeout should requeue at all is a flow decision for the author (gate/tsan.py:212-216 returns stage 'tsan' on a timeout).

_STAGE_GUIDANCE['tsan'] (phase_a.py:1058-1061)
- On a timeout, use: 'The ThreadSanitizer run did not finish in time. No race was reported; do not change the code because of a race that was not observed.'
- Keep 'ThreadSanitizer found a REAL data race' only when the diagnostic contains a race.

_STAGE_GUIDANCE['dependences'] (phase_a.py:1085-1089)
- Before: 'remove that dependence by restructuring'
- After: 'restructure so that this loop no longer carries it (the value must still reach its reader)'.

phase_a.py:1159
- Before: f"Your diff failed at the '{stage}' stage."
- After: f"Your rewrite failed at the '{stage}' stage."

**Why.** - bfs region 2 (E2-B1 smoke) reads: 'fails the check at 'tsan': TSan run timed out (300 s) … So a dependence DiscoPoP did not observe is carried here'.
- The reply invents 'a race … that ThreadSanitizer detects as a timeout (deadlock or extreme contention)' and builds a snapshot buffer around it.
- The s211 and s244 retries say 'Your diff' in direct mode.

**Arms.** F: agent arms only. Twins use FIRST_REASON and get no feedback; bare gets none. For requeued regions this already is an agent/twin asymmetry, and the change narrows it.

**Risk.** It changes the gate's contribution in the three-way comparison, so record a feedback version.

**Test.** - Unit-test the reason builder with a synthetic TSan timeout and a synthetic race.
- Re-render bfs region 2.

### [should] D6 — Array accesses: fix the 'read-only' tag and state the which-loop rule only for plain subscripts

**What.** (a) render.py:275
- Before: '   (read-only here: never a source of a dependence)'
- After: '   (not written in these lines)'. Append ', but a function called here may write it' when ev.calls_in_region is non-empty.

(b) render.py:277-282
- Before: 'A loop whose index appears identically in every subscript that touches an array visits a different element on each of its iterations, so THAT loop does not carry a dependence through the array.  A dependence is carried by the loop whose index differs between a write and a read (`a[i]` written, `a[i-1]` read).'
- After: 'A loop whose index is the same plain subscript in every access to an array (`a[i]` written, `a[i]` read) touches a different element on each iteration, so that loop carries no dependence through that array.  A dependence is carried by the loop whose index differs between a write and a read (`a[i]` written, `a[i-1]` read).  An indirect subscript (`a[idx[i]]`) settles nothing: which iterations meet depends on idx's contents, which only the observed dependences show.'

**Why.** - s211/s244 read 'c: … (read-only here: never a source of a dependence)', while pb_mix(), called at line 139 inside the region, writes c, and the deps list c under RAW.
- ORDER-2 reads 'u: written as [ju[i]] | read as [ju[i]], [ku[i]]' right above a rule that reads as settling it.

**Arms.** D.

**Risk.** Low.

**Test.** Re-render s244 (the tag changes for c, d and e) and ORDER-2 (the indirect sentence appears).

### [should] D7 — Digest: no 'structural, not data flow' claim when blockers or calls exist

**What.** render.py:225-228
- Before: '  - No RAW dependences observed apart from loop counters and parameters — the blocker is structural (control flow), not data flow.'
- After: '  - No RAW with both ends in these lines was observed.'
- When calls exist, add: ' The region calls {callees}(); dependences inside those calls are not listed line by line, and DiscoPoP's Do-All blockers may come from them.'
- Say 'the blocker is structural (control flow)' only when the blockers list is empty and there is no call.

**Why.** s151 (E2-B1 smoke) shows the contradiction in one request:
- The digest says the blocker is structural.
- The blockers say 'RAW on `GEPRESULT_a` loop-carried (loop at line 25)'.
- The body is `s151s(a, b, 1); pb_mix(nl);`.
- The model guessed s151s's body and inlined it.

**Arms.** D.

**Risk.** Low.

**Test.** A unit fixture from the s151 request: the structural sentence is absent and the calls sentence is present.

### [should] D8 — Do not list the target loop as 'already parallel inside this region'

**What.** _fmt_inner_patterns (render.py:286-311) and the digest (render.py:242-245): read p['is_target'], which context.py:346 computes and nothing reads.

For the target loop:
- Leave it out of the digest.
- Render it as: '  - this loop itself (line {line}): DiscoPoP reports a Do-All{clauses}, but its pragma did not pass the check (see 'Why this region is here').'
- Keep 'What is asked of you is whatever stops a loop OUTSIDE them' only when some listed loop is not the target.

**Why.** bfs region 2 (lines 34-42) reads:
- 'DiscoPoP ALREADY reports parallel loop(s) inside this region (line 34) — those need a pragma, not a rewrite'
- '…whatever stops a loop OUTSIDE them'
The task in the same request targets lines 34-42, and no such outside loop exists.

**Arms.** D. It occurs only for regions requeued under --requeue-rejected; twins get FIRST_REASON and may never produce it.

**Risk.** Low.

**Test.** Re-render bfs region 2; a test_features case with is_target=True.

### [should] E1 — E2 Part D: each ablated block has copies elsewhere — decide before E2-D runs

**What.** Decision for the author.

(a) Run E2-D on v2 as registered, and report as a limitation:
- prompt_without_granularity keeps checklist item 2 ('Which is the OUTERMOST loop … speed is not judged at this input size …', request.py:88-90) and the loop-nest parenthetical (render.py:371-376). _evidence_sections receives gate.require_speedup, not gate.omit.
- prompt_without_gate keeps _ASK's and _goal's 'race-free … output-preserving'.
- prompt_without_checklist keeps _PLAN_SPEC.

(b) Re-version first:
- Make checklist item 2 and the loop-nest note honor omit 'granularity'.
- Have _PLAN_SPEC point to the checklist, with its own text as the fallback.

Independently, checklist item 2 (speed off) points at the nl repetition loop on TSVC. The s151 request carries both 'Which is the OUTERMOST loop …' and the protected note 'the repetitions … must run in order'. Replace it with '  - Which loop, once its iterations are independent, carries the most work?\n'; the mirror changes identically through _task_checklist.

**Why.** - Verified in the code: _task_checklist never reads gate.omit for granularity.
- _evidence_sections gets only speed_judged.
- The E2 headline still lists Parts C/D as to run.

**Arms.** The checklist and _PLAN_SPEC are A. The loop-nest note is D.

**Risk.** (a) weakens E2-D's reading; (b) is a new version.

**Test.** No model: render each prompt_without_*_b1 arm and grep for 'OUTERMOST', 'ThreadSanitizer' and 'Re-derive'. Each must be absent from its own arm.

### [should] A8 — Protected notes: say the repetition loop stays sequential and what the output is (package text)

**What.** prepare_tsvc.py:698-700 (PROTECTED_NOTE)
- Before: '`pb_mix(nl)` changes a few input values between two repetitions of the `nl` loop, so the repetitions depend on each other and must run in order; the loop under study is the one inside it.'
- After: '… must run in order: leave the `nl` loop sequential; the loop under study is the one inside it.  What the program prints is a checksum of the arrays, so every element's final value is part of the output.'

evidence_pilot.py:116-118
- Before: '…calls `kernel_%s` once and prints its result.'
- After: '…calls `kernel_%s` once and prints checksums of `u` and `v`, so every element's final value is part of the output.'
- kernel_k17 returns 0; pb_finish prints sums of u and v.

Region selection: s151's target region is the nl loop itself (lines 25-28). Consider not selecting a region the note declares sequential. That is a planner decision.

**Why.** - s151 has three contradictions in one request: the target is the nl loop; the blocker is 'RAW … loop at line 25 … must be removed'; the note says the nl repetitions must run in order.
- The notes call a checksum 'its result'.

**Arms.** A: every arm reads _protected_block. A new package version: bump GENERATOR_VERSION and run test_integrity.py. Check the wording against D36 (it describes the output and the harness, not a transformation).

**Risk.** - A package change mid-campaign, so only for the next experiment.
- Sensitive to D36 hint leaks; the author decides.

**Test.** - Regenerate one tsvc_b1 package and bfs; run test_integrity.py and test_arms.py.
- Replay s151 and s244 as single calls (N=5) and count rewrites that touch nl.

### [could] D9 — Small wording fixes (glosses, dangling references, header)

**What.** - Scalar gloss (render.py:222-223)
  - Before: '— usually a reused location or an accumulator, not a value travelling between iterations.'
  - After: '— usually a temporary every iteration rewrites (declare it inside the loop body), or an accumulator or flag whose running value does travel between iterations (a reduction handles it).'
- Induction footer (render.py:104-106): '; see 'Loop structure' for which of them a pragma has to privatise' points to a NOTE printed only under llm_pragmas (render.py:377). Drop the clause when llm_pragmas is off.
- extra_vars (render.py:482-484)
  - Before: 'static-only deps (compiler-conservative, NEVER observed at runtime → the dependence is likely spurious; exposing or privatizing may already be safe)'
  - After: 'dependences only DiscoPoP's static analysis reports (not observed on the one small profiling input; your rewrite is checked on other inputs too)'
- Classification (render.py:416-417)
  - Before: '(the data structures — a loop-carried dep on these is ALGORITHMIC, not removable by privatizing/renaming)'
  - After: '(shared by all threads in DiscoPoP's pragma)'
- Header (request.py:234)
  - Before: f"## Target region: {region_label} {evidence.region_id} at lines {s}–{e}"
  - After: f"## Target region: the {region_label} at lines {s}–{e} (DiscoPoP id {evidence.region_id})". The old form reads 'loop 1:10 at lines 5–8', a second apparent line range.

**Why.** - bfs: 'RAW on SCALARS: id, k, stop — usually a reused location…', although stop is a flag read after the loop.
- The dangling footer appears in every no-pragma request (ORDER-2, s211, s244).
- The ORDER-2 header shows 'loop 1:10 at lines 5–8'.
- The extra_vars and classification glosses contradict the text proposed in D1 and D10. No archived sample showed extra_vars.

**Arms.** The glosses are D. The header is every agent arm, including none, and the twins; not bare.

**Risk.** Low.

**Test.** Re-render the bfs and ORDER-2 requests; grep that no no-pragma request contains 'a pragma has to privatise'.

### [could] A6 — Contract on buffers and cost (a speed question, later stage)

**What.** _CONTRACT_OPEN bullets 1-2 (prompts.py:126-131), and the numeric variant at prompts.py:310-314
- Before: 'Everything else is yours: execution order, loop bounds, extra buffers, extra passes.' / 'Extra work is fine within a constant factor — a second buffer, one more pass.'
- After: 'Within that, execution order, loop bounds and temporary storage are yours to change, as long as every read still gets the value it got in the original.' plus 'Prefer the rewrite that adds least: most loops need their statements split or reordered, not a copy of an array; a whole-array copy on every repetition of an enclosing loop costs as much memory traffic as the loop itself.'
- The first bullet must still begin '  - The program's output', because _contract_open indexes on it.
- Shorten the heap bullet's arithmetic, keeping the pinned phrases 'HEAP-allocated' and 'stack is 8 MB'.

**Why.** - Whole-array copies per repetition: bfs record 0 (h_cost_new copied in and out each level); s151 (a temp copy of a); s211 without evidence (b_new plus a copy-back).
- The claim that E1's 15 Settle-dropped rewrites were slow for this reason comes from the task lens citing memory; I did not re-verify it.
- The D40 record says cost advice goes via feedback. This version keeps every arm symmetric but is still a speed lever.

**Arms.** A: every arm, including the bare 'contract' prompt unless frozen.

**Risk.** - It may suppress correct buffer rewrites (s211's b_new was correct).
- It affects FASTER, not the wrong-output failure measured here; E2-B1 runs with speed off.

**Test.** Single-call replays of speed-on loops (N=5): count whole-array copies inside repetition loops; then FASTER on a small E2 subset.

### [could] A10 — Simplify and reorder the whole prompt (only as one new version, all arms rerun)

**What.** Apply the proposed outline:
- Merge ROLE and WHAT WE ASK.
- Replace WHAT WE GIVE YOU with a static 'reading the evidence' legend (D10's text), independent of which sections are included.
- State the pragma rule once, as the contract line.
- Remove _granularity's repeated constant-factor sentence.
- Build check steps 2 and 4 through _step so they wrap. Step 4 today renders 'static, dynamic and\n     guided schedules and output' on an unwrapped 100-char line.
- Request: header → function excerpt → one facts block (in-region flows, crossing values, DiscoPoP's per-loop verdict, loop nest, calls, inner patterns, accesses) → the generated order statement (stage 2) → why-here (requeue only) → Task (one sentence, protected block, checklist, output line).
- Drop the digest, which repeats the later sections.
- Mechanism: a GateFacts field whose default reproduces today's text byte for byte (the D40 precedent, judge_as_shipped), so v1 stays reproducible.

**Why.** - System prompt 6,392 chars. Request X/full 5,642 (X/none 1,893, so the evidence is about 3.75k): array_note 1,108, accesses 1,017 (about 520 of it read-only rows), digest 369.
- s211 is 7,652 chars and bfs 9,546, growing mostly by repeated boilerplate.
- Advice sits between facts: the last evidence the model reads before the Task is the blockers' imperative.

**Arms.** A, B2 and C for the system prompt; D for the facts block. Comparable only when every arm of the new version is run.

**Risk.** - It changes many things at once, so no single effect can be attributed.
- It does not by itself fix a measured failure.
- Adopt only after the must/should groups have been measured.

**Test.** - The M2 hash check; the pinned-phrase feature checks updated deliberately.
- ORDER-2 'reordered, same sentences' vs 'as today' (X/Y × 10) separates order from content.

### [could] A7 — Abstention: not recommended for the agent (author decision)

**What.** Option A would append to _CONTRACT_CLOSE: 'If you find no rewrite that keeps the output, leave the code as it is and say why.' This conflicts with the standing rule that the model always aims for a parallelizable version and the gate decides.

Option B would add only to the twins' and the mirror's judged heads: 'A program that fails any step is counted as broken; one you leave unchanged is counted as unchanged.' This is the counterpart of the agent's 'or the rewrite is reverted', but D37/D38 say nothing is added.

Recommendation: neither now. Record the asymmetry in the three-way comparison: a forced change is reverted in the agent and kept in the twin and the mirror.

**Why.** - twin.py:340 keeps whatever the model left.
- The model alone had 17/88 BROKEN in E1-bare (per memory).

**Arms.** A: every arm. B: twins and mirror only.

**Risk.** A lowers the agent's reach; B breaks 'nothing added'.

**Test.** Only if pursued: single calls on recurrence loops versus winnable loops, measuring the abstain rate and the BROKEN rate.

## Proposed outline

Target layout for prompt v2. Sizes are estimates, measured against ORDER-2 X/full today: system 6,392 chars, request 5,642.

SYSTEM PROMPT (cached, byte-identical within a run). The block order stays, so the twin's CHECKED→JUDGED swap and the mirror's replaces still work.
1. ROLE + WHAT WE ASK (~450; B2). The rewrite must compute exactly what it computes now, with at least one loop whose iterations no longer depend on each other. DiscoPoP re-profiles it and inserts the pragmas. Success, in order: sequential output unchanged → a Do-All or Reduction in the changed lines → DiscoPoP's pragma race-free, keeping the output (and faster when speed is on). (A4)
2. READING THE EVIDENCE (~450, evidence arms; the none arms keep their 174-char 'no profiling data' text).
   - Each pair is written 'line W writes → line R reads'.
   - A carried RAW is a value in transit: move it (the writer's loop first), never replace it with a pre-loop copy.
   - WAR and WAW are reuse, which a copy or a private variable fixes.
   - Counters are omitted.
   - Dynamic means observed on the small profiling input; static means not ruled out. (D10, D2)
3. THE CONTRACT (~1,000; A). Output byte-identical (numeric variant kept). Order, bounds and storage are yours as long as every read gets its value. Work within a constant factor. The heap rule, keeping the pinned phrases. Signature and I/O untouched. The pragma line (E3's variable). Unchanged code is not an answer; a dependence is moved, not deleted; the accumulator carve-out. (A1; A6 later)
4. HOW YOUR REWRITE IS CHECKED (~850; B2; generated from GateFacts). Four wrapped steps, then 'Both halves are required…' (A4, A10).
5. Granularity (~300 speed off, ~350 speed on; A). Stated once here only (E1).
6. WHAT OPENMP REQUIRES (~530; A). Unchanged; shared with bare.
7. OUTPUT (~750; B1 + A). Direct-mode mechanics, then the revised _PLAN_SPEC (A2).
Total: about 4.3k with A10, about 5.6k with only the must/should edits.

REQUEST (not cached; every character is paid on every call). Data first, task last, as today; no advice inside the facts.
1. Header (~150): file; function with its lines; 'Target region: the loop at lines 5–8 (DiscoPoP id 1:10)'. (D9)
2. The function excerpt (~330). Kept: it anchors the line numbers.
3. 'What DiscoPoP observed (small profiling input)' (~600-900 for ORDER-2, ~1.5k for s211 down from about 3.5k). Evidence arms only; every line keeps its section tag so --evidence subsets and E2-C stay definable.
   - Value flows (RAW), one line per in-region pair, with the statements quoted once. (D2, D5)
   - Reuse (WAR/WAW), one line each.
   - One line for values that cross the region's edge. (D5)
   - DiscoPoP's Do-All verdict per loop, with neutral notes. (D1)
   - Loop nest in 1-3 lines, with the count note once.
   - Calls. Inner patterns, filtered by is_target. (D8)
   - Reductions.
   - Array accesses: written arrays only, one line for read-only arrays, and the revised plain-subscript rule. (D6)
4. 'What the observed flow means for a rewrite' (array_note; ~300 per pair). Stage 2 only, generated, and only where DiscoPoP names the carrying loop. (D4)
5. 'Why this region is here': omitted on a first attempt (A10); the verbatim diagnostic on a requeue. (F1)
6. Task (~900 today-equivalent): one sentence goal (A4), the protected block (A8), the checklist (item 1 extended by A3, item 2 per E1), and the final instruction line.

Estimated request sizes:
- ORDER-2 X/full: about 4.4k after stage 1 (without A10), about 3.3k with A10, plus about 350 per stage-2 bullet.
- s211: about 5.0k, down from 7,652.
- none arm: about 1.9-2.1k (the A3 checklist grows it slightly).

## Test plan

Stage 0 — no model calls; run first.
1. M1, M2 and M3 land together:
   - the pilot instrument fix;
   - replace-target assertions and the arm hash manifest, built from today's code before anything else changes;
   - the mirror leak fix with its test.
2. Render checks from the archived profiles, with no profiling. Sources: runs/evidence_pilot_order2/profile/{k17,k42}, v3_pilot_3/profiles/tsvc/s244, the s211 profile, and the E2-B1 smoke s151/bfs. Assert:
   - no 'must be removed', 'GEPRESULT', 'sub-passes', 'second buffer' or dangling 'Choosing the fix';
   - k17 renders 'line 7 writes → line 6 reads' and k42 'line 6 writes → line 7 reads';
   - no variable is both tagged 'not written here' and listed as an in-region RAW;
   - c, d, e and v are not in the RAW list for s211/s244;
   - bfs region 2's target is not listed as 'already parallel';
   - the s151 digest does not say 'structural'.
3. The M2 hash check for each change group. Changed arms must equal the declared set: a D-change leaves no_evidence*, twin_no_evidence* and bare* unchanged; C touches only the evidence arms' system prompts; A changes all.
4. D4 truth table. For the 18 E2 TSVC loops, ORDER-2 and s151/bfs, hand-derive the correct fission order inside the target loop. Every generated bullet must agree, and none may fire on s244-like records.
5. M4, on the server, explorer only: doall_prevented for s244 and s211 on the fixed DiscoPoP.
- Pass/fail on these checks is mechanical and needs no judgement.

Stage 1 — ORDER-2 single-call pilots (Haiku, the agent's direct mode, confined workspace, N=10 per version and arm, scored by the pilot's full rule including the re-profile). Pre-register every arm and threshold, and state the count and cost before launch (the user's rule on fan-outs).
- P1, which layer carries the direction (60 calls):
  - full_clean: today's rendering, instrument fixed;
  - arrow_only: full_clean + D2;
  - order_clean: full_clean + the pilot's order note, placed before '### Task'.
  - GO for order_clean: X ≥ 7/10 and Y ≥ 8/10 (the follow-up's thresholds).
  - arrow_only's X count decides how much of D4 is needed: ≥ 5/10 means the arrow largely suffices.
  - full_clean also re-measures the first pilot's full arm without the confound.
- P2, the evidence bundle (40 calls):
  - stage1_v2 = D1+D2+D3+D5+D10;
  - render_v2 = stage1_v2 + D4 (single-loop rule; fires on ORDER-2).
  - GO: stage1_v2 Y ≥ 9/10 with ≤ 1/10 buffer/snapshot rewrites (harm removed); render_v2 X ≥ 7/10 and Y ≥ 9/10.
- P3, shared text (40 calls): A1+A2+A3+A4 on the none arm (X/Y), then render_v2 + shared.
  - GO for the shared text: Y none ≥ 9/10. X none is expected to stay about 0, because the direction cannot be known without evidence; that is the correct outcome, not a failure.
  - The bundle must not fall below render_v2.
- Second model: render_v2 + shared on Sonnet, X/Y × 5 (10 calls), against the order2b sonnet_full result once it is scored.

Stage 2 — replays on real loops (single calls, twin-style, no gate, Haiku; 60-160 calls).
- Loops: s211 and s244 at N=10, from profiles re-explored on the fixed DiscoPoP (M4), else s244 measures a DiscoPoP defect. If affordable, the other 16 E2 loops at N=3.
- Arms: full_v1, full_v2, none_v2.
- Outcomes, in order: output identical on the harness's two inputs; then, on the server, DiscoPoP reports a Do-All in the changed lines. Also count odd/even splits, snapshot-on-RAW rewrites and wrong fission order.
- GO: on s211 and s244, full_v2's wrong-output rate ≤ none_v2's and below full_v1's. No loop may have full_v2 worse than full_v1 by ≥ 3/10.

Stage 3 — a small agent run on the server, after E2-B1 has finished.
- Loops: an E2 subset (s211, s244, s212, s241, s243, s252) plus E2-B1's s151 and bfs.
- Arms: full_b1_v2, no_evidence_b1_v2, twin_full_v2, twin_no_evidence_v2 and bare_llm_v2, N=5.
- This decides whether v2 becomes the registered version of the next experiment. E2 Parts C and D are then run on v2, with E1's choice made first.

What decides adoption:
- A change group is adopted only if all three hold: its stage-0 assertions pass; the hash check shows exactly the intended arms changed; its pre-registered pilot threshold is met.
- A10 (simplification and reordering) and A6 (cost wording) are adopted only as part of a new version where every arm is rerun, never on taste.
- Nothing in A, B2, C or D is deployed while E2-B1 is running.

## Implications for experiments already run

1. E1c, E2 and E2-B1 were all run with prompt v1, the texts reviewed here.
   - Their results stand as measurements of DiscoPoP's evidence as rendered in v1, with Haiku.
   - Report the E2 null (H12, H5b and H5d not supported) that way, not as 'DiscoPoP's evidence does not help'.
   - Name the v1 rendering defects as a limitation and as a finding: evidence can hurt when rendered as imperatives and generic fixes. The defects are the backwards arrow, 'it must be removed', the buffer/sub-pass note, false 'loop-carried' labels, a false 'read-only' tag and a false 'structural' line.
   - s211's odd/even splits (7/18 vs 0/13) are attributable to the note's text.

2. s244 in E2.
   - E2 A+B (e2c_ab_2) and the V3 pilot ran before the B4 explorer fix of 26 Sep. The V3 profile charges the RAW on a to the inner loop; t0_11 (20 Sep) charges it to the nl loop.
   - Run M4 before interpreting s244's 1/18 vs 12/18. If the inner-loop blocker is a DiscoPoP artefact, report s244's evidence-arm loss as caused by a DiscoPoP defect.
   - Under the fixed-DiscoPoP rule, rerun s244's evidence arms and twins on the fixed DiscoPoP, or report s244 separately.

3. ORDER-2 first pilot (evidence_pilot_order2).
   - Record the instrument deviation: evidence arms carried '### What went wrong\nk17/k42', the none arms did not.
   - The NO-GO stands: X is 0/10 in all three arms, including no_note, which shares the confound with full.
   - The Y full-vs-none contrast (7 vs 10) is confounded. The clean full-vs-no_note contrast (7 vs 8) says the generic note alone is not what drives the Y harm.
   - All 5 Y failures in the evidence arms are buffer or snapshot rewrites. Every X answer in every arm kept the textual order.

4. order2b.
   - Record two deviations: the same confound (order, sonnet_full), and the note placed inside '### Task'.
   - The order-vs-full contrast is clean. sonnet_full vs sonnet_none is confounded, so re-run sonnet_full with M1 before claiming a Sonnet effect.
   - Preliminary, from my scratchpad compile-and-run check (output only, not the pilot's score): X/order gives the original output in 8/10 (all 8 put line 7's loop first), and Y/order in 10/10. Cite it only after the pilot's own scoring.
   - The result does not transfer to TSVC without D4's carrying-loop gate: the s244 records would produce a wrong order.

5. E2-B1, running now: do not change prompts mid-run. Record as deviations:
   - The mirror leak in bare_llm_nospeed ('profiled', 'evidence', and 'The blocking dependence' with no referent). The author decides whether that cheap arm is re-run.
   - The requeue text on bfs region 2, which asserts an unobserved dependence after a TSan timeout. It is agent-only; the twins do not requeue.
   - s151: the target region is the nl loop, while the protected note says nl must run in order and the checklist says to take the outermost loop.

6. E2 Parts C and D (not yet run).
   - If D3/D4 are adopted, the 'howto' group measures different text: re-register E2-C.
   - E2-D's ablations leak their blocks through the checklist, _PLAN_SPEC and the loop-nest note. Choose between running as registered with the limitation stated, or re-versioning (E1).

7. Versioning.
   - Any A, B2 or C change is prompt v2 for every arm. The three-way comparison stays matched within v2, but v1 and v2 results must not be pooled.
   - D-only changes leave the none and bare prompts byte-identical, as the hash check proves. They still define a new evidence treatment, so any evidence arm compared across versions has to be re-run.
   - DiscoPoP alone is unaffected by prompt changes; M4's DiscoPoP changes apply to every arm, per the user's rule.
