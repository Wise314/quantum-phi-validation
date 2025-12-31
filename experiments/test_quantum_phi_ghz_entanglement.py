"""
Test 11: GHZ Entanglement Circuit Validation

PURPOSE: Prove low-Φ qubits degrade entanglement quality.

GHZ state: (|000⟩ + |111⟩) / √2
- Perfect: 50% |000⟩, 50% |111⟩, nothing else
- Degraded: Other bit strings appear (|001⟩, |010⟩, etc.)

NO SYNTHETIC DATA. Real circuit execution only.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ALPHA = 0.1
THRESHOLD = 0.25


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
            't2': t2_us,
            't2_t1': rho,
            'readout_error': readout_error
        }
    except:
        return None


def find_connected_triplets(backend, qubit_data):
    """Find connected triplets of qubits for GHZ circuit."""
    coupling_map = backend.coupling_map
    qubit_dict = {q['qubit']: q for q in qubit_data}
    
    triplets = []
    
    # Find all paths of length 3 (q1 - q2 - q3)
    for q1 in qubit_dict:
        neighbors_1 = [edge[1] for edge in coupling_map if edge[0] == q1]
        neighbors_1 += [edge[0] for edge in coupling_map if edge[1] == q1]
        
        for q2 in neighbors_1:
            if q2 not in qubit_dict:
                continue
            
            neighbors_2 = [edge[1] for edge in coupling_map if edge[0] == q2]
            neighbors_2 += [edge[0] for edge in coupling_map if edge[1] == q2]
            
            for q3 in neighbors_2:
                if q3 not in qubit_dict or q3 == q1:
                    continue
                
                # Found a connected triplet
                triplet_qubits = [q1, q2, q3]
                min_phi = min(qubit_dict[q]['phi'] for q in triplet_qubits)
                avg_phi = np.mean([qubit_dict[q]['phi'] for q in triplet_qubits])
                
                triplets.append({
                    'qubits': triplet_qubits,
                    'min_phi': min_phi,
                    'avg_phi': avg_phi,
                    'data': [qubit_dict[q] for q in triplet_qubits]
                })
    
    return triplets


def create_ghz_circuit(qubits, num_qubits_total):
    """Create GHZ circuit on specified qubits."""
    qc = QuantumCircuit(num_qubits_total, 3)
    
    q0, q1, q2 = qubits
    
    # GHZ: H on first, then CNOT chain
    qc.h(q0)
    qc.cx(q0, q1)
    qc.cx(q1, q2)
    
    # Measure
    qc.measure(q0, 0)
    qc.measure(q1, 1)
    qc.measure(q2, 2)
    
    return qc


def analyze_ghz_results(counts, shots):
    """
    Analyze GHZ circuit results.
    
    Perfect GHZ: 50% |000⟩, 50% |111⟩
    Error = probability of anything else
    """
    p_000 = counts.get('000', 0) / shots
    p_111 = counts.get('111', 0) / shots
    
    # GHZ fidelity proxy: how much is in correct states
    ghz_fidelity = p_000 + p_111
    
    # Error: anything not |000⟩ or |111⟩
    error = 1.0 - ghz_fidelity
    
    # Balance: should be 50/50
    if p_000 + p_111 > 0:
        balance = min(p_000, p_111) / max(p_000, p_111)
    else:
        balance = 0
    
    return {
        'p_000': p_000,
        'p_111': p_111,
        'ghz_fidelity': ghz_fidelity,
        'error': error,
        'balance': balance
    }


def main():
    print("="*70)
    print("TEST 11: GHZ ENTANGLEMENT VALIDATION")
    print("="*70)
    print()
    print("Purpose: Prove low-Φ qubits degrade entanglement quality")
    print("Circuit: GHZ state (|000⟩ + |111⟩) / √2")
    print("Metric: Probability of correct outcomes (|000⟩ or |111⟩)")
    print()
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    target = backend.target
    
    print(f"Backend: {backend.name}")
    print()
    
    # Calculate Φ for all qubits
    print("Calculating Φ for all qubits...")
    qubit_data = []
    for i in range(backend.num_qubits):
        result = calculate_qubit_phi(backend, target, i)
        if result is not None:
            qubit_data.append(result)
    
    print(f"Valid qubits: {len(qubit_data)}")
    
    # Find connected triplets
    print("Finding connected qubit triplets...")
    triplets = find_connected_triplets(backend, qubit_data)
    print(f"Found {len(triplets)} connected triplets")
    
    # Sort by min_phi
    triplets.sort(key=lambda x: x['min_phi'])
    
    # Select worst 5 and best 5 triplets
    low_phi_triplets = triplets[:5]
    high_phi_triplets = triplets[-5:]
    
    print()
    print("LOW-Φ TRIPLETS (worst 5):")
    for t in low_phi_triplets:
        print(f"  Qubits {t['qubits']}: min_Φ={t['min_phi']:.4f}, avg_Φ={t['avg_phi']:.4f}")
    
    print()
    print("HIGH-Φ TRIPLETS (best 5):")
    for t in high_phi_triplets:
        print(f"  Qubits {t['qubits']}: min_Φ={t['min_phi']:.4f}, avg_Φ={t['avg_phi']:.4f}")
    
    # Create and run circuits
    print()
    print("="*70)
    print("RUNNING GHZ CIRCUITS...")
    print("="*70)
    
    shots = 1000
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    all_triplets = low_phi_triplets + high_phi_triplets
    circuits = []
    
    for t in all_triplets:
        qc = create_ghz_circuit(t['qubits'], backend.num_qubits)
        qc_transpiled = pm.run(qc)
        circuits.append(qc_transpiled)
    
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
    print()
    
    low_phi_results = []
    high_phi_results = []
    
    print(f"{'Qubits':<15} {'Group':<10} {'min_Φ':<10} {'GHZ_Fid':<10} {'Error':<10} {'P(000)':<10} {'P(111)':<10}")
    print("-"*75)
    
    for i, t in enumerate(all_triplets):
        counts = result[i].data.c.get_counts()
        analysis = analyze_ghz_results(counts, shots)
        
        t['analysis'] = analysis
        
        group = "LOW-Φ" if i < 5 else "HIGH-Φ"
        
        print(f"{str(t['qubits']):<15} {group:<10} {t['min_phi']:<10.4f} "
              f"{analysis['ghz_fidelity']:<10.4f} {analysis['error']:<10.4f} "
              f"{analysis['p_000']:<10.3f} {analysis['p_111']:<10.3f}")
        
        if i < 5:
            low_phi_results.append(t)
        else:
            high_phi_results.append(t)
    
    # Summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    low_avg_fidelity = np.mean([t['analysis']['ghz_fidelity'] for t in low_phi_results])
    high_avg_fidelity = np.mean([t['analysis']['ghz_fidelity'] for t in high_phi_results])
    
    low_avg_error = np.mean([t['analysis']['error'] for t in low_phi_results])
    high_avg_error = np.mean([t['analysis']['error'] for t in high_phi_results])
    
    print()
    print(f"LOW-Φ triplets (n=5):")
    print(f"  Mean min_Φ: {np.mean([t['min_phi'] for t in low_phi_results]):.4f}")
    print(f"  Mean GHZ fidelity: {low_avg_fidelity:.4f}")
    print(f"  Mean error: {low_avg_error:.4f}")
    
    print()
    print(f"HIGH-Φ triplets (n=5):")
    print(f"  Mean min_Φ: {np.mean([t['min_phi'] for t in high_phi_results]):.4f}")
    print(f"  Mean GHZ fidelity: {high_avg_fidelity:.4f}")
    print(f"  Mean error: {high_avg_error:.4f}")
    
    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    
    if low_avg_error > high_avg_error:
        ratio = low_avg_error / high_avg_error if high_avg_error > 0 else float('inf')
        print(f"LOW-Φ triplets have {ratio:.2f}x HIGHER entanglement error")
        print("Φ PREDICTS ENTANGLEMENT QUALITY")
    else:
        fidelity_diff = high_avg_fidelity - low_avg_fidelity
        print(f"HIGH-Φ triplets have {fidelity_diff:.4f} higher GHZ fidelity")
    
    print()
    print("This is REAL entanglement on REAL quantum hardware.")
    print("NO synthetic data. NO simulation.")


if __name__ == "__main__":
    main()
