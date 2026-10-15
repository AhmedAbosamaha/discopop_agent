# E8 — what was read by hand (15 Oct 2026, no model)

The registered read-out is `../e8_readout.md` (`../build.sh`). What it lists "to be read by hand", and the three wrong
programs, were read with these scripts; each output file was written by the script beside it, run from the repository
root (the replays on the Mac).

| script | output | what it reads |
|---|---|---|
| `broken_replay.py OUT SMALL TRIAL…` | `broken_replay_small.txt` | the three BROKEN programs and their originals built sequentially (the pragmas ignored) with the package's harness header at the agent's check size, once printing the digest and once every value (`-DPB_FULL_DUMP`), on the shipped input and on the perturbed input 7: the digests are byte-identical, 46, 68 and 1 of 160,001 values differ |
| `broken_positions.py BIN_DIR` | `broken_positions_small.txt` | where those values sit: none on a position the digest reads (both ends, the middle 32 and every `LEN_1D / 2000`-th index — every 16th at this size; `pb_emit_array` in `prepared/_harness/tsvc_c2/<loop>.h`) |
| `fix107_by_hand.py` | `fix107_by_hand.txt` | the 54 trials the read-out lists with candidate Fix 107's pattern after a repair of Settle's finished-program check: in every one the finished program kept no pragma — the repairs (each "slower than the original") dropped them all, then the rewrites went as orphans; no orphan drop could have missed a pragma |
| `speed_by_depth.py` | `speed_by_depth.txt` | the 18 loops: the median speed-up of the FASTER programs at depth 0 (E3's cells), 1 and 2 |
| (read by hand) | `forms_depth_set.md` | the depth set: the form each changed program reached — the original, step 1 or the final form — against the references (registered) |

The three BROKEN programs, read in their trial folders (`final/`, `agent_patches/`): in each the wrong rewrite is the
last level's (`s121` depth 1, `s281` depth 1 — the function, `s127` depth 2), judged `ok` by D40 (3.27×, 2.20×, 1.99×);
the rewrites kept before it are correct. Each copies an array to break a dependence and takes the copy where it misses
the change `dummy()` makes to that array between two repetitions — `s121` copies `a` for the next repetition before
`dummy()`, `s281` refreshes its copy of `a` before `dummy()`, `s127` computes with a copy of `c` taken before the
`dummy()` call that now precedes the computation — so the program reads, at the positions `dummy()` changes, values
one repetition old.
