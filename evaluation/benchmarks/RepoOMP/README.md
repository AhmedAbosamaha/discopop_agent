# RepoOMP Simplified

[中文版 (Chinese)](README.zh.md)

RepoOMP generates OpenMP parallelization rewrites using a rule engine and LLM. It covers NPB and BOTS benchmarks.

Method has three steps.

1. Build a Multi-granularity Attributes Performance graph (MAP) to organize repos, files, functions, and runtime attributes.
2. Run confidence propagation and deterministic routing, splitting candidate rewrites into High, Middle, Low confidence.
3. Build a Structured Transformation Context (STC), run constrained rewrites, and verify results.

All commands below use the repo root as working directory. Adjust paths if running from a different directory.

## 1. Implementation scope

Current code covers 8 NPB programs (bt, cg, ep, ft, is, lu, mg, sp) and 8 BOTS programs (alignment, fft, floorplan, health, nqueens, sort, sparselu, strassen).

- `Method/primitive_addition/rule_transformer.py` Rule engine handles reduction detection, nested loops, and independent array patterns. Returns empty silently on mismatch.
- `Method/run_all.py` Unified entry. Rules first, LLM fallback, compile + verify + time + `_aaai.c` reference compare.
- `Method/dependency_analysis/dependency_analyzer.py` Analyzes a single C file, extracts direct function calls, global variable reads/writes, boolean dependency matrix, and heuristic loop classification.
- `Method/performance_analysis/hotspot_analyzer.py` Uses uftrace self time, absolute self-time threshold, and top-N to extract hotspots.
- `Method/primitive_addition/primitive_adder.py` Combines source code, two JSON summaries, loop classification, and fixed expert rules into a prompt for LLM.
- Current code lacks full MAP, Bear compilation database, tree-sitter, transitive confidence propagation, blocker merging, and High/Middle/Low routing artifacts.

## 2. Environment and benchmarks

NPB and BOTS directory layout.

- `benchmark/NPB3.0-omp-C/` NPB 3.0 structured OpenMP C benchmarks. Each program directory contains `XXX_#_omp.c` (baseline) and `XXX_ori.c` (expert version).
- `benchmark/bots/` BOTS subtree. Each program under `omp-tasks/` has a `Makefile`. Official run scripts are in `run/`. `benchmark/bots/serial_repo/` holds the serial baseline each BOTS program is compared against; regenerate it with `Method/gen_bots_serial.py`.
- `method_data/NPB/NPB_RepoOMP/` and `method_data/BOTS/BOTS_RepoOMP/` contain `_aaai.c` reference sources.

NPB build uses `benchmark/NPB3.0-omp-C/Makefile`. `make cg CLASS=W` produces `bin/cg.W`.

Current [`make.def`](benchmark/NPB3.0-omp-C/config/make.def):

- C compiler `gcc`
- C compile flags `-O0 -fopenmp`
- C linker `gcc`
- C link flags `-fopenmp -lm`
- C common header dir `-I../common`
- Random number implementation `randdp`
- C timer source `wtime.c`

See [`README.install`](benchmark/NPB3.0-omp-C/Doc/README.install) for NPB install instructions and [`benchmark/NPB3.0-omp-C/README`](benchmark/NPB3.0-omp-C/README) for version info.

## 3. Prerequisites

Run the setup script to install all dependencies:

```bash
bash setup.sh
```

This installs:

- **Clang** (LLVM IR generation)
- **GCC** with OpenMP
- **GNU Make**
- **uftrace** (performance hotspot analysis)
- Python package `openai`

Set API credentials for LLM-based transformation:

```bash
export REPOOMP_API_KEY='your key'
export REPOOMP_API_BASE='https://your-api-endpoint/v1'
export REPOOMP_MODEL='your-model'
```

Check local tools:

```bash
python3 --version
python3 -c 'import openai; print(openai.__version__)'
clang --version
gcc --version
make --version
uftrace --version
```

If `uftrace` is not in `PATH`, add its directory to `PATH` or set the `UFTRACE` variable in the hotspot script.

## 4. Verify NPB environment first

Do this step first. It needs no API and does not change algorithm source code. It only generates or updates NPB build artifacts and `CG/npbparams.h`.

```bash
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W
cd ../..
```

Success criteria:

- `make cg CLASS=W` exits with code 0
- `./bin/cg.W` prints `VERIFICATION SUCCESSFUL`
- Output includes `Threads = 4` and `Time in seconds`

`make clean` removes NPB subdirectory object files, `npbparams.h`, core files, and benchmark executables under `bin/`. Back up any build artifacts you want to keep.

If this step fails, check `benchmark/NPB3.0-omp-C/config/make.def`, GCC OpenMP support, and `common/` files. Do not proceed to the API stage.

## 5. Full auto run

Cover all programs:

```bash
python3 Method/run_all.py --suite all --class W --threads 4 --runs 5 --out res/final.json
```

Run individual programs:

```bash
python3 Method/run_all.py --suite npb --name cg --class W --threads 4 --runs 5 --out res/cg.json
python3 Method/run_all.py --suite bots --name fft --threads 4 --runs 3 --out res/fft.json
```

Pipeline order:

1. Rule engine generates optimized versions (reduction, nested loops, independent array patterns).
2. If rule engine produces no pragma or compilation fails, fall back to LLM.
3. If LLM also fails, record failure and continue with other programs.
4. Compile optimized version, run functional verification, take best of 5 timing runs.
5. Build `_aaai.c` reference, verify and time the same way.
6. Output JSON with accepted, speedup, and other fields.

## 6. Step-by-step execution

### 6.1 Dependency analysis

Dependency analysis uses clang to parse source code. But NPB programs depend on `npbparams.h` generated by `make`. Run make once for the target program:

```bash
cd benchmark/NPB3.0-omp-C
make cg CLASS=W
cd ../..
```

Then run dependency analysis:

```bash
python3 Method/dependency_analysis/dependency_analyzer.py \
  --src 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --out res/pipeline/cg/dependency_analysis/dep.json \
  --include=-Ibenchmark/NPB3.0-omp-C/common \
  --flag=-fopenmp
```

Arguments:

- `--src` Required. Path to C source.
- `--out` Required. JSON output path.
- `--include` Repeatable. Include path for Clang.
- `--flag` Repeatable. Extra flag for Clang.

Output:

- `res/pipeline/cg/dependency_analysis/dep.json`
- `res/pipeline/cg/dependency_analysis/dep.json.ll`

### 6.2 Performance analysis

The pipeline does not use the NPB Makefile to build `cg.W.pg`. Instead it runs the equivalent commands below. Note the linker uses `c_wtime.o`, matching `run_pipeline.py`.

```bash
mkdir -p benchmark/NPB3.0-omp-C/bin

for src in c_print_results c_randdp c_timers; do
  gcc -g -pg -O0 -fopenmp \
    -Ibenchmark/NPB3.0-omp-C/common -c \
    "benchmark/NPB3.0-omp-C/common/${src}.c" \
    -o "benchmark/NPB3.0-omp-C/common/${src}.o"
done

gcc -g -pg -O0 -fopenmp \
  -Ibenchmark/NPB3.0-omp-C/common -c \
  benchmark/NPB3.0-omp-C/common/wtime.c \
  -o benchmark/NPB3.0-omp-C/common/wtime.o

gcc -g -pg -O0 -fopenmp \
  -Ibenchmark/NPB3.0-omp-C/common -c \
  'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  -o benchmark/NPB3.0-omp-C/CG/cg.o

gcc -pg -fopenmp -lm \
  -o benchmark/NPB3.0-omp-C/bin/cg.W.pg \
  benchmark/NPB3.0-omp-C/CG/cg.o \
  benchmark/NPB3.0-omp-C/common/c_print_results.o \
  benchmark/NPB3.0-omp-C/common/c_randdp.o \
  benchmark/NPB3.0-omp-C/common/c_timers.o \
  benchmark/NPB3.0-omp-C/common/wtime.o -lm
```

Run the hotspot script:

```bash
python3 Method/performance_analysis/hotspot_analyzer.py \
  --bin benchmark/NPB3.0-omp-C/bin/cg.W.pg \
  --out res/pipeline/cg/performance_analysis/hot.json \
  --threads 4 \
  --top 10 \
  --min-self-ms 1.0
```

Arguments:

- `--bin` Required. Binary compiled with `-pg`.
- `--out` Required. JSON output path.
- `--trace-dir` Optional. Defaults to `<out>.uftrace`.
- `--threads` Default `4`.
- `--top` Default `10`.
- `--min-self-ms` Default `1.0` in milliseconds. Uses absolute self-time threshold.

The script runs `uftrace record -d <trace-dir> --no-libcall`, then `uftrace report -d <trace-dir>`. If `uftrace report` cannot parse the local output format, the script fails. Do not use this failure to judge code correctness.

### 6.3 OpenMP primitive addition

```bash
python3 Method/primitive_addition/primitive_adder.py \
  --src 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --dep res/pipeline/cg/dependency_analysis/dep.json \
  --hot res/pipeline/cg/performance_analysis/hot.json \
  --out res/pipeline/cg/primitive_addition/cg_opt.c
```

Arguments:

- `--src` Required. Target source.
- `--dep` Required. Dependency JSON.
- `--hot` Required. Hotspot JSON.
- `--out` Required. Output source path.
- `--model` Optional. Default model set in script.
- `--api-base` Optional. Default API base set in script.

The script reads API config from environment variables, not from source code:

```bash
export REPOOMP_API_KEY='your key'
```

`REPOOMP_API_KEY` is required. `REPOOMP_API_BASE` and `REPOOMP_MODEL` have defaults. The script fails loudly if the `openai` package or the key is missing. Full target source, analysis summaries, and rules are sent to the remote API. The generated prompt is written to `<out>.prompt.txt`. Output passes up to two `gcc -c -O0 -fopenmp` checks, but passing compilation does not mean correct function or better performance. Before public release, revoke any keys that were exposed in commit history and check git history.

### 6.4 Install candidate source and verify

Primitive addition output does not replace NPB build input automatically. Install and run manually:

```bash
cp res/pipeline/cg/primitive_addition/cg_opt.c benchmark/NPB3.0-omp-C/CG/cg.c
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W
cd ../..
```

Confirm output contains `VERIFICATION SUCCESSFUL`, then time it:

```bash
cd benchmark/NPB3.0-omp-C
for i in 1 2 3 4 5 6 7; do
  OMP_NUM_THREADS=4 ./bin/cg.W | grep 'Time in seconds'
done
cd ../..
```

Same for the expert baseline:

```bash
cp benchmark/NPB3.0-omp-C/CG/cg_ori.c benchmark/NPB3.0-omp-C/CG/cg.c
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W | grep -E 'VERIFICATION SUCCESSFUL|Time in seconds'
cd ../..
```

## 7. Verification rules

The paper pipeline includes Compilation check, Workload-specific executable check, and Performance check, with rollback on failure. The current prototype implements only partial checks.

Current implementation:

- Primitive addition runs GCC compile check on candidate source.
- NPB run checks output for exact string `VERIFICATION SUCCESSFUL`.
- Candidate and expert versions each run one functional check.
- Each version runs 7 times. Runs where `Time in seconds` cannot be parsed are ignored. Remaining times use the minimum.
- `speedup = expert_time / opt_time`
- Status is `PASS` only when candidate verifies successfully and `opt_time < expert_time`.
- `PASS` returns exit code `0`. Other results return exit code `1`.

The current prototype lacks full oracle, MD5, numeric tolerance, ThreadSanitizer, cross-thread protocol checks, candidate rollback, and does not check whether expert baseline verification failure stops comparison. The paper evaluation uses 16 threads and mean of 5 runs. The current prototype uses 4 threads, Class W, best-of-7. Do not mix the two.

## 8. Artifacts and side effects

Running the end-to-end pipeline cleans build files and generates or overwrites:

- `res/pipeline/cg/dependency_analysis/dep.json`
- `res/pipeline/cg/dependency_analysis/dep.json.ll`
- `res/pipeline/cg/performance_analysis/hot.json`
- `res/pipeline/cg/performance_analysis/hot.json.uftrace/`
- `res/pipeline/cg/primitive_addition/cg_opt.c`
- `res/pipeline/cg/primitive_addition/cg_opt.c.prompt.txt`
- `benchmark/NPB3.0-omp-C/CG/cg.c`
- `benchmark/NPB3.0-omp-C/CG/cg.o`
- `benchmark/NPB3.0-omp-C/CG/npbparams.h`
- `benchmark/NPB3.0-omp-C/bin/cg.W` and `cg.W.pg`
- `res/pipeline/cg/result.json`

The pipeline overwrites `CG/cg.c` again when building the expert version, then copies the candidate back to `CG/cg.c` at the end. The pipeline exits early on API failure, Clang failure, uftrace failure, generated code compilation failure, NPB build failure, or unparseable timing. Generated files are not restored.

`res/pipeline/cg/result.json` fields: `expert_time`, `expert_verified`, `opt_time`, `opt_verified`, `speedup`, `status`, `opt_times`, `exp_times`.

## 9. Directory layout

```text
Method/
  dependency_analysis/    LLVM IR analysis, dep.json, map_builder, route_router, stc_builder
  performance_analysis/  uftrace analysis, hot.json
  primitive_addition/    Rule engine, LLM rewriting, prompt, rule post-processing, reference matrix
  run_all.py             Full pipeline entry
  run_pipeline.py        Legacy CG end-to-end entry
  run_method.py          Method.md offline entry
  verify.py              NPB candidate verification and rollback
benchmark/
  NPB3.0-omp-C/          NPB 3.0 structured OpenMP C benchmarks
  bots/                  BOTS subtree
README.md                This file (English)
README.zh.md             [Chinese version](README.zh.md)
```

## 10. Limitations

Dependency analysis uses regex to parse LLVM IR. Loop classification is heuristic. Hotspot results depend on CPU, thread runtime, system load, and uftrace version. Generated results depend on a remote model and may fail to compile, fail verification, or show worse performance. Passing string verification is not proof of paper-level concurrent correctness.

The current pipeline has no candidate version management or auto-restore. To preserve source code, copy `CG/cg.c`, `Method/` artifacts, and NPB build artifacts before running.

## 11. License and citation

Code in this repo is Apache 2.0 licensed (see [LICENSE](LICENSE)). `benchmark/bots/LICENSE` applies only to the BOTS subtree. The NPB subtree retains its own notices. See [`benchmark/NPB3.0-omp-C/README`](benchmark/NPB3.0-omp-C/README) for details.

```bibtex
@misc{qian2026repoomprepositoryawarehotspotopenmp,
      title={RepoOMP: Repository-Aware Hotspot OpenMP Parallelization via Dependency-Aware Context Reduction}, 
      author={Yongjie Qian and Ke Gao and Zhibin Zhang and Shaohui Peng and Ling Li},
      year={2026},
      eprint={2608.05855},
      archivePrefix={arXiv},
      primaryClass={cs.DC},
      url={https://arxiv.org/abs/2608.05855}, 
}
```

## 12. Method entry points

See [Method/README.md](Method/README.md) for offline tools (MAP, routing, STC, verification, reference matrix, reference-guided, prototype pipeline).
