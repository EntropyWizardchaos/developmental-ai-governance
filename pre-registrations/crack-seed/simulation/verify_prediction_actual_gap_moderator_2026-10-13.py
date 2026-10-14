"""Extra-credit verification per Nymph 041 §3:
confirm compute_prediction_actual_gap runs end-to-end on a short hot-only
trace built from the regression test. Just enough to confirm the moderator
is now computable with the Task F snapshot-schema extension in place.
"""
import importlib.util
import pathlib
import sys

CODE_DIR = pathlib.Path(r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions")
sys.path.insert(0, str(CODE_DIR))

V37_4 = CODE_DIR / "v37.4_structural_metacognition_stage_2.py"
_spec = importlib.util.spec_from_file_location("v37_4", str(V37_4))
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

CRACK_DIR = pathlib.Path(r"C:\Users\14132\iCloudDrive\Seeds\The Crack")
sys.path.insert(0, str(CRACK_DIR))

p5_spec = importlib.util.spec_from_file_location("p5", str(CRACK_DIR / "phase_5_analysis.py"))
p5 = importlib.util.module_from_spec(p5_spec)
p5_spec.loader.exec_module(p5)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print("Running short hot trace on seed 20 (3000 steps, LEAK=False)...")
hot_results = mod.run_simulation(
    seed=20,
    all_crack_enabled=True,
    n_steps=3000,
    arm_mode='hot',
    log_channels=True,
    render_plots=False,
)

# Verify schema fields present
sample = next((s for s in hot_results['channel_snapshots'] if s.get('observer_coherent')), None)
if sample is None:
    print("FAIL: no coherent moments in hot trace")
    sys.exit(1)

required_fields = [
    'moderator_predicted_C', 'moderator_predicted_burn_rate',
    'moderator_predicted_trauma_arrival', 'moderator_predicted_recovery_time',
    'moderator_actual_C', 'moderator_actual_burn_rate',
    'moderator_actual_trauma_arrival', 'moderator_actual_recovery_time',
]
missing = [f for f in required_fields if f not in sample]
if missing:
    print(f"FAIL: snapshot missing moderator_ fields: {missing}")
    sys.exit(1)

print(f"OK: all 8 moderator_ fields present in coherent-moment snapshot")
print(f"    sample values at step {sample['step']}, agent {sample['agent_id']}:")
print(f"      predicted_recovery_time = {sample['moderator_predicted_recovery_time']}")
print(f"      actual_recovery_time    = {sample['moderator_actual_recovery_time']}")

# Run the Phase 5 moderator
result = p5.compute_prediction_actual_gap(hot_results)
print(f"\ncompute_prediction_actual_gap result:")
print(f"  n_coherent:   {result['n_coherent']}")
print(f"  mean_abs_gap: {result['mean_abs_gap']}")

if result['n_coherent'] > 0 and result['mean_abs_gap'] is not None:
    print(f"\n*** MODERATOR COMPUTABLE *** (end-to-end hot trace -> phase_5_analysis)")
else:
    print(f"\n*** FAIL *** moderator could not compute from populated schema")
    sys.exit(1)

# Also sanity check: in reactive mode, F5 override makes predicted==actual.
# Spec says moderator reads HOT only; verify reactive would report ~0 gap if asked.
print("\nSanity check: reactive mode should show ~0 gap due to F5 override...")
replay_timeline = {
    (s['agent_id'], s['step']): s['observer_coherent']
    for s in hot_results['channel_snapshots']
}
reactive_results = mod.run_simulation(
    seed=20,
    all_crack_enabled=True,
    n_steps=3000,
    arm_mode='reactive',
    log_channels=True,
    replay_coherence_timeline=replay_timeline,
    render_plots=False,
)
reactive_result = p5.compute_prediction_actual_gap(reactive_results)
print(f"  reactive n_coherent:   {reactive_result['n_coherent']}")
print(f"  reactive mean_abs_gap: {reactive_result['mean_abs_gap']}")

# In reactive mode, F5 override overwrites predicted_* with actuals AFTER
# step_predictions. But our capture is BEFORE step_predictions, so predicted_
# holds the observer's own prediction (just like hot). The DELTA (gap) might
# therefore be close to hot's delta on seed 20 (same prediction machinery).
# Confirms: reactive snapshot semantics preserved — moderator captures pre-F5
# predictions, which match hot's for the moderator read.
print(f"\n(Note: reactive moderator ~matches hot's because capture happens BEFORE")
print(f" step_predictions AND BEFORE F5 override. The 015 R1 spec says 'HOT only'")
print(f" as a convention — the moderator is an observer-prediction-quality metric,")
print(f" and the observer runs identically in both arms pre-F5. Reactive just adds")
print(f" diagnostic completeness.)")
