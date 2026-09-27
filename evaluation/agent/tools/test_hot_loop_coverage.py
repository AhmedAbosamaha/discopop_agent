#!/usr/bin/env python3
"""Tests for hot_loop_coverage.py, E2-B1's check that a program's parallel construct covers the hot loop.

Run: `python3 agent/tools/test_hot_loop_coverage.py` (exit status 1 on any failure). No model, no
DiscoPoP, no compiler: every case is a text built from the packager's own rendering of s151 and s161
(`prepare_tsvc.render`), so the test runs on a fresh clone, where `prepared/` does not exist. Each case
states what the criterion must say about it (the author's decision 3, 27 Sep; the criterion is in the
tool's docstring).
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[2] / "shared")]
import hot_loop_coverage as H  # noqa: E402
import naive_pragma  # noqa: E402
import prepare_tsvc  # noqa: E402

fails = 0


def expect(label: str, cond: bool, detail: object = "") -> None:
    global fails
    fails += not cond
    print(f"  [{'pass' if cond else 'FAIL'}] {label}{(' — ' + str(detail)) if detail and not cond else ''}")


B1 = {l.name: l for l in prepare_tsvc.B1_LOOPS}
S151, S161 = prepare_tsvc.render(B1["s151"]), prepare_tsvc.render(B1["s161"])
HOT151, HOT161 = prepare_tsvc.hot_loop(B1["s151"]), prepare_tsvc.hot_loop(B1["s161"])
assert HOT151 is not None and HOT161 is not None


def covered(src: str, hot: dict) -> dict:
    return H.coverage(src, hot)


def seen(src: str, entry: str) -> list:
    """Every construct the parser finds in the functions the entry reaches, with ALL it writes — so
    a NOT-covered verdict is shown to come from what the construct writes, not from a construct missed."""
    p = H.Program(src, entry)
    return [(c.text, sorted(p.region_writes(p.funcs[n], c.lo, c.hi))) for n in p.reach for c in p.constructs(p.funcs[n])]


def edit(src: str, old: str, new: str) -> str:
    assert old in src, f"not in the source: {old!r}"
    return src.replace(old, new, 1)


# the texts the edits below anchor on (verbatim from the rendering)
LOOP161 = "        for (int i = 0; i < LEN_1D-1; ++i) {\n"
LOOP151 = "    for (int i = 0; i < LEN_1D-1; i++) {\n        a[i] = a[i + m] + b[i];\n    }\n"
CALL151 = "        s151s(a, b,  1);\n"
REP = "    for (int nl = 0; nl < R; nl++) {\n"

print("1. the hot loop the packager declares")
expect("s151: the loop in the callee s151s, line 18, writes a",
       HOT151 == {"entry": "kernel_s151", "function": "s151s", "line": 18, "writes": ["a"]}, HOT151)
expect("s161: the loop inside the repetition loop, line 19, writes a and c",
       HOT161 == {"entry": "kernel_s161", "function": "kernel_s161", "line": 19, "writes": ["a", "c"]}, HOT161)
for name, src, hot in (("s151", S151, HOT151), ("s161", S161, HOT161)):
    expect(f"{name}: the same line as naive_pragma.py's hot loop (the H13/C2 check's loop)",
           naive_pragma.hot_loop_line(src) == hot["line"], naive_pragma.hot_loop_line(src))
    expect(f"{name}: the declared line holds a `for`", src.splitlines()[hot["line"] - 1].lstrip().startswith("for ("))
expect("no hot loop for the E1-E2 suite (tsvc): its meta.json stays as it was",
       all(prepare_tsvc.hot_loop(l) is None for l in prepare_tsvc.LOOPS))
# the loop's own temporaries and counters are not what it writes (s281's shape)
tmp_src = """static real_t kernel_t(void)
{
    for (int nl = 0; nl < R; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}
"""
d = H.describe(tmp_src, "kernel_t", "kernel_t")
expect("a temporary declared in the loop and the loop counter are not among its writes",
       d["writes"] == ["a", "b"] and d["line"] == 4, d)
# scalars: the one a loop reduces into counts, a scratch or carried one does not (s252, s313, s3112)
s252 = """static real_t kernel_t(void)
{
    real_t t, s;
    for (int nl = 0; nl < R; nl++) {
        t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            s = b[i] * c[i];
            a[i] = s + t;
            t = s;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}
"""
d = H.describe(s252, "kernel_t", "kernel_t")
expect("s252's shape: the scratch `s` and the carried `t` are not writes, `a` is", d["writes"] == ["a"], d)
scratch = edit(s252, "        t = (real_t) 0.;\n",
               "        #pragma omp parallel for private(s)\n        for (int i = 0; i < LEN_1D; i++) "
               "{ s = b[i] * c[i]; pb_tmp[i] = s; }\n        t = (real_t) 0.;\n")
expect("... a parallel loop reusing its scratch `s` to fill a temporary — NOT covered, listed in `elsewhere`",
       covered(scratch, d)["covered"] is False and covered(scratch, d)["elsewhere"][0]["writes"] == ["pb_tmp"],
       covered(scratch, d))
s3112 = s252.replace("real_t t, s;", "real_t sum;").replace(
    "            s = b[i] * c[i];\n            a[i] = s + t;\n            t = s;\n",
    "            sum += a[i];\n            b[i] = sum;\n")
d = H.describe(s3112, "kernel_t", "kernel_t")
expect("s3112's shape: the running sum `sum` (updated from itself) and `b` are writes",
       d["writes"] == ["b", "sum"], d)
s313 = s252.replace("real_t t, s;", "real_t dot;").replace(
    "            s = b[i] * c[i];\n            a[i] = s + t;\n            t = s;\n", "            dot = dot + a[i] * b[i];\n")
d = H.describe(s313, "kernel_t", "kernel_t")
expect("s313's shape: the dot product's `dot = dot + ...` is its one write", d["writes"] == ["dot"], d)
par313 = edit(s313, "        for (int i = 0; i < LEN_1D; i++) {\n",
              "        #pragma omp parallel for reduction(+:dot)\n        for (int i = 0; i < LEN_1D; i++) {\n")
expect("... and a `parallel for reduction(+:dot)` on it — covered", covered(par313, d)["covered"] is True)

print("\n2. the required cases")
for name, src, hot in (("s151", S151, HOT151), ("s161", S161, HOT161)):
    r = covered(src, hot)
    expect(f"{name}: the original serial program is NOT covered", r["covered"] is False and not r["uncounted"], r)

r = covered(edit(S161, LOOP161, "        #pragma omp parallel for\n" + LOOP161), HOT161)
expect("s161: a pragma on the hot loop — covered", r["covered"] is True and len(r["covering"]) == 1
       and r["covering"][0]["line"] == 19 and r["covering"][0]["writes"] == ["a", "c"], r)

copy = ("        #pragma omp parallel for\n"
        "        for (int i = 0; i < LEN_1D; i++) pb_tmp[i] = c[i];\n")
src = edit(S161, LOOP161, copy + LOOP161)
r = covered(src, HOT161)
expect("s161: a parallel copy loop into pb_tmp, the hot loop serial — NOT covered (the loop found, "
       "writing only pb_tmp)", r["covered"] is False and seen(src, "kernel_s161") == [("omp parallel for", ["pb_tmp"])],
       (r, seen(src, "kernel_s161")))
src = edit(S151, CALL151, copy.replace("c[i]", "a[i]") + CALL151)
r = covered(src, HOT151)
expect("s151: a parallel copy loop into pb_tmp in the kernel, the callee serial — NOT covered",
       r["covered"] is False and seen(src, "kernel_s151") == [("omp parallel for", ["pb_tmp"])], r)

split = """    int half = (LEN_1D - 1) / 2;
    #pragma omp parallel for
    for (int i = 0; i < half; i++) a[i] = a[i + m] + b[i];
    #pragma omp parallel for
    for (int i = half; i < LEN_1D-1; i++) {
        a[i] = a[i + m] + b[i];
    }
"""
r = covered(edit(S151, LOOP151, split), HOT151)
expect("s151: the hot loop split into two parallel loops writing the same array — covered",
       r["covered"] is True and len(r["covering"]) == 2, r)

region = LOOP161.replace("        for", "        #pragma omp parallel\n        {\n        #pragma omp for\n        for")
body_end = "L10:\n            ;\n        }\n"
r = covered(edit(edit(S161, LOOP161, region), body_end, body_end + "        }\n"), HOT161)
expect("s161: a parallel region with `omp for` on the hot loop — covered",
       r["covered"] is True and [c["directive"] for c in r["covering"]] == ["#pragma omp for"], r)

r = covered(edit(S151, LOOP151, "    #pragma omp parallel for\n" + LOOP151), HOT151)
expect("s151: the pragma inside the callee s151s — covered",
       r["covered"] is True and r["covering"][0]["function"] == "s151s", r)

print("\n3. how the writes are named")
renamed = edit(edit(S151, "void s151s(real_t a[LEN_1D], real_t b[LEN_1D],  int m)",
                    "void s151s(real_t * restrict dst, const real_t *src,  int m)"),
               LOOP151, "    #pragma omp parallel for\n    for (int i = 0; i < LEN_1D-1; i++)\n"
                        "        dst[i] = dst[i + m] + src[i];\n")
r = covered(renamed, HOT151)
expect("s151: the callee's parameter renamed (dst) — still covered, bound to the caller's `a`",
       r["covered"] is True and r["covering"][0]["writes"] == ["a"], r)
src = edit(renamed, CALL151, "        s151s(b, a,  1);\n")
r = covered(src, HOT151)
expect("... and NOT covered when the call binds it to another array (b)",
       r["covered"] is False and seen(src, "kernel_s151") == [("omp parallel for", ["b"])], r)
alias = edit(S161, LOOP161, "        real_t *restrict pc = c + 1;\n        #pragma omp parallel for\n"
                            "        for (int i = 0; i < LEN_1D-1; i++) pc[i] = a[i] + d[i] * d[i];\n" + LOOP161)
r = covered(alias, HOT161)
expect("s161: a parallel loop writing through a pointer alias (pc = c + 1) — covered",
       r["covered"] is True and r["covering"][0]["writes"] == ["c"], r)
value = edit(S161, LOOP161, "        real_t v = c[0];\n        #pragma omp parallel for reduction(+:v)\n"
                            "        for (int i = 0; i < LEN_1D-1; i++) v += d[i];\n" + LOOP161)
expect("s161: a parallel loop writing a VALUE copy of c (v = c[0]) — NOT covered",
       covered(value, HOT161)["covered"] is False
       and seen(value, "kernel_s161") == [("omp parallel for reduction(+:v)", ["v"])], seen(value, "kernel_s161"))
malloc_tmp = ("    real_t *old = (real_t *)malloc((LEN_1D) * sizeof(real_t));\n"
              "    #pragma omp parallel for\n    for (int i = 0; i < LEN_1D; i++) old[i] = a[i];\n"
              "    for (int i = 0; i < LEN_1D-1; i++) a[i] = old[i + m] + b[i];\n    free(old);\n")
src = edit(S151, LOOP151, malloc_tmp)
r = covered(src, HOT151)
expect("s151: a parallel copy into a malloc'd temporary, the update serial — NOT covered",
       r["covered"] is False and seen(src, "kernel_s151") == [("omp parallel for", ["old"])], r)
r = covered(edit(S151, LOOP151, malloc_tmp.replace("    for (int i = 0; i < LEN_1D-1;",
                                                   "    #pragma omp parallel for\n    for (int i = 0; i < LEN_1D-1;")), HOT151)
expect("... and covered once the update from it runs in parallel", r["covered"] is True, r)
swap = edit(S161, LOOP161, """        real_t *cur = NULL, *nxt = (real_t *)malloc(LEN_1D * sizeof(real_t));
        cur = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int k = 0; k < 4; k++) {
            #pragma omp parallel for
            for (int i = 1; i < LEN_1D; i++) nxt[i] = cur[i - 1] * d[i];
            real_t *tmp = cur; cur = nxt; nxt = tmp;
        }
        memcpy(c, cur, LEN_1D * sizeof(real_t));
""" + LOOP161)
r = covered(swap, HOT161)
expect("a double buffer (malloc'd, swapped through tmp) computed in parallel, copied back serially — NOT "
       "covered; `elsewhere` names the buffers", r["covered"] is False
       and [e["writes"] for e in r["elsewhere"]] == [["cur", "nxt"]], r)
helper = edit(edit(S161, "static real_t kernel_s161(void)",
                   "static void step(real_t *x, const real_t *y, int i)\n{\n    x[i] = y[i] + d[i] * e[i];\n}\n\n"
                   "static real_t kernel_s161(void)"),
              LOOP161, "        #pragma omp parallel for\n        for (int i = 0; i < LEN_1D-1; i++) step(a, c, i);\n"
                       + LOOP161)
r = covered(helper, HOT161)
expect("s161: a parallel loop whose body calls a helper writing `a` through its parameter — covered",
       r["covered"] is True and r["covering"][0]["writes"] == ["a"], r)

print("\n4. which constructs count")
on_hot = lambda d: edit(S161, LOOP161, d + LOOP161)  # noqa: E731
r = covered(on_hot("        #pragma omp simd\n"), HOT161)
expect("`simd` alone on the hot loop — NOT covered, recorded as uncounted",
       r["covered"] is False and len(r["uncounted"]) == 1 and "simd" in r["uncounted"][0]["reason"], r)
expect("`parallel for simd` — covered", covered(on_hot("        #pragma omp parallel for simd\n"), HOT161)["covered"] is True)
expect("`parallel for` with clauses on a `\\`-continued line — covered",
       covered(on_hot("        #pragma omp parallel for schedule(static) \\\n            private(i)\n"),
               HOT161)["covered"] is True)
r = covered(on_hot("        #pragma omp for\n"), HOT161)
expect("an `omp for` with no parallel region around it — NOT covered (runs on one thread)",
       r["covered"] is False and "no parallel region" in r["uncounted"][0]["reason"], r)
r = covered(on_hot("        #pragma omp parallel for num_threads(1)\n"), HOT161)
expect("`num_threads(1)` — NOT covered", r["covered"] is False and r["uncounted"], r)
expect("`if(0)` — NOT covered", covered(on_hot("        #pragma omp parallel for if(0)\n"), HOT161)["covered"] is False)
expect("`_Pragma(\"omp parallel for\")` — covered",
       covered(on_hot('        _Pragma("omp parallel for")\n'), HOT161)["covered"] is True)
for label, text in (("inside a block comment", "        /* #pragma omp parallel for\n        */\n"),
                    ("after //", "        // #pragma omp parallel for\n"),
                    ("under #if 0", "#if 0\n        #pragma omp parallel for\n#endif\n")):
    src = on_hot(text)
    expect(f"a pragma {label} — NOT covered, and not seen at all",
           covered(src, HOT161)["covered"] is False and seen(src, "kernel_s161") == [])
expect("... and one under the #else of an #if 0 — covered",
       covered(on_hot("#if 0\n#else\n        #pragma omp parallel for\n#endif\n"), HOT161)["covered"] is True)
r = covered(edit(S161, REP, "    #pragma omp parallel for\n" + REP), HOT161)
expect("`parallel for` on the repetition loop — covered (it contains the hot loop; the verification "
       "judges the program)", r["covered"] is True, r)
orphan = edit(edit(S151, LOOP151, "    #pragma omp for\n" + LOOP151), CALL151,
              "        #pragma omp parallel\n        s151s(a, b,  1);\n")
r = covered(orphan, HOT151)
expect("an orphaned `omp for` in the callee, called from a parallel region — covered", r["covered"] is True, r)
dead = edit(S161, "static real_t kernel_s161(void)",
            "static void unused(void)\n{\n    #pragma omp parallel for\n"
            "    for (int i = 0; i < LEN_1D-1; i++) a[i] = c[i] + d[i] * e[i];\n}\n\nstatic real_t kernel_s161(void)")
expect("a parallel loop in a function the kernel never calls — NOT covered",
       covered(dead, HOT161)["covered"] is False and seen(dead, "kernel_s161") == []
       and seen(dead, "unused") == [("omp parallel for", ["a"])])
spmd = on_hot("""        #pragma omp parallel
        {
            int t = omp_get_thread_num(), nt = omp_get_num_threads();
            for (int i = t; i < LEN_1D-1; i += nt) a[i] = c[i] + d[i] * e[i];
        }
""")
r = covered(spmd, HOT161)
expect("a loop split by hand inside `omp parallel` — NOT covered, recorded as uncounted",
       r["covered"] is False and "parallel` region's own code" in r["uncounted"][0]["reason"], r)
sections = on_hot("""        #pragma omp parallel sections
        {
            #pragma omp section
            for (int i = 0; i < LEN_1D/2; i++) a[i] = c[i] + d[i] * e[i];
            #pragma omp section
            for (int i = LEN_1D/2; i < LEN_1D-1; i++) a[i] = c[i] + d[i] * e[i];
        }
""")
expect("`parallel sections`, each section writing `a` — covered", covered(sections, HOT161)["covered"] is True)
task = on_hot("""        #pragma omp parallel
        #pragma omp single
        {
            #pragma omp task
            for (int i = 0; i < LEN_1D/2; i++) a[i] = c[i] + d[i] * e[i];
        }
""")
r = covered(task, HOT161)
expect("an explicit `task` — NOT covered, recorded as uncounted",
       r["covered"] is False and any("task" in u["reason"] for u in r["uncounted"]), r)
taskloop = on_hot("        #pragma omp parallel\n        #pragma omp single\n        #pragma omp taskloop\n"
                  "        for (int i = 0; i < LEN_1D-1; i++) a[i] = c[i] + d[i] * e[i];\n")
expect("`taskloop` inside `parallel` + `single` — covered", covered(taskloop, HOT161)["covered"] is True)
forsimd = on_hot("        #pragma omp parallel\n        #pragma omp for simd\n"
                 "        for (int i = 0; i < LEN_1D-1; i++) a[i] = c[i] + d[i] * e[i];\n")
expect("`for simd` inside a parallel region — covered", covered(forsimd, HOT161)["covered"] is True)
r = covered(S161.replace("kernel_s161", "kernel_other"), HOT161)
expect("the entry function gone — no verdict (null), with the problem named", "problem" in r, r)

print("\n5. the trial record (cli.py)")
f = H.trial_fields(None, S161)
expect("a package without `hot_loop`: only hot_loop_covered, and it is null (not false)",
       f == {"hot_loop_covered": None}, f)
f = H.trial_fields(HOT161, S161)
expect("an E2-B1 package: the hot loop kept with the record, covered false for the original",
       f["hot_loop"] == HOT161 and f["hot_loop_covered"] is False and f["hot_loop_coverage"]["covered"] is False, f)
f = H.trial_fields({"entry": "kernel_s161"}, S161)
expect("a check that cannot decide records null and says why",
       f["hot_loop_covered"] is None and f["hot_loop_coverage"].get("problem"), f)
import cli  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    cli._save_trial(Path(tmp), {"benchmark": "tsvc_b1/s161", "status": "profile_error"}, 1)
    rec = json.loads((Path(tmp) / "trial.json").read_text())
expect("a record written without a final program (profile_error) carries hot_loop_covered: null",
       "hot_loop_covered" in rec and rec["hot_loop_covered"] is None, rec)

# Through the real `run_trial`, the agent and the verification stubbed: the "agent" leaves the given
# final program in its working copy, as the agent does; the record must judge that file.
print("\n6. run_trial writes the fields (agent and verification stubbed)")


def trial_with(final: str, meta_extra: dict) -> dict:
    import argparse
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        pkg, prof, trial = t / "pkg", t / "profile", t / "trial"
        for d in (pkg, prof / ".discopop"):
            d.mkdir(parents=True)
        (pkg / "meta.json").write_text(json.dumps({"suite": "tsvc_b1", "file": "s161.c", **meta_extra}))
        (prof / "s161.c").write_text(S161)

        def fake_run(cmd, cwd, env=None, timeout=3600, log=None):
            (Path(cwd) / "s161.c").write_text(final)
            if log is not None:
                log.write_text("")
            return 0, 0.0, ""

        def fake_size(requested, kernel):
            return "SMALL", None

        def fake_verify(*a, **k):
            return {"status": "ok", "par": {}}

        keep = cli._run, cli.verify, cli._verify_size
        cli._run, cli.verify, cli._verify_size = fake_run, fake_verify, fake_size
        try:
            a = argparse.Namespace(agent_repo=str(cli.DEFAULT_AGENT_REPO), provider="none", edit_mode="direct",
                                   check_seed=None, min_runtime_share=0.0, agent_arg=[], timeout=60,
                                   keep_work=False, verify_size="SMALL", threads=[2], repeats=1)
            cli.run_trial("tsvc_b1/s161", pkg, prof, trial, "full", [], "stub", a, "cc", "cxx")
            return json.loads((trial / "trial.json").read_text())
        finally:
            cli._run, cli.verify, cli._verify_size = keep


par161 = edit(S161, LOOP161, "        #pragma omp parallel for\n" + LOOP161)
copy161 = edit(S161, LOOP161, copy + LOOP161)
r1 = trial_with(par161, {"hot_loop": HOT161})
expect("a pragma on the hot loop: hot_loop_covered true, the hot loop kept with the record",
       r1.get("hot_loop_covered") is True and r1.get("hot_loop") == HOT161 and r1.get("pragmas_in_final") == 1, r1)
r2 = trial_with(copy161, {"hot_loop": HOT161})
expect("a parallel copy only: hot_loop_covered false — and the outcome is what it was without the check",
       r2.get("hot_loop_covered") is False and r2["outcome"] == cli.classify(
           {k: v for k, v in r2.items() if not k.startswith("hot_loop")}), r2)
r3 = trial_with(par161, {})
expect("the same program in a package without `hot_loop`: hot_loop_covered null, nothing else added",
       r3.get("hot_loop_covered", "absent") is None and "hot_loop" not in r3 and "hot_loop_coverage" not in r3, r3)

print(f"\n{'ALL PASS' if not fails else f'{fails} FAILURE(S)'}")
sys.exit(1 if fails else 0)
