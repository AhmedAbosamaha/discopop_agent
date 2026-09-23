# t0_9_refresh_d29 — T0.9 re-run: fast refresh vs full profile over chains of rewrites (no model)

Owed before E3 (record §5s): D29 (21 Sep) changed the fast-refresh path T0.9 exercises (it now
re-measures runtimes too), so the 18 Sep result is re-taken on the current code. Mac, 23 Sep 2026,
commit `2b2f8a0b`, LLVM 19 (the server repeat on LLVM 20 follows, as E3 runs there):

    venv/bin/python -m discopop_agent.benchmark.refresh_depth --json <this folder>/refresh_depth.json

Three synthetic programs × three successive rewrites × two arms (fast-step: one refresh on the full
profile's previous state; fast-chain: a refresh on the previous refresh, as the agent does within a
depth), each compared with a full instrumented re-profile of the byte-identical source.

**Result: 11 of 18 comparisons reach the full profile's conclusions; 7 produce a suggestion the
measured profile does NOT support** (18 Sep, before D29: 8 identical, 8 unsupported, 2 lost). Trip
counts stale or missing in 13. The reading of 18 Sep stands: the fast refresh is a queue-maintenance
optimisation, not an analysis to decide a pragma on — which is why the agent always takes one full
re-profile before Phase B when its profile holds carried-forward data, and why E3's fast-refresh arms
are judged against the full re-profile.

`console.log` (every comparison), `refresh_depth.json` (the full result).
