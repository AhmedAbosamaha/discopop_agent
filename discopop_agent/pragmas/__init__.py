"""Reading and writing `#pragma omp` — everything that treats a pragma as text.

Independent of the pipeline: nothing here knows about phases, budgets or the
LLM, which is what makes it directly testable.
"""
from .arbitrate import arbitrate as arbitrate_pragmas, collisions as pragma_collisions
from .clauses import check_llm_pragmas, check_pragma_clauses
from .parse import (_added_pragmas, _touched_span, changed_span,
                    existing_parallel_spans, net_new_pragmas)
from .patch import (_already_annotated, _read_tier1_patch,
                    _repair_pragma_clauses, derive_pragma_patch)

__all__ = [
    "existing_parallel_spans", "changed_span", "net_new_pragmas",
    "check_llm_pragmas", "check_pragma_clauses", "derive_pragma_patch",
    "_repair_pragma_clauses", "_already_annotated", "_read_tier1_patch",
    "_added_pragmas", "_touched_span",
    "arbitrate_pragmas", "pragma_collisions",
]
