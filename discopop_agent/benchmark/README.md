# Agent benchmark

Eight self-contained C++ programs, one per class of parallelization obstacle,
plus a driver that runs the **whole** pipeline on each and reports what the
agent actually achieved.

```bash
# from the repository root
venv/bin/python -m discopop_agent.benchmark.run --list
venv/bin/python -m discopop_agent.benchmark.run                      # all cases
venv/bin/python -m discopop_agent.benchmark.run --cases stencil_war  # one case
venv/bin/python -m discopop_agent.benchmark.run \
    --provider claude-agent-sdk --model haiku --edit-mode direct --verbose
```

Each run writes to `runs/<timestamp>/`:

```
runs/20260816-173000/
├── report.md                 the table + per-case detail (start here)
├── results.json              same data, machine-readable
└── <case>/
    ├── original.cpp          the case as shipped
    ├── <case>.cpp            what the agent left behind
    ├── agent_changes.diff    what it changed
    ├── agent.log             the agent's full output (add --verbose for prompts)
    └── .discopop/            the profile, patches, and accepted.json
```

## The verdict is measured, not reported

The agent judges its own work, so a benchmark that echoed its verdicts would
measure its self-assessment. After the agent finishes, the driver independently
compiles the **original** source sequentially and the **final** source with
`-fopenmp`, runs both on the same input, and compares wall time and stdout
itself. That is the `Speedup` and `Output` in the report.

| Verdict | Meaning |
|---|---|
| `FASTER` | final source is parallel and ≥1.1× faster, output identical |
| `parallel-not-faster` | pragmas present, correct, but no measured gain |
| `changed-not-parallel` | the source was rewritten but nothing parallelized |
| `no-change` | agent accepted nothing and left the source alone |
| `BROKEN` | **output differs from the original** — a gate escape, investigate |
| `ERROR` / `TIMEOUT` | the case never got as far as a verdict |

`BROKEN` should never appear: producing different output is exactly what the
correctness gate exists to prevent. If it does, the gate has a hole.

## The cases

| Case | Cause | What the model has to work out |
|---|---|---|
| `doall_clean` | — | Nothing. Already a Do-All; DiscoPoP alone should handle it and the LLM should never be called. |
| `storage_reuse` | 1 storage | A scalar hoisted out of the loop is reused, not carried. Privatize. |
| `array_accumulator` | 2 reduction | `acc[0] +=` hides a reduction behind an array slot. Make it a scalar. |
| `stencil_war` | 3a in-place, no read-back | Every input is a previous-sweep value → double-buffer. |
| `bubble_sort` | 3b in-place, read-back | Swaps cascade within a sweep → odd-even partition, bounds re-derived. |
| `prefix_sum` | 4 recurrence | Split the independent work out, then scan the accumulator. |
| `early_exit` | 5 control flow | `break` kills the trip count. Hoist the guard, then a canonical loop. |
| `fine_grained` | 6 granularity | The inner loop is a *correct* Do-All that is too small to pay. Coarsen. |

Two design rules keep the cases fair under a byte-identical-output contract:

- **Cross-element accumulation is integer.** Floating-point reduction is not
  associative, so an FP total would change in the last bits under any parallel
  schedule and fail the correctness gate for a *correct* parallelization.
- **Per-element arithmetic is schedule-independent.** Each element's value is
  computed by the same operations in the same order however the loop is
  scheduled, so only the ordering the case is *about* can affect the result.

`fine_grained` is expected to end in a revert with "correct but not faster" —
it exists to exercise that feedback path, not to be solved easily.
`bubble_sort` runs with `--no-require-speedup`: sorting is memory-bound, the
profiled run caps `N`, and the timed run is then too short to resolve a 1.1×
ratio. Its correctness check is unaffected.

## Cost

A profile cycle (instrument → run → explore) is roughly 30 s per case on a
laptop, and the agent re-profiles once per accepted rewrite, so a full
eight-case run with `--budget 3` takes on the order of 30–60 minutes plus LLM
latency. Run a single case while iterating.
