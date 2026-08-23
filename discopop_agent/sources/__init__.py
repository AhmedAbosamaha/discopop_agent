"""Writing to the user's file and to DiscoPoP's profile — always reversibly."""
from .edits import (_apply_change_log, _apply_in_memory, _apply_to_source,
                    _function_edit_to_diff)
from .snapshots import _restore_profile, _snapshot_profile

__all__ = ["_apply_to_source", "_apply_in_memory", "_apply_change_log",
           "_function_edit_to_diff", "_snapshot_profile", "_restore_profile"]
