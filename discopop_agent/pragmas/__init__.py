"""Reading and writing `#pragma omp` — everything that treats a pragma as text.

Independent of the pipeline: nothing here knows about phases, budgets or the
LLM, which is what makes it directly testable.
"""
from .clauses import check_llm_pragmas, check_pragma_clauses
from .parse import _added_pragmas, _touched_span
from .patch import (_already_annotated, _read_tier1_patch,
                    _repair_pragma_clauses, derive_pragma_patch)

__all__ = [
    "check_llm_pragmas", "check_pragma_clauses", "derive_pragma_patch",
    "_repair_pragma_clauses", "_already_annotated", "_read_tier1_patch",
    "_added_pragmas", "_touched_span",
]
