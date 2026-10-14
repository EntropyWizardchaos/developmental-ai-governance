"""Reactive-mode regression test for Task D on seed 22 (2026-10-13).

Strengthening test per Sal 016 recommendation. Seed 22 had 32.6% F5-direct
coherence-timeline divergence in the Oct 9 probe — reactive trajectory diverges
from hot's materially. Under REPLAY mode, we expect:
  - Coherence sets forced to match hot's (by replay construction) — bit-exact
  - Trajectory divergence > 0 (F5 overrides predicted_* with actuals; mapping
    functions read overridden values -> different modulation each step)
  - POSSIBLY Case A or Case B counters firing non-zero if formation timing
    shifts under divergent trajectory

Additional metrics beyond seed 20 regression:
  - Mean |canonical_burn_decay_mult_hot - canonical_burn_decay_mult_reactive|
    across coherent (agent, step) tuples
  - Final burn_integral delta
  - Divergence sanity: if 0, something's wrong (F5 not firing OR trajectories
    inexplicably identical). Investigate before Phase 1.
"""
import importlib.util
import sys
import pathlib

CODE_DIR = pathlib.Path(r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions")
sys.path.insert(0, str(CODE_DIR))

V37_4 = CODE_DIR / "v37.4_structural_metacognition_stage_2.py"
_spec = importlib.util.spec_from_file_location("v37_4", str(V37_4))
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
run_simulation = mod.run_simulation

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SEED = 22

print(f"Step 1: Run hot arm on seed {SEED}...")
hot_results = run_simulation(
    seed=SEED,
    all_crack_enabled=True,
    n_steps=3000,
    arm_mode='hot',
    log_channels=True,
    render_plots=False,
)

snapshots = hot_results['channel_snapshots']
print(f"  channel_snapshots: {len(snapshots)}")
print(f"  coherence_declaration: {hot_results['coherence_declaration']}")

# Build replay timeline
print("\nStep 2: Build replay_coherence_timeline...")
replay_coherence_timeline = {
    (s['agent_id'], s['step']): s['observer_coherent']
    for s in snapshots
}
coherent_keys = {k for k, v in replay_coherence_timeline.items() if v}
print(f"  timeline entries: {len(replay_coherence_timeline)}")
print(f"  hot coherent (agent,step) pairs: {len(coherent_keys)}")

hot_coherent_steps = {}
hot_burn_decay_by_key = {}  # (agent_id, step) -> canonical_burn_decay_mult, coherent only
for s in snapshots:
    if s['observer_coherent']:
        hot_coherent_steps[s['agent_id']] = hot_coherent_steps.get(s['agent_id'], 0) + 1
        hot_burn_decay_by_key[(s['agent_id'], s['step'])] = s['burn_decay_multiplier']
print(f"  hot coherent_steps per agent: {hot_coherent_steps}")

# Hot burn_integral
hot_burn_integral = 0.0
# BURN_RATE baseline — read from module
BURN_BASELINE = getattr(mod, 'BURN_RATE_BASELINE', None)
if BURN_BASELINE is None:
    # Fall back to the mean of birth burn rates (matches regression test logic)
    BURN_BASELINE = 0.0
    print(f"  WARNING: BURN_RATE_BASELINE not found; using 0.0 as baseline")
for s in snapshots:
    excess = s['actual_burn_rate'] - BURN_BASELINE
    if excess > 0:
        hot_burn_integral += excess
print(f"  hot burn_integral: {hot_burn_integral:.6f}")

print(f"\nStep 3: Run reactive arm on seed {SEED}...")
reactive_results = run_simulation(
    seed=SEED,
    all_crack_enabled=True,
    n_steps=3000,
    arm_mode='reactive',
    log_channels=True,
    replay_coherence_timeline=replay_coherence_timeline,
    render_plots=False,
)

reactive_snapshots = reactive_results['channel_snapshots']
case_a = reactive_results['replay_fallback_case_a_count']
case_b = reactive_results['replay_divergence_case_b_count']

print(f"  reactive channel_snapshots: {len(reactive_snapshots)}")
print(f"  fallback_case_a_count: {case_a}")
print(f"  formation_divergence_case_b_count: {case_b}")

reactive_coherent_keys = {
    (s['agent_id'], s['step'])
    for s in reactive_snapshots
    if s['observer_coherent']
}

hot_only = coherent_keys - reactive_coherent_keys
reactive_only = reactive_coherent_keys - coherent_keys

reactive_coherent_steps = {}
reactive_burn_decay_by_key = {}
for s in reactive_snapshots:
    if s['observer_coherent']:
        reactive_coherent_steps[s['agent_id']] = reactive_coherent_steps.get(s['agent_id'], 0) + 1
        reactive_burn_decay_by_key[(s['agent_id'], s['step'])] = s['burn_decay_multiplier']
print(f"  reactive coherent_steps per agent: {reactive_coherent_steps}")

reactive_burn_integral = 0.0
for s in reactive_snapshots:
    excess = s['actual_burn_rate'] - BURN_BASELINE
    if excess > 0:
        reactive_burn_integral += excess
print(f"  reactive burn_integral: {reactive_burn_integral:.6f}")

# Trajectory divergence metrics (coherent-subset)
print("\nStep 4: Trajectory divergence metrics...")
common_coherent_keys = coherent_keys & reactive_coherent_keys
burn_decay_diffs = []
for key in common_coherent_keys:
    hot_val = hot_burn_decay_by_key.get(key)
    rea_val = reactive_burn_decay_by_key.get(key)
    if hot_val is not None and rea_val is not None:
        burn_decay_diffs.append(abs(hot_val - rea_val))

if burn_decay_diffs:
    mean_divergence = sum(burn_decay_diffs) / len(burn_decay_diffs)
    max_divergence  = max(burn_decay_diffs)
    nonzero_count   = sum(1 for d in burn_decay_diffs if d > 1e-15)
    print(f"  common coherent (agent, step) tuples: {len(common_coherent_keys)}")
    print(f"  mean |burn_decay_mult_hot - burn_decay_mult_reactive|: {mean_divergence:.8f}")
    print(f"  max  |burn_decay_mult_hot - burn_decay_mult_reactive|: {max_divergence:.8f}")
    print(f"  non-zero diffs (> 1e-15): {nonzero_count}/{len(burn_decay_diffs)}")
else:
    mean_divergence = 0.0
    max_divergence  = 0.0
    nonzero_count   = 0
    print(f"  NO common coherent tuples (unexpected on seed 22)")

burn_integral_delta = reactive_burn_integral - hot_burn_integral
print(f"\n  burn_integral delta (reactive - hot): {burn_integral_delta:+.6f}")

print("\nStep 5: Verification...")
passed = True

if case_a != 0:
    print(f"  NOTE: fallback_case_a_count={case_a}  (replay catching agents not in hot's trace — meaningful signal)")
else:
    print(f"  OK:   fallback_case_a_count=0")

if case_b != 0:
    print(f"  NOTE: formation_divergence_case_b_count={case_b}  (replay catching formation-timing shift — meaningful signal)")
else:
    print(f"  OK:   formation_divergence_case_b_count=0")

if hot_only:
    print(f"  FAIL: {len(hot_only)} (agent,step) pairs coherent in hot but NOT in reactive")
    passed = False
else:
    print(f"  PASS: all hot-coherent (agent,step) pairs are coherent in reactive")

if reactive_only:
    print(f"  FAIL: {len(reactive_only)} (agent,step) pairs coherent in reactive but NOT in hot")
    passed = False
else:
    print(f"  PASS: no reactive-only coherent pairs")

if hot_coherent_steps != reactive_coherent_steps:
    print(f"  FAIL: per-agent coherent_steps mismatch")
    print(f"    hot:      {hot_coherent_steps}")
    print(f"    reactive: {reactive_coherent_steps}")
    passed = False
else:
    print(f"  PASS: per-agent coherent_steps match exactly")

# Divergence sanity check (Sal 016): if 0 trajectory divergence, something's wrong
if mean_divergence == 0.0 and len(common_coherent_keys) > 0:
    print(f"  FAIL: trajectory divergence is ZERO across {len(common_coherent_keys)} common coherent tuples")
    print(f"        Expected > 0 on seed 22 (F5 overrides predicted_* with actuals)")
    print(f"        Either F5 is not firing OR trajectories are inexplicably identical")
    passed = False
elif mean_divergence > 0:
    print(f"  PASS: trajectory divergence > 0 (replay drives correct coherence despite F5 modulation)")
else:
    print(f"  NOTE: trajectory divergence check skipped (no common coherent tuples)")

print()
if passed:
    print("*** SEED 22 REACTIVE REGRESSION PASS ***")
    print(f"    Replay mechanism verified on divergent trajectory.")
    print(f"    Coherence sets forced to match (bit-exact).")
    print(f"    Trajectory divergence: mean={mean_divergence:.8f}, max={max_divergence:.8f}")
    print(f"    Case A/B counters: {case_a}/{case_b}")
else:
    print("*** SEED 22 REACTIVE REGRESSION FAIL *** See above.")
    sys.exit(1)
