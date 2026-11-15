# E4 step 4 — where the time of the whole trials goes

Descriptive, added 15 Nov 2026 (`e4live_time_split.py`); no trial, count or test changes. The trials are those of the registered read-out (`e4live_readout.md`), whose trial counts, agent seconds and cost this script reproduces before it writes anything. *In model calls*: the seconds the agent waited for the model, each trial's `llm_usage.model_seconds`, equal to the summed `duration_ms` of its usage log. *Model calls*: the rows of the usage log; with the fast refresh they include the reports, one after each fast refresh, which `llm_calls` (the rewrite calls) does not count.

| set | setup | trials | race-free FASTER | agent time, s | in model calls, s | share | everything else, s | model calls | rewrite calls | reports | s per call | cost $ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| The 18 loops | full re-profile (`default_v5`, E3/E3b) | 90 | 75 | 37,680 | 23,524 | 62 % | 14,156 | 321 | 320 | 0 | 73.3 | 52.08 |
| The 18 loops | fast refresh + report (`fast_recon_v5`) | 90 | 78 | 55,018 | 41,359 | 75 % | 13,659 | 535 | 312 | 220 | 77.3 | 61.89 |
| The contrast set and its control (`s311`) | full re-profile (`default_v5`, E3/E3b) | 35 | 30 | 16,450 | 12,284 | 75 % | 4,166 | 155 | 154 | 0 | 79.3 | 25.94 |
| The contrast set and its control (`s311`) | fast refresh + report (`fast_recon_v5`) | 35 | 30 | 31,300 | 26,848 | 86 % | 4,452 | 337 | 185 | 146 | 79.7 | 41.22 |
| **both sets** | full re-profile (`default_v5`, E3/E3b) | 125 | 105 | 54,130 | 35,808 | 66 % | 18,322 | 476 | 474 | 0 | 75.2 | 78.02 |
| **both sets** | fast refresh + report (`fast_recon_v5`) | 125 | 108 | 86,318 | 68,207 | 79 % | 18,111 | 872 | 497 | 366 | 78.2 | 103.11 |

Over both sets the agent's time rose from 15.0 to 24.0 hours (+32,189 s). The time in model calls rose from 9.9 to 18.9 hours (+32,399 s); everything else (building, the refresh or re-profile, the gate's checks, timing) went from 5.09 to 5.03 hours (-210 s). The usage log holds 872 calls against 476: 366 of the difference are reports. A call took 75.2 s on average with the full re-profile and 78.2 s with the fast refresh, so the added time is added calls, not slower ones.

What skipping the instrumented run saved, as the registered read-out estimates it (step 1's medians per refresh, 1.75 s against 1.54 s): 366 fast refreshes × 0.21 s = 76.9 s. The difference in "everything else" above is not this saving: it also holds the directive checks and the timing, which differ from trial to trial.

The two setups were not run side by side: the full re-profile's trials are E3's and E3b's and finished between 2026-10-09 and 2026-10-10, the fast refresh's between 2026-10-18 and 2026-10-19; both on one machine.
