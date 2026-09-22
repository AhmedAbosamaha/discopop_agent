# Thesis material — case studies

Built by `agent/tools/thesis_material.py` from the archived runs; every number is in `facts.json`. Grouped by what the agent actually DID, because that is the question a reader asks first and a line count does not answer it: a pragma is not a restructuring, and neither is a comment the model wrote to explain itself.

## The agent changed the code

- **2mm_default_vs_dp_alone** — polybench/2mm, `default`: **FASTER**, code +14/−13, 1 pragma(s), kernel speedup {'6': 5.555, '12': 10.621}, 1 call(s), 410.4 s
- **floyd_e1_conditional_write_gained** — polybench/floyd-warshall, `default`: **FASTER**, code +5/−2, 1 pragma(s), kernel speedup {'6': 5.281, '12': 5.933}, 1 call(s), 189.8 s
- **floyd_restructured_faster** — polybench/floyd-warshall, `full`: **FASTER**, code +3/−2, 1 pragma(s), kernel speedup {'6': 1.605, '12': 2.92}, 2 call(s), 233.6 s
- **floyd_restructured_peeling** — polybench/floyd-warshall, `speed_gate_large`: **FASTER**, code +5/−2, 1 pragma(s), kernel speedup {'6': 5.826, '12': 9.556}, 2 call(s), 161.6 s
- **floyd_stack_array_broken** — polybench/floyd-warshall, `full`: **BROKEN**, code +5/−1, 2 pragma(s), kernel speedup {}, 1 call(s), 156.5 s
- **hotspot_correct_but_12x_slower** — rodinia-3.1/hotspot, `full`: **parallel-not-faster**, code +9/−10, 3 pragma(s), kernel speedup {'6': 0.973, '12': 0.948}, 2 call(s), 488.1 s
- **s127_induction_5of5_faster** — tsvc/s127, `default`: **FASTER**, code +2/−6, 1 pragma(s), kernel speedup {'6': 3.804, '12': 3.686}, 1 call(s), 94.9 s
- **s211_distributed_dp_annotates_exposed_loop** — tsvc/s211, `default`: **parallel-not-faster**, code +3/−1, 1 pragma(s), kernel speedup {'6': 1.064, '12': 1.039}, 2 call(s), 387.5 s
- **s254_carry_around_5of5_faster** — tsvc/s254, `default`: **FASTER**, code +4/−4, 1 pragma(s), kernel speedup {'6': 3.354, '12': 3.83}, 1 call(s), 117.1 s
- **s291_peeled_5of5_faster** — tsvc/s291, `default`: **FASTER**, code +1/−4, 1 pragma(s), kernel speedup {'6': 3.304, '12': 3.938}, 1 call(s), 162.5 s
- **trisolv_reduction_extracted** — polybench/trisolv, `full`: **parallel-speed-not-measurable**, code +3/−1, 1 pragma(s), kernel speedup {'6': 0.442, '12': 0.158}, 1 call(s), 88.0 s

## The agent only added pragmas

- **2mm_annotated_faster** — polybench/2mm, `full`: **FASTER**, 2 pragma(s), no code changed, kernel speedup {'6': 4.698, '12': 7.464}, 1 call(s), 137.8 s
- **jacobi2d_annotated_faster** — polybench/jacobi-2d-imper, `full`: **FASTER**, 2 pragma(s), no code changed, kernel speedup {'6': 4.78, '12': 5.848}, 1 call(s), 129.2 s
- **lu_annotated_after_fix84** — polybench/lu, `full`: **FASTER**, 2 pragma(s), no code changed, kernel speedup {'6': 1.586, '12': 2.72}, 1 call(s), 161.7 s
- **lu_inner_pragma_correct_but_5x_slower** — polybench/lu, `full`: **parallel-not-faster**, 2 pragma(s), no code changed, kernel speedup {'6': 0.205, '12': 0.161}, 1 call(s), 167.5 s
- **lu_with_speed_check_faster** — polybench/lu, `speed_gate_large`: **FASTER**, 1 pragma(s), no code changed, kernel speedup {'6': 1.488, '12': 2.385}, 2 call(s), 318.4 s

## The agent changed nothing (declined)

- **s121_memcpy_pragmas_slower** — tsvc/s121, `default`: **no-change**, nothing changed, kernel speedup {'6': 1.022, '12': 1.008}, 1 call(s), 174.5 s
- **s241_copy_per_repetition_settle_dropped** — tsvc/s241, `default`: **no-change**, nothing changed, kernel speedup {'6': 0.996, '12': 0.998}, 1 call(s), 737.9 s
- **s321_recurrence_declined_9_attempts** — tsvc/s321, `default`: **no-change**, nothing changed, kernel speedup {'6': 1.003, '12': 0.998}, 9 call(s), 1216.6 s
- **seidel2d_correctly_declined** — polybench/seidel-2d, `full`: **no-change**, nothing changed, kernel speedup {'6': 0.981, '12': 1.0}, 12 call(s), 1661.2 s

