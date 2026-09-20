# RepoOMP Simplified

RepoOMP 用规则引擎和 LLM 生成 OpenMP 并行化改写，覆盖 NPB 和 BOTS 基准测试。

方法包含三步。

1. 构建 Multi-granularity Attributes Performance graph，简称 MAP，组织仓库、文件、函数和运行时属性。
2. 执行 confidence propagation and deterministic routing，把候选改写分为 High、Middle、Low confidence。
3. 构造 Structured Transformation Context，简称 STC，执行受约束改写并验证结果。

All commands below use the repo root as working directory. Adjust paths if running from a different directory.

## 1. 实现边界

当前代码覆盖 NPB 8 个程序（bt, cg, ep, ft, is, lu, mg, sp）和 BOTS 8 个程序（alignment, fft, floorplan, health, nqueens, sort, sparselu, strassen）。

- `Method/primitive_addition/rule_transformer.py` 规则引擎处理 reduction 检测、嵌套循环、独立数组模式。不匹配则静默返回空。
- `Method/run_all.py` 统一入口。规则优先，LLM 兜底，编译+功能验证+计时+`_aaai.c` 参考对比。
- `Method/dependency_analysis/dependency_analyzer.py` 分析单个 C 文件，提取直接函数调用、全局变量读写、布尔依赖矩阵和启发式循环分类。
- `Method/performance_analysis/hotspot_analyzer.py` 使用 uftrace self time、绝对 self-time 阈值和 top-N 提取热点。
- `Method/primitive_addition/primitive_adder.py` 把源码、两个 JSON 摘要、循环分类和固定专家规则拼进 prompt 调用 LLM。
- 当前代码没有完整 MAP、Bear compilation database、tree-sitter、传递置信度传播、blocker 合并，也没有 High、Middle、Low 路由产物。

## 2. 环境和基准

NPB 和 BOTS 目录结构。

- `benchmark/NPB3.0-omp-C/` — NPB 3.0 structured OpenMP C 基准。每个程序目录包含 `XXX_#_omp.c`（基线）、`XXX_ori.c`（专家版）。
- `benchmark/bots/` — BOTS 子树。`omp-tasks/` 下每个程序有 `Makefile`，`run/` 下有官方运行脚本。`benchmark/bots/serial_repo/` 存放串行基线，用于和每个 BOTS 程序对比。用 `Method/gen_bots_serial.py` 重新生成。
- `method_data/NPB/NPB_RepoOMP/` 和 `method_data/BOTS/BOTS_RepoOMP/` — `_aaai.c` 参考源码。

NPB 构建由 `benchmark/NPB3.0-omp-C/Makefile` 完成。`make cg CLASS=W` 生成 `bin/cg.W`。

当前 [`make.def`](benchmark/NPB3.0-omp-C/config/make.def)：

- C 编译器 `gcc`
- C 编译参数 `-O0 -fopenmp`
- C 链接器 `gcc`
- C 链接参数 `-fopenmp -lm`
- C 公共头文件目录 `-I../common`
- 随机数实现 `randdp`
- C 计时源文件 `wtime.c`

NPB 原始安装说明见 [`README.install`](benchmark/NPB3.0-omp-C/Doc/README.install)，版本说明见 [`benchmark/NPB3.0-omp-C/README`](benchmark/NPB3.0-omp-C/README)。

## 3. 环境准备

运行 setup 脚本一键安装所有依赖：

```bash
bash setup.sh
```

自动安装：

- **Clang**（LLVM IR 生成）
- **GCC**，支持 OpenMP
- **GNU Make**
- **uftrace**（性能热点分析）
- Python 包 `openai`

设置 API 凭据（LLM 改写需要）：

```bash
export REPOOMP_API_KEY='your key'
export REPOOMP_API_BASE='https://your-api-endpoint/v1'
export REPOOMP_MODEL='your-model'
```

检查本地工具：

```bash
python3 --version
python3 -c 'import openai; print(openai.__version__)'
clang --version
gcc --version
make --version
uftrace --version
```

If `uftrace` is not in `PATH`, add its directory to `PATH` or set the `UFTRACE` variable in the hotspot script.

## 4. 先验证 NPB 环境

先做这一步。它不需要 API，也不改算法源码，只会生成或更新 NPB 构建产物和 `CG/npbparams.h`。

```bash
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W
cd ../..
```

成功条件：

- `make cg CLASS=W` 退出码为 0
- `./bin/cg.W` 输出 `VERIFICATION SUCCESSFUL`
- 输出包含 `Threads = 4`，输出字段通常还包含 `Time in seconds`

`make clean` 会清理 NPB 子目录对象文件、`npbparams.h`、核心文件和 `bin/` 下的基准可执行文件。需要保留的构建产物先备份。

如果这一步失败，先检查 `benchmark/NPB3.0-omp-C/config/make.def`、GCC OpenMP 支持和 `common/` 文件，不要进入 API 阶段。

## 5. 全自动运行

覆盖所有程序：

```bash
python3 Method/run_all.py --suite all --class W --threads 4 --runs 5 --out res/final.json
```

程序逐个运行：

```bash
python3 Method/run_all.py --suite npb --name cg --class W --threads 4 --runs 5 --out res/cg.json
python3 Method/run_all.py --suite bots --name fft --threads 4 --runs 3 --out res/fft.json
```

流水线顺序：

1. 规则引擎生成优化版本（reduction、嵌套循环、独立数组模式）。
2. 规则引擎未产生 pragma 或编译失败 → 降级到 LLM。
3. LLM 也失败 → 记录 failure，不阻塞其他程序。
4. 编译优化版本 → 功能验证 → 5 次计时取最优。
5. 构建 `_aaai.c` 参考，同样验证+计时。
6. 输出 JSON 含 accepted、speedup 等。

## 6. 分步执行

### 6.1 依赖分析

依赖分析需要 clang 解析源码，但 NPB 程序依赖 `make` 生成的 `npbparams.h`。先对目标程序执行一次 make 生成该文件：

```bash
cd benchmark/NPB3.0-omp-C
make cg CLASS=W
cd ../..
```

然后运行依赖分析：

```bash
python3 Method/dependency_analysis/dependency_analyzer.py \
  --src 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --out res/pipeline/cg/dependency_analysis/dep.json \
  --include=-Ibenchmark/NPB3.0-omp-C/common \
  --flag=-fopenmp
```

参数：

- `--src` 必填，C 源码路径
- `--out` 必填，JSON 输出路径
- `--include` 可重复，传给 Clang 的 include 参数
- `--flag` 可重复，传给 Clang 的额外参数

输出：

- `res/pipeline/cg/dependency_analysis/dep.json`
- `res/pipeline/cg/dependency_analysis/dep.json.ll`

### 6.2 性能分析

流水线不使用 NPB Makefile 构建 `cg.W.pg`，而是直接执行下面等价命令。注意链接使用 `c_wtime.o`，与 `run_pipeline.py` 保持一致。

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

运行热点脚本：

```bash
python3 Method/performance_analysis/hotspot_analyzer.py \
  --bin benchmark/NPB3.0-omp-C/bin/cg.W.pg \
  --out res/pipeline/cg/performance_analysis/hot.json \
  --threads 4 \
  --top 10 \
  --min-self-ms 1.0
```

参数：

- `--bin` 必填，`-pg` 编译的二进制
- `--out` 必填，JSON 输出路径
- `--trace-dir` 可选，默认 `<out>.uftrace`
- `--threads` 默认 `4`
- `--top` 默认 `10`
- `--min-self-ms` 默认 `1.0`，单位毫秒，使用绝对 self time 阈值

脚本执行 `uftrace record -d <trace-dir> --no-libcall`，然后执行 `uftrace report -d <trace-dir>`。若 `uftrace report` 无法解析本机输出格式，脚本会失败，不能据此判断代码正确性。

### 6.3 OpenMP primitive addition

```bash
python3 Method/primitive_addition/primitive_adder.py \
  --src 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --dep res/pipeline/cg/dependency_analysis/dep.json \
  --hot res/pipeline/cg/performance_analysis/hot.json \
  --out res/pipeline/cg/primitive_addition/cg_opt.c
```

参数：

- `--src` 必填，目标源码
- `--dep` 必填，依赖 JSON
- `--hot` 必填，热点 JSON
- `--out` 必填，生成源码路径
- `--model` 可选，默认值在脚本中设置。
- `--api-base` 可选，默认值在脚本中设置。

脚本从环境变量读取 API 配置，不把密钥写入源码：

```bash
export REPOOMP_API_KEY='your key'
```

`REPOOMP_API_KEY` 必须提供。`REPOOMP_API_BASE` 和 `REPOOMP_MODEL` 有默认值。缺少 `openai` 包或密钥时，脚本会明确失败。完整目标源码、分析摘要和规则会发送到远端 API。生成 prompt 写入 `<out>.prompt.txt`。输出会经过最多两次 `gcc -c -O0 -fopenmp` 检查，但编译通过不等于功能正确或性能更好。公开发布前应撤销历史中曾经暴露的密钥，并检查提交记录。

### 6.4 安装候选源码并验证

primitive addition 输出不会自动替换 NPB 的构建输入。手动安装并运行：

```bash
cp res/pipeline/cg/primitive_addition/cg_opt.c benchmark/NPB3.0-omp-C/CG/cg.c
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W
cd ../..
```

确认输出含 `VERIFICATION SUCCESSFUL` 后再计时：

```bash
cd benchmark/NPB3.0-omp-C
for i in 1 2 3 4 5 6 7; do
  OMP_NUM_THREADS=4 ./bin/cg.W | grep 'Time in seconds'
done
cd ../..
```

专家基线同样操作：

```bash
cp benchmark/NPB3.0-omp-C/CG/cg_ori.c benchmark/NPB3.0-omp-C/CG/cg.c
cd benchmark/NPB3.0-omp-C
make clean
make cg CLASS=W
OMP_NUM_THREADS=4 ./bin/cg.W | grep -E 'VERIFICATION SUCCESSFUL|Time in seconds'
cd ../..
```

## 7. 验证规则

论文流程包含 Compilation check、Workload-specific executable check 和 Performance check，失败时要求回滚。当前原型只实现部分检查。

当前实现：

- primitive addition 对候选源码执行 GCC 编译检查
- NPB 运行检查输出是否包含精确字符串 `VERIFICATION SUCCESSFUL`
- 候选版和专家版各执行一次功能检查
- 两个版本各运行 7 次，忽略无法解析 `Time in seconds` 的运行，使用剩余时间最小值
- `speedup = expert_time / opt_time`
- 只有候选验证成功且 `opt_time < expert_time` 时，状态为 `PASS`
- `PASS` 返回退出码 `0`，其他结果返回退出码 `1`

当前原型没有完整 oracle、MD5、数值容差、ThreadSanitizer、跨线程协议检查、候选回滚，也不检查专家基线验证失败后是否停止比较。论文评价使用 16 线程、5 次均值，当前原型使用 4 线程、Class W、best-of-7，两者不能混用。

## 8. 产物和副作用

运行端到端流水线会清理构建文件，并生成或覆盖：

- `res/pipeline/cg/dependency_analysis/dep.json`
- `res/pipeline/cg/dependency_analysis/dep.json.ll`
- `res/pipeline/cg/performance_analysis/hot.json`
- `res/pipeline/cg/performance_analysis/hot.json.uftrace/`
- `res/pipeline/cg/primitive_addition/cg_opt.c`
- `res/pipeline/cg/primitive_addition/cg_opt.c.prompt.txt`
- `benchmark/NPB3.0-omp-C/CG/cg.c`
- `benchmark/NPB3.0-omp-C/CG/cg.o`
- `benchmark/NPB3.0-omp-C/CG/npbparams.h`
- `benchmark/NPB3.0-omp-C/bin/cg.W` 和 `cg.W.pg`
- `res/pipeline/cg/result.json`

流水线构建专家版时会再次覆盖 `CG/cg.c`，结束时再复制候选版回 `CG/cg.c`。API 失败、Clang 失败、uftrace 失败、生成代码编译失败、NPB 构建失败或时间无法解析时，流水线会提前退出，已生成文件不会自动恢复。

`res/pipeline/cg/result.json` 字段：`expert_time`、`expert_verified`、`opt_time`、`opt_verified`、`speedup`、`status`、`opt_times`、`exp_times`。

## 9. 目录结构

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
README.zh.md             Chinese version
```

## 10. 限制

依赖分析用正则解析 LLVM IR，循环分类是启发式方法。热点结果受 CPU、线程运行时、系统负载和 uftrace 版本影响。生成结果依赖远端模型，可能不可编译、验证失败或性能下降。验证字符串通过不等于论文级并发正确性证明。

当前流水线没有候选版本管理和自动恢复机制。需要保留源码时，运行前复制 `CG/cg.c`、`Method/` 产物和 NPB 构建产物。

## 11. 许可证和引用

本仓库代码使用 Apache 2.0 许可证（见 [LICENSE](LICENSE)）。`benchmark/bots/LICENSE` 仅适用于 BOTS 子树。NPB 子树保留自身声明，详见 [`benchmark/NPB3.0-omp-C/README`](benchmark/NPB3.0-omp-C/README)。

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

## 12. 方法入口

离线工具（MAP、路由、STC、验证、参考矩阵、参考引导、原型流水线）见 [Method/README.zh.md](Method/README.zh.md)。
