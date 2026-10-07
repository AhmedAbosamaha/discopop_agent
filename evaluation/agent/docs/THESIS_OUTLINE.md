# Thesis outline — draft of 7 Oct 2026

Built from the campaign page (`docs/EXPERIMENT_PLAN.html`), the pipeline page (`docs/FLOW.html`), the experiment
record (`docs/THESIS_EXPERIMENTS.md`) and the results folder. Structure as given: abstract, introduction, related
work, approach, evaluation, conclusion. Every evaluation section carries its status:
**[done]** measured and read out · **[partly]** · **[planned]** not run yet · **[open]** a question still to answer.

**Working title (a suggestion):** *Dependences as Diagnoses — an LLM Agent that Restructures Code so that DiscoPoP
Can Parallelize It*

**The thesis in one sentence:** a dependence DiscoPoP reports is read as a diagnosis, not as a limit — a language
model rewrites the loop so that the dependence is gone, DiscoPoP confirms it and writes the OpenMP directive, and
a gate decides whether the result is safe and worth keeping.

---

## Abstract (about 200 words — what each sentence carries)

1. **Problem.** Tools such as DiscoPoP parallelize loops that are parallel as written; where they report a
   dependence, the work stops.
2. **Idea.** Read the dependence as a diagnosis and let a language model restructure the code.
3. **System.** An agent around DiscoPoP: profile, rank, restructure, check, re-profile, annotate, verify.
4. **Results.** On 18 loops that need restructuring: DiscoPoP alone 0 of 90 trials; the agent with a small model
   73 of 90 right, race-free and faster (77 once one loop is corrected for a DiscoPoP defect), none unusable; the
   same model alone 38, with 50 unusable. Where the fact that decides the rewrite is not in the file: 44 of 50 with
   DiscoPoP's evidence against 14 without, at the speed of an expert's version, and no stronger model alone is
   fast and right in more than 5 of 20.
5. **Limits.** Stronger models alone reach further on plain loops (89 of 90); the agent's reach is bounded by its
   model and by what DiscoPoP confirms; the cost claim is not measured yet.

## 1 Introduction

- **1.1 Motivation.** Parallelizing existing code is still manual. Dependence profilers find the loops that are
  already parallel; a reported dependence ends the story.
- **1.2 The idea.** One move: the dependence is a diagnosis. The model removes it, DiscoPoP checks that it is gone.
- **1.3 Two problems the move creates.** *Trust* — a rewrite can be wrong or racy, so every change needs a judge.
  *Cost* — every edit makes the profile stale, and profiling again is expensive.
- **1.4 Research questions**, grouped by the three claims of the campaign page:
  - Coverage (C1): does restructuring parallelize what DiscoPoP alone cannot, and how close to an expert does it get?
  - Trust (C2): is every accepted change right and race-free, what does each check catch, and where is the gate blind?
  - Cost (C3): can DiscoPoP's evidence stay valid across edits without profiling from scratch?
  - Inside the pipeline: what does DiscoPoP's evidence add, what do retries add, how much does the model's strength
    matter, who should write the directive, how deep should restructuring go, where should the agent look first?
- **1.5 Contributions.** (1) the agent; (2) the gate; (3) an evaluation method that holds itself to a stated
  standard — hypotheses fixed before the runs, a three-way comparison, benchmark files that are ordinary code,
  instruments proven first; (4) the results; (5) defects in DiscoPoP found and fixed at the root.
- **1.6 Structure of the thesis.**

## 2 Background and related work

*Placement.* Two honest options. **After the introduction** (recommended): the reader needs dependence profiling
and DiscoPoP before the approach makes sense. **After the evaluation**: the thesis measures its neighbours (Polly,
expert OpenMP, the closest published system), so the field can be discussed with the numbers on the table instead
of listed before them. With the first option, the measured comparison still lives in the evaluation.

- **2.1 Background.** OpenMP worksharing and data races; loop-carried dependences; how DiscoPoP works (static pass
  and instrumentation, the profiling run, the pattern explorer, the patch generator); what "DiscoPoP alone" can
  and cannot do.
- **2.2 Automatic parallelization.** Polyhedral and compiler parallelizers (Polly is measured as a baseline):
  static and conservative.
- **2.3 Dependence profiling and parallelization advice.** DiscoPoP and its relatives: they suggest directives for
  the code as it is; they do not change it.
- **2.4 Language models for parallel code.** Models that predict directives; models that write parallel code;
  agents. The closest published system, RepoOMP (arXiv 2608.05855), is compared head-to-head in 4.3.
- **2.5 Checking parallel code.** Race detection (ThreadSanitizer with Archer), testing by output, schedule stress.
- **2.6 What is missing, and what this thesis adds.**

*References are to be verified before citing; this list names areas, not a bibliography.*

## 3 Approach — the agent

Follows the pipeline page stage by stage; each design decision is given with its reason.

- **3.1 Overview and principles.** DiscoPoP's measured dependences are trusted; its directives are checked. The
  model exposes parallelism, DiscoPoP writes the directive, the gate decides. No rule-by-pattern checks. Every
  text the model reads is true and carries no hint.
- **3.2 Start-up.** The profile; what DiscoPoP alone can do with it (the floor); the references every later check
  is measured against — output on two inputs, the numerical noise floor, the runtime.
- **3.3 Planning.** Regions (loops and their functions), ranked by measured time saved.
- **3.4 Restructuring one region.** What the model is told (the code, DiscoPoP's blockers, the order of the
  statements when it matters) and what it is not told; one attempt or several; what goes back after a failure.
- **3.5 The gate.** Compile; race check; schedule stress; equal output on the shipped and a perturbed input with a
  measured noise floor; the speed check at a size where speed can be measured. What each stage is for, and what
  none of them can see.
- **3.6 After a rewrite.** Profiling again; DiscoPoP writes the directives; judging a rewrite the way it will
  ship; the final check of the finished file.
- **3.7 Keeping the evidence valid more cheaply.** Fast refresh; dependences reported by the model for the code it
  wrote (adding is safe, deleting is not).
- **3.8 Variants.** Who writes the directive, evidence on or off, attempts, restructuring depth, ranking — defined
  here, measured in chapter 4.
- **3.9 Implementation.** Structure, the model's sandbox, multi-file programs, platforms.
- **3.10 What was fixed in DiscoPoP.** The defects found on the way, each with cause and effect
  (`DISCOPOP_BUG_REPORTS.md`): a Do-All verdict that changed between runs, a carried scalar reported Do-All, a
  write-after-write that did not block Do-All, dependences lost under `do … while`, loops side by side modelled
  as nested (found through the hidden-order experiment: it held the agent's programs to half their speed, and it
  could report a recurrence as parallel — which the gate caught), and others; the candidates still open.

## 4 Evaluation

- **4.1 Method.** The questions and the hypotheses fixed before the runs. The comparison is always three-way:
  DiscoPoP alone · DiscoPoP with the agent · the model alone. Outcomes: right, race-free and faster · parallel but
  not faster · unchanged · unusable (wrong, racy, crashing, not compiling). The verdict comes from a harness
  independent of the agent. Benchmarks and their measured classes (parallel as written · needs restructuring ·
  must be left alone). Why the benchmark files are ordinary code and what happened when they were not (a helper
  note, a false sentence about sizes, repetitions that could be skipped). Machine, models, statistics.
- **4.2 The instruments are proven first.** **[done]** Sizes, DiscoPoP's own variation, timing noise, whether the
  output check can see a wrong program (it could not on `seidel-2d`), the expert references.
- **4.3 The whole system.** **[done for the kernels]** The main comparison on 18 loops that need restructuring,
  with controls: DiscoPoP alone 0 of 90; the agent 73 with none unusable; Haiku alone 38 with 50 unusable; Sonnet
  77 with 11; Opus 89; Fable 89. Why the agent is safe but behind the strongest models. Two loops to be re-run on
  the corrected packages. **[planned]** A large code (LULESH) and the head-to-head with RepoOMP on its own programs.
- **4.4 Where to look first.** **[planned]** Ranking by measured time saved against a static estimate.
- **4.5 What the model is told, and how often it may try.** **[done]** First, why the evidence did nothing as it
  was first worded. Then the experiment where the deciding fact is not in the file, on the fixed DiscoPoP: 44 of
  50 with evidence against 14 without, and the programs run at the expert's speed (4.07× against 4.14×). Retries
  with feedback alone reach 22 of 50 at eight times the calls per success; against 14 at one attempt that effect
  is not established. No model alone is fast and right in more than 5 of 20. Stated with it: retries produce
  pointless parallel programs where nothing can be gained. The first run of this experiment, on the profiler with
  the defect, is told as part of the story: it is how the defect was found (section 3.10).
- **4.6 Who judges the result.** **[done]** The speed check: on, at a measurable size, it is the only setting with
  nothing unsafe and nothing below DiscoPoP alone. The unsafe programs that did occur, each by name and cause.
  **[planned]** The gate as a classifier: its error rate and what each stage alone catches.
- **4.7 Who writes the directive, and how evidence survives the edit.** **[planned]** Nothing measured yet.
- **4.8 How far to chain restructuring.** **[planned]**
- **4.9 Cost.** **[partly]** Model calls, time and money are recorded in every trial; the scale study is planned.
- **4.10 Threats to validity.** Constructed kernels; one model family; one shared machine; few repetitions per
  cell; what the output check cannot see; public benchmarks the models may have seen.
- **4.11 The answers, question by question.** One table: question · answer · evidence · status.

## 5 Conclusion

- **5.1 What was shown.** Coverage and trust, with the numbers.
- **5.2 What was not.** The cost claim (C3) has no result yet; the agent's reach is its model's reach.
- **5.3 Limits.** The gate tests at the sizes it is given; DiscoPoP confirms less than is true on some shapes.
- **5.4 Future work.**

## Appendices

A. The pre-registration and every deviation · B. Benchmarks and their measured classes · C. Every text a model
reads · D. DiscoPoP defect reports · E. Reproducibility: repository, commits, the map of the results folder.

---

## Where the thesis stands today

| Claim | Supported by | Status |
|---|---|---|
| Coverage (C1) | the main comparison; the hidden-order experiment | **supported on kernels**; a large code and RepoOMP planned |
| Trust (C2) | no unusable program in the main comparison; the speed check; the unsafe cases named | **supported**; the gate's own error rate planned |
| Cost (C3) | — | **no result yet** — sections 4.7 and 4.9 depend on experiments not run |

Dropped, to be said in the thesis: the profiling-cost curve, the small open model, two parts of the first evidence
experiment.

## Decisions the outline needs from the author

1. The title.
2. Related work after the introduction or after the evaluation.
3. Whether cost (C3) stays a claim if its experiments are not run — or becomes future work.
