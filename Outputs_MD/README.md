# Outputs

Raw terminal outputs from quantum Φ validation tests.

## Quick Terminal Access
```bash
cd ~/Desktop/quantum-phi-validation/Outputs_MD
```

## Contents

- `test_quantum_phi_output.md` - Single backend test (ibm_fez)
- `test_quantum_phi_all_backends_output.md` - All backends (445 qubits)
- `test_quantum_phi_2qubit_gates_output.md` - Two-qubit gate analysis (1004 gates)
- `test_quantum_phi_deep_circuit_output.md` - Deep circuit validation (25-63x discrimination)
- `test_quantum_phi_threshold_sweep_output.md` - Threshold sensitivity (0.25 validated)

## Results Summary

| Test | Key Finding |
|------|-------------|
| Single qubit | r = 0.9458 correlation with T2/T1 |
| All backends | 445 qubits, 5 dead qubits identified |
| Two-qubit gates | 4.34x higher error when min_Φ < 0.25 |
| Deep circuits | 25-63x higher error for low-Φ qubits |
| Threshold sweep | 0.25 in optimal plateau (4.26x discrimination) |

## Note

All outputs are raw terminal paste. No AI editing of data.
