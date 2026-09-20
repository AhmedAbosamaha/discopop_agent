# T0.10 — the expert ceiling of the TSVC restructuring benchmarks

What the EXPERT reference solution of each class-R/A TSVC loop achieves on the experiment
server, so the agent's result on that loop can be reported as a fraction of what is reachable.
No model, no DiscoPoP: `agent/tools/tsvc_ceiling.py` builds the original (`-O2`) and the
reference (`-O2 -fopenmp`) at each dataset size, times both, and checks the reference computes
the original's values.

* 42 rows (21 loops × 2 sizes), **42 correct** — every reference reproduces the original within
  the oracle's tolerance at 6 and 12 threads.
* Best speedups span **0.87× to 4.64×**. These loops do little arithmetic per element, so they
  are memory-bound: two references (`s255`, and `s112`/`s121`, which need a full copy of an
  array) do not reach 1.1× even written by hand. For class R the headline outcome is therefore
  *verified-correct parallelization reached*, with speed reported against this ceiling rather
  than as an absolute claim.
* Measured under a host load of ~1,500–2,000 from other users, pinned to NUMA node 1.

Generated in `~/tsvc_probe` on the server (outside the harness tree, so it could run beside an
experiment) and archived here on 2026-09-20. **To re-measure with the generator-v2 sizes**, which
is still owed: `agent/tools/tsvc_ceiling.py --packages agent/prepared/tsvc --references
agent/reference_solutions/tsvc --out agent/runs/t0_10_tsvc_ceiling --sizes LARGE,EXTRALARGE
--threads 6,12 --pin 1`.
