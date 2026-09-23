# Every candidate of tsvc/s211 · default · rep1 (E01_main_comparison/preflight/e1_smoke5/benchmarks/tsvc/s211/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:81 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum -184016.80651324999
  got:      pb_sum -377280.26117025089
--- expected (original) ---
```

```diff
--- s211.c
+++ s211.c
@@ -134,7 +134,11 @@
 static real_t kernel_s211(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D-1; i++) {
+        for (int i = 1; i < LEN_1D-1; i += 2) {
+            a[i] = b[i - 1] + c[i] * d[i];
+            b[i] = b[i + 1] - e[i] * d[i];
+        }
+        for (int i = 2; i < LEN_1D-1; i += 2) {
             a[i] = b[i - 1] + c[i] * d[i];
             b[i] = b[i + 1] - e[i] * d[i];
         }
```

## 2. Phase A · region 1:81 — passed the gate

```diff
--- s211.c
+++ s211.c
@@ -135,8 +135,10 @@
 {
     for (int nl = 0; nl < R; nl++) {
         for (int i = 1; i < LEN_1D-1; i++) {
+            b[i] = b[i + 1] - e[i] * d[i];
+        }
+        for (int i = 1; i < LEN_1D-1; i++) {
             a[i] = b[i - 1] + c[i] * d[i];
-            b[i] = b[i + 1] - e[i] * d[i];
         }
         pb_mix(nl);
     }
```

## 3. Phase B · region 1:84 · do_all — rejected at `tsan`

```
Race detected:
WARNING: ThreadSanitizer: data race (pid=3173919)
  Read of size 8 at 0x7ffff663d6c8 by thread T3:
    #0 kernel_s211.omp_outlined_debug__ /tmp/dp_agent_val_7079x69z/s211.c:139:20 (tsan_binary+0xe9ca8) (BuildId: 6fb0fb5e72d366883af228d9ba5d4d1ce0d56e8d)
    #1 kernel_s211.omp_outlined /tmp/dp_agent_val_7079x69z/s211.c:137:9 (tsan_binary+0xe9ca8)
    #2 __kmp_invoke_microtask <null> (libomp.so.5+0xe59b8) (BuildId: d91221260262a3d206b469a18cea4fa6f58113ee)
```

```diff
--- s211.c
+++ s211.c
@@ -134,6 +134,7 @@
 static real_t kernel_s211(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        #pragma omp parallel for 
         for (int i = 1; i < LEN_1D-1; i++) {
             b[i] = b[i + 1] - e[i] * d[i];
         }
```

## 4. Phase B · region 1:90 · do_all — passed the gate

```diff
--- s211.c
+++ s211.c
@@ -137,6 +137,7 @@
         for (int i = 1; i < LEN_1D-1; i++) {
             b[i] = b[i + 1] - e[i] * d[i];
         }
+        #pragma omp parallel for 
         for (int i = 1; i < LEN_1D-1; i++) {
             a[i] = b[i - 1] + c[i] * d[i];
         }
```

