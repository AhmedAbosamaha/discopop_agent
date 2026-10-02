"""The measurement lines, kept by every arm (the author, 3 Oct 2026)
=================================================================
A benchmark's file shares a few lines with the harness that measures it: for a TSVC loop the
`#include`, the per-repetition `pb_mix(nl)` call and `PB_MAIN(kernel)`, in older packages the
timer and the digest (`pb_*`/`PB_*`). A program that changes them changes what is MEASURED, so
the harness cannot judge it (`SCAFFOLD_MODIFIED`). Every arm is told about these lines in the
same words (`llm/request.py:_protected_block`); until 3 Oct only the agent also enforced them
(Fix 97, `harness_lines.check_protected` in its gate, retry not charged). The twins and the
model alone had no such check by design (D37, D38), so when their model edited the
measurement — Fable 5.1 alone in E12 wrote a parallel path and a serial fallback, each with its
own `pb_mix(nl)` — the trial measured nothing and was left out of every count.

The author (3 Oct): telling the model is not enough, and a trial that is not counted is not a
result — prevent it, or fix it and redo it. So the arms without the agent's gate get the
agent's own enforcement, after the model's turn:

  * the finished file is checked with the JUDGE's rules (`scaffold.check`, a byte-identical
    copy of the harness's `agent/tools/scaffold.py`; a harness test keeps the two identical),
    so nothing the harness would call a harness edit gets through;
  * a violation is sent back in the agent's own words (phase_a.py, stage `harness`: the same
    guidance, the agent's diagnostic from `check_protected`, the same retry instruction) in the
    same model session, at most `HARNESS_REASKS` times, never charged as an attempt — the
    parallelization is not what failed;
  * if the lines are still edited after that, the edit is discarded (the file stays as it was),
    as the agent's gate never keeps a candidate it refused.

Nothing changes for a trial whose model leaves the measurement alone: the check runs after
the turn and says nothing, so such a trial is the same as before 3 Oct. The runner keeps a
backstop of its own (agent/tools/cli.py: a trial the harness still classifies
`SCAFFOLD_MODIFIED` is redone).
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional, Sequence

from .harness_lines import check_protected
from ..llm.diffs import make_diff

# Re-asks after a turn that edited the measurement; each is one more model call.
HARNESS_REASKS = 2

# The agent's own words for this stage (phase_a.py, `_STAGE_GUIDANCE["harness"]` and the
# harness retry instruction); `test_harness_guard` proves they are the agent's verbatim.
GUIDANCE = ("The change touched lines that belong to the program's "
            "measurement (listed in the task). They decide what is measured, not "
            "what is computed, so they must stay exactly as they are and where "
            "they are; nothing was built or run.")
RETRY = ("Your parallelization is not what failed. Make the same change again, "
         "leaving the measurement lines exactly as they were.")


def harness_problem(before: str, after: str, protected: Sequence[str], name: str = "source.c") -> Optional[str]:
    """None when `after` keeps the measurement of `before` as the harness judges it; otherwise
    what changed, in the agent's words — the agent's own check (`check_protected`, which applies
    the protected-line rule and the judge's `scaffold.check`), on the two texts."""
    with tempfile.TemporaryDirectory(prefix="dp_harness_") as tmp:
        path = os.path.join(tmp, Path(name).name)
        Path(path).write_text(before)
        return check_protected(make_diff(before, after, path), path, tuple(protected))


def harness_feedback(diagnostic: str) -> str:
    """The message the agent's model gets when its candidate fails the stage `harness`."""
    return (f"Your diff failed at the 'harness' stage. {GUIDANCE}\n\n"
            f"Diagnostic:\n{diagnostic[:1400]}\n\n"
            f"{RETRY}")
