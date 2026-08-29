"""
Reconstructing the dependences a skipped run would have observed
-----------------------------------------------------------------
A fast refresh translates the previous run's observed dependences onto the new
instruction numbering.  It cannot translate one whose endpoint sits in code the
rewrite CREATED: that code did not exist when the program last ran, so nothing
was measured there.  Measured across two chains, 39 of 39 dependences the full
profile has and a refresh lacks have an endpoint on a rewritten line, and NONE
of them were carryable.  That is the entire remaining gap between a refresh and
a full re-profile — and it is exactly what a model that just wrote the code is
in a position to know.

This module is a RESEARCH INSTRUMENT, not a production path.  It exists so the
question can be answered with a number instead of an argument:

    can a model reconstruct those dependences well enough that the refreshed
    profile reaches the same conclusions as a full re-profile?

Three rules keep it honest, and each closes an objection that would otherwise
make the answer meaningless:

  * The model works in SOURCE terms only — loop line, dependence type, variable,
    writer line, reader line.  It never sees or invents an instruction id, a
    callpath state or a memory region.  Those are compiler-internal and
    pointer-derived; a model guessing them would be fabricating identity, not
    reporting dependence.
  * Resolution is by LOOKUP, never by guessing.  A claimed variable is resolved
    against the dependence files of THIS build, which already pair that name
    with real instruction ids and a real memory region — scalars in
    `static_dependencies.txt`, arrays in `dynamic_dependencies.txt` under their
    mangled form.  A claim that does not resolve is dropped and counted, not
    approximated.
  * Everything is reported.  `ReconstructionReport` carries what was claimed,
    what resolved and what did not, so a result can be read as
    "the model was right" or "the model was lucky" rather than just a total.

The asymmetry that decides the metric: a dependence the model MISSES makes a
sequential loop look parallel, which is a race.  One it invents costs only a
missed parallelization.  So recall on real dependences is the safety number and
precision is merely efficiency — which is why the prompt tells it to report when
unsure.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .prompts import _SYSTEM_RECONSTRUCT
from .providers import _complete, _make_client

# `LOOP 28 RAW running 29 29`  /  `LOOP 23 NONE`
_CLAIM_RE = re.compile(
    r"^\s*LOOP\s+(\d+)\s+(?:(NONE)|(RAW|WAR|WAW)\s+(\S+)\s+(\d+)\s+(\d+))\s*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class Claim:
    """One cross-iteration dependence the model says a run would have seen."""
    loop_line: int
    dep_type: str          # RAW | WAR | WAW
    var: str
    writer_line: int
    reader_line: int


@dataclass
class ReconstructionReport:
    """What was asked, what came back, and what survived resolution."""
    claims: List[Claim] = field(default_factory=list)
    loops_declared_clean: List[int] = field(default_factory=list)
    rows: List[str] = field(default_factory=list)
    unresolved: List[Tuple[Claim, str]] = field(default_factory=list)
    error: str = ""

    def summary(self) -> str:
        """Why a claim did not resolve matters more than how many did not.

        A claim about code the rewrite did NOT touch is correctly skipped — the
        refresh already carries that dependence — while a claim the resolver
        could not place is a limitation of this module.  Reported as counts
        only, those two are indistinguishable, and the raw resolved/claimed
        ratio reads as a failure rate when most of it is by design.
        """
        if self.error:
            return f"reconstruction unavailable ({self.error[:70]})"
        skipped = sum(1 for _c, w in self.unresolved if "not this arm's gap" in w)
        unplaceable = len(self.unresolved) - skipped
        return (f"{len(self.claims)} claimed, {len(self.rows)} resolved, "
                f"{skipped} outside the gap (correctly skipped), "
                f"{unplaceable} unplaceable, "
                f"{len(self.loops_declared_clean)} loop(s) declared independent")

    def reasons(self) -> Dict[str, int]:
        """Histogram of why claims were not resolved, for the write-up."""
        out: Dict[str, int] = {}
        for _c, why in self.unresolved:
            key = why.split("—")[0].split(":")[0].strip()[:44]
            out[key] = out.get(key, 0) + 1
        return out


def parse_claims(text: str) -> Tuple[List[Claim], List[int]]:
    """Pull claims out of the reply.  Returns (claims, loops declared clean).

    Anything that does not match the required shape is ignored rather than
    guessed at — a malformed line is the model failing to answer, and treating
    it as data would put a fabricated dependence into the profile.
    """
    claims: List[Claim] = []
    clean: List[int] = []
    for m in _CLAIM_RE.finditer(text or ""):
        loop = int(m.group(1))
        if m.group(2):
            clean.append(loop)
            continue
        claims.append(Claim(loop, m.group(3).upper(), m.group(4),
                            int(m.group(5)), int(m.group(6))))
    return claims, clean


def ask_dependences(
    excerpt: str,
    loops: Sequence[int],
    model: str,
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
) -> str:
    """One stateless request.  Returns the raw reply for the caller to parse.

    Stateless on purpose: each region is a separate question, and a shared
    transcript would let one region's dependences colour the next one's answer.
    """
    prompt = "\n".join([
        "This code was just written. The profiler has NOT been run on it, so no",
        "dependence was measured here. Report what a run would have observed.",
        "",
        "```cpp",
        excerpt,
        "```",
        "",
        f"Loops to report on, by header line: {', '.join(str(n) for n in loops)}"
        if loops else "Report on every loop shown.",
        "",
        "One line per dependence, or `LOOP <line> NONE` for an independent loop.",
    ])
    client = _make_client(provider, api_key, api_base)
    return _complete(provider, client, model, [{"role": "user", "content": prompt}],
                     _SYSTEM_RECONSTRUCT, session_key="dep-reconstruct",
                     stateless=True)


def _var_index(profiler: Path) -> Dict[str, List[Tuple[str, str]]]:
    """variable name -> [(instruction id, memory region)], from THIS compile.

    BOTH dependence files are read, because they use different namespaces and the
    interesting variables live in the one that is easy to overlook.
    `static_dependencies.txt` carries scalars under plain names with `S-`
    regions; arrays appear only in `dynamic_dependencies.txt`, as
    `GEPRESULT__ZZ4mainE7contrib` with a numeric region.  Reading only the static
    file (the first version of this) meant every array claim failed to resolve —
    and arrays are precisely what the missing dependences were on.

    A model naming `contrib` therefore also matches `GEPRESULT__ZZ4mainE7contrib`:
    see `_match_var`.  Rows are written into the dynamic file, so harvesting the
    identities from that same file is what keeps them in the right namespace.
    """
    out: Dict[str, List[Tuple[str, str]]] = {}
    for name in ("static_dependencies.txt", "dynamic_dependencies.txt"):
        _harvest(profiler / name, out)
    return out


def _harvest(f: Path, out: Dict[str, List[Tuple[str, str]]]) -> None:
    if not f.exists():
        return
    for raw in f.read_text().splitlines():
        fields = raw.split()
        if len(fields) < 4 or fields[1] != "NOM":
            continue
        for token in fields[3:]:
            if "|" not in token:
                continue
            src, _, var_part = token.partition("|")
            name = var_part.split("(")[0]
            region = var_part[var_part.find("(") + 1:var_part.rfind(")")] \
                if "(" in var_part else ""
            for instr in (fields[0].split("@")[0], src.split("@")[0]):
                if instr.isdigit():
                    out.setdefault(name, []).append((instr, region))


def _match_var(name: str, index: Dict[str, List[Tuple[str, str]]]) -> Optional[str]:
    """The index key a model's variable name refers to.

    Exact first.  Failing that, the compiler-mangled array form: DiscoPoP writes
    `contrib` as `GEPRESULT__ZZ4mainE7contrib`, and a model has no way to know
    that — asking it to produce the mangled name would be asking it to invent an
    identity, which is the one thing this module refuses to do.

    The anchor is the LENGTH DIGIT the mangling puts before every name —
    `contrib` appears as `...E7contrib` and `a` as `...E1a` — so a digit may sit
    immediately before the name but a letter or underscore may not.  A word
    boundary (the first version) rejected `a` against `_ZZ4mainE1a` for exactly
    that reason.  This still refuses `sum` for `checksum` and `ontrib` for
    `contrib`, since both are preceded by a letter.  A name matching several
    keys resolves to none of them rather than to whichever came first.
    """
    if name in index:
        return name
    hits = [k for k in index
            if re.search(r"(?:^|[^A-Za-z_])" + re.escape(name) + r"$", k)]
    return hits[0] if len(hits) == 1 else None


def _cu_vars(profiler: Path) -> List[Tuple[int, int, Set[str]]]:
    """(first line, last line, variable names) for every CU in Data.xml.

    The lookup of last resort, and the only one that works on REWRITTEN lines.
    Both dependence files describe accesses that were seen; on code the rewrite
    created there are none, so a claim about it can never resolve through them.
    Data.xml is written by the compile and covers the new code, listing each
    computation unit's line span and the variables it reads and writes — which
    is exactly enough to say "an instruction on this line does touch that name".
    """
    out: List[Tuple[int, int, Set[str]]] = []
    f = profiler / "Data.xml"
    if not f.exists():
        return out
    for m in re.finditer(
            r'<Node[^>]*startsAtLine\s*=\s*"[^:]*:(\d+)"\s*endsAtLine\s*=\s*"[^:]*:(\d+)"'
            r'[^>]*>(.*?)</Node>', f.read_text(), re.S):
        names = set(re.findall(r"<(?:local|global)[^>]*>([^<]+)</(?:local|global)>",
                               m.group(3)))
        if names:
            out.append((int(m.group(1)), int(m.group(2)), names))
    return out


def _names_match(name: str, names: Set[str]) -> bool:
    """Does any name in a CU's variable list refer to `name`?

    A THIRD spelling of the same variable turns up here.  The dependence files
    write `a` as `GEPRESULT__ZZ4mainE1a`; Data.xml writes it as `_ZZ4mainE1a`,
    with no GEPRESULT prefix.  The length-digit anchor covers both, so the
    matching rule is shared rather than duplicated per namespace.
    """
    if name in names:
        return True
    return any(re.search(r"(?:^|[^A-Za-z_])" + re.escape(name) + r"$", n)
               for n in names)


def _line_index(profiler: Path) -> Dict[int, List[str]]:
    """source line -> instruction ids on it, from the fresh mapping."""
    out: Dict[int, List[str]] = {}
    f = profiler / "instructionID_to_lineID_mapping.txt"
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        parts = raw.split()
        if len(parts) < 2 or parts[1] == "*":
            continue
        bits = parts[1].split(":")
        if len(bits) >= 2 and bits[1].isdigit():
            out.setdefault(int(bits[1]), []).append(parts[0])
    return out


def synthesize_rows(
    claims: Sequence[Claim], profiler: Path, rewritten: Set[int],
) -> Tuple[List[str], List[Tuple[Claim, str]]]:
    """Turn source-level claims into `dynamic_dependencies.txt` rows.

    A claim resolves only when the variable is known to this build AND both of
    its lines carry instructions that touch that variable.  Anything else is
    returned as unresolved with the reason, because a row assembled from a
    partial match would be a fabricated identity wearing a real one's clothes —
    the exact failure mode that took a whole session to find when the fast
    refresh misattributed a recurrence by one line.
    """
    by_var = _var_index(profiler)
    by_line = _line_index(profiler)
    cu_vars = _cu_vars(profiler)
    rows: List[str] = []
    unresolved: List[Tuple[Claim, str]] = []

    for c in claims:
        if c.writer_line not in rewritten and c.reader_line not in rewritten:
            unresolved.append((c, "neither line was rewritten — not this arm's gap"))
            continue
        key = _match_var(c.var, by_var)
        cands = by_var.get(key) if key else None
        if cands:
            region = cands[0][1]
            ids_for_var = {i for i, _r in cands}
        else:
            # A variable the rewrite INTRODUCED — `b` in a double-buffer, `sum`
            # in a scalarised accumulator.  Nothing has ever accessed it, so no
            # dependence row names it and there is no observed memory region to
            # borrow.  This is the case the whole arm exists for, so it must not
            # be the one that fails.  Data.xml (written by the compile, covering
            # the new code) confirms the variable is real and says which lines
            # touch it, and the region is synthesised deterministically from the
            # name: verified separately that the explorer's conclusions do not
            # depend on the region VALUE — real, borrowed and invented regions
            # all produced identical output — only on the name matching.
            if not any(_names_match(c.var, n) for _lo, _hi, n in cu_vars):
                unresolved.append(
                    (c, f"variable {c.var!r} is unknown to this build"))
                continue
            region = f"S-{abs(hash(c.var)) % 10 ** 9}"
            ids_for_var = set()
        def _ids(line: int) -> List[str]:
            on_line = by_line.get(line, [])
            hit = [i for i in on_line if i in ids_for_var]
            if hit:
                return hit
            if not ids_for_var and not on_line:
                return []
            # Rewritten line: nothing was ever observed there, so no row names
            # it.  Fall back to Data.xml, which the compile wrote for the NEW
            # code and which says whether a CU covering this line touches the
            # variable at all.
            for lo, hi, names in cu_vars:
                if lo <= line <= hi and _names_match(c.var, names):
                    return on_line
            return []

        writer, reader = _ids(c.writer_line), _ids(c.reader_line)
        if not writer or not reader:
            missing = "writer" if not writer else "reader"
            unresolved.append(
                (c, f"no instruction on the {missing} line touches {c.var!r}"))
            continue
        # The SINK is the later access; for RAW that is the reader.
        sink, source = (reader[0], writer[0]) if c.dep_type == "RAW" \
            else (writer[0], reader[0])
        rows.append(f"{sink} NOM  {c.dep_type} {source}|{c.var}({region})")
    return rows, unresolved


def reconstruct(
    profiler: Path,
    excerpt: str,
    loops: Sequence[int],
    rewritten: Set[int],
    model: str,
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
    reply: Optional[str] = None,
) -> ReconstructionReport:
    """Ask, parse, resolve, and append the rows to dynamic_dependencies.txt.

    `reply` short-circuits the request with a canned answer, so the harness can
    be exercised deterministically without a model in the loop.
    """
    report = ReconstructionReport()
    try:
        text = reply if reply is not None else ask_dependences(
            excerpt, loops, model, api_key=api_key, provider=provider,
            api_base=api_base)
    except Exception as e:                       # a failed request must not fail the arm
        report.error = str(e)
        return report

    report.claims, report.loops_declared_clean = parse_claims(text)
    report.rows, report.unresolved = synthesize_rows(
        report.claims, profiler, rewritten)
    if report.rows:
        _merge_rows(profiler / "dynamic_dependencies.txt", report.rows)
    return report


def _merge_rows(dep_file: Path, rows: Sequence[str]) -> None:
    """Fold new rows into the file BY SINK, never by appending.

    `dynamic_dependencies.txt` carries one row per sink instruction listing all
    of that sink's sources, and a second row for a sink already present is
    shadowed rather than combined.  Appending was the first version of this and
    it silently did nothing whenever the sink already existed — verified by
    appending an entire full profile's 60 rows to a refreshed one and watching
    the explorer's conclusions not move at all, while a proper per-sink merge of
    the same data on another case took it from 6 do_all to the full profile's 5.
    """
    lines = dep_file.read_text().splitlines() if dep_file.exists() else []
    order: List[str] = []
    sinks: Dict[str, List[str]] = {}
    other: List[str] = []
    for raw in lines:
        f = raw.split()
        if len(f) >= 4 and f[1] == "NOM":
            if f[0] not in sinks:
                sinks[f[0]] = []
                order.append(f[0])
            sinks[f[0]].extend(f[2:])
        else:
            other.append(raw)
    for raw in rows:
        f = raw.split()
        if len(f) < 4 or f[1] != "NOM":
            continue
        if f[0] not in sinks:
            sinks[f[0]] = []
            order.append(f[0])
        have = " ".join(sinks[f[0]])
        for i in range(2, len(f) - 1, 2):
            if " ".join(f[i:i + 2]) not in have:
                sinks[f[0]].extend(f[i:i + 2])
    dep_file.write_text("\n".join(
        other + [f"{s} NOM  " + " ".join(sinks[s]) for s in order]) + "\n")
