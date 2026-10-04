#!/usr/bin/env python3
"""Prototype of the package form in which the benchmark's function holds its own repetition loop, as TSVC's
function does ("c2"), beside the two forms that exist — the one-file packaging of E1-final ("v4") and the clean
layout as launched ("c1") — as source trees a timing script can build. No model, nothing in the repository
is written.

    venv/bin/python v6_proto.py OUT            (run from evaluation/agent)

    OUT/_h/<suite>/<loop>.h                    the measurement headers (outside every tree)
    OUT/<variant>/<loop>/orig/…                the sequential original
    OUT/<variant>/<loop>/ref/…                 the expert reference in that form
    OUT/manifest.json                          loops, sizes, variants (units, flags)

Variants:  v4      one file, the repetition loop inside the function, data `static` in the same unit
           c1      two files, the function is ONE repetition, main.c calls it R times (as launched)
           c1call  c1 with the reference's temporary array obtained and released on every call
           c2      two files, the function holds the repetition loop and TSVC's call between repetitions
           c2arr   c2 with the data declared as arrays, as TSVC declares them
"""
from __future__ import annotations

import copy
import glob
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, "tools")
import prepare_tsvc as P  # noqa: E402

CALL = "        dummy(a, b, c, d, e);"
PROTO = "int dummy(real_t *a, real_t *b, real_t *c, real_t *d, real_t *e);"
ALLOC = "    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));\n"


def _sizes(loop: P.Loop) -> str:
    return "\n".join(l for l in (P.SIZE_BLOCK % {"reps": loop.reps}).strip("\n").splitlines()
                     if not l.startswith("#define R "))


def c2_header(loop: P.Loop, arrays: bool = False) -> str:
    decl, _defn = P._v5_split_globals(loop)
    param = P.V5_PARAMS.get(loop.name, ("void", ""))[0]
    data = ("extern real_t a[LEN_1D], b[LEN_1D], c[LEN_1D], d[LEN_1D], e[LEN_1D];\n" if arrays
            else "extern real_t *a, *b, *c, *d, *e;\n")
    return ("#ifndef DATA_H\n#define DATA_H\n\n" + _sizes(loop) + f"\n#define iterations {loop.reps}\n"
            + "\ntypedef double real_t;\n\n" + data + "".join(l + "\n" for l in decl)
            + "\n" + PROTO + f"\nreal_t kernel_{loop.name}({param});\n\n#endif\n")


def _free_before_return(body: str) -> str:
    lines = body.split("\n")
    idx = max(i for i, l in enumerate(lines) if l.strip().startswith("return "))
    lines.insert(idx, "    free(tmp);")
    return "\n".join(lines)


def c2_expert_body(loop: P.Loop) -> Tuple[str, str]:
    """The reference with the repetition loop inside: its temporary array obtained once, before the loop."""
    body = P._exact(loop.expert or "", "for (int nl = 0; nl < R; nl++) {", "for (int nl = 0; nl < iterations; nl++) {")
    body = P._exact(body, "        pb_mix(nl);", CALL).rstrip("\n")
    includes = ""
    if "pb_tmp" in body:
        body = ALLOC + _free_before_return(body.replace("pb_tmp", "tmp"))
        includes += "#include <stdlib.h>\n"
    if "omp_get" in body:
        includes += "#include <omp.h>\n"
    return body, includes


def c1call_expert_body(loop: P.Loop) -> Tuple[str, str]:
    """The clean layout's reference with the temporary array obtained and released on EVERY call — what a
    function that is one repetition does when it is written the ordinary way (Sonnet's and Opus's s211)."""
    body, includes = P._v5_expert_body(loop)
    keep = ("    static real_t *tmp;\n"
            "    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));\n")
    body = _free_before_return(P._exact(body, keep, ALLOC))
    return body, includes


def c2_kernel(loop: P.Loop, expert: bool = False) -> str:
    _category, decls, rep, ret = P._loop_function(loop)
    kernel_globals = "" if P._is_harness_global(loop.globals_) else P._no_comments(loop.globals_)
    param = P.V5_PARAMS.get(loop.name, ("void", ""))[0]
    if expert:
        body, includes = c2_expert_body(loop)
    else:
        pre = "\n".join(l for l in loop.pre.splitlines() if "pb_" not in l)
        body = "\n".join(x for x in (P._no_comments(pre), P._no_comments(decls),
                                     "    for (int nl = 0; nl < iterations; nl++) {",
                                     P._no_comments(rep), CALL, "    }", f"    return {ret};") if x)
        includes = "#include <stdlib.h>\n" if re.search(r"\bexit\s*\(", rep) else ""
    return (includes + f'#include "{P.V5_HEADER}"\n' + ("\n" + kernel_globals + "\n" if kernel_globals else "")
            + f"\nreal_t kernel_{loop.name}({param})\n{{\n" + body + "\n}\n")


def c2_main(loop: P.Loop, hsuite: str) -> str:
    mix = [l for l in P.PB_MIX.strip("\n").splitlines() if not l.lstrip().startswith(("/*", "*"))]
    body = "\n".join(mix[2:-1])                       # between the braces of pb_mix
    arg = P.V5_PARAMS.get(loop.name, ("", ""))[1]
    return (f'#include "{P.V5_HEADER}"\n#include "{hsuite}/{loop.name}.h"\n\n'
            "int dummy(real_t *a, real_t *b, real_t *c, real_t *d, real_t *e)\n{\n"
            "  static int nl = 0;\n" + body + "\n  nl++;\n  return 0;\n}\n\n"
            "int main(int argc, char** argv)\n{\n"
            "  if (pb_setup(argc, argv)) return 1;\n"
            "  pb_timer_start();\n"
            f"  real_t pb_result = kernel_{loop.name}({arg});\n"
            "  pb_timer_stop();\n"
            "  pb_finish(pb_result);\n"
            "  return 0;\n}\n")


def arrays_harness(text: str) -> str:
    """The measurement header with TSVC's five vectors as arrays (no allocation, nothing released)."""
    text = P._exact(text, "real_t *a, *b, *c, *d, *e;", "real_t a[LEN_1D], b[LEN_1D], c[LEN_1D], d[LEN_1D], e[LEN_1D];")
    for v in "abcde":
        text = P._exact(text, f"  {v} = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));\n", "")
    text = P._exact(text, '  if (!a || !b || !c || !d || !e) { fprintf(stderr, "out of memory\\n"); return 1; }\n', "")
    text = P._exact(text, "  free(a); free(b); free(c); free(d); free(e);\n", "")
    return text


def put(root: Path, files: Dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (root / name).write_text(text)


def main() -> int:
    out = Path(sys.argv[1]).resolve()
    sizes: Dict[str, str] = {}
    for f in glob.glob("results/T0_instruments/T0.16_clean_layout/preflight/t0_14_c1_refs/**/trial.json", recursive=True):
        t = json.loads(Path(f).read_text())
        sizes[t["benchmark"].split("/")[-1]] = (t.get("verify") or {}).get("verify_size")
    b1 = {l.name: l for l in P.B1_LOOPS}
    loops: Dict[str, Dict[str, object]] = {}
    for loop in P.SUITES[P.V5_SUITE]:
        n = loop.name
        row: Dict[str, object] = {"size": sizes.get(n), "reps": loop.reps, "expert": loop.expert is not None,
                                  "tmp": bool(loop.expert and "pb_tmp" in loop.expert), "variants": []}
        var: List[str] = row["variants"]            # type: ignore[assignment]
        (out / "_h" / P.V5_SUITE).mkdir(parents=True, exist_ok=True)
        hdr = P.render_v5_harness(loop)
        (out / "_h" / P.V5_SUITE / f"{n}.h").write_text(hdr)
        # v4: one file, the measurement header of its own suite
        old: Optional[P.Loop] = None
        if n in b1:
            old = copy.copy(b1[n])
            old.expert = loop.expert
            (out / "_h" / old.suite).mkdir(parents=True, exist_ok=True)
            (out / "_h" / old.suite / f"{n}.h").write_text(P.render_harness(old))
            put(out / "v4" / n / "orig", {f"{n}.c": P.render(old)})
            if old.expert is not None:
                put(out / "v4" / n / "ref", {f"{n}.c": P.render(old, expert=True)})
            var.append("v4")
        # c1: as launched
        files = P.v5_files(loop)
        put(out / "c1" / n / "orig", files)
        if loop.expert is not None:
            put(out / "c1" / n / "ref", {**files, f"{n}.c": P.render_v5_kernel(loop, expert=True)})
        var.append("c1")
        if row["tmp"]:
            body, inc = c1call_expert_body(loop)
            param = P.V5_PARAMS.get(n, ("void", ""))[0]
            put(out / "c1call" / n / "orig", files)
            put(out / "c1call" / n / "ref", {**files, f"{n}.c": inc + f'#include "{P.V5_HEADER}"\n'
                                              + f"\nreal_t kernel_{n}({param})\n{{\n" + body + "\n}\n"})
            var.append("c1call")
        # c2: the repetition loop inside the function
        c2 = {f"{n}.c": c2_kernel(loop), P.V5_HEADER: c2_header(loop), P.V5_MAIN: c2_main(loop, P.V5_SUITE)}
        put(out / "c2" / n / "orig", c2)
        if loop.expert is not None:
            put(out / "c2" / n / "ref", {**c2, f"{n}.c": c2_kernel(loop, expert=True)})
        var.append("c2")
        # c2arr: the same with arrays — only where the data is TSVC's five vectors and nothing else
        if not loop.globals_.strip() and not loop.init_extra.strip() and loop.body is None:
            (out / "_h" / "arr").mkdir(parents=True, exist_ok=True)
            (out / "_h" / "arr" / f"{n}.h").write_text(arrays_harness(hdr))
            arr = {f"{n}.c": c2_kernel(loop), P.V5_HEADER: c2_header(loop, arrays=True), P.V5_MAIN: c2_main(loop, "arr")}
            put(out / "c2arr" / n / "orig", arr)
            if loop.expert is not None:
                put(out / "c2arr" / n / "ref", {**arr, f"{n}.c": c2_kernel(loop, expert=True)})
            var.append("c2arr")
        loops[n] = row
    (out / "manifest.json").write_text(json.dumps({
        "loops": loops,
        "variants": {"v4": {"units": ["{loop}.c"]}, "c1": {"units": ["{loop}.c", "main.c"]},
                     "c1call": {"units": ["{loop}.c", "main.c"]}, "c2": {"units": ["{loop}.c", "main.c"]},
                     "c2arr": {"units": ["{loop}.c", "main.c"]}},
    }, indent=1) + "\n")
    print(f"{len(loops)} loops → {out}")
    for v in ("v4", "c1", "c1call", "c2", "c2arr"):
        print(f"  {v:7} {sum(1 for r in loops.values() if v in r['variants'])} loops")   # type: ignore[operator]
    return 0


if __name__ == "__main__":
    sys.exit(main())
