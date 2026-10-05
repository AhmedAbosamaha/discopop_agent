| benchmark | draw | dir | hot loop | Do-All on it | blocker (first found) | names a hot variable | condition 4 |
|---|---|---|---:|---|---|---|---|
| `rodinia_b1/bfs` | t0_11_b1_a | a | 13 | yes | — | no | FAILS |
| `rodinia_b1/bfs` | t0_11_b1_b | a | 13 | yes | — | no | FAILS |
| `rodinia_b1/bfs` | t0_11_b1_c | a | 13 | yes | — | no | FAILS |
| `tsvc_b1/s131` | t0_11_b1_a | a | 20 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s131` | t0_11_b1_b | a | 20 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s131` | t0_11_b1_c | a | 20 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s151` | t0_11_b1_a | a | 18 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s151` | t0_11_b1_b | a | 18 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s151` | t0_11_b1_c | a | 18 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s152` | t0_11_b1_a | b | 24 | yes | — | no | holds |
| `tsvc_b1/s152` | t0_11_b1_b | b | 24 | yes | — | no | holds |
| `tsvc_b1/s152` | t0_11_b1_c | b | 24 | yes | — | no | holds |
| `tsvc_b1/s161` | t0_11_b1_a | a | 19 | no | RAW `c` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s161` | t0_11_b1_b | a | 19 | no | RAW `c` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s161` | t0_11_b1_c | a | 19 | no | RAW `c` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s171` | t0_11_b1_a | b | 19 | yes | — | no | holds |
| `tsvc_b1/s171` | t0_11_b1_b | b | 19 | yes | — | no | holds |
| `tsvc_b1/s171` | t0_11_b1_c | b | 19 | yes | — | no | holds |
| `tsvc_b1/s277` | t0_11_b1_a | b | 19 | yes | — | no | holds |
| `tsvc_b1/s277` | t0_11_b1_b | b | 19 | yes | — | no | holds |
| `tsvc_b1/s277` | t0_11_b1_c | b | 19 | yes | — | no | holds |
| `tsvc_b1/s424` | t0_11_b1_a | a | 21 | no | RAW `flat_2d_array` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s424` | t0_11_b1_b | a | 21 | no | RAW `flat_2d_array` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s424` | t0_11_b1_c | a | 21 | no | RAW `flat_2d_array` (DYNAMIC_ANALYSIS) | yes | holds |
| `tsvc_b1/s481` | t0_11_b1_a | b | 19 | yes | — | no | holds |
| `tsvc_b1/s481` | t0_11_b1_b | b | 19 | yes | — | no | holds |
| `tsvc_b1/s481` | t0_11_b1_c | b | 19 | yes | — | no | holds |
| `tsvc_b1/s482` | t0_11_b1_a | b | 19 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | FAILS |
| `tsvc_b1/s482` | t0_11_b1_b | b | 19 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | FAILS |
| `tsvc_b1/s482` | t0_11_b1_c | b | 19 | no | RAW `a` (DYNAMIC_ANALYSIS) | yes | FAILS |
| `tsvc_b1/vas` | t0_11_b1_a | b | 20 | yes | — | no | holds |
| `tsvc_b1/vas` | t0_11_b1_b | b | 20 | yes | — | no | holds |
| `tsvc_b1/vas` | t0_11_b1_c | b | 20 | yes | — | no | holds |

| benchmark | draws | condition 4 holds |
|---|---:|---:|
| `rodinia_b1/bfs` | 3 | 0 of 3 |
| `tsvc_b1/s131` | 3 | 3 of 3 |
| `tsvc_b1/s151` | 3 | 3 of 3 |
| `tsvc_b1/s152` | 3 | 3 of 3 |
| `tsvc_b1/s161` | 3 | 3 of 3 |
| `tsvc_b1/s171` | 3 | 3 of 3 |
| `tsvc_b1/s277` | 3 | 3 of 3 |
| `tsvc_b1/s424` | 3 | 3 of 3 |
| `tsvc_b1/s481` | 3 | 3 of 3 |
| `tsvc_b1/s482` | 3 | 0 of 3 |
| `tsvc_b1/vas` | 3 | 3 of 3 |
