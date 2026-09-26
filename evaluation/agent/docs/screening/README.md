# Benchmark screening (26 Sep 2026)

The author's decision 5 (record §6, 26 Sep): every experiment gets benchmarks where its mechanism can
matter, chosen without bias. The property of each experiment was written into the record BEFORE this
screen (record §6, "The benchmark property of every experiment"). Whole sources were then screened
against those properties, every candidate listed with its in/out reason:

- `brief.md` — what the screeners were given (properties, hard constraints, the selection rule).
- `tsvc2_all_151_loops.md` — all 151 TSVC-2 loop functions (one row each).
- `burkardt_rodinia_polybench42.md` — every John Burkardt serial/OpenMP pair, Rodinia 3.1's serial/OpenMP
  pairs, and the PolyBench/C 4.2 kernels new or changed since 3.2.

Two read-only agents (default model) did the reading; no tool or model result was consulted. Their
claims are the screeners' until checked: a sample was read against the sources by hand (record §6), and
every selected benchmark still passes the measured pre-flight (T0.1 sizes, T0.10 expert ≥ 1.1×, T0.11
class ×3, T0.13, the routing pre-check for E2-B1) before any agent trial.
