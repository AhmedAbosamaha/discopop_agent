#!/usr/bin/env python3
"""E8's three BROKEN programs, read by hand (Mac, no model, sequential builds — the pragmas are ignored, so what is
seen is the program's own order, not a race): build each trial's original/ and final/ with the harness's header, at a
given size, with the digest (what the agent's checks and the harness's digest compare) and with -DPB_FULL_DUMP (what
the harness's dump compares); run on the shipped input and on the perturbed input 7; report whether the digests are
byte-identical, the largest relative difference of the dumps, and where the dumps differ.

    python3 broken_replay.py OUT_DIR SIZE TRIAL_DIR...
"""
import subprocess
import sys
from pathlib import Path

HARNESS = Path("evaluation/agent/prepared/_harness").resolve()   # run from the repository root


def build(src: Path, out: Path, size: str, dump: bool) -> Path:
    units = sorted(str(p) for p in src.glob("*.c"))
    flags = ["-O2", f"-D{size}_DATASET", "-I", str(HARNESS), "-I", str(src)] + (["-DPB_FULL_DUMP"] if dump else [])
    subprocess.run(["cc", *flags, *units, "-o", str(out), "-lm"], check=True, capture_output=True, text=True)
    return out


def run(binary: Path, args: list) -> str:
    return subprocess.run([str(binary), *args], check=True, capture_output=True, text=True, timeout=600).stdout


def main() -> int:
    out_dir, size, trials = Path(sys.argv[1]), sys.argv[2], [Path(p) for p in sys.argv[3:]]
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in trials:
        tag = "__".join(t.parts[-6:-3] + t.parts[-1:])
        print(f"== {tag} at {size}")
        bins = {}
        for side in ("original", "final"):
            for dump in (False, True):
                bins[(side, dump)] = build(t / side, out_dir / f"{tag}_{side}_{'dump' if dump else 'digest'}_{size}", size, dump)
        for args in ([], ["7"]):
            d_o, d_f = run(bins[("original", False)], args), run(bins[("final", False)], args)
            v_o, v_f = run(bins[("original", True)], args).split(), run(bins[("final", True)], args).split()
            diffs = [(i, float(x), float(y)) for i, (x, y) in enumerate(zip(v_o, v_f)) if x != y]
            worst = max((abs(x - y) / max(abs(x), abs(y), 1e-300) for _, x, y in diffs), default=0.0)
            n = (len(v_o) - 1) // 5          # the result first, then a, b, c, d, e of LEN_1D each
            where = [("result" if i == 0 else "abcde"[(i - 1) // n] + f"[{(i - 1) % n}]") for i, _, _ in diffs]
            print(f"   input {'7' if args else 'shipped'}: digest {'identical' if d_o == d_f else 'DIFFERS'}; "
                  f"dump: {len(diffs)} of {len(v_o)} values differ, largest relative difference {worst:.3g}"
                  + (f"; first: {', '.join(where[:12])}" if diffs else ""))
            if d_o != d_f:
                print("      original:", d_o.replace("\n", " | "), "\n      final:   ", d_f.replace("\n", " | "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
