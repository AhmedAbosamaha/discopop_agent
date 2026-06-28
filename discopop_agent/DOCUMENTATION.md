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
├── l3_llm.py        L3: LLM prompt builder + Anthropic API caller
├── l4_validator.py  L4: quality gate (apply / compile / TSan)
├── mock_llm.py      pre-computed diffs for offline testing
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
| `raw_deps` | `dynamic_dependencies.txt` | Read-after-write deps crossing iteration boundaries |
| `war_deps` | `dynamic_dependencies.txt` | Write-after-read deps |
| `waw_deps` | `dynamic_dependencies.txt` | Write-after-write deps |
| `reduction_vars` | `reduction.txt` | Variables involved in reduction patterns |
| `iteration_count` | `loop_counter_output.txt` | How many times the loop ran |
| `tier1_failure_reason` | previous stage | TSan/compile error text from last failed attempt |

**Key design point:** `tier1_failure_reason` is updated after every failed validation attempt. This means each retry gives the LLM a fresh, accurate failure diagnostic — not the same generic message every time.

---

### L3 — LLM Engine (`l3_llm.py`)

**Purpose:** Build a structured prompt from the `EvidencePackage`, call the Claude API, and return a valid unified diff.

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
    RAW — read-after-write: line 22 → 23  variable: arr
    WAR — write-after-read: none
    WAW — write-after-write: none

  ### What went wrong                       ← TSan/compile diagnostic from Tier-1
  DiscoPoP suggested do_all but TSan detected a data race...

  ### Task
  Restructure the loop at lines 1:23 in example4/bubble_sort.cpp...
  Output a unified diff only.
```

**On budget retries the conversation continues (multi-turn):**

```
[Turn 1 — User]   initial task (as above)
[Turn 1 — Assistant]  first attempted diff
[Turn 2 — User]   "Your diff failed at 'tsan'. Diagnostic: ..."
[Turn 2 — Assistant]  second attempted diff
[Turn 3 — User]   "Your diff failed at 'compile'. Diagnostic: ..."
...
```

The controller appends each quality-gate failure as a proper user turn to `tier2_messages`. On the next budget retry `call_llm` (or `call_manual`) resumes from that history — the LLM sees all previous attempts and diagnostics in their natural conversation positions, not embedded as text in a fresh prompt. `--manual-llm` mode uses the same mechanism: the full conversation history is printed to stdout before the human enters each new diff.

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
- **Budget retries**: each one continues the same conversation — `tier2_messages` accumulates all prior assistant diffs and quality-gate failure diagnostics as proper user turns. The LLM sees the full multi-turn exchange on each retry. Consumes one budget slot per attempt. `--manual-llm` mode uses the same mechanism: the human sees the full conversation history before entering each new diff.

**Prompt caching:** The system prompt is marked with `cache_control: ephemeral`. The Anthropic API caches it server-side, so it is not re-billed across budget retries within a session.

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
          while budget > 0:
            assemble evidence (L2) with current failure_reason
            call LLM (L3) continuing conversation (tier2_messages)
            diff valid? NO  → update failure_reason, continue
            run quality gate (L4)
            PASSED → apply patch in-place, back up original,
                     re-profile (refresh Tier-1 data, no new candidates),
                     ACCEPT
            FAILED → append diagnostic as user turn to tier2_messages, continue
          budget exhausted → SKIP
```

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
    --model         <model-id>               default: claude-opus-4-8
    --api-key       <key>                    fallback: LLM_API_KEY env var
    --provider      {anthropic,openai-compat} default: anthropic
    --api-base      <url>                    fallback: LLM_API_BASE env var (openai-compat)
    --lambda-penalty <float>                 default: 1.0
    --min-workload   <float>                  default: 1.0
    --output-dir    <path>                   default: <discopop-dir>/agent_patches
    --distance      <int>                    default: 0
    --dry-run                                plan only, no LLM calls, no file changes
    --mock-llm                               use pre-computed diffs (no API key needed)
```

**`--budget`:** Maximum number of LLM retry attempts per region. Each retry costs one API call. A region where the LLM fails every attempt is marked as skipped.

**`--provider` / `--api-base`:** Selects the LLM backend. `anthropic` (default) uses the Anthropic API. `openai-compat` targets any OpenAI-compatible endpoint (e.g. a self-hosted vLLM server) at `--api-base` (e.g. `http://localhost:18000/v1`), with `--model` as the served model id and `--api-key` as its key. Tunnel a remote endpoint to localhost first (`ssh -fN -L 18000:localhost:18000 <user>@<server>`).

**`--lambda-penalty`:** Controls how much the Tier-2 LLM cost discounts a candidate's score. Higher values make the agent prefer Tier-1 (DiscoPoP) regions and skip Tier-2 (LLM-only) regions with lower workload.

**`--min-workload`:** Regions whose profiled workload proxy (`W`) is below this threshold are never processed. This is a cheap static pre-filter, not a measured speedup. Use `--min-workload 0` to include function regions, which have `workload=0` in Data.xml (only CU nodes carry `instructionsCount`).

**`--distance`:** Number of additional discovery passes to run after the initial candidate list is exhausted.

- `--distance 0` (default): process only the candidates found in the original DiscoPoP profile. After each accepted Tier-2 patch the source is re-profiled to keep Tier-1 pattern data fresh for remaining original candidates, but no new regions are added to the queue mid-pass.
- `--distance 1`: after all original candidates are processed, re-profile the (now-modified) source and process any newly discovered candidate regions.
- `--distance N`: repeat the discovery-and-process cycle up to N additional times. Each pass stops early if re-profiling fails or no new candidates are found.

Use `--distance 1` to capture regions that only become parallelisable after a Tier-2 restructuring (e.g. an inner loop that was unreachable via Do-All in the original code becomes visible after double-buffering).

**`--dry-run`:** Prints the priority table and Tier-1 decisions but never calls the LLM or modifies any file. Useful for inspecting what the agent would do.

**`--mock-llm`:** Replaces every LLM call with a lookup in `mock_llm.py`. Pre-computed diffs are keyed by region start line. Used for the full demo and offline testing.

**API key resolution order:** `--api-key` CLI argument → `LLM_API_KEY` environment variable → `.env` file in the project root.

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

# 7. Run the agent (mock LLM, no API key needed)
python -m discopop_agent \
    --source-file  example4/bubble_sort.cpp \
    --discopop-dir example4/.discopop \
    --mock-llm \
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

**4. Region ID stability after re-profiling.**
The ID-based queue rebuild assumes that region IDs for code outside the patched function remain stable across re-profiling. This holds in practice — DiscoPoP traverses functions in source order, so only regions inside the modified function are renumbered. However, if a patch changes the number of functions or reorders them, IDs in unrelated functions could shift, causing those candidates to be dropped from the current pass and re-discovered (correctly) in a `--distance` pass.

**5. Mock LLM is keyed by start line only.**
`mock_llm.py` maps `region.start_line → diff`. If two different source files have regions that start at the same line number, the wrong diff may be returned. This is a demo limitation and does not affect the real LLM path.
