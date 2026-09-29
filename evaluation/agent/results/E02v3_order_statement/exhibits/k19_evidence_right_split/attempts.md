# Every candidate of tsvc_b1/k19 · full_b1_nospeed_v3 · rep1 (E02v3_order_statement/runs/e2v3_k19/benchmarks/tsvc_b1/k19/full_b1_nospeed_v3/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:14 — passed the gate

```diff
--- k19.c
+++ k19.c
@@ -16,8 +16,10 @@
 {
     for (int nl = 0; nl < R; nl++) {
         for (long i = 1; i < LEN_1D; i++) {
+            v[jv[i]] = u[ku[i]] * d[i] + c[i];
+        }
+        for (long i = 1; i < LEN_1D; i++) {
             u[ju[i]] += v[kv[i]] * c[i];
-            v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
         pb_mix(nl);
     }
```

## 2. Phase A-D40 · region 1:14 — passed the gate

```diff
--- k19.c
+++ k19.c
@@ -15,6 +15,7 @@
 static real_t kernel_k19(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        #pragma omp parallel for 
         for (long i = 1; i < LEN_1D; i++) {
             v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
```

## 3. Phase B · region 1:17 · do_all — passed the gate

```diff
--- k19.c
+++ k19.c
@@ -15,6 +15,7 @@
 static real_t kernel_k19(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        #pragma omp parallel for 
         for (long i = 1; i < LEN_1D; i++) {
             v[jv[i]] = u[ku[i]] * d[i] + c[i];
         }
```

