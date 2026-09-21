# T0.11 — the class of every benchmark, measured

What DiscoPoP plus the gate does on each benchmark with **no model at all**, from **three
independent profile draws** (three separate runs, because a run profiles each benchmark once and
DiscoPoP's answer depends on the draw). 166 trials, server, 20–21 Sep 2026.

| class | meaning | count |
|---|---|---:|
| **R** | DiscoPoP alone reaches nothing — where the thesis's claim is tested | **26** |
| **A** | DiscoPoP alone parallelizes it — the control, where the agent must do no harm | **26** |
| **D** | a genuine recurrence — the correct answer is to decline | **4** |

By suite: TSVC 18 R / 3 A / 4 D · PolyBench 5 R / 22 A · `md`, NPB `is`, `hotspot` R ·
`pathfinder` A. Every benchmark has at least one usable draw; none is undetermined.

**The TSVC suite validates.** All 25 loops were built with an intended class, declared in each
package's `restructuring_class`, and the measurement agrees with the design on **25 of 25** —
`class_table.py` flags any disagreement and printed none. The restructuring loops really do
defeat DiscoPoP, and the controls really are already parallel.

**Three applications are class R** — `burkardt/md`, NPB `is` and Rodinia `hotspot` — so the claim
can be tested at application scale, not only on single loops.

**Five class-A benchmarks are ones DiscoPoP alone makes SLOWER than sequential:** `ludcmp`
0.15×, `lu` 0.21×, `reg_detect` 0.25×, `atax` 0.30×, `dynprog` 0.98×. DiscoPoP produces a
verified parallel program there and harms the program doing it — a category the plan had not
named, and one where the agent's speed check should show an easy gain.

**Profile errors: 12 of 166 draws (7 %), all of them TSVC (12 of 75, 16 %), none elsewhere.**
Every one is the random explorer stall (L5), bounded at 20 minutes by the phase timeout. It falls
on different loops in different draws, which is why the class is taken from the draws that
succeeded and a failed draw is never read as "DiscoPoP found nothing".

Files: `classes.csv` (one row per benchmark), `classes.json` (every draw, with outcome, speedup,
host load and explorer time). Rebuild with
`agent/tools/class_table.py t0_11_classes_a t0_11_classes_b t0_11_classes_c --out <dir>`.
