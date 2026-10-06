# E2-v6 — the registered tests, as `e2b1_stats.py` writes them

The tool is E2-B1's; its tables carry E2-B1's row names. How to read them here:

| folder | the registered test | X against Y | read the tool's rows as |
|---|---|---|---|
| `v6_i/` | **V6-i, confirmatory** — the evidence effect inside the agent at one attempt | `full_b1_nospeed_v4` against `no_evidence_b1_nospeed_v4` | row `E2B1-i` is V6-i. Row `E2B1-iii` (unsafe programs, the agent with evidence against Haiku alone) is descriptive in E2-v6 |
| `v6_ii/` | **V6-ii** — without evidence, three attempts with feedback against one | `no_evidence_nospeed_v4` against `no_evidence_b1_nospeed_v4` | row `E2B1-i` is V6-ii: "agent, full evidence" stands for THREE attempts without evidence, "agent, no evidence" for ONE attempt without evidence |

- The rows `E2B1-ii-twins` and `E2B1-ii-interaction` have no data and the tool's header says "NOT ESTABLISHED" for them: E2-v6 has no twin arms (they are not part of its registration).
- Family size: V6-i was registered with M = 51; the amendment added V6-ii to the family (M = 52). Both folders are computed with `--family-size 52` (the larger family only widens the bound).
- `models_alone.md` (`e12_stats.py --set e2v6`): every setup per unit, each against the agent with evidence at one attempt, Fisher's exact test, one-sided — descriptive.
- Everything the registration lists as descriptive is in `../analysis/e2v6_readout.md` (`tools/e2v6_readout.py`).

Commands (from `evaluation/agent`, `C=results/E02v6_hidden_order_clean_files/checks/e2v6_race_check`):

    tools/e2b1_stats.py e2v6_agent_1 e2v6_agent_2 e2v6_agent_3 e2v6_bare_haiku t0_11_c2_a t0_11_c2_b t0_11_c2_c \
        --population config/e2v6_population.json --agent-full full_b1_nospeed_v4 --agent-none no_evidence_b1_nospeed_v4 \
        --twin-full twin_full_nospeed_v4 --twin-none twin_no_evidence_nospeed_v4 --bare bare_llm_nospeed_v4 --family-size 52 \
        --races $C/haiku/results.jsonl --races $C/control_full_b1/results.jsonl --races $C/control_none_b1/results.jsonl --out …/stats/v6_i
    tools/e2b1_stats.py e2v6_agent_1 e2v6_agent_2 e2v6_agent_3 e2v6_fb_1 e2v6_fb_2 e2v6_fb_3 \
        --population config/e2v6_population.json --agent-full no_evidence_nospeed_v4 --agent-none no_evidence_b1_nospeed_v4 \
        --twin-full twin_full_nospeed_v4 --twin-none twin_no_evidence_nospeed_v4 --bare bare_llm_nospeed_v4 --family-size 52 \
        --races $C/control_none/results.jsonl --races $C/control_none_b1/results.jsonl --out …/stats/v6_ii
    tools/e12_stats.py --set e2v6 --races $C/<each of the eight parts>/results.jsonl --out …/stats
    tools/e2v6_readout.py --out …/analysis
