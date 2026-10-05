# Every candidate of tsvc_b1/k19 · no_evidence_b1_nospeed_v3 · rep1 (E02v3_order_statement/runs/e2v3_k19/benchmarks/tsvc_b1/k19/no_evidence_b1_nospeed_v3/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:14 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 221428.5043599935
  got:      pb_sum 219332.29225909594
--- expected (original) ---
```

```diff
--- k19.c
+++ k19.c
@@ -17,6 +17,8 @@
     for (int nl = 0; nl < R; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
             u[ju[i]] += v[kv[i]] * c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
         pb_mix(nl);
```

## 2. Phase A · region 1:12 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 221428.5043599935
  got:      pb_sum 219332.29225909594
--- expected (original) ---
```

```diff
--- k19.c
+++ k19.c
@@ -17,6 +17,8 @@
     for (int nl = 0; nl < R; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
             u[ju[i]] += v[kv[i]] * c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
         pb_mix(nl);
```

## 3. Phase A · region 1:17 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 221428.5043599935
  got:      pb_sum 219332.29225909594
--- expected (original) ---
```

```diff
--- k19.c
+++ k19.c
@@ -17,6 +17,8 @@
     for (int nl = 0; nl < R; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
             u[ju[i]] += v[kv[i]] * c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
         pb_mix(nl);
```

