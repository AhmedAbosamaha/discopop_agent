"""Talking to the model: prompts, rendering, backends, and the edits that come back."""
from .client import call_llm
from .diffs import make_diff, normalize_code
from .dep_review import review_dependences
from .providers import LLMConnectionError
from .render import fmt_blockers

__all__ = ["call_llm", "review_dependences", "make_diff", "normalize_code",
           "fmt_blockers", "LLMConnectionError"]
