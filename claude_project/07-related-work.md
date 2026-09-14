# Related work and reading list

**Bibliographic details in this file are NOT verified.** They came from live search in
August 2026. Re-check every entry against DBLP, ACM DL, or Semantic Scholar before it
enters a `.bib` file.

**Fix first:** the June 2026 proposal's reference [1] attributes DiscoPoP to *"S.
Aldinucci et al."* That is wrong — Aldinucci is associated with FastFlow, and DiscoPoP is
the author's own lab's tool (Li, Atre, Jannesari, Wolf, Norouzi).

## The paper that changes the positioning

**RepoOMP: Repository-Aware Hotspot OpenMP Parallelization via Dependency-Aware Context
Reduction.** Qian, Gao, Zhang, Peng, Li. arXiv 2608.05855.

Abstract, verbatim (fetched from arXiv, quoted exactly):

> "RepoOMP builds a Multi-granularity Attributes Performance graph (MAP), routes hotspots
> between deterministic rules and an LLM agent, and constructs a Structured Transformation
> Context (STC) that exposes dependency facts without flooding the model with unrelated
> repository text."

951 profiled hotspots from NPB, BOTS, FFmpeg, NCNN, GROMACS. Acceptance: *"under
compilation, workload-specific checks, and positive speedup, 372 hotspots are accepted."*
Speedups 8.23× (NPB), 8.96× (BOTS), median 2.25× across 330 real-world hotspots. Token
cost 47–68% below *"the unstructured Claude Code baseline."*

**Three design decisions converge with this thesis:** routing between a deterministic tool
and an LLM, hotspot ranking, and structured dependence context. Independent convergence is
evidence the design is right and should be said so — but none can carry a novelty claim
any more. They become design, not contribution.

**Where the thesis lives** (inferred from the abstract only):

| Axis | RepoOMP | This agent |
|---|---|---|
| Action | annotates hotspots | **restructures** when parallelism is not present |
| Acceptance | compile + workload checks + positive speedup | **seven stages** incl. race detection, schedule stress, measured noise floor |
| Evidence after an edit | not addressed — nothing rewrites the code | **fast refresh + reconstruction** |

**⚠ Read the body before relying on any of that.** The abstract was verified; the paper
body was not readable (no PDF tooling available, and an automated summary contradicted the
abstract on at least one point — it claimed no dynamic profiling while the abstract says
"951 *profiled* hotspots"). Check specifically whether their dependency facts are static
or dynamic, and what "workload-specific checks" means. If those checks are strong, C2
weakens and C1/C3 must carry more.

## §3.1 Classical automatic parallelization

Polyhedral (Pluto, Polly/LLVM), Cetus, ROSE, production compiler autoparallelization.
Point to land: sound, but restricted to affine statically-analysable regions, and no
restructuring beyond a fixed catalogue.

- User-directed loop transformations in Clang — arXiv 1811.00624
- A proposal for loop-transformation pragmas — arXiv 1805.03374

These two give the transformation vocabulary the community considers legitimate — which is
the vocabulary Tier-2 rewrites should be described in.

## §3.2 Dependence profiling and its cost

Establishes that dynamic profiling gives precision static analysis cannot, and that its
cost is the known published obstacle — which is what makes C3 a contribution rather than
an optimisation.

- **DiscoPoP** — Li, Atre, Jannesari, Wolf et al. Pull exact entries from the lab (the
  2015 tool paper, the JSS 2016 article, the runtime/CU work)
- **SD3** — Kim et al. The standard cost citation
- **Prospector** — discovering parallelism via dynamic dependence profiling
- **Kremlin** — hierarchical critical path analysis
- **Accelerating data-dependence profiling with static hints** — Springer, 2019
- **Fast data-dependence profiling through prior static analysis** — ParCo 2024
- **Skipping repeatedly executed memory operations** — Springer, 2015

The last three are **the closest prior work, and from the same lab's line.** They attack
profiling cost from the static-hint side; C3 attacks it from the reuse side. Position
explicitly against them.

## §3.3 LLMs for parallelization

Organise as a progression so RepoOMP and this work land at the end of a trajectory:

- *Classifiers:* PragFormer, OMPify
- *Generators:* OMP-Engineer (arXiv 2405.03215), OMPAR, HPC-Coder / HPC-Coder-V2 (arXiv 2412.15178)
- *Analysis-guided:* **AutoParLLM** (arXiv 2310.04047) — GNN-guided context generation.
  The closest philosophical ancestor. Say what **dynamic** evidence adds over their static graph
- *Agentic:* Evaluating the Parallelization Capabilities of State-of-the-Art Agentic LLMs
  (Springer 10.1007/978-3-032-35248-4_2) — 8 agents, 11 HPC applications, multi-stage
  validation, multiple invocations per data point to quantify variance. **Read for its
  methodology**; its validation ladder and repeat protocol are close to what §6.1 needs
- *Evidence-guided:* RepoOMP
- *Benchmarks:* ParEval (arXiv 2401.12554), ParEval-Repo (ICPP 2025)
- *Repair:* LLOR (arXiv 2411.14590)
- *Challenge to C1:* **Don't Transform the Code, Code the Transforms** (arXiv 2410.08806)
  — argues the model should synthesise *transformations*, not rewrites, because
  transformations are inspectable. Answer it: the gate makes rewrites inspectable
  **behaviourally** where their approach makes them inspectable **syntactically**
- LOOPRAG (ASPLOS 2026) — retrieval-augmented loop transformation

## §3.4 Verifying parallel code

Argument: correctness of parallel code is not decidable by testing, so the literature uses
layered partial oracles — and seven stages is a principled instance, not an ad-hoc pile.

- ThreadSanitizer, and **Archer** (TSan's OpenMP-aware companion)
- **Metamorphic testing** — Chen et al.'s original formulation; Segura et al.'s survey.
  The schedule matrix *is* a metamorphic relation
- Testing the Unknown: OpenMP testing via random program generation (arXiv 2410.09191, LLNL)
- LLM4VV (arXiv 2408.11729) and its 2025 follow-up (arXiv 2507.21447) — cite as **the
  alternative rejected**: execution is the oracle here, not a model's judgement
- Detecting data races in OpenMP with deep learning and LLMs (10.1145/3677333.3678160)
- Numerical reproducibility under reassociation — Demmel & Nguyen; Goldberg for basics
- A Formal Semantics of C with OpenMP Parallelism (arXiv 2605.26527) — one-sentence
  contrast for why this thesis tests rather than proves

## §3.5 Incremental program analysis — THE MISSING SECTION

This does not exist in the proposal and it is what makes C3 legible as research.

**The term needed: from-scratch consistency.** An incremental analysis is from-scratch
consistent if, after an edit, it produces exactly the result a full re-analysis would
have. Anchor: **Stein et al., "Interactive Abstract Interpretation with Demanded
Summarization," TOPLAS 2024** (10.1145/3648441).

This reframes RQ5 from engineering to science: fast refresh is *not* from-scratch
consistent, so characterise the deviation and show it is safe. The 39/39 measurement **is
that characterisation** — the work was done, the word was missing.

Two more things this literature gives for free:
- **Prior art for the accumulation bug.** Invalidation tracking is documented as where
  soundness bugs live, with Infer as a named real-world case
- **Reuse-vs-recompute framing** — standard language for stating C3's limits precisely
  rather than apologetically

## §3.6 LLM grounding (optional)

Two or three citations on retrieval-augmented generation and hallucination in code tasks,
enough to establish that "give the model verified facts" is a recognised technique with a
recognised failure mode. Do not over-invest.
