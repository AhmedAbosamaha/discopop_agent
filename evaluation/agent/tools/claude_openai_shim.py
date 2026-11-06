#!/usr/bin/env python3
"""E11 part 2 — RepoOMP's model calls to Claude through the Claude Agent SDK (no API key).

RepoOMP's release calls its model through the `openai` client (`primitive_adder.call_llm`: one user message,
`temperature=0`, `max_tokens`, `stream=True`, `extra_body={"thinking": {"type": "disabled"}}`) at
`REPOOMP_API_BASE`. Our agent reaches Claude through the Claude Agent SDK on the author's subscription; this is
a local OpenAI-compatible endpoint that forwards each request there, so RepoOMP and the agent call the same model
by the same route. What it does with a request, and nothing more:

  * the messages are sent as they are: system messages (RepoOMP sends none) as the system prompt, the rest as
    the one prompt; no tools, one turn, no settings files — the SDK options our agent's text calls use;
  * no tool definitions are sent (`tools=[]`), and thinking is off when the request asks for it (RepoOMP's
    `extra_body` always does);
  * `temperature` and `max_tokens` cannot be set through the SDK and are not applied (RepoOMP asks for 0 and a
    length bound): a repeated request may get a different answer, where RepoOMP's API would repeat itself;
  * the answer comes back whole, as one streamed chunk when `stream` is set, then `[DONE]`;
  * every call's usage (tokens, cost, time), any failure, and the full text of the prompt and of the answer are
    appended to `--log` (what the model read and wrote is archived with the trial: the rule of 4 Oct).

    venv/bin/python evaluation/agent/tools/claude_openai_shim.py --port 18765 --log RUN/shim_calls.jsonl
    REPOOMP_API_BASE=http://127.0.0.1:18765/v1 REPOOMP_API_KEY=local REPOOMP_MODEL=claude-sonnet-4-5-20250929 ...
"""
from __future__ import annotations

import argparse
import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple

LOCK = threading.Lock()


def _ask(model: str, system: str, prompt: str, thinking_off: bool) -> Tuple[str, Dict[str, Any]]:
    from claude_agent_sdk import (  # type: ignore[import-not-found]
        AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query)

    async def run() -> Tuple[str, Dict[str, Any]]:
        text, usage = "", {}
        # tools=[]: no tool definitions in the request (RepoOMP's API call has none; `allowed_tools` alone would
        # still send the CLI's tool list, about 20,000 tokens); thinking off when the request asks for it.
        opts = ClaudeAgentOptions(system_prompt=system, model=model, max_turns=1, tools=[], allowed_tools=[],
                                  permission_mode="dontAsk", setting_sources=[],
                                  thinking={"type": "disabled"} if thinking_off else None)
        async for m in query(prompt=prompt, options=opts):
            if isinstance(m, AssistantMessage):
                text += "".join(b.text for b in m.content if isinstance(b, TextBlock))
            if isinstance(m, ResultMessage):
                usage = {"usage": m.usage, "total_cost_usd": m.total_cost_usd, "duration_ms": m.duration_ms,
                         "is_error": bool(getattr(m, "is_error", False)),
                         "result": str(getattr(m, "result", ""))[:300] if getattr(m, "is_error", False) else ""}
        return text, usage
    return asyncio.run(run())


class Handler(BaseHTTPRequestHandler):
    log_path: Path = Path("shim_calls.jsonl")

    def log_message(self, format: str, *args: Any) -> None:   # quiet
        return

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:   # noqa: N802
        if not self.path.rstrip("/").endswith("/chat/completions"):
            self._send(404, b'{"error": {"message": "not found"}}', "application/json")
            return
        req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        msgs: List[Dict[str, Any]] = list(req.get("messages") or [])
        system = "\n\n".join(str(m.get("content", "")) for m in msgs if m.get("role") == "system")
        prompt = "\n\n".join(str(m.get("content", "")) for m in msgs if m.get("role") != "system")
        model = str(req.get("model") or "")
        t0 = time.time()
        rec: Dict[str, Any] = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "model": model,
                               "prompt_chars": len(prompt), "system_chars": len(system),
                               "asked": {k: req.get(k) for k in ("temperature", "max_tokens", "stream")}}
        try:
            thinking_off = (req.get("thinking") or {}).get("type") == "disabled"   # RepoOMP's extra_body
            rec["thinking_off"] = thinking_off
            text, usage = _ask(model, system, prompt, thinking_off)
            rec.update(usage, ok=bool(text) and not usage.get("is_error"), answer_chars=len(text))
        except Exception as e:   # the failure goes back to RepoOMP as an API error, and into the log
            text, rec["ok"], rec["error"] = "", False, f"{type(e).__name__}: {e}"[:500]
        rec["seconds"] = round(time.time() - t0, 1)
        rec["system"], rec["prompt"], rec["answer"] = system, prompt, text
        with LOCK, self.log_path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        if not rec["ok"]:
            self._send(500, json.dumps({"error": {"message": rec.get("error") or rec.get("result") or "empty answer"}}).encode(),
                       "application/json")
            return
        created = int(time.time())
        if req.get("stream"):
            chunk = {"id": "shim", "object": "chat.completion.chunk", "created": created, "model": model,
                     "choices": [{"index": 0, "delta": {"role": "assistant", "content": text}, "finish_reason": None}]}
            end = {"id": "shim", "object": "chat.completion.chunk", "created": created, "model": model,
                   "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
            body = (f"data: {json.dumps(chunk)}\n\n" f"data: {json.dumps(end)}\n\n" "data: [DONE]\n\n").encode()
            self._send(200, body, "text/event-stream")
        else:
            out = {"id": "shim", "object": "chat.completion", "created": created, "model": model,
                   "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]}
            self._send(200, json.dumps(out).encode(), "application/json")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=18765)
    ap.add_argument("--log", type=Path, required=True)
    a = ap.parse_args()
    a.log.parent.mkdir(parents=True, exist_ok=True)
    Handler.log_path = a.log
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"shim on http://127.0.0.1:{a.port}/v1, calls -> {a.log}", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
