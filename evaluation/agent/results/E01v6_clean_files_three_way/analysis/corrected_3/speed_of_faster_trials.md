# E1-v6, third corrected read-out: the speed of each setup's faster trials

Descriptive, added 15 Nov 2026 (`speed_of_faster_trials.py`); no trial, count or test changes. Speedup: the harness's measurement, the better of 6 and 12 threads at the verification size, over the sequential original. The 18 class-R loops, 90 trials per setup. "Faster" in the thesis means faster and race-free; the registered read-out's median is over all trials the harness judged FASTER, racy ones included, and is reproduced here.

| setup | FASTER | median | faster and race-free | median | lowest | highest | loops solved |
|---|---|---|---|---|---|---|---|
| the agent (Haiku 4.5) | 75 | 2.58× | 75 | **2.58×** | 1.11× | 5.33× | 16 of 18 |
| Haiku 4.5 alone | 40 | 3.23× | 37 | **3.34×** | 1.39× | 4.55× | 13 of 18 |
| Sonnet 5 alone | 82 | 2.85× | 77 | **3.20×** | 1.27× | 5.68× | 17 of 18 |
| Opus 5.5 alone | 89 | 3.13× | 89 | **3.13×** | 1.13× | 5.50× | 18 of 18 |
| Fable 5.1 alone | 89 | 3.08× | 89 | **3.08×** | 1.14× | 5.45× | 18 of 18 |

Each median covers the setup's own faster trials, so the setups are compared on different loops. On the loops that the agent and a model alone both solved (median speedup of the faster and race-free trials per loop):

| model alone | loops both solved | model alone faster | the agent faster | median ratio, model alone / agent |
|---|---|---|---|---|
| Haiku 4.5 alone | 12 | 10 | 2 | 1.03 |
| Sonnet 5 alone | 15 | 12 | 3 | 1.08 |
| Opus 5.5 alone | 16 | 11 | 5 | 1.17 |
| Fable 5.1 alone | 16 | 13 | 3 | 1.07 |

Per loop, the median speedup of the faster and race-free trials (— : none):

| loop | the agent (Haiku 4.5) | Haiku 4.5 alone | Sonnet 5 alone | Opus 5.5 alone | Fable 5.1 alone |
|---|---|---|---|---|---|
| `s112` | 1.40× | — | 1.46× | 1.14× | 1.42× |
| `s121` | 1.40× | — | 1.40× | 2.70× | 1.46× |
| `s1213` | 2.47× | 2.57× | 2.09× | 2.16× | 2.57× |
| `s127` | 3.74× | 3.89× | 3.93× | 3.06× | 3.94× |
| `s211` | 1.55× | — | 2.34× | 2.12× | 2.19× |
| `s212` | 1.37× | 1.73× | 2.32× | 3.34× | 3.17× |
| `s241` | 1.40× | 2.11× | 1.88× | 1.76× | 1.92× |
| `s243` | 1.21× | 1.39× | 2.39× | 2.54× | 2.44× |
| `s244` | 4.95× | — | 5.36× | 5.39× | 5.42× |
| `s252` | 2.41× | 3.61× | 3.59× | 3.46× | 3.66× |
| `s254` | 3.36× | 3.43× | 3.50× | 3.29× | 3.39× |
| `s255` | 2.49× | 2.55× | 3.28× | 3.65× | 3.35× |
| `s281` | 3.30× | 3.21× | 4.01× | 3.48× | 2.54× |
| `s291` | 3.46× | 3.48× | 3.40× | 3.48× | 3.45× |
| `s292` | 2.93× | 2.93× | 2.91× | 4.14× | 3.88× |
| `s293` | 3.00× | 2.65× | — | 2.34× | 2.88× |
| `s331` | — | 4.43× | 4.56× | 4.54× | 4.48× |
| `s341` | — | — | 1.98× | 2.39× | 2.32× |
