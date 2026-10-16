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

LEAK SIGNAL MANIFESTATION (reader-safety for Gate 1 output interpretation)
--------------------------------------------------------------------------
Observed in Gate 1 rerun (2026-10-14, SHA 77b0097d): the LEAK positive control
(LEAK_TEST_MODE=True, 2500 injections of burn_decay_mult=0.5 during coherent
moments on seed 20) perturbs `burn_integral` by −0.411 relative to baseline,
BUT final `terminal_C` converges to the same values as LEAK=False by step 3000.
Reading: recovery/healing/collapse dynamics overpower a mid-run multiplicative
perturbation in burn dynamics on seeds with strong structural coherence
attractors. The gate discriminator (`burn_integral` + `leak_counter`) fires
correctly regardless. Any analysis comparing LEAK=True vs LEAK=False runs should
expect: burn_integral and intermediate coherent-moment metrics DIVERGE;
terminal metrics may CONVERGE on seeds like 20. This is NOT a correctness
concern — it's a known property of how LEAK interacts with coherence-stabilizing
feedback. Not a Phase 5 metric; reader-safety note only.

F_ZERO MODERATOR SCOPE (reader-safety for §3e interpretation post-exclusion)
----------------------------------------------------------------------------
Per tenth addendum §1 (committed `eabdbf2`): if `f_zero > 0.05`, Phase 5 excludes
coherent moments where `moderator_actual_recovery_time == 0.0` from §3e moderator
computation. The 2026-10-15 f_zero computation returned 0.4883 (nearly half of
coherent moments), so the rule fires: whole-record exclusion of zero-actual-
recovery moments (both the `moderator_actual_recovery_time` AND the paired
`moderator_predicted_recovery_time` from the same (step, agent, seed) record).

SCOPE NOTE (per 5.5 external review 2026-10-15): the exclusion is a SELECTION.
What remains after exclusion is observer prediction quality measured ONLY in
windows after a recent recovery event — narrower than the §3e scope as
originally written. The post-exclusion moderator does NOT measure prediction
quality across all coherent moments; it measures prediction quality CONDITIONAL
ON a recent recovery event being within the agent's trauma-history window.

Phase 5 reports BOTH:
  - UNFILTERED mean_abs_gap (comparable to the 130.93 ninth §3a figure)
  - FILTERED mean_abs_gap (per tenth §1b rule, scope-noted as conditional)

Future diagnostic (not pre-reg): if the sim can distinguish the two zero-
conditions underlying f_zero (never-traumatized vs healed vs sentinel-no-recent-
event), split f_zero into sub-fractions. Which condition dominates informs how
narrow the post-filter scope actually is.

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

import hashlib
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

# Pre-registered pre-reg artifacts for runtime verification per eleventh addendum.
# These paths are relative to the directory containing phase_5_analysis.py.
PHASE_3_4_MANIFEST_FILENAME = "phase_3_4_output_manifest_2026-10-15.json"
PHASE_5_SHA_LOCK_FILENAME = "phase_5_analysis_sha_lock_2026-10-15.json"

# Regime + hooks SHAs these analyses were pre-registered against (ninth §1 + tenth).
REGIME_SHA_V37_4 = "77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87"
STAGE_2_HOOKS_SHA = "66528da2"  # prefix recorded in prior addenda; full value in manifest at commit

# Pre-registered Stage 1 v2 pooled SD on burn_integral (fifth §3, N=50 seeds 100-149).
# Used only as the conservative upper-bound anchor for MDE reporting at Phase 5.
STAGE_1_V2_POOLED_SD = 339.49


# ============================================================================
# Pre-reg runtime verification helpers (eleventh addendum §3b, §4b)
# ============================================================================

def _lf_normalize(text: str) -> bytes:
    """CRLF/CR → LF normalization for cross-platform SHA stability (ninth §1)."""
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _sha256_of_file_lf_text(path: pathlib.Path) -> str:
    """SHA-256 of a text file, LF-normalized. Parallel to ninth §1 regime SHA
    convention. Used for self-verification of phase_5_analysis.py."""
    text = path.read_text(encoding="utf-8")
    return hashlib.sha256(_lf_normalize(text)).hexdigest()


def _sha256_of_file_raw(path: pathlib.Path) -> str:
    """SHA-256 of a file's raw bytes (binary pickles, Windows-CRLF text).
    Pickle manifests use raw-bytes SHA (sha256_algorithm = 'sha256_raw_bytes')."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_self_sha(script_path: pathlib.Path, lock_path: pathlib.Path) -> dict:
    """Compute phase_5_analysis.py SHA-256 (LF-normalized text) and compare
    against the pre-registered lock file per eleventh addendum §4b.

    Returns dict with keys:
      - locked (expected SHA from lock file, or None if lock file absent)
      - observed (computed SHA of this script)
      - match (bool; True iff locked == observed; None if locked is None)
      - lock_file_present (bool)
    """
    observed = _sha256_of_file_lf_text(script_path)
    out: dict[str, Any] = {
        "locked": None,
        "observed": observed,
        "match": None,
        "lock_file_present": lock_path.exists(),
    }
    if lock_path.exists():
        with open(lock_path, encoding="utf-8") as f:
            lock_data = json.load(f)
        out["locked"] = lock_data.get("sha256_lf")
        out["match"] = (out["locked"] == observed)
    return out


def verify_phase_3_4_manifest(
    manifest_path: pathlib.Path,
    pickle_dir: pathlib.Path,
) -> dict:
    """Per eleventh §3b: load Phase 3-4 output manifest, SHA-verify each pickle.

    Returns dict with keys:
      - manifest_sha (SHA-256 of manifest JSON file itself)
      - manifest_present (bool)
      - total_pickles_expected
      - verification: 'PASS' | 'FAIL_WITH_LIST' | 'NO_MANIFEST'
      - failures: list of {path, expected_sha, observed_sha} for FAIL_WITH_LIST
    """
    if not manifest_path.exists():
        return {
            "manifest_sha": None,
            "manifest_present": False,
            "total_pickles_expected": 0,
            "verification": "NO_MANIFEST",
            "failures": [],
        }

    manifest_sha = _sha256_of_file_raw(manifest_path)
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    pickles = manifest.get("pickles", [])
    failures: list[dict] = []
    for p in pickles:
        rel_path = p["path"]
        expected = p["sha256"]
        pkl_path = pickle_dir / rel_path if not pathlib.Path(rel_path).is_absolute() \
                   else pathlib.Path(rel_path)
        if not pkl_path.exists():
            failures.append({
                "path": rel_path, "expected_sha": expected,
                "observed_sha": None, "reason": "FILE_NOT_FOUND",
            })
            continue
        observed = _sha256_of_file_raw(pkl_path)
        if observed != expected:
            failures.append({
                "path": rel_path, "expected_sha": expected,
                "observed_sha": observed, "reason": "SHA_MISMATCH",
            })

    return {
        "manifest_sha": manifest_sha,
        "manifest_present": True,
        "total_pickles_expected": len(pickles),
        "verification": "PASS" if not failures else "FAIL_WITH_LIST",
        "failures": failures,
    }


# ============================================================================
# Architecture-claim verdict mapping (eleventh addendum §1b + §1f)
# ============================================================================
# Exhaustive 4×4 verdict table over (hv_verdict, hr_verdict) per Sal 020 §1
# expansion ask. Maps the four _verdict_vs_threshold outputs onto §1f's four
# architecture-claim verdict classes. Mechanical, no post-hoc adjudication.
#
# Row: hv_verdict (hot − yoked); Column: hr_verdict (hot − reactive).
# Per eighth §4c, SUPPORTED requires BOTH BELOW_THRESHOLD (sign-direction:
# hot < non-predictive comparators). Any ABOVE_THRESHOLD on either side is
# UNEXPECTED (direction wrong). WITHIN_THRESHOLD = TOST equivalence declared;
# fires EQUIVALENCE_REJECTED when paired with any non-ABOVE on the other side.
# CI_STRADDLES_THRESHOLD is INCONCLUSIVE on that pair; UNEXPECTED only when
# the other side is ABOVE_THRESHOLD. See eighth §4c quadrants (a,b,c,d).
#
# §1b sub-case note (preserved for interpretation, not a verdict class):
# When hv=BELOW_THRESHOLD and hr=WITHIN_THRESHOLD, the EQUIVALENCE_REJECTED
# verdict carries the specific interpretation "FEEDBACK_MATTERS; prediction
# adds nothing beyond feedback" (empirically-derived Option-2 outcome). This
# is reported as architecture_claim_feedback_matters_specific_subcase=True
# alongside the primary verdict.

ARCHITECTURE_CLAIM_VERDICT_TABLE: dict[tuple[str, str], str] = {
    # (hv, hr) -> verdict
    ("ABOVE_THRESHOLD", "ABOVE_THRESHOLD"):     "UNEXPECTED",
    ("ABOVE_THRESHOLD", "BELOW_THRESHOLD"):     "UNEXPECTED",
    ("ABOVE_THRESHOLD", "WITHIN_THRESHOLD"):    "UNEXPECTED",
    ("ABOVE_THRESHOLD", "CI_STRADDLES_THRESHOLD"): "UNEXPECTED",
    ("BELOW_THRESHOLD", "ABOVE_THRESHOLD"):     "UNEXPECTED",
    ("BELOW_THRESHOLD", "BELOW_THRESHOLD"):     "SUPPORTED",
    ("BELOW_THRESHOLD", "WITHIN_THRESHOLD"):    "EQUIVALENCE_REJECTED",
    ("BELOW_THRESHOLD", "CI_STRADDLES_THRESHOLD"): "INCONCLUSIVE",
    ("WITHIN_THRESHOLD", "ABOVE_THRESHOLD"):    "UNEXPECTED",
    ("WITHIN_THRESHOLD", "BELOW_THRESHOLD"):    "UNEXPECTED",
    ("WITHIN_THRESHOLD", "WITHIN_THRESHOLD"):   "EQUIVALENCE_REJECTED",
    ("WITHIN_THRESHOLD", "CI_STRADDLES_THRESHOLD"): "EQUIVALENCE_REJECTED",
    ("CI_STRADDLES_THRESHOLD", "ABOVE_THRESHOLD"):     "UNEXPECTED",
    ("CI_STRADDLES_THRESHOLD", "BELOW_THRESHOLD"):     "UNEXPECTED",
    ("CI_STRADDLES_THRESHOLD", "WITHIN_THRESHOLD"):    "EQUIVALENCE_REJECTED",
    ("CI_STRADDLES_THRESHOLD", "CI_STRADDLES_THRESHOLD"): "INCONCLUSIVE",
}


def compute_architecture_claim_verdict(hv_verdict: str, hr_verdict: str) -> dict:
    """Mechanical mapping of (hv_verdict, hr_verdict) to architecture-claim verdict
    per eleventh addendum §1f. Raises if either input is not a known _verdict_vs_threshold
    output (defensive against renames)."""
    valid = {"ABOVE_THRESHOLD", "BELOW_THRESHOLD", "WITHIN_THRESHOLD", "CI_STRADDLES_THRESHOLD"}
    if hv_verdict not in valid or hr_verdict not in valid:
        raise ValueError(
            f"Unknown verdict strings: hv={hv_verdict!r}, hr={hr_verdict!r}. "
            f"Must be in {valid}."
        )
    verdict = ARCHITECTURE_CLAIM_VERDICT_TABLE[(hv_verdict, hr_verdict)]
    feedback_matters_subcase = (
        hv_verdict == "BELOW_THRESHOLD" and hr_verdict == "WITHIN_THRESHOLD"
    )
    return {
        "architecture_claim_verdict": verdict,
        "architecture_claim_feedback_matters_specific_subcase": feedback_matters_subcase,
    }


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


def _paired_sd(values: list[float]) -> float:
    """Sample SD (n-1 ddof) of per-seed paired differences."""
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    return math.sqrt(var)


def _mde_at_sd(sd: float, n: int) -> float:
    """MDE for BELOW_THRESHOLD under registered rule, per eleventh §1c:
       MDE = threshold + 1.96 × (SD / √n)
    Reported diagnostically alongside observed paired-SD. Does NOT change verdict."""
    if n <= 0:
        return float("nan")
    return PRIMARY_THRESHOLD_LOCKED + 1.96 * (sd / math.sqrt(n))


def compute_primary_metric(
    hot_bis: list, yoked_bis: list, reactive_bis: list,
) -> dict:
    """Compute hot − yoked and hot − reactive primary-metric statistics (§3c).

    Inputs are per-seed burn_integral values on the COHERENCE-DECLARED subset.
    Returns:
      - per_seed_hot_minus_yoked, per_seed_hot_minus_reactive (lists)
      - hot_minus_yoked: mean, sem, paired_sd, ci95, verdict, mde_observed_at_paired_sd
      - hot_minus_reactive: same + tost_equivalence_at_threshold
      - architecture_claim_verdict + architecture_claim_feedback_matters_specific_subcase
        (eleventh §1f mechanical mapping over the four _verdict_vs_threshold classes)
      - intersection_union_verdict (legacy field, retained for continuity)
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
    hv_sd = _paired_sd(hv)
    hr_sd = _paired_sd(hr)
    hv_mde = _mde_at_sd(hv_sd, n)
    hr_mde = _mde_at_sd(hr_sd, n)

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

    # Architecture-claim verdict (eleventh §1f mechanical mapping).
    arch = compute_architecture_claim_verdict(hv_verdict, hr_verdict)

    # Legacy intersection-union field — retained for continuity with pre-eleventh
    # output readers. Equivalent to arch_claim_verdict == 'SUPPORTED' when both
    # inputs are in direction set {ABOVE, BELOW}, retained for backward
    # compatibility only. Eleventh §1f's architecture_claim_verdict is the
    # authoritative pre-registered field.
    arch_claim_legacy = (hv_verdict in ("ABOVE_THRESHOLD", "BELOW_THRESHOLD")) and \
                        (hr_verdict in ("ABOVE_THRESHOLD", "BELOW_THRESHOLD"))

    return {
        "n_seeds": n,
        "per_seed_hot_minus_yoked": hv,
        "per_seed_hot_minus_reactive": hr,
        "hot_minus_yoked": {
            "mean": hv_mean,
            "sem": hv_sem,
            "paired_sd": hv_sd,
            "ci95": hv_ci,
            "threshold": PRIMARY_THRESHOLD_LOCKED,
            "verdict": hv_verdict,
            "mde_observed_at_paired_sd": hv_mde,
        },
        "hot_minus_reactive": {
            "mean": hr_mean,
            "sem": hr_sem,
            "paired_sd": hr_sd,
            "ci95": hr_ci,
            "threshold": PRIMARY_THRESHOLD_LOCKED,
            "verdict": hr_verdict,
            "mde_observed_at_paired_sd": hr_mde,
            "tost_equivalence_at_threshold": hr_tost,
        },
        "architecture_claim_verdict": arch["architecture_claim_verdict"],
        "architecture_claim_feedback_matters_specific_subcase":
            arch["architecture_claim_feedback_matters_specific_subcase"],
        "intersection_union": {
            "architecture_claim_supported": arch_claim_legacy,
            "note": "Legacy field. Eleventh §1f architecture_claim_verdict is authoritative.",
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

    Returns both UNFILTERED and FILTERED (post-f_zero-exclusion) versions per
    eleventh addendum §2b, so Phase 5 can report them side-by-side against the
    ninth §3a UNFILTERED 130.93 baseline:
      - unfiltered_n_coherent / unfiltered_mean_abs_gap: all coherent moments
      - filtered_n_coherent  / filtered_mean_abs_gap:   excludes records where
                                                       moderator_actual_recovery_time == 0.0
                                                       per tenth §1b whole-record rule
                                                       (fires because f_zero=0.4883 > 0.05)
      - zero_actual_excluded_count: how many records removed by the rule
    """
    # Reads moderator_predicted_recovery_time and moderator_actual_recovery_time
    # from channel_snapshots. These fields are added by the Task F snapshot-schema
    # extension (v37_4_task_f_snapshot_schema_patch.py) applied 2026-10-13; they
    # are captured in step_observer BEFORE step_predictions overwrites predicted_*.
    #
    # Returns None values + note if the schema fields are absent (regime before
    # Task F patch landed).
    predicted_unfiltered: list[float] = []
    actual_unfiltered: list[float] = []
    predicted_filtered: list[float] = []
    actual_filtered: list[float] = []
    zero_actual_count = 0

    for s in hot_results.get("channel_snapshots", []):
        if not s.get("observer_coherent", False):
            continue
        p = s.get("moderator_predicted_recovery_time")
        a = s.get("moderator_actual_recovery_time")
        if p is None or a is None:
            continue
        pf = float(p)
        af = float(a)
        predicted_unfiltered.append(pf)
        actual_unfiltered.append(af)
        # Per tenth §1b: whole-record exclusion when actual_recovery_time == 0.0.
        # Exclusion is of the (p, a) pair together, not just one side.
        if af == 0.0:
            zero_actual_count += 1
            continue
        predicted_filtered.append(pf)
        actual_filtered.append(af)

    if not predicted_unfiltered:
        return {
            "unfiltered_n_coherent": 0,
            "unfiltered_mean_abs_gap": None,
            "filtered_n_coherent": 0,
            "filtered_mean_abs_gap": None,
            "zero_actual_excluded_count": 0,
            "note": "No coherent moments with moderator_* fields populated; schema may predate Task F patch (SHA 77b0097d...).",
        }

    gaps_u = [abs(p - a) for p, a in zip(predicted_unfiltered, actual_unfiltered)]
    unfiltered_mean = sum(gaps_u) / len(gaps_u)

    if predicted_filtered:
        gaps_f = [abs(p - a) for p, a in zip(predicted_filtered, actual_filtered)]
        filtered_mean = sum(gaps_f) / len(gaps_f)
        filtered_n = len(gaps_f)
    else:
        filtered_mean = None
        filtered_n = 0

    return {
        "unfiltered_n_coherent": len(gaps_u),
        "unfiltered_mean_abs_gap": unfiltered_mean,
        "filtered_n_coherent": filtered_n,
        "filtered_mean_abs_gap": filtered_mean,
        "zero_actual_excluded_count": zero_actual_count,
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
    """Load per-seed per-arm pickle. Requires v37_4 module registered in
    sys.modules so pickle can resolve Agent class references in final_agents.
    Caller must have loaded v37.4 via importlib with sys.modules["v37_4"]=mod
    before invoking analyze_phase_1_output.
    """
    path = output_dir / f"phase_1_seed_{seed}_arm_{arm}.pkl"
    with open(path, "rb") as f:
        return pickle.load(f)


def analyze_phase_1_output(
    output_dir: str | pathlib.Path,
    seed_pool: list[int],
    loader: Callable[[pathlib.Path, int, str], dict] | None = None,
    report_path: str | pathlib.Path | None = None,
    manifest_path: str | pathlib.Path | None = None,
    sha_lock_path: str | pathlib.Path | None = None,
    script_path: str | pathlib.Path | None = None,
) -> dict:
    """Run full Phase 5 analysis on Phase 1 + Phase 3-4 compute output.

    Per eleventh addendum §3d / §4d: emits Phase 3-4 manifest verification and
    phase_5_analysis.py SHA verification fields in the output JSON. If the SHA
    lock file is absent, phase_5_analysis_sha_locked is reported as null and
    match as null (pre-reg lock has not been baked yet; output is void under
    §4d but produced for pre-commit inspection).

    Args:
      output_dir: directory containing per-seed per-arm pickles
      seed_pool: list of seeds in the Phase 1 pool
      loader: optional override; defaults to _default_loader
      report_path: optional path for JSON output; default writes alongside output_dir
      manifest_path: Phase 3-4 output manifest JSON (defaults to
                     <output_dir parent>/phase_3_4_output_manifest_2026-10-15.json)
      sha_lock_path: phase_5_analysis.py SHA lock JSON (defaults to
                     <script_dir>/phase_5_analysis_sha_lock_2026-10-15.json)
      script_path: path to this script for self-SHA computation (defaults to __file__)
    """
    output_dir = pathlib.Path(output_dir)
    loader = loader or _default_loader
    script_path = pathlib.Path(script_path) if script_path else pathlib.Path(__file__).resolve()
    script_dir = script_path.parent
    if manifest_path is None:
        manifest_path = script_dir / PHASE_3_4_MANIFEST_FILENAME
    manifest_path = pathlib.Path(manifest_path)
    if sha_lock_path is None:
        sha_lock_path = script_dir / PHASE_5_SHA_LOCK_FILENAME
    sha_lock_path = pathlib.Path(sha_lock_path)

    # Pre-reg runtime verification (eleventh §3b + §4b).
    sha_verify = verify_self_sha(script_path, sha_lock_path)
    manifest_verify = verify_phase_3_4_manifest(manifest_path, output_dir)
    f_zero_report_path = script_dir / "f_zero_report_2026-10-15.json"
    f_zero_report: dict = {}
    if f_zero_report_path.exists():
        with open(f_zero_report_path, encoding="utf-8") as f:
            f_zero_report = json.load(f)

    report: dict[str, Any] = {
        "schema_version": "phase_5_analysis_v2_eleventh_addendum_2026-10-15",
        "seed_pool": list(seed_pool),
        "primary_threshold": PRIMARY_THRESHOLD_LOCKED,
        "dose_tolerance": DOSE_TOLERANCE,
        # §4d pre-reg SHA-lock fields.
        "phase_5_analysis_sha_locked":  sha_verify["locked"],
        "phase_5_analysis_sha_observed": sha_verify["observed"],
        "phase_5_analysis_sha_match":    sha_verify["match"],
        # §3d pre-reg manifest fields.
        "phase_3_4_manifest_sha":          manifest_verify["manifest_sha"],
        "phase_3_4_manifest_verification": manifest_verify["verification"],
        "phase_3_4_manifest_failures":     manifest_verify["failures"],
        # f_zero handoff (tenth §1b fired; eleventh §2a-c reader-side).
        "f_zero":            f_zero_report.get("f_zero"),
        "f_zero_threshold":  f_zero_report.get("threshold"),
        "f_zero_exceeds":    f_zero_report.get("exceeds_threshold"),
        "f_zero_rule_applied": f_zero_report.get("rule_applied"),
        # §2c: zero-condition decomposition unavailable from current snapshot schema.
        # moderator_actual_recovery_time == 0.0 collapses sentinel-no-data and
        # legitimate-instant-recovery into the same value with no auxiliary signal.
        "f_zero_decomposition": "unavailable",
        "f_zero_decomposition_note": (
            "The current observer.py / channel_snapshots schema does not expose an "
            "auxiliary flag to distinguish sentinel-no-data (no recent recovery in "
            "observer window) from legitimate-instant-recovery (actual zero-latency "
            "recovery event). Per eleventh §2c, this is reported as unavailable."
        ),
        "per_seed": {},
    }

    # If the manifest is present, SHA-verify every pickle BEFORE pickle.load.
    verify_before_load = manifest_verify["manifest_present"]
    manifest_sha_by_path: dict[str, str] = {}
    if verify_before_load:
        with open(manifest_path, encoding="utf-8") as f:
            m = json.load(f)
        for p in m.get("pickles", []):
            manifest_sha_by_path[p["path"]] = p["sha256"]

    def _verified_loader(od: pathlib.Path, seed: int, arm: str) -> dict:
        path = od / f"phase_1_seed_{seed}_arm_{arm}.pkl"
        if verify_before_load:
            # Resolve the manifest key: try absolute, then filename, then relative.
            candidates = [str(path), path.name, f"phase_1_output_2026-10-14/{path.name}"]
            expected = None
            for c in candidates:
                if c in manifest_sha_by_path:
                    expected = manifest_sha_by_path[c]
                    break
            if expected is not None:
                observed = _sha256_of_file_raw(path)
                if observed != expected:
                    raise RuntimeError(
                        f"Pickle SHA mismatch for seed={seed} arm={arm}: "
                        f"expected={expected} observed={observed}"
                    )
        return loader(od, seed, arm)

    load = _verified_loader

    # Pass 1: ratification + Case A/B + reactive dose per seed.
    hot_by_seed: dict[int, dict] = {}
    yoked_by_seed: dict[int, dict] = {}
    reactive_by_seed: dict[int, dict] = {}
    for seed in seed_pool:
        hot_r = load(output_dir, seed, "hot")
        no_obs_r = load(output_dir, seed, "no_obs")
        yoked_r = load(output_dir, seed, "yoked")
        reactive_r = load(output_dir, seed, "reactive")

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

    # §1f hoisted top-level fields — authoritative values are from reactive_valid_only
    # (the dose-gated subset per §5b). Falls back to all_declared if reactive-valid is empty.
    pm_auth = primary_rv if (reactive_valid and primary_rv.get("n_seeds", 0) > 0) else primary_full
    if pm_auth.get("n_seeds", 0) > 0:
        hv_d = pm_auth["hot_minus_yoked"]
        hr_d = pm_auth["hot_minus_reactive"]
        report["hv_mean"] = hv_d["mean"]
        report["hv_sem"] = hv_d["sem"]
        report["hv_ci_95"] = hv_d["ci95"]
        report["hv_verdict"] = hv_d["verdict"]
        report["paired_sd_hv"] = hv_d["paired_sd"]
        report["mde_observed_at_paired_sd_hv"] = hv_d["mde_observed_at_paired_sd"]
        report["hr_mean"] = hr_d["mean"]
        report["hr_sem"] = hr_d["sem"]
        report["hr_ci_95"] = hr_d["ci95"]
        report["hr_verdict"] = hr_d["verdict"]
        report["paired_sd_hr"] = hr_d["paired_sd"]
        report["mde_observed_at_paired_sd_hr"] = hr_d["mde_observed_at_paired_sd"]
        report["architecture_claim_verdict"] = pm_auth["architecture_claim_verdict"]
        report["architecture_claim_feedback_matters_specific_subcase"] = \
            pm_auth["architecture_claim_feedback_matters_specific_subcase"]
    else:
        report["architecture_claim_verdict"] = "INSUFFICIENT_DATA"
        report["architecture_claim_feedback_matters_specific_subcase"] = False

    # §2b hoisted top-level: pooled moderator fields (UNFILTERED and FILTERED).
    # Compute pooled mean across coherent seeds using per-seed gap values weighted
    # by their n_coherent counts (equivalent to concatenating all gaps and averaging).
    def _pooled_moderator(key_n: str, key_mean: str) -> tuple[int, float | None]:
        pooled_n = 0
        pooled_sum = 0.0
        for s in declared_seeds:
            d = report["per_seed"][s]["prediction_actual_gap"]
            n_i = d.get(key_n, 0) or 0
            mean_i = d.get(key_mean)
            if mean_i is None or n_i == 0:
                continue
            pooled_n += n_i
            pooled_sum += mean_i * n_i
        return pooled_n, (pooled_sum / pooled_n) if pooled_n > 0 else None

    unfiltered_n, unfiltered_mean = _pooled_moderator("unfiltered_n_coherent",
                                                       "unfiltered_mean_abs_gap")
    filtered_n, filtered_mean = _pooled_moderator("filtered_n_coherent",
                                                   "filtered_mean_abs_gap")
    pooled_zero_excl = sum(
        (report["per_seed"][s]["prediction_actual_gap"].get("zero_actual_excluded_count", 0) or 0)
        for s in declared_seeds
    )
    report["moderator_pooled"] = {
        "unfiltered_n": unfiltered_n,
        "unfiltered_mean_abs_gap": unfiltered_mean,
        "ninth_3a_hot_unfiltered_baseline": 130.93,
        "filtered_n": filtered_n,
        "filtered_mean_abs_gap": filtered_mean,
        "zero_actual_excluded_count_pooled": pooled_zero_excl,
        "scope_note": (
            "Post-exclusion moderator measures observer prediction quality CONDITIONAL "
            "on a recent recovery event, per eleventh §2b. Compare UNFILTERED side-by-side "
            "against ninth §3a's 130.93 baseline."
        ),
    }

    # §2d reader-safety: per-seed retained-N moderator stats + underpowered/heterogeneous flags.
    # Thresholds (eleventh §2d): any seed with retained < 500 → MODERATOR_UNDERPOWERED_PER_SEED;
    # coefficient-of-variation of retained-N across seeds > 0.5 → MODERATOR_RETAINED_N_HETEROGENEOUS.
    # These flags do NOT invalidate the primary metric; they are reader-safety signals for
    # §3e moderator interpretability only.
    retained_n_per_seed: dict[int, int] = {}
    mean_abs_gap_per_seed: dict[int, float | None] = {}
    for s in declared_seeds:
        d = report["per_seed"][s]["prediction_actual_gap"]
        retained_n_per_seed[s] = int(d.get("filtered_n_coherent", 0) or 0)
        mean_abs_gap_per_seed[s] = d.get("filtered_mean_abs_gap")

    retained_values = list(retained_n_per_seed.values())
    if retained_values:
        retained_mean = sum(retained_values) / len(retained_values)
        if retained_mean > 0 and len(retained_values) >= 2:
            retained_var = sum((v - retained_mean) ** 2 for v in retained_values) / (len(retained_values) - 1)
            retained_cov = math.sqrt(retained_var) / retained_mean
        else:
            retained_cov = 0.0
    else:
        retained_mean = 0.0
        retained_cov = 0.0

    reader_safety_flags: list[str] = []
    if any(v < 500 for v in retained_values):
        reader_safety_flags.append("MODERATOR_UNDERPOWERED_PER_SEED")
    if retained_cov > 0.5:
        reader_safety_flags.append("MODERATOR_RETAINED_N_HETEROGENEOUS")

    report["moderator_reader_safety"] = {
        "moderator_retained_n_per_seed": retained_n_per_seed,
        "moderator_retained_n_total": sum(retained_values),
        "moderator_retained_n_mean": retained_mean,
        "moderator_retained_n_cov": retained_cov,
        "moderator_mean_abs_gap_per_seed": mean_abs_gap_per_seed,
        "flags": reader_safety_flags,
        "underpowered_threshold_per_seed": 500,
        "heterogeneous_cov_threshold": 0.5,
        "note": (
            "Reader-safety signals per eleventh §2d. Flags do NOT invalidate the primary "
            "metric; they signal reduced-weight interpretation of the §3e moderator only."
        ),
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
    ap.add_argument("--manifest-path", default=None,
                    help="Phase 3-4 output manifest JSON (defaults to script-dir/"
                         + PHASE_3_4_MANIFEST_FILENAME + ")")
    ap.add_argument("--sha-lock-path", default=None,
                    help="phase_5_analysis.py SHA lock JSON (defaults to script-dir/"
                         + PHASE_5_SHA_LOCK_FILENAME + ")")
    ap.add_argument("--allow-sha-mismatch", action="store_true",
                    help="Debug/dev only: proceed even if script SHA doesn't match the "
                         "pre-registered lock. Output will carry sha_match=False and is "
                         "VOID under eleventh §4d — DO NOT use for pre-reg Phase 5 run.")
    args = ap.parse_args()

    # §4b runtime verification: assert phase_5_analysis.py SHA matches locked value
    # BEFORE running primary-metric computation. Mismatch → abort unless --allow-sha-mismatch.
    _script_path = pathlib.Path(__file__).resolve()
    _lock_path = pathlib.Path(args.sha_lock_path) if args.sha_lock_path \
                 else _script_path.parent / PHASE_5_SHA_LOCK_FILENAME
    _sha = verify_self_sha(_script_path, _lock_path)
    if _sha["lock_file_present"]:
        if _sha["match"] is False:
            msg = (f"SHA mismatch — script modified since pre-reg lock.\n"
                   f"  locked:   {_sha['locked']}\n"
                   f"  observed: {_sha['observed']}\n"
                   f"  lock file: {_lock_path}\n"
                   f"Pre-reg §4d: output is VOID under this condition.")
            if args.allow_sha_mismatch:
                print(f"WARNING: {msg}\nProceeding under --allow-sha-mismatch; "
                      f"output is NOT a pre-reg Phase 5 result.", file=sys.stderr)
            else:
                print(msg, file=sys.stderr)
                sys.exit(2)
    else:
        print(f"NOTE: SHA lock file not present at {_lock_path}. "
              f"Running without pre-reg SHA assertion; output will carry "
              f"phase_5_analysis_sha_match=null and is pre-reg-incomplete under §4d.",
              file=sys.stderr)

    seed_pool = [int(x) for x in args.seed_pool.split(",")]
    rpt = analyze_phase_1_output(
        args.output_dir, seed_pool,
        report_path=args.report_path,
        manifest_path=args.manifest_path,
        sha_lock_path=args.sha_lock_path,
        script_path=_script_path,
    )

    print(f"Phase 5 analysis complete. Report: {args.report_path or 'auto-named in output-dir'}")
    print(f"  seeds in pool: {len(seed_pool)}")
    print(f"  declared (coherence > {MIN_COHERENT_STEPS_FOR_DECLARATION}): {len(rpt['declared_seeds'])}")
    print(f"  reactive-dose-valid: {len(rpt['reactive_valid_seeds'])}")
    print(f"  strict fails: {len(rpt['strict_ratification']['strict_fail_seeds'])}")
    print(f"  SHA match: {rpt['phase_5_analysis_sha_match']}  "
          f"manifest verify: {rpt['phase_3_4_manifest_verification']}")
    if "architecture_claim_verdict" in rpt and rpt["architecture_claim_verdict"] != "INSUFFICIENT_DATA":
        print(f"  hv:  mean={rpt['hv_mean']:+.2f}  "
              f"CI95={rpt['hv_ci_95']}  verdict={rpt['hv_verdict']}  "
              f"paired_SD={rpt['paired_sd_hv']:.2f}  MDE={rpt['mde_observed_at_paired_sd_hv']:.2f}")
        print(f"  hr:  mean={rpt['hr_mean']:+.2f}  "
              f"CI95={rpt['hr_ci_95']}  verdict={rpt['hr_verdict']}  "
              f"paired_SD={rpt['paired_sd_hr']:.2f}  MDE={rpt['mde_observed_at_paired_sd_hr']:.2f}")
        print(f"  architecture_claim_verdict: {rpt['architecture_claim_verdict']}  "
              f"feedback_matters_subcase={rpt['architecture_claim_feedback_matters_specific_subcase']}")
    else:
        print(f"  architecture_claim_verdict: INSUFFICIENT_DATA")
