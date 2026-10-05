# Why the evidence started to help — what changed between prompt version 1 and version 3

*Written 2 Oct 2026 for the thesis (RQ4). Every number below is from a pre-registered run; the record is
`THESIS_EXPERIMENTS.md` §6 (28 Sep – 2 Oct) and §7. The rendered texts are generated, not hand-copied:
`venv/bin/python evaluation/agent/tools/render_evidence.py k17 --version 1` (and `--version 3`).*

## The question

In E2 (TSVC, 28 Sep and before) and E2-B1 (loops whose deciding fact sits outside the loop), DiscoPoP's
evidence did not help the model: no advantage inside the agent, and harm to the gate-free twins. In E2-V3 the
same kind of evidence decided success: ORDER-2 X 10/10 with evidence against 1/10 without, inside the agent.
**The facts DiscoPoP measured were the same in both. What changed is how the agent wrote them into the prompt.**

## The kernel where it matters (ORDER-2, constructed — `tools/prepare_tsvc.py`, `_ORDER2B_BODY`)

```c
u[ju[i]] += v[kv[i]] * c[i];        // line 19 (line 6 in the pilots' kernel)
v[jv[i]]  = u[ku[i]] * d[i] + c[i]; // line 20 (line 7)
```

The index tables live in a harness header the model never sees. In X, `kv[i] = i-1`: line 19 reads the `v`
that line 20 wrote one iteration earlier, so the loop can only be split with **line 20's loop first**; the
textual order gives wrong results. In Y (the control) the tables are swapped and the textual order is right.
The model's files of X and Y are identical up to the kernel's name.

## What the model read about the same measurement

Same DiscoPoP profile (the pilots' kernel `k17`, lines 5–7), rendered by the agent's own code.

**Prompt version 1** (E2, E2-B1, the first pilots):

```
### Evidence digest (details in the sections below)
  - Loop-carried RAW on ARRAY ELEMENTS of: v — a value moves between iterations through the data; see 'Choosing the fix' below.
  - `u` is written as [ju[i]] and read as [ju[i]], [ku[i]].
  - `v` is written as [jv[i]] and read as [kv[i]], [jv[i]].
  - Loop lines 5–8 (index: i): 1 activation(s) × ~31999 iterations.

### Runtime data dependences in the target region (observed)
(grouped per variable, each tagged [array element] or [scalar])
  RAW — read-after-write (the blocking ones):
    v  [array element]  at lines 6→7
        line 6: `u[ju[i]] += v[kv[i]] * c[i];`
        line 7: `v[jv[i]] += u[ku[i]] * d[i];`

  WAR — write-after-read: none

  WAW — write-after-write: none

  (Not listed: dependences on the induction variable(s) i — they are never what blocks a loop; see 'Loop structure' for which of them a pragma has to privatise.)

### Choosing the fix for this array dependence
The blocking RAW dependence is on ARRAY ELEMENTS (v): an iteration reads an element another iteration wrote.  Renaming the array does not change that.  Settle two things, in this order:
  1. WHICH LOOP carries it.  Compare the subscripts written with the subscripts read.  A loop whose index sits identically in all of them is not the one — it may be parallel as it stands, and then the answer is a pragma on THAT loop, not a rewrite.
  2. For a loop that does carry it: can a value written during one sweep be read again LATER IN THE SAME SWEEP?
     - No — each result depends only on values from before the sweep.  Read from one buffer and write to another (or copy just the elements that are read across iterations before the sweep starts).
     - Yes — the update travels along the array as the sweep runs, so a second buffer would change the answer.  Split each sweep into ordered sub-passes over disjoint elements instead; every bound then has to be re-derived, because a value now moves a shorter distance per sweep than the original order carried it.

### Why DiscoPoP could not parallelize (Do-All blockers)
DiscoPoP identified these exact dependences as what blocks Do-All — target these specifically:
  - RAW on `GEPRESULT_v`  loop-carried (loop at line 5)  [dynamic — a real, observed dependency; it must be removed]
```

- `at lines 6→7` prints the record sink → source: it reads "from 6 to 7", the **wrong direction** (the
  value flows from line 7 to line 6).
- `it must be removed` tells the model to **delete** the dependence — the answers did so by giving line 6
  `v`'s values from before the loop (a snapshot), which changes the result.
- The generic note offers exactly that fix (`Read from one buffer and write to another`).

**Prompt version 3** (E2-V3, its Sonnet follow-up, E12, and every experiment from 2 Oct):

```
### Evidence digest (details in the sections below)
  - RAW on array elements within these lines: v.
  - `u` is written as [ju[i]] and read as [ju[i]], [ku[i]].
  - `v` is written as [jv[i]] and read as [kv[i]], [jv[i]].
  - Loop lines 5–8 (index: i): 1 activation(s) × ~31999 iterations.

### Runtime data dependences in the target region (observed)
(grouped per variable, each tagged [array element] or [scalar]; each pair is the earlier access → the later one)
  RAW — read-after-write (a value written by one access and read by a later one):
    `v` [array element]: line 7 writes → line 6 reads
        line 6: `u[ju[i]] += v[kv[i]] * c[i];`
        line 7: `v[jv[i]] += u[ku[i]] * d[i];`

  WAR — write-after-read: none

  WAW — write-after-write: none

  (Not listed: dependences on the induction variable(s) i — they are never what blocks a loop; see 'Loop structure' for which of them a pragma has to privatise.)

### Why DiscoPoP could not parallelize (Do-All blockers)
DiscoPoP's Do-All check stopped at these.  Each names the variable and the loop it blocks; the line pairs are in the dependence list, when it is shown.
  - RAW on `v`  loop-carried (loop at line 5)  [observed: an iteration of this loop read a value an earlier iteration wrote — that value must keep reaching its reader, so the dependence can be moved out of the loop you make parallel, not deleted]

### What the observed flow means for a rewrite (from DiscoPoP's records)
  - Line 6 (`u[ju[i]] += v[kv[i]] * c[i];`) reads an element of `v` that line 7 (`v[jv[i]] += u[ku[i]] * d[i];`) writes; DiscoPoP names the loop at line 5 as carrying this dependence.  The value must flow from line 7 to line 6: if you split that loop, the loop holding line 7 has to run completely before the loop holding line 6; reading `v`'s values from before the loop would change the result.
```

plus, in the evidence arms' system prompt, what a carried RAW means ("a value in transit … can be moved but
not deleted, and handing the reader a copy taken before the loop changes the result") and, in every arm's
contract, "a dependence is moved, not deleted".

## Which change did it — the pilot that added them one at a time

`evidence_pilot_v2` (28 Sep, pre-registered; `results/history/pilots/runs/evidence_pilot_v2/summary.md`): single
Haiku calls in the agent's direct mode, no agent loop, 10 per cell; success = the output identical on both
inputs, no pragma written, and DiscoPoP's re-profile reports both loops Do-All.

| What the model read | ORDER-2 X (order hidden) | ORDER-2 Y (control) |
|---|---|---|
| version 1 | **0/10** | 6/10 |
| version 1 + only the arrow corrected (`line 7 writes → line 6 reads`, D2) | **0/10** | 8/10 |
| version 2 (arrow corrected, "must be removed" gone, the generic note gone, false lines gone, "moved, not deleted") | **4/10** | 8/10 |
| **version 3 = version 2 + the order statement (D4)** | **8/10** | **10/10** |
| version 1 + only an order statement (hand-built) | **9/10** | **10/10** |
| no evidence (version 2's text) | **0/10** | 10/10 |

**Reading.** The order statement (D4) is the change that carries the effect: it alone takes X from 0 to 8–9 of
10. The corrected arrow alone does nothing; removing the misleading text (version 2) helps partly on X and
removes the harm on Y. The first pilot (`evidence_pilot_order2`) had shown the same facts as rendered give
X 0/10 in every arm, and the follow-up (`evidence_pilot_order2b`) that the hand-built order note gives 8/10.

**How the order statement is made (D4, `discopop_agent/llm/render.py`, `order_statement`).** From DiscoPoP's
records only: for an array read-after-write between two lines of the region, the writing and the reading line
come from the dependence record; the loop that carries it from DiscoPoP's Do-All blockers. The statement is
written only when the blockers name exactly one loop for the variable (anywhere in the file) and that loop is
the innermost one holding both lines; a flow the other way between the same lines makes the pair a cycle
("splitting between them changes the result"). Nothing is benchmark-specific. Checked by hand on 64 regions of
29 programs before any model saw it: it spoke on 5 and was right on all 5, and stayed silent on `s244`, where a
naive rule would have stated the wrong order.

## Inside the agent, and against the models alone

| ORDER-2 X | correct parallel program | of them faster | unsafe | source |
|---|---|---|---|---|
| **Haiku agent + evidence (v3)** | **10/10** | **10** | 0 | E2-V3, `e2v3_k19` |
| Haiku agent, no evidence (v3) | 1/10 (9 no change) | 1 | 0 | E2-V3, `e2v3_k19` |
| Sonnet agent + evidence / no evidence (v3) | 9/10 / 0/10 | 9 / 0 | 0 / 0 | `e2v3s_k19` |
| Haiku alone | 0/10 | 0 | 10 | `e2v3_k19` |
| Sonnet alone | 0/10 | 0 | 10 | `e2v3s_k19` |
| Opus alone | 3/5 | **0** | 2 | E12, `e12_opus_v3` |
| Fable alone | 3/3 (+2 harness edits) | **0** | 0 | E12, `e12_fable_v3` |

(ORDER-2 Y, the control: the Haiku agent 10/10 with and without evidence — no harm.)

**Why the agent beats the model alone here — three things together:**

1. **DiscoPoP measures what the code hides.** The index tables are invisible to any model; the profiler
   sees at run time which line feeds which. No model alone has this fact, whatever its strength — Opus and
   Fable alone protect themselves with a run-time dependence analysis (an inspector computing wavefront
   levels) that is correct but runs this loop one iteration at a time: never faster.
2. **The order statement turns the measurement into the right action.** The same fact rendered as in version
   1 gave 0/10.
3. **The gate catches the wrong attempts.** Without the evidence, the agent's wrong-order splits fail the
   output check and are reverted: it ends with no change, not with a wrong program; the models alone ship the
   wrong program.

## Limits (stated with the result)

- **One constructed kernel carries the effect.** On the real loops where the order statement fires (`s1213`,
  `s211`) the agent without evidence already reaches 9–10/10 (gate + retry). A search of the repository's
  suites and 16 real HPC mini-apps (`tools/order_screen.py`, `tools/text_order_screen.py`; §7, 29 Sep) found
  no real loop with a hidden split order.
- On E2-B1's real hidden-dependence loops version 3 helps the twins on `s161` but still harms them on `s151`
  (the dependence sits in a called function, which the evidence builder does not show) and `bfs`.
- Haiku and Sonnet at N = 10, Opus and Fable at N = 5.

## Where everything is

- Record: `docs/THESIS_EXPERIMENTS.md` §6 (28 Sep: the pilots, the prompt review, D4; 29 Sep: E2-V3; 30 Sep:
  the Sonnet follow-up, E12; 2 Oct: E2's combined conclusion) and §7 (run entries).
- The review that found the rendering defects: `docs/PROMPT_REVIEW_2026_09_28.md`.
- Pilots: `results/history/pilots/runs/evidence_pilot_order2`, `evidence_pilot_order2b`, `evidence_pilot_v2`.
- E2-V3: `results/history/E02v3_order_statement/` (`stats/e2b1_stats.md`, `stats_sonnet/`, exhibits
  `k19_evidence_right_split`, `k19_no_evidence_reverted`, `k19_twin_wrong_order` — before/after pictures,
  LaTeX diffs, consoles).
- E12: `results/history/E12_stronger_models_alone/stats/e12_stats.md`.
- Code: `discopop_agent/llm/render.py` (`order_statement`, `_fmt_deps_v2`, `_fmt_blockers_v2`),
  `discopop_agent/llm/prompts.py` (`PROMPT_VERSIONS`, `_given`, `_CONTRACT_CLOSE_V2`).
