# Test E: Variational Circuit Performance

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_variational.py`  
**Backend:** ibm_fez

## Purpose

Test Φ impact on VQE/QAOA-style variational circuits.

## Raw Output
```
LOW-Φ pairs (min_Φ < 0.25): 34
HIGH-Φ pairs (min_Φ ≥ 0.25): 140

Testing 15 pairs from each group

Ansatz depth: 2 layers
Group        Mean TVD     Std TVD      n     
LOW-Φ        0.0311       0.0123       15    
HIGH-Φ       0.0276       0.0101       15    
TVD ratio: 1.13x (higher = less consistent)
LOW-Φ pairs are LESS consistent ✓

Ansatz depth: 4 layers
Group        Mean TVD     Std TVD      n     
LOW-Φ        0.0228       0.0112       15    
HIGH-Φ       0.0284       0.0153       15    
TVD ratio: 0.80x

Ansatz depth: 6 layers
Group        Mean TVD     Std TVD      n     
LOW-Φ        0.0321       0.0140       15    
HIGH-Φ       0.0376       0.0175       15    
TVD ratio: 0.85x

Ansatz depth: 8 layers
Group        Mean TVD     Std TVD      n     
LOW-Φ        0.0193       0.0078       15    
HIGH-Φ       0.0230       0.0095       15    
TVD ratio: 0.84x

FINAL ANALYSIS: Entropy of Output Distributions
Group        Mean Entropy   Std         
LOW-Φ        1.5612         0.0606      
HIGH-Φ       1.5465         0.0933      
(Max entropy for 2 qubits = 2.0 bits)

LOW-Φ pairs have 0.0147 bits HIGHER entropy (more noise)
```

## Summary

### TVD Consistency (run-to-run variation)

| Depth | LOW-Φ TVD | HIGH-Φ TVD | Ratio | Expected? |
|-------|-----------|------------|-------|-----------|
| 2 layers | 0.0311 | 0.0276 | 1.13x | ✓ |
| 4 layers | 0.0228 | 0.0284 | 0.80x | ✗ |
| 6 layers | 0.0321 | 0.0376 | 0.85x | ✗ |
| 8 layers | 0.0193 | 0.0230 | 0.84x | ✗ |

### Entropy Analysis

| Group | Mean Entropy | Difference |
|-------|--------------|------------|
| LOW-Φ | 1.5612 bits | +0.0147 bits (more noise) |
| HIGH-Φ | 1.5465 bits | baseline |

## Key Finding

**WEAK/MIXED RESULTS**

- TVD consistency metric shows inverted results for deeper circuits
- Entropy shows correct pattern (LOW-Φ more noisy) but small effect
- Effect size is small compared to other tests

## Interpretation

Variational circuits may be less sensitive to single-qubit quality because:
1. Random parameters create inherently noisy outputs
2. Entangling gates dominate error (not captured by single-qubit Φ)
3. TVD metric may be too noisy for this use case

This test is INCONCLUSIVE - does not strongly validate or contradict Φ.
