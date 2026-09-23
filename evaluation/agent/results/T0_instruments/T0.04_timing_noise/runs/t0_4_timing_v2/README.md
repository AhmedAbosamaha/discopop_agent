# T0.4 (repeat) — how much a timed measurement varies on the experiment host

160 timed runs of four benchmarks in three conditions, under the load the campaign actually runs
at: **median 5,701, peak 6,758**. The September pass was taken at 15–430 and never finished.

**The headline:** on a single run the variation reaches 1.131× (`2mm` in two lanes), which is
above our 1.1× acceptance threshold. The harness compares the **median of 5** on each side, so
the resolvable ratio is 1 + 2·CV/√5 and the worst case anywhere becomes **1.058×**. The threshold
holds on every benchmark — because of the repeats, not despite the load.

| benchmark | CV | one run | median of 5 |
|---|---:|---:|---:|
| `tsvc/s211` | 0.7 % | 1.015× | 1.007× |
| `jacobi-2d` | 1.3 % | 1.026× | 1.012× |
| `2mm` | 3.3 % | 1.065× | 1.029× |
| `hotspot` | 5.2 % | 1.104× | 1.046× |

Variation is a property of the benchmark, not of the load: `s211` stays at 0.7 % while `hotspot`
sits at 5.2 % on the same machine at the same moment. Two lanes raise `2mm` to 6.5 % and leave
the others alone, so headline speed numbers are taken one job per node.

Produced by `agent/tools/timing_noise.py --serial-only --repeats 10 --first-node 1 --lanes 2`.
See THESIS_EXPERIMENTS.md §7 `t0_4_timing_v2`.
