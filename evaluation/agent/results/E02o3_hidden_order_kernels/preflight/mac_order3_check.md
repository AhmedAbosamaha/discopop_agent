# E2-O3 — the no-model check of the three ORDER-3 kernels (Mac, 3 Oct 2026, before any trial)

Packages `tsvc_b1/k23`, `k31`, `k36` from `tools/prepare_tsvc.py` (ORDER-3, layout v4; `--validate` OK), `k19`
(ORDER-2b X) as the reference. Commit `67ff59a0` (branch `order3`).

## 1. The split order, by running it

Each kernel's inner loop was replaced by the two possible splits (no pragmas) and compiled with `clang -O2`
against its harness header; the output (digest and dump, default input and perturbed input `7`) compared
with the original's:

| kernel | S2's loop first (the order DiscoPoP's flow imposes) | textual order (S1's loop first) |
|---|---|---|
| `k23` offset pointer | identical | differs |
| `k31` offset variable | identical | differs |
| `k36` accessor macro | identical | differs |
| `k19` (reference) | identical | differs |

## 2. DiscoPoP on the packages (`cli.profile_once`, one draw each)

No Do-All, no reduction, no task in any of the four (explorer attempt 1).

## 3. Prompt version 3's order statement (`llm/render.order_statement`, the hot loop's region, lines 18–21)

- `k23`: "Line 19 (`u[i] += w[i] * c[i];`) reads an element of `w` that line 20 (`v[i] = x[i] * d[i] + c[i];`)
  writes; DiscoPoP names the loop at line 18 as carrying this dependence. The value must flow from line 20 to
  line 19: if you split that loop, the loop holding line 20 has to run completely before the loop holding
  line 19; reading `w`'s values from before the loop would change the result." — DiscoPoP names the read by
  its own name (`w`), so the statement both orders the split and reveals the alias.
- `k31`: the same statement with `v` (`u[i] += v[i + off] * c[i];` / `v[i] = u[i + far] * d[i] + c[i];`).
- `k36`: the same statement with `v` (`u[i] += AT1(v, i) * c[i];` / `v[i] = AT2(u, i) * d[i] + c[i];`).
- `k19` (reference): the same statement with `v`, as in E2-V3.

Every statement is right (line 20's loop first). All three kernels enter E2-O3 (record §6, 3 Oct).
