```
E3, DiscoPoP writes the pragma   class A:   5 programs, repetition loop and `dummy` kept as they are in 5
      temporary memory: {'none': 5}
      a loop of the kernel outside the repetition loop: 1 {'FASTER': 1}
E3, DiscoPoP writes the pragma   class R:  30 programs, repetition loop and `dummy` kept as they are in 30
      temporary memory: {'none': 18, 'before the repetition loop': 5, 'inside or after it': 7}
      a loop of the kernel outside the repetition loop: 0
E3, the model writes the pragma  class A:   5 programs, repetition loop and `dummy` kept as they are in 5
      temporary memory: {'none': 5}
      a loop of the kernel outside the repetition loop: 0
E3, the model writes the pragma  class R:  30 programs, repetition loop and `dummy` kept as they are in 30
      temporary memory: {'none': 28, 'inside or after it': 2}
      a loop of the kernel outside the repetition loop: 0

every program that changed the repetition loop or the `dummy` call:
  none

every program with a loop of the kernel outside the repetition loop:
  E3, DiscoPoP writes the pragma | A | s311 | e3b_3 | rep5 | 1 loop(s) outside the repetition loop | FASTER
```
