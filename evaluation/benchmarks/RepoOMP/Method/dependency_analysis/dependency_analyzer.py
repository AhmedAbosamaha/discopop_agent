#!/usr/bin/env python3
"""Global dependency analysis via clang LLVM IR.

Generates LLVM IR from C source with clang, then parses the IR to extract:
- Function call graph (caller -> callees)
- Global variable read/write sets per function
- Function-level dependency matrix
- Loop-carried dependency hints (reduction vs sequential) from source

Output is a JSON file consumed by the primitive addition stage.

Usage:
    python dependency_analyzer.py --src cg.c --out dep.json [--include -I../common]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict

FUNC_RE = re.compile(r"(?:^|\n)\s*(?:static\s+|extern\s+|inline\s+|const\s+|unsigned\s+|signed\s+|long\s+|short\s+|double\s+|float\s+|int\s+|void\s+|char\s+|struct\s+\w+\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{")


def stable_key(*parts):
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode()).hexdigest()[:16]


def span_for(text, start, end):
    line_start = text.rfind("\n", 0, start) + 1
    end_pos = max(start, end - 1)
    end_line_start = text.rfind("\n", 0, end_pos) + 1
    return {"start_line": text.count("\n", 0, start) + 1, "start_column": start - line_start + 1, "end_line": text.count("\n", 0, end_pos) + 1, "end_column": end - end_line_start + 1, "start_offset": start, "end_offset": end}


def function_spans(src_text, file=""):
    spans = []
    for match in FUNC_RE.finditer(src_text):
        depth = 0
        for pos in range(match.end() - 1, len(src_text)):
            if src_text[pos] == "{": depth += 1
            elif src_text[pos] == "}":
                depth -= 1
                if depth == 0:
                    spans.append({"name": match.group(1), "file": file,
                                  "line": src_text.count("\n", 0, match.start(1)) + 1,
                                  "end_line": src_text.count("\n", 0, pos + 1) + 1,
                                  "start": match.start(), "end": pos + 1,
                                  "text": src_text[match.start():pos + 1]})
                    break
    return spans


def independent_batches(records, dependency_matrix=None):
    matrix = dependency_matrix or []
    batches = []
    for record in records:
        # Only shared-write (true cross-function global mutation) forces a
        # singleton batch. unsafe-loop is informational and does not block
        # batching, since loop-level safety is decided per-loop.
        hard_block = "shared-write" in record.get("blockers", [])
        if record.get("evidence_confidence") != "high" or hard_block:
            batches.append([record]); continue
        placed = False
        for batch in batches:
            if any(x.get("evidence_confidence") != "high" or "shared-write" in x.get("blockers", []) for x in batch):
                continue
            conflict = any(record["name"] in x.get("calls", []) or x["name"] in record.get("calls", []) or
                           set(record.get("global_writes", [])) & set(x.get("global_reads", []) + x.get("global_writes", [])) or
                           set(x.get("global_writes", [])) & set(record.get("global_reads", [])) for x in batch)
            i = record.get("matrix_index")
            matrix_conflict = i is None or any(k is None or i >= len(matrix) or k >= len(matrix) or matrix[i][k] or matrix[k][i] for k in [x.get("matrix_index") for x in batch])
            if not conflict and not matrix_conflict:
                batch.append(record); placed = True; break
        if not placed: batches.append([record])
    return batches

CLANG = shutil.which("clang") or "clang"


def _run(cmd, cwd=None):
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout, proc.stderr


def generate_llvm_ir(src, out_ll, includes=None, extra_flags=None):
    """clang -S -emit-llvm -g -O0 <src> -o <out_ll>."""
    includes = includes or []
    extra_flags = extra_flags or []
    cmd = [CLANG, "-S", "-emit-llvm", "-g", "-O0"] + includes + extra_flags \
          + [src, "-o", out_ll]
    rc, out, err = _run(cmd)
    if rc != 0 or not os.path.exists(out_ll):
        raise RuntimeError(f"clang IR generation failed: {err.strip()}")
    return out_ll


def _collect_globals(ir):
    """Find @-prefixed global variable names."""
    globs = set()
    for line in ir.splitlines():
        m = re.match(r"(@[\w.]+)\s*=.*global", line.strip())
        if m:
            globs.add(m.group(1))
    return globs


def _analyze_functions(ir, globals_set):
    """Parse IR into function defs, calls, reads, writes of globals."""
    funcs = []
    calls = defaultdict(set)
    reads = defaultdict(set)
    writes = defaultdict(set)
    current = None
    for line in ir.splitlines():
        line = line.strip()
        m = re.match(r"define .*?(@[\w.]+)\(", line)
        if m:
            current = m.group(1)
            funcs.append(current)
            continue
        if current is None:
            continue
        if line == "}":
            current = None
            continue
        for called in re.findall(r"call .*?(@[\w.]+)\(", line):
            calls[current].add(called)
        for g in re.findall(r"load [^,]+,\s*[^,]*\*\s*(@[\w.]+)", line):
            if g in globals_set:
                reads[current].add(g)
        for g in re.findall(r"load [^,]*\*\s*(@[\w.]+)", line):
            if g in globals_set:
                reads[current].add(g)
        for g in re.findall(r"store [^,]+,[^,]*\*\s*(@[\w.]+)", line):
            if g in globals_set:
                writes[current].add(g)
        for g in re.findall(r"store [^,]+,\s*[^,]*\*\s*(@[\w.]+)", line):
            if g in globals_set:
                writes[current].add(g)
    defined = set(funcs)
    for f in calls:
        calls[f] = calls[f] & defined
    return funcs, calls, reads, writes


def _build_matrix(funcs, calls, reads, writes):
    """Boolean dependency matrix over functions."""
    n = len(funcs)
    idx = {f: i for i, f in enumerate(funcs)}
    mat = [[False] * n for _ in range(n)]
    for i, f in enumerate(funcs):
        if writes.get(f):
            mat[i][i] = True
    all_vars = set()
    for f in funcs:
        all_vars |= writes.get(f, set()) | reads.get(f, set())
    for v in all_vars:
        ws = [f for f in funcs if v in writes.get(f, set())]
        rs = [f for f in funcs if v in reads.get(f, set())]
        for w in ws:
            for r in rs:
                if w != r:
                    mat[idx[w]][idx[r]] = mat[idx[r]][idx[w]] = True
        for i, w1 in enumerate(ws):
            for w2 in ws[i + 1:]:
                mat[idx[w1]][idx[w2]] = mat[idx[w2]][idx[w1]] = True
    for caller in funcs:
        for callee in calls.get(caller, set()):
            if callee in idx:
                mat[idx[caller]][idx[callee]] = mat[idx[callee]][idx[caller]] = True
    return mat


def _strip_name(name):
    """@main -> main."""
    return name.lstrip("@")


def _loop_var_from_header(header):
    """Extract the induction variable name from a for-loop header."""
    m = re.search(r"\bfor\s*\(\s*(?:int\s+|long\s+|size_t\s+)?([A-Za-z_]\w*)\s*=", header)
    return m.group(1) if m else None


def _loop_body_end(lines, header_end_idx):
    """Find the line index of the closing brace of the loop body.

    header_end_idx is the index of the last line of the for-header. The
    opening brace often sits on that same header line (e.g. `for (...) {`),
    so we scan from header_end_idx itself, not header_end_idx+1, to count
    it. Returns the index of the line containing the matching '}'.
    Falls back to header_end_idx + 40 if no balanced brace is found.
    """
    depth = 0
    started = False
    for idx in range(header_end_idx, min(len(lines), header_end_idx + 200)):
        for ch in lines[idx]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return idx
    return min(len(lines) - 1, header_end_idx + 40)


def _strip_for_headers(body):
    """Remove inner for-loop header lines so stencil detection only sees data
    statements. A bound expression like `k < rowstr[j+1]` inside an inner loop
    header is not a data dependency on the outer loop var j."""
    out = []
    for line in body.splitlines():
        if re.match(r"\s*for\s*\(", line):
            continue
        out.append(line)
    return "\n".join(out)


def _has_stencil_read(body, loop_var):
    """True if body reads arr[loopvar ± const] or arr[... loopvar ± const ...],
    indicating a loop-carried (cross-iteration) data dependency. Only data
    statements are checked; inner for-loop headers are stripped first so a
    bound like `k < rowstr[j+1]` does not count as a stencil on j."""
    if not loop_var:
        return False
    body = _strip_for_headers(body)
    lv = re.escape(loop_var)
    # arr[loopvar+1], arr[loopvar-1], arr[loopvar + 2], arr[1+loopvar], etc.
    # Match the index expression in ANY subscript group (multi-dim arrays like
    # rhs[i][j+1][k] put the offset in a non-first subscript). Only data
    # statements are checked because inner for-loop headers are stripped first,
    # so a bound like k < rowstr[j+1] does not count as a stencil on j.
    pat = (
        r"\[[^\]]*\b" + lv + r"\s*[+\-]\s*\d+[^\]]*\]"
        r"|\[[^\]]*\b\d+\s*[+\-]\s*" + lv + r"[^\]]*\]"
    )
    return re.search(pat, body) is not None


def _writes_loopvar_offset(body, loop_var):
    """True if body writes arr[loopvar ± const] = ... (shifted write = dep).

    The offset subscript may sit in any dimension of a multi-dim array, so
    trailing subscript groups between the offset group and the assignment
    operator are allowed (e.g. lhs[i][j+1][k][0][0] = ...)."""
    if not loop_var:
        return False
    lv = re.escape(loop_var)
    tail = r"(?:\s*\[[^\]]*\])*"
    pat = (
        r"\w+\s*(?:\s*\[[^\]]*\])*\["
        r"[^\]]*\b" + lv + r"\s*[+\-]\s*\d+[^\]]*\]" + tail + r"\s*(?:\+=|-=|\*=|/=|=(?!=))"
        r"|\w+\s*(?:\s*\[[^\]]*\])*\["
        r"[^\]]*\b\d+\s*[+\-]\s*" + lv + r"[^\]]*\]" + tail + r"\s*(?:\+=|-=|\*=|/=|=(?!=))"
    )
    return re.search(pat, body) is not None


def _has_indirect_write(body, loop_var):
    """True if body writes arr[idx] = ... where idx does NOT contain the loop
    variable. An indirect index (e.g. i = colidx[k]; x[i] = ...) may alias
    across iterations, so the loop is not safely parallelizable."""
    if not loop_var:
        return False
    lv = re.escape(loop_var)
    assignment = r"(?:\+=|-=|\*=|/=|=(?!=))"
    # find every arr[...] = ... write
    for m in re.finditer(r"\w+\s*((?:\s*\[[^\]\n]*\])+)\s*" + assignment, body):
        subscripts = m.group(1)
        # safe if any subscript level contains the loop variable
        if re.search(r"\b" + lv + r"\b", subscripts):
            continue
        # no loop var in any subscript => indirect write
        return True
    return False


def _is_independent_loop(body, loop_var=None):
    """A loop is independent if it writes arr[loopvar] = ... (distinct index
    per iteration) AND has no stencil read arr[loopvar±const] AND no indirect
    write arr[non-loopvar] = ... (which may alias across iterations)."""
    if loop_var and _has_stencil_read(body, loop_var):
        return False
    if loop_var and _writes_loopvar_offset(body, loop_var):
        return False
    if loop_var and _has_indirect_write(body, loop_var):
        return False
    if loop_var:
        lv = re.escape(loop_var)
        # write to arr[loopvar] = ... (loop var as a sole or simple index).
        # Support multi-dim arrays: arr[k][j][i] = ... The loop var must appear
        # in the FIRST subscript so each iteration writes a distinct slice.
        # Match the array name followed by one or more [subscript] groups where
        # the first group contains the loop var, then an assignment operator.
        if re.search(
            r"\w+\s*\[[^\]]*\b" + lv + r"\b[^\]]*\](?:\s*\[[^\]]*\])*\s*(?:\.\w+\s*=|->\w+\s*=|\+=|-=|\*=|/=|=(?!=))",
            body):
            return True
        # Multi-dim write where the loop var sits in a non-first subscript,
        # e.g. cffts3 outer j loop writes xout[k][j][i] = y0[k][i]... Each j
        # writes a distinct slice, so it is independent. Stencil reads and
        # indirect writes are already excluded above. Match an array write
        # whose subscript chain contains the loop var anywhere.
        if re.search(
            r"\w+((?:\s*\[[^\]]*\])+)\s*(?:\.\w+\s*=|->\w+\s*=|\+=|-=|\*=|/=|=(?!=))",
            body):
            for m in re.finditer(
                r"\w+((?:\s*\[[^\]]*\])+)\s*(?:\.\w+\s*=|->\w+\s*=|\+=|-=|\*=|/=|=(?!=))",
                body):
                if re.search(r"\b" + lv + r"\b", m.group(1)):
                    return True
        # NPB complex-multiply macros (cmul, crmul, cadd) write their first
        # argument: crmul(u1[k][j][i], a, b) expands to u1[k][j][i].real = ...
        # The first arg is the write target. If it is arr[loopvar]..., the loop
        # is independent (each iteration writes a distinct element).
        for m in re.finditer(r"\b(?:cmul|crmul|cadd|csub)\s*\(\s*(\w+(?:\s*\[[^\]]*\])+)", body):
            first_arg = m.group(1)
            # first subscript must contain the loop var
            first_sub = re.match(r"\w+\s*\[([^\]]*)\]", first_arg)
            if first_sub and re.search(r"\b" + lv + r"\b", first_sub.group(1)):
                return True
    return bool(re.search(r"\w+\s*\[\s*\w+\s*\]\s*=", body))
    return bool(re.search(r"\w+\s*\[\s*\w+\s*\]\s*=", body))


def _body_has_call(body):
    """True if body calls a function (identifier followed by '(' that is not a
    control keyword). Function calls inside a loop body can have side effects
    or carry cross-iteration state, so the loop is not a safe reduction."""
    return re.search(r"\b(?!if|for|while|switch|return|sizeof)([A-Za-z_]\w*)\s*\(", body) is not None


def _is_reset_in_body(body, var):
    """True if var is assigned a non-self value (var = <expr not starting with
    var>) inside body, meaning it is recomputed rather than accumulated across
    iterations. `var = var + ...` and `var += ...` do not count as resets."""
    ev = re.escape(var)
    for m in re.finditer(r"\b" + ev + r"\s*=(?!=)\s*", body):
        rest = body[m.end():].lstrip()
        # if the rhs starts with the same var, it is a self-update (var = var ...)
        if rest.startswith(var) and re.match(r"\b" + ev + r"\b", rest):
            return False
        return True
    return False


def _body_has_array_write(body):
    """True if body writes to any array element (arr[...] = ...). A reduction
    loop that also writes arrays may alias across iterations, so it is not a
    safe parallel reduction. Also catches writes through a dereferenced
    pointer (*ptr = ... or *(ptr) = ... or *(ptr+off) = ...), which are
    array writes in disguise (e.g. Strassen's *(C11) += x)."""
    if re.search(r"\w+\s*\[[^\]]*\]\s*(?:\+=|-=|\*=|/=|=(?!=))", body):
        return True
    return re.search(r"\*\s*\(*\s*\w+(?:\s*[+\-]\s*\w+)*\s*\)*\s*(?:\+=|-=|\*=|/=|=(?!=))", body) is not None


def _is_reduction_loop(body, loop_var):
    """True if body accumulates into a scalar (not indexed by loop var) via
    +=/-=/*=//= or x = x op expr, AND that scalar is not an array element
    indexed by the loop var (which would be a race, not a reduction).

    Rejects loops whose body contains a function call (side effects or
    cross-iteration state), an array write (may alias across iterations), or
    where the accumulator is reset by a plain assignment inside the body
    (meaning it is not a cross-iteration sum)."""
    if not loop_var:
        return False
    if _body_has_call(body):
        return False
    if _body_has_array_write(body):
        return False
    lv = re.escape(loop_var)
    def _used_as_index(var):
        # True if var appears inside [...] brackets as an array index.
        # Such a variable is read to compute an access position, so it is
        # loop-carried, not a pure reduction accumulator.
        return re.search(r"\[[^\]]*\b" + re.escape(var) + r"\b", body) is not None
    # If any scalar accumulator is read as an array index, the loop has a
    # loop-carried dependency (the index value depends on prior iterations),
    # so the whole loop is not a safe parallel reduction.
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(\+=|-=|\*=|/=|\+\+|--)\s*", body):
        var = m.group(1)
        if var == loop_var:
            continue
        if _used_as_index(var):
            return False
    for m in re.finditer(r"\+\+\s*([A-Za-z_]\w*)|--\s*([A-Za-z_]\w*)", body):
        var = m.group(1) or m.group(2)
        if var == loop_var:
            continue
        if _used_as_index(var):
            return False
    # scalar += expr  (scalar is a bare name, not arr[...])
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(\+=|-=|\*=|/=)\s*", body):
        var = m.group(1)
        if var == loop_var:
            continue
        # skip if var appears as arr[var] write target (array, not scalar)
        if re.search(r"\b" + re.escape(var) + r"\s*\[", body):
            continue
        # skip if var is read as an array index inside [...] (loop-carried)
        if _used_as_index(var):
            continue
        # accumulator reset by a plain assignment to a non-self value inside
        # body => it is recomputed each iteration, not a cross-iteration sum
        if _is_reset_in_body(body, var):
            continue
        return True
    # x = x + expr  (scalar self-update)
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*=\s*\1\s*[+\-*/]", body):
        var = m.group(1)
        if var == loop_var:
            continue
        if re.search(r"\b" + re.escape(var) + r"\s*\[", body):
            continue
        if _used_as_index(var):
            continue
        # same reset check: var = <not var> means recomputed, not reduced
        if _is_reset_in_body(body, var):
            continue
        return True
    return False


def _reads_threadprivate(body, threadprivate):
    """True if body reads a threadprivate variable. Reading a threadprivate
    var populated by serial code outside the loop reads uninitialized
    per-thread storage on non-master threads."""
    if not threadprivate:
        return False
    for var in threadprivate:
        if re.search(r"\b" + re.escape(var) + r"\b", body):
            return True
    return False


def _scalar_used_after_loop(lines, body_end_idx, body, loop_var):
    """True if a scalar assigned inside the loop is read after the loop in the
    same function. Such a scalar carries state out of the loop and cannot be
    safely privatized (the master thread's copy may not reflect other threads'
    writes). Reduction variables are excluded because they are handled by
    reduction clauses, not private."""
    # find scalars assigned in the body (bare name = ..., not arr[...])
    candidates = set()
    for m in re.finditer(r"(?m)^\s*([A-Za-z_]\w*)\s*(?:\+=|-=|\*=|/=|=(?!=))", body):
        var = m.group(1)
        if var == loop_var:
            continue
        # skip if used as array (arr[var])
        if re.search(r"\b" + re.escape(var) + r"\s*\[", body):
            continue
        # skip reduction accumulators (x = x + ... or x += ...)
        if re.search(r"\b" + re.escape(var) + r"\s*=\s*" + re.escape(var) + r"\b", body) or \
           re.search(r"\b" + re.escape(var) + r"\s*(\+=|-=|\*=|/=)", body):
            continue
        # skip per-iteration temporaries that are reset each iteration
        # (fac1 = 1./lhs[...] recomputed, not state carried across iterations).
        # Such a scalar is written and fully consumed within one iteration, so
        # it privatizes cleanly. Only a scalar whose value flows from one
        # iteration to the next truly blocks parallelization.
        if _is_reset_in_body(body, var):
            continue
        candidates.add(var)
    if not candidates:
        return False
    # scan up to 40 lines after the loop body for a read of any candidate
    tail = "\n".join(lines[body_end_idx + 1:body_end_idx + 1 + 40])
    for var in candidates:
        if re.search(r"\b" + re.escape(var) + r"\b", tail):
            return True
    return False


def analyze_loops(src_text, threadprivate=None):
    """Heuristic loop-carried dependency analysis from C source.

    Scans for `for (...)` loops and classifies each as:
      - parallel_safe: no cross-iteration write to same index
      - reduction: accumulates into a scalar (+=, -=, etc.)
      - sequential: loop body writes to array indexed by loop var of an
        outer/earlier iteration (true loop-carried dep)
    Returns list of loop descriptors with source line numbers.
    """
    threadprivate = threadprivate or set()
    loops = []
    lines = src_text.splitlines()
    for i, line in enumerate(lines):
        if not re.search(r"\bfor\s*\(", line):
            continue
        # gather the loop header (may span lines)
        header = line
        depth = header.count("(") - header.count(")")
        j = i
        while depth > 0 and j + 1 < len(lines):
            j += 1
            header += " " + lines[j]
            depth += lines[j].count("(") - lines[j].count(")")
        # find the loop body region using balanced-brace matching
        body_start = j + 1
        body_end = _loop_body_end(lines, j)
        body = "\n".join(lines[body_start:body_end + 1])
        loop_var = _loop_var_from_header(header)
        is_reduction = _is_reduction_loop(body, loop_var)
        independent = _is_independent_loop(body, loop_var)
        # A loop is parallelizable only if it is a true scalar reduction or a
        # stencil-free independent array write. Stencil reads (arr[i±1]) and
        # shifted writes make it sequential. Reading a threadprivate variable
        # populated outside the loop also blocks parallelization. A scalar
        # assigned in the body and read after the loop also blocks it, because
        # privatizing it would lose other threads' writes.
        tp_read = _reads_threadprivate(body, threadprivate)
        scalar_escape = _scalar_used_after_loop(lines, body_end, body, loop_var)
        parallelizable = (is_reduction or independent) and not tp_read and not scalar_escape
        loops.append({
            "line": i + 1,
            "header": header.strip()[:120],
            "is_reduction": is_reduction,
            "parallelizable": parallelizable,
        })
    return loops


def _collect_threadprivate(src_text, src_path=None, includes=None):
    """Find variables declared #pragma omp threadprivate(...).

    These are per-thread copies. A loop that reads a threadprivate variable
    which was populated by serial code outside the loop reads uninitialized
    per-thread storage on other threads. Such loops are NOT parallelizable.

    Scans the main source plus any .h headers in the source directory and the
    provided -I include dirs, since threadprivate pragmas usually live in
    headers (e.g. NPB header.h).
    """
    names = set()
    texts = [src_text]
    # gather candidate header paths
    header_dirs = []
    if src_path:
        header_dirs.append(os.path.dirname(os.path.abspath(src_path)))
    if includes:
        for inc in includes:
            if inc.startswith("-I"):
                header_dirs.append(inc[2:])
    for d in header_dirs:
        if not d or not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if fname.endswith(".h"):
                try:
                    with open(os.path.join(d, fname), errors="replace") as f:
                        texts.append(f.read())
                except OSError:
                    pass
    for text in texts:
        for m in re.finditer(r"#\s*pragma\s+omp\s+threadprivate\s*\(([^)]*)\)", text):
            for var in m.group(1).split(","):
                var = var.strip()
                if var:
                    names.add(var)
    return names


def analyze(src, out_json, includes=None, extra_flags=None):
    includes = includes or []
    extra_flags = extra_flags or []
    os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
    out_ll = out_json + ".ll"
    generate_llvm_ir(src, out_ll, includes, extra_flags)
    with open(out_ll) as f:
        ir = f.read()
    globs = _collect_globals(ir)
    funcs, calls, reads, writes = _analyze_functions(ir, globs)
    matrix = _build_matrix(funcs, calls, reads, writes)
    with open(src) as f:
        src_text = f.read()
    threadprivate = _collect_threadprivate(src_text, src_path=src, includes=includes)
    loops = analyze_loops(src_text, threadprivate=threadprivate)
    spans = function_spans(src_text, os.path.basename(src))
    evidence = []
    for index, name in enumerate(funcs):
        clean = _strip_name(name)
        span = next((item for item in spans if item["name"] == clean), None)
        local_loops = [item for item in loops if span and span["line"] <= item["line"] <= span["end_line"]]
        blockers = []
        if writes.get(name): blockers.append("shared-write")
        # unsafe-loop is informational: some loops in this function carry
        # dependencies. Loop-level safety is decided per-loop by the
        # parallelizable flag, so this does not block function-level LLM work.
        if any(not item["parallelizable"] for item in local_loops): blockers.append("unsafe-loop")
        evidence.append({
            "name": clean, "file": os.path.basename(src),
            "line": span["line"] if span else None,
            "end_line": span["end_line"] if span else None,
            "span": span_for(src_text, span["start"], span["end"]) if span else None,
            "evidence_id": "evidence:function:" + stable_key(os.path.abspath(src), clean, span["start"], span["end"]) if span else None,
            "calls": sorted(_strip_name(item) for item in calls.get(name, set())),
            "global_reads": sorted(reads.get(name, set())),
            "global_writes": sorted(writes.get(name, set())),
            "openmp": bool(span and "#pragma omp" in span["text"]),
            "loops": local_loops, "blockers": blockers,
            "hotspot_keys": [f"{clean}:{os.path.basename(src)}:{span['line']}" if span else clean],
            "evidence_confidence": "high" if span else "low", "matrix_index": index,
        })
    result = {
        "source": os.path.abspath(src),
        "llvm_ir": os.path.abspath(out_ll),
        "functions": [_strip_name(f) for f in funcs],
        "function_calls": {
            _strip_name(k): [_strip_name(v) for v in vs]
            for k, vs in calls.items()
        },
        "function_reads": {
            _strip_name(k): sorted(v) for k, v in reads.items()
        },
        "function_writes": {
            _strip_name(k): sorted(v) for k, v in writes.items()
        },
        "dependency_matrix": matrix,
        "loops": loops,
        "function_evidence": evidence,
        "independent_batches": independent_batches(evidence, matrix),
        "summary": {
            "total_functions": len(funcs),
            "total_loops": len(loops),
            "parallelizable_loops": sum(1 for l in loops if l["parallelizable"]),
            "reduction_loops": sum(1 for l in loops if l["is_reduction"]),
        },
    }
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    return result


def main():
    ap = argparse.ArgumentParser(description="LLVM IR dependency analyzer")
    ap.add_argument("--src", required=True, help="C source file")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--include", action="append", default=[],
                    help="include path (repeatable), e.g. -I../common")
    ap.add_argument("--flag", action="append", default=[],
                    help="extra clang flag (repeatable), e.g. -fopenmp")
    args = ap.parse_args()
    res = analyze(args.src, args.out, args.include, args.flag)
    print(f"[dep] wrote {args.out}")
    print(f"[dep] functions: {res['summary']['total_functions']}, "
          f"loops: {res['summary']['total_loops']} "
          f"(parallelizable: {res['summary']['parallelizable_loops']}, "
          f"reduction: {res['summary']['reduction_loops']})")


if __name__ == "__main__":
    main()
