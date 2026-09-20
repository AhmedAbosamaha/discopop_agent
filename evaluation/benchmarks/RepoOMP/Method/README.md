# Method tools

[中文版 (Chinese)](README.zh.md)

Run from the repo root.

## Function-scoped transformation

Analysis records function name, file, inclusive line range, calls, global reads and writes, OpenMP use, loop classes, blockers, and stable evidence ID. Hotspots match by name plus file and line. Missing or ambiguous matches produce identity output.

Only safe hotspot functions enter prompts. Independent functions share a batch only when ranges do not overlap, calls are absent in both directions, dependency matrix has no edge, and shared writes do not conflict. Unknown evidence stays serial. Rules and LLM candidates merge by source range. Edits outside target ranges or beyond OpenMP directives are rejected.

Each batch must compile, pass workload verification, produce finite output with requested thread count, and have best timing no slower than same-workload baseline. Failed batches roll back to last accepted source. Audit files beside outputs record prompts, candidates, diffs, status, rejection reason, timing runs, hashes, and final hash.

## MAP, routing, STC

```bash
python3 Method/dependency_analysis/map_builder.py \
  --root benchmark/NPB3.0-omp-C/CG \
  --out res/method_run/map.json
python3 Method/dependency_analysis/route_router.py \
  --map res/method_run/map.json \
  --out res/method_run/routes.json
```

Pick a function ID from `res/method_run/routes.json`, then build STC:

```bash
python3 Method/dependency_analysis/stc_builder.py \
  --map res/method_run/map.json \
  --routes res/method_run/routes.json \
  --function 'function:cg.c:conj_grad:227' \
  --out res/method_run/stc.json
```

MAP records file nodes, function nodes, call edges, global read/write edges, loops, reductions, I/O, serial control, indirect memory, and blockers. The router propagates blockers along call edges. High goes to rules. Middle generates STC then passes to LLM. Low stays serial and records the reason.

## Verification

```bash
python3 Method/verify.py \
  --source method_data/NPB/NPB_RepoOMP/cg_aaai.c \
  --benchmark-root benchmark/NPB3.0-omp-C \
  --name cg --class W --threads 4 --runs 5 \
  --out res/reports/verify/cg.verify.json
```

Verification has three stages: compile, workload, performance. On candidate failure, returns non-zero and restores source to pre-verification state. The verifier checks NPB output for `VERIFICATION SUCCESSFUL`, parses `Time in seconds`, and keeps the minimum of successfully parsed values.

## Reference matrix

```bash
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite npb --class A --threads 4 --runs 5 \
  --out res/reports/matrix/npb.matrix.json
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite bots --threads 4 \
  --out res/reports/matrix/bots.matrix.json
```

NPB references come from `method_data/NPB/NPB_RepoOMP/*_aaai.c`. BOTS references come from `method_data/BOTS/BOTS_RepoOMP/*_aaai.c`. The matrix temporarily installs each BOTS reference source into the corresponding OpenMP source file, runs `make` in the app directory, then calls the official run script. `--runs` applies to both NPB and BOTS. BOTS re-parses functional verification and timing on each run, then restores the source and rebuilds the original version. Current default small input mapping: alignment `for-omp-tasks/prot.20.aa`, fft `omp-tasks/1048576`, floorplan `omp-tasks/input.5`, health `omp-tasks/test.input`, nqueens `omp-tasks/10`, sort `omp-tasks/1048576`, sparselu `for-omp-tasks/10x10`, strassen `omp-tasks/128`. The report includes `Verification = successful`, program time, and serial time when available. BOTS matrix builds `_aaai.c`, expert, and serial versions in their native directories. Serial official output is `Verification = n/a`. The report keeps that status and timing. `--generated` feeds BOTS expert source through the rule rewriter, then temporarily replaces the real OpenMP source file to build and run. Candidate results are tagged `generated`. `--thread-list 1,4,16` runs the matrix at multiple thread counts.

Registered benchmarks can use the exemplar route:

```bash
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite npb --class W --threads 4 --runs 3 \
  --generated --generator exemplar \
  --out res/reports/matrix/npb.exemplar.matrix.json
```

This route only retrieves the `_aaai.c` with the same name from `method_data`. It does not claim to complete inference for new programs. The audit file records baseline and exemplar hashes. The matrix report must honestly preserve compilation failures, verification failures, missing mappings, and missing performance data. Do not skip failures.

## Offline entry

The offline entry supports conservative rule candidates and real verification. If rule candidate verification fails, returns non-zero, keeps the failure JSON, and does not overwrite NPB source:

```bash
python3 Method/run_method.py \
  --suite bots \
  --transform-source 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --verify-candidate \
  --npb-class W --threads 4 --runs 1 \
  --out-dir res/method_run
```

The current rule engine only accepts simple independent array loops that pass lexical cleaning, bracket balance, real array lvalue, and OpenMP scope checks. Source files with existing OpenMP tasks stay serial to avoid breaking task dependencies. `--generated` feeds NPB `_#_omp.c` input through the rule rewriter, then runs the same matrix verification. The rule engine does not generate persistent parallel regions, reductions, single, task cutoffs, or cross-phase synchronization. So it cannot reproduce most `_aaai.c` region-level structure. NPB Class W auto candidates currently do not reach `_aaai.c` level. Failed items and performance lag must be kept in the matrix report. Do not treat compilation pass as success.

Reference-guided experiments are only for verifying STC target scope and upper bound. They do not represent auto-generated results:

```bash
python3 Method/primitive_addition/reference_guided.py \
  --source 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --reference method_data/NPB/NPB_RepoOMP/cg_aaai.c \
  --function conj_grad \
  --out res/method_run/cg.reference-guided.c \
  --audit res/method_run/cg.reference-guided.json
```

This tool only replaces the specified function and writes the reference source to the audit file. The candidate still goes through `Method/verify.py`.

Entry point for evidence without remote API calls and reference acceptance:

```bash
python3 Method/run_method.py \
  --suite bots --threads 4 --out-dir res/method_run
```

Full NPB and BOTS:

```bash
python3 Method/run_method.py \
  --suite all --npb-class A --threads 4 --runs 3 \
  --out-dir res/method_run
```

The entry generates MAP, routing, and benchmark matrix JSON. If any NPB reference fails compilation or function, the command returns non-zero, but all results are still written to the report.

## Reference comparison

```bash
python3 Method/primitive_addition/compare_references.py \
  --matrix res/reports/matrix/npb.matrix.json \
  --out res/reports/compare/npb.compare.json
```

The comparison report summarizes compilation, function, timing, and computable speedup only. Times from different Class, input, thread count, compiler, or machine cannot be directly claimed to reach `_aaai.c` level. Current measurements: NPB Class A reference 8/8 pass function, BOTS 8/8 pass function on small inputs. The rule engine does not generate cross-loop parallel regions, reductions, single, or task cutoffs. So auto candidates overall still do not reach `_aaai.c` level. The FFmpeg, NCNN, and GROMACS workloads listed in Method.md are not provided with source code, inputs, build wrappers, or oracles in this repo. They are not implemented. Do not fill in passing results.

## Prototype pipeline

The original three-stage API pipeline for CG is still available:

```bash
python3 Method/run_pipeline.py
```

It needs a remote API. It always analyzes `cg_#_omp.c`, generates `cg_opt.c`, builds Class W, uses 4 threads, and compares the candidate against `cg_ori.c`. It is not a full MAP, routing, and STC implementation. It does not auto-cover all NPB and BOTS programs.