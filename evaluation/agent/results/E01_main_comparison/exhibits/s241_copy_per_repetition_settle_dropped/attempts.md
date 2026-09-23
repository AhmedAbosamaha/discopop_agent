# Every candidate of tsvc/s241 · default · rep2 (E01_main_comparison/runs/e1_r_a/benchmarks/tsvc/s241/default/claude-haiku-4-5-20251001/rep2)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:81 — passed the gate

```diff
--- s241.c
+++ s241.c
@@ -134,10 +134,18 @@
 static real_t kernel_s241(void)
 {
     for (int nl = 0; nl < R; nl++) {
+        real_t *a_old = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
+        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
+
         for (int i = 0; i < LEN_1D-1; i++) {
             a[i] = b[i] * c[i  ] * d[i];
-            b[i] = a[i] * a[i+1] * d[i];
         }
+
+        for (int i = 0; i < LEN_1D-1; i++) {
+            b[i] = a[i] * a_old[i+1] * d[i];
+        }
+
+        free(a_old);
         pb_mix(nl);
     }
     return (real_t)0;
```

## 2. Phase B · region 1:86 · do_all — passed the gate

```diff
--- s241.c
+++ s241.c
@@ -137,6 +137,7 @@
         real_t *a_old = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
         memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
 
+        #pragma omp parallel for 
         for (int i = 0; i < LEN_1D-1; i++) {
             a[i] = b[i] * c[i  ] * d[i];
         }
```

## 3. Phase B · region 1:91 · do_all — passed the gate

```diff
--- s241.c
+++ s241.c
@@ -142,6 +142,7 @@
             a[i] = b[i] * c[i  ] * d[i];
         }
 
+        #pragma omp parallel for shared(a_old) 
         for (int i = 0; i < LEN_1D-1; i++) {
             b[i] = a[i] * a_old[i+1] * d[i];
         }
```

