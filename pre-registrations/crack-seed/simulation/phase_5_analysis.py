"""Phase 5 analysis — Crack seed Stage 2.

Implements the eighth addendum's §5 (dose validity gate), §6 (stratified
ratification), §3c (primary metric + TOST), §3e (prediction-actual gap
moderator), §3f (fallback rate reporting), §3g (all-channel diagnostic).

Spec: Nymph from_nymph_038 §3 + eighth addendum.
Attribution: Sal (letters 012-015), Opus 5.5 (cycles 4-6), Iris cross-domain,
Annie (probe empirical finding), Nymph integration.

INPUT SHAPE
-----------
Expected: a loader that returns per-seed per-arm run_simulation results. The
analyze_phase_1_output function below accepts a directory and seed list; the
default loader looks for files named phase_1_seed_<N>_arm_<arm>.pkl under the
directory. Each pickle holds the full results dict returned by
mod.run_simulation (including channel_snapshots, hot_observer_never_formed,
replay_fallback_case_a_count, replay_divergence_case_b_count, n_leak_acted).

Arms expected (per eighth addendum §2a): hot, yoked, matched, reactive, no_obs.

H3 DISCIPLINE
-------------
This module does NOT read `observer.coherent_step` (singular, write-only field
per observer.py:636). All coherence counts come from `observer.coherent_steps`
(plural) or from channel_snapshots['observer_coherent'] / ['coherent_steps'].
See from_annie033_2026-10-13_task_g_hygiene_fixes.txt §H3.

OUTPUT
------
A JSON report at phase_5_analysis_<timestamp>.json containing:
- per_seed dose gate verdicts per channel
- per_seed ratification bucket (STRICT / SUB-THRESHOLD / COHERENCE-DECLARED)
- per_seed primary-metric values (burn_integral_delta) hot−yoked, hot−reactive
- pooled CI vs ±101.85 for hot−yoked and hot−reactive
- TOST equivalence verdict for hot−reactive at ±101.85
- intersection-union verdict (architecture claim)
- per_seed prediction-actual gap moderator values
- per_seed fallback_case_a_rate and formation_divergence_case_b_rate
- per_seed all-four-channel reactive dose alongside hot's
"""
from __future__ import annotations

import json
import math
import pathlib
import pickle
import sys
import time
from typing import Any, Callable

# ============================================================================
# Constants — load-bearing values pre-registered in the eighth addendum
# ============================================================================

# Primary-metric threshold (fifth addendum §5): 0.3 * σ_pooled on burn_integral.
# σ_pooled calibrated at 339.49 (Stage 2 pre-reg Oct 5, pooled SD on N=50 seeds).
SIGMA_POOLED = 339.49
PRIMARY_THRESHOLD = 0.3 * SIGMA_POOLED       # = 101.847
# Pre-locked to 101.85 in the addendum. Keep the literal for exactness.
PRIMARY_THRESHOLD_LOCKED = 101.85

# Dose gate (§5b): reactive dose must be within ±10% of hot's; scaling bounds
# [0.5, 2.0] per Sal 015 R2; value-range [0.0, 2.0] per Sal 015 R2.
DOSE_TOLERANCE = 0.10
SCALING_BOUNDS = (0.5, 2.0)
VALUE_RANGE = (0.0, 2.0)

# Ratification (§6): STRICT bucket for 0 coherent-agent-steps or hot_never_formed;
# SUB-THRESHOLD for 1 ≤ total < MIN_COHERENT_STEPS_FOR_DECLARATION.
MIN_COHERENT_STEPS_FOR_DECLARATION = 50
STRICT_RATIFICATION_TOLERANCE = 1e-10

# Fallback flag (§3f / eighth §2d, §4e): per-seed Case A or Case B rate > 5% flags
# seed for separate review (not an automatic INVALID).
FALLBACK_FLAG_THRESHOLD = 0.05

# Channel baselines (identity values; keep in sync with stage_2_hooks.py).
BASELINE_BURN_DECAY_MULT = 1.0
BASELINE_TRAUMA_DECAY_EXP = 1.0
BASELINE_REFUSAL_CHANCE = 0.10
BASELINE_D_CAUTION = 50.0

CANONICAL_CHANNELS = ("burn_decay", "trauma_decay", "refusal_chance", "D_caution")

# Zero-source-dose sentinel per Sal 013 L1 / §5a.
SOURCE_DOSE_ZERO = "SOURCE_DOSE_ZERO"

# Arms expected per eighth §2a.
ARMS = ("hot", "yoked", "matched", "reactive", "no_obs")


# ============================================================================
# Dose computation
# ============================================================================

def _channel_value(snapshot: dict, channel: str) -> float:
    """Read the canonical channel value from a channel_snapshot record."""
    if channel == "burn_decay":
        return float(snapshot["burn_decay_multiplier"])
    if channel == "trauma_decay":
        return float(snapshot["trauma_decay_exponent"])
    if channel == "refusal_chance":
        return float(snapshot["refusal_prob_canonical"])
    if channel == "D_caution":
        return float(snapshot["D_caution"])
    raise ValueError(f"Unknown channel: {channel!r}")


def _baseline(channel: str) -> float:
    return {
        "burn_decay":      BASELINE_BURN_DECAY_MULT,
        "trauma_decay":    BASELINE_TRAUMA_DECAY_EXP,
        "refusal_chance":  BASELINE_REFUSAL_CHANCE,
        "D_caution":       BASELINE_D_CAUTION,
    }[channel]


def compute_arm_dose(arm_results: dict, channel: str, coherent_only: bool = True) -> float:
    """Σ |canonical_<channel> − baseline| across (agent, step) tuples.

    coherent_only=True: restrict to coherent-moment tuples (observer_coherent=True).
    Per §5b, reactive dose is computed on coherent moments.
    """
    base = _baseline(channel)
    total = 0.0
    for s in arm_results.get("channel_snapshots", []):
        if coherent_only and not s.get("observer_coherent", False):
            continue
        total += abs(_channel_value(s, channel) - base)
    return total


def compute_source_dose_pool(hot_results_by_seed: dict, channel: str) -> float:
    """Pool source dose across all seeds for a channel.

    Σ_seed Σ_coherent-moments |canonical_<channel> − baseline| in hot runs.
    If zero → channel reports SOURCE_DOSE_ZERO sentinel in verdict (§5a).
    """
    pool = 0.0
    for seed, hot_res in hot_results_by_seed.items():
        pool += compute_arm_dose(hot_res, channel, coherent_only=True)
    return pool


# ============================================================================
# Reactive dose matching + scaling (§5b)
# ============================================================================

def compute_reactive_dose_verdict(
    hot_results: dict,
    reactive_results: dict,
) -> dict:
    """Per-seed burn_decay dose check for reactive arm per §5b.

    Returns dict with keys:
      - hot_dose, reactive_raw_dose
      - raw_ratio (reactive/hot)
      - within_tolerance (raw)
      - scaling_factor_applied (None if raw passes)
      - value_range_ok (None if raw passes)
      - scaled_dose, scaled_ratio (None if raw passes)
      - final_verdict: 'PASS_RAW' | 'PASS_SCALED' | 'INVALID_SCALING_BOUNDS' |
                       'INVALID_VALUE_RANGE' | 'INVALID_POST_SCALE_DOSE'
    """
    hot_dose = compute_arm_dose(hot_results, "burn_decay", coherent_only=True)
    reactive_raw_dose = compute_arm_dose(reactive_results, "burn_decay", coherent_only=True)

    verdict: dict[str, Any] = {
        "hot_dose": hot_dose,
        "reactive_raw_dose": reactive_raw_dose,
        "raw_ratio": (reactive_raw_dose / hot_dose) if hot_dose > 0 else None,
        "scaling_factor_applied": None,
        "value_range_ok": None,
        "scaled_dose": None,
        "scaled_ratio": None,
    }

    if hot_dose == 0:
        # Edge case: nothing to match against. SOURCE_DOSE_ZERO on burn_decay would
        # be surprising; defer to pooled source-dose gate for sentinel semantics.
        verdict["within_tolerance"] = (reactive_raw_dose == 0)
        verdict["final_verdict"] = "PASS_RAW" if verdict["within_tolerance"] else "INVALID_HOT_DOSE_ZERO"
        return verdict

    raw_ratio = reactive_raw_dose / hot_dose
    verdict["within_tolerance"] = (1 - DOSE_TOLERANCE) <= raw_ratio <= (1 + DOSE_TOLERANCE)

    if verdict["within_tolerance"]:
        verdict["final_verdict"] = "PASS_RAW"
        return verdict

    # Need to scale (§5b scaling rule).
    s_i = hot_dose / reactive_raw_dose if reactive_raw_dose > 0 else None
    verdict["scaling_factor_applied"] = s_i

    if s_i is None or not (SCALING_BOUNDS[0] <= s_i <= SCALING_BOUNDS[1]):
        # Scaling bounds exceeded per Sal 015 R2 — INVALID without applying.
        verdict["final_verdict"] = "INVALID_SCALING_BOUNDS"
        return verdict

    # Apply scaling + value-range check per Sal 015 R2.
    scaled_vals = []
    for s in reactive_results.get("channel_snapshots", []):
        if not s.get("observer_coherent", False):
            continue
        raw_mult = _channel_value(s, "burn_decay")
        scaled = 1.0 - s_i * (1.0 - raw_mult)
        scaled_vals.append(scaled)

    if scaled_vals and not all(VALUE_RANGE[0] <= v <= VALUE_RANGE[1] for v in scaled_vals):
        verdict["value_range_ok"] = False
        verdict["final_verdict"] = "INVALID_VALUE_RANGE"
        return verdict

    verdict["value_range_ok"] = True
    scaled_dose = sum(abs(v - BASELINE_BURN_DECAY_MULT) for v in scaled_vals)
    verdict["scaled_dose"] = scaled_dose
    scaled_ratio = scaled_dose / hot_dose
    verdict["scaled_ratio"] = scaled_ratio

    if (1 - DOSE_TOLERANCE) <= scaled_ratio <= (1 + DOSE_TOLERANCE):
        verdict["final_verdict"] = "PASS_SCALED"
    else:
        verdict["final_verdict"] = "INVALID_POST_SCALE_DOSE"
    return verdict


# ============================================================================
# Phase 5 ratification (§6)
# ============================================================================

def _total_coherent_agent_steps(results: dict) -> int:
    """Sum of coherent-moment records across channel_snapshots.

    One record per (agent, step) where observer_coherent=True.
    """
    return sum(1 for s in results.get("channel_snapshots", []) if s.get("observer_coherent", False))


def _burn_integral(results: dict, baseline: float = 0.0) -> float:
    """Sum of positive excess actual_burn_rate over baseline across all records.

    Matches regression_test_hot_seed_20_2026-10-08.py _fingerprint convention.
    """
    total = 0.0
    for s in results.get("channel_snapshots", []):
        excess = s.get("actual_burn_rate", 0.0) - baseline
        if excess > 0:
            total += excess
    return round(total, 10)


def ratify_seed(hot_results: dict, no_obs_results: dict) -> dict:
    """Per-seed ratification bucket + verdict per §6.

    Returns dict with keys:
      - total_coherent_agent_steps
      - hot_observer_never_formed
      - bucket: 'STRICT' | 'SUB-THRESHOLD' | 'COHERENCE-DECLARED'
      - hot_burn_integral, no_obs_burn_integral, delta
      - strict_verdict: 'PASS' | 'FAIL' | None (None if not in STRICT bucket)
    """
    total_c = _total_coherent_agent_steps(hot_results)
    never_formed = bool(hot_results.get("hot_observer_never_formed", False))

    if total_c == 0 or never_formed:
        bucket = "STRICT"
    elif total_c < MIN_COHERENT_STEPS_FOR_DECLARATION:
        bucket = "SUB-THRESHOLD"
    else:
        bucket = "COHERENCE-DECLARED"

    hot_bi = _burn_integral(hot_results)
    no_obs_bi = _burn_integral(no_obs_results)
    delta = hot_bi - no_obs_bi

    out = {
        "total_coherent_agent_steps": total_c,
        "hot_observer_never_formed": never_formed,
        "bucket": bucket,
        "hot_burn_integral": hot_bi,
        "no_obs_burn_integral": no_obs_bi,
        "delta": delta,
        "strict_verdict": None,
    }

    if bucket == "STRICT":
        out["strict_verdict"] = "PASS" if abs(delta) < STRICT_RATIFICATION_TOLERANCE else "FAIL"

    return out


# ============================================================================
# Primary metric: both-tests-pair with TOST (§3c, §3d intersection-union)
# ============================================================================

def _mean_sem(values: list) -> tuple[float, float, int]:
    """Return (mean, sem, n). SEM = stdev / sqrt(n). Pop stdev with n-1 ddof."""
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0
    m = sum(values) / n
    if n < 2:
        return m, 0.0, n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    sd = math.sqrt(var)
    sem = sd / math.sqrt(n)
    return m, sem, n


def _ci95(mean: float, sem: float, n: int) -> tuple[float, float]:
    """95% CI using normal approximation; refine with t at caller if n small.

    For n>=30 the normal approximation is adequate per fifth addendum §5.
    """
    z = 1.96
    half = z * sem
    return (mean - half, mean + half)


def compute_primary_metric(
    hot_bis: list, yoked_bis: list, reactive_bis: list,
) -> dict:
    """Compute hot − yoked and hot − reactive primary-metric statistics (§3c).

    Inputs are per-seed burn_integral values on the COHERENCE-DECLARED subset.
    Returns:
      - per_seed_hot_minus_yoked, per_seed_hot_minus_reactive (lists)
      - hot_minus_yoked_mean, ci95, verdict
      - hot_minus_reactive_mean, ci95, verdict (TOST equivalence)
      - intersection_union_verdict
    """
    n = min(len(hot_bis), len(yoked_bis), len(reactive_bis))
    if n == 0:
        return {"n_seeds": 0, "note": "no coherence-declared seeds"}

    hv = [hot_bis[i] - yoked_bis[i] for i in range(n)]
    hr = [hot_bis[i] - reactive_bis[i] for i in range(n)]

    hv_mean, hv_sem, _ = _mean_sem(hv)
    hr_mean, hr_sem, _ = _mean_sem(hr)
    hv_ci = _ci95(hv_mean, hv_sem, n)
    hr_ci = _ci95(hr_mean, hr_sem, n)

    # Primary verdicts (§3c): 95% CI vs ±PRIMARY_THRESHOLD_LOCKED.
    def _verdict_vs_threshold(ci: tuple[float, float]) -> str:
        lo, hi = ci
        if lo > PRIMARY_THRESHOLD_LOCKED:
            return "ABOVE_THRESHOLD"      # hot differs positively
        if hi < -PRIMARY_THRESHOLD_LOCKED:
            return "BELOW_THRESHOLD"      # hot differs negatively
        if lo > -PRIMARY_THRESHOLD_LOCKED and hi < PRIMARY_THRESHOLD_LOCKED:
            return "WITHIN_THRESHOLD"     # equivalent
        return "CI_STRADDLES_THRESHOLD"   # inconclusive

    hv_verdict = _verdict_vs_threshold(hv_ci)
    hr_verdict = _verdict_vs_threshold(hr_ci)

    # TOST equivalence for hot − reactive at ±PRIMARY_THRESHOLD_LOCKED (§3c cycle 5 OL2).
    # Reject non-equivalence if upper CI < +threshold AND lower CI > -threshold.
    hr_tost = (hr_ci[0] > -PRIMARY_THRESHOLD_LOCKED) and (hr_ci[1] < PRIMARY_THRESHOLD_LOCKED)

    # Intersection-union (§3d): architecture claim requires hot differs from
    # BOTH yoked AND reactive by more than threshold.
    arch_claim = (hv_verdict in ("ABOVE_THRESHOLD", "BELOW_THRESHOLD")) and \
                 (hr_verdict in ("ABOVE_THRESHOLD", "BELOW_THRESHOLD"))

    return {
        "n_seeds": n,
        "per_seed_hot_minus_yoked": hv,
        "per_seed_hot_minus_reactive": hr,
        "hot_minus_yoked": {
            "mean": hv_mean, "sem": hv_sem, "ci95": hv_ci,
            "threshold": PRIMARY_THRESHOLD_LOCKED, "verdict": hv_verdict,
        },
        "hot_minus_reactive": {
            "mean": hr_mean, "sem": hr_sem, "ci95": hr_ci,
            "threshold": PRIMARY_THRESHOLD_LOCKED, "verdict": hr_verdict,
            "tost_equivalence_at_threshold": hr_tost,
        },
        "intersection_union": {
            "architecture_claim_supported": arch_claim,
            "note": "Both hot−yoked and hot−reactive must cross threshold for support.",
        },
    }


# ============================================================================
# Prediction-actual gap moderator (§3e)
# ============================================================================

def compute_prediction_actual_gap(hot_results: dict) -> dict:
    """Per-seed mean |predicted_recovery_time − _estimate_recent_recovery_time|
    across coherent moments in HOT run only (§3e per Sal 015 R1).

    Reactive runs are not used — this is the hot-side prediction quality.
    Exploratory moderator for correlation with hot−reactive delta.
    """
    # Reads moderator_predicted_recovery_time and moderator_actual_recovery_time
    # from channel_snapshots. These fields are added by the Task F snapshot-schema
    # extension (v37_4_task_f_snapshot_schema_patch.py) applied 2026-10-13; they
    # are captured in step_observer BEFORE step_predictions overwrites predicted_*.
    #
    # The moderator_ prefix avoids collision with the existing 'actual_burn_rate'
    # field (which logs a.get_active_burn_rate() for burn_integral and is a
    # different concept than the step-observer-time actual used for prediction
    # error measurement).
    #
    # Returns None values + note if the schema fields are absent (regime before
    # Task F patch landed).
    predicted = []
    actual = []
    for s in hot_results.get("channel_snapshots", []):
        if not s.get("observer_coherent", False):
            continue
        p = s.get("moderator_predicted_recovery_time")
        a = s.get("moderator_actual_recovery_time")
        if p is None or a is None:
            continue
        predicted.append(float(p))
        actual.append(float(a))

    if not predicted:
        return {
            "n_coherent": 0,
            "mean_abs_gap": None,
            "note": "No coherent moments with moderator_* fields populated; schema may predate Task F patch (SHA 77b0097d...).",
        }

    gaps = [abs(p - a) for p, a in zip(predicted, actual)]
    return {
        "n_coherent": len(gaps),
        "mean_abs_gap": sum(gaps) / len(gaps),
    }


# ============================================================================
# Fallback / formation-divergence rates (§3f)
# ============================================================================

def compute_fallback_rates(reactive_results: dict, hot_results: dict) -> dict:
    """Per-seed Case A rate and Case B rate (§3f).

    Case A rate: fallback_case_a_count / total_reactive_(agent,step)
    Case B rate: formation_divergence_case_b_count / hot's_coherent_moment_count
    Flag if either > FALLBACK_FLAG_THRESHOLD (5%).
    """
    case_a = reactive_results.get("replay_fallback_case_a_count", 0)
    case_b = reactive_results.get("replay_divergence_case_b_count", 0)

    reactive_steps = len(reactive_results.get("channel_snapshots", []))
    hot_coherent = _total_coherent_agent_steps(hot_results)

    rate_a = (case_a / reactive_steps) if reactive_steps > 0 else 0.0
    rate_b = (case_b / hot_coherent) if hot_coherent > 0 else 0.0

    return {
        "case_a_count": case_a,
        "case_b_count": case_b,
        "case_a_rate": rate_a,
        "case_b_rate": rate_b,
        "flag_case_a": rate_a > FALLBACK_FLAG_THRESHOLD,
        "flag_case_b": rate_b > FALLBACK_FLAG_THRESHOLD,
    }


# ============================================================================
# All-channel diagnostic reporting (§3g)
# ============================================================================

def compute_all_channel_doses(
    hot_results: dict,
    reactive_results: dict,
) -> dict:
    """Report per-seed dose on all four canonical channels for hot and reactive.

    Only burn_decay has a pass/fail constraint (§5b); others reported for
    inspection + future-regime comparison per Sal 015 R4.
    """
    out = {}
    for ch in CANONICAL_CHANNELS:
        hd = compute_arm_dose(hot_results, ch, coherent_only=True)
        rd = compute_arm_dose(reactive_results, ch, coherent_only=True)
        out[ch] = {
            "hot_dose": hd,
            "reactive_dose": rd,
            "ratio": (rd / hd) if hd > 0 else None,
        }
    return out


# ============================================================================
# Main entry: analyze_phase_1_output
# ============================================================================

def _default_loader(output_dir: pathlib.Path, seed: int, arm: str) -> dict:
    path = output_dir / f"phase_1_seed_{seed}_arm_{arm}.pkl"
    with open(path, "rb") as f:
        return pickle.load(f)


def analyze_phase_1_output(
    output_dir: str | pathlib.Path,
    seed_pool: list[int],
    loader: Callable[[pathlib.Path, int, str], dict] | None = None,
    report_path: str | pathlib.Path | None = None,
) -> dict:
    """Run full Phase 5 analysis on Phase 1 compute output.

    Args:
      output_dir: directory containing per-seed per-arm pickles
      seed_pool: list of seeds in the Phase 1 pool
      loader: optional override; defaults to _default_loader
      report_path: optional path for JSON output; default writes alongside output_dir
    """
    output_dir = pathlib.Path(output_dir)
    loader = loader or _default_loader

    report: dict[str, Any] = {
        "schema_version": "phase_5_analysis_v1_2026-10-13",
        "seed_pool": list(seed_pool),
        "primary_threshold": PRIMARY_THRESHOLD_LOCKED,
        "dose_tolerance": DOSE_TOLERANCE,
        "per_seed": {},
    }

    # Pass 1: ratification + Case A/B + reactive dose per seed.
    hot_by_seed: dict[int, dict] = {}
    yoked_by_seed: dict[int, dict] = {}
    reactive_by_seed: dict[int, dict] = {}
    for seed in seed_pool:
        hot_r = loader(output_dir, seed, "hot")
        no_obs_r = loader(output_dir, seed, "no_obs")
        yoked_r = loader(output_dir, seed, "yoked")
        reactive_r = loader(output_dir, seed, "reactive")

        hot_by_seed[seed] = hot_r
        yoked_by_seed[seed] = yoked_r
        reactive_by_seed[seed] = reactive_r

        seed_rpt = {
            "ratification": ratify_seed(hot_r, no_obs_r),
            "reactive_dose": compute_reactive_dose_verdict(hot_r, reactive_r),
            "all_channel_doses": compute_all_channel_doses(hot_r, reactive_r),
            "fallback_rates": compute_fallback_rates(reactive_r, hot_r),
            "prediction_actual_gap": compute_prediction_actual_gap(hot_r),
        }
        report["per_seed"][seed] = seed_rpt

    # Pass 2: pooled source dose per channel (§5a sentinel).
    source_dose_pool = {}
    for ch in CANONICAL_CHANNELS:
        pool = compute_source_dose_pool(hot_by_seed, ch)
        source_dose_pool[ch] = SOURCE_DOSE_ZERO if pool == 0 else pool
    report["source_dose_pool"] = source_dose_pool

    # Pass 3: primary metric on COHERENCE-DECLARED subset.
    declared_seeds = [
        s for s in seed_pool
        if report["per_seed"][s]["ratification"]["bucket"] == "COHERENCE-DECLARED"
    ]
    # Further require reactive dose verdict to be PASS_RAW or PASS_SCALED for
    # hot−reactive inclusion. hot−yoked runs on all declared seeds.
    reactive_valid = [
        s for s in declared_seeds
        if report["per_seed"][s]["reactive_dose"]["final_verdict"] in ("PASS_RAW", "PASS_SCALED")
    ]
    report["declared_seeds"] = declared_seeds
    report["reactive_valid_seeds"] = reactive_valid

    hot_bis = [_burn_integral(hot_by_seed[s]) for s in declared_seeds]
    yoked_bis = [_burn_integral(yoked_by_seed[s]) for s in declared_seeds]
    reactive_bis = [_burn_integral(reactive_by_seed[s]) for s in declared_seeds]

    # Primary metric computed on seeds valid for the pairing (reactive seeds filtered
    # to the subset passing dose gate).
    reactive_valid_idx = [declared_seeds.index(s) for s in reactive_valid]
    hot_bis_for_hr = [hot_bis[i] for i in reactive_valid_idx]
    reactive_bis_for_hr = [reactive_bis[i] for i in reactive_valid_idx]
    yoked_bis_for_hr = [yoked_bis[i] for i in reactive_valid_idx]

    # Compute pooled hot−yoked on all declared seeds; hot−reactive on reactive_valid.
    # To expose both, run two passes: full for hv, reactive-valid for hr.
    primary_full = compute_primary_metric(hot_bis, yoked_bis, reactive_bis) \
                   if declared_seeds else {"n_seeds": 0}
    primary_rv = compute_primary_metric(hot_bis_for_hr, yoked_bis_for_hr, reactive_bis_for_hr) \
                 if reactive_valid else {"n_seeds": 0}

    report["primary_metric"] = {
        "declared_seeds": declared_seeds,
        "all_declared": primary_full,
        "reactive_valid_only": primary_rv,
    }

    # STRICT ratification pooled summary.
    strict_seeds = [s for s in seed_pool
                    if report["per_seed"][s]["ratification"]["bucket"] == "STRICT"]
    strict_fails = [s for s in strict_seeds
                    if report["per_seed"][s]["ratification"]["strict_verdict"] == "FAIL"]
    report["strict_ratification"] = {
        "strict_seeds": strict_seeds,
        "strict_fail_seeds": strict_fails,
        "any_strict_fail": bool(strict_fails),
        "note": "Any STRICT fail → canonical surface leak; investigate before pooling.",
    }

    # Flag flags.
    report["flagged_seeds_case_a"] = [
        s for s in seed_pool if report["per_seed"][s]["fallback_rates"]["flag_case_a"]
    ]
    report["flagged_seeds_case_b"] = [
        s for s in seed_pool if report["per_seed"][s]["fallback_rates"]["flag_case_b"]
    ]

    # Timestamp + save.
    report["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if report_path is None:
        report_path = output_dir / f"phase_5_analysis_{time.strftime('%Y%m%d_%H%M%S')}.json"
    report_path = pathlib.Path(report_path)
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


# ============================================================================
# CLI entry
# ============================================================================

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Phase 5 analysis — Crack seed Stage 2.")
    ap.add_argument("--output-dir", required=True,
                    help="Directory containing phase_1_seed_<N>_arm_<arm>.pkl files")
    ap.add_argument("--seed-pool", required=True,
                    help="Comma-separated list of seeds (e.g. '100,101,102,...')")
    ap.add_argument("--report-path", default=None,
                    help="Optional output JSON path (default: auto-named in output-dir)")
    args = ap.parse_args()

    seed_pool = [int(x) for x in args.seed_pool.split(",")]
    rpt = analyze_phase_1_output(args.output_dir, seed_pool, report_path=args.report_path)

    print(f"Phase 5 analysis complete. Report: {args.report_path or 'auto-named in output-dir'}")
    print(f"  seeds in pool: {len(seed_pool)}")
    print(f"  declared (coherence > {MIN_COHERENT_STEPS_FOR_DECLARATION}): {len(rpt['declared_seeds'])}")
    print(f"  reactive-dose-valid: {len(rpt['reactive_valid_seeds'])}")
    print(f"  strict fails: {len(rpt['strict_ratification']['strict_fail_seeds'])}")
    pm = rpt["primary_metric"]["reactive_valid_only"]
    if pm.get("n_seeds", 0) > 0:
        hv = pm["hot_minus_yoked"]
        hr = pm["hot_minus_reactive"]
        print(f"  hot−yoked:    mean={hv['mean']:+.2f}  CI95={hv['ci95']}  verdict={hv['verdict']}")
        print(f"  hot−reactive: mean={hr['mean']:+.2f}  CI95={hr['ci95']}  verdict={hr['verdict']}  TOST={hr['tost_equivalence_at_threshold']}")
        print(f"  architecture_claim: {pm['intersection_union']['architecture_claim_supported']}")
