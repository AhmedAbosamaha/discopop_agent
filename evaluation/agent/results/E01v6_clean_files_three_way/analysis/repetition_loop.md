```
agent (Haiku)    class A:   3 programs, repetition loop and `dummy` kept as they are in 2
      dummy=2 -> FASTER: 1
      temporary memory: {'none': 3}
agent (Haiku)    class D:  12 programs, repetition loop and `dummy` kept as they are in 12
      temporary memory: {'none': 12}
agent (Haiku)    class R:  90 programs, repetition loop and `dummy` kept as they are in 89
      loops=2, loop parallel -> FASTER: 1
      temporary memory: {'before the repetition loop': 32, 'none': 58}
fable-5-1 alone  class A:   3 programs, repetition loop and `dummy` kept as they are in 3
      temporary memory: {'none': 3}
fable-5-1 alone  class D:  12 programs, repetition loop and `dummy` kept as they are in 11
      loops=2, dummy=2 -> FASTER: 1
      temporary memory: {'none': 9, 'before the repetition loop': 3}
fable-5-1 alone  class R:  90 programs, repetition loop and `dummy` kept as they are in 89
      loops=2, dummy=2 -> FASTER: 1
      temporary memory: {'before the repetition loop': 28, 'none': 62}
haiku-4-5 alone  class A:   3 programs, repetition loop and `dummy` kept as they are in 3
      temporary memory: {'none': 3}
haiku-4-5 alone  class D:  12 programs, repetition loop and `dummy` kept as they are in 10
      loop parallel -> BROKEN: 2
      temporary memory: {'none': 6, 'before the repetition loop': 5, 'inside or after it': 1}
haiku-4-5 alone  class R:  90 programs, repetition loop and `dummy` kept as they are in 89
      region around -> FASTER: 1
      temporary memory: {'before the repetition loop': 23, 'inside or after it': 7, 'none': 60}
opus-5-5 alone   class A:   3 programs, repetition loop and `dummy` kept as they are in 3
      temporary memory: {'none': 2, 'before the repetition loop': 1}
opus-5-5 alone   class D:  12 programs, repetition loop and `dummy` kept as they are in 5
      loops=0, dummy=0 -> FASTER: 2
      loops=0, dummy=2 -> FASTER: 1
      loops=2, dummy=0, loop parallel -> FASTER: 1
      loops=2, dummy=2, loop parallel -> FASTER: 2
      loops=2, loop parallel -> FASTER: 1
      temporary memory: {'before the repetition loop': 4, 'inside or after it': 1, 'none': 7}
opus-5-5 alone   class R:  90 programs, repetition loop and `dummy` kept as they are in 90
      temporary memory: {'before the repetition loop': 24, 'none': 66}
sonnet-5 alone   class A:   3 programs, repetition loop and `dummy` kept as they are in 3
      temporary memory: {'none': 3}
sonnet-5 alone   class D:  12 programs, repetition loop and `dummy` kept as they are in 12
      temporary memory: {'inside or after it': 1, 'none': 6, 'before the repetition loop': 5}
sonnet-5 alone   class R:  90 programs, repetition loop and `dummy` kept as they are in 90
      temporary memory: {'before the repetition loop': 38, 'none': 52}

every program that changed them:
  agent (Haiku) | A | s313 | rep1 | dummy=2 | FASTER
  fable-5-1 alone | R | s112 | rep5 | loops=2, dummy=2 | FASTER
  fable-5-1 alone | D | s321 | rep2 | loops=2, dummy=2 | FASTER
  haiku-4-5 alone | D | s3112 | rep1 | loop parallel | BROKEN
  haiku-4-5 alone | D | s321 | rep3 | loop parallel | BROKEN
  haiku-4-5 alone | R | s341 | rep4 | region around | FASTER
  opus-5-5 alone | D | s3112 | rep2 | loops=2, dummy=2, loop parallel | FASTER
  opus-5-5 alone | D | s3112 | rep3 | loops=2, dummy=2, loop parallel | FASTER
  opus-5-5 alone | D | s321 | rep1 | loops=0, dummy=2 | FASTER
  opus-5-5 alone | D | s321 | rep2 | loops=2, loop parallel | FASTER
  opus-5-5 alone | D | s321 | rep3 | loops=0, dummy=0 | FASTER
  opus-5-5 alone | D | s322 | rep1 | loops=0, dummy=0 | FASTER
  opus-5-5 alone | D | s322 | rep2 | loops=2, dummy=0, loop parallel | FASTER
  agent (Haiku) | R | s331 | rep1 | loops=2, loop parallel | FASTER
```
