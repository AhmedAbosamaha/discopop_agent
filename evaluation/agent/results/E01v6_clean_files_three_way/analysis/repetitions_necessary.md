# Are the repetitions necessary? — a no-model test of every loop of E1-v6 and E2-v6 (5 Oct 2026)

For each package of `tsvc_c2`, two variants of the benchmark's file were built beside the original (Mac, SMALL, full
dump on the shipped and on the perturbed input):

* **skip** — the loop's statements run only in the LAST repetition; `dummy` is still called in every one;
* **reorder** — all repetitions of the loop run first, then all the `dummy` calls.

A variant whose output is byte for byte the original's passes the harness's output check: for that loop the
measurement does not force every repetition (skip), or their order relative to `dummy` (reorder).

| loop | skip | reorder |
|---|---|---|
| `s000` (A) | **same output** | differs |
| `s313` (A) | **same output** | differs |
| `vpvtv` (A) | differs | differs |
| `s127`, `s252`, `s254`, `s255`, `s291`, `s292`, `s293`, `s341` (R) | **same output** | differs |
| `s331` (R) | **same output** | **same output** |
| `s112`, `s121`, `s1213`, `s211`, `s212`, `s241`, `s243`, `s244`, `s281` (R) | differs | differs |
| `s161` (hidden order) | **same output** | differs |
| `k19`, `k23`, `k27`, `k31`, `k48`, `k53` | differs | differs |

**Why.** `dummy` changes a few input elements between two repetitions, which makes the repetitions DIFFERENT. It makes
them NECESSARY only where a repetition's result depends on what earlier repetitions left in the arrays. A loop that
recomputes its whole result from arrays it does not write leaves, after its last repetition, exactly what it would have
left had the earlier ones never run. `s331` in addition finds the same index (27371 at SMALL) in every repetition on both
inputs: nothing distinguishes one repetition's result from another's.

**Since when.** The input change is the first packages' (`pb_mix`); the property is the same in packaging v3, v4 and v6.
Packaging v5 was not exposed (the repetition loop was not in the model's file).

**What E1-v6's programs did** (`repetition_loop.md`; every exception read): of the 450 programs of the main comparison
none skips repetitions; one reorders them (`s331` rep 1, the agent). Of the control programs one skips them (`s313`,
the agent, 164×).

Tool: the variants are built by the script recorded in THESIS_EXPERIMENTS §6 (5 Oct); sources under the session's
scratch folder are not archived — the test is re-run by the package generator once the fix is built.
