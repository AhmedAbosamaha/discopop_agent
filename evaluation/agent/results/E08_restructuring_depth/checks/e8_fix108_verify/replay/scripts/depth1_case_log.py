"""The feature check's depth-1 case on whichever agent is checked out, with its log: which D40 verdicts, which feedback."""
import contextlib, importlib, io, re, shutil, sys, tempfile
from pathlib import Path
sys.argv = ["x"]
from discopop_agent.benchmark import test_features as tf
from discopop_agent.args import parse_args
from discopop_agent.llm import make_diff
agent_run = importlib.import_module("discopop_agent.run")
phase_a = importlib.import_module("discopop_agent.phases.phase_a")
d = Path(tempfile.mkdtemp(prefix="fix108_old_")) / "size_run"
d.mkdir(parents=True)
src = d / "k.c"
src.write_text(tf._SIZE_SRC)
ok, err = tf._profile(d, "k.c")
assert ok, err
calls = []
def model(evidence, model_name, **kw):
    msgs = kw.get("messages")
    calls.append(msgs[-1]["content"] if msgs else "(first request)")
    new = tf._SIZE_STACK if len(calls) == 1 else tf._SIZE_HEAP
    history = (msgs or [{"role": "user", "content": "request"}]) + [{"role": "assistant", "content": "plan"}]
    return make_diff(src.read_text(), new, str(src)), history, "plan"
argv = ["x", "--discopop-dir", str(d / ".discopop"), "--source-file", str(src), "--provider", "claude-agent-sdk",
        "--model", "m", "--edit-mode", "direct", "--exclude-functions", "main", "--budget", "2",
        "--timing-cflags=-DDP_BIG", "--restructure-depth", "1"]
saved = (phase_a.call_llm, sys.argv)
log = io.StringIO()
try:
    phase_a.call_llm, sys.argv = model, argv
    with contextlib.redirect_stdout(log):
        agent_run.run(parse_args())
finally:
    phase_a.call_llm, sys.argv = saved
text = log.getvalue()
for ln in text.splitlines():
    if re.search(r"┌─ \[depth=|D40 verdict|D40 size run|D40: the timing|DiscoPoP now finds|└─ ACCEPTED|└─ retry|CRASHED", ln):
        print(ln[:180])
for i, c in enumerate(calls[1:], start=2):
    m = re.search(r"Diagnostic:\n(.*)", c, re.S)
    print(f"call {i} feedback diagnostic: {m.group(1)[:160]!r}" if m else f"call {i}: {c[:120]!r}")
shutil.rmtree(d.parent, ignore_errors=True)
