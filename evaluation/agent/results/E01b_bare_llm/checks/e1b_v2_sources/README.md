# e1b_v2_sources — E1's programs as agent v2 would have finished them (the inputs of `e1b_v2_verify`)

Each file is rebuilt, no model, from one E1 `default` trial's archived patches: the original plus the
Phase-A rewrite the log KEPT (`tools/marginal_replay.py`'s rule), plus DiscoPoP's Phase-B pragmas that
agent v2 keeps where v1 dropped them. They go through the harness's `verify-source` as run
`e1b_v2_verify` — the same verification every trial gets — so "E1 under v2" is a measured outcome, not
the agent's own timing.

| files | trial | what v2 changes |
|---|---|---|
| `e1_r_a_tsvc_s1213@1`, `@3`, `s121@1`, `@2`, `@5`, `s244@1`, `s112@4` `_final.c` | the 7 trials `e1b_marginal_replay` found recoverable | **D33**: the rewrite with ALL its safe pragmas — v1 dropped each one alone |
| `s281_rep2` … `rep5_both_halves.c` | `s281` reps 2–5 (`e1_r_b`) | **Fix 91**: DiscoPoP's pragma on BOTH halves of the `LEN/2` split — v1's clause stage refused `private(x)` on one half |
| `e1_r_a_tsvc_s127@1_final.c` | control: FASTER in E1 | unchanged — must reproduce E1's verdict |
| `e1_r_a_tsvc_s121@4_final.c` | control: a slow rewrite (0.13× the original in the replay) | unchanged — must NOT come out FASTER |

The `*_final.c` files are copied from `../e1b_marginal_replay/node0/`, where the replay wrote them.
