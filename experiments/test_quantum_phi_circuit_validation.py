"""
Test 4: Circuit Execution Validation

PURPOSE: Prove low-Φ qubits cause actual circuit failures.

METHOD:
1. Calculate Φ for all qubits
2. Select high-Φ qubits (best 5) and low-Φ qubits (worst 5 that aren't dead)
3. Run identical circuits on both groups
4. Compare success rates

NO SYNTHETIC DATA. Real circuit execution on real quantum hardware.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ALPHA = 0.1
THRESHOLD = 0.25


def calculate_qubit_phi(backend, target, qubit_idx):
    """Calculate Φ for a single qubit. Returns None if data unavailable."""
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
        
        # Skip dead qubits
        if fidelity < 0.5:
            return None
        
        random_baseline = 0.50
        I = (fidelity - random_baseline) / (1.0 - random_baseline)
        rho = min(t2_us / t1_us, 1.0) if t1_us > 0 else 0
        S = readout_error
        
        phi = I * rho - ALPHA * S
        
        return {
            'qubit': qubit_idx,
            'phi': phi,
            'fidelity': fidelity,
            't2_t1': rho,
            'readout_error': readout_error
        }
    except:
        return None


def analyze_superposition_results(counts, shots):
    """
    Analyze Hadamard test results.
    Perfect qubit: 50% '0', 50% '1'
    
    Returns: deviation from ideal (0 = perfect, 1 = completely wrong)
    """
    p0 = counts.get('0', 0) / shots
    p1 = counts.get('1', 0) / shots
    
    # Ideal is 0.5/0.5
    deviation = abs(p0 - 0.5) + abs(p1 - 0.5)
    
    return {
        'p0': p0,
        'p1': p1,
        'deviation': deviation,
        'success_rate': 1.0 - deviation
    }


def main():
    print("="*70)
    print("TEST 4: CIRCUIT EXECUTION VALIDATION")
    print("="*70)
    print()
    print("Purpose: Prove low-Φ qubits cause actual circuit failures")
    print("Method: Run identical circuits on high-Φ vs low-Φ qubits")
    print()
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    target = backend.target
    
    print(f"Backend: {backend.name}")
    print(f"Status: {backend.status()}")
    print()
    
    # Calculate Φ for all qubits
    print("Calculating Φ for all qubits...")
    qubit_data = []
    for i in range(backend.num_qubits):
        result = calculate_qubit_phi(backend, target, i)
        if result is not None:
            qubit_data.append(result)
    
    # Sort by Φ
    qubit_data.sort(key=lambda x: x['phi'])
    
    # Select worst 5 (lowest Φ, but not dead) and best 5 (highest Φ)
    low_phi_qubits = qubit_data[:5]
    high_phi_qubits = qubit_data[-5:]
    
    print()
    print("LOW-Φ QUBITS (worst 5):")
    for q in low_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, fidelity={q['fidelity']:.4f}")
    
    print()
    print("HIGH-Φ QUBITS (best 5):")
    for q in high_phi_qubits:
        print(f"  Q{q['qubit']}: Φ={q['phi']:.4f}, fidelity={q['fidelity']:.4f}")
    
    # Create circuits for each qubit
    print()
    print("="*70)
    print("RUNNING CIRCUITS (this may take a few minutes)...")
    print("="*70)
    
    shots = 1000
    
    # Prepare circuits for all test qubits
    all_test_qubits = low_phi_qubits + high_phi_qubits
    circuits = []
    qubit_map = []
    
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    for q_data in all_test_qubits:
        qc = QuantumCircuit(backend.num_qubits, 1)
        qc.h(q_data['qubit'])
        qc.measure(q_data['qubit'], 0)
        
        qc_transpiled = pm.run(qc)
        circuits.append(qc_transpiled)
        qubit_map.append(q_data)
    
    # Run all circuits
    print(f"Submitting {len(circuits)} circuits with {shots} shots each...")
    
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=shots)
    
    print(f"Job ID: {job.job_id()}")
    print("Waiting for results...")
    
    result = job.result()
    
    # Analyze results
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    
    low_phi_results = []
    high_phi_results = []
    
    for i, q_data in enumerate(qubit_map):
        counts = result[i].data.c.get_counts()
        analysis = analyze_superposition_results(counts, shots)
        
        result_data = q_data.copy()
        result_data['counts'] = counts
        result_data['deviation'] = analysis['deviation']
        result_data['success_rate'] = analysis['success_rate']
        
        if i < 5:
            low_phi_results.append(result_data)
            phi_group = "LOW-Φ"
        else:
            high_phi_results.append(result_data)
            phi_group = "HIGH-Φ"
        
        print(f"Q{q_data['qubit']} ({phi_group}): Φ={q_data['phi']:.4f}, "
              f"deviation={analysis['deviation']:.4f}, "
              f"counts={counts}")
    
    # Summary comparison
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    low_avg_deviation = np.mean([r['deviation'] for r in low_phi_results])
    high_avg_deviation = np.mean([r['deviation'] for r in high_phi_results])
    
    low_avg_success = np.mean([r['success_rate'] for r in low_phi_results])
    high_avg_success = np.mean([r['success_rate'] for r in high_phi_results])
    
    print(f"LOW-Φ qubits (n={len(low_phi_results)}):")
    print(f"  Mean Φ: {np.mean([r['phi'] for r in low_phi_results]):.4f}")
    print(f"  Mean deviation from ideal: {low_avg_deviation:.4f}")
    print(f"  Mean success rate: {low_avg_success:.4f}")
    
    print()
    print(f"HIGH-Φ qubits (n={len(high_phi_results)}):")
    print(f"  Mean Φ: {np.mean([r['phi'] for r in high_phi_results]):.4f}")
    print(f"  Mean deviation from ideal: {high_avg_deviation:.4f}")
    print(f"  Mean success rate: {high_avg_success:.4f}")
    
    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    
    if low_avg_deviation > high_avg_deviation:
        ratio = low_avg_deviation / high_avg_deviation if high_avg_deviation > 0 else float('inf')
        print(f"LOW-Φ qubits have {ratio:.2f}x HIGHER deviation (WORSE)")
        print("Φ PREDICTS CIRCUIT EXECUTION QUALITY")
    else:
        print("Results inconclusive or opposite to prediction")
    
    print()
    print("This is REAL circuit execution on REAL quantum hardware.")
    print("NO synthetic data. NO simulation.")


if __name__ == "__main__":
    main()
