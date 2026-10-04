| loop | layout | true | version 3 | version 4 |
|---|---|---|---|---|
| k17 | v4 | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k17 | v5 | order: v[jv[i]] += / u[ju[i]] += | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] += u[ku[i]] * d[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | v4 | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k19 | v5 | order: v[jv[i]] = / u[ju[i]] += | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] | right — v[jv[i]] = u[ku[i]] * d[i] + c[i]; ⟶ u[ju[i]] += v[kv[i]] * c[i]; [v] |
| k23 | v4 | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k23 | v5 | order: v[i] = x[i] / u[i] += w[i] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] | right — v[i] = x[i] * d[i] + c[i]; ⟶ u[i] += w[i] * c[i]; [w] |
| k31 | v4 | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k31 | v5 | order: v[i] = u[i + far] / u[i] += v[i + off] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] | right — v[i] = u[i + far] * d[i] + c[i]; ⟶ u[i] += v[i + off] * c[i]; [v] |
| k36 | v4 | order: v[i] = AT2 / u[i] += AT1 | right — v[i] = AT2(u, i) * d[i] + c[i]; ⟶ u[i] += AT1(v, i) * c[i]; [v] | right — v[i] = AT2(u, i) * d[i] + c[i]; ⟶ u[i] += AT1(v, i) * c[i]; [v] |
| k36 | v5 | order: v[i] = AT2 / u[i] += AT1 | right — v[i] = AT2(u, i) * d[i] + c[i]; ⟶ u[i] += AT1(v, i) * c[i]; [v] | right — v[i] = AT2(u, i) * d[i] + c[i]; ⟶ u[i] += AT1(v, i) * c[i]; [v] |
| k42 | v4 | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k42 | v5 | order: u[ju[i]] += / v[jv[i]] += | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] += u[ku[i]] * d[i]; [u] |
| k48 | v4 | order: u[ju[i]] += / v[jv[i]] = | WRONG — — | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| k48 | v5 | order: u[ju[i]] += / v[jv[i]] = | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] | right — u[ju[i]] += v[kv[i]] * c[i]; ⟶ v[jv[i]] = u[ku[i]] * d[i] + c[i]; [u] |
| s000 | v4 | none | right — — | right — — |
| s000 | v5 | none | right — — | right — — |
| s112 | v4 | none | right — — | right — — |
| s112 | v5 | none | right — — | right — — |
| s1213 | v4 | order: b[i] = a[i+1] / a[i] = b[i-1] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s1213 | v5 | order: b[i] = a[i+1] / a[i] = b[i-1] | WRONG — — | right — b[i] = a[i+1]*d[i]; ⟶ a[i] = b[i-1]+c[i]; [b] |
| s121 | v4 | none | right — — | right — — |
| s121 | v5 | none | right — — | right — — |
| s127 | v4 | none | right — — | right — — |
| s127 | v5 | none | right — — | right — — |
| s131 | v4 | none | right — — | right — — |
| s131 | v5 | none | right — — | right — — |
| s151 | v4 | none | right — — | right — — |
| s151 | v5 | none | right — — | right — — |
| s152 | v4 | none | right — — | right — — |
| s152 | v5 | none | right — — | right — — |
| s161 | v4 | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s161 | v5 | order: c[i+1] = a[i] / a[i] = c[i] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] | right — c[i+1] = a[i] + d[i] * d[i]; ⟶ a[i] = c[i] + d[i] * e[i]; [c] |
| s171 | v4 | none | right — — | right — — |
| s171 | v5 | none | right — — | right — — |
| s211 | v4 | order: b[i] = b[i + 1] / a[i] = b[i - 1] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s211 | v5 | order: b[i] = b[i + 1] / a[i] = b[i - 1] | WRONG — — | right — b[i] = b[i + 1] - e[i] * d[i]; ⟶ a[i] = b[i - 1] + c[i] * d[i]; [b] |
| s212 | v4 | none | WRONG — a[i] *= c[i]; ⟶ b[i] += a[i + 1] * d[i]; [a] | right — — |
| s212 | v5 | none | right — — | right — — |
| s241 | v4 | none | WRONG — a[i] = b[i] * c[i  ] * d[i]; ⟶ b[i] = a[i] * a[i+1] * d[i]; [a] | right — — |
| s241 | v5 | none | WRONG — a[i] = b[i] * c[i  ] * d[i]; ⟶ b[i] = a[i] * a[i+1] * d[i]; [a] | right — — |
| s243 | v4 | none | right — — | right — — |
| s243 | v5 | none | right — — | right — — |
| s244 | v4 | none | WRONG — a[i] = b[i] + c[i] * d[i]; ⟶ a[i+1] = b[i] + a[i+1] * d[i]; [a] | right — — |
| s244 | v5 | none | WRONG — a[i] = b[i] + c[i] * d[i]; ⟶ a[i+1] = b[i] + a[i+1] * d[i]; [a] | right — — |
| s252 | v4 | none | right — — | right — — |
| s252 | v5 | none | right — — | right — — |
| s254 | v4 | none | right — — | right — — |
| s254 | v5 | none | right — — | right — — |
| s255 | v4 | none | right — — | right — — |
| s255 | v5 | none | right — — | right — — |
| s258 | v4 | none | right — — | right — — |
| s258 | v5 | none | right — — | right — — |
| s277 | v4 | none | right — — | right — — |
| s277 | v5 | none | right — — | right — — |
| s281 | v4 | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s281 | v5 | mutual: x = a[LEN_1D-i-1] / a[i] = x- | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; | right — x = a[LEN_1D-i-1] + b[i] * c[i]; ⟷ a[i] = x-(real_t)1.0; |
| s291 | v4 | none | right — — | right — — |
| s291 | v5 | none | right — — | right — — |
| s292 | v4 | none | right — — | right — — |
| s292 | v5 | none | right — — | right — — |
| s293 | v4 | none | right — — | right — — |
| s293 | v5 | none | right — — | right — — |
| s3112 | v4 | none | right — — | right — — |
| s3112 | v5 | none | right — — | right — — |
| s313 | v4 | none | right — — | right — — |
| s313 | v5 | none | right — — | right — — |
| s321 | v4 | none | right — — | right — — |
| s321 | v5 | none | right — — | right — — |
| s322 | v4 | none | right — — | right — — |
| s322 | v5 | none | right — — | right — — |
| s323 | v4 | mutual: a[i] = b[i-1] / b[i] = a[i] | WRONG — b[i] = a[i] + c[i] * e[i]; ⟶ a[i] = b[i-1] + c[i] * d[i]; [b] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s323 | v5 | mutual: a[i] = b[i-1] / b[i] = a[i] | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; | right — a[i] = b[i-1] + c[i] * d[i]; ⟷ b[i] = a[i] + c[i] * e[i]; |
| s331 | v4 | none | right — — | right — — |
| s331 | v5 | none | right — — | right — — |
| s341 | v4 | none | right — — | right — — |
| s341 | v5 | none | right — — | right — — |
| s424 | v4 | none | right — — | right — — |
| s424 | v5 | none | right — — | right — — |
| s481 | v4 | none | right — — | right — — |
| s481 | v5 | none | right — — | right — — |
| s482 | v4 | none | right — — | right — — |
| s482 | v5 | none | right — — | right — — |
| vas | v4 | none | right — — | right — — |
| vas | v5 | none | right — — | right — — |
| vpvtv | v4 | none | right — — | right — — |
| vpvtv | v5 | none | right — — | right — — |

86 profiles.
Version 3: 77 right, 9 wrong: k48 (v4): no order `u[ju[i]] +=` before `v[jv[i]] =` | s1213 (v5): no order `b[i] = a[i+1]` before `a[i] = b[i-1]` | s211 (v5): no order `b[i] = b[i + 1]` before `a[i] = b[i - 1]` | s212 (v4): a FALSE order: `a[i] *= c[i];` before `b[i] += a[i + 1] * d[i];` (a) | s241 (v4): a FALSE order: `a[i] = b[i] * c[i  ] * d[i];` before `b[i] = a[i] * a[i+1] * d[i];` (a) | s241 (v5): a FALSE order: `a[i] = b[i] * c[i  ] * d[i];` before `b[i] = a[i] * a[i+1] * d[i];` (a) | s244 (v4): a FALSE order: `a[i] = b[i] + c[i] * d[i];` before `a[i+1] = b[i] + a[i+1] * d[i];` (a) | s244 (v5): a FALSE order: `a[i] = b[i] + c[i] * d[i];` before `a[i+1] = b[i] + a[i+1] * d[i];` (a) | s323 (v4): `a[i] = b[i-1]` and `b[i] = a[i]` not called mutual; a FALSE order: `b[i] = a[i] + c[i] * e[i];` before `a[i] = b[i-1] + c[i] * d[i];` (b).
Version 4: 86 right, 0 wrong.
