| loop | layout | true | version 3 | version 4 |
|---|---|---|---|---|
| k17 | tsvc_c2 | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | tsvc_c2 | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k23 | tsvc_c2 | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k27 | tsvc_c2 | order: v[jv[i]] = u[ku[i]] / w[jw[i]] = v[kv[i]]; order: w[jw[i]] = v[kv[i]] / u[ju[i]] += w[kw[i]] | WRONG — w[jw[i]] = v[kv[i]] * e[i] + d[i]; ⟶ u[ju[i]] += w[kw[i]] * c[i]; [w] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ w[jw[i]] = v[kv[i]] * e[i] + d[i]; [v]<br>w[jw[i]] = v[kv[i]] * e[i] + d[i]; ⟶ u[ju[i]] += w[kw[i]] * c[i]; [w] |
| k31 | tsvc_c2 | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k42 | tsvc_c2 | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k48 | tsvc_c2 | order: u[ju[i]] += / v[jv[i]] = | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| k53 | tsvc_c2 | mutual: u[ju[i]] += / v[jv[i]] = | WRONG — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟷ v[jv[i]] = u[ku[i]] * d[i] + c[i]; |
| s000 | tsvc_c2 | none | right — — | right — — |
| s112 | tsvc_c2 | none | right — — | right — — |
| s1213 | tsvc_c2 | order: b[i] = a[i+1] / a[i] = b[i-1] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s121 | tsvc_c2 | none | right — — | right — — |
| s127 | tsvc_c2 | none | right — — | right — — |
| s131 | tsvc_c2 | none | right — — | right — — |
| s151 | tsvc_c2 | none | right — — | right — — |
| s152 | tsvc_c2 | none | right — — | right — — |
| s161 | tsvc_c2 | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s171 | tsvc_c2 | none | right — — | right — — |
| s211 | tsvc_c2 | order: b[i] = b[i + 1] / a[i] = b[i - 1] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s212 | tsvc_c2 | none | WRONG — a[i] *= c[i]; ⟶ b[i] += a[i + 1] * d[i]; [a] | right — — |
| s241 | tsvc_c2 | none | WRONG — a[i] = b[i] * c[i  ] * d[i]; ⟶ b[i] = a[i] * a[i+1] * d[i]; [a] | right — — |
| s243 | tsvc_c2 | none | WRONG — a[i] = b[i] + c[i  ] * d[i]; ⟷ b[i] = a[i] + d[i  ] * e[i]; | right — — |
| s244 | tsvc_c2 | none | WRONG — a[i] = b[i] + c[i] * d[i]; ⟶ a[i+1] = b[i] + a[i+1] * d[i]; [a] | right — — |
| s252 | tsvc_c2 | none | right — — | right — — |
| s254 | tsvc_c2 | none | right — — | right — — |
| s255 | tsvc_c2 | none | right — — | right — — |
| s258 | tsvc_c2 | none | right — — | right — — |
| s277 | tsvc_c2 | none | right — — | right — — |
| s281 | tsvc_c2 | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s291 | tsvc_c2 | none | right — — | right — — |
| s292 | tsvc_c2 | none | right — — | right — — |
| s293 | tsvc_c2 | none | right — — | right — — |
| s3112 | tsvc_c2 | none | right — — | right — — |
| s313 | tsvc_c2 | none | right — — | right — — |
| s321 | tsvc_c2 | none | right — — | right — — |
| s322 | tsvc_c2 | none | right — — | right — — |
| s323 | tsvc_c2 | mutual: a[i] = b[i-1] / b[i] = a[i] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s331 | tsvc_c2 | none | right — — | right — — |
| s341 | tsvc_c2 | none | right — — | right — — |
| s424 | tsvc_c2 | none | right — — | right — — |
| s481 | tsvc_c2 | none | right — — | right — — |
| s482 | tsvc_c2 | none | right — — | right — — |
| vas | tsvc_c2 | none | right — — | right — — |
| vpvtv | tsvc_c2 | none | right — — | right — — |

44 profiles.
Version 3: 38 right, 6 wrong: k27 (tsvc_c2): no order `v[jv[i]] = u[ku[i]]` before `w[jw[i]] = v[kv[i]]` | k53 (tsvc_c2): `u[ju[i]] +=` and `v[jv[i]] =` not called mutual; a FALSE order: `v[jv[i]] = u[ku[i]] * d[i] + c[i];` before `u[ju[i]] += v[kv[i]] * c[i];` (v) | s212 (tsvc_c2): a FALSE order: `a[i] *= c[i];` before `b[i] += a[i + 1] * d[i];` (a) | s241 (tsvc_c2): a FALSE order: `a[i] = b[i] * c[i  ] * d[i];` before `b[i] = a[i] * a[i+1] * d[i];` (a) | s243 (tsvc_c2): a FALSE mutual: `a[i] = b[i] + c[i  ] * d[i];` / `b[i] = a[i] + d[i  ] * e[i];` | s244 (tsvc_c2): a FALSE order: `a[i] = b[i] + c[i] * d[i];` before `a[i+1] = b[i] + a[i+1] * d[i];` (a).
Version 4: 44 right, 0 wrong.
