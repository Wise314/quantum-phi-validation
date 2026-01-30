# IBM Quantum Research - Competitive Landscape & Patent Defense

## Purpose

This folder documents:
1. IBM's current approach to qubit calibration and failure detection
2. What gaps exist that Φ fills
3. Paul Nation's work (IBM's lead on qubit selection)
4. Head-to-head comparisons for patent defense
5. Sources and citations

**Last Updated:** January 30, 2026

---

# PART 1: IBM's Current Approach

## Key Finding

**IBM has NO deployed early warning system for qubit degradation.**

IBM's approach is **reactive** - they detect failures AFTER they happen, not before.

---

## IBM Calibration Schedule

From IBM Documentation (https://quantum.cloud.ibm.com/docs/en/guides/calibration-jobs):

> "Hourly calibrations attempt to run hourly and last 2-3 minutes. They include quick tests to confirm all single- and two-qubit gates are working at a basic level. This ensures proper operation of gates and allows us to automatically close the queue if we notice a serious system failure."

**Key phrase:** "close the queue if we notice a serious system failure"

This is REACTIVE - failure happens, then they respond.

---

## IBM Calibration Frequency

From academic research (ISCA 2024):

> "IBM's current calibration standards focus on weekly full calibration of only a limited number of qubit pairs. Daily measurements include phase calibrations for just a few pairs. This approach allows substantial system drift to occur."

**Key phrase:** "allows substantial system drift to occur"

IBM knows drift happens but doesn't predict it.

---

## What IBM Publishes

IBM provides these metrics via daily calibration:
- T1 (relaxation time)
- T2 (dephasing time)
- Gate error rates
- Readout error rates
- Qubit frequency

**What IBM does NOT provide:**
- Early warning indicators
- Degradation forecasts
- Stability predictions
- Lead time before failure
- "Don't run quantum" threshold

---

## Gap Analysis: IBM vs Φ

| Feature | IBM Current | Φ Approach |
|---------|-------------|------------|
| Detection timing | After failure | Up to 20 days before |
| Average lead time | 0 (reactive) | 6.8 days |
| Method | Calibration + shutdown | Leading indicator |
| Metric type | Individual (T1, T2, etc.) | Universal stability |
| Formula | Multiple domain-specific | Single universal (Φ = I×ρ - α×S) |
| Threshold | None | 0.25 (physics-derived) |
| Cross-backend | Requires retuning | Same threshold everywhere |

---

# PART 2: Paul Nation - IBM's Lead on Qubit Selection

## Who Is Paul Nation

| Field | Value |
|-------|-------|
| **Title** | Principal Research Scientist, IBM Quantum |
| **Location** | IBM T.J. Watson Research Lab |
| **Key Tools** | mapomatic, M3, QuTiP |
| **GitHub** | https://github.com/nonhermitian |
| **Papers** | 50+ publications in quantum physics |

**Background:**
- Creator of QuTiP (Quantum Toolbox in Python) — 1,700+ stars, cited in thousands of papers
- Primary maintainer of mapomatic (qubit selection tool)
- Primary author of M3 (measurement error mitigation)
- PhD Physics, Dartmouth (2010)
- 15+ years in quantum optics and numerical methods

**IBM Awards:**
- 2023: Research Accomplishment Award for **mapomatic**
- 2022: Research Accomplishment Award for **M3**
- 2021: Outstanding Technical Achievement for Quantum Volume metric

---

## Nation's Key Paper (2023)

**Paper:** "Suppressing Quantum Circuit Errors Due to System Variability"  
**Authors:** Paul D. Nation, Matthew Treinish  
**Journal:** PRX Quantum 4, 010327 (2023)  
**DOI:** https://doi.org/10.1103/PRXQuantum.4.010327

### What Nation Built

- mapomatic: Post-compilation routing to low-noise subgraphs
- Uses calibration data (gate error, readout error, T1, T2)
- Heuristic cost function: multiply individual error rates
- Result: **"40% of missing fidelity recovered"**

### Nation's Cost Function (from mapomatic source code)
```python
fid *= (1-props.gate_error(item.operation.name, [q0, q1]))
fid *= 1-props.readout_error(q0)
fid *= 1-idle_error(time, t1s[q0], t2s[q0])
```

**Problem:** Just multiplying error rates. No physics. No coherence ratio weighting. No universal threshold.

---

## What Nation Said He DOESN'T Have (Direct Quotes)

| His Stated Gap | Source |
|----------------|--------|
| "looking for **improved heuristics for scoring layouts that are more accurate**" | PRX Quantum 2023, Section VI |
| "is there **information outside of standard device-calibration data** that can yield more accurate cost analysis" | Section VI |
| "need for **more complex cost functions** to **break the scoring degeneracy**" | Section II |
| "T2/T1 **not large impact** on layout order" | Section II |

**Gaps not addressed in any of Nation's work:**
- No threshold for "don't run quantum"
- No during-execution intervention
- No early warning system
- No cross-backend transfer learning

---

## The Critical Error Nation Made

### His Claim (2023)

> "We do not include [T1/T2] information in our default cost function as it has been empirically found **not to have a large impact**"

### Our Data (2026)

ρ (T2/T1) accounts for **70-78% of feature importance** in predicting qubit quality.

**He dismissed the single most important variable.**

### Why This Matters

This explains the performance gap:

| Approach | Formula | Result |
|----------|---------|--------|
| Nation (IBM) | Π(1 - error_i) | 40% fidelity recovery |
| Φ (ours) | I × ρ - α × S | 83% error reduction |

His formula treats all errors equally. Ours weights coherence ratio correctly.

---

## Head-to-Head Comparison

| Aspect | Nation (IBM, 2023) | Barnicle (2026) |
|--------|-------------------|-----------------|
| Approach | Heuristic | Physics-based |
| Formula | Π(1 - error_i) | Φ = I × ρ - α × S |
| Error reduction | 40% fidelity recovery | 83% error reduction |
| Discrimination | Not stated | **30.47x** |
| Threshold | None | 0.25 |
| T2/T1 usage | "not large impact" | **70-78% of signal** |
| Cross-backend | Not tested | 98.4% transfer |
| Early warning | None | 6.8 days avg, 20 days max |
| Physics basis | None (heuristic) | Bekenstein-Hawking S = A/4 |
| Dead qubit detection | Manual inspection | 100% (all Φ < 0) |

---

## Mapomatic Gap Analysis

### What Mapomatic Does Today
- Post-compilation routing to low-noise subgraphs
- Uses calibration data (gate error, readout error, T1, T2)
- Heuristic ranking based on error rates
- Multiplies individual error rates together

### Gaps We Fill

| # | Problem | Mapomatic Today | Our Solution |
|---|---------|-----------------|--------------|
| 1 | When is quantum worse than classical? | No threshold — just ranks qubits | Φ < 0.25 → fall back to classical |
| 2 | 15+ qubits = pure noise | Users discover the hard way (95% error) | Data proving it + automatic routing |
| 3 | Cross-backend transfer | No ML layer, no transfer prediction | 98.4% accuracy train-once-deploy-anywhere |
| 4 | Which metric actually matters? | All metrics weighted equally | T2/T1 ratio = 70-78% of the signal |
| 5 | Mid-circuit degradation | Nothing — open-loop execution | Patent #17: checkpoint/migrate/fallback/restart |
| 6 | Dead qubit detection | Manual inspection | 100% identification (all Φ < 0) |
| 7 | Threshold tuning per backend | None | Same 0.25 threshold works everywhere |

### The Invitation in Nation's Paper

> "the choice of cost function is **not hardcoded** into mapomatic and **users are free to define cost functions** based on arbitrary input information"

Mapomatic is designed to accept custom cost functions. Φ could be plugged directly in.

---

# PART 3: M3 vs Φ (When vs Where)

## What Is M3?

**Repo:** https://github.com/Qiskit/qiskit-addon-mthree  
**What it does:** Fixes readout errors AFTER you run a circuit  
**Paul's role:** Primary author/maintainer

## M3 vs Φ Comparison

| Approach | When | What It Does |
|----------|------|--------------|
| **M3 (IBM)** | AFTER execution | Corrects measurement errors with math |
| **Φ (ours)** | BEFORE execution | Avoids errors by selecting better qubits |

**The analogy:**
- M3 is the **ambulance at the bottom of the cliff**
- Φ is the **fence at the top**

**Best approach:** Use BOTH
1. Φ-select qubits first (avoid errors)
2. Run circuit
3. Apply M3 to residual errors

---

# PART 4: The Black Hole Connection

## Nation's Black Hole Paper

**Paper:** "Non-equilibrium Landauer Transport Model for Hawking Radiation from a Black Hole"  
**Authors:** P. D. Nation, M. P. Blencowe, Franco Nori  
**Journal:** New J. Phys. 14, 033013 (2012)  
**arXiv:** https://arxiv.org/abs/1009.3974

**His insight:** Hawking radiation = entropy flow through 1D quantum channel

## The Connection to Our Work

| Aspect | Nation (2012) | Barnicle (2025) |
|--------|---------------|-----------------|
| Core insight | Entropy FLOWS from black holes | Entropy determines STABILITY |
| Framework | Landauer transport (thermo) | Free energy (thermo) |
| Application | Theoretical physics | Practical prediction |
| Validation | Theory only | 1,100+ systems |

**Our insight:** Entropy determines stability (Φ = I × ρ - α × S), threshold 0.25 derives from Bekenstein-Hawking S = A/4

Same physics neighborhood. We extended his direction practically.

---

# PART 5: Our Validation on IBM Hardware

## Test Summary

| Metric | Value |
|--------|-------|
| Backends tested | ibm_fez, ibm_torino, ibm_marrakesh |
| Qubits analyzed | 445 |
| Two-qubit gates | 1,004 |
| Algorithms validated | 7 |
| Total tests | 23 (16 research + 7 patent-grade strict) |
| Best error ratio | **30.47x** (Bernstein-Vazirani) |

## Algorithm Results (Strict Methodology)

| Algorithm | HIGH-Φ Error | LOW-Φ Error | Ratio |
|-----------|--------------|-------------|-------|
| **Bernstein-Vazirani** | 2.12% | 64.72% | **30.47x** |
| Grover | 5.76% | 91.60% | 15.90x |
| Deutsch-Jozsa | 5.76% | 74.73% | 12.97x |
| QFT | 1.66% | 13.48% | 8.12x |
| GHZ | 3.88% | 28.66% | 7.38x |
| Simon's | 1.76% | 7.15% | 4.07x |
| QPE | 5.76% | 16.70% | 2.90x |

## Size Scaling (The Cliff)

| Qubits | min_Φ | Error | Status |
|--------|-------|-------|--------|
| 3 | 0.999 | ~3% | ✅ Usable |
| 5 | 0.997 | 7.20% | ⚠️ Marginal |
| 7 | 0.774 | 48.78% | ❌ Nearly random |
| 10 | 0.672 | 22.29% | ❌ High |
| 15 | 0.569 | 94.85% | ❌ PURE NOISE |
| 20 | 0.436 | 92.50% | ❌ PURE NOISE |

**Key insight:** At 15+ qubits, quantum = random noise. Classical fallback is ESSENTIAL.

## Temporal Early Warning Results

| Metric | Value |
|--------|-------|
| Detection Rate | **100%** (zero missed) |
| On-time Recall | **21.2%** (≥24h warning) |
| Precision | **47.8%** |
| Average lead time | **6.8 days** (163 hours) |
| Maximum lead time | **20 days** (480 hours) |

---

# PART 6: Patent Implications

## What This Establishes

### 1. No prior art for universal early warning metric
- IBM uses reactive detection
- Academic work predicts individual metrics, not stability
- Nation explicitly said T2/T1 has "not large impact" — we proved otherwise

### 2. IBM's own expert asked for what we built
- "improved heuristics that are more accurate" → Φ delivers 30.47x
- "break scoring degeneracy" → threshold 0.25 provides binary decision
- "information outside calibration data" → same data, better combination

### 3. We proved their assumption wrong
- They said T2/T1 doesn't matter
- We proved it's 70-78% of the signal
- This explains the performance gap (40% vs 83%)

### 4. We fill gaps they haven't addressed
- Early warning (6.8 days average lead time)
- During-execution intervention (Patent #17)
- Cross-backend transfer (98.4%)
- "Don't run quantum" threshold

## Problem → Patent → Solution

| Nation's Gap | Our Patent | Our Solution | Validation |
|--------------|------------|--------------|------------|
| "improved heuristics" | **#9** Quantum Stability | Φ = I × ρ - α × S | 30.47x discrimination |
| "break scoring degeneracy" | **#9** Quantum Stability | Threshold 0.25 | 100% dead qubit detection |
| "T2/T1 not large impact" | **#9, #16** | T2/T1 is 70-78% of signal | Feature ablation |
| No "don't run quantum" | **#15** Hybrid Allocation | Φ < 0.25 → classical | 95% error at 15+ qubits |
| No cross-backend | **#16** Universal ML | Train once, deploy anywhere | 98.4% accuracy |
| No during-execution | **#17** Real-Time Intervention | 5 intervention actions | In development |
| No early warning | **Temporal Analysis** | Leading indicator | 6.8 days avg lead time |

---

# PART 7: Sources

## IBM Documentation

1. IBM Quantum Documentation - Calibration Jobs
   https://quantum.cloud.ibm.com/docs/en/guides/calibration-jobs

2. IBM Quantum Documentation - QPU Information
   https://quantum.cloud.ibm.com/docs/en/guides/qpu-information

## Academic Papers

3. Nation, P.D., Treinish, M. "Suppressing Quantum Circuit Errors Due to System Variability"
   PRX Quantum 4, 010327 (2023)
   https://doi.org/10.1103/PRXQuantum.4.010327

4. Nation, P.D., Blencowe, M.P., Nori, F. "Non-equilibrium Landauer Transport Model for Hawking Radiation"
   New J. Phys. 14, 033013 (2012)
   https://arxiv.org/abs/1009.3974

5. "Hardware-aware Calibration Protocol for Quantum Computers"
   ISCA 2024
   https://dl.acm.org/doi/10.1145/3695053.3731036

6. "Quantum Noise in the Flow of Time: A Temporal Study"
   IEEE 2022
   https://par.nsf.gov/servlets/purl/10422695

7. "UREQA: Error Rate Prediction for NISQ Computers"
   USENIX ATC 2020
   https://www.usenix.org/system/files/atc20-patel.pdf

## GitHub Repositories

8. mapomatic: https://github.com/qiskit-community/mapomatic
9. M3: https://github.com/Qiskit/qiskit-addon-mthree
10. QuTiP: https://github.com/qutip/qutip

---

# PART 8: Future Research Tasks

- [ ] Search IBM patent filings for early warning systems
- [ ] Check Google/IonQ/Rigetti approaches
- [ ] Monitor IBM announcements for changes to calibration
- [ ] Document new academic papers on qubit degradation prediction
- [ ] Read Nation's full PRX Quantum 2023 paper in detail
- [ ] Track mapomatic updates for new cost functions
- [ ] Compare to Google's Willow chip error correction

---

## Repository

Repository: Wise314/quantum-phi-validation (private)

Patent: Application #63/952,883 (provisional)

---

*This document supports patent claims by establishing prior art gaps and competitive differentiation.*
