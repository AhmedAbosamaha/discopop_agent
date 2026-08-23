"""The quality gate: is a change safe, correct, and worth keeping?

`_validate_cached` is the entry point — it adds result reuse and the
OMP-barrier re-verification that `validate` alone does not do.
"""
from .patching import fix_hunk_headers, run_patch
from .timing import (capture_reference, measure_marginal, noise_floor,
                     time_source)
from .toolchain import find_archer
from .tsan import _is_omp_barrier_false_positive
from .validate import _gate_key, _validate_cached, check_pragma_compiles, validate

__all__ = [
    "validate", "_validate_cached", "_gate_key", "check_pragma_compiles",
    "capture_reference", "time_source", "noise_floor", "measure_marginal",
    "fix_hunk_headers", "run_patch", "find_archer",
    "_is_omp_barrier_false_positive",
]
