"""DiscoPoP Agentic Controller.

    plan/       what to work on, in what order — regions, measured cost, ranking
    evidence/   what is known about a region, from DiscoPoP's output
    llm/        talking to the model: prompts, rendering, backends, edits back
    gate/       is a change safe, correct, and worth keeping
    pragmas/    reading and writing `#pragma omp` — clause rules, patch derivation
    sources/    changing the user's file and DiscoPoP's profile, reversibly
    profiling/  producing and refreshing profile data (full, fast, hotspots)
    phases/     the pipeline: restructure (A), annotate (B), settle
    run.py      the orchestrator that drives them
"""
