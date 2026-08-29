"""
The three backends, behind one `_complete` call
-------------------------------------------------
`anthropic` and `openai-compat` are stateless HTTP: the whole conversation is
resent every call.  `claude-agent-sdk` runs the local `claude` CLI headlessly and
keeps one real session PER REGION, so a retry sends only the newest message and
the CLI reconstructs the rest from its own transcript — the model genuinely
remembers its earlier attempts and the gate feedback on them.

Sessions are keyed on the region FINGERPRINT, not the region id: ids are
reassigned across a re-profile, and keying on one would hand a region another
region's transcript.
"""
from __future__ import annotations

import asyncio
import atexit
import hashlib
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import anthropic

from .diffs import make_diff, normalize_code


# One real Claude Code CLI session per region, kept for the life of this
# process: session_key -> the CLI's own session_id.  Populated/consulted by
# _complete_claude_agent_sdk() below.  Keyed on EvidencePackage.region_fingerprint
# (content-based), NOT region_id — DiscoPoP reassigns region_id from a global
# counter after a re-profile, so it can silently point at a different, unrelated
# region; resuming a session under a reused region_id would leak that other
# region's full transcript into this one.
_region_sessions: Dict[str, str] = {}
# --edit-mode direct: one throwaway workspace per region, keyed the same way.
# Each holds a single file — a copy of the source the model is allowed to edit
# — plus the on-disk content it was copied from, so a later call can tell an
# edit the model made from a change the controller made (another region's
# accepted patch, or a revert).
_region_workspaces: Dict[str, Tuple[Path, str]] = {}
# One ROOT for all of them, removed at exit.  Each workspace used to be its own
# mkdtemp that nothing ever cleaned up, so a run left one directory per region
# behind in /tmp for the life of the machine (66 were sitting there when this
# was found).  A per-key subdirectory keeps the same isolation — the file inside
# is named after the source, so a shared flat directory would collide.
_workspace_root: Optional[Path] = None


def _ws_dir(session_key: str) -> Path:
    global _workspace_root
    if _workspace_root is None or not _workspace_root.exists():
        _workspace_root = Path(tempfile.mkdtemp(prefix="dp_agent_edit_"))
        atexit.register(shutil.rmtree, _workspace_root, ignore_errors=True)
    d = _workspace_root / hashlib.sha1(session_key.encode()).hexdigest()[:16]
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _make_client(provider: str, api_key: Optional[str], api_base: Optional[str]) -> Any:
    """Create the provider client.  'anthropic' (default) uses the Anthropic SDK;
    'openai-compat' uses the OpenAI SDK pointed at an OpenAI-compatible endpoint
    (e.g. a self-hosted vLLM server) via api_base; 'claude-agent-sdk' has no
    persistent client — each call spins up the local `claude` CLI headlessly via
    the Claude Agent SDK, authenticated through the Claude Code subscription
    login (`claude login`) rather than a billed API key."""
    if provider == "openai-compat":
        try:
            import openai
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "provider 'openai-compat' requires the openai package "
                "(`venv/bin/pip install openai`)."
            ) from e
        return openai.OpenAI(api_key=api_key or "EMPTY", base_url=api_base)
    if provider == "claude-agent-sdk":
        return None
    return anthropic.Anthropic(api_key=api_key)


def _sync_workspace(session_key: str, source_file: str) -> Tuple[Path, str]:
    """Return (workspace copy of `source_file`, its current on-disk content).

    The workspace is created on the region's first direct-mode call and then
    reused: within one region, retries keep whatever the model already edited,
    so it refines its own attempt against the quality-gate feedback instead of
    starting from the original every time.  It is re-seeded from disk whenever
    the real file changed underneath it (another region's patch was applied, or
    this region's was reverted), because the stale edits no longer apply."""
    disk = Path(source_file).read_text()
    entry = _region_workspaces.get(session_key)
    if entry is not None:
        ws_file, base = entry
        if ws_file.exists() and base == disk:
            return ws_file, disk
    else:
        ws_file = _ws_dir(session_key) / Path(source_file).name
    ws_file.parent.mkdir(parents=True, exist_ok=True)
    ws_file.write_text(disk)
    _region_workspaces[session_key] = (ws_file, disk)
    return ws_file, disk


def _workspace_diff(ws_file: Path, source_file: str, disk: str) -> Optional[str]:
    """Unified diff of the model's edited copy against the real source, ready
    for the L4 gate.  Built from the actual on-disk content, so it always
    applies cleanly.  None when the model changed nothing that matters (no
    edit, or a comment/whitespace-only edit)."""
    edited = ws_file.read_text()
    if normalize_code(edited) == normalize_code(disk):
        return None
    return make_diff(disk, edited, source_file)


def _complete_claude_agent_sdk(
    model: str,
    system: str,
    current: list,
    session_key: str,
    workspace: Optional[Path] = None,
    stateless: bool = False,
) -> str:
    """Run one turn through the local `claude` CLI headlessly (Claude Agent
    SDK), billed against the Claude Code subscription rather than a per-token
    API key.  `model` accepts Claude Code's own aliases (e.g. "haiku",
    "sonnet", "opus") as well as full model IDs.

    Without `workspace` (edit modes diff/function) tool use is disabled and the
    turn count capped at 1 — the call site wants a single text response, never
    agentic file/bash actions against the profiled source tree.  With
    `workspace` (--edit-mode direct) the model gets Read/Edit/Write confined to
    that directory, which holds nothing but a private COPY of the source file:
    the real, profiled source is not reachable from there, and the answer is
    the copy's final content rather than anything the model prints.

    Unlike the other two providers (stateless HTTP — the full conversation is
    resent on every call), this keeps one real Claude Code session PER REGION:
    the first call for a region starts a fresh session; every later call for
    that same region (a format retry inside call_llm(), or the next budget
    attempt from the controller) resumes it via `resume=<session_id>` and
    sends ONLY the newest message (`current[-1]`, by construction always the
    one new thing to say this turn — see call_llm()'s docstring) — the CLI
    reconstructs everything else from its own on-disk session transcript, so
    the model genuinely remembers prior diff attempts and quality-gate
    feedback for that region instead of having the whole history re-explained
    to it on every call."""
    try:
        from claude_agent_sdk import (  # type: ignore[import-not-found]
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            TextBlock,
            query,
        )
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "provider 'claude-agent-sdk' requires the claude-agent-sdk package "
            "(`venv/bin/pip install claude-agent-sdk`) and the `claude` CLI "
            "installed and logged in (`claude login`)."
        ) from e

    prompt = current[-1]["content"]

    def _options(resume: Optional[str]) -> Any:
        return ClaudeAgentOptions(
            system_prompt=system,
            model=model,
            # Direct mode needs several turns (read → edit → …); the text modes
            # want exactly one response and nothing else.
            max_turns=24 if workspace else 1,
            allowed_tools=["Read", "Edit", "Write"] if workspace else [],
            cwd=str(workspace) if workspace else None,
            permission_mode="acceptEdits" if workspace else "dontAsk",
            # Without this, the CLI auto-loads this project's own CLAUDE.md and
            # any user/project settings ("user", "project" are the defaults)
            # into context alongside our system prompt — verified
            # experimentally: the model becomes aware of unrelated
            # dev-guideline instructions. Keep the region-restructuring system
            # prompt uncontaminated.
            setting_sources=[],
            resume=resume,
        )

    async def _run(resume: Optional[str]) -> Tuple[str, Optional[str]]:
        text = ""
        session_id: Optional[str] = None
        async for message in query(prompt=prompt, options=_options(resume)):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text += block.text
            if isinstance(message, ResultMessage):
                session_id = message.session_id
        return text, session_id

    # Two different hiccups are retried here, and neither is worth losing a run
    # over.  A cached session can go stale (its on-disk transcript evicted), and
    # the CLI itself fails calls transiently — observed repeatedly as
    # `Claude Code returned an error result: success`, with the identical call
    # succeeding moments later.  After the first failure the session is dropped
    # and every further attempt starts fresh, so a bad transcript cannot poison
    # the retries.  A real problem (not logged in, no CLI) fails every attempt
    # and the last exception is re-raised.
    # `stateless`: ask, answer, forget.  The dependence review passes this
    # because its session key is a module-level CONSTANT — every --llm-deps call
    # in a run was resuming one shared, growing transcript, so region 3's
    # verdicts were produced with regions 1 and 2's dependence discussions still
    # in context.  That works directly against the review's own design rule of
    # keeping each question as narrow as possible, and the transcript grew
    # without bound over a long run.  Each review is self-contained anyway.
    resume_id = None if stateless else _region_sessions.get(session_key)
    text = ""
    session_id = None
    last_error: Optional[BaseException] = None
    for attempt in range(3):
        try:
            text, session_id = asyncio.run(_run(resume_id if attempt == 0 else None))
            last_error = None
            break
        except Exception as e:                       # noqa: BLE001 - reported below
            last_error = e
            _region_sessions.pop(session_key, None)
            resume_id = None
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    if last_error is not None:
        raise last_error

    if session_id and not stateless:
        _region_sessions[session_key] = session_id
    return text


class LLMConnectionError(RuntimeError):
    """The LLM endpoint could not be reached (server not running, wrong
    --api-base, or network failure).  Fatal for the whole run — every region
    would hit the same error — so the controller aborts cleanly on it."""


def _complete(
    provider: str, client: Any, model: str, current: list, system: str, session_key: str = "",
    workspace: Optional[Path] = None, stateless: bool = False,
) -> str:
    """Run one completion against the chosen provider and return the raw text.

    Both providers receive the same `system` instructions and the same
    user/assistant conversation; only the wire format differs (Anthropic takes
    `system` separately, OpenAI takes it as the first message).  `session_key`
    is only used by 'claude-agent-sdk', to key its per-region CLI session — it
    must be a content-based identity (EvidencePackage.region_fingerprint), not
    DiscoPoP's region_id, which gets reassigned to unrelated regions after a
    re-profile.  `workspace` (--edit-mode direct, claude-agent-sdk only) is the
    directory the model may edit; passing it turns on its file tools."""
    try:
        if provider == "openai-compat":
            resp = client.chat.completions.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "system", "content": system}] + current,
            )
            return resp.choices[0].message.content or ""
        if provider == "claude-agent-sdk":
            return _complete_claude_agent_sdk(model, system, current, session_key,
                                              workspace, stateless=stateless)
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=current,
        )
        return str(resp.content[0].text)
    except Exception as e:
        # Both the openai and anthropic SDKs raise an `APIConnectionError`
        # when the endpoint is unreachable; match by name so the openai SDK
        # stays an optional dependency.
        if type(e).__name__ == "APIConnectionError":
            endpoint = getattr(client, "base_url", None) or "the configured endpoint"
            raise LLMConnectionError(
                f"cannot reach the LLM endpoint at {endpoint} — "
                f"is the model server running?"
            ) from e
        if type(e).__name__ in ("CLINotFoundError", "CLIConnectionError", "ProcessError"):
            raise LLMConnectionError(
                f"cannot run the Claude Code CLI for provider 'claude-agent-sdk' — "
                f"is `claude` installed and on PATH, and are you logged in "
                f"(`claude login`)? ({e})"
            ) from e
        raise
