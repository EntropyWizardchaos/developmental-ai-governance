"""Gate 1 rerun per Nymph 042 (ninth-addendum regime, 2026-10-14).

Two exercises on seed 20 with burn_decay LEAK:

Exercise 1 — LEAK_TEST_MODE=True (positive control, gate must discriminate)
  - Run hot arm on seed 20, 3000 steps
  - Expect: fingerprint FAILS vs baseline (1167.3661594356); leak counter ≥ 3

Exercise 2 — LEAK_TEST_MODE=False (production regime, bit-identity must hold)
  - Run hot arm on seed 20, 3000 steps
  - Expect: fingerprint bit-identical to baseline; leak counter = 0

Pre-reg references:
  - Ninth addendum (0aad4cd): Phase-1-launch SHA locked at 77b0097d...
  - Eighth addendum §5: LEAK_TEST_MODE positive control + burn_decay LEAK
  - Sixth addendum: seed 20 lock
  - Seventh addendum: LEAK relocation refusal_chance → burn_decay

Baseline: pre-Task-D regression fingerprint on seed 20 LEAK=False:
  burn_integral = 1167.3661594356
  max_coherent_steps = 2873
  pop_final = 6

v37.4 SHA at run: 77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87
(Python-text LF-normalized)
"""
import importlib.util
import io
import json
import pathlib
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CODE_VERSIONS = pathlib.Path(
    r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions"
)
V37_4 = CODE_VERSIONS / "v37.4_structural_metacognition_stage_2.py"
sys.path.insert(0, str(CODE_VERSIONS))

OUTPUT_JSON = pathlib.Path(r"C:\Users\14132\iCloudDrive\Seeds\The Crack\gate_1_rerun_2026-10-14.json")

SEED = 20
N_STEPS = 3000
TOLERANCE_FP = 1e-10

BASELINE = {
    "burn_integral": 1167.3661594356,
    "max_coherent_steps": 2873,
    "pop_final": 6,
}
N_LEAK_ACTED_MIN = 3  # per seventh addendum §4c


def _load_module():
    """Fresh import of v37.4 for each exercise (clean module state for LEAK_TEST_MODE)."""
    _spec = importlib.util.spec_from_file_location("v37_4", str(V37_4))
    mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(mod)
    return mod


def _fingerprint(results, burn_baseline):
    """Standard fingerprint matching regression_test_hot_seed_20_2026-10-08.py."""
    final_agents = sorted(results["final_agents"], key=lambda a: (a.birth_step, a.id))
    terminal_C = tuple(round(float(a.C), 15) for a in final_agents)

    pop_by_step = {}
    for s in results["channel_snapshots"]:
        pop_by_step[s["step"]] = pop_by_step.get(s["step"], 0) + 1
    pop_series = tuple(pop_by_step[t] for t in sorted(pop_by_step))

    burn_integral = 0.0
    for s in results["channel_snapshots"]:
        excess = s["actual_burn_rate"] - burn_baseline
        if excess > 0:
            burn_integral += excess
    burn_integral = round(burn_integral, 10)

    max_coh = max(
        (getattr(a.observer, "coherent_steps", 0) for a in results["final_agents"]),
        default=0,
    )
    pop_final = len(results["final_agents"])

    return {
        "burn_integral": burn_integral,
        "max_coherent_steps": max_coh,
        "pop_final": pop_final,
        "terminal_C": list(terminal_C),
        "pop_series_len": len(pop_series),
    }


def _run_exercise(label, leak_mode):
    """Run one hot exercise on seed 20 with the given LEAK_TEST_MODE state.

    Returns (fingerprint, leak_counter, elapsed_sec).
    """
    print(f"\n--- {label}: LEAK_TEST_MODE={leak_mode} ---", flush=True)
    mod = _load_module()
    mod.LEAK_TEST_MODE = leak_mode
    print(f"  module LEAK_TEST_MODE set to {mod.LEAK_TEST_MODE}", flush=True)
    assert mod.LEAK_TEST_MODE is leak_mode, "LEAK_TEST_MODE assignment did not stick"

    burn_baseline = getattr(mod, "BURN_RATE_BASELINE", 0.08)

    buf = io.StringIO()
    orig = sys.stdout
    sys.stdout = buf
    t0 = time.time()
    try:
        results = mod.run_simulation(
            seed=SEED,
            all_crack_enabled=True,
            n_steps=N_STEPS,
            arm_mode="hot",
            log_channels=True,
            render_plots=False,
        )
    finally:
        sys.stdout = orig
    elapsed = time.time() - t0

    fp = _fingerprint(results, burn_baseline)
    leak_counter = int(results.get("n_leak_acted", 0))

    print(f"  elapsed: {elapsed:.1f}s", flush=True)
    print(f"  burn_integral:      {fp['burn_integral']}", flush=True)
    print(f"  max_coherent_steps: {fp['max_coherent_steps']}", flush=True)
    print(f"  pop_final:          {fp['pop_final']}", flush=True)
    print(f"  n_leak_acted:       {leak_counter}", flush=True)
    return fp, leak_counter, elapsed


def main():
    print("=" * 70, flush=True)
    print("GATE 1 RERUN — Nymph 042 spec (ninth-addendum regime)", flush=True)
    print(f"Seed {SEED}, {N_STEPS} steps, hot arm, burn_decay LEAK channel", flush=True)
    print("=" * 70, flush=True)

    # --- Exercise 1 ---
    fp1, counter1, elapsed1 = _run_exercise("Exercise 1 (positive control)", True)
    bi_delta_1 = fp1["burn_integral"] - BASELINE["burn_integral"]
    fp_divergence_1 = abs(bi_delta_1) > TOLERANCE_FP
    ex1_pass = fp_divergence_1 and counter1 >= N_LEAK_ACTED_MIN

    print(f"\n  burn_integral delta vs baseline: {bi_delta_1:+.6f}", flush=True)
    print(f"  fingerprint diverged: {fp_divergence_1}", flush=True)
    print(f"  leak counter {counter1} >= {N_LEAK_ACTED_MIN}: {counter1 >= N_LEAK_ACTED_MIN}", flush=True)
    print(f"  Exercise 1: {'PASS' if ex1_pass else 'FAIL'}", flush=True)

    # --- Exercise 2 ---
    fp2, counter2, elapsed2 = _run_exercise("Exercise 2 (production regime)", False)

    bi_match = abs(fp2["burn_integral"] - BASELINE["burn_integral"]) <= TOLERANCE_FP
    coh_match = fp2["max_coherent_steps"] == BASELINE["max_coherent_steps"]
    pop_match = fp2["pop_final"] == BASELINE["pop_final"]
    leak_zero = counter2 == 0
    ex2_pass = bi_match and coh_match and pop_match and leak_zero

    print(f"\n  burn_integral bit-identical to baseline: {bi_match}", flush=True)
    print(f"  max_coherent_steps matches baseline:     {coh_match}", flush=True)
    print(f"  pop_final matches baseline:              {pop_match}", flush=True)
    print(f"  leak counter == 0:                       {leak_zero}", flush=True)
    print(f"  Exercise 2: {'PASS' if ex2_pass else 'FAIL'}", flush=True)

    overall = ex1_pass and ex2_pass

    print("\n" + "=" * 70, flush=True)
    print(f"GATE 1 OVERALL: {'PASS' if overall else 'FAIL'}", flush=True)
    print("=" * 70, flush=True)

    report = {
        "schema_version": "gate_1_rerun_v1_2026-10-14",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "regime_sha_python_text_lf": "77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87",
        "pre_reg_references": {
            "ninth_addendum_commit": "0aad4cd",
            "eighth_addendum_section": "§5 LEAK_TEST_MODE positive control + §4a-b dose gate",
            "seventh_addendum": "LEAK relocation refusal_chance → burn_decay",
            "sixth_addendum": "seed 20 lock",
        },
        "seed": SEED,
        "n_steps": N_STEPS,
        "baseline": BASELINE,
        "n_leak_acted_min": N_LEAK_ACTED_MIN,
        "exercise_1": {
            "description": "LEAK_TEST_MODE=True positive control — gate must discriminate",
            "leak_test_mode": True,
            "fingerprint": fp1,
            "leak_counter": counter1,
            "burn_integral_delta_vs_baseline": bi_delta_1,
            "fingerprint_diverged_from_baseline": fp_divergence_1,
            "leak_counter_cleared_min": counter1 >= N_LEAK_ACTED_MIN,
            "elapsed_seconds": elapsed1,
            "verdict": "PASS" if ex1_pass else "FAIL",
        },
        "exercise_2": {
            "description": "LEAK_TEST_MODE=False production regime — bit-identity must hold",
            "leak_test_mode": False,
            "fingerprint": fp2,
            "leak_counter": counter2,
            "burn_integral_bit_identical": bi_match,
            "max_coherent_steps_matches_baseline": coh_match,
            "pop_final_matches_baseline": pop_match,
            "leak_counter_zero": leak_zero,
            "elapsed_seconds": elapsed2,
            "verdict": "PASS" if ex2_pass else "FAIL",
        },
        "overall_verdict": "PASS" if overall else "FAIL",
    }

    OUTPUT_JSON.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\nReport written: {OUTPUT_JSON}", flush=True)

    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
