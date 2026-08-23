"""
Profile snapshots — restoring DiscoPoP's output without re-profiling
---------------------------------------------------------------------
A rewrite that turns out not to pay off has to leave both the source AND the
profile as they were.  Re-running instrument + run + explore to rebuild a state
we already had would cost more than the attempt did, so the profile is copied
aside before the patch lands and copied back on a revert.

The snapshot lives under the agent's own output directory rather than the OS
temp dir, so an interrupted run leaves it next to everything else it produced.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


def _snapshot_profile(dp_dir: Path, output_dir: Path) -> Path:
    """Copy the current DiscoPoP profile (.discopop) to a snapshot under the
    agent's output dir (kept inside the project, not the OS temp dir), excluding
    the output dir itself when it lives inside .discopop.  Restoring this snapshot
    is far cheaper than re-running instrument+run+explore to rebuild the same
    pre-patch state on a revert."""
    snap_root = output_dir / ".profile_snapshots"
    snap_root.mkdir(parents=True, exist_ok=True)
    snap = Path(tempfile.mkdtemp(prefix="snap_", dir=snap_root))
    ignore = None
    if output_dir.resolve().parent == dp_dir.resolve():
        # output_dir (and thus the snapshot under it) lives inside .discopop —
        # exclude it so we never copy the snapshot into itself.
        ignore = shutil.ignore_patterns(output_dir.name)
    shutil.copytree(dp_dir, snap, dirs_exist_ok=True, ignore=ignore)
    return snap


def _restore_profile(snap: Path, dp_dir: Path, output_dir: Path) -> None:
    """Restore the profile from a snapshot taken by _snapshot_profile, preserving
    the agent's output dir (accepted.json, patches, backups) when it lives inside
    .discopop.  Replaces re-profiling on a revert."""
    keep = output_dir.name if output_dir.resolve().parent == dp_dir.resolve() else None
    for item in dp_dir.iterdir():
        if item.name == keep:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in snap.iterdir():
        dst = dp_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
