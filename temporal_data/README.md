# Temporal Data Collection

**Purpose:** Prove Φ PREDICTS qubit failures BEFORE they happen.

---

## Why This Matters

| What We Proved | What This Proves |
|----------------|------------------|
| Low Φ = bad qubit NOW | Low Φ = qubit WILL FAIL SOON |
| Correlation | **Prediction** |
| "Interesting" | **"Game-changing"** |

This is the difference between a $5M patent and a $100M+ patent.

---

## What's In This Folder

| File | Description |
|------|-------------|
| `phi_snapshot_YYYYMMDD_HHMMSS.json` | Daily snapshot of all 445 qubits |
| `latest.json` | Copy of most recent snapshot (for easy access) |

Each JSON contains Φ values for all qubits on all 3 IBM backends.

---

## How To Collect Data

### Step 1: Open Terminal

On your Mac, open Terminal.

### Step 2: Run the Collection Script
```bash
python ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py
```

### Step 3: Verify It Worked

You should see output like:
```
============================================================
DAILY Φ DATA COLLECTION
Date: 2025-01-01 10:00:00
============================================================

Collecting from ibm_fez...
  Valid: 156, Skipped: 0
  Φ range: -0.0343 to 0.9992
  GOOD: 140, MARGINAL: 15, BAD: 1

Collecting from ibm_torino...
  Valid: 133, Skipped: 0
  ...

✓ Saved to /Users/shawnbarnicle/Desktop/quantum-phi-validation/temporal_data/phi_snapshot_20250101_100000.json
✓ Updated latest.json

Total qubits collected: 445
```

### Step 4: Repeat Daily

Run this **every day** for **14-30 days**.

---

## Quick Copy-Paste Command
```bash
python ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py
```

---

## Set a Daily Reminder

### Option A: Phone Reminder
Set a daily alarm/reminder on your phone: "Run Φ data collection"

### Option B: Mac Calendar
1. Open Calendar app
2. Create recurring daily event
3. Title: "Run: python ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py"

### Option C: Sticky Note on Desktop
You already have: `~/Desktop/DAILY_PHI_REMINDER.txt`

---

## Where Does the Data Come From?

### IBM Quantum Platform

**Website:** https://quantum.ibm.com

**What it provides:**
- Real-time calibration data for 445 qubits
- 3 backends: ibm_fez, ibm_torino, ibm_marrakesh
- Updated by IBM every few hours

**Your account:** Already set up (you ran tests today)

**Free tier:** 10 minutes of quantum time per month (this script uses ~0 minutes - just reads calibration data)

---

## What Gets Collected

For each qubit, the script saves:

| Field | Description |
|-------|-------------|
| `qubit` | Qubit number (0-155) |
| `phi` | The Φ stability metric |
| `t1` | T1 relaxation time (seconds) |
| `t2` | T2 coherence time (seconds) |
| `fidelity` | Gate fidelity (0-1) |
| `readout_error` | Measurement error (0-1) |
| `status` | GOOD / MARGINAL / BAD |

---

## Timeline

| Day | Action |
|-----|--------|
| Day 1 (Dec 31, 2025) | ✓ DONE - First snapshot collected |
| Days 2-14 | Run daily_phi_collection.py each day |
| Day 14+ | Can start analysis (minimum data) |
| Day 30 | Ideal amount of data for strong proof |

---

## After 14-30 Days: Analysis

Once you have enough data, you'll analyze:

1. **Which qubits crossed below Φ = 0.25?**
2. **Did those qubits actually degrade later?**
3. **How many days warning did Φ provide?**

### Success Criteria

| Metric | Target |
|--------|--------|
| True positive rate | > 90% (Φ < 0.25 → qubit failed) |
| False positive rate | < 10% (Φ < 0.25 but qubit was fine) |
| Warning time | > 24 hours before failure |

### Analysis Script (run after 14+ days)
```bash
python ~/Desktop/quantum-phi-validation/experiments/analyze_temporal_data.py
```

(This script will be created when you have enough data)

---

## Troubleshooting

### "Command not found: python"
Try:
```bash
python3 ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py
```

### "No module named qiskit_ibm_runtime"
```bash
pip install qiskit-ibm-runtime
```

### "Token invalid" or authentication error
1. Go to https://quantum.ibm.com
2. Click profile → Account settings → API keys
3. Create new key
4. Run:
```bash
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_NEW_TOKEN', overwrite=True)"
```

### Script hangs or takes forever
IBM servers might be slow. Wait 2-3 minutes. If still stuck, press Ctrl+C and try again later.

---

## Files Collected So Far

| Date | File | Qubits |
|------|------|--------|
| Dec 31, 2025 | phi_snapshot_20251231_165011.json | 445 |

(This table will grow as you collect more days)

---

## Summary

| What | Details |
|------|---------|
| **Goal** | Prove Φ predicts failures |
| **Method** | Daily snapshots for 14-30 days |
| **Command** | `python ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py` |
| **Time** | ~30 seconds per run |
| **Cost** | Free (just reads calibration data) |
| **Website** | https://quantum.ibm.com |

---

## DON'T FORGET

**Run this every day:**
```bash
python ~/Desktop/quantum-phi-validation/experiments/daily_phi_collection.py
```

Set a reminder. This is the most important test for your patent.

---

*Started: December 31, 2025*
*Target: January 14-30, 2026*
