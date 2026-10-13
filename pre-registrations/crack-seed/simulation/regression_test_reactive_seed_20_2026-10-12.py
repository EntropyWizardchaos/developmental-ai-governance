"""Reactive-mode regression test for Task D (2026-10-12).

Spec: Nymph from_nymph_038 §2d.

Steps:
  1. Run hot arm on seed 20 with log_channels=True to capture channel_snapshots.
  2. Build replay_coherence_timeline: {(agent_id, step): observer_coherent}.
  3. Run reactive arm on seed 20 using the replay timeline.
  4. Verify:
     a. All (agent, step) tuples where hot was coherent are also coherent in reactive.
     b. fallback_case_a_count == 0 (no agent/step in reactive missing from hot).
     c. formation_divergence_case_b_count == 0 (no formation divergence on seed 20).
     d. Reactive coherent_steps per agent matches hot's coherent_steps per agent.
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

SEED = 20

print(f"Step 1: Run hot arm on seed {SEED} with channel_snapshots...")
hot_results = run_simulation(
    seed=SEED,
    all_crack_enabled=True,
    n_steps=3000,
    arm_mode='hot',
    log_channels=True,
    render_plots=False,
)

snapshots = hot_results['channel_snapshots']
print(f"  channel_snapshots count: {len(snapshots)}")
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

# Per-agent coherent_steps in hot
hot_coherent_steps = {}
for s in snapshots:
    if s['observer_coherent']:
        hot_coherent_steps[s['agent_id']] = hot_coherent_steps.get(s['agent_id'], 0) + 1
print(f"  hot coherent_steps per agent: {hot_coherent_steps}")

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

print(f"  reactive channel_snapshots count: {len(reactive_snapshots)}")
print(f"  fallback_case_a_count: {case_a}")
print(f"  formation_divergence_case_b_count: {case_b}")

# Verify coherence alignment
reactive_coherent_keys = {
    (s['agent_id'], s['step'])
    for s in reactive_snapshots
    if s['observer_coherent']
}

hot_only = coherent_keys - reactive_coherent_keys
reactive_only = reactive_coherent_keys - coherent_keys

# Per-agent coherent_steps in reactive
reactive_coherent_steps = {}
for s in reactive_snapshots:
    if s['observer_coherent']:
        reactive_coherent_steps[s['agent_id']] = reactive_coherent_steps.get(s['agent_id'], 0) + 1
print(f"  reactive coherent_steps per agent: {reactive_coherent_steps}")

print("\nStep 4: Verification...")
passed = True

if case_a != 0:
    print(f"  FAIL: fallback_case_a_count={case_a} (expected 0)")
    passed = False
else:
    print(f"  PASS: fallback_case_a_count=0")

if case_b != 0:
    print(f"  FAIL: formation_divergence_case_b_count={case_b} (expected 0)")
    passed = False
else:
    print(f"  PASS: formation_divergence_case_b_count=0")

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

print()
if passed:
    print("*** REACTIVE REGRESSION PASS *** Replay drives coherence correctly on seed 20.")
else:
    print("*** REACTIVE REGRESSION FAIL *** See above.")
    sys.exit(1)
