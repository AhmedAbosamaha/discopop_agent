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

---

## Fix 44 — `discopop_cxx` APPENDS to every artifact: three profiles into one directory merged into one corrupt analysis

**File:** `profiling/runner.py`, `benchmark/refresh_depth.py`

**Problem:**
`discopop_cxx` appends to every artifact it writes and never truncates. Profiling into a directory that already held an analysis **merged the two**. Measured on **one unchanged source**, three profiles into the same directory:

| artifact | 1st | 2nd | 3rd |
|---|---|---|---|
| `Data.xml` | 444 | 888 | 1332 |
| `instructionID_to_lineID_mapping.txt` | 90 | 180 | 270 |
| `static_dependencies.txt` | 23 | 46 | 69 |

Every re-profile the agent performed, and every profile the benchmark harness took, was reading a superset of two or more runs.

**Fix:**
`_reprofil` and `_reprofil_fast` both `shutil.rmtree` the `profiler/` directory before the compile. `benchmark/refresh_depth.py`'s `_full_profile` does the same. `reduction.txt` moved out of `_RUN_ARTIFACTS` into `_COMPILE_ARTIFACTS` — the compile writes it correctly for the new source, so preserving the old one was wrong.

**Effect — and why this is the most important entry in this file:**
The corruption **flattered**. One benchmark case scored a perfect 6/6 and revealed **five** unsafe divergences once the fix was in. Corruption that penalised would have been noticed immediately; corruption that improves the score looks like success.

**Every measurement taken before this fix is void.** The measuring instrument shared a defect with the subject it was measuring — which belongs in the thesis's threats-to-validity chapter, stated plainly.

---

## Fix 45 — `remap_dependencies` dropped the observed rows (71% of the data)

**File:** `profiling/fast_refresh.py`

**Problem:**
Dependence rows carrying a **bare instruction id** — no `@callpath-state` suffix — were treated as unparseable and dropped. They are not malformed: they are the **observed** rows, about 71% of the file. They have zero overlap with `static_dependencies.txt`, and that file does not exist at all after a compile-only build, so nothing else covered them.

A fast refresh was therefore discarding most of the dynamic evidence it existed to preserve.

**Fix:**
Added `_BARE_INSTR = re.compile(r"^\d+$")`. `endpoint()` and `endpoint_line()` translate bare ids like any other. The statistic was renamed `deps_bare_id` and is reported in `RemapStats.summary()` rather than hidden — a refresh that silently dropped most of the profile would otherwise look identical to one that worked.

---

## Fix 46 — Settle's re-gate compared timings with a bare `>`, so it failed on identical source 5 times in 8

**File:** `phases/settle.py`

**Problem:**
The final whole-file re-gate compared `t_final > reference_time` with **no tolerance at all**. Ordinary timing wobble was read as a regression.

**Verified:** on completely unchanged source, **5 false failures out of 8**, with ratios 0.961–1.010. The verdict was close to a coin flip.

**Fix:**
`if t_final > reference_time / _MARGINAL_NOISE:` — the same measured-noise principle the correctness gate already used for numbers, applied to the clock.

---

## Fix 47 — `--evidence`: making the agent's own premise testable

**File:** `args.py`, `llm/render.py`

**Problem:**
The premise of the whole agent is that DiscoPoP's evidence helps a model parallelize. Nothing in the tool could test that claim, because the evidence could not be turned off.

**Fix:**
`--evidence` gates the nine sections named in `EVIDENCE_SECTIONS` (`deps`, `reductions`, `classification`, `extra_vars`, `array_note`, `loop_nest`, `calls`, `blockers`, `failure`) via `_evidence_sections(ev, deps_header, include=None)`. `full` (default), `none`, a comma list to **select**, or `-name` entries to **subtract** — the subtract form needs `--evidence=-a,-b` since a leading dash is otherwise read as a flag.

**Measured:** the evidence block is **48% of the prompt** — 3748 characters at `full`, 1986 at `none`.

**Trap, documented in the help text:** `failure` is the **gate's** diagnostic, not DiscoPoP's, so a no-evidence run still receives empirical feedback about why its last attempt was rejected. Pair the ablation with `--budget 1` to isolate the two variables.

Also added `--allow-unverified`: the run now **aborts** when the original program cannot be built or run, instead of continuing with the correctness gate silently switched off. Continuing is still possible, but only as an explicit opt-in with a loud warning.

---

## Fix 48 — `--llm-deps` defaults to OFF

**File:** `args.py`

**Problem:**
`--llm-deps` followed `--fast-refresh`, so it was on in the default configuration. It is the only place a model's claim **edits DiscoPoP's analysis** rather than being tested against the program, and it only ever *deletes* — the unsound direction, where a wrong judgement produces a racy loop.

It also rarely pays for itself. A fast refresh saves only the instrumented run — measured **8.6 s** on `prefix_sum` and **7.9 s** on `array_accumulator` — and one LLM call per kept rewrite usually costs more than that. Slower *and* less sound.

**Fix:**
The flag now parses to `None` and resolves to `False`. It is kept behind the flag so runs with and without it can be compared and reported, and it still errors when asked for explicitly without `--fast-refresh`. `--llm-pragmas` is the sound channel for the same judgement: the model writes the pragma and the gate has to be convinced.

---

## Fix 49 — `--llm-recon`: closing the refresh's gap by ADDING dependences

**File:** `llm/dep_reconstruct.py` (new), `llm/prompts.py`, `phases/phase_a.py`, `args.py`

**Problem:**
A fast refresh cannot carry a dependence whose endpoint sits in code the rewrite *created* — that code did not exist when the program last ran. **Measured across two chains: 39 of 39 dependences a full profile has and a refresh lacks have an endpoint on a rewritten line, and NONE were carryable.** That is the entire remaining gap.

**Fix:**
The model reports the dependences in the code it just wrote, in the opposite direction to `--llm-deps` — it **adds**, which is the conservative direction. Three rules keep it honest:

- **Source terms only.** `LOOP <line> <RAW|WAR|WAW> <var> <writer-line> <reader-line>`, or `LOOP <line> NONE`. The model never sees or emits an instruction id, callpath state or memory region — those are compiler-internal and pointer-derived, and a model guessing them would be fabricating identity, not reporting dependence.
- **Resolution by lookup, never guessing.** A claimed variable is resolved against the dependence files of *this* build. A claim that does not resolve is dropped and counted, not approximated.
- **Rows are MERGED per sink, not appended.** Verified the hard way: appending a full profile's 60 rows produced **zero** change in the explorer's output, because an appended row is silently shadowed by the existing row for that sink.

`--llm-recon-mode` picks when to ask. `followup` (default) is a fresh turn on the **same session** after the gate passed, so the model still has its own code in view and the refreshed instruction mapping already exists; only kept rewrites cost a request. `folded` appends the ask to the rewrite prompt for no extra request at all. The `followup` prompt carries a warning with no counterpart in `folded`: the model knows its rewrite passed TSan by then, and *"no race was found, so there is no dependence"* is exactly wrong for a pragma-free rewrite — TSan ran on code with no pragma, running sequentially, so its silence is not evidence.

**Verification is containment, not proof.** Over-claiming is safe by construction (a wrong added dependence costs only a missed parallelization). The failure that hurts is **omission**, and nothing at run time can catch it — the premise is that the program was not run. The partial check is `contradictions()`: static analysis is over-approximate, so a dependence it records for a loop the model called independent is the shape of a dangerous omission. It **detects, it does not decide** — nothing is blocked on one.

**`_not_carried` is what makes that check usable.** Unfiltered it fired on induction variables and body locals — all four loops in a two-loop test. Filtered: 4 → 0.

**Measured:** control arm **4 unsafe divergences / 9 comparisons** (zero variance over 10 repeats); reconstruction arm **1**, identical across 3 repeats, repairing the **same three** comparisons each time.

`--llm-recon` and `--llm-deps` are mutually exclusive — they move the analysis in opposite directions — and both require `--fast-refresh`.

---

## Fix 50 — Harness: the chained arm was never seeded, and a trip-count rule was added then removed

**File:** `benchmark/refresh_depth.py`, `profiling/fast_refresh.py`

**Problem 1 — the seeding bug produced four wrong diagnoses in a row.**
`fast-llm` is a **chained** arm; the stepped arms were reset from `full` before each step and it was not. The resulting divergence on `prefix_sum` loop 27/28 was diagnosed in turn as a lost dependence, then trip counts, then corrupted profiles, then model over-reporting. All four were wrong. The cause was the missing seed.

**Fix:** both stepped arms are reset from `full`. `_edges` no longer excludes bare-id rows (see Fix 45), and `_full_profile` clears the profiler directory (see Fix 44). The harness now passes `source_lines` and `audit_path` through to `reconstruct` — without `source_lines` the contradiction filter cannot run, and an earlier reported figure of "18 contradictions" was noise from exactly that.

**Problem 2 — a fix that was measured and then reverted.**
A trip-count **span** rule was added to `remap_loop_counters` so counts could survive re-indentation. It dropped counts over a re-indented brace and made trip problems **worse** (8 → 12). Relaxed to semantic lines, then **removed entirely** when a clean-baseline measurement showed zero effect either way.

`remap_loop_counters(text, lmap)` is header-only, deliberately, with a note in the source recording the failed experiment so it is not re-attempted. `remap_reduction` is marked as no longer used by the fast refresh.

---

## Fix 51 — C sources are built and profiled as C; LLVM 20 and its archer on the evaluation server

**Files:** `gate/toolchain.py`, `gate/patching.py`, `gate/tsan.py`, `profiling/tools.py`, `profiling/runner.py`, `profiling/__init__.py`, `plan/impact.py`, `profiler/scripts/CC_wrapper.sh`, `hotspot_detection/scripts/CC_wrapper.sh` (and their installed copies in the venv)

**Problem 1 — the agent was C++-only by accident.**
`--source-file` is documented as "C/C++" and the prompts say "C/C++ programs", but every build went through `_find_clangpp()` and every profile through `discopop_cxx`. `clang++` accepts a `.c` file and compiles it **as C++**, so a C program was either rejected (implicit `void*` conversion, `restrict`, identifiers such as `new`) or silently analysed as a different language. Measured on PolyBench `seidel-2d` at SMALL, one profile each: DiscoPoP reports **4** `do_all` for the C++ translation and **7** for the C original. The benchmark suites the thesis evaluates on (PolyBench, NPB, most of Rodinia) are C.

**Fix:** the language is taken from the file extension at the few places that build or instrument.
- `toolchain.is_c_source`, `compiler_for(source, clangpp)` (clang for `.c`, never a silent fall-back to clang++), `link_flags_for(source)` (`-lm` for C; LLVM's libc++ on macOS for C++ as before).
- `patching._compile`, `patching._compile_variant` and `tsan._tsan` — the only three places a gate compile command is built — use them, so every stage (compile, OpenMP build, TSan, timing, noise floor, Settle) follows.
- `tools._wrapper_for` picks `discopop_cc`/`discopop_cxx`; `runner._reprofil` and `runner._reprofil_fast` use it; `impact.run_hotspot_detection` picks `discopop_hotspot_cc`/`discopop_hotspot_cxx`.

**Problem 2 — the C wrapper scripts never got the macOS fixes.**
Fixes 2–3 and the hotspot-detection fixes (Fix 38-era) were applied to both `CXX_wrapper.sh` files only. On macOS `discopop_cc` failed with `'stdio.h' file not found` (no SDK sysroot) and `discopop_hotspot_cc` loaded `/LLVMHotspotDetection.so` (GNU-only `readlink -fm`, `.so` hard-coded).

**Fix:** ported the same blocks into both `CC_wrapper.sh` sources — SDK sysroot, LLVM's libc++ in place of `-lstdc++` (the runtime libraries are C++ built against it), symlink-safe script path, `.dylib` plugin fallback, `DP_PROJECT_ROOT_DIR` default. All platform-specific parts are inside `uname == Darwin`; on Linux the scripts run exactly as before. Installed copies replaced; INSTALL.md §4 updated.

**Problem 3 — the evaluation server's toolchain.**
The candidate list tried `clang++-19` before anything else available there, and that clang-19 has no `omp.h` (`libomp-19-dev` absent), so every OpenMP build would fail. `find_archer` did not look under `/usr/lib/llvm-20/lib`, where the server's archer is, so TSan would have fallen back to the barrier heuristic.

**Fix:** `clang++-20`/`clang-20` are tried before 19 (the macOS Homebrew keg path stays first); `DP_CXX`/`DP_CC` override the search; `/usr/lib/llvm-20/lib/libarcher.so` and `/usr/lib/llvm-19/lib/libarcher.so` added to the archer candidates.

**Verified (macOS, LLVM 19):**
- mypy: 82 errors before, 82 after, none in changed lines.
- A C OpenMP program with an implicit `void*` conversion passes `_compile`, `_compile_variant` (runs, correct output) and `_tsan` (clean) — the identical `.cpp` copy fails to compile, as it should.
- `_reprofil` on PolyBench `seidel-2d.c` through `discopop_cc`: OK in 17.7 s, 416 dynamic dependence rows, 7 `do_all`. Hotspot detection through `discopop_hotspot_cc`: OK, `Hotspots.json` written.
- Feature suite (C++ paths unchanged): **16 passed, 0 failed, 0 skipped**, archer active.

Not yet verified: the LLVM-20 selection and archer path on the server itself (to be checked when the checkout there is synced).

---

## Fix 52 — The speedup gate can time the computation instead of the whole process

**File:** `gate/timing.py`

**Problem:**
Every timing in the gate was whole-process wall-clock: allocation, initialisation, the computation and output. At the small problem sizes the agent profiles and gates at, the computation can be a small share of that — PolyBench `2mm` at MINI spends 69 µs in its kernel inside a process that takes milliseconds. A real kernel speedup is diluted by work no pragma can touch, and a correct parallelization can be rejected as `no_speedup`. Benchmark suites time the kernel for this reason (PolyBench's own `POLYBENCH_TIME` convention).

**Fix:**
A program may report its computation time on stderr as `DP_TIMED_REGION_SECONDS <seconds>`. `_elapsed()` returns that (summed if reported more than once) and falls back to wall-clock when the line is absent. It is used at the only two places the gate measures time: `_run_timed` (therefore also the reference time, `time_source`, `noise_floor`, `measure_marginal`) and the interleaved pair loop of `_measure_speedup`. stdout is untouched, so output comparison is unaffected.

Nothing changes for a program that does not print the line. The harness's PolyBench packaging (generator v4) prints it around the kernel. A rewrite that deletes the markers is timed on wall-clock against a kernel-timed reference and looks slower — rejected, the conservative direction. A rewrite that *moves* work out of the timed region is not caught here; the harness records whole-program speedup alongside kernel speedup and flags a kernel gain the program does not share.

**Verified:** mypy 82 → 82 (no new errors). All 30 packaged PolyBench kernels (v4) print exactly one `DP_TIMED_REGION_SECONDS` line and still reproduce the original output byte for byte. Feature suite: **16 passed, 0 failed, 0 skipped**.

---

## Fix 53 — Every gate candidate and every model call's token usage are recorded

**Files:** `phases/report.py`, `phases/phase_a.py`, `phases/phase_b.py`, `llm/providers.py`

**Problem:**
Two things an evaluation needs were not recorded. (1) `accepted.json` keeps only what survived, and Phase A overwrote `region_*_tier2.patch` with the last passing diff — every rejected candidate was lost. The gate can therefore not be evaluated as a classifier (how often it rejects a correct change or accepts a wrong one): the rejections are the data. (2) The SDK's `ResultMessage` carries `usage`, `model_usage`, `total_cost_usd` and `duration_ms`, and the agent discarded them, so cost could only be reported in wall-clock and call counts.

**Fix:**
- `report._record_candidate(output_dir, entry, diff, dry_run)` writes `candidates/NNNN.patch` and one line in `candidates.jsonl`: phase, region, verdict, stage, diagnostic (first 2,000 chars), measured speedup, barrier re-check. Called after every Phase A gate verdict (model rewrites, including the controller's own clause stage) and at both Phase B decision points (DiscoPoP pragmas: static clause check and `_validate_cached`). A dry run writes nothing.
- `providers._record_usage(...)` appends one JSON line per call to `$DP_LLM_USAGE_LOG` when that variable is set (the experiment harness sets it per trial); unset, nothing is written. Hooked into the `claude-agent-sdk` result and the `openai-compat` response. Best-effort: it cannot raise.

Neither changes a decision; both only write files.

**Verified:** unit test without a model — two usage records summarised correctly (2,000 input / 400 output tokens, $0.0052); two candidates written with index lines, a dry-run call writes nothing. Harness side (`_summarise_usage`, `candidates_recorded`) type-checks.

---

## Fix 54 — Model calls went to cold regions: measurements matched nothing, and nothing kept cold regions out

**Files:** `run.py`, `plan/scoring.py`, `args.py`, `phases/phase_a.py`, `phases/phase_b.py`

**Problem 1 — hotspot measurements silently matched no region.**
Hotspots are keyed by (file id, line), and DiscoPoP assigns file ids by **absolute path** in `.discopop/FileMapping.txt`. When the profile was taken in one directory and the agent runs in another (the experiment harness copies the profile into each trial; a server checkout does the same), the agent's hotspot detection registers the source again as a **new file id**. Every measurement then carried file id 2, every region file id 1, and ranking fell back to the static workload proxy while the banner still said "ranking by predicted time saved". Reproduced on the seidel-2d smoke profile: 15 measurements, 0 of 19 regions matched; with the mapping pointed at the copy, 14 of 19 matched. In the smoke trial this spread 35 model calls over 11 regions — `xmalloc`, `init_array`, `print_array` and small helpers received as many attempts as the kernel.

**Fix:** `run.py` now warns loudly when measurements exist but match no region. (The harness fixes the mapping in each trial copy.)

**Problem 2 — ranking only ordered the queue; every region was still attempted.** `--min-impact` defaults to 0, and it is in seconds, which depend on the problem size profiled at.

**Fix:** `--min-runtime-share F` skips any region below fraction F of the measured runtime and, when hotspots were measured, any region the detector did not report at all (instead of competing on the proxy). `--exclude-functions a,b,…` removes named functions and every region inside them — for code outside the computation under study, such as a benchmark's output and setup routines. Both default to off: the agent as shipped behaves exactly as before.

**Verified:** mypy 82 → 82. On the seidel-2d smoke profile: without filters 19 candidates (14 measured); `--min-runtime-share 0.05` → 9; plus the packaging's exclusions (`print_array`, `init_array`, allocators, digest/timer helpers) → 5: `main`, `kernel_seidel_2d` and the kernel's three loops. Model restructuring can now reach 2 regions instead of 11. Feature suite: **16 passed, 0 failed, 0 skipped**.

**Known, not changed:** `main` still ranks first (100 % of runtime): the function-demotion rule only fires when one loop inside carries ≥ 90 % of the function's time. Left as tuned earlier; the server pilot measures how many calls it costs.

## Fix 55 — The speed check can time a larger size than the one profiled and checked

**Files:** `args.py`, `run.py`, `gate/timing.py`, `gate/validate.py`, `phases/phase_b.py`, `phases/settle.py`, `benchmark/test_features.py`

**Problem.** Every timed build used the same source and size as profiling and the correctness checks. For programs whose size is fixed at compile time (PolyBench's dataset macros), that size is chosen small so DiscoPoP's instrumented run stays affordable — and there the computation is too short to time. Measured on the evaluation server: at SMALL the serial kernels take 0.06–15 ms (2mm 3 ms, lu 0.7 ms, trisolv 0.06 ms), below the cost of starting an OpenMP thread team, so the performance stage judged noise and rejected correct rewrites (10 such rejections in the seeded smoke trial). The only alternative was `--no-require-speedup`, which removes the check that keeps changes that do not pay off out of the program.

**Fix:** `--timing-cflags FLAGS` (write it as `--timing-cflags=-DLARGE_DATASET`). The flags are added only to the builds that are timed: the gate's performance stage builds a separate `check_timing` binary of the same patched source (every correctness stage still uses `check_par`); Phase B's noise floor and marginal measurement; Settle's final timing; and the timed reference build, so the net-regression baseline comes from the same size (the reference *output* still comes from the plain build). A timing build of the original that fails is fatal rather than silently dropping the speed baseline. Empty by default and used only with `--require-speedup`: the agent as shipped behaves exactly as before.

**Verified:** mypy 82 → 82. New feature check `timing-size`: a probe reports a fixed timed region (0.001 s without the flag; 0.5 s sequential and 0.25 s parallel with it), so the result is deterministic — the reference time moves 0.001 → 0.5 s; `time_source`, `noise_floor` and `measure_marginal` receive the flags (a flag that makes the build `#error` fails them); the gate measures 2.0× and accepts with the flag and rejects at `performance` without; a correctness-only gate run with the breaking flag still passes, so no correctness build takes it. Feature suite: **18 passed, 0 failed, 0 skipped** (with Fix 56).

## Fix 57 — mypy: 82 errors down to zero

**Files:** annotations in 24 files across the package; one variable renamed in `plan/scoring.py`

**Problem.** The project's mypy configuration sets `disallow_any_generics`, and the package carried a standing baseline of 82 errors: 78 "Missing type arguments for generic type" (a bare `dict`, `list`, `set`, `tuple`, `re.Match` or `subprocess.CompletedProcess` in an annotation) and 4 in `plan/scoring.py`, where one local variable `key` held a string for the loop-count lookup and a `(file_id, start_line, end_line)` tuple for the deduplication dictionary a few lines later — legal at runtime, but it left mypy reporting the dictionary's key type as wrong. A baseline of 82 is not free: every change had to be checked as "82 → 82" instead of "no errors", so a new error of the same kind would have been invisible.

**Fix:** type parameters written at each site, taken from the call sites rather than filled in with `Any` where the type is evident — `binary_args: List[str]`, reference outputs `List[Tuple[List[str], str]]`, `dep_region: Tuple[int, int, int]`, JSON-shaped records `Dict[str, Any]`, `re.Match[str]`, `subprocess.CompletedProcess[str]`; `Any` only where the element type genuinely varies (message lists, change-log entries). In `plan/scoring.py` the second use is renamed to `span`. Annotations only — every file already has `from __future__ import annotations`, so nothing is evaluated at runtime.

**Verified:** mypy 82 → **0 errors in 55 source files**. `python -m discopop_agent --help` runs. Feature suite: **18 passed, 0 failed, 0 skipped**. From here a new type error is visible as such, and the rule for future work is "mypy stays at zero" rather than "do not add to 82".

## Fix 56 — On macOS, a candidate that includes `<omp.h>` could not build

**Files:** `gate/patching.py`, `gate/tsan.py`, `benchmark/test_features.py`

**Problem.** OpenMP builds on macOS linked Homebrew's libomp (`-L/usr/local/opt/libomp/lib` plus rpath) but never added its headers, and LLVM 19 from Homebrew ships no `omp.h` of its own. Any candidate calling an OpenMP runtime function — `omp_get_thread_num`, `omp_get_wtime`, `omp_get_max_threads` — failed at `openmp_compile` with `'omp.h' file not found`, reported as if the model had written invalid code. Found while testing Fix 55, whose first probe included `omp.h`. The existing feature checks never included it, and neither do the packaged benchmarks, which is why it stayed hidden. Linux is unaffected: the path does not exist there, and LLVM 20 on the server finds its own `omp.h`.

**Fix:** where the libomp library directory is added, its sibling `include` directory is added too (`-I/usr/local/opt/libomp/include`), in both the gate's compile helper and the ThreadSanitizer build.

**Verified:** before the fix, the probe built without `-fopenmp` and failed with `-fopenmp` (`'omp.h' file not found`). New feature check `omp-include`: a C and a C++ program that include `<omp.h>` build with `-fopenmp` and run. mypy 82 → 82. Feature suite: **18 passed, 0 failed, 0 skipped**.

## Fix 58 — A rejected credential was reported as a clean run with no changes

**Files:** `llm/providers.py`

**Problem.** The first server pilot finished in four minutes, spent zero tokens, produced no candidate, and recorded the outcome `no-change` — in `trial.json` indistinguishable from the agent correctly deciding a kernel needed no restructuring. In fact **all nine of its model calls had failed**: the OAuth token was invalid and the API answered 401 every time.

Three faults let that pass for a result:

1. **The CLI signals an auth failure as a success.** It emits a result message with `is_error: true`, `subtype: "success"`, `api_error_status: 401` — and exits **0**. The reason lives only in the result body (`Failed to authenticate. API Error: 401 OAuth access token is invalid.`).
2. **The SDK's exception dropped the reason.** When the CLI exits non-zero, the SDK replaces its `ProcessError` with `Claude Code returned an error result: <text>`, where the text is `"; ".join(errors)` or, when that is empty, the **subtype** — which is `"success"`. Every failure, whatever its cause, therefore produced the identical and self-contradictory string `Claude Code returned an error result: success`. A local smoke run logged 10 such lines among 35 calls and they could not be told apart from these.
3. **The agent retried, then carried on.** `_complete_claude_agent_sdk` retried three times and re-raised; Phase A caught it as "a bad attempt, not a broken run" and moved on — the right rule for a flaky call, the wrong one for a credential that fails identically on every region. Nine calls became three exhausted budgets, three skipped regions, and a clean-looking run.

**Fix:** the result body is read where it exists. `_run` inspects the `ResultMessage`: when `is_error` is set it records the body, **leaves the stream**, and calls `_raise_for_result` — breaking out rather than raising into the suspended async generator, which would make the generator's own close fail (`aclose(): asynchronous generator is already running`) and print a second, irrelevant traceback over the real error. `_raise_for_result` classifies the text: an authentication failure (`_AUTH_MARKERS`: `oauth token is invalid`, `api error: 401/403`, `invalid api key`, …) raises `LLMConnectionError`, which the retry loop re-raises untouched and Phase A already treats as fatal for the whole run; anything else raises `RuntimeError` carrying the CLI's own wording and is retried as before. A broken credential now aborts on the first call; a transient fault still costs one attempt; both name their cause in the log.

**Verified:** with the invalid token and an isolated `CLAUDE_CONFIG_DIR`, the call fails in ~2 s with `LLMConnectionError: Claude Code could not authenticate: Failed to authenticate. API Error: 401 OAuth access token is invalid. … Create a new one with 'claude setup-token'`, no retries and no spurious traceback — where before it retried three times and reported `error result: success`. mypy **0 → 0**, feature suite **18 passed, 0 failed, 0 skipped**.

The success path was re-checked against a working credential, because the fix adds code to it: one call returned `'banana'` in 6.1 s and wrote a usage record of `input_tokens=10, output_tokens=66, cache_read=9517, cost=0.0092` — the first direct confirmation that token accounting populates at all, the pilot's zeros having been a consequence of every call failing rather than a fault in `_record_usage`. The two failure modes are also distinguishable now where they were not before: a rejected credential reports `401 OAuth access token is invalid` and a missing one reports `Not logged in · Please run /login`, both previously collapsing to the single string `Claude Code returned an error result: success`.

Companion changes outside this repo: the harness records `llm_call_failures` per trial (in `trial.json` and as a `trials.csv` column), and `job.sh` refuses to start a campaign whose credential cannot answer one probe call.

## Fix 59 — `--exclude-functions` matched nothing in C++ programs

**Files:** `plan/regions.py` (new `demangle`), `plan/scoring.py`, `evidence/context.py`, `benchmark/test_features.py`

**Problem.** DiscoPoP writes C++ function names into `Data.xml` mangled — `_Z10initializeiiPdPiS_S_S_`, `_ZL7pb_emitd` for a file-local `static` function, `_ZN2ns6nestedEPii` for a namespaced one — and `build_candidates` compared them unchanged against `--exclude-functions`, which names functions as the source does (`initialize`, `pb_emit`). On every C++ program the list therefore excluded nothing, silently. Found while measuring runtime shares for the seven packaged applications, all C++: for `burkardt/md` the agent's queue held 26 candidates where the packaging meant 13, including `initialize`'s six loops and the harness's own `pb_emit`, `pb_seed`, `pb_uniform`, `pb_report` and timer functions. The C pilots could not show it. The evidence path had its own `_demangle`, but it understood only `_Z<len><name>`, so `_ZL…` and `_ZN…E` names also reached the model's prompt mangled.

**Fix:** `plan.regions.demangle` returns the innermost identifier of an Itanium-mangled name (handles `L` internal linkage, `N…E` nesting with cv-qualifiers, `St`, and ABI tags such as `B8ne190107`) and leaves C names unchanged. The exclusion compares both the raw and the demangled name. `evidence.context._demangle` now delegates to it. Region names are otherwise unchanged, so the region fingerprint that keys model sessions is unaffected.

**Verified:** 11 name cases, including a `std::__1::__math::pow` template with an ABI tag, all give the plain name. On `md`'s own profile the queue shrinks from 26 to 13 candidates, and exactly the listed functions and their loops leave it. New feature check `exclude-cxx`: a C++ probe with a `static` helper, a namespaced function and a plain one. The first two are excluded by plain name, the third stays. It **passes with the fix and fails with the old comparison restored**. mypy **0**.

## Fix 60 — A crash of DiscoPoP's explorer was treated as a verdict on the code

**Files:** `profiling/tools.py` (new `run_explorer`), `profiling/runner.py`, `phases/phase_a.py`, `llm/dep_review.py`

**Problem.** DiscoPoP's pattern explorer is not deterministic on a fixed profile. Measured by profiling a program once and running only `discopop_explorer` on that same profile again and again:

- **2mm, 10 runs:** 10 different `patterns.json`. Do-All stayed at 21 every time, while task patterns ranged from 6 to 57, and 2 reduction patterns appeared in some runs only.
- **Rodinia `pathfinder`, 20 runs:** 15 crashed with `IndexError: string index out of range` in `TaskGraph.recursive_assignment` (`loopstate_info[loopstate_position]`, an unchecked string index); 5 succeeded.
- **Fixing `PYTHONHASHSEED`** (0 or 7, five runs each) changed neither result. The variation is not string-hash randomisation.
- **Likely cause** (not proven): the task-graph code keeps sets of `Context` objects, which have no `__hash__` of their own, so they hash by memory address and are walked in a different order on every run.
- **No switch avoids it:** the task graph is built on every run, whichever patterns are requested, and the Do-All/reduction detector uses it too.

The agent runs the explorer at four places, and none of them retried:

1. the full re-profile after a kept rewrite (`_reprofil`), where a crash means `reprofile_failed` and the rewrite is reverted unless the model annotated it;
2. the fast refresh (`_reprofil_fast`);
3. the re-exploration after reconstruction (`--llm-recon`);
4. the dependence review (`--llm-deps`), which then threw its result away.

In each case a random crash of the comparison tool was treated as a property of the rewrite. On `pathfinder`, three out of four such decisions would have gone against the code for no reason.

**Fix:** `profiling.tools.run_explorer` runs the explorer and, on failure, clears only the explorer's own partial output and runs it again on the **unchanged** profile, up to `EXPLORER_ATTEMPTS` = 20 times. Each retry is printed (`[explorer] attempt N failed (...) — retrying on the same profile`). At a 75 % crash rate, 20 attempts leave a 0.75²⁰ ≈ 0.3 % chance of losing the step. All four call sites use it.

DiscoPoP itself is deliberately not patched. It is the baseline the agent is compared against, and a retry changes nothing about its analysis: it only draws another of its outputs, as a user re-running it would.

**Verified:** mypy **0**. On the `pathfinder` profile, three calls of `run_explorer` all succeeded, after 5, 2 and 4 attempts, with every retry logged. The harness counts the retries per trial (`explorer_retries` in `trial.json` and `trials.csv`) and applies the same policy to its own once-per-run profile (`explore_attempts`, `explore_failures`).

## Fix 61 — A region already covered by an accepted rewrite still received a full model budget

**Files:** `plan/scoring.py`, `benchmark/test_features.py`

**Problem.** When a region is parallelised, `ImpactModel.mark_covered` records its span, and every region nested inside it then has a predicted saving of exactly 0: the time is already won. `build_candidates` dropped a measured region only when its saving was *below* `min_impact`, whose default is 0, so a saving of exactly 0 passed. Each covered region, for example the inner loops of an accepted outer loop, therefore went on to use the full `--budget` of model calls with nothing left to gain.

This is separate from `--restructure-depth`, which decides whether regions *created or revealed* by a kept rewrite may be rewritten in turn. The covered regions here were in the queue from the start (depth 0), so depth never stopped them.

**Fix:** a measured region whose predicted saving is ≤ 0 is dropped from the queue before the `min_impact` test. This applies to Phase A and Phase B alike, since both build their queues with `build_candidates`. Regions without a measurement are unaffected.

**Verified:** new feature check `covered-skip` on the `priority_mix` profile. Covering the outer loop (lines 20–24) removes the 2 regions inside it and keeps the 3 outside. The check **fails with the old comparison restored** (1 passed, 1 failed) and passes with the fix. `impact` and `min-impact` still pass. mypy **0**. Decision D2 in the harness's thesis record (§5d).

## Fix 62 — Model attempts can follow a region's share of runtime (`--budget-policy share`)

**Files:** `args.py`, `plan/scoring.py` (new `region_budget`), `plan/__init__.py`, `phases/phase_a.py`, `phases/report.py`, `benchmark/test_features.py`

**Why.** Every region reaching the model got the same `--budget` of attempts, so a loop at 2 % of runtime cost as much as the kernel at 90 %. The author asked for more attempts where the time is (decision D3 in the harness's thesis record, §5d). The data to set the values does not exist yet: across the three trials in which the model answered, 3 regions were accepted, all on the second attempt, and no third attempt succeeded in about 14. So this change adds the mechanism only. The default stays `fixed`, and no existing arm changes behaviour.

**What.** `--budget-policy {fixed,share}` and `--budget-min` (default 1). Under `share`, a region gets `budget_min + round((budget − budget_min) · f / f_top)` attempts, where `f` is its measured runtime share and `f_top` the largest share among the regions still queued when it is reached. So the top region gets `--budget` and small ones approach `--budget-min`. An unmeasured region gets `--budget-min`. `--budget 0` stays 0 under both policies. Under `share` each region's allowance is logged (`[Tier-2] Budget N (policy share: share X%, largest queued Y%)`), and a region given 0 attempts is skipped before its profile snapshot is taken. Under `fixed` the code path and the log are unchanged.

**Verified:** mypy **0**. New feature check `budget-policy` covers 9 cases: `fixed` unchanged, `share` running from minimum to maximum, unmeasured regions at the minimum, zero staying zero, and the result never above the maximum. `--help` lists the options. The values for the default (`--budget`, `--budget-min`) come from a calibration run on benchmarks held out of the evaluation, before the default changes.

## Fix 63 — The clause check refused correct pragmas on every PolyBench-style kernel

**Files:** `pragmas/scope.py`, `benchmark/test_features.py`

**Problem.** The clause stage rejects `private(x)` when the loop writes `x` and later code reads it, because the writes are then discarded. `_read_after` answered "is it read later?" by treating **any** later mention of the name as a read, except a line beginning with a plain assignment. Three kinds of mention are not reads, and each refused a correct pragma in the observed run `local_obs1`:

1. **The next loop re-initialises the counter.** PolyBench declares `int i, j, k;` once per function and every nest reuses them: `for (j = 0; j < _PB_NJ; j++)` overwrites `j` before reading it, so the parallel loop's value is dead. This is the normal shape of every kernel in the suite.
2. **A later pragma names it.** `#pragma omp parallel for private(j, k)` for the *next* loop was counted as a read of `j`. A directive reads nothing at runtime.
3. **A comment mentions it.** The model's own note — `/* Second phase: copy B to A. Independent (i,j) iterations. */` — was counted as a read of `j`. Comments are never stripped in this analysis.

Measured on the recorded candidates: `2mm` was rejected for `private(j, k)` and `jacobi-2d-imper` for `private(i, j)`, both correct pragmas; the same rejection appears twice in `pilot2`. The model then produced `lastprivate(j, k)`, which is accepted but needless, so the defect also costs attempts.

**Fix:** in `_read_after`, comments are blanked first (`_without_comments`, keeping line indices and indentation); directive lines are skipped; and a later `for (name = …; …)` header whose initialiser does not itself read the name is treated as killing the value — the loop's whole span is skipped, while uses **after** it are still examined, because a loop nested inside another may run zero times and leave the old value live. The direction of caution is unchanged: a missed read would ship a wrong program, so only mentions that provably cannot read the stale value are discounted.

**Verified:** all 11 recorded candidates of `2mm`, `jacobi-2d-imper` and `seidel-2d` now pass the clause stage; before the fix, 2 of them were refused. Four cases added to the feature check `clause` (counter re-initialised by the next loop, a later pragma naming it, a comment mentioning it — all three must be accepted; a genuine read after the re-initialising loop — must still be rejected), giving **8/8 verdicts and 16 scope cases**. With the three changes reverted the check **fails on exactly those three cases**. mypy **0**.

---

# Fixes 64–73 — the September 2026 full review

Found by reading every module in pipeline order and by rendering a real prompt and reading it as the model does (`docs/REVIEW_2026-09.md` has the finding list, F1–F17 and P1–P12). No thesis experiment had run; `pilot2` and `local_obs1` predate these fixes and are not comparable with later runs.

## Fix 64 — The `dependences` stage judged a rewrite by the code it replaced

**Files:** `gate/dependences.py`, `gate/validate.py`, `benchmark/test_features.py`

**Problem.** Stage 3b fails a pragma when DiscoPoP OBSERVED a loop-carried dependence on the annotated loop. Phase A passed the ORIGINAL region's span, and blockers were matched by any OVERLAP with it. But a region reaches the model precisely because it has such a blocker, and removing it is what the rewrite is for. **Proven on Floyd–Warshall:** the correct parallelisation (copy row k and column k, `parallel for` on the i loop) is ThreadSanitizer-clean, agrees over 7 thread/schedule configurations and reproduces the output on both inputs — and was rejected at `dependences`. A second defect in the same match: an INNER loop's blocker failed DiscoPoP's own correct pragma on the independent loop around it. Whether the blocker file exists at all is an explorer draw (seidel-2d: 2 of 6 profiles), so the verdict was also random.

**Fix:** `annotated_loop_lines(diff)` returns the old-file lines of the loops a PURE annotation puts a pragma on, or `None` when the diff changes code. A rewrite is recorded as `evidence["dependences"] = "rewritten-code"` and never fails this stage — the profile does not describe that code. A pure annotation is judged against blockers of exactly the annotated loop (`loop_start` equality), not any loop overlapping the region.

**Verified:** feature check `dep-standing` (hand-written blocker file, so it does not depend on the explorer's draw): rewrite not judged by the old profile; outer Do-All survives an inner blocker; the blocked loop itself is still contradicted. Fails with the fix reverted.

## Fix 65 — The schedule matrix did not vary the schedule

**Files:** `gate/schedules.py`, `gate/validate.py`, `benchmark/test_features.py`

**Problem.** The matrix set `OMP_SCHEDULE`, which OpenMP applies only to loops declaring `schedule(runtime)`. Measured: the iteration→thread map of a plain `parallel for` is identical (`0000111122223333`) under `static`, `dynamic,1` and `guided`. So two of the three schedule entries in every `evidence["schedules"]` list were repeats of the static run, and `dynamic,1` — the configuration that interleaves neighbouring iterations and exposes a recurrence — never ran.

**Fix:** `with_runtime_schedule(text)` adds `schedule(runtime)` to every worksharing-loop pragma that has no schedule clause of its own, for the stress build only (`check_stress` binary); the count is recorded as `evidence["schedule_runtime_loops"]`. A loop with an explicit schedule keeps it.

**Verified:** feature check `schedule-runtime`, 10 pragma shapes (clause added only to unscheduled loop constructs; `sections`, `simd`, explicit schedules untouched). Fails reverted.

## Fix 66 — Numeric tolerance: calibrated on one input, ignored by Settle; a dead guard

**Files:** `gate/equivalence.py`, `run.py`, `phases/settle.py`, `gate/validate.py`, `benchmark/test_features.py`

**Problem.** (a) The numerical noise floor was measured on the default input only and applied to every `--check-input`. When the default input is rounding-free (integer-derived initial values) the floor is 0 and the perturbed input — which does round — was compared byte for byte. **Proven on `calib/dotprod`:** floor 0 on the default input, 1.0e-12 on the seeded one; the textbook `reduction(+:acc)` was rejected at `correctness`. (b) Settle re-judged the finished file without `noise_floor` (nor the stress settings), so a reduction accepted in Phase A/B under tolerance failed Settle and, with nothing else left, the whole run was reverted. (c) The OMP-barrier false-positive heuristic must not fire when the patch uses `nowait` or tasks; both callers omitted the `code` argument, so that guard was dead.

**Fix:** `numerical_noise_floor(..., extra_inputs=…)` takes the maximum over all inputs the gate will compare; `_check_final_source` passes `noise_floor`, `stress` and `stress_threads`; both heuristic callers pass the code.

**Verified:** feature check `noise-floor-inputs`: floor 0 on the default input, non-zero with the seeded one; a correct reduction passes the gate AND Settle. Fails reverted.

## Fix 67 — The prompt described a gate that was not the one running

**Files:** `llm/prompts.py`, `llm/request.py`, `llm/client.py`, `phases/phase_a.py`, `types.py` (`GateFacts`)

**Problem.** "HOW YOUR REWRITE IS CHECKED" was a constant. It listed a timing step ("has to be faster") that is off in every arm of the campaign; it said "byte for byte" where a measured tolerance applies; it omitted the two checks that catch most wrong rewrites (the schedule matrix, the second input). The task text was one constant too: in the default mode it said "after re-profiling, DiscoPoP must detect a genuinely parallel pattern … and achieves measurable speedup" while the system prompt said "nothing here re-profiles your code". And the loop-structure section branded every loop "too fine-grained on its own" against ~1000 iterations — the campaign profiles at a size where every PolyBench loop has 32 — while the system prompt said to annotate "the outermost one that qualifies". None did. A model told its loop must beat one thread at a deliberately tiny size has a reason not to parallelise at all.

**Fix:** `GateFacts(require_speedup, n_inputs, numeric, stress)` is built from the run's arguments and drives the system prompt (both pragma modes), the task text (`_goal`, `_task_checklist`) and the loop-structure rendering. With the speed check off the prompt says so, explains that the iteration counts come from a small profiling input, and asks for the OUTERMOST loop that can be made independent. The facts are constant for a run, so the prompt stays byte-identical across calls and the prompt cache still hits.

**Verified:** feature check `prompt-truth` renders all three edit modes under the campaign gate and a strict gate and asserts what each must and must not say. Fails with any of three mutations (section filter, granularity marker, task text).

## Fix 68 — `--evidence none` still carried DiscoPoP's evidence

**Files:** `llm/render.py`, `llm/request.py`, `llm/prompts.py`

**Problem.** The "Evidence digest" was printed unconditionally, outside the `--evidence` filter: under `none` the request still opened with the dependence variables, the loop nest with trip counts, the calls and the reductions (and, in diff mode, the iteration count in the header). The system prompt told the model it had been given observed dependences. This is the arm the thesis's evidence claim is measured against (B4, X1, E2-feedback).

**Fix:** every digest line belongs to a named section and is dropped with it; with no section there is no digest. The "what we give you" block is generated from the sections actually sent; under `none` it says no profiling data is provided.

**Verified:** `prompt-truth` asserts that under `none` every edit mode carries the source and the task and nothing DiscoPoP measured.

## Fix 69 — Evidence: arrays called scalars, mangled names, noise before signal, and three missing facts

**Files:** `evidence/package.py`, `evidence/context.py`, `evidence/deps.py`, `plan/regions.py`, `llm/render.py`, `types.py`

**Problem.** (P1) Array-ness was inferred from DiscoPoP's `GEPRESULT_` prefix, which the C kernels do not get — and C++ only sometimes. All PolyBench arrays reached the model as `[scalar]`, beside a digest line saying scalar dependences are "usually a reused location, not a value travelling between iterations": the opposite of the truth for the one array the kernel is about. (P12) Names arrived mangled or mutilated (`ZL1b[]`, `_ZL1a`, `_ZZ4mainE7contrib`). (P5) Dependences on the induction variables and on the function's signature line (the parameter being passed in) were listed at the weight of the real one.

**Fix:** arrays are recognised from the source (`_array_accesses`: `name[...]`, including `(*name)[i][j]`; declarations are not accesses) and the dependences re-tagged; names are demangled (`demangle` now handles `_ZZ…E<n><name>`), one spelling per variable. Induction-variable and signature-line entries are left out and said to be. Added: **array accesses** — per array, the subscripts written and read (`path: written as [i][j] | read as [i][j], [i][k], [k][j]`), the fact a restructuring is designed around (P6); **loops DiscoPoP already reports parallel inside the region** (P7); the region's **share of runtime** (P8); and a note naming the loop indices declared outside their `for`, which a pragma on an enclosing loop must list `private` (P11). The array-dependence note now first asks WHICH loop carries the dependence. All new sections are named in `EVIDENCE_SECTIONS`, so ablations can remove them.

**Verified:** feature check `evidence-enrich` profiles one kernel as C and as C++ and asserts array tags, plain names, the access summary and the inner patterns against `patterns.json`. Fails with any of three mutations.

## Fix 70 — Gate feedback: two stages without guidance, one instruction for every failure

**Files:** `phases/phase_a.py`

**Problem / fix.** `schedules` and `dependences` had no guidance text. The retry instruction asked "which of (a) or (b)" for every non-build failure although only `correctness` defines those, and contradicted the `clause` guidance. Each stage now has guidance and an instruction that fits it (build: fix the error only; clause: change only the clause; correctness: (a)/(b); performance: keep the dependence removal, coarsen; race/schedule/dependence: say which iterations still interact).

## Fix 71 — The pattern index hid DiscoPoP's own suggestions; Phase B could nest pragmas

**Files:** `plan/regions.py`, `plan/scoring.py`, `phases/phase_b.py`, `pragmas/parse.py`, `types.py`

**Problem.** `_load_patterns` kept the FIRST pattern per line and `patterns.json` lists `task` before `do_all` before `reduction`. A task entry — DiscoPoP generates no patch for those, and most are not applicable — hid the loop pattern on the same line: 44 lines across the suite (T0.6), each a suggestion no arm could apply, the DiscoPoP baseline included. On 11 kernel lines a `do_all` hid a `reduction`. In Phase B, a loop was marked covered before its patch was written, and without runtime measurements nothing stopped DiscoPoP's pragma going inside a loop the model had already parallelised.

**Fix:** per loop, patterns are ordered applicable-first, then `reduction` > `do_all` > others; the best one speaks for the loop and the other applicable ones ride along as `HotspotCandidate.alternates`, which Phase B tries when the first pragma does not survive. Phase B reads the loops already parallel in the source on entry (`existing_parallel_spans`) and records a span only after its patch is on disk.

**Verified:** feature check `pattern-choice`. Fails reverted.

## Fix 72 — Phase A bookkeeping: a silent queue drop, an eager 7 GB copy, an ignored write failure

**Files:** `phases/phase_a.py`

When a self-annotated rewrite was kept but its re-profile failed, the rest of the queue was deleted without a word — now each region is counted as skipped and the reason printed. The profile snapshot (all of `.discopop`; 7.1 GB on LULESH) was taken before the first model call of every region — now it is taken when a rewrite has passed the gate and is about to touch the file. If the validated patch could not be written to the real file the run carried on, re-profiled the unpatched source and recorded the rewrite as accepted — now the source is restored and the region skipped.

## Fix 73 — Line-keyed state in the wrong coordinates; re-profile failures unnoticed

**Files:** `phases/phase_a.py`, `plan/impact.py`, `pragmas/parse.py`, `profiling/runner.py`

**Problem.** Runtime measurements and "covered" spans are keyed by line. (a) They were translated onto the rewritten file on the fast-refresh path only; after a full re-profile (`--no-fast-refresh` arms, and the fallback) every region below a rewrite inherited the runtime of whatever used to sit at its line. (b) The covered span used the region's OLD line numbers. (c) A reverted rewrite restored source and profile but not the measurements. (d) `_reprofil` ignored the instrumented run's exit status.

**Fix:** one translation after either refresh path (`remap_lines(..., measurements=False)` when the runtimes were just re-measured); the covered span is computed in new coordinates from the line map and the diff's changed lines (`changed_span`, context excluded); `ImpactModel.snapshot()/restore()` around every attempt that reaches the file; the re-profile fails on a non-zero exit or a missing `dynamic_dependencies.txt`. `profile_is_fast` is decided at commit.

**Verified:** feature check `hotspot-remap` extended (covered-only remap, revert restore, changed span). Suite: **27 passed, 0 failed**; mypy **0 errors**.

## Fix 74 — Multi-file programs

**Files:** `project.py` (new), `gate/patching.py` (`run_build`), `gate/toolchain.py`, `gate/tsan.py`, `gate/validate.py`, `profiling/tools.py` (`InstrumentedBuild`), `profiling/runner.py`, `profiling/fast_refresh.py`, `plan/impact.py`, `plan/scoring.py`, `evidence/deps.py`, `evidence/package.py`, `phases/*`, `sources/edits.py`, `llm/providers.py`, `llm/request.py`, `args.py`, `run.py`. Design, measurements and the reproducer: `docs/MULTIFILE.md`.

**Problem.** One `--source-file`, so every benchmark had to be merged into one translation unit. And the obvious alternative is unsafe: profiled the way DiscoPoP documents (unit by unit), a two-file program had **both of its recurrences reported as applicable Do-All** — this DiscoPoP build constructs its call-path state graph from `main`'s unit only, so loops in other units get no loop states and no dependence is seen as loop-carried.

**Fix.** `--project-dir` turns on project mode. (1) **Profile** through a generated unity unit (one file that `#include`s every unit, compiled as one by the wrapper, removed again): DiscoPoP sees the whole program, and `FileMapping.txt` still names the real files and lines. (2) **Judge the real program:** every compile the gate performs already handed one candidate file to one of three functions; they now share `run_build`, which for a project stages the tree into a fresh directory, replaces the focus file with the candidate and builds all units (or runs `--build-cmd`). The user's tree is only read. (3) **Work per file:** regions resolve to their file through `FileMapping.txt`; the phases point `args.source_file` at each region's own file (`project.work_on`); dependences, reductions and static-only variables are filtered by file id; the fast refresh moves only the rewritten file's positions; Settle keeps originals and replays changes per file. (4) **Direct edit mode** gives the model the whole staged tree to read and takes back only the one file's changes. With no `--project-dir` no new path is taken.

**Verified:** feature check `project-mode` — the unit-by-unit false Do-Alls are recorded, the unity profile blocks them; regions carry their real file; the gate passes a correct pragma in the unit without `main` and catches a racy one without touching the user's files; after an edit to `kern.c` a fast refresh keeps all 23 of `main.c`'s observed dependences (22 are lost with the file-aware translation reverted). Three mutations killed. End to end with a model: unity profile → rewrite in `kern.c` → real two-unit gate → fast refresh → full re-profile → Settle, exit 0.

## Fix 75 — The pattern index mixed start lines with node ids

**Files:** `plan/regions.py` (`line_key`, `node_key`), `plan/scoring.py`. One dictionary held patterns by `start_line` ("1:7") and by `node_id` ("1:4"); a region looked up by `file:start_line` could hit a NODE id. A function starting at line 4 inherited the pattern of node 1:4, was deferred as "already parallelisable" and never reached the model. The two key spaces are now distinct. **Verified:** `pattern-choice` asserts a node id cannot answer a start-line lookup; fails reverted.

## Fix 76 — What "covered" means: the parallel loops, with their time — not the edited region

**Files:** `phases/phase_a.py` (`covered_spans_after`, the inside-parallel skip), `plan/impact.py` (`remaining_fraction`, `covered_time`), `plan/scoring.py`, `pragmas/parse.py` (`existing_parallel_spans`, `net_new_pragmas`).

**Problem.** Three defects around one idea. (F19) The covered mark was set after the queue had been rebuilt, so a loop nested in the loop the model had just parallelised came back as a survivor and was sent to the model — a wasted call whose "rewrite" re-spelled the pragma, counted as a second accepted rewrite and a fourth pragma in a file holding three. (F20) A pragma-free rewrite marked its region covered; since Fix 61 drops covered regions from every queue, Phase B never saw the loops such a rewrite had exposed, and Settle discarded the rewrite as an orphan — the `--no-llm-pragmas` arms could not keep a rewrite. (F21) The WHOLE edited span was covered: sibling loops of the same function were hidden from Phase B, and since everything a rewrite creates lies inside its own span, `--restructure-depth` ≥ 1 could never see anything.

**Fix.** Covered = the parallel constructs found in the rewritten source inside the region, each charged its measured share (constructs whose measurement was lost with their lines share what is left of the region's). Marked before the queue is rebuilt; nothing is marked for a pragma-free rewrite. `remaining_fraction` = a region's share minus the covered constructs it contains (0 inside one, measured or not); ranking, the 1 % floor and the share-weighted budget all use it. Independently of runtime measurements, Phase A skips a region that lies inside a construct already parallel in the source. Pragma counts are net of re-spelled lines.

**Verified:** `hotspot-remap` — pragma-free covers nothing; an annotated rewrite of a two-loop function covers only its parallel loop; remaining shares (function 0.40, parallel loop 0, its body 0, sibling loop 0.40). End to end: the nested loop is no longer attempted (2 model calls instead of 3, 2 pragmas reported for 2 in the file).

## Fix 77 — The contract bounds extra work

**Files:** `llm/prompts.py`. With the speed check off the prompt said speed is not judged and that "doing more work than the original is fine". Observed: a linear recurrence parallelised by recomputing every element from the start — O(n) → O(n²), correct, race-free, and certain to lose at full size. Extra work is now allowed within a constant factor, with that example named, and the speed note says where the rewrite finally has to win. **Verified:** `prompt-truth` asserts the wording in the campaign configuration.

## Fix 78 — Included units lost their clauses in the explorer's AST matching

**Files:** `explorer/discopop_explorer/utilities/ASTUtils/ASTLoader.py`, harness `agent/tools/cli.py` (`profile_once`), `benchmark/test_features.py`.

**Problem.** The explorer takes `private`/`firstprivate`/`shared` from the AST dump and matches AST file names to `FileMapping.txt` with `endswith("/" + path)`. Clang spells a unit found through a relative include directory as `./src/kern.c`, which never matches, so every declaration in the file was invisible and every Do-All there lost its clauses. Seen on the harness's first project profile (`privtemp_proj`): DiscoPoP's `#pragma omp parallel for` without `private(t)`, rejected at `tsan`, outcome `no-change`.

**Fix.** The matcher normalises the AST path (`os.path.normpath`, leading `./` removed) before the suffix match; the harness compiles the unity unit by its absolute path with absolute include directories, as the agent already did. **Verified:** explorer tests 23 passed; `project-mode` asserts `private(t)` on the kernel loop; the harness smoke run on `privtemp_proj` and `vecsum_proj` now applies the pragma in `src/kernel.c` and verifies FASTER (2.17×, 1.58× at 8 threads, digests exact).

## Fix 79 — Phase B repairs every clause that names a loop-body local, not only `shared()`

**Files:** `pragmas/patch.py` (`_repair_pragma_clauses`), `benchmark/test_features.py` (`clause`).

**Problem.** DiscoPoP lists loop-body locals in the clauses of its generated pragmas — in C++ especially (`private(x)` for `int x` declared in the body). Such a name is not in scope at the pragma, so the `-fopenmp` build fails outright. The repair covered `shared()` only; on the first project trial of NPB `is` (18 Sep) three of DiscoPoP's four suggestions were dropped for `private(x)`, `private(num_bucket_keys)`, `private(m)` before any real judge saw them.

**Fix.** A name declared inside the loop the pragma governs is removed from *every* clause (`private`, `firstprivate`, `lastprivate`, `shared`, `reduction`). That is semantically free: the variable is created afresh by its own declaration in each iteration, so it can carry nothing between iterations or across the loop's boundary. Names from an enclosing scope are never touched — there the clause check still decides. `default(none)` pragmas are left alone.

**Verified:** `clause` check — `private(x, k) firstprivate(t) shared(a, x) reduction(+:acc, x)` on a loop declaring `x` and `t` becomes `private(k) shared(a) reduction(+:acc)`; fails with the repair reverted to `shared()` only. Re-running Phase B on the `is` profile: the three repaired pragmas reach ThreadSanitizer, where all three are real races (`randlc`'s state, `rank`'s writes) — a baseline result, not a scope artefact.

## Fix 80 — DiscoPoP's explorer: a loop with several back edges is marked once, not once per cycle

**Files:** `explorer/discopop_explorer/classes/TaskGraph/TaskGraph.py` (`__break_cycles`, new `__loop_body_cu_ids`), `benchmark/test_features.py` (`explorer-multi-backedge`). An explorer change, like Fix 78, made because the harness cannot get a profile of Rodinia `nw` without it.

**Problem.** The task-graph builder replaces every loop of the CU graph by explicit loop and iteration markers. It finds one cycle at a time (`nx.find_cycle`), takes the first node of that cycle with an outside successor as the loop header, inserts StartLoop/StartIteration markers after the header, breaks *that cycle's* back edge and marks it as the iteration exit, and then re-wires *every remaining predecessor* of the header to the new StartLoop marker. A loop whose body returns to its header along several paths — `continue` statements, or the two arms of a branch that both end the iteration — has several back edges, and all but the first were re-wired as if they were the loop's entry. That closed a second cycle through the same header (StartLoop → header → body → StartLoop), the next pass marked the header again with a second set of markers chained onto the first (StartIteration → StartIteration), and `__assign_loop_contexts` stopped with `Invalid iteration structure found at node`. Rodinia `nw`'s traceback walk — `for (i, j; i >= 0 && j >= 0;)` with a short-circuit condition (a branch at the header) and three `continue`s, four back edges — failed that way on every attempt (server T0.6 re-run, 18 Sep: 3 of 3; a fourth by hand), so no trial of `nw`, a core-ten benchmark, could have existed. The `mg`/`pathfinder` failures of the same run are the other, random crash (T0.7) and are not this.

**Fix.** In the first pass over a header, every predecessor that lies in the loop's own body, as the CU graph knows it (the CUs in the subtree of the innermost PET loop containing the header), is a back edge and receives its own end-of-iteration marker, so no back edge is ever re-wired to the StartLoop marker and no second cycle through the header exists. Loops with one back edge are handled exactly as before.

**Verified:** `explorer-multi-backedge` check — a bounded loop with two `continue`s and a copy of `nw`'s walk (short-circuit header, three `continue`s, no increment): the shipped explorer fails in `__assign_loop_contexts`, the fixed one finishes and reports the bounded loop as a Do-All. Do-All and reduction sets on three existing profiles (`2mm` project, `vecsum`, NPB `is`) are byte-identical with and without the fix (order and per-run labels removed). The explorer's own 100 tests pass; mypy 0. `nw`'s own profile then runs through the whole explorer (its 620 MB call-path state mapping makes that slow — a cost, not a failure).

## Fix 81 — DiscoPoP's profiler: a loop that ends an `else` block gets its loop markers (root cause of the explorer's random `IndexError`)

**Files:** `profiler/DiscoPoP/utils/CFA.cpp`, `profiler/DiscoPoP/instrumentation/low_level/instrumentLoopExit.cpp`, `profiler/DiscoPoP/DiscoPoP.hpp`, `benchmark/test_features.py` (`profiler-else-loop`). A change to DiscoPoP's LLVM pass — the profiler must be rebuilt (`pip install ./profiler`, non-editable) on every machine. Upstream report: `docs/DISCOPOP_BUG_REPORTS.md` B3.

**Problem.** The explorer crashed with `IndexError: string index out of range` in `TaskGraph.recursive_assignment` on some runs of one unchanged profile (T0.7: `pathfinder` 40 of 60; NPB `mg` on every attempt of three separate studies and of the pilot). Since 16 Sep this was handled by retrying the explorer up to 20 times. The cause is not in the explorer: the pass instruments a loop only if its header **and its exit block** contain an instruction with a debug line, and clang gives the branch that ends an `else` block none — so a loop that is the last statement of an `else` got neither `__dp_loop_entry` nor `__dp_loop_exit`, while `loop_meta.txt` and the CU graph still list it. The static call-path states are built from the `__dp_loop_entry` calls in the IR, so that function's loop-state strings are one position short. The explorer, counting loops from the CU graph, (a) indexes past the string when its traversal happens to reach the last loop's context — the crash, "random" because the traversal short-circuits over sets — and (b) matches every loop after the missing one to the **wrong position** without any error, which changes which dependences count as loop-carried.

**Fix.** A valid header is enough; an exit block without a line id is marked with the header's.

**Verified:** `profiler-else-loop` check (six loops, one nest ending an `else`: 5 loop-state positions and a failing check on the unfixed pass, 6 positions and five explorer runs of five on the fixed one). `pathfinder`: explorer finished 1 of 6 runs before, **10 of 10 after**. DiscoPoP's own profiler tests 184/184; agent suite 28 passed, 1 skipped (the known explorer-instability skip), 0 failed. The 20-attempt retry stays as a safety net and its count is recorded per profile; profiles and instrument studies taken before this fix (T0.2, T0.6, T0.7, T0.8) describe the unfixed pass and are re-run.

## Fix 82 — DiscoPoP's explorer: a loop state is matched only against loops of its own function

**Files:** `explorer/discopop_explorer/classes/TaskGraph/TaskGraph.py` (`recursive_assignment`, new `__function_name_of_loop`). Upstream report: `docs/DISCOPOP_BUG_REPORTS.md` B5.

**Problem.** With Fix 81 every function of NPB `mg` has as many loop-state positions as loops, and the explorer still stopped with the same `IndexError` on every attempt. A call-path element `<function>_loopstate<digits>` carries one digit per loop *of that function*; `recursive_assignment` reads digit `loopstate_position` of it for the loop context it is visiting, and after a missed state it continues into successor contexts — which may belong to another function (the caller, once an inlined call is left). The position is then read from the wrong function's digits: a wrong match when it fits, an `IndexError` when the other function has more loops.

**Fix.** A loop state is compared only with loops whose function it names; otherwise it is a miss.

**Verified:** `mg`'s profile on the server gets past the crash (every earlier attempt died within 5 minutes). Do-All/reduction sets unchanged on 2mm, vecsum, NPB `is`; pathfinder 5 of 5; explorer tests 100/100; mypy 0. **What this exposes:** `mg`'s state assignment then walks 5,118 call-path states at ≈ 1.5 s each — about two hours per explorer run (measured run in progress). Like `nw`, a scalability limit of the call-path-state design, to be decided on (optimise, or report).

## Fix 83 — DiscoPoP's explorer: call-path state assignment memoised (hours → seconds)

**Files:** `explorer/discopop_explorer/classes/TaskGraph/TaskGraph.py` (`__assign_state_ids`: `recursive_assignment` now answers each (context, remaining call path) pair once per state id). Upstream report: `docs/DISCOPOP_BUG_REPORTS.md` P1.

**Problem.** For every call-path state the explorer walks the context graph from every function context, descending into contained contexts and again along successor chains. The same (context, remaining call path) pair is reached along many routes and re-answered every time, so the walk grows exponentially with nesting. Once Fixes 80–82 stopped the crashes, this was what remained: Rodinia `nw` ≈ 25 h, NPB-CPP `mg` hours, RepoOMP's NPB-C `CG` (469 lines) more than 20 minutes in this phase alone.

**Fix.** A per-state memo keyed by (context identity, remaining call path). The answer for a pair cannot change within one state id, a pair already answered `True` has already received the id (so the id is no longer appended twice), and a pair still being answered counts as a miss.

**Verified:** NPB-C `CG`: state assignment 278 states in under a second (was > 20 min, unfinished); whole explorer 99 s. Do-All and reduction sets on 2mm, vecsum, NPB `is` and `pathfinder` equal the known sets (two runs each); explorer tests 100/100; mypy 0. NPB-CPP `mg` on the server: past the phase that took hours (run in progress at the time of writing).

## Fix 84 — A generated pragma lands on ITS loop when a sibling loop has the same header (the DiscoPoP-only baseline was being under-measured)

**Files:** `pragmas/parse.py` (`_locate_header` ranks candidates by the patch's own context, then by distance from the pragma's line; new `_pragma_anchor_index`, `_pragma_context`), `pragmas/patch.py` (`derive_pragma_patch`, `_already_annotated`), `pragmas/clauses.py` (`check_pragma_clauses`) pass the patch. Feature check `pragma-sibling-loops`.

**Problem.** Phase B does not replay DiscoPoP's stored patch; it re-derives it against the current file from two facts, the pragma text and the loop header that follows it, and picks among identical headers the one nearest to the patch. "Nearest" was measured from the hunk's first line — three context lines ABOVE the pragma. PolyBench writes sibling loops with identical headers two or three lines apart (`for (j = 0; j < _PB_NY; j++)` twice in `atax`, two identical nests in `mvt`, four in `gemver`), so the pragma for the second loop was put on the first. Found on `atax`: DiscoPoP's pattern #29 (the valid Do-All over `y[j] = y[j] + A[i][j] * tmp[i]`, its own patch correct, line 74) was tested on line 72 (`tmp[i] = tmp[i] + …`, a recurrence), raced under TSan, was served the first pattern's cached verdict (identical diff) and was dropped — `discopop_gate` ended `no-change` on a kernel where DiscoPoP alone has a correct pragma.

**Measured blast radius** (every stored profile of the harness, 539 DiscoPoP pragma patches, old locator against new on the unchanged source): **29 misplaced (5.4 %), in 12 of 26 PolyBench kernels** — 2mm, atax, covariance, fdtd-2d, gemm, gemver, gramschmidt, lu, mvt, reg_detect, syr2k, syrk; none in TSVC, NPB `is`, Rodinia. The error is one-sided: Phase B is the ONLY source of pragmas in the DiscoPoP-only arm and a secondary one in the agent arms (there the model writes the pragmas with its rewrite), so it biased the thesis's main comparison in the agent's favour. Every `discopop_gate` number measured before this fix on those kernels is void and re-measured; of the agent results, `polybench/lu` is the one kernel of E10 it touches.

**Fix.** Candidates are ranked by how many of the patch's unchanged lines they reproduce — the loop body below the header, the lines above the pragma (pragmas inserted since are skipped, not counted as mismatches) — and only ties are broken by distance, now measured from the line the pragma stands in front of. Context decides even after earlier pragmas have shifted the file, where distance alone ties.

**Verified:** `atax` on its real profile: #28 → line 72, #29 → line 74, #30 → line 69, also with a pragma inserted above; feature check fails on the old code and passes on the new; `discopop_gate` on `atax` now ends with DiscoPoP's pragma applied and verified (`dp_alone_fix84_mac`); clause, anchor-vs-ref, omp-include checks pass; mypy 0. Full feature suite: 30 passed, 1 failed — `explorer-multi-backedge` timed out in the explorer's patch-generator subprocess (the open DiscoPoP bug B6, ≈ 3 hangs in 20 runs, unrelated to this change) and passed when re-run alone.

## Fix 85 — When the model and DiscoPoP both annotate the same loop, measure both instead of letting one win silently

**Files:** `pragmas/arbitrate.py` (new: `collisions`, `swap`, `arbitrate`), `pragmas/__init__.py`, `phases/phase_a.py` (an arbitration step immediately before COMMIT), `llm/render.py` (`_fmt_inner_patterns`). Feature check `pragma-arbitration`.

**Problem.** The deferral rule works: a loop DiscoPoP can already parallelize is left to Phase B (`[Phase-A] DiscoPoP already has a pattern here — deferred to Phase B`). But a LARGER region containing that loop — a function with no pattern of its own — still goes to the model, and under `--llm-pragmas` the model annotates the inner loops from inside its rewrite. Phase B then re-profiles, finds them annotated, reports "DiscoPoP proposes no applicable pattern for the final source", and DiscoPoP's own pragma is never built, never timed, never seen. The prompt made this worse: with `--llm-pragmas` it told the model that "annotating one of these as it stands is a valid answer".

Seen on PolyBench `jacobi-2d` (E10, 6 of 6 trials): DiscoPoP claims the two stencil loops with `parallel for private(j) shared(A,B)`; the model writes `parallel for collapse(2)` over them from a function-level rewrite; DiscoPoP's version is **5.9×** on the server against the model's **2.5×**, so the agent finished 2.4× BELOW DiscoPoP alone — in the comparison the thesis leads with.

**Measured frequency.** Across every archived run, **22 trials** end with a deferred DiscoPoP pattern and only model-written pragmas (`floyd-warshall`, `jacobi-2d`, `lu`). Displacement is not uniformly bad: on `lu` the model's pragmas give 2.6–2.8× where DiscoPoP's own give **0.21×**. So the fix must not pick a side.

**Fix.** Two parts.
1. *Prompt* (`_fmt_inner_patterns`): under `--llm-pragmas` the model is now told that DiscoPoP annotates these loops itself, afterwards, and that it must write pragmas only for loops it restructures or creates. Leaving them alone is stated as a valid answer.
2. *Arbitration* (`pragmas/arbitrate.py`, called from Phase A before COMMIT): for every loop DiscoPoP claimed in the region's evidence that now carries a DIFFERENT, model-written pragma, build DiscoPoP's pragma as an alternative, put it through the SAME gate (its clauses are not assumed correct), time the two against each other with `measure_marginal`, and keep the faster. Outside the noise band `[1/min_measured_speedup, min_measured_speedup]` the winner is taken; inside it the model's pragma stands, because nothing was shown. Loops are matched by HEADER TEXT, not by line, since the rewrite has moved them. Every collision is recorded in the candidate record as `pragma_arbitration` (winner, reason, ratio), whichever side wins — which is the per-collision answer to "who writes the better pragma, the model or the analysis tool?", data E3 would otherwise have to produce separately.

Arbitration needs a measurement, so it runs only where the run already measures (`--require-speedup`, the campaign default since 2026-09-20). With the check off the collision is left alone.

**Verified:** feature check `pragma-arbitration` reproduces the `jacobi-2d` collision and checks all five outcomes without a model or a compiler — DiscoPoP's pragma taken when faster, the model's kept inside the noise band, the model's kept when DiscoPoP's alternative fails the gate (and the reason recorded), an identical pragma not treated as a collision, and a loop left to Phase B not treated as one. `prompt-truth` and `evidence-enrich` pass with the new wording; mypy 0.

## Fixes 86–90 — recorded in the experiment record

Fixes 86–89 (the exposed loops filtered out before Phase B; the hotspot re-measurement that described the old program; DiscoPoP's mispaired loop counts; Settle's unpaired speed verdict) and Fix 90 (reverted before it ever ran) are documented where they were found, in `evaluation/agent/docs/THESIS_EXPERIMENTS.md` §6, each with its feature check (`new-region-ranking`, `hotspot-remeasure`, `loop-counts`, `settle-paired`).

## Fix 91 — The clause stage refused a correct `private(x)`: a later loop that WRITES the name first reads nothing stale

**Files:** `pragmas/scope.py` (`_read_after` skips a later loop whose body writes the name before any read; new `_body_writes_first`), `benchmark/test_features.py` (`clause`)

**Problem.** `private(x)` / `firstprivate(x)` discard the loop's writes to `x`, so the clause stage rejects them when code after the loop READS `x`. It counted any later mention that is not a plain assignment as a read. E1, `tsvc/s281` reps 2–5: the model split the loop at `LEN/2`, DiscoPoP reported a do-all on both halves with `private(x)`, and the pragma on the first half was refused because the second half mentions `x` — as `x = …` first, then `a[i] = x - 1.0`. The later read sees the value written in its own iteration, never the one the parallel loop discards. With one half parallel the program was 0.63–0.97× the original, so the agent lost `s281` in all five repeats although its model wrote the right rewrite every time (found by E1-bare, `e1b_marginal_replay`).

**Fix.** The same reasoning `init_kill` already applies to `for (j = 0; …)`, one step further in: a later loop whose body's FIRST mention of the name is an unconditional, top-level `name = expr;` with the name absent from `expr` is skipped. Conservative: a write under an `if`, a read before the write, or a read after the later loop (it may run zero times) still count.

**Verified:** feature check `clause` — the `s281` shape accepted; a write only under an `if`, a read before the write and a read after the later loop still rejected; the check fails on the old code. Replay of every archived clause-stage rejection (`evaluation/agent/tools/clause_replay.py`, 25 found, 11 reconstructible): **exactly 4 verdicts change, all `s281` reps 2–5**; the old code flips none of them. mypy 0.

## Fix 92 — A program that calls the OpenMP runtime is judged by the gate, not refused at compile

**Files:** `gate/toolchain.py` (`uses_omp_runtime`, `omp_build_flags`), `gate/patching.py` (`_compile`), `gate/validate.py` (the check build), `gate/timing.py` (`capture_reference`), `gate/equivalence.py` (the numerical noise floor's builds), `benchmark/test_features.py` (`omp-runtime`)

**Problem.** The gate's plain compile — and the reference build, the noise-floor builds and a pragma-free candidate's check build — are made without OpenMP. A program that calls `omp_get_thread_num()` cannot even link that way, so it failed at `compile` whatever it computed. Found by E1-bare's race check: `tsvc/s341` rep 5 of the model alone, harness-verified FASTER, came back from the gate as a `compile` failure.

**Fix.** Those builds add the OpenMP flags when, and only when, the source calls the runtime (`omp_…(`) or includes `<omp.h>`; every other program is still compiled plain.

**Verified:** feature check `omp-runtime` — a per-thread-partial-sum program calling `omp_get_thread_num`/`omp_get_max_threads` passes the gate; the same program with every thread adding into one slot fails at `tsan`; the check fails on the old code. Replay: `s341` rep 5 now receives a verdict — clean, carried by TSan (the schedule matrix saw its output move under `guided`: it relies on two `omp for` loops giving each thread the same iterations, which OpenMP guarantees only with an explicit `schedule(static)`). mypy 0.

## Fix 93 — D33: Phase B judges the pragmas that do not pay ALONE as a set

**Files:** `phases/phase_b.py` (`annotate` returns `deferred`; new `_judge_jointly`), `phases/settle.py` (a set's fingerprints justify its rewrite), `run.py` (a set's region ids keep its records), `benchmark/test_features.py` (`phase-b-joint`)

**Problem.** Phase B timed each of DiscoPoP's pragmas against the state before it and dropped the ones that did not pay. When a rewrite splits one loop into two or three — a buffer loop and a compute loop, one loop per statement — each pragma alone can be slower (0.6–1.1×) while all of them together are 2.5–4× faster: one parallel loop next to a sequential one does not pay, both do. Phase B never measured the set, so the program that wins was never built. E1 (class-R TSVC, `default`): 18 of the 44 `no-change` trials ended here; replaying the agent's own `measure_marginal` on their archived states (`e1b_marginal_replay`) found the set 1.2–2.8× faster than the ORIGINAL in 7 of them (`s1213` ×2, `s121` ×3, `s244`, `s112`), the other 11 slower with every pragma.

**Fix.** A pragma that passes every safety stage but is slower than the noise threshold alone is DEFERRED, not dropped. After the pass, per file: the deferred pragmas are applied together (outermost first; one nested in another is left out), the SET is re-checked for safety (TSan, schedule matrix, output), timed against the state before it with the same paired measurement and threshold, and — if it pays — members are removed one at a time while removing one does not make it slower (backward elimination). What is kept is ONE change-log entry carrying every member's fingerprint and region id, so Settle keeps or drops the set as a unit. A single deferred pragma is dropped exactly as before; a pragma that pays alone takes exactly the old path. Recorded per trial by the harness: `phase_b_deferred`, `phase_b_joint_kept`.

**Verified:** feature check `phase-b-joint` (speed and safety stood in, the real derivation and application): a pair paying together kept as one entry with both regions; a pair not paying leaves the file unchanged; a dead-weight member eliminated; a lone deferred pragma dropped. Replayed on E1 and verified by the harness (`e1b_v2_verify`, `verify-source`, server): **the 7 recovered programs are FASTER, 1.49–3.00×**, output identical on both inputs; control `s127` rep 1 FASTER 4.48× as in E1, control `s121` rep 4 (a slow rewrite) parallel-not-faster 0.14×. mypy 0; feature suite 42 passed, 1 skipped (the known explorer draw).

## Fix 94 — D32: a floor at DiscoPoP alone

**Files:** `phases/floor.py` (new: `build_floor`, `apply_floor`, `_measure_states`), `run.py`, `benchmark/test_features.py` (`dp-floor`)

**Problem.** Settle asked whether the finished program is slower than the ORIGINAL, never whether it is slower than what DiscoPoP alone would have delivered — so "DiscoPoP + agent" could subtract. E1 class A: `vpvtv` finished at 2.37× where DiscoPoP alone reached 4.08× (worse); on `s000` the rewrite ended slower than the original, Settle reverted everything and DiscoPoP's own 4.03× pragma went with it (lost).

**Fix.** Before Phase A the agent builds DiscoPoP's own gated program — Phase B and Settle on the original, no model, exactly what the `discopop_gate` arm delivers (its console in `<output>/floor/floor.log`, so the run's log and every counter the harness reads describe the agent's own run) — keeps it as the floor and restores the original. After the final Settle the agent's program is timed against the floor with the same paired measurement and threshold (whole program; for a project both versions' other units are written before each side is timed); if it is slower, DiscoPoP's program and its records are shipped instead. Skipped for `--budget 0` (that arm is its own floor). Where DiscoPoP alone keeps nothing — all 90 class-R TSVC trials of E1 — the floor is the original and nothing changes. Recorded per trial: `dp_floor` ∈ {original, same, agent, discopop}.

**Verified:** feature check `dp-floor` (Phase B, Settle and timing stood in): the floor captured and the original put back; no floor when DiscoPoP keeps nothing; a slower agent program replaced by the floor with its records, a faster one kept, an identical one not timed, and the `s000` shape — the agent back at the original while DiscoPoP's pragma pays — ships DiscoPoP's program. On E1 by construction from the archived programs: `vpvtv` and `s000` become `equal` (DiscoPoP's program shipped), `s313` stays `better`. mypy 0.

## Fix 95 — The model's file tools are confined to its workspace, and shell / web / search are blocked

**Files:** `llm/providers.py` (`BLOCKED_TOOLS`, `FILE_TOOLS`, `confine_to`, the direct-mode options), `benchmark/test_features.py` (`workspace-confined`)

**Problem.** In `--edit-mode direct` the model gets Read / Edit / Write on a temporary workspace holding a copy of the sources, and the docstring said those tools were "confined to that directory". They were not: `allowed_tools=["Read", "Edit", "Write"]` lists each tool WHOLE, and the SDK auto-approves a whole-listed tool for ANY path before any permission check (`claude_agent_sdk.types`: "an allowed_tools entry that allows a whole tool auto-approves it before the callback is consulted"). Found on 23 Sep when the author asked whether the reference solutions could reach the model. Measured live, one Haiku call, the old options: asked to read a file OUTSIDE its workspace, the model read it and reported its content. In the campaign's prompts no path outside the workspace is ever named, the workspace is a fresh temporary directory, and nothing in any archived log shows an access outside it — but the model's session transcripts are not kept, so for the runs before this fix that cannot be proven either way (record §6, D36).

**Fix.** A PreToolUse hook (`confine_to(workspace)`, matcher `Read|Edit|Write|MultiEdit|NotebookEdit|Glob|Grep|LS`) resolves each file tool's path — relative, absolute, `..`, symlinks — and denies it unless it lies inside the workspace. Hooks run for every call, auto-approved or not. `disallowed_tools` blocks the shell, the web, sub-agents and search outright (`Bash`, `WebFetch`, `WebSearch`, `Task`, `Agent`, `Glob`, `Grep`, `LS`, …). The model still reads and edits its own files as before.

**Verified:** feature check `workspace-confined` — 9 paths judged by the hook itself (outside absolute, `..`, a symlink leading out, the repository's `reference_solutions/tsvc/s211.c`, `/tmp` denied; the workspace's own file allowed, relative and absolute), shell/web/search in the blocked list. Live, one Haiku call each: old options — the outside file read and its secret word reported (LEAKED); new options — the model reports it cannot access the path and answers only from the workspace file (NOT LEAKED). mypy 0.

## Fix 96 — D37: the model-alone baseline gets nothing of ours that helps it

**Files:** `bare_llm.py` (`_ROLE_MINIMAL`, `_system(prompt)`, `_request_minimal`, `--prompt minimal|contract`), `benchmark/test_features.py` (`bare-llm`)

**Problem.** The author: "the LLM alone should not use anything of ours to help or guide it — just the LLM, and afterwards we evaluate its speedup, correctness, races and everything against the agent." The baseline's prompt (E1-bare) carried about 560 words of the agent's own guidance — THE CONTRACT (output identical, bounded extra work, heap for large buffers, clause rules), the OpenMP loop rules, the pragma forms — and a task line naming transformations ("splitting a loop, adding a buffer, reordering statements").

**Fix.** `--prompt minimal`, the default: the role and how its tools work; the task ("Parallelize this program with OpenMP so that it runs faster on a multi-core machine. Its output must stay exactly the same."); and the functions it must not change because they set up, time and print the program — a condition of the MEASUREMENT (a rewritten timer voids the trial), not help. 87 words in all. `--prompt contract` reproduces E1-bare's prompt exactly. Judged afterwards as before: the harness's verification (outputs on two inputs, repeatability, speed) and the gate's race stages run over its programs (`tools/race_check.py`), nothing during.

**Verified:** feature check `bare-llm` in both modes — minimal: none of the contract, clause, OpenMP-rule or transformation words, the goal and the measuring functions present, stateless, the edit kept unchecked; contract: THE CONTRACT and the single attempt still there. The check fails against the old runner. mypy 0.
