# VOID — this run is not a result

All 9 of this run's model calls failed with HTTP 401 (the stored OAuth token was
truncated: 80 of 108 characters). The agent was never answered, so:

* `outcome = no-change` here means "no model ever replied", NOT "the agent declined".
* `llm_usage` is zero because nothing was billed, not because the agent was cheap.
* `agent_s = 136.4` is fast because no work happened.

**Nothing in this directory may enter any analysis** — including the derived
`figures/`, `tables/` and `overview.md`, which were generated from these trials.

Full diagnosis: `agent/THESIS_EXPERIMENTS.md` section 7, entry `pilot_seidel`.
Agent fix so this cannot recur silently: `discopop_agent/docs/FIXES.md`, Fix 58.
