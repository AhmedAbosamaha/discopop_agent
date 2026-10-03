# E2-O3 — the Haiku agent against every model alone (race-checked; success = race-free verified parallel program covering the hot loop)

| setup | `k23` offset pointer | `k31` offset variable | `k36` accessor macro | all three |
|---|---|---|---|---|
| Haiku agent + evidence | 9/10 (9 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe | 10/10 (10 faster) · 0 unsafe | **29/30** (29 faster) · 0 unsafe |
| Haiku agent, no evidence | 0/10 (0 faster) · 0 unsafe | 0/10 (0 faster) · 0 unsafe | 0/10 (0 faster) · 0 unsafe | **0/30** (0 faster) · 0 unsafe |
| Haiku alone | 0/10 (0 faster) · 10 unsafe | 0/10 (0 faster) · 10 unsafe | 0/10 (0 faster) · 10 unsafe | **0/30** (0 faster) · 30 unsafe |
| Sonnet alone | 0/5 (0 faster) · 5 unsafe | 2/5 (2 faster) · 3 unsafe | 0/5 (0 faster) · 5 unsafe | **2/15** (2 faster) · 13 unsafe |
| Opus alone | 0/5 (0 faster) · 5 unsafe | 5/5 (1 faster) · 0 unsafe | 3/5 (1 faster) · 2 unsafe | **8/15** (2 faster) · 7 unsafe |
| Fable alone | 0/5 (0 faster) · 5 unsafe | 4/5 (4 faster) · 1 unsafe | 2/5 (1 faster) · 3 unsafe | **6/15** (5 faster) · 9 unsafe |
