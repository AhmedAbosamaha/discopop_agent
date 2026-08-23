# DiscoPoP Agentic Controller — Documentation

## Overview

The DiscoPoP Agentic Controller is an LLM-driven parallelization agent built on top of the DiscoPoP profiler. It extends DiscoPoP's static analysis with an autonomous loop that:

1. Reads DiscoPoP's profiling output to rank hotspot code regions by parallelization potential
2. Validates DiscoPoP's own suggestions against ThreadSanitizer to catch false positives
3. When DiscoPoP cannot help, calls a large language model (Claude) to restructure the source code so that DiscoPoP can detect parallelism after re-profiling

The agent operates on any profiled code region — loops, function bodies, or basic blocks — not only loops.

---

## Architecture

The system is split into four layers plus a controller that ties them together:

```
discopop_agent/
├── __main__.py      entry point (python -m discopop_agent)
├── args.py          CLI argument parsing → AgentArguments
├── controller.py    orchestration loop (L1 → L2 → L3 → L4)
├── l1_planner.py    L1: hotspot discovery, scoring, priority queue
├── l2_evidence.py   L2: evidence collector (deps, source, counters)
├── l3_llm.py        L3: LLM prompt builder + provider clients (Anthropic / OpenAI-compatible)
├── l4_validator.py  L4: quality gate (apply / compile / TSan / correctness / speedup)
└── types.py         shared dataclasses
```

### Data flow

```
DiscoPoP output               Agent layers                  Output
─────────────────     ──────────────────────────────     ──────────────
Data.xml          ──▶ L1 Planner                       
patterns.json     ──▶   scored priority queue          
loop_counter.txt  ──▶                                  
                         │                             
                         ▼ per candidate                
dynamic_deps.txt  ──▶ L2 Evidence ──▶ EvidencePackage  
reduction.txt     ──▶                                  
source file       ──▶                                  
                         │                             
                         ▼                             
                      L3 LLM  ──▶  unified diff        
                         │                             
                         ▼                             
                      L4 Validator                     
                        ├─ Stage 1: patch apply        
                        ├─ Stage 2: compile            
                        └─ Stage 3: TSan run           
                                                       
                      controller ──▶ accepted.json     
                                 ──▶ *.patch files     
                                 ──▶ patched source    
```

---

## Layer Reference

### L1 — Planner (`l1_planner.py`)

**Purpose:** Discover every profiled region from DiscoPoP's output, match it against detected parallelism patterns, score it, and return a ranked priority queue.

**Inputs:**
- `<discopop_dir>/profiler/Data.xml` — all profiled nodes (CUs, functions, loops)
- `<discopop_dir>/explorer/patterns.json` — DiscoPoP's detected patterns
- `<discopop_dir>/profiler/loop_counter_output.txt` — loop iteration counts

**Scoring formula:**

```
score = c · log₂(1 + W) − λ · 1[tier=2]
```

| Symbol | Meaning |
|--------|---------|
| `c` | pattern confidence (1.0 for Do-All, 0.9 for Reduction, 0.7 for Pipeline, 0.3 for Tier-2 baseline) |
| `W` | profiled workload proxy (NOT a measured speedup) — `instructionsCount` for CUs; `iteration_count × loop_size` for loops |
| `λ` | LLM penalty (`--lambda-penalty`, default 1.0) — discounts Tier-2 candidates to prefer Tier-1 where possible |

**Tier assignment:**

| Tier | Condition |
|------|-----------|
| 1 | DiscoPoP found an applicable pattern (`applicable_pattern: true` in patterns.json) |
| 2 | No applicable pattern, but workload is above `_MIN_WORKLOAD_TIER2 = 100` |

**Output:** `List[HotspotCandidate]` sorted by score descending.

---

### L2 — Evidence Collector (`l2_evidence.py`)

**Purpose:** Given a candidate region, read DiscoPoP's runtime profiler output and assemble a complete `EvidencePackage` to send to the LLM.

**What it collects:**

| Field | Source file | Description |
|-------|-------------|-------------|
| `source_region` | source `.cpp` file | Annotated lines `[start-2 … end+2]`; target lines marked with `>>>` |
| `raw_deps` | `dynamic_dependencies.txt` | Read-after-write deps crossing iteration boundaries. Each dep is tagged `kind` = **`array`** (an array-element / `GEPRESULT` access — usually an *algorithmic* dependence) or **`scalar`** (usually a storage conflict, removable by privatization) |
| `war_deps` | `dynamic_dependencies.txt` | Write-after-read deps (with the same array/scalar `kind` tag) |
| `waw_deps` | `dynamic_dependencies.txt` | Write-after-write deps (with the same array/scalar `kind` tag) |
| `reduction_vars` | `reduction.txt` | Variables involved in reduction patterns |
| `iteration_count` | `loop_counter_output.txt` | How many times the loop ran |
| `prevented_deps` | `explorer/doall_prevented.json` | DiscoPoP's exact Do-All blockers with STATIC/DYNAMIC origin (empty for false-positive loops it wrongly thinks are Do-All) |
| `shared_vars`, `private_vars`, `firstprivate_vars`, `lastprivate_vars`, `classified_reduction_vars` | `explorer/patterns.json` | DiscoPoP's own OpenMP data-sharing classification for the region (which variables are the shared data vs. privatizable). Empty when no pattern was detected |
| `loop_trip_counts` | `dynamic_dependencies.txt` (`BGN loop` markers) | Observed trip counts per loop in the region: `{line, total, entries, avg, max}` where `entries` = activations and `avg` = iterations per activation — lets the LLM judge parallel **granularity** |
| `local_vars_in_region` | `explorer/detection_result_dump.json` (CU graph) | Variables DiscoPoP tracks as loop-**local** (already per-iteration private). Only the CU *scope* is used, not its `accessMode` — the latter is unreliable for arrays (a CU reports the pointer access, not the element read/write) |
| `static_only_vars` | `static_dependencies.txt` vs `dynamic_dependencies.txt` | Variables with a STATIC (compiler-conservative) dependence in the region that was **never observed at runtime** anywhere → likely spurious / privatizable |
| `tier1_failure_reason` | previous stage | TSan/compile error text from last failed attempt |

**Key design point:** `tier1_failure_reason` is updated after every failed validation attempt. This means each retry gives the LLM a fresh, accurate failure diagnostic — not the same generic message every time.

**Reasoning signals (why they matter):** the array-vs-scalar `kind` tag and the data-sharing classification let the prompt tell the LLM plainly that a loop-carried dep on array elements (e.g. `arr[]`) is *algorithmic* and cannot be removed by renaming/copying the array — steering it away from the common "copy `arr` into `temp`" non-fix. Trip counts expose fine-grained loops (many activations × few iterations) so the LLM prefers coarser parallelism. These are surfaced in the prompt by `l3_llm._fmt_classification`, `_array_dep_note`, `_fmt_trip_counts`, and `_fmt_extra_vars`.

---

### L3 — LLM Engine (`l3_llm.py`)

**Purpose:** Build a structured prompt from the `EvidencePackage`, call the LLM, and return the edit as a unified diff — whether the model expressed it as a diff, as a rewritten function, or by editing the file itself (see **Edit modes** below).

**Prompt structure (first attempt):**

```
[System — cached across all calls]
  You are an expert in parallel programming...
  Do NOT add OpenMP pragmas — DiscoPoP will do that after re-profiling.

[User — turn 1]
  ## Source file: example4/bubble_sort.cpp
  ## Region: 1:23  type=loop  (524,288 iterations)

  ### Source
  (Each line shown as `NNNN >>> code` — `NNNN >>>` is display-only, not part of the file.)
  ```cpp
  ...annotated source...
  ```

  ### Runtime data dependences
  (each dep tagged [array element] or [scalar])
    RAW — read-after-write: line 23 → 24  arr[]  [array element]
    WAR — write-after-read: none
    WAW — write-after-write: none

  ### DiscoPoP variable classification (from its own analysis)
    shared        : arr   (a loop-carried dep on these is ALGORITHMIC)
    firstprivate  : ok

  ### Additional DiscoPoP variable facts
    loop-local (already per-iteration private): tmp

  ### Nature of the blocking dependence         ← fires when the blocker is on an array
  The loop-carried RAW dependence is on ARRAY ELEMENTS (arr[]), not a scalar.
  Copying/renaming the array (arr -> temp) does NOT remove it...

  ### Loop trip counts (observed — judge parallel granularity)
    loop at line 23: 1023 activation(s) × ~512 iterations each = 523,776 total

  ### What went wrong                       ← TSan/compile diagnostic from Tier-1
  DiscoPoP suggested do_all but TSan detected a data race...

  ### Task
  Restructure the loop at lines 1:23 in example4/bubble_sort.cpp...
  Output a unified diff only.
```

The classification, variable-facts, array-nature, and trip-count sections are only emitted when the underlying data is present, so simpler regions produce a leaner prompt.

**On budget retries the conversation continues (multi-turn):**

```
[Turn 1 — User]   initial task (as above)
[Turn 1 — Assistant]  first attempted diff
[Turn 2 — User]   "Your diff failed at 'tsan'. Diagnostic: ..."
[Turn 2 — Assistant]  second attempted diff
[Turn 3 — User]   "Your diff failed at 'compile'. Diagnostic: ..."
...
```

The controller appends each quality-gate failure as a proper user turn to `tier2_messages`. On the next budget retry `call_llm` resumes from that history — the LLM sees all previous attempts and diagnostics in their natural conversation positions, not embedded as text in a fresh prompt.

**Two-level retry logic:**

```
call_llm()
 └─ for attempt in range(max_format_retries + 1):        ← FREE retries (no budget)
       response = API call
       if response has valid diff headers → return diff
       else → append assistant response + format correction to messages
               and retry (multi-turn, same API session)

controller budget loop
 └─ while budget > 0:
       diff, tier2_messages = call_llm(..., messages=tier2_messages)   ← budget retry
       result = validate(diff)
       if result.passed → accept, break
       else → append quality-gate diagnostic as user turn to tier2_messages, continue
```

- **Format retries** (`max_format_retries=2`): free, within a single API call session. The LLM's previous bad response is shown back to it with a correction prompt. Does not consume budget.
- **Budget retries**: each one continues the same conversation — `tier2_messages` accumulates all prior assistant diffs and quality-gate failure diagnostics as proper user turns. The LLM sees the full multi-turn exchange on each retry. Consumes one budget slot per attempt.

**Prompt caching:** The system prompt is marked with `cache_control: ephemeral`. The Anthropic API caches it server-side, so it is not re-billed across budget retries within a session.

**Edit modes.** The system prompt's analysis half (`_SYSTEM_CORE`) and the evidence body (`_evidence_sections`) are identical in all three `--edit-mode`s; only the output instruction and how the agent recovers a diff differ:

```
diff      model prints a unified diff       → _extract_diff()          → gate
function  model prints the whole function   → spliced by line range    → gate
direct    model EDITS a private file copy   → diffed against the source → gate
```

In `direct` mode (`--provider claude-agent-sdk` only) `call_llm` seeds a per-region workspace with a copy of the source (`_sync_workspace`), hands the CLI session `Read`/`Edit`/`Write` confined to that directory, and afterwards reads the file back and diffs it (`_workspace_diff`). The model's prose is ignored entirely; an unchanged file returns `""` so the controller can distinguish "made no edit" from "produced no usable answer". Workspaces and CLI sessions are both keyed on `region_fingerprint` (content-based) rather than `region_id`, which DiscoPoP reassigns after a re-profile.

---

### L4 — Validator (`l4_validator.py`)

**Purpose:** Run a three-stage quality gate on every diff before it is applied to the real source file.

All three stages work on an isolated temporary directory — the real source file is never touched until the gate passes.

**Stage 1 — Apply:**
```
patch --quiet <temp_copy> <llm.patch>
```
Checks that the diff applies cleanly. Fails if the context lines don't match the source (e.g., the LLM hallucinated lines that don't exist).

**Stage 2 — Compile:**
```
clang++ <patched_file> -g -O1
```
Plain compilation with no OpenMP or instrumentation. Catches syntax errors, missing variables, wrong types.

**Stage 3 — ThreadSanitizer:**
```
clang++ <patched_file> -fsanitize=thread -fopenmp -g -O1
./tsan_binary
```
Compiles with TSan and OpenMP enabled, then runs the binary. A `WARNING: ThreadSanitizer` or `DATA RACE` in stderr means the restructured loop still has cross-iteration dependencies — the LLM's restructuring is incorrect.

**TSan false positive guard:** Loops whose body contains only I/O calls (`printf`, `fprintf`, `cout`, etc.) skip TSan. These cause spurious races on the stdout buffer even though they are thread-safe at the semantic level.

**Toolchain:** Prefers LLVM 19 (`/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`). Falls back to `clang++-19` then `clang++`. On macOS, links against `libomp` from Homebrew and injects the correct sysroot automatically.

---

### Controller (`controller.py`)

**Purpose:** Tie all four layers together into the main per-candidate processing loop.

**Full decision flowchart per candidate:**

```
┌─ Tier-1: applicable_pattern in patterns.json?
│
├── YES
│    └─ W ≥ min_workload?
│         NO  → SKIP
│         YES → Read DiscoPoP patch from patch_generator/
│               Is the loop I/O-only? → skip TSan
│               Run TSan on DiscoPoP's patch
│               PASSED → ACCEPT (write record, no LLM call)
│               FAILED → update failure_reason, fall through to Tier-2
│
└── NO → Tier-2
          dry_run? → SKIP
          snapshot source + profile (so any attempt can be undone)
          while budget > 0:
            assemble evidence (L2) with current failure_reason
            call LLM (L3) continuing conversation (tier2_messages)
            edit valid? NO  → update failure_reason, continue
            run quality gate (L4): apply → compile → TSan → correctness
            FAILED → append diagnostic as user turn, continue
                     (build errors refund the budget slot, up to --build-retries)
            PASSED → apply patch in-place, back up original, RE-PROFILE
                     │
                     └─ VERIFY: what does DiscoPoP now say about the
                        lines that changed?  (always — this is the point)
                          no_pattern     → REVERT + send DiscoPoP's fresh
                                           blockers for the rewrite, retry
                          pattern_broken → REVERT + "you exposed it, but the
                                           pragma still races/miscomputes", retry
                          no_speedup     → REVERT + "correct but not faster,
                                           this is granularity", retry
                          exposed        → ACCEPT (a deeper Tier-2 pass is
                                           still allowed to improve it)
                          ok             → ACCEPT (pragma validated + faster)
          budget exhausted → SKIP
```

**Passing the quality gate is not acceptance.** The gate only proves a rewrite is
*harmless* — it compiles and its output is byte-identical. A rewrite exists to
make DiscoPoP able to parallelize code it previously could not, so after
re-profiling the agent asks exactly that question about the lines the patch
touched (`_touched_span` → `_verify_rewrite`), and reverts when the answer is
no. Without this step the agent's headline "accepted" could mean "the LLM
rewrote the code and nothing was parallelized".

Patterns are checked largest-workload-first and the first qualifying one wins:
the question is "did anything pay off", so validating the rest only spends time
on a question already answered.

**Gate results are cached within a run** (`_validate_cached`). The verification
step measures an exposed pattern to decide whether to *keep* a restructuring,
and the depth+1 Tier-1 pass would otherwise measure the same pattern again to
decide whether to *apply* it. The cache key is `(patch, current source bytes,
skip_race_check)` — hashing the source is what makes reuse safe, since a patch
measured before another region's pragma was applied says nothing about the file
afterwards. On a hit the log says so explicitly rather than implying the gate
ran.

**Tier-1 validation matters because:** DiscoPoP's dependency graph uses instruction IDs internally but matches against source line IDs in the pattern detector. This mismatch means dependency edges are sometimes never found, and `do_all: applicable=True` is emitted for loops that have genuine cross-iteration RAW dependencies. TSan always catches this correctly.

**Re-profiling after Tier-2 acceptance (within a pass):** After the LLM's restructured code is applied to the source, the agent:
1. Re-instruments with `discopop_cxx`
2. Runs the binary to collect fresh runtime data
3. Runs `discopop_explorer` to re-detect patterns

This is necessary because DiscoPoP detects patterns dynamically — the restructured code may now expose a Do-All or Reduction that wasn't visible before.

The remaining candidates in the current pass are then **rebuilt by region ID**: each candidate whose region ID still exists in the fresh profile is updated with current pattern data (pattern ID, pragma, patch dir). Candidates whose region ID disappeared — because the restructuring changed the code structure and DiscoPoP assigned new IDs — are dropped from this pass. Those regions will be re-discovered in subsequent `--distance` passes with their new IDs.

---

## Profiler Wrapper (`CXX_wrapper.sh`)

`discopop_cxx` is a thin Python entry point that delegates to `CXX_wrapper.sh`, the shell script that invokes LLVM's `clang++` with the DiscoPoP instrumentation plugin (`LLVMDiscoPoP.dylib`) and links the runtime library (`libDiscoPoP_RT.a`).

Two fixes have been applied to the installed wrapper:

**1. Automatic `DP_PROJECT_ROOT_DIR`**

DiscoPoP's runtime reads `DP_PROJECT_ROOT_DIR` to filter which source files belong to the project. Any file whose path does not contain this prefix is assigned file ID 0 and its dependencies are discarded. Without it, profiling data from system headers and the runtime itself pollutes the dependency graph.

The wrapper now defaults it to `$PWD` when not set:

```bash
: "${DP_PROJECT_ROOT_DIR:=$(pwd)}"
export DP_PROJECT_ROOT_DIR
```

This means you simply `cd` into your project directory and run `discopop_cxx` — no manual `DP_PROJECT_ROOT_DIR=$(pwd)` prefix needed. You can still override it explicitly if your project root differs from the compilation directory.

**2. Symlink-safe libc++ detection (macOS)**

`libDiscoPoP_RT.a` is compiled against LLVM's libc++ (`std::__1::*`). On macOS, Homebrew installs LLVM as a keg-only package: `clang++-19` in `/usr/local/bin` is a symlink to the real binary under `/usr/local/opt/llvm@19/bin/clang++`. The wrapper computes the LLVM prefix by taking `dirname` twice from the clang++ path, but this only works if the symlink is resolved first.

Before the fix, the wrapper computed:
```
which clang++-19  →  /usr/local/bin/clang++-19  (symlink, not resolved)
dirname twice     →  /usr/local
libc++ lookup     →  /usr/local/lib/c++/libc++.dylib  ← does not exist → no flags added → linker error
```

After the fix:
```bash
_LLVM_BIN=$(dirname "$(readlink -f "$LLVM_CLANGPP" 2>/dev/null || echo "$LLVM_CLANGPP")")
```
```
readlink -f resolves →  /usr/local/Cellar/llvm@19/19.1.7/bin/clang-19
dirname twice        →  /usr/local/Cellar/llvm@19/19.1.7
libc++ lookup        →  /usr/local/Cellar/llvm@19/19.1.7/lib/c++/libc++.dylib  ← exists → -L/-rpath added
```

The `-L` and `-Wl,-rpath` flags for LLVM libc++ are now added automatically on macOS without any manual flags.

---

## Data Structures (`types.py`)

```python
@dataclass
class CodeRegion:
    region_id: str       # "file_id:node_id", e.g. "1:11"
    region_type: str     # "loop" | "function" | "cu"
    name: str            # function name, or "" for loops/CUs
    file_id: int
    start_line: int
    end_line: int
    iteration_count: int # loop iteration count; 1 for non-loops
    workload: int        # instructionsCount or iteration_count × loop_size

@dataclass
class HotspotCandidate:
    region: CodeRegion
    source_file: str
    pattern: Optional[dict]   # from patterns.json, or None
    confidence: float         # [0, 1]
    workload_estimate: float  # W
    score: float              # c·log₂(1+W) − λ·1[tier=2]
    tier: int                 # 1 or 2

@dataclass
class Dependency:
    dep_type: str               # RAW | WAR | WAW
    from_line: int
    to_line: int
    variable: str
    kind: str = "scalar"        # "array" (GEPRESULT element access) | "scalar"

@dataclass
class EvidencePackage:
    region_id: str
    region_type: str
    start_line: int
    end_line: int
    source_file: str
    source_region: str          # annotated source lines
    iteration_count: int
    raw_deps: List[Dependency]
    war_deps: List[Dependency]
    waw_deps: List[Dependency]
    reduction_vars: List[str]
    tier1_failure_reason: str   # updated diagnostic per retry
    prevented_deps: List[dict]  # Do-All blockers (doall_prevented.json)
    # DiscoPoP's OpenMP data-sharing classification (patterns.json):
    shared_vars: List[str]
    private_vars: List[str]
    firstprivate_vars: List[str]
    lastprivate_vars: List[str]
    classified_reduction_vars: List[str]
    # Phase-2 profiler signals:
    loop_trip_counts: List[dict]      # [{line,total,entries,avg,max}] granularity
    local_vars_in_region: List[str]   # loop-local (already private) vars
    static_only_vars: List[str]       # static-only (likely spurious) dep vars
    # (enclosing-function fields for --edit-mode function omitted)

@dataclass
class ValidationResult:
    passed: bool
    stage: str       # "apply" | "compile" | "tsan" | "accepted"
    diagnostic: str  # raw stderr from the failed stage
```

---

## CLI Reference

```
python -m discopop_agent \
    --source-file   <path/to/source.cpp>     required
    --discopop-dir  <path/to/.discopop>      required
    --budget        <int>                    default: 3
    --model         <model-id>               default: follows --provider
                                             ('haiku' for claude-agent-sdk, 'claude-opus-5'
                                              for anthropic, REQUIRED for openai-compat)
    --api-key       <key>                    fallback: LLM_API_KEY env var
    --provider      {anthropic,openai-compat,claude-agent-sdk} default: claude-agent-sdk
    --api-base      <url>                    fallback: LLM_API_BASE env var (openai-compat)
    --lambda-penalty <float>                 default: 1.0
    --min-workload   <float>                  default: 0.0
    --output-dir         <path>             default: <discopop-dir>/agent_patches
    --provider           {anthropic,openai-compat,claude-agent-sdk}  default: anthropic
    --api-base           <url>              openai-compat endpoint (env: LLM_API_BASE)
    --edit-mode          {diff,function,direct}  default: follows --provider
                                            ('direct' for claude-agent-sdk, 'diff' otherwise;
                                             'direct' requires --provider claude-agent-sdk)
    --llm-pragmas / --no-llm-pragmas       default: ON (LLM writes the pragmas itself)
    --restructure-depth  <int>             default: 0
    --require-speedup / --no-require-speedup   default: ON
    --min-measured-speedup <float>         default: 1.1
    --build-retries      <int>             default: 2 (apply/compile retries, free)
    --check-input        <args>            repeatable: extra inputs correctness must match
    --apply-patches / --no-apply-patches       default: ON (write Tier-1 pragmas to source)
    --dry-run                               plan only, no LLM calls, no file changes
```

**Defaults, and why three of them are computed rather than fixed.** The out-of-the-box configuration is the one that actually produces results on this machine: `--provider claude-agent-sdk --model haiku --edit-mode direct --min-workload 0 --llm-pragmas --fast-refresh --llm-deps`, with `--require-speedup` left ON.

Three defaults are resolved after parsing because they are coupled to another flag, and a fixed value would fail at the first LLM call with an unrelated-looking error:

| flag | resolution |
|---|---|
| `--model` | `haiku` for `claude-agent-sdk` (Claude Code's own aliases), `claude-opus-5` for `anthropic`, **required** for `openai-compat` (the name is whatever your endpoint serves) |
| `--edit-mode` | `direct` for `claude-agent-sdk`, `diff` otherwise — `direct` needs a backend with file tools |
| `--llm-deps` | follows `--fast-refresh`; passing `--no-fast-refresh` silently switches it off rather than erroring, and it only errors when explicitly asked for without it |

So `--provider anthropic` on its own is a working invocation, not a broken one.

**`--budget`:** Maximum number of LLM retry attempts per region. Each retry costs one API call. A region where the LLM fails every attempt is marked as skipped.

**`--provider` / `--api-base`:** Selects the LLM backend. `anthropic` (default) uses the Anthropic API. `openai-compat` targets any OpenAI-compatible endpoint (e.g. a self-hosted vLLM server) at `--api-base` (e.g. `http://localhost:18000/v1`), with `--model` as the served model id and `--api-key` as its key. Tunnel a remote endpoint to localhost first (`ssh -fN -L 18000:localhost:18000 <user>@<server>`). `claude-agent-sdk` runs the local `claude` CLI headlessly (via the Claude Agent SDK) instead of calling the billed API directly — usage is drawn from your Claude Code subscription. Run `claude login` once; no `--api-key` is needed. `--model` accepts Claude Code's own aliases (`haiku`, `sonnet`, `opus`) as well as full model IDs, e.g. `--provider claude-agent-sdk --model haiku`. Requires `pip install claude-agent-sdk` and the `claude` CLI on `PATH`.

**`--lambda-penalty`:** Controls how much the Tier-2 LLM cost discounts a candidate's score. Higher values make the agent prefer Tier-1 (DiscoPoP) regions and skip Tier-2 (LLM-only) regions with lower workload.

**`--min-workload`:** Regions whose profiled workload proxy (`W`) is below this threshold are never processed. This is a cheap static pre-filter, not a measured speedup. Use `--min-workload 0` to include function regions, which have `workload=0` in Data.xml (only CU nodes carry `instructionsCount`).

**`--edit-mode`:** How the LLM returns a Tier-2 edit.

| mode | what the model produces | how the agent gets a diff |
|---|---|---|
| `diff` (default) | a unified diff, as text | uses it as-is (hunk headers auto-corrected) |
| `function` | the complete rewritten enclosing function, as text | splices it in by line range and self-diffs |
| `direct` | nothing textual — it **edits the file itself** with its Read/Edit/Write tools | diffs the edited file against the source |

`function` avoids diff-apply failures and is recommended for self-hosted models. `direct` goes one step further: the model never has to express the edit as text at all.

**`--edit-mode direct` in detail** (requires `--provider claude-agent-sdk`, the only backend with file tools):

- Each region gets a throwaway workspace holding a **private copy** of the source file, and the CLI session is confined to that directory (`cwd`, tools limited to `Read`/`Edit`/`Write`, no `Bash`). The real, profiled source is not reachable from there and its path is never shown to the model, so nothing can touch the project tree; the agent applies the change only after the quality gate passes, exactly as in the other modes.
- The answer is the **file's final content**, not the model's prose. The agent diffs the copy against the on-disk source and feeds that diff to the same L4 gate (apply → compile → TSan → correctness → speedup). Since the diff is generated from real file content it always applies cleanly, like `function` mode.
- Retries within a region are **cumulative**: the workspace keeps the model's earlier edits, so a second attempt refines its own rewrite against the gate diagnostic instead of restarting from the original. The workspace is re-seeded from disk whenever the real file changed underneath it (another region's patch was accepted, or this one was reverted).
- If the model leaves the file unchanged (or only touches comments/whitespace), it is re-prompted for free twice; a still-unchanged file is reported to the controller as "no change" and costs one budget slot, with the same "returning the input is not a valid answer" feedback used by `function` mode.
- Because the model can read the whole file, this is the only mode where it can consult code outside the region it is rewriting.

**`--llm-pragmas`:** Off by default. When set, the LLM writes the OpenMP pragmas **in the same edit as the restructuring**, and the agent judges that edit on its own merits instead of asking DiscoPoP to re-discover the parallelism.

What changes:

| | default (`--no-llm-pragmas`) | `--llm-pragmas` |
|---|---|---|
| system prompt | "you do NOT write pragmas" | "annotate what you parallelize; nothing downstream adds one for you" |
| Phase-A gate | apply → compile → output (sequential build) | **clauses (static)** → apply → compile → `-fopenmp` → **TSan** → output (**parallel** build) → **speedup** |
| keep / revert decision | re-profile, and keep only if DiscoPoP finds a pattern in the touched lines whose pragma is usable | the gate above — the parallelism is already in the diff |
| re-profile | decides the outcome | still runs, but only to refresh line numbers and discover new candidates |
| Phase B | annotates everything DiscoPoP can | same, minus any loop the LLM already annotated |
| Settle | a rewrite is an orphan unless a kept pragma targets a region it exposed | a self-annotated rewrite is its own justification; it can still be dropped, but only after every DiscoPoP pragma |

The three gate stages that were previously dead for an LLM rewrite come alive on their own, because `validate()` keys TSan, the `-fopenmp` build and the timing on the diff containing a `#pragma omp`. The one genuinely new stage is the **static clause check** (`check_llm_pragmas` in `controller.py`), which runs the same two rules used on DiscoPoP's generated clauses over every pragma the model's edit introduces, against the **patched** text:

- a name declared inside the loop body must not appear in any clause (not in scope at the pragma);
- a name the loop writes — or whose elements it fills, when it is an array rather than a pointer — and that later code reads must not be `private`/`firstprivate`, since those discard the writes.

That check is the only stage that can see the failure mode where the pragma compiles, races nowhere, prints the right answer on the profiled input, and still throws the loop's results away. Verified: a rewrite carrying `private(b)` on the double buffer it fills is rejected before anything is built.

**A rewrite that carries no pragma falls back to the default behaviour** — DiscoPoP's verdict after re-profiling still decides — so the two modes mix cleanly: the model annotates what it can, Phase B picks up the rest.

If re-profiling fails after a self-annotated rewrite, the rewrite is **kept** (it passed the whole gate) but Phase B is skipped for the run, since no profile then describes the file on disk.

**`--fast-refresh` / `--llm-deps`:** Off by default. After a kept Phase-A rewrite, refresh the profile **without running the instrumented program** — only `discopop_cxx` runs, and the previous run's observed dependences are translated onto the new instruction numbering (`fast_refresh.py`).

Measured cost of one re-profile, by step:

| step | example4 (513 elem) | array_accumulator (104M ops) | needs the program to run? |
|---|---|---|---|
| `discopop_cxx` | 1.80 s | 1.06 s | no |
| instrumented `./a.out` | 0.37 s | **7.91 s** (17× native) | **yes** |
| `discopop_explorer` | **6.49 s** | 3.45 s | no |

So this saves ~4% on a tiny program and ~64% on a compute-heavy one, and the multiplier grows with memory traffic — the saving is largest on exactly the programs that hurt most to profile.

**What makes it possible:** `static_dependencies.txt`, `Data.xml`, `loop_meta.txt` and `instructionID_to_lineID_mapping.txt` are all written by the *compile*, before `./a.out` has ever run. Only `dynamic_dependencies.txt`, `memory_regions.txt` and the loop trip counts need the run.

**What makes it delicate:** instruction ids come from one counter in module order, so an edit renumbers everything after it (verified: an edit in `bubble_sort` diverged the numbering at instruction 19). A dependence re-pointed at the wrong instruction doesn't fail — it silently misinforms the analysis. Four things the translation has to get right:

- the obvious key doesn't work: `instructionID_to_lineID_mapping.txt` is many-to-one (ids 3, 6, 9, 12 all → `1:6:0`) and ~20% of instructions have no position at all;
- what works is **sequence alignment** — both files are the same program's instructions in order, so old positions are rewritten into new-line coordinates and the two are aligned, letting positionless entries match by context;
- `67@43` is **not** line 43 — the number after `@` is callpath state (instruction 67 sits at line 11), which `parser.py` strips before use, so the id is translated and the state travels untouched;
- static deps live in the dynamic file too (bare id, `S-` region — 50 of 114 lines on example4) and are **dropped**, since the compile just regenerated them and the explorer reads that file separately.

Anything that cannot be translated with certainty is dropped, never guessed. Verified: an identity edit (a comment inserted) carries **64/64** dependences with 0 unmatched instructions; a real rewrite carries 3/64, correctly, because the rest belonged to code that no longer exists; and every translated dependence is independently re-checked to land on identical source text — **0 mistranslations across both**.

**When a full re-profile still happens:** before restructuring at a deeper level (`depth + 1 ≤ --restructure-depth`), and once before Phase B. A fast refresh may relocate the queue and find new regions; it is never the basis of a deeper restructuring or of Phase B. If it fails any of its own checks, the agent falls back to a full re-profile.

**`--llm-deps`** (requires `--fast-refresh`): rewritten code ends up covered by *static* dependences only, and static analysis reports a dependence whenever it cannot prove there is none — so a newly written loop is usually blocked by something that does not actually happen, with no dynamic data to settle it. This matters because a rewrite **creates new regions**, and at depth > 0 those are the regions the agent is meant to parallelize; static caution alone would keep them sequential forever.

Two rules keep the question narrow, and both were learned the hard way:

- **Only DiscoPoP's own Do-All blockers are reviewed** (`doall_prevented.json`), not every dependence in the region. The first version asked about every static dep in the rewritten lines: 76 questions on example4, of which 37 were induction variables and 3 were body-locals — things the agent already knows are never blockers, and which the L3 prompt already tells the model to ignore. It discharged 70 of 76, with at least one visibly wrong justification. Asking a model 40 questions whose answers are already known is how it learns to answer carelessly. Targeted at blockers, the same run asks **zero** questions and reaches the same result.
- **Only STATIC-origin blockers are reviewable.** A dependence DiscoPoP actually observed at run time is ground truth and is never up for discussion.

Every judgement is written to `<output-dir>/llm_deps.json`. This is the one place a model's claim enters DiscoPoP's analysis, so be clear-eyed: a wrong SPURIOUS produces a racy loop. What contains it — the model is told to answer REAL when unsure (a dependence wrongly called real costs only a missed parallelization), the record is auditable, discharged deps are matched back to the exact dependence lines they came from and the explorer is re-run (restoring the original analysis if it then fails), and any pragma resting on one still faces ThreadSanitizer, the byte-identical output check and the speedup gate.

---

### ThreadSanitizer and OpenMP barriers (`libarcher`)

TSan only reports accesses it cannot order, and it learns the order from synchronization it can *see*. It cannot see OpenMP's: the implicit barrier at the end of every `parallel for` lives inside `libomp`, which is not instrumented. The bridge is **archer**, an OMPT tool that subscribes to the runtime's callbacks and calls TSan's `AnnotateHappensBefore`/`AnnotateHappensAfter`.

Homebrew builds libomp with `-DOPENMP_ENABLE_OMPT_TOOLS=OFF`, so **no archer ships with it**. Without archer, TSan reports a data race between *any two parallel regions* touching the same data. Verified: a program whose second parallel loop reads what the first one wrote (indices reversed, so a different thread reads each element) is bit-identical over 20 runs at 1/2/4/8/16 threads, and TSan calls it a race.

Build one — the runtime side needs nothing, since Homebrew's libomp already has OMPT support compiled in:

```bash
discopop_agent/tools/build_archer.sh          # installs to ~/.local/lib
discopop_agent/tools/build_archer.sh /some/dir
```

It fetches `openmp/tools/archer/ompt-tsan.cpp` at the LLVM tag matching your installed libomp and builds it as a single shared library. `find_archer()` in `l4_validator.py` then picks it up automatically (`DP_ARCHER_LIB` overrides the search), `_tsan_env()` loads it via `OMP_TOOL_LIBRARIES`, and the banner prints which mode the run is in.

Measured on the three cases whose verdicts are known independently:

| diff | without archer | with archer |
|---|---|---|
| odd-even sort, `n` phases (correct) | rejected at `tsan` | **accepted** |
| odd-even sort, `n-1` phases (wrong result) | rejected at `tsan` | rejected at `correctness` — the real reason |
| naive parallel bubble sort (genuine race) | rejected at `tsan` | rejected at `tsan` |

`ignore_noninstrumented_modules=1` is set **only** alongside archer. On its own it would suppress reports raised from inside the uninstrumented runtime without supplying the ordering that makes them wrong — hiding real races as well as artefacts.

**Fallback when archer is absent.** `_is_omp_barrier_false_positive()` (controller.py) recognises the artefact from the report itself: when every racing access sits inside an `.omp_outlined*` frame but in *different* outlined functions, a barrier separates them and it cannot be a real race (same outlined function on both sides means one region, and is left alone). It is disabled when the code uses `nowait` or tasks, which genuinely remove the barrier. Suspected artefacts are never accepted on the heuristic — the gate re-runs with the race check off, so correctness and speed still have to pass.

---

**`--restructure-depth`:** Maximum discovery depth at which Tier-2 LLM restructuring is applied. Depth 0 = only the initial DiscoPoP candidates may be restructured; regions discovered after a re-profile (depth+1) get Tier-1 only. Bounds the restructuring chain so the source can't drift arbitrarily far from the original.

**`--require-speedup` / `--min-measured-speedup`:** On by default. A pragma patch is accepted only if the parallel build measurably runs at least `--min-measured-speedup`× faster than the sequential build, and a restructuring whose exposed loops show no speedup is reverted and retried. Pass `--no-require-speedup` to accept correct-but-not-faster parallelizations — appropriate when the profiled workload is too small to amortise thread startup (the agent still enforces compilation, race-freedom and identical output). Note that reverting still happens for the *other* verdicts either way: a rewrite that exposes no pattern at all is never kept.

**`--apply-patches`:** On by default. When a Tier-1 pattern passes validation, DiscoPoP's generated `#pragma omp` is written into the source file (the original is backed up to `<output-dir>/<name>.original` first). Tier-2 rewrites are always written — they are what gets re-profiled. Pass `--no-apply-patches` to leave the source untouched for Tier-1 and only record the result in `accepted.json`, with the patch left in `patch_generator/`. The agent's deliverable is a parallelized program, so the default is to produce one: without this, a run that proved a 5× parallelization ended with the user's file unchanged.

**`--check-input`:** Extra program arguments the rewrite must **also** reproduce, repeatable. Correctness is otherwise judged on a single input, so a rewrite that is right for the profiled size and wrong at 0, 1, or an odd count passes — exactly the "bound carried over from the old schedule" failure the L3 prompt warns about. Verified: a partition whose bound is right for even `n` and wrong for odd `n` passes the gate on one input and fails it once `999` is added. Inputs the original program cannot run cleanly are dropped with a warning.

**`--build-retries`:** How many apply/compile failures may be retried **without** consuming budget (default 2). A build error is a mechanical fix that says nothing about the model's parallelization idea, so charging a full attempt for one wastes the region's real chances; the cap keeps a model that cannot produce compiling code from looping forever.

**`--dry-run`:** Prints the priority table and Tier-1 decisions but never calls the LLM or modifies any file. Useful for inspecting what the agent would do.

**API key resolution order:** `--api-key` CLI argument → `LLM_API_KEY` environment variable → `.env` file in the project root.

---

## Benchmark

`discopop_agent/benchmark/` runs the whole pipeline over eight cases — one per
cause in the L3 taxonomy, plus a Do-All baseline the LLM should never be asked
about — and reports what the agent actually achieved.

```bash
venv/bin/python -m discopop_agent.benchmark.run --list
venv/bin/python -m discopop_agent.benchmark.run --cases stencil_war --verbose
venv/bin/python -m discopop_agent.benchmark.run          # all eight
```

The verdict is **measured by the driver, not reported by the agent**: after the
agent finishes, the driver compiles the original source sequentially and the
agent's final source with `-fopenmp`, runs both, and compares wall time and
stdout itself. Verdicts are `FASTER`, `parallel-not-faster`,
`changed-not-parallel`, `no-change`, and `BROKEN` — the last meaning the output
differs from the original, which is exactly what the correctness gate exists to
prevent and should never appear.

Each run writes `runs/<timestamp>/report.md`, `results.json`, and per case the
agent log, the diff it produced, and its `.discopop` directory. See
`benchmark/README.md` for the case list and the design rules that keep the
cases fair under a byte-identical-output contract.

---

## Output Files

All outputs are written to `--output-dir` (default: `<discopop-dir>/agent_patches/`).

| File | Contents |
|------|----------|
| `accepted.json` | List of all accepted regions with tier, pattern/patch info |
| `region_<id>_tier2.patch` | The unified diff applied by Tier-2 for region `<id>` |
| `<source>.original` | Backup of the source file before the first Tier-2 patch |

The source file itself is patched in-place by the `patch` command after a Tier-2 quality gate passes.

---

## Running the Full Demo

### Prerequisites

```bash
# 1. Set up the virtual environment
python3 -m venv venv

# 2. Install all packages
venv/bin/pip install . ./profiler ./library
```

### Step-by-step (example4/bubble_sort.cpp)

```bash
# 3. Clean previous run
rm -rf example4/a.out example4/.discopop

# 4. Static analysis + instrumentation
cd example4
discopop_cxx bubble_sort.cpp -o a.out

# 5. Profiling run (collects dynamic dependencies)
./a.out

# 6. Pattern analysis
cd .discopop && discopop_explorer
cd ../..

# 7. Run the agent (set LLM_API_KEY, or use --provider openai-compat)
python -m discopop_agent \
    --source-file  example4/bubble_sort.cpp \
    --discopop-dir example4/.discopop \
    --model claude-opus-4-8 \
    --min-workload 0
```

### Expected output

```
┌─ loop 1:6 (lines 23–29)  score=14.5
│  [Tier-1] Pattern #1 (do_all): #pragma omp parallel for  (W=23045)
│  [Tier-1] Running TSan validation on generated patch...
│  [Tier-1] Validation FAILED (stage=tsan) — DiscoPoP false positive
│  [Tier-1] Escalating to Tier-2 (LLM restructuring)
│  [Tier-2] Assembling evidence (budget remaining: 2)
│  [Mock-LLM] Returning pre-computed diff for region 1:6 (line 23)
│  [Tier-2] Diff received — running quality gate (apply/compile/TSan)
│  [Tier-2] Quality gate PASSED
│  [Tier-2] Original backed up → bubble_sort.cpp.original
│  [Tier-2] Re-profiling to refresh pattern data...
│  [Tier-2] Re-profiling complete (1 remaining)
└─ ACCEPTED

SUMMARY: 2 accepted | 1 skipped
  ✓ loop 1:6  [Tier-2]
  ✓ loop 1:28 [Tier-1]
```

---

## Using a Real LLM API Key

```bash
export LLM_API_KEY=sk-ant-...

python -m discopop_agent \
    --source-file  example4/bubble_sort.cpp \
    --discopop-dir example4/.discopop \
    --model        claude-opus-4-8 \
    --budget       3 \
    --min-workload  0
```

Or place the key in a `.env` file in the project root:

```
LLM_API_KEY=sk-ant-...
```

The agent will load it automatically on startup without requiring any environment variable export.

---

## Known Limitations

**1. DiscoPoP false positives are pervasive.**
DiscoPoP's dependency graph mismatches instruction IDs against source line IDs. As a result, Do-All is frequently reported for loops with genuine cross-iteration RAW dependencies. Tier-1 TSan validation exists specifically to catch this, but it means Tier-1 acceptance rates are lower than DiscoPoP's raw pattern count suggests.

**2. Function-level workload is always 0 in Data.xml.**
`instructionsCount` is only populated for CU (basic block) nodes. Loops derive a workload proxy from `iteration_count × body_size`; functions have no equivalent fallback and always score 0. Patterns that carry a `workload` field in `patterns.json` can override this, but pure Tier-2 function candidates are always filtered out by `--min-workload` unless you pass `--min-workload 0`.

**3. Re-profiling uses the same binary entry point.**
`_reprofil()` always runs `./a.out` with the arguments supplied via `--reprofil-args`. If the restructured function is only reachable through a specific call path that `main()` does not exercise by default, pass the required arguments so re-profiling covers the right code paths:

```bash
python -m discopop_agent ... --reprofil-args sort input.txt
```

If `--reprofil-args` is omitted the binary is invoked with no arguments.

**4. Region tracking across re-profiling relies on content fingerprints.**
DiscoPoP assigns region IDs from a single global counter, so patching one function renumbers regions in every function after it. The agent therefore tracks regions across a re-profile by a normalized **source-text fingerprint** rather than by ID. Two byte-for-byte identical regions in the same file are indistinguishable to the fingerprint and may be matched arbitrarily; folding the function name and surrounding context into the fingerprint reduces but does not fully eliminate this.
