# `agent/prepared_single/` — the one-file layout of multi-file benchmarks (NOT in git)

What is here: PolyBench kernels merged into a single file, the layout used before decision D6
(multi-file programs are profiled through a generated unity unit). Kept for T0.8, which compares
DiscoPoP on both layouts; no experiment runs on it. Regenerate:
`agent/benchmark prepare --layout single` (see `agent/tools/prepare_polybench.py`).
