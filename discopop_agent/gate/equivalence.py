"""
Comparing program output when the correct answer moves
--------------------------------------------------------
The gate used to ask one question of a patched program: are the bytes it prints
identical to the bytes the original printed?  For integer and text output that
is the right question and this module answers it in one line.  For floating
point it is the wrong question, and answering it wrongly costs correct work.

Parallelizing a reduction changes the order the additions happen in.  Floating
point addition is not associative, so the sum changes in its last bits.  That is
not an error introduced by the rewrite — it is the arithmetic doing what it
always does, and LULESH's own reference OpenMP has the property: at 48 threads
it disagrees with its serial build from about the sixteenth digit, while being
the answer LLNL ships.  A gate that demands identical bytes reverts it.

So the comparison is structural rather than textual.  Everything that is not a
number — labels, punctuation, line breaks, the count of values printed — must
still match exactly, which is what keeps this strict: a rewrite that drops a
line, renames a field, or prints a different number of results fails here just
as hard as before.  Only the digits inside numbers are allowed to move, and only
by as much as this program's own numbers already move for reasons nobody calls a
bug (`numerical_noise_floor`).

Two decisions are worth stating because they are what make the slack safe:

Integers are compared exactly.  An iteration count, an element total or a size
that changes is never rounding, so integer-formatted tokens get no tolerance at
all and any change in one is a hard failure.

Numbers are judged against the scale of the output they appear in, not against
themselves.  This is the part a plain relative tolerance gets wrong.  LULESH
prints energies around 1e5 alongside symmetry residuals around 1e-12; those
residuals are roundoff being measured directly, so two correct runs disagree
about them by a factor of two while both mean "zero".  Relative-to-itself
rejects that.  Relative to the largest magnitude in the same output accepts it,
and needs no hand-set constant, which is the whole point — the alternative is a
per-program tolerance that someone has to guess.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

# A number, but only where it stands on its own.  The lookarounds keep digits
# that are part of an identifier out of it: `T1`, `0x7ffd`, `omp_outlined.2`
# stay in the skeleton and are therefore compared literally, which is what we
# want — a thread id or an address that changes is not a rounding question.
_NUM_RE = re.compile(
    r"(?<![A-Za-z_])"
    r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
    r"(?![A-Za-z_])"
)


@dataclass
class OutputMatch:
    """Verdict on one (expected, got) pair.

    `mode` records HOW it passed, not just that it did, because the two are
    different claims: "exact" is byte-identical output, "numeric" means the
    values moved and were judged against the noise floor.  Callers write this
    into the accepted record so a later reader can tell which changes rest on
    equality and which rest on judgement.
    """
    equal: bool
    mode: str                  # "exact" | "numeric" | "structural" | "integer" | "value"
    diagnostic: str = ""
    max_deviation: float = 0.0     # largest scaled difference seen
    scale: float = 0.0             # output magnitude the comparison used


def _tokenize(text: str) -> Tuple[List[str], List[str]]:
    """Split into (skeleton, numbers).

    The skeleton is everything between the numbers, in order, so re-joining it
    with the numbers reproduces the input exactly.  Comparing skeletons is what
    enforces "same structure"; comparing numbers is where tolerance applies.
    """
    skeleton: List[str] = []
    numbers: List[str] = []
    pos = 0
    for m in _NUM_RE.finditer(text):
        skeleton.append(text[pos:m.start()])
        numbers.append(m.group())
        pos = m.end()
    skeleton.append(text[pos:])
    return skeleton, numbers


def _is_integer_token(tok: str) -> bool:
    return "." not in tok and "e" not in tok and "E" not in tok


def _output_scale(numbers: List[str]) -> float:
    """The magnitude this output lives at: the largest finite absolute value in it.

    Falls back to 1.0 for an output with no usable magnitude, which makes the
    comparison relative-to-unity rather than dividing by zero.
    """
    best = 0.0
    for tok in numbers:
        try:
            v = abs(float(tok))
        except ValueError:
            continue
        if v != float("inf") and v == v and v > best:
            best = v
    return best if best > 0.0 else 1.0


def _first_line_diff(expected: str, got: str) -> str:
    """The first line where two outputs part company, for the diagnostic."""
    e_lines, g_lines = expected.splitlines(), got.splitlines()
    for i in range(max(len(e_lines), len(g_lines))):
        e = e_lines[i] if i < len(e_lines) else "<end of output>"
        g = g_lines[i] if i < len(g_lines) else "<end of output>"
        if e != g:
            return f"first difference at line {i + 1}:\n  expected: {e}\n  got:      {g}"
    return ""


def compare_outputs(expected: str, got: str, floor: float = 0.0) -> OutputMatch:
    """Are these two outputs the same program's answer?

    `floor` is the dimensionless slack from `numerical_noise_floor`.  At 0.0 —
    the default, and what an integer-only program measures — this degrades
    exactly to byte comparison, so nothing that passes today starts failing and
    nothing that fails today starts passing.
    """
    if expected == got:
        return OutputMatch(equal=True, mode="exact")
    if floor <= 0.0:
        return OutputMatch(
            equal=False, mode="exact",
            diagnostic="output differs and no numerical slack is in effect\n"
                       + _first_line_diff(expected, got),
        )

    e_skel, e_nums = _tokenize(expected)
    g_skel, g_nums = _tokenize(got)

    if len(e_nums) != len(g_nums):
        return OutputMatch(
            equal=False, mode="structural",
            diagnostic=(
                f"the patched program printed {len(g_nums)} numbers, the original "
                f"{len(e_nums)} — a different amount of output is not a rounding "
                f"difference.\n" + _first_line_diff(expected, got)
            ),
        )
    if e_skel != g_skel:
        for i, (e_part, g_part) in enumerate(zip(e_skel, g_skel)):
            if e_part != g_part:
                return OutputMatch(
                    equal=False, mode="structural",
                    diagnostic=(
                        f"the text around the numbers changed (near value {i + 1}): "
                        f"labels, punctuation and line structure must match exactly.\n"
                        + _first_line_diff(expected, got)
                    ),
                )

    scale = _output_scale(e_nums)
    tol = floor * scale
    worst = 0.0
    for idx, (a_tok, b_tok) in enumerate(zip(e_nums, g_nums)):
        if a_tok == b_tok:
            continue
        if _is_integer_token(a_tok) or _is_integer_token(b_tok):
            return OutputMatch(
                equal=False, mode="integer",
                diagnostic=(
                    f"an integer changed: {a_tok} -> {b_tok} (value {idx + 1}). "
                    f"Counts, sizes and iteration totals are never rounding.\n"
                    + _first_line_diff(expected, got)
                ),
            )
        try:
            a, b = float(a_tok), float(b_tok)
        except ValueError:
            return OutputMatch(
                equal=False, mode="value",
                diagnostic=f"unparseable numeric token: {a_tok!r} vs {b_tok!r}",
            )
        # NaN and infinity carry meaning; they are never "close to" anything.
        if not math.isfinite(a) or not math.isfinite(b):
            return OutputMatch(
                equal=False, mode="value",
                diagnostic=(
                    f"non-finite value changed: {a_tok} -> {b_tok} (value {idx + 1})"
                ),
            )
        dev = abs(a - b) / scale
        worst = max(worst, dev)
        if abs(a - b) > tol:
            return OutputMatch(
                equal=False, mode="value", max_deviation=dev, scale=scale,
                diagnostic=(
                    f"value {idx + 1} moved further than this program's own "
                    f"numerical noise: {a_tok} -> {b_tok}, a difference of "
                    f"{abs(a - b):.3e} against an output scale of {scale:.3e} "
                    f"({dev:.2e} scaled) where the measured floor allows "
                    f"{floor:.2e}.\n" + _first_line_diff(expected, got)
                ),
            )
    return OutputMatch(equal=True, mode="numeric", max_deviation=worst, scale=scale)


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

# Builds of the SAME program whose numeric results may legitimately differ.
#
# Optimization level alone is not enough, and assuming it was is the trap here:
# under default IEEE semantics a compiler is FORBIDDEN from reassociating a
# floating-point reduction, so -O1/-O2/-O3 all emit the same left-to-right sum
# and agree to the last bit.  Calibrating from those variants alone measures a
# floor of exactly zero on precisely the programs that need slack — measured on
# a two-million-element sum, where all of -O1/-O2/-O3 agreed exactly.
#
# `-fassociative-math` is what makes this work.  It grants the compiler the same
# licence a parallel schedule takes for itself: reassociate the reduction and
# sum it in a different order.  On that same program it moves the total by 1.5e-13
# of its magnitude, which is a real, program-specific measurement of what
# reordering costs this code — the number the gate actually needs.
#
# `-ffast-math` would also do it and is deliberately NOT used: it additionally
# assumes no NaN or infinity ever occurs, which can change control flow rather
# than just rounding, and would inflate the floor with movement no correct
# parallelization could produce.
_REASSOC = ["-fassociative-math", "-fno-signed-zeros", "-fno-trapping-math"]
_CALIBRATION_VARIANTS: List[Tuple[str, str, List[str]]] = [
    ("O2", "-O2", []),
    ("O2-nofma", "-O2", ["-ffp-contract=off"]),
    ("O2-reassoc", "-O2", list(_REASSOC)),
    ("O3-reassoc", "-O3", list(_REASSOC)),
    ("O3", "-O3", []),
    ("O1", "-O1", []),
]


@dataclass
class NoiseFloor:
    """How far this program's numbers already move with no change in meaning."""
    value: float = 0.0
    variants_run: List[str] = field(default_factory=list)
    scale: float = 0.0
    diagnostic: str = ""

    @property
    def measured(self) -> bool:
        return len(self.variants_run) >= 2


def numerical_noise_floor(
    source_file: str, binary_args: Optional[List[str]] = None,
    margin: float = 10.0,
) -> NoiseFloor:
    """Measure the original program against itself under legal build variation.

    This is the numerical counterpart of `noise_floor()` in timing.py, which
    runs an unchanged program against itself to learn what timing wobble to
    ignore before believing a speedup.  Same reasoning, applied to values: learn
    what digit movement to ignore before disbelieving a rewrite.

    The variant that carries the measurement is the reassociating build (see
    `_CALIBRATION_VARIANTS`), because it is the one that reorders the program's
    additions the way a parallel schedule does.  Without it this function
    reports zero for every program, since optimization level alone may not
    reassociate floating point.

    Returns 0.0 — meaning "stay byte-exact" — whenever the program's output has
    no float in it, or every variant agreed, or too few variants built to form a
    comparison.  Integer-only programs therefore keep the strict gate for free,
    which is what the existing benchmark cases were deliberately written to be.

    `margin` widens the measured spread before it is used as slack.  Compiler
    variation is a floor, not a ceiling: schedule reordering can move a value
    further than any of these builds do, and a floor that admitted nothing beyond
    what it directly observed would reject correct parallelizations for being
    slightly noisier than the calibration.  It is deliberately not large — the
    gap between rounding and a real defect is many orders of magnitude, so a
    factor of ten costs nothing that matters.
    """
    from .patching import _compile_variant     # local: avoids an import cycle
    from .timing import _run_timed
    from .toolchain import _find_clangpp

    import shutil
    import tempfile

    clangpp = _find_clangpp()
    if clangpp is None:
        return NoiseFloor(diagnostic="no supported clang++ found")

    outputs: List[Tuple[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="dp_agent_floor_") as tmp:
        work = Path(tmp)
        dst = work / Path(source_file).name
        shutil.copy2(source_file, dst)
        for name, opt, extra in _CALIBRATION_VARIANTS:
            ok, _diag, binary = _compile_variant(
                dst, clangpp, work, f"floor_{name}", openmp=False,
                optimize=opt, extra_flags=extra,
            )
            if not ok or binary is None:
                continue
            ok_r, out, _t, _d = _run_timed(binary, work, binary_args, repeats=1)
            if ok_r:
                outputs.append((name, out))

    if len(outputs) < 2:
        return NoiseFloor(
            variants_run=[n for n, _ in outputs],
            diagnostic="fewer than two build variants ran; staying byte-exact",
        )

    base_name, base = outputs[0]
    _skel, base_nums = _tokenize(base)
    if not base_nums:
        return NoiseFloor(
            variants_run=[n for n, _ in outputs],
            diagnostic="output contains no numbers; byte comparison is exact and correct",
        )
    scale = _output_scale(base_nums)

    worst = 0.0
    for name, other in outputs[1:]:
        if other == base:
            continue
        o_skel, o_nums = _tokenize(other)
        if len(o_nums) != len(base_nums) or o_skel != _skel:
            # Different structure between builds of the same program is not
            # rounding — refuse to derive slack from it.
            return NoiseFloor(
                variants_run=[n for n, _ in outputs],
                diagnostic=(
                    f"build variant {name} changed the STRUCTURE of the output "
                    f"relative to {base_name}; not deriving a floor from that"
                ),
            )
        for a_tok, b_tok in zip(base_nums, o_nums):
            if a_tok == b_tok or _is_integer_token(a_tok):
                continue
            try:
                a, b = float(a_tok), float(b_tok)
            except ValueError:
                continue
            if not math.isfinite(a) or not math.isfinite(b):
                continue
            worst = max(worst, abs(a - b) / scale)

    return NoiseFloor(
        value=worst * margin if worst > 0.0 else 0.0,
        variants_run=[n for n, _ in outputs],
        scale=scale,
        diagnostic=(
            f"{len(outputs)} build variants agreed exactly" if worst == 0.0
            else f"widest disagreement {worst:.2e} of output scale across "
                 f"{len(outputs)} build variants, x{margin:g} margin"
        ),
    )
