#!/usr/bin/env python3
"""Unified per-execution run storage shared by all benchmark harnesses.

Every execution of a harness produces exactly one self-contained directory so
that the data and reports of a run can never be confused with those of another:

    <harness>/runs/<run_id>/
    ├── manifest.json          # self-describing metadata (what was run)
    ├── results.json           # metrics data (harness-specific "runs" array)
    ├── overview.md            # human-readable summary
    ├── overview.pdf           # summary plot(s), if matplotlib is available
    ├── tables/*.md            # individual markdown tables
    └── benchmarks/<rel/path>/ # per-benchmark artifacts (report.pdf, data.json, …)

``run_id`` is a timestamp, ``YYYYmmdd_HHMMSS``. Callers may also supply their own
id (e.g. the GUI) via the harness ``--run-id`` flag; any filesystem-safe string
works, and a timestamp prefix keeps lexical sorting meaningful.

The manifest is the single source of truth for *what* an execution was: the
harness, the exact invocation (benchmarks, versions, configs, variants, thread
count, algorithm, …), timestamps, and status. ``results.json`` embeds the same
invocation block so the data file is self-describing even in isolation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

RUN_ID_FORMAT = "%Y%m%d_%H%M%S"


class RunStore:
    """Manages the ``runs/`` directory of a single harness."""

    def __init__(self, harness_dir: Path, harness_name: str):
        self.harness_dir = Path(harness_dir)
        self.harness_name = harness_name
        self.runs_dir = self.harness_dir / "runs"

    # ---- run ids / paths -------------------------------------------------

    @staticmethod
    def new_run_id() -> str:
        return datetime.now().strftime(RUN_ID_FORMAT)

    def run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def manifest_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "manifest.json"

    def results_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "results.json"

    def tables_dir(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "tables"

    def benchmarks_dir(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "benchmarks"

    # ---- lifecycle -------------------------------------------------------

    def create_run(self, run_id: str, invocation: dict) -> Path:
        """Create the run directory skeleton and write the initial manifest."""
        d = self.run_dir(run_id)
        self.tables_dir(run_id).mkdir(parents=True, exist_ok=True)
        self.benchmarks_dir(run_id).mkdir(parents=True, exist_ok=True)
        self.write_manifest(run_id, {
            "run_id": run_id,
            "harness": self.harness_name,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None,
            "status": "running",
            "invocation": invocation,
            "summary": {},
        })
        return d

    def finish_run(self, run_id: str, status: str = "finished", summary: Optional[dict] = None):
        m = self.read_manifest(run_id) or {}
        m["status"] = status
        m["finished_at"] = datetime.now().isoformat(timespec="seconds")
        if summary is not None:
            m["summary"] = summary
        self.write_manifest(run_id, m)

    # ---- manifest --------------------------------------------------------

    def write_manifest(self, run_id: str, manifest: dict):
        p = self.manifest_path(run_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps(manifest, indent=2))
        tmp.replace(p)

    def read_manifest(self, run_id: str) -> Optional[dict]:
        p = self.manifest_path(run_id)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text())
        except (OSError, ValueError):
            return None

    # ---- results ---------------------------------------------------------

    def write_results(self, run_id: str, runs: List[dict], extra: Optional[dict] = None):
        manifest = self.read_manifest(run_id) or {}
        data = {
            "run_id": run_id,
            "harness": self.harness_name,
            "timestamp": run_id,  # backwards-compatible key
            "invocation": manifest.get("invocation", {}),
            "runs": runs,
        }
        if extra:
            data.update(extra)
        self.results_path(run_id).write_text(json.dumps(data, indent=2))

    def read_results(self, run_id: str) -> dict:
        return json.loads(self.results_path(run_id).read_text())

    # ---- listing / lookup ------------------------------------------------

    def list_run_ids(self) -> List[str]:
        if not self.runs_dir.exists():
            return []
        ids = [d.name for d in self.runs_dir.iterdir()
               if d.is_dir() and (d / "manifest.json").exists()]
        return sorted(ids)

    def latest_run_id(self) -> Optional[str]:
        ids = self.list_run_ids()
        return ids[-1] if ids else None

    def list_runs(self) -> List[dict]:
        """Return manifests for all runs, oldest first."""
        out = []
        for rid in self.list_run_ids():
            m = self.read_manifest(rid)
            if m:
                out.append(m)
        return out

    def resolve_run_id(self, run_id: Optional[str]) -> Optional[str]:
        """Return the given run_id if present, else the latest available run."""
        if run_id:
            return run_id if self.run_dir(run_id).exists() else None
        return self.latest_run_id()
