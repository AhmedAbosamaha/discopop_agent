# Pitfalls — things that have already gone wrong

Read this before trusting any measurement or writing any new harness code.

## 1. `discopop_cxx` APPENDS to every artifact and never truncates

Profiling into a directory that already holds an analysis **merges the two**. Measured on
one unchanged source, three profiles into the same directory:

| Artifact | 1st | 2nd | 3rd |
|---|---|---|---|
| `Data.xml` | 444 | 888 | 1332 |
| mapping | 90 | 180 | 270 |
| static deps | 23 | 46 | 69 |

**Fixed** — `_reprofil` and `_reprofil_fast` in `profiling/runner.py` both `rmtree` the
profiler directory first, and the harness's `_full_profile` does the same.

Two things make this the most important entry here:

- The corruption **flattered** the results. One case scored a perfect 6/6 and revealed
  **five** unsafe divergences once fixed. Corruption that penalised would have been found
  immediately.
- **The measuring instrument shared a defect with the subject.** That belongs in the
  threats-to-validity chapter, stated plainly. It reads as competence, not embarrassment.

Prior art exists: the incremental-analysis literature documents that invalidation tracking
is where soundness bugs live, with the Infer static analyzer as a named case. This is a
known hazard class, not a one-off slip.

## 2. Bare-id dependence rows are the observed data

Rows without callpath state carry a **bare instruction id**. They are ~71% of the data,
have zero overlap with `static_dependencies.txt`, and that file does not even exist after
a compile-only build. An early version of `remap_dependencies` **dropped them**.

## 3. The `@` number is callpath state, not a line number

`evidence/deps.py` misread it. Check any new code that parses dependence lines.

## 4. Memory-region ids are not comparable across builds

They are pointer-derived. Instruction ids **are** deterministic for identical source —
that asymmetry is what makes translation possible at all.

## 5. Synthesized dependence rows must be MERGED per sink, not appended

Appended rows are silently shadowed. Proved by appending a full profile's 60 rows and
observing **zero** effect on the explorer. `_merge_rows` in `llm/dep_reconstruct.py`.

## 6. Seeding: chained vs stepped arms

`fast-llm` is a **chained** arm and was initially not seeded from `full`, unlike the
stepped arms. This produced a string of wrong diagnoses on `prefix_sum` loop 27/28 — lost
dependence, trip counts, corrupted profiles, model over-reporting — all wrong. The cause
was the missing seed. **Check seeding before diagnosing an arm.**

## 7. The contradiction check cries wolf without a filter

Four spurious contradictions on induction variables and body locals. `_not_carried`
filters them (4 → 0). A reported contradiction count taken without `source_lines` passed
through is noise.

## 8. The repo is NOT black-formatted

50 of 52 files would change. **Match the surrounding manual style**; do not run the
formatter across the tree.

## 9. mypy baseline is 82

Not zero. Regressions introduced three times during one session — a dataclass field
missing a default, a bare `-> tuple` without type args, a shadowed name plus a late
import. Check against 82, not against clean.

## 10. Timing tolerance was a bare `>`

`phases/settle.py` compared `t_final > reference_time` with no margin, producing 5 false
failures in 8 on identical source. Any new timing comparison needs the noise floor.

## 11. A failed experiment worth not repeating

A trip-count **span** rule was added to `remap_loop_counters` to carry counts across
re-indentation. It dropped counts over a re-indented brace and made trip problems worse
(8 → 12). Relaxed to semantic lines, then **removed entirely** when a clean-baseline
measurement showed zero effect. `remap_loop_counters` is header-only, deliberately.
