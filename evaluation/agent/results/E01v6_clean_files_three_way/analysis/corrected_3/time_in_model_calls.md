# E1-v6, third corrected read-out: the agent's time in model calls

Descriptive, added 15 Nov 2026 (`time_in_model_calls.py`, from `trials.csv` of this folder); no trial, count or test changes. The agent's 105 trials (`default_v4`: the 18 class-R loops × 5 and the controls).

| | |
|---|---:|
| the agent's seconds, all trials | 52,527 |
| of them in model calls | 38,484 |
| **share of the agent's time in model calls** | **73.3 %** |
| the share within a trial, median | 53 % |
| lower and upper quartile | 40 % – 75 % |
| smallest and largest | 26 % – 99 % |
| trials with more than half of their time in model calls | 59 of 105 |
| profiles (the first of each trial and 260 re-profiles) | 365 |
| seconds of profiling, each profile at its trial's first profile's seconds | 635 |
| **share of the agent's time in profiling** | **1.2 %** |
| median model calls per trial | 2 |
| median agent minutes per trial | 5.4 |
| mean model cost per trial | $0.78 |

The share of all seconds is larger than the median share within a trial because long trials are long through their model calls: a trial that uses all its attempts waits for the model almost all of its time.

Profiling is a small part of the rest. A trial times its first profile only; a re-profile after a kept rewrite is counted at the same seconds, the rewritten program being of the same size. The instrumented runs that a fast refresh would skip are a part of that again: 0.08 % of the agent's time on the 90 trials of the 18 loops (the record's row of 9 Oct 2026, from the second corrected read-out).
