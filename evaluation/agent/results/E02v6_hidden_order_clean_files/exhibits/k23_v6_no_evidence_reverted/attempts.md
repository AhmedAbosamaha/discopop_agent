# Every candidate of tsvc_c2/k23 · no_evidence_b1_nospeed_v4 · rep1 (E02v6_hidden_order_clean_files/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:2 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
@@ -4,7 +4,7 @@
 {
     for (int nl = 0; nl < iterations; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
-            u[i] += w[i] * c[i];
+            u[i] = u[i] + w[i] * c[i];
             v[i] = x[i] * d[i] + c[i];
         }
         dummy(a, b, c, d, e);
```

## 2. Phase A · region 0:0 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 219338.67935999352
  got:      pb_sum 217242.46725909595
--- expected (original) ---
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
@@ -5,6 +5,8 @@
     for (int nl = 0; nl < iterations; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
             u[i] += w[i] * c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             v[i] = x[i] * d[i] + c[i];
         }
         dummy(a, b, c, d, e);
```

## 3. Phase A · region 1:5 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 219338.67935999352
  got:      pb_sum 217242.46725909595
--- expected (original) ---
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e2v6_agent_1/benchmarks/tsvc_c2/k23/no_evidence_b1_nospeed_v4/claude-haiku-4-5-20251001/rep1/work/k23.c
@@ -5,6 +5,8 @@
     for (int nl = 0; nl < iterations; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
             u[i] += w[i] * c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             v[i] = x[i] * d[i] + c[i];
         }
         dummy(a, b, c, d, e);
```

