# Temporal Prediction Analysis (Φ)

**No synthetic data.** Analysis uses only stored calibration snapshots.


## Dataset

- Snapshots: **19**

- Date range: **2025-12-31T16:50:08.472280+00:00** → **2026-01-29T17:01:24.915792+00:00**

- Backends: **3**

- Qubits tracked: **445**


## Warning Configuration

- Mode: **simple**

- Threshold: **Φ < 0.12**


## Failure Configuration

- Mode: **any**

- Threshold: **Φ < 0.1**

- Min lead time for on-time: **24.0** hours


## Event Counts

- Warnings issued: **64**

- True positives (≥24.0h lead): **11**

- Late warnings (<24.0h lead): **0**

- Same-snapshot (warn=fail time): **41**

- False positives (no failure): **12**

- Pending (too recent): **0**

- Missed failures (no warning): **0**

- Already failed (fail before warn): **0**


## Key Metrics

### Warning Quality

- **Precision** (TP/(TP+FP)): 47.8%

- **On-time Rate** (TP/resolved): 17.2%

- **FP Rate** (FP/resolved): 18.8%


### Failure Coverage

- **On-time Recall** (TP/total_failures): 21.2% ← KEY

- **Detection Rate** (any_warn/total_failures): 100.0%

- **Late/Same Rate** (sampling limitation): 64.1%


## Lead Time (hours, on-time TPs only)

- n: **11**

- mean: **162.7**

- p50: **147.6**

- p90: **243.6**

- range: **29.6 – 480.0**


## Parsing Integrity

- **ibm_fez**: parsed 19/19 (100%)

- **ibm_torino**: parsed 19/19 (100%)

- **ibm_marrakesh**: parsed 19/19 (100%)
