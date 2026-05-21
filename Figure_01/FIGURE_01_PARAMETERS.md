# Figure 01 — Panel Parameters

## Network & Fixed Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| N | 50 | Number of FitzHugh-Nagumo nodes |
| P | 10 | Neighbourhood half-width (circulant ring) |
| γ (gamma) | 0.06 | Coupling strength (`c_00600`, i.e. 600 × 10⁻⁴) |
| α (alpha) | 0.99 | FHN excitability parameter |
| I | 0.0 | External current |

---

## Panel (a)

| Parameter | Value |
|-----------|-------|
| **Data file tag** | `n_00060_c_00600` |
| **Noise d** | 0.006 (= 60 × 10⁻⁴) |
| **Coupling γ** | 0.06 |
| **Highlighted node** | 30 (1-indexed) |
| **t₀** | 259.110 (× 10³ steps) |
| **t₁** | 269.265 (× 10³ steps) |
| **Inset window** | [t₀ − 2.0, t₁ + 2.0] (× 10³ steps) |
| **Sweep range** | 259.010 → 269.365 (× 10³ steps) |
| **Sweep frames** | 10 356 |

---

## Panel (b)

| Parameter | Value |
|-----------|-------|
| **Data file tag** | `n_00140_c_00600` |
| **Noise d** | 0.014 (= 140 × 10⁻⁴) |
| **Coupling γ** | 0.06 |
| **Highlighted node** | 31 (1-indexed) |
| **t₀** | 409.050 (× 10³ steps) |
| **t₁** | 412.010 (× 10³ steps) |
| **Inset window** | [t₀ − 3.0, t₁ + 5.0] (× 10³ steps) |
| **Sweep range** | 408.900 → 412.210 (× 10³ steps) |
| **Sweep frames** | 3 311 |

---

## Notes

- Time values are in units of **10³ simulation steps** (e.g. t = 269.265 → absolute step 269 265 + 5 000 = 274 265).
- The inset spacetime raster always shows the fixed window [t₀ − dt₀, t₁ + dt₁] regardless of the current frame t.
- Two vector variants are generated per panel: **normalised** (unit length, scaled to 0.4) and **raw** (actual magnitude, unscaled).
- Vectors: hotpink = coupling (C), blueviolet = local dynamics (L), teal = noise (N).
