# Every candidate of tsvc/s121 · default · rep1 (e1_r_a/benchmarks/tsvc/s121/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:81 — passed the gate

```diff
--- s121.c
+++ s121.c
@@ -134,13 +134,20 @@
 static real_t kernel_s121(void)
 {
     int j;
+    real_t *temp = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
+    if (!temp) return (real_t)0;
+
     for (int nl = 0; nl < R; nl++) {
         for (int i = 0; i < LEN_1D-1; i++) {
             j = i + 1;
-            a[i] = a[j] + b[i];
+            temp[i] = a[j] + b[i];
+        }
+        for (int i = 0; i < LEN_1D-1; i++) {
+            a[i] = temp[i];
         }
         pb_mix(nl);
     }
+    free(temp);
     return (real_t)0;
 }
 
```

## 2. Phase B · region 1:86 · do_all — passed the gate

```diff
--- s121.c
+++ s121.c
@@ -138,6 +138,7 @@
     if (!temp) return (real_t)0;
 
     for (int nl = 0; nl < R; nl++) {
+        #pragma omp parallel for private(j) shared(temp) 
         for (int i = 0; i < LEN_1D-1; i++) {
             j = i + 1;
             temp[i] = a[j] + b[i];
```

## 3. Phase B · region 1:92 · do_all — passed the gate

```diff
--- s121.c
+++ s121.c
@@ -142,6 +142,7 @@
             j = i + 1;
             temp[i] = a[j] + b[i];
         }
+        #pragma omp parallel for shared(temp) 
         for (int i = 0; i < LEN_1D-1; i++) {
             a[i] = temp[i];
         }
```

