# e1b_v2_race_check — the 13 programs of `e1b_v2_verify` through the gate's safety stages

`verify-source` judges output (two inputs) and repeatability at fixed thread counts, not races. So the
programs E1 would have ended with under agent v2 (`../e1b_v2_sources/`, verified in `../e1b_v2_verify/`)
were also put through the agent's own `validate(mode="safety")` — TSan with archer (clang-20,
`/usr/lib/llvm-20/lib/libarcher.so`), the schedule matrix (1/2/4 threads × static / dynamic,1 / guided),
output on the shipped input and on `--check-input 7` — with `tools/race_check.py` on the server, no model
(23 Sep 2026, commit `51c6da78` + registration):

    numactl --cpunodebind=0 --membind=0 venv/bin/python evaluation/agent/tools/race_check.py \
        --runs e1b_v2_verify --arm "*" --out evaluation/agent/analysis/race_check_v2

**Result: 13 of 13 clean** — the 7 D33 programs (each a set of DiscoPoP pragmas that passed the gate one
by one and here passes as a set), the 4 `s281` programs with both halves annotated (Fix 91), and both
controls. With `e1b_v2_verify` this makes "E1 under v2: FASTER in 55 of 90, 0 unsafe" a measured statement:
output-checked by the harness and race-checked by the gate.

`manifest.json` (toolchain, archer), `results.jsonl` (one record per program), `logs/` (console).
