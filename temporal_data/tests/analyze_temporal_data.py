#!/usr/bin/env python3
"""
PATENT-GRADE TEMPORAL PREDICTION ANALYSIS (NO SYNTHETIC DATA)

Goal:
  Prove Φ provides EARLY WARNING of later qubit degradation events.

Inputs:
  temporal_data/phi_snapshot_*.json (daily or periodic calibration snapshots)

Outputs (in temporal_data/analysis_out/):
  - temporal_prediction_summary.json
  - temporal_prediction_events.csv
  - temporal_prediction_report.md

No hardcoded thresholds:
  - All thresholds are CLI args
  - Use --sweep-warning-thresholds for data-driven threshold selection

Warning modes (mutually exclusive):
  - simple: Φ < threshold (default)
  - persistence: Φ < threshold for N consecutive snapshots (--persistence-count N)
  - trend: slope ΔΦ/Δt < threshold (--trend-threshold, provide NEGATIVE value)
  - combined: BOTH persistence AND trend (--combined-mode with both args)

Failure events (--failure-mode):
  - status_bad: status == "BAD"
  - phi_below: Φ < failure_thr
  - any: status_bad OR phi_below

IMPORTANT:
  This script does NOT contact IBM. It only reads your stored JSON snapshots.

RECOMMENDED WORKFLOW:
  1. Run sweep first to find optimal threshold
  2. Pick threshold that maximizes on_time_recall with acceptable fp_rate
  3. Re-run with chosen threshold to generate final report
"""

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


TEMPORAL_DIR = Path("temporal_data")


def die(msg: str, code: int = 2) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def parse_dt(s: str) -> datetime:
    if not isinstance(s, str):
        raise ValueError("date/timestamp is not a string")
    ss = s.strip()
    if ss.endswith("Z"):
        ss = ss[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(ss)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ss, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    raise ValueError(f"Unrecognized datetime format: {s}")


def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as e:
        die(f"Failed to read/parse JSON: {path} ({e})")
    return {}


def looks_like_qubit_records(lst: Any) -> bool:
    if not isinstance(lst, list) or not lst:
        return False
    for ex in lst[:10]:
        if isinstance(ex, dict) and ("qubit" in ex) and (("phi" in ex) or ("status" in ex)):
            return True
    return False


def discover_backend_qubits(backend_obj: Any) -> Optional[List[Dict[str, Any]]]:
    if isinstance(backend_obj, list):
        return backend_obj if looks_like_qubit_records(backend_obj) else None

    if isinstance(backend_obj, dict):
        for k in ("qubits", "results", "data", "records"):
            v = backend_obj.get(k)
            if looks_like_qubit_records(v):
                return v
        for _, v in backend_obj.items():
            if looks_like_qubit_records(v):
                return v

    return None


@dataclass
class QubitObs:
    dt: datetime
    phi: Optional[float]
    status: Optional[str]


@dataclass
class EventRow:
    backend: str
    qubit: int
    warning_dt: Optional[datetime]
    failure_dt: Optional[datetime]
    lead_hours: Optional[float]
    outcome: str
    failure_kind: str
    warning_type: str


def build_history(files: List[Path]) -> Tuple[List[datetime], Dict[str, Dict[int, List[QubitObs]]], Dict[str, Any]]:
    history: Dict[str, Dict[int, List[QubitObs]]] = {}
    timeline: List[datetime] = []
    meta: Dict[str, Any] = {"files": [], "backend_shapes": {}, "dt_to_file": {}, "parse_ok": {}}

    for fp in files:
        d = load_json(fp)
        if "backends" not in d:
            die(f"{fp} missing top-level 'backends' key")

        snap_time = None
        for k in ("timestamp", "date"):
            if k in d and isinstance(d[k], str):
                try:
                    snap_time = parse_dt(d[k])
                    break
                except Exception:
                    pass
        if snap_time is None:
            die(f"{fp} has no parseable 'timestamp' or 'date'")

        timeline.append(snap_time)
        meta["files"].append({"file": fp.name, "dt": snap_time.isoformat()})
        meta["dt_to_file"][snap_time.isoformat()] = fp.name

        backends = d["backends"]
        if not isinstance(backends, dict):
            die(f"{fp} top-level 'backends' is not a dict")

        for backend_name, backend_obj in backends.items():
            qubits_list = discover_backend_qubits(backend_obj)

            meta["parse_ok"].setdefault(fp.name, {})[backend_name] = bool(qubits_list)

            if backend_name not in meta["backend_shapes"]:
                meta["backend_shapes"][backend_name] = {
                    "type": type(backend_obj).__name__,
                    "qubits_list_detected": bool(qubits_list),
                    "example_keys": list(backend_obj.keys())[:20] if isinstance(backend_obj, dict) else None,
                }

            if not qubits_list:
                continue

            for rec in qubits_list:
                if not isinstance(rec, dict):
                    continue
                qid = rec.get("qubit", None)
                try:
                    qid_int = int(qid)
                except Exception:
                    continue

                phi = safe_float(rec.get("phi"))
                status = rec.get("status")
                if isinstance(status, str):
                    status = status.strip().upper()
                else:
                    status = None

                history.setdefault(backend_name, {}).setdefault(qid_int, []).append(
                    QubitObs(dt=snap_time, phi=phi, status=status)
                )

    timeline_sorted = sorted(set(timeline))
    for b in history:
        for q in history[b]:
            history[b][q].sort(key=lambda o: o.dt)

    meta["timeline_start"] = timeline_sorted[0].isoformat() if timeline_sorted else None
    meta["timeline_end"] = timeline_sorted[-1].isoformat() if timeline_sorted else None
    meta["num_snapshots"] = len(timeline_sorted)
    meta["num_backends_with_data"] = len(history)
    meta["num_qubits_total"] = sum(len(history[b]) for b in history)

    return timeline_sorted, history, meta


def first_warning_simple(obs: List[QubitObs], warning_thr: float) -> Tuple[Optional[datetime], str]:
    """Simple threshold: warn when Φ < threshold."""
    for o in obs:
        if o.phi is None:
            continue
        if o.phi < warning_thr:
            return o.dt, "simple"
    return None, ""


def first_warning_persistence(obs: List[QubitObs], warning_thr: float, persist_count: int) -> Tuple[Optional[datetime], str]:
    """Persistence: require N consecutive snapshots below threshold."""
    consecutive = 0
    first_below_dt = None
    
    for o in obs:
        if o.phi is None:
            consecutive = 0
            first_below_dt = None
            continue
        
        if o.phi < warning_thr:
            if consecutive == 0:
                first_below_dt = o.dt
            consecutive += 1
            if consecutive >= persist_count:
                return first_below_dt, "persistence"
        else:
            consecutive = 0
            first_below_dt = None
    
    return None, ""


def first_warning_trend(obs: List[QubitObs], trend_threshold: float) -> Tuple[Optional[datetime], str]:
    """Trend: warn when slope ΔΦ/Δt < trend_threshold (threshold should be negative)."""
    prev = None
    
    for o in obs:
        if o.phi is None:
            prev = None
            continue
        
        if prev is not None and prev.phi is not None:
            dt_hours = (o.dt - prev.dt).total_seconds() / 3600.0
            if dt_hours > 0:
                slope = (o.phi - prev.phi) / dt_hours
                if slope < trend_threshold:
                    return o.dt, "trend"
        
        prev = o
    
    return None, ""


def first_warning_combined(
    obs: List[QubitObs], 
    warning_thr: float, 
    persist_count: int, 
    trend_threshold: float
) -> Tuple[Optional[datetime], str]:
    """Combined: require BOTH persistence AND trend conditions."""
    consecutive = 0
    first_below_dt = None
    prev = None
    
    for o in obs:
        if o.phi is None:
            consecutive = 0
            first_below_dt = None
            prev = None
            continue
        
        # Check persistence
        if o.phi < warning_thr:
            if consecutive == 0:
                first_below_dt = o.dt
            consecutive += 1
        else:
            consecutive = 0
            first_below_dt = None
        
        # Check trend
        has_negative_trend = False
        if prev is not None and prev.phi is not None:
            dt_hours = (o.dt - prev.dt).total_seconds() / 3600.0
            if dt_hours > 0:
                slope = (o.phi - prev.phi) / dt_hours
                if slope < trend_threshold:
                    has_negative_trend = True
        
        # Both conditions met?
        if consecutive >= persist_count and has_negative_trend:
            return first_below_dt, "combined"
        
        prev = o
    
    return None, ""


def determine_warning_mode(persist_count: int, trend_threshold: Optional[float], use_combined: bool) -> str:
    """Determine warning mode from CLI args (explicit, no coupling)."""
    if use_combined:
        return "combined"
    elif trend_threshold is not None:
        return "trend"
    elif persist_count > 1:
        return "persistence"
    else:
        return "simple"


def first_warning(
    obs: List[QubitObs],
    warning_thr: float,
    persist_count: int,
    trend_threshold: Optional[float],
    warning_mode: str
) -> Tuple[Optional[datetime], str]:
    """Dispatcher for warning detection (mode already determined)."""
    if warning_mode == "combined":
        # trend_threshold already validated as not None in main()
        return first_warning_combined(obs, warning_thr, persist_count, trend_threshold)
    elif warning_mode == "trend":
        # trend_threshold already validated as not None in main()
        return first_warning_trend(obs, trend_threshold)
    elif warning_mode == "persistence":
        return first_warning_persistence(obs, warning_thr, persist_count)
    else:
        return first_warning_simple(obs, warning_thr)


def first_failure(
    obs: List[QubitObs],
    failure_mode: str,
    failure_thr: Optional[float],
) -> Optional[datetime]:
    for o in obs:
        status_bad = (o.status == "BAD")
        phi_below = (failure_thr is not None and o.phi is not None and o.phi < failure_thr)

        if failure_mode == "status_bad":
            if status_bad:
                return o.dt
        elif failure_mode == "phi_below":
            if phi_below:
                return o.dt
        elif failure_mode == "any":
            if status_bad or phi_below:
                return o.dt
        else:
            die(f"Unknown failure_mode: {failure_mode}")

    return None


def compute_events(
    timeline: List[datetime],
    history: Dict[str, Dict[int, List[QubitObs]]],
    warning_thr: float,
    failure_mode: str,
    failure_thr: Optional[float],
    min_lead_hours: float,
    meta: Dict[str, Any],
    persist_count: int,
    trend_threshold: Optional[float],
    warning_mode: str,
) -> Tuple[List[EventRow], Dict[str, Any]]:
    events: List[EventRow] = []
    counters = {
        "warnings": 0,
        "true_positive": 0,
        "late_warning": 0,
        "same_snapshot": 0,
        "false_positive": 0,
        "pending": 0,
        "missed": 0,
        "already_failed": 0,
        "no_data": 0,
    }

    for backend in history:
        for qid, obs in history[backend].items():
            if not obs:
                counters["no_data"] += 1
                events.append(EventRow(backend, qid, None, None, None, "NO_DATA", "", ""))
                continue

            warn_dt, warn_type = first_warning(obs, warning_thr, persist_count, trend_threshold, warning_mode)
            fail_dt = first_failure(obs, failure_mode, failure_thr)

            chosen_fail_dt = fail_dt
            chosen_fail_kind = "metric" if fail_dt else ""

            if warn_dt is None and chosen_fail_dt is None:
                continue

            if warn_dt is None and chosen_fail_dt is not None:
                counters["missed"] += 1
                events.append(EventRow(backend, qid, None, chosen_fail_dt, None, "MISSED", chosen_fail_kind, ""))
                continue

            counters["warnings"] += 1

            if chosen_fail_dt is not None and chosen_fail_dt < warn_dt:
                counters["already_failed"] += 1
                events.append(EventRow(backend, qid, warn_dt, chosen_fail_dt, 0.0, "ALREADY_FAILED", chosen_fail_kind, warn_type))
                continue

            if chosen_fail_dt is not None and chosen_fail_dt == warn_dt:
                counters["same_snapshot"] += 1
                events.append(EventRow(backend, qid, warn_dt, chosen_fail_dt, 0.0, "SAME_SNAPSHOT", chosen_fail_kind, warn_type))
                continue

            if chosen_fail_dt is None:
                dataset_end = timeline[-1] if timeline else warn_dt
                hours_remaining = (dataset_end - warn_dt).total_seconds() / 3600.0

                if hours_remaining < min_lead_hours:
                    counters["pending"] += 1
                    events.append(EventRow(backend, qid, warn_dt, None, None, "PENDING", "", warn_type))
                else:
                    counters["false_positive"] += 1
                    events.append(EventRow(backend, qid, warn_dt, None, None, "FALSE_POSITIVE", "", warn_type))
                continue

            lead_hours = (chosen_fail_dt - warn_dt).total_seconds() / 3600.0
            if lead_hours >= min_lead_hours:
                counters["true_positive"] += 1
                events.append(EventRow(backend, qid, warn_dt, chosen_fail_dt, lead_hours, "TRUE_POSITIVE", chosen_fail_kind, warn_type))
            else:
                counters["late_warning"] += 1
                events.append(EventRow(backend, qid, warn_dt, chosen_fail_dt, lead_hours, "LATE_WARNING", chosen_fail_kind, warn_type))

    # === METRICS WITH CORRECT SEMANTICS ===
    
    TP = counters["true_positive"]
    FP = counters["false_positive"]
    late = counters["late_warning"]
    same = counters["same_snapshot"]
    missed = counters["missed"]
    
    # Resolved warnings = warnings that reached a definite outcome
    resolved = TP + late + same + FP
    
    # Total failures = all failure events (detected or not)
    total_failures = TP + late + same + missed
    
    # --- Classic Precision (PPV) ---
    # TP / (TP + FP) where TP = on-time warnings that preceded failure
    precision_denom = TP + FP
    precision = (TP / precision_denom) if precision_denom > 0 else None
    
    # --- On-time Rate (among resolved) ---
    # Of all resolved warnings, what fraction were on-time TPs?
    on_time_rate = (TP / resolved) if resolved > 0 else None
    
    # --- Late/Same Rate ---
    late_same_rate = ((late + same) / resolved) if resolved > 0 else None
    
    # --- False Positive Rate (among resolved) ---
    fp_rate = (FP / resolved) if resolved > 0 else None
    
    # --- On-time Recall ---
    # Of all failures, what fraction got ≥min_lead warning?
    on_time_recall = (TP / total_failures) if total_failures > 0 else None
    
    # --- Detection Rate (any warning) ---
    # Of all failures, what fraction got ANY warning (TP + late + same)?
    detected = TP + late + same
    detection_rate = (detected / total_failures) if total_failures > 0 else None

    summary = {
        "warning_threshold": warning_thr,
        "failure_mode": failure_mode,
        "failure_threshold": failure_thr,
        "min_lead_hours": min_lead_hours,
        "warning_mode": warning_mode,
        "persist_count": persist_count,
        "trend_threshold": trend_threshold,
        "counters": counters,
        "resolved_warnings": resolved,
        "total_failures": total_failures,
        "precision": precision,
        "on_time_rate": on_time_rate,
        "late_same_rate": late_same_rate,
        "fp_rate": fp_rate,
        "on_time_recall": on_time_recall,
        "detection_rate": detection_rate,
        "lead_hours_stats": lead_stats([e.lead_hours for e in events if e.lead_hours is not None and e.lead_hours > 0]),
    }

    return events, summary


def lead_stats(xs: List[float]) -> Dict[str, Any]:
    if not xs:
        return {"n": 0}
    xs2 = sorted(xs)
    def pct(p: float) -> float:
        idx = int(round((p/100.0) * (len(xs2)-1)))
        return xs2[max(0, min(len(xs2)-1, idx))]
    return {
        "n": len(xs2),
        "min": xs2[0],
        "max": xs2[-1],
        "mean": sum(xs2)/len(xs2),
        "p50": pct(50),
        "p90": pct(90),
    }


def write_csv(path: Path, events: List[EventRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["backend", "qubit", "warning_dt", "failure_dt", "lead_hours", "outcome", "failure_kind", "warning_type"])
        for e in events:
            w.writerow([
                e.backend,
                e.qubit,
                e.warning_dt.isoformat() if e.warning_dt else "",
                e.failure_dt.isoformat() if e.failure_dt else "",
                f"{e.lead_hours:.2f}" if e.lead_hours is not None else "",
                e.outcome,
                e.failure_kind,
                e.warning_type
            ])


def write_md(path: Path, meta: Dict[str, Any], summary: Dict[str, Any]) -> None:
    c = summary["counters"]
    ls = summary["lead_hours_stats"]

    lines = []
    lines.append("# Temporal Prediction Analysis (Φ)\n")
    lines.append("**No synthetic data.** Analysis uses only stored calibration snapshots.\n")
    
    lines.append("\n## Dataset\n")
    lines.append(f"- Snapshots: **{meta.get('num_snapshots')}**\n")
    lines.append(f"- Date range: **{meta.get('timeline_start')}** → **{meta.get('timeline_end')}**\n")
    lines.append(f"- Backends: **{meta.get('num_backends_with_data')}**\n")
    lines.append(f"- Qubits tracked: **{meta.get('num_qubits_total')}**\n")

    lines.append("\n## Warning Configuration\n")
    lines.append(f"- Mode: **{summary['warning_mode']}**\n")
    lines.append(f"- Threshold: **Φ < {summary['warning_threshold']}**\n")
    if summary['persist_count'] > 1:
        lines.append(f"- Persistence: **{summary['persist_count']}** consecutive snapshots\n")
    if summary['trend_threshold'] is not None:
        lines.append(f"- Trend condition: **slope < {summary['trend_threshold']}** per hour\n")

    lines.append("\n## Failure Configuration\n")
    lines.append(f"- Mode: **{summary['failure_mode']}**\n")
    lines.append(f"- Threshold: **Φ < {summary['failure_threshold']}**\n")
    lines.append(f"- Min lead time for on-time: **{summary['min_lead_hours']}** hours\n")

    lines.append("\n## Event Counts\n")
    lines.append(f"- Warnings issued: **{c['warnings']}**\n")
    lines.append(f"- True positives (≥{summary['min_lead_hours']}h lead): **{c['true_positive']}**\n")
    lines.append(f"- Late warnings (<{summary['min_lead_hours']}h lead): **{c['late_warning']}**\n")
    lines.append(f"- Same-snapshot (warn=fail time): **{c['same_snapshot']}**\n")
    lines.append(f"- False positives (no failure): **{c['false_positive']}**\n")
    lines.append(f"- Pending (too recent): **{c['pending']}**\n")
    lines.append(f"- Missed failures (no warning): **{c['missed']}**\n")
    lines.append(f"- Already failed (fail before warn): **{c['already_failed']}**\n")

    lines.append("\n## Key Metrics\n")
    lines.append("### Warning Quality\n")
    if summary["precision"] is not None:
        lines.append(f"- **Precision** (TP/(TP+FP)): {summary['precision']*100:.1f}%\n")
    if summary["on_time_rate"] is not None:
        lines.append(f"- **On-time Rate** (TP/resolved): {summary['on_time_rate']*100:.1f}%\n")
    if summary["fp_rate"] is not None:
        lines.append(f"- **FP Rate** (FP/resolved): {summary['fp_rate']*100:.1f}%\n")
    
    lines.append("\n### Failure Coverage\n")
    if summary["on_time_recall"] is not None:
        lines.append(f"- **On-time Recall** (TP/total_failures): {summary['on_time_recall']*100:.1f}% ← KEY\n")
    if summary["detection_rate"] is not None:
        lines.append(f"- **Detection Rate** (any_warn/total_failures): {summary['detection_rate']*100:.1f}%\n")
    if summary["late_same_rate"] is not None:
        lines.append(f"- **Late/Same Rate** (sampling limitation): {summary['late_same_rate']*100:.1f}%\n")

    lines.append("\n## Lead Time (hours, on-time TPs only)\n")
    if ls.get("n", 0) == 0:
        lines.append("- No lead-time samples.\n")
    else:
        lines.append(f"- n: **{ls['n']}**\n")
        lines.append(f"- mean: **{ls['mean']:.1f}**\n")
        lines.append(f"- p50: **{ls['p50']:.1f}**\n")
        lines.append(f"- p90: **{ls['p90']:.1f}**\n")
        lines.append(f"- range: **{ls['min']:.1f} – {ls['max']:.1f}**\n")

    lines.append("\n## Parsing Integrity\n")
    for b, info in (meta.get("backend_shapes") or {}).items():
        ok = 0; total = 0
        for fname, m in (meta.get("parse_ok") or {}).items():
            if b in m:
                total += 1
                ok += 1 if m[b] else 0
        rate = (100.0 * ok / total) if total else 0.0
        lines.append(f"- **{b}**: parsed {ok}/{total} ({rate:.0f}%)\n")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def threshold_sweep(
    timeline: List[datetime],
    history: Dict[str, Dict[int, List[QubitObs]]],
    failure_mode: str,
    failure_thr: Optional[float],
    min_lead_hours: float,
    sweep_values: List[float],
    meta: Dict[str, Any],
    persist_count: int,
    trend_threshold: Optional[float],
    warning_mode: str,
) -> List[Dict[str, Any]]:
    out = []
    for wthr in sweep_values:
        _, summ = compute_events(
            timeline, history,
            warning_thr=wthr,
            failure_mode=failure_mode,
            failure_thr=failure_thr,
            min_lead_hours=min_lead_hours,
            meta=meta,
            persist_count=persist_count,
            trend_threshold=trend_threshold,
            warning_mode=warning_mode,
        )
        out.append({
            "warning_threshold": wthr,
            "precision": summ["precision"],
            "on_time_rate": summ["on_time_rate"],
            "on_time_recall": summ["on_time_recall"],
            "detection_rate": summ["detection_rate"],
            "fp_rate": summ["fp_rate"],
            "resolved_warnings": summ["resolved_warnings"],
            "total_failures": summ["total_failures"],
            "true_positive": summ["counters"]["true_positive"],
            "late_warning": summ["counters"]["late_warning"],
            "same_snapshot": summ["counters"]["same_snapshot"],
            "false_positive": summ["counters"]["false_positive"],
            "missed": summ["counters"]["missed"],
            "already_failed": summ["counters"]["already_failed"],
        })
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Patent-grade temporal prediction analysis for Φ stability metric.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
RECOMMENDED WORKFLOW (data-driven, no hardcoded thresholds):

  STEP 1: Run sweep to find optimal warning threshold
    python analyze_temporal_data.py \\
      --warning-threshold 0.20 \\
      --failure-mode any --failure-threshold 0.10 \\
      --min-lead-hours 24 \\
      --sweep-warning-thresholds 0.10:0.40:0.02

  STEP 2: Review sweep output, pick threshold with best on_time_recall vs fp_rate

  STEP 3: Re-run with chosen threshold for final report
        """
    )
    ap.add_argument("--temporal-dir", default=str(TEMPORAL_DIR), help="Directory with phi_snapshot_*.json")
    ap.add_argument("--warning-threshold", type=float, required=True, help="Warn when Φ < this")
    ap.add_argument("--failure-mode", choices=["status_bad", "phi_below", "any"], required=True)
    ap.add_argument("--failure-threshold", type=float, default=None, help="Required for phi_below/any")
    ap.add_argument("--min-lead-hours", type=float, required=True, help="Min hours for on-time TP")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    ap.add_argument("--sweep-warning-thresholds", default=None, help="Sweep 'start:stop:step'")
    
    # Warning policy
    ap.add_argument("--persistence-count", type=int, default=1, help="Require N consecutive snapshots (default 1)")
    ap.add_argument("--trend-threshold", type=float, default=None, help="Slope threshold (NEGATIVE, e.g. -0.001)")
    ap.add_argument("--combined-mode", action="store_true", help="Require BOTH persistence AND trend")
    
    args = ap.parse_args()

    temporal_dir = Path(args.temporal_dir)
    if not temporal_dir.exists():
        die(f"Temporal dir not found: {temporal_dir}")

    files = sorted(temporal_dir.glob("phi_snapshot_*.json"))
    if not files:
        die(f"No phi_snapshot_*.json found in {temporal_dir}")

    if args.failure_mode in ("phi_below", "any") and args.failure_threshold is None:
        die("--failure-threshold required for phi_below/any mode")

    # Clamp persistence_count to minimum 1
    persist_count = max(1, args.persistence_count)

    # Validate combined mode requirements
    if args.combined_mode:
        if persist_count < 2:
            die("--combined-mode requires --persistence-count >= 2")
        if args.trend_threshold is None:
            die("--combined-mode requires --trend-threshold")

    # Determine warning mode explicitly (no silent coupling)
    warning_mode = determine_warning_mode(persist_count, args.trend_threshold, args.combined_mode)

    timeline, history, meta = build_history(files)

    out_dir = Path(args.out_dir) if args.out_dir else (temporal_dir / "analysis_out")
    out_dir.mkdir(parents=True, exist_ok=True)

    events, summary = compute_events(
        timeline=timeline,
        history=history,
        warning_thr=float(args.warning_threshold),
        failure_mode=args.failure_mode,
        failure_thr=args.failure_threshold,
        min_lead_hours=float(args.min_lead_hours),
        meta=meta,
        persist_count=persist_count,
        trend_threshold=args.trend_threshold,
        warning_mode=warning_mode,
    )

    summary_path = out_dir / "temporal_prediction_summary.json"
    events_csv = out_dir / "temporal_prediction_events.csv"
    report_md = out_dir / "temporal_prediction_report.md"

    payload = {"meta": meta, "summary": summary}
    summary_path.write_text(json.dumps(payload, indent=2))

    write_csv(events_csv, events)
    write_md(report_md, meta, summary)

    print("="*70)
    print("TEMPORAL PREDICTION ANALYSIS (NO SYNTHETIC DATA)")
    print("="*70)
    print(f"Snapshots: {meta.get('num_snapshots')}  Range: {meta.get('timeline_start')[:10]} → {meta.get('timeline_end')[:10]}")
    print(f"Warning: mode={warning_mode}, threshold={args.warning_threshold}, persist={persist_count}, trend={args.trend_threshold}")
    print(f"Failure: mode={args.failure_mode}, threshold={args.failure_threshold}, min_lead={args.min_lead_hours}h")
    print(f"\nOutputs: {summary_path.name}, {events_csv.name}, {report_md.name}")
    
    c = summary["counters"]
    print(f"\nCounts:")
    print(f"  warnings={c['warnings']}  TP={c['true_positive']}  late={c['late_warning']}  same={c['same_snapshot']}  FP={c['false_positive']}  missed={c['missed']}")
    
    print(f"\nMetrics:")
    if summary["precision"] is not None:
        print(f"  Precision (TP/(TP+FP)):     {summary['precision']*100:.1f}%")
    if summary["on_time_recall"] is not None:
        print(f"  On-time Recall (TP/fails):  {summary['on_time_recall']*100:.1f}%  ← KEY METRIC")
    if summary["detection_rate"] is not None:
        print(f"  Detection Rate (any/fails): {summary['detection_rate']*100:.1f}%")
    if summary["late_same_rate"] is not None:
        print(f"  Late/Same Rate:             {summary['late_same_rate']*100:.1f}%  (sampling limitation)")
    if summary["fp_rate"] is not None:
        print(f"  FP Rate (FP/resolved):      {summary['fp_rate']*100:.1f}%")

    if args.sweep_warning_thresholds:
        try:
            s0, s1, st = args.sweep_warning_thresholds.split(":")
            start = float(s0); stop = float(s1); step = float(st)
            if step <= 0:
                raise ValueError("step must be > 0")
            vals = []
            v = start
            while v <= stop + 1e-12:
                vals.append(round(v, 10))
                v += step
            sweep = threshold_sweep(
                timeline=timeline,
                history=history,
                failure_mode=args.failure_mode,
                failure_thr=args.failure_threshold,
                min_lead_hours=float(args.min_lead_hours),
                sweep_values=vals,
                meta=meta,
                persist_count=persist_count,
                trend_threshold=args.trend_threshold,
                warning_mode=warning_mode,
            )
            sweep_path = out_dir / "temporal_threshold_sweep.json"
            sweep_path.write_text(json.dumps(sweep, indent=2))
            print(f"\nSweep saved: {sweep_path}")
        except Exception as e:
            die(f"Sweep failed: {e}")

if __name__ == "__main__":
    main()
