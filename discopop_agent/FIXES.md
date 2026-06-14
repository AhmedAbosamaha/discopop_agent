# Bug Fixes & Improvements Log

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

**Reverted by Fix 20.** The score and `--min-speedup` system is the correct gate. ID drift in rebuilt candidates is handled separately by Fix 19.

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

## Fix 18 — `--distance`: pass-based discovery; `_refresh_candidates` replaces stale line-map logic

**Files:** `args.py`, `controller.py`

**Problem (two parts):**

**Part A — Candidates lost after re-profiling.**
After accepting a Tier-2 patch and re-profiling, the controller replaced `candidates[i:]` (all remaining queued regions) using a lookup keyed by exact adjusted start-line (`fresh_by_key.get((file_id, adj_line))`). The `_adjusted_line` function uses proportional intra-hunk interpolation which is approximate — a candidate whose original start-line falls inside the modified hunk maps to the wrong line and misses the lookup, dropping it from the queue. In practice, the inner loop of `example5/stencil.cpp` (start-line 26, inside the diff hunk) adjusted to line 28 but the fresh profile placed it at line 30 — it was silently dropped.

**Part B — Uncontrolled new-candidate discovery.**
The same post-acceptance block also added "structural parent" candidates from the fresh profile (any region that contained the patched region). This implicit discovery was hard to reason about, interleaved arbitrarily with pass-0 work, and there was no way to bound or disable it.

**Fix:**
- **New `--distance N` CLI parameter** (default 0, added to `AgentArguments`).
  - `--distance 0`: process only original candidates; no new discovery at all.
  - `--distance N`: after the initial pass, run up to N additional full discovery passes on the modified source.
- **Outer pass loop** in `run()`: pass 0 uses the existing profile; passes 1…N re-profile and discover candidates with region IDs not seen in any prior pass (`all_seen_ids` set).
- **ID-based queue rebuild** replaces the entire `fresh_by_key` / `parent_keys` / `queued_keys` / `updated` block. After a within-pass Tier-2 acceptance and re-profile, the remaining queue is rebuilt by region ID:
  ```python
  fresh_by_id = {nc.region.region_id: nc for nc in fresh}
  remaining = [
      fresh_by_id[old_c.region.region_id]
      for old_c in candidates[i:]
      if old_c.region.region_id not in resolved
      and old_c.region.region_id in fresh_by_id
  ]
  del candidates[i:]
  candidates.extend(remaining)
  ```
  - Candidates whose region ID still exists in the fresh profile (unmodified regions like the bounds-check loop in `main`) are updated with fresh pattern data.
  - Candidates whose region ID disappeared (the region was structurally changed by the patch, e.g. the inner loop gained a new ID after double-buffering) are dropped from this pass and re-discovered in distance passes.
  - No line-number arithmetic, no tolerance parameter, no wrong matches.
- Removed `_adjusted_line`, `_HUNK_RE`, and `HotspotCandidate` import — all were only needed by the old line-based matching logic.
- Removed `seen_keys` (line-based, per-pass) — superseded by `all_seen_ids` (ID-based, cross-pass).
- `_print_banner` updated to display the distance setting.

**Effect:**
- All original candidates survive re-profiling within a pass, even when their lines shifted inside a modified hunk.
- New-region discovery is explicit and bounded: only happens between passes, never mid-pass.
- `--distance 1` gives the old "structural parent" behaviour more reliably: re-profile once after all originals are processed, then handle whatever is new.
- `--distance 0` (default) is safe and predictable: exactly the initial candidate list is processed.

---

## Fix 20 — `controller.py`: remove global `≤ 1 iteration` skip (reverts Fix 11)

**File:** `controller.py`

**Problem:**
Fix 11 added a global early-exit guard that skipped any candidate with `iteration_count ≤ 1`. This was too aggressive:

1. **Profiling input ≠ production workload.** The profiling run uses a fixed input; a loop that ran once on the profiling input may run millions of times in production. The score/speedup system already accounts for observed workload — a second filter on raw iteration count is redundant and wrong.
2. **Functions are never loops.** Function-level candidates (`type=function`) naturally report `iteration_count = 1` (the function is called once). They can still contain regions worth restructuring, and Tier-2 LLM analysis is exactly what handles them.
3. **ID drift** (after Tier-2 restructuring changes CFG traversal order) could assign an old ID to a trivial new construct, making an originally-busy region appear to have 1 iteration and be silently dropped.

**Fix:**
Removed the `if region.iteration_count <= 1: skip` block entirely from the main candidate loop. The score gate (`--min-speedup`) and Tier-1/Tier-2 logic are the sole filters for whether a region is worth processing.

**ID drift is handled separately** by Fix 19: during the within-pass ID-based queue rebuild (after a Tier-2 acceptance), candidates whose fresh `iteration_count` collapsed to ≤ 1 are excluded from `remaining` — because the fresh data is known to be unreliable for those IDs (the ID drifted to different code). This localised filter does not affect initial or discovery-pass candidates.

---

## Fix 19 — ID-based rebuild: drop iteration-count-collapsed candidates (ID drift)

**File:** `controller.py`

**Problem:**
After a Tier-2 patch restructures code inside a function, LLVM re-traverses the changed CFG during re-instrumentation and assigns region IDs in a different order. A remaining candidate's ID may still *exist* in the fresh profile but now map to a completely different construct — for example, a single-statement allocation block — rather than the original loop.

When this happens, the fresh `iteration_count` for that ID is 1 (or 0). The early-exit guard (Fix 11) then fires:

```
└─ SKIPPED (only 1 iteration(s) profiled)
```

The candidate is skipped not because the original region is serial, but because the ID drifted to trivial code. Regions with 12,700 iterations in the initial profile were showing up as 1 iteration after re-profiling.

**Fix:**
Added an `iteration_count > 1` guard to the ID-based rebuild filter inside the Tier-2 acceptance block:

```python
remaining = [
    fresh_by_id[old_c.region.region_id]
    for old_c in candidates[i:]
    if old_c.region.region_id not in resolved
    and old_c.region.region_id in fresh_by_id
    # Drop IDs whose iteration count collapsed — signals ID drift to different code.
    # These regions are re-discovered with correct new IDs in distance passes.
    and fresh_by_id[old_c.region.region_id].region.iteration_count > 1
]
```

IDs that drifted to a trivial construct (≤ 1 iteration) are now silently dropped from the current pass's remaining queue instead of being carried forward and immediately skipped.

**Effect:**
Drifted IDs no longer consume a candidate slot, do not appear in the `skipped` list, and are not added to `all_seen_ids` — so they remain eligible for re-discovery in subsequent distance passes, where DiscoPoP will assign them the correct new IDs with the correct iteration counts.
