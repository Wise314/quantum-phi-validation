# Test: Circuit Depth Scaling Analysis

**Date:** December 31, 2025  
**Script:** `experiments/test_quantum_phi_depth_scaling.py`  
**Backend:** ibm_fez

## Purpose

Show error discrimination holds across circuit depths.

## Results

| Depth | LOW-Φ Error | HIGH-Φ Error | Ratio |
|-------|-------------|--------------|-------|
| 10 | 1.52% | 0.17% | 8.94x |
| 25 | 1.77% | 0.15% | 11.80x |
| 50 | 1.51% | 0.16% | 9.44x |
| 75 | 1.77% | 0.23% | 7.70x |
| 100 | 1.83% | 0.19% | 9.63x |
| 150 | 2.10% | 0.22% | 9.55x |
| 200 | 1.85% | 0.15% | 12.33x |
| 300 | 1.57% | 0.13% | 12.08x |
| 400 | 1.76% | 0.10% | 17.60x |
| 500 | 1.87% | 0.23% | 8.13x |

## Key Finding

- **8-18x discrimination** consistent across all depths (10-500 gates)
- HIGH-Φ qubits stay flat (~0.1-0.2% error) even at 500 gates
- LOW-Φ qubits consistently ~1.5-2% error
- Φ predicts circuit error across ALL depths

## Conclusion

Φ discrimination holds regardless of circuit depth.
Total circuits: 200 (20 qubits × 10 depths)
NO synthetic data.
