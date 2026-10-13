"""Task D — Reactive arm wiring (replay-driven coherence).

Patches both v37.4_structural_metacognition_stage_2.py and stage_2_hooks.py.

Pre-SHA (v37.4, Python-text LF-normalized):
    dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f
Pre-SHA (stage_2_hooks, Python-text LF-normalized):
    092c8442749e8d6ee8f652566e35f06630c76a56fe64fef1c7467200f2a4c5aa

Post-SHAs: printed on completion.

Spec: Nymph from_nymph_038 §1 (2026-10-09). Eighth addendum committed at
GitHub 86b7eee before this patch was applied (pre-reg discipline).

Changes applied:
  stage_2_hooks.py:
    H1 — Add MODE_REACTIVE constant + to VALID_MODES
    H2 — apply_canonical_override: treat MODE_REACTIVE like MODE_HOT (no-op)
    H3 — assert_observer_off: treat MODE_REACTIVE like MODE_HOT (skip)

  v37.4:
    V1 — Agent.__init__: add replay_coherence_timeline param + counters
    V2 — Agent birth line A (sage_act memoir path): propagate reactive attrs
    V3 — Agent birth line B (mentor_act path): propagate reactive attrs
    V4 — run_simulation signature: add replay_coherence_timeline param
    V5 — run_simulation docstring: add 'reactive' to arm_mode description
    V6 — hook-integrity assert: arm_mode='reactive' requires timeline
    V7 — Initial agent construction: pass reactive attrs
    V8 — Born agents in main loop: pass reactive attrs
    V9 — Twin agent construction: pass reactive attrs
    V10 — step_observer: add replay-driven coherence path (Cases A/B/C)
    V11 — results dict: add replay case counts
"""
import hashlib
import pathlib
import sys

HOOKS_PATH = pathlib.Path(
    r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions\stage_2_hooks.py"
)
SIM_PATH = pathlib.Path(
    r"C:\Users\14132\iCloudDrive\Seeds\Birth Tree 11\Jiminy Core\AI Life Cycle\Society\Code Versions\v37.4_structural_metacognition_stage_2.py"
)

EXPECTED_PRE_SHA_SIM   = "dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f"
EXPECTED_PRE_SHA_HOOKS = "092c8442749e8d6ee8f652566e35f06630c76a56fe64fef1c7467200f2a4c5aa"


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def apply_edit(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count == 0:
        raise RuntimeError(f"Edit {label}: anchor not found in source")
    if count > 1:
        raise RuntimeError(f"Edit {label}: anchor not unique ({count} matches)")
    return src.replace(old, new)


# ============================================================
# Load
# ============================================================
sim_src   = lf(SIM_PATH.read_text(encoding="utf-8"))
hooks_src = lf(HOOKS_PATH.read_text(encoding="utf-8"))

pre_sha_sim   = sha256_of(sim_src)
pre_sha_hooks = sha256_of(hooks_src)

print(f"pre_sha sim:   {pre_sha_sim}")
print(f"pre_sha hooks: {pre_sha_hooks}")

if pre_sha_sim != EXPECTED_PRE_SHA_SIM:
    print(f"ABORT: sim pre-SHA mismatch.\n  expected: {EXPECTED_PRE_SHA_SIM}")
    sys.exit(1)
if pre_sha_hooks != EXPECTED_PRE_SHA_HOOKS:
    print(f"ABORT: hooks pre-SHA mismatch.\n  expected: {EXPECTED_PRE_SHA_HOOKS}")
    sys.exit(1)

print("Pre-SHAs verified. Applying edits...")

# ============================================================
# H1 — Add MODE_REACTIVE to stage_2_hooks.py
# ============================================================
hooks_src = apply_edit(
    hooks_src,
    'MODE_MATCHED = "matched"     # observer off, uniform mu_c offset\n\nVALID_MODES = {MODE_HOT, MODE_NO_OBS, MODE_YOKED, MODE_MATCHED}\nNON_HOT_MODES = {MODE_NO_OBS, MODE_YOKED, MODE_MATCHED}',
    'MODE_MATCHED  = "matched"    # observer off, uniform mu_c offset\nMODE_REACTIVE = "reactive"   # observer live, coherence driven by replay timeline\n\nVALID_MODES  = {MODE_HOT, MODE_NO_OBS, MODE_YOKED, MODE_MATCHED, MODE_REACTIVE}\nNON_HOT_MODES = {MODE_NO_OBS, MODE_YOKED, MODE_MATCHED}',
    "H1",
)

# ============================================================
# H2a — apply_canonical_override: MODE_REACTIVE → no-op (unique via docstring anchor)
# ============================================================
hooks_src = apply_edit(
    hooks_src,
    "      MODE_YOKED: replace from trace_dict's canonical records at step t, matched by rank\n      MODE_MATCHED: write baseline + mu_c uniformly\n    Refusal_chance is clamped to [0,1] in both inject modes.\n    \"\"\"\n    if mode in (MODE_HOT, MODE_NO_OBS):\n        return",
    "      MODE_YOKED: replace from trace_dict's canonical records at step t, matched by rank\n      MODE_MATCHED: write baseline + mu_c uniformly\n    Refusal_chance is clamped to [0,1] in both inject modes.\n    \"\"\"\n    if mode in (MODE_HOT, MODE_NO_OBS, MODE_REACTIVE):\n        return",
    "H2a",
)

# ============================================================
# H2b — apply_canonical_override_D_caution: MODE_REACTIVE → no-op
# ============================================================
hooks_src = apply_edit(
    hooks_src,
    "      MODE_HOT, MODE_NO_OBS: no-op\n      MODE_YOKED: replace from trace_dict's D_caution record at (step t, matching rank).\n                  None injected verbatim when source had None (behaviorally neutral).\n      MODE_MATCHED: write BASELINE_D_CAUTION + mu_c uniformly.\n    \"\"\"\n    if mode in (MODE_HOT, MODE_NO_OBS):\n        return",
    "      MODE_HOT, MODE_NO_OBS: no-op\n      MODE_YOKED: replace from trace_dict's D_caution record at (step t, matching rank).\n                  None injected verbatim when source had None (behaviorally neutral).\n      MODE_MATCHED: write BASELINE_D_CAUTION + mu_c uniformly.\n    \"\"\"\n    if mode in (MODE_HOT, MODE_NO_OBS, MODE_REACTIVE):\n        return",
    "H2b",
)

# ============================================================
# H3 — assert_observer_off: skip for MODE_REACTIVE (observers expected)
# ============================================================
hooks_src = apply_edit(
    hooks_src,
    "    if mode == MODE_HOT:\n        return\n    if mode not in NON_HOT_MODES:",
    "    if mode in (MODE_HOT, MODE_REACTIVE):\n        return\n    if mode not in NON_HOT_MODES:",
    "H3",
)

# ============================================================
# V1 — Agent.__init__: add replay_coherence_timeline + counters
# ============================================================
sim_src = apply_edit(
    sim_src,
    "                 crack_enabled=False, pair_id=None, reactive_mode=False):",
    "                 crack_enabled=False, pair_id=None, reactive_mode=False,\n                 replay_coherence_timeline=None):",
    "V1a",
)
sim_src = apply_edit(
    sim_src,
    "        self.reactive_mode = reactive_mode",
    "        self.reactive_mode = reactive_mode\n        self.replay_coherence_timeline = replay_coherence_timeline\n        self._replay_fallback_a = 0      # Case A: (agent,step) not in timeline\n        self._replay_divergence_b = 0    # Case B: hot coherent, reactive observer not formed",
    "V1b",
)

# ============================================================
# V2 — Agent birth line A (sage_act memoir path, line ~1517)
# Unique anchor: "new_agent = Agent(new_id, key, t, self.generation + 1)  # v33: fresh burn rate\n        agents.append(new_agent)\n\n        self.stage = \"ANCESTOR\""
# ============================================================
sim_src = apply_edit(
    sim_src,
    "        new_agent = Agent(new_id, key, t, self.generation + 1)  # v33: fresh burn rate\n        agents.append(new_agent)\n\n        self.stage = \"ANCESTOR\"",
    "        new_agent = Agent(new_id, key, t, self.generation + 1,\n                          reactive_mode=self.reactive_mode,\n                          replay_coherence_timeline=self.replay_coherence_timeline)\n        agents.append(new_agent)\n\n        self.stage = \"ANCESTOR\"",
    "V2",
)

# ============================================================
# V3 — Agent birth line B (mentor_act path, line ~1671)
# Unique anchor includes subsequent emb line
# ============================================================
sim_src = apply_edit(
    sim_src,
    "            new_agent = Agent(new_id, key, t, self.generation + 1)  # v33: fresh burn rate\n            new_agent.emb = self.emb * 0.7",
    "            new_agent = Agent(new_id, key, t, self.generation + 1,\n                              reactive_mode=self.reactive_mode,\n                              replay_coherence_timeline=self.replay_coherence_timeline)\n            new_agent.emb = self.emb * 0.7",
    "V3",
)

# ============================================================
# V4 — run_simulation signature: add replay_coherence_timeline
# ============================================================
sim_src = apply_edit(
    sim_src,
    "                   arm_mode=None, trace_buffer=None, trace_dict=None,\n                   mu_c_dict=None):",
    "                   arm_mode=None, trace_buffer=None, trace_dict=None,\n                   replay_coherence_timeline=None, mu_c_dict=None):",
    "V4",
)

# ============================================================
# V5 — run_simulation docstring: note 'reactive' in arm_mode list
# ============================================================
sim_src = apply_edit(
    sim_src,
    "#   arm_mode:     one of {'hot','no_obs','yoked','matched'}; None = legacy behavior",
    "#   arm_mode:     one of {'hot','no_obs','yoked','matched','reactive'}; None = legacy behavior",
    "V5",
)

# ============================================================
# V6 — hook-integrity: assert arm_mode='reactive' requires timeline
# ============================================================
sim_src = apply_edit(
    sim_src,
    "    if arm_mode == 'hot':\n        assert all_crack_enabled is True, (\n            f\"MODE_HOT requires all_crack_enabled=True. \"\n            f\"Got arm_mode='hot' with all_crack_enabled={all_crack_enabled!r}. \"\n            f\"The observer pathway cannot be exercised without crack enabled.\"\n        )",
    "    if arm_mode == 'hot':\n        assert all_crack_enabled is True, (\n            f\"MODE_HOT requires all_crack_enabled=True. \"\n            f\"Got arm_mode='hot' with all_crack_enabled={all_crack_enabled!r}. \"\n            f\"The observer pathway cannot be exercised without crack enabled.\"\n        )\n    if arm_mode == 'reactive':\n        assert replay_coherence_timeline is not None, (\n            \"arm_mode='reactive' requires replay_coherence_timeline. \"\n            \"Load hot arm's channel_snapshots and build the timeline dict first.\"\n        )",
    "V6",
)

# ============================================================
# V7 — Initial agent construction: pass reactive attrs
# ============================================================
sim_src = apply_edit(
    sim_src,
    "        agent_a = Agent(next_agent_id, subkey1, _bs, 0,\n                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_a, pair_id=pair_id)\n        next_agent_id += 1\n\n        # Agent B: crack disabled control (or per arm)\n        agent_b = Agent(next_agent_id, subkey2, _bs, 0,\n                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_b, pair_id=pair_id)",
    "        agent_a = Agent(next_agent_id, subkey1, _bs, 0,\n                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_a, pair_id=pair_id,\n                        reactive_mode=(arm_mode == 'reactive'),\n                        replay_coherence_timeline=replay_coherence_timeline)\n        next_agent_id += 1\n\n        # Agent B: crack disabled control (or per arm)\n        agent_b = Agent(next_agent_id, subkey2, _bs, 0,\n                        birth_burn_rate=shared_burn_rate, crack_enabled=_ce_b, pair_id=pair_id,\n                        reactive_mode=(arm_mode == 'reactive'),\n                        replay_coherence_timeline=replay_coherence_timeline)",
    "V7",
)

# ============================================================
# V8 — Born agents in main loop: pass reactive attrs
# ============================================================
sim_src = apply_edit(
    sim_src,
    "            agent_a = Agent(next_agent_id, subkey1, t, current_generation,\n                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_a, pair_id=pair_id)\n            agents.append(agent_a)\n            birth_log.append((t, next_agent_id, current_generation, 'CRACK' if _bce_a else 'CONTROL'))\n            next_agent_id += 1\n\n            agent_b = Agent(next_agent_id, subkey2, t, current_generation,\n                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_b, pair_id=pair_id)",
    "            agent_a = Agent(next_agent_id, subkey1, t, current_generation,\n                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_a, pair_id=pair_id,\n                            reactive_mode=(arm_mode == 'reactive'),\n                            replay_coherence_timeline=replay_coherence_timeline)\n            agents.append(agent_a)\n            birth_log.append((t, next_agent_id, current_generation, 'CRACK' if _bce_a else 'CONTROL'))\n            next_agent_id += 1\n\n            agent_b = Agent(next_agent_id, subkey2, t, current_generation,\n                            birth_burn_rate=shared_burn_rate, crack_enabled=_bce_b, pair_id=pair_id,\n                            reactive_mode=(arm_mode == 'reactive'),\n                            replay_coherence_timeline=replay_coherence_timeline)",
    "V8",
)

# ============================================================
# V9 — Twin agent construction: pass reactive attrs
# ============================================================
sim_src = apply_edit(
    sim_src,
    "                    twin = Agent(next_agent_id, twin_key, t, sage.generation + 1,\n                                 birth_burn_rate=new_agent.birth_burn_rate,\n                                 crack_enabled=_twin_ce,\n                                 pair_id=pair_id)",
    "                    twin = Agent(next_agent_id, twin_key, t, sage.generation + 1,\n                                 birth_burn_rate=new_agent.birth_burn_rate,\n                                 crack_enabled=_twin_ce,\n                                 pair_id=pair_id,\n                                 reactive_mode=(arm_mode == 'reactive'),\n                                 replay_coherence_timeline=replay_coherence_timeline)",
    "V9",
)

# ============================================================
# V10 — step_observer: add replay-driven coherence path (Cases A/B/C)
# ============================================================
OLD_STEP_OBS = '''    def step_observer(self, t):
        """v37.3: Per-agent per-step observer update.

        Runs prediction updates across four channels (C, burn_rate,
        trauma_arrival, recovery_time), promotes to coherent when the
        gate clears, and syncs legacy aliases (`self.cracked`,
        `self.metacognition_observations`, `self.pre_crack_D`) so v37.2's
        downstream code keeps working.
        """
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
        # on the observer\'s learned predictions. Applied AFTER step_predictions
        # so the observer\'s own prediction machinery still runs (variance +
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
                self._test_leak_burn_decay_mult = 0.5'''

NEW_STEP_OBS = '''    def step_observer(self, t):
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
        # on the observer\'s learned predictions. Applied AFTER step_predictions
        # so the observer\'s own prediction machinery still runs (variance +
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
                self._test_leak_burn_decay_mult = 0.5'''

sim_src = apply_edit(sim_src, OLD_STEP_OBS, NEW_STEP_OBS, "V10")

# ============================================================
# V11 — results dict: add replay case counts
# ============================================================
sim_src = apply_edit(
    sim_src,
    "        'n_leak_acted': _LEAK_ACTIVATION_COUNT,\n    }",
    "        'n_leak_acted': _LEAK_ACTIVATION_COUNT,\n        # Task D (2026-10-12): replay case counts for Phase 5 reporting.\n        # Case A: (agent,step) key not in timeline. Case B: hot coherent but\n        # reactive observer not formed. Both flagged if > 5% per seed.\n        'replay_fallback_case_a_count': sum(\n            a._replay_fallback_a for a in agents),\n        'replay_divergence_case_b_count': sum(\n            a._replay_divergence_b for a in agents),\n    }",
    "V11",
)

# ============================================================
# Write and verify
# ============================================================
post_sha_sim   = sha256_of(sim_src)
post_sha_hooks = sha256_of(hooks_src)

SIM_PATH.write_text(sim_src, encoding="utf-8")
HOOKS_PATH.write_text(hooks_src, encoding="utf-8")

print(f"\nAll edits applied.")
print(f"post_sha sim:   {post_sha_sim}")
print(f"post_sha hooks: {post_sha_hooks}")
print("\nNext: run regression_test_hot_seed_20_2026-10-08.py to verify bit-identity.")
