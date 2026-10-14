"""Task F snapshot-schema extension — adds predicted/actual values to channel_snapshots.

Patches v37.4_structural_metacognition_stage_2.py only.

Spec: Nymph from_nymph_041 (Option A greenlight, 2026-10-13).
Blocked gap: eighth addendum §4e / Sal 015 R1 pre-registered the prediction-actual
gap moderator (predicted_recovery_time vs _estimate_recent_recovery_time) as the
primary Phase 5 moderator. Current channel_snapshots schema at v37.4:2696-2721
does not log predicted_* or actual_* raw values, so the moderator can't compute.

Pre-SHA (v37.4, Python-text LF-normalized):
    51aa504c385c1e46d8f80fcf08d0eb8bf257ff8ca96bcf892bef6a5637aae4ea
Post-SHA: printed on completion.

Changes applied:
  F1 — Agent.__init__: initialize _last_predicted_snapshot + _last_actuals_snapshot
  F2 — step_observer reactive branch: capture predicted/actual before step_predictions
  F3 — step_observer native branch: capture predicted/actual before step_predictions
  F4 — channel_snapshots dict: append 8 new fields (4 predicted + 4 actual)

Design notes:
- observer.predicted_* gets overwritten by step_predictions (observer.py:450),
  so the captured snapshot must happen BEFORE step_predictions runs.
- In reactive mode, _apply_reactive_override overwrites predicted_* AFTER
  step_predictions. The captured snapshot still reflects pre-step_predictions
  state, which is the authoritative observer prediction FOR this step.
- Phase 5 moderator reads HOT runs only per Sal 015 R1 (reactive's predicted==
  actual trivially due to F5, so reactive values are not informative for the
  moderator — captured regardless for diagnostic completeness).
- Patch is pure read + dict append; no simulation state change expected.
  Regression on seed 20 LEAK=False must stay bit-identical.

H3 discipline: patch adds fields derived from state already present; no reads
of `observer.coherent_step` (singular) are added.
"""
import hashlib
import pathlib
import sys

SIM_PATH = pathlib.Path(
    r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions\v37.4_structural_metacognition_stage_2.py"
)

EXPECTED_PRE_SHA_SIM = "51aa504c385c1e46d8f80fcf08d0eb8bf257ff8ca96bcf892bef6a5637aae4ea"


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def apply_edit(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count == 0:
        raise RuntimeError(f"Edit {label}: anchor not found")
    if count > 1:
        raise RuntimeError(f"Edit {label}: anchor not unique ({count} matches)")
    return src.replace(old, new)


# ============================================================
# Load + verify pre-SHA
# ============================================================
sim_src = lf(SIM_PATH.read_text(encoding="utf-8"))
pre_sha_sim = sha256_of(sim_src)

print(f"pre_sha sim: {pre_sha_sim}")
if pre_sha_sim != EXPECTED_PRE_SHA_SIM:
    print(f"ABORT: pre-SHA mismatch.\n  expected: {EXPECTED_PRE_SHA_SIM}")
    sys.exit(1)
print("Pre-SHA verified. Applying edits...")

# ============================================================
# F1 — Agent.__init__: initialize snapshot slots
# ============================================================
sim_src = apply_edit(
    sim_src,
    "        self.reactive_mode = reactive_mode\n        self.replay_coherence_timeline = replay_coherence_timeline\n        self._replay_fallback_a = 0      # Case A: (agent,step) not in timeline\n        self._replay_divergence_b = 0    # Case B: hot coherent, reactive observer not formed",
    "        self.reactive_mode = reactive_mode\n        self.replay_coherence_timeline = replay_coherence_timeline\n        self._replay_fallback_a = 0      # Case A: (agent,step) not in timeline\n        self._replay_divergence_b = 0    # Case B: hot coherent, reactive observer not formed\n        # Task F snapshot schema (2026-10-13, §4e / Sal 015 R1 moderator):\n        # captured in step_observer BEFORE step_predictions overwrites predicted_*,\n        # then read by channel_snapshots dict construction in run_simulation.\n        # None until first step_observer call where observer.exists is True.\n        self._last_predicted_snapshot = None\n        self._last_actuals_snapshot = None",
    "F1",
)

# ============================================================
# F2 — step_observer reactive branch: capture before step_predictions
# Anchor uniqueness via trailing "_apply_reactive_override" + comment that only
# appears in the reactive branch.
# ============================================================
sim_src = apply_edit(
    sim_src,
    "            actuals = {\n                'C':              float(self.C),\n                'burn_rate':      float(self.current_burn_rate),\n                'trauma_arrival': self._estimate_steps_to_next_trauma(),\n                'recovery_time':  self._estimate_recent_recovery_time(),\n            }\n            step_predictions(self.observer, actuals)\n            self._apply_reactive_override(actuals)",
    "            actuals = {\n                'C':              float(self.C),\n                'burn_rate':      float(self.current_burn_rate),\n                'trauma_arrival': self._estimate_steps_to_next_trauma(),\n                'recovery_time':  self._estimate_recent_recovery_time(),\n            }\n            # Task F snapshot (§4e / Sal 015 R1): capture BEFORE step_predictions\n            # overwrites observer.predicted_*. Note: in reactive mode,\n            # _apply_reactive_override will overwrite predicted_* with actuals\n            # AFTER step_predictions, but this captured snapshot reflects the\n            # authoritative pre-step_predictions prediction for this step.\n            self._last_predicted_snapshot = {\n                'C':              self.observer.predicted_C,\n                'burn_rate':      self.observer.predicted_burn_rate,\n                'trauma_arrival': self.observer.predicted_trauma_arrival,\n                'recovery_time':  self.observer.predicted_recovery_time,\n            }\n            self._last_actuals_snapshot = dict(actuals)\n            step_predictions(self.observer, actuals)\n            self._apply_reactive_override(actuals)",
    "F2",
)

# ============================================================
# F3 — step_observer native branch: capture before step_predictions
# Anchor uniqueness via trailing "# Reactive fifth arm (F5):" comment that only
# appears in the native branch.
# ============================================================
sim_src = apply_edit(
    sim_src,
    "        actuals = {\n            'C':              float(self.C),\n            'burn_rate':      float(self.current_burn_rate),\n            'trauma_arrival': self._estimate_steps_to_next_trauma(),\n            'recovery_time':  self._estimate_recent_recovery_time(),\n        }\n\n        step_predictions(self.observer, actuals)\n\n        # Reactive fifth arm (F5): overwrite predictions with current",
    "        actuals = {\n            'C':              float(self.C),\n            'burn_rate':      float(self.current_burn_rate),\n            'trauma_arrival': self._estimate_steps_to_next_trauma(),\n            'recovery_time':  self._estimate_recent_recovery_time(),\n        }\n\n        # Task F snapshot (§4e / Sal 015 R1): capture BEFORE step_predictions\n        # overwrites observer.predicted_*. Native path captures the authoritative\n        # observer prediction FOR this step (made at t-1), to be joined with\n        # the actual values seen at step t for the Phase 5 moderator.\n        self._last_predicted_snapshot = {\n            'C':              self.observer.predicted_C,\n            'burn_rate':      self.observer.predicted_burn_rate,\n            'trauma_arrival': self.observer.predicted_trauma_arrival,\n            'recovery_time':  self.observer.predicted_recovery_time,\n        }\n        self._last_actuals_snapshot = dict(actuals)\n\n        step_predictions(self.observer, actuals)\n\n        # Reactive fifth arm (F5): overwrite predictions with current",
    "F3",
)

# ============================================================
# F4 — channel_snapshots dict: append predicted_* + actual_* fields
# Anchor via the last existing field 'taught_D_caution'.
# ============================================================
sim_src = apply_edit(
    sim_src,
    "                    'taught_D_caution': a.taught_D_caution,  # v37.4 for effective_D_caution reconstruction\n                })",
    "                    'taught_D_caution': a.taught_D_caution,  # v37.4 for effective_D_caution reconstruction\n                    # Task F snapshot schema (2026-10-13, eighth §4e / Sal 015 R1):\n                    # Observer prediction FOR this step (made at t-1), captured in\n                    # step_observer BEFORE step_predictions overwrote them. Joined with\n                    # the actuals observed at step t. Enables compute_prediction_actual_gap\n                    # in phase_5_analysis.py. Reactive runs have predicted==actual due to\n                    # F5 override; moderator reads HOT runs only per 015 R1.\n                    # moderator_ prefix avoids collision with 'actual_burn_rate' above\n                    # (which logs a.get_active_burn_rate() for burn_integral computation).\n                    'moderator_predicted_C':              (a._last_predicted_snapshot['C']              if a._last_predicted_snapshot else None),\n                    'moderator_predicted_burn_rate':      (a._last_predicted_snapshot['burn_rate']      if a._last_predicted_snapshot else None),\n                    'moderator_predicted_trauma_arrival': (a._last_predicted_snapshot['trauma_arrival'] if a._last_predicted_snapshot else None),\n                    'moderator_predicted_recovery_time':  (a._last_predicted_snapshot['recovery_time']  if a._last_predicted_snapshot else None),\n                    'moderator_actual_C':                 (a._last_actuals_snapshot['C']                if a._last_actuals_snapshot else None),\n                    'moderator_actual_burn_rate':         (a._last_actuals_snapshot['burn_rate']        if a._last_actuals_snapshot else None),\n                    'moderator_actual_trauma_arrival':    (a._last_actuals_snapshot['trauma_arrival']   if a._last_actuals_snapshot else None),\n                    'moderator_actual_recovery_time':     (a._last_actuals_snapshot['recovery_time']    if a._last_actuals_snapshot else None),\n                })",
    "F4",
)

# ============================================================
# Write + verify
# ============================================================
post_sha_sim = sha256_of(sim_src)
SIM_PATH.write_text(sim_src, encoding="utf-8")

print(f"\nAll edits applied.")
print(f"post_sha sim: {post_sha_sim}")
print("\nNext: run regression_test_hot_seed_20_2026-10-08.py to verify bit-identity.")
