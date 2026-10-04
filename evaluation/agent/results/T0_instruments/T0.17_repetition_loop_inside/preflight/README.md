# T0.17 pre-flight — the repetition loop inside the benchmark's function (packaging v6), 4 Oct 2026, no model

**Why.** The author stopped E1-v5: the clean layout (packaging v5) must not make speedups worse — "the best
achievable speedup is lower is a problem and the tmp array is also a problem" (record §6, 4 Oct).

**What v5 did.** It made the benchmark's function ONE repetition and let `main.c` call it 48 times. A
temporary array that a solution obtains inside the function is then obtained, and its pages faulted in, on
every call.

**The form tested (v6, suite `tsvc_c2`).** v5 with the repetition loop inside the function, where TSVC's own
function has it (`benchmarks/TSVC_2/src/tsvc.c`):

| file | whose | what it holds |
|---|---|---|
| `<name>.c` | the benchmark | `#include "data.h"` and the function: `for (int nl = 0; nl < iterations; nl++) {` TSVC's loop `dummy(a, b, c, d, e); }` — no comment, no name of ours; the one file a model's changes are taken from |
| `data.h` | ours | v5's declarations, `#define iterations N`, the prototype of `dummy` |
| `main.c` | ours | `dummy` (changes a few input values between two repetitions, as `pb_mix` did) and `main`: set-up, timer, ONE call of the function |
| `_harness/tsvc_c2/<name>.h` | ours, outside the package | data, initial values, perturbed input, digest, timing — as v5 |

**Variants timed** (`tools/v6_proto.py` builds them as source trees, `tools/speed_probe.py` times them: the
harness's own build line `clang-20 -O2 -D<SIZE>_DATASET`, the reference with `-fopenmp`, 6 and 12 threads, 5
repetitions, the variants interleaved, one 12-core lane per job, the loop's verification size):

| name | what |
|---|---|
| `v4` | E1-final's one-file packaging: the repetition loop inside the function, data `static` in the same unit |
| `c1` | packaging v5 as launched; the reference keeps its temporary array in a `static` pointer |
| `c1call` | v5, the reference written the ordinary way: `malloc` at the top of the function, `free` at its end |
| `c2` | packaging v6; the reference obtains its temporary array once, in front of the repetition loop |
| `c2arr` | v6 with the data declared as arrays, as TSVC declares them (prototype only, `-mcmodel=medium`) |
| `+lto` | the same sources built with `-flto` |

## Results

1. **The program is the same.** Output (full dump on the shipped and the perturbed input, digest) byte for
   byte the clean layout's — itself v4's — for 44 of 44 loops; every reference equal to its original
   (`outputs_mac.txt`; the generator's own `--validate` on the Mac and on the server: 44 of 44, package digests
   equal on both machines).
2. **The best the reference reaches is the SAME in all three packagings when they are measured alike**
   (`speed/tableA_median.txt`, `speed/tableA_min.txt`; 28 loops with a reference, 27 in v4). Median over the
   loops of the reference's speedup, best of 6 and 12 threads: v4 3.27×, v5 3.19×, v6 3.32× (median of the 5
   repetitions) — 3.47×, 3.50×, 3.54× taking the fastest repetition. Reference time v5 / v4, per loop: median
   1.00 (0.93–1.08). The earlier statement "the ceiling is lower in the clean layout (median 2.98× against
   4.10×)" compared two SETTINGS: T0.10 left the 12 threads the whole node (24 cores), `t0_14_c1_refs` ran on a
   12-core lane. With the threads free on the node both packagings give T0.10's numbers again
   (`speed/tableD_node_min.txt`: `s000` 4.46× and 4.41×, `s112` 1.91× and 1.92×).
3. **The temporary array is the real cost of v5, and v6 removes it.** The five references that need one,
   speedup (median of 5):

   | loop | v4 | v5, array kept in a `static` | v5, array obtained in the function | v6 |
   |---|---:|---:|---:|---:|
   | `s112` | 1.41 | 1.40 | **0.39** | 1.36 |
   | `s121` | 1.53 | 1.51 | **0.39** | 1.44 |
   | `s211` | 2.24 | 2.18 | **0.80** | 2.17 |
   | `s241` | 2.27 | 2.20 | **0.82** | 2.01 |
   | `s243` | 2.39 | 2.85 | **1.09** | 2.60 |

   In v6 the reference pays for its array once, inside the timed function (0.03–0.09 s: obtaining and
   releasing 256 MB to 1.5 GB) — as every model-written program of E1-final did.
4. **What stays different from the one-file packaging — in v5 and v6 alike:** the function is compiled without
   seeing where the data comes from, so the compiler cannot tell the arrays apart. The SEQUENTIAL original is
   18–33 % slower on four loops (`s243`, `s244`, `s292`, `s482`; `s212` 4 %), within 3 % on the other 37 of
   the 42 loops both packagings have (`speed/tableA_min.txt`, `speed/tableB_min.txt`); those loops' speedups
   come out higher, none lower.
   `-flto` does not restore it on the server (`speed/tableC_min.txt`); arrays instead of pointers change the
   sequential times in both directions (`c2arr`: 0.94–1.12 of v4's) and need `-mcmodel=medium` at the largest
   size — not adopted.
5. **DiscoPoP's view is v4's** (`mac_screen/screen.md`, one profile per layout, Mac): 40 of 42 loops the same
   on every criterion — candidates with tier and pattern, the Do-All set, the blocker of the loop under study,
   the repetition loop blocked, the order statement. `s244` and `s482` differ in WHICH blocker the detector
   names for the loop (T0.16: that changes with the draw in every layout). Two draws on the server:
   `../checks/t0_17_server_a`, `../checks/t0_17_server_b`.
6. **The order statement under prompt version 4 is right on all 42 profiles, the repetition loop's own request
   included** (`order_replay_mac.md`, `order_replay.py --repetition-loop`; version 3 wrong on 3) — in v6 the
   repetition loop is the agent's first region again, as in E1-final.
7. **Sizes measured on the new packages** (`t0_1_c2_sizes`, merged into `config/kernel_sizes.json`): 42 of 44
   as packaging v5's; the timing size of `k19` and `s161` is STANDARD (v5: LARGE).

**A measurement condition found on the way.** Two processes of another user, each using one core fully, move
freely over the server's 48 cores (since about 12 Sep). When one sits on a core of the lane, a 12-thread run of
a loop bound by arithmetic takes up to twice as long (`s255`, `s292`: 1.15 s or 2.1 s in the same
configuration, `speed/passA_lane00.json`). It hits every packaging and every arm alike; the harness's median
of 5 and its best of two thread counts bound it. The tables give the fastest and the median repetition.

**Owed before a model reads the packages:** the author's decision; then the classes in three draws
(`t0_11_c2_a`–`c`), the references through the harness (`t0_14_c2_refs`), prompt fixtures of the new packages,
a smoke run.
