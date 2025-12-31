"""
TEMPORAL DATA COLLECTION

PURPOSE: Collect daily Φ snapshots to prove PREDICTION (not just correlation).

Run this DAILY for 2-4 weeks. Then analyze:
- Which qubits degraded?
- Did Φ predict it BEFORE it happened?

This is the CRITICAL test that separates "interesting" from "game-changing."
"""

from datetime import datetime
import json
import os
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA = 0.1
OUTPUT_DIR = os.path.expanduser("~/Desktop/quantum-phi-validation/temporal_data")


def collect_phi_data():
    print("="*60)
    print("DAILY Φ DATA COLLECTION")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    service = QiskitRuntimeService()
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'backends': {}
    }
    
    backends = ['ibm_fez', 'ibm_torino', 'ibm_marrakesh']
    
    for backend_name in backends:
        print(f"\nCollecting from {backend_name}...")
        
        try:
            backend = service.backend(backend_name)
            target = backend.target
        except Exception as e:
            print(f"  ERROR: Could not connect to {backend_name}: {e}")
            continue
        
        qubits = []
        valid = 0
        skipped = 0
        
        for i in range(backend.num_qubits):
            try:
                props = backend.qubit_properties(i)
                t1, t2 = props.t1, props.t2
                
                if t1 is None or t2 is None:
                    skipped += 1
                    continue
                
                sx_props = target['sx'][(i,)]
                meas_props = target['measure'][(i,)]
                
                if sx_props.error is None or meas_props.error is None:
                    skipped += 1
                    continue
                
                fidelity = 1.0 - sx_props.error
                readout_error = meas_props.error
                
                # Calculate Φ
                if fidelity > 0.5:
                    I = (fidelity - 0.50) / 0.50
                else:
                    I = 0
                
                rho = min(t2 / t1, 1.0) if t1 > 0 else 0
                phi = I * rho - ALPHA * readout_error
                
                # Classify
                if phi >= 0.25:
                    status = "GOOD"
                elif phi >= 0:
                    status = "MARGINAL"
                else:
                    status = "BAD"
                
                qubits.append({
                    'qubit': i,
                    'phi': round(phi, 6),
                    't1_us': round(t1 * 1e6, 2),
                    't2_us': round(t2 * 1e6, 2),
                    't2_t1': round(t2/t1, 4) if t1 > 0 else 0,
                    'fidelity': round(fidelity, 6),
                    'readout_error': round(readout_error, 6),
                    'status': status
                })
                valid += 1
                
            except Exception as e:
                skipped += 1
                continue
        
        data['backends'][backend_name] = {
            'num_qubits': backend.num_qubits,
            'valid_qubits': valid,
            'skipped_qubits': skipped,
            'qubits': qubits
        }
        
        # Summary stats
        if qubits:
            phis = [q['phi'] for q in qubits]
            good = sum(1 for q in qubits if q['status'] == 'GOOD')
            marginal = sum(1 for q in qubits if q['status'] == 'MARGINAL')
            bad = sum(1 for q in qubits if q['status'] == 'BAD')
            
            print(f"  Valid: {valid}, Skipped: {skipped}")
            print(f"  Φ range: {min(phis):.4f} to {max(phis):.4f}")
            print(f"  GOOD: {good}, MARGINAL: {marginal}, BAD: {bad}")
    
    # Save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"phi_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Saved to {filepath}")
    
    # Also save a "latest" copy for easy access
    latest_path = os.path.join(OUTPUT_DIR, "latest.json")
    with open(latest_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Updated {latest_path}")
    
    # Count total
    total_qubits = sum(d['valid_qubits'] for d in data['backends'].values())
    print(f"\nTotal qubits collected: {total_qubits}")
    print("\nRun this script daily to build temporal dataset.")
    print("After 2-4 weeks, run temporal analysis to prove prediction.")
    
    return filepath


if __name__ == "__main__":
    collect_phi_data()
