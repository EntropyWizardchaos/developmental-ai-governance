"""Stage 2 four-arm hooks — symmetric capture + inject + observer-off assertion.

Three hooks, two sites. All four arms (hot/yoked/matched/no_obs) traverse the
same code path at each site. Mode dispatch is pure parameter difference — no
arm has unique branching code.

Hook Site 1 (top of step, after canonicalize_observer_channels):
  _capture_canonical          — snapshot burn_decay/trauma_decay/refusal
  _apply_canonical_override   — inject or offset burn_decay/trauma_decay/refusal
  _assert_observer_off        — per-step invariant for non-hot arms

Hook Site 2 (inside society_step, after agent.step_observer):
  _capture_canonical_D_caution        — snapshot canonical_D_caution
  _apply_canonical_override_D_caution — inject or offset canonical_D_caution

Rank snapshot computed ONCE at top of step; used at BOTH sites so an agent
cannot receive two different source ranks within one step.

Mode split per Salazaar Finding 6 (2026-10-06): MODE_IDENTITY was ambiguous
between hot (observer on) and no_obs (observer off), which enabled the
Finding 1 vacuous-sanity-gate bug. Split into MODE_HOT and MODE_NO_OBS.

Reference: stage_2_yoked_design_2026-10-05.md §4
Spec attribution: Opus 5.5 (via Harley) + Salazaar 2026-10-06.
"""
from __future__ import annotations

# -- Modes --
MODE_HOT = "hot"             # observer live; capture may be enabled
MODE_NO_OBS = "no_obs"       # observer off, no injection; baselines stand
MODE_YOKED = "yoked"         # observer off, canonical values injected from source trace
MODE_MATCHED  = "matched"    # observer off, uniform mu_c offset
MODE_REACTIVE = "reactive"   # observer live, coherence driven by replay timeline

VALID_MODES  = {MODE_HOT, MODE_NO_OBS, MODE_YOKED, MODE_MATCHED, MODE_REACTIVE}
NON_HOT_MODES = {MODE_NO_OBS, MODE_YOKED, MODE_MATCHED}

# -- Baselines (identity values); keep in sync with v37.3.1 constants --
BASELINE_BURN_DECAY_MULT = 1.0
BASELINE_TRAUMA_DECAY_EXP = 1.0
BASELINE_REFUSAL_CHANCE = 0.10        # SACRIFICE_REFUSAL_CHANCE
BASELINE_D_CAUTION = 50.0             # D_MAX; None also behaviorally neutral

# -- Coherence declaration criterion (locked in fifth addendum §7) --
MIN_COHERENT_STEPS_FOR_DECLARATION = 50


# ---------------------------------------------------------------------------
# Rank snapshot — computed once per step, used at both hook sites.
# ---------------------------------------------------------------------------
def build_step_rank_snapshot(agents):
    """Sort rule written in trace pickle metadata (schema §5):
    rank = sorted(agents_alive_at_step_t, key=lambda a: (a.birth_step, a.id)).
    Returns {agent_id: rank}.
    """
    sorted_agents = sorted(agents, key=lambda a: (a.birth_step, a.id))
    return {a.id: rank for rank, a in enumerate(sorted_agents)}


# ---------------------------------------------------------------------------
# Hook Site 1 — top of step, after canonicalize_observer_channels for all agents.
# ---------------------------------------------------------------------------
def capture_canonical(agents, t, trace_buffer, rank_snapshot):
    """No-op when trace_buffer is None.
    When active, writes one record per agent per step keyed by rank.
    """
    if trace_buffer is None:
        return
    records = []
    for a in agents:
        records.append({
            "rank": rank_snapshot[a.id],
            "agent_id": a.id,                    # Sal Finding 7: forensic trace
            "burn_decay_mult": a.canonical_burn_decay_mult,
            "trauma_decay_exp": a.canonical_trauma_decay_exp,
            "refusal_chance": a.canonical_refusal_chance,
            "observer_coherent": _safe_coherent(a),
        })
    if t not in trace_buffer:
        trace_buffer[t] = {"canonical": records, "D_caution": []}
    else:
        trace_buffer[t]["canonical"] = records


def apply_canonical_override(agents, t, mode, trace_dict, mu_c_dict, rank_snapshot):
    """Mode dispatch:
      MODE_HOT, MODE_NO_OBS: no-op (observer-written or baseline values stand)
      MODE_YOKED: replace from trace_dict's canonical records at step t, matched by rank
      MODE_MATCHED: write baseline + mu_c uniformly
    Refusal_chance is clamped to [0,1] in both inject modes.
    """
    if mode in (MODE_HOT, MODE_NO_OBS, MODE_REACTIVE):
        return

    if mode == MODE_YOKED:
        if trace_dict is None:
            raise ValueError("mode=yoked requires trace_dict")
        step_records = trace_dict.get("traces_by_step", {}).get(t, {}).get("canonical", [])
        rec_by_rank = {r["rank"]: r for r in step_records}
        for a in agents:
            rank = rank_snapshot[a.id]
            if rank in rec_by_rank:
                r = rec_by_rank[rank]
                a.canonical_burn_decay_mult = r["burn_decay_mult"]
                a.canonical_trauma_decay_exp = r["trauma_decay_exp"]
                a.canonical_refusal_chance = _clamp01(r["refusal_chance"])
            # else: overhang; baselines stand from canonicalize_observer_channels
        return

    if mode == MODE_MATCHED:
        if mu_c_dict is None:
            raise ValueError("mode=matched requires mu_c_dict")
        burn_offset = mu_c_dict.get("burn_decay", 0.0)
        trauma_offset = mu_c_dict.get("trauma_decay", 0.0)
        refusal_offset = mu_c_dict.get("refusal_chance", 0.0)
        for a in agents:
            a.canonical_burn_decay_mult = BASELINE_BURN_DECAY_MULT + burn_offset
            a.canonical_trauma_decay_exp = BASELINE_TRAUMA_DECAY_EXP + trauma_offset
            a.canonical_refusal_chance = _clamp01(BASELINE_REFUSAL_CHANCE + refusal_offset)
        return

    raise ValueError(f"Unknown mode: {mode!r} (expected one of {VALID_MODES})")


def assert_observer_off(agents, mode, t):
    """Per-step invariant: non-hot arms must have observer.exists == False
    for every agent at step t. Catches mid-run observer leaks immediately.
    MODE_HOT is skipped (observers are expected); the MODE_HOT inverse
    assertion (at least one observer ever formed) runs at end of simulation
    via assert_hot_had_observer().
    """
    if mode in (MODE_HOT, MODE_REACTIVE):
        return
    if mode not in NON_HOT_MODES:
        raise ValueError(f"Unknown mode: {mode!r}")
    for a in agents:
        if a.observer.exists:
            raise AssertionError(
                f"Observer-off invariant failed at step {t} in mode={mode!r}: "
                f"agent {a.id} has observer.exists=True."
            )


def assert_hot_had_observer(agents_history, seed):
    """MODE_HOT inverse assertion — called once at end of hot run.
    At least one agent must have had observer.exists=True at some point.
    If none, the arm isn't doing what it claims.

    agents_history: iterable yielding every agent that ever lived during
                    the run (including those that died). Caller must
                    track this; current v37.3.1 only has `agents` list at
                    end-of-run — see integration note in design doc §13.5.
    """
    for a in agents_history:
        if a.observer.exists:
            return
    raise AssertionError(
        f"MODE_HOT invariant failed on seed {seed}: no observer ever formed. "
        f"Arm did not exercise the observer pathway."
    )


# ---------------------------------------------------------------------------
# Hook Site 2 — inside society_step, immediately after agent.step_observer(t).
# ---------------------------------------------------------------------------
def capture_canonical_D_caution(agent, t, trace_buffer, rank_snapshot):
    """Per-agent per-step snapshot of canonical_D_caution. No-op if trace_buffer None."""
    if trace_buffer is None:
        return
    if t not in trace_buffer:
        trace_buffer[t] = {"canonical": [], "D_caution": []}
    trace_buffer[t]["D_caution"].append({
        "rank": rank_snapshot[agent.id],
        "agent_id": agent.id,                        # Sal Finding 7
        "canonical_D_caution": agent.canonical_D_caution,
        "observer_coherent": _safe_coherent(agent),
    })


def apply_canonical_override_D_caution(agent, t, mode, trace_dict, mu_c_dict, rank_snapshot):
    """Per-agent dispatch at Hook Site 2.
      MODE_HOT, MODE_NO_OBS: no-op
      MODE_YOKED: replace from trace_dict's D_caution record at (step t, matching rank).
                  None injected verbatim when source had None (behaviorally neutral).
      MODE_MATCHED: write BASELINE_D_CAUTION + mu_c uniformly.
    """
    if mode in (MODE_HOT, MODE_NO_OBS, MODE_REACTIVE):
        return

    if mode == MODE_YOKED:
        if trace_dict is None:
            raise ValueError("mode=yoked requires trace_dict")
        step_records = trace_dict.get("traces_by_step", {}).get(t, {}).get("D_caution", [])
        rec_by_rank = {r["rank"]: r for r in step_records}
        rank = rank_snapshot[agent.id]
        if rank in rec_by_rank:
            agent.canonical_D_caution = rec_by_rank[rank]["canonical_D_caution"]
        # else: overhang; stays at init (None)
        return

    if mode == MODE_MATCHED:
        if mu_c_dict is None:
            raise ValueError("mode=matched requires mu_c_dict")
        D_offset = mu_c_dict.get("D_caution", 0.0)
        agent.canonical_D_caution = BASELINE_D_CAUTION + D_offset
        return

    raise ValueError(f"Unknown mode: {mode!r} (expected one of {VALID_MODES})")


# ---------------------------------------------------------------------------
# Trace serialization + coherence declaration.
# ---------------------------------------------------------------------------
def compute_coherence_declaration(agents_history):
    """Per fifth addendum §7: seed declared coherent if at least one agent
    had observer.coherent_steps >= MIN_COHERENT_STEPS_FOR_DECLARATION (50)
    at any point during the 3000-step run.

    agents_history: iterable yielding every agent that ever lived.
    """
    for a in agents_history:
        if getattr(a.observer, "coherent_steps", 0) >= MIN_COHERENT_STEPS_FOR_DECLARATION:
            return True
    return False


def build_trace_pickle_payload(seed, code_sha, trace_buffer, created_utc,
                               coherence_declaration):
    """Produce the dict to pickle for a hot run's trace. Schema per design doc §5."""
    return {
        "schema_version": 1,
        "source_seed": seed,
        "code_sha_v37_3_1": code_sha,
        "created_utc": created_utc,
        "coherence_declaration": coherence_declaration,
        "sort_rule": (
            "rank = sorted(agents_alive_at_step_t, "
            "key=lambda a: (a.birth_step, a.id))"
        ),
        "baselines": {
            "canonical_burn_decay_mult": BASELINE_BURN_DECAY_MULT,
            "canonical_trauma_decay_exp": BASELINE_TRAUMA_DECAY_EXP,
            "canonical_refusal_chance": BASELINE_REFUSAL_CHANCE,
            "canonical_D_caution": BASELINE_D_CAUTION,
        },
        "traces_by_step": trace_buffer,
    }


# ---------------------------------------------------------------------------
# Dose accounting.
# ---------------------------------------------------------------------------
def compute_dose(records, channel, baseline):
    """Sum |value - baseline| over all records. None values contribute 0."""
    total = 0.0
    for r in records:
        v = r.get(channel)
        if v is None:
            continue
        total += abs(v - baseline)
    return total


# ---------------------------------------------------------------------------
# Non-trivial-input assertion for Gate 1 Phase A (Sal Finding 1b).
# ---------------------------------------------------------------------------
def count_non_baseline_trace_records(trace_buffer, threshold_k=10):
    """Returns count of trace records (across all steps and both canonical+D_caution)
    where any channel differs from its baseline. Used to assert Gate 1 Phase A
    captured a non-trivial trace.

    Threshold K=10 locked in fifth addendum §5.2.
    """
    count = 0
    for step_data in trace_buffer.values():
        for r in step_data.get("canonical", []):
            if abs(r.get("burn_decay_mult", BASELINE_BURN_DECAY_MULT) - BASELINE_BURN_DECAY_MULT) > 0:
                count += 1; continue
            if abs(r.get("trauma_decay_exp", BASELINE_TRAUMA_DECAY_EXP) - BASELINE_TRAUMA_DECAY_EXP) > 0:
                count += 1; continue
            if abs(r.get("refusal_chance", BASELINE_REFUSAL_CHANCE) - BASELINE_REFUSAL_CHANCE) > 0:
                count += 1; continue
        for r in step_data.get("D_caution", []):
            v = r.get("canonical_D_caution")
            if v is not None and abs(v - BASELINE_D_CAUTION) > 0:
                count += 1
    return count


def assert_non_trivial_trace(trace_buffer, threshold_k=10):
    """Raises AssertionError if trace is all-baseline (or near enough)."""
    n = count_non_baseline_trace_records(trace_buffer)
    if n < threshold_k:
        raise AssertionError(
            f"Gate 1 Phase A trace has only {n} non-baseline records "
            f"(threshold K={threshold_k}). Either the hot run never produced "
            f"coherence (pick a different gate seed), or the capture code is "
            f"broken. Halting — does NOT count as a passed gate."
        )


# ---------------------------------------------------------------------------
# Internal helpers.
# ---------------------------------------------------------------------------
def _clamp01(x):
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _safe_coherent(agent):
    """Return True if agent.observer exists and is coherent."""
    obs = getattr(agent, "observer", None)
    if obs is None:
        return False
    exists = getattr(obs, "exists", False)
    coherent = getattr(obs, "coherent", False)
    return bool(exists and coherent)
