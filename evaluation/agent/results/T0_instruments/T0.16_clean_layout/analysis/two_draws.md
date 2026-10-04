| loop | output | time new/old (LARGE) | candidates | Do-All set | blocker of the loop under study | repetition loop | order statement (version 4) |
|---|---|---|---|---|---|---|---|
| k17 | same | 0.999 | same | same | same | same | same |
| k19 | same | 0.998 | same | same | same | same | same |
| k23 | same | 0.998 | same | same | same | same | same |
| k31 | same | 1.017 | same | same | same | same | same |
| k42 | same | 0.996 | same | same | same | same | same |
| k48 | same | 1.002 | same | same | same | same | same |
| s000 | same | 0.989 | same | same | same | same | same |
| s112 | same | 1.001 | same | same | same | same | same |
| s121 | same | 1.038 | same | same | same | same | same |
| s1213 | same | 1.0 | same | same | one draw only | same | same |
| s127 | same | 0.993 | same | same | same | same | same |
| s131 | same | 0.985 | same | same | same | same | same |
| s151 | same | 1.038 | DIFF in both | same | same | same | same |
| s152 | same | 1.002 | same | same | same | same | same |
| s161 | same | 1.0 | same | same | same | same | same |
| s171 | same | 0.963 | same | same | same | same | same |
| s211 | same | 1.001 | same | same | same | same | same |
| s212 | same | 1.041 | same | same | same | same | same |
| s241 | same | 0.991 | same | same | same | same | same |
| s243 | same | 1.195 | same | same | same | same | same |
| s244 | same | 1.259 | same | same | DIFF in both | same | same |
| s252 | same | 1.008 | same | same | same | same | same |
| s254 | same | 1.0 | same | same | same | same | same |
| s255 | same | 0.97 | same | same | same | same | same |
| s258 | same | 1.0 | same | same | same | same | same |
| s277 | same | 0.999 | same | same | same | same | same |
| s281 | same | 1.001 | same | same | same | same | same |
| s291 | same | 0.981 | same | same | same | same | same |
| s292 | same | 0.815 | same | same | same | same | same |
| s293 | same | 0.999 | same | same | same | same | same |
| s3112 | same | 0.998 | same | same | same | same | same |
| s313 | same | 0.998 | same | same | same | same | same |
| s321 | same | 1.001 | same | same | same | same | same |
| s322 | same | 1.0 | same | same | same | same | same |
| s323 | same | 1.0 | same | same | same | same | same |
| s331 | same | 0.999 | same | same | same | same | same |
| s341 | same | 1.034 | same | same | same | same | same |
| s424 | same | 1.016 | same | same | same | same | same |
| s481 | same | 0.993 | same | same | same | DIFF in both | same |
| s482 | same | 1.22 | DIFF in both | DIFF in both | DIFF in both | same | same |
| vas | same | 0.998 | same | same | same | same | same |
| vpvtv | same | 1.004 | same | same | same | same | same |

42 loops, two draws on the server. Output identical in both draws: 42.
The same on every criterion in both draws: 37;
a difference in BOTH draws (kept): 4 — s151: candidates; s244: blocker; s481: repetition; s482: candidates, do_all, blocker;
a difference in one draw only (not kept): s1213: blocker.
Sequential time new/old at LARGE (draw a): within 0.96-1.04 for 37 of 42;
outside: s292 0.815, s212 1.041, s243 1.195, s482 1.22, s244 1.259.

WAR/WAW between two draws of ONE layout (84 loop-layout pairs): the reading of versions 1-3 differs on
23; read by each dependence's own type (D12) it differs on 0; RAW differs on 0.
