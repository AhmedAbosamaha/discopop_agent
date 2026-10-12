cd "$HOME/discopop_agent" || exit 1
export PATH="$PWD/venv/bin:$PATH"
W=$(mktemp -d /tmp/b24_lu.XXXXXX)
cat > $W/draw.py <<'PY'
import json, shutil, sys
from pathlib import Path
REPO = Path.home() / "discopop_agent"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "evaluation" / "agent" / "tools")); sys.path.insert(0, str(REPO / "evaluation" / "shared"))
import harness_include
from discopop_agent import project as project_mod
from discopop_agent.profiling import _reprofil
harness_include.install()
pkg = REPO / "evaluation" / "agent" / "prepared" / "polybench" / "lu"
work = Path(sys.argv[1]); n = int(sys.argv[2])
meta = json.loads((pkg / "meta.json").read_text()); proj = meta.get("project")
import collections
answers = collections.Counter()
for i in range(n):
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    for f in pkg.iterdir():
        if f.suffix in (".c", ".h", ".cpp", ".hpp"): shutil.copy2(f, work / f.name)
    src = work / meta["file"]
    project_mod.activate(None)
    if proj:
        project_mod.activate(project_mod.Project.discover(work, units=proj["units"], include_dirs=["."], editable=proj.get("editable")))
        project_mod.set_focus(str(src))
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        ok = _reprofil(str(src), work / ".discopop", None)
    if not ok: answers["profile failed"] += 1; continue
    pats = json.loads((work / ".discopop" / "explorer" / "patterns.json").read_text()).get("patterns", {})
    fm = {}
    for ln in (work / ".discopop" / "FileMapping.txt").read_text().splitlines():
        a, b = ln.split("\t"); fm[a] = Path(b).name
    got = sorted((k, fm.get(str(p.get("start_line")).split(":")[0]), int(str(p.get("start_line")).split(":")[1]), tuple(str(v.get("operation")) + ":" + str(v.get("name")) if isinstance(v, dict) else str(v) for v in p.get("reduction", [])))
                 for k in ("do_all", "reduction") for p in pats.get(k, []))
    kern = [(k, l, r) for k, f, l, r in got if f == "lu.c" and 60 <= l <= 70]
    answers[json.dumps(kern)] += 1
for k, v in answers.most_common(): print(v, k)
PY
venv/bin/python $W/draw.py $W/work 12 2>&1 | tail -6
rm -rf $W
git status --short | head -3
