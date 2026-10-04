| loop | layout | true | version 3 | version 4 |
|---|---|---|---|---|
| k17 | tsvc_c2proto | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | tsvc_c2proto | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k23 | tsvc_c2proto | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k31 | tsvc_c2proto | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k42 | tsvc_c2proto | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k48 | tsvc_c2proto | order: u[ju[i]] += / v[jv[i]] = | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| s000 | tsvc_c2proto | none | right — — | right — — |
| s112 | tsvc_c2proto | none | right — — | right — — |
| s1213 | tsvc_c2proto | order: b[i] = a[i+1] / a[i] = b[i-1] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s121 | tsvc_c2proto | none | right — — | right — — |
| s127 | tsvc_c2proto | none | right — — | right — — |
| s131 | tsvc_c2proto | none | right — — | right — — |
| s151 | tsvc_c2proto | none | right — — | right — — |
| s152 | tsvc_c2proto | none | right — — | right — — |
| s161 | tsvc_c2proto | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s171 | tsvc_c2proto | none | right — — | right — — |
| s211 | tsvc_c2proto | order: b[i] = b[i + 1] / a[i] = b[i - 1] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s212 | tsvc_c2proto | none | WRONG — a[i] *= c[i]; ⟶ b[i] += a[i + 1] * d[i]; [a] | right — — |
| s241 | tsvc_c2proto | none | WRONG — a[i] = b[i] * c[i  ] * d[i]; ⟷ b[i] = a[i] * a[i+1] * d[i]; | right — — |
| s243 | tsvc_c2proto | none | right — — | right — — |
| s244 | tsvc_c2proto | none | WRONG — a[i] = b[i] + c[i] * d[i]; ⟶ a[i+1] = b[i] + a[i+1] * d[i]; [a] | right — — |
| s252 | tsvc_c2proto | none | right — — | right — — |
| s254 | tsvc_c2proto | none | right — — | right — — |
| s255 | tsvc_c2proto | none | right — — | right — — |
| s258 | tsvc_c2proto | none | right — — | right — — |
| s277 | tsvc_c2proto | none | right — — | right — — |
| s281 | tsvc_c2proto | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s291 | tsvc_c2proto | none | right — — | right — — |
| s292 | tsvc_c2proto | none | right — — | right — — |
| s293 | tsvc_c2proto | none | right — — | right — — |
| s3112 | tsvc_c2proto | none | right — — | right — — |
| s313 | tsvc_c2proto | none | right — — | right — — |
| s321 | tsvc_c2proto | none | right — — | right — — |
| s322 | tsvc_c2proto | none | right — — | right — — |
| s323 | tsvc_c2proto | mutual: a[i] = b[i-1] / b[i] = a[i] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s331 | tsvc_c2proto | none | right — — | right — — |
| s341 | tsvc_c2proto | none | right — — | right — — |
| s424 | tsvc_c2proto | none | right — — | right — — |
| s481 | tsvc_c2proto | none | right — — | right — — |
| s482 | tsvc_c2proto | none | right — — | right — — |
| vas | tsvc_c2proto | none | right — — | right — — |
| vpvtv | tsvc_c2proto | none | right — — | right — — |

42 profiles.
Version 3: 39 right, 3 wrong: s212 (tsvc_c2proto): a FALSE order: `a[i] *= c[i];` before `b[i] += a[i + 1] * d[i];` (a) | s241 (tsvc_c2proto): a FALSE mutual: `a[i] = b[i] * c[i  ] * d[i];` / `b[i] = a[i] * a[i+1] * d[i];` | s244 (tsvc_c2proto): a FALSE order: `a[i] = b[i] + c[i] * d[i];` before `a[i+1] = b[i] + a[i+1] * d[i];` (a).
Version 4: 42 right, 0 wrong.
