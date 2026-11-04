# Every candidate of llnl_c1/lulesh · llm_pragmas_v5 · rep1 (E06_lulesh/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1)

In the order the agent built them. `passed` = the gate accepted it; what happened to it after (kept, reverted, dropped for speed, dropped by Settle) is in `console.txt`.

## 1. Phase A · region 2:355 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -737,6 +737,7 @@
 {
   Index_t numNode = domain.numNode() ;
 
+#pragma omp parallel for shared(domain) schedule(static)
   for (Index_t i=0; i<numNode; ++i) {
      domain.fx(i) = Real_t(0.0) ;
      domain.fy(i) = Real_t(0.0) ;
@@ -751,6 +752,7 @@
 void CalcAccelerationForNodes(Domain &domain, Index_t numNode)
 {
 
+#pragma omp parallel for shared(domain) schedule(static)
    for (Index_t i = 0; i < numNode; ++i) {
       domain.xdd(i) = domain.fx(i) / domain.nodalMass(i);
       domain.ydd(i) = domain.fy(i) / domain.nodalMass(i);
@@ -766,16 +768,19 @@
 
    {
       if (!domain.symmXempty() != 0) {
+#pragma omp parallel for shared(domain) schedule(static)
          for(Index_t i=0 ; i<numNodeBC ; ++i)
             domain.xdd(domain.symmX(i)) = Real_t(0.0) ;
       }
 
       if (!domain.symmYempty() != 0) {
+#pragma omp parallel for shared(domain) schedule(static)
          for(Index_t i=0 ; i<numNodeBC ; ++i)
             domain.ydd(domain.symmY(i)) = Real_t(0.0) ;
       }
 
       if (!domain.symmZempty() != 0) {
+#pragma omp parallel for shared(domain) schedule(static)
          for(Index_t i=0 ; i<numNodeBC ; ++i)
             domain.zdd(domain.symmZ(i)) = Real_t(0.0) ;
       }
@@ -787,6 +792,7 @@
                           Index_t numNode)
 {
 
+#pragma omp parallel for shared(domain, dt, u_cut) schedule(static)
    for ( Index_t i = 0 ; i < numNode ; ++i )
    {
      Real_t xdtmp, ydtmp, zdtmp ;
@@ -808,6 +814,7 @@
 static inline
 void CalcPositionForNodes(Domain &domain, const Real_t dt, Index_t numNode)
 {
+#pragma omp parallel for shared(domain, dt) schedule(static)
    for ( Index_t i = 0 ; i < numNode ; ++i )
    {
      domain.x(i) += domain.xd(i) * dt ;
@@ -1063,6 +1070,7 @@
                              Real_t deltaTime, Index_t numElem )
 {
 
+#pragma omp parallel for shared(domain, deltaTime) schedule(static)
   for( Index_t k=0 ; k<numElem ; ++k )
   {
     Real_t B[3][8] ;
@@ -1128,6 +1136,7 @@
 
       CalcKinematicsForElems(domain, deltatime, numElem) ;
 
+#pragma omp parallel for shared(domain) schedule(static)
       for ( Index_t k=0 ; k<numElem ; ++k )
       {
          Real_t vdov = domain.dxx(k) + domain.dyy(k) + domain.dzz(k) ;
@@ -1152,6 +1161,7 @@
 {
    Index_t numElem = domain.numElem();
 
+#pragma omp parallel for shared(domain, numElem) schedule(static)
    for (Index_t i = 0 ; i < numElem ; ++i ) {
       const Real_t ptiny = Real_t(1.e-36) ;
       Real_t ax,ay,az ;
@@ -1446,6 +1456,7 @@
 {
… (truncated)
```

## 2. Phase A-tier1 · region 1:377 — rejected at `openmp_compile`

```
OpenMP compile failed (loop not in OpenMP-canonical form):
/tmp/dp_agent_val_mriszk73/_dp_proj_tsan_binary/lulesh.cc:1882:1: error: expected statement
 1882 | }
      | ^
1 error generated.
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 10:11:40.590363881 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 10:16:41.562213186 +0000
@@ -1866,6 +1866,10 @@
 static inline
 void LagrangeElements(Domain& domain, Index_t numElem)
 {
+  #pragma omp parallel
+  #pragma omp single
+  {
+  #pragma omp task
   CalcLagrangeElements(domain) ;
 
   CalcQForElems(domain) ;
@@ -1874,6 +1878,8 @@
 
   UpdateVolumesForElems(domain,
                         domain.v_cut(), numElem) ;
+#pragma omp task
+}
 }
 
 static inline
```

## 3. Phase A · region 1:377 — rejected at `tsan`

```
Race detected:
WARNING: ThreadSanitizer: data race (pid=619266)
  Write of size 8 at 0x72ac0005b000 by main thread:
    #0 CalcKinematicsForElems(Domain&, double, int) (.omp_outlined_debug__) /tmp/dp_agent_val_2012ax1x/_dp_proj_tsan_binary/lulesh.cc:1094:20 (tsan_binary+0xec0
    #1 CalcKinematicsForElems(Domain&, double, int) (.omp_outlined) /tmp/dp_agent_val_2012ax1x/_dp_proj_tsan_binary/lulesh.cc:1073:1 (tsan_binary+0xec013)
    #2 __kmp_invoke_microtask <null> (libomp.so.5+0xe59b8) (BuildId: d91221260262a3d206b469a18cea4fa6f58113ee)
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1866,14 +1866,29 @@
 static inline
 void LagrangeElements(Domain& domain, Index_t numElem)
 {
-  CalcLagrangeElements(domain) ;
-
-  CalcQForElems(domain) ;
-
-  ApplyMaterialPropertiesForElems(domain) ;
-
-  UpdateVolumesForElems(domain,
-                        domain.v_cut(), numElem) ;
+  /* Four independent phases of Lagrange calculation, each operating on the full domain.
+     No data dependencies between phases (confirmed by DiscoPoP).
+     Each phase can execute in parallel. */
+
+#pragma omp parallel for shared(domain, numElem) schedule(static)
+  for (int phase = 0; phase < 4; ++phase) {
+    if (phase == 0) {
+      /* Phase 0: Calculate Lagrangian strains and kinematics */
+      CalcLagrangeElements(domain);
+    }
+    else if (phase == 1) {
+      /* Phase 1: Calculate artificial viscosity Q */
+      CalcQForElems(domain);
+    }
+    else if (phase == 2) {
+      /* Phase 2: Apply material properties */
+      ApplyMaterialPropertiesForElems(domain);
+    }
+    else if (phase == 3) {
+      /* Phase 3: Update element volumes */
+      UpdateVolumesForElems(domain, domain.v_cut(), numElem);
+    }
+  }
 }
 
 static inline
```

## 4. Phase A · region 1:377 — rejected at `performance`

```
No speedup from parallelization: measured 0.95× (same binary, median of interleaved pairs; best at 1 thread 1056.3 ms vs best at all threads 1107.3 ms), below t
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1794,11 +1794,13 @@
     Real_t *vnewc = Allocate<Real_t>(numElem) ;
 
     {
+#pragma omp parallel for shared(domain, numElem, vnewc, eosvmin, eosvmax) schedule(static)
        for(Index_t i=0 ; i<numElem ; ++i) {
           vnewc[i] = domain.vnew(i) ;
        }
 
        if (eosvmin != Real_t(0.)) {
+#pragma omp parallel for shared(numElem, vnewc, eosvmin) schedule(static)
           for(Index_t i=0 ; i<numElem ; ++i) {
              if (vnewc[i] < eosvmin)
                 vnewc[i] = eosvmin ;
@@ -1806,12 +1808,14 @@
        }
 
        if (eosvmax != Real_t(0.)) {
+#pragma omp parallel for shared(numElem, vnewc, eosvmax) schedule(static)
           for(Index_t i=0 ; i<numElem ; ++i) {
              if (vnewc[i] > eosvmax)
                 vnewc[i] = eosvmax ;
           }
        }
 
+#pragma omp parallel for shared(domain, numElem, eosvmin, eosvmax) schedule(static)
        for (Index_t i=0; i<numElem; ++i) {
           Real_t vc = domain.v(i) ;
           if (eosvmin != Real_t(0.)) {
@@ -1850,6 +1854,7 @@
                            Real_t v_cut, Index_t length)
 {
    if (length != 0) {
+#pragma omp parallel for shared(domain, v_cut) schedule(static)
       for(Index_t i=0 ; i<length ; ++i) {
          Real_t tmpV = domain.vnew(i) ;
 
@@ -1866,14 +1871,27 @@
 static inline
 void LagrangeElements(Domain& domain, Index_t numElem)
 {
-  CalcLagrangeElements(domain) ;
-
-  CalcQForElems(domain) ;
-
-  ApplyMaterialPropertiesForElems(domain) ;
-
-  UpdateVolumesForElems(domain,
-                        domain.v_cut(), numElem) ;
+  /* Restructured: phases execute sequentially with barriers to prevent
+     nested parallelism races, while preserving parallelism of internal element loops.
+     Each phase's internal parallel loops can execute independently within the team. */
+
+#pragma omp parallel shared(domain, numElem)
+  {
+#pragma omp single
+    CalcLagrangeElements(domain);
+#pragma omp barrier
+
+#pragma omp single
+    CalcQForElems(domain);
+#pragma omp barrier
+
+#pragma omp single
+    ApplyMaterialPropertiesForElems(domain);
+#pragma omp barrier
+
+#pragma omp single
+    UpdateVolumesForElems(domain, domain.v_cut(), numElem);
+  }
 }
 
 static inline
```

## 5. Phase A · region 1:377 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1794,25 +1794,21 @@
     Real_t *vnewc = Allocate<Real_t>(numElem) ;
 
     {
+       /* Merged element loops into single parallel region to reduce thread startup overhead */
+#pragma omp parallel for shared(domain, numElem, vnewc, eosvmin, eosvmax) schedule(static)
        for(Index_t i=0 ; i<numElem ; ++i) {
           vnewc[i] = domain.vnew(i) ;
-       }
-
-       if (eosvmin != Real_t(0.)) {
-          for(Index_t i=0 ; i<numElem ; ++i) {
+
+          if (eosvmin != Real_t(0.)) {
              if (vnewc[i] < eosvmin)
                 vnewc[i] = eosvmin ;
           }
-       }
-
-       if (eosvmax != Real_t(0.)) {
-          for(Index_t i=0 ; i<numElem ; ++i) {
+
+          if (eosvmax != Real_t(0.)) {
              if (vnewc[i] > eosvmax)
                 vnewc[i] = eosvmax ;
           }
-       }
-
-       for (Index_t i=0; i<numElem; ++i) {
+
           Real_t vc = domain.v(i) ;
           if (eosvmin != Real_t(0.)) {
              if (vc < eosvmin)
@@ -1850,6 +1846,7 @@
                            Real_t v_cut, Index_t length)
 {
    if (length != 0) {
+#pragma omp parallel for shared(domain, v_cut) schedule(static)
       for(Index_t i=0 ; i<length ; ++i) {
          Real_t tmpV = domain.vnew(i) ;
 
```

## 6. Phase A-tier1 · region 1:362 — rejected at `openmp_compile`

```
OpenMP compile failed (loop not in OpenMP-canonical form):
/tmp/dp_agent_val_g29ay879/_dp_proj_tsan_binary/lulesh.cc:851:3: error: expected statement
  851 |   }
      |   ^
1 error generated.
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 10:25:32.591496606 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 10:45:35.832781883 +0000
@@ -835,6 +835,10 @@
 
   CalcForceForNodes(domain);
 
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    CalcAccelerationForNodes(domain, domain.numNode());
 
    ApplyAccelerationBoundaryConditionsForNodes(domain);
@@ -843,6 +847,8 @@
 
    CalcPositionForNodes( domain, delt, domain.numNode() );
 
+  #pragma omp task
+  }
   return;
 }
 
```

## 7. Phase A-tier1 · region 1:362 — rejected at `compile`

```
/tmp/dp_agent_val_z_ldekh5/_dp_proj_validate_binary/lulesh.cc:848:34: error: use of undeclared identifier 'delt'
  848 |    CalcVelocityForNodes( domain, delt, u_cut, domain.numNode()) ;
      |                                  ^
/tmp/dp_agent_val_z_ldekh5/_dp_proj_validate_binary/lulesh.cc:848:40: error: use of undeclared identifier 'u_cut'
  848 |    CalcVelocityForNodes( domain, delt, u_cut, domain.numNode()) ;
      |                                        ^
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 10:25:32.591496606 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 10:45:40.229808716 +0000
@@ -830,9 +830,15 @@
    Domain_member fieldData[6] ;
 #endif
 
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    const Real_t delt = domain.deltatime() ;
+   #pragma omp task
    Real_t u_cut = domain.u_cut() ;
 
+  }
   CalcForceForNodes(domain);
 
    CalcAccelerationForNodes(domain, domain.numNode());
```

## 8. Phase A · region 1:362 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -833,15 +833,23 @@
    const Real_t delt = domain.deltatime() ;
    Real_t u_cut = domain.u_cut() ;
 
-  CalcForceForNodes(domain);
-
-   CalcAccelerationForNodes(domain, domain.numNode());
-
-   ApplyAccelerationBoundaryConditionsForNodes(domain);
-
-   CalcVelocityForNodes( domain, delt, u_cut, domain.numNode()) ;
-
-   CalcPositionForNodes( domain, delt, domain.numNode() );
+#pragma omp parallel shared(domain, delt, u_cut)
+   {
+   #pragma omp single
+      CalcForceForNodes(domain);
+
+   #pragma omp single
+      CalcAccelerationForNodes(domain, domain.numNode());
+
+   #pragma omp single
+      ApplyAccelerationBoundaryConditionsForNodes(domain);
+
+   #pragma omp single
+      CalcVelocityForNodes( domain, delt, u_cut, domain.numNode()) ;
+
+   #pragma omp single
+      CalcPositionForNodes( domain, delt, domain.numNode() );
+   }
 
   return;
 }
```

## 9. Phase A · region 2:1851 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -718,10 +718,16 @@
                                sigxx, sigyy, sigzz, determ, numElem,
                                domain.numNode()) ;
 
+      bool error_found = false;
+      #pragma omp parallel for reduction(||:error_found)
       for ( Index_t k=0 ; k<numElem ; ++k ) {
          if (determ[k] <= Real_t(0.0)) {
-            exit(VolumeError);
+            error_found = true;
          }
+      }
+
+      if (error_found) {
+         exit(VolumeError);
       }
 
       CalcHourglassControlForElems(domain, determ, hgcoef) ;
```

## 10. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
/tmp/dp_agent_val_wgwmqog0/_dp_proj_validate_binary/lulesh.cc:679:10: error: use of undeclared identifier 'dvdx'
  679 |          dvdx[jj] = pfx[ii];
      |          ^
/tmp/dp_agent_val_wgwmqog0/_dp_proj_validate_binary/lulesh.cc:696:60: error: use of undeclared identifier 'dvdx'
  696 |                                     determ, x8n, y8n, z8n, dvdx, dvdy, dvdz,
      |                                                            ^
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:12.863092895 +0000
@@ -651,7 +651,13 @@
 {
    Index_t numElem = domain.numElem() ;
    Index_t numElem8 = numElem * 8 ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
+   #pragma omp task
    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
+   }
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
```

## 11. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
al_t>(numElem8) ;
      |            ^
/tmp/dp_agent_val_76lto5s6/_dp_proj_validate_binary/lulesh.cc:683:10: error: use of undeclared identifier 'y8n'
  683 |          y8n[jj]  = y1[ii];
      |          ^
/tmp/dp_agent_val_76lto5s6/_dp_proj_validate_binary/lulesh.cc:696:45: error: use of undeclared identifier 'x8n'; did you mean 'z8n'?
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:12.985093648 +0000
@@ -654,8 +654,14 @@
    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
+   #pragma omp task
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
+   }
    Real_t *z8n  = Allocate<Real_t>(numElem8) ;
 
    for (Index_t i=0 ; i<numElem ; ++i){
```

## 12. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
'dvdx' declared here
  654 |    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
      |            ^
/tmp/dp_agent_val_nk3dqf2s/_dp_proj_validate_binary/lulesh.cc:696:66: error: use of undeclared identifier 'dvdy'; did you mean 'dvdx'?
  696 |                                     determ, x8n, y8n, z8n, dvdx, dvdy, dvdz,
      |                                                                  ^~~~
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:13.075094204 +0000
@@ -652,8 +652,14 @@
    Index_t numElem = domain.numElem() ;
    Index_t numElem8 = numElem * 8 ;
    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
+   #pragma omp task
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
+   }
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
    Real_t *z8n  = Allocate<Real_t>(numElem8) ;
```

## 13. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
/lulesh.cc:662:12: note: 'dvdz' declared here
  662 |    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
      |            ^
/tmp/dp_agent_val_quuqn9qn/_dp_proj_validate_binary/lulesh.cc:696:60: error: use of undeclared identifier 'dvdx'; did you mean 'dvdz'?
  696 |                                     determ, x8n, y8n, z8n, dvdx, dvdy, dvdz,
      |                                                            ^~~~
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:16.368114547 +0000
@@ -651,8 +651,14 @@
 {
    Index_t numElem = domain.numElem() ;
    Index_t numElem8 = numElem * 8 ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
+   #pragma omp task
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
+   }
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
```

## 14. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
x8n
/tmp/dp_agent_val_d2olpdol/_dp_proj_validate_binary/lulesh.cc:657:12: note: 'x8n' declared here
  657 |    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
      |            ^
/tmp/dp_agent_val_d2olpdol/_dp_proj_validate_binary/lulesh.cc:696:50: error: use of undeclared identifier 'y8n'; did you mean 'x8n'?
  696 |                                     determ, x8n, y8n, z8n, dvdx, dvdy, dvdz,
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:22.161150333 +0000
@@ -655,9 +655,15 @@
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
+   #pragma omp task
    Real_t *z8n  = Allocate<Real_t>(numElem8) ;
 
+   }
    for (Index_t i=0 ; i<numElem ; ++i){
       Real_t  x1[8],  y1[8],  z1[8] ;
       Real_t pfx[8], pfy[8], pfz[8] ;
```

## 15. Phase A-tier1 · region 1:1939 — rejected at `compile`

```
/tmp/dp_agent_val_pq071ebt/_dp_proj_validate_binary/lulesh.cc:681:10: error: use of undeclared identifier 'dvdz'
  681 |          dvdz[jj] = pfz[ii];
      |          ^
/tmp/dp_agent_val_pq071ebt/_dp_proj_validate_binary/lulesh.cc:682:10: error: use of undeclared identifier 'x8n'
  682 |          x8n[jj]  = x1[ii];
      |          ^
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc	2026-11-03 11:11:15.941258216 +0000
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc.discopop_patch_generator.temp	2026-11-03 11:16:23.282157258 +0000
@@ -653,8 +653,14 @@
    Index_t numElem8 = numElem * 8 ;
    Real_t *dvdx = Allocate<Real_t>(numElem8) ;
    Real_t *dvdy = Allocate<Real_t>(numElem8) ;
+   #pragma omp parallel
+   #pragma omp single
+   {
+   #pragma omp task
    Real_t *dvdz = Allocate<Real_t>(numElem8) ;
+   #pragma omp task
    Real_t *x8n  = Allocate<Real_t>(numElem8) ;
+   }
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
    Real_t *z8n  = Allocate<Real_t>(numElem8) ;
 
```

## 16. Phase A · region 1:1939 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -658,6 +658,7 @@
    Real_t *y8n  = Allocate<Real_t>(numElem8) ;
    Real_t *z8n  = Allocate<Real_t>(numElem8) ;
 
+   #pragma omp parallel for shared(domain, dvdx, dvdy, dvdz, x8n, y8n, z8n, determ) schedule(static)
    for (Index_t i=0 ; i<numElem ; ++i){
       Real_t  x1[8],  y1[8],  z1[8] ;
       Real_t pfx[8], pfy[8], pfz[8] ;
```

## 17. Phase A · region 1:2347 — rejected at `openmp_compile`

```
OpenMP compile failed (loop not in OpenMP-canonical form):
/tmp/dp_agent_val_6weak9x1/_dp_proj_tsan_binary/lulesh.cc:1512:40: error: use of undeclared identifier 'i'
 1512 |       #pragma omp parallel for private(i) shared(domain, violations, numElem)
      |                                        ^
1 error generated.
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1500,12 +1500,30 @@
       domain.DeallocateGradients();
 
       Index_t idx = -1;
+
+      // Allocate array to track violations (one per element)
+      bool* violations = (bool*)malloc(numElem * sizeof(bool));
+
+      // Parallel loop: check which elements violate the condition
+      // idx: loop counter (private, implicit from loop)
+      // numElem: loop bound (shared, read-only)
+      // domain: shared, accessed read-only via q() and qstop()
+      // violations: shared, written once per iteration to violations[i]
+      #pragma omp parallel for private(i) shared(domain, violations, numElem)
       for (Index_t i=0; i<numElem; ++i) {
-         if ( domain.q(i) > domain.qstop() ) {
+         violations[i] = (domain.q(i) > domain.qstop());
+      }
+
+      // Sequential scan: find first violation and set idx
+      for (Index_t i=0; i<numElem; ++i) {
+         if (violations[i]) {
             idx = i ;
             break ;
          }
       }
+
+      // Clean up
+      free(violations);
 
       if(idx >= 0) {
          exit(QStopError);
```

## 18. Phase A · region 1:2347 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1500,12 +1500,30 @@
       domain.DeallocateGradients();
 
       Index_t idx = -1;
+
+      // Allocate array to track violations (one per element)
+      bool* violations = (bool*)malloc(numElem * sizeof(bool));
+
+      // Parallel loop: check which elements violate the condition
+      // i: loop counter (private, implicit from loop)
+      // numElem: loop bound (shared, read-only)
+      // domain: shared, accessed read-only via q() and qstop()
+      // violations: shared, written once per iteration to violations[i]
+      #pragma omp parallel for shared(domain, violations, numElem)
       for (Index_t i=0; i<numElem; ++i) {
-         if ( domain.q(i) > domain.qstop() ) {
+         violations[i] = (domain.q(i) > domain.qstop());
+      }
+
+      // Sequential scan: find first violation and set idx
+      for (Index_t i=0; i<numElem; ++i) {
+         if (violations[i]) {
             idx = i ;
             break ;
          }
       }
+
+      // Clean up
+      free(violations);
 
       if(idx >= 0) {
          exit(QStopError);
```

## 19. Phase A · region 2:178 — rejected at `performance`

```
Net regression: the program with this rewrite runs at 0.33x the speed of the program before it (the two timed in turn, paired; kept at or above 0.99x). The 1.35
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -67,41 +67,13 @@
                                    Real_t elemY[8],
                                    Real_t elemZ[8])
 {
-   Index_t nd0i = elemToNode[0] ;
-   Index_t nd1i = elemToNode[1] ;
-   Index_t nd2i = elemToNode[2] ;
-   Index_t nd3i = elemToNode[3] ;
-   Index_t nd4i = elemToNode[4] ;
-   Index_t nd5i = elemToNode[5] ;
-   Index_t nd6i = elemToNode[6] ;
-   Index_t nd7i = elemToNode[7] ;
-
-   elemX[0] = domain.x(nd0i);
-   elemX[1] = domain.x(nd1i);
-   elemX[2] = domain.x(nd2i);
-   elemX[3] = domain.x(nd3i);
-   elemX[4] = domain.x(nd4i);
-   elemX[5] = domain.x(nd5i);
-   elemX[6] = domain.x(nd6i);
-   elemX[7] = domain.x(nd7i);
-
-   elemY[0] = domain.y(nd0i);
-   elemY[1] = domain.y(nd1i);
-   elemY[2] = domain.y(nd2i);
-   elemY[3] = domain.y(nd3i);
-   elemY[4] = domain.y(nd4i);
-   elemY[5] = domain.y(nd5i);
-   elemY[6] = domain.y(nd6i);
-   elemY[7] = domain.y(nd7i);
-
-   elemZ[0] = domain.z(nd0i);
-   elemZ[1] = domain.z(nd1i);
-   elemZ[2] = domain.z(nd2i);
-   elemZ[3] = domain.z(nd3i);
-   elemZ[4] = domain.z(nd4i);
-   elemZ[5] = domain.z(nd5i);
-   elemZ[6] = domain.z(nd6i);
-   elemZ[7] = domain.z(nd7i);
+   #pragma omp parallel for default(none) shared(domain, elemToNode, elemX, elemY, elemZ)
+   for (int i = 0; i < 8; ++i) {
+      Index_t ndi = elemToNode[i];
+      elemX[i] = domain.x(ndi);
+      elemY[i] = domain.y(ndi);
+      elemZ[i] = domain.z(ndi);
+   }
 
 }
 
```

## 20. Phase A · region 2:178 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -67,41 +67,12 @@
                                    Real_t elemY[8],
                                    Real_t elemZ[8])
 {
-   Index_t nd0i = elemToNode[0] ;
-   Index_t nd1i = elemToNode[1] ;
-   Index_t nd2i = elemToNode[2] ;
-   Index_t nd3i = elemToNode[3] ;
-   Index_t nd4i = elemToNode[4] ;
-   Index_t nd5i = elemToNode[5] ;
-   Index_t nd6i = elemToNode[6] ;
-   Index_t nd7i = elemToNode[7] ;
-
-   elemX[0] = domain.x(nd0i);
-   elemX[1] = domain.x(nd1i);
-   elemX[2] = domain.x(nd2i);
-   elemX[3] = domain.x(nd3i);
-   elemX[4] = domain.x(nd4i);
-   elemX[5] = domain.x(nd5i);
-   elemX[6] = domain.x(nd6i);
-   elemX[7] = domain.x(nd7i);
-
-   elemY[0] = domain.y(nd0i);
-   elemY[1] = domain.y(nd1i);
-   elemY[2] = domain.y(nd2i);
-   elemY[3] = domain.y(nd3i);
-   elemY[4] = domain.y(nd4i);
-   elemY[5] = domain.y(nd5i);
-   elemY[6] = domain.y(nd6i);
-   elemY[7] = domain.y(nd7i);
-
-   elemZ[0] = domain.z(nd0i);
-   elemZ[1] = domain.z(nd1i);
-   elemZ[2] = domain.z(nd2i);
-   elemZ[3] = domain.z(nd3i);
-   elemZ[4] = domain.z(nd4i);
-   elemZ[5] = domain.z(nd5i);
-   elemZ[6] = domain.z(nd6i);
-   elemZ[7] = domain.z(nd7i);
+   for (int i = 0; i < 8; ++i) {
+      Index_t ndi = elemToNode[i];
+      elemX[i] = domain.x(ndi);
+      elemY[i] = domain.y(ndi);
+      elemZ[i] = domain.z(ndi);
+   }
 
 }
 
```

## 21. Phase A-D40 · region 2:178 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -67,6 +67,7 @@
                                    Real_t elemY[8],
                                    Real_t elemZ[8])
 {
+   #pragma omp parallel for shared(elemX,elemZ,elemToNode,domain,elemY) 
    for (int i = 0; i < 8; ++i) {
       Index_t ndi = elemToNode[i];
       elemX[i] = domain.x(ndi);
```

## 22. Phase A · region 2:178 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -67,41 +67,32 @@
                                    Real_t elemY[8],
                                    Real_t elemZ[8])
 {
-   Index_t nd0i = elemToNode[0] ;
-   Index_t nd1i = elemToNode[1] ;
-   Index_t nd2i = elemToNode[2] ;
-   Index_t nd3i = elemToNode[3] ;
-   Index_t nd4i = elemToNode[4] ;
-   Index_t nd5i = elemToNode[5] ;
-   Index_t nd6i = elemToNode[6] ;
-   Index_t nd7i = elemToNode[7] ;
-
-   elemX[0] = domain.x(nd0i);
-   elemX[1] = domain.x(nd1i);
-   elemX[2] = domain.x(nd2i);
-   elemX[3] = domain.x(nd3i);
-   elemX[4] = domain.x(nd4i);
-   elemX[5] = domain.x(nd5i);
-   elemX[6] = domain.x(nd6i);
-   elemX[7] = domain.x(nd7i);
-
-   elemY[0] = domain.y(nd0i);
-   elemY[1] = domain.y(nd1i);
-   elemY[2] = domain.y(nd2i);
-   elemY[3] = domain.y(nd3i);
-   elemY[4] = domain.y(nd4i);
-   elemY[5] = domain.y(nd5i);
-   elemY[6] = domain.y(nd6i);
-   elemY[7] = domain.y(nd7i);
-
-   elemZ[0] = domain.z(nd0i);
-   elemZ[1] = domain.z(nd1i);
-   elemZ[2] = domain.z(nd2i);
-   elemZ[3] = domain.z(nd3i);
-   elemZ[4] = domain.z(nd4i);
-   elemZ[5] = domain.z(nd5i);
-   elemZ[6] = domain.z(nd6i);
-   elemZ[7] = domain.z(nd7i);
+   elemX[0] = domain.x(elemToNode[0]);
+   elemX[1] = domain.x(elemToNode[1]);
+   elemX[2] = domain.x(elemToNode[2]);
+   elemX[3] = domain.x(elemToNode[3]);
+   elemX[4] = domain.x(elemToNode[4]);
+   elemX[5] = domain.x(elemToNode[5]);
+   elemX[6] = domain.x(elemToNode[6]);
+   elemX[7] = domain.x(elemToNode[7]);
+
+   elemY[0] = domain.y(elemToNode[0]);
+   elemY[1] = domain.y(elemToNode[1]);
+   elemY[2] = domain.y(elemToNode[2]);
+   elemY[3] = domain.y(elemToNode[3]);
+   elemY[4] = domain.y(elemToNode[4]);
+   elemY[5] = domain.y(elemToNode[5]);
+   elemY[6] = domain.y(elemToNode[6]);
+   elemY[7] = domain.y(elemToNode[7]);
+
+   elemZ[0] = domain.z(elemToNode[0]);
+   elemZ[1] = domain.z(elemToNode[1]);
+   elemZ[2] = domain.z(elemToNode[2]);
+   elemZ[3] = domain.z(elemToNode[3]);
+   elemZ[4] = domain.z(elemToNode[4]);
+   elemZ[5] = domain.z(elemToNode[5]);
+   elemZ[6] = domain.z(elemToNode[6]);
+   elemZ[7] = domain.z(elemToNode[7]);
 
 }
 
```

## 23. Phase A · region 1:2440 — rejected at `performance`

```
Net regression: the program with this rewrite runs at 0.95x the speed of the program before it (the two timed in turn, paired; kept at or above 0.99x). The 1.51
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1857,13 +1857,15 @@
        }
     }
 
-    for (Int_t r=0 ; r<domain.numReg() ; r++) {
+    Int_t numReg = domain.numReg();
+#pragma omp parallel for shared(domain, vnewc, numReg) schedule(static)
+    for (Int_t r=0 ; r<numReg ; r++) {
        Index_t numElemReg = domain.regElemSize(r);
        Index_t *regElemList = domain.regElemlist(r);
        Int_t rep;
-       if(r < domain.numReg()/2)
+       if(r < numReg/2)
 	 rep = 1;
-       else if(r < (domain.numReg() - (domain.numReg()+15)/20))
+       else if(r < (numReg - (numReg+15)/20))
          rep = 1 + domain.cost();
        else
 	 rep = 10 * (1+ domain.cost());
```

## 24. Phase A · region 1:2440 — rejected at `performance`

```
Net regression: the program with this rewrite runs at 0.94x the speed of the program before it (the two timed in turn, paired; kept at or above 0.99x). The 1.40
```

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1857,17 +1857,23 @@
        }
     }
 
-    for (Int_t r=0 ; r<domain.numReg() ; r++) {
-       Index_t numElemReg = domain.regElemSize(r);
-       Index_t *regElemList = domain.regElemlist(r);
-       Int_t rep;
-       if(r < domain.numReg()/2)
-	 rep = 1;
-       else if(r < (domain.numReg() - (domain.numReg()+15)/20))
-         rep = 1 + domain.cost();
-       else
-	 rep = 10 * (1+ domain.cost());
-       EvalEOSForElems(domain, vnewc, numElemReg, regElemList, rep);
+    Int_t numReg = domain.numReg();
+    /* Batch regions to reduce parallel task overhead and increase work per region */
+#pragma omp parallel for shared(domain, vnewc, numReg) schedule(static)
+    for (Int_t rb=0 ; rb<((numReg + 2) / 3) ; rb++) {
+       Int_t r_end = ((rb + 1) * 3 <= numReg) ? (rb + 1) * 3 : numReg;
+       for (Int_t r=rb*3 ; r<r_end ; r++) {
+          Index_t numElemReg = domain.regElemSize(r);
+          Index_t *regElemList = domain.regElemlist(r);
+          Int_t rep;
+          if(r < numReg/2)
+	    rep = 1;
+          else if(r < (numReg - (numReg+15)/20))
+            rep = 1 + domain.cost();
+          else
+	    rep = 10 * (1+ domain.cost());
+          EvalEOSForElems(domain, vnewc, numElemReg, regElemList, rep);
+       }
     }
 
     Release(&vnewc) ;
```

## 25. Phase A · region 1:2440 — passed the gate

```diff
--- /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
+++ /home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e6c_r3b/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/work/lulesh.cc
@@ -1825,10 +1825,13 @@
     Real_t eosvmin = domain.eosvmin() ;
     Real_t eosvmax = domain.eosvmax() ;
     Real_t *vnewc = Allocate<Real_t>(numElem) ;
-
+    Int_t numReg = domain.numReg();
+
+    /* Merged element and region loops into single parallel region to reduce thread startup overhead */
+#pragma omp parallel shared(domain, numElem, vnewc, eosvmin, eosvmax, numReg)
     {
-       /* Merged element loops into single parallel region to reduce thread startup overhead */
-#pragma omp parallel for shared(domain, numElem, vnewc, eosvmin, eosvmax) schedule(static)
+       /* Element processing loop */
+#pragma omp for schedule(static)
        for(Index_t i=0 ; i<numElem ; ++i) {
           vnewc[i] = domain.vnew(i) ;
 
@@ -1855,19 +1858,26 @@
              exit(VolumeError);
           }
        }
-    }
-
-    for (Int_t r=0 ; r<domain.numReg() ; r++) {
-       Index_t numElemReg = domain.regElemSize(r);
-       Index_t *regElemList = domain.regElemlist(r);
-       Int_t rep;
-       if(r < domain.numReg()/2)
-	 rep = 1;
-       else if(r < (domain.numReg() - (domain.numReg()+15)/20))
-         rep = 1 + domain.cost();
-       else
-	 rep = 10 * (1+ domain.cost());
-       EvalEOSForElems(domain, vnewc, numElemReg, regElemList, rep);
+
+       /* Implicit barrier between worksharing constructs */
+
+       /* Region processing loop with batching to increase work per task */
+#pragma omp for schedule(static)
+       for (Int_t rb=0 ; rb<((numReg + 2) / 3) ; rb++) {
+          Int_t r_end = ((rb + 1) * 3 <= numReg) ? (rb + 1) * 3 : numReg;
+          for (Int_t r=rb*3 ; r<r_end ; r++) {
+             Index_t numElemReg = domain.regElemSize(r);
+             Index_t *regElemList = domain.regElemlist(r);
+             Int_t rep;
+             if(r < numReg/2)
+	       rep = 1;
+             else if(r < (numReg - (numReg+15)/20))
+               rep = 1 + domain.cost();
+             else
+	       rep = 10 * (1+ domain.cost());
+             EvalEOSForElems(domain, vnewc, numElemReg, regElemList, rep);
+          }
+       }
     }
 
     Release(&vnewc) ;
```

