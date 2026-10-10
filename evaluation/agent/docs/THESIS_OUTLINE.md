# Thesis outline — detailed draft for approval (7 Oct 2026)

Built from the campaign page (`docs/EXPERIMENT_PLAN.html`), the pipeline page (`docs/FLOW.html`), the agent's
documentation (`discopop_agent/docs/`), the experiment record (`docs/THESIS_EXPERIMENTS.md`) and the results
registry. It covers everything the agent does and everything the campaign measures or plans to measure, whether the
experiment has run or not. Every evaluation section carries its status:

**[done]** measured and read out · **[partly]** some of it measured · **[planned]** designed and registered, not run ·
**[dropped]** decided against, with the reason · **[open]** a decision is still owed.

The chapter list is a proposal and goes beyond the six default parts (abstract, introduction, related work,
approach, evaluation, conclusion): background, implementation, the evaluation method and a discussion get chapters
of their own. Section 12 shows how to fold it back into six parts if that is preferred.

---

## 0 The thesis at a glance

**Working title (the author decides).**
1. *Dependences as Diagnoses: an LLM Agent that Restructures Code so that DiscoPoP Can Parallelize It*
2. *Beyond Annotation: Combining Dependence Profiling and a Language Model to Parallelize Loops that Need Restructuring*
3. *Agentic DiscoPoP: Profile-Guided Restructuring of Sequential Code for OpenMP*

**The thesis in one sentence.** A dependence DiscoPoP reports is read as a diagnosis, not as a limit: a language
model rewrites the loop so that the dependence is gone, DiscoPoP confirms it and writes the OpenMP directive, and a
sequence of checks decides whether the result is safe and worth keeping.

**Three claims.**

| Claim | Statement | Measured against |
|---|---|---|
| C1 Coverage | Restructuring parallelizes what DiscoPoP alone cannot | DiscoPoP's own suggestions pushed through the same checks |
| C2 Trust | The checks are strong enough to permit rewriting, and their blind spots are known | every accepted change judged again by an independent harness; unsafe acceptances counted and named |
| C3 Cost | DiscoPoP's evidence can stay valid across edits without profiling from scratch | the full re-profile as ground truth |

**Research questions.** The campaign page refers to RQ1–RQ9 through its hypothesis table; the wording below is
proposed here and is to be confirmed with the title.

| RQ | Question | Claim | Hypotheses | Experiments | Section | Status |
|---|---|---|---|---|---|---|
| RQ1 | Does restructuring parallelize loops DiscoPoP alone cannot? | C1 | H1, H11 | E1, E11 | 7.2, 7.9 | done on kernels |
| RQ2 | Is every accepted change right and race-free, what does each check catch, and where are the checks blind? | C2 | H2, H3, H10, H10b, H13 | E1, E10, E7 | 7.2, 7.6 | E1, E10 done · E7 designed 9 Oct and set aside by the author the same day (not run) |
| RQ3 | How close do the accepted programs come to an expert's version, and do they scale with threads? | C1 | H4, H11 | E1, E2, E6, E11 | 7.2, 7.5, 7.9 | partly |
| RQ4 | What does the model need: DiscoPoP's evidence, feedback from failed attempts, or more strength? | C1 | H5, H5b, H5d, H12 | E2, E12 | 7.3, 7.5 | done |
| RQ5 | Who should write the directive: DiscoPoP or the model? | C1, C2 | H6 (its half on the author), H6b | E3 | 7.7 | done 10 Oct: 81 of 90 fast and race-free where the model writes, 76 of 90 where DiscoPoP writes — not established (p = 0.14; four of the five trials are `s331`); no unusable program in either setup; the directive's author for 7.7.2 is the author's decision |
| RQ6 | Can the model close the gap a fast refresh leaves, without making the analysis unsafe? | C3 | H7, H7b | E4 | 7.7 | planned, after E3 — one experiment with RQ7 (9 Oct) |
| RQ7 | Can the profile be refreshed without running the program again, without changing decisions? | C3 | H6 | E4 | 7.7 | planned, after E3 (moved out of E3 by the author, 9 Oct) |
| RQ8 | How far should restructuring be chained? | C1, C3 | H8 | E8 | 7.8 | planned |
| RQ9 | Where should the agent look first? | C1 | H9 | E9 | 7.4 | planned |

**Contributions.**
1. The agent: a pipeline around DiscoPoP that profiles, ranks, restructures with a language model, checks,
   profiles again, annotates and verifies.
2. The checks ("the gate"): what makes it acceptable to let a model rewrite code, with its error cases named.
3. The design space, each option implemented and switchable: who writes the directive, how the profile is
   refreshed after an edit, how deep restructuring is chained, where the agent looks first, what the model is told
   and how often it may try.
4. An evaluation method that holds itself to a stated standard: hypotheses fixed before the runs, a three-way
   comparison, benchmark files that are ordinary code, instruments proven before the experiments.
5. The results, including the ones against the thesis's own expectations.
6. Defects in DiscoPoP found on the way and fixed at the root, each documented for upstream.

**Chapters and estimated length.**

| # | Chapter | Pages | Can be written now? |
|---|---|---|---|
| — | Abstract | 1 | after chapter 7 |
| 1 | Introduction | 6–8 | yes, results paragraph last |
| 2 | Background | 10–12 | yes |
| 3 | Related work | 6–8 | yes, after the literature check |
| 4 | Approach: the agent | 20–24 | yes |
| 5 | Implementation | 8–10 | yes |
| 6 | Evaluation method | 12–14 | yes |
| 7 | Results | 26–32 | 7.1–7.3, 7.5, 7.6 (speed check), 7.11 now; the rest as experiments finish |
| 8 | Discussion | 6–8 | after chapter 7 |
| 9 | Conclusion and future work | 3–4 | last |
| | Appendices A–G | as needed | mostly generated from the repository |
| | **Total** | **about 100–120** | |

**Terms used in this outline.**
- *Directive*: an OpenMP `#pragma omp …` line.
- *The gate*: the sequence of checks every change must pass before the agent keeps it.
- *Evidence*: what DiscoPoP measured about a loop, in the form the model is shown.
- *Attempt*: one try of the model on one region; after a failure the reason is sent back and it may try again.
- *Model alone*: the same model with the same task text, but without DiscoPoP, without the gate and without feedback.
- *Twin*: the agent's setup with the gate taken out — the same model, the same DiscoPoP information, nothing checking it.
- *Class R / A / D*: the measured class of a loop — needs restructuring / parallel as written / must be left alone.
- *Hidden order*: a loop that must be split, where the order of the two halves is decided by data outside the file.
- *Unusable program*: wrong output, a data race, a crash, a compile error, or slower than the original.
- *Full re-profile / fast refresh*: after an edit, run the instrumented program again / only compile and carry the
  earlier observations over to the new code.
- *Depth*: how many times in a row the agent may restructure code that an earlier rewrite created.

---

## Abstract (about 250 words — what each sentence carries)

1. **Problem.** Tools such as DiscoPoP parallelize loops that are parallel as written; where they report a
   dependence, their work stops. Language models rewrite such loops readily, but ship wrong and racy programs.
2. **Idea.** Read the dependence as a diagnosis: the model removes it, DiscoPoP confirms that it is gone and writes
   the directive, a gate decides.
3. **System.** An agent around DiscoPoP: profile, rank, restructure, check, profile again, annotate, verify.
4. **Results.** On 18 loops that need restructuring: DiscoPoP alone 0 of 90 trials; the agent with a small model
   79 of 90 right, race-free and faster, none unusable; the same model alone 38, with 50 unusable. Where the fact that decides the rewrite is not in the file: 44 of 50
   with DiscoPoP's evidence against 14 without, at the speed of an expert's version, and no stronger model alone is
   fast and right in more than 5 of 20.
5. **Limits.** Stronger models alone reach further on plain loops (89 of 90); the agent's reach is bounded by its
   model and by what DiscoPoP confirms; which design options pay (who writes the directive, depth, refresh) is
   stated with the experiments that have run by submission.

---

## 1 Introduction (6–8 pages)

- **1.1 Motivation.** Sequential code on multicore machines; parallelizing it is still manual work. Dependence
  profilers find the loops that are already parallel. A reported dependence ends the story.
- **1.2 The problem.** Two tools, two failures. DiscoPoP alone: nothing on loops that need restructuring (0 of 90).
  A language model alone: many rewrites, but half of a small model's programs are unusable, and it cannot know
  facts that are not in the file.
- **1.3 The idea.** One move: the dependence is a diagnosis. Division of labour: the model exposes parallelism,
  DiscoPoP confirms it and writes the directive, the gate decides.
- **1.4 Two problems the move creates.** *Trust*: a rewrite can be wrong or racy, so every change needs a judge.
  *Cost*: every edit makes the profile stale, and profiling again is expensive.
- **1.5 Research questions.** RQ1–RQ9 as in section 0, grouped under the three claims.
- **1.6 Contributions.** The six of section 0.
- **1.7 Results in brief.** One paragraph with the headline numbers and the limit stated beside them.
- **1.8 Structure of the thesis.**

## 2 Background (10–12 pages)

- **2.1 Shared-memory parallelism with OpenMP.** Worksharing loops; data-sharing clauses (`private`,
  `firstprivate`, `lastprivate`, `reduction`); schedules; what a data race is.
- **2.2 Data dependences.** Read-after-write, write-after-read, write-after-write; carried by a loop or inside one
  iteration; why a carried dependence forbids a parallel loop.
- **2.3 Restructuring transformations.** The moves an expert makes, with one small example each: splitting a loop
  (distribution), privatizing or expanding a scalar, peeling an iteration, aligning statements, replacing a
  carried variable by a closed form, recognising a reduction. These are the transformations the benchmark loops need.
- **2.4 DiscoPoP.** The static pass and the instrumentation; the profiling run; computational units and the
  dependence graph; the pattern explorer (Do-All, reduction and others); the patch generator; hotspot detection.
  What its answers mean: observed on one input, hence optimistic; not the same from run to run; profiling cost.
- **2.5 Language models as coding agents.** Tool-using models that edit files; variation between runs; why a
  feedback loop needs a judge outside the model.
- **2.6 Checking parallel programs.** Race detection (ThreadSanitizer with Archer); testing by output and its
  limit (a check sees only the inputs it runs); floating-point sums change with the order of additions; behaviour
  that depends on the schedule.
- **2.7 Measuring speed-up.** Problem size, timing noise on a shared machine, pinning, the sequential reference.

## 3 Related work (6–8 pages)

*Placement: after the background (recommended) or after the evaluation — decision 2 in section 11.*
*The works named below are candidates from memory. Every reference is to be verified before it is cited.*

- **3.1 Automatic parallelization by compilers.** Polyhedral and classic parallelizers (Polly, Pluto, Cetus,
  ROSE): static and conservative. Polly is measured as a baseline in chapter 7.
- **3.2 Dependence profiling and parallelization advice.** DiscoPoP and its relatives (Kremlin, Parwiz, vendor
  advisors): they suggest directives for the code as it is; they do not change it.
- **3.3 Learned directive prediction.** Models that predict whether and which directive a loop needs
  (PragFormer, OMPify, Graph2Par and similar): no rewriting, no verification.
- **3.4 Language models that write or transform parallel code.** Fine-tuned and general models (HPC-Coder, OMPGPT,
  AutoParLLM and similar), and agents with tools. The closest published system, RepoOMP (arXiv 2608.05855), is
  compared head-to-head in 7.9.
- **3.5 Verifying parallelizations.** Race detectors and their benchmarks (DataRaceBench); equivalence testing of
  transformed code.
- **3.6 Benchmarks.** TSVC, PolyBench, NPB, Rodinia, LULESH; the problem that models have seen public benchmarks.
- **3.7 Position of this thesis.** One table: system · changes the code? · uses measured dependences? · who writes
  the directive · how results are verified.

## 4 Approach: the agent (20–24 pages)

Follows the pipeline page stage by stage. Each design decision is given with its reason and with the decision
number of the record (D-numbers), so the text can be checked against the repository.

- **4.1 Principles.**
  - DiscoPoP's measured dependences are trusted as evidence; its directives are checked.
  - The model exposes parallelism, DiscoPoP writes the directive, the gate decides.
  - No rule-by-pattern shortcuts: nothing is accepted or refused because of how the code looks.
  - The agent never grades itself: the verdict comes from a harness outside it.
  - A model's claim may enter the analysis only in the direction where an error costs an opportunity, not
    correctness (adding a dependence is safe, deleting one is not).
  - Every text the model reads is true and carries no hint. Every default is a decision with a reason.
- **4.2 Overview.** Figure: the pipeline. Profile → start-up → planning → restructuring, one region at a time,
  with the file kept free of directives → annotation, once → verification of the finished file → the floor.
  A running example is carried through the chapter: one loop that must be split, from DiscoPoP's report to the
  accepted program.
- **4.3 Start-up.** The DiscoPoP profile. The references every later check is measured against: the output on the
  shipped and on a perturbed input, the program's own numerical noise, its runtime and timing noise. What DiscoPoP
  alone can do with the program (kept as the floor).
- **4.4 Planning: where to look.**
  - Regions: loops and functions from DiscoPoP's data. Two kinds: DiscoPoP already reports a pattern (no model
    needed) or it does not (the model is asked).
  - Ranking by measured time saved (Amdahl's law over DiscoPoP's hotspot measurement) instead of a static
    instruction count (`--hotspots`); the case that caused the change (a 0.1 ms checksum loop ranked first).
  - Filters: share of runtime (`--min-runtime-share`, 1 %), predicted seconds saved (`--min-impact`), functions
    that are out of scope.
  - Attempts per region: a fixed number (`--budget`, 3) or scaled with the region's share (`--budget-policy`).
- **4.5 Evidence: what the model is told.**
  - The region's code; what DiscoPoP names as the obstacle (which variable, which kind of dependence, between
    which statements); how DiscoPoP classifies the variables; loop trip counts; dependences seen only statically.
  - The order statement: when the measured dependences fix the order in which two statements must run, this is
    said as a fact. Why it was introduced (the first wording named the dependence but not what follows from it).
  - Evidence as a switch (`--evidence`: none, location only, another tool's remarks, full) and the prompt
    versions 1 to 4, with what changed in each and why (the prompt review).
  - What the model is not told: no name of a transformation, no solution vocabulary, no note of ours in the file.
- **4.6 The model call.**
  - Editing modes: the model edits a private copy of the file (default), returns a diff, or returns a function.
  - Confinement: file tools restricted to the working copy; shell, web and search blocked.
  - Retries that cost nothing (format, build errors) and attempts that count.
  - What goes back after a failure: the check that failed and its message; DiscoPoP's answer when the rewrite
    exposed nothing; the measured ratio when it was not faster.
- **4.7 The gate: who judges a change.**
  - Stages in order: lines that belong to the measurement must be untouched → the change applies → it compiles →
    the sequential output equals the original's on every input, within the program's measured numerical noise.
  - For a change that carries a directive: OpenMP build, clause check, race detection, a matrix of thread counts
    and schedules, and the speed check — paired timing against the program before the change, at a size where
    speed can be measured.
  - What each stage is for, and what none of them can see: inputs and sizes that are not run, dependences the
    input did not exercise.
- **4.8 After a rewrite passes.**
  - Profile again and ask DiscoPoP's question: is there now a pattern in the changed lines? If not, revert and
    tell the model.
  - Judging a rewrite the way it will ship (D40): DiscoPoP's directives for the rewrite are staged, checked and
    timed against the program before the rewrite while the model can still react.
  - A region whose DiscoPoP directive the gate refuses goes to the model (Fix 101).
- **4.9 Annotation.** DiscoPoP's directives from the final profile, each derived again against the current file,
  checked, timed for what it adds; directives that only pay together are judged as a set (D33); a set already
  judged is reused (D41).
- **4.10 Verifying the finished file, and the floor.** Rebuild from the change log, check the whole file again,
  time it against the original, drop changes newest-first until it holds. Never ship a program slower than
  DiscoPoP's own (D32).
- **4.11 The design space.** Each option is implemented, switchable, and measured in chapter 7.
  - **4.11.1 Who writes the directive.** DiscoPoP after a re-profile (default since D23) or the model, together
    with its rewrite (`--llm-pragmas`), with the gate as the judge. Where both claim a loop: arbitration. The two
    clause rules. Why the default changed.
  - **4.11.2 How the evidence survives an edit.** Full re-profile (default since D27) or fast refresh
    (`--fast-refresh`): compile only and translate the earlier run's observations onto the new code. What a
    refresh cannot know: the dependences of code that did not exist when the program last ran. Where a refreshed
    profile may decide and where it must not.
  - **4.11.3 Closing the refresh's gap with the model.** Reconstruction (`--llm-recon`): the model reports the
    dependences of the code it just wrote — it adds; asked in a follow-up call or folded into the rewrite call.
    Review (`--llm-deps`): the model deletes static dependences it calls spurious. The soundness principle of 4.1
    says the first is safe and the second is not; chapter 7 tests exactly that.
  - **4.11.4 How deep to chain restructuring** (`--restructure-depth` 0, 1, 2). What a deeper level may see
    (D2′, Fix 76), what it costs (a full re-profile and new runtime measurement before each level), and the risk
    (each level moves the code further from the original; a rewrite can be slower sequentially).
  - **4.11.5 Where to look first.** Measured time saved against the static count (4.4).
  - **4.11.6 What the model is told and how often it may try.** Evidence on or off; one attempt or three.
  - **4.11.7 The speed check.** Off, on at a measurable size, on at the agent's small size (D8, D22).
  - **4.11.8 The model.** Haiku and Sonnet inside the agent; an open model through an OpenAI-compatible endpoint
    as a capability.
  - Table: every setting of the agent with its role — studied (with its hypothesis), held fixed (with the
    reason), or plumbing.
- **4.12 Programs of more than one file.** The whole program profiled through one generated translation unit, so
  DiscoPoP sees every function; which files may be changed; a project's own build command. Needed for LULESH and NPB.
- **4.13 Limits of the design.** The gate tests at the inputs and sizes it is given. DiscoPoP's answers come from
  one run. The agent's reach is its model's reach.

## 5 Implementation (8–10 pages)

- **5.1 Architecture.** Layers — planning, evidence, model, gate, directives, source edits, profiling, phases —
  and the controller. Figure: data flow from DiscoPoP's files to the accepted program.
- **5.2 Working with DiscoPoP.** Compiler wrappers; the explorer with a time limit and retries on the same
  profile; profile snapshots and restore; loop counters and file mapping.
- **5.3 Reversible edits.** The change log; applying, replaying and reverting a change.
- **5.4 Toolchain.** LLVM 19 and 20; building Archer where the system ships none; what the race detector reports
  around OpenMP barriers and how the agent treats it (Fix 104).
- **5.5 Timing inside the agent.** Interleaved paired runs, the noise threshold, the timing size.
- **5.6 Testing the agent.** The deterministic feature checks (68, no model), unit and end-to-end tests, type checks.
- **5.7 What was fixed in DiscoPoP.** Table of the defects with cause, effect and how each was found: a Do-All
  verdict that changed between runs (B4); a call into code outside the project (B8); a callee's accesses lost
  (B9); a carried scalar reported Do-All (B10); a failed instrumented build reported as success (B12); a
  write-after-write that did not block Do-All (B13); two loops side by side modelled as nested (B14);
  dependences lost after a `do … while` (B15); loop tracking switched off by the length of a path (B17); the
  outer loop of a nest blocked on its inner counter (B18, one of our own fixes meeting older code); a wrong
  `lastprivate` in three places — a value assigned under a condition, a whole array, a variable of the code
  around the loop (B19; its array rule corrected the same day, after the server's draws showed a work array
  shared that each thread needs for itself); the earlier crashes (B1–B3, B5). Not fixed: the patch generator's hang (B6); loop
  counts paired with the wrong loops (B7: cause found, worked around in the agent); four candidates, each
  measured and reproduced — a dependence of the surrounding loop charged to the inner loop (B16); a call that
  does not return inside a nest (B20); an analysis that on one profile blocks every loop carrying an observed
  dependence or none of them (B21, PolyBench); a write-after-read between iterations that never blocks a loop,
  also on an array element (B22). Limits met: programs DiscoPoP cannot profile in reasonable time (L1–L5).
- **5.8 The repository.** Layout, the experiment registry, how a number in the thesis is traced to a file.

## 6 Evaluation method (12–14 pages)

- **6.1 Claims, questions, hypotheses.** The table of section 0 with the hypotheses H1–H13 as they were written
  down before the runs, each with what would refute it.
- **6.2 The comparison is three-way.** DiscoPoP alone (its suggestions through the same gate) · DiscoPoP with the
  agent · the model alone (D35, D37). For the design options: the twin of each setup (D38), so that an effect
  inside the agent can be told from an effect on the model. Outside baselines: the sequential original (the
  reference), expert OpenMP, Polly, RepoOMP's released outputs.
- **6.3 The harness and its verdict.** One profile per benchmark and run, shared by all setups. One outcome per
  trial, decided outside the agent: right, race-free and faster · parallel but not faster · unchanged · unusable.
  A program that changed the measurement code has no valid measurement and is listed separately. The separate
  race check over every shipped program. Whether the parallel construct covers the loop under study.
- **6.4 Benchmarks.** TSVC-2 (ground truth for restructuring: 18 loops of class R, 3 of class A, 4 of class D);
  constructed kernels with a hidden order and why they were needed (no real benchmark has one); PolyBench; NPB;
  Rodinia; LULESH. Admission rules decided without a model (D30). Measured classes from three independent
  profile draws.
- **6.5 The benchmark file is an ordinary code file.** The packaging from version 3 to 7 and what each version
  corrected: a header that named the solution (D36), measurement code inside the file, a helper note, a false
  sentence about sizes, repetitions that could be skipped. What the generator now proves per package. Integrity
  checks around every trial.
- **6.6 Sizes, threads, machine.** Verification size by measurement (at least one second sequentially); 6 and 12
  threads; five timing repeats; four pinned groups of 12 cores on a two-socket server; timing noise.
- **6.7 The instruments are proven first.** One table: study · question · result. Sizes; DiscoPoP's variation
  between profiles and within one; whether the output check can see a wrong program (it could not on
  `seidel-2d`); timing noise; where the runtime goes; packaging equivalence (five studies);
  fast-refresh fidelity; expert references; measured classes; what the default setup can keep at best when handed
  a perfect rewrite (16 of 18).
- **6.8 Statistics.** Repeats sized to the claim; paired tests per loop; exact tests for stratified two-by-two
  tables; intervals on every rate; one error budget across all confirmatory tests; unsafe programs as named
  cases, never a p-value. Failures are sorted by cause with a written codebook, so the chapter can say why and
  not only how often.
- **6.9 Models, versions, cost.** Model identifiers and tool versions per run; cost reported as time, model calls,
  tokens and API-equivalent dollars.
- **6.10 Deviations.** What went differently from the registration and how each case is reported (appendix A).

## 7 Results (26–32 pages)

Order as on the campaign page: first the whole system, then one region through each stage of the agent. Every
section has the same fields: question · hypothesis · setups · benchmarks and repeats · what is read out ·
result, or the expectation written down before the run.

- **7.1 The instruments.** **[done]** What chapter 6.7 promised, with the numbers that matter later: DiscoPoP alone
  varies between profiles; expert versions reach 1.33× to 5.51× (median 2.95×) on class R.
- **7.2 The whole system: coverage and safety** (E1; RQ1–RQ3; H1, H2, H4, H13). **[done on kernels]**
  - Setups: DiscoPoP alone · the agent with Haiku · Haiku, Sonnet, Opus and Fable alone. 18 loops × 5 trials,
    with class-A and class-D controls.
  - Result on clean files, corrected: DiscoPoP alone 0 of 90; the agent 79 with none unusable; Haiku alone 38
    with 50 unusable; Sonnet 77 with 11; Opus 89; Fable 89. The agent declines all 12 class-D trials.
  - Read with it: how the comparison developed (five runs, each on a corrected instrument: 44 → 51 → 71 → 65 → 73,
    and 79 after three corrections: one loop on the fixed profiler, two loops on packages in which no repetition
    can be skipped, one loop run again on the repaired DiscoPoP) and what each correction was; that the table
    then holds agent trials on three DiscoPoP versions, said with it; where the agent's lost trials go (after the model, not in it);
    what the claim is and is not — the pipeline makes a small model safe and beats DiscoPoP alone; it does not
    out-reach a strong model alone on loops whose dependences are visible.
  - One loop where the agent ends with nothing and every model alone succeeds in one call (`s331`): the loop
    needs a maximum reduction; DiscoPoP wrote a `lastprivate` that gives wrong results, and the checks refused
    it every time (B19, repaired 8 Oct: DiscoPoP no longer calls this loop parallel). The bridge to 7.7.
  - Worked examples from the archived trials: a rewrite the agent kept, one it reverted and why, one the model
    alone shipped wrong.
  - The replay, without a model, of the rewrites the agent discarded before the profiler fix: two trials on
    one loop had thrown away a rewrite that is right and 1.8× faster once DiscoPoP reports both of its loops.
    The count was 76 measured, at most 78; the other discarded rewrites were dropped for good reason. Run again
    on the repaired DiscoPoP, that loop is faster in 5 of 5 trials, all race-free: 79 of 90. (A replay bounds
    what the old trials' rewrites could reach, not what a new run writes.)
- **7.3 A small model inside the pipeline against stronger models alone** (E12). **[done]** On the two
  hidden-order kernels only the Haiku agent is ever faster (20 of 20; every model alone 0); on four real loops
  the strong models alone are as good or better.
- **7.4 Stage 1 — where to look** (E9; RQ9; H9). **[planned]**
  - Question: does ranking by measured time saved spend fewer model calls before the first success than the
    static count?
  - Setups: ranking on against off, with twins. Benchmarks: LULESH and NPB kernels (a kernel with one loop has
    nothing to rank), three repeats. Offline, from the main comparison's logs: how well each ranking predicts
    the time actually saved; what a floor of 10, 50 or 100 ms would have skipped.
  - Read out: model calls before the first faster program; time saved per call; share of calls spent on regions
    under 1 % of the runtime.
- **7.5 Stage 2 — what the model is told, how often it may try, how strong it is** (E2; RQ4; H5, H5b, H5d, H12).
  **[done]**
  - 7.5.1 The evidence as first worded did nothing, and why: on loops whose dependences are visible the model
    needs no evidence, and the speed was lost after the model's turn.
  - 7.5.2 Where the deciding fact is not in the file. The line of experiments (constructed kernels, three more
    ways of hiding the order, clean files) and its result on the fixed DiscoPoP: 44 of 50 with evidence against
    14 without; the programs run at the expert's speed (4.07× against 4.14×); no unsafe program in 280 trials.
  - 7.5.3 Retries with feedback: 22 of 50 at eight times the calls per success; against 14 at one attempt the
    effect is not established. Stated with it: where nothing can be gained, retries produce pointless parallel
    programs (10 of 20).
  - 7.5.4 Model strength: no model alone is fast and right in more than 5 of 20 on the hidden-order kernels.
  - 7.5.5 The first run of this experiment, on the profiler with the defect, as part of the story: it is how
    defect B14 was found.
  - Dropped: the evidence's parts given one by one and the prompt's parts left out one by one; the small open
    model.
- **7.6 Stage 3 — who judges the result** (E10, E7; RQ2; H3, H10, H10b).
  - 7.6.1 The speed check. **[done]** On, at a measurable size: 11 faster, nothing slower kept, nothing wrong.
    Off: 8 faster, 5 slower programs kept, 1 wrong. On at the small size: 2 faster, 16 of 18 unchanged — it drops
    DiscoPoP's own good directives.
  - 7.6.2 The unsafe programs that did occur, each by name and cause. **[done]** A racy program the barrier rule
    excused; three programs with data-sized arrays on the stack that crash at the verification size (only in
    setups with the speed check off); a false Do-All from DiscoPoP that the race stage refused. And one wrong
    refusal with a known cause: the check against DiscoPoP's observed dependences compared line numbers of the
    working file with those of the profiled file and refused a correct directive below an accepted one (once
    among the 14,200 candidates of the whole archive; found 8 Oct). Counted from the archive: on the loops of the
    two main experiments it only made the check silent (149 of 569 directives, no other loop read); on whole
    programs it read an inner loop's record for 19 of 248 directives. What its repair changes has not been counted (7.6.3).
  - 7.6.3 The gate as a classifier. **[dropped for now, 9 Oct, by the author — designed, not run]** What the
    thesis reports instead, from the runs in hand: the harness judges every final program on its own, and in the
    283 trials of the two main experiments in which the agent changed the source it found no wrong program (the
    models alone: 51 of 450 wrong or not verifiable); the race checks of the agent's final programs reported
    nothing (279 clean); and one early look at single candidates (18 Sep, 82 candidates): 14 of 23 wrong ones
    were stopped by the second input only, 2 correct programs were refused. Stated as limits, not measured:
    what each check catches that the others miss (H3 stays open); how many correct candidates the checks refused
    — 576 of the 1,389 distinct programs they judged were refused and never judged by anything else, and 105 of
    the 248 directives DiscoPoP alone offered on the 75 packages; how the race check does on programs with
    labelled races. The design (every saved candidate judged again by the harness, each check on its own,
    DataRaceBench from outside) is kept in the record and needs no model call — it can be run at any point and
    would turn each of these limits into a number.
- **7.7 Stage 4 — who writes the directive, and how the evidence survives the edit** (E3, E4; RQ5–RQ7;
  H6, H6b, H7, H7b). **[7.7.1 done 10 Oct; 7.7.2 planned — two experiments, split by the author on 9 Oct]**
  - 7.7.1 Who writes the directive (E3): DiscoPoP, as the agent does now, or the model in the same edit as its
    rewrite — the whole program profiled again after every kept rewrite in both. Two setups on the main
    comparison's whole set: 18 loops that need restructuring × 5, four loops with a true recurrence × 3, three
    loops DiscoPoP alone parallelizes × 1 (25 loops, 105 trials per setup, 210 trials); DiscoPoP alone run again
    beside them, the models alone taken from 7.2. The setup in which the model writes is, as built and as its
    instructions now say, "the model may write, DiscoPoP adds what it can": DiscoPoP still adds its own
    directive to a loop it finds parallel that carries none; it never replaces the model's (the timing of the
    two against each other is switched off for this experiment). The instructions of this setup had described
    the model alone's situation, not the agent's; they and three sentences about what DiscoPoP "observed" were
    corrected before the run (a new version of the texts; the finished experiments keep theirs). No trials of
    the agent without its checks, so the claim that a factor acts through the checks (H12) is not tested here
    and the thesis says so. The motivating case: `s331` of 7.2.
    **Result (10 Oct; 315 trials, no failed model call, every changed program race-clean).**
    - *The counts.* On the 18 loops: fast and race-free in 81 of 90 trials where the model writes, 76 of 90 where
      DiscoPoP writes, 38 of 90 for the model alone (7.2). Unusable programs shipped: none in either setup's 105
      trials. On the four recurrence loops: nothing shipped by either.
    - *The two tests written down before the run.* More fast and race-free trials where the model writes: not
      established (one-sided p = 0.142, exact 0.140, odds ratio 2.0 with interval 0.70–5.68), and not refuted
      (no more unusable programs). With the model writing, the agent reaches at least what the model alone
      reaches and ships nothing wrong: holds (ahead on 15 loops, behind on none).
    - *Where the difference sits.* Ten loops at 5 of 5 in both. `s331`: 5 of 5 against 1 of 5 — the loop needs
      a directive DiscoPoP cannot write (a maximum of an index, or a guarded update); the model wrote it at its
      first call in four trials, while with DiscoPoP writing the model must find a two-pass rewrite DiscoPoP
      can annotate. One or two trials either way on six more loops.
    - *The recurrence loops.* Where the model writes it put a directive on a true recurrence 144 times and the
      checks refused every one (wrong output 65, a race 24, the schedule test 1, 42 not compiling or breaking
      a clause rule, 12 correct but not faster). It costs more there ($3.70 a trial against $2.54).
    - *Who wrote the kept directives where the model may write:* 150 the model's, 9 DiscoPoP's.
    - *Cost.* $175.03 for both setups ($84.49 and $90.54); 465 and 446 model calls.
    - *To say with it.* (a) The setup in which DiscoPoP writes reached 76 where 7.2 has 79 on the same loops;
      texts and DiscoPoP changed in between, so it is not a repetition and the cause is not known. (b) Seven of
      the model's fast programs open one parallel region around the repetition loop — threads started once, a
      form DiscoPoP's directives never take; no trial of the comparison turns on it, their speed-ups are not
      comparable. (c) `s341`: the one win in each setup, and the four of 7.2, compute the positions once in
      front of the repetition loop — right on the tested data only (the routine called between repetitions
      changes the array); the thesis states the cell with this limit, and 7.2 also without the loop (75 of
      85), unless the author decides to change the loop's data and run it again. (d) One control program
      (`s000`, 127.70×) runs the loop once instead of in every repetition: exact output, not a parallel
      speed-up, in no test.
    - *Limits.* Five trials per loop; one model; the lead sits on few loops; the timing of two directives
      against each other was off.
  - 7.7.2 The fast refresh, with the model reporting the dependences of the code it wrote (E4). An experiment of
    its own after 7.7.1 (the author, 9 Oct); whether DiscoPoP or the model writes the directive in it is the
    author's decision, open since 10 Oct: under the rule proposed before 7.7.1 the model would write (met exactly,
    81 − 76 = 5), but the refresh decides something only where DiscoPoP writes — where the model writes, the
    checks alone judged 441 of the 446 rewrites. Already known from the main comparison: on
    the 18 loops the profiling run the refresh skips is 0.08 % of the agent's time (188 re-profiles in 90 trials,
    0.17 s each), so the saving can only be measured on programs whose profiling run is long (53 s, 31 s and
    21 s on three whole programs in the archive). What it is compared against (the full re-profile; the fast
    refresh without the model's report), on which programs and how many trials: fixed when it is planned. Read
    out: profiling seconds per kept rewrite; decisions that differ from the full re-profile, split into unsafe
    and over-cautious; extra calls. Written down before the run: the refresh can only change a decision where
    DiscoPoP, not the gate, judges the rewrite.
- **7.8 Stage 5 — how far to chain restructuring** (E8; RQ8; H8). **[planned]** Depth 0, 1 and 2 with twins,
  18 loops × 3 (108 new trials). Read out per level: speed-up gained, regions seen and regions parallelized,
  re-profiles, calls and time, unusable programs, the sequential cost of kept rewrites. Written down before the
  run: on single-nest loops depth 0 should suffice, so no difference is the expected result and a finding; a
  first small run must show that a deeper level is ever entered, or the experiment is dropped and that is said.
- **7.9 Scale and the outside comparison.**
  - A large code: LULESH (E6). **[planned]** Does the loop still work when one profile takes 28 GB? Setups:
    sequential, DiscoPoP alone, the agent, the model alone, the laboratory's own OpenMP version.
  - The closest published system: RepoOMP on its eight NPB kernels (E11; H11). **[planned]** Every contestant
    through one verification: the agent, RepoOMP's released outputs and baselines, NPB's expert version, DiscoPoP
    alone, Polly. Written down before the run: little benefit from the agent's default here, because that code
    is already restructured and what remains is writing directives. Limits stated with the result: their outputs
    were produced on other hardware and with other models, and their repository builds without optimisation, so
    their own reported acceptance is shown beside ours.
- **7.10 Cost** (C3). **[partly]** Model calls, tokens, time and API-equivalent cost per success from every run
  (recorded). Profiling time per kept rewrite from 7.7. The profile of a large code from 7.9. The separate
  cost-curve experiment was dropped (it measures DiscoPoP, not the agent).
- **7.11 What the campaign found in DiscoPoP.** **[done]** The defects by their effect on results: programs held
  to half their speed and a recurrence reported as parallel (B14); verdicts that were a draw (B4); a wrong
  clause that shipped in one program and crashed three others at the larger size (B19); outer loops of PolyBench
  nests lost and given back (B18). Open, and it decides how PolyBench may be described: on one profile DiscoPoP's
  analysis blocks every loop that carries an observed dependence, or none of them — over nine draws "none" in 133
  of the 198 profiles of the 22 kernels that ever block, never a part — so that "DiscoPoP alone" there is what DiscoPoP offered and the checks let through (B21); on TSVC
  the loops called parallel and the loops blocked do not vary, the dependence named for a blocked loop does (on one
  loop also its kind). A loop whose iteration reads an array element a later iteration overwrites is called
  parallel (B22), hidden on TSVC by B16. The rule: the fixed version in every setup.
- **7.12 The answers, question by question.** One table: question · answer · evidence · status.

## 8 Discussion (6–8 pages)

- **8.1 What restructuring adds, and where it stops.** The agent reaches what its model can write and DiscoPoP can
  confirm.
- **8.2 Trust.** Why the pipeline makes a small model safe; where the gate is blind and what would close each gap.
- **8.3 Evidence against feedback.** A measured fact the file does not show is worth more than retries.
- **8.4 Strong models alone.** Further reach on plain loops, unsafe or slow where the order is hidden; what that
  means for a tool like this one.
- **8.5 Lessons for evaluating tools built on language models.** Benchmark files as ordinary code; hints that
  leak; instruments first; registration and deviations; the three-way comparison.
- **8.6 Threats to validity.** Constructed kernels; one model family; public benchmarks the models may have seen;
  one shared machine; few repetitions per cell; what the output check cannot see; DiscoPoP's own variation.

## 9 Conclusion and future work (3–4 pages)

- **9.1 What was shown.** Coverage and trust, with the numbers.
- **9.2 What was not.** Whatever of the design space has no result by submission, named as such.
- **9.3 Future work.** A gate that knows about sizes and inputs; stronger and open models inside the agent;
  beyond loops (tasks, sections); larger codes; the DiscoPoP fixes upstream.

## Appendices

A. The pre-registration and every deviation · B. Benchmarks, packages and measured classes · C. Every text a
model reads, by prompt version · D. DiscoPoP defect reports · E. Reproducibility: repository, commits, the map of
the results folder · F. Full result tables · G. The agent's command-line reference.

---

## 10 Figures and tables planned

| | Content | Section |
|---|---|---|
| Fig. 1 | The pipeline, one stage per box | 4.2 |
| Fig. 2 | The gate's stages and what each refuses | 4.7 |
| Fig. 3 | Two-by-two: who writes the directive × how the profile is refreshed | 4.11 |
| Fig. 4 | Outcomes per setup in the main comparison | 7.2 |
| Fig. 5 | Speed-up per loop beside the expert version | 7.2 |
| Fig. 6 | Where trials are lost on the way through the agent | 7.2 |
| Fig. 7 | Evidence × attempts: successes of 50, with the models alone | 7.5 |
| Fig. 8 | Speed of the successes beside the expert version | 7.5 |
| Fig. 9 | The gate against the harness: confusion matrix | 7.6 |
| Fig. 10 | Decisions under fast refresh against the full re-profile | 7.7 |
| Fig. 11 | Gain and cost per restructuring depth | 7.8 |
| Tab. 1 | Questions, claims, hypotheses, experiments, status | 1.5, 7.12 |
| Tab. 2 | Related systems compared | 3.7 |
| Tab. 3 | Every setting of the agent and its role | 4.11 |
| Tab. 4 | DiscoPoP defects fixed and open | 5.7 |
| Tab. 5 | Benchmarks and measured classes | 6.4 |
| Tab. 6 | The instruments and their results | 6.7 |
| Tab. 7 | Cost per success, per setup | 7.10 |

## 11 Decisions the outline needs

1. **Title.** Three candidates in section 0. Recommended: the first — it says the idea, not the tool. The case
   for the third: it names the system the way the repository and DiscoPoP's users would look for it.
2. **Related work after the background or after the evaluation.** Recommended: after the background — the reader
   needs to know what annotation tools and language models do before the approach makes sense. The case for the
   other place: the thesis measures its neighbours (Polly, expert OpenMP, RepoOMP), so the field could be
   discussed with the numbers on the table.
3. **The cost claim (C3).** Recommended: keep it as a claim only if the fast-refresh experiment of 7.7.2 has run; otherwise C3
   becomes a design contribution with its experiment registered, and moves to future work. The case for keeping
   it regardless: the fast refresh and the reconstruction are built and tested, and the soundness principle
   behind them is a contribution even without the measurement.
4. **Which planned experiments must run before submission.** Order: the two-by-two, depth, then ranking,
   LULESH and RepoOMP as time allows. The gate as a classifier was set aside by the author on 9 Oct (no model
   calls; it can be run at any point — until then 7.6.3 states its questions as limits). Each planned section is
   written so that it can move to future work without changing the chapter's structure.
5. **Nine chapters or six parts.** See section 12.

## 12 Folded into the six default parts

| Default part | Holds |
|---|---|
| Abstract | Abstract |
| Introduction | chapter 1 |
| Related work | chapters 2 and 3 (background first) |
| Approach | chapters 4 and 5 |
| Evaluation | chapters 6, 7 and 8 |
| Conclusion | chapter 9 |

## 13 Where the thesis stands today

| Claim | Supported by | Status |
|---|---|---|
| Coverage (C1) | the main comparison; the hidden-order experiments | **supported on kernels**; a large code and RepoOMP planned |
| Trust (C2) | no unusable program in the main comparison; the speed check; the unsafe cases named | **supported**; the gate's own error rate planned |
| Cost (C3) | calls, time and cost recorded in every run | **no result yet** on refresh, reconstruction and depth |

Dropped, to be said in the thesis with the reason: the profiling-cost curve (26 Sep: it measures DiscoPoP, not
the agent); the small open model as a third model; the evidence's parts and the prompt's parts given one by one
(2 Oct: the experiment was closed); the first clean-file layout (4 Oct: stopped after eight trials, replaced by
TSVC's own form).
