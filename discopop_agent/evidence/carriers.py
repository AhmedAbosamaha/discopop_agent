"""
What carries an observed dependence
------------------------------------
A dependence between two lines of a loop is one of three things, and they mean
different things for a rewrite:

  iteration   both accesses happen in the SAME iteration of the loop that holds
              both lines — the later statement uses what the earlier one just did;
  loop        they happen in DIFFERENT iterations of that loop, in one activation
              of it — the loop carries the dependence;
  outside     they happen in different activations of that loop: carried by a loop
              around it, or between two calls of the function.

Until prompt version 3 the agent told these apart by which VARIABLE DiscoPoP's
Do-All detector names for which loop (`render.order_statement`, D4).  The detector
records one blocker per loop, the first it meets, and a variable name cannot say
whether a flow stays inside one iteration — so the statement depended on the
profile's draw and was wrong on true recurrences (record §6, 4 Oct 2026; T0.16).

The profile itself holds the answer.  Every dependence in
`dynamic_dependencies.txt` names both accesses as `<instruction>@<state>`, and
`stateID_to_callpath_mapping.txt` spells each state out:

    main-->main_loopstate1-->call_87-->kernel-->kernel_loopstate0-->kernel_loopstate1

a call path, and for every function on it the state of that function's loops.  A
loop state's digits are one per loop of the function — the iteration class of
that loop (0, 1, 2: the iteration number modulo 3) or 3 for a loop the access is
not in — and the chain of states lists the loops in the order they were entered,
outermost first.  Two accesses of one function are compared loop by loop from the
outside in: the first loop whose class differs carries the dependence.

A dependence on a function's own scalar (a stack variable) is recorded WITHOUT states
(`41 NOM  RAW 33|x(S-…)`): its relation is `unknown`.  Such a variable lives in one call
of the function, so a reader of this table treats `unknown` as "possibly inside one
activation" — never as proof that a flow comes from outside.

Limits, stated because the statement built on this is shown to a model:
  * the class is the iteration number modulo 3, so a dependence between
    iterations 3, 6, … apart reads as `iteration`; the errors that follow are on
    the careful side (an order is withheld, or a pair is called mutual);
  * a state names a call PATH, not a call: two calls of a function from the same
    place in the same iteration class of the caller's loop cannot be told apart.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .deps import _classify_var, _load_instruction_lines, _typed_targets

_LOOPSTATE = re.compile(r"^(?P<fn>.+)_loopstate(?P<digits>\d+)$")
_CALL = re.compile(r"^call_\d+$")

# (type, later access's line, earlier access's line, variable) -> the relations it was observed in
Relations = Dict[Tuple[str, int, int, str], Set[str]]


def load_state_paths(profiler_dir: Path) -> Dict[str, List[str]]:
    """state id -> the elements of its call path; {} when the profile has no mapping."""
    out: Dict[str, List[str]] = {}
    f = profiler_dir / "stateID_to_callpath_mapping.txt"
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        sid, _, path = raw.partition(" ")
        out[sid.strip()] = [e for e in path.strip().split("-->") if e]
    return out


def _frame(path: List[str]) -> Tuple[Tuple[str, ...], List[str]]:
    """(the call path down to and including the function that executes the access, that function's own
    chain of loop states)."""
    last_fn = -1
    for i, e in enumerate(path):
        if not _LOOPSTATE.match(e) and not _CALL.match(e):
            last_fn = i
    return tuple(path[:last_fn + 1]), path[last_fn + 1:]


def _loops(chain: List[str]) -> Optional[Tuple[List[int], Dict[int, str]]]:
    """From a function's chain of loop states: the loops the access sits in — by their position in the
    state's digits, outermost first — and the iteration class of each.  None when the chain is not one."""
    order: List[int] = []
    digits = ""
    for e in chain:
        m = _LOOPSTATE.match(e)
        if not m:
            return None
        digits = m.group("digits")
        for pos, d in enumerate(digits):
            if d != "3" and pos not in order:
                order.append(pos)
    active = [p for p in order if p < len(digits) and digits[p] != "3"]
    return active, {p: digits[p] for p in active}


def relation(later: List[str], earlier: List[str]) -> Optional[Tuple[str, int]]:
    """(relation, depth) of two accesses of ONE function, given their call paths: relative to the innermost
    loop of that function that holds both — `depth` loops of the function hold both.  None when they are
    not accesses of one function, share no loop of it, or a path cannot be read."""
    frame_l, chain_l = _frame(later)
    frame_e, chain_e = _frame(earlier)
    if not frame_l or not frame_e or frame_l[-1] != frame_e[-1]:
        return None
    loops_l, loops_e = _loops(chain_l), _loops(chain_e)
    if loops_l is None or loops_e is None:
        return None
    common: List[int] = []
    for a, b in zip(loops_l[0], loops_e[0]):
        if a != b:
            break
        common.append(a)
    if not common:
        return None
    if frame_l != frame_e:
        return "outside", len(common)
    for p in common[:-1]:
        if loops_l[1][p] != loops_e[1][p]:
            return "outside", len(common)
    inner = common[-1]
    return ("loop" if loops_l[1][inner] != loops_e[1][inner] else "iteration"), len(common)


def load_flow_relations(profiler_dir: Path, file_id: Optional[int], start_line: int, end_line: int,
                        loop_spans: Optional[List[Tuple[int, int]]] = None) -> Relations:
    """For every RAW and WAR whose two accesses lie on lines of [start_line, end_line] (of `file_id`, in a
    project): the relations it was observed in.  Keys carry the variable without DiscoPoP's `[]`.

    `loop_spans` — the (first, last) lines of the loops around these lines, from the explorer's loop nodes —
    is the cross-check: the call paths of a record must show as many common loops as hold both of its lines
    in the source; a record that does not is left out rather than believed."""
    out: Relations = {}
    paths = load_state_paths(profiler_dir)
    dep_file = profiler_dir / "dynamic_dependencies.txt"
    if not paths or not dep_file.exists():
        return out
    instr = _load_instruction_lines(profiler_dir)

    def place(token: str) -> Tuple[int, Optional[List[str]]]:
        ins, _, state = token.partition("@")
        f, ln = instr.get(ins.strip(), (0, 0))
        if file_id is not None and f != file_id:
            return 0, None
        return ln, paths.get(state.strip()) if state.strip() else None

    for line in dep_file.read_text().splitlines():
        parts = line.strip().split()
        if len(parts) < 4 or parts[1] != "NOM":
            continue
        later_line, later_path = place(parts[0])
        if not (start_line <= later_line <= end_line):
            continue
        for dep_type, target in _typed_targets(parts):
            if dep_type not in ("RAW", "WAR"):
                continue
            to_part, var_part = target.split("|", 1)
            earlier_line, earlier_path = place(to_part)
            if not (start_line <= earlier_line <= end_line):
                continue
            var = _classify_var(var_part.split("(")[0])[0]
            var = var[:-2] if var.endswith("[]") else var
            key = (dep_type, later_line, earlier_line, var)
            if not later_path or not earlier_path:            # recorded without states: a stack scalar
                out.setdefault(key, set()).add("unknown")
                continue
            rel = relation(later_path, earlier_path)
            if rel is None:
                continue
            if loop_spans:
                lo, hi = min(later_line, earlier_line), max(later_line, earlier_line)
                if sum(1 for a, b in loop_spans if a <= lo and hi <= b) != rel[1]:
                    continue
            out.setdefault(key, set()).add(rel[0])
    return out
