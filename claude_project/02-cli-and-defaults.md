# CLI reference and current defaults

Generated from `venv/bin/python -m discopop_agent --help` on 2026-08-30 (commit
`4927898c`). **This is the authoritative default list.** Older documents state
`--min-workload 1.0` and describe `--llm-deps` as a default — both are wrong now.

## Defaults that matter

| Flag | Default | Note |
|---|---|---|
| `--budget` | `3` | LLM retry attempts per region |
| `--min-workload` | `0.0` | 0 on purpose — `FUNCTION` regions report workload 0 |
| `--llm-pragmas` | **on** | model writes the pragma; the gate decides |
| `--fast-refresh` | **on** | skip the instrumented run after a kept rewrite |
| `--llm-deps` | **OFF** | kept only for comparison experiments — see below |
| `--llm-recon` | off | additive dependence reconstruction |
| `--llm-recon-mode` | `followup` | vs `folded` — which is better is an open question |
| `--hotspots` | **on** | rank by measured time saved, not instruction count |
| `--min-impact` | `0.0` | off; in seconds, needs `--hotspots` |
| `--restructure-depth` | `0` | only initial candidates may be restructured |
| `--require-speedup` | **on** | |
| `--min-measured-speedup` | `1.1` | |
| `--apply-patches` | on | |
| `--evidence` | `full` | ablation control |
| `--allow-unverified` | off | run aborts if the original cannot be built/run |
| `--build-retries` | `2` | build failures do not consume budget |
| `--numeric-tolerance` | **on** | measured noise floor, not a fixed epsilon |
| `--schedule-stress` | **on** | |
| `--stress-threads` | `1,2,4` | |

Three defaults are **computed, not fixed**:
- `--model` follows `--provider` (`haiku` for `claude-agent-sdk`, `claude-opus-5`
  otherwise) — a Claude Code alias passed to the `anthropic` provider is a 404.
- `--edit-mode` follows `--provider` (`direct` for `claude-agent-sdk`, `diff` otherwise).
- `--llm-deps` resolves from `None` to `False` in `args.py` (~line 328).

## The three LLM-evidence flags — do not confuse them

| Flag | Direction | Soundness |
|---|---|---|
| `--llm-pragmas` | model writes a pragma | **sound** — the gate tests the claim |
| `--llm-recon` | model **adds** dependences | **sound direction** — more conservative |
| `--llm-deps` | model **deletes** static dependences | **unsound direction** — the only place a model's claim edits DiscoPoP's analysis instead of being tested |

`--llm-deps` is off by default and is not recommended. It never adds a dependence, and
observed dependences are filtered out before the model sees them. It also rarely pays for
itself: a fast refresh saves only the instrumented run (8.6 s and 7.9 s on the two
benchmark cases), and one LLM call usually costs more than that.

`--llm-recon` and `--llm-deps` are mutually exclusive, and both require `--fast-refresh`.

## `--evidence` — the ablation control

Nine sections: `deps`, `reductions`, `classification`, `extra_vars`, `array_note`,
`loop_nest`, `calls`, `blockers`, `failure`.

- `full` — everything (default)
- `none` — source and task only
- `deps,blockers` — SELECT those sections
- `--evidence=-classification,-loop_nest` — SUBTRACT from full. **Use the equals sign**, a
  leading dash is otherwise read as a flag.

`failure` is the **gate's** diagnostic, not DiscoPoP's. Leaving it in means a no-evidence
run still gets empirical feedback, so pair the ablation with `--budget 1` to isolate the
two variables.

## Correctness inputs

`--check-input` is repeatable and matters more than it looks: correctness is otherwise
judged on a **single** input, so a rewrite that is right at the profiled size and wrong at
0, 1, or an odd count passes. Inputs the original cannot run are dropped with a warning.
