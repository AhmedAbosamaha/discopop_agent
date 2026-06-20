# Installation Guide

Complete setup guide for the DiscoPoP Agentic Controller on macOS.

---

## Prerequisites

- macOS with Homebrew
- Python 3.9 (system)
- LLVM 19 via Homebrew

### Install LLVM 19

```bash
brew install llvm@19
```

Verify:
```bash
/usr/local/opt/llvm@19/bin/clang++ --version
# expected: clang version 19.x.x
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/AhmedAbosamaha/discopop_agent.git
cd discopop_agent
git checkout agentic_DiscoPop
```

---

## 2. Create and Activate the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Verify Python version (must be 3.9):
```bash
python --version
# Python 3.9.x
```

---

## 3. Install Python Packages

```bash
pip install . ./profiler ./library
```

> **Important:** Do NOT use `-e` (editable) for the profiler:
> ```bash
> # WRONG — breaks CXX_wrapper.sh relative paths
> pip install -e ./profiler
>
> # CORRECT
> pip install ./profiler
> ```

Verify the profiler CLI is available:
```bash
venv/bin/discopop_cxx --version 2>/dev/null || echo "discopop_cxx installed"
venv/bin/discopop_explorer --help > /dev/null && echo "discopop_explorer installed"
```

---

## 4. Apply the CXX_wrapper.sh Fixes

Two bugs in the installed wrapper must be patched manually after installation.

### Find the wrapper

```bash
WRAPPER=$(find venv -name "CXX_wrapper.sh" 2>/dev/null | head -1)
echo $WRAPPER
```

### Fix 1 — Auto-set `DP_PROJECT_ROOT_DIR`

Open the wrapper and add the following lines **after the `SCRIPT_PATH=` line** at the top:

```bash
: "${DP_PROJECT_ROOT_DIR:=$(pwd)}"
export DP_PROJECT_ROOT_DIR
```

Without this fix you must manually export `DP_PROJECT_ROOT_DIR=$(pwd)` before every `discopop_cxx` invocation.

### Fix 2 — Symlink-safe LLVM prefix detection

Find the line that reads:

```bash
_llvm_libcxx="$(dirname "$LLVM_CLANGPP")/../lib/c++"
```

and replace it with:

```bash
_clangpp_real="$(readlink -f "$LLVM_CLANGPP" 2>/dev/null || echo "$LLVM_CLANGPP")"
_llvm_libcxx="$(dirname "$_clangpp_real")/../lib/c++"
```

Without this fix, `dirname` operates on the symlink path (`/usr/local/bin/clang++-19`) instead of the real binary path (`/usr/local/Cellar/llvm@19/19.1.7/bin/clang++`), causing the linker to fail with:

```
ld: library 'c++' not found
```

---

## 5. Install the LLM Client (Anthropic SDK)

```bash
pip install anthropic
```

Verify:
```bash
python -c "import anthropic; print(anthropic.__version__)"
```

---

## 6. Set the API Key

Either export it in your shell:

```bash
export LLM_API_KEY=sk-ant-...
```

Or place it in a `.env` file at the project root (loaded automatically):

```
LLM_API_KEY=sk-ant-...
```

---

## 7. Run a Full Example (example4 — Bubble Sort)

This is the canonical demo that exercises the full Tier-1 → Tier-2 → re-profile pipeline.

### Step 1 — Clean any previous run

```bash
rm -rf example4/.discopop example4/a.out
```

### Step 2 — Instrument the source

```bash
cd example4
../venv/bin/discopop_cxx bubble_sort.cpp -o a.out
```

> On macOS you may need to add explicit libc++ flags if Fix 2 was not applied:
> ```bash
> ../venv/bin/discopop_cxx bubble_sort.cpp -o a.out \
>     -L/usr/local/Cellar/llvm@19/19.1.7/lib/c++ \
>     -Wl,-rpath,/usr/local/Cellar/llvm@19/19.1.7/lib/c++
> ```

### Step 3 — Run to collect profiling data

```bash
./a.out
```

### Step 4 — Run the pattern explorer

```bash
cd .discopop
../../venv/bin/discopop_explorer
cd ../..
```

### Step 5 — Run the agent (mock LLM, no API key needed)

```bash
python -m discopop_agent \
    --discopop-dir example4/.discopop \
    --source-file   example4/bubble_sort.cpp \
    --mock-llm \
    --min-workload 0
```

Expected output summary:
```
SUMMARY: 2 accepted  |  8 skipped
  ✓  loop 1:6   [Tier-2]   ← false positive caught by TSan, restructured by LLM
  ✓  loop 1:28  [Tier-1]   ← genuine Do-All, accepted directly
```

### Step 6 — Run the agent with a real LLM

```bash
python -m discopop_agent \
    --discopop-dir example4/.discopop \
    --source-file   example4/bubble_sort.cpp \
    --model        claude-opus-4-8 \
    --budget       3 \
    --min-workload  0
```

---

## 8. Optional — Type Checking and Formatting

### Type checking

```bash
pip install mypy
venv/bin/python -m mypy --config-file=mypy.ini -p discopop_agent
```

### Formatting

```bash
pip install black
venv/bin/python -m black -l 120 discopop_agent/
```

---

## Troubleshooting

### `ld: library 'c++' not found`
CXX_wrapper.sh Fix 2 (symlink-safe LLVM prefix) was not applied. See Section 4.

### `DP_PROJECT_ROOT_DIR` not set warning
CXX_wrapper.sh Fix 1 was not applied. See Section 4. Workaround: `export DP_PROJECT_ROOT_DIR=$(pwd)` before running `discopop_cxx`.

### `No module named discopop_agent`
You are not in the project root. Run from `/Users/ahmedsamir/discopop_agent` (or wherever the repo lives), not from inside `.discopop/` or a subdirectory.

### `pip install -e ./profiler` breaks `discopop_cxx`
Editable installs place a `.pth` pointer in site-packages instead of copying the files. `CXX_wrapper.sh` uses relative paths that only work when the files are physically present. Reinstall with `pip install ./profiler` (no `-e`).

### LLM diff has wrong hunk counts (`malformed patch`)
The agent auto-corrects off-by-one hunk header counts in `_fix_hunk_headers()` (l4_validator.py). No manual action needed — this is handled transparently.
