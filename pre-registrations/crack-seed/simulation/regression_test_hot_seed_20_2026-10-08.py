"""Post-integration regression test — hot on seed 20 under v37.4.

Compares bit-identically against the pre-integration pickle produced by
secondary_preflight_seed_20_2026-10-08.py (hot run on v37.3.1 code,
pre_integration_sha=9b57fea26d26f5b7...).

Expected: identical terminal_C tuple, pop_series, burn_integral, max_coh_steps.
If any divergence > TOLERANCE_FP, the v37.4 integration perturbed hot behavior.

Attribution: free-check design from Opus 5.5 2026-10-07 (hooks must be true
no-ops in hot mode by design; this test proves it empirically).
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import pickle
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CODE_VERSIONS = Path(
    r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions"
)
V37_4 = CODE_VERSIONS / "v37.4_structural_metacognition_stage_2.py"
sys.path.insert(0, str(CODE_VERSIONS))

PRE_PICKLE = Path(
    r"C:\Users\14132\iCloudDrive\Seeds\The Crack\preflight_fingerprints_2026-10-07\preflight_seed_20_hot_fingerprint.pkl"
)
SEED = 20
N_STEPS = 3000
TOLERANCE_FP = 1e-10


def _fingerprint(res, burn_baseline):
    final_agents = sorted(res["final_agents"], key=lambda a: (a.birth_step, a.id))
    terminal_C = tuple(round(float(a.C), 15) for a in final_agents)
    pop_by_step = {}
    for s in res["channel_snapshots"]:
        pop_by_step[s["step"]] = pop_by_step.get(s["step"], 0) + 1
    pop_series = tuple(pop_by_step[t] for t in sorted(pop_by_step))

    burn_integral = 0.0
    for s in res["channel_snapshots"]:
        excess = s["actual_burn_rate"] - burn_baseline
        if excess > 0:
            burn_integral += excess
    burn_integral = round(burn_integral, 10)

    max_coh_steps = max(
        (getattr(a.observer, "coherent_steps", 0) for a in res["final_agents"]),
        default=0,
    )
    return {
        "terminal_C": terminal_C,
        "pop_series": pop_series,
        "burn_integral": burn_integral,
        "max_coherent_steps_final_agents": max_coh_steps,
    }


def main():
    v37_4_sha = hashlib.sha256(V37_4.read_bytes()).hexdigest()
    print(f"Regression test — hot seed {SEED} on v37.4", flush=True)
    print(f"v37.4 post-integration SHA: {v37_4_sha}", flush=True)

    _spec = importlib.util.spec_from_file_location("v37_4", str(V37_4))
    mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(mod)

    assert mod.LEAK_TEST_MODE is False, "LEAK_TEST_MODE must be False for production regression"
    print(f"LEAK_TEST_MODE verified False.", flush=True)

    print(f"\nRunning hot arm_mode='hot', trace_buffer=None (no capture) on seed {SEED}...", flush=True)
    buf = io.StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        res = mod.run_simulation(
            seed=SEED,
            all_crack_enabled=True,
            n_steps=N_STEPS,
            log_channels=True,
            render_plots=False,
            arm_mode="hot",
            trace_buffer=None,
        )
    finally:
        sys.stdout = orig

    burn_baseline = getattr(mod, "BURN_RATE_BASELINE", 0.08)
    fp_post = _fingerprint(res, burn_baseline)

    with open(PRE_PICKLE, "rb") as f:
        pre_data = pickle.load(f)
    fp_pre = pre_data["fingerprint"]
    pre_sha = pre_data["pre_int_sha"]

    print(f"\nPre-integration SHA (from pickle): {pre_sha[:16]}...", flush=True)
    print(f"Post-integration SHA (v37.4):       {v37_4_sha[:16]}...", flush=True)

    # Compare fingerprints
    diags = []
    if fp_pre["terminal_C"] != fp_post["terminal_C"]:
        n = len(fp_pre["terminal_C"])
        diffs = [(i, a, b) for i, (a, b) in enumerate(zip(fp_pre["terminal_C"], fp_post["terminal_C"]))
                 if abs(a - b) > TOLERANCE_FP]
        if diffs:
            diags.append(f"terminal_C MISMATCH on {len(diffs)}/{n} agents")
            for i, a, b in diffs[:5]:
                diags.append(f"  agent[{i}]: pre={a:.15f}  post={b:.15f}  d={a-b:+.3e}")
    if fp_pre["pop_series"] != fp_post["pop_series"]:
        n = sum(1 for a, b in zip(fp_pre["pop_series"], fp_post["pop_series"]) if a != b)
        diags.append(f"pop_series MISMATCH at {n} steps")
    bd = fp_pre["burn_integral"] - fp_post["burn_integral"]
    if abs(bd) > TOLERANCE_FP:
        diags.append(f"burn_integral MISMATCH: pre={fp_pre['burn_integral']}  post={fp_post['burn_integral']}  d={bd:+.6e}")
    if fp_pre["max_coherent_steps_final_agents"] != fp_post["max_coherent_steps_final_agents"]:
        diags.append(f"max_coherent_steps MISMATCH: pre={fp_pre['max_coherent_steps_final_agents']}  post={fp_post['max_coherent_steps_final_agents']}")

    print(f"\n[fingerprint comparison]", flush=True)
    print(f"  pre:  burn_integral={fp_pre['burn_integral']}  max_coh_steps={fp_pre['max_coherent_steps_final_agents']}  pop_final={fp_pre['pop_series'][-1] if fp_pre['pop_series'] else 'n/a'}", flush=True)
    print(f"  post: burn_integral={fp_post['burn_integral']}  max_coh_steps={fp_post['max_coherent_steps_final_agents']}  pop_final={fp_post['pop_series'][-1] if fp_post['pop_series'] else 'n/a'}", flush=True)

    print(f"\n[v37.4 extras — not in pre-integration fingerprint]", flush=True)
    print(f"  arm_mode: {res.get('arm_mode')}", flush=True)
    print(f"  coherence_declaration: {res.get('coherence_declaration')}", flush=True)
    print(f"  trace_buffer: {type(res.get('trace_buffer')).__name__}", flush=True)

    if not diags:
        print(f"\n*** REGRESSION PASS *** v37.4 hooks are true no-ops in hot mode.", flush=True)
        print(f"Bit-identical to pre-integration v37.3.1 on seed {SEED} within TOLERANCE_FP = {TOLERANCE_FP}.", flush=True)
        return 0
    print(f"\n*** REGRESSION FAIL *** v37.4 perturbed hot behavior. Diagnostics:", flush=True)
    for d in diags:
        print(d, flush=True)
    print(f"\nHalt. Locate the drift source before any further integration work.", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
