from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


@dataclass
class Dependency:
    dep_type: str       # RAW | WAR | WAW
    from_line: int
    to_line: int
    variable: str
    kind: str = "scalar"   # "array" (array-element / GEPRESULT access) | "scalar"


@dataclass
class CodeRegion:
    """Any profiled code region: a loop, function body, or CU (basic block)."""
    region_id: str      # "file_id:node_id"  e.g. "1:11"
    region_type: str    # "loop" | "function" | "cu"
    name: str           # function name or "" for loops/CUs
    file_id: int
    start_line: int
    end_line: int
    iteration_count: int    # loop iteration count; 1 for non-loops
    workload: int           # instructionsCount or derived estimate


@dataclass
class HotspotCandidate:
    region: CodeRegion
    source_file: str
    pattern: Optional[dict]     # from patterns.json — None if no Tier-1 match
    pattern_type: Optional[str] # "do_all" | "reduction" | "pipeline" | etc.
    confidence: float           # pattern confidence [0, 1]
    workload_estimate: float    # W — profiled workload proxy (NOT a measured speedup)
    score: float                # c·log₂(1+W) − λ·1[tier=2]
    tier: int                   # 1 = DiscoPoP pattern available, 2 = LLM needed


@dataclass
class EvidencePackage:
    region_id: str
    region_type: str            # "loop" | "function" | "cu"
    start_line: int
    end_line: int
    source_file: str
    source_region: str          # annotated source lines
    iteration_count: int
    raw_deps: List[Dependency]
    war_deps: List[Dependency]
    waw_deps: List[Dependency]
    reduction_vars: List[str]
    tier1_failure_reason: str = ""
    # DiscoPoP's own OpenMP data-sharing classification for this region, taken
    # from the detected pattern (patterns.json).  Empty lists when no pattern was
    # detected for the region.  Tells the LLM which variables DiscoPoP considers
    # shared data (a loop-carried dep on these is algorithmic) vs. privatizable.
    shared_vars: List[str] = field(default_factory=list)
    private_vars: List[str] = field(default_factory=list)
    firstprivate_vars: List[str] = field(default_factory=list)
    lastprivate_vars: List[str] = field(default_factory=list)
    classified_reduction_vars: List[str] = field(default_factory=list)
    # Observed loop trip counts for loops in this region (from the profiler's
    # BGN-loop markers).  Each dict: {line, total, entries, avg, max} where
    # entries = number of activations, avg = iterations per activation.  Lets the
    # LLM reason about parallel granularity (few iters/activation => fine-grained).
    loop_trip_counts: List[dict] = field(default_factory=list)
    # Variables DiscoPoP tracks as loop-LOCAL in this region (from the CU graph):
    # already per-iteration private, so they need no privatization.
    local_vars_in_region: List[str] = field(default_factory=list)
    # Variables whose dependences DiscoPoP found only STATICALLY (compiler-
    # conservative) but never observed at runtime — likely spurious / privatizable.
    static_only_vars: List[str] = field(default_factory=list)
    # Do-All blockers from DiscoPoP's new detector (explorer/doall_prevented.json):
    # the specific dependences that prevented parallelization of this region.
    # Each dict: {dep_type, source_line, sink_line, var_name, memory_region, origin,
    #             loop_file, loop_start, loop_end}
    prevented_deps: List[dict] = field(default_factory=list)
    # Loop structure of the region (from the explorer's PEGraph LoopNodes): one
    # dict per loop overlapping the region, {start, end, depth, index_vars,
    # entries, avg, total, max}.  depth counts containing loops within the region
    # (0 = outermost).  index_vars are DiscoPoP's induction variables for the
    # loop — deps on these are never the real blocker.
    loop_nest: List[Dict[str, Any]] = field(default_factory=list)
    # Function calls made inside the region (from Data.xml callsNode): one dict
    # per call site, {line, callee, recursive}.  Non-empty means the loop body
    # has side effects the source alone may not show.
    calls_in_region: List[Dict[str, Any]] = field(default_factory=list)
    # Raw source text by absolute line number, covering the enclosing function
    # plus the region.  Lets the prompt quote the exact statement a dependence
    # points at instead of making the LLM cross-reference line numbers.
    line_text: Dict[int, str] = field(default_factory=dict)
    # Enclosing function (used by --edit-mode function: the LLM rewrites this whole
    # function and the agent splices it in by line range).  Falls back to the
    # region's own span when no containing function is found.
    enclosing_function_name: str = ""
    enclosing_function_start: int = 0
    enclosing_function_end: int = 0
    enclosing_function_source: str = ""


@dataclass
class ValidationResult:
    passed: bool
    # "apply" | "compile" | "openmp_compile" | "tsan" | "correctness"
    # | "performance" | "accepted"
    stage: str
    diagnostic: str = ""
    measured_speedup: Optional[float] = None   # set by the performance stage
