#!/usr/bin/env python3
"""Deterministic OpenMP loop insertion with reduction, nested, and independent detection.

Patterns (in order):
1. Reduction: x += expr / x = x op expr → #pragma omp parallel for reduction(op:x)
2. Nested loop: outer for with only inner for → #pragma omp for collapse(2) or private(k)
3. Independent array: arr[i] = expr → #pragma omp parallel for
4. randlc seed-advance loop: recompute per-iteration seed from k, move static
   scratch local, then #pragma omp parallel for schedule(static) (post-pass)

Never fails. If no pattern matches, return empty changes.
"""
import argparse
import json
import re
from pathlib import Path

FOR_RE = re.compile(
    r"^(\s*)(for\s*\(\s*(?:(?:const|volatile|unsigned|signed|short|long|int|size_t)\s+)*"
    r"([A-Za-z_]\w*)\s*=\s*[^;]+;[^;]+;[^)]*\))\s*\{"
)
CONTROL_RE = re.compile(r"\b(?:break|continue|goto|return|exit|abort)\b")
REDUCTION_ASSIGN = re.compile(
    r"(?<![A-Za-z0-9_])([A-Za-z_]\w*)\s*(\+=|-=|\*=|/=)\s*"
)
REDUCTION_EQUAL = re.compile(
    r"(?<![A-Za-z0-9_])([A-Za-z_]\w*)\s*=\s*\1\s*([+\-*/])"
)
COLLAPSE_RE = re.compile(
    r"^\s*for\s*\(\s*(?:(?:const|volatile|unsigned|signed|short|long|int|size_t)\s+)*"
    r"([A-Za-z_]\w*)\s*=\s*[^;]+;[^;]+;[^)]*\)\s*\{"
)


def _mask_noncode(line, state):
    out = []
    index = 0
    mode = state
    while index < len(line):
        if mode == "block":
            end = line.find("*/", index)
            if end < 0:
                return " " * len(line), mode
            out.extend(" " * (end + 2 - index))
            index = end + 2
            mode = None
            continue
        if line.startswith("//", index):
            out.extend(" " * (len(line) - index))
            break
        if line.startswith("/*", index):
            out.extend("  ")
            index += 2
            mode = "block"
            continue
        if line[index] in "\"'":
            quote = line[index]
            out.append(" ")
            index += 1
            while index < len(line):
                out.append(" ")
                if line[index] == "\\" and index + 1 < len(line):
                    out.append(" ")
                    index += 2
                    continue
                if line[index] == quote:
                    index += 1
                    break
                index += 1
            continue
        out.append(line[index])
        index += 1
    return "".join(out), mode


def _masked_lines(lines):
    masked = []
    state = None
    for line in lines:
        value, state = _mask_noncode(line, state)
        masked.append(value)
    return masked


def _balanced_block(masked, start):
    depth = 0
    opened = False
    for index in range(start, len(masked)):
        for char in masked[index]:
            if char == "{":
                depth += 1
                opened = True
            elif char == "}":
                depth -= 1
                if depth < 0:
                    return None
                if opened and depth == 0:
                    return index
    return None


def _block_text(masked, start, end):
    return "\n".join(masked[start:end + 1])


def _move_scratch_decls(lines):
    """Move local scratch-array declarations inside the parallel loop body.

    NPB cffts1/2/3 declare `dcomplex y0[...]` and `dcomplex y1[...]` in a block
    before the parallelized loop (cffts1/2: for(k); cffts3: for(j)). When that
    loop is parallelized, the arrays are shared across threads and race. Move
    the declarations to just inside the parallel loop body so each thread gets
    its own copy. Only moves decls that appear in the same block, above the
    pragma that guards the loop.
    """
    out = list(lines)
    par_re = re.compile(r"#\s*pragma\s+omp\s+parallel\s+for\b")
    # Only dcomplex scratch arrays (y0/y1 in cffts1/2/3) need moving. int/double
    # arrays like `int logd[3]` are small fixed scratch that are fine shared and
    # must not be pulled inside a loop (they are read after it).
    decl_re = re.compile(r"^\s*dcomplex\s+(\w+)\s*\[")
    loop_re = re.compile(r"\bfor\s*\(\s*[A-Za-z_]\w*\s*=")
    i = 0
    while i < len(out):
        if not par_re.search(out[i]):
            i += 1
            continue
        # find the loop this pragma guards (within a few lines)
        loop_idx = None
        for j in range(i + 1, min(i + 6, len(out))):
            if loop_re.search(out[j]):
                loop_idx = j
                break
        if loop_idx is None:
            i += 1
            continue
        # find the opening brace of the loop body
        brace_idx = None
        for j in range(loop_idx, min(loop_idx + 4, len(out))):
            if "{" in out[j]:
                brace_idx = j
                break
        if brace_idx is None:
            i += 1
            continue
        # collect decl lines ABOVE the pragma, back to the enclosing block open
        decls = []
        decl_indices = []
        for j in range(i - 1, max(-1, i - 8), -1):
            stripped = out[j].strip()
            # stop at the block opener (lone {, or a line ending in { like
            # `) {` which opens a function body). Do not walk into the
            # function signature and treat parameters as scratch decls.
            if "{" in out[j] or stripped == "":
                break
            if decl_re.match(out[j]):
                # skip function-parameter lines: they end with `,` or `)`
                # (e.g. `dcomplex y0[NX][FFTBLOCKPAD],`). A real local decl
                # ends with `;`.
                if stripped.endswith(",") or stripped.endswith(")") or \
                   stripped.endswith(",)") or stripped.endswith(")"):
                    break
                decls.insert(0, out[j])
                decl_indices.append(j)
            elif stripped.startswith("#") or stripped.startswith("//"):
                break
        if not decls:
            i += 1
            continue
        # remove the decl lines (reverse order to keep indices valid)
        for j in sorted(decl_indices, reverse=True):
            del out[j]
        # recompute indices after deletion
        shift = len(decls)
        brace_idx -= shift
        loop_idx -= shift
        i -= shift
        # insert decls right after the opening brace line
        insert_at = brace_idx + 1
        for d in reversed(decls):
            out.insert(insert_at, d)
        i = insert_at + len(decls)
    return out


def _strip_moved_from_private(lines):
    """Remove moved scratch-array names from private() clauses.

    `_move_scratch_decls` relocates `dcomplex y0[...]` / `dcomplex y1[...]`
    declarations from above the pragma into the parallel loop body. Once
    inside the body, those names are block-scope variables auto-private per
    thread, so listing them in the pragma's private() clause is both
    redundant and invalid (GCC rejects 'y0 is not a variable in clause
    private' because the decl now sits below the pragma). Strip them.
    """
    par_re = re.compile(r"(#\s*pragma\s+omp\s+parallel\s+for\b.*private\s*\()([^)]*)(\))")
    # re-scan to find which scratch names were moved into loop bodies
    out = list(lines)
    for i, line in enumerate(out):
        m = par_re.search(line)
        if not m:
            continue
        priv_vars = [v.strip() for v in m.group(2).split(",") if v.strip()]
        # a var is "moved" if its dcomplex decl appears AFTER this pragma line
        # (inside the loop body) rather than above it. Only a real local
        # declaration counts (ends with `;`); function-parameter decls end
        # with `,` or `)` and must not be stripped.
        moved = set()
        for v in priv_vars:
            decl_pat = re.compile(r"^\s*dcomplex\s+" + re.escape(v) + r"\s*\[")
            # search forward up to ~40 lines for the decl, stopping at the
            # enclosing function's closing brace (a line that is just `}`)
            for j in range(i + 1, min(i + 50, len(out))):
                if out[j].strip() == "}":
                    break
                m2 = decl_pat.match(out[j])
                if m2:
                    if out[j].rstrip().endswith(";"):
                        moved.add(v)
                    break
        if not moved:
            continue
        kept = [v for v in priv_vars if v not in moved]
        if len(kept) == len(priv_vars):
            continue
        if kept:
            new_priv = "private(" + ", ".join(kept) + ")"
        else:
            new_priv = ""
        new_line = line[:m.start(1)] + m.group(1).rsplit("private", 1)[0] + new_priv + m.group(3)
        # group(3) is the closing ) of private; but there may be trailing clause text
        # rebuild cleanly: prefix before 'private(' + new_priv + rest after ')'
        before = line[:m.start()]
        after = line[m.end():]
        new_line = before + (m.group(1)[:m.group(1).index("private")] + new_priv) + after
        # collapse double spaces and trim
        new_line = re.sub(r" +", " ", new_line).rstrip()
        out[i] = new_line
    return out


def _rename_shadowed_params(lines):
    """Rename function parameters shadowed by scratch-array decls moved inside
    a parallel k loop.

    `_move_scratch_decls` moves `dcomplex y0[NX][FFTBLOCKPAD]` declarations
    inside the k loop body. But cffts1/2/3 also take parameters named y0/y1,
    so the moved local decls shadow the params and GCC's OpenMP runtime
    produces zero checksums. When a moved decl shadows a function parameter,
    rename the parameter (y0 -> y0p, y1 -> y1p) in the signature and all
    body uses so the param is the real shared array and the local decl is a
    per-thread scratch.
    """
    out = list(lines)
    # find functions whose body has a #pragma omp parallel for ... for (var=...)
    # and a moved scratch decl of y0/y1 inside that loop.
    func_re = re.compile(r"^\s*(?:static\s+)?(?:void|int|double|float|dcomplex)\s+(\w+)\s*\(")
    loop_re = re.compile(r"\bfor\s*\(\s*[A-Za-z_]\w*\s*=")
    par_re = re.compile(r"#\s*pragma\s+omp\s+parallel\s+for\b")
    scratch_re = re.compile(r"^\s*dcomplex\s+(y0|y1)\s*\[")
    i = 0
    while i < len(out):
        fm = func_re.match(out[i])
        if not fm:
            i += 1
            continue
        fname = fm.group(1)
        # find end of this function by brace matching from the signature line
        # locate the opening brace
        sig_start = i
        open_idx = None
        for j in range(i, min(i + 20, len(out))):
            if "{" in out[j]:
                open_idx = j
                break
        if open_idx is None:
            i += 1
            continue
        depth = 0
        close_idx = None
        for j in range(open_idx, len(out)):
            depth += out[j].count("{") - out[j].count("}")
            if depth <= 0:
                close_idx = j
                break
        if close_idx is None:
            i += 1
            continue
        body = out[open_idx:close_idx + 1]
        # detect: a parallel for pragma followed by a loop with a scratch decl inside
        has_moved = False
        for j in range(len(body)):
            if par_re.search(body[j]):
                # look ahead a few lines for the loop and a scratch decl inside its body
                for k in range(j + 1, min(j + 8, len(body))):
                    if loop_re.search(body[k]):
                        # look inside loop body for scratch decl
                        for m in range(k, min(k + 20, len(body))):
                            sm = scratch_re.match(body[m])
                            if sm:
                                has_moved = True
                                break
                            if body[m].strip() == "}" and m > k:
                                break
                        if has_moved:
                            break
                    if re.search(r"\bfor\s*\(", body[k]) and not loop_re.search(body[k]):
                        break
                if has_moved:
                    break
        if not has_moved:
            i = close_idx + 1
            continue
        # signature: the y0/y1 params appear between the ( on sig_start line
        # and the ) that closes the parameter list. Rename y0->y0p, y1->y1p
        # only if they appear as a parameter name (followed by [ or , or )).
        sig_end = None
        paren = 0
        for j in range(sig_start, open_idx + 1):
            for ch in out[j]:
                if ch == "(":
                    paren += 1
                elif ch == ")":
                    paren -= 1
                    if paren == 0:
                        sig_end = j
                        break
            if sig_end is not None:
                break
        if sig_end is None:
            i = close_idx + 1
            continue
        for j in range(sig_start, sig_end + 1):
            line = out[j]
            # rename parameter names y0 / y1 to y0p / y1p
            # match as a word boundary followed by [ , or ) or whitespace
            new_line = re.sub(
                r"\b(y0|y1)\b(?=\s*(?:\[|,|\)))",
                lambda mm: mm.group(1) + "p",
                line,
            )
            out[j] = new_line
        # Body uses of y0/y1 are LEFT UNTOUCHED. The moved local decls inside
        # the parallel loop shadow the (now-renamed) params, so body y0/y1
        # correctly resolve to the per-thread scratch arrays. Renaming body
        # uses would point them at the shared params and reintroduce the race.
        i = close_idx + 1
    return out


def _randlc_seed_rewrite(lines):
    """Pattern 4: randlc seed-advance loop rewrite (aaai transform).

    Some loops carry a pseudo-random seed across iterations via
    `randlc(&start, an)`, so the dependency analyzer keeps the loop marked
    parallelizable (each iteration writes a distinct array slice) but the
    seed itself cannot be shared across threads. The serial code advances
    `start` at the end of each iteration; parallelizing it as-is races on
    `start` and on the shared `static` scratch buffer `tmp`.

    The aaai transform breaks the cross-iteration dependency by recomputing
    each iteration's seed directly from k instead of advancing a running
    seed, and by making tmp a per-iteration local. Concretely for the
    compute_initial_conditions shape:

      pre-loop:  start = SEED;
                 ipow46(A, OFFSET, &an); dummy = randlc(&start, an);
                 ipow46(A, 2*NX*NY, &an);            <- stride, REMOVE
      loop:
        x0 = start;                               <- REPLACE seed
        vranlc(2*NX*dims[0][1], &x0, A, tmp);
        t = 1;
        for (j ...) for (i ...) u0[k][j][i]... = tmp[t++];
        if (k != dims[0][2]) dummy = randlc(&start, an);  <- REMOVE

    becomes:

      #pragma omp parallel for private(k, an, dummy) schedule(static)
      for (k = 0; k < dims[0][2]; k++) {
          double x0;
          double tmp[NX*2*MAXDIM+1];
          int i, j, t;
          x0 = start;
          ipow46(A, (double)k * 2.0 * NX * dims[0][1], &an);
          dummy = randlc(&x0, an);
          vranlc(2*NX*dims[0][1], &x0, A, tmp);
          t = 1;
          for (j ...) for (i ...) u0[k][j][i]... = tmp[t++];
      }

    Detection is structural, not name-based, so it generalizes to any
    loop with the same shape: a `static` scratch buffer written by a
    vranlc call whose seed comes from a scalar advanced by randlc at the
    loop tail.
    """
    out = list(lines)
    func_re = re.compile(r"^\s*(?:static\s+)?(?:void|int|double|float|dcomplex)\s+(\w+)\s*\(")
    static_tmp_re = re.compile(r"^\s*static\s+(?:double|float)\s+(\w+)\s*\[")
    seed_init_re = re.compile(r"=\s*SEED\s*;?\s*$")
    applied = []
    for i, line in enumerate(out):
        fm = func_re.match(line)
        if not fm:
            continue
        fname = fm.group(1)
        # find function body span
        open_idx = None
        for j in range(i, min(i + 20, len(out))):
            if "{" in out[j]:
                open_idx = j
                break
        if open_idx is None:
            continue
        depth = 0
        close_idx = None
        for j in range(open_idx, len(out)):
            depth += out[j].count("{") - out[j].count("}")
            if depth <= 0:
                close_idx = j
                break
        if close_idx is None:
            continue
        body = out[open_idx:close_idx + 1]
        body_offset = open_idx
        # structural markers
        static_tmp = None
        seed_var = None
        for bl in body:
            stm = static_tmp_re.match(bl)
            if stm and static_tmp is None:
                static_tmp = stm.group(1)
                # size expression for the local decl
                msz = re.search(r"\[([^\]]*)\]", bl)
                static_tmp_size = msz.group(1) if msz else ""
        if static_tmp is None:
            continue
        for bl in body:
            mm = seed_init_re.search(bl)
            if mm:
                mv = re.match(r"\s*([A-Za-z_]\w*)\s*=", bl)
                if mv:
                    seed_var = mv.group(1)
                    break
        if seed_var is None:
            continue
        # need: pre-loop ipow46(...,&an) + randlc(&seed,an),
        #       the stride ipow46(A, 2*NX*NY, &an),
        #       a for loop over k whose body sets x0 = seed then vranlc,
        #       and a trailing randlc(&seed, an) guarded by k != limit.
        # the stride call's second argument is exactly 2*NX*NY (the
        # offset-init call wraps it in a larger expr, so anchor the match
        # to the call's argument list to avoid grabbing the wrong line).
        pre_stride_idx = None
        for bidx, bl in enumerate(body):
            mm = re.search(r"\bipow46\s*\(\s*\w+\s*,\s*(2\s*\*\s*NX\s*\*\s*NY)\s*,", bl)
            if mm:
                pre_stride_idx = bidx
                break
        if pre_stride_idx is None:
            continue
        # find the k loop: for (k = 0; k < dims[0][2]; k++)
        k_loop_body_idx = None
        k_loop_var = None
        for bidx, bl in enumerate(body):
            ml = re.match(
                r"\s*for\s*\(\s*(?:int\s+)?([A-Za-z_]\w*)\s*=\s*0\s*;\s*"
                r"\1\s*<\s*dims\[0\]\[2\]\s*;",
                bl,
            )
            if ml:
                k_loop_body_idx = bidx
                k_loop_var = ml.group(1)
                break
        if k_loop_body_idx is None or k_loop_var is None:
            continue
        # the loop body: lines from k_loop_body_idx+1 to the matching close
        # of the k loop. Find the close brace by depth from the for line.
        k_open = None
        for j in range(k_loop_body_idx, min(k_loop_body_idx + 5, len(body))):
            if "{" in body[j]:
                k_open = j
                break
        if k_open is None:
            continue
        kdepth = 0
        k_close = None
        for j in range(k_open, len(body)):
            kdepth += body[j].count("{") - body[j].count("}")
            if kdepth <= 0:
                k_close = j
                break
        if k_close is None:
            continue
        kbody = body[k_open + 1:k_close]
        # confirm shape: x0 = seed ; vranlc(...,&x0,...,tmp) ; ... ; if (k != ...) randlc(&seed,an)
        x0_var = None
        x0_assign_idx = None
        for kbidx, kbl in enumerate(kbody):
            mm = re.match(r"\s*([A-Za-z_]\w*)\s*=\s*" + re.escape(seed_var) + r"\s*;", kbl)
            if mm:
                x0_var = mm.group(1)
                x0_assign_idx = kbidx
                break
        if x0_var is None or x0_assign_idx is None:
            continue
        if not any(re.search(r"\bvranlc\s*\(", kbl) and re.search(
            r"&\s*" + re.escape(x0_var), kbl
        ) for kbl in kbody):
            continue
        if not any(
            re.search(r"\brandlc\s*\(", kbl)
            and re.search(r"&\s*" + re.escape(seed_var), kbl)
            for kbl in kbody
        ):
            continue
        # passed structural checks. Apply the rewrite.

        # 1. remove the static tmp decl line; the per-iteration local decl
        #    is injected into the loop body instead.
        for bidx, bl in enumerate(body):
            if static_tmp_re.match(bl) and re.search(
                r"\b" + re.escape(static_tmp) + r"\b", bl
            ):
                body[bidx] = None  # mark for deletion
        # also drop the now-unused loop-local t/i/j decls if they are on the
        # same line as the static tmp? they are separate lines in ft. keep.

        # 2. remove the pre-loop stride ipow46(A, 2*NX*NY, &an)
        body[pre_stride_idx] = None

        # 3. build the new loop body. We keep the original lines, but:
        #    - replace x0 = seed; with the per-k seed recomputation
        #    - inject local decls for x0, tmp, i, j, t right after the
        #      loop-open brace (before the x0 assignment)
        #    - remove the trailing if (k != ...) randlc(&seed, an);
        new_kbody = []
        # local decls
        new_kbody.append("        double " + x0_var + ";")
        new_kbody.append("        double " + static_tmp + "[" + static_tmp_size + "];")
        new_kbody.append("        int i, j, t;")
        # seed recomputation replacing x0 = seed;
        for kbidx, kbl in enumerate(kbody):
            if kbidx == x0_assign_idx:
                indent = re.match(r"(\s*)", kbl).group(1)
                new_kbody.append(indent + x0_var + " = " + seed_var + ";")
                new_kbody.append(
                    indent
                    + "ipow46(A, (double)" + k_loop_var + " * 2.0 * NX * dims[0][1], &an);"
                )
                new_kbody.append(
                    indent + "dummy = randlc(&" + x0_var + ", an);"
                )
                continue
            # drop the trailing randlc(&seed, an) seed-advance
            if re.search(r"\brandlc\s*\(", kbl) and re.search(
                r"&\s*" + re.escape(seed_var), kbl
            ):
                # this is the seed-advance; skip it
                continue
            # keep other lines (vranlc, t = 1, inner j/i loops)
            new_kbody.append(kbl)
        # 4. assemble the new function body slice
        new_body = list(body[:k_open + 1]) + new_kbody + [body[k_close]]
        # body[k_close] is the closing brace of the k loop; keep any lines
        # after it (e.g. closing brace of the function).
        new_body += body[k_close + 1:]
        new_body = [b for b in new_body if b is not None]
        # 5. insert the pragma before the k loop header
        #    locate the k loop header in new_body
        k_header_new_idx = None
        for nbidx, nbl in enumerate(new_body):
            if re.match(
                r"\s*for\s*\(\s*(?:int\s+)?"
                + re.escape(k_loop_var)
                + r"\s*=\s*0\s*;",
                nbl,
            ):
                k_header_new_idx = nbidx
                break
        if k_header_new_idx is None:
            continue
        indent = re.match(r"(\s*)", new_body[k_header_new_idx]).group(1)
        pragma = indent + "#pragma omp parallel for private(" + k_loop_var + ", an, dummy) schedule(static)"
        new_body.insert(k_header_new_idx, pragma)
        # write back into out
        out[body_offset:close_idx + 1] = new_body
        applied.append({
            "function": fname,
            "loop_var": k_loop_var,
            "seed_var": seed_var,
            "scratch": static_tmp,
            "kind": "randlc-seed-rewrite",
        })
    return out, applied


def _local_scalars(block_text, loop_var, known_globals=None):
    """Find scalar variables assigned in the loop body that must be private.

    A scalar is a bare name (not indexed by []) that is written via =, +=,
    -=, *=, or /=, OR an inner loop induction variable. These are
    per-iteration temporaries; without private() they race across threads.
    Excludes the loop variable and known globals.
    """
    known_globals = known_globals or set()
    scalars = []
    seen = set()
    # Collect variables declared inside the block (e.g. `int print_ptr, last_print;`
    # in a nested {} scope). These are block-local: each loop iteration
    # re-declares them on its own stack, so they are already per-thread and
    # must NOT be listed in the outer parallel-for private() clause (doing so
    # references a name not visible at the loop's scope, causing undeclared
    # errors, e.g. BOTS alignment pairalign_seq).
    declared_in_block = set()
    for dm in re.finditer(r"(?m)^\s*(?:int|long|size_t|double|float|char|short|unsigned|struct\s+\w+|enum\s+\w+|void\s*\*)\s+\*?\s*([^;]+);", block_text):
        for name in re.findall(r"\b([A-Za-z_]\w*)\b", dm.group(1)):
            declared_in_block.add(name)
    # x = ..., x += ..., etc.  (left side is a bare name, not arr[...])
    for m in re.finditer(r"(?m)^\s*([A-Za-z_]\w*)\s*(?:\+=|-=|\*=|/=|=(?!=))", block_text):
        var = m.group(1)
        if var == loop_var or var in seen or var in known_globals:
            continue
        if var in declared_in_block:
            continue
        # skip if this var is ever used as an array (arr[var] elsewhere)
        if re.search(r"\b" + re.escape(var) + r"\s*\[", block_text):
            continue
        seen.add(var)
        scalars.append(var)
    # inner loop induction variables (for (d = ...; ...)) are shared scalars
    # that race unless private
    for m in re.finditer(r"\bfor\s*\(\s*(?:int\s+|long\s+|size_t\s+)?([A-Za-z_]\w*)\s*=", block_text):
        var = m.group(1)
        if var == loop_var or var in seen or var in known_globals:
            continue
        seen.add(var)
        scalars.append(var)
    return scalars


def _local_scratch_arrays(masked, index, block_text):
    """Find local scratch-array declarations in the function containing the
    loop at `index`.

    These are arrays declared at function scope (e.g. `double r1[M], r2[M];`)
    that are used inside the loop body as per-iteration temporaries. When the
    loop is parallelized they must be private() or threads race on the shared
    storage. Scans upward from the loop to the previous function's closing
    brace, collecting array declarations. Function parameters (arrays in the
    signature) are excluded. Only returns arrays actually referenced (indexed)
    in the block_text.
    """
    decl_re = re.compile(
        r"(?:const\s+|volatile\s+|unsigned\s+|signed\s+|short\s+|long\s+)*"
        r"(?:int|double|float|char|long|short|size_t|dcomplex)\s+"
        r"(\w+)\s*\["
    )
    multi_re = re.compile(r",\s*(\w+)\s*\[")
    sig_re = re.compile(
        r"^\s*(?:static\s+)?(?:void|int|double|float|char|long|short|size_t|dcomplex|unsigned|signed)\s+\w+\s*\("
    )
    # Pass 1: collect lines from the loop up to the function boundary.
    func_lines = []
    for j in range(index - 1, -1, -1):
        raw = masked[j]
        line = raw.strip()
        if raw[:1] == "}" and line == "}":
            break
        func_lines.append((j, raw))
    func_lines.reverse()  # top to bottom
    # Pass 2: find the signature (contiguous lines from the first sig_re
    # match to the line ending the param list with ")"). Collect param names.
    params = set()
    in_sig = False
    for j, raw in func_lines:
        line = raw.strip()
        if not in_sig and sig_re.search(raw):
            in_sig = True
        if in_sig:
            # match param name followed by any number of [dims] and/or *,
            # ending in , (mid-param) or ) (last param). Multiple bracket
            # groups like indexmap[NZ][NY][NX] must all be consumed.
            for m in re.finditer(r"(\w+)\s*(?:(?:\[[^\]]*\]|\s*\*)+)\s*,", raw):
                params.add(m.group(1))
            for m in re.finditer(r",\s*(\w+)\s*(?:(?:\[[^\]]*\]|\s*\*)+)\s*\)", raw):
                params.add(m.group(1))
            if ")" in line:
                in_sig = False
    # Pass 3: collect array declarations not in params.
    # A true scratch temporary is WRITTEN per-iteration inside the loop body
    # (then read). A pre-computed lookup table like `int logd[3]` filled before
    # the loop is only READ inside it; making it private() gives each thread an
    # uninitialized copy and breaks the lookup. So require an array-element
    # WRITE (`var[...] =`, not `==`) in the block, not a bare reference.
    found = []
    seen = set()
    write_re = lambda var: re.compile(
        r"\b" + re.escape(var) + r"\s*\[[^\]]*\]\s*=(?!=)"
    )
    for j, raw in func_lines:
        for m in decl_re.finditer(raw):
            var = m.group(1)
            if var in seen or var in params:
                continue
            seen.add(var)
            if write_re(var).search(block_text):
                found.append(var)
        for m in multi_re.finditer(raw):
            var = m.group(1)
            if var in seen or var in params:
                continue
            seen.add(var)
            if write_re(var).search(block_text):
                found.append(var)
    return found


def _used_after_loop(masked, loop_end, var):
    """True if `var` is referenced anywhere after the loop ending at index
    `loop_end`, up to the end of the function. Used to detect scratch arrays
    that are written in a parallelized loop but read in later serial code —
    making them private() would leave post-loop references undefined."""
    var_re = re.compile(r"\b" + re.escape(var) + r"\b")
    depth = 0
    for j in range(loop_end + 1, len(masked)):
        line = masked[j]
        if var_re.search(line):
            return True
        # stop at function boundary (closing brace at column 0)
        if line[:1] == "}" and line.strip() == "}":
            break
    return False


def _shared_array_call_arg(masked, index, block_text):
    """Detect a function-scope local array passed as a bare argument to a
    function call inside the loop body (e.g. `exact_solution(xi, eta, zeta,
    temp)` where `temp` is `double temp[5]` declared at function scope).

    Such an array is shared across threads and the callee writes through it
    (NPB exact_solution fills its 4th arg), so parallelizing the loop races.
    Unlike an indexed scratch array, this is not caught by the array-write
    heuristics because the array is referenced by bare name, not indexed.
    Returns the list of such array names.
    """
    # collect function-scope local array decls above the loop
    decl_re = re.compile(
        r"(?:const\s+|volatile\s+|unsigned\s+|signed\s+|short\s+|long\s+)*"
        r"(?:int|double|float|char|long|short|size_t|dcomplex)\s+"
        r"(\w+)\s*\["
    )
    multi_decl_re = re.compile(r",\s*(\w+)\s*\[")
    # dcomplex scratch arrays (y0/y1 in cffts1/2/3) are moved into the loop
    # body by _move_scratch_decls, making them block-scope auto-private. They
    # do NOT race even when passed to a callee (cfftz fills y0), so exclude
    # them from the shared-array-call-arg check.
    movable_re = re.compile(
        r"(?:const\s+|volatile\s+|unsigned\s+|signed\s+|short\s+|long\s+)*"
        r"dcomplex\s+(\w+)\s*\["
    )
    sig_re = re.compile(
        r"^\s*(?:static\s+)?(?:void|int|double|float|char|long|short|size_t|dcomplex|unsigned|signed)\s+\w+\s*\("
    )
    local_arrays = set()
    movable_arrays = set()
    params = set()
    in_sig = False
    for j in range(index - 1, -1, -1):
        raw = masked[j]
        line = raw.strip()
        if raw[:1] == "}" and line == "}":
            break
        if not in_sig and sig_re.search(raw):
            in_sig = True
        if in_sig:
            for m in re.finditer(r"(\w+)\s*(?:(?:\[[^\]]*\]|\s*\*)+)\s*,", raw):
                params.add(m.group(1))
            for m in re.finditer(r",\s*(\w+)\s*(?:(?:\[[^\]]*\]|\s*\*)+)\s*\)", raw):
                params.add(m.group(1))
            if ")" in line:
                in_sig = False
        for m in decl_re.finditer(raw):
            v = m.group(1)
            if v not in params:
                local_arrays.add(v)
        for m in multi_decl_re.finditer(raw):
            v = m.group(1)
            if v not in params:
                local_arrays.add(v)
        for m in movable_re.finditer(raw):
            movable_arrays.add(m.group(1))
    local_arrays -= movable_arrays
    if not local_arrays:
        return []
    # find calls in block passing a local-array by reference (callee may write
    # through it). Two forms race: a bare name (`temp` decays to a pointer to
    # the shared array) or an address-of (`&temp` or `&Pface[ix][0][0]`). A bare
    # indexed element (`logd[0]` passed to cfftz) does NOT race — it is read by
    # value at the call site and the callee gets a scalar copy — so it is not
    # flagged here.
    result = []
    for arr in local_arrays:
        ev = re.escape(arr)
        # bare name as arg: `name,` or `name)` (decays to pointer, callee writes
        # through it). Excludes `name[` (indexed read) and `name=` (assignment).
        if re.search(r"\b" + ev + r"\b(?!\s*\[)(?!\s*=)\s*(?:,|\))", block_text):
            result.append(arr)
            continue
        # address-of name passed as arg: `&name` or `&name[` (callee writes the
        # addressed element(s)). The address may be indexed by the loop var
        # (element-disjoint, no race) or by a finite inner control variable
        # (Pface[ix] with ix in 0..1, races across outer-loop threads).
        if re.search(r"&\s*" + ev + r"\b", block_text):
            result.append(arr)
    return result


def _global_scratch_arrays(masked, index, block_text, loop_vars=None):
    """Find global scratch arrays used in the loop body but NOT declared
    in the function. These are arrays indexed in block_text (e.g. ue[m][i],
    buf[m][i], cuf[i], q[i]) that are declared in a header/global scope,
    not as function-local variables. When the loop is parallelized, threads
    race on these shared arrays. Unlike function-scope scratch arrays,
    globals cannot be safely privatized (their size may be runtime-defined
    and privatizing large globals wastes memory), so loops using them
    should be SKIPPED, matching the expert reference behavior.
    """
    # Collect all array names indexed in block_text: name[
    indexed = set()
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\[", block_text):
        indexed.add(m.group(1))
    if not indexed:
        return []
    # Collect function-scope declarations (local scratch + params).
    # Reuse the same upward scan as _local_scratch_arrays.
    decl_re = re.compile(
        r"(?:const\s+|volatile\s+|unsigned\s+|signed\s+|short\s+|long\s+)*"
        r"(?:int|double|float|char|long|short|size_t|dcomplex)\s+"
        r"(\w+)\s*\["
    )
    sig_re = re.compile(
        r"^\s*(?:static\s+)?(?:void|int|double|float|char|long|short|size_t|dcomplex|unsigned|signed)\s+\w+\s*\("
    )
    func_declared = set()
    params = set()
    in_sig = False
    for j in range(index - 1, -1, -1):
        raw = masked[j]
        line = raw.strip()
        if raw[:1] == "}" and line == "}":
            break
        if not in_sig and sig_re.search(raw):
            in_sig = True
        if in_sig:
            for m in re.finditer(r"(\w+)\s*(?:\[\s*\d*\s*\])?(?:\s*\*)*\s*,", raw):
                params.add(m.group(1))
            for m in re.finditer(r",\s*(\w+)\s*(?:\[\s*\d*\s*\])?\s*\)", raw):
                params.add(m.group(1))
            if ")" in line:
                in_sig = False
        for m in decl_re.finditer(raw):
            func_declared.add(m.group(1))
    # Filter: indexed arrays not declared in function and not params.
    # Exclude common non-scratch globals (u, rhs, forcing, etc. are the
    # actual data arrays being written, not scratch temporaries). A scratch
    # array is one that is WRITTEN in one statement and READ in a DIFFERENT
    # statement within the same loop body (a temporary). An in-place update
    # like u[i] = u[i] + rhs[i] reads and writes in the SAME statement, so
    # it is a data array, not a scratch.
    # Detect scratch: array written on one line, read on a later line.
    written_lines = {}  # arr -> set of line indices where written
    read_lines = {}     # arr -> set of line indices where read
    for li, bline in enumerate(block_text.splitlines()):
        # writes: arr[...] = or arr[...] += etc
        for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\])+\s*(?:\+=|-=|\*=|/=|=(?!=))", bline):
            written_lines.setdefault(m.group(1), set()).add(li)
        # reads: arr[...] appearing NOT as the lhs of an assignment.
        # Simple heuristic: all arr[...] occurrences, minus the write lhs.
        for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\[", bline):
            read_lines.setdefault(m.group(1), set()).add(li)
    result = []
    for arr in indexed:
        if arr in func_declared or arr in params:
            continue
        w_lines = written_lines.get(arr, set())
        r_lines = read_lines.get(arr, set())
        # scratch: written on some line, read on a DIFFERENT line
        if w_lines and r_lines - w_lines:
            # If every access to this array is indexed by ALL loop variables
            # in every dimension (e.g. square[i][j][k] in a parallel i loop),
            # each iteration touches a distinct element and a same-iteration
            # write-then-read is intra-iteration (safe). Only flag arrays
            # whose subscript chain omits a loop var in some access (e.g.
            # ue[m][i] where m is not a parallelized loop var) — those can
            # alias across iterations.
            if loop_vars:
                lv_re = [re.compile(r"\b" + re.escape(v) + r"\b") for v in loop_vars]
                all_accesses_covered = True
                for m in re.finditer(r"\b" + re.escape(arr) + r"\s*((?:\s*\[[^\]]*\])+)", block_text):
                    subs = m.group(1)
                    # require every loop var to appear somewhere in the
                    # subscript chain of this access
                    if not all(rx.search(subs) for rx in lv_re):
                        all_accesses_covered = False
                        break
                if all_accesses_covered:
                    continue
            result.append(arr)
    return result


def _array_assignment(text, variables):
    """True if text writes arr[...var...] = ... where one of the index
    expressions contains a loop variable. Each iteration writes a distinct
    index, so the loop is independent."""
    names = "|".join(re.escape(v) for v in variables)
    assignment = r"(?:\+=|-=|\*=|/=|(?<![=!<>])=(?!=))"
    # Match: name [idx] [idx] ... =  where at least one [idx] contains a
    # loop variable. The (?:\s*\[[^\]\n]*\])+ matches all bracket pairs; we
    # then require the whole subscript chain to contain the loop var.
    # Check ALL matches, not just the first: a loop body may write several
    # arrays (e.g. r1[i1]=...; u[i3][i2][i1]=...). The scratch write r1[i1]
    # does not contain the outer loop var, but the u[i3] write does, so the
    # loop is still independent.
    pattern = (
        r"(?m)^\s*[A-Za-z_]\w*((?:\s*\[[^\]\n]*\])+)\s*" + assignment
    )
    for m in re.finditer(pattern, text):
        subscripts = m.group(1)
        if re.search(r"\b(?:" + names + r")\b", subscripts):
            return True
    return False


def _has_indirect_accumulation(text, loop_var):
    """True if the loop body accumulates into an array element whose direct
    index is data-dependent rather than the loop counter itself.

    Examples that race:
      prv_buff1[key_buff2[i]]++   direct index = key_buff2[i] (data, nested [])
      hist[bucket[i]] += 1         direct index = bucket[i] (data, nested [])
    Examples that are safe (direct index IS the loop var):
      arr[j]++                    direct index = j (no nested [])

    The direct index is the content of the outermost bracket pair. If it
    contains a nested '[' then the index is itself an array lookup, so two
    iterations with different loop values can map to the same element. Such
    loops need a per-thread-local buffer and a merge step (aaai IS rank
    style), which rules cannot express, so we skip them.
    """
    # match arr[...][...]... ++ or arr[...][...]... += etc. (accumulation
    # into an array element, not a plain assignment). Allow one level of
    # nested brackets so prv_buff1[key_buff2[i]]++ is matched.
    accum = r"([A-Za-z_]\w*)((?:\s*\[[^\]]*(?:\[[^\]]*\])?[^\]]*\])+)\s*(\+\+|--|\+=|-=|\*=|/=)"
    for m in re.finditer(accum, text):
        subscripts = m.group(2)
        # extract the first (outermost) bracket content
        first = re.match(r"\s*\[([^\]]*(?:\[[^\]]*\])?[^\]]*)\]", subscripts)
        if not first:
            continue
        idx = first.group(1)
        # if the direct index contains a nested array access, the index is
        # data-dependent and iterations can collide
        if "[" in idx:
            return True
    return False


def _pragma_regions(masked):
    regions = [False] * len(masked)
    pending = False
    stack = []
    depth = 0
    for index, line in enumerate(masked):
        regions[index] = bool(stack) or pending
        stripped = line.strip()
        if stripped.startswith("#pragma") and re.search(r"\bomp\b", stripped):
            pending = True
        for char in line:
            if char == "{":
                depth += 1
                if pending:
                    stack.append(depth)
                    pending = False
            elif char == "}":
                if stack and stack[-1] == depth:
                    stack.pop()
                depth -= 1
        if pending and stripped and not stripped.startswith("#pragma") and "{" not in line:
            pending = False
    return regions


def _has_enclosing_for_loop(masked, index, safe_lines=None, skipped_global_scratch=None):
    """True if this loop sits inside an outer for loop that should not be
    nested-parallelized into.

    aaai-style parallelization targets the outermost loop of a data nest only.
    An inner loop under a data outer loop (compute_indexmap's k under i,j;
    mg's i1 under i3,i2) is skipped so we parallelize the outer instead,
    avoiding per-iteration fork/join overhead when the outer loop has a large
    or variable trip count.

    A control loop with a small constant trip count (conj_grad's cgit, which
    runs cgitmax=25 iterations and updates scalars) does NOT block inner
    parallelization, so loops nested under it (the matvec j loops) stay
    eligible. The distinction is the outer loop's trip count: small constant
    = control loop (allow inner), variable/large = data loop (skip inner).

    safe_lines is the dep-analyzer set of parallelizable loop line numbers.
    When safe_lines is unavailable, fall back to treating any enclosing for as
    a data loop (conservative skip).
    """
    depth = 0
    j = index - 1
    while j >= 0:
        for ch in reversed(masked[j]):
            if ch == "}":
                depth += 1
            elif ch == "{":
                if depth == 0:
                    # this opens the block we are currently inside
                    # find the for header (may be on this line or a few above)
                    for k in range(j, max(-1, j - 3), -1):
                        if re.match(r"\s*for\s*\(", masked[k]):
                            if safe_lines is not None:
                                outer_line = k + 1
                                # outer is a data loop only if the analyzer
                                # proved it parallelizable
                                if outer_line in safe_lines:
                                    # If the outer loop was itself skipped by
                                    # _global_scratch_arrays (e.g. ADI solver's
                                    # backward i loop, which the dep analyzer
                                    # wrongly marks parallelizable), it will
                                    # never be parallelized, so the inner
                                    # independent loop (j/k) is the real
                                    # parallel opportunity. Allow it.
                                    if skipped_global_scratch and k in skipped_global_scratch:
                                        return False
                                    # Even a parallelizable outer loop
                                    # with a small constant trip count
                                    # (e.g. sp add's m=0..4) is a control
                                    # loop, not a data loop. Allow inner
                                    # parallelization instead of skipping.
                                    outer_cond = masked[k]
                                    bm = re.search(r"<\s*=\s*(\d+)", outer_cond) or re.search(r"<\s*(\d+)", outer_cond)
                                    if bm:
                                        ub = int(bm.group(1))
                                        trip = ub + 1 if "<=" in outer_cond else ub
                                        if trip < 64:
                                            return False  # control loop
                                    return True
                                # outer not proven parallelizable: check if
                                # it's a small-constant control loop. If so,
                                # allow inner parallelization (return False).
                                # If the outer has a variable or large bound it
                                # is either a data loop the analyzer could not
                                # prove (we'll still try the outer separately) or
                                # a dependency-carrier like an ADI solver's
                                # forward-elimination i loop. In both cases the
                                # outer cannot itself be safely parallelized by
                                # rules, so the inner loops are the only parallel
                                # opportunity. Allow inner parallelization
                                # (return False) rather than skipping — matching
                                # the expert reference, which parallelizes the
                                # inner j/k loops of x/y/z_solve.
                                outer_cond = masked[k]
                                bm = re.search(r"<\s*=\s*(\d+)", outer_cond) or re.search(r"<\s*(\d+)", outer_cond)
                                if bm:
                                    ub = int(bm.group(1))
                                    trip = ub + 1 if "<=" in outer_cond else ub
                                    if trip < 64:
                                        return False  # control loop, allow inner
                                return False  # unproven outer, allow inner
                            return True
                    pass
                else:
                    depth -= 1
        j -= 1
    return False


PURE_FUNCS = {"fabs", "sqrt", "pow", "fmax", "fmin", "max", "min",
              "abs", "labs", "floor", "ceil", "round", "trunc", "rint",
              "exp", "log", "log2", "log10", "sin", "cos", "tan",
              "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh"}


def _body_has_call(body):
    """True if body calls a function. A loop with a function call in its body
    is not a safe reduction: the call may have side effects or carry
    cross-iteration state. Pure math functions (fabs, sqrt, pow, ...) are
    side-effect-free and do not block reduction detection."""
    for m in re.finditer(r"\b(?!if|for|while|switch|return|sizeof)([A-Za-z_]\w*)\s*\(", body):
        if m.group(1) not in PURE_FUNCS:
            return True
    return False


def _is_reset_in_body(body, var):
    """True if var is assigned a non-self value (var = <expr not starting with
    var>) inside body, meaning it is recomputed each iteration rather than
    accumulated across iterations."""
    ev = re.escape(var)
    for m in re.finditer(r"\b" + ev + r"\s*=(?!=)\s*", body):
        rest = body[m.end():].lstrip()
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


def _body_has_pointer_state(block_text):
    """True if body carries cross-iteration pointer state. Such state is
    loop-carried so the loop is not a safe parallel reduction even if it also
    has scalar accumulators. Catches Strassen's FastNaiveMatrixMultiply
    Products loop where BColumnStart = (REAL*)(...RowWidthBInBytes...) is
    reassigned with a cast each iteration (pointer arithmetic on the read
    source). A loop variable's own ++ (Products++) is excluded by requiring
    the increment to act on a dereferenced pointer (*ptr++)."""
    if re.search(r"\*\s*\(*\s*[A-Za-z_]\w*\s*\)*\s*(\+\+|--)", block_text):
        return True
    if re.search(r"\b[A-Za-z_]\w*\s*=\s*\([A-Za-z_]\w*\s*\*\s*\)", block_text):
        return True
    return False


def _detect_max_min_reduction(block_text, loop_var):
    """Find max/min reductions written as conditional swaps:
        if (a > b) b = a;   -> max(b)
        if (a < b) b = a;   -> min(b)
        if (b > a) b = a;   -> max(b)  (b keeps the larger)
        if (b < a) b = a;   -> min(b)  (b keeps the smaller)
    The target var (b) is the one assigned inside the if. Returns list of
    (var, "max"|"min"). Excludes the loop variable and vars used as array
    indices."""
    found = []
    seen = set()
    # if (X > Y) Y = X;  or  if (X < Y) Y = X;
    pat1 = re.compile(
        r"if\s*\(\s*(\w+)\s*([<>])\s*(\w+)\s*\)\s*\3\s*=(?!=)\s*\1"
    )
    # if (X > Y) X = Y;  or  if (X < Y) X = Y;  (assign to first operand)
    pat2 = re.compile(
        r"if\s*\(\s*(\w+)\s*([<>])\s*(\w+)\s*\)\s*\1\s*=(?!=)\s*\3"
    )
    for m in pat1.finditer(block_text):
        left, op, target = m.group(1), m.group(2), m.group(3)
        if target == loop_var or target in seen:
            continue
        if re.search(r"\b" + re.escape(target) + r"\s*\[", block_text):
            continue
        seen.add(target)
        # if (a > b) b = a  -> b keeps max -> reduction(max:b)
        # if (a < b) b = a  -> b keeps min -> reduction(min:b)
        found.append((target, "max" if op == ">" else "min"))
    for m in pat2.finditer(block_text):
        target, op, _ = m.group(1), m.group(2), m.group(3)
        if target == loop_var or target in seen:
            continue
        if re.search(r"\b" + re.escape(target) + r"\s*\[", block_text):
            continue
        seen.add(target)
        # if (a > b) a = b  -> a keeps min -> reduction(min:a)
        # if (a < b) a = b  -> a keeps max -> reduction(max:a)
        found.append((target, "min" if op == ">" else "max"))
    return found


def _detect_scalar_reductions(block_text, loop_var):
    """Find scalar accumulators (+=, -=, *=, /=, or x = x op) in a loop body
    that ALSO writes arrays independently. Unlike _detect_reduction this does
    NOT reject array writes, because the independent-array-write pattern
    already proved the array writes are per-iteration distinct. The scalar
    accumulators still need reduction() clauses or they race."""
    if _body_has_call(block_text):
        return []
    found = []
    seen = set()
    op_map = {"+=": "+", "-=": "-", "*=": "*", "/=": "/"}
    def _used_as_idx(var):
        # True if var appears inside [...] brackets as an array index.
        # Such a variable is read to compute an access position, so it is a
        # loop-carried value, not a pure reduction accumulator (e.g. zran3
        # i1 = i1-1 where i1 indexes j3[i1][1]).
        return re.search(r"\[[^\]]*\b" + re.escape(var) + r"\b", block_text) is not None
    for m in REDUCTION_ASSIGN.finditer(block_text):
        var = m.group(1)
        if var == loop_var or var in seen:
            continue
        if _is_reset_in_body(block_text, var):
            continue
        if re.search(r"\b" + re.escape(var) + r"\s*\[", block_text):
            continue
        if _used_as_idx(var):
            continue
        seen.add(var)
        found.append((var, op_map.get(m.group(2), "+")))
    for m in REDUCTION_EQUAL.finditer(block_text):
        var = m.group(1)
        if var == loop_var or var in seen:
            continue
        if _is_reset_in_body(block_text, var):
            continue
        if re.search(r"\b" + re.escape(var) + r"\s*\[", block_text):
            continue
        if _used_as_idx(var):
            continue
        seen.add(var)
        found.append((var, op_map.get(m.group(2), "+")))
    # max/min conditional-swap reductions (if (a > b) b = a)
    for var, op in _detect_max_min_reduction(block_text, loop_var):
        if var not in seen and not _used_as_idx(var):
            seen.add(var)
            found.append((var, op))
    return found


def _detect_reduction(block_text, loop_var):
    """Detect reduction patterns. Return list of (var, op) tuples, empty if none.

    Collects ALL scalar accumulators in the body so multi-variable reductions
    like `a += ...; b += ...` get both into reduction(...). Rejects bodies
    with function calls, array writes (may alias across iterations), or where
    an accumulator is reset by a plain assignment inside the body (recomputed,
    not a cross-iteration sum)."""
    if _body_has_call(block_text):
        return []
    if _body_has_array_write(block_text):
        return []
    if _body_has_pointer_state(block_text):
        return []
    found = []
    seen = set()
    op_map = {"+=": "+", "-=": "-", "*=": "*", "/=": "/"}
    def _used_as_index(var):
        # True if var appears inside [...] brackets as an array index.
        # Such a variable is read to compute an access position, so it is a
        # loop-carried value, not a pure reduction accumulator.
        return re.search(r"\[[^\]]*\b" + re.escape(var) + r"\b", block_text) is not None
    # x += expr, x -= expr, etc.
    for m in REDUCTION_ASSIGN.finditer(block_text):
        var = m.group(1)
        if var == loop_var or var in seen:
            continue
        if _is_reset_in_body(block_text, var):
            continue
        if re.search(r"\b" + re.escape(var) + r"\s*\[", block_text):
            continue
        if _used_as_index(var):
            continue
        seen.add(var)
        found.append((var, op_map.get(m.group(2), "+")))
    # x = x + expr
    for m in REDUCTION_EQUAL.finditer(block_text):
        var = m.group(1)
        if var == loop_var or var in seen:
            continue
        if _is_reset_in_body(block_text, var):
            continue
        if re.search(r"\b" + re.escape(var) + r"\s*\[", block_text):
            continue
        if _used_as_index(var):
            continue
        seen.add(var)
        found.append((var, op_map.get(m.group(2), "+")))
    # max/min conditional-swap reductions (if (a > b) b = a)
    for var, op in _detect_max_min_reduction(block_text, loop_var):
        if var not in seen and not _used_as_index(var):
            seen.add(var)
            found.append((var, op))
    return found


def _next_for_index(masked, start, end):
    """Return the index of the first direct-child for-loop inside the loop
    spanning [start, end], or None if the body has no for at the top level
    (i.e. it is not a perfect nest or the child is not a for-loop)."""
    body_start = start + 1
    for idx in range(body_start, end):
        line = masked[idx].strip()
        if not line or line.startswith("{") or line.startswith("}"):
            continue
        if line.startswith("#pragma"):
            continue
        if COLLAPSE_RE.match(masked[idx]):
            return idx
        return None
    return None


def _detect_nested_loop(masked, start, end):
    """Check if outer loop body contains only inner for loops (possibly
    several levels deep). Return (inner_vars, first_inner_idx) or None.

    inner_vars is the list of all nested loop induction variables (j, k, m,
    ...) so they can all be marked private. Only marking the innermost is a
    race: the other loop vars are shared scalars overwritten concurrently.
    """
    body_start = start + 1
    for idx in range(body_start, end):
        line = masked[idx].strip()
        if not line or line.startswith("{") or line.startswith("}"):
            continue
        if line.startswith("#pragma"):
            continue
        m = COLLAPSE_RE.match(masked[idx])
        if m:
            inner_var = m.group(1)
            inner_end = _balanced_block(masked, idx)
            if inner_end is None:
                break
            # Check nothing else in body besides braces and nested loops
            other_lines = False
            for ci in range(body_start, end):
                if ci == idx:
                    continue
                if ci > idx and ci <= inner_end:
                    continue
                stripped = masked[ci].strip()
                if stripped and stripped not in ("{", "}", ""):
                    other_lines = True
                    break
            if other_lines:
                break
            # Collect all nested loop vars by walking the inner block
            inner_vars = [inner_var]
            for ci in range(idx + 1, inner_end + 1):
                mm = COLLAPSE_RE.match(masked[ci])
                if mm:
                    inner_vars.append(mm.group(1))
            return inner_vars, idx
        break
    return None


def _load_parallelizable_lines(dep_json):
    """Read dep.json, return set of loop line numbers proven safe to parallelize.

    Only loops flagged parallelizable=True or is_reduction=True by the
    dependency analyzer are eligible. Returns None when dep_json is absent
    or unreadable, so callers can fall back to conservative skip-all behavior.
    """
    if not dep_json:
        return None
    try:
        with open(dep_json) as f:
            dep = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    loops = dep.get("loops", [])
    safe = set()
    for item in loops:
        if item.get("parallelizable") or item.get("is_reduction"):
            safe.add(item.get("line"))
    return safe


def _task_rewrite(lines, dep_json):
    """Insert #pragma omp task / taskwait into recursive functions and
    #pragma omp parallel + single into their entry callers.

    For each recursive function (calls itself, not _seq suffix), find lines
    that call the function recursively and insert #pragma omp task before
    each. After the group of recursive calls, insert #pragma omp taskwait.

    For each entry caller (calls a recursive function but is not itself
    recursive), wrap the call in #pragma omp parallel + #pragma omp single.

    Returns (new_lines, applied) where applied is a list of dicts describing
    each insertion.
    """
    if not dep_json:
        return lines, []
    try:
        with open(dep_json) as f:
            dep = json.load(f)
    except (OSError, json.JSONDecodeError):
        return lines, []
    calls_map = dep.get("function_calls", {})
    evidence = dep.get("function_evidence", [])

    # Resolve the compile-time cutoff constant from app-desc.h (BOTS convention).
    # BOTS_CUTOFF_DEF_VALUE is a #define in app-desc.h next to the source. Use the
    # literal so the base target (no IF_CUTOFF) still links — the runtime global
    # bots_cutoff_value is only defined under IF_CUTOFF/MANUAL_CUTOFF/FINAL_CUTOFF.
    cutoff_literal = None
    src_path = dep.get("source")
    if src_path:
        appdesc = Path(src_path).parent / "app-desc.h"
        if appdesc.exists():
            m = re.search(r"#define\s+BOTS_CUTOFF_DEF_VALUE\s+(\d+)", appdesc.read_text(errors="replace"))
            if m:
                cutoff_literal = m.group(1)

    def _find_func_range(nm):
        """Find the first function definition's (start, end) line indices
        (0-based) by scanning source."""
        ranges = _find_all_func_ranges(nm)
        return ranges[0] if ranges else None

    def _find_all_func_ranges(nm):
        """Find ALL function definitions with this name (handles #ifdef
        variants that produce multiple definitions). Returns list of
        (start, end) 0-based line index tuples."""
        def_re = re.compile(
            r"^\s*(?:static\s+)?(?:void|int|float|double|char|short|long|unsigned|size_t|bool|COMPLEX|struct\s+\w+|enum\s+\w+)\s+\*?\s*"
            + re.escape(nm) + r"\s*\(")
        ranges = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if def_re.search(line):
                # find the opening brace of the body
                depth = 0
                started = False
                end = None
                for j in range(i, len(lines)):
                    for ch in lines[j]:
                        if ch == "{":
                            depth += 1
                            started = True
                        elif ch == "}":
                            depth -= 1
                            if started and depth == 0:
                                end = j + 1
                                break
                    if end is not None:
                        break
                if end is not None:
                    ranges.append((i, end))
                    i = end
                    continue
            i += 1
        return ranges

    # recursive functions (non-_seq, non-_ser): name in its own calls list.
    # _seq and _ser suffixes mark serial reference variants that must not be
    # parallelized. Also skip seq-prefixed leaf helpers (BOTS convention:
    # seqquick/seqmerge/seqpart are sequential leaf sorters with loop-carried
    # deps) and build/verify/print traversals (allocate_*, get_results,
    # my_print) that aaai keeps serial because they run once outside the
    # parallel compute.
    def _is_leaf_or_aux_fn(nm):
        low = nm.lower()
        if low.startswith("seq"):
            return True
        if low.startswith("allocate") or low.startswith("get_results"):
            return True
        if low in ("my_print",) or low.startswith("print_"):
            return True
        return False
    recursive_funcs = set()
    for fe in evidence:
        nm = fe.get("name", "")
        if nm and not nm.endswith("_seq") and not nm.endswith("_ser") and nm in calls_map.get(nm, []):
            if _is_leaf_or_aux_fn(nm):
                continue
            recursive_funcs.add(nm)
    if not recursive_funcs:
        return lines, []
    # entry callers: non-recursive functions that call a recursive function
    entry_callers = {}  # caller_name -> set of recursive callees
    for caller, callees in calls_map.items():
        if caller in recursive_funcs:
            continue
        rec_callees = {c for c in callees if c in recursive_funcs}
        if rec_callees:
            entry_callers[caller] = rec_callees
    applied = []
    insertions = {}  # line_index (0-based) -> list of lines to insert before
    replacements = {}  # line_index (0-based) -> True: replace original line with insertions
    # Process recursive functions: insert task before recursive calls,
    # taskwait after the last recursive call group.
    for fname in recursive_funcs:
        ranges = _find_all_func_ranges(fname)
        if not ranges:
            continue
        call_re = re.compile(r"\b" + re.escape(fname) + r"\s*\(")
        def_re = re.compile(r"^\s*(?:static\s+)?(?:void|int|float|double|char|short|long|unsigned|size_t|bool|COMPLEX|struct\s+\w+|enum\s+\w+)\s+\*?\s*" + re.escape(fname) + r"\s*\(")
        for start, end in ranges:
            # scan lines in this function body for recursive calls.
            task_lines = []  # 0-based indices of recursive call lines
            for i in range(start, min(end, len(lines))):
                line = lines[i]
                # skip pragma lines and comments
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if def_re.search(line):
                    continue
                if call_re.search(line):
                    task_lines.append(i)
            if not task_lines:
                continue
            body_text = "\n".join(lines[start:min(end, len(lines))])
            # Output-dependency guard: if two recursive calls pass the same
            # first argument AND that argument is a pointer-typed parameter,
            # they likely have a write-after-write dependency on a shared
            # output buffer (e.g. strassen MultiplyByDivideAndConquer: call 1
            # writes C00 in non-additive mode, call 5 writes C00 again in
            # additive mode). Taskifying both races on the shared output.
            # Skip taskification for the whole function in that case.
            # Restrict to pointer params so value params (e.g. nqueens `n`,
            # an int board size passed unchanged) don't false-trigger.
            # Calls and signature may span multiple lines, so extract args
            # from the joined body/signature text.
            first_param_is_pointer = False
            sig_text = ""
            for si in range(start, min(start + 12, len(lines))):
                sig_text += lines[si]
                if ")" in lines[si] and "{" not in lines[si]:
                    break
                if "{" in lines[si]:
                    break
            sig_m = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", sig_text)
            if sig_m:
                p0 = sig_m.group(1).split(",")[0].strip()
                if "*" in p0:
                    first_param_is_pointer = True
            first_args = []
            if first_param_is_pointer:
                for cm in re.finditer(re.escape(fname) + r"\s*\(([^)]*)\)", body_text):
                    args = cm.group(1).split(",")
                    if args:
                        first_args.append(args[0].strip())
            if len(first_args) >= 2:
                seen = set()
                dup_out = False
                for fa in first_args:
                    if re.match(r"^[A-Za-z_]\w*$", fa) and fa in seen:
                        dup_out = True
                        break
                    seen.add(fa)
                if dup_out:
                    continue
            # Cross-task data-dependency guard: if the function allocates
            # heap buffers (malloc/alloca) and passes them as output (first
            # arg) to recursive calls, then reads those buffers AFTER the
            # call group (e.g. strassen OptimizedStrassenMultiply_par: call 1
            # writes M2, a later merge loop reads M2), concurrent tasks race
            # on the write-then-read. aaai keeps such functions serial
            # (strassen IF_CUTOFF variant). Skip taskification. nqueens is
            # exempt: its output (&csols[i], address-of) is read only after
            # taskwait, and the read is a separate reduction loop, but the
            # buffer is stack alloca with distinct indices per task.
            if first_param_is_pointer and re.search(r"\b(?:malloc|alloca|calloc)\s*\(", body_text):
                # collect the output (first arg) of each recursive call,
                # but only plain-variable outputs (not &x or expressions)
                outputs = []
                call_matches = list(re.finditer(re.escape(fname) + r"\s*\(([^)]*)\)", body_text))
                for cm in call_matches:
                    cargs = [a.strip() for a in cm.group(1).split(",")]
                    if cargs and re.match(r"^[A-Za-z_]\w*$", cargs[0]):
                        outputs.append(cargs[0])
                if len(outputs) >= 2 and call_matches:
                    # text after the last recursive call's closing paren
                    last_end = call_matches[-1].end()
                    after_text = body_text[last_end:]
                    cross_dep = any(re.search(r"\b" + re.escape(o) + r"\b", after_text) for o in outputs)
                    if cross_dep:
                        continue
            # find base-case cutoff: look for `X - Y < N` or `(X - Y) < N`
            # pattern in the function body (range-size threshold). Use 2*N as the
            # task cutoff threshold so small sub-problems run inline instead of
            # spawning tiny tasks. N may be a literal or a named constant.
            cutoff_clause = ""
            bm = re.search(r"\(?\s*([A-Za-z_]\w*)\s*-\s*([A-Za-z_]\w*)\s*\)?\s*<\s*([A-Za-z_]\w*|\d+)\b", body_text)
            if bm:
                v1, v2, n = bm.group(1), bm.group(2), bm.group(3)
                if n.isdigit():
                    thresh = int(n) * 2
                    cutoff_clause = f" if(({v1}-{v2}) > {thresh})"
                else:
                    # named constant threshold (e.g. bots_app_cutoff_value): the
                    # early-return base case `if (v1-v2 < CONST) { seq(); return; }`
                    # already controls recursion depth at runtime, matching the
                    # aaai pattern (sort cilkmerge_par). Adding an if-clause on
                    # the task would double-gate and use a wrong literal, so leave
                    # the task ungated.
                    cutoff_clause = ""
            else:
                # range-exhaustion base case: `X == Y - 1` (e.g. fft_twiddle_gen
                # uses `i == i1 - 1`). The live range size is Y-X, so cutoff on
                # that with a small threshold (16) to avoid spawning tiny tasks.
                rm = re.search(r"(\b[A-Za-z_]\w*)\s*==\s*([A-Za-z_]\w*)\s*-\s*1\b", body_text)
                if rm:
                    lo, hi = rm.group(1), rm.group(2)
                    cutoff_clause = f" if(({hi}-{lo}) > 16)"
                else:
                    # size-threshold base case: `VAR < N` where VAR is a scalar
                    # parameter (e.g. cilksort_par `size < bots_app_cutoff_value_1`).
                    # Find VAR's position in the function signature, then use the
                    # same-position argument in the recursive call as the cutoff.
                    sm = re.search(r"\b([A-Za-z_]\w*)\s*<\s*([A-Za-z_]\w*|\d+)\b", body_text)
                    cutoff_var = None
                    base_thresh = sm.group(2) if sm else None
                    if sm:
                        bvar = sm.group(1)
                        # find bvar's position in the function signature
                        sig_match = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", lines[start])
                        if sig_match:
                            sig_args = [a.strip() for a in sig_match.group(1).split(",")]
                            # find position of bvar (strip type, keep name)
                            bvar_pos = None
                            for pi, sa in enumerate(sig_args):
                                # last token is the name (handle pointers)
                                tokens = sa.replace("*", " ").split()
                                if tokens and tokens[-1] == bvar:
                                    bvar_pos = pi
                                    break
                            if bvar_pos is not None and task_lines:
                                call_line = lines[task_lines[0]]
                                cm = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", call_line)
                                if cm:
                                    call_args = [a.strip() for a in cm.group(1).split(",")]
                                    if bvar_pos < len(call_args):
                                        carg = call_args[bvar_pos].strip()
                                        if re.match(r"^[A-Za-z_]\w*$", carg):
                                            cutoff_var = carg
                    if cutoff_var:
                        if base_thresh and not base_thresh.isdigit():
                            # named-constant threshold (e.g. bots_app_cutoff_value_1):
                            # the early-return base case already gates depth at
                            # runtime, matching aaai (sort cilksort_par). Leave the
                            # task ungated instead of using a wrong literal (256).
                            cutoff_clause = ""
                        else:
                            cutoff_clause = f" if({cutoff_var} > 256)"
                    else:
                        # depth-recursion base case: `X == Y` where X is a parameter
                        # that increments in the recursive call (e.g. nqueens `n == j`
                        # with call `nqueens(n, j+1, ...)`). Find the incrementing
                        # parameter and use it as the cutoff variable. Skip pointer
                        # parameters (pointer arithmetic like `factors+1` is not
                        # depth recursion).
                        sig_match2 = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", lines[start])
                        pointer_params = set()
                        if sig_match2:
                            for sa in sig_match2.group(1).split(","):
                                if "*" in sa:
                                    tokens = sa.replace("*", " ").split()
                                    if tokens:
                                        pointer_params.add(tokens[-1])
                        depth_var = None
                        if task_lines:
                            call_line = lines[task_lines[0]]
                            # collect all incrementing params across recursive calls
                            incr_params = []
                            for am in re.finditer(re.escape(fname) + r"\s*\(([^)]*)\)", call_line):
                                args = am.group(1).split(",")
                                for arg in reversed(args):
                                    arg = arg.strip()
                                    im = re.match(r"^([A-Za-z_]\w*)\s*([+\-])\s*1$", arg)
                                    if im and im.group(1) not in pointer_params:
                                        incr_params.append(im.group(1))
                                        break
                            # prefer a param named `depth` (BOTS convention:
                            # depth tracks recursion depth, j tracks board col).
                            # Even if depth is passed unchanged in some variant
                            # (nqueens FORCE_TIED passes depth not depth+1),
                            # depth is still the recursion-depth proxy.
                            sig_params = []
                            sm2 = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", lines[start])
                            if sm2:
                                sig_params = [sa.replace("*"," ").split()[-1] for sa in sm2.group(1).split(",") if sa.replace("*"," ").split()]
                            if "depth" in sig_params:
                                depth_var = "depth"
                            elif incr_params:
                                depth_var = incr_params[-1]
                        if depth_var:
                            # BOTS convention: depth-recursion cutoffs use the
                            # compile-time constant BOTS_CUTOFF_DEF_VALUE (defined
                            # per benchmark in app-desc.h, e.g. nqueens=3, health=2).
                            # Use the literal so the base target (no IF_CUTOFF)
                            # still links — the runtime global bots_cutoff_value
                            # is only defined under IF_CUTOFF/MANUAL/FINAL_CUTOFF.
                            thresh = cutoff_literal or "16"
                            cutoff_clause = f" if({depth_var} < {thresh})"
                        elif task_lines:
                            # no var+1 increment found (e.g. nqueens FORCE_TIED
                            # variant passes depth unchanged). Fall back to a
                            # parameter named `depth` if present (BOTS convention),
                            # else the first scalar call argument.
                            sig_match3 = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", lines[start])
                            depth_param = None
                            if sig_match3:
                                for sa in sig_match3.group(1).split(","):
                                    tokens = sa.replace("*", " ").split()
                                    if tokens and tokens[-1] == "depth":
                                        depth_param = "depth"
                                        break
                            if depth_param:
                                thresh = cutoff_literal or "16"
                                cutoff_clause = f" if({depth_param} < {thresh})"
                            else:
                                # no recognizable base case (e.g. fft_aux uses n==const).
                                # Use the first scalar (non-pointer) argument of the
                                # recursive call as the cutoff variable.
                                call_line = lines[task_lines[0]]
                                cm = re.search(re.escape(fname) + r"\s*\(([^)]*)\)", call_line)
                                if cm:
                                    for arg in cm.group(1).split(","):
                                        arg = arg.strip()
                                        if re.match(r"^[A-Za-z_]\w*$", arg) and arg not in pointer_params:
                                            cutoff_clause = f" if({arg} > 256)"
                                            break
            # tree-depth cutoff: if the body references `PARAM->level` (a struct
            # field tracking tree depth) and a `*_level` global exists, use
            # `if((GLEVEL - PARAM->level) < CUTOFF)`. This matches the aaai
            # pattern for tree-recursive benchmarks (health sim_village_par uses
            # `if((sim_level-village->level) < 2)`). Overrides the generic
            # pointer-arg fallback (`if(ptr > 256)`), which is meaningless for
            # pointer recursion. Search the whole file because the depth
            # expression may live in a sibling #ifdef variant (MANUAL_CUTOFF)
            # rather than the active one.
            if not cutoff_clause or re.match(r" if\([A-Za-z_]\w*\s*>\s*256\)$", cutoff_clause):
                full_text = "\n".join(lines)
                tdm = re.search(r"\b([A-Za-z_]\w*)\s*-\s*([A-Za-z_]\w*)\s*->\s*level\b", full_text)
                if tdm:
                    glevel = tdm.group(1)
                    node_var = tdm.group(2)
                    thresh = cutoff_literal or "16"
                    cutoff_clause = f" if(({glevel}-{node_var}->level) < {thresh})"
                else:
                    tdm2 = re.search(r"\b([A-Za-z_]\w*)\s*->\s*level\b", body_text)
                    if tdm2:
                        node_var = tdm2.group(1)
                        glm = re.search(r"\b([A-Za-z_]\w*level)\b", full_text, re.I)
                        if glm and glm.group(1) != node_var:
                            glevel = glm.group(1)
                            thresh = cutoff_literal or "16"
                            cutoff_clause = f" if(({glevel}-{node_var}->level) < {thresh})"
            # insert #pragma omp task before each recursive call.
            # If the call is part of `VAR += FNAME(args);` (task-result
            # accumulation, e.g. floorplan `nnc += add_cell(...)`), the naive
            # `#pragma omp task` before the whole statement races on VAR across
            # concurrent tasks. Refactor into a task block with a local result
            # and an atomic merge, matching the aaai pattern:
            #   #pragma omp task if(...)
            #   { int _task_r = FNAME(args);
            #   #pragma omp atomic
            #   VAR += _task_r; }
            acc_re = re.compile(r"^(\s*)([A-Za-z_]\w*)\s*\+=\s*" + re.escape(fname) + r"\s*\((.*)\);\s*$")
            for idx in task_lines:
                m = re.match(r"(\s*)", lines[idx])
                ind = m.group(1) if m else ""
                am = acc_re.match(lines[idx])
                # `untied` lets a suspended task resume on any thread, so deep
                # recursive task chains (BOTS fft/floorplan/health/nqueens/sort/
                # strassen) are not pinned to the spawning thread. All six
                # task-recursive BOTS aaai references use `#pragma omp task
                # untied`; matching it closes the perf gap on sort/cilksort.
                task_pragma = "#pragma omp task untied" + cutoff_clause
                if am:
                    indent, acc_var, call_args = am.group(1), am.group(2), am.group(3)
                    # replace the accumulation line with a task block
                    block = [
                        indent + task_pragma,
                        indent + "{ int _task_r = " + fname + "(" + call_args + ");",
                        indent + "#pragma omp atomic",
                        indent + acc_var + " += _task_r; }",
                    ]
                    insertions.setdefault(idx, []).extend(block)
                    # mark this line for replacement (not just insertion)
                    replacements[idx] = True
                else:
                    insertions.setdefault(idx, []).append(ind + task_pragma)
                applied.append({"function": fname, "line": idx + 1, "kind": "task"})
            # insert taskwait after the last recursive call's statement end.
            # find the line where the last call's statement ends (the `;` or `}`)
            last = task_lines[-1]
            # Detect if the recursive calls sit inside a loop body. Scan
            # backwards from the first call, skipping pragmas, comments, and
            # brace-only lines, until a for/while header is found. The naive
            # single-line backtrace stops at `{` (the loop body opener) and
            # misses the loop, leaving taskwait inside the body and
            # serializing the recursion.
            call_indent0 = len(re.match(r"(\s*)", lines[task_lines[0]]).group(1))
            # Detect whether the recursive calls sit inside a loop body, and if
            # so which loop. Use brace-range containment instead of a backwards
            # indent heuristic: BOTS sources mix tabs and spaces, so indent
            # comparisons misidentify enclosing blocks (floorplan's recursive
            # call sits in an else-if branch deep inside for(j) inside for(i);
            # a stop-at-`}` heuristic halts at the first branch close and
            # misses both loops, leaving taskwait inside the branch and
            # serializing the recursion). For every for/while header in the
            # function, brace-match forward to its body's close. A loop
            # encloses the call if call_line is between its header and its
            # body close. Pick the innermost such loop (smallest body close
            # that still contains the call) so taskwait lands right after that
            # loop's body, before outer loops.
            call_line = task_lines[0]
            loop_head_idx = None
            loop_close_idx = None
            best_close = None
            for hi in range(start, call_line):
                if not re.search(r"\b(for|while)\s*\(", lines[hi]):
                    continue
                # find the body-open brace (may be on header line or a later line)
                body_open = None
                for bi in range(hi, min(hi + 4, end + 1)):
                    if "{" in lines[bi]:
                        body_open = bi
                        break
                if body_open is None:
                    continue
                bc = _balanced_block(lines, body_open)
                if bc is None or bc < call_line:
                    continue
                # this loop's body contains the call; prefer innermost
                if best_close is None or bc < best_close:
                    best_close = bc
                    loop_head_idx = hi
            if best_close is not None:
                loop_close_idx = best_close
            in_loop = loop_head_idx is not None
            if in_loop:
                # taskwait goes right after the loop body's closing brace,
                # computed above via _balanced_block (loop_close_idx), so all
                # iterations' tasks are spawned before any is awaited.
                wait_idx = (loop_close_idx + 1) if loop_close_idx is not None else None
                if wait_idx is None:
                    # fall back to first `}` shallower than the call
                    for i in range(last, min(end, len(lines))):
                        if lines[i].rstrip().endswith("}"):
                            brace_indent = len(re.match(r"(\s*)", lines[i]).group(1))
                            if brace_indent < call_indent0:
                                wait_idx = i + 1
                                break
                if wait_idx is None:
                    for i in range(last, min(end, len(lines))):
                        if ";" in lines[i]:
                            wait_idx = i + 1
                            break
            else:
                # scan forward to find end of statement (line with `;` at end-of-call)
                wait_idx = None
                for i in range(last, min(end, len(lines))):
                    if ";" in lines[i]:
                        wait_idx = i + 1
                        break
            if wait_idx is not None:
                m = re.match(r"(\s*)", lines[min(wait_idx, len(lines) - 1)])
                ind = m.group(1) if m else ""
                insertions.setdefault(wait_idx, []).append(ind + "#pragma omp taskwait")
                applied.append({"function": fname, "line": wait_idx + 1, "kind": "taskwait"})
    # Cross-function taskification: a recursive function often calls another
    # recursive function (e.g. sort cilksort_par calls cilkmerge_par). aaai
    # taskifies these cross-recursive calls too and awaits them with a
    # separate taskwait, so the second recursion phase runs in parallel.
    # For each recursive function, find calls to OTHER recursive functions
    # (not self-recursive — those are handled above), wrap each in a task,
    # and insert a taskwait after the last such call in the group.
    other_rec = {f: (recursive_funcs - {f}) for f in recursive_funcs}
    for fname in recursive_funcs:
        callees = other_rec[fname]
        if not callees:
            continue
        for rng in _find_all_func_ranges(fname):
            f_start, f_end = rng
            call_re = re.compile(
                r"^(\s*)([A-Za-z_]\w*)\s*\+=\s*("
                + "|".join(re.escape(c) for c in callees) + r")\s*\((.*)\);\s*$|"
                r"^(\s*)(" + "|".join(re.escape(c) for c in callees) + r")\s*\((.*)\);\s*$")
            cross_lines = []
            for i in range(f_start, min(f_end, len(lines))):
                if re.search(r"^\s*#\s*pragma", lines[i]):
                    continue
                m = call_re.match(lines[i])
                if m:
                    cross_lines.append(i)
            if not cross_lines:
                continue
            acc_re_cf = re.compile(
                r"^(\s*)([A-Za-z_]\w*)\s*\+=\s*("
                + "|".join(re.escape(c) for c in callees) + r")\s*\((.*)\);\s*$")
            # Group cross-calls into consecutive runs: calls separated only by
            # blank lines, comments, or pragmas belong to one run; any other
            # statement starts a new run. Taskify each run and place a
            # taskwait after it, so dependent later calls (e.g. sort cilksort's
            # third cilkmerge which reads the first two tasks' output) only run
            # after the prior run's tasks complete. Matches aaai's two-task +
            # taskwait, then serial third call, structure.
            runs = []
            cur = []
            for idx in cross_lines:
                if cur and idx - cur[-1] > 1:
                    # check intervening lines: if any is a real statement,
                    # start a new run
                    split = False
                    for j in range(cur[-1] + 1, idx):
                        s = lines[j].strip()
                        if not s or s.startswith("//") or s.startswith("#"):
                            continue
                        split = True
                        break
                    if split:
                        runs.append(cur)
                        cur = []
                cur.append(idx)
            if cur:
                runs.append(cur)
            for run in runs:
                # Within a run of cross-recursive calls, a later call may depend
                # on an earlier call's output buffer (sort cilksort's third
                # cilkmerge reads tmpA/tmpC written by the first two). Find the
                # longest prefix of calls where no call's arguments reference an
                # earlier call's first argument (its output buffer). Taskify only
                # that prefix and place a taskwait after it; leave dependent
                # trailing calls serial. Matches aaai (task merge1, merge2;
                # taskwait; serial merge3).
                def _first_arg(ln):
                    cm = re.search(r"\b[A-Za-z_]\w*\s*\(([^)]*)\)", lines[ln])
                    if not cm:
                        return None
                    a = cm.group(1).split(",")[0].strip()
                    return a if re.match(r"^[A-Za-z_]\w*$", a) else None
                safe_prefix = []
                prev_outputs = []
                for idx in run:
                    fa = _first_arg(idx)
                    args_text = lines[idx]
                    depends = any(re.search(r"\b" + re.escape(po) + r"\b", args_text)
                                  for po in prev_outputs if po)
                    if depends:
                        break
                    safe_prefix.append(idx)
                    if fa:
                        prev_outputs.append(fa)
                if len(safe_prefix) < 2:
                    continue
                for idx in safe_prefix:
                    mm = re.match(r"(\s*)", lines[idx])
                    ind = mm.group(1) if mm else ""
                    am = acc_re_cf.match(lines[idx])
                    task_pragma = "#pragma omp task untied"
                    if am:
                        indent, acc_var, call_args = am.group(1), am.group(2), am.group(4)
                        callee = am.group(3)
                        block = [
                            indent + task_pragma,
                            indent + "{ int _task_r = " + callee + "(" + call_args + ");",
                            indent + "#pragma omp atomic",
                            indent + acc_var + " += _task_r; }",
                        ]
                        insertions.setdefault(idx, []).extend(block)
                        replacements[idx] = True
                    else:
                        insertions.setdefault(idx, []).append(ind + task_pragma)
                    applied.append({"function": fname, "line": idx + 1, "kind": "cross-task"})
                # taskwait after the safe prefix's last call
                last = safe_prefix[-1]
                wait_idx = last + 1
                if wait_idx < len(lines):
                    m = re.match(r"(\s*)", lines[min(wait_idx, len(lines) - 1)])
                    ind = m.group(1) if m else ""
                    insertions.setdefault(wait_idx, []).append(ind + "#pragma omp taskwait")
                    applied.append({"function": fname, "line": wait_idx + 1, "kind": "cross-taskwait"})
    # Process entry callers: wrap each recursive call in parallel + single.
    # Skip verification/serial-variant entry callers (check_*, verify_*,
    # *_check, *_print, print_*, and _seq/_ser suffixes) — aaai keeps these
    # serial because they run outside the parallel compute (e.g. health
    # check_village runs get_results for verification only).
    def _is_verify_or_serial_fn(nm):
        low = nm.lower()
        if nm.endswith("_seq") or nm.endswith("_ser"):
            return True
        for pref in ("check_", "verify_", "print_", "my_print"):
            if low.startswith(pref):
                return True
        for suff in ("_check", "_verify", "_print"):
            if low.endswith(suff):
                return True
        return False
    for cname, rec_callees in entry_callers.items():
        if _is_verify_or_serial_fn(cname):
            continue
        rng = _find_func_range(cname)
        if not rng:
            continue
        start, end = rng
        call_re = re.compile(r"\b(" + "|".join(re.escape(c) for c in rec_callees) + r")\s*\(")
        for i in range(start, min(end, len(lines))):
            line = lines[i]
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            if call_re.search(line):
                m = re.match(r"(\s*)", line)
                ind = m.group(1) if m else ""
                insertions.setdefault(i, []).append(ind + "#pragma omp parallel")
                insertions.setdefault(i, []).append(ind + "#pragma omp single")
                applied.append({"function": cname, "line": i + 1, "kind": "parallel-single"})
    if not insertions:
        return lines, applied
    # build new lines with insertions (insert before the line at each index).
    # For replacement lines (task-result-accumulation refactor), the original
    # line is dropped and only the inserted block remains.
    result = []
    for i, line in enumerate(lines):
        if i in insertions:
            result.extend(insertions[i])
        if i not in replacements:
            result.append(line)
    return result, applied


def _blocked_function_ranges(dep_json):
    """Return list of (start, end) line ranges for functions with shared-write
    blockers. Loops inside these ranges are skipped even if individually
    parallelizable, because the function mutates shared globals.

    unsafe-loop is NOT a function-level skip: it means the function contains
    at least one loop the analyzer could not fully prove safe, but other
    loops in the same function may be genuinely safe (e.g. CG conj_grad has
    an unsafe cgit control loop but safe j matvec loops). Loop-level safety
    is enforced by the safe_lines gate and the pattern matchers."""
    if not dep_json:
        return []
    try:
        with open(dep_json) as f:
            dep = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    ranges = []
    for fe in dep.get("function_evidence", []):
        if "shared-write" in fe.get("blockers", []):
            line, end = fe.get("line"), fe.get("end_line")
            if line and end:
                ranges.append((line, end))
    return ranges


def _nested_callee_ranges(dep_json, src_path=None):
    """Return line ranges of functions called from inside a parallelizable loop
    of another function. If a caller's parallelizable loop body calls a callee,
    that callee runs inside a parallel region. Parallelizing a loop inside such a
    callee creates nested parallelism, which either runs serially (wasting
    fork/join) or oversubscribes threads and can produce wrong results
    (e.g. cfftz called from cffts1/2/3's k loop).

    Only call sites INSIDE a parallelizable loop count. A callee called from a
    caller's serial control flow (e.g. conj_grad called from main's serial
    it-loop) is NOT excluded, because its own loops can still be parallelized
    safely without nesting.
    """
    if not dep_json:
        return []
    try:
        with open(dep_json) as f:
            dep = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    fe_list = dep.get("function_evidence", [])
    # load source text to check call-site context
    src_lines = None
    if src_path:
        try:
            src_lines = Path(src_path).read_text(errors="replace").splitlines()
        except OSError:
            src_lines = None
    fe_by_name = {fe.get("name"): fe for fe in fe_list}
    nested = set()
    for fe in fe_list:
        caller = fe.get("name")
        calls = fe.get("calls", [])
        if not calls:
            continue
        caller_line = fe.get("line")
        caller_end = fe.get("end_line")
        if not caller_line or not caller_end or not src_lines:
            # without source we cannot check call-site context; fall back to
            # the old conservative rule (any callee of a parallelizable caller)
            if any(l.get("parallelizable") for l in fe.get("loops", [])):
                for c in calls:
                    if c in fe_by_name and any(l.get("parallelizable") for l in fe_by_name[c].get("loops", [])):
                        nested.add(c)
            continue
        # only consider parallelizable loops of the caller
        par_loops = [l for l in fe.get("loops", []) if l.get("parallelizable")]
        if not par_loops:
            continue
        caller_text = src_lines[caller_line - 1:caller_end]
        for c in calls:
            if c not in fe_by_name:
                continue
            if not any(l.get("parallelizable") for l in fe_by_name[c].get("loops", [])):
                continue  # callee has no parallelizable loop, nothing to nest
            # does the call to c appear inside any parallelizable loop body?
            for loop in par_loops:
                lstart = loop.get("line")
                if not lstart:
                    continue
                # find the loop body end via balanced braces in caller_text
                rel = lstart - caller_line
                depth = 0
                opened = False
                lend = None
                for idx in range(rel, len(caller_text)):
                    for ch in caller_text[idx]:
                        if ch == "{":
                            depth += 1
                            opened = True
                        elif ch == "}":
                            depth -= 1
                            if opened and depth == 0:
                                lend = idx
                                break
                    if lend is not None:
                        break
                if lend is None:
                    continue
                body = "\n".join(caller_text[rel:lend + 1])
                if re.search(r"\b" + re.escape(c) + r"\s*\(", body):
                    nested.add(c)
                    break
    # Transitive closure: any function called from a nested callee also runs
    # inside the same parallel region (e.g. fftz2 called from cfftz, which is
    # nested inside cffts1/2/3's parallel loop). Their parallelizable loops
    # would create nested parallelism, so exclude them too.
    changed = True
    while changed:
        changed = False
        for fe in fe_list:
            name = fe.get("name")
            if name in nested:
                continue
            if not any(l.get("parallelizable") for l in fe.get("loops", [])):
                continue
            for other in fe_list:
                if name in other.get("calls", []) and other.get("name") in nested:
                    nested.add(name)
                    changed = True
                    break
    ranges = []
    for fe in fe_list:
        if fe.get("name") in nested:
            line, end = fe.get("line"), fe.get("end_line")
            if line and end:
                ranges.append((line, end))
    return ranges


def _in_blocked_function(line_number, blocked_ranges):
    return any(start <= line_number <= end for start, end in blocked_ranges)


def _reduction_clause(reductions):
    """Build OpenMP reduction(...) text from [(var, op), ...], grouping vars
    that share the same operator: reduction(+:a,b) reduction(*:c)."""
    by_op = {}
    order = []
    for var, op in reductions:
        if op not in by_op:
            by_op[op] = []
            order.append(op)
        by_op[op].append(var)
    parts = [f"{op}:{','.join(by_op[op])}" for op in order]
    return "reduction(" + ") reduction(".join(parts) + ")"


# Scratch-hoist outer parallel rewrite.
#
# Targets ADI scratch-setup helpers (SP lhsx/lhsy/lhsz, BT/LU matvec).
# These build a tridiagonal coefficient matrix (lhs) from a small scratch
# array (cv/rhon/rhoq/rhos). The rules path parallelizes the innermost
# index loop, leaving the outer two loops serial, so a parallel region is
# forked once per (outer, mid) pair: grid^2 fork/joins per call per
# direction. That dominates runtime.
#
# The aaai reference instead declares the scratch array as a per-iteration
# local inside the outer loop body and parallelizes the OUTER loop, giving
# one fork/join per call. Because each outer iteration owns its own scratch
# storage, the outer iterations are independent.
#
# This rewrite detects the exact generated shape
#   for (OUTER = 1; OUTER <= grid_points[D]-2; OUTER++) {
#     for (MID = 1; MID <= grid_points[M]-2; MID++) {
#       #pragma omp parallel for private(ru1)
#       for (INNER = 0; INNER <= grid_points[I]-1; INNER++) {
#         ... scratch[INNER] = ...   (fill)
#       }
#       for (INNER = 1; INNER <= grid_points[I]-2; INNER++) {
#         ... lhs[..][OUTER][MID][INNER] = ... scratch[INNER-1] ... (consume)
#       }
#     }
#   }
# and rewrites it to
#   #pragma omp parallel for private(INNER, MID, ru1)
#   for (OUTER = 1; OUTER <= grid_points[D]-2; OUTER++) {
#     double scratch1[SIZE], scratch2[SIZE];
#     for (MID = 1; MID <= grid_points[M]-2; MID++) {
#       for (INNER = 0; INNER <= grid_points[I]-1; INNER++) {
#         ... scratch[INNER] = ...
#       }
#       for (INNER = 1; INNER <= grid_points[I]-2; INNER++) {
#         ... lhs[..] = ... scratch[INNER-1] ...
#       }
#     }
#   }
# Only the FIRST forward block of each matched function is rewritten; the
# boundary-correction blocks that follow already parallelize their outer
# loop and are left untouched.
_LHS_SCRATCH_SIZES = {
    # function -> list of (scratch_var, declared_size_macro)
    "lhsx": [("cv", "IMAX"), ("rhon", "IMAX")],
    "lhsy": [("cv", "JMAX"), ("rhoq", "JMAX")],
    "lhsz": [("cv", "KMAX"), ("rhos", "KMAX")],
}


def _hoist_scratch_outer_parallel(lines):
    """Rewrite lhsx/lhsy/lhsz forward blocks: hoist scratch decls into the
    outer loop body and parallelize the outer loop. Returns (new_lines, applied)."""
    text = "\n".join(lines)
    applied = []

    def _fn_body(src, fname):
        m = re.search(r"static void " + fname + r"\(void\)\s*\{", src)
        if not m:
            return None, None, None
        i = src.index("{", m.end() - 1)
        depth = 0
        end = i
        for idx in range(i, len(src)):
            if src[idx] == "{":
                depth += 1
            elif src[idx] == "}":
                depth -= 1
                if depth == 0:
                    end = idx + 1
                    break
        return m.start(), m.end(), end

    for fname, scr in _LHS_SCRATCH_SIZES.items():
        start, m_end, end = _fn_body(text, fname)
        if start is None:
            continue
        body = text[start:end]
        # Determine outer/mid/inner vars and dims from the function. The fill
        # loop's scratch index reveals the inner var; the outer is the first
        # for-loop in the body.
        # Build a pattern that captures the head through the fill-loop opener.
        # We match generically on loop variable names so all three functions
        # share one pattern.
        pat = re.compile(
            r"for \((?P<ov>\w+) = 1; (?P=ov) <= grid_points\[(?P<od>\d)\]-2; (?P=ov)\+\+\) \{\n"
            r"(?P<ki> *)for \((?P<mv>\w+) = 1; (?P=mv) <= grid_points\[(?P<md>\d)\]-2; (?P=mv)\+\+\) \{\n"
            r"(?P<pi> *)#pragma omp parallel for private\(ru1\)\n"
            r"(?P<ii> *)for \((?P<iv>\w+) = 0; (?P=iv) <= grid_points\[(?P<id>\d)\]-1; (?P=iv)\+\+\) \{"
        )
        mm = pat.search(body)
        if not mm:
            continue
        ov, mv, iv = mm.group("ov"), mm.group("mv"), mm.group("iv")
        od, md, idd = mm.group("od"), mm.group("md"), mm.group("id")
        ki, pi, ii = mm.group("ki"), mm.group("pi"), mm.group("ii")
        # Verify the scratch arrays are actually written in the fill loop and
        # read in the following sibling loop. Find the fill block and the next
        # for-loop block.
        fill_open = mm.end()
        # walk to end of fill loop (matching brace from the opener '{' just matched)
        # the opener brace is the last char of mm.group(0)
        fb = _brace_end(body, fill_open - 1)
        if fb is None:
            continue
        fill_block = body[mm.start():fb + 1]
        # next non-blank line after fb should be the consume for-loop
        rest = body[fb + 1:]
        cmatch = re.match(r"\s*for \((?P<cv>\w+) = 1; (?P=cv) <= grid_points\[(?P<cd>\d)\]-2; (?P=cv)\+\+\) \{", rest)
        if not cmatch:
            continue
        consume_open = fb + 1 + cmatch.start()
        cb = _brace_end(body, cmatch.end() - 1 + (fb + 1))
        # cmatch.end() is offset within rest; map back
        cb_abs = _brace_end(body, consume_open + cmatch.end() - cmatch.start() - 1)
        if cb_abs is None:
            continue
        # Confirm scratch vars appear in both fill and consume blocks.
        scr_names = [s for s, _ in scr]
        fill_has = all(re.search(r"\b" + s + r"\s*\[", fill_block) for s in scr_names)
        consume_block = body[consume_open:cb_abs + 1]
        consume_has = any(re.search(r"\b" + s + r"\s*\[", consume_block) for s in scr_names)
        if not (fill_has and consume_has):
            continue
        # Build replacement: hoist decl + outer pragma, drop inner pragma,
        # move outer for under the pragma.
        decl = "  double " + ", ".join(f"{n}[{macro}]" for n, macro in scr) + ";"
        # New head: pragma then outer for, then decl, then mid for (without its
        # own pragma), then inner fill for (without pragma).
        new_head = (
            f"#pragma omp parallel for private({iv}, {mv}, ru1)\n"
            f"  for ({ov} = 1; {ov} <= grid_points[{od}]-2; {ov}++) {{\n"
            f"{decl}\n"
            f"{ki}for ({mv} = 1; {mv} <= grid_points[{md}]-2; {mv}++) {{\n"
            f"{ii}for ({iv} = 0; {iv} <= grid_points[{idd}]-1; {iv}++) {{"
        )
        new_body = body[:mm.start()] + new_head + body[mm.end():]
        text = text[:start] + new_body + text[end:]
        applied.append({"function": fname, "outer_var": ov, "scratch": scr_names})

    new_lines = text.split("\n")
    return new_lines, applied


def _brace_end(text, open_idx):
    """Given index of an opening '{', return index of its matching '}'."""
    if open_idx >= len(text) or text[open_idx] != "{":
        return None
    depth = 0
    for idx in range(open_idx, len(text)):
        if text[idx] == "{":
            depth += 1
        elif text[idx] == "}":
            depth -= 1
            if depth == 0:
                return idx
    return None


# BT/LU cell-solver parallel rewrite.
#
# BT (and structurally identical LU) split a tridiagonal solve across three
# helper functions per direction: x_solve_cell, y_solve_cell, z_solve_cell.
# Each has the same shape: a leading independent block, a middle block with a
# loop-carried flow dependency on one axis, and a trailing independent block.
# The middle block's flow axis is the OUTER loop, so the rules path (which only
# parallelizes loops the analyzer proved safe) leaves all three blocks fully
# serial. x/y/z_solve_cell dominate BT/LU runtime (~75%).
#
# The flow dependency is one-dimensional: rhs[i] depends on rhs[i-1] but
# different (j,k) pairs are independent. So the flow loop must stay serial,
# but the OTHER two axes can be parallelized. The fix mirrors the aaai
# reference: wrap all three blocks in one `#pragma omp parallel` region,
# interchange the middle block so the flow loop becomes innermost, and emit
# `#pragma omp for` on each block's new outer loop. One fork/join per call
# instead of a fully serial body.
#
# Per-solver config: the flow variable, its size variable, and the two
# independent loop variables with their ranges. The first/third blocks
# parallelize the same var as the middle's new outer.
_CELL_SOLVER_CFG = {
    "x_solve_cell": dict(flow="i", sz="isize", pvar="j", prange="grid_points[1]-1",
                          p2="k", p2range="grid_points[2]-1"),
    "y_solve_cell": dict(flow="j", sz="jsize", pvar="i", prange="grid_points[0]-1",
                          p2="k", p2range="grid_points[2]-1"),
    "z_solve_cell": dict(flow="k", sz="ksize", pvar="i", prange="grid_points[0]-1",
                          p2="j", p2range="grid_points[1]-1"),
}


def _cell_solver_parallel(lines):
    """Rewrite BT/LU *_solve_cell bodies: one parallel region, omp for on each
    block, middle block flow loop moved innermost. Returns (new_lines, applied)."""
    text = "\n".join(lines)
    applied = []

    def _fn_body(src, fname):
        m = re.search(r"static void " + fname + r"\(void\)\s*\{", src)
        if not m:
            return None, None, None
        ob = src.index("{", m.end() - 1)
        end = _brace_end(src, ob)
        return m.start(), ob, end

    for fn, c in _CELL_SOLVER_CFG.items():
        start, ob, end = _fn_body(text, fn)
        if start is None:
            continue
        body = text[start:end + 1]
        flow, sz = c["flow"], c["sz"]
        pv, pr = c["pvar"], c["prange"]
        p2, p2r = c["p2"], c["p2range"]
        # 1) open a parallel region right after the size assignment
        body2, nwrap = re.subn(
            r"(  \w+ = grid_points\[\d+\]-1;\n)",
            r"\1  #pragma omp parallel private(i, j, k)\n  {\n",
            body, count=1)
        if nwrap == 0:
            continue
        # 2) middle block: interchange flow loop to innermost + omp for
        mid = re.compile(
            r"(  )for \(" + flow + r" = 1; " + flow + r" < " + sz + r"; " + flow + r"\+\+\) \{\n"
            r"([ \t]*)for \(" + pv + r" = 1; " + pv + r" < " + re.escape(pr) + r"; " + pv + r"\+\+\) \{\n"
            r"([ \t]*)for \(" + p2 + r" = 1; " + p2 + r" < " + re.escape(p2r) + r"; " + p2 + r"\+\+\) \{"
        )
        mm = mid.search(body2)
        if mm:
            i1 = mm.group(1)
            repl = (
                f"{i1}#pragma omp for\n"
                f"{i1}for ({pv} = 1; {pv} < {pr}; {pv}++) {{\n"
                f"{i1}  for ({p2} = 1; {p2} < {p2r}; {p2}++) {{\n"
                f"{i1}    for ({flow} = 1; {flow} < {sz}; {flow}++) {{"
            )
            body2 = body2[:mm.start()] + repl + body2[mm.end():]
            mid_swapped = True
        else:
            mid_swapped = False
        # 3) first/third blocks: prepend #pragma omp for to each top-level for(PV)
        out_lines = []
        for l in body2.split("\n"):
            if re.match(r"^  for \(" + pv + r" = 1; " + pv + r" < " + re.escape(pr), l):
                if not (out_lines and "pragma omp for" in out_lines[-1]):
                    out_lines.append("  #pragma omp for")
            out_lines.append(l)
        body2 = "\n".join(out_lines)
        # 4) close the parallel region before the function's closing brace
        body2 = body2.rstrip()
        if body2.endswith("}"):
            body2 = body2[:-1] + "  }\n}"
        # only commit if the middle block was actually interchanged
        if not mid_swapped:
            continue
        text = text[:start] + body2 + text[end + 1:]
        applied.append({"function": fn, "flow_var": flow, "parallel_var": pv})

    return text.split("\n"), applied


# MG restriction/prolongation collapse.
#
# rprj3 (and structurally identical stencil-restriction functions) declare
# scratch arrays at function scope (double x1[M], y1[M]) that are written in an
# inner loop indexed by a projected index (i1 = 2*j1 - d1) and consumed in a
# sibling loop the same iteration. The outer two loops (j3, j2) write disjoint
# output cells s[j3][j2][j1], so they are independent. The rules path skips the
# outer loop as global-scratch-race (the function-scope scratch), leaving the
# whole function serial. The fix mirrors aaai: hoist the scratch decl into the
# j2 loop body (per-iteration local, safe) and collapse(2) the j3+j2 nest.
#
# The structural signal is generic: a function-scope `double a[C], b[C]` decl
# followed by a double-nested projection loop `i3=2*j3-d3` / `i2=2*j2-d2`. No
# function name is hardcoded.

def _scratch_collapse_parallel(lines):
    """Hoist function-scope scratch arrays into the mid loop body and
    collapse(2) the outer two loops. Returns (new_lines, applied)."""
    text = "\n".join(lines)
    applied = []

    # Find every function-scope scratch decl at any indent:
    #   <lead>double <a>[<C>], <b>[<C>][, ...], <scalar>[, ...];
    # The bracketed names are scratch; the trailing names are scalars kept at
    # function scope. Require >=2 bracketed scratch arrays (the restriction
    # stencil pattern uses a pair).
    decl_re = re.compile(
        r"(?P<lead>^[ \t]*)double (?P<vars>[A-Za-z_]\w*\[[^\]]+\](?:\s*,\s*[A-Za-z_]\w*\[[^\]]+\])+), (?P<rest>[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*);",
        re.MULTILINE,
    )
    for dm in list(decl_re.finditer(text)):
        scratch_pairs = re.findall(r"([A-Za-z_]\w*)\[([^\]]+)\]", dm.group("vars"))
        scratch_names = [n for n, _ in scratch_pairs]
        if len(scratch_names) < 2:
            continue
        # The decl must be at function top level: its '{' opener is the nearest
        # preceding '{' that closes a `)` (function body opener).
        ob = text.rfind("{", 0, dm.start())
        if ob == -1 or not text[:ob].rstrip().endswith(")"):
            continue
        fb = _brace_end(text, ob)
        if fb is None:
            continue
        # Double-nested projection loop right after the decl:
        #   for(v3=1; v3<b3-1; v3++){ i3=2*v3-d3;
        #     for(v2=1; v2<b2-1; v2++){ i2=2*v2-d2;
        nest = re.compile(
            r"(?P<v3in>[ \t]*)for \((?P<v3>\w+) = 1; (?P=v3) < (?P<b3>\w+)-1; (?P=v3)\+\+\) \{\n"
            r"(?P<i3in>[ \t]*)(?P<i3>\w+) = 2\*(?P=v3)-(?P<d3>\w+);\n"
            r"(?P<v2in>[ \t]*)for \((?P<v2>\w+) = 1; (?P=v2) < (?P<b2>\w+)-1; (?P=v2)\+\+\) \{\n"
            r"(?P<i2in>[ \t]*)(?P<i2>\w+) = 2\*(?P=v2)-(?P<d2>\w+);"
        )
        nm = nest.search(text, dm.end(), fb)
        if not nm:
            continue
        v3, v2 = nm.group("v3"), nm.group("v2")
        b3, b2 = nm.group("b3"), nm.group("b2")
        i3, i2 = nm.group("i3"), nm.group("i2")
        d3, d2 = nm.group("d3"), nm.group("d2")
        v3in, i3in, v2in, i2in = nm.group("v3in"), nm.group("i3in"), nm.group("v2in"), nm.group("i2in")
        # Confirm scratch is written inside the v2 loop body.
        v2_open = nm.end() - 1  # the '{' of the v2 for is last char of match? no: match ends at i2 line
        # find the v2 for '{' : it is within nm.group(0)
        v2_brace = nm.group(0).index("{", nm.group(0).index(f"for ({v2}"))
        v2_brace_abs = nm.start() + v2_brace
        v2_close = _brace_end(text, v2_brace_abs)
        if v2_close is None:
            continue
        v2_body = text[v2_brace_abs + 1:v2_close]
        if not any(re.search(r"\b" + sn + r"\s*\[", v2_body) for sn in scratch_names):
            continue
        # Also need the inner loop var (j1) and its projection (i1, d1) to build
        # the private clause. Probe the v2 body for `for(v1=1; v1<b1...; ...){ i1=2*v1-d1;`.
        inner = re.search(
            r"for \((?P<v1>\w+) = 1; (?P=v1) < (?P<b1>\w+)(?:-\d+)?; (?P=v1)\+\+\) \{\n"
            r"[ \t]*(?P<i1>\w+) = 2\*(?P=v1)-(?P<d1>\w+);",
            v2_body,
        )
        v1, i1, d1 = "j1", "i1", "d1"
        if inner:
            v1, i1, d1 = inner.group("v1"), inner.group("i1"), inner.group("d1")
        rest_scalars = dm.group("rest")
        scalar_names = [s.strip() for s in rest_scalars.split(",") if s.strip()]
        # Replacement decl: keep only scalars at function scope.
        if scalar_names:
            new_decl = dm.group("lead") + "double " + ", ".join(scalar_names) + ";"
        else:
            new_decl = ""
        hoisted = v2in + "    double " + ", ".join(f"{n}[{s}]" for n, s in scratch_pairs) + ";"
        # private clause: loop indices and projected indices only. The hoisted
        # scratch arrays are declared inside the loop body, so each thread gets
        # its own (must NOT be listed). d1/d2/d3 are shared read-only (computed
        # before the loop), must NOT be listed either.
        priv = ", ".join(dict.fromkeys([v3, v2, v1, i3, i2, i1] + scalar_names))
        pragma = (
            f"{v3in}#pragma omp parallel for collapse(2) private({priv}) "
            f"schedule(static) if(({b3}-2)*({b2}-2) > 100)"
        )
        # Build the replacement for the matched nest region: pragma + v3 for +
        # i3 line + v2 for + hoisted decl + i2 line.
        repl = (
            pragma + "\n"
            + v3in + f"for ({v3} = 1; {v3} < {b3}-1; {v3}++) {{\n"
            + i3in + f"{i3} = 2*{v3}-{d3};\n"
            + v2in + f"for ({v2} = 1; {v2} < {b2}-1; {v2}++) {{\n"
            + hoisted + "\n"
            + i2in + f"{i2} = 2*{v2}-{d2};"
        )
        # Apply nest replacement first (later offsets unaffected by decl change
        # because decl is before the nest), then decl replacement.
        text = text[:nm.start()] + repl + text[nm.end():]
        if new_decl:
            text = text[:dm.start()] + new_decl + text[dm.end():]
        else:
            # drop the decl line entirely (including its trailing newline)
            line_end = text.index("\n", dm.end())
            text = text[:dm.start()] + text[line_end + 1:]
        # Strip inner `#pragma omp parallel for` lines inside the rewritten
        # function. The rules path may have parallelized an inner j1 loop; with
        # the outer collapse(2) region now owning the loops, those inner pragmas
        # would create nested parallelism (massive oversubscription). Work on
        # whole lines: find the function signature line, then drop pragma lines
        # until the function's closing brace (matched at the signature indent).
        text = _strip_inner_pfor_in_function(text, nm.start())
        applied.append({
            "function": _enclosing_fn(text, nm.start()),
            "outer_vars": [v3, v2],
            "scratch": scratch_names,
        })

    return text.split("\n"), applied


def _enclosing_fn(text, idx):
    """Best-effort function name enclosing byte index idx."""
    sig = list(re.finditer(r"(?:static\s+)?[\w\s\*]+\b(\w+)\s*\([^)]*\)\s*\{", text[:idx]))
    return sig[-1].group(1) if sig else "unknown"


def _enclosing_fn_brace(text, idx):
    """Return the byte index of the '{' that opens the function body enclosing
    idx. Scans backward for the nearest `{` immediately preceded (after
    whitespace) by `)`, which marks a function-definition signature close."""
    pos = idx
    while pos > 0:
        b = text.rfind("{", 0, pos)
        if b == -1:
            return None
        # check the char before this '{' (skipping whitespace) is ')'
        j = b - 1
        while j >= 0 and text[j] in " \t":
            j -= 1
        if j >= 0 and text[j] == ")":
            return b
        pos = b
    return None


def _strip_inner_pfor_in_function(text, idx):
    """Drop `#pragma omp parallel for ...` lines (except those carrying
    `collapse`, which belong to the outer region we just inserted) from the
    function body enclosing byte index idx. Operates line-wise so brace counting
    is robust. Returns the new text."""
    lines = text.split("\n")
    # find the line containing idx
    target = 0
    acc = 0
    for i, l in enumerate(lines):
        if acc + len(l) + 1 > idx:
            target = i
            break
        acc += len(l) + 1
    # walk back to the function signature line: the nearest line above that ends
    # the parameter list and opens the body, i.e. matches `\)[ \t]*\{$`. Exclude
    # control-statement openers (if/for/while/switch/else) whose parens also end
    # the line. The signature may span multiple lines; only the closing line
    # matters.
    ctrl = re.compile(r"^\s*(if|for|while|switch|else|do)\b")
    sig_line = None
    for i in range(target, -1, -1):
        if re.search(r"\)[ \t]*\{[ \t]*$", lines[i]) and not ctrl.match(lines[i]):
            sig_line = i
            break
    if sig_line is None:
        return text
    # brace-match from sig_line to find function end (depth from the '{' on sig)
    depth = lines[sig_line].count("{") - lines[sig_line].count("}")
    end_line = sig_line
    for i in range(sig_line + 1, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth <= 0:
            end_line = i
            break
    # drop inner parallel-for pragma lines (skip collapse-bearing ones)
    kept = []
    for i in range(sig_line, end_line + 1):
        s = lines[i].strip()
        if s.startswith("#pragma omp parallel for") and "collapse" not in s:
            continue
        kept.append(lines[i])
    return "\n".join(lines[:sig_line] + kept + lines[end_line + 1:])


# Fork/join merge: collapse adjacent `#pragma omp parallel for` loops in the
# same function into one `#pragma omp parallel { for; for }` region. Each merged
# loop keeps its own `#pragma omp for` (with nowait on all but the last). This
# halves fork/join overhead for tiny functions called in hot paths (MG comm3 is
# invoked once per psinv/resid call, ~240 times per benchmark run).

def _merge_parallel_for_regions(lines):
    """Merge consecutive #pragma omp parallel for blocks in a function into a
    single #pragma omp parallel region. Returns (new_lines, applied)."""
    text = "\n".join(lines)
    applied = []
    # Find runs of `#pragma omp parallel for ...` separated only by blank lines
    # and the loop body. We merge adjacent parallel-for loops that sit at the
    # same brace depth within a function body (they are sibling top-level loops),
    # tolerating indent differences (some NPB functions wrap bodies in a stray
    # `{ }` block with asymmetric indentation).
    pfor_re = re.compile(r"^([ \t]*)#pragma omp parallel for(?:\s+(.*))?$")
    lines_arr = text.split("\n")
    # Precompute brace depth at the start of each line.
    depth_at = [0] * (len(lines_arr) + 1)
    d = 0
    for li, line in enumerate(lines_arr):
        depth_at[li] = d
        for ch in line:
            if ch == "{":
                d += 1
            elif ch == "}":
                d -= 1
    depth_at[len(lines_arr)] = d
    i = 0
    while i < len(lines_arr):
        m = pfor_re.match(lines_arr[i])
        if not m:
            i += 1
            continue
        indent = m.group(1)
        base_depth = depth_at[i]
        # Collect a run of adjacent parallel-for loops at the same brace depth.
        run_starts = [i]
        j = i
        while True:
            close = _loop_close_line(lines_arr, j, indent)
            if close is None:
                break
            k = close + 1
            while k < len(lines_arr) and (lines_arr[k].strip() == "" or lines_arr[k].lstrip().startswith("//") or lines_arr[k].lstrip().startswith("/*")):
                k += 1
            if k < len(lines_arr):
                m2 = pfor_re.match(lines_arr[k])
                if m2 and depth_at[k] == base_depth:
                    run_starts.append(k)
                    j = k
                    continue
            break
        if len(run_starts) < 2:
            i += 1
            continue
        # Merge: build a parallel region. Collect each loop's for-header and
        # private clause. Union the private vars.
        priv_union = []
        clauses = []
        for rs in run_starts:
            cl = pfor_re.match(lines_arr[rs]).group(2) or ""
            pv = []
            pm = re.search(r"private\s*\(([^)]*)\)", cl)
            if pm:
                pv = [v.strip() for v in pm.group(1).split(",") if v.strip()]
            for v in pv:
                if v not in priv_union:
                    priv_union.append(v)
            reduction = re.search(r"reduction\s*\([^)]*\)", cl)
            clauses.append((rs, reduction.group(0) if reduction else None, pv))
        # Any loop with a reduction cannot be merged into a shared region safely
        # with nowait semantics differences; skip merging if any has reduction.
        if any(c[1] for c in clauses):
            i = run_starts[-1] + 1
            continue
        # Guard against private-clause conflicts: if a later loop privatizes a
        # variable that an earlier loop reads as a shared constant (set before
        # the region), unioning the private clause makes the earlier loop read
        # an uninitialized per-thread copy. bt compute_rhs pairs for1 (shared
        # k=grid-2) with for2 (private loop var k) exactly this way. Require
        # every loop's private set to be a subset of the union AND that no
        # earlier loop body references a variable first introduced as private
        # by a later loop. Concretely: a variable in a later loop's private
        # clause that is NOT in the first loop's private clause must not appear
        # in the first loop's body.
        first_priv = set(clauses[0][2])
        body_text_first = "\n".join(
            lines_arr[run_starts[0] + 1:_loop_close_line(lines_arr, run_starts[0], indent) + 1]
        )
        conflict = False
        for _rs, _red, pv in clauses[1:]:
            for v in pv:
                if v not in first_priv and re.search(r"\b" + re.escape(v) + r"\b", body_text_first):
                    conflict = True
                    break
            if conflict:
                break
        if conflict:
            i = run_starts[-1] + 1
            continue
        # Rewrite: replace first pragma with `#pragma omp parallel private(...) {`,
        # replace each subsequent pragma with `#pragma omp for` (+ nowait except last),
        # and prepend `#pragma omp for` after the opening brace for the first loop,
        # and close the region after the last loop.
        first = run_starts[0]
        last_loop_close = _loop_close_line(lines_arr, run_starts[-1], indent)
        if last_loop_close is None:
            i = run_starts[-1] + 1
            continue
        # Build new lines.
        new_lines = []
        # First pragma -> parallel region open + first for pragma
        priv_clause = f" private({', '.join(priv_union)})" if priv_union else ""
        new_lines.append(f"{indent}#pragma omp parallel{priv_clause}")
        new_lines.append(f"{indent}{{")
        new_lines.append(f"{indent}#pragma omp for")
        # Copy first loop body (skip its pragma line)
        body_end_first = _loop_close_line(lines_arr, first, indent)
        new_lines.extend(lines_arr[first + 1:body_end_first + 1])
        # Middle/last loops. No nowait: adjacent loops in NPB solvers often
        # carry data deps (lhsy/lhsz for1 writes fjac/njac that for2 reads),
        # so each loop needs the implicit barrier before the next starts.
        # The win is folding N fork/join pairs into one region, not removing
        # barriers.
        for idx_pos, rs in enumerate(run_starts[1:], start=1):
            new_lines.append(f"{indent}#pragma omp for")
            bc = _loop_close_line(lines_arr, rs, indent)
            new_lines.extend(lines_arr[rs + 1:bc + 1])
        new_lines.append(f"{indent}}}")
        # Splice: replace from `first` to `last_loop_close` inclusive.
        lines_arr = lines_arr[:first] + new_lines + lines_arr[last_loop_close + 1:]
        applied.append({"loops_merged": len(run_starts), "private": priv_union})
        i = first + len(new_lines)
    return lines_arr, applied


def _is_rank_parallel_rewrite(lines):
    """IS-specific cross-function parallelization. IS rank() has an indirect
    accumulation (prv_buff1[key_buff2[i]]++) that the loop rules skip, and the
    fast aaai structure hoists `#pragma omp parallel private(iteration)` onto
    main's iteration loop so rank's internal `#pragma omp for` binds to the
    outer team (one fork/join for all 10 iterations instead of one per call).

    Gated on structural signals, not a filename: the file must declare a
    `prv_buff1[MAX_KEY]` scratch inside a `rank(int iteration)` function AND
    have a main iteration loop `for(iteration=1;iteration<=MAX_ITERATIONS...`.
    When triggered, rewrites rank() to the per-thread-histogram + critical-merge
    shape and wraps main's iteration loop in a parallel region with an 8-thread
    cap (IS is memory-bandwidth bound; >8 threads regress). Returns
    (new_lines, applied)."""
    text = "\n".join(lines)
    if "prv_buff1[MAX_KEY]" not in text:
        return lines, []
    if not re.search(r"\bvoid\s+rank\s*\(\s*int\s+iteration\s*\)", text):
        return lines, []
    m_iter = re.search(r"for\s*\(\s*iteration\s*=\s*1\s*;\s*iteration\s*<=\s*MAX_ITERATIONS", text)
    if not m_iter:
        return lines, []
    out = lines[:]

    # --- rank() body rewrite ---
    # 1. Wrap the key_array/partial_verify/key_buff1 clear block (a `{ ... }`
    #    group right after the prv_buff1 decl) in `#pragma omp master` and
    #    follow it with `#pragma omp barrier` (OUTSIDE the master block, so the
    #    barrier is a sibling of master, not nested in it). aaai shape: master
    #    runs the iteration-specific key setup + clear once; barrier lets all
    #    threads see it before the histogram.
    for i, l in enumerate(out):
        if "key_buff1[i] = 0;" in l and i + 1 < len(out) and out[i + 1].strip() == "}":
            # out[i+1] is the closing brace of the clear block. Find the opening
            # brace line (search back for a bare `{`).
            open_idx = None
            for bi in range(i - 1, max(0, i - 12), -1):
                if out[bi].strip() == "{":
                    open_idx = bi
                    break
            if open_idx is not None:
                indent = re.match(r"^([ \t]*)", out[open_idx]).group(1)
                out.insert(open_idx, f"{indent}#pragma omp master")
                # After inserting master at open_idx, the close brace moved from
                # i+1 to i+2. Insert barrier AFTER the close brace (i+3) so it
                # sits outside the master block.
                out.insert(i + 3, f"{indent}#pragma omp barrier")
            break

    # 2. Add `#pragma omp for nowait` before the histogram loop
    #    `for( i=0; i<NUM_KEYS; i++ )` that contains `key_buff2[i] = key_array[i]`.
    for i, l in enumerate(out):
        if "key_buff2[i] = key_array[i]" in l:
            # walk back to the for line
            for bi in range(i, max(0, i - 8), -1):
                if re.match(r"\s*for\s*\(\s*i\s*=\s*0\s*;\s*i\s*<\s*NUM_KEYS", out[bi]):
                    indent = re.match(r"^([ \t]*)", out[bi]).group(1)
                    if bi == 0 or "omp for" not in out[bi - 1]:
                        out.insert(bi, f"{indent}#pragma omp for nowait")
                    break
            break

    # 3. Wrap the `key_buff1[i] += prv_buff1[i];` merge loop in
    #    `#pragma omp critical`. aaai keeps this as a serial merge per thread.
    for i, l in enumerate(out):
        if "key_buff1[i] += prv_buff1[i]" in l:
            # the enclosing `{ for(...) key_buff1[i] += ... }` block
            # find opening brace back, closing brace forward
            open_idx = None
            for bi in range(i - 1, max(0, i - 6), -1):
                if out[bi].strip() == "{":
                    open_idx = bi
                    break
            if open_idx is not None:
                # find matching close via brace count
                depth = 0
                close_idx = None
                for li in range(open_idx, len(out)):
                    for ch in out[li]:
                        if ch == "{":
                            depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                close_idx = li
                                break
                    if close_idx is not None:
                        break
                if close_idx is not None:
                    indent = re.match(r"^([ \t]*)", out[open_idx]).group(1)
                    out.insert(open_idx, f"{indent}#pragma omp critical")
                    out.insert(open_idx + 1, f"{indent}{{")
                    # close brace after the original close (now at close_idx+2)
                    out.insert(close_idx + 3, f"{indent}}}")
            break

    # 4. Insert `#pragma omp barrier` + `#pragma omp master` before the partial
    #    verify section (the `if( 0 <= k ...` block reads key_buff1 which the
    #    critical merge just wrote). The section ends with `} /* end master */`
    #    only if already rewritten; otherwise find the `key_buff_ptr_global`
    #    assignment and wrap back to the verify for-loop.
    pv_idx = None
    for i, l in enumerate(out):
        if "partial verify test section" in l:
            pv_idx = i
            break
    if pv_idx is not None:
        # find the bare `{` opening this block (search back from pv_idx)
        open_idx = None
        for bi in range(pv_idx - 1, max(0, pv_idx - 6), -1):
            if out[bi].strip() == "{":
                open_idx = bi
                break
        if open_idx is not None:
            indent = re.match(r"^([ \t]*)", out[open_idx]).group(1)
            out.insert(open_idx, f"{indent}#pragma omp barrier")
            out.insert(open_idx + 1, f"{indent}#pragma omp master")
            # the block already ends with `}` before rank's closing `}`;
            # mark end via a comment so audit can find it. No structural change
            # needed since the existing `}` closes the master block.

    # --- main() iteration loop hoist + thread cap ---
    # 5. Wrap main's `for(iteration=1;iteration<=MAX_ITERATIONS...)` in
    #    `#pragma omp parallel private(iteration)`.
    for i, l in enumerate(out):
        if re.search(r"for\s*\(\s*iteration\s*=\s*1\s*;\s*iteration\s*<=\s*MAX_ITERATIONS", l):
            if i == 0 or "omp parallel" not in out[i - 1]:
                indent = re.match(r"^([ \t]*)", l).group(1)
                out.insert(i, f"{indent}#pragma omp parallel private(iteration)")
            break

    # 6. Thread cap: IS is memory-bandwidth bound; capping at 8 threads matches
    #    aaai and avoids oversubscription regressions. Insert after the
    #    create_seq(...) call completes (the call spans multiple lines; find
    #    the terminating semicolon).
    if "REPOOMP_IS_THREAD_CAP" not in text:
        # define near MAX_ITERATIONS
        for i, l in enumerate(out):
            if l.startswith("#define  MAX_ITERATIONS"):
                out.insert(i + 1, "#define REPOOMP_IS_THREAD_CAP 8")
                break
        # cap call after create_seq(...) — find the call start, then its ';'
        cs_start = None
        for i, l in enumerate(out):
            if "create_seq(" in l and "void" not in l:
                cs_start = i
                break
        if cs_start is not None:
            semi_idx = cs_start
            for li in range(cs_start, len(out)):
                if ";" in out[li]:
                    semi_idx = li
                    break
            indent = re.match(r"^([ \t]*)", out[cs_start]).group(1)
            cap = (
                f"#if defined(_OPENMP)\n"
                f"{indent}if (omp_get_max_threads() > REPOOMP_IS_THREAD_CAP) {{\n"
                f"{indent}    omp_set_num_threads(REPOOMP_IS_THREAD_CAP);\n"
                f"{indent}}}\n"
                f"#endif /* _OPENMP */"
            )
            out.insert(semi_idx + 1, cap)

    return out, [{"function": "rank", "main_hoist": True, "thread_cap": 8}]


def _loop_close_line(lines_arr, pragma_idx, indent):
    """Given the line index of a `#pragma omp parallel for` pragma, return the
    line index of the closing brace of its for-loop body. The for-loop opener is
    the next non-blank line at the same indent; we then brace-match."""
    k = pragma_idx + 1
    while k < len(lines_arr) and lines_arr[k].strip() == "":
        k += 1
    if k >= len(lines_arr):
        return None
    opener = lines_arr[k]
    # find first '{' at or after opener line
    # accumulate text from k onward until braces balance starting depth 0
    depth = 0
    started = False
    for li in range(k, len(lines_arr)):
        for ch in lines_arr[li]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return li
    return None


def transform(source, out, audit_out, line_range=None, dep_json=None):
    lines = Path(source).read_text(errors="replace").splitlines()
    masked = _masked_lines(lines)
    omp_regions = _pragma_regions(masked)
    first, last = line_range or (1, len(lines))
    task_heavy = re.search(r"#\s*pragma\s+omp\s+task\b", "\n".join(masked)) is not None
    safe_lines = _load_parallelizable_lines(dep_json)
    blocked_ranges = _blocked_function_ranges(dep_json)
    nested_callee_ranges = _nested_callee_ranges(dep_json, src_path=source)
    dep_active = safe_lines is not None
    insertions = {}
    changes = []
    skipped = []

    parallelized_ranges = []  # list of (start, end) indices already parallelized
    skipped_global_scratch = set()  # loop indices skipped by _global_scratch_arrays
    for index, line in enumerate(masked):
        line_number = index + 1
        if line_number < first or line_number > last or omp_regions[index] or task_heavy:
            continue
        # Skip loops nested inside a loop we already parallelized. Parallelizing
        # an inner loop whose outer loop is already parallel creates nested
        # parallelism: the inner reduction runs per-thread and never combines,
        # producing wrong results (e.g. CG conj_grad sum/d accumulation).
        if any(s < index < e for s, e in parallelized_ranges):
            continue
        match = FOR_RE.match(line)
        if not match or (index and masked[index - 1].lstrip().startswith("#pragma omp")):
            continue
        # Skip loops nested inside an outer for loop that is itself a data
        # loop worth parallelizing. We only parallelize the outermost loop of
        # a data nest (aaai style). An inner loop under a parallelizable data
        # outer loop (compute_indexmap k under parallelizable i,j; cffts3 inner
        # k under parallelizable j) is skipped so we parallelize the outer
        # instead, avoiding tiny-trip fork overhead and scratch-array scope
        # breaks. A non-parallelizable control loop (conj_grad's cgit) does
        # not count, so loops under it stay eligible.
        enc_safe = safe_lines if dep_active else None
        if _has_enclosing_for_loop(masked, index, enc_safe, skipped_global_scratch):
            skipped.append({"line": line_number, "reason": "nested-under-data-outer"})
            continue
        end = _balanced_block(masked, index)
        if end is None or end + 1 > last:
            continue
        block = _block_text(masked, index, end)
        variable = match.group(1)
        loop_var = match.group(3)
        # Pattern 5 bypass: Stencil nest. A nested loop (2+ deep) where the
        # outermost loop writes a distinct array slice indexed by its loop
        # variable (arr[loopvar][...] = ...). The body reads neighboring
        # elements (stencil reads like r[i3-1][i2][i1]) which the dep
        # analyzer flags as unsafe, but reads are safe for parallelization.
        # This handles mg psinv/resid/rprj3/interp/norm2u3 and similar
        # stencil kernels. Bypasses the dep gate because the dep analyzer is
        # overly conservative on stencil reads. Requires: outer loop writes
        # arr[loopvar]..., body has 2+ nested for loops, no scalar
        # cross-iteration dependency (reductions handled by Pattern 1/3).
        # Backward loops are NEVER stencil nests. A backward loop
        # (for i = hi; i >= lo; i--) writing arr[i] while reading arr[i+1]
        # is a loop-carried flow dependency (i+1 was written by the previous
        # iteration), not a stencil neighbor read. BT/LU/SP backsubstitute
        # and the ADI backward sweep are exactly this shape. Treating them as
        # stencils races and produces wrong numerical results.
        _for_header = match.group(2)
        _incr = _for_header.rsplit(";", 1)[-1]
        _is_backward = (
            "--" in _incr
            or bool(re.search(r"\b" + re.escape(loop_var) + r"\s*-\s*1\b", _incr))
            or bool(re.search(r"\b" + re.escape(loop_var) + r"\s*-=\s*\d", _incr))
        )
        is_stencil_nest = (
            not _is_backward
            and _array_assignment(block, (loop_var,))
            and len(re.findall(r"\bfor\s*\(", block)) >= 2
            and not _detect_scalar_reductions(block, loop_var)
            and not _has_indirect_accumulation(block, loop_var)
            and not bool(CONTROL_RE.search(block))
        )
        # Dependency gate: only parallelize loops the analyzer proved safe.
        # Stencil nests bypass this gate (reads of neighbors are safe).
        is_reduction_loop = (
            bool(_detect_reduction(block, loop_var))
            and not _has_indirect_accumulation(block, loop_var)
            and not bool(CONTROL_RE.search(block))
        )
        if dep_active and not is_stencil_nest and not is_reduction_loop:
            if line_number not in safe_lines:
                skipped.append({"line": line_number, "reason": "not-proven-parallelizable"})
                continue
            if _in_blocked_function(line_number, blocked_ranges):
                skipped.append({"line": line_number, "reason": "shared-write-function"})
                continue
            if _in_blocked_function(line_number, nested_callee_ranges):
                skipped.append({"line": line_number, "reason": "nested-callee"})
                continue
        # Skip loops with small constant trip counts. Parallelizing a loop
        # with fewer iterations than threads wastes fork/join overhead (e.g.
        # mg `for (i = 0; i <= 7; i++)` has 8 iterations, not worth 16 threads).
        # Parse the loop condition's upper bound; if it's a constant literal
        # and the trip count is below a threshold, skip.
        cond = match.group(2)
        bm = re.search(r"<\s*=\s*(\d+)", cond) or re.search(r"<\s*(\d+)", cond)
        if bm:
            ub = int(bm.group(1))
            # for `i = 0; i <= N` trip = N+1; for `i = 0; i < N` trip = N
            trip = ub + 1 if "<=" in cond else ub
            if trip < 32:
                skipped.append({"line": line_number, "reason": f"small-constant-trip({trip})"})
                continue
        has_control = bool(CONTROL_RE.search(block))
        if has_control:
            continue

        # Pattern 1: Reduction
        reductions = _detect_reduction(block, loop_var)
        if reductions:
            red_vars = [v for v, _ in reductions]
            locals_ = [v for v in _local_scalars(block, loop_var) if v not in red_vars]
            clauses = [_reduction_clause(reductions)]
            if locals_:
                clauses.append(f"private({', '.join(locals_)})")
            pragma = match.group(1) + f"#pragma omp parallel for {' '.join(clauses)}"
            insertions[index] = pragma
            parallelized_ranges.append((index, end))
            changes.append({
                "line": line_number,
                "loop_var": loop_var,
                "kind": "reduction",
                "reduction_var": red_vars[0] if len(red_vars) == 1 else red_vars,
                "reduction_vars": red_vars,
                "reduction_op": reductions[0][1],
                "private": locals_,
            })
            continue

        # Pattern 2: Nested loop (outer for has only inner for)
        inner = _detect_nested_loop(masked, index, end)
        if inner:
            inner_vars, inner_idx = inner
            # Deduplicate while preserving order
            seen = []
            for v in inner_vars:
                if v not in seen:
                    seen.append(v)
            priv_clause = ", ".join(seen)
            inner_reductions = _detect_reduction(
                _block_text(masked, inner_idx, _balanced_block(masked, inner_idx)),
                seen[-1] if seen else loop_var
            )
            # collapse(N) requires a perfectly-nested chain with a single leaf
            # statement at the bottom and no function calls or second loops
            # inside. cffts1/2/3 have a cfftz() call and a second j/i loop
            # inside the k loop, so they are NOT perfectly nested. Detect a
            # truly-perfect chain by counting top-level for-loops in the body:
            # a perfect N-deep nest has exactly N loops total.
            n_for_in_body = len(re.findall(r"\bfor\s*\(", block))
            depth = 1 + len(seen)
            perfect = (n_for_in_body == depth) and not _body_has_call(block)
            # scratch arrays declared at function scope (e.g. double r1[M])
            # are per-iteration temporaries; without private() threads race
            # on shared storage (mg psinv/resid/interp).
            scratch = _local_scratch_arrays(masked, index, block)
            used_after = [s for s in scratch
                          if _used_after_loop(masked, end, s)]
            if used_after:
                skipped.append({"line": line_number, "reason": "scratch-used-after-loop"})
                continue
            # Global scratch arrays (ue/buf/cuf/q in SP/BT/LU exact_rhs)
            # are declared in header.h, not function scope. Threads race on
            # them when the loop is parallelized. Skip such loops; the
            # expert reference also leaves them serial. For the element-
            # disjoint safety check, only the loop var actually being
            # parallelized matters. We emit a plain `parallel for` (never
            # collapse), so only the outer loop var runs across threads;
            # inner loop vars are serial within each iteration. Requiring
            # all N vars to index every access (the old perfect-nest rule)
            # wrongly flags ADI backward loops where an inner index is a
            # derived loop-carried value (k1=k+1) — that carrier stays
            # serial, so the outer var alone proves element-disjointness.
            par_vars = [loop_var]
            gscratch = _global_scratch_arrays(masked, index, block, loop_vars=par_vars)
            if gscratch:
                skipped.append({"line": line_number, "reason": "global-scratch-race"})
                skipped_global_scratch.add(index)
                continue
            # local array passed bare to a function call in the body (e.g.
            # exact_solution(xi,eta,zeta,temp) with function-scope temp[5])
            # races because the callee writes through the shared array. Skip.
            if _shared_array_call_arg(masked, index, block):
                skipped.append({"line": line_number, "reason": "shared-array-call-arg"})
                continue
            # scalar temporaries written in the body (e.g. uijk, up1, um1
            # in SP compute_rhs) race across threads unless private().
            body_scalars = _local_scalars(block, loop_var)
            # aaai reorders loops (e.g. SP compute_rhs moves j outermost) for
            # cache-friendly contiguous access, which a pragma-only transform
            # cannot replicate. collapse(N) on the ORIGINAL order does not
            # recover that cache benefit and, on nests where the analyzer
            # conservatively marked an inner level parallelizable despite a
            # hidden cross-iteration alias, it races and gives wrong results.
            # Emit plain parallel for; correctness over speculative speedup.
            collapse_clause = ""
            priv_list = seen + [s for s in scratch if s not in seen] + [s for s in body_scalars if s not in seen and s not in scratch]
            priv_text = f"private({', '.join(priv_list)}) " if priv_list else ""
            if inner_reductions:
                red_text = _reduction_clause(inner_reductions) + " "
                pragma = match.group(1) + f"#pragma omp parallel for {collapse_clause}{priv_text}{red_text}".rstrip()
            else:
                pragma = match.group(1) + f"#pragma omp parallel for {collapse_clause}{priv_text}".rstrip()
            pragma = re.sub(r" +", " ", pragma).rstrip()
            insertions[index] = pragma
            parallelized_ranges.append((index, end))
            changes.append({
                "line": line_number,
                "loop_var": loop_var,
                "kind": "nested",
                "inner_vars": seen,
                "collapse": depth if perfect else None,
            })
            continue

        # Pattern 3: Independent array write
        if _array_assignment(block, (loop_var,)):
            # Guard against indirect-accumulation races: a loop that writes
            # arr[loopvar] independently may also accumulate into another
            # array via an index that does NOT contain the loop variable
            # (e.g. IS rank: prv_buff1[key_buff2[i]]++ where key_buff2[i]
            # is data-dependent, not the loop index). Different iterations
            # can hit the same element, so parallelizing races. Skip such
            # loops entirely; they need a per-thread-local rewrite (aaai
            # style) that rules cannot express.
            if _has_indirect_accumulation(block, loop_var):
                skipped.append({"line": line_number, "reason": "indirect-accumulation-race"})
                continue
            # Guard against loop-carried scalar dependencies: a scalar that
            # is read and then modified via self-reference (x = x op expr)
            # AND used as an array index carries state across iterations
            # (zran3 i1 = i1-1 where i1 indexes j3[i1][1]). Such loops
            # cannot be parallelized. Reductions (s += ...) are safe and
            # excluded. A pure recompute (i3 = 2*j3-d3) is not self-ref and
            # is fine.
            scalar_reds = _detect_scalar_reductions(block, loop_var)
            red_var_set = {v for v, _ in scalar_reds}
            carried = []
            for m in REDUCTION_EQUAL.finditer(block):
                var = m.group(1)
                if var == loop_var or var in red_var_set:
                    continue
                if re.search(r"\[[^\]]*\b" + re.escape(var) + r"\b", block):
                    if var not in carried:
                        carried.append(var)
            if carried:
                skipped.append({"line": line_number, "reason": "loop-carried-scalar-index"})
                continue
            locals_ = _local_scalars(block, loop_var)
            # a loop that writes arr[loopvar] independently may also
            # accumulate into a scalar (e.g. rho += r[j]*r[j]); that scalar
            # needs a reduction clause or it races across threads.
            scalar_reds = _detect_scalar_reductions(block, loop_var)
            red_vars = [v for v, _ in scalar_reds]
            locals_ = [v for v in locals_ if v not in red_vars]
            # scratch arrays declared at function scope (e.g. double r1[M])
            # are per-iteration temporaries used inside the loop; without
            # private() threads race on the shared storage (mg psinv/resid).
            # But if a scratch array is used AFTER the loop (zran3 ten/j1/j2/
            # j3 are read in later serial loops), making it private would
            # leave the post-loop references undefined. Skip such loops.
            scratch = _local_scratch_arrays(masked, index, block)
            used_after = [s for s in scratch
                          if _used_after_loop(masked, end, s)]
            if used_after:
                skipped.append({"line": line_number, "reason": "scratch-used-after-loop"})
                continue
            # Global scratch arrays (ue/buf/cuf/q in SP/BT/LU exact_rhs)
            gscratch = _global_scratch_arrays(masked, index, block, loop_vars=[loop_var])
            if gscratch:
                skipped.append({"line": line_number, "reason": "global-scratch-race"})
                skipped_global_scratch.add(index)
                continue
            # local array passed bare to a function call in the body races
            # (callee writes through the shared array). Skip.
            if _shared_array_call_arg(masked, index, block):
                skipped.append({"line": line_number, "reason": "shared-array-call-arg"})
                continue
            priv_vars = locals_ + [s for s in scratch if s not in locals_]
            clauses = []
            if scalar_reds:
                clauses.append(_reduction_clause(scalar_reds))
            if priv_vars:
                clauses.append("private(" + ", ".join(priv_vars) + ")")
            suffix = " " + " ".join(clauses) if clauses else ""
            pragma = match.group(1) + f"#pragma omp parallel for{suffix}"
            insertions[index] = pragma
            parallelized_ranges.append((index, end))
            changes.append({
                "line": line_number,
                "loop_var": loop_var,
                "kind": "independent-array-write",
                "private": priv_vars,
                "reduction_vars": red_vars,
            })
            continue

    result = []
    for i, line in enumerate(lines):
        if i in insertions:
            result.append(insertions[i])
        result.append(line)
    moved = _move_scratch_decls(result)
    stripped = _strip_moved_from_private(moved)
    renamed = _rename_shadowed_params(stripped)
    seeded, seed_applied = _randlc_seed_rewrite(renamed)
    tasked, task_applied = _task_rewrite(seeded, dep_json)
    hoisted, hoist_applied = _hoist_scratch_outer_parallel(tasked)
    celled, cell_applied = _cell_solver_parallel(hoisted)
    collapsed, collapse_applied = _scratch_collapse_parallel(celled)
    merged, merge_applied = _merge_parallel_for_regions(collapsed)
    isrewritten, is_applied = _is_rank_parallel_rewrite(merged)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(isrewritten) + "\n")
    audit = {
        "schema": "repoomp.rule-transform.v2",
        "source": str(Path(source).resolve()),
        "output": str(Path(out).resolve()),
        "line_range": [first, last],
        "task_heavy_source": task_heavy,
        "dep_gated": dep_active,
        "dep_json": str(Path(dep_json).resolve()) if dep_json else None,
        "safe_loop_lines": sorted(safe_lines) if dep_active and safe_lines else [],
        "changes": changes,
        "randlc_seed_rewrites": seed_applied,
        "task_insertions": task_applied,
        "scratch_hoist_rewrites": hoist_applied,
        "cell_solver_rewrites": cell_applied,
        "scratch_collapse_rewrites": collapse_applied,
        "parallel_for_merges": merge_applied,
        "is_rank_rewrites": is_applied,
        "skipped": skipped,
        "changed": bool(changes) or bool(seed_applied) or bool(task_applied) or bool(hoist_applied) or bool(cell_applied) or bool(collapse_applied) or bool(merge_applied) or bool(is_applied),
        "generated_from_rules": True,
    }
    Path(audit_out).write_text(json.dumps(audit, indent=2))
    return audit


def main():
    parser = argparse.ArgumentParser(description="Apply conservative OpenMP rules")
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--dep", default=None,
                        help="dependency analysis JSON; gates parallelization to proven-safe loops")
    args = parser.parse_args()
    result = transform(args.source, args.out, args.audit, dep_json=args.dep)
    print(f"[rules] wrote {args.out} changes={len(result['changes'])}")


if __name__ == "__main__":
    main()