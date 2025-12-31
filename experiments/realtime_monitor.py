"""
REAL-TIME Φ MONITORING DEMO

PURPOSE: Proof-of-concept monitoring system.
Shows live qubit health across all backends.

Features:
- Color-coded status (GOOD/MARGINAL/BAD)
- Alerts for qubits crossing threshold
- Comparison to previous snapshot
- Summary statistics
"""

import json
import os
from datetime import datetime
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA = 0.1
THRESHOLD = 0.25
DATA_DIR = os.path.expanduser("~/Desktop/quantum-phi-validation/temporal_data")


def load_previous_snapshot():
    """Load the most recent previous snapshot for comparison."""
    latest_path = os.path.join(DATA_DIR, "latest.json")
    if os.path.exists(latest_path):
        with open(latest_path, 'r') as f:
            return json.load(f)
    return None


def calculate_phi(fidelity, t1, t2, readout_error):
    """Calculate Φ for a qubit."""
    if fidelity > 0.5:
        I = (fidelity - 0.50) / 0.50
    else:
        I = 0
    
    rho = min(t2 / t1, 1.0) if t1 > 0 else 0
    phi = I * rho - ALPHA * readout_error
    return phi


def get_status(phi):
    """Get status string for Φ value."""
    if phi >= THRESHOLD:
        return "GOOD"
    elif phi >= 0:
        return "MARGINAL"
    else:
        return "BAD"


def color_status(status):
    """Add ANSI color to status."""
    colors = {
        "GOOD": "\033[92m",      # Green
        "MARGINAL": "\033[93m",  # Yellow
        "BAD": "\033[91m",       # Red
        "RESET": "\033[0m"
    }
    return f"{colors.get(status, '')}{status}{colors['RESET']}"


def monitor():
    print()
    print("="*70)
    print("         REAL-TIME Φ MONITORING SYSTEM")
    print("="*70)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Threshold: Φ_c = {THRESHOLD}")
    print("="*70)
    
    # Load previous for comparison
    previous = load_previous_snapshot()
    prev_qubits = {}
    if previous:
        print(f"  Previous snapshot: {previous.get('date', 'unknown')}")
        for backend_name, backend_data in previous.get('backends', {}).items():
            for q in backend_data.get('qubits', []):
                key = (backend_name, q['qubit'])
                prev_qubits[key] = q
    else:
        print("  Previous snapshot: None (first run)")
    
    print("="*70)
    
    service = QiskitRuntimeService()
    backends = ['ibm_fez', 'ibm_torino', 'ibm_marrakesh']
    
    all_alerts = []
    total_stats = {'GOOD': 0, 'MARGINAL': 0, 'BAD': 0}
    
    for backend_name in backends:
        print(f"\n{'─'*70}")
        print(f"  BACKEND: {backend_name.upper()}")
        print(f"{'─'*70}")
        
        try:
            backend = service.backend(backend_name)
            target = backend.target
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        
        stats = {'GOOD': 0, 'MARGINAL': 0, 'BAD': 0}
        alerts = []
        worst_qubits = []
        
        for i in range(backend.num_qubits):
            try:
                props = backend.qubit_properties(i)
                t1, t2 = props.t1, props.t2
                
                if t1 is None or t2 is None:
                    continue
                
                sx_props = target['sx'][(i,)]
                meas_props = target['measure'][(i,)]
                
                if sx_props.error is None or meas_props.error is None:
                    continue
                
                fidelity = 1.0 - sx_props.error
                readout_error = meas_props.error
                
                phi = calculate_phi(fidelity, t1, t2, readout_error)
                status = get_status(phi)
                stats[status] += 1
                total_stats[status] += 1
                
                # Track worst qubits
                worst_qubits.append({
                    'qubit': i,
                    'phi': phi,
                    'status': status,
                    't2_us': t2 * 1e6
                })
                
                # Check for threshold crossing
                key = (backend_name, i)
                if key in prev_qubits:
                    prev_phi = prev_qubits[key]['phi']
                    prev_status = prev_qubits[key]['status']
                    
                    # Alert: crossed below threshold
                    if prev_status == "GOOD" and status in ["MARGINAL", "BAD"]:
                        alerts.append({
                            'qubit': i,
                            'prev_phi': prev_phi,
                            'curr_phi': phi,
                            'change': 'DEGRADED',
                            'message': f"Q{i}: {prev_phi:.4f} → {phi:.4f} (DEGRADED)"
                        })
                    
                    # Alert: crossed to BAD
                    if prev_status != "BAD" and status == "BAD":
                        alerts.append({
                            'qubit': i,
                            'prev_phi': prev_phi,
                            'curr_phi': phi,
                            'change': 'CRITICAL',
                            'message': f"Q{i}: {prev_phi:.4f} → {phi:.4f} (CRITICAL)"
                        })
                    
                    # Alert: recovered
                    if prev_status in ["MARGINAL", "BAD"] and status == "GOOD":
                        alerts.append({
                            'qubit': i,
                            'prev_phi': prev_phi,
                            'curr_phi': phi,
                            'change': 'RECOVERED',
                            'message': f"Q{i}: {prev_phi:.4f} → {phi:.4f} (RECOVERED)"
                        })
                
            except:
                continue
        
        # Summary
        total = stats['GOOD'] + stats['MARGINAL'] + stats['BAD']
        print(f"\n  Status Summary:")
        print(f"    {color_status('GOOD')}: {stats['GOOD']:3d} ({100*stats['GOOD']/total:.1f}%)")
        print(f"    {color_status('MARGINAL')}: {stats['MARGINAL']:3d} ({100*stats['MARGINAL']/total:.1f}%)")
        print(f"    {color_status('BAD')}: {stats['BAD']:3d} ({100*stats['BAD']/total:.1f}%)")
        
        # Worst qubits
        worst_qubits.sort(key=lambda x: x['phi'])
        print(f"\n  Worst 5 Qubits:")
        for q in worst_qubits[:5]:
            status_str = color_status(q['status'])
            print(f"    Q{q['qubit']:3d}: Φ={q['phi']:7.4f}  T2={q['t2_us']:6.1f}μs  [{status_str}]")
        
        # Alerts
        if alerts:
            print(f"\n  ⚠️  ALERTS ({len(alerts)}):")
            for alert in alerts:
                if alert['change'] == 'CRITICAL':
                    print(f"    🔴 {alert['message']}")
                elif alert['change'] == 'DEGRADED':
                    print(f"    🟡 {alert['message']}")
                elif alert['change'] == 'RECOVERED':
                    print(f"    🟢 {alert['message']}")
            all_alerts.extend(alerts)
        else:
            print(f"\n  ✓ No threshold crossings detected")
    
    # Overall summary
    print()
    print("="*70)
    print("  OVERALL SYSTEM STATUS")
    print("="*70)
    
    total = total_stats['GOOD'] + total_stats['MARGINAL'] + total_stats['BAD']
    print(f"\n  Total Qubits Monitored: {total}")
    print(f"    {color_status('GOOD')}: {total_stats['GOOD']:3d} ({100*total_stats['GOOD']/total:.1f}%)")
    print(f"    {color_status('MARGINAL')}: {total_stats['MARGINAL']:3d} ({100*total_stats['MARGINAL']/total:.1f}%)")
    print(f"    {color_status('BAD')}: {total_stats['BAD']:3d} ({100*total_stats['BAD']/total:.1f}%)")
    
    if all_alerts:
        critical = sum(1 for a in all_alerts if a['change'] == 'CRITICAL')
        degraded = sum(1 for a in all_alerts if a['change'] == 'DEGRADED')
        recovered = sum(1 for a in all_alerts if a['change'] == 'RECOVERED')
        print(f"\n  Threshold Crossings Since Last Snapshot:")
        if critical > 0:
            print(f"    🔴 CRITICAL: {critical}")
        if degraded > 0:
            print(f"    🟡 DEGRADED: {degraded}")
        if recovered > 0:
            print(f"    🟢 RECOVERED: {recovered}")
    else:
        print(f"\n  ✓ System stable - no threshold crossings")
    
    # Health score
    health_score = (total_stats['GOOD'] + 0.5 * total_stats['MARGINAL']) / total * 100
    print(f"\n  System Health Score: {health_score:.1f}%")
    
    if health_score >= 90:
        print("  Status: 🟢 HEALTHY")
    elif health_score >= 75:
        print("  Status: 🟡 FAIR")
    else:
        print("  Status: 🔴 DEGRADED")
    
    print()
    print("="*70)
    print("  Run daily_phi_collection.py to update baseline for comparison")
    print("="*70)
    print()


if __name__ == "__main__":
    monitor()
