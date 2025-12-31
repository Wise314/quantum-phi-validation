"""
Test 10: Threshold Sensitivity Analysis

PURPOSE: Prove 0.25 is the optimal threshold for quantum systems.

METHOD:
1. Sweep threshold from 0.05 to 0.50
2. At each threshold, measure discrimination power
3. Find threshold that maximizes separation

If 0.25 is optimal, this validates the triality relation derivation.
"""

import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA = 0.1


def calculate_qubit_phi(backend, target, qubit_idx):
    """Calculate Φ for a single qubit."""
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
        
        random_baseline = 0.50
        if fidelity <= random_baseline:
            I = 0.0
        else:
            I = (fidelity - random_baseline) / (1.0 - random_baseline)
        
        rho = min(t2_us / t1_us, 1.0) if t1_us > 0 else 0
        S = readout_error
        
        phi = I * rho - ALPHA * S
        
        return {
            'qubit': qubit_idx,
            'phi': phi,
            'fidelity': fidelity,
            't2': t2_us,
            't2_t1': rho,
            'readout_error': readout_error,
            'gate_error': sx_props.error
        }
    except:
        return None


def evaluate_threshold(qubit_data, threshold):
    """
    Evaluate how well a threshold separates good from bad qubits.
    
    Returns discrimination metrics.
    """
    below = [q for q in qubit_data if q['phi'] < threshold]
    above = [q for q in qubit_data if q['phi'] >= threshold]
    
    if len(below) == 0 or len(above) == 0:
        return None
    
    # Compare T2 (coherence time) - primary quality metric
    below_t2 = np.mean([q['t2'] for q in below])
    above_t2 = np.mean([q['t2'] for q in above])
    t2_ratio = above_t2 / below_t2 if below_t2 > 0 else 0
    
    # Compare gate error
    below_gate_err = np.mean([q['gate_error'] for q in below])
    above_gate_err = np.mean([q['gate_error'] for q in above])
    gate_ratio = below_gate_err / above_gate_err if above_gate_err > 0 else 0
    
    # Compare readout error
    below_read_err = np.mean([q['readout_error'] for q in below])
    above_read_err = np.mean([q['readout_error'] for q in above])
    read_ratio = below_read_err / above_read_err if above_read_err > 0 else 0
    
    # Combined discrimination score
    # Higher is better - means threshold separates good from bad
    discrimination = t2_ratio * gate_ratio * read_ratio
    
    return {
        'threshold': threshold,
        'n_below': len(below),
        'n_above': len(above),
        'below_t2': below_t2,
        'above_t2': above_t2,
        't2_ratio': t2_ratio,
        'below_gate_err': below_gate_err,
        'above_gate_err': above_gate_err,
        'gate_ratio': gate_ratio,
        'below_read_err': below_read_err,
        'above_read_err': above_read_err,
        'read_ratio': read_ratio,
        'discrimination': discrimination
    }


def main():
    print("="*70)
    print("TEST 10: THRESHOLD SENSITIVITY ANALYSIS")
    print("="*70)
    print()
    print("Purpose: Find optimal threshold for quantum systems")
    print("Method: Sweep threshold, measure discrimination power")
    print("Prediction: 0.25 should be optimal (from triality relation)")
    print()
    
    service = QiskitRuntimeService()
    
    # Get data from all backends
    backends = ["ibm_fez", "ibm_torino", "ibm_marrakesh"]
    all_qubits = []
    
    for backend_name in backends:
        print(f"Loading {backend_name}...")
        backend = service.backend(backend_name)
        target = backend.target
        
        for i in range(backend.num_qubits):
            result = calculate_qubit_phi(backend, target, i)
            if result is not None:
                result['backend'] = backend_name
                all_qubits.append(result)
    
    print(f"\nTotal qubits: {len(all_qubits)}")
    
    # Sweep thresholds
    thresholds = np.arange(0.05, 0.55, 0.05)
    
    print()
    print("="*70)
    print("THRESHOLD SWEEP")
    print("="*70)
    print()
    print(f"{'Thresh':<8} {'n_low':<8} {'n_high':<8} {'T2_ratio':<10} {'Gate_ratio':<12} {'Read_ratio':<12} {'Score':<10}")
    print("-"*78)
    
    results = []
    
    for thresh in thresholds:
        eval_result = evaluate_threshold(all_qubits, thresh)
        if eval_result:
            results.append(eval_result)
            print(f"{thresh:<8.2f} {eval_result['n_below']:<8} {eval_result['n_above']:<8} "
                  f"{eval_result['t2_ratio']:<10.2f} {eval_result['gate_ratio']:<12.2f} "
                  f"{eval_result['read_ratio']:<12.2f} {eval_result['discrimination']:<10.2f}")
    
    # Find optimal threshold
    best = max(results, key=lambda x: x['t2_ratio'])
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    print(f"OPTIMAL THRESHOLD (max T2 separation): {best['threshold']:.2f}")
    print()
    print(f"At threshold = {best['threshold']:.2f}:")
    print(f"  Qubits below: {best['n_below']} (mean T2 = {best['below_t2']:.1f} μs)")
    print(f"  Qubits above: {best['n_above']} (mean T2 = {best['above_t2']:.1f} μs)")
    print(f"  T2 ratio: {best['t2_ratio']:.2f}x")
    
    print()
    print("="*70)
    print("COMPARISON WITH THEORETICAL PREDICTION")
    print("="*70)
    
    # Evaluate specifically at 0.25
    eval_025 = evaluate_threshold(all_qubits, 0.25)
    
    print()
    print(f"At threshold = 0.25 (theoretical from triality):")
    print(f"  Qubits below: {eval_025['n_below']} (mean T2 = {eval_025['below_t2']:.1f} μs)")
    print(f"  Qubits above: {eval_025['n_above']} (mean T2 = {eval_025['above_t2']:.1f} μs)")
    print(f"  T2 ratio: {eval_025['t2_ratio']:.2f}x")
    
    print()
    if abs(best['threshold'] - 0.25) <= 0.10:
        print("*** OPTIMAL THRESHOLD IS NEAR 0.25 - VALIDATES TRIALITY DERIVATION ***")
    else:
        print(f"Optimal threshold ({best['threshold']:.2f}) differs from 0.25")
        print("May indicate quantum-specific adjustment needed")
    
    print()
    print("="*70)
    print("T2 RATIO BY THRESHOLD")
    print("="*70)
    print()
    for r in results:
        bar = "*" * int(r['t2_ratio'] * 5)
        marker = " <-- 0.25" if abs(r['threshold'] - 0.25) < 0.01 else ""
        print(f"{r['threshold']:.2f}: {r['t2_ratio']:5.2f}x {bar}{marker}")


if __name__ == "__main__":
    main()
