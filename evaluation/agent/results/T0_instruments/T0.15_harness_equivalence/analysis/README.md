# T0.15 on the fixed DiscoPoP — read-out (27 Sep 2026)

**Question.** Does packaging v4 (the measurement harness in a header outside the model's file, D39,
reversed for E2-B1) change anything but the harness — the program's output, and DiscoPoP's view of the
code under test?

**Runs.** `t0_15_fixed_a`, `t0_15_fixed_b` (`checks/`): `tools/harness_equivalence.py`, the 33 TSVC
packages of E1–E2, v3 (`prepared/tsvc`) against v4 (rendered by `prepare_tsvc.py --layout v4`), one
profile of each layout per run; server (rms14562, LLVM 20), repository at `0581de3d` — DiscoPoP with
B4, B8, B9, B10 and B12 fixed; no model. Draw a 27 Sep 14:38–15:02 UTC, draw b 15:02–15:24 UTC, one
after the other.

**Read-out** (`tools/t015_compare.py`, output in `draws.md` / `draws.json`): per package, the agent's
candidates inside the kernel (type, lines relative to the kernel, tier, pattern) and the dependences in
their evidence with both endpoints in the code the layouts share (the kernel and `pb_mix`), compared
across the four profiles, so a difference between the layouts is told from DiscoPoP's draw-to-draw
variation.

| | result |
|---|---|
| output (digest, perturbed digest, full dump) | identical in both layouts, 33 of 33, both draws |
| a region crossing the 1 % share floor | none |
| **candidates on the code under test** | **identical in all four profiles, 33 of 33** |
| dependences on the code under test | same 9, draw noise 17, stable within each layout over two draws 4 (s121, s291, s3112, vpvtv), undecided 3 (s254, s255, s4113) |

Every one of the 7 non-noise dependence differences is a WAW or WAR of the kernel's store line with
itself or with `pb_mix` — a dependence carried from one repetition to the next — and they go both ways
(v3 only in s121, s254, s291; v4 only in s3112, s4113, vpvtv). None changes a candidate's tier or
pattern in any profile. Two draws cannot tell them from noise; they are the kind the draws of one
layout already differ in (17 packages).

**Against the 26 Sep draws (Mac, only B8 fixed; record §6).** There, the candidates of s254, s3112 and
s341 differed between the layouts (a loop carrying a scalar was reported Do-All in one layout — B10),
and the repetition loop was Do-All in s254, s3112 and s341 (B9). On the fixed DiscoPoP, no candidate
differs, and no repetition loop is Do-All in any of the 132 profiles.

**For E2-B1.** v4 leaves DiscoPoP's verdicts on the code under test unchanged on all 33 packages; the
dependence records the model is shown differ only in inter-repetition WAW/WAR lines, as between two
draws of one layout. E2-B1 measures every unit in v4 itself (T0.11 on v4, the selection rule), so it
does not depend on the v3 equivalence.

**Not covered.** The `dependences ADDED` lines in `results.jsonl` are an artefact of the tool: the
evidence carries no file id, so a dependence with an endpoint in the v4 header reads as a line of
the file (text "") — the read-out leaves any endpoint outside the kernel and `pb_mix` out as harness
code. Header lines with the numbers of kernel lines hold no code (includes, macros), so no header
dependence can pass for a kernel one.
