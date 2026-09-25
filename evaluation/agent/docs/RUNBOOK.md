# Runbook — running the thesis experiments

Written for: whoever runs the campaign next — the author alone at a terminal, or a fresh
Claude session with no memory of how any of this was built. It assumes nothing except the two
repositories and SSH access to the server.

Read this file first. Then, only if you need the reasoning behind a decision:

| File | What it holds |
|---|---|
| `agent/docs/THESIS_EXPERIMENTS.md` | the thesis record: every decision, why it was made, the change log, and the run log with measured results |
| `agent/docs/EXPERIMENT_PLAN.html` | the pre-registered plan: hypotheses, arms, benchmark groups, experiments E1–E11, budget ([published copy](https://claude.ai/code/artifact/a981e32c-feb1-4d45-928b-1483117858dc)) |
| `agent/README.md` | how-to for the harness commands, in more detail than here |
| `discopop_agent/docs/FIXES.md` | every agent change, numbered, with how it was verified |

---

## 1. The setup in one picture

- **One repository** (since 2026-09-20), on the Mac and on the server: `~/discopop_agent` — the
  agent and DiscoPoP, with this harness in `~/discopop_agent/evaluation/` (`agent/`, `shared/`,
  `benchmarks/`). One commit identifies an experiment's whole state. Until 19 Sep the harness
  was the `agent-experiments` branch of the group's `new_benchmark_harness` (frozen there, tag
  `moved-to-discopop_agent`); every path in this document is relative to `evaluation/`.
- **The Mac is where code is edited.** The server is where experiments run.
  Code is never edited on the server: it is synced from the Mac, and every launch first
  proves the two are identical.
- **Server:** the group's shared server — its address and account are kept OUT of this public
  repository, in the untracked `agent/tools/server.local` (`DP_SERVER=user@host`,
  `DP_SERVER_KEY=~/.ssh/<key>`); 2 × AMD EPYC 9255
  (48 cores, NUMA node 0 = CPUs 0–23, node 1 = 24–47), 755 GB RAM, LLVM 20.
  It is **shared** — other users run jobs on it, so timing runs are pinned to one NUMA node
  and every trial records the host load.
- **The agent runs from the checkout**, not from an installed copy: the harness sets
  `PYTHONPATH` to the agent repo and calls `<agent>/venv/bin/python -m discopop_agent`.

## 2. Before anything else

```bash
cd ~/discopop_agent/evaluation
agent/tools/server.sh parity          # must end with PARITY OK
```

`PARITY OK` means: both repos at the same commit, both working trees clean, the DiscoPoP
wrapper scripts identical, `discopop_explorer`/`discopop_library` imported from the checkout
on both machines, and the same `anthropic` / `claude-agent-sdk` versions. **A run refuses to
start unless this passes** — a result that cannot be traced to a commit is not worth the
model calls. If it fails:

| Row says | Do this |
|---|---|
| `harness_head DIFFER` | `agent/tools/server.sh sync` |
| `agent_head DIFFER` | commit **and push** the agent, then `sync` (the server pulls the agent from GitHub) |
| `harness_tree dirty` | commit the harness; or, for a pilot only, add `--allow-dirty-harness` (the run manifest still records the exact diff hash) |
| `wrappers DIFFER` | `sync` reinstalls them; if it persists, copy `profiler/scripts/*_wrapper.sh` and `hotspot_detection/scripts/*_wrapper.sh` into the venv's `.libs` directories |
| `explorer`/`library` not `checkout` | on the server: `cd ~/discopop_agent && venv/bin/pip install --no-deps -e ./explorer -e ./library -e ./GUI` |

**The token** (needed only for runs that call a model):

```bash
claude setup-token                                                      # prints a token
security add-generic-password -U -a "$USER" -s claude-code-oauth-token -w   # paste it twice
```

**The `-U` is not optional.** Without it `security add-generic-password` *refuses* to
overwrite an existing item instead of replacing it, so a freshly minted token never reaches
storage and every tool keeps reading the old one. Worse, a second item can end up under the
same service name while `find-generic-password` only ever returns the first — which is how a
replaced token can appear replaced and still fail with 401. When replacing a token, delete
every copy first and check the value really changed:

```bash
security delete-generic-password -a "$USER" -s claude-code-oauth-token   # repeat until "could not be found"
security find-generic-password -a "$USER" -s claude-code-oauth-token | grep -E '"(cdat|mdat)"'
```

`mdat` equal to `cdat` means the item has never been updated since it was created.

**The token is longer than one terminal line, and a partial paste looks valid.** It wraps
across two lines where `claude setup-token` prints it, and copying only the visible first
line yields a value with the right `sk-ant-oat01-` prefix, no whitespace, and nothing to
mark it as incomplete — which then fails with the same `401 OAuth access token is invalid`
as a revoked token. Avoid the paste altogether: `claude setup-token` also prints an
`export` line, so store it straight from the variable (leading space keeps it out of
history), then check the length round-trips.

```bash
 security add-generic-password -U -a "$USER" -s claude-code-oauth-token -w "$CLAUDE_CODE_OAUTH_TOKEN"
security find-generic-password -a "$USER" -s claude-code-oauth-token -w | wc -c
```

It never leaves the Keychain except into a job's environment. To remove it later: delete the
Keychain item, **revoke it at <https://claude.ai/settings/claude-code>** (deleting locally does
not invalidate it), then `agent/tools/server.sh sweep`.

**A token that once worked can stop working** — revoked, expired, or superseded when the
account re-authenticates — and the failure is silent by nature: the CLI reports a rejected
credential as `is_error` with subtype `"success"` and **exit code 0**. Since 2026-09-16 the
job refuses to start on it (`== auth check` → `== ABORT`) and the agent treats it as fatal,
so it can no longer be mistaken for a result. To check by hand before a long campaign:

```bash
agent/tools/server.sh run --node 1 -- --help    # aborts at the auth check if the token is dead
```

## 3. The commands you will actually use

```bash
agent/tools/server.sh sync                      # Mac -> server, then parity
agent/tools/server.sh run --node 1 -- ARGS      # launch a run on the server, detached
agent/tools/server.sh status [LINES]            # running jobs + tail of the launcher log
agent/tools/server.sh fetch [RUN_ID...]         # copy results back AND archive them into agent/results/
agent/tools/server.sh sweep                     # confirm no credential is left on the server
```

Everything after `--` goes to `agent/benchmark run`. Locally, the same harness runs directly:

```bash
agent/benchmark list-benchmarks        # 37: 30 PolyBench kernels + 7 applications
agent/benchmark list-arms              # the arms and the flags each one adds
agent/benchmark list-runs              # runs and their status
agent/benchmark run BENCH... --arms A,B --models M --trials N --run-id NAME
agent/benchmark verify-source BENCH --label L [--source FILE] [--final-flags "..."]
agent/benchmark plots [--runs a,b --name NAME]
agent/benchmark report [--run RUN_ID]
agent/benchmark rescore RUN_ID         # re-apply the scaffolding check and outcome rules to a finished run
agent/benchmark archive RUN_ID... | --all   # copy runs into the tracked agent/results/ (then commit)
```

**A run is resumable.** Re-running with the same `--run-id` skips trials that already have a
`trial.json` and continues. Ctrl-C is safe: the report covers what finished.

**Where things land:** `agent/runs/<run_id>/` — `benchmarks/<bench>/<arm>/<model>/rep<N>/trial.json`
(one record per trial, including the agent's log and every candidate patch), `profiles/`
(the DiscoPoP profile each benchmark used), `figures/`, `tables/`, `overview.md`, and
`manifest.json` (commits, tool versions, host, every setting). Launcher logs for server jobs:
`agent/runs/_launcher/<timestamp>.log`, ending in `SWEEP:` lines.

## 4. Running an experiment

The plan defines E1–E11. The pattern is always the same: pick benchmarks, pick arms, pick a
model, give it a run id.

```bash
# E1 — the whole system, core set, 5 repeats (the list below predates D12/D13/D15: use the eight of §5)
agent/tools/server.sh run --node 1 -- polybench/2mm polybench/jacobi-2d-imper \
    polybench/floyd-warshall polybench/seidel-2d polybench/trisolv polybench/lu \
    rodinia-3.1/hotspot rodinia-3.1/nw npb/mg burkardt/md \
    --arms discopop_gate,full --models claude-haiku-4-5-20251001 \
    --trials 5 --threads 1,2,4,8,12 --repeats 5 --run-id e1_core

# E1-bare — the same model with no DiscoPoP and no gate, on TSVC class R (the 18 loops of
# benchmark_classes.json); its `default` counterpart is E1's own trials. Two lanes, 9 loops each.
agent/tools/server.sh run --node 0 -- tsvc/s112 tsvc/s121 tsvc/s1213 tsvc/s127 tsvc/s211 \
    tsvc/s212 tsvc/s241 tsvc/s243 tsvc/s244 --arms bare_llm --models claude-haiku-4-5-20251001 \
    --trials 5 --threads 6,12 --repeats 5 --run-id e1_bare_a
agent/tools/server.sh run --node 1 -- tsvc/s252 tsvc/s254 tsvc/s255 tsvc/s281 tsvc/s291 \
    tsvc/s292 tsvc/s293 tsvc/s331 tsvc/s341 --arms bare_llm --models claude-haiku-4-5-20251001 \
    --trials 5 --threads 6,12 --repeats 5 --run-id e1_bare_b

# E2 — evidence x model (one attempt per region, so feedback cannot substitute for evidence). Its
# `default`, `bare_llm` and `discopop_gate` cells are E1c's (same loops, same agent commit — D38 row);
# its own runs add the evidence arms, their twins (D38, in the SAME runs, so twin and agent read the
# same profile) and `twin_dp` (DiscoPoP unchecked, no model — compared with E1c's `discopop_gate`
# per benchmark over independent profile draws). Four lanes, the E1c split.
... --arms full_b1,no_evidence,no_evidence_b1,twin_full,twin_no_evidence,twin_dp \
    --models claude-haiku-4-5-20251001 --trials 5 --threads 6,12 --repeats 5 --run-id e2_ab_...

# E10 — the speed check (needs a timing size per kernel, see §6)
... --arms full,speed_gate_large,speed_gate_small --models claude-haiku-4-5-20251001 --trials 3 --run-id e10

# Baselines — no model, no agent
agent/benchmark verify-source polybench/2mm --label polly \
    --final-flags "-mllvm -polly -mllvm -polly-parallel -mllvm -polly-process-unprofitable" \
    --cc /usr/lib/llvm-20/bin/clang --threads 24 --run-id e1_baselines
agent/benchmark verify-source npb/is --label expert_openmp --source /path/to/is_ori.c --run-id e1_baselines
```

Always name the model in full (`claude-haiku-4-5-20251001`, `claude-sonnet-5`); an alias can
move to a different model mid-campaign and the comparison would be meaningless.

### After every experiment: fetch, archive, commit

```bash
agent/tools/server.sh fetch e1_core                       # copies the run back and archives it
agent/tools/campaign.py check                            # the definition of done (below)
git add agent/results && git commit -m "results: e1_core (E1)" && git push
```

`agent/results/<EXPERIMENT>/runs/<run_id>/` is tracked in git and holds everything the thesis will cite —
`figures/trials.csv` (one row per trial), `gate_failures.csv`, the figures, every trial's
record, log, diff and candidate patches, and the program every trial started from — with a
sha256 per file in `ARCHIVE.json`. `agent/results/README.md` is the map, `INDEX.md` lists the
runs by experiment, `EXHIBITS.md` the case studies, and each experiment folder has a `REPORT.md`. Only the DiscoPoP profile trees,
scratch copies and binaries stay behind in `agent/runs/`. A run archived again replaces its
directory (git history keeps the earlier state) — archive again after a resume or a rescore.

### The benchmarks cannot be corrupted between trials

Every trial starts from the run's archived copy of the package (`profiles/<bench>/`) and works
in its own fresh `work/` copy; nothing is ever run in `agent/prepared/`. The runner proves it
rather than assuming it (`check_package` in `cli.py`, tested by `tools/test_integrity.py`):

- **at run start** the package is compared with the digest its packager wrote into
  `meta.json` (`output_sha256`; `prepare_*.py` compute it over the generated sources);
- **before every trial** the same, plus the archived sources against the package and the
  archived DiscoPoP profile tree against `profile_sha256` recorded in `profile.json` when it
  was taken;
- **after every trial** the same again, so the NEXT trial's starting point is proven intact.

Every trial records the two checks (`trial.json` → `package_integrity.before/after`). A
difference stops the run (status `aborted_package_corrupted`, exit status 2 — an unattended
sweep stops with it) with a message naming what changed; the trial that ran last keeps its
record because it ran on a copy proven intact beforehand. A modified package is never run:
regenerate it with the prepare tool. If the archived copy differs, delete
`agent/runs/<run>/profiles/<bench>/` and the run re-profiles from the package.

### The checklist for EVERY experiment (a new session starts here)

**Changing the agent between experiments (D34, the author, 23 Sep).** Allowed, and every change is
documented: (a) it comes from a recorded finding; (b) it is replayed on archived trials before it is
merged (the Fix-90 lesson); (c) every run stamps the agent version it used (`manifest.json` →
`invocation.agent_git.head`, `dirty_sha256`); (d) the thesis tells the sequence — found, measured,
fixed. **Earlier experiments are not rerun:** each experiment runs once on its stamped agent and its
arms are compared inside it; a later change is evaluated on earlier experiments by replaying the
CHANGED stage on their archived candidates (deterministic, no model — `marginal_replay.py`,
`clause_replay.py`, `race_check.py`, then `verify-source` on the rebuilt programs), and only what that
cannot answer is rerun. The model's own answers are never replayed. Agent v2 (Fixes 91–94, `ad57f134`)
was introduced this way; E1 under v2 is `results/E01b_bare_llm/checks/e1b_v2_verify`.

**Before launching**
0e. **An experiment's arms differ in EXACTLY its variable — machine-checked.** `arms.json` has an
   `experiments` block: each experiment names its arms, its variable (resolved agent settings)
   and what may differ only as a consequence. Run `venv/bin/python evaluation/agent/tools/test_arms.py`
   after ANY change to an agent default, a common flag or an arm, and before every launch: it
   resolves all arms through the agent's own parser on a timeable and an untimeable kernel and
   fails on a confound, on a variable that does not vary, and on a stale declaration. It is what
   found E2's pinned `--fast-refresh` (21 Sep) after the prose claim "verified" had missed it.
   A new experiment gets its block BEFORE its first run.
   **What actually happened is recorded per trial, not assumed from the arm:** `refresh_fast` /
   `refresh_full` / `refresh_fallback` (a fast refresh that fell back to a full re-profile —
   the trial did not get its arm's treatment; E3 reports the rate and analyses both ways),
   `runtime_remeasurements`, `explorer_stalls` (a random explorer stall, killed at 600 s and
   the draw repeated), `speed_check_off`. Read them in `trials.csv` before believing a contrast.
0d. **Arguments that depend on other arguments (D28).** The agent REFUSES a combination that
   cannot work — `--llm-recon` and `--llm-deps` each need `--fast-refresh`; `--pragma-arbitration`
   needs both `--llm-pragmas` and `--require-speedup`; `--llm-recon` with `--llm-deps` is a
   contradiction — so those cannot reach a run. The dangerous kind is the one that raises no
   error: a setting another setting makes INERT. Every run prints them before it starts; read
   that list and check it against the experiment's variable. Known: `--no-hotspots` makes
   `--min-runtime-share` and `--min-impact` inert (E9's `full_no_hotspots` varies both together,
   and its write-up must say so); `--restructure-depth > 0` with `--fast-refresh` refreshes only
   at the last level; `--no-require-speedup` with a per-kernel timing size. The agent's default
   is a FULL re-profile after a kept rewrite (`--no-fast-refresh`, D27).
0c. **Scope (D26): exclude what DiscoPoP cannot profile, keep what it profiles but finds nothing
   in.** A benchmark whose profile cannot be produced within the phase timeout leaves the
   model-driven set, is measured once, and is reported with its cost. A benchmark DiscoPoP
   profiles happily while reporting no applicable pattern is class R — the thesis's whole point —
   and is never excluded. Do not conflate the two.
0b. **Every argument of every arm is declared and verified (D24).** Each arm in `arms.json`
   carries a `settings` block naming the arguments that carry its purpose; the harness checks
   them against `discopop_agent --print-config` before a run starts and REFUSES to run on any
   difference, including a missing declaration. Adding an arm therefore means adding its
   `settings`. Every run also prints the settings its arms differ on — that list must contain
   exactly the experiment's variable and nothing else. The agent's default is
   `--no-llm-pragmas` (D23): the model restructures, DiscoPoP annotates. An experiment that
   wants the model to write the pragmas says so in its arm.
0f. **No answer in what the model reads (D36), and nothing but its workspace within reach (Fix 95).** Until 23 Sep every
   TSVC source opened with its solving transformation (`class: restructure   transformation: …`), read by the model in
   every arm. `tools/test_integrity.py` §1b now fails on any class/transformation label in an experiment package
   source and on transformation vocabulary in a TSVC source; a packager keeps such labels in `meta.json` only, which
   never enters the workspace. The model's file tools are confined to its workspace by a PreToolUse hook (feature
   check `workspace-confined`); shell, web and search tools are blocked. **The model alone (`bare_llm`) runs with
   the MIRROR prompt (D37 revised)**: the agent's own instructions minus DiscoPoP, minus the gate during the run,
   minus feedback — one attempt, judged afterwards exactly as the agent's final program; `bare_llm_minimal` and
   `bare_llm_contract` reproduce the two earlier prompts.
0a. **The main comparison is THREE-WAY: DiscoPoP alone · DiscoPoP + agent · the model alone (D19 +
   D35, the author's rules); the sequential original is the reference column, never the result.** Every
   model-driven run includes `discopop_gate` on the same benchmarks (`--arms discopop_gate,<arms>`), and
   every experiment has a model-alone reference (`bare_llm`) on the same benchmarks with the same
   model: TSVC class R with Haiku is E1-bare's 90 trials (the bare arm never runs the agent, so an agent
   change does not touch it); a new model (Sonnet) or a new benchmark set (LULESH, NPB-C, a harder tier)
   needs its own `bare_llm` run, registered with the experiment. The read-out: (1) the three arms against
   the sequential reference — verified parallel, FASTER, race-free FASTER (`race_check.py` over the bare
   arm's parallel programs is a standard step), BROKEN, slower-shipped; (2) agent vs DiscoPoP alone —
   `vs_discopop_alone.md` (gained · better · equal · worse · lost · neither · unsafe); (3) agent vs model
   alone — per-benchmark FASTER counts paired (Wilcoxon), and **unusable programs (BROKEN, racy, slower)
   paired per benchmark as H13 — every one a model-only arm ships is a RESULT (the pipeline's trust
   advantage), listed by case, never dropped** (`main_comparison_stats.py --three-way … --bare <arm>`). The model alone's
   speed is over its correct trials only and is never set against the agent's all-trials median. A run
   whose overview says MISSING is not reported.
0b. **Every experiment with a model-only meaning carries its MATCHED TWINS (D38), in the same run as
   the agent arms they are twins of.** A twin (`"runner": "twin"`, `discopop_agent/twin.py`) is its
   agent arm minus the gate: the same arguments, region, evidence and request, one attempt per region,
   no feedback, DiscoPoP's pragmas inserted at the end with nothing checked. Which twins go with which
   experiment is in arms.json (`E2-twins`, `E2-source-twins`, `E3-twins`, `E8-twins`, `E9-twins`;
   `twin_dp` beside `discopop_gate` wherever it runs — no model cost). `race_check.py` over EVERY twin
   arm's programs is part of the read-out, as for `bare_llm`; `twin_model_program.*` in each trial's
   `agent_patches/` is the program before DiscoPoP's unchecked pragmas. The read-out's headline is the
   pipeline × factor interaction (agent difference vs twin difference, paired per benchmark), pre-
   registered in the plan before the run; the model + gate FILTER (the twins' programs through the gate's
   race stages and the harness verification) is computed afterwards at no model cost.
0. **Suitability pre-flight (D18, thesis record §5k) — no model.** The experiment's benchmarks
   must be able to tell its arms apart: class measured (`discopop_gate` × 3 profiles: R =
   DiscoPoP alone fails and a verified reference exists, A = DiscoPoP alone succeeds, D = true
   recurrence); for class R the reference solution verified and its speedup at the
   verification size known (`tsvc_ceiling.py`, T0.10); sizes from T0.1; then ONE smoke trial
   per arm on two benchmarks and READ the logs — did the arm's code path run (a rewrite, a
   refresh, depth 1)? An experiment whose arms cannot differ on its benchmarks is not run.
   **"The code path ran" is not enough — follow it to the end (the Fix 86 lesson).** Smoke 3
   accepted a correct, gate-passing rewrite in both trials and still reported `no-change` in
   both, because the loops the rewrite exposed were filtered out before Phase B could annotate
   them and Settle then discarded the rewrite as an orphan. So for every accepted rewrite,
   check the log in order: DiscoPoP reports a pattern in the rewritten lines → **that region
   appears in Phase B's candidate list** → the pragma reaches a gate verdict. A `DROPPED` with
   a named reason (tsan, slower) is a real result; a region that never appears at all is a bug.
1. The experiment, its arms, benchmarks, repeats and hypotheses are in the plan; any deviation
   is written into `THESIS_EXPERIMENTS.md` §6 (change log) with its reason **before the first
   trial exists**.
1b. **Register the run ids in `agent/results/campaign.json` BEFORE launching** — group (the
   experiment; add the group with its folder name and question if it is new), section (`runs`,
   `preflight`, `checks`), a one-line role, status `running`. The archive puts the run where
   the registry says; an unregistered run lands in `results/_unregistered/` and the check fails.
2. Both repos committed and pushed; `agent/tools/server.sh sync` → `PARITY OK`. If `profiler/`
   changed: rebuilt on Mac and server (§5). Never touch the server's agent checkout while a
   run is in progress.
3. **Tell the author before launching a real experiment** (pilots and no-model studies do not
   need it). Model runs spend the author's subscription.
4. Launch: `agent/tools/server.sh run --node N -- <benchmarks> --arms ... --models <FULL id>
   --trials R --threads 6,12 --repeats 5 --run-id <id>`. One job per lane: `--node N` is a whole NUMA
   node (24 cores); `--node N.H` is half H of it (12 cores, node N's memory) — four lanes, used once T0.4 at
   four lanes (`t0_4_four_lanes`) shows the timing still resolves 1.1× (the author, 23 Sep). The agent's explorer
   limit is set per benchmark by the harness (max 60 s, 10 × its own explorer run).

**While it runs** — `server.sh status`; outcomes appear as `→ OUTCOME` lines in
`agent/runs/_launcher/<stamp>.log`. `aborted_package_corrupted` or a `SWEEP: TOKEN FOUND`
line stops everything until understood.

**After it ends — the definition of done. An experiment is DONE when `agent/tools/campaign.py
check` prints `OK`, and not before.** The check fails on anything below that a program can see;
the rest is on this list because a program cannot.
1. `agent/tools/server.sh fetch <run_id>` — copies the run back and archives it into its
   experiment's folder, `agent/results/<EXPERIMENT>/runs/<run_id>/`; check the launcher log
   ends with `SWEEP: clean`. In `campaign.json` set the run's status from `running` to `valid`.
2. `agent/benchmark rescore <run_id>` if an outcome rule changed since it started; then
   `agent/benchmark archive <run_id>` again.
3. **Read out** — `agent/benchmark plots --runs <ids> --name <exp>` and, for the primary set,
   `--suite tsvc --name <exp>_tsvc`; `agent/tools/main_comparison_stats.py <ids> [--suite tsvc]`.
   Copy the read-out into `agent/results/<EXPERIMENT>/analysis/` (and `analysis/tsvc/`) with a
   `README.md` naming the commands. `agent/analysis/` is scratch and git-ignored: a number that
   is not in `agent/results/` does not exist. **A read-out that combines arms** (E1-bare beside
   E1's `default`): run `main_comparison_stats.py` once per `--arm` — without it the tool, and
   the `main_comparison_stats.md` that `plots` writes, POOL every non-baseline arm into one
   meaningless figure; do not copy the pooled file. Read every BROKEN / invalid trial by name and
   cause, and the diffs of the surprising trials — numbers alone have hidden every important
   finding so far.
4. **Record** in `THESIS_EXPERIMENTS.md`: a §7 run-log entry per run group (what ran, when,
   where, on which commits, the table, the reading, the deviations FIRST, what it changes), a
   §6 change-log row for every decision or rule change, §5e status for an instrument. Every
   run id must appear in the record by its full name (the check looks).
5. **Exhibits** — `agent/tools/thesis_material.py <run>:<suite>/<kernel>/<arm>[@<rep>]:<label>`
   for the best, the worst, every BROKEN trial and every finding; they land in
   `agent/results/<EXPERIMENT>/exhibits/`. Register each in `campaign.json` → `exhibits` with
   the one sentence it supports ("shows"). Look at one picture before relying on it.
6. **Report** — `headline` of the experiment in `campaign.json` (one paragraph, the result
   against DiscoPoP alone), status `done`, then `agent/tools/campaign.py reports`: writes the
   experiment's `REPORT.md`, `results/INDEX.md` and `results/EXHIBITS.md`.
7. **Plan artifact** — `agent/docs/EXPERIMENT_PLAN.html` (status, results, decisions, version line)
   republished to https://claude.ai/artifact/Mw2YU7Y8wb4oNpuW9ikncK; the pipeline page
   (https://claude.ai/artifact/FNsRJjnicDw7gBB6mXgKbQ, `agent/docs/FLOW.html`) when the flow changed.
8. A bug in DiscoPoP itself → fix at the root, entry in the agent's `docs/FIXES.md` AND
   `docs/DISCOPOP_BUG_REPORTS.md`, fixed DiscoPoP in every arm, affected instruments re-run.
9. `agent/tools/campaign.py check` → `OK`; commit and push; update the session memory
   (what ran, what it found, what is running, what is next).

**Handover.** A new session, or a reader, starts at `agent/results/README.md` (the map),
`agent/results/INDEX.md` (every run by experiment, with purpose and status), each experiment's
`REPORT.md`, and this checklist; `campaign.py check` says whether anything is unfinished.

## 5. What is already done — do not redo it

| Item | State |
|---|---|
| 37 benchmarks packaged and validated | 30 PolyBench kernels + `md`, `pathfinder`, `nw`, `hotspot`, `is`, `mg`, `lu` — **since 18 Sep in their original file layout (D6)**: regenerate with `python3 agent/tools/prepare_polybench.py --out agent/prepared/polybench --validate` and `python3 agent/tools/prepare_apps.py --out agent/prepared --validate --cxx clang++-20` (on the Mac `--cxx /usr/local/Cellar/llvm@19/19.1.7/bin/clang++`). `prepared/` is git-ignored: regenerate on every machine. The merged one-file packages exist only for the packaging study: `--layout single --out agent/prepared_single/...` |
| **T0.1** sizes for the kernels | `agent/config/kernel_sizes.json` — verification size (serial kernel ≥ 1 s) and timing size (≥ 0.25 s) |
| **T0.2** DiscoPoP stability | run `t0_2_stability`; the finding is in §5b of the thesis record |
| Verify-only baselines | `verify-source`; first result: Polly on 2mm, 35.2× at 24 threads |
| Agent fixes 51–57 | C support, kernel timing, candidate/token logging, targeting, `--timing-cflags`, macOS `omp.h`, mypy 82 → 0 |
| Token, parity, server setup | done |

**T0.1 sizes: done for all 34 benchmarks** (run `t0_1_apps`, merged into
`agent/config/kernel_sizes.json`; `cholesky`, `durbin` and `trmm` are excluded weak oracles and stay
out). Keys are **full names** (`npb/lu`, `polybench/lu`) — bare names collide and silently gave
one benchmark another's sizes. Eleven benchmarks have no verification size and are
correctness-only.

**Re-run owed by the packaging change (D6, 18 Sep):** T0.1 (`size_table.py`), T0.2
(`profile_stability.py`), T0.5 (`share_study.py`) and T0.6 (`dp_main_study.py`) were taken on
the merged packages and are re-run on the original-format ones; T0.8
(`packaging_equivalence.py --single agent/prepared_single/polybench --project
agent/prepared/polybench --out agent/runs/t0_8_packaging`) says whether DiscoPoP saw the same
program (Mac: yes, on every kernel checked). A project benchmark is profiled through a
generated unity unit — see the agent's `docs/MULTIFILE.md` for why unit-by-unit profiling is
unsafe — and the unity unit must be compiled by its ABSOLUTE path (Fix 78).

**Where the campaign stands (19 Sep 2026)** — details in the thesis record §7 and the plan:

1. **Instruments T0.1–T0.9: done** on the original-format packages; T0.2/T0.6/T0.7/T0.8 are
   re-run on the FIXED DiscoPoP (`DP_T0_STEPS="T0.7 T0.2 T0.6 T0.8" DP_T0_TAG=_fix agent/tools/t0_chain.sh`).
2. **Pilot: done** (`pilot4`, fixed DiscoPoP): E1 runs with **Haiku** (D9). `pilot3` is superseded.
3. **E10 runs first** (D8; run `e10`), then E1, E11, E2 (with the 19 Sep amendments: evidence-source
   arms, grouped Part C, prompt ablation Part D), then the rest in the plan's order.
4. **Model-driven core set = eight**: 2mm, hotspot · jacobi-2d-imper, floyd-warshall, md ·
   seidel-2d, trisolv, polybench/lu. NPB `lu`, `mg` and Rodinia `nw` are DiscoPoP limits
   (agent `docs/DISCOPOP_BUG_REPORTS.md` L1–L3; `mg`/`nw` to be re-measured after Fix 83).
5. **Ask the author before starting any real experiment.** After every run: `server.sh fetch`
   → commit `agent/results`.

**DiscoPoP itself is fixed where it is broken** (author's rule, 18 Sep): fixes 78, 80–83 are in
the agent repository; every one is logged for upstream in `docs/DISCOPOP_BUG_REPORTS.md`. A
change under `profiler/` needs a rebuild on EVERY machine — `server.sh sync` does not do it:

```bash
# Mac
venv/bin/pip install ./profiler --config-settings="cmake.args=-DLLVM_DIST_PATH=/usr/local/opt/llvm@19"
# server
cd ~/discopop_agent && venv/bin/pip install ./profiler --config-settings="cmake.args=-DLLVM_DIST_PATH=/usr/lib/llvm-20"
~/discopop_agent/evaluation/agent/tools/job.sh install-wrappers                 # re-installs the wrappers
```

Never update the server's agent checkout while an experiment is running: the agent and the
explorer run from that checkout, so the run's conditions would change between trials.

## 6. Traps — every one of these cost hours to find

* **The measurement harness stays in the benchmark's file (D39, 25 Sep).** `prepare_tsvc.py --layout v4`
  (the harness in a header outside the package, found through CPATH) is built and kept, but NOT for
  experiments: with a program spanning two files DiscoPoP's explorer reports a true recurrence
  (`s211`) as Do-All in every draw (bug report B8). Regenerate packages only with the default layout;
  it reproduces the packages in use byte for byte. A harness edit by any arm is its own row, never
  a failure (H13); the agent's gate refuses it for packages that list protected lines (Fix 97).

- **A rewrite can be 3–30× slower than the original and pass every gate before Settle.**
  Phase A judges a pragma-free rewrite on output; Phase B measures each pragma against the
  state before it. Only Settle compares with the original. In E1 a `malloc` + `memcpy` per
  repetition (TSVC) and a 30× slower `is` rewrite reached Phase B with their pragmas accepted;
  the TSVC ones were dropped at Settle, the `is` ones ran the 90-minute limit out. When a
  trial is slow or ends `no-change` after `Quality gate PASSED`, read the `Re-measured
  runtimes: … total` lines and the SETTLING block before suspecting the host. D31 (a bound in
  Phase A) is the author's open decision.
- **Replay any change to what reaches the model on archived trials BEFORE merging it.** Fix 90
  ("skip a region whose loops all carry a DiscoPoP pattern") looked obviously right for class A
  and, replayed on E1's own logs, would have blocked the model on 11 of 18 class-R loops —
  including every 5-of-5 winner — because in class R DiscoPoP reports patterns the gate then
  rejects. A rule on DiscoPoP's patterns cannot tell a false positive from a true one; only the
  gate can. Every trial's `agent.log` has the initial candidate table (tier per region) and the
  region each model call was made on: that is enough to replay a routing rule without a model.
- **Do not diagnose a speed verdict from the agent's log alone.** Settle's "slower than the
  original: 4061 ms vs 1115 ms" looked like host interference; rebuilt from the archived
  patches and judged by the harness, the program WAS 3× slower. Every candidate the agent
  judged is in `agent_patches/candidates/` with its verdict in `candidates.jsonl`: rebuild it
  (`patch -p0 -F0` in order) and run `verify-source` before calling a verdict wrong. On the
  server that takes 10–15 min per kernel at EXTRALARGE.
- **A package's dump may hold RESULTS only — never a diagnostic that subtracts equal numbers.**
  LULESH prints three symmetry differences; on the symmetric input they are rounding residue
  (2e-11 against energies of 3e+5) and a correct parallel version moves them by 25 %. The
  package emitted them, so the harness called LLNL's own OpenMP release `BROKEN` while every
  energy agreed to 2e-16 — and the agent's gate, which reads the digest, would have accepted
  the same program: `unsafe` for both arms on the campaign's one application. **Before a
  benchmark is used, run its expert version through `verify-source` (T0.14); `BROKEN` there is
  a defect of the package until shown otherwise.**
- **Four threads cannot see a schedule-dependent result.** Rodinia's own `hotspot` pragma
  passes every check on the Mac and fails at 24 threads under a dynamic schedule. A correctness
  verdict taken on the Mac is provisional; repeat it on the server at 6 / 12 / 24 threads
  before citing it.
- **The Mac has 8 GB. DiscoPoP-profiling an application on it (NPB, Rodinia, LULESH) — or
  leaving two jobs in the background — swaps until the disk is full** (21 Sep: 1.7 GiB left).
  Those jobs go to the server, in a scratch directory outside the campaign's checkout while an
  experiment runs. On the Mac: TSVC and small PolyBench kernels, tests, `verify-source`, one
  job at a time; check `df -h /System/Volumes/Data` first.
- **`SCAFFOLD_MODIFIED` is not a result.** A trial whose final source changed the packaging's
  own code (timer calls or their position, `PB_PERTURB`, the digest) gets this outcome and is
  never counted. The check is `agent/tools/scaffold.py`; `pilot2` is the example.
- **DiscoPoP's explorer crashes at random on some programs** (`pathfinder`: 15 of 20 runs on
  one profile, `IndexError` in `TaskGraph.recursive_assignment`) and its task patterns change
  from run to run on one profile. The harness and the agent retry it on the same profile, up
  to 20 times; retries appear as `explore_attempts` (profile) and `explorer_retries`
  (trial). A benchmark whose profile shows `explore failed on all 20 attempts` has no result
  for that run: re-run it, and do not replace the profile with a different one mid-run.
- **C++ function names are mangled in DiscoPoP's data.** `--exclude-functions` works on
  C++ only since agent Fix 59. An application run on an older agent excluded nothing.
- **Instrument studies** (no model): `share_study.py` (T0.5, runtime share per region),
  `dp_main_study.py` (T0.6, DiscoPoP's suggestions in `main`). Method and results:
  `THESIS_EXPERIMENTS.md` §5e and §7.
- **The scaffolding check has its own tests**: `python3 agent/tools/test_scaffold.py` (26 cases,
  exit 1 on failure). Run it after touching `scaffold.py` — two bugs in that check were found
  this way, one too lax (a timer moved inside a computation window) and one too strict (the
  model inlining the kernel into the timed region).
- **NPB `lu` cannot be profiled on the Mac**: DiscoPoP's instrumenting compile did not finish
  within an hour. Profile it on the server, and never assume a local failure means the
  benchmark is broken.

- **A dashed flag value needs `=`.** `--final-flags=-funroll-loops`, not
  `--final-flags "-funroll-loops"` (argparse reads a lone dashed word as an option). A quoted
  string containing spaces is fine as-is.
- **Per-kernel sizes are mandatory.** Benchmarks missing from `kernel_sizes.json` abort the
  run before it starts. Pass an explicit `--verify-size` only to override deliberately.
- **Eight kernels are too short to time at any size that runs** (atax, bicg, gemver, gesummv,
  jacobi-1d-imper, mvt, reg_detect, trisolv). They count for correctness and are excluded from
  every speed statistic; their outcome is `parallel-speed-not-measurable`.
- **The agent's speed check is off in every arm** (`--no-require-speedup` in `arms.json`):
  at the agent's size kernels run 0.06–15 ms, below thread start-up, so it judged noise.
  E10 studies the check itself. Speed is judged by the harness at the verification size.
- **DiscoPoP is deterministic in what it observes, not in what it reports.** Across 60
  profiles the dependence multiset never changed, while `patterns.json` differed in every
  profile and suggestion counts moved up to 3×. Hence: one profile per benchmark per run,
  shared by all arms; archive it with the run; report `discopop_gate` counts as a range.
- **NPB cannot be perturbed.** It verifies against fixed reference values, so `is`/`mg`/`lu`
  record perturbation as *not applicable* — never as a pass.
- **Polly is not a thread-scaling result.** It tiles and vectorises too; 35.2× on 24 threads
  is a compiler baseline and must be labelled as one.
- **`list-runs` status can lag** — it comes from the run manifest, so a finished run may still
  read `running`. Trust `trial.json` files and `server.sh status`.
- **The server is shared.** Pin to one NUMA node (`--node`), and check `load` in the parity
  table before trusting a timing run.
- **A fast, cheap, tidy run is a symptom, not a success.** A trial that ends in minutes with
  zero tokens and `no-change` almost certainly made no model call at all. Check
  `llm_call_failures` in `trial.json` (0 is the only acceptable value) and grep the trial's
  `agent.log` for `LLM call failed`. This is how `pilot_seidel` was lost, and the numbers it
  produced looked entirely plausible.

## 7. When something goes wrong

| Symptom | What it means |
|---|---|
| `PARITY FAILED` | see the table in §2; the run never started, nothing was spent |
| `kernel X is not in kernel_sizes.json` | T0.1 has not covered X yet (§5, item 1) |
| a trial's `status` is `profile_error` | DiscoPoP failed on that benchmark; the agent log in the trial directory has the compiler output |
| `explore failed on all 20 attempts` | DiscoPoP's explorer crashed every time on that profile (see §6); re-run the benchmark |
| `verify_build_failed` | the rewrite did not compile at the verification size; the trial records the compiler error |
| the job vanished | `agent/runs/_launcher/*.log` on the server holds its output, ending in `SWEEP:` lines |
| you need to stop a run | `ssh` in and kill the `job.sh __job` process; the config directory is cleaned by the next `sweep` |

## 8. Standing rules

1. **Never put credentials on the server.** The token reaches a job only through its
   environment; the job deletes its config directory and sweeps for the token value when it
   ends. Never paste the token into a chat or a file.
2. **The Mac and the server hold identical code.** Edit on the Mac, `sync`, and let parity
   prove it.
3. **Document every change** in `agent/docs/THESIS_EXPERIMENTS.md` (harness and decisions) or
   `discopop_agent/docs/FIXES.md` (agent), including what was verified and how.
4. **The harness judges, not the agent.** Outcomes come from independent verification;
   the agent's own verdict is recorded but never counted.
5. **Deviations get written down, not smoothed over** — a packaging that changes data, a
   check that cannot apply, a number that flatters. The thesis record already carries several.
6. **A benchmark is in an experiment by a rule that never looks at the agent's results** (D30,
   record §5r): DiscoPoP profiles it; DiscoPoP alone reaches nothing verified; an expert
   version verifies (T0.10, T0.14); the no-model ceiling test keeps it (T0.13). The scope is
   TSVC-2, LULESH and RepoOMP's NPB-C; §5s says which instrument each still owes.
7. **Every run is archived and committed** (`server.sh fetch` → `git commit agent/results`)
   before it is quoted anywhere. A number that is not in `agent/results/` does not exist.
