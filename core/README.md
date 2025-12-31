# Core

Standalone Φ calculation source code.

No dependencies on external repositories.

## Contents

- `phi_quantum.py` - Φ calculation for quantum systems (to be added)

## Formula
```
Φ = I × ρ - α × S

For qubits (2-level systems):
- I = (fidelity - 0.50) / 0.50
- ρ = T2 / T1
- S = readout_error
- α = 0.1
- Threshold: Φ_c = 0.25
```
