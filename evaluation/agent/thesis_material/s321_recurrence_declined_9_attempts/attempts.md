# Every candidate of tsvc/s321 · default · rep1 (e1_smoke5/benchmarks/tsvc/s321/default/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 1:86 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 62629.192629100035
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -133,12 +133,25 @@
 
 static real_t kernel_s321(void)
 {
+    real_t *a_new = (real_t*)malloc((size_t)LEN_1D * sizeof(real_t));
+    if (!a_new) return (real_t)0;
+
     for (int nl = 0; nl < R; nl++) {
+        /* Compute new values in a_new, reading from constant a.
+         * This breaks the loop-carried dependence: each iteration i writes to
+         * a unique location a_new[i] and reads only from a[i-1], a[i], and b[i].
+         */
+        a_new[0] = a[0];
         for (int i = 1; i < LEN_1D; i++) {
-            a[i] += a[i-1] * b[i];
+            a_new[i] = a[i-1] * b[i] + a[i];
+        }
+        /* Copy results back to a for pb_mix and next iteration */
+        for (int i = 0; i < LEN_1D; i++) {
+            a[i] = a_new[i];
         }
         pb_mix(nl);
     }
+    free(a_new);
     return (real_t)0;
 }
 
```

## 2. Phase A · region 1:86 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 8.3522091503660674e+28
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,8 +134,27 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
-            a[i] += a[i-1] * b[i];
+        /* Split into ordered sub-passes over disjoint (odd/even) elements.
+         * Each pass updates a subset with no intra-pass dependencies.
+         * Repeat passes to allow wavefront propagation through the array.
+         */
+        int num_rounds = 1;
+        int tmp = LEN_1D;
+        while (tmp > 1) { tmp >>= 1; num_rounds++; }
+
+        for (int round = 0; round < num_rounds; round++) {
+            /* Odd-indexed pass: a[1], a[3], a[5], ...
+             * Each reads a[i-1] (even, not updated in this pass).
+             */
+            for (int i = 1; i < LEN_1D; i += 2) {
+                a[i] += a[i-1] * b[i];
+            }
+            /* Even-indexed pass: a[2], a[4], a[6], ...
+             * Each reads a[i-1] (odd, updated by previous odd pass).
+             */
+            for (int i = 2; i < LEN_1D; i += 2) {
+                a[i] += a[i-1] * b[i];
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
  expected: pb_sum 584408.5576695262
  got:      pb_sum 135301.3395114119
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,7 +134,19 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
+        /* Split into ordered sub-passes over disjoint (odd/even) elements.
+         * Each pass updates a subset with no intra-pass dependencies → Do-All.
+         * Odd-indexed pass: a[1], a[3], a[5], ...
+         * Each iteration reads a[i-1] (even, untouched in this pass).
+         */
+        for (int i = 1; i < LEN_1D; i += 2) {
+            a[i] += a[i-1] * b[i];
+        }
+        /* Even-indexed pass: a[2], a[4], a[6], ...
+         * Each iteration reads a[i-1] (odd, updated by preceding pass).
+         * No intra-pass dependencies because even indices do not depend on each other.
+         */
+        for (int i = 2; i < LEN_1D; i += 2) {
             a[i] += a[i-1] * b[i];
         }
         pb_mix(nl);
```

## 4. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 108004.26536266915
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,7 +134,12 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
+        /* Process even indices: each reads from odd-indexed a (unchanged in this pass) */
+        for (int i = 2; i < LEN_1D; i += 2) {
+            a[i] += a[i-1] * b[i];
+        }
+        /* Process odd indices: each reads from even-indexed a (now updated from pass 1) */
+        for (int i = 1; i < LEN_1D; i += 2) {
             a[i] += a[i-1] * b[i];
         }
         pb_mix(nl);
```

## 5. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 135301.3395114119
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,7 +134,12 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
+        /* Process odd indices: each reads from even-indexed a (elements 0, 2, 4, ...) */
+        for (int i = 1; i < LEN_1D; i += 2) {
+            a[i] += a[i-1] * b[i];
+        }
+        /* Process even indices: each reads from odd-indexed a (now updated from pass 1) */
+        for (int i = 2; i < LEN_1D; i += 2) {
             a[i] += a[i-1] * b[i];
         }
         pb_mix(nl);
```

## 6. Phase A · region 1:89 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 6.6918688757007924e+57
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,8 +134,16 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
-            a[i] += a[i-1] * b[i];
+        /* Logarithmic iterations: each round allows values to propagate one doubling distance */
+        for (int round = 0; round < 32; round++) {  /* log2(LEN_1D) rounds for full propagation */
+            /* Process odd indices: independent within the round */
+            for (int i = 1; i < LEN_1D; i += 2) {
+                a[i] += a[i-1] * b[i];
+            }
+            /* Process even indices: independent within the round */
+            for (int i = 2; i < LEN_1D; i += 2) {
+                a[i] += a[i-1] * b[i];
+            }
         }
         pb_mix(nl);
     }
```

## 7. Phase A · region 1:84 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 62629.192629100035
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -133,12 +133,17 @@
 
 static real_t kernel_s321(void)
 {
+    real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
     for (int nl = 0; nl < R; nl++) {
         for (int i = 1; i < LEN_1D; i++) {
-            a[i] += a[i-1] * b[i];
+            a_new[i] = a[i] + a[i-1] * b[i];
+        }
+        for (int i = 1; i < LEN_1D; i++) {
+            a[i] = a_new[i];
         }
         pb_mix(nl);
     }
+    free(a_new);
     return (real_t)0;
 }
 
```

## 8. Phase A · region 1:84 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 135301.3395114119
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,7 +134,10 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
+        for (int i = 1; i < LEN_1D; i += 2) {
+            a[i] += a[i-1] * b[i];
+        }
+        for (int i = 2; i < LEN_1D; i += 2) {
             a[i] += a[i-1] * b[i];
         }
         pb_mix(nl);
```

## 9. Phase A · region 1:84 — rejected at `correctness`

```
Program output changed — the patched program is NOT semantically equivalent to the original.
output differs and no numerical slack is in effect
first difference at line 2:
  expected: pb_sum 584408.5576695262
  got:      pb_sum 135301.3395114119
--- expected (original) ---
```

```diff
--- s321.c
+++ s321.c
@@ -134,7 +134,10 @@
 static real_t kernel_s321(void)
 {
     for (int nl = 0; nl < R; nl++) {
-        for (int i = 1; i < LEN_1D; i++) {
+        for (int i = 1; i < LEN_1D; i += 2) {
+            a[i] += a[i-1] * b[i];
+        }
+        for (int i = 2; i < LEN_1D; i += 2) {
             a[i] += a[i-1] * b[i];
         }
         pb_mix(nl);
```

