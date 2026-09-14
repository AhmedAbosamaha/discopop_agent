# Thesis plan — chapters, contributions, research questions

Full version: https://claude.ai/code/artifact/7de0d7f1-2a30-43ed-b5c1-77cc4d0abfe6

## Contribution claims

- **C1 Coverage — restructuring, not just annotation.** A dependence profiler reports what
  the code *does*. When a loop is not parallel as written, annotation tools stop. The
  agent treats the reported dependence as a **diagnosis** and rewrites the code. The cause
  taxonomy is what makes this systematic rather than anecdotal.
  *Defends against:* "this is a prompt wrapper around DiscoPoP."

- **C2 Trust — a gate strong enough to permit rewriting.** Compile-and-speedup gates are
  calibrated for annotation. Once the code is rewritten they admit wrong results.
  *Defends against:* "how do you know the LLM did not break it?"

- **C3 Cost — keeping dependence evidence valid across edits.** Restructuring invalidates
  the profile that justified it. This is **incremental program analysis**. **The novel
  one** — nobody in the LLM-parallelization literature has it, because nobody else
  restructures.

## Chapters

| # | Chapter | pp | Job |
|---|---|---|---|
| 1 | Introduction | 6–8 | Establish the gap against a reader who knows RepoOMP exists |
| 2 | Background | 12–16 | Only what Ch. 4 needs. Resist writing an OpenMP tutorial |
| 3 | Related Work | 9–12 | Five subsections, each ending with what it leaves open |
| 4 | Design | 18–22 | Every non-obvious decision gets a justification paragraph |
| 5 | Implementation | 8–11 | Only what a reimplementer needs or a reviewer would doubt |
| 6 | **Evaluation** | 24–30 | Structured by research question, never by experiment number |
| 7 | Discussion & Threats | 7–9 | Grounded in what actually went wrong |
| 8 | Conclusion | 3–4 | Restate C1/C2/C3 with numbers attached |

If Ch. 6 is not the longest chapter, the thesis is under-evaluated.

## Research questions

| RQ | Question | Status |
|---|---|---|
| RQ1 | What does restructuring add over DiscoPoP alone? | partial |
| RQ2 | What does the gate catch, stage by stage? | not run |
| RQ3 | What speedup, and at what cost? | not run |
| RQ4 | **Does the evidence actually help?** | flag ready |
| RQ5 | Can profiling be made incremental without changing conclusions? | **measured** |
| RQ6 | Can a model substitute for measurement on code it wrote? | **measured** |

RQ4 is the proposal's unexamined *premise*. RQ5 and RQ6 are new and already have results.

## How to evaluate — the part most papers get wrong

**Classify every suggestion into a 2×2 and report all four cells:**

|  | Actually safe | Actually unsafe |
|---|---|---|
| **Accepted** | true positive — report speedup here and only here | **unsafe acceptance — the failure that matters.** Report as a count, never a rate. Target zero |
| **Rejected** | over-caution — needs a reference parallel version to detect at all | true negative — invisible unless the suite has genuinely unparallelizable cases |

Two consequences: you cannot measure over-caution without reference parallel versions, and
you cannot measure true negatives without unparallelizable cases. **Both are missing from
the current suite.**

**Do not use pass@k.** It rewards any of k samples passing and hides the only cell that
matters.

## Baselines — the ablation cross

| ID | Configuration | Isolates |
|---|---|---|
| B0 | sequential | denominator |
| B1 | DiscoPoP alone | coverage floor — mandatory |
| B2 | LLM, no evidence, no gate | the naive agent; RepoOMP's own baseline |
| B3 | LLM + evidence, no gate | **what the gate is worth** |
| B4 | LLM + gate, no evidence | **what the evidence is worth** = RQ4 |
| B5 | full agent | the system |
| B6 | Polly / Pluto | what classical tools already do on PolyBench |

B3 and B4 turn a system description into an empirical thesis. B3 gives the sentence *"here
is what would have shipped without the gate."*

## Non-determinism is first-class

Three independent sources, all characterised: LLM sampling (N ≥ 5, report distributions),
the tool itself (~1-in-6 racy pragma makes B1 stochastic), and timing (warm-up, pinned
threads, median of ≥ 5).

Non-parametric statistics: medians and IQRs, Mann–Whitney U for pairwise comparisons. **Do
not compute a p-value on a count of unsafe acceptances** — report the count and the cases.

## Benchmarks

**Have:** 9 hand-written cases in `discopop_agent/benchmark/cases/`, organised by cause.
They are a **diagnostic instrument** — a failure says *which* capability is missing. No
standard suite does that. Weakness: small, synthetic, and written by the author.

**Add first — PolyBench/C (~30 kernels).** Highest value per hour. Known-good parallel
forms give the **false-negative oracle**, and it sets up the comparison against
polyhedral tools.

**Then NPB (serial C / SNU).** The credibility benchmark, and RepoOMP used it. Reference
OpenMP implementations plus built-in verification. Realistic scale is where C3 finally has
stakes.

**Also add true negatives** to the existing suite — loops that must be *declined*. Cheap,
and their absence is the most common hole in LLM-parallelization evaluations.

**Recommend against** repository scale (FFmpeg/GROMACS). That is where RepoOMP spent its
effort and where a master's thesis drowns. State it as future work and defend the scope.

**ParEval** — use once, to characterise the chosen model's unaided ability. It is
generation-from-specification, not restructuring, so it does not exercise the pipeline.
