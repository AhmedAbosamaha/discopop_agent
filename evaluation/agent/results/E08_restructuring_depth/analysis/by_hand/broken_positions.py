#!/usr/bin/env python3
"""E8's three BROKEN programs: where the wrong values sit, against the positions the harness's digest reads.

Runs the -DPB_FULL_DUMP builds that broken_replay.py made (BIN_DIR, size SMALL — the agent's check size) on the shipped
and the perturbed input, and for every value that differs from the original's prints its array and its index modulo 16,
and how many of them lie where the digest reads: indices 0-31, the 32 around the middle, the last 32, and every
(LEN_1D / 2000)-th index from 32 on (`pb_emit_array` in the package's harness header; at SMALL, LEN_1D 32000, every 16th).

    python3 broken_positions.py BIN_DIR
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

bins = Path(sys.argv[1])
for tag in ["benchmarks__tsvc_c2__s121__rep2", "benchmarks__tsvc_c2__s281__rep1", "benchmarks__tsvc_c2__s127__rep3"]:
    for args in ([], ["7"]):
        o = subprocess.run([str(bins / f"{tag}_original_dump_SMALL"), *args], capture_output=True, text=True).stdout.split()
        f = subprocess.run([str(bins / f"{tag}_final_dump_SMALL"), *args], capture_output=True, text=True).stdout.split()
        n = (len(o) - 1) // 5
        idx = [((i - 1) // n, (i - 1) % n) for i, (x, y) in enumerate(zip(o, f)) if x != y and i > 0]
        step = max(n // 2000, 1)
        read = [p for _, p in idx if p < 32 or (n // 2 - 16 <= p < n // 2 + 16) or p >= n - 32 or (p - 32) % step == 0]
        print(tag.split("__")[2], "input", "7" if args else "shipped", "| values that differ", len(idx),
              "| arrays", dict(Counter("abcde"[a] for a, _ in idx)),
              "| index mod 16", dict(sorted(Counter(p % 16 for _, p in idx).items())),
              "| on a position the digest reads:", len(read))
