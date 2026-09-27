# T0.15 read-out over 2 runs: t0_15_fixed_a, t0_15_fixed_b

| package | candidates | dependences |
|---|---|---|
| `s000` | same | noise |
| `s112` | same | noise |
| `s121` | same | LAYOUT |
| `s1213` | same | noise |
| `s127` | same | same |
| `s211` | same | noise |
| `s212` | same | same |
| `s241` | same | noise |
| `s243` | same | same |
| `s244` | same | noise |
| `s252` | same | noise |
| `s254` | same | undecided |
| `s255` | same | undecided |
| `s281` | same | noise |
| `s291` | same | LAYOUT |
| `s292` | same | noise |
| `s293` | same | same |
| `s3112` | same | LAYOUT |
| `s313` | same | same |
| `s321` | same | same |
| `s322` | same | noise |
| `s323` | same | noise |
| `s331` | same | same |
| `s341` | same | noise |
| `s353` | same | same |
| `s4112` | same | noise |
| `s4113` | same | undecided |
| `s4114` | same | noise |
| `s4115` | same | same |
| `s4117` | same | noise |
| `s4121` | same | noise |
| `s491` | same | noise |
| `vpvtv` | same | LAYOUT |

| dimension | same | noise | LAYOUT | undecided |
|---|---:|---:|---:|---:|
| candidates | 33 | 0 | 0 | 0 |
| dependences | 9 | 17 | 4 | 3 |

## Stable or undecided differences, per package

- `s121` dependences (LAYOUT): v3 only ["('WAR', ('kernel', 6), ('pb_mix', 5), 'a')"]; v4 only —
- `s254` dependences (undecided): v3 only ["('WAW', ('kernel', 6), ('kernel', 6), 'a')", "('WAW', ('kernel', 6), ('pb_mix', 3), 'a')"]; v4 only —
- `s255` dependences (undecided): v3 only —; v4 only —
- `s291` dependences (LAYOUT): v3 only ["('WAW', ('kernel', 6), ('kernel', 6), 'a')", "('WAW', ('kernel', 6), ('pb_mix', 3), 'a')"]; v4 only —
- `s3112` dependences (LAYOUT): v3 only —; v4 only ["('WAW', ('kernel', 7), ('kernel', 7), 'b')", "('WAW', ('kernel', 7), ('pb_mix', 3), 'b')", "('WAW', ('kernel', 7), ('pb_mix', 5), 'b')"]
- `s4113` dependences (undecided): v3 only —; v4 only ["('WAW', ('kernel', 5), ('kernel', 5), 'a')", "('WAW', ('kernel', 5), ('pb_mix', 3), 'a')"]
- `vpvtv` dependences (LAYOUT): v3 only —; v4 only ["('WAR', ('kernel', 4), ('kernel', 4), 'a')"]
