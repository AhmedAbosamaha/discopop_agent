# What the agent is and how a run proceeds

Verified against the code on 2026-08-30 (commit `4927898c`).

## The pipeline it sits on

DiscoPoP is a three-step tool:

1. `discopop_cxx prog.cpp -o a.out` — an LLVM pass instruments the program and emits
   static analysis artifacts.
2. `./a.out` — the instrumented binary runs and records **observed (dynamic)** memory
   dependences.
3. `discopop_explorer` — reads the profile, identifies computational units and regions,
   and emits parallel patterns as patch files in `patch_generator/`.

The agent consumes `.discopop/` and the profiled source file.

## Two tiers

- **Tier 1 — DiscoPoP already found a pattern here.** A pragma exists; the agent's job is
  only to decide whether it survives the gate. No LLM call.
- **Tier 2 — no pattern.** The loop is not parallel as written. The LLM is given the
  source plus DiscoPoP's evidence and asked to restructure it.

Tier-2 rewrites fall into a **cause taxonomy** — the same taxonomy the benchmark suite is
organised by:

| Cause | Name | Fix the model is expected to find |
|---|---|---|
| 1 | storage / false dependence | privatize the reused scalar |
| 2 | accumulation hidden in an array slot | turn `acc[0] += …` into a scalar reduction |
| 3a | in-place coupling, no same-sweep read-back | double-buffer the sweep |
| 3b | in-place coupling, same-sweep read-back | odd–even partition |
| 4 | true recurrence | split independent work out, scan the rest |
| 5 | non-canonical control flow | hoist the guard, then a canonical loop |
| 6 | granularity | coarsen — the loop is correct but too small to pay |

## Two phases

**Phase A — restructure.** The source is kept **pragma-free** throughout. Regions are
worked highest-impact first; each accepted rewrite is written to the source and (at
`--restructure-depth > 0`) re-profiled, which can expose new regions at `depth + 1`.

*Why phases and not interleaving:* the work queue **grows while Phase A runs**. A pragma
written against a region that is about to be rewritten again is wasted work, and two
pragmas placed independently can interact in ways neither was gated for.

Under `--llm-pragmas` (the default) the model writes its pragma in the same edit as the
restructuring, and the gate judges the pragma on its own merits rather than waiting to see
whether re-profiling makes DiscoPoP find a pattern.

**Phase B — annotate.** Every region the LLM did not annotate is considered once, in one
pass, against the settled source.

**Settle** — the finished file is re-gated as a whole, so interactions between separately
accepted changes are caught.

## Where the evidence comes from after a rewrite

This is the problem C3 exists to solve. Once the LLM rewrites a loop, the profile that
justified the rewrite describes code that no longer exists.

- **Full re-profile** — correct, but runs the instrumented binary again. That run is what
  scales with the workload.
- **Fast refresh** (`--fast-refresh`, default on) — only `discopop_cxx` runs. The previous
  run's observed dependences are translated onto the new instruction numbering by
  **difflib sequence alignment** (`build_id_map`), with `(file, line, column, k)` used as
  an independent cross-check. Anything that cannot be translated with certainty is
  dropped, leaving the rewritten region covered by static (over-approximate) dependences.
- **Reconstruction** (`--llm-recon`, default off) — the model reports the dependences in
  the code it just wrote. **Additive**: it adds dependences a refresh could not carry.
  Claims are made in source terms only (loop line, type, variable, writer/reader lines);
  the agent resolves them to instruction ids itself and drops what it cannot place.

A full re-profile still happens before restructuring at a deeper level and once before
Phase B, so no decision rests on carried-forward data for long.

## Identity facts that matter

- **Instruction ids are deterministic** for identical source — this is what makes
  translation possible at all.
- **Memory-region ids are pointer-derived and NOT comparable across builds.**
- Dependence rows without callpath state carry a **bare instruction id** and are the
  *observed* rows — about 71% of the data. They have zero overlap with
  `static_dependencies.txt`, and that file does not exist after a compile-only build.
- In a dependence line, the `@` number is **callpath state, not a line number**.
