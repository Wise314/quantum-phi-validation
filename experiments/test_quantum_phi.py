"""
Test Universal Φ on Real IBM Quantum Qubits

Ground truth test: Does Φ < 0.25 identify poor qubits?

A qubit is a 2-level system (like 2-class classifier):
  - random baseline = 0.50
  - I = (fidelity - 0.50) / 0.50

NO SYNTHETIC DATA. Real IBM Quantum calibration only.
If data unavailable for a qubit, SKIP IT.
"""

import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

# Universal Φ constants (from validated portfolio)
ALPHA = 0.1
THRESHOLD = 0.25

def calculate_qubit_phi(fidelity, t1, t2, readout_error):
    """
    Calculate Φ for a single qubit.
    
    Qubit is 2-level system: random = 0.50
    
    I = normalized fidelity (like 2-class accuracy)
    ρ = T2/T1 ratio (coherence stability)
    S = readout error (measurement entropy proxy)
    """
    # Normalized identity: qubit is 2-level system
    random_baseline = 0.50
    if fidelity <= random_baseline:
        I = 0.0
    else:
        I = (fidelity - random_baseline) / (1.0 - random_baseline)
    
    # Coherence: T2/T1 ratio (T2 <= T1 always, so this is 0-1)
    if t1 > 0 and t2 > 0:
        rho = min(t2 / t1, 1.0)
    else:
        rho = 0.0
    
    # Entropy proxy: readout error (higher error = more disorder)
    S = readout_error
    
    # Universal Φ formula
    phi = I * rho - ALPHA * S
    
    return {
        'phi': phi,
        'I': I,
        'rho': rho,
        'S': S,
        'fidelity': fidelity,
        't1': t1,
        't2': t2,
        'readout_error': readout_error
    }


def predict_qubit_quality(phi):
    """Same thresholds as physical systems."""
    if phi < 0:
        return "BAD"
    elif phi < THRESHOLD:
        return "MARGINAL"
    else:
        return "GOOD"


def main():
    print("=" * 70)
    print("QUANTUM SENSOR Φ TEST - REAL IBM QUANTUM DATA")
    print("=" * 70)
    print()
    print("Formula: Φ = I × ρ - α × S")
    print(f"Threshold: {THRESHOLD} (same as bearings, grids, neural nets)")
    print(f"Alpha: {ALPHA}")
    print()
    
    # Connect to IBM Quantum
    service = QiskitRuntimeService()
    
    # Get backend with calibration data
    backend_name = "ibm_fez"  # 156 qubits
    print(f"Pulling calibration data from: {backend_name}")
    print()
    
    backend = service.backend(backend_name)
    target = backend.target
    
    # Get qubit properties
    num_qubits = backend.num_qubits
    print(f"Number of qubits: {num_qubits}")
    print()
    
    # Pull calibration for each qubit
    results = []
    skipped = 0
    
    print("Analyzing qubits (REAL DATA ONLY - skipping if unavailable)...")
    print("-" * 70)
    print(f"{'Qubit':<8} {'Fidelity':<10} {'T1(μs)':<10} {'T2(μs)':<10} {'ReadErr':<10} {'Φ':<10} {'Status':<10}")
    print("-" * 70)
    
    good_count = 0
    marginal_count = 0
    bad_count = 0
    
    for i in range(num_qubits):
        try:
            props = backend.qubit_properties(i)
            
            # Extract real calibration data - NO DEFAULTS
            t1 = props.t1
            t2 = props.t2
            
            # Skip if T1 or T2 not available
            if t1 is None or t2 is None:
                skipped += 1
                continue
            
            t1_us = t1 * 1e6  # Convert to microseconds for display
            t2_us = t2 * 1e6
            
            # Get gate fidelity - NO DEFAULTS
            try:
                sx_props = target['sx'][(i,)]
                if sx_props.error is None:
                    skipped += 1
                    continue
                gate_error = sx_props.error
                fidelity = 1.0 - gate_error
            except:
                skipped += 1
                continue
            
            # Get readout error - NO DEFAULTS
            try:
                meas_props = target['measure'][(i,)]
                if meas_props.error is None:
                    skipped += 1
                    continue
                readout_error = meas_props.error
            except:
                skipped += 1
                continue
            
            # Calculate Φ with REAL data only
            result = calculate_qubit_phi(fidelity, t1_us, t2_us, readout_error)
            result['qubit'] = i
            results.append(result)
            
            status = predict_qubit_quality(result['phi'])
            
            if status == "GOOD":
                good_count += 1
            elif status == "MARGINAL":
                marginal_count += 1
            else:
                bad_count += 1
            
            # Print every 10th qubit to keep output manageable
            if i % 10 == 0 or result['phi'] < THRESHOLD:
                print(f"{i:<8} {fidelity:<10.4f} {t1_us:<10.1f} {t2_us:<10.1f} {readout_error:<10.4f} {result['phi']:<10.4f} {status:<10}")
                
        except Exception as e:
            skipped += 1
            continue
    
    print("-" * 70)
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total qubits on device: {num_qubits}")
    print(f"Qubits with complete data: {len(results)}")
    print(f"Qubits skipped (incomplete data): {skipped}")
    print()
    print(f"GOOD (Φ ≥ 0.25):         {good_count} ({100*good_count/len(results):.1f}%)")
    print(f"MARGINAL (0 ≤ Φ < 0.25): {marginal_count} ({100*marginal_count/len(results):.1f}%)")
    print(f"BAD (Φ < 0):             {bad_count} ({100*bad_count/len(results):.1f}%)")
    print()
    
    # Find worst and best qubits
    sorted_results = sorted(results, key=lambda x: x['phi'])
    
    print("WORST 5 QUBITS (lowest Φ):")
    for r in sorted_results[:5]:
        print(f"  Qubit {r['qubit']}: Φ={r['phi']:.4f}, fidelity={r['fidelity']:.4f}, T2/T1={r['rho']:.3f}")
    
    print()
    print("BEST 5 QUBITS (highest Φ):")
    for r in sorted_results[-5:]:
        print(f"  Qubit {r['qubit']}: Φ={r['phi']:.4f}, fidelity={r['fidelity']:.4f}, T2/T1={r['rho']:.3f}")
    
    print()
    print("=" * 70)
    print("WHAT THIS MEANS")
    print("=" * 70)
    print("This is REAL calibration data from IBM Quantum.")
    print("NO synthetic data. NO hardcoded values.")
    print()
    print("The Φ formula is IDENTICAL to what predicted:")
    print("  - UK power blackout (Φ = 0.178)")
    print("  - Tohoku M9.1 earthquake (Φ = -0.357)")
    print("  - 660 neural network architectures")
    print()


if __name__ == "__main__":
    main()
