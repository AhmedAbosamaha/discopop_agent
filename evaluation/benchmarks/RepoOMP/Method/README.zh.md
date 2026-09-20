# Method 工具

从仓库根目录执行。

## 函数范围转换

分析记录函数名、文件、起止行、调用、全局读写、OpenMP、循环类别、阻塞原因和稳定证据 ID。热点按函数名、文件、起始行匹配。匹配缺失或重复时输出原文件。

只有安全热点函数进入提示词。函数只有在范围不重叠、互不调用、依赖矩阵无边、共享写入不冲突时才可共用批次。证据未知时保持串行。规则和 LLM 结果按函数范围合并。范围外修改或非 OpenMP 修改都会拒绝。

每个批次都要编译、通过工作负载校验、输出有限数值、线程数一致，且最佳时间不慢于同工作负载基线。失败批次回滚到最近接受版本。输出目录审计文件记录提示词、候选、差异、状态、拒绝原因、时间、哈希和最终哈希。

## MAP、路由、STC

```bash
python3 Method/dependency_analysis/map_builder.py \
  --root benchmark/NPB3.0-omp-C/CG \
  --out res/method_run/map.json
python3 Method/dependency_analysis/route_router.py \
  --map res/method_run/map.json \
  --out res/method_run/routes.json
```

从 `res/method_run/routes.json` 选出函数 ID 后生成 STC：

```bash
python3 Method/dependency_analysis/stc_builder.py \
  --map res/method_run/map.json \
  --routes res/method_run/routes.json \
  --function 'function:cg.c:conj_grad:227' \
  --out res/method_run/stc.json
```

MAP 记录文件节点、函数节点、调用边、全局读写边、循环、reduction、I/O、串行控制、间接内存和 blocker。路由器沿调用边传播 blocker。High 走规则，Middle 生成 STC 后再交给 LLM，Low 保持串行并记录原因。

## 验证

```bash
python3 Method/verify.py \
  --source method_data/NPB/NPB_RepoOMP/cg_aaai.c \
  --benchmark-root benchmark/NPB3.0-omp-C \
  --name cg --class W --threads 4 --runs 5 \
  --out res/reports/verify/cg.verify.json
```

验证分编译、工作负载和性能三阶段。候选失败时返回非零，源码恢复到验证前版本。验证器检查 NPB 输出中的 `VERIFICATION SUCCESSFUL`，计时解析 `Time in seconds`，保留成功解析值中的最小值。

## 参考矩阵

```bash
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite npb --class A --threads 4 --runs 5 \
  --out res/reports/matrix/npb.matrix.json
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite bots --threads 4 \
  --out res/reports/matrix/bots.matrix.json
```

NPB 参考来自 `method_data/NPB/NPB_RepoOMP/*_aaai.c`。BOTS 参考来自 `method_data/BOTS/BOTS_RepoOMP/*_aaai.c`。矩阵会把每个 BOTS 参考源码临时安装到对应 OpenMP 源文件，执行该应用目录的 `make`，再调用官方 run 脚本。`--runs` 对 NPB 和 BOTS 都生效，BOTS 每次运行都会重新解析功能验证和计时，最后恢复源码并重新构建原始版本。当前默认小输入映射为 alignment `for-omp-tasks/prot.20.aa`、fft `omp-tasks/1048576`、floorplan `omp-tasks/input.5`、health `omp-tasks/test.input`、nqueens `omp-tasks/10`、sort `omp-tasks/1048576`、sparselu `for-omp-tasks/10x10`、strassen `omp-tasks/128`。报告包含 `Verification = successful`、程序时间和可用的串行时间。BOTS 矩阵分别在原生目录构建 `_aaai.c`、专家版和 serial 版。serial 官方输出 `Verification = n/a`，报告保留该状态和计时。`--generated` 会把 BOTS 专家源码送入规则改写器，再临时替换真实 OpenMP 源文件构建和运行，候选结果单独标记为 `generated`。`--thread-list 1,4,16` 可在多个线程数下分别运行矩阵。

已登记基准可使用 exemplar 路由：

```bash
python3 Method/primitive_addition/benchmark_matrix.py \
  --suite npb --class W --threads 4 --runs 3 \
  --generated --generator exemplar \
  --out res/reports/matrix/npb.exemplar.matrix.json
```

该路由只检索 `method_data` 中同名 `_aaai.c`，不声称完成新程序推理。审计文件记录 baseline 和 exemplar 哈希。矩阵报告必须如实保留编译失败、验证失败、缺少映射和性能数据缺失，不得跳过失败项。

## 离线入口

离线入口支持保守规则候选和真实验证。规则候选验证失败时返回非零，保留失败 JSON，不覆盖 NPB 源码：

```bash
python3 Method/run_method.py \
  --suite bots \
  --transform-source 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --verify-candidate \
  --npb-class W --threads 4 --runs 1 \
  --out-dir res/method_run
```

当前规则器只接受经过词法清理、括号平衡、真实数组左值和 OpenMP 作用域检查的简单独立数组循环。含既有 OpenMP task 的源文件保持串行，避免破坏任务依赖。`--generated` 可把 NPB `_#_omp.c` 输入送入规则改写器，再执行同一矩阵验证。规则器不会生成持久 parallel region、reduction、single、task cutoff 或跨阶段同步，因此不能复现多数 `_aaai.c` 的区域级结构。NPB Class W 当前自动候选仍未达到 `_aaai.c`，失败项和性能落后项必须保留在矩阵报告中。不能把编译通过当成功。

参考引导实验只用于验证 STC 目标范围和上界，不代表自动生成结果：

```bash
python3 Method/primitive_addition/reference_guided.py \
  --source 'benchmark/NPB3.0-omp-C/CG/cg_#_omp.c' \
  --reference method_data/NPB/NPB_RepoOMP/cg_aaai.c \
  --function conj_grad \
  --out res/method_run/cg.reference-guided.c \
  --audit res/method_run/cg.reference-guided.json
```

该工具只替换指定函数，并把参考来源写入审计文件。候选仍须经过 `Method/verify.py`。

不调用远端 API 的证据和参考验收入口：

```bash
python3 Method/run_method.py \
  --suite bots --threads 4 --out-dir res/method_run
```

全套 NPB 和 BOTS：

```bash
python3 Method/run_method.py \
  --suite all --npb-class A --threads 4 --runs 3 \
  --out-dir res/method_run
```

入口生成 MAP、路由和 benchmark matrix JSON。只要 NPB 参考中有一项编译或功能失败，命令返回非零，但所有结果仍写入报告。

## 参考对比

```bash
python3 Method/primitive_addition/compare_references.py \
  --matrix res/reports/matrix/npb.matrix.json \
  --out res/reports/compare/npb.compare.json
```

比较报告只汇总编译、功能、计时和可计算 speedup。不同 Class、输入、线程、编译器或机器的时间不可直接宣称达到 `_aaai.c` 水平。当前实测 NPB Class A 参考 8/8 功能通过，BOTS 8/8 小输入功能通过。规则器不会生成跨循环 parallel region、reduction、single 或 task cutoff，因此自动候选整体仍未达到 `_aaai.c`。Method.md 列出的 FFmpeg、NCNN 和 GROMACS 工作负载当前未随本仓库提供源码、输入、构建封装和 oracle，尚未实现，不能填写通过结果。

## 原型流水线

CG 的原始三阶段 API 流程仍由下面命令提供：

```bash
python3 Method/run_pipeline.py
```

它需要远端 API，固定分析 `cg_#_omp.c`，生成 `cg_opt.c`，构建 Class W，使用 4 线程，并比较候选与 `cg_ori.c`。它不是 MAP、路由、STC 全量实现，也不会自动覆盖 NPB 和 BOTS 全部程序。