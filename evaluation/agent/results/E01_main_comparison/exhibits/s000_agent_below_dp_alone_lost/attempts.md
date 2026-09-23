# Every candidate of tsvc/s000 · default · rep1 (E01_main_comparison/runs/e1_a/benchmarks/tsvc/s000/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:79 — passed the gate

```diff
--- s000.c
+++ s000.c
@@ -133,12 +133,15 @@
 
 static real_t kernel_s000(void)
 {
+    real_t *b_snapshot = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
     for (int nl = 0; nl < R; nl++) {
+        memcpy(b_snapshot, b, (size_t)LEN_1D * sizeof(real_t));
         for (int i = 0; i < LEN_1D; i++) {
-            a[i] = b[i] + 1;
+            a[i] = b_snapshot[i] + 1;
         }
         pb_mix(nl);
     }
+    free(b_snapshot);
     return (real_t)0;
 }
 
```

## 2. Phase B · region 1:82 · do_all — rejected at `tsan`

```
Race detected:
WARNING: ThreadSanitizer: data race (pid=3812588)
  Write of size 8 at 0x7ffff7c20030 by thread T10:
    #0 kernel_s000.omp_outlined_debug__ /tmp/dp_agent_val_ueppix50/s000.c:141:18 (tsan_binary+0xe9b06) (BuildId: 5a9c8e9c847764dbf753ebedf01b11b15feca425)
    #1 kernel_s000.omp_outlined /tmp/dp_agent_val_ueppix50/s000.c:137:5 (tsan_binary+0xe9b06)
    #2 __kmp_invoke_microtask <null> (libomp.so.5+0xe59b8) (BuildId: d91221260262a3d206b469a18cea4fa6f58113ee)
```

```diff
--- s000.c
+++ s000.c
@@ -134,6 +134,7 @@
 static real_t kernel_s000(void)
 {
     real_t *b_snapshot = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
+    #pragma omp parallel for shared(b_snapshot) 
     for (int nl = 0; nl < R; nl++) {
         memcpy(b_snapshot, b, (size_t)LEN_1D * sizeof(real_t));
         for (int i = 0; i < LEN_1D; i++) {
```

## 3. Phase B · region 1:86 · do_all — passed the gate

```diff
--- s000.c
+++ s000.c
@@ -136,6 +136,7 @@
     real_t *b_snapshot = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
     for (int nl = 0; nl < R; nl++) {
         memcpy(b_snapshot, b, (size_t)LEN_1D * sizeof(real_t));
+        #pragma omp parallel for shared(b_snapshot) 
         for (int i = 0; i < LEN_1D; i++) {
             a[i] = b_snapshot[i] + 1;
         }
```

