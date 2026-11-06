"""E11 part 2, descriptive: RepoOMP's validate_candidate (primitive_adder.py) on a candidate as written and with the
loop counter `long i` written `int i` in both the original function and the candidate.
    python3 -I validator_long_counter_test.py <original k23.c> <candidate.c> kernel_k23
"""
import sys, re
sys.path.insert(0, "/Users/ahmedsamir/discopop_agent/evaluation/benchmarks/RepoOMP/Method/primitive_addition")
sys.path.insert(0, "/Users/ahmedsamir/discopop_agent/evaluation/benchmarks/RepoOMP/Method")
import primitive_adder as pa
orig_file, cand_file, name = sys.argv[1], sys.argv[2], sys.argv[3]
orig = open(orig_file).read(); cand = open(cand_file).read()
rec = {"name": name, "file": orig_file}
of = [f for f in pa.extract_function_ranges(orig, orig_file) if f["name"] == name][0]["text"]
print("as written:", pa.validate_candidate(of, cand, rec, refactor=True))
print("'long i' -> 'int i' in both:", pa.validate_candidate(of.replace("long i", "int i"), cand.replace("long i", "int i"), rec, refactor=True))
