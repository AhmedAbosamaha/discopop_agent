#!/usr/bin/env python3
"""Compare generated/reference source inventory and measured reports."""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Compare RepoOMP results against AAAI reference inventory")
    ap.add_argument("--matrix", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args(); matrix = json.loads(Path(args.matrix).read_text())
    rows = []
    groups = {}
    for r in matrix["results"]:
        row = {"suite": r.get("suite"), "name": r.get("name"), "variant": r.get("variant"), "reference": r.get("reference"), "functional": bool(r.get("verified", False)), "compiled": bool(r.get("compile", False))}
        if r.get("best_time") is not None: row["best_time"] = r["best_time"]
        if r.get("program_time") is not None: row["program_time"] = r["program_time"]
        if r.get("sequential_time") is not None: row["sequential_time"] = r["sequential_time"]
        if r.get("speedup_vs_sequential") is not None: row["speedup_vs_sequential"] = r["speedup_vs_sequential"]
        row["status"] = "functional-pass" if row["compiled"] and row["functional"] else "not-accepted"
        rows.append(row)
        groups.setdefault((row["suite"], row["name"]), []).append(row)
    parity = []
    for (suite, name), variants in groups.items():
        times = {v.get("variant"): v.get("best_time", v.get("program_time")) for v in variants}
        ref_time = times.get("aaai")
        item = {"suite": suite, "name": name, "times": times, "aaai_time": ref_time}
        if ref_time is not None:
            for variant, value in times.items():
                if value is not None:
                    item[f"{variant}_relative_to_aaai"] = value / ref_time
        generated = next((v for v in variants if v.get("variant") == "generated"), None)
        generated_ratio = item.get("generated_relative_to_aaai")
        item["generated_functional"] = bool(generated and generated.get("compiled") and generated.get("functional"))
        item["generated_performance_pass"] = bool(item["generated_functional"] and generated_ratio is not None and generated_ratio <= 1.0)
        item["generated_accepted"] = bool(item["generated_performance_pass"])
        generated_identity = next((v.get("source_identity_parity") for v in variants if v.get("variant") == "generated"), False)
        item["generated_source_identity_parity"] = bool(generated_identity)
        if item["generated_source_identity_parity"]:
            item["generated_acceptance_basis"] = "exemplar-source-identity-plus-independent-verification"
        else:
            item["generated_acceptance_basis"] = "independent-verification-and-timing"
        parity.append(item)
    report = {"schema": "repoomp.reference-comparison.v2", "rows": rows, "parity": parity, "warning": "Timing parity requires identical workload, thread count, compiler, flags, and input. This report records measurements; it does not convert functional success into method parity."}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2)); print(f"[compare] wrote {args.out} rows={len(rows)}")

if __name__ == "__main__": main()
