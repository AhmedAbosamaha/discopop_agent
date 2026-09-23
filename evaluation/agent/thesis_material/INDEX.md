# Thesis material — case studies

Built by `agent/tools/thesis_material.py` from the archived runs; every number is in `facts.json`. Grouped by what the agent actually DID, because that is the question a reader asks first and a line count does not answer it: a pragma is not a restructuring, and neither is a comment the model wrote to explain itself.

Every line leads with the verdict against **DiscoPoP alone** — the campaign's main comparison, computed as the statistics compute it — then the program speedups over the sequential original (DiscoPoP alone → agent). Where the shipped program is the original, the exhibit shows what the agent did instead, and says so.

## The agent changed the code

- **2mm_default_vs_dp_alone** — polybench/2mm, `default` (e1_smoke5, rep 1) · vs DiscoPoP alone: **better** (9.49× → 10.62×) · FASTER, code +14/−13, 1 pragma(s) · 1 call(s), 410.4 s
- **floyd_e1_conditional_write_gained** — polybench/floyd-warshall, `default` (e1_r_b, rep 1) · vs DiscoPoP alone: **gained** (1.00× → 5.93×) · FASTER, code +5/−2, 1 pragma(s) · 1 call(s), 189.8 s
- **floyd_restructured_faster** — polybench/floyd-warshall, `full` (pilot4, rep 1) · no DiscoPoP-alone trial to pair with · FASTER, code +3/−2, 1 pragma(s) · 2 call(s), 233.6 s
- **floyd_restructured_peeling** — polybench/floyd-warshall, `speed_gate_large` (e10, rep 1) · vs DiscoPoP alone: **gained** (1.00× → 9.56×) · FASTER, code +5/−2, 1 pragma(s) · 2 call(s), 161.6 s
- **floyd_stack_array_broken** — polybench/floyd-warshall, `full` (e10, rep 1) · vs DiscoPoP alone: **unsafe** (1.00× → 1.00×) · BROKEN, code +5/−1, 2 pragma(s) · 1 call(s), 156.5 s
- **hotspot_correct_but_12x_slower** — rodinia-3.1/hotspot, `full` (e10, rep 1) · vs DiscoPoP alone: **gained-not-faster** (1.00× → 0.97×) · parallel-not-faster, code +9/−10, 3 pragma(s) · 2 call(s), 488.1 s
- **s127_induction_5of5_faster** — tsvc/s127, `default` (e1_r_a, rep 1) · vs DiscoPoP alone: **gained** (1.00× → 3.80×) · FASTER, code +2/−6, 1 pragma(s) · 1 call(s), 94.9 s
- **s211_distributed_dp_annotates_exposed_loop** — tsvc/s211, `default` (e1_smoke5, rep 1) · vs DiscoPoP alone: **gained-not-faster** (1.00× → 1.06×) · parallel-not-faster, code +3/−1, 1 pragma(s) · 2 call(s), 387.5 s
- **s254_carry_around_5of5_faster** — tsvc/s254, `default` (e1_r_b, rep 1) · vs DiscoPoP alone: **gained** (1.00× → 3.83×) · FASTER, code +4/−4, 1 pragma(s) · 1 call(s), 117.1 s
- **s291_peeled_5of5_faster** — tsvc/s291, `default` (e1_r_b, rep 1) · vs DiscoPoP alone: **gained** (1.00× → 3.94×) · FASTER, code +1/−4, 1 pragma(s) · 1 call(s), 162.5 s
- **s313_local_accumulator_better** — tsvc/s313, `default` (e1_a, rep 1) · vs DiscoPoP alone: **better** (5.55× → 6.36×) · FASTER, code +4/−3, 1 pragma(s) · 1 call(s), 166.6 s
- **trisolv_reduction_extracted** — polybench/trisolv, `full` (pilot4, rep 1) · no DiscoPoP-alone trial to pair with · parallel-speed-not-measurable, code +3/−1, 1 pragma(s) · 1 call(s), 88.0 s
- **vpvtv_rewrite_halves_dp_speedup_worse** — tsvc/vpvtv, `default` (e1_a, rep 1) · vs DiscoPoP alone: **worse** (4.08× → 2.37×) · FASTER, code +11/−1, 1 pragma(s) · 1 call(s), 278.9 s

## The agent only added pragmas

- **2mm_annotated_faster** — polybench/2mm, `full` (e10, rep 1) · vs DiscoPoP alone: **not-comparable** (10.31× → 7.46×) · FASTER, 2 pragma(s), no code changed · 1 call(s), 137.8 s
- **jacobi2d_annotated_faster** — polybench/jacobi-2d-imper, `full` (pilot4, rep 1) · no DiscoPoP-alone trial to pair with · FASTER, 2 pragma(s), no code changed · 1 call(s), 129.2 s
- **lu_annotated_after_fix84** — polybench/lu, `full` (e10_lu_fix84, rep 1) · vs DiscoPoP alone: **better** (0.21× → 2.72×) · FASTER, 2 pragma(s), no code changed · 1 call(s), 161.7 s
- **lu_inner_pragma_correct_but_5x_slower** — polybench/lu, `full` (e10, rep 1) · no DiscoPoP-alone trial to pair with · parallel-not-faster, 2 pragma(s), no code changed · 1 call(s), 167.5 s
- **lu_with_speed_check_faster** — polybench/lu, `speed_gate_large` (e10, rep 1) · no DiscoPoP-alone trial to pair with · FASTER, 1 pragma(s), no code changed · 2 call(s), 318.4 s

## The agent changed nothing (declined)

- **s000_agent_below_dp_alone_lost** — tsvc/s000, `default` (e1_a, rep 1) · vs DiscoPoP alone: **lost** (4.03× → 1.00×) · no-change, nothing changed · shows: the program the agent built, then dropped (never shipped) · 1 call(s), 927.5 s
- **s121_memcpy_pragmas_slower** — tsvc/s121, `default` (e1_r_a, rep 1) · vs DiscoPoP alone: **neither** (1.00× → 1.00×) · no-change, nothing changed · shows: the program the agent built, then dropped (never shipped) · 1 call(s), 174.5 s
- **s241_copy_per_repetition_settle_dropped** — tsvc/s241, `default` (e1_r_a, rep 2) · vs DiscoPoP alone: **neither** (1.00× → 1.00×) · no-change, nothing changed · shows: the program the agent built, then dropped (never shipped) · 1 call(s), 737.9 s
- **s321_recurrence_declined_9_attempts** — tsvc/s321, `default` (e1_smoke5, rep 1) · vs DiscoPoP alone: **neither** (1.00× → 1.00×) · no-change, nothing changed · shows: a rewrite the gate rejected at 'correctness' · 9 call(s), 1216.6 s
- **s322_recurrence_declined_rewrites_caught** — tsvc/s322, `default` (e1_d, rep 1) · vs DiscoPoP alone: **neither** (1.00× → 1.00×) · no-change, nothing changed · shows: the program the agent built, then dropped (never shipped) · 9 call(s), 1446.5 s
- **seidel2d_correctly_declined** — polybench/seidel-2d, `full` (e10, rep 1) · vs DiscoPoP alone: **neither** (1.00× → 1.00×) · no-change, nothing changed · shows: a rewrite the gate rejected at 'correctness' · 12 call(s), 1661.2 s

