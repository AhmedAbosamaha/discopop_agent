# Thesis material — case studies

Built by `agent/tools/thesis_material.py` from the archived runs; every number is in `facts.json`.

- **2mm_annotated_faster** — polybench/2mm, `full`, claude-haiku-4-5-20251001: **FASTER**, kernel speedup {'6': 5.467, '12': 9.471}, 1 call(s), 137.5 s
- **floyd_restructured_faster** — polybench/floyd-warshall, `full`, claude-haiku-4-5-20251001: **FASTER**, kernel speedup {'6': 1.605, '12': 2.92}, 2 call(s), 233.6 s
- **floyd_stack_array_broken** — polybench/floyd-warshall, `full`, claude-haiku-4-5-20251001: **BROKEN**, kernel speedup {}, 2 call(s), 238.0 s
- **hotspot_correct_but_12x_slower** — rodinia-3.1/hotspot, `full`, claude-haiku-4-5-20251001: **parallel-not-faster**, kernel speedup {'6': 0.08, '12': 0.064}, 1 call(s), 1120.3 s
- **jacobi2d_annotated_faster** — polybench/jacobi-2d-imper, `full`, claude-haiku-4-5-20251001: **FASTER**, kernel speedup {'6': 4.78, '12': 5.848}, 1 call(s), 129.2 s
- **lu_inner_pragma_correct_but_5x_slower** — polybench/lu, `full`, claude-haiku-4-5-20251001: **parallel-not-faster**, kernel speedup {'6': 0.205, '12': 0.161}, 1 call(s), 167.5 s
- **lu_with_speed_check_faster** — polybench/lu, `speed_gate_large`, claude-haiku-4-5-20251001: **FASTER**, kernel speedup {'6': 1.488, '12': 2.385}, 2 call(s), 318.4 s
- **seidel2d_correctly_declined** — polybench/seidel-2d, `full`, claude-haiku-4-5-20251001: **no-change**, kernel speedup {'6': 1.0, '12': 1.001}, 3 call(s), 299.0 s
