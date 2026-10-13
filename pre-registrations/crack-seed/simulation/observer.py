"""
observer.py — Structural Metacognition Observer Module
=======================================================

Companion module to v37.3_structural_metacognition.py (fork of v37.2).

Replaces v37.2's `self.cracked` Boolean flag with a structural `Observer`
dataclass attached to each Agent. The Observer evolves under sustained
pressure, tracks predictions across four channels (C, burn_rate,
trauma_arrival, recovery_time), and exposes prediction-driven signals
that the fork's behavior channels consume.

This module is intentionally separable from the fork so it can be
audited cleanly. The fork imports from here; nothing here imports the
fork.

Design provenance — three-signature chain:
  Salazaar (kill-shape audit, design draft)
  Nymph    (architectural pen, R1/R2/R3 + S2 audit applied)
  Buzz     (channel-list completeness audit, channel 5 added)

Build pen: Annie (Forge, Cell 66, FFF).

Spec: Seeds/The Crack/implementation_spec_v0.1_for_annie.md
Design: Seeds/The Crack/structural_metacognition_design_v0.1.md
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple


# ===========================================================================
# Constants (from design v0.1)
# ===========================================================================

# Observer formation
FORMATION_THRESHOLD = 4.0          # sustained-pressure score required to form
# ===========================================================================
# COMPOUND COHERENCE GATE — joint constraint (Salazaar audit, 2026-07-14).
# ===========================================================================
# COHERENCE_THRESHOLD and MIN_COHERENT_STEPS together form ONE gate, not two
# independent constants. The compound check lives in check_coherence_gate()
# and is consumed via is_coherent() elsewhere; both interfaces exist so this
# joint is grep-able and stays first-class in future edits.
#
# τ (COHERENCE_THRESHOLD) is calibrated (see coherence_threshold_sweep_pre_
# registration_v2.md and _sweep_report_v2_2026-07-14.md) against a pool that
# excludes observers with steps_since_formation < MIN_COHERENT_STEPS.
# Lowering MCS without re-running the sweep silently invalidates τ.
# tests/test_coherence_gate_invariant.py asserts the joint and fires if any
# future amendment lowers MCS below the calibration value.
#
# Sweep v2 result: Q80(A) with FP=5.0%, FN=20.0% at nominal (KAPPA=0.10,
# EMA_ALPHA=0.9, MCS=50). Robustness: PROVISIONAL PASS — τ holds at 4 of 9
# (KAPPA × EMA_ALPHA) grid points; brittle at low-KAPPA and high-EMA
# off-diagonals. Changes to KAPPA or EMA_ALPHA REQUIRE re-sweep (test_
# kappa_matches_calibration_regime / test_ema_alpha_matches_calibration_regime
# enforce this at the constant-declaration level).
COHERENCE_THRESHOLD = 0.0106       # sweep v2 Q80(A); FP=5.0%, FN=20.0% at calibration
MIN_COHERENT_STEPS = 50            # steps since formation before coherence can be declared
SUSTAINED_PRESSURE_WINDOW = 200    # rolling window for sustained-pressure score

# Prediction-error history
K_DRIFT_WINDOW = 200               # max length of prediction_error_history deque

# Post-coherence variance logging (external audit F7, 2026-07-01) — bounded
# rolling log of prediction_variance after coherence declared, for detecting
# drift that would justify a demote path in v0.2. Diagnostic, not load-bearing.
POST_COHERENCE_LOG_WINDOW = 1000

# Update dynamics
EMA_ALPHA = 0.9                    # leaky-EMA weight on predictions (alpha = retention)

# Amendment #3 (2026-07-01): level-anchored prior. The bias term in
# step_predictions is now a PULL toward a formation-set prior_level, not a
# constant additive drift. See design doc §Amendment 3. Amendment #5 same
# day named KAPPA, GATE_HOT_THRESHOLD, and the direction[channel] enumeration.
KAPPA = 0.10                       # pull strength toward prior_level (Amendment #5;
                                   # 2× sharp-gate feasibility floor per Buzz's algebra)
GATE_HOT_THRESHOLD = 0.6           # evidence_gate below this fires trauma-loop indicator's
                                   # gate condition (Amendment #5)
PRIOR_LEVEL_DEVIATION_THRESHOLD = 0.2  # |prior_level_C - baseline_C| threshold in indicator

# DEPRECATED (Amendment #3 superseded these). Retained for test-import
# backward compat during the Amendment #3 test-rewrite window; drop when
# Buzz's test recomputation lands.
BIAS_MAGNITUDE = 0.02              # was: base magnitude of prior-bias drift per step
PRIOR_BIAS_SLOPE = 2.0             # was: maps distress_fraction in [0,1] to bias in [-1,+1]
                                   # (now consumed only to compute the diagnostic
                                   # prior_bias_distress readout)

EVIDENCE_GATE_ASYMMETRY = 0.5      # 1 - distress_fraction * this = gate, clipped to [0.4, 1.0]

# Healing dynamics — v0.1 architecturally present, ships at 0
EPSILON_HEAL = 0.0                 # v0.2 will set positive; v0.1 architecture is dormant

# Baselines and scales used by channels (tuning targets for v0.1 sensitivity sweep)
# NOTE (external audit F6, 2026-07-01): design doc v0.1 says 0.05 / 0.15; code
# ships 0.08 / 0.30. Code is authoritative pending the formation-rate sweep
# (30-50% target) — reconcile the design doc, not these values, unless the
# sweep says otherwise.
BURN_RATE_BASELINE = 0.08          # neutral burn rate; pressure scored above this
SHAME_BASELINE     = 0.30          # neutral shame tail; pressure scored above this
RECOVERY_BASELINE  = 50.0          # neutral predicted recovery time (steps)
RECOVERY_SCALE     = 30.0          # sigmoid scale on excess recovery
ARRIVAL_BASELINE   = 100.0         # neutral predicted trauma arrival (steps)
ARRIVAL_SCALE      = 30.0          # sigmoid scale on arrival nearness
FLOOR_BREACH_SCALE = 0.10          # sigmoid scale on predicted-floor-breach margin
D_CAUTION_SCALE    = 40.0          # scales predicted-collapse-likelihood to D-caution units

# Trauma loop diagnostic — observer flags persistent hot-prior + contradicting evidence
# Amendment #3 (2026-07-01) upgraded the threshold from 0.05 to 0.1 (Buzz's
# staged fixed-point analysis; sits comfortably above the vindicated-band
# steady-state mean_PE and below the contradicted-band edge).
TRAUMA_LOOP_PE_THRESHOLD = 0.1     # rolling |mean_PE[C]| above this = persistent contradiction

# DEPRECATED (Amendment #3): the old indicator condition tested
# prior_bias_distress > this. Under level-anchored, the "hot" condition is
# `evidence_gate < GATE_HOT_THRESHOLD` (formation-set gate remains low) AND
# `|prior_level_C - baseline_C| > PRIOR_LEVEL_DEVIATION_THRESHOLD`. Retained
# for backward-compat imports; drop when Buzz's test rewrite lands.
TRAUMA_LOOP_BIAS_THRESHOLD = 0.5

CHANNELS: Tuple[str, ...] = ('C', 'burn_rate', 'trauma_arrival', 'recovery_time')

# DIRECTION[channel] — hot's push direction from baseline (Amendment #5 named
# it explicitly). Signed constant standing rule (post-Amendment-#5): FIVE
# consumers — formation of prior_level, bias term via prior_level, evidence-
# gate contradiction condition, trauma-loop indicator distance test, kill-
# test #4 discriminatory bands.
DIRECTION: Dict[str, int] = {
    'C':              -1,   # hot expects LOWER coherence
    'burn_rate':      +1,   # hot expects HIGHER burn
    'trauma_arrival': -1,   # hot expects SOONER trauma
    'recovery_time':  +1,   # hot expects LONGER recovery
}

# Per-channel BASELINE — the "neutral" value each channel is anchored to at
# formation for a calm observer (distress_fraction = 0). Sharp observers
# have prior_level[ch] == BASELINE[ch]; hot observers have prior_level
# shifted by DIRECTION[ch] * PRIOR_LEVEL_OFFSET[ch].
BASELINE: Dict[str, float] = {
    'C':              0.5,
    'burn_rate':      BURN_RATE_BASELINE,
    'trauma_arrival': ARRIVAL_BASELINE,
    'recovery_time':  RECOVERY_BASELINE,
}

# Per-channel PRIOR_LEVEL_OFFSET — magnitude of the formation-time shift
# from baseline at maximum distress (distress_fraction = 1). Formation
# function form (Amendment #3):
#   prior_level[ch] = BASELINE[ch] + DIRECTION[ch] * PRIOR_LEVEL_OFFSET[ch]
#                       * distress_fraction
# Linear in distress_fraction. Values tuned so hot's prior_level lands at
# semantically meaningful contradictions of reality per channel.
PRIOR_LEVEL_OFFSET: Dict[str, float] = {
    'C':              0.2,    # hot's prior_level_C = 0.5 - 0.2 = 0.3
    'burn_rate':      0.06,   # hot's prior_level_burn_rate = 0.08 + 0.06 = 0.14
    'trauma_arrival': 60.0,   # hot's prior_level_trauma_arrival = 100 - 60 = 40
    'recovery_time':  30.0,   # hot's prior_level_recovery_time = 50 + 30 = 80
}

# DEPRECATED (Amendment #3): the drift-era signed magnitudes. Under level-
# anchored, direction is in DIRECTION and offset magnitude is in
# PRIOR_LEVEL_OFFSET (formation-time), and neither is consumed at every
# step (bias term is now KAPPA·(prior_level - predicted)). Retained for
# backward-compat imports; drop when Buzz's test rewrite lands.
CHANNEL_SENSITIVITY: Dict[str, float] = {
    'C':              -1.0,
    'burn_rate':      +0.8,
    'trauma_arrival': -1.2,
    'recovery_time':  +0.8,
}

# Per-channel error scale for variance pooling (external audit F4, 2026-07-01).
# C and burn errors live at ~0.1 scale; trauma_arrival / recovery_time at
# ~30-100 steps. Un-normalized pooling let the step-scale channels dominate
# coherence 900:1. Errors are divided by these before squaring.
CHANNEL_SCALE: Dict[str, float] = {
    'C':              1.0,
    'burn_rate':      BURN_RATE_BASELINE,
    'trauma_arrival': ARRIVAL_SCALE,
    'recovery_time':  RECOVERY_SCALE,
}

# Channels that feed compute_prediction_variance (and therefore the coherence
# gate). Narrowed from all 4 to C + burn_rate (Salazaar, 2026-07-19):
# trauma_arrival and recovery_time are stochastic targets in the live sim
# (trauma every ~200 steps); their normalized squared errors (~25/step each)
# keep variance structurally above τ regardless of prediction quality.
# C and burn_rate have unit-scale targets the observer can realistically
# converge on, preserving the gate's intent (detecting genuine convergence).
#
# τ = COHERENCE_THRESHOLD was calibrated on 4-channel variance (sweep v2,
# 2026-07-14). It is NOW A PLACEHOLDER pending sweep v3 on this narrowed
# gate. Do not treat 0.0106 as a validated threshold until sweep v3 is done.
COHERENCE_CHANNELS: Tuple[str, ...] = ('C', 'burn_rate')


# ===========================================================================
# Observer dataclass
# ===========================================================================

@dataclass
class Observer:
    """Structural metacognition state attached to each Agent.

    Replaces v37.2's `self.cracked` Boolean. Exists once formed; becomes
    `coherent` once predictions stabilize. Holds predictions across four
    channels and the prior-bias / evidence-gate that shape how new
    evidence is absorbed.
    """

    exists: bool = False
    formation_step: int = -1

    # Prior bias diagnostic readout (DEPRECATED authority per Amendment #3;
    # kept as derived value at formation for backward-compat serialization,
    # paired-cohort analysis, and legacy prints. Bias term now consumes
    # prior_level per channel).
    prior_bias_distress: float = 0.0
    # Evidence gate: 0 closed, 1 open. Under-update when evidence
    # contradicts prior (gate < 1 dampens the contradicting EMA term).
    evidence_gate: float = 1.0

    # Per-channel prior_level (Amendment #3, 2026-07-01) — the formation-set
    # belief this observer is anchored to. The bias term in step_predictions
    # pulls predictions toward these levels. Set at formation by
    # form_observer; fixed thereafter (v0.2 will explore level-healing).
    prior_level_C: float = 0.0
    prior_level_burn_rate: float = 0.0
    prior_level_trauma_arrival: float = 0.0
    prior_level_recovery_time: float = 0.0

    # Predictions per channel
    predicted_C: float = 0.0
    predicted_burn_rate: float = 0.0
    predicted_trauma_arrival: float = 0.0
    predicted_recovery_time: float = 0.0

    # Rolling history of (predicted, actual) per channel
    prediction_error_history: Deque[Dict[str, Tuple[float, float]]] = field(
        default_factory=lambda: deque(maxlen=K_DRIFT_WINDOW)
    )
    prediction_variance: float = float('inf')

    # Rolling-mean prediction error per channel (R3, Nymph audit)
    rolling_mean_pe_C: float = 0.0
    rolling_mean_pe_burn_rate: float = 0.0
    rolling_mean_pe_trauma_arrival: float = 0.0
    rolling_mean_pe_recovery_time: float = 0.0

    # Diagnostic — fires when observer holds hot prior against contradicting evidence
    trauma_loop_indicator: bool = False

    # Coherent once prediction_variance < COHERENCE_THRESHOLD AND
    # steps_since_formation > MIN_COHERENT_STEPS.
    coherent: bool = False
    coherent_step: int = -1            # step at which coherence was first declared
    coherent_steps: int = 0            # total steps spent coherent (for Channel 5)

    # Post-coherence variance log (external audit F7, 2026-07-01). Bounded
    # deque; every entry is prediction_variance sampled while coherent. Used
    # to detect drift for a v0.2 demote path — diagnostic, not consumed by
    # any current channel.
    post_coherence_variance_log: Deque[float] = field(
        default_factory=lambda: deque(maxlen=POST_COHERENCE_LOG_WINDOW)
    )


# ===========================================================================
# Helpers (pure functions on observer + raw agent state)
# ===========================================================================

def sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0:
        ez = math.exp(-x)
        return 1.0 / (1.0 + ez)
    ez = math.exp(x)
    return ez / (1.0 + ez)


def clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def compute_distress_fraction(history: Deque[float]) -> float:
    """Fraction of the sustained-pressure window where pressure was non-zero.

    Used at observer formation to set prior_bias_distress and evidence_gate.
    """
    if not history:
        return 0.0
    distressed = sum(1 for p in history if p > 0.0)
    return distressed / len(history)


def initialize_observer_predictions_from_window(
    observer: Observer,
    pressure_history: Deque[float],
    initial_C: float,
    initial_burn_rate: float,
) -> None:
    """Seed initial predictions at observer formation.

    Uses the current C and burn_rate as anchors; trauma_arrival and
    recovery_time start at neutral baselines (the observer will EMA into
    actual values once stepping begins).
    """
    observer.predicted_C = initial_C
    observer.predicted_burn_rate = initial_burn_rate
    observer.predicted_trauma_arrival = ARRIVAL_BASELINE
    observer.predicted_recovery_time = RECOVERY_BASELINE


def _compute_prior_level(channel: str, distress_fraction: float) -> float:
    """Formation function (Amendment #3, 2026-07-01):
        prior_level[ch] = BASELINE[ch] + DIRECTION[ch] * PRIOR_LEVEL_OFFSET[ch]
                            * distress_fraction

    Linear in distress_fraction. Sharp observer (d=0) → baseline;
    hot observer (d=1) → baseline shifted by the full per-channel offset in
    the direction hot pushes.
    """
    return (
        BASELINE[channel]
        + DIRECTION[channel] * PRIOR_LEVEL_OFFSET[channel] * distress_fraction
    )


def form_observer(
    observer: Observer,
    t: int,
    pressure_history: Deque[float],
    initial_C: float,
    initial_burn_rate: float,
) -> None:
    """Establish the observer with per-channel prior_level and evidence gate
    from the distress fraction observed during sustained-pressure accumulation.

    Called once when sustained-pressure-score exceeds FORMATION_THRESHOLD.

    Amendment #3 (2026-07-01): per-channel prior_level replaces the scalar
    prior_bias_distress as the load-bearing formation output. The bias term
    in step_predictions now pulls predictions toward each channel's level
    rather than adding a constant per-step drift. prior_bias_distress
    retained as a diagnostic readout (superseded but backward-compat).
    """
    observer.exists = True
    observer.formation_step = t

    distress_fraction = compute_distress_fraction(pressure_history)

    # Diagnostic readout — superseded by prior_level fields below (Amendment #3).
    observer.prior_bias_distress = clip(
        distress_fraction * PRIOR_BIAS_SLOPE - 1.0, -1.0, 1.0
    )

    observer.evidence_gate = clip(
        1.0 - distress_fraction * EVIDENCE_GATE_ASYMMETRY, 0.4, 1.0
    )

    # Amendment #3: per-channel prior_level from formation function.
    observer.prior_level_C              = _compute_prior_level('C',              distress_fraction)
    observer.prior_level_burn_rate      = _compute_prior_level('burn_rate',      distress_fraction)
    observer.prior_level_trauma_arrival = _compute_prior_level('trauma_arrival', distress_fraction)
    observer.prior_level_recovery_time  = _compute_prior_level('recovery_time',  distress_fraction)

    initialize_observer_predictions_from_window(
        observer, pressure_history, initial_C, initial_burn_rate
    )


def step_predictions(
    observer: Observer,
    actuals: Dict[str, float],
) -> Dict[str, float]:
    """Run one prediction-update step over all four channels.

    Returns (raw_errors, effective_errors) — both per-channel signed dicts.
    The gap between them measures how much the evidence gate is filtering
    (design §Direct evidence-gating instrumentation: raw_error vs
    effective_error is the "trapped" state made measurable). Return
    contract widened 2026-07-01 (Buzz verification pass) — the previous
    signature exposed only raw errors, leaving the logging requirement
    unsatisfiable.

    `actuals` must contain keys: 'C', 'burn_rate', 'trauma_arrival',
    'recovery_time'.
    """
    raw_errors: Dict[str, float] = {}
    effective_errors: Dict[str, float] = {}
    pe_record: Dict[str, Tuple[float, float]] = {}

    for channel in CHANNELS:
        predicted_attr = f'predicted_{channel}'
        predicted = getattr(observer, predicted_attr)
        actual = actuals[channel]
        prior_level = getattr(observer, f'prior_level_{channel}')
        prediction_error = actual - predicted
        raw_errors[channel] = prediction_error

        # Evidence-gate contradiction condition (Amendment #5 §5.1,
        # 2026-07-01): under level-anchored, "contradicting" means the
        # actual sits on the calm side of prior_level for a hot prior.
        #   contradicting iff sign(actual - prior_level[ch]) == -direction[ch]
        # For hot on C (direction=-1): actual > prior_level_C is contradicting
        # (calm reality contradicts hot's low-C paranoia). direction[channel]
        # is now the fifth consumer of the signed constant per Amendment #5.
        level_offset_sign = sign(actual - prior_level)
        contradicting = (
            level_offset_sign != 0
            and level_offset_sign == -DIRECTION[channel]
        )
        if contradicting:
            g_eff = observer.evidence_gate
        else:
            g_eff = 1.0
        effective_error = g_eff * prediction_error
        effective_errors[channel] = effective_error

        # Level-anchored update rule (Amendment #3, 2026-07-01):
        #   new_pred = predicted + (1-α)·g_eff·PE + KAPPA·(prior_level - predicted)
        # Bias term is now a PULL toward the formation-set level, not a
        # constant additive drift. Steady state: predicted converges to the
        # weighted average of actual and prior_level with weights
        # (1-α)·g_eff and KAPPA respectively. Mean_PE at steady state ∝
        # KAPPA·(actual - prior_level)/((1-α)·g_eff + KAPPA), so vindicated
        # environments (actual ≈ prior_level) yield ~zero PE while
        # contradicted environments yield persistent proportional PE — the
        # discriminatory band kill-test #4 needs.
        new_pred = (
            predicted
            + (1.0 - EMA_ALPHA) * effective_error
            + KAPPA * (prior_level - predicted)
        )
        setattr(observer, predicted_attr, new_pred)

        pe_record[channel] = (predicted, actual)

    observer.prediction_error_history.append(pe_record)
    update_rolling_mean_prediction_errors(observer)
    observer.prediction_variance = compute_prediction_variance(observer)

    # R2 hook — heals evidence gate when rolling-mean PE indicates persistent
    # contradiction on C. Under level-anchored (Amendment #3), contradiction
    # is "actual persistently on the calm side of prior_level_C", which at
    # steady state shows as sign(rolling_mean_pe_C) == -DIRECTION['C'] = +1
    # (predicted stuck near prior_level_C below actual). At EPSILON_HEAL=0
    # (v0.1) this is dormant but architecturally present. direction[channel]
    # is the fifth consumer per Amendment #5.
    if EPSILON_HEAL > 0:
        contradiction_sign_C = -DIRECTION['C']
        if sign(observer.rolling_mean_pe_C) == contradiction_sign_C:
            observer.evidence_gate = clip(
                observer.evidence_gate + EPSILON_HEAL, 0.0, 1.0
            )

    update_trauma_loop_indicator(observer)

    return raw_errors, effective_errors


def update_rolling_mean_prediction_errors(observer: Observer) -> None:
    """Update per-channel rolling-mean prediction errors from the history.

    Uses the full deque (bounded at K_DRIFT_WINDOW). Stored back on observer
    for fast read by channels / diagnostics.
    """
    if not observer.prediction_error_history:
        return

    sums = {ch: 0.0 for ch in CHANNELS}
    n = 0
    for record in observer.prediction_error_history:
        for ch in CHANNELS:
            if ch in record:
                predicted, actual = record[ch]
                sums[ch] += (actual - predicted)
        n += 1

    if n == 0:
        return

    observer.rolling_mean_pe_C              = sums['C']              / n
    observer.rolling_mean_pe_burn_rate      = sums['burn_rate']      / n
    observer.rolling_mean_pe_trauma_arrival = sums['trauma_arrival'] / n
    observer.rolling_mean_pe_recovery_time  = sums['recovery_time']  / n


def compute_prediction_variance(observer: Observer) -> float:
    """Aggregate cross-channel variance of recent prediction errors.

    Single scalar collapsing all four channels — used by the coherence
    gate. Smaller is more coherent (predictions tracking actuals tightly).
    """
    if not observer.prediction_error_history:
        return float('inf')

    n = 0
    sum_sq = 0.0
    for record in observer.prediction_error_history:
        for ch in COHERENCE_CHANNELS:
            if ch in record:
                predicted, actual = record[ch]
                err = (actual - predicted) / CHANNEL_SCALE[ch]
                sum_sq += err * err
                n += 1

    if n == 0:
        return float('inf')

    return sum_sq / n


def is_coherent(observer: Observer) -> bool:
    """Public read of the compound coherence-gate state (sticky).

    Reads observer.coherent — the boolean set once by
    maybe_promote_to_coherent when both compound-gate conditions
    (variance < COHERENCE_THRESHOLD AND ssf > MIN_COHERENT_STEPS) held
    at some past step. Once set, remains set.

    Prefer this function over direct `.coherent` attribute access:
    it makes the compound gate grep-able as one interface and gives us
    one place to change semantics if the gate's composition evolves.

    Joint constraint reminder: τ (COHERENCE_THRESHOLD) is calibrated
    against a pool that excludes observers with ssf < MIN_COHERENT_STEPS.
    See constant-declaration block at top of module.
    """
    return observer.coherent


def check_coherence_gate(observer: Observer, t: int) -> bool:
    """Compound gate check at time t: `variance < τ AND ssf > MCS`.

    Encapsulates BOTH constants COHERENCE_THRESHOLD and MIN_COHERENT_STEPS
    in one place. Used at promotion time inside maybe_promote_to_coherent.
    External callers should typically read `is_coherent(observer)` for
    the sticky state instead of re-evaluating the gate every step.

    Returns False for un-formed observers (before formation, the gate
    is not defined).
    """
    if not observer.exists:
        return False
    steps_since_formation = t - observer.formation_step
    return (
        observer.prediction_variance < COHERENCE_THRESHOLD
        and steps_since_formation > MIN_COHERENT_STEPS
    )


def get_prediction_variance_for_diagnostic(observer: Observer) -> float:
    """Read `observer.prediction_variance` for logging/telemetry only.

    NOT for coherence-gate decisions — use `is_coherent(observer)` or
    `check_coherence_gate(observer, t)` for that. This named accessor
    exists so the bypass-scan invariant test in
    `tests/test_coherence_gate_invariant.py` can distinguish accidental
    gate-bypass reads (which should trip the test) from legitimate
    telemetry reads (which shouldn't). Callers should use this instead
    of reading `.prediction_variance` directly.
    """
    return observer.prediction_variance


def compute_per_channel_variance_for_diagnostic(observer: Observer) -> Dict[str, float]:
    """Per-channel breakdown of prediction_variance (telemetry only).

    Same math as compute_prediction_variance but keeps the per-channel
    squared-normalized-error means separate instead of summing them into
    the scalar the gate consumes. Diagnostic D3 (2026-07-25) uses this to
    settle F7.3 and F10 — whether the variance signal is driven by C, by
    burn_rate, or by a saturation clip on one of them.

    NOT for coherence-gate decisions. The gate consumes the single scalar
    from compute_prediction_variance(). Do not sum the returned dict's
    values in production code paths — that would bypass whatever future
    changes the gate makes (weighting, clipping, etc.) that this accessor
    is deliberately unaware of.
    """
    per_channel_sum_sq = {ch: 0.0 for ch in COHERENCE_CHANNELS}
    per_channel_count = {ch: 0 for ch in COHERENCE_CHANNELS}
    for record in observer.prediction_error_history:
        for ch in COHERENCE_CHANNELS:
            if ch in record:
                predicted, actual = record[ch]
                err = (actual - predicted) / CHANNEL_SCALE[ch]
                per_channel_sum_sq[ch] += err * err
                per_channel_count[ch] += 1
    return {
        ch: (per_channel_sum_sq[ch] / per_channel_count[ch])
             if per_channel_count[ch] > 0 else 0.0
        for ch in COHERENCE_CHANNELS
    }


def maybe_promote_to_coherent(observer: Observer, t: int) -> bool:
    """Check coherence gate; promote and return True if newly coherent.

    Already-coherent observers stay coherent (and accumulate coherent_steps).
    Returns True only on the transition (for downstream effects / logging).

    Post-coherence variance logging (external audit F7, 2026-07-01) fires on
    both the already-coherent branch and the newly-coherent branch — every
    step spent coherent contributes exactly one entry to
    post_coherence_variance_log. Bounded deque; older entries drop as newer
    ones arrive.

    Gate composition promoted to first-class 2026-07-14 (Salazaar audit):
    the compound check lives in check_coherence_gate() so the joint of
    COHERENCE_THRESHOLD and MIN_COHERENT_STEPS is grep-able as one unit.
    """
    if is_coherent(observer):
        observer.coherent_steps += 1
        observer.post_coherence_variance_log.append(observer.prediction_variance)
        return False

    if check_coherence_gate(observer, t):
        observer.coherent = True
        observer.coherent_step = t
        observer.coherent_steps = 1
        observer.post_coherence_variance_log.append(observer.prediction_variance)
        return True

    return False


def update_trauma_loop_indicator(observer: Observer) -> None:
    """Fire diagnostic when observer holds a hot-formed prior_level against
    persistently contradicting evidence on C.

    Amendment #3 reformulation (2026-07-01) under level-anchored prior. Four
    conditions all required:

    1. Formation-set gate was low (`evidence_gate < GATE_HOT_THRESHOLD`),
       indicating hot formation persisted. Formation clips gate to [0.4,
       1.0]; hot agents land near 0.5, sharp agents near 1.0. GATE_HOT_
       THRESHOLD = 0.6 (Amendment #5) catches hot-formed observers without
       false-positiving sharp ones.
    2. `prior_level_C` significantly departs from baseline (indicates hot
       prior on C specifically). Uses PRIOR_LEVEL_DEVIATION_THRESHOLD.
    3. Rolling |mean_PE[C]| persistently large (> TRAUMA_LOOP_PE_THRESHOLD,
       upgraded to 0.1 by Amendment #3 per Buzz's staged fixed-point).
    4. `sign(mean_PE[C]) == -DIRECTION['C']` (predicted stuck below actual;
       hot's paranoid prior contradicted by benign reality). direction[
       channel] is the fifth consumer per Amendment #5.

    Not load-bearing for v0.1 behavior; logged for analysis. Kill-test #4
    (Amendment #3): indicator fires <20% of hot agents in vindicated
    environments, >80% in contradicted. Vindicated ≡ actual ≈ prior_level;
    contradicted ≡ actual sustained far from prior_level.
    """
    if not observer.exists:
        observer.trauma_loop_indicator = False
        return

    # Condition 1: formation-set gate remains hot.
    gate_condition = observer.evidence_gate < GATE_HOT_THRESHOLD

    # Condition 2: prior_level_C significantly departs from baseline.
    level_deviation = abs(observer.prior_level_C - BASELINE['C'])
    # >= not > (Buzz test-recomputation pass, 2026-07-02): max-hot formation
    # (distress_fraction = 1) lands prior_level_C at EXACTLY baseline -
    # PRIOR_LEVEL_DEVIATION_THRESHOLD, and float arithmetic returns the
    # deviation as exactly 0.2 — strict-greater made the indicator
    # unreachable via formation for the canonical hot arm. Fourth instance
    # of the boundary-unreachability class (gate<0.3 vs clip 0.4;
    # GATE_HOT_THRESHOLD; KAPPA floor; now this). Flagged to Salazaar for
    # ratification since 0.2 is Amendment #3's constant.
    level_condition = level_deviation >= PRIOR_LEVEL_DEVIATION_THRESHOLD

    # Condition 3: rolling PE magnitude persistently large.
    mean_pe_C = observer.rolling_mean_pe_C
    pe_magnitude_condition = abs(mean_pe_C) > TRAUMA_LOOP_PE_THRESHOLD

    # Condition 4: mean PE sign indicates predicted stuck opposite hot's push.
    # For hot on C (DIRECTION['C']=-1), contradiction shows as positive mean_pe.
    contradiction_sign_condition = sign(mean_pe_C) == -DIRECTION['C']

    observer.trauma_loop_indicator = (
        gate_condition
        and level_condition
        and pe_magnitude_condition
        and contradiction_sign_condition
    )


# ===========================================================================
# Helpers for channels (predictions consumed by behavior channels in fork)
# ===========================================================================

def collapse_likelihood(predicted_C: float, predicted_burn_rate: float) -> float:
    """Heuristic likelihood that an agent will lose coherence soon.

    Used by Channel 3 (D-caution from observer prediction). Low predicted C
    AND high predicted burn rate together → high collapse likelihood.

    Returns a value in [0, 1].
    """
    # Low-C term: rises sharply as predicted_C drops toward 0
    low_c_term = 1.0 - sigmoid((predicted_C - 0.3) * 10.0)
    # High-burn term: rises as predicted_burn_rate exceeds baseline
    high_burn_term = sigmoid((predicted_burn_rate - BURN_RATE_BASELINE) * 10.0)
    return clip(0.5 * low_c_term + 0.5 * high_burn_term, 0.0, 1.0)


def burn_decay_multiplier_from_observer(observer: Observer) -> float:
    """Channel 1 component: multiplier on base burn-decay.

    When observer is incoherent, returns 1.0 (no modulation).
    When coherent, slows decay only when predicted_recovery_time exceeds
    baseline (agent is bracing for a longer recovery). At baseline, no
    modulation. Below baseline (faster recovery predicted), no acceleration.

    Patched 2026-06-28 per Salazaar's confirmation that Annie's
    sigmoid-floor catch was a spec bug. The `max(0, sigmoid - 0.5)`
    clipping makes the modulation one-sided: brakes on threat, does NOT
    accelerate on safety.
    """
    if not is_coherent(observer):
        return 1.0
    excess = observer.predicted_recovery_time - RECOVERY_BASELINE
    return 1.0 - 0.05 * 2.0 * max(0.0, sigmoid(excess / RECOVERY_SCALE) - 0.5)


def mean_abs_prediction_error(observer: Observer) -> float:
    """Mean absolute prediction error across all channels, NORMALIZED per
    CHANNEL_SCALE.

    Un-normalized mean-abs would let step-scale channels (trauma_arrival,
    recovery_time) dominate C and burn_rate ~30:1 (external audit F4
    propagates here — same disease that affected variance pooling, same
    fix). Every channel error divided by its scale before absolute-value
    and averaging.

    Returns 0.0 when history is empty (avoids denominator-of-zero
    contamination downstream in `observer_quality_bonus`).
    """
    if not observer.prediction_error_history:
        return 0.0
    total = 0.0
    n = 0
    for record in observer.prediction_error_history:
        for ch in CHANNELS:
            if ch in record:
                predicted, actual = record[ch]
                total += abs(actual - predicted) / CHANNEL_SCALE[ch]
                n += 1
    if n == 0:
        return 0.0
    return total / n


def observer_quality_bonus(observer: Observer) -> float:
    """Channel 5 component: memoir quality bonus from observer's track record.

    Design v0.1 §Channel 5:
        bonus = coherent_steps * 0.005 * accuracy_factor
        accuracy_factor = 1 / (1 + mean_abs_prediction_error)

    Both coherence duration AND prediction accuracy contribute. A hot
    observer with many coherent_steps but persistent contradiction gets a
    modest bonus (accuracy_factor drops). A sharp observer with low error
    gets full bonus per coherent step (accuracy_factor → 1). No observer
    or zero coherent_steps → zero bonus.

    Fires at `transition_to_ancestor` (per-event, not per-step).
    """
    if not observer.exists or observer.coherent_steps == 0:
        return 0.0
    accuracy_factor = 1.0 / (1.0 + mean_abs_prediction_error(observer))
    return observer.coherent_steps * 0.005 * accuracy_factor


def refusal_probability_from_observer(
    observer: Observer,
    sacrifice_cost: float,
    floor: float,
) -> float:
    """Channel 2 component: sacrifice refusal probability from predicted C.

    Design v0.1 §Channel 2 formulation:
        predicted_C_after = observer.predicted_C - sacrifice_cost
        breach_margin     = floor - predicted_C_after
        refusal           = sigmoid(breach_margin / FLOOR_BREACH_SCALE)

    Positive margin = predicted post-sacrifice C would breach the floor →
    high refusal (~1.0 as margin grows). Sigmoid gives ~0.5 exactly at the
    floor, ~0 well above, ~1 well below.

    Coherence gate is the caller's responsibility: incoherent observers
    have unstable predictions and should fall back to the baseline random
    refusal chance the fork already defines (SACRIFICE_REFUSAL_CHANCE).
    The gate lives at the caller because Channel 2 is a REPLACEMENT
    pattern (predicted replaces baseline), not a MODULATION pattern (base
    times modifier), unlike Channels 1 and 4 which fold the gate inside.
    """
    predicted_C_after = observer.predicted_C - sacrifice_cost
    breach_margin = floor - predicted_C_after
    return sigmoid(breach_margin / FLOOR_BREACH_SCALE)


def trauma_decay_exponent_from_observer(observer: Observer) -> float:
    """Channel 4 component: exponent on base trauma decay.

    When observer is incoherent, returns 1.0 (no modulation).
    When coherent, raises exponent only when predicted_trauma_arrival is
    SHORTER than baseline (trauma expected soon → system braces and
    processes lingering penalty faster). At baseline or when trauma
    predicted to arrive late, no modulation.

    Sign note: spec narrative ("system braces when expecting more
    trauma") + ARRIVAL_BASELINE - predicted_trauma_arrival as the
    "nearness" direction is preserved here. Salazaar's 2026-06-28 patch
    letter used `predicted_trauma_arrival - arrival_baseline` which
    inverts the threat semantic; flagging back in a sister-letter. The
    `max(0, sigmoid - 0.5)` clipping pattern from his Channel 1 patch is
    applied here unchanged.
    """
    if not is_coherent(observer):
        return 1.0
    nearness_excess = ARRIVAL_BASELINE - observer.predicted_trauma_arrival
    return 1.0 + 0.3 * 2.0 * max(0.0, sigmoid(nearness_excess / ARRIVAL_SCALE) - 0.5)


# ===========================================================================
# Backward-compat aliases (v37.2 fields → observer-derived values)
# ===========================================================================

def cracked_alias(observer: Observer) -> bool:
    """Spec'd backward-compat: `self.cracked = self.observer.coherent`.

    Lets v37.2's downstream serialization, display, and diagnostic prints
    keep working. v0.2 may remove these aliases entirely.
    """
    return is_coherent(observer)


def metacognition_observations_alias(observer: Observer) -> int:
    """Backward-compat: maps to coherent_steps.

    v37.2 incremented this on every observe_self() call for cracked agents.
    The closest observer-state equivalent is coherent_steps.
    """
    return observer.coherent_steps
