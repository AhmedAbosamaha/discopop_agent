# Measured results — with provenance

Every number here was measured in this codebase. **All of it postdates the
artifact-accumulation fix** (see `07-pitfalls.md`); anything measured before that fix is
void, because the corruption *flattered* the results.

Each entry says what was measured and under what conditions. Nothing here is a
projection. Re-run under final conditions before any of it goes into the thesis.

## Reconstruction repairs unsafe divergence

- **Control arm (`fast-step`, seeded from a full profile): 4 unsafe divergences out of 9
  comparisons.**
- **Reconstruction arm (`fast-llm`): 1 unsafe.** Identical across 3 repeats, and the
  *same three comparisons* were repaired each time.

"Unsafe divergence" = a suggestion the measured profile does not support. This is a
proxy, not a proof of incorrectness — define it precisely in the thesis.

Caveat: only `stencil_war` has been re-measured since the contradiction filter
(`_not_carried`) was added. Re-run all three repeats before writing the contradiction
figure.

## The deterministic pipeline is deterministic

**Zero variance across 10 repeats of the control arm.**

This is not a null result. It establishes that the non-LLM parts of the pipeline are
genuinely deterministic, which licenses attributing all observed variance to the model.
Every later variance claim depends on it.

## Fast refresh deviation is characterised

Across two chains: **39 of 39 dependences a refresh lacks have an endpoint on a rewritten
line, and NONE were carryable.**

The academic framing for this is **from-scratch consistency** — does the incremental
result match what a full re-analysis would produce? Fast refresh is not from-scratch
consistent, and this measurement *characterises the deviation*, which is the standard
thing to do about it.

## Evidence dominates the prompt

**48% of prompt characters** — 3748 → 1986 when `--evidence none` is passed.

This makes RQ4 (does the evidence actually help?) non-trivial a priori: half the prompt is
under test.

## The tool has a soundness bug of its own

**DiscoPoP emits a racy pragma roughly 1 run in 6.**

Two consequences: it justifies the gate (C2), and it means the **DiscoPoP-alone baseline
is stochastic** — single-run comparisons against it are invalid.

## Naive re-gating is a coin flip

Before the noise floor: **5 false failures out of 8 on identical source**, ratios
0.961–1.010. The fix was a margin in `phases/settle.py`; it had been a bare `>`.

## Fast refresh saves the instrumented run only

**8.60 s (prefix_sum) and 7.94 s (array_accumulator).**

This is honest and it is a **problem for C3 as currently evidenced** — 8 seconds does not
motivate a chapter. The cost argument only has stakes at NPB scale, where instrumented
profiling costs minutes to hours. Either climb to that scale, or measure profile cost as a
function of program size and argue the extrapolation explicitly.

## Setup cost

The setup phase runs the program roughly **9 times natively plus once instrumented** —
not 3, which older documents claim.

## Open — measured but needing a re-run, or not measured at all

| Item | Status |
|---|---|
| Three repeats with the contradiction filter active | only `stencil_war` re-measured |
| `--llm-recon` `followup` vs `folded` **inside the agent** | neither mode has a number |
| X1 evidence-section ablation | flag ready, not run |
| X2 small model + evidence vs large model + none | not run |
| X3 gate stage attribution | not run |
| X4 tool-stability study, N=20 | not run |
| B3 (evidence, no gate) / B4 (gate, no evidence) | not run |
| `prefix_sum` step 2 | still unsafe in the LLM arm; separately measured as **not** fixable by adding dependences, on clean profiles |
