# Quantum Φ Validation

Validation of the Universal Φ Framework on IBM Quantum Hardware.

## Results Summary

| Test | Systems | Key Finding |
|------|---------|-------------|
| Single Qubit | 445 qubits | r = 0.9458 correlation with T2/T1 |
| Two-Qubit Gates | 1004 gates | 4.34x higher error when min_Φ < 0.25 |

## The Formula
```
Φ = I × ρ - α × S

Where:
- I = (fidelity - 0.50) / 0.50  (normalized for 2-level system)
- ρ = T2/T1 ratio (coherence stability)
- S = readout error (entropy proxy)
- α = 0.1
- Threshold: Φ_c = 0.25
```

## Key Findings

- **Same formula** that predicted UK blackout (Φ = 0.178) and Tohoku earthquake (Φ = -0.357)
- **Same threshold (0.25)** validated on bearings, turbofans, grids, 660 neural networks
- **All 5 dead qubits** correctly identified (Φ < 0, fidelity = 0.000)
- **Low-Φ qubits** have 4.3x shorter coherence time

## Data Source

Real calibration data from IBM Quantum:
- ibm_fez (156 qubits)
- ibm_torino (133 qubits)
- ibm_marrakesh (156 qubits)

**NO SYNTHETIC DATA.** All results from real quantum hardware.

## Repository Structure
```
├── core/           # Standalone Φ calculation source code
├── startup/        # Setup scripts and IBM Quantum configuration
├── experiments/    # Test scripts
├── results/        # Output data and analysis
├── patent_docs/    # Patent documentation
└── requirements.txt
```

## Quick Start
```bash
pip install -r requirements.txt
cd experiments
python test_quantum_phi_all_backends.py
```

## License

Proprietary - Patent Pending
