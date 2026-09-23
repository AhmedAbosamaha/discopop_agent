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
from typing import List

from .llm.prompts import _CONTRACT_PRAGMA, _OMP_RULES, _PRAGMA_FORMS, _contract
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


def _system(prompt: str = "minimal") -> str:
    """`minimal` (D37, the default): the role and the tools, nothing else.  `contract` (E1-bare,
    kept to reproduce it): the baseline's own role, then the text it shared with the agent —
    THE CONTRACT as the agent states it when the model writes the pragmas, the OpenMP loop rules
    and the pragma forms."""
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
    p.add_argument("--prompt", choices=("minimal", "contract"), default="minimal",
                   help="minimal (D37): role, tools, goal, the measuring functions; contract: E1-bare's prompt")
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
    request = (_request_minimal if a.prompt == "minimal" else _request)(units, excluded)
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
