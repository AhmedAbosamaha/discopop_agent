```
E1-v6, the agent                 class A:   4 programs, repetition loop and `dummy` kept as they are in 3
      dummy=2 -> FASTER: 1
      temporary memory: {'none': 4}
      a loop of the kernel outside the repetition loop: 1 {'FASTER': 1}
E1-v6, the agent                 class D:  12 programs, repetition loop and `dummy` kept as they are in 12
      temporary memory: {'none': 12}
      a loop of the kernel outside the repetition loop: 0
E1-v6, the agent                 class R: 105 programs, repetition loop and `dummy` kept as they are in 104
      loops=2, loop parallel -> FASTER: 1
      temporary memory: {'before the repetition loop': 38, 'none': 67}
      a loop of the kernel outside the repetition loop: 6 {'FASTER': 6}
E3, DiscoPoP writes the pragma   class A:   3 programs, repetition loop and `dummy` kept as they are in 2
      dummy=2 -> FASTER: 1
      temporary memory: {'none': 3}
      a loop of the kernel outside the repetition loop: 1 {'FASTER': 1}
E3, DiscoPoP writes the pragma   class D:  12 programs, repetition loop and `dummy` kept as they are in 12
      temporary memory: {'none': 12}
      a loop of the kernel outside the repetition loop: 0
E3, DiscoPoP writes the pragma   class R:  90 programs, repetition loop and `dummy` kept as they are in 90
      temporary memory: {'before the repetition loop': 32, 'none': 57, 'inside or after it': 1}
      a loop of the kernel outside the repetition loop: 1 {'FASTER': 1}
E3, the model writes the pragma  class A:   3 programs, repetition loop and `dummy` kept as they are in 3
      temporary memory: {'none': 3}
      a loop of the kernel outside the repetition loop: 0
E3, the model writes the pragma  class D:  12 programs, repetition loop and `dummy` kept as they are in 12
      temporary memory: {'none': 12}
      a loop of the kernel outside the repetition loop: 0
E3, the model writes the pragma  class R:  90 programs, repetition loop and `dummy` kept as they are in 83
      region around -> FASTER: 7
      temporary memory: {'before the repetition loop': 30, 'none': 59, 'inside or after it': 1}
      a loop of the kernel outside the repetition loop: 1 {'FASTER': 1}

every program that changed the repetition loop or the `dummy` call:
  E3, DiscoPoP writes the pragma | A | s000 | e3_a | rep1 | dummy=2 | FASTER
  E3, the model writes the pragma | R | s112 | e3_r_1 | rep1 | region around | FASTER
  E3, the model writes the pragma | R | s112 | e3_r_1 | rep2 | region around | FASTER
  E3, the model writes the pragma | R | s112 | e3_r_1 | rep4 | region around | FASTER
  E3, the model writes the pragma | R | s121 | e3_r_1 | rep3 | region around | FASTER
  E3, the model writes the pragma | R | s121 | e3_r_1 | rep4 | region around | FASTER
  E3, the model writes the pragma | R | s121 | e3_r_1 | rep5 | region around | FASTER
  E3, the model writes the pragma | R | s212 | e3_r_2 | rep5 | region around | FASTER
  E1-v6, the agent | A | s313 | e1v6_a | rep1 | dummy=2 | FASTER
  E1-v6, the agent | R | s331 | e1v6_r_4 | rep1 | loops=2, loop parallel | FASTER

every program with a loop of the kernel outside the repetition loop:
  E3, DiscoPoP writes the pragma | A | s000 | e3_a | rep1 | 1 loop(s) outside the repetition loop | FASTER
  E3, DiscoPoP writes the pragma | R | s341 | e3_r_4 | rep5 | 1 loop(s) outside the repetition loop | FASTER
  E3, the model writes the pragma | R | s341 | e3_r_4 | rep5 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | A | s313 | e1v6_a | rep1 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s243 | e1v6_r_2 | rep1 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s331 | e1v6_r_4 | rep1 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s341 | e1v6_r_4 | rep1 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s341 | e1v6_r_4 | rep3 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s341 | e1v6_r_4 | rep4 | 1 loop(s) outside the repetition loop | FASTER
  E1-v6, the agent | R | s341 | e1v6_r_4 | rep5 | 1 loop(s) outside the repetition loop | FASTER
```
