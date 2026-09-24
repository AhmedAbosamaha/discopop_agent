# t0_4_four_lanes — T0.4 at four lanes of 12 cores (the author's time lever, 23–24 Sep)

Server, 24 Sep 2026 17:06–17:17 UTC, commit `89f8178a`, no model. **Host load at start ≈ 2** (the other
users' jobs were absent), so this measures interference between the campaign's OWN four lanes, not with
other users (T0.4 v2 measured two lanes at load 5,700):

    ../venv/bin/python agent/tools/timing_noise.py --out agent/runs/t0_4_four_lanes \
        --benchmarks tsvc/s211,tsvc/s254,polybench/2mm --repeats 10 --lanes 4 --lane-cores 12 --first-node 0 --threads 12

Resolvable ratio with the harness's median of 5 = 1 + 2·CV/√5:

| benchmark | alone (serial / parallel) | four lanes at once | at 1.1× |
|---|---|---|---|
| `tsvc/s211` | 1.005× / 1.003× | 1.016× / 1.008× | holds |
| `tsvc/s254` | 1.020× / 1.014× | 1.013× / 1.011× | holds |
| `polybench/2mm` | 1.048× / 1.007× | **1.123×** / 1.020× | **does not hold** for the serial run |

**Decision (within the author's condition "used once T0.4 at four lanes shows the timing still resolves
1.1×"):** four lanes for TSVC-based runs (E1-clean, E2, E3, E4, E8); two lanes stay for PolyBench and the
applications (LULESH, NPB-C), whose serial runs are memory-bound — 2mm's varies 13.8 % when four lanes share
each node's memory — until a check on those programs says otherwise. Running unpinned is never acceptable
(`s254` parallel 1.19×, 2mm serial 1.24×).

`run.log`, `runs.csv` (every timed run), `summary.json`.
