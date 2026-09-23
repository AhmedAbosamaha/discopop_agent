# T0.10 (v2) — the expert ceiling at the sizes the experiments actually use

Re-measurement of `t0_10_tsvc_ceiling/` after the TSVC generator moved to v2 sizes (STANDARD 4M,
LARGE 32M, EXTRALARGE 192M elements, 48 repetitions for the additive loops). The first
measurement was taken on the v1 packages, so its numbers cannot be quoted beside results from
these packages.

**Result: 42 rows (21 loops × 2 sizes), all correct.** At EXTRALARGE the expert references reach
**1.87× to 6.40×, median 4.10×**, at 12 threads under a host load of ~650–1,500.

**What changed, and why it matters.** At the v1 sizes three references did not reach 1.1× even
written by hand — the loops do little arithmetic per element, so at small sizes they are bound by
memory bandwidth and there was no speed to win. At the v2 sizes **every loop clears 1.87×**:
`s331` went 2.35× → 6.40×, `s255` 1.23× → 2.57×, `s281` 2.75× → 4.44×. The consequence for the
thesis is direct: on the restructuring benchmarks we can now report BOTH outcomes — whether a
verified-correct parallelization was reached, and how much of the expert's speedup it captured —
instead of correctness alone. The earlier caveat "for class R the headline is correctness, speed
is secondary because the references themselves are barely faster" no longer applies.

Produced by `agent/tools/tsvc_ceiling.py` on the server, node 1, `clang-20`, no model and no
DiscoPoP involved: it builds the original (`-O2`) and the reference (`-O2 -fopenmp`), times both
and checks the reference reproduces the original's values.
