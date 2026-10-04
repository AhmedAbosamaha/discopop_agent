#!/usr/bin/env python3
"""PROTOTYPE of the clean two-file layout ("v5", §6 4 Oct) — scratchpad only, nothing in the repo is written.

For every loop of suite tsvc_b1 it renders, from the packager's own records (prepare_tsvc.Loop):
    <out>/prepared/tsvc_c1/<name>/<name>.c   the benchmark's file: one include, the loop's function
    <out>/prepared/tsvc_c1/<name>/data.h     what the code uses: the type, the size, the arrays (declarations)
    <out>/prepared/tsvc_c1/<name>/main.c     ours: main, the repetition loop, pb_mix
    <out>/_harness/tsvc_c1/<name>.h          ours, outside the package: data, initial values, perturbed input,
                                             digest, timing (v4's header without PB_MAIN; data with linkage)
"""
import json
import re
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "evaluation/agent/tools"))
import prepare_tsvc as P  # noqa: E402
from prepare_calib import SCAFFOLD  # noqa: E402

SUITE = "tsvc_c1"
HIDDEN_MACROS = {"k36"}          # the hidden fact is CODE (two accessor macros): it needs a header no model can open


def split_globals(loop):
    """The harness's file-scope lines of a loop -> (declarations for data.h, definitions for the hidden header,
    macros that must stay hidden)."""
    vis, hid, mac = [], [], []
    if not P._is_harness_global(loop.globals_):
        return vis, hid, mac
    for line in loop.globals_.splitlines():
        code = re.sub(r"\s*/\*.*?\*/\s*$", "", line).rstrip()
        if not code:
            continue
        if code.startswith("#define"):
            (mac if loop.name in HIDDEN_MACROS else vis).append(code)
        elif code.startswith("static "):
            vis.append("extern " + code[len("static "):])
            hid.append(code[len("static "):])
        else:
            raise ValueError(f"{loop.name}: unexpected harness global {line!r}")
    return vis, hid, mac


def size_block(loop):
    text = P.SIZE_BLOCK % {"reps": loop.reps}
    return "\n".join(l for l in text.splitlines() if not l.startswith("#define R ")).strip("\n") + "\n"


def data_h(loop):
    vis, _hid, mac = split_globals(loop)
    return ("#ifndef DATA_H\n#define DATA_H\n\n" + size_block(loop) + "\ntypedef double real_t;\n\n"
            + "extern real_t *a, *b, *c, *d, *e;\n" + "".join(l + "\n" for l in vis)
            + (f'\n#include "{SUITE}/{loop.name}_macros.h"\n' if mac else "")
            + f"\nreal_t kernel_{loop.name}(void);\n\n#endif\n")


def kernel_c(loop):
    _cat, decls, rep, ret = P._loop_function(loop)
    kernel_globals = "" if P._is_harness_global(loop.globals_) else loop.globals_
    body = textwrap.dedent(rep)
    body = "\n".join(("    " + l) if l.strip() else l for l in body.splitlines())
    std = "#include <stdlib.h>\n" if re.search(r"\bexit\s*\(", rep) else ""    # s481 calls exit()
    return (std + '#include "data.h"\n'
            + ("\n" + kernel_globals + "\n" if kernel_globals else "")
            + f"\nreal_t kernel_{loop.name}(void)\n{{\n"
            + (loop.pre + "\n" if loop.pre else "")
            + (decls + "\n" if decls else "")
            + body + "\n"
            + f"    return {ret};\n}}\n")


def main_c(loop):
    mix = "\n".join(l for l in P.PB_MIX.strip("\n").splitlines() if not l.lstrip().startswith(("/*", "*")))
    return (f'#include "data.h"\n#include "{SUITE}/{loop.name}.h"\n\n' + mix + "\n\n"
            "int main(int argc, char** argv)\n{\n"
            "  if (pb_setup(argc, argv)) return 1;\n"
            "  pb_timer_start();\n"
            "  real_t pb_result = (real_t)0;\n"
            "  for (int nl = 0; nl < R; nl++) {\n"
            f"    pb_result = kernel_{loop.name}();\n"
            "    pb_mix(nl);\n"
            "  }\n"
            "  pb_timer_stop();\n"
            "  pb_finish(pb_result);\n"
            "  return 0;\n}\n")


def harness_h(loop):
    _vis, hid, _mac = split_globals(loop)
    data = P.DATA % {"init_extra": loop.init_extra, "harness_globals": "".join(l + "\n" for l in hid)}
    assert "static real_t *a, *b, *c, *d, *e;" in data
    data = data.replace("static real_t *a, *b, *c, *d, *e;", "real_t *a, *b, *c, *d, *e;")
    driver = (P.DRIVER % {"emit_extra": loop.emit_extra}).split("/* `main`, expanded", 1)[0]
    return ("/* Measurement harness (prototype v5): data, initial values, perturbed input, digest, timing.\n"
            " * Outside the package; included by the package's main.c after data.h. */\n"
            "#ifndef PB_TSVC_HARNESS\n#define PB_TSVC_HARNESS\n\n"
            "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <math.h>\n#include <time.h>\n\n"
            f"#define R {loop.reps}\n" + SCAFFOLD + data + driver + "\n#endif\n")


def main():
    out = Path(sys.argv[1])
    names = sys.argv[2:]
    loops = [l for l in P.B1_LOOPS if not names or l.name in names]
    for loop in loops:
        d = out / "prepared" / SUITE / loop.name
        h = out / "_harness" / SUITE
        d.mkdir(parents=True, exist_ok=True)
        h.mkdir(parents=True, exist_ok=True)
        (d / f"{loop.name}.c").write_text(kernel_c(loop))
        (d / "data.h").write_text(data_h(loop))
        (d / "main.c").write_text(main_c(loop))
        (h / f"{loop.name}.h").write_text(harness_h(loop))
        mac = split_globals(loop)[2]
        if mac:
            (h / f"{loop.name}_macros.h").write_text("\n".join(mac) + "\n")
        import hashlib
        meta = {
            "suite": SUITE, "kernel": loop.name, "file": f"{loop.name}.c", "language": "c", "layout": "project",
            "project": {"units": [f"{loop.name}.c", "main.c"], "include_dirs": ["."]},
            "exclude_functions": ["main", "pb_mix"], "harness": f"{SUITE}/{loop.name}.h",
            "harness_sha256": hashlib.sha256((h / f"{loop.name}.h").read_bytes()).hexdigest(),
            "restructuring_class": loop.expected, "agent_dataset": "SMALL", "generator_version": "5-prototype",
        }
        blob = "".join((d / rel).read_text() for rel in sorted(p.name for p in d.iterdir() if p.suffix in (".c", ".h")))
        meta["output_sha256"] = hashlib.sha256(blob.encode()).hexdigest()   # as cli._package_digest computes it
        (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"{len(loops)} packages -> {out}")


if __name__ == "__main__":
    main()
