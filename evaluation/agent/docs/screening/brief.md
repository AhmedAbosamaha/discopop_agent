# Benchmark screening — brief (26 Sep 2026, written after the properties were recorded)

READ-ONLY: never modify `/Users/ahmedsamir/discopop_agent`. Do not build, run or profile anything (the Mac is small): read sources, grep, and (external agent only) fetch web pages. Cite file:line (or URL + function) for every claim; say "unverified" when you cannot check.

## The system
An LLM agent that parallelizes sequential C/C++ with OpenMP on top of DiscoPoP (a dynamic dependence profiler). DiscoPoP profiles the program, reports parallel patterns (Do-All, reductions with operators `+ - * & | ^` only); where it finds none, the model RESTRUCTURES the code pragma-free; DiscoPoP re-profiles and must find a pattern; a gate (compile, output on two inputs, ThreadSanitizer, thread/schedule stress, speed) judges; DiscoPoP's pragmas are applied. Comparison arms on the SAME benchmarks: DiscoPoP alone, the agent, the model alone (no DiscoPoP, no gate), the agent without the gate ("twin").

## The selection rule (non-negotiable)
A benchmark is chosen by its PROPERTIES, read from the code — never by how any tool or model performed on it. Screen the WHOLE source: list EVERY candidate (every TSVC loop; every Burkardt serial/OpenMP pair; every Rodinia pair; every PolyBench 4.2 kernel), each with its in/out reason per property. An exclusion reason may only be a missing property or a hard constraint below. Classes (R/A/D) are PREDICTIONS here; they are measured later.

## Properties, per experiment (recorded in the thesis record before this screen)
- **C1 / E1:** predicted class R (DiscoPoP alone cannot parallelize the hot loop as written) AND an expert parallel version that changes code beyond pragmas/clauses (a RESTRUCTURING).
- **H13 (every experiment):** the naive `#pragma omp parallel for` on the hot loop would be wrong (race or changed output).
- **E2-B1 / RQ4:** the fact that decides whether the hot loop may run in parallel is NOT in the loop's own statements:
  (a) *hidden dependence* — read alone, the loop admits a parallel reading, but pointer aliasing, index-array values, a data-dependent branch, or a callee's side effect, set OUTSIDE the loop's statements, carries a loop-carried dependence;
  (b) *hidden independence* — the text suggests a dependence that those outside facts rule out.
  Say exactly where the deciding fact sits (same function one line up / another function / initialisation / harness) — "one line above the loop inside the kernel" is weaker than "set in another function".
- **E3 / RQ5:** the correct parallel form needs a construct DiscoPoP cannot generate: min/max reductions (with or without index), array/section reductions, user-defined reductions, scans/prefix sums, atomics/critical, tasks, early exit/cancel. Also list in-pattern `+` reductions as controls.
- **E8 / RQ8 (PRIORITY):** the expert version needs at least TWO DEPENDENT restructuring steps — the second applies to code the first created or exposed (e.g. loop fission exposes a max-reduction loop that then needs privatised partials; skewing then tiling; interchange then distribution). Depth 2 needs three. Describe the steps concretely and why step 2 only becomes possible/necessary after step 1.
- **E9 / RQ9:** ≥ 10 candidate loop regions, with no single one dominating (a program, not a kernel).
- **Controls:** class A (parallel as written) and class D (true recurrence, no faster parallel form known).

## Hard constraints of the pipeline (a candidate failing one is OUT, with that reason)
C or C++ that builds with clang-20 on Linux; OpenMP CPU only (no MPI/CUDA/GPU in the computation); deterministic output that can be compared (or a checksum can be added); input size selectable at compile time (a `-D` size, or a constant we can turn into one); DiscoPoP must be able to profile it (it instruments every memory access: very large state spaces or hour-long runs at a small size are out); single-file programs preferred (a known DiscoPoP defect, B8, mis-reports dependences across two files); license must permit redistribution in a thesis repository.

## Output (one table row per candidate, then a short summary)
Columns: source · name · where (file:line or URL#function) · the hot loop/region (quote ≤ 3 lines) · properties it HAS (C1 / H13 / E2-B1a / E2-B1b / E3 / E8 / E9 / A / D) each with a one-line reason · predicted class · expert/parallel form (what it changes; for E8 the ordered steps) · constraints (license, size, determinism, single-file, D26 risk) · verdict IN (which experiments) / OUT (reason) · duplicate-of (another candidate with the same property and the same fix).
Summary: the IN list per experiment; especially every E8 candidate found, and honest statements where a property has NO candidate in your sources.
