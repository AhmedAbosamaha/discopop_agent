# Bug Fixes & Improvements Log

> **Note on file names.** This is a historical changelog: entries name the files as
> they were at the time. The package was reorganised on 2026-08-23 — `controller.py`
> became `run.py` plus `phases/`, and `l1_planner` / `l2_evidence` / `l3_llm` /
> `l4_validator` became `plan/` / `evidence/` / `llm/` / `gate/`. See
> DOCUMENTATION.md for the current layout.


Chronological record of all fixes applied to the `discopop_agent` layer.

---

## Fix 1 — LLM retry receives its previous failed diff (`prior_diff`)

**File:** `l3_llm.py`, `controller.py`

**Problem:**
When a Tier-2 LLM-generated patch failed validation and the budget loop retried, the next call to `call_llm()` built a completely fresh prompt with no memory of what the LLM had already attempted. The LLM had no way to know what it tried before or why it failed — it would often produce the same broken diff again.

**Fix:**
- Added `prior_diff: Optional[str] = None` parameter to `_build_prompt()` and `call_llm()`.
- When set, the prompt includes a `### Your previous attempt (FAILED)` section containing the previous diff in a code block.
- In `controller.py`, added `last_diff: str | None = None` in the budget loop; set it after each LLM call and pass it as `prior_diff=last_diff` on the next iteration.

**Effect:**
On budget retries the LLM sees exactly what it generated before and the failure diagnostic, allowing it to produce a meaningfully different restructuring rather than repeating the same mistake.

---

## Fix 2 — CXX_wrapper.sh: symlink-safe LLVM prefix detection

**File:** `venv/lib/python3.9/site-packages/discopop-profiler.libs/CXX_wrapper.sh`

**Problem:**
On macOS with Homebrew, `which clang++-19` returns a symlink path (e.g. `/usr/local/bin/clang++-19`). The wrapper computed the LLVM prefix by calling `dirname` twice on this path, yielding `/usr/local` instead of the real Cellar path `/usr/local/opt/llvm@19`. As a result, the wrapper looked for `libc++` in `/usr/local/lib/c++/` which does not exist, causing a linker error:

```
ld: library 'c++' not found
```

**Fix:**
Applied `readlink -f` before computing the prefix:
```bash
_LLVM_BIN=$(dirname "$(readlink -f "$LLVM_CLANGPP" 2>/dev/null || echo "$LLVM_CLANGPP")")
```

**Effect:**
`readlink -f` resolves the symlink to the real binary path before `dirname` is called, so the LLVM prefix is computed correctly and `libc++` is found.

---

## Fix 3 — CXX_wrapper.sh: auto-set `DP_PROJECT_ROOT_DIR`

**File:** `venv/lib/python3.9/site-packages/discopop-profiler.libs/CXX_wrapper.sh`

**Problem:**
DiscoPoP's runtime library (`DPUtils.cpp`) uses `DP_PROJECT_ROOT_DIR` to filter out non-project functions from the dependency graph. If this variable was not set before invoking `discopop_cxx`, all function calls (including standard library functions) were profiled, producing noisy and incorrect dependency data. Previously the user had to manually export this variable before every compilation.

**Fix:**
Added a default at the top of the wrapper:
```bash
: "${DP_PROJECT_ROOT_DIR:=$(pwd)}"
export DP_PROJECT_ROOT_DIR
```

**Effect:**
Running `discopop_cxx bubble_sort.cpp` from the source directory now works without any environment variable setup. `$(pwd)` gives the correct project root in the common case where the user compiles from the source directory.

---

## Fix 4 — Re-profiling: new candidates are queued in the active loop

**File:** `controller.py`

**Problem:**
After a successful Tier-2 patch, `_reprofil()` re-ran DiscoPoP and discovered new parallelism patterns in the restructured code. However, the candidate loop was written as:

```python
for candidate in candidates:
    ...
```

Python's `for` loop over a list takes a snapshot of the list length at loop start. Any candidates appended during the loop are invisible to it. New patterns from re-profiling were silently ignored.

**Fix:**
Changed to an index-based `while` loop with a `seen_ids` set to prevent duplicates:

```python
seen_ids: set = {c.region.region_id for c in candidates}
i = 0
while i < len(candidates):
    candidate = candidates[i]
    i += 1
    ...
    # after successful re-profile:
    fresh = build_candidates(dp_dir, ...)
    for nc in fresh:
        if nc.region.region_id not in seen_ids:
            seen_ids.add(nc.region.region_id)
            candidates.append(nc)
```

**Effect:**
Newly discovered candidates from re-profiling are appended to `candidates` and processed in the same agent run, without needing to re-invoke the agent manually.

---

## Fix 5 — Re-profiling: support custom binary arguments (`--reprofil-args`)

**Files:** `args.py`, `controller.py`

**Problem:**
`_reprofil()` always invoked the re-instrumented binary as `./a.out` with no arguments. If the target function was only reachable via a specific execution path (e.g. `./a.out sort input.txt`), re-profiling would produce empty profiling data for that function and miss new patterns.

**Fix:**
- Added `reprofil_args: list` field to `AgentArguments`.
- Added `--reprofil-args` CLI flag (using `nargs=argparse.REMAINDER`) that forwards any trailing arguments to the binary.
- Updated `_reprofil(source_file, discopop_dir, binary_args=None)` to run `[binary] + (binary_args or [])`.

**Usage:**
```bash
python -m discopop_agent \
    --discopop-dir src/.discopop \
    --source-file  src/main.cpp \
    --reprofil-args sort input.txt
```

**Effect:**
Re-profiling exercises the correct execution path, ensuring new patterns in restructured functions that require specific inputs are captured.

---

## Fix 6 — L4 validator: auto-correct off-by-one hunk headers in LLM diffs

**File:** `l4_validator.py`

**Problem:**
LLMs frequently produce unified diffs with incorrect line counts in `@@ -a,b +c,d @@` hunk headers (e.g., writing `+21,20` when the body provides only 18 new lines). GNU `patch` is strict about these counts and fails immediately with:

```
patch: **** malformed patch at line N
```

This caused a real LLM's structurally correct diff to fail at `stage=apply`, wasting a budget retry on a purely mechanical formatting error rather than a logic error.

**Fix:**
Added `_fix_hunk_headers(diff: str) -> str` inside `_apply()`. It scans each hunk body, counts actual context/removed/added lines, and rewrites the `@@ ... @@` header with the correct numbers before the diff is written to disk:

```python
def _fix_hunk_headers(diff: str) -> str:
    # For each @@ header: scan body, recount old_count and new_count, rewrite header
    ...
```

**Effect:**
Minor LLM line-count errors are silently corrected. The budget is only consumed for genuine failures (wrong logic, compile errors, data races) — not for a trivial header miscalculation. For diffs with already-correct headers, the recount matches and nothing changes.

---

## Fix 7 — `l1_planner.py`: corrected misleading workload comment

**File:** `l1_planner.py`

**Problem:**
The comment at the workload parsing block read:
```python
# Workload from instructionsCount for CUs; 0 for loops/functions
# (loop/function workload is aggregated from child CUs later)
```

This was incorrect: no child-CU aggregation code exists for functions (that feature was designed but not implemented). The comment implied a step that never happens, which was misleading when reading or extending the planner.

**Fix:**
Replaced with an accurate description:
```python
# Workload from instructionsCount for CUs only.
# Loops get a proxy (iteration_count × body_size) below.
# Functions have no fallback and remain 0.
```

**Effect:**
Comment accurately reflects the actual behavior. Loops get a workload estimate; functions always score 0 unless a pattern provides a `workload` field.

---

## Fix 8 — Documentation: corrected and extended Known Limitations

**File:** `DOCUMENTATION.md`

**Problems corrected:**

- **Limitation 3** previously stated "Functions and loops derive their workload from child CUs" — this was wrong for functions. Corrected to state that loops use `iteration_count × body_size` as a proxy and functions always remain 0.

- **Missing limitation** about re-profiling candidates not being queued (the `for` loop issue, now fixed by Fix 4 above). Added as limitation 4, then removed once fixed.

- **Missing limitation** about the binary entry point was updated to reflect the new `--reprofil-args` flag (Fix 5), changing it from a hard limitation to a configurable parameter.

**Limitations renumbered** after fixes 4 and 5 resolved two of the original items:

| # | Limitation |
|---|---|
| 1 | LLM sees original source on retry, not cumulative patches |
| 2 | DiscoPoP false positives are pervasive |
| 3 | Function-level workload is always 0 in Data.xml |
| 4 | Re-profiling uses the same binary entry point (mitigated by `--reprofil-args`) |
| 5 | Mock LLM is keyed by start line only |

---

## Fix 9 — `_is_omp_barrier_false_positive`: allocation lines matched as access lines

**File:** `controller.py`

**Problem:**
The false-positive detector checked `"by main thread:" in line` to identify which TSan diagnostic lines indicate the main thread is one of the racing accessors. However, TSan heap-location blocks contain a line such as:

```
Location is heap block of size N ... allocated by main thread:
```

This line also matches `"by main thread:"`, so the detector would scan the *allocation* stack frames (which never contain `.omp_outlined`) and conclude there was no worker access — incorrectly classifying a real WAW scatter race as a false positive. The scatter-add kernel in `lulesh/ex2` was silently accepted without escalating to Tier-2.

**Fix:**
Added `and ("Write" in line or "Read" in line)` to the condition, so only genuine *access* lines (`"Write of size N ... by main thread:"` / `"Read of size N ... by main thread:"`) trigger the false-positive check:

```python
if "by main thread:" in line and ("Write" in line or "Read" in line):
```

**Effect:**
Allocation lines in TSan heap-location blocks are ignored. Only actual write/read-access lines by the main thread trigger the OMP-barrier false-positive path. Real WAW scatter races now correctly escalate to Tier-2.

---

## Fix 10 — `call_manual` (`l3_llm.py`): `---END---` delimiter for piped multi-diff input

**File:** `l3_llm.py`

**Problem:**
In `--manual-llm` mode, `call_manual()` read stdin until `EOFError`. When multiple diffs are piped in a single shell session (e.g. via process substitution or heredoc), the first call consumes EOF, which closes stdin permanently. Every subsequent `call_manual()` call in the same agent run immediately hit `EOFError` and returned an empty string, exhausting the Tier-2 budget with "LLM returned invalid diff" for all remaining regions.

**Fix:**
Added `_MANUAL_EOF = "---END---"` as a per-diff terminator. Each `call_manual()` call reads lines until it sees `---END---` on its own line (or true EOF). Piped runs separate diffs with `---END---`:

```bash
{ echo "$DIFF1"; echo "---END---"; echo "$DIFF2"; echo "---END---"; } | python -m discopop_agent ...
```

**Effect:**
Multiple Tier-2 diff requests in a single agent run can be served from a single piped stdin. Interactive users type `---END---` to submit each diff. True EOF still works as a fallback terminator.

---

## Fix 11 — `controller.py`: 1-iteration early-exit filter *(reverted — see Fix 20)*

**File:** `controller.py`

**Originally added:**
An early-exit guard `if region.iteration_count <= 1: skip` was placed at the top of the candidate processing loop to avoid spending budget on regions that only ran once during profiling.

**Why it was wrong:**
The profiling run uses a fixed input (e.g. N=256, STEPS=50). The iteration count reflects *that input*, not the production workload. A loop that ran once under the profiling input may run millions of times in production. Filtering on raw iteration count silently discards candidates that the score/speedup system already handles correctly.

Additionally, after a Tier-2 restructuring causes region IDs to drift (see Fix 19), unrelated constructs inherit the old ID and report ≤ 1 iteration — causing legitimate original regions to be skipped for the wrong reason.

**Reverted by Fix 20.** The score and `--min-workload` system is the correct gate. ID drift in rebuilt candidates is handled separately by Fix 19.

---

## Fix 12 — `_adjusted_line`: proportional intra-hunk line mapping

**File:** `controller.py`

**Problem:**
`_adjusted_line(diff, old_line)` accumulates per-hunk `(new_count - old_count)` shifts for all hunks that end *before* `old_line`. For lines that fall *inside* a hunk (i.e. within the changed region), the function broke out of the hunk loop without adding any shift, returning the stale pre-patch line number.

Concrete failure: the odd-even bubble sort diff inserts `int start = pass % 2;` before the inner loop, moving it from line 23 to line 24. But `_adjusted_line(diff, 23)` returned 23 (line 23 is inside the `@@ -19,8 +19,9 @@` hunk), so `fresh_by_key.get((file_id, 23))` found a 1-iteration IR artifact at line 23 rather than the real inner loop at line 24. The inner stride-2 loop was never queued and never parallelized.

A secondary bug: using Python's `round()` (banker's rounding) would compute `round(4 × 9/8) = round(4.5) = 4` instead of 5, keeping the result at 23 even after the proportional mapping was added.

**Fix:**
- Extract `new_start` from the `+N,M` part of the hunk header (previously ignored).
- For inside-hunk lines, compute a proportional position within the new hunk using classic round-half-up (`int(x + 0.5)`) instead of `round()`:

```python
if old_line < old_start + old_count:
    offset = old_line - old_start
    new_pos = new_start + int(offset * new_count / max(old_count, 1) + 0.5)
    return min(new_pos, new_start + new_count - 1)
```

**Effect:**
`_adjusted_line(diff, 23) = 24` for the bubble sort odd-even diff. `fresh_by_key.get((1, 24))` finds the inner stride-2 loop with 512+ iterations, which is then correctly processed at Tier-1 (TSan passes, OMP barrier false positive correctly identified) and accepted. All context lines within the hunk also map correctly via proportional scaling.

---

## Fix 13 — `mock_llm.py`: invalid OpenMP loop condition `i + 1 < n`

**File:** `mock_llm.py`

**Problem:**
The pre-computed `_DIFF_BUBBLE_SORT` diff used `for (int i = start; i + 1 < n; i += 2)` for the restructured inner loop. OpenMP requires that the loop condition be a simple relational comparison directly against the loop variable (`i < expr`, `i <= expr`, etc.). The compound expression `i + 1 < n` is rejected at compile time:

```
error: condition of OpenMP for loop must be a relational comparison
       ('<', '<=', '>', '>=', or '!=') of loop variable 'i'
```

This caused the inner loop (region 1:45) to fail at `stage=compile` and exhaust its Tier-2 budget attempting to fix a problem introduced by the mock diff itself.

**Fix:**
Changed to the mathematically equivalent `i < n - 1`:

```python
for (int i = start; i < n - 1; i += 2) {
```

**Effect:**
The inner stride-2 loop compiles with `#pragma omp parallel for`, TSan passes (no cross-iteration conflicts at stride 2), and region 1:45 is accepted at Tier-1 without consuming any Tier-2 budget.

---

## Fix 14 — `call_llm` and `call_manual`: full conversation history across budget retries

**Files:** `l3_llm.py`, `controller.py`

**Problem:**
Each budget retry was a completely fresh API call. The only context the LLM had about previous attempts was a single `### Your previous attempt (FAILED)` text block embedded in the new user prompt. This approach had two weaknesses:

1. **Only the most recent attempt was visible** — on budget retry 3, the LLM saw attempt 2's diff but not attempt 1's diff or its failure diagnostic.
2. **Loss of conversational role structure** — the previous diff was pasted as inert text rather than appearing as an actual assistant turn. The LLM couldn't "own" its previous response or reason about it naturally.

The root cause was that `call_llm` accepted `prior_diff: Optional[str]` (a string) and returned `Optional[str]` (just the diff), with no way to carry state between budget iterations.

**Fix:**
- **`l3_llm.py`**: Changed `call_llm` signature from `(evidence, ..., prior_diff=None) → Optional[str]` to `(evidence, ..., messages=None) → tuple[Optional[str], list]`.
  - When `messages=None` (first call), the initial prompt is built from evidence.
  - When `messages` is provided (subsequent calls), the conversation continues from that history — no prompt rebuild.
  - Returns `(diff, updated_messages)` on success so the controller can extend the conversation; `(None, current_messages)` on format failure.
- **`controller.py`**: Added `tier2_messages: list | None = None` before the budget while-loop.
  - `call_llm` is now called as `diff, tier2_messages = call_llm(..., messages=tier2_messages)`.
  - After each quality-gate failure, the controller appends a user turn with the stage name and diagnostic to `tier2_messages`:
    ```python
    tier2_messages = tier2_messages + [{
        "role": "user",
        "content": (
            f"Your diff failed at the '{result.stage}' stage.\n\n"
            f"Diagnostic:\n{diagnostic_snippet}\n\n"
            f"Please try a different restructuring approach."
        ),
    }]
    ```
  - On the next budget retry, `call_llm` receives these accumulated messages and the LLM sees the full exchange — all previous diffs in their natural assistant-turn positions and all failure diagnostics as user turns.

**Behavior in mock mode:**
`call_mock` is unaffected — it uses `diff = call_mock(evidence)` (single return value). `tier2_messages` remains `None` and the quality-gate extension block does not fire.

**`call_manual` updated identically (Fix 17):**
`call_manual` was subsequently updated to the same contract: `(evidence, messages=None) → tuple[Optional[str], list]`. It displays the full conversation history to the user before each diff input, so the human playing the LLM sees exactly the same context a real model would receive.

**Effect:**
On budget retry N, the LLM sees a multi-turn conversation:
```
user:      initial task + dependency profile + original failure reason
assistant: first attempted diff
user:      "Your diff failed at 'compile'. Diagnostic: ..."
assistant: second attempted diff
user:      "Your diff failed at 'tsan'. Diagnostic: ..."
```
This gives the LLM complete context to avoid repeating the same mistake or introducing the same category of error twice, without any extra API cost (the system prompt remains cached via `cache_control: ephemeral`).

---

## Fix 15 — `controller.py`: patch written to disk was not header-corrected, apply failure was silent

**Files:** `l4_validator.py`, `controller.py`

**Problem:**
The L4 quality gate calls `_fix_hunk_headers(diff)` internally before applying the diff to its temporary working copy — this corrects the `@@ -a,b +c,d @@` line counts that LLMs frequently miscalculate. The quality gate therefore PASSES on the corrected version.

However, the controller then:
1. Wrote the **original** (uncorrected) diff directly to `patch_file`:
   ```python
   patch_file.write_text(diff)
   ```
2. Applied the **uncorrected** patch to the actual source file:
   ```python
   subprocess.run(["patch", "--quiet", str(src_abs), str(patch_file)], capture_output=True)
   ```
3. Never checked the return code.

The result: GNU `patch` rejected the malformed hunk header silently (both `--quiet` and `capture_output=True` suppressed all output), the source file was left unmodified, re-profiling ran on the original code, and the agent printed `ACCEPTED` while nothing had actually changed.

**Concrete example:** A `--manual-llm` diff for `example4/bubble_sort.cpp` had header `@@ -22,10 +22,20 @@` but the new hunk body was 17 lines, not 20. The quality gate fixed it to `+22,17` and passed. The controller saved `+22,20` to disk and `patch` rejected it at line 28.

**Fix:**
- Renamed `_fix_hunk_headers` → `fix_hunk_headers` in `l4_validator.py` (made public).
- Controller imports `fix_hunk_headers` and applies it to `diff` before writing the patch file:
  ```python
  clean_diff = fix_hunk_headers(diff)
  patch_file.write_text(clean_diff)
  ```
- Controller checks `patch_result.returncode` and logs a warning if non-zero.

**Effect:**
The same header correction used by the quality gate is now also applied when writing the patch to disk. The saved `.patch` file and the applied modification are always consistent. A failed apply is now logged as a WARNING instead of silently accepted.

---

## Fix 16 — `_build_prompt`: clarify that source line-number prefix is display-only

**File:** `l3_llm.py`

**Problem:**
The source region shown in the prompt used the format `f"{i:4d} {marker} {code_line}"`, producing lines like:
```
  25 >>>     for (int step = 0; step < steps; step++) {
```
LLMs read this as the actual file content and copied the `  25 >>> ` prefix into diff context lines (lines beginning with a space). GNU `patch` then failed with "1 out of 1 hunks failed" because those context lines did not match the raw source file, which has no line-number prefix.

**Fix:**
Changed the `### Source` section header in `_build_prompt` to include an explicit note:
```
(Each line is shown as `NNNN >>> code` where `NNNN` is the line number and `>>>` marks
the target region. These prefixes are display-only — NOT part of the actual source file.
When writing diff context lines copy only the raw code indentation, never the `NNNN >>>` prefix.)
```
Also added the same reminder to the `### Task` section at the bottom of the prompt.

**Effect:**
LLMs write diff context lines with the correct raw indentation, matching the actual file content. Patch apply no longer fails due to line-number padding copied from the source display.

---

## Fix 17 — `call_manual`: full conversation history (mirrors Fix 14)

**File:** `l3_llm.py`, `controller.py`

**Problem:**
`call_manual` (the `--manual-llm` mode) still used the old `prior_diff: Optional[str]` approach: the previous failed diff was embedded as text under `### Your previous attempt (FAILED)`. The human acting as the LLM only saw the most-recent failed diff, not the full exchange including quality-gate diagnostics, and `tier2_messages` was never populated for manual mode so the quality-gate feedback block (`if tier2_messages is not None:`) never fired.

**Fix:**
- Changed `call_manual` signature from `(evidence, prior_diff=None) → Optional[str]` to `(evidence, messages=None) → tuple[Optional[str], list]`, matching `call_llm` exactly.
- First call (`messages=None`): prints system prompt + initial user prompt as before.
- Subsequent calls (`messages=[...]`): prints the full conversation history (each user and assistant turn labelled) so the human sees the same context a real LLM would receive.
- Returns `(diff, messages + [{"role": "assistant", "content": diff}])` on success.
- In `controller.py`: changed `diff = call_manual(evidence, prior_diff=last_diff)` to `diff, tier2_messages = call_manual(evidence, messages=tier2_messages)`. Removed `last_diff`. The quality-gate feedback block now fires for manual mode too.

**Effect:**
On a manual-LLM retry the terminal shows the full exchange:
```
[USER]   initial task + source + dependencies
[ASSISTANT]  previous diff
[USER]   "Your diff failed at 'apply'. Diagnostic: ..."
```
The human has complete context before typing the next diff.

---

## Fix 18 — `--distance`: pass-based discovery *(superseded by Fix 21)*

**Files:** `args.py`, `controller.py`

Originally introduced a `--distance N` parameter that ran N additional discovery passes after the initial candidate list was exhausted.  Replaced by Fix 21 with continuous discovery via `--max-reprof`.

---

## Fix 19 — ID-based rebuild: drop iteration-count-collapsed candidates *(superseded by Fix 21)*

Originally filtered ID-drifted candidates from the within-pass rebuild by checking `iteration_count > 1`.  The entire ID-based rebuild block was removed by Fix 21, which discards the stale remaining queue after each re-profile instead.

---

## Fix 20 — `controller.py`: remove global `≤ 1 iteration` skip (reverts Fix 11)

**File:** `controller.py`

**Problem:**
Fix 11 added a global early-exit guard that skipped any candidate with `iteration_count ≤ 1`. This was too aggressive:

1. **Profiling input ≠ production workload.** The profiling run uses a fixed input; a loop that ran once on the profiling input may run millions of times in production. The score/speedup system already accounts for observed workload — a second filter on raw iteration count is redundant and wrong.
2. **Functions are never loops.** Function-level candidates (`type=function`) naturally report `iteration_count = 1` (the function is called once). They can still contain regions worth restructuring, and Tier-2 LLM analysis is exactly what handles them.
3. **ID drift** (after Tier-2 restructuring changes CFG traversal order) could assign an old ID to a trivial new construct, making an originally-busy region appear to have 1 iteration and be silently dropped.

**Fix:**
Removed the `if region.iteration_count <= 1: skip` block entirely from the main candidate loop. The score gate (`--min-workload`) and Tier-1/Tier-2 logic are the sole filters for whether a region is worth processing.

---

## Fix 21 — Replace `--distance`/`--max-reprof` with `--restructure-depth`: bounded discovery chain

**Files:** `args.py`, `controller.py`

**Problem:**
Both `--distance` and `--max-reprof` were blunt cycle counters. They capped re-profiling but did not address the root concern: each Tier-2 restructuring exposes new regions, which could themselves be restructured, exposing more regions — a cascading chain that drifts the source arbitrarily far from the original.

**Fix — `--restructure-depth N` (default 0):**

Every candidate now carries a `discovery_depth`:
- Initial candidates from the first DiscoPoP profile → `depth=0`
- Candidates discovered after a Tier-2 re-profile → `depth = parent_depth + 1`

Tier-2 (LLM restructuring) is only applied to candidates at `depth ≤ N`. Candidates at `depth > N` are processed with Tier-1 only. If no pattern is found or Tier-1 fails, they are skipped — no LLM call, no further source modification.

```
--restructure-depth 0 (default):
  depth=0  initial regions  → Tier-1 or Tier-2 → re-profile
  depth=1  discovered       → Tier-1 only       → no re-profile → terminates

--restructure-depth 1:
  depth=0 → Tier-1/Tier-2 → re-profile → depth=1 → Tier-1/Tier-2 → re-profile
  depth=2 → Tier-1 only   → terminates
```

**After each Tier-2 acceptance** the agent (see Fix 22 for the content-matching detail):
1. Snapshots the content fingerprint of each still-queued candidate (before the patch touches the file).
2. Applies the patch to source.
3. Re-profiles the whole file.
4. Matches survivors by content fingerprint and rebuilds them with fresh data, keeping their depth.
5. Appends newly discovered candidates (unseen content) at `depth + 1`.

**Termination is guaranteed**: at `depth N+1` no Tier-2 is applied, so the source never changes again, re-profiling stops, and the queue drains.

**Candidate table** now shows a `Depth` column. Summary shows `depth=N` per accepted region.

**Effect:**
- LLM restructures the source at most at depths 0…N — the chain is explicitly bounded.
- Discovered regions at depth N+1 are harvested via Tier-1 only, capturing parallelism the restructuring exposed without triggering further code changes.
- `--restructure-depth 0` (default) is the safe choice: only initial regions are restructured, everything discovered after is Tier-1 only.

---

## Fix 22 — Content fingerprinting: track regions across re-profiles by source text, not ID

**File:** `controller.py`

**Problem:**
DiscoPoP assigns region IDs from a single global counter (`Structs.hpp:60`: `ID = fileID + ":" + CUIDCounter++`). The counter increments across every CU in every function, in top-to-bottom file order. Patching one function adds/removes CUs, which shifts the counter for **every region defined after it** — even in completely untouched functions.

Concretely, after patching `smooth()` in `stencil.cpp`:
- Every region in `main()` (which follows `smooth` in the file) drifts by exactly the number of CUs added — **100% of the time**.
- Regions inside the patched function drift too.

So the previous ID-based rebuild (`fresh_by_id[old_id]`) was almost always wrong: the old ID, looked up in the fresh profile, returned a *different* region. There was also no reliable way to tell a genuinely new region apart from an original region that had merely drifted to a new ID.

**Fix:**
Identity is now keyed on the region's **source text**, not its ID. A region's text is invariant under ID drift and line-number shifts — it only changes if that exact region was patched.

`_fingerprint(source_file, start_line, end_line, name)` returns a normalized signature: whitespace-stripped, blank/comment lines dropped, prefixed with the enclosing region name (function name where available) to disambiguate textually identical siblings.

The flow on Tier-2 acceptance:
1. **Before** the patch touches the file, snapshot `old_prints = [(depth, fingerprint) for each remaining candidate]`. (A survivor's text is identical pre/post patch, so its fingerprint will match.)
2. Apply patch, re-profile, build `fresh_all`.
3. Index fresh candidates into `fresh_by_print` (a bucket list per fingerprint, so duplicate sibling regions pair up 1:1).
4. **Survivors**: for each `old_prints` entry, consume one matching fresh candidate — keeps the old depth, adopts the fresh candidate's current lines / pattern / patch data.
5. **Discovered**: fresh candidates with content never seen (`fp not in all_seen_prints`) and not consumed as a survivor → enqueued at `depth + 1`.

`all_seen_ids` (ID-based, broken by drift) is replaced by `all_seen_prints` (content-based).

**Known limitation:**
Two byte-for-byte identical regions in the same function are matched arbitrarily within their fingerprint bucket. Folding the function name and surrounding context into the fingerprint reduces, but does not fully eliminate, this ambiguity. A heavily-restructured region whose text changed is treated as new (depth+1), which is acceptable.

**Why not fix it in DiscoPoP instead:**
The root cause is the global `CUIDCounter`. A per-function counter (`ID = fileID:functionName:localCounter`) in `Structs.hpp` would make IDs stable across patches to other functions. That is the proper long-term fix but requires changing the C++ LLVM pass and its downstream consumers; content fingerprinting solves it entirely at the agent layer without touching the profiler.

---

## Fix 23 — Summary: carry depth on skipped regions, de-duplicate IDs accepted elsewhere

**File:** `controller.py`

**Problem:**
Because DiscoPoP reuses region IDs across re-profiles, a single ID can describe different *content versions* at different depths. In the `example5` run, the bounds-check loop was skipped as `1:79` at depth 0 (with a `break`, Tier-2 diffs failed), then — after an enclosing region's restructuring removed the `break` — re-appeared as a new-content `1:79` at depth 1 and was accepted at Tier-1. The summary listed the same ID under both ✓ and ✗, which reads as a contradiction. The skipped list also stored bare ID strings with no depth, so there was no way to tell which version was meant.

**Fix:**
- `skipped` now stores `(region_id, discovery_depth)` tuples instead of bare IDs (all five skip sites updated).
- The summary:
  - drops any skipped ID that also appears in `accepted` (it was resolved in some version),
  - de-duplicates remaining skipped IDs, keeping the lowest depth seen,
  - prints `depth=N` on each skipped line, matching the accepted lines.
- The skipped count in the `SUMMARY:` header reflects the de-duplicated total.

**Effect:**
Each region ID appears under exactly one outcome. A loop that was skipped at depth 0 but accepted at depth 1 shows only as accepted. Skipped lines now carry depth, so overlapping/re-profiled versions are distinguishable.

---

## Fix 24 — OpenMP-canonical loop form: prompt constraint + distinct `openmp_compile` stage

**Files:** `l3_llm.py`, `l4_validator.py`, `controller.py`

**Problem:**
On `example4` (bubble sort), the LLM restructured the inner loop into a correct, race-free odd-even transposition sort — but wrote the phase loops as `for (int i = 0; i + 1 < n; i += 2)`. That condition is logically fine but **not OpenMP-canonical**: OpenMP requires the loop condition to compare the loop variable directly against a loop-invariant bound. When DiscoPoP later generated `#pragma omp parallel for` for those phases (at depth 1), the build failed:

```
error: condition of OpenMP for loop must be a relational comparison
       ('<', '<=', '>', '>=', or '!=') of loop variable 'i'
   31 | for (int i = 0; i + 1 < n; i += 2) {
```

Two things made this hard to see and impossible to recover from:

1. **Misleading stage.** Stage-2 compile uses plain `clang++`, which *ignores* `#pragma omp`, so it passed. The error only appeared in stage-3, which compiles with `-fopenmp`. But stage-3 returned `stage="tsan"`, so the controller printed `Validation FAILED (stage=tsan) — DiscoPoP false positive` — framing a **compile error** as a **data race / false positive**.

2. **Unrecoverable at depth > restructure-depth.** The phase loops were depth-1 candidates. With `--restructure-depth 0` they get Tier-1 only, so the agent could not escalate to Tier-2 to rewrite `i+1<n` → `i<n-1`. Result: a correct restructuring exposed parallelism that was then **silently discarded** — 2 restructurings accepted, 0 parallel loops validated.

**Fix (three parts):**

1. **Prevent at the source** — added a `CRITICAL` block to the L3 system prompt (`l3_llm.py`) requiring every loop intended for parallelization (including newly created ones) to be OpenMP-canonical:
   - condition compares the loop variable directly to a loop-invariant bound (`i < n - 1`, never `i + 1 < n`);
   - increment is `i++`/`i--`/`i += c`/`i -= c`;
   - no `break`/`continue`/`return`/`goto` in the body (convert early-exit/flag loops to a full scan accumulating into a variable);
   - computable trip count.

2. **Distinct stage** — `_tsan()` in `l4_validator.py` now returns `(ok, diagnostic, stage)`. An `-fopenmp` build failure returns `stage="openmp_compile"` with the diagnostic `"OpenMP compile failed (loop not in OpenMP-canonical form)"`; a genuine race still returns `stage="tsan"`. `validate()` propagates the returned stage.

3. **Correct framing** — the controller's Tier-1 failure branch now distinguishes `openmp_compile` from `tsan`: it prints `loop not in OpenMP-canonical form` (not "false positive") and, when escalating to Tier-2, gives a targeted instruction to rewrite the loop into canonical form rather than the generic "loop-carried dependency" hint.

**Effect:**
- The LLM is told up front to emit canonical loops, so the restructuring's exposed loops compile under `-fopenmp` and pass Tier-1 directly at depth+1.
- When a non-canonical loop does slip through, the diagnostic correctly says "OpenMP compile error", not "data race / false positive", and at depth 0 the Tier-2 retry gets a precise fix instruction.
- Note the residual design constraint: with `--restructure-depth 0`, exposed loops must be *directly* parallelizable, because depth+1 loops cannot be escalated to Tier-2. The prompt constraint is what makes that constraint satisfiable in practice.

---

## Fix 25 — Correctness gate, measured-speedup gate, and correctness prompt guidance

**Files:** `l4_validator.py`, `controller.py`, `args.py`, `types.py`, `l3_llm.py`

**Problem:**
On `example4`, the LLM's odd-even restructuring used `int total = n - 1` — but odd-even transposition sort needs **`n`** phases. With `n-1` phases the array no longer fully sorts (the program printed `sorted: NO`). The agent **accepted it anyway**: the quality gate checked only apply / compile / race, never whether the program still produced correct output. This directly violated the system prompt's own first rule ("identical observable results"), which was *requested* but never *verified*.

Separately, there was no check that a parallelization actually runs *faster* — a correct but pointless pragma (overhead > benefit) would still be accepted.

**Fix (four parts):**

1. **Correctness gate (Stage 4).** `capture_reference_output()` compiles the unmodified source (`-O2`, no OpenMP/TSan) and runs it once to record golden stdout. `validate()` gained a `reference_output` parameter; after the TSan stage it compiles the patched source **with** `-fopenmp`, runs it, and compares stdout byte-for-byte. A mismatch fails with `stage="correctness"` and an `expected vs got` diagnostic. The controller captures the reference once at start-up and passes it to every `validate()` call.

2. **Measured-speedup gate (Stage 5).** When `--require-speedup` is set and the patch adds a `#pragma omp`, `validate()` builds the patched source both sequentially (no `-fopenmp`) and in parallel (`-fopenmp`), times each (min of 3 runs), and requires `seq_time / par_time ≥ --min-measured-speedup` (default 1.0). Otherwise it fails with `stage="performance"`. The measured ratio is stored on `ValidationResult.measured_speedup` and printed on the accepted line. A performance failure **skips** the region (does not escalate to Tier-2 — restructuring cannot manufacture a bigger workload).

3. **OMP-barrier false positive now ground-truthed.** When the controller suspects a macOS OMP-barrier false positive (TSan race whose other accessor is the sequential main thread), it no longer accepts on the heuristic alone — it re-runs `validate(skip_race_check=True)` so the correctness (and performance) gates verify the patch. `_tsan()` gained `skip_race_check`: it still compiles (so `openmp_compile` errors are caught) but ignores a reported race, letting the later stages decide.

4. **Correctness prompt guidance.** Added a `CORRECTNESS` block to the L3 system prompt telling the LLM its change is auto-verified against reference output and how to stay equivalent: preserve the algorithm's full work (e.g. odd-even sort needs N phases, not N-1), don't drop boundary elements or tighten bounds, prefer the smallest dependency-targeted transform over a wholesale rewrite, and re-derive results identically (same accumulation/order for floating-point).

**New CLI:** `--require-speedup` (default off) and `--min-measured-speedup FLOAT` (default 1.0).

**New result stages:** `correctness`, `performance` (in addition to `openmp_compile` from Fix 24).

**Verified:** on the `example4` odd-even transform, the gate accepts the `n`-phase version (`stage=accepted`) and rejects the `n-1`-phase version (`stage=correctness`).

**Caveat:** the correctness gate needs a program with deterministic, observable output (the examples print results — fine); if the reference can't be captured it is disabled with a warning. The speedup gate is opt-in because tiny workloads may not beat thread-spawn overhead.

---

## Fix 26 — Every validation failure carries its reason into the next LLM prompt

**File:** `controller.py`

**Problem:**
Two gaps meant the LLM did not always learn *why* a patch was rejected:

1. **Performance failures were a dead end.** A Tier-1 pragma patch that was correct but not faster set `escalate = False` and simply skipped — the LLM was never told the parallelization was rejected for being slow, so it had no chance to try a coarser-grained restructuring.
2. **The fed-back diagnostic was over-truncated.** The Tier-2 retry message truncated the diagnostic to 600 chars; the correctness stage's `expected vs got` comparison (~1.3 KB) was cut off, so the LLM often couldn't see how the output differed.

**Fix:**

- **Performance failures now escalate to Tier-2** (when depth allows) with a targeted hint: the pragma is correct but measured `X×` < required, so increase parallel granularity / hoist invariant work / fuse tiny loops to amortise thread overhead. The dead `escalate` flag and its guard were removed (all failure stages now escalate; only `tier2_allowed`/depth gates a skip).
- **Plain-English per-stage guidance.** A `_STAGE_GUIDANCE` map gives every stage (`apply`, `compile`, `openmp_compile`, `tsan`, `correctness`, `performance`) a one-line explanation of what went wrong and what to do, prepended to both `failure_reason` (first Tier-2 prompt) and the appended conversation turn (budget retries).
- **Wider diagnostic.** The fed-back diagnostic limit was raised from 500/600 to 1400 chars so the correctness `expected vs got` block survives intact.

**Effect:**
On any rejection — including correctness and speedup — the next prompt the LLM sees states the stage, a human-readable reason, and the full diagnostic. The LLM can act on *why* it failed instead of guessing. Note this makes the speedup gate actively drive restructuring (correct-but-slow regions now get an LLM attempt, bounded by `--budget` and `--restructure-depth`) rather than silently dropping them.

---

## Fix 27 — Restructuring must pay off: revert + retry when no exposed loop speeds up

**File:** `controller.py`

**Problem:**
A Tier-2 LLM restructuring produces pragma-less code, so it can't be speed-tested on its own — the speedup only appears later, once DiscoPoP parallelizes the loops it exposed (at depth+1, Tier-1). The agent therefore *committed* a restructuring the moment it passed correctness, then judged each exposed loop's speedup **separately and independently** downstream. Nothing ever asked the combined question: *"did this restructuring actually make anything faster?"* A restructuring whose exposed loops all turned out too small to beat thread overhead stayed committed on disk, having changed the source for no benefit, and the LLM never got a chance to try a better decomposition.

**Fix — speedup-gated commit with rollback:**
When `--require-speedup` is set and the exposed loops are **terminal** (`depth+1 > --restructure-depth`, i.e. they won't get their own Tier-2 pass), the controller now treats the restructuring as *tentative*:

1. Save the pre-patch source; apply the patch; re-profile (queue and `all_seen_prints` are computed **read-only**, not yet mutated).
2. `_best_exposed_speedup()` runs each exposed loop's DiscoPoP pragma through the full gate (compile + correctness + measured speedup; barrier-FP re-verified). It returns the best qualifying speedup, or `None` if no exposed loop is both correct and faster.
3. **If `None` → revert:** restore the source, re-profile back to the pre-patch state, delete the patch file, and `continue` the budget loop. The next attempt gets `failure_reason` / a conversation turn explaining *"your restructuring preserved correctness but produced no speedup — expose coarser-grained, higher-payoff parallelism."* Budget is consumed naturally (it was decremented at the loop top), and the remaining queue is intact because `candidates[i:]` was never deleted.
4. **If a speedup exists → commit:** only now delete `candidates[i:]`, enqueue survivors + discovered, update `all_seen_prints`, record `exposed_speedup`, and accept.

When `--require-speedup` is off, or the exposed loops are non-terminal (`depth+1 ≤ --restructure-depth`, so they can still be restructured further), behaviour is unchanged — commit on correctness.

**Effect:**
A restructuring is kept only if it demonstrably leads to a faster parallel loop; otherwise it is rolled back and the LLM retries from the same budget with the reason. This closes the loop the user identified: the speedup result now feeds back as an accept/reject **verdict on the restructuring itself**, not just per-exposed-loop verdicts after the fact.

**Cost/limitations:** exposed loops are speed-tested at commit time and again when later processed from the queue (double work — correctness prioritised over caching). The check only applies to terminal exposed loops, so at `--restructure-depth ≥ 1` an intermediate restructuring is still committed on correctness and judged once its descendants become terminal.

---

## Fix 28 — Fast revert: restore a profile snapshot instead of re-profiling

**File:** `controller.py`

**Problem:**
The speedup-gated revert (Fix 27) restored the source file (cheap) but then called `_reprofil()` to rebuild the `.discopop` state — a full instrument + run + explore — just to get back to a state the agent *already had* a moment earlier. That re-profile dominated the revert cost and is pure waste: a revert returns to a known prior state, so there is nothing new to compute.

**Fix — snapshot + restore:**
- `_snapshot_profile(dp_dir, output_dir)` copies `.discopop/` to a snapshot under `<output_dir>/.profile_snapshots/` (kept **inside the project**, not the OS temp dir) once, **before** the budget loop (only when a revert is possible: `--require-speedup` and the exposed loops are terminal). It excludes the agent's own `output_dir` (e.g. `agent_patches`) when that lives inside `.discopop`, so accepted records/patches/backups — and the snapshot itself — are never part of the copy.
- `_restore_profile(snap, dp_dir, output_dir)` reverts on a no-speedup result by deleting the regenerated profile contents (keeping `output_dir`) and copying the snapshot back — pure file operations, **no re-instrumentation/run/explore**.
- One snapshot serves every retry of a candidate (the pre-patch state is identical across retries, since each revert restores it). The snapshot is removed after the budget loop (commit or skip).

**Effect:**
A revert is now two directory copies instead of a full DiscoPoP re-profile — the expensive `_reprofil` is gone from the revert path entirely. Verified: restore reverts `Data.xml`/profile dirs, removes the re-profile's new directories, and preserves `agent_patches` (accepted.json, patches written during the attempt).

**Note:** the forward re-profile after applying a patch (needed to *discover* the exposed loops) is unchanged — only the revert's redundant re-profile is eliminated. On APFS/Linux the directory copies are fast; for very large `.discopop` profiles a copy-on-write clone (`cp -c` / reflink) would make it effectively instant.

---

## Fix 29 — Pluggable LLM provider: OpenAI-compatible endpoints (`--provider openai-compat`)

**Files:** `args.py`, `l3_llm.py`, `controller.py`

**Problem:**
`call_llm` was hard-wired to the Anthropic SDK, so the agent could only use Claude. Running against a self-hosted model (e.g. a vLLM server exposing an OpenAI-compatible API, such as `Qwen/Qwen3-Coder-30B-A3B-Instruct` on the HPC lab) was impossible without code edits.

**Fix:**
- **`l3_llm.py`**: factored the backend into `_make_client(provider, api_key, api_base)` and `_complete(provider, client, model, current)`. `call_llm` gained `provider` and `api_base` params.
  - `provider="anthropic"` (default) — unchanged: `system` sent separately, prompt-cached.
  - `provider="openai-compat"` — uses the `openai` SDK with `base_url=api_base`; the same `_SYSTEM` text is sent as the first `{"role":"system"}` message, followed by the identical user/assistant conversation. Diff extraction, format-retry, and the message protocol are shared across both.
- **`args.py`**: `--provider {anthropic,openai-compat}` (default anthropic) and `--api-base` (falls back to `LLM_API_BASE`). New `AgentArguments` fields `provider`, `api_base`.
- **`controller.py`**: passes `provider`/`api_base` to `call_llm`; banner shows `model @ base (openai-compat)`.
- Added `openai` to the venv.

**Usage (self-hosted, via SSH port-forward of the endpoint):**
```bash
ssh -fN -L 18000:localhost:18000 <user>@<server>     # tunnel the API locally
python -m discopop_agent \
    --source-file  example4/bubble_sort.cpp \
    --discopop-dir example4/.discopop \
    --provider openai-compat \
    --api-base http://localhost:18000/v1 \
    --model    Qwen/Qwen3-Coder-30B-A3B-Instruct \
    --api-key  ppkitestapikey \
    --budget 3 --min-workload 0 --restructure-depth 0
```

**Note:** the OpenAI path does not use Anthropic's ephemeral prompt cache, so the (large) system prompt is re-sent each call — fine for a local/free endpoint, but worth knowing for token accounting on metered OpenAI-compatible services.

---

## Fix 30 — `--edit-mode function`: LLM returns the rewritten function, agent makes the diff

**Files:** `args.py`, `types.py`, `l1_planner.py`, `l2_evidence.py`, `l3_llm.py`, `controller.py`

**Problem:**
Making the LLM emit a byte-exact unified diff is the single biggest source of wasted budget — most failures we saw were `stage=apply` (wrong `@@` anchors, off indentation, copied `NNNN >>>` prefixes, miscounted hunks), none of which are about parallelization quality. Self-hosted models (Qwen) are especially poor at exact diffs.

**Fix — a second edit mode where the LLM returns code, not a diff:**
- **`--edit-mode {diff,function}`** (default `diff`, unchanged behavior). In `function` mode the LLM is asked for the **complete rewritten enclosing function**; the agent splices it in by line range and **generates the diff itself**, so the apply step cannot fail on formatting.
- **`l1_planner.find_enclosing_function(profiler_dir, file_id, start, end)`** — finds the tightest function-type region containing the target (falls back to the region's own span).
- **`l2_evidence.assemble`** populates new `EvidencePackage` fields: `enclosing_function_{name,start,end,source}`.
- **`l3_llm`**: system prompt split into `_SYSTEM_CORE` + per-mode output trailer (`_OUTPUT_DIFF` / `_OUTPUT_FUNCTION`); new `_build_function_prompt` (shows the whole function + the target region's dependence profile, asks for the full function) and `_extract_code` (pulls the ```cpp block, requires braces). `call_llm`/`call_manual` take `edit_mode`; in function mode they return the rewritten function text.
- **`controller`**: `_function_edit_to_diff(source, start, end, new_code)` splices the function over `[start,end]` and emits a `difflib` unified diff — **generated from the real on-disk file, so it always applies**. Everything downstream (validate, correctness/speedup gates, snapshots, revert, `.patch` artifact) is unchanged; it just receives a guaranteed-clean diff.

**Effect:**
The entire `stage=apply` failure class disappears in function mode — budget is spent only on real issues (compile, race, correctness, speedup). Works identically on Anthropic and the self-hosted Qwen endpoint. Verified: a fenced function reply is extracted, spliced, and the generated diff applies cleanly via `patch`.

**Trade-off:** the LLM rewrites a whole function (more output tokens than a tight diff) and could in principle change more than the target loop — but the correctness gate already rejects any semantic drift, and the change stays bounded to one function.

**Follow-up (brace-match span):** DiscoPoP's function `endsAtLine` points at the last *statement*, not the closing `}` (e.g. it reports `main`'s `return 0;` line, not the `}` after it). Early function-mode runs then failed at `stage=compile` with "extraneous closing brace" because the splice left the original `}` in place beside the LLM's. Fixed with `l2_evidence._brace_match_end(source, start)` — it scans from the function's start line, balancing `{`/`}` (skipping `//`, `/* */`, and string/char literals), to find the true closing-brace line, which `assemble` uses for both the shown function source and the splice span. Verified on `example4`: `main` 33→48 (DiscoPoP said 47), `bubble_sort` 21→31. End-to-end function-mode run against Qwen then accepted 2 Tier-2 rewrites + 1 validated Do-All with zero apply/brace failures.

---

## Fix 31 — Cleanup: remove mock-LLM and manual-LLM modes; drop dead code

**Files:** `mock_llm.py` (deleted), `l3_llm.py`, `controller.py`, `args.py`, `l1_planner.py`, `types.py`, `DOCUMENTATION.md`, `INSTALL.md`

**Why:** With a real provider path in place (Fix 29 `--provider openai-compat` + Fix 30 `--edit-mode function`), the offline testing aids became dead weight. `mock_llm.py` was ~280 lines of pre-computed, example-specific diffs keyed fragilely by start line; `--manual-llm` was a human-in-the-loop crutch. Neither was referenced by any test or CI.

**Removed:**
- `mock_llm.py` deleted; `call_mock` import, the `--mock-llm` branch, and the `not args.mock_llm` guard removed from `controller.py`.
- `call_manual` (and `_MANUAL_EOF`) removed from `l3_llm.py`; `call_manual` import removed from `controller.py`.
- `--mock-llm` / `--manual-llm` flags and `AgentArguments.mock_llm` / `.manual_llm` fields removed from `args.py`. The Tier-2 dispatch is now a single `call_llm(...)` call; the banner shows only the provider/model.
- Dead `prior_diff` parameter and `### Your previous attempt (FAILED)` block removed from `_build_prompt` (superseded by conversation history, Fix 14).
- Unused imports removed: `re` in `l1_planner.py`, `field` in `types.py`.

**Docs:** `DOCUMENTATION.md` / `INSTALL.md` updated — removed `mock_llm.py` from the file tree, the `--mock-llm`/`--manual-llm` CLI entries and demo commands; refreshed the CLI reference (it still listed the long-removed `--distance`; replaced with `--provider`/`--api-base`/`--edit-mode`/`--restructure-depth`/`--require-speedup`); rewrote stale Known-Limitations entries (ID-based rebuild → content fingerprinting; dropped the mock-LLM note).

**Effect:** The only LLM paths are now `--provider anthropic` and `--provider openai-compat`. `pyflakes` reports no unused imports/vars; all modules import clean.

---

## Fix 33 — Surface DiscoPoP's Do-All blockers to the LLM (`prevents-doall` integration)

**Files:** `explorer/discopop_explorer/pattern_detectors/new_do_all_detector.py` (from the `new_explorer` merge), `l2_evidence.py`, `l3_llm.py`, `types.py`

**Background:** the `new_explorer` merge brought a rewritten Do-All detector that *computes the exact dependency preventing Do-All* (type, source→sink line, variable, memory region, and whether it's a trustworthy `DYNAMIC_ANALYSIS` dep or a possibly-pessimistic static one) — but only threw it away via `logger.debug("Prevents doall: …")`. Previously the agent's Tier-2 prompt could only say the generic "DiscoPoP found no applicable pattern" and dump *all* region deps for the LLM to guess from.

**Fix (three parts):**
1. **Persist (explorer):** `identify_simple_doall_and_reduction` now collects each blocker at both prevention points (the dynamic definite-breaker and the confirmed static one) via `_blocker_record(node, dep)` and writes `explorer/doall_prevented.json` (fresh each run, next to `patterns.json`). Additive, best-effort.
2. **Consume (L2):** `l2_evidence._load_prevented_deps` reads that file and returns the blockers whose loop overlaps the candidate region (or whose source/sink line falls inside it); stored on `EvidencePackage.prevented_deps`.
3. **Prompt (L3):** `_fmt_blockers` renders a `### Why DiscoPoP could not parallelize (Do-All blockers)` section in both the diff- and function-mode prompts — listing the exact dependency(ies) to break and flagging dynamic ("real, must remove") vs static ("may be resolvable by privatization").

**Verified (agent side):** with a synthetic `doall_prevented.json`, L2 matches only the region's blocker and L3 renders the precise section. Explorer edit syntax-checks.

**Activation caveat:** the installed `discopop_explorer` in the venv is the pre-merge copy, so `doall_prevented.json` is not produced until the merged explorer is (re)installed (`pip install ./explorer`, or `-e` for live edits). Reinstalling switches detection to the new task-graph-based engine, so the agent's L1 parsing of `Data.xml`/`patterns.json` should be validated against the new output. Until then the agent runs unchanged (the loader returns `[]` when the file is absent — fully backward-compatible).

---

## Fix 34 — Python 3.11 migration + macOS re-port to activate the merged explorer & prevents-doall

**Files:** environment (venv), `profiler/scripts/CXX_wrapper.sh`, `l1_planner.py`, `l3_llm.py`, `GUI/.../Viewable.py`

**Why:** the `new_explorer` merge (and Fix 33's `doall_prevented.json`) only take effect once the merged explorer is installed — but the merged code (its GUI, imported transitively) requires **Python 3.10+**, while the env was 3.9. Chosen path: upgrade to Python 3.11.

**Migration steps performed:**
1. `brew install python@3.11` + `python-tk@3.11` (Homebrew python ships without Tk; the merged explorer imports `discopop_gui` → tkinter even headless). New venv on 3.11 (old one kept as `venv_py39_backup`).
2. Reinstalled the local sources: `library`, `explorer`, `GUI` **editable**; `profiler`, `hotspot_detection` **non-editable** (build the C++ `.so`/`.dylib`). The profiler build needs `--config-settings="cmake.args=-DLLVM_DIST_PATH=/usr/local/opt/llvm@19"`.
3. Converted the one 3.10 `match` in `GUI/.../Viewable.py` to `if/elif` (defensive; explorer/library themselves are 3.9-clean).

**macOS profiler re-port (the new profiler's `CXX_wrapper.sh` lost the earlier macOS fixes):**
- Added `-isysroot $(xcrun --show-sdk-path)` so Homebrew clang finds system C headers (`printf`/`free` undeclared without it).
- `-isysroot` then links the SDK's libc++, but `libDiscoPoP_RT.a` (which now uses `std::stringstream`) needs LLVM's libc++ (`abi:ne190107`). Fixed by linking LLVM's `libc++.dylib`/`libc++abi.dylib` by full path with `-nostdlib++`, locating it robustly via `brew --prefix llvm@19` / `readlink -f` (the `clang++-19` path is a symlink, so a naive `dirname/../lib/c++` resolved to a non-existent dir and silently fell back to the SDK libc++ — the root cause of a long "symbol not found" chase).
- Re-added the `DP_PROJECT_ROOT_DIR` default (Fix 3). Patched **both** the installed wrapper and the source `profiler/scripts/CXX_wrapper.sh` so it survives future reinstalls.

**Agent compatibility with the new explorer output:**
- `l1_planner`: the new `patterns.json` may carry a null `workload`; coerce to `int` before comparing (was `TypeError: '>' not supported between NoneType and int`).
- `l3_llm._fmt_blockers`: strip enum prefixes (`DepType.RAW`→`RAW`) and, since the new detector leaves `source_line`/`sink_line` unset on these deps, fall back to "loop-carried (loop at line N)".

**Verified end-to-end on 3.11:** `discopop_cxx` instruments+runs; `discopop_explorer` produces `patterns.json` **and** `doall_prevented.json`; the agent's L1 parses it, L2 loads the blockers, and the Tier-2 prompt renders, e.g.:
`RAW on \`GEPRESULT_arr\` loop-carried (loop at line 23) [dynamic — a real, observed dependency; it must be removed]`.

**Follow-ups noted:** the new detector doesn't populate `source_line`/`sink_line` on the blocker deps (they show as loop-level) — a data-quality enrichment for later, along with the earlier #1/#2/#4 blocker enrichments (GEP/scalar + intra/inter-iteration flags, reduction candidacy, memory-region grouping).

---

## Fix 36 — Re-profile crash after Tier-2 accept: missing `discopop` meta-package

**Symptom:** the very first Tier-2 acceptance on a fresh **Python 3.11** venv reached the re-profile step and died: `discopop_explorer`'s internal call to `discopop_patch_generator` exited 1 with `FileNotFoundError: No pattern file found ... Expected pattern file: .../explorer/patterns.json`. This dropped the rest of the agent queue. Manual `discopop_explorer` runs on the same restructured source succeeded (exit 0, `patterns.json` written) — the failure only appeared inside the agent's re-profile.

**Root cause:** when I rebuilt the venv for Python 3.11 (Fix 35) I installed the sub-packages (`library`, `explorer`, `GUI`, `profiler`, `hotspot_detection`) but **not the root `discopop` meta-package**. `importlib.metadata.version("discopop")` therefore raised `PackageNotFoundError: No package metadata was found for discopop`, which cascaded during the patch-generation/version lookup inside the re-profile and surfaced as the misleading "no pattern file" error.

**Fix:** `venv/bin/pip install --no-deps .` from the repo root to register the `discopop` meta-package metadata (installs `discopop-5.0.3a1`). Not a code change — the documented install in CLAUDE.md already includes the leading `.` (`pip install . ./profiler ./library`); my 3.11 rebuild simply omitted it. Noted here so a future fresh-venv rebuild includes the root package.

**Verified:** full agentic flow on `example4/bubble_sort.cpp` against Qwen (`--edit-mode function`, `--restructure-depth 0`) now runs end-to-end: loop 1:28 Tier-1 fails at `openmp_compile` (early `break` → non-canonical) → Tier-2 Qwen removes the `break` → quality gate PASSED (compile/TSan/correctness) → **re-profile succeeds** → ACCEPTED. `SUMMARY: 1 accepted | 0 skipped`.

---

## Fix 37 — Re-profile crash: explorer picks up a STALE global `discopop_patch_generator` off PATH

**Symptom (the real one behind Fix 36's symptom):** after a Tier-2 accept, the agent's re-profile ran `discopop_explorer`, which exited 1. The explorer's own log showed:
```
/Users/ahmedsamir/.local/bin/discopop_patch_generator, line 33 ...
    __requires__ = 'discopop==5.0.2'
ValueError: Unknown task type: PARALLELREGION
subprocess.CalledProcessError: Command '['discopop_patch_generator']' returned non-zero exit status 1
```
It was **intermittent** — it only fired when the re-profile's detected patterns included a `PARALLELREGION`, a pattern type the old tool doesn't know.

**Root cause:** `discopop_explorer.py` shells out to a **bare** `discopop_patch_generator` (resolved via `$PATH`). The agent is launched as `venv/bin/python -m discopop_agent` *without activating the venv*, so `venv/bin` is **not on PATH**. `which -a discopop_patch_generator` resolved only to a stale global install at `~/.local/bin/discopop_patch_generator` (`discopop==5.0.2`, pinned to a different `Documents/DiscoPoP/.../python3.9` venv) — which shadows our venv's `5.0.3a1`. The old 5.0.2 patch_generator chokes on the new explorer's `PARALLELREGION` type. Fix 36's meta-package install was a red herring: it removed the `PackageNotFoundError` *warning* but not this failure (manual `../../venv/bin/discopop_patch_generator` worked only because it bypassed PATH).

**Fix:** `_reprofil` now spawns the cxx wrapper, `./a.out`, and the explorer with an env whose `PATH` is prepended by our venv's bin dir (`Path(sys.executable).parent`), via new helper `_venv_env()`. The explorer's internal bare `discopop_patch_generator` then resolves to our matching 5.0.3a1. Verified: `PATH=venv/bin:$PATH discopop_explorer` → exit 0, no `Unknown task type`.

**User-env note:** the stale `~/.local/bin/discopop_patch_generator` (and siblings) from the old `Documents/DiscoPoP` install still shadow the venv for any *manually*-run DiscoPoP command with the venv unactivated (e.g. the user's initial `discopop_explorer` step). The agent's own re-profile is now immune; consider removing/upgrading that global install to avoid surprises elsewhere.

---

## Fix 38 — Generalize the L3 system prompt: evidence-driven cause taxonomy + guardrails

**File:** `l3_llm.py`, `controller.py`

**Problem:**
The system prompt (`_SYSTEM_CORE`) was a cookbook keyed to *named algorithms* — bubble sort, shell sort, Jacobi, odd-even transposition. This anchored the model on recognizing an algorithm rather than reasoning from the dependency evidence, and did not generalize. It also lacked two guardrails: the LLM could "solve" a loop with a **sequential optimization** (early-termination) or by **adding a `break`**, neither of which exposes parallelism.

**Fix:**
- Rewrote `_SYSTEM_CORE` into an algorithm-agnostic method: **classify each blocking dependence by its cause, then fix the cause** — (1) storage/false, (2) reduction, (3) in-place coupling, (4) recurrence/scan, (5) non-canonical control flow, (6) mixed concerns.
- Added guardrails: **"EXPOSE PARALLELISM, not a faster serial algorithm"** (forbids early-exit shortcuts / algorithm substitution) and **"NEVER INTRODUCE new `break`/`continue`/`return`."**
- Cause 3 now carries an explicit **decide-first test** (double-buffer only if each new value depends solely on the *previous* sweep; otherwise partition/colour into ordered sub-passes) and names the `arr → temp` rename as a non-fix.
- Aligned the controller's per-stage failure feedback (`t2_hint`, `_STAGE_GUIDANCE`, the revert message) to the same cause vocabulary; converted Unicode bullets/arrows to ASCII for cross-provider consistency.

**Verified:** Claude derives the correct odd-even transposition from the generalized prompt with **no algorithm named**; the guardrails eliminated the earlier early-exit-plus-`break` answer.

---

## Fix 39 — Richer evidence for the LLM: array/scalar dep tags, DiscoPoP data-sharing classification, profiler granularity signals

**File:** `types.py`, `l2_evidence.py`, `l3_llm.py`

**Problem:**
DiscoPoP computes far more than the evidence package surfaced. The single most discriminating field — each dependence's **memory region** (`GEPRESULT` array-element vs. scalar) — was stripped in `_parse_dep_line`, so the LLM could not tell an *algorithmic* array dependence from a *privatizable* scalar and repeatedly "fixed" the loop by renaming `arr → temp` (which removes nothing). `doall_prevented.json` is also empty for the classic false-positive loop, so the "why not parallel" signal was blank exactly when it was needed most.

**Fix:**
- `Dependency` gains `kind` (`"array"`|`"scalar"`), classified from the `GEPRESULT` tag (`_classify_var`); each dep now renders as `… [array element]` / `[scalar]`.
- `EvidencePackage` gains DiscoPoP's **OpenMP data-sharing classification** (`shared` / `private` / `first_private` / `last_private` / `reduction`) from `patterns.json`, plus three profiler signals: **`loop_trip_counts`** (from `BGN loop` markers — parallel granularity), **`local_vars_in_region`** (loop-local / already-private, from the CU graph's *scope* only — `accessMode` is unreliable for arrays because a CU records the pointer access, not the element read/write), and **`static_only_vars`** (static deps never observed at runtime → likely spurious).
- `l3_llm` renders `_fmt_classification`, `_array_dep_note` (states plainly that copying/renaming an array cannot remove an array-element dep), `_fmt_trip_counts` (granularity hint), and `_fmt_extra_vars` — in **both** diff-mode and function-mode prompts, each section emitted only when its data is present.
- `static_only_vars` is compared against **globally**-observed dynamic vars (not region-filtered), fixing a bug where loop-induction variables (`i`/`pass`/`n`) — whose deps sit at the loop header just outside the body window — were wrongly flagged as spurious.

**Verified:** renders correctly on the pristine `example4` profile (`arr[] [array element]`; `shared: arr`; `loop-local: tmp`; trip counts `line 23: 1023 × ~512`). With the enriched prompt Qwen began attempting stride/partition (`i += 2`) — a shift it never made in prior runs — though the 30B model remains the capability ceiling; the `--require-speedup` gate still correctly reverts every non-solution (no false accept).

---

## Fix 40 — `--edit-mode direct`: the LLM edits the file itself instead of describing an edit

**Files:** `args.py`, `l3_llm.py`, `controller.py`, `viz.py`

**Problem:**
Both existing edit modes make the model *serialize* its change into the reply: a byte-exact unified diff (`diff`) or the whole function pasted back (`function`). `function` removed the `stage=apply` failure class, but the model still cannot look at anything outside the function it was handed, and every retry re-states the entire function just to change three lines. With `--provider claude-agent-sdk` the model already runs inside a real Claude Code session — it has file tools it was simply never given.

**Fix — a third edit mode where the answer is a file, not text:**
- **`--edit-mode {diff,function,direct}`** (default `diff`, unchanged). `direct` requires `--provider claude-agent-sdk` — the only backend with file tools — and `args.py` rejects the combination up front rather than failing mid-run.
- **Per-region workspace** (`l3_llm._sync_workspace`): a throwaway directory holding a **private copy** of the source file. `_complete_claude_agent_sdk` gets `cwd=<workspace>`, `allowed_tools=["Read","Edit","Write"]`, `permission_mode="acceptEdits"`, `max_turns=24`. The real profiled source is not reachable from that directory and its path never appears in the prompt, so no tool call can touch the project tree; `Bash` stays off.
- **The answer is the file's final content** (`_workspace_diff`): the agent reads the copy back and diffs it against the on-disk source with `difflib`. As in `function` mode the diff is built from real file content, so it always applies — the same L4 gate (apply → compile → TSan → correctness → speedup) runs unchanged. Model prose is ignored.
- **Retries are cumulative within a region**: the workspace keeps the earlier edits, so attempt *n+1* refines its own rewrite against the gate diagnostic instead of restarting from the original — which is what the resumed per-region CLI session already assumed. It is re-seeded from disk whenever the real file changed underneath (another region's patch accepted, or this one reverted), keyed on `region_fingerprint` like the session (not the reassignable `region_id`).
- **No-op handling**: an unchanged (or comment/whitespace-only) file gets two free re-prompts, then returns `""` — distinct from `None` ("no usable answer") — so the controller reports "produced no change" and sends the existing "returning the input is not a valid answer" feedback. That branch is now shared with `function` mode instead of duplicated.
- Housekeeping: the evidence body common to all three prompts factored into `_evidence_sections` / `_TASK_CHECKLIST` (was copy-pasted between `_build_prompt` and `_build_function_prompt`); `_normalize_code` moved from `controller` to `l3_llm.normalize_code` (both no-op detectors now share it); `viz` renders the model's file edit as a diff panel and distinguishes "did not edit the file" from "could not extract an edit".

**Also fixed — latent EOF-newline bug in self-generated diffs (affected `function` mode too):**
Building a diff from a source file whose last line has no trailing newline makes `difflib` emit an unterminated `-` line that runs straight into the following `+` line (`-int x;+int y;`), which the apply stage rejects as malformed. `function` mode papered over it by forcing `"\n"` onto every line — which instead produces context that no longer matches the file, so BSD `patch` rejects the hunk (verified: `1 out of 1 hunks failed`). Both modes now go through one shared builder, **`l3_llm.make_diff(old_text, new_text, path)`**, which emits the standard `\ No newline at end of file` marker (accepted by both GNU and BSD patch — verified). `l4_validator.fix_hunk_headers` skips `\`-prefixed lines when recounting, since the marker is not a line of either file and counting it corrupts the very header being fixed. Triggered whenever an edit lands within ~3 lines of EOF in a file with no final newline.

**Verified:** live `claude-agent-sdk` turn edits the workspace file and a resumed second turn builds on its own edit; offline test covers edit→applicable diff (`patch` exits 0), cumulative retry, comment-only→`""` after 2 free re-prompts, workspace re-seeding after an external source change, and rejection of `direct` with a non-tool provider.

---

## Fix 41 — Make the agent's acceptance criterion its actual purpose; add the DiscoPoP→LLM feedback channel and a benchmark

**Files:** `controller.py`, `l3_llm.py`, `l4_validator.py`, `l2_evidence.py`, `args.py`, `benchmark/*`

**Problem — the agent could report success without doing its job.**
A Tier-2 rewrite exists for exactly one reason: to let DiscoPoP parallelize code it previously could not. But the check for that (`_best_exposed_speedup`) only ran when `--require-speedup` was passed **and** the exposed loops were terminal:

```python
if (args.require_speedup and reprofile_ok and (depth + 1) > args.restructure_depth):
```

`--require-speedup` was opt-in, so by **default** a rewrite was ACCEPTED as soon as it compiled and reproduced the original output — even if the re-profile found nothing at all. Passing the quality gate only proves a rewrite is *harmless*. `SUMMARY: 1 accepted` could therefore mean "the LLM rewrote the code and nothing was parallelized". A second gap: the LLM was never told what DiscoPoP made of its rewrite, so on retry it re-reasoned from the ORIGINAL code's blockers — the one piece of evidence guaranteed to be out of date.

**Fix — verify against DiscoPoP every time, and say what it found:**
- **`_verify_rewrite()`** now runs after **every** accepted-by-the-gate rewrite, not conditionally. `_touched_span()` parses the patch's `@@` headers to get the rewritten line range, and only patterns overlapping *those lines* count — a pattern elsewhere in the file proves nothing about this rewrite. Verdicts: `ok` (pragma validated, and faster when required), `exposed` (a deeper Tier-2 pass may still improve it, so validation is deferred), `no_pattern`, `pattern_broken`, `no_speedup`, `reprofile_failed`. Anything other than `ok`/`exposed` reverts via the existing snapshot restore.
- **`_rewrite_feedback()`** turns each verdict into a different instruction, because they mean opposite things. `no_pattern` re-runs `load_prevented_deps()` against the **fresh** profile and shows DiscoPoP's Do-All blockers **for the model's own rewritten code** ("not of the original code") — this is the signal that was missing entirely. `no_speedup` explicitly tells the model the dependence is *already gone* and to stop hunting for dependences (the previous single message conflated the two and pushed models off correct transformations).
- **`--require-speedup` now defaults ON** (`--no-require-speedup` to disable), matching the project's premise that a restructuring is worth keeping only if it ends in measured speedup.
- A failed re-profile is now a revert too, instead of a silent commit with `reprofiled: false`.
- The system prompt's "THE ONE CONTRACT" section was replaced by the real four-step pipeline (compile → byte-identical output → DiscoPoP finds a pattern → its pragma is race-free and faster), stating plainly that steps 1-2 are the constraint and 3-4 are the goal, and that a correct Do-All over too few iterations is a *failed* rewrite.

**Speed — the gate's dominant cost was TSan, and it was almost all waste.**
Measured on a 0.2 s benchmark kernel, the sanitized parallel build took **37 s** (185x). Nearly all of it is spent *after* the first race is found: the default is to report and keep going, unwinding a stack for every further racing access, while the agent only ever uses the first warning block. Setting `TSAN_OPTIONS=halt_on_error=1` cut it to **0.7 s with the race still reported on 3 runs out of 3**.
Capping `OMP_NUM_THREADS=4` was tried and **rejected**: it was faster still, but the same race then went **undetected on 2 runs out of 2** on an 8-thread machine. Race detection is probabilistic, and a gate that passes because it looked less hard is worse than a slow one — so thread count is left alone and only the redundant post-report work is removed.
Also: `_measure_speedup` stops after 3 of its 5 interleaved pairs once the running median is clear of the threshold (only borderline ratios spend the full budget), and `_verify_rewrite` stops at the first qualifying pattern instead of validating them all.

**Budget — build errors no longer cost a real attempt.**
`--build-retries` (default 2) refunds the budget slot when a rewrite fails at `apply`/`compile`/`openmp_compile`. Those are mechanical fixes that say nothing about the parallelization idea; the cap keeps a model that cannot produce compiling code terminating.

**Benchmark (`discopop_agent/benchmark/`).**
Eight self-contained cases, one per cause in the taxonomy (plus a Do-All baseline that the LLM should never be asked about), and a driver that runs profile → agent → **independent re-measurement**: it compiles the original sequentially and the agent's final source with `-fopenmp` and compares wall time and stdout **itself**, so the report measures the agent rather than echoing its self-assessment. Verdicts include `BROKEN` (output differs — a gate escape, which should never appear). Two design rules keep the cases fair under a byte-identical-output contract: all cross-element accumulation is integer (FP reduction is not associative, so a *correct* parallelization would fail the correctness gate), and per-element arithmetic is schedule-independent. Cases are sized from measurement, not guesswork: the arithmetic-heavy/memory-light shape keeps DiscoPoP's profiled run near 15 s while the timed run stays long enough (~0.2 s) to resolve a 1.1x ratio. The driver passes `--min-workload 500000` because each case's small checksum loop is otherwise proposed as a candidate in its own right.

**Two further defects the benchmark exposed on its first run (both agent bugs, not case bugs):**

1. **A validated Tier-1 parallelization never reached the source file.** Tier-2 rewrites were written back, but an accepted Tier-1 pattern was only recorded in `accepted.json` with its patch left in `patch_generator/`. The benchmark's independent re-measurement showed it plainly: the agent reported `ACCEPTED (measured 5.03x)` while the final source still had **zero** `#pragma omp` and measured 0.46x. The agent's deliverable is a parallelized program, so accepted patches of either tier now land in the file via `_apply_to_source()` (shared with the Tier-2 path, same backup). `--no-apply-patches` restores the old record-only behaviour. Re-measured after the fix: **5.29x end-to-end, output identical**.

2. **The macOS OMP-barrier false-positive guard ignored globals.** `_is_omp_barrier_false_positive()` recognised only `Location is heap block ... allocated by main thread` and `Location is stack of main thread`. TSan reports `Location is global 'main::out'` for `static` arrays, so on a *correctly* parallelized Do-All over a static array the guard returned False, Tier-1 "failed", and the agent spent LLM budget restructuring code that was already right. The location clause only establishes the main-thread-vs-worker shape — the reasoning (one access inside `.omp_outlined`, the other in sequential main-thread code) is storage-class agnostic — so globals were added. Verified: the real report is now classified as a false positive, and a synthetic worker-vs-worker race over a global is still rejected.

**Verified end to end:** `doall_clean` — Tier-1 detected, OMP-barrier false positive correctly identified, validated at 4.81x, pragma applied to the source, driver's independent verdict `FASTER 5.29x` with identical output, whole case in **28 s** (the same case took over 10 minutes before the TSan fix).

---

## Fix 42 — Stop measuring the same pragma twice

**File:** `controller.py`

**Problem:**
Fix 41's verification step measures an exposed pattern to decide whether to KEEP a restructuring. One queue position later the same pattern arrives as an ordinary depth+1 candidate and the Tier-1 branch measures it **again** to decide whether to APPLY it — a full duplicate gate run for the same verdict: two compiles, a ThreadSanitizer build and run, a correctness run, and up to five interleaved timing pairs. Visible in the `fine_grained` log as the same `3.03×` printed twice, once by verification and once by Tier-1.

**Fix:**
- **`_validate_cached(cache, diff, args, …)`** — runs the gate or returns the answer already computed for that exact question, and is now the single entry point for both call sites.
- **`_gate_key()`** keys on `(patch bytes, current source bytes, skip_race_check)`. Hashing the source is what makes reuse safe: a patch measured before another region's pragma was applied says nothing about the file afterwards, and that case genuinely occurs — a rewrite that exposes two loops has the first loop's pragma applied before the second is measured, so the second correctly misses the cache and re-validates.
- The macOS OMP-barrier false-positive re-check moved inside the helper, so both callers get it identically instead of implementing it twice (it was duplicated between the Tier-1 branch and `_verify_rewrite`), and the re-checked verdict is what gets cached — a hit never has to redo it.
- The cache is a local in `run()`, not a module global, so nothing leaks between runs.
- Tier-1 now prints `Reusing the verification result for this patch (accepted, 3.03×) — gate not re-run` on a hit, so the log never implies a check ran when it didn't.

**Verified:** unit test counts real `validate()` calls through a stub — repeat asks reuse the result, a changed source file invalidates the hit, `skip_race_check` is keyed separately, and the barrier re-check is cached as one unit.

---

## Fix 43 — Fix the two oracles: attributable speedup, and correctness on more than one input

**File:** `l4_validator.py`, `controller.py`, `args.py`

Both of the agent's oracles were weaker than the decisions resting on them.

**Problem 1 — the speedup ratio was not attributable to the parallelism.**
`_measure_speedup` compared two DIFFERENT BUILDS: the source without `-fopenmp` against the source with it. `-fopenmp` changes codegen and layout, so part of every ratio came from the compiler rather than from the pragma. Near the 1.1x threshold that decided accept/reject, the noise swamped the signal — the same pragma on `fine_grained` measured **0.89x on one run and 1.10x on the next**, straddling the cutoff, so the verdict was partly a coin flip.

**Fix:** measure ONE binary under `OMP_NUM_THREADS=1` and then unrestricted. Identical machine code on both sides, so whatever changes is the parallelism. Measured on the same kernel, 7 interleaved repetitions each:

```
OLD  seq build vs par build : median 5.69x  range 1.57-5.87  spread 76%
NEW  same binary, 1 vs N    : median 5.70x  range 5.19-5.91  spread 13%
```

Same median — the old instrument was unbiased, just noisy — with the spread cut by a factor of six, and the 1.57x outlier (the kind that flips a threshold decision) gone. The correctness stage's `-O2 -fopenmp` build is now reused for the timed runs, so the gate compiles this source **once** instead of three times, and `ThreadPoolExecutor` is no longer needed.

**Problem 2 — semantic equivalence was proven on a single input.**
Correctness compared stdout for exactly one argv, so a rewrite correct at the profiled size and wrong at 0, 1, or an odd count passed — precisely the "bound carried over from the old schedule" failure the L3 prompt warns about. The benchmark cases even had to be *designed around* the oracle (integer checksums, because FP reduction reassociation would fail a *correct* parallelization).

**Fix:** `--check-input` (repeatable) records extra argument vectors from the ORIGINAL program, and the correctness stage replays every one of them. Inputs the original cannot run cleanly are dropped with a warning rather than failing the run. When only one input is in play the startup banner says so explicitly, so a thin check never looks like a thorough one. A failure on a non-profiled input gets its own diagnostic naming the input and the likely cause.

**Verified** with a rewrite whose partition bound is right for even `n` and wrong for odd `n` (correct at 0, 1, 2, 8, 1000; wrong at 7, 999):

```
1. one input  (n=1000)          -> accepted     passed=True     <- fooled
2. four inputs (adds 999, 1, 0) -> correctness  passed=False    <- caught
3. correct rewrite, four inputs -> accepted     passed=True     <- no false positive
```

**Known gap:** the benchmark cases hard-code their problem size and take no argv, so they cannot exercise `--check-input` yet; giving them a size argument is the natural follow-up.
