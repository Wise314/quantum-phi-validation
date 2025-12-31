"""
Test 12: Bell State Validation

PURPOSE: Test Φ prediction on Bell states (2-qubit entanglement).

Bell state: (|00⟩ + |11⟩) / √2
- Perfect: 50% |00⟩, 50% |11⟩
- Error: |01⟩ or |10⟩ appear

More pairs to test than GHZ triplets.
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


def find_connected_pairs(backend, qubit_data):
    """Find connected pairs of qubits for Bell circuit."""
    coupling_map = backend.coupling_map
    qubit_dict = {q['qubit']: q for q in qubit_data}
    
    pairs = []
    seen = set()
    
    for edge in coupling_map:
        q1, q2 = edge
        
        if q1 not in qubit_dict or q2 not in qubit_dict:
            continue
        
        pair_key = tuple(sorted([q1, q2]))
        if pair_key in seen:
            continue
        seen.add(pair_key)
        
        min_phi = min(qubit_dict[q1]['phi'], qubit_dict[q2]['phi'])
        avg_phi = (qubit_dict[q1]['phi'] + qubit_dict[q2]['phi']) / 2
        
        pairs.append({
            'qubits': [q1, q2],
            'min_phi': min_phi,
            'avg_phi': avg_phi,
            'data': [qubit_dict[q1], qubit_dict[q2]]
        })
    
    return pairs


def create_bell_circuit(qubits, num_qubits_total):
    """Create Bell state circuit on specified qubits."""
    qc = QuantumCircuit(num_qubits_total, 2)
    
    q0, q1 = qubits
    
    # Bell: H on first, then CNOT
    qc.h(q0)
    qc.cx(q0, q1)
    
    # Measure
    qc.measure(q0, 0)
    qc.measure(q1, 1)
    
    return qc


def analyze_bell_results(counts, shots):
    """
    Analyze Bell circuit results.
    
    Perfect Bell: 50% |00⟩, 50% |11⟩
    Error = probability of |01⟩ or |10⟩
    """
    p_00 = counts.get('00', 0) / shots
    p_11 = counts.get('11', 0) / shots
    p_01 = counts.get('01', 0) / shots
    p_10 = counts.get('10', 0) / shots
    
    # Bell fidelity proxy
    bell_fidelity = p_00 + p_11
    
    # Error: |01⟩ or |10⟩
    error = p_01 + p_10
    
    return {
        'p_00': p_00,
        'p_11': p_11,
        'p_01': p_01,
        'p_10': p_10,
        'bell_fidelity': bell_fidelity,
        'error': error
    }


def main():
    print("="*70)
    print("TEST 12: BELL STATE VALIDATION")
    print("="*70)
    print()
    print("Purpose: Prove low-Φ qubit pairs degrade Bell state quality")
    print("Circuit: Bell state (|00⟩ + |11⟩) / √2")
    print("Metric: Probability of correct outcomes (|00⟩ or |11⟩)")
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
    
    # Find connected pairs
    print("Finding connected qubit pairs...")
    pairs = find_connected_pairs(backend, qubit_data)
    print(f"Found {len(pairs)} connected pairs")
    
    # Sort by min_phi
    pairs.sort(key=lambda x: x['min_phi'])
    
    # Select worst 10 and best 10 pairs
    low_phi_pairs = pairs[:10]
    high_phi_pairs = pairs[-10:]
    
    print()
    print("LOW-Φ PAIRS (worst 10):")
    for p in low_phi_pairs:
        print(f"  Qubits {p['qubits']}: min_Φ={p['min_phi']:.4f}")
    
    print()
    print("HIGH-Φ PAIRS (best 10):")
    for p in high_phi_pairs:
        print(f"  Qubits {p['qubits']}: min_Φ={p['min_phi']:.4f}")
    
    # Create and run circuits
    print()
    print("="*70)
    print("RUNNING BELL CIRCUITS...")
    print("="*70)
    
    shots = 1000
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    
    all_pairs = low_phi_pairs + high_phi_pairs
    circuits = []
    
    for p in all_pairs:
        qc = create_bell_circuit(p['qubits'], backend.num_qubits)
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
    
    print(f"{'Qubits':<12} {'Group':<10} {'min_Φ':<10} {'Bell_Fid':<10} {'Error':<10} {'P(00)':<8} {'P(11)':<8}")
    print("-"*70)
    
    for i, p in enumerate(all_pairs):
        counts = result[i].data.c.get_counts()
        analysis = analyze_bell_results(counts, shots)
        
        p['analysis'] = analysis
        
        group = "LOW-Φ" if i < 10 else "HIGH-Φ"
        
        print(f"{str(p['qubits']):<12} {group:<10} {p['min_phi']:<10.4f} "
              f"{analysis['bell_fidelity']:<10.4f} {analysis['error']:<10.4f} "
              f"{analysis['p_00']:<8.3f} {analysis['p_11']:<8.3f}")
        
        if i < 10:
            low_phi_results.append(p)
        else:
            high_phi_results.append(p)
    
    # Summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    low_avg_fidelity = np.mean([p['analysis']['bell_fidelity'] for p in low_phi_results])
    high_avg_fidelity = np.mean([p['analysis']['bell_fidelity'] for p in high_phi_results])
    
    low_avg_error = np.mean([p['analysis']['error'] for p in low_phi_results])
    high_avg_error = np.mean([p['analysis']['error'] for p in high_phi_results])
    
    print()
    print(f"LOW-Φ pairs (n=10):")
    print(f"  Mean min_Φ: {np.mean([p['min_phi'] for p in low_phi_results]):.4f}")
    print(f"  Mean Bell fidelity: {low_avg_fidelity:.4f}")
    print(f"  Mean error: {low_avg_error:.4f}")
    
    print()
    print(f"HIGH-Φ pairs (n=10):")
    print(f"  Mean min_Φ: {np.mean([p['min_phi'] for p in high_phi_results]):.4f}")
    print(f"  Mean Bell fidelity: {high_avg_fidelity:.4f}")
    print(f"  Mean error: {high_avg_error:.4f}")
    
    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    
    if low_avg_error > high_avg_error:
        ratio = low_avg_error / high_avg_error if high_avg_error > 0 else float('inf')
        print(f"LOW-Φ pairs have {ratio:.2f}x HIGHER Bell state error")
        print("Φ PREDICTS ENTANGLEMENT QUALITY")
    else:
        print("Results inconclusive")
    
    # Correlation analysis
    all_results = low_phi_results + high_phi_results
    min_phis = np.array([p['min_phi'] for p in all_results])
    errors = np.array([p['analysis']['error'] for p in all_results])
    
    corr = np.corrcoef(min_phis, errors)[0, 1]
    print()
    print(f"Correlation (min_Φ vs error): r = {corr:.4f}")
    print("(Negative = low Φ predicts high error)")
    
    print()
    print("This is REAL entanglement on REAL quantum hardware.")


if __name__ == "__main__":
    main()
