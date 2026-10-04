| loop | layout | true | version 3 | version 4 |
|---|---|---|---|---|
| k17 | tsvc_b1 | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k17 | tsvc_c1 | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | tsvc_b1 | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | tsvc_c1 | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k23 | tsvc_b1 | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k23 | tsvc_c1 | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k31 | tsvc_b1 | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k31 | tsvc_c1 | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k42 | tsvc_b1 | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k42 | tsvc_c1 | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k48 | tsvc_b1 | order: u[ju[i]] += / v[jv[i]] = | WRONG — — | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| k48 | tsvc_c1 | order: u[ju[i]] += / v[jv[i]] = | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| s000 | tsvc_b1 | none | right — — | right — — |
| s000 | tsvc_c1 | none | right — — | right — — |
| s112 | tsvc_b1 | none | right — — | right — — |
| s112 | tsvc_c1 | none | right — — | right — — |
| s1213 | tsvc_b1 | order: b[i] = a[i+1] / a[i] = b[i-1] | WRONG — a[i] = b[i-1]+c[i]; ⟷ b[i] = a[i+1]*d[i]; | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s1213 | tsvc_c1 | order: b[i] = a[i+1] / a[i] = b[i-1] | WRONG — — | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s121 | tsvc_b1 | none | right — — | right — — |
| s121 | tsvc_c1 | none | right — — | right — — |
| s127 | tsvc_b1 | none | right — — | right — — |
| s127 | tsvc_c1 | none | right — — | right — — |
| s131 | tsvc_b1 | none | right — — | right — — |
| s131 | tsvc_c1 | none | right — — | right — — |
| s151 | tsvc_b1 | none | right — — | right — — |
| s151 | tsvc_c1 | none | right — — | right — — |
| s152 | tsvc_b1 | none | right — — | right — — |
| s152 | tsvc_c1 | none | right — — | right — — |
| s161 | tsvc_b1 | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s161 | tsvc_c1 | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s171 | tsvc_b1 | none | right — — | right — — |
| s171 | tsvc_c1 | none | right — — | right — — |
| s211 | tsvc_b1 | order: b[i] = b[i + 1] / a[i] = b[i - 1] | WRONG — — | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s211 | tsvc_c1 | order: b[i] = b[i + 1] / a[i] = b[i - 1] | WRONG — — | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s212 | tsvc_b1 | none | WRONG — a[i] *= c[i]; ⟶ b[i] += a[i + 1] * d[i]; [a] | right — — |
| s212 | tsvc_c1 | none | WRONG — a[i] *= c[i]; ⟶ b[i] += a[i + 1] * d[i]; [a] | right — — |
| s241 | tsvc_b1 | none | right — — | right — — |
| s241 | tsvc_c1 | none | WRONG — a[i] = b[i] * c[i  ] * d[i]; ⟶ b[i] = a[i] * a[i+1] * d[i]; [a] | right — — |
| s243 | tsvc_b1 | none | WRONG — a[i] = b[i] + c[i  ] * d[i]; ⟷ b[i] = a[i] + d[i  ] * e[i]; | right — — |
| s243 | tsvc_c1 | none | WRONG — a[i] = b[i] + c[i  ] * d[i]; ⟶ b[i] = a[i] + d[i  ] * e[i]; [a] | right — — |
| s244 | tsvc_b1 | none | WRONG — a[i] = b[i] + c[i] * d[i]; ⟶ a[i+1] = b[i] + a[i+1] * d[i]; [a] | right — — |
| s244 | tsvc_c1 | none | right — — | right — — |
| s252 | tsvc_b1 | none | right — — | right — — |
| s252 | tsvc_c1 | none | right — — | right — — |
| s254 | tsvc_b1 | none | right — — | right — — |
| s254 | tsvc_c1 | none | right — — | right — — |
| s255 | tsvc_b1 | none | right — — | right — — |
| s255 | tsvc_c1 | none | right — — | right — — |
| s258 | tsvc_b1 | none | right — — | right — — |
| s258 | tsvc_c1 | none | right — — | right — — |
| s277 | tsvc_b1 | none | right — — | right — — |
| s277 | tsvc_c1 | none | right — — | right — — |
| s281 | tsvc_b1 | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s281 | tsvc_c1 | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s291 | tsvc_b1 | none | right — — | right — — |
| s291 | tsvc_c1 | none | right — — | right — — |
| s292 | tsvc_b1 | none | right — — | right — — |
| s292 | tsvc_c1 | none | right — — | right — — |
| s293 | tsvc_b1 | none | right — — | right — — |
| s293 | tsvc_c1 | none | right — — | right — — |
| s3112 | tsvc_b1 | none | right — — | right — — |
| s3112 | tsvc_c1 | none | right — — | right — — |
| s313 | tsvc_b1 | none | right — — | right — — |
| s313 | tsvc_c1 | none | right — — | right — — |
| s321 | tsvc_b1 | none | right — — | right — — |
| s321 | tsvc_c1 | none | right — — | right — — |
| s322 | tsvc_b1 | none | right — — | right — — |
| s322 | tsvc_c1 | none | right — — | right — — |
| s323 | tsvc_b1 | mutual: a[i] = b[i-1] / b[i] = a[i] | WRONG — b[i] = a[i] + c[i] * e[i]; ⟶ a[i] = b[i-1] + c[i] * d[i]; [b] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s323 | tsvc_c1 | mutual: a[i] = b[i-1] / b[i] = a[i] | WRONG — b[i] = a[i] + c[i] * e[i]; ⟶ a[i] = b[i-1] + c[i] * d[i]; [b] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s331 | tsvc_b1 | none | right — — | right — — |
| s331 | tsvc_c1 | none | right — — | right — — |
| s341 | tsvc_b1 | none | right — — | right — — |
| s341 | tsvc_c1 | none | right — — | right — — |
| s424 | tsvc_b1 | none | right — — | right — — |
| s424 | tsvc_c1 | none | right — — | right — — |
| s481 | tsvc_b1 | none | right — — | right — — |
| s481 | tsvc_c1 | none | right — — | right — — |
| s482 | tsvc_b1 | none | right — — | right — — |
| s482 | tsvc_c1 | none | right — — | right — — |
| vas | tsvc_b1 | none | right — — | right — — |
| vas | tsvc_c1 | none | right — — | right — — |
| vpvtv | tsvc_b1 | none | right — — | right — — |
| vpvtv | tsvc_c1 | none | right — — | right — — |

84 profiles.
Version 3: 71 right, 13 wrong: k48 (tsvc_b1): no order `u[ju[i]] +=` before `v[jv[i]] =` | s1213 (tsvc_b1): no order `b[i] = a[i+1]` before `a[i] = b[i-1]`; a FALSE mutual: `a[i] = b[i-1]+c[i];` / `b[i] = a[i+1]*d[i];` | s1213 (tsvc_c1): no order `b[i] = a[i+1]` before `a[i] = b[i-1]` | s211 (tsvc_b1): no order `b[i] = b[i + 1]` before `a[i] = b[i - 1]` | s211 (tsvc_c1): no order `b[i] = b[i + 1]` before `a[i] = b[i - 1]` | s212 (tsvc_b1): a FALSE order: `a[i] *= c[i];` before `b[i] += a[i + 1] * d[i];` (a) | s212 (tsvc_c1): a FALSE order: `a[i] *= c[i];` before `b[i] += a[i + 1] * d[i];` (a) | s241 (tsvc_c1): a FALSE order: `a[i] = b[i] * c[i  ] * d[i];` before `b[i] = a[i] * a[i+1] * d[i];` (a) | s243 (tsvc_b1): a FALSE mutual: `a[i] = b[i] + c[i  ] * d[i];` / `b[i] = a[i] + d[i  ] * e[i];` | s243 (tsvc_c1): a FALSE order: `a[i] = b[i] + c[i  ] * d[i];` before `b[i] = a[i] + d[i  ] * e[i];` (a) | s244 (tsvc_b1): a FALSE order: `a[i] = b[i] + c[i] * d[i];` before `a[i+1] = b[i] + a[i+1] * d[i];` (a) | s323 (tsvc_b1): `a[i] = b[i-1]` and `b[i] = a[i]` not called mutual; a FALSE order: `b[i] = a[i] + c[i] * e[i];` before `a[i] = b[i-1] + c[i] * d[i];` (b) | s323 (tsvc_c1): `a[i] = b[i-1]` and `b[i] = a[i]` not called mutual; a FALSE order: `b[i] = a[i] + c[i] * e[i];` before `a[i] = b[i-1] + c[i] * d[i];` (b).
Version 4: 84 right, 0 wrong.
