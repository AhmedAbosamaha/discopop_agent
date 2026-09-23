# Every candidate of tsvc/s291 · default · rep1 (E01_main_comparison/runs/e1_r_b/benchmarks/tsvc/s291/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:79 — passed the gate

```diff
--- s291.c
+++ s291.c
@@ -133,12 +133,9 @@
 
 static real_t kernel_s291(void)
 {
-    int im1;
     for (int nl = 0; nl < R; nl++) {
-        im1 = LEN_1D-1;
         for (int i = 0; i < LEN_1D; i++) {
-            a[i] = (b[i] + b[im1]) * (real_t).5;
-            im1 = i;
+            a[i] = (b[i] + b[(i == 0) ? (LEN_1D - 1) : (i - 1)]) * (real_t).5;
         }
         pb_mix(nl);
     }
```

## 2. Phase B · region 1:81 · do_all — rejected at `tsan`

```
Race detected:
WARNING: ThreadSanitizer: data race (pid=3367415)
  Write of size 8 at 0x7ffff7c20000 by thread T16:
    #0 kernel_s291.omp_outlined_debug__ /tmp/dp_agent_val_o92h978p/s291.c:139:18 (tsan_binary+0xe9acb) (BuildId: 1c987a3ac6bd059c70672968165075042255f252)
    #1 kernel_s291.omp_outlined /tmp/dp_agent_val_o92h978p/s291.c:136:5 (tsan_binary+0xe9acb)
    #2 __kmp_invoke_microtask <null> (libomp.so.5+0xe59b8) (BuildId: d91221260262a3d206b469a18cea4fa6f58113ee)
```

```diff
--- s291.c
+++ s291.c
@@ -133,6 +133,7 @@
 
 static real_t kernel_s291(void)
 {
+    #pragma omp parallel for 
     for (int nl = 0; nl < R; nl++) {
         for (int i = 0; i < LEN_1D; i++) {
             a[i] = (b[i] + b[(i == 0) ? (LEN_1D - 1) : (i - 1)]) * (real_t).5;
```

## 3. Phase B · region 1:84 · do_all — passed the gate

```diff
--- s291.c
+++ s291.c
@@ -134,6 +134,7 @@
 static real_t kernel_s291(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        #pragma omp parallel for 
         for (int i = 0; i < LEN_1D; i++) {
             a[i] = (b[i] + b[(i == 0) ? (LEN_1D - 1) : (i - 1)]) * (real_t).5;
         }
```

