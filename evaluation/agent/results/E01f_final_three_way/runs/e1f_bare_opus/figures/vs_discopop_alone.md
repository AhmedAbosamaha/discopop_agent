| Arm | Model | Trials | gained | gained-not-faster | better | equal | worse | lost | neither | unsafe | invalid | not-comparable | no-baseline | median agent / DiscoPoP alone |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bare_llm_v3 | claude-opus-5-5 | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | — |

| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | Agent / DiscoPoP alone | Verdicts |
|---|---|---|---|---|---:|---|
| tsvc_b1/s000 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER · 3.26x | — | 1 no-baseline |
| tsvc_b1/s112 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 1.36x | — | 5 no-baseline |
| tsvc_b1/s121 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 1.38x | — | 5 no-baseline |
| tsvc_b1/s1213 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.52x | — | 5 no-baseline |
| tsvc_b1/s127 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.89x | — | 5 no-baseline |
| tsvc_b1/s211 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.12x | — | 5 no-baseline |
| tsvc_b1/s212 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.99x | — | 5 no-baseline |
| tsvc_b1/s241 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 1.83x | — | 5 no-baseline |
| tsvc_b1/s243 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.05x | — | 5 no-baseline |
| tsvc_b1/s244 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,VERIFY_FAILED · 4.06x | — | 5 no-baseline |
| tsvc_b1/s252 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.60x | — | 5 no-baseline |
| tsvc_b1/s254 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.51x | — | 5 no-baseline |
| tsvc_b1/s255 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.46x | — | 5 no-baseline |
| tsvc_b1/s281 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.02x | — | 5 no-baseline |
| tsvc_b1/s291 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.12x | — | 5 no-baseline |
| tsvc_b1/s292 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 3.07x | — | 5 no-baseline |
| tsvc_b1/s293 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.89x | — | 5 no-baseline |
| tsvc_b1/s3112 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER · 3.34x | — | 3 no-baseline |
| tsvc_b1/s313 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER · 4.63x | — | 1 no-baseline |
| tsvc_b1/s321 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER · 3.66x | — | 3 no-baseline |
| tsvc_b1/s322 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER · 4.27x | — | 3 no-baseline |
| tsvc_b1/s323 | bare_llm_v3 | claude-opus-5-5 | — · — | parallel-not-faster,parallel-not-faster,parallel-not-faster · 0.81x | — | 3 no-baseline |
| tsvc_b1/s331 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 4.83x | — | 5 no-baseline |
| tsvc_b1/s341 | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER,FASTER,FASTER,FASTER,FASTER · 2.37x | — | 5 no-baseline |
| tsvc_b1/vpvtv | bare_llm_v3 | claude-opus-5-5 | — · — | FASTER · 3.83x | — | 1 no-baseline |

Verdicts: **gained** — DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster; **gained-not-faster** — as gained, but the agent's program is not faster (or the kernel is too short to time); **better** — both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's; **equal** — both parallel and correct; within 1.1x of each other (or not timeable); **worse** — correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves; **lost** — DiscoPoP alone reaches a verified parallel program; the agent's trial does not; **neither** — neither reaches a verified parallel program; **unsafe** — the agent's final program computes different values (BROKEN); **invalid** — the agent's trial has no verdict (scaffold modified, verification/agent/profile error); **not-comparable** — both parallel and correct, but timed on another host, size or thread set: no ratio; **no-baseline** — no DiscoPoP-alone trial for this benchmark among the given runs.
A program left unchanged IS the sequential original (1.00x); the sequential original is the reference both columns are measured against, never the comparison itself.
