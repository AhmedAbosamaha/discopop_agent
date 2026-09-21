#!/usr/bin/env python3
"""Tidy data and thesis figures for agent experiment runs.

``build(trials, out_dir)`` writes, for any set of trials (one run or several runs
combined):

* ``trials.csv``        one row per trial — every number a thesis table needs
* ``gate_failures.csv`` long format: one row per (trial, phase, gate stage)
* ``fig_*.pdf`` / ``fig_*.png``  static figures (PDF for the thesis, PNG for slides)
* ``figures.md``        what each figure shows, which experiment it serves, and n

Figures are light-surface only: they are for print. Colours follow the reference
data-viz palette and were run through its validator (categorical slots 1–3 all-pairs,
the ordinal blue ramp, the outcome set). Arms beyond three are faceted, never given a
fourth hue in an overlapping mark.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---- palette (reference instance, light surface) ---------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]          # categorical slots 1–3
GOOD, CRITICAL = "#0ca30c", "#d03b3b"               # status: good / critical
# Gate stages grouped by what they check, cheapest first, on five steps of one blue ramp
# (250/350/450/550/650). Nine separate steps failed the validator's adjacent-ΔL check.
STAGE_GROUPS: List[Tuple[str, List[str], str]] = [
    ("static checks", ["clause", "dependences"], "#86b6ef"),
    ("build", ["apply", "compile", "openmp_compile"], "#5598e7"),
    ("races", ["tsan", "schedules"], "#2a78d6"),
    ("correctness", ["correctness"], "#1c5cab"),
    ("performance", ["performance"], "#104281"),
]
# Outcome hues validated as an adjacent set; grey is a deliberate neutral for "nothing happened".
OUTCOME_ORDER: List[Tuple[str, str]] = [
    ("FASTER", GOOD),
    ("parallel-not-faster", "#2a78d6"),
    # Same hue as parallel-not-faster plus a hatch, not a new colour: it is the same kind of
    # result without a speed verdict (kernel too short to time, T0.1).
    ("parallel-speed-not-measurable", "#2a78d6"),
    ("changed-not-parallel", "#eda100"),
    ("no-change", AXIS),
    ("BROKEN", CRITICAL),
    # Same hue as BROKEN plus a hatch, not a new colour: both are results that must not be
    # counted, and the validated outcome palette stays unchanged.
    ("SCAFFOLD_MODIFIED", CRITICAL),
    ("no verdict", "#4a3aa7"),
]
OUTCOME_HATCH = {"parallel-speed-not-measurable": "////", "SCAFFOLD_MODIFIED": "xxxx"}
NO_VERDICT = {"VERIFY_FAILED", "AGENT_ERROR", "AGENT_TIMEOUT", "PROFILE_ERROR"}

GROUPS_FILE = Path(__file__).resolve().parents[1] / "kernel_groups.json"


# ---------------------------------------------------------------------------
# Tidy data
# ---------------------------------------------------------------------------

def _groups() -> Dict[str, str]:
    try:
        spec = json.loads(GROUPS_FILE.read_text())["groups"]
    except (OSError, ValueError, KeyError):
        return {}
    return {k: g for g, ks in spec.items() for k in ks}


CLASSES_FILE = Path(__file__).resolve().parents[1] / "benchmark_classes.json"


def _classes() -> Dict[str, str]:
    """benchmark -> its MEASURED class (R / A / D, T0.11), from the campaign's input file.

    The main comparison is read per class: the claim is about R (DiscoPoP alone reaches
    nothing there), A shows no harm, D shows no unsafe acceptance. Pooled over all classes the
    verdict counts would mostly reflect how many benchmarks of each class a run happened to
    contain. The guessed groups of kernel_groups.json stay for the runs made before T0.11.
    """
    try:
        spec = json.loads(CLASSES_FILE.read_text())["classes"]
    except (OSError, ValueError, KeyError):
        return {}
    return {b: c for c, bs in spec.items() for b in bs}


def best_speedup(t: dict) -> Optional[float]:
    par = (t.get("verify") or {}).get("par") or {}
    vals = [p.get("speedup") for p in par.values() if p.get("speedup")]
    return max(vals) if vals else None


def outcome_bucket(t: dict) -> str:
    o = t.get("outcome", "no verdict")
    return "no verdict" if o in NO_VERDICT else o


def series_label(t: dict) -> str:
    return f"{t.get('arm')} · {t.get('model')}"


def _last_switch(flags: List[str], name: str) -> Optional[bool]:
    """Value of a --name / --no-name switch as the agent parses it: the last one wins."""
    value: Optional[bool] = None
    for f in flags:
        if f == f"--{name}":
            value = True
        elif f == f"--no-{name}":
            value = False
    return value


def _last_value(cmd: List[str], flag: str) -> Optional[float]:
    """Value of a numeric option as the agent parses it: the last occurrence wins."""
    value: Optional[float] = None
    for i, f in enumerate(cmd[:-1]):
        if f == flag:
            try:
                value = float(cmd[i + 1])
            except ValueError:
                pass
        elif f.startswith(flag + "="):
            try:
                value = float(f.split("=", 1)[1])
            except ValueError:
                pass
    return value


def flat_row(t: dict) -> dict:
    v = t.get("verify") or {}
    prof = t.get("profile") or {}
    groups = _groups()
    row = {
        "run_id": t.get("run_id"), "benchmark": t.get("benchmark"), "kernel": t.get("kernel"),
        "group": groups.get(t.get("kernel", ""), ""), "arm": t.get("arm"), "model": t.get("model"),
        "repeat": t.get("repeat"), "outcome": t.get("outcome"), "best_speedup": best_speedup(t),
        "seq_median_s": v.get("seq_median_s"), "seq_kernel_median_s": v.get("seq_kernel_median_s"),
        "timing_basis": v.get("timing_basis"),
        "kernel_program_disagree": v.get("kernel_program_disagree"),
        "dump_exact": v.get("dump_exact"), "dump_exact_seeded": v.get("dump_exact_seeded"),
        "digest_max_rel_err": v.get("digest_max_rel_err"),
        # Relative error of the full value dump. Byte-equality (`dump_exact`) is kept for
        # information, but the verdict uses this: a correct parallel reduction reorders
        # additions and moves the last digits (md, 3.5e-15).
        "dump_max_rel_err": v.get("dump_max_rel_err"),
        "dump_seeded_max_rel_err": v.get("dump_seeded_max_rel_err"),
        "digest_seeded_rel_err": v.get("digest_seeded_rel_err"),
        "stable_at_fixed_threads": v.get("stable_at_fixed_threads"),
        "source_changed": t.get("source_changed"), "pragmas_in_final": t.get("pragmas_in_final"),
        "pragmas_discopop": t.get("pragmas_discopop"), "pragmas_llm": t.get("pragmas_llm"),
        "rewrites_kept": t.get("rewrites_kept"), "baseline_pragmas": t.get("baseline_pragmas"),
        "agent_verdict": t.get("agent_verdict"), "llm_calls": t.get("llm_calls"),
        # Non-zero means the trial did less work than its call count suggests.
        # A trial whose calls ALL failed still records a tidy "no-change", so
        # this column is what separates "the agent declined" from "the agent was
        # never answered" (§7, pilot_seidel).
        "llm_call_failures": t.get("llm_call_failures"),
        "explorer_retries": t.get("explorer_retries"),
        "profile_explore_attempts": (t.get("profile") or {}).get("explore_attempts"),
        # False: the rewrite edited the packaging's timer, perturbation or digest (scaffold.py).
        "scaffold_ok": (t.get("scaffold") or {}).get("ok"),
        "scaffold_problems": "; ".join((t.get("scaffold") or {}).get("problems") or []) or None,
        "input_tokens": (t.get("llm_usage") or {}).get("input_tokens"),
        "output_tokens": (t.get("llm_usage") or {}).get("output_tokens"),
        "cache_read_input_tokens": (t.get("llm_usage") or {}).get("cache_read_input_tokens"),
        "cost_usd_equivalent": (t.get("llm_usage") or {}).get("cost_usd"),
        "model_seconds": (t.get("llm_usage") or {}).get("model_seconds"),
        "candidates_recorded": t.get("candidates_recorded"),
        "reverts": t.get("reverts"), "gate_passes_phase_a": t.get("gate_passes_phase_a"),
        "speed_check_off": t.get("speed_check_off"),
        "refresh_fast": t.get("refresh_fast"), "refresh_full": t.get("refresh_full"),
        "refresh_fallback": t.get("refresh_fallback"),
        "runtime_remeasurements": t.get("runtime_remeasurements"),
        "settle_dropped": t.get("settle_dropped"),
        "agent_s": t.get("agent_s"), "verify_s": t.get("verify_s"),
        "profile_s": round(sum(prof.get(k, 0) or 0 for k in ("instrument_s", "profiled_run_s", "explore_s")), 2)
        if prof else None,
        "discopop_do_all": (prof.get("patterns") or {}).get("do_all"),
        "host_load_start_1m": (t.get("host_load_start") or [None])[0],
        "host_load_end_1m": (t.get("host_load_end") or [None])[0],
        "started_at": t.get("started_at"), "finished_at": t.get("finished_at"),
        "verify_size": v.get("verify_size"), "speed_measurable": v.get("speed_measurable"),
        "require_speedup": _last_switch(t.get("arm_flags") or [], "require-speedup"),
        "min_runtime_share": _last_value(t.get("agent_cmd") or [], "--min-runtime-share"),
        "timing_cflags": next((f.split("=", 1)[1] for f in (t.get("arm_flags") or [])
                               if f.startswith("--timing-cflags=")), None),
    }
    for th, p in ((v.get("par") or {}).items()):
        row[f"speedup_T{th}"] = p.get("speedup")
        row[f"program_speedup_T{th}"] = p.get("program_speedup")
    return row


# ---------------------------------------------------------------------------
# THE MAIN COMPARISON: DiscoPoP alone vs DiscoPoP + agent (rule of 2026-09-19, D19)
# ---------------------------------------------------------------------------
# A speedup over the sequential original cannot show what the agent adds: DiscoPoP's own
# pragmas reach most of it on code that is parallel as written (§5k). Every agent trial is
# therefore paired with the DiscoPoP-alone arm on the same benchmark, and the verdict is
# about THAT pair; the sequential original stays in the table as the reference (1×).

BASELINE_ARM = "discopop_gate"
PARALLEL_OK = ("FASTER", "parallel-not-faster", "parallel-speed-not-measurable")
TIMED_OK = ("FASTER", "parallel-not-faster")
WIN_RATIO = 1.1
VS_ORDER: List[Tuple[str, str]] = [
    ("gained", "DiscoPoP alone reaches no verified parallel program; the agent does, and it is >= 1.1x faster"),
    ("gained-not-faster", "as gained, but the agent's program is not faster (or the kernel is too short to time)"),
    ("better", "both parallel and correct; the agent's program is >= 1.1x faster than DiscoPoP alone's"),
    ("equal", "both parallel and correct; within 1.1x of each other (or not timeable)"),
    ("worse", "correct, but the agent's program is >= 1.1x slower than the one DiscoPoP alone leaves"),
    ("lost", "DiscoPoP alone reaches a verified parallel program; the agent's trial does not"),
    ("neither", "neither reaches a verified parallel program"),
    ("unsafe", "the agent's final program computes different values (BROKEN)"),
    ("invalid", "the agent's trial has no verdict (scaffold modified, verification/agent/profile error)"),
    ("not-comparable", "both parallel and correct, but timed on another host, size or thread set: no ratio"),
    ("no-baseline", "no DiscoPoP-alone trial for this benchmark among the given runs"),
]


def _program_speedup_vs_seq(t: dict) -> Optional[float]:
    """Speedup of a trial's FINAL program over the sequential original, for pairing:
    a program left unchanged IS the original (1.0); a wrong program has none."""
    o = t.get("outcome")
    if o in TIMED_OK:
        return best_speedup(t)
    if o in ("no-change", "changed-not-parallel"):
        return 1.0
    return None


def _timing_setup(t: dict) -> Tuple[Optional[str], Optional[str], Tuple[int, ...]]:
    v = t.get("verify") or {}
    return (t.get("host"), v.get("verify_size"), tuple(sorted(int(n) for n in (v.get("par") or {}))))


def vs_discopop_alone(trials: List[dict]) -> List[dict]:
    """One row per agent trial, paired with the DiscoPoP-alone trials of its benchmark."""
    base: Dict[str, List[dict]] = {}
    for t in trials:
        if t.get("arm") == BASELINE_ARM and t.get("kind") != "baseline":
            base.setdefault(str(t.get("benchmark")), []).append(t)
    groups = _groups()
    classes = _classes()
    rows: List[dict] = []
    for t in trials:
        if t.get("arm") == BASELINE_ARM or t.get("kind") == "baseline":
            continue
        bs = base.get(str(t.get("benchmark")), [])
        # Speeds are only comparable when both programs were timed the same way: same host,
        # same verification size, same thread counts. Otherwise the OUTCOMES are still paired
        # (they do not depend on the machine) and the ratio is withheld.
        comparable = bool(bs) and all(_timing_setup(b) == _timing_setup(t) for b in bs)
        dp_par = [b for b in bs if b.get("outcome") in PARALLEL_OK]
        dp_parallel = bool(bs) and len(dp_par) * 2 > len(bs)           # majority of its repeats
        dp_speeds = [x for x in (_program_speedup_vs_seq(b) for b in bs) if x]
        dp_speed = statistics.median(dp_speeds) if dp_speeds else None
        o = t.get("outcome")
        a_speed = _program_speedup_vs_seq(t)
        ratio = (a_speed / dp_speed) if a_speed and dp_speed and comparable else None
        if not bs:
            verdict = "no-baseline"
        elif o == "BROKEN":
            verdict = "unsafe"
        elif o in NO_VERDICT or o == "SCAFFOLD_MODIFIED":
            verdict = "invalid"
        elif o not in PARALLEL_OK:
            verdict = "lost" if dp_parallel else "neither"
        elif not dp_parallel:
            # DiscoPoP alone left the sequential original: the agent's speedup over the original IS
            # its speedup over DiscoPoP alone, whatever machine the baseline was classified on.
            # A parallel program that RUNS SLOWER than the one DiscoPoP alone leaves behind is not a
            # gain, however new the parallelism is — `hotspot` at 0.09× is 11× slower than doing
            # nothing. Those are counted as `worse`, like any other regression.
            if o == "FASTER":
                verdict = "gained"
            elif a_speed and a_speed <= 1 / WIN_RATIO:
                verdict = "worse"
            else:
                verdict = "gained-not-faster"
        elif not comparable and a_speed and dp_speed:
            verdict = "not-comparable"
        elif ratio is None or o == "parallel-speed-not-measurable":
            verdict = "equal"
        else:
            verdict = "better" if ratio >= WIN_RATIO else "worse" if ratio <= 1 / WIN_RATIO else "equal"
        rows.append({
            "run_id": t.get("run_id"), "benchmark": t.get("benchmark"), "kernel": t.get("kernel"),
            "group": groups.get(t.get("kernel", ""), ""), "arm": t.get("arm"), "model": t.get("model"),
            "class": classes.get(str(t.get("benchmark")), ""),
            "repeat": t.get("repeat"),
            "dp_alone_trials": len(bs), "dp_alone_outcomes": ",".join(sorted(str(b.get("outcome")) for b in bs)),
            "dp_alone_parallel": dp_parallel if bs else None,
            "dp_alone_speedup_vs_seq": round(dp_speed, 3) if dp_speed else None,
            "agent_outcome": o, "agent_speedup_vs_seq": round(a_speed, 3) if a_speed else None,
            "agent_vs_dp_alone": round(ratio, 3) if ratio else None,
            "timing_comparable": comparable if bs else None,
            "rewrites_kept": t.get("rewrites_kept"), "llm_calls": t.get("llm_calls"),
            "verdict": verdict,
        })
    return rows


def vs_discopop_alone_md(trials: List[dict]) -> str:
    """The main comparison as markdown: verdict counts per arm, then one line per benchmark."""
    rows = vs_discopop_alone(trials)
    if not rows:
        return ""
    names = [n for n, _ in VS_ORDER]
    out = ["| Arm | Model | Trials | " + " | ".join(names) + " | median agent / DiscoPoP alone |",
           "|---|---|---:|" + "---:|" * len(names) + "---:|"]
    series: List[Tuple[str, str]] = []
    for r in rows:
        if (r["arm"], r["model"]) not in series:
            series.append((r["arm"], r["model"]))
    for arm, model in series:
        rs = [r for r in rows if (r["arm"], r["model"]) == (arm, model)]
        ratios = [r["agent_vs_dp_alone"] for r in rs if r["agent_vs_dp_alone"]]
        med = f"{statistics.median(ratios):.2f}x (n={len(ratios)})" if ratios else "—"
        out.append(f"| {arm} | {model} | {len(rs)} | "
                   + " | ".join(str(sum(1 for r in rs if r["verdict"] == n)) for n in names) + f" | {med} |")
    # Per measured class: THIS is the table the claim is read from (class R), with A as the
    # no-harm control and D as the must-decline control.
    if any(r.get("class") for r in rows):
        out += ["", "| Class | Arm | Model | Benchmarks | Trials | " + " | ".join(names)
                + " | median agent / DiscoPoP alone |",
                "|---|---|---|---:|---:|" + "---:|" * len(names) + "---:|"]
        for cls in ("R", "A", "D", ""):
            for arm, model in series:
                rs = [r for r in rows if (r["arm"], r["model"]) == (arm, model) and (r.get("class") or "") == cls]
                if not rs:
                    continue
                ratios = [r["agent_vs_dp_alone"] for r in rs if r["agent_vs_dp_alone"]]
                med = f"{statistics.median(ratios):.2f}x (n={len(ratios)})" if ratios else "—"
                out.append(f"| {cls or 'unclassified'} | {arm} | {model} | {len({r['benchmark'] for r in rs})} | {len(rs)} | "
                           + " | ".join(str(sum(1 for r in rs if r["verdict"] == n)) for n in names) + f" | {med} |")
        out += ["", "Classes are MEASURED (T0.11, `benchmark_classes.json`): R = DiscoPoP alone reaches no verified "
                    "parallel program in any of three profile draws; A = it does in the majority; D = R, and a true "
                    "recurrence by design. The claim is read from R; A is the no-harm control; D the must-decline control."]
    out += ["", "| Benchmark | Arm | Model | DiscoPoP alone (outcomes · x over seq.) | Agent (outcomes · median x over seq.) | "
                "Agent / DiscoPoP alone | Verdicts |", "|---|---|---|---|---|---:|---|"]
    keys: List[Tuple[str, str, str]] = []
    for r in rows:
        k = (str(r["benchmark"]), str(r["arm"]), str(r["model"]))
        if k not in keys:
            keys.append(k)
    for bench, arm, model in keys:
        rs = [r for r in rows if (str(r["benchmark"]), str(r["arm"]), str(r["model"])) == (bench, arm, model)]
        dp = rs[0]
        dps = f"{dp['dp_alone_speedup_vs_seq']:.2f}x" if dp["dp_alone_speedup_vs_seq"] else "—"
        a_sp = [r["agent_speedup_vs_seq"] for r in rs if r["agent_speedup_vs_seq"]]
        ra = [r["agent_vs_dp_alone"] for r in rs if r["agent_vs_dp_alone"]]
        verdicts = ", ".join(f"{sum(1 for r in rs if r['verdict'] == n)} {n}" for n in names
                             if any(r["verdict"] == n for r in rs))
        out.append(f"| {bench} | {arm} | {model} | {dp['dp_alone_outcomes'] or '—'} · {dps} | "
                   f"{','.join(sorted(str(r['agent_outcome']) for r in rs))} · "
                   f"{f'{statistics.median(a_sp):.2f}x' if a_sp else '—'} | "
                   f"{f'{statistics.median(ra):.2f}x' if ra else '—'} | {verdicts} |")
    withheld = sum(1 for r in rows if r["timing_comparable"] is False)
    if withheld:
        out += ["", f"**Speed ratios withheld for {withheld} trial(s):** the DiscoPoP-alone trial was timed on another "
                    "host, size or thread set. Outcomes are still paired; run `discopop_gate` in the same run for the ratio."]
    out += ["", "Verdicts: " + "; ".join(f"**{n}** — {d}" for n, d in VS_ORDER) + ".",
            "A program left unchanged IS the sequential original (1.00x); the sequential original is the "
            "reference both columns are measured against, never the comparison itself."]
    return "\n".join(out) + "\n"


def write_csvs(trials: List[dict], out: Path) -> List[Path]:
    rows = [flat_row(t) for t in trials]
    keys: List[str] = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    p1 = out / "trials.csv"
    with p1.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    p2 = out / "gate_failures.csv"
    with p2.open("w", newline="") as fh:
        w2 = csv.writer(fh)
        w2.writerow(["run_id", "benchmark", "arm", "model", "repeat", "phase", "stage", "count"])
        for t in trials:
            for phase in ("a", "b"):
                for stage, n in (t.get(f"gate_failures_phase_{phase}") or {}).items():
                    w2.writerow([t.get("run_id"), t.get("benchmark"), t.get("arm"), t.get("model"),
                                 t.get("repeat"), phase.upper(), stage, n])
    written = [p1, p2]
    pairs = vs_discopop_alone(trials)
    if pairs:
        p3 = out / "vs_discopop_alone.csv"
        with p3.open("w", newline="") as fh:
            w3 = csv.DictWriter(fh, fieldnames=list(pairs[0]))
            w3.writeheader()
            w3.writerows(pairs)
        (out / "vs_discopop_alone.md").write_text(vs_discopop_alone_md(trials))
        written += [p3, out / "vs_discopop_alone.md"]
    return written


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif",
        # Not Helvetica: on macOS it is a .ttc collection that the PDF backend cannot embed as
        # Type 42 ("specify a font number between 0 and 5"), and the server does not have it.
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK_2, "axes.facecolor": SURFACE,
        "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "xtick.color": MUTED, "ytick.color": INK_2, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": False, "pdf.fonttype": 42,
    })
    return plt


def _save(fig, out: Path, name: str) -> List[Path]:
    paths = [out / f"{name}.pdf", out / f"{name}.png"]
    fig.savefig(paths[0], bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight", dpi=200)
    return paths


def _series(trials: List[dict]) -> List[str]:
    seen: List[str] = []
    for t in trials:
        s = series_label(t)
        if s not in seen:
            seen.append(s)
    return seen


def fig_outcomes(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    series = _series(trials)
    fig, ax = plt.subplots(figsize=(6.4, 0.5 + 0.42 * len(series)))
    for yi, s in enumerate(series):
        ts = [t for t in trials if series_label(t) == s]
        left = 0
        for name, color in OUTCOME_ORDER:
            n = sum(1 for t in ts if outcome_bucket(t) == name)
            if n:
                ax.barh(yi, n, left=left, height=0.5, color=color, edgecolor=SURFACE, linewidth=2,
                        hatch=OUTCOME_HATCH.get(name))
                left += n
        ax.text(left + 0.15, yi, f"n = {len(ts)}", va="center", fontsize=8, color=INK_2)
    longest = max(sum(1 for t in trials if series_label(t) == s) for s in series)
    ax.set_xlim(0, longest * 1.15 + 0.5)
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.set_yticks(range(len(series)), series)
    ax.invert_yaxis()
    ax.set_xlabel("trials")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=SURFACE, hatch=OUTCOME_HATCH.get(n))
               for n, c in OUTCOME_ORDER]
    ax.legend(handles, [n for n, _ in OUTCOME_ORDER], ncol=3, fontsize=8, loc="lower left",
              bbox_to_anchor=(0, 1.02))
    caption = ("Outcome of every trial as judged by the harness (not the agent), per arm and model. "
               "BROKEN = accepted but computes different values (unsafe acceptance); "
               "no verdict = verification, agent or profiling error; hatched = correct and parallel "
               "on a kernel too short to time (T0.1), so no speed verdict.")
    paths = _save(fig, out, "fig_outcomes")
    plt.close(fig)
    return paths, caption


def fig_speedups(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    ok = [t for t in trials if t.get("outcome") in ("FASTER", "parallel-not-faster") and best_speedup(t)]
    if not ok:
        return [], ""
    groups = _groups()
    kernels = sorted({t["kernel"] for t in ok}, key=lambda k: (groups.get(k, "Z"), k))
    series = _series(ok)
    panels = [series] if len(series) <= 3 else [[s] for s in series]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.4 * len(panels) + 1.2, 0.6 + 0.32 * len(kernels)),
                             sharey=True, squeeze=False)
    for ax, panel in zip(axes[0], panels):
        ax.set_xscale("log", base=2)
        ax.axvline(1.0, color=AXIS, linewidth=1)
        ax.axvline(1.1, color=MUTED, linewidth=0.8)
        for si, s in enumerate(panel):
            off = (si - (len(panel) - 1) / 2) * 0.22
            xs = [best_speedup(t) for t in ok if series_label(t) == s]
            ys = [kernels.index(t["kernel"]) + off for t in ok if series_label(t) == s]
            ax.scatter(xs, ys, s=36, color=SERIES[si if len(panel) > 1 else 0],
                       edgecolor=SURFACE, linewidth=1.2, zorder=3, label=s)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("speedup over sequential original (log scale)")
        all_x = [best_speedup(t) or 1.0 for t in ok]
        lo, hi = min(0.5, min(all_x) * 0.8), max(4.0, max(all_x) * 1.25)
        ax.set_xlim(lo, hi)
        ticks = [t for t in (0.25, 0.5, 1, 2, 4, 8, 16, 32, 64) if lo <= t <= hi]
        ax.set_xticks(ticks, [f"{t:g}×" for t in ticks])
        if len(panels) > 1:
            ax.set_title(panel[0], fontsize=9, color=INK_2)
    axes[0][0].set_yticks(range(len(kernels)),
                          [f"{k} ({groups[k]})" if k in groups else k for k in kernels])
    axes[0][0].invert_yaxis()
    if len(panels) == 1 and len(series) > 1:
        axes[0][0].legend(fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=len(series))
    caption = ("Best measured speedup per trial at the verify size, on the timed kernel region "
               "(PolyBench convention; whole-program speedup is in trials.csv), correct parallel results only "
               "(BROKEN trials are never given a speedup). Grey lines: 1× and the 1.1× acceptance "
               "threshold. Kernel labels carry the plan's group (A ready, B restructurable, C order matters).")
    paths = _save(fig, out, "fig_speedups")
    plt.close(fig)
    return paths, caption


def fig_vs_discopop_alone(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    """The main comparison as a dumbbell per benchmark: DiscoPoP alone -> DiscoPoP + agent."""
    rows = [r for r in vs_discopop_alone(trials)
            if r["verdict"] not in ("no-baseline", "invalid", "not-comparable") and r["timing_comparable"]]
    if not rows:
        return [], ""
    series: List[Tuple[str, str]] = []
    for r in rows:
        if (r["arm"], r["model"]) not in series:
            series.append((r["arm"], r["model"]))
    benches: List[str] = []
    for r in rows:
        if r["benchmark"] not in benches:
            benches.append(r["benchmark"])

    def _agent(b: str, sm: Tuple[str, str]) -> Optional[float]:
        v = [r["agent_speedup_vs_seq"] for r in rows
             if r["benchmark"] == b and (r["arm"], r["model"]) == sm and r["agent_speedup_vs_seq"]]
        return statistics.median(v) if v else None

    def _dp(b: str) -> Optional[float]:
        return next((r["dp_alone_speedup_vs_seq"] for r in rows if r["benchmark"] == b), None)

    benches.sort(key=lambda b: -((_agent(b, series[0]) or 0) / (_dp(b) or 1)))
    fig, axes = plt.subplots(1, len(series), figsize=(4.4 * len(series) + 1.0, 0.7 + 0.3 * len(benches)),
                             sharey=True, squeeze=False)
    xs_all = [x for b in benches for x in ([_dp(b)] + [_agent(b, sm) for sm in series]) if x]
    lo, hi = min(0.5, min(xs_all) * 0.8), max(4.0, max(xs_all) * 2.2)
    for ax, sm in zip(axes[0], series):
        ax.set_xscale("log", base=2)
        ax.axvline(1.0, color=AXIS, linewidth=1)
        for yi, b in enumerate(benches):
            d, a = _dp(b), _agent(b, sm)
            unsafe = any(r["verdict"] == "unsafe" for r in rows
                         if r["benchmark"] == b and (r["arm"], r["model"]) == sm)
            if d and a:
                ax.plot([d, a], [yi, yi], color=AXIS, linewidth=2, zorder=2, solid_capstyle="round")
            if d:
                ax.scatter([d], [yi], s=40, color=SERIES[1], edgecolor=SURFACE, linewidth=1.2, zorder=3)
            if a:
                ax.scatter([a], [yi], s=40, color=SERIES[0], edgecolor=SURFACE, linewidth=1.2, zorder=4)
            note = (f"{a / d:.2f}×" if d and a else "—") + ("  (a BROKEN repeat)" if unsafe else "")
            ax.text(max(x for x in (d, a, 1.0) if x) * 1.18, yi, note, va="center", fontsize=8, color=INK_2)
        ax.set_xlim(lo, hi)
        ticks = [t for t in (0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64) if lo <= t <= hi]
        ax.set_xticks(ticks, [f"{t:g}×" for t in ticks])
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("speedup over the sequential original (reference, log scale)")
        ax.set_title(f"{sm[0]} · {sm[1]}", fontsize=9, color=INK_2)
    axes[0][0].set_yticks(range(len(benches)), benches)
    axes[0][0].invert_yaxis()
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=SERIES[1], markersize=6),
               plt.Line2D([], [], marker="o", linestyle="", color=SERIES[0], markersize=6)]
    axes[0][0].legend(handles, ["DiscoPoP alone (its pragmas through the gate, no model)", "DiscoPoP + agent"],
                      fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.08), ncol=2)
    caption = ("THE MAIN COMPARISON — DiscoPoP alone against DiscoPoP + agent, per benchmark. Both programs are "
               "timed against the same sequential original (the reference axis; a program left unchanged sits "
               "at 1×); the number at the right is agent ÷ DiscoPoP alone, medians over repeats. Rows sorted by "
               "that ratio. Verdict counts and every pair: vs_discopop_alone.md / .csv.")
    paths = _save(fig, out, "fig_vs_discopop_alone")
    plt.close(fig)
    return paths, caption


def fig_evidence_model(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    arms = ["full_b1", "no_evidence_b1"]
    ts = [t for t in trials if t.get("arm") in arms]
    models = sorted({t["model"] for t in ts})
    if len({t["arm"] for t in ts}) < 2 or not models:
        return [], ""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.8))
    width = 0.34
    for ai, arm in enumerate(arms):
        rates, broken = [], []
        for m in models:
            cell = [t for t in ts if t["arm"] == arm and t["model"] == m]
            # Kernels too short to time have no speed verdict: out of the rate's denominator.
            timed = [t for t in cell if t["outcome"] != "parallel-speed-not-measurable"]
            rates.append(100 * sum(t["outcome"] == "FASTER" for t in timed) / len(timed) if timed else float("nan"))
            broken.append(sum(t["outcome"] == "BROKEN" for t in cell))
        label = "with evidence" if arm == "full_b1" else "no evidence"
        a1.plot(range(len(models)), rates, color=SERIES[ai], linewidth=2, marker="o", markersize=7,
                markeredgecolor=SURFACE, markeredgewidth=1.2, label=label)
        xs = [i + (ai - 0.5) * width for i in range(len(models))]
        a2.bar(xs, broken, width=width, color=SERIES[ai], edgecolor=SURFACE, linewidth=2, label=label)
    for ax in (a1, a2):
        ax.set_xticks(range(len(models)), models)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    a1.set_ylabel("trials FASTER (%)")
    a1.set_ylim(0, 100)
    a2.set_ylabel("BROKEN trials (count)")
    a2.yaxis.get_major_locator().set_params(integer=True)
    a1.legend(fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
    caption = ("Evidence × model (E2). Left: share of trials with a correct parallel speedup ≥ 1.1×. "
               "Right: unsafe acceptances as counts, never rates. One LLM attempt per region in both arms.")
    paths = _save(fig, out, "fig_evidence_model")
    plt.close(fig)
    return paths, caption


def fig_gate(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    series = _series(trials)
    group_of = {st: g for g, sts, _ in STAGE_GROUPS for st in sts}
    totals = {s: {g: 0 for g, _, _ in STAGE_GROUPS} for s in series}
    for t in trials:
        for st, n in (t.get("gate_failures_phase_a") or {}).items():
            g = group_of.get(st)
            if g:
                totals[series_label(t)][g] += n
    if not any(sum(v.values()) for v in totals.values()):
        return [], ""
    fig, ax = plt.subplots(figsize=(6.4, 0.5 + 0.42 * len(series)))
    for yi, s in enumerate(series):
        left = 0
        for g, _, color in STAGE_GROUPS:
            n = totals[s][g]
            if n:
                ax.barh(yi, n, left=left, height=0.5, color=color, edgecolor=SURFACE, linewidth=2)
                left += n
    ax.set_yticks(range(len(series)), series)
    ax.invert_yaxis()
    ax.set_xlabel("rejected model rewrites (Phase A)")
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in STAGE_GROUPS]
    ax.legend(handles, [g for g, _, _ in STAGE_GROUPS], ncol=5, fontsize=8, loc="lower left",
              bbox_to_anchor=(0, 1.02))
    caption = ("Which part of the gate rejected the model's rewrites, cheapest first: static checks "
               "(clause, dependences), build (apply, compile, OpenMP compile), races (TSan, schedule "
               "stress), correctness, performance. Per-stage counts are in gate_failures.csv. "
               "Build-error rejections are refunded by the agent and still counted here.")
    paths = _save(fig, out, "fig_gate_stages")
    plt.close(fig)
    return paths, caption


def fig_cost(plt, trials: List[dict], out: Path) -> Tuple[List[Path], str]:
    series = _series(trials)
    if not series:
        return [], ""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 0.7 + 0.42 * len(series)), sharey=True)
    for yi, s in enumerate(series):
        ts = [t for t in trials if series_label(t) == s]
        mins = [t["agent_s"] / 60 for t in ts if t.get("agent_s") is not None]
        calls = [t.get("llm_calls", 0) for t in ts]
        for ax, vals in ((a1, mins), (a2, calls)):
            if vals:
                ax.scatter(vals, [yi] * len(vals), s=30, color=SERIES[0], edgecolor=SURFACE,
                           linewidth=1.2, zorder=3)
                med = statistics.median(vals)
                ax.plot([med, med], [yi - 0.28, yi + 0.28], color=INK, linewidth=2, zorder=4)
    a1.set_yticks(range(len(series)), series)
    a1.invert_yaxis()
    a1.set_xlabel("agent wall-clock per trial (min)")
    a2.set_xlabel("model calls per trial")
    for ax in (a1, a2):
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlim(left=0)
    caption = ("Cost per trial: agent wall-clock time and model calls. Dots are trials; the black tick is "
               "the median. Two measures of different scale, so two panels.")
    paths = _save(fig, out, "fig_cost")
    plt.close(fig)
    return paths, caption


def build(trials: List[dict], out_dir: Path) -> List[Path]:
    """Write CSVs, every figure the data supports, and figures.md. Returns all paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = write_csvs(trials, out_dir)
    if not trials:
        return written
    plt = _plt()
    runs = sorted({str(t.get("run_id")) for t in trials})
    index = [f"# Figures\n\nBuilt from {len(trials)} trial(s) in run(s): {', '.join(runs)}.\n"
             "Data: `trials.csv` (one row per trial), `gate_failures.csv` (long format), "
             "`vs_discopop_alone.csv` / `.md` (the main comparison: every agent trial paired with "
             "DiscoPoP alone on the same benchmark).\n"]
    for fn in (fig_vs_discopop_alone, fig_outcomes, fig_speedups, fig_gate, fig_evidence_model, fig_cost):
        paths, caption = fn(plt, trials, out_dir)
        if paths:
            written += paths
            index.append(f"## `{paths[0].name}`\n\n{caption}\n")
    (out_dir / "figures.md").write_text("\n".join(index))
    written.append(out_dir / "figures.md")
    return written
