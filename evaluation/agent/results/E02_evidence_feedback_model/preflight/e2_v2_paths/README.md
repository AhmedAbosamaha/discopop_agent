# e2_v2_paths — agent v2's new Phase B paths, run end to end without a model (E2 pre-flight)

E2 runs on agent v2 (D32, D33, Fixes 91–92). Its smoke (`e2_smoke_a`, `e2_smoke_b`) exercised D33 and
Fix 91 only where the model's draw produced a suitable rewrite (three `s281` trials): on `s121` Haiku
copied the array with `memcpy` (nothing for D33 to combine). So v2's two new Phase B paths were also run
on E1's own rewrites, with no model, through the live agent on the server (23 Sep 2026, commit
`8ac62000`, NUMA node 1):

    numactl --cpunodebind=1 --membind=1 venv/bin/python evaluation/agent/tools/default_arm_ceiling.py \
        s112=.../e1_r_a_tsvc_s112@4_final.c s121=.../e1_r_a_tsvc_s121@1_final.c ... \
        --out evaluation/agent/analysis/e2_v2_paths

Input: the 13 programs of `../../../E01b_bare_llm/checks/e1b_v2_sources/` (E1's kept Phase-A rewrites
with the pragmas v2 keeps), **pragmas stripped** — i.e. exactly the pragma-free rewrite E1's model handed
over. The agent then runs as `discopop_gate` does (`--budget 0`, the campaign's flags, timing at the
kernel's timing size): DiscoPoP profiles the rewrite, Phase B pushes its pragmas through the gate,
Settle verifies. **Settle's reference here is the rewrite itself, not TSVC's original** — the speed
figures below say the path works, they are not speedups over the original (those are `e1b_v2_verify`'s).

| program | result | Phase B path | Settle (vs the rewrite) |
|---|---|---|---|
| `s1213` rep 1 | KEPT, 2 pragmas | **D33**: 0.80×, 0.95× alone → set kept | 4.14× |
| `s121` rep 2 | KEPT, 2 | **D33**: 0.66×, 0.72× alone → set kept | 3.85× |
| `s121` rep 5 | KEPT, 2 | **D33**: 0.76×, 0.78× alone → set kept | 3.50× |
| `s244` rep 1 | KEPT, 3 | **D33**: 0.63×, 0.55×, 0.53× alone → set of three kept | 4.04× |
| `s281` rep 2 | KEPT, 2 | **Fix 91 + D33**: both halves pass the clause stage; 0.73×, 0.53× alone → set kept | 3.05× |
| `s281` rep 3 | KEPT, 2 | Fix 91 + D33: 0.68×, 0.59× | 2.75× |
| `s281` rep 4 | KEPT, 2 | Fix 91 + D33: 0.55×, 0.84× | 2.75× |
| `s281` rep 5 | KEPT, 2 | Fix 91 + D33: 0.65×, 0.58× | 3.10× |
| `s112` rep 4 | KEPT, 2 | old path — both paid alone this time (1.04×, 3.70×) | 3.14× |
| `s1213` rep 3 | KEPT, 2 | old path (1.09×, 4.07×) | 3.89× |
| `s121` rep 1 | KEPT, 2 | old path (1.00×, 4.71×) | 2.64× |
| `s127` rep 1 (control, FASTER in E1) | KEPT, 1 | old path (4.23×) | 3.95× |
| `s121` rep 4 (control, a slow rewrite) | **not kept** | a lone deferred pragma (0.79×) — dropped as measured alone | — |

**Result.** D33's joint judgement ran live in 8 of 13 programs, including a set of three (`s244`); Fix
91's clause stage passed both halves of all four `s281` splits (0 clause rejections); a lone deferred
pragma is dropped as before (the control). In every program one DiscoPoP pattern — its `do_all` on the
repetition loop — was rejected by TSan, the same false positive E1 recorded. Four programs whose
pragmas E1 dropped one at a time now paid alone: single marginals near 1.0 are unstable on the shared
host (T0.4), which is why D33 judges the set.

Files: `console.log`, `ceiling.csv` (one row per program), and per program `agent.log`, the finished
source (`s*.c`) and `.discopop/agent_patches/` (the agent's own change log and every candidate). The
DiscoPoP profile trees (126 MB) stayed on the server.
