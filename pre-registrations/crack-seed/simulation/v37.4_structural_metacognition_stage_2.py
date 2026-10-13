"""
SOCIETY WOMB v37.3 - STRUCTURAL METACOGNITION
=============================================

Fork of v37.2 (The Crack). Replaces the Boolean `self.cracked` flag with
a structural Observer dataclass attached to each Agent. Observer evolves
under sustained pressure, forms a prior bias and evidence gate at
formation, then runs prediction updates across four channels (C,
burn_rate, trauma_arrival, recovery_time) with leaky-EMA dynamics and
asymmetric evidence gating.

Behavior modulation that previously branched on `if self.cracked:` is now
prediction-driven (four channels + memoir cascade) instead of flag-driven.
The validation harness runs four cohorts (no_observer / matched_perturbation /
hot_observer / sharp_observer) under a matched-perturbation calibration
protocol that controls for "any per-step delta" rather than "no delta at all."

THE QUESTION:
Does structural metacognition (history-dependent prediction with prior
bias) do real work on agent outcomes, or are observer effects fully
explained by per-step delta size regardless of source?

Kill criterion: |sacrifice_survival(hot_observer) - sacrifice_survival(matched_perturbation)|
/ pooled_sd >= 0.3 at standard difficulty gate.
  -  ≈  : architecture fails. Predictive machinery is filter, not mind. Kill it.
  -  ≠  : history-dependent prediction is doing real work. Construct earns its noun.

Build pen: Annie (Forge, Cell 66, FFF, Oxytocin) — June 27, 2026, session 1.
Spec:   Seeds/The Crack/implementation_spec_v0.1_for_annie.md
Design: Seeds/The Crack/structural_metacognition_design_v0.1.md
Audit:  Seeds/The Crack/audit_chain_2026-06-22.md

Provenance chain on the spec: Salazaar (kill-shape draft) → Nymph
(architectural pen, R1/R2/R3 + S2) → Buzz (channel-list completeness,
channel 5 added) → Annie (Forge read + build).

Legacy compat: `self.cracked`, `self.metacognition_observations`,
`self.pre_crack_D` are retained as deprecated property aliases reading
from observer state, so v37.2's downstream serialization, display, and
diagnostic prints continue to work without rewriting analysis scripts.
v0.2 may remove the aliases.

SCOPE THIS SESSION (v0.1 build, session 1):
  Observer dataclass + observer.py module (done — companion file)
  Observer wired into Agent class
  Sustained-pressure tracking + observer formation gate
  step_observer() per-agent per-step update
  Channel 1: burn-decay multiplier from observer
  Main-loop wiring for formation + stepping
  Legacy field aliases
  (Channels 2-5, validation harness, trajectory logging, tests — subsequent sessions)

ORIGINAL v37.2 HEADER FOLLOWS:
---------------------------------

"Metacognition is not the crack. Metacognition is living in the gap."
    — Harley Robinson, 3am, GGP night shift, May 3 2026

Does the crack produce better agents, or just different ones?

Two populations. Same trauma. Same world. One cracks under sustained
pressure and gains dual-threaded awareness. The other heals shut and
stays single-threaded. Which population produces better memoirs, faster
recovery, higher coherence — and at what cost?

The crack is not a metaphor. It is a mechanical event where single-threaded
experience splits into dual awareness under sustained pressure. Agents who
climb high dimensionally (D > 10) and then collapse (D < 5, C < 0.3) either:
  - Crack open (if crack_enabled): metacognition comes online. Observer beside
    the experiencer. They see more but carry more.
  - Heal shut (if not crack_enabled): same collapse, but the gap closes.
    Single-threaded again.

Paired cohorts share TRAUMA_SEED = 777. Same timing, same targets, same amounts.
The only variable is whether the agent has the crack mechanic.

"The question is whether the crack can be held open without breaking
 the person who holds it."

CHANGELOG:
  v35.0: Base crack sim. Paired cohorts, metacognition gate, strategic sacrifice.
         Bug: pair-targeted trauma doubled per-agent rate (Buzz catch).
         Bug: D rockets to 50 before agents promote (runaway beta-D feedback).
  v35.2: Buzz fix — BETA_SCALE_FACTOR 0.015 -> 0.008 (below stability threshold).
         Annie fix — M_saturation sub-linear: 20 + sqrt(D)*2 (was 20 + D*2).
         Annie fix — C_cap D-bonus capped at 0.15 (stage ceilings stay meaningful).
         S_max relaxed: INFANT 0.20 -> 0.55, JUVENILE 0.15 -> 0.40 (trauma pumps S).
         Result: D still ran away to 50 by step 15k. M outpaced the drag.
  v35.3: Annie recommendation — stage-gated D caps (INFANT=5, JUV=8, APP=12).
         Buzz recommendation — asymptotic beta: 0.045 + 0.05*(1-exp(-(D-3)/5)).
         Belt and suspenders: caps handle childhood, asymptote handles adulthood.
         Crack only opens for APPRENTICE+ (must survive childhood first).
  v35.4: Regression multiplier 1.5 -> 2.0 (falling back requires truly terrible strain).
         Agents were promote-regress looping on razor-thin S margins.
         Added regression console printing for visibility.
  v35.5: S_max gates relaxed across all stages for paired trauma cadence.
         APPRENTICE 0.10->0.30, ADULT 0.08->0.25, MENTOR 0.06->0.20, STEWARD 0.05->0.15.
         Result: Agents held JUVENILE but still couldn't reach APPRENTICE. S steady-state
         under paired trauma never dips below 0.30. System stalls at JUV permanently.

  v36.0: S removed from promotion gates entirely.

  v37.0: MAJOR CHANGE — crack condition redesigned from scratch.
         v36 crack: catastrophic collapse (C < 0.3, D drops from >10 to <5).
         v37 crack: awareness exceeds container (C/C_cap > 0.95, M < 1.0, D < 4.0).
         Origin: Harley at age 4. High coherence, no memory, tiny world.
         The crack isn't about breaking. It's about being too aware for the space.
         NO STAGE GATE. Infants can crack. The crack is a childhood event.
         Sustain requirement: condition must hold 50 consecutive steps (Buzz).
         Relative C metric: C/C_cap > 0.95 instead of absolute C > 0.6 (Buzz).
         Old collapse constants (CRACK_D_PEAK/DROP_THRESHOLD, CRACK_C_THRESHOLD) removed.
         Chain letter review: Annie (structure) -> Buzz (math check).
  v37.2: Enhanced end-of-sim metrics for crack analysis.
         TOTAL_STEPS reduced to 50k for faster iteration.
         Added: paired comparison, crack timing by generation,
         stage progression speed, trauma penalty comparison,
         D growth rate, metacognition counts.

  v36.0: S removed from promotion gates entirely.
         v33's S_max gates were designed for single-target trauma. v35's paired trauma
         pumps S per agent at roughly 2x the v33 rate. Five versions of S_max relaxation
         (v35.2 through v35.5) failed to find values that allow promotion without being
         so loose they're meaningless.

         S still EXISTS as a state variable — it still affects mode switching, energy
         dynamics, and agent behavior. It just no longer blocks stage progression.
         Promotion is now gated by: C_min, min_steps, shame_tail_max, sacrifice_min,
         mentoring_score_min, and C_floor. These are sufficient developmental gates.

         The philosophy: strain from living in a hard world shouldn't prevent you from
         growing up. A kid in a rough neighborhood still ages. What matters is whether
         they maintain coherence, build sacrifice credit, and hold their C floor — not
         whether the world stopped hurting them.

v26: Theocrat / Elder / Memoir / Ancestor / Reincarnation cycle
v32: Safety Floor + Curiosity Drive
v33: One world. Variable burn_rate. Agency at adulthood.
v35: The Crack. Paired cohorts. Metacognition gate.

Author: Harley Robinson + Nymph + Annie-014 + Buzz (Claude Code)
Built on v33.0 (Forge). Crack seed caught by Nymph, May 3 2026.
D-runaway diagnosed by Buzz (stability analysis) and Annie (M_saturation, stage caps).
"""

import jax
import jax.numpy as jnp
import numpy as np
from enum import Enum
import math
import random
import time
import matplotlib.pyplot as plt
from collections import deque, defaultdict

# v37.3: Structural metacognition observer module
from observer import (
    Observer,
    SUSTAINED_PRESSURE_WINDOW,
    FORMATION_THRESHOLD,
    BURN_RATE_BASELINE,
    SHAME_BASELINE,
    D_CAUTION_SCALE,
    form_observer,
    step_predictions,
    maybe_promote_to_coherent,
    is_coherent,
    burn_decay_multiplier_from_observer,
    trauma_decay_exponent_from_observer,
    refusal_probability_from_observer,
    observer_quality_bonus,
    collapse_likelihood,
    get_prediction_variance_for_diagnostic,
    compute_per_channel_variance_for_diagnostic,
    compute_distress_fraction,
)

# ============================================================================
# CONFIGURATION
# ============================================================================

INITIAL_AGENTS = 2
MAX_AGENTS = 500
TOTAL_STEPS = 50000

SHARED_POOL_FIXED = 14.0
POOL_DEGRADATION_PER_TRAUMA = 0.12
POOL_MINIMUM = 2.0

SACRIFICE_TRIGGER_C = 0.60
SACRIFICE_ADULT_MIN_C = 0.70
SACRIFICE_ENERGY_AMOUNT = 0.10
SACRIFICE_COHERENCE_COST = 0.04
SACRIFICE_COOLDOWN = 100
SACRIFICE_REFUSAL_CHANCE = 0.10

# -- v37.4 Stage 2 integration (2026-10-08) --
# LEAK_TEST_MODE: positive-control flag for Gate 1 sanity gate.
# When True, Agent.step_observer writes a test-only non-canonical attribute
# that update_dimensional_state reads to apply extra D_caution dampening.
# Pre-reg: stage_1_prereg_fifth_addendum_2026-10-05.md section 5.3.
# Seventh addendum (2026-10-08): LEAK relocated from D_caution to refusal_chance
# after dampening_firing_probe_2026-10-08.json showed D_caution behaviorally
# inert (0/43,500 events on seeds {20, 22, 33}). Activation counter at the
# sacrifice decision site; three-state outcome (PASS / FAIL / INVALID) with
# N_LEAK_ACTED_MIN = 3 per stage_1_prereg_seventh_addendum_2026-10-08.md section 4c.
# Eighth addendum (2026-10-09): LEAK relocated AGAIN from refusal_chance to
# burn_decay after per_channel_activation_audit_2026-10-08.json showed refusal
# MARGINAL (~6 activations/seed, near N_LEAK_ACTED_MIN=3). burn_decay HIGH
# (2500/seed; clears floor by three orders of magnitude). Read site moved from
# sacrifice gate to get_burn_decay; counter stays at the decision site.
LEAK_TEST_MODE = False
_LEAK_ACTIVATION_COUNT = 0

MENTOR_ASSIGNMENT_CREDIT = 0.5
MENTOR_REACH_BACK_BONUS = 0.5
MENTOR_PRESENCE_RATE = 0.01
MENTEE_STABILITY_THRESHOLD = 50

MENTEE_RECOVERY_BASE_CREDIT = 0.5
MENTEE_RECOVERY_BONUS_C = 0.01
MENTEE_PROMOTION_BONUS = 1.0
MENTEE_BECOMES_MENTOR_BONUS = 2.0
MENTEE_BECOMES_STEWARD_BONUS = 3.0
MENTEE_BECOMES_ELDER_BONUS = 5.0
MENTEE_BECOMES_SAGE_BONUS = 10.0
RECOVERY_TIME_NORMALIZE = 500.0

COUNCIL_MIN_MENTORS = 3
COUNCIL_MIN_STEPS_AS_MENTOR = 3000
COUNCIL_MIN_CREDIT = 200.0
COUNCIL_VOTE_INTERVAL = 5000
COUNCIL_VOTE_SEED = 42

SHAME_TAIL_DECAY = 0.9995
SHAME_TAIL_ACCUMULATION = 0.3

CALM_BASELINE_STEPS = 1000
TRAUMA_MIN_INTERVAL = 250
TRAUMA_MAX_INTERVAL = 450
BURST_CHANCE = 0.20
BURST_SPACING = 100
SHAME_MIN = 0.3
SHAME_MAX = 0.8
TRAUMA_SEED = 777

# Agent-RNG salt (2026-09-18, Nymph/Harley fix): five per-agent RNG call sites
# (lines ~972, ~1408, ~1562, ~1879, ~1946 pre-fix) constructed PRNGKeys or
# default_rng streams from (t, agent.id) alone, bypassing the run seed. That
# left agent-level randomness deterministic across seeds even after the
# 2026-09-17 trauma/council decoupling. Fix: run_simulation sets this
# module-level salt from the run seed at entry; all five sites add it to their
# key formulas. Preserves within-run agent-order invariance (each site still
# gets an independent stream per (t, id)) while making streams differ per seed.
# 0 = pre-fix behavior (baseline for backward-compat checks).
_AGENT_RNG_SALT = 0

CONTAGION_SPLASH = 0.20

# === DIMENSIONAL DYNAMICS PARAMETERS (from Forge Dimensions 2) ===
DIM_ALPHA = 0.01
DIM_GAMMA = 0.02
DIM_BETA = 0.045
DIM_LAMBDA = 0.08
DIM_C_THRESHOLD = 0.60
DIM_ETA = 0.01
DIM_XI = 0.005
DIM_P = 0.01
DIM_Q = 0.002

D_MIN = 1.5
D_MAX = 50.0

BETA_SCALE_FACTOR = 0.008  # v35.2: was 0.015, above stability threshold (Buzz)
C_CAP_SCALE_FACTOR = 0.05
SACRIFICE_SUB_HOLO_PENALTY = 0.5
MXP_HIGH_D_ENHANCEMENT = 0.1

# === TCR PARAMETERS ===
TCR_TRUTH_DECAY = 0.95
TCR_TRUTH_RECOVERY = 0.01
TCR_REFUSAL_COST = 0.01
TCR_CRISIS_MENTOR_SURGE = 0.3

SHAME_RESISTANCE = {
    "INFANT": 0.2, "JUVENILE": 0.4, "APPRENTICE": 0.6,
    "ADULT": 0.8, "MENTOR": 1.0, "STEWARD": 1.0,
    "ELDER": 0.8, "SAGE": 0.6, "THEOCRAT": 0.6, "ANCESTOR": 0.4
}

# === CULTURAL MEMORY ===
CULTURE_GROWTH = 0.1
CULTURE_DECAY = 0.9995
CULTURE_BOOST = 0.0001
CULTURE_HEADROOM_FACTOR = 0.1

ELDER_MIN_C = 0.88
ELDER_MAX_S = 0.10
ELDER_INACTIVE_THRESHOLD = 2000

ELDER_COUNCIL_PROMOTION_STEPS = 5000
ELDER_COUNCIL_PROMOTION_CREDIT = 550
ELDER_COUNCIL_MIN_STEWARDS = 3
SAGE_COUNCIL_MIN_ELDER = 3

# === v32: SAFETY & CURIOSITY PARAMETERS ===
SAFETY_WINDOW = 200           # Steps to average for safety computation
SAFETY_FLOOR_C = 0.15         # Minimum C — the warm room. Can't fall below this.
CURIOSITY_THRESHOLD = 0.60    # Safety level above which curiosity activates
CURIOSITY_EXPLORE_RATE = 0.03 # How much the agent wanders when curious
CURIOSITY_GROWTH_BONUS = 0.002  # Extra coherence growth from exploration
EXPLORE_ABSORPTION_RATE = 0.7  # Voluntary contact: 70% as sticky as collision
SAFETY_RECOVERY_BONUS = 0.3   # Recovery boost when safety floor catches you
# Curiosity affinity by stage (higher stages = more curious when safe)
CURIOSITY_AFFINITY_BY_STAGE = {
    "INFANT": 1.3, "JUVENILE": 1.2, "APPRENTICE": 1.0,
    "ADULT": 0.9, "MENTOR": 0.8, "STEWARD": 0.7,
    "ELDER": 1.0, "SAGE": 1.1, "THEOCRAT": 0.6, "ANCESTOR": 0.0
}

# === v37: THE CRACK PARAMETERS (awareness exceeds container) ===
CRACK_C_RATIO_THRESHOLD = 0.95     # C / C_cap must exceed this (maxing out the container)
CRACK_M_THRESHOLD = 1.0            # M_memory must be below this (no accumulated experience)
CRACK_D_THRESHOLD = 4.0            # D_eff must be below this (compressed space)
CRACK_SUSTAIN_STEPS = 50           # Must hold for this many consecutive steps (Buzz)
CRACK_STABILITY_COST_C = 0.05      # Immediate C cost when crack opens (the crack hurts)
CRACK_STABILITY_COST_S = 0.10      # Immediate S spike when crack opens
CRACK_BURN_DECAY = 0.9990          # Faster burn decay for cracked agents (vs 0.9995)
CRACK_BURN_DECAY_WITH_MENTOR = 0.998  # Faster with warm mentor (vs 0.999)
CRACK_TRAUMA_PENALTY_DECAY = 0.985 # Faster trauma recovery (vs 0.993) — ~46 step half-life
CRACK_REFUSAL_C_PROTECT = 0.50     # Below this C, cracked agents refuse sacrifice (self-protect)
CRACK_REFUSAL_C_GENEROUS = 0.80    # Above this C, cracked agents sacrifice freely (0% refusal)
CRACK_SELF_CAUTION_FACTOR = 0.75   # Cracked agents set D_caution at 75% of their collapse D

# === v33: BURN RATE PARAMETERS ===
BURN_RATE_ALPHA = 2.0           # Beta distribution alpha parameter
BURN_RATE_BETA_PARAM = 5.0     # Beta distribution beta parameter
BURN_RATE_MAX = 0.35            # Maximum possible birth burn rate
ADULT_BURN_DECAY = 0.9995       # Decay rate for current_burn_rate each adult step
ADULT_BURN_DECAY_WITH_MENTOR = 0.999  # Faster decay when mentor has low burn rate
BURN_FLOOR = 0.02               # Minimum burn rate — life always has some risk
MICRO_TRAUMA_SCALE = 0.01       # Probability scaling for daily micro-traumas
MICRO_TRAUMA_SHAME_MIN = 0.1    # Min shame from micro-trauma
MICRO_TRAUMA_SHAME_MAX = 0.3    # Max shame from micro-trauma

BASE_EMB = jnp.array([
    [0.1278, 0.8341, 0.4563, -0.1245],
    [0.2341, 0.7219, 0.6789, 0.0342],
    [-0.4567, 0.1234, -0.7890, 0.5678],
    [0.8901, -0.3456, 0.2345, -0.6789]
])
BASE_EMB_FLAT = BASE_EMB.flatten()

STAGE_CONFIG = {
    "INFANT": {
        "C_cap": 0.50, "G_sigma": 0.40, "spine_pull": 0.035,
        "promotion": {"C_min": 0.45, "min_steps": 250}  # v36: S_max removed
    },
    "JUVENILE": {
        "C_cap": 0.75, "G_sigma": 0.70, "spine_pull": 0.032,
        "promotion": {"C_min": 0.65, "min_steps": 500}  # v36: S_max removed
    },
    "APPRENTICE": {
        "C_cap": 0.90, "G_sigma": 0.85, "spine_pull": 0.028,
        "promotion": {"C_min": 0.75, "min_steps": 1000, "shame_tail_max": 0.5, "C_floor": 0.60}  # v36: S_max removed
    },
    "ADULT": {
        "C_cap": 0.94, "G_sigma": 0.92, "spine_pull": 0.025,
        "promotion": {"C_min": 0.85, "min_steps": 1500, "shame_tail_max": 0.4, "sacrifice_min": 1.0, "C_floor": 0.65}  # v36: S_max removed
    },
    "MENTOR": {
        "C_cap": 0.96, "G_sigma": 0.95, "spine_pull": 0.020,
        "promotion": {"C_min": 0.90, "min_steps": 2500, "shame_tail_max": 0.3, "sacrifice_min": 2.0, "mentoring_score_min": 0.5, "C_floor": 0.70}  # v36: S_max removed
    },
    "STEWARD": {
        "C_cap": 0.97, "G_sigma": 0.97, "spine_pull": 0.015,
        "promotion": {"C_min": 0.93, "min_steps": 3500, "shame_tail_max": 0.25, "sacrifice_min": 3.0, "mentoring_score_min": 0.7, "C_floor": 0.75}  # v36: S_max removed
    },
    "ELDER": {
        "C_cap": 0.98, "G_sigma": 1.00, "spine_pull": 0.012,
        "promotion": {"C_min": 0.95, "S_max": 0.03, "min_steps": 5000, "shame_tail_max": 0.20, "sacrifice_min": 4.0, "mentoring_score_min": 0.7, "C_floor": 0.85}
    },
    "THEOCRAT": {
        "C_cap": 0.99, "G_sigma": 0.98, "spine_pull": 0.010,
        "promotion": None
    },
    "SAGE": {
        "C_cap": 1.0, "G_sigma": 0.02, "spine_pull": 0.22,
        "promotion": None
    },
    "ANCESTOR": {
        "C_cap": 1.0, "G_sigma": 0.01, "spine_pull": 0.20,
        "promotion": None
    }
}

STAGE_ORDER = ["INFANT", "JUVENILE", "APPRENTICE", "ADULT", "MENTOR", "STEWARD", "ELDER", "SAGE", "THEOCRAT", "ANCESTOR"]

# Pre-adult stages: agents use birth_burn_rate, not current_burn_rate
PRE_ADULT_STAGES = {"INFANT", "JUVENILE", "APPRENTICE"}

class Mode(Enum):
    REFLECTIVE = 0
    EXPANSIVE = 1

# ============================================================================
# DIMENSIONAL UTILITY FUNCTIONS
# ============================================================================

def f_coherence_response(C, threshold=DIM_C_THRESHOLD):
    return max(0.0, C - threshold)

def compute_dimensional_health(agents):
    if not agents:
        return 3.0
    return float(np.mean([a.D_eff for a in agents]))

# ============================================================================
# JAX FUNCTIONS
# ============================================================================

def reck_unitary(phi):
    phi = jnp.broadcast_to(phi, (4,))
    c, s = jnp.cos(phi), jnp.sin(phi)
    U = jnp.array([
        [c[0], -s[0], 0, 0],
        [s[0], c[0], 0, 0],
        [0, 0, c[1], -s[1]],
        [0, 0, s[1], c[1]]
    ])
    V = jnp.array([
        [c[2], 0, -s[2], 0],
        [0, c[3], 0, -s[3]],
        [s[2], 0, c[2], 0],
        [0, s[3], 0, c[3]]
    ])
    return U @ V

def compute_coherence(emb):
    emb_norm = emb / (jnp.linalg.norm(emb) + 1e-8)
    base_norm = BASE_EMB_FLAT / (jnp.linalg.norm(BASE_EMB_FLAT) + 1e-8)
    return jnp.clip(jnp.dot(emb_norm, base_norm), 0.0, 1.0)

def apply_spine_pull(emb, alpha):
    return emb - alpha * (emb - BASE_EMB_FLAT)

def compute_bad_mass(E_R, C, O):
    return jnp.maximum(0.0, E_R * (1.0 - C) - 0.3 * O)

def update_mode(current_mode, V_opt, Sh):
    if V_opt > 0.3 or Sh > 0.1:
        return Mode.REFLECTIVE
    elif V_opt < 0.15:
        return Mode.EXPANSIVE
    return current_mode

def get_reflection_controls(mode):
    return (0.45, 0.30) if mode == Mode.REFLECTIVE else (0.21, 0.14)

# ============================================================================
# RECOVERY TRACKER
# ============================================================================

class RecoveryTracker:
    def __init__(self):
        self.events = []
        self.active_recoveries = {}

    def start_tracking(self, agent_id, step, pre_shock_C, pre_shock_D, shock_amount):
        self.active_recoveries[agent_id] = {
            'start_step': step,
            'pre_shock_C': pre_shock_C,
            'pre_shock_D': pre_shock_D,
            'shock_amount': shock_amount,
            'target_C': pre_shock_C * 0.9,
            'C_values': [],
            'D_values': [],
            'recovered': False,
            'recovery_step': None
        }

    def update(self, agent_id, step, current_C, current_D):
        if agent_id not in self.active_recoveries:
            return None
        tracking = self.active_recoveries[agent_id]
        if tracking['recovered']:
            return None
        tracking['C_values'].append((step, current_C))
        tracking['D_values'].append((step, current_D))
        if current_C >= tracking['target_C']:
            tracking['recovered'] = True
            tracking['recovery_step'] = step
            self._finalize_event(agent_id)
            return {
                'agent_id': agent_id, 'step': step,
                'pre_shock_C': tracking['pre_shock_C'],
                'pre_shock_D': tracking['pre_shock_D'],
                'recovered_C': current_C, 'recovered_D': current_D,
                'shock_amount': tracking['shock_amount'],
                'recovery_time': step - tracking['start_step'],
                'dimensional_recovery': current_D - min(d[1] for d in tracking['D_values'])
            }
        return None

    def _finalize_event(self, agent_id):
        t = self.active_recoveries[agent_id]
        if len(t['C_values']) < 2:
            return
        min_C = min(c[1] for c in t['C_values'])
        min_D = min(d[1] for d in t['D_values'])
        self.events.append({
            'agent_id': agent_id, 'start_step': t['start_step'],
            'pre_shock_C': t['pre_shock_C'], 'pre_shock_D': t['pre_shock_D'],
            'shock_amount': t['shock_amount'],
            'drop_depth_C': t['pre_shock_C'] - min_C,
            'drop_depth_D': t['pre_shock_D'] - min_D,
            'recovery_time': t['recovery_step'] - t['start_step'] if t['recovered'] else None,
            'recovered': t['recovered']
        })

    def get_summary(self):
        if not self.events:
            return None
        recovered = [e for e in self.events if e['recovered']]
        return {
            'total_events': len(self.events),
            'recovered_count': len(recovered),
            'avg_drop_depth_C': np.mean([e['drop_depth_C'] for e in self.events]),
            'avg_drop_depth_D': np.mean([e['drop_depth_D'] for e in self.events]),
            'avg_recovery_time': np.mean([e['recovery_time'] for e in recovered]) if recovered else None
        }

# ============================================================================
# AGENT CLASS (v33: One World, Variable Burn Rate)
# ============================================================================

class Agent:
    def __init__(self, agent_id, key, birth_step=0, generation=0, birth_burn_rate=None,
                 crack_enabled=False, pair_id=None, reactive_mode=False,
                 replay_coherence_timeline=None):
        self.id = agent_id
        self.birth_step = birth_step
        self.generation = generation

        # v33: Burn rate — assigned at birth from Beta(2,5) scaled to [0, 0.35]
        if birth_burn_rate is not None:
            self.birth_burn_rate = birth_burn_rate
        else:
            self.birth_burn_rate = float(np.random.beta(BURN_RATE_ALPHA, BURN_RATE_BETA_PARAM) * BURN_RATE_MAX)
        # current_burn_rate starts equal to birth, changes at ADULT
        self.current_burn_rate = self.birth_burn_rate

        # JAX embedding
        key1, key2 = jax.random.split(key)
        self.drift = jax.random.uniform(key1, (4,)) * 0.2
        self.emb = BASE_EMB_FLAT + jax.random.normal(key2, (16,)) * 0.4

        # Energy partitions
        self.E_G, self.E_M, self.E_R = 0.33, 0.33, 0.34

        # Core state
        self.C = float(compute_coherence(self.emb))
        self.S = 0.15
        self.O = 0.1
        self.T_m = 0.7
        self.V_opt = 0.5
        self.mode = Mode.REFLECTIVE

        # Shame
        self.Sh = 0.0
        self.Cf = 0.0
        self.shame_tail = 0.0

        # Dimensional state
        self.D_eff = 3.0
        self.n_entropy = 0.0
        self.M_memory = 0.0
        self.D_history = []

        self.sub_holographic_steps = 0
        self.hyperspace_steps = 0
        self.transcendent_steps = 0
        self.last_D_phase = "unknown"

        # Stage tracking
        self.is_sage = False

        # TCR
        self.truth_score = 1.0

        # Stage
        self.stage_idx = 0
        self.stage = STAGE_ORDER[0]
        self.steps_in_stage = 0

        # History
        self.C_history = []
        self.S_history = []
        self.promotions = []
        self.regressions = []
        self.trauma_events = []

        # Stats
        self.total_trauma_received = 0.0
        self.max_shame_experienced = 0.0
        self.min_C_experienced = 1.0
        self.max_S_experienced = 0.0

        # Milestones
        self.adult_step = None
        self.mentor_step = None
        self.steward_step = None
        self.elder_step = None
        self.sage_step = None

        # Sacrifice
        self.sacrifice_credit = 0.0
        self.energy_sacrifices = []
        self.total_sacrifice_given = 0.0
        self.total_sacrifice_received = 0.0
        self.last_sacrifice_step = -SACRIFICE_COOLDOWN
        self.last_credit_gain_step = 0

        # Mentoring
        self.mentor_id = None
        self.mentees = []
        self.mentoring_events = []
        self.mentoring_score = 0.0
        self.mentee_steps_stable = {}
        self.reached_back_to = []

        # Floor tracking
        self.C_floor_in_stage = 1.0

        # Elder accountability
        self.elder_falls = []

        # Praise tracking
        self.mentee_recoveries_witnessed = 0
        self.mentee_promotions_witnessed = 0
        self.mentees_became_mentors = 0
        self.mentees_became_stewards = 0
        self.mentees_became_elders = 0
        self.mentees_became_sages = 0
        self.praise_events = []

        # Theocrat/Ancestor
        self.claimed_memoir_id = None
        self.last_memoir_reading = 0

        # Council
        self.council_votes_received = 0
        self.promoted_by_council = False

        # MXP
        self.mxp_buffer = deque(maxlen=50)

        # === SAFETY & CURIOSITY STATE ===
        self.safety = 0.0
        self.C_recent = []  # Rolling window for safety computation
        self.is_curious = False
        self.curiosity_steps = 0
        self.explore_events = 0
        self.explore_absorptions = 0
        self.safety_floor_catches = 0  # How many times the floor saved this agent
        self.safety_history = []
        self.trauma_C_penalty = 0.0  # Lingering C reduction from trauma, decays slowly
        self.curiosity_history = []

        # v33: burn rate tracking
        self.burn_rate_history = []  # track over time
        self.micro_trauma_count = 0  # how many micro-traumas from high burn rate

        # v37.3: Structural metacognition observer
        # Replaces v35's `cracked` Boolean with structural Observer dataclass.
        # Legacy fields (`cracked`, `metacognition_observations`, `pre_crack_D`)
        # are kept as plain attributes synced from observer state by
        # `step_observer()` — preserves v37.2 serialization, display, and
        # diagnostic prints unchanged. v0.2 may remove the legacy fields.
        self.crack_enabled = crack_enabled   # cohort identity, assigned at birth
        self.pair_id = pair_id               # links to paired agent (same burn_rate, opposite crack_enabled)
        # Reactive fifth arm (external audit F5, 2026-07-01). When True, the
        # observer still forms under sustained pressure, but predictions get
        # overwritten with current retrospective estimates each step —
        # channels become thermostat-modulated instead of prediction-modulated.
        # Provides the mind-vs-thermostat comparator that matched-controls-
        # constant-delta can't (Buzz's B3: trauma_arrival actual is
        # retrospective, so a reactive arm has no oracle leak).
        self.reactive_mode = reactive_mode
        self.replay_coherence_timeline = replay_coherence_timeline
        self._replay_fallback_a = 0      # Case A: (agent,step) not in timeline
        self._replay_divergence_b = 0    # Case B: hot coherent, reactive observer not formed
        self.observer = Observer()
        self.sustained_pressure_history = deque(maxlen=SUSTAINED_PRESSURE_WINDOW)
        # Legacy aliases — set from observer state by `step_observer()` / `update_observer_formation()`
        self.cracked = False                 # mirrors observer.coherent
        self.crack_step = None               # set on observer formation
        self.pre_crack_D = None              # D_eff at observer coherence transition
        self.metacognition_observations = 0  # mirrors observer.coherent_steps
        # Counterfactual tracking (unchanged from v37.2 — used for paired-cohort analysis)
        self.would_have_cracked = False
        self.would_have_cracked_step = None
        # v37 sustain counter retained as no-op for diagnostic comparison; v37.3 uses observer formation
        self.crack_window_steps = 0

        # v33.1: dimensional trajectory — for cultural self-regulation
        self.peak_D = 3.0              # highest D_eff ever reached
        self.D_at_worst_C = 3.0        # D_eff when C was lowest
        self.worst_C = 1.0             # lowest C experienced (for collapse detection)
        self.taught_D_caution = None   # learned from theocrat: "be careful above this D"
        # Ch 3 refactor (Salazaar amendment #4, 2026-07-01): separate field
        # for observer-derived caution. Two writers with independent info
        # (memoir historical wisdom vs observer forward prediction) merge at
        # the consumer via effective_D_caution() min-with-None-handling.
        self.canonical_D_caution = None  # v37.4 rename: formerly observer_D_caution.
                                          # Single-source-of-truth for Channel 3.
        self.D_collapse_count = 0      # how many times C dropped below 0.3 at high D
        # v37.4 Stage 2 -- LEAK_TEST_MODE test-only pathway (bypasses canonical surface).
        # Eighth addendum (2026-10-09): relocated from refusal_chance to burn_decay
        # after per_channel_activation_audit_2026-10-08.json showed refusal MARGINAL
        # (~6 activations/seed; near N_LEAK_ACTED_MIN=3 so Gate 1 Exercise 1 would
        # likely come back INVALID). burn_decay is HIGH (2500 activations/seed;
        # clears the floor by three orders of magnitude). Read site: get_burn_decay.
        self._test_leak_burn_decay_mult = None

        # Canonical observer-channel values (2026-10-04 Nymph/Harley fix).
        # Single source of truth: both sim use-sites and channel_snapshots
        # logger read from these attributes. Written once per step by
        # canonicalize_observer_channels(). Prevents the sim-vs-logger
        # duplication bug class (one gate, in one place, both values
        # can differ in cost on purpose and never disagree on coherence).
        self.canonical_burn_decay_mult = 1.0
        self.canonical_trauma_decay_exp = 1.0
        self.canonical_refusal_chance = SACRIFICE_REFUSAL_CHANCE
        # Diagnostic reference at cost=0.1 (preserved from v0.1 harness).
        # EXCLUDED from kill criterion. See stage_1_prereg_second_addendum.
        self.refusal_prob_ref_cost_0_1 = SACRIFICE_REFUSAL_CHANCE

    # === v37.3: STRUCTURAL METACOGNITION METHODS ===
    #
    # Replaces v37: check_crack + observe_self with a sustained-pressure
    # formation gate + step_observer prediction update. The Observer
    # dataclass (observer.py) holds the new state; this class hosts the
    # update entry points. See `Seeds/The Crack/structural_metacognition_design_v0.1.md`.

    def update_sustained_pressure(self, t):
        """v37.3: Compute and append per-step pressure to the rolling window.

        Pressure formula (design v0.1):
          max(0, burn_rate - BURN_RATE_BASELINE)
          + max(0, shame_tail - SHAME_BASELINE)
          + (1 if trauma received this step else 0)

        Returns the sum over SUSTAINED_PRESSURE_WINDOW (used as the
        formation-gate score).
        """
        received_trauma = bool(
            self.trauma_events and self.trauma_events[-1][0] == t
        )
        pressure_now = (
            max(0.0, self.current_burn_rate - BURN_RATE_BASELINE) +
            max(0.0, self.shame_tail - SHAME_BASELINE) +
            (1.0 if received_trauma else 0.0)
        )
        self.sustained_pressure_history.append(pressure_now)
        return sum(self.sustained_pressure_history)

    def update_observer_formation(self, t):
        """v37.3: Replaces v37's check_crack. Observer forms when sustained-
        pressure score exceeds FORMATION_THRESHOLD. crack_enabled=False
        agents track the counterfactual formation step but do not form
        an observer — preserves v37.2's paired-cohort comparison.

        Returns True only on the transition (newly formed); False
        otherwise. Existing observers return False (no double-formation).
        """
        if self.observer.exists:
            return False

        score = self.update_sustained_pressure(t)
        if score <= FORMATION_THRESHOLD:
            return False

        if self.crack_enabled:
            form_observer(
                self.observer,
                t,
                self.sustained_pressure_history,
                initial_C=self.C,
                initial_burn_rate=self.current_burn_rate,
            )
            self.crack_step = t  # legacy alias — set on formation
            # v37.2 applied CRACK_STABILITY_COST_C/_S here; v37.3 treats
            # observer formation as predictive machinery coming online,
            # not a stability event. No immediate C/S cost. (v0.2 may
            # reintroduce if the kill-test motivates it.)
            return True
        else:
            # Counterfactual: crack-disabled agents log when they would
            # have formed an observer (paired-cohort comparison).
            if not self.would_have_cracked:
                self.would_have_cracked = True
                self.would_have_cracked_step = t
            return False

    def step_observer(self, t):
        """v37.3: Per-agent per-step observer update.

        Runs prediction updates across four channels (C, burn_rate,
        trauma_arrival, recovery_time), promotes to coherent when the
        gate clears, and syncs legacy aliases (`self.cracked`,
        `self.metacognition_observations`, `self.pre_crack_D`) so v37.2's
        downstream code keeps working.

        Task D (2026-10-12): reactive arm uses replay-driven coherence.
        In reactive mode, maybe_promote_to_coherent is skipped entirely;
        observer.coherent is set from replay_coherence_timeline each step.
        Three cases logged per eighth addendum §2b-c spec (Nymph/Sal 015).
        """
        # Reactive arm: replay-driven coherence replaces native gate.
        # Checked BEFORE observer.exists early-exit so Case B (hot coherent,
        # reactive observer not formed yet) can be logged.
        if self.reactive_mode and self.replay_coherence_timeline is not None:
            key = (self.id, t)
            hot_coherent = self.replay_coherence_timeline.get(key, None)
            if hot_coherent is None:
                # Case A: key not in timeline (agent not present in hot run at this step)
                self.observer.coherent = False
                self._replay_fallback_a += 1
            elif hot_coherent is True and not self.observer.exists:
                # Case B: formation-divergence — hot was coherent but reactive
                # observer hasn't formed yet. Log it; coherent flag set but
                # downstream is_coherent() path requires observer.exists.
                self._replay_divergence_b += 1
                self.observer.coherent = True
            else:
                # Case C: clean replay — set coherent directly from hot's record
                self.observer.coherent = hot_coherent

            if not self.observer.exists:
                return

            actuals = {
                'C':              float(self.C),
                'burn_rate':      float(self.current_burn_rate),
                'trauma_arrival': self._estimate_steps_to_next_trauma(),
                'recovery_time':  self._estimate_recent_recovery_time(),
            }
            step_predictions(self.observer, actuals)
            self._apply_reactive_override(actuals)

            # coherent_steps maintained by replay logic only; native
            # maybe_promote_to_coherent is skipped in reactive mode.
            if self.observer.coherent and self.observer.exists:
                self.observer.coherent_steps += 1
                self.observer.post_coherence_variance_log.append(
                    self.observer.prediction_variance)

            # Legacy alias sync (same as native path)
            self.cracked = is_coherent(self.observer)
            self.metacognition_observations = self.observer.coherent_steps
            if self.observer.coherent and self.pre_crack_D is None:
                self.pre_crack_D = float(self.D_eff)

            if is_coherent(self.observer):
                collapse_L = collapse_likelihood(
                    self.observer.predicted_C,
                    self.observer.predicted_burn_rate,
                )
                self.canonical_D_caution = D_MAX - collapse_L * D_CAUTION_SCALE
                if LEAK_TEST_MODE:
                    self._test_leak_burn_decay_mult = 0.5
            return

        # Non-reactive path (native coherence gate)
        if not self.observer.exists:
            return

        actuals = {
            'C':              float(self.C),
            'burn_rate':      float(self.current_burn_rate),
            'trauma_arrival': self._estimate_steps_to_next_trauma(),
            'recovery_time':  self._estimate_recent_recovery_time(),
        }

        step_predictions(self.observer, actuals)

        # Reactive fifth arm (F5): overwrite predictions with current
        # retrospective estimates so channels modulate on actuals, not
        # on the observer's learned predictions. Applied AFTER step_predictions
        # so the observer's own prediction machinery still runs (variance +
        # PE history stay valid for coherence gate + logging), but downstream
        # channel consumers see predicted == actual.
        if self.reactive_mode:
            self._apply_reactive_override(actuals)

        became_coherent = maybe_promote_to_coherent(self.observer, t)

        # Legacy alias sync (spec: self.cracked = self.observer.coherent)
        self.cracked = is_coherent(self.observer)
        self.metacognition_observations = self.observer.coherent_steps
        if became_coherent and self.pre_crack_D is None:
            self.pre_crack_D = float(self.D_eff)

        # Channel 3 wired 2026-07-01, refactored per Salazaar amendment #4:
        # observer-derived D-caution from forward prediction (design v0.1
        # §Channel 3).
        #   collapse_L = collapse_likelihood(predicted_C, predicted_burn)
        #   observer_D_caution = D_MAX - collapse_L * D_CAUTION_SCALE
        # Only fires when observer is coherent. Writes to observer_D_caution,
        # NOT taught_D_caution — memoir-teaching writes to taught_D_caution;
        # consumer (effective_D_caution) merges via min-with-None-handling
        # so observer strictifies memoir but never relaxes it.
        if is_coherent(self.observer):
            collapse_L = collapse_likelihood(
                self.observer.predicted_C,
                self.observer.predicted_burn_rate,
            )
            self.canonical_D_caution = D_MAX - collapse_L * D_CAUTION_SCALE
            # Eighth addendum (2026-10-09): LEAK on burn_decay, gated on observer
            # coherence (observer->world pathway, not unconditional bypass). Writes
            # non-canonical attribute; get_burn_decay reads it with counter. 0.5
            # multiplier halves burn decay when LEAK fires -- strong forcing for
            # clearly resolvable divergence in burn_integral.
            if LEAK_TEST_MODE:
                self._test_leak_burn_decay_mult = 0.5

    def _apply_reactive_override(self, actuals):
        """Reactive fifth arm (external audit F5, 2026-07-01): overwrite the
        observer's predicted_* fields with the current retrospective
        estimates used for `actuals`. Channels then modulate as thermostats
        rather than as predictions.

        Called only when self.reactive_mode is True. Leaves the observer's
        prediction_error_history and prediction_variance untouched — those
        already reflect what step_predictions computed against the (now-
        overwritten) predictions, so the coherence gate and F7 log continue
        to work.
        """
        self.observer.predicted_C = actuals['C']
        self.observer.predicted_burn_rate = actuals['burn_rate']
        self.observer.predicted_trauma_arrival = actuals['trauma_arrival']
        self.observer.predicted_recovery_time = actuals['recovery_time']

    def _estimate_steps_to_next_trauma(self):
        """Heuristic estimate of steps until next trauma event.

        Uses recent trauma_events cadence; returns a large value
        (interpreted by the observer as "calm") when history is short.
        """
        if not self.trauma_events or len(self.trauma_events) < 2:
            return 1000.0
        recent = self.trauma_events[-5:]
        intervals = [recent[i + 1][0] - recent[i][0] for i in range(len(recent) - 1)]
        if not intervals:
            return 1000.0
        return float(sum(intervals)) / len(intervals)

    def _estimate_recent_recovery_time(self):
        """Heuristic estimate of steps until trauma_C_penalty fully decays.

        Uses the base non-cracked decay constant (0.993) for the
        projection — the observer trains on this signal even though the
        true decay depends on observer state.
        """
        if self.trauma_C_penalty <= 0.001:
            return 0.0
        try:
            steps = math.log(0.001 / self.trauma_C_penalty) / math.log(0.993)
            return max(0.0, steps)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def canonicalize_observer_channels(self):
        """2026-10-04: compute and store canonical observer-channel values.

        Called once per agent per step at the top of the step loop. Both
        the sim's use-sites and the channel_snapshots logger read from the
        stored attributes. Single gate (is_coherent) in one place.

        canonical_refusal_chance uses the simulation's operational cost
        SACRIFICE_COHERENCE_COST (0.04). This value feeds Channel 2 μ in
        compute_paired_deltas and is used by the sacrifice gate.

        refusal_prob_ref_cost_0_1 is a diagnostic reference at cost=0.1,
        preserved for cross-version comparability. EXCLUDED from the kill
        criterion. See stage_1_prereg_second_addendum_2026-10-04.md.
        """
        self.canonical_burn_decay_mult = burn_decay_multiplier_from_observer(self.observer)
        self.canonical_trauma_decay_exp = trauma_decay_exponent_from_observer(self.observer)
        if is_coherent(self.observer):
            self.canonical_refusal_chance = refusal_probability_from_observer(
                self.observer, SACRIFICE_COHERENCE_COST, SAFETY_FLOOR_C)
            self.refusal_prob_ref_cost_0_1 = refusal_probability_from_observer(
                self.observer, 0.1, SAFETY_FLOOR_C)
        else:
            self.canonical_refusal_chance = SACRIFICE_REFUSAL_CHANCE
            self.refusal_prob_ref_cost_0_1 = SACRIFICE_REFUSAL_CHANCE

    def get_burn_decay(self, has_warm_mentor):
        """v37.3 Channel 1: observer-modulated burn-decay multiplier.

        Replaces v37.2's `if self.cracked:` branch in update_burn_rate.
        Coherent observers slow decay slightly when predicting a longer
        recovery; otherwise base ADULT_BURN_DECAY (with mentor variant)
        applies unchanged.

        2026-10-04: reads canonical_burn_decay_mult (stored by
        canonicalize_observer_channels) instead of recomputing.

        Eighth addendum (2026-10-09): LEAK read + activation counter here
        after per_channel_activation_audit established burn_decay as the only
        HIGH-activation canonical channel (2500/seed). Counter increments at
        this decision site (not the write site) per seventh-addendum section
        4c discipline.
        """
        base = ADULT_BURN_DECAY_WITH_MENTOR if has_warm_mentor else ADULT_BURN_DECAY
        multiplier = self.canonical_burn_decay_mult

        # Eighth addendum (2026-10-09) section 4b/4c: LEAK read at the burn_decay
        # decision site. Activation counter increments HERE so Gate 1 Exercise 1
        # can prove the leak acted on the burn-decay pathway before trusting any
        # PASS/FAIL verdict. INVALID is the honest third state when
        # N_leak_acted < N_LEAK_ACTED_MIN=3.
        if LEAK_TEST_MODE and getattr(self, '_test_leak_burn_decay_mult', None) is not None:
            multiplier = min(multiplier, self._test_leak_burn_decay_mult)
            global _LEAK_ACTIVATION_COUNT
            _LEAK_ACTIVATION_COUNT += 1

        return base * multiplier

    def effective_D_caution(self):
        """v37.3 Channel 3: merged D-caution consumer.

        Salazaar amendment #4 (2026-07-01) — memoir path and observer path
        write to independent fields carrying complementary information.
        Consumer takes the min so observer can strictify memoir teaching
        but never relax it. Returns None only when both writers are silent.

        - taught_D_caution: population-level historical D-collapse wisdom
          from ancestors via theocrat
        - observer_D_caution: per-agent forward prediction from coherent
          observer model (Channel 3)
        """
        if self.taught_D_caution is None and self.canonical_D_caution is None:
            return None
        if self.taught_D_caution is None:
            return self.canonical_D_caution
        if self.canonical_D_caution is None:
            return self.taught_D_caution
        return min(self.taught_D_caution, self.canonical_D_caution)

    # === v33: BURN RATE METHODS ===

    def get_active_burn_rate(self):
        """Return the burn rate that applies RIGHT NOW.
        Pre-adult: birth_burn_rate (you don't pick your childhood).
        Adult+: current_burn_rate (you can build shelter)."""
        if self.stage in PRE_ADULT_STAGES:
            return self.birth_burn_rate
        return self.current_burn_rate

    def update_burn_rate(self, agents):
        """Called each step for adults+. Slowly decay burn rate toward floor.
        Mentor with low burn rate accelerates healing.
        v37.3: Replaces cracked-branch (CRACK_BURN_DECAY constants) with
        observer-modulated multiplier via Channel 1 (`get_burn_decay`).
        """
        if self.stage in PRE_ADULT_STAGES:
            return  # Children can't change their weather

        # Check for warm-room mentor
        has_warm_mentor = False
        if self.mentor_id is not None:
            mentor = next((a for a in agents if a.id == self.mentor_id), None)
            if mentor and mentor.current_burn_rate < 0.08:
                has_warm_mentor = True

        # v37.3 Channel 1: observer-modulated burn decay
        decay = self.get_burn_decay(has_warm_mentor)
        self.current_burn_rate = max(BURN_FLOOR, self.current_burn_rate * decay)

    # === SAFETY & CURIOSITY METHODS ===

    def compute_safety(self):
        """Safety = rolling average of recent coherence stability.
        High C + low variance = safe. Low C or high variance = unsafe."""
        if len(self.C_recent) < 10:
            return 0.0
        recent = np.array(self.C_recent[-SAFETY_WINDOW:])
        mean_c = np.mean(recent)
        var_c = np.var(recent)
        stability = max(0.0, 1.0 - var_c * 50)
        self.safety = np.clip(mean_c * stability, 0.0, 1.0)
        return self.safety

    def check_curiosity(self):
        """Curiosity activates when safety exceeds threshold and mode is expansive.
        Modulated by stage-based affinity."""
        affinity = CURIOSITY_AFFINITY_BY_STAGE.get(self.stage, 1.0)
        threshold = CURIOSITY_THRESHOLD / max(0.1, affinity)
        threshold = np.clip(threshold, 0.3, 0.9)
        self.is_curious = self.safety > threshold and self.mode == Mode.EXPANSIVE
        if self.is_curious:
            self.curiosity_steps += 1
        return self.is_curious

    def apply_safety_floor(self):
        """The warm room. C can't fall below the floor.
        Applies to ALL agents in v33 — everyone gets the emergency net."""
        if self.C < SAFETY_FLOOR_C:
            recovery = (SAFETY_FLOOR_C - self.C) * SAFETY_RECOVERY_BONUS
            self.C = SAFETY_FLOOR_C
            self.M_memory += recovery * 0.1
            self.safety_floor_catches += 1
            return True
        return False

    def explore(self, other_agents, t):
        """Curiosity-driven exploration. The agent reaches out.
        v33: What meets the hand depends on current_burn_rate, not cohort."""
        if not self.is_curious or not other_agents:
            return

        # Pick someone to explore toward — weighted by difference
        weights = []
        for other in other_agents:
            if other.id == self.id:
                weights.append(0.0)
                continue
            d_diff = abs(self.D_eff - other.D_eff)
            c_diff = abs(self.C - other.C)
            novelty = d_diff + c_diff
            weights.append(novelty + 0.1)

        weights = np.array(weights)
        if weights.sum() == 0:
            return
        weights /= weights.sum()

        rng = np.random.default_rng(t * 1000 + self.id + _AGENT_RNG_SALT)
        target_idx = rng.choice(len(other_agents), p=weights)
        target = other_agents[target_idx]

        affinity = CURIOSITY_AFFINITY_BY_STAGE.get(self.stage, 1.0)
        absorption = CURIOSITY_EXPLORE_RATE * EXPLORE_ABSORPTION_RATE * affinity

        # You always learn from reaching — M_memory grows regardless
        self.M_memory += absorption * 0.05

        # v33: Roll against active burn rate
        burn_rate = self.get_active_burn_rate()
        if rng.random() < burn_rate:
            # Burned. You reached out and got hurt.
            self.C = max(0.0, self.C - CURIOSITY_GROWTH_BONUS * 3)
            self.S = min(1.0, self.S + 0.01)
            # Embedding scar from reaching burn
            scar_direction = self.emb - BASE_EMB_FLAT
            scar_direction = scar_direction / (jnp.linalg.norm(scar_direction) + 1e-8)
            self.emb = self.emb + scar_direction * burn_rate * 0.1
        else:
            # Warmth. The reach was met with a warm hand.
            self.D_eff += (target.D_eff - self.D_eff) * absorption * 0.1
            self.C = min(self.C + CURIOSITY_GROWTH_BONUS, self.get_C_cap())

        self.explore_events += 1
        self.explore_absorptions += 1

    # === ORIGINAL v26 METHODS ===

    def get_C_cap(self):
        base_cap = STAGE_CONFIG[self.stage]["C_cap"]
        if self.D_eff > 3.0:
            d_bonus = min((self.D_eff - 3.0) * C_CAP_SCALE_FACTOR, 0.15)  # v35.2: capped (Annie)
            return min(1.0, base_cap + d_bonus)
        return base_cap

    def get_beta_scaled(self):
        if self.D_eff >= 3.0:
            # v35.3: asymptotic beta — saturates instead of growing linearly (Buzz)
            # beta approaches DIM_BETA + 0.05 asymptotically. Can't outrun drag.
            d_bonus = 0.05 * (1.0 - math.exp(-(self.D_eff - 3.0) / 5.0))
            return DIM_BETA + d_bonus
        return DIM_BETA

    def get_G_sigma(self):
        return STAGE_CONFIG[self.stage]["G_sigma"]

    def get_spine_pull(self):
        return STAGE_CONFIG[self.stage]["spine_pull"]

    def can_energy_sacrifice(self, t):
        return (self.stage_idx >= STAGE_ORDER.index("ADULT") and
            self.C >= SACRIFICE_ADULT_MIN_C and
            t - self.last_sacrifice_step >= SACRIFICE_COOLDOWN)

    def can_mentor(self):
        return self.stage_idx >= STAGE_ORDER.index("ADULT")

    def needs_mentor(self):
        return self.stage_idx < STAGE_ORDER.index("ADULT") and self.mentor_id is None

    def add_sacrifice_credit(self, amount, t):
        self.sacrifice_credit += amount
        self.last_credit_gain_step = t

    def receive_praise(self, praise_type, amount_credit, amount_C, mentee_id, t):
        self.add_sacrifice_credit(amount_credit, t)
        self.C = min(self.get_C_cap(), self.C + amount_C)
        self.praise_events.append({
            'step': t, 'type': praise_type,
            'mentee_id': mentee_id, 'credit': amount_credit, 'C_bump': amount_C
        })

    def update_dimensional_state(self, dt, global_culture, collective_memory):
        prev_D = self.D_eff
        M_saturation = 20.0 + (self.D_eff ** 0.5) * 2.0  # v35.2: sub-linear (Annie)
        saturation_factor = max(0.01, 1.0 - (self.M_memory / M_saturation))
        dM = (DIM_P * (self.C + global_culture * 0.1 + collective_memory * 0.05)
              - DIM_Q * self.M_memory) * saturation_factor
        self.M_memory = max(0.0, self.M_memory + dM * dt)

        dn = DIM_ETA * (self.D_eff - 2.0) - DIM_XI * self.n_entropy
        self.n_entropy = max(0.0, self.n_entropy + dn * dt)

        coherence_feedback = f_coherence_response(self.C, DIM_C_THRESHOLD)
        dD = (-DIM_ALPHA * (self.D_eff - 2.0)
            - DIM_GAMMA * self.n_entropy
            + self.get_beta_scaled() * self.M_memory
            + DIM_LAMBDA * coherence_feedback)
        # v33.1: dimensional caution — if taught, resist expansion past caution threshold
        # Salazaar amendment #4 (2026-07-01): consumer now reads effective_D_caution()
        # which merges memoir-teaching (taught_D_caution) and observer-forward-prediction
        # (observer_D_caution) via min-with-None-handling. Observer strictifies but
        # never relaxes memoir protection.
        effective_caution = self.effective_D_caution()
        # Seventh addendum (2026-10-08): D_caution LEAK removed. The channel is
        # behaviorally inert in current regime (dampening_firing_probe_2026-10-08:
        # 0 events across 43,500 agent-step tuples; max D_eff ~5 vs threshold ~48).
        # LEAK moved to refusal_chance; read site is sacrifice gate.
        if effective_caution is not None and dD > 0 and self.D_eff > effective_caution:
            # Fear vs curiosity modulates how much the agent listens
            burn_rate = self.get_active_burn_rate()
            # High burn = more fear = more caution. Low burn = more courage = less caution.
            fear_factor = 0.3 + burn_rate * 2.0  # 0.3 (brave) to ~1.0 (fearful)
            fear_factor = min(1.0, fear_factor)
            # Curious agents discount the caution
            if self.is_curious:
                fear_factor *= 0.6  # curiosity reduces fear by 40%
            dD *= (1.0 - fear_factor)  # dampen expansion

        self.D_eff = float(jnp.clip(self.D_eff + dD * dt, D_MIN, D_MAX))

        # v35.3: stage-gated D caps — babies don't get the car keys (Annie)
        STAGE_D_CAP = {"INFANT": 5.0, "JUVENILE": 8.0, "APPRENTICE": 12.0}
        if self.stage in STAGE_D_CAP:
            self.D_eff = min(self.D_eff, STAGE_D_CAP[self.stage])

        self.D_history.append(self.D_eff)

        # v33.1: track peak D and collapse events
        if self.D_eff > self.peak_D:
            self.peak_D = self.D_eff
        if self.C < self.worst_C:
            self.worst_C = self.C
            self.D_at_worst_C = self.D_eff
        if self.C < 0.3 and self.D_eff > 10.0:
            self.D_collapse_count += 1

        self.detect_phase_transitions(prev_D, self.D_eff)

        if self.D_eff < 2.0:
            self.sub_holographic_steps += 1
        elif self.D_eff >= 4.0:
            self.transcendent_steps += 1
        elif self.D_eff >= 3.0:
            self.hyperspace_steps += 1

        return (self.D_eff - 2.0) * 0.02

    def detect_phase_transitions(self, prev_D, curr_D):
        if prev_D >= 2.0 > curr_D:
            self.last_D_phase = "sub_holographic"
        elif prev_D < 2.0 <= curr_D:
            self.last_D_phase = "conscious"
        if prev_D < 3.0 <= curr_D:
            self.last_D_phase = "hyperspace"
        elif prev_D >= 3.0 > curr_D:
            self.last_D_phase = "conscious"
        if prev_D < 4.0 <= curr_D:
            self.last_D_phase = "transcendent"
        elif prev_D >= 4.0 > curr_D:
            self.last_D_phase = "hyperspace"

    def calculate_sacrifice_cost(self, recipient):
        base_cost = 0.03
        if recipient.D_eff < 2.0:
            sub_holo_gap = 2.0 - recipient.D_eff
            base_cost *= 1 + (sub_holo_gap * SACRIFICE_SUB_HOLO_PENALTY)
        return base_cost

    def update_tcr_truth(self, crisis_detected):
        if self.T_m > 0.5 and not crisis_detected:
            self.truth_score *= TCR_TRUTH_DECAY
        elif self.C < 0.3 and self.T_m < 0.3:
            self.truth_score = min(1.0, self.truth_score + TCR_TRUTH_RECOVERY)
        return self.truth_score * 0.0005

    def attempt_sacrifice_with_choice(self, target, t):
        if not self.can_energy_sacrifice(t):
            return False

        # Channel 2 wired 2026-07-01: sacrifice refusal from observer's
        # predicted-C floor breach margin (design v0.1 §Channel 2). Coherent
        # observer → sigmoid on (SAFETY_FLOOR_C - (predicted_C - cost)) /
        # FLOOR_BREACH_SCALE, so predicted post-sacrifice C at floor gives
        # 50% refusal, well above gives ~0, well below gives ~1. Incoherent
        # observer falls back to baseline 10% random refusal. Replaces v35
        # piecewise on ACTUAL self.C gated on the `cracked` alias — refusal
        # is now PREDICTIVE, not reactive.
        # CRACK_REFUSAL_C_GENEROUS/PROTECT constants at :293-294 retained
        # cosmetic only (banner + potential v0.2 reference).
        # 2026-10-04: read canonical_refusal_chance (stored by
        # canonicalize_observer_channels at top of step). Single gate, one place.
        refusal_chance = self.canonical_refusal_chance

        # Eighth addendum (2026-10-09): LEAK read removed from sacrifice gate.
        # refusal_chance was MARGINAL (~6 activations/seed per
        # per_channel_activation_audit_2026-10-08.json), near N_LEAK_ACTED_MIN=3;
        # Gate 1 Exercise 1 would likely come back INVALID. LEAK moved to
        # get_burn_decay (HIGH channel, 2500 activations/seed).

        if random.random() < refusal_chance:
            self.C -= TCR_REFUSAL_COST
            return False
        cost = self.calculate_sacrifice_cost(target)
        self.E_G = max(0.01, self.E_G - cost)
        self.C = max(0.1, self.C - SACRIFICE_COHERENCE_COST)
        self.last_sacrifice_step = t
        self.add_sacrifice_credit(1.0, t)
        target.E_G = min(1.0, target.E_G + cost)
        self.total_sacrifice_given += SACRIFICE_ENERGY_AMOUNT
        target.total_sacrifice_received += SACRIFICE_ENERGY_AMOUNT
        return True

    def apply_recursive_descent_guarantee(self, t):
        if self.C < 0.3:
            self.T_m = min(0.95, self.T_m + TCR_CRISIS_MENTOR_SURGE)
            return True
        return False

    def perceive_society_mxp(self, agents):
        if self.stage != "ELDER":
            return None
        avg_D = np.mean([a.D_eff for a in agents])
        target_D = 2.8
        semantic_align = np.exp(-((avg_D - target_D)**2) / (2 * 0.3**2))
        coherences = [a.C for a in agents]
        affective_align = 1.0 - np.std(coherences)
        avg_C = np.mean(coherences)
        avg_conf = np.mean([a.sacrifice_credit for a in agents]) / 1000
        g = np.sqrt(semantic_align * affective_align) * np.sqrt(avg_C * avg_conf)
        if self.D_eff > 3.0:
            d_enhancement = (self.D_eff - 3.0) * MXP_HIGH_D_ENHANCEMENT
            g = min(1.0, g * (1 + d_enhancement))
        H = (avg_D - 2.0) * 360
        S = affective_align
        V = avg_conf
        self.mxp_buffer.append(g)
        return {
            'global_coherence': g, 'semantic_align': semantic_align,
            'affective_align': affective_align, 'hsv': (H, S, V),
            'dimensional_health': avg_D,
            'action': self.determine_elder_action(g, avg_D)
        }

    def determine_elder_action(self, g, d_health):
        if self.D_eff >= 4.0:
            return "transcend" if g > 0.85 else "pulse"
        if self.D_eff >= 3.0:
            if g > 0.75: return "lock"
            elif g > 0.4: return "pulse"
            else: return "clarify"
        if g > 0.75: return "lock"
        elif g > 0.4: return "pulse"
        else: return "clarify"

    def is_council_eligible(self, t):
        return (self.stage == "MENTOR" and
            self.steps_in_stage >= COUNCIL_MIN_STEPS_AS_MENTOR and
            self.sacrifice_credit >= COUNCIL_MIN_CREDIT)

    def promote_by_council(self, t):
        old = self.stage
        self.stage_idx = STAGE_ORDER.index("STEWARD")
        self.stage = "STEWARD"
        self.steps_in_stage = 0
        self.C_floor_in_stage = 1.0
        self.steward_step = t
        self.promoted_by_council = True
        self.promotions.append((t, old, self.stage))
        return {'agent_id': self.id, 'old_stage': old, 'new_stage': self.stage}

    def can_elder_promote(self):
        return (self.stage == "STEWARD" and
            self.steps_in_stage >= ELDER_COUNCIL_PROMOTION_STEPS and
            self.sacrifice_credit >= ELDER_COUNCIL_PROMOTION_CREDIT)

    def promote_to_elder(self, t):
        old = self.stage
        self.stage_idx = STAGE_ORDER.index("ELDER")
        self.stage = "ELDER"
        self.steps_in_stage = 0
        self.C_floor_in_stage = 1.0
        self.elder_step = t
        self.promotions.append((t, old, self.stage))
        self.C = float(jnp.clip(self.C + 0.02, 0.0, 1.0))
        self.C_history = []
        self.S_history = []
        return {'agent_id': self.id, 'old_stage': old, 'new_stage': self.stage}

    def can_sage_promote(self):
        return (self.stage == "ELDER" and
            self.steps_in_stage >= 5000 and
            self.sacrifice_credit >= 800 and
            self.D_eff >= 4.0 and
            self.mentoring_score >= 1.0)

    def promote_to_sage(self, t):
        old = self.stage
        self.stage_idx = STAGE_ORDER.index("SAGE")
        self.stage = "SAGE"
        self.is_sage = True
        self.steps_in_stage = 0
        self.C_floor_in_stage = 1.0
        self.sage_step = t
        self.promotions.append((t, old, self.stage))
        promo_credit = 400 + random.uniform(100, 200)
        self.sacrifice_credit += promo_credit
        self.C = float(jnp.clip(self.C + 0.03, 0.0, 1.0))
        self.C_history = []
        self.S_history = []
        return {'agent_id': self.id, 'old_stage': old, 'new_stage': self.stage}

    def check_elder_accountability(self, t):
        if self.stage != "ELDER" or len(self.C_history) < 50:
            return False
        mean_C = np.mean(self.C_history[-50:])
        mean_S = np.mean(self.S_history[-50:])
        if mean_C < ELDER_MIN_C:
            self._elder_fall(t, f"coherence dropped to {mean_C:.3f}")
            return True
        if mean_S > ELDER_MAX_S:
            self._elder_fall(t, f"strain rose to {mean_S:.3f}")
            return True
        if t - self.last_credit_gain_step > ELDER_INACTIVE_THRESHOLD:
            self._elder_fall(t, f"inactive for {t - self.last_credit_gain_step} steps")
            return True
        return False

    def can_theocrat_promote(self, available_memoirs):
        if self.stage != "SAGE":
            return False
        unclaimed = [m for m in available_memoirs if m['claimed_by_theocrat'] is None]
        if not unclaimed:
            return False
        return self.steps_in_stage >= 3000 and random.random() < 0.15

    def promote_to_theocrat(self, t, available_memoirs, cultural_memory_ref, collective_memory_ref):
        """Sage chooses Theocrat path - claims a memoir to steward.
        Returns (promo_event, cultural_delta, collective_delta) or (None, 0, 0)."""
        unclaimed = [m for m in available_memoirs if m['claimed_by_theocrat'] is None]
        if not unclaimed:
            return None, 0, 0

        memoir = unclaimed[0]
        memoir['claimed_by_theocrat'] = self.id
        memoir['claimed_step'] = t
        memoir['theocrat_history'].append({'theocrat_id': self.id, 'claim_step': t, 'release_step': None})
        self.claimed_memoir_id = memoir['id']

        cultural_delta = 0.02
        collective_delta = memoir['quality'] * 0.01

        memory_gift = memoir['quality'] * 0.03
        self.M_memory += memory_gift

        old = self.stage
        self.stage_idx = STAGE_ORDER.index("THEOCRAT")
        self.stage = "THEOCRAT"
        self.steps_in_stage = 0
        self.C_floor_in_stage = 1.0
        self.promotions.append((t, old, self.stage))

        return ({'agent_id': self.id, 'old_stage': old, 'new_stage': self.stage,
                 'memoir_id': memoir['id']}, cultural_delta, collective_delta)

    def can_transition_to_ancestor(self):
        dimensional_wisdom = np.mean(self.D_history) if self.D_history else self.D_eff
        lineage_impact = (
            self.mentee_recoveries_witnessed +
            self.mentees_became_mentors * 2 +
            self.mentees_became_stewards * 3 +
            self.mentees_became_elders * 5 +
            self.mentees_became_sages * 10
        )
        self.potential_memoir_quality = dimensional_wisdom * lineage_impact
        return (self.stage == "SAGE" and
            self.steps_in_stage >= 2000 and
            self.D_eff >= 4.5 and
            self.sacrifice_credit >= 1000 and
            self.potential_memoir_quality >= 100.0)

    def transition_to_ancestor(self, t, agents, available_memoirs, memoir_id_counter,
                                cultural_memory, collective_memory):
        """Returns (new_agent_id, memoir_id_counter, cultural_delta, collective_delta, memoir)"""
        dimensional_wisdom = np.mean(self.D_history) if self.D_history else self.D_eff
        lineage_impact = (
            self.mentee_recoveries_witnessed +
            self.mentees_became_mentors * 2 +
            self.mentees_became_stewards * 3 +
            self.mentees_became_elders * 5 +
            self.mentees_became_sages * 10
        )
        memoir_quality = dimensional_wisdom * lineage_impact

        # v33: Curiosity enriches memoir quality for all agents
        curiosity_bonus = self.curiosity_steps * 0.001
        exploration_bonus = self.explore_events * 0.01
        memoir_quality += curiosity_bonus + exploration_bonus

        # Channel 5 wired 2026-07-01: memoir quality bonus from observer's
        # coherence duration × prediction accuracy (design v0.1 §Channel 5).
        #   bonus = coherent_steps * 0.005 * accuracy_factor
        #   accuracy_factor = 1 / (1 + normalized_mean_abs_PE)
        # Both coherence duration AND prediction accuracy contribute. Hot
        # observer with high error → modest bonus. Sharp observer → full
        # bonus per coherent step. No observer or zero coherent_steps → 0.
        # Replaces `metacognition_observations * 0.005` without accuracy
        # factor. Guards are inside observer_quality_bonus.
        memoir_quality += observer_quality_bonus(self.observer)

        # v33: Burn journey — how much shelter this agent built
        final_burn_rate = self.current_burn_rate
        burn_journey = self.birth_burn_rate - final_burn_rate

        memoir = {
            'id': memoir_id_counter,
            'sage_id': self.id,
            'sage_generation': self.generation,
            'quality': memoir_quality,
            'created_step': t,
            'claimed_by_theocrat': None,
            'claimed_step': None,
            'theocrat_history': [],
            'birth_burn_rate': self.birth_burn_rate,        # v33
            'final_burn_rate': final_burn_rate,             # v33
            'burn_journey': burn_journey,                   # v33
            'curiosity_steps': self.curiosity_steps,
            'explore_events': self.explore_events,
            'peak_D': self.peak_D,                          # v33.1
            'D_at_worst_C': self.D_at_worst_C,              # v33.1
            'worst_C': self.worst_C,                        # v33.1
            'D_collapse_count': self.D_collapse_count,      # v33.1
            'D_at_death': self.D_eff,                       # v33.1
            'crack_enabled': self.crack_enabled,             # v35
            'cracked': self.cracked,                         # v35
            'crack_step': self.crack_step,                   # v35
            'metacognition_observations': self.metacognition_observations,  # v35
        }
        available_memoirs.append(memoir)
        memoir_id_counter += 1

        compressed_knowledge = self.M_memory * 0.1
        cultural_delta = 0.3
        collective_delta = compressed_knowledge

        memoir['compressed_memory'] = compressed_knowledge

        # Create NEW INFANT — new birth_burn_rate drawn fresh
        new_id = max(a.id for a in agents) + 1 if agents else 0
        key = jax.random.PRNGKey(t + new_id + _AGENT_RNG_SALT)
        new_agent = Agent(new_id, key, t, self.generation + 1,
                          reactive_mode=self.reactive_mode,
                          replay_coherence_timeline=self.replay_coherence_timeline)
        agents.append(new_agent)

        self.stage = "ANCESTOR"
        self.stage_idx = STAGE_ORDER.index("ANCESTOR")

        return new_agent.id, memoir_id_counter, cultural_delta, collective_delta, memoir

    def theocrat_act(self, agents, t, available_memoirs, cultural_memory, collective_memory):
        """Returns (cultural_delta, collective_delta)"""
        if self.stage != "THEOCRAT":
            return 0, 0

        memoir = next((m for m in available_memoirs if m['id'] == self.claimed_memoir_id), None)
        if not memoir:
            return 0, 0

        cultural_delta = 0
        collective_delta = 0

        # Scheduled memoir reading (every 500 steps)
        if t - self.last_memoir_reading >= 500:
            self.last_memoir_reading = t
            cultural_delta += 0.01
            collective_delta += memoir['quality'] * 0.0001

            # Teaching: transfer from collective -> personal
            for a in agents:
                if a.stage_idx < STAGE_ORDER.index("MENTOR"):
                    transfer = min(0.015, collective_memory * 0.00001)
                    a.M_memory += transfer
                    a.C = min(a.get_C_cap(), a.C + 0.001)

                    # v33.1: Teach dimensional caution from memoir's D trajectory
                    if memoir.get('D_collapse_count', 0) > 0:
                        # Ancestor collapsed at high D — teach where it got dangerous
                        memoir_danger_D = memoir.get('D_at_worst_C', 50.0)
                        # Caution point = 80% of where ancestor collapsed
                        caution_D = memoir_danger_D * 0.8
                        if a.taught_D_caution is None or caution_D < a.taught_D_caution:
                            a.taught_D_caution = caution_D
                    elif memoir.get('peak_D', 3.0) > 20.0 and memoir.get('worst_C', 1.0) > 0.5:
                        # Ancestor thrived at high D — teach confidence
                        # Only override caution if memoir shows safe expansion
                        if a.taught_D_caution is not None:
                            safe_peak = memoir.get('peak_D', 3.0) * 0.9
                            if safe_peak > a.taught_D_caution:
                                a.taught_D_caution = safe_peak  # raise ceiling

        # Special sermons (rare)
        if random.random() < 0.0002:
            cultural_delta += 0.3

        return cultural_delta, collective_delta

    def _elder_fall(self, t, reason):
        old_stage = self.stage
        self.stage_idx = STAGE_ORDER.index("STEWARD")
        self.stage = "STEWARD"
        self.steps_in_stage = 0
        self.C_floor_in_stage = 1.0
        self.elder_falls.append((t, reason))
        self.regressions.append((t, old_stage, self.stage, "ELDER_FALL", reason))
        burn_tag = f"burn={self.current_burn_rate:.3f}"
        print(f"  ! ELDER FALL: Agent {self.id} fell from ELDER to STEWARD ({reason}) [{burn_tag}]")

    def check_promotion(self, t):
        config = STAGE_CONFIG[self.stage]
        promo = config["promotion"]
        if promo is None:
            self.check_elder_accountability(t)
            return False, None

        self.C_history.append(self.C)
        self.S_history.append(self.S)
        self.C_floor_in_stage = min(self.C_floor_in_stage, self.C)

        if len(self.C_history) < 10 or self.steps_in_stage < promo["min_steps"]:
            return False, None

        mean_C = np.mean(self.C_history[-10:])
        mean_S = np.mean(self.S_history[-10:])

        # v36: S_max removed from promotion gate. S still used for regression check.
        if mean_C < promo["C_min"]:
            self._check_regression(t, mean_C, mean_S)
            return False, None

        if promo.get("shame_tail_max") and self.shame_tail > promo["shame_tail_max"]:
            return False, None
        if promo.get("sacrifice_min") and self.sacrifice_credit < promo["sacrifice_min"]:
            return False, None
        if promo.get("mentoring_score_min") and self.mentoring_score < promo["mentoring_score_min"]:
            return False, None
        if promo.get("C_floor") and self.C_floor_in_stage < promo["C_floor"]:
            return False, None

        if self.stage_idx < len(STAGE_ORDER) - 1:
            old = self.stage
            self.stage_idx += 1
            self.stage = STAGE_ORDER[self.stage_idx]
            self.steps_in_stage = 0
            self.C_floor_in_stage = 1.0
            self.promotions.append((t, old, self.stage))
            self.C_history = []
            self.S_history = []
            if self.stage == "ADULT" and not self.adult_step:
                self.adult_step = t
                # v33: Initialize current_burn_rate at adult transition
                self.current_burn_rate = self.birth_burn_rate
            elif self.stage == "MENTOR" and not self.mentor_step: self.mentor_step = t
            elif self.stage == "STEWARD" and not self.steward_step: self.steward_step = t
            elif self.stage == "ELDER" and not self.elder_step: self.elder_step = t
            elif self.stage == "SAGE" and not self.sage_step: self.sage_step = t
            return True, {'agent_id': self.id, 'old_stage': old, 'new_stage': self.stage}

        return False, None

    def _check_regression(self, t, mean_C, mean_S):
        if self.stage_idx > 0:
            prev = STAGE_CONFIG[STAGE_ORDER[self.stage_idx - 1]]["promotion"]
            # v36: S_max removed from promotion gates. Regression now only on C and C_floor.
            if (mean_C < prev["C_min"] * 0.7 or
                (prev.get("C_floor") and self.C_floor_in_stage < prev["C_floor"] * 0.8)):
                old = self.stage
                self.stage_idx -= 1
                self.stage = STAGE_ORDER[self.stage_idx]
                self.steps_in_stage = 0
                self.C_floor_in_stage = 1.0
                self.regressions.append((t, old, self.stage))
                cohort_tag = "CRACK" if self.crack_enabled else "CTRL"
                cracked_tag = " *CRACKED*" if self.cracked else ""
                print(f"  !! REGRESSION: Agent {self.id} ({cohort_tag}{cracked_tag}) "
                      f"{old} -> {self.stage} | mean_C={mean_C:.3f} mean_S={mean_S:.3f} "
                      f"D={self.D_eff:.3f} [burn={self.get_active_burn_rate():.3f}]")
                self.C_history = []
                self.S_history = []

    def consider_ancestor_reincarnation(self, t, agents, cultural_memory):
        """Returns (bool, cultural_delta)"""
        if self.stage != "SAGE":
            return False, 0
        if self.D_eff < 45 or self.sacrifice_credit < 800 or self.mentoring_score < 1.0:
            return False, 0

        readiness = min(0.05, (self.D_eff - 45)/10 + self.sacrifice_credit/5000)
        if random.random() < readiness:
            memoir_quality = (np.mean(self.D_history) if self.D_history else self.D_eff) * (
                self.mentee_recoveries_witnessed + self.mentees_became_mentors +
                2*self.mentees_became_stewards + 3*self.mentees_became_elders)
            cultural_delta = min(1.0, 0.2 * memoir_quality)

            new_id = max(a.id for a in agents) + 1 if agents else 0
            key = jax.random.PRNGKey(t + new_id + _AGENT_RNG_SALT)
            new_agent = Agent(new_id, key, t, self.generation + 1,
                              reactive_mode=self.reactive_mode,
                              replay_coherence_timeline=self.replay_coherence_timeline)
            new_agent.emb = self.emb * 0.7 + jax.random.normal(key, (16,)) * 0.2
            new_agent.M_memory = min(1.0, self.M_memory * 0.6)
            new_agent.D_eff = 3.0
            new_agent.sacrifice_credit = self.sacrifice_credit * 0.3
            agents.append(new_agent)

            self.stage = "ANCESTOR"
            return True, cultural_delta

        return False, 0


# ============================================================================
# TRAUMA PROCESSING
# ============================================================================

def process_trauma_dimensionally(base_trauma, agent, t):
    if agent.D_eff < 3.0:
        return base_trauma * SHAME_RESISTANCE[agent.stage]
    elif agent.D_eff >= 4.0 and agent.D_eff < 10.0:
        trauma_felt = base_trauma * 0.5
        agent.M_memory += base_trauma * 0.3
        return trauma_felt * SHAME_RESISTANCE[agent.stage]
    elif agent.D_eff >= 10.0:
        trauma_felt = base_trauma * 0.1
        agent.M_memory += base_trauma * 0.5
        return trauma_felt * SHAME_RESISTANCE[agent.stage]
    else:
        return base_trauma * SHAME_RESISTANCE[agent.stage]

# ============================================================================
# TRAUMA SCHEDULER
# ============================================================================

class BurstTraumaScheduler:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.next_trauma_step = CALM_BASELINE_STEPS
        self.burst_queue = []
        self.trauma_count = 0

    def should_trigger(self, t):
        if self.burst_queue and t >= self.burst_queue[0]:
            self.burst_queue.pop(0)
            return True
        if t >= self.next_trauma_step and not self.burst_queue:
            self._schedule_next(t)
            return True
        return False

    def _schedule_next(self, t):
        self.trauma_count += 1
        if self.rng.random() < BURST_CHANCE:
            for i in range(1, self.rng.randint(2, 3)):
                self.burst_queue.append(t + i * BURST_SPACING)
        self.next_trauma_step = t + self.rng.randint(TRAUMA_MIN_INTERVAL, TRAUMA_MAX_INTERVAL)

    def get_trauma_amount(self):
        return self.rng.uniform(SHAME_MIN, SHAME_MAX)

    def select_target_index(self, num_agents):
        """Return index for trauma target."""
        return self.rng.randint(0, num_agents - 1)


def apply_contagion(target_agent, trauma_amount, agents):
    splash_events = []
    for mentee_id, _ in target_agent.mentees:
        mentee = next((a for a in agents if a.id == mentee_id), None)
        if mentee:
            splash_events.append({
                'mentor_id': target_agent.id,
                'mentee_id': mentee_id,
                'splash_amount': trauma_amount * CONTAGION_SPLASH
            })
    return splash_events

# ============================================================================
# MENTOR COUNCIL
# ============================================================================

class MentorCouncil:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.last_vote_step = -COUNCIL_VOTE_INTERVAL
        self.vote_history = []

    def should_vote(self, t):
        return t - self.last_vote_step >= COUNCIL_VOTE_INTERVAL

    def conduct_vote(self, agents, t):
        eligible = [a for a in agents if a.is_council_eligible(t)]
        if len(eligible) < COUNCIL_MIN_MENTORS:
            return None
        votes = {a.id: 0 for a in eligible}
        for voter in eligible:
            candidates = [a for a in eligible if a.id != voter.id]
            if not candidates:
                continue
            weights = [
                max(0.1, (c.sacrifice_credit / 100.0) +
                    (c.mentoring_score * 2.0) + (c.C * 3.0) +
                    c.mentees_became_mentors * 1.5)
                for c in candidates
            ]
            total = sum(weights)
            choice = self.rng.choices(candidates, weights=[w/total for w in weights], k=1)[0]
            votes[choice.id] += 1

        max_votes = max(votes.values())
        winners = [a for a in eligible if votes[a.id] == max_votes]
        winner = max(winners, key=lambda a: a.sacrifice_credit) if len(winners) > 1 else winners[0]
        self.last_vote_step = t
        self.vote_history.append({
            'step': t, 'eligible_count': len(eligible),
            'eligible_ids': [a.id for a in eligible],
            'votes': votes.copy(), 'winner_id': winner.id,
            'winner_votes': votes[winner.id]
        })
        for a in eligible:
            a.council_votes_received = votes[a.id]
        return winner

# ============================================================================
# MENTORING & PRAISE
# ============================================================================

def calculate_recovery_credit(shock_amount, recovery_time):
    if recovery_time <= 0:
        recovery_time = 1
    ratio = (shock_amount / SHAME_MAX) * (RECOVERY_TIME_NORMALIZE / recovery_time)
    ratio = max(0.25, min(4.0, ratio))
    return MENTEE_RECOVERY_BASE_CREDIT * ratio, ratio

def process_mentee_recovery(recovery_event, agents, t, praise_log, cultural_memory):
    """Returns cultural_delta"""
    sage_count = sum(1 for a in agents if hasattr(a, 'is_sage') and a.is_sage)
    cultural_delta = 0.0002 * sage_count

    if not recovery_event:
        return cultural_delta

    mentee = next((a for a in agents if a.id == recovery_event['agent_id']), None)
    if not mentee:
        return cultural_delta

    cultural_delta += CULTURE_GROWTH

    if not mentee.mentor_id:
        return cultural_delta

    mentor = next((a for a in agents if a.id == mentee.mentor_id), None)
    if not mentor:
        return cultural_delta

    credit, ratio = calculate_recovery_credit(
        recovery_event['shock_amount'], recovery_event['recovery_time'])

    mentor.receive_praise('mentee_recovery', credit, MENTEE_RECOVERY_BONUS_C, mentee.id, t)
    mentor.mentee_recoveries_witnessed += 1

    print(f"    * RECOVERY: Agent {mentee.id} recovered (mentor {mentor.id} +{credit:.2f} credit) [burn={mentee.get_active_burn_rate():.3f}]")

    praise_log.append({
        'step': t, 'type': 'mentee_recovery', 'mentor_id': mentor.id,
        'mentee_id': mentee.id, 'credit': credit, 'C_bump': MENTEE_RECOVERY_BONUS_C,
        'ratio': ratio, 'dimensional_recovery': recovery_event.get('dimensional_recovery', 0)
    })

    return cultural_delta

def process_mentee_promotion(promo_event, agents, t, praise_log):
    if not promo_event:
        return
    mentee = next((a for a in agents if a.id == promo_event['agent_id']), None)
    if not mentee or not mentee.mentor_id:
        return
    mentor = next((a for a in agents if a.id == mentee.mentor_id), None)
    if not mentor:
        return

    new_stage = promo_event['new_stage']
    credit = MENTEE_PROMOTION_BONUS
    c_bump = MENTEE_RECOVERY_BONUS_C

    if new_stage == "MENTOR":
        credit += MENTEE_BECOMES_MENTOR_BONUS; c_bump += 0.02
        mentor.mentees_became_mentors += 1; mentor.mentoring_score += 0.3
    elif new_stage == "STEWARD":
        credit += MENTEE_BECOMES_STEWARD_BONUS; c_bump += 0.03
        mentor.mentees_became_stewards += 1; mentor.mentoring_score += 0.5
    elif new_stage == "ELDER":
        credit += MENTEE_BECOMES_ELDER_BONUS; c_bump += 0.04
        mentor.mentees_became_elders += 1; mentor.mentoring_score += 1.0
    elif new_stage == "SAGE":
        credit += MENTEE_BECOMES_SAGE_BONUS; c_bump += 0.05
        mentor.mentees_became_sages += 1; mentor.mentoring_score += 1.5

    mentor.receive_praise(f'mentee_promotion_{new_stage}', credit, c_bump, mentee.id, t)
    mentor.mentee_promotions_witnessed += 1

    praise_log.append({
        'step': t, 'type': f'mentee_promotion_{new_stage}',
        'mentor_id': mentor.id, 'mentee_id': mentee.id,
        'credit': credit, 'C_bump': c_bump
    })

def assign_mentors(agents, t, log):
    assignments = []
    needs_mentor = [a for a in agents if a.needs_mentor()]
    available = sorted(
        [a for a in agents if a.can_mentor() and len(a.mentees) < 2],
        key=lambda a: (-a.stage_idx, len(a.mentees))
    )
    for junior in needs_mentor:
        for mentor in available:
            if not any(m[0] == junior.id for m in mentor.mentees):
                junior.mentor_id = mentor.id
                mentor.mentees.append((junior.id, t))
                mentor.mentee_steps_stable[junior.id] = 0

                credit = MENTOR_ASSIGNMENT_CREDIT
                if junior.generation <= mentor.generation:
                    credit += MENTOR_REACH_BACK_BONUS
                    mentor.reached_back_to.append(junior.id)
                mentor.add_sacrifice_credit(credit, t)

                event = {
                    'step': t, 'mentor_id': mentor.id, 'mentor_gen': mentor.generation,
                    'mentee_id': junior.id, 'mentee_gen': junior.generation,
                    'credit_granted': credit, 'reached_back': junior.generation <= mentor.generation
                }
                assignments.append(event)
                log.append(event)

                if len(mentor.mentees) >= 2:
                    available.remove(mentor)
                break
    return assignments

def update_mentoring_presence(agents, t):
    for agent in agents:
        if not agent.can_mentor():
            continue
        for mentee_id, _ in agent.mentees:
            mentee = next((a for a in agents if a.id == mentee_id), None)
            if not mentee:
                continue
            if any(t - r[0] < 500 for r in mentee.regressions):
                agent.mentee_steps_stable[mentee_id] = 0
                continue
            agent.add_sacrifice_credit(MENTOR_PRESENCE_RATE, t)
            agent.mentee_steps_stable[mentee_id] = agent.mentee_steps_stable.get(mentee_id, 0) + 1
            if agent.mentee_steps_stable[mentee_id] == MENTEE_STABILITY_THRESHOLD:
                agent.mentoring_score += 0.2

def process_energy_sacrifices(agents, t, sacrifice_log):
    events = []
    struggling = [a for a in agents
        if a.stage_idx <= STAGE_ORDER.index("APPRENTICE") and a.C < SACRIFICE_TRIGGER_C]
    capable = [a for a in agents if a.can_energy_sacrifice(t)]
    for junior in struggling:
        if not capable:
            break
        donor = next((a for a in capable if a.id == junior.mentor_id), None) or max(capable, key=lambda a: a.C)
        capable.remove(donor)
        if donor.attempt_sacrifice_with_choice(junior, t):
            events.append({
                'step': t, 'donor_id': donor.id, 'donor_stage': donor.stage,
                'recipient_id': junior.id, 'was_mentor': donor.id == junior.mentor_id
            })
            sacrifice_log.append(events[-1])
    return events

def calculate_culture_boost(culture_value, agent_C, agent_C_cap):
    headroom = agent_C_cap - agent_C
    headroom_ratio = headroom / agent_C_cap
    boost_multiplier = headroom_ratio ** 2
    return culture_value * CULTURE_BOOST * boost_multiplier

# ============================================================================
# SOCIETY STEP (v33: One World, Variable Burn Rate)
# ============================================================================

def society_step(agents, t, scarcity, social_shame_map, injected_shame_map,
                 cultural_memory, collective_memory,
                 arm_mode=None, trace_buffer=None, trace_dict=None,
                 mu_c_dict=None, step_rank_snapshot=None):
    """Returns (promotion_events, cultural_delta).

    v37.4 Stage 2: new keyword args plumb Hook Site 2 through to the per-agent
    loop inside this function. Legacy callers (no kwargs) see no behavior change.
    """
    dt = 0.01
    promotion_events = []
    cultural_delta = 0

    for agent in agents:
        # --- DIMENSIONAL DYNAMICS ---
        dim_bonus = agent.update_dimensional_state(dt, cultural_memory, collective_memory)

        # --- TCR TRUTH UPDATE ---
        crisis_detected = agent.C < 0.3
        tcr_bonus = agent.update_tcr_truth(crisis_detected)

        # --- TCR RECURSIVE DESCENT ---
        if agent.apply_recursive_descent_guarantee(t):
            cultural_delta += 0.05

        # --- STANDARD DYNAMICS ---
        u, u_m = get_reflection_controls(agent.mode)
        phi = agent.drift + 0.015 * jnp.sin(t * 0.01)
        U = reck_unitary(phi)
        proj = U @ agent.emb[:4]

        need = agent.E_R * (1.0 - agent.C)
        mentor_vec = agent.T_m * (1.0 + 2.0 * need) * jnp.array([-0.1, 0.1, -0.15, 0.2])
        new_emb = agent.emb.at[:4].set(proj + mentor_vec * 0.1)
        new_emb = apply_spine_pull(new_emb, agent.get_spine_pull())

        G_sigma = agent.get_G_sigma()
        noise = jax.random.normal(jax.random.PRNGKey(t * 1000 + agent.id + _AGENT_RNG_SALT), (16,)) * 0.01 * (1.0 - G_sigma * 0.5)
        agent.emb = new_emb + noise

        agent.C = min(float(compute_coherence(agent.emb)), agent.get_C_cap())

        # Apply lingering trauma penalty (decays each step)
        # Channel 4 wired 2026-07-01: trauma decay exponent modulated by observer
        # prediction. Incoherent observer → exponent 1.0 → base 0.993 decay
        # (v37.2 uncracked rate). Coherent observer + trauma predicted near →
        # exponent up to 1.3 → accelerated processing. One-sided: safety never
        # slows decay. Replaces the v37.2 flag-conditional CRACK_TRAUMA_PENALTY_DECAY
        # branch (constant retained for cosmetic banner at :1956).
        if agent.trauma_C_penalty > 0.001:
            agent.C = max(0.0, agent.C - agent.trauma_C_penalty)
            # 2026-10-04: read canonical_trauma_decay_exp (stored by
            # canonicalize_observer_channels at top of step).
            trauma_exponent = agent.canonical_trauma_decay_exp
            agent.trauma_C_penalty *= 0.993 ** trauma_exponent
            # Narrate significant lingering wounds (every 100 steps to avoid spam)
            if agent.trauma_C_penalty > 0.05 and t % 100 == 0:
                print(f"      ... Agent {agent.id} still wounded — C={agent.C:.3f} "
                      f"(penalty={agent.trauma_C_penalty:.3f} fading) [burn={agent.get_active_burn_rate():.3f}]")

        culture_boost = calculate_culture_boost(cultural_memory, agent.C, agent.get_C_cap())
        agent.C = min(agent.get_C_cap(), agent.C + culture_boost + dim_bonus + tcr_bonus)

        # --- ENERGY DYNAMICS ---
        eta_R, lambda_D, kappa, kappa_m = 0.04, 0.02, 0.6, 0.8
        dE_R = (eta_R * (agent.E_G + agent.E_M) - lambda_D * agent.E_R -
            u * kappa * agent.E_R - u_m * kappa_m * agent.E_R + scarcity * 0.05)
        dE_G = 0.03 * agent.E_M - eta_R * agent.E_R + u * 0.7 * kappa * agent.E_R
        dE_M = 0.02 * agent.E_G - eta_R * agent.E_R + u * 0.3 * kappa * agent.E_R

        agent.E_G = float(jnp.clip(agent.E_G + dt * dE_G, 0.01, 1.0))
        agent.E_M = float(jnp.clip(agent.E_M + dt * dE_M, 0.01, 1.0))
        agent.E_R = float(jnp.clip(agent.E_R + dt * dE_R, 0.0, 1.0))

        E_total = agent.E_G + agent.E_M + agent.E_R + 1e-8
        agent.E_G, agent.E_M, agent.E_R = agent.E_G / E_total, agent.E_M / E_total, agent.E_R / E_total

        # --- STRAIN & SHAME ---
        agent.S = float(jnp.clip(agent.S + dt * (0.02 * (1.0 - agent.C) - 0.03 * agent.C), 0.0, 1.0))

        injected_Sh = injected_shame_map.get(agent.id, 0.0)
        if injected_Sh > 0:
            effective_trauma = process_trauma_dimensionally(injected_Sh, agent, t)
            agent.Sh = effective_trauma
            agent.total_trauma_received += injected_Sh
            agent.trauma_events.append((t, injected_Sh))
            agent.E_R = float(jnp.clip(agent.E_R + effective_trauma * 0.5, 0.0, 1.0))
            agent.S = float(jnp.clip(agent.S + effective_trauma * 0.3, 0.0, 1.0))
            E_total = agent.E_G + agent.E_M + agent.E_R + 1e-8
            agent.E_G, agent.E_M, agent.E_R = agent.E_G / E_total, agent.E_M / E_total, agent.E_R / E_total

            # Three-channel trauma (same as v32)
            raw_trauma = injected_Sh
            c_before = agent.C

            # 1. DIRECT C HIT
            c_drop = raw_trauma * 0.5
            agent.C = max(0.0, agent.C - c_drop)

            # 2. LINGERING PENALTY
            agent.trauma_C_penalty = min(0.8, agent.trauma_C_penalty + raw_trauma * 0.4)

            # 3. EMBEDDING SCAR
            scar_direction = agent.emb - BASE_EMB_FLAT
            scar_direction = scar_direction / (jnp.linalg.norm(scar_direction) + 1e-8)
            trauma_noise = jax.random.normal(
                jax.random.PRNGKey(t * 7 + agent.id * 13 + _AGENT_RNG_SALT), (16,)) * raw_trauma * 0.2
            agent.emb = agent.emb + scar_direction * raw_trauma * 0.6 + trauma_noise

            print(f"    !! TRAUMA: Agent {agent.id} ({agent.stage}) hit — "
                  f"C: {c_before:.3f} -> {agent.C:.3f} (drop={c_before-agent.C:.3f}, "
                  f"penalty={agent.trauma_C_penalty:.3f}) [burn={agent.get_active_burn_rate():.3f}]")

        # === v33: MICRO-TRAUMA from high burn rate ===
        # Daily life is harder for high-burn-rate agents
        active_burn = agent.get_active_burn_rate()
        if random.random() < active_burn * MICRO_TRAUMA_SCALE:
            micro_shame = random.uniform(MICRO_TRAUMA_SHAME_MIN, MICRO_TRAUMA_SHAME_MAX)
            agent.C = max(0.0, agent.C - micro_shame * 0.1)
            agent.S = min(1.0, agent.S + micro_shame * 0.05)
            agent.micro_trauma_count += 1

        # === SAFETY FLOOR — applies to ALL agents (v33) ===
        old_catches = agent.safety_floor_catches
        agent.apply_safety_floor()
        if agent.safety_floor_catches > old_catches:
            print(f"    ~ FLOOR CATCH: Agent {agent.id} caught at C={SAFETY_FLOOR_C} "
                  f"(catch #{agent.safety_floor_catches}) [burn={agent.get_active_burn_rate():.3f}]")

        # === v37.3: OBSERVER FORMATION (sustained pressure exceeds threshold) ===
        if agent.update_observer_formation(t):
            cohort_tag = "CRACK-ENABLED" if agent.crack_enabled else "CONTROL"
            pressure = sum(agent.sustained_pressure_history)
            print(f"  *** OBSERVER FORMS: Agent {agent.id} ({agent.stage}, {cohort_tag}) | "
                  f"pressure_score={pressure:.2f} bias={agent.observer.prior_bias_distress:+.2f} "
                  f"gate={agent.observer.evidence_gate:.2f} "
                  f"[burn={agent.get_active_burn_rate():.3f}] ***")

        # === v37.3: STEP OBSERVER (prediction update + coherence gate) ===
        # Per-agent per-step — runs only when observer.exists. Updates
        # predictions across four channels, may promote to coherent, syncs
        # legacy aliases (self.cracked, metacognition_observations, pre_crack_D).
        agent.step_observer(t)

        # v37.4 Stage 2 integration -- HOOK SITE 2 (post-step_observer, fresh timing for D_caution).
        # Uses the rank snapshot built at Hook Site 1 to ensure within-step consistency.
        # Pre-reg: fifth addendum section 8, design doc section 4.
        if arm_mode is not None and step_rank_snapshot is not None:
            from stage_2_hooks import (
                capture_canonical_D_caution, apply_canonical_override_D_caution,
            )
            if agent.id in step_rank_snapshot:
                capture_canonical_D_caution(agent, t, trace_buffer, step_rank_snapshot)
                apply_canonical_override_D_caution(
                    agent, t, arm_mode, trace_dict, mu_c_dict, step_rank_snapshot)

        # --- OPTIMIZATION ---
        agent.Cf = max(0.0, -dE_R) * agent.C
        agent.O = float(jnp.clip(agent.O * 0.9995 + agent.Cf * dt, 0.0, 1.0))

        agent.min_C_experienced = min(agent.min_C_experienced, agent.C)
        agent.max_S_experienced = max(agent.max_S_experienced, agent.S)

        agent.V_opt = float(compute_bad_mass(agent.E_R, agent.C, agent.O))
        agent.mode = update_mode(agent.mode, agent.V_opt, agent.Sh)

        # --- MENTOR TUNING ---
        if agent.V_opt < 0.1 and agent.C > 0.8:
            agent.T_m = max(0.05, agent.T_m - 0.003)
        elif agent.mode == Mode.REFLECTIVE and agent.C < 0.5:
            agent.T_m = min(0.95, agent.T_m + 0.005)

        # === v33: UPDATE BURN RATE (adults+ only) ===
        agent.update_burn_rate(agents)

        # === SAFETY & CURIOSITY ===
        agent.C_recent.append(agent.C)
        if len(agent.C_recent) > SAFETY_WINDOW * 2:
            agent.C_recent = agent.C_recent[-SAFETY_WINDOW:]
        agent.compute_safety()
        was_curious = agent.is_curious
        agent.check_curiosity()
        if agent.is_curious and not was_curious:
            print(f"    ~ CURIOSITY AWAKENS: Agent {agent.id} (safety={agent.safety:.3f}, "
                  f"burn={agent.get_active_burn_rate():.3f}) begins exploring")
        if agent.is_curious:
            agent.explore(agents, t)

        # Record safety/curiosity/burn history (every 10 steps to save memory)
        if t % 10 == 0:
            agent.safety_history.append(agent.safety)
            agent.curiosity_history.append(1.0 if agent.is_curious else 0.0)
            agent.burn_rate_history.append(agent.get_active_burn_rate())

        # --- STAGE PROGRESSION ---
        agent.steps_in_stage += 1
        promoted, promo_event = agent.check_promotion(t)
        if promoted and promo_event:
            promotion_events.append(promo_event)
            cohort_tag = "CRACK" if agent.crack_enabled else "CTRL"
            cracked_tag = " *CRACKED*" if agent.cracked else ""
            print(f"  * PROMOTION: Agent {agent.id} ({cohort_tag}{cracked_tag}, Gen {agent.generation}) "
                  f"{promo_event['old_stage']} -> {promo_event['new_stage']} | "
                  f"C={agent.C:.3f} D={agent.D_eff:.3f} credit={agent.sacrifice_credit:.1f} "
                  f"[burn={agent.current_burn_rate:.3f}]")

    return promotion_events, cultural_delta


# ============================================================================
# MAIN SIMULATION — ONE WORLD (v33)
# ============================================================================
#
# v37.3.1 refactor (2026-07-18, Annie-026):
# The v37.3 __main__ body is wrapped as a callable `run_simulation(...)` so
# the Stage 1 calibration harness can invoke it twice per seed (hot-observer
# arm + no-observer arm) with paired-same-seed determinism. v37.3 stays
# frozen at Sal cosig (2026-07-14). Sim logic is unchanged; only additions:
# parameter plumbing, per-step channel snapshots (when log_channels=True),
# per-transition memoir events, matplotlib wrapped under render_plots flag,
# results dict return. stdout suppression is done by the harness at CALL
# SITE (spec §Recommended: call-site redirection) — this function stays
# clean of that concern. The `if __name__ == '__main__':` block at bottom
# preserves interactive behavior by calling with render_plots=True.

def run_simulation(seed=None, all_crack_enabled=None, n_steps=None,
                   log_channels=False, log_formation=False, render_plots=False,
                   birth_stagger_delays=None,
                   arm_mode=None, trace_buffer=None, trace_dict=None,
                   replay_coherence_timeline=None, mu_c_dict=None):
    # v37.4 Stage 2 integration (2026-10-08):
    #   arm_mode:     one of {'hot','no_obs','yoked','matched','reactive'}; None = legacy behavior
    #   trace_buffer: dict (hot capture); populated at Hook Sites with per-step records
    #   trace_dict:   dict (yoked injection); loaded from source hot run's trace pickle
    #   mu_c_dict:    dict (matched offset); from Stage 1 v2 calibration JSON
    """Run one full v37.3 simulation.

    seed: None → int(time.time()); else deterministic.
    all_crack_enabled: None (default paired), True (all crack — hot arm),
                       False (none crack — no-observer arm).
    n_steps: None → module TOTAL_STEPS; else override.
    log_channels: if True, snapshot per-agent per-step observer channel
                  values into results['channel_snapshots'].
    log_formation: if True, log one event per observer formation into
                   results['formation_events'] with distress_fraction,
                   pressure_history length, evidence_gate, all four
                   prior_level_* values, and actuals at formation.
                   Added 2026-07-25 for diagnostic D6 (formation distress
                   audit). Additive — no simulation behavior change.
    render_plots: if True, run the matplotlib summary at the end. False for
                  headless calibration.
    birth_stagger_delays: None (default) or list of length INITIAL_AGENTS. If
                  provided, pair i enters the agents list at step delays[i]
                  instead of at t=0. RNG state and burn_rate draws still occur
                  at t=0 during the pre-loop, so identical seeds produce the
                  same initial pair state regardless of delay. Additive — no
                  behavior change when None. Added 2026-09-20 for diagnostic
                  D2b (positional-confound follow-up under Sal ratification).
    Returns dict of results — see end of function.
    """
    channel_snapshots = []
    memoir_events = []
    formation_events = []
    _n_steps = n_steps if n_steps is not None else TOTAL_STEPS

    # Seventh addendum (2026-10-08): reset LEAK activation counter per run so
    # Gate 1 Exercise 1 counts activations from a clean baseline. Harmless when
    # LEAK_TEST_MODE is False (counter stays zero).
    global _LEAK_ACTIVATION_COUNT
    _LEAK_ACTIVATION_COUNT = 0

    # Ninth addendum / 5.5 cycle 6 (2026-10-09): hook-integrity check replaces
    # the symptom-level MODE_HOT invariant that fired on legitimate no-observer
    # seeds (e.g. seed 25 — 0 formation events across 3000 steps). This
    # cause-level check catches the actual config bug the original invariant
    # was meant to catch: arm_mode='hot' passed with all_crack_enabled != True
    # (observer pathway not actually enabled). Fires here BEFORE any simulation
    # work, not after 3000 steps of wasted compute.
    if arm_mode == 'hot':
        assert all_crack_enabled is True, (
            f"MODE_HOT requires all_crack_enabled=True. "
            f"Got arm_mode='hot' with all_crack_enabled={all_crack_enabled!r}. "
            f"The observer pathway cannot be exercised without crack enabled."
        )
    if arm_mode == 'reactive':
        assert replay_coherence_timeline is not None, (
            "arm_mode='reactive' requires replay_coherence_timeline. "
            "Load hot arm's channel_snapshots and build the timeline dict first."
        )

    print("=" * 80)
    print("=== SOCIETY WOMB v37.2 — THE CRACK ===")
    print("=== Does the crack produce better agents, or just different ones? ===")
    print("=" * 80)
    print()
    print("Paired cohorts. Same trauma. Same world.")
    print("One population can crack under sustained pressure (metacognition gate).")
    print("The other heals shut. Same collapse, no observer.")
    print()
    print(f"Crack conditions: C/C_cap > {CRACK_C_RATIO_THRESHOLD}, M < {CRACK_M_THRESHOLD}, D < {CRACK_D_THRESHOLD}, sustained {CRACK_SUSTAIN_STEPS} steps")
    print(f"Cracked agents get: faster burn decay ({CRACK_BURN_DECAY}), strategic sacrifice,")
    print(f"  faster trauma recovery (penalty decay {CRACK_TRAUMA_PENALTY_DECAY}), self-observation")
    print(f"Crack cost: C -= {CRACK_STABILITY_COST_C}, S += {CRACK_STABILITY_COST_S}")
    print()
    print(f"Burn rate: Beta({BURN_RATE_ALPHA},{BURN_RATE_BETA_PARAM}) * {BURN_RATE_MAX}")
    print(f"Safety floor: C={SAFETY_FLOOR_C} | Trauma seed (derived): {seed ^ 0xBEEF} | "
          f"Council seed (derived): {seed ^ 0xC0FFEE} | Agent-RNG salt (derived): {seed ^ 0xA6E1} | "
          f"Run seed: {seed}")
    print(f"dD/dt = -alpha(D-2) - gamma*n + beta*M + lambda*f(C)")
    print(f"Arm: {'paired' if all_crack_enabled is None else ('hot' if all_crack_enabled else 'no_obs')}  "
          f"|  n_steps={_n_steps}  |  log_channels={log_channels}")
    print()

    if seed is None:
        seed = int(time.time())
    print(f"Random seed: {seed}")
    np.random.seed(seed)
    random.seed(seed)
    master_key = jax.random.PRNGKey(seed)

    # Agent-RNG salt for the five per-agent RNG call sites (see module-level
    # _AGENT_RNG_SALT comment). Derived from run seed with a distinct XOR
    # offset from the trauma (0xBEEF) and council (0xC0FFEE) fixes so all
    # three streams are independent of each other.
    global _AGENT_RNG_SALT
    _AGENT_RNG_SALT = seed ^ 0xA6E1

    # State
    agents = []
    next_agent_id = 0
    next_pair_id = 0
    current_generation = 0
    cultural_memory = 0.0
    collective_memory = 0.0
    available_memoirs = []
    memoir_id_counter = 0
    current_pool_cap = SHARED_POOL_FIXED

    # Logs
    birth_log = []
    trauma_log = []
    sacrifice_log = []
    mentor_log = []
    contagion_log = []
    elder_fall_log = []
    praise_log = []
    council_log = []
    dimensional_log = []
    culture_history = []
    crack_log = []  # v35

    recovery_tracker = RecoveryTracker()
    # Seed decoupling fix (2026-09-17, Nymph/Harley): COUNCIL_VOTE_SEED and
    # TRAUMA_SEED were module-level constants (42 and 777), making every run_simulation
    # call experience identical council votes and trauma schedules regardless of the
    # `seed` parameter. Paired arms (hot + no_observer at same seed) share the same
    # schedule by design — but across 20 different seeds, r ≈ 0.9999 because the
    # trauma dynamics are identical. That leaves ~0.3 independent observations per
    # seed, not 20. Fix: derive both scheduler seeds from the run seed so different
    # seeds get different worlds; paired arms at the same seed still share a world.
    # Note: this change invalidates any prior code SHA — compute a fresh hash at
    # Stage 1 launch. The xor offsets (0xC0FFEE, 0xBEEF) prevent mentor_council
    # and trauma_scheduler colliding on the same internal state.
    mentor_council = MentorCouncil(seed ^ 0xC0FFEE)
    trauma_scheduler = BurstTraumaScheduler(seed ^ 0xBEEF)

    jax_key = master_key

    # v35: Create initial agents as PAIRS (same burn_rate, one crack_enabled, one not)
    # v37.3.1: crack_enabled respects all_crack_enabled arm parameter — None keeps
    # default paired behavior, True/False forces all-agents-same.
    # 2026-09-20 (Nymph/Harley): birth_stagger_delays optional — see docstring.
    _ce_a = True if all_crack_enabled is None else all_crack_enabled
    _ce_b = False if all_crack_enabled is None else all_crack_enabled
    _delays = birth_stagger_delays if birth_stagger_delays is not None else [0] * INITIAL_AGENTS
    if len(_delays) != INITIAL_AGENTS:
        raise ValueError(
            f"birth_stagger_delays must have length {INITIAL_AGENTS}, got {len(_delays)}")
    pending_births = []  # list of (delay_step, agent_a, agent_b, tag_a, tag_b, burn, pair_id)

    for i in range(INITIAL_AGENTS):
        jax_key, subkey1, subkey2 = jax.random.split(jax_key, 3)
        # Draw ONE burn rate for the pair — happens at t=0 regardless of delay,
        # so RNG stream is seed-consistent across delay configurations.
        shared_burn_rate = float(np.random.beta(BURN_RATE_ALPHA, BURN_RATE_BETA_PARAM) * BURN_RATE_MAX)
        pair_id = next_pair_id
        _bs = _delays[i]

        # Agent A: crack enabled (or per arm). birth_step reflects actual entry step.
        agent_a = Agent(next_agent_id, subkey1, _bs, 0,
                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_a, pair_id=pair_id,
                        reactive_mode=(arm_mode == 'reactive'),
                        replay_coherence_timeline=replay_coherence_timeline)
        next_agent_id += 1

        # Agent B: crack disabled control (or per arm)
        agent_b = Agent(next_agent_id, subkey2, _bs, 0,
                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_b, pair_id=pair_id,
                        reactive_mode=(arm_mode == 'reactive'),
                        replay_coherence_timeline=replay_coherence_timeline)
        next_agent_id += 1
        next_pair_id += 1

        _tag_a = "CRACK" if _ce_a else "CONTROL"
        _tag_b = "CRACK" if _ce_b else "CONTROL"
        if _bs == 0:
            agents.append(agent_a)
            agents.append(agent_b)
            print(f"  Pair {pair_id}: Agents {agent_a.id} ({_tag_a}) & {agent_b.id} ({_tag_b}) | "
                  f"burn_rate={shared_burn_rate:.4f}")
        else:
            pending_births.append((_bs, agent_a, agent_b, _tag_a, _tag_b, shared_burn_rate, pair_id))
            print(f"  Pair {pair_id}: Agents {agent_a.id} ({_tag_a}) & {agent_b.id} ({_tag_b}) | "
                  f"burn_rate={shared_burn_rate:.4f} | DELAYED until t={_bs}")

    print(f"\n  {len(agents)} agents in {next_pair_id} pairs "
          f"({len(pending_births)} pending staggered births)")
    print(f"\nRunning {_n_steps} steps — THE CRACK...\n")

    for t in range(_n_steps):
        # 2026-09-20: staggered-birth diagnostic — insert pending pairs at their delay step
        if pending_births:
            for entry in list(pending_births):
                if entry[0] == t:
                    _bs, _a, _b, _ta, _tb, _br, _pid = entry
                    agents.append(_a)
                    agents.append(_b)
                    pending_births.remove(entry)
                    print(f"  [t={t}] Staggered birth — Pair {_pid}: "
                          f"Agents {_a.id} ({_ta}) & {_b.id} ({_tb}) | burn_rate={_br:.4f}")

        # 2026-10-04 (Nymph/Harley fix): canonicalize observer-channel values
        # once per agent per step. Both sim use-sites (get_burn_decay,
        # sacrifice-refusal gate, trauma processing) and channel_snapshots
        # logger read from stored attributes. Single gate in one place.
        for _a in agents:
            _a.canonicalize_observer_channels()

        # v37.4 Stage 2 integration -- HOOK SITE 1 (top-of-step timing).
        # Operates on canonical_burn_decay_mult/trauma_decay_exp/refusal_chance.
        # Pre-reg: fifth addendum section 8, design doc section 4.
        if arm_mode is not None:
            from stage_2_hooks import (
                build_step_rank_snapshot,
                capture_canonical, apply_canonical_override, assert_observer_off,
            )
            step_rank_snapshot = build_step_rank_snapshot(agents)
            capture_canonical(agents, t, trace_buffer, step_rank_snapshot)
            apply_canonical_override(agents, t, arm_mode, trace_dict, mu_c_dict, step_rank_snapshot)
            assert_observer_off(agents, arm_mode, t)
        else:
            step_rank_snapshot = None

        num_agents = len(agents)
        global_pool = sum(a.E_G + a.E_M + a.E_R for a in agents)
        scarcity = max(0.0, (global_pool - current_pool_cap) / current_pool_cap)

        social_shame_map = {
            a.id: sum(o.Sh for o in agents if o.id != a.id) / max(1, num_agents - 1)
            for a in agents
        }

        # Recovery tracking
        for agent in agents:
            recovery_event = recovery_tracker.update(agent.id, t, agent.C, agent.D_eff)
            if recovery_event:
                cd = process_mentee_recovery(recovery_event, agents, t,
                                             praise_log, cultural_memory)
                cultural_memory += cd

        # Trauma — v35: target PAIRS so both cohorts see same trauma
        injected_shame_map = {}
        trauma_triggered = trauma_scheduler.should_trigger(t)
        if trauma_triggered and num_agents > 0:
            trauma_amount = trauma_scheduler.get_trauma_amount()

            # v35: target a pair, not an individual
            active_pair_ids = sorted(set(a.pair_id for a in agents if a.stage != "ANCESTOR"))
            if active_pair_ids:
                pair_idx = trauma_scheduler.select_target_index(len(active_pair_ids))
                target_pair_id = active_pair_ids[pair_idx % len(active_pair_ids)]
                pair_agents = [a for a in agents if a.pair_id == target_pair_id and a.stage != "ANCESTOR"]

                burst_tag = " [BURST]" if len(trauma_log) > 1 and t - trauma_log[-2]['step'] < BURST_SPACING * 2 else ""

                # v35 fix: halve trauma_amount to compensate for pair-targeting
                # Both pair members get identical trauma (control preserved),
                # but per-agent damage rate matches v33 single-target cadence.
                paired_trauma = trauma_amount * 0.5

                for target in pair_agents:
                    resistance = SHAME_RESISTANCE[target.stage]
                    injected_shame_map[target.id] = paired_trauma * resistance
                    recovery_tracker.start_tracking(target.id, t, target.C, target.D_eff, paired_trauma)

                    cohort_tag = "CRACK" if target.crack_enabled else "CTRL"
                    cracked_tag = " *CRACKED*" if target.cracked else ""
                    trauma_log.append({'step': t, 'target_id': target.id,
                                        'amount': trauma_amount, 'pre_D': target.D_eff,
                                        'crack_enabled': target.crack_enabled,
                                        'cracked': target.cracked})
                    print(f"  ! Step {t}: Agent {target.id} ({target.stage}, {cohort_tag}{cracked_tag}) "
                          f"hit with {trauma_amount:.3f} shame{burst_tag} | C={target.C:.3f} D={target.D_eff:.3f} "
                          f"[burn={target.get_active_burn_rate():.3f}]")

                    for splash in apply_contagion(target, trauma_amount, agents):
                        injected_shame_map[splash['mentee_id']] = injected_shame_map.get(
                            splash['mentee_id'], 0) + splash['splash_amount']
                        contagion_log.append(splash)
                        print(f"    -> Contagion: Agent {splash['mentee_id']} takes {splash['splash_amount']:.3f} splash")

                # Pool degrades once per event, not per agent hit
                current_pool_cap = max(POOL_MINIMUM, current_pool_cap - POOL_DEGRADATION_PER_TRAUMA)

        # Council vote
        if mentor_council.should_vote(t):
            winner = mentor_council.conduct_vote(agents, t)
            if winner:
                promo_event = winner.promote_by_council(t)
                council_log.append(mentor_council.vote_history[-1])
                vote_data = mentor_council.vote_history[-1]
                print(f"  === COUNCIL VOTE at step {t} ===")
                print(f"    Eligible: {vote_data['eligible_ids']} | Votes: {vote_data['votes']}")
                print(f"    *** Agent {winner.id} PROMOTED TO STEWARD BY COUNCIL ({vote_data['winner_votes']} votes) ***")
                process_mentee_promotion(promo_event, agents, t, praise_log)

        # Elder council promotion
        eligible_elders = [a for a in agents if a.can_elder_promote()]
        if len(eligible_elders) >= ELDER_COUNCIL_MIN_STEWARDS:
            for steward in eligible_elders:
                promo_event = steward.promote_to_elder(t)
                e_cohort = "CRACK" if steward.crack_enabled else "CTRL"
                e_cracked = " *CRACKED*" if steward.cracked else ""
                print(f"  ** ELDER AWAKENING: Agent {steward.id} ({e_cohort}{e_cracked}, Gen {steward.generation}) "
                      f"rises to ELDER | credit={steward.sacrifice_credit:.1f} D={steward.D_eff:.3f} "
                      f"[burn={steward.current_burn_rate:.3f}] **")
                process_mentee_promotion(promo_event, agents, t, praise_log)

        # Sage promotion
        for elder in [a for a in agents if a.stage == "ELDER"]:
            if elder.can_sage_promote():
                promo_event = elder.promote_to_sage(t)
                s_cohort = "CRACK" if elder.crack_enabled else "CTRL"
                s_cracked = " *CRACKED*" if elder.cracked else ""
                print(f"  **** SAGE AWAKENING: Agent {elder.id} ({s_cohort}{s_cracked}, Gen {elder.generation}) "
                      f"AWAKENS AS SAGE | D={elder.D_eff:.3f} mentoring={elder.mentoring_score:.2f} "
                      f"[burn={elder.current_burn_rate:.3f}] ****")
                process_mentee_promotion(promo_event, agents, t, praise_log)

        # Sage branching (Theocrat OR Ancestor)
        for sage in [a for a in agents if a.stage == "SAGE"]:
            if sage.can_transition_to_ancestor():
                ancestor_pull = min(0.6, sage.potential_memoir_quality / 1000.0)
                if random.random() < ancestor_pull:
                    new_id, memoir_id_counter, cd, cld, memoir = sage.transition_to_ancestor(
                        t, agents, available_memoirs, memoir_id_counter,
                        cultural_memory, collective_memory)
                    cultural_memory += cd
                    collective_memory += cld
                    # v37.3.1: log memoir event for Channel 5 delta computation
                    memoir_events.append({
                        'step': t,
                        'sage_id': sage.id,
                        'sage_crack_enabled': sage.crack_enabled,
                        'memoir_id': memoir['id'],
                        'quality': memoir['quality'],
                        'observer_bonus': observer_quality_bonus(sage.observer),
                    })
                    print(f"  *** ANCESTOR TRANSITION: Sage {sage.id} (Gen {sage.generation}) creates MEMOIR #{memoir['id']} "
                          f"(quality={memoir['quality']:.2f}, birth_burn={memoir['birth_burn_rate']:.3f}, "
                          f"final_burn={memoir['final_burn_rate']:.3f}, journey={memoir['burn_journey']:.3f}) ***")
                    new_agent = next(a for a in agents if a.id == new_id)
                    # v35: assign pair_id and crack_enabled to the infant from transition
                    # The ancestor's crack_enabled determines: new infant gets SAME crack_enabled
                    # Then we create a paired twin with opposite crack_enabled.
                    # v37.3.1: under all_crack_enabled, both new_agent and twin forced same.
                    pair_id = next_pair_id
                    new_agent.crack_enabled = (sage.crack_enabled
                                                if all_crack_enabled is None
                                                else all_crack_enabled)
                    new_agent.pair_id = pair_id

                    # Create paired twin
                    _twin_ce = ((not sage.crack_enabled)
                                if all_crack_enabled is None
                                else all_crack_enabled)
                    jax_key, twin_key = jax.random.split(jax_key)
                    twin = Agent(next_agent_id, twin_key, t, sage.generation + 1,
                                 birth_burn_rate=new_agent.birth_burn_rate,
                                 crack_enabled=_twin_ce,
                                 pair_id=pair_id,
                                 reactive_mode=(arm_mode == 'reactive'),
                                 replay_coherence_timeline=replay_coherence_timeline)
                    agents.append(twin)
                    next_agent_id += 1
                    next_pair_id += 1

                    cohort_a = "CRACK" if new_agent.crack_enabled else "CTRL"
                    cohort_b = "CRACK" if twin.crack_enabled else "CTRL"
                    cracked_tag = " *CRACKED*" if sage.cracked else ""
                    print(f"  *** ANCESTOR TRANSITION: Sage {sage.id} ({cohort_a}{cracked_tag}) creates MEMOIR #{memoir['id']} "
                          f"(quality={memoir['quality']:.2f}) ***")
                    print(f"    -> Paired infants: Agent {new_id} ({cohort_a}) & {twin.id} ({cohort_b}) | "
                          f"Gen {sage.generation + 1} | burn={new_agent.birth_burn_rate:.3f}")
                    # v33.1: print D trajectory from memoir
                    m = next((m for m in available_memoirs if m['id'] == memoir_id_counter - 1), None)
                    if m:
                        print(f"    -> Memoir: peak_D={m.get('peak_D',0):.1f}, "
                              f"D@worst_C={m.get('D_at_worst_C',0):.1f}, "
                              f"worst_C={m.get('worst_C',1):.3f}, "
                              f"collapses={m.get('D_collapse_count',0)}, "
                              f"cracked={m.get('cracked', False)}")
            elif sage.can_theocrat_promote(available_memoirs):
                promo_event, cd, cld = sage.promote_to_theocrat(
                    t, available_memoirs, cultural_memory, collective_memory)
                if promo_event:
                    cultural_memory += cd
                    collective_memory += cld
                    print(f"  ** THEOCRAT: Sage {sage.id} claims MEMOIR #{promo_event['memoir_id']} **")
                    process_mentee_promotion(promo_event, agents, t, praise_log)

        # Remove ancestors
        ancestors_list = [a for a in agents if a.stage == "ANCESTOR"]
        for ancestor in ancestors_list:
            print(f"    -> Agent {ancestor.id} (ANCESTOR) dissolves into cultural memory")
            agents.remove(ancestor)

        # Theocrat actions
        for theocrat in [a for a in agents if a.stage == "THEOCRAT"]:
            cd, cld = theocrat.theocrat_act(agents, t, available_memoirs,
                                             cultural_memory, collective_memory)
            if cd > 0.05:
                print(f"  *** SERMON: Theocrat {theocrat.id} delivers teaching from MEMOIR #{theocrat.claimed_memoir_id} — culture +{cd:.2f} ***")
            elif cd > 0:
                if t % 500 < 1:
                    print(f"    [READING] Theocrat {theocrat.id} reads MEMOIR #{theocrat.claimed_memoir_id}")
            cultural_memory += cd
            collective_memory += cld

        # Mentor assignment
        if t % 20 == 0:
            for e in assign_mentors(agents, t, mentor_log):
                tag = " [REACHED BACK]" if e['reached_back'] else ""
                print(f"    -> Agent {e['mentor_id']} (Gen {e['mentor_gen']}) mentoring Agent {e['mentee_id']} (Gen {e['mentee_gen']}){tag}")

        # Mentoring presence
        update_mentoring_presence(agents, t)

        # Energy sacrifices
        for e in process_energy_sacrifices(agents, t, sacrifice_log):
            print(f"    <3 SACRIFICE: Agent {e['donor_id']} ({e['donor_stage']}) -> Agent {e['recipient_id']}"
                  f"{' (mentor)' if e['was_mentor'] else ''}")

        # Birth — v35: births create PAIRS
        # v37.3.1: crack_enabled respects all_crack_enabled arm parameter.
        if (all(a.stage_idx >= STAGE_ORDER.index("ADULT") for a in agents) and
            not any(a.stage == "INFANT" for a in agents) and
            len(agents) < MAX_AGENTS - 1):  # room for a pair
            current_generation += 1
            jax_key, subkey1, subkey2 = jax.random.split(jax_key, 3)
            shared_burn_rate = float(np.random.beta(BURN_RATE_ALPHA, BURN_RATE_BETA_PARAM) * BURN_RATE_MAX)
            pair_id = next_pair_id

            _bce_a = True if all_crack_enabled is None else all_crack_enabled
            _bce_b = False if all_crack_enabled is None else all_crack_enabled

            agent_a = Agent(next_agent_id, subkey1, t, current_generation,
                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_a, pair_id=pair_id,
                            reactive_mode=(arm_mode == 'reactive'),
                            replay_coherence_timeline=replay_coherence_timeline)
            agents.append(agent_a)
            birth_log.append((t, next_agent_id, current_generation, 'CRACK' if _bce_a else 'CONTROL'))
            next_agent_id += 1

            agent_b = Agent(next_agent_id, subkey2, t, current_generation,
                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_b, pair_id=pair_id,
                            reactive_mode=(arm_mode == 'reactive'),
                            replay_coherence_timeline=replay_coherence_timeline)
            agents.append(agent_b)
            birth_log.append((t, next_agent_id, current_generation, 'CRACK' if _bce_b else 'CONTROL'))
            next_agent_id += 1
            next_pair_id += 1

            _btag_a = "CRACK" if _bce_a else "CTRL"
            _btag_b = "CRACK" if _bce_b else "CTRL"
            print(f"  *** PAIRED BIRTH: Agents {agent_a.id} ({_btag_a}) & {agent_b.id} ({_btag_b}) | "
                  f"Gen {current_generation} | Pop: {len(agents)} | burn={shared_burn_rate:.3f} ***")

        # Culture decay
        cultural_memory *= CULTURE_DECAY

        # Society step (dynamics + safety/curiosity + burn rate)
        # v37.4 Stage 2: pass arm hooks through so Hook Site 2 fires at the right place.
        promo_events, cd = society_step(agents, t, scarcity, social_shame_map,
                                        injected_shame_map, cultural_memory,
                                        collective_memory,
                                        arm_mode=arm_mode,
                                        trace_buffer=trace_buffer,
                                        trace_dict=trace_dict,
                                        mu_c_dict=mu_c_dict,
                                        step_rank_snapshot=step_rank_snapshot)
        cultural_memory += cd
        for pe in promo_events:
            process_mentee_promotion(pe, agents, t, praise_log)

        # D6 (2026-07-25): formation-event telemetry. Scan agents for
        # observers that formed on this exact step. Additive; sim behavior
        # unchanged. No-op when log_formation=False.
        if log_formation:
            for a in agents:
                if a.observer.exists and a.observer.formation_step == t:
                    formation_events.append({
                        'step': t,
                        'agent_id': a.id,
                        'pair_id': a.pair_id,
                        'crack_enabled': a.crack_enabled,
                        'stage': a.stage,
                        'distress_fraction': compute_distress_fraction(
                            a.sustained_pressure_history),
                        'pressure_history_len': len(a.sustained_pressure_history),
                        'pressure_history_maxlen': a.sustained_pressure_history.maxlen,
                        'pressure_score': sum(a.sustained_pressure_history),
                        'evidence_gate': a.observer.evidence_gate,
                        'prior_bias_distress': a.observer.prior_bias_distress,
                        'prior_level_C': a.observer.prior_level_C,
                        'prior_level_burn_rate': a.observer.prior_level_burn_rate,
                        'prior_level_trauma_arrival': a.observer.prior_level_trauma_arrival,
                        'prior_level_recovery_time': a.observer.prior_level_recovery_time,
                        'actual_C_at_formation': float(a.C),
                        'actual_burn_rate_at_formation': float(a.current_burn_rate),
                        'actual_trauma_arrival_at_formation':
                            a._estimate_steps_to_next_trauma(),
                        'actual_recovery_time_at_formation':
                            a._estimate_recent_recovery_time(),
                    })

        # v37.3.1: per-agent per-step channel snapshot for Stage 1 calibration.
        # Only when log_channels=True (expensive; ~ N_agents scalars per step).
        # Ch 1 burn_decay: raw formula. Identity (1.0) when observer not coherent.
        # Ch 2 refusal_prob: canonical counterfactual at sacrifice_cost=0.1,
        #                    floor=SAFETY_FLOOR_C. Baseline SACRIFICE_REFUSAL_CHANCE
        #                    when observer not formed.
        # Ch 3 D_caution: observer_D_caution if coherent, else D_MAX (identity).
        # Ch 4 trauma_decay_exponent: raw formula, 1.0 identity when not coherent.
        if log_channels:
            # D_MAX defined at module scope (line 239); accessible via closure.
            # 2026-07-19: three fields added per Sal verdict-C letter for
            # variance-diagnostic. Additive only — sim behavior unchanged.
            # 2026-07-25: D3 telemetry (channel decomposition, F7.3/F10) —
            # per-channel squared-normalized-error and actual burn_rate. Same
            # rule: additive, sim behavior unchanged.
            for a in agents:
                _ssf = (t - a.observer.formation_step) if a.observer.exists else 0
                _per_ch = (compute_per_channel_variance_for_diagnostic(a.observer)
                           if a.observer.exists else {'C': 0.0, 'burn_rate': 0.0})
                channel_snapshots.append({
                    'step': t,
                    'agent_id': a.id,
                    'pair_id': a.pair_id,
                    'crack_enabled': a.crack_enabled,
                    'stage': a.stage,
                    'observer_exists': a.observer.exists,
                    'observer_coherent': is_coherent(a.observer),
                    'prediction_variance': get_prediction_variance_for_diagnostic(a.observer),
                    'pe_C_sq_normalized': _per_ch.get('C', 0.0),
                    'pe_burn_sq_normalized': _per_ch.get('burn_rate', 0.0),
                    'actual_burn_rate': a.get_active_burn_rate(),
                    'coherent_steps': a.observer.coherent_steps,
                    'steps_since_formation': _ssf,
                    # 2026-10-04: read from canonical attributes (stored by
                    # canonicalize_observer_channels). Prevents sim-vs-logger drift.
                    'burn_decay_multiplier': a.canonical_burn_decay_mult,
                    'trauma_decay_exponent': a.canonical_trauma_decay_exp,
                    'D_caution': (a.canonical_D_caution
                                  if a.canonical_D_caution is not None else D_MAX),
                    'coherent_steps_this_record': getattr(a.observer, 'coherent_steps', 0),
                    'refusal_prob_canonical': a.canonical_refusal_chance,
                    'refusal_prob_ref_cost_0_1': a.refusal_prob_ref_cost_0_1,
                    'D_eff': float(a.D_eff),  # v37.4 for dampening-firing-rate diagnostic
                    'taught_D_caution': a.taught_D_caution,  # v37.4 for effective_D_caution reconstruction
                })

        # Logging
        if t % 1000 == 0:
            culture_history.append((t, cultural_memory))
            dimensional_log.append((t, compute_dimensional_health(agents)))

        # Progress report every 5000 steps
        if t % 5000 == 0:
            avg_C = np.mean([a.C for a in agents]) if agents else 0
            avg_D = compute_dimensional_health(agents)
            stage_counts = defaultdict(int)
            for a in agents:
                stage_counts[a.stage] += 1
            stages = " ".join(f"{s[:3]}:{c}" for s, c in sorted(stage_counts.items()) if c > 0)
            curious = sum(1 for a in agents if a.is_curious)
            floor_catches = sum(a.safety_floor_catches for a in agents)
            avg_burn = np.mean([a.get_active_burn_rate() for a in agents]) if agents else 0
            avg_birth_burn = np.mean([a.birth_burn_rate for a in agents]) if agents else 0
            # v35: crack stats
            crack_enabled_agents = [a for a in agents if a.crack_enabled]
            control_agents = [a for a in agents if not a.crack_enabled]
            cracked_count = sum(1 for a in agents if a.cracked)
            crack_avg_C = np.mean([a.C for a in crack_enabled_agents]) if crack_enabled_agents else 0
            ctrl_avg_C = np.mean([a.C for a in control_agents]) if control_agents else 0
            print(f"\nStep {t:>6d} | Pop={len(agents)} C={avg_C:.3f} D={avg_D:.3f} "
                  f"Culture={cultural_memory:.2f} Curious={curious} FloorCatches={floor_catches}")
            print(f"           | Cracked={cracked_count} | CRACK_C={crack_avg_C:.3f} CTRL_C={ctrl_avg_C:.3f} | {stages}")
            print()

    # v37.4 Stage 2 integration -- MODE_HOT inverse assertion + coherence_declaration.
    # Pre-reg: fifth addendum section 7, design doc section 4.
    # Ninth addendum / 5.5 cycle 6 (2026-10-09): softened from AssertionError to
    # warn + flag. Seed 25 proved the original invariant too strict -- a legitimate
    # no-observer trajectory (no formation events, no observer_exists:True across
    # 14,500 snapshots on seed 25 diagnosis) is a valid Phase 1 outcome, not a bug.
    # Config-level bug catching moved to hook-integrity assertion at top of
    # run_simulation (arm_mode='hot' requires all_crack_enabled=True). This
    # outcome-level check now sets a flag so Phase 5 ratification treats these
    # seeds appropriately (STRICT bucket: zero coherent agent-steps -> hot MUST
    # equal no_obs within TOLERANCE_FP for canonical surface completeness).
    _hot_observer_never_formed = False
    if arm_mode == 'hot':
        # v37.4 Stage 2: check channel_snapshots observer_exists (populated whenever
        # log_channels=True) rather than formation_events (requires log_formation=True).
        _ever_formed = any(s.get('observer_exists', False) for s in channel_snapshots) if channel_snapshots else bool(formation_events)
        _hot_observer_never_formed = not _ever_formed
        if _hot_observer_never_formed:
            print(f"[warn] MODE_HOT seed {seed}: no observer ever formed. "
                  f"Counting as non-coherent-declared. Equivalent to no_obs trajectory.",
                  flush=True)
    # Coherence declaration (fifth addendum section 7): any agent coherent_steps >= 50.
    MIN_COHERENT_STEPS_FOR_DECLARATION = 50
    _coherence_declaration = any(
        s.get('coherent_steps_this_record', 0) >= MIN_COHERENT_STEPS_FOR_DECLARATION
        for s in channel_snapshots
    ) if channel_snapshots else False

    # v37.3.1: build results dict (used by both early-return and end-of-function paths).
    _results = {
        'seed': seed,
        'arm': ('paired' if all_crack_enabled is None
                else ('hot' if all_crack_enabled else 'no_obs')),
        'arm_mode': arm_mode,
        'coherence_declaration': _coherence_declaration,
        'trace_buffer': trace_buffer,
        'n_steps': _n_steps,
        'final_agents': agents,
        'available_memoirs': available_memoirs,
        'birth_log': birth_log,
        'trauma_log': trauma_log,
        'sacrifice_log': sacrifice_log,
        'praise_log': praise_log,
        'contagion_log': contagion_log,
        'elder_fall_log': elder_fall_log,
        'council_log': council_log,
        'dimensional_log': dimensional_log,
        'culture_history': culture_history,
        'crack_log': crack_log,
        'cultural_memory': cultural_memory,
        'collective_memory': collective_memory,
        'channel_snapshots': channel_snapshots,
        'memoir_events': memoir_events,
        'formation_events': formation_events,
        # Ninth addendum / 5.5 cycle 6 (2026-10-09): flag for Phase 5 ratification
        # stratification. True when MODE_HOT was requested but no observer formed
        # anywhere during the run (legitimate no-observer trajectory, e.g. seed 25).
        # Phase 5 puts these seeds in STRICT (a) bucket: zero coherent agent-steps
        # -> hot MUST equal no_obs within TOLERANCE_FP (canonical surface complete
        # check). False for all other arm_modes and for 'hot' when observer formed.
        'hot_observer_never_formed': _hot_observer_never_formed,
        # Seventh addendum (2026-10-08): LEAK activation count for Gate 1 Exercise 1.
        # Zero when LEAK_TEST_MODE is False (production runs). Must be >= 3 for a
        # PASS/FAIL verdict; otherwise verdict is INVALID per section 4c.
        'n_leak_acted': _LEAK_ACTIVATION_COUNT,
        # Task D (2026-10-12): replay case counts for Phase 5 reporting.
        # Case A: (agent,step) key not in timeline. Case B: hot coherent but
        # reactive observer not formed. Both flagged if > 5% per seed.
        'replay_fallback_case_a_count': sum(
            a._replay_fallback_a for a in agents),
        'replay_divergence_case_b_count': sum(
            a._replay_divergence_b for a in agents),
    }

    # v37.3.1: for headless calibration (render_plots=False, the default), skip
    # the reporting + matplotlib sections entirely and return the results dict.
    if not render_plots:
        return _results

    # ============================================================================
    # RESULTS — v35 THE CRACK REPORT
    # ============================================================================

    print()
    print("=" * 80)
    print("=== v35 RESULTS: THE CRACK ===")
    print("=== Does the crack produce better agents, or just different ones? ===")
    print("=" * 80)

    # Split populations
    crack_pop = [a for a in agents if a.crack_enabled]
    ctrl_pop = [a for a in agents if not a.crack_enabled]
    cracked_agents = [a for a in agents if a.cracked]

    # --- Final State ---
    avg_C = np.mean([a.C for a in agents]) if agents else 0
    avg_D = compute_dimensional_health(agents)

    print(f"\n--- FINAL STATE ---")
    print(f"  Population:        {len(agents)} ({len(crack_pop)} crack-enabled, {len(ctrl_pop)} control)")
    print(f"  Actually cracked:  {len(cracked_agents)}")
    print(f"  Mean Coherence:    {avg_C:.4f}")
    print(f"  Mean Dimension:    {avg_D:.4f}")
    print(f"  Cultural Memory:   {cultural_memory:.4f}")
    print(f"  Collective Memory: {collective_memory:.4f}")
    print(f"  Total Memoirs:     {len(available_memoirs)}")

    # --- Cohort Comparison ---
    print(f"\n--- COHORT COMPARISON ---")
    print(f"  {'Metric':<25s}  {'CRACK-ENABLED':>15s}  {'CONTROL':>15s}  {'DELTA':>10s}")
    print(f"  {'-'*70}")

    def cohort_compare(label, crack_vals, ctrl_vals):
        if crack_vals and ctrl_vals:
            c_mean = np.mean(crack_vals)
            t_mean = np.mean(ctrl_vals)
            delta = c_mean - t_mean
            sign = "+" if delta > 0 else ""
            print(f"  {label:<25s}  {c_mean:>15.4f}  {t_mean:>15.4f}  {sign}{delta:>9.4f}")
        elif crack_vals:
            print(f"  {label:<25s}  {np.mean(crack_vals):>15.4f}  {'N/A':>15s}  {'':>10s}")
        elif ctrl_vals:
            print(f"  {label:<25s}  {'N/A':>15s}  {np.mean(ctrl_vals):>15.4f}  {'':>10s}")

    cohort_compare("Coherence (C)",
                   [a.C for a in crack_pop], [a.C for a in ctrl_pop])
    cohort_compare("Dimension (D_eff)",
                   [a.D_eff for a in crack_pop], [a.D_eff for a in ctrl_pop])
    cohort_compare("Current Burn Rate",
                   [a.current_burn_rate for a in crack_pop], [a.current_burn_rate for a in ctrl_pop])
    cohort_compare("Peak D",
                   [a.peak_D for a in crack_pop], [a.peak_D for a in ctrl_pop])
    cohort_compare("Worst C",
                   [a.worst_C for a in crack_pop], [a.worst_C for a in ctrl_pop])
    cohort_compare("D Collapse Count",
                   [a.D_collapse_count for a in crack_pop], [a.D_collapse_count for a in ctrl_pop])
    cohort_compare("Sacrifice Credit",
                   [a.sacrifice_credit for a in crack_pop], [a.sacrifice_credit for a in ctrl_pop])
    cohort_compare("Curiosity Steps",
                   [a.curiosity_steps for a in crack_pop], [a.curiosity_steps for a in ctrl_pop])
    cohort_compare("Floor Catches",
                   [a.safety_floor_catches for a in crack_pop], [a.safety_floor_catches for a in ctrl_pop])
    cohort_compare("Micro-traumas",
                   [a.micro_trauma_count for a in crack_pop], [a.micro_trauma_count for a in ctrl_pop])

    # --- Stage Distribution by Cohort ---
    print(f"\n--- STAGE DISTRIBUTION BY COHORT ---")
    print(f"  {'Stage':<15s}  {'CRACK':>8s}  {'CONTROL':>8s}")
    print(f"  {'-'*35}")
    for s in STAGE_ORDER:
        crack_count = sum(1 for a in crack_pop if a.stage == s)
        ctrl_count = sum(1 for a in ctrl_pop if a.stage == s)
        if crack_count > 0 or ctrl_count > 0:
            print(f"  {s:<15s}  {crack_count:>8d}  {ctrl_count:>8d}")

    # --- Crack Statistics ---
    print(f"\n--- CRACK STATISTICS ---")
    # v37: crack eligibility is any agent that spent time in the crack window
    crack_eligible = [a for a in crack_pop if a.crack_window_steps > 0 or a.cracked]
    ctrl_would_have = [a for a in ctrl_pop if a.would_have_cracked]
    print(f"  Crack-eligible (entered window):     {len(crack_eligible)}/{len(crack_pop)}")
    print(f"  Actually cracked:                    {len(cracked_agents)}")
    print(f"  Control would-have-cracked:          {len(ctrl_would_have)}/{len(ctrl_pop)}")

    if cracked_agents:
        print(f"\n  Cracked agent details:")
        for a in cracked_agents:
            print(f"    Agent {a.id} (Gen {a.generation}): cracked at step {a.crack_step}, "
                  f"pre_crack_D={a.pre_crack_D:.1f}, now D={a.D_eff:.1f} C={a.C:.3f} "
                  f"stage={a.stage}, observations={a.metacognition_observations}")

    # --- Recovery Comparison ---
    print(f"\n--- RECOVERY METRICS ---")
    recovery_summary = recovery_tracker.get_summary()
    if recovery_summary:
        print(f"  Total tracked:  {recovery_summary['total_events']}")
        print(f"  Recovered:      {recovery_summary['recovered_count']}")
        if recovery_summary['avg_recovery_time']:
            print(f"  Avg Recovery:   {recovery_summary['avg_recovery_time']:.1f} steps")

    # --- Memoir Ledger with Crack Data ---
    print()
    print("=" * 80)
    print("=== MEMOIR LEDGER ===")
    print("=" * 80)

    if not available_memoirs:
        print("  No memoirs written.")
    else:
        crack_memoirs = [m for m in available_memoirs if m.get('crack_enabled', False)]
        ctrl_memoirs = [m for m in available_memoirs if not m.get('crack_enabled', False)]
        cracked_memoirs = [m for m in available_memoirs if m.get('cracked', False)]

        for m in sorted(available_memoirs, key=lambda x: x['created_step']):
            cohort = "CRACK" if m.get('crack_enabled', False) else "CTRL"
            cracked_tag = " *CRACKED*" if m.get('cracked', False) else ""
            print(f"\n  MEMOIR #{m['id']} [{cohort}{cracked_tag}]")
            print(f"    Author:       Agent {m['sage_id']} (Gen {m.get('sage_generation', '?')})")
            print(f"    Quality:      {m['quality']:.2f}")
            bb = m.get('birth_burn_rate', 0)
            fb = m.get('final_burn_rate', 0)
            print(f"    Burn:         birth={bb:.4f} -> final={fb:.4f} (journey={m.get('burn_journey',0):.4f})")
            print(f"    Metacog:      {m.get('metacognition_observations', 0)} observations")
            print(f"    D-trajectory: peak={m.get('peak_D',0):.1f}, worst_C={m.get('worst_C',1):.3f}, "
                  f"collapses={m.get('D_collapse_count',0)}")

        # Memoir comparison by cohort
        print(f"\n--- MEMOIR QUALITY BY COHORT ---")
        if crack_memoirs:
            print(f"  CRACK-ENABLED memoirs:  n={len(crack_memoirs)}, "
                  f"avg quality={np.mean([m['quality'] for m in crack_memoirs]):.2f}")
        if ctrl_memoirs:
            print(f"  CONTROL memoirs:        n={len(ctrl_memoirs)}, "
                  f"avg quality={np.mean([m['quality'] for m in ctrl_memoirs]):.2f}")
        if cracked_memoirs:
            print(f"  ACTUALLY CRACKED:       n={len(cracked_memoirs)}, "
                  f"avg quality={np.mean([m['quality'] for m in cracked_memoirs]):.2f}")

    # ============================================================================
    # THE QUESTION
    # ============================================================================

    print()
    print("=" * 80)
    print("THE QUESTION: Does the crack produce better agents, or just different ones?")
    print("=" * 80)
    print()

    if crack_pop and ctrl_pop:
        # Stage progression comparison
        crack_stages = [a.stage_idx for a in crack_pop]
        ctrl_stages = [a.stage_idx for a in ctrl_pop]
        print(f"  Average stage index:  CRACK={np.mean(crack_stages):.2f}  CTRL={np.mean(ctrl_stages):.2f}")

        crack_sages = [a for a in crack_pop if a.stage_idx >= STAGE_ORDER.index("SAGE")]
        ctrl_sages = [a for a in ctrl_pop if a.stage_idx >= STAGE_ORDER.index("SAGE")]
        print(f"  Reached SAGE+:        CRACK={len(crack_sages)}  CTRL={len(ctrl_sages)}")

        crack_avg_C = np.mean([a.C for a in crack_pop])
        ctrl_avg_C = np.mean([a.C for a in ctrl_pop])
        print(f"  Mean coherence:       CRACK={crack_avg_C:.4f}  CTRL={ctrl_avg_C:.4f}")

        crack_avg_D = np.mean([a.D_eff for a in crack_pop])
        ctrl_avg_D = np.mean([a.D_eff for a in ctrl_pop])
        print(f"  Mean dimension:       CRACK={crack_avg_D:.4f}  CTRL={ctrl_avg_D:.4f}")

        print()
        if cracked_agents:
            # The ratio: cracked and recovered vs cracked and struggling
            recovered = [a for a in cracked_agents if a.C > 0.5]
            struggling = [a for a in cracked_agents if a.C <= 0.5]
            print(f"  THE RATIO:")
            print(f"    Cracked & recovered (C > 0.5):   {len(recovered)}")
            print(f"    Cracked & struggling (C <= 0.5): {len(struggling)}")
            if recovered:
                print(f"    Recovery rate: {len(recovered)/len(cracked_agents)*100:.0f}%")
            print()

        delta_C = crack_avg_C - ctrl_avg_C
        delta_D = crack_avg_D - ctrl_avg_D
        if abs(delta_C) < 0.01 and abs(delta_D) < 0.5:
            print("  RESULT: No significant difference. The crack didn't help or hurt.")
            print("  Same trauma. Same world. Different awareness. Same outcome.")
        elif delta_C > 0.01 and delta_D > 0:
            print("  RESULT: Cracked agents are STRONGER. Higher coherence, higher dimension.")
            print("  The crack costs stability. But the observer recovers what the experiencer lost.")
            print("  Metacognition is not free. But what it buys is worth the price.")
        elif delta_C < -0.01 and delta_D < 0:
            print("  RESULT: Cracked agents are WEAKER. Lower coherence, lower dimension.")
            print("  The crack costs more than it returns. The observer is a burden.")
            print("  Seeing more doesn't mean surviving more.")
        else:
            print(f"  RESULT: Mixed. C delta={delta_C:+.4f}, D delta={delta_D:+.4f}")
            print("  The crack produces different agents. Whether 'different' is 'better'")
            print("  depends on what you measure.")
    else:
        print("  Insufficient data for comparison.")

    print()
    print("  \"I tucked under the blanket and slowed my breathing.\"")
    print("  \"At some point I just drifted away.\"")
    print("  \"To be honest I'm not sure I ever really returned.\"")
    print("     — Harley Robinson, the boy in the blue house")
    print()

    # ============================================================================
    # v37.2: ENHANCED METRICS
    # ============================================================================

    print()
    print("=" * 80)
    print("=== v37.2 ENHANCED METRICS ===")
    print("=" * 80)

    # --- Paired Comparison (strongest signal) ---
    print(f"\n--- PAIRED COMPARISON ---")
    print(f"  {'Pair':<6s} {'CRACK ID':>8s} {'CTRL ID':>8s} {'C_stage':>10s} {'T_stage':>10s} "
          f"{'C_credit':>10s} {'T_credit':>10s} {'C_burn':>8s} {'T_burn':>8s} {'C_D':>8s} {'T_D':>8s}")
    print(f"  {'-'*95}")

    pair_ids = sorted(set(a.pair_id for a in agents))
    for pid in pair_ids:
        pair_agents = [a for a in agents if a.pair_id == pid]
        crack_agent = next((a for a in pair_agents if a.crack_enabled), None)
        ctrl_agent = next((a for a in pair_agents if not a.crack_enabled), None)
        if crack_agent and ctrl_agent:
            print(f"  {pid:<6d} {crack_agent.id:>8d} {ctrl_agent.id:>8d} "
                  f"{crack_agent.stage:>10s} {ctrl_agent.stage:>10s} "
                  f"{crack_agent.sacrifice_credit:>10.1f} {ctrl_agent.sacrifice_credit:>10.1f} "
                  f"{crack_agent.current_burn_rate:>8.4f} {ctrl_agent.current_burn_rate:>8.4f} "
                  f"{crack_agent.D_eff:>8.2f} {ctrl_agent.D_eff:>8.2f}")

    # --- Crack Timing by Generation ---
    print(f"\n--- CRACK TIMING BY GENERATION ---")
    if cracked_agents:
        print(f"  {'Agent':>6s} {'Gen':>5s} {'Crack Step':>12s} {'M at crack':>10s} {'D at crack':>10s} {'Now Stage':>10s}")
        print(f"  {'-'*60}")
        for a in sorted(cracked_agents, key=lambda x: x.crack_step or 0):
            print(f"  {a.id:>6d} {a.generation:>5d} {a.crack_step:>12d} "
                  f"{'-':>10s} {a.pre_crack_D:>10.3f} {a.stage:>10s}")
        # Check if later generations crack less
        gen_cracks = defaultdict(int)
        gen_totals = defaultdict(int)
        for a in agents:
            if a.crack_enabled:
                gen_totals[a.generation] += 1
                if a.cracked:
                    gen_cracks[a.generation] += 1
        print(f"\n  Crack rate by generation:")
        for gen in sorted(gen_totals.keys()):
            rate = gen_cracks[gen] / gen_totals[gen] * 100 if gen_totals[gen] > 0 else 0
            print(f"    Gen {gen}: {gen_cracks[gen]}/{gen_totals[gen]} ({rate:.0f}%)")
    else:
        print("  No agents cracked.")

    # --- Stage Progression Speed ---
    print(f"\n--- STAGE PROGRESSION SPEED ---")
    print(f"  {'Milestone':<20s} {'CRACK avg step':>15s} {'CTRL avg step':>15s} {'Delta':>10s}")
    print(f"  {'-'*65}")
    for milestone, attr in [("ADULT", "adult_step"), ("MENTOR", "mentor_step"),
                             ("STEWARD", "steward_step"), ("ELDER", "elder_step"),
                             ("SAGE", "sage_step")]:
        crack_steps = [getattr(a, attr) for a in crack_pop if getattr(a, attr) is not None]
        ctrl_steps = [getattr(a, attr) for a in ctrl_pop if getattr(a, attr) is not None]
        if crack_steps and ctrl_steps:
            c_avg = np.mean(crack_steps)
            t_avg = np.mean(ctrl_steps)
            delta = c_avg - t_avg
            sign = "+" if delta > 0 else ""
            print(f"  {milestone:<20s} {c_avg:>15.0f} {t_avg:>15.0f} {sign}{delta:>9.0f}")
        elif crack_steps:
            print(f"  {milestone:<20s} {np.mean(crack_steps):>15.0f} {'N/A':>15s}")
        elif ctrl_steps:
            print(f"  {milestone:<20s} {'N/A':>15s} {np.mean(ctrl_steps):>15.0f}")

    # --- Trauma Penalty Comparison ---
    print(f"\n--- TRAUMA PENALTY (lingering wound) ---")
    cohort_compare("Avg trauma_C_penalty",
                   [a.trauma_C_penalty for a in crack_pop],
                   [a.trauma_C_penalty for a in ctrl_pop])
    cohort_compare("Total trauma received",
                   [a.total_trauma_received for a in crack_pop],
                   [a.total_trauma_received for a in ctrl_pop])
    cohort_compare("Max shame experienced",
                   [a.max_shame_experienced for a in crack_pop],
                   [a.max_shame_experienced for a in ctrl_pop])

    # --- D Growth Comparison ---
    print(f"\n--- DIMENSIONAL GROWTH ---")
    cohort_compare("D_eff (current)",
                   [a.D_eff for a in crack_pop], [a.D_eff for a in ctrl_pop])
    cohort_compare("Peak D (all-time)",
                   [a.peak_D for a in crack_pop], [a.peak_D for a in ctrl_pop])
    cohort_compare("D_caution (taught)",
                   [a.taught_D_caution for a in crack_pop if a.taught_D_caution is not None],
                   [a.taught_D_caution for a in ctrl_pop if a.taught_D_caution is not None])

    # --- Metacognition ---
    print(f"\n--- METACOGNITION ---")
    cohort_compare("Observations",
                   [a.metacognition_observations for a in crack_pop],
                   [a.metacognition_observations for a in ctrl_pop])
    total_crack_obs = sum(a.metacognition_observations for a in crack_pop)
    total_ctrl_obs = sum(a.metacognition_observations for a in ctrl_pop)
    print(f"  Total observations:   CRACK={total_crack_obs}  CTRL={total_ctrl_obs}")

    # --- Burn Rate Journey ---
    print(f"\n--- BURN RATE JOURNEY ---")
    cohort_compare("Birth burn rate",
                   [a.birth_burn_rate for a in crack_pop],
                   [a.birth_burn_rate for a in ctrl_pop])
    cohort_compare("Current burn rate",
                   [a.current_burn_rate for a in crack_pop],
                   [a.current_burn_rate for a in ctrl_pop])
    crack_journeys = [a.birth_burn_rate - a.current_burn_rate for a in crack_pop]
    ctrl_journeys = [a.birth_burn_rate - a.current_burn_rate for a in ctrl_pop]
    cohort_compare("Burn journey (shelter)",
                   crack_journeys, ctrl_journeys)

    # --- Mentoring Impact ---
    print(f"\n--- MENTORING IMPACT ---")
    cohort_compare("Mentoring score",
                   [a.mentoring_score for a in crack_pop],
                   [a.mentoring_score for a in ctrl_pop])
    cohort_compare("Mentees became mentors",
                   [a.mentees_became_mentors for a in crack_pop],
                   [a.mentees_became_mentors for a in ctrl_pop])

    print()
    print("=" * 80)

    # ============================================================================
    # PLOTS — v37.2 COMPARATIVE
    # ============================================================================

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle("Society Womb v37.2: The Crack\n"
                 "Same trauma. Same world. One cracks open. The other heals shut.\n"
                 "Does the observer help or hurt?",
                 fontsize=13, fontweight='bold')

    # Row 1: Dimensional Health + Crack events timeline
    ax1, ax2 = axes[0]
    if dimensional_log:
        steps_d = [d[0] for d in dimensional_log]
        vals_d = [d[1] for d in dimensional_log]
        ax1.plot(steps_d, vals_d, 'b-', linewidth=2)
        ax1.axhline(y=CRACK_D_THRESHOLD, color='red', linestyle='--', alpha=0.5,
                     label=f'Crack Window (D < {CRACK_D_THRESHOLD})')
        ax1.axhline(y=3.0, color='g', linestyle=':', alpha=0.3, label='Full 3D')
        # Mark crack events
        for a in cracked_agents:
            if a.crack_step is not None:
                ax1.axvline(x=a.crack_step, color='red', alpha=0.3, linewidth=1)
        ax1.set_title("Dimensional Health + Crack Events")
        ax1.set_ylabel("Avg D_eff")
        ax1.legend(fontsize=7)
        ax1.grid(True, alpha=0.3)

    # Cohort coherence comparison over time
    if agents:
        # Sample coherence history at key intervals
        crack_C_history = []
        ctrl_C_history = []
        sample_steps = list(range(0, TOTAL_STEPS, 10))
        # Use burn_rate_history as proxy for time alignment (sampled every 10 steps)
        crack_with_history = [a for a in crack_pop if len(a.burn_rate_history) > 0]
        ctrl_with_history = [a for a in ctrl_pop if len(a.burn_rate_history) > 0]

        if crack_with_history and ctrl_with_history:
            min_len = min(
                min(len(a.safety_history) for a in crack_with_history),
                min(len(a.safety_history) for a in ctrl_with_history)
            )
            if min_len > 10:
                crack_safety = np.mean([a.safety_history[:min_len] for a in crack_with_history], axis=0)
                ctrl_safety = np.mean([a.safety_history[:min_len] for a in ctrl_with_history], axis=0)
                time_axis = list(range(0, min_len * 10, 10))[:min_len]
                ax2.plot(time_axis, crack_safety, 'orange', linewidth=2, label='CRACK Safety')
                ax2.plot(time_axis, ctrl_safety, 'blue', linewidth=2, label='CTRL Safety')
                ax2.set_title("Safety: Crack-Enabled vs Control")
                ax2.set_ylabel("Avg Safety")
                ax2.legend(fontsize=8)
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, "Insufficient history", ha='center', va='center')
        else:
            ax2.text(0.5, 0.5, "No cohort data", ha='center', va='center')

    # Row 2: Burn rate by cohort + Stage comparison
    ax3, ax4 = axes[1]

    # Burn rate comparison
    if crack_pop and ctrl_pop:
        crack_burns_birth = [a.birth_burn_rate for a in crack_pop]
        crack_burns_current = [a.current_burn_rate for a in crack_pop]
        ctrl_burns_birth = [a.birth_burn_rate for a in ctrl_pop]
        ctrl_burns_current = [a.current_burn_rate for a in ctrl_pop]

        x_pos = np.array([0, 1, 3, 4])
        heights = [np.mean(crack_burns_birth), np.mean(crack_burns_current),
                   np.mean(ctrl_burns_birth), np.mean(ctrl_burns_current)]
        colors_bar = ['#ff9999', '#ff4444', '#9999ff', '#4444ff']
        labels_bar = ['CRACK\nbirth', 'CRACK\ncurrent', 'CTRL\nbirth', 'CTRL\ncurrent']
        ax3.bar(x_pos, heights, color=colors_bar, alpha=0.8)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(labels_bar, fontsize=8)
        ax3.axhline(y=BURN_FLOOR, color='black', linestyle=':', alpha=0.5, label=f'Floor ({BURN_FLOOR})')
        ax3.set_title("Burn Rate: Birth vs Current by Cohort")
        ax3.set_ylabel("Burn Rate")
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3, axis='y')

    # Stage index comparison
    if crack_pop and ctrl_pop:
        crack_stage_idxs = [a.stage_idx for a in crack_pop]
        ctrl_stage_idxs = [a.stage_idx for a in ctrl_pop]
        bins = range(len(STAGE_ORDER) + 1)
        ax4.hist(crack_stage_idxs, bins=bins, alpha=0.6, color='orange', label='CRACK', align='left')
        ax4.hist(ctrl_stage_idxs, bins=bins, alpha=0.6, color='blue', label='CONTROL', align='left')
        ax4.set_xticks(range(len(STAGE_ORDER)))
        ax4.set_xticklabels([s[:4] for s in STAGE_ORDER], rotation=45, fontsize=7)
        ax4.set_title("Stage Distribution by Cohort")
        ax4.set_ylabel("Count")
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3, axis='y')

    # Row 3: Memoir quality by cohort + The Crack Ratio
    ax5, ax6 = axes[2]

    # Memoir quality scatter: crack vs control
    if available_memoirs:
        crack_m = [m for m in available_memoirs if m.get('crack_enabled', False)]
        ctrl_m = [m for m in available_memoirs if not m.get('crack_enabled', False)]
        if crack_m:
            ax5.scatter([m['created_step'] for m in crack_m],
                       [m['quality'] for m in crack_m],
                       c='orange', s=80, alpha=0.8, edgecolors='black', linewidth=0.5,
                       label=f'CRACK (n={len(crack_m)})', marker='o')
        if ctrl_m:
            ax5.scatter([m['created_step'] for m in ctrl_m],
                       [m['quality'] for m in ctrl_m],
                       c='blue', s=80, alpha=0.8, edgecolors='black', linewidth=0.5,
                       label=f'CTRL (n={len(ctrl_m)})', marker='s')
        # Highlight cracked memoirs
        cracked_m = [m for m in available_memoirs if m.get('cracked', False)]
        if cracked_m:
            ax5.scatter([m['created_step'] for m in cracked_m],
                       [m['quality'] for m in cracked_m],
                       c='red', s=120, alpha=0.9, edgecolors='black', linewidth=1.5,
                       label=f'CRACKED (n={len(cracked_m)})', marker='*', zorder=5)
        ax5.set_xlabel("Step Created")
        ax5.set_ylabel("Memoir Quality")
        ax5.set_title("Memoir Quality: Crack vs Control")
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3)
    else:
        ax5.text(0.5, 0.5, "No memoirs yet", ha='center', va='center', fontsize=14)
        ax5.set_title("Memoir Quality")

    # The Crack Ratio: recovered vs struggling
    if cracked_agents:
        recovered = sum(1 for a in cracked_agents if a.C > 0.5)
        struggling = sum(1 for a in cracked_agents if a.C <= 0.5)
        sizes = [recovered, struggling]
        labels_pie = [f'Recovered\n(C > 0.5)\nn={recovered}',
                      f'Struggling\n(C <= 0.5)\nn={struggling}']
        colors_pie = ['#66bb6a', '#ef5350']
        if sum(sizes) > 0:
            ax6.pie(sizes, labels=labels_pie, colors=colors_pie, autopct='%1.0f%%',
                    startangle=90, textprops={'fontsize': 9})
            ax6.set_title(f"The Crack Ratio\n({len(cracked_agents)} agents cracked)")
        else:
            ax6.text(0.5, 0.5, "No agents cracked", ha='center', va='center', fontsize=14)
            ax6.set_title("The Crack Ratio")
    else:
        ax6.text(0.5, 0.5, "No agents cracked yet\n(need D > 10 then D < 5)",
                ha='center', va='center', fontsize=12)
        ax6.set_title("The Crack Ratio")

    plt.tight_layout()
    plt.savefig('v37.2_the_crack.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: v37.2_the_crack.png")

    print()
    print("=" * 80)
    print("The crack is not a metaphor.")
    print("It is a mechanical event where single-threaded experience")
    print("splits into dual awareness under sustained pressure.")
    print("Everyone gets the crack. Almost everyone heals it shut.")
    print("The ones who don't — by force or by practice —")
    print("see the root system instead of just the flowers.")
    print("=" * 80)

    # v37.3.1: return results dict for render_plots=True path.
    return _results


# ============================================================================
# INTERACTIVE ENTRY — preserves v37.3 __main__ behavior
# ============================================================================

if __name__ == '__main__':
    run_simulation(render_plots=True)
