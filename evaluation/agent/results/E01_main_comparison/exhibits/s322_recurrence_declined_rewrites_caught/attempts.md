# Every candidate of tsvc/s322 · default · rep1 (E01_main_comparison/runs/e1_d/benchmarks/tsvc/s322/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:86 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 95541.829366611681
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,9 +134,14 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        real_t *temp_a = (real_t *)malloc(LEN_1D * sizeof(real_t));
+        memcpy(temp_a, a, LEN_1D * sizeof(real_t));
+
         for (int i = 2; i < LEN_1D; i++) {
-            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+            a[i] = temp_a[i] + temp_a[i - 1] * b[i] + temp_a[i - 2] * c[i];
         }
+
+        free(temp_a);
         pb_mix(nl);
     }
     return (real_t)0;
```

## 2. Phase A · region 1:86 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 246468.89058322748
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,8 +134,10 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 2; i < LEN_1D; i++) {
-            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        for (int offset = 0; offset < 3; offset++) {
+            for (int i = 2 + offset; i < LEN_1D; i += 3) {
+                a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+            }
         }
         pb_mix(nl);
     }
```

## 3. Phase A · region 1:86 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 630655.14856794418
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -135,7 +135,10 @@
 {
     for (int nl = 0; nl < R; nl++) {
         for (int i = 2; i < LEN_1D; i++) {
-            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+            a[i] = a[i] + a[i - 1] * b[i];
+        }
+        for (int i = 2; i < LEN_1D; i++) {
+            a[i] = a[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
     }
```

## 4. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 246468.89058322748
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,7 +134,13 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 2; i < LEN_1D; i++) {
+        for (int i = 2; i < LEN_1D; i += 3) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 3; i < LEN_1D; i += 3) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 4; i < LEN_1D; i += 3) {
             a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
```

## 5. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 515830.83687410731
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,7 +134,10 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 2; i < LEN_1D; i++) {
+        for (int i = 2; i < LEN_1D; i += 2) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 3; i < LEN_1D; i += 2) {
             a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
```

## 6. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 95541.829366611695
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -133,12 +133,17 @@
 
 static real_t kernel_s322(void)
 {
+    real_t* temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
     for (int nl = 0; nl < R; nl++) {
         for (int i = 2; i < LEN_1D; i++) {
-            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+            temp[i] = a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 2; i < LEN_1D; i++) {
+            a[i] = a[i] + temp[i];
         }
         pb_mix(nl);
     }
+    free(temp);
     return (real_t)0;
 }
 
```

## 7. Phase A · region 1:84 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 246468.89058322748
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,7 +134,13 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 2; i < LEN_1D; i++) {
+        for (int i = 2; i < LEN_1D; i += 3) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 3; i < LEN_1D; i += 3) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 4; i < LEN_1D; i += 3) {
             a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
```

## 8. Phase A · region 1:84 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 3038051.4038706799
  got:      pb_sum 515830.83687410731
--- expected (original) ---
```

```diff
--- s322.c
+++ s322.c
@@ -134,7 +134,10 @@
 static real_t kernel_s322(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 2; i < LEN_1D; i++) {
+        for (int i = 2; i < LEN_1D; i += 2) {
+            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+        }
+        for (int i = 3; i < LEN_1D; i += 2) {
             a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
```

## 9. Phase A · region 1:84 — passed the gate

```diff
--- s322.c
+++ s322.c
@@ -133,12 +133,15 @@
 
 static real_t kernel_s322(void)
 {
+    real_t *a_old = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
     for (int nl = 0; nl < R; nl++) {
+        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
         for (int i = 2; i < LEN_1D; i++) {
-            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
+            a[i] = a_old[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
         }
         pb_mix(nl);
     }
+    free(a_old);
     return (real_t)0;
 }
 
```

## 10. Phase B · region 1:87 · do_all — rejected at `tsan`

```
Race detected:
WARNING: ThreadSanitizer: data race (pid=3846420)
  Write of size 8 at 0x7ffff7c20010 by thread T4:
    #0 kernel_s322.omp_outlined_debug__ /tmp/dp_agent_val_7stli6kj/s322.c:141:18 (tsan_binary+0xe9c4f) (BuildId: 73eddef9a77563bb130ba2c85dbdd827412a66d9)
    #1 kernel_s322.omp_outlined /tmp/dp_agent_val_7stli6kj/s322.c:137:5 (tsan_binary+0xe9c4f)
    #2 __kmp_invoke_microtask <null> (libomp.so.5+0xe59b8) (BuildId: d91221260262a3d206b469a18cea4fa6f58113ee)
```

```diff
--- s322.c
+++ s322.c
@@ -134,6 +134,7 @@
 static real_t kernel_s322(void)
 {
     real_t *a_old = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
+    #pragma omp parallel for shared(a_old) 
     for (int nl = 0; nl < R; nl++) {
         memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
         for (int i = 2; i < LEN_1D; i++) {
```

