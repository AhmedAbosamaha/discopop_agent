"""
The bare-LLM baseline: just ask the model
------------------------------------------
What does the pipeline add over handing the program to the same model and asking it to
parallelize it?  This runner answers that, and nothing else.  It is deliberately NOT the
agent with switches turned off — it shares no control flow with it:

  * no DiscoPoP: no profile is read, no region ranked, no dependence or runtime shown;
  * no gate: nothing is compiled, run, raced or timed here.  Whatever the model leaves in
    the file is the result, and the experiment harness judges it exactly as it judges the
    agent's — so wrong programs are EXPECTED here, and counted;
  * one attempt, no feedback.

What it does share, so that the comparison is about the pipeline and not about access or
wording: the same model through the same client call (`_complete_claude_agent_sdk`, direct
edit mode on a private copy of the sources), and the same CONTRACT, OpenMP loop rules and
pragma forms the agent gives the model when the model writes the pragmas (output identical,
bounded extra work, heap for size-dependent buffers, signatures untouched).  Its role and
task are its own: the agent's say "a stage of DiscoPoP" and describe a profile and a gate,
none of which exists here.

    python -m discopop_agent.bare_llm --source-file s211.c --model claude-haiku-4-5-20251001 \\
        --exclude-functions main,init_array,pb_emit
    python -m discopop_agent.bare_llm --project-dir . --project-units a.c,b.c --model ...
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

from .llm.prompts import (_ASK_ANNOTATE, _CONTRACT_PRAGMA, _OMP_RULES, _PLAN_SPEC, _PRAGMA_FORMS,
                          _RULE, _contract, _granularity, _how_compared, _step)
from .llm.request import _goal, _protected_block, _task_checklist
from .llm.providers import _complete_claude_agent_sdk
from .types import GateFacts

_ROLE_BARE = (
    "You are an expert in parallel programming with OpenMP.  You are given a sequential C/C++\n"
    "program and asked to make its computation run in parallel.  You have Read / Edit / Write\n"
    "on a private working copy of the program's files; only their final content is used —\n"
    "pasting code into the reply does nothing.  You have no compiler here, so re-read\n"
    "anything you are unsure of and leave the files compiling.\n\n")


# D37 (the author, 23 Sep): the model alone gets nothing of ours that helps it parallelize —
# only how its tools work, the goal any user would state (faster, same output) and which
# functions measure the program (a rewrite of those would void the measurement, not help it).
# Until then (`--prompt contract`, E1-bare's runs) it also received the agent's contract, the
# OpenMP loop rules, the pragma forms and a task line naming transformations ("splitting a
# loop, adding a buffer, reordering statements") — about 560 words of guidance from us.
_ROLE_MINIMAL = (
    "You are an expert in parallel programming with OpenMP.  You have Read / Edit / Write on a\n"
    "private working copy of the program's files; only their final content is used.\n")


# THE MIRROR (the author, 23 Sep, revising D37 the same evening): the model alone gets the
# agent's own instructions — built here from the agent's own prompt code, so every shared
# passage is its exact text — in the mode where the model writes the pragmas (the model alone
# has nobody else to write them), minus exactly three things: DiscoPoP (the role naming it, what
# it profiled and hands over, which region to work on, its evidence), the gate DURING the run
# (the same checks are described, as what judges the finished program), and feedback / retries
# (one attempt).  A sentence of the agent's that names one of those is rewritten; nothing is
# added that the agent's model does not get.
MIRROR_GATE = GateFacts(require_speedup=True, n_inputs=2, numeric=False, stress=True)
_ROLE_MIRROR = ("You are an expert in parallel programming with OpenMP, asked to parallelize a C/C++\n"
                "program.\n\n")


def _judged_mirror(gate: GateFacts) -> str:
    """The agent's "HOW YOUR REWRITE IS CHECKED" (prompts._checked_annotate), as what judges the
    FINISHED program: the harness's verification and, afterwards, the gate's race stages.  The
    static clause pre-check is the gate's alone and is not applied to the model alone's program."""
    steps = [
        "it must compile, plain and again with -fopenmp",
        "ThreadSanitizer runs the parallel build: any real race fails it",
        "the parallel build is run repeatedly at one thread count, then at\n"
        "     other thread counts and under static, dynamic and guided schedules:\n"
        "     every run has to agree with the others",
        _how_compared(gate).replace("not only the one that was profiled", "not only the one you can see"),
        "it is timed at several thread counts against the original sequential\n"
        "     program, and has to be faster",
    ]
    body = "\n".join(f"  {i}. {t}" for i, t in enumerate(steps, 1))
    gran = _granularity(gate, len(steps), "annotate").replace(
        "  The evidence marks\nwhich loops qualify; annotate the outermost one that does",
        "  Annotate the\noutermost loop that has enough of them")
    return (_RULE + "HOW YOUR REWRITE IS JUDGED\n" + _RULE
            + "Nothing checks your work while you do it, and you get one attempt.  When you are\n"
            "done, the program as you leave it is judged:\n"
            + f"{body}\n\n"
            f"Steps 2-{len(steps)} run your loops with iterations overlapping in arbitrary order.  A\n"
            "loop you marked parallel has to give the same result whatever order its\n"
            "iterations run in — reproducing the output in serial proves nothing about\n"
            "that.  This list is the whole judgement, and a pragma you did not write is a\n"
            "loop that was never parallelized.\n\n" + gran)


def _system_mirror() -> str:
    gate = MIRROR_GATE
    ask = (_ASK_ANNOTATE
           .replace("DiscoPoP profiled one region and could not extract safe parallelism from\n"
                    "it.  Rewrite that region's sequential source so the parallelism becomes\n"
                    "explicit,", "This program runs sequentially.  Rewrite its sequential source so the\n"
                    "parallelism becomes explicit,")
           .replace("{SPEED_GOAL}", ", and is measurably faster than the original sequential program")
           .replace("Nothing downstream adds\na pragma to the code you rewrite", "Nothing adds a\npragma to the code you rewrite"))
    given = (_RULE + "WHAT WE GIVE YOU\n" + _RULE
             + "The program's source files, and nothing else.\n\n")
    out = ("\n>>> OUTPUT: edit the files yourself. <<<\n"
           "You have Read / Edit / Write on a private working copy of the program's files;\n"
           "their names are in the request.  Read them, write the short plan in your reply,\n"
           "then apply the rewrite with Edit.  Only the files' final content is used —\n"
           "pasting code into the reply does nothing.\n" + _PLAN_SPEC + "\n"
           "Leave the functions the request names as measuring the program untouched, and\n"
           "leave the files compiling — you have no compiler here, so re-read anything you\n"
           "are unsure of.\n")
    return (_ROLE_MIRROR + ask + given + _contract(gate, _CONTRACT_PRAGMA) + _judged_mirror(gate)
            + _OMP_RULES + _PRAGMA_FORMS + out)


def _request_mirror(files: List[str], excluded: List[str], protected: Tuple[str, ...] = (),
                    protected_note: str = "") -> str:
    gate = MIRROR_GATE
    goal = (_goal(True, gate)
            .replace("runs faster than the same build on one thread", "runs faster than the original sequential program")
            .replace("  Nothing re-profiles your rewrite, and nothing adds a pragma for you.",
                     "  Nothing adds a pragma for you."))
    # Packaging v4 (D39): the harness is outside the file; the lines the file shares with it are
    # described in EXACTLY the agent's words (Fix 97) — the old sentence naming the measuring
    # functions was the model alone's only (the asymmetry found in E1c class A), and stays for
    # packages that still carry the harness in the file (v3).
    keep = (_protected_block(GateFacts(protected=protected, protected_note=protected_note)) if protected
            else f"Do not change these functions — they set up, time and print the program, and the "
                 f"measurement depends on them: {', '.join(excluded)}.\n" if excluded else "")
    return ("## The program\n"
            + "".join(f"  - {f}\n" for f in files)
            + "\nThese files are in your working directory.  Read them.\n\n"
            "### Task\n"
            f"This program's computation is to be {goal}\n" + keep + "\n"
            "Worth settling before you write:\n" + _task_checklist(gate, set()) + "\n"
            ">>> Read the files, give the short plan, then APPLY the rewrite with the Edit tool. "
            "Do not print a diff or the rewritten code — the files' content is what is used. "
            "Keep the functions' names and signatures.")


def _system(prompt: str = "mirror") -> str:
    """`mirror` (the default since 23 Sep evening): the agent's own instructions minus DiscoPoP,
    the gate during the run and feedback.  `minimal` (D37 as first decided, `d36_hint_check`'s
    `bare_llm` arm): role and tools only.  `contract` (E1-bare, kept to reproduce it): the
    baseline's own role, then THE CONTRACT, the OpenMP loop rules and the pragma forms."""
    if prompt == "mirror":
        return _system_mirror()
    if prompt == "minimal":
        return _ROLE_MINIMAL
    return _ROLE_BARE + _contract(GateFacts(), _CONTRACT_PRAGMA) + _OMP_RULES + _PRAGMA_FORMS


def _request_minimal(files: List[str], excluded: List[str]) -> str:
    keep = (f"Do not change these functions — they set up, time and print the program, and the "
            f"measurement depends on them: {', '.join(excluded)}.\n" if excluded else "")
    return ("## The program\n"
            + "".join(f"  - {f}\n" for f in files)
            + "\nThese files are in your working directory.\n\n"
            "### Task\n"
            "Parallelize this program with OpenMP so that it runs faster on a multi-core machine.\n"
            "Its output must stay exactly the same.\n"
            + keep)


def _request(files: List[str], excluded: List[str]) -> str:
    may = (f"You may edit any function EXCEPT these, which are the program's own input, output, "
           f"timing and setup code and must stay exactly as they are: {', '.join(excluded)}.\n"
           if excluded else "")
    return ("## The program\n"
            + "".join(f"  - {f}\n" for f in files)
            + "\nThese files are in your working directory.  Read them.\n\n"
            "### Task\n"
            "Parallelize this program's computation with OpenMP so that it runs faster on a\n"
            "multi-core machine and prints exactly what it prints now.  Restructure the code where\n"
            "that is what it takes — splitting a loop, adding a buffer, reordering statements —\n"
            "and write the `#pragma omp` lines yourself: nothing downstream will add one.\n"
            + may +
            "Nothing will check your work before it is judged, and you get one attempt: the\n"
            "files as you leave them are compiled with -fopenmp, run at several thread counts on\n"
            "inputs larger than any you can see, and compared with the original's output.\n\n"
            "Write a short plan in your reply, then make the edits with Edit.  Only the files'\n"
            "final content counts.\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-file", default=None)
    p.add_argument("--project-dir", default=None)
    p.add_argument("--project-units", default="")
    p.add_argument("--project-include", default="")
    p.add_argument("--project-cflags", default="")
    p.add_argument("--project-ldflags", default="")
    p.add_argument("--model", required=True)
    p.add_argument("--exclude-functions", default="")
    p.add_argument("--protected-line", action="append", default=[],
                   help="a line of the file that belongs to the measurement harness (D39), repeatable")
    p.add_argument("--protected-note", default="")
    p.add_argument("--prompt", choices=("mirror", "minimal", "contract"), default="mirror",
                   help="mirror: the agent's instructions minus DiscoPoP, gate and feedback (default); "
                        "minimal: role, tools, goal; contract: E1-bare's prompt")
    a = p.parse_args()

    root = Path(a.project_dir or ".").resolve()
    units = ([u for u in a.project_units.split(",") if u] if a.project_dir
             else [a.source_file] if a.source_file else [])
    if not units:
        p.error("give --source-file, or --project-dir with --project-units")
    excluded = [x for x in a.exclude_functions.split(",") if x]

    print("\n" + "=" * 60 + "\n  Bare-LLM baseline — no DiscoPoP, no gate, one attempt\n" + "=" * 60)
    print(f"  Files          : {', '.join(units)}")
    print(f"  Model          : {a.model}")
    print(f"  Not editable   : {', '.join(excluded) or '—'}")
    print(f"  Prompt         : {a.prompt}\n")

    system = _system(a.prompt)
    protected = tuple(x.strip() for x in a.protected_line if x.strip())
    request = (_request_mirror(units, excluded, protected, a.protected_note.strip()) if a.prompt == "mirror"
               else {"minimal": _request_minimal, "contract": _request}[a.prompt](units, excluded))
    with tempfile.TemporaryDirectory(prefix="dp_bare_") as tmp:
        ws = Path(tmp)
        # A private copy of the whole program (headers included, so the model can read them);
        # only the units are ever copied back.
        for f in sorted(root.iterdir()):
            if f.is_file() and f.suffix in (".c", ".cc", ".cpp", ".h", ".hpp"):
                shutil.copy2(f, ws / f.name)
        for u in units:
            if not (ws / Path(u).name).exists():
                shutil.copy2(root / u, ws / Path(u).name)
        before = {u: (ws / Path(u).name).read_text(errors="replace") for u in units}
        key = "bare:" + hashlib.sha256("".join(before.values()).encode()).hexdigest()[:16]
        print(f"│  [bare] Calling {a.model}...")
        try:
            reply = _complete_claude_agent_sdk(a.model, system,
                                               [{"role": "user", "content": request}],
                                               key, workspace=ws, stateless=True)
        except Exception as e:                       # noqa: BLE001 - one attempt: say why it failed
            print(f"│  [bare] LLM call failed: {str(e)[:300]}")
            print("\n  SUMMARY: 0 file(s) changed  |  the call failed")
            return 1
        changed = 0
        for u in units:
            after = (ws / Path(u).name).read_text(errors="replace")
            if after != before[u]:
                (root / u).write_text(after)         # no gate: what the model left IS the result
                changed += 1
                pragmas = sum(1 for ln in after.splitlines() if ln.lstrip().startswith("#pragma omp"))
                print(f"│  [bare] {u}: edited, {pragmas} OpenMP pragma(s) in the file")
        plan = " ".join(reply.split())[:400]
        if plan:
            print(f"│  [bare] the model's plan: {plan}")
    print(f"\n  SUMMARY: {changed} file(s) changed  |  nothing was checked here — the harness judges the result")
    return 0


if __name__ == "__main__":
    sys.exit(main())
