"""The pipeline: restructure (A), annotate (B), then judge the finished file."""
from .phase_a import RunState, phase_a
from .phase_b import _phase_b
from .report import (_REGION_LABEL, _print_banner, _print_candidates,
                     _write_record)
from .settle import _check_final_source, _settle
from .verdicts import RewriteOutcome, _OUTCOME_LABEL, _rewrite_feedback, _verify_rewrite

__all__ = ["phase_a", "RunState", "_phase_b", "_settle", "_check_final_source", "RewriteOutcome",
           "_verify_rewrite", "_rewrite_feedback", "_OUTCOME_LABEL",
           "_print_banner", "_print_candidates", "_write_record", "_REGION_LABEL"]
