"""
One call to the model, with the retries that must not cost a budget slot
-------------------------------------------------------------------------
`call_llm` is the only entry point the pipeline uses.  It owns three things the
callers should not have to think about:

  * which system prompt applies, from the edit mode and who writes the pragmas;
  * FORMAT retries — a reply in the wrong shape is re-prompted for free, since a
    malformed answer says nothing about the model's parallelization idea;
  * direct mode's convention that the answer is the FILE the model left behind,
    not its prose, and that "" means "changed nothing" rather than "no answer".
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Set

from .. import viz
from ..types import EvidencePackage
from .diffs import _extract_code, _extract_diff, _is_valid_diff
from .prompts import _system_prompt
from .request import (_build_direct_prompt, _build_function_prompt,
                      _build_prompt)
from .providers import (_complete, _make_client,
                        _sync_workspace, _workspace_diff)


def call_llm(
    evidence: EvidencePackage,
    model: str,
    api_key: Optional[str] = None,
    max_format_retries: int = 2,
    messages: Optional[list] = None,
    provider: str = "anthropic",
    api_base: Optional[str] = None,
    edit_mode: str = "diff",
    llm_pragmas: bool = False,
    verbose: bool = False,
    evidence_sections: Optional[Set[str]] = None,
) -> tuple[Optional[str], list]:
    """Call the LLM and return (output or None, updated messages).

    In edit_mode="diff" (default) the output is a unified diff.  In
    edit_mode="function" it is the complete rewritten enclosing function (the
    controller splices it in by line range and generates the diff itself), which
    avoids the LLM having to produce a byte-exact diff.  In edit_mode="direct"
    (claude-agent-sdk only) the model EDITS a private copy of the file with its
    own Read/Edit/Write tools and the returned string is the diff of that copy
    against the real source — the model never has to express an edit as text at
    all.  Direct mode returns "" (not None) when the model left the file
    unchanged, so the controller can tell "made no edit" apart from "produced
    no usable answer".

    On the first call for a region pass messages=None — the initial prompt is
    built from evidence.  Pass the list returned by the previous call on
    subsequent budget retries.  Every entry in `messages` is preserved
    (the caller only ever appends), but by construction the LAST entry is
    always the one genuinely new thing to say this turn: the initial prompt on
    the very first call, a re-prompt on a format retry, or the quality-gate
    feedback on the next budget attempt.  The "anthropic"/"openai-compat"
    providers still resend the full list every call (both are stateless HTTP
    APIs); "claude-agent-sdk" instead sends only that last entry and relies on
    its own real per-region CLI session (keyed by evidence.region_fingerprint —
    a content-based identity, NOT the reassignable region_id) to supply
    everything earlier — see _complete_claude_agent_sdk().

    `llm_pragmas` switches the system prompt: off (default) the model is told
    DiscoPoP will insert the pragmas, on it is told to write them itself and
    that nothing downstream will add one for it.

    `provider` selects the backend: "anthropic" (default, billed API key),
    "openai-compat" (any OpenAI-compatible endpoint at `api_base`, e.g. a
    self-hosted vLLM), or "claude-agent-sdk" (runs the local `claude` CLI
    headlessly via the Claude Agent SDK, billed against the Claude Code
    subscription instead of a per-token API key — `model` accepts Claude
    Code's own aliases like "haiku" as well as full model IDs, and `api_key`
    is ignored since auth comes from `claude login`).
    """
    function_mode = edit_mode == "function"
    direct_mode = edit_mode == "direct"
    if direct_mode and provider != "claude-agent-sdk":
        raise RuntimeError(
            "--edit-mode direct requires --provider claude-agent-sdk (it is the "
            "only backend that can edit files itself)."
        )
    system = _system_prompt(edit_mode, llm_pragmas)
    client = _make_client(provider, api_key, api_base)
    session_key = evidence.region_fingerprint or evidence.region_id

    workspace_file: Optional[Path] = None
    disk = ""
    if direct_mode:
        workspace_file, disk = _sync_workspace(session_key, evidence.source_file)

    if messages is None:
        # First attempt for this region — build initial prompt from evidence.
        if direct_mode:
            assert workspace_file is not None
            user_prompt = _build_direct_prompt(evidence, workspace_file,
                                               evidence_sections)
        elif function_mode:
            user_prompt = _build_function_prompt(evidence, evidence_sections)
        else:
            user_prompt = _build_prompt(evidence, evidence_sections)
        messages = [{"role": "user", "content": user_prompt}]

    current = list(messages)
    kind = "direct" if direct_mode else "function" if function_mode else "diff"

    for attempt in range(max_format_retries + 1):
        if verbose:
            last_user = next(
                (m["content"] for m in reversed(current) if m["role"] == "user"), ""
            )
            viz.llm_request(model, provider, system, last_user, attempt=attempt)

        text = _complete(provider, client, model, current, system,
                         session_key=session_key,
                         workspace=workspace_file.parent if workspace_file else None)

        if verbose:
            viz.llm_response(text, kind=kind)

        if direct_mode:
            assert workspace_file is not None
            # The answer is the file the model left behind, not its prose.
            out = _workspace_diff(workspace_file, evidence.source_file, disk)
        else:
            out = _extract_code(text) if function_mode else _extract_diff(text)
        valid = (
            out is not None if function_mode or direct_mode
            else bool(out and _is_valid_diff(out))
        )

        if verbose:
            viz.llm_extracted(kind, out if valid else None)

        if valid:
            # Return messages with assistant turn appended so the controller
            # can extend the conversation with quality-gate feedback and retry.
            return out, current + [{"role": "assistant", "content": text}]

        # Free format re-prompt — doesn't consume a budget slot.
        if attempt < max_format_retries:
            reprompt = (
                f"You did not change `{workspace_file}` (comment or formatting "
                "edits do not count). Read the file, then APPLY your rewrite "
                "with the Edit tool — describing it in your reply has no effect."
                if direct_mode else
                "Your response must end with the complete rewritten function as a "
                "single ```cpp code block — signature and full body, no diff. "
                "A short plain-text PLAN before the code block is allowed; "
                "nothing may follow the code block."
                if function_mode else
                "Your response must END with a unified diff.\n"
                "After your short plain-text PLAN, write '--- <original_file>' "
                "on its own line, then '+++ <modified_file>' on the next, then "
                "one or more '@@ … @@' hunks — and stop there.\n"
                "No code fences, and no PLAN line may start with '---', '+++' "
                "or '@@'."
            )
            current = current + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": reprompt},
            ]

    # Direct mode's only failure here is "the model never edited the file" —
    # report it as the no-op ("") the controller feeds back, not as garbage output.
    return ("" if direct_mode else None), current
