"""What is known about a region, gathered from DiscoPoP's output."""
from .blockers import load_prevented_deps
from .context import _brace_match_end
from .package import assemble

__all__ = ["assemble", "load_prevented_deps", "_brace_match_end"]
