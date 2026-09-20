#!/usr/bin/env python3
"""OpenMP primitive addition via LLM API + expert rules.

Consumes dependency analysis JSON + hotspot JSON + source, asks the LLM to
insert OpenMP pragmas, constrained by expert rules so the output is correct
and faster than the expert baseline.

Usage:
    python primitive_adder.py --src cg.c --dep dep.json --hot hot.json \
        --out cg_opt.c
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def _load_repoomp_env():
    """Load REPOOMP_* exports from ~/.bashrc for non-interactive shells."""
    if os.environ.get("REPOOMP_API_KEY"):
        return
    bashrc = Path.home() / ".bashrc"
    if not bashrc.exists():
        return
    for line in bashrc.read_text(errors="replace").splitlines():
        m = re.match(r"\s*export\s+(REPOOMP_\w+)=['\"]?([^'\"\n]*)['\"]?\s*$", line)
        if m:
            os.environ[m.group(1)] = m.group(2)


_load_repoomp_env()

API_BASE = os.environ.get("REPOOMP_API_BASE", "")
if API_BASE.endswith("/chat/completions"):
    API_BASE = API_BASE[:-len("/chat/completions")]
API_KEY = os.environ.get("REPOOMP_API_KEY", "")
MODEL = os.environ.get("REPOOMP_MODEL", "GLM-5.2")


# ---- expert rules ----------------------------------------------------------

REDUCTION_OPS = re.compile(
    r"(\w+)\s*(\+=|-=|\*=|/=)\s*"
)
REDUCTION_ASSIGN = re.compile(r"(\w+)\s*=\s*\1\s*[+\-*/]")


def detect_reduction_vars(body_lines):
    """Return set of scalar names that are reduction accumulators."""
    vars_ = set()
    text = "\n".join(body_lines)
    for m in REDUCTION_OPS.finditer(text):
        vars_.add(m.group(1))
    for m in REDUCTION_ASSIGN.finditer(text):
        vars_.add(m.group(1))
    return vars_


def is_array_write_indexed(body_lines):
    """True if loop body writes arr[<var>] = ... (iteration-independent)."""
    text = "\n".join(body_lines)
    return bool(re.search(r"\w+\s*\[\s*\w+\s*\]\s*=", text))


def classify_loops(src_text):
    """Per-loop expert classification. Returns list of dicts keyed by line."""
    lines = src_text.splitlines()
    out = []
    for i, line in enumerate(lines):
        if not re.search(r"\bfor\s*\(", line):
            continue
        # gather body (next 30 lines, naive brace depth)
        body = []
        depth = 0
        started = False
        for j in range(i, min(i + 31, len(lines))):
            body.append(lines[j])
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]:
                started = True
            if started and depth == 0 and j > i:
                break
        red_vars = detect_reduction_vars(body)
        arr_write = is_array_write_indexed(body)
        kind = "sequential"
        if red_vars:
            kind = "reduction"
        elif arr_write:
            kind = "independent"
        out.append({
            "line": i + 1,
            "header": line.strip()[:100],
            "kind": kind,
            "reduction_vars": sorted(red_vars),
        })
    return out


# ---- LLM prompt ------------------------------------------------------------

EXPERT_RULES_TEXT = """EXPERT RULES (must follow):
1. A loop that accumulates into a scalar (x += ... or x = x + ...) is a
   REDUCTION. Parallelize with `#pragma omp for reduction(+:x)` (or
   appropriate op). Do NOT use critical sections for reductions.
2. A loop that writes arr[j] = ... where each j is distinct is INDEPENDENT.
   Parallelize with `#pragma omp for`. Add `nowait` only if the next loop
   does not read the written values.
3. A scalar used across loop iterations with a true cross-iteration
   dependency (e.g. alpha = rho0/d where rho0 comes from previous iter)
   is SEQUENTIAL. Do NOT parallelize that loop. Instead parallelize the
   inner independent/reduction loops and use `#pragma omp single` or a
   barrier to compute the scalar between parallel loops.
4. Group consecutive parallel loops inside ONE `#pragma omp parallel`
   region to avoid fork/join overhead. Use `#pragma omp for` (with
   reduction clause if needed) for each loop inside.
5. For the CG conj_grad cgit loop: the cgit loop itself is sequential
   (rho0=rho, alpha=rho0/d, beta=rho/rho0 are cross-iteration deps). But
   each inner loop over j is parallel. The `#pragma omp parallel` region
   goes INSIDE the cgit for loop body, wrapping the inner j loops of ONE
   cgit iteration. Do NOT put the parallel region around the cgit loop.
   If you wrap the cgit loop itself in a parallel region, all threads
   execute the cgit loop redundantly and the loop counter cgit races,
   causing deadlock or wrong results. Correct structure:
     for (cgit = ...) {        // sequential, outside any parallel region
         rho0 = rho; d = 0.0; rho = 0.0;
         #pragma omp parallel private(sum, k, alpha, beta)
         {
             #pragma omp for ...
             for (j ...) { ... }
             #pragma omp for reduction(+:d)
             for (j ...) { ... }
             alpha = rho0 / d;   // redundant, all threads compute
             #pragma omp for reduction(+:rho)
             for (j ...) { ... }
             beta = rho / rho0;  // redundant
             #pragma omp for
             for (j ...) { ... }
         }
     }
   Compute alpha and beta redundantly (all threads compute the same value)
   by declaring them private. This avoids omp single overhead.
6. Remove redundant barriers: a `#pragma omp for reduction(...)` already
   has an implicit barrier at the end. Do not add an explicit
   `#pragma omp barrier` right after it.
7. Fix nthreads detection: omp_get_num_threads() must be called inside a
   parallel region (use #pragma omp master inside #pragma omp parallel).
8. Preserve all computation, only add OpenMP pragmas. Do not change
   numerical results. Verification must still pass.
9. CRITICAL: Every `#pragma omp for` whose loop body contains an inner
   `for (k = ...)` loop MUST list `k` in its private clause. Example:
   `#pragma omp for private(sum, k)`. Forgetting `k` causes a data race
   on the shared loop counter k and produces wrong results. This is the
   most common OpenMP bug. Always check inner loop variables.
10. LOOP SAFETY: The LOOP CLASSIFICATION above marks each loop SAFE or
    UNSAFE based on dependency analysis. SAFE loops have no cross-iteration
    dependencies and can be parallelized directly. UNSAFE loops were flagged
    because the analyzer detected a possible stencil read, indirect write
    (arr[non-loop-var] = ...), or function call in the body. You MAY
    parallelize an UNSAFE loop ONLY IF you can prove it is actually safe:
    - The body writes arr[loopvar] = ... via a macro (e.g. crmul(c, a, b)
      expands to c.real = a.real * b). Each iteration writes a distinct
      element, so it is independent.
    - The body declares local arrays inside the loop and writes only to
      them and to arr[loopvar] slices. Each iteration's locals are private.
    - The body calls a function that only reads shared data and writes to
      per-iteration-local or arr[loopvar] storage.
    If you cannot prove safety, leave the loop serial. Parallelizing a
    truly unsafe loop causes data races and NaN. When in doubt, do NOT
    parallelize.
11. REDUNDANT EXECUTION DANGER: A `for` loop inside a `#pragma omp
    parallel` region but WITHOUT a `#pragma omp for` is executed by ALL
    threads redundantly. If that loop updates shared variables (e.g.
    ku = ku + ln, ln = 2 * ln), all threads race on them, causing wrong
    results or hangs. NEVER put a sequential loop with cross-iteration
    state inside a parallel region unless it is wrapped in `#pragma omp
    single`. If a loop has cross-iteration scalar dependencies, leave it
    OUTSIDE the parallel region entirely.
12. For FFT functions (cffts1/cffts2/cffts3): the outer `for (k = 0; k <
    d[2]; k++)` loop is parallelizable. Each iteration writes a distinct
    xout[k] slice. The y0/y1 arrays used as scratch buffers MUST be declared
    INSIDE the k loop body so each iteration (and thus each thread) gets its
    own private copy. If y0/y1 are declared OUTSIDE the k loop, all threads
    share them and race, producing wrong results. Move the `dcomplex y0[...]`
    and `dcomplex y1[...]` declarations to just inside the k loop, right
    after the `for (k = 0; k < d[2]; k++) {` line. Then add `#pragma omp
    parallel for private(k, jj, j, i)` before the k loop. The inner jj, j, i
    loops stay serial inside. Do NOT parallelize the inner loops.
13. For the FT evolve function: the triple-nested k/j/i loop writes
    u1[k][j][i] via the crmul macro (distinct element per iteration).
    Parallelize with `#pragma omp parallel for collapse(3) private(i,j,k)`.
    Do NOT list loop variables in both parallel private AND collapse for
    private clauses. Use `collapse(3)` to flatten all three loops.
14. REFACTOR MODE: When the prompt asks for a full refactored function
    (not INSERT lines), you may rewrite the function body to eliminate
    loop-carried dependencies that block parallelization. This applies to
    three structural patterns that pragma insertion alone cannot fix:
    (a) Indirect accumulation: a loop body does arr[data[i]]++ where the
    index is data-dependent (contains a nested array access), so two
    iterations can hit the same element. Fix by giving each thread a
    private local array, parallelizing the counting loop, then merging
    the per-thread arrays into the shared one inside a
    `#pragma omp critical` block.
    (b) Shared static scratch buffer: a loop writes through a pointer
    into a `static` scratch array whose seed advances across iterations
    via a randlc-style call. Fix by recomputing each iteration's seed
    directly from the loop counter (not advancing a running seed) and
    making the scratch array a per-iteration local.
    (c) Unsafe-loop with a parallelizable inner loop: the analyzer
    flagged the function unsafe but an inner loop is genuinely
    independent. Fix by restructuring so the independent loop runs in a
    `#pragma omp for` and any sequential state stays outside the
    parallel region or under `#pragma omp single`.
    (d) Loop reordering for stencil solvers (SP/BT/LU x_solve, y_solve,
    z_solve, and similar ADI solver functions): a nest of 3 loops where
    ONE loop has a loop-carried dependency and the other two are
    independent. The dependent loop writes arr[v+1] or arr[v+2] (via
    v1=v+1, v2=v+2) which the next iteration of that same loop reads.
    To parallelize, you must FIRST identify which loop is dependent:
    - x_solve: the i loop is dependent (i1=i+1, i2=i+2, writes lhs[][i1]).
      j and k are independent. Move j to the outermost position.
    - y_solve: the j loop is dependent (j1=j+1, j2=j+2, writes lhs[][j1]).
      i and k are independent. Move i to the outermost position.
    - z_solve: the k loop is dependent (k1=k+1, k2=k+2, writes lhs[][k1]).
      i and j are independent. Move j (or i) to the outermost position.
    Then SWAP loops so the independent loop becomes outermost, and put
    `#pragma omp parallel for` on it. The dependent loop stays serial
    inside. Example for x_solve (i dependent, j independent):
      BEFORE:
        for (i = 0; i < N-3; i++) {        // dependent: writes lhs[i+1]
          i1 = i+1; i2 = i+2;
          for (j = 1; j < M-2; j++) {     // independent
            for (k = 1; k < P-2; k++) { ... }
          }
        }
      AFTER (j outer parallel, i middle serial):
        #pragma omp parallel for private(i, k, i1, i2, m, fac1, fac2)
        for (j = 1; j < M-2; j++) {
          for (i = 0; i < N-3; i++) {
            i1 = i+1; i2 = i+2;
            for (k = 1; k < P-2; k++) { ... }
          }
        }
    For y_solve the SAME swap but i becomes outer (i is independent, j
    is dependent). For z_solve j becomes outer (j is independent, k is
    dependent). The parallel loop's iterations touch disjoint slices so
    they never race. The dependent loop still runs serial within each
    parallel iteration, preserving its dependency. Apply this swap to
    EVERY dependent-outer/independent-middle nest in the function. Do
    NOT parallelize the dependent loop itself. CRITICAL: list ALL scalar
    temporaries written in the body (fac1, fac2, i1, i2, j1, j2, k1, k2,
    m) in the private clause. Forgetting any causes a data race.
    (e) BT solver cells (x_solve_cell, y_solve_cell, z_solve_cell and
    their backsubstitute partners): these have a nest of 2-3 loops where
    ONE loop has a cross-iteration dependency because the body reads
    rhs[v-1] or lhs[v-1] from the previous iteration of that same loop.
    The dependent axis is DIFFERENT for each function, you must identify
    it from the body (look for which index appears as [v-1] or [v+1]):
    - x_solve_cell and x_backsubstitute: the i loop is dependent (body
      reads rhs[i-1] or rhs[i+1]). j and k are independent. Parallelize
      the j loop (move j outermost, add `#pragma omp parallel for`).
    - y_solve_cell and y_backsubstitute: the j loop is dependent (body
      reads rhs[j-1] or rhs[j+1]). i and k are independent. Parallelize
      the i loop (move i outermost, add `#pragma omp parallel for`).
    - z_solve_cell and z_backsubstitute: the k loop is dependent (body
      reads rhs[k-1] or rhs[k+1]). i and j are independent. Parallelize
      the i loop (move i outermost, add `#pragma omp parallel for`).
    NEVER parallelize the dependent loop. The dependent loop stays serial
    inside the parallel outer loop. The body calls helper functions
    (binvcrhs, matvec_sub, matmul_sub) that write to arr[i][j][k] slices;
    each parallel iteration touches a distinct slice so they are safe.
    CRITICAL: the private clause must list EVERY loop variable that is
    NOT the parallelized outer loop, INCLUDING the dependent loop
    variable. The dependent loop runs serially inside each thread, but
    it is still a per-iteration variable that each thread must own
    privately; if it is shared, all threads write to one variable at
    once and you get a race that produces NaN or wrong results. The exact
    private clauses are, by function:
      x_solve_cell:        parallelize j, private(i, k)
      y_solve_cell:        parallelize i, private(j, k)
      z_solve_cell:        parallelize i, private(j, k)
      x_backsubstitute:    parallelize j, private(i, k, m, n)
      y_backsubstitute:    parallelize i, private(j, k, m, n)
      z_backsubstitute:    parallelize i, private(j, k, m, n)
    Use these EXACT clauses. Do not list the parallelized loop variable
    in private() (it is private automatically). Do not omit the dependent
    loop variable from private(). After reordering, the loop order for
    x_solve_cell is j outer, i middle (dependent), k inner. For
    y_solve_cell and z_solve_cell it is i outer, then the dependent loop,
    then the remaining independent loop. For x_backsubstitute the order is
    j outer, i middle (dependent, runs downward from grid-2), k inner.
    For y_backsubstitute the order is i outer, j middle (dependent), k
    inner. For z_backsubstitute the order is i outer, j middle, k inner
    (dependent). Keep the dependent loop's original bounds and direction.
    In refactor mode you may move declarations, add per-thread local
    arrays, rewrite seed or index computation, and add
    critical/single/barrier pragmas. You MUST keep the function
    signature (name, parameters, return type) unchanged and the
    numerical results identical. Verification will compile and run the
    full workload, so correctness is enforced by execution, not by
    line-by-line diff.
    (f) Function-scope scratch arrays that race when the outer loop is
    parallelized. A function declares `double cv[N], rhon[N];` (or any
    fixed-size buffer) at function scope and fills it inside a
    (j,k,i)-nest, then reads it in a sibling loop over the SAME j,k:
        double cv[IMAX], rhon[IMAX];          // function scope
        for (j=...) { for (k=...) {
            for (i=...) { cv[i] = ...; rhon[i] = ...; }   // fill
            for (i=...) { lhs[..][i][j][k] = ...cv[i-1]..rhon[i]..; }  // read
        }}
    If you parallelize the j loop, different j-threads write the SAME
    cv[i]/rhon[i] (indexed by i, not j) and the read loop sees torn
    values -> NaN. The fix is to MOVE the scratch declarations INSIDE
    the parallelized loop body so each iteration owns its own copy:
        #pragma omp parallel for private(i, k, ru1)
        for (j = 1; j <= grid_points[1]-2; j++) {
          double cv[IMAX], rhon[IMAX];        // per-iteration, auto-private
          for (k = 1; k <= grid_points[2]-2; k++) {
            for (i = 0; i <= grid_points[0]-1; i++) { cv[i] = ...; rhon[i] = ...; }
            for (i = 1; i <= grid_points[0]-2; i++) { lhs[..][i][j][k] = ...cv[i]..; }
          }
        }
    This applies to SP lhsx/lhsy/lhsz (cv, rhon) and any function with
    the same shape: a function-scope buffer filled and consumed within
    one outer iteration, indexed by a loop variable that is NOT the
    parallelized one. Never leave such a buffer at function scope when
    parallelizing the loop that fills it.
    (g) Cache-friendly loop reordering for fully-independent nests. When
    a nest of 3+ loops has NO loop-carried dependency on any axis (every
    axis is dep-proven parallelizable, e.g. SP compute_rhs forcing/rhs
    loops over i,j,k writing u/rho_i/us/vs/ws/qss/speed/ainv), the
    choice of which loop to parallelize affects cache locality, not
    correctness. The C array is `arr[i][j][k]` with k innermost
    (contiguous), so the LAST index advances fastest in memory. To get
    contiguous access per parallel iteration, move the MIDDLE index
    outermost and parallelize it, keeping the fastest-varying and
    slowest indices inner. For `for(i){for(j){for(k){ arr[i][j][k]... }}}`
    reorder to `for(j){ for(i){ for(k){ arr[i][j][k]... }}}` and put
    `#pragma omp parallel for private(i, k, ...)` on the j loop. Each
    j-slice then walks contiguous k-memory. This recovers the 2-3x cache
    benefit of the expert reference on grid kernels like SP compute_rhs.
    Only reorder when ALL axes are independent; never reorder a nest
    that has a dependent axis (use rule (d)/(e) for those).
"""


def _numbered_source(src_text):
    """Return source with 1-indexed line numbers for patch-style prompting."""
    lines = src_text.splitlines()
    width = len(str(len(lines)))
    return "\n".join(f"{str(i+1).rjust(width)}: {lines[i]}" for i in range(len(lines)))


def build_prompt(src_text, dep_info, hot_info, loop_classes, refactor=False):
    hot_funcs = hot_info.get("hotspots", [])
    hot_str = "\n".join(
        f"  {h.get('name','?')}: self={h.get('self_time_ms',0):.1f}ms "
        f"({h.get('self_pct',0)}%) calls={h.get('calls',0)}"
        for h in hot_funcs if h.get("name")
    )
    # loop_classes come from the dependency analyzer (accurate) when available.
    # Each has: line, header, parallelizable (bool), is_reduction (bool).
    # Fall back to classify_loops shape (kind/reduction_vars) if no dep data.
    loop_str = "\n".join(
        f"  L{l.get('line')} {'SAFE' if l.get('parallelizable') or l.get('kind') in ('reduction','independent') else 'UNSAFE'} "
        f"{'reduction' if l.get('is_reduction') or l.get('kind')=='reduction' else 'independent' if l.get('parallelizable') or l.get('kind')=='independent' else 'sequential'} "
        f"red={l.get('reduction_vars', [])} | {l.get('header','')}"
        for l in loop_classes
    )
    numbered = _numbered_source(src_text)
    func_name = re.search(r'([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{', src_text)
    func_name = func_name.group(1) if func_name else 'UNKNOWN'
    if refactor:
        output_format = """OUTPUT FORMAT. This function has a loop-carried
dependency that pragma insertion alone cannot fix (indirect accumulation,
shared static scratch buffer, an unsafe loop with a parallelizable inner
loop, or a dependent outer loop with an independent middle loop needing
reordering). You must REFACTOR the function body to eliminate the dependency,
then add OpenMP pragmas. Return the COMPLETE refactored function inside a
single fenced ```c code block. Do NOT output INSERT lines.

Refactor rules:
- You may move declarations, add per-thread local arrays, rewrite seed or
  index computation, and add critical/single/barrier pragmas.
- You MUST keep the function signature (name, parameters, return type)
  unchanged.
- You MUST keep numerical results identical. Verification runs the full
  workload, so correctness is enforced by execution.
- Goal: eliminate the loop-carried dependency so the loop can run in a
  `#pragma omp for`, then add the pragma.
- Concrete refactor techniques:
  * Indirect accumulation (arr[data[i]]++): give each thread a private
    local array, parallelize the counting loop with `#pragma omp for`, then
    merge per-thread arrays into the shared one inside
    `#pragma omp critical`. If the local array is large (thousands of
    elements or more), allocate it with `malloc` inside the parallel region
    and `free` it after the merge, NOT as a stack array (stack overflow).
    Initialize it with a loop, not memset, unless the element type is bytes.
  * Shared static scratch with advancing seed: recompute each iteration's
    seed directly from the loop counter (not advancing a running seed) and
    make the scratch array a per-iteration local.
  * Unsafe loop with parallelizable inner loop: run the independent loop in
    `#pragma omp for`, keep sequential state outside the parallel region or
    under `#pragma omp single`.
  * Stencil nest (nested loops writing distinct array slices, e.g.
    arr[outer][inner] = f(arr[outer-1]...)): the outermost loop is
    parallelizable because each iteration writes a distinct slice. Move any
    scratch arrays (declared at function scope, e.g. `double r1[M]`) INSIDE
    the `#pragma omp parallel` region so each thread gets a private copy,
    then parallelize the outermost loop with `#pragma omp for`. Do NOT list
    scratch arrays in the `private` clause if you moved their declaration
    inside the region (they are already private). Do NOT delete their
    declaration. Variables used as inner loop counters or scratch indices
    (i2, i1, etc.) that are declared at function scope MUST be listed in
    the `#pragma omp parallel private(...)` clause or they race.
  * Recursive function (calls itself): the recursive calls are independent
    sub-problems. Wrap each recursive call in `#pragma omp task` and add
    `#pragma omp taskwait` after the calls to join. Add a cutoff: when the
    problem size is small (below a threshold), fall through to direct
    computation to avoid spawning tiny tasks. Use `firstprivate` for the
    arguments of each task so each task gets its own copy. The parallel
    region is opened by the caller, not inside this function.
  * Entry caller of a recursive function: this function calls a recursive
    callee that will spawn tasks. Open a parallel region with
    `#pragma omp parallel` followed by `#pragma omp single` (or
    `#pragma omp parallel single`), then call the recursive function once
    inside it. Do NOT add `#pragma omp task` here; the callee does that.
    Keep all non-recursive setup (allocation, factorization) outside the
    parallel region.
- CRITICAL THREAD-SAFETY: Inside a `#pragma omp parallel` region, any loop
  variable used in a per-thread loop (initializing a private array, merging
  in a critical section) MUST be a variable declared INSIDE the parallel
  region, NOT a variable declared outside it. A variable declared outside
  the parallel region is shared; using it as a loop counter in two
  per-thread loops races across threads and corrupts results. Declare a
  fresh local (e.g. `int li;`) inside the parallel region and use it for
  all per-thread loops. The `#pragma omp for` loop may reuse the outer
  variable because the pragma makes it private for that loop only.
- REDUCTION VARIABLES: If a scalar is accumulated in a loop and you
  parallelize that loop with `#pragma omp for reduction(+:v)` (or any
  reduction op), write the accumulation DIRECTLY to `v`. Do NOT introduce a
  per-thread `local_v` and write to that instead. The reduction clause
  already gives each thread a private copy of `v` and merges them at the
  end. Writing to `local_v` means the reduction never sees the values and
  the result is wrong (typically zero). The ONLY variables that need a
  per-thread local copy are array accumulators (e.g. `arr[idx]++` where
  `arr` is an array), which use a per-thread local array plus a
  `#pragma omp critical` merge. Scalar sums, max, min use the reduction
  clause directly, no local copy.
- Output ONLY the fenced code block containing the full refactored function.
  No explanation, no INSERT lines, no FUNCTION_NAME marker.
"""
    else:
        output_format = """OUTPUT FORMAT. You may ONLY insert new lines. You may NOT modify, delete,
reorder, or rename any existing line. Output a list of insertions, one per
line, in this exact format:

INSERT <line_number> <text to insert before that line>

Rules for insertions:
- <line_number> is the 1-indexed line BEFORE which the text is inserted.
- To insert a pragma before line 5: "INSERT 5 #pragma omp for reduction(+:sum)"
- To open a parallel region before line 5: "INSERT 5 #pragma omp parallel"
- To open the region block: "INSERT 5 {{"
- To close the region block after line 10: "INSERT 11 }}"
- Use a literal open brace {{ and close brace }} on their own INSERT lines to
  open and close a parallel region. Place the close brace AFTER the last line
  that should be inside the region.
- Group consecutive parallel loops inside ONE parallel region to avoid
  fork/join overhead. Open the region before the first loop, close it after
  the last loop. Use #pragma omp for (not parallel for) for loops inside.
- For a scalar computed between parallel loops that depends on prior loop
  results (e.g. alpha = rho0 / d), wrap that scalar assignment in
  #pragma omp single {{ }} so one thread computes it and the implicit barrier
  makes it visible to all threads.
- CRITICAL PLACEMENT: `#pragma omp for` must be inserted IMMEDIATELY BEFORE
  the `for (...)` header line, NOT inside the loop body. If the for header is
  on line 19, use "INSERT 19 #pragma omp for". Do NOT use the line number of
  a statement inside the loop body. The pragma and the for header must be
  adjacent lines after insertion.
- List every insertion on its own INSERT line. Output NOTHING except INSERT
  lines. No code blocks, no explanation, no FUNCTION_NAME marker.
"""
    return f"""You are an OpenMP optimization expert. Add OpenMP pragmas to the
C function below to maximize performance on a 4-thread Xeon. The result must
be numerically identical (verification must pass) and faster than serial.

HOTSPOT ANALYSIS (functions above the self-time threshold):
{hot_str}

The self-time threshold is {hot_info.get('self_time_threshold_ms','?')} ms.
Only the functions listed above are worth optimizing. The hottest is
{hot_info.get('hottest','?')}. Focus parallelization there.

LOOP CLASSIFICATION (expert rules, line numbers are 1-indexed):
{loop_str}

DEPENDENCY SUMMARY:
- functions: {dep_info['summary']['total_functions']}
- loops: {dep_info['summary']['total_loops']}
- parallelizable: {dep_info['summary']['parallelizable_loops']}
- reduction loops: {dep_info['summary']['reduction_loops']}

{EXPERT_RULES_TEXT}

TARGET FUNCTION (with 1-indexed line numbers):
{numbered}

{output_format}

FUNCTION: {func_name}
"""


# ---- post-processing: fix missing private clauses -------------------------

def strip_nowait(code):
    """Remove `nowait` clauses from `#pragma omp for` lines.

    The LLM sometimes adds nowait to amortize fork/join when several loops
    share one `#pragma omp parallel` region. nowait drops the implicit
    barrier between consecutive worksharing loops, so a later loop can read
    an array a prior loop is still writing (e.g. SP compute_rhs loop 1
    writes rho_i/us/vs/... that later loops read). That races and produces
    NaN. Proving inter-loop independence is hard for the LLM, so strip
    nowait unconditionally; the implicit barrier is always safe.
    """
    return re.sub(r"\bnowait\b\s*", "", code)


def strip_collapse(code):
    """Remove `collapse(N)` clauses emitted by the LLM.

    collapse(N) requires a PERFECTLY nested chain of N rectangular loops
    with a single leaf statement and no intervening code. The LLM
    frequently emits collapse(3)/collapse(4) on nests that are NOT perfect
    (sibling for-loops, declarations, or if-statements between levels), or
    lists a private() set whose count does not match N. A malformed
    collapse produces undefined OpenMP behavior including hangs (the
    runtime never converges the schedule) and wrong results. The benefit
    of correct collapse(2) is cache/load-balance, which plain `parallel
    for` on the outer loop already captures adequately at 16 threads; the
    risk of a wrong collapse outweighs it. Strip all collapse(N) so only
    the outer loop is parallelized.
    """
    return re.sub(r"\bcollapse\s*\(\s*\d+\s*\)\s*", "", code)


def fix_parallel_private_conflicts(code):
    """A variable used in a `reduction(+:X)` clause on an inner `omp for`
    must NOT appear in the enclosing `#pragma omp parallel private(...)`.
    gcc rejects this with "reduction variable is private in outer context".

    Scan each parallel region, collect its reduction variables from inner
    `omp for reduction(...)` lines, and strip them from the parallel
    private clause.
    """
    lines = code.splitlines()
    # find parallel region spans
    regions = []
    i = 0
    while i < len(lines):
        if re.match(r"\s*#pragma omp parallel\b", lines[i]):
            start = i
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                if j > i and depth <= 0:
                    break
                j += 1
            regions.append((start, j))
            i = j + 1
        else:
            i += 1
    # collect reduction vars per region
    for rs, re_ in regions:
        red_vars = set()
        for k in range(rs, re_ + 1):
            for m in re.finditer(r"reduction\s*\([^:]*:([^)]*)\)", lines[k]):
                for v in m.group(1).split(","):
                    red_vars.add(v.strip())
        if not red_vars:
            continue
        # strip them from the parallel private clause
        pm = re.search(r"private\s*\(([^)]*)\)", lines[rs])
        if not pm:
            continue
        priv = [v.strip() for v in pm.group(1).split(",")]
        new_priv = [v for v in priv if v not in red_vars]
        if new_priv != priv:
            new_clause = "private(" + ", ".join(new_priv) + ")"
            lines[rs] = re.sub(r"private\s*\([^)]*\)", new_clause, lines[rs])
    return "\n".join(lines)


def postfix_private_clauses(code):
    """Expert-rule post-processing: ensure every `#pragma omp for` whose
    body has an inner `for (k = ...)` lists `k` as private.

    LLMs frequently forget inner loop variables in private clauses, which
    causes data races and wrong numerical results. This is a deterministic
    fix that does not depend on the LLM getting it right.
    """
    lines = code.splitlines()
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"(\s*)#pragma omp for(\s+(.*))?$", line)
        if m:
            indent = m.group(1)
            tail = (m.group(3) or "").strip()
            # scan only the body of THIS loop: from the line after the
            # pragma, track brace depth, stop when the loop body closes.
            # This avoids picking up loop vars from a later sibling loop.
            body_lines = []
            depth = 0
            seen_for = False
            for j in range(i + 1, min(i + 30, len(lines))):
                ln = lines[j]
                depth += ln.count("{") - ln.count("}")
                if "for " in ln or "for(" in ln:
                    seen_for = True
                body_lines.append(ln)
                if seen_for and depth <= 0:
                    break
            ahead = "\n".join(body_lines)
            inner_vars = set(re.findall(r"for\s*\(\s*(\w+)\s*=", ahead))
            # the outer loop var is the first `for` after the pragma
            outer_match = re.search(r"for\s*\(\s*(\w+)\s*=", ahead)
            outer_var = outer_match.group(1) if outer_match else None
            # inner vars = all loop vars except the outer one
            inner = inner_vars - {outer_var} if outer_var else inner_vars
            # parse existing private vars
            priv_match = re.search(r"private\s*\(([^)]*)\)", tail)
            existing = set()
            if priv_match:
                existing = {v.strip() for v in priv_match.group(1).split(",")}
            # parse reduction vars: these MUST NOT be added to private
            # (a variable cannot be both reduction and private)
            red_match = re.search(r"reduction\s*\([^:]*:([^)]*)\)", tail)
            red_vars = set()
            if red_match:
                red_vars = {v.strip() for v in red_match.group(1).split(",")}
            needed = (inner - existing) - red_vars
            if needed:
                all_priv = sorted(existing | needed)
                # rebuild the clause
                if priv_match:
                    new_priv = "private(" + ", ".join(all_priv) + ")"
                    tail = re.sub(r"private\s*\([^)]*\)", new_priv, tail)
                else:
                    sep = " " if tail else ""
                    tail = tail + sep + "private(" + ", ".join(all_priv) + ")"
                line = f"{indent}#pragma omp for {tail}".rstrip()
                if not tail:
                    line = f"{indent}#pragma omp for private(" + ", ".join(sorted(needed)) + ")"
        out.append(line)
    return "\n".join(out)


def strip_preamble(code):
    """LLMs sometimes emit a natural-language preamble before the code.
    Keep only from the first `#include` line onward."""
    m = re.search(r"^[ \t]*#\s*include\b", code, re.MULTILINE)
    if m:
        return code[m.start():]
    return code


def single_to_redundant(code):
    """Convert `#pragma omp single` scalar computations into bare
    redundant computation (every thread computes it).

    When a parallel region declares alpha/beta as private (so every
    thread has its own copy), `#pragma omp single` is wrong: only one
    thread writes its private copy, the others read uninitialized
    values. The expert pattern is redundant computation. This rewrite
    unifies on the expert pattern and avoids the single/private mismatch
    that produces NaN.

    Handles both forms:
      #pragma omp single\n    { stmt; }
      #pragma omp single\n    stmt;
    """
    # form 1: single with braces. Preserve the statement's original indentation.
    pat1 = re.compile(
        r"([ \t]*)#pragma omp single\s*\n"
        r"\s*\{\s*\n"
        r"([ \t]*[^\n]+;)\s*\n"
        r"\s*\}\s*\n?",
        re.MULTILINE,
    )
    code = pat1.sub(r"\2\n", code)
    # form 2: single without braces, single statement on next line
    pat2 = re.compile(
        r"[ \t]*#pragma omp single\s*\n"
        r"([ \t]*[^\n{}]+;)\s*\n",
        re.MULTILINE,
    )
    code = pat2.sub(r"\1\n", code)
    return code


def fix_thread_report(code):
    """Wrap omp_get_num_threads() in a parallel master region so NPB reports
    the real thread count. Serial NPB sources call it outside any parallel
    region, which always reports 1. Skip calls already inside a parallel
    region (e.g. FT already wraps it correctly)."""
    lines = code.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if not re.search(r"nthreads\s*=\s*omp_get_num_threads\(\)", line):
            continue
        ctx = "".join(lines[max(0, i - 10):i])
        if re.search(r"#\s*pragma\s+omp\s+parallel\b(?!.*\bfor\b)", ctx) or "#pragma omp master" in ctx:
            continue
        replacement = "#pragma omp parallel\n  {\n#pragma omp master\n    nthreads = omp_get_num_threads();\n  }\n"
        lines[i] = replacement
        return "".join(lines)
    return code


def fix_pragma_placement(code):
    """Move misplaced `#pragma omp for` lines to immediately before the
    nearest `for (...)` header. The LLM sometimes inserts the pragma inside
    the loop body (using a body line number) instead of before the for header.
    A `#pragma omp for` must be directly above a `for` statement."""
    lines = code.splitlines(keepends=True)
    ws_re = re.compile(r"(\s*)#\s*pragma\s+omp\s+(for|parallel\s+for)\b")
    for_re = re.compile(r"\bfor\s*\(")
    i = 0
    while i < len(lines):
        m = ws_re.match(lines[i])
        if not m:
            i += 1
            continue
        indent = m.group(1)
        # check if the next non-empty line is a for header
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j < len(lines) and for_re.search(lines[j]):
            i += 1
            continue  # already correctly placed
        # find the nearest for header below (within 5 lines)
        for k in range(i + 1, min(i + 6, len(lines))):
            if for_re.search(lines[k]):
                # move the pragma to just before line k
                pragma = lines[i]
                del lines[i]
                # adjust k for deletion
                k -= 1
                lines.insert(k, pragma)
                break
        i += 1
    return "".join(lines)


def ensure_includes(code, src_text):
    """LLMs sometimes drop the project header that defines boolean/FALSE/
    TRUE. If the source had `#include "npb-C.h"` but the output does not,
    re-add it before npbparams.h."""
    if '#include "npb-C.h"' in code:
        return code
    # find what the original source included
    if '#include "npb-C.h"' in src_text:
        # insert before the first #include in the output
        m = re.search(r"^[ \t]*#\s*include\b", code, re.MULTILINE)
        if m:
            return '#include "npb-C.h"\n' + code[m.start():]
    return code


def parse_structured_candidate(raw, expected_name):
    """Extract one C function from LLM response. Tolerant of format drift."""
    raw = raw.strip()
    # FUNCTION_NAME marker is preferred but not required.
    name_matches = re.findall(r"(?m)^\s*FUNCTION_NAME:\s*([A-Za-z_]\w*)\s*$", raw)
    if name_matches and expected_name not in name_matches:
        raise RuntimeError("FUNCTION_NAME marker mismatched: " + ",".join(name_matches))
    blocks = re.findall(r"```(?:c|C)?\s*\n(.*?)\n```", raw, flags=re.S | re.I)
    if not blocks:
        # No fenced block: treat whole response as code (strip common preambles).
        code = strip_preamble(raw)
    elif len(blocks) == 1:
        code = blocks[0].strip()
    else:
        # Multiple blocks: pick the one containing the target function signature.
        sig = re.compile(r"\b" + re.escape(expected_name) + r"\s*\(")
        cand = [b for b in blocks if sig.search(b)]
        if len(cand) != 1:
            raise RuntimeError("ambiguous code blocks: " + str(len(blocks)))
        code = cand[0].strip()
    code = code.strip() + "\n"
    # Verify the target function signature appears.
    if not re.search(r"(?m)^\s*(?:[A-Za-z_][\w\s*]*\s+)?" + re.escape(expected_name) + r"\s*\([^;{}]*\)\s*\{", code) and \
       not re.search(r"\b" + re.escape(expected_name) + r"\s*\([^;{}]*\)\s*\{", code):
        raise RuntimeError("candidate function name mismatch")
    return code


def apply_patches(src_text, patch_text):
    """Apply INSERT <line> <text> patches to source. Returns modified source.

    Patches insert text BEFORE the given 1-indexed line. Multiple patches at
    the same line preserve their order. Line numbers refer to the ORIGINAL
    source (before any insertion), so we process in descending line order to
    avoid offset drift, grouping same-line patches in given order.
    """
    src_lines = src_text.splitlines()
    # Parse INSERT lines. Tolerate leading whitespace and optional braces.
    patches = []  # (line_number, text)
    for m in re.finditer(r"(?m)^\s*INSERT\s+(\d+)\s+(.*?)\s*$", patch_text):
        ln = int(m.group(1))
        text = m.group(2).strip()
        if not text:
            continue
        patches.append((ln, text))
    if not patches:
        raise RuntimeError("no INSERT patches parsed from LLM output")
    # Group by line number, preserve order within group.
    by_line = {}
    for ln, text in patches:
        by_line.setdefault(ln, []).append(text)
    # Apply in descending line order. Clamp line numbers to valid range.
    out = list(src_lines)
    for ln in sorted(by_line.keys(), reverse=True):
        idx = max(0, min(ln - 1, len(out)))
        block = by_line[ln]
        # Insert before line idx. Insert in reverse order so the listed order
        # is preserved in the output (later patches end up below earlier ones).
        for text in reversed(block):
            text = text.replace("{{", "{").replace("}}", "}")
            out[idx:idx] = [text]
    return "\n".join(out) + "\n"


def call_llm(prompt, model, src_text=None, max_tokens=None, expected_name=None):
    if OpenAI is None:
        raise RuntimeError("openai package is required for LLM transformation")
    if not API_KEY:
        raise RuntimeError("REPOOMP_API_KEY is required for LLM transformation")
    client = OpenAI(base_url=API_BASE, api_key=API_KEY, timeout=600)
    if max_tokens is None:
        max_tokens = max(4096, min(12288, len(prompt) // 2))
    chunks = []
    reasoning_chunks = []
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=max_tokens,
        stream=True,
        extra_body={"thinking": {"type": "disabled"}},
    )
    for event in stream:
        if not getattr(event, "choices", None):
            continue
        delta = event.choices[0].delta
        piece = getattr(delta, "content", None)
        if piece:
            chunks.append(piece)
        rpiece = getattr(delta, "reasoning_content", None)
        if rpiece:
            reasoning_chunks.append(rpiece)
    code = "".join(chunks).strip()
    if not code:
        code = "".join(reasoning_chunks).strip()
    if not code:
        raise RuntimeError("LLM returned empty candidate (stream)")
    # Patch mode: LLM returns INSERT lines. Apply to original target.
    if src_text is not None and re.search(r"(?m)^\s*INSERT\s+\d+", code):
        code = apply_patches(src_text, code)
        # post-processing identical to full-function path
        code = fix_pragma_placement(code)
        code = postfix_private_clauses(code)
        code = fix_parallel_private_conflicts(code)
        code = single_to_redundant(code)
        return code
    if expected_name:
        code = parse_structured_candidate(code, expected_name)
    if src_text is not None and len(code) > max(8192, len(src_text) * 4):
        raise RuntimeError("LLM candidate exceeds 4x target function length")
    else:
        code = re.sub(r"^```c\n", "", code)
        code = re.sub(r"\n```$", "", code)
        code = strip_preamble(code)
    # re-add dropped project headers (boolean/FALSE/TRUE live in npb-C.h)
    if src_text is not None:
        code = ensure_includes(code, src_text)
    # fix misplaced #pragma omp for lines (LLM puts them in loop body)
    code = fix_pragma_placement(code)
    # expert-rule post-processing: fix missing private clauses for inner
    # loop variables (common LLM mistake that causes data races)
    code = postfix_private_clauses(code)
    # fix reduction vars wrongly placed in parallel private clause
    code = fix_parallel_private_conflicts(code)
    # convert omp single to redundant computation (avoids single/private
    # mismatch when alpha/beta are declared private)
    code = single_to_redundant(code)
    return code


def _compile_check(src_path, include_dirs=None):
    """Return gcc exit code for a syntax-only compile. 0 = ok.

    NPB IS serial sources declare `main( argc, argv )` without a return
    type and call c_print_results without a prototype. The run_all
    npb_build step patches these before make; this gate must apply the
    same patches so it does not reject valid IS candidates that make
    would accept. We detect the IS shape (bare `main(` + a
    c_print_results call) and prepend the forward declarations.
    """
    import shutil
    import subprocess
    import tempfile
    cc = shutil.which("gcc") or "gcc"
    inc = []
    if include_dirs:
        for d in include_dirs:
            inc.append("-I" + d)
    text = Path(src_path).read_text(errors="replace") if src_path else ""
    patched = text
    if re.search(r"(?m)^main\(\s*argc\s*,\s*argv\s*\)", patched) and \
       re.search(r"\bc_print_results\s*\(", patched):
        declarations = (
            'void timer_clear(int);\nvoid timer_start(int);\n'
            'void timer_stop(int);\ndouble timer_read(int);\n'
            'void c_print_results(char *, char, int, int, int, int, int, '
            'double, double, char *, int, char *, char *, char *, char *, '
            'char *, char *, char *, char *, char *);\n'
        )
        patched = declarations + re.sub(
            r"^main\(\s*argc\s*,\s*argv\s*\)", "int main( argc, argv )",
            patched, count=1, flags=re.M,
        )
    if patched != text:
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False, mode="w") as tf:
            tf.write(patched)
            check_src = tf.name
        cleanup_src = True
    else:
        check_src = src_path
        cleanup_src = False
    with tempfile.NamedTemporaryFile(suffix=".o", delete=False) as tf:
        out = tf.name
    cmd = [cc, "-c", "-O0", "-fopenmp"] + inc + [check_src, "-o", out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(out)
    except OSError:
        pass
    if cleanup_src:
        try:
            os.remove(check_src)
        except OSError:
            pass
    return p.returncode


# ---- function scope --------------------------------------------------------

def extract_function_ranges(source_text, file=""):
    """Extract stable function records with 1-indexed inclusive ranges."""
    try:
        from ..dependency_analysis.dependency_analyzer import function_spans
    except ImportError:
        try:
            from dependency_analysis.dependency_analyzer import function_spans
        except ImportError:
            _method_dir = str(Path(__file__).resolve().parents[1])
            if _method_dir not in sys.path:
                sys.path.insert(0, _method_dir)
            from dependency_analysis.dependency_analyzer import function_spans
    return function_spans(source_text, file)


def match_hotspots(records, hot_info, match_line=True, match_file=True):
    hotspots = hot_info.get("hotspots", []) if isinstance(hot_info, dict) else []
    selected = []
    for record in records:
        matches = []
        for hot in hotspots:
            if hot.get("name") != record["name"]: continue
            if match_file and hot.get("file") and hot["file"] != record.get("file"): continue
            if match_line and hot.get("line") and hot["line"] != record.get("line"):
                continue
            matches.append(hot)
        if len(matches) == 1:
            selected.append(dict(record, hotspot=matches[0]))
        elif len(matches) > 1 and not match_line:
            selected.append(dict(record, hotspot=matches[0]))
    return selected


def select_batches(records, dependency_matrix=None):
    try:
        from ..dependency_analysis.dependency_analyzer import independent_batches
    except ImportError:
        try:
            from dependency_analysis.dependency_analyzer import independent_batches
        except ImportError:
            _method_dir = str(Path(__file__).resolve().parents[1])
            if _method_dir not in sys.path:
                sys.path.insert(0, _method_dir)
            from dependency_analysis.dependency_analyzer import independent_batches
    return independent_batches(records, dependency_matrix)


def merge_function_ranges(source_text, replacements, records):
    """Merge function replacements in reverse source order.

    Re-resolves each function's line range in the CURRENT source_text by
    name, instead of trusting record["line"]/["end_line"]. Those come from
    dep analysis of the original source, but by merge time the source may
    have shifted lines (the rules candidate inserts pragmas; _fix_thread_report
    adds a parallel region). Stale line numbers caused merge to cut at the
    wrong place, duplicating braces and producing compile-fail-merged.
    """
    try:
        from ..dependency_analysis.dependency_analyzer import function_spans
    except ImportError:
        try:
            from dependency_analysis.dependency_analyzer import function_spans
        except ImportError:
            _method_dir = str(Path(__file__).resolve().parents[1])
            if _method_dir not in sys.path:
                sys.path.insert(0, _method_dir)
            from dependency_analysis.dependency_analyzer import function_spans
    current_spans = {s["name"]: s for s in function_spans(source_text)}
    lines = source_text.splitlines(True)
    by_name = {r["name"]: text for r, text in replacements}
    # process in reverse order of CURRENT line so earlier edits don't shift
    # later line indices
    ordered = sorted(
        ((name, current_spans[name]) for name in by_name if name in current_spans),
        key=lambda kv: kv[1]["line"], reverse=True,
    )
    for name, span in ordered:
        replacement = by_name[name]
        if not replacement.endswith("\n"): replacement += "\n"
        lines[span["line"] - 1:span["end_line"]] = [replacement]
    return "".join(lines)


def autofix_private(candidate):
    """Inject missing scalar temporaries into #pragma omp ... for private(...).

    The LLM often lists some body-assigned scalars in private() but omits
    others (e.g. lists fac1 but forgets fac2 in the same loop). A scalar
    assigned inside a parallel-for body that is declared in the function but
    absent from private races across threads. Since such a scalar is written
    and read within one iteration (no cross-iteration accumulation, else the
    dep analyzer would have marked the loop unsafe), making it private is
    always the correct fix. This auto-injects those missing names so a
    one-variable omission does not discard an otherwise-valid candidate.

    Only scalar temporaries declared in the function are injected. Array
    names, reduction accumulators (already caught), and loop variables
    (auto-private) are skipped.
    """
    if not candidate:
        return candidate
    lines = candidate.splitlines(keepends=True)
    # scalar declaration regex: `double fac1, fac2;` etc.
    scalar_decl = set()
    for ln in lines:
        m = re.match(r"\s*(?:static\s+)?(?:int|double|float|long|short|unsigned|size_t|char)\s+([^;]+);", ln)
        if not m:
            continue
        for nm in re.findall(r"\b([A-Za-z_]\w*)\b(?:\s*(?:=[^,;]*)?)?(?:,|$)", m.group(1)):
            # skip pointers and arrays (those have * or [ in the decl token)
            scalar_decl.add(nm)
    # Only fix `#pragma omp for` and `#pragma omp parallel for` (worksharing
    # loops). NEVER touch a bare `#pragma omp parallel private(...)` region:
    # its body spans many loops including reduction loops, so scanning it
    # collects reduction accumulators (sx, sy) and injects them into the
    # parallel private clause, which gcc rejects ("reduction variable is
    # private in outer context"). The parallel clause is the LLM's job.
    pragma_re = re.compile(r"^(\s*#\s*pragma\s+omp\s+(?:parallel\s+)?for\s+)(.*private\s*\(([^)]*)\))(.*)$")
    out = []
    i = 0
    while i < len(lines):
        m = pragma_re.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        # collect private vars from this pragma line (may span continuation)
        priv = set(v.strip() for v in m.group(3).split(",") if v.strip())
        # also handle a following private(...) on a continuation line
        # scan the for body for assigned scalars until the loop's closing brace
        depth = 0; started = False
        assigned = set()
        j = i + 1
        # find the for header to get outer var + inner loop vars
        outer_var = None
        inner_loop_vars = set()
        while j < len(lines):
            bd = lines[j].count("{") - lines[j].count("}")
            depth += bd
            for fm in re.finditer(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", lines[j]):
                if outer_var is None:
                    outer_var = fm.group(1)
                else:
                    inner_loop_vars.add(fm.group(1))
            for am in re.finditer(r"\b([A-Za-z_]\w*)\s*=(?!=)", lines[j]):
                assigned.add(am.group(1))
            if "{" in lines[j]:
                started = True
            if started and depth <= 0:
                break
            j += 1
        # reduce-clause vars are NOT private; detect reduction(...) on pragma
        reduction_vars = set()
        rm = re.search(r"reduction\s*\(([^)]*)\)", m.group(2))
        if rm:
            for rpart in rm.group(1).split(","):
                rpart = rpart.strip()
                # form op:var or op:list
                for rv in re.findall(r"[A-Za-z_]\w*", rpart):
                    if rv not in ("+", "-", "*", "&", "|", "^", "min", "max"):
                        reduction_vars.add(rv)
        missing = set()
        for v in assigned:
            if v in priv: continue
            if v == outer_var: continue  # parallelized loop var, auto-private
            if v in reduction_vars: continue  # reduction vars handled separately
            if v not in scalar_decl: continue
            # inner loop variables (j, k, m in nested for) and scalar
            # temporaries (fac1, fac2) assigned in the body must all be
            # private when the outer loop is parallelized. The LLM often
            # lists some but omits others in the same clause.
            missing.add(v)
        if not missing:
            out.append(lines[i]); i += 1; continue
        # inject missing into the private() clause
        new_priv = ", ".join(sorted(priv | missing))
        prefix = m.group(1)
        # rebuild: everything up to private(...) then new list then rest.
        # Find the private(...) clause's OWN close paren, not the first ')'
        # on the line (which may belong to an earlier reduction(...) clause
        # and would leave a stale duplicate `private(i)` tail).
        clause_tail = m.group(2)
        priv_start = clause_tail.index("private")
        # the close paren is the first ')' at or after the private( opening
        priv_open = clause_tail.index("(", priv_start)
        priv_close = clause_tail.index(")", priv_open)
        before_priv = clause_tail[:priv_start]
        rest_after = clause_tail[priv_close + 1:]
        new_line = f"{prefix}{before_priv}private({new_priv}){rest_after}{m.group(4)}"
        # preserve original line ending
        if not new_line.endswith("\n"):
            new_line += "\n" if lines[i].endswith("\n") else ""
        out.append(new_line)
        i += 1
    return "".join(out)


def _has_only_call_seed_loops(record):
    """True when every parallelizable loop of the function advances a scalar
    seed through a function call (e.g. `randlc(&seed, ...)`).

    Such loops are marked parallelizable by the analyzer (each iteration
    writes a distinct array element) but carry a true cross-iteration
    dependency: the seed scalar is passed by address to a PRNG whose next
    output depends on the previous. Parallelizing races on the seed and
    produces wrong results. The dependency cannot be refactored away (the
    PRNG sequence is inherently serial), so the function must stay serial.

    Generalizes to any loop whose body calls a function with a `&scalar`
    argument where the scalar is not reset each iteration.
    """
    loops = record.get("loops", [])
    body = record.get("text") or ""
    par_loops = [l for l in loops if l.get("parallelizable")]
    if not par_loops:
        return False
    # a function call passing a scalar by address (e.g. randlc(&seed, &a)).
    # the & must be a single ampersand (not &&), so require it to not be
    # preceded by another & and to be followed by optional space then a name.
    call_seed = re.compile(r"\b[A-Za-z_]\w*\s*\([^)]*(?<!&)&\s*[A-Za-z_]\w*[^)]*\)")
    for loop in par_loops:
        # approximate loop body as text from header onward
        if not call_seed.search(body):
            return False
    # all parallelizable loops have a &scalar call -> cannot parallelize
    return True


def _should_refactor(record, src_text, dep_info=None):
    """Decide whether a function should use refactor mode (full-function
    rewrite) instead of INSERT mode.

    Refactor mode triggers on structural signals that pragma insertion
    cannot fix: indirect accumulation (arr[data[i]]++), shared static
    scratch buffer with an advancing seed, or an unsafe-loop blocker with
    at least one parallelizable loop. These generalize to any function with
    the same shape, not just IS/FT.

    Returns (bool, reason).
    """
    loops = record.get("loops", [])
    blockers = record.get("blockers", [])
    body = record.get("text") or ""
    # Signal 1: indirect accumulation in any loop body. Reuse the
    # rule_transformer detector so detection stays consistent with the
    # rules path (which skips these loops for the LLM to handle).
    try:
        from .rule_transformer import _has_indirect_accumulation
    except ImportError:
        try:
            from rule_transformer import _has_indirect_accumulation
        except ImportError:
            _pa_dir = str(Path(__file__).resolve().parent)
            if _pa_dir not in sys.path:
                sys.path.insert(0, _pa_dir)
            from rule_transformer import _has_indirect_accumulation
    # Scan each loop body for indirect accumulation. We approximate the
    # loop body by the text from the loop header to the function end.
    for loop in loops:
        loop_var = re.search(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", loop.get("header", ""))
        loop_var = loop_var.group(1) if loop_var else ""
        if loop_var and _has_indirect_accumulation(body, loop_var):
            return True, "indirect-accumulation"
    # Signal 1b: data-dependent index accumulation. A loop accumulates into
    # an array element whose index is a scalar computed in the body (not the
    # loop variable, not a nested array access). Different iterations can map
    # to the same element, so parallelizing races. Example: ep
    # qq[l] += 1.0 where l = max(fabs(t3), fabs(t4)). Needs per-thread local
    # array + critical merge (aaai ep style).
    for loop in loops:
        loop_var = re.search(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", loop.get("header", ""))
        loop_var = loop_var.group(1) if loop_var else ""
        if not loop_var:
            continue
        # find arr[idx] += or arr[idx]++ where idx is a bare name (not the
        # loop var) that is assigned in the body
        for m in re.finditer(r"([A-Za-z_]\w*)\s*\[\s*(\w+)\s*\]\s*(?:\+\+|--|\+=|-=|\*=|/=)", body):
            arr, idx = m.group(1), m.group(2)
            if idx == loop_var:
                continue
            # idx is data-dependent if it is assigned in the body (not a
            # loop counter, not a parameter read-only)
            if re.search(r"(?m)^\s*(?:int\s+|double\s+|float\s+|long\s+|short\s+|size_t\s+|INT_TYPE\s+)?"
                         + re.escape(idx) + r"\s*=(?!=)", body):
                return True, "data-dependent-index-accumulation"
    # Signal 2: shared static scratch buffer written inside a loop. A
    # `static` array written via a pointer-passing call (vranlc/randlc)
    # whose seed advances across iterations is the FT compute_initial
    # shape. The rules path (Pattern 4) handles it deterministically;
    # refactor mode is the LLM fallback when rules did not fire.
    if re.search(r"\bstatic\s+\w+\s+\w+\s*\[", body) and \
       re.search(r"\b(?:vranlc|randlc|ipow46)\s*\(", body):
        return True, "static-scratch-seed"
    # Signal 3: unsafe-loop blocker with at least one parallelizable loop.
    # The analyzer flagged the function unsafe (could not prove all loops
    # safe), but an inner loop is genuinely parallelizable. Refactor mode
    # lets the LLM restructure to expose the safe loop.
    if "unsafe-loop" in blockers and any(l.get("parallelizable") for l in loops):
        return True, "unsafe-loop-with-parallelizable"
    # Signal 3b: unsafe-loop blocker with nested loops (2+ deep) but none
    # marked parallelizable. The analyzer is conservative when the body
    # calls helper functions (binvcrhs, matvec_sub) it cannot prove safe.
    # But a nest of 2+ loops where one has a cross-iteration dependency
    # and the other is independent can be parallelized by loop reordering
    # (SP/BT/LU solver cells). Let the LLM attempt the refactor.
    if "unsafe-loop" in blockers and len(loops) >= 2:
        return True, "unsafe-loop-nested-reorder"
    # Signal 4: recursive function (calls itself). These have 0
    # parallelizable loops but are parallelizable via #pragma omp task on
    # the recursive calls (BOTS pattern: fib, nqueens, fft, strassen).
    calls = record.get("calls", [])
    if record.get("name") in calls:
        return True, "recursive-task"
    # Signal 5: entry caller of a recursive function. This function calls a
    # recursive callee (which will get task pragmas). It must open the
    # #pragma omp parallel + single region and call the recursive function
    # once inside it. Without this, the tasks have no parallel region to run in.
    func_calls_map = {}
    try:
        func_calls_map = dep_info.get("function_calls", {})
    except Exception:
        pass
    my_callees = func_calls_map.get(record.get("name", ""), [])
    for callee in my_callees:
        callee_calls = func_calls_map.get(callee, [])
        if callee in callee_calls:  # callee is recursive
            return True, "task-entry-caller"
    # Signal 6: stencil-nest. A function with an unsafe-loop blocker whose
    # body has 2+ nested for loops where the outermost loop writes a distinct
    # array slice (arr[loopvar][...] = ...). The analyzer marks these unsafe
    # because the body has inner loops and reads, but the outer loop is
    # genuinely parallelizable (each iteration writes a distinct slice, like
    # mg psinv/resid/rprj3/interp). Refactor mode lets the LLM move scratch
    # arrays per-thread and parallelize the outer loop.
    if "unsafe-loop" in blockers:
        body_text = body
        # count nested for loops
        n_for = len(re.findall(r"\bfor\s*\(", body_text))
        if n_for >= 2:
            # check the outermost loop writes an array element indexed by
            # its loop variable (distinct slice per iteration)
            for loop in loops:
                lv = re.search(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", loop.get("header", ""))
                if not lv:
                    continue
                var = lv.group(1)
                # arr[var]... =  or arr[expr(var)]... =  in the loop body
                write_re = re.compile(
                    r"\b[A-Za-z_]\w*\s*\[[^\]]*\b" + re.escape(var) + r"\b[^\]]*\][^\]]*\](?:\[[^\]]*\])*\s*=")
                if write_re.search(body_text):
                    return True, "stencil-nest"
            # Signal 7: reduction-nest. A nested loop that accumulates into a
            # scalar (s += ... or s = s + ... or tmp = max(tmp, ...)) across
            # all iterations. The analyzer marks it unsafe (cross-iteration
            # scalar dep) but it is a standard reduction parallelizable with
            # collapse + reduction clause (mg norm2u3: s = s + r*r,
            # if (a > tmp) tmp = a).
            red_re = re.compile(r"(\w+)\s*(\+=|-=|\*=|/=)\s*")
            red_eq = re.compile(r"(\w+)\s*=\s*\1\s*([+\-*/])")
            max_re = re.compile(r"if\s*\([^)]*\b(\w+)\s*[<>]\s*(\w+)\b[^)]*\)\s*\2\s*=")
            if red_re.search(body_text) or red_eq.search(body_text) or max_re.search(body_text):
                return True, "reduction-nest"
    return False, ""


def validate_candidate(original, candidate, record, refactor=False):
    """Allow only OpenMP additions inside one unchanged function.

    original and candidate are both single-function text (target scope).
    The candidate may be longer than the original because pragmas add lines,
    so we compare function bodies via extract_function_ranges rather than
    fixed line numbers.

    When `refactor` is True, the LLM is allowed to rewrite the function body
    to eliminate loop-carried dependencies. The line-by-line non-openmp-edit
    check is skipped; correctness is enforced by the compile check (run after
    merge) and the run_all workload verification. Structural guards still
    apply: signature unchanged, single function, brace balance, and valid
    OpenMP nesting.
    """
    if not candidate or candidate == original: return False, "identity"
    name = record["name"]
    old_funcs = extract_function_ranges(original, record.get("file", ""))
    new_funcs = extract_function_ranges(candidate, record.get("file", ""))
    old_match = [x for x in old_funcs if x["name"] == name]
    new_match = [x for x in new_funcs if x["name"] == name]
    if len(old_match) != 1 or len(new_match) != 1:
        return False, "missing-or-ambiguous-function"
    # Reject extra functions introduced by the LLM.
    if len(new_funcs) != len(old_match):
        return False, "extra-functions"
    old_body = old_match[0]["text"]
    new_body = new_match[0]["text"]
    # Refactor mode: verify the function signature is unchanged (name,
    # parameter list, return type). The body may differ. We extract the
    # signature as the text up to the opening brace of the function body.
    if refactor:
        def _signature(text):
            m = re.search(r"^[^{]*\{", text, re.MULTILINE | re.DOTALL)
            sig = m.group(0).rstrip("{ \t\n") if m else text.split("{", 1)[0]
            # normalize trailing whitespace so cosmetic diffs don't reject
            return re.sub(r"\s+", " ", sig).strip()
        if _signature(old_body) != _signature(new_body):
            return False, "signature-changed"
    # Strip pragma lines from both, then compare non-brace lines in order.
    # The LLM may add standalone { and } lines to open/close parallel regions;
    # those are allowed. Every other line must match the original exactly.
    def _strip_pragma(text):
        out = []
        for line in text.splitlines():
            if re.match(r"\s*#\s*pragma\s+omp", line):
                continue
            out.append(line)
        return out
    old_lines = _strip_pragma(old_body)
    new_lines = _strip_pragma(new_body)
    # Brace balance check: after removing pragmas, the net brace depth change
    # must match. A mismatched brace means the LLM broke the function structure
    # (e.g. closed the function early, leaving code outside it).
    def _brace_depth(text):
        depth = 0
        for ch in text:
            if ch == "{": depth += 1
            elif ch == "}": depth -= 1
        return depth
    if _brace_depth("\n".join(old_lines)) != _brace_depth("\n".join(new_lines)):
        return False, "brace-imbalance"
    # Check for invalid OpenMP nesting: a work-sharing `#pragma omp for` must
    # not be directly nested inside another `#pragma omp for` (without an
    # intervening `#pragma omp parallel`). This is a common LLM error that
    # causes "work-sharing region may not be closely nested" compile errors.
    ws_re = re.compile(r"\s*#\s*pragma\s+omp\s+(for|parallel\s+for)\b")
    par_re = re.compile(r"\s*#\s*pragma\s+omp\s+parallel\b")
    single_re = re.compile(r"\s*#\s*pragma\s+omp\s+single\b")
    barrier_re = re.compile(r"\s*#\s*pragma\s+omp\s+barrier\b")
    for_re = re.compile(r"\bfor\s*\(")
    depth = 0  # work-sharing nesting depth (1 = inside a for body)
    par_brace = 0  # brace depth since entering parallel region
    in_parallel = False
    just_entered = False  # skip brace check on the pragma line itself
    for line in new_body.splitlines():
        # `#pragma omp parallel for` is combined parallel+work-sharing: it
        # opens a parallel region AND marks the next for as work-sharing. Treat
        # it like `#pragma omp for` (depth=1) so the for body's inner loops are
        # allowed. A bare `#pragma omp parallel` (no `for`) only opens a region.
        combined_re = re.compile(r"\s*#\s*pragma\s+omp\s+parallel\s+for\b")
        bare_par_re = re.compile(r"\s*#\s*pragma\s+omp\s+parallel\b(?!.*\bfor\b)")
        if combined_re.match(line):
            depth = 1
            par_brace = 0
            in_parallel = True
            just_entered = True
        elif bare_par_re.match(line):
            depth = 0
            par_brace = 0
            in_parallel = True
            just_entered = True
        elif single_re.match(line):
            # `single` may not be closely nested inside a work-sharing for
            # body (OpenMP forbids it; gcc errors out). A bare `parallel`
            # region (depth 0) is the only valid parent. Inside `single`,
            # loops are allowed, so reset depth to 0.
            if depth > 0:
                return False, "single-in-work-sharing"
            depth = 0  # single resets, loop inside single is ok
        elif barrier_re.match(line):
            # `barrier` likewise may not be closely nested inside a
            # work-sharing for body.
            if depth > 0:
                return False, "barrier-in-work-sharing"
        elif ws_re.match(line):
            if depth > 0:
                return False, "nested-work-sharing"
            depth = 1  # entering a work-sharing for body
        elif for_re.search(line) and in_parallel and depth == 0 and not refactor:
            # In INSERT mode, a bare `for` inside a parallel region (without
            # `#pragma omp for`) runs redundantly on all threads and races on
            # shared cross-iteration state. In refactor mode the LLM may
            # legitimately place a per-thread loop (writing thread-private
            # memory) inside a parallel region; the workload verify catches
            # true redundant-execution bugs, so we do not block here.
            return False, "redundant-loop-in-parallel"
        # track braces: when a work-sharing for body closes, reset depth
        if in_parallel:
            par_brace += line.count("{") - line.count("}")
            if just_entered:
                just_entered = False
                # the pragma line has no brace; wait for the next line
            else:
                if depth > 0 and line.count("}") > 0 and par_brace <= 1:
                    depth = 0
                if par_brace <= 0:
                    in_parallel = False
                    depth = 0
    # Refactor mode skips the line-by-line non-openmp-edit check. The body is
    # expected to differ; correctness is enforced by compile + workload verify.
    # But we still catch one common LLM bug that compile-check cannot: a loop
    # variable used inside a `#pragma omp for` body that is declared OUTSIDE
    # the parallel region (thus shared) and not listed in the for's private
    # clause. This races across threads. The LLM often declares fresh per-
    # thread variables (e.g. i3p) but forgets to use them, leaving the real
    # loop index (i3) shared.
    if refactor:
        # Collect variables declared inside each parallel region (these are
        # automatically private). Collect the for's private-clause vars too.
        # Then scan the for body for scalar loop-index-like usage of variables
        # declared outside the region.
        lines_n = new_body.splitlines()
        # Track declarations: a var declared at brace depth <= the parallel
        # region's opening depth is shared.
        # Simpler heuristic: find `#pragma omp for private(...)` lines, parse
        # their private vars, then check the for body for assignments to vars
        # that are (a) used as loop counters in inner for loops, (b) not in the
        # private clause, and (c) not declared inside the parallel region.
        # Parse parallel-region-scoped declarations.
        par_decl_vars = set()  # vars declared inside any parallel region
        par_priv_vars = set()  # vars in any #pragma omp parallel private(...)
        in_par = False
        par_depth = 0
        brace_depth = 0
        for ln in lines_n:
            if re.match(r"\s*#\s*pragma\s+omp\s+parallel\b", ln):
                in_par = True
                par_depth = brace_depth
                # collect private clause on the parallel pragma itself
                pm = re.search(r"private\s*\(([^)]*)\)", ln)
                if pm:
                    par_priv_vars.update(re.findall(r"\b([A-Za-z_]\w*)\b", pm.group(1)))
            # collect `int x, y, z;` and `double x[M];` declarations
            for m in re.finditer(r"\b(?:int|double|float|long|short|unsigned|size_t|char)\s+([^;]+);", ln):
                for name in re.findall(r"\b([A-Za-z_]\w*)\b", m.group(1)):
                    if in_par and brace_depth > par_depth:
                        par_decl_vars.add(name)
            brace_depth += ln.count("{") - ln.count("}")
            if in_par and brace_depth <= par_depth:
                in_par = False
        # Check each `#pragma omp for` for shared loop-index usage.
        for i, ln in enumerate(lines_n):
            m = re.match(r"\s*#\s*pragma\s+omp\s+(?:parallel\s+)?for\b(.*)", ln)
            if not m:
                continue
            # parse private and reduction clauses (both make vars per-thread)
            priv = set()
            pm = re.search(r"private\s*\(([^)]*)\)", m.group(1))
            if pm:
                priv = set(re.findall(r"\b([A-Za-z_]\w*)\b", pm.group(1)))
            rm = re.findall(r"reduction\s*\([^)]*:([^)]*)\)", m.group(1))
            for rgroup in rm:
                priv.update(re.findall(r"\b([A-Za-z_]\w*)\b", rgroup))
            # the for header is on the next line(s); find inner for loops
            # and their loop variables in the body until the for closes.
            # Collect loop vars of inner for loops in this for's body.
            # Skip the FIRST for header (that is the pragma's own loop, whose
            # counter is auto-private in OpenMP).
            inner_loop_vars = set()
            # scan forward until brace balance returns
            bd = 0
            started = False
            seen_first_for = False
            single_stmt_body = False  # for-loop body has no braces
            for j in range(i + 1, len(lines_n)):
                bd += lines_n[j].count("{") - lines_n[j].count("}")
                for fm in re.finditer(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", lines_n[j]):
                    if not seen_first_for:
                        seen_first_for = True
                        # detect single-statement body: for header line has
                        # no opening brace. The body is the next line only.
                        if "{" not in lines_n[j]:
                            single_stmt_body = True
                        continue  # pragma's own loop, auto-private
                    inner_loop_vars.add(fm.group(1))
                if started and bd <= 0:
                    break
                if "{" in lines_n[j]:
                    started = True
                # single-statement body: stop after the one body line
                if single_stmt_body and seen_first_for and j > i + 1:
                    break
            # an inner loop var that is not private and not declared in the
            # parallel region is shared -> race
            for v in inner_loop_vars:
                if v not in priv and v not in par_decl_vars:
                    return False, f"shared-loop-index({v})"
            # Find the outer loop variable (the pragma's own for counter).
            # It is auto-private in OpenMP, so skip it in the scalar check.
            outer_var = None
            for j in range(i + 1, min(i + 5, len(lines_n))):
                fm = re.search(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", lines_n[j])
                if fm:
                    outer_var = fm.group(1)
                    break
            # Also check for shared scalar temporaries assigned inside the
            # for body. A variable assigned (`v = ...`, not `v ==`) inside
            # the for body that is declared outside the parallel region and
            # not in the private clause races across threads. This catches
            # the common LLM bug of declaring fresh per-thread names (i3p)
            # but still using the original shared names (i3) in the body.
            assigned = set()
            bd2 = 0
            started2 = False
            single_stmt2 = False
            seen_for2 = False
            for j in range(i + 1, len(lines_n)):
                bd2 += lines_n[j].count("{") - lines_n[j].count("}")
                for fm in re.finditer(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", lines_n[j]):
                    if not seen_for2:
                        seen_for2 = True
                        if "{" not in lines_n[j]:
                            single_stmt2 = True
                for am in re.finditer(r"\b([A-Za-z_]\w*)\s*=(?!=)", lines_n[j]):
                    assigned.add(am.group(1))
                if started2 and bd2 <= 0:
                    break
                if "{" in lines_n[j]:
                    started2 = True
                if single_stmt2 and seen_for2 and j > i + 1:
                    break
            for v in assigned:
                if v in priv or v in par_decl_vars or v in par_priv_vars:
                    continue
                if v in inner_loop_vars or v == outer_var:
                    continue  # loop vars, auto-private or already checked
                # is it declared outside the parallel region? check the
                # original function's declarations (old_body) for a scalar
                # declaration of v.
                if re.search(r"\b(?:int|double|float|long|short|unsigned|size_t|char)\s+[^;]*\b" + re.escape(v) + r"\b[^;]*;", old_body):
                    return False, f"shared-scalar-in-for({v})"
        # Detect shared-array accumulation races: a `#pragma omp for` body
        # does `arr[idx]++` or `arr[idx] += ...` where `arr` is a shared
        # array (declared outside the parallel region, not a per-thread
        # local). This races across threads. The correct pattern uses a
        # per-thread local array + `#pragma omp critical` merge. If the
        # candidate has a local array declared inside the parallel region
        # AND a critical section, it is safe. Otherwise reject.
        for i, ln in enumerate(lines_n):
            m = re.match(r"\s*#\s*pragma\s+omp\s+(?:parallel\s+)?for\b", ln)
            if not m:
                continue
            # scan the for body for arr[idx]++ or arr[idx] +=
            bd3 = 0
            started3 = False
            single_stmt3 = False
            seen_for3 = False
            shared_acc = set()
            for j in range(i + 1, len(lines_n)):
                bd3 += lines_n[j].count("{") - lines_n[j].count("}")
                for fm in re.finditer(r"for\s*\(\s*(?:int\s+)?(\w+)\s*=", lines_n[j]):
                    if not seen_for3:
                        seen_for3 = True
                        if "{" not in lines_n[j]:
                            single_stmt3 = True
                # arr[idx]++ or arr[idx] +=  (idx may be data-dependent,
                # may have nested brackets like arr[key[i]])
                for am in re.finditer(r"\b([A-Za-z_]\w*)\s*\[.*?\]\s*(?:\+\+|--|\+=|-=|\*=|/=)", lines_n[j]):
                    shared_acc.add(am.group(1))
                if started3 and bd3 <= 0:
                    break
                if "{" in lines_n[j]:
                    started3 = True
                if single_stmt3 and seen_for3 and j > i + 1:
                    break
            # check each accumulated array: is it shared (declared outside
            # the parallel region) and not protected by a local copy +
            # critical?
            has_critical = any("critical" in l for l in lines_n)
            for arr in shared_acc:
                if arr in par_decl_vars:
                    continue  # declared inside parallel region = per-thread
                if has_critical and arr in par_decl_vars:
                    continue
                # is it declared outside (shared)? check old_body for any
                # declaration of arr as an array (any type, including
                # typedef'd types like INT_TYPE, LOGICAL, etc.)
                if re.search(r"\b\w+\s+\*?\s*" + re.escape(arr) + r"\s*\[", old_body):
                    # shared array accumulated in a for without a per-thread
                    # local copy of the SAME name -> race
                    if arr not in par_decl_vars:
                        return False, f"shared-array-race({arr})"
        return True, "accepted-refactor"
    # Filter to non-brace-only lines for comparison. A brace-only line is
    # one whose stripped content is exactly { or }.
    def _non_brace(lines):
        return [l for l in lines if l.strip() not in ("{", "}")]
    old_nb = _non_brace(old_lines)
    new_nb = _non_brace(new_lines)
    if old_nb != new_nb:
        return False, "non-openmp-edit"
    return True, "accepted"


# ---- main ------------------------------------------------------------------

def add_primitives(src, dep_json, hot_json, out_path, model=MODEL,
                   retries=4, base_source=None, include_dirs=None):
    """Add OpenMP primitives to functions in `src`.

    When `base_source` is set, `src` is a partially-optimized file (e.g. the
    rules candidate) rather than the original serial source. In that case the
    dependency-JSON function line ranges (computed on the serial source) no
    longer match `src`, so we re-derive function records from `src` itself
    and carry over loop/blocker evidence from the dep JSON by name. We also
    restrict selection to functions the rules did NOT already parallelize
    (no `#pragma omp` in their body), so the LLM only fills the gaps.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(src) as f:
        src_text = f.read()
    with open(dep_json) as f:
        dep_info = json.load(f)
    with open(hot_json) as f:
        hot_info = json.load(f)
    loop_classes = classify_loops(src_text)
    dep_records = dep_info.get("function_evidence", [])
    if base_source:
        # Re-derive line ranges from the (rules-optimized) source so INSERT
        # merges line up. Carry loop evidence over from the dep records by name.
        fresh = extract_function_ranges(src_text, os.path.basename(src))
        dep_by_name = {r.get("name"): r for r in dep_records}
        records = []
        for r in fresh:
            name = r.get("name")
            base = dep_by_name.get(name, {})
            merged = dict(r)
            merged["loops"] = base.get("loops", [])
            merged["blockers"] = base.get("blockers", [])
            merged["calls"] = base.get("calls", [])
            merged["hotspot_keys"] = base.get("hotspot_keys", [])
            merged["text"] = r.get("text")
            records.append(merged)
    else:
        records = dep_records
        if not records:
            records = extract_function_ranges(src_text, os.path.basename(src))
        source_lines = src_text.splitlines(True)
        for record in records:
            if not record.get("text") and record.get("line") and record.get("end_line"):
                record["text"] = "".join(source_lines[record["line"] - 1:record["end_line"]])
    selected = match_hotspots(records, hot_info, match_line=not base_source, match_file=not base_source)
    if not selected:
        with open(out_path, "w") as f: f.write(src_text)
        with open(out_path + ".prompt.txt", "w") as f: f.write("NO_SAFE_HOTSPOT\n")
        return out_path, loop_classes
    # Only shared-write (cross-function global mutation) blocks a function.
    # unsafe-loop is informational; loop-level safety is enforced per-loop.
    safe = [item for item in selected if "shared-write" not in item.get("blockers", [])]
    # Exclude BOTS sequential reference functions (suffix _seq). These are the
    # serial baseline used by KERNEL_CHECK to verify the parallel version;
    # parallelizing them breaks verification. They are recursive (so the
    # recursive-task signal would fire) but must be left serial.
    safe = [item for item in safe if not item["name"].endswith("_seq")]
    # Keep only functions with at least one parallelizable loop, then take the
    # top 2 by parallelizable-loop count. This focuses the LLM on the real
    # compute hotspots (e.g. conj_grad with 10 parallel loops) and avoids
    # parallelizing setup functions (sparse, sprnvc) that have few safe loops
    # and produce wrong results when their unsafe loops get parallelized.
    # Recursive functions are also kept: they have 0 parallelizable loops but
    # are parallelizable via #pragma omp task on recursive calls (BOTS pattern).
    safe = [item for item in safe
            if (any(loop.get("parallelizable") for loop in item.get("loops", []))
                or item["name"] in item.get("calls", [])
                or _should_refactor(item, src_text, dep_info)[0])
            and (_should_refactor(item, src_text, dep_info)[0]
                 or not _has_only_call_seed_loops(item))]
    # When building on a rules candidate, skip functions the rules already
    # parallelized (their body already contains #pragma omp). The LLM should
    # only touch functions rules left serial (the semantic-transform cases
    # rules cannot handle, e.g. compute_initial_conditions' static-tmp loop).
    # EXCEPTION: functions that need refactor mode (unsafe-loop with a
    # dependent outer loop, e.g. SP x_solve/y_solve/z_solve). The rules path
    # parallelizes their INNER loop (nested parallelism, one fork/join per
    # outer iteration, ~34x overhead). Refactor mode reorders to put the
    # independent loop outermost (one fork/join total, aaai-style). So even
    # though rules added #pragma omp inside, the LLM must still rewrite the
    # whole function to swap the loop order. Keep these eligible.
    if base_source:
        safe = [item for item in safe
                if "#pragma omp" not in (item.get("text") or "")
                or _should_refactor(item, src_text, dep_info)[0]]
    safe.sort(key=lambda item: (sum(1 for l in item.get("loops", []) if l.get("parallelizable")),
                               item["name"] in item.get("calls", [])), reverse=True)
    # Functions that trigger refactor mode (indirect accumulation, static
    # scratch, unsafe-loop-with-parallelizable, recursive, task-entry) need a
    # full-function rewrite that rules cannot express. Select ALL of them so
    # the LLM fills every semantic-transform gap (e.g. mg psinv/resid/rprj3/
    # interp are all stencil nests the rules skip). INSERT-mode functions are
    # capped at 2 to focus the LLM on the hottest compute loops.
    refactor_funcs = [item for item in safe
                      if _should_refactor(item, src_text, dep_info)[0]]
    insert_funcs = [item for item in safe
                    if item not in refactor_funcs][:2]
    safe = refactor_funcs + insert_funcs
    # For task-parallel (recursive) functions, also select their non-recursive
    # caller as an entry point. The caller opens #pragma omp parallel + single
    # and calls the recursive function once; the recursive function adds task
    # pragmas on its recursive calls. Without the caller, no parallel region
    # exists. Find callers of recursive functions in safe that are themselves
    # non-recursive, and add them to safe (capped at 4 total).
    recursive_names = {item["name"] for item in safe if item["name"] in item.get("calls", [])}
    if recursive_names:
        calls_map = dep_info.get("function_calls", {})
        entry_callers = []
        for rec in records:
            if rec["name"] in recursive_names:
                continue
            callees = calls_map.get(rec["name"], [])
            if any(c in recursive_names for c in callees) and rec["name"] not in recursive_names:
                if rec["name"] not in {s["name"] for s in safe}:
                    entry_callers.append(rec)
        # rank entry callers by how many recursive callees they call
        entry_callers.sort(key=lambda r: sum(1 for c in calls_map.get(r["name"], []) if c in recursive_names), reverse=True)
        for ec in entry_callers[:2]:
            if len(safe) >= 4:
                break
            safe.append(ec)
    # Exclude functions that call another function which will open its own
    # #pragma omp parallel region (refactor mode). If the caller wraps a loop
    # that calls such a callee inside a parallel region, all threads run the
    # callee redundantly, and the callee's own parallel region nests inside,
    # causing oversubscription or deadlock (e.g. main calling conj_grad).
    # This does NOT apply to task-parallel callees: the caller opens the
    # parallel region specifically to spawn tasks from the callee, which is
    # correct. Insert-mode callees only add #pragma omp for (no parallel
    # region of their own), so a serial call from the caller is safe.
    refactor_names = {item["name"] for item in safe
                      if _should_refactor(item, src_text, dep_info)[0]}
    loop_parallelized_names = {item["name"] for item in safe
                               if item["name"] in refactor_names
                               and any(loop.get("parallelizable") for loop in item.get("loops", []))}

    def _callee_called_in_par_loop(caller_text, callee_name, caller_start, safe_lines):
        """True if callee_name is invoked inside a PARALLELIZABLE for-loop
        body of the caller. A call inside a control loop (e.g. main's serial
        `for (step = ...)` step loop, par=False) does NOT count, because that
        loop will never carry a `#pragma omp parallel for` and so the callee's
        own parallel region cannot nest inside it. Only a loop the analyzer
        proved parallelizable (in safe_lines) can become a parallel region.

        caller_start is the caller function's 1-indexed start line in the
        source, used to map caller_text lines back to source line numbers so
        they can be checked against safe_lines.
        """
        if not safe_lines:
            return False
        lines = caller_text.splitlines()
        stack = []  # list of bool: is_parallelizable for each active loop
        d = 0
        for li, ln in enumerate(lines):
            src_line = caller_start + li
            par_here = src_line in safe_lines
            for_open = bool(re.match(r"\s*for\s*\(", ln))
            opens = ln.count("{")
            closes = ln.count("}")
            opened_here = for_open and "{" in ln
            if opened_here:
                stack.append(par_here)
            d += opens - closes
            # a loop's body ends when depth drops below its own level
            while stack and d < len(stack):
                stack.pop()
            if re.search(r"\b" + re.escape(callee_name) + r"\s*\(", ln) and any(stack):
                return True
        return False

    # Load dep-proven parallelizable loop line numbers for the caller-in-loop
    # check (a call inside a control loop like main's step loop does not nest).
    try:
        from rule_transformer import _load_parallelizable_lines
    except ImportError:
        _pa_dir = str(Path(__file__).resolve().parent)
        if _pa_dir not in sys.path:
            sys.path.insert(0, _pa_dir)
        from rule_transformer import _load_parallelizable_lines
    safe_lines = _load_parallelizable_lines(dep_json) if dep_json else None

    safe = [item for item in safe
            if not (item["name"] not in item.get("calls", [])
                    and any(c in loop_parallelized_names
                            and _callee_called_in_par_loop(item.get("text", ""), c,
                                                           item.get("line", 1), safe_lines)
                            for c in item.get("calls", [])))]
    # Exclude functions that are CALLED by another function in safe. If a
    # callee is parallelized (gets its own #pragma omp parallel for) and a
    # caller invokes it inside a parallel loop, the callee's region nests
    # inside the caller's, causing oversubscription and wrong results (e.g.
    # bt matvec_sub/binvcrhs called from x_solve_cell's parallel j loop).
    # These small helpers should stay serial; the caller's parallel loop
    # already distributes the work.
    called_by_safe = set()
    calls_map = dep_info.get("function_calls", {})
    for item in safe:
        for c in item.get("calls", []):
            # Only exclude the callee if THIS caller invokes it inside a
            # parallelizable loop body. A serial call (e.g. main's step loop
            # calling x_solve, or x_solve calling lhsx before its loops) does
            # not nest parallel regions, so the callee must stay eligible.
            if _callee_called_in_par_loop(item.get("text", ""), c,
                                          item.get("line", 1), safe_lines):
                called_by_safe.add(c)
    safe = [item for item in safe if item["name"] not in called_by_safe]
    if not safe:
        with open(out_path, "w") as f: f.write(src_text)
        with open(out_path + ".prompt.txt", "w") as f: f.write("NO_SAFE_HOTSPOT\n")
        return out_path, loop_classes
    src_dir = os.path.dirname(os.path.abspath(src))
    if include_dirs is None:
        include_dirs = [d for d in (src_dir, os.path.join(src_dir, "..", "common")) if os.path.isdir(d)]
    accepted = src_text
    audits = []
    replacements = []  # [(record, candidate)] collected, merged once at end
    for record in safe:
        target = record.get("text", "")
        # In base_source (rules+llm) mode, refactor candidates replace the
        # WHOLE function. If the rules candidate already inserted pragmas
        # (e.g. SP x_solve got nested inner-loop parallelism), sending that
        # modified text confuses the LLM (it sees pragmas it did not write
        # and may keep the nested-parallel structure). Strip rules-inserted
        # pragmas so the LLM refactors from clean serial logic and applies
        # its own (reordered) parallelization. Only do this for refactor
        # candidates; INSERT mode builds on the existing pragmas.
        refactor, refactor_reason = _should_refactor(record, src_text, dep_info)
        if base_source and refactor:
            target = "\n".join(
                ln for ln in target.splitlines()
                if not re.match(r"\s*#\s*pragma\s+omp\b", ln)
            )
        # Use the dependency analyzer's loop classification (accurate) for this
        # function's loops. Fall back to classify_loops if dep has no loop data.
        # Rebase loop line numbers to function-relative (target starts at line 1).
        func_start = record.get("line", 1)
        dep_loops = record.get("loops", [])
        if dep_loops:
            func_loops = [dict(loop, line=loop["line"] - func_start + 1)
                          for loop in dep_loops]
        else:
            func_loops = [dict(loop, line=loop["line"] - func_start + 1)
                          for loop in loop_classes
                          if func_start <= loop["line"] <= record.get("end_line", func_start)]
        prompt = build_prompt(target, dep_info, {"hotspots": [record.get("hotspot", {})]},
                              func_loops, refactor=refactor)
        candidate = None
        reason = "unknown"
        for attempt in range(1, retries + 1):
            try:
                candidate = call_llm(prompt, model, target, expected_name=record["name"])
                with open(out_path + f".{record['name']}.candidate{attempt}.c", "w") as f:
                    f.write(candidate)
                # Auto-inject scalar temporaries the LLM omitted from
                # private() clauses (common: lists fac1 but forgets fac2 in
                # the same loop). Safe because such scalars are written+read
                # within one iteration (no cross-iteration accumulation).
                # autofix_private only touches `#pragma omp for` / `parallel
                # for` clauses (never a bare `#pragma omp parallel` region),
                # skips reduction accumulators, and rebuilds the private(...)
                # clause by locating its own close paren, so it is safe in
                # both INSERT and refactor modes.
                candidate = autofix_private(candidate)
                local_record = dict(record, line=1, end_line=len(target.splitlines()))
                ok, reason = validate_candidate(target, candidate, local_record, refactor=refactor)
                if not ok:
                    continue
                # Per-candidate compile check: merge this candidate alone into
                # the source and compile. This catches undeclared-variable and
                # syntax errors that the structural validator misses, so a
                # malformed candidate is rejected before it can corrupt the
                # batch merge and discard good candidates.
                trial = merge_function_ranges(src_text, [(record, candidate)], [record])
                trial = fix_thread_report(trial)
                # Strip reduction vars that the LLM wrongly listed in the
                # enclosing parallel private(...) (gcc: "reduction variable
                # is private in outer context"), and ensure inner loop vars
                # are present in omp for private(...). Strip nowait so a
                # shared-parallel region keeps implicit barriers between
                # worksharing loops (inter-loop data deps would race).
                trial = strip_nowait(trial)
                trial = strip_collapse(trial)
                trial = postfix_private_clauses(trial)
                trial = fix_parallel_private_conflicts(trial)
                with open(out_path + ".trial.c", "w") as f:
                    f.write(trial)
                if _compile_check(out_path + ".trial.c", include_dirs) != 0:
                    reason = "compile-fail-solo"
                    candidate = None
                    continue
                break
            except Exception as exc:
                reason = str(exc)
        if candidate is not None and reason.startswith("accepted"):
            replacements.append((record, candidate))
            audits.append({"function": record["name"], "accepted": True, "attempts": attempt,
                           "mode": "refactor" if refactor else "insert"})
        else:
            audits.append({"function": record["name"], "accepted": False, "reason": reason, "attempts": attempt,
                           "mode": "refactor" if refactor else "insert"})
        with open(out_path + f".{record['name']}.prompt.txt", "w") as f: f.write(prompt)
    # Merge all accepted replacements at once. merge_function_ranges sorts
    # records by line number in reverse, so applying all replacements to the
    # original src_text in one pass avoids line-shift corruption (incremental
    # merge would use stale line ranges after the first replacement changes
    # the file length). If the combined merge fails to compile, drop
    # candidates one at a time (last first) until it compiles, so one bad
    # candidate does not discard the good ones.
    accepted = src_text
    accepted_records = []
    rec_list = [r for r, _ in replacements]
    cand_list = [c for _, c in replacements]
    while rec_list:
        trial = merge_function_ranges(src_text, list(zip(rec_list, cand_list)), rec_list)
        trial = fix_thread_report(trial)
        trial = strip_nowait(trial)
        trial = strip_collapse(trial)
        trial = postfix_private_clauses(trial)
        trial = fix_parallel_private_conflicts(trial)
        with open(out_path, "w") as f: f.write(trial)
        if _compile_check(out_path, include_dirs) == 0:
            accepted = trial
            accepted_records = list(rec_list)
            break
        # drop the last candidate and retry with the rest
        dropped = rec_list.pop()
        cand_list.pop()
        for a in audits:
            if a.get("function") == dropped["name"] and a.get("accepted"):
                a["accepted"] = False
                a["reason"] = "compile-fail-merged"
    # Fix NPB thread reporting on the final accepted source.
    accepted = fix_thread_report(accepted)
    with open(out_path, "w") as f: f.write(accepted)
    with open(out_path + ".status.json", "w") as f: json.dump({"accepted": any(x["accepted"] for x in audits), "batches": audits}, f, indent=2)
    with open(out_path + ".prompt.txt", "w") as f: f.write("\n\n".join(x["function"] for x in audits))
    return out_path, loop_classes


def main():
    ap = argparse.ArgumentParser(description="OpenMP primitive adder")
    ap.add_argument("--src", required=True)
    ap.add_argument("--dep", required=True, help="dependency JSON")
    ap.add_argument("--hot", required=True, help="hotspot JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--base", default=None,
                    help="base source (e.g. rules candidate) to build on; "
                         "LLM only touches functions the base left serial")
    ap.add_argument("--include-dirs", default=None,
                    help="comma-separated include dirs for compile check "
                         "(used when src is in a scratch dir without headers)")
    args = ap.parse_args()
    inc = args.include_dirs.split(",") if args.include_dirs else None
    out, loops = add_primitives(args.src, args.dep, args.hot, args.out,
                               args.model, base_source=args.base,
                               include_dirs=inc)
    n_pragma = 0
    with open(out) as f:
        n_pragma = f.read().count("#pragma omp")
    print(f"[prim] wrote {out}")
    print(f"[prim] loops classified: {len(loops)} "
          f"(reduction={sum(1 for l in loops if l['kind']=='reduction')}, "
          f"independent={sum(1 for l in loops if l['kind']=='independent')}, "
          f"sequential={sum(1 for l in loops if l['kind']=='sequential')})")
    print(f"[prim] #pragma omp count in output: {n_pragma}")


if __name__ == "__main__":
    main()
