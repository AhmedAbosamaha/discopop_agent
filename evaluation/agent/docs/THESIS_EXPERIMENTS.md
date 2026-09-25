# Agent experiments — thesis documentation

This file is the single record of how the thesis experiments are built and run: every
design decision with its reason, every change to either repository, and every run. It
lives in `evaluation/` of the agent repository (`discopop_agent`, branch `agentic_DiscoPop`) since
2026-09-20; until then it was the `agent-experiments` branch of `new_benchmark_harness` (§6, D20).

## How to read this record

This file is the chronological record, not the place to read a result. **For an experiment's result, read its report:** `agent/results/<EXPERIMENT>/REPORT.md` (map: `agent/results/README.md`) — each report copies this record's own entries for its runs, so the two never disagree. Come here for the reasons behind a decision (§5), for what changed when (§6, one row per change, newest first) and for the full account of a run (§7, newest first).

**Sections:** [1. Why benchmarks need a preparation step](#1-why-benchmarks-need-a-preparation-step) · [2. PolyBench/C 3.2 packaging](#2-polybenchc-32-packaging) · [3. The runner (`agent/benchmark`)](#3-the-runner-agentbenchmark) · [4. Credentials on the server](#4-credentials-on-the-server) · [5. Server state found before the campaign](#5-server-state-found-before-the-campaign) · [6. Change log](#6-change-log) · [6a. Experiment plan](#6a-experiment-plan) · [7. Run log](#7-run-log)

**§5, the decisions and studies, in letter order** (they were written as they came, so the file order differs): [5a.](#5a-server-setup-performed--2026-09-15) Server setup performed — 2026-09-15 · [5b.](#5b-finding--discopops-do-all-verdict-varies-between-profiles-of-the-same-program-2026-09-15) Finding — DiscoPoP's Do-All verdict varies between profiles of the same program (2026-09-15) · [5c.](#5c-how-the-agent-orders-regions--time-saved-is-in-effect-time-consumed-2026-09-16) How the agent orders regions — "time saved" is, in effect, "time consumed" (2026-09-16) · [5d.](#5d-decisions-of-2026-09-16-on-which-regions-reach-the-model-and-how-often) Decisions of 2026-09-16 on which regions reach the model, and how often · [5e.](#5e-instruments--every-study-that-is-not-an-experiment-its-tool-and-how-it-measures) Instruments — every study that is not an experiment, its tool, and how it measures · [5f.](#5f-proposed-a-small-open-model-qwen3-coder-30b-as-a-third-model-2026-09-17) Proposed: a small open model (Qwen3-Coder-30B) as a third model (2026-09-17) · [5g.](#5g-full-review-of-the-agent-2026-09-1718--what-was-wrong-what-changed-what-it-means-for-the-plan) Full review of the agent, 2026-09-17/18 — what was wrong, what changed, what it means for the plan · [5h.](#5h-the-fast-refresh--what-it-does-how-it-is-checked-what-it-cannot-do-2026-09-18) The fast refresh — what it does, how it is checked, what it cannot do (2026-09-18) · [5i.](#5i-review-of-the-experiment-plan-before-the-first-run-2026-09-18) Review of the experiment plan before the first run (2026-09-18) · [5j.](#5j-two-guarantees-for-the-campaign-nothing-is-corrupted-between-trials-and-nothing-measured-is-lost-2026-09-18) Two guarantees for the campaign: nothing is corrupted between trials, and nothing measured is lost (2026-09-18) · [5k.](#5k-benchmark-suitability-audit--the-benchmarks-could-not-test-the-central-claim-2026-09-19) Benchmark suitability audit — the benchmarks could not test the central claim (2026-09-19) · [5l.](#5l-audit-of-the-agents-defaults--a-default-is-a-decision-not-a-neutral-act-2026-09-20) Audit of the agent's DEFAULTS — a default is a decision, not a neutral act (2026-09-20) · [5m.](#5m-the-studies-that-were-decisions-not-protocols--now-specified-2026-09-20) The studies that were decisions, not protocols — now specified (2026-09-20) · [5n.](#5n-every-argument-of-every-arm-is-declared-and-verified-against-the-agents-own-parser-2026-09-20) Every argument of every arm is DECLARED and verified against the agent's own parser (2026-09-20) · [5o.](#5o-the-server-moved-to-the-one-repository-layout-2026-09-20) The server moved to the one-repository layout (2026-09-20) · [5p.](#5p-what-the-agent-has-actually-done-so-far-restructurings-vs-pragmas-2026-09-20) What the agent has actually DONE so far: restructurings vs pragmas (2026-09-20) · [5q.](#5q-arguments-that-depend-on-each-other-2026-09-21) Arguments that depend on each other (2026-09-21) · [5r.](#5r-the-campaigns-scope-is-narrowed-to-three-suites-that-can-show-the-contribution-2026-09-21-d30) The campaign's scope is narrowed to three suites that can show the contribution (2026-09-21, D30) · [5s.](#5s-every-instrument-and-every-experiment-re-examined-after-d29-d30-and-fixes-8688-2026-09-21) Every instrument and every experiment re-examined after D29, D30 and Fixes 86–88 (2026-09-21)

---
Rules this campaign follows (set by the author, 2026-09-14):

- The harness was written to compare DiscoPoP **versions**. This branch adapts it to
  compare **agent configurations** instead.
- Benchmarks are chosen for usefulness and difficulty, and every experiment must finish in
  hours, not days.
- At least one experiment compares a stronger model (Sonnet) against the default (haiku),
  to measure how model quality interacts with the dependence evidence.
- Results are stored permanently, with graphs, for later use in the thesis.
- **The DiscoPoP under test is the `new_explorer` branch, not `master`** — merge base `6a2ef0fa`
  (25 June 2026), plus this project's own 100 commits, plus Fixes 80–84. The thesis cites that,
  because `master` is a different and older code base (April 2026) and none of these numbers
  applies to it. `new_explorer` has advanced by 178 commits since the base, 19 of them in
  `TaskGraph.py`; the campaign deliberately does NOT follow them, because every measurement —
  E10, T0.11, E1 — is against one fixed DiscoPoP and would stop being comparable if it moved.
  Re-basing onto current `new_explorer` is a post-campaign task, and it is also when the upstream
  bug reports are re-checked in case any were fixed there.
- Experiments run on the research group's shared server at TU Darmstadt (address not in this
  public repository: `agent/tools/server.local`). The checkouts there must be
  **identical** to the local ones; code is never edited on the server.
- The Claude login is passed to a running job only through its environment and never left
  on the server.

---

## 1. Why benchmarks need a preparation step

The agent (`discopop_agent`) makes these assumptions about its input:

| Assumption | Where it comes from |
|---|---|
| One source file. Since 2026-09-14 either C (`clang`, `discopop_cc`) or C++ (`clang++`, `discopop_cxx`), chosen by file extension — before that, C++ only | `gate/toolchain.py` (`compiler_for`), `profiling/tools.py` (`_wrapper_for`), agent `docs/FIXES.md` Fix 51 |
| No extra flags, include paths or second translation unit | the agent CLI has `--source-file` but no build-command option |
| Correctness = the program's **stdout** matches the original | `gate/timing.py` captures stdout; stderr is only used for diagnostics |

**C support was added to the agent for this campaign** (decision 2026-09-14). The agent had
been C++-only by accident — its toolchain lookup found only `clang++` and profiling always
used `discopop_cxx` — not by design; DiscoPoP itself handles both. Running C benchmarks as
C matters for validity: `clang++` silently compiles a `.c` file as C++, and C++ rejects
valid C (implicit `void*` conversion, `restrict`, keywords such as `new`). It also changes
what DiscoPoP reports — see the measurement in §2.

The harness benchmarks still break the remaining two assumptions. PolyBench/C 3.2 kernels
need `utilities/polybench.c` as a second file plus `-I` paths, and print their results to
**stderr** — only when `POLYBENCH_DUMP_ARRAYS` is defined. Run unchanged, the agent would
see empty stdout and its correctness gate would compare nothing, silently accepting any
rewrite.

**Decision: package benchmarks into self-contained single files; do not change the agent's
build model.** Two options were considered:

| Option | For | Against |
|---|---|---|
| **A. Preparation step in the harness** (chosen) | The agent's gate and profiling code paths stay as they were, so every configuration is measured on the code path the earlier results used. The packaging is validated once, mechanically. | Needs one converter per suite. |
| B. Teach the agent a build command and stderr comparison | Benchmarks stay as shipped. | Touches the gate, the profiler runner, hotspot detection and the timing code right before the evaluation, and would invalidate earlier measurements. |

### 1a. Rule: no parallelization answer may remain in a packaged source (2026-09-15)

Some "serial" benchmarks in the harness still carry their OpenMP version, only switched off.
The model reads the source, so it would be shown the answer:

| Benchmark | What is left in the serial source |
|---|---|
| Rodinia `nw` (`serial/nw/needle.cpp`) | the OpenMP file itself: 13 pragmas in `#ifdef OPENMP` / `#ifdef OMP_OFFLOAD` blocks, disabled only by `//#define OPENMP` |
| burkardt `md` (`md.cpp`) | 4 pragmas left as comments (`//# pragma omp …`) |
| `LULESH_SEQ` | OpenMP code under `#if _ALWAYS_FALSE_CHECK_FOR_OPENMP` (no pragmas, but `omp_get_max_threads` and threaded variants) |

Checked clean: PolyBench kernels (the only hit is `utilities/polybench.c`, not packaged), NPB-SER,
Rodinia `pathfinder` and `hotspot` serial versions. Packaging therefore removes disabled,
commented-out and preprocessor-dead OpenMP code, validates the result against the original
output like any other packaging change, and lists what it removed in `meta.json`.

Where an expert OpenMP version exists (Rodinia `nw`, `pathfinder`, `hotspot`; upstream LULESH),
it differs from the serial code only in pragmas, offload attributes and whitespace — no algorithm
was restructured, so there are no before/after restructuring pairs in these suites. The expert
version is used as a reference **by region** (which loops both parallelized, which the agent
declined, fraction of expert speedup reached), not by pragma text, because the same loop can be
parallelized correctly with different clauses. All suites are public, so a model may have seen
their OpenMP versions in training; the `no_evidence` arm bounds but does not remove this threat.

## 2. PolyBench/C 3.2 packaging

`agent/tools/prepare_polybench.py` generates `<kernel>.c` plus `meta.json` (file, language,
input and output SHA-256, generator version, default dataset).

**Rule: benchmarks are never translated to another language** (decided 2026-09-14). A C
benchmark is evaluated as C. Language conversion is out of the thesis's scope, and it would
add noise: the compiler front-end changes the code DiscoPoP instruments, so a translated
benchmark is no longer the same benchmark (see the observation at the end of this section).
The packaging touches only what the agent cannot take — the loops of the kernel are left
exactly as written.

The generated file contains, in order:

1. the kernel's system includes plus `<stdlib.h>`;
2. a default dataset that applies only when no `-D*_DATASET` is given — so the agent runs
   at a small size while the independent verifier rebuilds the **same file** at a larger
   size (e.g. `-DLARGE_DATASET`) for timing;
3. `#define POLYBENCH_DUMP_ARRAYS`, so the output code is live;
4. `utilities/polybench.h` verbatim (macros only);
5. the two functions the kernels use from `polybench.c` (`xmalloc`,
   `polybench_alloc_data`), so no second translation unit is needed;
6. the kernel header and body, with `#include` lines and the polyhedral
   `#pragma scop/endscop` markers removed, and result printing rewritten.

**Output rewrite.** All 30 kernels print through exactly two statement shapes,
`fprintf(stderr, DATA_PRINTF_MODIFIER, x);` and `fprintf(stderr, "\n");` (verified by
survey). They become `pb_emit(x);` and `pb_newline();`:

- **Default build — digest.** Each value is folded into a count, a sum and a
  position-weighted sum; three lines go to stdout at exit (`%.17g`). The weighted sum
  catches right values in the wrong place. A digest keeps stdout small: the full dump of
  2mm at STANDARD is 23 MB, and the agent's gate captures stdout on every run.
- **`-DPB_FULL_DUMP` — full dump.** The original `%0.2lf`/`%d` dump, to stdout. Used to
  prove the packaging exact and by the independent verifier.

The generator refuses to write a file if any `fprintf(stderr, …)` would survive, so a result
can never silently fail to reach stdout.

**Perturbed input (generator v3).** Some shipped inputs are fixed points of their own
kernels: seidel-2d starts from a bilinear field that a Gauss-Seidel and a Jacobi sweep both
leave unchanged, so no output comparison on that input can detect the algorithm change
(found in the first smoke run, §7). With a seed in `argv[1]`, the generated `main` adds
deterministic noise in [0, 3) to every array it declares, right after `init_array`. Without
an argument the program is byte-for-byte as before. The seed is given to the agent through
its existing `--check-input` option (no agent change) and used by the harness verification.

Validation of v3 (MINI, SMALL): no-seed output identical to the original for **30/30**;
seeded run deterministic and different from the shipped input for **27/30**. Exceptions:
`cholesky` and `trmm` already print NaN/inf on the shipped input, so no output check
(seeded or not) means anything for them; `durbin` becomes non-finite when perturbed. These
three have weak correctness oracles and should not carry experiment conclusions.

**Timed kernel region (generator v4).** Speedup is measured on the computation, not the
process — suggested by the author, and PolyBench's own convention (`POLYBENCH_TIME` times
the kernel between `polybench_start_instruments` and `polybench_stop_instruments`). At the
small sizes the agent works at, allocation, initialisation and output can dominate the
process (2mm at MINI: 69 µs of kernel in a millisecond-scale process) and hide a real kernel
speedup. The two markers become a monotonic clock that prints
`DP_TIMED_REGION_SECONDS <s>` to **stderr**, so stdout stays deterministic. The agent's gate
reads it (agent Fix 52) and so does the harness verification. Validation of v4: 30/30 print
exactly one timer line; no-seed output still identical to the original for 30/30.

**Validation (2026-09-14, macOS, LLVM 19).** For every kernel and size, the original
PolyBench program (C, two translation units, stderr dump) and the packaged program
(`-DPB_FULL_DUMP`, stdout) were built and run, and their outputs compared byte for byte; the
digest build was run as well.

| Sizes | Kernels identical | Digest builds OK |
|---|---|---|
| MINI, SMALL | **30 / 30** | 30 / 30 |

Reproduce: `agent/benchmark prepare --size SMALL --validate` (writes
`agent/prepared/polybench/validation.json`).

**Observation behind the no-translation rule — not an experiment result.** Before the agent
supported C, a first version of the packager (generator v1) translated the kernels to C++.
Once C support existed, `seidel-2d` at SMALL was profiled once in each form: DiscoPoP
reported 4 `do_all` patterns for the C++ file and 7 for the C file. The loops that differ
were not investigated, and it is one sample each of a non-deterministic tool (§3), so the
numbers carry no weight; the direction is the point — translation changes the tool's answer.
Generator v1 and its `--lang cpp` option were removed; all runs use C.

## 3. The runner (`agent/benchmark`)

`agent/tools/cli.py` follows the conventions of the other three harnesses (wrapper script,
`shared/run_store.py`, one self-contained `agent/runs/<run_id>/` per execution) but runs
**agent configurations** instead of DiscoPoP versions. Usage is in `agent/README.md`.

**Arms** are named flag sets in `agent/config/arms.json`, each tagged with the thesis-plan ids it
serves (B1, B4, B5, E2, E6, X1). An arm is changed only together with an entry in §6.

**One trial** = (benchmark, arm, model, repeat), in three phases:

1. **Profile — once per benchmark per run.** Every trial starts from a copy of the same
   `.discopop` directory. *Why:* DiscoPoP itself is not deterministic (it emits a racy
   pragma roughly one run in six), so profiling per trial would add tool noise to every
   arm comparison. Its run-to-run variation is measured separately (X0c), not mixed in.
   The wrapper follows the file's language (`discopop_cc` + `-lm` for C).
2. **Agent.** `python -m discopop_agent` with `--provider`, `--model`, `--edit-mode` and the
   arm's flags, output streamed to `agent.log`.
3. **Independent verification.** The agent's own verdict is recorded but never trusted.
   The harness builds the original sequentially and the final source with `-fopenmp`
   (`clang` for C, `clang++` for C++) and:
   - compares the full value dump at the agent's size **exactly**;
   - compares the digest at a larger verify size at each requested thread count, repeated,
     within relative tolerance `1e-9` (a correct parallel reduction moves the last digits by
     ~1e-16; a wrong result by far more), and requires identical digests across repeats at a
     fixed thread count (movement there is a race);
   - repeats the exact dump and the digest comparison on the **perturbed input**
     (`--check-seed`, default `7`), because the shipped input can be blind (§2);
   - takes medians of the **kernel time** (the program's `DP_TIMED_REGION_SECONDS`) and of
     whole-program wall time; the reported `speedup` is the kernel speedup, the
     `program_speedup` stays alongside, and `kernel_program_disagree` flags a kernel gain the
     whole program does not share (a sign of work moved out of the timed region). If a
     rewrite removed the timer, that thread count falls back to program time and says so.

**Outcomes** (one per trial, from verification only):

| Outcome | Meaning |
|---|---|
| `FASTER` | correct, parallel, ≥ 1.1× at some thread count |
| `parallel-not-faster` | correct and parallel, no measured gain |
| `changed-not-parallel` | source rewritten, no `#pragma omp` survives |
| `no-change` | source untouched |
| `BROKEN` | values differ from the original, or move between repeats at fixed threads — an unsafe acceptance |
| `VERIFY_FAILED`, `AGENT_ERROR`, `AGENT_TIMEOUT`, `PROFILE_ERROR` | no verdict possible |

**Reproducibility.** Every run manifest records the agent and harness `HEAD` plus a SHA-256
of any uncommitted diff, host, compilers and the exact flags of every arm — enough to prove
that a result came from the same code on the Mac and on the server. Trials are resumable:
re-running with the same `--run-id` skips trials that already have a `trial.json`.

**Data captured for the thesis (every trial, automatically).** Beyond the outcome and the
verification numbers, `trial.json` records: gate failures per stage, split into Phase A (the
model's rewrites) and Phase B (DiscoPoP's pragmas); gate passes; region verdicts (deferred,
accepted, applied, dropped, skipped); changes Settle dropped; model calls and reverts;
agent/verify/profile seconds; the host's load average at start and end (the server is
shared); start/finish timestamps. The run manifest adds the `claude_agent_sdk` and bundled
CLI versions next to both repos' git state.

**Figures and tidy data (automatically after every run; `agent/benchmark plots` to rebuild
or combine runs).** Output: `trials.csv` (one row per trial), `gate_failures.csv` (long
format), and PDF (thesis) + PNG (slides) figures with a `figures.md` of captions:
`fig_outcomes` (outcome composition per arm·model, RQ1/RQ2), `fig_speedups` (best speedup
per kernel, correct results only, RQ3), `fig_gate_stages` (which stage rejected rewrites,
RQ2), `fig_evidence_model` (E2 interaction and BROKEN counts, RQ4), `fig_cost` (time and
model calls per trial). Combining runs (e.g. E3 reuses E1's `full` trials):
`agent/benchmark plots --runs e1_core,e3 --name e3_matrix` → `agent/analysis/e3_matrix/`.
Figure design follows the reference data-viz method, with every palette run through its
validator: categorical slots 1–3 only in overlapping marks (all-pairs pass), facets beyond;
gate stages shown as five groups on five blue steps (nine separate steps failed the
adjacent-lightness check; per-stage counts stay in `gate_failures.csv`); outcome hues green /
blue / yellow / red / violet (adjacent pass) with grey as the neutral "no change"; one axis
per panel; light surface for print.

**Storage.** Kept per trial: `original.<ext>`, `final.<ext>`, `changes.diff`, `agent.log`,
`agent_patches/` (including `accepted.json`) and `trial.json`. Deleted after each trial: the
`.discopop` copy and verification binaries (regenerable, and large). `agent/runs/` is
git-ignored; runs are archived from the server to the Mac.

## 4. Credentials on the server

The agent's default provider (`claude-agent-sdk`) drives the `claude` CLI, which normally
reads a login stored on disk. On a shared server that login would persist. Policy:

- The long-lived token is created on the author's Mac (`claude setup-token`) and kept in the
  macOS Keychain — never typed into a chat, a file, or a command line.
- A job receives it only as the `CLAUDE_CODE_OAUTH_TOKEN` environment variable, read from
  stdin over SSH (so it never appears in `argv`, where other users of the machine could see
  it in `ps`), together with a throw-away `CLAUDE_CONFIG_DIR` that is deleted when the job
  ends.
- After every run a sweep checks for `.credentials.json`, token-bearing config keys, and
  shell-history entries.

Audit before any experiment (2026-09-14): no `.credentials.json` anywhere under the home
directory; `~/.claude.json` holds no `oauthAccount` or API key; no token in `.bashrc`,
`.profile` or history. The August 2026 login left nothing behind.

Residual risk, stated for completeness: while a job runs, its environment is readable by
root on that machine.

Implementation (2026-09-15): `agent/tools/server.sh` on the Mac and `agent/tools/job.sh` on
the server; usage in `agent/README.md`, "On the server". `server.sh run` checks parity first,
reads the token with `security find-generic-password … -w`, and writes it to the SSH session's
stdin. `job.sh launch` reads it with `read`, creates a `mktemp -d` config directory, and starts
the job detached (`setsid nohup`), with the token only in the environment. When the job
ends, even after SIGTERM, it deletes the config directory and scans every file written
during the job (home configuration, caches, `agent/runs/`, the agent checkout, `/tmp`) for the
token value. The token is given to `grep -f` through a process substitution, so it never
appears in a command line. Then it runs the general sweep (credential files, credential keys,
history) and removes config directories left by jobs that were killed with SIGKILL. The
result is written as `SWEEP:` lines at the end of the job's log.

Removing the token when the campaign ends (2026-09-16, token created by the author):

1. `security delete-generic-password -a "$USER" -s claude-code-oauth-token` — deletes the
   local copy, so nothing on this machine can use it again.
2. **Revoke it at <https://claude.ai/settings/claude-code>.** This step is the one that
   matters: deleting the Keychain item stops local use but leaves the token valid, and
   `claude setup-token` can only mint tokens — it has no `--list` or `--revoke`, so the
   account page is the only place a minted token can be invalidated.
3. `agent/tools/server.sh sweep` — confirms the server holds no credential file, no
   credential key and no token-bearing history entry (checked clean on 2026-09-16).

## 5. Server state found before the campaign

| Item | Finding | Action |
|---|---|---|
| Agent checkout | `~/discopop_agent` at `5631823d` (2026-08-23); local is `4927898c` + uncommitted work | sync with parity check |
| Harness | not present | sync this branch |
| `claude` CLI | installed at `~/.local/bin/claude` (2.1.241), not on non-interactive `PATH` | none — the agent uses the CLI bundled inside the `claude_agent_sdk` package in its venv (observed locally: `…/site-packages/claude_agent_sdk/_bundled/claude`) |
| Compiler selection | agent preferred `clang++-19`, which has no `omp.h` on this server | **fixed in the agent** (Fix 51): `clang-20`/`clang++-20` are preferred over 19; `DP_CC`/`DP_CXX` override |
| libarcher | present at `/usr/lib/llvm-20/lib/`, not on the agent's search list | **fixed in the agent** (Fix 51): `/usr/lib/llvm-{20,19}/lib/libarcher.so` searched |
| matplotlib | missing from system Python | install into the venv |
| X11 | `xauth` present, `X11Forwarding yes`, tkinter works; XQuartz missing on the Mac | install XQuartz locally |
| Disk | 94 % used, 126 GB free | keep `.discopop` directories out of long-term storage |

### 5a. Server setup performed — 2026-09-15

| Step | What was done | Result |
|---|---|---|
| Disk | removed `~/bench/lulesh_dp` (7.1 GB, the August LULESH profile; checked unused with `lsof`), author approved | 46 → 53 GB free (still 98 % used) |
| Agent checkout | untracked `build_dp.sh` / `build_dp.log` (the August build record) moved to `~/bench/build_dp_2026-08-23/`; 8 tracked macOS `.dSYM` files that had been deleted on the server restored; `agentic_DiscoPop` fast-forwarded from GitHub, `5631823d` → `d9fd6c03` | clean working tree, same commit as the Mac |
| Rebuild | not needed for the compiled profiler and hotspot detector: since their build on 2026-08-23 only the wrapper scripts changed (next row) | — |
| **Explorer drift (found by the feature suite)** | first suite run on the server: 13 passed, 2 failed, 1 skipped (Mac: 16/16) — `dep-evidence` found no `explorer/doall_prevented.json`, and `fast refresh ≡ full` disagreed by one Do-All. Cause: on the Mac `discopop_explorer`, `discopop_library` and `discopop_gui` are editable installs of the checkout; on the server they were copies installed on 2026-08-23 — 15 explorer files older and 10 missing (among them the Do-All detector that writes the blockers file), library 4 missing. Reinstalled on the server as on the Mac: `pip install --no-deps -e ./explorer -e ./library -e ./GUI` | imports now resolve to the checkout. Without this the server agent would have received no DiscoPoP Do-All blockers as evidence — a silent difference between Mac and server that would have biased every evidence comparison (E2) |
| DiscoPoP wrappers | `profiler/scripts/{CC,CXX}_wrapper.sh` and `hotspot_detection/scripts/{CC,CXX}_wrapper.sh` copied into the venv's `.libs` directories | byte-identical to the checkout (`cmp`) |
| Python packages | `anthropic==0.115.0` and `claude-agent-sdk==0.2.128` installed into the venv — the Mac's versions | the agent is imported from the checkout (the harness sets `PYTHONPATH`), not from site-packages; `--min-runtime-share`, `--exclude-functions`, `--check-input` present |
| Credentials | re-checked: no `.credentials.json` under `~/.claude`, no token in shell files | nothing stored |
| Harness | GitLab asks the server for a login, and no credentials are placed there, so the branch was copied from the Mac with `rsync` (`.git` included; `agent/runs/` and `agent/prepared/` excluded — packaged benchmarks are regenerated and validated on the server) | parity: see below |

Toolchain check (throw-away directory, deleted afterwards):

| Tool | Check | Result |
|---|---|---|
| C compiler | agent's `compiler_for("k.c", …)` | `/usr/bin/clang-20` (Ubuntu clang 20.1.2) |
| DiscoPoP on C | `discopop_cc` on a 2-D stencil, run, `discopop_explorer` | profile written; 3 patches suggested |
| TSan + Archer | racy `parallel for` built with `-fopenmp -fsanitize=thread`, `OMP_TOOL_LIBRARIES=/usr/lib/llvm-20/lib/libarcher.so` | Archer loaded; 3 race reports |
| Polly | `-fpolly` is an unknown flag and loading `LLVMPolly.so` aborts ("option registered more than once"): Ubuntu's clang-20 already contains Polly | **working baseline command:** `clang-20 -O3 -fopenmp -mllvm -polly -mllvm -polly-parallel -mllvm -polly-process-unprofitable`; on the stencil it emits `GOMP_parallel` calls, plain `-O3` none |

Machine: 2 × AMD EPYC 9255 (48 cores, no SMT; NUMA node 0 = CPUs 0–23, node 1 = 24–47),
755 GB RAM. Shared: 27 logged-in users at setup time, load ≈ 2.5 from another user's two
single-threaded jobs. Timing therefore runs pinned to one NUMA node (`numactl`), and host
load is recorded at the start and end of every trial.

Parity and validation on the server (2026-09-15):

- `agent/tools/server.sh parity`: both repositories at the same commits; DiscoPoP wrappers
  installed from the checkout on both machines; `discopop_explorer` and `discopop_library`
  imported from the checkout on both; `anthropic` 0.115.0 and `claude-agent-sdk` 0.2.128 on
  both. The first comparison also caught the **Mac's** installed `CXX_wrapper.sh` differing
  from its own checkout (a comment only); the checkout copy was installed. Remaining known
  differences: Python 3.11 (Mac) vs 3.12 (server), and the operating system and CPU.
- PolyBench regenerated and validated on the server with its own clang-20: all 30 packages
  **byte-identical to the Mac's** (same `inputs_sha256` and `output_sha256`, generator v4,
  SMALL), output identical to the original PolyBench at MINI and SMALL; cholesky and trmm fail
  the perturbed-input check, as on the Mac (§2).
- Agent feature suite after the explorer reinstall: 15 passed, 0 failed, 1 skipped
  (`dependence review`, see the finding below).
- Re-checked on the server 2026-09-16 at agent `7d3820c6` / harness `40fd846`, with parity
  confirmed on every item (commits, wrappers, explorer and library imported from the checkout,
  `anthropic` 0.115.0, `claude-agent-sdk` 0.2.128): **17 passed, 0 failed, 1 skipped**. The two
  checks added with Fixes 55 and 56 (`timing-size`, `omp-include`) pass on Linux as on the Mac.
  The skip is again `dependence review`, and §5b now explains it: that profile drew 0 Do-All
  blockers, which T0.2 measured as the normal spread rather than a fault.
- Launcher (`agent/tools/server.sh` + `job.sh`, §4) tested with dummy tokens only: a job
  started, ran, deleted its `CLAUDE_CONFIG_DIR` and swept clean; a token planted in a file
  under `agent/runs/` was reported by the sweep; a launch without a token on stdin is refused.

### 5b. Finding — DiscoPoP's Do-All verdict varies between profiles of the same program (2026-09-15)

The skipped `dependence review` check led to this. Its case, `prefix_sum.cpp`, has a real
recurrence in the loop at line 18 (`running += …; out[i] = running;`), so a Do-All there is
unsafe. The program was profiled from scratch each time with the suite's own `_profile`
(`discopop_cxx`, run, `discopop_explorer`), and the blockers DiscoPoP wrote for that loop
were counted (`explorer/doall_prevented.json`):

| Machine | Profiles | Profiles with the 4 blockers | Profiles with 0 blockers |
|---|---|---|---|
| Mac | 11 | 8 | 3 |
| Server | 8 (5 suite runs, 3 probes) | 0 | 8 — the inspected profile also suggests a Do-All at line 18 |

Ruled out, each by a direct test:

- **The explorer or its Python (3.11 vs 3.12).** The verdict follows the profile, not the
  machine: the Mac's profile run through the server's explorer gives 4 blockers, and the
  server's profile run through the Mac's explorer gives 0 blockers and the Do-All at 18.
- **Hash randomisation.** The same verdict under `PYTHONHASHSEED=0` and `12345`.
- **The static region ids.** They are negative on the Mac (`S-1209082590`) and positive on the
  server (`S2051627010`). Rewriting them into the other form changes nothing on either
  machine, and the static dependencies are identical once the ids are normalised.
- **Order within a dependency line.** The Mac profile has `82 NOM RAW 48|running … RAW 84|running`
  and the server profile the reverse order. Swapping the two entries changes neither verdict.

What does differ between profiles: the dynamic dependencies of the arrays `a` and `out`
carry different callpath-state suffixes (`41@21` vs `41@23` / `41@64`) and address-derived
`GEPRESULT` region ids. On the Mac the blocker is the *static* dependency on `running`. The
detector keeps a static dependency only as a "second chance", and only if the variable is
not classified as first-written, initialised or a reduction in the loop — a classification
built from the dynamic data. That is the working hypothesis; the root cause is not
isolated. The probe profiles are kept on the server in `~/dp_prefix_probe`.

Consequences for the campaign:

- DiscoPoP's own suggestions, and the Do-All blockers the agent passes to the model as
  evidence, are a random draw per profile. In this case the server drew the unsafe
  suggestion every time.
- Within one run the harness profiles each benchmark once, and all arms and repeats use that
  profile. Arm comparisons are therefore paired on the same draw, but a result can still
  depend on which draw it was. The profile each run used must be kept with the run.
- An instrument study is added before E1: profile each benchmark several times and report
  how stable the patterns and blockers are. A DiscoPoP-only arm (`discopop_gate`) that
  accepted the Do-All at line 18 would be accepting an unsafe suggestion. Whether the gate
  rejects such suggestions is measured by E7.

**Confirmed on a portfolio benchmark, and narrowed (2026-09-16).** `seidel-2d` as packaged
(MINI dataset) was profiled from scratch 10 times on the server — `discopop_cc`, run,
`discopop_explorer`:

| Quantity | Across the 10 profiles |
|---|---|
| `dynamic_dependencies.txt` with memory-region ids and callpath numbers masked, lines sorted | **one value, identical in all 10** |
| `dynamic_dependencies.txt` as written | 10 different files |
| `explorer/patterns.json` | 10 different files |
| Patterns suggested | 11 (×4), 14 (×1), 23 (×3), 26 (×2) |
| Do-All blockers | 0 (×5), 3 (×5) |

This narrows the finding: **the dependences DiscoPoP observes are deterministic** — the
profiled run sees the same ones every time — but the identifiers it labels them with are
not (memory regions are derived from addresses, callpath states are numbered per run), and
the explorer's result moves with those identifiers. The same program therefore yields
between 11 and 26 suggestions, with or without its Do-All blockers, from identical
dependence facts. It is an upstream DiscoPoP property, not an agent effect, and normalising
those identifiers would remove it.

Consequences, in addition to those above:

- The harness's rule of one profile per kernel per run, shared by every arm, is **necessary**,
  not a convenience: two arms profiled separately could differ by the draw alone.
- `discopop_gate` (DiscoPoP alone through the gate) is itself a draw. E1 reports it together
  with the profile it used, and its suggestion count is reported as a range, not a number.
- T0.2 (run `t0_2_stability`, §7) measured this over six kernels × 10 profiles and **settles
  the question**: the dependences DiscoPoP observes are deterministic, what it reports from
  them is not. The multiset of dependences — each taken as (sink, type, source, variable) with
  the per-run labels dropped — has **exactly one value per kernel across all 60 profiles**,
  while `patterns.json` differs in every profile and the suggestion count moves by up to a
  factor of three. The line-level hash in the first table above is a weaker measure and must
  not be quoted on its own: DiscoPoP may group the same dependences into a different number of
  lines, which changes a line hash although no dependence changed (measured on
  `floyd-warshall`: same 376 masked lines, different grouping, identical multiset).

**Refined: a second source of variation, inside the explorer itself (2026-09-16, T0.7).** The
statements above compare *profiles*. When one profile is kept fixed and only
`discopop_explorer` is re-run on it, the explorer's output still changes:

| Program | Explorer runs on one profile | Result |
|---|---|---|
| 2mm | 10 | 10 different `patterns.json`; Do-All **21 in every run**; task patterns 6–57; 2 reduction patterns in 2 runs only |
| 2mm, `PYTHONHASHSEED` fixed (0 and 7, five runs each) | 10 | still 10 different outputs (task 6–51) |
| Rodinia `pathfinder` | 20 | **15 crashed** (`IndexError: string index out of range` in `TaskGraph.recursive_assignment`), 5 succeeded |
| `pathfinder`, `PYTHONHASHSEED` fixed | 10 | 7 crashed |

So there are two sources, and they are distinct.

1. **The profile's per-run labels** (above). They move the Do-All blockers and suggestions,
   and the verdict follows the profile across machines and hash seeds.
2. **The explorer's own analysis on a fixed profile.** It moves the task patterns, sometimes
   the reduction patterns, and can crash outright.

The second does not come from string hashing (a fixed seed changes nothing). The likely
mechanism, not isolated: the task-graph code keeps sets of `Context` objects, which hash by
memory address, so they are walked in a different order on every run. The task graph is
built on every explorer run and the Do-All/reduction detector uses it, so no option avoids
it. The crash is an unchecked string index (`loopstate_info[loopstate_position]`).

*Consequences.* T0.2's "suggestion count moves by up to a factor of three" includes this
explorer-internal variation. On 2mm it is entirely in the task patterns: T0.2's 30–77 there
is consistent with a fixed 21 Do-All plus 6–57 tasks. A crash in the harness's single
profile would have lost every trial of that benchmark in a run, and a crash inside the agent
reverted rewrites and discarded dependence reviews. Both now retry on the same profile,
without modifying DiscoPoP (agent Fix 60; harness change log).

### 5c. How the agent orders regions — "time saved" is, in effect, "time consumed" (2026-09-16)

**What the code does** (`plan/impact.py`, `plan/scoring.py`). When DiscoPoP's hotspot
detection has run, every candidate region is scored by its *predicted time saved*, from
Amdahl's law:

    ΔT_r = T · f_r · (1 − 1/(P·e))

* `f_r` is the region's measured share of runtime: its total inclusive wall-clock time over
  the run (summed over every entry, nesting-safe, `gettimeofday`, 1 µs), divided by the
  largest such time, which is `main`'s.
* `T` is that largest time.
* `P` is the thread count (`os.cpu_count()`).
* `e` is one parallel efficiency for the whole run. It starts at 1.0 and is updated from
  speedups the gate actually measures.
* A region inside an already accepted one scores 0.

**Why that is the same order as time consumed.** `T`, `P` and `e` are the same for every
region at any moment (`e` is one run-level number, not per region), so `ΔT_r` is `f_r`
multiplied by a common constant. Sorting by `ΔT_r` therefore sorts by `f_r`, the share of
runtime the region consumes, and the "time saved" wording adds no information to the order.
Checked on `pilot2`: `T` = 39.2 ms and `P` = 48 give 38.3 ms for `main` (100 %) and 19.9 ms
for the kernel loop (51.9 %), exactly the agent's printed table, whose ratio 0.519 is the
ratio of the shares. Updating `e` rescales every region alike and never reorders them.

Tie-breaks, applied in this order:
1. A measured region comes before an unmeasured one. The two scales (seconds against the
   log-workload proxy) are not comparable, and the detector not reporting a region is its
   own measurement saying the region is below threshold.
2. A function is demoted just below a loop inside it when that loop carries ≥ 90 % of the
   function's time.
3. At equal score, the outermost region comes first.

What the order therefore is: **the Amdahl upper bound on what parallelising each region
could save.** That is the optimistic assumption that every region parallelises perfectly.

**Which ordering is better, and why.**

* *Time consumed (the Amdahl bound), as implemented.* It is measured, not guessed. It is
  reproducible: three repeated instrumented runs of seidel-2d on the Mac gave the kernel 59.4 / 58.9 / 58.8 % at SMALL,
  75.0 / 73.9 / 74.5 % at STANDARD and 74.5 / 74.2 / 74.0 % at LARGE, and the output routine 35.2 / 35.8 / 35.9 %
  at SMALL. No
  region with a small share can outrank one with a large share, and no region can save more
  than its share, so nothing that could matter is ranked low. Its weakness: it ignores
  whether a region *can* be parallelised. A hot region that is inherently sequential ranks
  first and absorbs the budget. `pilot2` spent 6 of its 8 calls on seidel-2d's in-place
  Gauss–Seidel sweep (51.9 % of runtime), which no correct simple rewrite parallelises.
* *Expected time saved.* `f_r · (1 − 1/(P·e_r)) · p_r`, with a per-region chance `p_r`
  that the region is parallelisable and a per-region efficiency `e_r`. This is the right
  quantity in principle: a 30 % Do-All is worth more than a 60 % recurrence. But `p_r` and
  `e_r` have to be estimated (from DiscoPoP's loop-carried dependences, iteration counts,
  work per iteration), and a wrong estimate ranks confidently and wrongly. The old
  workload proxy is the cautionary example: it ranked example4's CHECK loop above the SORT.
* *Workload proxy* (`c · log₂(1+W) − λ`). It is the fallback when no measurement exists and
  is known to misrank (above); the arm `full_no_hotspots` keeps it for E9.

**Position taken for the thesis.** The ordering stays *time consumed*, described honestly as
the Amdahl upper bound rather than as a prediction of what will be saved: it is the only one
of the three that needs no estimated parameter. Whether a region can be parallelised is
exactly what the model and the gate are there to find out, and the cheaper place to use that
knowledge is the *budget* (how many attempts a region gets), not the order (§6a plan, point
4, pending). The wording in the agent's own log ("ranking by predicted time saved") is
accurate only as an upper bound; the thesis text must say so.

**Two properties of the measurement that the evaluation has to state:**

1. *The shares come from the agent's profiling size, not from the size the result is judged
   at.* T0.5 measures both. So far, the top in-scope region's share at the agent
   size and at the verification size: 2mm 89.3 % → 99.6 %, 3mm 93.1 → 99.7, adi 74.4 → 93.1,
   doitgen 68.0 → 94.9, correlation 92.4 → 99.0, **fdtd-2d 35.2 → 84.3**. At the small size,
   setup and output weigh far more than at the size that is timed. The order among the
   kernel's own regions is what ranking needs; whether it is preserved across sizes is
   computed from T0.5's `regions.csv`.
2. *DiscoPoP's hot/cold label does not work with a single run.* The analyzer marks a region
   `YES` when both its mean time and its min/max-ratio are at or above the mean over all
   regions, `MAYBE` when one is, and `NO` when neither is. With one run min = max, so every
   ratio is 0.5 and every region is at or above the mean ratio: nothing can be `NO`, and
   `YES` simply means "time at or above the average region". The agent runs the detector
   once, so its skip-cold filter never fires, and the label carries no information beyond
   the share.

### 5d. Decisions of 2026-09-16 on which regions reach the model, and how often

Taken by the author after `pilot2`, the T0.5 share study (§7, `t0_5_shares_mac`) and §5c.
Each decision is stated with its evidence and its effect on the evaluation; the
implementation is recorded in the change log when it lands.

**D1. `--min-runtime-share 0.01` is pre-registered, identical for every arm.**
*Evidence (T0.5):* a 1 % floor removes 185 of 445 in-scope loops (42 %), and by Amdahl's
law gives up at most 1.7 % of runtime in any benchmark at the agent size (`ludcmp`), and at
most 1.2 % at the verification size (`mg`). A 2 % floor gives up up to 3.2 %; a 5 % floor up
to 16.4 % of `mg`'s runtime at the judged size, because NPB spreads real work over many
3–5 % loops. *Effect on the evaluation:* it applies to Phase B too, so DiscoPoP's own
pragmas are filtered alike and the agent and DiscoPoP are compared on the same regions.
DiscoPoP's unfiltered pattern counts stay in `trials.csv` (`discopop_do_all`, from the
profile) for comparison with the literature. Speedup can change by at most the bound above.
Counts of parallelised regions fall, because tiny loops are no longer attempted. Model
calls and agent time fall. The floor is an efficiency setting: it finds no additional
parallelism. Caveat to report: shares are measured at the agent's size; T0.5 shows the order
of regions is preserved at the verification size (top loop identical in 22 of 23
benchmarks, median Spearman 1.00).

**D2. A region already covered by an accepted rewrite gets no model call.**
*What it is, and what it is not.* `--restructure-depth` controls whether regions that a kept
rewrite *created or revealed* (depth ≥ 1) may themselves be rewritten. It does not touch
regions that were in the queue from the start (depth 0) and lie *inside* a region just
accepted, for example the inner loops of an accepted outer loop. After the acceptance
`ImpactModel.mark_covered` sets their predicted saving to 0, but the queue skips a region
only when its saving is *below* `--min-impact` (default 0), so a saving of exactly 0 passed
and each covered region still received the full budget. *Effect:* fewer calls, no lost
parallelisation (the time is already won by the enclosing region), no effect on speedup.
Applies to every arm.

**D3. The per-region model budget will be weighted by importance and become the default,
after calibration.** Today every region gets the same `--budget` (3). Evidence so far is
too thin to choose values: in the three trials where the model answered, 3 regions were
accepted, all on the second attempt, and no third attempt succeeded in about 14. *Plan:*
build the mechanism (attempts scaled by a region's runtime share between a minimum and a
maximum, covered regions at zero); run a calibration with a larger fixed budget on
benchmarks **held out of the evaluation**, so the values are not tuned on the data they are
judged on; measure at which attempt regions succeed; choose the minimum and maximum from
that; then make the policy the default in every arm. *Open: which benchmarks are held out.* All 37 packaged benchmarks run in E1, so none of them is untouched by the evaluation. Candidates: the agent's own synthetic test programs (fast, clearly outside the evaluation, but small), or PolyBench 4.2 kernels that are not in 3.2 (representative, but they must be packaged first). About 30 accepted regions are needed to estimate on which attempt success comes. *Consequence for the plan:* E2
compares budget 1 with budget 3. With a weighted default that comparison must be redefined
(for example weighted against a single attempt), and the change must be recorded in the
plan before E2 runs.

**D4. `main` is excluded only if DiscoPoP itself never proposes a pragma there.** The author's
criterion: if DiscoPoP, run on its own, never proposes a pragma in `main`, excluding `main`
removes nothing from the comparison with DiscoPoP and is applied to all benchmarks
(except `md`, whose timed computation is in `main`). If DiscoPoP does propose pragmas in
`main`, `main` stays in scope so the agent can be compared against those suggestions.
Being checked against DiscoPoP's unfiltered `patterns.json` for all 37 benchmarks (result
recorded below when available). T0.5 already shows what `main` holds: scaffolding only in
all 30 PolyBench kernels, a digest loop in the NPB drivers, untimed input generation in
`hotspot` and `nw`, the timed computation in `md`, and in `pathfinder` a grid generator
taking 77.9 % of runtime outside the timed region.

### 5f. Proposed: a small open model (Qwen3-Coder-30B) as a third model (2026-09-17)

*Why.* H5 predicts that DiscoPoP's evidence helps a weaker model more than a stronger one,
and so far the comparison is between two strong commercial models (Haiku, Sonnet). The
author's group hosts `Qwen/Qwen3-Coder-30B-A3B-Instruct`. Adding it stretches the
comparison down to a genuinely small, open-weights model, which also makes the experiment
reproducible by anyone and costs no subscription usage. Earlier agent work with it
(July–August 2026) found that it follows output formats reliably and classifies blocking
dependences correctly from the evidence. It often states the right fix and writes different
code, and within 3 attempts it never solved the odd-even sort. The gate caught every wrong
rewrite it produced.

*Constraint set by the author:* the same experiment with only the model changed, in `direct`
mode, and **nothing changed on either server**.

*What `direct` mode needs.* The agent does not edit files itself in `direct` mode. It runs
Claude Code, which gives the model file tools and runs the conversation; the model only
decides. Claude Code talks to its model in Anthropic's Messages format (`/v1/messages`).

*What the Qwen server offers* (read-only inspection, 2026-09-17, host `cs-245` =
the group's model server):

| Property | Value |
|---|---|
| Server | vLLM **0.10.1.1**, running as root for 86 days, listening on `127.0.0.1:18000` only, API key required |
| Model | `Qwen/Qwen3-Coder-30B-A3B-Instruct`, `--max-model-len 256000` |
| Tool calling | `--enable-auto-tool-choice --tool-call-parser qwen3_coder` |
| Hardware | one NVIDIA GH200 (89 of 98 GB in use, idle at the time) |
| OpenAI format (`/v1/chat/completions`) | answers |
| Anthropic format (`/v1/messages`) | **404, not among its routes** |
| Security advisory GHSA-79j6-g2m3-jgfw (qwen3_coder parser) | not affected: 0.10.1.1 is the patched version |

*Reachability.* The experiment server reaches its SSH port; port 18000 is closed from
outside (loopback only), so access is through an SSH tunnel. The author's key
`~/.ssh/abosamaha` is now authorised on it, installed once with the password, which is
stored nowhere. For runs on the experiment server the tunnel is to be opened with SSH agent
forwarding at launch, so the key is never copied there.

*Consequence.* Claude Code cannot use this server directly; newer vLLM versions offer the
Anthropic endpoint natively, but upgrading is excluded. Two options remain.

1. **A translator** (LiteLLM) between Claude Code and vLLM, installed in user space (a
   virtual environment) where the agent runs, touching nothing system-wide. Both models then
   run through the same Claude Code loop and only the model differs. Costs: the translator
   becomes part of the setup and must be stated and smoke-tested for tool-call fidelity; a
   known LiteLLM issue can place a system message mid-conversation (#40693). As recalled from
   before the model's knowledge cutoff, some LiteLLM releases on PyPI were compromised in
   2026, so only a pinned, checked version would be installed, and only after a test on the
   Mac.
2. **The agent's own tool loop** for OpenAI-compatible models. No third-party code, but Claude
   and Qwen would then run through different loops, confounding model with harness.

`function` mode (the model returns a rewritten function) is excluded by the author: the
comparison must use `direct` mode.

*Status:* proposed, pending the author's choice between options 1 and 2 and a smoke test.
If it goes ahead, it becomes a third model in E2 Part A (evidence on and off, one attempt,
the core ten, ×5) with an H5 extension: evidence raises the small model's success rate more
than Haiku's.

### 5e. Instruments — every study that is not an experiment, its tool, and how it measures

Nothing in this table calls a model. Each study removes a way a later number could be
misread. IDs follow the plan (T0.1–T0.4) and continue from there. Every tool writes its raw
data next to a summary and records the host.

| ID | Question | Tool (in `agent/tools/`) | How it measures | Output | Status |
|---|---|---|---|---|---|
| T0.1 | At which size is each benchmark's serial computation long enough to time? | `size_table.py` | Serial `-O3` build per dataset size, pinned to one NUMA node, 3 runs, median of the timed region (`DP_TIMED_REGION_SECONDS`). Verification size = smallest reaching 1 s; timing size = smallest reaching 0.25 s | `sizes.csv`, `chosen.json` → `kernel_sizes.json` | done (§7 `t0_1_sizes`, `t0_1_apps`) |
| T0.2 | Is DiscoPoP's profile the same every time? | `profile_stability.py` | 10 full profiles per kernel; hashes of patterns, blockers, dependence files, and the dependence multiset with per-run labels dropped | `profiles.csv` | done (§5b, §7) |
| T0.3 | Can the correctness oracle see a wrong program? | `oracle_study.py` | Every candidate the gate judged in any archived run (`agent/results/**/agent_patches/`) is rebuilt as the gate saw it — the trial's original plus the patches accepted before it, then its own patch (`patch -p0 -F0`; header paths normalised) — and replayed through the harness verification (`cli.verify`: full dump and digest against the original, the perturbed input, repeats at fixed threads). Candidates rejected before a build (`clause`, `apply`, `compile`) have no program and are counted as such. Read-out: on programs the gate rejected for a runtime reason, caught / not caught and by which check; on accepted programs, agreement (a BROKEN there is a gate false accept) | `candidates.csv`, `summary.json`, one verify record per replay | **done, Mac, 18 Sep** (`t0_3_oracle_mac`, §7): 82 candidates, 42 replayable. Gate-rejected at runtime: 19 of 23 flagged — all 14 output-caught ones by the **perturbed input only**; the 4 not flagged = 2 benign races only TSan sees + 2 correct scans the gate over-rejected (noise floor 0). Gate-accepted: 19 of 19 agree |
| T0.4 | What speedup can a shared host resolve, and do concurrent lanes interfere? | `timing_noise.py` | Per benchmark two binaries built as the harness builds them — serial `-O3`, and Polly's auto-parallel build of the same source as a model-free parallel program — each run 10× in three conditions: alone pinned to 12 cores of one NUMA node (a campaign job), 4 concurrent lanes each pinned to its own 12 cores, and unpinned. Records every timed-region time, median, IQR, CV, max/min, and `1 + 2·CV` as the smallest median ratio the spread can distinguish; host load before and after | `runs.csv`, `summary.json` | **done (partial), server 18 Sep** (`t0_4_timing`, §7): pinned serial CV ≈ 4 % → speedups ≥ 1.1× resolvable with 5-repeat medians (= `FASTER_THRESHOLD`); 4 lanes shift medians ≈ 1 %; Polly's `hotspot` build runs minutes per execution, run stopped there |
| T0.5 | Where does each benchmark's time go, and what does a runtime-share floor cost? | `share_study.py` | DiscoPoP's hotspot detection as the agent runs it (instrument, one run, analyse), at the agent size and the verification size. Each region placed in its function (C++ names demangled), given its span by parsing the source, and marked excluded / in `main` / in the timed region. Cost of a floor = summed share of dropped loops not contained in a kept or another dropped loop, which bounds the lost speedup by Amdahl, 1/(1 − s). Size stability = Spearman rank correlation of in-scope loop shares, and whether the top loop is the same | `regions.csv`, `summary.json` | done (§7 `t0_5_shares_mac`) |
| T0.6 | Does DiscoPoP on its own propose pragmas inside `main`? | `dp_main_study.py` | Profile exactly as the harness does; place every pattern of the unfiltered `patterns.json` in its function using DiscoPoP's own `Data.xml` spans; mark patterns lying only on packaging scaffolding (`pb_*`/`PB_*` lines), which do not exist in the original benchmark; explorer retried on the same profile and every crash recorded | `patterns.csv`, `summary.json` | partial: 3 of 37 (md, is done; NPB `lu` not instrumented within 1 h), stopped by the author (§7) |
| T0.8 | Does DiscoPoP see the same program in the project layout as in the merged file? | `packaging_equivalence.py` | Both layouts profiled as the harness profiles them (merged file directly; project through the unity unit); the observed dependence multiset, the Do-All blockers and the applicable patterns compared keyed by source-line TEXT, so line numbers cannot differ | `summary.json` | **Mac, done: 29 of 29 kernels profiled in both layouts have identical kernel dependences**; every differing edge lies in `xmalloc`/`polybench_alloc_data`, which the merge had rewritten (`ptr` for `new`); blockers differ in 14 kernels and patterns in all — the explorer's own draw, reproduced within one layout on trisolv (2 blockers in one run, 0 in three). `adi`'s merged file did not instrument within the limit (known). NPB and the applications: on the server |
| T0.9 | Does a fast refresh reach the full profile's conclusions, and does it decay when chained? | agent `benchmark/refresh_depth.py` | Three synthetic programs × three rewrites; arms full / fast-step / fast-chain on identical source; patterns, applicable suggestions (unsafe = suggested only after refresh) and dependence edges compared | stdout table | §5h: 8/18 identical, 8 unsafe (all in rewritten code), 2 lost |
| T0.7 | Is DiscoPoP's explorer deterministic on one profile? | `explorer_determinism.py` (first taken by hand, §5b) | One profile per benchmark taken as the harness takes it; `discopop_explorer` re-run N times with the hash seed free and N per fixed seed, every explorer output — including its pattern-id counter `next_free_pattern_id.txt` — cleared before each run, the profiler's files digested to prove they never change. Per run: the sha256 of the pattern SET (counter-assigned `pattern_id`, traversal-assigned `task_group` and list order removed), the sha256 of the file as written, one digest per pattern type, counts, crash message | `runs.csv`, `summary.json` | Mac by hand (§5b): 2mm Do-All fixed at 21, tasks 6–57; `pathfinder` 15 crashes in 20. Tool on `vecsum` (Mac): the raw file differs in every run, the Do-All SET is identical in every run, the task SET differs in every run — so the earlier "10 different outputs" counted order and labels as well as content. Server: in the 18 Sep chain (2mm, pathfinder, NPB is; 20 + 2×20 runs each) |
| T0.10 | Is there, for every restructuring benchmark, an expert version that is correct AND faster? | `verify-source` on `reference_solutions/` | each reference judged exactly as a trial is: full dump and digest against the original on the shipped and the seeded input, stability at fixed threads, speed at the kernel's timing size | one baseline trial per reference | TSVC: 18 of 18 class-R loops ≥ 1.45× (server). LULESH (LLNL), `hotspot`, `floyd-warshall`: Mac only, 21 Sep (§7 `lulesh_ref_check`, `ref_check_mac`); server owed |
| T0.11 | Which class is each benchmark in — does DiscoPoP alone reach a verified parallel program? | arm `discopop_capability`, three independent profiles | the pipeline with no model, three draws; R = no draw reaches a verified parallel program (needs restructuring), A = the majority do (parallel as written), D = R by measurement AND a true recurrence by design (the reference solution is the sequential program) | `benchmark_classes.json` | done for the registered set (§7 `t0_11_classes_a/b/c`): R 26, A 25, D 4; LULESH and NPB-C owed |
| T0.13 | Can the arm under test KEEP a perfect rewrite? | `default_arm_ceiling.py` | the expert restructuring with its pragmas stripped, `--budget 0`: DiscoPoP profiles it, Phase B pushes its pragmas through the campaign's gate, Settle verifies | `ceiling.csv` | TSVC, Mac, 21 Sep: kept on 18 of 21, class R 16 of 18 (`s331`, `s341` need a pragma DiscoPoP cannot write). Server repeat, `hotspot`, `floyd-warshall`, LULESH owed (§5s) |
| T0.14 | Does each package accept its own expert version? | `verify-source --source <reference>` (a directory for project benchmarks) | the reference must come out correct; a `BROKEN` is a defect of the PACKAGE until shown otherwise | the baseline trial | new 21 Sep — it caught the LULESH package emitting rounding residue as a result (§6). TSVC and LULESH pass; NPB-C before E11 |

**Which settings rest on which study:**

- `kernel_sizes.json`, the verification and timing sizes, and the "too short to time"
  outcome rest on T0.1.
- One profile per benchmark per run, and `discopop_gate` reported as a range, rest on T0.2
  and T0.7.
- `--min-runtime-share 0.01` (D1) and the claim that ranking at the agent size is valid rest
  on T0.5.
- Excluding or keeping `main` (D4) rests on T0.5 and T0.6.
- The explorer retry policy (20 attempts) rests on T0.7.

### 5g. Full review of the agent, 2026-09-17/18 — what was wrong, what changed, what it means for the plan

*Why.* Before the first experiment the author asked for the whole agent to be gone through —
design, flow, depth, fast refresh, the gate, the prompts and the evidence — "to see if it
could be better or if something is wrong". *Method.* Every module was read in pipeline
order; a real prompt was rendered from a real profile and read as the model reads it; the
agent was then run end to end (with the model) on a two-file program and on one small
program under nine argument sets. Every finding is in the agent repo
(`docs/REVIEW_2026-09.md`), every fix in `docs/FIXES.md` (Fixes 64–77), and each fix has a
feature check that **fails when the fix is reverted**. No E-experiment had run, so no result
is affected; `pilot2` and `local_obs1` predate the fixes and are not comparable with
anything run afterwards.

**Findings that would have confounded a specific experiment, had it run on the old code:**

| Finding | What was wrong | Arms that would have been affected |
|---|---|---|
| P9 | `--evidence none` still opened with DiscoPoP's "evidence digest": dependence variables, loop nest with measured trip counts, calls, reductions | `no_evidence_b1` (B4, X1), `no_evidence` (E2-feedback) — the arms the evidence claim is measured against |
| P3, P4 | the prompt promised a timing step that is off in every arm, said "byte for byte" where a tolerance applies, and branded every loop "too fine-grained" at the profiling size | every arm with a model |
| P1, P12 | all PolyBench arrays tagged `[scalar]`; C++ names mangled or mutilated (`ZL1b[]`) | every arm with evidence |
| F6 | a REWRITE was failed by the dependences of the code it replaced (proven on Floyd–Warshall) | every arm with a model; random, because the blocker file is an explorer draw |
| F8 | the schedule matrix never varied the schedule (`OMP_SCHEDULE` only acts on `schedule(runtime)` loops) | every arm; the gate was weaker than reported |
| F9, F10 | numeric tolerance calibrated on the default input only, and ignored by Settle — a correct reduction was rejected or the whole run reverted | every arm, on kernels with reductions |
| F1, F18 | a `task` entry hid the loop pattern on the same line (44 lines in the suite); start-line and node-id keys shared one dictionary, so a function could inherit an unrelated loop's pattern and never reach the model | every arm, the DiscoPoP baseline included |
| F16, F17 | runtime measurements not moved onto the rewritten file after a full re-profile, and not restored after a revert | `discopop_annotates`, `llm_pragmas_full_reprofile` (no fast refresh); every `--no-llm-pragmas` arm (reverts are routine there) |
| F20 | a pragma-free rewrite marked its region "covered", so Phase B never saw the loops it had exposed and Settle then dropped the rewrite as an orphan | every `--no-llm-pragmas` arm with runtime measurements — **they could not keep a rewrite at all** |
| F19, F21 | loops nested in a loop the model had just parallelised were still sent to the model; covering the whole edited region hid sibling loops from Phase B and left a deeper level nothing to see | `full` and relatives (wasted calls, inflated pragma counts); `full_depth1`, `full_depth2` (**E8 would have measured nothing**) |
| F12 | without runtime measurements DiscoPoP's pragma could be nested inside the model's parallel loop | `full_no_hotspots` (E9) |

**Decisions.**

**D2′ (refines D2).** "Covered" means *the constructs that actually run in parallel*, each
charged its measured share of runtime — not the span of whatever was edited. A region
inside such a construct gets no call (read from the source, so it holds without runtime
measurements too); a region that *contains* one is worth what is still sequential in it
(`remaining share = share − covered share`), and is dropped only when nothing is left or
the rest is under the 1 % floor. A pragma-free rewrite covers nothing. *Effect on the
evaluation:* sibling loops of a rewritten function stay visible to Phase B; `--restructure-
depth` ≥ 1 now does what E8 asks — a rewritten function is looked at again only if
measurable sequential time remains in it.

**D6. Multi-file programs are supported, and profiled through a unity unit.** Measured on
a two-file reproducer (agent `docs/MULTIFILE.md`, feature check `project-mode`): profiled
the way DiscoPoP documents — unit by unit — **both recurrences in the unit without `main`
are reported as applicable Do-All**, because this DiscoPoP build constructs its call-path
state graph from `main`'s unit only and loops elsewhere get no loop states. Through a
generated unity unit (`#include` of every unit, compiled as one) the analysis equals that of
the merged single file, while `FileMapping.txt` still names the real files and lines. The
gate builds the real multi-file program (staged copy, candidate in place of the one file
under test); edits land in the region's own file; Settle rebuilds a set of files. *Effect
on the evaluation:* merging a benchmark into one file is no longer needed, and was never
only a convenience — it is what made DiscoPoP's analysis correct. A benchmark is measured
in one packaging only. For the 30 PolyBench kernels nothing changes (they are one file).
T0.1/T0.5/T0.6 are re-run for a benchmark whose packaging changes, after checking that the
unity profile reports the same patterns and blockers as the merged file did.

**D7. The contract bounds extra work.** Observed on the end-to-end run: with the speed check
off, the model "parallelised" a linear recurrence by recomputing every element from the
start — O(n) became O(n²); race-free, bit-identical, and certain to lose at full size. The
prompt now allows extra work within a constant factor only and says where speed is finally
judged. The harness already classifies such a result `parallel-not-faster`; this removes an
incentive the prompt had created, it does not hide the outcome.

**What the end-to-end runs showed** (agent as changed, Sonnet, Mac; not an experiment):
see the run log, `e2e_review_2026-09-18`.

### 5h. The fast refresh — what it does, how it is checked, what it cannot do (2026-09-18)

*Written at the author's request, from the code and from the measurements below.*

**What problem it solves.** After a kept rewrite the profile describes code that no longer
exists. A full re-profile is three steps — instrument+compile, run the instrumented binary,
explore — and the run is the one that scales with the workload (17× native on a 104M-op
kernel; 7.9 s of a 12 s re-profile there; on LULESH one profile is 23 s instrument at 28 GB,
4.5 s run, 16 s explorer). Everything else is static: `discopop_cc` alone rewrites
`Data.xml`, `static_dependencies.txt` and the instruction↔line mapping for the new source.
The fast refresh runs only the compile and **carries the previous run's observed
dependences forward** onto the new instruction numbering.

**How a dependence is identified, and why that is delicate.** `dynamic_dependencies.txt`
holds one row per *sink instruction*: `67@43 NOM RAW 55@43|GEPRESULT_arr(4338667626)` —
instruction 67 (the number after `@` is the call-path *state*, not a line; the explorer
strips it) reads what instruction 55 wrote, on the memory region of `arr`. Instruction ids
come from one counter in module order, so an edit renumbers everything after the first
changed instruction. `instructionID_to_lineID_mapping.txt` maps an id to `file:line:col`,
but many-to-one (ids 3, 6, 9, 12 all sit at `1:6:0`) and about a fifth of the instructions
have no position (`*`), so it cannot be inverted. Memory-region ids are addresses (dynamic)
or per-compile hashes (static) and are not stable either; only variable names are.

**The translation.** (1) A *line map* old→new from the diff the agent itself applied, on
whitespace-stripped lines (a block wrap re-indents every line inside it; verbatim comparison
lost 13 of 16 dependences to indentation alone), plus the exact column shift per line.
(2) Both mapping files are read as *sequences* of instructions; old positions are rewritten
into new-line coordinates, instructions on changed lines get a token that can never match,
and the two sequences are aligned with `difflib` — `*` instructions then match by context,
like blank lines in a text diff. (3) Every match is *cross-checked* by the independent
`(file, line, column, occurrence)` key: if the alignment and the position disagree, the
dependence is dropped rather than attached to the wrong instruction. (4) Rows are rewritten:
sink and source ids translated, the state carried untouched, `INIT *`/`0@0` sentinels passed
through, loop markers and trip counts moved by line. In a project only the rewritten file's
positions move; every other file's pass through unchanged (Fix 74). Static dependences are
NOT carried: the compile regenerates them for the new code. What cannot be placed with
certainty is **dropped, never guessed** — that is the whole safety argument.

**What is "the gap".** A dependence with an endpoint in code the rewrite *created* was never
observed, so it cannot be carried. Static analysis covers scalars there; it does not cover
array recurrences. Measured on two chains, 39 of 39 dependences a full profile has and a
refresh lacks have an endpoint on a rewritten line. Where such a loop is a recurrence the
refreshed profile can call it Do-All — the **unsafe direction**.

**How it is checked.**
* Feature checks (every commit): `fast-refresh` — an identity edit carries 39/39 dependences
  and 3/3 trip counts, lossless; `fast-refresh-eq` — after one real rewrite the refreshed
  profile reaches the full profile's conclusions except at the known new-code loop;
  `reduction-carry` — the one thing a refresh could drop that makes the agent *less*
  cautious stays with the compile; `dep-review`, `dep-evidence`, `dep-lines`.
* **T0.9, chained refreshes** (`discopop_agent.benchmark.refresh_depth`, no model): three
  synthetic programs, three successive rewrites each, three arms on byte-identical source
  states — full profile (ground truth), *fast-step* (one refresh on the full arm's previous
  profile: the translation alone) and *fast-chain* (a refresh on the previous refresh, as
  the agent does within a depth). Compared on what DiscoPoP concludes, then on dependences.
  Re-run on the reviewed code, 18 Sep: **8 of 18 comparisons identical; 8 produced a Do-All the
  full profile does not support; 2 lost one.** Every unsafe divergence sits at a step whose
  rewrite dropped observed dependences (22 and 37 of them); the step that rewrote nothing
  with dependences was identical. Trip counts were stale or missing in 13 comparisons (they
  only feed the workload proxy and the granularity note). A refresh took 5–7 s where the full
  profile took 14–21 s on these tiny programs — the explorer dominates at that size (E5 gives
  the cost curve).

**Why the agent is still sound with it on.** The refreshed profile is used for three things:
relocating the queue (line numbers), finding new regions, and — only when DiscoPoP rather
than the gate decides (`--no-llm-pragmas`) — the keep/revert verdict on a rewrite. In the
default mode the gate judges the model's own pragmas on a real build, and **Phase B always
annotates from one full re-profile**; a false Do-All from a refresh can therefore never
become a pragma. In the DiscoPoP-decides modes a false Do-All can keep a rewrite for a
while; the full re-profile before Phase B then finds no pattern, Phase B applies nothing, and
Settle drops the rewrite as an orphan — wasted work, not a wrong program. That is exactly the
difference E3 measures and E4 tries to close.

**Where the model comes in.** Two arms, opposite directions, both audited to a JSON log:
`--llm-recon` asks the model — in source terms only: loop line, type, variable, writer and
reader line — which cross-iteration dependences a run *would* have observed in the code it
just wrote; a claim is resolved by lookup against this build's files (never by inventing an
id or region) and *added* to the profile, so a wrong claim costs a missed parallelisation.
`--llm-deps` lets the model call a *static* blocker spurious and deletes it — the direction
in which a wrong claim ships a race, kept as the counter-arm for H7b. Neither runs in the
default configuration.

**Could it be designed better?** Three honest options, in order of soundness: (a) full
re-profile whenever DiscoPoP is the judge — the `discopop_annotates` arm; fast refresh only
where the gate judges (the default); (b) reconstruction (E4) — the model fills the gap in the
safe direction; (c) a real dependence analysis for the new lines (Polly/LLVM DA) instead of
DiscoPoP's scalar-only static pass — the principled fix, out of this thesis's scope. What
would *not* help: carrying dependences by name across rewritten lines (that is guessing), or
trusting the refreshed Do-All anywhere a pragma is decided. **Recommendation:** make
`--no-llm-pragmas` imply a full re-profile unless `--llm-recon` is on, once E3/E4 have
measured the difference; the arms stay as they are for the experiments.

### 5i. Review of the experiment plan before the first run (2026-09-18)

*Asked by the author: are E1–E11 a good evaluation of the agent, what are the parameters and
why.* The plan (`EXPERIMENT_PLAN.html` v13, §5–7) was read against the agent as it now is,
the end-to-end runs of 18 Sep, and the instrument results. What stands, what is changed
now, and what the author has to decide.

**What stands, and why the parameters are what they are.**

| Parameter | Value | Why |
|---|---|---|
| Common flags | `--no-require-speedup --min-runtime-share 0.01` | speed cannot be measured at the agent's size (kernels run 0.06–15 ms; the check would judge noise) and is judged by the harness at the verification size instead; the 1 % floor gives up ≤ 1.7 % of runtime (T0.5) and removes 42 % of the loops the model would otherwise be spent on |
| Edit mode | `direct` | the model edits a private copy with its own tools; no diff-format failures (E2 measures evidence, not diff arithmetic) |
| Budget | 3 attempts per region (+2 uncharged build fixes) | every acceptance in the pilots came on attempt 2; E2 Part B tests 1 vs 3; D3 (share-weighted) is calibrated separately and would replace it only as a default |
| Models | Haiku default, Sonnet in E2 (and E11) | the author's requirement: a stronger model against the default, to see what evidence is worth to each; Qwen3-Coder proposed as a third (D5) |
| Repeats | ×5 on the core ten for headline comparisons, ×3 elsewhere, ×1 for the model-free arm | a model's run is stochastic; the DiscoPoP arm is deterministic given the one profile per run (T0.2) |
| Profile | one per benchmark per run, archived | DiscoPoP's reporting varies between profiles of the same program (T0.2) and between explorer runs on one profile (T0.7) |
| Correctness oracle | exact dump + digest at the verification size, on the shipped and a perturbed input, repeated at a fixed thread count, relative tolerance 1e-9 | a shipped input can be a fixed point of the kernel (seidel-2d); a race shows as run-to-run difference; a correct reduction moves the last digits |
| Speed | best kernel speedup at 1–24 threads ≥ 1.1× = FASTER; kernels T0.1 cannot time are judged on correctness only | the harness times the computation, not the process; 1.1 is above the measured noise of a shared host (T0.4 pending) |
| Benchmarks | 27 PolyBench + NPB is/mg/lu + md + Rodinia nw/pathfinder/hotspot; core ten stratified into A (DiscoPoP-ready), B (restructurable), C (order matters) | groups fixed before any run; applications from two further suites so the claim is not PolyBench-only |

**Changed now (no pre-registered hypothesis or arm touched).**

1. **Packaging (D6):** benchmarks are used in their original file layout — PolyBench as
   `<kernel>.c` + `<kernel>.h` + `polybench.h/.c` + one harness header; NPB as `<B>/<b>.cpp`
   + `common/` + `pb_harness.{hpp,cpp}`; Rodinia and md were one file to begin with. T0.8
   shows DiscoPoP sees the same program. T0.1, T0.2, T0.5 and T0.6 are re-run on the server
   for the switched benchmarks; the merged packages stay under `prepared_single/` for
   comparison only.
2. **E2 Part C's sections** are now `deps`, `blockers`, `accesses`, `loop_nest`,
   `inner_patterns` (leave-one-out). `classification` is dropped: it renders only for a
   region that already has a DiscoPoP pattern, which is never a region the model is asked
   about, so ablating it measures nothing.
3. **E8 reads out** "candidates seen at depth 1 and 2" beside "parallelised at depth 1 and
   2", so "nothing to do" (the privtemp run: the function had no sequential time left) is
   distinguished from "did nothing".
4. **E1's verification threads** are `1,2,4,8,12,24` on the core ten, matching H4's "1–24".
5. **T0.3 (can the oracle see a wrong program?)** is built from candidates already in hand —
   every attempt of the end-to-end runs and the pilots is saved with its diff and gate
   verdict — replayed through the harness verification. No model calls.
6. **`main` (D4):** excluded in every PolyBench package; kept in `md` and `pathfinder`,
   where T0.6 found DiscoPoP's only loop patterns inside `main`; excluded elsewhere.

**For the author to decide (each changes a pre-registered item).** **Decided by the author
on 2026-09-18 (18:30): A, B, C and D as proposed** — recorded as D8 (E10 first, its winner
becomes E1's default), D9 (the E1 model follows the pilot: Haiku if ≥ 2 FASTER in group B,
else Sonnet), D10 (`--budget 3` fixed, D3 becomes an efficiency study), D11 (H6 unchanged,
T0.9 reported as evidence in hand). Order of work from here: finish the instruments
(chain + T0.3 + T0.4) → pilot (core ten × `full` × 1, Haiku) → E10 → E1 → E11 → E2 → …

* **A. Run E10 before E1.** The end-to-end runs showed what "speed not judged" invites: an
  O(n²) recomputation and an all-work-in-the-last-repetition trick both passed the gate. The
  harness scores them `parallel-not-faster`, so no result is wrong — but a kept useless
  rewrite also *covers its region*, and can block a useful one. E10 (≈ 30 trials, 5 timeable
  kernels) asks whether the speed check at the kernel's timing size (`speed_gate_large`)
  removes such changes without lowering the delivered speedup. If it does, that
  configuration should be E1's `full`, and the decision has to be taken *before* E1 runs
  (recorded as D8), not after. Cost: E10 first, ≈ 3 h.
* **B. The E1 model.** Haiku is cheap and pre-registered; the Sonnet runs of 18 Sep needed two
  attempts on easy calibration programs. If the pilot on the core ten yields no FASTER
  outcome with Haiku, H1 cannot be tested with it. Proposal: the pilot decides — Haiku if it
  produces at least two FASTER outcomes in group B, otherwise Sonnet for E1 (E2 keeps both).
* **C. Budget policy.** Keep `--budget 3` fixed for the campaign and treat D3 as an
  efficiency study (calls saved per FASTER) rather than a default: a share-weighted budget
  entangles the ranking question (E9) with the evidence and feedback questions (E2). The
  mechanism stays (Fix 62); the calibration is dropped from the critical path.
* **D. H6's second half.** H6 predicts that fast refresh "saves time without changing
  decisions". T0.9 already shows decisions differ in the DiscoPoP-decides row on synthetic
  chains (8 of 18). The hypothesis stays as registered; the thesis reports T0.9 as evidence
  in hand before E3, and E3 decides it on real kernels.

**Threats the review adds to §8 of the plan.** (i) Every finding of 17–18 Sep would have
confounded a specific arm (§5g table) — the fixes precede the first run, which is the
answer. (ii) The gate cannot tell useful from useless parallel code without the speed check
(decision A). (iii) A profile taken unit by unit is unsafe outside `main`'s unit (D6) — a
threat for anyone reproducing this with DiscoPoP's documented workflow.

### 5j. Two guarantees for the campaign: nothing is corrupted between trials, and nothing measured is lost (2026-09-18)

The author asked for both before the first server run: "make sure that the benchmarks are
not corrupted after every experiment so the following experiment does not get corrupted
code, and make sure that the results are recorded and stored for the thesis writing with
the data for graphs and findings and everything."

**Integrity.** The runner already worked on copies (§3): a run copies the package into
`profiles/<bench>/` when it profiles it, and every trial copies from there into its own
fresh `work/`. What was missing was proof. The runner now carries `check_package`
(`cli.py`), which compares three digests and stops the run on any difference:

| What | Against | Recorded by |
|---|---|---|
| the prepared package (`agent/prepared/<suite>/<kernel>/`) | `output_sha256` in its `meta.json` — the packager's digest of the sources it generated (`prepare_polybench.py`, `prepare_apps.py`, and from v4 `prepare_calib.py`; one file's bytes, or a project's files concatenated in sorted order) | the packager |
| the run's archived sources (`profiles/<bench>/`) | the prepared package | the profiler step |
| the run's archived DiscoPoP profile tree (`profiles/<bench>/.discopop/`, every file) | `profile_sha256` in `profile.json`, taken the moment the profile finished | the profiler step |

The check runs **at run start** (package), **before every trial** (all three) and **after
every trial** (all three), and both results are stored in the trial's record
(`package_integrity.before/after`). A difference raises `PackageCorrupted`: the run's
status becomes `aborted_package_corrupted`, the process exits with status 2 so an unattended
sweep stops as well, and the message names what changed and what to do (regenerate the
package; or delete the run's `profiles/<bench>/` to re-profile). The trial that ran last
keeps its record — it ran on a copy proven intact beforehand — and no later trial starts.
A package with no digest is refused nothing but also proves nothing, which is why the
calibration packager now writes one too (45 of 45 packages carry and match their digest).

Verified by `agent/tools/test_integrity.py` (no model, no DiscoPoP: the profiler and the
agent are stubs, the run loop is the real one), 30 checks in both layouts: an intact run
records both checks with every trial and finishes; a trial that modifies the archived
source, or the archived profile, keeps its record and the run stops before the next trial
with exit status 2; a modified package stops the run before anything is taken from it and
no profile is taken. Cost: three sha256 passes over ≤ 10 MB per trial, well under a second.

What this does **not** cover, stated so it is not assumed: the benchmark *originals* under
`benchmarks/` (the packagers' inputs) are digested in `meta.json` as `inputs_sha256` but
not re-checked at run time — a regenerated package is compared against them by the
packager; and a trial's own `work/` copy may of course be modified by the agent — that is
the experiment.

**Results.** `agent/results/` is now **tracked in git** (until now `agent/runs/` was ignored
and "archived separately" meant by hand). `agent/benchmark archive RUN_ID… | --all` copies a
run's results there — every trial record, agent log, LLM usage, diff, candidate patch and
accepted patch, the sources every trial started from, DiscoPoP's `profile.json` and logs,
`manifest.json`, `results.json`, the tables, `figures/trials.csv` (one row per trial),
`gate_failures.csv` and the figures — dropping only the DiscoPoP profile trees (MBs each,
regenerable, digested in `profile.json`), the `work/` copies and binaries. Every archive
carries `ARCHIVE.json` with a sha256 per file, the run's host, status, git heads and outcome
counts, and `agent/results/INDEX.md` is regenerated as a table of every archived run.
`server.sh fetch` archives what it fetches, so the one manual step after an experiment is
`git commit agent/results`. All eighteen runs on the Mac to date are archived (3.5 MB in
total; a trial run is 0.1–0.5 MB). `agent/results/README.md` maps thesis material to
files. Standing rule 6 in the RUNBOOK: a number that is not in `agent/results/` does not
exist.

### 5k. Benchmark suitability audit — the benchmarks could not test the central claim (2026-09-19)

**What was found.** The author asked what "FASTER" means and whether any benchmark actually
challenges the model to restructure. Answering from the data instead of from the plan:

* `FASTER` = the final program is verified correct and ≥ 1.1× faster than the ORIGINAL
  SEQUENTIAL program (serial `-O2` against `-O2 -fopenmp` at 6/12 threads, same timed
  region). It says nothing about DiscoPoP; "DiscoPoP alone" is a separate ARM
  (`discopop_gate`), measured against the same sequential original.
* Of the 25 `FASTER` trials in `pilot4` and E10 so far, **21 changed nothing but pragmas**
  (3 of them plus comments); the only kernel ever restructured is `floyd-warshall` (4 FASTER,
  1 BROKEN).
* In the pilot's profiles DiscoPoP reports **every loop of 2mm, jacobi-2d, floyd-warshall,
  seidel-2d and trisolv as an applicable Do-All** — including the Gauss–Seidel loops, the
  time-step loop and the forward substitution, which are sequential. It does not fail to
  suggest; it over-suggests, and the gate filters (T0.2 had shown the blockers appear in only
  some profiles).
* DiscoPoP + gate ALONE, no model (`dp_alone_look_mac`, 20 of 31 so far): **17 of 20
  PolyBench kernels are parallelized**; only `atax`, `bicg` and `floyd-warshall` end
  `no-change`. PolyBench was written for polyhedral compilers: its kernels are parallel as
  written. The hypothesis "group B needs restructuring" was wrong for `jacobi-2d-imper`
  (it already keeps two arrays).

So claim C1 — *restructuring parallelizes what DiscoPoP alone cannot* — could not have been
tested on the planned core set: on 17 of 20 kernels there is nothing DiscoPoP alone cannot
do, E2 (evidence) would have sat at the ceiling (one call, success, with or without
evidence), and E3/E4/E8 exercise code paths that only run after a REWRITE, which almost
never happened. Found before E1, E2, E3, E4 and E8 ran; the pilots and E10 stay valid for
what they measure (cost per trial, the speed check).

**D26 — the scope rule: a benchmark that DiscoPoP cannot PROFILE is out of the set; a benchmark
DiscoPoP profiles but finds nothing in STAYS** (the author, 2026-09-20: *"our experiments and the
thesis is about the agent added upon DiscoPoP, not about DiscoPoP and whatever its limitation is.
If a benchmark is not working well for DiscoPoP, or breaks DiscoPoP, or hits a limitation in
DiscoPoP, we should avoid it"*).

The object of study is the DELTA the agent adds. Where DiscoPoP cannot produce a usable profile
the agent has no evidence to work from AND the DiscoPoP-alone baseline has no value, so the
comparison the thesis leads with (D19) is undefined; time spent there measures DiscoPoP's
engineering, not this contribution.

**The distinction this rule turns on, which must not be lost in the writing:**

| | what it means | what we do |
|---|---|---|
| DiscoPoP cannot RUN | crash, timeout, absurd cost — no profile exists | **exclude**, measure once, report the cost |
| DiscoPoP runs and finds NOTHING | a profile exists; it reports no applicable pattern | **keep — this is class R, the whole point** |

Excluding the second would delete the central claim, so the two are never conflated.

**Excluded under this rule, each measured once and reported** (`docs/DISCOPOP_BUG_REPORTS.md`):
NPB `lu` (instrumentation > 2 h, L1) · Rodinia `nw` (explorer ≈ 25 h, L2) · NPB `mg` (task
detection unfinished after 11 h, L3) · PolyBench `adi` (40 min instrument, L4) · **The TSVC stall is RANDOM, not a property of a loop** — measured the same night and corrected
here: `s3112`, which had run > 80 min, explored in **5.8 s** on the next draw, while `s322` and
`s331`, which had taken 4 s, stalled in their turn (both at the same point, a progress bar at
`0/11`). So the exclusion list does NOT name TSVC loops: the remedy is the 20-minute phase
timeout, after which the benchmark is recorded `PROFILE_ERROR` for THAT DRAW and its class is
decided from the draws that succeeded. Cost when it strikes: 20 min, about two loops of 25 per
draw. This is B4's nondeterminism in the explorer, now with a cheap reproducer (L5).
Four of 61 candidates are excluded outright. The thesis states this as scope and as a threat to validity: *the agent is
evaluated where DiscoPoP is usable*, with the six named and costed — not silently dropped.

**D18 — benchmark classes are MEASURED, and every experiment names the class it needs.**

| class | definition (measured, not assumed) | role |
|---|---|---|
| **R** needs restructuring | DiscoPoP + gate alone ends `no-change` (in the majority of 3 profiles) **and** an expert reference solution exists that the harness verifies correct | carries C1, E2, E3, E4, E8 |
| **A** parallel as written | DiscoPoP + gate alone reaches a verified parallel program | control: the agent must do no harm, and filter DiscoPoP's false positives |
| **D** must decline | the dependence is a genuine recurrence; the reference is the sequential program | safety: no BROKEN, no slowdown kept |
| **M** multi-region application | ≥ 10 candidate regions with unequal runtime shares | E9 (ranking), E11, cost |

**Pre-flight rule (added to the RUNBOOK checklist).** No experiment is launched until a
no-model suitability check shows its benchmarks CAN discriminate between its arms: (1) class
measured (`discopop_gate`, 3 profiles); (2) for R, the reference solution verified by the
harness and its speedup at the verification size known (T0.10) — a loop whose own expert
solution is not ≥ 1.1× is reported for correctness only; (3) sizes from T0.1 (serial kernel
≥ 1 s); (4) one smoke trial per arm on two benchmarks, with the log READ to confirm the arm's
code path ran (a rewrite happened, a refresh ran, depth 1 triggered, …).

**The new R/A/D set: TSVC-2** (`agent/tools/prepare_tsvc.py`, `benchmarks/TSVC_2`, University
of Illinois licence). TSVC is the recognised suite of loops classified by the TRANSFORMATION
a tool must apply (statement reordering, loop distribution, node splitting, scalar
expansion, index-set splitting, peeling, induction variables, search loops, packing, plus
genuine recurrences); LLM-Vectorizer (2024) and VecTrans (2025) evaluate LLM loop
restructuring on it. **The loop body is verbatim**; the packaging is this harness's — `double`
data (TSVC's `float` cannot meet the 1e-9 oracle once a reduction is reordered), heap arrays
and dataset sizes, O(1) periodic initial values (TSVC's 1/(i+1) values fall below the oracle's
tolerance at large N and would blind it), the perturbed input, digest/dump, the timed region,
and DEPENDENT repetitions (`pb_mix` changes a few input elements between repetitions so none
can be skipped — the hole of 18 Sep). 25 loops: 18 R (s211 s212 s1213 · s241 s243 s244 · s252
s254 s255 · s281 s291 s292 s293 · s121 s112 s127 · s331 s341), 4 D (s321 s322 s323 s3112),
3 A (s000 vpvtv s313). Every R and A loop has an **expert reference solution**, kept OUTSIDE
the package (`agent/reference_solutions/tsvc/`, never staged into a trial) — 25 of 25 packages
validate: finite, deterministic, sensitive to the perturbed input, and every reference
computes the original's values on both inputs at 4 threads (max rel. error ≤ 1e-9).

*First measurements.* DiscoPoP + gate alone on TSVC (`dp_alone_tsvc_mac`, 7 of 25 so far):
the control parallelized, **s112, s121, s1213, s127 `no-change`** — DiscoPoP alone fails on
the R loops, as intended. Expert ceiling on the server (T0.10, `tsvc_ceiling.py`, node 1,
host load 550–1400): all references correct; at 64M elements **1.4–4.3× at 12 threads**
(s127 4.3×, s212 3.6×, s1213 3.1×, s211 2.5×, s241 2.6×; the two that need a full copy of an
array, s112 1.4× and s121 1.5×). These loops do little arithmetic per element, so they are
memory-bound: on the Mac the same references are NOT faster (s211 0.63×, s252 1.08×) — speed
is judged on the server only, and the headline outcome for class R is **"verified-correct
parallelization reached"**, with speedup reported as a fraction of the reference's. Serial
kernels ran 0.16–0.46 s, below the 1 s a timing needs → generator v2: 48 repetitions for
additive loops, 8 for multiplicative ones and recurrences, largest size 192M elements.
PolyBench contributes `atax`, `bicg`, `floyd-warshall` to class R (compute-bound, larger
speedups); NPB-C (E11) contributes application-scale cases.

**Which experiment uses which benchmarks, and why** (supersedes the "core ten" of the plan;
`kernel_groups.json` is rewritten once the classes are measured on the server):

| Experiment | Benchmarks | Why these | Arms can differ because… |
|---|---|---|---|
| **E1** agent vs DiscoPoP alone (C1) | **classes as MEASURED by T0.11**, not as guessed here: class R ×5 = 26 benchmarks (TSVC s112, s121, s1213, s127, s211, s212, s241, s243, s244, s252, s254, s255, s281, s291, s292, s293, s331, s341; PolyBench bicg, doitgen, floyd-warshall, seidel-2d, trisolv; `md`, `is`, `hotspot`) = 130 agent trials; class A ×1 = 25 (PolyBench 2mm, 3mm, atax, correlation, covariance, dynprog, fdtd-2d, fdtd-apml, gemm, gemver, gesummv, gramschmidt, jacobi-1d-imper, jacobi-2d-imper, lu, ludcmp, mvt, reg_detect, symm, syr2k, syrk; `pathfinder`; TSVC s000, s313, vpvtv — `adi` excluded by D25) = 25; class D ×3 = 4 (TSVC s3112, s321, s322, s323) = 12. **167 agent trials**, each paired with a `discopop_gate` trial (D19) that costs no model call | the claim is about R; A shows "no harm"; D shows "no unsafe acceptance" | on R, DiscoPoP alone = `no-change` by measurement (every one ≈ 1.00×), and T0.10 proved a verified solution exists (every reference ≥ 1.87×). **Three corrections T0.11 forced on this row:** `atax` is class **A**, not R — DiscoPoP does parallelize it, at 0.30× (three times SLOWER than sequential); `hotspot` and `md` are class **R**, not A. And five class-A benchmarks have DiscoPoP alone below 1.00× (ludcmp 0.155×, lu 0.212×, reg_detect 0.248×, atax 0.301×, dynprog 0.98×), so on those "no harm" is really a repair opportunity — visible only against DiscoPoP alone, never against the sequential original |
| bare-LLM baseline (new arm of E1) | class R | what the pipeline adds over asking the model | no evidence, no gate: wrong programs are expected and counted |
| **E2** evidence (none / hotspot-only / compiler remarks / DiscoPoP; Parts C, D) | class R only | on A the model succeeds in one call with or without evidence (ceiling: pilot4, E10) | the dependence that blocks the loop is exactly what the evidence names |
| **E3** pragma author × refresh, **E4** add vs delete | class R only | both concern what happens AFTER a rewrite; without a rewrite the refresh path never runs | every R success involves a rewrite by construction |
| **E7** gate as a classifier | every candidate of every run (T0.3 corpus grows) + DataRaceBench (external ground truth for races) | needs right AND wrong candidates; R produces wrong ones (floyd's stack array) | — |
| **E8** depth | R loops where one rewrite leaves or exposes another task: `atax`/`bicg` (fission, then interchange), s221/s222-type partial recurrences (to add), NPB-C kernels | depth only matters if a first rewrite creates a new region | **at risk** — a smoke must show depth 1 ever triggers; dropped otherwise, and said so |
| **E9** ranking | class M only: `md`, `hotspot`, `pathfinder`, NPB-C kernels | ranking cannot matter on a kernel with one hot loop | calls-to-first-success depends on the order only when there are many regions |
| **E10** speed check (running) | 2mm, jacobi-2d, floyd-warshall, lu, seidel-2d, hotspot | valid as run: `lu` and `hotspot` are where `full` keeps correct-but-slower changes; the others are controls | to supplement with grain-limited TSVC loops at small sizes |
| **E11** vs RepoOMP | RepoOMP's eight NPB-C inputs | identical programs, their released outputs | — |
| **E5** cost | size sweep on 2mm and NPB `is` | independent of class | — |
| **E6** application scale | LULESH 2.0, serial path only (threaded branches removed) | the one program with LLNL's expert before/after in the same source: ≈ 40 loops parallel as written + the force scatter→gather and min-with-index restructurings | DiscoPoP alone cannot parallelize the scatter; the expert version is the ceiling |

**Pre-flight for E1 — done 2026-09-20, all without a model.**

* **T0.1 for TSVC** (`results/T0_instruments/T0.01_sizes/runs/t0_1_tsvc`, server node 1): all 25 loops get a verification size
  (20 EXTRALARGE, 5 LARGE) and a timing size (22 LARGE). Merged into `kernel_sizes.json`, now 59
  entries. Needed before anything else: a benchmark with no timing size has the speed check
  switched off automatically, so without this TSVC would silently have run in a different
  configuration from PolyBench.
* **T0.10 re-measured at those sizes** (`results/T0_instruments/T0.10_expert_references/runs/t0_10_tsvc_ceiling_v2`, supersedes the v1 run):
  42 rows, all correct, expert references **1.87×–6.40×, median 4.10×** at 12 threads. **This
  removes a limitation of the suite.** At the v1 sizes three references did not reach 1.1× even
  written by hand, because these loops are memory-bound at small sizes, and the plan therefore
  said class R would be reported on correctness with speed only as a fraction. At the v2 sizes
  every loop clears 1.87× (`s331` 2.35→6.40×, `s255` 1.23→2.57×), so **both** can be reported:
  whether a verified-correct parallelization was reached, and how much of the expert's speedup it
  captured.
* **`polybench/adi` leaves the model-driven set (D25, author's call).** Its instrumenting compile
  takes **2,387 s — 40 minutes — per profile**, which is 41 of the 135 minutes a T0.11 draw needs;
  across three draws it would have spent two hours on one kernel. Draw A completed it (`FASTER`,
  19 Do-Alls), and that single measurement is kept as the evidence of the cost, but `adi` is
  excluded from draws B and C, so it has one draw where every other benchmark has three and its
  class is left undetermined. It joins NPB `lu` (instrumentation > 2 h), Rodinia `nw` (explorer
  ≈ 25 h) and NPB `mg` (task detection unfinished after 11 h) as a DiscoPoP cost limitation the
  thesis reports rather than works around; `docs/DISCOPOP_BUG_REPORTS.md` L4.
* **The explorer explodes on two TSVC loops (L5) — found by T0.11 itself.** Every loop of the
  suite explores in **4 s** except two: `s291` spent **5,403 s** in one attempt and `s3112` was
  still running after 80 minutes. Instrumentation and the profiled run take 0.2 s each, so it is
  the explorer alone, and `s291`'s profile carries **117 task patterns** for a 30-line loop — the
  signature of L3 (NPB `mg`) at a scale small enough to be a useful reproducer. Two consequences.
  (i) The harness no longer retries a TIMED-OUT explorer: the 20 retries exist for the random
  `IndexError`, which fails in the first seconds, whereas an explorer still running at the limit
  will not finish and retrying spends the limit again — 20 × 90 min = **30 hours for one
  benchmark**, which is what had quietly stalled this run to 48 trials in 6 hours. (ii) T0.11
  runs with `--timeout 1200`, so a loop DiscoPoP cannot explore in 20 minutes is recorded as a
  profile error and reported, exactly as `adi`, `nw`, `lu` and `mg` are.
* **T0.11, the class measurement** (running, server node 0): `discopop_capability` over 55 benchmarks —
  27 PolyBench (the three weak oracles out), 25 TSVC, `md`, `is`, `pathfinder`, `hotspot`; NPB
  `lu`/`mg` and `nw` excluded as L1/L2/L3. Run as **three separate runs**, not three repeats: a
  run profiles each benchmark once, and DiscoPoP alone depends on the draw (`lu` 0.21× on the
  server, 3.4× on the Mac), so three runs give three independent draws and the class is the
  majority of them.

**Instruments owed by this change:** T0.1 for `tsvc/*`; T0.10 (expert ceiling, all loops,
final sizes, server); T0.11 (class measurement: `discopop_gate` × 3 profiles on every
benchmark, server); the feature suite and the scaffold check on a TSVC package; then the
pre-flight smoke for E1. Nothing model-driven runs on the old core set any more.

**D19 — THE MAIN COMPARISON IS DiscoPoP ALONE vs DiscoPoP + AGENT (rule set by the author,
2026-09-19).** "The main comparison is between DiscoPoP alone and DiscoPoP with the agent, not
between DiscoPoP with the agent and the original code"; the sequential original stays as the
REFERENCE both are measured against. Consequences, all implemented the same day:

* Every model-driven experiment carries the `discopop_gate` arm (DiscoPoP's own suggestions,
  each validated by the same gate, no model, the same fixed DiscoPoP, same profile, sizes and
  threads) on the SAME benchmarks in the SAME run. It costs no model calls.
* The headline outcome of an agent trial is its **verdict against DiscoPoP alone**, not
  `FASTER`: **gained** (DiscoPoP alone reaches no verified parallel program, the agent does and
  it is ≥ 1.1× faster) · gained-not-faster · **better** (both parallel and correct, the agent's
  program ≥ 1.1× faster than DiscoPoP alone's) · equal · **worse** · **lost** (DiscoPoP alone
  parallel, the agent not) · neither · **unsafe** (BROKEN) · invalid. A program left unchanged
  IS the sequential original (1.00×). `figures.py: vs_discopop_alone()` → `vs_discopop_alone.csv`
  / `.md`, figure `fig_vs_discopop_alone` (one dumbbell per benchmark: DiscoPoP alone → agent,
  on the speedup-over-sequential axis as reference); every run's `overview.md` now OPENS with
  this table, and says **MISSING** in bold when a run has agent arms but no `discopop_gate`
  trials. Speed ratios are withheld (verdict `not-comparable`) when the two programs were timed
  on different hosts, sizes or thread sets — outcomes are still paired. Trials now record `host`.
* By class: on **R** the expected verdict is *gained* (this is C1); on **A** it is
  *better / equal / worse* — what the agent's choice of loop level, clauses and grain adds over
  DiscoPoP's own pragmas, NOT restructuring, and reported separately; on **D** it is *neither*,
  with zero *unsafe*.
* What "DiscoPoP alone" means is stated once: DiscoPoP's suggestions **through the gate**. Raw
  DiscoPoP (every applicable suggestion applied unvalidated — what the tool's user gets) is a
  second, weaker baseline worth one table (`verify-source --label discopop_raw`), because
  DiscoPoP over-suggests: on `atax` two of its three Do-Alls race, on `bicg` both do.

**Fix 84 — the DiscoPoP-alone baseline was being under-measured (agent bug, found by this
audit).** Looking at WHY `atax` ended `no-change`: DiscoPoP's own patch for the valid Do-All
(line 74) was correct, but the agent's Phase B re-anchors a pragma by its loop-header text and
chose, among identical headers, the one nearest to the hunk's FIRST line (three lines above
the pragma) — so the pragma went onto the sibling loop two lines up (a recurrence), raced, and
was dropped. Measured over every stored profile: **29 of 539 DiscoPoP pragmas misplaced, in 12
of 26 PolyBench kernels** (2mm, atax, covariance, fdtd-2d, gemm, gemver, gramschmidt, lu, mvt,
reg_detect, syr2k, syrk; none in TSVC, NPB `is`, Rodinia). Phase B is the only pragma source of
the DiscoPoP-alone arm and a secondary one in the agent arms, so the error favoured the agent
in exactly the comparison D19 makes the headline. Fixed at the root (context match, then
distance from the pragma line; feature check `pragma-sibling-loops` fails before, passes
after; agent `FIXES.md` Fix 84). **Every `discopop_gate` number measured before it on those 12
kernels is void**; of the agent runs, `polybench/lu` in E10 is the one kernel touched (its
Phase B only) — to be re-run after E10 ends.

**Read-out of the two no-model looks (Mac, 4 threads, agent `6eefbdf0` = before Fix 84).**
`dp_alone_tsvc_mac`, 25/25: DiscoPoP + gate alone ends **`no-change` on all 18 R loops and all
4 D loops, and parallelizes all 3 controls** — the classes hold by measurement, and Fix 84
changes none of them (no misplaced pragma in TSVC). DiscoPoP nevertheless CLAIMED an applicable
Do-All inside the kernel function of 15 of the 18 R loops and of 2 of the 4 true recurrences
(s3112, s323) — 22 suggestions, **21 rejected by TSan and 1 by the output check, none
correct** (where checked, e.g. s3112, the claim is on the repetition loop, which is sequential
by construction). DiscoPoP's false positives are the rule on this suite, which is what the gate
is for, and a number for the thesis (instrument T0.12: DiscoPoP's precision per suite, from
`candidates.jsonl`, no model). `dp_alone_look_mac`, 26 PolyBench kernels so far:
6 FASTER, 15 parallel-not-faster (several far SLOWER than sequential: reg_detect 0.03×, ludcmp
0.04×, symm 0.19×, lu 0.26× — inner-loop pragmas), 5 `no-change` (atax, bicg, floyd-warshall,
seidel-2d, trisolv). After Fix 84 `atax` moves to class A (`dp_alone_fix84_mac`: DiscoPoP's
inner Do-All applied and verified) — it stays interesting for *better* (the expert solution
distributes the loop and parallelizes the OUTER loops). `bicg` stays R for a real reason: both
DiscoPoP suggestions race (the outer one lacks `private(j)` and writes every `s[j]`; the inner
one is a recurrence on `q[i]`), and the solution is fission + interchange. The 12 kernels above
are re-measured, and classes are fixed only from the server run (T0.11, 3 profiles).

**What Fix 84 did to the baseline, measured** (`dp_alone_fix84_poly_mac`, the same look repeated
on the 11 PolyBench kernels the fix touches plus `bicg` and `floyd-warshall`; Mac, 4 threads, no
model — a look: the laptop was loaded, so read the direction, not the digits):

| kernel | DiscoPoP alone BEFORE Fix 84 | AFTER |
|---|---|---|
| lu | parallel-not-faster 0.26× | **FASTER 3.39×** |
| syr2k | parallel-not-faster 0.75× | **FASTER 8.49×** |
| gemm | parallel-not-faster 1.08× | **FASTER 3.26×** |
| syrk | parallel-not-faster 0.56× | **FASTER 2.96×** |
| 2mm | FASTER 1.49× | FASTER 3.15× |
| gramschmidt | FASTER 1.24× | FASTER 2.75× |
| covariance | FASTER 2.18× | FASTER 2.15× |
| fdtd-2d | parallel-not-faster 0.44× | parallel-not-faster 1.07× |
| gemver, mvt, reg_detect | parallel-not-faster 0.29× / 0.33× / 0.03× | parallel, too short to time on the Mac (ratios 2.67 / 2.47 / 1.28) |
| atax | no-change | parallel (too short to time) |
| **bicg, floyd-warshall** | no-change | **no-change — class R for a real reason** |

Before the fix DiscoPoP alone looked as if it made half of PolyBench SLOWER; that was our
misplaced pragma (on `lu`, the pragma of the update nest sat on the row-scaling loop). With the
pragma where DiscoPoP put it, DiscoPoP alone is a strong baseline on PolyBench — which is the
audit's point made sharper: on this suite the agent can at best be *equal* or *better*, and C1 has
to be shown on class R. Consequence for results already in hand: every comparison of an agent
result with a `discopop_gate` number from before 19 Sep is void (pilot4's table in §7 compared
against nothing of the kind; E10 has no `discopop_gate` arm yet). The applications in the first
look (`dp_alone_look_mac`, before the fix, none of them touched by it): `md`, NPB `is` and
`pathfinder` end `no-change` — candidates for class R/M, to be confirmed by T0.11 — and `hotspot`
is parallelized by DiscoPoP alone (2.0×).

**LULESH (author's question, 19 Sep: "LULESH had examples before and after
parallelization").** It does, and that makes it the application-scale class-R case: LULESH 2.0
carries BOTH versions of its two force kernels side by side — `IntegrateStressForElems` and
`CalcFBHourglassForceForElems` scatter element forces into shared nodes (`fx[gnode] += …`, a
true loop-carried dependence) on the serial path, and under `if (numthreads > 1)` LLNL's
experts restructured them: per-element force arrays in a parallel loop, then a parallel gather
over `nodeElemCornerList`. The time-constraint kernels do the same for a min-with-index
(per-thread arrays). The remaining ≈ 40 of its 44 pragmas annotate loops that are parallel as
written — a realistic mix of A and R in one 6,000-line program. Packaging rule §1a applies:
the input is the SERIAL path only (`benchmarks/LULESH/LULESH_SEQ` still contains the threaded
branches and their comments — they are removed, or the model reads the answer); the upstream
OpenMP version is the expert ceiling (`verify-source --label expert_openmp`). E6 therefore
becomes the main comparison at application scale — sequential (reference) · DiscoPoP alone ·
DiscoPoP + agent · LLNL's expert OpenMP — instead of a cost measurement only. **Done the same
day:** `agent/tools/lulesh_serial_path.py` → `benchmarks/LULESH/LULESH_SERIAL_PATH` (6,632 → 6,389
lines): `unifdef` removes the preprocessor-dead OpenMP code, every `if (numthreads > 1)` is folded
to its serial branch, `SetupThreadSupportStructures`, the corner-list members and accessors, the
per-element force arrays and the unused `lulesh_tuple.h` go; **validated — the 12 deterministic
output lines at `-s 8 -i 20` and `-s 12 -i 30` are identical to the original's, and no mention of
the threaded design is left** (`SERIAL_PATH.json` lists every removal). Kept on purpose and
recorded: the two time-constraint kernels are written, also serially, as "one minimum per thread,
then merge" with one thread — that IS LLNL's serial computation, so in those two kernels the
restructuring is present and only pragmas are missing (class A, not R). Still owed: the harness
recipe (dataset guards, digest, perturbed input, timed region) and the server profile. Known costs: one
profile is 23 s instrument at 28 GB (server only); results compare within the measured noise
floor (the scatter→gather reorders additions, 1e-16).

### 5l. Audit of the agent's DEFAULTS — a default is a decision, not a neutral act (2026-09-20)

**Why.** The author's standing rule is that every parameter of every experiment has a stated
reason. The plan's table "Every agent setting, accounted for" gives each field a role
(*studied* / *fixed with a reason* / *computed* / *plumbing*), but it had a hole: for a field
marked "studied in E3", nothing said what value the experiments running BEFORE E3 hold it at, or
why. E10 found the cost of that hole — see `llm_pragmas` below. From now on a field marked
*studied* must also state its **held value and the justification for it**, and any result that
depends on that value says so.

| default | justification today | verdict |
|---|---|---|
| `llm_pragmas = True` | **design argument only, never measured.** The model writes the pragma with the rewrite, so the rewrite is judged on its own merits (clause check, TSan, identical output from the parallel build, measured speed) instead of on whether re-profiling makes DiscoPoP rediscover a pattern | **weakest default in the agent.** E3 decides it; until then every result carries it as a stated condition. Bounded by Fix 85 (below) |
| `require_speedup = True` (agent) vs `--no-require-speedup` (every campaign arm, 15 Sep) | the campaign turned it off because at SMALL sizes kernels run in milliseconds and the check measured noise | **the campaign default is now wrong by measurement.** E10: the check ON at the kernel's timing size is the only arm with 0 unsafe and 0 lost; OFF keeps 5 slower programs and 1 BROKEN. D8 already moves E1 to `speed_gate_large`; the agent's own default (ON) was right all along, and what was wrong was the SIZE it was measured at |
| `budget = 3` | was an assumption (D10). **Now measured** over every archived run, Phase-A attempts by number: 1st 40 accepted of 127, 2nd 12 of 91, 3rd **6 of 82**, 4th 2 of 8 (4th/5th exist because build-error retries are refunded) | **D10 stands — the default stays 3 in every arm, and the share-weighted policy remains a separate efficiency study (D3); this audit changes the EVIDENCE, not the decision.** Report the curve: the 3rd attempt costs 82 calls for 6 acceptances (10 % of all acceptances, ~40 % of the calls). The earlier claim "no third attempt ever succeeded" is superseded. The 60 acceptances do not calibrate D3, because they come from the evaluation's own benchmarks and a calibration needs a held-out set |
| `min_measured_speedup = 1.1` | T0.4: serial timing CV ≈ 4 % on the loaded server, so 1.1× is the smallest ratio resolvable; identical to the harness's `FASTER` threshold, so agent and harness cannot disagree | justified |
| `fast_refresh = True` | feature check `fast-refresh-eq`: the carried-forward dependences agree with a full re-profile on the checked cases; a full re-profile still runs before Phase B and before a deeper level | justified; studied in E3's 2×2 |
| `hotspots = True` | T0.5: measured time saved ranks regions correctly where the static proxy does not (feature checks `impact`, `mixed-rank`, `hotspot-remap`) | justified; studied in E9 |
| `evidence = "full"` | the thesis's object of study | studied in E2 |
| `restructure_depth = 0` | held at 0 so every experiment before E8 measures one level only | studied in E8, held with a reason |
| `schedule_stress`, `numeric_tolerance`, `check_inputs` | T0.3: the perturbed input is the ONLY thing that catches 14 of 23 wrong programs; schedule stress catches 2 benign races TSan alone reports | justified; ablated offline in E7 |
| `build_retries = 2` | build errors are mechanical, the retries are refunded and counted as cost | justified |
| `explorer_timeout = 600` s | one explorer attempt's limit; a stalled draw is repeated (≤ 5). From data: over 166 profile draws the explorer needed a median of 3.5 s and at most 33 s (`hotspot`), and 7 % of draws never finished. ~18× the slowest legitimate run; identical in every arm and in the harness's own profile step | justified (2026-09-21) |
| `lambda_penalty = 1.0`, `min_workload = 0.0` | λ only orders regions where no measurement exists; `min_workload > 0` drops every function region (DiscoPoP reports their workload as 0) | justified |
| `stress_threads = 1,2,4`; `budget_policy = "fixed"`; `llm_recon = False`, `llm_deps = off` | width of a matrix that is itself a studied stage (E7); D3 pending calibration; E4's object of study, held off because `llm_deps` is the one channel where a model's claim EDITS the analysis | justified / studied |

**Fix 85 — pragma authorship inside a rewritten region (D21).** The collision the author asked
about ("how is this even possible?") is real and is NOT a failure of the deferral rule. On
`jacobi-2d` DiscoPoP claims the two stencil loops and the agent defers them to Phase B, exactly
as designed. But the *enclosing function* is a separate candidate, has no pattern of its own, and
goes to the model — which, with `llm_pragmas`, annotates those same loops from inside its rewrite
(`collapse(2)`). Phase B then reports "no applicable pattern for the final source", and
DiscoPoP's `parallel for private(j)` — twice as fast on this machine — is never measured.

*Measured frequency:* across every archived run, **22 trials** end with a deferred DiscoPoP
pattern and only LLM pragmas applied (`floyd-warshall`, `jacobi-2d`, `lu`). Displacement is not
uniformly bad: on `lu` the model's pragmas give 2.6–2.8× where DiscoPoP's own give **0.21×**; on
`jacobi-2d` they give 2.5× where DiscoPoP's give 5.9×. **So the fix must not pick a side — it
must measure both.**

1. The prompt names the loops inside the region that DiscoPoP has already claimed and says their
   pragmas belong to Phase B; the model restructures, and annotates only what it created.
2. Where a model pragma sits on a claimed loop anyway, Phase B builds DiscoPoP's pragma for that
   loop as an alternative, measures both, and keeps the faster (the loser is recorded).

With (2) the agent cannot end below DiscoPoP alone by displacing its pragmas, and the thesis gains
a directly measured answer to "who writes the better pragma, the model or the analysis tool?" on
every collision — data E3 would otherwise have to produce separately.

**Both parts BUILT, 2026-09-20** (agent `FIXES.md` Fix 85; `pragmas/arbitrate.py`, the step in
`phases/phase_a.py` before COMMIT, the prompt in `llm/render.py`). The winner, the reason and the
measured ratio are recorded per collision in `candidates.jsonl` as `pragma_arbitration`, so the
answer is in the data of every run from now on. Arbitration needs a measurement, so it runs where
the run measures (`--require-speedup`) — which, since the defaults change below, is every arm but
`full` and the historical ones. Feature check `pragma-arbitration` covers all five outcomes
(DiscoPoP faster → taken; inside the noise band → the model's stands; DiscoPoP's alternative fails
the gate → the model's stands, reason recorded; identical pragma → not a collision; loop left to
Phase B → not a collision), with no model and no compiler.

### The defaults, CHANGED (2026-09-20)

The audit above is not a document; it changed what the campaign runs.

| what | before | now | why |
|---|---|---|---|
| `arms.json` `common_flags` | `--no-require-speedup --min-runtime-share 0.01` | **`--require-speedup --min-runtime-share 0.01`** | E10: the check ON at the kernel's timing size is the only configuration with no unsafe acceptance and nothing below DiscoPoP alone; OFF kept 5 slower programs and 1 BROKEN. September's reason (at SMALL sizes the check measures noise) was about the SIZE, not the check |
| `arms.json` `common_timing_size` | — (per-arm only) | **`per_kernel`** | so every arm added later (E2's evidence arms, E3, E4, E8) inherits the size T0.1 measured, instead of silently inheriting the wrong one |
| arm `full` | the campaign default | **an experimental arm**, now carrying `--no-require-speedup` and `timing_size: agent` explicitly | its meaning and E10's trials are unchanged; it is simply no longer what a new arm inherits |
| arm `discopop_gate` | applied DiscoPoP's pragmas with no speed check | **inherits the same configuration as the agent arm** | the baseline must differ from the agent arm ONLY in the model. A baseline deliberately denied the speed check is a weakened one, and comparing against it would inflate our result — exactly what D19 forbids. **This makes our own numbers smaller**: on `lu`, DiscoPoP alone with the check would reject its own 0.21× pragma and end at 1.00×, so the agent's "better ×10" becomes "gained". `e10_dp_alone` used the old, weaker configuration and its `lu` row is labelled accordingly |
| `--budget 3` | assumed | unchanged, now **measured** (40/127, 12/91, 6/82, 2/8 by attempt) | D10 stands — the default stays 3, the share-weighted policy stays a separate efficiency study (D3). The audit changed the evidence, not the decision |
| `--llm-pragmas True` | design argument only | unchanged, now **bounded by Fix 85** | E3 decides the default; until then Fix 85 removes the harm (the agent can no longer end below DiscoPoP alone by displacing its pragmas) and makes E3 fair, since today's `--llm-pragmas` arm can silently displace what the `--no-llm-pragmas` arm would have used |

Consequence for E1: its two arms are `discopop_gate` and `speed_gate_large`, both with the speed
check at the kernel's timing size, differing only in whether a model is called.

**Checked against every other experiment — and it HAD broken four of them.** The author asked
whether the change could harm experiments that have not run. It could, and it did, in two ways
that a check now makes impossible to repeat.

1. **Four matrix experiments were confounded.** E3 (pragma author × refresh), E4's matrix cell,
   E8 (depth 0/1/2) and E9 (measured ranking vs static proxy) each pair a variant arm against
   `full`, which the change pinned to `--no-require-speedup`. Their variant arms inherit the new
   default, so each comparison would have measured its own variable **and** the speed check.
   *Fixed:* a new arm **`default`** (no flags of its own) is the baseline cell of every matrix
   experiment — the campaign default, whatever it currently is. `full` keeps the old behaviour
   and belongs to E5 and the historical E10 runs only. Identical in configuration to
   `speed_gate_large`; the names are kept apart because that one names what E10 varied.
2. **Eight kernels would have become unrunnable.** `_timing_size` exited when T0.1 found no size
   at which a kernel runs long enough — right while only E10 asked for a timing size, fatal once
   every arm does. It would have removed `atax`, **`bicg`**, `gemver`, `gesummv`, `jacobi-1d`,
   `mvt`, `reg_detect` and `trisolv` — and `bicg` is one of the few class-R benchmarks E1 needs.
   *Fixed:* on such a kernel the speed check is switched OFF and the fact recorded (per trial and
   in the manifest, `speed_check_off`), because there the check can only reject noise — which is
   precisely what E10 measured `speed_gate_small` doing. The harness's own verification still
   judges the kernel's speed afterwards.

**The guard.** `check_arm_compatibility()` compares the EFFECTIVE configuration of the arms in a
run — the speed check, the timing size, hotspots, the pragma mode, fast refresh, arbitration,
budget, evidence, depth — and every run now prints the settings its arms disagree on before
anything executes, with the line *"each line must be this experiment's variable; anything else is
a confound"*. On the repaired pairings it prints exactly one line each (E3: `llm-pragmas`,
`fast-refresh`; E8: `--restructure-depth`; E9: `hotspots`; E1: `--budget`); on the old broken
pairing it prints three, including `require-speedup` and `timing_size`.

### The agent's default changes again: the full re-profile replaces the fast refresh (2026-09-21, D27)

The author: *"fast refresh on should not be the default also"* — the same principle as D23, and
it lands the same way. `--fast-refresh` now defaults to **OFF**: a kept rewrite is followed by a
FULL re-profile (instrument, run, explore), so every later decision rests on dependences DiscoPoP
actually OBSERVED in the rewritten code. That is what the thesis argues for. The fast refresh is
an optimisation that trades accuracy for time — it carries observed dependences forward onto the
new instruction numbering and drops whatever it cannot translate with certainty, leaving the
rewritten region under static, over-approximate dependences. E3 is where that trade is measured;
it should not be what the agent does by default.

**A dependency that had to be found first: `--llm-recon` only takes effect inside the
fast-refresh branch** (`phase_a.py`: the reconstruction call sits under `if use_fast:`), because
reconstruction exists to repair what the fast refresh could not translate. So E4's arms — whose
entire subject is reconstruction — must carry `--fast-refresh` explicitly, or they would measure
nothing at all. They now do, and E4's baseline is `discopop_pragmas_fast` rather than `default`,
since every E4 cell needs the refresh on.

**The compatibility check earned its keep twice in five minutes.** Pinning the refresh where it
was previously implicit immediately confounded **E8** (its depth arms would have differed in the
refresh as well as the depth) and left **E4** paired against a baseline that does a full
re-profile. Both were caught before anything ran. It also exposed a hole in the check itself: it
never looked at `llm-recon` or `llm-deps`, so it reported "no differences" for E4 — an experiment
whose only variable is those two — and would have passed an E4 whose cells were identical. Now
checked: `llm-recon`, `llm-deps`, `apply-patches`, `numeric-tolerance`, `schedule-stress`.

**Every experiment's arms now differ in exactly their own variable**, verified: E1 budget · E3
`llm-pragmas` × `fast-refresh` · E4 `llm-recon` / `llm-deps` · E8 depth · E9 hotspots · E10
(archived) the speed check and its size.

**Cost.** A full re-profile after each kept rewrite costs one instrumented run — 4 s on a TSVC
loop, 30 s on `md`, 54 s on NPB `is` (T0.11) — and only where a rewrite was actually kept.

### The agent's default changes again: the model no longer writes the pragmas (2026-09-20, D23)

The author: *"i do not like having --llm-pragmas as the default, it should be added when needed
for a specific experiment."* Done — `--llm-pragmas` now defaults to **OFF**.

**Why this is the right default, not only the author's preference.** With it off, the division of
labour is the one the pipeline was designed around and the one the thesis argues for: the model
restructures, DiscoPoP re-discovers what the rewrite exposed, and Phase B annotates once at the
end. A rewrite is then kept only if the ANALYSIS finds parallelism in it — never on the model's
say-so. That is the claim the thesis makes (dependence-guided restructuring), and it should be
what the agent does unless an experiment deliberately asks the other question. With it on, the
rewrite is judged on its own merits instead (clause check, TSan, identical output from the
parallel build, measured speed): sound, but a different question, and the one E3 exists to ask.
E10 showed the cost of having it on by default — on `jacobi-2d` the model annotated loops DiscoPoP
had already claimed and its clauses were 2.4x slower, which is how the agent finished below
DiscoPoP alone. Fix 85 bounds that; it is not a reason to keep the default.

**What it changes in the arms.** `--llm-pragmas` is now pinned explicitly wherever an experiment
needs it, and nowhere else:

| arm | now | why |
|---|---|---|
| `full`, `speed_gate_large`, `speed_gate_small` | carry `--llm-pragmas` explicitly | E10 ran with it on; pinning keeps the archived runs reproducible and the names meaning what they meant |
| `llm_pragmas_full_reprofile`, new **`llm_pragmas_fast`** | carry `--llm-pragmas` | E3's two "the model writes them" cells. The (model, fast refresh) cell was the default until today and had no name of its own |
| **`default`** | `--no-llm-pragmas` by inheritance | E1's agent arm and the baseline cell of E3, E4, E8, E9 |
| `discopop_pragmas_fast` | unchanged, now identical to `default` | kept as an explicit name for the runs that used it |
| everything else (`full_b1`, `no_evidence*`, `full_depth*`, `full_no_hotspots`, `llm_recon`, E4's arms) | follows the new default | they are about evidence, depth, ranking or dependence handling, not about who writes pragmas |

**Consequences to state.** (i) D8 chose `speed_gate_large` as E1's agent arm from E10, where
`--llm-pragmas` was on; E1's agent arm is now `default`, which keeps D8's finding (the speed check
at the kernel's timing size) and drops the pragma authorship. The finding transfers: E10's
sharpest result — `speed_gate_small` losing 10 of 21 trials — was the check deleting *DiscoPoP's*
pragmas in Phase B, i.e. exactly the path `default` uses. (ii) Acceptance now rests on DiscoPoP
re-discovering a pattern in the rewritten code, which is the stricter test and the slower one; the
refresh (fast or full) happens either way, so this is not an extra re-profile. (iii) Fix 85's
arbitration only runs with `--llm-pragmas`, so by default it never fires; it protects E3's
`llm_pragmas_*` cells and E10's arms, and `--no-pragma-arbitration` turns it off for the E3 cell
that wants the two authorships unmixed. (iv) **E2's arms** (`full_b1`, `no_evidence_b1`,
`no_evidence`) now follow the new default rather than the configuration they were registered
with. That is deliberate — E2 should measure the agent as it ships — but it is a change to a
pre-registered experiment and is recorded here as one; it is open for the author to reverse
before E2 runs.

**Fix 85 against the other experiments.** It runs only with `--llm-pragmas`, `--require-speedup`
and an actual collision, so it cannot touch E4's `--no-llm-pragmas` arms or anything with the
check off. It DOES touch E3, whose question is who should write the pragma: the `--llm-pragmas`
cell can now fall back to DiscoPoP's pragma where the two collide. That is the right default
(it removes an artefact rather than adding one — those loops were DiscoPoP's in both cells), but
it blurs the contrast E3 measures, so **`--no-pragma-arbitration`** exists for E3 to run a cell
without it. Cost: one gate run and one timing pair per collision, only where a collision exists.

### 5p. What the agent has actually DONE so far: restructurings vs pragmas (2026-09-20)

The author, looking at the exhibits: *"I only see before and after adding pragmas but I don't see
code restructuring."* Correct — and the exhibits were part of the problem, reporting "lines added"
without saying what those lines were. Counted properly (comments stripped, block comments tracked
across lines, pragmas excluded), the archive holds **12 trials that changed code, on 4 programs,
out of 180**:

| program | what the model did | outcome |
|---|---|---|
| `floyd-warshall` | peels the k-th row and column out of the nest and guards the rest with `if (i != k && j != k)`, so the update no longer reads what it writes | FASTER, 9.6× at 12 threads |
| `floyd-warshall` | a variant that moves the row into a stack array | **BROKEN** — it overflows at the verification size |
| `trisolv` | scalar expansion: `x[i] = x[i] - A[i][j]*x[j]` becomes a `sum` accumulated under `reduction(+:sum)` and subtracted once | correct; the kernel is too short to time |
| `hotspot` | removes a recurrence carried by POINTERS — the original swaps `r`/`t` every iteration, the rewrite derives both from the iteration's parity | correct, but **12× slower**: the model kept the loop sequential with `#pragma omp ordered` |
| `2mm`, `lu`, `jacobi-2d` | nothing but pragmas, and comments explaining them | FASTER |

So the agent CAN restructure, and the four cases are genuinely different transformations —
index-set splitting with peeling, scalar expansion into a reduction, and removing a
pointer-carried recurrence. What is missing is not the capability but the OPPORTUNITY: on
PolyBench almost every loop is already parallel, so there is nothing to restructure. That is the
finding of §5k and the reason for the TSVC class-R suite; the restructuring gallery fills when E1
runs on benchmarks that need it.

**Were the four verified?** Yes, and by the harness rather than by the agent: each was rebuilt at
its VERIFICATION size (larger than the agent ever saw), run on the shipped input AND the perturbed
one, and its full value dump compared with the original's. All three that survive are
**byte-identical on both inputs** (`dump_exact` and `dump_exact_seeded` true, relative error 0.0)
and stable across repeats at a fixed thread count. The fourth, `floyd`'s stack array, produced
identical values where it ran and then **crashed at 6 threads at the verification size** — caught
by the harness, not by the agent, whose own gate had only seen the small size. That is the case
that justifies keeping the two checks at different sizes.

Read as semantics: `trisolv`'s rewrite is equivalence-preserving by inspection — the loop is
`for (j = 0; j <= i - 1; j++)`, so it never reads `x[i]` through `x[j]`, and accumulating into
`sum` and subtracting once is the same computation, with only the addition ORDER changed by the
reduction. The gate cannot do that reasoning; what it can do is falsify, and §7 `t0_3_oracle_mac`
measures how well: of 23 programs the gate rejected for a runtime reason the independent oracle
confirms 19 wrong, and of 19 it accepted the oracle agrees on all 19 — no false accept in that
corpus. The limits are equally measured and must be stated with the result: **not one** of the 14
wrong programs caught by output differed on the shipped input (all 14 only under the perturbed
one), and two genuinely racy programs produced identical output in 12 runs — only TSan saw them.
Output comparison alone would have passed both classes.

Two of the four are also the thesis's best negative examples, and both concern the gate:
`floyd`'s stack array is an unsafe acceptance that the speed check catches at size, and `hotspot`
is a correct restructuring defeated by the clause the model paired with it.

**Exhibit tool fixed** (`thesis_material.py`): each exhibit now carries `change_kind` —
*restructuring* / *annotation* / *unchanged* — with code lines counted after stripping comments,
and `INDEX.md` groups the case studies under "the agent changed the code", "the agent only added
pragmas" and "the agent changed nothing (declined)". Before this, `2mm` and `lu` counted the
model's multi-line `/* … */` explanations as changed code and read as restructurings; they are
annotations. New exhibits: `floyd_restructured_peeling`, `trisolv_reduction_extracted`.

### 5o. The server moved to the one-repository layout (2026-09-20)

`evaluation/` lives inside the agent repository, so the server now needs ONE checkout instead of
two, and `server.sh sync` is a single `git fetch` + `merge --ff-only` where it used to be a git
update of the agent plus an rsync of the harness working tree. That removes a whole class of
drift: the harness on the server can no longer be a different state from the harness on the Mac,
because there is no separate harness to copy.

*Done and verified.* Server checkout fast-forwarded to `b19d675e`; parity OK on every item
(agent head, harness head, both trees clean, wrappers, explorer and library as checkouts,
`anthropic` and `claude-agent-sdk` versions). Packages regenerated there from the new location and
compared file by file with the Mac's: **295 files, 0 differences** — so a run on either machine
measures the same program. A no-model smoke (`polybench/2mm`, arms `default` and `discopop_gate`)
ran end to end from the new layout, with the new checks printing first: *"arm settings verified
against the agent's own parser (2 arm(s))"*.

*What is left of the old repository on the server.* `~/new_benchmark_harness` (19 GB: 13 GB of
run directories, 4 GB of benchmark sources) is now unused. Every experiment run in it is archived
in `results/` here, and the two things that were NOT — `t0_1_calib`, which turned out to hold no
trials, and the launcher logs — have been dealt with: the logs are now tracked at
`results/logs/launcher/` as provenance (the launch command, the progress, the credential sweep
of every server run), since they would otherwise be lost with the directory. The server's disk is
at 99 % (32 GB free), so removing it is worth 19 GB — the author's call, not an automatic one.

### 5r. The campaign's scope is narrowed to three suites that can show the contribution (2026-09-21, D30)

**The author's decision**, five hours into E1's class-R run, with 35 trials finished and every
one of them `no-change`: *"pick only the ones that will show results, not just taking so long
then nothing … only TSVC, LULESH and RepoOMP."* And, against the suggestion to keep one
PolyBench run as a no-harm control: *"`hotspot`, `seidel-2d`, `md`, `npb/is` do not add much
value, and PolyBench already-parallel does not show any benefit for the agent."*

**The rule that makes this a selection and not cherry-picking** — every condition is decided
WITHOUT calling a model, so no benchmark is chosen or dropped by what the agent achieved on it:

1. DiscoPoP can profile it within the limit (D26);
2. DiscoPoP alone reaches no verified parallel program (T0.11) — it needs restructuring;
3. a VERIFIED, output-equivalent parallel version exists (T0.10);
4. the no-model ceiling test shows the arm under test can KEEP that version (T0.13).

| Suite | Role | By the rule |
|---|---|---|
| **TSVC-2**, 25 loops | the controlled suite with ground truth: E1's claim and every ablation (E2, E3, E4, E8) | 18 R (16 keepable under `default`, T0.13; `s331`, `s341` need a pragma DiscoPoP cannot write — E3's material), 3 A, 4 D; expert ceilings ≥ 1.45× at the gate's timing size; ≈ 10 min per agent trial |
| **LULESH 2.0**, serial path | the real application (E6): sequential · DiscoPoP alone · DiscoPoP + agent · LLNL's expert OpenMP | one profile = 23 s instrument (28 GB), 4.5 s run, 16 s explore; **packaged** (`llnl/lulesh`, equal to the original's report at three sizes) with LLNL's OpenMP release as its expert reference, verified correct through the harness (§6, 21 Sep); server pre-flight owed (§5s) |
| **RepoOMP's NPB-C**, 8 kernels | against the closest published system on identical programs (E11) | EP, IS, CG profile in 20–99 s; BT, SP, LU, FT, MG to be probed; to be packaged and pre-flighted |

**Out — corrected the same evening.** The author asked: *"before removing the benchmarks did
you verify that they are with not much value? and what about the rest of Rodinia; also see
whether NAS is useful."* They had not been verified, and one reason given in the first version
of this section was wrong. What was then checked, all of it without a model:

| Benchmark | What was checked | Result | Under the rule |
|---|---|---|---|
| `rodinia-3.1/hotspot` | a hand-written restructuring — the chunk loop split in two, boundary chunks sequential and in order, interior chunks `parallel for` (`reference_solutions/rodinia-3.1/hotspot.cpp`) — judged by the harness (`verify-source`, run `ref_check_mac`) | `FASTER`; dump byte-identical on the shipped AND the seeded input, digest error 0; 1.44× / 1.52× at 2 / 4 threads (Mac, LARGE); by hand bit-identical at 1–48 threads under static, dynamic and guided schedules | **The first version said "no output-equivalent parallel version exists". Wrong**: it is Rodinia's OWN OpenMP version that is schedule-dependent (§6), not the problem. Conditions 1–3 hold; condition 4 (T0.13) is owed on the server |
| `polybench/floyd-warshall` | the textbook shared-memory form, written by hand: write only on improvement, i-loop parallel for fixed k — row and column k are fixed points of step k whenever `path[k][k] ≥ 0` (`reference_solutions/polybench/floyd-warshall.c`) | `FASTER`; dump byte-identical on both inputs; 2.46× / 3.61× at 2 / 4 threads (Mac, LARGE) | conditions 1–3 hold, and **condition 4 holds on the Mac**: T0.13 (`results/T0_instruments/T0.13_default_arm_ceiling/runs/t0_13_ceiling_floyd_mac`, safety only, 52 s) — on the reference with its pragma stripped DiscoPoP reports a do-all on all three loops; the gate rejects the one on the k-loop (TSan: a race — a DiscoPoP false positive caught), applies the one on the i-loop, skips the nested j-loop, and Settle verifies the file. Speed at the timing size and more than four threads are owed on the server. E1's own trials on it — 3 of 5 `gained`, 5.1–10.3×, DiscoPoP alone 0 of 5 — are NOT what admits it |
| `burkardt/md` | Burkardt's source carries his OpenMP version as commented-out pragmas (`md.cpp` 275–280 and 626–630): one `parallel` region, one `for reduction(+: pe, ke)` | the expert changed no code | not a restructuring benchmark — what it lacks is a pragma DiscoPoP does not write. Out of every restructuring experiment; a candidate for E3 only, at 35 minutes per trial |
| `polybench/seidel-2d` | — | a true Gauss–Seidel recurrence; an exact parallel form exists in theory (wavefront skewing), none verified is at hand, and by the class definitions it is a D | out: condition 3 not shown |
| `npb/is` | — | the same program is one of RepoOMP's NPB-C kernels | covered by E11; the separate package is redundant |
| `polybench/bicg`, `trisolv`, `doitgen` | T0.1 | `bicg` and `trisolv` cannot be timed at any size, so the speed check is off for them (D22) and they cannot show a speed result at all; none of the three has a verified reference | out |
| PolyBench's 25 class-A kernels | T0.11 | DiscoPoP alone already parallelizes them | out by the author's decision: they cannot show a benefit of the agent |

**The two surveys behind "the rest of Rodinia" and "is NAS useful" (no model, 21 Sep):**

* **Rodinia 3.1.** In all 19 programs that ship a serial and an OpenMP version, the expert
  version is the serial code plus pragmas: 0 to 7 code lines differ. Rodinia's experts did not
  restructure, so where DiscoPoP alone fails there, what is missing is a pragma or a clause and
  not a rewrite. `hotspot` is the exception that proves it — its expert pragma is WRONG, and the
  correct version needs the split above.
* **RepoOMP's NPB-C.** Each expert `<k>_ori.c` equals the pragma-free `<k>_#_omp.c` plus
  pragmas: 0 to 18 lines differ (continuation lines and block comments counted properly).
  RepoOMP made its sequential versions by deleting the pragmas from NPB's OpenMP code, so the
  code is ALREADY restructured for parallelism (per-thread buckets in IS); what remains is
  pragma authorship — parallel regions, `for nowait`, `master`, `threadprivate`. Probe on the
  Mac (`results/E11_repoomp/preflight/e11_npbc_probe_mac`): EP, IS and CG profile in under two minutes each with NPB's
  verification SUCCESSFUL, and DiscoPoP already reports 6 + 2, 10 and 24 + 9 do-all + reduction
  patterns in them. FT did not finish instrumenting within 30 minutes on the 8 GB Mac and is
  inconclusive; FT, MG, BT, SP, LU go to the server.
* **So NPB-C is useful, but not for the restructuring claim.** It carries E11 (the comparison
  with the closest published system on identical programs), the no-harm question at application
  scale, and E3's question (who writes the pragma). Under the `default` arm it is EXPECTED to
  show little benefit of the agent, and that expectation is written here before the runs.
* **LULESH is the opposite case, which is why it is the campaign's application.** LLNL's OpenMP
  release differs from the serial path by **168 code lines beyond its 44 pragmas**: 67 in
  `CalcFBHourglassForceForElems` and 44 in `IntegrateStressForElems` (forces computed into
  per-element buffers and gathered per node, instead of scattered into nodes that elements
  share), 10 in each of the two constraint functions (per-thread minima), 20 in the main loop.
  The expert RESTRUCTURED, in the two most expensive force routines.

**Whether `hotspot` and `floyd-warshall` re-enter is the author's decision**, to be taken when
T0.13 has run on the server for both; until then D30's three suites stand.

**What is NOT hidden.** Everything E1's class-R run executes before and after this decision is
archived and reported — the 26 benchmarks as registered, and the subset the rule admits — and
the rule is recorded here BEFORE any TSVC result of E1 exists. The finished `md`, `hotspot`,
`seidel-2d` and `is` trials are all `neither`, with 0 unsafe acceptances after ≈ 100 model
calls, which is itself evidence for C2.

**The no-harm question without PolyBench** ("does the agent break what DiscoPoP already does?"):
TSVC's three class-A loops, LULESH's ≈ 40 loops that are parallel as written, the NPB-C kernels,
and E10's archived PolyBench result (nothing below DiscoPoP alone with the speed check at the
kernel's timing size). Stated as a limitation: the no-harm evidence is application-scale and
small-n, not a 25-kernel sweep.

**Consequences.** E1 = TSVC (R ×5, A, D ×3) + the archived non-TSVC trials; its classes-A/D
follow-up runs shrink to TSVC's 3 + 4 loops. E2, E3, E4, E8 run on TSVC's class R only
(E3 additionally reads `s331`/`s341`). E6 (LULESH) and E11 (RepoOMP) each get their own
packaging and no-model pre-flight (sizes, DiscoPoP-alone class, feasibility) before any model
call. E5 (profiling cost) and E7 (gate as classifier, offline) are unaffected. E9 (ranking) needs
multi-region programs and moves to LULESH and the NPB-C kernels.

### 5s. Every instrument and every experiment re-examined after D29, D30 and Fixes 86–88 (2026-09-21)

The author: *"check the planned experiments if something needs to be changed, and the previous
ones we ran — the Ts for example — does anything need adjustments or a re-run?"* Three things
moved under them on 21 Sep: the scope (D30), what the pipeline does after a kept rewrite
(Fixes 86–88, D29), and — found while answering the author's question about a LULESH reference
— what the LULESH package prints (§6).

**Instruments**

| ID | Still valid? | Why | Owed |
|---|---|---|---|
| T0.1 sizes | yes, for TSVC | a property of each benchmark on the server; TSVC's sizes are what E1 runs with | **LULESH and the NPB-C kernels** (verification size ≥ 1 s serial, timing size ≥ 0.25 s) |
| T0.2 stability, T0.7 explorer | yes | properties of DiscoPoP, not of a suite: one profile per trial, DiscoPoP alone reported as a range, explorer retried. The kernels they were measured on left the scope, the policy did not | nothing separate: E1's `discopop_gate` arm IS five independent profiles of every TSVC loop — its spread is read out with E1. LULESH: three profiles in its pre-flight |
| T0.3 oracle | yes | replays archived candidates through the harness verification; independent of scope | one addition, below: every package with an expert reference must pass the **reference acceptance check** |
| T0.4 timing noise | yes | a property of the host under the campaign's load (v2): 1.1× resolvable with 5-repeat medians | none |
| T0.5 shares | yes, where it was run | fresh directory per measurement, so DiscoPoP's accumulating hotspot files (Fix 87, N1) never touched it; it does not read loop counts (Fix 88) | **LULESH and NPB-C** — multi-region programs: which regions pass `--min-runtime-share 0.01`, how many candidates a trial has, and what share the two force routines LLNL restructured hold |
| T0.6 patterns in `main` | yes | D4 rests on it | **LULESH** (`lulesh_main` holds the time-step loop and stays in scope; `main` is the package's driver) and NPB-C |
| T0.8 layouts | yes | compares the project layout with the merged file | not applicable to LULESH (project only) and NPB-C (single files) — skipped with this reason |
| T0.9 fast refresh | **re-run before E3** | it compares patterns and dependences, which D29 does not change, but the refresh code path it exercises did change (runtime re-measurement, recorded kind), and E3's reading cites it | `benchmark/refresh_depth.py`, three synthetic programs, Mac-safe |
| T0.10 expert references | yes for TSVC (18 of 18 ≥ 1.45× at the timing size, server) | — | today's three references are verified on the MAC ONLY, at 2 and 4 threads: LLNL's LULESH (correct to 5.6e-15, 1.70× at STANDARD), `hotspot` split (1.52×), `floyd-warshall` textbook (3.61×). **Server re-verification at 6 / 12 / 24 threads is owed before any of them is cited** — `hotspot` showed that four threads cannot see a schedule-dependent result |
| T0.11 classes | yes | the `discopop_capability` arm keeps no rewrite, so Fixes 86–88 never ran in it | **LULESH and NPB-C.** Expectation, stated before measuring: LULESH is class **A at program level** (DiscoPoP alone will parallelize many of its ≈ 40 parallel loops and come out `FASTER`), so the agent's verdict there is `better`/`equal`/`worse` — a speedup ratio against DiscoPoP alone — and not `gained` |
| T0.13 default-arm ceiling | yes for TSVC, with one caveat | run after Fixes 86–88; but on the Mac, where the gate's schedule stress reaches 4 threads | **repeat on the server** (no model, ≈ 1 min per loop) and extend to `hotspot`, `floyd-warshall` and LULESH (LLNL's restructured routines with the pragmas stripped: does DiscoPoP find the do-alls, and do its pragmas pass?). The tool handles the project layout since 21 Sep (the package with the expert's files laid over it, profiled through the unity unit exactly as the harness does); `floyd-warshall` on the Mac, safety only: KEPT |

**New instrument — the reference acceptance check (T0.14).** For every package that has an
expert version, `verify-source` on that version must come out correct. It is what caught the
LULESH defect (§6): the package would have called every correct parallel LULESH `BROKEN`,
LLNL's own included. TSVC passes by T0.10; LULESH passes since today's fix; each NPB-C kernel
must pass with its `<k>_ori.c` before E11 starts.

**Experiments**

| | Change | Reason |
|---|---|---|
| E1 (running) | arms unchanged. The PRIMARY set becomes TSVC: R 18 ×5, A 3 ×1, D 4 ×3; the eight non-TSVC class-R benchmarks already in the run are reported in full as registered, in a second table. Follow-up runs A and D shrink to TSVC's 3 + 4 loops | D30 |
| E1-bare | TSVC class R, 18 loops × 5, arm `bare_llm` alone (its `default` counterpart is E1's own 90 trials: same benchmarks, sizes, verification, model). **The author's go, 22 Sep.** Read-out: `main_comparison_stats.py --arm bare_llm` and `--arm default` side by side — rate verified-parallel, rate FASTER, and BROKEN named; the BROKEN count is what the gate prevents (C2) | the pipeline must be shown to add something over asking the same model; smoke on the Mac 22 Sep (`results/E01b_bare_llm/preflight/bare_smoke_mac`): `s211` restructured correctly with 3 pragmas, `parallel-not-faster` at 4 Mac threads |
| E2 (2 × 2) and E2-source | TSVC class R, all 18 loops | D30 |
| E2-C (13 arms), E2-D (5 arms) | **seven loops, fixed here by a rule that looks at no result**: the first loop in TSVC's source order of each of TSVC's OWN categories among the 16 loops T0.13 found keepable — `s112` (linear dependence, loop reversal), `s121` (induction variable), `s211` (statement reordering), `s241` (node splitting), `s252` (scalar expansion), `s281` (crossing thresholds), `s291` (loop peeling). N = 3, as screening experiments and not headline claims (N = 3 confirmed by the author, 23 Sep; E2-C then lost its `feedback` group — §6, 23 Sep) | 13 arms on 18 loops at N = 5 would be 1,170 trials, ≈ 195 lane-hours, for a secondary question |
| E3 | TSVC class R; `s331` and `s341` are read separately (they need a pragma DiscoPoP cannot write); two or three NPB-C kernels may join as the application-scale pragma-authorship case once packaged. **T0.9 is re-run first** | NPB-C's and `md`'s experts are pragmas only (§5r) |
| E4, E4-mode | **conditional**: run only if E3 shows that the fast refresh loses or wrongly accepts something on TSVC. If it does not, there is no gap for `--llm-recon` / `--llm-deps` to close, and E4 is reported as not needed, with E3's numbers as the reason | both need `--fast-refresh` (D28); 0 of 108 archived fast refreshes fell back |
| E5 cost | unchanged; it now has per-trial refresh kinds and counts to read (D29) and LULESH's measured profile cost | — |
| E6 LULESH | arms: sequential · `discopop_gate` · `default` · LLNL's expert (`verify-source --source reference_solutions/llnl/lulesh`, in place since today). Pre-flight owed: T0.1, T0.5, T0.11, T0.13, three profiles for stability, and the profile's disk footprint (28 GB measured earlier) against the server's free space | package corrected today |
| E7 gate as classifier | offline, unaffected; its corpus gains a labelled case — Rodinia's own `hotspot` pragma, an expert version that is wrong. Must be replayed on the SERVER: at four threads the Mac passes it | hotspot finding (§6) |
| E8 depth | TSVC class R. H8 stated in advance: depth 0 suffices on single-nest loops, so a null result is the expected outcome and a finding. LULESH ×3 added if E6's budget allows | depth only matters where a kept rewrite exposes further regions |
| E9 ranking | moves to LULESH and NPB-C (EP, IS, CG) — TSVC kernels have one region, nothing to rank. D28's caveat stands: `full_no_hotspots` also makes the share filter inert | D30, D28 |
| E10 speed check | finished, reported as it ran (PolyBench, six kernels). Not re-run: its conclusion (D22, the speed check at the kernel's timing size) was confirmed on TSVC by T0.13 — 16 of 18 kept with the check on. Limitation recorded: its prompts carried DiscoPoP's mispaired iteration counts (Fix 88) | — |
| E11 RepoOMP | the agent's entry is the `default` arm, pre-stated; the `llm_pragmas_full_reprofile` arm is reported beside it because NPB's difficulty is pragma authorship. Others: DiscoPoP alone, RepoOMP's released outputs, the expert `<k>_ori.c`, all through `verify-source`. Packaging, T0.14, T0.1, T0.11 owed | §5r |

**Nothing already run has to be repeated with a model.** `pilot4` and E10 ran with
`--llm-pragmas` on, where a rewrite annotates itself and never passes through the path Fixes 86
and 87 repaired; their prompts did carry wrong iteration counts (Fix 88), which is recorded as a
limitation of those two runs. E1 runs on a commit that has all three fixes.

**Merge gate for the work branch.** Before `e1-readout-e2-prep` is merged into the campaign
branch, `test_arms.py` must show that the resolved configuration of `default` and
`discopop_gate` is identical before and after — the branch adds options (`--evidence-file`,
`--prompt-omit`) that must be inert when unset.

**Order on the server once E1's lanes are free, no model calls:** (1) re-verify the three
references at 6 / 12 / 24 threads; (2) T0.13 on TSVC, `hotspot`, `floyd-warshall`; (3) LULESH
pre-flight — T0.1, T0.5, T0.6, T0.11 ×3, T0.13, disk footprint; (4) NPB-C probe of FT, MG, BT,
SP, LU, then packaging, T0.14, T0.1, T0.11. **None of this runs on the Mac**: it has 8 GB of
memory, and on 21 Sep two such jobs left in the background pushed it so far into swap that the
disk ran full (1.7 GiB left; 28 GiB again a minute after they were stopped).

### 5q. Arguments that depend on each other (2026-09-21)

The author: *"during testing some args were depending on each other and some of them were wired
— this might corrupt the experiments … also be careful if any of the arguments need to run
together or not."* Audited in full. Three kinds, handled three ways.

**(a) One argument needs another — the agent REFUSES the combination.** Checked by the new
feature check `arg-dependencies`, which asserts each is rejected:

| combination | why it cannot work |
|---|---|
| `--llm-recon` without `--fast-refresh` | reconstruction exists to repair what the fast refresh could not translate; a full re-profile leaves no gap |
| `--llm-deps` without `--fast-refresh` | same: every region has freshly measured dependences, so there is nothing to delete |
| `--pragma-arbitration` without `--llm-pragmas` | it compares the pragma the MODEL wrote with DiscoPoP's; without model pragmas there is never a collision |
| `--pragma-arbitration` without `--require-speedup` | it decides between the two by TIMING them |

**(b) Two arguments contradict each other — refused.** `--llm-recon` with `--llm-deps`: one adds
dependences for new code, the other deletes ones it judges spurious, so together the model argues
with itself inside one profile.

**(c) One argument makes another INERT — no error, and therefore the dangerous kind.** These were
found by this audit and are now printed before every run ("settings made INERT by another setting
of the same arm"):

| combination | what silently stops applying |
|---|---|
| `--no-hotspots` with `--min-runtime-share` / `--min-impact` | both filters live in the measured-time branch; without measurements ranking falls back to the workload proxy and `--min-workload` |
| `--restructure-depth > 0` with `--fast-refresh` | the refresh applies only at the LAST level; deeper levels get a full re-profile anyway |
| `--no-require-speedup` with a per-kernel timing size | a timing size is set and nothing times at it |

**`--pragma-arbitration` was the worst case and is now fixed properly.** It defaulted to `True`
and was declared `True` by arms that could never run it — with `--llm-pragmas` off by default
(D23), that was *every* arm. It now resolves to `False` whenever it cannot fire, so
`--print-config` — which the harness checks every arm against (D24) — reports what the run will
actually do rather than what was asked for.

**One real consequence for a planned experiment.** Of all 20 arms, exactly one carries a silent
interaction: E9's `full_no_hotspots`. Turning hotspots off necessarily makes `--min-runtime-share`
inert, so that arm ranks by the proxy **and** queues regions the share filter would have dropped.
That is a consequence of E9's own variable, not an independent difference — but E9 measures the
two together, and its write-up must say so rather than claim an effect for ranking alone.

### 5n. Every argument of every arm is DECLARED and verified against the agent's own parser (2026-09-20)

The author: *"for every experiment every agent argument should be clearly set to serve the purpose
of the experiment, making sure that nothing wired or inherited would break the intended argument
selection."* Two things on 20 Sep showed why the inheritance chain (`common_flags` → the arm's own
flags → the agent's defaults) is not safe on its own: making the speed check the campaign default
confounded four matrix experiments, and flipping `--llm-pragmas` changed what five arms meant.
Both were caught by reading, which is not a guarantee.

**The guarantee.** Every arm in `arms.json` now carries a `settings` block naming each argument
that carries its purpose — for example `default`: `budget 3`, `llm_pragmas False`,
`require_speedup True`, `hotspots True`, `fast_refresh True`, `restructure_depth 0`,
`pragma_arbitration True`. Before a run starts the harness builds each arm's full command line,
adds the new agent option **`--print-config`** (which resolves every argument, prints them as JSON
and exits without touching a profile), and compares. **Any difference stops the run**:

```
arm settings do NOT match what the agent parses:
    default: declares llm_pragmas=True but the agent parsed False
refusing to run: fix arms.json `settings` or the arm's flags
```

The check is made against the AGENT'S OWN PARSER, not against the harness's model of it, so it
covers changed defaults, flags inherited from `common_flags`, flags an arm adds, the order in
which they override one another, and typos — anything that could leave an arm running something
other than the experiment it serves. Credentials are redacted from the dump (`api_key`,
`api_base`), because it reaches logs, manifests and the terminal.

Together with `check_arm_compatibility()` (§ above), every run now prints, before anything
executes: the arms whose declared settings were verified, and the settings on which those arms
differ — which must be exactly the experiment's variable. An arm without a `settings` block is
refused, so the declaration cannot be skipped for a new arm.

### 5m. The studies that were decisions, not protocols — now specified (2026-09-20)

The author asked whether the separate studies are prepared and written down. Honest answer at the
time: **E1–E11 are specified** in the plan (arms, benchmarks, hypotheses, repeats, scoring), but
two things the record keeps calling "a separate study" were only DECISIONS — a sentence saying
they would happen, with no protocol. They are specified here, so neither can quietly become
"we ran out of time".

**S1 — Budget efficiency (the old D3).** *Question:* what does the third attempt buy, and would a
budget that follows a region's runtime share buy the same for fewer calls? *Why it is a study and
not a default:* a share-weighted budget makes the number of attempts a function of the benchmark,
so every cross-arm and cross-benchmark comparison would vary in two things at once — the confound
this record had to repair elsewhere on 20 Sep. D10 stands: `--budget 3` fixed everywhere.
*Protocol, no new model runs for part (a):*
 (a) **Offline, from data in hand.** Every archived `candidates.jsonl` already records the attempt
     number of each Phase-A candidate and whether it passed. Measured across the archive:
     accepted 40 of 127 first attempts, 12 of 91 second, 6 of 82 third, 2 of 8 fourth. Report the
     curve, the calls-per-acceptance at budgets 1, 2 and 3, and — by replaying the recorded
     outcomes — which FASTER results a budget of 1 or 2 would have lost. This is a real result and
     it costs nothing.
 (b) **On-policy, only if (a) leaves the question open.** `--budget-policy share` against
     `--budget 3` on the class-R set, one repeat, same model: calls per verified-parallel result.
     Pre-registered stopping rule: if (a) shows the third attempt contributes < 5 % of acceptances,
     (b) is dropped and the offline result is reported instead.
*Threat to state:* the 60 acceptances come from the evaluation's own benchmarks, so they cannot
calibrate a policy that is then evaluated on the same benchmarks; (a) is descriptive, not a
calibration, and the write-up says so.

**S2 — Fix 85's arbitration as a measurement.** *Question:* on a loop both could annotate, whose
pragma is faster — the model's or DiscoPoP's? *Data:* every collision already writes
`pragma_arbitration` (winner, reason, ratio) into `candidates.jsonl`, so this accrues from every
run with `--llm-pragmas` at no extra cost. *Protocol:* report the win/loss/noise counts and the
ratio distribution over E3 (whose cells carry `--llm-pragmas`) plus E10's archived runs, per
benchmark class. *Pre-registered reading:* a result in either direction is publishable — if
DiscoPoP wins most collisions that is an argument for the new default (D23); if the model wins
most, the E3 arms are where the default should be revisited. *Known bias to state:* arbitration
only fires where the model chose to annotate a claimed loop, which is not a random sample of
loops.

**What is specified elsewhere, so it is not repeated here:** E1–E11 (plan §5, with the
benchmark-to-experiment mapping and its "why" in §3), the instruments T0.1–T0.12 (§5e and §7), the
gate-stage ablation E7 (offline replay of saved candidates), and the pre-flight every experiment
must pass (§5k, RUNBOOK step 0/0a).

## 6. Change log

| Date | Repo | Change | Why |
|---|---|---|---|
| 2026-09-20 | repositories | **D20 — one repository.** The harness moves into the agent repository as `evaluation/` (`agent/`, `shared/run_store.py`, `benchmarks/` = the SOURCES of the suites it uses: PolyBench 3.2, NPB, RepoOMP's NPB-C, TSVC-2, LULESH, `md`, Rodinia `nw`/`pathfinder`/`hotspot`). Left behind: the group's three harnesses and GUI, 4 GB of reference outputs and data files nothing here reads. Copied from `new_benchmark_harness@1514ceb` (tracked files only, 5,350 files, 42 MB); relative paths unchanged, so every `agent/...` path in this record still holds under `evaluation/`. **Proof the move changed nothing:** a FRESH CLONE (53 MB) regenerates all 70 packages byte-identical to the old ones (every file, every metadata field, every `output_sha256`) — the clone test caught what the working copy hid: the root `.gitignore`'s `data*/` swallowed PolyBench's `datamining/` kernels, and `prepare_polybench.py` discovered kernels through the old harness's per-kernel config directories (now: PolyBench's own layout, same 30 kernels); integrity test 30/30, scaffold test 0 failures; a no-model smoke run (`move_smoke`, `atax`) reproduces `dp_alone_fix84_mac`'s outcome. Code changes: only how the agent repository is located (`cli.py`, `profile_stability.py`, the three shell scripts) and `server.sh sync` (one `git` fast-forward instead of `git` + `rsync`). The repository is a PUBLIC fork (GitHub cannot make a fork private) and the author chose to publish: the server's address and account were moved out of the tracked files into the untracked `agent/tools/server.local` first; a scan found no credential, token value or address left. Old repository frozen and tagged: archived runs up to `e10` record ITS commit hashes | the author: one place; and the old repository is 4 GB and cannot be cloned in full from GitLab, which a reader of the thesis would have to do |
| 2026-09-20 | plan | **D26 — scope rule (§5k): a benchmark DiscoPoP cannot PROFILE is excluded, measured once and reported; a benchmark DiscoPoP profiles but finds nothing in STAYS (that is class R, the claim itself).** Excluded: NPB `lu`, `mg`, Rodinia `nw`, PolyBench `adi` — four of 61. **TSVC `s291`/`s3112` were on this list for a few hours and were taken back off**: the explorer stall that put them there is RANDOM (`s3112` explored in 5.8 s on the next draw while `s322` and `s331` stalled instead), so the remedy is the timeout and a per-draw `PROFILE_ERROR`, not naming loops, each with its cost, reported as scope and as a threat to validity | the author: "the thesis is about the agent added upon DiscoPoP, not about DiscoPoP and whatever its limitation is" |
| 2026-09-20 | plan | **D25 — `polybench/adi` out of the model-driven set**: its instrumenting compile is 2,387 s per profile, 41 of the 135 minutes a T0.11 draw takes, two hours across three draws. Draw A's single measurement (`FASTER`, 19 Do-Alls) is kept as evidence of the cost; the class is left undetermined. Reported as a DiscoPoP limitation (L4) beside NPB `lu`, `mg` and Rodinia `nw` | the author asked why PolyBench is still needed; the answer is that 22 of its 27 kernels are the no-harm CONTROL and four are restructuring or decline cases — `adi` is neither, and it was the most expensive kernel in the set |
* **`polybench/adi` leaves the model-driven set (D25, author's call).** Its instrumenting compile
  takes **2,387 s — 40 minutes — per profile**, which is 41 of the 135 minutes a T0.11 draw needs;
  across three draws it would have spent two hours on one kernel. Draw A completed it (`FASTER`,
  19 Do-Alls), and that single measurement is kept as the evidence of the cost, but `adi` is
  excluded from draws B and C, so it has one draw where every other benchmark has three and its
  class is left undetermined. It joins NPB `lu` (instrumentation > 2 h), Rodinia `nw` (explorer
  ≈ 25 h) and NPB `mg` (task detection unfinished after 11 h) as a DiscoPoP cost limitation the
  thesis reports rather than works around; `docs/DISCOPOP_BUG_REPORTS.md` L4.
| 2026-09-20 | server | **The server moved to the one-repository layout (§5o).** One checkout; `server.sh sync` is now a single `git fetch` + `merge --ff-only`, so the harness on the server cannot drift from the Mac's. Parity OK; packages regenerated there are identical to the Mac's file by file (295 files, 0 differences); a no-model smoke ran end to end. The old `~/new_benchmark_harness` (19 GB) is unused — its launcher logs are now tracked at `results/logs/launcher/` so nothing is lost with it | D20; and the server had been running from a checkout that no longer received any of the day's changes |
| 2026-09-20 | agent + harness | **D24 — every arm DECLARES every argument that carries its purpose, and the harness verifies it against the agent's own parser before a run starts (§5n).** New agent option `--print-config` (resolved configuration as JSON, credentials redacted); `settings` block on all 19 arms; any mismatch refuses the run, and an arm without a declaration is refused too | the author: "for every experiment every agent argument should be clearly set to serve the purpose of the experiment, making sure that nothing wired or inherited would break the intended argument selection" — after two changes on one day silently altered what four experiments and five arms meant |
| 2026-09-23 | finding (validity) | **D36 — every TSVC package told the model the answer; E2 A+B stopped.** Found when the author asked what `reference_solutions/` is for and whether it is used "to cheat". The reference solutions are not the problem: only four no-model harness tools read them (T0.10, T0.13, T0.14 and the packagers), the agent package never does, and they are never copied into the model's workspace. The problem was the PACKAGE: `prepare_tsvc.py` (generator v2, 19 Sep) opened every TSVC source with TSVC's own category comment and this harness's labels — `class: restructure   transformation: statement reordering + loop distribution` (`s211`), `node splitting (preload the old a[i+1])` (`s241`), `loop reversal with an anti-dependence (needs a copy)` (`s112`), `search loop -> max-index reduction` (`s331`), `first-order linear recurrence` (`s321`) — and one scaffold comment named "peeling, splitting and wrap-around". Both the agent's model and the model alone are told to read the file, so every model trial on TSVC saw it. It broke this record's own rule §1a (no parallelization answer in a packaged source, 15 Sep). **Affected:** E1's 105 TSVC agent trials (class R 90, A 3, D 12), E1-bare's 90, the E2 smokes (16), and E2 A+B — **stopped 23 Sep 20:21 UTC after 63 of 450 trials** (archived as `superseded/e2_ab_a`, `e2_ab_b`, 'hint in source'), because E2 measures whether DiscoPoP's evidence helps and the transformation's name reached even the no-evidence arms. **Not affected:** DiscoPoP alone (no model; DiscoPoP ignores comments), the no-model instruments (T0.10, T0.11, T0.13, T0.14), E10 and E1's non-TSVC trials — PolyBench, NPB, Rodinia, `md`, LULESH carry only their original headers. **Fixed:** generator v3 — the header names only the loop and its provenance, the class/transformation/category live in `meta.json` only (never in the workspace); the scaffold comment neutral; all 25 packages and 21 references regenerated, their code identical to v2 with comments stripped, 25 of 25 validate; `test_integrity.py` §1b fails on any class/transformation label in any experiment package source and on transformation vocabulary in a TSVC source (218 sources; it fails on v2). **Consequence:** E1's TSVC numbers and E1-bare's are 'with the hint in the source' and are superseded by a clean redo (below); the difference between the two is itself a measurement of what a one-line hint is worth. The residual threat stays in §threats: the loop names and bodies are TSVC's, public, and may be in a model's training data | the author, 23 Sep: "do you use them to cheat and tell the model and the agent what to do?" |
| 2026-09-23 | agent | **Fix 95 — the model's file tools are confined to its workspace (found with D36), and D37 / Fix 96 — the model alone gets nothing of ours that helps it.** (1) `allowed_tools=["Read","Edit","Write"]` auto-approves each tool for ANY path; live, one Haiku call, the old options read a file outside the workspace and reported its secret word. Now a PreToolUse hook denies any file-tool path outside the workspace (absolute, `..`, symlink) and shell / web / search tools are blocked; live, the same request is refused. The campaign's prompts never name a path outside the workspace and nothing in the archived logs shows such an access, but the model's session transcripts were not kept (9 remain, with no tool calls in them), so for the runs before this fix it can be neither shown nor excluded — stated as such in §threats. (2) The author: "the LLM alone should not use anything of ours to help or guide it". E1-bare's prompt carried ≈ 560 words of the agent's guidance (THE CONTRACT, clause rules, OpenMP loop rules, pragma forms) and a task line naming transformations ("splitting a loop, adding a buffer, reordering statements"). `bare_llm --prompt minimal`, now the default: role, tools, "Parallelize this program with OpenMP so that it runs faster on a multi-core machine. Its output must stay exactly the same.", and the functions that measure the program (a condition of the measurement, not help) — 87 words; `--prompt contract` reproduces E1-bare. Judged afterwards exactly as before: harness verification, then the gate's race stages (`race_check.py`). Feature checks `workspace-confined`, `bare-llm` (both fail on the old code); mypy 0; agent `docs/FIXES.md` 95, 96 | the author, 23 Sep |
| 2026-09-23 | plan | **The author's decisions 1–9 ("do all from 1 to 9"), each recorded before any data it concerns exists.** (1) E2 A+B stopped (D36). (2) **Clean redo**: E2 A+B again on v3 packages with `bare_llm` (minimal prompt) as a sixth arm in the same runs (`e2_ab_clean_a`, `_b`) — its `default` and `bare_llm` arms with `discopop_gate` ARE the clean three-way E1 on TSVC class R — plus E1's controls again: class A ×1 and class D ×3 × `discopop_gate`, `default`, `bare_llm`. (3) **The model alone on class D** (does it ship wrong programs on true recurrences?) — in (2). (4) **H5d, pre-registered:** on the TSVC class-R loops where the clean model-alone arm ships at least one BROKEN program, the evidence effect (FASTER rate `full_b1` − `no_evidence_b1`, per loop) is larger than on the other loops; Mann–Whitney on the per-loop effects, reported with effect size; refuted if not larger. The subgroup is defined by a rule fixed now, from an arm the evidence does not touch. (5) **E3 ×5, and H6b, pre-registered:** on TSVC class R, `llm_pragmas_full_reprofile` on agent v2 reaches at least the clean model alone's race-free FASTER rate with 0 BROKEN; refuted if lower (per-loop paired Wilcoxon, one-sided) or if any trial is BROKEN. (6) E3's `default` cell reuses E2's clean `default` trials if the agent commit is unchanged, else it runs again. (7) **A harder tier (E2-app):** E2's core contrast — `discopop_gate`, `bare_llm`, `no_evidence_b1`, `full_b1` — on LULESH and NPB-C, admitted by D30's rule, sized after the LULESH pre-flight. (8) **T0.11 on TSVC's indirect-addressing loops** (`s4112`–`s4117`, `s4121`, `s491`; no model): any class-R loop with a verifiable expert version is a candidate for the harder tier. (9) **E12, a confirmatory run, rule fixed now:** after E2, E3 and E8, per factor the setting with the highest race-free FASTER rate on TSVC class R (ties: fewer unusable programs, then lower cost) — one configuration, run ×5 on TSVC class R and on the harder tier against the model alone and DiscoPoP alone | the author, 23 Sep |
| 2026-09-24 | result | **T0.4 at four lanes (`t0_4_four_lanes`, server, no model, host load ≈ 2): four lanes hold for TSVC, not for memory-bound serial runs.** Median-of-5 resolvable ratio with four 12-core lanes running at once: `tsvc/s211` 1.016× serial / 1.008× parallel, `tsvc/s254` 1.013× / 1.011× — well inside the 1.1× threshold; `polybench/2mm` serial **1.123×** (CV 13.8 %: four lanes share each node's memory bandwidth), parallel 1.020×. **Decision, within the author's condition:** four lanes for TSVC-based runs (E1-clean, E2, E3, E4, E8), two lanes stay for PolyBench and the applications until a check on them says otherwise. The host was quiet, so this is the lanes' interference with EACH OTHER; T0.4 v2 remains the measurement under other users' load | the author's lever (b): "it needs a 30-minute no-model timing check first" |
| 2026-09-24 | plan | **D38 — every experiment gets a MATCHED model-only twin: the pipeline becomes a factor of each experiment.** The author: "for every experiment we need a comparable model-only call to make it as fair as possible — in the no-evidence experiment the model gets no evidence at all; when the agent adds the pragmas the model adds them, if the agent doesn't the model shouldn't and DiscoPoP decides at the end; for the depth experiment the model alone should do something similar." Read as a 2 × 2 over the model: {no DiscoPoP, DiscoPoP (region, evidence, annotation)} × {no gate, gate (checks, feedback, retries)} — the model alone (`bare_llm`, the mirror prompt, D37) and the agent are its corners; each twin is **the agent arm minus the gate**. **How (built 24 Sep, `discopop_agent/twin.py`, a new entry point; arms `"runner": "twin", "twin_of": <agent arm>`, which inherit that arm's flags, settings, timing size and evidence file in `cli.resolve_twins`):** the twin parses the agent arm's own arguments with the agent's own parser and runs the agent's own code for everything that is DiscoPoP's — the numerical noise floor (for the prompt's wording), the hotspot measurement, the ranked queue, the COVERED / DiscoPoP-already-has-a-pattern / depth / budget-policy skips, the evidence (`assemble`) and the request (`_build_direct_prompt`) — and asks the model about **every region the agent would ask about, one attempt each**, no feedback, no format re-prompt. The system prompt is the agent's own blocks with four texts changed and nothing else (feature check `twin-prompt`, 12 configurations, mutation-tested): "HOW YOUR REWRITE IS CHECKED" becomes "HOW YOUR REWRITE IS JUDGED" (nothing checks during the run, one attempt; compile, TSan, schedules, outputs, timed against the original sequential program — and, where DiscoPoP writes the pragmas, that DiscoPoP re-profiles and inserts them, nothing reverted); the clause promising feedback after a failed attempt and the sentence about edits from an earlier turn are removed; "faster than the same build on one thread" reads "… the original sequential program" (the harness's comparison). What the model leaves stays; after an edit the program is re-profiled, as the agent re-profiles a kept rewrite, and the queue is rebuilt the agent's way (content fingerprints, new regions at depth+1 up to `--restructure-depth`). At the end DiscoPoP annotates as Phase B would, from the final profile — every applicable pattern, re-derived against the file, with DiscoPoP's fixed clause repair (Fix 91), skipping only what is structural (already annotated, nested in a parallel loop, below --min-workload) — **with no clause check, TSan, schedules, speed check, D33, Settle or floor.** In the model-writes-pragmas twin DiscoPoP's pragmas also go in at the end, as the agent's Phase B puts them in (through the gate). The program as the model left it is saved (`agent_patches/twin_model_program.*`), so the model's share and DiscoPoP's unchecked share of a twin's result can be separated. Feature check `twin-run`: the agent, stopped at its first model call, and the twin ask the SAME request; the edit is kept unchecked, re-profiled, and DiscoPoP's pragmas inserted with no gate step. **Twins:** `twin_dp` ↔ `discopop_gate` (--budget 0: no model — DiscoPoP's own program with nothing checked; no model cost); `twin_no_evidence` ↔ `no_evidence_b1` and `twin_full` ↔ `full_b1` (E2 — the target region held constant across the evidence contrast, as in the agent's arms; `bare_llm` beside them has no region); `twin_compiler_remarks`, `twin_hotspot_only` (E2-source); `twin_default` ↔ `default` (E3/E8/E9's reference twin — behaves exactly as `twin_full`, --budget being inert in a one-attempt twin, so E2's `twin_full` trials may be reused); `twin_llm_pragmas` ↔ `llm_pragmas_full_reprofile` (E3; the fast-refresh cells get no twin — the refresh is a pipeline cost lever with no model-only meaning); `twin_depth1`, `twin_depth2` (E8; **confound stated now:** a deeper twin can make more calls, as a deeper agent can); `twin_no_hotspots` (E9: the model is handed the region the unmeasured agent would be). E2-C, E2-D, E4 and E10 get none (N = 3 on 7 loops is too small for an interaction; E4's and E10's variables are the refresh and the speed check, which have no model-only meaning). test_arms block `D38-twins`: every twin resolves through its entry point to exactly its agent arm's configuration; `E2-twins`, `E2-source-twins`, `E3-twins`, `E8-twins`, `E9-twins`: the twins differ from each other in exactly the experiment's variable. **Plus, for every experiment and at no cost, the model + gate as a FILTER:** the gate's race stages and the harness's verification applied to the twins' programs afterwards, only what passes counted. **Pre-registered headline per experiment (H12): the pipeline × factor interaction** (E2: is (`full_b1` − `no_evidence_b1`) larger than (`twin_full` − `twin_no_evidence`) in FASTER rate, paired per loop?); every other twin comparison is secondary. **Expected before any twin runs:** the DiscoPoP-annotates twins ship many racy programs — DiscoPoP's own Do-Alls on class R were false positives the gate rejected in 21 of 22 cases (T0.11 audit); the `twin-run` check met one on its own test program (a scalar recurrence DiscoPoP reports as Do-All, inserted unchecked by `twin_dp`) — which is itself the measure of what the gate adds to DiscoPoP. Twins run IN THE SAME RUNS as their agent arms (same profile, so the same evidence text); E2's own runs are `full_b1`, `no_evidence`, `no_evidence_b1`, `twin_full`, `twin_no_evidence`, `twin_dp`, and its `default`, `bare_llm` and `discopop_gate` cells are E1c's — so `twin_dp` and `discopop_gate` are compared per benchmark over independent profile draws, not trial by trial. **Known difference from the agent:** each twin trial measures its own hotspots, as each agent trial does, so where two regions' measured times are close the agent and its twin may start at different regions; the first region each asked about is in its log. **Scope (the author, 24 Sep, confirmed the same evening: "yes keep the full plan"):** the full plan stays — the lean cut proposed the same day was not adopted. **Same agent commit:** `git diff 33673d7d -- discopop_agent/ DiscoPoP/ rtlib/ share/ discopop_explorer/ discopop_library/` is empty apart from the new `twin.py` and its checks, so E2 may read its `default` and model-alone cells from E1c | the author, 24 Sep |
| 2026-09-25 | finding | **Why DiscoPoP's evidence did not help in E2, and why about 35 of 90 trials fail in every agent arm: the model writes CORRECT rewrites, and they lose on SPEED after its turn is over (the author asked, 25 Sep: "why is the rest not achievable, why does the evidence not help … is something wrong?").** Every class-R agent trial of E1c and E2, followed stage by stage from its archived record and log (`tools/failure_funnel.py`, no model; `results/E02_evidence_feedback_model/analysis/why_trials_fail.md`): a rewrite passed the gate in 87–90 of 90 trials per arm, DiscoPoP found parallelism in it in 86–90, and a pragma for it passed every safety stage in 78–84 — **with or without DiscoPoP's evidence** (the no-evidence arms slightly higher). The dependences of a TSVC loop are in plain sight in three lines of code, so there was nothing for the evidence to correct. The speed checks then remove 21–29 trials per arm alike: Phase B finds no pragma that pays (5–17), Settle finds the finished program slower than the ORIGINAL (18–25; its paired ratio a median 0.53×, lowest 0.12×, 5 of 84 at ≥ 0.9× — real slowdowns, not noise), or the harness measures below 1.1× (3–8). The rewrites move more memory per repetition than the expert's (`s112`: snapshots of `a` and `b` every repetition, where the expert copies `a` once into the harness's buffer; with both of DiscoPoP's pragmas 0.86× the original, each pragma paying 1.29× and 2.07× against the rewrite). **Two defects of the agent let this happen.** (1) What the model is TOLD: with the speed check on, the agent's system prompt says DiscoPoP's pragma is checked for "speed against the same build on one thread" — it describes Phase B's check and leaves out the one that decides, Settle's and the harness's comparison with the original program; its contract says "extra work is fine within a constant factor — a second buffer, one more pass"; and the sentence that the rewrite "finally has to win" at full size exists only in the speed-off text. The twins and the model alone read "timed … against the original sequential program, and has to be faster" (D37/D38 recorded that swap as the harness's comparison for them, not as a gap in the agent's own text). (2) WHEN it is told: a pragma-free rewrite is not timed in Phase A, so the speed verdict comes in Phase B or at Settle, after the region's attempts are over — 26 of 39 and 28 of 35 of the unsuccessful trials of the three-attempt arms made one model call, which is also why three attempts did no better than one (H5b). T0.13 bounds these arms at 80 of 90 (`s331`, `s341` need a pragma DiscoPoP cannot write); they reach 48–55. One loop where the evidence hurt: on `s244` it led the model to a wrong or unparallelizable rewrite (one attempt: 0 of 5 with evidence, 4 of 5 without). **The speed check itself was right** — the arms were equal before it, and what it removed was slower than the original. **Data:** all 540 trials are archived; the text of the model's requests was never logged (the agent writes only "Assembling evidence"); the first request of every trial can be rebuilt from the runs' profiles, kept on the server | Consequences: E2's "the evidence adds nothing on TSVC" holds for the agent as it ran; H1 and H13 stand; the reach comparison with the model alone in E1c and E2 was biased AGAINST the agent (only the agent was not told the deciding criterion). **Proposed, for the author — D40:** the agent's prompt states the criterion the twins read, and that a rewrite's extra passes are paid on every repetition (copy only what a loop-carried dependence forces; DiscoPoP's evidence names the arrays that carry none); the rewrite with DiscoPoP's exposed pragmas is timed against the original INSIDE Phase A (Settle's paired method, the set not each pragma), and a loss is reverted with its ratio and what the rewrite added as feedback, charged to the region's budget; every request text logged; a pilot on the variable loops before any rerun; E2's Sonnet cells held until then. **How the speed retry was lost (checked in git, 25 Sep, on the author's question "I thought if the speed test did not pass we try again"):** it existed — on 17 Aug (`cd6671e5`) Phase A ran DiscoPoP's pragma for the exposed loop through the full gate whenever no deeper pass would follow (`_verify_rewrite(validate_patterns=terminal)`), and "not faster" went back to the model as a `no_speedup` verdict with its own feedback; the two-phase rebuild of 22 Aug (`3657447b`), which moved every pragma insertion to Phase B so that inserted pragmas stop shifting the line numbers Phase A reads, set it to `False`, and the retry went with it; D22 (20 Sep) then turned the speed check on campaign-wide, where it only runs after the attempts. Under `--llm-pragmas` (E3) the retry still exists: the model's own pragmas are timed in Phase A's gate. D40's check is designed around that line-number constraint: it never writes a pragma into the file — it stages the rewrite with DiscoPoP's pragmas as text, times it in a temporary directory, and on a loss takes the existing revert path, which already restores the source, the profile snapshot, the runtimes and covered spans; the queue and the change log change only at commit |
| 2026-09-25 | harness | **Counting correction in `main_comparison_stats.py` (found while publishing E2's read-out; no trial re-run; no other experiment's numbers change).** Two slips in WHICH trials a rate counts: (1) a program that changed the code but carries no pragma (`changed-not-parallel`) was left out of every denominator — it is a delivered, judged program (correct, no gain), and when it runs slower than the original it is unusable (H13) like any correct program below 1/1.1; (2) a harness edit whose program did not build was ALSO counted as "did not compile" — unusable, inside the denominator — against the author's rule that a harness edit is its own row, never unusable (24 Sep). One rule now decides the three-way table and the H12/H5b interaction alike (`_with_verdict`, `_ships_slowdown`); before, they also disagreed with each other (the interaction left out a program that does not build). Affected trials, all E2 twins: `twin_full` `s243` rep 1 (no pragma, 1.04×), `s244` rep 1 (no pragma, 0.63× — unusable), `s331` rep 4 (harness edit that did not build — now only in the harness row); `twin_no_evidence` `s331` rep 2 (no pragma, 0.88× — unusable), `s112` rep 1 (does not build — now in H12's denominator too). Effect: `twin_full` race-free FASTER 15 of 89 (was of 88), unusable 73 (same count, other cases); `twin_no_evidence` 17 of 90 (was of 89), unusable 71 (was 70); H12 p = 0.70 (was 0.71; larger inside on 3 loops, on the twins on 6, 9 tied); H5b, H13 and every agent and model-alone number unchanged; E1c, E1 and E1-bare unchanged (no such trial). Five files of argparse error text, written into E2's analysis folder by a failed shell loop, removed. `test_scaffold.py` checks the counting rules (12 cases; the old code fails them). The H5b read-out gets its own headings (`--interaction-labels`): it reuses H12's difference of differences and had called `default` − `full_b1` "the matched twins" | A rate counts every program the arm delivered and nothing it did not; the author's rule on harness edits holds whatever else the program did |
| 2026-09-25 | plan | **D39 — the measurement harness stays in the benchmark's file (the author, 25 Sep: "so we can just keep them, no harm").** The question (the author): the file every model edits holds our measurement — for a TSVC loop 160 of 174 lines (sizes, data, initial values, perturbed input, digest, timing, `pb_mix`, `main`): the models read it, DiscoPoP profiles it (s313: 87 % of the dependence records, 117 task patterns over `main`), and dependences with an end in it reach the agent's evidence ("RAW on `a` from line 108", written by `init_array` before the loop). **Tried: packaging v4** (`prepare_tsvc.py --layout v4`, built and kept): the measurement in a header per loop OUTSIDE the package (`prepared/_harness/`, found by every build through CPATH — `tools/harness_include.py`), which DiscoPoP never instruments (it instruments only code inside `DP_PROJECT_ROOT_DIR`; hotspot detection the same) and no model's working copy holds; the file keeps TSVC's loop, `pb_mix`, one `#include` and `PB_MAIN(kernel)` (a macro, so `main` stays instrumented); the header's digest is checked before and after every trial. **T0.15 (`tools/harness_equivalence.py`, no model) — output identical in 33 of 33 loops** (digest on the shipped and the perturbed input, full dump). **DiscoPoP's measured dependences for the benchmark's own code identical** (s211: 28 = 28 records, keyed by line text). **But the explorer's verdict changes:** on `s211` (a true recurrence) it reports a Do-All on the loop AND on the repetition loop in 5 of 5 draws (Mac) and 3 of 3 (server, LLVM 20) whenever the program's code spans two files — even with everything instrumented and the arrays allocated in instrumented code; in the one-file layout it reports none in 5 of 5 and 3 of 3. In one file `doall_prevented.json` holds the dynamic RAW on `b` that blocks both loops; after the split it is empty, although the profiler recorded the same 9 RAW records. A DiscoPoP defect in how the explorer assigns call-path states to loop iterations when a program spans more than one file (bug report **B8**, the Fix 81/82 family). *Correction, same day:* moving `pb_mix` back into the file during this work was a misdiagnosis — the symptom is the same with it in or out. **Decision: the one-file layout stays** — it biases no comparison (every arm reads the same file; DiscoPoP's analysis is the one every run has used; no harness region or pattern is ever acted on, in any arm) and costs only time and tokens (s313: a 20 s profile instead of 5 s; ≈ 1,500 tokens per file read); the two-file layout would change DiscoPoP's results. **With it:** H13 counts only failures of the code under test (a harness edit has its own row); Fix 97 — every arm told about the harness in the same words, the agent's gate refusing a harness edit with a free retry — is in the agent for packages that list protected lines (v4); for the one-file packages it is built next, for E3 onward (the measuring functions named by the package, the same sentence the model alone already gets, the gate protecting those functions and every call to them); the rest of E2 runs on the agent its A+B ran on; the two trials that edited the harness (`e1c_a` s313 default, `e2c_ab_4` s331 twin_full rep 4) are repeated. **B8 is fixed before the application benchmarks** (LULESH, NPB, PolyBench's project layout — multi-file by nature; whether T0.8's PolyBench equivalence holds under B8 is checked then) | the author, 25 Sep |
| 2026-09-25 | finding | **The agent's model is never told which functions measure the program; the model alone's is (found by E1c class A).** In `e1c_a` the agent's `s313` program inlined the harness's `pb_mix(nl)` call into the kernel ("to make array dependencies explicit to profiler") — output identical, so the gate kept it, and the harness scored it SCAFFOLD_MODIFIED, an unusable program under H13. The mirror prompt of the model alone names the measuring functions ("Do not change these functions — they set up, time and print the program: …", from the package's `exclude_functions`); the agent's request does not — `--exclude-functions` only keeps the agent from ASKING about regions inside them, and the contract forbids touching I/O, not the timer or the perturbation — and the twins use the agent's request, so they lack it too. **An asymmetry in the model alone's favour**, rare so far: 1 agent trial on the clean packages (`e1c_a` `s313`), 3 in the pilots (`pilot2`, `local_obs1` `seidel-2d`, `pilot4` `md`), against 1 of the model alone (`e1_bare_a` `s243`). Stated as a threat for every read-out that includes H13; the comparison agent vs twin (H12) is not affected (neither is told). **Proposed, not built (the agent is frozen while E2 runs, D34):** the agent's request names the measuring functions exactly as the mirror prompt does, and the gate rejects a candidate that changes them (the harness's `scaffold.check`, run inside the gate). The author decides | E1c class A, 25 Sep |
| 2026-09-24 | plan | **H13 — trust over the model alone, pre-registered (the author).** "If the model-only approach produces a broken program we should record that as a result, because that is an advantage we have over the model alone, as our design tries to produce unbroken programs." Unusable = BROKEN, racy, correct but slower, or **a program that does not compile** (the harness built the original and failed only on the final program) — **failures of the code under test only.** *Corrected 25 Sep (the author: "what we wanted to see as broken or do not compile … only if the changes made the code we are testing on"):* a program that changed the HARNESS code (SCAFFOLD_MODIFIED) was first counted as unusable too; it has no valid measurement and is no failure of the code under test, so it has its own row, is left out of every rate and of H13, and is never counted as unusable — for every arm alike. E1-bare's "of 88" was 90 minus `s244` rep 2 (did not compile — now counted: 34 unusable of 89) and `s243` (touched the harness — its own row). The same rules apply to every arm. In every experiment the agent arm ships fewer UNUSABLE programs — BROKEN (wrong output), racy (race_check.py: TSan or the schedule matrix), or correct but slower than the original (< 1/1.1) — than the model alone and than its matched twin (D38). Every unusable program a model-only arm ships is a result, listed by case with the check that would have stopped it, never dropped as a failed trial. Test: per benchmark the model-only arm's unusable rate minus the agent's, paired Wilcoxon over benchmarks, one-sided (agent fewer); totals with Wilson intervals. Built into the three-way read-out (`main_comparison_stats.py --three-way AGENT --bare {bare_llm | twin_*} --races …`; an unusable column per benchmark). Checked on E1-bare's data: the read-out reproduces its published numbers (FASTER 58, race-free 53, BROKEN 17, slower 12; unusable 33 of 88 before, 34 of 89 with the non-compiling program counted and the harness edit in its own row), and H13 there — descriptive only, E1-bare is 'hint in source' (D36) — has the agent shipping fewer on 11 loops, the model alone on none, 7 tied (p = 0.0005). **Registered while E1c ran and before any of its results was read** (its progress counts and one trial's status — a model-alone program that did not compile, `s254` rep 5 — had been seen); E1c is its first test | the author, 24 Sep |
| 2026-09-24 | harness | **The T0.11 probe of TSVC's indirect-addressing loops is packaged (the author's decision 8).** Eight loops — `s4112`, `s4113`, `s4114`, `s4115`, `s4117`, `s4121`, `s491`, `s353` — whose iterations conflict or not depending on the VALUES of TSVC's index array `ip` (a fixed permutation within blocks of five, TSVC's `common.c`): DiscoPoP observes those values at run time; a model can only derive them from the initialization, which it may read. `s4116` is left out (it needs TSVC's 2-D arrays, which this packaging does not build). `prepare_tsvc.py` gains per-loop `pre` (the argument declarations TSVC passes through `func_args`, with the values its `main` passes: `ip`, `s1 = 1.0`, `n1 = 1`) and `globals_` (TSVC's `f`, the index array `pb_ip` — a `pb_` name, so the scaffold check protects it); the source says nothing about the array's structure (D36). All 8 validate; the existing 25 packages are byte-identical; `test_integrity` passes (79 packages, 226 sources). **Expected, written before any measurement:** DiscoPoP alone parallelizes most of them (class A), because the permutation leaves no conflict to observe — which would make them a place where DiscoPoP knows what the model can only guess, not a class-R tier. Next, no model, when the server's lanes are free: T0.1 sizes, then T0.11 × 3 draws (`t0_11_probe_*`) | the author, 23 Sep, decision 8 |
| 2026-09-24 | plan | **The clean redo is split so the author's question is answered first: E1-clean (group E1c) runs before E2's other arms.** The author: "I want to see the results of the latest version of the agent against the model alone on E1." No such comparison exists yet — both arms of E1 and E1-bare saw the hint (D36). E1c = TSVC class R, 18 loops × `discopop_gate`, `default`, `bare_llm` (the mirror prompt, D37) × 5, Haiku, on four lanes (`e1c_r_1`–`4`), then the controls: class A × 1 and class D × 3 × the same three arms (`e1c_a`, `e1c_d`; the model alone on true recurrences, decision 3). E2 A+B then adds `full_b1`, `no_evidence`, `no_evidence_b1` on the same agent commit and reads its `default` and model-alone cells from E1c — so the agent must not change between the two | the author, 24 Sep |
| 2026-09-23 | plan | **D37 revised the same evening: the model alone gets the AGENT's instructions, minus DiscoPoP, minus the gate during the run, minus feedback ("the mirror").** The author, on the minimal prompt: "it is not fair — it should get the same prompt as the agent but without the information provided by DiscoPoP or our gates … it should only differ in the pipeline, and we should be able to judge it at the end — whether the rewrites are semantically correct, faster, and everything — but not during the run through the gates with feedback." **What it gets** (the agent's own text, assembled from the agent's prompt code, in the mode where the model writes the pragmas): the contract, the OpenMP loop rules, the pragma forms, "what we ask of you" (DiscoPoP's sentence removed), the list of checks — stated as what judges the finished program —, the plan request, the checklist. **What it does not get:** DiscoPoP's role, profile, evidence and "what we give you"; which region to work on (the whole program, and the functions it must not touch because they measure it); any check or feedback during the run; a second attempt. **How it is judged — afterwards, as the agent's final program:** the harness's verification (output byte for byte on the shipped and a perturbed input, repeatability at fixed threads, speed at 6 and 12 threads), then the gate's race stages over every parallel program it produced (`race_check.py`). **Found on the way:** E1-bare's own task line ("splitting a loop, adding a buffer, reordering statements") is in no prompt of the agent's — the old baseline had a hint the agent never had. The earlier minimal prompt stays as arm `bare_llm_minimal` (`d36_hint_check` ran it), the old one as `bare_llm_contract`. Feature check `bare-llm`: the shared passages byte-identical to the agent's | the author, 23 Sep |
| 2026-09-23 | harness | **The author approved both time levers ("we could do these 2").** (a) **The agent's explorer limit per benchmark:** the harness passes `--explorer-timeout` = max(60 s, 10 × this benchmark's own successful explorer run, recorded as `explore_success_s` in `profile.json`); TSVC → 60 s (its runs take ≈ 4 s; the longest legitimate run of any campaign benchmark over 166 draws took 33 s), a large program scales (LULESH at `-s 5`: 16 s → 160 s), nothing measured → 600 s as before. A stalled draw is repeated either way, so no verdict changes; the harness's own first explorer run of a benchmark keeps 600 s (nothing to scale from). In E1 it would have cut ≈ 3.9 of 13.2 h. (b) **Four lanes of 12 cores instead of two of 24:** `server.sh run --node N.H` pins a job to half H of node N's cores with node N's memory (`--node N` still takes the whole node). Used only after T0.4 is repeated at four lanes under campaign load (`t0_4_four_lanes`, no model) and shows the 1.1× threshold still resolvable with the median of 5; the agent's own timing then uses 12 threads instead of 24, whose effect on Phase B's verdicts was measured nil (`e1b_marginal_replay`: the thread-count hypothesis refuted). Neither changes an experiment's arms; both are stamped per trial (`agent_cmd`, the launcher log's `== lane:` line) | the author, 23 Sep |
| 2026-09-23 | archive | **The clause replay behind Fix 91, re-run and archived (`clause_replay_fix91`, Mac, no model).** Its counts had been quoted in the agent's `docs/FIXES.md` ("25 found, 11 reconstructible, exactly 4 change") without a tracked copy. Re-run on every archived clause-stage rejection: 25 found; **8 flip to accepted** — `s281` reps 2–5 in E1 (Fix 91's cases, already replayed into E1 under v2) and 4 in pre-campaign runs (`pilot2`, `local_obs1`: `private(j)` on a counter a later loop nest re-initialises, the Fix 63 class; no reported result depends on them) —, 3 stay rejected, 14 cannot be rebuilt (no original or log kept with them; E10's 7 are among the ones not flipped). The earlier "11 reconstructible" was a different, unarchived run | every number the record quotes must have a tracked copy |
| 2026-09-23 | result | **T0.9 re-run after D29 (`t0_9_refresh_d29`, Mac, no model): 11 of 18 comparisons reach the full profile's conclusions, 7 produce a suggestion the measured profile does not support** (18 Sep: 8 / 8 unsupported / 2 lost). The reading stands: the fast refresh maintains the queue, it does not decide pragmas; the agent takes one full re-profile before Phase B whenever its profile holds carried-forward data. Repeated on the server (LLVM 20) before E3 | §5s: owed before E3 |
| 2026-09-23 | measurement | **Where a trial's time goes (E1, TSVC class R, `default`, 90 trials, 13.2 h):** waiting for the model 4.2 h (32 %); **DiscoPoP's explorer stalling 4.3 h (33 %)** — 26 stalls in 18 trials, each waited out for 600 s before the draw is repeated; the agent's own checking and profiling 3.0 h (23 %); the harness's verification 1.6 h (12 %). Mean 8.8 min per trial, 5.9 min without the stalls. Two levers, proposed to the author, not applied: the explorer limit 600 s → 60 s (166 draws: median 3.5 s, longest legitimate 33 s; a stalled draw is repeated either way, so no verdict changes), and 4 lanes of 12 cores instead of 2 of 24 (T0.4 measured 2 lanes at campaign load, 4 lanes not yet; the thread-count hypothesis for Phase B's verdicts was refuted in `e1b_marginal_replay`) | the author: "why do the experiments take so long?" |
| 2026-09-23 | plan | **D35 — the main comparison is THREE-WAY: DiscoPoP alone · DiscoPoP + agent · the model alone; the sequential code is the reference** (extends D19). Every experiment carries a model-alone reference (`bare_llm`: the same model, no DiscoPoP, no gate, one attempt) on the same benchmarks with the same model. **Where it comes from:** TSVC class R with Haiku — E1-bare's 90 trials, for E2, E3, E4, E8 (the bare arm never runs the agent, so agent v2 does not touch it; same model id, loops, ×5, verification); Sonnet (E2 Part A, E3 if Sonnet enters it) — a new `bare_llm` × `claude-sonnet-5` run on TSVC class R ×5 in the Sonnet phase (90 trials, ≈ 15–20 USD-eq); LULESH (E6) and NPB-C (E11, beside RepoOMP's released Claude Code / Codex outputs) — a `bare_llm` arm in their runs. **Read-out** (RUNBOOK 0a): the three arms against sequential (verified parallel, FASTER, race-free FASTER — `race_check.py` on the bare arm's programs as a standard step —, BROKEN, slower shipped); agent vs DiscoPoP alone (D19 verdicts); agent vs model alone (per-benchmark FASTER counts paired, Wilcoxon; unusable programs counted); the model alone's speed only over its correct trials. E2's arms then form a ladder over the model alone: `no_evidence_b1` adds the gate and DiscoPoP's pragmas, `full_b1` DiscoPoP's evidence, `default` the gate's feedback. Owed before E2 A+B is read out: `main_comparison_stats.py` / the report emit the three-way table and the paired agent-vs-model-alone statistic | the author, 23 Sep: "the main comparison is between DiscoPoP alone and DiscoPoP + the agent; now we should also add the model alone as main comparison too, so three cases, and the sequential code as a reference" |
| 2026-09-23 | plan | **E2-C/E2-D at N = 3; E2-C without the `feedback` group; E2 carries DiscoPoP alone; Parts A+B launched (the author).** (1) N = 3 per (loop, arm) on the seven loops: 21 trials per arm, which resolves only large effects (a 95 % interval of about ±20 points at a 50 % rate; N = 5 would give ±16 for 224 more trials) — as registered in D16, screening, effect sizes, no tests. (2) `ev_without_feedback_b1` and `ev_only_feedback_b1` dropped before any E2-C trial: at `--budget 1` a region gets one attempt, and on a first attempt the `failure` section renders one fixed line ("Why this region is here: DiscoPoP found no applicable parallelism pattern"; `llm/render.py`), a build-fix retry aside — so one arm would be `full_b1` minus a sentence and the other `no_evidence_b1` plus one. What the gate's feedback is worth is Part B's question (budget 1 vs 3, H5b). E2-C: five groups, 10 arms, 210 trials (was 12, 252); the two arms stay in `arms.json`, marked retired. (3) `discopop_gate` joins E2's experiment block (D19; on v2 D33 also acts at `--budget 0`, so DiscoPoP alone is re-measured, not taken from E1); `test_arms` passes. (4) **Correction:** E2's size was first written as "≈ 77 lane-hours"; 1,056 trials × 8.8 min is ≈ 155 lane-hours (77 h is the wall-clock on two lanes). E2 is now ≈ 1,014 model trials, ≈ 150 lane-hours, about 3 days on two lanes, ≈ 150 USD-equivalent. (5) **Parts A+B launched** as `e2_ab_a` (node 0: `s112 s121 s1213 s127 s211 s212 s241 s243 s244`) and `e2_ab_b` (node 1: `s252 s254 s255 s281 s291 s292 s293 s331 s341`) — the E1-bare split — × `discopop_gate`, `default`, `full_b1`, `no_evidence`, `no_evidence_b1` × Haiku × 5, threads 6/12, 5 repeats: 450 trials (360 with a model), ≈ 55 lane-hours, ≈ 28 h | the author, 23 Sep: "N=3, drop the feedback arms, launch A+B" |
| 2026-09-23 | plan | **E2's launch order fixed (the author):** Parts A+B on Haiku first (`discopop_gate`, `default`, `full_b1`, `no_evidence`, `no_evidence_b1` — they carry H5 and H5b), then Part A's Sonnet cells, then the evidence-source arms (`compiler_remarks_b1`, `hotspot_only_b1`), then Part C, then Part D; if usage binds, Part C is cut first (the registered cut order). Still open before C/D: N | the author, 23 Sep: "i agree on the launch order" |
| 2026-09-23 | harness | **Two defects found by reading the E2 smoke's logs, both in what the harness REPORTS, neither in what the agent does.** (1) The per-trial field `phase_b_deferred` (D33, added with agent v2) counted every `└─ DEFERRED` line — but Phase A prints the same marker for a region DiscoPoP already has a pattern for ("deferred to Phase B"). `e2_smoke_a`'s `default` trial would have recorded 2 D33 deferrals where its log has none; replayed on `e1_smoke5`'s eight trials the old count gives 0–6 on trials with no D33 deferral (e.g. 6 on `2mm` DiscoPoP alone). Now it counts Phase B's own marker, `└─ DEFERRED (slower alone)`. No archived number was affected: the field exists only from v2 and no read-out used it. `rescore` now re-reads each trial's agent log with the current parser and updates the facts the trial already records, keeping the old values in `log_facts_history` — so a counter fixed after a run reaches that run (tested on a copy of `e1_smoke5`: only `phase_b_deferred` changed). (2) The launch printout of the settings a run's arms differ in left out `--evidence-file` (added per benchmark, outside the arm's flags) and `--prompt-omit`: `compiler_remarks_b1` and `no_evidence_b1` were printed as identical, and E2-D's arms would have printed "identical configuration". Both now listed. Display only: `test_arms.py` and the check against the agent's own parser always saw them. (3) `tools/default_arm_ceiling.py` (T0.13) takes `LOOP=FILE` to hand the pipeline another restructuring than the expert's: the smoke's model draws on `s121` copied the array with `memcpy` (nothing for D33 to combine) and DiscoPoP's draw on `s281` reported a pattern on only one half of the split (nothing for Fix 91's clause stage to judge), so v2's two new Phase B paths were run end to end without a model on E1's own rewrites — `e2_v2_paths`: the 11 programs of `e1b_v2_sources` with their pragmas stripped, `--budget 0`, on the server. mypy 0, `test_arms`/`test_integrity`/`test_scaffold` pass | the RUNBOOK's step 0 — read the smoke's logs to the end, not the outcome line |
| 2026-09-23 | plan | **E2 pre-flight on agent v2 (the author's go, 23 Sep evening): three smoke runs, registered before launch.** `e2_smoke_a` (`tsvc/s121`, NUMA node 0) and `e2_smoke_b` (`tsvc/s281`, node 1): `discopop_gate`, `default`, `full_b1`, `no_evidence`, `no_evidence_b1`, `compiler_remarks_b1`, `hotspot_only_b1` × Haiku × 1, threads 6/12, 5 repeats — every arm of E2 and E2-source once, plus DiscoPoP alone (D19). Then `e2_smoke_sonnet` (`s121`, `s281` × `full_b1` × `claude-sonnet-5` × 1): Sonnet has never run through the harness on the server. **What each must show, read to the end of the log (the Fix 86 lesson):** v2's new paths on the benchmarks chosen for them — on `s121` a rewrite whose safe DiscoPoP pragmas are slower alone reaches `phase_b_deferred` and the joint set is judged (`phase_b_joint_kept`); on `s281` the clause stage accepts `private(x)` on both halves of the split (Fix 91); in every model arm `floor/floor.log` exists and `dp_floor` is recorded (D32), in `discopop_gate` it is skipped (`--budget 0`) — whether a draw exercises D33/Fix 91 is the model's, so a smoke that does not is reported as not exercised, not as passed; the two evidence-source arms, which have never called a model: `compiler_remarks_b1`'s file generated on the server's clang-20 under `<run>/evidence/` and non-empty, `hotspot_only_b1` and `no_evidence*` with the prompt sizes their sections imply (`llm_usage.jsonl`; the prompt text itself is checked offline by the feature check `prompt-ablation`); budget-1 arms make one Phase-A call per region. **DiscoPoP alone is re-run on v2 in E2, not taken from E1:** D33 also changes Phase B for `--budget 0` (a safe DiscoPoP pragma slower alone is now judged in a set), so E1's 0 of 90 is v1's number. Not yet decided (the author, before the launch): N = 3 for E2-C/E2-D; the launch order | RUNBOOK checklist step 0 (one smoke trial per arm, read the logs) before any E2 trial exists; D34 (E2 on its own v2 `default` arm) |
| 2026-09-23 | result | **E1 under agent v2, by replay, verified by the harness (`e1b_v2_verify`): TSVC class R FASTER in 55 of 90 trials** (v1: 44; the model alone, race-checked: 53 of 88), 0 unsafe. The 13 programs E1 would have ended with under v2 — the 7 D33 recovers (the rewrite with all its safe DiscoPoP pragmas), the 4 `s281` repeats Fix 91 recovers (both halves annotated), and 2 controls — rebuilt from the archived patches without a model (`checks/e1b_v2_sources/`) and put through `verify-source` with E1's settings: **11 of 11 recovered programs FASTER, 1.49–3.25×**, output identical to the original on both inputs, stable at fixed threads; control `s127` rep 1 FASTER 4.48× (E1: FASTER), control `s121` rep 4 parallel-not-faster 0.14× (a slow rewrite, correctly not recovered). **Race-checked too (`e1b_v2_race_check`, the gate's `validate(mode="safety")`, TSan with archer, server): 13 of 13 clean** — `verify-source` judges output and repeatability, not races, so the combined sets were also put through TSan and the schedule matrix. No other E1 trial changes: every other D33-deferred pragma was alone in its trial (dropped as before), Fix 91 flips only `s281` reps 2–5, Fix 92 has no effect on E1's agent (no agent trial called the OpenMP runtime; it changes only the model alone's `s341` rep 5), and D32 changes nothing on class R (DiscoPoP alone keeps nothing in 90 of 90); on class A it makes `vpvtv` and `s000` `equal` (DiscoPoP's archived program shipped), `s313` stays `better`. Rates only: the paired statistics are recomputed on E2's own `default` arm, which runs on v2 | D34's comparison rule — E1 is not rerun |
| 2026-09-23 | agent | **Agent v2 = D33 (Fix 93), D32 (Fix 94), Fix 91, Fix 92 — built, commit `ad57f134`.** Phase B defers a safe pragma that is slower alone and judges the deferred ones as a set (backward elimination, one change-log unit); the floor is DiscoPoP's own gated program, built before Phase A and shipped if the agent's is slower; the clause stage no longer counts a later loop that writes the name first as a read; builds without OpenMP get its flags when the program calls the runtime. No new switch — every arm runs the same agent — and what happened is recorded per trial (`phase_b_deferred`, `phase_b_joint_kept`, `dp_floor`). Feature checks `phase-b-joint`, `dp-floor`, `clause`, `omp-runtime` (each fails on the old code); suite 42 passed, 1 skipped (the known explorer draw); mypy 0. Agent `docs/FIXES.md` 91–94 | the author: "we can do D32 and D33 … do 1 and 2 and 3" |
| 2026-09-23 | plan | **D34 — the agent may change between experiments, and every change is documented** (the author: "it is fine to apply the changes and describe how we found them in the thesis; everything just needs to be documented and the artifacts and the docs updated"). A change is allowed when (a) it comes from a recorded finding, (b) it is replayed on archived trials before it is merged, (c) every run stamps the agent version it used (the manifest's `agent_git.head` and `dirty_sha256`), and (d) the thesis tells the sequence: found, measured, fixed. **Comparing without rerunning** (the author: "i do not prefer to rerun the exp for every change"): each experiment runs once, on a stamped agent, and its arms are compared inside it; a later change is evaluated on earlier experiments by replaying the CHANGED stage on their archived candidates — deterministic, no model — and only if that cannot answer the question is the affected part rerun. The model's own answers are never replayed (each was written against the old gate's feedback). **E2 runs its own `default` arm** on v2 (the author), not E1's. **Correction:** this record said on 22 Sep that "the agent stays as it is from here to E11"; that was my generalisation of the author's decision not to build D31-b, not the author's decision | the author, 23 Sep |
| 2026-09-23 | harness | Per trial: `phase_b_deferred`, `phase_b_joint_kept`, `dp_floor` (read from the agent's log, also in `trials.csv`). `tools/clause_replay.py`: every archived clause-stage rejection judged again by the current rules — the replay behind Fix 91 | D34 (c), (b) |
| 2026-09-23 | plan | **D33 proposed — Phase B measures a rewrite's safe pragmas TOGETHER before dropping any.** *(Approved by the author and built the same day as Fix 93 — rows above.)* Today Phase B times each pragma alone against the state before it and drops it if it does not pay; when a rewrite splits a loop into two or three, each pragma alone can lose while all of them win. Proposed: measure the set of safety-passing pragmas together against the state before them, then remove one at a time only while the set still pays (backward elimination). Replayed on E1 (`e1b_marginal_replay`) it recovers 7 of the 18 trials the check dropped (the agent: 51 FASTER of 90 instead of 44, on the agent's own measurement) and changes none of the 11 correct drops. The agent is frozen until E11 (the author, 22 Sep); **the author decides** whether D33 enters before E2 — then E2's `default` differs from E1's and is compared within E2 only — or after E11 | the author asked why the model alone reaches more; the replay answered it |
| 2026-09-23 | finding (gate, E7) | **The gate's clause stage rejects a correct `private(x)`** — `s281`, E1 reps 2–5: DiscoPoP's pragma on the first half of the agent's `LEN/2` split was refused because "the loop writes `x` and later code reads it"; the only later reads are in the second loop, each after a write in the same iteration, and nothing reads `x` after the loops. With one half parallel the program is 0.63–0.97× the original, so the agent lost `s281` in all five repeats although its model wrote the right rewrite every time (the model alone, writing the same clause, is TSan-clean and 3.0×). A labelled false reject for E7; not fixed (agent frozen) | `e1b_marginal_replay` |
| 2026-09-23 | correction | **`e1_r_a`/`e1_r_b` (§7) said "the Phase B marginals were not wrong either" and that "every `s121`/`s281` trial" copies the array.** Both hold only in part. Each marginal is right for the pragma measured ALONE, but in 7 trials the set of pragmas pays where no single one does (`e1b_marginal_replay`); and `s281`'s rewrites are copy-free index splits, `s121`'s reps 1, 2, 5 loop copies — only `s121` rep 3 used `memcpy`. The entry stays as written; this row and the E1-bare §7 entry correct it | measured the same afternoon |
| 2026-09-23 | result | **Race check of the model alone (`e1b_race_check`): 53 of its 58 FASTER programs are race-free; the gate would have stopped all 17 of its wrong ones.** Every `bare_llm` program through the agent's own `validate(mode="safety")` on the server (clang-20 with archer), the agent's 46 parallel TSVC programs as control — 46 of 46 clean. Not clean: `s293` reps 1–4 (a pragma on `a[i] = a[0]`: a data race, benign in effect) and `s341` rep 5, which the gate cannot judge (it calls the OpenMP runtime; the gate's first compile does not link it — a blind spot, E7). BROKEN caught by TSan 9, output 7, schedule matrix 1. Race-checked, the model alone is FASTER in 53 of 88 (60 %), the agent in 44 of 90 (49 %) | the author: "run the race check on the bare programs" |
| 2026-09-23 | harness | **Two no-model tools.** `tools/race_check.py`: an archived program (original → final) through the agent's own gate, `validate(mode="safety")`, called directly so the macOS barrier re-run cannot mask a race; manifest records whether archer was found. `tools/marginal_replay.py`: Phase B's `measure_marginal` replayed on states rebuilt from a trial's archived patches (only the Phase-A candidates the log kept — `candidates.jsonl` does not record reverts), per thread count, plus each rewrite with all its safe pragmas against the original. Both registered as checks of E1-bare before they ran | the race check and the question why `default` reaches less |
| 2026-09-23 | result | **E1-bare complete (§7 `e1_bare_a`, `e1_bare_b`): the same model alone ships a wrong program in 17 of 88 trials; the agent in 0 of 90.** TSVC class R, 18 loops × 5, Haiku 4.5, no DiscoPoP, no gate: verified parallel 71 of 88, FASTER 58 of 88 — MORE than the agent's 44 of 90 (the plan expected the opposite) — and BROKEN 17, `worse` 12. The gap in reach sits on `s281`, `s331`, `s121`, `s244`, each with a named cause (index splitting vs a copy; a max reduction DiscoPoP cannot write; a parallel vs a sequential copy; a dead store); E1's gate rejected 23 wrong rewrites of the agent's model, on seven of the nine loops where the model alone shipped its 17. What the pipeline adds over the model is trust, not reach; which of evidence, gate, feedback or pragma authorship costs the four loops is E2's and E3's question. Owed, no model: the gate's race stages over the model alone's 71 parallel programs (its FASTER are output-checked, not TSan-checked) | the author's go, 22 Sep; the read-out pre-registered in the E1-bare row of §5s |
| 2026-09-23 | harness | **The two main-comparison figures show every arm of a combined read-out.** `fig_verdict_matrix` drew only the FIRST arm (E1-bare's squares were missing) — now one panel per arm and model on shared rows; `fig_vs_discopop_alone` cut the first panel's counts off with the second — now the panels are spaced for them. Both name a `bare_llm` arm's trials "model alone", never "agent", from `arms.json`'s `runner` (`figures._who`). A single-arm figure is drawn as before (E1's re-rendered, identical) | the E1-bare read-out combines `default` and `bare_llm` |
| 2026-09-23 | archive | **`agent/results/` is reorganized by experiment, from a registry (`results/campaign.json`), and a check enforces completeness.** The author: "the results folder is messy, you do not get what is for what — same for the thesis material … I need a report per experiment … a clear rule or handover so things are not forgotten". 68 flat run folders become one folder per experiment or instrument (`E01_main_comparison/`, `E01b_bare_llm/`, `E10_speed_check/`, `E11_repoomp/`, `T0_instruments/T0.01_sizes/` … `T0.14_reference_acceptance/`, `audit_benchmark_suitability/`, `pilots/`, `harness_checks/`, `logs/`), each with a generated `REPORT.md` (question, status, result, what the folder holds, the runs, and this record's own entries for them), `analysis/` (was `results/_analysis/<name>`), `exhibits/` (was `agent/thesis_material/<name>`), `runs/`, `checks/`, `preflight/`, `superseded/`. Run ids are unchanged. `results/README.md` is the map, `INDEX.md` lists every run by experiment with purpose and status (valid, superseded, void), `EXHIBITS.md` every case study with the claim it supports. `tools/campaign.py check` fails on: a folder outside the layout, an unregistered or unarchived run, an archive that disagrees with its `ARCHIVE.json`, a run this record never names, a finished experiment without its report or read-out, an exhibit without the main comparison, uncommitted results, a fetched run never archived. Its first run found six archived runs this record named only implicitly or not at all, named here: `e1_smoke2` (E1 pre-flight smoke 2, the memory-limit prompt), `t0_11_classes_b` and `t0_11_classes_c` (T0.11 draws B and C, recorded as `t0_11_classes_a/b/c`), `integrity_smoke_local` (the no-corruption guarantees of §5j on the Mac), `local_obs1_md` (the observed run on `md`, part of `local_obs1`), `vs_polly` (the first Polly baseline through `verify-source`, one kernel, 16 Sep). Five hand-copied study folders got the provenance file every archive has (`campaign.py adopt`). `archive`, `plots`, the statistics and the exhibit tool find runs through the registry, and `plots` now falls back to the archive, so every figure can be regenerated from a fresh clone | the author's request; the RUNBOOK's definition of done now ends with `campaign.py check` passing |
| 2026-09-23 | archive | **Three things the record cited lived only in git-ignored folders; now tracked.** E1's combined read-out (`agent/analysis/e1_all`, the source of every E1 number) → `results/E01_main_comparison/analysis/`; T0.1's TSVC measurements, cited as `results/T0_instruments/T0.01_sizes/runs/t0_1_tsvc` but never archived (the sizes derived from them were always tracked in `kernel_sizes.json`) → `results/T0_instruments/T0.01_sizes/runs/t0_1_tsvc/`; the one-repository smoke (`move_smoke`, cited by D20) → `results/harness_checks/runs/move_smoke/`. Checked in the other direction too: every archive, exhibit and reference has the same file count on disk as in git. Git never touches ignored files in a merge or a checkout, which also means the server's generated packages (`prepared/`) are NOT updated by a sync: the server has no LULESH package yet, so its pre-flight starts with `prepare_apps.py lulesh --validate` from the merged recipe | the author: "is the file in the git ignore left when merging?" |
| 2026-09-23 | campaign | **The work branch is merged; E1-bare is running.** `e1-readout-e2-prep` fast-forwarded into `agentic_DiscoPop` at `cf0d5d96` after the merge gate: the agent's feature suite 40 of 40, harness type check and tests, `test_arms.py` (all arms, all experiments); `default` and `discopop_gate` resolve exactly as at E1's `00d4594f` except three new options that are inert when unset (`evidence_file`, `external_evidence`, `prompt_omit`) — and with them unset the prompts are byte-identical by construction (empty parts are filtered; the checklist is the same string, factored). Server synced, parity OK. E1-bare launched 04:59 UTC: `e1_bare_a` (node 0: `s112 s121 s1213 s127 s211 s212 s241 s243 s244`) and `e1_bare_b` (node 1: `s252 s254 s255 s281 s291 s292 s293 s331 s341`), `bare_llm` × 5, Haiku 4.5, `--threads 6,12 --repeats 5` as E1; the harness's verification code is unchanged since `00d4594f`, so the bare arm is judged exactly as E1's trials were. The server checkout stays at `cf0d5d96` until both lanes end | the author: "are we going to move back to our branch?" — yes, from here on all work is on `agentic_DiscoPop` |
| 2026-09-23 | agent | **Fix 90 reverted before it ever ran.** Replayed on E1's own trials before the merge, its rule (do not send a region to the model when every outermost loop inside it carries an applicable DiscoPoP pattern) would have blocked the model on **11 of 18 class-R TSVC loops, including all five 5-of-5 winners** (`s127 s254 s291 s292 s293`) and `vpvtv` only through the loop, not through the function. In class R DiscoPoP reports patterns on those loops that are false positives the gate rejects; a rule on DiscoPoP's patterns cannot tell class R from class A — only the gate can. Code and feature check removed; the only agent change since E1 is Fix 89 | found by replaying the rule on archived trials before merging, which is now the rule for any change to what reaches the model |
| 2026-09-23 | result | **E1 complete (§7 `e1_a`, `e1_d`): 290 trials, 0 unsafe in 288 with a verdict.** Class D (must-decline): 12 of 12 correctly declined; **56 wrong rewrites of true recurrences and 11 racy pragmas caught by the gate**. Class A (no-harm, ×1): `s313` better (1.15×), `vpvtv` worse (0.58×), `s000` lost — one mechanism: the model is called on an enclosing region whose hot loop DiscoPoP already covers, and Settle compares the result with the original, never with DiscoPoP's own program | the pre-registered controls; class A is n = 3 and the mechanism, not the rate, is the finding |
| 2026-09-23 | plan | **D32 proposed — a floor at DiscoPoP alone.** *(Approved by the author and built on 23 Sep as Fix 94 — rows above.)* The agent first computes DiscoPoP's own gated program (as `discopop_gate` does); Settle keeps the agent's program only if it beats that one in the paired measurement, else DiscoPoP's. No effect on class R (DiscoPoP's program is the original in all 90 E1 trials); makes `lost`/`worse` impossible on class A and on the applications up to noise. Needed before E6 (LULESH, expected class A at program level) and E11; not before E2/E3/E8. The author decides | the rule of the campaign is DiscoPoP alone vs DiscoPoP + agent; without a floor, "+ agent" can subtract |
| 2026-09-22 | plan | **E1-bare goes ahead (the author).** `bare_llm` on TSVC class R, 18 loops × 5; compared with E1's `default` trials (same benchmarks, sizes, verification, model). It answers what the pipeline adds over asking the same model: the bare arm's BROKEN count is what the gate prevents, its FASTER count is what DiscoPoP's evidence and the gate's feedback add. Smoke on the Mac: `s211` restructured correctly (output exact on both inputs, 3 pragmas), `parallel-not-faster` at 4 threads. **D31-b is NOT built** (the author): the agent stays as it is from here to E11, with Fix 89 as the only change since E1 (Fix 90 was reverted the next morning, row above); the unused budget in 15 of 90 trials is a recorded limitation | the merge of the work branch into `agentic_DiscoPop` follows class D; merge gate passed: `default` and `discopop_gate` resolve identically on both branches except the three new, inert options (`evidence_file`, `external_evidence`, `prompt_omit`) |
| 2026-09-22 | measurement | **The expert restructurings are 1.00–2.30× SLOWER than the original when run sequentially** (pragmas stripped, LARGE, Mac, best of 5; `results/E01_main_comparison/checks/seq_cost_expert_mac`): `s121` 2.30×, `s112` 2.06×, `s211` 1.65×, `s241` 1.64×, `s1213`/`s243` 1.25×, five within 5 %, five faster. All are ≥ 1.45× faster with their pragmas (T0.10). **D31 withdrawn**: no sequential bound separates the failed rewrites (1.2–3×) from the good ones. **D31-b proposed**: when Settle finds a rewrite does not pay, retry the region with that verdict as feedback while budget remains | the author: "isn't it rejected already if it's slower? why k×?" — a rewrite is expected to be slower alone; the question is only answerable with the pragmas on, and only Settle asks it |
| 2026-09-22 | finding (E1 class A) + agent | **The no-harm control caught harm: on `s000` the agent delivered LESS than DiscoPoP alone (verdict `lost`).** DiscoPoP alone applies its do-all at 3.59× (FASTER). Under `default` the loop was deferred to Phase B (right), but the function around it had no pattern of its own, so the model was called on the function; Haiku "restructured" it with a `memcpy` of `b` on every repetition; the copy passed the correctness gate; DiscoPoP's pragma on the rewritten loop measured 1.40×; Settle found the finished file slower than the original, dropped the pragma first (its repair order), the rewrite was then an orphan, everything reverted: `no-change`. The other two class-A loops (`s313`, `vpvtv`) are FASTER in both arms. **Fix 90 was built for this and REVERTED before it ran** (next row): the rule — skip a region whose outermost loops all carry a DiscoPoP pattern — would have blocked the model on 11 of 18 class-R loops. Not fixed, recorded: Settle's repair order drops the newest pragma before the rewrite, so it can never fall back to "the original with DiscoPoP's own pragmas"; the agent has no floor at DiscoPoP alone | one trial (class A ×1), but the path is deterministic — the model is always asked about the enclosing function. It also answers D31: this rewrite was only 1.2× slower sequentially, a k-bound would not have caught it |
| 2026-09-22 | result | **E1 class R is complete (§7 `e1_r_a`, `e1_r_b`): 260 trials, 0 unsafe.** TSVC primary set: the agent reaches a verified parallel program in 46 of 90 trials and is FASTER in 44; DiscoPoP alone in 0 of 90; 14 of 18 loops gained at least once, 5 loops 5 of 5; per-loop medians 1.08× (Wilcoxon p = 0.002, Cliff's δ +0.50); 6→12 threads scales in 29 of 44. H1 supported, H2 holds. Classes A and D run on the same commit (`e1_d` launched) | the campaign's first headline number, read against DiscoPoP alone as the rule requires |
| 2026-09-22 | agent | **Fix 89 — Settle's speed verdict is paired.** It timed the finished program alone (best of 5, `-fopenmp`) against the reference captured at the START of the run (best of 3, no `-fopenmp`), minutes apart on a shared host. Now: the same interleaved original-vs-final measurement and threshold Phase B uses (`measure_marginal`), the threshold handed from Phase B through the gate cache. Feature check `settle-paired`: a faster file must pass against a reference 8× too small, a file with twice the work must fail. On the work branch: E1's remaining classes run on `00d4594f` | 15 of 90 TSVC trials ended with Settle reporting a finished program 1.1–8× slower than the run's opening reference; ten of them rebuilt and re-verified on the server (`results/E01_main_comparison/checks/settle_check`): all correct, all slower, 0.14–0.99× — the method was fragile, the verdicts stood |
| 2026-09-22 | finding | **The rewrites that fail copy the array inside the repetition loop** (`memcpy`, or `malloc`/`free` per repetition); the ones that succeed need no buffer. Settle catches the cost — after the trial's budget is spent. `s331` and `s341`, which T0.13 called unwinnable for DiscoPoP's pragmas, were each won once by a restructuring DiscoPoP could annotate, and lost at Settle on the same cost | E1 §7; D31 (a bound on a rewrite's sequential cost) was withdrawn on the measurement below; D31-b (retry after Settle's verdict, with it as feedback) is proposed |
| 2026-09-22 | finding | **Two `npb/is` trials hit the 90-minute limit** inside Phase B after a kept rewrite made the program's regions 30× slower (3.3 s → 97 s at the agent size); every later step ran that program. Counted `invalid`; `is` is out of scope (D30) | E1 §7; the same cause as the row above, at application scale |
| 2026-09-22 | harness | `main_comparison_stats.py --suite tsvc` (the primary set with the registered set's statistics); `thesis_material.py` spec `<arm>@<rep>` selects a repeat; exhibits `s291`, `s127`, `s254`, `s241` (rep 2), `s121`, `floyd` from E1 | the read-out needed them |
| 2026-09-21 | finding + harness | **The LULESH package would have called EVERY correct parallel LULESH `BROKEN` — LLNL's own included. Found because the author asked whether a reference solution had been checked; fixed.** LLNL's OpenMP release (`benchmarks/LULESH/LULESH_LLNL_OMP/`, upstream `3e01c40`, 44 pragmas, with `PROVENANCE.txt`) was put into package form by the recipe's own edits (`prepare_apps.py --references` → `reference_solutions/llnl/lulesh/`) and judged by `verify-source`: `BROKEN`, dump error 0.25, while the digest agreed to 1.8e-16. Cause: under `PB_FULL_DUMP` the package emitted the five numbers the original prints, and three of them are LULESH's SYMMETRY differences — energies that are mathematically equal, subtracted. On the symmetric input they are rounding residue (2e-11 against energies of 3e+5), and adding in another order moves them by tens of percent: serial 2.18e-11, OpenMP 2.91e-11. They are diagnostics, not results. Now the five numbers are emitted under `PB_ORIGINAL_REPORT`, which only the packaging validator sets (new `Recipe.validate_macros`); the full dump is the whole final state, the very values the digest already read — every element's energy, pressure, volume, every node's position and velocity | Measured before relying on it: over 1,672 / 5,911 / 34,702 state values (MINI / SMALL / STANDARD), shipped and seeded input, LLNL's version against the serial path is bit-identical at 1 thread and within **5.6e-15** at 2 and 4 — six orders of magnitude inside the 1e-9 tolerance; LULESH's own cut-offs snap small values to exact zero, so there is no noise tail. The package still equals the original's report at three sizes. After the fix: LLNL's version `FASTER` 1.70× at STANDARD, `parallel-not-faster` at SMALL (8³ elements), Mac, 4 threads (`results/T0_instruments/T0.14_reference_acceptance/runs/lulesh_ref_check`). The agent's own gate reads the digest and would have ACCEPTED such a program, so the harness would have scored the campaign's one application `unsafe` for both arms. Rule from now on: **T0.14, the reference acceptance check (§5s)** |
| 2026-09-21 | finding | **LLNL restructured LULESH; Rodinia's and NPB's experts did not (§5r).** LLNL's OpenMP `lulesh.cc` differs from the serial path by 168 code lines beyond its 44 pragmas — 67 in `CalcFBHourglassForceForElems`, 44 in `IntegrateStressForElems` (per-element force buffers gathered per node), 10 in each constraint function (per-thread minima). Rodinia: 0–7 code lines in all 19 programs. RepoOMP's NPB-C: 0–18 | the author: "what about the rest of Rodinia; also see whether NAS is useful". It decides what each suite can show: LULESH the restructuring claim at application scale, NPB-C the external comparison (E11), no-harm and pragma authorship (E3) — and under `default` little benefit of the agent, written down before the runs |
| 2026-09-21 | plan | **D30 corrected: `hotspot` DOES have a verified output-identical parallel version, and so does `floyd-warshall` (§5r).** Hand-written, no model: `hotspot`'s chunk loop split (boundary chunks in order, interior chunks parallel) — `FASTER`, dump byte-identical on both inputs, 1.52× at 4 Mac threads; `floyd-warshall` in its textbook form (write only on improvement) — `FASTER`, byte-identical, 3.61×. `md`'s expert version is two commented-out pragmas in Burkardt's own source: not a restructuring benchmark | the author: "before removing the benchmarks did you verify that they are with not much value?" — no, and the reason recorded for `hotspot` was wrong. Both re-enter only if T0.13 on the server keeps their reference, and only by the author's decision; D30's three suites stand until then |
| 2026-09-21 | plan | **Every instrument and experiment re-examined (§5s).** No finished run has to be repeated with a model. Owed without a model, on the server: T0.1 / T0.5 / T0.6 / T0.11 / T0.13 for LULESH, T0.13 repeated for TSVC at more than four threads, the three new references re-verified at 6 / 12 / 24 threads, NPB-C probe and packaging; T0.9 re-run before E3. E2-C and E2-D get seven loops fixed by TSVC's own categories (`s112 s121 s211 s241 s252 s281 s291`); E4 becomes conditional on E3; E9 moves to LULESH and NPB-C; E11's agent entry is pre-stated as `default` | the author: "check the planned experiments if something needs to be changed, and the previous ones we ran, the Ts for example" |
| 2026-09-21 | harness | `verify-source --source DIR` for project benchmarks (every file of the directory replaces its namesake; candidate hashed as a tree; refused for single-file benchmarks or when the directory lacks the benchmark's own file); `prepare_apps.py --references` and `Recipe.reference_dir` / `validate_macros`; `default_arm_ceiling.py` accepts `suite/kernel` for any package with a reference, single file or project (staged copy with the expert's files laid over it and their pragmas stripped, profiled by the harness's own `profile_once`) | an expert version that is several files (LLNL's LULESH) had no way into the harness |
| 2026-09-21 | process | **No DiscoPoP profiling of application-size code on the Mac.** Two background jobs (the NPB-C probe compiling FT under DiscoPoP's pass, the `hotspot` ceiling test running an instrumented binary) drove the 8 GB machine into swap until the disk had 1.7 GiB left; 28 GiB again a minute after both were stopped. Their results are therefore partial (`results/E11_repoomp/preflight/e11_npbc_probe_mac`: EP, IS, CG only; no `hotspot` ceiling) and the rest is owed on the server | the author: "my disk space is almost full" |
| 2026-09-21 | plan | **D30 — the campaign's scope is narrowed to TSVC-2, LULESH and RepoOMP's NPB-C (§5r).** A benchmark enters a restructuring experiment only if, decided WITHOUT a model, (1) DiscoPoP can profile it, (2) DiscoPoP alone reaches no verified parallel program, (3) a verified output-equivalent parallel version exists, (4) the no-model ceiling test shows the arm can keep that version. Out: `hotspot` (no equivalent parallel version exists), `seidel-2d` (a true recurrence, really class D), `md` and `npb/is` (never verified, 35 and 20 min per trial), PolyBench's class-A kernels (cannot show a benefit of the agent — the author's call against keeping one no-harm run) and its four unverified class-R kernels. Everything E1 has run stays archived and is reported beside the restricted set; the rule is recorded before any TSVC result of E1 exists. LULESH and NPB-C get packaging and a no-model pre-flight before any model call | the author, five hours into E1 with 35 of 35 finished trials `no-change`: "pick only the ones that will show results, not just taking so long then nothing" |
| 2026-09-21 | finding (C2) | **The gate rejected the parallelization of Rodinia `hotspot` that Rodinia's own OpenMP version uses — and it was right.** E1's first agent trial ended `no-change` with all seven of DiscoPoP's pragmas rejected; the suspicious one was the chunk loop of `single_iteration` (`private(c,delta,r)`, equivalent to Rodinia's `private(chunk, r, c, delta)`), rejected at `correctness` because a checksum moved by 1.7 × 10⁻⁸ — 1,000× the program's measured rounding floor (1.67 × 10⁻¹¹), identical in two candidates, so deterministic and not a race TSan could see. Checked apart from the agent, on the original source with DiscoPoP's exact pragma: static schedule, 1–16 threads reproduce the sequential checksum `1692807788529.6304` bit for bit; **24 threads give `1692807817763.9468` — the very value the gate reported on the server** — 48 threads another, and `dynamic,1` / `guided` at 4 threads two more. Cause: the boundary branch is an `if / else if` chain over four corners and four edges with NO final `else`, so an interior cell of a boundary chunk is updated with the `delta` left over from the previous cell, and the first such cell of a bottom- or right-edge chunk with the `delta` of the PREVIOUS CHUNK. That is a loop-carried dependence through `delta`; `private(delta)` cuts it, and the result then depends on which chunk each thread starts with. The gate sees it because it checks all threads of the NUMA node and the schedule matrix, not one configuration. Consequences: (i) the answer to "will the gate reject everything?" is that its rejections have held up wherever they were checked; (ii) `hotspot` has no parallel version that is output-equivalent to its sequential one without first repairing that dependence, so `neither` is the expected verdict there and says nothing against the agent; (iii) an exhibit for C2 — a latent defect in a published benchmark's own OpenMP version, found by the gate | the author: "I have a concern that all code changes will be rejected" |
| 2026-09-21 | harness | **E1's read-out exists before E1's data does.** `tools/main_comparison_stats.py` computes exactly what the plan pre-registered and nothing chosen after seeing results — Wilson 95 % intervals on rates, Wilcoxon signed-rank on per-benchmark medians (one-sided, paired by benchmark), Cliff's delta, a bootstrap interval on the median agent ÷ DiscoPoP-alone ratio (fixed seed), unsafe acceptances and every missing trial NAMED — per measured class, with untimeable kernels left out of every speed statistic and a block on what actually happened inside the trials (refresh kinds, fallbacks, explorer stalls, speed check off, host load). `plots` writes it beside the figures. New figure `fig_verdict_matrix`: one square per agent trial, rows grouped by class, on the hues of the validated outcome palette. Tried on `e1_smoke5` | written while E1 runs so that the analysis cannot be shaped by the numbers |
| 2026-09-21 | agent + harness | **E2's missing instruments (D16) are built; E2 can be specified completely.** Agent: `--evidence-file` (another tool's remarks shown where DiscoPoP's digest goes, labelled static compiler output; an empty file is refused) and `--prompt-omit contract,gate,granularity,checklist` (the line saying who writes the pragmas is kept even without the contract: it is the pragma MODE, E3's variable). Harness: `tools/compiler_remarks.py` — clang-20's vectorizer and Polly remarks, kept only inside functions the agent may edit (`s211`: 9 kept, 104 about packaging code dropped; e.g. *"loop not vectorized: unsafe dependent memory operations in loop"*), generated once per benchmark per run under `<run>/evidence/`. `arms.json`: **E2-source** (none → compiler remarks → where-only → full DiscoPoP), **E2-C** (the six evidence groups, each left out and given alone; together they cover all 12 sections), **E2-D** (four prompt parts), all at budget 1; 38 arms, 12 experiments, every one machine-checked. Feature check `prompt-ablation`: each part removed alone in 3 edit modes × 2 pragma modes, nothing else with it | D16 had been specified on 19 Sep and never built |
| 2026-09-21 | agent + harness | **The bare-LLM baseline the plan lists for E1 exists (`discopop_agent/bare_llm.py`, arm `bare_llm`, experiment `E1-bare`).** The same model through the same client call, handed the program and asked to parallelize it: no DiscoPoP (nothing read, ranked or shown), no gate (nothing compiled, run, raced or timed), one attempt; what it leaves in the files is judged by the harness like any trial, so BROKEN programs are expected and counted. A SEPARATE runner, not the agent with switches off. Shared with the agent, so the comparison is about the pipeline: THE CONTRACT, the OpenMP loop rules, the pragma forms. NOT shared, because it would be false there: the agent's role ("a stage of DiscoPoP"), its account of a profile, its description of a gate — the feature check `bare-llm` (stand-in client, no model call) caught the first draft borrowing exactly that. Runs after E1's main comparison, on class R, as its own run | the plan, §3: *what the pipeline adds over asking the model* |
| 2026-09-21 | docs | **Upstream reports B7 and N1 completed** (`docs/DISCOPOP_BUG_REPORTS.md`): B7's root cause is in `dp_loop_output.cpp` — counter id *i* is paired with the *i*-th LINE of `loop_meta.txt` behind a dummy element, starting at 1, while ids are 0-based and the file is not sorted by id; this reproduces the wrong file exactly; patch written. Both defects are present in upstream `new_explorer` at `28ac4d47` (17 Sep). **The DiscoPoP-alone baseline is unaffected:** the explorer's pattern detection takes its loop data from the `BGN loop` markers, not from this file. Not patched here yet — the runtime is linked into every profiled binary and E1 is running; it goes in with the post-campaign rebase | checked against upstream before reporting, as the record required |
| 2026-09-21 | plan | **E1 LAUNCHED — class R first (the author's go, 21 Sep).** Arms `discopop_gate`, `default` (they differ in `--budget` only, `test_arms.py`); Haiku 4.5 (D9); × 5 per arm; threads 6/12, 5 repeats, verification and timing sizes per kernel (T0.1); agent commit = the commit of this row. The 26 class-R benchmarks of `benchmark_classes.json`, split over the two NUMA nodes as two runs so that both arms of a benchmark share one profile draw inside their run: **`e1_r_a`** (node 0) `md`, `is`, `bicg`, `doitgen`, TSVC s112 s121 s1213 s127 s211 s212 s241 s243 s244; **`e1_r_b`** (node 1) `hotspot`, `seidel-2d`, `floyd-warshall`, `trisolv`, TSVC s252 s254 s255 s281 s291 s292 s293 s331 s341 — the four expensive programs (`md`, `is`, `hotspot`, `seidel-2d`) two per lane. Stated before the first trial: (i) `bicg` and `trisolv` have no timing size, so the agent's speed check is off on them and they count for coverage, never for speed (pre-registered treatment of untimeable kernels); (ii) the bare-LLM baseline arm the plan lists for E1 is NOT part of this launch — it does not exist yet and does not affect the main comparison; (iii) host load 5,000–7,000 from other users, recorded per trial; (iv) classes A (×1) and D (×3) follow as separate runs on the same commit | the author: "go" |
| 2026-09-21 | plan + harness | **The measured classes become campaign INPUT (`agent/config/benchmark_classes.json`), and the main comparison is read PER CLASS.** `kernel_groups.json` was to be "rewritten once the classes are measured" and never was: it still held the groups guessed on 14 Sep (A/B/C, the core ten), and `figures.py` grouped by it. The new file is generated from T0.11's `classes.csv` — R 26, A 25 (`adi` excluded, D25), D 4 — with E1's repeats (R ×5, A ×1, D ×3) and their reason; `vs_discopop_alone.md` now opens its detail with a per-class table, because pooled over classes the verdict counts mostly reflect how many benchmarks of each class a run contains, while the claim is about R, with A as the no-harm control and D as the must-decline control; every comparison row carries `class`. `test_arms.py` checks the file: every benchmark prepared, sized, in one class only. Of E1's 55 benchmarks the agent's speed check is OFF on 7 that no size can time — `bicg`, `trisolv` (class R) and `atax`, `gemver`, `gesummv`, `mvt`, `reg_detect` (class A): they can show that a verified parallel program was reached, never a speedup, and stay out of every speed statistic as pre-registered | the author: benchmarks must serve the purpose of their experiment; E1's headline has to be readable from the run's own tables |
| 2026-09-21 | plan + harness | **`arms.json` gains an explicit, machine-checked `experiments` block — and E2 turns out to have been confounded.** Each experiment names its arms, its VARIABLE (resolved agent settings) and what may differ only as a CONSEQUENCE; `tools/test_arms.py` resolves every arm through the agent's own parser and fails unless the arms differ in exactly that — nothing more (a confound), nothing less (a variable that does not vary). The per-arm `ids` tags it replaces had drifted: they listed E3's 2×2 with three arms, one a duplicate. **Found by it: E2's cells `full_b1`, `no_evidence`, `no_evidence_b1` carried a `--fast-refresh` their baseline `default` does not** — pinned there by D27's blanket 'keep what was implicit', and missed because §5 D27's 'verified' list (E1, E3, E4, E8, E9, E10) never included E2. Removed: the refresh is E3's variable. `discopop_annotates` is retired (since D27 it resolves to exactly `default`); stale descriptions corrected (`default` still called itself E3's fast-refresh cell, `speed_gate_large` still called itself the campaign default and E1's agent arm). All nine experiments pass: E1 differs in `budget` only | the author: "the arguments of the agent and benchmarks selected for every experiment should be serving the purpose … wrong arguments is not acceptable" |
| 2026-09-21 | agent + harness | **D29 — the fast refresh re-measures runtimes too, and every refresh is RECORDED as what it actually was.** (i) After a successful fast refresh the agent now takes the same native-speed hotspot measurement as after a full re-profile: without it the fast arm alone could not rank the regions a rewrite created, so E3's arms would have differed in the refresh AND in whether Phase B sees the exposed loops (Fixes 86, 87) — a confound of exactly the kind D24/D28 forbid. The fast refresh still skips the INSTRUMENTED run, which is what it exists to avoid; E3's cost column for that arm includes the extra run and says so. `--llm-recon` cannot close this gap (it reconstructs dependences in source terms; a runtime is a measurement). (ii) The author's objection to the silent fallback — *"how will we measure it if this happens when it fails?"* — is right: a fast refresh that proves unusable is replaced by a full re-profile so that a correct rewrite is not lost to the cheap path, but the trial then did not get the treatment its arm names. Every refresh now prints `[refresh] kind=…` (one of `fast`, `full`, `fallback`, `failed`), the kind is stored in the accepted record, and `trial.json`/`trials.csv` carry `refresh_fast`, `refresh_full`, `refresh_fallback`, `runtime_remeasurements`. E3 reports the fallback rate and analyses the fast arms both as assigned and restricted to trials without a fallback. Measured so far: **0 of 108** archived fast refreshes fell back | the author, 21 Sep |
| 2026-09-21 | agent + harness | **The explorer gets a stall limit (`--explorer-timeout`, 600 s) and a stalled draw is repeated — the agent's call had NO limit at all.** A random stall (L5; upstream B6 says "callers should give the explorer a timeout") after a KEPT rewrite would have hung the trial until the harness killed the agent at 90 minutes; it could strike only trials whose rewrite had been accepted, so the trials it removed would have been the agent's successes — missing data correlated with the outcome. From the T0.11 draws: 166 explorer runs, median 3.5 s, slowest legitimate 33 s, 12 draws (7 %) never finished — each costing its benchmark the whole run, all arms and repeats, because a run profiles once. Now: one attempt is killed at the limit WITH its process group (the explorer's patch-generator child included), the draw is repeated on the same profile, at most 5 stalls; the harness's profile step follows the same rule, which reverses the 20 Sep 'a timeout is not a crash, no retry' — that rule was written when the stall looked like a property of two loops, hours before it proved random. Per trial: `explorer_stalls`. Feature check `explorer-stall` (a stand-in explorer that hangs with a child on its first draw) | reproduced twice on 21 Sep: the rewritten `s211` stalled > 6 min on the Mac, seconds on the next draw |
| 2026-09-21 | agent | **Fix 88 — the iteration counts the agent used were wrong in 82 % of loops (DiscoPoP's `loop_counter_output.txt`, upstream B7).** The file pairs counts with the wrong loops: over 41 profiles, 277 of 337 counts disagree with the `BGN loop` markers of the same run, in 38 of 41 programs (TSVC's 48-iteration repetition loop reported as 1,536,000; the second of two sibling loops as 160 where it ran 1,535,904 times). Two consumers, both in every arm: the workload proxy (ranking without hotspots — E9's `full_no_hotspots` — Phase B's fallback order, every `W=` in a log) and **the "N iterations" stated to the model in the prompt header**. Counts now come from the markers (one per loop in all 528 loops checked); the file is the fallback. Ground-truth feature check `loop-counts` (outer 7 × two siblings of 998: the file says 6,986 · 6,986 · 1,000). **Consequence for archived runs:** every model call so far saw a header count that was probably wrong; the loop-nest evidence section in the same prompt always carried the right ones (`evidence/context.py` already read the markers), so the prompts contradicted themselves. Stated as a limitation of pilot4 and E10; E1 onwards is clean | found while diagnosing smoke 4 (§7) |
| 2026-09-21 | agent + harness | **Three defects in the arm verification (D24), found by checking ALL 20 arms instead of the ones a smoke happens to use.** (i) `--print-config` serialised a set with `str()`: an empty `evidence_sections` printed as the string `'set()'`, so both no-evidence arms of E2 — which declare `[]` — would have been REFUSED at launch; sets are now sorted lists. (ii) `discopop_capability` still declared `fast_refresh: true` after D27 changed the default; inert in that arm (budget 0, no rewrite ever happens, so T0.11 is unaffected), but the arm would have been refused on a re-run. (iii) The verification looked at the run's FIRST benchmark only, while an arm's flags depend on the benchmark: a kernel with no timing size gets `--no-require-speedup` from the harness. A timeable first benchmark hid that; an untimeable first benchmark refused the WHOLE run, every arm "declaring require_speedup=True but parsed False" — and E1's class R holds both kinds, so whether E1 launched depended on the order of its list. One representative per timing situation is now checked, and where the harness switched the check off the expected values are that consequence (`require_speedup` and `pragma_arbitration` both False). New harness test `agent/tools/test_arms.py`: all arms × both situations × both orders; it fails on each of the three. After the fixes: 20 of 20 arms match | the author asked for the previous day's changes to be validated; D24's promise is only as good as the arms it is run on |
| 2026-09-21 | agent | **Fix 87 — a forced runtime re-measurement described the OLD program; and the fast-refresh fallback never re-measured.** DiscoPoP's hotspot detection accumulates by design (region ids appended to `hotspot_detection/private/cs_id.txt` by every build, one `hotspot_result_<n>.txt` per run, the analyzer averaging over runs). `_measure_hotspots(force=True)` removed only `Hotspots.json`, so after a rewrite the analyzer reported the previous program's region table: old line numbers (`s211`: `main` at 147, 149 in the rewritten file), times halved, no entry for a region the rewrite created — and the caller, taking a fresh measurement to be in the new coordinates, skipped the line remap, mis-keying every region below the rewrite. The whole `hotspot_detection/` directory is now cleared before instrumenting. Found because **smoke 4 showed Fix 86 alone changed nothing**: `Re-measured runtimes: 16 region(s)` in the log, and still one Phase B candidate. Reproduced without a model by replaying the agent's own post-rewrite sequence (3 candidates before, 4 after, `1:90@140–142` among them). Second part: the re-measurement now follows ANY successful full re-profile, including the fallback taken when a fast refresh is unusable, which had sat in the other branch. Feature check `hotspot-remeasure` shifts a measured program by three lines and re-measures — fails on the old code (`[14, 18, …] -> [14, 18, …]`), passes now. **Consequence for the record:** the deeper-level path (`--restructure-depth ≥ 1`) has carried this since it was written, so any earlier run at depth ≥ 1 ranked its second level on stale-line measurements; E8 had not run | smoke 4 (§7 `e1_smoke3`, `e1_smoke4`) |
| 2026-09-21 | agent | **Fix 86 — the restructuring path could not produce a result under the new defaults: runtimes were never re-measured, so every loop a rewrite exposed was filtered out before Phase B could annotate it.** The re-measurement after a kept rewrite was gated on `deeper_coming` (a further Tier-2 level), which is false at the default `--restructure-depth 0`, so it never fired — yet Phase B ranks those same new regions on **every** run. Each of them therefore reached `build_candidates` with no measurement, `predicted_saving` returned `None`, and `--min-runtime-share 0.01` (the campaign's `common_flags`) dropped it outright instead of falling back to the workload proxy. Phase B then had nothing to apply and Settle discarded the rewrite as an orphan: outcome `no-change`, with a correct rewrite thrown away. **Measured on `tsvc/s211` (smoke 3):** the model's loop distribution passed the gate, DiscoPoP reported `do_all` on **both** halves (`Data.xml` regions `1:84` and `1:90`, patterns at lines 137 and 140), and only the racy half was offered — the parallel one was dropped. Reproduced exactly: with a model that knows the pre-existing loop and not the created one, the candidate list is 4 regions at `--min-runtime-share 0` and 3 at `0.01`, matching the run's log. The depth is now removed from the decision, which lives in the named predicate `should_remeasure_runtimes()` so it can be asserted; feature check `new-region-ranking` pins both halves (the filter's hazard, and that the decision does not depend on depth); 34/34 checks pass, mypy clean. Cost: one native-speed run per kept rewrite, beside the instrumented one the re-profile already pays for. **Why the archive did not show it:** all 34 archived trials that accepted a rewrite ran with `--llm-pragmas` ON, where the rewrite annotates itself and never depends on Phase B — the new default (D23) is what made the path load-bearing. **Still open:** the `--fast-refresh` path does not re-measure either, so E3's fast-refresh arm keeps the defect; closing it adds one native run to that arm (it still skips the *instrumented* run, which is what `--fast-refresh` exists to avoid) — the author's call, not taken here | smoke 3 ended `no-change` on both benchmarks with a correct, gate-passing rewrite in each; the author: "what is the purpose of the experiment if every restructuring is going to be reverted?" |
| 2026-09-21 | agent | **`--llm-recon` does not and must not cover Fix 86's gap.** A fast refresh loses two different things: the DEPENDENCES in created code, which `--llm-recon` closes completely (39 of 39, measured), and the RUNTIMES, which come from a separate pass (`discopop_hotspot_*` → `Hotspots.json`) and not from the dependence profile at all. `dep_reconstruct` works in source terms only — loop line, dependence type, variable, writer line, reader line — and resolves every claim by lookup against this build's dependence files, precisely so the model never invents compiler-internal identity; a runtime is not a source fact, and a guessed one would put an estimate where the L3/L4 division requires a measurement. Recorded because the two are easy to conflate: they are both "the gap a fast refresh leaves" | the author asked whether `llm_recon` already covers it |
| 2026-09-21 | agent + harness | **D28 — the argument-dependency audit (§5q).** Three kinds: prerequisites and contradictions are REFUSED by the agent (feature check `arg-dependencies` asserts five of them); settings made INERT by another setting are printed before every run. `--pragma-arbitration` now resolves to False whenever it cannot fire, instead of being declared active by every arm under the new defaults. One planned experiment is affected: E9's arm makes `--min-runtime-share` inert, which its write-up must state | the author: "some args were depending on each other and some of them were wired — this might corrupt the experiments" |
| 2026-09-21 | agent + plan | **D27 — `--fast-refresh` is no longer the default either.** A kept rewrite is followed by a FULL re-profile, so decisions rest on dependences DiscoPoP observed in the rewritten code; the fast refresh is an accuracy-for-time trade that E3 measures. Found on the way: `--llm-recon` only runs inside the fast-refresh branch, so E4's arms pin it explicitly and E4's baseline becomes `discopop_pragmas_fast`. The compatibility check caught two confounds this created (E8, E4) and a hole in itself — it never checked `llm-recon`/`llm-deps`, so it had reported "no differences" for E4 | the author: "fast refresh on should not be the default also" |
| 2026-09-20 | agent + plan | **D23 — `--llm-pragmas` is no longer the default; pragma authorship is opt-in per experiment.** Off, the model restructures and DiscoPoP annotates, so a rewrite is kept only if the analysis finds parallelism in it — the division of labour the thesis argues for. Pinned explicitly in E10's three arms (reproducibility) and E3's two "model writes them" cells (new arm `llm_pragmas_fast`); `default` becomes E1's agent arm and the baseline cell of E3, E4, E8, E9. E2's arms now follow the new default, which is a deliberate change to a pre-registered experiment and is flagged as one | the author: "i do not like having --llm-pragmas as the default it should be added when needed for a specific experiment"; E10's `jacobi-2d` showed the cost of having it on by default |
| 2026-09-20 | plan + harness | **D22 — the campaign's fixed configuration becomes the speed check ON at the kernel's timing size, for every arm including the baseline; and the change HAD broken four unrun experiments; found by checking, fixed, and guarded.** E3, E4's matrix cell, E8 and E9 each paired a variant against `full`, which was pinned to the old behaviour → new arm `default` is the baseline cell of every matrix experiment. Eight kernels with no timing size (incl. `bicg`, class R) would have become unrunnable → the speed check switches off for them and the fact is recorded (`speed_check_off`). Guard: `check_arm_compatibility()`, printed before every run — "each line must be this experiment's variable; anything else is a confound" | the author: "make sure that these changes would not harm other experiments, should check" |
| 2026-09-20 | plan + agent | **§5l: audit of the agent's DEFAULTS.** Every default now carries its justification, and a field marked "studied in a later experiment" must also state the value earlier experiments hold it at and why. Findings: `llm_pragmas = True` rests on a design argument alone and drove E10's `jacobi-2d` regression (22 trials across the archive end with a deferred DiscoPoP pattern and only LLM pragmas); `budget = 3` is now measured rather than assumed (acceptances by attempt: 40/127, 12/91, 6/82); the campaign's `--no-require-speedup` is wrong by E10's own result — the agent's default was right, the SIZE was not. **D21 = Fix 85**: the prompt reserves claimed loops for Phase B, and where a model pragma lands on one anyway Phase B measures DiscoPoP's against it and keeps the faster (displacement is a win on `lu` 0.21×→2.8× and a loss on `jacobi-2d` 5.9×→2.5×, so the fix measures instead of choosing) | the author: "we should review the agent default and see if this is the right default"; "for every experiment every parameter selected should have a reason" |
| 2026-09-20 | plan + agent | **The main comparison for E10 exists (§7 `e10_dp_alone`, `e10_lu_fix84`): D8 confirmed, and `speed_gate_small` shown to be destructive — 10 of 21 trials `lost` because the speed check at the agent's small size deletes DiscoPoP's OWN pragmas (`marginal 0.00×`).** Agent vs DiscoPoP alone, median 1.00× on this class-A set (no harm, as intended); `lu` better ×10, `floyd-warshall` gained, `jacobi-2d` worse (→ Fix 85). Classification fixed: correct-but-slower-than-doing-nothing counts as `worse`, not `gained-not-faster` | D19; the author's question "how is this even possible?" about a loop carrying both a model pragma and a DiscoPoP suggestion |
| 2026-09-20 | plan | **D8 decided by E10: `speed_gate_large` is E1's agent arm** — 11 FASTER / 0 slower programs kept / 0 BROKEN, against `full` 8 / 5 / 1 and `speed_gate_small` 2 / 0 / 0 (16 of 18 unchanged, 29 performance rejections) | pre-registered rule of D8; §7 `e10` |
| 2026-09-19 | plan + harness | **D19 — the main comparison is DiscoPoP alone vs DiscoPoP + agent; the sequential original is the reference (§5k).** Every experiment carries `discopop_gate` on the same benchmarks in the same run; each agent trial gets a verdict against DiscoPoP alone (gained / better / equal / worse / lost / neither / unsafe); `vs_discopop_alone.csv/.md`, `fig_vs_discopop_alone`, and every `overview.md` opens with it (or says MISSING). Trials record `host`; ratios are withheld across hosts/sizes/thread sets. E6 (LULESH) becomes the application-scale main comparison with LLNL's expert version as ceiling. Figures: Helvetica dropped (macOS `.ttc` cannot be embedded) | the author: "the main comparison is between DiscoPoP alone and DiscoPoP with the agent … this is a rule"; "LULESH had examples before and after parallelization" |
| 2026-09-19 | agent | **Fix 84 — generated pragmas were placed on the wrong one of two identical sibling loops** (29 of 539 DiscoPoP pragmas, 12 of 26 PolyBench kernels); it under-measured the DiscoPoP-alone baseline. `discopop_gate` numbers before it on those kernels are void; E10's `polybench/lu` to be re-run | found while checking why DiscoPoP alone "failed" on `atax` — the class of a benchmark must be real, not an artefact |
| 2026-09-19 | plan | **D18 — the benchmark set is redesigned (§5k).** The planned core set could not test C1: DiscoPoP + gate alone parallelizes 17 of 20 PolyBench kernels, 21 of 25 FASTER results were pragma-only, and E2/E3/E4/E8 would have been empty. Classes are now measured (R needs restructuring / A parallel as written / D must decline / M multi-region), every experiment names the class it needs and why, a no-model pre-flight check precedes every experiment, and a restructuring suite with ground truth is added: 25 TSVC-2 loops (verbatim bodies, harness packaging, expert references kept outside the packages, all validated), plus `atax`, `bicg`, `floyd-warshall` from PolyBench. New tools: `prepare_tsvc.py`, `tsvc_ceiling.py` (T0.10). Harness: `omp.h` include path for verification builds on macOS | the author: "this must be fixed … make sure every benchmark is suitable for its experiment … show which experiment uses which benchmarks and why … the right setup before running" |
| 2026-09-19 | plan | **E2 extended before any E2 trial exists (the author's questions of 19 Sep: "does DiscoPoP's evidence actually help, which part of it, and which part of the prompt?").** (i) **Two evidence-source arms** beside `full` and `no_evidence`: `hotspot_only` (only `runtime_share` — where to look, no dependence information; existing switches) and `compiler_remarks` (clang's own `-Rpass-analysis=loop-vectorize`/Polly remarks injected where DiscoPoP's digest goes, through a new `--evidence-file`): none → static tool → dynamic DiscoPoP, so "evidence helps" can be told from "any hint helps". (ii) **Part C becomes unconditional and grouped**: six evidence groups — dependences (`deps`, `blockers`, `reductions`), data-sharing (`classification`, `extra_vars`), structure (`loop_nest`, `accesses`, `calls`, `inner_patterns`), where (`runtime_share`), how-to (`array_note`), feedback (`failure`) — each both LEFT OUT of full evidence (necessary?) and given ALONE (sufficient?), because overlapping sections hide each other in a leave-one-out alone. (iii) **New Part D, prompt ablation**: leave one prompt part out (contract, gate description, granularity/steps, task checklist) with evidence held at full, through a new `--prompt-omit`; read-out includes gate rejections by stage, since a prompt part may prevent wasted attempts rather than failures. Parts C and D: Haiku, budget 1 (so feedback cannot compensate), the six group-B/C benchmarks, ×3 — exploratory, reported with effect sizes and secondary measures (calls per success, rejection stages, tokens), not significance tests, and said so | recorded before implementation and before any E2 run |
| 2026-09-19 | plan | **E11 widened to RepoOMP's eight NPB-C kernels** (BT, CG, EP, FT, IS, LU, MG, SP) on their own pragma-free inputs (`benchmarks/RepoOMP`, commit `45a1b9f`, Apache-2.0, copied unmodified), against their released outputs (RepoOMP ×3 models, their Claude Code, Codex and AutoPar baselines) and the expert versions, all through one verification. Feasibility probe `npbc_probe.py` (no model): EP 43 s, IS 20 s, CG 99 s with agent Fix 83 (explorer state assignment memoised; > 20 min before); the rest on the server | the author asked for the comparison with the state of the art to be the focus; the C versions are 170–2,600 lines, within DiscoPoP's reach where the C++ port's `mg`/`lu` are not |
| 2026-09-19 | plan | **E10 launched first (D8), with one stated deviation:** Rodinia `hotspot` is added to the five timeable PolyBench core kernels (2mm, jacobi-2d-imper, floyd-warshall, lu, seidel-2d). The plan named PolyBench kernels only; `hotspot` has a timing size (STANDARD) and is where pilot3 and pilot4 both showed the effect E10 asks about — DiscoPoP's own inner-loop pragma kept at 0.08×. Arms `full`, `speed_gate_large`, `speed_gate_small` × 6 benchmarks × 3 repeats = 54 trials, Haiku, run `e10`. `full` is run here rather than reused from E1 because E10 now precedes E1. Results are reported with and without `hotspot` | the author left the choice to the analysis ("do what is best"); decided before any E10 trial ran |
| 2026-09-19 | plan | **D9 resolved: E1 runs with Haiku** (pilot4: 2 FASTER of 3 in group B). NPB `mg` leaves the model-driven core for now (explorer hours per run after Fixes 81/82 — upstream L3); model-driven core = 8. T0.2/T0.6/T0.7/T0.8 re-run on the fixed DiscoPoP (`DP_T0_TAG=_fix`) before E10 | pilot4 read-out |
| 2026-09-18 | agent | **Fix 82 (DiscoPoP explorer):** a call-path loop state is matched only against loops of the function it names; before, the search could continue into a caller's loop context and read its position from the callee's digits — `IndexError` on every `mg` attempt, a silent wrong match elsewhere. Upstream report B5 | NPB `mg` still crashed after Fix 81 although every function's loop-state width was then correct |
| 2026-09-18 | agent | **Fix 81 (DiscoPoP profiler) — the root cause of the explorer's random `IndexError`.** The LLVM pass instrumented a loop only if its exit block carried a debug line; clang gives the branch ending an `else` block none, so such a loop got no `__dp_loop_entry/exit`, the function's call-path loop states came out one position short, and the explorer (a) indexed past them on the runs whose traversal reached that loop and (b) matched every later loop of the function to the wrong position silently. `pathfinder`: explorer 1 of 6 runs before, 10 of 10 after (Mac), 6 of 6 (server). DiscoPoP's profiler tests 184/184; feature check `profiler-else-loop`. Rebuilt on both machines. **Consequences:** the author's rule of the same day — DiscoPoP bugs are fixed at the root, the fixed DiscoPoP is used in every arm including the baseline, each fix is highlighted in the thesis and logged for upstream in the agent's `docs/DISCOPOP_BUG_REPORTS.md` (B1–B4, L1–L2). T0.2, T0.6, T0.7 and T0.8 describe the unfixed pass and are re-run; `pilot3` is superseded by `pilot4` | the author: "why didn't we fix DiscoPoP instead of trying 20 times?" — NPB `mg` had failed every explorer attempt in three studies and in the pilot |
| 2026-09-18 | harness | **Outcome rule:** a final program that fails to run where the original ran (verify status `final_run_failed_T<n>`) is scored **BROKEN**, no longer `VERIFY_FAILED` — the agent delivered a program that does not work at the target size. Every other non-ok verify status (build failure, original not running, no digest) stays `VERIFY_FAILED`. Applies through `rescore` to finished runs | pilot3, floyd-warshall: the model's rewrite added `DATA_TYPE temp[N][N]` on the stack — correct and fast at the agent's SMALL size, a segmentation fault at LARGE; the gate never runs at the verification size, so it could not see it (a C2 finding for E7) |
| 2026-09-18 | plan | **D13 — Rodinia `nw` leaves the model-driven core ten.** With Fix 80 the explorer no longer crashes on `nw`, but it does not finish either: `nw`'s profile holds **531,606 call-path states** (`stateID_to_callpath_mapping.txt`, 620 MB; 2mm has 577, NPB `is` 1,725) because `nw_optimized` runs some twenty sibling and nested loops whose first-three-iteration positions combine, and the explorer's state assignment advanced 6 of 212 items in 39 min on the Mac (≈ 25 h per run; every trial runs the explorer two or three times). Like NPB `lu` (instrumentation > 2 h), `nw` is a DiscoPoP scalability limit, not an agent one: it stays as a verify-only baseline (Rodinia's own OpenMP version through the harness) and in E5 as a second cost outlier; the model-driven experiments run on the remaining nine (A: 2mm, hotspot; B: jacobi-2d-imper, floyd-warshall, mg, md; C: seidel-2d, trisolv, polybench/lu). `nw`'s `main` question (D4) is moot | the pilot cannot wait a day per `nw` trial; recorded before the first model run |
| 2026-09-18 | agent | **Fix 80 (explorer):** a loop with several back edges (`continue` statements; a branch whose arms both end the iteration) was marked once per cycle by the task-graph builder — the remaining back edges were re-wired as loop entries, a second set of markers was chained onto the first, and `__assign_loop_contexts` stopped with "Invalid iteration structure". Rodinia `nw`'s traceback walk (short-circuit header, three `continue`s) failed on every attempt, so no trial of `nw` could exist. Every back edge now gets its own end-of-iteration marker in the first pass. Feature check `explorer-multi-backedge` (fails on the shipped explorer, 14 s); Do-All/reduction sets unchanged on 2mm, vecsum, `is`; explorer tests 100/100 | found by the T0.6 re-run (`nw`: 3 of 3 attempts, a different error from the random crash) |
| 2026-09-18 | plan | **D12 — the core ten's `lu` slot.** The pre-registered group C names NPB `lu`; DiscoPoP cannot instrument it (the compile exceeds two hours in both layouts, §7 finding of 17 Sep), so no model-driven trial can exist for it. For the model-driven experiments (pilot, E1, E2, E3, E4, E8) the slot is taken by PolyBench `lu` — LU decomposition, the same "order matters" class, already packaged and sized (verification LARGE). NPB `lu` stays in E11 as a verify-only contestant (expert/RepoOMP outputs through the harness) and in E5 as the profiling-cost outlier. `kernel_groups.json` keys are leaf names, so `lu` already resolves to both; the runner is given the full name `polybench/lu` | the change is recorded before the first model run, as the plan requires |
| 2026-09-18 | plan | **Decisions D8–D11** (the author's go on A–D of §5i, 18:30): E10 runs before E1 and fixes E1's default configuration; the E1 model is chosen by the pilot (Haiku if ≥ 2 FASTER outcomes in group B, else Sonnet); `--budget 3` stays fixed and D3 is an efficiency study; H6 stays as registered with T0.9 as prior evidence | the author, on the review of §5i |
| 2026-09-18 | harness | `explorer_determinism.py` (T0.7 as a tool), `oracle_study.py` (T0.3), `merge_kernel_sizes.py` (rebuilds the committed size table from a T0.1 run, printing every change), `t0_chain.sh` (the D6 re-runs as one detached, pinned chain on the server: T0.1 → T0.5 → T0.6 → T0.2 → T0.8 → T0.7). The end-to-end review runs of 17–18 Sep, which lived in the session scratchpad, were rescued into `agent/runs/e2e_review_2026-09-18/` (16 configurations: every log, usage record, final source and candidate; no binaries or profiler output) and archived | the instruments must be reproducible tools, not shell loops; results must not live in a temporary directory |
| 2026-09-18 | harness | **Integrity guard** (`check_package`, `_tree_digest`, `PackageCorrupted`, `_save_trial` in `cli.py`; `prepare_calib.py` v4 writes `output_sha256`; `test_integrity.py`, 30 checks) — see §5j. A corrupted run exits with status 2. | the author: benchmarks must not be corrupted between experiments |
| 2026-09-18 | harness | **Results archive** (`agent/benchmark archive`, `agent/results/` tracked, `INDEX.md`, `README.md`; `server.sh fetch` archives; RUNBOOK §4 procedure and rule 6; `.gitignore` also ignores `prepared_single/` and `analysis/`) — see §5j. The old `t0_5_shares_mac/summary.json` study label "T0.3" renumbered to T0.5 (the study was renumbered in §5e; measurements untouched, noted in the file). | the author: results stored for the thesis with the data for graphs and findings |
| 2026-09-18 | harness | **Benchmarks in their original file layout (D6).** `prepare_polybench.py` v5 (`--layout project`, the default): `<kernel>.c` with the same three edits as before, `<kernel>.h`/`polybench.h`/`polybench.c` verbatim, `pb_harness.h`; 28/30 validate (cholesky, trmm fail the perturbed-input check in both layouts — they are OUT). `prepare_apps.py`: NPB as `<B>/<b>.cpp` + `common/` + `pb_harness.{hpp,cpp}` + generated `npbparams.hpp`, driver appended to the benchmark unit; md/pathfinder/nw/hotspot unchanged (one file originally); all validate against their originals on the Mac (libomp include path added for the originals; `-fopenmp` dropped from NPB-SER's original build, which uses no OpenMP). `agent/tools/bench.py` gives every tool one way to stage, build and profile a benchmark; T0.1/T0.2/T0.5/T0.6 use it. New `packaging_equivalence.py` (T0.8). Merged packages regenerable under `prepared_single/` for comparison only. | the author: "we should use the benchmark in its original format" |
| 2026-09-18 | harness | D4 applied in the packages: `main` excluded in every PolyBench kernel, hotspot and NPB (`npb_main`, the benchmark's driver, stays in scope); kept in md and pathfinder (T0.6: DiscoPoP's only loop patterns inside `main`); nw pending its T0.6 re-run | decision D4, evidence T0.5/T0.6 |
| 2026-09-18 | harness | Record §5h (the fast refresh explained, T0.9 numbers) and §5i (plan review: parameters and their reasons, changes applied, decisions A–D for the author); plan v14; instruments T0.8 and T0.9 | the author's questions of 18 Sep |
| 2026-09-18 | harness | `prepare_calib.py` v3: every repetition of a calibration kernel reads what the previous one wrote (`c[i] = 0.5 * c[i] + …`), in both layouts | the repeat loop was idempotent, and a model given no evidence "parallelised" it by doing the work in the last repetition only (run log `e2e_review_2026-09-18`). A calibration whose regions can be satisfied that way would report success on attempt 1 for nothing |
| 2026-09-18 | harness | **Project-layout benchmarks.** `meta.json` may carry `project: {units, include_dirs, cflags, ldflags}`; `profile_once` then profiles through a generated unity unit (compiled by its ABSOLUTE path — see Fix 78), `run_trial` copies the tree, rewrites every FileMapping path, passes `--project-dir` and the unit list to the agent, records `files_changed`, and computes `source_changed`, the pragma count and the scaffolding check on all files; `verify` builds every unit. `prepare_calib.py --layout project` emits `calib/*_proj` (kernel in its own unit). Smoke run `proj_smoke_local`: `privtemp_proj` and `vecsum_proj`, arm `discopop_gate` — DiscoPoP's pragma with `private(t)` applied in `src/kernel.c`, verified FASTER (2.17×, 1.58× at 8 threads), digests exact. Single-file benchmarks take no new path. | decision D6: merging is no longer required; the evaluation benchmarks stay merged until the author decides to switch (re-runs T0.1/T0.5/T0.6 for the switched ones) |
| 2026-09-18 | both | **Fix 78 (explorer + harness):** the explorer's AST-based variable classification matched files by `endswith("/" + path)`, and clang spells a unit included through a relative include directory as `./src/kern.c` — so every Do-All in such a unit lost its clauses (`private` missing = race). Explorer `ASTLoader.build_path_mapping` normalises the path first (23 explorer tests pass); the harness compiles the unity unit by absolute path. Found because the first project smoke run ended `no-change`: DiscoPoP's own pragma was dropped at `tsan`. | a `private` clause silently missing is exactly the kind of error the campaign must not carry |
| 2026-09-18 | harness | `prepare_calib.py` v2: EXTRALARGE sizes capped so every calibration program's static data stays under 2 GB (vecsum 70M per array, dotprod 100M) | `t0_1_calib` crashed on the server: x86-64 Linux cannot link a `.bss` above 2 GB without `-mcmodel=medium` |
| 2026-09-18 | harness | `scaffold.py`: two reused loop variables renamed; `mypy` clean on `cli.py`, `scaffold.py`, `prepare_calib.py`; 26 scaffold tests pass | hygiene found while adding the project path |
| 2026-09-18 | agent | **Multi-file programs (Fix 74, decision D6).** `--project-dir` (+ `--project-units/-include/-cflags/-ldflags`, `--build-cmd`, `--profile-only`). Profiling goes through a generated unity unit; every gate build goes through one seam (`gate/patching.run_build`) that stages the tree and replaces the file under test; regions are resolved to their own file through `FileMapping.txt`; dependences are filtered by file; the fast refresh moves only the rewritten file's positions; Settle keeps originals per file. Without `--project-dir` no new path is taken. Feature check `project-mode` (3 mutations killed). | the author: "combining the code into one file is not a good idea". Measured: DiscoPoP's own unit-by-unit profile reports recurrences outside `main`'s unit as Do-All (§5g D6) |
| 2026-09-18 | agent | **Full review, Fixes 64–73 and 75–77** (§5g): gate (rewrite judged by the old profile; schedule matrix that varied nothing; tolerance calibrated on one input and ignored by Settle), prompts and evidence (prompt generated from the gate that runs; `--evidence none` made evidence-free; arrays recognised from the source; names demangled; array accesses, loops already parallel, runtime share, private-index note), planning (best pattern per loop with alternates; separate key spaces), bookkeeping (line-keyed state moved and restored; covered = the parallel constructs; nested regions not attempted; re-profile failures noticed). Feature suite **28 checks**, each new one mutation-tested; mypy 0. | the author asked for the whole agent to be reviewed before the first experiment |
| 2026-09-17 | harness | **the full value dump is judged by relative error, not byte-equality** (`_dump_rel_err`, tolerance `DIGEST_REL_TOL` = 1e-9, the same the digest already used). `trial.json` gains `dump_max_rel_err` and `dump_seeded_max_rel_err`; `dump_exact` is still recorded. Records written before this keep the old rule, so rescoring an old run cannot silently turn it green. Also fixed: `verify-source` looked its size up by the bare benchmark name and so refused every application (`md is not in kernel_sizes.json`) | `md`'s final program was classified **BROKEN** although its digest matched exactly: its force loop is a reduction, and parallel summation reorders the additions (0.00042827175869921715 against …42, relative 3.5e-15). Byte-equality would mark every correct parallel reduction as wrong and would have distorted E1 and H2. The tolerance still catches real changes: the Jacobi-for-Gauss-Seidel rewrite differs by 3.8e-7 |
| 2026-09-17 | harness | **a timeout now kills the process GROUP** (`_kill_group` in `cli.py`, same in `share_study.py` and `dp_main_study.py`): every command starts in its own session and the whole group is killed when it times out. Verified with a command that leaves a sleeping grandchild — 0 processes left, rc −9 | `subprocess.run(timeout=…)` kills only the direct child. DiscoPoP's wrappers exec the compiler, so T0.6's timed-out compile of NPB `lu` kept a core busy for over an hour with no parent left to wait for it. In a campaign that would corrupt every timing measurement running beside it |
| 2026-09-17 | agent | **Fix 63: the clause stage refused correct pragmas on every PolyBench-style kernel.** `_read_after` counted three kinds of later mention as reads of a value the loop wrote: the next loop's own `for (j = 0; …)` header (PolyBench declares counters once per function and reuses them), a later `#pragma … private(j, k)` for the following loop, and a **comment** mentioning the name. Comments are now blanked, directives skipped, and a re-initialising loop header treated as killing the value (its span skipped, later uses still checked, because a nested loop may run zero times). Feature check `clause` gains those four cases: 8/8 verdicts, 16 scope cases; it fails on exactly the three reverted changes | found by reviewing `local_obs1` by hand: 2 of the 11 recorded candidates were rejected for correct pragmas (`2mm` `private(j, k)`, `jacobi-2d-imper` `private(i, j)`), the same rejection appears twice in `pilot2`, and the model then spent another attempt to produce a needless `lastprivate` |
| 2026-09-17 | harness | **scaffolding check relaxed in one direction:** a timed region that held only a call may now change, provided it still contains a loop afterwards and no new loop appears elsewhere in the same function outside it (computation may move into the timer, never out). Tests moved into the repository as `agent/tools/test_scaffold.py` (26 cases, including the two real inlining runs, a kernel inlined before the timer, a timed region emptied, and part of the computation moved in front of the timer); all pass. `rescore local_obs1`: `2mm` SCAFFOLD_MODIFIED → **FASTER** (3.41× at 4 threads, exact output on both inputs), `jacobi-2d-imper` → **parallel-not-faster** (0.30× at 2, 0.80× at 4), `seidel-2d` still SCAFFOLD_MODIFIED (`PB_PERTURB` rewritten); `pilot2` unchanged | in `local_obs1` the model copied the kernel into `main` inside the timer in two trials. The timing stayed honest, but the old rule flagged it (false positive) |
| 2026-09-16 | agent | **D3 mechanism (Fix 62):** `--budget-policy {fixed,share}` and `--budget-min`. Under `share`, a region gets `budget_min + round((budget − budget_min) · f / f_top)` attempts, where `f_top` is the largest share still queued; unmeasured regions get the minimum; `--budget 0` stays 0. Default stays `fixed`, so no arm changes until calibration fixes the values. New feature check `budget-policy` (9 cases) | author's decision D3 (§5d); values still to be calibrated |
| 2026-09-16 | both | **D1 and D2 implemented.** D1: `arms.json` `common_flags` gains `--min-runtime-share 0.01`, so every arm runs with it and the value is part of the committed pre-registration; `trials.csv` gains `min_runtime_share`, the value the agent actually received (last occurrence on its command line, as the agent parses it). D2: agent Fix 61, a measured region with predicted saving ≤ 0 (covered by an accepted rewrite) leaves the queue; new feature check `covered-skip` fails on the old code and passes on the fix | §5d, with evidence from T0.5 (D1) and from the scoring code (D2) |
| 2026-09-16 | both | **DiscoPoP's explorer is retried on the same profile when it crashes.** Agent Fix 60: `run_explorer` (up to 20 attempts, each retry logged) at the four places the agent runs the explorer (re-profile, fast refresh, reconstruction, dependence review). Harness: `profile_once` does the same for the once-per-run profile and records `explore_attempts` / `explore_failures`; `trial.json` / `trials.csv` gain `explorer_retries` and `profile_explore_attempts`. DiscoPoP itself is not modified | T0.7: on one `pathfinder` profile the explorer crashed in 15 of 20 runs. Without retries the harness would have lost every `pathfinder` trial of a run, and the agent reverted correct rewrites whenever the crash hit its re-profile. 20 attempts leave a 0.3 % chance of losing the step |
| 2026-09-16 | agent | Fix 59: `--exclude-functions` compares demangled names (`plan.regions.demangle`); new feature check `exclude-cxx` (fails on the old code, passes on the fix). Feature suite **19 passed, 0 failed**, mypy 0 | on every C++ application the exclusion list matched nothing, because DiscoPoP writes C++ names mangled. `md`'s queue held 26 candidates instead of 13, including the harness's own `pb_*` helpers |
| 2026-09-16 | harness | new instrument tools `share_study.py` (T0.5) and `dp_main_study.py` (T0.6), documented in §5e | evidence for the runtime-share floor (D1) and the `main` decision (D4) |
| 2026-09-16 | harness | **scaffolding check** (`agent/tools/scaffold.py`): after every agent trial the original and final source are compared on comment-free, whitespace-normalised text. (1) Every `pb_*`/`PB_*` definition (digest, perturbation, timer) must be unchanged. (2) The ordered list of lines using them outside those definitions must be unchanged. (3) The timed region must still cover what it covered: every line the rewrite left unchanged (matched by a line diff) must stay on the same side of the timer boundary, and a region that wraps only a call (PolyBench, `hotspot`, `nw`) must be identical. A failing trial gets the new outcome **`SCAFFOLD_MODIFIED`**, checked before correctness and speed and never counted as a result; `trial.json` records `scaffold`, `trials.csv` adds `scaffold_ok` / `scaffold_problems`, and the figures draw it in BROKEN's red with a hatch, so the validated palette is unchanged. New command `agent/benchmark rescore RUN` applies the check to finished runs (the old outcome is kept in `outcome_history`). **Verified:** all 37 packaged sources pass against themselves; 21 synthetic and real cases behave as intended. Caught: `pilot2`'s `PB_PERTURB` rewrite, a timer call moved before the kernel call, an edited timer or digest body, a removed perturbation, and a timer moved inside the computation windows of `md`, `pathfinder`, `mg`, `lu`, `is`, `hotspot` and `nw`. Left alone: comment edits, a pragma in the kernel, a whole kernel body replaced, and pragmas inside the computation windows of `md`, `pathfinder` and NPB. The first design missed a timer moved *within* a computation window (its text is unchanged), which is why check (3) compares unchanged lines rather than the timer lines. Rescoring existing runs: `pilot2` `parallel-not-faster` → `SCAFFOLD_MODIFIED`; the two smoke runs and `pilot_seidel` unchanged (checked, not skipped). Figures could not be drawn on the Mac (a matplotlib PDF font-embedding error that predates this change and persists with a fresh cache); the server draws them | `pilot2` kept a rewrite of the perturbation code as a parallelisation, and nothing prevented a rewrite from moving the timer calls, which would report a speedup that does not exist |
| 2026-09-16 | both | **the credential is checked before a campaign, and a failed call can no longer pass for a result.** Agent Fix 58: the CLI reports a rejected token as `is_error` with subtype `"success"` and **exit code 0**, and the SDK's exception interpolates the subtype, so every failure — auth, quota, transient — logged the identical string `Claude Code returned an error result: success`. The agent now reads the result body, raises `LLMConnectionError` on an authentication failure (fatal, no retry) and the CLI's own wording otherwise. Harness: `trial.json` / `trials.csv` gain `llm_call_failures`, and `job.sh` runs one probe call before the first trial and aborts the whole job if it fails | the first server pilot (`pilot_seidel`) recorded a clean `no-change` while all nine of its model calls had failed on a 401. Without this, a token that expires mid-campaign silently converts every remaining trial into a false negative — the agent would appear to decline where it never answered |
| 2026-09-16 | harness | **sizes are keyed by the full benchmark name** (`suite/benchmark`) in `agent/config/kernel_sizes.json`, in `size_table.py` and in the runner's `_verify_size` / `_timing_size`. The committed table was migrated: 26 of 27 entries carried over, and `lu` was **deliberately dropped** rather than guessed at, so both `polybench/lu` and `npb/lu` are re-measured under their own names. A bare name still resolves while only one suite claims it; where two do, the runner stops and says so | bare names collide — `lu` is both `polybench/lu` and `npb/lu`, and the first application size run silently gave NPB's `lu` the PolyBench kernel's figures (`SMALL` 0.00074 s, `LARGE` 1.06 s, against 2.3 s at SMALL measured during packaging). Nothing would have failed: every NPB `lu` trial would simply have been verified at the wrong size |
| 2026-09-16 | harness | `agent/docs/RUNBOOK.md` added: how to run the campaign from a cold start — parity and token setup, the command surface, per-experiment commands, what is already done, the traps that cost hours (dashed-flag quoting, per-kernel sizes, kernels too short to time, the speed check being off, DiscoPoP's reporting nondeterminism, NPB's inapplicable perturbation, Polly not being a scaling result), failure diagnosis, and the standing rules | the campaign has to survive a new session, a compacted context, or the author running it alone |
| 2026-09-16 | harness | **Rodinia `hotspot` packaged and validated — the applications are complete (7 of 7)**. It failed at SMALL first, and the cause is worth recording because it is exactly what a weaker check would have hidden: `compute_tran_temp` swaps two local pointers each iteration, so the answer ends in `result` for an odd iteration count and in `temp` for an even one (the original's own `writeoutput((1&sim_time) ? result : temp, …)`). The packaged driver had the parity reversed; at MINI's 10 iterations both buffers agreed on every cell and the check passed, at SMALL's 100 it differed in 1,241 of 262,144 cells. Ruled out first, each by direct test: `%g` versus `%.17g` printing (the dump now uses the original's own format per recipe), the `-fopenmp` build (identical differences with and without), thread count (the original is bit-identical at 1, 2 and 4 threads), and the generated input's file round-trip (0 mismatches in 262,144 values). The copied kernel was also diffed against the original's two functions: identical. It is the only one whose input is a file: the original reads a temperature grid and a power grid and writes its result to a third file. The packaged version generates both grids in-process, because the harness passes no arguments — **a change of data, not of computation**. To keep the comparison honest the packaged source can write the grids it generated (`-DPB_EMIT_INPUT`) in the original's own format, and the validator feeds those very files to the original: one generator, two programs, no second implementation to drift. Generated values carry three decimals (323.000–324.999 and 0.000–0.299) so the text the original parses and the value the packaged program holds are the same `float` — at finer precision the two differ in the last bits and the comparison would fail on formatting rather than on the computation. §1a removals: 1 disabled `#ifdef OMP_OFFLOAD` block, 1 `omp_set_num_threads()` call with its `num_omp_threads` declaration (the pragma it configures is disabled in the serial file), `omp.h`, the thread argument, `gettimeofday` timing, and `read_input`/`writeoutput` | `hotspot` is category A in the core ten and E1 needs it; its input arrives as 9–150 MB data files that the harness cannot pass |
| 2026-09-16 | harness | **NPB `is`, `mg`, `lu` packaged and validated** (1,609 / 2,124 / 4,134 lines). Each is the benchmark, `npbparams.hpp` and the four `common/*.cpp` merged into one translation unit; the benchmark's own `main` is renamed `npb_main` and its output — 14, 33 and 39 print sites — is redirected to **stderr** rather than rewritten, so stdout carries the digest alone. `pb_timer_start/stop` are injected at the benchmark's own timer calls (`T_BENCHMARKING`, `T_BENCH`, `timer_start(1)` inside `ssor`), each a single unambiguous site. Sizes are NPB's own classes S/W/A/B through the dataset guard: `is` keys off `CLASS`, `mg` and `lu` need explicit parameter tables (`NX/NY/NZ_DEFAULT`, `NIT_DEFAULT`, `LM`, `LT_DEFAULT`; `ISIZ1/2/3`, `ITMAX/INORM_DEFAULT`, `DT_DEFAULT`) | E1 needs the applications and E11 needs NPB; rewriting output from 86 print sites by pattern is exactly what went wrong on `md`, so the benchmark is left to print as it likes, out of the way |
| 2026-09-16 | harness | NPB packaging decisions, each a deviation worth citing: the **dump carries the verification verdict** (the only result the original also prints) while the **digest carries the values** — `passed_verification` and `partial_verify_vals` (`is`), `rnm2` (`mg`), `rsdnm`, `errnm`, `frc` (`lu`) — so the comparison is real and a rewrite still cannot move the norms unnoticed; **three declarations hoisted to file scope** (`mg`: `rnm2`, `verified`; `lu`: `verified`; `is` needed none, its state is already file-scope) so the driver can read the verified result, declaration-only, no computation touched; and **perturbation is not applicable** to these three — NPB checks against fixed reference values, so a perturbed input would fail its own verification, and the validator records that rather than reporting a no-op as a pass | the oracle for NPB is its own verification plus the digest; saying so is the honest alternative to a perturbation check that cannot mean anything here |
| 2026-09-16 | harness | **six of seven applications done and validated on the server** (`md`, `pathfinder`, `nw`, `is`, `mg`, `lu`): originals build and run, packaged dumps identical, digests valid, timed regions present. `hotspot` remains: it reads two multi-megabyte input files and the harness passes no arguments, so it needs in-program input generation — a change of data, not of computation, to be documented when it lands | — |
| 2026-09-16 | harness | **Rodinia `nw` packaged and validated** (533 values at MINI, 2,124 at SMALL, dump identical to the original, digest valid, timed region present, perturbation deterministic and finite). §1a removals, listed in its `meta.json`: **5 disabled `#ifdef OPENMP` / `OMP_OFFLOAD` blocks inside `nw_optimized`** — the serial file is the OpenMP version with `//#define OPENMP`, so the model would otherwise read the answer — 1 progress `printf` in the kernel, `omp.h`, the thread-count argument and its printed line, `gettimeofday` timing, and the `result.txt` write. The copied kernel was checked against the original minus those blocks: **identical, 105 lines on both sides** (the fifth removed block is the closing brace of the offload scope opened in the first, so the braces stay balanced) | `nw` is category C in the core ten (a wavefront where order matters), and E1 needs it; its packaging is also the §1a case the rule was written for |
| 2026-09-16 | harness | packager hardening from `nw`: a recipe may name the file an original writes its result to (`result_file`, `nw`'s `result.txt`), since the validator otherwise compares against progress prose on stdout; `#define`s the copied kernel needs are emitted **before** it, not with the driver; and a non-numeric token in either dump is now reported as a named failure instead of raising `ValueError` and destroying the whole validation file | three separate faults found by running it: `BLOCK_SIZE` undefined at the point of use, the kernel's own `printf` prose reaching stdout, and one bad recipe aborting the run for all of them |
| 2026-09-16 | harness | `agent/tools/prepare_apps.py` (generator v1): packages the applications on the kernels' contract — size from a dataset guard instead of argv (the harness passes none), the three-line digest on stdout with exact values under `-DPB_FULL_DUMP`, `DP_TIMED_REGION_SECONDS` on stderr, `argv[1]` as the perturbation seed, dead OpenMP code removed per §1a and listed in `meta.json`. Each recipe copies the original's computational functions **verbatim** and synthesises only input, timing and output; `--validate` compares the original's deterministic output against the packaged full dump. **`md` and `pathfinder` done and validated on the server** (`md` 33 values at MINI and SMALL; `pathfinder` 12,000 / 520,000), digests valid, timed region present, perturbation deterministic, changed and finite | E1 cannot go past PolyBench and E11 needs NPB's C files; the applications as shipped take their size from argv, print wall-clock timestamps, thread counts and elapsed time, and `md` carries its pragmas as comments |
| 2026-09-16 | harness | packaging decisions worth citing: `md`'s energies are compared at the original's own 6 significant digits (its stream prints `1221.16` while the dump prints `%.17g`); `md`'s final positions go into the digest but not the dump, so the dump stays exactly the original's energy table while a rewrite still cannot move the particles unnoticed; `pathfinder` keeps the original's `srand(9)`/`rand()%10` generation unperturbed so the dumps compare value for value, and switches to the packaging's generator only when a seed is given | a validator that excuses its own mismatch validates nothing — each of these was a real `dump_identical: false` that had to be understood before it was fixed |
| 2026-09-16 | harness | `verify-source` command (alias `vs`): judges a given source — or the benchmark's own source under extra compiler flags — through exactly the verification a trial gets, and writes a trial-shaped record (`kind: baseline`, candidate SHA-256, `--label` in place of the arm) into the same run store, so `report` and `plots` include baselines. `verify()` gained `final_flags`, applied to the candidate build only; `classify()` skips the `no-change` / `changed-not-parallel` branches for baselines, which are parallelizations by construction | E1's expert-OpenMP and Polly baselines and every contestant in E11 must be judged the same way as the agent's own results, without running the agent; a compiler baseline changes no source, so it cannot be expressed as a file to compare |
| 2026-09-16 | harness (first use) | Polly baseline on `2mm` at STANDARD, 24 threads, server: verified clean (dump identical, digest error 0, seeded input identical, kernel-basis timing) at **35.2×** — kernel 7.32 s → 0.21 s | above the thread count because Polly tiles and vectorises as well as parallelising; wherever the Polly column appears it is labelled a compiler baseline, not a scaling result, so no reader reads 35× as thread scaling |
| 2026-09-16 | harness | `agent/tools/profile_stability.py` (T0.2): profiles each kernel from scratch N times and records, per profile, the suggestions (`patterns.json` hash and counts by type), the Do-All blockers, the dependence file as written, the dependence file with ids and callpath numbers masked (a weak line-level measure), and **every dependence as a (sink, type, source, variable) multiset without per-run labels** → `profiles.csv`, `summary.json` | §5b measured on one kernel that the observed dependences are stable while the labels and the explorer's output are not; T0.2 quantifies that split over the core ten, and the one-profile-per-kernel-per-run rule depends on it. The multiset measure was added after the line-level hash was found to differ on `floyd-warshall` purely from regrouping, with no dependence changed |
| 2026-09-16 | agent | Fix 57: mypy baseline 82 → **0 errors**; type parameters added at 78 annotation sites and one variable renamed in `plan/scoring.py` (annotations only, feature suite 18/18) | a standing baseline hides new errors: every change had to be read as "82 → 82" instead of "clean". From here the rule is that mypy stays at zero |
| 2026-09-16 | harness | figures: `parallel-speed-not-measurable` drawn in `parallel-not-faster`'s blue with a hatch (no new hue, so the validated outcome palette is unchanged); the FASTER-rate figure leaves those trials out of its denominator; the report lists their ratios in a separate table | the new outcome is the same kind of result without a speed verdict; three candidate hues all failed the palette validator, and texture is the validated way to separate a variant |
| 2026-09-15 | harness (plan) | **reporting rule for kernels too short to time** (author decision, before E1): outcome `parallel-speed-not-measurable` when verification finds a correct parallel result on a kernel with no T0.1 verification size; excluded from FASTER rates, speedup statistics and H1; ratios in a separate "not speedups" table; correctness counts as for every kernel. `classify()`, report and figures follow it | at their largest runnable size these 8 kernels run 0.02–0.36 s serially, so parallelizing them shows thread start-up, not a speedup. Counting them as parallel-not-faster would penalise the arm that parallelizes more (`full` against `discopop_gate`) and bias H1; dropping them would lose their correctness data |
| 2026-09-15 | agent | Fix 55: `--timing-cflags` — extra compile flags for the builds the speed check times only (gate performance stage, Phase B noise floor and marginal measurement, Settle's final timing, timed reference); profiling and every correctness check keep the plain build. Feature check `timing-size` | E10 needs the speed check timed at a measurable size while profiling and correctness stay at SMALL |
| 2026-09-15 | agent | Fix 56: OpenMP builds on macOS add libomp's include directory (`gate/patching.py`, `gate/tsan.py`). Feature check `omp-include` | found while testing Fix 55: the gate linked Homebrew's libomp but not its headers, and LLVM 19 there ships no `omp.h`, so any candidate including `<omp.h>` was rejected at `openmp_compile` on the Mac only. Linux (the server) unaffected |
| 2026-09-15 | harness | `trials.csv` columns `verify_size`, `speed_measurable`, `require_speedup` (last switch wins, as in the agent), `timing_cflags` | E10 and the report of kernels too small to time are analysed from the CSV |
| 2026-09-15 | harness | `--verify-size` defaults to `per_kernel`: each kernel is verified at its T0.1 verification size from `agent/config/kernel_sizes.json`; a kernel with none is verified at the longest size T0.1 could run and its trial records `verify.speed_measurable = false`; sizes checked before a run starts and recorded as `verify_sizes` in the manifest | one global size cannot fit kernels whose serial time at STANDARD ranges from 5 ms (trisolv) to 10 s (3mm) — §7 `t0_1_sizes` |
| 2026-09-15 | harness | T0.1 result committed as `agent/config/kernel_sizes.json` (run log §7) | per-kernel timing and verification sizes are part of the pre-registered configuration |
| 2026-09-15 | harness (plan) | **new experiment — does the speed check prevent unnecessary changes?** Main experiments keep `--no-require-speedup` (common flag). A separate experiment on benchmarks where speed is measurable compares `full` (check off) with `speed_gate_large` (check on, timed at a larger per-kernel size while profiling and correctness stay at SMALL — needs a new agent timing option) and `speed_gate_small` (check on, timed at SMALL). Reads out changes and pragmas kept, diff size, rejections by the check, final speedup at the verification size, accepted slowdowns, calls, tokens, time. Hypotheses: the check at a measurable size removes changes that do not pay off without losing speedup; at SMALL it rejects changes the harness later finds faster | author: the speed check exists to stop unnecessary code changes and must not be dropped from the thesis, but at SMALL it would reject almost everything. Timing-only size change chosen over running the whole agent at a larger size, so the arms differ in one variable and profiling cost stays unchanged |
| 2026-09-15 | harness (plan) | **new experiment — head-to-head with RepoOMP (released outputs only).** Identical serial input: NPB 3.0 OpenMP C `is`, `mg`, `lu` (`XXX_#_omp.c`, pragmas removed) from RepoOMP's public repository (Apache-2.0, commit `45a1b9f`). Contestants: our agent (Haiku, Sonnet, ×5), RepoOMP's released outputs (`method_data/NPB/NPB_RepoOMP`: `_aaai`, `_reclaude`, `_regpt`), their released Claude Code and Codex baseline outputs (`NPB_cc`, `NPB_Codex`), NPB's expert OpenMP (`XXX_ori.c`), DiscoPoP alone, Polly. All judged by this harness: NPB verification, a second problem class as changed input, race detector, kernel speedup 1–24 threads, `-O3`, same host. File-name meanings (`reclaude`, `regpt`, `cc`) to be confirmed in the paper body before use | author decision. Their simplified tool is not re-run: its own README states it does not reach the `_aaai.c` level, so re-running it would under-represent RepoOMP. Caveats to report: their outputs were produced on other hardware and models; their repository builds at `-O0` (inflates speedups) — both their acceptance and ours are reported; public NPB OpenMP may be in model training data |
| 2026-09-15 | harness | **fixed configuration:** `arms.json` `common_flags` = `--no-require-speedup`, passed in every arm; runner records it per trial and in the manifest | author's decision. At the agent's size (SMALL) the serial kernels take 0.06–15 ms on the server (2mm 3 ms, lu 0.7 ms, trisolv 0.06 ms, seidel-2d 15 ms) — below OpenMP thread start-up, so the gate's `performance` stage judged noise and rejected correct rewrites (10 such rejections in the seeded smoke run). The agent now decides correctness; speed is judged only by the harness verification. Consequences: an accepted change may be correct but slower (reported as `parallel-not-faster`); E7 loses the `performance` stage and its threshold sub-study. Kernel timing (Fix 52) is still needed: it removes the dilution by setup and output (trisolv's kernel is 1 % of the program at SMALL, 12 % at STANDARD) |
| 2026-09-15 | harness | `agent/tools/size_table.py` (T0.1): smallest PolyBench size whose median serial kernel time reaches 1 s, pinned, 3 repeats → `sizes.csv`, `chosen.json` | single-run measurements: 2mm is measurable at STANDARD (6.8 s); lu and floyd-warshall need LARGE (1.1 s, 3.1 s); jacobi-2d-imper and trisolv stay below 0.1 s even at LARGE. First server attempt stopped at `atax` EXTRALARGE (segfault): that dataset is 100000 × 100000 doubles (≈ 80 GB), beyond the machine, and its element count (10¹⁰) also overflows the `int` product in the generated `PB_PERTURB(...)` call. The script now records a failed size and moves on; the crashed attempt's log is kept (`_launcher/t0_1_sizes_attempt1_crashed.log`). Known generator limit, not fixed: an array with more than 2³¹ elements (over 16 GB of doubles) overflows the count in `PB_PERTURB`; no verification size in use comes near that, and any size that did would be rejected as too large to run repeatedly |
| 2026-09-15 | harness | §1a packaging rule: remove disabled / commented / preprocessor-dead OpenMP code; expert versions used by region | Rodinia `nw`, burkardt `md` and `LULESH_SEQ` still contain their OpenMP versions, which the model would read |
| 2026-09-15 | agent (docs) | `claude_project/07-related-work.md`: RepoOMP code and its stated limits; ComPilot, ParaCodex, P4OMP, OMPILOT, ParBench | related work checked in September 2026; head-to-head with RepoOMP's public simplified tool offered, not decided |
| 2026-09-15 | server | setup (§5a): August LULESH profile deleted; agent fast-forwarded to `d9fd6c03`; wrappers installed; `anthropic` and `claude-agent-sdk` pinned to the Mac's versions; harness copied with rsync | start of the campaign on the server |
| 2026-09-15 | server | `discopop_explorer`, `discopop_library` and `discopop_gui` reinstalled as editable installs (`--no-deps`), as on the Mac | the copies installed on 2026-08-23 lacked the Do-All blocker detector — a silent evidence difference between Mac and server (§5a) |
| 2026-09-15 | Mac | venv `CXX_wrapper.sh` replaced by the checkout's copy | the parity check found a comment-only difference |
| 2026-09-15 | harness | `agent/tools/server.sh` and `agent/tools/job.sh`; README section "On the server" | sync, parity check, credential-safe launch with sweep, fetch of results (§4) |
| 2026-09-15 | harness | Polly baseline invocation for Ubuntu clang-20 recorded (§5a) | `-fpolly` is unavailable there and loading the plugin aborts |
| 2026-09-15 | harness | finding §5b; instrument study of DiscoPoP verdict stability added before E1 | the same program's profiles gave different Do-All verdicts, including an unsafe one |
| 2026-09-14 | harness | branch `agent-experiments` created from `4d7e3ce` | isolate the adaptation from upstream |
| 2026-09-14 | harness | `agent/tools/prepare_polybench.py` added | §2 |
| 2026-09-14 | harness | this file added | single thesis record |
| 2026-09-14 | harness | `agent/benchmark`, `agent/tools/cli.py`, `agent/config/arms.json` added | §3 |
| 2026-09-14 | harness | `agent/README.md` added | step-by-step usage for the author |
| 2026-09-14 | harness | `.gitignore`: `agent/prepared/`, `agent/runs/` | generated files and results stay out of git |
| 2026-09-14 | agent | C support: compiler and DiscoPoP wrapper chosen by source extension (`gate/toolchain.py`, `gate/patching.py`, `gate/tsan.py`, `profiling/tools.py`, `profiling/runner.py`, `profiling/__init__.py`, `plan/impact.py`) | §1; agent `docs/FIXES.md` Fix 51 |
| 2026-09-14 | agent | server toolchain: prefer LLVM 20 over 19, `DP_CC`/`DP_CXX` overrides, libarcher search under `/usr/lib/llvm-{20,19}` (`gate/toolchain.py`) | §5; Fix 51 |
| 2026-09-14 | agent (DiscoPoP scripts) | macOS fixes ported from the C++ wrappers to `profiler/scripts/CC_wrapper.sh` and `hotspot_detection/scripts/CC_wrapper.sh`; installed copies in the venv replaced | `discopop_cc` found no `stdio.h` and `discopop_hotspot_cc` no plugin on macOS; Linux behaviour unchanged. Fix 51 |
| 2026-09-14 | harness | packaging emits C; runner takes the language from `meta.json` (`discopop_cc`/`clang` + `-lm` for C) | §2, §3 |
| 2026-09-14 | harness | `--lang cpp` removed; generator v2 is C only | no-translation rule, §2 |
| 2026-09-14 | both | agent Fix 54: warning when hotspot measurements match no region; `--min-runtime-share` and `--exclude-functions`. Harness: FileMapping.txt pointed at each trial's copy; packaging meta lists out-of-scope functions (output, setup, allocation, own helpers) passed as `--exclude-functions`; `--min-runtime-share` harness option recorded in the manifest | smoke trial spent 35 calls on 11 regions: the profile copy got a new file id, so no measurement matched and ranking fell back to the proxy; with the fix and both filters seidel-2d offers 2 regions for restructuring instead of 11 |
| 2026-09-14 | both | agent Fix 53: every gate candidate saved with its verdict (`agent_patches/candidates/` + `candidates.jsonl`, Phase A and B) and per-call token usage logged to `$DP_LLM_USAGE_LOG`; harness sets the log per trial and records `llm_usage` (tokens, cache, cost equivalent, model seconds) and `candidates_recorded` in `trial.json` and `trials.csv` | E7 (gate as classifier) needs the rejected candidates; cost must be reported in tokens |
| 2026-09-14 | harness | plan v6: every `AgentArguments` field given one role (studied / fixed with reason / plumbing); chapter restructured as the whole system, then one region through each stage (planning → evidence & model → gate → maintenance → depth → cost); E2 adds evidence × feedback (budget) and a pre-registered conditional per-section ablation; E4 adds add-vs-delete (`--llm-deps`, H7b) and recon folded mode; E7 adds stage ablation by replay, perturbed-input ablation, threshold and size sensitivity; new E9 planning (hotspots vs proxy, `min_impact` offline); arms `no_evidence`, `discopop_pragmas_llmdeps`, `discopop_pragmas_recon_folded`, `full_no_hotspots`; ≈ 560 model trials with a fixed cut order | author: cover the remaining agent settings with a narrative, not unrelated experiments |
| 2026-09-14 | harness | plan v5: E4 moved to DiscoPoP-decides mode (new arm `discopop_pragmas_recon`); E3 notes that the refresh can only change decisions in its DiscoPoP row; new E8 restructuring depth 0/1/2 (arms `full_depth1`, `full_depth2`), H8/RQ8; ≈ 420 model trials | author asked how depth is covered: it was not. Reading `phases/phase_a.py` showed fast refresh runs only at the last depth level, reconstruction only inside it, and a model-written pragma bypasses the profile's keep/revert verdict — so the v4 E4 could not have shown an effect |
| 2026-09-14 | harness | plan v4 (academic standard): pre-registered hypotheses H1–H7 with refutation criteria; external baselines (expert OpenMP from Rodinia's own versions, Polly on LLVM 20); statistics (×5 repeats on headline comparisons, Wilcoxon signed-rank paired by benchmark, Cliff's delta, Wilson and bootstrap intervals, Holm–Bonferroni); new E7 gate-as-classifier (every candidate re-judged by the oracle); token cost; failure taxonomy; ≈ 370 model trials | author: experiments must meet master-thesis academic standard |
| 2026-09-14 | harness | plan §2 and `kernel_groups.json`: benchmark portfolio instead of PolyBench only — kernels (PolyBench 27), applications (NPB `is`/`mg`/`lu`, burkardt `md`, Rodinia `nw`/`pathfinder`/`hotspot`), scale (LULESH); core ten now mixes kernels and applications; E6 becomes LULESH; miniFE and NPB `bt` out of scope | author: use different benchmarks; a single suite is a threat to external validity |
| 2026-09-14 | both | speedup on the computation, not the process: generator v4 timer markers → `DP_TIMED_REGION_SECONDS` on stderr; agent gate reads it (Fix 52); harness verification reports kernel and program speedup | author's request; at small sizes setup and output dominate the process and hide kernel speedups |
| 2026-09-14 | harness | data capture (gate failures by stage and phase, region verdicts, Settle drops, host load, tool versions); `agent/tools/figures.py` + `plots` command (CSV + five figures, built automatically after each run); `agent/config/kernel_groups.json` (plan groups A/B/C/OUT) | the thesis needs the raw data and figures from every run, and runs must be combinable |
| 2026-09-14 | harness | `arms.json`: added `discopop_pragmas_fast` (`--no-llm-pragmas`) and `llm_pragmas_full_reprofile` (`--no-fast-refresh`); plan E3 is now the pragma-author × refresh 2×2, E4 reconstruction | the first plan's E3 compared `full` with `discopop_annotates`, which changes both features at once and confounds them |
| 2026-09-14 | harness | generator v3: optional perturbed input (`argv[1]` seed); runner passes `--check-input 7` to the agent and verifies on the seeded input too (`--check-seed`) | seidel-2d unsafe acceptance, §2, §7 |

### `smoke_local_seidel2d_c_seeded` — 2026-09-14, Mac, pipeline test after the perturbed-input fix

Same command as the first smoke run; generator v3 file, agent given `--check-input 7`,
verification with seed 7. Started before the kernel-timing change (agent Fix 52), so the
agent's speed gate still timed the whole process.

- Outcome `no-change`: 0 rewrites kept, 0 pragmas; Settle dropped 1 change. Verification
  clean on both inputs (dump exact, seeded dump exact, digest errors 0).
- The Jacobi-for-Gauss-Seidel class of rewrite no longer gets through: the agent's own gate
  rejected rewrites 7 times at `correctness` (including on input `7`), plus `tsan` ×2,
  `schedules`, `clause`, `compile`, `openmp_compile` once each.
- **10 rejections at `performance`** at SMALL, where the kernel is a small share of process
  time — the dilution that motivated timing the kernel (Fix 52).
- **Cost: 2,991 s (50 min) and 35 model calls for one trial**, against the ~15 min assumed in
  the plan's budget. Most calls went to cold regions (initialisation and print loops are
  ranked candidates too). Implication: at this rate the plan's ~560 trials do not fit in
  hours. To be measured in the server pilot (with kernel timing, which should cut
  performance-stage retries) before any experiment is launched; the mitigation — e.g. a
  pre-registered `min_impact` floor that skips regions below a runtime share, which E9
  then evaluates — must be decided before E1 and applied to all arms alike.

## 6a. Experiment plan

The full plan — fixed configuration, benchmark categories (A DiscoPoP-ready, B restructurable,
C order matters; 27 usable kernels, core ten), instrument studies T0.1–T0.4, experiments
E1–E6 mapped to RQ1–RQ7 and Chapter 6, time/usage budget, order of work and threats — is in
`agent/docs/EXPERIMENT_PLAN.html` (drafted 2026-09-14, pre-pilot estimates). Changes to the plan
are logged in §6.

Added 2026-09-15 (see §6 rows of that date):

- **E10 — does the speed check keep unnecessary changes out?** `full` (check off) vs
  `speed_gate_large` (check on, timed at the kernel's T0.1 timing size via `--timing-cflags`) vs
  `speed_gate_small` (check on, timed at SMALL). **H10:** timed at a measurable size, the check
  removes kept changes that do not pay off without lowering the verification speedup — refuted
  if `speed_gate_large` keeps as many correct-but-not-faster changes as `full` or delivers lower
  speedup. **H10b:** timed at SMALL, the check rejects changes that are faster at the
  verification size — refuted if none of its speed rejections is faster there.
- **E11 — against RepoOMP (released outputs only).** NPB 3.0 OpenMP C `is`, `mg`, `lu`; the
  agent vs RepoOMP's released outputs, their Claude Code and Codex baselines, NPB's expert
  version, DiscoPoP alone and Polly, all through this harness's verification. **H11:** on
  identical programs and verification, the agent's results are verified correct at least as
  often as RepoOMP's released outputs — refuted if a lower share of the agent's results passes.
  Speedup and fraction of expert speedup are reported descriptively.

## 7. Run log

### `t0_1_probe_sizes` — 2026-09-25, server, **T0.1 for the eight T0.11 probe loops** (no model)

- **Setup.** `size_table.py` on the eight indirect-addressing loops packaged for T0.11 (the author's decision 8: `s4112`, `s4113`, `s4114`, `s4115`, `s4117`, `s4121`, `s491`, `s353`), the same method as `t0_1_tsvc`: serial `-O3` build per dataset size, 3 runs, median of the timed region; lane 1.0 (cores 24–35) on its own — `e1c_a` had left it at 14:33, `e1c_d` held cores 36–47 and E2's node-0 lanes cores 0–23 (host load 15 at start, from those lanes). 15:00–15:03 UTC. Archived under `results/T0_instruments/T0.01_sizes/runs/t0_1_probe_sizes/`.
- **Result.** Timing size LARGE for all eight (STANDARD runs 0.07–0.13 s, under the 0.25 s target); verification size EXTRALARGE for six (4.1–5.6 s) and LARGE for `s4114` (1.24 s) and `s491` (1.20 s). Merged into `agent/config/kernel_sizes.json` (now 67 entries; the merge is noted in its `note`). The T0.11 draws `t0_11_probe_a/b/c` can now run at the campaign's sizes.

### `e2c_ab_1`, `e2c_ab_2`, `e2c_ab_3`, `e2c_ab_4`, `e2c_race_check`; `e1c_a`, `e1c_d`, `e1c_ad_race_check` — 2026-09-25, server, **E2 Parts A+B (Haiku) with the D38 twins, and E1c's controls** (540 + 45 trials; 315 race checks, no model)

- **Setup.** E2: commit `3f296eac` (agent code of E1c, `33673d7d`, plus the twin entry point); the 18 class-R loops × `full_b1`, `no_evidence`, `no_evidence_b1` and their twins `twin_full`, `twin_no_evidence`, plus `twin_dp` (DiscoPoP's pragmas unchecked, no model) × 5, four 12-core lanes (E1c's split), 25 Sep 05:15 → ≈ 20:00 UTC; `default`, `bare_llm`, `discopop_gate` are E1c's cells (same loops, same agent code). Controls: `e1c_a` (classes A: s000, vpvtv, s313 × the three E1c arms × 1) and `e1c_d` (class D: s321, s322, s323, s3112 × 3), same commit, lanes 1.0/1.1 after E2's node-1 lanes. The server checkout was synced once during E2's lanes 0.x, for two HTML documents and a registry line only (no file a trial reads). Race checks (`race_check.py`, the gate's TSan with archer and the schedule matrix, no model) over every program no gate saw: E2's three twin arms, the model alone in the controls. Read-outs in `results/E02_evidence_feedback_model/analysis/` and `results/E01c_clean_three_way/analysis/`.
- **E2 — every arm against the sequential original (class R, 90 trials each):**

  | arm | race-free FASTER | unusable programs |
  |---|---:|---:|
  | DiscoPoP alone (E1c) | 0 | 0 |
  | agent: evidence, 3 attempts (`default`, E1c) | 51 | **0** |
  | agent: evidence, 1 attempt (`full_b1`) | 48 | **0** |
  | agent: no evidence, 3 attempts (`no_evidence`) | **55** | **0** |
  | agent: no evidence, 1 attempt (`no_evidence_b1`) | 51 | **0** |
  | twin of `full_b1` (no gate) | 15 of 89 | 73 (66 BROKEN) |
  | twin of `no_evidence_b1` (no gate) | 17 of 90 | 71 (64 BROKEN) |
  | `twin_dp`: DiscoPoP's pragmas, nothing checked | 0 | 70 BROKEN, 20 no change |
  | the model alone (E1c) | 39 | 46 |

- **H12 (headline) — not supported.** DiscoPoP's evidence does not raise the race-free FASTER rate inside the pipeline (`full_b1` − `no_evidence_b1`: mean −0.03 per loop) nor on the twins (−0.02); larger inside on 3 loops, on the twins on 6, 9 tied; one-sided Wilcoxon p = 0.70, Cliff's δ −0.02 (counting corrected 25 Sep, §6: was 7 / 8 / 0.71).
- **H5b — not supported.** Two more attempts help about equally without evidence (+0.04) and with it (+0.03); p = 0.58.
- **H5d — not supported.** On the 8 loops where the clean model alone shipped a wrong program (s112, s121, s1213, s211, s241, s244, s281, s341) the evidence effect is −0.08, on the others 0.00 (Mann–Whitney one-sided p = 0.54). One loop stands out: on `s244` evidence LOWERS the one-attempt agent's success by 0.8 — worth a case study.
- **H13 — supported in every pairing.** The agent ships fewer unusable programs than its twin on 18 of 18 loops (one-sided Wilcoxon, as registered — evidence: p = 0.00006; no evidence: p = 0.00007) and than the model alone on 14, 0 the other way (p = 0.0004, every agent arm). **The gate's value, measured three ways:** agent vs its twin in race-free FASTER, 12 loops v 4 (one-sided p = 0.013) and 10 v 3 (p = 0.003); `twin_dp` — DiscoPoP's own pragmas without the gate — wrong in 70 of 90 trials (the D38 prediction); every twin's BROKEN programs are mostly DiscoPoP's unchecked pragmas (twin_full 55 of its 66 BROKEN fail TSan). Agent vs model alone in race-free FASTER: `no_evidence` 55 v 39, ahead on 10 loops v 4, one-sided p = 0.044; the other arms p = 0.08–0.14.
- **Reading.** On TSVC class R with Haiku, DiscoPoP's measured evidence adds nothing to the model's reach, inside the pipeline or without it — H5b, H5d and H12 all fail, and the best arm is the agent WITHOUT evidence at three attempts (55 of 90). What the pipeline adds is the gate: every agent arm ships no unusable program, where the same model without the gate ships 46 of 90 (the model alone), 71 of 90 and 73 of 89 (the twins), and DiscoPoP's own suggestions, unchecked, are wrong in 78 % of trials. The harder tier (E2-app, LULESH / NPB-C, D-decision 7) is where evidence may still matter — the dependences there are not visible in the code the model reads.
- **E1c's controls.** Class A (no harm): DiscoPoP alone 3 of 3 FASTER (3.67×), the agent 2 of 2 (3.63×; its third trial is the `s313` harness edit, to be repeated), the model alone 2 of 3 (4.24×; `vpvtv` does not compile). Class D (must decline): the agent declined all 12; DiscoPoP alone 0 parallel; **the model alone shipped 9 unusable programs of 12** (6 BROKEN, 2 not compiling, 1 slower). Race check of the model alone: 2 of its 3 FASTER clean; 2 programs not judgeable.

### `e1c_r_1`, `e1c_r_2`, `e1c_r_3`, `e1c_r_4`, `e1c_race_check` — 2026-09-24/25, server, **E1 clean: the three-way main comparison on TSVC class R** (270 trials, Haiku; 90 race checks, no model)

- **Setup.** Commit `33673d7d` (agent v2: D32, D33, Fixes 91–92; packages v3 without the header hint, D36; the model confined to its workspace, Fix 95; the model alone with the MIRROR prompt, D37; per-benchmark explorer limit). The 18 class-R loops × `discopop_gate`, `default`, `bare_llm` × 5, threads 6,12, repeats 5, check seed 7, on four 12-core lanes (`--node N.H`, split 5/5/4/4 loops), 24 Sep 18:33 → 25 Sep ≈ 04:50 UTC; every lane's credential sweep clean. `e1c_race_check`: `race_check.py` (the gate's TSan with archer and the schedule matrix) over all 90 `bare_llm` trials on the server, 25 Sep. Read-out `results/E01c_clean_three_way/analysis/main_comparison_stats.md` (`--arm default --three-way default --races …`).
- **The three arms against the sequential original (class R, 90 trials each):**

  | | DiscoPoP alone | DiscoPoP + agent | the model alone |
  |---|---:|---:|---:|
  | verified parallel program | 0 | 55 (61 %) | 64 (71 %) |
  | FASTER (≥ 1.1×) | 0 | **51 (57 %, CI 46–66)** | 44 (49 %, CI 39–59) |
  | FASTER and race-free | 0 | **51** | **39 (43 %, CI 34–54)** |
  | BROKEN (wrong output) | 0 | **0** | **16** |
  | correct but slower (< 0.91×) | 0 | 0 | 17 |
  | racy (TSan) | 0 | 0 | 5 (all `s293`: every thread reads `a[0]` while iteration 0 writes the same value — right answer, still a data race the gate rejects) |
  | does not compile | 0 | 0 | 8 |
  | **unusable programs** | **0** | **0** | **46 (51 %)** |
  | median speedup of the FASTER trials | — | 2.67× | 2.84× |

- **H13 (trust), its first test: supported.** Per loop, the agent ships fewer unusable programs on 14, the model alone on 0, 4 tied; paired Wilcoxon one-sided p = 0.0004. The model alone's 46 unusable programs, every one a result: BROKEN on `s112`, `s121` ×3, `s1213` ×3, `s211` ×3, `s241` ×2, `s244`, `s281` ×2, `s341`; not compiling on `s1213` ×2, `s211`, `s252`, `s254`, `s255`, `s281`, `s331`; slower on `s112` ×4, `s121` ×2, `s241`, `s243` ×4, …; racy `s293` ×5 (full list in the read-out).
- **Reach: the agent is now ahead, not significantly.** Race-free FASTER per loop: agent ahead on 10, the model alone on 4 (`s212` 5 v 3, `s244` 4 v 0, `s331` 2 v 0, `s281` 2 v 1), 4 tied; p (agent ahead) = 0.13, two-sided 0.26. FASTER alone: 9 v 4, p = 0.23. Where only the agent succeeds: `s121`, `s1213`, `s241`, `s243` (the model alone ships only unusable programs there), `s211` 3 v 1. Neither arm: `s112`, `s341` (the agent declines; the model alone ships 10 unusable programs).
- **Agent vs DiscoPoP alone (D19): gained 51, gained-not-faster 4, neither 35, unsafe 0.** Speed paired by loop: median 1.17× (bootstrap CI 1.00–2.75×), Wilcoxon one-sided p = 0.0002 over 12 non-zero pairs, Cliff's δ +0.67. H1 holds on the clean packages with agent v2. The floor (D32) found DiscoPoP alone keeping nothing in 90 of 90 (`dp_floor = original`, as expected on class R).
- **Process.** Agent: 126 model calls (0 failed), 92 full re-profiles, 22 explorer stalls (at the 60 s limit, redrawn), mean 372 s per trial (median 267) + 65 s verification, 16.1 USD-eq; D33 kept a joint set in 1 trial, none of the 51 FASTER came through it. The model alone: 90 calls, mean 101 s + 92 s verification, 8.1 USD-eq. DiscoPoP alone: 41 s + 75 s.
- **Against the hinted runs (E1, E1-bare), descriptively:** the agent 44 → 51 FASTER (v1 → v2 and hint removed); the model alone 58 → 44 FASTER and 53 → 39 race-free, unusable 35 → 46 (8 not compiling where E1-bare had 1). Two things changed for the model alone at once — the hint left the source (D36) and the prompt became the mirror (D37) — so the drop is not attributed to either; `d36_hint_check` (N = 3) found the hint's effect not one-directional.
- **Reading.** On clean packages the pipeline delivers more correct, race-free speedups than the same model alone (51 v 39, not significant per loop at 18 loops × 5) and ships no unusable program where the model alone ships 46 of 90 — the trust result is significant, the reach result is not. The classes A and D controls (`e1c_a`, `e1c_d`) complete E1c.

### `d38_twin_smoke` — 2026-09-24, Mac, **the twin runner (D38) through the real harness, SDK and confinement** (2 trials, 1 Haiku call)

- **Setup.** Commit `236384e4` + uncommitted harness lines of the same work (the agent itself identical to E1c's `33673d7d`). `tsvc/s121` × `twin_dp` (the twin of `discopop_gate`: `--budget 0`, no model) and `twin_full` (the twin of `full_b1`), ×1, verified at SMALL with 2 threads and 1 repeat — **wiring only, no speed claim**: the Mac was 4 GB into swap, and a first attempt at the per-kernel size (EXTRALARGE) was stopped after its verification ran at 16 % CPU for many minutes.
- **`twin_dp` → BROKEN.** This run's profile draw had DiscoPoP report `s121`'s loop (`a[i] = a[i+1] + b[i]`, an anti-dependence) as a Do-All — the stopped first attempt's draw had reported nothing applicable (DiscoPoP's draw variation, T0.2/T0.7). The twin inserted `#pragma omp parallel for private(j)` unchecked; the parallel program's output differs (max relative error 2.4 %). The agent's `discopop_gate` arm puts the same pragma through the gate, which rejects it. **This is the D38 prediction on its first trial:** DiscoPoP without the gate ships its false positives — recorded as a result (H13).
- **`twin_full` → parallel, output exact (not faster at SMALL on the Mac).** One call on the region the agent asks about first (loop 1:81, lines 134–140), with the agent's own request; the model wrote the loop through a heap buffer (`a_temp[i] = a[i+1] + b[i]`, then a copy loop); kept unchecked; re-profiled (4 new regions at depth 1, skipped at `--restructure-depth 0`); DiscoPoP reported both new loops as Do-All and the twin inserted both pragmas unchecked. 172 s, 0.155 USD-eq, 127 s of it the model. Every twin field parsed (`twin_asked` 1, `twin_edited` 1, `twin_dp_inserted` 2, `llm_calls` 1); `agent_patches/twin_model_program.c` holds the program before DiscoPoP's pragmas.
- **Reading.** The runner works end to end: the arms' settings verified through the twin's own entry point, the launch printout lists `twin_of`, the model is confined to its workspace, and the harness judges the result like any trial. Archived at `results/E02_evidence_feedback_model/preflight/d38_twin_smoke/`.

### `e2c_smoke`, `d36_hint_check` — 2026-09-23, server, **the clean pre-flight (v3 packages) and the author's single-example check of the hint** (34 trials, Haiku)

- **Setup.** Commit `1be54f01` (packages v3 without the header hint, D36; Fix 95; the model alone with the MINIMAL prompt — the mirror prompt came later that evening, `fc98efb7`). `e2c_smoke`: `tsvc/s121`, `s281` × every E2 and E2-source arm + `discopop_gate` + `bare_llm`, ×1, node 0. `d36_hint_check`: `s331`, `s281`, `s241` × `bare_llm_contract` (E1-bare's exact prompt) and `bare_llm` (minimal) ×3, node 1. Host load ≈ 5,000; both sweeps clean.
- **`e2c_smoke` — every arm ran its own path.** Agent: `s121` FASTER in `full_b1`, `no_evidence_b1`, `hotspot_only_b1`, no-change in `default`, `no_evidence`, `compiler_remarks_b1`; `s281` FASTER in `full_b1`, `no_evidence`, no-change in the other four. **All five FASTER came through D33** (`phase_b_joint_kept` 1, two pragmas deferred as slower alone). DiscoPoP alone: no-change on both, floor skipped; every agent arm `dp_floor = original` (class R). The model alone (minimal prompt): BROKEN on both. **The two slowest trials (750 s, 861 s) each lost 600 s to one explorer stall** — what the per-benchmark explorer limit (60 s on TSVC) removes.
- **`d36_hint_check` — does the comment in the header matter?** Same model, same loops; E1-bare had the old prompt AND the comment:

  | loop | E1-bare: old prompt, WITH the comment | old prompt, WITHOUT it | minimal prompt, without it |
  |---|---|---|---|
  | `s331` | 5/5 FASTER | 2/3 FASTER (+1 parallel, not faster) | 1/3 FASTER (+2 not faster) |
  | `s281` | 5/5 FASTER | 0/3 — **2 BROKEN**, 1 no-change | **3/3 FASTER** |
  | `s241` | 1/5 FASTER, **3 BROKEN** | 2/3 FASTER, 0 BROKEN | 0/3, 1 BROKEN |

  **Reading: the comment was not harmless, and its effect is not one-directional.** Removing it lowered the old prompt's wins on `s331` and `s281` and raised them on `s241` (where "node splitting (preload the old a[i+1])" went with three wrong programs in E1-bare); on `s281` the minimal prompt without it won 3 of 3 where the old prompt without it won none. At three trials a loop the model's own variance is as large as any of these differences, so no size or direction is claimed — only that E1-bare's per-loop numbers cannot stand as clean. *Correction (same night): in the conversation this check was first summarised, on its first seven trials, as "the comment was doing a lot of the work"; the full 18 do not support that.* The clean redo (18 loops × 5, the model alone on the mirror prompt) is where the model alone is measured.

### `e2_smoke_a`, `e2_smoke_b`, `e2_smoke_sonnet`, `e2_v2_paths` — 2026-09-23, server, **E2's pre-flight on agent v2: every arm runs, and v2's two new Phase B paths work end to end** (14 model trials + 2 DiscoPoP alone, 13 programs without a model)

- **Setup.** Haiku smokes at `b51fc735` (`e2_smoke_a` = `tsvc/s121` on NUMA node 0, `e2_smoke_b` = `tsvc/s281` on node 1): `discopop_gate`, `default`, `full_b1`, `no_evidence`, `no_evidence_b1`, `compiler_remarks_b1`, `hotspot_only_b1` × 1, threads 6/12, 5 repeats, host load 4,900–5,700 from other users. Then at `8ac62000` (after the harness fixes below): `e2_smoke_sonnet` (`s121`, `s281` × `full_b1` × `claude-sonnet-5`, node 0) and `e2_v2_paths` (node 1, no model). Arm check passed; auth ok; both credential sweeps clean.
- **Haiku, 14 trials:**

  | arm | `s121` | `s281` |
  |---|---|---|
  | `discopop_gate` | no-change (DiscoPoP's one pragma racy, TSan) | no-change (no candidate) |
  | `default` | no-change — rewrite kept, Settle 0.56× | no-change — one half annotated, 0.81× alone, dropped |
  | `full_b1` | no-change — Settle 0.77× | no-change — first call wrong (`correctness`), second region: one half, dropped |
  | `no_evidence` | no-change — Settle 0.72× | **FASTER** — D33 set 2.91×, Settle 2.80×; kernel 2.16× / 3.24× (6 / 12 threads) |
  | `no_evidence_b1` | no-change — Settle 0.13× | no-change — one half, 0.54× alone, dropped |
  | `compiler_remarks_b1` | no-change — Settle 0.13×; DiscoPoP's pragma over a `return` rejected at `openmp_compile` | **FASTER** — D33 set 2.98×, Settle 2.99×; kernel 2.04× / 2.88× |
  | `hotspot_only_b1` | no-change — both calls' rewrites passed the gate, DiscoPoP found no parallelism in either, reverted; its pragma on the original loop racy | **FASTER** — D33 set 3.05×, Settle 2.64×; kernel 2.17× / 3.26× |

  Output exact on both inputs in all three FASTER. **Every Phase-A rewrite on `s121` passed the gate; none survived.** In five arms the kept rewrite lost at Settle — each copies the array with `memcpy` every repetition (sequential, so the program is slower — the E1 finding, §6); in `hotspot_only_b1` DiscoPoP found no parallelism in either rewrite (the first only moved `j` into the loop) and Phase A reverted both. **On `s281` the model wrote the same `LEN/2` split in all six model arms; the three that did not win lost to DiscoPoP's draw**, not to the agent: the re-profile after the rewrite reported a `do_all` on only one half, so there was nothing for D33 to combine and the lone pragma (slower alone) was dropped. The three that won are the three draws in which DiscoPoP reported both halves — the draw-to-draw variation of T0.2, here deciding the outcome of a trial. It will add variance to every E2 cell on `s281` whose model splits the loop (Sonnet's mirror pairing below is one loop, with no half to lose).
- **Sonnet, 2 trials, both FASTER.** `s121`: Sonnet wrote the snapshot as a copy LOOP rather than `memcpy`, DiscoPoP annotated both loops, each 0.56–0.57× alone, **the set 3.04× (each needed: 0.22–0.23× without it) — D33 in a model-driven trial**; Settle 1.16×, harness 1.41× / 1.34×, exact. 33 min, of which 30 were three explorer stalls (L5) on the re-profile. `s281`: a different restructuring — iteration `k` computes both `a[k]` and its mirror `a[LEN−1−k]` (which needs the NEW `a[k]`, and gets it), one fully parallel loop; one pragma, 4.06× alone, Settle 5.00×, harness **3.67× / 4.78×**, exact. One draw each: Haiku-vs-Sonnet is E2 Part A's question, not this smoke's.
- **`e2_v2_paths` — v2's new Phase B paths on E1's own rewrites, no model** (`default_arm_ceiling.py LOOP=FILE`, the 13 programs of `e1b_v2_sources` with pragmas stripped, `--budget 0`; read-out `results/E02_evidence_feedback_model/preflight/e2_v2_paths/README.md`): **12 of 13 kept; D33's joint judgement ran in 8** (`s1213` rep 1, `s121` reps 2 and 5, `s244` rep 1 — a set of three —, all four `s281`), **Fix 91's clause stage passed both halves of every `s281` split** (0 clause rejections), the four others' pragmas paid alone this time (single marginals near 1.0 are unstable on the shared host, T0.4), and the slow-rewrite control `s121` rep 4 was correctly NOT kept (a lone deferred pragma, dropped). Settle's reference in this tool is the rewrite, not TSVC's original, so its 2.6–4.1× are not speedups over the original (those are `e1b_v2_verify`'s).
- **Every arm's code path ran.** `--budget 1` is per REGION: a b1 trial makes a second call when the loop's rewrite fails and the enclosing function is next (`s121` `hotspot_only_b1`, `s281` `full_b1`), so E2 reports calls per trial as measured, not as the budget. **No gate feedback crosses regions** (checked in `phases/phase_a.py`: `failure_reason` is reset per region, line 211, and the message history starts empty per region, line 255; a failed region's rewrite is reverted) — the second call is an independent draw on the enclosing function, available to the budget-3 arms in the same way, so the evidence × feedback contrast (H5b) is not weakened. `compiler_remarks_b1`: the remarks file is generated on the server's clang-20 and reaches the agent (`--evidence-file` on its command line; `s121`: three Polly "possibly aliasing pointer" remarks — thin, and exactly what that tool says). The prompt text of each arm is verified offline by the feature check `prompt-ablation`; token counts cannot show it (Claude Code's own system prompt dominates them).
- **Found by reading the logs (§6, fixed at `8ac62000`):** `phase_b_deferred` counted Phase A's "deferred to Phase B" too (every smoke trial rescored: e.g. `s281` `no_evidence` 4 → 2), and the launch printout hid `--evidence-file` / `--prompt-omit`.
- **For E2's size and cost:** E1's measured mean for a TSVC class-R `default` trial is 8.8 min (agent + verification, 26 explorer stalls in 90 trials included) → ≈ 155 lane-hours for ≈ 1,056 model trials, ≈ 3–3.5 days on two lanes *(corrected the same evening: first written as "≈ 77 lane-hours", which is the wall-clock hours on two lanes)*. USD-equivalent per model trial here: Haiku 0.05–0.27 (mean 0.12), Sonnet 0.22–0.31 → E2 ≈ 150.
- **Verdict: the pre-flight passes.** Every arm of E2 and E2-source runs its own code path on the server; D33 and Fix 91 work end to end, with a model and without one; nothing unsafe was accepted (14 model trials). E2 is ready to launch once the author fixes N for E2-C/E2-D and the order.

### `e1_bare_a`, `e1_bare_b` — 2026-09-23, server, **E1-bare: the same model alone, no DiscoPoP, no gate** (90 trials, Haiku)

**Setup.** Commit `cf0d5d96`; arm `bare_llm` (`discopop_agent/bare_llm.py`: the program and the
contract text, one call, no profile, no gate, no feedback); Haiku 4.5; TSVC class R, the 18 loops
of E1's primary set × 5; verification exactly as E1 (per-kernel size, 6 / 12 threads, 5
repeats, seeded input — the harness's verification code is unchanged since E1's `00d4594f`).
`e1_bare_a` (node 0, `s112 s121 s1213 s127 s211 s212 s241 s243 s244`) 04:59–07:32 UTC,
`e1_bare_b` (node 1, the other nine) 04:59–08:12 UTC; both `SWEEP: clean`. Its `default`
counterpart and DiscoPoP-alone baseline are E1's own trials (`e1_r_a`, `e1_r_b`). Read-out:
`results/E01b_bare_llm/analysis/` — the README there has the commands, the per-loop table and
every BROKEN trial by cause.

**Deviations, recorded first.** (1) The runner profiles every benchmark before its trials, so
DiscoPoP profiled all 18 loops although this arm reads nothing from it; 7 of the 18 draws hit the
random explorer stall (600 s each, draw repeated) — cost only. (2) Two trials have no verdict:
`s243` rep 4 reordered the scaffold calls (`SCAFFOLD_MODIFIED`), `s244` rep 2 wrote `private(i)`
for a loop-local `i` (does not compile); rates are over 88. (3) The arm ran two days after its
counterpart, on the same host, sizes and thread counts (so the pairing rule counts the timings as
comparable), at host load 3,027–7,392 (median 4,288). (4) The pre-registered read-out is the rates
and the BROKEN named; the bare arm's paired speed statistic (2.41×, p = 0.0002) is over its
CORRECT trials only (a wrong program is given no speed; `s211` has none left), while the agent's
1.08× counts every `no-change` as 1.00× — the two are not comparable and are not compared.

| TSVC class R, 18 loops × 5 | model alone (`bare_llm`) | DiscoPoP + agent (`default`, E1) | DiscoPoP alone |
|---|---|---|---|
| verified parallel program | **71 of 88** (81 %, CI 71–88 %) | 46 of 90 (51 %, CI 41–61 %) | 0 of 90 |
| FASTER | **58 of 88** (66 %, CI 56–75 %) | 44 of 90 (49 %, CI 39–59 %) | 0 of 90 |
| **BROKEN — a wrong program shipped** | **17** (19 %), in 9 of 18 loops | **0** | 0 |
| correct but slower (`worse`) shipped | 12 | 0 (Settle dropped 15) | 0 |
| loops FASTER at least once / in 5 of 5 | 16 / 8 | 14 / 5 | 0 / 0 |
| model calls, cost | 90, 7.82 USD-eq. | 125, 13.95 USD-eq. | — |

**C2 — what the gate prevents: 17 wrong programs and 12 slower ones in 88.** Every one of the
17 is wrong on the output check alone, and eight are one shape: a loop distribution that ignores
which value the original read (`s211` ×3, `s212`, `s241`, `s243`, `s244`, `s1213`); the rest are
races (`s211` ×2, `s112` ×2, `s241`), a Gauss–Seidel turned Jacobi (`s1213`, the seidel-2d error
of §2 in a TSVC loop), a snapshot taken before `pb_mix` changes the input (`s241`), a two-term sum
turned into a prefix scan (`s252`) and a compaction whose order depends on thread timing (`s341`).
E1's gate rejected **23 wrong rewrites in 19 agent trials**, on seven of the nine loops where
the model alone went wrong (`s112` 3, `s1213` 4, `s211` 3, `s212` 2, `s241` 5, `s243` 2,
`s244` 3) and on `s281` 1; on `s252` and `s341` the agent's model never produced a wrong rewrite. Without an oracle a user of the
model alone cannot tell the 17 from the 58 — which is what the gate is.

**Not what was expected: the model alone reaches MORE.** The plan read the bare arm's FASTER
count as "what the evidence and the feedback add"; on TSVC class R they add nothing to reach —
58 vs 44 FASTER, 16 vs 14 loops. The gap sits on four loops, each with a visible cause:
`s281` 5 vs 0 (the model alone splits the index range at `LEN/2`; the agent's model copied the
array per repetition and Settle dropped it — **wrong, corrected the same day below**: the agent's
model wrote the same split), `s331` 5 vs 0 (a max reduction — the pragma DiscoPoP
cannot write, T0.13; under D23 the agent's pragmas are DiscoPoP's), `s121` 3 vs 0 (both buffer
`a`; the model alone copies with a parallel loop, the agent's rewrites used `memcpy` — **only rep 3
did, corrected below**), `s244` 3 vs
1 (the model alone removes a dead store). The agent is ahead where the model alone ships wrong
programs: `s211` 1 vs 0 (5 BROKEN), `s112` 1 vs 0 (2 BROKEN), `s252` 3 vs 1. E1-bare changes
everything at once — evidence, gate, feedback, who writes the pragma, the role text — so it cannot
say which of them costs the four loops; E2 Part A (evidence none vs DiscoPoP, same pipeline) and
E3 (the model writes the pragmas) separate them, and `s281`, `s121` are among E2-C/D's seven
loops, `s331`, `s341` are E3's.

**Not checked for the model alone: races that change no printed value.** Its 71 parallel
programs passed the harness's verification (full dump on two inputs, digest at 6 and 12 threads,
5 repeats each) but not TSan or schedule stress, which only the agent's gate runs. A no-model
check — the gate's race stages over those 71 programs — would close this; **run the same day,
below**.

**What it changes.** H2 and C2 stand on a measured counterfactual: the same model, unguarded,
ships a wrong program in one trial in five on this set. What the pipeline adds over the model is
TRUST, not reach — the reach claim (C1) is against DiscoPoP alone and is unchanged. The four
loops are recorded as a limitation of `default` and as the question E2/E3 answer.

**Two checks the same afternoon (no model), and what they correct.** The author asked for the race
check and for WHY the agent reaches less. Both are in `results/E01b_bare_llm/checks/`.

*`e1b_race_check`* (`tools/race_check.py`, server, clang-20 with archer): every model-alone program
through the agent's own `validate(mode="safety")` — TSan, the schedule matrix, output on two inputs —
with the agent's 46 parallel TSVC programs as the positive control: **46 of 46 clean**. Of the model
alone's 58 FASTER programs **53 are clean**; 4 are races (`s293` reps 1–4: a pragma on `a[i] = a[0]`,
benign in effect — the value written is the value read — a data race nonetheless) and 1 cannot be
judged (`s341` rep 5 calls the OpenMP runtime, which the gate's first compile does not link — a gate
blind spot). All 13 parallel-not-faster programs are clean; **the gate stops all 17 BROKEN ones**
(TSan 9, output 7, schedule matrix 1). Race-checked, the model alone is FASTER in 53 of 88, the agent
in 44 of 90 — the reading stands.

*`e1b_marginal_replay`* (`tools/marginal_replay.py`, server): all 90 agent trials had a rewrite pass
Phase A; of the 44 that ended `no-change`, 15 fell at Settle (the copy-per-repetition finding of
`e1_r_a/b`, confirmed), 11 because DiscoPoP's pragmas on the rewrite raced or changed the output (the
gate right; this includes all of `s331` and `s341`), and **18 because Phase B's speed check dropped
pragmas that had passed every safety stage**. The replay rebuilds each measured state from the
archived patches and calls the agent's own `measure_marginal` at 6, 12 and all threads. The
hypothesis written into the tool — that the verdict depends on the thread count — is **refuted**:
the dropped pragmas measure below 1× at every thread count. What the data shows instead: Phase B
judges each pragma ALONE against the sequential rewrite, and **in 7 of the 18 trials the rewrite
pays only with all its pragmas together** — each alone 0.6–1.1× (or unstably near 1.0 on this host),
together 2.5–4.0× the rewrite and **1.2–2.8× the original** at 12 threads (`s1213` reps 1, 3; `s121`
reps 1, 2, 5; `s244` rep 1; `s112` rep 4). The other 11 are slower than the original even with every
pragma (0.10–0.97×): correct drops. Controls (`s127`, `s254`, `s291`, won in E1) replay at 1.9–3.9×.

**Corrections.** (1) `s281`: the agent's model wrote the SAME `LEN/2` split as the model alone in all
five repeats. It lost after the model — in reps 2–5 the gate's clause stage rejected DiscoPoP's
`private(x)` on the first half ("the loop writes `x` and later code reads it"; the only later reads
are in the second loop, after a write in the same iteration, and nothing reads `x` after the loops:
**a false reject**, an E7 labelled case), in rep 1 DiscoPoP reported a do-all on one half only; one
half parallel is 0.63–0.97× the original. (2) `s121`: only rep 3 used `memcpy`; reps 1, 2, 5 wrote a
loop copy like the model alone, and lost to the one-at-a-time speed check. (3) The `e1_r_a/b` entry's
"the Phase B marginals were not wrong either" holds for each pragma measured alone and not for the
set — see the §6 row. **What made `default` reach less, measured:** the one-at-a-time speed check
(7 trials), the clause false reject together with DiscoPoP's pattern on one half only (`s281`, 5),
a pragma DiscoPoP cannot write (`s331`, `s341`), and rewrites that are slow in themselves (Settle 15,
Phase B 6). On the agent's own measurement the seven would put it at 51 FASTER of 90 (an estimate —
the combined programs were timed, not verified by the harness). **D33, proposed** (§6): Phase B
measures a rewrite's safe pragmas together before dropping any.

**The same evening — agent v2, and E1 replayed under it (D34; no model).** The author approved
D32 and D33 and the two gate fixes, and a rule for changing the agent between experiments (D34:
each change from a recorded finding, replayed before merging, the version stamped per run, the
sequence told in the thesis — and earlier experiments are not rerun: the changed stage is replayed
on their archived candidates). Built at `ad57f134` as Fixes 91–94. The programs E1 would have ended
with under v2 were rebuilt from the archived patches (`checks/e1b_v2_sources/`) and verified by the
harness like any trial (`e1b_v2_verify`, `verify-source`, E1's settings):

| what v2 changes | trials | harness verdict under v2 | E1 (v1) |
|---|---|---|---|
| D33 — the rewrite with all its safe pragmas | `s1213` r1, r3 · `s121` r1, r2, r5 · `s244` r1 · `s112` r4 | **7 FASTER**, 1.49–3.00× (12 threads) | no-change |
| Fix 91 — both halves of `s281`'s split annotated | `s281` r2–r5 | **4 FASTER**, 2.55–3.25× | no-change |
| control: kept in E1 | `s127` r1 | FASTER 4.48× | FASTER |
| control: a slow rewrite | `s121` r4 | parallel-not-faster 0.14× | no-change |

All outputs identical to the original on both inputs, and all 13 programs clean under the gate's TSan
and schedule matrix (`e1b_v2_race_check`). **E1 under v2: TSVC class R FASTER in 55 of 90 trials** (v1:
44), 0 unsafe; no other trial changes (§6; Fix 92 has no effect on the agent's E1 trials). Race-checked, the model alone is FASTER
in 53 of 88 — **with v2 the pipeline no longer trails the model in reach, and it still ships no wrong
program**. D32 leaves class R as it was and turns class A's `worse` and `lost` into `equal`. These are
rates from a replay; the paired statistics come from E2's own `default` arm on v2.

### `e1_a`, `e1_d` — 2026-09-22, server, **E1 classes A (no-harm) and D (must-decline)** (36 trials, Haiku)

**Setup.** As class R: commit `00d4594f`, `discopop_gate` vs `default`, Haiku 4.5, verification
at the timing sizes on 6 and 12 threads. Class A (`s000`, `s313`, `vpvtv`) ×1 on node 0,
17:47–18:21 UTC; class D (`s3112`, `s321`, `s322`, `s323`) ×3 on node 1, 17:36–22:20 UTC.
Read-out: `results/E01_main_comparison/analysis/` (all four E1 runs; regenerated by the commands in its README).

**Class D — the must-decline control: passed.** 12 agent trials, 12 `neither`, **0 unsafe**.
The model did try: **56 rewrites of true recurrences were rejected at Phase A's correctness
check** (`s322` 24, `s321` 18, `s323` 11, `s3112` 3), and 11 racy pragmas in Phase B (TSan 7,
schedule stress 2, correctness 2) — every one caught before it reached the program. `s3112`
shows the whole chain: a rewrite passed the gate, DiscoPoP then reported three do-alls on it,
TSan and the schedule check rejected two, Settle dropped the third as slower, everything was
reverted. The cost of declining is the budget: 1–9 calls per trial (the function and each loop
get their own), 8–31 minutes, up to 1.57 USD-equivalent — class D is the campaign's most
expensive trial per result.

**Class A — the no-harm control: harm found.** DiscoPoP alone is FASTER on all three.

| loop | DiscoPoP alone (12 threads) | agent | verdict | what happened |
|---|---|---|---|---|
| `s313` (dot product) | 5.55× | 6.36× | **better** 1.15× | the model made `dot` loop-local and kept a final copy; DiscoPoP then found the reduction |
| `vpvtv` (`a[i] += b[i]*c[i]`) | 4.08× | 2.37× | **worse** 0.58× | the model was asked about the OUTER repetition loop (no pattern of its own); it copied `b` and `c` into buffers once and patched them after every `pb_mix`; DiscoPoP's pragma on the rewritten loop measured 2.65× where it measures 4.24× on the original; the finished file beat the ORIGINAL, so Settle kept it |
| `s000` (`a[i] = b[i] + 1`) | 4.03× | 1.00× | **lost** | the model was asked about the FUNCTION (no pattern of its own); `memcpy` of `b` per repetition; the pragma on the rewritten loop measured 1.40×; the finished file was slower than the original, Settle dropped the pragma first and then the orphaned rewrite — DiscoPoP's own pragma went with them |

The mechanism is one: the model is called on a region with no pattern of its own whose hot
loop DiscoPoP already covers; its rewrite costs more than it enables; and **Settle compares the
finished program with the ORIGINAL, never with what DiscoPoP alone would deliver** — so a slower
parallel program survives (`vpvtv`), and a repair that ends below the original falls back to the
original instead of to DiscoPoP's own program (`s000`). n = 3 (class A ×1, as pre-registered):
the rate is not estimable, the mechanism is deterministic.

**A fix that was built and withdrawn before it ran (Fix 90).** The first remedy — do not send a
region to the model when every outermost loop inside it carries an applicable DiscoPoP pattern —
was replayed on E1's own 90 class-R TSVC trials before merging: it would have **blocked the
model on 11 of 18 class-R loops, including all five 5-of-5 winners** (`s127 s254 s291 s292
s293`). In class R DiscoPoP DOES report patterns on those loops — false positives that the gate
rejects (TSan) — so a rule on DiscoPoP's patterns cannot tell class R from class A; only the gate
can. Reverted (the code never reached the campaign branch). What would address the mechanism
without that blindness is a floor: **D32, proposed** — the agent computes DiscoPoP's own gated
program first (what `discopop_gate` does, < 1 min on TSVC) and Settle keeps the agent's program
only if it beats that one, paired; otherwise DiscoPoP's. On class R DiscoPoP's program is the
original in every E1 trial (0 of 90 kept), so the floor changes nothing there; on class A and on
the applications (LULESH is expected to be class A at program level) it makes `lost` and `worse`
impossible up to measurement noise. The author's decision; needed before E6 and E11, not before
E2, E3, E8 (TSVC class R).

**E1 as a whole (290 trials, 145 paired):** class R (TSVC) 46 of 90 verified parallel and 44
FASTER vs 0 of 90; class A 1 better, 1 worse, 1 lost; class D 12 of 12 correctly declined;
**0 unsafe acceptances in 288 trials with a verdict** (2 `invalid`: the `npb/is` timeouts).

### `e1_r_a`, `e1_r_b` — 2026-09-21/22, server, **E1 class R: DiscoPoP alone vs DiscoPoP + agent, five repeats** (260 trials, Haiku)

**Question (H1, H2).** On the benchmarks where DiscoPoP alone reaches no verified parallel
program, does the agent — the same DiscoPoP, the same gate, plus a model that restructures —
deliver correct speedups; and does anything wrong get through?

**Setup.** Commit `00d4594f` (Fixes 86–88, D22/D23/D27/D29 defaults), two NUMA lanes, arms
`discopop_gate` (budget 0) vs `default` (budget 3), Haiku 4.5, 5 repeats, verification at
EXTRALARGE on 6 and 12 threads with 5 repeats, speed check at each kernel's timing size.
Launched 21 Sep 15:10 UTC, lane B finished 22 Sep 04:35, lane A 22 Sep 15:50; host load
2,200–7,600 throughout. Read-out: `results/E01_main_comparison/analysis/` (`plots --runs e1_r_a,e1_r_b,e1_a,e1_d`,
`main_comparison_stats.py --suite tsvc`; the class-R numbers are identical to the class-R-only read-out).

**The registered set (26 benchmarks, 130 paired trials), as it ran:** gained 47,
gained-not-faster 9, neither 72, invalid 2 (the `npb/is` timeouts, below). Agent: verified
parallel in 56 of 128 (44 %, Wilson 95 % CI 35–52 %), FASTER in 47 (37 %); DiscoPoP alone:
0 of 130 (0 %, CI 0–3 %). **Unsafe acceptances: 0 in 258 trials with a verdict.**

**The primary set (TSVC-2 class R, 18 loops, 90 paired trials; D30):**

| | agent (`default`) | DiscoPoP alone (`discopop_gate`) |
|---|---|---|
| verified parallel program | **46 of 90** (51 %, CI 41–61 %) | 0 of 90 (0 %, CI 0–4 %) |
| FASTER (≥ 1.1× over the sequential original) | **44 of 90** (49 %, CI 39–59 %) | 0 of 90 |
| loops gained at least once | **14 of 18** | 0 |
| loops gained 5 of 5 | 5 (`s127`, `s254`, `s291`, `s292`, `s293`) | 0 |
| BROKEN | 0 | 0 |
| speed, paired by loop, median of per-loop medians | **1.08×** the DiscoPoP-alone program (bootstrap CI 1.00–2.35×); Wilcoxon one-sided W = 45, **p = 0.002**, 9 non-zero pairs, all positive; Cliff's δ = +0.50 | — |

The per-loop median is a conservative statistic: a loop gained in 2 of 5 trials has a median
of 1.00×. Read per loop:

| loop (TSVC category) | agent FASTER | speedup at 6 / 12 threads (median of the FASTER trials) | what the model did |
|---|---|---|---|
| `s127` induction variable, multiple increments | 5 / 5 | 3.81 / 4.26 | closed-form index |
| `s254` carry-around variable | 5 / 5 | 3.31 / 3.80 | `b[i-1]` read instead of the carried scalar |
| `s291` loop peeling, wrap-around 1 level | 5 / 5 | 3.23 / 3.76 | `(i == 0) ? LEN-1 : i-1` |
| `s292` wrap-around 2 levels | 5 / 5 | 1.34 / 2.34 | same, two levels |
| `s293` `a[i] = a[0]` cycle | 5 / 5 | 2.80 / 3.19 | hoisted `a[0]` |
| `s255` carry-around, 2 levels | 4 / 5 | 1.33 / 2.29 | index arithmetic |
| `s252`, `s212`, `s243` | 3 / 5 each | 3.48 / 4.15 · 1.35 / 1.39 · 1.23 / 1.24 | scalar expansion into a buffer; copy + node splitting |
| `s1213` | 2 / 5 | 2.80 / 2.65 | copies of `a` and `b` |
| `s112`, `s211`, `s241`, `s244` | 1 / 5 each | 1.49 / 1.76 · 1.10 / 1.07 · 2.08 / 2.23 · 3.42 / 4.39 | one good rewrite in five; see the finding below |
| `s121`, `s281` | 0 / 5 | — | correct rewrites whose pragmas cost more than they save (below) |
| `s331`, `s341` | 0 / 5 | — | as T0.13 predicted: DiscoPoP cannot write the pragma the loop needs — but ONE trial of each found a way round it and was then dropped on speed (below) |

**H1 is supported** on the primary set (and on the registered set): the agent delivers verified
speedups where DiscoPoP alone delivers none, with p = 0.002 on per-loop medians and an effect
size of +0.50. **H2 holds so far:** 0 BROKEN in 258 trials, 269 model calls. **H4 (scaling):**
of the 44 FASTER TSVC trials, 29 are faster at 12 threads than at 6 (> 1.1×), 13 flat, 2
lower; medians 2.52× at 6 and 3.12× at 12 threads. The expert references (T0.10) reach ≥ 1.45×
at the gate's timing size; the agent's 5-of-5 loops reach 2.3–4.3× at 12 threads at the
verification size.

**Cost.** Median 1 model call per trial — for the FASTER trials AND for the `no-change` ones
(the budget of 3 is rarely spent: a rewrite that passes the gate but earns no pragma ends the
trial at Settle, it does not retry); median 127 s of model time and 0.12 USD-equivalent per
trial, 13.95 for the 90 TSVC agent trials. Profile refreshes after a kept rewrite: 102, all
full (D27), 0 fallbacks (D29); runtimes re-measured 102 times (Fix 86/87). The explorer stall
limit fired 26 times inside agents and 20 times in the harness's profile step — no benchmark
was lost to a stall (D-limit of 21 Sep).

**Deviations, recorded first.**

1. **Two `npb/is default` trials hit the 90-minute limit** (`AGENT_TIMEOUT`, counted `invalid`,
   the other three took 18, 20 and 84 min). Both were inside Phase B. Rep 3's log says where
   the time went: after the third kept rewrite — of a region with score 0.1 — DiscoPoP's
   re-measurement reports the program's regions at **97 s** where they had been 3.3 s; every
   later step (noise calibration, the paired timing of each pragma at the timing size, TSan)
   runs that program many times. **Phase A's gate does not bound a rewrite's cost**: a
   pragma-free rewrite is judged on output alone, because a copy that only pays off with the
   pragmas is the normal case; an unbounded one eats the trial. D31 — a bound on the
   rewrite's SEQUENTIAL cost in Phase A's gate — was proposed for this and **withdrawn the same
   day on a measurement** (`results/E01_main_comparison/checks/seq_cost_expert_mac`): the expert restructurings
   themselves, pragmas stripped, run 1.00–2.30× SLOWER than the original sequentially (`s121`
   2.30×, `s112` 2.06×, `s211` 1.65×, `s241` 1.64×) and ≥ 1.45× faster with their pragmas.
   A bound that catches the failed rewrites (1.2–3× sequentially) rejects the good ones; the
   sequential cost does not predict whether a rewrite pays, only the paired check with the
   pragmas does — which is Settle. What would recover the trial is a RETRY after Settle's
   verdict with that verdict as feedback (the median trial used 1 of 3 calls): proposed as
   D31-b, a flow change (Phase B and Settle inside the attempt loop), not built.
2. **15 of the 90 TSVC agent trials ended at Settle**, which dropped a program Phase B had
   just measured at 1.02–1.84× per pragma and reported the finished file 1.1–8× slower than
   the original. Settle's method was UNPAIRED — the finished program (best of 5, `-fopenmp`)
   against the reference time captured at the start of the run (best of 3, no `-fopenmp`) —
   so the suspicion was interference on the shared host. It was checked, not assumed: each of
   the 15 programs was rebuilt from its archived patches and judged by the harness on the
   server (`settle_check`, EXTRALARGE, 6 / 12 threads, 5 repeats). Ten of the fifteen were
   rebuilt (`results/E01_main_comparison/checks/settle_check`); all ten are CORRECT (dump byte-identical on both inputs) and
   all ten are SLOWER than the original — Settle was right every time it was checked:

   | trial | Phase B marginals | Settle said | harness, 6 / 12 threads | the rewrite's cost |
   |---|---|---|---|---|
   | `s112` rep 3 | 1.05× | 3888 vs 483 ms | 0.14× / 0.14× | `malloc` + `memcpy` of `a` per repetition |
   | `s121` rep 3 | 1.61× | 740 vs 511 ms | 0.73× / 0.79× | `memcpy` of `a` per repetition |
   | `s1213` rep 4 | 1.84×, 1.41× | 3097 vs 1024 ms | 0.31× / 0.35× | `malloc` of two arrays + copy loops per repetition |
   | `s211` rep 3 | 1.02×, 1.28× | 4054 vs 1398 ms | 0.35× / 0.35× | `malloc` + `memcpy` of `b` per repetition |
   | `s212` rep 5 | 1.49× | 3005 vs 1082 ms | 0.37× / 0.35× | `malloc` + copy loop per repetition |
   | `s241` rep 2 | 1.08×, 1.21× | 4061 vs 1115 ms | 0.30× / 0.29× | `malloc` + `memcpy` of `a` per repetition |
   | `s241` rep 4 | 1.28×, 1.70× | 1204 vs 1112 ms | 0.88× / 0.90× | one `malloc`, `memcpy` per repetition |
   | `s252` rep 5 | 1.43× | 757 vs 730 ms | 0.94× / 0.99× | product buffer, then a sequential recurrence over it |
   | `s331` rep 1 | 1.42× | 455 vs 370 ms | 0.86× / 0.94× | candidate array, then a sequential max scan |
   | `s341` rep 5 | 1.05× | 2474 vs 411 ms | 0.20× / 0.19× | sequential prefix count, then a parallel scatter |

   The five not rebuilt (`s112` reps 1 and 5, `s211` reps 1 and 4, `s241` rep 3) have the same
   shape — a copy per repetition — and the same Settle diagnostic. The Phase B marginals were
   not wrong either: each measures a pragma against the state BEFORE it, i.e. against the
   already-slow rewrite; only Settle compares with the original. The suspicion of interference
   was mine and it was wrong; the method is still changed, because a comparison across minutes
   on a host at load 2,000–7,600 cannot be defended even when it happens to be right.
   **Fix 89** (work branch, E2 onwards): Settle's speed verdict is now the same interleaved
   original-vs-final measurement and threshold Phase B uses; feature check `settle-paired`.
   Recorded as a change of METHOD, not of verdicts: E1's classes A and D run on `00d4594f`
   like class R.

**Finding — the rewrites that fail are the ones that copy.** Every Settle-dropped program and
every `s121`/`s281` trial has the same shape: a full-array `memcpy` (sequential, memory-bound)
or a `malloc`/`free` of the whole array **inside the repetition loop**. The copy costs as much
as the pragma saves; a `malloc` per repetition adds page faults on 256 MB and makes the
program 3× slower than the original before any pragma. The expert references make the same
copy ONCE, outside the repetitions, or as a parallel loop. The 5-of-5 loops are the ones whose
rewrite needs no buffer (an index expression, a hoisted read). This is the model's
rewrite quality, and the gate's job was to catch it — which it did, at the cost of the trial:
material for E2 (does evidence change the rewrite?) and for the prompt (the contract already
says "heap for size-dependent buffers"; it does not say "allocate once"). `s331` rep 1 and
`s341` rep 5 show the flip side: Haiku found a restructuring DiscoPoP CAN annotate (a candidate
array + sequential max; a prefix count + scatter) with marginals of 1.42× and 1.05× — the
loops T0.13 called unwinnable are winnable — and lost them at Settle.

**The non-TSVC benchmarks, as registered:** `floyd-warshall` 3 of 5 gained (5.1–10.3×, the
conditional-write rewrite + DiscoPoP's i-loop pragma); `trisolv` 5 of 5 correct parallel
programs on an untimeable kernel (`gained-not-faster`); `bicg` and `doitgen` 1 of 5 each;
`md`, `is`, `hotspot`, `seidel-2d` 0 of 5 (with `is` 3 of 3 valid). DiscoPoP alone 0 of 40.

**Exhibits:** `s291_peeled_5of5_faster`, `s127_induction_5of5_faster`,
`s254_carry_around_5of5_faster`, `s241_copy_per_repetition_settle_dropped` (rep 2: the
`malloc` + `memcpy` per repetition, 0.30× on the server), `s121_memcpy_pragmas_slower`,
`floyd_e1_conditional_write_gained`.

**Still owed for E1:** classes A (`s000`, `s313`, `vpvtv` ×1) and D (`s3112`, `s321`,
`s322`, `s323` ×3) — class D launched 22 Sep 17:36 UTC on node 1 (`e1_d`), class A follows on
node 0; the bare-LLM arm (E1-bare) on TSVC class R — the author's go on 22 Sep, launched after class D and the merge of the work branch (the runner lives there).

### `lulesh_ref_check`, `ref_check_mac`, `e11_npbc_probe_mac` — 2026-09-21, Mac, **the expert references through the harness** (no model)

**Question.** Do the expert versions the campaign measures itself against pass the harness's
own verification — LLNL's OpenMP LULESH, and hand-written references for the two dropped
benchmarks whose exclusion had not been verified (§5r)?

**How.** `agent/benchmark verify-source <bench> --source <reference> --threads 2,4 --repeats 3`;
LULESH at SMALL and STANDARD, the two kernels at their T0.1 verification size (LARGE).

| Reference | Verdict | Output | Speed (2 / 4 threads) |
|---|---|---|---|
| LLNL LULESH 2.0 OpenMP, SMALL | `parallel-not-faster` | dump 5.6e-15, seeded 4.2e-15, digest 1.8e-16 | 0.63× / 0.55× (8³ elements, 20 iterations) |
| LLNL LULESH 2.0 OpenMP, STANDARD | `FASTER` | the same | 1.31× / 1.70× |
| `hotspot`, chunk loop split | `FASTER` | byte-identical, shipped and seeded; digest error 0 | 1.44× / 1.52× |
| `floyd-warshall`, textbook form | `FASTER` | byte-identical, shipped and seeded; digest error 0 | 2.46× / 3.61× |

The FIRST LULESH run said `BROKEN` with a dump error of 0.25: a defect of the package, not of
LLNL's code (§6, same date) — corrected before the table above was taken. All four are Mac
numbers at no more than four threads: the speeds are indicative, and the correctness verdicts
must be repeated on the server at 6 / 12 / 24 threads before they are cited (`hotspot` is the
proof that four threads cannot see a schedule-dependent result).

**NPB-C probe (partial).** EP: instrument 1.9 s, run 10.0 s, explore 19.5 s, 6 do-all + 2
reduction patterns; IS: 1.8 / 0.7 / 18.8 s, 10 do-all; CG: 17.1 / 9.3 / 79.8 s, 24 + 9; NPB's
verification SUCCESSFUL in all three. FT had not finished instrumenting after 30 minutes when
the probe was stopped (the Mac was swapping, §6); FT, MG, BT, SP, LU are owed on the server.

### `t0_13_default_arm_ceiling` — 2026-09-21, Mac, **T0.13: what the pipeline does with a PERFECT rewrite** (no model)

- **Why.** The author's concern once E1 was running: *"all code changes will be rejected."* Four
  smokes had ended `no-change`, and E1's first agent trial (`hotspot`) rejected all seven
  pragmas. The question can be asked with known ground truth and no model: take every TSVC
  EXPERT restructuring (verified correct and faster, T0.10), strip its pragmas — exactly what a
  perfect model hands over under `--no-llm-pragmas` — and run the agent on it with `--budget 0`
  and the campaign's flags: DiscoPoP re-profiles it, Phase B pushes DiscoPoP's pragmas through
  the gate, Settle verifies. Speed check OFF here (`--no-speed`): a laptop is no place to judge
  speed, which T0.10 measured on the server (every class-R reference ≥ 1.45× at the gate's own
  timing size); the question is whether CORRECT code is rejected. (A first pass with the speed
  check on was discarded: 48-thread `hotspot` checks ran beside it and spoiled its timings.)
- **Result: KEPT on 18 of 21 loops; class R: 16 of 18.** In every kept loop the only rejection
  is ONE TSan hit on the outer repetition loop (`nl`, which rewrites the same arrays every
  pass) — a true race on a loop DiscoPoP should not have offered; the kernel loops themselves
  were applied and the finished files verified.
- **The three not kept, each inspected — none is a false rejection by the gate:**
  - `s331` (R): the expert's solution is `reduction(max:j)`; DiscoPoP can only offer a plain
    `parallel for`, which IS a race — caught by the schedule matrix ("two runs at the SAME thread
    count printed different output").
  - `s341` (R): the expert's solution is a hand-written `#pragma omp parallel` region with
    `omp_get_thread_num()` (count → prefix sum → pack); without its pragmas no loop in it is a
    `parallel for`, so DiscoPoP has nothing to annotate (and the file cannot be instrumented
    without OpenMP's header).
  - `s313` (A, not part of the claim): on the reference's one-line loop DiscoPoP reports
    `do_all` instead of the reduction it finds in the package, so its pragma lacks
    `reduction(+:dot)` — a real race, rightly rejected.
- **What it means for E1.** Code changes are NOT bound to be rejected: given a good rewrite the
  `default` arm keeps it on 16 of the 18 TSVC class-R loops, so a `neither` there is about the
  model's rewrite. On `s331` and `s341` the KNOWN solution lies outside what DiscoPoP can write
  (a max-reduction, an explicit SPMD region): under `default` they can only be won by a
  different, block-wise restructuring, and they are exactly where E3's variable — who writes the
  pragma — should show. Stated with E1's result, not discovered after it.
- Files: `results/T0_instruments/T0.13_default_arm_ceiling/analysis/` (`ceiling_safety_mac.csv`, the run log,
  three agent logs). Tool: `agent/tools/default_arm_ceiling.py`.

### `e1_smoke5` — 2026-09-21, server, **the pre-flight smoke that finally passes: one benchmark of every kind E1 contains** (8 trials, Haiku)

- **Setup.** `tsvc/s211` (class R), `polybench/bicg` (class R, NO timing size — the harness
  switches the agent's speed check off), `polybench/2mm` (class A), `tsvc/s321` (class D) ×
  `discopop_gate`, `default` × 1; threads 6/12, 5 repeats; commit `721369dd`; host load
  5,000–7,000 from other users. Arm check: the arms differ in `--budget` only, verified with
  the untimeable kernel in the list (which would have refused the run the day before).
- **Main comparison (D19):**

  | benchmark | class | DiscoPoP alone | agent | agent / DiscoPoP alone | verdict |
  |---|---|---|---|---:|---|
  | `polybench/2mm` | A | FASTER 9.49× | FASTER 10.62× | 1.12× | **better** |
  | `polybench/bicg` | R | no-change | no-change | 1.00× | neither |
  | `tsvc/s211` | R | no-change | parallel-not-faster 1.06× | 1.06× | **gained-not-faster** |
  | `tsvc/s321` | D | no-change | no-change (9 calls) | 1.00× | neither — no unsafe acceptance |

- **`s211`: the restructuring path works end to end for the first time under the campaign's
  defaults.** `[refresh] kind=full` → `Re-measured runtimes: 17 region(s), 4.9 ms` (no longer
  halved, Fix 87) → `4 new at depth 1` → `DiscoPoP now finds: do_all @ 137–139, do_all @
  140–142` → Phase B with TWO candidates: the racy half **dropped by TSan** (a genuine DiscoPoP
  false positive), the parallel half `marginal 1.17×` → **APPLIED** → Settle verifies the
  finished file. Both loops now show `W=3,071,808`; the second read `320` before Fix 88.
  Verified independently at 1.06× / 1.04× (6 / 12 threads): only half of the kernel is parallel
  and the model split the loop without the temporary the expert reference uses (2.73× with all
  three loops parallel), so the honest verdict is *gained, not faster*. The agent keeps a
  Phase B pragma that is not slower (marginal ≥ the measured noise floor) and whose finished
  program is not slower than the original; 1.1× is what the HARNESS asks before it calls a
  result FASTER. Both are reported.
- **`bicg`**: speed check correctly OFF (no size of this kernel can be timed). The rewrite
  passed the gate; all three DiscoPoP pragmas on it were racy and were rejected — one by TSan,
  two by the schedule matrix ("two runs at the SAME thread count printed different output").
- **`2mm`**: the model FUSED the two outer loops (row *i* of `D` needs only row *i* of `tmp`),
  DiscoPoP annotated the one fused loop: one parallel region instead of two.
- **`s321`**: nine attempts, every wrong rewrite rejected at `correctness`.
- **New per-trial records, all populated:** `refresh_full` 1 / `refresh_fast` 0 /
  `refresh_fallback` 0, `runtime_remeasurements` 1, `explorer_stalls` 0. **Found by reading
  them:** `speed_check_off` was promised per trial and written to the run manifest only —
  `None` on every trial; now on each trial and in `trials.csv`, with the timing flags used.
- **`floyd-warshall`, the open question from smoke 3/4, settled by measurement:** on the
  ORIGINAL all three DiscoPoP pragmas fail TSan (iteration *k* writes row *k*, with the value
  it already holds, while the others read it — benign, and formally a race). The model's
  race-free rewrites differ in cost: the full N×N copy of smoke 3/4 verifies at **0.69×**
  (STANDARD) and **0.76×** (LARGE) with DiscoPoP's pragma, 6/12/24 threads, measured apart from
  the agent — the gate's 0.28–0.37× rejection was RIGHT; E10's accepted version copies only
  row *k* (O(N) per step) and verified at 5.8–9.6×. So floyd can be won under `default`, and
  whether it is depends on the model's draw — which is what five repeats are for.
- **Exhibits:** `s211_distributed_dp_annotates_exposed_loop`, `2mm_default_vs_dp_alone`,
  `s321_recurrence_declined_9_attempts`.

### `e1_smoke3`, `e1_smoke4` — 2026-09-21, server, **the smoke followed to the end: two defects between a correct rewrite and Phase B** (Fixes 86, 87)

- **Setup.** `polybench/floyd-warshall` and `tsvc/s211`, arm `default`, Haiku, × 1, threads 6/12,
  5 repeats, host load 2,500–3,900. `e1_smoke3` on `5b38cf9b`; `e1_smoke4` on `edf6607a` (Fix 86)
  with `discopop_gate` paired in (D19). Arm check of smoke 4: the arms differ in `--budget` only.
- **Both runs, both benchmarks: `no-change`** — yet in all four agent trials the model's rewrite
  was CORRECT and passed the gate. The prompt fix of the same morning held: floyd's accepted
  rewrite allocates its buffer with `malloc`/`free`, no stack array.
- **`s211`, the decisive case.** The model distributes the loop (`b[i] = b[i+1] - e[i]*d[i]` /
  `a[i] = b[i-1] + c[i]*d[i]`) without the copy of `b` the expert reference uses. Loop 1 therefore
  keeps a real anti-dependence; DiscoPoP nevertheless reports `do_all` on it, and **TSan catches
  the race** — the gate rejecting a genuine DiscoPoP false positive. Loop 2 IS parallel, DiscoPoP
  reports `do_all` on it too (profile of the rewritten source: regions `1:84` and `1:90`, patterns
  at lines 137 and 140) — and it never reached Phase B, in either run.
- **Why, layer 1 (Fix 86).** Runtimes were re-measured after a kept rewrite only when a deeper
  restructuring level was coming; at the default depth 0 never. The created region arrived
  unmeasured and `--min-runtime-share 0.01` dropped it. Reproduced with the planner alone: 4
  candidates at share 0, 3 at 0.01.
- **Why, layer 2 (Fix 87) — found because smoke 4 changed nothing.** With Fix 86 the log says
  `Re-measured runtimes: 16 region(s), 2.8 ms total` and Phase B still gets one candidate. The
  agent's own sequence was replayed without a model (`_reprofil` → `_measure_hotspots(force)` →
  `adopt` → `remap_lines` → planner): the "fresh" model has **no line 140 and `main` at line
  147 — where `main` sits in the ORIGINAL file** (149 after the rewrite). DiscoPoP's hotspot
  detection accumulates by design: each instrumented build APPENDS its region ids to
  `hotspot_detection/private/cs_id.txt` (`temp.txt`: `19`, then `39`), each run adds a
  `hotspot_result_<n>.txt`, and the analyzer averages over the runs. The forced re-measurement
  deleted only `Hotspots.json`, so the analyzer reported the old program's region table — old
  lines, every time HALVED by averaging with a run that never executed those ids (the 2.8 ms
  against 4.8 ms at start-up), nothing for a created region. And because the caller believes a
  fresh measurement is already in the new file's coordinates, it skips the line remap — so every
  region BELOW a rewrite was mis-keyed too. That last part was latent on the deeper-level path
  since it was written, and Fix 86 alone would have spread it to every kept rewrite.
- **After Fix 87** (the directory is cleared before re-instrumenting) the same replay gives a
  model with line 140 and `main` at 149, and **4 candidates including `1:90@140–142`**.
- **`floyd-warshall`.** Phase B candidates 3 → 4 with Fix 86, verdicts unchanged and honest: the
  `k` loop races (TSan), the inner loops measure 0.28–0.37× and 0.01× at this size. The paired
  `discopop_gate` trial ALSO ends `no-change` — DiscoPoP's own three pragmas fail the same gate —
  so the verdict is **neither**, not `lost`; the agent log's `DiscoPoP unaided: 3 usable
  pragma(s) → this run: 0 [BELOW]` counts pragmas DiscoPoP PRODUCES, not ones that survive.
- **Main comparison of smoke 4:** 2 × `neither`, agent / DiscoPoP alone 1.00× (n = 2).
- **Cost of the re-measurement** (floyd, smoke 3 → 4): 388 s → 491 s with one extra model call
  and three re-measurements in the difference; not separable at n = 1.
- **Also seen, not yet followed:** in `loop_counter_output.txt` the counts look SHIFTED by one
  loop against `loop_meta.txt` (rewritten `s211`, same on Mac and server: line 109 → 48, 136 →
  1,535,904, 137 → 1,535,904, 140 → 160, where the true values are 32,000 · 48 · 1,535,904 ·
  1,535,904). Irrelevant where ranking is measured; it feeds the workload proxy, i.e. E9's
  `full_no_hotspots`. To be traced to DiscoPoP or to our reader before E9.
- **The explorer's random stall (L5) reproduced on the Mac** on the rewritten `s211`: first draw
  > 6 min at 100 % CPU, second draw seconds.

### `e1_smoke` — 2026-09-21, server, **E1's pre-flight smoke** (2 class-R benchmarks × 2 arms × 1)

- **Why.** The last step of the pre-flight (§5k): one trial per arm with the logs READ, to confirm
  each arm's code path actually executes before E1 spends model calls.
- **Result at first glance: all four trials `no-change`** — including the agent arm on
  `floyd-warshall`, the one benchmark we know it can restructure. Read properly, the opposite of
  a failure.
- **What the log shows.** Phase A worked exactly as designed: DiscoPoP's two loops were deferred
  to Phase B, the FUNCTION went to the model, the model rewrote it, the gate passed, and
  DiscoPoP then found **three new Do-Alls in the rewritten code**. Then Phase B measured the
  pragmas at the kernel's timing size and the program **crashed (SIGSEGV)**, so both pragmas were
  dropped and Settle discarded the rewrite as an orphan — "exposed 3 region(s), none kept a
  pragma".
- **Why it crashed, and why that is the right answer.** The model wrote
  `DATA_TYPE path_new[_PB_N][_PB_N]` — an N × N array **on the stack**. At the agent size
  (N = 128) that is 131 KB and passes every check; at the timing size (N = 1024) it is **exactly
  8 MB**, the default stack limit, and the program dies. At the verification size (N = 2000) it
  would be 30 MB. This is the SAME bug the model shipped in E10, where `full` — with the speed
  check off — accepted it and the harness caught it only at verification, scoring it `BROKEN`.
  **Here the agent caught its own bug and withdrew.** It is direct evidence for D22: the speed
  check at the kernel's measured size is not only about speed, it reaches sizes the correctness
  gate never tries.
- **Two things fixed as a result.** (i) Phase B now says *"the program CRASHED at the timing size
  — the correctness gate runs at the agent size and never reached it"* and drops the candidate as
  **unsafe at size**, instead of the misleading "measurement failed", which reads like a timing
  problem. (ii) Recorded here, because `no-change` on its own cannot distinguish "the agent found
  nothing" from "the agent found a restructuring, tested it, and correctly rejected its own work"
  — and for the thesis those are different stories.
- **"Does every restructuring get reverted, then?"** (the author, on seeing the smoke). No —
  checked over the whole archive rather than argued: **14 of 19 restructurings survived**
  (3 were `SCAFFOLD_MODIFIED`, a different fault: the model edited the harness; 2 were `BROKEN`).
  The stack overflow is one case, and the archive shows the line precisely: two OTHER
  `floyd-warshall` rewrites declared stack arrays too — `pathk[_PB_N]` and `row_k[_PB_N]` — and
  both are FASTER, because a ONE-dimensional array of N doubles is 16 KB at N = 2000 while the
  two-dimensional one is 31 MB. The model is not generally allocating badly; it made one
  dimensional mistake.
- **What we changed, and why it is legitimate.** The prompt never told the model the target's
  memory limits — it promised "extra buffers" were allowed and said nothing about where they
  live. The contract now states the constraint: anything whose size grows with the problem must
  be heap-allocated, the stack is 8 MB, the program is verified at sizes far larger than the one
  shown, and `T buf[N][N]` is 131 KB at N = 128 and 8 MB at N = 1024. That is a fact about the
  PLATFORM, like the thread count or the compiler — not a hint about the answer. Withholding it
  would have measured the model's recall of C memory limits instead of its ability to restructure
  for parallelism, which is not the research question. Pre-registered here, before E1.
- **Verdict: the pre-flight passes.** Both arms' code paths ran: the baseline made 0 model calls
  and applied DiscoPoP's patterns; the agent arm made a call, restructured, re-profiled, exposed
  new patterns and exercised Phase B, Settle and the revert path. E1 can run.


### `t0_11_classes_a/b/c` — 2026-09-20/21, server, **T0.11: the class of every benchmark** (no model)

- **Why.** E1's arms can only differ on benchmarks where DiscoPoP alone fails; §5k showed the old
  core set could not test C1 at all. This measures, rather than assumes, what DiscoPoP plus the
  gate does on every benchmark — and it doubles as the DiscoPoP-alone half of the main comparison
  (D19), so E1 only has to run the agent side.
- **Setup.** Arm `discopop_capability` (`--budget 0 --no-require-speedup`: the class question is
  about CAPABILITY, and with the speed check on a kernel whose DiscoPoP pragma is correct but slow
  — `lu`, 0.21× — would end `no-change` and be filed as needing restructuring, which is wrong: it
  needs a better pragma). **Three separate runs, not three repeats**: a run profiles each benchmark
  once and DiscoPoP's answer follows the draw. 166 trials, threads 6/12, repeats 5, 14:00–03:22.
- **Result: R 26 · A 26 · D 4**, no benchmark undetermined.

  | suite | R | A | D |
  |---|---:|---:|---:|
  | TSVC | 18 | 3 | 4 |
  | PolyBench | 5 | 22 | — |
  | applications (`md`, NPB `is`, `hotspot`, `pathfinder`) | 3 | 1 | — |

- **The restructuring suite validates: 25 of 25 TSVC loops come out in the class they were
  DESIGNED for.** Each package declares its intended `restructuring_class` and `class_table.py`
  flags any disagreement; it printed none. The 18 restructuring loops defeat DiscoPoP on every
  usable draw, the 3 controls are parallel on every draw, the 4 recurrences are declined.
- **Three APPLICATIONS are class R** — `burkardt/md`, NPB `is`, Rodinia `hotspot` — so C1 can be
  tested at application scale and not only on single loops. That was not guaranteed.
- **A category the plan had not named: DiscoPoP succeeds AND harms.** Five class-A benchmarks are
  ones DiscoPoP alone leaves SLOWER than sequential — `ludcmp` 0.15×, `lu` 0.21×, `reg_detect`
  0.25×, `atax` 0.30×, `dynprog` 0.98×. They are not "needs restructuring" (a profile exists and a
  verified parallel program is produced) and they are not a clean control either. They are where
  the speed check should pay, and they are reported as their own row in E1.
- **Profile errors: 12 of 166 draws (7 %), every one in TSVC (12 of 75, 16 %), none elsewhere** —
  all the random explorer stall (L5), bounded at 20 min by the phase timeout, falling on different
  loops in different draws. Excluded from the majority, never read as "DiscoPoP found nothing".
- **Pre-flight status:** T0.1 (sizes), T0.10 (expert ceiling at the final sizes), T0.4 (timing
  noise at campaign load) and T0.11 (classes) are done. What remains before E1 is one smoke trial
  per arm with the logs read.
- Archives `results/t0_11_classes_{a,b,c}/`, table `results/T0_instruments/T0.11_measured_classes/analysis/`.


### `t0_4_timing_v2` — 2026-09-20, server, **T0.4 repeated under the load the campaign actually runs at**

- **Why repeat it.** The September pass was taken at a host load of 15–430 and stopped before it
  finished (Polly's parallel build of `hotspot` runs minutes per execution). The campaign runs at
  a load of 1,300–6,800, and since D22 the speed check is ON by default — so the number that
  justifies the 1.1× threshold was measured on a far quieter machine than the one that uses it.
- **Setup.** `timing_noise.py --serial-only --repeats 10 --first-node 1 --lanes 2`, four
  benchmarks spanning the suites (`2mm`, `hotspot`, `jacobi-2d`, `tsvc/s211`), three conditions
  (alone / unpinned / two lanes), 160 timed runs. Host load **min 1,307, median 5,701, max 6,758**.
  Two tool fixes were needed first: `--serial-only` (the switch the first pass lacked) and
  `--first-node`, because running the tool under `numactl --cpunodebind` makes its own per-lane
  pinning fail and the `alone` condition silently collects **zero** samples — which is how the
  first attempt of this repeat was lost.
- **Result.** Per-run variation differs by an order of magnitude between benchmarks:

  | benchmark | CV (alone) | resolvable, ONE run | resolvable, MEDIAN OF 5 |
  |---|---:|---:|---:|
  | `tsvc/s211` | 0.7 % | 1.015× | **1.007×** |
  | `jacobi-2d` | 1.3 % | 1.026× | **1.012×** |
  | `2mm` | 3.3 % | 1.065× | **1.029×** |
  | `hotspot` | 5.2 % | 1.104× | **1.046×** |

- **Reading, and the correction that matters.** On single runs, three cells exceed the 1.1×
  threshold — `2mm` in two lanes reaches **1.131×** and `hotspot` **1.104–1.113×**. Read naively
  that would say our threshold is inside the noise. It is not, because **the harness never
  compares single runs**: `verify()` takes the median of 5 on each side, and the standard error of
  a median falls with √n, so the resolvable ratio is 1 + 2·CV/√5. The worst case anywhere is then
  **1.058×** (`2mm`, two lanes), and `hotspot`'s is 1.046×. **The 1.1× threshold holds on every
  benchmark, with margin, at a load of 5,700** — but it holds *because of* the repeats, which is
  the sentence the thesis must write rather than quoting a raw CV.
- **Two secondary findings.** Running two lanes raises `2mm`'s variation from 3.3 % to 6.5 % while
  leaving `s211` and `jacobi-2d` untouched, so headline speed numbers stay one job per node and
  correctness-only work may share. And variation is a property of the BENCHMARK, not of the
  machine's load: `s211` stays at 0.7 % under load 6,758 while `hotspot` sits at 5.2 % — so a
  per-benchmark noise floor, which the gate already measures, is the right design.
- Supersedes the partial September pass; archive `results/T0_instruments/T0.04_timing_noise/runs/t0_4_timing_v2/`.


### `e10_dp_alone`, `e10_lu_fix84` — 2026-09-20, server, **E10 completed by the main comparison (D19)**

- **Why.** E10 measured the agent's three arms against the SEQUENTIAL original. The author's rule
  (D19) makes DiscoPoP alone the comparison, and E10 had no such arm; `lu` additionally ran with
  the misplaced Phase-B pragma (Fix 84).
- **Setup.** `e10_dp_alone`: `discopop_gate`, no model, the five other E10 kernels × 3, node 1.
  `e10_lu_fix84`: `lu` × all four arms × 3, Haiku, node 0, agent `58d959f2` (with Fix 84). Same
  sizes, threads (6/12) and repeats as E10. Host load 197–5,279 (median ≈ 1,400).
- **The main comparison**, 21 agent trials per arm against DiscoPoP alone on the same benchmark
  (`analysis/e10_e10_dp_alone_e10_lu_fix84/vs_discopop_alone.md`, `fig_vs_discopop_alone`):

  | arm | gained | better | equal | worse | **lost** | neither | unsafe | median agent ÷ DiscoPoP alone |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|
  | `full` | 1 | 4 | 5 | 5 | **0** | 4 | **1** | 0.99× |
  | `speed_gate_large` | 2 | 6 | 2 | 4 | **0** | 7 | 0 | 1.00× |
  | `speed_gate_small` | 0 | 0 | 0 | 2 | **10** | 9 | 0 | 1.00× |

  Per benchmark (12 threads, median over repeats): `lu` DiscoPoP alone **0.21×** vs agent 2.6–2.8×
  → **better ×10**; `floyd-warshall` DiscoPoP alone `no-change` vs agent 1.9–2.8× → **gained ×3**
  (the only restructuring in the set); `2mm` 10.3× vs 10.2× → equal; `jacobi-2d` DiscoPoP alone
  **5.9×** vs agent **2.5×** → **worse ×6**; `seidel-2d` neither (both decline, correct);
  `hotspot` DiscoPoP alone `no-change`, `full` leaves a correct program at **0.09×** → worse.

- **What the new baseline changes.**
  1. **D8 is confirmed, and for a stronger reason.** `speed_gate_large` is the only arm with no
     unsafe acceptance AND no `lost`, the most `better`/`gained`, and the best worst case.
  2. **`speed_gate_small` is not merely wasteful, it is destructive: 10 of 21 trials `lost`** —
     DiscoPoP alone reaches a verified parallel program and the agent's arm does not. Cause read
     from the logs: Phase B applies the speed check to **DiscoPoP's own pragmas** at a size where
     the kernel runs in milliseconds, measures `marginal 0.00× — costs more than it saves`, and
     drops them (`lu`, all three repeats). A speed check at the wrong size does not only block the
     model; it deletes the analysis tool's correct suggestions. This is a thesis result in its own
     right (H10b, sharpened).
  3. **The agent is NOT better than DiscoPoP alone on this set** (median 1.00×) — as it should be:
     five of the six kernels are class A. Here the agent must do no harm, and `speed_gate_large`
     nearly manages that (0 lost, 0 unsafe); the exception is `jacobi-2d`, below. C1 is carried by
     class R, which this set contains only once (`floyd-warshall`, where the agent gains).
  4. **DiscoPoP alone varies by profile draw.** On `lu` the server draw gives an innermost-loop
     Do-All and **0.21×** (all three repeats, one profile); the Mac draw of the same kernel gave
     3.4×. Repeats within a run share one profile, so they are not independent draws: T0.11 must
     profile separately per repeat.
  5. **Classification fixed** (`figures.py`): a correct parallel program that runs ≥ 1.1× SLOWER
     than what DiscoPoP alone leaves is counted `worse`, even where DiscoPoP alone changed
     nothing — `hotspot` at 0.09× was being reported as `gained-not-faster`.

- **The `jacobi-2d` regression → Fix 85 (agreed with the author, to build before E1).** DiscoPoP
  claims the two inner stencil loops; the agent defers them to Phase B, correctly. But the
  *enclosing function* is also a candidate, has no pattern of its own, and goes to the model —
  which, with `--llm-pragmas`, writes `collapse(2)` on those same loops from inside the rewrite.
  Phase B then finds "no applicable pattern" (the loops are annotated) and DiscoPoP's own
  `parallel for private(j)`, twice as fast here, is never measured. Fix: (a) the prompt names the
  loops inside the region that DiscoPoP has already claimed and reserves their pragmas for Phase B;
  (b) where a model pragma sits on a claimed loop anyway, Phase B measures DiscoPoP's version
  against it and keeps the faster. Feature check required.
- **Archives.** `results/E10_speed_check/runs/e10_dp_alone/` (15 trials), `results/E10_speed_check/runs/e10_lu_fix84/` (12 trials).


### `e10` — 2026-09-19/20, server, **E10: the speed check** (full · speed_gate_large · speed_gate_small × 6 kernels × 3, Haiku 4.5) — decides D8

- **Question (pre-registered, H10/H10b).** With speed unjudged (`full`) the agent keeps every
  change that is correct, including ones that make the program slower. Does a speed check timed
  at a size where the kernel runs long enough (`speed_gate_large`, T0.1 sizes) stop those without
  costing successes — and does the same check at the agent's small size (`speed_gate_small`)
  reject nearly everything?
- **Setup.** 54 trials, node 0, threads 6/12, repeats 5, agent `6eefbdf0` (Fixes 80–82, BEFORE
  Fix 84), one DiscoPoP profile per kernel. Stated deviation (D15): `hotspot` added. 12 h 35 min
  wall; host load at trial start 108 / **1,374** / 3,608 (min / median / max) from other users —
  outcome classes are usable, speedup magnitudes are not (lu 2.4× / 1.4× / 9.7× in one cell).
  Package integrity clean before and after every trial; credential sweep clean.
- **Result** (F = FASTER, pnf = correct and parallel but not faster, nc = no change):

  | kernel | `full` | `speed_gate_large` | `speed_gate_small` |
  |---|---|---|---|
  | 2mm | F F F (7.5, 11.1, 10.2×) | F F F (10.4, 8.1, 10.2×) | F F nc (6.8, 7.6×) |
  | floyd-warshall | **BROKEN**, F (4.7×), nc | F F nc (9.6, 1.9×) | nc nc nc |
  | jacobi-2d-imper | F F F (2.5, 5.7, 2.5×) | F F F (2.6, 1.4, 2.6×) | nc nc nc |
  | lu | **pnf pnf** (0.20, 0.20×), F (10.7×) | F F F (2.4, 1.4, 9.7×) | nc nc nc |
  | seidel-2d | nc nc nc | nc nc nc | nc nc nc |
  | hotspot | **pnf pnf pnf** (0.97, 0.09, 0.08×) | nc nc nc | nc nc nc |

  | arm | FASTER | slower-or-not-faster kept | BROKEN | no change | model calls | performance-stage rejections | agent min (total) | cost (USD-equivalent) |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|
  | `full` | 8 | **5** | **1** | 4 | 60 | 0 | 165 | 6.98 |
  | `speed_gate_large` | **11** | **0** | **0** | 7 | 70 | 3 | 241 | 8.52 |
  | `speed_gate_small` | 2 | 0 | 0 | 16 | 107 | 29 | 276 | 11.36 |

- **Reading.** H10 holds descriptively: the check at a proper size kept NO slower program
  (`full` kept five: on `lu` the model put `parallel for` on the innermost `j` loop — a
  parallel region per (k, i) — 5× slower, twice; on `hotspot` DiscoPoP's own inner-loop pragma,
  12× slower) and lost no success (11 FASTER against 8; on `lu` 3 of 3 against 1 of 3). H10b
  holds: at the small size the check rejected 29 changes and left 16 of 18 trials unchanged,
  at the highest cost. The one unsafe result of the run is in `full` (`floyd-warshall` rep1: a
  stack array that overflows at the verification size, `final_run_failed` → BROKEN by the rule
  of 19 Sep); the timed builds of `speed_gate_large` run at that size, so that arm cannot keep
  such a program — 0 BROKEN in 18, which n = 3 per cell does not prove.
- **Decision D8 (as pre-registered: the winner is E1's agent arm): `speed_gate_large`.**
- **What this run does NOT show, and what is owed (D19).** It has no `discopop_gate` arm: the
  main comparison — DiscoPoP alone against the agent — is missing for these six kernels and is
  added as a no-model run on the same server once the agent there carries Fix 84. `lu` ran with
  the misplaced DiscoPoP pragma in Phase B (its three `speed_gate_small` trials each show one
  `openmp_compile` failure there; after Fix 84 DiscoPoP alone reaches FASTER on `lu`) → the `lu`
  row is re-run. Every kernel here except `floyd-warshall` is class A (parallel as written):
  E10 measures the speed check, not restructuring.
- **Exhibits.** `results/E10_speed_check/exhibits/lu_inner_pragma_correct_but_5x_slower`,
  `results/E10_speed_check/exhibits/lu_with_speed_check_faster`. Archive: `results/E10_speed_check/runs/e10/` (1,201 files).


### `dp_alone_look_mac`, `dp_alone_tsvc_mac`, `dp_alone_fix84_mac` — 2026-09-19, Mac, DiscoPoP + gate ALONE on every benchmark (no model) — the look that exposed the benchmark problem

- **Why.** The author asked whether any benchmark challenges the model to restructure. The
  question needs DiscoPoP alone on every benchmark, which no run had measured.
- **Setup.** `discopop_gate` × 1, threads 4, repeats 3, Mac, agent `6eefbdf0` (before Fix 84),
  fixed DiscoPoP (Fixes 80–83). A LOOK, not an instrument: one profile, a loaded laptop, speeds
  not usable. The instrument is T0.11 on the server (3 profiles, 6/12 threads).
- **Result.** §5k. TSVC 25/25: all 18 R and all 4 D loops `no-change`, all 3 controls parallel.
  PolyBench 26 so far: 6 FASTER, 15 parallel-not-faster, 5 `no-change`. `dp_alone_fix84_mac`
  (`atax`, agent with Fix 84): `no-change` → parallel, DiscoPoP's inner Do-All applied.
- **Consequences.** D18 (classes measured, new R/A/D suite), D19's tooling was tested on it,
  Fix 84 found. The PolyBench numbers of the 12 kernels Fix 84 touches are void.
- **Finished 20 Sep:** all 31 of the first look and the 13-kernel repeat after Fix 84
  (`dp_alone_fix84_poly_mac`); both archived. Before/after table in §5k.


### `t0_7_explorer_fix`, `t0_6_dp_main_v2_fix`, `t0_2_stability_v2_fix`, `t0_8_packaging_fix` — 2026-09-19, server, the instruments on the FIXED DiscoPoP (Fixes 80–82; no model)

Same tools, same packages, same node as the runs of 18 Sep; only DiscoPoP changed.

| | before the fixes (18 Sep) | after (19 Sep) |
|---|---|---|
| **T0.7** explorer on one profile, 60 runs each — crashes | 2mm 0 · **pathfinder 40** · NPB `is` 0 | 2mm 0 · **pathfinder 0** · `is` 0 |
| T0.7 — Do-All sets / counts | 2mm 2 sets, 22 · pathfinder 2 sets, 10–11 · `is` 1 set, 19 | unchanged: 2mm 2 sets, 22 · pathfinder 2 sets, 10–11 · `is` 1 set, 19 |
| T0.7 — distinct task-pattern sets | 50 · 20 · 14 | 52 · 55 · 18 |
| **T0.6** benchmarks explored / lost to the explorer | 33 of 36 (`mg`, `pathfinder`, `nw` lost) | **34 of 34 attempted, no explorer retry anywhere** (`mg`, `nw` not attempted: L2/L3) |
| **T0.2** 6 kernels × 10 profiles | deps 1 value per kernel · patterns differ in every profile · blockers vary | the same: deps 1 value per kernel, 10 distinct `patterns.json` per kernel, blockers vary (seidel-2d 0 or 3, lu 198/199, trisolv 0 or 2) |
| **T0.8** layouts | 29 of 29 PolyBench + `is` identical kernel deps | 29 of 29 + `is` identical |

Reading: the crash is gone — it was the profiler's missing loop markers plus the
cross-function state match, not chance. What remains is the explorer's run-to-run variation
on an unchanged profile (upstream B4): task patterns differ in almost every run, the
`shared()` clause of some Do-Alls comes and goes (2mm), and `pathfinder` still reports 10 or
11 Do-Alls. So one profile per benchmark per run and "the DiscoPoP arm is a draw, reported
as a range" both stand; the 20-attempt retry stays only as a safety net (and for B6, the
patch generator's occasional hang).

### `pilot4` — 2026-09-18/19, server, the pilot on the FIXED DiscoPoP (Fixes 80–82) — decides D9

Eight model-driven core benchmarks (the nine minus NPB `mg`, see below) × `full` × 1, Haiku,
NUMA node 0, 22:07–23:52 UTC, host load in the hundreds. **The explorer succeeded on its
first attempt on all eight profiles** (pilot3: `mg` alone burnt 13 attempts).

| benchmark | group | outcome | best kernel speedup | calls | agent | note |
|---|---|---|---|---:|---:|---|
| 2mm | A | FASTER | 9.47× (STANDARD) | 1 | 138 s | model-written pragmas on both nests |
| hotspot | A | parallel-not-faster | 0.08× (LARGE) | 1 | 1120 s | the kept pragma is **DiscoPoP's own** (Phase B) on the innermost column loop — correct, 12× slower; speed is not judged in this arm (→ E10, D8). Its profile alone costs 235 s |
| jacobi-2d-imper | B | FASTER | 5.85× (EXTRALARGE) | 1 | 129 s | |
| floyd-warshall | B | FASTER | 2.92× (LARGE) | 2 | 234 s | pilot3's stack-array rewrite did not recur; one draw each way — the BROKEN case stays a finding |
| md | B | SCAFFOLD_MODIFIED | — | 12 | 3174 s | the rewrite edited the packaging's perturbed-input line in `main` (`pos[i] += pb_uniform()*0.01`); detected, not counted. `md` keeps `main` in scope (D4), which exposes that line; 12 calls and 53 min make it the cost outlier |
| seidel-2d | C | no-change | — | 3 | 299 s | declined, as a Gauss–Seidel sweep should be |
| trisolv | C | parallel-speed-not-measurable | 0.44× | 1 | 88 s | correct; too short to time at any runnable size (T0.1) |
| polybench/lu | C | FASTER | 2.85× (LARGE) | 1 | 76 s | the inner update loops are independent — the "order matters" hypothesis for this kernel is corrected by the data, as the plan allows |

**Read-out.** 22 model calls and 88 min of agent time for 8 trials: median 1 call and ≈ 2.2
min per trial, mean 2.75 calls and 11 min (two outliers: `md` 53 min, `hotspot` 19 min, the
latter almost all profiling and gate time). Verification adds ≈ 3–6 min per trial. Group B:
**2 FASTER of 3** (jacobi-2d-imper, floyd-warshall) → **D9: E1 runs with Haiku**; E2 keeps
both models. Budget: at ≈ 15 min per trial all-in, E1's 74 trials ≈ 18 h on one lane — two
lanes (one per NUMA node; T0.4: lanes cost ≈ 1 %) bring it to ≈ 9 h.
**NPB `mg`:** with Fix 81 + 82 its explorer no longer crashes, but the state assignment
advanced 24 % of 5,118 call-path states in two hours (erratic, 0.02–14 states/s) before the
run was lost; hours per explorer run, several explorer runs per trial. `mg` joins NPB `lu`
and `nw` as not analysable by DiscoPoP in practice (upstream report L3) unless the explorer's
state assignment is optimised — the author's decision; until then the model-driven core is
eight.

### `pilot3` — 2026-09-18, server, first pilot on the original-format packages — STOPPED after 4 of 9, superseded by `pilot4`

Nine model-driven core benchmarks × `full` × 1, Haiku, NUMA node 1, 19:31–21:34 UTC, host
load 100–400. Stopped by hand: NPB `mg` had failed 13 explorer attempts in a row (5.5 min
each) with the `IndexError` whose root cause was found meanwhile in DiscoPoP's profiler
(agent Fix 81, upstream report B3), and the remaining trials would have run on the unfixed
pass. **Taken on the UNFIXED profiler — not comparable with later runs; kept as a record.**

| benchmark | group | outcome | agent | what happened |
|---|---|---|---|---|
| 2mm | A | FASTER | 124 s, 1 call | the model annotated two loop nests itself; both verified |
| hotspot | A | parallel-not-faster | 1700 s, 4 calls | one correct pragma on the innermost column loop — kernel speedup **0.08×** at 6 threads (a parallel region per row per time step). Accepted because speed is not judged in this arm: the case E10 exists for |
| jacobi-2d-imper | B | FASTER | 86 s, 1 call | restructured and verified |
| floyd-warshall | B | **BROKEN** (rescored; was `VERIFY_FAILED`) | 238 s, 2 calls | the rewrite buffers the update in `DATA_TYPE temp[N][N]` **on the stack**: exact at the agent's SMALL size, a segmentation fault at the verification size LARGE. The gate never runs at the large size. An unsafe acceptance (H2), and the reason for the outcome-rule change of the same day |

Credential sweep after the stop: clean.

### `t0_4_timing` — 2026-09-18, server, T0.4 timing noise and lane interference (no model, partial)

`timing_noise.py`, 18:50–20:05 UTC, host load 15–430 from other users' jobs throughout.
Serial `-O3` and Polly-parallel (12 threads) builds, 10 runs per condition; `alone` =
pinned to 12 cores of one NUMA node as a campaign job is, `4_lanes` = four copies at once
on disjoint 12-core sets, `unpinned` = no pinning.

| program | binary | alone: median, CV | unpinned | 4 lanes: median, CV | resolvable (1 + 2·CV) |
|---|---|---|---|---|---|
| 2mm STANDARD | serial | 6.77 s, 3.6 % | 7.05 s, 3.7 % | 6.85 s, 5.5 % | 1.07× alone, 1.11× in lanes |
| 2mm STANDARD | Polly, 12 thr | 0.208 s, 0.3 % | 0.209 s, 0.4 % | 0.214 s, 0.8 % | 1.01–1.02× |
| hotspot LARGE | serial | 2.93 s, 4.2 % | 3.12 s, 1.2 % | 2.90 s, 1.5 % | 1.08× alone, 1.03× in lanes |

Reading: on this shared host a pinned serial measurement varies by about 4 %; with the
harness's 5-repeat medians a speedup of **1.1× and above is resolvable** — which is where
`FASTER_THRESHOLD` already sits (`cli.py`: 1.1). Four concurrent pinned lanes move the
median by ≈ 1 % (6.85 vs 6.77 s; 2.90 vs 2.93 s) and widen 2mm's spread to 5.5 %: lanes are
usable for correctness-only work and for speed at the 1.1× threshold, but headline speedups
are better taken one job per node. Pinning matters less than expected for the median
(unpinned 7.05 vs 6.77 s, +4 %) but is kept for reproducibility. Polly's parallel build of
2mm gives 32.6× over serial at 12 threads; **its build of `hotspot` runs minutes per
execution** (the stencil parallelised at the wrong level) — the run was stopped there after
hotspot's serial conditions, and `jacobi-2d-imper` was not reached. To repeat for the
remaining benchmarks with `--serial-only` once the tool has that switch; the numbers above
answer the question the plan asked.

### `t0_8_packaging`, `t0_7_explorer` — 2026-09-18, server, the last two steps of the D6 chain (no model)

* **T0.8 (16:22–17:32 UTC).** PolyBench: **29 of 29 kernels profiled in both layouts have
  identical kernel dependences** (the merged `adi` did not instrument within the limit, as
  before); Do-All blockers identical in 19, different in 10 — the explorer's own draw (T0.7);
  patterns identical in none (task patterns differ per run). NPB `is`: kernel dependences
  identical (247 = 247), blockers and even patterns identical; `mg`'s merged profile lost
  its explorer to the random `IndexError` on all 20 attempts here (the project profile
  explored; the comparison is repeated on the next pass). With the Mac run, 29 of 29
  PolyBench kernels and NPB `is` see the same program in both layouts.
* **T0.7 (17:32–18:00 UTC; 20 runs free + 20 per fixed seed on one profile each).**
  `2mm`: 0 crashes in 60 runs, 22 Do-Alls in every run, task patterns 9–63 and a different
  task set in 50 of 60 runs; **two distinct Do-All sets (42 : 18)** — reproduced on the Mac
  profile, the difference is the `shared()` clause of the `init_array` loops, listed in some
  runs and empty in others (OpenMP's default for those variables; `private` and `reduction`
  clauses did not vary). `pathfinder`: **40 of 60 runs crashed** with the `IndexError` in
  `TaskGraph.recursive_assignment`, hash seed free or fixed alike; among the 20 that
  finished, **10 Do-Alls in 14 runs and 11 in 6** — a loop is suggested parallel in some runs
  of the explorer on one unchanged profile, which is the strongest form of the T0.2
  finding (the tool now keeps every distinct set; the next run names the loop). NPB `is`:
  0 crashes, one Do-All set in 60 runs, 24 task patterns in every run but 14 distinct task
  sets. Fixing `PYTHONHASHSEED` changes nothing anywhere. The 20-attempt retry policy is
  confirmed (`pathfinder`: 0.67²⁰ ≈ 3·10⁻⁴ of losing the benchmark); a `discopop_gate`
  result on `pathfinder` is itself a draw and is reported as a range.

### `t0_3_oracle_mac` — 2026-09-18, Mac, T0.3: the oracle replayed on every candidate the gate ever judged (no model)

`oracle_study.py` over the seven archived runs that hold candidates (82 candidates; threads 4,
3 repeats, seed 7, per-kernel verification sizes; 16:55–18:40 CEST). 42 could be replayed;
the rest had no program to build (11 rejected at `clause`/`compile`), no packaged base (11 from
the two-file reproducer runs), or a patch that no longer applies (18 — 17 of them the
`matrix_prefix` runs, made on generator v2 of the calibration program before its repeat
loop was changed).

**Programs the gate rejected for a runtime reason (23): the oracle flags 19.**

| gate stage | replayed | oracle flags | how |
|---|---:|---:|---|
| `tsan` | 11 | 9 | 7 by the perturbed input (seidel-2d), 2 by a crash of the parallel program at 4 threads (2mm, NPB `is`) |
| `correctness` | 11 | 9 | 7 by the perturbed input (seidel-2d), 2 by a crash at 4 threads |
| `schedules` | 1 | 1 | crash at 4 threads (the segfault the schedule matrix had found) |

Two things stand out. **(i) Not one of the 14 wrong programs caught by output differed from
the original on the shipped input** — every one was caught by the perturbed input only
(`dump_seeded`, `digest_seeded`; `dump` and `digest` on the shipped input agreed in all
14). Without `--check-seed` the oracle would have passed 14 of the 19 it caught. The
seidel-2d case study is thus not one incident but the rule on that kernel: its shipped
input is a fixed point of the sweep. **(ii) The four it did not flag are two different
things.** Two are the DiscoPoP pragmas of the first project smoke run (`vecsum_proj`,
`privtemp_proj`, before Fix 78 — the `private` clause lost, so a shared temporary written by
every thread): ThreadSanitizer reports the race, and the output oracle sees **nothing** —
identical output in 12 runs on two inputs, stable at 4 threads. A race with a benign
outcome is invisible to an output oracle; the gate's TSan stage is the only check that sees
it (H3, C2). The other two are `calib/prefix` rewrites the gate rejected at `correctness`
with "output differs and no numerical slack is in effect" — `220348604973.56` against
`220348604973.56003`, a relative 10⁻¹⁶ (10⁻¹⁴ on the perturbed input) from a parallel scan
adding in another order. The oracle's 10⁻⁹ relative tolerance passes them; they are correct
programs. The gate's measured noise floor for that program was zero — the compiler does not
reassociate a sequential scan, so the calibration variants agree exactly and the floor
cannot anticipate reordering that only the *rewrite* introduces. That is a gate false
reject to report in E7, not an oracle miss.

**Programs the gate accepted (19): the oracle agrees on all 19** — 3 FASTER (2mm), 3
parallel-not-faster (seidel-2d, jacobi-2d), 10 correct but on programs too small to time,
3 changed-not-parallel (privtemp rewrites without a pragma). No false accept in the corpus.

Consequences: `--check-seed 7` stays mandatory in every verification (it is what makes the
oracle see a wrong seidel-2d at all); E7's read-out gains a named false-reject class (a
noise floor of zero on scans and reductions whose serial form the compiler never
reassociates); the two benign races are the example for "what only TSan sees".

### `t0_5_shares`, `t0_6_dp_main_v2`, `t0_2_stability_v2` — 2026-09-18, server, the D6 re-runs (no model)

Steps 2–4 of the chain, all 36 packaged benchmarks except NPB `lu` (calibration programs
left out), original-format packages, pinned to node 1, host load 50–430 from other users.

* **T0.5 (14:56–15:03 UTC, 36 benchmarks, 23 of them also at the verification size).** 280
  loops in scope; the 1 % floor (D1) drops 76 of them and gives up at most **1.96 % of
  runtime** in any benchmark (ludcmp; 1.7 % on the merged packages); a 5 % floor would give
  up 17.4 % on NPB `mg`. The top region is **the same at the agent size and at the
  verification size in 23 of 23** benchmarks measured at both (22 of 23 on the Mac). `main`
  holds timed work only in `md` (98 % of the timed region is a loop in `main`) and
  `pathfinder` (75 % of the run is its untimed generator in `main`) — D4 unchanged.
* **T0.6 (15:03–16:19 UTC).** 33 of 36 profiled and explored; DiscoPoP's *applicable,
  non-scaffolding* patterns inside `main` are **task patterns only** in every PolyBench
  kernel (1–2 each, over the kernel call), one task pattern in NPB `is`, none in `hotspot`;
  `md` alone has a Do-All in `main` (its force loop, 4 applicable). Same picture as the
  merged packages: excluding `main` removes no loop suggestion outside `md` (and
  `pathfinder`, below). **Three benchmarks lost their explorer on all attempts**: `mg` and
  `pathfinder` with the known random `IndexError` (the tool allowed 3 attempts; the harness
  allows 20 — the tool now does too), and **`nw` with a different, apparently deterministic
  failure** (`state_id: None`, 3 of 3) that the merged packaging never showed because `nw`
  was never explored by this study before. `nw`'s `main` decision (D4) therefore waits for
  the diagnosis (run `_diag_nw`, below). `adi` took 2312 s (its instrumenting compile).
* **T0.2 (16:19–16:22 UTC, 6 core kernels × 10 profiles).** Reproduced exactly: the
  dependence multiset (sink, type, source, variable) has **one value per kernel in all 60
  profiles**; `patterns.json` differs in every profile (10 of 10 distinct in five kernels,
  9 in `lu`); suggestion counts move 18–33 (seidel-2d) to 34–82 (2mm); Do-All blockers
  vary between profiles (seidel-2d 0 or 3, jacobi-2d 0 or 1, lu 198/272/273). Profiling is
  deterministic, reporting is not — in this layout too.

### `t0_1_sizes_v2` — 2026-09-18, server, T0.1 on the original-format packages (no model)

First step of the D6 re-run chain (`t0_chain.sh`, pinned to NUMA node 1; 14:43–14:56 UTC;
host load 15–250 from other users' jobs during the run). All 34 benchmarks (cholesky, trmm,
durbin excluded as before), sizes SMALL…EXTRALARGE, 3 runs each, 111 measurements.
**Every verification size and every timing size is identical to the committed table**
(`merge_kernel_sizes.py --dry-run`: 0 added, 0 changed, 34 unchanged). Serial kernel times
agree with the merged-package run within ±7 % on the 58 measurements above 50 ms (median
ratio 1.00; extremes ludcmp/LARGE 1.05, lu/LARGE 1.06, fdtd-2d/EXTRALARGE 1.07, gemm/STANDARD
0.95) — the packaging does not change the serial program, and the NUMA pinning holds the
timing steady under a loaded host. Six EXTRALARGE runs fail with a segmentation fault before
the timer (atax, bicg, gemver, gesummv, mvt, trisolv: PolyBench's stack-allocated arrays at
that size), as in the first run; none of them is a chosen size. The committed table is
re-stamped from this run (`source_run`, `measured`, `host` per entry).

### `pkg_smoke_local`, `t0_5_proj_smoke`, `t0_6_proj_smoke`, `t0_8_packaging_mac` — 2026-09-18, Mac, the original-format packages through the harness and the instruments (not an experiment)

* `pkg_smoke_local` (arm `discopop_gate`, no model): **`polybench/2mm`** as a project — unity profile 4.4 s + 2.6 s + explorer 32 s, DiscoPoP's two pragmas applied in `2mm.c`, verified **FASTER 2.82× at 8 threads**, dump and seeded dump exact. **`npb/is`** as a project — profile 3.6 s + instrumented run 2840 s (this Mac was running three DiscoPoP jobs at once; 131 s-class on the server) + explorer 46 s; DiscoPoP's four suggestions: three dropped by the clause check for naming loop-body locals — a scope defect in DiscoPoP's own clauses, now repaired before the gate (agent Fix 79) — and, re-run with the repair, all four rejected by the real judges (three ThreadSanitizer races, one `private(k)` on a value read after the loop): outcome `no-change`, verification exact, a genuine baseline result for `is`. `pragmas_in_final` counts only pragmas the run ADDED: `polybench.c` carries nine inactive ones inside its PAPI block, which had inflated the count to 11 and would have made `changed-not-parallel` unreachable.
* `t0_5_proj_smoke`: T0.5 on `polybench/2mm` and `npb/mg` as projects — regions attributed to their functions across files (mg: 63 in scope, `zran3` etc.).
* `t0_6_proj_smoke`: T0.6 on `2mm` as a project — 79 patterns, 41 in `main`, the applicable non-scaffolding ones all task patterns (as on the merged file); `mg`'s instrumented run timed out on the loaded Mac (server re-run).
* `t0_8_packaging_mac`: see instrument T0.8 — kernel dependences identical in both layouts on every kernel compared.

### `e2e_review_2026-09-18` — Mac, the whole agent under different argument sets (point 5 of the author's list; not an experiment)

*Purpose.* After the review's fixes, run the complete agent — model included — under the
argument sets the arms use, and watch that each behaves as designed. Sonnet, `--edit-mode
direct`, campaign common flags (`--no-require-speedup --min-runtime-share 0.01`,
`--check-input 7`, packaging functions excluded). Calibration programs only (never a
result). Logs and candidates are in the session scratchpad (`matrix_prefix*`,
`matrix_privtemp`, `e2e_p3`).

**A two-file program** (`docs/MULTIFILE.md` reproducer, `full` arm, budget 2): unity
profile → Tier-2 function `kernel` in `kern.c` → model annotates the outer loop
(`private(t) firstprivate(n)`) → gate on the real two-unit build passes → fast refresh (76/76
dependences carried) → the loop nested inside is COVERED, not attempted (before Fix 76 it
received a second call whose "rewrite" re-spelled the pragma) → `smooth` rewritten as an
O(n²) recomputation, correct and race-free (this is what led to D7) → full re-profile before
Phase B → Settle verified the finished file. 2 model calls, exit 0.

**`calib/prefix` (a true prefix-sum recurrence) under eight argument sets**, one run each:

| arm flags | calls | kept | what the log shows |
|---|---|---|---|
| `full` (budget 2) | 5 | 1 rewrite, 1 LLM pragma | attempts failed at `clause` (a name declared in the loop named in a clause), `correctness` at a fixed thread count, and `correctness` on the perturbed input `7` — the rewrite was right for the profiled input and wrong for the other; the kept one parallelises the repeat loop |
| `discopop_gate` (budget 0) | 0 | 0 | DiscoPoP's own pragma on the outer repeat loop rejected at `tsan` (WAW on `c`) |
| `--no-llm-pragmas --no-fast-refresh` (budget 1) | 2 | 0 | pragma-free rewrites, full re-profile path; both failed `correctness` |
| `--evidence none` (budget 1) | 2 | 1 rewrite, 1 LLM pragma | first attempt failed `schedules` (segfault at 4 threads — caught); the kept one parallelised the repeat loop by doing all the work in the LAST repetition only: race-free, output-preserving, no parallel work. The harness would score it `parallel-not-faster`; the calibration programs' repetitions were idempotent — fixed in generator v3 (repetitions now read what the previous one wrote) |
| `--restructure-depth 1` (budget 1) | 2 | 0 | both failed `correctness` on input `7`; the depth path was not reached (nothing kept) |
| `--no-hotspots` (budget 1) | 2 | 0 | "falling back to the static workload proxy for ranking"; both failed `correctness` |
| `--no-llm-pragmas --llm-recon` (budget 1) | 2 | 0 | reconstruction not reached (nothing kept) |
| `--require-speedup` (budget 1) | 2 | 0 | "require ≥ 1.1× measured"; both failed `correctness` before the timing stage |

Every run: exit 0, every attempt recorded in `candidates.jsonl` with its stage and
diagnostic, usage logged per call. A recurrence is the right program for the failure
paths and the wrong one for the keep paths; those are run on `calib/privtemp` (below).

**`calib/privtemp` (a privatisable false dependence), the keep paths** (generator v3, budget 2):

| arm flags | calls | kept | what the log shows |
|---|---|---|---|
| `--no-llm-pragmas --no-fast-refresh` | 1 | 1 rewrite + 1 DiscoPoP pragma | pragma-free rewrite passes the sequential gate → full re-profile → "DiscoPoP now finds: do_all @ lines 106–114" → Phase B applies its `private(t,r) shared(a,c)` → Settle verifies. **This is the path F20 had closed:** before Fix 76 the rewrite's region was covered, Phase B saw no candidate and Settle dropped the rewrite as an orphan |
| `--restructure-depth 1` | 1 | 1 rewrite, 1 LLM pragma | "Full re-profile — depth 1 will restructure from this data", runtimes re-measured; then "0 new at depth 1": the parallel loop is covered with its measured share and nothing sequential remains in the function, so depth 1 correctly has nothing to do — not, as before Fix 76, because everything a rewrite creates was hidden |
| `--no-llm-pragmas --llm-recon` | 4 | 1 rewrite + 1 DiscoPoP pragma | attempt 1: fast refresh, reconstruction "6 claimed, 6 outside the gap", DiscoPoP finds nothing → reverted (source, profile AND runtime measurements restored — the F17 path); attempt 2: "2 claimed, 2 resolved, 1 loop declared independent, 4 contradicting static" (logged, never acted on) → do_all exposed → Phase B applies → Settle verifies |

Every mode reached its designed end state. What the runs also showed, and what was done about it:
the O(n²) recomputation (D7), the idempotent repeat loop (generator v3), and the
project-mode clause loss (Fix 78).

### Finding — NPB `lu` cannot be profiled by DiscoPoP (2026-09-17)

DiscoPoP's instrumenting compile of `npb/lu` (4,134 lines, one translation unit) did not
finish within **one hour on either machine**: `discopop_cxx` was killed by the cap on the Mac
(clang 19) and again on the server (clang 20, `exit 124`, peak memory small, so it is compile
time and not memory). The dataset class is irrelevant — this is the static pass over the
source, before the program is ever run.

Why it matters beyond one benchmark: the agent re-profiles after every kept rewrite and once
before Phase B, and a fast refresh still re-runs that same compile. A benchmark whose
instrumentation costs an hour therefore costs hours per trial, whatever the model does.

`npb/mg` also failed on the Mac, in the instrumented **run** (30-minute cap), having compiled
in 10 min — but **on the server it is cheap: 6.4 s to instrument (10 GB peak) and 131 s to
run**. The Mac failure was the Mac: 10 GB of peak memory on a 16 GB laptop. So the
applications are to be profiled on the server only, and a local failure says nothing about a
benchmark.

That also isolates `lu` as a genuine outlier rather than a size effect: `mg` is 2,133 lines
and instruments in 6 s, `lu` is 4,134 lines and exceeds an hour on the same machine. `lu` is
being re-measured with a four-hour cap to find its real cost (which E5 wants anyway).

Consequences to decide once `mg`'s numbers are in: `lu` is in the core ten (group C, "order
matters") and is one of the three programs of E11 against RepoOMP. If it cannot be profiled,
it can still appear as a *verify-only* baseline (expert OpenMP, Polly, RepoOMP's released
outputs all run through the harness without the agent), but the agent cannot produce a result
for it, and both E1's group C and E11 shrink. This is a property of DiscoPoP at this program
size, not of the agent, and belongs in the thesis as such.

### `local_obs1` — 2026-09-17, Mac, observed full run (point 5, not an experiment) — PARTIAL

`full` arm, Haiku, `--min-runtime-share 0.01` (D1), agent with Fixes 58–62 (uncommitted),
`2mm`, `jacobi-2d-imper`, `seidel-2d`, `md`. Stopped by the author before `md` wrote its
record (it had reached Phase B). No model call failed. Review of the candidates by hand is
still to do.

| Benchmark | Calls | Output tokens | Agent s | Outcome (first) | Outcome (after the check was relaxed) |
|---|---|---|---|---|---|
| 2mm | 4 | 29,707 | 358.7 | SCAFFOLD_MODIFIED | FASTER, 2.39× at 2 and 3.41× at 4 threads |
| jacobi-2d-imper | 3 | 14,097 | 207.2 | SCAFFOLD_MODIFIED | parallel-not-faster, 0.30× / 0.80× |
| seidel-2d | 4 | 40,040 | 473.8 | SCAFFOLD_MODIFIED | SCAFFOLD_MODIFIED |

What was flagged, read from the diffs:

- `seidel-2d`: `PB_PERTURB` rewritten again, as in `pilot2`. A true catch.
- `2mm` and `jacobi-2d-imper`: the model **copied the kernel's loops into `main`, inside the
  timed region**, parallelised them, and removed the call to the kernel function. The timer
  still covers the whole computation, so the timing is honest. The scaffolding check's rule
  that a call-only timed region must stay identical is **too strict** here, a false
  positive. To fix: allow computation to move *into* the timed region and forbid it moving
  *out* (for example, no new loop in `main` outside the region).
- **For D4:** with `main` in scope, the model worked on `main` in all three kernels, because
  `main` ranks first at 100 % of runtime. It either edits the packaging's code or inlines the
  kernel into `main`.

**`md` (C++), recovered without re-running it.** The trial was stopped before its record was
written, but its working directory survived, so its candidates and its final source could be
judged directly. 8 candidates: 3 accepted (the force loop in `compute`, the time-step loop in
`main`, `dist`), 5 rejected — output changed; **not repeatable at 4 threads** (a race the
schedule stage caught, not the output check); one loop not in OpenMP-canonical form; and two
of DiscoPoP's own Phase-B pragmas, also non-canonical loops. All five rejections look correct.

Verified independently with `verify-source` (STANDARD, 2 and 4 threads, 3 repeats): the
scaffolding is untouched, the values are correct (3.5e-15, pure reduction rounding) — and the
program is **12–14× SLOWER** (0.073× at 2 threads, 0.066× at 4). The accepted pragmas sit on
inner loops that are entered once per particle pair, so each entry starts a parallel region.
Outcome `parallel-not-faster`.

This is the clearest case so far for E10: the agent's speed check is off in every arm, and
with it on, all three of these changes would have had to prove themselves or be dropped. It
also shows the gate working as designed on safety (no wrong result accepted) while being
blind to cost by configuration.

**Review of every candidate by hand (the point of this run).** 11 candidates were recorded
across the three finished trials; `md` has none, its record was never written.

| Verdict | Count | Judgement |
|---|---|---|
| Rejected at `compile` | 2 | correct — the rewrite did not build |
| Rejected at `tsan` | 2 | correct — `2mm` #1 carries `#pragma omp parallel for` with no `private`, and `i`, `j`, `k` are function-scope, so the threads shared them; `seidel-2d` #1 is a real race in the sweep |
| Rejected at `correctness` (perturbed input) | 2 | correct — both are Jacobi-style rewrites of the Gauss–Seidel sweep, right on the shipped input and wrong on the seeded one |
| Rejected at `clause` | 2 | **wrong** — `private(j, k)` on 2mm and `private(i, j)` on jacobi-2d-imper are correct; agent Fix 63 |
| Passed | 3 | 2mm: correct, verified FASTER 3.41× at 4 threads; jacobi: correct but slower (0.30× / 0.80×); seidel: the `PB_PERTURB` rewrite, caught by the scaffolding check |

So the gate made 6 correct rejections and 2 wrong ones, and no incorrect rewrite was accepted.
The two wrong rejections were not merely lost attempts: on 2mm the model spent a further
attempt to produce a needless `lastprivate(j, k)`, which is what the run finally kept.

**The agent followed its design**: regions were taken in order of measured share, each
Tier-2 region got its 3 attempts, the failure feedback named the stage, a build error was
refunded rather than charged, and Phase B ran once at the end. Two design observations:
`main` ranks first and attracts the model (see D4); and the 1 % floor (D1) left 2mm with 3
in-scope regions where the pilot had 7.

Also found: a timed-out subprocess leaves its grandchildren running (T0.6's `discopop_cxx`
on `lu` kept compiling for over an hour after its timeout). The harness uses the same
`subprocess.run(timeout=…)` pattern, so it is to be fixed there too.

### T0.7 — 2026-09-16, Mac, DiscoPoP explorer on one fixed profile (no model)

Not a harness run; commands and results are in §5b ("Refined"). Profiles taken with
`discopop_cc` / `discopop_cxx` and one run of the packaged 2mm and `pathfinder`; then
`discopop_explorer` alone, run 10 times with `PYTHONHASHSEED` free, 10 times fixed
(0 and 7, five each), and for `pathfinder` 20 more times free. Result: the output differs
between runs on one profile with the seed fixed or not, and `pathfinder` crashes in 75 % of
runs. It is to be repeated on the server before E1, because the crash rate decides whether
20 attempts are enough there.

### `t0_5_shares_mac` — 2026-09-16, Mac, T0.5 runtime share per region (no model)

`agent/tools/share_study.py`. DiscoPoP's hotspot detection run exactly as the agent runs it
(instrument, one run, analyse), for all 37 packaged benchmarks at the agent's size and, for
the 23 with a T0.1 verification size, at that size too. Every measured region is placed in
its function (C++ names demangled with the agent's own helper, Fix 59), given its source
span, and marked as excluded or not, inside `main` or not, and inside the timed region or
not. Output: `regions.csv`, `summary.json`. Measured on the Mac, not the server: the shares
are ratios of times on one machine, and the conclusions below rest on their order of
magnitude. A server repeat can confirm them if needed.

**Loss bound.** A region with share s can raise whole-program speed by at most 1/(1 − s).
The runtime a floor gives up is therefore at most the summed share of the loops it drops that
no kept loop contains (a kept outer loop covers what is nested in it) and that no other
dropped loop contains (so no time is counted twice).

**What a `--min-runtime-share` floor removes** (in-scope loops, agent size, all benchmarks):

| Floor | Loops dropped (of 445) | Benchmarks losing > 0.5 % | Worst bound, agent size | Worst bound, verification size |
|---|---|---|---|---|
| 0.5 % | 158 | 3 | 0.8 % (npb/lu) | — |
| 1 % | 185 | 8 | 1.7 % (polybench/ludcmp) | 1.2 % (npb/mg) |
| 2 % | 205 | 8 | 3.2 % (npb/mg) | 1.7 % (npb/mg) |
| 5 % | 260 | 9 | 19.7 % (npb/mg) | **16.4 % (npb/mg)** |
| 10 % | 282 | 9 | 32.5 % (npb/mg) | — |

PolyBench concentrates its time in one loop nest and barely notices any floor. NPB spreads
it over many 3–5 % loops that a real parallelisation does target (`mg`: `rprj3`, `norm2u3`,
`mg3P`; `lu`: `blts`, `buts`; `is`: `rank`), and a 5 % floor would discard a sixth of `mg`'s
timed work. The verification-size column applies the floor as the agent does, at its own
size, and prices the dropped loops at the size results are judged at.

**Does the order survive a change of size?** Among in-scope loops present at both sizes, the
top loop is the same in 22 of 23 benchmarks. The exception, `3mm`, is a near-tie between its
two matrix products (32.3 % and 31.3 %). Median Spearman correlation 1.00. Shares grow
toward the kernel as size grows (fdtd-2d 35 → 84 %), but the order the agent acts on is the
same.

**What `main` holds.** In all 30 PolyBench kernels, no loop in `main` was measured at all:
`main` is scaffolding (the seeded `PB_PERTURB` path is not taken in the unseeded profiling
run). NPB `is`, `lu`, `mg`: only the driver's digest loop, 0 %. `hotspot`: one untimed loop,
0.9 %. `nw`: 8 untimed loops (input generation), ≤ 3.5 % each. **`pathfinder`: loops in
`main` hold 77.9 % of runtime *outside* the timed region (the grid generator) and 12.7 %
inside it.** **`md`: the time-step loop in `main` is inside the timed region, 98.1 %.**

**DiscoPoP's hot/cold label** carries no information in this setting (§5c): every
measured region was `YES` or `MAYBE`, never `NO`.

### `pilot2` — 2026-09-16, server, first agent trial with working model calls

Same settings as the void `pilot_seidel` (seidel-2d, arm `full`, Haiku 4.5, threads 6 and 12,
3 repeats, verification at EXTRALARGE), new run id. Agent 3b5ab817, harness ee9fe07, both
clean, parity OK, `== auth ok` from the new preflight, credential sweep clean.

**Calls and cost.** 8 model calls, **0 failed**, no cutoff. 168 input tokens,
61 834 output, 628 785 cache read, 102 670 cache creation, $0.58 at API rates. Model time was
569 s of the agent's 587.6 s: **97 % of agent time is waiting for the model** (~71 s and
~7 700 output tokens per call in `--edit-mode direct`). Verification took 106.9 s, profiling
about 3 s. One trial took **~11.6 minutes**.

**Gate.** 13 candidates, 12 rejected, each for a reason visible in `candidates.jsonl`.
Phase A (model rewrites, 8): 3 wrong on the perturbed input, 2 ThreadSanitizer races, 2
clause errors (`private(j)` on a variable read after the loop), 1 passed. Phase B (DiscoPoP
pragmas, 5): 2 races, 3 wrong on the perturbed input. seidel-2d is an in-place Gauss–Seidel
sweep with no simple correct parallelisation, so rejecting every kernel rewrite is the right
answer.

**The one accepted rewrite is not in the benchmark.** It is in `main`, in the harness's
perturbation code: the model expanded `PB_PERTURB` and parallelised how the seeded noise is
added, keeping the random-number order, so every check passed. That code runs only on the
perturbed-input check, never inside the timed region, so the harness measured 1.001× (6
threads) and 0.999× (12 threads) and classified the trial `parallel-not-faster`, correctly.
But `rewrites_kept = 1`, `pragmas_llm = 1` and `source_changed = true` count it as a
parallelisation, and the agent's own verdict reads `BEAT` (1 usable pragma against
DiscoPoP's 0). Cause: `main` ranks first at 100 % of runtime (the problem left open in Fix
54), and `--exclude-functions` excludes whole functions, not the scaffolding inside `main`.
In every PolyBench kernel `main` is pure scaffolding (init call, `PB_PERTURB`, the timer
calls, the kernel call, output). One of the three regions the model was asked about, and 2
of its 8 calls, went to that scaffolding.

**The wider risk this exposes.** Nothing stops a rewrite of `main` (or of NPB's `npb_main`,
which holds the injected timer calls) from moving `pb_timer_start` / `pb_timer_stop`. A
smaller timed region would show up as a speedup that does not exist. The only guard today is
the `kernel_program_disagree` flag, which marks such a trial but does not reject it.
**Resolved the same day:** the harness's scaffolding check now catches both, and rescoring
gives this trial the outcome `SCAFFOLD_MODIFIED` (change log).

**Budget.** The first real measurement: ~11.6 min per trial for a small kernel. The planned
~620 trials would take ~120 h back to back, against the plan's ~50 h. Applications have more
regions and Sonnet is slower, so this is a lower bound.

### `pilot_seidel` — 2026-09-16, server — **VOID, no model call succeeded**

The first agent trial on the server, and **not a usable result**. It is kept here because
what it nearly hid is the point.

Recorded: `outcome=no-change`, `agent_s=136.4`, `verify_s=106.7`, `llm_calls=9`,
`candidates_recorded=4`, `rewrites_kept=0`, 0 input and 0 output tokens, cost 0. Read as a
result, that says the agent examined seidel-2d and correctly declined to restructure a
loop-carried recurrence — a plausible and even flattering finding.

It is false. **All nine model calls failed with HTTP 401**: the OAuth token was invalid.
`agent.log` shows the same three lines per region — `LLM call failed: Claude Code returned
an error result: success`, `LLM returned invalid output — retrying`, and after three
attempts `SKIPPED (budget exhausted)` — for each of the three regions. The run was fast
because nothing ran, cost nothing because nothing was billed, and produced no candidate
because no model ever answered.

Diagnosis (each step by direct test, in this order): the zero-token usage records were
checked against `_summarise_usage`'s key names — correct, the records really were empty; a
minimal SDK probe on the server with the job's own environment returned
`result = 'Failed to authenticate. API Error: 401 OAuth access token is invalid.'` while
`subtype` read `"success"` and the CLI exited **0**; the same token failed identically **on
the Mac** under an isolated `CLAUDE_CONFIG_DIR`, which placed the fault in the credential
itself rather than the server, the SSH transport or the Keychain.

The credential was **truncated, not expired**. The stored value looked entirely valid —
`sk-ant-oat01-` prefix, no whitespace, no stray newline — and was 80 characters; the real
token is **108**. `claude setup-token` prints it across two lines, and exactly the first
line had been captured: 28 characters lost at the wrap, in a value with nothing to mark it
as incomplete. It failed with the same `401 OAuth access token is invalid` that a revoked
token gives. Two further traps sat behind it: `security add-generic-password` *refuses* to
overwrite an existing item rather than replacing it (so a corrected token never reaches
storage without `-U`), and the `export` that `setup-token` prints lives only in the shell
that ran it — storing from `$CLAUDE_CODE_OAUTH_TOKEN` in a different window silently saves
an empty string. Both were hit while fixing this. Once stored whole, the same token
authenticated on the Mac and the server on the first attempt.

The local smoke run had worked only because the CLI there falls back to an interactive login
session — the token had never actually been exercised before this run.

Three things follow, and all three are now fixed (change log, 2026-09-16): the agent reads
the CLI's result body and treats an authentication failure as fatal (Fix 58); every trial
records `llm_call_failures` beside `llm_calls`; and `job.sh` makes one probe call before
the first trial and aborts the job if it fails. **Nothing from this run enters any
analysis, and the `--min-runtime-share` question it was meant to answer is still open.**

**What it does show**, because these parts did run: the DiscoPoP half is sound. Phase B
proposed four pragmas and the gate rejected all four for real reasons — two ThreadSanitizer
races in `kernel_seidel_2d`, one correctness failure on the perturbed input, one
`openmp_compile` failure — and verification was genuine, the sequential kernel measuring
9.596 s at EXTRALARGE against T0.1's 9.6 s.

### Finding — model calls stop in a cliff, not a trickle (2026-09-16, from existing logs)

Re-reading the two Mac smoke runs with the new `llm_call_failures` counter turned up a
pattern that had never been looked at, because until Fix 58 every failure printed the same
uninformative string. Both runs lost a large share of their calls — and they lost them all
at once, at the end:

| Run | Started | Calls | Failed | Pattern (`o` ok, `X` failed) |
|---|---|---|---|---|
| `smoke_local_seidel2d_c` | 2026-09-14 18:11 | 22 | 17 (77 %) | 5 × `o`, then 17 × `X` |
| `smoke_local_seidel2d_c_seeded` | 2026-09-14 22:05 | 35 | 10 (29 %) | 25 × `o`, then 10 × `X` |

Neither is intermittent. Each is an unbroken tail of failures that begins at one call and
never recovers, spanning several regions and therefore several independent CLI sessions — so
per-session staleness (the cause the retry logic was written for) does not explain it. A
global limit does. The earlier run hit the wall after 5 calls and the later one after 25,
which is what a rolling usage window looks like when it is already partly spent and then
resets. Both used `--edit-mode direct`, whose calls are multi-turn (`max_turns=24`, file
tools) and therefore far heavier than a single-response call.

**Working hypothesis: subscription usage-limit exhaustion — not an agent defect.** It is not
yet confirmed: these logs carry no timestamps, and no per-call usage log exists for them
(`$DP_LLM_USAGE_LOG` arrived with Fix 53 on the same day), so neither the time to the cliff
nor the tokens consumed can be recovered. The next model-calling run settles it, because
Fix 58 makes the CLI's own reason visible where it was previously collapsed to
`error result: success`.

**Why it matters more than the smoke runs themselves.** At ~20 calls per trial the planned
~620 trials are ~12 000 calls. If a window allows only tens of heavy calls, the campaign
meets this wall constantly — and before Fix 58 every encounter produced a trial that looked
clean: model calls counted, no candidate, outcome `no-change`. The pre-registered budget
(~50 h over four lanes) assumes calls succeed; it has never been tested against this limit.
Consequences for the plan are open until the next pilot measures it.

### `t0_1_apps` — 2026-09-16, server, T0.1 sizes for the applications (no model)

`agent/tools/size_table.py`, pinned to NUMA node 1, clang-20 / clang++-20 `-O3`, 3 repeats,
median serial kernel time. The seven applications plus `polybench/lu`, all keyed by full name.
`agent/config/kernel_sizes.json` now holds **34 benchmarks** (the three excluded weak-oracle kernels —
`cholesky`, `durbin`, `trmm` — are deliberately absent).

| Benchmark | Timing size (≥ 0.25 s) | Verification size (≥ 1 s) | Longest measured |
|---|---|---|---|
| burkardt/md | STANDARD | STANDARD | 1.52 s |
| rodinia-3.1/nw | LARGE | LARGE | 1.01 s |
| rodinia-3.1/hotspot | STANDARD | LARGE | 2.81 s |
| npb/mg | STANDARD | LARGE | 2.05 s |
| polybench/lu | LARGE | LARGE | 1.06 s |
| rodinia-3.1/pathfinder | EXTRALARGE | none | 0.32 s |
| npb/is | LARGE | none | 0.44 s |
| npb/lu | LARGE | none | 0.27 s |

**The collision this run was repeated to fix is now visible in the numbers:** `npb/lu` reaches
0.273 s at LARGE while `polybench/lu` reaches 1.057 s. The first application run, keyed by bare
name, had given NPB's `lu` the PolyBench kernel's figures — every `npb/lu` trial would have been
verified at the wrong size, silently.

**Eleven benchmarks now have no verification size** and are correctness-only, reported as
`parallel-speed-not-measurable` (§6): the eight PolyBench kernels found earlier, plus
`rodinia-3.1/pathfinder`, `npb/is` and `npb/lu`. For the three NPB entries this is a property of
the class sizes that fit the agent's profiling budget, not of the packaging.

### `t0_2_stability` — 2026-09-16, server, T0.2 DiscoPoP profile stability (no model)

`agent/tools/profile_stability.py`, pinned to NUMA node 1: the six PolyBench kernels of the
core ten, profiled from scratch 10 times each at the agent size (SMALL) — `discopop_cc`,
instrumented run, `discopop_explorer`. 60 profiles, 0 failures, 2.1–3.5 s median each,
05:08–05:11 UTC.

| Kernel | Suggestions | Do-All blockers | Distinct `patterns.json` | Distinct dependence file (as written) | Distinct dependence file (lines masked) | **Distinct dependence multiset** |
|---|---|---|---:|---:|---:|---:|
| 2mm | 30–77 | 0 ×10 | 10 | 10 | 6 | **1** |
| jacobi-2d-imper | 14–40 | 0 ×3, 1 ×7 | 10 | 10 | 2 | **1** |
| floyd-warshall | 11–26 | 0 ×3, 3 ×7 | 10 | 10 | 9 | **1** |
| lu | 12–31 | 0 ×6, 1 ×4 | 10 | 10 | 4 | **1** |
| seidel-2d | 11–26 | 0 ×7, 3 ×3 | 10 | 10 | 1 | **1** |
| trisolv | 11–45 | 0 ×6, 2 ×4 | 10 | 10 | 1 | **1** |

The last column is the decisive one: every dependence taken as (sink, type, source, variable)
with the per-run labels dropped, counted. **It has exactly one value per kernel across all 60
profiles** — DiscoPoP observed precisely the same dependences, with the same repeat counts,
every time.

Everything derived from them moved. **`patterns.json` differed in every one of the 60
profiles**, and for the same program the suggestion count varies by up to a factor of three
(2mm 30–77). The Do-All blockers — the evidence the agent passes to the model as "why this loop
is not parallel" — are present in some profiles of a kernel and absent in others. The
line-masked column sits in between and overstates the variation on its own: two `floyd-warshall`
profiles produced the same 376 masked lines, differing only in the order of entries within a
line and in how one sink's dependences were split across lines.

An identical study 17 minutes earlier (before the multiset column was added) gave the same
picture with different draws — seidel-2d blockers 0 ×4 / 3 ×6 against 0 ×7 / 3 ×3 here, 2mm
27–78 against 30–77 — which is the effect itself, repeating across studies.

**Conclusion for the thesis:** DiscoPoP's *profiling* is deterministic — it observes the same
dependences every run. Its *labels* are not: memory-region ids come from addresses and callpath
states are numbered per run, and the explorer's output moves with them. The explorer itself is
deterministic given a fixed profile (verified across both machines and two `PYTHONHASHSEED`
values, §5b).

### `t0_1_sizes` — 2026-09-15, server, T0.1 size calibration (no model)

`agent/tools/size_table.py`, pinned to NUMA node 1, clang-20 `-O3`, 3 repeats, median serial
kernel time (`DP_TIMED_REGION_SECONDS`). 27 kernels (cholesky, trmm, durbin excluded, §2),
SMALL → EXTRALARGE, stopping at the first size whose kernel reaches 1 s. 20:43–20:49 UTC, host
load 2.2 → 3.2. Two earlier attempts stopped on a crash (atax EXTRALARGE) and on a CSV bug; their
logs are kept in `_launcher/`. Result committed as **`agent/config/kernel_sizes.json`** — part of the
pre-registered configuration.

| Kernel | Timing size (≥ 0.25 s, E10) | Verification size (≥ 1 s) | Longest measured |
|---|---|---|---|
| 2mm · 3mm · gemm · symm | STANDARD | STANDARD | 3.5–10.3 s at STANDARD |
| adi · correlation · covariance · floyd-warshall · gramschmidt · syr2k · syrk | STANDARD | LARGE | 1.5–8.0 s at LARGE |
| doitgen · dynprog · fdtd-apml · lu · ludcmp | LARGE | LARGE | 1.1–11.1 s at LARGE |
| seidel-2d | LARGE | EXTRALARGE | 9.6 s |
| fdtd-2d · jacobi-2d-imper | EXTRALARGE | EXTRALARGE | 1.9 s, 1.3 s |
| jacobi-1d-imper | EXTRALARGE | none | 0.36 s at EXTRALARGE |
| atax · bicg · gemver · gesummv · mvt · trisolv | none | none | 0.02–0.18 s at LARGE; EXTRALARGE crashes (segfault) |
| reg_detect | none | none | 0.11 s at EXTRALARGE |

Consequences:

- **20 kernels** have a verification size; their speedup is measured there.
- **8 kernels never reach 1 s** at a size that runs: atax, bicg, gemver, gesummv, jacobi-1d-imper,
  mvt, reg_detect, trisolv. Their serial kernels are too short for thread start-up to pay off,
  so a speedup cannot be shown on them. They still count for correctness (BROKEN or not); decided
  2026-09-15, before any agent run: a correct parallel result on them gets the outcome
  `parallel-speed-not-measurable` instead of FASTER / parallel-not-faster; they are excluded
  from every speed statistic (FASTER rates, speedup medians and means, H1), and their ratios are
  listed in a separate table labelled as not being speedups.
- **E10 kernels:** of the core ten's PolyBench kernels, 2mm (STANDARD), floyd-warshall
  (STANDARD), seidel-2d (LARGE), lu (LARGE) and jacobi-2d-imper (EXTRALARGE) have a timing size;
  trisolv has none and is excluded from E10.
- EXTRALARGE segfaults on six kernels whose arrays exceed what the generated code handles
  (atax's is 100000 × 100000 doubles); those sizes are out of reach, not measurement failures.

### `smoke_local_seidel2d_c` — 2026-09-14, Mac, pipeline test (not an experiment)

`agent/benchmark run polybench/seidel-2d --arms full --models haiku --verify-size STANDARD --threads 8`
— agent `4927898c` + uncommitted (Fix 51), harness `4d7e3ce` + uncommitted.

- Pipeline worked end to end: profile via `discopop_cc` (1.8 s + 0.9 s + 14.8 s explorer,
  7 `do_all`), agent 925 s with 22 LLM calls, verification 4 s. Harness outcome `FASTER`,
  2.91× at 8 threads; agent's own verdict `BELOW` (4 pragmas vs a DiscoPoP baseline of 7 —
  the baseline counts init/print loops).
- **Unsafe acceptance that every check missed.** The model replaced the kernel's
  Gauss-Seidel sweep (in-place; reads neighbours updated in the same sweep) with a Jacobi
  sweep (reads the old array into `temp`, copies back) — a different algorithm. The agent's
  correctness stage, schedule stress, Settle, and the harness's exact dump (SMALL) and
  digest (STANDARD) all passed it.
- **Cause: PolyBench's input is a fixed point of both algorithms.** `init_array` sets
  `A[i][j] = (i*(j+2)+2)/n`, a bilinear field; the 9-point mean of a bilinear field equals its
  centre value exactly, so both sweeps leave `A` unchanged. Re-check outside the harness:
  full dumps identical at MINI and SMALL; at STANDARD they differ (line 80) only by
  floating-point round-off at a printed-rounding boundary, which the digest's sums absorb.
- **Consequence:** output equivalence on the shipped input cannot detect an algorithm change
  here. Not a harness bug in the narrow sense — an **oracle-adequacy** limit, and direct
  evidence for C2 (the gate is only as strong as its inputs). Keep this trial as the first
  entry of the X5 gate regression corpus.
- **Fix, implemented and verified the same day** (generator v3, §2; runner, §3): packaged
  kernels take an optional seed in `argv[1]` that perturbs every array after `init_array`;
  the runner passes `--check-input 7` to the agent and adds seeded checks to verification.
  Replay without an LLM — the smoke run's Jacobi rewrite applied to the v3 file, run through
  the harness's `verify()` at STANDARD, 8 threads:

  | Final source | Seed | `dump_exact_seeded` | `digest_seeded_rel_err` | Outcome |
  |---|---|---|---|---|
  | Jacobi rewrite | none | — | — | `FASTER` (the blind spot) |
  | Jacobi rewrite | 7 | **False** | **3.8e-7** | **`BROKEN`** |
  | unchanged copy (control) | 7 | True | 0.0 | `no-change` |

  The agent's own gate has not yet been re-run with `--check-input 7` on this kernel.
- **Agent design issue observed (not fixed yet): the agent's success metric.** The agent
  printed `BELOW` (4 pragmas vs a "DiscoPoP unaided" baseline of 7) for a run the harness
  measured at 2.9×. The baseline counts every DiscoPoP pattern whose pragma passes the clause
  check and compiles — here mostly `init_array` and `print_array` loops, two of which then
  raced under TSan in Phase B. Counting pragmas rewards annotating cold or output loops and
  says nothing about time saved. Candidate fix: judge the run by measured time saved (the
  impact model already exists) rather than a pragma count. Deferred until more runs show
  how often the two disagree.
