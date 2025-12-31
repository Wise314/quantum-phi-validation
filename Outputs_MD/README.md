# Outputs

Raw terminal outputs from quantum Φ validation tests.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation/Outputs_MD
```

## Contents

| File | Test | Result |
|------|------|--------|
| test_quantum_phi_output.md | Single backend (ibm_fez) | ✓ |
| test_quantum_phi_all_backends_output.md | All backends (445 qubits) | ✓ |
| test_quantum_phi_2qubit_gates_output.md | Two-qubit gates (1004) | ✓ |
| test_quantum_phi_deep_circuit_output.md | Deep circuits (10-200 gates) | ✓ |
| test_quantum_phi_threshold_sweep_output.md | Threshold sensitivity | ✓ |
| test_quantum_phi_ghz_output.md | GHZ entanglement | ✓ |
| test_quantum_phi_bell_states_output.md | Bell states | ⚠️ Inconclusive |
| test_quantum_phi_stress_test_output.md | T-gate & identity stress | ✓ |
| test_quantum_phi_cross_backend_output.md | Cross-backend validation | ✓ |

## Results Summary

| Test | Key Finding |
|------|-------------|
| Single qubit | r = 0.9458 correlation with T2/T1 |
| All backends | 445 qubits, 5 dead qubits identified |
| Two-qubit gates | 4.34x higher error when min_Φ < 0.25 |
| Deep circuits | 25-63x higher error for low-Φ qubits |
| Threshold sweep | 0.25 in optimal plateau (4.26x discrimination) |
| GHZ entanglement | 4.42x higher error for low-Φ triplets |
| Bell states | Inconclusive (gate quality varies) |
| Stress tests | 16x-∞ higher error for low-Φ |
| Cross-backend | 2.5x-5.75x on torino/marrakesh |

**8/9 tests validate Φ. 1 inconclusive (not contradictory).**

## Note

All outputs are raw terminal paste. No AI editing of data.
