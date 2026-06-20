from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Dependency:
    dep_type: str       # RAW | WAR | WAW
    from_line: int
    to_line: int
    variable: str


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


@dataclass
class ValidationResult:
    passed: bool
    # "apply" | "compile" | "openmp_compile" | "tsan" | "correctness"
    # | "performance" | "accepted"
    stage: str
    diagnostic: str = ""
    measured_speedup: Optional[float] = None   # set by the performance stage
