# DiscoPoP Agentic Controller
# L1: Planner  — hotspot priority queue + scoring + orchestration loop
# L2: Evidence — assembles DiscoPoP runtime output into LLM context
# L3: LLM      — calls Claude API to restructure non-parallelizable code
# L4: Validator — compile + ThreadSanitizer + semantic diff quality gate
