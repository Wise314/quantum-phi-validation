"""
Test: Does Φ Predict Two-Qubit Gate Errors?

Two-qubit gates are the bottleneck in quantum computing.
If Φ predicts which qubit PAIRS will have higher errors, that's huge.

Hypothesis: Pairs with lower average Φ should have higher 2-qubit gate errors.

NO SYNTHETIC DATA. Real IBM Quantum calibration only.
"""

import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA = 0.1
THRESHOLD = 0.25


def calculate_qubit_phi(fidelity, t1, t2, readout_error):
    """Calculate Φ for a single qubit."""
    random_baseline = 0.50
    if fidelity <= random_baseline:
        I = 0.0
    else:
        I = (fidelity - random_baseline) / (1.0 - random_baseline)
    
    if t1 > 0 and t2 > 0:
        rho = min(t2 / t1, 1.0)
    else:
        rho = 0.0
    
    S = readout_error
    phi = I * rho - ALPHA * S
    
    return phi


def get_qubit_phi(backend, target, qubit_idx):
    """Get Φ for a single qubit. Returns None if data unavailable."""
    try:
        props = backend.qubit_properties(qubit_idx)
        t1 = props.t1
        t2 = props.t2
        
        if t1 is None or t2 is None:
            return None
        
        t1_us = t1 * 1e6
        t2_us = t2 * 1e6
        
        sx_props = target['sx'][(qubit_idx,)]
        if sx_props.error is None:
            return None
        fidelity = 1.0 - sx_props.error
        
        meas_props = target['measure'][(qubit_idx,)]
        if meas_props.error is None:
            return None
        readout_error = meas_props.error
        
        return calculate_qubit_phi(fidelity, t1_us, t2_us, readout_error)
    except:
        return None


def analyze_two_qubit_gates(service, backend_name):
    """Analyze correlation between qubit Φ and two-qubit gate errors."""
    print(f"\n{'='*70}")
    print(f"TWO-QUBIT GATE ANALYSIS: {backend_name}")
    print('='*70)
    
    backend = service.backend(backend_name)
    target = backend.target
    
    # Find all two-qubit gates (CZ or ECR depending on backend)
    two_qubit_gate = None
    for gate_name in ['cz', 'ecr', 'cx']:
        if gate_name in target.operation_names:
            two_qubit_gate = gate_name
            break
    
    if two_qubit_gate is None:
        print("No two-qubit gate found!")
        return []
    
    print(f"Two-qubit gate type: {two_qubit_gate}")
    
    # Get all two-qubit gate data
    results = []
    skipped = 0
    
    gate_data = target[two_qubit_gate]
    
    for qubits, props in gate_data.items():
        if props is None or props.error is None:
            skipped += 1
            continue
        
        q1, q2 = qubits
        gate_error = props.error
        
        # Get Φ for each qubit
        phi1 = get_qubit_phi(backend, target, q1)
        phi2 = get_qubit_phi(backend, target, q2)
        
        if phi1 is None or phi2 is None:
            skipped += 1
            continue
        
        # Metrics for the pair
        avg_phi = (phi1 + phi2) / 2
        min_phi = min(phi1, phi2)
        
        results.append({
            'q1': q1,
            'q2': q2,
            'phi1': phi1,
            'phi2': phi2,
            'avg_phi': avg_phi,
            'min_phi': min_phi,
            'gate_error': gate_error,
            'backend': backend_name
        })
    
    print(f"Two-qubit gates analyzed: {len(results)} (skipped: {skipped})")
    
    if len(results) == 0:
        return []
    
    # Correlations
    avg_phis = np.array([r['avg_phi'] for r in results])
    min_phis = np.array([r['min_phi'] for r in results])
    gate_errors = np.array([r['gate_error'] for r in results])
    
    corr_avg = np.corrcoef(avg_phis, gate_errors)[0, 1]
    corr_min = np.corrcoef(min_phis, gate_errors)[0, 1]
    
    print(f"\nCorrelation with 2-qubit gate error:")
    print(f"  Average Φ of pair: r = {corr_avg:.4f}")
    print(f"  Minimum Φ of pair: r = {corr_min:.4f}")
    print(f"  (Negative = low Φ predicts high error = GOOD)")
    
    # Group comparison
    median_phi = np.median(avg_phis)
    low_phi_pairs = [r for r in results if r['avg_phi'] < median_phi]
    high_phi_pairs = [r for r in results if r['avg_phi'] >= median_phi]
    
    low_error = np.mean([r['gate_error'] for r in low_phi_pairs])
    high_error = np.mean([r['gate_error'] for r in high_phi_pairs])
    
    print(f"\nGroup comparison (median split):")
    print(f"  Low-Φ pairs:  mean gate error = {low_error:.4f} ({100*low_error:.2f}%)")
    print(f"  High-Φ pairs: mean gate error = {high_error:.4f} ({100*high_error:.2f}%)")
    print(f"  Ratio: Low-Φ pairs have {low_error/high_error:.2f}x higher error")
    
    # Worst and best pairs
    sorted_by_error = sorted(results, key=lambda x: x['gate_error'], reverse=True)
    
    print(f"\nWORST 5 GATES (highest error):")
    for r in sorted_by_error[:5]:
        print(f"  Q{r['q1']}-Q{r['q2']}: error={r['gate_error']:.4f}, avg_Φ={r['avg_phi']:.4f}, min_Φ={r['min_phi']:.4f}")
    
    print(f"\nBEST 5 GATES (lowest error):")
    for r in sorted_by_error[-5:]:
        print(f"  Q{r['q1']}-Q{r['q2']}: error={r['gate_error']:.4f}, avg_Φ={r['avg_phi']:.4f}, min_Φ={r['min_phi']:.4f}")
    
    return results


def main():
    print("="*70)
    print("Φ vs TWO-QUBIT GATE ERRORS - REAL IBM QUANTUM DATA")
    print("="*70)
    print("\nHypothesis: Low-Φ qubit pairs should have higher 2-qubit gate errors")
    print("NO SYNTHETIC DATA. Real calibration only.")
    
    service = QiskitRuntimeService()
    
    backends = ["ibm_fez", "ibm_torino", "ibm_marrakesh"]
    
    all_results = []
    
    for backend_name in backends:
        try:
            results = analyze_two_qubit_gates(service, backend_name)
            all_results.extend(results)
        except Exception as e:
            print(f"\nError with {backend_name}: {e}")
    
    # Aggregate analysis
    print(f"\n{'='*70}")
    print("AGGREGATE RESULTS (ALL BACKENDS)")
    print('='*70)
    print(f"Total two-qubit gates analyzed: {len(all_results)}")
    
    if len(all_results) > 0:
        avg_phis = np.array([r['avg_phi'] for r in all_results])
        min_phis = np.array([r['min_phi'] for r in all_results])
        gate_errors = np.array([r['gate_error'] for r in all_results])
        
        corr_avg = np.corrcoef(avg_phis, gate_errors)[0, 1]
        corr_min = np.corrcoef(min_phis, gate_errors)[0, 1]
        
        print(f"\nOVERALL CORRELATION:")
        print(f"  Average Φ vs gate error: r = {corr_avg:.4f}")
        print(f"  Minimum Φ vs gate error: r = {corr_min:.4f}")
        
        # Threshold analysis
        low_phi_gates = [r for r in all_results if r['min_phi'] < THRESHOLD]
        high_phi_gates = [r for r in all_results if r['min_phi'] >= THRESHOLD]
        
        print(f"\nTHRESHOLD ANALYSIS (Φ = 0.25):")
        print(f"  Gates where min_Φ < 0.25: {len(low_phi_gates)}")
        print(f"  Gates where min_Φ ≥ 0.25: {len(high_phi_gates)}")
        
        if len(low_phi_gates) > 0 and len(high_phi_gates) > 0:
            low_err = np.mean([r['gate_error'] for r in low_phi_gates])
            high_err = np.mean([r['gate_error'] for r in high_phi_gates])
            print(f"\n  Mean error (min_Φ < 0.25): {low_err:.4f} ({100*low_err:.2f}%)")
            print(f"  Mean error (min_Φ ≥ 0.25): {high_err:.4f} ({100*high_err:.2f}%)")
            print(f"  *** Low-Φ gates have {low_err/high_err:.2f}x higher error ***")
    
    print(f"\n{'='*70}")
    print("CONCLUSION")
    print('='*70)
    print("If correlation is negative: Φ PREDICTS two-qubit gate quality")
    print("This would mean the same formula works for:")
    print("  - Single qubit coherence (previous test)")
    print("  - Two-qubit gate errors (this test)")
    print("  - Bearings, turbofans, grids, neural networks")
    print('='*70)


if __name__ == "__main__":
    main()
