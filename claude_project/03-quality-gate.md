# The quality gate

Stage order verified in `discopop_agent/gate/validate.py` on 2026-08-30.

## The principle

> No single stage concludes "correct"; the verdict is their conjunction.
> — `gate/validate.py`

Each stage establishes one narrow thing. The gate also records **which evidence carried
the verdict**, because a change accepted on exact equality and a change accepted on
numerical judgement are different claims.

## Stage order

| # | Stage | What it alone can catch |
|---|---|---|
| 1 | **clause** | a clause that compiles, races nowhere, prints the right answer, and still throws the loop's results away |
| 2 | **apply** | the diff does not apply |
| 3 | **compile** | sequential build breaks |
| 4 | **openmp_compile / tsan** | a data race, via ThreadSanitizer |
| 5 | **dependences** | the rewrite contradicts what the profile says |
| 6 | **schedules** | output that moves between runs — the stage that actually looks for races behaviourally |
| 7 | **correctness** | output differs from the golden reference at fixed threads |
| 8 | **performance** | not measurably faster (`--require-speedup`) |

A pragma-free diff skips the stages that ask whether the change is *parallel* — there is
nothing there to race or to speed up. Skipped stages are tracked in `skipped_stages`
rather than silently passing.

## Two things that are measured, not assumed

**Numerical noise floor** (`--numeric-tolerance`, on). Before judging anything, compile
the unmodified source several semantically neutral ways — with and without vectorization,
with and without FMA contraction, at two optimization levels — run each, and record how
far this program's own numbers move. A rewrite is allowed to move that far and no
further.

Why it exists: parallelizing a reduction reorders additions, which moves the last digits.
LULESH's own reference OpenMP disagrees with its serial build from the sixteenth digit; a
byte-identical gate would revert LLNL's correct answer. Programs with no floating point
measure a floor of zero and stay byte-exact. Labels, line structure, and how many values
are printed must still match exactly. Integers are never given slack.

**Gotcha:** `-fassociative-math` is not a valid neutral variant for measuring this floor.

**Schedule stress** (`--schedule-stress`, on). Run a pragma-bearing patch across thread
counts (`1,2,4`) and OpenMP schedules instead of once. A single run samples a single
interleaving, which is why an output diff alone cannot catch a race.

The discrimination rule:
- output that moves **at the same thread count** → a race → fails at any magnitude
- output stable at fixed threads that moves **across thread counts** → reordered
  arithmetic → judged against the noise floor

In thesis terms this is a **metamorphic relation**: output must be invariant under thread
count and schedule kind. Naming it as such is worth doing — it upgrades an engineering
trick into a recognised methodology.

## TSan on OpenMP

Plain ThreadSanitizer reports false races on OpenMP barriers. The fix is **libarcher**
(`tools/build_archer.sh`); Homebrew ships none, so it has to be built. There is a fallback
heuristic when it is unavailable.

## Why this gate is a contribution, not plumbing

The comparable published system, RepoOMP, accepts on *"compilation, workload-specific
checks, and positive speedup."* That is calibrated for **annotation**, where the code is
unchanged. Once the code is **rewritten**, it admits results that are wrong.

Direct evidence that a weak gate is insufficient: **DiscoPoP itself emits a racy pragma
roughly one run in six.** A compile-and-speedup gate accepts it.
